# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: current/active authorization resolution has no subject.

This file resolved the current active authorization row for a project and
asserted version-ordering behaviour. Both the ``project_authorizations`` table
and its ``current_project_authorizations`` view are gone, so it now asserts the
relations and their accessors are absent.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present on the same object. If the control
fails, the absence claims are not trusted.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import SCHEMA_VERSION, KnowledgeDB

REMOVED_WRITERS = (
    "insert_project_authorization",
    "update_project_authorization",
    "get_project_authorization",
    "list_project_authorizations",
)


def _fresh(tmp_path: Path) -> Path:
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project("Fixture", "test", "fixture", id="PROJECT-FIXTURE")
    finally:
        db.close()
    return db_path


def test_control_schema_version_is_readable() -> None:
    """Non-vacuity guard: the module imported and exposes a real constant."""
    assert isinstance(SCHEMA_VERSION, int)


def test_authorization_relations_are_absent(tmp_path: Path) -> None:
    connection = sqlite3.connect(_fresh(tmp_path))
    try:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()
    assert "projects" in names, "control relation missing; the fixture database did not build"
    assert "project_authorizations" not in names
    assert "current_project_authorizations" not in names


def test_no_accessor_resolves_a_current_authorization() -> None:
    assert hasattr(KnowledgeDB, "insert_project"), "control method missing"
    for name in REMOVED_WRITERS:
        assert not hasattr(KnowledgeDB, name), f"KnowledgeDB should no longer expose {name}"
