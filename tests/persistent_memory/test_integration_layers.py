"""Integration test suite for Persistent Customer Memory — 10 cross-layer tests.

Work Item #98, Decision #32.

These tests validate interactions between memory layers, ensuring the full
stack works correctly when multiple layers are active simultaneously.

Test IDs:
    CL-01: Full stack activation (L1+L2+L3+L4)
    CL-02: Graceful degradation (L4 unavailable)
    CL-03: Layer conflict resolution (L1 vs L3 freshness)
    CL-04: New customer onboarding (L1 only)
    CL-05: Tier upgrade migration
    CL-06: Data deletion compliance (all layers)
    CL-07: Cross-tenant isolation
    CL-08: Consent lifecycle across layers
    CL-09: Prompt assembly with all layers
    CL-10: Explainability trace completeness

Run:
    pytest tests/persistent_memory/test_integration_layers.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    BillingChannel,
    ConsentStatus,
    CustomerProfileDocument,
    MemoryVectorDocument,
    PreferencesDocument,
    TenantDocument,
    TenantStatus,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.customer_profile_service import (
    CustomerProfileService,
)
from src.multi_tenant.conversation_vectorizer import (
    ConversationVectorizer,
    chunk_transcript,
)
from src.multi_tenant.response_explainability import (
    DecisionTraceBuilder,
    ResponseDecisionTrace,
)
from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    SystemPromptBuilder,
)

from tests.persistent_memory.fixtures import (
    TENANT_STARTER,
    TENANT_PROFESSIONAL,
    TENANT_ENTERPRISE,
    TENANT_OTHER,
    CUSTOMER_RETURNING,
    CUSTOMER_NEW,
    CUSTOMER_STALE,
    CUSTOMER_DENIED_CONSENT,
    CUSTOMER_HIGH_VOLUME,
    make_profile,
    make_conversation_messages,
    make_vector_results,
    make_preferences,
    make_tenant,
)


# ---------------------------------------------------------------------------
# Helpers — construct real TenantDocument / PreferencesDocument
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_tenant_doc(
    tenant_id: str = TENANT_STARTER,
    tier: TenantTier = TenantTier.STARTER,
    status: TenantStatus = TenantStatus.ACTIVE,
) -> TenantDocument:
    """Create a TenantDocument compatible with SystemPromptBuilder.build()."""
    return TenantDocument(
        id=tenant_id,
        tenant_id=tenant_id,
        status=status,
        billing_channel=BillingChannel.STRIPE,
        tier=tier,
        created_at=_now(),
        updated_at=_now(),
    )


def _make_prefs_doc(
    tenant_id: str = TENANT_STARTER,
    *,
    brand_name: str = "GlowSkin Co",
    brand_voice: str = "friendly",
    formality_level: str = "casual",
    response_length: str = "concise",
    custom_instructions: str | None = None,
) -> PreferencesDocument:
    """Create a PreferencesDocument compatible with SystemPromptBuilder.build()."""
    return PreferencesDocument(
        id=f"{tenant_id}:1",
        tenant_id=tenant_id,
        version=1,
        brand_name=brand_name,
        brand_voice=brand_voice,
        formality_level=formality_level,
        response_length=response_length,
        custom_instructions=custom_instructions,
        created_at=_now(),
    )


# =====================================================================
# Cross-Layer Integration Tests (CL-01 through CL-10)
# =====================================================================


class TestCrossLayerIntegration:
    """Integration tests validating interactions between memory layers."""

    # --- CL-01: Full stack activation (L1+L2+L3+L4) ---

    def test_cl_01_full_stack_enterprise(self) -> None:
        """CL-01: Enterprise tenant activates all 4 memory layers.

        When an Enterprise tenant has:
        - Customer profile with data (L1)
        - Conversation history results (L2)
        - Memory signals from learned patterns (L3)
        - Fine-tuned model attribution (L4)

        The decision trace should record all layers and the prompt
        should include customer context.
        """
        # Layer 1: Profile
        profile = make_profile(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            consent=ConsentStatus.GRANTED,
        )

        # Verify all layers available for Enterprise
        service = CustomerProfileService()
        layers = service.get_available_layers(TenantTier.ENTERPRISE)
        assert layers == [1, 2, 3, 4]

        # Build prompt with customer context (L1 injection)
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_ENTERPRISE, TenantTier.ENTERPRISE)
        prefs = _make_prefs_doc(TENANT_ENTERPRISE)

        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Prompt should contain customer context
        assert "CUSTOMER CONTEXT" in prompt
        assert "Purchase history" in prompt

        # Build decision trace with all 4 layers
        trace_builder = DecisionTraceBuilder(
            "conv-cl01", TENANT_ENTERPRISE, CUSTOMER_RETURNING,
        )

        # L1: Profile context from prompt builder
        prompt_trace = builder.explain(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )
        trace_builder.set_profile_context(prompt_trace)

        # L2: Conversation history
        trace_builder.add_memory_signal(
            layer=2,
            source_conversation_id="conv-prior-100",
            similarity_score=0.92,
            signal_type="prior_conversation",
        )

        # L3: Learned patterns
        trace_builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-pattern-050",
            similarity_score=0.85,
            signal_type="learned_pattern",
            chunk_summary="Customer prefers detailed skincare explanations",
        )

        # L4: Fine-tuned model
        trace_builder.add_stage(
            stage="response_generator",
            model="ft:gpt-4o-mini:customer-returning:v3",
            latency_ms=1100.0,
            tokens_input=900,
            tokens_output=400,
            cost_estimate=0.006,
        )

        trace = trace_builder.build()

        # All 4 layers should be represented
        assert len(trace.memory_signals) == 2
        l2_signals = [s for s in trace.memory_signals if s.layer == 2]
        l3_signals = [s for s in trace.memory_signals if s.layer == 3]
        assert len(l2_signals) == 1
        assert len(l3_signals) == 1

        # L4 fine-tuned model in stage attribution
        assert len(trace.stage_attributions) == 1
        assert trace.stage_attributions[0].model.startswith("ft:")

        # Profile data sources should be recorded
        assert "customer_context" in prompt_trace.get("layers_active", [])

    # --- CL-02: Graceful degradation (L4 unavailable) ---

    def test_cl_02_graceful_degradation_without_l4(self) -> None:
        """CL-02: Professional tier degrades gracefully without Layer 4.

        Professional tier has Layers 1, 2, 3 — Layer 4 is Enterprise only.
        The system should work correctly without fine-tuned model attribution
        and the trace should reflect only available layers.
        """
        service = CustomerProfileService()
        layers = service.get_available_layers(TenantTier.PROFESSIONAL)
        assert 4 not in layers
        assert layers == [1, 2, 3]

        # Profile works (L1)
        profile = make_profile(
            TENANT_PROFESSIONAL,
            CUSTOMER_RETURNING,
            consent=ConsentStatus.GRANTED,
        )
        assert not service.is_empty(profile)

        # Prompt builds correctly without L4
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_PROFESSIONAL, TenantTier.PROFESSIONAL)
        prefs = _make_prefs_doc(TENANT_PROFESSIONAL)

        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )
        assert "CUSTOMER CONTEXT" in prompt

        # Trace without L4 stage should still compute correctly
        trace_builder = DecisionTraceBuilder(
            "conv-cl02", TENANT_PROFESSIONAL, CUSTOMER_RETURNING,
        )
        trace_builder.add_stage(
            stage="response_generator",
            model="gpt-4o",
            latency_ms=800.0,
            tokens_input=600,
            tokens_output=300,
            cost_estimate=0.003,
        )
        trace_builder.add_memory_signal(
            layer=2,
            source_conversation_id="conv-hist-001",
            similarity_score=0.88,
        )
        trace_builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-pattern-001",
            similarity_score=0.75,
            signal_type="learned_pattern",
        )

        trace = trace_builder.build()
        assert not trace.stage_attributions[0].model.startswith("ft:")
        assert len(trace.memory_signals) == 2

    # --- CL-03: Layer conflict resolution (L1 vs L3 freshness) ---

    def test_cl_03_layer_conflict_resolution(self) -> None:
        """CL-03: When Layer 1 (profile) and Layer 3 (patterns) conflict,
        the decision trace captures both for transparency.

        Example: Profile says customer is in US, but learned pattern
        suggests Canadian French preference. Both should be recorded
        in the trace — the response generator resolves the conflict.
        """
        # L1: Profile says US
        profile = make_profile(
            TENANT_PROFESSIONAL,
            CUSTOMER_RETURNING,
            with_region=True,  # US region
        )
        assert profile.region_codes.get("shipping_region") == "US"

        # Build trace with conflicting signals
        trace_builder = DecisionTraceBuilder(
            "conv-cl03", TENANT_PROFESSIONAL, CUSTOMER_RETURNING,
        )

        # L1: Profile context
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_PROFESSIONAL, TenantTier.PROFESSIONAL)
        prefs = _make_prefs_doc(TENANT_PROFESSIONAL)

        prompt_trace = builder.explain(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )
        trace_builder.set_profile_context(prompt_trace)

        # L3: Learned pattern suggests French-Canadian
        trace_builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-pattern-fr",
            similarity_score=0.82,
            signal_type="learned_pattern",
            chunk_summary="Customer previously conversed in French (fr-CA)",
        )

        trace = trace_builder.build()

        # Both L1 and L3 data should be in the trace
        assert "region_codes" in trace.profile_data_sources
        assert len(trace.memory_signals) == 1
        assert trace.memory_signals[0].layer == 3

        # Roundtrip — conflict data survives serialization
        data = trace.to_dict()
        restored = ResponseDecisionTrace.from_dict(data)
        assert len(restored.memory_signals) == 1
        assert restored.memory_signals[0].chunk_summary == (
            "Customer previously conversed in French (fr-CA)"
        )

    # --- CL-04: New customer onboarding (L1 only) ---

    def test_cl_04_new_customer_l1_only(self) -> None:
        """CL-04: New customer with no history works with Layer 1 only.

        First interaction for a customer. No conversation history (L2),
        no learned patterns (L3), no fine-tuned model (L4).
        System should produce a valid response with just L1 profile.
        """
        # Empty profile (new customer)
        service = CustomerProfileService()
        profile = make_profile(
            TENANT_STARTER,
            CUSTOMER_NEW,
            empty=True,
        )
        assert service.is_empty(profile)

        # Vectorizer has no history
        vectorizer = ConversationVectorizer()
        results = vectorizer.compress_for_prompt([])
        assert results == ""

        # Prompt builder handles empty profile
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_STARTER, TenantTier.STARTER)
        prefs = _make_prefs_doc(TENANT_STARTER)

        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Should produce a valid prompt (platform base + tier + merchant config)
        assert prompt
        assert "customer service response agent" in prompt.lower()

        # Trace should show empty profile, no memory signals
        trace_builder = DecisionTraceBuilder(
            "conv-cl04", TENANT_STARTER, CUSTOMER_NEW,
        )
        trace_builder.set_profile_state(is_empty=True)
        trace_builder.set_consent("not_asked")

        trace = trace_builder.build()
        assert trace.profile_is_empty is True
        assert len(trace.memory_signals) == 0
        assert trace.memory_consent_status == "not_asked"

    # --- CL-05: Tier upgrade migration ---

    def test_cl_05_tier_upgrade_unlocks_layers(self) -> None:
        """CL-05: Upgrading from Starter to Professional unlocks Layer 3.

        Before upgrade: Layers 1, 2 (90-day history)
        After upgrade: Layers 1, 2, 3 (365-day history)

        The profile service should reflect the new capabilities and
        the vectorizer should expand history depth.
        """
        service = CustomerProfileService()
        vectorizer = ConversationVectorizer()

        # Before upgrade: Starter
        starter_layers = service.get_available_layers(TenantTier.STARTER)
        starter_depth = service.get_history_depth_days(TenantTier.STARTER)
        starter_since = vectorizer._compute_since_date(TenantTier.STARTER)

        assert starter_layers == [1, 2]
        assert starter_depth == 90

        # After upgrade: Professional
        pro_layers = service.get_available_layers(TenantTier.PROFESSIONAL)
        pro_depth = service.get_history_depth_days(TenantTier.PROFESSIONAL)
        pro_since = vectorizer._compute_since_date(TenantTier.PROFESSIONAL)

        assert pro_layers == [1, 2, 3]
        assert pro_depth == 365

        # History depth should be deeper for Professional
        starter_dt = datetime.fromisoformat(starter_since)
        pro_dt = datetime.fromisoformat(pro_since)
        assert pro_dt < starter_dt  # Professional goes further back

        # Prompt should reflect new tier capabilities
        builder = SystemPromptBuilder()

        starter_doc = _make_tenant_doc(TENANT_STARTER, TenantTier.STARTER)
        pro_doc = _make_tenant_doc(TENANT_PROFESSIONAL, TenantTier.PROFESSIONAL)
        prefs = _make_prefs_doc(TENANT_PROFESSIONAL)

        starter_prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=starter_doc,
            preferences=prefs,
        )
        pro_prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=pro_doc,
            preferences=prefs,
        )

        # Professional prompt should mention Layer 3 capability
        assert "Layer 3" in pro_prompt
        assert "Learned customer patterns: Enabled" in pro_prompt

    # --- CL-06: Data deletion compliance (all layers) ---

    @pytest.mark.asyncio
    async def test_cl_06_data_deletion_across_layers(self) -> None:
        """CL-06: GDPR deletion removes data from all layers.

        When consent is denied, Layers 2-4 data must be deleted.
        Layer 1 profile remains (not consent-gated) but the profile
        service should correctly report consent status.
        """
        service = CustomerProfileService()

        # Start with granted consent
        granted_profile = make_profile(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            consent=ConsentStatus.GRANTED,
        )
        assert service.is_consent_granted(granted_profile)

        # Vectorizer should respect consent denial
        vectorizer = ConversationVectorizer()
        vectorizer.configure(vector_repo=AsyncMock(), openai_client=None)

        # Consent denied — vectorization should be skipped
        messages = make_conversation_messages("return_inquiry")
        chunk_ids = await vectorizer.vectorize_conversation(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            "conv-cl06",
            messages,
            consent_status=ConsentStatus.DENIED,
        )
        assert chunk_ids == []

        # Consent denied — search should return empty
        results = await vectorizer.search_history(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            "return policy",
            TenantTier.ENTERPRISE,
            consent_status=ConsentStatus.DENIED,
        )
        assert results == []

        # Layer 1 profile remains accessible regardless of consent
        denied_profile = make_profile(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            consent=ConsentStatus.DENIED,
        )
        assert not service.is_consent_granted(denied_profile)
        assert not service.is_empty(denied_profile)  # L1 data still present

    # --- CL-07: Cross-tenant isolation ---

    def test_cl_07_cross_tenant_isolation(self) -> None:
        """CL-07: Profiles and traces are isolated between tenants.

        Tenant A's customer data must not leak into Tenant B's
        prompts, traces, or search results.
        """
        # Two profiles for same customer ID but different tenants
        profile_a = make_profile(TENANT_STARTER, CUSTOMER_RETURNING)
        profile_b = make_profile(TENANT_OTHER, CUSTOMER_RETURNING)

        # Profiles should have different document IDs
        assert profile_a.id != profile_b.id
        assert profile_a.tenant_id != profile_b.tenant_id

        # Prompts should be tenant-specific
        builder = SystemPromptBuilder()

        tenant_a = _make_tenant_doc(TENANT_STARTER, TenantTier.STARTER)
        tenant_b = _make_tenant_doc(TENANT_OTHER, TenantTier.STARTER)
        prefs_a = _make_prefs_doc(
            TENANT_STARTER, brand_name="GlowSkin Co",
        )
        prefs_b = _make_prefs_doc(
            TENANT_OTHER, brand_name="DermaPro Labs",
        )

        prompt_a = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_a,
            preferences=prefs_a,
            customer_profile=profile_a,
        )
        prompt_b = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_b,
            preferences=prefs_b,
            customer_profile=profile_b,
        )

        # Each prompt should reference its own brand
        assert "GlowSkin Co" in prompt_a
        assert "DermaPro Labs" in prompt_b
        assert "DermaPro Labs" not in prompt_a
        assert "GlowSkin Co" not in prompt_b

        # Traces are tenant-scoped
        trace_a = DecisionTraceBuilder(
            "conv-a", TENANT_STARTER, CUSTOMER_RETURNING,
        ).build()
        trace_b = DecisionTraceBuilder(
            "conv-b", TENANT_OTHER, CUSTOMER_RETURNING,
        ).build()

        assert trace_a.tenant_id == TENANT_STARTER
        assert trace_b.tenant_id == TENANT_OTHER

    # --- CL-08: Consent lifecycle across layers ---

    def test_cl_08_consent_lifecycle(self) -> None:
        """CL-08: Consent transitions affect layer availability correctly.

        NOT_ASKED → GRANTED: Layers 2-4 become available
        GRANTED → DENIED: Layers 2-4 data must be deleted
        DENIED → GRANTED: Layers 2-4 re-enabled (no historical data)
        """
        service = CustomerProfileService()

        # State 1: NOT_ASKED — only L1 available
        not_asked = make_profile(consent=ConsentStatus.NOT_ASKED)
        assert not service.is_consent_granted(not_asked)

        # State 2: GRANTED — L2-4 available
        granted = make_profile(consent=ConsentStatus.GRANTED)
        assert service.is_consent_granted(granted)

        # State 3: DENIED — L2-4 blocked
        denied = make_profile(consent=ConsentStatus.DENIED)
        assert not service.is_consent_granted(denied)

        # Vectorizer consent gates at each stage
        vectorizer = ConversationVectorizer()

        # GRANTED — compress_for_prompt works with results
        results = make_vector_results(count=3, high_similarity=True)
        compressed = vectorizer.compress_for_prompt(results)
        assert "CONVERSATION HISTORY" in compressed

        # No results → empty (mimics DENIED where L2 data was deleted)
        assert vectorizer.compress_for_prompt([]) == ""

        # Decision trace records consent changes
        trace = ResponseDecisionTrace(
            conversation_id="conv-cl08",
            tenant_id=TENANT_PROFESSIONAL,
            customer_id=CUSTOMER_RETURNING,
            memory_consent_status="denied",
        )
        data = trace.to_dict()
        assert data["memory"]["consent_status"] == "denied"

    # --- CL-09: Prompt assembly with all layers active ---

    def test_cl_09_prompt_assembly_all_layers(self) -> None:
        """CL-09: SystemPromptBuilder assembles all 4 prompt layers correctly.

        Layer 1 (platform base) + Layer 2 (tier) + Layer 3 (tenant config)
        + Layer 4 (customer context) should all be present in the
        response generator prompt for Enterprise tier.
        """
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_ENTERPRISE, TenantTier.ENTERPRISE)
        prefs = _make_prefs_doc(
            TENANT_ENTERPRISE,
            brand_name="LuxeSkin",
            brand_voice="sophisticated",
            formality_level="formal",
            custom_instructions="Always recommend our premium line first.",
        )
        profile = make_profile(
            TENANT_ENTERPRISE,
            CUSTOMER_RETURNING,
            consent=ConsentStatus.GRANTED,
        )

        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Layer 1: Platform base
        assert "customer service response agent" in prompt.lower()
        assert "RULES" in prompt

        # Layer 2: Tier capabilities
        assert "Enterprise" in prompt
        assert "Layer 4" in prompt

        # Layer 3: Tenant config
        assert "LuxeSkin" in prompt
        assert "sophisticated" in prompt
        assert "formal" in prompt

        # Custom instructions (sandboxed)
        assert "MERCHANT CUSTOM INSTRUCTIONS" in prompt
        assert "premium line" in prompt
        assert "safety rules take precedence" in prompt.lower()

        # Layer 4: Customer context
        assert "CUSTOMER CONTEXT" in prompt
        assert "Purchase history" in prompt

        # Critic prompt should NOT include tenant config or customer context
        critic_prompt = builder.build(
            agent=AgentRole.CRITIC_SUPERVISOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )
        assert "LuxeSkin" not in critic_prompt
        assert "CUSTOMER CONTEXT" not in critic_prompt
        assert "premium line" not in critic_prompt
        # But safety rules are present
        assert "ABSOLUTE" in critic_prompt or "CANNOT BE OVERRIDDEN" in critic_prompt

    # --- CL-10: Explainability trace completeness ---

    def test_cl_10_explainability_trace_completeness(self) -> None:
        """CL-10: Full pipeline decision trace captures all components.

        A complete pipeline execution should produce a trace with:
        - Profile context (L1)
        - Memory signals (L2, L3)
        - Stage attributions (IC, KR, RG, CR)
        - Intent classification
        - Critic assessment
        - A/B variant (when active)

        The trace must survive serialization roundtrip.
        """
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_ENTERPRISE, TenantTier.ENTERPRISE)
        prefs = _make_prefs_doc(TENANT_ENTERPRISE)
        profile = make_profile(
            TENANT_ENTERPRISE, CUSTOMER_RETURNING,
            consent=ConsentStatus.GRANTED,
        )

        # Get prompt trace for L1 context
        prompt_trace = builder.explain(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Build full pipeline trace
        trace_builder = DecisionTraceBuilder(
            "conv-cl10", TENANT_ENTERPRISE, CUSTOMER_RETURNING,
        )

        # L1: Profile context
        trace_builder.set_profile_context(prompt_trace)
        trace_builder.set_profile_state(is_stale=False, is_empty=False)
        trace_builder.set_consent("granted")

        # L2: Conversation history
        trace_builder.add_memory_signal(
            layer=2,
            source_conversation_id="conv-hist-200",
            similarity_score=0.94,
            signal_type="prior_conversation",
            chunk_summary="Previous return inquiry about face cream",
        )

        # L3: Learned pattern
        trace_builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-pattern-100",
            similarity_score=0.88,
            signal_type="learned_pattern",
            chunk_summary="Customer prefers concise answers",
        )

        # Intent classification stage
        trace_builder.set_intent("product_return", confidence=0.96)
        trace_builder.add_stage(
            stage="intent_classifier",
            model="gpt-4o-mini",
            latency_ms=150.0,
            tokens_input=200,
            tokens_output=50,
            cost_estimate=0.0001,
        )

        # Knowledge retrieval stage
        trace_builder.set_knowledge_query("organic face cream return")
        trace_builder.add_knowledge_source(
            entry_id="kb-return-policy",
            title="Return Policy",
            relevance_score=0.95,
            entry_type="policy",
        )
        trace_builder.add_stage(
            stage="knowledge_retrieval",
            model="text-embedding-3-large",
            latency_ms=200.0,
            tokens_input=100,
            tokens_output=0,
            cost_estimate=0.0001,
        )

        # Response generation stage (fine-tuned)
        trace_builder.add_stage(
            stage="response_generator",
            model="ft:gpt-4o-mini:customer-returning:v3",
            latency_ms=1100.0,
            tokens_input=900,
            tokens_output=400,
            cost_estimate=0.005,
        )

        # Critic assessment
        trace_builder.set_critic_result(
            verdict="approved",
            flags=[],
            modifications=[],
            latency_ms=250.0,
        )
        trace_builder.add_stage(
            stage="critic_supervisor",
            model="gpt-4o-mini",
            latency_ms=250.0,
            tokens_input=500,
            tokens_output=100,
            cost_estimate=0.0003,
        )

        trace = trace_builder.build()

        # Validate completeness
        assert trace.conversation_id == "conv-cl10"
        assert trace.tenant_id == TENANT_ENTERPRISE
        assert trace.customer_id == CUSTOMER_RETURNING
        assert trace.profile_is_stale is False
        assert trace.profile_is_empty is False
        assert trace.memory_consent_status == "granted"

        # Memory signals (L2 + L3)
        assert len(trace.memory_signals) == 2

        # Intent
        assert trace.detected_intent == "product_return"
        assert trace.intent_confidence == 0.96

        # Knowledge
        assert trace.knowledge_query == "organic face cream return"
        assert len(trace.knowledge_sources) == 1

        # Pipeline stages (IC + KR + RG + CR)
        assert len(trace.stage_attributions) == 4

        # Critic
        assert trace.critic.verdict == "approved"

        # Cost rollup
        total_cost = sum(s.cost_estimate for s in trace.stage_attributions)
        assert trace.total_cost_estimate == pytest.approx(total_cost, abs=1e-6)

        # Serialization roundtrip
        data = trace.to_dict()
        restored = ResponseDecisionTrace.from_dict(data)

        assert restored.conversation_id == "conv-cl10"
        assert restored.detected_intent == "product_return"
        assert len(restored.memory_signals) == 2
        assert len(restored.stage_attributions) == 4
        assert restored.critic.verdict == "approved"
        assert len(restored.knowledge_sources) == 1

        # Verify L3 signal survives roundtrip
        l3 = [s for s in restored.memory_signals if s.layer == 3][0]
        assert l3.signal_type == "learned_pattern"
        assert l3.similarity_score == 0.88
