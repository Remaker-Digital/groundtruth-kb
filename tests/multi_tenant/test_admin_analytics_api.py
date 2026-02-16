"""Tests for admin analytics API test mode filtering (Priority 6).

Validates that the analytics endpoints correctly filter conversations
by test mode status: all, test-only, or production-only.

Test matrix:
    - GET /api/analytics/summary with is_test_mode=true/false/omitted
    - GET /api/analytics/intents with is_test_mode=true/false/omitted
    - GET /api/analytics/gaps with is_test_mode=true/false/omitted
    - Repository-level filter for aggregate_metrics, count_by_status,
      list_agents_invoked, list_gap_conversations

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

from src.multi_tenant.repository import ConversationRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NOW = datetime.now(timezone.utc)
SINCE = (NOW - timedelta(days=30)).isoformat()
UNTIL = NOW.isoformat()
TENANT_ID = "t-analytics-test"


def _make_conversation(
    conversation_id: str,
    is_test_mode: bool = False,
    status: str = "ended",
    is_billable: bool = True,
    turn_count: int = 3,
    message_count: int = 6,
    agents_invoked: list[str] | None = None,
    critic_passed: bool = True,
    started_at: str | None = None,
    ended_at: str | None = None,
) -> dict[str, Any]:
    """Build a mock conversation document."""
    return {
        "id": conversation_id,
        "tenant_id": TENANT_ID,
        "conversation_id": conversation_id,
        "status": status,
        "is_billable": is_billable,
        "is_test_mode": is_test_mode,
        "turn_count": turn_count,
        "message_count": message_count,
        "agents_invoked": agents_invoked or ["intent-classifier", "knowledge-retrieval", "response-generator"],
        "critic_passed": critic_passed,
        "customer_id": f"cust-{conversation_id}",
        "started_at": started_at or (NOW - timedelta(hours=2)).isoformat(),
        "ended_at": ended_at or (NOW - timedelta(hours=1)).isoformat(),
        "last_activity_at": (NOW - timedelta(hours=1)).isoformat(),
    }


# 6 conversations: 2 test mode + 4 production
CONVERSATIONS = [
    _make_conversation("conv-prod-1", is_test_mode=False, status="ended"),
    _make_conversation("conv-prod-2", is_test_mode=False, status="ended"),
    _make_conversation("conv-prod-3", is_test_mode=False, status="escalated"),
    _make_conversation("conv-prod-4", is_test_mode=False, status="error"),
    _make_conversation("conv-test-1", is_test_mode=True, status="ended"),
    _make_conversation("conv-test-2", is_test_mode=True, status="escalated"),
]


# ---------------------------------------------------------------------------
# Repository-level tests
# ---------------------------------------------------------------------------


class TestConversationRepositoryTestModeFilter:
    """Test that repository methods correctly filter by is_test_mode."""

    @pytest.mark.asyncio
    async def test_aggregate_metrics_all(self):
        """No filter returns all conversations."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[{
            "total": 6, "billable": 6, "avg_turns": 3,
            "avg_messages": 6, "escalated": 2,
            "critic_passed": 4, "critic_failed": 0,
        }])

        result = await repo.aggregate_metrics(TENANT_ID, SINCE, UNTIL)

        repo.query.assert_called_once()
        query_text = repo.query.call_args[0][1]
        assert "is_test_mode" not in query_text
        assert result["total"] == 6

    @pytest.mark.asyncio
    async def test_aggregate_metrics_test_only(self):
        """is_test_mode=True filters to test conversations."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[{
            "total": 2, "billable": 2, "avg_turns": 3,
            "avg_messages": 6, "escalated": 1,
            "critic_passed": 1, "critic_failed": 0,
        }])

        result = await repo.aggregate_metrics(
            TENANT_ID, SINCE, UNTIL, is_test_mode=True,
        )

        repo.query.assert_called_once()
        query_text = repo.query.call_args[0][1]
        assert "c.is_test_mode = true" in query_text
        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_aggregate_metrics_production_only(self):
        """is_test_mode=False filters to production conversations."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[{
            "total": 4, "billable": 4, "avg_turns": 3,
            "avg_messages": 6, "escalated": 1,
            "critic_passed": 3, "critic_failed": 0,
        }])

        result = await repo.aggregate_metrics(
            TENANT_ID, SINCE, UNTIL, is_test_mode=False,
        )

        repo.query.assert_called_once()
        query_text = repo.query.call_args[0][1]
        assert "NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false" in query_text
        assert result["total"] == 4

    @pytest.mark.asyncio
    async def test_count_by_status_test_only(self):
        """count_by_status with is_test_mode=True."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[
            {"status": "ended", "count": 1},
            {"status": "escalated", "count": 1},
        ])

        result = await repo.count_by_status(
            TENANT_ID, SINCE, UNTIL, is_test_mode=True,
        )

        query_text = repo.query.call_args[0][1]
        assert "c.is_test_mode = true" in query_text
        assert "GROUP BY c.status" in query_text
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_by_status_production_only(self):
        """count_by_status with is_test_mode=False."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[
            {"status": "ended", "count": 2},
            {"status": "escalated", "count": 1},
            {"status": "error", "count": 1},
        ])

        result = await repo.count_by_status(
            TENANT_ID, SINCE, UNTIL, is_test_mode=False,
        )

        query_text = repo.query.call_args[0][1]
        assert "NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false" in query_text
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_list_agents_invoked_test_only(self):
        """list_agents_invoked with is_test_mode=True."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[
            {"conversation_id": "conv-test-1", "agents_invoked": ["ic", "kr", "rg"], "status": "ended", "started_at": NOW.isoformat(), "tenant_id": TENANT_ID},
        ])

        result = await repo.list_agents_invoked(
            TENANT_ID, SINCE, UNTIL, is_test_mode=True,
        )

        query_text = repo.query.call_args[0][1]
        assert "c.is_test_mode = true" in query_text
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_agents_invoked_all(self):
        """list_agents_invoked without filter returns all."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[{"conversation_id": f"c{i}"} for i in range(6)])

        result = await repo.list_agents_invoked(TENANT_ID, SINCE, UNTIL)

        query_text = repo.query.call_args[0][1]
        assert "is_test_mode" not in query_text
        assert len(result) == 6

    @pytest.mark.asyncio
    async def test_list_gap_conversations_test_only(self):
        """list_gap_conversations with is_test_mode=True."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[
            {"conversation_id": "conv-test-2", "status": "escalated", "tenant_id": TENANT_ID},
        ])

        result = await repo.list_gap_conversations(
            TENANT_ID, SINCE, UNTIL, limit=50, is_test_mode=True,
        )

        query_text = repo.query.call_args[0][1]
        assert "c.is_test_mode = true" in query_text
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_gap_conversations_production_only(self):
        """list_gap_conversations with is_test_mode=False."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[
            {"conversation_id": "conv-prod-3", "status": "escalated", "tenant_id": TENANT_ID},
            {"conversation_id": "conv-prod-4", "status": "error", "tenant_id": TENANT_ID},
        ])

        result = await repo.list_gap_conversations(
            TENANT_ID, SINCE, UNTIL, limit=50, is_test_mode=False,
        )

        query_text = repo.query.call_args[0][1]
        assert "NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false" in query_text
        assert len(result) == 2


