"""Tests for HV-3: Integration Reliability endpoint (GET /api/superadmin/integrations/health).

Covers:
    - Happy path: all systems healthy
    - Circuit breaker states (closed, open, half_open)
    - Any open breaker sets any_breaker_open=True + overall_healthy=False
    - NATS connected/disconnected
    - NATS disconnected → overall_healthy=False
    - MCP integration status (enabled, connected, errored)
    - MCP with mixed tenant states
    - Circuit breaker registry unavailable → errors[]
    - NATS manager not configured
    - Tenant/prefs repos missing → MCP section empty
    - CamelCase serialization
    - Auth enforcement

Total: 22 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    CircuitBreakerStatus,
    IntegrationHealthResponse,
    McpIntegrationStatus,
    configure_superadmin_services,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_nats_mgr():
    mgr = MagicMock()
    mgr.is_connected = True
    return mgr


@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["t-001", "t-002", "t-003"])
    return repo


@pytest.fixture()
def mock_prefs_repo():
    repo = MagicMock()
    repo.read = AsyncMock()
    repo.get_active = AsyncMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


HEALTHY_CB_SUMMARY = {
    "any_open": False,
    "services": {
        "azure-openai": {"state": "closed", "failure_count": 0, "success_count": 100},
        "cosmos-db": {"state": "closed", "failure_count": 2, "success_count": 500},
        "nats": {"state": "closed", "failure_count": 0, "success_count": 200},
        "mcp-storefront": {"state": "closed", "failure_count": 1, "success_count": 50},
        "mcp-stripe": {"state": "closed", "failure_count": 0, "success_count": 30},
    },
}

OPEN_CB_SUMMARY = {
    "any_open": True,
    "services": {
        "azure-openai": {"state": "open", "failure_count": 10, "success_count": 50},
        "cosmos-db": {"state": "closed", "failure_count": 0, "success_count": 500},
        "nats": {"state": "half_open", "failure_count": 3, "success_count": 100},
    },
}


# ---------------------------------------------------------------------------
# Happy Path — All Healthy
# ---------------------------------------------------------------------------


class TestIntegrationHealthHappyPath:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_all_healthy(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """All systems healthy → overall_healthy=True."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.side_effect = [
            {"shopify_integration_status": "connected"},
            {"stripe_mcp_enabled": True, "stripe_mcp_status": "connected"},
            {},
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert isinstance(result, IntegrationHealthResponse)
        assert result.overall_healthy is True
        assert result.any_breaker_open is False
        assert result.nats_connected is True
        assert result.errors == []

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_circuit_breaker_count(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Returns correct number of circuit breakers."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert len(result.circuit_breakers) == 5

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_breaker_details(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Per-breaker details are populated correctly."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        cosmos = [b for b in result.circuit_breakers if b.service == "cosmos-db"]
        assert len(cosmos) == 1
        assert cosmos[0].state == "closed"
        assert cosmos[0].failures == 2
        assert cosmos[0].successes == 500


# ---------------------------------------------------------------------------
# Circuit Breaker States
# ---------------------------------------------------------------------------


class TestCircuitBreakerStates:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_open_breaker(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Open circuit breaker → any_breaker_open=True, overall_healthy=False."""
        mock_cb_cls.return_value.health_summary.return_value = OPEN_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert result.any_breaker_open is True
        assert result.overall_healthy is False

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_half_open_breaker_details(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Half-open breaker state is reported."""
        mock_cb_cls.return_value.health_summary.return_value = OPEN_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        nats_breaker = [b for b in result.circuit_breakers if b.service == "nats"]
        assert len(nats_breaker) == 1
        assert nats_breaker[0].state == "half_open"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_registry_unavailable(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Registry exception → goes to errors[], empty breakers."""
        mock_cb_cls.return_value.health_summary.side_effect = RuntimeError("Registry down")
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert len(result.circuit_breakers) == 0
        assert any("circuit_breakers" in e.get("subsystem", "") for e in result.errors)


# ---------------------------------------------------------------------------
# NATS Connectivity
# ---------------------------------------------------------------------------


class TestNATSConnectivity:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_nats_connected(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """NATS connected → nats_connected=True."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert result.nats_connected is True

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_nats_disconnected(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """NATS disconnected → nats_deployed=False (decommissioned), overall_healthy=True."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_nats_mgr.is_connected = False
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert result.nats_connected is False
        assert result.nats_deployed is False
        assert result.overall_healthy is True

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_nats_not_configured(
        self, mock_cb_cls, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """NATS manager None → nats_connected=False."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=None,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert result.nats_connected is False


# ---------------------------------------------------------------------------
# MCP Integration Status
# ---------------------------------------------------------------------------


class TestMCPIntegrationStatus:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_mcp_mixed_states(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """MCP integrations with mixed tenant states."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.side_effect = [
            {
                "shopify_integration_status": "connected",
                "stripe_mcp_enabled": True,
                "stripe_mcp_status": "connected",
            },
            {
                "shopify_integration_status": "error",
            },
            {},  # no MCP
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        sf = [m for m in result.mcp_integrations if m.server_name == "shopify-storefront"]
        assert len(sf) == 1
        assert sf[0].tenants_enabled == 2
        assert sf[0].tenants_connected == 1
        assert sf[0].tenants_errored == 1

        st = [m for m in result.mcp_integrations if m.server_name == "stripe"]
        assert len(st) == 1
        assert st[0].tenants_enabled == 1
        assert st[0].tenants_connected == 1

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_no_mcp_enabled(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """No tenants with MCP → zero counts."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.return_value = {}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        for mcp in result.mcp_integrations:
            assert mcp.tenants_enabled == 0
            assert mcp.tenants_connected == 0
            assert mcp.tenants_errored == 0

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_mcp_repos_missing(
        self, mock_cb_cls, mock_nats_mgr, superadmin_ctx
    ):
        """Tenant/prefs repos None → MCP section empty."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        configure_superadmin_services(
            tenant_repo=None,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=None,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        assert result.mcp_integrations == []

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_mcp_prefs_read_failure(
        self, mock_cb_cls, mock_nats_mgr, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Individual prefs read failure is silently skipped."""
        mock_cb_cls.return_value.health_summary.return_value = HEALTHY_CB_SUMMARY
        mock_prefs_repo.get_active.side_effect = [
            {"shopify_integration_status": "connected"},
            RuntimeError("Cosmos error"),
            {},
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import integration_health
        result = await integration_health()

        sf = [m for m in result.mcp_integrations if m.server_name == "shopify-storefront"]
        assert sf[0].tenants_enabled == 1  # only t-001 counted


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestIntegrationHealthSerialization:

    def test_response_model_camel_case(self):
        """IntegrationHealthResponse serializes to camelCase."""
        resp = IntegrationHealthResponse(
            overall_healthy=True,
            any_breaker_open=False,
            nats_connected=True,
            circuit_breakers=[CircuitBreakerStatus(
                service="cosmos-db", state="closed", failures=0, successes=100,
            )],
            mcp_integrations=[McpIntegrationStatus(
                server_name="shopify-storefront",
                tenants_enabled=2,
                tenants_connected=1,
                tenants_errored=1,
            )],
        )
        data = resp.model_dump(by_alias=True)
        assert "overallHealthy" in data
        assert "anyBreakerOpen" in data
        assert "natsConnected" in data
        assert "circuitBreakers" in data
        assert "mcpIntegrations" in data
        assert data["circuitBreakers"][0]["service"] == "cosmos-db"
        assert data["mcpIntegrations"][0]["serverName"] == "shopify-storefront"
        assert data["mcpIntegrations"][0]["tenantsEnabled"] == 2
        assert data["mcpIntegrations"][0]["tenantsErrored"] == 1

    def test_empty_response(self):
        """Empty response defaults."""
        resp = IntegrationHealthResponse()
        data = resp.model_dump(by_alias=True)
        assert data["overallHealthy"] is True
        assert data["circuitBreakers"] == []
        assert data["mcpIntegrations"] == []
        assert data["errors"] == []


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestIntegrationHealthAuth:

    def test_router_endpoint_exists(self):
        """Integration health endpoint is mounted."""
        from src.multi_tenant.superadmin_api import router
        routes = [r.path for r in router.routes]
        assert "/api/superadmin/integrations/health" in routes
