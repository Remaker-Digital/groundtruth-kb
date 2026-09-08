"""Programs plan; projects authorize and complete; work items have one parent."""

from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService
from groundtruth_kb.project.membership_resolver import MembershipResolutionError, resolve_execution_membership


@pytest.fixture(autouse=True)
def isolated_cli_database(tmp_path: Path, monkeypatch):
    # Repository-level pytest may put tmp_path below a real groundtruth.toml.
    # Override both paths so parent-directory discovery cannot select live SoT.
    monkeypatch.setenv("GT_DB_PATH", str(tmp_path / "groundtruth.db"))
    monkeypatch.setenv("GT_PROJECT_ROOT", str(tmp_path))


@pytest.fixture
def work_db(tmp_path: Path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    yield db
    db.close()


def project(db, name="Alpha", **values):
    return ProjectLifecycleService(db).create_project(name, changed_by="test", change_reason="fixture", **values)


def item(db, identifier="WI-ONE"):
    db.insert_work_item(identifier, "One change", "new", "platform", "open", "test", "fixture")
    return identifier


def history_size(db):
    return db._get_conn().execute("SELECT COUNT(*) FROM project_work_item_memberships").fetchone()[0]


def test_authorization_survives_updates_and_is_written(work_db):
    service = ProjectLifecycleService(work_db)
    original = project(work_db)
    assert original["authorization"] == "authorized"
    changed = service.update_project(original["id"], authorization="not authorized", change_reason="owner direction")
    assert changed["authorization"] == "not authorized"
    renamed = service.update_project(original["id"], name="New name", change_reason="rename")
    assert renamed["authorization"] == "not authorized"
    rows = work_db._get_conn().execute("SELECT authorization FROM projects ORDER BY version").fetchall()
    assert [row[0] for row in rows] == ["authorized", "not authorized", "not authorized"]


def test_standing_intake_defaults_to_not_authorized_and_cannot_be_authorized(work_db):
    intake = project(work_db, "Intake", project_id="PROJECT-GTKB-NEW-WORK-INTAKE")
    assert intake["authorization"] == "not authorized"
    with pytest.raises(ValueError, match="standing intake"):
        ProjectLifecycleService(work_db).update_project(
            intake["id"], authorization="authorized", change_reason="invalid"
        )
    assert work_db.get_project(intake["id"])["version"] == 1


def test_program_has_no_authorization_and_exposes_its_projects(work_db):
    program = project(work_db, "Repair", kind="program")
    child = project(work_db, parent_project_id=program["id"])
    assert program["id"] == "PROGRAM-REPAIR"
    assert program["authorization"] is None
    view = ProjectLifecycleService(work_db).show_project(program["id"])
    assert [row["id"] for row in view["projects"]] == [child["id"]]
    assert view["work_items"] == []
    with pytest.raises(ValueError, match="Programs have no authorization"):
        project(work_db, "Invalid", kind="program", authorization="authorized")


def test_only_programs_can_contain_projects(work_db):
    parent = project(work_db)
    with pytest.raises(ValueError, match="parent must be an existing program"):
        project(work_db, "Child", parent_project_id=parent["id"])
    program = project(work_db, "Program", kind="program")
    project(work_db, "Child", parent_project_id=program["id"])
    with pytest.raises(ValueError, match="cannot contain other projects"):
        ProjectLifecycleService(work_db).update_project(program["id"], kind="project", change_reason="invalid")


def test_project_with_work_items_cannot_become_a_program(work_db):
    parent = project(work_db)
    work_db.link_project_work_item(parent["id"], item(work_db), "test", "fixture")
    with pytest.raises(ValueError, match="Move direct work-item"):
        ProjectLifecycleService(work_db).update_project(parent["id"], kind="program", change_reason="invalid")
    assert work_db.get_project(parent["id"])["kind"] == "project"


def test_program_cannot_accept_a_work_item(work_db):
    program = project(work_db, kind="program")
    with pytest.raises(ValueError, match="cannot contain work items"):
        work_db.link_project_work_item(program["id"], item(work_db), "test", "invalid")
    assert history_size(work_db) == 0


def test_new_membership_has_no_authority_role(work_db):
    parent = project(work_db)
    with pytest.raises(ValueError, match="no authority or planning role"):
        work_db.link_project_work_item(
            parent["id"], item(work_db), "test", "invalid", membership_role="execution_authority"
        )
    assert history_size(work_db) == 0


def test_a_second_membership_is_rejected_without_mutation(work_db):
    first, second = project(work_db), project(work_db, "Beta")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    with pytest.raises(ValueError, match="already belongs"):
        work_db.link_project_work_item(second["id"], wi, "test", "invalid")
    assert history_size(work_db) == 1
    assert resolve_execution_membership(work_db, wi).project_id == first["id"]


def test_move_changes_one_parent_and_preserves_both_authorization_values(work_db):
    first = project(work_db, authorization="not authorized")
    second = project(work_db, "Beta")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    result = ProjectLifecycleService(work_db).move_project_item(wi, first["id"], second["id"], change_reason="move")
    assert result["project_id"] == second["id"]
    assert work_db.get_project(first["id"])["authorization"] == "not authorized"
    assert work_db.get_project(second["id"])["authorization"] == "authorized"
    assert history_size(work_db) == 3
    rows = (
        work_db._get_conn()
        .execute("SELECT project_id,status FROM current_project_work_item_memberships ORDER BY project_id")
        .fetchall()
    )
    assert [tuple(row) for row in rows] == [(first["id"], "removed"), (second["id"], "active")]


@pytest.mark.parametrize("destination", ["PROJECT-MISSING", "PROGRAM-INVALID"])
def test_failed_move_restores_original_membership(work_db, destination):
    first = project(work_db)
    project(work_db, "Invalid", kind="program")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    with pytest.raises(ValueError):
        ProjectLifecycleService(work_db).move_project_item(wi, first["id"], destination, change_reason="invalid")
    assert history_size(work_db) == 1
    assert resolve_execution_membership(work_db, wi).project_id == first["id"]


def test_move_rejects_a_stale_source(work_db):
    first, second = project(work_db), project(work_db, "Beta")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    with pytest.raises(ProjectLifecycleError, match="belongs to"):
        ProjectLifecycleService(work_db).move_project_item(wi, second["id"], first["id"], change_reason="stale")
    assert history_size(work_db) == 1


def test_remove_cannot_orphan_an_item(work_db):
    parent = project(work_db)
    wi = item(work_db)
    work_db.link_project_work_item(parent["id"], wi, "test", "fixture")
    with pytest.raises(ProjectLifecycleError, match="retain one parent"):
        ProjectLifecycleService(work_db).remove_project_item(parent["id"], wi, change_reason="invalid")
    assert history_size(work_db) == 1


def test_legacy_role_does_not_hide_a_second_parent(work_db):
    first, second = project(work_db), project(work_db, "Beta")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    conn = work_db._get_conn()
    conn.execute("UPDATE project_work_item_memberships SET membership_role='execution_authority'")
    conn.execute(
        "INSERT INTO project_work_item_memberships "
        "(id,version,project_id,work_item_id,membership_role,status,changed_by,changed_at,change_reason) "
        "VALUES ('PWM-OLD',1,?,?,'planning','active','test','2026-01-01','legacy fixture')",
        (second["id"], wi),
    )
    conn.commit()
    with pytest.raises(MembershipResolutionError) as exc:
        resolve_execution_membership(work_db, wi)
    assert exc.value.code == "project_membership_ambiguous"


def test_reopening_does_not_infer_membership_from_text_labels(tmp_path):
    path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(path)
    db.insert_work_item(
        "WI-OLD", "Old", "new", "platform", "open", "test", "fixture", project_name="Inferred", subproject_name="Nested"
    )
    db.close()
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA user_version=0")
    db = KnowledgeDB(path)
    try:
        assert db.list_projects(include_terminal=True) == []
        assert history_size(db) == 0
        assert db.get_work_item("WI-OLD")["project_name"] == "Inferred"
    finally:
        db.close()


def test_concurrent_links_cannot_create_two_parents(work_db, tmp_path):
    first, second = project(work_db), project(work_db, "Beta")
    wi = item(work_db)
    barrier = Barrier(2)

    def attempt(parent):
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        try:
            barrier.wait(timeout=10)
            db.link_project_work_item(parent, wi, "test", "concurrent link")
            return "linked"
        except ValueError:
            return "rejected"
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, [first["id"], second["id"]]))
    assert sorted(results) == ["linked", "rejected"]
    assert history_size(work_db) == 1


