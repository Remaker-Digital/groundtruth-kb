"""
GroundTruth KB — F7 Session Health Dashboard.

Threshold definitions and text rendering for session health snapshots.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import Any

# Default alert thresholds — keyed by existing lifecycle metric IDs.
DEFAULT_THRESHOLDS: dict[str, float] = {
    "M6_max": 0.25,  # defect injection rate
    "M11_max": 0.01,  # regression rate
    "M12_max": 0.15,  # spec retirement rate
    "M16_min": 0.60,  # verified with passing tests (minimum)
    "M17_max": 0.50,  # stale test ratio
    "M18_max": 0,  # implemented without tests (count)
}


def _metric_value(metric: Any) -> float | None:
    """Extract numeric value from a lifecycle metric dict."""
    if isinstance(metric, dict):
        v = metric.get("value")
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
    return None


def _check_threshold(
    metric_id: str,
    value: float | None,
    thresholds: dict[str, float],
) -> str:
    """Return PASS, WARN, or ALERT for a metric against thresholds."""
    if value is None:
        return "PASS"

    max_key = f"{metric_id}_max"
    min_key = f"{metric_id}_min"

    if max_key in thresholds and value > thresholds[max_key]:
        return "ALERT"
    if min_key in thresholds and value < thresholds[min_key]:
        return "ALERT"
    return "PASS"


def render_health_text(
    snapshot: dict[str, Any],
    thresholds: dict[str, float] | None = None,
) -> str:
    """Render a session health snapshot as a text report.

    Args:
        snapshot: Dict with lifecycle_metrics, summary, quality_distribution,
            constraint_coverage keys (from capture_session_snapshot or data_parsed).
        thresholds: Alert thresholds. Defaults to DEFAULT_THRESHOLDS.

    Returns:
        Multi-line text report with metric values and PASS/ALERT status.
    """
    t = thresholds or DEFAULT_THRESHOLDS
    metrics = snapshot.get("lifecycle_metrics", {})
    summary = snapshot.get("summary", {})
    quality = snapshot.get("quality_distribution", {})
    coverage = snapshot.get("constraint_coverage", {})

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  Session Health Report")
    lines.append("=" * 60)

    # Lifecycle metrics
    lines.append("\n  Lifecycle Metrics:")
    for mid in ("M6", "M11", "M12", "M16", "M17", "M18"):
        val = _metric_value(metrics.get(mid))
        status = _check_threshold(mid, val, t)
        val_str = f"{val:.4f}" if val is not None else "N/A"
        lines.append(f"    {mid}: {val_str}  [{status}]")

    # Summary counts
    lines.append("\n  Summary:")
    lines.append(f"    Specs: {summary.get('spec_total', 0)}")
    lines.append(f"    Tests: {summary.get('test_artifact_count', 0)}")
    lines.append(f"    Work Items: {summary.get('work_item_total', 0)}")

    # Quality distribution
    lines.append("\n  Quality Distribution:")
    for tier in ("gold", "silver", "bronze", "needs-work"):
        td = quality.get(tier, {})
        count = td.get("count", 0) if isinstance(td, dict) else 0
        lines.append(f"    {tier}: {count}")

    # Constraint coverage
    lines.append("\n  Constraint Coverage:")
    lines.append(f"    Ratio: {coverage.get('coverage_ratio', 0):.2%}")
    lines.append(f"    Constraints: {coverage.get('constraint_count', 0)}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
