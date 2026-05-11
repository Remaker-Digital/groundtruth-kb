# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cost and unit economics analytics for the service provider.

Provides per-tenant cost attribution based on conversation volume,
AI token consumption, and storage usage. Costs are modeled from
actual Azure consumption patterns (serverless Cosmos DB, Container
Apps, Azure OpenAI).

Phase 3 (HV-2): Usage-based cost model.

Endpoints:
    GET /api/superadmin/costs          — Cross-tenant cost overview
    GET /api/superadmin/costs/{tenant}  — Per-tenant cost breakdown

Cost model:
    - AI tokens: $0.003 per 1K input tokens + $0.015 per 1K output tokens
      (Azure OpenAI GPT-4o pricing, serverless)
    - Cosmos DB: $0.25 per 100K RU (serverless, per-request billing)
    - Container Apps: amortized across tenants by conversation share
    - Storage: $0.01 per article per month (Cosmos DB item storage)

All costs are estimates based on usage metrics. Actual Azure billing
may differ due to reserved capacity, tier discounts, or rounding.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.middleware import require_platform_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/superadmin/costs",
    tags=["Cost Analytics"],
    dependencies=[Depends(require_platform_admin())],
)


# ---------------------------------------------------------------------------
# Cost model constants
# ---------------------------------------------------------------------------

# Azure OpenAI GPT-4o serverless pricing (per 1K tokens)
_AI_INPUT_COST_PER_1K = 0.003
_AI_OUTPUT_COST_PER_1K = 0.015

# Cosmos DB serverless RU cost (per 100K RU)
_COSMOS_COST_PER_100K_RU = 0.25

# Estimated RU per conversation (read + write operations)
_RU_PER_CONVERSATION = 50.0

# Estimated RU per KB article (indexing + retrieval)
_RU_PER_ARTICLE = 20.0

# Container Apps base cost per month (amortized, consumption plan)
_CONTAINER_APPS_BASE_MONTHLY = 25.0

# Storage cost per article per month
_STORAGE_COST_PER_ARTICLE = 0.01


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class CostBreakdown(CamelCaseModel):
    """Cost breakdown by category."""

    ai_tokens: float = Field(description="AI token processing cost")
    cosmos_db: float = Field(description="Cosmos DB RU cost")
    storage: float = Field(description="Data storage cost")
    compute: float = Field(description="Container Apps compute share")
    total: float = Field(description="Total estimated cost")


class TenantCostProfile(CamelCaseModel):
    """Per-tenant cost profile with usage metrics."""

    tenant_id: str
    tier: str | None = None
    period_start: str
    period_end: str
    conversation_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    article_count: int = 0
    cost_breakdown: CostBreakdown
    cost_per_conversation: float = Field(
        description="Average cost per conversation",
    )
    cost_share_pct: float = Field(
        description="Percentage of total platform cost attributed to this tenant",
    )


class CostOverview(CamelCaseModel):
    """Cross-tenant cost summary."""

    period_start: str
    period_end: str
    total_platform_cost: float
    total_conversations: int
    total_tenants: int
    avg_cost_per_tenant: float
    avg_cost_per_conversation: float
    tenants: list[TenantCostProfile]
    cost_by_tier: dict[str, float] = Field(
        default_factory=dict,
        description="Total cost grouped by subscription tier",
    )


# ---------------------------------------------------------------------------
# Cost calculation helpers
# ---------------------------------------------------------------------------


def _calculate_cost(
    conversation_count: int,
    input_tokens: int,
    output_tokens: int,
    article_count: int,
    compute_share: float,
) -> CostBreakdown:
    """Calculate cost breakdown from usage metrics."""
    ai_cost = (
        (input_tokens / 1000) * _AI_INPUT_COST_PER_1K
        + (output_tokens / 1000) * _AI_OUTPUT_COST_PER_1K
    )

    # Cosmos DB RU: conversations + articles
    total_ru = (
        conversation_count * _RU_PER_CONVERSATION
        + article_count * _RU_PER_ARTICLE
    )
    cosmos_cost = (total_ru / 100_000) * _COSMOS_COST_PER_100K_RU

    storage_cost = article_count * _STORAGE_COST_PER_ARTICLE
    compute_cost = _CONTAINER_APPS_BASE_MONTHLY * compute_share

    total = ai_cost + cosmos_cost + storage_cost + compute_cost

    return CostBreakdown(
        ai_tokens=round(ai_cost, 4),
        cosmos_db=round(cosmos_cost, 4),
        storage=round(storage_cost, 4),
        compute=round(compute_cost, 4),
        total=round(total, 4),
    )


async def _get_tenant_usage(
    tenant_id: str,
    since: datetime,
    until: datetime,
) -> dict[str, Any]:
    """Fetch usage metrics for a tenant in the given period."""
    try:
        from src.multi_tenant.repositories import (
            ConversationRepository,
            UsageRepository,
        )

        conv_repo = ConversationRepository()
        usage_repo = UsageRepository()

        # Count conversations in period
        conversations = await conv_repo.count_in_period(
            tenant_id, since.isoformat(), until.isoformat(),
        )

        # Get token usage
        usage = await usage_repo.get_period_summary(
            tenant_id, since.isoformat(), until.isoformat(),
        )

        return {
            "conversation_count": conversations if isinstance(conversations, int) else 0,
            "input_tokens": usage.get("total_input_tokens", 0) if usage else 0,
            "output_tokens": usage.get("total_output_tokens", 0) if usage else 0,
        }
    except Exception:
        logger.exception("Failed to fetch usage for tenant=%s", tenant_id)
        return {
            "conversation_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
        }


