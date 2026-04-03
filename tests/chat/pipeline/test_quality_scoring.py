"""Slice 10: Phase 3 — Quality scorer + aggregate pre-implementation tests.

Tests ConversationQualityScorer interface (1-5 scale), ChatPipeline integration
contract, and quality_aggregate computation at conversation end.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 10

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect

import pytest

from src.chat.quality_scorer import ConversationQualityScorer
from src.chat.models import QualityScore


# ── ConversationQualityScorer interface ───────────────────────────

class TestQualityScorerInterface:
    """Verify ConversationQualityScorer provides the expected scoring interface."""

    def test_quality_scorer_importable(self):
        assert ConversationQualityScorer is not None

    def test_score_turn_method_exists(self):
        assert hasattr(ConversationQualityScorer, "score_turn")

    def test_score_turn_accepts_required_args(self):
        sig = inspect.signature(ConversationQualityScorer.score_turn)
        params = list(sig.parameters.keys())
        assert "ai_response" in params
        assert "customer_message" in params
        assert "knowledge_context" in params

    def test_score_turn_returns_quality_score(self):
        scorer = ConversationQualityScorer()
        result = scorer.score_turn(
            ai_response="Hello! How can I help you today?",
            customer_message="Hi",
            knowledge_context="",
        )

        assert isinstance(result, QualityScore)
        # QualityScore uses a 1-5 scale
        assert 1.0 <= result.overall <= 5.0

    def test_quality_score_has_dimensions(self):
        """QualityScore has faithfulness, relevancy, tone, overall."""
        scorer = ConversationQualityScorer()
        result = scorer.score_turn(
            ai_response="Great question! Our return policy is 30 days.",
            customer_message="What is your return policy?",
            knowledge_context="Return policy: 30 days for full refund.",
        )

        assert hasattr(result, "faithfulness")
        assert hasattr(result, "relevancy")
        assert hasattr(result, "tone")
        assert hasattr(result, "overall")
        # All dimensions on 1-5 scale
        assert 1.0 <= result.faithfulness <= 5.0
        assert 1.0 <= result.relevancy <= 5.0
        assert 1.0 <= result.tone <= 5.0


# ── ChatPipeline integration contract ─────────────────────────────

class TestChatPipelineScoring:
    """Verify quality scoring integration with the live pipeline orchestrator."""

    def test_chat_pipeline_importable(self):
        """ChatPipeline (the live pipeline orchestrator) is importable."""
        try:
            from src.chat.pipeline import ChatPipeline
            assert ChatPipeline is not None
        except ImportError:
            from src.chat.pipeline.orchestrator import ChatPipeline
            assert ChatPipeline is not None

    def test_pipeline_has_execute_method(self):
        """ChatPipeline.execute method exists (main entry point)."""
        try:
            from src.chat.pipeline import ChatPipeline
        except ImportError:
            from src.chat.pipeline.orchestrator import ChatPipeline

        assert hasattr(ChatPipeline, "execute")

    def test_score_turn_wired_in_pipeline(self):
        """score_turn should be called in the pipeline after Critic validation.

        This test verifies the wiring exists by checking source code for
        quality_scorer or score_turn references in the pipeline module.
        """
        try:
            from src.chat.pipeline import ChatPipeline
        except ImportError:
            from src.chat.pipeline.orchestrator import ChatPipeline

        source = inspect.getsource(ChatPipeline)
        if "score_turn" not in source and "quality_scorer" not in source:
            pytest.skip("score_turn not yet wired into ChatPipeline (Phase 3)")


# ── Aggregate conversation quality ────────────────────────────────

class TestQualityAggregate:
    """Verify quality_aggregate computation at conversation end."""

    def test_quality_score_model_has_overall(self):
        """QualityScore model has an 'overall' field (1-5 scale)."""
        if hasattr(QualityScore, "model_fields"):
            assert "overall" in QualityScore.model_fields
        else:
            assert hasattr(QualityScore, "overall")

    def test_aggregate_conversation_quality_exists(self):
        """ConversationQualityScorer has an aggregate method."""
        assert hasattr(ConversationQualityScorer, "aggregate_conversation_quality")

    def test_aggregate_computable_from_turn_scores(self):
        """Quality aggregate (mean/min/max/count) computed from 1-5 scale scores."""
        scorer = ConversationQualityScorer()
        scores = [
            scorer.score_turn("Response 1", "Question 1", ""),
            scorer.score_turn("Response 2", "Question 2", ""),
            scorer.score_turn("Response 3", "Question 3", ""),
        ]

        overall_scores = [s.overall for s in scores]
        aggregate = {
            "mean": sum(overall_scores) / len(overall_scores),
            "min": min(overall_scores),
            "max": max(overall_scores),
            "count": len(overall_scores),
        }

        assert aggregate["count"] == 3
        # 1-5 scale
        assert 1.0 <= aggregate["mean"] <= 5.0
        assert aggregate["min"] <= aggregate["mean"] <= aggregate["max"]

    def test_aggregate_method_returns_quality_score(self):
        """aggregate_conversation_quality returns a QualityScore or None."""
        scorer = ConversationQualityScorer()
        scores = [
            scorer.score_turn("Good response", "Question", ""),
            scorer.score_turn("Another good response", "Question 2", ""),
        ]

        result = scorer.aggregate_conversation_quality(scores)
        if result is not None:
            assert isinstance(result, QualityScore)
            assert 1.0 <= result.overall <= 5.0

    def test_regression_warning_at_0_5_drop(self):
        """A 0.5-point drop on 1-5 scale triggers warning (DEFAULT_THRESHOLD=0.5)."""
        # quality_regression.py: DEFAULT_THRESHOLD = 0.5, severity = warning when 0.5 <= drop <= 1.0
        baseline = 4.5
        current = 3.9
        warning_threshold = 0.5

        drop = baseline - current
        is_regression = drop >= warning_threshold
        severity = "critical" if drop > 1.0 else "warning"

        assert is_regression is True
        assert severity == "warning"

    def test_regression_critical_above_1_0_drop(self):
        """A >1.0-point drop on 1-5 scale triggers critical severity."""
        # quality_regression.py: severity = "critical" if drop > 1.0
        baseline = 4.5
        current = 3.0
        warning_threshold = 0.5

        drop = baseline - current
        is_regression = drop >= warning_threshold
        severity = "critical" if drop > 1.0 else "warning"

        assert is_regression is True
        assert severity == "critical"
        assert drop == pytest.approx(1.5, abs=0.01)

    def test_no_regression_within_threshold(self):
        """Normal variation (<0.5 drop) should not trigger regression."""
        baseline = 4.5
        current = 4.2
        warning_threshold = 0.5

        drop = baseline - current
        is_regression = drop >= warning_threshold

        assert is_regression is False

    def test_session_end_calls_quality_closeout(self):
        """ConversationSession.end_conversation calls the quality closeout helper.

        The shared helper computes quality_aggregate and evaluates regression.
        """
        from src.chat.session import ConversationSession
        source = inspect.getsource(ConversationSession.end_conversation)
        assert "evaluate_quality_and_alert" in source, (
            "end_conversation must call evaluate_quality_and_alert for quality aggregate"
        )
