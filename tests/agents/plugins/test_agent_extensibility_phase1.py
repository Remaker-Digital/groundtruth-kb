"""Phase 1 Agent Extensibility Tests (SPEC-1856, SPEC-1857, SPEC-1858).

Tests for agent skill bindings, deny-by-default enforcement, and
credential scoping.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.dispatch import PluginDispatcher
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.registry import PluginAgentRegistry


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset singletons between tests."""
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()
    yield
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()


@pytest.fixture
def binding_svc():
    return SkillBindingService.get_instance()


@pytest.fixture
def registry():
    reg = PluginAgentRegistry.get_instance()
    reg.load_from_yaml()
    return reg


# ---------------------------------------------------------------------------
# SPEC-1856: Agent Skill Binding Model
# ---------------------------------------------------------------------------


class TestAgentSkillBinding:
    """SPEC-1856: Explicit bindings connect tenant to agent skills."""

    def test_create_binding(self, binding_svc):
        """Can create a skill binding."""
        b = binding_svc.create_binding(
            tenant_id="t-1",
            agent_id="campaigns",
            skill_id="campaigns:list-active",
            credential_ref="vault://t-1/campaigns-key",
            mode="read",
        )
        assert b["tenant_id"] == "t-1"
        assert b["skill_id"] == "campaigns:list-active"
        assert b["credential_ref"] == "vault://t-1/campaigns-key"

    def test_get_binding(self, binding_svc):
        """Can retrieve a binding by key."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products", mode="read",
        )
        b = binding_svc.get_binding("t-1", "sales", "sales:search-products")
        assert b is not None
        assert b["mode"] == "read"

    def test_get_binding_not_found(self, binding_svc):
        """Returns None for nonexistent binding."""
        assert binding_svc.get_binding("t-1", "x", "x:y") is None

    def test_list_bindings_for_tenant(self, binding_svc):
        """List bindings filtered by tenant."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        binding_svc.create_binding(
            tenant_id="t-2", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        assert len(binding_svc.list_bindings("t-1")) == 2
        assert len(binding_svc.list_bindings("t-2")) == 1

    def test_list_bindings_by_agent(self, binding_svc):
        """List bindings filtered by agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        assert len(binding_svc.list_bindings("t-1", agent_id="campaigns")) == 1

    def test_delete_binding(self, binding_svc):
        """Can delete a binding."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        assert binding_svc.delete_binding("t-1", "campaigns", "campaigns:list-active")
        assert binding_svc.get_binding("t-1", "campaigns", "campaigns:list-active") is None

    def test_delete_nonexistent_returns_false(self, binding_svc):
        """Deleting nonexistent binding returns False."""
        assert not binding_svc.delete_binding("t-1", "x", "x:y")

    def test_list_bindings_by_credential(self, binding_svc):
        """Can find all bindings using a specific credential (SPEC-1858 req 6)."""
        cred = "vault://t-1/shopify-key"
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
            credential_ref=cred,
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:manage-cart",
            credential_ref=cred,
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:check-inventory",
            credential_ref="vault://t-1/other-key",
        )
        results = binding_svc.list_bindings_by_credential(cred)
        assert len(results) == 2


# ---------------------------------------------------------------------------
# SPEC-1857: Deny-by-Default Enforcement
# ---------------------------------------------------------------------------


