# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-7657: the one-active-version invariant has no relation to hold it.

This file asserted that a project carried exactly one active authorization
version. The relation that carried versions is gone; authorization is now a
field on the project row, which cannot hold two values at once, so the
invariant is structural rather than checked.

Non-vacuity: an absence assertion passes trivially if the symbol name is
misspelled or the import silently failed, so every test below pairs the absent
names with a control that is still present on the same object. If the control
fails, the absence claims are not trusted.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB


def test_project_row_carries_a_single_authorization_value(tmp_path: Path) -> None:
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
        rows = connection.execute(
            "SELECT authorization FROM current_projects WHERE id = ?", ("PROJECT-FIXTURE",)
        ).fetchall()
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    finally:
        connection.close()

    assert "authorization" in columns, "control column missing; the surviving authorization field is the subject here"
    assert len(rows) == 1, "a project row must resolve to exactly one authorization value"
    assert not [name for name in names if "project_authorization" in name]
