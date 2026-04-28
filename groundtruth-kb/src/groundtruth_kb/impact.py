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


def _find_dependents(db: KnowledgeDB, spec_id: str) -> list[dict[str, Any]]:
    """Find specs that depend on spec_id via affected_by linkages.

    Traversal: max depth 2 (direct + 1 transitive level).
    Cycle-safe via visited set.  Dedup at shallowest depth.
    Returns sorted by (depth, spec_id).
    """
    if not spec_id or spec_id == "<unsaved>":
        return []

    visited: set[str] = {spec_id}
    result_map: dict[str, dict[str, Any]] = {}

    # Depth 1: direct dependents
    direct = db.get_specs_affected_by(spec_id)
    for s in direct:
        sid = s["id"]
        if sid not in visited:
            visited.add(sid)
            result_map[sid] = {
                "id": sid,
                "title": s.get("title", ""),
                "depth": 1,
                "via": spec_id,
            }

    # Depth 2: transitive dependents (one more level)
    for d in list(result_map.values()):
        if d["depth"] != 1:
            continue
        transitive = db.get_specs_affected_by(d["id"])
        for s in transitive:
            sid = s["id"]
            if sid not in visited:
                visited.add(sid)
                result_map[sid] = {
                    "id": sid,
                    "title": s.get("title", ""),
                    "depth": 2,
                    "via": d["id"],
                }

    return sorted(result_map.values(), key=lambda x: (x["depth"], x["id"]))


def _get_spec_tags(spec: dict[str, Any]) -> set[str]:
    """Extract tags as a set from a spec dict (handles parsed or raw)."""
    parsed = spec.get("tags_parsed")
    if isinstance(parsed, list):
        return set(parsed)
    raw = spec.get("tags")
    if isinstance(raw, list):
        return set(raw)
    return set()


def compute_impact_analysis(
    db: KnowledgeDB,
    operation: str,
    spec_data: dict[str, Any],
    *,
    config: ImpactConfig | None = None,
) -> dict[str, Any]:
    """Compute advisory change-impact analysis for a specification.

    Args:
        db: KnowledgeDB instance.
        operation: The planned operation — "add", "modify", or "remove".
        spec_data: Spec dict (may or may not be persisted yet).  Must contain
            at least the fields used for overlap: ``section``, ``scope``,
            ``tags``/``tags_parsed``, and ``assertions``/``_assertions_parsed``.
        config: Optional thresholds (defaults to ImpactConfig()).

    Returns:
        dict with keys: spec_id, operation, blast_radius, related_spec_count,
        related_specs, dependents, applicable_constraints, potential_conflicts,
        annotations, touches_architecture, recommendation.
    """
    cfg = config or ImpactConfig()
    spec_id = spec_data.get("id", "<unsaved>")

    # --- Related specs: section OR scope OR tags overlap ---
    section = spec_data.get("section")
    scope = spec_data.get("scope")
    spec_tags = _get_spec_tags(spec_data)

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
        if spec_tags and not match:
            other_tags = _get_spec_tags(s)
            if spec_tags & other_tags:
                match = True
        if match:
            related.append(s)
            seen_ids.add(s["id"])

    related_count = len(related)
    blast_radius = _classify_blast_radius(related_count, cfg)

    # --- Applicable constraints via F4-A ---
    applicable_constraints = db.check_constraints_for_spec(
        section=section,
        scope=scope,
        tags=list(spec_tags) if spec_tags else None,
    )

    # --- Assertion-target conflict detection ---
    spec_targets = _targets_for_spec(spec_data)
    potential_conflicts, annotations = _detect_conflicts(
        spec_id,
        spec_targets,
        related,
    )

    # --- F2-B: Dependents via affected_by traversal ---
    dependents = _find_dependents(db, spec_id)

    # --- F2-B: Authority distribution ---
    authority_dist: dict[str, int] = {}
    for s in related:
        auth = s.get("authority") or "null"
        authority_dist[auth] = authority_dist.get(auth, 0) + 1

    # --- F2-B: Testability summary ---
    testability_summary: dict[str, int] = {}
    for s in related:
        tb = s.get("testability") or "null"
        testability_summary[tb] = testability_summary.get(tb, 0) + 1

    # --- Recommendation (with F2-B authority awareness) ---
    high_authority = authority_dist.get("stated", 0) + authority_dist.get("inherited", 0)
    if blast_radius == "systemic" and high_authority == 0 and related_count > 0:
        recommendation = (
            "Systemic blast radius, but all related specs have low-confidence authority. Review may be lower priority."
        )
    elif blast_radius == "systemic":
        recommendation = "High-impact change. Review all related specs before proceeding."
    elif potential_conflicts:
        recommendation = "Conflicts detected. Resolve assertion contradictions before proceeding."
    elif applicable_constraints:
        recommendation = "Architectural constraints apply. Verify compliance with ADR/DCL specs."
    else:
        recommendation = "Low-risk change. Proceed with standard review."

    return {
        "spec_id": spec_id,
        "operation": operation,
        "blast_radius": blast_radius,
        "related_spec_count": related_count,
        "related_specs": related,
        "dependents": dependents,
        "applicable_constraints": applicable_constraints,
        "potential_conflicts": potential_conflicts,
        "annotations": annotations,
        "touches_architecture": len(applicable_constraints) > 0,
        "recommendation": recommendation,
        "authority_distribution": authority_dist,
        "testability_summary": testability_summary,
    }
