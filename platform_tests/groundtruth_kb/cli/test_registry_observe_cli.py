from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB


def test_new_database_does_not_create_per_tool_permission_storage(tmp_path: Path) -> None:
    path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=path)
    with sqlite3.connect(path) as conn:
        assert (
            conn.execute("SELECT name FROM sqlite_master WHERE name='sot_registry_observation_capabilities'").fetchone()
            is None
        )
