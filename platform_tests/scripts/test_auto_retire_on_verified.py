"""Regression tests for WI-4741 automatic project retirement on VERIFIED."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = REPO_ROOT / "scripts" / "project_verified_completion_scanner.py"
CLAUDE_HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
CODEX_HELPER_PATH = REPO_ROOT / ".codex" / "skills" / "verify" / "helpers" / "write_verdict.py"


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _seed_project(project_root: Path, statuses: dict[str, str], *, project_id: str = "PROJECT-X") -> KnowledgeDB:
    db = KnowledgeDB(project_root / "groundtruth.db")
    db.insert_project("Auto Retire Project", "test", "seed", id=project_id, status="active")
    for work_item_id, status in statuses.items():
        db.insert_work_item(
            work_item_id,
            f"Work item {work_item_id}",
            "new",
            "backlog",
            status,
            "test",
            "seed",
        )
        db.link_project_work_item(project_id, work_item_id, "test", "seed")
    return db


def _seed_authorization(db: KnowledgeDB, work_item_ids: list[str], *, project_id: str = "PROJECT-X") -> None:
    db.insert_deliberation(
        "DELIB-SEED",
        "owner_conversation",
        "Owner approved",
        "Owner approved the fixture authorization.",
        "{}",
        "test",
        "seed",
        outcome="owner_decision",
    )
    db.insert_spec(id="SPEC-SEED", title="Seed spec", status="verified", changed_by="test", change_reason="seed")
    db.insert_project_authorization(
        project_id,
        "Fixture authorization",
        "DELIB-SEED",
        "Bounded scope.",
        "test",
        "seed",
        id="PAUTH-X",
        status="active",
        included_work_item_ids=work_item_ids,
        included_spec_ids=["SPEC-SEED"],
    )


def _write_verified_threads(project_root: Path, db: KnowledgeDB, work_item_ids: list[str]) -> None:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    for index, work_item_id in enumerate(work_item_ids):
        slug = f"gtkb-auto-retire-fixture-{index}"
        (bridge / f"{slug}-001.md").write_text(
            f"VERIFIED\n\n# Fixture verdict\n\nWork Item: {work_item_id}\n",
            encoding="utf-8",
        )
        db.add_project_artifact_link(
            "PROJECT-X",
            "bridge_thread",
            slug,
            "test",
            "seed implements link",
            relationship="implements",
        )


def _add_completion_guard(db: KnowledgeDB) -> None:
    db.add_project_artifact_link(
        "PROJECT-X",
        "completion_guard",
        "plan-incomplete-fixture",
        "test",
        "seed plan_incomplete guard",
        relationship="plan_incomplete",
    )


def test_auto_retire_completed_projects_retires_all_terminal_members(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "resolved"})
    try:
        service = ProjectLifecycleService(db)
        records = service.auto_retire_completed_projects(project_root=tmp_path)

        assert [record["project_id"] for record in records] == ["PROJECT-X"]
        assert db.get_project("PROJECT-X")["status"] == "retired"
        assert db.list_project_work_items("PROJECT-X") == []
        assert db.get_work_item("WI-1")["resolution_status"] == "retired"
        assert db.get_work_item("WI-2")["resolution_status"] == "retired"
    finally:
        db.close()


def test_auto_retire_skips_open_member_work_item(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open"})
    try:
        service = ProjectLifecycleService(db)

        assert service.auto_retire_completed_projects(project_root=tmp_path) == []
        status = service.member_completion_status("PROJECT-X")
        assert status["nonterminal_work_item_ids"] == ["WI-2"]
        assert "nonterminal_member_work_items" in status["exclusion_reasons"]
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


def test_auto_retire_skips_zero_member_project(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_project("Empty Project", "test", "seed", id="PROJECT-X", status="active")
        service = ProjectLifecycleService(db)

        assert service.auto_retire_completed_projects(project_root=tmp_path) == []
        assert "zero_active_members" in service.member_completion_status("PROJECT-X")["exclusion_reasons"]
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


def test_auto_retire_skips_plan_incomplete_guard(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified"})
    try:
        _add_completion_guard(db)
        service = ProjectLifecycleService(db)

        assert service.auto_retire_completed_projects(project_root=tmp_path) == []
        status = service.member_completion_status("PROJECT-X")
        assert status["completion_guarded"] is True
        assert "plan_incomplete_guard" in status["exclusion_reasons"]
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


def test_keep_open_election_blocks_later_auto_retire_sweep(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified"})
    try:
        _seed_authorization(db, ["WI-1"])
        _write_verified_threads(tmp_path, db, ["WI-1"])
        service = ProjectLifecycleService(db)

        kept_open = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete but keep open",
            retire_project=False,
        )
        assert kept_open["project_retired"] is False
        assert db.get_project_authorization("PAUTH-X")["status"] == "completed"

        assert service.auto_retire_completed_projects(project_root=tmp_path) == []
        status = service.member_completion_status("PROJECT-X")
        assert status["keep_open_elected"] is True
        assert "keep_open_election" in status["exclusion_reasons"]
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


def test_scanner_member_completion_view_matches_lifecycle_predicate(tmp_path: Path) -> None:
    scanner = _load_module(SCANNER_PATH, "project_verified_completion_scanner_auto_retire_test")
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "wont_fix"})
    try:
        service_status = ProjectLifecycleService(db).member_completion_status("PROJECT-X")
    finally:
        db.close()

    scanner_status = scanner.member_completion_scan(tmp_path)[0].as_dict()
    assert scanner.member_completion_ready(tmp_path)[0].project_id == "PROJECT-X"
    for key in (
        "active_member_work_item_ids",
        "terminal_work_item_ids",
        "nonterminal_work_item_ids",
        "keep_open_elected",
        "completion_ready",
        "exclusion_reasons",
    ):
        assert scanner_status[key] == service_status[key]


def test_verify_helper_twins_are_byte_identical() -> None:
    assert CLAUDE_HELPER_PATH.read_bytes() == CODEX_HELPER_PATH.read_bytes()


def test_verify_helper_actuation_wrapper_swallows_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    helper = _load_module(CLAUDE_HELPER_PATH, "claude_write_verdict_auto_retire_test")
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.close()

    def boom(self: ProjectLifecycleService, **_: object) -> list[dict[str, object]]:
        raise RuntimeError("actuation failed")

    monkeypatch.setattr(ProjectLifecycleService, "auto_retire_completed_projects", boom)

    assert helper._auto_retire_completed_projects_after_verified(tmp_path) == ()
    assert "VERIFIED auto-retire skipped: actuation failed" in capsys.readouterr().err