def test_cli_program_and_authorization_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    def invoke(*args):
        result = runner.invoke(main, ["projects", *args, "--json"])
        assert result.exit_code == 0, (result.output, result.exception)
        return json.loads(result.output)

    program = invoke("create", "Repair", "--kind", "program", "--change-reason", "test")
    execution = invoke("create", "Execution", "--parent-project-id", program["id"], "--change-reason", "test")
    updated = invoke("update", execution["id"], "--authorization", "not authorized", "--change-reason", "test")
    assert updated["authorization"] == "not authorized"
    assert invoke("show", program["id"])["projects"][0]["id"] == execution["id"]


def test_old_project_schema_migrates_without_rewriting_history(tmp_path):
    path = tmp_path / "groundtruth.db"
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            CREATE TABLE projects (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL,
                version INTEGER NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active',
                rank INTEGER, parent_project_id TEXT, purpose TEXT, target_outcome TEXT,
                scope_note TEXT, start_date TEXT, target_date TEXT, completed_at TEXT,
                notes TEXT, source_project_name TEXT, source_subproject_name TEXT,
                authorization TEXT NOT NULL DEFAULT 'authorized',
                activation_status TEXT, changed_by TEXT NOT NULL, changed_at TEXT NOT NULL,
                change_reason TEXT NOT NULL, UNIQUE(id,version)
            );
            INSERT INTO projects(id,version,name,authorization,activation_status,changed_by,changed_at,change_reason)
                VALUES ('PROJECT-OLD',1,'Before','authorized','old evidence','test','2026-01-01','first'),
                       ('PROJECT-OLD',2,'After','not authorized','other evidence','test','2026-02-01','second');
            CREATE VIEW saved_project_names AS SELECT id,name FROM projects;
        """)
        conn.row_factory = sqlite3.Row
        before = [dict(row) for row in conn.execute("SELECT * FROM projects ORDER BY rowid")]
    db = KnowledgeDB(path)
    try:
        after = [dict(row) for row in db._get_conn().execute("SELECT * FROM projects ORDER BY rowid")]
        assert [{key: row[key] for key in before[0]} for row in after] == before
        assert {row["kind"] for row in after} == {"project"}
        assert db.get_project("PROJECT-OLD")["authorization"] == "not authorized"
        assert db._get_conn().execute("SELECT COUNT(*) FROM saved_project_names").fetchone()[0] == 2
        assert db._get_conn().execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert project(db, "Plan", kind="program")["authorization"] is None
    finally:
        db.close()


def test_program_conversion_and_membership_link_serialize(work_db, tmp_path):
    parent = project(work_db)
    wi = item(work_db)
    barrier = Barrier(2)

    def operation(convert):
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        try:
            barrier.wait(timeout=10)
            if convert:
                db.insert_project("Alpha", "test", "convert", id=parent["id"], kind="program")
            else:
                db.link_project_work_item(parent["id"], wi, "test", "link")
            return "applied"
        except ValueError:
            return "rejected"
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(operation, [True, False]))
    assert sorted(results) == ["applied", "rejected"]
    current = work_db.get_project(parent["id"])
    memberships = work_db.list_project_work_items(parent["id"])
    assert (current["kind"] == "project") == bool(memberships)


def test_concurrent_legacy_removals_retain_one_parent(work_db, tmp_path):
    first, second = project(work_db), project(work_db, "Beta")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    conn = work_db._get_conn()
    conn.execute(
        "INSERT INTO project_work_item_memberships "
        "(id,version,project_id,work_item_id,membership_role,status,changed_by,changed_at,change_reason) "
        "VALUES ('PWM-LEGACY',1,?,?,'planning','active','test','2026-01-01','legacy fixture')",
        (second["id"], wi),
    )
    conn.commit()
    barrier = Barrier(2)

    def remove(parent):
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        try:
            barrier.wait(timeout=10)
            ProjectLifecycleService(db).remove_project_item(parent, wi, change_reason="reconcile")
            return "removed"
        except ProjectLifecycleError:
            return "rejected"
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(remove, [first["id"], second["id"]]))
    assert sorted(results) == ["rejected", "removed"]
    assert resolve_execution_membership(work_db, wi).project_id in {first["id"], second["id"]}


def test_cli_move_and_kind_filter(work_db, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    program = project(work_db, "Repair", kind="program")
    first, second = project(work_db), project(work_db, "Beta", authorization="not authorized")
    wi = item(work_db)
    work_db.link_project_work_item(first["id"], wi, "test", "fixture")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "projects",
            "move-item",
            wi,
            "--from-project",
            first["id"],
            "--to-project",
            second["id"],
            "--change-reason",
            "move",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["project_id"] == second["id"]
    result = runner.invoke(main, ["projects", "list", "--kind", "program", "--json"])
    assert result.exit_code == 0, result.output
    assert [row["id"] for row in json.loads(result.output)] == [program["id"]]
    assert work_db.get_project(second["id"])["authorization"] == "not authorized"
