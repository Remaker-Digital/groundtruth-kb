from __future__ import annotations

import sqlite3
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def test_registry_help_does_not_offer_observation_receipts(tmp_path: Path) -> None:
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    result = CliRunner().invoke(main, ["--config", str(config), "registry", "--help"])
    assert result.exit_code == 0, result.output
    assert "observe" not in result.output
    assert not (tmp_path / "groundtruth.db").exists()


def test_new_database_does_not_create_per_tool_permission_storage(tmp_path: Path) -> None:
    path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=path)
    with sqlite3.connect(path) as conn:
        assert (
            conn.execute("SELECT name FROM sqlite_master WHERE name='sot_registry_observation_capabilities'").fetchone()
            is None
        )


def test_schema_setup_preserves_old_observation_history_without_using_it(tmp_path: Path) -> None:
    from groundtruth_kb.project.registry_control_plane import ensure_control_plane_schema

    with sqlite3.connect(tmp_path / "legacy.db") as conn:
        conn.execute("CREATE TABLE sot_registry_observation_capabilities (historical_value TEXT)")
        conn.execute("INSERT INTO sot_registry_observation_capabilities VALUES ('preserve historical bytes')")
        ensure_control_plane_schema(conn)
        assert conn.execute("SELECT * FROM sot_registry_observation_capabilities").fetchall() == [
            ("preserve historical bytes",)
        ]
