"""Slice 1 regression tests for SPEC-ADVISORY-DASHBOARD-COUNTERS-001.

Trace: ``bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`` (REVISED-1)
IP-3 T1-T6 regression coverage; Codex GO at ``-004``.

The SPEC records six distinct counter metrics for dashboard/startup
bridge-state surfaces with explicit ADVISORY-and-VERIFIED-aware boundaries:

- ``advisory_count`` -- ADVISORY entries (distinct from no_go_count)
- ``no_go_count`` -- NO-GO entries, MUST NOT include ADVISORY
- ``actionable_count_for_prime`` -- GO + NO-GO only, MUST NOT include latest
  VERIFIED or latest ADVISORY (Prime continuation queue)
- ``actionable_count_for_lo`` -- NEW + REVISED, MUST NOT include ADVISORY
- ``advisory_disposition_count`` -- ADVISORY entries (Prime's disposition
  surface, distinct from actionable_count_for_prime)
- ``failed_proposal_count`` -- NO-GO entries on Prime-authored proposals only

Tests:

- T1 (structural)                     -- ``test_spec_row_structure``
- T2 (enumeration)                    -- ``test_description_enumerates_six_metrics``
- T3 (F1+F3 closure)                  -- ``test_no_go_count_excludes_advisory``
- T4 (F1+F3 closure)                  -- ``test_actionable_count_for_prime_excludes_verified``
- T5 (F1+F3 closure)                  -- ``test_advisory_disposition_count_separate``
- T6 (display distinction)            -- ``test_description_documents_display_distinction``
"""

from __future__ import annotations

import pytest
from groundtruth_kb import KnowledgeDB

SPEC_ID = "SPEC-ADVISORY-DASHBOARD-COUNTERS-001"


@pytest.fixture(scope="module")
def spec_row() -> dict:
    db = KnowledgeDB("groundtruth.db")
    spec = db.get_spec(SPEC_ID)
    assert spec is not None, f"{SPEC_ID} not found in MemBase"
    return spec


def test_spec_row_structure(spec_row: dict) -> None:
    """T1 (structural): SPEC row exists with type='requirement', status='specified', non-empty description."""
    assert spec_row.get("type") == "requirement"
    assert spec_row.get("status") == "specified"
    desc = spec_row.get("description") or ""
    assert desc.strip(), "SPEC description must be non-empty"


def test_description_enumerates_six_metrics(spec_row: dict) -> None:
    """T2 (enumeration): description enumerates all six counter requirements by name."""
    desc = spec_row.get("description") or ""
    for metric in (
        "advisory_count",
        "no_go_count",
        "actionable_count_for_prime",
        "actionable_count_for_lo",
        "advisory_disposition_count",
        "failed_proposal_count",
    ):
        assert metric in desc, f"description must enumerate the {metric!r} counter"


def test_no_go_count_excludes_advisory(spec_row: dict) -> None:
    """T3 (F1+F3 closure): description states no_go_count MUST NOT include ADVISORY entries."""
    desc = spec_row.get("description") or ""
    # The exclusion must be explicit. Accept either canonical phrasing.
    explicit = "no_go_count" in desc and ("MUST NOT include ADVISORY" in desc)
    assert explicit, (
        "description must explicitly state 'no_go_count' alongside 'MUST NOT include ADVISORY' (T3 F1+F3 closure)"
    )


def test_actionable_count_for_prime_excludes_verified(spec_row: dict) -> None:
    """T4 (F1+F3 closure): description states actionable_count_for_prime MUST NOT include latest VERIFIED."""
    desc = spec_row.get("description") or ""
    assert "actionable_count_for_prime" in desc, "description must reference 'actionable_count_for_prime'"
    assert "MUST NOT include latest VERIFIED" in desc, (
        "description must explicitly state 'MUST NOT include latest VERIFIED' "
        "for actionable_count_for_prime (T4 F1+F3 closure)"
    )


def test_advisory_disposition_count_separate(spec_row: dict) -> None:
    """T5 (F1+F3 closure): description identifies advisory_disposition_count as a separate Prime-disposition metric, distinct from actionable_count_for_prime."""
    desc = spec_row.get("description") or ""
    assert "advisory_disposition_count" in desc, "description must reference 'advisory_disposition_count'"
    # The "separate" / "disposition surface" framing must be explicit
    separate_phrasing = "separate disposition target" in desc or "disposition surface" in desc
    assert separate_phrasing, (
        "description must explicitly identify advisory_disposition_count as "
        "Prime's separate disposition surface (T5 F1+F3 closure)"
    )
    # Must reference the procedure rule for disposition recording
    assert ".claude/rules/peer-solution-advisory-loop.md" in desc, (
        "description must cite the procedure-rule path where disposition is recorded"
    )


def test_description_documents_display_distinction(spec_row: dict) -> None:
    """T6 (display distinction): description states dashboard surfaces MUST visually distinguish ADVISORY from NO-GO."""
    desc = spec_row.get("description") or ""
    assert "visually distinguish" in desc, "description must reference the visual-distinction display requirement (T6)"
    assert "ADVISORY" in desc and "NO-GO" in desc, (
        "description must explicitly reference both ADVISORY and NO-GO in the display requirement"
    )
