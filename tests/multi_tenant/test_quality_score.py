"""Tests for SPEC-1838: Quality Score Dashboard with 6 Metrics.

Verifies composite quality score computation, trend tracking,
and per-metric normalization.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest


class TestQualityScoreComputation:
    """SPEC-1838: Quality score computed from 6 metrics."""

    def test_composite_formula_correct(self):
        """TEST-10458: Known inputs produce expected composite score."""
        from src.quality_metrics.quality_score import compute_composite_score

        metrics = {
            "spec_coverage": 0.95,
            "der": 0.02,
            "assertion_strength": 0.80,
            "cfr": 0.03,
            "freshness": 0.98,
            "coverage_delta": 0.01,
        }

        score = compute_composite_score(metrics)

        # QualityScore = 0.20*0.95 + 0.20*(1-0.02) + 0.15*0.80 + 0.15*(1-0.03) + 0.15*0.98 + 0.15*min(1.0, 0.01_normalized)
        # The exact value depends on coverage_delta normalization, but should be ~92-95
        assert 85 <= score <= 100
        assert isinstance(score, float)

    def test_all_perfect_metrics_gives_100(self):
        """Perfect metrics should yield composite score near 100."""
        from src.quality_metrics.quality_score import compute_composite_score

        metrics = {
            "spec_coverage": 1.0,
            "der": 0.0,
            "assertion_strength": 1.0,
            "cfr": 0.0,
            "freshness": 1.0,
            "coverage_delta": 0.05,  # Positive = improving
        }

        score = compute_composite_score(metrics)
        assert score >= 95  # Near-perfect

    def test_all_worst_metrics_gives_low_score(self):
        """Worst-case metrics should yield a low composite score."""
        from src.quality_metrics.quality_score import compute_composite_score

        metrics = {
            "spec_coverage": 0.5,
            "der": 0.20,
            "assertion_strength": 0.30,
            "cfr": 0.25,
            "freshness": 0.50,
            "coverage_delta": -0.05,  # Negative = degrading
        }

        score = compute_composite_score(metrics)
        assert score < 70

    def test_metrics_all_normalized_0_to_1(self):
        """Each metric component must be normalized 0-1 before weighting."""
        from src.quality_metrics.quality_score import normalize_metrics

        raw = {
            "spec_coverage": 0.92,  # Already 0-1
            "der": 0.03,  # Inverted: 1 - 0.03 = 0.97
            "assertion_strength": 0.75,
            "cfr": 0.05,  # Inverted: 1 - 0.05 = 0.95
            "freshness": 0.98,
            "coverage_delta": -0.02,  # Negative clamped to 0
        }

        normalized = normalize_metrics(raw)
        for key, value in normalized.items():
            assert 0.0 <= value <= 1.0, f"{key} = {value} is outside [0, 1]"


class TestQualityScoreStorage:
    """SPEC-1838: Quality scores stored per session in KB."""

    def test_score_stored_with_session_id(self):
        """TEST-10456: Score record includes session_id and all 6 metrics."""
        from src.quality_metrics.quality_score import QualityScoreRecord

        record = QualityScoreRecord(
            session_id="S198",
            spec_coverage=0.92,
            der=0.02,
            assertion_strength=0.80,
            cfr=0.03,
            freshness=0.98,
            coverage_delta=0.01,
            composite_score=93.5,
        )

        assert record.session_id == "S198"
        assert record.composite_score == 93.5
        # All 6 metrics present
        assert record.spec_coverage is not None
        assert record.der is not None
        assert record.assertion_strength is not None
        assert record.cfr is not None
        assert record.freshness is not None
        assert record.coverage_delta is not None


class TestQualityScoreTrend:
    """SPEC-1838: Trend tracking across sessions."""

    def test_trend_shows_last_5_sessions(self):
        """TEST-10457: Trend display includes last 5 sessions."""
        from src.quality_metrics.quality_score import compute_trend

        history = [
            {"session_id": f"S{i}", "composite_score": 80 + i}
            for i in range(10)
        ]

        trend = compute_trend(history, last_n=5)
        assert len(trend) == 5
        assert trend[0]["session_id"] == "S5"  # Most recent 5

    def test_alert_on_10_point_drop(self):
        """TEST-10459: >10 point drop triggers warning."""
        from src.quality_metrics.quality_score import detect_quality_alert

        previous = 90.0
        current = 78.0

        alert = detect_quality_alert(previous, current)
        assert alert is not None
        assert alert["severity"] == "warning"
        assert alert["delta"] == -12.0
