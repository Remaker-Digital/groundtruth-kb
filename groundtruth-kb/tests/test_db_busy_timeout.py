"""Regression coverage for KnowledgeDB SQLite busy-timeout configuration."""

from __future__ import annotations

from groundtruth_kb.db import DEFAULT_SQLITE_BUSY_TIMEOUT_MS, KnowledgeDB


def test_knowledge_db_sets_explicit_busy_timeout(tmp_path) -> None:
    db = KnowledgeDB(db_path=tmp_path / "busy-timeout.db")
    try:
        conn = db._get_conn()
        busy_timeout_ms = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    finally:
        db.close()

    assert busy_timeout_ms == DEFAULT_SQLITE_BUSY_TIMEOUT_MS
    assert foreign_keys == 1
    assert journal_mode.lower() == "wal"