async def _get_article_count(tenant_id: str) -> int:
    """Get KB article count for a tenant."""
    try:
        from src.multi_tenant.repositories import KnowledgeBaseRepository

        kb_repo = KnowledgeBaseRepository()
        result = await kb_repo.count(tenant_id)
        return result if isinstance(result, int) else 0
    except Exception:
        logger.debug("Failed to get article count for tenant=%s", tenant_id)
        return 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=CostOverview,
    summary="Cross-tenant cost overview (HV-2)",
    description="Estimates per-tenant costs based on usage metrics. "
    "Provides cost breakdown by AI tokens, database, storage, and compute.",
)
async def get_cost_overview(
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
) -> CostOverview:
    """Return cross-tenant cost estimates for the specified period."""
    until = datetime.now(UTC)
    since = until - timedelta(days=days)

    try:
        from src.multi_tenant.repositories import TenantRepository

        tenant_repo = TenantRepository()
        tenants = await tenant_repo.list_all_active()
    except Exception:
        logger.exception("Failed to list tenants for cost analysis")
        tenants = []

    tenant_profiles: list[TenantCostProfile] = []
    total_conversations = 0
    cost_by_tier: dict[str, float] = {}

    for tenant in tenants:
        tid = tenant.get("tenant_id", tenant.get("id", ""))
        tier = tenant.get("tier")

        usage = await _get_tenant_usage(tid, since, until)
        articles = await _get_article_count(tid)
        total_conversations += usage["conversation_count"]

    # Second pass: calculate costs with compute share
    total_convs_for_share = max(total_conversations, 1)
    for tenant in tenants:
        tid = tenant.get("tenant_id", tenant.get("id", ""))
        tier = tenant.get("tier")

        usage = await _get_tenant_usage(tid, since, until)
        articles = await _get_article_count(tid)

        compute_share = usage["conversation_count"] / total_convs_for_share

        cost = _calculate_cost(
            conversation_count=usage["conversation_count"],
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            article_count=articles,
            compute_share=compute_share,
        )

        cpc = (
            cost.total / usage["conversation_count"]
            if usage["conversation_count"] > 0
            else 0.0
        )

        profile = TenantCostProfile(
            tenant_id=tid,
            tier=tier,
            period_start=since.isoformat(),
            period_end=until.isoformat(),
            conversation_count=usage["conversation_count"],
            total_input_tokens=usage["input_tokens"],
            total_output_tokens=usage["output_tokens"],
            article_count=articles,
            cost_breakdown=cost,
            cost_per_conversation=round(cpc, 4),
            cost_share_pct=round(compute_share * 100, 2),
        )
        tenant_profiles.append(profile)

        tier_key = tier or "unknown"
        cost_by_tier[tier_key] = cost_by_tier.get(tier_key, 0) + cost.total

    total_cost = sum(p.cost_breakdown.total for p in tenant_profiles)
    num_tenants = len(tenant_profiles)

    return CostOverview(
        period_start=since.isoformat(),
        period_end=until.isoformat(),
        total_platform_cost=round(total_cost, 4),
        total_conversations=total_conversations,
        total_tenants=num_tenants,
        avg_cost_per_tenant=round(total_cost / max(num_tenants, 1), 4),
        avg_cost_per_conversation=round(
            total_cost / max(total_conversations, 1), 4,
        ),
        tenants=tenant_profiles,
        cost_by_tier={k: round(v, 4) for k, v in cost_by_tier.items()},
    )


@router.get(
    "/{tenant_id}",
    response_model=TenantCostProfile,
    summary="Per-tenant cost breakdown (HV-2)",
    description="Detailed cost breakdown for a specific tenant.",
)
async def get_tenant_cost(
    tenant_id: str,
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
) -> TenantCostProfile:
    """Return detailed cost breakdown for a single tenant."""
    until = datetime.now(UTC)
    since = until - timedelta(days=days)

    # Verify tenant exists
    try:
        from src.multi_tenant.repositories import TenantRepository

        tenant_repo = TenantRepository()
        tenant = await tenant_repo.read(tenant_id)
    except Exception:
        logger.exception("Failed to read tenant %s", tenant_id)
        raise HTTPException(status_code=500, detail="Failed to read tenant")

    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")

    tier = tenant.get("tier")
    usage = await _get_tenant_usage(tenant_id, since, until)
    articles = await _get_article_count(tenant_id)

    # For a single-tenant view, compute share is 100% of their own usage
    cost = _calculate_cost(
        conversation_count=usage["conversation_count"],
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        article_count=articles,
        compute_share=0.0,  # No compute share attribution for single-tenant view
    )

    cpc = (
        cost.total / usage["conversation_count"]
        if usage["conversation_count"] > 0
        else 0.0
    )

    return TenantCostProfile(
        tenant_id=tenant_id,
        tier=tier,
        period_start=since.isoformat(),
        period_end=until.isoformat(),
        conversation_count=usage["conversation_count"],
        total_input_tokens=usage["input_tokens"],
        total_output_tokens=usage["output_tokens"],
        article_count=articles,
        cost_breakdown=cost,
        cost_per_conversation=round(cpc, 4),
        cost_share_pct=0.0,  # Not meaningful for single-tenant view
    )
