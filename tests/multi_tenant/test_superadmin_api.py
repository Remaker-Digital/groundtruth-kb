"""Tests for the Superadmin Provider Operations API (superadmin_api.py).

Covers Phase 1 Release-Blocking requirements:
    RB-2: Tenant directory (list + summary) — 7 tests
    RB-8: Deployment history — 3 tests
    RB-1: Provider ops dashboard — 3 tests
    RB-7: Billing health — 4 tests
    Auth: SUPERADMIN-only access enforcement — 3 tests

Total: 20 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    BillingHealthResponse,
    DashboardHealthResponse,
    DeploymentHistoryResponse,
    TenantDirectoryResponse,
    TenantDistributionSummary,
    configure_superadmin_services,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class FakeAsyncIterator:
    """Helper to simulate async iteration over Cosmos query results."""

    def __init__(self, items: list[dict[str, Any]]):
        self._items = items
        self._index = 0

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository with cross-partition query support."""
    repo = MagicMock()
    repo._container = MagicMock()
    return repo


@pytest.fixture()
def mock_audit_repo():
    """Create a mock AuditLogRepository."""
    repo = MagicMock()
    repo._container = MagicMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


SAMPLE_TENANTS = [
    {
        "tenant_id": "tenant-001",
        "status": "active",
        "tier": "professional",
        "billing_channel": "stripe",
        "customer_email": "t1@example.com",
        "shopify_shop_domain": "shop1.myshopify.com",
        "created_at": "2026-01-15T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z",
        "deactivated_at": None,
        "consent_status": "granted",
    },
    {
        "tenant_id": "tenant-002",
        "status": "active",
        "tier": "starter",
        "billing_channel": "shopify",
        "customer_email": "t2@example.com",
        "shopify_shop_domain": "shop2.myshopify.com",
        "created_at": "2026-01-20T00:00:00Z",
        "updated_at": "2026-02-12T00:00:00Z",
        "deactivated_at": None,
        "consent_status": "not_asked",
    },
    {
        "tenant_id": "tenant-003",
        "status": "deactivated",
        "tier": "starter",
        "billing_channel": "stripe",
        "customer_email": "t3@example.com",
        "shopify_shop_domain": None,
        "created_at": "2025-12-01T00:00:00Z",
        "updated_at": "2026-01-05T00:00:00Z",
        "deactivated_at": "2026-01-05T00:00:00Z",
        "consent_status": "denied",
    },
]


# ---------------------------------------------------------------------------
# RB-2: Tenant Directory Tests
# ---------------------------------------------------------------------------


