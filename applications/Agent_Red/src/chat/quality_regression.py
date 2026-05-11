# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CQ-4: Automated quality regression detection (SPEC-0183).

Monitors conversation quality scores over time and detects statistically
significant drops.  Compares a recent window of scores against a longer
baseline window and fires an alert when the recent mean drops below the
baseline mean by more than a configurable threshold.

Severity levels:
    - ``warning``: drop of 0.5-1.0 points on the 1-5 scale
    - ``critical``: drop > 1.0 point

Integrates with the default alert rules engine (SPEC-1831) for
notification delivery.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_WINDOW_SIZE = 50
DEFAULT_BASELINE_SIZE = 200
DEFAULT_THRESHOLD = 0.5  # minimum drop to trigger alert


@dataclass(frozen=True)
class QualityRegressionAlert:
    """Alert emitted when a quality regression is detected."""

    severity: str  # "warning" or "critical"
    baseline_mean: float
    recent_mean: float
    drop: float  # positive value = quality decreased
    window_size: int
    baseline_size: int
    message: str = ""

    def __post_init__(self):
        if not self.message:
            object.__setattr__(
                self,
                "message",
                f"Quality regression detected: {self.severity}. "
                f"Baseline {self.baseline_mean:.2f} -> Recent {self.recent_mean:.2f} "
                f"(drop: {self.drop:.2f} over last {self.window_size} conversations)",
            )


def detect_regression(
    scores: list[float],
    *,
    window_size: int = DEFAULT_WINDOW_SIZE,
    baseline_size: int = DEFAULT_BASELINE_SIZE,
    threshold: float = DEFAULT_THRESHOLD,
) -> QualityRegressionAlert | None:
    """Detect a quality regression in a series of conversation scores.

    Args:
        scores: Chronologically ordered list of overall quality scores (1-5).
            Most recent scores are at the end.
        window_size: Number of recent conversations to compare.
        baseline_size: Number of older conversations for the baseline.
        threshold: Minimum drop (in score points) to trigger an alert.

    Returns:
        QualityRegressionAlert if a regression is detected, else None.
    """
    min_required = window_size + 1  # need at least 1 baseline score
    if len(scores) < min_required:
        return None

    recent = scores[-window_size:]
    # Baseline is everything before the recent window, capped at baseline_size
    baseline_pool = scores[:-window_size]
    if not baseline_pool:
        return None
    baseline = baseline_pool[-baseline_size:]

    recent_mean = sum(recent) / len(recent)
    baseline_mean = sum(baseline) / len(baseline)

    drop = baseline_mean - recent_mean
    if drop < threshold:
        return None

    severity = "critical" if drop > 1.0 else "warning"

    return QualityRegressionAlert(
        severity=severity,
        baseline_mean=round(baseline_mean, 2),
        recent_mean=round(recent_mean, 2),
        drop=round(drop, 2),
        window_size=len(recent),
        baseline_size=len(baseline),
    )
