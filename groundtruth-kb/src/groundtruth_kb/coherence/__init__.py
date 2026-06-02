"""Deterministic spec-coherence checks for GroundTruth KB."""

from __future__ import annotations

from groundtruth_kb.coherence.checker import (
    CoherenceResult,
    CoherenceRuleError,
    Finding,
    PolarityPair,
    Rule,
    check_authority_hierarchy,
    check_status_drift,
    check_surface_overlap,
    emit_json,
    emit_markdown,
    load_rules,
    load_specs_from_db,
    make_result,
    run_all,
)

__all__ = [
    "CoherenceResult",
    "CoherenceRuleError",
    "Finding",
    "PolarityPair",
    "Rule",
    "check_authority_hierarchy",
    "check_status_drift",
    "check_surface_overlap",
    "emit_json",
    "emit_markdown",
    "load_rules",
    "load_specs_from_db",
    "make_result",
    "run_all",
]
