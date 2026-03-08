"""Superadmin Contact Messages API — cross-tenant contact message management.

Provides REST endpoints for the service provider (SUPERADMIN role) to
query, update, and export contact messages submitted via the merchant
admin "Contact Us" form.

Endpoints (SPEC-1589, SPEC-1590, SPEC-1592):
    GET    /api/superadmin/contact-messages           — List with filters
    GET    /api/superadmin/contact-messages/export     — CSV download
    GET    /api/superadmin/contact-messages/{id}       — Single message detail
    PATCH  /api/superadmin/contact-messages/{id}       — Update status/notes

All endpoints require SUPERADMIN role.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.cosmos_schema import (
    COLLECTION_CONTACT_MESSAGES,
    ContactMessageDocument,
)
from src.multi_tenant.middleware import require_platform_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/superadmin/contact-messages",
    tags=["Superadmin Contact Messages"],
    dependencies=[Depends(require_platform_admin())],
)

# ---------------------------------------------------------------------------
# Module-level repository reference (set via configure function)
# ---------------------------------------------------------------------------

_contact_repo: Any = None


def configure_superadmin_contact_services(contact_repo: Any) -> None:
    """Wire the contact_messages repository at startup."""
    global _contact_repo
    _contact_repo = contact_repo


def _require_repo() -> Any:
    if _contact_repo is None:
        raise HTTPException(status_code=503, detail="Contact messages service not initialized")
    return _contact_repo


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ContactMessageItem(CamelCaseModel):
    """Single contact message in list responses."""

    id: str
    tenant_id: str
    topic: str
    subject: str
    message: str
    member_email: str | None = None
    member_role: str | None = None
    member_id: str | None = None
    tier: str | None = None
    status: str
    notes: str = ""
    created_at: str
    updated_at: str


class ContactMessageListResponse(CamelCaseModel):
    """Paginated list of contact messages."""

    messages: list[ContactMessageItem]
    total: int
    skip: int
    limit: int


class ContactMessageUpdateRequest(CamelCaseModel):
    """Request body for updating a contact message."""

    status: str | None = Field(None, description="New status: new, read, resolved, archived")
    notes: str | None = Field(None, description="Operator annotations")


class ContactMessageUpdateResponse(CamelCaseModel):
    """Response after updating a contact message."""

    ok: bool
    message: ContactMessageItem


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=ContactMessageListResponse,
    summary="List contact messages (cross-partition)",
    description="List all contact messages with optional filtering by topic, status, tenant, and date range.",
    status_code=200,
)
async def list_contact_messages(
    topic: str | None = Query(None, description="Filter by topic"),
    status: str | None = Query(None, description="Filter by status"),
    tenant_id: str | None = Query(None, description="Filter by tenant ID"),
    created_after: str | None = Query(None, description="Filter messages created after (ISO 8601)"),
    created_before: str | None = Query(None, description="Filter messages created before (ISO 8601)"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
) -> ContactMessageListResponse:
    """List contact messages with optional filtering and pagination."""
    repo = _require_repo()

    conditions: list[str] = []
    params: list[dict[str, Any]] = []

    if topic:
        conditions.append("c.topic = @topic")
        params.append({"name": "@topic", "value": topic})
    if status:
        conditions.append("c.status = @status")
        params.append({"name": "@status", "value": status})
    if tenant_id:
        conditions.append("c.tenant_id = @tenant_id")
        params.append({"name": "@tenant_id", "value": tenant_id})
    if created_after:
        conditions.append("c.created_at >= @created_after")
        params.append({"name": "@created_after", "value": created_after})
    if created_before:
        conditions.append("c.created_at <= @created_before")
        params.append({"name": "@created_before", "value": created_before})

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Count query
    count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
    total = 0
    async for item in repo._container.query_items(
        query=count_query,
        parameters=params if params else None,
        max_item_count=1,
    ):
        total = item

    # Data query with pagination
    data_query = (
        f"SELECT * FROM c WHERE {where_clause} "
        f"ORDER BY c.created_at DESC "
        f"OFFSET {skip} LIMIT {limit}"
    )

    messages: list[ContactMessageItem] = []
    async for item in repo._container.query_items(
        query=data_query,
        parameters=params if params else None,
        max_item_count=limit,
    ):
        messages.append(ContactMessageItem(
            id=item["id"],
            tenant_id=item["tenant_id"],
            topic=item.get("topic", ""),
            subject=item.get("subject", ""),
            message=item.get("message", ""),
            member_email=item.get("member_email"),
            member_role=item.get("member_role"),
            member_id=item.get("member_id"),
            tier=item.get("tier"),
            status=item.get("status", "new"),
            notes=item.get("notes", ""),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
        ))

    return ContactMessageListResponse(
        messages=messages,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/export",
    summary="Export contact messages as CSV",
    description="Download all matching contact messages as a CSV file.",
    status_code=200,
)
async def export_contact_messages(
    topic: str | None = Query(None, description="Filter by topic"),
    status: str | None = Query(None, description="Filter by status"),
    tenant_id: str | None = Query(None, description="Filter by tenant ID"),
    created_after: str | None = Query(None, description="Filter messages created after (ISO 8601)"),
    created_before: str | None = Query(None, description="Filter messages created before (ISO 8601)"),
) -> StreamingResponse:
    """Export contact messages as CSV (SPEC-1589)."""
    repo = _require_repo()

    conditions: list[str] = []
    params: list[dict[str, Any]] = []

    if topic:
        conditions.append("c.topic = @topic")
        params.append({"name": "@topic", "value": topic})
    if status:
        conditions.append("c.status = @status")
        params.append({"name": "@status", "value": status})
    if tenant_id:
        conditions.append("c.tenant_id = @tenant_id")
        params.append({"name": "@tenant_id", "value": tenant_id})
    if created_after:
        conditions.append("c.created_at >= @created_after")
        params.append({"name": "@created_after", "value": created_after})
    if created_before:
        conditions.append("c.created_at <= @created_before")
        params.append({"name": "@created_before", "value": created_before})

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    data_query = f"SELECT * FROM c WHERE {where_clause} ORDER BY c.created_at DESC"

    csv_fields = [
        "id", "tenant_id", "topic", "subject", "message",
        "member_email", "member_role", "member_id", "tier",
        "status", "notes", "created_at", "updated_at",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=csv_fields, extrasaction="ignore")
    writer.writeheader()

    async for item in repo._container.query_items(
        query=data_query,
        parameters=params if params else None,
    ):
        writer.writerow({f: item.get(f, "") for f in csv_fields})

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contact-messages.csv"},
    )


@router.get(
    "/{message_id}",
    response_model=ContactMessageItem,
    summary="Get a single contact message",
    description="Retrieve a single contact message by its ID.",
    status_code=200,
)
async def get_contact_message(
    message_id: str,
) -> ContactMessageItem:
    """Get a single contact message by ID (cross-partition)."""
    repo = _require_repo()

    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": message_id}]

    async for item in repo._container.query_items(
        query=query,
        parameters=params,
        max_item_count=1,
    ):
        return ContactMessageItem(
            id=item["id"],
            tenant_id=item["tenant_id"],
            topic=item.get("topic", ""),
            subject=item.get("subject", ""),
            message=item.get("message", ""),
            member_email=item.get("member_email"),
            member_role=item.get("member_role"),
            member_id=item.get("member_id"),
            tier=item.get("tier"),
            status=item.get("status", "new"),
            notes=item.get("notes", ""),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
        )

    raise HTTPException(status_code=404, detail=f"Contact message {message_id} not found")


@router.patch(
    "/{message_id}",
    response_model=ContactMessageUpdateResponse,
    summary="Update contact message status/notes",
    description="Update the status or notes on a contact message (SPEC-1592).",
    status_code=200,
)
async def update_contact_message(
    message_id: str,
    body: ContactMessageUpdateRequest,
) -> ContactMessageUpdateResponse:
    """Update status and/or notes on a contact message."""
    repo = _require_repo()

    # Validate status if provided
    if body.status is not None and body.status not in ContactMessageDocument.VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{body.status}'. "
            f"Valid values: {ContactMessageDocument.VALID_STATUSES}",
        )

    # Find the message (cross-partition)
    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": message_id}]

    existing = None
    async for item in repo._container.query_items(
        query=query,
        parameters=params,
        max_item_count=1,
    ):
        existing = item

    if existing is None:
        raise HTTPException(status_code=404, detail=f"Contact message {message_id} not found")

    # Build patch operations
    from datetime import datetime, timezone

    patch_ops: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()

    if body.status is not None:
        patch_ops.append({"op": "set", "path": "/status", "value": body.status})
        existing["status"] = body.status
    if body.notes is not None:
        patch_ops.append({"op": "set", "path": "/notes", "value": body.notes})
        existing["notes"] = body.notes

    if not patch_ops:
        raise HTTPException(status_code=400, detail="No fields to update")

    patch_ops.append({"op": "set", "path": "/updated_at", "value": now})
    existing["updated_at"] = now

    # Execute patch with partition key
    tenant_id = existing["tenant_id"]
    await repo._container.patch_item(
        item=message_id,
        partition_key=tenant_id,
        patch_operations=patch_ops,
    )

    logger.info(
        "Contact message %s updated: status=%s notes_updated=%s",
        message_id,
        body.status,
        body.notes is not None,
    )

    return ContactMessageUpdateResponse(
        ok=True,
        message=ContactMessageItem(
            id=existing["id"],
            tenant_id=existing["tenant_id"],
            topic=existing.get("topic", ""),
            subject=existing.get("subject", ""),
            message=existing.get("message", ""),
            member_email=existing.get("member_email"),
            member_role=existing.get("member_role"),
            member_id=existing.get("member_id"),
            tier=existing.get("tier"),
            status=existing.get("status", "new"),
            notes=existing.get("notes", ""),
            created_at=existing.get("created_at", ""),
            updated_at=existing.get("updated_at", ""),
        ),
    )