class TestDenyByDefault:
    """SPEC-1857: No tool call proceeds without an active binding."""

    def test_no_binding_denied(self, binding_svc):
        """Missing binding = denied (SPEC-1857 req 2)."""
        check = binding_svc.check_binding("t-1", "campaigns", "campaigns:list-active")
        assert check.denied
        assert check.policy_verdict == "denied_by_binding"

    def test_disabled_binding_denied(self, binding_svc):
        """Disabled binding = denied (SPEC-1857 req 2)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            enabled=False,
        )
        check = binding_svc.check_binding("t-1", "campaigns", "campaigns:list-active")
        assert check.denied
        assert check.policy_verdict == "denied_by_binding"

    def test_read_binding_denies_mutate(self, binding_svc):
        """Read-only binding denies mutate mode (SPEC-1857 req 3)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:track-metrics",
            mode="read",
        )
        check = binding_svc.check_binding(
            "t-1", "campaigns", "campaigns:track-metrics",
            required_mode="mutate",
        )
        assert check.denied
        assert check.policy_verdict == "denied_by_mode"

    def test_mutate_binding_allows_mutate(self, binding_svc):
        """Mutate binding allows mutate mode."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:track-metrics",
            mode="mutate",
        )
        check = binding_svc.check_binding(
            "t-1", "campaigns", "campaigns:track-metrics",
            required_mode="mutate",
        )
        assert check.allowed
        assert check.policy_verdict == "allowed"

    def test_active_binding_allowed(self, binding_svc):
        """Active enabled binding = allowed."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            mode="read",
        )
        check = binding_svc.check_binding("t-1", "campaigns", "campaigns:list-active")
        assert check.allowed

    def test_get_bound_skill_ids(self, binding_svc):
        """get_bound_skill_ids returns only enabled bindings (SPEC-1857 req 5)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:get-discount-codes",
            enabled=False,
        )
        ids = binding_svc.get_bound_skill_ids("t-1")
        assert "campaigns:list-active" in ids
        assert "campaigns:get-discount-codes" not in ids

    @pytest.mark.asyncio
    async def test_dispatch_with_binding_denied(self, registry, binding_svc):
        """Dispatcher rejects unbound tool calls (SPEC-1857 req 2)."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        dispatcher = PluginDispatcher(registry=registry)
        result = await dispatcher.dispatch_with_binding(
            "campaigns.list_active",
            {"query": "summer"},
            tenant_id="t-1",
            agent_id="campaigns",
            skill_id="campaigns:list-active",
            conversation_id="c-1",
        )
        assert not result.success
        assert result.metadata["policy_verdict"] == "denied_by_binding"

        # SPEC-1857 req 6: Denial event emitted
        events = bus.get_buffered_events()
        assert len(events) == 1
        assert events[0].result_class == "denied"

    @pytest.mark.asyncio
    async def test_dispatch_with_binding_allowed(self, registry, binding_svc):
        """Dispatcher allows bound tool calls."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            credential_ref="vault://t-1/key",
            mode="read",
        )
        dispatcher = PluginDispatcher(registry=registry)
        result = await dispatcher.dispatch_with_binding(
            "campaigns.list_active",
            {"query": "summer"},
            tenant_id="t-1",
            agent_id="campaigns",
            skill_id="campaigns:list-active",
            conversation_id="c-1",
        )
        assert result.success
        assert result.metadata["policy_verdict"] == "allowed"
        assert result.metadata["credential_ref"] == "vault://t-1/key"


# ---------------------------------------------------------------------------
# SPEC-1858: Credential Scoping
# ---------------------------------------------------------------------------


class TestCredentialScoping:
    """SPEC-1858: Credentials scoped to agent-skill bindings."""

    def test_credential_from_binding(self, binding_svc):
        """Credential resolved from binding, not global config (SPEC-1858 req 2)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="stripe_mcp",
            skill_id="stripe_mcp:get-balance",
            credential_ref="vault://t-1/stripe-oauth",
            mode="read",
        )
        cred = binding_svc.resolve_credential(
            "t-1", "stripe_mcp", "stripe_mcp:get-balance"
        )
        assert cred == "vault://t-1/stripe-oauth"

    def test_no_binding_no_credential(self, binding_svc):
        """No binding = no credential (SPEC-1858 req 4)."""
        cred = binding_svc.resolve_credential("t-1", "stripe_mcp", "stripe_mcp:get-balance")
        assert cred is None

    def test_shared_credential_across_bindings(self, binding_svc):
        """Same credential used by multiple bindings (SPEC-1858 req 3)."""
        shared_cred = "vault://t-1/shopify-api"
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
            credential_ref=shared_cred,
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:manage-cart",
            credential_ref=shared_cred,
        )
        assert binding_svc.resolve_credential("t-1", "sales", "sales:search-products") == shared_cred
        assert binding_svc.resolve_credential("t-1", "sales", "sales:manage-cart") == shared_cred

    def test_binding_check_includes_credential(self, binding_svc):
        """Binding check result includes credential_ref."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="campaigns",
            skill_id="campaigns:list-active",
            credential_ref="vault://t-1/campaigns-key",
        )
        check = binding_svc.check_binding("t-1", "campaigns", "campaigns:list-active")
        assert check.allowed
        assert check.credential_ref == "vault://t-1/campaigns-key"
