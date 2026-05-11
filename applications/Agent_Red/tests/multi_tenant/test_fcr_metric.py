"""Tests for First Contact Resolution (FCR) proxy metric (CQ-5).

FCR definition: the percentage of conversations that were resolved on
the first contact without the customer reopening or following up within
72 hours.

Test matrix:
    FCR-01: Zero conversations returns fcr_rate=0
    FCR-02: All resolved, no follow-ups -> fcr_rate=1.0
    FCR-03: Some resolved with follow-ups -> fcr_rate < 1.0
    FCR-04: Only non-resolved conversations -> resolved_count=0, fcr_rate=0
    FCR-05: Date range filtering works
    FCR-06: is_test_mode filtering works
    FCR-07: Customer with multiple resolved conversations, some with follow-ups
    FCR-08: FCR fields appear in analytics summary response
    FCR-09: 72-hour window boundary: follow-up at exactly 72h is NOT counted
    FCR-10: Follow-up at 71h 59m IS counted as a repeat

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock

from src.multi_tenant.repository import ConversationRepository


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
SINCE = (NOW - timedelta(days=30)).isoformat()
UNTIL = NOW.isoformat()
TENANT_ID = "t-fcr-test"


def _ts(delta_hours: float = 0) -> str:
    """Generate an ISO timestamp relative to NOW."""
    return (NOW + timedelta(hours=delta_hours)).isoformat()


def _resolved_conv(
    conversation_id: str,
    customer_id: str,
    ended_hours_ago: float,
    is_test_mode: bool = False,
    started_at: str | None = None,
) -> dict[str, Any]:
    """Build a resolved conversation document for the first query."""
    ended_at = (NOW - timedelta(hours=ended_hours_ago)).isoformat()
    return {
        "conversation_id": conversation_id,
        "customer_id": customer_id,
        "ended_at": ended_at,
        "status": "resolved",
        "is_test_mode": is_test_mode,
        "started_at": started_at or (NOW - timedelta(hours=ended_hours_ago + 1)).isoformat(),
        "tenant_id": TENANT_ID,
    }


def _followup_conv(
    conversation_id: str,
    customer_id: str,
    started_at: str,
) -> dict[str, Any]:
    """Build a follow-up conversation document for the second query."""
    return {
        "conversation_id": conversation_id,
        "customer_id": customer_id,
        "started_at": started_at,
        "tenant_id": TENANT_ID,
    }


# ---------------------------------------------------------------------------
# FCR-01: Zero conversations returns fcr_rate=0
# ---------------------------------------------------------------------------


class TestFCR01ZeroConversations:
    """When there are no resolved conversations, FCR should be 0."""

    @pytest.mark.asyncio
    async def test_zero_resolved_returns_zero_rate(self):
        repo = ConversationRepository()
        # First query (resolved conversations) returns empty
        repo.query = AsyncMock(return_value=[])

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        assert result["resolved_count"] == 0
        assert result["fcr_count"] == 0
        assert result["fcr_rate"] == 0.0


# ---------------------------------------------------------------------------
# FCR-02: All resolved, no follow-ups -> fcr_rate=1.0
# ---------------------------------------------------------------------------


class TestFCR02AllResolvedNoFollowups:
    """When all conversations are resolved and no customer returned, FCR=1.0."""

    @pytest.mark.asyncio
    async def test_all_fcr_when_no_followups(self):
        resolved = [
            _resolved_conv("conv-1", "cust-A", ended_hours_ago=48),
            _resolved_conv("conv-2", "cust-B", ended_hours_ago=24),
            _resolved_conv("conv-3", "cust-C", ended_hours_ago=12),
        ]

        call_count = 0

        async def mock_query(tenant_id, query_text, params, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call: resolved conversations
                return resolved
            else:
                # Second call: follow-up window — return only the resolved
                # conversations themselves (they will be filtered out)
                return resolved

        repo = ConversationRepository()
        repo.query = AsyncMock(side_effect=mock_query)

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        assert result["resolved_count"] == 3
        assert result["fcr_count"] == 3
        assert result["fcr_rate"] == 1.0


# ---------------------------------------------------------------------------
# FCR-03: Some resolved with follow-ups -> fcr_rate < 1.0
# ---------------------------------------------------------------------------


class TestFCR03SomeFollowups:
    """When some customers follow up within 72h, FCR < 1.0."""

    @pytest.mark.asyncio
    async def test_partial_fcr(self):
        # 3 resolved conversations, cust-A has a follow-up within 72h
        resolved = [
            _resolved_conv("conv-1", "cust-A", ended_hours_ago=48),
            _resolved_conv("conv-2", "cust-B", ended_hours_ago=24),
            _resolved_conv("conv-3", "cust-C", ended_hours_ago=12),
        ]

        # cust-A's resolution ended 48h ago; follow-up started 24h ago
        # (24 hours after resolution = within 72h window)
        (NOW - timedelta(hours=48)).isoformat()
        followup_started = (NOW - timedelta(hours=24)).isoformat()

        followup_window_convs = resolved + [
            _followup_conv("conv-4", "cust-A", started_at=followup_started),
        ]

        call_count = 0

        async def mock_query(tenant_id, query_text, params, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return resolved
            else:
                return followup_window_convs

        repo = ConversationRepository()
        repo.query = AsyncMock(side_effect=mock_query)

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        assert result["resolved_count"] == 3
        assert result["fcr_count"] == 2  # cust-B and cust-C are FCR
        assert result["fcr_rate"] == pytest.approx(2 / 3, abs=0.001)


# ---------------------------------------------------------------------------
# FCR-04: Only non-resolved conversations -> resolved_count=0, fcr_rate=0
# ---------------------------------------------------------------------------


class TestFCR04NonResolvedOnly:
    """When no conversations are resolved, resolved_count and fcr_rate are 0."""

    @pytest.mark.asyncio
    async def test_no_resolved_conversations(self):
        repo = ConversationRepository()
        # The resolved query returns empty (no resolved conversations)
        repo.query = AsyncMock(return_value=[])

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        assert result["resolved_count"] == 0
        assert result["fcr_count"] == 0
        assert result["fcr_rate"] == 0.0
        # Only one query should be made (early return after empty resolved)
        repo.query.assert_called_once()


# ---------------------------------------------------------------------------
# FCR-05: Date range filtering works
# ---------------------------------------------------------------------------


class TestFCR05DateRangeFiltering:
    """Verify that since/until parameters are passed to the query."""

    @pytest.mark.asyncio
    async def test_since_and_until_in_query(self):
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])

        await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        repo.query.assert_called_once()
        query_text = repo.query.call_args[0][1]
        params = repo.query.call_args[0][2]

        assert "c.started_at >= @since" in query_text
        assert "c.started_at < @until" in query_text
        param_names = {p["name"] for p in params}
        assert "@since" in param_names
        assert "@until" in param_names

    @pytest.mark.asyncio
    async def test_since_only_no_until(self):
        """When until=None, the query should not include the upper bound."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])

        await repo.count_fcr(TENANT_ID, SINCE, until=None)

        query_text = repo.query.call_args[0][1]
        params = repo.query.call_args[0][2]

        assert "c.started_at >= @since" in query_text
        assert "@until" not in query_text
        param_names = {p["name"] for p in params}
        assert "@until" not in param_names


