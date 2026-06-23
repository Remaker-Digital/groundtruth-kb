"""SPEC-1709 coverage for Sales Agent registry and dispatch surfaces."""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.registry import PluginAgentRegistry

SALES_CAPABILITIES = (
    "sales.search_products",
    "sales.manage_cart",
    "sales.check_inventory",
    "sales.create_checkout",
    "sales.track_order",
)

SALES_SKILLS = {
    "sales:check-inventory": ("read", ("sales.check_inventory",)),
    "sales:create-checkout": ("mutate", ("sales.create_checkout",)),
    "sales:manage-cart": ("mutate", ("sales.manage_cart",)),
    "sales:search-products": ("read", ("sales.search_products",)),
    "sales:track-order": ("read", ("sales.track_order",)),
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


class TestSalesAgentSpec1709:
    def test_sales_agent_metadata_from_production_yaml(self, monkeypatch):
        monkeypatch.setenv("AGENT_SALES_URL", "http://sales-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        sales_agent = registry.get("sales")
        assert sales_agent is not None
        assert sales_agent.display_name == "Sales Agent"
        assert sales_agent.spec_id == "SPEC-1709"
        assert sales_agent.category == "commerce"
        assert sales_agent.agent_kind == "peer"
        assert sales_agent.auth_type == "internal"
        assert sales_agent.tier_gate == "professional"
        assert sales_agent.health_check == "/health"
        assert sales_agent.status == "available"
        assert sales_agent.endpoint == "${AGENT_SALES_URL:-http://10.0.1.22:8080}"
        assert sales_agent.resolve_endpoint() == "http://sales-agent.test:8080"
        assert sales_agent.capabilities == SALES_CAPABILITIES

    def test_sales_agent_skills_catalog_and_tool_resolution(self):
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()

        skills = {skill.skill_id: skill for skill in registry.list_skills("sales")}
        assert set(skills) == set(SALES_SKILLS)

        for skill_id, (mode, tool_names) in SALES_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert registry.resolve_skill_to_tools(skill_id) == tool_names

        for tool_name in SALES_CAPABILITIES:
            agent = registry.resolve_tool_agent(tool_name)
            assert agent is not None
            assert agent.agent_id == "sales"

        catalog = {
            tool["function"]["name"]: tool
            for tool in registry.get_tool_catalog(tier="professional")
            if tool["_agent_id"] == "sales"
        }
        assert set(catalog) == set(SALES_CAPABILITIES)
        for tool_name in SALES_CAPABILITIES:
            assert catalog[tool_name]["_endpoint"] == ("${AGENT_SALES_URL:-http://10.0.1.22:8080}")
            assert catalog[tool_name]["_is_external"] is False

    @pytest.mark.asyncio
    async def test_dispatch_sales_tool_through_production_registry(self, monkeypatch):
        monkeypatch.setenv("AGENT_SALES_URL", "http://sales-agent.test:8080")
        registry = PluginAgentRegistry.get_instance()
        registry.load_from_yaml()
        http_client = RecordingHttpClient()
        dispatcher = PluginDispatcher(registry=registry, http_client=http_client)

        result = await dispatcher.dispatch(
            "sales.search_products",
            {"query": "widget", "limit": 3},
            tenant_id="tenant-sales",
            conversation_id="conversation-sales",
            timeout_ms=2500,
        )

        assert result.success is True
        assert result.agent_id == "sales"
        assert result.tool_name == "sales.search_products"
        assert result.content == {
            "ok": True,
            "received": {
                "tool_name": "sales.search_products",
                "arguments": {"query": "widget", "limit": 3},
                "tenant_id": "tenant-sales",
                "conversation_id": "conversation-sales",
            },
        }
        assert result.metadata == {
            "endpoint": "http://sales-agent.test:8080",
            "is_external": False,
            "category": "commerce",
        }

        assert http_client.calls == [
            {
                "url": "http://sales-agent.test:8080/tools/sales.search_products",
                "json": {
                    "tool_name": "sales.search_products",
                    "arguments": {"query": "widget", "limit": 3},
                    "tenant_id": "tenant-sales",
                    "conversation_id": "conversation-sales",
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-Tenant-Id": "tenant-sales",
                    "X-Conversation-Id": "conversation-sales",
                },
                "timeout": 2.5,
            }
        ]
