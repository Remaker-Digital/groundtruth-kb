"""Tests for CostAnalytics and AbuseDetection superadmin endpoints (WI #88, WI #89).

Verifies:
- Cost overview returns expected structure with per-tenant breakdown
- Abuse signals scan detects rate anomalies and error rates
- Tenant flag toggle works correctly
- Response models serialize with camelCase

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Cost Analytics response model tests
# ---------------------------------------------------------------------------


class TestCostModels:
    """Verify cost analytics response models."""

    def test_cost_breakdown_defaults(self):
        from src.multi_tenant.superadmin_api import CostBreakdownModel

        cb = CostBreakdownModel()
        assert cb.ai_tokens == 0.0
        assert cb.cosmos_db == 0.0
        assert cb.total == 0.0

    def test_cost_overview_response_structure(self):
        from src.multi_tenant.superadmin_api import CostOverviewResponse

        resp = CostOverviewResponse(
            period_start="2026-01-01",
            period_end="2026-01-31",
            total_platform_cost=1.5,
            total_conversations=100,
            total_tenants=2,
            avg_cost_per_tenant=0.75,
            avg_cost_per_conversation=0.015,
        )
        assert resp.total_platform_cost == 1.5
        assert resp.total_tenants == 2

    def test_cost_overview_camel_case_serialization(self):
        from src.multi_tenant.superadmin_api import CostOverviewResponse

        resp = CostOverviewResponse(
            period_start="2026-01-01",
            period_end="2026-01-31",
            total_platform_cost=1.5,
            total_conversations=100,
            total_tenants=2,
        )
        data = resp.model_dump(mode="json", by_alias=True)
        assert "totalPlatformCost" in data
        assert "totalConversations" in data


# ---------------------------------------------------------------------------
# Abuse Detection response model tests
# ---------------------------------------------------------------------------


class TestAbuseModels:
    """Verify abuse detection response models."""

    def test_abuse_signal_model(self):
        from src.multi_tenant.superadmin_api import AbuseSignalModel

        sig = AbuseSignalModel(
            tenant_id="t-001",
            signal_type="rate_anomaly",
            severity="high",
            description="150 conversations in 24h",
            detected_at="2026-01-01T00:00:00Z",
            metric_value=150.0,
            threshold=100.0,
        )
        assert sig.severity == "high"

    def test_abuse_overview_defaults(self):
        from src.multi_tenant.superadmin_api import AbuseOverviewResponse

        resp = AbuseOverviewResponse()
        assert resp.total_tenants_scanned == 0
        assert resp.flagged_count == 0
        assert resp.high_risk_tenants == []

    def test_flag_tenant_request(self):
        from src.multi_tenant.superadmin_api import FlagTenantRequest

        req = FlagTenantRequest(flagged=True)
        assert req.flagged is True


# ---------------------------------------------------------------------------
# Cost Analytics endpoint test
# ---------------------------------------------------------------------------


class TestCostEndpoint:
    """Tests for GET /api/superadmin/costs."""

    @pytest.mark.asyncio
    async def test_cost_analytics_returns_overview(self):
        from src.multi_tenant.superadmin_api import get_cost_analytics

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["t-001"])
        mock_tenant_repo.read = AsyncMock(return_value={"tier": "starter"})

        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=[
            {"id": "c1", "message_count": 5, "messages": [{"role": "customer"}, {"role": "agent"}]},
            {"id": "c2", "message_count": 3, "messages": [{"role": "customer"}]},
        ])

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "spa"

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._conv_repo", mock_conv_repo),
            patch(
                "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
                return_value=MagicMock(query=AsyncMock(return_value=[5])),
            ),
        ):
            resp = await get_cost_analytics(days=30, ctx=mock_ctx)

        assert resp.total_tenants == 1
        assert resp.total_conversations == 2
        assert resp.total_platform_cost > 0
        assert len(resp.tenants) == 1
        assert resp.tenants[0].tenant_id == "t-001"
        assert resp.tenants[0].cost_breakdown.total > 0

    @pytest.mark.asyncio
    async def test_cost_analytics_service_not_initialized(self):
        from fastapi import HTTPException

        from src.multi_tenant.superadmin_api import get_cost_analytics

        mock_ctx = MagicMock()

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", None),
            pytest.raises(HTTPException) as exc_info,
        ):
            await get_cost_analytics(days=30, ctx=mock_ctx)

        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Abuse Detection endpoint tests
# ---------------------------------------------------------------------------


class TestAbuseEndpoint:
    """Tests for GET /api/superadmin/abuse/signals."""

    @pytest.mark.asyncio
    async def test_abuse_scan_no_anomalies(self):
        """Clean tenant produces no signals."""
        from src.multi_tenant.superadmin_api import get_abuse_signals

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["t-001"])
        mock_tenant_repo.read = AsyncMock(return_value={
            "tier": "starter",
            "abuse_flagged": False,
        })

        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=[
            {"status": "resolved"} for _ in range(5)
        ])

        mock_ctx = MagicMock()

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._conv_repo", mock_conv_repo),
        ):
            resp = await get_abuse_signals(ctx=mock_ctx)

        assert resp.total_tenants_scanned == 1
        assert resp.flagged_count == 0
        assert len(resp.high_risk_tenants) == 0

    @pytest.mark.asyncio
    async def test_abuse_scan_detects_rate_anomaly(self):
        """High conversation rate triggers rate_anomaly signal."""
        from src.multi_tenant.superadmin_api import get_abuse_signals

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["t-001"])
        mock_tenant_repo.read = AsyncMock(return_value={
            "tier": "starter",
            "abuse_flagged": False,
        })

        # 250 conversations in 24h exceeds 2x threshold (200) → "high" severity → risk_score=25
        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=[
            {"status": "resolved"} for _ in range(250)
        ])

        mock_ctx = MagicMock()

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._conv_repo", mock_conv_repo),
        ):
            resp = await get_abuse_signals(ctx=mock_ctx)

        assert resp.total_tenants_scanned == 1
        assert len(resp.high_risk_tenants) == 1
        assert resp.high_risk_tenants[0].risk_score >= 25
        assert resp.signals_by_type.get("rate_anomaly", 0) == 1


class TestAbuseFlagEndpoint:
    """Tests for POST /api/superadmin/abuse/tenant/{id}/flag."""

    @pytest.mark.asyncio
    async def test_flag_tenant(self):
        from src.multi_tenant.superadmin_api import FlagTenantRequest, toggle_abuse_flag

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.patch = AsyncMock()

        mock_audit_repo = MagicMock()
        mock_audit_repo.log_event = AsyncMock()

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "spa"
        mock_ctx.user_id = "admin@example.com"

        body = FlagTenantRequest(flagged=True)

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", mock_audit_repo),
        ):
            resp = await toggle_abuse_flag("t-001", body, mock_ctx)

        assert resp.tenant_id == "t-001"
        assert resp.flagged is True
        mock_tenant_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_unflag_tenant(self):
        from src.multi_tenant.superadmin_api import FlagTenantRequest, toggle_abuse_flag

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.patch = AsyncMock()

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "spa"
        mock_ctx.user_id = "admin@example.com"

        body = FlagTenantRequest(flagged=False)

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
        ):
            resp = await toggle_abuse_flag("t-001", body, mock_ctx)

        assert resp.flagged is False
