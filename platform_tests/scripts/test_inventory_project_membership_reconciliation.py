from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "inventory_project_membership_reconciliation.py"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module():
    spec = importlib.util.spec_from_file_location("inventory_project_membership_reconciliation_for_test", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _create_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE current_work_items (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                origin TEXT,
                component TEXT,
                source_spec_id TEXT,
                source_test_id TEXT,
                failure_description TEXT,
                resolution_status TEXT,
                priority TEXT,
                stage TEXT,
                approval_state TEXT,
                project_name TEXT,
                subproject_name TEXT,
                implementation_order INTEGER,
                status_detail TEXT,
                source_owner_directive TEXT,
                source_deliberation_query TEXT,
                related_deliberation_ids TEXT,
                related_spec_ids_at_creation TEXT,
                related_bridge_threads TEXT,
                depends_on_work_items TEXT,
                blocks_work_items TEXT,
                acceptance_summary TEXT,
                regression_visibility TEXT,
                completion_evidence TEXT,
                supersedes TEXT,
                superseded_by TEXT
            );
            CREATE TABLE current_projects (
                id TEXT PRIMARY KEY,
                name TEXT,
                status TEXT,
                rank INTEGER,
                parent_project_id TEXT,
                source_project_name TEXT,
                source_subproject_name TEXT
            );
            CREATE TABLE current_project_work_item_memberships (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                work_item_id TEXT,
                membership_role TEXT,
                membership_order INTEGER,
                status TEXT,
                source TEXT
            );
            CREATE TABLE current_project_dependencies (
                id TEXT PRIMARY KEY,
                from_project_id TEXT,
                to_project_id TEXT,
                dependency_type TEXT,
                rationale TEXT,
                blocking_status TEXT,
                related_work_item_id TEXT,
                status TEXT
            );
            """
        )
        for project in [
            ("PROJECT-ACTIVE", "Active Project", "active", None, "Active Project", None),
            ("PROJECT-EXACT", "Exact Project", "active", None, "Exact Project", None),
            ("PROJECT-WEAK-MATCH", "Weak Matching Project", "active", None, None, None),
            ("PROJECT-BLOCKED", "Blocked Project", "active", None, "Blocked Project", None),
            ("PROJECT-BLOCKER", "Blocking Project", "active", None, "Blocking Project", None),
            ("PROJECT-RETIRED", "Retired Project", "retired", None, "Retired Project", None),
        ]:
            conn.execute(
                """INSERT INTO current_projects
                   (id, name, status, parent_project_id, source_project_name, source_subproject_name)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                project,
            )
        rows = [
            ("WI-ACTIVE", "Already linked work", "open", "P2", "ops", None, None, None, None, None),
            ("WI-DANGLING", "Dangling member work", "open", "P2", "ops", None, None, None, None, None),
            ("WI-EXACT", "Exact project work", "open", "P1", "ops", "Exact Project", None, None, None, None),
            ("WI-WEAK", "Weak Matching Project follow-up", "open", "P2", "ops", None, None, None, None, None),
            ("WI-CLUSTER-1", "Cluster work one", "open", "P3", "ops", "New Cluster", None, None, None, None),
            ("WI-CLUSTER-2", "Cluster work two", "open", "P3", "ops", "New Cluster", None, None, None, None),
            ("WI-SINGLE", "Single project signal", "open", "P3", "ops", "One Off Project", None, None, None, None),
            ("WI-DUPLICATE", "Duplicate obsolete cleanup", "open", "P2", "ops", None, None, None, None, "WI-ACTIVE"),
            ("WI-BLOCKED", "Blocked project work", "open", "P0", "ops", None, None, None, None, None),
            ("WI-MANUAL", "Unclear work item", "open", "P3", "", None, None, None, None, None),
            ("WI-TERMINAL", "Resolved work", "resolved", "P3", "ops", None, None, None, None, None),
        ]
        for row in rows:
            conn.execute(
                """INSERT INTO current_work_items
                   (id, title, resolution_status, priority, component, project_name,
                    subproject_name, related_bridge_threads, supersedes, superseded_by,
                    origin, stage)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'test', 'backlogged')""",
                row,
            )
        for membership in [
            ("PWM-ACTIVE", "PROJECT-ACTIVE", "WI-ACTIVE", "member", 1, "active", "test"),
            ("PWM-DANGLING", "PROJECT-RETIRED", "WI-DANGLING", "member", 1, "active", "test"),
            ("PWM-BLOCKED", "PROJECT-BLOCKED", "WI-BLOCKED", "member", 1, "active", "test"),
        ]:
            conn.execute(
                """INSERT INTO current_project_work_item_memberships
                   (id, project_id, work_item_id, membership_role, membership_order, status, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                membership,
            )
        conn.execute(
            """INSERT INTO current_project_dependencies
               (id, from_project_id, to_project_id, dependency_type, rationale, blocking_status,
                related_work_item_id, status)
               VALUES ('DEP-BLOCKED', 'PROJECT-BLOCKED', 'PROJECT-BLOCKER', 'depends_on',
                       'fixture dependency', 'open', 'WI-BLOCKED', 'active')"""
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def inventory_module():
    return _load_module()


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "groundtruth.db"
    _create_db(path)
    return path


def test_build_inventory_classifies_every_taxonomy_class(inventory_module, db_path: Path) -> None:
    inventory = inventory_module.build_inventory(db_path)
    by_id = {item["id"]: item for item in inventory["items"]}

    assert inventory["summary"]["total_non_terminal_work_items"] == 10
    assert set(inventory["summary"]["classification_counts"]) == set(inventory_module.PRIMARY_CLASSIFICATIONS)
    assert by_id["WI-ACTIVE"]["classification"] == "already_active_project_member"
    assert by_id["WI-ACTIVE"]["active_project_ids"] == ["PROJECT-ACTIVE"]
    assert by_id["WI-ACTIVE"]["candidate_project_ids"] == []
    assert by_id["WI-ACTIVE"]["dependency_project_ids"] == ["PROJECT-ACTIVE"]
    assert by_id["WI-DANGLING"]["classification"] == "dangling_or_terminal_project_membership"
    assert by_id["WI-EXACT"]["classification"] == "existing_project_candidate_exact"
    assert by_id["WI-EXACT"]["candidate_project_ids"] == ["PROJECT-EXACT"]
    assert by_id["WI-WEAK"]["classification"] == "existing_project_candidate_weak"
    assert by_id["WI-WEAK"]["candidate_project_ids"] == ["PROJECT-WEAK-MATCH"]
    assert by_id["WI-CLUSTER-1"]["classification"] == "new_project_candidate_cluster"
    assert by_id["WI-CLUSTER-2"]["classification"] == "new_project_candidate_cluster"
    assert by_id["WI-SINGLE"]["classification"] == "single_wi_project_candidate"
    assert by_id["WI-DUPLICATE"]["classification"] == "obsolete_or_duplicate_candidate"
    assert by_id["WI-BLOCKED"]["classification"] == "dependency_blocked_candidate"
    assert by_id["WI-BLOCKED"]["active_project_ids"] == ["PROJECT-BLOCKED"]
    assert by_id["WI-BLOCKED"]["candidate_project_ids"] == []
    assert by_id["WI-BLOCKED"]["dependency_project_ids"] == ["PROJECT-BLOCKED"]
    assert by_id["WI-BLOCKED"]["dependency_blockers"][0]["to_project_id"] == "PROJECT-BLOCKER"
    assert by_id["WI-MANUAL"]["classification"] == "needs_manual_triage"
    assert "WI-TERMINAL" not in by_id


def test_validate_exactly_once_reports_duplicates_and_omissions(inventory_module) -> None:
    with pytest.raises(inventory_module.InventoryValidationError, match="duplicate=WI-1"):
        inventory_module.validate_exactly_once(["WI-1"], [{"id": "WI-1"}, {"id": "WI-1"}])

    with pytest.raises(inventory_module.InventoryValidationError, match="omitted=WI-2"):
        inventory_module.validate_exactly_once(["WI-1", "WI-2"], [{"id": "WI-1"}])


def test_renderers_include_all_classes_and_source_authority(inventory_module, db_path: Path) -> None:
    inventory = inventory_module.build_inventory(db_path)
    json_text = inventory_module.render_json(inventory)
    markdown = inventory_module.render_markdown(inventory)

    parsed = json.loads(json_text)
    assert parsed["source_authority"]["work_items"] == "fresh read: current_work_items"
    for classification in inventory_module.PRIMARY_CLASSIFICATIONS:
        assert classification in json_text
        assert classification in markdown
    assert "read-only dry-run" in markdown


def test_output_paths_and_cli_stdout(inventory_module, db_path: Path, tmp_path: Path, capsys) -> None:
    json_path = tmp_path / "inventory.json"
    markdown_path = tmp_path / "inventory.md"

    result = inventory_module.main(
        [
            "--db-path",
            str(db_path),
            "--format",
            "markdown",
            "--output-json",
            str(json_path),
            "--output-markdown",
            str(markdown_path),
        ]
    )

    assert result == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["summary"]["total_non_terminal_work_items"] == 10
    assert "# Project Membership Reconciliation Inventory" in markdown_path.read_text(encoding="utf-8")
    assert "Project Membership Reconciliation Inventory" in capsys.readouterr().out


def test_cli_does_not_mutate_database(inventory_module, db_path: Path) -> None:
    before = _file_hash(db_path)

    result = inventory_module.main(["--db-path", str(db_path), "--format", "json"])

    assert result == 0
    assert _file_hash(db_path) == before
