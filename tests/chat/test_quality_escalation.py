"""CQ-6: Quality-aware escalation tests (SPEC-0185 / WI-1516).

Tests for should_quality_escalate(), QualityEscalationConfig, and
QualityEscalationRecommendation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from src.chat.models import QualityScore
from src.chat.quality_escalation import (
    QualityEscalationConfig,
    QualityEscalationRecommendation,
    should_quality_escalate,
)


def _make_score(overall: float) -> QualityScore:
    """Helper to create a QualityScore with a given overall value."""
    return QualityScore(
        faithfulness=overall,
        relevancy=overall,
        tone=overall,
        overall=overall,
    )


# ---------------------------------------------------------------------------
# Config model
# ---------------------------------------------------------------------------


class TestQualityEscalationConfig:
    """QualityEscalationConfig has sensible defaults."""

    def test_default_config(self):
        cfg = QualityEscalationConfig()
        assert cfg.escalation_threshold == 2.5
        assert cfg.consecutive_low_turns == 3
        assert cfg.enabled is True

    def test_custom_config(self):
        cfg = QualityEscalationConfig(
            escalation_threshold=3.0,
            consecutive_low_turns=5,
            enabled=False,
        )
        assert cfg.escalation_threshold == 3.0
        assert cfg.consecutive_low_turns == 5
        assert cfg.enabled is False


# ---------------------------------------------------------------------------
# No escalation cases
# ---------------------------------------------------------------------------


class TestNoEscalation:
    """should_quality_escalate returns no-escalate for good quality."""

    def test_good_scores_no_escalation(self):
        scores = [_make_score(4.0) for _ in range(5)]
        result = should_quality_escalate(scores)
        assert result.should_escalate is False
        assert result.severity == "none"

    def test_empty_scores(self):
        result = should_quality_escalate([])
        assert result.should_escalate is False

    def test_disabled_config(self):
        scores = [_make_score(1.0) for _ in range(5)]
        cfg = QualityEscalationConfig(enabled=False)
        result = should_quality_escalate(scores, config=cfg)
        assert result.should_escalate is False

    def test_insufficient_consecutive_turns(self):
        # 2 low turns but need 3 consecutive
        scores = [_make_score(4.0), _make_score(1.5), _make_score(1.5)]
        result = should_quality_escalate(scores)
        assert result.should_escalate is False


# ---------------------------------------------------------------------------
# Escalation triggered
# ---------------------------------------------------------------------------


class TestEscalationTriggered:
    """should_quality_escalate triggers on consecutive low-quality turns."""

    def test_three_consecutive_low(self):
        scores = [_make_score(4.0), _make_score(2.0), _make_score(2.0), _make_score(2.0)]
        result = should_quality_escalate(scores)
        assert result.should_escalate is True
        assert result.severity in ("warning", "critical")
        assert len(result.recent_scores) == 3

    def test_critical_severity_very_low(self):
        scores = [_make_score(4.0)] + [_make_score(1.5) for _ in range(3)]
        result = should_quality_escalate(scores)
        assert result.should_escalate is True
        assert result.severity == "critical"

    def test_warning_severity_moderate_low(self):
        scores = [_make_score(4.0)] + [_make_score(2.2) for _ in range(3)]
        result = should_quality_escalate(scores)
        assert result.should_escalate is True
        assert result.severity == "warning"


# ---------------------------------------------------------------------------
# Custom thresholds
# ---------------------------------------------------------------------------


class TestCustomThresholds:
    """Custom config changes escalation sensitivity."""

    def test_stricter_threshold(self):
        # Threshold 3.5 — scores of 3.0 would trigger
        scores = [_make_score(4.0)] + [_make_score(3.0) for _ in range(3)]
        cfg = QualityEscalationConfig(escalation_threshold=3.5)
        result = should_quality_escalate(scores, config=cfg)
        assert result.should_escalate is True

    def test_more_consecutive_required(self):
        # Need 5 consecutive, only 3 provided
        scores = [_make_score(4.0)] + [_make_score(2.0) for _ in range(3)]
        cfg = QualityEscalationConfig(consecutive_low_turns=5)
        result = should_quality_escalate(scores, config=cfg)
        assert result.should_escalate is False


# ---------------------------------------------------------------------------
# Recommendation data
# ---------------------------------------------------------------------------


class TestRecommendationData:
    """Recommendation includes useful context."""

    def test_recommendation_has_reason(self):
        scores = [_make_score(4.0)] + [_make_score(2.0) for _ in range(3)]
        result = should_quality_escalate(scores)
        assert result.reason
        assert "2.5" in result.reason  # threshold mentioned

    def test_recommendation_has_scores(self):
        scores = [_make_score(4.0)] + [_make_score(2.0) for _ in range(3)]
        result = should_quality_escalate(scores)
        assert len(result.recent_scores) > 0
        assert result.threshold == 2.5
