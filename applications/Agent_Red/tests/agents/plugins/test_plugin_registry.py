"""Tests for MCP Agent Plug-in Registry (SPEC-1706).

Tests cover:
  - YAML loading (agents.yaml)
  - Dict loading (testing)
  - Agent lookup by ID
  - Filtering by category, capability, tier
  - Internal vs external separation
  - Tool catalog generation
  - Tool → agent resolution
  - Singleton lifecycle
  - Endpoint resolution with env vars and templates

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.plugins.registry import (
    PluginAgentDefinition,
    PluginAgentRegistry,
)

CAMPAIGNS_CAPABILITIES = (
    "campaigns.list_active",
    "campaigns.get_discount_codes",
    "campaigns.get_talking_points",
    "campaigns.track_metrics",
)

CAMPAIGNS_SKILLS = {
    "campaigns:list-active": ("read", ("campaigns.list_active",)),
    "campaigns:get-discount-codes": ("read", ("campaigns.get_discount_codes",)),
    "campaigns:get-talking-points": ("read", ("campaigns.get_talking_points",)),
    "campaigns:track-metrics": ("mutate", ("campaigns.track_metrics",)),
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_AGENTS = {
    "test_agent": {
        "display_name": "Test Agent",
        "description": "A test agent",
        "spec_id": "SPEC-TEST",
        "category": "testing",
        "endpoint": "http://localhost:8080",
        "auth_type": "internal",
        "tier_gate": "starter",
        "capabilities": ["test.do_thing", "test.do_other"],
        "status": "available",
        "is_external": False,
    },
    "premium_agent": {
        "display_name": "Premium Agent",
        "description": "Enterprise-only agent",
        "spec_id": "SPEC-PREMIUM",
        "category": "premium",
        "endpoint": "http://localhost:9090",
        "tier_gate": "enterprise",
        "capabilities": ["premium.exclusive"],
        "status": "available",
    },
    "external_server": {
        "display_name": "External MCP",
        "description": "3rd party server",
        "spec_id": "SPEC-1712",
        "category": "external",
        "endpoint": "https://mcp.example.com",
        "auth_type": "oauth2",
        "credential_env": "EXT_SECRET",
        "tier_gate": "professional",
        "capabilities": ["ext.query", "ext.list"],
        "status": "available",
        "is_external": True,
        "read_only": True,
    },
    "disabled_agent": {
        "display_name": "Disabled Agent",
        "description": "Should not appear in queries",
        "spec_id": "SPEC-DIS",
        "category": "testing",
        "endpoint": "http://disabled:8080",
        "capabilities": ["disabled.do"],
        "status": "disabled",
    },
}


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    yield
    PluginAgentRegistry.reset()


@pytest.fixture
def registry() -> PluginAgentRegistry:
    r = PluginAgentRegistry.get_instance()
    r.load_from_dict(SAMPLE_AGENTS)
    return r


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


class TestLoading:
    def test_load_from_dict(self, registry: PluginAgentRegistry):
        assert registry.agent_count == 4

    def test_load_from_yaml(self):
        r = PluginAgentRegistry.get_instance()
        count = r.load_from_yaml()
        # agents.yaml has 7 core + 5 peer internal + 5 external + 3 integration = 20
        assert count == 20

    def test_load_from_missing_yaml(self, tmp_path):
        r = PluginAgentRegistry.get_instance()
        count = r.load_from_yaml(tmp_path / "nonexistent.yaml")
        assert count == 0

    def test_loaded_flag(self, registry: PluginAgentRegistry):
        assert registry.loaded is True


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


class TestQueries:
    def test_get_by_id(self, registry: PluginAgentRegistry):
        defn = registry.get("test_agent")
        assert defn is not None
        assert defn.display_name == "Test Agent"

    def test_get_missing(self, registry: PluginAgentRegistry):
        assert registry.get("nonexistent") is None

    def test_list_available_excludes_disabled(self, registry: PluginAgentRegistry):
        available = registry.list_available()
        ids = [a.agent_id for a in available]
        assert "disabled_agent" not in ids

    def test_list_available_includes_active(self, registry: PluginAgentRegistry):
        available = registry.list_available()
        ids = [a.agent_id for a in available]
        assert "test_agent" in ids
        assert "external_server" in ids

    def test_filter_by_category(self, registry: PluginAgentRegistry):
        results = registry.list_available(category="testing")
        assert len(results) == 1
        assert results[0].agent_id == "test_agent"

    def test_filter_by_capability(self, registry: PluginAgentRegistry):
        results = registry.list_available(capability="ext.query")
        assert len(results) == 1
        assert results[0].agent_id == "external_server"

    def test_filter_by_tier_starter(self, registry: PluginAgentRegistry):
        results = registry.list_available(tier="starter")
        # starter can only access starter-gated agents
        ids = [a.agent_id for a in results]
        assert "test_agent" in ids
        assert "premium_agent" not in ids  # enterprise-gated

    def test_filter_by_tier_enterprise(self, registry: PluginAgentRegistry):
        results = registry.list_available(tier="enterprise")
        ids = [a.agent_id for a in results]
        assert "premium_agent" in ids
        assert "test_agent" in ids  # lower tier also accessible

    def test_internal_agents_only(self, registry: PluginAgentRegistry):
        internal = registry.get_internal_agents()
        for a in internal:
            assert not a.is_external

    def test_external_servers_only(self, registry: PluginAgentRegistry):
        external = registry.get_external_servers()
        for a in external:
            assert a.is_external

    def test_find_by_capability(self, registry: PluginAgentRegistry):
        results = registry.find_by_capability("test.do_thing")
        assert len(results) == 1
        assert results[0].agent_id == "test_agent"

    def test_find_by_capability_empty(self, registry: PluginAgentRegistry):
        results = registry.find_by_capability("nonexistent.tool")
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Tool catalog
# ---------------------------------------------------------------------------


class TestToolCatalog:
    def test_catalog_generation(self, registry: PluginAgentRegistry):
        catalog = registry.get_tool_catalog()
        assert len(catalog) > 0

    def test_catalog_tool_format(self, registry: PluginAgentRegistry):
        catalog = registry.get_tool_catalog()
        for tool in catalog:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "_agent_id" in tool

    def test_catalog_tier_filter(self, registry: PluginAgentRegistry):
        starter_catalog = registry.get_tool_catalog(tier="starter")
        enterprise_catalog = registry.get_tool_catalog(tier="enterprise")
        assert len(enterprise_catalog) >= len(starter_catalog)

    def test_resolve_tool_agent(self, registry: PluginAgentRegistry):
        defn = registry.resolve_tool_agent("test.do_thing")
        assert defn is not None
        assert defn.agent_id == "test_agent"

    def test_resolve_unknown_tool(self, registry: PluginAgentRegistry):
        assert registry.resolve_tool_agent("unknown.tool") is None


class TestCampaignsAgentSpec1707:
    def test_campaigns_agent_metadata_from_production_yaml(self, monkeypatch):
        monkeypatch.setenv("AGENT_CAMPAIGNS_URL", "http://campaigns-agent.test:8080")
        r = PluginAgentRegistry.get_instance()
        r.load_from_yaml()

        campaigns = r.get("campaigns")
        assert campaigns is not None
        assert campaigns.display_name == "Campaigns Agent"
        assert campaigns.spec_id == "SPEC-1707"
        assert campaigns.category == "marketing"
        assert campaigns.agent_kind == "peer"
        assert campaigns.auth_type == "internal"
        assert campaigns.tier_gate == "professional"
        assert campaigns.health_check == "/health"
        assert campaigns.status == "available"
        assert campaigns.endpoint == "${AGENT_CAMPAIGNS_URL:-http://10.0.1.20:8080}"
        assert campaigns.resolve_endpoint() == "http://campaigns-agent.test:8080"
        assert campaigns.capabilities == CAMPAIGNS_CAPABILITIES

    def test_campaigns_agent_skills_catalog_and_tool_resolution(self):
        r = PluginAgentRegistry.get_instance()
        r.load_from_yaml()

        skills = {skill.skill_id: skill for skill in r.list_skills("campaigns")}
        assert set(skills) == set(CAMPAIGNS_SKILLS)

        for skill_id, (mode, tool_names) in CAMPAIGNS_SKILLS.items():
            assert skills[skill_id].mode == mode
            assert r.resolve_skill_to_tools(skill_id) == tool_names

        for tool_name in CAMPAIGNS_CAPABILITIES:
            agent = r.resolve_tool_agent(tool_name)
            assert agent is not None
            assert agent.agent_id == "campaigns"

        catalog = {
            tool["function"]["name"]: tool
            for tool in r.get_tool_catalog(tier="professional")
            if tool["_agent_id"] == "campaigns"
        }
        assert set(catalog) == set(CAMPAIGNS_CAPABILITIES)
        for tool_name in CAMPAIGNS_CAPABILITIES:
            assert catalog[tool_name]["_endpoint"] == "${AGENT_CAMPAIGNS_URL:-http://10.0.1.20:8080}"
            assert catalog[tool_name]["_is_external"] is False


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------


class TestAgentDefinition:
    def test_is_frozen(self):
        defn = PluginAgentDefinition(
            agent_id="test",
            display_name="Test",
            description="",
            spec_id="",
            category="",
            endpoint="http://test:8080",
        )
        with pytest.raises(AttributeError):
            defn.agent_id = "changed"  # type: ignore

    def test_has_capability(self):
        defn = PluginAgentDefinition(
            agent_id="test",
            display_name="",
            description="",
            spec_id="",
            category="",
            endpoint="",
            capabilities=("a.b", "c.d"),
        )
        assert defn.has_capability("a.b") is True
        assert defn.has_capability("x.y") is False

    def test_resolve_endpoint_template(self):
        defn = PluginAgentDefinition(
            agent_id="test",
            display_name="",
            description="",
            spec_id="",
            category="",
            endpoint="https://{shop_domain}/mcp",
        )
        resolved = defn.resolve_endpoint(shop_domain="test.myshopify.com")
        assert resolved == "https://test.myshopify.com/mcp"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_instance_same(self):
        a = PluginAgentRegistry.get_instance()
        b = PluginAgentRegistry.get_instance()
        assert a is b

    def test_reset_new_instance(self):
        a = PluginAgentRegistry.get_instance()
        PluginAgentRegistry.reset()
        b = PluginAgentRegistry.get_instance()
        assert a is not b
