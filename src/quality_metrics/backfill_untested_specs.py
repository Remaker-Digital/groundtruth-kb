"""SPEC-1841: Untested Spec Backfill Program.

Identifies implemented/verified specs with 0 linked tests, categorizes
by risk tier, and generates skeleton test records in KB.

Usage:
    python -m src.quality_metrics.backfill_untested_specs [--dry-run] [--limit N]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Risk tiers (SPEC-1841)
# ---------------------------------------------------------------------------

RISK_TIERS = {
    "critical": {
        "keywords": ["auth", "chat", "widget", "billing", "payment", "security",
                      "middleware", "customer", "otp", "magic_link"],
        "description": "Customer-facing or security-critical specs",
    },
    "high": {
        "keywords": ["api", "endpoint", "rate_limit", "cosmos", "redis",
                      "deploy", "entitlement", "tenant"],
        "description": "Infrastructure and API specs",
    },
    "medium": {
        "keywords": ["config", "admin", "superadmin", "monitor", "alert",
                      "log", "metric", "diagnostic"],
        "description": "Administrative and monitoring specs",
    },
    "low": {
        "keywords": [],
        "description": "All other specs (docs, internal tooling, etc.)",
    },
}


def classify_risk_tier(spec: dict[str, Any]) -> str:
    """Classify a spec into a risk tier based on title and description.

    Returns one of: 'critical', 'high', 'medium', 'low'.
    """
    text = (
        (spec.get("title", "") + " " + (spec.get("description", "") or ""))
        .lower()
    )

    for tier in ["critical", "high", "medium"]:
        keywords = RISK_TIERS[tier]["keywords"]
        if any(kw in text for kw in keywords):
            return tier

    return "low"


def find_untested_specs(kb: Any) -> list[dict[str, Any]]:
    """Find implemented/verified specs with 0 linked tests.

    Returns list of spec dicts with added 'risk_tier' field.
    """
    untested = kb.get_untested_specs()

    # Filter to only implemented/verified (get_untested_specs excludes retired)
    result = []
    for spec in untested:
        if spec.get("status") in ("implemented", "verified"):
            spec["risk_tier"] = classify_risk_tier(spec)
            result.append(spec)

    # Sort by risk tier priority
    tier_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    result.sort(key=lambda s: (tier_order.get(s["risk_tier"], 4), s["id"]))

    return result


def generate_skeleton_tests(
    kb: Any,
    specs: list[dict[str, Any]],
    *,
    changed_by: str = "backfill_untested_specs",
    dry_run: bool = False,
    limit: int | None = None,
) -> dict[str, int]:
    """Generate skeleton test records in KB for untested specs.

    Args:
        kb: KnowledgeDB instance.
        specs: Output of find_untested_specs().
        changed_by: Attribution for KB records.
        dry_run: If True, don't write to KB.
        limit: Max specs to process (None = all).

    Returns:
        Counts dict: {total, created, skipped, by_tier: {tier: count}}.
    """
    if limit:
        specs = specs[:limit]

    counts = {"total": len(specs), "created": 0, "skipped": 0, "by_tier": {}}

    for spec in specs:
        tier = spec.get("risk_tier", "low")
        counts["by_tier"][tier] = counts["by_tier"].get(tier, 0) + 1

        if dry_run:
            logger.info(
                "DRY RUN: Would create skeleton test for %s [%s] — %s",
                spec["id"], tier, spec.get("title", ""),
            )
            counts["created"] += 1
            continue

        # Generate a unique test ID
        next_id = _get_next_test_id(kb)

        try:
            kb.insert_test(
                id=next_id,
                title=f"Backfill: {spec.get('title', spec['id'])}",
                spec_id=spec["id"],
                test_type="logical",
                expected_outcome="pass",
                changed_by=changed_by,
                change_reason=f"SPEC-1841 backfill — untested {spec.get('status')} spec, risk tier: {tier}",
                description=f"Skeleton test for {spec['id']}. Needs implementation.",
            )
            counts["created"] += 1
        except Exception as e:
            logger.warning("Failed to create skeleton test for %s: %s", spec["id"], e)
            counts["skipped"] += 1

    return counts


def _get_next_test_id(kb: Any) -> str:
    """Get the next available TEST-NNNNN ID."""
    conn = kb._get_conn()
    row = conn.execute(
        "SELECT MAX(CAST(REPLACE(id, 'TEST-', '') AS INTEGER)) FROM tests WHERE id LIKE 'TEST-%'"
    ).fetchone()
    next_num = (row[0] or 0) + 1
    return f"TEST-{next_num}"


def get_backfill_summary(kb: Any) -> dict[str, Any]:
    """Get a summary of untested specs for reporting.

    Returns:
        Dict with counts by tier and top 5 highest-risk untested specs.
    """
    untested = find_untested_specs(kb)

    by_tier: dict[str, int] = {}
    for spec in untested:
        tier = spec.get("risk_tier", "low")
        by_tier[tier] = by_tier.get(tier, 0) + 1

    return {
        "total_untested": len(untested),
        "by_tier": by_tier,
        "top_5_critical": [
            {"id": s["id"], "title": s.get("title", ""), "tier": s.get("risk_tier")}
            for s in untested[:5]
        ],
    }
