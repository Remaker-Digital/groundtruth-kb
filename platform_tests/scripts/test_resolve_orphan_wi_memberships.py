"""Tests for the orphan-WI membership resolution driver (Slice 2; WI-3450).

Authority: bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-003.md
(REVISED-1), Codex GO at -004. Source work item: WI-3450. Project
authorization: PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001. Owner-decision
source: DELIB-2509.

Covers the 10-test Spec-Derived Verification Plan from the GO'd proposal:

* T1 ``build_resolution_plan`` is a pure function (no DB access; deterministic
  output from a given inventory).
* T2 high-confidence recoverable (>= 0.80) maps to ``assign_candidate``.
* T3 low-confidence recoverable (title_match 0.70) maps to ``owner_pick``.
* T4 unrecoverable maps to ``owner_decision``; ``apply_resolution`` skips it
  fail-closed when no decision entry is present.
* T5 ``apply_resolution`` performs an assignment via ``add_project_item`` for
  an ``assign`` decision.
* T6 ``apply_resolution`` writes a deferred-actions record for a ``retire``
  or ``exclude`` decision (NO canonical mutation).
* T7 idempotency: applying ``assign`` for a WI already a member is a no-op.
* T8 the driver re-runs discovery (calls ``build_inventory``) before
  planning -- fresh orphan set, not a stale report.
* T9 threshold boundary: ``id_match`` (0.80) is ``assign_candidate``;
  ``title_match`` (0.70) is ``owner_pick``.
* T10 ``--apply`` without ``--decisions`` errors (CLI guard).

All tests run against temporary DBs seeded inline; no test mutates the
canonical ``groundtruth.db`` or any other production artifact.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: E402

from scripts.resolve_orphan_wi_memberships import (  # noqa: E402
    HIGH_CONFIDENCE_THRESHOLD,
    RESOLUTION_ACTIONS,
    apply_resolution,
    build_and_run,
    build_resolution_plan,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_minimal_project(db_path: Path) -> None:
    """Seed a minimal canonical project for assignment tests.

    Creates PROJECT-X (canonical-shape id; the doubled-prefix bug would
    produce PROJECT-PROJECT-X, but the idempotent fix prevents that) so the
    test's ``assign`` decision has a legitimate target.
    """
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project(
            name="X",
            id="PROJECT-X",
            changed_by="test-seed",
            change_reason="seed minimal target project for resolve driver tests",
        )
    finally:
        db.close()


def _seed_orphan_wi(db_path: Path, wi_id: str, title: str) -> None:
    """Insert a single orphan-shaped WI (no project_name, no membership)."""
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_work_item(
            id=wi_id,
            title=title,
            origin="new",
            component="backlog",
            resolution_status="open",
            changed_by="test-seed",
            change_reason="seed orphan WI for resolve driver tests",
        )
    finally:
        db.close()


def _seed_assigned_wi(db_path: Path, wi_id: str, project_id: str) -> None:
    """Insert a WI and link it to ``project_id`` (membership pre-exists)."""
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_work_item(
            id=wi_id,
            title="Pre-membered WI",
            origin="new",
            component="backlog",
            resolution_status="open",
            changed_by="test-seed",
            change_reason="seed pre-membered WI for idempotence test",
        )
        db.link_project_work_item(
            project_id=project_id,
            work_item_id=wi_id,
            changed_by="test-seed",
            change_reason="seed pre-existing canonical membership for idempotence test",
        )
    finally:
        db.close()


def _inventory(*orphans: dict) -> dict:
    """Synthesize a discovery-shaped inventory for plan tests."""
    return {
        "run_id": "synthesized-for-test",
        "generated_at": "2026-05-29T00:00:00+00:00",
        "orphan_count": len(orphans),
        "orphan_count_by_class": {},  # not consumed by the planner
        "orphans": list(orphans),
    }


# ---------------------------------------------------------------------------
# T1 build_resolution_plan is pure (no DB access)
# ---------------------------------------------------------------------------


def test_plan_generation_is_pure_no_db_access(tmp_path: Path) -> None:
    """T1: the planner is a pure function over the inventory; no DB needed."""
    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Pure plan-gen",
            "recoverability_class": "recoverable_via_source_spec",
            "confidence_score": 0.95,
            "candidate_project_id": "PROJECT-X",
        }
    )
    plan = build_resolution_plan(inv)
    assert plan["orphan_count"] == 1
    assert plan["high_confidence_threshold"] == HIGH_CONFIDENCE_THRESHOLD
    assert plan["entries"][0]["planned_action"] == "assign_candidate"
    # The plan vocabulary is locked to the published action set.
    for entry in plan["entries"]:
        assert entry["planned_action"] in RESOLUTION_ACTIONS


# ---------------------------------------------------------------------------
# T2 high-confidence -> assign_candidate
# ---------------------------------------------------------------------------


def test_high_confidence_maps_to_candidate_assign() -> None:
    """T2: 0.95 source_spec class -> assign_candidate."""
    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "High confidence",
            "recoverability_class": "recoverable_via_source_spec",
            "confidence_score": 0.95,
            "candidate_project_id": "PROJECT-X",
        }
    )
    plan = build_resolution_plan(inv)
    assert plan["entries"][0]["planned_action"] == "assign_candidate"
    assert plan["entries"][0]["candidate_project_id"] == "PROJECT-X"


# ---------------------------------------------------------------------------
# T3 low-confidence (title_match 0.70) -> owner_pick
# ---------------------------------------------------------------------------


def test_low_confidence_maps_to_owner_pick() -> None:
    """T3: title_match 0.70 is below the 0.80 threshold -> owner_pick."""
    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Low confidence",
            "recoverability_class": "recoverable_via_title_match",
            "confidence_score": 0.70,
            "candidate_project_id": "PROJECT-X",
        }
    )
    plan = build_resolution_plan(inv)
    assert plan["entries"][0]["planned_action"] == "owner_pick"


# ---------------------------------------------------------------------------
# T4 unrecoverable -> owner_decision; apply skips without a decision
# ---------------------------------------------------------------------------


def test_unrecoverable_requires_owner_decision(tmp_path: Path) -> None:
    """T4: unrecoverable plans owner_decision; apply skips fail-closed."""
    db_path = tmp_path / "groundtruth.db"
    _seed_orphan_wi(db_path, "WI-9001", "Unrecoverable")

    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Unrecoverable",
            "recoverability_class": "unrecoverable",
            "confidence_score": 0.0,
            "candidate_project_id": None,
        }
    )
    plan = build_resolution_plan(inv)
    assert plan["entries"][0]["planned_action"] == "owner_decision"

    db = KnowledgeDB(db_path=db_path)
    try:
        service = ProjectLifecycleService(db)
        deferred_path = tmp_path / "deferred.json"
        results = apply_resolution(
            plan,
            decisions={},  # NO decisions
            service=service,
            db=db,
            deferred_actions_path=deferred_path,
        )
    finally:
        db.close()

    assert results["skipped_no_decision"] == ["WI-9001"]
    assert results["assigned"] == []
    assert results["deferred_actions_written"] == []
    # No deferred-actions file should have been created either.
    assert not deferred_path.exists()


# ---------------------------------------------------------------------------
# T5 apply_resolution assigns via add_project_item for an assign decision
# ---------------------------------------------------------------------------


def test_apply_assigns_with_decision_evidence(tmp_path: Path) -> None:
    """T5: assign decision -> service.add_project_item produces the membership."""
    db_path = tmp_path / "groundtruth.db"
    _seed_minimal_project(db_path)
    _seed_orphan_wi(db_path, "WI-9001", "Will be assigned")

    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Will be assigned",
            "recoverability_class": "recoverable_via_source_spec",
            "confidence_score": 0.95,
            "candidate_project_id": "PROJECT-X",
        }
    )
    plan = build_resolution_plan(inv)
    decisions = {
        "WI-9001": {
            "action": "assign",
            "project_id": "PROJECT-X",
            "decision_evidence": "AUQ 2026-05-29 test",
        }
    }

    db = KnowledgeDB(db_path=db_path)
    try:
        service = ProjectLifecycleService(db)
        results = apply_resolution(
            plan,
            decisions=decisions,
            service=service,
            db=db,
            deferred_actions_path=tmp_path / "deferred.json",
        )
        members = db.list_project_work_items("PROJECT-X", include_inactive=False)
    finally:
        db.close()

    assert results["assigned"] == [{"work_item_id": "WI-9001", "project_id": "PROJECT-X"}]
    assert any(str(m.get("work_item_id")) == "WI-9001" for m in members)


# ---------------------------------------------------------------------------
# T6 retire/exclude decision writes deferred-action record (no canonical mut.)
# ---------------------------------------------------------------------------


def test_apply_writes_deferred_action_for_retire(tmp_path: Path) -> None:
    """T6: retire decision writes deferred-actions record; canonical untouched."""
    db_path = tmp_path / "groundtruth.db"
    _seed_orphan_wi(db_path, "WI-9001", "Will be deferred")

    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Will be deferred",
            "recoverability_class": "unrecoverable",
            "confidence_score": 0.0,
            "candidate_project_id": None,
        }
    )
    plan = build_resolution_plan(inv)
    decisions = {
        "WI-9001": {
            "action": "retire",
            "decision_evidence": "AUQ 2026-05-29 owner retire decision",
        }
    }
    deferred_path = tmp_path / "deferred.json"

    db = KnowledgeDB(db_path=db_path)
    try:
        service = ProjectLifecycleService(db)
        results = apply_resolution(
            plan,
            decisions=decisions,
            service=service,
            db=db,
            deferred_actions_path=deferred_path,
        )
        # Canonical state for WI-9001: still an orphan (no active membership).
        # We probe the resolution_status as a coarse-grained check that retire
        # was NOT executed; per-WI retire would flip it to ``retired``.
        wi = db.get_work_item("WI-9001")
        wi_status = str(wi.get("resolution_status")) if wi else ""
    finally:
        db.close()

    assert len(results["deferred_actions_written"]) == 1
    assert results["deferred_actions_written"][0]["action"] == "retire"
    assert results["assigned"] == []
    assert deferred_path.exists()
    saved = json.loads(deferred_path.read_text(encoding="utf-8"))
    assert isinstance(saved, list) and len(saved) == 1
    assert saved[0]["work_item_id"] == "WI-9001"
    assert saved[0]["action"] == "retire"
    # Fail-closed contract: WI was not retired by this slice.
    assert wi_status == "open"


# ---------------------------------------------------------------------------
# T7 idempotency: assign for already-member WI is a no-op
# ---------------------------------------------------------------------------


def test_apply_idempotent_already_member(tmp_path: Path) -> None:
    """T7: re-asserting an existing membership is a no-op."""
    db_path = tmp_path / "groundtruth.db"
    _seed_minimal_project(db_path)
    _seed_assigned_wi(db_path, "WI-9001", "PROJECT-X")

    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Already a member",
            "recoverability_class": "recoverable_via_source_spec",
            "confidence_score": 0.95,
            "candidate_project_id": "PROJECT-X",
        }
    )
    plan = build_resolution_plan(inv)
    decisions = {
        "WI-9001": {
            "action": "assign",
            "project_id": "PROJECT-X",
            "decision_evidence": "AUQ test - already member",
        }
    }

    db = KnowledgeDB(db_path=db_path)
    try:
        service = ProjectLifecycleService(db)
        results = apply_resolution(
            plan,
            decisions=decisions,
            service=service,
            db=db,
            deferred_actions_path=tmp_path / "deferred.json",
        )
        # Count active memberships -- still exactly one, no duplicate.
        members = db.list_project_work_items("PROJECT-X", include_inactive=False)
        wi_memberships = [m for m in members if str(m.get("work_item_id")) == "WI-9001"]
    finally:
        db.close()

    assert results["already_member_noop"] == [{"work_item_id": "WI-9001", "project_id": "PROJECT-X"}]
    assert results["assigned"] == []
    assert len(wi_memberships) == 1


# ---------------------------------------------------------------------------
# T8 driver re-runs discovery (calls build_inventory) before planning
# ---------------------------------------------------------------------------


def test_driver_reruns_discovery_for_fresh_set(tmp_path: Path) -> None:
    """T8: build_and_run calls build_inventory on each invocation.

    Strategy: build_and_run with an empty seeded DB produces a plan with
    zero orphan entries. We then seed one orphan and call build_and_run
    again -- the plan now reflects the new orphan. Stale-report consumption
    would produce identical plans across calls; fresh discovery does not.
    """
    db_path = tmp_path / "groundtruth.db"
    _seed_minimal_project(db_path)

    report_a = build_and_run(
        db_path,
        apply=False,
        decisions_path=None,
        run_id="rerun-test-a",
        deferred_actions_path=None,
    )
    assert report_a["plan"]["orphan_count"] == 0

    # Seed an orphan AFTER the first call; the second call must see it.
    _seed_orphan_wi(db_path, "WI-9001", "Fresh orphan after first call")
    report_b = build_and_run(
        db_path,
        apply=False,
        decisions_path=None,
        run_id="rerun-test-b",
        deferred_actions_path=None,
    )
    assert report_b["plan"]["orphan_count"] == 1
    assert report_b["plan"]["entries"][0]["work_item_id"] == "WI-9001"


# ---------------------------------------------------------------------------
# T9 threshold boundary at 0.80
# ---------------------------------------------------------------------------


def test_threshold_boundary_at_080() -> None:
    """T9: id_match (0.80) -> assign_candidate; title_match (0.70) -> owner_pick."""
    inv = _inventory(
        {
            "id": "WI-9001",
            "title": "Boundary high",
            "recoverability_class": "recoverable_via_id_match",
            "confidence_score": 0.80,
            "candidate_project_id": "PROJECT-X",
        },
        {
            "id": "WI-9002",
            "title": "Boundary low",
            "recoverability_class": "recoverable_via_title_match",
            "confidence_score": 0.70,
            "candidate_project_id": "PROJECT-X",
        },
    )
    plan = build_resolution_plan(inv)
    by_id = {e["work_item_id"]: e["planned_action"] for e in plan["entries"]}
    assert by_id["WI-9001"] == "assign_candidate"
    assert by_id["WI-9002"] == "owner_pick"


# ---------------------------------------------------------------------------
# T10 --apply without --decisions errors (CLI guard)
# ---------------------------------------------------------------------------


def test_apply_requires_decisions_path(tmp_path: Path) -> None:
    """T10: build_and_run raises ValueError when apply=True and decisions=None."""
    db_path = tmp_path / "groundtruth.db"
    _seed_minimal_project(db_path)
    with pytest.raises(ValueError, match="--apply requires --decisions"):
        build_and_run(
            db_path,
            apply=True,
            decisions_path=None,
            run_id="guard-test",
            deferred_actions_path=None,
        )
