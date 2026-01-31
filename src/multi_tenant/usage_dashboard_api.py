"""Usage Dashboard API — billing transparency endpoints (Decision #25, WI #73-74).

Provides REST endpoints for the three-layer usage transparency model:

    Layer 1 — Real-time dashboard:   GET /api/dashboard/usage
              Daily volume breakdown: GET /api/dashboard/usage/daily
    Layer 2 — Per-conversation audit: GET /api/dashboard/conversations
              Single conversation:    GET /api/dashboard/conversations/{id}
              CSV export:             GET /api/dashboard/conversations/export

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters.  This guarantees tenant isolation: a merchant can
only see their own usage data.

The data layer (ConversationMeter, ConversationRepository, UsageRepository)
is already implemented.  This module is the HTTP surface that exposes it.

Architecture references
-----------------------
- Decision #25:  Three-layer usage transparency
- Decision #24:  Billable conversation definition
- WI #73:        Implement real-time usage dashboard
- WI #74:        Implement per-conversation audit trail with CSV export

Dependencies (all implemented):
- conversation_meter.py:  ConversationMeter, UsageDashboard
- repository.py:          ConversationRepository
- middleware.py:           get_tenant_context, TenantContext
- cosmos_schema.py:        ConversationStatus

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models (Pydantic)
# ---------------------------------------------------------------------------


class UsageDashboardResponse(BaseModel):
    """Layer 1: Real-time usage dashboard for the current billing period."""

    tenant_id: str
    billing_period: str

    # Counters
    total_conversations: int = Field(description="Total conversations this period")
    included_allowance: int = Field(description="Conversations included in plan")
    remaining_included: int = Field(description="Remaining free conversations")
    pack_balance: int = Field(description="Remaining prepaid pack conversations")
    overage_conversations: int = Field(description="Conversations billed as overage")
    overage_reported: int = Field(description="Overage events reported to Stripe")

    # Calculated
    usage_percent: float = Field(description="Usage as percentage of allowance")
    estimated_overage_cost: float = Field(description="Estimated overage cost (USD)")

    # Alerts
    active_alerts: list[str] = Field(
        default_factory=list,
        description="Active usage alerts (e.g. allowance_80_percent)",
    )


class DailyVolumeEntry(BaseModel):
    """A single day's conversation volume."""

    date: str = Field(description="Date (YYYY-MM-DD)")
    total: int = Field(description="Total conversations")
    billable: int = Field(description="Billable conversations")


class DailyVolumeResponse(BaseModel):
    """Daily volume breakdown for chart rendering."""

    tenant_id: str
    billing_period: str
    days: list[DailyVolumeEntry]


class ConversationSummary(BaseModel):
    """Compact conversation record for list endpoints."""

    conversation_id: str
    status: str | None = None
    customer_id: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None


class ConversationListResponse(BaseModel):
    """Paginated list of conversations with metadata."""

    tenant_id: str
    billing_period: str
    total_count: int = Field(description="Total matching conversations")
    offset: int
    limit: int
    conversations: list[ConversationSummary]


class ConversationDetailResponse(BaseModel):
    """Full billing detail for a single conversation (Layer 2)."""

    conversation_id: str
    tenant_id: str
    status: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    customer_id: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------
# The ConversationMeter and repositories are initialised at app startup and
# injected here.  In development (before full DI wiring), we use lazy module-
# level accessors that return None when the services aren't available yet.
#
# Production wiring: replace these with proper FastAPI dependency injection
# once the Cosmos DB connection is bootstrapped in main.py startup.
# ---------------------------------------------------------------------------

_conversation_meter: Any | None = None
_conversation_repo: Any | None = None


def configure_dashboard_services(
    conversation_meter: Any,
    conversation_repo: Any,
) -> None:
    """Wire the dashboard API to its backing services.

    Called during app startup after ConversationMeter and
    ConversationRepository are initialised.

    Args:
        conversation_meter: ConversationMeter instance.
        conversation_repo: ConversationRepository instance.
    """
    global _conversation_meter, _conversation_repo  # noqa: PLW0603
    _conversation_meter = conversation_meter
    _conversation_repo = conversation_repo
    logger.info("Usage dashboard API services configured")


def _get_meter() -> Any:
    """Get the ConversationMeter, raising 503 if not initialised."""
    if _conversation_meter is None:
        raise HTTPException(
            status_code=503,
            detail="Usage dashboard services not initialised",
        )
    return _conversation_meter


def _get_repo() -> Any:
    """Get the ConversationRepository, raising 503 if not initialised."""
    if _conversation_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Usage dashboard services not initialised",
        )
    return _conversation_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Layer 1: Real-time usage dashboard
# ---------------------------------------------------------------------------