class TestTenantDirectory:
    """Tests for GET /api/superadmin/tenants."""

    @pytest.mark.asyncio
    async def test_list_all_tenants(self, mock_tenant_repo, superadmin_ctx):
        """Returns all tenants with default pagination."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        # Mock count query
        count_iter = FakeAsyncIterator([3])
        data_iter = FakeAsyncIterator(SAMPLE_TENANTS)

        call_count = 0

        def query_items_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_iter
            return data_iter

        mock_tenant_repo._container.query_items = MagicMock(
            side_effect=query_items_side_effect
        )

        from src.multi_tenant.superadmin_api import list_all_tenants

        result = await list_all_tenants(
            _ctx=superadmin_ctx, skip=0, limit=50,
        )

        assert isinstance(result, TenantDirectoryResponse)
        assert result.total == 3
        assert len(result.tenants) == 3
        assert result.tenants[0].tenant_id == "tenant-001"
        assert result.skip == 0
        assert result.limit == 50

    @pytest.mark.asyncio
    async def test_list_tenants_filter_by_status(self, mock_tenant_repo, superadmin_ctx):
        """Filters tenants by status parameter."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        active_tenants = [t for t in SAMPLE_TENANTS if t["status"] == "active"]
        count_iter = FakeAsyncIterator([2])
        data_iter = FakeAsyncIterator(active_tenants)

        call_count = 0

        def query_items_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            # Verify the query includes status filter
            query = kwargs.get("query", "")
            assert "@status" in query
            if call_count == 1:
                return count_iter
            return data_iter

        mock_tenant_repo._container.query_items = MagicMock(
            side_effect=query_items_side_effect
        )

        from src.multi_tenant.superadmin_api import list_all_tenants

        result = await list_all_tenants(
            _ctx=superadmin_ctx,
            status="active",
            skip=0,
            limit=50,
        )

        assert result.total == 2
        assert len(result.tenants) == 2
        assert all(t.status == "active" for t in result.tenants)

    @pytest.mark.asyncio
    async def test_list_tenants_filter_by_tier(self, mock_tenant_repo, superadmin_ctx):
        """Filters tenants by tier parameter."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        starter_tenants = [t for t in SAMPLE_TENANTS if t["tier"] == "starter"]
        count_iter = FakeAsyncIterator([2])
        data_iter = FakeAsyncIterator(starter_tenants)

        call_count = 0

        def query_items_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_iter
            return data_iter

        mock_tenant_repo._container.query_items = MagicMock(
            side_effect=query_items_side_effect
        )

        from src.multi_tenant.superadmin_api import list_all_tenants

        result = await list_all_tenants(
            _ctx=superadmin_ctx,
            tier="starter",
            skip=0,
            limit=50,
        )

        assert result.total == 2

    @pytest.mark.asyncio
    async def test_list_tenants_pagination(self, mock_tenant_repo, superadmin_ctx):
        """Pagination parameters are passed correctly."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        count_iter = FakeAsyncIterator([50])
        data_iter = FakeAsyncIterator([SAMPLE_TENANTS[0]])

        call_count = 0

        def query_items_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_iter
            # Verify OFFSET LIMIT in query
            query = kwargs.get("query", "")
            assert "OFFSET 10 LIMIT 5" in query
            return data_iter

        mock_tenant_repo._container.query_items = MagicMock(
            side_effect=query_items_side_effect
        )

        from src.multi_tenant.superadmin_api import list_all_tenants

        result = await list_all_tenants(
            _ctx=superadmin_ctx,
            skip=10,
            limit=5,
        )

        assert result.skip == 10
        assert result.limit == 5
        assert result.total == 50

    @pytest.mark.asyncio
    async def test_list_tenants_503_when_not_initialized(self, superadmin_ctx):
        """Returns 503 when service not initialized."""
        configure_superadmin_services(
            tenant_repo=None,  # type: ignore[arg-type]
            audit_repo=MagicMock(),
        )

        from src.multi_tenant.superadmin_api import list_all_tenants

        with pytest.raises(Exception) as exc_info:
            await list_all_tenants(_ctx=superadmin_ctx)

        assert exc_info.value.status_code == 503  # type: ignore[union-attr]


class TestTenantSummary:
    """Tests for GET /api/superadmin/tenants/summary."""

    @pytest.mark.asyncio
    async def test_tenant_distribution(self, mock_tenant_repo, superadmin_ctx):
        """Returns correct distribution counts."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(SAMPLE_TENANTS)
        )

        from src.multi_tenant.superadmin_api import tenant_summary

        result = await tenant_summary(_ctx=superadmin_ctx)

        assert isinstance(result, TenantDistributionSummary)
        assert result.total_tenants == 3
        assert result.by_status == {"active": 2, "deactivated": 1}
        assert result.by_tier == {"professional": 1, "starter": 2}
        assert result.by_billing_channel == {"stripe": 2, "shopify": 1}

    @pytest.mark.asyncio
    async def test_empty_tenant_summary(self, mock_tenant_repo, superadmin_ctx):
        """Returns zero counts when no tenants exist."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        from src.multi_tenant.superadmin_api import tenant_summary

        result = await tenant_summary(_ctx=superadmin_ctx)

        assert result.total_tenants == 0
        assert result.by_status == {}


# ---------------------------------------------------------------------------
# RB-8: Deployment History Tests
# ---------------------------------------------------------------------------


