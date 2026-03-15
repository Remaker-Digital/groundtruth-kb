"""Admin Knowledge Base API — merchant knowledge management (WI #175).

Provides REST endpoints for the merchant admin dashboard's Knowledge Base
Manager component:

    GET    /api/admin/knowledge              — List with filtering & pagination
    GET    /api/admin/knowledge/{id}         — Get single entry
    GET    /api/admin/knowledge/{id}/chunks  — Chunk preview (C5)
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

import csv
import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.activation_service import get_activation_service
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import DocumentNotFoundError, KnowledgeBaseRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid entry types
# ---------------------------------------------------------------------------

VALID_ENTRY_TYPES = {"product", "faq", "policy", "custom", "article"}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class KnowledgeEntryResponse(CamelCaseModel):
    """A single knowledge base entry."""


    id: str
    tenant_id: str
    entry_type: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    language: str = "en"
    is_active: bool = True
    category: str | None = Field(default=None, description="Article category (e.g. Shipping, Returns, Product Info)")
    status: str = Field(default="draft", description="Article status: published | draft | archived")
    created_at: str
    updated_at: str
    # Staleness fields (WI #219-221)
    staleness_score: float | None = Field(default=None, description="0.0 (fresh) to 1.0 (stale)")
    staleness_category: str | None = Field(default=None, description="fresh | aging | stale | very_stale")
    last_verified_at: str | None = Field(default=None, description="Last human verification timestamp")
    embedded_at: str | None = Field(default=None, description="Last embedding timestamp")
    source_type: str | None = Field(default=None, description="manual | pdf | docx | csv | url")
    source_filename: str | None = None
    source_url: str | None = None


class KnowledgeListResponse(CamelCaseModel):
    """Paginated list of knowledge base entries."""


    tenant_id: str
    total_count: int = Field(description="Total matching entries")
    offset: int
    limit: int
    articles: list[KnowledgeEntryResponse]


class CreateKnowledgeEntryRequest(CamelCaseModel):
    """Request body for POST /api/admin/knowledge."""


    entry_type: str = Field(
        default="article",
        description="Entry type: product, faq, policy, article, or custom",
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
    category: str | None = Field(
        default=None,
        max_length=200,
        description="Article category (e.g. Shipping, Returns, Product Info)",
    )
    status: str = Field(
        default="draft",
        description="Article status: published, draft, or archived",
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


class UpdateKnowledgeEntryRequest(CamelCaseModel):
    """Request body for PUT /api/admin/knowledge/{id}."""


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
    category: str | None = Field(
        default=None,
        max_length=200,
        description="Article category (e.g. Shipping, Returns, Product Info)",
    )
    status: str | None = Field(
        default=None,
        description="Article status: published, draft, or archived",
    )


class DeleteKnowledgeEntryResponse(CamelCaseModel):
    """Response for successful soft-delete."""


    id: str
    deleted_at: str


class UploadResultResponse(CamelCaseModel):
    """Response for document upload (WI #214)."""


    source_type: str = Field(description="pdf | docx | csv | txt | url")
    source_filename: str | None = Field(default=None, description="Original filename")
    source_url: str | None = Field(default=None, description="Source URL if URL import")
    entries_created: int = Field(description="Number of KB entries created")
    total_chars: int = Field(description="Total characters extracted")
    entry_ids: list[str] = Field(description="IDs of created entries")
    parent_entry_id: str | None = Field(default=None, description="Parent ID for multi-chunk documents")


class URLImportRequest(CamelCaseModel):
    """Request body for POST /api/admin/knowledge/import-url."""


    url: str = Field(description="URL to scrape and import")
    entry_type: str = Field(
        default="custom",
        description="Entry type for imported content",
    )
    crawl: bool = Field(
        default=False,
        description="If true, follow same-domain links and import multiple pages",
    )
    max_pages: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of pages to crawl (1-50)",
    )


class StalenessScoreResponse(CamelCaseModel):
    """Staleness score for a single entry."""


    id: str
    staleness_score: float
    staleness_category: str
    last_verified_at: str | None = None
    embedded_at: str | None = None


class StalenessSummaryResponse(CamelCaseModel):
    """Summary of staleness across the tenant's KB."""


    total_entries: int
    avg_staleness_score: float
    fresh_count: int
    aging_count: int
    stale_count: int
    very_stale_count: int
    needs_attention: int


class StaleEntriesResponse(CamelCaseModel):
    """List of stale entries."""


    entries: list[StalenessScoreResponse]
    threshold: float


class ConflictPairResponse(CamelCaseModel):
    """A pair of KB entries with a detected conflict."""


    entry_a_id: str
    entry_a_title: str
    entry_b_id: str
    entry_b_title: str
    conflict_type: str = Field(description="near_duplicate | conflicting | topical_overlap | similar_titles")
    severity: str = Field(description="high | medium | low")
    embedding_similarity: float
    content_overlap: float
    title_similarity: float
    conflicting_facts: list[str] = Field(default_factory=list)
    resolution: str


class ScanResultResponse(CamelCaseModel):
    """Result of a full KB conflict scan."""


    tenant_id: str
    scanned_at: str
    total_entries_scanned: int
    entries_with_embeddings: int
    entries_without_embeddings: int
    conflicts: list[ConflictPairResponse]
    high_count: int
    medium_count: int
    low_count: int
    scan_duration_ms: int


class ConfigConflictRequest(CamelCaseModel):
    """Request body for config-vs-KB conflict check (SPEC-1714)."""

    return_policy: str | None = None
    shipping_info: str | None = None
    brand_voice: str | None = None


class ConfigConflictItem(CamelCaseModel):
    """A single config-vs-KB conflict."""

    config_field: str
    config_value: str
    article_id: str
    article_title: str
    conflicting_facts: list[str] = Field(default_factory=list)
    resolution: str


