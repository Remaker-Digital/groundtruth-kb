"""Tests for Langfuse trace exporter — Lane 1 structural export.

SPEC-1874: Validates that:
1. Exporter produces valid Langfuse trace format
2. Hashed fields are irreversible (SHA-256, not base64)
3. No content-bearing fields appear in Lane 1 export
4. Exporter failure does not block pipeline execution
5. Config toggle works (disabled = no Langfuse calls)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import MagicMock, patch

import pytest

from src.multi_tenant.response_explainability import (
    CriticAssessment,
    KnowledgeSource,
    MemorySignal,
    ResponseDecisionTrace,
    StageAttribution,
)
from src.observability.langfuse_exporter import (
    _CONTENT_BEARING_FIELDS,
    _hash_id,
    _prompt_version_hash,
    _prompt_field_band,
    _scrub_for_export,
    build_lane1_payload,
    build_lane2_payload,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_trace() -> ResponseDecisionTrace:
    """Build a fully-populated ResponseDecisionTrace for testing."""
    return ResponseDecisionTrace(
        conversation_id="conv-abc-123",
        tenant_id="tenant-xyz-789",
        customer_id="cust-secret-456",
        message_index=3,
        timestamp="2026-03-30T12:00:00Z",
        # Profile (content-bearing — must NOT appear in Lane 1)
        profile_factors_used=["name", "order_history"],
        profile_data_sources=["shopify", "crm"],
        profile_is_stale=False,
        profile_is_empty=False,
        # Knowledge (content-bearing — only count exported)
        knowledge_sources=[
            KnowledgeSource(
                entry_id="kb-1",
                entry_type="faq",
                title="Return Policy Details",
                relevance_score=0.92,
                matched_query="how to return",
            ),
            KnowledgeSource(
                entry_id="kb-2",
                entry_type="product",
                title="Widget Pro Max",
                relevance_score=0.78,
                matched_query="widget specs",
            ),
        ],
        knowledge_query="how do I return a widget?",
        knowledge_results_count=2,
        # Memory (content-bearing — must NOT appear)
        memory_signals=[
            MemorySignal(
                layer=2,
                source_conversation_id="conv-old",
                chunk_summary="Customer previously asked about refunds",
                similarity_score=0.85,
                signal_type="prior_conversation",
            ),
        ],
        memory_consent_status="granted",
        # A/B variant
        ab_variant="treatment_v2",
        ab_experiment_id="exp-tone-test",
        # Stage attributions (structural — exported)
        stage_attributions=[
            StageAttribution(
                stage="intent_classifier",
                model="gpt-4o-mini",
                latency_ms=120.5,
                tokens_input=50,
                tokens_output=10,
                cost_estimate=0.0002,
            ),
            StageAttribution(
                stage="response_generator",
                model="gpt-4o",
                latency_ms=850.3,
                tokens_input=500,
                tokens_output=200,
                cost_estimate=0.015,
            ),
        ],
        total_latency_ms=1200.8,
        total_cost_estimate=0.0152,
        # Critic (structural — exported)
        critic=CriticAssessment(
            verdict="approved",
            flags=["tone_check"],
            modifications=[],
            latency_ms=95.2,
        ),
        # Intent (structural — exported)
        detected_intent="product_return",
        intent_confidence=0.94,
        # Route (structural — exported)
        route_target="core_pipeline",
        route_agent_id=None,
        route_fallback_from=None,
        # Response metadata (content-bearing)
        response_language="en",
        was_escalated=False,
        escalation_reason="Customer requested manager",
    )


# ---------------------------------------------------------------------------
# Hashing tests
# ---------------------------------------------------------------------------


@patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
class TestHashing:
    """Verify hashing is SHA-256, irreversible, and salted."""

    def test_hash_is_sha256_based(self):
        """Hash output matches SHA-256 hex prefix."""
        result = _hash_id("test-value")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_is_deterministic(self):
        """Same input produces same hash."""
        assert _hash_id("conv-123") == _hash_id("conv-123")

    def test_hash_differs_for_different_inputs(self):
        """Different inputs produce different hashes."""
        assert _hash_id("conv-123") != _hash_id("conv-456")

    def test_hash_is_not_base64(self):
        """Hash is hex, not base64 (no +, /, = characters)."""
        result = _hash_id("test")
        assert "+" not in result
        assert "/" not in result
        assert "=" not in result

    def test_hash_includes_salt(self):
        """Hash with salt differs from raw SHA-256."""
        raw_sha = hashlib.sha256("test".encode()).hexdigest()[:16]
        salted = _hash_id("test")
        assert salted != raw_sha

    def test_prompt_version_hash_deterministic(self):
        """Same template produces same version hash."""
        template = "You are a helpful assistant for {{tenant_name}}."
        h1 = _prompt_version_hash(template)
        h2 = _prompt_version_hash(template)
        assert h1 == h2
        assert len(h1) == 12

    def test_prompt_version_hash_differs_for_changes(self):
        """Different templates produce different version hashes."""
        h1 = _prompt_version_hash("Template A")
        h2 = _prompt_version_hash("Template B")
        assert h1 != h2


# ---------------------------------------------------------------------------
# Lane 1 payload tests
# ---------------------------------------------------------------------------


class TestBuildLane1Payload:
    """Verify Lane 1 export contains ONLY structural fields."""

    def test_contains_hashed_identifiers(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert "conversation_id_hash" in payload
        assert "tenant_id_hash" in payload
        # Hashed, not raw
        assert payload["conversation_id_hash"] != sample_trace.conversation_id
        assert payload["tenant_id_hash"] != sample_trace.tenant_id

    def test_contains_intent_fields(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["detected_intent"] == "product_return"
        assert payload["intent_confidence"] == 0.94

    def test_contains_route_fields(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["route_target"] == "core_pipeline"
        assert payload["route_agent_id"] is None
        assert payload["route_fallback_from"] is None

    def test_contains_stage_attributions(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        stages = payload["stage_attributions"]
        assert len(stages) == 2
        assert stages[0]["stage"] == "intent_classifier"
        assert stages[0]["model"] == "gpt-4o-mini"
        assert stages[0]["latency_ms"] == 120.5
        assert stages[0]["tokens_input"] == 50
        assert stages[1]["stage"] == "response_generator"

    def test_contains_critic_assessment(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["critic_verdict"] == "approved"
        assert payload["critic_flags"] == ["tone_check"]
        assert payload["critic_latency_ms"] == 95.2

    def test_contains_timing(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["total_latency_ms"] == 1200.8

    def test_contains_ab_testing(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["ab_variant"] == "treatment_v2"
        assert payload["ab_experiment_id"] == "exp-tone-test"

    def test_contains_knowledge_count_only(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["knowledge_results_count"] == 2

    def test_contains_prompt_version_hash(self, sample_trace):
        payload = build_lane1_payload(
            sample_trace,
            system_prompt_template="You are helpful.",
        )
        assert payload["prompt_version_hash"] is not None
        assert len(payload["prompt_version_hash"]) == 12

    def test_no_prompt_hash_when_no_template(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        assert payload["prompt_version_hash"] is None

    # -- Content exclusion tests (critical for ZK compliance) --

    def test_no_raw_conversation_id(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "conv-abc-123" not in payload_str

    def test_no_raw_tenant_id(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "tenant-xyz-789" not in payload_str

    def test_no_customer_id(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "cust-secret-456" not in payload_str

    def test_no_knowledge_query(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "how do I return" not in payload_str

    def test_no_knowledge_titles(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "Return Policy Details" not in payload_str
        assert "Widget Pro Max" not in payload_str

    def test_no_memory_summaries(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "previously asked about refunds" not in payload_str

    def test_no_escalation_reason(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "requested manager" not in payload_str

    def test_no_profile_factors(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "order_history" not in payload_str

    def test_no_profile_data_sources(self, sample_trace):
        payload = build_lane1_payload(sample_trace)
        payload_str = str(payload)
        assert "shopify" not in payload_str
        assert "crm" not in payload_str


# ---------------------------------------------------------------------------
# Content-bearing field exclusion (exhaustive check)
# ---------------------------------------------------------------------------


class TestContentFieldExclusion:
    """Verify the _CONTENT_BEARING_FIELDS set is complete and enforced."""

    def test_content_fields_set_complete(self):
        """All known content-bearing fields are in the exclusion set."""
        expected = {
            "knowledge_query",
            "knowledge_sources",
            "memory_signals",
            "escalation_reason",
            "profile_factors_used",
            "profile_data_sources",
            "customer_id",
            "conversation_id",
            "tenant_id",
        }
        assert _CONTENT_BEARING_FIELDS == expected

    def test_payload_keys_dont_match_content_fields(self, sample_trace):
        """No payload key matches a content-bearing field name exactly."""
        payload = build_lane1_payload(sample_trace)
        for key in payload:
            assert key not in _CONTENT_BEARING_FIELDS, (
                f"Content-bearing field '{key}' leaked into Lane 1 payload"
            )


# ---------------------------------------------------------------------------
# Export function tests
# ---------------------------------------------------------------------------


class TestExportTrace:
    """Verify fire-and-forget behavior and toggle."""

    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", False)
    def test_disabled_is_noop(self, sample_trace):
        """When disabled, export_trace does nothing."""
        from src.observability.langfuse_exporter import export_trace

        # Should not raise, should not call anything
        export_trace(sample_trace, trace_id="test-123")

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_client_none_is_noop(self, mock_get_client, sample_trace):
        """When client returns None, export is a no-op."""
        from src.observability.langfuse_exporter import export_trace

        mock_get_client.return_value = None
        export_trace(sample_trace, trace_id="test-123")

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_successful_export(self, mock_get_client, sample_trace):
        """Successful export creates trace with spans and flushes (v3 API)."""
        from src.observability.langfuse_exporter import export_trace

        mock_client = MagicMock()
        # v3 API: start_as_current_observation returns a context manager
        mock_ctx = MagicMock()
        mock_client.start_as_current_observation.return_value = mock_ctx
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_get_client.return_value = mock_client

        export_trace(sample_trace, trace_id="trace-001")

        # v3: uses start_as_current_observation, not trace()
        assert mock_client.start_as_current_observation.call_count >= 1
        root_call = mock_client.start_as_current_observation.call_args_list[0]
        assert root_call.kwargs["name"] == "agent-red-pipeline"
        assert root_call.kwargs["trace_id"] == "trace-001"
        assert "intent:product_return" in root_call.kwargs["tags"]

        # Root span + child spans for each stage (2 in fixture)
        assert mock_client.start_as_current_observation.call_count == 3
        mock_client.flush.assert_called_once()

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_exception_swallowed(self, mock_get_client, sample_trace):
        """Exporter exceptions are swallowed, not propagated."""
        from src.observability.langfuse_exporter import export_trace

        mock_client = MagicMock()
        mock_client.start_as_current_observation.side_effect = RuntimeError(
            "Langfuse down"
        )
        mock_get_client.return_value = mock_client

        # Should not raise
        export_trace(sample_trace, trace_id="trace-001")


# ---------------------------------------------------------------------------
# Empty/minimal trace tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Verify exporter handles edge cases gracefully."""

    def test_empty_trace(self):
        """Minimal trace with defaults produces valid payload."""
        trace = ResponseDecisionTrace()
        payload = build_lane1_payload(trace)
        assert payload["detected_intent"] == ""
        assert payload["stage_attributions"] == []
        assert payload["knowledge_results_count"] == 0
        assert payload["prompt_version_hash"] is None

    def test_trace_with_no_stages(self):
        """Trace with no stage attributions produces empty list."""
        trace = ResponseDecisionTrace(
            detected_intent="greeting",
            intent_confidence=0.99,
        )
        payload = build_lane1_payload(trace)
        assert payload["stage_attributions"] == []

    def test_trace_with_many_stages(self):
        """Trace with many stages exports all of them."""
        stages = [
            StageAttribution(stage=f"stage_{i}", model="gpt-4o-mini")
            for i in range(10)
        ]
        trace = ResponseDecisionTrace(stage_attributions=stages)
        payload = build_lane1_payload(trace)
        assert len(payload["stage_attributions"]) == 10


