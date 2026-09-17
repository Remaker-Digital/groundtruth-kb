"""Pure specification quality scoring shared by the legacy store and native writers."""

from __future__ import annotations

from typing import Any

# Executable assertion types per assertions.py
_EXECUTABLE = frozenset({"grep", "glob", "grep_absent", "file_exists", "count", "json_path", "all_of", "any_of"})


def score_spec_quality(spec: dict[str, Any]) -> dict[str, Any]:
    """Compute the quality score for one specification record.

    Returns overall, d1-d5 dimension scores, tier and flags. F1 fields that are
    absent adjust the completeness denominator instead of failing the score.
    Native records carry ``assertions`` directly; legacy rows carry the parsed
    forms, so both spellings are read.
    """
    flags: list[str] = []
    assertions = spec.get("assertions_parsed") or spec.get("_assertions_parsed") or spec.get("assertions") or []
    if not isinstance(assertions, list):
        assertions = []

    has_assertions = bool(assertions)
    has_executable = (
        any(isinstance(a, dict) and a.get("type") in _EXECUTABLE for a in assertions) if has_assertions else False
    )

    if not has_assertions:
        flags.append("NO_ASSERTIONS")
    elif not has_executable:
        flags.append("NO_EXECUTABLE_ASSERTIONS")

    # D1: Clarity
    d1 = 0.0
    title = spec.get("title", "")
    if title and 40 <= len(title) <= 120:
        d1 += 0.2
    if title and any(w in title.lower() for w in ("must", "shall", "should", "requires")):
        d1 += 0.3
    if spec.get("description") and len(spec.get("description", "")) > 50:
        d1 += 0.3
    if spec.get("description") and any(
        w in spec["description"].lower() for w in ("because", "rationale", "reason", "ensures")
    ):
        d1 += 0.2

    # D2: Testability
    d2 = 0.0
    if has_assertions:
        d2 += 0.3
    if has_executable:
        d2 += 0.4
    if has_assertions and any(isinstance(a, dict) and a.get("description") for a in assertions):
        d2 += 0.15
    if has_assertions and any(isinstance(a, dict) and a.get("file") for a in assertions):
        d2 += 0.15
    # F1 bonus: testability field
    if spec.get("testability"):
        d2 = min(1.0, d2 + 0.1)

    # D3: Completeness (dynamic denominator)
    d3_checks = 0
    d3_hits = 0
    for field in ("type", "tags", "section", "scope", "priority", "description"):
        d3_checks += 1
        if spec.get(field):
            d3_hits += 1
    # F1 fields: only count if present in spec dict (graceful degradation)
    for f1_field in ("authority", "constraints", "affected_by"):
        if f1_field in spec:
            d3_checks += 1
            val = spec.get(f1_field)
            if val is not None and val != "" and val != "[]" and val != "{}":
                d3_hits += 1
    d3 = d3_hits / max(d3_checks, 1)

    # D4: Isolation
    d4 = 0.0
    if spec.get("section"):
        d4 += 0.4
    if spec.get("handle"):
        d4 += 0.3
    if spec.get("affected_by_parsed") or spec.get("_affected_by_parsed"):
        d4 += 0.3

    # D5: Freshness (simplified — based on version existence)
    d5 = 0.5  # Base freshness
    if has_assertions:
        d5 += 0.3
    if spec.get("version", 0) > 1:
        d5 += 0.2
    d5 = min(1.0, d5)

    overall = (d1 + d2 + d3 + d4 + d5) / 5.0

    # Tier classification
    if overall >= 0.8:
        tier = "gold"
    elif overall >= 0.6:
        tier = "silver"
    elif overall >= 0.4:
        tier = "bronze"
    else:
        tier = "needs-work"

    return {
        "overall": round(overall, 4),
        "d1_clarity": round(d1, 4),
        "d2_testability": round(d2, 4),
        "d3_completeness": round(d3, 4),
        "d4_isolation": round(d4, 4),
        "d5_freshness": round(d5, 4),
        "tier": tier,
        "flags": flags,
    }
