"""Tests for the generic agent container app factory.

Verifies:
    - create_agent_app() produces a FastAPI app
    - Health endpoint returns agent status
    - Ready endpoint reflects configured state
    - HTTP process endpoint wraps request in A2A Message
    - Extra routes are registered

Run:
    pytest tests/agents/test_agent_app.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from src.agents.base import AgentRedBaseAgent
from src.agents.containers.agent_app import create_agent_app


# ---------------------------------------------------------------------------
# Concrete test agent (same pattern as test_base_agent.py)
# ---------------------------------------------------------------------------


class _TestAgent(AgentRedBaseAgent):
    """Simple agent for container app testing."""

    agent_type = "test-container"

    async def process(
        self, payload: dict[str, Any], headers: dict[str, str],
    ) -> dict[str, Any]:
        return {"echo": payload, "headers_received": headers}


# ---------------------------------------------------------------------------
# APP-01 to APP-03: App creation
# ---------------------------------------------------------------------------


class TestAppCreation:
    """create_agent_app() factory behavior."""

    def test_app_01_creates_fastapi_app(self):
        """Factory returns a FastAPI app with the agent attached."""
        app = create_agent_app(_TestAgent)
        assert app is not None
        assert app.state.agent.agent_type == "test-container"

    def test_app_02_app_title_includes_agent_type(self):
        """App title includes the agent type."""
        app = create_agent_app(_TestAgent)
        assert "test-container" in app.title


# ---------------------------------------------------------------------------
# APP-04 to APP-06: Health and readiness
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    """Health and readiness probe endpoints."""

    def test_app_04_health_before_setup(self):
        """Health returns 503 before agent setup."""
        app = create_agent_app(_TestAgent)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.get("/health")
        assert resp.status_code == 503
        body = resp.json()
        assert body["status"] == "not_configured"

    def test_app_05_ready_before_configure(self):
        """Ready returns 503 before agent configuration."""
        app = create_agent_app(_TestAgent)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.get("/ready")
        assert resp.status_code == 503
        assert resp.json()["ready"] is False

    def test_app_06_ready_after_configure(self):
        """Ready returns 200 after agent is configured."""
        app = create_agent_app(_TestAgent)
        # Manually mark as configured (normally done by startup)
        app.state.agent._configured = True

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/ready")
        assert resp.status_code == 200
        assert resp.json()["ready"] is True


# ---------------------------------------------------------------------------
# APP-07 to APP-09: HTTP process endpoint
# ---------------------------------------------------------------------------


class TestProcessEndpoint:
    """HTTP process endpoint (/agents/{type}/process)."""

    def test_app_07_process_endpoint_exists(self):
        """Agent-specific process endpoint is registered."""
        app = create_agent_app(_TestAgent)
        app.state.agent._configured = True

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/agents/test-container/process",
            json={"message": "hello"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["echo"]["message"] == "hello"

    def test_app_08_process_injects_headers(self):
        """Process endpoint passes tenant headers to agent."""
        app = create_agent_app(_TestAgent)
        app.state.agent._configured = True

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/agents/test-container/process",
            json={"data": "test"},
            headers={
                "x-tenant-id": "t-001",
                "x-conversation-id": "c-001",
            },
        )

        body = resp.json()
        assert body["headers_received"]["x-tenant-id"] == "t-001"

    def test_app_09_process_includes_metadata(self):
        """Process endpoint includes _agent and _latency_ms metadata."""
        app = create_agent_app(_TestAgent)
        app.state.agent._configured = True

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/agents/test-container/process",
            json={"test": True},
        )

        body = resp.json()
        assert body["_agent"] == "test-container"
        assert "_latency_ms" in body


# ---------------------------------------------------------------------------
# APP-10: Extra routes
# ---------------------------------------------------------------------------


class TestExtraRoutes:
    """Agent-specific extra routes."""

    def test_app_10_extra_routes_registered(self):
        """extra_routes_fn adds custom endpoints."""

        def add_custom_route(app, agent):
            @app.get("/custom/status")
            async def custom_status():
                return {"agent": agent.agent_type, "custom": True}

        app = create_agent_app(_TestAgent, extra_routes_fn=add_custom_route)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.get("/custom/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["agent"] == "test-container"
        assert body["custom"] is True
