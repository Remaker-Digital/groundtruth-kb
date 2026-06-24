"""Multi-replica agent routing coverage for SPEC-1800 / WI-3204."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from src.agents.plugins.registry import PluginAgentRegistry
from src.chat.pipeline import constants
from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
from src.multi_tenant import agntcy_directory, agntcy_sdk_integration


@pytest.fixture(autouse=True)
def _reset_agent_routing_state(monkeypatch: pytest.MonkeyPatch) -> None:
    PluginAgentRegistry.reset()
    agntcy_directory._agent_cache.clear()
    monkeypatch.setattr(agntcy_directory, "_agent_names_cache", None)
    monkeypatch.setattr(agntcy_directory, "_directory_client", None)
    monkeypatch.setattr(agntcy_directory, "_directory_available", False)
    monkeypatch.setattr(agntcy_directory, "DIRECTORY_ADDR", "")
    yield
    PluginAgentRegistry.reset()
    agntcy_directory._agent_cache.clear()


def _core_agent_ids() -> set[str]:
    registry = PluginAgentRegistry.get_instance()
    registry.load_from_yaml()
    return set(registry.get_core_agent_ids())


def _env_key(agent_id: str) -> str:
    return "AGENT_" + agent_id.upper().replace("-", "_") + "_URL"


def test_registry_urls_use_aca_service_names_without_replica_ordinals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core_agents = _core_agent_ids()
    monkeypatch.setattr(
        constants,
        "_INTERNAL_BASE",
        "http://agent-red-{name}.internal.apps.example:8080",
    )
    for agent_id in core_agents:
        monkeypatch.delenv(_env_key(agent_id), raising=False)

    urls = constants._build_agent_urls()

    assert set(urls) == core_agents
    for agent_id, url in urls.items():
        assert url == f"http://agent-red-{agent_id}.internal.apps.example:8080"
        service_host = url.split("://", maxsplit=1)[1].split(".", maxsplit=1)[0]
        assert service_host == f"agent-red-{agent_id}"


def test_critic_urls_parse_multi_endpoint_failover_and_single_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        constants.AGENT_URLS,
        "critic-supervisor",
        "http://critic-a:8080, http://critic-b:8080,,http://critic-c:8080",
    )

    assert constants.get_critic_urls() == [
        "http://critic-a:8080",
        "http://critic-b:8080",
        "http://critic-c:8080",
    ]

    monkeypatch.setitem(
        constants.AGENT_URLS,
        "critic-supervisor",
        "http://critic-single:8080",
    )

    assert constants.get_critic_urls() == ["http://critic-single:8080"]


def test_directory_static_fallback_lists_registry_core_agents() -> None:
    core_agents = _core_agent_ids()

    listed = agntcy_directory.list_agents()

    assert {agent["short_name"] for agent in listed} == core_agents
    assert {agent["source"] for agent in listed} == {"static"}
    for agent in listed:
        assert agent["name"] == (f"{agntcy_directory.ORG_NAMESPACE}/{agent['short_name']}")


def test_agent_topic_uses_directory_metadata_then_stable_agent_id() -> None:
    agntcy_directory._agent_cache["intent-classifier"] = {
        "name": "remaker-digital/agent-red/intent-classifier",
        "topic": "tenant-a.intent-classifier.v2",
        "source": "directory",
        "resolved": True,
    }

    assert agntcy_directory.get_agent_topic("intent-classifier") == "tenant-a.intent-classifier.v2"

    agntcy_directory._agent_cache.clear()

    assert agntcy_directory.get_agent_topic("knowledge-retrieval") == "knowledge-retrieval"
    assert agntcy_directory.get_agent_topic("unknown-agent") == "unknown-agent"


class _DispatchHarness(AgentDispatchMixin):
    def __init__(self) -> None:
        self._current_tenant_id = "tenant-001"
        self._current_conversation_id = "conversation-001"
        self._current_trace_id = "trace-001"


class _FakeA2AClient:
    async def send_message(self, request: Any) -> Any:
        return SimpleNamespace(
            root=SimpleNamespace(
                result=SimpleNamespace(
                    parts=[
                        SimpleNamespace(text='{"routed": true}'),
                    ],
                ),
            ),
        )


@pytest.mark.asyncio()
async def test_transport_dispatch_resolves_directory_topic_before_client_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested_topics: list[str] = []
    client_topics: list[str] = []

    def fake_get_agent_topic(agent_topic: str) -> str:
        requested_topics.append(agent_topic)
        return f"resolved.{agent_topic}"

    async def fake_create_a2a_client(topic: str) -> _FakeA2AClient:
        client_topics.append(topic)
        return _FakeA2AClient()

    monkeypatch.setattr(
        agntcy_directory,
        "get_agent_topic",
        fake_get_agent_topic,
    )
    monkeypatch.setattr(
        agntcy_sdk_integration,
        "create_a2a_client",
        fake_create_a2a_client,
    )

    result = await _DispatchHarness()._call_via_transport(
        "intent-classifier",
        {"message": "hello"},
    )

    assert result == {"routed": True}
    assert requested_topics == ["intent-classifier"]
    assert client_topics == ["resolved.intent-classifier"]