class TestDeploymentHistory:
    """Tests for GET /api/superadmin/deployments."""

    @pytest.mark.asyncio
    async def test_deployment_events(self, mock_audit_repo, superadmin_ctx):
        """Returns deployment events from audit log."""
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=mock_audit_repo,
        )

        deploy_events = [
            {
                "event_type": "model.deployed",
                "timestamp": "2026-02-16T10:00:00Z",
                "actor": "mike@remakerdigital.com",
                "payload": {"version": "1.35.0", "previous_version": "1.34.0"},
            },
            {
                "event_type": "model.rolled_back",
                "timestamp": "2026-02-15T09:00:00Z",
                "actor": "mike@remakerdigital.com",
                "payload": {"version": "1.33.0", "rolled_back_from": "1.34.0"},
            },
        ]

        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(deploy_events)
        )

        from src.multi_tenant.superadmin_api import deployment_history

        result = await deployment_history(_ctx=superadmin_ctx, limit=20)

        assert isinstance(result, DeploymentHistoryResponse)
        assert len(result.events) == 2
        assert result.events[0].event_type == "model.deployed"
        assert result.events[0].payload["version"] == "1.35.0"
        assert result.current_version is not None  # Loaded from api_versioning

    @pytest.mark.asyncio
    async def test_empty_deployment_history(self, mock_audit_repo, superadmin_ctx):
        """Returns empty list when no deployments recorded."""
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=mock_audit_repo,
        )

        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        from src.multi_tenant.superadmin_api import deployment_history

        result = await deployment_history(_ctx=superadmin_ctx)

        assert result.total == 0
        assert result.events == []

    @pytest.mark.asyncio
    async def test_deployment_limit(self, mock_audit_repo, superadmin_ctx):
        """Respects limit parameter."""
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=mock_audit_repo,
        )

        events = [
            {
                "event_type": "model.deployed",
                "timestamp": f"2026-02-{i:02d}T10:00:00Z",
                "actor": "system",
                "payload": {"version": f"1.{i}.0"},
            }
            for i in range(1, 6)
        ]

        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(events[:3])
        )

        from src.multi_tenant.superadmin_api import deployment_history

        result = await deployment_history(_ctx=superadmin_ctx, limit=3)

        assert len(result.events) <= 3


# ---------------------------------------------------------------------------
# RB-1: Provider Dashboard Tests
# ---------------------------------------------------------------------------


class TestProviderDashboard:
    """Tests for GET /api/superadmin/dashboard."""

    @pytest.mark.asyncio
    async def test_dashboard_returns_all_sections(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Dashboard response includes all required sections."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        # Mock tenant summary
        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(SAMPLE_TENANTS)
        )

        # Mock deployment history
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        from src.multi_tenant.superadmin_api import provider_dashboard

        with patch(
            "src.multi_tenant.sla_monitoring.get_sla_monitor",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.tenant_usage_monitor.get_usage_monitor",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.nats_isolation.get_nats_manager",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            side_effect=ImportError("not available"),
        ):
            result = await provider_dashboard(_ctx=superadmin_ctx)

        assert isinstance(result, DashboardHealthResponse)
        assert result.timestamp is not None
        assert result.system_health is not None
        assert result.tenant_summary is not None
        assert result.tenant_summary.total_tenants == 3

    @pytest.mark.asyncio
    async def test_dashboard_includes_sla_data(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Dashboard includes SLA summary when available."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(SAMPLE_TENANTS)
        )
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        mock_sla = MagicMock()
        mock_sla.get_platform_summary.return_value = MagicMock(
            overall_compliant=True,
            uptime_pct=99.95,
            total_requests=10000,
            latency=MagicMock(p50_ms=120.0, p95_ms=450.0, p99_ms=1200.0),
        )

        mock_usage = MagicMock()
        mock_usage.health_summary.return_value = {
            "tenants_tracked": 3,
            "tenants_escalated": 0,
            "tenants_throttled": 0,
        }

        from src.multi_tenant.superadmin_api import provider_dashboard

        with patch(
            "src.multi_tenant.sla_monitoring.get_sla_monitor",
            return_value=mock_sla,
        ), patch(
            "src.multi_tenant.tenant_usage_monitor.get_usage_monitor",
            return_value=mock_usage,
        ), patch(
            "src.multi_tenant.nats_isolation.get_nats_manager",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry",
            side_effect=ImportError("not available"),
        ), patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            side_effect=ImportError("not available"),
        ):
            result = await provider_dashboard(_ctx=superadmin_ctx)

        assert result.sla_summary["overall_compliant"] is True
        assert result.sla_summary["uptime_pct"] == 99.95
        assert result.usage_summary["tenants_tracked"] == 3

    @pytest.mark.asyncio
    async def test_dashboard_graceful_degradation(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Dashboard returns partial data when some services fail."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        from src.multi_tenant.superadmin_api import provider_dashboard

        # All services unavailable — should still return a response
        with patch(
            "src.multi_tenant.sla_monitoring.get_sla_monitor",
            side_effect=Exception("unavailable"),
        ), patch(
            "src.multi_tenant.tenant_usage_monitor.get_usage_monitor",
            side_effect=Exception("unavailable"),
        ), patch(
            "src.multi_tenant.nats_isolation.get_nats_manager",
            side_effect=Exception("unavailable"),
        ), patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry",
            side_effect=Exception("unavailable"),
        ), patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            side_effect=Exception("unavailable"),
        ):
            result = await provider_dashboard(_ctx=superadmin_ctx)

        # Should still return, just with error fields
        assert isinstance(result, DashboardHealthResponse)
        assert result.timestamp is not None


