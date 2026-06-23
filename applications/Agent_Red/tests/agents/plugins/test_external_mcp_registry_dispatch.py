"""SPEC-1712 coverage for external MCP registry and dispatch surfaces."""

from __future__ import annotations

import pytest

from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.registry import PluginAgentRegistry

EXTERNAL_MCP_SERVERS = {
    "coinbase_mcp": {
        "auth_type": "api_key",
        "capabilities": ("coinbase.get_charge", "coinbase.list_events"),
        "credential_env": "COINBASE_MCP_KEY",
        "endpoint": "https://mcp.coinbase.com",
        "read_only": True,
        "status": "beta",
        "tier_gate": "enterprise",
    },
    "paypal_mcp": {
        "auth_type": "oauth2",
        "capabilities": ("paypal.get_transaction", "paypal.list_disputes"),
        "credential_env": "PAYPAL_MCP_SECRET",
        "endpoint": "https://mcp.paypal.com",
        "read_only": True,
        "status": "beta",
        "tier_gate": "professional",
    },
    "shopify_mcp": {
        "auth_type": "none",
        "capabilities": (
            "shopify.search_products",
            "shopify.get_order",
            "shopify.get_collections",
        ),
        "credential_env": "",
        "endpoint": "https://{shop_domain}/mcp",
        "read_only": True,
        "status": "available",
        "tier_gate": "starter",
    },
    "square_mcp": {
        "auth_type": "oauth2",
        "capabilities": (
            "square.get_payments",
            "square.list_appointments",
            "square.get_loyalty",
        ),
        "credential_env": "SQUARE_MCP_SECRET",
        "endpoint": "https://mcp.squareup.com",
        "read_only": False,
        "status": "beta",
        "tier_gate": "professional",
    },
    "stripe_mcp": {
        "auth_type": "oauth2",
        "capabilities": (
            "stripe.get_balance",
            "stripe.list_charges",
            "stripe.create_refund",
            "stripe.get_subscription",
        ),
        "credential_env": "STRIPE_MCP_SECRET",
        "endpoint": "https://mcp.stripe.com",
        "read_only": False,
        "status": "available",
        "tier_gate": "starter",
    },
}

EXTERNAL_MCP_SKILLS = {
    "coinbase_mcp:get-charge": ("read", ("coinbase.get_charge",), ("api_key",)),
    "coinbase_mcp:list-events": ("read", ("coinbase.list_events",), ("api_key",)),
    "paypal_mcp:get-transaction": ("read", ("paypal.get_transaction",), ("oauth2",)),
    "paypal_mcp:list-disputes": ("read", ("paypal.list_disputes",), ("oauth2",)),
    "shopify_mcp:get-collections": ("read", ("shopify.get_collections",), ()),
    "shopify_mcp:get-order": ("read", ("shopify.get_order",), ()),
    "shopify_mcp:search-products": ("read", ("shopify.search_products",), ()),
    "square_mcp:get-loyalty": ("read", ("square.get_loyalty",), ("oauth2",)),
    "square_mcp:get-payments": ("read", ("square.get_payments",), ("oauth2",)),
    "square_mcp:list-appointments": ("read", ("square.list_appointments",), ("oauth2",)),
    "stripe_mcp:create-refund": ("mutate", ("stripe.create_refund",), ("oauth2",)),
    "stripe_mcp:get-balance": ("read", ("stripe.get_balance",), ("oauth2",)),
    "stripe_mcp:get-subscription": ("read", ("stripe.get_subscription",), ("oauth2",)),
    "stripe_mcp:list-charges": ("read", ("stripe.list_charges",), ("oauth2",)),
}


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    yield
    PluginAgentRegistry.reset()


@pytest.fixture
def registry() -> PluginAgentRegistry:
    registry = PluginAgentRegistry.get_instance()
    registry.load_from_yaml()
    return registry