# ---------------------------------------------------------------------------
# Phase 0: Critic flag normalization tests (S251 ZK boundary fix)
# ---------------------------------------------------------------------------


class TestCriticFlagNormalization:
    """Verify critic.flags are normalized to a closed safe set."""

    def test_safe_flags_pass_through(self):
        """Known safe flags are preserved."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        result = _normalize_critic_flags(["tone_check", "pii_leakage"])
        assert result == ["tone_check", "pii_leakage"]

    def test_unknown_flags_become_other(self):
        """Free-form model output maps to 'other'."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        result = _normalize_critic_flags([
            "customer said their email is john@example.com",
            "mentions internal KB article about returns",
        ])
        assert result == ["other", "other"]

    def test_alias_matching(self):
        """Substring aliases resolve to safe flags."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        result = _normalize_critic_flags([
            "potential pii leak detected",
            "medical recommendation",
        ])
        assert result == ["pii_leakage", "medical_advice"]

    def test_case_insensitive(self):
        """Flag matching is case-insensitive."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        result = _normalize_critic_flags(["TONE_CHECK", "Policy_Contradiction"])
        assert result == ["tone_check", "policy_contradiction"]

    def test_adversarial_flags_with_pii(self):
        """Flags containing customer PII are safely normalized to 'other'."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        adversarial = [
            "user john.doe@example.com asked about returns",
            "order #12345 has shipping issue",
            "customer phone (555) 123-4567 mentioned",
        ]
        result = _normalize_critic_flags(adversarial)
        assert all(f == "other" for f in result), f"PII leaked via flags: {result}"

    def test_empty_flags(self):
        """Empty flags list returns empty."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        assert _normalize_critic_flags([]) == []

    def test_flags_normalized_in_payload(self, sample_trace):
        """build_lane1_payload applies normalization."""
        sample_trace.critic.flags = [
            "tone_check",
            "customer wants refund on Widget Pro",
        ]
        payload = build_lane1_payload(sample_trace)
        assert payload["critic_flags"] == ["tone_check", "other"]

    def test_internal_code_preserved(self):
        """Internal Critic code passes through."""
        from src.observability.langfuse_exporter import _normalize_critic_flags

        result = _normalize_critic_flags(["modified_verdict_without_text"])
        assert result == ["modified_verdict_without_text"]


