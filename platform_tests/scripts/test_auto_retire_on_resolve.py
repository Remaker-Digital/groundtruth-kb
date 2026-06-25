"""Regression tests for WI-4807 automatic project retirement on resolve/update."""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb import cli_backlog_update
from groundtruth_kb.cli_backlog_update import BacklogUpdateRequest, update_backlog_item
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService


def _config(project_root: Path) -> GTConfig:
    return GTConfig(db_path=project_root / "groundtruth.db", project_root=project_root)


def _resolve_request(work_item_id: str) -> BacklogUpdateRequest:
    return BacklogUpdateRequest(
        work_item_id=work_item_id,
        resolution_status="resolved",
        stage="resolved",
        priority=None,
        related_bridge_threads=None,
        status_detail=None,
        owner_approved=False,
        change_reason="resolve member work item",
        dry_run=False,
    )


def _seed_project(project_root: Path, statuses: dict[str, str], *, project_id: str = "PROJECT-X") -> KnowledgeDB:
    db = KnowledgeDB(project_root / "groundtruth.db")
    db.insert_project("Auto Retire Resolve Project", "test", "seed", id=project_id, status="active")
    for work_item_id, status in statuses.items():
        db.insert_work_item(
            work_item_id,
            f"Work item {work_item_id}",
            "improvement",
            "platform",
            status,
            "test",
            "seed",
            stage="created",
        )
        db.link_project_work_item(project_id, work_item_id, "test", "seed")
    return db


def _add_completion_guard(db: KnowledgeDB, *, project_id: str = "PROJECT-X") -> None:
    db.add_project_artifact_link(
        project_id,
        "completion_guard",
        "plan-incomplete-fixture",
        "test",
        "seed plan_incomplete guard",
        relationship="plan_incomplete",
    )


def _write_verified_threads(
    project_root: Path,
    db: KnowledgeDB,
    work_item_ids: list[str],
    *,
    project_id: str = "PROJECT-X",
) -> None:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    for index, work_item_id in enumerate(work_item_ids):
        slug = f"gtkb-auto-retire-resolve-fixture-{index}"
        (bridge / f"{slug}-001.md").write_text(
            f"VERIFIED\n\n# Fixture verdict\n\nWork Item: {work_item_id}\n",
            encoding="utf-8",
        )
        db.add_project_artifact_link(
            project_id,
            "bridge_thread",
            slug,
            "test",
            "seed implements link",
            relationship="implements",
        )


def _seed_keep_open_authorization(db: KnowledgeDB, project_root: Path, *, project_id: str = "PROJECT-X") -> None:
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
        included_work_item_ids=["WI-1", "WI-2"],
        included_spec_ids=["SPEC-SEED"],
    )
    _write_verified_threads(project_root, db, ["WI-1", "WI-2"], project_id=project_id)
    ProjectLifecycleService(db).complete_project_authorization(
        "PAUTH-X",
        project_root=project_root,
        change_reason="complete but keep open",
        retire_project=False,
    )


@pytest.fixture(autouse=True)
def _mock_changed_by(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_backlog_update, "_resolve_changed_by", lambda: "test/prime-builder")


def test_resolve_last_terminal_member_retires_ready_project(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open"})
    try:
        result = update_backlog_item(_config(tmp_path), _resolve_request("WI-2"))

        assert [record["project_id"] for record in result["auto_retired_projects"]] == ["PROJECT-X"]
        assert db.get_project("PROJECT-X")["status"] == "retired"
        assert db.list_project_work_items("PROJECT-X") == []
        assert db.get_work_item("WI-1")["resolution_status"] == "retired"
        assert db.get_work_item("WI-2")["resolution_status"] == "retired"
    finally:
        db.close()


def test_resolve_does_not_retire_when_plan_incomplete(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open"})
    try:
        _add_completion_guard(db)

        result = update_backlog_item(_config(tmp_path), _resolve_request("WI-2"))

        assert result["auto_retired_projects"] == []
        assert db.get_project("PROJECT-X")["status"] == "active"
        status = ProjectLifecycleService(db).member_completion_status("PROJECT-X")
        assert status["completion_guarded"] is True
        assert "plan_incomplete_guard" in status["exclusion_reasons"]
    finally:
        db.close()


def test_resolve_does_not_retire_with_keep_open_election(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open"})
    try:
        _seed_keep_open_authorization(db, tmp_path)

        result = update_backlog_item(_config(tmp_path), _resolve_request("WI-2"))

        assert result["auto_retired_projects"] == []
        assert db.get_project("PROJECT-X")["status"] == "active"
        status = ProjectLifecycleService(db).member_completion_status("PROJECT-X")
        assert status["keep_open_elected"] is True
        assert "keep_open_election" in status["exclusion_reasons"]
    finally:
        db.close()


def test_resolve_does_not_retire_multi_slice_guarded(tmp_path: Path) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open", "WI-3": "in_progress"})
    try:
        result = update_backlog_item(_config(tmp_path), _resolve_request("WI-2"))

        assert result["auto_retired_projects"] == []
        assert db.get_project("PROJECT-X")["status"] == "active"
        status = ProjectLifecycleService(db).member_completion_status("PROJECT-X")
        assert status["nonterminal_work_item_ids"] == ["WI-3"]
        assert "nonterminal_member_work_items" in status["exclusion_reasons"]
    finally:
        db.close()


def test_resolve_succeeds_when_retire_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _seed_project(tmp_path, {"WI-1": "verified", "WI-2": "open"})
    try:

        def boom(self: ProjectLifecycleService, work_item_id: str, **_: object) -> list[dict[str, object]]:
            raise RuntimeError(f"actuation failed for {work_item_id}")

        monkeypatch.setattr(ProjectLifecycleService, "auto_retire_projects_for_work_item", boom)

        result = update_backlog_item(_config(tmp_path), _resolve_request("WI-2"))

        assert result["updated"] is True
        assert result["auto_retired_projects"] == []
        assert db.get_work_item("WI-2")["resolution_status"] == "resolved"
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()
