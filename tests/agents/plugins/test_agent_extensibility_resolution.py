"""Effective Resolution + KR Migration Tests (SPEC-1859, SPEC-1860).

Tests for three-layer resolution algorithm, list_available_skills,
and KR MCP migration to binding system.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.kr_migration import (
    KR_AGENT_ID,
    KR_SKILL_ID,
    MigrationState,
    get_migration_state,
    is_tenant_migrated,
    migrate_tenant_kr_bindings,
    reset_migration_states,
    resolve_kr_with_fallback,
    set_migration_state,
)
from src.agents.plugins.overlay import (
    ResolvedSkill,
    SkillDenial,
    clear_resolution_cache,
    list_available_skills,
    resolve_skill,
)
from src.agents.plugins.registry import PluginAgentRegistry


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()
    clear_resolution_cache()
    reset_migration_states()
    yield
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()
    clear_resolution_cache()
    reset_migration_states()


@pytest.fixture
def registry():
    reg = PluginAgentRegistry.get_instance()
    reg.load_from_yaml()
    return reg


@pytest.fixture
def binding_svc():
    return SkillBindingService.get_instance()


# ---------------------------------------------------------------------------
# SPEC-1859: Effective Resolution
# ---------------------------------------------------------------------------


class TestEffectiveResolution:
    """SPEC-1859: Three-layer resolution algorithm."""

    def test_denied_unknown_agent(self, registry):
        """Unknown agent = denied."""
        result = resolve_skill("t-1", "nonexistent", "nonexistent:x")
        assert isinstance(result, SkillDenial)
        assert "not in registry" in result.reason

    def test_denied_unknown_skill(self, registry):
        """Unknown skill = denied."""
        result = resolve_skill("t-1", "campaigns", "campaigns:nonexistent")
        assert isinstance(result, SkillDenial)
        assert "not in registry" in result.reason

    def test_denied_no_binding(self, registry):
        """No binding = denied (three layers required)."""
        result = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(result, SkillDenial)
        assert "No binding" in result.reason

    def test_denied_agent_disabled_by_overlay(self, registry, binding_svc):
        """Agent disabled by overlay = denied even with binding."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        overlay = {"campaigns": {"enabled": False}}
        result = resolve_skill(
            "t-1", "campaigns", "campaigns:list-active",
            overlay_store=overlay,
        )
        assert isinstance(result, SkillDenial)
        assert "disabled by tenant overlay" in result.reason

    def test_denied_skill_disabled_by_overlay(self, registry, binding_svc):
        """Skill disabled by overlay = denied."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        overlay = {
            "campaigns": {
                "enabled": True,
                "skill_overrides": {
                    "campaigns:list-active": {"enabled": False},
                },
            }
        }
        result = resolve_skill(
            "t-1", "campaigns", "campaigns:list-active",
            overlay_store=overlay,
        )
        assert isinstance(result, SkillDenial)
        assert "disabled by tenant overlay" in result.reason

    def test_denied_binding_disabled(self, registry, binding_svc):
        """Disabled binding = denied."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            enabled=False,
        )
        result = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(result, SkillDenial)
        assert "disabled" in result.reason.lower()

    def test_resolved_with_all_three_layers(self, registry, binding_svc):
        """Full resolution: registry + overlay + binding = ResolvedSkill."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            credential_ref="vault://t-1/campaigns-key",
            mode="read",
            approval_policy="auto",
        )
        result = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(result, ResolvedSkill)
        assert result.skill_id == "campaigns:list-active"
        assert result.credential_ref == "vault://t-1/campaigns-key"
        assert result.mode == "read"
        assert result.enabled is True

    def test_overlay_mode_override_takes_precedence(self, registry, binding_svc):
        """Overlay mode_override > binding mode > base skill mode."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            mode="read",
        )
        overlay = {
            "campaigns": {
                "skill_overrides": {
                    "campaigns:list-active": {"mode_override": "mutate"},
                },
            }
        }
        result = resolve_skill(
            "t-1", "campaigns", "campaigns:list-active",
            overlay_store=overlay,
        )
        assert isinstance(result, ResolvedSkill)
        assert result.mode == "mutate"

    def test_resolution_cache(self, registry, binding_svc):
        """Results are cached (SPEC-1859 req 5)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        r1 = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(r1, ResolvedSkill)

        # Delete binding — cached result should still return resolved
        binding_svc.delete_binding("t-1", "campaigns", "campaigns:list-active")
        r2 = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(r2, ResolvedSkill)  # Still cached

        # Clear cache — should now be denied
        clear_resolution_cache()
        r3 = resolve_skill("t-1", "campaigns", "campaigns:list-active")
        assert isinstance(r3, SkillDenial)

    def test_list_available_skills_filters(self, registry, binding_svc):
        """list_available_skills returns only fully resolved skills (SPEC-1859 req 7)."""
        # Create binding for one skill only
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        clear_resolution_cache()
        available = list_available_skills("t-1", agent_id="campaigns")
        assert len(available) == 1
        assert available[0].skill_id == "campaigns:list-active"

    def test_list_available_skills_empty_without_bindings(self, registry):
        """No bindings = no available skills."""
        clear_resolution_cache()
        available = list_available_skills("t-1")
        assert len(available) == 0

    def test_list_available_skills_tier_filter_with_agent_id(self, registry, binding_svc):
        """list_available_skills enforces tier even when agent_id is specified (regression)."""
        # zendesk is professional-gated — create a binding for its actual skill
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="zendesk",
            skill_id="zendesk:sync-tickets",
        )
        # Starter tier should get zero skills from zendesk
        available = list_available_skills("t-1", agent_id="zendesk", tier="starter")
        assert len(available) == 0

        # Professional tier should get skills
        available = list_available_skills("t-1", agent_id="zendesk", tier="professional")
        ids = {s.skill_id for s in available}
        assert "zendesk:sync-tickets" in ids

    def test_list_available_skills_multiple_agents(self, registry, binding_svc):
        """list_available_skills across multiple agents."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        clear_resolution_cache()
        available = list_available_skills("t-1")
        ids = {s.skill_id for s in available}
        assert "campaigns:list-active" in ids
        assert "sales:search-products" in ids
        assert len(available) == 2


