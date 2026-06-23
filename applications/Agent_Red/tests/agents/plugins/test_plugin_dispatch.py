"""Tests for MCP Agent Plug-in Dispatch (SPEC-1706).

Tests cover:
  - Dispatch to internal agents
  - Dispatch to external MCP servers
  - Unknown tool handling
  - Error handling and tracking
  - Health check
  - Stats (call_count, error_count)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher, PluginDispatchResult
from src.agents.plugins.registry import PluginAgentRegistry


class RecordingResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class RecordingHttpClient:
    def __init__(self):
        self.calls = []

    async def post(self, url, *, json, headers, timeout):
        self.calls.append(
            {
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return RecordingResponse({"ok": True, "received": json})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    yield
    PluginAgentRegistry.reset()


@pytest.fixture
def registry() -> PluginAgentRegistry:
    r = PluginAgentRegistry.get_instance()
    r.load_from_dict(
        {
            "test_agent": {
                "display_name": "Test",
                "description": "Test agent",
                "spec_id": "SPEC-TEST",
                "category": "testing",
                "endpoint": "http://test:8080",
                "capabilities": ["test.do_thing"],
                "status": "available",
            },
            "ext_server": {
                "display_name": "External",
                "description": "External MCP",
                "spec_id": "SPEC-1712",
                "category": "external",
                "endpoint": "https://mcp.ext.com",
                "capabilities": ["ext.query"],
                "status": "available",
                "is_external": True,
            },
        }
    )
    return r


@pytest.fixture
def dispatcher(registry) -> PluginDispatcher:
    return PluginDispatcher(registry=registry)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDispatch:
    @pytest.mark.asyncio
    async def test_dispatch_internal(self, dispatcher: PluginDispatcher):
        result = await dispatcher.dispatch("test.do_thing", {"query": "hello"}, tenant_id="t-1")
        assert result.success is True
        assert result.agent_id == "test_agent"
        assert result.tool_name == "test.do_thing"
        assert result.elapsed_ms > 0

    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self, dispatcher: PluginDispatcher):
        result = await dispatcher.dispatch("unknown.tool", {}, tenant_id="t-1")
        assert result.success is False
        assert "No agent registered" in result.error
        assert result.agent_id == "unknown"

    @pytest.mark.asyncio
    async def test_dispatch_tracks_call_count(self, dispatcher: PluginDispatcher):
        await dispatcher.dispatch("test.do_thing", {})
        await dispatcher.dispatch("test.do_thing", {})
        assert dispatcher.call_count == 2

    @pytest.mark.asyncio
    async def test_dispatch_tracks_error_count(self, dispatcher: PluginDispatcher):
        await dispatcher.dispatch("unknown.tool", {})
        assert dispatcher.error_count == 1

    @pytest.mark.asyncio
    async def test_dispatch_result_metadata(self, dispatcher: PluginDispatcher):
        result = await dispatcher.dispatch("test.do_thing", {"q": "test"}, tenant_id="t-1")
        assert result.metadata.get("agent_id") or result.agent_id == "test_agent"
        assert result.metadata.get("is_external") is False

    @pytest.mark.asyncio
    async def test_dispatch_external_mock(self, dispatcher: PluginDispatcher):
        result = await dispatcher.dispatch("ext.query", {"q": "test"}, tenant_id="t-1")
        # External dispatch falls back to mock when no AGNTCY SDK
        assert result.success is True
        assert result.agent_id == "ext_server"

    @pytest.mark.asyncio
    async def test_dispatch_campaigns_tool_through_production_registry(self, monkeypatch):
        monkeypatch.setenv("AGENT_CAMPAIGNS_URL", "http://campaigns-agent.test:8080")
        r = PluginAgentRegistry.get_instance()
        r.load_from_yaml()
        http_client = RecordingHttpClient()
        dispatcher = PluginDispatcher(registry=r, http_client=http_client)

        result = await dispatcher.dispatch(
            "campaigns.list_active",
            {"status": "active"},
            tenant_id="tenant-campaigns",
            conversation_id="conversation-campaigns",
            timeout_ms=1234,
        )

        assert result.success is True
        assert result.agent_id == "campaigns"
        assert result.tool_name == "campaigns.list_active"
        assert result.content == {
            "ok": True,
            "received": {
                "tool_name": "campaigns.list_active",
                "arguments": {"status": "active"},
                "tenant_id": "tenant-campaigns",
                "conversation_id": "conversation-campaigns",
            },
        }
        assert result.metadata == {
            "endpoint": "http://campaigns-agent.test:8080",
            "is_external": False,
            "category": "marketing",
        }

        assert http_client.calls == [
            {
                "url": "http://campaigns-agent.test:8080/tools/campaigns.list_active",
                "json": {
                    "tool_name": "campaigns.list_active",
                    "arguments": {"status": "active"},
                    "tenant_id": "tenant-campaigns",
                    "conversation_id": "conversation-campaigns",
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-Tenant-Id": "tenant-campaigns",
                    "X-Conversation-Id": "conversation-campaigns",
                },
                "timeout": 1.234,
            }
        ]


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_no_http(self, dispatcher: PluginDispatcher):
        # Without HTTP client, health check returns False
        result = await dispatcher.health_check("test_agent")
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_unknown_agent(self, dispatcher: PluginDispatcher):
        result = await dispatcher.health_check("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_all(self, dispatcher: PluginDispatcher):
        results = await dispatcher.health_check_all()
        assert isinstance(results, dict)
        assert "test_agent" in results


class TestDispatchResult:
    def test_result_structure(self):
        result = PluginDispatchResult(
            tool_name="test.tool",
            agent_id="test",
            success=True,
            content={"data": 1},
            elapsed_ms=5.0,
        )
        assert result.tool_name == "test.tool"
        assert result.success is True
        assert result.content == {"data": 1}
