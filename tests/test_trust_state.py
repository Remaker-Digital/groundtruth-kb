from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb import reconciliation
from groundtruth_kb.db import KnowledgeDB


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    kb = KnowledgeDB(db_path=tmp_path / "trust.db")
    yield kb
    kb.close()


def _insert_spec(db: KnowledgeDB, spec_id: str = "PB-001", **kwargs):
    return db.insert_spec(
        id=spec_id,
        title="Protected behavior",
        status=kwargs.pop("status", "verified"),
        changed_by="test",
        change_reason="seed",
        assertions=[{"type": "file_exists", "file": "README.md"}],
        **kwargs,
    )


def test_verified_with_latest_passing_assertion_is_passing(db: KnowledgeDB) -> None:
    _insert_spec(
        db,
        pbc_anchor="auth.session.expiry",
        verified_at="2026-05-01T00:00:00+00:00",
        verification_expires_after_days=30,
        required_evidence=["assertions"],
    )
    db.insert_assertion_run("PB-001", 1, True, [{"passed": True}], "test")

    trust = db.get_spec_trust_state("PB-001", now="2026-05-15T00:00:00+00:00")

    assert trust["trust_state"] == "passing"
    assert trust["reason"] == "latest_evidence_passed"
    assert trust["pbc_anchor"] == "auth.session.expiry"


def test_verified_with_latest_failing_assertion_is_failing(db: KnowledgeDB) -> None:
    _insert_spec(db, pbc_anchor="billing.invoice.total", required_evidence=["assertions"])
    db.insert_assertion_run("PB-001", 1, False, [{"passed": False}], "test")

    trust = db.get_spec_trust_state("PB-001")

    assert trust["trust_state"] == "failing"
    assert trust["reason"] == "latest_evidence_failed"


def test_verified_with_expired_lease_is_stale(db: KnowledgeDB) -> None:
    _insert_spec(
        db,
        verified_at="2026-04-01T00:00:00+00:00",
        verification_expires_after_days=7,
    )

    trust = db.get_spec_trust_state("PB-001", now="2026-05-15T00:00:00+00:00")

    assert trust["trust_state"] == "stale"
    assert trust["reason"] == "verification_lease_expired"


def test_passing_assertion_and_failing_test_is_disputed(db: KnowledgeDB) -> None:
    _insert_spec(db, required_evidence=["assertions", "tests"])
    db.insert_assertion_run("PB-001", 1, True, [{"passed": True}], "test")
    db.insert_test(
        id="TEST-001",
        title="Linked test",
        spec_id="PB-001",
        test_type="unit",
        expected_outcome="pass",
        changed_by="test",
        change_reason="seed",
        test_file="tests/test_behavior.py",
        test_function="test_behavior",
        last_result="fail",
    )

    trust = db.get_spec_trust_state("PB-001")

    assert trust["trust_state"] == "disputed"
    assert trust["reason"] == "conflicting_evidence"


def test_required_tau_task_replay_without_evidence_is_stale(db: KnowledgeDB) -> None:
    _insert_spec(db, required_evidence=["tau_task_replay"])

    trust = db.get_spec_trust_state("PB-001")

    assert trust["trust_state"] == "stale"
    assert trust["reason"] == "required_evidence_missing:tau_task_replay"


def test_trust_reconciliation_flags_failing_and_missing_anchor(db: KnowledgeDB) -> None:
    _insert_spec(db)
    db.insert_assertion_run("PB-001", 1, False, [{"passed": False}], "test")

    report = reconciliation.find_trust_state_drift(db)

    finding_types = {finding["type"] for finding in report.findings}
    assert "verified_but_failing" in finding_types
    assert "pbc_anchor_missing" in finding_types


def test_pbc_evidence_export_uses_anchor(db: KnowledgeDB) -> None:
    _insert_spec(db, pbc_anchor="auth.session.expiry")
    db.insert_assertion_run("PB-001", 1, True, [{"passed": True}], "test")

    evidence = db.export_pbc_evidence()

    assert evidence == [
        {
            "pbc_anchor": "auth.session.expiry",
            "spec_id": "PB-001",
            "spec_status": "verified",
            "trust_state": "passing",
            "reason": "latest_evidence_passed",
            "latest_assertion_run_at": evidence[0]["latest_assertion_run_at"],
            "latest_assertion_passed": 1,
        }
    ]
