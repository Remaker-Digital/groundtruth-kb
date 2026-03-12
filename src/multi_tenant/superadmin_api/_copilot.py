"""Superadmin API -- Co-Pilot knowledge management, document CRUD, ingestion, config.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


class CopilotDocumentResponse(CamelCaseModel):
    """Single document in the Co-Pilot knowledge base."""

    id: str
    document_category: str
    title: str
    content: str = ""
    section: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
    content_hash: str | None = None
    embedded_at: str | None = None
    source_file: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CopilotDocumentListResponse(CamelCaseModel):
    """List of Co-Pilot documents."""

    total: int = 0
    documents: list[CopilotDocumentResponse] = Field(default_factory=list)


class CopilotDocumentCreateRequest(BaseModel):
    """Request to create a Co-Pilot document."""

    document_category: str
    title: str
    content: str
    section: str | None = None
    tags: list[str] = Field(default_factory=list)


class CopilotDocumentUpdateRequest(BaseModel):
    """Request to update a Co-Pilot document."""

    title: str | None = None
    content: str | None = None
    section: str | None = None
    tags: list[str] | None = None
    is_active: bool | None = None


class CopilotIngestionResponse(CamelCaseModel):
    """Result of a batch ingestion operation."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[dict[str, str]] = Field(default_factory=list)


class CopilotStatsResponse(CamelCaseModel):
    """Collection statistics for Co-Pilot knowledge base."""

    total_documents: int = 0
    active_documents: int = 0
    by_category: dict[str, int] = Field(default_factory=dict)
    embedded_count: int = 0
    stale_count: int = 0
    total_content_length: int = 0


class CopilotTestQueryRequest(BaseModel):
    """Request for testing Co-Pilot retrieval."""

    query: str
    top_k: int = 5


class CopilotTestQueryResult(CamelCaseModel):
    """Single result from a test query."""

    id: str
    title: str
    category: str
    rrf_score: float = 0.0
    snippet: str = ""


class CopilotTestQueryResponse(CamelCaseModel):
    """Response from testing Co-Pilot retrieval."""

    query: str
    results: list[CopilotTestQueryResult] = Field(default_factory=list)
    total_documents: int = 0


class CopilotURLImportRequest(BaseModel):
    """Request to import a URL as a Co-Pilot document."""

    url: str
    document_category: str
    title: str | None = None
    tags: list[str] = Field(default_factory=list)


# ── SPEC-1570: Document CRUD endpoints ────────────────────────────────────


