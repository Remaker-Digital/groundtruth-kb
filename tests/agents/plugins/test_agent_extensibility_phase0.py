"""Phase 0 Agent Extensibility Tests (SPEC-1852, SPEC-1853, SPEC-1854, SPEC-1855).

Tests for canonical agent identity, stable skill identity, tenant agent
overlay, and invocation event contracts.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.plugins.registry import (
    AgentKind,
    AgentType,  # backward-compat alias
    PluginAgentDefinition,
    PluginAgentRegistry,
    SkillDefinition,
    SkillMode,
)
from src.agents.plugins.overlay import (
    EffectiveAgentConfig,
    EffectiveSkillConfig,
    resolve_effective_config,
    resolve_for_tenant,
)
from src.agents.plugins.events import (
    InvocationEvent,
    InvocationEventBus,
    emit_invocation,
)


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset singletons between tests."""
    PluginAgentRegistry.reset()
    InvocationEventBus.reset()
    yield
    PluginAgentRegistry.reset()
    InvocationEventBus.reset()


# ---------------------------------------------------------------------------
# SPEC-1852: Canonical Agent Identity
# ---------------------------------------------------------------------------


class TestCanonicalAgentIdentity:
    """SPEC-1852: Every agent has a unique agent_id and declared type."""

    def test_agent_kind_enum_values(self):
        """AgentKind has core, peer, internal values."""
        assert AgentKind.CORE.value == "core"
        assert AgentKind.PEER.value == "peer"
        assert AgentKind.INTERNAL.value == "internal"

    def test_agent_type_backward_compat_alias(self):
        """AgentType is a backward-compat alias for AgentKind."""
        assert AgentType is AgentKind

    def test_plugin_agent_definition_has_agent_kind(self):
        """PluginAgentDefinition includes agent_kind field (SPEC-1852 req 4)."""
        defn = PluginAgentDefinition(
            agent_id="test-agent",
            display_name="Test",
            description="Test agent",
            spec_id="SPEC-TEST",
            category="test",
            endpoint="http://localhost:8080",
            agent_kind="core",
        )
        assert defn.agent_kind == "core"

    def test_agent_kind_defaults_to_peer(self):
        """Default agent_kind is 'peer' (SPEC-1852)."""
        defn = PluginAgentDefinition(
            agent_id="test-agent",
            display_name="Test",
            description="Test",
            spec_id="",
            category="",
            endpoint="",
        )
        assert defn.agent_kind == "peer"

    def test_core_agents_registered_from_yaml(self):
        """Core pipeline agents are registered in agents.yaml (SPEC-1852)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        core = reg.get_core_agents()
        core_ids = {a.agent_id for a in core}
        expected = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
            "co-pilot",
        }
        assert core_ids == expected

    def test_list_agents_returns_all_with_kind_and_status(self):
        """list_agents() returns all registered agents (SPEC-1852 req 7)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        all_agents = reg.list_agents()
        assert len(all_agents) == 17
        for a in all_agents:
            assert a.agent_kind in ("core", "peer", "internal")
            assert a.status in ("available", "beta", "disabled", "deprecated")

    def test_list_agents_filters_by_kind(self):
        """list_agents(agent_kind=...) filters correctly."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        core = reg.list_agents(agent_kind="core")
        peer = reg.list_agents(agent_kind="peer")
        assert all(a.agent_kind == "core" for a in core)
        assert all(a.agent_kind == "peer" for a in peer)
        assert len(core) + len(peer) == 17

    def test_get_core_agent_ids_replaces_pipeline_agents(self):
        """get_core_agent_ids() provides same data as old PIPELINE_AGENTS (SPEC-1852 req 3)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        ids = reg.get_core_agent_ids()
        assert len(ids) == 7
        assert "intent-classifier" in ids
        assert "knowledge-retrieval" in ids

    def test_pipeline_edges_from_registry(self):
        """Pipeline edges are loaded from YAML config."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        edges = reg.get_pipeline_edges()
        assert len(edges) == 7
        assert ("intent-classifier", "knowledge-retrieval") in edges


# ---------------------------------------------------------------------------
# SPEC-1853: Stable Skill/Tool Identity
# ---------------------------------------------------------------------------


class TestStableSkillIdentity:
    """SPEC-1853: Every skill has a stable skill_id decoupled from MCP tool name."""

    def test_skill_id_format(self):
        """skill_id follows agent_id:skill_name format (SPEC-1853 req 1)."""
        skill = SkillDefinition(
            skill_id="campaigns:list-active",
            agent_id="campaigns",
            skill_name="list-active",
            display_name="List Active",
        )
        assert skill.skill_id == "campaigns:list-active"
        parts = skill.skill_id.split(":")
        assert len(parts) == 2
        assert parts[0] == skill.agent_id

    def test_skill_mode_values(self):
        """SkillMode enum has read, mutate, internal (SPEC-1853 req 4)."""
        assert SkillMode.READ.value == "read"
        assert SkillMode.MUTATE.value == "mutate"
        assert SkillMode.INTERNAL.value == "internal"

    def test_skill_to_mcp_tool_mapping(self):
        """Skill maintains mapping to MCP tool names (SPEC-1853 req 3)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        tools = reg.resolve_skill_to_tools("campaigns:list-active")
        assert tools == ("campaigns.list_active",)

    def test_list_skills_by_agent(self):
        """list_skills(agent_id) returns skills (SPEC-1853 req 6)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        skills = reg.list_skills("campaigns")
        assert len(skills) == 4
        for s in skills:
            assert s.agent_id == "campaigns"
            assert s.mode in ("read", "mutate", "internal")

    def test_list_skills_filters_by_mode(self):
        """list_skills can filter by mode."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        mutate = reg.list_skills("campaigns", mode="mutate")
        assert len(mutate) == 1
        assert mutate[0].skill_id == "campaigns:track-metrics"

    def test_get_skill_returns_none_for_unknown(self):
        """get_skill returns None for unknown skill_id."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        assert reg.get_skill("nonexistent:skill") is None

    def test_all_skills_have_valid_format(self):
        """Every registered skill follows the agent_id:skill_name format."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        for skill in reg.list_skills():
            parts = skill.skill_id.split(":")
            assert len(parts) == 2, f"Bad format: {skill.skill_id}"
            assert parts[0] == skill.agent_id, f"Agent mismatch: {skill.skill_id}"

    def test_credential_types_declared(self):
        """External skills declare credential types (SPEC-1853 req 5)."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        stripe_skills = reg.list_skills("stripe_mcp")
        for s in stripe_skills:
            assert "oauth2" in s.credential_types


# ---------------------------------------------------------------------------
# SPEC-1854: Tenant Agent Overlay
# ---------------------------------------------------------------------------


class TestTenantAgentOverlay:
    """SPEC-1854: Per-tenant agent/skill configuration overlay."""

    def _make_agent(self, **kwargs) -> PluginAgentDefinition:
        defaults = dict(
            agent_id="test-agent",
            display_name="Test Agent",
            description="Test",
            spec_id="SPEC-TEST",
            category="test",
            endpoint="http://localhost:8080",
            agent_kind="peer",
            skills=(
                SkillDefinition(
                    skill_id="test-agent:skill-a",
                    agent_id="test-agent",
                    skill_name="skill-a",
                    display_name="Skill A",
                    mode="read",
                    mcp_tool_names=("tool.a",),
                ),
                SkillDefinition(
                    skill_id="test-agent:skill-b",
                    agent_id="test-agent",
                    skill_name="skill-b",
                    display_name="Skill B",
                    mode="mutate",
                    mcp_tool_names=("tool.b",),
                ),
            ),
        )
        defaults.update(kwargs)
        return PluginAgentDefinition(**defaults)

    def test_no_overlay_returns_base_defaults(self):
        """No overlay = base registry defaults (SPEC-1854 req 4)."""
        agent = self._make_agent()
        config = resolve_effective_config(agent, overlay=None)
        assert config.enabled is True
        assert len(config.skills) == 2
        assert config.prompt_overrides == {}

    def test_overlay_disables_agent(self):
        """Overlay can disable an agent for a tenant."""
        agent = self._make_agent()
        config = resolve_effective_config(agent, overlay={"enabled": False})
        assert config.enabled is False

    def test_overlay_disables_specific_skill(self):
        """Overlay can disable a specific skill."""
        agent = self._make_agent()
        overlay = {
            "skill_overrides": {
                "test-agent:skill-b": {"enabled": False},
            }
        }
        config = resolve_effective_config(agent, overlay)
        skill_b = [s for s in config.skills if s.skill_id == "test-agent:skill-b"][0]
        assert skill_b.enabled is False

    def test_overlay_overrides_skill_mode(self):
        """Overlay can change skill mode."""
        agent = self._make_agent()
        overlay = {
            "skill_overrides": {
                "test-agent:skill-a": {"mode_override": "mutate"},
            }
        }
        config = resolve_effective_config(agent, overlay)
        skill_a = [s for s in config.skills if s.skill_id == "test-agent:skill-a"][0]
        assert skill_a.mode == "mutate"

    def test_overlay_adds_credential_ref(self):
        """Overlay can attach credential reference to a skill."""
        agent = self._make_agent()
        overlay = {
            "skill_overrides": {
                "test-agent:skill-a": {"credential_ref": "vault://tenant/key"},
            }
        }
        config = resolve_effective_config(agent, overlay)
        skill_a = [s for s in config.skills if s.skill_id == "test-agent:skill-a"][0]
        assert skill_a.credential_ref == "vault://tenant/key"

    def test_overlay_prompt_overrides(self):
        """Overlay can provide prompt overrides."""
        agent = self._make_agent()
        overlay = {"prompt_overrides": {"system": "Custom system prompt"}}
        config = resolve_effective_config(agent, overlay)
        assert config.prompt_overrides == {"system": "Custom system prompt"}

    def test_resolve_for_tenant_with_registry(self):
        """resolve_for_tenant integrates with the live registry."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        config = resolve_for_tenant("tenant-001", "campaigns")
        assert config is not None
        assert config.agent_id == "campaigns"
        assert config.enabled is True
        assert len(config.skills) == 4

    def test_resolve_for_tenant_unknown_agent(self):
        """resolve_for_tenant returns None for unknown agent_id."""
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        assert resolve_for_tenant("tenant-001", "nonexistent") is None


