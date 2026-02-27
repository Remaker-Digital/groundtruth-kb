"""
Knowledge Database — Append-only SQLite store for project artifacts: specifications,
tests, test plans, work items, backlog snapshots, operational procedures, documents,
and environment config. No UPDATE in place, no DELETE. Every mutation creates a new
versioned record. Claude is the sole writer; the owner observes via read-only UI.

RETENTION POLICY: Never delete. All rows are retained indefinitely. At ~20 KB per
session (~48 assertion runs + spec updates), 400 GB of storage supports ~57,000 years
of daily sessions. Storage is not a constraint. No pruning, archival, or compaction
is needed or desired. Use export_json() for logical backups.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "knowledge.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS specifications (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,
    scope TEXT,
    section TEXT,
    handle TEXT,
    tags TEXT,
    status TEXT NOT NULL,
    assertions TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS test_procedures (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    type TEXT,
    content TEXT,
    assertion_count INTEGER,
    last_execution_status TEXT,
    last_executed_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS operational_procedures (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    type TEXT,
    variables TEXT,
    steps TEXT,
    known_failure_modes TEXT,
    last_verified_at TEXT,
    last_corrected_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS assertion_runs (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    run_at TEXT NOT NULL,
    overall_passed INTEGER NOT NULL,
    results TEXT NOT NULL,
    triggered_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_prompts (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    event_type TEXT NOT NULL DEFAULT 'created',
    created_at TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    context TEXT
);

CREATE TABLE IF NOT EXISTS environment_config (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    environment TEXT NOT NULL,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    sensitive INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS documents (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT,
    tags TEXT,
    status TEXT NOT NULL,
    source_path TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS test_coverage (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id TEXT NOT NULL,
    test_file TEXT NOT NULL,
    test_class TEXT,
    test_function TEXT NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'high',
    match_reason TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tests (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    spec_id TEXT NOT NULL,
    test_type TEXT NOT NULL,
    test_file TEXT,
    test_class TEXT,
    test_function TEXT,
    description TEXT,
    expected_outcome TEXT NOT NULL,
    last_result TEXT,
    last_executed_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS test_plans (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS test_plan_phases (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    plan_id TEXT NOT NULL,
    phase_order INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    gate_criteria TEXT NOT NULL,
    test_ids TEXT,
    last_result TEXT,
    last_executed_at TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS work_items (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    origin TEXT NOT NULL,
    component TEXT NOT NULL,
    source_spec_id TEXT,
    source_test_id TEXT,
    failure_description TEXT,
    resolution_status TEXT NOT NULL,
    priority TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS backlog_snapshots (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    snapshot_at TEXT NOT NULL,
    work_item_ids TEXT NOT NULL,
    summary_by_origin TEXT,
    summary_by_component TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

-- Indexes for query performance (append-only tables grow monotonically)
CREATE INDEX IF NOT EXISTS idx_specs_id_version ON specifications(id, version);
CREATE INDEX IF NOT EXISTS idx_specs_status ON specifications(status);
CREATE INDEX IF NOT EXISTS idx_specs_changed_at ON specifications(changed_at);
CREATE INDEX IF NOT EXISTS idx_test_procs_id_version ON test_procedures(id, version);
CREATE INDEX IF NOT EXISTS idx_op_procs_id_version ON operational_procedures(id, version);
CREATE INDEX IF NOT EXISTS idx_assertion_runs_spec ON assertion_runs(spec_id, rowid);
CREATE INDEX IF NOT EXISTS idx_session_prompts_session ON session_prompts(session_id, rowid);
CREATE INDEX IF NOT EXISTS idx_env_config_id_version ON environment_config(id, version);
CREATE INDEX IF NOT EXISTS idx_env_config_env_cat ON environment_config(environment, category);
CREATE INDEX IF NOT EXISTS idx_docs_id_version ON documents(id, version);
CREATE INDEX IF NOT EXISTS idx_docs_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_test_cov_spec ON test_coverage(spec_id);
CREATE INDEX IF NOT EXISTS idx_test_cov_file ON test_coverage(test_file);
CREATE INDEX IF NOT EXISTS idx_tests_id_version ON tests(id, version);
CREATE INDEX IF NOT EXISTS idx_tests_spec_id ON tests(spec_id);
CREATE INDEX IF NOT EXISTS idx_test_plans_id_version ON test_plans(id, version);
CREATE INDEX IF NOT EXISTS idx_tpp_id_version ON test_plan_phases(id, version);
CREATE INDEX IF NOT EXISTS idx_tpp_plan_id ON test_plan_phases(plan_id);
CREATE INDEX IF NOT EXISTS idx_work_items_id_version ON work_items(id, version);
CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(resolution_status);
CREATE INDEX IF NOT EXISTS idx_work_items_origin ON work_items(origin);
CREATE INDEX IF NOT EXISTS idx_backlog_id_version ON backlog_snapshots(id, version);

-- Views: current state = latest version per ID
CREATE VIEW IF NOT EXISTS current_specifications AS
SELECT s.* FROM specifications s
INNER JOIN (SELECT id, MAX(version) AS max_v FROM specifications GROUP BY id) m
ON s.id = m.id AND s.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_test_procedures AS
SELECT t.* FROM test_procedures t
INNER JOIN (SELECT id, MAX(version) AS max_v FROM test_procedures GROUP BY id) m
ON t.id = m.id AND t.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_operational_procedures AS
SELECT o.* FROM operational_procedures o
INNER JOIN (SELECT id, MAX(version) AS max_v FROM operational_procedures GROUP BY id) m
ON o.id = m.id AND o.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_environment_config AS
SELECT e.* FROM environment_config e
INNER JOIN (SELECT id, MAX(version) AS max_v FROM environment_config GROUP BY id) m
ON e.id = m.id AND e.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_documents AS
SELECT d.* FROM documents d
INNER JOIN (SELECT id, MAX(version) AS max_v FROM documents GROUP BY id) m
ON d.id = m.id AND d.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_tests AS
SELECT t.* FROM tests t
INNER JOIN (SELECT id, MAX(version) AS max_v FROM tests GROUP BY id) m
ON t.id = m.id AND t.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_test_plans AS
SELECT t.* FROM test_plans t
INNER JOIN (SELECT id, MAX(version) AS max_v FROM test_plans GROUP BY id) m
ON t.id = m.id AND t.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_test_plan_phases AS
SELECT t.* FROM test_plan_phases t
INNER JOIN (SELECT id, MAX(version) AS max_v FROM test_plan_phases GROUP BY id) m
ON t.id = m.id AND t.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_work_items AS
SELECT w.* FROM work_items w
INNER JOIN (SELECT id, MAX(version) AS max_v FROM work_items GROUP BY id) m
ON w.id = m.id AND w.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_backlog_snapshots AS
SELECT b.* FROM backlog_snapshots b
INNER JOIN (SELECT id, MAX(version) AS max_v FROM backlog_snapshots GROUP BY id) m
ON b.id = m.id AND b.version = m.max_v;
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def spec_sort_key(spec_id: str) -> tuple:
    """Convert decimal ID to tuple for correct numeric ordering.

    "245" → (1, 245,), "245.2" → (1, 245, 2), "245.10" → (1, 245, 10)
    "PB-001" → (0, "PB-001")   (prefix-based IDs sort before numeric IDs)

    This ensures 245.2 sorts before 245.10 (unlike lexicographic TEXT sort),
    and non-numeric IDs (like PB-*) sort into their own group at the top.
    """
    try:
        return (1,) + tuple(int(x) for x in spec_id.split("."))
    except (ValueError, AttributeError):
        # Non-numeric IDs (PB-001, etc.) — sort lexicographically in group 0
        return (0, spec_id)


def get_parent_id(spec_id: str) -> str | None:
    """Return parent ID by stripping the last decimal segment.

    "245.1.3" → "245.1", "245.1" → "245", "245" → None
    """
    parts = spec_id.rsplit(".", 1)
    return parts[0] if len(parts) > 1 else None


def get_depth(spec_id: str) -> int:
    """Return nesting depth: "245" → 0, "245.1" → 1, "245.1.3" → 2."""
    return spec_id.count(".")


class KnowledgeDB:
    """Append-only knowledge database."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _ensure_schema(self) -> None:
        conn = self._get_conn()
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        self._migrate_schema()

    def _migrate_schema(self) -> None:
        """Apply incremental migrations that cannot be expressed as CREATE IF NOT EXISTS."""
        conn = self._get_conn()
        # Migration 1: Add 'type' column to specifications (S113)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)").fetchall()}
        if "type" not in cols:
            conn.execute("ALTER TABLE specifications ADD COLUMN type TEXT DEFAULT 'requirement'")
            # Backfill based on ID patterns
            conn.execute("UPDATE specifications SET type = 'governance' WHERE id LIKE 'GOV-%'")
            conn.execute("UPDATE specifications SET type = 'protected_behavior' WHERE id LIKE 'PB-%'")
            conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Specifications
    # ------------------------------------------------------------------

    def _next_spec_version(self, spec_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM specifications WHERE id = ?", (spec_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_spec(
        self,
        id: str,
        title: str,
        status: str,
        changed_by: str,
        change_reason: str,
        *,
        description: str | None = None,
        priority: str | None = None,
        scope: str | None = None,
        section: str | None = None,
        handle: str | None = None,
        tags: list[str] | None = None,
        assertions: list[dict] | None = None,
        type: str = "requirement",
    ) -> dict[str, Any]:
        """Insert a new version of a specification.

        Args:
            type: Specification type — 'requirement', 'governance', or 'protected_behavior'.
        """
        version = self._next_spec_version(id)
        assertions_json = json.dumps(assertions) if assertions else None
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, type, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, priority, scope, section,
             handle, tags_json, status, assertions_json, type, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_spec(id)

    def update_spec(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a spec, carrying forward unchanged fields."""
        current = self.get_spec(id)
        if not current:
            raise ValueError(f"Spec {id} not found")

        version = self._next_spec_version(id)
        # Merge: new fields override current values
        # Use _UNSET sentinel so callers can explicitly pass None or [] to clear fields
        _UNSET = object()
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        priority = fields.get("priority", current["priority"])
        scope = fields.get("scope", current["scope"])
        section = fields.get("section", current["section"])
        handle = fields.get("handle", current["handle"])
        status = fields.get("status", current["status"])
        spec_type = fields.get("type", current.get("type", "requirement"))

        # Tags and assertions: use 'is not _UNSET' to allow explicit [] or None
        raw_tags = fields.get("tags", _UNSET)
        if raw_tags is not _UNSET:
            tags_json = json.dumps(raw_tags) if raw_tags is not None else None
        else:
            tags_json = current["tags"]

        raw_assertions = fields.get("assertions", _UNSET)
        if raw_assertions is not _UNSET:
            assertions_json = json.dumps(raw_assertions) if raw_assertions is not None else None
        else:
            assertions_json = current["assertions"]

        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, type, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, priority, scope, section,
             handle, tags_json, status, assertions_json, spec_type, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_spec(id)

    def get_spec(self, spec_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of a specification."""
        row = self._get_conn().execute(
            "SELECT * FROM current_specifications WHERE id = ?", (spec_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_spec_history(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all versions of a specification, newest first."""
        rows = self._get_conn().execute(
            "SELECT * FROM specifications WHERE id = ? ORDER BY version DESC",
            (spec_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_specs(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        section: str | None = None,
        handle: str | None = None,
        tag: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current specifications with optional filters."""
        query = "SELECT * FROM current_specifications WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if section:
            query += " AND section LIKE ?"
            params.append(f"%{section}%")
        if handle:
            query += " AND handle = ?"
            params.append(handle)
        if tag:
            # Tags stored as JSON array — LIKE gives approximate containment.
            # Known limitation: "admin" matches both ["admin"] and ["non-admin"].
            # Exact matching would require a junction table (overkill at current scale).
            query += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        rows = self._get_conn().execute(query, params).fetchall()
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    def list_children(self, parent_id: str) -> list[dict[str, Any]]:
        """List current specs that are direct or nested children of parent_id.

        E.g., parent_id="245" returns 245.1, 245.2, 245.1.1, etc.
        """
        rows = self._get_conn().execute(
            "SELECT * FROM current_specifications WHERE id LIKE ?",
            (f"{parent_id}.%",),
        ).fetchall()
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    def list_direct_children(self, parent_id: str) -> list[dict[str, Any]]:
        """List current specs that are immediate children of parent_id.

        E.g., parent_id="245" returns 245.1, 245.2 but NOT 245.1.1.
        """
        target_depth = get_depth(parent_id) + 1
        all_children = self.list_children(parent_id)
        return [r for r in all_children if get_depth(r["id"]) == target_depth]

    # ------------------------------------------------------------------
    # Test Procedures
    # ------------------------------------------------------------------

    def _next_test_proc_version(self, proc_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM test_procedures WHERE id = ?", (proc_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_test_procedure(
        self,
        id: str,
        title: str,
        changed_by: str,
        change_reason: str,
        *,
        type: str | None = None,
        content: str | None = None,
        assertion_count: int | None = None,
        last_execution_status: str | None = None,
        last_executed_at: str | None = None,
    ) -> dict[str, Any]:
        version = self._next_test_proc_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_procedures
               (id, version, title, type, content, assertion_count,
                last_execution_status, last_executed_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, type, content, assertion_count,
             last_execution_status, last_executed_at,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_procedure(id)

    def get_test_procedure(self, proc_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_test_procedures WHERE id = ?", (proc_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_procedure_history(self, proc_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM test_procedures WHERE id = ? ORDER BY version DESC",
            (proc_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_test_procedures(self, *, type: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM current_test_procedures WHERE 1=1"
        params: list[Any] = []
        if type:
            query += " AND type = ?"
            params.append(type)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Operational Procedures
    # ------------------------------------------------------------------

    def _next_op_version(self, proc_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM operational_procedures WHERE id = ?", (proc_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_op_procedure(
        self,
        id: str,
        title: str,
        changed_by: str,
        change_reason: str,
        *,
        type: str | None = None,
        variables: dict | None = None,
        steps: list[dict] | None = None,
        known_failure_modes: list[dict] | None = None,
        last_verified_at: str | None = None,
        last_corrected_at: str | None = None,
    ) -> dict[str, Any]:
        version = self._next_op_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO operational_procedures
               (id, version, title, type, variables, steps, known_failure_modes,
                last_verified_at, last_corrected_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, type,
             json.dumps(variables) if variables else None,
             json.dumps(steps) if steps else None,
             json.dumps(known_failure_modes) if known_failure_modes else None,
             last_verified_at, last_corrected_at,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_op_procedure(id)

    def get_op_procedure(self, proc_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_operational_procedures WHERE id = ?", (proc_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_op_procedure_history(self, proc_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM operational_procedures WHERE id = ? ORDER BY version DESC",
            (proc_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_op_procedures(self, *, type: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM current_operational_procedures WHERE 1=1"
        params: list[Any] = []
        if type:
            query += " AND type = ?"
            params.append(type)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Environment Config
    # ------------------------------------------------------------------

    def _next_env_version(self, config_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM environment_config WHERE id = ?", (config_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_env_config(
        self,
        id: str,
        environment: str,
        category: str,
        key: str,
        value: str,
        changed_by: str,
        change_reason: str,
        *,
        sensitive: bool = False,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of an environment config entry.

        Args:
            id: Unique identifier (e.g., "prod-api-gateway-fqdn", "prod-tenant-remaker-widget-key").
            environment: Environment name ("production", "staging", "shared").
            category: Config category ("url", "credential", "infrastructure", "tenant").
            key: Human-readable key name (e.g., "API Gateway FQDN", "Widget Key").
            value: The actual value (URL, key, etc.).
            sensitive: If True, value is masked in web UI display (shown as ****).
            notes: Optional context (e.g., "Re-seeded S95", "Tenant: remaker-digital-001").
        """
        version = self._next_env_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO environment_config
               (id, version, environment, category, key, value, sensitive,
                notes, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, environment, category, key, value, int(sensitive),
             notes, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_env_config(id)

    def update_env_config(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of an env config entry, carrying forward unchanged fields."""
        current = self.get_env_config(id)
        if not current:
            raise ValueError(f"Environment config {id} not found")

        version = self._next_env_version(id)
        environment = fields.get("environment", current["environment"])
        category = fields.get("category", current["category"])
        key = fields.get("key", current["key"])
        value = fields.get("value", current["value"])
        sensitive = fields.get("sensitive", current["sensitive"])
        notes = fields.get("notes", current["notes"])

        conn = self._get_conn()
        conn.execute(
            """INSERT INTO environment_config
               (id, version, environment, category, key, value, sensitive,
                notes, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, environment, category, key, value, int(sensitive),
             notes, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_env_config(id)

    def get_env_config(self, config_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of an environment config entry."""
        row = self._get_conn().execute(
            "SELECT * FROM current_environment_config WHERE id = ?", (config_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def list_env_config(
        self,
        *,
        environment: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current environment config entries with optional filters."""
        query = "SELECT * FROM current_environment_config WHERE 1=1"
        params: list[Any] = []
        if environment:
            query += " AND environment = ?"
            params.append(environment)
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY environment, category, key"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_env_config_history(self, config_id: str) -> list[dict[str, Any]]:
        """Get all versions of an environment config entry, newest first."""
        rows = self._get_conn().execute(
            "SELECT * FROM environment_config WHERE id = ? ORDER BY version DESC",
            (config_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def _next_doc_version(self, doc_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_document(
        self,
        id: str,
        title: str,
        category: str,
        status: str,
        changed_by: str,
        change_reason: str,
        *,
        content: str | None = None,
        tags: list[str] | None = None,
        source_path: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of a document."""
        version = self._next_doc_version(id)
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO documents
               (id, version, title, category, content, tags, status,
                source_path, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, category, content, tags_json, status,
             source_path, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_document(id)

    def update_document(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a document, carrying forward unchanged fields."""
        current = self.get_document(id)
        if not current:
            raise ValueError(f"Document {id} not found")

        version = self._next_doc_version(id)
        _UNSET = object()
        title = fields.get("title", current["title"])
        category = fields.get("category", current["category"])
        content = fields.get("content", current["content"])
        status = fields.get("status", current["status"])
        source_path = fields.get("source_path", current["source_path"])

        raw_tags = fields.get("tags", _UNSET)
        if raw_tags is not _UNSET:
            tags_json = json.dumps(raw_tags) if raw_tags is not None else None
        else:
            tags_json = current["tags"]

        conn = self._get_conn()
        conn.execute(
            """INSERT INTO documents
               (id, version, title, category, content, tags, status,
                source_path, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, category, content, tags_json, status,
             source_path, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_document(id)

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_documents WHERE id = ?", (doc_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def list_documents(
        self, *, category: str | None = None, status: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM current_documents WHERE 1=1"
        params: list[Any] = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        if tag:
            query += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Test Coverage
    # ------------------------------------------------------------------

    def insert_test_coverage(
        self,
        spec_id: str,
        test_file: str,
        test_function: str,
        created_by: str,
        *,
        test_class: str | None = None,
        confidence: str = "high",
        match_reason: str | None = None,
    ) -> None:
        """Record a test-to-spec mapping."""
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_coverage
               (spec_id, test_file, test_class, test_function,
                confidence, match_reason, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec_id, test_file, test_class, test_function,
             confidence, match_reason, _now(), created_by),
        )
        conn.commit()

    def insert_test_coverage_batch(
        self,
        mappings: list[dict],
        created_by: str,
    ) -> int:
        """Batch-insert test coverage mappings. Returns count inserted."""
        conn = self._get_conn()
        count = 0
        for m in mappings:
            conn.execute(
                """INSERT INTO test_coverage
                   (spec_id, test_file, test_class, test_function,
                    confidence, match_reason, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (m["spec_id"], m["test_file"], m.get("test_class"),
                 m["test_function"], m.get("confidence", "high"),
                 m.get("match_reason"), _now(), created_by),
            )
            count += 1
        conn.commit()
        return count

    def get_test_coverage_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all test mappings for a spec."""
        rows = self._get_conn().execute(
            "SELECT * FROM test_coverage WHERE spec_id = ? ORDER BY test_file, test_function",
            (spec_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_test_coverage_summary(self) -> dict[str, Any]:
        """Get coverage statistics."""
        conn = self._get_conn()
        total_mappings = conn.execute("SELECT COUNT(*) FROM test_coverage").fetchone()[0]
        specs_covered = conn.execute(
            "SELECT COUNT(DISTINCT spec_id) FROM test_coverage"
        ).fetchone()[0]
        tests_mapped = conn.execute(
            "SELECT COUNT(DISTINCT test_file || ':' || test_function) FROM test_coverage"
        ).fetchone()[0]
        by_confidence = dict(conn.execute(
            "SELECT confidence, COUNT(*) FROM test_coverage GROUP BY confidence"
        ).fetchall())
        return {
            "total_mappings": total_mappings,
            "specs_covered": specs_covered,
            "tests_mapped": tests_mapped,
            "by_confidence": by_confidence,
        }

    # ------------------------------------------------------------------
    # Tests (individual test artifacts)
    # ------------------------------------------------------------------

    def _next_test_version(self, test_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM tests WHERE id = ?", (test_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_test(
        self,
        id: str,
        title: str,
        spec_id: str,
        test_type: str,
        expected_outcome: str,
        changed_by: str,
        change_reason: str,
        *,
        test_file: str | None = None,
        test_class: str | None = None,
        test_function: str | None = None,
        description: str | None = None,
        last_result: str | None = None,
        last_executed_at: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of a test artifact.

        Args:
            id: Unique identifier (e.g., "TEST-0001").
            spec_id: The specification this test verifies (required).
            test_type: 'unit', 'integration', 'e2e', 'manual', or 'assertion'.
            expected_outcome: What constitutes PASS — stated in human-readable terms.
        """
        version = self._next_test_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO tests
               (id, version, title, spec_id, test_type, test_file, test_class,
                test_function, description, expected_outcome, last_result,
                last_executed_at, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, spec_id, test_type, test_file, test_class,
             test_function, description, expected_outcome, last_result,
             last_executed_at, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test(id)

    def update_test(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a test, carrying forward unchanged fields."""
        current = self.get_test(id)
        if not current:
            raise ValueError(f"Test {id} not found")
        version = self._next_test_version(id)
        title = fields.get("title", current["title"])
        spec_id = fields.get("spec_id", current["spec_id"])
        test_type = fields.get("test_type", current["test_type"])
        test_file = fields.get("test_file", current["test_file"])
        test_class = fields.get("test_class", current["test_class"])
        test_function = fields.get("test_function", current["test_function"])
        description = fields.get("description", current["description"])
        expected_outcome = fields.get("expected_outcome", current["expected_outcome"])
        last_result = fields.get("last_result", current["last_result"])
        last_executed_at = fields.get("last_executed_at", current["last_executed_at"])
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO tests
               (id, version, title, spec_id, test_type, test_file, test_class,
                test_function, description, expected_outcome, last_result,
                last_executed_at, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, spec_id, test_type, test_file, test_class,
             test_function, description, expected_outcome, last_result,
             last_executed_at, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test(id)

    def get_test(self, test_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_tests WHERE id = ?", (test_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_history(self, test_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM tests WHERE id = ? ORDER BY version DESC", (test_id,)
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_tests(
        self,
        *,
        spec_id: str | None = None,
        test_type: str | None = None,
        last_result: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current tests with optional filters."""
        query = "SELECT * FROM current_tests WHERE 1=1"
        params: list[Any] = []
        if spec_id:
            query += " AND spec_id = ?"
            params.append(spec_id)
        if test_type:
            query += " AND test_type = ?"
            params.append(test_type)
        if last_result:
            query += " AND last_result = ?"
            params.append(last_result)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_tests_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all current tests that verify a given specification."""
        return self.list_tests(spec_id=spec_id)

    def get_untested_specs(self) -> list[dict[str, Any]]:
        """Get specifications that have no tests linked to them."""
        rows = self._get_conn().execute(
            """SELECT s.* FROM current_specifications s
               LEFT JOIN current_tests t ON t.spec_id = s.id
               WHERE t.id IS NULL
               ORDER BY s.id"""
        ).fetchall()
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    # ------------------------------------------------------------------
    # Test Plans
    # ------------------------------------------------------------------

    def _next_plan_version(self, plan_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM test_plans WHERE id = ?", (plan_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_test_plan(
        self,
        id: str,
        title: str,
        status: str,
        changed_by: str,
        change_reason: str,
        *,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of a test plan.

        Args:
            status: 'draft', 'active', or 'retired'.
        """
        version = self._next_plan_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_plans
               (id, version, title, description, status,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, status,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan(id)

    def update_test_plan(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a test plan, carrying forward unchanged fields."""
        current = self.get_test_plan(id)
        if not current:
            raise ValueError(f"Test plan {id} not found")
        version = self._next_plan_version(id)
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        status = fields.get("status", current["status"])
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_plans
               (id, version, title, description, status,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, status,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan(id)

    def get_test_plan(self, plan_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_test_plans WHERE id = ?", (plan_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_plan_history(self, plan_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM test_plans WHERE id = ? ORDER BY version DESC", (plan_id,)
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_test_plans(self, *, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM current_test_plans WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_active_test_plan(self) -> dict[str, Any] | None:
        """Get the currently active test plan (status='active'). Returns None if no active plan."""
        plans = self.list_test_plans(status="active")
        return plans[0] if plans else None

    # ------------------------------------------------------------------
    # Test Plan Phases
    # ------------------------------------------------------------------

    def _next_phase_version(self, phase_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM test_plan_phases WHERE id = ?", (phase_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_test_plan_phase(
        self,
        id: str,
        plan_id: str,
        phase_order: int,
        title: str,
        gate_criteria: str,
        changed_by: str,
        change_reason: str,
        *,
        description: str | None = None,
        test_ids: list[str] | None = None,
        last_result: str | None = None,
        last_executed_at: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of a test plan phase.

        Args:
            plan_id: Which test plan this phase belongs to.
            phase_order: Execution sequence (1, 2, 3...).
            gate_criteria: What constitutes PASS for this phase.
            test_ids: JSON-serializable list of test IDs in this phase.
        """
        version = self._next_phase_version(id)
        test_ids_json = json.dumps(test_ids) if test_ids else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_plan_phases
               (id, version, plan_id, phase_order, title, description,
                gate_criteria, test_ids, last_result, last_executed_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, plan_id, phase_order, title, description,
             gate_criteria, test_ids_json, last_result, last_executed_at,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan_phase(id)

    def update_test_plan_phase(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a test plan phase, carrying forward unchanged fields."""
        current = self.get_test_plan_phase(id)
        if not current:
            raise ValueError(f"Test plan phase {id} not found")
        version = self._next_phase_version(id)
        _UNSET = object()
        plan_id = fields.get("plan_id", current["plan_id"])
        phase_order = fields.get("phase_order", current["phase_order"])
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        gate_criteria = fields.get("gate_criteria", current["gate_criteria"])
        last_result = fields.get("last_result", current["last_result"])
        last_executed_at = fields.get("last_executed_at", current["last_executed_at"])
        raw_test_ids = fields.get("test_ids", _UNSET)
        if raw_test_ids is not _UNSET:
            test_ids_json = json.dumps(raw_test_ids) if raw_test_ids is not None else None
        else:
            test_ids_json = current["test_ids"]
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_plan_phases
               (id, version, plan_id, phase_order, title, description,
                gate_criteria, test_ids, last_result, last_executed_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, plan_id, phase_order, title, description,
             gate_criteria, test_ids_json, last_result, last_executed_at,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan_phase(id)

    def get_test_plan_phase(self, phase_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_test_plan_phases WHERE id = ?", (phase_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def list_test_plan_phases(self, plan_id: str) -> list[dict[str, Any]]:
        """List current phases for a test plan, ordered by phase_order."""
        rows = self._get_conn().execute(
            "SELECT * FROM current_test_plan_phases WHERE plan_id = ? ORDER BY phase_order",
            (plan_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Work Items
    # ------------------------------------------------------------------

    def _next_work_item_version(self, item_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM work_items WHERE id = ?", (item_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_work_item(
        self,
        id: str,
        title: str,
        origin: str,
        component: str,
        resolution_status: str,
        changed_by: str,
        change_reason: str,
        *,
        description: str | None = None,
        source_spec_id: str | None = None,
        source_test_id: str | None = None,
        failure_description: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new version of a work item.

        Args:
            origin: 'regression', 'defect', or 'new'.
            component: From the component taxonomy (e.g., 'agent_implementation', 'customer_interface').
            resolution_status: 'open', 'in_progress', 'resolved', or 'verified'.
            source_spec_id: The specification this work item relates to (required for all origins).
            source_test_id: The test that revealed the failure (required for regression/defect).
            failure_description: What failed and why (required for regression/defect).
        """
        version = self._next_work_item_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO work_items
               (id, version, title, description, origin, component,
                source_spec_id, source_test_id, failure_description,
                resolution_status, priority,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, origin, component,
             source_spec_id, source_test_id, failure_description,
             resolution_status, priority,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_work_item(id)

    def update_work_item(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Create a new version of a work item, carrying forward unchanged fields."""
        current = self.get_work_item(id)
        if not current:
            raise ValueError(f"Work item {id} not found")
        version = self._next_work_item_version(id)
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        origin = fields.get("origin", current["origin"])
        component = fields.get("component", current["component"])
        source_spec_id = fields.get("source_spec_id", current["source_spec_id"])
        source_test_id = fields.get("source_test_id", current["source_test_id"])
        failure_description = fields.get("failure_description", current["failure_description"])
        resolution_status = fields.get("resolution_status", current["resolution_status"])
        priority = fields.get("priority", current["priority"])
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO work_items
               (id, version, title, description, origin, component,
                source_spec_id, source_test_id, failure_description,
                resolution_status, priority,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, origin, component,
             source_spec_id, source_test_id, failure_description,
             resolution_status, priority,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_work_item(id)

    def get_work_item(self, item_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_work_items WHERE id = ?", (item_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_work_item_history(self, item_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM work_items WHERE id = ? ORDER BY version DESC", (item_id,)
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_work_items(
        self,
        *,
        origin: str | None = None,
        component: str | None = None,
        resolution_status: str | None = None,
        priority: str | None = None,
        source_spec_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current work items with optional filters."""
        query = "SELECT * FROM current_work_items WHERE 1=1"
        params: list[Any] = []
        if origin:
            query += " AND origin = ?"
            params.append(origin)
        if component:
            query += " AND component = ?"
            params.append(component)
        if resolution_status:
            query += " AND resolution_status = ?"
            params.append(resolution_status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if source_spec_id:
            query += " AND source_spec_id = ?"
            params.append(source_spec_id)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_open_work_items(self) -> list[dict[str, Any]]:
        """Get all work items that are not yet verified (the active backlog)."""
        rows = self._get_conn().execute(
            """SELECT * FROM current_work_items
               WHERE resolution_status != 'verified'
               ORDER BY priority, id"""
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Backlog Snapshots
    # ------------------------------------------------------------------

    def _next_backlog_version(self, snapshot_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM backlog_snapshots WHERE id = ?", (snapshot_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_backlog_snapshot(
        self,
        id: str,
        title: str,
        work_item_ids: list[str],
        changed_by: str,
        change_reason: str,
        *,
        description: str | None = None,
        snapshot_at: str | None = None,
        summary_by_origin: dict | None = None,
        summary_by_component: dict | None = None,
    ) -> dict[str, Any]:
        """Insert a new backlog snapshot.

        Args:
            work_item_ids: Ordered list of active work item IDs (priority order).
            summary_by_origin: Counts by origin (e.g., {"regression": 2, "defect": 5, "new": 12}).
            summary_by_component: Counts by component.
        """
        version = self._next_backlog_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO backlog_snapshots
               (id, version, title, description, snapshot_at, work_item_ids,
                summary_by_origin, summary_by_component,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, snapshot_at or _now(),
             json.dumps(work_item_ids),
             json.dumps(summary_by_origin) if summary_by_origin else None,
             json.dumps(summary_by_component) if summary_by_component else None,
             changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_backlog_snapshot(id)

    def get_backlog_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            "SELECT * FROM current_backlog_snapshots WHERE id = ?", (snapshot_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_backlog_snapshot_history(self, snapshot_id: str) -> list[dict[str, Any]]:
        rows = self._get_conn().execute(
            "SELECT * FROM backlog_snapshots WHERE id = ? ORDER BY version DESC",
            (snapshot_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_backlog_snapshots(self, *, limit: int = 20) -> list[dict[str, Any]]:
        """List backlog snapshots, most recent first."""
        rows = self._get_conn().execute(
            "SELECT * FROM current_backlog_snapshots ORDER BY snapshot_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def create_backlog_snapshot_from_current(
        self,
        snapshot_id: str,
        changed_by: str,
        change_reason: str,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a backlog snapshot from the current state of open work items.

        Queries all non-verified work items, captures their IDs in priority order,
        and computes summary counts by origin and component.
        """
        open_items = self.get_open_work_items()
        work_item_ids = [item["id"] for item in open_items]
        summary_origin: dict[str, int] = {}
        summary_component: dict[str, int] = {}
        for item in open_items:
            o = item.get("origin", "unknown")
            c = item.get("component", "unknown")
            summary_origin[o] = summary_origin.get(o, 0) + 1
            summary_component[c] = summary_component.get(c, 0) + 1
        return self.insert_backlog_snapshot(
            id=snapshot_id,
            title=title or f"Backlog snapshot {snapshot_id}",
            work_item_ids=work_item_ids,
            changed_by=changed_by,
            change_reason=change_reason,
            description=description,
            summary_by_origin=summary_origin,
            summary_by_component=summary_component,
        )

    # ------------------------------------------------------------------
    # Assertion Runs
    # ------------------------------------------------------------------

    def insert_assertion_run(
        self,
        spec_id: str,
        spec_version: int,
        overall_passed: bool,
        results: list[dict],
        triggered_by: str,
    ) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO assertion_runs
               (spec_id, spec_version, run_at, overall_passed, results, triggered_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (spec_id, spec_version, _now(), int(overall_passed),
             json.dumps(results), triggered_by),
        )
        conn.commit()

    def get_latest_assertion_run(self, spec_id: str) -> dict[str, Any] | None:
        row = self._get_conn().execute(
            """SELECT * FROM assertion_runs
               WHERE spec_id = ? ORDER BY rowid DESC LIMIT 1""",
            (spec_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_all_latest_assertion_runs(self) -> list[dict[str, Any]]:
        """Get the most recent assertion run for each spec."""
        rows = self._get_conn().execute(
            """SELECT a.* FROM assertion_runs a
               INNER JOIN (
                   SELECT spec_id, MAX(rowid) AS max_rowid
                   FROM assertion_runs GROUP BY spec_id
               ) m ON a.spec_id = m.spec_id AND a.rowid = m.max_rowid
               ORDER BY a.spec_id"""
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Session Prompts
    # ------------------------------------------------------------------

    def _next_session_prompt_version(self, session_id: str) -> int:
        row = self._get_conn().execute(
            "SELECT MAX(version) FROM session_prompts WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return (row[0] or 0) + 1

    def insert_session_prompt(
        self,
        session_id: str,
        prompt_text: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Store a next-session handoff prompt (append-only).

        Args:
            session_id: The session that generated this prompt (e.g. "S97").
            prompt_text: The full prompt text for the next session.
            context: Optional structured context (WIs changed, test counts, etc.).

        Multiple calls for the same session_id create versioned records.
        """
        version = self._next_session_prompt_version(session_id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO session_prompts
               (session_id, version, event_type, created_at, prompt_text, context)
               VALUES (?, ?, 'created', ?, ?, ?)""",
            (session_id, version, _now(), prompt_text,
             json.dumps(context) if context else None),
        )
        conn.commit()
        return self.get_session_prompt(session_id)

    def get_session_prompt(self, session_id: str) -> dict[str, Any] | None:
        """Get the latest event for a specific session's handoff prompt."""
        row = self._get_conn().execute(
            """SELECT * FROM session_prompts
               WHERE session_id = ? ORDER BY rowid DESC LIMIT 1""",
            (session_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_next_session_prompt(self) -> dict[str, Any] | None:
        """Get the latest unconsumed handoff prompt.

        A prompt is unconsumed if its most recent event is 'created' (not 'consumed').
        Returns the most recently created prompt that hasn't been consumed.
        """
        # Find session_ids whose latest event is 'created'
        row = self._get_conn().execute(
            """SELECT p.* FROM session_prompts p
               INNER JOIN (
                   SELECT session_id, MAX(rowid) AS max_rowid
                   FROM session_prompts GROUP BY session_id
               ) m ON p.session_id = m.session_id AND p.rowid = m.max_rowid
               WHERE p.event_type = 'created'
               ORDER BY p.rowid DESC LIMIT 1"""
        ).fetchone()
        return _row_to_dict(row) if row else None

    def consume_session_prompt(self, session_id: str) -> None:
        """Record consumption of a session prompt (append-only — inserts new row)."""
        current = self.get_session_prompt(session_id)
        if not current:
            return
        version = self._next_session_prompt_version(session_id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO session_prompts
               (session_id, version, event_type, created_at, prompt_text, context)
               VALUES (?, ?, 'consumed', ?, ?, ?)""",
            (session_id, version, _now(),
             current.get("prompt_text", ""),
             current.get("context")),
        )
        conn.commit()

    def list_session_prompts(self, *, include_consumed: bool = False) -> list[dict[str, Any]]:
        """List session prompts, optionally including consumed ones."""
        if include_consumed:
            rows = self._get_conn().execute(
                "SELECT * FROM session_prompts ORDER BY rowid DESC"
            ).fetchall()
        else:
            # Only show sessions whose latest event is 'created'
            rows = self._get_conn().execute(
                """SELECT p.* FROM session_prompts p
                   INNER JOIN (
                       SELECT session_id, MAX(rowid) AS max_rowid
                       FROM session_prompts GROUP BY session_id
                   ) m ON p.session_id = m.session_id AND p.rowid = m.max_rowid
                   WHERE p.event_type = 'created'
                   ORDER BY p.rowid DESC"""
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Audit Cadence
    # ------------------------------------------------------------------

    AUDIT_INTERVAL = 5  # every 5 sessions

    @staticmethod
    def parse_session_number(session_id: str) -> int | None:
        """Extract the numeric part from a session ID like 'S98'. Returns None if not parseable."""
        import re
        m = re.match(r"[Ss](\d+)$", session_id.strip())
        return int(m.group(1)) if m else None

    def is_audit_session(self, next_session_id: str, interval: int | None = None) -> bool:
        """Check whether the given session should be an audit session.

        Audit sessions occur every `interval` sessions (default: AUDIT_INTERVAL).
        S100, S105, S110, ... are audit sessions at interval=5.
        """
        n = self.parse_session_number(next_session_id)
        if n is None:
            return False
        return n % (interval or self.AUDIT_INTERVAL) == 0

    @staticmethod
    def get_audit_directive() -> str:
        """Return the standard audit session directive text."""
        return (
            "AUDIT SESSION: This is a scheduled self-care session. Before starting "
            "new feature work, perform a fresh-context review:\n"
            "1. Knowledge DB integrity — run assertions, check for status drift, "
            "verify append-only invariants hold\n"
            "2. MEMORY.md and CLAUDE.md — accuracy, staleness, contradictions, "
            "line count within limits\n"
            "3. Repeatable Procedures — still accurate? Any procedure defects "
            "from recent sessions?\n"
            "4. Open design debt — any patterns from recent sessions that need "
            "cleanup or consolidation?\n"
            "5. Hooks and scheduler — verify all hooks execute without errors "
            "(check stderr output)\n"
            "Report findings to the owner before proceeding with regular work."
        )

    # ------------------------------------------------------------------
    # Global History
    # ------------------------------------------------------------------

    def get_history(
        self, *, limit: int = 50, changed_by: str | None = None, table: str | None = None
    ) -> list[dict[str, Any]]:
        """Get recent changes across all tables, newest first."""
        parts = []
        params: list[Any] = []

        tables = {
            "specifications": ("id", "specifications", "title"),
            "test_procedures": ("id", "test_procedures", "title"),
            "operational_procedures": ("id", "operational_procedures", "title"),
            "environment_config": ("id", "environment_config", "key"),
            "documents": ("id", "documents", "title"),
            "tests": ("id", "tests", "title"),
            "test_plans": ("id", "test_plans", "title"),
            "test_plan_phases": ("id", "test_plan_phases", "title"),
            "work_items": ("id", "work_items", "title"),
            "backlog_snapshots": ("id", "backlog_snapshots", "title"),
        }

        for tbl_key, (id_col, tbl_name, title_col) in tables.items():
            if table and table != tbl_key:
                continue
            where = ""
            if changed_by:
                where = " WHERE changed_by = ?"
                params.append(changed_by)
            parts.append(
                f"SELECT '{tbl_key}' AS table_name, {id_col} AS record_id, "
                f"version, {title_col} AS title, changed_by, changed_at, change_reason "
                f"FROM {tbl_name}{where}"
            )

        if not parts:
            return []

        query = " UNION ALL ".join(parts) + f" ORDER BY changed_at DESC LIMIT {limit}"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Export / Backup
    # ------------------------------------------------------------------

    def export_json(self, output_path: str | Path | None = None) -> str:
        """Export the entire database as a JSON file (all tables, all rows).

        This is a full logical backup — every row from every table, preserving
        the complete append-only history. The export can be used to reconstruct
        the database from scratch if the SQLite file is lost or corrupted.

        Args:
            output_path: Where to write the JSON. Defaults to sibling of the DB
                         file with a UTC timestamp suffix.

        Returns:
            The path to the written file.
        """
        from datetime import datetime, timezone

        conn = self._get_conn()
        tables = ["specifications", "test_procedures", "operational_procedures",
                   "assertion_runs", "session_prompts", "environment_config",
                   "documents", "test_coverage", "tests", "test_plans",
                   "test_plan_phases", "work_items", "backlog_snapshots"]
        export = {"exported_at": _now(), "tables": {}}
        for table in tables:
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
            export["tables"][table] = [_row_to_dict(r) for r in rows]

        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            output_path = self.db_path.parent / f"knowledge-export-{timestamp}.json"
        else:
            output_path = Path(output_path)

        output_path.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
        return str(output_path)

    # ------------------------------------------------------------------
    # Summary stats
    # ------------------------------------------------------------------

    def get_summary(self) -> dict[str, Any]:
        conn = self._get_conn()
        specs = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM current_specifications GROUP BY status"
        ).fetchall()
        spec_counts = {r["status"]: r["cnt"] for r in specs}

        test_count = conn.execute(
            "SELECT COUNT(*) FROM current_test_procedures"
        ).fetchone()[0]

        op_count = conn.execute(
            "SELECT COUNT(*) FROM current_operational_procedures"
        ).fetchone()[0]

        assertion_stats = conn.execute(
            """SELECT
                 COUNT(*) as total,
                 SUM(overall_passed) as passed
               FROM (
                 SELECT a.* FROM assertion_runs a
                 INNER JOIN (
                   SELECT spec_id, MAX(rowid) AS max_rowid
                   FROM assertion_runs GROUP BY spec_id
                 ) m ON a.spec_id = m.spec_id AND a.rowid = m.max_rowid
               )"""
        ).fetchone()

        total_versions = conn.execute(
            "SELECT COUNT(*) FROM specifications"
        ).fetchone()[0]

        env_count = conn.execute(
            "SELECT COUNT(*) FROM current_environment_config"
        ).fetchone()[0]

        doc_count = conn.execute(
            "SELECT COUNT(*) FROM current_documents"
        ).fetchone()[0]

        # Test coverage stats (legacy — superseded by tests table)
        cov_mappings = conn.execute("SELECT COUNT(*) FROM test_coverage").fetchone()[0]
        cov_specs = conn.execute("SELECT COUNT(DISTINCT spec_id) FROM test_coverage").fetchone()[0]

        # New artifact counts
        test_artifact_count = conn.execute("SELECT COUNT(*) FROM current_tests").fetchone()[0]
        test_plan_count = conn.execute("SELECT COUNT(*) FROM current_test_plans").fetchone()[0]
        test_plan_phase_count = conn.execute("SELECT COUNT(*) FROM current_test_plan_phases").fetchone()[0]

        wi_stats = conn.execute(
            "SELECT resolution_status, COUNT(*) as cnt FROM current_work_items GROUP BY resolution_status"
        ).fetchall()
        work_item_counts = {r["resolution_status"]: r["cnt"] for r in wi_stats}

        backlog_count = conn.execute("SELECT COUNT(*) FROM current_backlog_snapshots").fetchone()[0]

        return {
            "spec_counts": spec_counts,
            "spec_total": sum(spec_counts.values()),
            "spec_total_versions": total_versions,
            "test_procedure_count": test_count,
            "op_procedure_count": op_count,
            "assertions_total": assertion_stats["total"] or 0,
            "assertions_passed": assertion_stats["passed"] or 0,
            "assertions_failed": (assertion_stats["total"] or 0) - (assertion_stats["passed"] or 0),
            "env_config_count": env_count,
            "document_count": doc_count,
            "test_coverage_mappings": cov_mappings,
            "test_coverage_specs": cov_specs,
            "test_artifact_count": test_artifact_count,
            "test_plan_count": test_plan_count,
            "test_plan_phase_count": test_plan_phase_count,
            "work_item_counts": work_item_counts,
            "work_item_total": sum(work_item_counts.values()),
            "backlog_snapshot_count": backlog_count,
        }


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    # Parse JSON fields — expose as both "field_parsed" (clean) and "_field_parsed" (legacy)
    for key in ("assertions", "results", "variables", "steps", "known_failure_modes",
                 "tags", "context", "test_ids", "work_item_ids",
                 "summary_by_origin", "summary_by_component"):
        if key in d and d[key] and isinstance(d[key], str):
            try:
                parsed = json.loads(d[key])
                d[f"{key}_parsed"] = parsed
                d[f"_{key}_parsed"] = parsed  # backward compat
            except (json.JSONDecodeError, TypeError):
                pass
    return d
