"""
GroundTruth KB — F2 Change Impact Analysis (Phase A).

Advisory impact analysis for specification changes.  Phase A uses section/scope/tags
overlap for related-spec discovery, F4-A constraint lookup, and assertion-target
conflict detection with exact-string file comparison.

Phase A limitations (documented):
  - Conflict comparison is exact-string on file_target.  A literal path
    (``src/api.py``) will NOT conflict with a glob (``src/**/*.py``) that
    covers it.  This is the literal-vs-glob false-negative class.
  - ``dependents`` is always empty (Phase B adds ``affected_by_parsed`` lookup).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from groundtruth_kb.assertions import AssertionTarget, _extract_assertion_targets

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB


@dataclass
class ImpactConfig:
    """Tunable thresholds for blast-radius classification."""

    contained_threshold: int = 5
    systemic_threshold: int = 20


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------


def _targets_for_spec(spec: dict[str, Any]) -> list[AssertionTarget]:
    """Extract all assertion targets from a spec's parsed assertions."""
    assertions = spec.get("_assertions_parsed") or []
    targets: list[AssertionTarget] = []
    for a in assertions:
        targets.extend(_extract_assertion_targets(a))
    return targets


def _detect_conflicts(
    spec_id: str,
    spec_targets: list[AssertionTarget],
    related_specs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Detect assertion-target conflicts between a spec and related specs.

    Returns (conflicts, annotations).

    Conflict rule: two targets conflict when they share the same file_target
    (exact string) and the same match_target (exact string) but have different
    assertion_types.

    The literal-vs-glob false-negative applies only when file_target strings
    differ and at least one side is a glob.  When both targets have the same
    file_target string (exact match), they are always compared regardless of
    glob status.
    """
    conflicts: list[dict[str, Any]] = []
    annotations: list[str] = []
    seen_glob_notes: set[str] = set()

    for st in spec_targets:
        if not st.file_target:
            continue
        for rel in related_specs:
            rel_id = rel["id"]
            if rel_id == spec_id:
                continue
            rel_targets = _targets_for_spec(rel)
            for rt in rel_targets:
                if not rt.file_target:
                    continue

                # Exact-string file_target comparison first — always honored
                if st.file_target == rt.file_target:
                    if (
                        st.match_target
                        and rt.match_target
                        and st.match_target == rt.match_target
                        and st.assertion_type != rt.assertion_type
                    ):
                        conflicts.append(
                            {
                                "type": "assertion_conflict",
                                "spec_a": spec_id,
                                "spec_a_assertion_type": st.assertion_type,
                                "spec_b": rel_id,
                                "spec_b_assertion_type": rt.assertion_type,
                                "file_target": st.file_target,
                                "match_target": st.match_target,
                            }
                        )
                elif st.file_is_glob or rt.file_is_glob:
                    # Different file targets, at least one is a glob —
                    # document the literal-vs-glob false-negative
                    note_key = f"{st.file_target}|{rt.file_target}"
                    if note_key not in seen_glob_notes:
                        seen_glob_notes.add(note_key)
                        annotations.append(
                            f"file-glob limitation: cannot compare "
                            f"{st.file_target!r} with {rt.file_target!r} "
                            f"(one or both are globs)"
                        )

    return conflicts, annotations


# ---------------------------------------------------------------------------
# Blast-radius classification
# ---------------------------------------------------------------------------


def _classify_blast_radius(related_count: int, config: ImpactConfig) -> str:
    """Classify blast radius from related-spec count."""
    if related_count >= config.systemic_threshold:
        return "systemic"
    if related_count >= config.contained_threshold:
        return "moderate"
    return "contained"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_impact_analysis(
    db: KnowledgeDB,
    spec_id: str,
    *,
    config: ImpactConfig | None = None,
) -> dict[str, Any]:
    """Compute advisory change-impact analysis for a specification.

    Args:
        db: KnowledgeDB instance.
        spec_id: ID of the spec to analyze.
        config: Optional thresholds (defaults to ImpactConfig()).

    Returns:
        dict with keys: spec_id, blast_radius, related_spec_count,
        applicable_constraints, potential_conflicts, annotations,
        touches_architecture.
    """
    cfg = config or ImpactConfig()

    spec = db.get_spec(spec_id)
    if spec is None:
        return {"error": f"Spec {spec_id} not found"}

    # --- Related specs: section OR scope overlap ---
    section = spec.get("section")
    scope = spec.get("scope")
    seen_ids: set[str] = set()
    related: list[dict[str, Any]] = []
    for s in db.list_specs():
        if s["id"] == spec_id or s["id"] in seen_ids:
            continue
        match = False
        if section and s.get("section") and s["section"] == section:
            match = True
        if scope and s.get("scope") and s["scope"] == scope:
            match = True
        if match:
            related.append(s)
            seen_ids.add(s["id"])

    related_count = len(related)
    blast_radius = _classify_blast_radius(related_count, cfg)

    # --- Applicable constraints via F4-A ---
    applicable_constraints = db.check_constraints_for_spec(spec_id)

    # --- Assertion-target conflict detection ---
    spec_targets = _targets_for_spec(spec)
    potential_conflicts, annotations = _detect_conflicts(
        spec_id,
        spec_targets,
        related,
    )

    # --- Recommendation ---
    if blast_radius == "systemic":
        recommendation = "High-impact change. Review all related specs before proceeding."
    elif potential_conflicts:
        recommendation = "Conflicts detected. Resolve assertion contradictions before proceeding."
    elif applicable_constraints:
        recommendation = "Architectural constraints apply. Verify compliance with ADR/DCL specs."
    else:
        recommendation = "Low-risk change. Proceed with standard review."

    return {
        "spec_id": spec_id,
        "blast_radius": blast_radius,
        "related_spec_count": related_count,
        "related_specs": related,
        "dependents": [],  # Phase A — Phase B adds affected_by_parsed lookup
        "applicable_constraints": applicable_constraints,
        "potential_conflicts": potential_conflicts,
        "annotations": annotations,
        "touches_architecture": len(applicable_constraints) > 0,
        "recommendation": recommendation,
    }
