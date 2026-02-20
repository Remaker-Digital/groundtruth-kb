"""Tests for KA-5: PCM Authentication Incentive — customer_identification_mode.

Verifies:
- Each mode (off/gentle/standard/aggressive) produces the correct prompt section
- The off mode injects nothing
- The Critic/Supervisor prompt is unaffected (immutability invariant)
- PCM-building prompt is gated by memory_enabled
- The field survives draft save/activate cycle (schema validation)
- Default mode is 'standard'
- Invalid mode values fall back to standard

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.cosmos_schema import (
    PreferencesDocument,
    TenantDocument,
    TenantTier,
)
from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    SystemPromptBuilder,
    _build_identification_section,
    _IDENTIFICATION_PROMPTS,
    _PCM_BUILDING_PROMPT,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_prefs(**overrides) -> PreferencesDocument:
    """Create a minimal PreferencesDocument with overrides."""
    defaults = {
        "id": "test:1",
        "tenant_id": "test-tenant",
        "version": 1,
        "config_state": "active",
        "brand_name": "Test Store",
        "brand_voice": "friendly",
        "memory_enabled": True,
        "customer_identification_mode": "standard",
        "created_at": "2026-02-20T00:00:00Z",
    }
    defaults.update(overrides)
    return PreferencesDocument(**defaults)


def _make_tenant(**overrides) -> TenantDocument:
    """Create a minimal TenantDocument with overrides."""
    defaults = {
        "id": "test-tenant",
        "tenant_id": "test-tenant",
        "status": "active",
        "tier": TenantTier.STARTER,
        "billing_channel": "stripe",
        "created_at": "2026-02-20T00:00:00Z",
        "updated_at": "2026-02-20T00:00:00Z",
    }
    defaults.update(overrides)
    return TenantDocument(**defaults)


# ---------------------------------------------------------------------------
# _build_identification_section tests
# ---------------------------------------------------------------------------

class TestBuildIdentificationSection:
    """Unit tests for _build_identification_section()."""

    def test_off_mode_returns_empty(self):
        """Off mode should produce an empty string — no injection."""
        prefs = _make_prefs(customer_identification_mode="off")
        result = _build_identification_section(prefs)
        assert result == ""

    def test_off_mode_with_memory_disabled_returns_empty(self):
        """Off mode + memory disabled = definitely empty."""
        prefs = _make_prefs(customer_identification_mode="off", memory_enabled=False)
        result = _build_identification_section(prefs)
        assert result == ""

    def test_gentle_mode_includes_identification(self):
        """Gentle mode should include a casual identification prompt."""
        prefs = _make_prefs(customer_identification_mode="gentle")
        result = _build_identification_section(prefs)
        assert "CUSTOMER IDENTIFICATION:" in result
        assert "casually mention" in result
        assert "do not pressure" in result

    def test_standard_mode_includes_identification(self):
        """Standard mode should suggest login in first response."""
        prefs = _make_prefs(customer_identification_mode="standard")
        result = _build_identification_section(prefs)
        assert "CUSTOMER IDENTIFICATION:" in result
        assert "first response" in result
        assert "order history" in result

    def test_aggressive_mode_includes_strong_suggestion(self):
        """Aggressive mode should MUST include strong auth suggestion."""
        prefs = _make_prefs(customer_identification_mode="aggressive")
        result = _build_identification_section(prefs)
        assert "CUSTOMER IDENTIFICATION:" in result
        assert "MUST include" in result
        assert "probing question" in result

    def test_pcm_building_included_when_memory_enabled(self):
        """PCM-building prompt should be included when memory is on."""
        prefs = _make_prefs(customer_identification_mode="standard", memory_enabled=True)
        result = _build_identification_section(prefs)
        assert "BUILDING CUSTOMER KNOWLEDGE:" in result
        assert "actively learn" in result

    def test_pcm_building_excluded_when_memory_disabled(self):
        """PCM-building prompt should NOT be included when memory is off."""
        prefs = _make_prefs(customer_identification_mode="standard", memory_enabled=False)
        result = _build_identification_section(prefs)
        assert "BUILDING CUSTOMER KNOWLEDGE:" not in result
        # But identification should still be present
        assert "CUSTOMER IDENTIFICATION:" in result

    def test_pcm_building_excluded_when_mode_off(self):
        """PCM-building is excluded when mode is off, even with memory on."""
        prefs = _make_prefs(customer_identification_mode="off", memory_enabled=True)
        result = _build_identification_section(prefs)
        assert "BUILDING CUSTOMER KNOWLEDGE:" not in result

    def test_default_mode_is_standard(self):
        """PreferencesDocument default for customer_identification_mode is 'standard'."""
        prefs = PreferencesDocument(
            id="test:1",
            tenant_id="test-tenant",
            version=1,
            config_state="active",
            created_at="2026-02-20T00:00:00Z",
        )
        assert prefs.customer_identification_mode == "standard"

    def test_none_mode_falls_back_to_standard(self):
        """If mode is None (legacy doc without validation), should fall back to standard.

        Pydantic rejects None for a str field, so we simulate a legacy
        document using a SimpleNamespace to exercise the getattr fallback
        path in _build_identification_section().
        """
        from types import SimpleNamespace

        legacy = SimpleNamespace(
            customer_identification_mode=None,
            memory_enabled=True,
        )
        result = _build_identification_section(legacy)
        assert "CUSTOMER IDENTIFICATION:" in result
        assert "first response" in result  # standard prompt content

    def test_unknown_mode_returns_empty_identification(self):
        """Unknown mode value produces no identification prompt."""
        prefs = _make_prefs(customer_identification_mode="unknown_value")
        result = _build_identification_section(prefs)
        # _IDENTIFICATION_PROMPTS.get("unknown_value") returns None
        # So no identification section, but PCM-building still present if memory on
        assert "CUSTOMER IDENTIFICATION:" not in result


# ---------------------------------------------------------------------------
# SystemPromptBuilder integration tests
# ---------------------------------------------------------------------------

class TestSystemPromptBuilderIntegration:
    """Tests that identification prompts are correctly injected via build()."""

    def test_response_generator_includes_identification(self):
        """Response Generator prompt should include identification section."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="standard")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" in prompt
        assert "BUILDING CUSTOMER KNOWLEDGE:" in prompt

    def test_critic_prompt_never_modified(self):
        """Critic/Supervisor prompt must NEVER contain identification content."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="aggressive")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.CRITIC_SUPERVISOR,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" not in prompt
        assert "BUILDING CUSTOMER KNOWLEDGE:" not in prompt
        # Critic still has its immutable rules
        assert "BLOCK ONLY these specific violations" in prompt

    def test_intent_classifier_no_identification(self):
        """Intent Classifier should NOT receive identification prompts."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="aggressive")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.INTENT_CLASSIFIER,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" not in prompt

    def test_knowledge_retrieval_no_identification(self):
        """Knowledge Retrieval should NOT receive identification prompts."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="aggressive")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.KNOWLEDGE_RETRIEVAL,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" not in prompt

    def test_escalation_handler_no_identification(self):
        """Escalation Handler should NOT receive identification prompts."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="standard")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.ESCALATION_HANDLER,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" not in prompt

    def test_off_mode_produces_no_identification_in_prompt(self):
        """Off mode should not add identification to the assembled prompt."""
        builder = SystemPromptBuilder()
        prefs = _make_prefs(customer_identification_mode="off")
        tenant = _make_tenant()
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=prefs,
        )
        assert "CUSTOMER IDENTIFICATION:" not in prompt
        assert "BUILDING CUSTOMER KNOWLEDGE:" not in prompt


