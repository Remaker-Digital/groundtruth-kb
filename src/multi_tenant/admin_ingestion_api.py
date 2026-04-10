# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Admin Ingestion API — Knowledge Automation (KA-2).

REST endpoints for triggering and monitoring storefront ingestion jobs
and applying industry category templates to merchant knowledge bases.

Endpoints:
    POST   /api/admin/knowledge/ingest              — Start ingestion job
    GET    /api/admin/knowledge/ingest/status        — Get latest job status
    POST   /api/admin/knowledge/ingest/cancel        — Cancel running job
    GET    /api/admin/knowledge/templates            — List available templates
    POST   /api/admin/knowledge/templates/{id}/apply — Apply template to KB

All endpoints derive tenant_id from the authenticated TenantContext.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/knowledge", tags=["knowledge-automation"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class StartIngestionRequest(CamelCaseModel):
    """Request body for POST /api/admin/knowledge/ingest."""

    source_type: str = Field(
        description="Ingestion source: 'shopify' | 'url' | 'category_template'",
    )
    url: str | None = Field(
        default=None,
        description="Target URL for URL-based ingestion",
    )
    max_pages: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum pages to crawl (URL ingestion only)",
    )
    category_id: str | None = Field(
        default=None,
        description="Category template ID (for category_template source_type)",
    )


class IngestionJobResponse(CamelCaseModel):
    """Response model for ingestion job status."""

    id: str
    tenant_id: str
    job_type: str
    status: str
    progress_percent: int = 0
    articles_created: int = 0
    articles_failed: int = 0
    total_chars: int = 0
    pages_crawled: int = 0
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None


class CategoryTemplateResponse(CamelCaseModel):
    """Response model for a single category template."""

    id: str
    name: str
    description: str
    article_count: int
    suggested_brand_voice: str
    suggested_escalation_keywords: list[str]


class TemplateApplyResponse(CamelCaseModel):
    """Response model after applying a category template."""

    articles_created: int
    articles_failed: int
    total_chars: int
    config_suggestions: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/ingest — Start ingestion job
# ---------------------------------------------------------------------------


