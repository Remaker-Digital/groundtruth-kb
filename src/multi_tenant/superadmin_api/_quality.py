"""Superadmin API -- Quality endpoints (SPEC-1838, SPEC-0188).

Provides read-only API endpoints for quality data:

  GET /quality/score         — Composite quality metrics (SPEC-1838)
  GET /quality/conversations — Per-conversation quality scores (SPEC-0188 / CQ-9)
  GET /quality/summary       — Aggregate quality summary (SPEC-0188 / CQ-9)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class QualityMetricResponse(CamelCaseModel):
    """Individual quality metric with value and description."""
    name: str = Field(description="Metric identifier")
    value: float = Field(description="Metric value (0.0-1.0 for ratios, raw for delta)")
    weight: float = Field(description="Weight in composite score")
    description: str = Field(description="Human-readable description")


class MutationScoreResponse(CamelCaseModel):
    """Mutation testing score and oracle gap analysis (SPEC-1842/WI-1498)."""
    score: float = Field(default=0.0, description="Mutation score (0.0-1.0)")
    killed: int = Field(default=0, description="Number of killed mutants")
    survived: int = Field(default=0, description="Number of survived mutants")
    timeout: int = Field(default=0, description="Number of timed-out mutants")
    oracle_gap_modules: list[dict] = Field(
        default_factory=list,
        description="Modules with high coverage but low mutation score",
    )


class QualityScoreResponse(CamelCaseModel):
    """Composite quality score and individual metrics (SPEC-1838)."""
    composite_score: float = Field(description="Weighted composite score (0-100)")
    metrics: list[QualityMetricResponse] = Field(description="Individual metric details")
    previous_coverage: float = Field(default=0.0, description="Previous line coverage %")
    current_coverage: float = Field(default=0.0, description="Current line coverage %")
    mutation_score: MutationScoreResponse | None = Field(
        default=None, description="Mutation testing score (if available)",
    )


class QualityConversationEntry(CamelCaseModel):
    """Single conversation quality entry (SPEC-0188 / CQ-9)."""
    conversation_id: str = Field(description="Conversation identifier")
    overall_score: float = Field(description="Overall quality score (1.0-5.0)")
    turn_count: int = Field(default=0, description="Number of scored turns")
    scored_at: str = Field(default="", description="ISO timestamp of scoring")


class QualitySummaryResponse(CamelCaseModel):
    """Aggregate quality summary across conversations (SPEC-0188 / CQ-9)."""
    mean_overall: float = Field(description="Mean overall quality score")
    trend: str = Field(description="Quality trend: improving, declining, or stable")
    score_distribution: dict[str, int] = Field(
        description="Score distribution buckets: 1-2, 2-3, 3-4, 4-5",
    )
    total_scored: int = Field(description="Total conversations scored")
    period_days: int = Field(default=30, description="Reporting period in days")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@_state.router.get(
    "/quality/score",
    response_model=QualityScoreResponse,
    summary="Get quality score dashboard (SPEC-1838)",
    tags=["quality"],
)
async def get_quality_score(
    ctx: TenantContext = Depends(get_tenant_context),
) -> QualityScoreResponse:
    """Return the current composite quality score and all 6 metrics.

    Requires platform admin authentication (SPA key).
    Reads from the Knowledge Database to compute real-time metrics.
    """
    if not ctx.is_platform_admin:
        raise HTTPException(status_code=403, detail="Platform admin required")

    try:
        from src.quality_metrics.quality_score import (
            compute_all_metrics,
            WEIGHTS,
        )
        import sys
        sys.path.insert(0, "tools/knowledge-db")
        from db import KnowledgeDB

        kb = KnowledgeDB()
        # TODO: Read previous/current coverage from quality_scores table
        # For now, use 0.0 defaults (delta will normalize to 0.5)
        result = compute_all_metrics(kb, previous_coverage=0.0, current_coverage=0.0)

        metrics = [
            QualityMetricResponse(
                name="spec_coverage",
                value=result["spec_coverage"],
                weight=WEIGHTS["spec_coverage"],
                description="Specs with at least one non-stale test",
            ),
            QualityMetricResponse(
                name="defect_escape_rate",
                value=result["defect_escape_rate"],
                weight=WEIGHTS["defect_escape_rate"],
                description="Open defects / total defects (lower is better)",
            ),
            QualityMetricResponse(
                name="assertion_strength",
                value=result["assertion_strength"],
                weight=WEIGHTS["assertion_strength"],
                description="Specs with machine-verifiable assertions",
            ),
            QualityMetricResponse(
                name="change_failure_rate",
                value=result["change_failure_rate"],
                weight=WEIGHTS["change_failure_rate"],
                description="Regressions / total work items (lower is better)",
            ),
            QualityMetricResponse(
                name="test_freshness",
                value=result["test_freshness"],
                weight=WEIGHTS["test_freshness"],
                description="Tests with pass/fail results vs total non-stale",
            ),
            QualityMetricResponse(
                name="coverage_delta",
                value=result["coverage_delta"],
                weight=WEIGHTS["coverage_delta"],
                description="Line coverage change since last session",
            ),
        ]

        # Mutation score (best-effort — may not have recent results)
        mutation = None
        try:
            from src.quality_metrics.mutation_tracking import (
                compute_mutation_score,
            )
            # Read latest mutation results from KB documents if available
            doc = kb._get_conn().execute(
                """SELECT content FROM current_documents
                   WHERE id = 'DOC-mutation-results'"""
            ).fetchone()
            if doc and doc[0]:
                import json as _json
                mdata = _json.loads(doc[0])
                mscore = compute_mutation_score(
                    mdata.get("killed", 0),
                    mdata.get("survived", 0),
                    mdata.get("timeout", 0),
                )
                mutation = MutationScoreResponse(
                    score=mscore,
                    killed=mdata.get("killed", 0),
                    survived=mdata.get("survived", 0),
                    timeout=mdata.get("timeout", 0),
                    oracle_gap_modules=mdata.get("oracle_gap_modules", []),
                )
        except Exception:
            pass  # Mutation data not yet available — return None

        return QualityScoreResponse(
            composite_score=result["composite_score"],
            metrics=metrics,
            previous_coverage=result["details"]["previous_line_coverage"],
            current_coverage=result["details"]["current_line_coverage"],
            mutation_score=mutation,
        )

    except Exception as e:
        logger.error("Quality score computation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Quality score computation failed: {e!s}",
        )


# ---------------------------------------------------------------------------
# CQ-9: Per-conversation quality endpoints (SPEC-0188 / WI-1519)
# ---------------------------------------------------------------------------


@_state.router.get(
    "/quality/conversations",
    response_model=list[QualityConversationEntry],
    summary="List conversation quality scores (SPEC-0188 / CQ-9)",
    tags=["quality"],
)
async def list_quality_conversations(
    limit: int = Query(default=50, ge=1, le=200, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[QualityConversationEntry]:
    """Return paginated conversation quality scores for the tenant.

    Reads quality_score metadata from Cosmos conversation documents.
    Requires platform admin authentication.
    """
    if not ctx.is_platform_admin:
        raise HTTPException(status_code=403, detail="Platform admin required")

    # Read from Cosmos conversations container
    try:
        from src.multi_tenant.cosmos_client import get_conversations_container

        container = get_conversations_container()
        query = (
            "SELECT c.id, c.quality_aggregate, c.message_count, c._ts "
            "FROM c WHERE c.quality_aggregate != null "
            "ORDER BY c._ts DESC "
            f"OFFSET {offset} LIMIT {limit}"
        )
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        entries = []
        for item in items:
            agg = item.get("quality_aggregate", {})
            entries.append(QualityConversationEntry(
                conversation_id=item["id"],
                overall_score=agg.get("overall", 0.0),
                turn_count=item.get("message_count", 0),
                scored_at=datetime.fromtimestamp(
                    item.get("_ts", 0), tz=timezone.utc
                ).isoformat() if item.get("_ts") else "",
            ))
        return entries

    except ImportError:
        # Cosmos not available (test/local mode) — return empty
        return []
    except Exception as e:
        logger.error("Failed to list quality conversations: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Quality data unavailable: {e!s}")


@_state.router.get(
    "/quality/summary",
    response_model=QualitySummaryResponse,
    summary="Get quality summary (SPEC-0188 / CQ-9)",
    tags=["quality"],
)
async def get_quality_summary(
    period_days: int = Query(default=30, ge=1, le=365, description="Reporting period"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> QualitySummaryResponse:
    """Return aggregate quality statistics for the tenant.

    Computes mean score, trend, and distribution from scored conversations
    within the specified period.  Requires platform admin authentication.
    """
    if not ctx.is_platform_admin:
        raise HTTPException(status_code=403, detail="Platform admin required")

    try:
        from src.multi_tenant.cosmos_client import get_conversations_container
        import time

        container = get_conversations_container()
        cutoff_ts = int(time.time()) - (period_days * 86400)

        query = (
            "SELECT c.quality_aggregate FROM c "
            f"WHERE c.quality_aggregate != null AND c._ts >= {cutoff_ts}"
        )
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        if not items:
            return QualitySummaryResponse(
                mean_overall=0.0,
                trend="stable",
                score_distribution={"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0},
                total_scored=0,
                period_days=period_days,
            )

        scores = [
            item["quality_aggregate"].get("overall", 0.0)
            for item in items
            if item.get("quality_aggregate")
        ]

        if not scores:
            return QualitySummaryResponse(
                mean_overall=0.0,
                trend="stable",
                score_distribution={"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0},
                total_scored=0,
                period_days=period_days,
            )

        mean_overall = round(sum(scores) / len(scores), 2)

        # Distribution buckets
        dist = {"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0}
        for s in scores:
            if s < 2.0:
                dist["1-2"] += 1
            elif s < 3.0:
                dist["2-3"] += 1
            elif s < 4.0:
                dist["3-4"] += 1
            else:
                dist["4-5"] += 1

        # Trend: compare first half vs second half
        mid = len(scores) // 2
        if mid > 0:
            first_half = sum(scores[:mid]) / mid
            second_half = sum(scores[mid:]) / (len(scores) - mid)
            delta = second_half - first_half
            if delta > 0.2:
                trend = "improving"
            elif delta < -0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return QualitySummaryResponse(
            mean_overall=mean_overall,
            trend=trend,
            score_distribution=dist,
            total_scored=len(scores),
            period_days=period_days,
        )

    except ImportError:
        # Cosmos not available — return empty summary
        return QualitySummaryResponse(
            mean_overall=0.0,
            trend="stable",
            score_distribution={"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0},
            total_scored=0,
            period_days=period_days,
        )
    except Exception as e:
        logger.error("Failed to compute quality summary: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Quality summary unavailable: {e!s}")
