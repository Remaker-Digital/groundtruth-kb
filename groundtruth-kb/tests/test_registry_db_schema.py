"""Current registry declarations need no SQLite projection or permission storage.

GOV-PLATFORM-SOT-REGISTRY-001 and the current registry DCLs put membership in
canonical TOML. Opening a database preserves historical rows and definitions
without extending retired ledgers. Actual quarantine recovery remains separate.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.postgres_kernel import REBUILT_LATER_TABLES, RETIRED_TABLES
from groundtruth_kb.project import sot_registry

RETIRED_REGISTRY_TABLES = (
    "sot_artifacts",
    "sot_artifact_revisions",
    "sot_registry_transaction_journal",
)


def test_fresh_database_has_no_registry_projection_or_permission_ledger(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        names = {row[0] for row in db._get_conn().execute("SELECT name FROM sqlite_master")}
        assert not set(RETIRED_REGISTRY_TABLES) & names
        assert "current_sot_artifacts" not in names
        assert {"specifications", "work_items", "projects"} <= names
    finally:
        db.close()


def test_opening_database_preserves_retired_rows_and_schema_without_upgrades(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as conn:
        for table in RETIRED_REGISTRY_TABLES:
            conn.execute(f"CREATE TABLE {table} (historical_value BLOB)")
            conn.execute(f"INSERT INTO {table} VALUES (?)", (b"historical bytes\x00\xff",))
        before = {row[0]: row[1] for row in conn.execute("SELECT name,sql FROM sqlite_master WHERE type='table'")}
    db = KnowledgeDB(path)
    try:
        db._ensure_schema()
        conn = db._get_conn()
        for table in RETIRED_REGISTRY_TABLES:
            assert conn.execute("SELECT sql FROM sqlite_master WHERE name=?", (table,)).fetchone()[0] == before[table]
            assert [tuple(row) for row in conn.execute(f"SELECT * FROM {table}")] == [(b"historical bytes\x00\xff",)]
    finally:
        db.close()


def test_current_database_schema_initialization_remains_idempotent(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        conn = db._get_conn()
        before = [tuple(row) for row in conn.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name")]
        db._ensure_schema()
        db._ensure_schema()
        after = [tuple(row) for row in conn.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name")]
        assert before == after
    finally:
        db.close()


def test_retired_registry_projection_has_no_refresh_writer_or_rebuild_plan() -> None:
    assert not hasattr(sot_registry, "sync_projection")
    assert not hasattr(sot_registry, "SyncReport")
    assert set(RETIRED_REGISTRY_TABLES) <= RETIRED_TABLES
    assert not set(RETIRED_REGISTRY_TABLES) & REBUILT_LATER_TABLES


def test_quarantine_recovery_storage_is_not_removed_with_registry_permissions(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        columns = {row[1] for row in db._get_conn().execute("PRAGMA table_info(sot_quarantine_receipts)")}
        assert {"receipt_id", "original_relative_path", "payload_path", "content_digest", "restore_pending"} <= columns
    finally:
        db.close()