# ---------------------------------------------------------------------------
# Phase 0: Hash salt fail-closed tests (S251)
# ---------------------------------------------------------------------------


class TestHashSaltFailClosed:
    """Verify export is disabled when LANGFUSE_HASH_SALT is not set."""

    @patch("src.observability.langfuse_exporter._HASH_SALT", "")
    def test_hash_id_returns_empty_without_salt(self):
        """_hash_id returns empty string when salt is not configured."""
        from src.observability.langfuse_exporter import _hash_id

        assert _hash_id("some-value") == ""

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    def test_hash_id_works_with_salt(self):
        """_hash_id produces a 16-char hex hash when salt is set."""
        from src.observability.langfuse_exporter import _hash_id

        result = _hash_id("test-value")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    @patch("src.observability.langfuse_exporter._HASH_SALT", "")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    def test_export_disabled_without_salt(self, sample_trace):
        """export_trace is a no-op when salt is empty."""
        from src.observability.langfuse_exporter import export_trace

        # Should not raise or call any client
        export_trace(sample_trace, trace_id="test-123")

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    def test_hash_deterministic(self):
        """Same input + same salt = same hash."""
        from src.observability.langfuse_exporter import _hash_id

        assert _hash_id("conv-123") == _hash_id("conv-123")


# ---------------------------------------------------------------------------
# Phase 2: PII scrubber tests (S251)
# ---------------------------------------------------------------------------


