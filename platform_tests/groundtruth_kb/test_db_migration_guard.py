"""Specification-derived tests for KnowledgeDB connect-time schema migration guard (WI-6609)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import SCHEMA_VERSION, KnowledgeDB


def test_knowledgedb_initialization_stamps_user_version(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _ = KnowledgeDB(db_path=db_file)
    conn = sqlite3.connect(str(db_file))
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    assert version == SCHEMA_VERSION


def test_knowledgedb_reconnect_performs_no_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    # First init stamps schema version
    _ = KnowledgeDB(db_path=db_file)

    # Re-connect
    db2 = KnowledgeDB(db_path=db_file)
    conn = db2._get_conn()
    assert KnowledgeDB._schema_version(conn) == SCHEMA_VERSION


def test_knowledgedb_read_connection_concurrency(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    # First initialization
    _ = KnowledgeDB(db_path=db_file)

    # Concurrent read connection
    db2 = KnowledgeDB(db_path=db_file)
    specs = db2.list_specs()
    assert isinstance(specs, list)


def test_knowledgedb_user_version_guard_prevents_redundant_writes(tmp_path: Path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    _ = KnowledgeDB(db_path=db_file)

    upgrade_called = False

    def fake_upgrade(self, conn):
        nonlocal upgrade_called
        upgrade_called = True

    monkeypatch.setattr(KnowledgeDB, "_upgrade_schema", fake_upgrade)

    _ = KnowledgeDB(db_path=db_file)
    assert not upgrade_called
