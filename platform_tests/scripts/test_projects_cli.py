from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.governance.approval_packet import construct_approval_packet


def _write_config(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
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


def _create_project_with_item(
    config_path: Path,
    tmp_path: Path,
    *,
    project_id: str = "PROJECT-RETIRE",
    work_item_id: str = "WI-1001",
) -> None:
    _seed_work_items(tmp_path, work_item_id)
    _invoke_json(
        config_path,
        "projects",
        "create",
        "Retire Item Project",
        "--id",
        project_id,
        "--change-reason",
        "create retire-item test project",
    )
    _invoke_json(
        config_path,
        "projects",
        "add-item",
        project_id,
        work_item_id,
        "--change-reason",
        "link retire-item test work item",
    )


def _write_retire_item_packet(
    tmp_path: Path,
    *,
    project_id: str = "PROJECT-RETIRE",
    work_item_id: str = "WI-1001",
    action: str = "retire",
    status: str = "retired",
    filename: str = "retire-item-approval.json",
    approved_by: str = "owner",
) -> str:
    approvals_dir = tmp_path / ".groundtruth" / "formal-artifact-approvals"
    approvals_dir.mkdir(parents=True, exist_ok=True)
    full_content = f"Owner approves {action} of {work_item_id} in {project_id} with requested status {status}."
    packet = construct_approval_packet(
        artifact_type="deliberation",
        artifact_id=f"DELIB-{project_id}-{work_item_id}-{status}",
        action="approve",
        source_ref="owner-test-approval",
        full_content=full_content,
        approval_mode="approve",
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request=full_content,
        changed_by="owner",
        change_reason="owner approval for retire-item test",
        approved_by=approved_by,
    )
    packet.update(
        {
            "project_id": project_id,
            "work_item_id": work_item_id,
            "lifecycle_action": action,
            "requested_status": status,
        }
    )
    rel_path = f".groundtruth/formal-artifact-approvals/{filename}"
    (tmp_path / rel_path).write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    return rel_path


def _membership_rows(tmp_path: Path, project_id: str = "PROJECT-RETIRE") -> list[tuple[str, str]]:
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        return conn.execute(
            """
            SELECT work_item_id, status
            FROM project_work_item_memberships
            WHERE project_id = ?
            ORDER BY version
            """,
            (project_id,),
        ).fetchall()


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


def test_retire_item_executes_with_exact_matching_approval_packet(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _create_project_with_item(config_path, tmp_path)
    packet_path = _write_retire_item_packet(tmp_path)

    retired = _invoke_json(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        f"owner approved retire-item via {packet_path}",
    )

    assert retired["project_id"] == "PROJECT-RETIRE"
    assert retired["work_item_id"] == "WI-1001"
    assert retired["status"] == "retired"
    assert retired["version"] == 2
    assert _invoke_json(config_path, "projects", "show", "PROJECT-RETIRE")["work_items"] == []
    assert _membership_rows(tmp_path) == [("WI-1001", "active"), ("WI-1001", "retired")]


@pytest.mark.parametrize(
    ("packet_overrides", "expected_fragment"),
    [
        ({"project_id": "PROJECT-OTHER"}, "project_id='PROJECT-RETIRE'"),
        ({"work_item_id": "WI-OTHER"}, "work_item_id='WI-1001'"),
        ({"action": "exclude"}, "lifecycle_action='retire'"),
        ({"status": "excluded"}, "requested_status='retired'"),
    ],
)
def test_retire_item_rejects_mismatched_approval_packet(
    tmp_path: Path,
    packet_overrides: dict[str, str],
    expected_fragment: str,
) -> None:
    config_path = _write_config(tmp_path)
    _create_project_with_item(config_path, tmp_path)
    packet_path = _write_retire_item_packet(tmp_path, filename="mismatch.json", **packet_overrides)

    result = _invoke(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        f"owner approved retire-item via {packet_path}",
    )

    assert result.exit_code != 0
    assert "does not cover this retire-item request" in result.output
    assert expected_fragment in result.output
    assert _membership_rows(tmp_path) == [("WI-1001", "active")]


@pytest.mark.parametrize(
    ("change_reason", "packet_text", "expected_fragment"),
    [
        ("owner approved retire-item without packet", None, "No .groundtruth/formal-artifact-approvals"),
        (
            "owner approved retire-item via .groundtruth/formal-artifact-approvals/malformed.json",
            "{",
            "not readable JSON",
        ),
        (
            "owner approved retire-item via .groundtruth/formal-artifact-approvals/schema-invalid.json",
            "{}",
            "fails schema validation",
        ),
        (
            "owner approved retire-item via .groundtruth/formal-artifact-approvals/../../../outside.json",
            None,
            "outside the project root",
        ),
    ],
)
def test_retire_item_refuses_missing_invalid_or_out_of_root_packet(
    tmp_path: Path,
    change_reason: str,
    packet_text: str | None,
    expected_fragment: str,
) -> None:
    config_path = _write_config(tmp_path)
    _create_project_with_item(config_path, tmp_path)
    if packet_text is not None:
        packet_path = tmp_path / ".groundtruth" / "formal-artifact-approvals" / change_reason.rsplit("/", 1)[-1]
        packet_path.parent.mkdir(parents=True, exist_ok=True)
        packet_path.write_text(packet_text, encoding="utf-8")

    result = _invoke(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        change_reason,
    )

    assert result.exit_code != 0
    assert expected_fragment in result.output
    assert _membership_rows(tmp_path) == [("WI-1001", "active")]


def test_retire_item_idempotent_and_distinct_from_removed(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _create_project_with_item(config_path, tmp_path)
    packet_path = _write_retire_item_packet(tmp_path)

    _invoke_json(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        f"owner approved retire-item via {packet_path}",
    )
    duplicate = _invoke(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        f"owner approved retire-item via {packet_path}",
    )
    assert duplicate.exit_code != 0
    assert "No active membership to retire" in duplicate.output
    assert _membership_rows(tmp_path) == [("WI-1001", "active"), ("WI-1001", "retired")]

    for status in ("", "active", "removed"):
        config_path = _write_config(tmp_path / status.replace(" ", "_") if status else tmp_path / "empty-status")
        status_root = config_path.parent
        _create_project_with_item(config_path, status_root)
        packet_path = _write_retire_item_packet(status_root, status=status or "retired")
        result = _invoke(
            config_path,
            "projects",
            "retire-item",
            "PROJECT-RETIRE",
            "WI-1001",
            "--status",
            status,
            "--change-reason",
            f"owner approved retire-item via {packet_path}",
        )
        assert result.exit_code != 0
        assert "distinct from 'removed'" in result.output
        assert _membership_rows(status_root) == [("WI-1001", "active")]


def test_retire_item_change_reason_carries_owner_decision_reference(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _create_project_with_item(config_path, tmp_path)
    packet_path = _write_retire_item_packet(tmp_path)
    change_reason = f"DELIB-OWNER-RETIRE-ITEM via {packet_path}"

    _invoke_json(
        config_path,
        "projects",
        "retire-item",
        "PROJECT-RETIRE",
        "WI-1001",
        "--change-reason",
        change_reason,
    )

    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        stored_reason = conn.execute(
            """
            SELECT change_reason
            FROM project_work_item_memberships
            WHERE project_id = 'PROJECT-RETIRE'
            ORDER BY version DESC
            LIMIT 1
            """
        ).fetchone()[0]
    assert stored_reason == change_reason


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
