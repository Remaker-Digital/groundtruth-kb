"""Tests for first-class project artifacts over canonical work_items."""

from __future__ import annotations

import json

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def _insert_work_item(db: KnowledgeDB, item_id: str, **fields: object) -> dict[str, object] | None:
    defaults = {
        "title": f"Work item {item_id}",
        "origin": "new",
        "component": "backlog",
        "resolution_status": "open",
        "changed_by": "test",
        "change_reason": "create test work item",
    }
    defaults.update(fields)
    return db.insert_work_item(id=item_id, **defaults)


def test_project_schema_preserves_work_item_authority(db: KnowledgeDB) -> None:
    conn = db._get_conn()
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    views = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'view'")}

    assert {
        "projects",
        "project_work_item_memberships",
        "project_dependencies",
        "project_artifact_links",
    } <= tables
    assert {
        "current_projects",
        "current_project_work_item_memberships",
        "current_project_dependencies",
        "current_project_artifact_links",
        "current_work_items",
    } <= views
    assert "work_items" in tables
    assert "backlog_items" not in tables
    assert "backlog_entries" not in tables
    assert "subjects" not in tables


def test_work_item_can_belong_to_multiple_projects_without_duplication(db: KnowledgeDB) -> None:
    _insert_work_item(db, "WI-MULTI", title="Shared implementation")
    db.insert_project("Project Alpha", "test", "create", id="PROJECT-ALPHA", rank=1)
    db.insert_project("Project Beta", "test", "create", id="PROJECT-BETA", rank=2)

    db.link_project_work_item("PROJECT-ALPHA", "WI-MULTI", "test", "link")
    db.link_project_work_item("PROJECT-BETA", "WI-MULTI", "test", "link")

    alpha_items = db.list_project_work_items("PROJECT-ALPHA")
    beta_items = db.list_project_work_items("PROJECT-BETA")
    work_items = db.list_work_items()

    assert [item["work_item_id"] for item in alpha_items] == ["WI-MULTI"]
    assert [item["work_item_id"] for item in beta_items] == ["WI-MULTI"]
    assert [item["id"] for item in work_items] == ["WI-MULTI"]


def test_project_dependencies_are_queryable_independently(db: KnowledgeDB) -> None:
    _insert_work_item(db, "WI-BLOCKER", title="Shared blocker")
    db.insert_project("Foundation", "test", "create", id="PROJECT-FOUNDATION")
    db.insert_project("Release", "test", "create", id="PROJECT-RELEASE")

    dependency = db.add_project_dependency(
        "PROJECT-RELEASE",
        "PROJECT-FOUNDATION",
        "test",
        "record dependency",
        rationale="Release needs foundation complete first.",
        related_work_item_id="WI-BLOCKER",
    )

    dependencies = db.list_project_dependencies("PROJECT-RELEASE")
    assert dependency is not None
    assert dependency["from_project_id"] == "PROJECT-RELEASE"
    assert dependency["to_project_id"] == "PROJECT-FOUNDATION"
    assert dependencies[0]["related_work_item_id"] == "WI-BLOCKER"


def test_project_artifact_links_cover_bridge_deliberation_and_spec(db: KnowledgeDB) -> None:
    db.insert_project("Evidence Project", "test", "create", id="PROJECT-EVIDENCE")

    db.add_project_artifact_link("PROJECT-EVIDENCE", "bridge", "gtkb-first-class-project-artifacts", "test", "link")
    db.add_project_artifact_link("PROJECT-EVIDENCE", "deliberation", "DELIB-0838", "test", "link")
    db.add_project_artifact_link("PROJECT-EVIDENCE", "spec", "GOV-FILE-BRIDGE-AUTHORITY-001", "test", "link")

    links = db.list_project_artifact_links("PROJECT-EVIDENCE")
    assert {(link["artifact_type"], link["artifact_ref"]) for link in links} == {
        ("bridge", "gtkb-first-class-project-artifacts"),
        ("deliberation", "DELIB-0838"),
        ("spec", "GOV-FILE-BRIDGE-AUTHORITY-001"),
    }


def test_compatibility_backfill_maps_project_strings_to_project_memberships(tmp_path) -> None:
    db_path = tmp_path / "project-backfill.db"
    db = KnowledgeDB(db_path=db_path)
    _insert_work_item(
        db,
        "WI-BACKFILL",
        title="Backfilled item",
        project_name="Platform Upgrade",
        subproject_name="Bridge Automation",
        implementation_order=7,
    )
    db.close()

    reopened = KnowledgeDB(db_path=db_path)
    try:
        root_project = reopened.get_project("PROJECT-PLATFORM-UPGRADE")
        subproject = reopened.get_project("PROJECT-PLATFORM-UPGRADE-BRIDGE-AUTOMATION")
        root_items = reopened.list_project_work_items("PROJECT-PLATFORM-UPGRADE")
        subproject_items = reopened.list_project_work_items("PROJECT-PLATFORM-UPGRADE-BRIDGE-AUTOMATION")
    finally:
        reopened.close()

    assert root_project is not None
    assert root_project["source_project_name"] == "Platform Upgrade"
    assert subproject is not None
    assert subproject["parent_project_id"] == "PROJECT-PLATFORM-UPGRADE"
    assert [item["work_item_id"] for item in root_items] == ["WI-BACKFILL"]
    assert [item["work_item_id"] for item in subproject_items] == ["WI-BACKFILL"]


def test_project_summary_counts_project_layer(db: KnowledgeDB) -> None:
    db.insert_project("Summary Project", "test", "create", id="PROJECT-SUMMARY")
    summary = db.get_summary()

    assert summary["project_total"] == 1
    assert summary["project_counts"] == {"active": 1}
    assert summary["project_membership_count"] == 0


def test_projects_cli_show_reports_members_from_current_work_items(project_dir, runner: CliRunner) -> None:
    config_flag = ["--config", str(project_dir / "groundtruth.toml")]
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        _insert_work_item(db, "WI-CLI", title="CLI visible item")
        db.insert_project("CLI Project", "test", "create", id="PROJECT-CLI")
        db.link_project_work_item("PROJECT-CLI", "WI-CLI", "test", "link")
    finally:
        db.close()

    result = runner.invoke(main, [*config_flag, "projects", "show", "PROJECT-CLI", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project"]["id"] == "PROJECT-CLI"
    assert payload["work_items"][0]["work_item_id"] == "WI-CLI"
    assert payload["work_items"][0]["work_item_title"] == "CLI visible item"