class TestExternalMcpSpec1712:
    def test_external_mcp_server_metadata_from_production_yaml(self, registry: PluginAgentRegistry):
        servers = {server.agent_id: server for server in registry.get_external_servers()}
        assert set(EXTERNAL_MCP_SERVERS).issubset(servers)

        for server_id, expected in EXTERNAL_MCP_SERVERS.items():
            server = servers[server_id]
            assert server.spec_id == "SPEC-1712"
            assert server.category == "external"
            assert server.agent_kind == "peer"
            assert server.is_external is True
            assert server.auth_type == expected["auth_type"]
            assert server.capabilities == expected["capabilities"]
            assert server.credential_env == expected["credential_env"]
            assert server.endpoint == expected["endpoint"]
            assert server.read_only is expected["read_only"]
            assert server.status == expected["status"]
            assert server.tier_gate == expected["tier_gate"]

    def test_external_mcp_skills_catalog_and_tool_resolution(self, registry: PluginAgentRegistry):
        skills = {skill.skill_id: skill for skill in registry.list_skills()}
        for skill_id, (mode, tool_names, credential_types) in EXTERNAL_MCP_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert skills[skill_id].credential_types == credential_types
            assert registry.resolve_skill_to_tools(skill_id) == tool_names

        for server_id, expected in EXTERNAL_MCP_SERVERS.items():
            for tool_name in expected["capabilities"]:
                agents = registry.find_by_capability(tool_name)
                assert [agent.agent_id for agent in agents] == [server_id]
                agent = registry.resolve_tool_agent(tool_name)
                assert agent is not None
                assert agent.agent_id == server_id

        catalog = {
            tool["function"]["name"]: tool
            for tool in registry.get_tool_catalog(tier="enterprise")
            if tool["_agent_id"] in EXTERNAL_MCP_SERVERS
        }
        expected_tools = {tool_name for server in EXTERNAL_MCP_SERVERS.values() for tool_name in server["capabilities"]}
        assert set(catalog) == expected_tools
        for tool_name, tool in catalog.items():
            assert tool["_is_external"] is True
            assert tool["_agent_id"] in EXTERNAL_MCP_SERVERS
            assert tool["_endpoint"] == EXTERNAL_MCP_SERVERS[tool["_agent_id"]]["endpoint"]
            assert tool["function"]["name"] == tool_name

    def test_default_payment_routes_target_stripe_mcp(self, registry: PluginAgentRegistry):
        assert registry.get_routing_rule("payment_issue") == {
            "suggested_peer": "stripe_mcp",
            "skill": "stripe_mcp:list-charges",
        }
        assert registry.get_routing_rule("subscription_question") == {
            "suggested_peer": "stripe_mcp",
            "skill": "stripe_mcp:get-subscription",
        }

    @pytest.mark.asyncio
    async def test_dispatch_external_mcp_tool_without_live_provider_call(
        self, registry: PluginAgentRegistry, monkeypatch
    ):
        calls = []

        async def fake_dispatch_external(
            defn,
            tool_name,
            arguments,
            *,
            tenant_id="",
            timeout_ms=0,
            **template_vars,
        ):
            calls.append(
                {
                    "agent_id": defn.agent_id,
                    "arguments": arguments,
                    "endpoint": defn.resolve_endpoint(**template_vars),
                    "tenant_id": tenant_id,
                    "timeout_ms": timeout_ms,
                    "tool_name": tool_name,
                }
            )
            return {
                "provider": defn.agent_id,
                "tool_name": tool_name,
                "tenant_id": tenant_id,
            }

        dispatcher = PluginDispatcher(registry=registry)
        monkeypatch.setattr(dispatcher, "_dispatch_external", fake_dispatch_external)

        result = await dispatcher.dispatch(
            "stripe.list_charges",
            {"limit": 5},
            tenant_id="tenant-external",
            timeout_ms=2500,
        )

        assert result.success is True
        assert result.agent_id == "stripe_mcp"
        assert result.tool_name == "stripe.list_charges"
        assert result.content == {
            "provider": "stripe_mcp",
            "tool_name": "stripe.list_charges",
            "tenant_id": "tenant-external",
        }
        assert result.metadata == {
            "endpoint": "https://mcp.stripe.com",
            "is_external": True,
            "category": "external",
        }
        assert calls == [
            {
                "agent_id": "stripe_mcp",
                "arguments": {"limit": 5},
                "endpoint": "https://mcp.stripe.com",
                "tenant_id": "tenant-external",
                "timeout_ms": 2500,
                "tool_name": "stripe.list_charges",
            }
        ]