class ConfigConflictResponse(CamelCaseModel):
    """Result of config-vs-KB conflict check (SPEC-1714)."""

    tenant_id: str
    scanned_at: str
    config_fields_checked: int
    articles_checked: int
    conflicts: list[ConfigConflictItem]
    scan_duration_ms: int


class ChunkPreviewItem(CamelCaseModel):
    """A single chunk in the chunk preview response (C5)."""


    chunk_index: int
    title: str
    text: str
    char_count: int
    estimated_tokens: int


class ChunkPreviewResponse(CamelCaseModel):
    """Response for GET /api/admin/knowledge/{entry_id}/chunks (C5).

    Returns a preview of how a KB article would be chunked by the
    document parser, including per-chunk metadata for visualization.
    """


    entry_id: str
    title: str
    total_chars: int
    total_chunks: int
    chunk_size: int = Field(description="Target chunk size in tokens")
    chunk_overlap: int = Field(description="Overlap between chunks in tokens")
    chunks: list[ChunkPreviewItem]


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_knowledge_repo: KnowledgeBaseRepository | None = None
_knowledge_vectorizer: Any = None  # KnowledgeVectorizer (optional)
_staleness_service: Any = None  # StalenessService (optional)
_conflict_scanner: Any = None  # KBConflictScanner (optional)


def configure_admin_knowledge_services(
    knowledge_repo: KnowledgeBaseRepository,
    knowledge_vectorizer: Any = None,
    staleness_service: Any = None,
    conflict_scanner: Any = None,
) -> None:
    """Wire the admin knowledge API to its backing repository and vectorizer.

    Called during app startup after KnowledgeBaseRepository is initialised.
    When knowledge_vectorizer is provided, KB entries are automatically
    embedded on create and update (WI #210).

    Args:
        knowledge_repo: KnowledgeBaseRepository instance.
        knowledge_vectorizer: Optional KnowledgeVectorizer for auto-embedding.
        staleness_service: Optional StalenessService for freshness tracking.
    """
    global _knowledge_repo, _knowledge_vectorizer, _staleness_service, _conflict_scanner
    _knowledge_repo = knowledge_repo
    _knowledge_vectorizer = knowledge_vectorizer
    _staleness_service = staleness_service
    _conflict_scanner = conflict_scanner
    vectorizer_status = "enabled" if knowledge_vectorizer else "disabled"
    staleness_status = "enabled" if staleness_service else "disabled"
    scanner_status = "enabled" if conflict_scanner else "disabled"
    logger.info(
        "Admin knowledge base API services configured (vectorization=%s, staleness=%s, scanner=%s)",
        vectorizer_status, staleness_status, scanner_status,
    )


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


def _build_entry_response(entry: dict[str, Any], tenant_id: str) -> KnowledgeEntryResponse:
    """Build a KnowledgeEntryResponse from a raw entry dict."""
    from src.multi_tenant.staleness_service import classify_staleness, compute_staleness_score

    score = entry.get("staleness_score")
    if score is None:
        # Compute on-the-fly when staleness_score has not been persisted yet.
        # This handles articles created by the Setup Wizard or manual entry
        # that haven't had a staleness scan run against them.
        score = compute_staleness_score(entry)
    staleness_cat = classify_staleness(score)

    return KnowledgeEntryResponse(
        id=entry.get("id", ""),
        tenant_id=tenant_id,
        entry_type=entry.get("entry_type", "custom"),
        title=entry.get("title", ""),
        content=entry.get("content", ""),
        metadata=entry.get("metadata", {}),
        tags=entry.get("tags", []),
        language=entry.get("language", "en"),
        is_active=entry.get("is_active", True),
        category=entry.get("category"),
        status=entry.get("status", "draft"),
        created_at=entry.get("created_at", ""),
        updated_at=entry.get("updated_at", ""),
        staleness_score=score,
        staleness_category=staleness_cat,
        last_verified_at=entry.get("last_verified_at"),
        embedded_at=entry.get("embedded_at"),
        source_type=entry.get("source_type"),
        source_filename=entry.get("source_filename"),
        source_url=entry.get("source_url"),
    )


