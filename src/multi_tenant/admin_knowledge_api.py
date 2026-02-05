"""Admin Knowledge Base API — merchant knowledge management (WI #175).

Provides REST endpoints for the merchant admin dashboard's Knowledge Base
Manager component:

    GET    /api/admin/knowledge              — List with filtering & pagination
    GET    /api/admin/knowledge/{id}         — Get single entry
    POST   /api/admin/knowledge              — Create entry
    PUT    /api/admin/knowledge/{id}         — Update entry
    DELETE /api/admin/knowledge/{id}         — Soft-delete entry

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §7: WI #175 — Knowledge Base CRUD
    - Decision #1: TenantScopedRepository enforces tenant isolation
    - KnowledgeBaseDocument schema in cosmos_schema.py

Dependencies:
    - repository.py: KnowledgeBaseRepository (list_filtered, count_filtered,
      create, read, upsert, soft_delete)
    - cosmos_schema.py: KnowledgeBaseDocument
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import DocumentNotFoundError, KnowledgeBaseRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid entry types
# ---------------------------------------------------------------------------

VALID_ENTRY_TYPES = {"product", "faq", "policy", "custom"}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class KnowledgeEntryResponse(BaseModel):
    """A single knowledge base entry."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    tenant_id: str
    entry_type: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    language: str = "en"
    is_active: bool = True
    created_at: str
    updated_at: str


class KnowledgeListResponse(BaseModel):
    """Paginated list of knowledge base entries."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tenant_id: str
    total_count: int = Field(description="Total matching entries")
    offset: int
    limit: int
    articles: list[KnowledgeEntryResponse]


class CreateKnowledgeEntryRequest(BaseModel):
    """Request body for POST /api/admin/knowledge."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entry_type: str = Field(
        description="Entry type: product, faq, policy, or custom",
    )
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Entry title / product name",
    )
    content: str = Field(
        min_length=1,
        max_length=50000,
        description="Full text content for retrieval",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific metadata (e.g. product_id, category, price)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Search tags",
    )
    language: str = Field(
        default="en",
        max_length=10,
        description="Content language (ISO 639-1)",
    )


class UpdateKnowledgeEntryRequest(BaseModel):
    """Request body for PUT /api/admin/knowledge/{id}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entry_type: str | None = Field(
        default=None,
        description="Entry type: product, faq, policy, or custom",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Entry title / product name",
    )
    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=50000,
        description="Full text content for retrieval",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Type-specific metadata",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Search tags (replaces existing)",
    )
    language: str | None = Field(
        default=None,
        max_length=10,
        description="Content language (ISO 639-1)",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether entry is searchable",
    )


class DeleteKnowledgeEntryResponse(BaseModel):
    """Response for successful soft-delete."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    deleted_at: str


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_knowledge_repo: KnowledgeBaseRepository | None = None


def configure_admin_knowledge_services(
    knowledge_repo: KnowledgeBaseRepository,
) -> None:
    """Wire the admin knowledge API to its backing repository.

    Called during app startup after KnowledgeBaseRepository is initialised.
    """
    global _knowledge_repo
    _knowledge_repo = knowledge_repo
    logger.info("Admin knowledge base API services configured")


def _get_repo() -> KnowledgeBaseRepository:
    """Get the KnowledgeBaseRepository, raising 503 if not initialised."""
    if _knowledge_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin knowledge base services not initialised",
        )
    return _knowledge_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/knowledge", tags=["admin-knowledge"])


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge — List with filtering & pagination
# ---------------------------------------------------------------------------


