"""Phase execution evidence must not survive the membership it was produced against.

Work item: WI-6126 (TEST-11861).
Governing: SPEC-1605, GOV-13, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

These tests are written test-first against the UNMODIFIED writers and are expected to
fail on the clearing assertions until the WI-6126 invariant lands. They must fail on
assertions, never on import or fixture error.

The rule under test is subtraction-first: on a semantic ``test_ids`` change the
evidence is cleared REGARDLESS of what the caller supplied, because
``insert_test_plan_phase`` carries no membership digest, executed phase version or
sentinel that could distinguish evidence copied from the prior row from evidence
genuinely produced for the new membership -- and all three production callers copy.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

_EXECUTED_AT = "2026-04-04T14:38:03.677803+00:00"


def _db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(db_path=str(tmp_path / "groundtruth.db"))


def _seed(db: KnowledgeDB, test_ids: list[str], *, result: str | None = "PASS") -> None:
    """Seed PHASE-001 with a membership and a recorded execution result."""
    db.insert_test_plan_phase(
        "PHASE-001",
        plan_id="PLAN-001",
        phase_order=1,
        title="Pre-flight Checks",
        gate_criteria="all pass",
        changed_by="test",
        change_reason="seed with recorded execution evidence",
        test_ids=test_ids,
        last_result=result,
        last_executed_at=_EXECUTED_AT if result else None,
    )


def _current(db: KnowledgeDB, phase_id: str = "PHASE-001") -> sqlite3.Row:
    row = db._get_conn().execute("SELECT * FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
    assert row is not None, f"{phase_id} missing"
    return row


def _copy_forward(db: KnowledgeDB, new_test_ids: list[str]) -> None:
    """Reproduce the exact production caller pattern.

    ``cli_backlog_add_work_item.py`` lines 731-733 grow the membership while
    explicitly copying the prior row's evidence forward in the same INSERT. This
    helper is that pattern verbatim, which is why an "explicit values are fresh"
    exception cannot work.
    """
    prior = _current(db)
    db.insert_test_plan_phase(
        "PHASE-001",
        plan_id=prior["plan_id"],
        phase_order=prior["phase_order"],
        title=prior["title"],
        gate_criteria=prior["gate_criteria"],
        changed_by="test",
        change_reason="membership change copying prior evidence forward",
        test_ids=new_test_ids,
        last_result=prior["last_result"],
        last_executed_at=prior["last_executed_at"],
    )


# --- clearing on semantic membership change --------------------------------


def test_membership_addition_clears_prior_result(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed(db, ["TEST-1", "TEST-2"])
    _copy_forward(db, ["TEST-1", "TEST-2", "TEST-3"])
    row = _current(db)
    assert row["last_result"] is None
    assert row["last_executed_at"] is None


def test_membership_removal_clears_prior_result(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed(db, ["TEST-1", "TEST-2"])
    _copy_forward(db, ["TEST-1"])
    row = _current(db)
    assert row["last_result"] is None
    assert row["last_executed_at"] is None


def test_explicit_stale_copy_is_cleared_not_trusted(tmp_path: Path) -> None:
    """The F1 case: an explicitly supplied value is not evidence of freshness."""
    db = _db(tmp_path)
    _seed(db, ["TEST-1"])
    # Caller explicitly supplies values -- exactly what all three production
    # callers do -- while changing membership. Subtraction-first clears anyway.
    db.insert_test_plan_phase(
        "PHASE-001",
        plan_id="PLAN-001",
        phase_order=1,
        title="Pre-flight Checks",
        gate_criteria="all pass",
        changed_by="test",
        change_reason="explicit copy of stale evidence alongside a membership change",
        test_ids=["TEST-1", "TEST-2"],
        last_result="PASS",
        last_executed_at=_EXECUTED_AT,
    )
    row = _current(db)
    assert row["last_result"] is None
    assert row["last_executed_at"] is None


def test_update_writer_also_clears_on_membership_change(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed(db, ["TEST-1"])
    db.update_test_plan_phase(
        "PHASE-001",
        changed_by="test",
        change_reason="membership change through the update writer",
        test_ids=["TEST-1", "TEST-2"],
    )
    row = _current(db)
    assert row["last_result"] is None
    assert row["last_executed_at"] is None


# --- preservation where membership did not semantically change -------------


def test_unchanged_membership_preserves_result(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed(db, ["TEST-1", "TEST-2"])
    db.update_test_plan_phase(
        "PHASE-001",
        changed_by="test",
        change_reason="title-only change, membership untouched",
        title="Pre-flight Checks (renamed)",
    )
    row = _current(db)
    assert row["last_result"] == "PASS"
    assert row["last_executed_at"] == _EXECUTED_AT


def test_idempotent_reordered_membership_preserves_result(tmp_path: Path) -> None:
    """Set-based comparison: reordering is not a semantic change."""
    db = _db(tmp_path)
    _seed(db, ["TEST-1", "TEST-2"])
    _copy_forward(db, ["TEST-2", "TEST-1"])
    row = _current(db)
    assert row["last_result"] == "PASS"
    assert row["last_executed_at"] == _EXECUTED_AT


def test_prior_versions_retain_their_own_evidence(tmp_path: Path) -> None:
    """Append-only history keeps the executed result readable at its own version."""
    db = _db(tmp_path)
    _seed(db, ["TEST-1"])
    _copy_forward(db, ["TEST-1", "TEST-2"])
    rows = (
        db._get_conn()
        .execute(
            "SELECT version, last_result, last_executed_at FROM test_plan_phases "
            "WHERE id = 'PHASE-001' ORDER BY version"
        )
        .fetchall()
    )
    assert len(rows) == 2
    assert rows[0]["last_result"] == "PASS"
    assert rows[0]["last_executed_at"] == _EXECUTED_AT
    assert rows[1]["last_result"] is None


# --- atomicity -------------------------------------------------------------


def test_injected_failure_rolls_back_membership_and_evidence(tmp_path: Path) -> None:
    """An injected failure leaves both membership and evidence unchanged."""
    db = _db(tmp_path)
    _seed(db, ["TEST-1"])
    before = _current(db)
    conn = db._get_conn()
    conn.execute("BEGIN IMMEDIATE")
    try:
        db.insert_test_plan_phase(
            "PHASE-001",
            plan_id="PLAN-001",
            phase_order=1,
            title="Pre-flight Checks",
            gate_criteria="all pass",
            changed_by="test",
            change_reason="doomed membership change",
            test_ids=["TEST-1", "TEST-2"],
            last_result="PASS",
            last_executed_at=_EXECUTED_AT,
            commit=False,
        )
        raise RuntimeError("injected failure")
    except RuntimeError:
        conn.rollback()
    after = _current(db)
    assert after["version"] == before["version"]
    assert after["test_ids"] == before["test_ids"]
    assert after["last_result"] == before["last_result"]
    assert after["last_executed_at"] == before["last_executed_at"]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
