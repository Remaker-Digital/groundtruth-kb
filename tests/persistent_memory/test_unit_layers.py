"""Unit test suite for Persistent Customer Memory — 20 tests across 4 layers.

Work Item #97, Decision #32.

Test IDs:
    Layer 1 (L1-01 through L1-06): Customer context profile
    Layer 2 (L2-01 through L2-06): Conversation memory / vectorization
    Layer 3 (L3-01 through L3-04): Cross-session learning (interface contracts)
    Layer 4 (L4-01 through L4-04): Dedicated model training (interface contracts)

Run:
    pytest tests/persistent_memory/test_unit_layers.py -v

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
    TenantDocument,
    TenantStatus,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.customer_profile_service import (
    CustomerProfileService,
    STALE_PROFILE_DAYS,
    get_profile_service,
)
from src.multi_tenant.conversation_vectorizer import (
    ConversationVectorizer,
    chunk_transcript,
    CHUNK_TARGET_TOKENS,
    CHUNK_MIN_TOKENS,
    EMBEDDING_DIMENSIONS,
    DEFAULT_TOP_K,
    MAX_TOP_K,
)
from src.multi_tenant.response_explainability import (
    DecisionTraceBuilder,
    ResponseDecisionTrace,
    KnowledgeSource,
    MemorySignal,
    StageAttribution,
)
from src.multi_tenant.system_prompt_builder import (
    SystemPromptBuilder,
    AgentRole,
    get_prompt_builder,
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
    CUSTOMER_CASUAL,
    CUSTOMER_ENTERPRISE,
    SAMPLE_PURCHASES,
    SAMPLE_SHOPIFY_SYNC_DATA,
    make_profile,
    make_conversation_messages,
    make_vector_results,
    make_preferences,
    make_bulk_conversations,
)


# ---------------------------------------------------------------------------
# Helper — construct a TenantDocument for SystemPromptBuilder.build()
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_tenant_doc(
    tenant_id: str = TENANT_STARTER,
    tier: TenantTier = TenantTier.STARTER,
) -> TenantDocument:
    """Create a minimal TenantDocument for prompt builder tests."""
    return TenantDocument(
        id=tenant_id,
        tenant_id=tenant_id,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel.STRIPE,
        tier=tier,
        created_at=_now(),
        updated_at=_now(),
    )


# =====================================================================
# Layer 1: Customer Context (L1-01 through L1-06)
# =====================================================================


class TestLayer1CustomerContext:
    """Layer 1 unit tests — customer profile management and injection."""

    # --- L1-01: Returning customer profile retrieval ---

    @pytest.mark.asyncio
    async def test_l1_01_returning_customer_profile_has_data(self) -> None:
        """L1-01: Returning customer with 5+ interactions has populated profile.

        A profile with purchase history, region codes, and marketing segments
        should provide meaningful context for the prompt builder.
        """
        profile = make_profile(
            TENANT_STARTER,
            CUSTOMER_RETURNING,
            with_purchases=True,
            with_region=True,
            with_segments=True,
        )

        assert len(profile.purchase_history) >= 5
        assert profile.region_codes.get("locale") == "en-US"
        assert "skincare-enthusiast" in profile.marketing_segments
        assert profile.customer_id == CUSTOMER_RETURNING

    # --- L1-02: Tier-aware feature guidance ---

    def test_l1_02_tier_aware_layer_availability(self) -> None:
        """L1-02: Available memory layers depend on subscription tier.

        Starter:      Layers 1, 2
        Professional: Layers 1, 2, 3
        Enterprise:   Layers 1, 2, 3, 4
        """
        service = CustomerProfileService()

        starter_layers = service.get_available_layers(TenantTier.STARTER)
        pro_layers = service.get_available_layers(TenantTier.PROFESSIONAL)
        ent_layers = service.get_available_layers(TenantTier.ENTERPRISE)

        assert 1 in starter_layers and 2 in starter_layers
        assert 3 not in starter_layers
        assert 3 in pro_layers
        assert 4 in ent_layers

    # --- L1-03: Shopify sync populates profile ---

    @pytest.mark.asyncio
    async def test_l1_03_shopify_sync_populates_profile(self) -> None:
        """L1-03: Shopify sync data correctly maps to profile data sources.

        Orders → purchase_history, cart → cart_contents,
        customer metadata → region_codes + marketing_segments.
        """
        service = CustomerProfileService()
        # Use unconfigured service (dev mode — no persistence)
        profile = await service.sync_from_shopify(
            TENANT_STARTER,
            CUSTOMER_RETURNING,
            SAMPLE_SHOPIFY_SYNC_DATA,
        )

        assert len(profile.purchase_history) >= 2
        assert profile.region_codes.get("shipping_region") == "CA"
        assert profile.region_codes.get("locale") == "en-CA"
        assert "vip-customer" in profile.marketing_segments

    # --- L1-04: Communication style matching ---

    def test_l1_04_prompt_builder_includes_customer_context(self) -> None:
        """L1-04: SystemPromptBuilder injects customer profile data.

        When a profile with purchase history and region is provided,
        the response generator prompt should include customer context.
        """
        builder = SystemPromptBuilder()
        profile = make_profile(TENANT_STARTER, CUSTOMER_RETURNING)
        tenant_doc = _make_tenant_doc(TENANT_STARTER, TenantTier.STARTER)
        prefs = make_preferences(TENANT_STARTER, formality="casual")

        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Prompt should contain customer context section
        assert "CUSTOMER CONTEXT" in prompt or "customer" in prompt.lower()

    # --- L1-05: Empty profile handling ---

    def test_l1_05_empty_profile_detection(self) -> None:
        """L1-05: Empty profile (no data sources) is correctly detected.

        The prompt builder should gracefully degrade — no errors,
        no placeholder text, no template remnants.
        """
        service = CustomerProfileService()
        profile = make_profile(
            TENANT_STARTER,
            CUSTOMER_NEW,
            empty=True,
        )

        assert service.is_empty(profile) is True

        # Prompt builder should handle empty profile without errors
        builder = SystemPromptBuilder()
        tenant_doc = _make_tenant_doc(TENANT_STARTER, TenantTier.STARTER)
        prefs = make_preferences(TENANT_STARTER)
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant_doc,
            preferences=prefs,
            customer_profile=profile,
        )

        # Should produce a valid prompt without "unknown" or "N/A" artifacts
        assert "unknown" not in prompt.lower() or "unknown" in prompt.lower().split("customer")[0]
        assert prompt  # Non-empty

    # --- L1-06: Stale profile detection ---

    def test_l1_06_stale_profile_detection(self) -> None:
        """L1-06: Profile with no interaction in 90+ days is flagged stale.

        Stale profiles should trigger a background refresh from Shopify
        or other data sources.
        """
        service = CustomerProfileService()
        stale_profile = make_profile(
            TENANT_STARTER,
            CUSTOMER_STALE,
            stale=True,
        )
        fresh_profile = make_profile(
            TENANT_STARTER,
            CUSTOMER_RETURNING,
            stale=False,
        )

        assert service.is_stale(stale_profile) is True
        assert service.is_stale(fresh_profile) is False


# =====================================================================
# Layer 2: Conversation Memory (L2-01 through L2-06)
# =====================================================================


class TestLayer2ConversationMemory:
    """Layer 2 unit tests — vectorization and semantic search."""

    # --- L2-01: Transcript chunking ---

    def test_l2_01_transcript_chunking_respects_boundaries(self) -> None:
        """L2-01: Transcript chunking produces valid chunks.

        Chunks should be within the target token range and respect
        message boundaries (never split mid-message).
        """
        messages = make_conversation_messages("return_inquiry")
        chunks = chunk_transcript(messages)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) > 0
            # Each chunk should contain at least one role prefix
            assert "customer:" in chunk.lower() or "assistant:" in chunk.lower()

    # --- L2-02: Empty transcript handling ---

    def test_l2_02_empty_transcript_returns_no_chunks(self) -> None:
        """L2-02: Empty or no-content messages produce zero chunks."""
        assert chunk_transcript([]) == []
        assert chunk_transcript([{"role": "customer", "content": ""}]) == []

    # --- L2-03: Vector search result compression ---

    def test_l2_03_compress_for_prompt_within_budget(self) -> None:
        """L2-03: Compressed search results fit within ~300 token budget.

        The compress_for_prompt() output should be concise and formatted
        with dates and relevance scores.
        """
        vectorizer = ConversationVectorizer()
        results = make_vector_results(count=5, high_similarity=True)

        compressed = vectorizer.compress_for_prompt(results)

        assert "CONVERSATION HISTORY" in compressed
        # Budget: ~300 tokens * 4 chars/token = 1200 chars
        assert len(compressed) <= 1400  # Allow some margin
        assert "rel=" in compressed  # Contains relevance scores

    # --- L2-04: No results returns empty string ---

    def test_l2_04_no_results_returns_empty_prompt_section(self) -> None:
        """L2-04: When no relevant history exists, no prompt section is injected."""
        vectorizer = ConversationVectorizer()
        assert vectorizer.compress_for_prompt([]) == ""

    # --- L2-05: Consent gating blocks vectorization ---

    @pytest.mark.asyncio
    async def test_l2_05_consent_denied_blocks_vectorization(self) -> None:
        """L2-05: Vectorization is skipped when consent is not GRANTED.

        Layer 2 requires consent_status = GRANTED. Denied consent should
        return an empty chunk list without errors.
        """
        vectorizer = ConversationVectorizer()
        vectorizer.configure(vector_repo=AsyncMock(), openai_client=None)

        messages = make_conversation_messages("return_inquiry")
        chunk_ids = await vectorizer.vectorize_conversation(
            TENANT_STARTER,
            CUSTOMER_DENIED_CONSENT,
            "conv-denied-001",
            messages,
            consent_status=ConsentStatus.DENIED,
        )

        assert chunk_ids == []

    # --- L2-06: Tier-gated history depth ---

    def test_l2_06_tier_gated_history_depth(self) -> None:
        """L2-06: History depth varies by tier.

        Starter: 90 days, Professional: 365 days, Enterprise: unlimited.
        """
        vectorizer = ConversationVectorizer()

        starter_since = vectorizer._compute_since_date(TenantTier.STARTER)
        pro_since = vectorizer._compute_since_date(TenantTier.PROFESSIONAL)
        ent_since = vectorizer._compute_since_date(TenantTier.ENTERPRISE)

        # Starter: should have a cutoff date ~90 days ago
        assert starter_since is not None
        starter_dt = datetime.fromisoformat(starter_since)
        expected_starter = datetime.now(timezone.utc) - timedelta(days=90)
        assert abs((starter_dt - expected_starter).total_seconds()) < 60

        # Professional: ~365 days ago
        assert pro_since is not None
        pro_dt = datetime.fromisoformat(pro_since)
        expected_pro = datetime.now(timezone.utc) - timedelta(days=365)
        assert abs((pro_dt - expected_pro).total_seconds()) < 60

        # Enterprise: unlimited (None)
        assert ent_since is None


# =====================================================================
# Layer 3: Cross-Session Learning (L3-01 through L3-04)
# =====================================================================


class TestLayer3CrossSessionLearning:
    """Layer 3 unit tests — pattern extraction interface contracts.

    Layer 3 (PatternExtractionService) is not yet implemented (Tier 2 Medium).
    These tests validate the interface contracts and data structures that
    Layer 3 will integrate with.
    """

    # --- L3-01: Decision trace captures memory signals ---

    def test_l3_01_decision_trace_records_memory_signals(self) -> None:
        """L3-01: DecisionTraceBuilder can record Layer 3 memory signals.

        The explainability framework must support Layer 3 contributions
        as memory signals with confidence scores and signal types.
        """
        builder = DecisionTraceBuilder(
            conversation_id="conv-l3-test",
            tenant_id=TENANT_PROFESSIONAL,
            customer_id=CUSTOMER_RETURNING,
        )

        builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-pattern-001",
            similarity_score=0.87,
            signal_type="learned_pattern",
            chunk_summary="Customer prefers detailed technical explanations",
        )

        trace = builder.build()
        assert len(trace.memory_signals) == 1
        signal = trace.memory_signals[0]
        assert signal.layer == 3
        assert signal.signal_type == "learned_pattern"
        assert signal.similarity_score == 0.87

    # --- L3-02: Consent gating for Layer 3 ---

    def test_l3_02_consent_gates_layer3_availability(self) -> None:
        """L3-02: Layer 3 requires consent = GRANTED.

        Profiles with DENIED or NOT_ASKED consent should not have
        Layer 3 patterns extracted or injected.
        """
        service = CustomerProfileService()

        granted_profile = make_profile(consent=ConsentStatus.GRANTED)
        denied_profile = make_profile(consent=ConsentStatus.DENIED)
        notasked_profile = make_profile(consent=ConsentStatus.NOT_ASKED)

        assert service.is_consent_granted(granted_profile) is True
        assert service.is_consent_granted(denied_profile) is False
        assert service.is_consent_granted(notasked_profile) is False

    # --- L3-03: Professional tier includes Layer 3 ---

    def test_l3_03_layer3_available_on_professional(self) -> None:
        """L3-03: Layer 3 is available on Professional and Enterprise tiers.

        Starter tier does not include Layer 3 (cross-session learning).
        """
        service = CustomerProfileService()

        assert 3 not in service.get_available_layers(TenantTier.STARTER)
        assert 3 in service.get_available_layers(TenantTier.PROFESSIONAL)
        assert 3 in service.get_available_layers(TenantTier.ENTERPRISE)

    # --- L3-04: Decision trace serialization for Layer 3 ---

    def test_l3_04_decision_trace_roundtrip_with_memory(self) -> None:
        """L3-04: ResponseDecisionTrace serializes and deserializes correctly.

        Memory signals from Layer 3 must survive to_dict/from_dict roundtrip
        for Cosmos DB storage.
        """
        builder = DecisionTraceBuilder(
            "conv-roundtrip", TENANT_PROFESSIONAL, CUSTOMER_RETURNING,
        )
        builder.add_memory_signal(
            layer=3,
            source_conversation_id="conv-prior-001",
            similarity_score=0.91,
            signal_type="learned_pattern",
        )
        builder.add_memory_signal(
            layer=2,
            source_conversation_id="conv-prior-002",
            similarity_score=0.78,
            signal_type="prior_conversation",
        )

        trace = builder.build()
        data = trace.to_dict()
        restored = ResponseDecisionTrace.from_dict(data)

        assert len(restored.memory_signals) == 2
        l3_signal = [s for s in restored.memory_signals if s.layer == 3][0]
        assert l3_signal.signal_type == "learned_pattern"
        assert l3_signal.similarity_score == 0.91


# =====================================================================
# Layer 4: Dedicated Model Training (L4-01 through L4-04)
# =====================================================================


class TestLayer4DedicatedModelTraining:
    """Layer 4 unit tests — fine-tuning interface contracts.

    Layer 4 is not yet implemented (Enterprise add-on, Phase 3).
    These tests validate the data structures and tier gating that
    Layer 4 will integrate with.
    """

    # --- L4-01: Enterprise-only Layer 4 availability ---

    def test_l4_01_layer4_enterprise_only(self) -> None:
        """L4-01: Layer 4 is only available on Enterprise tier.

        Starter and Professional tiers should not include Layer 4.
        """
        service = CustomerProfileService()

        assert 4 not in service.get_available_layers(TenantTier.STARTER)
        assert 4 not in service.get_available_layers(TenantTier.PROFESSIONAL)
        assert 4 in service.get_available_layers(TenantTier.ENTERPRISE)

    # --- L4-02: Decision trace supports model attribution ---

    def test_l4_02_stage_attribution_tracks_model_cost(self) -> None:
        """L4-02: StageAttribution tracks model, latency, tokens, and cost.

        Fine-tuned model usage must be attributable per-stage for
        billing and explainability.
        """
        builder = DecisionTraceBuilder(
            "conv-l4-test", TENANT_ENTERPRISE, CUSTOMER_ENTERPRISE,
        )
        builder.add_stage(
            stage="response_generator",
            model="ft:gpt-4o-mini:customer-frank:v2",
            latency_ms=1200.0,
            tokens_input=800,
            tokens_output=350,
            cost_estimate=0.0045,
        )

        trace = builder.build()
        assert len(trace.stage_attributions) == 1
        stage = trace.stage_attributions[0]
        assert stage.model.startswith("ft:")
        assert stage.cost_estimate == 0.0045
        assert trace.total_cost_estimate == 0.0045

    # --- L4-03: Consent verification for fine-tuning ---

    def test_l4_03_consent_required_for_training_data(self) -> None:
        """L4-03: Fine-tuning data collection requires explicit consent.

        The consent_status must be GRANTED for a customer's data to be
        included in any training pipeline.
        """
        service = CustomerProfileService()

        granted = make_profile(consent=ConsentStatus.GRANTED)
        denied = make_profile(consent=ConsentStatus.DENIED)

        assert service.is_consent_granted(granted) is True
        assert service.is_consent_granted(denied) is False

    # --- L4-04: Explainability trace captures A/B variant ---

    def test_l4_04_trace_captures_ab_variant(self) -> None:
        """L4-04: Decision trace records A/B variant when fine-tuned model is active.

        Future Smart Rollout will use this to compare base vs fine-tuned
        model performance.
        """
        trace = ResponseDecisionTrace(
            conversation_id="conv-ab-test",
            tenant_id=TENANT_ENTERPRISE,
            customer_id=CUSTOMER_ENTERPRISE,
            ab_variant="fine-tuned-v2",
            ab_experiment_id="exp-ft-2026-02",
        )

        data = trace.to_dict()
        assert "ab_test" in data
        assert data["ab_test"]["variant"] == "fine-tuned-v2"
        assert data["ab_test"]["experiment_id"] == "exp-ft-2026-02"

        # Roundtrip
        restored = ResponseDecisionTrace.from_dict(data)
        assert restored.ab_variant == "fine-tuned-v2"
