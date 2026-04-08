"""Tests for Usage Dashboard API endpoint specifications.

Covers:
    - Router prefix verification
    - get_usage_dashboard with meter=None (zeroed fallback)
    - get_daily_volume with repo=None (empty days list)
    - list_conversations with repo=None (empty list)
    - get_conversation_detail (delegates to meter)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.usage_dashboard_api import (
    configure_dashboard_services,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", "test-tenant-001")
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


# ---------------------------------------------------------------------------
# DASH-01: Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Verify the dashboard router is mounted at /api/dashboard."""

    def test_router_prefix_is_api_dashboard(self):
        assert router.prefix == "/api/dashboard"


# ---------------------------------------------------------------------------
# DASH-02: get_usage_dashboard with meter=None
# ---------------------------------------------------------------------------


class TestGetUsageDashboard:
    """GET /api/dashboard/usage returns zeroed fallback when meter is None."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        configure_dashboard_services(None, None)
        yield
        configure_dashboard_services(None, None)

    @pytest.mark.asyncio
    async def test_meter_none_returns_zeroed_fallback(self):
        """When _conversation_meter is None, returns zeroed usage response."""
        from src.multi_tenant.usage_dashboard_api import get_usage_dashboard

        ctx = _ctx()
        response = await get_usage_dashboard(billing_period="2026-02", ctx=ctx)

        assert response.tenant_id == "test-tenant-001"
        assert response.billing_period == "2026-02"
        assert response.total_conversations == 0
        assert response.included_allowance == 0
        assert response.remaining_included == 0
        assert response.pack_balance == 0
        assert response.overage_conversations == 0
        assert response.usage_percent == 0.0
        assert response.estimated_overage_cost == 0.0
        assert response.active_alerts == []


# ---------------------------------------------------------------------------
# DASH-03: get_daily_volume with repo=None
# ---------------------------------------------------------------------------


class TestGetDailyVolume:
    """GET /api/dashboard/usage/daily returns empty days when repo is None."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        configure_dashboard_services(None, None)
        yield
        configure_dashboard_services(None, None)

    @pytest.mark.asyncio
    async def test_repo_none_returns_empty_days(self):
        """When _conversation_repo is None, returns empty days list."""
        from src.multi_tenant.usage_dashboard_api import get_daily_volume

        ctx = _ctx()
        response = await get_daily_volume(billing_period="2026-02", ctx=ctx)

        assert response.tenant_id == "test-tenant-001"
        assert response.billing_period == "2026-02"
        assert response.days == []


# ---------------------------------------------------------------------------
# DASH-04: list_conversations with repo=None
# ---------------------------------------------------------------------------


class TestListConversations:
    """GET /api/dashboard/conversations returns empty list when repo is None."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        configure_dashboard_services(None, None)
        yield
        configure_dashboard_services(None, None)

    @pytest.mark.asyncio
    async def test_repo_none_returns_empty_conversations(self):
        """When repos are None, returns empty conversation list."""
        from src.multi_tenant.usage_dashboard_api import list_conversations

        ctx = _ctx()
        response = await list_conversations(
            billing_period="2026-02", offset=0, limit=50, ctx=ctx,
        )

        assert response.tenant_id == "test-tenant-001"
        assert response.total_count == 0
        assert response.conversations == []
        assert response.offset == 0
        assert response.limit == 50


# ---------------------------------------------------------------------------
# DASH-05: get_conversation_detail delegates to meter
# ---------------------------------------------------------------------------


class TestGetConversationDetail:
    """GET /api/dashboard/conversations/{id} delegates to meter."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.meter = MagicMock()
        self.repo = MagicMock()
        configure_dashboard_services(self.meter, self.repo)
        yield
        configure_dashboard_services(None, None)

    @pytest.mark.asyncio
    async def test_conversation_detail_from_meter(self):
        """get_conversation_detail calls meter.get_conversation_billing_detail."""
        from src.multi_tenant.usage_dashboard_api import get_conversation_detail

        self.meter.get_conversation_billing_detail = AsyncMock(return_value={
            "conversation_id": "conv-123",
            "tenant_id": "test-tenant-001",
            "status": "ended",
            "is_billable": True,
            "message_count": 8,
            "turn_count": 4,
            "started_at": "2026-02-20T10:00:00Z",
            "ended_at": "2026-02-20T10:05:00Z",
            "customer_id": "cust-001",
            "agents_invoked": ["intent-classifier", "knowledge-retrieval"],
            "model_used": "gpt-4o",
            "critic_passed": True,
        })

        ctx = _ctx()
        response = await get_conversation_detail("conv-123", ctx=ctx)

        self.meter.get_conversation_billing_detail.assert_called_once_with(
            tenant_id="test-tenant-001",
            conversation_id="conv-123",
        )
        assert response.conversation_id == "conv-123"
        assert response.is_billable is True
        assert response.turn_count == 4
        assert "intent-classifier" in response.agents_invoked