# ---------------------------------------------------------------------------
# FCR-06: is_test_mode filtering works
# ---------------------------------------------------------------------------


class TestFCR06TestModeFiltering:
    """Verify that is_test_mode parameter is correctly applied to queries."""

    @pytest.mark.asyncio
    async def test_test_mode_true(self):
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])

        await repo.count_fcr(TENANT_ID, SINCE, UNTIL, is_test_mode=True)

        query_text = repo.query.call_args[0][1]
        assert "c.is_test_mode = true" in query_text

    @pytest.mark.asyncio
    async def test_test_mode_false(self):
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])

        await repo.count_fcr(TENANT_ID, SINCE, UNTIL, is_test_mode=False)

        query_text = repo.query.call_args[0][1]
        assert "NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false" in query_text

    @pytest.mark.asyncio
    async def test_test_mode_none(self):
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])

        await repo.count_fcr(TENANT_ID, SINCE, UNTIL, is_test_mode=None)

        query_text = repo.query.call_args[0][1]
        assert "is_test_mode" not in query_text


# ---------------------------------------------------------------------------
# FCR-07: Customer with multiple resolved conversations, some with follow-ups
# ---------------------------------------------------------------------------


class TestFCR07MultipleResolvedSameCustomer:
    """A customer with multiple resolved conversations where only some
    have follow-ups within 72h."""

    @pytest.mark.asyncio
    async def test_multiple_resolved_partial_followup(self):
        # cust-A has 2 resolved conversations:
        # - conv-1 resolved 96h ago (no follow-up within 72h -> FCR)
        # - conv-2 resolved 24h ago (follow-up 12h ago = 12h after resolution -> NOT FCR)
        resolved = [
            _resolved_conv("conv-1", "cust-A", ended_hours_ago=96),
            _resolved_conv("conv-2", "cust-A", ended_hours_ago=24),
        ]

        # Follow-up started 12h ago (12 hours after conv-2 resolution)
        followup_started = (NOW - timedelta(hours=12)).isoformat()
        followup_convs = resolved + [
            _followup_conv("conv-3", "cust-A", started_at=followup_started),
        ]

        call_count = 0

        async def mock_query(tenant_id, query_text, params, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return resolved
            else:
                return followup_convs

        repo = ConversationRepository()
        repo.query = AsyncMock(side_effect=mock_query)

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        assert result["resolved_count"] == 2
        # conv-1: resolved 96h ago, follow-up at 12h ago = 84h after resolution -> outside 72h window -> FCR
        # conv-2: resolved 24h ago, follow-up at 12h ago = 12h after resolution -> inside 72h window -> NOT FCR
        assert result["fcr_count"] == 1
        assert result["fcr_rate"] == 0.5


# ---------------------------------------------------------------------------
# FCR-08: FCR fields appear in analytics summary response
# ---------------------------------------------------------------------------


class TestFCR08AnalyticsSummaryResponse:
    """Verify FCR fields are included in the analytics summary endpoint."""

    @pytest.fixture
    def fcr_client(self):
        """Create a TestClient with mock repo returning FCR data."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.multi_tenant.admin_analytics_api import (
            router,
            configure_admin_analytics_services,
        )
        from src.multi_tenant.middleware import get_tenant_context
        from src.multi_tenant.auth import TenantContext
        from src.multi_tenant.cosmos_schema import TenantTier, TenantStatus

        repo = AsyncMock(spec=ConversationRepository)
        repo.aggregate_metrics = AsyncMock(return_value={
            "total": 10, "billable": 10, "avg_turns": 3.0,
            "avg_messages": 6.0, "escalated": 1,
            "critic_passed": 8, "critic_failed": 1,
            "avg_response_time": 1.5, "customer_satisfaction": 4.0,
        })
        repo.count_by_status = AsyncMock(return_value=[
            {"status": "resolved", "count": 7},
            {"status": "escalated", "count": 1},
            {"status": "error", "count": 2},
        ])
        repo.count_fcr = AsyncMock(return_value={
            "resolved_count": 7,
            "fcr_count": 5,
            "fcr_rate": 0.7143,
        })

        configure_admin_analytics_services(repo)

        app = FastAPI()
        app.include_router(router)

        ctx = TenantContext(
            tenant_id=TENANT_ID,
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="api_key",
        )
        app.dependency_overrides[get_tenant_context] = lambda: ctx

        return TestClient(app)

    def test_fcr_fields_in_summary_response(self, fcr_client):
        """Analytics summary response must include fcrCount and fcrRate."""
        resp = fcr_client.get("/api/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "fcrCount" in data
        assert "fcrRate" in data
        assert data["fcrCount"] == 5
        assert data["fcrRate"] == pytest.approx(0.7143, abs=0.0001)

    def test_fcr_with_test_mode_filter(self, fcr_client):
        """FCR endpoint should be called with is_test_mode parameter."""
        resp = fcr_client.get("/api/analytics/summary?is_test_mode=true")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# FCR-09: 72-hour window boundary — follow-up at exactly 72h NOT counted
# ---------------------------------------------------------------------------


class TestFCR09BoundaryExactly72Hours:
    """A follow-up starting at exactly 72 hours after resolution is NOT
    counted as a repeat (the window is strictly less than 72h)."""

    @pytest.mark.asyncio
    async def test_followup_at_exactly_72h_is_fcr(self):
        # Resolved 100h ago
        resolved = [
            _resolved_conv("conv-1", "cust-A", ended_hours_ago=100),
        ]

        # Follow-up at exactly 72 hours after resolution
        # ended_at = NOW - 100h -> follow-up at NOW - 100h + 72h = NOW - 28h
        ended_at_dt = NOW - timedelta(hours=100)
        followup_at_72h = (ended_at_dt + timedelta(hours=72)).isoformat()

        followup_convs = resolved + [
            _followup_conv("conv-2", "cust-A", started_at=followup_at_72h),
        ]

        call_count = 0

        async def mock_query(tenant_id, query_text, params, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return resolved
            else:
                return followup_convs

        repo = ConversationRepository()
        repo.query = AsyncMock(side_effect=mock_query)

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        # Follow-up at exactly 72h is NOT within the window (< not <=)
        assert result["resolved_count"] == 1
        assert result["fcr_count"] == 1  # Still FCR
        assert result["fcr_rate"] == 1.0


# ---------------------------------------------------------------------------
# FCR-10: Follow-up at 71h 59m IS counted as a repeat
# ---------------------------------------------------------------------------


class TestFCR10Boundary71h59m:
    """A follow-up starting at 71h 59m after resolution IS counted as
    a repeat (within the 72h window)."""

    @pytest.mark.asyncio
    async def test_followup_at_71h59m_is_repeat(self):
        # Resolved 100h ago
        resolved = [
            _resolved_conv("conv-1", "cust-A", ended_hours_ago=100),
        ]

        # Follow-up at 71 hours 59 minutes after resolution
        ended_at_dt = NOW - timedelta(hours=100)
        followup_at_71h59m = (
            ended_at_dt + timedelta(hours=71, minutes=59)
        ).isoformat()

        followup_convs = resolved + [
            _followup_conv("conv-2", "cust-A", started_at=followup_at_71h59m),
        ]

        call_count = 0

        async def mock_query(tenant_id, query_text, params, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return resolved
            else:
                return followup_convs

        repo = ConversationRepository()
        repo.query = AsyncMock(side_effect=mock_query)

        result = await repo.count_fcr(TENANT_ID, SINCE, UNTIL)

        # Follow-up at 71h59m IS within the 72h window -> NOT FCR
        assert result["resolved_count"] == 1
        assert result["fcr_count"] == 0
        assert result["fcr_rate"] == 0.0
