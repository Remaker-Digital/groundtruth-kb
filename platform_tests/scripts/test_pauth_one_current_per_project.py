# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the one-current-authorization-per-project collapse is retired.

This file exercised ``groundtruth_kb.project.authorization_collapse`` to
supersede surplus per-item authorizations into one row per project. With the
relation removed there is nothing left to collapse: authorization is a single
field on the project row, so the invariant the collapse enforced is now
structural rather than something a sweep has to establish.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present.
"""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService


def test_control_lifecycle_surface_is_present() -> None:
    """Non-vacuity guard: the surviving lifecycle surface imported."""
    assert hasattr(ProjectLifecycleService, "update_project")


def test_collapse_module_is_absent() -> None:
    """The collapse module and its only consumer were removed together.

    Removing the module while its single consumer survived would have turned a
    call-time failure into an import-time one, which fails at collection and
    takes down unrelated tests in the same tree. Both went in one step.
    """
    assert importlib.util.find_spec("groundtruth_kb.project.lifecycle") is not None, "control module missing"
    assert importlib.util.find_spec("groundtruth_kb.project.authorization_collapse") is None, (
        "groundtruth_kb.project.authorization_collapse should have been removed"
    )


def test_one_authorization_per_project_is_structural(tmp_path: Path) -> None:
    """A project row holds one authorization value, so no collapse is possible."""
    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project("Fixture", "test", "fixture", id="PROJECT-FIXTURE")
    finally:
        db.close()

    connection = sqlite3.connect(db_path)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)")}
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert "authorization" in columns, "control column missing; the surviving field is the subject here"
    assert not [name for name in names if "project_authorization" in name]
