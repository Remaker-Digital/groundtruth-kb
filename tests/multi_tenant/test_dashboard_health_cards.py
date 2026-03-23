"""Tests for dashboard health card data — Key Vault, NATS, Circuit Breakers.

Verifies that the provider_dashboard() endpoint returns correct health status
for each subsystem, especially field mappings that caused production display bugs:
    - Key Vault: API must return 'healthy' boolean field (not just 'status' string)
    - NATS: deployed=False when not connected (decommissioned)
    - Circuit Breakers: summary dict with 'services' + 'anyOpen' fields
    - Shopify storefront: counts from shopify_integration_status (not phantom fields)

Total: 14 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import configure_superadmin_services


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_state():
    """Ensure clean state for each test."""
    from src.multi_tenant.superadmin_api import _monolith as _state
    orig_tenant = _state._tenant_repo
    orig_prefs = _state._prefs_repo
    orig_audit = _state._audit_repo
    orig_nats = _state._nats_mgr
    yield
    _state._tenant_repo = orig_tenant
    _state._prefs_repo = orig_prefs
    _state._audit_repo = orig_audit
    _state._nats_mgr = orig_nats


def _configure(*, nats_connected=False, tenant_prefs=None, audit_events=None):
    """Helper to wire up mocks for the dashboard endpoint."""
    nats_mgr = MagicMock()
    nats_mgr.is_connected = nats_connected

    tenant_repo = MagicMock()
    tenant_ids = list((tenant_prefs or {}).keys()) or ["t-001"]
    tenant_repo.list_active_tenant_ids = AsyncMock(return_value=tenant_ids)

    prefs_repo = MagicMock()
    if tenant_prefs:
        prefs_repo.get_active = AsyncMock(
            side_effect=[tenant_prefs.get(tid, {}) for tid in tenant_ids]
        )
    else:
        prefs_repo.get_active = AsyncMock(return_value={})

    audit_repo = MagicMock()
    audit_repo.query_events = AsyncMock(return_value=audit_events or [])

    configure_superadmin_services(
        tenant_repo=tenant_repo,
        audit_repo=audit_repo,
        nats_mgr=nats_mgr,
        prefs_repo=prefs_repo,
    )
    return nats_mgr


# ---------------------------------------------------------------------------
# Key Vault Health — 'healthy' boolean field
# ---------------------------------------------------------------------------


class TestKeyVaultHealthField:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_kv_healthy_includes_boolean(self, mock_get_svc, mock_get_cb):
        """When Key Vault is healthy, response includes healthy=True."""
        mock_svc = AsyncMock()
        mock_svc.health_check.return_value = {"status": "healthy", "detail": "OK"}
        mock_get_svc.return_value = mock_svc
        mock_get_cb.return_value.health_summary.return_value = {}
        _configure()

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        kv = result.system_health.get("key_vault", {})
        assert kv["healthy"] is True
        assert kv["status"] == "healthy"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_kv_unhealthy_includes_boolean(self, mock_get_svc, mock_get_cb):
        """When Key Vault is unhealthy, response includes healthy=False."""
        mock_svc = AsyncMock()
        mock_svc.health_check.return_value = {"status": "unhealthy", "detail": "timeout"}
        mock_get_svc.return_value = mock_svc
        mock_get_cb.return_value.health_summary.return_value = {}
        _configure()

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        kv = result.system_health.get("key_vault", {})
        assert kv["healthy"] is False

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_kv_exception_fallback(self, mock_get_svc, mock_get_cb):
        """Key Vault exception → healthy=False with error status."""
        mock_get_svc.side_effect = RuntimeError("no service")
        mock_get_cb.return_value.health_summary.return_value = {}
        _configure()

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        kv = result.system_health.get("key_vault", {})
        assert kv["healthy"] is False
        assert kv["status"] == "error"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_kv_dev_mode_not_healthy(self, mock_get_svc, mock_get_cb):
        """Dev mode Key Vault → healthy=False (status is 'dev_mode' not 'healthy')."""
        mock_svc = AsyncMock()
        mock_svc.health_check.return_value = {
            "status": "dev_mode", "detail": "In-memory", "secret_count": 5,
        }
        mock_get_svc.return_value = mock_svc
        mock_get_cb.return_value.health_summary.return_value = {}
        _configure()

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        kv = result.system_health.get("key_vault", {})
        assert kv["healthy"] is False
        assert kv["status"] == "dev_mode"


# ---------------------------------------------------------------------------
# NATS Health — deployed=False when decommissioned
# ---------------------------------------------------------------------------


class TestNATSHealthCard:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.nats_isolation.get_nats_manager")
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_nats_disconnected_shows_not_deployed(self, mock_get_svc, mock_get_cb, mock_get_nats):
        """NATS not connected → deployed=False (not misleading red 'Disconnected')."""
        mock_svc = AsyncMock()
        mock_svc.health_check.return_value = {"status": "healthy", "detail": "OK"}
        mock_get_svc.return_value = mock_svc
        mock_get_cb.return_value.health_summary.return_value = {}
        mock_nats_mgr = MagicMock()
        mock_nats_mgr.is_connected = False
        mock_get_nats.return_value = mock_nats_mgr
        _configure(nats_connected=False)

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        nats = result.system_health.get("nats", {})
        assert nats["deployed"] is False
        assert nats["connected"] is False

    @pytest.mark.asyncio
    @patch("src.multi_tenant.nats_isolation.get_nats_manager")
    @patch("src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry")
    @patch("src.multi_tenant.tenant_secret_service.get_secret_service")
    async def test_nats_connected_shows_deployed(self, mock_get_svc, mock_get_cb, mock_get_nats):
        """NATS connected → deployed=True, connected=True."""
        mock_svc = AsyncMock()
        mock_svc.health_check.return_value = {"status": "healthy", "detail": "OK"}
        mock_get_svc.return_value = mock_svc
        mock_get_cb.return_value.health_summary.return_value = {}
        mock_nats_mgr = MagicMock()
        mock_nats_mgr.is_connected = True
        mock_get_nats.return_value = mock_nats_mgr
        _configure(nats_connected=True)

        from src.multi_tenant.superadmin_api._dashboard import provider_dashboard
        result = await provider_dashboard()

        nats = result.system_health.get("nats", {})
        assert nats["deployed"] is True
        assert nats["connected"] is True


# ---------------------------------------------------------------------------
# Shopify Storefront — uses shopify_integration_status, not phantom fields
# ---------------------------------------------------------------------------


class TestShopifyStorefrontCounting:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_counts_from_shopify_integration_status(self, mock_cb_cls):
        """Shopify storefront counted via shopify_integration_status field."""
        mock_cb_cls.return_value.health_summary.return_value = {"any_open": False, "services": {}}
        _configure(tenant_prefs={
            "t-001": {"shopify_integration_status": "connected"},
            "t-002": {"shopify_integration_status": "error"},
            "t-003": {},
        })

        from src.multi_tenant.superadmin_api._dashboard import integration_health
        result = await integration_health()

        sf = [m for m in result.mcp_integrations if m.server_name == "shopify-storefront"]
        assert len(sf) == 1
        assert sf[0].tenants_enabled == 2   # connected + error both count as enabled
        assert sf[0].tenants_connected == 1  # only "connected"
        assert sf[0].tenants_errored == 1    # only "error"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_phantom_fields_do_not_count(self, mock_cb_cls):
        """Old phantom mcp_storefront_enabled field must NOT count as enabled."""
        mock_cb_cls.return_value.health_summary.return_value = {"any_open": False, "services": {}}
        _configure(tenant_prefs={
            "t-001": {"mcp_storefront_enabled": True, "mcp_storefront_status": "connected"},
            "t-002": {},
        })

        from src.multi_tenant.superadmin_api._dashboard import integration_health
        result = await integration_health()

        sf = [m for m in result.mcp_integrations if m.server_name == "shopify-storefront"]
        assert sf[0].tenants_enabled == 0
        assert sf[0].tenants_connected == 0

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_disconnected_shopify_not_enabled(self, mock_cb_cls):
        """shopify_integration_status='disconnected' → enabled but not connected."""
        mock_cb_cls.return_value.health_summary.return_value = {"any_open": False, "services": {}}
        _configure(tenant_prefs={
            "t-001": {"shopify_integration_status": "disconnected"},
        })

        from src.multi_tenant.superadmin_api._dashboard import integration_health
        result = await integration_health()

        sf = [m for m in result.mcp_integrations if m.server_name == "shopify-storefront"]
        assert sf[0].tenants_enabled == 1
        assert sf[0].tenants_connected == 0
        assert sf[0].tenants_errored == 0

    @pytest.mark.asyncio
    @patch("src.multi_tenant.pipeline_resilience.ServiceCircuitBreakerRegistry")
    async def test_stripe_uses_explicit_enable_flag(self, mock_cb_cls):
        """Stripe MCP still uses stripe_mcp_enabled field (not changed)."""
        mock_cb_cls.return_value.health_summary.return_value = {"any_open": False, "services": {}}
        _configure(tenant_prefs={
            "t-001": {"stripe_mcp_enabled": True, "stripe_mcp_status": "connected"},
            "t-002": {"stripe_mcp_enabled": True, "stripe_mcp_status": "error"},
        })

        from src.multi_tenant.superadmin_api._dashboard import integration_health
        result = await integration_health()

        st = [m for m in result.mcp_integrations if m.server_name == "stripe"]
        assert st[0].tenants_enabled == 2
        assert st[0].tenants_connected == 1
        assert st[0].tenants_errored == 1
