"""Admin Analytics API — aggregated conversation metrics (WI #176-178).

Provides REST endpoints for the merchant admin dashboard's Analytics
Overview component:

    GET /api/analytics/summary  — Aggregated metrics for a date range
    GET /api/analytics/intents  — Top agents/intents by invocation volume
    GET /api/analytics/gaps     — Knowledge gap report (escalated/error convos)

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §7: WI #176-178 — Analytics APIs
    - Decision #1: TenantScopedRepository enforces tenant isolation
    - ConversationDocument schema in cosmos_schema.py

Dependencies:
    - repository.py: ConversationRepository (count_by_status,
      aggregate_metrics, list_agents_invoked, list_gap_conversations)
    - cosmos_schema.py: ConversationStatus
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import ConversationRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class StatusBreakdown(CamelCaseModel):
    """Conversation count for a single status."""

    status: str
    count: int


class AnalyticsSummaryResponse(CamelCaseModel):
    """Aggregated conversation metrics for a date range (WI #176)."""

    tenant_id: str
    since: str = Field(description="Start of date range (ISO 8601)")
    until: str = Field(description="End of date range (ISO 8601)")

    # Totals
    total_conversations: int = Field(description="Total conversations in range")
    billable_conversations: int = Field(description="Billable conversations")

    # Averages
    avg_turns: float = Field(description="Average turn count per conversation")
    avg_messages: float = Field(description="Average message count per conversation")

    # Frontend-expected fields (AnalyticsSummary type)
    avg_response_time: float | None = Field(default=None, description="Average response time in seconds")
    resolution_rate: float | None = Field(default=None, description="Resolution rate (0.0-1.0)")
    customer_satisfaction: float | None = Field(default=None, description="Customer satisfaction score (1.0-5.0)")

    # Status breakdown
    status_breakdown: list[StatusBreakdown] = Field(
        default_factory=list,
        description="Conversation count by status",
    )

    # Quality metrics
    escalation_count: int = Field(description="Conversations escalated to human")
    escalation_rate: float = Field(description="Escalation rate (0.0-1.0)")
    critic_passed: int = Field(description="Conversations where Critic approved")
    critic_failed: int = Field(description="Conversations where Critic rejected")
    critic_pass_rate: float = Field(description="Critic pass rate (0.0-1.0)")

    # First Contact Resolution (CQ-5)
    fcr_count: int = Field(
        default=0,
        description="First Contact Resolution count — resolved conversations "
        "with no follow-up from the same customer within 72 hours",
    )
    fcr_rate: float = Field(
        default=0.0,
        description="FCR rate (0.0-1.0)",
    )


class IntentEntry(CamelCaseModel):
    """A single agent/intent with its invocation count."""

    agent: str = Field(description="Agent name (e.g. intent-classifier)")
    invocation_count: int = Field(description="Number of conversations invoking this agent")
    percentage: float = Field(description="Percentage of total conversations")


class IntentsResponse(CamelCaseModel):
    """Top agents/intents by invocation volume (WI #177)."""

    tenant_id: str
    since: str
    until: str
    total_conversations: int = Field(description="Total conversations analysed")
    intents: list[IntentEntry] = Field(description="Agents sorted by invocation count (desc)")


class GapEntry(CamelCaseModel):
    """A conversation representing a potential knowledge gap."""

    conversation_id: str
    status: str
    customer_id: str | None = None
    turn_count: int = 0
    message_count: int = 0
    agents_invoked: list[str] = Field(default_factory=list)
    critic_passed: bool | None = None
    started_at: str | None = None
    ended_at: str | None = None


class GapsResponse(CamelCaseModel):
    """Knowledge gap report — conversations the AI couldn't resolve (WI #178)."""

    tenant_id: str
    since: str
    until: str
    total_gaps: int = Field(description="Total escalated + error conversations")
    escalated_count: int = Field(description="Conversations escalated to human")
    error_count: int = Field(description="Conversations ended in error")
    gaps: list[GapEntry] = Field(description="Gap conversations (newest first)")


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_conversation_repo: ConversationRepository | None = None


def configure_admin_analytics_services(
    conversation_repo: ConversationRepository,
) -> None:
    """Wire the admin analytics API to its backing repository.

    Called during app startup after ConversationRepository is initialised.
    """
    global _conversation_repo
    _conversation_repo = conversation_repo
    logger.info("Admin analytics API services configured")


def _get_repo() -> ConversationRepository:
    """Get the ConversationRepository, raising 503 if not initialised."""
    if _conversation_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin analytics services not initialised",
        )
    return _conversation_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_since() -> str:
    """Default date range start: 30 days ago."""
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()


