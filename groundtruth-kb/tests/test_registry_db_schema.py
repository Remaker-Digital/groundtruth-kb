"""WI-5441 Phase 1B: additive artifact-registry DB schema and migration tests.

Governing specifications (spec-to-test mapping carried into the implementation report):

- ``DCL-SOT-REGISTRY-RECORD-SCHEMA-001`` v3: additive nullable ``coverage_mode``
  locator column with no default (preserves existing ``NULL`` classification states).
- ``DCL-SOT-REGISTRY-PROJECTION-PARITY-001`` v2: observed revisions record history
  but never grant registry membership.
- ``DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`` v1: transaction-journal
  substrate for deterministic recovery after partial failure.
- ``DCL-QUARANTINE-RETENTION-EXPIRY-001`` v1: quarantine-receipt substrate binding
  identity, digests, immutable timestamps, and ``restore_pending``.
- ``GOV-PLATFORM-SOT-REGISTRY-001`` v2: registry projection parity preserved.

GO scope invariants (``bridge/gtkb-wi5441-registry-db-schema-002.md``): nullable
``coverage_mode`` with no default; idempotent migration; row/parity preservation;
no premature feature mutation. This is a schema-only slice: no retention/expiry,
quarantine, sweep, CLI, loader, or hook enforcement is exercised here.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB


def _columns(conn: sqlite3.Connection, table: str) -> dict[str, tuple]:
    # PRAGMA table_info row: (cid, name, type, notnull, dflt_value, pk).
    return {row[1]: tuple(row) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _fresh_db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(db_path=tmp_path / "groundtruth.db")


# --- DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v3: coverage_mode locator column ------


def test_coverage_mode_present_nullable_no_default(tmp_path):
    col = _columns(_fresh_db(tmp_path)._get_conn(), "sot_artifacts").get("coverage_mode")
    assert col is not None, "coverage_mode column must exist on sot_artifacts"
    assert col[2] == "TEXT"
    assert col[3] == 0, "coverage_mode must be nullable (notnull == 0)"
    assert col[4] is None, "coverage_mode must have no default (preserve existing NULL states)"


# --- New registry substrate tables carry all DCL-required columns ------------


def test_registry_tables_present_with_required_columns(tmp_path):
    conn = _fresh_db(tmp_path)._get_conn()

    revisions = set(_columns(conn, "sot_artifact_revisions"))
    assert {
        "revision_id",
        "entry_id",
        "canonical_relative_path",
        "object_kind",
        "content_digest",
        "size_bytes",
        "observed_at",
        "actor_session",
        "operation",
        "predecessor_revision_id",
    } <= revisions

    journal = set(_columns(conn, "sot_registry_transaction_journal"))
    assert {
        "journal_id",
        "operation",
        "entry_id",
        "intent_recorded_at",
        "declaration_digest",
        "prior_revision_id",
        "current_revision_id",
        "filesystem_result",
        "projection_transaction",
        "receipt_digest",
        "journal_state",
        "completed_at",
        "actor_session",
    } <= journal

    receipts = set(_columns(conn, "sot_quarantine_receipts"))
    assert {
        "receipt_id",
        "original_relative_path",
        "object_kind",
        "source_stat_evidence",
        "payload_path",
        "content_digest",
        "logical_size",
        "registry_declaration_digest",
        "observed_revision_cutoff",
        "inventory_digest",
        "sweep_plan_digest",
        "actor_session",
        "quarantined_at",
        "expires_at",
        "restore_pending",
        "receipt_state",
    } <= receipts


# --- GO invariant 3: idempotent migration ------------------------------------


def test_schema_migration_idempotent(tmp_path):
    db = _fresh_db(tmp_path)
    before = len(_columns(db._get_conn(), "sot_artifacts"))
    # Re-running SCHEMA_SQL + _migrate_schema must be a guarded no-op.
    db._ensure_schema()
    db._ensure_schema()
    after = len(_columns(db._get_conn(), "sot_artifacts"))
    assert before == after, "re-running schema/migration must not duplicate columns or error"


# --- GO invariant 4: migration from a pre-column DB preserves rows ------------

_OLD_SOT_ARTIFACTS = """
CREATE TABLE sot_artifacts (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    domain TEXT NOT NULL,
    lifecycle TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    authority_spec_id TEXT NOT NULL,
    mutation_api TEXT NOT NULL,
    versioning_policy TEXT NOT NULL,
    backup_policy TEXT NOT NULL,
    health_check_function TEXT,
    owner_role TEXT NOT NULL,
    depends_on TEXT,
    forbidden_substitutes TEXT,
    notes TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);
"""

_INSERT_SOT_ROW = (
    "INSERT INTO sot_artifacts "
    "(id,version,domain,lifecycle,storage_path,authority_spec_id,mutation_api,"
    "versioning_policy,backup_policy,owner_role,changed_by,changed_at,change_reason) "
    "VALUES (?,1,'d','active','p','A','api','v','b','owner','t','2026-01-01','r')"
)


def test_migration_adds_coverage_mode_and_preserves_rows(tmp_path):
    db_path = tmp_path / "groundtruth.db"
    raw = sqlite3.connect(db_path)
    raw.executescript(_OLD_SOT_ARTIFACTS)
    raw.execute(_INSERT_SOT_ROW, ("SOT-LEGACY",))
    raw.commit()
    raw.close()

    # Opening as KnowledgeDB runs SCHEMA_SQL (no-ops the existing table) then
    # _migrate_schema, which ALTERs in coverage_mode.
    conn = KnowledgeDB(db_path=db_path)._get_conn()
    assert "coverage_mode" in _columns(conn, "sot_artifacts")
    row = conn.execute("SELECT id, coverage_mode FROM sot_artifacts WHERE id = 'SOT-LEGACY'").fetchone()
    assert row is not None, "pre-existing row must survive the migration"
    assert row[0] == "SOT-LEGACY"
    assert row[1] is None, "migrated legacy row must retain NULL coverage_mode"


# --- DCL-SOT-REGISTRY-PROJECTION-PARITY-001: revisions don't grant membership -


def test_observed_revision_does_not_change_membership(tmp_path):
    conn = _fresh_db(tmp_path)._get_conn()
    conn.execute(_INSERT_SOT_ROW, ("SOT-M",))
    conn.commit()
    before = conn.execute("SELECT COUNT(*) FROM current_sot_artifacts").fetchone()[0]
    conn.execute(
        "INSERT INTO sot_artifact_revisions "
        "(revision_id,entry_id,canonical_relative_path,object_kind,content_digest,"
        "observed_at,actor_session,operation,changed_by,changed_at,change_reason) "
        "VALUES ('REV-1','SOT-M','p','file','sha256:x','2026-01-01','sess','observe','t','2026-01-01','r')"
    )
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM current_sot_artifacts").fetchone()[0]
    assert before == after, "observed-revision rows must not alter registry membership"
