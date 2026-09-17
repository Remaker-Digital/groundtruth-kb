"""Regression coverage for KnowledgeDB SQLite busy-timeout configuration.

Also covers WI-6609: connect-time schema migration must be guarded behind
``PRAGMA user_version`` so an up-to-date database takes no write lock on
construction.
"""

from __future__ import annotations

import json
import sqlite3

from groundtruth_kb.db import (
    DEFAULT_SQLITE_BUSY_TIMEOUT_MS,
    SCHEMA_VERSION,
    KnowledgeDB,
)


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


# --------------------------------------------------------------------------
# WI-6609: connect-time migration guard
# --------------------------------------------------------------------------


def test_schema_version_is_stamped_on_creation(tmp_path) -> None:
    db = KnowledgeDB(db_path=tmp_path / "stamp.db")
    try:
        assert db._schema_version(db._get_conn()) == SCHEMA_VERSION
    finally:
        db.close()


def test_construction_takes_no_write_lock_when_current(tmp_path) -> None:
    """The reported failure: a second connection got ``database is locked``.

    An external writer holds the write lock. Constructing ``KnowledgeDB``
    against an already-stamped database must not attempt any write, so it must
    not contend. Before WI-6609 this raised ``OperationalError`` after the full
    30s busy timeout.
    """
    db_path = tmp_path / "locked.db"
    KnowledgeDB(db_path=db_path).close()

    blocker = sqlite3.connect(db_path, timeout=1)
    try:
        blocker.execute("BEGIN IMMEDIATE")
        blocker.execute("PRAGMA user_version")
        db = KnowledgeDB(db_path=db_path)  # must not raise
        db.close()
    finally:
        blocker.rollback()
        blocker.close()


def test_repeat_construction_performs_no_writes(tmp_path) -> None:
    """An up-to-date database must issue zero write statements at connect."""
    db_path = tmp_path / "readonly-path.db"
    KnowledgeDB(db_path=db_path).close()

    observed: list[str] = []

    def _trace(statement: str) -> None:
        head = statement.lstrip().split(None, 1)[0].upper() if statement.strip() else ""
        if head in {"INSERT", "UPDATE", "DELETE", "ALTER", "CREATE", "DROP"}:
            observed.append(statement.strip()[:80])

    db = KnowledgeDB(db_path=db_path)
    try:
        db._get_conn().set_trace_callback(_trace)
        db._ensure_schema()
    finally:
        db._get_conn().set_trace_callback(None)
        db.close()

    assert observed == [], f"connect-time writes on an up-to-date database: {observed}"


def test_stale_database_is_migrated_and_stamped(tmp_path) -> None:
    """A version-0 database (the pre-WI-6609 shape) upgrades exactly once."""
    db_path = tmp_path / "stale.db"
    KnowledgeDB(db_path=db_path).close()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA user_version = 0")
    conn.commit()
    conn.close()

    db = KnowledgeDB(db_path=db_path)
    try:
        assert db._schema_version(db._get_conn()) == SCHEMA_VERSION
    finally:
        db.close()


def test_migrations_are_idempotent(tmp_path) -> None:
    """Re-running the migration pass must not change schema or row state.

    This is the property that makes bootstrapping safe: existing databases
    report version 0 despite being fully migrated, so the first construction
    after WI-6609 re-runs all migrations before stamping.
    """
    db = KnowledgeDB(db_path=tmp_path / "idempotent.db")
    try:
        conn = db._get_conn()
        before = conn.execute("SELECT type, name, sql FROM sqlite_master ORDER BY type, name").fetchall()
        db._migrate_schema()
        after = conn.execute("SELECT type, name, sql FROM sqlite_master ORDER BY type, name").fetchall()
    finally:
        db.close()

    assert before == after


def test_schema_version_matches_migration_count(tmp_path) -> None:
    """Retained selector checks an actual stale-schema upgrade, not comments.

    Comment counts do not define schema generations. Exercise a supported
    column missing at the preceding generation and preserve pre-existing rows,
    including an inert old prompt table. This is not a complete migration audit.
    """
    path = tmp_path / "prior-generation.db"
    KnowledgeDB(path).close()
    with sqlite3.connect(path) as connection:
        connection.execute("ALTER TABLE specifications DROP COLUMN source_paths")
        connection.execute("CREATE TABLE session_prompts (id INTEGER PRIMARY KEY, prompt_text TEXT)")
        connection.execute("INSERT INTO session_prompts VALUES (1, 'OLD_PROMPT_RETAINED')")
        connection.execute("CREATE TABLE unrelated_payload (id INTEGER PRIMARY KEY, value TEXT)")
        connection.execute("INSERT INTO unrelated_payload VALUES (7, 'UNRELATED_RETAINED')")
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION - 1}")
    db = KnowledgeDB(path)
    try:
        spec = db.insert_spec(
            id="SPEC-MIGRATION-FIXTURE",
            title="Supported source paths after migration",
            status="specified",
            source_paths=["src/current.py"],
            changed_by="test",
            change_reason="exercise repaired column",
        )
        assert json.loads(db.get_spec(spec["id"])["source_paths"]) == ["src/current.py"]
        with sqlite3.connect(path) as connection:
            assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
            assert connection.execute("SELECT * FROM session_prompts").fetchall() == [(1, "OLD_PROMPT_RETAINED")]
            assert connection.execute("SELECT * FROM unrelated_payload").fetchall() == [(7, "UNRELATED_RETAINED")]
            before = list(connection.iterdump())
    finally:
        db.close()
    KnowledgeDB(path).close()
    with sqlite3.connect(path) as connection:
        assert list(connection.iterdump()) == before
