# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for WI-5615 test-plan-phase JSON membership normalization."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from groundtruth_kb.cli_test_plan_phase import (  # noqa: E402
    PhaseMembershipNormalizeError,
    PhaseMembershipNormalizeRequest,
    normalize_phase_membership,
)
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

_LEGACY_MEMBERS = ["TEST-1480", "TEST-1481", "TEST-1482", "TEST-1483", "TEST-11239"]


def _db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(db_path=str(tmp_path / "groundtruth.db"))


def _seed_legacy_phase(db: KnowledgeDB, *, test_ids_raw: str | None = None) -> None:
    """Seed PHASE-003 with a comma-delimited (legacy) test_ids via direct row write.

    We write the raw malformed value directly to simulate the pre-existing
    production malformation (WI-5615), bypassing the JSON-encoding insert.
    """
    raw = test_ids_raw if test_ids_raw is not None else ",".join(_LEGACY_MEMBERS)
    db.insert_test_plan_phase(
        "PHASE-003",
        plan_id="PLAN-001",
        phase_order=3,
        title="Production Regression",
        gate_criteria="all pass",
        changed_by="test",
        change_reason="seed",
        test_ids=None,
    )
    # Overwrite the just-inserted version's test_ids with the raw legacy string.
    conn = db._get_conn()
    conn.execute("UPDATE test_plan_phases SET test_ids = ? WHERE id = ?", (raw, "PHASE-003"))
    conn.commit()


def _raw_sha(db: KnowledgeDB, phase_id: str) -> str:
    conn = db._get_conn()
    row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
    return hashlib.sha256((row["test_ids"] or "").encode("utf-8")).hexdigest()


def _phase_version(db: KnowledgeDB, phase_id: str) -> int | None:
    conn = db._get_conn()
    row = conn.execute("SELECT version FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
    return row["version"] if row is not None else None


# --- dry-run ---------------------------------------------------------------


def test_dry_run_reports_members_without_appending(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db)
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=1,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
            dry_run=True,
        )
        result = normalize_phase_membership(db, request)
        assert result.member_count == len(_LEGACY_MEMBERS)
        assert result.member_list == _LEGACY_MEMBERS
        assert result.applied is False
        assert _phase_version(db, "PHASE-003") == 1  # no append
        # other phases unchanged
    finally:
        db.close()


# --- apply -----------------------------------------------------------------


def test_apply_appends_one_json_version_preserving_order(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db)
    try:
        before_version = _phase_version(db, "PHASE-003")
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=before_version,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
            dry_run=False,
        )
        result = normalize_phase_membership(db, request)
        assert result.applied is True
        assert result.new_version == before_version + 1
        # read back the new row raw value: must be canonical JSON array
        conn = db._get_conn()
        row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id = ?", ("PHASE-003",)).fetchone()
        raw = row["test_ids"]
        assert raw.startswith("[")
        decoded = json.loads(raw)
        assert decoded == _LEGACY_MEMBERS  # order + membership preserved byte-for-member
        assert result.new_raw_sha256 == hashlib.sha256(raw.encode("utf-8")).hexdigest()
    finally:
        db.close()


# --- fail-closed -----------------------------------------------------------


def test_wrong_phase_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db)
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-999",
            expected_version=1,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
        )
        with pytest.raises(PhaseMembershipNormalizeError):
            normalize_phase_membership(db, request)
    finally:
        db.close()


def test_version_drift_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db)
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=99,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
        )
        with pytest.raises(PhaseMembershipNormalizeError) as excinfo:
            normalize_phase_membership(db, request)
        assert "version drift" in str(excinfo.value)
        assert _phase_version(db, "PHASE-003") == 1  # no partial mutation
    finally:
        db.close()


def test_hash_drift_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db)
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=1,
            expected_raw_sha256="0" * 64,
        )
        with pytest.raises(PhaseMembershipNormalizeError) as excinfo:
            normalize_phase_membership(db, request)
        assert "hash drift" in str(excinfo.value)
        assert _phase_version(db, "PHASE-003") == 1
    finally:
        db.close()


def test_malformed_legacy_member_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db, test_ids_raw="TEST-1480,NOTATEST,TEST-1481")
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=1,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
        )
        with pytest.raises(PhaseMembershipNormalizeError) as excinfo:
            normalize_phase_membership(db, request)
        assert "non-canonical" in str(excinfo.value)
    finally:
        db.close()


def test_duplicate_member_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _seed_legacy_phase(db, test_ids_raw="TEST-1480,TEST-1480")
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-003",
            expected_version=1,
            expected_raw_sha256=_raw_sha(db, "PHASE-003"),
        )
        with pytest.raises(PhaseMembershipNormalizeError) as excinfo:
            normalize_phase_membership(db, request)
        assert "duplicate" in str(excinfo.value)
    finally:
        db.close()


def test_already_json_phase_fails(tmp_path: Path) -> None:
    db = _db(tmp_path)
    # Seed a proper JSON-encoded phase via the normal insert path.
    db.insert_test_plan_phase(
        "PHASE-004",
        plan_id="PLAN-001",
        phase_order=4,
        title="Already JSON",
        gate_criteria="all pass",
        changed_by="test",
        change_reason="seed",
        test_ids=["TEST-1", "TEST-2"],
    )
    try:
        request = PhaseMembershipNormalizeRequest(
            phase_id="PHASE-004",
            expected_version=1,
            expected_raw_sha256=_raw_sha(db, "PHASE-004"),
        )
        with pytest.raises(PhaseMembershipNormalizeError) as excinfo:
            normalize_phase_membership(db, request)
        assert "already" in str(excinfo.value).lower()
    finally:
        db.close()
