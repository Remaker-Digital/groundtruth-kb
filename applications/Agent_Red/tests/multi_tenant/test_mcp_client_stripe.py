"""Tests for Stripe MCP client extensions — Phase 3B additions to mcp_client.py.

Test IDs: MCPS-01 → MCPS-12

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock


from src.multi_tenant.mcp_client import (
    McpServerConfig,
    build_stripe_mcp_config,
    parse_mcp_server_config,
    resolve_mcp_configs,
)


# ---------------------------------------------------------------------------
# MCPS-01→MCPS-03: build_stripe_mcp_config
# ---------------------------------------------------------------------------

class TestBuildStripeMcpConfig:
    """Test Stripe MCP config builder."""

    def test_mcps_01_stripe_config_fields(self):
        """MCPS-01: build_stripe_mcp_config returns correct structure."""
        config = build_stripe_mcp_config()

        assert config["server_name"] == "stripe"
        assert config["server_url"] == "https://mcp.stripe.com"
        assert config["server_type"] == "stripe"
        assert config["enabled"] is True
        assert config["read_only"] is True
        assert config["timeout_ms"] == 5_000
        assert config["credential_ref"] == "stripe-api-key"

    def test_mcps_02_stripe_config_parseable(self):
        """MCPS-02: Stripe config dict parses to valid McpServerConfig."""
        raw = build_stripe_mcp_config()
        config = parse_mcp_server_config(raw)

        assert config is not None
        assert config.server_name == "stripe"
        assert config.server_type == "stripe"
        assert config.credential_ref == "stripe-api-key"
        assert config.read_only is True

    def test_mcps_03_stripe_locked_read_only(self):
        """MCPS-03: Stripe config enforces read_only=True (Cycle 5)."""
        config = build_stripe_mcp_config()
        assert config["read_only"] is True


# ---------------------------------------------------------------------------
# MCPS-04→MCPS-05: McpServerConfig credential_ref
# ---------------------------------------------------------------------------

class TestCredentialRef:
    """Test credential_ref field on McpServerConfig."""

    def test_mcps_04_credential_ref_default_none(self):
        """MCPS-04: Default credential_ref is None (no auth)."""
        config = McpServerConfig(
            server_name="test", server_url="https://test.com",
        )
        assert config.credential_ref is None

    def test_mcps_05_credential_ref_set(self):
        """MCPS-05: credential_ref is set from raw config."""
        raw = {
            "server_name": "stripe",
            "server_url": "https://mcp.stripe.com",
            "server_type": "stripe",
            "credential_ref": "stripe-api-key",
        }
        config = parse_mcp_server_config(raw)
        assert config is not None
        assert config.credential_ref == "stripe-api-key"


# ---------------------------------------------------------------------------
# MCPS-06→MCPS-10: resolve_mcp_configs with Stripe
# ---------------------------------------------------------------------------

class TestResolveMcpConfigsStripe:
    """Test resolve_mcp_configs with Stripe auto-populate."""

    def test_mcps_06_stripe_auto_populate(self):
        """MCPS-06: Stripe MCP auto-populates when connected + enabled."""
        prefs = MagicMock()
        prefs.mcp_enabled = False
        prefs.mcp_servers = []
        prefs.shopify_integration_status = None
        prefs.stripe_mcp_status = "connected"
        prefs.stripe_mcp_enabled = True

        tenant = MagicMock()
        tenant.shopify_shop_domain = None

        configs = resolve_mcp_configs(prefs, tenant)

        assert len(configs) == 1
        assert configs[0].server_name == "stripe"
        assert configs[0].server_type == "stripe"
        assert configs[0].credential_ref == "stripe-api-key"

    def test_mcps_07_stripe_not_connected(self):
        """MCPS-07: Stripe does NOT auto-populate when status != 'connected'."""
        prefs = MagicMock()
        prefs.mcp_enabled = False
        prefs.mcp_servers = []
        prefs.shopify_integration_status = None
        prefs.stripe_mcp_status = "disconnected"
        prefs.stripe_mcp_enabled = True

        tenant = MagicMock()
        tenant.shopify_shop_domain = None

        configs = resolve_mcp_configs(prefs, tenant)
        assert len(configs) == 0

    def test_mcps_08_stripe_not_enabled(self):
        """MCPS-08: Stripe does NOT auto-populate when stripe_mcp_enabled=False."""
        prefs = MagicMock()
        prefs.mcp_enabled = False
        prefs.mcp_servers = []
        prefs.shopify_integration_status = None
        prefs.stripe_mcp_status = "connected"
        prefs.stripe_mcp_enabled = False

        tenant = MagicMock()
        tenant.shopify_shop_domain = None

        configs = resolve_mcp_configs(prefs, tenant)
        assert len(configs) == 0

    def test_mcps_09_shopify_and_stripe_both(self):
        """MCPS-09: Both Shopify and Stripe auto-populate simultaneously."""
        prefs = MagicMock()
        prefs.mcp_enabled = False
        prefs.mcp_servers = []
        prefs.shopify_integration_status = "connected"
        prefs.stripe_mcp_status = "connected"
        prefs.stripe_mcp_enabled = True

        tenant = MagicMock()
        tenant.shopify_shop_domain = "mystore.myshopify.com"

        configs = resolve_mcp_configs(prefs, tenant)

        assert len(configs) == 2
        server_names = {c.server_name for c in configs}
        assert "shopify-storefront" in server_names
        assert "stripe" in server_names

    def test_mcps_10_explicit_config_overrides(self):
        """MCPS-10: Explicit mcp_servers with mcp_enabled=True takes priority."""
        prefs = MagicMock()
        prefs.mcp_enabled = True
        prefs.mcp_servers = [
            {
                "server_name": "custom-stripe",
                "server_url": "https://custom.stripe.com",
                "server_type": "stripe",
                "enabled": True,
            }
        ]
        prefs.shopify_integration_status = "connected"
        prefs.stripe_mcp_status = "connected"
        prefs.stripe_mcp_enabled = True

        tenant = MagicMock()
        tenant.shopify_shop_domain = "mystore.myshopify.com"

        configs = resolve_mcp_configs(prefs, tenant)

        # Path 1 takes priority — only explicit configs
        assert len(configs) == 1
        assert configs[0].server_name == "custom-stripe"


# ---------------------------------------------------------------------------
# MCPS-11→MCPS-12: Circuit breaker config
# ---------------------------------------------------------------------------

class TestStripeMcpCircuitBreaker:
    """Test mcp-stripe circuit breaker configuration."""

    def test_mcps_11_stripe_breaker_in_configs(self):
        """MCPS-11: 'mcp-stripe' circuit breaker is configured."""
        from src.multi_tenant.pipeline_resilience import CIRCUIT_BREAKER_CONFIGS

        assert "mcp-stripe" in CIRCUIT_BREAKER_CONFIGS
        config = CIRCUIT_BREAKER_CONFIGS["mcp-stripe"]
        assert config["failure_threshold"] == 3
        assert config["window_seconds"] == 30
        assert config["recovery_seconds"] == 15

    def test_mcps_12_stripe_breaker_via_registry(self):
        """MCPS-12: mcp-stripe breaker resolves from global registry."""
        from src.multi_tenant.pipeline_resilience import get_circuit_breaker

        breaker = get_circuit_breaker("mcp-stripe")
        assert breaker is not None
        assert breaker.service_name == "mcp-stripe"
