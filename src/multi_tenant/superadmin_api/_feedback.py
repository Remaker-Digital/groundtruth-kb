"""Superadmin API -- Feedback analytics (SPEC-1836).

Provides aggregate feedback metrics across tenants and conversations.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Query

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class FeedbackSummary(CamelCaseModel):
    """Aggregate feedback metrics for a tenant or platform-wide."""

    tenant_id: str | None = None
    total_feedback: int = 0
    positive_count: int = 0
    negative_count: int = 0
    satisfaction_rate: float | None = None  # positive / total, 0.0-1.0
    feedback_rate: float | None = None  # messages with feedback / total AI messages
    total_ai_messages: int = 0
    period_start: str | None = None
    period_end: str | None = None


class FeedbackDetail(CamelCaseModel):
    """Single feedback record for drill-down views."""

    tenant_id: str
    conversation_id: str
    message_id: str
    rating: str
    comment: str | None = None
    feedback_at: str | None = None


class FeedbackMetricsResponse(CamelCaseModel):
    """Response for GET /api/superadmin/feedback/metrics."""

    platform_summary: FeedbackSummary
    per_tenant: list[FeedbackSummary] = []


# ---------------------------------------------------------------------------
# GET /api/superadmin/feedback/metrics — Platform-wide feedback metrics
# ---------------------------------------------------------------------------


@router.get(
    "/feedback/metrics",
    response_model=FeedbackMetricsResponse,
    summary="Feedback metrics across all tenants (SPEC-1836)",
    description=(
        "Returns aggregate thumbs-up/down feedback metrics. Scans conversation "
        "documents for messages with feedback_rating metadata. Supports date "
        "range filtering."
    ),
    tags=["feedback"],
)
async def get_feedback_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Lookback period in days"),
) -> FeedbackMetricsResponse:
    """Compute aggregate feedback metrics across all tenants.

    Queries the conversations collection for messages that have
    feedback_rating in their metadata. Returns platform-wide and
    per-tenant satisfaction rates.
    """
    conv_repo = _state._conv_repo
    if not conv_repo:
        raise HTTPException(status_code=503, detail="Conversation repository not configured")

    period_end = datetime.now(timezone.utc)
    period_start = period_end - timedelta(days=days)

    # Query conversations with feedback in the time range
    try:
        results = await conv_repo.query(
            partition_key=None,  # Cross-partition query
            query=(
                "SELECT c.tenant_id, c.conversation_id, c.messages "
                "FROM c WHERE c.last_activity_at >= @start"
            ),
            parameters=[
                {"name": "@start", "value": period_start.isoformat()},
            ],
            cross_partition=True,
        )
    except Exception:
        logger.warning("Feedback metrics query failed — returning empty results")
        results = []

    # Aggregate feedback from message metadata
    per_tenant: dict[str, dict[str, int]] = {}

    for conv in results:
        tid = conv.get("tenant_id", "unknown")
        if tid not in per_tenant:
            per_tenant[tid] = {
                "positive": 0, "negative": 0, "total_ai": 0,
            }

        for msg in conv.get("messages", []):
            metadata = msg.get("metadata") or {}
            role = msg.get("role", "")

            if role == "ai":
                per_tenant[tid]["total_ai"] += 1

            rating = metadata.get("feedback_rating")
            if rating == "positive":
                per_tenant[tid]["positive"] += 1
            elif rating == "negative":
                per_tenant[tid]["negative"] += 1

    # Build per-tenant summaries
    tenant_summaries = []
    platform_positive = 0
    platform_negative = 0
    platform_ai = 0

    for tid, counts in sorted(per_tenant.items()):
        total = counts["positive"] + counts["negative"]
        sat_rate = counts["positive"] / total if total > 0 else None
        fb_rate = total / counts["total_ai"] if counts["total_ai"] > 0 else None

        tenant_summaries.append(FeedbackSummary(
            tenant_id=tid,
            total_feedback=total,
            positive_count=counts["positive"],
            negative_count=counts["negative"],
            satisfaction_rate=round(sat_rate, 4) if sat_rate is not None else None,
            feedback_rate=round(fb_rate, 4) if fb_rate is not None else None,
            total_ai_messages=counts["total_ai"],
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
        ))

        platform_positive += counts["positive"]
        platform_negative += counts["negative"]
        platform_ai += counts["total_ai"]

    platform_total = platform_positive + platform_negative
    platform_sat = platform_positive / platform_total if platform_total > 0 else None
    platform_fb_rate = platform_total / platform_ai if platform_ai > 0 else None

    return FeedbackMetricsResponse(
        platform_summary=FeedbackSummary(
            tenant_id=None,
            total_feedback=platform_total,
            positive_count=platform_positive,
            negative_count=platform_negative,
            satisfaction_rate=round(platform_sat, 4) if platform_sat is not None else None,
            feedback_rate=round(platform_fb_rate, 4) if platform_fb_rate is not None else None,
            total_ai_messages=platform_ai,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
        ),
        per_tenant=tenant_summaries,
    )


# ---------------------------------------------------------------------------
# GET /api/superadmin/feedback/{tenant_id} — Per-tenant feedback details
# ---------------------------------------------------------------------------


@router.get(
    "/feedback/{tenant_id}",
    response_model=list[FeedbackDetail],
    summary="Feedback details for a specific tenant (SPEC-1836)",
    description="Returns individual feedback records for a tenant, ordered by most recent.",
    tags=["feedback"],
)
async def get_tenant_feedback(
    tenant_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Lookback period in days"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
) -> list[FeedbackDetail]:
    """Retrieve individual feedback records for a specific tenant."""
    conv_repo = _state._conv_repo
    if not conv_repo:
        raise HTTPException(status_code=503, detail="Conversation repository not configured")

    period_start = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        results = await conv_repo.query(
            partition_key=tenant_id,
            query=(
                "SELECT c.tenant_id, c.conversation_id, c.messages "
                "FROM c WHERE c.tenant_id = @tid AND c.last_activity_at >= @start"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@start", "value": period_start.isoformat()},
            ],
        )
    except Exception:
        logger.warning("Tenant feedback query failed: tenant=%s", tenant_id)
        results = []

    # Extract feedback records from messages
    feedback_records: list[FeedbackDetail] = []

    for conv in results:
        for msg in conv.get("messages", []):
            metadata = msg.get("metadata") or {}
            rating = metadata.get("feedback_rating")
            if rating in ("positive", "negative"):
                feedback_records.append(FeedbackDetail(
                    tenant_id=tenant_id,
                    conversation_id=conv.get("conversation_id", ""),
                    message_id=msg.get("message_id", ""),
                    rating=rating,
                    comment=metadata.get("feedback_comment"),
                    feedback_at=metadata.get("feedback_at"),
                ))

    # Sort by most recent and limit
    feedback_records.sort(
        key=lambda r: r.feedback_at or "",
        reverse=True,
    )

    return feedback_records[:limit]
