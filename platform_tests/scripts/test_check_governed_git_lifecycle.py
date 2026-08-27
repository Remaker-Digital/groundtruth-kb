"""Semantic regression tests for the governed two-tier Git lifecycle evaluator.

Registered as the canonical regression test by:

- ``ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001``
- ``REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001``

Each record's postimage is covered by a positive branch (the contract holds, the
family passes) and a negative branch (the contract is violated, the family fails).
Behaviour markers required by the registered assertions:

- ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:positive
- ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:negative
- REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:positive
- REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:negative

WI-6547 (PROJECT-GTKB-GET-HEALTHY-PHASE-3).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_governed_git_lifecycle import (  # noqa: E402
    ADR_EVALUATOR_ID,
    ADR_SPEC_ID,
    REQ_EVALUATOR_ID,
    REQ_SPEC_ID,
    REQUIRED_CONSTRAINTS,
    Report,
    check_evaluator_binding,
    check_record_active,
    check_records_agree,
    check_semantic_invariants,
    check_singleton_work_item_per_commit,
)


def _spec(spec_id: str, evaluator_id: str, **overrides: object) -> dict[str, object]:
    constraints: dict[str, object] = {"canonical_evaluator_id": evaluator_id}
    constraints.update(REQUIRED_CONSTRAINTS)
    constraints.update(overrides)
    return {"id": spec_id, "version": 3, "status": "active", "constraints": json.dumps(constraints)}


def _only(report: Report) -> bool:
    assert report.findings, "evaluator produced no findings"
    return not report.violations


# --- ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:positive ----------------------


def test_adr_active_bound_and_consistent_record_passes() -> None:
    """ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:positive."""
    report = Report()
    spec = _spec(ADR_SPEC_ID, ADR_EVALUATOR_ID)
    check_record_active(report, spec, ADR_SPEC_ID)
    check_evaluator_binding(report, spec, ADR_SPEC_ID, ADR_EVALUATOR_ID)
    check_semantic_invariants(report, spec, ADR_SPEC_ID)
    assert _only(report), [f.detail for f in report.violations]
    assert len(report.findings) == 3


# --- ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:negative ----------------------


def test_adr_claiming_verified_has_lifecycle_effect_fails() -> None:
    """ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:negative.

    The decision states VERIFIED emission has no terminality or activation effect.
    A record asserting the opposite is contradictory evidence and must fail closed.
    """
    report = Report()
    spec = _spec(ADR_SPEC_ID, ADR_EVALUATOR_ID, verified_emission_has_lifecycle_effect=True)
    check_semantic_invariants(report, spec, ADR_SPEC_ID)
    assert not _only(report)
    assert "verified_emission_has_lifecycle_effect" in report.violations[0].detail


def test_adr_absent_record_fails_closed() -> None:
    """ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001:negative (missing evidence)."""
    report = Report()
    check_record_active(report, None, ADR_SPEC_ID)
    check_evaluator_binding(report, None, ADR_SPEC_ID, ADR_EVALUATOR_ID)
    assert not _only(report)
    assert len(report.violations) == 2


# --- REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:positive --------------------------


def test_req_active_bound_and_consistent_record_passes() -> None:
    """REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:positive."""
    report = Report()
    spec = _spec(REQ_SPEC_ID, REQ_EVALUATOR_ID)
    check_record_active(report, spec, REQ_SPEC_ID)
    check_evaluator_binding(report, spec, REQ_SPEC_ID, REQ_EVALUATOR_ID)
    check_semantic_invariants(report, spec, REQ_SPEC_ID)
    assert _only(report), [f.detail for f in report.violations]


# --- REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:negative --------------------------


def test_req_wrong_evaluator_binding_fails() -> None:
    """REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:negative."""
    report = Report()
    spec = _spec(REQ_SPEC_ID, "some-other-evaluator")
    check_evaluator_binding(report, spec, REQ_SPEC_ID, REQ_EVALUATOR_ID)
    assert not _only(report)
    assert REQ_EVALUATOR_ID in report.violations[0].detail


def test_req_retired_record_fails() -> None:
    """REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001:negative (inactive record)."""
    report = Report()
    spec = _spec(REQ_SPEC_ID, REQ_EVALUATOR_ID)
    spec["status"] = "retired"
    check_record_active(report, spec, REQ_SPEC_ID)
    assert not _only(report)
    assert "retired" in report.violations[0].detail


# --- cross-record agreement ------------------------------------------------


def test_records_that_disagree_fail_closed() -> None:
    report = Report()
    adr = _spec(ADR_SPEC_ID, ADR_EVALUATOR_ID)
    req = _spec(REQ_SPEC_ID, REQ_EVALUATOR_ID, dispatcher_post_verified_reconciliation_required=False)
    check_records_agree(report, adr, req)
    assert not _only(report)
    assert "disagree" in report.violations[0].detail


def test_records_that_agree_pass() -> None:
    report = Report()
    check_records_agree(report, _spec(ADR_SPEC_ID, ADR_EVALUATOR_ID), _spec(REQ_SPEC_ID, REQ_EVALUATOR_ID))
    assert _only(report)


# --- terminal-commit families against live repository state ----------------


def test_singleton_work_item_family_reports_against_live_repo() -> None:
    """The singleton-work-item family evaluates live Git state without mutating it."""
    report = Report()
    check_singleton_work_item_per_commit(report, REPO_ROOT, limit=40)
    assert len(report.findings) == 1
    assert report.findings[0].family == "terminal-commit:singleton-work-item"


def test_missing_git_evidence_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unavailable Git evidence yields a violation, never a silent pass.

    The failure is injected at the git shim rather than by pointing the evaluator at
    a non-repository directory: pytest's tmp_path resolves inside the project root
    (the root-boundary rule keeps temp output in-root), so a temp directory still
    discovers the enclosing repository and would not exercise this branch.
    """
    import scripts.check_governed_git_lifecycle as evaluator

    monkeypatch.setattr(evaluator, "_git", lambda *args, **kwargs: None)
    report = Report()
    evaluator.check_singleton_work_item_per_commit(report, REPO_ROOT, limit=5)
    assert not _only(report)
    assert "fail-closed" in report.violations[0].detail


@pytest.mark.parametrize("marker", [ADR_EVALUATOR_ID, REQ_EVALUATOR_ID])
def test_evaluator_declares_its_contract_markers(marker: str) -> None:
    """Both canonical_evaluator_id values are declared by the evaluator source."""
    source = (REPO_ROOT / "scripts" / "check_governed_git_lifecycle.py").read_text(encoding="utf-8")
    assert marker in source