class TestPiiScrubber:
    """Verify the union PII scrubber covers all pattern classes."""

    def test_scrub_email(self):
        assert _scrub_for_export("contact john@example.com") == "contact [EMAIL]"

    def test_scrub_phone_us(self):
        assert "[PHONE]" in _scrub_for_export("call (555) 123-4567 now")

    def test_scrub_phone_dashed(self):
        assert "[PHONE]" in _scrub_for_export("reach me at 555-123-4567")

    def test_scrub_order_hash(self):
        assert _scrub_for_export("order #12345 status") == "order [ORDER] status"

    def test_scrub_order_prefix(self):
        assert "[ORDER]" in _scrub_for_export("check ORD-98765")

    def test_scrub_shopify_token(self):
        assert _scrub_for_export("token shpat_abc123def") == "token [SHOPIFY_TOKEN]"

    def test_scrub_stripe_key(self):
        assert _scrub_for_export("key sk_live_abc123") == "key [STRIPE_KEY]"

    def test_scrub_ar_api_key(self):
        assert _scrub_for_export("key ar_spa_test123") == "key [API_KEY]"

    def test_scrub_clean_passthrough(self):
        clean = "how do I return a widget?"
        assert _scrub_for_export(clean) == clean

    def test_scrub_multiple_patterns(self):
        mixed = "email john@test.com phone 555-123-4567 order #12345"
        result = _scrub_for_export(mixed)
        assert "[EMAIL]" in result
        assert "[PHONE]" in result
        assert "[ORDER]" in result
        assert "john@test.com" not in result


