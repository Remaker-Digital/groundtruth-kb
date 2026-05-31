"""Tests for the governed ``gt backlog add-work-item`` CLI service.

Authority: bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-005.md
(REVISED-2), Codex GO at ``-006.md``. Source work item: WI-3455.

Spec-derived verification for the GOV-12 (work item triggers a linked test) +
GOV-13 (every test assigned to a test-plan phase at creation, fail-closed)
chain implemented by ``cli_backlog_add_work_item``. Every test runs against a
temporary ``groundtruth.db``; none mutate production state.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

_PHASE_ID = "PLAN-001-P1"


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _seed(db_path: Path) -> None:
    """Seed a spec, a test plan, and one empty phase so the chain can complete."""
    db = KnowledgeDB(db_path=db_path)
    db.insert_spec(
        id="SPEC-0001",
        title="Seed spec for add-work-item tests",
        status="specified",
        changed_by="test-seed",
        change_reason="seed",
        type="requirement",
    )
    db.insert_test_plan(
        id="PLAN-001",
        title="Seed plan",
        status="active",
        changed_by="test-seed",
        change_reason="seed",
    )
    db.insert_test_plan_phase(
        id=_PHASE_ID,
        plan_id="PLAN-001",
        phase_order=1,
        title="Pre-flight",
        gate_criteria="all pre-flight checks pass",
        changed_by="test-seed",
        change_reason="seed",
        test_ids=[],
    )
    db.close()


def _argv(config: Path, *extra: str) -> list[str]:
    return [
        "--config",
        str(config),
        "backlog",
        "add-work-item",
        "--title",
        "Migrate widget",
        "--origin",
        "new",
        "--component",
        "governance",
        "--source-spec-id",
        "SPEC-0001",
        "--test-title",
        "Verify widget migrated",
        "--test-type",
        "assertion",
        "--test-expected-outcome",
        "widget present in registry",
        "--change-reason",
        "slice 3 verb test",
        *extra,
    ]


def _counts(db_path: Path) -> tuple[int, int]:
    if not db_path.exists():
        return (0, 0)
    with sqlite3.connect(db_path) as conn:
        wi = conn.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
        tests = conn.execute("SELECT COUNT(*) FROM current_tests").fetchone()[0]
    return (int(wi), int(tests))


def _phase_test_ids(db_path: Path) -> list[str]:
    db = KnowledgeDB(db_path=db_path)
    phase = db.get_test_plan_phase(_PHASE_ID)
    db.close()
    raw = (phase or {}).get("test_ids")
    if isinstance(raw, str):
        raw = raw.strip()
        return list(json.loads(raw)) if raw else []
    return list(raw or [])


def _phase_versions(db_path: Path) -> int:
    with sqlite3.connect(db_path) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM test_plan_phases WHERE id = ?", (_PHASE_ID,)).fetchone()[0])


# --- GOV-12 + GOV-13 happy path --------------------------------------------


def test_creates_work_item_test_and_phase_assignment(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    wi, tests = _counts(db_path)
    assert wi == 1 and tests == 1
    assert payload["test_id"] in _phase_test_ids(db_path)
    assert payload["phase_id"] == _PHASE_ID


def test_test_links_to_source_spec_by_default(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--json"))
    assert result.exit_code == 0, result.output
    test_id = json.loads(result.output)["test_id"]
    db = KnowledgeDB(db_path=db_path)
    test_row = db.get_test(test_id)
    db.close()
    assert test_row is not None
    assert test_row["spec_id"] == "SPEC-0001"  # defaulted from --source-spec-id


# --- GOV-13 fail-closed -----------------------------------------------------


def test_missing_phase_fails_closed(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _counts(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config))  # no --test-plan-phase
    assert result.exit_code != 0
    assert "test-plan-phase" in result.output.lower() or "gov-13" in result.output.lower()
    assert _counts(db_path) == before  # no work item / test created


def test_invalid_phase_fails_closed(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _counts(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", "PLAN-001-NOPE"))
    assert result.exit_code != 0
    assert _counts(db_path) == before
    assert _phase_test_ids(db_path) == []  # real phase untouched


# --- GOV-13 append-only -----------------------------------------------------


def test_phase_assignment_appends_test_id_append_only(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    assert _phase_versions(db_path) == 1  # seeded version
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--json"))
    assert result.exit_code == 0, result.output
    test_id = json.loads(result.output)["test_id"]
    assert _phase_versions(db_path) == 2  # new append-only version
    assert test_id in _phase_test_ids(db_path)


# --- dry-run + fail-closed attribution -------------------------------------


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _counts(db_path)
    before_versions = _phase_versions(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--dry-run"))
    assert result.exit_code == 0, result.output
    assert "Would create" in result.output
    assert _counts(db_path) == before
    assert _phase_versions(db_path) == before_versions  # no new phase version


def test_fail_closed_attribution(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _counts(db_path)
    with (
        mock.patch.dict("os.environ", {}, clear=True),
        mock.patch("scripts._kb_attribution._resolve_harness_name", return_value=None),
    ):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID))
    assert result.exit_code != 0
    assert _counts(db_path) == before  # no work item / test created
