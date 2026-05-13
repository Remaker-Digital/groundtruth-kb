from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "groundtruth.toml"
    config_path.write_text(
        "\n".join(
            [
                "[groundtruth]",
                f'db_path = "{(tmp_path / "groundtruth.db").as_posix()}"',
                f'project_root = "{tmp_path.as_posix()}"',
                'app_title = "Projects CLI Test"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _seed_work_items(tmp_path: Path, *item_ids: str) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        for item_id in item_ids:
            db.insert_work_item(
                item_id,
                f"{item_id} title",
                "new",
                "platform",
                "open",
                "test",
                "seed test work item",
                stage="backlogged",
                status_detail="ready",
            )
    finally:
        db.close()


def _invoke_json(config_path: Path, *args: str) -> Any:
    result = CliRunner().invoke(cli_main, ["--config", str(config_path), *args, "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def _invoke(config_path: Path, *args: str):
    return CliRunner().invoke(cli_main, ["--config", str(config_path), *args])


def test_projects_lifecycle_cli_preserves_append_only_versions(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_work_items(tmp_path, "WI-0001", "WI-0002")

    created = _invoke_json(
        config_path,
        "projects",
        "create",
        "Alpha Project",
        "--id",
        "PROJECT-ALPHA",
        "--rank",
        "10",
        "--change-reason",
        "create project",
    )
    assert created["id"] == "PROJECT-ALPHA"
    assert created["version"] == 1

    updated = _invoke_json(
        config_path,
        "projects",
        "update",
        "PROJECT-ALPHA",
        "--purpose",
        "Coordinate deterministic project work.",
        "--change-reason",
        "add purpose",
    )
    assert updated["version"] == 2
    assert updated["purpose"] == "Coordinate deterministic project work."

    first_link = _invoke_json(
        config_path,
        "projects",
        "add-item",
        "PROJECT-ALPHA",
        "WI-0001",
        "--order",
        "2",
        "--change-reason",
        "link first item",
    )
    assert first_link["version"] == 1
    assert first_link["membership_order"] == 2

    _invoke_json(
        config_path,
        "projects",
        "add-item",
        "PROJECT-ALPHA",
        "WI-0002",
        "--order",
        "1",
        "--change-reason",
        "link second item",
    )

    shown = _invoke_json(config_path, "projects", "show", "PROJECT-ALPHA")
    assert [item["work_item_id"] for item in shown["work_items"]] == ["WI-0002", "WI-0001"]

    reordered = _invoke_json(
        config_path,
        "projects",
        "reorder",
        "PROJECT-ALPHA",
        "WI-0001",
        "WI-0002",
        "--change-reason",
        "reorder project items",
    )
    assert [(item["work_item_id"], item["membership_order"], item["version"]) for item in reordered] == [
        ("WI-0001", 1, 2),
        ("WI-0002", 2, 2),
    ]

    link = _invoke_json(
        config_path,
        "projects",
        "link-bridge",
        "PROJECT-ALPHA",
        "gtkb-projects-skill-001",
        "--change-reason",
        "link implementation bridge",
    )
    assert link["artifact_type"] == "bridge_thread"
    assert link["artifact_ref"] == "gtkb-projects-skill-001"

    retired = _invoke_json(
        config_path,
        "projects",
        "retire",
        "PROJECT-ALPHA",
        "--completed-at",
        "2026-05-13T00:00:00Z",
        "--change-reason",
        "retire after verification",
    )
    assert retired["status"] == "retired"
    assert retired["version"] == 3

    assert _invoke_json(config_path, "projects", "list") == []
    assert [project["id"] for project in _invoke_json(config_path, "projects", "list", "--all")] == ["PROJECT-ALPHA"]

    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        project_versions = conn.execute("SELECT COUNT(*) FROM projects WHERE id = 'PROJECT-ALPHA'").fetchone()[0]
        membership_versions = conn.execute(
            "SELECT COUNT(*) FROM project_work_item_memberships WHERE project_id = 'PROJECT-ALPHA'"
        ).fetchone()[0]
    assert project_versions == 3
    assert membership_versions == 4


def test_projects_link_bridge_records_artifact_without_editing_bridge_index(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    index_path = bridge_dir / "INDEX.md"
    original_index = "# Bridge Index\n\nDocument: existing\nGO: bridge/existing-002.md\n"
    index_path.write_text(original_index, encoding="utf-8")

    _invoke_json(
        config_path,
        "projects",
        "create",
        "Bridge Linked Project",
        "--id",
        "PROJECT-BRIDGE",
        "--change-reason",
        "create project",
    )
    link = _invoke_json(
        config_path,
        "projects",
        "link-bridge",
        "PROJECT-BRIDGE",
        "gtkb-projects-skill-001",
        "--change-reason",
        "record bridge link",
    )

    assert link["artifact_type"] == "bridge_thread"
    assert index_path.read_text(encoding="utf-8") == original_index


def test_projects_reorder_requires_exact_active_membership_set(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_work_items(tmp_path, "WI-0001", "WI-0002")
    _invoke_json(
        config_path,
        "projects",
        "create",
        "Strict Reorder",
        "--id",
        "PROJECT-STRICT",
        "--change-reason",
        "create project",
    )
    for item_id in ("WI-0001", "WI-0002"):
        _invoke_json(
            config_path,
            "projects",
            "add-item",
            "PROJECT-STRICT",
            item_id,
            "--change-reason",
            f"link {item_id}",
        )

    result = _invoke(
        config_path,
        "projects",
        "reorder",
        "PROJECT-STRICT",
        "WI-0001",
        "--change-reason",
        "incomplete reorder",
    )

    assert result.exit_code != 0
    assert "active membership set exactly" in result.output
