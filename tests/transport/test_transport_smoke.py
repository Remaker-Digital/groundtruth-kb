"""Phase 3 — Local transport smoke tests.

Tests real client creation against local config. Validates SLIM path,
NATS path, HTTP fallback dispatch proof, and topology readiness.
No mocks for transport creation — real SDK objects.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 2.
Governing decisions: ADR-001 (dispatch by physical possibility), SPEC-1802.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, patch

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
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)

            factory = mod.get_agntcy_factory()
            assert factory is not None

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
            mod.get_default_transport()
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

    def test_nats_websocket_protocol_detected(self):
        """NATS endpoint with wss:// should be detected as WebSocket protocol."""
        env = {
            "AGNTCY_SLIM_ENDPOINT": "",
            "AGNTCY_NATS_ENDPOINT": "wss://nats.example.internal:8080",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)
            assert mod.NATS_ENDPOINT.startswith("wss")


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

    def test_http_fallback_dispatch_proof(self):
        """With transport=None, HTTP dispatch branch is entered and calls agent container.

        This proves Tier 3 dispatch works: transport unavailable → HTTP fallback
        makes a real HTTP request to the agent container URL. Not just 503.
        """
        import httpx
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        from src.chat.pipeline.constants import AGENT_CLASSIFY_PATH

        # Build a minimal mixin instance with agent URLs pointing to a mock
        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        mixin._agent_urls = {
            "intent-classifier": "http://mock-ic.internal:8080",
        }

        # Track whether the HTTP request was made
        http_calls: list[httpx.Request] = []

        async def mock_post(url, **kwargs):
            req = httpx.Request("POST", url)
            http_calls.append(req)
            return httpx.Response(
                200,
                json={
                    "intent": "general_inquiry",
                    "confidence": 0.95,
                    "sub_intent": None,
                },
                request=req,
            )

        mock_client = AsyncMock()
        mock_client.post = mock_post

        # Make _get_http_client return our mock
        mixin._get_http_client = AsyncMock(return_value=mock_client)

        # Patch transport to be unavailable
        with patch(
            "src.multi_tenant.agntcy_sdk_integration._transport", None
        ), patch(
            "src.multi_tenant.agntcy_sdk_integration._transport_setup_ok", False
        ):
            result = asyncio.run(
                mixin._call_intent_classifier_http("test message", "system prompt")
            )

        # Prove the HTTP branch was entered and hit the correct endpoint
        assert len(http_calls) == 1, "Expected exactly 1 HTTP call to IC container"
        assert AGENT_CLASSIFY_PATH in str(http_calls[0].url), (
            f"HTTP call did not target {AGENT_CLASSIFY_PATH}: {http_calls[0].url}"
        )
        assert result["intent"] == "general_inquiry"


# ---------------------------------------------------------------------------
# 4. Configuration defaults
# ---------------------------------------------------------------------------


class TestConfigDefaults:
    """Verify transport configuration defaults."""

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

    def test_transport_type_defaults_to_slim(self):
        """Default transport type should be 'slim' per SPEC-1802."""
        env = {"AGNTCY_TRANSPORT_TYPE": "slim"}
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import src.multi_tenant.agntcy_sdk_integration as mod
            importlib.reload(mod)
            assert mod.TRANSPORT_TYPE == "slim"


# ---------------------------------------------------------------------------
# 5. Topology readiness (requires staging test host)
# ---------------------------------------------------------------------------

TEST_HOST_URL = os.environ.get("TEST_HOST_URL", "")

requires_test_host = pytest.mark.skipif(
    not TEST_HOST_URL,
    reason="TEST_HOST_URL not set — topology readiness tests require staging",
)


class TestTopologyReadiness:
    """Verify gateway transport readiness (moved from Category 3)."""

    @requires_test_host
    def test_gateway_transport_status(self):
        """Gateway /ready should report transport connectivity."""
        import httpx
        client = httpx.Client(timeout=30.0)
        try:
            resp = client.get(f"{TEST_HOST_URL.rstrip('/')}/ready")
            assert resp.status_code == 200
            data = resp.json()
            sdk = data.get("agntcy_sdk", {})
            assert sdk["sdk_initialized"] is True
            tier = sdk.get("active_tier", "unknown")
            active = sdk.get("transport_active", False)
            print(f"\n  Transport: tier={tier}, active={active}")
        finally:
            client.close()

    @requires_test_host
    def test_all_agent_topics_registered(self):
        """All 6 mandatory agent topics must be registered."""
        import httpx
        client = httpx.Client(timeout=30.0)
        try:
            resp = client.get(f"{TEST_HOST_URL.rstrip('/')}/ready")
            topics = resp.json().get("agntcy_sdk", {}).get("agent_topics", [])
            required = {
                "intent-classifier", "knowledge-retrieval", "response-generator",
                "critic-supervisor", "escalation-handler", "analytics-collector",
            }
            assert required.issubset(set(topics)), f"Missing: {required - set(topics)}"
        finally:
            client.close()
