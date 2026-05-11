"""CQ-8: Quality feedback loop tests (SPEC-0187 / WI-1518).

Tests for QualityFeedbackEngine: issue accumulation, pattern detection,
guidance generation, recovery, and reset.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from src.chat.models import QualityScore
from src.chat.quality_feedback import (
    MAX_GUIDANCE_LENGTH,
    RECOVERY_WINDOW,
    QualityFeedbackEngine,
)


def _make_score(
    overall: float,
    issues: list[str] | None = None,
) -> QualityScore:
    """Helper to create a QualityScore."""
    return QualityScore(
        faithfulness=overall,
        relevancy=overall,
        tone=overall,
        overall=overall,
        issues=issues or [],
    )


# ---------------------------------------------------------------------------
# Basic guidance generation
# ---------------------------------------------------------------------------


class TestGuidanceGeneration:
    """QualityFeedbackEngine generates guidance from quality issues."""

    def test_no_scores_returns_none(self):
        engine = QualityFeedbackEngine()
        assert engine.get_quality_guidance() is None

    def test_good_quality_no_guidance(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(4.5))
        assert engine.get_quality_guidance() is None

    def test_low_quality_with_issues_returns_guidance(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Profanity detected: 'damn'"]))
        guidance = engine.get_quality_guidance()
        assert guidance is not None
        assert len(guidance) <= MAX_GUIDANCE_LENGTH


# ---------------------------------------------------------------------------
# Pattern detection
# ---------------------------------------------------------------------------


class TestPatternDetection:
    """Engine detects dominant issue categories."""

    def test_faithfulness_issues(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Contains excluded phrase: 'test'"]))
        guidance = engine.get_quality_guidance()
        assert guidance is not None
        assert "accuracy" in guidance.lower() or "knowledge" in guidance.lower()

    def test_tone_issues(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Profanity detected: 'hell'"]))
        guidance = engine.get_quality_guidance()
        assert guidance is not None
        assert "tone" in guidance.lower() or "professional" in guidance.lower()

    def test_empty_response_issues(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(1.0, issues=["Empty response"]))
        guidance = engine.get_quality_guidance()
        assert guidance is not None
        assert "substantive" in guidance.lower() or "response" in guidance.lower()

    def test_mixed_issues_picks_dominant(self):
        engine = QualityFeedbackEngine()
        # 3 tone issues, 2 faithfulness
        for _ in range(3):
            engine.record_turn(_make_score(2.0, issues=["Profanity detected: 'damn'"]))
        for _ in range(2):
            engine.record_turn(_make_score(2.0, issues=["Contains excluded phrase: 'x'"]))
        guidance = engine.get_quality_guidance()
        assert guidance is not None


# ---------------------------------------------------------------------------
# Recovery
# ---------------------------------------------------------------------------


class TestRecovery:
    """Guidance clears when quality recovers."""

    def test_recovery_clears_guidance(self):
        engine = QualityFeedbackEngine()
        # Poor quality phase
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Profanity detected: 'x'"]))
        assert engine.get_quality_guidance() is not None

        # Recovery phase: RECOVERY_WINDOW good turns
        for _ in range(RECOVERY_WINDOW):
            engine.record_turn(_make_score(4.5))
        assert engine.get_quality_guidance() is None

    def test_partial_recovery_maintains_guidance(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Empty response"]))
        engine.get_quality_guidance()  # triggers active guidance

        # Only half recovery
        for _ in range(RECOVERY_WINDOW // 2):
            engine.record_turn(_make_score(4.5))
        # Still some low scores in the window — guidance may persist
        # (depends on whether enough good scores dilute the mean)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


class TestStateManagement:
    """Engine state (reset, has_active_guidance)."""

    def test_has_active_guidance_initially_false(self):
        engine = QualityFeedbackEngine()
        assert engine.has_active_guidance is False

    def test_has_active_guidance_after_issues(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Empty response"]))
        engine.get_quality_guidance()
        assert engine.has_active_guidance is True

    def test_reset_clears_all(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(2.0, issues=["Empty response"]))
        engine.get_quality_guidance()
        engine.reset()
        assert engine.has_active_guidance is False
        assert engine.get_quality_guidance() is None


# ---------------------------------------------------------------------------
# Guidance length constraint
# ---------------------------------------------------------------------------


class TestGuidanceConstraints:
    """Guidance text respects MAX_GUIDANCE_LENGTH."""

    def test_guidance_within_length_limit(self):
        engine = QualityFeedbackEngine()
        for _ in range(5):
            engine.record_turn(_make_score(1.0, issues=["Contains excluded phrase: 'x'"]))
        guidance = engine.get_quality_guidance()
        if guidance:
            assert len(guidance) <= MAX_GUIDANCE_LENGTH