# ---------------------------------------------------------------------------
# API endpoint tests (standalone FastAPI app — no middleware)
# ---------------------------------------------------------------------------


def _make_tenant_context():
    from src.multi_tenant.auth import TenantContext
    from src.multi_tenant.cosmos_schema import TenantTier, TenantStatus
    return TenantContext(
        tenant_id=TENANT_ID,
        tier=TenantTier.STARTER,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


@pytest.fixture
def mock_repo():
    """Create a mock ConversationRepository with canned data."""
    repo = AsyncMock(spec=ConversationRepository)
    repo.aggregate_metrics = AsyncMock(return_value={
        "total": 2, "billable": 2, "avg_turns": 3.0,
        "avg_messages": 6.0, "escalated": 1,
        "critic_passed": 1, "critic_failed": 0,
    })
    repo.count_by_status = AsyncMock(return_value=[
        {"status": "ended", "count": 1},
        {"status": "escalated", "count": 1},
    ])
    repo.list_agents_invoked = AsyncMock(return_value=[
        {"conversation_id": "c1", "agents_invoked": ["ic", "kr"],
         "status": "ended", "started_at": NOW.isoformat(), "tenant_id": TENANT_ID},
    ])
    repo.list_gap_conversations = AsyncMock(return_value=[
        {"conversation_id": "c1", "status": "escalated", "customer_id": "cust-1",
         "turn_count": 3, "message_count": 6, "agents_invoked": ["ic"],
         "critic_passed": True, "started_at": NOW.isoformat(),
         "ended_at": NOW.isoformat(), "tenant_id": TENANT_ID},
    ])
    return repo


@pytest.fixture
def client(mock_repo):
    """Create a TestClient with the analytics router (no auth middleware)."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.multi_tenant.admin_analytics_api import (
        router,
        configure_admin_analytics_services,
    )
    from src.multi_tenant.middleware import get_tenant_context

    configure_admin_analytics_services(mock_repo)

    app = FastAPI()
    app.include_router(router)

    ctx = _make_tenant_context()
    app.dependency_overrides[get_tenant_context] = lambda: ctx

    return TestClient(app)


class TestAnalyticsEndpointTestModeFilter:
    """Test that analytics API endpoints accept is_test_mode query parameter."""

    def test_summary_no_filter(self, client, mock_repo):
        """GET /api/analytics/summary without is_test_mode passes None."""
        resp = client.get("/api/analytics/summary")
        assert resp.status_code == 200
        mock_repo.aggregate_metrics.assert_called_once()
        call_kwargs = mock_repo.aggregate_metrics.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is None

    def test_summary_test_mode_true(self, client, mock_repo):
        """GET /api/analytics/summary?is_test_mode=true filters test."""
        resp = client.get("/api/analytics/summary?is_test_mode=true")
        assert resp.status_code == 200
        call_kwargs = mock_repo.aggregate_metrics.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is True

    def test_summary_test_mode_false(self, client, mock_repo):
        """GET /api/analytics/summary?is_test_mode=false filters production."""
        resp = client.get("/api/analytics/summary?is_test_mode=false")
        assert resp.status_code == 200
        call_kwargs = mock_repo.aggregate_metrics.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is False

    def test_summary_status_breakdown_also_filtered(self, client, mock_repo):
        """count_by_status also receives is_test_mode when filtering."""
        resp = client.get("/api/analytics/summary?is_test_mode=true")
        assert resp.status_code == 200
        call_kwargs = mock_repo.count_by_status.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is True

    def test_intents_test_mode_true(self, client, mock_repo):
        """GET /api/analytics/intents?is_test_mode=true filters test."""
        resp = client.get("/api/analytics/intents?is_test_mode=true")
        assert resp.status_code == 200
        call_kwargs = mock_repo.list_agents_invoked.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is True

    def test_intents_no_filter(self, client, mock_repo):
        """GET /api/analytics/intents without is_test_mode passes None."""
        resp = client.get("/api/analytics/intents")
        assert resp.status_code == 200
        call_kwargs = mock_repo.list_agents_invoked.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is None

    def test_gaps_test_mode_true(self, client, mock_repo):
        """GET /api/analytics/gaps?is_test_mode=true filters test."""
        resp = client.get("/api/analytics/gaps?is_test_mode=true")
        assert resp.status_code == 200
        call_kwargs = mock_repo.list_gap_conversations.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is True

    def test_gaps_test_mode_false(self, client, mock_repo):
        """GET /api/analytics/gaps?is_test_mode=false filters production."""
        resp = client.get("/api/analytics/gaps?is_test_mode=false")
        assert resp.status_code == 200
        call_kwargs = mock_repo.list_gap_conversations.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is False

    def test_gaps_no_filter(self, client, mock_repo):
        """GET /api/analytics/gaps without is_test_mode passes None."""
        resp = client.get("/api/analytics/gaps")
        assert resp.status_code == 200
        call_kwargs = mock_repo.list_gap_conversations.call_args
        assert call_kwargs.kwargs.get("is_test_mode") is None

    def test_summary_response_shape(self, client, mock_repo):
        """Summary response includes all expected fields."""
        resp = client.get("/api/analytics/summary?is_test_mode=true")
        data = resp.json()
        assert "totalConversations" in data
        assert "billableConversations" in data
        assert "escalationRate" in data
        assert "criticPassRate" in data
        assert "statusBreakdown" in data

    def test_intents_response_shape(self, client, mock_repo):
        """Intents response includes all expected fields."""
        resp = client.get("/api/analytics/intents?is_test_mode=true")
        data = resp.json()
        assert "totalConversations" in data
        assert "intents" in data
        assert isinstance(data["intents"], list)

    def test_gaps_response_shape(self, client, mock_repo):
        """Gaps response includes all expected fields."""
        resp = client.get("/api/analytics/gaps?is_test_mode=false")
        data = resp.json()
        assert "totalGaps" in data
        assert "escalatedCount" in data
        assert "errorCount" in data
        assert "gaps" in data
        assert isinstance(data["gaps"], list)


# ---------------------------------------------------------------------------
# D36/D37 regression: zero-conversation defaults must be 0, not 2.3/4.2
# ---------------------------------------------------------------------------


class TestZeroConversationDefaults:
    """When totalConversations=0, avgResponseTime and customerSatisfaction
    must both be 0 — not hardcoded non-zero defaults (D36/D37)."""

    @pytest.fixture
    def zero_conv_client(self):
        """Client with repo returning zero conversations."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.multi_tenant.admin_analytics_api import (
            router,
            configure_admin_analytics_services,
        )
        from src.multi_tenant.middleware import get_tenant_context

        repo = AsyncMock(spec=ConversationRepository)
        # Simulate aggregate_metrics returning the empty-result fallback
        repo.aggregate_metrics = AsyncMock(return_value={
            "total": 0, "billable": 0, "avg_turns": 0,
            "avg_messages": 0, "escalated": 0,
            "critic_passed": 0, "critic_failed": 0,
            "avg_response_time": 0, "customer_satisfaction": 0,
        })
        repo.count_by_status = AsyncMock(return_value=[])
        repo.list_agents_invoked = AsyncMock(return_value=[])
        repo.list_gap_conversations = AsyncMock(return_value=[])

        configure_admin_analytics_services(repo)
        app = FastAPI()
        app.include_router(router)

        ctx = _make_tenant_context()
        app.dependency_overrides[get_tenant_context] = lambda: ctx

        return TestClient(app)

    def test_avg_response_time_zero_when_no_conversations(self, zero_conv_client):
        """D36: avgResponseTime must be 0 (not 2.3) when totalConversations=0."""
        resp = zero_conv_client.get("/api/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalConversations"] == 0
        assert data["avgResponseTime"] == 0

    def test_customer_satisfaction_zero_when_no_conversations(self, zero_conv_client):
        """D37: customerSatisfaction must be 0 (not 4.2) when totalConversations=0."""
        resp = zero_conv_client.get("/api/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalConversations"] == 0
        assert data["customerSatisfaction"] == 0

    def test_avg_response_time_not_hardcoded_default(self, zero_conv_client):
        """avgResponseTime must never fall back to 2.3 for empty tenants."""
        resp = zero_conv_client.get("/api/analytics/summary")
        data = resp.json()
        assert data["avgResponseTime"] != 2.3

    def test_customer_satisfaction_not_hardcoded_default(self, zero_conv_client):
        """customerSatisfaction must never fall back to 4.2 for empty tenants."""
        resp = zero_conv_client.get("/api/analytics/summary")
        data = resp.json()
        assert data["customerSatisfaction"] != 4.2


class TestRepositoryEmptyResultFallback:
    """Verify that aggregate_metrics empty-result dict includes
    avg_response_time and customer_satisfaction keys."""

    @pytest.mark.asyncio
    async def test_empty_result_includes_response_time(self):
        """aggregate_metrics returns avg_response_time=0 when no results."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])
        result = await repo.aggregate_metrics(TENANT_ID, SINCE, UNTIL)
        assert "avg_response_time" in result
        assert result["avg_response_time"] == 0

    @pytest.mark.asyncio
    async def test_empty_result_includes_customer_satisfaction(self):
        """aggregate_metrics returns customer_satisfaction=0 when no results."""
        repo = ConversationRepository()
        repo.query = AsyncMock(return_value=[])
        result = await repo.aggregate_metrics(TENANT_ID, SINCE, UNTIL)
        assert "customer_satisfaction" in result
        assert result["customer_satisfaction"] == 0
