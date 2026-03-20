"""SPEC-1838: Quality Score Dashboard — compute 6 metrics and composite score.

Computes quality metrics from the Knowledge Database:
  1. Spec Coverage Rate       (specs with >=1 test / total non-retired)
  2. Defect Escape Rate (DER) (escaped defects / total defects)
  3. Assertion Strength        (specs with machine assertions / implemented)
  4. Change Failure Rate (CFR) (rollbacks / deployments)
  5. Test Freshness           (recently executed tests / total)
  6. Coverage Delta           (line coverage change since last session)

Composite: weighted sum → 0-100 scale.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Metric weights (SPEC-1838)
# ---------------------------------------------------------------------------

WEIGHTS = {
    "spec_coverage": 0.20,
    "defect_escape_rate": 0.20,  # Weight applied to (1 - DER)
    "assertion_strength": 0.15,
    "change_failure_rate": 0.15,  # Weight applied to (1 - CFR)
    "test_freshness": 0.15,
    "coverage_delta": 0.15,
}


def compute_spec_coverage(kb: Any) -> float:
    """Spec Coverage Rate: (specs with >=1 test) / (total non-retired specs).

    Returns 0.0-1.0.
    """
    conn = kb._get_conn()

    total = conn.execute(
        "SELECT COUNT(*) FROM current_specifications WHERE status != 'retired'"
    ).fetchone()[0]

    if total == 0:
        return 1.0

    tested = conn.execute(
        """SELECT COUNT(DISTINCT s.id)
           FROM current_specifications s
           INNER JOIN current_tests t ON t.spec_id = s.id
           WHERE s.status != 'retired' AND t.last_result != 'stale'"""
    ).fetchone()[0]

    return round(tested / total, 4)


def compute_defect_escape_rate(kb: Any) -> float:
    """Defect Escape Rate: escaped / (internal + escaped).

    Escaped = WI with origin='defect' created after most recent deployment.
    Internal = WI with origin='defect' created before deployment.
    Returns 0.0-1.0 (lower is better).
    """
    conn = kb._get_conn()

    # Count all defect WIs
    total_defects = conn.execute(
        "SELECT COUNT(*) FROM current_work_items WHERE origin = 'defect'"
    ).fetchone()[0]

    if total_defects == 0:
        return 0.0  # No defects = perfect

    # Approximate: WIs resolved are internal, open are escaped
    escaped = conn.execute(
        """SELECT COUNT(*) FROM current_work_items
           WHERE origin = 'defect' AND resolution_status = 'open'"""
    ).fetchone()[0]

    return round(escaped / total_defects, 4)


def compute_assertion_strength(kb: Any) -> float:
    """Assertion Strength: (specs with machine-verifiable assertions) / (implemented specs).

    Machine-verifiable = assertions field is non-empty JSON array.
    Returns 0.0-1.0.
    """
    conn = kb._get_conn()

    implemented = conn.execute(
        "SELECT COUNT(*) FROM current_specifications WHERE status IN ('implemented', 'verified')"
    ).fetchone()[0]

    if implemented == 0:
        return 1.0

    with_assertions = conn.execute(
        """SELECT COUNT(*) FROM current_specifications
           WHERE status IN ('implemented', 'verified')
           AND assertions IS NOT NULL AND assertions != '' AND assertions != '[]'"""
    ).fetchone()[0]

    return round(with_assertions / implemented, 4)


def compute_change_failure_rate(kb: Any) -> float:
    """Change Failure Rate: rollbacks / total deployments.

    Approximated from WI origin='regression' ratio.
    Returns 0.0-1.0 (lower is better).
    """
    conn = kb._get_conn()

    total_wis = conn.execute(
        "SELECT COUNT(*) FROM current_work_items"
    ).fetchone()[0]

    if total_wis == 0:
        return 0.0

    regressions = conn.execute(
        "SELECT COUNT(*) FROM current_work_items WHERE origin = 'regression'"
    ).fetchone()[0]

    return round(regressions / total_wis, 4)


def compute_test_freshness(kb: Any, days: int = 30) -> float:
    """Test Freshness: (tests with results) / (total non-stale tests).

    Returns 0.0-1.0.
    """
    conn = kb._get_conn()

    total = conn.execute(
        "SELECT COUNT(*) FROM current_tests WHERE last_result != 'stale'"
    ).fetchone()[0]

    if total == 0:
        return 1.0

    with_result = conn.execute(
        """SELECT COUNT(*) FROM current_tests
           WHERE last_result IN ('pass', 'fail') AND last_result != 'stale'"""
    ).fetchone()[0]

    return round(with_result / total, 4)


def compute_coverage_delta(previous_coverage: float, current_coverage: float) -> float:
    """Coverage Delta: current - previous line coverage.

    Returns raw delta (can be negative). Normalized to 0-1 for composite.
    """
    return round(current_coverage - previous_coverage, 2)


def normalize_coverage_delta(delta: float) -> float:
    """Normalize coverage delta to 0-1 range for composite score.

    +5% or more → 1.0, 0% → 0.5, -5% or worse → 0.0.
    """
    # Map [-5, +5] to [0, 1] with 0 → 0.5
    normalized = (delta + 5.0) / 10.0
    return round(max(0.0, min(1.0, normalized)), 4)


def compute_composite_score(
    spec_coverage: float,
    defect_escape_rate: float,
    assertion_strength: float,
    change_failure_rate: float,
    test_freshness: float,
    coverage_delta: float,
) -> float:
    """Compute the weighted composite quality score (0-100).

    SPEC-1838 formula:
    QS = 0.20*SpecCov + 0.20*(1-DER) + 0.15*AssertStr +
         0.15*(1-CFR) + 0.15*Freshness + 0.15*CovDelta_norm
    """
    cov_norm = normalize_coverage_delta(coverage_delta)

    raw = (
        WEIGHTS["spec_coverage"] * spec_coverage
        + WEIGHTS["defect_escape_rate"] * (1.0 - defect_escape_rate)
        + WEIGHTS["assertion_strength"] * assertion_strength
        + WEIGHTS["change_failure_rate"] * (1.0 - change_failure_rate)
        + WEIGHTS["test_freshness"] * test_freshness
        + WEIGHTS["coverage_delta"] * cov_norm
    )

    return round(raw * 100, 1)


from dataclasses import dataclass


@dataclass
class QualityScoreRecord:
    """A stored quality score snapshot for a session."""

    session_id: str
    spec_coverage: float
    der: float
    assertion_strength: float
    cfr: float
    freshness: float
    coverage_delta: float
    composite_score: float


def normalize_metrics(raw: dict[str, float]) -> dict[str, float]:
    """Normalize raw metrics to 0-1 range.

    - spec_coverage, assertion_strength, freshness: already 0-1
    - der, cfr: inverted (1 - value)
    - coverage_delta: normalized via normalize_coverage_delta
    """
    return {
        "spec_coverage": max(0.0, min(1.0, raw.get("spec_coverage", 0.0))),
        "defect_escape_rate": max(0.0, min(1.0, 1.0 - raw.get("der", 0.0))),
        "assertion_strength": max(0.0, min(1.0, raw.get("assertion_strength", 0.0))),
        "change_failure_rate": max(0.0, min(1.0, 1.0 - raw.get("cfr", 0.0))),
        "test_freshness": max(0.0, min(1.0, raw.get("freshness", 0.0))),
        "coverage_delta": normalize_coverage_delta(raw.get("coverage_delta", 0.0)),
    }


def compute_trend(
    history: list[dict[str, Any]], last_n: int = 5
) -> list[dict[str, Any]]:
    """Return the last N quality score records from history.

    Args:
        history: List of score dicts with session_id and composite_score.
        last_n: Number of recent sessions to include.

    Returns:
        The last N entries from history.
    """
    return history[-last_n:] if len(history) >= last_n else history


def detect_quality_alert(
    previous: float, current: float, threshold: float = 10.0
) -> dict[str, Any] | None:
    """Detect a quality score drop exceeding threshold.

    Args:
        previous: Previous session's composite score.
        current: Current session's composite score.
        threshold: Point drop that triggers an alert.

    Returns:
        Alert dict with severity and delta, or None if no alert.
    """
    delta = current - previous
    if delta < -threshold:
        return {
            "severity": "warning",
            "delta": delta,
            "previous": previous,
            "current": current,
            "message": f"Quality score dropped by {abs(delta):.1f} points",
        }
    return None


def compute_all_metrics(
    kb: Any,
    previous_coverage: float = 0.0,
    current_coverage: float = 0.0,
) -> dict[str, Any]:
    """Compute all 6 quality metrics and the composite score.

    Args:
        kb: KnowledgeDB instance.
        previous_coverage: Previous session's global line coverage %.
        current_coverage: Current session's global line coverage %.

    Returns:
        Dict with all 6 metrics + composite_score + details.
    """
    spec_cov = compute_spec_coverage(kb)
    der = compute_defect_escape_rate(kb)
    assertion = compute_assertion_strength(kb)
    cfr = compute_change_failure_rate(kb)
    freshness = compute_test_freshness(kb)
    cov_delta = compute_coverage_delta(previous_coverage, current_coverage)

    composite = compute_composite_score(
        spec_cov, der, assertion, cfr, freshness, cov_delta,
    )

    return {
        "spec_coverage": spec_cov,
        "defect_escape_rate": der,
        "assertion_strength": assertion,
        "change_failure_rate": cfr,
        "test_freshness": freshness,
        "coverage_delta": cov_delta,
        "composite_score": composite,
        "details": {
            "weights": WEIGHTS,
            "coverage_delta_normalized": normalize_coverage_delta(cov_delta),
            "previous_line_coverage": previous_coverage,
            "current_line_coverage": current_coverage,
        },
    }


def trend_arrow(current: float, previous: float, higher_is_better: bool = True) -> str:
    """Return a trend arrow comparing current vs previous metric.

    Args:
        current: Current metric value.
        previous: Previous metric value.
        higher_is_better: True if higher values are better (e.g., coverage).
                         False for metrics like DER, CFR where lower is better.

    Returns:
        One of: "^" (improving), "v" (degrading), "=" (flat).
    """
    delta = current - previous
    threshold = 0.005  # 0.5% change threshold

    if abs(delta) < threshold:
        return "="
    if higher_is_better:
        return "^" if delta > 0 else "v"
    else:
        return "^" if delta < 0 else "v"  # Lower is better, so decrease = improving