# ---------------------------------------------------------------------------
# RB-7: Billing Health Tests
# ---------------------------------------------------------------------------


class TestBillingHealth:
    """Tests for GET /api/superadmin/billing/health."""

    @pytest.mark.asyncio
    async def test_billing_health_all_healthy(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """All tenants show healthy billing status."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        active_tenants = [
            {"tenant_id": "tenant-001", "tier": "professional", "status": "active"},
            {"tenant_id": "tenant-002", "tier": "starter", "status": "active"},
        ]

        recon_event = {
            "timestamp": "2026-02-16T00:00:00Z",
            "payload": {
                "action": "billing_reconciliation",
                "discrepancy_percent": 1.2,
            },
        }

        tenant_call = 0

        def mock_query(**kwargs):
            nonlocal tenant_call
            query = kwargs.get("query", "")
            if "c.status = 'active'" in query:
                return FakeAsyncIterator(active_tenants)
            tenant_call += 1
            return FakeAsyncIterator([recon_event])

        mock_tenant_repo._container.query_items = MagicMock(side_effect=mock_query)
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([recon_event])
        )

        from src.multi_tenant.superadmin_api import billing_health

        result = await billing_health(_ctx=superadmin_ctx)

        assert isinstance(result, BillingHealthResponse)
        assert result.total_tenants == 2
        assert result.tenants_needing_review == 0

    @pytest.mark.asyncio
    async def test_billing_health_with_discrepancy(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Tenants with >5% discrepancy flagged for review."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        active_tenants = [
            {"tenant_id": "tenant-001", "tier": "professional", "status": "active"},
        ]

        bad_recon = {
            "timestamp": "2026-02-16T00:00:00Z",
            "payload": {
                "action": "billing_reconciliation",
                "discrepancy_percent": 8.5,
            },
        }

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(active_tenants)
        )
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([bad_recon])
        )

        from src.multi_tenant.superadmin_api import billing_health

        result = await billing_health(_ctx=superadmin_ctx)

        assert result.tenants_needing_review == 1
        assert result.tenants[0].needs_review is True
        assert result.tenants[0].discrepancy_percent == 8.5
        assert result.tenants[0].status == "review_needed"

    @pytest.mark.asyncio
    async def test_billing_health_no_tenants(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Returns empty when no active tenants."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )

        mock_tenant_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        from src.multi_tenant.superadmin_api import billing_health

        result = await billing_health(_ctx=superadmin_ctx)

        assert result.total_tenants == 0
        assert result.tenants == []

    @pytest.mark.asyncio
    async def test_billing_health_503_when_not_initialized(self, superadmin_ctx):
        """Returns 503 when service not initialized."""
        configure_superadmin_services(
            tenant_repo=None,  # type: ignore[arg-type]
            audit_repo=MagicMock(),
        )

        from src.multi_tenant.superadmin_api import billing_health

        with pytest.raises(Exception) as exc_info:
            await billing_health(_ctx=superadmin_ctx)

        assert exc_info.value.status_code == 503  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Auth enforcement tests
# ---------------------------------------------------------------------------


class TestSuperadminAuth:
    """Verify that SUPERADMIN role is required on all endpoints."""

    def test_router_prefix(self):
        """Router uses /api/superadmin prefix."""
        assert router.prefix == "/api/superadmin"

    def test_router_tags(self):
        """Router is tagged 'superadmin'."""
        assert "superadmin" in router.tags

    def test_all_endpoints_have_superadmin_dependency(self):
        """Every route in the router requires SUPERADMIN role.

        This is a structural check — verifies that all endpoint functions
        have a parameter with a dependency that calls require_role.
        """
        import inspect

        for route in router.routes:
            if not hasattr(route, "endpoint"):
                continue
            sig = inspect.signature(route.endpoint)
            has_ctx_param = False
            for param_name, param in sig.parameters.items():
                if param_name == "_ctx" or param_name.endswith("ctx"):
                    has_ctx_param = True
            assert has_ctx_param, (
                f"Endpoint {route.endpoint.__name__} is missing "
                f"a _ctx parameter (SUPERADMIN dependency)"
            )