async def _signal_kb_draft(ctx: "TenantContext") -> None:
    """Signal that KB content has changed by touching the draft document.

    Best-effort — failure here must NOT block the KB write that already
    succeeded.  The signal field ``kb_modified_at`` appears in the
    Activation Dialog's change summary so the owner knows KB content
    was modified since the last activation.

    D16 fix — KB Save→Activate integration.
    """
    try:
        from src.multi_tenant.cosmos_schema import TenantTier

        activation_svc = get_activation_service()
        tier = TenantTier(ctx.tier) if ctx.tier else TenantTier.STARTER
        await activation_svc.ensure_draft_for_signal(
            tenant_id=ctx.tenant_id,
            tier=tier,
            signal_field="kb_modified_at",
            actor=f"user:{ctx.user_id}" if ctx.user_id else "admin",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "KB draft signal failed (non-blocking): tenant=%s error=%s",
            ctx.tenant_id[:8] if ctx.tenant_id else "?",
            exc,
        )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge — List with filtering & pagination
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=KnowledgeListResponse,
    summary="List knowledge base entries",
    description="Returns a paginated list of knowledge base entries. Supports filtering by type, language, active status, and title search.",
    responses={
        400: {"description": "Invalid entry_type filter value"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
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
        description="Search by title or content (case-insensitive substring match)",
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

    entries = [_build_entry_response(e, ctx.tenant_id) for e in entries_raw]

    return KnowledgeListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        articles=entries,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/export — CSV export (WI #217)
# IMPORTANT: Registered BEFORE /{entry_id} to avoid path parameter shadowing.
# ---------------------------------------------------------------------------


@router.get(
    "/export",
    summary="Export knowledge base as CSV",
    description="Exports all knowledge base entries as a downloadable CSV file with columns for id, type, title, content, tags, language, active status, source info, and timestamps.",
    responses={
        503: {"description": "Knowledge base services not initialized"},
    },
)
async def export_knowledge_entries(
    ctx: TenantContext = Depends(get_tenant_context),
) -> StreamingResponse:
    """Export all knowledge base entries as CSV.

    Columns: id, entry_type, title, content, tags, language, is_active,
    source_type, source_filename, source_url, created_at, updated_at.
    """
    repo = _get_repo()

    entries = await repo.list_filtered(
        tenant_id=ctx.tenant_id,
        offset=0,
        limit=10000,  # Practical upper bound
    )

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id",
        "entry_type",
        "title",
        "content",
        "tags",
        "language",
        "is_active",
        "source_type",
        "source_filename",
        "source_url",
        "created_at",
        "updated_at",
    ])

    for entry in entries:
        tags_str = ";".join(entry.get("tags", []))
        writer.writerow([
            entry.get("id", ""),
            entry.get("entry_type", ""),
            entry.get("title", ""),
            entry.get("content", ""),
            tags_str,
            entry.get("language", "en"),
            entry.get("is_active", True),
            entry.get("source_type", "manual"),
            entry.get("source_filename", ""),
            entry.get("source_url", ""),
            entry.get("created_at", ""),
            entry.get("updated_at", ""),
        ])

    logger.info(
        "KB export: entries=%d tenant=%s",
        len(entries),
        ctx.tenant_id[:8],
    )

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=knowledge-base-export.csv"},
    )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/staleness — Staleness summary (WI #221)
# IMPORTANT: Registered BEFORE /{entry_id} to avoid path parameter shadowing.
# ---------------------------------------------------------------------------


@router.get(
    "/staleness",
    response_model=StalenessSummaryResponse,
    summary="Get content staleness summary",
    description="Returns a summary of content staleness across the knowledge base, including counts of fresh, aging, stale, and very stale entries with the average staleness score.",
    responses={
        503: {"description": "Staleness service not initialized"},
    },
)
async def get_staleness_summary(
    ctx: TenantContext = Depends(get_tenant_context),
) -> StalenessSummaryResponse:
    """Get a summary of content staleness across the knowledge base.

    Returns counts of fresh, aging, stale, and very stale entries
    along with the average staleness score.
    """
    if _staleness_service is None:
        raise HTTPException(status_code=503, detail="Staleness service not initialised")

    summary = await _staleness_service.get_summary(ctx.tenant_id)
    return StalenessSummaryResponse(**summary)


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/stale — List stale entries (WI #221)
# IMPORTANT: Registered BEFORE /{entry_id} to avoid path parameter shadowing.
# ---------------------------------------------------------------------------


@router.get(
    "/stale",
    response_model=StaleEntriesResponse,
    summary="List stale knowledge entries",
    description="Lists knowledge base entries above the staleness threshold. Default threshold is 0.6, returning stale and very stale entries.",
    responses={
        503: {"description": "Staleness service not initialized"},
    },
)
async def list_stale_entries(
    threshold: float = Query(
        0.6,
        ge=0.0,
        le=1.0,
        description="Minimum staleness score to include",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> StaleEntriesResponse:
    """List knowledge base entries above the staleness threshold.

    Default threshold is 0.6 (stale + very stale entries).
    """
    if _staleness_service is None:
        raise HTTPException(status_code=503, detail="Staleness service not initialised")

    stale = await _staleness_service.list_stale(ctx.tenant_id, threshold=threshold)
    entries = [
        StalenessScoreResponse(
            id=e["id"],
            staleness_score=e["staleness_score"],
            staleness_category=e["staleness_category"],
            last_verified_at=e.get("last_verified_at"),
            embedded_at=e.get("embedded_at"),
        )
        for e in stale
    ]
    return StaleEntriesResponse(entries=entries, threshold=threshold)


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/{entry_id} — Get single entry
# ---------------------------------------------------------------------------


@router.get(
    "/{entry_id}",
    response_model=KnowledgeEntryResponse,
    summary="Get knowledge base entry",
    description="Returns a single knowledge base entry by ID.",
    responses={
        404: {"description": "Knowledge entry not found"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
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

    return _build_entry_response(doc, ctx.tenant_id)


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/{entry_id}/chunks — Chunk preview (C5)
# ---------------------------------------------------------------------------


@router.get(
    "/{entry_id}/chunks",
    response_model=ChunkPreviewResponse,
    summary="Preview KB article chunking",
    description=(
        "Returns a preview of how a knowledge base article's content "
        "would be split into chunks by the document parser. Useful for "
        "visualizing chunk boundaries, sizes, and overlap before embedding."
    ),
    responses={
        404: {"description": "Knowledge entry not found"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
async def preview_entry_chunks(
    entry_id: str,
    chunk_size: int = Query(
        None,
        ge=50,
        le=2000,
        description="Target chunk size in tokens (default: parser default, typically 400)",
    ),
    chunk_overlap: int = Query(
        None,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens (default: parser default, typically 50)",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ChunkPreviewResponse:
    """Preview how a KB article would be chunked.

    Reads the article content and runs it through the document parser's
    ``chunk_text()`` function, returning the resulting chunks with
    per-chunk metadata (index, title, text, char count, estimated tokens).

    Optional ``chunk_size`` and ``chunk_overlap`` parameters allow
    experimenting with different chunking strategies without persisting
    any changes.
    """
    from src.multi_tenant.document_parser import (
        CHARS_PER_TOKEN,
        DEFAULT_CHUNK_OVERLAP,
        DEFAULT_CHUNK_SIZE,
        chunk_text,
    )

    repo = _get_repo()

    try:
        doc = await repo.read(ctx.tenant_id, entry_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge entry {entry_id} not found",
        )

    effective_chunk_size = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
    effective_chunk_overlap = chunk_overlap if chunk_overlap is not None else DEFAULT_CHUNK_OVERLAP

    content = doc.get("content", "")
    title = doc.get("title", "")

    chunks = chunk_text(
        text=content,
        title=title,
        chunk_size=effective_chunk_size,
        chunk_overlap=effective_chunk_overlap,
    )

    chars_per_tok = CHARS_PER_TOKEN if CHARS_PER_TOKEN > 0 else 4

    preview_items = [
        ChunkPreviewItem(
            chunk_index=c.chunk_index,
            title=c.title,
            text=c.text,
            char_count=len(c.text),
            estimated_tokens=max(1, len(c.text) // chars_per_tok),
        )
        for c in chunks
    ]

    return ChunkPreviewResponse(
        entry_id=entry_id,
        title=title,
        total_chars=len(content),
        total_chunks=len(preview_items),
        chunk_size=effective_chunk_size,
        chunk_overlap=effective_chunk_overlap,
        chunks=preview_items,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge — Create entry
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=KnowledgeEntryResponse,
    status_code=201,
    summary="Create knowledge base entry",
    description="Creates a new knowledge base entry. The entry is immediately active and searchable by the Knowledge Retrieval agent.",
    responses={
        400: {"description": "Invalid entry_type value"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
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
        category=request.category,
        status=request.status,
        tags=request.tags,
        language=request.language,
        is_active=(request.status != "archived"),
        staleness_score=0.0,
        last_verified_at=now,
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

    # Signal draft that KB content changed (D16 fix)
    await _signal_kb_draft(ctx)

    # Trigger async embedding (WI #210 — non-blocking, best-effort)
    if _knowledge_vectorizer:
        try:
            entry_dict = doc.model_dump() if hasattr(doc, "model_dump") else doc.dict()
            await _knowledge_vectorizer.embed_entry(ctx.tenant_id, entry_dict)
        except Exception as embed_exc:
            logger.warning(
                "KB entry embedding failed (non-blocking): id=%s error=%s",
                entry_id, embed_exc,
            )

    created_dict = {
        "id": entry_id,
        "entry_type": request.entry_type,
        "title": request.title,
        "content": request.content,
        "metadata": request.metadata,
        "tags": request.tags,
        "language": request.language,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    return _build_entry_response(created_dict, ctx.tenant_id)


# ---------------------------------------------------------------------------
# PUT /api/admin/knowledge/{entry_id} — Update entry
# ---------------------------------------------------------------------------


@router.put(
    "/{entry_id}",
    response_model=KnowledgeEntryResponse,
    summary="Update knowledge base entry",
    description="Updates an existing knowledge base entry. Only provided fields are updated; omitted fields retain their current values.",
    responses={
        400: {"description": "Invalid entry_type value"},
        404: {"description": "Knowledge entry not found"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
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
    if request.category is not None:
        operations.append({"op": "set", "path": "/category", "value": request.category})
    if request.status is not None:
        operations.append({"op": "set", "path": "/status", "value": request.status})

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
    if request.category is not None:
        updated["category"] = request.category
    if request.status is not None:
        updated["status"] = request.status
    updated["updated_at"] = now

    logger.info(
        "Knowledge entry updated: id=%s tenant=%s",
        entry_id,
        ctx.tenant_id[:8],
    )

    # Signal draft that KB content changed (D16 fix)
    await _signal_kb_draft(ctx)

    # Re-embed if title or content changed (WI #210 — content hash will detect changes)
    if _knowledge_vectorizer and (request.title is not None or request.content is not None):
        try:
            await _knowledge_vectorizer.embed_entry(ctx.tenant_id, updated)
        except Exception as embed_exc:
            logger.warning(
                "KB entry re-embedding failed (non-blocking): id=%s error=%s",
                entry_id, embed_exc,
            )

    updated["id"] = entry_id
    updated["updated_at"] = now
    return _build_entry_response(updated, ctx.tenant_id)


# ---------------------------------------------------------------------------
# DELETE /api/admin/knowledge/{entry_id} — Soft-delete entry
# ---------------------------------------------------------------------------


@router.delete(
    "/{entry_id}",
    response_model=DeleteKnowledgeEntryResponse,
    summary="Soft-delete knowledge base entry",
    description="Sets is_active to false so the entry is no longer returned by the Knowledge Retrieval agent. The data is preserved for audit purposes and can be reactivated via PUT.",
    responses={
        404: {"description": "Knowledge entry not found"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
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

    # Signal draft that KB content changed (D16 fix)
    await _signal_kb_draft(ctx)

    return DeleteKnowledgeEntryResponse(
        id=entry_id,
        deleted_at=now,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/upload — File upload (WI #214)
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=UploadResultResponse,
    status_code=201,
    summary="Upload document to knowledge base",
    description="Uploads a document (PDF, DOCX, CSV, or TXT) and parses it into knowledge base entries. Multi-page documents are chunked with paragraph-aware splitting.",
    responses={
        400: {"description": "Invalid entry_type, missing filename, or empty file"},
        422: {"description": "Document parsing failed or no content extracted"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
async def upload_knowledge_document(
    file: UploadFile = File(..., description="PDF, DOCX, CSV, or TXT file"),
    entry_type: str = Query(
        "custom",
        description="Default entry type for parsed entries (product, faq, policy, custom)",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> UploadResultResponse:
    """Upload a document and parse it into knowledge base entries.

    Supported formats:
        - **PDF**: Text extracted page-by-page, chunked into entries
        - **DOCX**: Paragraphs extracted with heading preservation
        - **CSV**: Each row becomes a separate entry (requires title,content columns)
        - **TXT**: Plain text chunked into entries

    Multi-page documents are automatically chunked with paragraph-aware
    splitting (~400 tokens per chunk, 50-token overlap). Each chunk becomes
    a separate KB entry linked via parent_entry_id.

    Size limits: PDF 50 MB, others 4 MB.
    """
    repo = _get_repo()

    if entry_type not in VALID_ENTRY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry_type '{entry_type}'. Valid values: {sorted(VALID_ENTRY_TYPES)}",
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Validate file type and size
    from src.multi_tenant.document_parser import validate_file

    validation_error = validate_file(file.filename, file_size)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    # Parse the document
    from src.multi_tenant.document_parser import chunks_to_kb_entries, parse_file

    parse_result = await parse_file(file_content, file.filename)

    if not parse_result.success:
        raise HTTPException(
            status_code=422,
            detail=f"Document parsing failed: {parse_result.error}",
        )

    # Convert chunks to KB entries
    entries = chunks_to_kb_entries(
        parse_result=parse_result,
        tenant_id=ctx.tenant_id,
        default_entry_type=entry_type,
    )

    if not entries:
        raise HTTPException(
            status_code=422,
            detail="No content could be extracted from the document.",
        )

    # Create entries in Cosmos DB
    entry_ids: list[str] = []
    from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument

    for entry_dict in entries:
        doc = KnowledgeBaseDocument(**entry_dict)
        await repo.create(ctx.tenant_id, doc)
        entry_ids.append(entry_dict["id"])

    parent_id = entries[0].get("parent_entry_id") if len(entries) > 1 else None

    logger.info(
        "Document uploaded: file=%s type=%s entries=%d chars=%d tenant=%s",
        file.filename,
        parse_result.source_type,
        len(entries),
        parse_result.total_chars,
        ctx.tenant_id[:8],
    )

    # Signal draft that KB content changed (D16 fix)
    await _signal_kb_draft(ctx)

    # Trigger batch embedding (non-blocking, best-effort)
    if _knowledge_vectorizer:
        try:
            await _knowledge_vectorizer.embed_batch(ctx.tenant_id, entries)
        except Exception as embed_exc:
            logger.warning(
                "Batch embedding after upload failed (non-blocking): %s", embed_exc
            )

    return UploadResultResponse(
        source_type=parse_result.source_type,
        source_filename=file.filename,
        entries_created=len(entries),
        total_chars=parse_result.total_chars,
        entry_ids=entry_ids,
        parent_entry_id=parent_id,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/import-url — URL import (WI #215)
# ---------------------------------------------------------------------------


@router.post(
    "/import-url",
    response_model=UploadResultResponse,
    status_code=201,
    summary="Import knowledge from URL",
    description="Scrapes a web page, extracts main text content, and creates knowledge base entries. Navigation, scripts, and non-content elements are stripped.",
    responses={
        400: {"description": "Invalid entry_type or malformed URL"},
        422: {"description": "URL import failed or no content extracted"},
        503: {"description": "Knowledge base services not initialized"},
    },
)
async def import_knowledge_from_url(
    request: URLImportRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> UploadResultResponse:
    """Import knowledge from a web page URL.

    Scrapes the page, extracts main text content, and creates KB entries.
    Navigation, scripts, and non-content elements are stripped.

    When ``crawl`` is true, follows same-domain links starting from the
    given URL and imports up to ``max_pages`` pages (default 10, max 50).

    Maximum page size: 4 MB per page.
    """
    repo = _get_repo()

    if request.entry_type not in VALID_ENTRY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry_type '{request.entry_type}'. Valid values: {sorted(VALID_ENTRY_TYPES)}",
        )

    # Validate URL
    url = request.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://",
        )

    from src.multi_tenant.document_parser import chunks_to_kb_entries, crawl_url, parse_url

    all_entries: list[dict[str, Any]] = []
    total_chars = 0
    source_type = "url"

    if request.crawl:
        # ---- Crawl mode: follow same-domain links ----
        crawl_results = await crawl_url(
            start_url=url,
            max_pages=request.max_pages,
        )

        if not crawl_results:
            raise HTTPException(
                status_code=422,
                detail="Crawl completed but no pages could be parsed. "
                "Check that the URL is reachable and contains HTML content.",
            )

        for page_result in crawl_results:
            page_entries = chunks_to_kb_entries(
                parse_result=page_result,
                tenant_id=ctx.tenant_id,
                default_entry_type=request.entry_type,
            )
            all_entries.extend(page_entries)
            total_chars += page_result.total_chars

        logger.info(
            "URL crawl: url=%s pages=%d entries=%d chars=%d tenant=%s",
            url,
            len(crawl_results),
            len(all_entries),
            total_chars,
            ctx.tenant_id[:8],
        )
    else:
        # ---- Single page mode ----
        parse_result = await parse_url(url)

        if not parse_result.success:
            raise HTTPException(
                status_code=422,
                detail=f"URL import failed: {parse_result.error}",
            )

        all_entries = chunks_to_kb_entries(
            parse_result=parse_result,
            tenant_id=ctx.tenant_id,
            default_entry_type=request.entry_type,
        )
        total_chars = parse_result.total_chars

        logger.info(
            "URL imported: url=%s entries=%d chars=%d tenant=%s",
            url,
            len(all_entries),
            total_chars,
            ctx.tenant_id[:8],
        )

    if not all_entries:
        raise HTTPException(
            status_code=422,
            detail="No content could be extracted from the URL.",
        )

    # Create entries in Cosmos DB
    entry_ids: list[str] = []
    from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument

    for entry_dict in all_entries:
        doc = KnowledgeBaseDocument(**entry_dict)
        await repo.create(ctx.tenant_id, doc)
        entry_ids.append(entry_dict["id"])

    parent_id = all_entries[0].get("parent_entry_id") if len(all_entries) > 1 else None

    # Signal draft that KB content changed (D16 fix)
    await _signal_kb_draft(ctx)

    # Trigger batch embedding (non-blocking, best-effort)
    if _knowledge_vectorizer:
        try:
            await _knowledge_vectorizer.embed_batch(ctx.tenant_id, all_entries)
        except Exception as embed_exc:
            logger.warning(
                "Batch embedding after URL import failed (non-blocking): %s", embed_exc
            )

    return UploadResultResponse(
        source_type=source_type,
        source_url=url,
        entries_created=len(all_entries),
        total_chars=total_chars,
        entry_ids=entry_ids,
        parent_entry_id=parent_id,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/{entry_id}/verify — Mark as verified (WI #221)
# ---------------------------------------------------------------------------


@router.post(
    "/{entry_id}/verify",
    response_model=StalenessScoreResponse,
    summary="Mark entry as verified",
    description="Marks a knowledge base entry as verified by a human, updating last_verified_at and recalculating the staleness score.",
    responses={
        404: {"description": "Knowledge entry not found"},
        503: {"description": "Staleness service not initialized"},
    },
)
async def verify_knowledge_entry(
    entry_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> StalenessScoreResponse:
    """Mark a knowledge base entry as verified by a human.

    Updates `last_verified_at` to the current time and recalculates
    the staleness score. This is the primary way merchants confirm
    that content is still current and accurate.
    """
    if _staleness_service is None:
        raise HTTPException(status_code=503, detail="Staleness service not initialised")

    try:
        result = await _staleness_service.verify_entry(ctx.tenant_id, entry_id)
    except Exception as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=f"Knowledge entry {entry_id} not found")
        raise

    return StalenessScoreResponse(**result)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/scan — Trigger conflict scan
# ---------------------------------------------------------------------------


@router.post(
    "/scan",
    response_model=ScanResultResponse,
    summary="Scan for conflicts and duplicates",
    description=(
        "Runs an on-demand scan of all active knowledge base entries to "
        "identify near-duplicates, conflicting information, topical overlaps, "
        "and similar titles. Results are cached for 5 minutes."
    ),
    responses={
        503: {"description": "Conflict scanner not initialized"},
    },
)
async def scan_for_conflicts(
    force: bool = Query(
        False,
        description="If true, bypass the 5-minute cache and re-scan",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ScanResultResponse:
    """Scan the knowledge base for conflicts and duplicates.

    Analyses all active entries using embedding similarity, title comparison,
    content overlap, and factual conflict detection. No external API calls —
    uses pre-computed embeddings only.
    """
    if _conflict_scanner is None:
        raise HTTPException(
            status_code=503,
            detail="Conflict scanner not initialised",
        )

    result = await _conflict_scanner.scan(ctx.tenant_id, force=force)

    return ScanResultResponse(
        tenant_id=result.tenant_id,
        scanned_at=result.scanned_at,
        total_entries_scanned=result.total_entries_scanned,
        entries_with_embeddings=result.entries_with_embeddings,
        entries_without_embeddings=result.entries_without_embeddings,
        conflicts=[
            ConflictPairResponse(
                entry_a_id=c.entry_a_id,
                entry_a_title=c.entry_a_title,
                entry_b_id=c.entry_b_id,
                entry_b_title=c.entry_b_title,
                conflict_type=c.conflict_type.value,
                severity=c.severity.value,
                embedding_similarity=round(c.embedding_similarity, 3),
                content_overlap=round(c.content_overlap, 3),
                title_similarity=round(c.title_similarity, 3),
                conflicting_facts=c.conflicting_facts,
                resolution=c.resolution,
            )
            for c in result.conflicts
        ],
        high_count=result.high_count,
        medium_count=result.medium_count,
        low_count=result.low_count,
        scan_duration_ms=result.scan_duration_ms,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/scan/result — Get cached scan result
# ---------------------------------------------------------------------------


@router.get(
    "/scan/result",
    response_model=ScanResultResponse,
    summary="Get last scan result",
    description="Returns the most recent conflict scan result if still cached (5-minute TTL). Returns 404 if no recent scan exists.",
    responses={
        404: {"description": "No recent scan result available"},
        503: {"description": "Conflict scanner not initialized"},
    },
)
async def get_scan_result(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ScanResultResponse:
    """Get the cached result of the most recent conflict scan."""
    if _conflict_scanner is None:
        raise HTTPException(
            status_code=503,
            detail="Conflict scanner not initialised",
        )

    result = _conflict_scanner.get_cached_result(ctx.tenant_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No recent scan result. Run POST /api/admin/knowledge/scan first.",
        )

    return ScanResultResponse(
        tenant_id=result.tenant_id,
        scanned_at=result.scanned_at,
        total_entries_scanned=result.total_entries_scanned,
        entries_with_embeddings=result.entries_with_embeddings,
        entries_without_embeddings=result.entries_without_embeddings,
        conflicts=[
            ConflictPairResponse(
                entry_a_id=c.entry_a_id,
                entry_a_title=c.entry_a_title,
                entry_b_id=c.entry_b_id,
                entry_b_title=c.entry_b_title,
                conflict_type=c.conflict_type.value,
                severity=c.severity.value,
                embedding_similarity=round(c.embedding_similarity, 3),
                content_overlap=round(c.content_overlap, 3),
                title_similarity=round(c.title_similarity, 3),
                conflicting_facts=c.conflicting_facts,
                resolution=c.resolution,
            )
            for c in result.conflicts
        ],
        high_count=result.high_count,
        medium_count=result.medium_count,
        low_count=result.low_count,
        scan_duration_ms=result.scan_duration_ms,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/scan/config — Config-vs-KB conflict check (SPEC-1714)
# ---------------------------------------------------------------------------


@router.post(
    "/scan/config",
    response_model=ConfigConflictResponse,
    summary="Check config fields against KB articles",
    description=(
        "Cross-checks tenant configuration field values (return_policy, shipping_info, "
        "brand_voice) against knowledge base articles for factual conflicts. "
        "Lightweight scan intended to run on config save."
    ),
    responses={
        503: {"description": "Conflict scanner not initialized"},
    },
)
async def scan_config_conflicts(
    body: ConfigConflictRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigConflictResponse:
    """Scan for conflicts between config fields and KB articles (SPEC-1714)."""
    if _conflict_scanner is None:
        raise HTTPException(
            status_code=503,
            detail="Conflict scanner not initialised",
        )

    config_fields: dict[str, str] = {}
    if body.return_policy:
        config_fields["return_policy"] = body.return_policy
    if body.shipping_info:
        config_fields["shipping_info"] = body.shipping_info
    if body.brand_voice:
        config_fields["brand_voice"] = body.brand_voice

    result = await _conflict_scanner.scan_config_conflicts(
        tenant_id=ctx.tenant_id,
        config_fields=config_fields,
    )

    return ConfigConflictResponse(
        tenant_id=result.tenant_id,
        scanned_at=result.scanned_at,
        config_fields_checked=result.config_fields_checked,
        articles_checked=result.articles_checked,
        conflicts=[
            ConfigConflictItem(
                config_field=c.config_field,
                config_value=c.config_value,
                article_id=c.article_id,
                article_title=c.article_title,
                conflicting_facts=c.conflicting_facts,
                resolution=c.resolution,
            )
            for c in result.conflicts
        ],
        scan_duration_ms=result.scan_duration_ms,
    )


# ---------------------------------------------------------------------------
# Website Source management — automated crawling (S89)
# ---------------------------------------------------------------------------


class WebsiteSourceResponse(CamelCaseModel):
    """A single website source configuration."""

    id: str
    tenant_id: str
    domain: str
    start_url: str
    max_pages: int = 25
    entry_type: str = "article"
    auto_refresh: bool = True
    refresh_interval_hours: int = 24
    status: str = "pending"
    last_crawled_at: str | None = None
    next_crawl_at: str | None = None
    pages_discovered: int = 0
    pages_crawled: int = 0
    articles_created: int = 0
    total_chars: int = 0
    error_message: str | None = None
    created_at: str
    updated_at: str


class WebsiteSourceListResponse(CamelCaseModel):
    """List of website sources for a tenant."""

    tenant_id: str
    sources: list[WebsiteSourceResponse]
    total_count: int


class CreateWebsiteSourceRequest(CamelCaseModel):
    """Request body for POST /api/admin/knowledge/sources."""

    start_url: str = Field(
        min_length=1,
        max_length=2000,
        description="Starting URL for the website crawl",
    )
    max_pages: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum pages to crawl per cycle",
    )
    entry_type: str = Field(
        default="article",
        description="KB entry type for crawled pages",
    )
    auto_refresh: bool = Field(
        default=True,
        description="Enable automatic re-crawling",
    )
    refresh_interval_hours: int = Field(
        default=24,
        ge=6,
        le=168,
        description="Hours between automatic re-crawls (6-168)",
    )


class UpdateWebsiteSourceRequest(CamelCaseModel):
    """Request body for PUT /api/admin/knowledge/sources/{id}."""

    max_pages: int | None = Field(default=None, ge=1, le=100)
    auto_refresh: bool | None = None
    refresh_interval_hours: int | None = Field(default=None, ge=6, le=168)
    status: str | None = Field(
        default=None,
        description="Set to 'paused' to pause or 'active' to resume",
    )


class WebsiteSourceActionResponse(CamelCaseModel):
    """Response for source action endpoints (crawl, delete)."""

    success: bool
    message: str
    source_id: str | None = None


def _source_to_response(doc: dict[str, Any]) -> WebsiteSourceResponse:
    """Convert a raw Cosmos document to a WebsiteSourceResponse."""
    return WebsiteSourceResponse(
        id=doc["id"],
        tenant_id=doc["tenant_id"],
        domain=doc.get("domain", ""),
        start_url=doc.get("start_url", ""),
        max_pages=doc.get("max_pages", 25),
        entry_type=doc.get("entry_type", "article"),
        auto_refresh=doc.get("auto_refresh", True),
        refresh_interval_hours=doc.get("refresh_interval_hours", 24),
        status=doc.get("status", "pending"),
        last_crawled_at=doc.get("last_crawled_at"),
        next_crawl_at=doc.get("next_crawl_at"),
        pages_discovered=doc.get("pages_discovered", 0),
        pages_crawled=doc.get("pages_crawled", 0),
        articles_created=doc.get("articles_created", 0),
        total_chars=doc.get("total_chars", 0),
        error_message=doc.get("error_message"),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
    )


@router.get("/sources", response_model=WebsiteSourceListResponse)
async def list_website_sources(
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceListResponse:
    """List all website sources for the authenticated tenant."""
    repo = KnowledgeBaseRepository()
    sources = await repo.list_website_sources(ctx.tenant_id)
    return WebsiteSourceListResponse(
        tenant_id=ctx.tenant_id,
        sources=[_source_to_response(s) for s in sources],
        total_count=len(sources),
    )


@router.post("/sources", response_model=WebsiteSourceResponse, status_code=201)
async def create_website_source(
    body: CreateWebsiteSourceRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceResponse:
    """Add a new website source and trigger the first crawl."""
    from urllib.parse import urlparse

    from src.multi_tenant.cosmos_schema import WebsiteSourceDocument
    from src.multi_tenant.website_crawl_service import get_tier_limits

    # --- Validate URL ---
    try:
        parsed = urlparse(body.start_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Invalid URL scheme or missing host")
        domain = parsed.netloc.lower().removeprefix("www.")
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid URL. Must be a valid http(s) URL.")

    repo = KnowledgeBaseRepository()

    # --- Tier limit enforcement ---
    tier = ctx.tier or "starter"
    limits = get_tier_limits(tier)
    current_count = await repo.count_website_sources(ctx.tenant_id)
    if current_count >= limits["max_sources"]:
        raise HTTPException(
            status_code=409,
            detail=f"Website source limit reached ({limits['max_sources']} for {tier} tier). "
                   f"Upgrade your plan or remove an existing source.",
        )

    # --- Enforce tier page limit ---
    effective_max_pages = min(body.max_pages, limits["max_pages"])

    # --- Enforce tier refresh interval ---
    effective_interval = max(body.refresh_interval_hours, limits["min_refresh_hours"])

    # --- Duplicate domain check ---
    existing = await repo.get_source_by_domain(ctx.tenant_id, domain)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A website source for domain '{domain}' already exists.",
        )

    # --- Create the source document ---
    now = datetime.now(timezone.utc).isoformat()
    doc = WebsiteSourceDocument(
        id=str(uuid.uuid4()),
        tenant_id=ctx.tenant_id,
        domain=domain,
        start_url=body.start_url,
        max_pages=effective_max_pages,
        entry_type=body.entry_type,
        auto_refresh=body.auto_refresh,
        refresh_interval_hours=effective_interval,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    await repo.create(ctx.tenant_id, doc)
    logger.info(
        "Website source created: tenant=%s domain=%s max_pages=%d",
        ctx.tenant_id[:8], domain, effective_max_pages,
    )

    # --- Trigger first crawl via ingestion job ---
    try:
        from src.multi_tenant.cosmos_schema import IngestionJobDocument, IngestionJobType
        job = IngestionJobDocument(
            id=str(uuid.uuid4()),
            tenant_id=ctx.tenant_id,
            job_type=IngestionJobType.WEBSITE_REFRESH.value,
            status="pending",
            source_config={"source_id": doc.id},
            created_at=now,
            updated_at=now,
        )
        await repo.create(ctx.tenant_id, job)
    except Exception:
        logger.warning(
            "Failed to create initial crawl job for source %s (non-fatal)",
            doc.id[:8],
            exc_info=True,
        )

    return _source_to_response(doc.model_dump())


@router.get("/sources/{source_id}", response_model=WebsiteSourceResponse)
async def get_website_source(
    source_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceResponse:
    """Get details for a single website source."""
    repo = KnowledgeBaseRepository()
    try:
        doc = await repo.read(ctx.tenant_id, source_id)
    except (DocumentNotFoundError, Exception):
        raise HTTPException(status_code=404, detail="Website source not found.")

    if doc.get("doc_type") != "website_source":
        raise HTTPException(status_code=404, detail="Website source not found.")

    return _source_to_response(doc)


@router.put("/sources/{source_id}", response_model=WebsiteSourceResponse)
async def update_website_source(
    source_id: str,
    body: UpdateWebsiteSourceRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceResponse:
    """Update a website source configuration."""
    from src.multi_tenant.website_crawl_service import get_tier_limits

    repo = KnowledgeBaseRepository()

    # Verify source exists and is a website source
    try:
        existing = await repo.read(ctx.tenant_id, source_id)
    except (DocumentNotFoundError, Exception):
        raise HTTPException(status_code=404, detail="Website source not found.")

    if existing.get("doc_type") != "website_source":
        raise HTTPException(status_code=404, detail="Website source not found.")

    # Build update fields
    fields: dict[str, Any] = {}
    tier = ctx.tier or "starter"
    limits = get_tier_limits(tier)

    if body.max_pages is not None:
        fields["max_pages"] = min(body.max_pages, limits["max_pages"])
    if body.auto_refresh is not None:
        fields["auto_refresh"] = body.auto_refresh
    if body.refresh_interval_hours is not None:
        fields["refresh_interval_hours"] = max(body.refresh_interval_hours, limits["min_refresh_hours"])
    if body.status is not None:
        if body.status not in ("paused", "active"):
            raise HTTPException(status_code=422, detail="Status must be 'paused' or 'active'.")
        fields["status"] = body.status

    if not fields:
        return _source_to_response(existing)

    updated = await repo.update_website_source(ctx.tenant_id, source_id, **fields)
    return _source_to_response(updated)


@router.delete("/sources/{source_id}", response_model=WebsiteSourceActionResponse)
async def delete_website_source(
    source_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceActionResponse:
    """Soft-delete a website source and its KB entries."""
    repo = KnowledgeBaseRepository()

    try:
        doc = await repo.read(ctx.tenant_id, source_id)
    except (DocumentNotFoundError, Exception):
        raise HTTPException(status_code=404, detail="Website source not found.")

    if doc.get("doc_type") != "website_source":
        raise HTTPException(status_code=404, detail="Website source not found.")

    domain = doc.get("domain", "")

    # Soft-delete the source itself
    await repo.soft_delete_website_source(ctx.tenant_id, source_id)

    # Cascade soft-delete KB entries from this source
    deleted_count = 0
    if domain:
        deleted_count = await repo.soft_delete_kb_entries_by_source(ctx.tenant_id, domain)

    logger.info(
        "Website source deleted: tenant=%s source=%s domain=%s kb_entries_deleted=%d",
        ctx.tenant_id[:8], source_id[:8], domain, deleted_count,
    )

    return WebsiteSourceActionResponse(
        success=True,
        message=f"Website source deleted. {deleted_count} KB entries removed.",
        source_id=source_id,
    )


@router.post("/sources/{source_id}/crawl", response_model=WebsiteSourceActionResponse)
async def trigger_crawl(
    source_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> WebsiteSourceActionResponse:
    """Manually trigger a re-crawl for a website source."""
    from src.multi_tenant.cosmos_schema import IngestionJobDocument, IngestionJobType

    repo = KnowledgeBaseRepository()

    try:
        doc = await repo.read(ctx.tenant_id, source_id)
    except (DocumentNotFoundError, Exception):
        raise HTTPException(status_code=404, detail="Website source not found.")

    if doc.get("doc_type") != "website_source":
        raise HTTPException(status_code=404, detail="Website source not found.")

    if doc.get("status") == "crawling":
        raise HTTPException(status_code=409, detail="A crawl is already in progress.")

    # Create ingestion job for the crawl
    now = datetime.now(timezone.utc).isoformat()
    job = IngestionJobDocument(
        id=str(uuid.uuid4()),
        tenant_id=ctx.tenant_id,
        job_type=IngestionJobType.WEBSITE_REFRESH.value,
        status="pending",
        source_config={"source_id": source_id},
        created_at=now,
        updated_at=now,
    )
    await repo.create(ctx.tenant_id, job)

    logger.info(
        "Manual crawl triggered: tenant=%s source=%s domain=%s",
        ctx.tenant_id[:8], source_id[:8], doc.get("domain", ""),
    )

    return WebsiteSourceActionResponse(
        success=True,
        message="Crawl job created. The source will be re-crawled shortly.",
        source_id=source_id,
    )