@router.get("", response_model=KnowledgeListResponse)
async def list_knowledge_entries(
    entry_type: str | None = Query(
        None,
        description="Filter by type (product, faq, policy, custom)",
    ),
    language: str | None = Query(
        None,
        description="Filter by language code (e.g. en, fr, es)",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status (true/false, omit for all)",
    ),
    search: str | None = Query(
        None,
        max_length=200,
        description="Search by title (case-insensitive substring match)",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> KnowledgeListResponse:
    """List knowledge base entries for the merchant admin.

    Supports filtering by type, language, active status, and title search.
    Results are ordered by most recently updated first.
    """
    repo = _get_repo()

    # Validate entry_type if provided
    if entry_type is not None and entry_type not in VALID_ENTRY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry_type '{entry_type}'. Valid values: {sorted(VALID_ENTRY_TYPES)}",
        )

    total_count = await repo.count_filtered(
        tenant_id=ctx.tenant_id,
        entry_type=entry_type,
        language=language,
        is_active=is_active,
        search=search,
    )

    entries_raw = await repo.list_filtered(
        tenant_id=ctx.tenant_id,
        entry_type=entry_type,
        language=language,
        is_active=is_active,
        search=search,
        offset=offset,
        limit=limit,
    )

    entries = [
        KnowledgeEntryResponse(
            id=e.get("id", ""),
            tenant_id=ctx.tenant_id,
            entry_type=e.get("entry_type", "custom"),
            title=e.get("title", ""),
            content=e.get("content", ""),
            metadata=e.get("metadata", {}),
            tags=e.get("tags", []),
            language=e.get("language", "en"),
            is_active=e.get("is_active", True),
            created_at=e.get("created_at", ""),
            updated_at=e.get("updated_at", ""),
        )
        for e in entries_raw
    ]

    return KnowledgeListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        articles=entries,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/{entry_id} — Get single entry
# ---------------------------------------------------------------------------


@router.get("/{entry_id}", response_model=KnowledgeEntryResponse)
async def get_knowledge_entry(
    entry_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> KnowledgeEntryResponse:
    """Get a single knowledge base entry by ID."""
    repo = _get_repo()

    try:
        doc = await repo.read(ctx.tenant_id, entry_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge entry {entry_id} not found",
        )

    return KnowledgeEntryResponse(
        id=doc.get("id", ""),
        tenant_id=ctx.tenant_id,
        entry_type=doc.get("entry_type", "custom"),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        metadata=doc.get("metadata", {}),
        tags=doc.get("tags", []),
        language=doc.get("language", "en"),
        is_active=doc.get("is_active", True),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge — Create entry
# ---------------------------------------------------------------------------


@router.post("", response_model=KnowledgeEntryResponse, status_code=201)
async def create_knowledge_entry(
    request: CreateKnowledgeEntryRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> KnowledgeEntryResponse:
    """Create a new knowledge base entry.

    The entry is immediately active and searchable by the Knowledge
    Retrieval agent during conversations.
    """
    repo = _get_repo()

    # Validate entry_type
    if request.entry_type not in VALID_ENTRY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry_type '{request.entry_type}'. Valid values: {sorted(VALID_ENTRY_TYPES)}",
        )

    now = datetime.now(timezone.utc).isoformat()
    entry_id = str(uuid.uuid4())

    from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument

    doc = KnowledgeBaseDocument(
        id=entry_id,
        tenant_id=ctx.tenant_id,
        entry_type=request.entry_type,
        title=request.title,
        content=request.content,
        metadata=request.metadata,
        tags=request.tags,
        language=request.language,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    created = await repo.create(ctx.tenant_id, doc)

    logger.info(
        "Knowledge entry created: id=%s type=%s tenant=%s",
        entry_id,
        request.entry_type,
        ctx.tenant_id[:8],
    )

    return KnowledgeEntryResponse(
        id=entry_id,
        tenant_id=ctx.tenant_id,
        entry_type=request.entry_type,
        title=request.title,
        content=request.content,
        metadata=request.metadata,
        tags=request.tags,
        language=request.language,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


# ---------------------------------------------------------------------------
# PUT /api/admin/knowledge/{entry_id} — Update entry
# ---------------------------------------------------------------------------


@router.put("/{entry_id}", response_model=KnowledgeEntryResponse)
async def update_knowledge_entry(
    entry_id: str,
    request: UpdateKnowledgeEntryRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> KnowledgeEntryResponse:
    """Update an existing knowledge base entry.

    Only provided fields are updated. Omitted fields retain their
    current values.
    """
    repo = _get_repo()

    # Validate entry_type if provided
    if request.entry_type is not None and request.entry_type not in VALID_ENTRY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry_type '{request.entry_type}'. Valid values: {sorted(VALID_ENTRY_TYPES)}",
        )

    # Read existing document to verify it exists
    try:
        existing = await repo.read(ctx.tenant_id, entry_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge entry {entry_id} not found",
        )

    # Build patch operations from provided fields
    now = datetime.now(timezone.utc).isoformat()
    operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/updated_at", "value": now},
    ]

    if request.entry_type is not None:
        operations.append({"op": "set", "path": "/entry_type", "value": request.entry_type})
    if request.title is not None:
        operations.append({"op": "set", "path": "/title", "value": request.title})
    if request.content is not None:
        operations.append({"op": "set", "path": "/content", "value": request.content})
    if request.metadata is not None:
        operations.append({"op": "set", "path": "/metadata", "value": request.metadata})
    if request.tags is not None:
        operations.append({"op": "set", "path": "/tags", "value": request.tags})
    if request.language is not None:
        operations.append({"op": "set", "path": "/language", "value": request.language})
    if request.is_active is not None:
        operations.append({"op": "set", "path": "/is_active", "value": request.is_active})

    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=entry_id,
        operations=operations,
    )

    # Build response from existing + updates
    updated = {**existing}
    if request.entry_type is not None:
        updated["entry_type"] = request.entry_type
    if request.title is not None:
        updated["title"] = request.title
    if request.content is not None:
        updated["content"] = request.content
    if request.metadata is not None:
        updated["metadata"] = request.metadata
    if request.tags is not None:
        updated["tags"] = request.tags
    if request.language is not None:
        updated["language"] = request.language
    if request.is_active is not None:
        updated["is_active"] = request.is_active
    updated["updated_at"] = now

    logger.info(
        "Knowledge entry updated: id=%s tenant=%s",
        entry_id,
        ctx.tenant_id[:8],
    )

    return KnowledgeEntryResponse(
        id=entry_id,
        tenant_id=ctx.tenant_id,
        entry_type=updated.get("entry_type", "custom"),
        title=updated.get("title", ""),
        content=updated.get("content", ""),
        metadata=updated.get("metadata", {}),
        tags=updated.get("tags", []),
        language=updated.get("language", "en"),
        is_active=updated.get("is_active", True),
        created_at=updated.get("created_at", ""),
        updated_at=now,
    )


# ---------------------------------------------------------------------------
# DELETE /api/admin/knowledge/{entry_id} — Soft-delete entry
# ---------------------------------------------------------------------------


@router.delete("/{entry_id}", response_model=DeleteKnowledgeEntryResponse)
async def delete_knowledge_entry(
    entry_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeleteKnowledgeEntryResponse:
    """Soft-delete a knowledge base entry.

    Sets is_active = false so the entry is no longer returned by the
    Knowledge Retrieval agent during conversations. The data is preserved
    for audit purposes and can be reactivated via PUT with is_active=true.
    """
    repo = _get_repo()

    try:
        await repo.soft_delete(ctx.tenant_id, entry_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge entry {entry_id} not found",
        )

    now = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Knowledge entry soft-deleted: id=%s tenant=%s",
        entry_id,
        ctx.tenant_id[:8],
    )

    return DeleteKnowledgeEntryResponse(
        id=entry_id,
        deleted_at=now,
    )