# ---------------------------------------------------------------------------
# SPEC-1860: KR MCP Migration
# ---------------------------------------------------------------------------


class TestKrMcpMigration:
    """SPEC-1860: KR migration to binding system."""

    def test_migrate_creates_base_binding(self, registry, binding_svc):
        """Migration creates base KR binding (SPEC-1860 req 2)."""
        results = migrate_tenant_kr_bindings("t-1")
        assert len(results) >= 1
        assert results[0]["skill_id"] == KR_SKILL_ID
        assert results[0]["agent_id"] == KR_AGENT_ID

    def test_migration_idempotent(self, registry, binding_svc):
        """Running migration twice produces same result (SPEC-1860 req 3)."""
        r1 = migrate_tenant_kr_bindings("t-1")
        r2 = migrate_tenant_kr_bindings("t-1")
        assert len(r1) == len(r2)

    def test_is_tenant_migrated(self, registry, binding_svc):
        """is_tenant_migrated checks for KR binding."""
        assert not is_tenant_migrated("t-1")
        migrate_tenant_kr_bindings("t-1")
        assert is_tenant_migrated("t-1")

    def test_resolve_with_fallback_legacy(self, registry, binding_svc):
        """Unmigrated tenant uses legacy path (SPEC-1860 req 5)."""
        result = resolve_kr_with_fallback("t-1", [{"name": "test"}])
        assert result["source"] == "legacy"

    def test_resolve_with_fallback_binding(self, registry, binding_svc):
        """Migrated tenant uses binding path."""
        migrate_tenant_kr_bindings("t-1")
        result = resolve_kr_with_fallback("t-1", [{"name": "test"}])
        assert result["source"] == "binding"
        assert result["binding"] is not None

    def test_migration_with_mcp_servers(self, registry, binding_svc):
        """Migration creates bindings for tenant MCP server tools."""
        mcp_servers = [
            {
                "name": "custom-search",
                "tools": ["semantic_search", "keyword_search"],
                "credential_ref": "vault://t-1/search-key",
            }
        ]
        results = migrate_tenant_kr_bindings("t-1", mcp_servers=mcp_servers)
        # Base binding + 2 tool bindings
        assert len(results) == 3


# ---------------------------------------------------------------------------
# Migration State Contract (Codex P1 finding)
# ---------------------------------------------------------------------------