@router.get("/usage", response_model=UsageDashboardResponse)
async def get_usage_dashboard(
    billing_period: str | None = Query(
        None,
        description="Billing period (YYYY-MM). Defaults to current period.",
        pattern=r"^\d{4}-\d{2}$",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> UsageDashboardResponse:
    """Get the real-time usage dashboard for the authenticated tenant.

    Returns current conversation counts, allowance remaining, overage
    estimate, pack balance, and active billing alerts.

    This is Layer 1 of the three-layer usage transparency model
    (Decision #25).
    """
    meter = _get_meter()

    dashboard = await meter.get_usage_dashboard(
        tenant_id=ctx.tenant_id,
        billing_period=billing_period,
    )

    return UsageDashboardResponse(
        tenant_id=dashboard.tenant_id,
        billing_period=dashboard.billing_period,
        total_conversations=dashboard.total_conversations,
        included_allowance=dashboard.included_allowance,
        remaining_included=dashboard.remaining_included,
        pack_balance=dashboard.pack_balance,
        overage_conversations=dashboard.overage_conversations,
        overage_reported=dashboard.overage_reported,
        usage_percent=dashboard.usage_percent,
        estimated_overage_cost=dashboard.estimated_overage_cost,
        active_alerts=[a.value for a in dashboard.active_alerts],
    )


# ---------------------------------------------------------------------------
# Layer 1 supplement: daily volume chart data
# ---------------------------------------------------------------------------

@router.get("/usage/daily", response_model=DailyVolumeResponse)
async def get_daily_volume(
    billing_period: str | None = Query(
        None,
        description="Billing period (YYYY-MM). Defaults to current period.",
        pattern=r"^\d{4}-\d{2}$",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> DailyVolumeResponse:
    """Get daily conversation volume for chart rendering.

    Returns per-day total and billable conversation counts for the
    specified billing period.  Used by the merchant dashboard to render
    a daily volume bar/line chart.
    """
    repo = _get_repo()

    if billing_period is None:
        billing_period = datetime.now(timezone.utc).strftime("%Y-%m")

    # Parse period to get date range
    try:
        year, month = billing_period.split("-")
        period_start = f"{year}-{month}-01T00:00:00Z"
    except (ValueError, IndexError):
        raise HTTPException(  # noqa: B904
            status_code=400,
            detail=f"Invalid billing_period format: {billing_period}. Expected YYYY-MM.",
        )

    # Calculate period end (first day of next month)
    month_int = int(month)
    year_int = int(year)
    if month_int == 12:
        next_year, next_month = year_int + 1, 1
    else:
        next_year, next_month = year_int, month_int + 1
    period_end = f"{next_year:04d}-{next_month:02d}-01T00:00:00Z"

    # Fetch all conversations in the period
    conversations = await repo.list_billable(
        tenant_id=ctx.tenant_id,
        since=period_start,
        until=period_end,
    )

    # Aggregate by day
    day_totals: dict[str, dict[str, int]] = {}  # date -> {total, billable}

    # First pass: count all conversations by day
    # list_billable only returns billable ones, so we also query all
    # conversations for total count
    all_conversations = await repo.query(
        tenant_id=ctx.tenant_id,
        query_text=(
            "SELECT c.started_at, c.is_billable FROM c "
            "WHERE c.started_at >= @since AND c.started_at < @until "
            "ORDER BY c.started_at ASC"
        ),
        parameters=[
            {"name": "@since", "value": period_start},
            {"name": "@until", "value": period_end},
        ],
    )

    for conv in all_conversations:
        started = conv.get("started_at", "")
        if not started:
            continue
        day = started[:10]  # YYYY-MM-DD
        if day not in day_totals:
            day_totals[day] = {"total": 0, "billable": 0}
        day_totals[day]["total"] += 1
        if conv.get("is_billable", False):
            day_totals[day]["billable"] += 1

    # Build sorted response
    days = [
        DailyVolumeEntry(
            date=day,
            total=counts["total"],
            billable=counts["billable"],
        )
        for day, counts in sorted(day_totals.items())
    ]

    return DailyVolumeResponse(
        tenant_id=ctx.tenant_id,
        billing_period=billing_period,
        days=days,
    )


# ---------------------------------------------------------------------------
# Layer 2: Per-conversation audit trail
# ---------------------------------------------------------------------------

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    billing_period: str | None = Query(
        None,
        description="Billing period (YYYY-MM). Defaults to current period.",
        pattern=r"^\d{4}-\d{2}$",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationListResponse:
    """List billable conversations for the authenticated tenant.

    Paginated list with compact summary per conversation.  Use the
    detail endpoint for full billing attribution on a specific
    conversation.

    This is Layer 2 of the three-layer usage transparency model
    (Decision #25).
    """
    repo = _get_repo()
    meter = _get_meter()

    if billing_period is None:
        billing_period = datetime.now(timezone.utc).strftime("%Y-%m")

    # Parse period
    try:
        year, month = billing_period.split("-")
        period_start = f"{year}-{month}-01T00:00:00Z"
    except (ValueError, IndexError):
        raise HTTPException(  # noqa: B904
            status_code=400,
            detail=f"Invalid billing_period format: {billing_period}. Expected YYYY-MM.",
        )

    month_int = int(month)
    year_int = int(year)
    if month_int == 12:
        next_year, next_month = year_int + 1, 1
    else:
        next_year, next_month = year_int, month_int + 1
    period_end = f"{next_year:04d}-{next_month:02d}-01T00:00:00Z"

    # Get total count for pagination metadata
    total_count = await repo.count_billable(
        tenant_id=ctx.tenant_id,
        since=period_start,
        until=period_end,
    )

    # Fetch page of conversations via paginated query
    conversations_raw = await repo.query(
        tenant_id=ctx.tenant_id,
        query_text=(
            "SELECT * FROM c "
            "WHERE c.is_billable = true "
            "AND c.started_at >= @since "
            "AND c.started_at < @until "
            "ORDER BY c.started_at DESC "
            "OFFSET @offset LIMIT @limit"
        ),
        parameters=[
            {"name": "@since", "value": period_start},
            {"name": "@until", "value": period_end},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ],
    )

    conversations = [
        ConversationSummary(
            conversation_id=c.get("conversation_id", c.get("id", "")),
            status=c.get("status"),
            customer_id=c.get("customer_id"),
            is_billable=c.get("is_billable", False),
            message_count=c.get("message_count", 0),
            turn_count=c.get("turn_count", 0),
            started_at=c.get("started_at"),
            ended_at=c.get("ended_at"),
            agents_invoked=c.get("agents_invoked", []),
            model_used=c.get("model_used"),
            critic_passed=c.get("critic_passed"),
        )
        for c in conversations_raw
    ]

    return ConversationListResponse(
        tenant_id=ctx.tenant_id,
        billing_period=billing_period,
        total_count=total_count,
        offset=offset,
        limit=limit,
        conversations=conversations,
    )


# ---------------------------------------------------------------------------
# Layer 2: Single conversation billing detail
# ---------------------------------------------------------------------------

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation_detail(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationDetailResponse:
    """Get full billing detail for a single conversation.

    Returns the complete billing attribution record including agents
    invoked, model used, Critic pass/fail, and timing data.
    """
    meter = _get_meter()

    try:
        detail = await meter.get_conversation_billing_detail(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
        )
    except Exception as exc:
        logger.warning(
            "Conversation detail lookup failed: tenant=%s conversation=%s error=%s",
            ctx.tenant_id[:8],
            conversation_id,
            exc,
        )
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        ) from exc

    return ConversationDetailResponse(**detail)


# ---------------------------------------------------------------------------
# Layer 2: CSV export
# ---------------------------------------------------------------------------

# CSV column definitions — controls export field order and headers
_CSV_COLUMNS = [
    ("conversation_id", "Conversation ID"),
    ("status", "Status"),
    ("customer_id", "Customer ID"),
    ("is_billable", "Billable"),
    ("message_count", "Messages"),
    ("turn_count", "Turns"),
    ("started_at", "Started At"),
    ("ended_at", "Ended At"),
    ("agents_invoked", "Agents Invoked"),
    ("model_used", "Model"),
    ("critic_passed", "Critic Passed"),
]


@router.get("/conversations/export")
async def export_conversations_csv(
    billing_period: str | None = Query(
        None,
        description="Billing period (YYYY-MM). Defaults to current period.",
        pattern=r"^\d{4}-\d{2}$",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> StreamingResponse:
    """Export billable conversations as a CSV file.

    Returns all billable conversations for the specified billing period
    in CSV format, suitable for download and import into spreadsheets
    or accounting systems.

    The CSV includes: conversation ID, status, customer ID, billable
    flag, message/turn counts, start/end timestamps, agents invoked,
    model used, and Critic pass/fail.
    """
    repo = _get_repo()

    if billing_period is None:
        billing_period = datetime.now(timezone.utc).strftime("%Y-%m")

    # Parse period
    try:
        year, month = billing_period.split("-")
        period_start = f"{year}-{month}-01T00:00:00Z"
    except (ValueError, IndexError):
        raise HTTPException(  # noqa: B904
            status_code=400,
            detail=f"Invalid billing_period format: {billing_period}. Expected YYYY-MM.",
        )

    month_int = int(month)
    year_int = int(year)
    if month_int == 12:
        next_year, next_month = year_int + 1, 1
    else:
        next_year, next_month = year_int, month_int + 1
    period_end = f"{next_year:04d}-{next_month:02d}-01T00:00:00Z"

    # Fetch all billable conversations (no pagination — full export)
    conversations = await repo.list_billable(
        tenant_id=ctx.tenant_id,
        since=period_start,
        until=period_end,
    )

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([header for _, header in _CSV_COLUMNS])

    # Data rows
    for conv in conversations:
        row: list[str] = []
        for field_name, _ in _CSV_COLUMNS:
            value = conv.get(field_name, "")
            if isinstance(value, list):
                value = "; ".join(str(v) for v in value)
            elif isinstance(value, bool):
                value = "Yes" if value else "No"
            elif value is None:
                value = ""
            row.append(str(value))
        writer.writerow(row)

    # Reset stream position for reading
    output.seek(0)

    filename = f"conversations-{ctx.tenant_id[:8]}-{billing_period}.csv"

    logger.info(
        "CSV export: tenant=%s period=%s rows=%d",
        ctx.tenant_id[:8],
        billing_period,
        len(conversations),
    )

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
