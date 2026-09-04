# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the project-authorization record and its CLI are absent.

This file was the primary suite for the authorization artifact: creation,
amendment, revocation, completion, scope evaluation, and the five ``gt
projects`` subcommands that drove them. The record is gone and authorization is
now a field on the project row, so the file asserts the absence of every
surface it used to exercise, plus the presence of the replacement.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present on the same object.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.cli import projects_cmd
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService

REMOVED_DB_WRITERS = (
    "insert_project_authorization",
    "update_project_authorization",
    "get_project_authorization",
    "list_project_authorizations",
)

REMOVED_SERVICE_METHODS = (
    "authorize_project",
    "get_project_authorization",
    "list_project_authorizations",
    "revoke_project_authorization",
    "complete_project_authorization",
    "amend_project_authorization",
    "update_project_authorization",
    "_append_reauthorization_for_membership_event",
)

REMOVED_SUBCOMMANDS = (
    "authorize",
    "authorizations",
    "show-authorization",
    "revoke-authorization",
    "complete-authorization",
)

#: The two values the surviving project-row field accepts.
VALID_AUTHORIZATION_VALUES = {"authorized", "not authorized"}


def test_control_surfaces_are_present() -> None:
    """Non-vacuity guard for every absence assertion in this module."""
    assert hasattr(KnowledgeDB, "insert_project")
    assert hasattr(ProjectLifecycleService, "update_project")
    assert "show" in projects_cmd.commands
    assert issubclass(ProjectLifecycleError, Exception)


def test_knowledge_db_writers_are_absent() -> None:
    """The four database accessors for the retired record are gone."""
    assert hasattr(KnowledgeDB, "insert_project"), "control method missing"
    for name in REMOVED_DB_WRITERS:
        assert not hasattr(KnowledgeDB, name), f"KnowledgeDB should no longer expose {name}"


def test_lifecycle_service_methods_are_absent() -> None:
    """The service layer exposes no authorization lifecycle operation."""
    assert hasattr(ProjectLifecycleService, "update_project"), "control method missing"
    for name in REMOVED_SERVICE_METHODS:
        assert not hasattr(ProjectLifecycleService, name), f"ProjectLifecycleService should no longer expose {name}"


def test_cli_subcommands_are_absent() -> None:
    """The five owner-facing authorization subcommands are unregistered."""
    assert "show" in projects_cmd.commands, "control subcommand missing"
    for name in REMOVED_SUBCOMMANDS:
        assert name not in projects_cmd.commands, f"gt projects {name} should have been removed"


def test_authorization_is_a_project_row_field(tmp_path: Path) -> None:
    """The replacement surface exists and carries the canonical vocabulary.

    This is the positive half. Asserting only absence would leave the suite
    unable to distinguish a completed migration from a deletion that removed
    the capability without replacing it.
    """
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project("Fixture", "test", "fixture", id="PROJECT-FIXTURE")
    finally:
        db.close()

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)")}
        row = connection.execute(
            "SELECT authorization FROM current_projects WHERE id = ?", ("PROJECT-FIXTURE",)
        ).fetchone()
        names = {entry[0] for entry in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert "authorization" in columns
    assert row["authorization"] in VALID_AUTHORIZATION_VALUES
    assert not [name for name in names if "project_authorization" in name]
