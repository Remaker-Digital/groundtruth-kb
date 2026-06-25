"""Spec-derived tests for the obsolete-reference-purge check (WI-4795).

Verifies ``DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`` assertions 1-3 and the
``ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`` doctor surface. Hermetic: the
integration tests build a fixture ``groundtruth.db`` and never mutate the live
MemBase, per the Loyal Opposition GO condition on bridge thread
``gtkb-obsolete-reference-purge-deterministic-check`` (-002).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
_SRC = _PROJECT_ROOT / "groundtruth-kb" / "src"
for _path in (_SCRIPTS, _SRC):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import check_obsolete_reference_purge as check  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

PAST_DATE = "2000-01-01"
FUTURE_DATE = "2099-01-01"
FIXTURE_SPEC = "RETIRE-SPEC-OBSOLETE-FIXTURE-001"


# ---------------------------------------------------------------------------
# Pure-function unit tests (hermetic; no database)
# ---------------------------------------------------------------------------


def test_is_retirement_class_retired_status():
    ok, reason = check.is_retirement_class({"id": "SPEC-1", "status": "retired"})
    assert ok
    assert "retired" in reason


def test_is_retirement_class_superseded_status():
    ok, _ = check.is_retirement_class({"id": "SPEC-2", "status": "superseded"})
    assert ok


def test_is_retirement_class_retire_spec_prefix():
    ok, reason = check.is_retirement_class({"id": FIXTURE_SPEC, "status": "specified"})
    assert ok
    assert "RETIRE-SPEC" in reason


def test_is_retirement_class_adr_supersedes_field():
    ok, reason = check.is_retirement_class(
        {
            "id": "ADR-X-001",
            "status": "specified",
            "type": "architecture_decision",
            "description": "Decision body.\nSupersedes: ADR-OLD-LOAD-BEARING-001\nConsequences...",
        }
    )
    assert ok
    assert "Supersedes" in reason


def test_is_retirement_class_definitional_supersedes_not_flagged():
    # Regression: an ADR/DCL whose PROSE contains the word "supersedes" (e.g. the
    # obligation DCL's own definition) but has no structured Supersedes: field must
    # NOT be flagged as retirement-class.
    ok, _ = check.is_retirement_class(
        {
            "id": "DCL-METHODOLOGY-001",
            "status": "specified",
            "type": "design_constraint",
            "description": "an ADR/DCL that supersedes a prior load-bearing implementation",
        }
    )
    assert not ok


def test_is_retirement_class_negative_active_spec():
    ok, _ = check.is_retirement_class(
        {"id": "SPEC-3", "status": "implemented", "type": "requirement", "description": "active"}
    )
    assert not ok


def test_paired_by_source_spec_id():
    work_items = [{"id": "WI-1", "source_spec_id": FIXTURE_SPEC}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) == "WI-1"


def test_paired_by_purges_token():
    work_items = [{"id": "WI-2", "description": f"purges: {FIXTURE_SPEC} residue"}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) == "WI-2"


def test_paired_by_purge_project_member():
    work_items = [
        {
            "id": "WI-3",
            "project_name": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
            "description": f"strip {FIXTURE_SPEC} references",
        }
    ]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) == "WI-3"


def test_unpaired_returns_none():
    work_items = [{"id": "WI-9", "description": "unrelated", "project_name": "OTHER"}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) is None


def test_in_window_boundary():
    start = check._window_start(None)
    assert check.in_window("2026-06-25T00:00:00Z", window_start=start)
    assert not check.in_window("2026-06-01T00:00:00Z", window_start=start)
    assert not check.in_window(None, window_start=start)


# ---------------------------------------------------------------------------
# Integration tests (fixture database; no live MemBase mutation)
# ---------------------------------------------------------------------------


def _fixture_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path)
    db.insert_spec(
        id=FIXTURE_SPEC,
        title="Fixture retire-spec",
        status="specified",
        changed_by="test",
        change_reason="fixture",
        type="requirement",
    )
    return db_path


def test_unpaired_retirement_in_window_warns(tmp_path):
    _fixture_db(tmp_path)
    result = check.evaluate(tmp_path, obligation_effective_date=PAST_DATE)
    assert result["status"] == "warning"
    assert any(f["artifact_id"] == FIXTURE_SPEC for f in result["unpaired"])


def test_paired_retirement_passes(tmp_path):
    _fixture_db(tmp_path)
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_work_item(
        id="WI-FIXTURE-PURGE",
        title="purge fixture",
        origin="hygiene",
        component="governance",
        resolution_status="open",
        changed_by="test",
        change_reason="fixture",
        source_spec_id=FIXTURE_SPEC,
    )
    result = check.evaluate(tmp_path, obligation_effective_date=PAST_DATE)
    assert result["status"] == "pass"
    assert result["unpaired"] == []
    assert any(f["artifact_id"] == FIXTURE_SPEC for f in result["paired"])


def test_pre_obligation_retirement_excluded(tmp_path):
    _fixture_db(tmp_path)
    # A future window start excludes the now-dated fixture -> no findings.
    result = check.evaluate(tmp_path, obligation_effective_date=FUTURE_DATE)
    assert result["status"] == "pass"
    assert result["evaluated"] == 0


def test_doctor_surface_warn_pass_failsoft(tmp_path):
    from groundtruth_kb.project.doctor import _check_obsolete_reference_purge

    _fixture_db(tmp_path)
    tool_check = _check_obsolete_reference_purge(tmp_path)
    # GO condition 1: doctor returns warning/pass, never fail.
    assert tool_check.status in {"warning", "pass"}
    assert tool_check.status != "fail"


def test_check_script_exists_at_declared_path():
    # DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 assertion 3.
    assert (_PROJECT_ROOT / "scripts" / "check_obsolete_reference_purge.py").is_file()


def test_adr_obligation_exists_with_type():
    # DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 assertion 2 (live read-only).
    root_db = _PROJECT_ROOT / "groundtruth.db"
    if not root_db.is_file():
        pytest.skip("live MemBase not present")
    db = KnowledgeDB(root_db)
    adrs = db.list_specs(type="architecture_decision")
    assert any(s.get("id") == "ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001" for s in adrs)