@router.get(
    "/copilot/documents",
    response_model=CopilotDocumentListResponse,
    summary="List Co-Pilot knowledge documents",
    status_code=200,
)
async def list_copilot_documents(
    category: str | None = Query(None, description="Filter by category"),

) -> CopilotDocumentListResponse:
    """List all documents in the Co-Pilot knowledge base."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    try:
        if category:
            docs = await _state._admin_doc_repo.list_by_category(category)
        else:
            docs = await _state._admin_doc_repo.list_all_active()

        return CopilotDocumentListResponse(
            total=len(docs),
            documents=[
                CopilotDocumentResponse(
                    id=d.get("id", ""),
                    document_category=d.get("document_category", ""),
                    title=d.get("title", ""),
                    content=d.get("content", ""),
                    section=d.get("section"),
                    tags=d.get("tags", []),
                    is_active=d.get("is_active", True),
                    content_hash=d.get("content_hash"),
                    embedded_at=d.get("embedded_at"),
                    source_file=d.get("source_file"),
                    created_at=d.get("created_at"),
                    updated_at=d.get("updated_at"),
                )
                for d in docs
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {exc}")


@router.post(
    "/copilot/documents",
    response_model=CopilotDocumentResponse,
    summary="Create a Co-Pilot knowledge document",
    status_code=201,
)
async def create_copilot_document(
    body: CopilotDocumentCreateRequest = Body(...),

) -> CopilotDocumentResponse:
    """Create a new document in the Co-Pilot knowledge base."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    import hashlib

    now = datetime.now(timezone.utc).isoformat()
    slug = body.title.lower().replace(" ", "-")[:50]
    doc_id = f"{body.document_category}:{slug}"
    content_hash = hashlib.sha256(
        f"{body.title}\n{body.content}".encode()
    ).hexdigest()

    from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

    doc = AdminDocumentationDocument(
        id=doc_id,
        document_category=body.document_category,
        title=body.title,
        content=body.content,
        section=body.section,
        tags=body.tags,
        content_hash=content_hash,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    try:
        await _state._admin_doc_repo.upsert_document(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {exc}")

    return CopilotDocumentResponse(
        id=doc_id,
        document_category=body.document_category,
        title=body.title,
        content=body.content,
        section=body.section,
        tags=body.tags,
        is_active=True,
        content_hash=content_hash,
        created_at=now,
        updated_at=now,
    )


@router.put(
    "/copilot/documents/{doc_id:path}",
    response_model=CopilotDocumentResponse,
    summary="Update a Co-Pilot knowledge document",
    status_code=200,
)
async def update_copilot_document(
    doc_id: str,
    body: CopilotDocumentUpdateRequest = Body(...),

) -> CopilotDocumentResponse:
    """Update an existing document in the Co-Pilot knowledge base."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    # Parse category from doc_id (format: "category:slug")
    parts = doc_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    category = parts[0]

    existing = await _state._admin_doc_repo.get_by_id(category, doc_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    import hashlib

    now = datetime.now(timezone.utc).isoformat()

    # Merge updates
    title = body.title if body.title is not None else existing.get("title", "")
    content = body.content if body.content is not None else existing.get("content", "")
    section = body.section if body.section is not None else existing.get("section")
    tags = body.tags if body.tags is not None else existing.get("tags", [])
    is_active = body.is_active if body.is_active is not None else existing.get("is_active", True)

    content_hash = hashlib.sha256(f"{title}\n{content}".encode()).hexdigest()

    from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

    doc = AdminDocumentationDocument(
        id=doc_id,
        document_category=category,
        title=title,
        content=content,
        section=section,
        tags=tags,
        content_hash=content_hash,
        is_active=is_active,
        embedding=existing.get("embedding"),
        embedding_model=existing.get("embedding_model"),
        embedded_at=existing.get("embedded_at"),
        source_file=existing.get("source_file"),
        created_at=existing.get("created_at", now),
        updated_at=now,
    )

    try:
        await _state._admin_doc_repo.upsert_document(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {exc}")

    return CopilotDocumentResponse(
        id=doc_id,
        document_category=category,
        title=title,
        content=content,
        section=section,
        tags=tags,
        is_active=is_active,
        content_hash=content_hash,
        embedded_at=existing.get("embedded_at"),
        source_file=existing.get("source_file"),
        created_at=existing.get("created_at"),
        updated_at=now,
    )


@router.delete(
    "/copilot/documents/{doc_id:path}",
    summary="Soft-delete a Co-Pilot knowledge document",
    status_code=200,
)
async def delete_copilot_document(
    doc_id: str,

) -> dict[str, Any]:
    """Soft-delete a document by setting is_active=false."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    parts = doc_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    category = parts[0]

    existing = await _state._admin_doc_repo.get_by_id(category, doc_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

    now = datetime.now(timezone.utc).isoformat()
    doc = AdminDocumentationDocument(
        **{**existing, "is_active": False, "updated_at": now}
    )

    try:
        await _state._admin_doc_repo.upsert_document(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {exc}")

    return {"id": doc_id, "is_active": False, "deleted_at": now}


# ── SPEC-1571: Batch ingestion from docs-site ─────────────────────────────


@router.post(
    "/copilot/ingest/docs-site",
    response_model=CopilotIngestionResponse,
    summary="Ingest admin documentation from docs-site",
    status_code=200,
)
async def ingest_docs_site(

) -> CopilotIngestionResponse:
    """Scan docs/admin-guide/*.md and create/update documents."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    import hashlib
    from pathlib import Path

    docs_dir = Path("docs/admin-guide")
    if not docs_dir.exists():
        # Also try relative to src
        docs_dir = Path("docs-site/docs/admin-guide")
    if not docs_dir.exists():
        raise HTTPException(status_code=404, detail="Admin guide directory not found")

    now = datetime.now(timezone.utc).isoformat()
    created = 0
    updated = 0
    skipped = 0
    errors: list[dict[str, str]] = []

    for md_file in sorted(docs_dir.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
            # Extract title from first heading
            title = md_file.stem.replace("-", " ").title()
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            # Determine category from filename
            category = _infer_category_from_filename(md_file.stem)
            doc_id = f"{category}:{md_file.stem}"

            content_hash = hashlib.sha256(
                f"{title}\n{content}".encode()
            ).hexdigest()

            # Check if document exists and hash matches
            existing = await _state._admin_doc_repo.get_by_id(category, doc_id)
            if existing and existing.get("content_hash") == content_hash:
                skipped += 1
                continue

            from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

            doc = AdminDocumentationDocument(
                id=doc_id,
                document_category=category,
                title=title,
                content=content,
                source_file=str(md_file),
                content_hash=content_hash,
                is_active=True,
                created_at=existing.get("created_at", now) if existing else now,
                updated_at=now,
            )

            await _state._admin_doc_repo.upsert_document(doc)

            if existing:
                updated += 1
            else:
                created += 1

        except Exception as exc:
            errors.append({
                "file": str(md_file),
                "message": f"Ingestion failed: {exc}",
            })

    return CopilotIngestionResponse(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
    )


def _infer_category_from_filename(stem: str) -> str:
    """Map a docs-site filename to a document category."""
    category_map = {
        "dashboard": "dashboard",
        "knowledge": "knowledge_base",
        "widget": "widget_configuration",
        "team": "team_management",
        "conversation": "conversations",
        "inbox": "conversations",
        "analytics": "analytics",
        "instruction": "custom_instructions",
        "brand": "brand_tone",
        "tone": "brand_tone",
        "policy": "business_policies",
        "escalation": "escalation_rules",
        "integration": "integrations",
        "shopify": "integrations",
        "save": "save_activate",
        "activate": "save_activate",
        "getting-started": "getting_started",
        "quickstart": "getting_started",
        "billing": "billing",
        "pricing": "billing",
    }
    stem_lower = stem.lower()
    for key, cat in category_map.items():
        if key in stem_lower:
            return cat
    return "getting_started"  # Default category


# ── SPEC-1572: URL import ─────────────────────────────────────────────────


@router.post(
    "/copilot/ingest/url",
    response_model=CopilotDocumentResponse,
    summary="Import a URL as a Co-Pilot document",
    status_code=201,
)
async def import_url(
    body: CopilotURLImportRequest = Body(...),

) -> CopilotDocumentResponse:
    """Fetch a URL and create a Co-Pilot document from its content."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    if not body.url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Only HTTPS URLs are accepted")

    import hashlib
    import httpx

    now = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(body.url)
            resp.raise_for_status()
            content = resp.text
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch URL: {exc}"
        )

    title = body.title or body.url.split("/")[-1].replace("-", " ").title()
    slug = title.lower().replace(" ", "-")[:50]
    doc_id = f"{body.document_category}:{slug}"
    content_hash = hashlib.sha256(f"{title}\n{content}".encode()).hexdigest()

    from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

    doc = AdminDocumentationDocument(
        id=doc_id,
        document_category=body.document_category,
        title=title,
        content=content,
        tags=body.tags,
        source_file=body.url,
        content_hash=content_hash,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    try:
        await _state._admin_doc_repo.upsert_document(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to store document: {exc}")

    return CopilotDocumentResponse(
        id=doc_id,
        document_category=body.document_category,
        title=title,
        content=content,
        tags=body.tags,
        is_active=True,
        content_hash=content_hash,
        source_file=body.url,
        created_at=now,
        updated_at=now,
    )


# ── SPEC-1573: Re-embedding trigger ──────────────────────────────────────


@router.post(
    "/copilot/re-embed",
    response_model=CopilotIngestionResponse,
    summary="Re-embed all active Co-Pilot documents",
    status_code=200,
)
async def re_embed_documents(

) -> CopilotIngestionResponse:
    """Re-embed all active documents using the current embedding model."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    errors: list[dict[str, str]] = []

    try:
        docs = await _state._admin_doc_repo.list_all_active()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {exc}")

    for d in docs:
        try:
            # Generate embedding
            embedding = await _generate_embedding(
                f"{d.get('title', '')}\n{d.get('content', '')}"
            )
            if embedding is None:
                errors.append({
                    "id": d.get("id", "unknown"),
                    "message": "Embedding generation failed",
                })
                continue

            from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

            doc = AdminDocumentationDocument(
                **{
                    **d,
                    "embedding": embedding,
                    "embedding_model": "text-embedding-3-large",
                    "embedded_at": now,
                    "updated_at": now,
                }
            )
            await _state._admin_doc_repo.upsert_document(doc)
            updated += 1
        except Exception as exc:
            errors.append({
                "id": d.get("id", "unknown"),
                "message": f"Re-embed failed: {exc}",
            })

    return CopilotIngestionResponse(
        created=0,
        updated=updated,
        skipped=0,
        errors=errors,
    )


async def _generate_embedding(text: str) -> list[float] | None:
    """Generate embedding for text using Azure OpenAI."""
    try:
        from openai import AsyncAzureOpenAI

        client = AsyncAzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        )
        response = await client.embeddings.create(
            model="text-embedding-3-large",
            input=text[:8000],  # Truncate to fit token limits
            dimensions=3072,
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.warning("Embedding generation failed: %s", exc)
        return None


# ── SPEC-1574: Collection statistics ──────────────────────────────────────


@router.get(
    "/copilot/stats",
    response_model=CopilotStatsResponse,
    summary="Co-Pilot knowledge collection statistics",
    status_code=200,
)
async def copilot_stats(

) -> CopilotStatsResponse:
    """Get statistics about the Co-Pilot knowledge collection."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    try:
        docs = await _state._admin_doc_repo.list_all_active()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read stats: {exc}")

    total = len(docs)
    by_category: dict[str, int] = {}
    embedded = 0
    stale = 0
    total_chars = 0

    import hashlib

    for d in docs:
        cat = d.get("document_category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1

        content = d.get("content", "")
        total_chars += len(content)

        if d.get("embedding"):
            embedded += 1

        # Check staleness: content_hash differs from hash of current content
        current_hash = hashlib.sha256(
            f"{d.get('title', '')}\n{content}".encode()
        ).hexdigest()
        stored_hash = d.get("content_hash")
        if d.get("embedding") and stored_hash and stored_hash != current_hash:
            stale += 1

    return CopilotStatsResponse(
        total_documents=total,
        active_documents=total,
        by_category=by_category,
        embedded_count=embedded,
        stale_count=stale,
        total_content_length=total_chars,
    )


# ── SPEC-1577: Test query endpoint ────────────────────────────────────────


@router.post(
    "/copilot/test-query",
    response_model=CopilotTestQueryResponse,
    summary="Test Co-Pilot knowledge retrieval",
    status_code=200,
)
async def test_copilot_query(
    body: CopilotTestQueryRequest = Body(...),

) -> CopilotTestQueryResponse:
    """Execute a test query against the Co-Pilot knowledge base."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    results: list[CopilotTestQueryResult] = []

    try:
        # Try vector search first
        embedding = await _generate_embedding(body.query)
        if embedding:
            vector_results = await _state._admin_doc_repo.vector_search_all_categories(
                embedding=embedding,
                top_k=body.top_k,
            )
            for vr in vector_results:
                content = vr.get("content", "")
                results.append(CopilotTestQueryResult(
                    id=vr.get("id", ""),
                    title=vr.get("title", ""),
                    category=vr.get("document_category", ""),
                    rrf_score=vr.get("similarity", 0.0),
                    snippet=content[:200] + ("..." if len(content) > 200 else ""),
                ))
    except Exception as exc:
        logger.warning("Test query vector search failed: %s", exc)

    total = await _state._admin_doc_repo.count_all()

    return CopilotTestQueryResponse(
        query=body.query,
        results=results,
        total_documents=total,
    )


# ---------------------------------------------------------------------------
# Co-Pilot Configuration: scan schedule + retrieval params (SPEC-1575/1576)
# ---------------------------------------------------------------------------


class CopilotScheduleRequest(CamelCaseModel):
    """Request to update scan schedule."""

    scan_frequency: str = "manual"
    scan_scope: str = "docs-site"


class CopilotScheduleResponse(CamelCaseModel):
    """Current scan schedule and history."""

    scan_frequency: str = "manual"
    scan_scope: str = "docs-site"
    last_scan_at: str | None = None
    next_scan_at: str | None = None
    scan_history: list[dict[str, Any]] = Field(default_factory=list)


class CopilotRetrievalConfigRequest(CamelCaseModel):
    """Request to update retrieval parameters."""

    vector_weight: float = 0.7
    bm25_weight: float = 0.3
    rrf_k: int = 60
    top_k: int = 5
    min_score: float = 0.1


class CopilotRetrievalConfigResponse(CamelCaseModel):
    """Current retrieval parameters."""

    vector_weight: float = 0.7
    bm25_weight: float = 0.3
    rrf_k: int = 60
    top_k: int = 5
    min_score: float = 0.1
    updated_at: str | None = None
    updated_by: str | None = None


async def _get_copilot_config() -> dict[str, Any]:
    """Load the singleton CopilotConfigDocument from Cosmos."""
    if _state._admin_doc_repo is None:
        return {}
    try:
        doc = await _state._admin_doc_repo.get_by_id("platform", "copilot_config")
        return doc or {}
    except Exception:
        return {}


async def _save_copilot_config(config: dict[str, Any]) -> None:
    """Save the singleton CopilotConfigDocument to Cosmos."""
    if _state._admin_doc_repo is None:
        return
    from src.multi_tenant.cosmos_schema import CopilotConfigDocument

    now = datetime.now(timezone.utc).isoformat()
    merged = {
        "id": "copilot_config",
        "document_category": "platform",
        "updated_at": now,
        **config,
    }
    doc = CopilotConfigDocument(**merged)
    await _state._admin_doc_repo.upsert_document(doc)

    # Push retrieval params to the CoPilotAgent runtime config
    try:
        from src.agents.co_pilot import configure_copilot_retrieval

        configure_copilot_retrieval({
            "vector_weight": doc.vector_weight,
            "bm25_weight": doc.bm25_weight,
            "rrf_k": doc.rrf_k,
            "top_k": doc.top_k,
            "min_score": doc.min_score,
        })
    except Exception as exc:
        logger.warning("Failed to push retrieval config: %s", exc)


@router.get(
    "/copilot/config/schedule",
    response_model=CopilotScheduleResponse,
    summary="Get Co-Pilot scan schedule",
    status_code=200,
)
async def get_copilot_schedule(

) -> CopilotScheduleResponse:
    """Return the current scan schedule configuration."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    config = await _get_copilot_config()
    return CopilotScheduleResponse(
        scan_frequency=config.get("scan_frequency", "manual"),
        scan_scope=config.get("scan_scope", "docs-site"),
        last_scan_at=config.get("last_scan_at"),
        next_scan_at=config.get("next_scan_at"),
        scan_history=config.get("scan_history", []),
    )


@router.put(
    "/copilot/config/schedule",
    response_model=CopilotScheduleResponse,
    summary="Update Co-Pilot scan schedule",
    status_code=200,
)
async def update_copilot_schedule(
    body: CopilotScheduleRequest = Body(...),

) -> CopilotScheduleResponse:
    """Update scan frequency and scope."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    if body.scan_frequency not in ("manual", "daily", "weekly"):
        raise HTTPException(status_code=400, detail="Invalid scan_frequency")
    if body.scan_scope not in ("docs-site", "urls", "both"):
        raise HTTPException(status_code=400, detail="Invalid scan_scope")

    config = await _get_copilot_config()
    config["scan_frequency"] = body.scan_frequency
    config["scan_scope"] = body.scan_scope

    # Compute next_scan_at based on frequency
    now = datetime.now(timezone.utc)
    if body.scan_frequency == "daily":
        next_scan = now + timedelta(days=1)
        config["next_scan_at"] = next_scan.isoformat()
    elif body.scan_frequency == "weekly":
        next_scan = now + timedelta(weeks=1)
        config["next_scan_at"] = next_scan.isoformat()
    else:
        config["next_scan_at"] = None

    config["updated_by"] = "spa-console"
    await _save_copilot_config(config)

    return CopilotScheduleResponse(
        scan_frequency=config["scan_frequency"],
        scan_scope=config["scan_scope"],
        last_scan_at=config.get("last_scan_at"),
        next_scan_at=config.get("next_scan_at"),
        scan_history=config.get("scan_history", []),
    )


@router.get(
    "/copilot/config/retrieval",
    response_model=CopilotRetrievalConfigResponse,
    summary="Get Co-Pilot retrieval parameters",
    status_code=200,
)
async def get_copilot_retrieval_config(

) -> CopilotRetrievalConfigResponse:
    """Return the current retrieval tuning parameters."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    config = await _get_copilot_config()
    return CopilotRetrievalConfigResponse(
        vector_weight=config.get("vector_weight", 0.7),
        bm25_weight=config.get("bm25_weight", 0.3),
        rrf_k=config.get("rrf_k", 60),
        top_k=config.get("top_k", 5),
        min_score=config.get("min_score", 0.1),
        updated_at=config.get("updated_at"),
        updated_by=config.get("updated_by"),
    )


@router.put(
    "/copilot/config/retrieval",
    response_model=CopilotRetrievalConfigResponse,
    summary="Update Co-Pilot retrieval parameters",
    status_code=200,
)
async def update_copilot_retrieval_config(
    body: CopilotRetrievalConfigRequest = Body(...),

) -> CopilotRetrievalConfigResponse:
    """Update retrieval tuning parameters (SPEC-1576)."""
    if _state._admin_doc_repo is None:
        raise HTTPException(status_code=503, detail="Co-Pilot knowledge not configured")

    # Validate ranges
    if not (0.0 <= body.vector_weight <= 1.0):
        raise HTTPException(status_code=400, detail="vector_weight must be 0.0-1.0")
    if not (0.0 <= body.bm25_weight <= 1.0):
        raise HTTPException(status_code=400, detail="bm25_weight must be 0.0-1.0")
    if not (1 <= body.rrf_k <= 100):
        raise HTTPException(status_code=400, detail="rrf_k must be 1-100")
    if not (1 <= body.top_k <= 20):
        raise HTTPException(status_code=400, detail="top_k must be 1-20")
    if not (0.0 <= body.min_score <= 1.0):
        raise HTTPException(status_code=400, detail="min_score must be 0.0-1.0")

    config = await _get_copilot_config()
    config["vector_weight"] = body.vector_weight
    config["bm25_weight"] = body.bm25_weight
    config["rrf_k"] = body.rrf_k
    config["top_k"] = body.top_k
    config["min_score"] = body.min_score
    config["updated_by"] = "spa-console"

    await _save_copilot_config(config)

    now = datetime.now(timezone.utc).isoformat()
    return CopilotRetrievalConfigResponse(
        vector_weight=body.vector_weight,
        bm25_weight=body.bm25_weight,
        rrf_k=body.rrf_k,
        top_k=body.top_k,
        min_score=body.min_score,
        updated_at=now,
        updated_by="spa-console",
    )
