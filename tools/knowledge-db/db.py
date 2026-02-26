"""
Knowledge Database — Append-only SQLite store for specifications, test procedures,
and operational procedures. No UPDATE in place, no DELETE. Every mutation creates
a new versioned record. Claude is the sole writer; the owner observes via read-only UI.

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
    created_at TEXT NOT NULL,
    consumed_at TEXT,
    prompt_text TEXT NOT NULL,
    context TEXT,
    UNIQUE(session_id)
);

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
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def spec_sort_key(spec_id: str) -> tuple[int, ...]:
    """Convert decimal ID to tuple for correct numeric ordering.

    "245" → (245,), "245.2" → (245, 2), "245.10" → (245, 10)
    This ensures 245.2 sorts before 245.10 (unlike lexicographic TEXT sort).
    """
    try:
        return tuple(int(x) for x in spec_id.split("."))
    except (ValueError, AttributeError):
        return (0,)


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
    ) -> dict[str, Any]:
        """Insert a new version of a specification."""
        version = self._next_spec_version(id)
        assertions_json = json.dumps(assertions) if assertions else None
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, priority, scope, section,
             handle, tags_json, status, assertions_json, changed_by, _now(), change_reason),
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
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        priority = fields.get("priority", current["priority"])
        scope = fields.get("scope", current["scope"])
        section = fields.get("section", current["section"])
        handle = fields.get("handle", current["handle"])
        tags = fields.get("tags", current.get("_tags_parsed"))
        tags_json = json.dumps(tags) if tags else current["tags"]
        status = fields.get("status", current["status"])
        assertions = fields.get("assertions", current.get("_assertions_parsed"))
        assertions_json = json.dumps(assertions) if assertions else current["assertions"]

        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, description, priority, scope, section,
             handle, tags_json, status, assertions_json, changed_by, _now(), change_reason),
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
            # Tags stored as JSON array — use LIKE for containment check
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

    def _next_test_version(self, proc_id: str) -> int:
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
        version = self._next_test_version(id)
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

    def insert_session_prompt(
        self,
        session_id: str,
        prompt_text: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Store a next-session handoff prompt.

        Args:
            session_id: The session that generated this prompt (e.g. "S97").
            prompt_text: The full prompt text for the next session.
            context: Optional structured context (WIs changed, test counts, etc.).
        """
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO session_prompts
               (session_id, created_at, consumed_at, prompt_text, context)
               VALUES (?, ?, NULL, ?, ?)""",
            (session_id, _now(), prompt_text,
             json.dumps(context) if context else None),
        )
        conn.commit()
        return self.get_session_prompt(session_id)

    def get_session_prompt(self, session_id: str) -> dict[str, Any] | None:
        """Get a specific session's handoff prompt."""
        row = self._get_conn().execute(
            "SELECT * FROM session_prompts WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_next_session_prompt(self) -> dict[str, Any] | None:
        """Get the latest unconsumed handoff prompt (FIFO: most recent wins)."""
        row = self._get_conn().execute(
            """SELECT * FROM session_prompts
               WHERE consumed_at IS NULL
               ORDER BY rowid DESC LIMIT 1"""
        ).fetchone()
        return _row_to_dict(row) if row else None

    def consume_session_prompt(self, session_id: str) -> None:
        """Mark a session prompt as consumed (used to start a session)."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE session_prompts SET consumed_at = ? WHERE session_id = ?",
            (_now(), session_id),
        )
        conn.commit()

    def list_session_prompts(self, *, include_consumed: bool = False) -> list[dict[str, Any]]:
        """List session prompts, optionally including consumed ones."""
        if include_consumed:
            query = "SELECT * FROM session_prompts ORDER BY rowid DESC"
        else:
            query = "SELECT * FROM session_prompts WHERE consumed_at IS NULL ORDER BY rowid DESC"
        rows = self._get_conn().execute(query).fetchall()
        return [_row_to_dict(r) for r in rows]

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
            "specifications": ("id", "specifications"),
            "test_procedures": ("id", "test_procedures"),
            "operational_procedures": ("id", "operational_procedures"),
        }

        for tbl_key, (id_col, tbl_name) in tables.items():
            if table and table != tbl_key:
                continue
            where = ""
            if changed_by:
                where = " WHERE changed_by = ?"
                params.append(changed_by)
            parts.append(
                f"SELECT '{tbl_key}' AS table_name, {id_col} AS record_id, "
                f"version, title, changed_by, changed_at, change_reason "
                f"FROM {tbl_name}{where}"
            )

        if not parts:
            return []

        query = " UNION ALL ".join(parts) + f" ORDER BY changed_at DESC LIMIT {limit}"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

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

        return {
            "spec_counts": spec_counts,
            "spec_total": sum(spec_counts.values()),
            "spec_total_versions": total_versions,
            "test_procedure_count": test_count,
            "op_procedure_count": op_count,
            "assertions_total": assertion_stats["total"] or 0,
            "assertions_passed": assertion_stats["passed"] or 0,
            "assertions_failed": (assertion_stats["total"] or 0) - (assertion_stats["passed"] or 0),
        }


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    # Parse JSON fields for convenience
    for key in ("assertions", "results", "variables", "steps", "known_failure_modes", "tags"):
        if key in d and d[key] and isinstance(d[key], str):
            try:
                d[f"_{key}_parsed"] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d