# ---------------------------------------------------------------------------
# SPEC-1855: Invocation Event Contract
# ---------------------------------------------------------------------------


class TestInvocationEvent:
    """SPEC-1855: Structured invocation events for observability and audit."""

    def test_event_has_required_fields(self):
        """InvocationEvent includes all SPEC-1855 req 1 fields."""
        event = InvocationEvent(
            trace_id="trace-001",
            invoker="system",
            target_agent_id="knowledge-retrieval",
            skill_id="knowledge-retrieval:retrieve-knowledge",
            tenant_id="tenant-001",
            conversation_id="conv-001",
            latency_ms=42.5,
            result_class="success",
            policy_verdict="allowed",
        )
        assert event.event_id  # Auto-generated UUID
        assert event.trace_id == "trace-001"
        assert event.target_agent_id == "knowledge-retrieval"
        assert event.timestamp  # Auto-generated

    def test_event_tree_structure(self):
        """Events form a tree via parent_event_id (SPEC-1855 req 2)."""
        root = InvocationEvent(
            trace_id="trace-001",
            target_agent_id="orchestrator",
            tenant_id="t-1",
            conversation_id="c-1",
        )
        child = InvocationEvent(
            trace_id="trace-001",
            parent_event_id=root.event_id,
            invoker="orchestrator",
            target_agent_id="knowledge-retrieval",
            tenant_id="t-1",
            conversation_id="c-1",
        )
        assert child.parent_event_id == root.event_id
        assert root.parent_event_id is None

    def test_event_bus_emit_and_subscribe(self):
        """Event bus delivers events to subscribers."""
        bus = InvocationEventBus.get_instance()
        received: list[InvocationEvent] = []
        bus.subscribe(lambda e: received.append(e))

        event = InvocationEvent(
            trace_id="t-1",
            target_agent_id="ic",
            tenant_id="tenant",
            conversation_id="conv",
        )
        bus.emit(event)
        assert len(received) == 1
        assert received[0].event_id == event.event_id

    def test_event_bus_buffer(self):
        """Event bus buffers events when enabled."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        emit_invocation(
            trace_id="t-1",
            target_agent_id="ic",
            tenant_id="tenant",
            conversation_id="conv",
        )
        emit_invocation(
            trace_id="t-1",
            target_agent_id="kr",
            tenant_id="tenant",
            conversation_id="conv",
        )

        events = bus.get_buffered_events()
        assert len(events) == 2
        assert events[0].target_agent_id == "ic"
        assert events[1].target_agent_id == "kr"

    def test_denied_invocation_event(self):
        """Denied attempts produce events (SPEC-1855 req 3 — dispatcher emits for denied)."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        emit_invocation(
            trace_id="t-1",
            target_agent_id="sales",
            skill_id="sales:create-checkout",
            tenant_id="tenant",
            conversation_id="conv",
            result_class="denied",
            policy_verdict="denied_by_binding",
        )

        events = bus.get_buffered_events()
        assert len(events) == 1
        assert events[0].result_class == "denied"
        assert events[0].policy_verdict == "denied_by_binding"

    def test_emit_convenience_function(self):
        """emit_invocation() creates and emits in one call."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        event = emit_invocation(
            trace_id="t-1",
            target_agent_id="campaigns",
            skill_id="campaigns:list-active",
            tenant_id="tenant-001",
            conversation_id="conv-001",
            invoker="intent-classifier",
            latency_ms=15.3,
        )

        assert event.event_id  # UUID assigned
        assert event.invoker == "intent-classifier"
        assert event.latency_ms == 15.3
        buffered = bus.get_buffered_events()
        assert len(buffered) == 1

    def test_subscriber_failure_does_not_crash_bus(self):
        """A failing subscriber does not prevent other subscribers from receiving events."""
        bus = InvocationEventBus.get_instance()
        received: list[str] = []

        def bad_sub(e: InvocationEvent) -> None:
            raise RuntimeError("boom")

        def good_sub(e: InvocationEvent) -> None:
            received.append(e.event_id)

        bus.subscribe(bad_sub)
        bus.subscribe(good_sub)

        event = InvocationEvent(
            trace_id="t", target_agent_id="a", tenant_id="t", conversation_id="c"
        )
        bus.emit(event)
        assert len(received) == 1


# ---------------------------------------------------------------------------
# Topology consistency (Codex P2 finding: no hard-coded agent lists)
# ---------------------------------------------------------------------------


class TestTopologyConsistency:
    """Verify topology surfaces use registry, not hard-coded agent lists."""

    def test_nats_agent_topics_match_registry(self):
        """NATS agent topics include all core agents (co-pilot was missing)."""
        from src.multi_tenant.nats_isolation import get_agent_topics, reset_agent_topics_cache
        reset_agent_topics_cache()
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        registry_ids = set(reg.get_core_agent_ids())
        nats_ids = set(get_agent_topics())
        assert "co-pilot" in nats_ids, "co-pilot must be in NATS agent topics"
        assert registry_ids == nats_ids

    def test_agent_urls_match_registry(self):
        """Pipeline AGENT_URLS covers all core agents from registry."""
        from src.chat.pipeline.constants import _build_agent_urls
        reg = PluginAgentRegistry.get_instance()
        reg.load_from_yaml()
        registry_ids = set(reg.get_core_agent_ids())
        url_ids = set(_build_agent_urls().keys())
        assert registry_ids == url_ids


# ---------------------------------------------------------------------------
# prompt_overrides non-operative marking (Codex P2 finding)
# ---------------------------------------------------------------------------


class TestPromptOverridesPhase2:
    """Verify prompt_overrides is accepted but not consumed."""

    def test_prompt_overrides_phase_constant(self):
        """_PROMPT_OVERRIDES_PHASE marks field as Phase 2 reserved."""
        from src.agents.plugins.overlay import _PROMPT_OVERRIDES_PHASE
        assert _PROMPT_OVERRIDES_PHASE == 2

    def test_prompt_overrides_not_consumed_by_prompt_builder(self):
        """SystemPromptBuilder has no reference to prompt_overrides."""
        import inspect
        from src.multi_tenant import system_prompt_builder
        source = inspect.getsource(system_prompt_builder)
        assert "prompt_overrides" not in source