def _default_until() -> str:
    """Default date range end: now."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/analytics", tags=["admin-analytics"])


# ---------------------------------------------------------------------------
# GET /api/analytics/summary — Aggregated metrics (WI #176)
# ---------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get analytics summary metrics",
    description=(
        "Returns aggregated conversation metrics for a date range including total/billable counts, average "
        "turns/messages, status breakdown, escalation rate, and Critic pass rate."
    ),
    responses={
        503: {"description": "Admin analytics services not initialized"},
    },
)
async def get_analytics_summary(
    since: str | None = Query(
        None,
        description="Start date (ISO 8601). Defaults to 30 days ago.",
    ),
    until: str | None = Query(
        None,
        description="End date (ISO 8601). Defaults to now.",
    ),
    is_test_mode: bool | None = Query(
        None,
        description="Filter by test mode: true = test only, false = production only, omit = all.",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AnalyticsSummaryResponse:
    """Get aggregated conversation metrics for a date range.

    Returns total/billable counts, average turns/messages, status breakdown,
    escalation rate, and Critic pass rate.

    Use ``is_test_mode`` to compare production vs test configuration
    performance side by side.
    """
    repo = _get_repo()

    effective_since = since or _default_since()
    effective_until = until or _default_until()

    # All dashboard metrics exclude non-billable conversations
    # (SPEC-1593..1600 — owner requirement: dashboard = billable only).
    # Parallel queries: aggregate metrics + status breakdown + FCR
    metrics = await repo.aggregate_metrics(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        is_test_mode=is_test_mode,
        billable_only=True,
    )

    status_counts = await repo.count_by_status(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        is_test_mode=is_test_mode,
        billable_only=True,
    )

    fcr_data = await repo.count_fcr(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        is_test_mode=is_test_mode,
        billable_only=True,
    )

    total = metrics.get("total", 0) or 0
    billable = metrics.get("billable", 0) or 0
    escalated = metrics.get("escalated", 0) or 0
    critic_passed = metrics.get("critic_passed", 0) or 0
    critic_failed = metrics.get("critic_failed", 0) or 0

    # Compute rates against billable total (= total when billable_only=True)
    escalation_rate = (escalated / total) if total > 0 else 0.0
    critic_total = critic_passed + critic_failed
    critic_pass_rate = (critic_passed / critic_total) if critic_total > 0 else 0.0

    # Resolution rate: proportion of non-escalated, non-error conversations
    resolved_count = sum(sc.get("count", 0) for sc in status_counts if sc.get("status") not in ("escalated", "error"))
    resolution_rate = (resolved_count / total) if total > 0 else 0.0

    status_breakdown = [
        StatusBreakdown(
            status=sc.get("status", "unknown"),
            count=sc.get("count", 0),
        )
        for sc in status_counts
    ]

    return AnalyticsSummaryResponse(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        total_conversations=total,
        billable_conversations=billable,
        avg_turns=round(metrics.get("avg_turns", 0) or 0, 2),
        avg_messages=round(metrics.get("avg_messages", 0) or 0, 2),
        avg_response_time=round(metrics.get("avg_response_time") or 0, 2),
        resolution_rate=round(resolution_rate, 4),
        customer_satisfaction=metrics.get("customer_satisfaction") or 0,
        status_breakdown=status_breakdown,
        escalation_count=escalated,
        escalation_rate=round(escalation_rate, 4),
        critic_passed=critic_passed,
        critic_failed=critic_failed,
        critic_pass_rate=round(critic_pass_rate, 4),
        fcr_count=fcr_data.get("fcr_count", 0),
        fcr_rate=fcr_data.get("fcr_rate", 0.0),
    )


# ---------------------------------------------------------------------------
# GET /api/analytics/intents — Top intents by volume (WI #177)
# ---------------------------------------------------------------------------


@router.get(
    "/intents",
    response_model=IntentsResponse,
    summary="Get intent distribution",
    description=(
        "Returns agent/intent invocation distribution for a date range, showing which pipeline stages are most active "
        "and identifying routing patterns."
    ),
    responses={
        503: {"description": "Admin analytics services not initialized"},
    },
)
async def get_intent_distribution(
    since: str | None = Query(
        None,
        description="Start date (ISO 8601). Defaults to 30 days ago.",
    ),
    until: str | None = Query(
        None,
        description="End date (ISO 8601). Defaults to now.",
    ),
    is_test_mode: bool | None = Query(
        None,
        description="Filter by test mode: true = test only, false = production only, omit = all.",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> IntentsResponse:
    """Get agent/intent invocation distribution for a date range.

    Counts how many conversations invoked each agent in the 6-agent
    pipeline. Useful for understanding which pipeline stages are most
    active and identifying routing patterns.

    Use ``is_test_mode`` to compare intent distribution between
    production and test configurations.
    """
    repo = _get_repo()

    effective_since = since or _default_since()
    effective_until = until or _default_until()

    # Top topics / topic breakdown: billable only (SPEC-1598, SPEC-1600)
    conversations = await repo.list_agents_invoked(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        is_test_mode=is_test_mode,
        billable_only=True,
    )

    total = len(conversations)

    # Count agent invocations across all conversations
    agent_counter: Counter[str] = Counter()
    for conv in conversations:
        agents = conv.get("agents_invoked", [])
        for agent in agents:
            agent_counter[agent] += 1

    # Sort by count descending
    intents = [
        IntentEntry(
            agent=agent,
            invocation_count=count,
            percentage=round((count / total) if total > 0 else 0.0, 4),
        )
        for agent, count in agent_counter.most_common()
    ]

    return IntentsResponse(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        total_conversations=total,
        intents=intents,
    )


# ---------------------------------------------------------------------------
# GET /api/analytics/gaps — Knowledge gap report (WI #178)
# ---------------------------------------------------------------------------


@router.get(
    "/gaps",
    response_model=GapsResponse,
    summary="Get knowledge gap report",
    description=(
        "Returns conversations with escalated or error status, representing cases where the AI could not resolve the "
        "customer's request. Useful for identifying missing knowledge base content."
    ),
    responses={
        503: {"description": "Admin analytics services not initialized"},
    },
)
async def get_knowledge_gaps(
    since: str | None = Query(
        None,
        description="Start date (ISO 8601). Defaults to 30 days ago.",
    ),
    until: str | None = Query(
        None,
        description="End date (ISO 8601). Defaults to now.",
    ),
    limit: int = Query(50, ge=1, le=200, description="Max gap entries (default 50)"),
    is_test_mode: bool | None = Query(
        None,
        description="Filter by test mode: true = test only, false = production only, omit = all.",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> GapsResponse:
    """Get knowledge gap report — conversations the AI couldn't resolve.

    Returns conversations with escalated or error status, representing
    cases where the AI was unable to satisfy the customer's request.
    Useful for identifying missing knowledge base content, common
    failure patterns, and training data opportunities.

    Use ``is_test_mode`` to isolate gaps from test configuration
    conversations vs production.
    """
    repo = _get_repo()

    effective_since = since or _default_since()
    effective_until = until or _default_until()

    # Knowledge gaps: billable only (SPEC-1597 — escalation rate)
    gap_conversations = await repo.list_gap_conversations(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        limit=limit,
        is_test_mode=is_test_mode,
        billable_only=True,
    )

    escalated_count = sum(1 for c in gap_conversations if c.get("status") == "escalated")
    error_count = sum(1 for c in gap_conversations if c.get("status") == "error")

    gaps = [
        GapEntry(
            conversation_id=c.get("conversation_id", ""),
            status=c.get("status", "unknown"),
            customer_id=c.get("customer_id"),
            turn_count=c.get("turn_count", 0),
            message_count=c.get("message_count", 0),
            agents_invoked=c.get("agents_invoked", []),
            critic_passed=c.get("critic_passed"),
            started_at=c.get("started_at"),
            ended_at=c.get("ended_at"),
        )
        for c in gap_conversations
    ]

    return GapsResponse(
        tenant_id=ctx.tenant_id,
        since=effective_since,
        until=effective_until,
        total_gaps=len(gap_conversations),
        escalated_count=escalated_count,
        error_count=error_count,
        gaps=gaps,
    )
