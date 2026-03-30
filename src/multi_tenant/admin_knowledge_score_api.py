"""Admin Knowledge Score API — knowledge quality metrics and gap review (SPEC-1873).

Provides REST endpoints for knowledge quality observability:

    GET  /api/admin/knowledge/score         — Composite knowledge score + breakdown
    GET  /api/admin/knowledge/gaps/review   — Clustered unanswered-question review

Professional+ tier gate enforced on all endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.knowledge_score import (
    RELEVANCE_THRESHOLD,
    KnowledgeScoreBreakdown,
    classify_unanswered,
    cluster_gaps,
    compute_knowledge_score,
    compute_trend,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/knowledge", tags=["admin-knowledge-score"])

# ---------------------------------------------------------------------------
# Tier gating
# ---------------------------------------------------------------------------

_TIER_ORDER = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
_REQUIRED_TIER = "professional"


def _enforce_tier_gate(ctx: TenantContext) -> None:
    """Require professional+ tier. Platform admins bypass."""
    if ctx.is_platform_admin:
        return
    tenant_tier = ctx.tier.value if ctx.tier and hasattr(ctx.tier, "value") else (ctx.tier or "free")
    if _TIER_ORDER.get(str(tenant_tier), 0) < _TIER_ORDER[_REQUIRED_TIER]:
        raise HTTPException(
            status_code=403,
            detail="Knowledge score requires Professional tier or above.",
        )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ScoreFactors(CamelCaseModel):
    coverage: float = Field(description="Answered query ratio (0-1)")
    relevance: float = Field(description="Average KR relevance score (0-1)")
    escalation_rate: float = Field(description="Gap escalation rate (0-1, lower=better)")
    freshness: float = Field(description="Fraction of KB entries updated within 30d (0-1)")


class KnowledgeScoreResponse(CamelCaseModel):
    score: float = Field(description="Composite knowledge score (0-100)")
    factors: ScoreFactors
    total_conversations: int
    unanswered_count: int
    kb_entry_count: int
    fresh_entry_count: int
    trend: dict[str, Any] = Field(default_factory=dict)


class GapClusterEntry(CamelCaseModel):
    intent: str
    sample_question: str
    frequency: int
    last_occurrence: str
    suggested_action: str
    priority_score: float
    conversation_ids: list[str] = Field(default_factory=list)


class GapReviewResponse(CamelCaseModel):
    tenant_id: str
    since: str
    until: str
    total_gaps: int
    clusters: list[GapClusterEntry]


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/score
# ---------------------------------------------------------------------------


@router.get(
    "/score",
    summary="Knowledge quality score with factor breakdown",
    response_model=KnowledgeScoreResponse,
)
async def get_knowledge_score(
    since: str | None = Query(
        None,
        description="Start date (ISO 8601). Defaults to 30 days ago.",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> KnowledgeScoreResponse:
    """Compute and return the tenant's knowledge quality score.

    The score (0-100) reflects how well the KB serves customer queries,
    based on coverage, relevance, escalation rate, and content freshness.
    """
    _enforce_tier_gate(ctx)

    from src.multi_tenant.repository import ConversationRepository, KnowledgeBaseRepository

    conv_repo = ConversationRepository()
    kb_repo = KnowledgeBaseRepository()

    now = datetime.now(timezone.utc)
    effective_since = since or (now - timedelta(days=30)).isoformat()
    effective_until = now.isoformat()

    # Gather metrics from Cosmos
    try:
        metrics = await conv_repo.aggregate_metrics(
            ctx.tenant_id,
            since=effective_since,
            until=effective_until,
            is_test_mode=False,  # Production only
        )
    except Exception:
        logger.debug("aggregate_metrics failed, using defaults", exc_info=True)
        metrics = {}

    total_conversations = metrics.get("total", 0)
    escalation_count = metrics.get("escalated", 0) + metrics.get("error", 0)
    answered_conversations = total_conversations - escalation_count

    # Average relevance from pipeline traces
    avg_relevance = metrics.get("avg_confidence", 0.6)  # Fallback

    # KB freshness
    try:
        kb_entries = await kb_repo.list_filtered(
            tenant_id=ctx.tenant_id,
            limit=1000,
        )
        kb_entry_count = len(kb_entries) if kb_entries else 0
        freshness_cutoff = now - timedelta(days=30)
        fresh_count = 0
        for entry in (kb_entries or []):
            updated = getattr(entry, "updated_at", None) or getattr(entry, "created_at", None)
            if updated:
                try:
                    if isinstance(updated, str):
                        updated = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if updated.tzinfo is None:
                        updated = updated.replace(tzinfo=timezone.utc)
                    if updated >= freshness_cutoff:
                        fresh_count += 1
                except (ValueError, TypeError):
                    pass
    except Exception:
        logger.debug("KB freshness check failed", exc_info=True)
        kb_entry_count = 0
        fresh_count = 0

    breakdown = compute_knowledge_score(
        total_conversations=total_conversations,
        answered_conversations=answered_conversations,
        avg_relevance=avg_relevance,
        escalation_count=escalation_count,
        kb_entry_count=kb_entry_count,
        fresh_entry_count=fresh_count,
    )

    # Trend: compare with previous 30-day window
    prev_since = (now - timedelta(days=60)).isoformat()
    prev_until = (now - timedelta(days=30)).isoformat()
    try:
        prev_metrics = await conv_repo.aggregate_metrics(
            ctx.tenant_id,
            since=prev_since,
            until=prev_until,
            is_test_mode=False,
        )
        prev_total = prev_metrics.get("total", 0)
        prev_esc = prev_metrics.get("escalated", 0) + prev_metrics.get("error", 0)
        prev_answered = prev_total - prev_esc
        prev_breakdown = compute_knowledge_score(
            total_conversations=prev_total,
            answered_conversations=prev_answered,
            avg_relevance=prev_metrics.get("avg_confidence", 0.6),
            escalation_count=prev_esc,
            kb_entry_count=kb_entry_count,  # Use current KB count
            fresh_entry_count=fresh_count,
        )
        trend = compute_trend(breakdown.composite, prev_breakdown.composite)
    except Exception:
        trend = compute_trend(breakdown.composite, None)

    return KnowledgeScoreResponse(
        score=breakdown.composite,
        factors=ScoreFactors(
            coverage=round(breakdown.coverage, 3),
            relevance=round(breakdown.relevance, 3),
            escalation_rate=round(1.0 - breakdown.escalation, 3),
            freshness=round(breakdown.freshness, 3),
        ),
        total_conversations=breakdown.total_conversations,
        unanswered_count=breakdown.unanswered_count,
        kb_entry_count=breakdown.kb_entry_count,
        fresh_entry_count=breakdown.fresh_entry_count,
        trend=trend,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/knowledge/gaps/review
# ---------------------------------------------------------------------------


@router.get(
    "/gaps/review",
    summary="Clustered unanswered-question review",
    response_model=GapReviewResponse,
)
async def get_gap_review(
    since: str | None = Query(
        None,
        description="Start date (ISO 8601). Defaults to 30 days ago.",
    ),
    until: str | None = Query(
        None,
        description="End date (ISO 8601). Defaults to now.",
    ),
    limit: int = Query(50, ge=1, le=200, description="Max clusters returned"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> GapReviewResponse:
    """Return clustered unanswered questions with suggested KB actions.

    Groups escalated/error conversations by detected intent, computes
    frequency and priority, and suggests specific KB improvement actions.
    """
    _enforce_tier_gate(ctx)

    from src.multi_tenant.repository import ConversationRepository

    repo = ConversationRepository()

    now = datetime.now(timezone.utc)
    effective_since = since or (now - timedelta(days=30)).isoformat()
    effective_until = until or now.isoformat()

    # Fetch gap conversations (escalated + error)
    try:
        gap_convs = await repo.list_gap_conversations(
            tenant_id=ctx.tenant_id,
            since=effective_since,
            until=effective_until,
            is_test_mode=False,
            limit=500,  # Fetch more than output limit for clustering
        )
    except Exception:
        logger.debug("list_gap_conversations failed", exc_info=True)
        gap_convs = []

    # Convert to dicts for processing
    conv_dicts = []
    for conv in gap_convs:
        if isinstance(conv, dict):
            conv_dicts.append(conv)
        else:
            conv_dicts.append({
                "conversation_id": getattr(conv, "conversation_id", ""),
                "status": getattr(conv, "status", ""),
                "pipeline_trace": getattr(conv, "pipeline_trace", None),
                "started_at": str(getattr(conv, "started_at", "")),
                "last_activity_at": str(getattr(conv, "last_activity_at", "")),
                "metadata": getattr(conv, "metadata", None),
            })

    # Filter to truly unanswered
    unanswered = [c for c in conv_dicts if classify_unanswered(c)]

    # Cluster by intent
    clusters = cluster_gaps(unanswered, now=now)

    # Limit output
    clusters = clusters[:limit]

    return GapReviewResponse(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        total_gaps=len(unanswered),
        clusters=[
            GapClusterEntry(
                intent=c.intent,
                sample_question=c.sample_question,
                frequency=c.frequency,
                last_occurrence=c.last_occurrence,
                suggested_action=c.suggested_action,
                priority_score=c.priority_score,
                conversation_ids=c.conversation_ids,
            )
            for c in clusters
        ],
    )
