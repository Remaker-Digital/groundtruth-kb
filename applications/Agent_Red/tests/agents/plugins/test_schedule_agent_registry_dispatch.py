"""SPEC-1711 coverage for Schedule Agent registry and dispatch surfaces."""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.registry import PluginAgentRegistry

SCHEDULE_CAPABILITIES = (
    "schedule.create_followup",
    "schedule.list_pending",
    "schedule.cancel_followup",
    "schedule.ingest_event",
    "schedule.send_notification",
)

SCHEDULE_SKILLS = {
    "schedule:create-followup": ("mutate", ("schedule.create_followup",)),
    "schedule:list-pending": ("read", ("schedule.list_pending",)),
    "schedule:cancel-followup": ("mutate", ("schedule.cancel_followup",)),
    "schedule:ingest-event": ("mutate", ("schedule.ingest_event",)),
    "schedule:send-notification": ("mutate", ("schedule.send_notification",)),
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


class TestScheduleAgentSpec1711:
    def test_schedule_agent_metadata_from_production_yaml(self, monkeypatch):
        monkeypatch.setenv("AGENT_SCHEDULE_URL", "http://schedule-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        schedule_agent = registry.get("schedule")
        assert schedule_agent is not None
        assert schedule_agent.display_name == "Schedule Agent"
        assert schedule_agent.spec_id == "SPEC-1711"
        assert schedule_agent.category == "scheduling"
        assert schedule_agent.agent_kind == "peer"
        assert schedule_agent.auth_type == "internal"
        assert schedule_agent.tier_gate == "professional"
        assert schedule_agent.health_check == "/health"
        assert schedule_agent.status == "available"
        assert schedule_agent.endpoint == "${AGENT_SCHEDULE_URL:-http://10.0.1.24:8080}"
        assert schedule_agent.resolve_endpoint() == "http://schedule-agent.test:8080"
        assert schedule_agent.capabilities == SCHEDULE_CAPABILITIES

    def test_schedule_agent_skills_catalog_and_tool_resolution(self):
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        skills = {skill.skill_id: skill for skill in registry.list_skills("schedule")}
        assert set(skills) == set(SCHEDULE_SKILLS)

        for skill_id, (mode, tool_names) in SCHEDULE_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert registry.resolve_skill_to_tools(skill_id) == tool_names

        for tool_name in SCHEDULE_CAPABILITIES:
            agent = registry.resolve_tool_agent(tool_name)
            assert agent is not None
            assert agent.agent_id == "schedule"

        catalog = {
            tool["function"]["name"]: tool
            for tool in registry.get_tool_catalog(tier="professional")
            if tool["_agent_id"] == "schedule"
        }
        assert set(catalog) == set(SCHEDULE_CAPABILITIES)
        for tool_name in SCHEDULE_CAPABILITIES:
            assert catalog[tool_name]["_endpoint"] == ("${AGENT_SCHEDULE_URL:-http://10.0.1.24:8080}")
            assert catalog[tool_name]["_is_external"] is False

    @pytest.mark.asyncio
    async def test_dispatch_schedule_tool_through_production_registry(self, monkeypatch):
        monkeypatch.setenv("AGENT_SCHEDULE_URL", "http://schedule-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()
        http_client = RecordingHttpClient()
        dispatcher = PluginDispatcher(registry=registry, http_client=http_client)

        result = await dispatcher.dispatch(
            "schedule.create_followup",
            {
                "customer_id": "customer-1",
                "scheduled_for": "2026-06-24T15:00:00Z",
                "message": "Follow up on order status",
            },
            tenant_id="tenant-schedule",
            conversation_id="conversation-schedule",
            timeout_ms=3000,
        )

        assert result.success is True
        assert result.agent_id == "schedule"
        assert result.tool_name == "schedule.create_followup"
        assert result.content == {
            "ok": True,
            "received": {
                "tool_name": "schedule.create_followup",
                "arguments": {
                    "customer_id": "customer-1",
                    "scheduled_for": "2026-06-24T15:00:00Z",
                    "message": "Follow up on order status",
                },
                "tenant_id": "tenant-schedule",
                "conversation_id": "conversation-schedule",
            },
        }
        assert result.metadata == {
            "endpoint": "http://schedule-agent.test:8080",
            "is_external": False,
            "category": "scheduling",
        }

        assert http_client.calls == [
            {
                "url": "http://schedule-agent.test:8080/tools/schedule.create_followup",
                "json": {
                    "tool_name": "schedule.create_followup",
                    "arguments": {
                        "customer_id": "customer-1",
                        "scheduled_for": "2026-06-24T15:00:00Z",
                        "message": "Follow up on order status",
                    },
                    "tenant_id": "tenant-schedule",
                    "conversation_id": "conversation-schedule",
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-Tenant-Id": "tenant-schedule",
                    "X-Conversation-Id": "conversation-schedule",
                },
                "timeout": 3.0,
            }
        ]
