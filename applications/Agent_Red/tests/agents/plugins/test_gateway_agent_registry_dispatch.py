"""SPEC-1710 coverage for Gateway Agent registry and dispatch surfaces."""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.registry import PluginAgentRegistry

GATEWAY_CAPABILITIES = (
    "gateway.check_availability",
    "gateway.queue_customer",
    "gateway.transfer_context",
    "gateway.monitor_queue",
)

GATEWAY_SKILLS = {
    "gateway:check-availability": ("read", ("gateway.check_availability",)),
    "gateway:monitor-queue": ("read", ("gateway.monitor_queue",)),
    "gateway:queue-customer": ("mutate", ("gateway.queue_customer",)),
    "gateway:transfer-context": ("mutate", ("gateway.transfer_context",)),
}


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


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    yield
    PluginAgentRegistry.reset()


class TestGatewayAgentSpec1710:
    def test_gateway_agent_metadata_from_production_yaml(self, monkeypatch):
        monkeypatch.setenv("AGENT_GATEWAY_URL", "http://gateway-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        gateway_agent = registry.get("gateway")
        assert gateway_agent is not None
        assert gateway_agent.display_name == "Gateway Agent"
        assert gateway_agent.spec_id == "SPEC-1710"
        assert gateway_agent.category == "escalation"
        assert gateway_agent.agent_kind == "peer"
        assert gateway_agent.auth_type == "internal"
        assert gateway_agent.tier_gate == "starter"
        assert gateway_agent.health_check == "/health"
        assert gateway_agent.status == "available"
        assert gateway_agent.endpoint == "${AGENT_GATEWAY_URL:-http://10.0.1.23:8080}"
        assert gateway_agent.resolve_endpoint() == "http://gateway-agent.test:8080"
        assert gateway_agent.capabilities == GATEWAY_CAPABILITIES

    def test_gateway_agent_skills_catalog_and_tool_resolution(self):
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        skills = {skill.skill_id: skill for skill in registry.list_skills("gateway")}
        assert set(skills) == set(GATEWAY_SKILLS)

        for skill_id, (mode, tool_names) in GATEWAY_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert registry.resolve_skill_to_tools(skill_id) == tool_names

        for tool_name in GATEWAY_CAPABILITIES:
            agent = registry.resolve_tool_agent(tool_name)
            assert agent is not None
            assert agent.agent_id == "gateway"

        catalog = {
            tool["function"]["name"]: tool
            for tool in registry.get_tool_catalog(tier="starter")
            if tool["_agent_id"] == "gateway"
        }
        assert set(catalog) == set(GATEWAY_CAPABILITIES)
        for tool_name in GATEWAY_CAPABILITIES:
            assert catalog[tool_name]["_endpoint"] == ("${AGENT_GATEWAY_URL:-http://10.0.1.23:8080}")
            assert catalog[tool_name]["_is_external"] is False

    @pytest.mark.asyncio
    async def test_dispatch_gateway_tool_through_production_registry(self, monkeypatch):
        monkeypatch.setenv("AGENT_GATEWAY_URL", "http://gateway-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()
        http_client = RecordingHttpClient()
        dispatcher = PluginDispatcher(registry=registry, http_client=http_client)

        result = await dispatcher.dispatch(
            "gateway.check_availability",
            {"skill": "billing"},
            tenant_id="tenant-gateway",
            conversation_id="conversation-gateway",
            timeout_ms=2500,
        )

        assert result.success is True
        assert result.agent_id == "gateway"
        assert result.tool_name == "gateway.check_availability"
        assert result.content == {
            "ok": True,
            "received": {
                "tool_name": "gateway.check_availability",
                "arguments": {"skill": "billing"},
                "tenant_id": "tenant-gateway",
                "conversation_id": "conversation-gateway",
            },
        }
        assert result.metadata == {
            "endpoint": "http://gateway-agent.test:8080",
            "is_external": False,
            "category": "escalation",
        }

        assert http_client.calls == [
            {
                "url": "http://gateway-agent.test:8080/tools/gateway.check_availability",
                "json": {
                    "tool_name": "gateway.check_availability",
                    "arguments": {"skill": "billing"},
                    "tenant_id": "tenant-gateway",
                    "conversation_id": "conversation-gateway",
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-Tenant-Id": "tenant-gateway",
                    "X-Conversation-Id": "conversation-gateway",
                },
                "timeout": 2.5,
            }
        ]
