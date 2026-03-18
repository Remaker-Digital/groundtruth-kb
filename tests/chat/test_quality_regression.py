"""CQ-4: Quality regression detection tests (SPEC-0183).

Tests for detect_regression() and QualityRegressionAlert.
8 tests covering: stable scores, threshold detection, configurable params,
severity levels, edge cases, and alert data.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from src.chat.quality_regression import (
    DEFAULT_BASELINE_SIZE,
    DEFAULT_THRESHOLD,
    DEFAULT_WINDOW_SIZE,
    QualityRegressionAlert,
    detect_regression,
)


# ---------------------------------------------------------------------------
# TEST-10545: detect_regression returns None when scores are stable
# ---------------------------------------------------------------------------


class TestStableScores:
    """TEST-10545: No alert when quality is stable."""

    def test_stable_scores_no_alert(self):
        scores = [4.0] * 300
        result = detect_regression(scores)
        assert result is None

    def test_slight_variation_no_alert(self):
        scores = [4.0] * 200 + [3.8] * 50
        result = detect_regression(scores)
        assert result is None  # drop of 0.2 < threshold 0.5


# ---------------------------------------------------------------------------
# TEST-10546: detect_regression fires alert on quality drop
# ---------------------------------------------------------------------------


class TestFiresAlert:
    """TEST-10546: Alert fires when recent window drops below threshold."""

    def test_regression_detected(self):
        # Baseline: 4.0, Recent: 3.0 → drop of 1.0
        scores = [4.0] * 200 + [3.0] * 50
        result = detect_regression(scores)
        assert result is not None
        assert isinstance(result, QualityRegressionAlert)
        assert result.drop >= DEFAULT_THRESHOLD

    def test_regression_exact_threshold(self):
        # Baseline: 4.0, Recent: 3.5 → drop of exactly 0.5
        scores = [4.0] * 200 + [3.5] * 50
        result = detect_regression(scores)
        assert result is not None
        assert result.drop >= 0.5


# ---------------------------------------------------------------------------
# TEST-10547: insufficient data
# ---------------------------------------------------------------------------


class TestInsufficientData:
    """TEST-10547: Returns None when not enough data for comparison."""

    def test_too_few_scores(self):
        result = detect_regression([4.0, 3.0, 2.0])
        assert result is None

    def test_empty_scores(self):
        result = detect_regression([])
        assert result is None

    def test_exactly_window_size(self):
        # window_size scores but no baseline → None
        scores = [4.0] * DEFAULT_WINDOW_SIZE
        result = detect_regression(scores)
        assert result is None


# ---------------------------------------------------------------------------
# TEST-10548: threshold is configurable
# ---------------------------------------------------------------------------


class TestConfigurableThreshold:
    """TEST-10548: threshold parameter controls sensitivity."""

    def test_custom_threshold_fires(self):
        scores = [4.0] * 200 + [3.8] * 50
        # Default threshold 0.5 would not fire (drop=0.2)
        result = detect_regression(scores, threshold=0.1)
        assert result is not None

    def test_custom_threshold_blocks(self):
        scores = [4.0] * 200 + [3.0] * 50
        # High threshold blocks the alert
        result = detect_regression(scores, threshold=2.0)
        assert result is None


# ---------------------------------------------------------------------------
# TEST-10549: window_size controls comparison window
# ---------------------------------------------------------------------------


class TestWindowSize:
    """TEST-10549: window_size parameter changes comparison scope."""

    def test_small_window(self):
        # Only last 10 conversations dropped
        scores = [4.0] * 200 + [2.0] * 10
        result = detect_regression(scores, window_size=10)
        assert result is not None
        assert result.window_size == 10

    def test_large_window_dilutes_drop(self):
        # Last 10 dropped but window is 100 → includes good scores
        scores = [4.0] * 200 + [4.0] * 90 + [2.0] * 10
        result = detect_regression(scores, window_size=100)
        # Drop is diluted: (90*4 + 10*2)/100 = 3.8, baseline ~4.0 → drop 0.2
        assert result is None


# ---------------------------------------------------------------------------
# TEST-10550: severity based on drop magnitude
# ---------------------------------------------------------------------------


class TestSeverity:
    """TEST-10550: alert severity is warning (0.5-1.0) or critical (>1.0)."""

    def test_warning_severity(self):
        scores = [4.0] * 200 + [3.2] * 50  # drop ~0.8
        result = detect_regression(scores)
        assert result is not None
        assert result.severity == "warning"

    def test_critical_severity(self):
        scores = [4.0] * 200 + [2.0] * 50  # drop ~2.0
        result = detect_regression(scores)
        assert result is not None
        assert result.severity == "critical"


# ---------------------------------------------------------------------------
# TEST-10551: alert includes baseline and recent statistics
# ---------------------------------------------------------------------------


class TestAlertStats:
    """TEST-10551: alert data includes means, sizes, drop magnitude."""

    def test_alert_contains_stats(self):
        scores = [4.0] * 200 + [2.5] * 50
        result = detect_regression(scores)
        assert result is not None
        assert result.baseline_mean == 4.0
        assert result.recent_mean == 2.5
        assert result.drop == 1.5
        assert result.baseline_size <= DEFAULT_BASELINE_SIZE
        assert result.window_size == DEFAULT_WINDOW_SIZE

    def test_alert_message_populated(self):
        scores = [4.0] * 200 + [2.5] * 50
        result = detect_regression(scores)
        assert result is not None
        assert "regression" in result.message.lower()
        assert "critical" in result.message.lower()


# ---------------------------------------------------------------------------
# TEST-10552: single-score edge case
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """TEST-10552: edge cases do not crash."""

    def test_single_score(self):
        result = detect_regression([3.0])
        assert result is None

    def test_minimum_viable_regression(self):
        # window_size + 1 scores minimum
        scores = [5.0] + [1.0] * DEFAULT_WINDOW_SIZE
        result = detect_regression(scores, window_size=DEFAULT_WINDOW_SIZE)
        assert result is not None
        assert result.baseline_mean == 5.0
        assert result.recent_mean == 1.0
