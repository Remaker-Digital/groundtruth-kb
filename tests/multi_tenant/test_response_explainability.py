"""Tests for response explainability — per-response decision trace.

Tests RE-01 through RE-15 covering:
    - Dataclass default values (KnowledgeSource, MemorySignal, CriticAssessment,
      StageAttribution, ResponseDecisionTrace)
    - DecisionTraceBuilder fluent API and incremental construction
    - to_dict() serialization and from_dict() deserialization
    - Full roundtrip (to_dict -> from_dict equality)

Test IDs: RE-01 to RE-15

References:
    - src/multi_tenant/response_explainability.py
    - Decision #28+: Response explainability framework
    - Decision #32: Test cases and validation framework

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from unittest.mock import patch

import pytest

from src.multi_tenant.response_explainability import (
    CriticAssessment,
    DecisionTraceBuilder,
    KnowledgeSource,
    MemorySignal,
    ResponseDecisionTrace,
    StageAttribution,
)


# ---------------------------------------------------------------------------
# RE-01: KnowledgeSource default values
# ---------------------------------------------------------------------------


class TestRE01KnowledgeSourceDefaults:
    """RE-01: KnowledgeSource fields initialise to documented defaults."""

    def test_defaults(self):
        ks = KnowledgeSource()
        assert ks.entry_id == ""
        assert ks.entry_type == ""
        assert ks.title == ""
        assert ks.relevance_score == 0.0
        assert ks.matched_query == ""

    def test_custom_values(self):
        ks = KnowledgeSource(
            entry_id="kb-001",
            entry_type="faq",
            title="Return Policy",
            relevance_score=0.95,
            matched_query="how to return",
        )
        assert ks.entry_id == "kb-001"
        assert ks.entry_type == "faq"
        assert ks.title == "Return Policy"
        assert ks.relevance_score == 0.95
        assert ks.matched_query == "how to return"


# ---------------------------------------------------------------------------
# RE-02: MemorySignal default values
# ---------------------------------------------------------------------------


class TestRE02MemorySignalDefaults:
    """RE-02: MemorySignal fields initialise to documented defaults."""

    def test_defaults(self):
        ms = MemorySignal()
        assert ms.layer == 2
        assert ms.source_conversation_id == ""
        assert ms.chunk_summary == ""
        assert ms.similarity_score == 0.0
        assert ms.signal_type == ""

    def test_layer_3_signal(self):
        ms = MemorySignal(layer=3, signal_type="learned_pattern", similarity_score=0.88)
        assert ms.layer == 3
        assert ms.signal_type == "learned_pattern"
        assert ms.similarity_score == 0.88


# ---------------------------------------------------------------------------
# RE-03: CriticAssessment default values
# ---------------------------------------------------------------------------


class TestRE03CriticAssessmentDefaults:
    """RE-03: CriticAssessment fields initialise to documented defaults."""

    def test_defaults(self):
        ca = CriticAssessment()
        assert ca.verdict == "unknown"
        assert ca.flags == []
        assert ca.modifications == []
        assert ca.latency_ms == 0.0

    def test_flags_and_modifications_are_independent_lists(self):
        """Each instance gets its own list (default_factory)."""
        ca1 = CriticAssessment()
        ca2 = CriticAssessment()
        ca1.flags.append("pii_detected")
        assert ca2.flags == []

    def test_custom_values(self):
        ca = CriticAssessment(
            verdict="rejected",
            flags=["pii_detected", "profanity"],
            modifications=["redact_name"],
            latency_ms=45.2,
        )
        assert ca.verdict == "rejected"
        assert len(ca.flags) == 2
        assert len(ca.modifications) == 1
        assert ca.latency_ms == 45.2


# ---------------------------------------------------------------------------
# RE-04: StageAttribution default values
# ---------------------------------------------------------------------------


class TestRE04StageAttributionDefaults:
    """RE-04: StageAttribution fields initialise to documented defaults."""

    def test_defaults(self):
        sa = StageAttribution()
        assert sa.stage == ""
        assert sa.model == ""
        assert sa.latency_ms == 0.0
        assert sa.tokens_input == 0
        assert sa.tokens_output == 0
        assert sa.cost_estimate == 0.0

    def test_custom_values(self):
        sa = StageAttribution(
            stage="response_generator",
            model="gpt-4o",
            latency_ms=1200.5,
            tokens_input=850,
            tokens_output=320,
            cost_estimate=0.0045,
        )
        assert sa.stage == "response_generator"
        assert sa.model == "gpt-4o"
        assert sa.latency_ms == 1200.5
        assert sa.tokens_input == 850
        assert sa.tokens_output == 320
        assert sa.cost_estimate == 0.0045


# ---------------------------------------------------------------------------
# RE-05: ResponseDecisionTrace default values
# ---------------------------------------------------------------------------


class TestRE05ResponseDecisionTraceDefaults:
    """RE-05: ResponseDecisionTrace fields initialise to documented defaults."""

    def test_scalar_defaults(self):
        trace = ResponseDecisionTrace()
        assert trace.conversation_id == ""
        assert trace.tenant_id == ""
        assert trace.customer_id == ""
        assert trace.message_index == 0
        assert trace.timestamp == ""
        assert trace.profile_is_stale is False
        assert trace.profile_is_empty is False
        assert trace.knowledge_query == ""
        assert trace.knowledge_results_count == 0
        assert trace.memory_consent_status == ""
        assert trace.memory_history_depth_days is None
        assert trace.ab_variant is None
        assert trace.ab_experiment_id is None
        assert trace.config_version == 0
        assert trace.custom_instructions_present is False
        assert trace.total_latency_ms == 0.0
        assert trace.total_cost_estimate == 0.0
        assert trace.detected_intent == ""
        assert trace.intent_confidence == 0.0
        assert trace.response_language == "en"
        assert trace.was_escalated is False
        assert trace.escalation_reason == ""

    def test_list_defaults_are_empty(self):
        trace = ResponseDecisionTrace()
        assert trace.profile_factors_used == []
        assert trace.profile_data_sources == []
        assert trace.knowledge_sources == []
        assert trace.memory_signals == []
        assert trace.config_overrides_applied == []
        assert trace.stage_attributions == []

    def test_critic_default_is_unknown(self):
        trace = ResponseDecisionTrace()
        assert isinstance(trace.critic, CriticAssessment)
        assert trace.critic.verdict == "unknown"

    def test_list_independence(self):
        """Each ResponseDecisionTrace gets its own list instances."""
        t1 = ResponseDecisionTrace()
        t2 = ResponseDecisionTrace()
        t1.profile_factors_used.append("geography")
        assert t2.profile_factors_used == []


# ---------------------------------------------------------------------------
# RE-06: Builder set_profile_context extracts fields
# ---------------------------------------------------------------------------


class TestRE06BuilderSetProfileContext:
    """RE-06: set_profile_context populates trace from prompt explain output."""

    def test_extracts_all_fields(self):
        prompt_trace = {
            "customer_context_sources": ["purchase_history", "geography"],
            "tenant_config_fields": ["brand_name", "formality_level"],
            "config_version": 7,
            "custom_instructions_present": True,
            "history_depth_days": 365,
        }
        builder = DecisionTraceBuilder("conv-1", "tenant-1", "cust-1")
        builder.set_profile_context(prompt_trace)
        trace = builder.build()

        assert trace.profile_data_sources == ["purchase_history", "geography"]
        assert trace.profile_factors_used == ["brand_name", "formality_level"]
        assert trace.config_version == 7
        assert trace.custom_instructions_present is True
        assert trace.config_overrides_applied == ["brand_name", "formality_level"]
        assert trace.memory_history_depth_days == 365

    def test_empty_prompt_trace(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.set_profile_context({})
        trace = builder.build()

        assert trace.profile_data_sources == []
        assert trace.profile_factors_used == []
        assert trace.config_version == 0
        assert trace.custom_instructions_present is False
        assert trace.memory_history_depth_days is None


# ---------------------------------------------------------------------------
# RE-07: Builder fluent chaining
# ---------------------------------------------------------------------------


class TestRE07BuilderFluentChaining:
    """RE-07: All builder setter methods return self for fluent chaining."""

    def test_all_setters_return_self(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1", "cust-1")

        # Every setter must return the same builder instance.
        result = (
            builder
            .set_profile_context({"customer_context_sources": []})
            .set_profile_state(is_stale=True, is_empty=False)
            .set_consent("granted")
            .add_knowledge_source("kb-1", "FAQ", 0.9)
            .set_knowledge_query("shipping info")
            .add_memory_signal(2, "conv-old", 0.85)
            .add_stage("intent_classifier", "gpt-4o-mini", 120.0)
            .set_intent("order_status", confidence=0.97)
            .set_critic_result("approved", latency_ms=50.0)
            .set_escalation(False)
            .set_language("fr")
        )

        assert result is builder

    def test_chained_build_produces_valid_trace(self):
        trace = (
            DecisionTraceBuilder("conv-2", "tenant-2", "cust-2", message_index=3)
            .set_consent("granted")
            .set_language("en")
            .set_intent("product_question", confidence=0.91)
            .set_critic_result("approved")
            .build()
        )

        assert trace.conversation_id == "conv-2"
        assert trace.tenant_id == "tenant-2"
        assert trace.customer_id == "cust-2"
        assert trace.message_index == 3
        assert trace.memory_consent_status == "granted"
        assert trace.response_language == "en"
        assert trace.detected_intent == "product_question"
        assert trace.intent_confidence == 0.91
        assert trace.critic.verdict == "approved"


# ---------------------------------------------------------------------------
# RE-08: Builder add_knowledge_source increments count
# ---------------------------------------------------------------------------


class TestRE08BuilderKnowledgeSourceCount:
    """RE-08: add_knowledge_source appends and updates knowledge_results_count."""

    def test_increments_count(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_knowledge_source("kb-1", "Return Policy", 0.95, entry_type="policy")
        builder.add_knowledge_source("kb-2", "Shipping FAQ", 0.87, entry_type="faq")
        builder.add_knowledge_source("kb-3", "Size Guide", 0.72, entry_type="product")
        trace = builder.build()

        assert trace.knowledge_results_count == 3
        assert len(trace.knowledge_sources) == 3
        assert trace.knowledge_sources[0].entry_id == "kb-1"
        assert trace.knowledge_sources[1].title == "Shipping FAQ"
        assert trace.knowledge_sources[2].relevance_score == 0.72

    def test_zero_sources(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        trace = builder.build()
        assert trace.knowledge_results_count == 0
        assert trace.knowledge_sources == []


# ---------------------------------------------------------------------------
# RE-09: Builder add_memory_signal appends
# ---------------------------------------------------------------------------


class TestRE09BuilderMemorySignal:
    """RE-09: add_memory_signal appends MemorySignal objects to trace."""

    def test_appends_signals(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_memory_signal(
            layer=2,
            source_conversation_id="conv-old-1",
            similarity_score=0.92,
            signal_type="prior_conversation",
            chunk_summary="Customer asked about sizing",
        )
        builder.add_memory_signal(
            layer=3,
            signal_type="learned_pattern",
            similarity_score=0.78,
        )
        trace = builder.build()

        assert len(trace.memory_signals) == 2
        assert trace.memory_signals[0].layer == 2
        assert trace.memory_signals[0].source_conversation_id == "conv-old-1"
        assert trace.memory_signals[0].similarity_score == 0.92
        assert trace.memory_signals[0].chunk_summary == "Customer asked about sizing"
        assert trace.memory_signals[1].layer == 3
        assert trace.memory_signals[1].signal_type == "learned_pattern"

    def test_default_signal_type(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_memory_signal(2)
        trace = builder.build()
        assert trace.memory_signals[0].signal_type == "prior_conversation"


# ---------------------------------------------------------------------------
# RE-10: Builder add_stage appends
# ---------------------------------------------------------------------------


class TestRE10BuilderAddStage:
    """RE-10: add_stage appends StageAttribution objects to trace."""

    def test_appends_stages(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_stage("intent_classifier", "gpt-4o-mini", 150.0, 200, 50, 0.0001)
        builder.add_stage("knowledge_retrieval", "text-embedding-3-large", 300.0, 100, 0, 0.00005)
        builder.add_stage("response_generator", "gpt-4o", 1800.0, 900, 350, 0.005)
        trace = builder.build()

        assert len(trace.stage_attributions) == 3
        assert trace.stage_attributions[0].stage == "intent_classifier"
        assert trace.stage_attributions[0].model == "gpt-4o-mini"
        assert trace.stage_attributions[0].latency_ms == 150.0
        assert trace.stage_attributions[1].tokens_input == 100
        assert trace.stage_attributions[2].tokens_output == 350
        assert trace.stage_attributions[2].cost_estimate == 0.005

    def test_stage_with_defaults(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_stage("analytics", "gpt-4o-mini", 80.0)
        trace = builder.build()

        sa = trace.stage_attributions[0]
        assert sa.tokens_input == 0
        assert sa.tokens_output == 0
        assert sa.cost_estimate == 0.0


# ---------------------------------------------------------------------------
# RE-11: Builder build() computes total_cost_estimate
# ---------------------------------------------------------------------------


class TestRE11BuilderBuildCostEstimate:
    """RE-11: build() sums stage cost_estimate values into total_cost_estimate."""

    def test_sums_stage_costs(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.add_stage("intent_classifier", "gpt-4o-mini", 100.0, cost_estimate=0.0001)
        builder.add_stage("knowledge_retrieval", "text-embedding-3-large", 200.0, cost_estimate=0.00005)
        builder.add_stage("response_generator", "gpt-4o", 1500.0, cost_estimate=0.005)
        builder.add_stage("critic_supervisor", "gpt-4o-mini", 80.0, cost_estimate=0.0001)
        trace = builder.build()

        expected = 0.0001 + 0.00005 + 0.005 + 0.0001
        assert abs(trace.total_cost_estimate - expected) < 1e-10

    def test_zero_stages_zero_cost(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        trace = builder.build()
        assert trace.total_cost_estimate == 0.0

    def test_total_latency_ms_is_wall_clock(self):
        """build() computes total_latency_ms from monotonic clock, not stage sum."""
        # Patch time.monotonic to simulate elapsed time.
        with patch("src.multi_tenant.response_explainability.time.monotonic") as mock_mono:
            mock_mono.return_value = 100.0  # start time
            builder = DecisionTraceBuilder("conv-1", "tenant-1")

            # Add stages with their own latency values (these are per-stage,
            # not used for total).
            builder.add_stage("intent_classifier", "gpt-4o-mini", 150.0)
            builder.add_stage("response_generator", "gpt-4o", 1800.0)

            # Simulate 2.5 seconds of wall-clock elapsed.
            mock_mono.return_value = 102.5
            trace = builder.build()

            # total_latency_ms should reflect wall-clock, not stage sum.
            assert abs(trace.total_latency_ms - 2500.0) < 1e-6


# ---------------------------------------------------------------------------
# RE-12: Builder set_critic_result
# ---------------------------------------------------------------------------


class TestRE12BuilderSetCriticResult:
    """RE-12: set_critic_result creates a CriticAssessment on the trace."""

    def test_approved_verdict(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.set_critic_result("approved", latency_ms=42.0)
        trace = builder.build()

        assert trace.critic.verdict == "approved"
        assert trace.critic.flags == []
        assert trace.critic.modifications == []
        assert trace.critic.latency_ms == 42.0

    def test_rejected_with_flags(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.set_critic_result(
            "rejected",
            flags=["pii_detected", "off_topic"],
            modifications=["response_blocked"],
            latency_ms=95.5,
        )
        trace = builder.build()

        assert trace.critic.verdict == "rejected"
        assert trace.critic.flags == ["pii_detected", "off_topic"]
        assert trace.critic.modifications == ["response_blocked"]
        assert trace.critic.latency_ms == 95.5

    def test_none_flags_become_empty_list(self):
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.set_critic_result("timeout", flags=None, modifications=None)
        trace = builder.build()

        assert trace.critic.flags == []
        assert trace.critic.modifications == []

    def test_overwrites_previous_critic(self):
        """Calling set_critic_result twice replaces the CriticAssessment."""
        builder = DecisionTraceBuilder("conv-1", "tenant-1")
        builder.set_critic_result("rejected", flags=["pii_detected"])
        builder.set_critic_result("approved")
        trace = builder.build()

        assert trace.critic.verdict == "approved"
        assert trace.critic.flags == []


# ---------------------------------------------------------------------------
# RE-13: to_dict() produces correct nested structure
# ---------------------------------------------------------------------------


class TestRE13ToDictStructure:
    """RE-13: to_dict() serialises to the documented nested dict shape."""

    def _build_full_trace(self) -> ResponseDecisionTrace:
        """Build a fully-populated trace for serialisation testing."""
        trace = ResponseDecisionTrace(
            conversation_id="conv-100",
            tenant_id="tenant-200",
            customer_id="cust-300",
            message_index=2,
            timestamp="2026-02-01T12:00:00+00:00",
            profile_factors_used=["brand_name", "formality"],
            profile_data_sources=["purchase_history", "geography"],
            profile_is_stale=True,
            profile_is_empty=False,
            knowledge_sources=[
                KnowledgeSource(
                    entry_id="kb-1", entry_type="faq",
                    title="Returns", relevance_score=0.95,
                ),
            ],
            knowledge_query="how to return an item",
            knowledge_results_count=1,
            memory_signals=[
                MemorySignal(
                    layer=2, source_conversation_id="conv-50",
                    similarity_score=0.88, signal_type="prior_conversation",
                    chunk_summary="Previous return discussion",
                ),
            ],
            memory_consent_status="granted",
            memory_history_depth_days=365,
            config_version=5,
            config_overrides_applied=["brand_name"],
            custom_instructions_present=True,
            stage_attributions=[
                StageAttribution(
                    stage="response_generator", model="gpt-4o",
                    latency_ms=1500.0, tokens_input=800, tokens_output=300,
                    cost_estimate=0.005,
                ),
            ],
            total_latency_ms=2200.0,
            total_cost_estimate=0.0065,
            critic=CriticAssessment(
                verdict="approved", flags=[], modifications=[], latency_ms=40.0,
            ),
            detected_intent="return_request",
            intent_confidence=0.96,
            response_language="en",
            was_escalated=False,
            escalation_reason="",
        )
        return trace

    def test_top_level_keys(self):
        d = self._build_full_trace().to_dict()
        expected_keys = {
            "conversation_id", "tenant_id", "customer_id", "message_index",
            "timestamp", "profile", "knowledge", "memory", "config",
            "pipeline", "critic", "intent", "response",
        }
        assert expected_keys.issubset(set(d.keys()))

    def test_profile_section(self):
        d = self._build_full_trace().to_dict()
        profile = d["profile"]
        assert profile["factors_used"] == ["brand_name", "formality"]
        assert profile["data_sources"] == ["purchase_history", "geography"]
        assert profile["is_stale"] is True
        assert profile["is_empty"] is False

    def test_knowledge_section(self):
        d = self._build_full_trace().to_dict()
        knowledge = d["knowledge"]
        assert knowledge["query"] == "how to return an item"
        assert knowledge["results_count"] == 1
        assert len(knowledge["sources"]) == 1
        assert knowledge["sources"][0]["entry_id"] == "kb-1"
        assert knowledge["sources"][0]["relevance_score"] == 0.95

    def test_memory_section(self):
        d = self._build_full_trace().to_dict()
        memory = d["memory"]
        assert memory["consent_status"] == "granted"
        assert memory["history_depth_days"] == 365
        assert len(memory["signals"]) == 1
        assert memory["signals"][0]["layer"] == 2
        assert memory["signals"][0]["similarity_score"] == 0.88

    def test_pipeline_section(self):
        d = self._build_full_trace().to_dict()
        pipeline = d["pipeline"]
        assert pipeline["total_latency_ms"] == 2200.0
        assert pipeline["total_cost_estimate"] == 0.0065
        assert len(pipeline["stages"]) == 1
        assert pipeline["stages"][0]["stage"] == "response_generator"
        assert pipeline["stages"][0]["tokens_input"] == 800

    def test_critic_section(self):
        d = self._build_full_trace().to_dict()
        critic = d["critic"]
        assert critic["verdict"] == "approved"
        assert critic["latency_ms"] == 40.0

    def test_intent_section(self):
        d = self._build_full_trace().to_dict()
        intent = d["intent"]
        assert intent["detected"] == "return_request"
        assert intent["confidence"] == 0.96

    def test_response_section(self):
        d = self._build_full_trace().to_dict()
        response = d["response"]
        assert response["language"] == "en"
        assert response["was_escalated"] is False
        assert response["escalation_reason"] == ""

    def test_ab_test_absent_when_no_variant(self):
        d = self._build_full_trace().to_dict()
        assert "ab_test" not in d

    def test_ab_test_present_when_variant_set(self):
        trace = self._build_full_trace()
        trace.ab_variant = "variant_b"
        trace.ab_experiment_id = "exp-42"
        d = trace.to_dict()
        assert "ab_test" in d
        assert d["ab_test"]["variant"] == "variant_b"
        assert d["ab_test"]["experiment_id"] == "exp-42"


# ---------------------------------------------------------------------------
# RE-14: from_dict() reconstructs trace
# ---------------------------------------------------------------------------


class TestRE14FromDict:
    """RE-14: from_dict() reconstructs a ResponseDecisionTrace from a dict."""

    def test_reconstructs_from_minimal_dict(self):
        data = {
            "conversation_id": "conv-1",
            "tenant_id": "tenant-1",
            "customer_id": "cust-1",
            "message_index": 5,
            "timestamp": "2026-02-01T00:00:00Z",
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert trace.conversation_id == "conv-1"
        assert trace.tenant_id == "tenant-1"
        assert trace.customer_id == "cust-1"
        assert trace.message_index == 5
        assert trace.timestamp == "2026-02-01T00:00:00Z"

    def test_reconstructs_profile(self):
        data = {
            "profile": {
                "factors_used": ["brand_name"],
                "data_sources": ["purchase_history"],
                "is_stale": True,
                "is_empty": False,
            },
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert trace.profile_factors_used == ["brand_name"]
        assert trace.profile_data_sources == ["purchase_history"]
        assert trace.profile_is_stale is True
        assert trace.profile_is_empty is False

    def test_reconstructs_knowledge_sources(self):
        data = {
            "knowledge": {
                "query": "shipping cost",
                "results_count": 2,
                "sources": [
                    {"entry_id": "kb-1", "entry_type": "faq", "title": "Shipping", "relevance_score": 0.9},
                    {"entry_id": "kb-2", "entry_type": "policy", "title": "Free Shipping", "relevance_score": 0.8},
                ],
            },
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert trace.knowledge_query == "shipping cost"
        assert trace.knowledge_results_count == 2
        assert len(trace.knowledge_sources) == 2
        assert isinstance(trace.knowledge_sources[0], KnowledgeSource)
        assert trace.knowledge_sources[0].entry_id == "kb-1"
        assert trace.knowledge_sources[1].relevance_score == 0.8

    def test_reconstructs_memory_signals(self):
        data = {
            "memory": {
                "consent_status": "granted",
                "history_depth_days": 90,
                "signals": [
                    {
                        "layer": 2,
                        "source_conversation_id": "conv-old",
                        "similarity_score": 0.85,
                        "signal_type": "prior_conversation",
                        "chunk_summary": "Asked about sizing",
                    },
                ],
            },
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert trace.memory_consent_status == "granted"
        assert trace.memory_history_depth_days == 90
        assert len(trace.memory_signals) == 1
        assert isinstance(trace.memory_signals[0], MemorySignal)
        assert trace.memory_signals[0].chunk_summary == "Asked about sizing"

    def test_reconstructs_critic(self):
        data = {
            "critic": {
                "verdict": "modified",
                "flags": ["tone_adjusted"],
                "modifications": ["softened_language"],
                "latency_ms": 55.0,
            },
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert isinstance(trace.critic, CriticAssessment)
        assert trace.critic.verdict == "modified"
        assert trace.critic.flags == ["tone_adjusted"]
        assert trace.critic.modifications == ["softened_language"]

    def test_reconstructs_ab_test(self):
        data = {
            "ab_test": {
                "variant": "control",
                "experiment_id": "exp-99",
            },
        }
        trace = ResponseDecisionTrace.from_dict(data)
        assert trace.ab_variant == "control"
        assert trace.ab_experiment_id == "exp-99"

    def test_missing_sections_use_defaults(self):
        trace = ResponseDecisionTrace.from_dict({})
        assert trace.conversation_id == ""
        assert trace.profile_factors_used == []
        assert trace.knowledge_sources == []
        assert trace.memory_signals == []
        assert trace.stage_attributions == []
        assert trace.critic.verdict == "unknown"
        assert trace.response_language == "en"
        assert trace.ab_variant is None


# ---------------------------------------------------------------------------
# RE-15: Serialization roundtrip (to_dict -> from_dict equality)
# ---------------------------------------------------------------------------


class TestRE15SerializationRoundtrip:
    """RE-15: to_dict -> from_dict produces an equivalent trace."""

    def _build_comprehensive_trace(self) -> ResponseDecisionTrace:
        """Build a trace with all fields populated for roundtrip testing."""
        return ResponseDecisionTrace(
            conversation_id="conv-rt",
            tenant_id="tenant-rt",
            customer_id="cust-rt",
            message_index=4,
            timestamp="2026-02-01T15:30:00+00:00",
            profile_factors_used=["brand_name", "formality_level", "response_length"],
            profile_data_sources=["purchase_history", "geography", "cart"],
            profile_is_stale=False,
            profile_is_empty=False,
            knowledge_sources=[
                KnowledgeSource(
                    entry_id="kb-10", entry_type="product",
                    title="Widget Pro", relevance_score=0.93,
                ),
                KnowledgeSource(
                    entry_id="kb-11", entry_type="faq",
                    title="How to Use Widget Pro", relevance_score=0.88,
                ),
            ],
            knowledge_query="widget pro features",
            knowledge_results_count=2,
            memory_signals=[
                MemorySignal(
                    layer=2, source_conversation_id="conv-prev-1",
                    similarity_score=0.91, signal_type="prior_conversation",
                    chunk_summary="Interested in premium features",
                ),
                MemorySignal(
                    layer=3, source_conversation_id="",
                    similarity_score=0.75, signal_type="learned_pattern",
                    chunk_summary="Prefers concise answers",
                ),
            ],
            memory_consent_status="granted",
            memory_history_depth_days=365,
            ab_variant="variant_a",
            ab_experiment_id="exp-101",
            config_version=12,
            config_overrides_applied=["brand_name", "response_length"],
            custom_instructions_present=True,
            stage_attributions=[
                StageAttribution(
                    stage="intent_classifier", model="gpt-4o-mini",
                    latency_ms=120.0, tokens_input=150, tokens_output=30,
                    cost_estimate=0.00008,
                ),
                StageAttribution(
                    stage="knowledge_retrieval", model="text-embedding-3-large",
                    latency_ms=250.0, tokens_input=100, tokens_output=0,
                    cost_estimate=0.00004,
                ),
                StageAttribution(
                    stage="response_generator", model="gpt-4o",
                    latency_ms=1600.0, tokens_input=900, tokens_output=350,
                    cost_estimate=0.0052,
                ),
                StageAttribution(
                    stage="critic_supervisor", model="gpt-4o-mini",
                    latency_ms=95.0, tokens_input=400, tokens_output=20,
                    cost_estimate=0.00015,
                ),
            ],
            total_latency_ms=2300.0,
            total_cost_estimate=0.00547,
            critic=CriticAssessment(
                verdict="approved", flags=[], modifications=[], latency_ms=95.0,
            ),
            detected_intent="product_question",
            intent_confidence=0.97,
            response_language="en",
            was_escalated=False,
            escalation_reason="",
        )

    def test_roundtrip_preserves_identifiers(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.conversation_id == original.conversation_id
        assert restored.tenant_id == original.tenant_id
        assert restored.customer_id == original.customer_id
        assert restored.message_index == original.message_index
        assert restored.timestamp == original.timestamp

    def test_roundtrip_preserves_profile(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.profile_factors_used == original.profile_factors_used
        assert restored.profile_data_sources == original.profile_data_sources
        assert restored.profile_is_stale == original.profile_is_stale
        assert restored.profile_is_empty == original.profile_is_empty

    def test_roundtrip_preserves_knowledge(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.knowledge_query == original.knowledge_query
        assert restored.knowledge_results_count == original.knowledge_results_count
        assert len(restored.knowledge_sources) == len(original.knowledge_sources)
        for orig_ks, rest_ks in zip(original.knowledge_sources, restored.knowledge_sources):
            assert rest_ks.entry_id == orig_ks.entry_id
            assert rest_ks.entry_type == orig_ks.entry_type
            assert rest_ks.title == orig_ks.title
            assert rest_ks.relevance_score == orig_ks.relevance_score

    def test_roundtrip_preserves_memory(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.memory_consent_status == original.memory_consent_status
        assert restored.memory_history_depth_days == original.memory_history_depth_days
        assert len(restored.memory_signals) == len(original.memory_signals)
        for orig_ms, rest_ms in zip(original.memory_signals, restored.memory_signals):
            assert rest_ms.layer == orig_ms.layer
            assert rest_ms.source_conversation_id == orig_ms.source_conversation_id
            assert rest_ms.similarity_score == orig_ms.similarity_score
            assert rest_ms.signal_type == orig_ms.signal_type
            assert rest_ms.chunk_summary == orig_ms.chunk_summary

    def test_roundtrip_preserves_config(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.config_version == original.config_version
        assert restored.config_overrides_applied == original.config_overrides_applied
        assert restored.custom_instructions_present == original.custom_instructions_present

    def test_roundtrip_preserves_pipeline(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.total_latency_ms == original.total_latency_ms
        assert restored.total_cost_estimate == original.total_cost_estimate
        assert len(restored.stage_attributions) == len(original.stage_attributions)
        for orig_sa, rest_sa in zip(original.stage_attributions, restored.stage_attributions):
            assert rest_sa.stage == orig_sa.stage
            assert rest_sa.model == orig_sa.model
            assert rest_sa.latency_ms == orig_sa.latency_ms
            assert rest_sa.tokens_input == orig_sa.tokens_input
            assert rest_sa.tokens_output == orig_sa.tokens_output
            assert rest_sa.cost_estimate == orig_sa.cost_estimate

    def test_roundtrip_preserves_critic(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.critic.verdict == original.critic.verdict
        assert restored.critic.flags == original.critic.flags
        assert restored.critic.modifications == original.critic.modifications
        assert restored.critic.latency_ms == original.critic.latency_ms

    def test_roundtrip_preserves_intent_and_response(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.detected_intent == original.detected_intent
        assert restored.intent_confidence == original.intent_confidence
        assert restored.response_language == original.response_language
        assert restored.was_escalated == original.was_escalated
        assert restored.escalation_reason == original.escalation_reason

    def test_roundtrip_preserves_ab_test(self):
        original = self._build_comprehensive_trace()
        restored = ResponseDecisionTrace.from_dict(original.to_dict())

        assert restored.ab_variant == original.ab_variant
        assert restored.ab_experiment_id == original.ab_experiment_id

    def test_double_roundtrip_stable(self):
        """Serialising twice produces identical dicts."""
        original = self._build_comprehensive_trace()
        d1 = original.to_dict()
        d2 = ResponseDecisionTrace.from_dict(d1).to_dict()
        assert d1 == d2