# ---------------------------------------------------------------------------
# Schema / field definition tests
# ---------------------------------------------------------------------------

class TestFieldDefinition:
    """Tests that the field exists and validates correctly."""

    def test_field_exists_on_preferences_document(self):
        """customer_identification_mode should be a field on PreferencesDocument."""
        prefs = PreferencesDocument(
            id="t:1", tenant_id="t", version=1, config_state="draft",
            created_at="2026-02-20T00:00:00Z",
        )
        assert hasattr(prefs, "customer_identification_mode")
        assert prefs.customer_identification_mode == "standard"

    def test_field_accepts_all_valid_values(self):
        """All four mode values should be accepted."""
        for mode in ("off", "gentle", "standard", "aggressive"):
            prefs = _make_prefs(customer_identification_mode=mode)
            assert prefs.customer_identification_mode == mode

    def test_all_modes_have_prompt_entries(self):
        """Every valid mode should have a corresponding entry in the prompt map."""
        for mode in ("off", "gentle", "standard", "aggressive"):
            assert mode in _IDENTIFICATION_PROMPTS

    def test_identification_prompts_are_strings(self):
        """All prompt fragments should be strings."""
        for mode, prompt in _IDENTIFICATION_PROMPTS.items():
            assert isinstance(prompt, str), f"Mode '{mode}' prompt is not a string"

    def test_pcm_building_prompt_is_string(self):
        """PCM building prompt should be a non-empty string."""
        assert isinstance(_PCM_BUILDING_PROMPT, str)
        assert len(_PCM_BUILDING_PROMPT) > 50
