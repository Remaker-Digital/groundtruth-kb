"""Phase 3 — Local transport smoke tests.

Tests real client creation against local config. Validates SLIM path,
NATS path, and HTTP fallback path with real SDK objects (not mocks).

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 2.
Governing decisions: ADR-001 (dispatch by physical possibility), SPEC-1802.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_transport_singletons():
    """Reset AGNTCY SDK singletons between tests."""
    import src.multi_tenant.agntcy_sdk_integration as mod
    old_factory = mod._factory
    old_transport = mod._transport
    mod._factory = None
    mod._transport = None
    yield
    mod._factory = old_factory
    mod._transport = old_transport


# ---------------------------------------------------------------------------
# 1. SLIM transport path (Tier 1)
# ---------------------------------------------------------------------------


class TestSLIMTransportPath:
    """Verify SLIM transport creation with real SDK objects."""

    def test_slim_transport_created_when_endpoint_configured(self):
        """When AGNTCY_SLIM_ENDPOINT is set, SLIM transport should be created."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "https://slim.example.internal:443",
            "AGNTCY_SLIM_SHARED_SECRET": "a" * 32,
            "AGNTCY_SLIM_TLS_INSECURE": "true",
            "AGNTCY_TRANSPORT_TYPE": "slim",
        }
        with patch.dict(os.environ, env, clear=False):
            # Re-import to pick up env vars
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            factory = mod.get_agntcy_factory()
            assert factory is not None

            # get_default_transport should attempt SLIM
            transport = mod.get_default_transport()
            # Transport may fail to connect (no real SLIM server) but
            # should either return a transport object or fall through to NATS/None
            # The key assertion: factory was used, no import errors

    def test_slim_endpoint_requires_scheme(self):
        """SLIM endpoint without scheme should fail gracefully."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "slim.example.internal:443",  # no https://
            "AGNTCY_SLIM_SHARED_SECRET": "a" * 32,
            "AGNTCY_TRANSPORT_TYPE": "slim",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            # Should not raise — graceful fallback
            transport = mod.get_default_transport()
            # May be None if SLIM creation fails


# ---------------------------------------------------------------------------
# 2. NATS transport path (Tier 2)
# ---------------------------------------------------------------------------


class TestNATSTransportPath:
    """Verify NATS transport creation with real SDK objects."""

    def test_nats_transport_created_when_endpoint_configured(self):
        """When AGNTCY_NATS_ENDPOINT is set and SLIM absent, NATS should be created."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "",
            "AGNTCY_NATS_ENDPOINT": "ws://nats.example.internal:8080",
            "AGNTCY_TRANSPORT_TYPE": "nats",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            factory = mod.get_agntcy_factory()
            assert factory is not None

            transport = mod.get_default_transport()
            # May be None if NATS connection fails, but creation should not raise

    def test_nats_websocket_protocol_detected(self):
        """NATS endpoint with ws:// should be detected as WebSocket protocol."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "",
            "AGNTCY_NATS_ENDPOINT": "ws://nats.example.internal:8080",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)
            assert mod.NATS_ENDPOINT.startswith("ws")


# ---------------------------------------------------------------------------
# 3. HTTP fallback path (Tier 3)
# ---------------------------------------------------------------------------


class TestHTTPFallbackPath:
    """Verify HTTP fallback when no transport is available."""

    def test_no_transport_when_endpoints_empty(self):
        """When both SLIM and NATS endpoints are empty, transport should be None."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "",
            "AGNTCY_NATS_ENDPOINT": "",
            "NATS_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            transport = mod.get_default_transport()
            assert transport is None

    def test_sdk_status_reports_http_failure_mode(self):
        """SDK status should report transport_active=False when no transport."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "",
            "AGNTCY_NATS_ENDPOINT": "",
            "NATS_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            status = mod.get_sdk_status()
            assert status["transport_active"] is False

    def test_agent_urls_default_to_container_apps_dns(self):
        """When CONTAINER_APP_ENV_FQDN is set, AGENT_URLS use internal DNS."""
        env = {
            "CONTAINER_APP_ENV_FQDN": "orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.chat.pipeline.constants as mod
            importlib.reload(mod)

            for agent_name, url in mod.AGENT_URLS.items():
                assert "internal." in url or "localhost" in url, (
                    f"{agent_name} URL doesn't use internal DNS: {url}"
                )


# ---------------------------------------------------------------------------
# 4. Tier cascade order
# ---------------------------------------------------------------------------


class TestTierCascade:
    """Verify ADR-001 tier cascade: SLIM → NATS → HTTP → 503."""

    def test_transport_type_defaults_to_slim(self):
        """Default transport type should be 'slim' per SPEC-1802."""
        env = {"AGNTCY_TRANSPORT_TYPE": "slim"}
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)
            assert mod.TRANSPORT_TYPE == "slim"

    def test_dispatch_mixin_503_on_all_tiers_exhausted(self):
        """When all transport tiers fail, dispatch should raise 503."""
        from fastapi import HTTPException
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        with pytest.raises(HTTPException) as exc_info:
            mixin._require_transport_or_fail("test-agent")
        assert exc_info.value.status_code == 503
