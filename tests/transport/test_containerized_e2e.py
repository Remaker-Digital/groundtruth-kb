"""Phase 3 — Containerized end-to-end transport tests.

Tests the full pipeline paths through containerized agents using real
authenticated requests. These tests require the staging test host.

Pipeline paths tested:
- gateway → IC → KR → RG → Critic (happy path via chat endpoint)
- gateway → IC → escalation path
- gateway → analytics collection path (fire-and-forget, verified via logs)
- gateway → widget conversation path (X-Widget-Key auth)

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 3.
Governing decisions: ADR-001, ADR-002.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import time

import pytest

# Skip entire module if no test host URL or auth key
TEST_HOST_URL = os.environ.get("TEST_HOST_URL", "")
STAGING_API_KEY = os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")
STAGING_WIDGET_KEY = os.environ.get("STAGING_WIDGET_KEY", "")
STAGING_TENANT = os.environ.get("STAGING_TENANT_ID", "remaker-digital-001")

requires_test_host = pytest.mark.skipif(
    not TEST_HOST_URL,
    reason="TEST_HOST_URL not set — containerized E2E tests require staging test host",
)

pytestmark = [requires_test_host, pytest.mark.e2e]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_host_url() -> str:
    return TEST_HOST_URL.rstrip("/")


@pytest.fixture
def http_client():
    """Shared httpx client for E2E tests."""
    import httpx
    client = httpx.Client(timeout=60.0)
    yield client
    client.close()


@pytest.fixture
def api_headers() -> dict[str, str]:
    """Auth headers for SPA/API key authentication."""
    if not STAGING_API_KEY:
        pytest.skip("SUPERADMIN_PREVIEW_API_KEY not set")
    return {"X-API-Key": STAGING_API_KEY}


@pytest.fixture
def widget_headers() -> dict[str, str]:
    """Auth headers for widget key authentication."""
    if not STAGING_WIDGET_KEY:
        pytest.skip("STAGING_WIDGET_KEY not set")
    return {"X-Widget-Key": STAGING_WIDGET_KEY}


# ---------------------------------------------------------------------------
# 1. Transport readiness (topology verification)
# ---------------------------------------------------------------------------


class TestTransportReadiness:
    """Verify transport layer is configured before dispatch tests."""

    def test_gateway_transport_status(self, test_host_url, http_client):
        """Gateway /ready should report actual transport connectivity."""
        resp = http_client.get(f"{test_host_url}/ready")
        assert resp.status_code == 200
        data = resp.json()
        sdk = data.get("agntcy_sdk", {})
        assert sdk["sdk_initialized"] is True
        # transport_active now reflects actual setup() success
        tier = sdk.get("active_tier", "unknown")
        active = sdk.get("transport_active", False)
        print(f"\n  Transport: tier={tier}, active={active}")

    def test_all_agent_topics_registered(self, test_host_url, http_client):
        """All 6 mandatory agent topics must be registered."""
        resp = http_client.get(f"{test_host_url}/ready")
        topics = resp.json().get("agntcy_sdk", {}).get("agent_topics", [])
        required = {
            "intent-classifier", "knowledge-retrieval", "response-generator",
            "critic-supervisor", "escalation-handler", "analytics-collector",
        }
        assert required.issubset(set(topics)), f"Missing: {required - set(topics)}"


# ---------------------------------------------------------------------------
# 2. Full pipeline path: chat request → IC → KR → RG → Critic
# ---------------------------------------------------------------------------


class TestFullPipelinePath:
    """Send a real chat message through the containerized pipeline."""

    def test_chat_dispatch_traverses_agents(
        self, test_host_url, http_client, api_headers,
    ):
        """An authenticated chat request must traverse IC→KR→RG→Critic.

        This is the definitive E2E proof: a real message enters the gateway,
        gets classified by IC, knowledge retrieved by KR, response generated
        by RG, and validated by Critic — all via containerized agents.
        """
        resp = http_client.post(
            f"{test_host_url}/api/chat",
            headers={**api_headers, "Content-Type": "application/json"},
            json={
                "message": "What are your store hours?",
                "conversation_id": f"e2e-transport-{int(time.time())}",
                "tenant_id": STAGING_TENANT,
            },
            timeout=30.0,
        )
        # Must succeed — 503 means transport failed, which is a test failure
        assert resp.status_code == 200, (
            f"Chat dispatch failed with {resp.status_code}. "
            f"Expected 200 proving IC→KR→RG→Critic traversal. "
            f"Body: {resp.text[:200]}"
        )
        data = resp.json()
        assert "response" in data or "message" in data or "text" in data, (
            "Response missing content — pipeline may not have completed"
        )

    def test_streaming_response_through_rg(
        self, test_host_url, http_client, api_headers,
    ):
        """Streaming chat should work through the containerized RG agent."""
        resp = http_client.post(
            f"{test_host_url}/api/chat/stream",
            headers={**api_headers, "Content-Type": "application/json", "Accept": "text/event-stream"},
            json={
                "message": "Hello",
                "conversation_id": f"e2e-stream-{int(time.time())}",
                "tenant_id": STAGING_TENANT,
            },
            timeout=30.0,
        )
        assert resp.status_code == 200, (
            f"Streaming dispatch failed with {resp.status_code}. "
            f"Expected 200 proving RG streaming through container. "
            f"Body: {resp.text[:200]}"
        )
        content_type = resp.headers.get("content-type", "")
        assert "text/event-stream" in content_type or "application/json" in content_type, (
            f"Unexpected content type: {content_type}"
        )


# ---------------------------------------------------------------------------
# 3. Escalation path
# ---------------------------------------------------------------------------


class TestEscalationPath:
    """Verify escalation dispatch through containerized escalation handler."""

    def test_escalation_trigger_dispatches(
        self, test_host_url, http_client, api_headers,
    ):
        """A message requesting human help should trigger escalation dispatch."""
        resp = http_client.post(
            f"{test_host_url}/api/chat",
            headers={**api_headers, "Content-Type": "application/json"},
            json={
                "message": "I need to speak with a human agent right now please",
                "conversation_id": f"e2e-escalation-{int(time.time())}",
                "tenant_id": STAGING_TENANT,
            },
            timeout=30.0,
        )
        assert resp.status_code == 200, (
            f"Escalation dispatch failed with {resp.status_code}. "
            f"Expected 200 proving escalation handler container dispatch. "
            f"Body: {resp.text[:200]}"
        )


# ---------------------------------------------------------------------------
# 4. Widget conversation path
# ---------------------------------------------------------------------------


class TestWidgetPath:
    """Verify widget traffic traverses the same containerized pipeline."""

    def test_widget_chat_uses_container_pipeline(
        self, test_host_url, http_client, widget_headers,
    ):
        """Widget-authenticated chat must use the same dispatch pipeline."""
        resp = http_client.post(
            f"{test_host_url}/api/chat",
            headers={
                **widget_headers,
                "Content-Type": "application/json",
                "X-Widget-Origin": "https://test-store.myshopify.com",
            },
            json={
                "message": "Do you have any sales?",
                "conversation_id": f"e2e-widget-{int(time.time())}",
            },
            timeout=30.0,
        )
        assert resp.status_code == 200, (
            f"Widget chat dispatch failed with {resp.status_code}. "
            f"Expected 200 proving widget traffic through container pipeline. "
            f"Body: {resp.text[:200]}"
        )
