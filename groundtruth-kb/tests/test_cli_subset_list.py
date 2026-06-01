"""Tests for subset filters on MemBase-backed list CLIs."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def _config_path(project_dir: Path) -> Path:
    return project_dir / "groundtruth.toml"


def _runner_result(project_dir: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(_config_path(project_dir)), *args])


def _seed_projects(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_project("Alpha", "test", "seed", id="PROJECT-ALPHA", rank=1, purpose="Bridge control")
        db.insert_project("Beta", "test", "seed", id="PROJECT-BETA", rank=2, purpose="Subset target")
        db.insert_project("Gamma", "test", "seed", id="PROJECT-GAMMA", rank=3, purpose="Other")
        db.insert_project("Retired", "test", "seed", id="PROJECT-RETIRED", status="retired", rank=4)
    finally:
        db.close()


def _seed_work_items(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_work_item(
            "WI-OPEN-1",
            "Bridge contention subset target",
            "new",
            "developer_tooling",
            "open",
            "test",
            "seed",
            description="Need compact CLI subset for bridge contention work.",
            priority="P1",
            stage="backlogged",
            project_name="Project Alpha",
            subproject_name="Bridge",
            implementation_order=1,
        )
        db.insert_work_item(
            "WI-OPEN-2",
            "Dashboard subset target",
            "hygiene",
            "dashboard",
            "open",
            "test",
            "seed",
            description="Need compact CLI subset for dashboard work.",
            priority="P2",
            stage="created",
            project_name="Project Beta",
            subproject_name="Discoverability",
            implementation_order=2,
        )
        db.insert_work_item(
            "WI-VERIFIED",
            "Verified terminal item",
            "new",
            "developer_tooling",
            "verified",
            "test",
            "seed",
            description="Terminal item for explicit subset lookup.",
            priority="P3",
            stage="resolved",
            project_name="Project Terminal",
            subproject_name="Archive",
            implementation_order=3,
        )
    finally:
        db.close()


def test_projects_list_limit_returns_existing_order(project_dir: Path) -> None:
    _seed_projects(project_dir)

    result = _runner_result(project_dir, "projects", "list", "--json", "--limit", "2")

    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert [row["id"] for row in rows] == ["PROJECT-ALPHA", "PROJECT-BETA"]


def test_projects_list_explicit_id_can_return_terminal_project(project_dir: Path) -> None:
    _seed_projects(project_dir)

    result = _runner_result(project_dir, "projects", "list", "--json", "--id", "PROJECT-RETIRED")

    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert [row["id"] for row in rows] == ["PROJECT-RETIRED"]
    assert rows[0]["status"] == "retired"


def test_backlog_list_explicit_id_can_return_terminal_work_item(project_dir: Path) -> None:
    _seed_work_items(project_dir)

    result = _runner_result(project_dir, "backlog", "list", "--json", "--id", "WI-VERIFIED")

    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert [row["id"] for row in rows] == ["WI-VERIFIED"]
    assert rows[0]["resolution_status"] == "verified"


def test_backlog_list_metadata_and_text_filters_return_compact_subset(project_dir: Path) -> None:
    _seed_work_items(project_dir)

    result = _runner_result(
        project_dir,
        "backlog",
        "list",
        "--json",
        "--project",
        "Project Alpha",
        "--subproject",
        "Bridge",
        "--priority",
        "P1",
        "--origin",
        "new",
        "--component",
        "developer_tooling",
        "--stage",
        "backlogged",
        "--contains",
        "contention",
    )

    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert [row["id"] for row in rows] == ["WI-OPEN-1"]


def test_backlog_list_repeatable_filters_and_resolution_status_include_terminal(project_dir: Path) -> None:
    _seed_work_items(project_dir)

    result = _runner_result(
        project_dir,
        "backlog",
        "list",
        "--json",
        "--priority",
        "P1",
        "--priority",
        "P3",
        "--resolution-status",
        "open",
        "--resolution-status",
        "verified",
        "--limit",
        "2",
    )

    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert [row["id"] for row in rows] == ["WI-OPEN-1", "WI-VERIFIED"]