# ---------------------------------------------------------------------------
# Phase 2: Prompt field band tests (S251)
# ---------------------------------------------------------------------------


class TestPromptFieldBand:
    """Verify bucketing avoids exact-count fingerprinting."""

    def test_band_none(self):
        assert _prompt_field_band(0) == "none"

    def test_band_few(self):
        assert _prompt_field_band(1) == "few"
        assert _prompt_field_band(3) == "few"

    def test_band_moderate(self):
        assert _prompt_field_band(4) == "moderate"
        assert _prompt_field_band(6) == "moderate"

    def test_band_extensive(self):
        assert _prompt_field_band(7) == "extensive"
        assert _prompt_field_band(15) == "extensive"


# ---------------------------------------------------------------------------
# Phase 2: Lane 2 payload tests (S251)
# ---------------------------------------------------------------------------


@patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
class TestBuildLane2Payload:
    """Verify Lane 2 payload structure, content exclusion, and ZK compliance."""

    def test_lane2_superset_of_lane1(self, sample_trace):
        """Every Lane 1 key must appear in Lane 2."""
        lane1 = build_lane1_payload(sample_trace)
        lane2 = build_lane2_payload(sample_trace)
        for key in lane1:
            assert key in lane2, f"Lane 1 key '{key}' missing from Lane 2"

    def test_lane2_has_enriched_fields(self, sample_trace):
        """Lane 2 includes fields not in Lane 1."""
        lane2 = build_lane2_payload(sample_trace)
        enriched_keys = {
            "message_index", "timestamp", "profile_factors_used",
            "profile_data_sources", "profile_is_stale", "profile_is_empty",
            "knowledge_sources", "knowledge_query_scrubbed",
            "memory_signal_count", "memory_signals",
            "memory_consent_status", "memory_history_depth_days",
            "tenant_prompt_field_band", "custom_instructions_present",
            "config_version", "total_cost_estimate",
            "response_language", "was_escalated",
        }
        for key in enriched_keys:
            assert key in lane2, f"Expected Lane 2 key '{key}' missing"

    def test_lane2_knowledge_sources_stripped(self, sample_trace):
        """Knowledge sources have no title or matched_query."""
        lane2 = build_lane2_payload(sample_trace)
        for ks in lane2["knowledge_sources"]:
            assert "title" not in ks
            assert "matched_query" not in ks
            assert "entry_id_hash" in ks
            assert "entry_type" in ks
            assert "relevance_score" in ks

    def test_lane2_entry_id_hashed(self, sample_trace):
        """entry_id is hashed, not raw."""
        lane2 = build_lane2_payload(sample_trace)
        for ks in lane2["knowledge_sources"]:
            assert ks["entry_id_hash"] != "kb-1"
            assert ks["entry_id_hash"] != "kb-2"
            assert len(ks["entry_id_hash"]) == 16

    def test_lane2_memory_signals_stripped(self, sample_trace):
        """Memory signals have no chunk_summary or source_conversation_id."""
        lane2 = build_lane2_payload(sample_trace)
        for ms in lane2["memory_signals"]:
            assert "chunk_summary" not in ms
            assert "source_conversation_id" not in ms
            assert "layer" in ms
            assert "similarity_score" in ms
            assert "signal_type" in ms

    def test_lane2_knowledge_query_scrubbed(self):
        """knowledge_query is PII-scrubbed before export."""
        trace = ResponseDecisionTrace(
            knowledge_query="my email is john@test.com order #12345",
        )
        lane2 = build_lane2_payload(trace)
        assert "john@test.com" not in lane2["knowledge_query_scrubbed"]
        assert "[EMAIL]" in lane2["knowledge_query_scrubbed"]
        assert "[ORDER]" in lane2["knowledge_query_scrubbed"]

    def test_lane2_zk_compliance_stringify_scan(self, sample_trace):
        """Serialize entire Lane 2 payload — no prohibited content appears."""
        import json as json_mod

        lane2 = build_lane2_payload(sample_trace)
        serialized = json_mod.dumps(lane2, default=str)

        # These strings are on the fixture trace but must NOT appear in export
        prohibited = [
            "Return Policy Details",  # knowledge_sources[].title
            "Widget Pro Max",          # knowledge_sources[].title
            "how to return",           # knowledge_sources[].matched_query
            "widget specs",            # knowledge_sources[].matched_query
            "Customer previously asked about refunds",  # memory chunk_summary
            "conv-old",                # memory source_conversation_id
            "Customer requested manager",  # escalation_reason
            "conv-abc-123",            # raw conversation_id
            "tenant-xyz-789",          # raw tenant_id
            "cust-secret-456",         # raw customer_id
        ]
        for text in prohibited:
            assert text not in serialized, f"Prohibited content leaked: {text}"

    def test_lane2_adversarial_zk(self):
        """PII-laden trace fields don't leak through Lane 2."""
        import json as json_mod

        trace = ResponseDecisionTrace(
            conversation_id="conv-123",
            tenant_id="tenant-456",
            customer_id="cust-789",
            knowledge_query="john.doe@evil.com wants refund on #99999",
            escalation_reason="Customer john.doe@evil.com is angry about order #99999",
        )
        trace.knowledge_sources.append(KnowledgeSource(
            entry_id="kb-secret",
            title="Internal: Customer john.doe@evil.com refund case",
            relevance_score=0.95,
            matched_query="john.doe@evil.com refund",
        ))
        trace.memory_signals.append(MemorySignal(
            layer=2,
            source_conversation_id="conv-private-session",
            chunk_summary="Customer SSN is 123-45-6789",
            similarity_score=0.9,
        ))

        lane2 = build_lane2_payload(trace)
        serialized = json_mod.dumps(lane2, default=str)

        assert "john.doe@evil.com" not in serialized
        assert "conv-private-session" not in serialized
        assert "123-45-6789" not in serialized
        assert "Internal: Customer" not in serialized
        assert "conv-123" not in serialized
        assert "tenant-456" not in serialized
        assert "cust-789" not in serialized

    def test_lane2_was_escalated_bool(self, sample_trace):
        """was_escalated is exported as boolean."""
        lane2 = build_lane2_payload(sample_trace)
        assert isinstance(lane2["was_escalated"], bool)

    def test_lane2_config_version_int(self, sample_trace):
        """config_version is exported as integer."""
        lane2 = build_lane2_payload(sample_trace)
        assert isinstance(lane2["config_version"], int)

    def test_lane2_response_language(self, sample_trace):
        """response_language is exported."""
        lane2 = build_lane2_payload(sample_trace)
        assert lane2["response_language"] == "en"

    def test_lane2_all_entry_types(self):
        """All 5 entry types are handled correctly."""
        trace = ResponseDecisionTrace()
        for et in ("product", "faq", "policy", "custom", "article"):
            trace.knowledge_sources.append(KnowledgeSource(
                entry_id=f"kb-{et}", entry_type=et, relevance_score=0.5,
            ))
        lane2 = build_lane2_payload(trace)
        types = [ks["entry_type"] for ks in lane2["knowledge_sources"]]
        assert types == ["product", "faq", "policy", "custom", "article"]

    def test_lane2_empty_trace(self):
        """Minimal trace produces valid Lane 2 payload."""
        trace = ResponseDecisionTrace()
        lane2 = build_lane2_payload(trace)
        assert lane2["knowledge_sources"] == []
        assert lane2["memory_signals"] == []
        assert lane2["memory_signal_count"] == 0
        assert lane2["tenant_prompt_field_band"] == "none"
        assert lane2["knowledge_query_scrubbed"] == ""

    def test_lane2_prompt_field_band_from_trace(self):
        """tenant_prompt_field_band is computed from config_overrides_applied."""
        trace = ResponseDecisionTrace(
            config_overrides_applied=["brand_name", "brand_voice", "return_policy",
                                      "shipping_info", "escalation_keywords"],
        )
        lane2 = build_lane2_payload(trace)
        assert lane2["tenant_prompt_field_band"] == "moderate"  # 5 fields