@router.post("/ingest", response_model=IngestionJobResponse, status_code=201)
async def start_ingestion(
    body: StartIngestionRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> IngestionJobResponse:
    """Start a storefront ingestion job.

    Supports three source types:
    - shopify: Import products/collections/policies via Shopify Admin API
    - url: Crawl a public URL and extract content
    - category_template: Apply a pre-built industry template
    """
    valid_types = {"shopify", "url", "category_template"}
    if body.source_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source_type '{body.source_type}'. "
            f"Must be one of: {', '.join(sorted(valid_types))}",
        )

    if body.source_type == "url" and not body.url:
        raise HTTPException(status_code=400, detail="URL is required for 'url' source_type")

    if body.source_type == "category_template" and not body.category_id:
        raise HTTPException(
            status_code=400,
            detail="category_id is required for 'category_template' source_type",
        )

    # Build source config
    source_config: dict[str, Any] = {}
    if body.source_type == "url":
        source_config["start_url"] = body.url
        source_config["max_pages"] = body.max_pages
    elif body.source_type == "category_template":
        source_config["category_id"] = body.category_id
    elif body.source_type == "shopify":
        # Populate Shopify source_config from tenant document + credentials.
        # Try Key Vault first (multi-tenant ready), fall back to env vars
        # (single-store deployment).
        from src.multi_tenant.repositories.tenant import TenantRepository

        tenant_repo = TenantRepository()
        tenant_doc = await tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
        shop_domain = (
            tenant_doc.get("shopify_shop_domain") if isinstance(tenant_doc, dict) else None
        )
        if not shop_domain:
            raise HTTPException(
                status_code=400,
                detail="No Shopify shop domain configured for this tenant",
            )
        source_config["shop_domain"] = shop_domain

        # Retrieve access token: Key Vault (preferred) → env var (fallback)
        access_token: str | None = None
        try:
            from src.multi_tenant.tenant_secret_service import (
                TenantSecretType,
                get_secret_service,
            )

            secret_service = get_secret_service()
            access_token = await secret_service.get_secret(
                ctx.tenant_id, TenantSecretType.SHOPIFY_TOKEN,
            )
        except Exception:
            pass  # Key Vault may not be configured in dev
        if not access_token:
            import os

            access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Shopify access token not available — check app installation",
            )
        source_config["access_token"] = access_token

    from src.multi_tenant.storefront_ingestion import get_ingestion_service

    service = get_ingestion_service()
    try:
        job = await service.start_ingestion(
            tenant_id=ctx.tenant_id,
            source_type=body.source_type,
            source_config=source_config,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(
        "Ingestion job started: %s for tenant %s (%s)",
        job["id"][:8], ctx.tenant_id[:8], body.source_type,
    )

    return IngestionJobResponse(**job)


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/ingest/status — Get latest job status
# ---------------------------------------------------------------------------


@router.get("/ingest/status", response_model=IngestionJobResponse | None)
async def get_ingestion_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> IngestionJobResponse | None:
    """Get the latest ingestion job status for the current tenant."""
    from src.multi_tenant.storefront_ingestion import get_ingestion_service

    try:
        service = get_ingestion_service()
        job = await service.get_latest_job(ctx.tenant_id)
    except Exception:
        # Collection may not exist yet or other transient error
        logger.debug("Failed to fetch ingestion status", exc_info=True)
        return None

    if job is None:
        return None

    return IngestionJobResponse(**job)


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/ingest/cancel — Cancel running job
# ---------------------------------------------------------------------------


class CancelIngestionResponse(CamelCaseModel):
    """Response for POST /ingest/cancel."""

    status: str
    job_id: str


@router.post("/ingest/cancel", response_model=CancelIngestionResponse)
async def cancel_ingestion(
    ctx: TenantContext = Depends(get_tenant_context),
) -> CancelIngestionResponse:
    """Cancel the currently running ingestion job for this tenant."""
    from src.multi_tenant.storefront_ingestion import get_ingestion_service

    service = get_ingestion_service()
    job = await service.get_latest_job(ctx.tenant_id)

    if job is None:
        raise HTTPException(status_code=404, detail="No ingestion job found")

    if job.get("status") not in ("pending", "running"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in '{job.get('status')}' state",
        )

    try:
        await service.cancel_job(ctx.tenant_id, job["id"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return CancelIngestionResponse(status="cancelled", job_id=job["id"])


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/templates — List available templates
# ---------------------------------------------------------------------------


@router.get("/templates", response_model=list[CategoryTemplateResponse])
async def list_templates() -> list[CategoryTemplateResponse]:
    """List all available industry category templates."""
    from src.multi_tenant.template_loader import get_template_loader

    loader = get_template_loader()
    categories = loader.list_categories()

    return [CategoryTemplateResponse(**cat) for cat in categories]


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/suggestions — Config suggestions from KB analysis
# ---------------------------------------------------------------------------


class ConfigSuggestionResponse(CamelCaseModel):
    """Response model for a single config suggestion."""

    field_name: str
    value: Any
    confidence: float
    source: str


@router.get("/suggestions", response_model=list[ConfigSuggestionResponse])
async def get_config_suggestions(
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[ConfigSuggestionResponse]:
    """Get configuration suggestions based on KB content analysis."""
    from src.multi_tenant.config_suggestion_engine import get_config_suggestion_engine

    engine = get_config_suggestion_engine()
    suggestion_set = await engine.generate_suggestions(ctx.tenant_id)

    return [
        ConfigSuggestionResponse(
            field_name=s.field_name,
            value=s.value,
            confidence=s.confidence,
            source=s.source,
        )
        for s in suggestion_set.suggestions
    ]


# ---------------------------------------------------------------------------
# POST /api/admin/knowledge/templates/{category_id}/apply — Apply template
# ---------------------------------------------------------------------------


@router.post(
    "/templates/{category_id}/apply",
    response_model=TemplateApplyResponse,
    status_code=201,
)
async def apply_template(
    category_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TemplateApplyResponse:
    """Apply a category template directly to the tenant's knowledge base.

    This creates KB articles immediately (synchronous) rather than via
    background job. Use this for quick template application.
    """
    from src.multi_tenant.template_loader import get_template_loader

    loader = get_template_loader()
    template = loader.get_template(category_id)

    if template is None:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {category_id}",
        )

    try:
        result = await loader.apply_template(ctx.tenant_id, category_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(
        "Template '%s' applied to tenant %s: %d articles",
        category_id, ctx.tenant_id[:8], result["articles_created"],
    )

    return TemplateApplyResponse(
        articles_created=result["articles_created"],
        articles_failed=result["articles_failed"],
        total_chars=result["total_chars"],
        config_suggestions=result.get("config_suggestions", {}),
    )
