"""Tests for SPEC-1838: Quality Score Dashboard.

Verifies 6 metrics, composite score computation, trend arrows,
and KB storage via quality_scores table.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import MagicMock


from src.quality_metrics.quality_score import (
    WEIGHTS,
    compute_all_metrics,
    compute_composite_score,
    compute_coverage_delta,
    normalize_coverage_delta,
    trend_arrow,
)


class TestWeights:
    """SPEC-1838: Weights sum to 1.0."""

    def test_weights_sum_to_one(self):
        assert abs(sum(WEIGHTS.values()) - 1.0) < 0.001

    def test_six_metric_weights(self):
        assert len(WEIGHTS) == 6


class TestCompositeScore:
    """SPEC-1838: Composite score formula."""

    def test_perfect_score(self):
        """All metrics at best values → ~100."""
        score = compute_composite_score(
            spec_coverage=1.0,
            defect_escape_rate=0.0,
            assertion_strength=1.0,
            change_failure_rate=0.0,
            test_freshness=1.0,
            coverage_delta=5.0,  # +5% → normalizes to 1.0
        )
        assert score == 100.0

    def test_worst_score(self):
        """All metrics at worst → ~0."""
        score = compute_composite_score(
            spec_coverage=0.0,
            defect_escape_rate=1.0,
            assertion_strength=0.0,
            change_failure_rate=1.0,
            test_freshness=0.0,
            coverage_delta=-5.0,
        )
        assert score == 0.0

    def test_middle_score(self):
        """50/50 metrics → roughly 50."""
        score = compute_composite_score(
            spec_coverage=0.5,
            defect_escape_rate=0.5,
            assertion_strength=0.5,
            change_failure_rate=0.5,
            test_freshness=0.5,
            coverage_delta=0.0,  # Neutral → 0.5 normalized
        )
        assert 45 <= score <= 55

    def test_score_range_0_to_100(self):
        """Score always in [0, 100]."""
        score = compute_composite_score(0.8, 0.1, 0.7, 0.05, 0.9, 2.0)
        assert 0 <= score <= 100


class TestNormalizeCoverageDelta:
    """Coverage delta normalization to 0-1."""

    def test_positive_5_maps_to_1(self):
        assert normalize_coverage_delta(5.0) == 1.0

    def test_negative_5_maps_to_0(self):
        assert normalize_coverage_delta(-5.0) == 0.0

    def test_zero_maps_to_half(self):
        assert normalize_coverage_delta(0.0) == 0.5

    def test_clamps_above(self):
        assert normalize_coverage_delta(10.0) == 1.0

    def test_clamps_below(self):
        assert normalize_coverage_delta(-10.0) == 0.0


class TestTrendArrow:
    """Trend direction indicators."""

    def test_improving_higher_is_better(self):
        assert trend_arrow(0.9, 0.8, higher_is_better=True) == "^"

    def test_degrading_higher_is_better(self):
        assert trend_arrow(0.7, 0.8, higher_is_better=True) == "v"

    def test_flat(self):
        assert trend_arrow(0.8, 0.8, higher_is_better=True) == "="

    def test_improving_lower_is_better(self):
        """DER/CFR: lower is better, so decrease = ^."""
        assert trend_arrow(0.02, 0.05, higher_is_better=False) == "^"

    def test_degrading_lower_is_better(self):
        assert trend_arrow(0.08, 0.03, higher_is_better=False) == "v"


class TestCoverageDelta:
    """Raw coverage delta computation."""

    def test_positive_delta(self):
        assert compute_coverage_delta(73.0, 75.0) == 2.0

    def test_negative_delta(self):
        assert compute_coverage_delta(75.0, 73.0) == -2.0

    def test_zero_delta(self):
        assert compute_coverage_delta(73.0, 73.0) == 0.0


class TestComputeAllMetrics:
    """Integration: compute_all_metrics returns complete structure."""

    def test_returns_all_keys(self):
        """Result has all 6 metrics + composite + details."""
        mock_kb = MagicMock()
        conn = MagicMock()
        mock_kb._get_conn.return_value = conn

        # Mock all queries to return reasonable values
        conn.execute.return_value.fetchone.return_value = [100]

        result = compute_all_metrics(mock_kb, 73.0, 75.0)

        assert "spec_coverage" in result
        assert "defect_escape_rate" in result
        assert "assertion_strength" in result
        assert "change_failure_rate" in result
        assert "test_freshness" in result
        assert "coverage_delta" in result
        assert "composite_score" in result
        assert "details" in result
        assert result["coverage_delta"] == 2.0