# ---------------------------------------------------------------------------
# Phase 2: Tenant allowlist gate tests (S251)
# ---------------------------------------------------------------------------


class TestTenantAllowlistGate:
    """Verify Lane 2 is only activated for opted-in tenants."""

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_tenant_opted_in_gets_lane2(self, mock_get_client, sample_trace):
        """Opted-in tenant triggers Lane 2 payload."""
        from src.observability.langfuse_exporter import export_trace

        mock_client = MagicMock()
        mock_ctx = MagicMock()
        mock_client.start_as_current_observation.return_value = mock_ctx
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_get_client.return_value = mock_client

        prefs = MagicMock()
        prefs.langfuse_lane2_enabled = True

        export_trace(sample_trace, trace_id="t-1", tenant_preferences=prefs)

        root_call = mock_client.start_as_current_observation.call_args_list[0]
        metadata = root_call.kwargs["metadata"]
        # Lane 2 has enriched fields
        assert "knowledge_sources" in metadata
        assert "memory_signals" in metadata
        assert "lane:2" in root_call.kwargs["tags"]

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_tenant_opted_out_gets_lane1(self, mock_get_client, sample_trace):
        """Opted-out tenant gets Lane 1 only."""
        from src.observability.langfuse_exporter import export_trace

        mock_client = MagicMock()
        mock_ctx = MagicMock()
        mock_client.start_as_current_observation.return_value = mock_ctx
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_get_client.return_value = mock_client

        prefs = MagicMock()
        prefs.langfuse_lane2_enabled = False

        export_trace(sample_trace, trace_id="t-1", tenant_preferences=prefs)

        root_call = mock_client.start_as_current_observation.call_args_list[0]
        metadata = root_call.kwargs["metadata"]
        # Lane 1 does NOT have enriched fields
        assert "knowledge_sources" not in metadata
        assert "memory_signals" not in metadata
        assert "lane:1" in root_call.kwargs["tags"]

    @patch("src.observability.langfuse_exporter._HASH_SALT", "test-salt")
    @patch("src.observability.langfuse_exporter.LANGFUSE_ENABLED", True)
    @patch("src.observability.langfuse_exporter._get_client")
    def test_no_preferences_gets_lane1(self, mock_get_client, sample_trace):
        """No preferences object defaults to Lane 1."""
        from src.observability.langfuse_exporter import export_trace

        mock_client = MagicMock()
        mock_ctx = MagicMock()
        mock_client.start_as_current_observation.return_value = mock_ctx
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_get_client.return_value = mock_client

        export_trace(sample_trace, trace_id="t-1", tenant_preferences=None)

        root_call = mock_client.start_as_current_observation.call_args_list[0]
        metadata = root_call.kwargs["metadata"]
        assert "knowledge_sources" not in metadata
        assert "lane:1" in root_call.kwargs["tags"]
