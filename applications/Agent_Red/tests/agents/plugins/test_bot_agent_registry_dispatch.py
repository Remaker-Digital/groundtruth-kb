"""SPEC-1708 coverage for Bot Agent registry and dispatch surfaces."""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.registry import PluginAgentRegistry

BOT_CAPABILITIES = (
    "bot.authenticate_agent",
    "bot.negotiate_parameters",
    "bot.exchange_messages",
    "bot.enforce_guardrails",
)

BOT_SKILLS = {
    "bot_agent:authenticate-agent": ("read", ("bot.authenticate_agent",)),
    "bot_agent:negotiate-parameters": ("read", ("bot.negotiate_parameters",)),
    "bot_agent:exchange-messages": ("mutate", ("bot.exchange_messages",)),
    "bot_agent:enforce-guardrails": ("read", ("bot.enforce_guardrails",)),
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


class TestBotAgentSpec1708:
    def test_bot_agent_metadata_from_production_yaml(self, monkeypatch):
        monkeypatch.setenv("AGENT_BOT_URL", "http://bot-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        bot_agent = registry.get("bot_agent")
        assert bot_agent is not None
        assert bot_agent.display_name == "Bot Agent (A2A)"
        assert bot_agent.spec_id == "SPEC-1708"
        assert bot_agent.category == "agent-to-agent"
        assert bot_agent.agent_kind == "peer"
        assert bot_agent.auth_type == "internal"
        assert bot_agent.tier_gate == "enterprise"
        assert bot_agent.health_check == "/health"
        assert bot_agent.status == "available"
        assert bot_agent.endpoint == "${AGENT_BOT_URL:-http://10.0.1.21:8080}"
        assert bot_agent.resolve_endpoint() == "http://bot-agent.test:8080"
        assert bot_agent.capabilities == BOT_CAPABILITIES

    def test_bot_agent_skills_catalog_and_tool_resolution(self):
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        skills = {skill.skill_id: skill for skill in registry.list_skills("bot_agent")}
        assert set(skills) == set(BOT_SKILLS)

        for skill_id, (mode, tool_names) in BOT_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert registry.resolve_skill_to_tools(skill_id) == tool_names

        for tool_name in BOT_CAPABILITIES:
            agent = registry.resolve_tool_agent(tool_name)
            assert agent is not None
            assert agent.agent_id == "bot_agent"

        catalog = {
            tool["function"]["name"]: tool
            for tool in registry.get_tool_catalog(tier="enterprise")
            if tool["_agent_id"] == "bot_agent"
        }
        assert set(catalog) == set(BOT_CAPABILITIES)
        for tool_name in BOT_CAPABILITIES:
            assert catalog[tool_name]["_endpoint"] == "${AGENT_BOT_URL:-http://10.0.1.21:8080}"
            assert catalog[tool_name]["_is_external"] is False

    @pytest.mark.asyncio
    async def test_dispatch_bot_tool_through_production_registry(self, monkeypatch):
        monkeypatch.setenv("AGENT_BOT_URL", "http://bot-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()
        http_client = RecordingHttpClient()
        dispatcher = PluginDispatcher(registry=registry, http_client=http_client)

        result = await dispatcher.dispatch(
            "bot.exchange_messages",
            {"message": "hello", "agent_session_id": "bot-session-1"},
            tenant_id="tenant-bot",
            conversation_id="conversation-bot",
            timeout_ms=2500,
        )

        assert result.success is True
        assert result.agent_id == "bot_agent"
        assert result.tool_name == "bot.exchange_messages"
        assert result.content == {
            "ok": True,
            "received": {
                "tool_name": "bot.exchange_messages",
                "arguments": {
                    "message": "hello",
                    "agent_session_id": "bot-session-1",
                },
                "tenant_id": "tenant-bot",
                "conversation_id": "conversation-bot",
            },
        }
        assert result.metadata == {
            "endpoint": "http://bot-agent.test:8080",
            "is_external": False,
            "category": "agent-to-agent",
        }

        assert http_client.calls == [
            {
                "url": "http://bot-agent.test:8080/tools/bot.exchange_messages",
                "json": {
                    "tool_name": "bot.exchange_messages",
                    "arguments": {
                        "message": "hello",
                        "agent_session_id": "bot-session-1",
                    },
                    "tenant_id": "tenant-bot",
                    "conversation_id": "conversation-bot",
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-Tenant-Id": "tenant-bot",
                    "X-Conversation-Id": "conversation-bot",
                },
                "timeout": 2.5,
            }
        ]