class TestMigrationStateContract:
    """SPEC-1860: Explicit 3-state migration contract."""

    def test_migration_state_enum_values(self):
        """MigrationState has legacy_only, dual_read, binding_enforced."""
        assert MigrationState.LEGACY_ONLY.value == "legacy_only"
        assert MigrationState.DUAL_READ.value == "dual_read"
        assert MigrationState.BINDING_ENFORCED.value == "binding_enforced"

    def test_default_migration_state_is_legacy_only(self):
        """Default state for unknown tenants is legacy_only."""
        assert get_migration_state("unknown-tenant") == MigrationState.LEGACY_ONLY

    def test_migrate_sets_dual_read_state(self, registry, binding_svc):
        """migrate_tenant_kr_bindings() promotes state to dual_read."""
        assert get_migration_state("t-1") == MigrationState.LEGACY_ONLY
        migrate_tenant_kr_bindings("t-1")
        assert get_migration_state("t-1") == MigrationState.DUAL_READ

    def test_migrate_does_not_downgrade_binding_enforced(self, registry, binding_svc):
        """Re-running migration on binding_enforced tenant does not downgrade."""
        set_migration_state("t-1", MigrationState.BINDING_ENFORCED)
        migrate_tenant_kr_bindings("t-1")
        assert get_migration_state("t-1") == MigrationState.BINDING_ENFORCED

    def test_binding_enforced_blocks_legacy_path(self, registry, binding_svc):
        """binding_enforced tenant with no binding gets error, not legacy fallback."""
        set_migration_state("t-1", MigrationState.BINDING_ENFORCED)
        result = resolve_kr_with_fallback("t-1", [{"name": "test"}])
        assert result["source"] == "error"
        assert "binding_enforced" in result["error"]

    def test_binding_enforced_with_binding_succeeds(self, registry, binding_svc):
        """binding_enforced tenant with binding uses binding path."""
        migrate_tenant_kr_bindings("t-1")
        set_migration_state("t-1", MigrationState.BINDING_ENFORCED)
        result = resolve_kr_with_fallback("t-1", [{"name": "test"}])
        assert result["source"] == "binding"
        assert result["binding"] is not None

    def test_binding_enforced_does_not_passthrough_legacy_configs(self, registry, binding_svc):
        """binding_enforced configs derive from binding, not from caller's legacy configs."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id=KR_AGENT_ID, skill_id=KR_SKILL_ID,
            credential_ref="vault://t-1/kr-key", mode="read",
        )
        set_migration_state("t-1", MigrationState.BINDING_ENFORCED)
        legacy_configs = [{"name": "shopify", "server_url": "https://shop.myshopify.com/mcp"}]
        result = resolve_kr_with_fallback("t-1", legacy_configs)
        assert result["source"] == "binding"
        # Configs must NOT be the legacy passthrough
        assert result["mcp_configs"] != legacy_configs
        # Configs must derive from binding credential_ref
        assert any(c.get("credential_ref") == "vault://t-1/kr-key" for c in result["mcp_configs"])

    def test_legacy_path_emits_audit_event(self, registry, binding_svc):
        """Legacy path usage emits an audit event."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        resolve_kr_with_fallback("t-1", [{"name": "test"}])

        events = bus.get_buffered_events()
        assert len(events) == 1
        assert events[0].result_class == "legacy_fallback"
        assert events[0].policy_verdict == "legacy_only"

    def test_dual_read_fallback_emits_audit_event(self, registry, binding_svc):
        """dual_read fallback to legacy emits audit event."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        # Set dual_read but don't create binding
        set_migration_state("t-1", MigrationState.DUAL_READ)
        result = resolve_kr_with_fallback("t-1", [{"name": "test"}])
        assert result["source"] == "legacy"

        events = bus.get_buffered_events()
        assert len(events) == 1
        assert events[0].policy_verdict == "dual_read_fallback"


# ---------------------------------------------------------------------------
# Runtime wiring: agent_dispatch calls resolve_kr_with_fallback (Codex P1)
# ---------------------------------------------------------------------------


class TestKrRuntimeWiring:
    """Verify resolve_kr_with_fallback() is wired into the live dispatch path."""

    def test_resolve_kr_wired_in_agent_dispatch(self):
        """agent_dispatch._resolve_kr_mcp_payload calls resolve_kr_with_fallback."""
        import inspect
        from src.chat.pipeline import agent_dispatch
        source = inspect.getsource(agent_dispatch)
        assert "resolve_kr_with_fallback" in source, (
            "resolve_kr_with_fallback must be called in agent_dispatch.py"
        )

    def test_binding_enforced_blocks_mcp_in_dispatch(self, registry, binding_svc):
        """binding_enforced tenant gets empty mcp_configs from dispatch helper."""
        set_migration_state("t-1", MigrationState.BINDING_ENFORCED)

        # Simulate the dispatch helper by calling resolve_kr_with_fallback
        # with some MCP configs — should return error, not the configs
        result = resolve_kr_with_fallback("t-1", [{"name": "shopify", "tools": ["search"]}])
        assert result["source"] == "error"
        assert result["mcp_configs"] == []

    def test_legacy_tenant_gets_mcp_configs(self, registry, binding_svc):
        """legacy_only tenant still receives MCP configs (backward compat)."""
        configs = [{"name": "shopify", "tools": ["search"]}]
        result = resolve_kr_with_fallback("t-1", configs)
        assert result["source"] == "legacy"
        assert result["mcp_configs"] == configs

    def test_migrated_tenant_gets_binding_path(self, registry, binding_svc):
        """dual_read tenant with binding uses binding-derived configs."""
        migrate_tenant_kr_bindings("t-1")
        legacy_configs = [{"name": "shopify", "tools": ["search"]}]
        result = resolve_kr_with_fallback("t-1", legacy_configs)
        assert result["source"] == "binding"
        # Binding source returns binding-derived configs, not legacy passthrough
        assert result["mcp_configs"] != legacy_configs

    @pytest.mark.asyncio
    async def test_http_fallback_receives_resolved_mcp_payload(self, monkeypatch):
        """HTTP fallback reuses the migration-resolved KR payload."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        import src.multi_tenant.otel_tracing as otel_tracing

        class _DummySpan:
            def set_attribute(self, *_args, **_kwargs) -> None:
                pass

            def set_status(self, *_args, **_kwargs) -> None:
                pass

            def end(self) -> None:
                pass

        monkeypatch.setattr(
            otel_tracing,
            "trace_agent_operation",
            lambda *_args, **_kwargs: _DummySpan(),
        )

        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        mixin._transport_available = lambda: False
        mixin._warn_http_failure_mode = lambda _agent: None
        mixin._resolve_kr_mcp_payload = lambda: {
            "mcp_configs": [{"name": "shopify", "tools": ["search"]}],
            "tenant_shop_domain": "example.myshopify.com",
            "kr_source": "legacy",
        }

        captured: dict[str, Any] = {}

        async def _fake_http(payload: dict[str, Any]) -> dict[str, Any]:
            captured.update(payload)
            return {"context": "ok"}

        mixin._call_knowledge_retrieval_http = _fake_http

        result = await mixin._call_knowledge_retrieval("hello", "order_status", "prompt")
        assert result == {"context": "ok"}
        assert captured["mcp_configs"] == [{"name": "shopify", "tools": ["search"]}]
        assert captured["tenant_shop_domain"] == "example.myshopify.com"

    @pytest.mark.asyncio
    async def test_http_helper_posts_full_payload(self):
        """HTTP helper posts the already-resolved payload, including MCP fields."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        captured: dict[str, Any] = {}

        class _DummyResponse:
            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict[str, Any]:
                return {"context": "ok"}

        class _DummyClient:
            async def post(self, url: str, **kwargs: Any) -> _DummyResponse:
                captured["url"] = url
                captured["json"] = kwargs["json"]
                return _DummyResponse()

        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        mixin._agent_urls = {"knowledge-retrieval": "http://kr"}

        async def _get_http_client() -> _DummyClient:
            return _DummyClient()

        mixin._get_http_client = _get_http_client

        payload = {
            "message": "hello",
            "intent": "order_status",
            "system_prompt": "prompt",
            "mcp_configs": [{"name": "shopify", "tools": ["search"]}],
            "tenant_shop_domain": "example.myshopify.com",
        }
        result = await mixin._call_knowledge_retrieval_http(payload)

        assert result == {"context": "ok"}
        assert captured["url"] == "http://kr/retrieve"
        assert captured["json"] == payload
