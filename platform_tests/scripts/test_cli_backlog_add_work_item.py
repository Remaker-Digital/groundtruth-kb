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

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.cli_backlog_add_work_item import _coerce_test_ids  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

_PHASE_ID = "PLAN-001-P1"


@pytest.fixture(autouse=True)
def document_actor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep compound-writer tests focused; provenance validation has dedicated tests."""
    monkeypatch.setattr(
        "groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by",
        lambda _project_root: "prime-builder/claude",
    )


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


def _snapshot(db_path: Path) -> tuple[int, int, int, int]:
    with sqlite3.connect(db_path) as conn:
        return tuple(
            int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("work_items", "tests", "test_plan_phases", "pipeline_events")
        )


def _set_phase_test_ids_raw(db_path: Path, raw: str | None) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE test_plan_phases SET test_ids = ? WHERE id = ? AND version = 1",
            (raw, _PHASE_ID),
        )
        conn.commit()


def _repair_argv(
    config: Path,
    *extra: str,
    work_item_id: str = "WI-5325",
    test_id: str = "TEST-11462",
) -> list[str]:
    return [
        "--config",
        str(config),
        "backlog",
        "repair-work-item-test-link",
        "--work-item",
        work_item_id,
        "--test",
        test_id,
        "--test-plan-phase",
        _PHASE_ID,
        "--change-reason",
        "repair exact historical add-work-item pair",
        *extra,
    ]


def _seed_exact_pair(
    db_path: Path,
    *,
    work_item_id: str = "WI-5325",
    test_id: str = "TEST-11462",
    linked_test_id: str | None = None,
    phase_contains_test: bool = False,
    provenance: str | None = None,
) -> None:
    provenance = provenance or f"Auto-created with {work_item_id} via gt backlog add-work-item."
    db = KnowledgeDB(db_path=db_path)
    db.insert_work_item(
        id=work_item_id,
        title="Historical partial add-work-item row",
        origin="hygiene",
        component="governance",
        resolution_status="open",
        changed_by="test-seed",
        change_reason="seed exact historical pair",
        source_spec_id="SPEC-0001",
        source_test_id=linked_test_id,
        stage="backlogged",
    )
    db.insert_test(
        id=test_id,
        title="Historical linked test",
        spec_id="SPEC-0001",
        test_type="assertion",
        expected_outcome="relationship is complete",
        changed_by="test-seed",
        change_reason="seed exact historical pair",
        description=provenance,
    )
    if phase_contains_test:
        phase = db.get_test_plan_phase(_PHASE_ID)
        assert phase is not None
        db.insert_test_plan_phase(
            id=phase["id"],
            plan_id=phase["plan_id"],
            phase_order=phase["phase_order"],
            title=phase["title"],
            gate_criteria=phase["gate_criteria"],
            changed_by="test-seed",
            change_reason="seed exact phase membership",
            test_ids=[test_id],
        )
    db.close()


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
    db = KnowledgeDB(db_path=db_path)
    work_item = db.get_work_item(payload["work_item_id"])
    db.close()
    assert work_item is not None
    assert work_item["source_test_id"] == payload["test_id"]
    assert work_item["version"] == 1


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


def test_dry_run_requires_and_validates_phase(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _snapshot(db_path)

    result = CliRunner().invoke(main, _argv(config, "--dry-run"))

    assert result.exit_code != 0
    assert "test-plan-phase" in result.output
    assert _snapshot(db_path) == before


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
    with mock.patch(
        "groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by",
        side_effect=RuntimeError("worker role provenance is missing"),
    ):
        result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID))
    assert result.exit_code != 0
    assert _counts(db_path) == before  # no work item / test created


def test_compound_writer_resolves_one_document_actor_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config = _project(tmp_path)
    _seed(root / "groundtruth.db")
    resolver = mock.Mock(return_value="loyal-opposition/claude")
    monkeypatch.setattr("groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by", resolver)

    result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--json"))

    assert result.exit_code == 0, result.output
    assert resolver.call_count == 1


# --- strict phase preflight -------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, []),
        ([], []),
        (["TEST-0001", "TEST-9999"], ["TEST-0001", "TEST-9999"]),
        ('["TEST-0001", "TEST-9999"]', ["TEST-0001", "TEST-9999"]),
    ],
)
def test_phase_test_id_parser_accepts_canonical_forms(raw: object, expected: list[str]) -> None:
    assert _coerce_test_ids(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "not-json",
        "123",
        '"TEST-0001"',
        '["TEST-0001", "TEST-0001"]',
        '[""]',
        '[" TEST-0001"]',
        '["not-a-test"]',
        "[1]",
        {"TEST-0001": True},
    ],
)
def test_phase_test_id_parser_rejects_malformed_or_ambiguous_forms(raw: object) -> None:
    with pytest.raises(Exception, match="phase test_ids"):
        _coerce_test_ids(raw)


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize(
    "raw",
    [
        "not-json",
        "123",
        '["TEST-0001", "TEST-0001"]',
        '["not-a-test"]',
        "[1]",
    ],
)
def test_malformed_phase_fails_before_any_artifact_write(tmp_path: Path, raw: str, dry_run: bool) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    _set_phase_test_ids_raw(db_path, raw)
    before = _snapshot(db_path)
    args = ["--test-plan-phase", _PHASE_ID]
    if dry_run:
        args.append("--dry-run")

    result = CliRunner().invoke(main, _argv(config, *args))

    assert result.exit_code != 0
    assert _snapshot(db_path) == before


# --- one transaction and rollback -----------------------------------------


def test_success_commits_work_item_test_phase_and_existing_events_once(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _snapshot(db_path)

    result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID, "--json"))

    assert result.exit_code == 0, result.output
    after = _snapshot(db_path)
    assert after[:3] == (before[0] + 1, before[1] + 1, before[2] + 1)
    assert after[3] == before[3] + 2
    payload = json.loads(result.output)
    with sqlite3.connect(db_path) as conn:
        events = conn.execute(
            "SELECT event_type, artifact_id FROM pipeline_events WHERE artifact_id IN (?, ?) ORDER BY event_type",
            (payload["work_item_id"], payload["test_id"]),
        ).fetchall()
    assert events == [("test_created", payload["test_id"]), ("wi_created", payload["work_item_id"])]


@pytest.mark.parametrize("failure_point", ["work_item", "test", "phase", "readback", "commit"])
def test_injected_failure_rolls_back_every_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    before = _snapshot(db_path)

    if failure_point == "work_item":
        original = KnowledgeDB.insert_work_item

        def fail_after_work_item(self: KnowledgeDB, *args: object, **kwargs: object) -> object:
            original(self, *args, **kwargs)
            raise RuntimeError("injected work-item failure")

        monkeypatch.setattr(KnowledgeDB, "insert_work_item", fail_after_work_item)
    elif failure_point == "test":
        original = KnowledgeDB.insert_test

        def fail_after_test(self: KnowledgeDB, *args: object, **kwargs: object) -> object:
            original(self, *args, **kwargs)
            raise RuntimeError("injected test failure")

        monkeypatch.setattr(KnowledgeDB, "insert_test", fail_after_test)
    elif failure_point == "phase":
        original = KnowledgeDB.insert_test_plan_phase

        def fail_after_phase(self: KnowledgeDB, *args: object, **kwargs: object) -> object:
            original(self, *args, **kwargs)
            raise RuntimeError("injected phase failure")

        monkeypatch.setattr(KnowledgeDB, "insert_test_plan_phase", fail_after_phase)
    elif failure_point == "readback":
        original = KnowledgeDB.get_work_item
        calls = 0

        def fail_final_work_item_readback(self: KnowledgeDB, item_id: str) -> object:
            nonlocal calls
            calls += 1
            if calls >= 3:
                return None
            return original(self, item_id)

        monkeypatch.setattr(KnowledgeDB, "get_work_item", fail_final_work_item_readback)
    else:
        monkeypatch.setattr(
            "groundtruth_kb.cli_backlog_add_work_item._commit_transaction",
            mock.Mock(side_effect=RuntimeError("injected final commit failure")),
        )

    result = CliRunner().invoke(main, _argv(config, "--test-plan-phase", _PHASE_ID))

    assert result.exit_code != 0
    assert _snapshot(db_path) == before


# --- exact historical repair -----------------------------------------------


def test_exact_repair_dry_run_reports_versions_without_writing(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    _seed_exact_pair(db_path)
    before = _snapshot(db_path)

    result = CliRunner().invoke(main, _repair_argv(config, "--dry-run", "--json"))

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["work_item_version"] == 2
    assert payload["phase_version"] == 2
    assert payload["already_repaired"] is False
    assert _snapshot(db_path) == before


@pytest.mark.parametrize(
    ("work_item_id", "test_id"),
    [("WI-5325", "TEST-11462"), ("WI-5456", "TEST-11557")],
)
def test_exact_repair_links_named_pair_and_is_idempotent(
    tmp_path: Path,
    work_item_id: str,
    test_id: str,
) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    _seed_exact_pair(db_path, work_item_id=work_item_id, test_id=test_id)

    first = CliRunner().invoke(
        main,
        _repair_argv(config, "--json", work_item_id=work_item_id, test_id=test_id),
    )

    assert first.exit_code == 0, first.output
    db = KnowledgeDB(db_path=db_path)
    work_item = db.get_work_item(work_item_id)
    db.close()
    assert work_item is not None and work_item["source_test_id"] == test_id
    assert test_id in _phase_test_ids(db_path)
    after_first = _snapshot(db_path)

    second = CliRunner().invoke(
        main,
        _repair_argv(config, "--json", work_item_id=work_item_id, test_id=test_id),
    )

    assert second.exit_code == 0, second.output
    assert json.loads(second.output)["already_repaired"] is True
    assert _snapshot(db_path) == after_first


@pytest.mark.parametrize("conflict", ["provenance", "work_item", "other_work_item", "other_phase"])
def test_exact_repair_rejects_conflicting_or_ambiguous_evidence(tmp_path: Path, conflict: str) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    provenance = (
        "wrong provenance" if conflict == "provenance" else ("Auto-created with WI-5325 via gt backlog add-work-item.")
    )
    linked = "TEST-9999" if conflict == "work_item" else None
    _seed_exact_pair(db_path, linked_test_id=linked, provenance=provenance)
    db = KnowledgeDB(db_path=db_path)
    if conflict == "other_work_item":
        db.insert_work_item(
            id="WI-9999",
            title="Conflicting claimant",
            origin="hygiene",
            component="governance",
            resolution_status="open",
            changed_by="test-seed",
            change_reason="seed conflicting claimant",
            source_spec_id="SPEC-0001",
            source_test_id="TEST-11462",
        )
    elif conflict == "other_phase":
        db.insert_test_plan_phase(
            id="PLAN-001-P2",
            plan_id="PLAN-001",
            phase_order=2,
            title="Other phase",
            gate_criteria="other",
            changed_by="test-seed",
            change_reason="seed conflicting phase",
            test_ids=["TEST-11462"],
        )
    db.close()
    before = _snapshot(db_path)

    result = CliRunner().invoke(main, _repair_argv(config))

    assert result.exit_code != 0
    assert _snapshot(db_path) == before


def test_exact_repair_rolls_back_work_item_when_phase_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed(db_path)
    _seed_exact_pair(db_path)
    before = _snapshot(db_path)
    original = KnowledgeDB.insert_test_plan_phase

    def fail_after_phase(self: KnowledgeDB, *args: object, **kwargs: object) -> object:
        original(self, *args, **kwargs)
        raise RuntimeError("injected repair phase failure")

    monkeypatch.setattr(KnowledgeDB, "insert_test_plan_phase", fail_after_phase)

    result = CliRunner().invoke(main, _repair_argv(config))

    assert result.exit_code != 0
    assert _snapshot(db_path) == before
