# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Admin Audit Log Query API — compliance reporting and inspection (WI #141).

Provides REST endpoints for querying the append-only audit log. Merchants
can inspect all auditable events within their tenant for GDPR compliance,
security investigation, and operational debugging.

Endpoints:
    GET /api/audit          — Query audit events with filtering & pagination
    GET /api/audit/export   — CSV export of audit events

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints.

The audit log is append-only and survives tenant deletion. Events are
retained for 1 year per Decision #13.

Architecture references:
    - Decision #13: Append-only audit log, 12 event types, 1-year retention
    - cosmos_schema.py: AuditLogDocument, AuditEventType
    - repository.py: AuditLogRepository

Dependencies:
    - repository.py: AuditLogRepository (query_by_tenant, count_by_tenant)
    - cosmos_schema.py: AuditEventType (12 event types)
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.multi_tenant.audit_sanitizer import sanitize_audit_payload
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid event types for filtering
# ---------------------------------------------------------------------------

VALID_EVENT_TYPES = {e.value for e in AuditEventType}


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AuditEventResponse(BaseModel):
    """A single audit log event."""

    id: str
    tenant_id: str
    event_type: str
    timestamp: str
    actor: str | None = None
    customer_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None


class AuditListResponse(BaseModel):
    """Paginated list of audit events."""

    tenant_id: str
    total_count: int
    offset: int
    limit: int
    events: list[AuditEventResponse]


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_audit_repo: Any | None = None


def configure_admin_audit_services(
    audit_repo: Any,
) -> None:
    """Wire the admin audit API to its backing repository.

    Called during app startup after AuditLogRepository is initialised.
    """
    global _audit_repo
    _audit_repo = audit_repo
    logger.info("Admin audit log API services configured")


def _get_repo() -> Any:
    if _audit_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Audit log services not initialised",
        )
    return _audit_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/audit", tags=["admin-audit"])


# ---------------------------------------------------------------------------
# GET /api/audit — Query audit events with filtering & pagination
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=AuditListResponse,
    summary="Query audit log events",
    description=(
        "Returns a paginated list of audit log events. Supports filtering by event type, customer ID, and date range, "
        "ordered by most recent first."
    ),
    responses={
        400: {"description": "Invalid event_type filter value"},
        500: {"description": "Audit log query failed"},
        503: {"description": "Audit log services not initialized"},
    },
)
async def list_audit_events(
    event_type: str | None = Query(
        None,
        description="Filter by event type (e.g., CONSENT_CHANGED, DATA_EXPORTED)",
    ),
    customer_id: str | None = Query(
        None,
        description="Filter by customer ID (exact match)",
    ),
    date_from: str | None = Query(
        None,
        description="Start date (ISO 8601, default: 30 days ago)",
    ),
    date_to: str | None = Query(
        None,
        description="End date (ISO 8601, default: now)",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Page size (max 1000)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AuditListResponse:
    """Query audit log events for the authenticated tenant.

    Supports filtering by event type, customer ID, and date range.
    Results are ordered by most recent first.
    """
    repo = _get_repo()

    # Validate event_type if provided
    if event_type is not None and event_type not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type '{event_type}'. Valid values: {sorted(VALID_EVENT_TYPES)}",
        )

    # Default date range: last 30 days
    now = datetime.now(UTC)
    if date_from is None:
        date_from = (now - timedelta(days=30)).isoformat()
    if date_to is None:
        date_to = now.isoformat()

    # Build query filters
    filters: dict[str, Any] = {
        "date_from": date_from,
        "date_to": date_to,
    }
    if event_type:
        filters["event_type"] = event_type
    if customer_id:
        filters["customer_id"] = customer_id

    # Query with count
    try:
        total_count = await repo.count_by_tenant(
            tenant_id=ctx.tenant_id,
            **filters,
        )
        events_raw = await repo.query_by_tenant(
            tenant_id=ctx.tenant_id,
            offset=offset,
            limit=limit,
            **filters,
        )
    except Exception:
        logger.exception("Audit log query failed: tenant=%s", ctx.tenant_id[:8])
        raise HTTPException(
            status_code=500,
            detail="Failed to query audit log",
        )

    events = [
        AuditEventResponse(
            id=e.get("id", ""),
            tenant_id=ctx.tenant_id,
            event_type=e.get("event_type", ""),
            timestamp=e.get("timestamp", ""),
            actor=e.get("actor"),
            customer_id=e.get("customer_id"),
            details=sanitize_audit_payload(e.get("payload") or e.get("details") or {}),
            trace_id=e.get("trace_id"),
        )
        for e in events_raw
    ]

    return AuditListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        events=events,
    )


# ---------------------------------------------------------------------------
# GET /api/audit/export — CSV export of audit events
# ---------------------------------------------------------------------------


@router.get(
    "/export",
    summary="Export audit log as CSV",
    description=(
        "Exports audit log events as a downloadable CSV file. Same filtering as the query endpoint but returns all "
        "matching events."
    ),
    responses={
        400: {"description": "Invalid event_type filter value"},
        500: {"description": "Audit log export failed"},
        503: {"description": "Audit log services not initialized"},
    },
)
async def export_audit_events(
    event_type: str | None = Query(None),
    customer_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    ctx: TenantContext = Depends(get_tenant_context),
) -> StreamingResponse:
    """Export audit log events as CSV.

    Same filtering as GET /api/audit but returns all matching events
    as a downloadable CSV file.
    """
    repo = _get_repo()

    if event_type is not None and event_type not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type '{event_type}'.",
        )

    now = datetime.now(UTC)
    if date_from is None:
        date_from = (now - timedelta(days=30)).isoformat()
    if date_to is None:
        date_to = now.isoformat()

    filters: dict[str, Any] = {
        "date_from": date_from,
        "date_to": date_to,
    }
    if event_type:
        filters["event_type"] = event_type
    if customer_id:
        filters["customer_id"] = customer_id

    try:
        events_raw = await repo.query_by_tenant(
            tenant_id=ctx.tenant_id,
            offset=0,
            limit=10000,  # CSV export limit
            **filters,
        )
    except Exception:
        logger.exception("Audit log export failed: tenant=%s", ctx.tenant_id[:8])
        raise HTTPException(
            status_code=500,
            detail="Failed to export audit log",
        )

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "event_type",
            "timestamp",
            "actor",
            "customer_id",
            "trace_id",
            "details",
        ]
    )

    import json

    for e in events_raw:
        writer.writerow(
            [
                e.get("id", ""),
                e.get("event_type", ""),
                e.get("timestamp", ""),
                e.get("actor", ""),
                e.get("customer_id", ""),
                e.get("trace_id", ""),
                json.dumps(sanitize_audit_payload(e.get("payload") or e.get("details") or {})),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit-log-{ctx.tenant_id[:8]}.csv",
        },
    )
