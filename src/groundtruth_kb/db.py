"""
GroundTruth KB — Versioned SQLite store for project artifacts.

Manages specifications, tests, test plans, work items, backlog snapshots,
operational procedures, documents, and environment config. Core data uses
append-only versioning (UNIQUE(id, version)) — every mutation creates a new
versioned record.

RETENTION POLICY: Core artifact rows are never deleted. Operational tables
(assertion_runs, quality_scores) permit maintenance deletes for pruning stale
history. Use export_json() for logical backups.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.gates import GateRegistry

# Default DB path — overridden by GTConfig.db_path or constructor arg
DB_PATH = Path("./groundtruth.db")

# ChromaDB optional dependency (ignore_missing_imports configured in pyproject.toml)
try:
    import chromadb

    HAS_CHROMADB = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    HAS_CHROMADB = False

# Semantic search constants
SEMANTIC_MAX_DISTANCE = 1.5  # L2 distance threshold for relevance filtering
CHUNK_MAX_TOKENS = 230  # Safe margin below all-MiniLM-L6-v2's 256 wordpiece limit
CHUNK_OVERLAP_TOKENS = 30  # Overlap between consecutive chunks
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_CHROMA_COLLECTION_NAME = "deliberations"


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
    stage TEXT NOT NULL DEFAULT 'created',
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

CREATE TABLE IF NOT EXISTS testable_elements (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    subsystem TEXT NOT NULL,
    page_or_module TEXT NOT NULL,
    name TEXT NOT NULL,
    element_type TEXT NOT NULL,
    expected_behavior TEXT NOT NULL,
    spec_id TEXT,
    applicable_dimensions TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS quality_scores (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    computed_at TEXT NOT NULL,
    spec_coverage REAL NOT NULL,
    defect_escape_rate REAL NOT NULL,
    assertion_strength REAL NOT NULL,
    change_failure_rate REAL NOT NULL,
    test_freshness REAL NOT NULL,
    coverage_delta REAL NOT NULL,
    composite_score REAL NOT NULL,
    details TEXT,
    UNIQUE(session_id)
);

-- F3: Per-spec quality scores (spec pipeline)
CREATE TABLE IF NOT EXISTS spec_quality_scores (
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    scored_at TEXT NOT NULL,
    overall REAL NOT NULL,
    d1_clarity REAL NOT NULL,
    d2_testability REAL NOT NULL,
    d3_completeness REAL NOT NULL,
    d4_isolation REAL NOT NULL,
    d5_freshness REAL NOT NULL,
    tier TEXT NOT NULL,
    flags TEXT,
    UNIQUE(spec_id, spec_version, session_id)
);

-- F7: Session health snapshots
CREATE TABLE IF NOT EXISTS session_snapshots (
    session_id TEXT NOT NULL PRIMARY KEY,
    captured_at TEXT NOT NULL,
    data TEXT NOT NULL
);

-- Pipeline lifecycle events (SPEC-2099) — append-only event log
CREATE TABLE IF NOT EXISTS pipeline_events (
    id              TEXT    NOT NULL PRIMARY KEY,
    event_type      TEXT    NOT NULL,
    session_id      TEXT,
    artifact_id     TEXT,
    artifact_type   TEXT,
    artifact_version INTEGER,
    timestamp       TEXT    NOT NULL,
    duration_ms     INTEGER,
    metadata        TEXT,
    changed_by      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS deliberations (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    spec_id TEXT,
    work_item_id TEXT,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT,
    participants TEXT,
    outcome TEXT,
    session_id TEXT,
    sensitivity TEXT DEFAULT 'normal',
    redaction_state TEXT DEFAULT 'clean',
    redaction_notes TEXT,
    origin_project TEXT,
    origin_repo TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    UNIQUE(id, version)
);

CREATE TABLE IF NOT EXISTS deliberation_specs (
    deliberation_id TEXT NOT NULL,
    spec_id TEXT NOT NULL,
    role TEXT DEFAULT 'related',
    UNIQUE(deliberation_id, spec_id)
);

CREATE TABLE IF NOT EXISTS deliberation_work_items (
    deliberation_id TEXT NOT NULL,
    work_item_id TEXT NOT NULL,
    role TEXT DEFAULT 'related',
    UNIQUE(deliberation_id, work_item_id)
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
CREATE INDEX IF NOT EXISTS idx_te_id_version ON testable_elements(id, version);
CREATE INDEX IF NOT EXISTS idx_te_subsystem ON testable_elements(subsystem);
CREATE INDEX IF NOT EXISTS idx_te_status ON testable_elements(status);
CREATE INDEX IF NOT EXISTS idx_quality_scores_session ON quality_scores(session_id);
CREATE INDEX IF NOT EXISTS idx_pe_event_type_ts ON pipeline_events(event_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_pe_artifact ON pipeline_events(artifact_type, artifact_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_pe_session_ts ON pipeline_events(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_deliberations_id_version ON deliberations(id, version);
CREATE INDEX IF NOT EXISTS idx_deliberations_spec_id ON deliberations(spec_id);
CREATE INDEX IF NOT EXISTS idx_deliberations_work_item_id ON deliberations(work_item_id);
CREATE INDEX IF NOT EXISTS idx_deliberations_source_type ON deliberations(source_type);
CREATE INDEX IF NOT EXISTS idx_deliberations_session_id ON deliberations(session_id);
CREATE INDEX IF NOT EXISTS idx_deliberations_source_ref ON deliberations(source_ref);
CREATE INDEX IF NOT EXISTS idx_dspecs_delib ON deliberation_specs(deliberation_id);
CREATE INDEX IF NOT EXISTS idx_dspecs_spec ON deliberation_specs(spec_id);
CREATE INDEX IF NOT EXISTS idx_dwis_delib ON deliberation_work_items(deliberation_id);
CREATE INDEX IF NOT EXISTS idx_dwis_wi ON deliberation_work_items(work_item_id);

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

CREATE VIEW IF NOT EXISTS current_testable_elements AS
SELECT t.* FROM testable_elements t
INNER JOIN (SELECT id, MAX(version) AS max_v FROM testable_elements GROUP BY id) m
ON t.id = m.id AND t.version = m.max_v;

CREATE VIEW IF NOT EXISTS current_deliberations AS
SELECT d.* FROM deliberations d
INNER JOIN (SELECT id, MAX(version) AS max_v FROM deliberations GROUP BY id) m
ON d.id = m.id AND d.version = m.max_v;
"""


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def spec_sort_key(spec_id: str) -> tuple[Any, ...]:
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


# --- F1: Schema Enrichment sentinels and validators ---

_UNSET = object()  # Sentinel: caller did not provide this argument
_CARRY_FORWARD = object()  # Sentinel: carry forward from previous version (update only)

_VALID_AUTHORITIES = frozenset({"stated", "inferred", "provisional", "inherited", "unknown"})
_VALID_TESTABILITIES = frozenset({"automatable", "observable", "structural", "untestable"})
_VALID_COMPLEXITY_CEILINGS = frozenset({"simple", "moderate", "complex"})
_VALID_DECISION_AUTHORITIES = frozenset({"owner", "ai", "either"})


def _normalize_provisional(authority: Any, provisional_until: Any) -> tuple[Any, Any]:
    """Enforce provisional lifecycle invariants INV-1 through INV-4.

    Returns (authority, provisional_until) after normalization.
    """
    if provisional_until is not None:
        if authority is _UNSET or authority is None:
            authority = "provisional"
        elif authority != "provisional":
            raise ValueError(f"provisional_until requires authority='provisional', got {authority!r}")
    else:
        if authority is not None and authority is not _UNSET and authority == "provisional":
            raise ValueError("authority='provisional' requires provisional_until to be set")
    return authority, provisional_until


def _validate_authority(authority: str) -> None:
    """Validate authority is one of the approved enum values."""
    if authority not in _VALID_AUTHORITIES:
        raise ValueError(f"Invalid authority: {authority!r}. Must be one of {sorted(_VALID_AUTHORITIES)}")


def _validate_testability(testability: str) -> None:
    """Validate testability is one of the approved enum values."""
    if testability not in _VALID_TESTABILITIES:
        raise ValueError(f"Invalid testability: {testability!r}. Must be one of {sorted(_VALID_TESTABILITIES)}")


def _validate_constraints(constraints: Any) -> None:
    """Validate constraints is None or a dict with approved known-key rules."""
    if constraints is None:
        return
    if not isinstance(constraints, dict):
        raise ValueError(f"constraints must be a dict, got {type(constraints).__name__}")
    cc = constraints.get("complexity_ceiling")
    if cc is not None and cc not in _VALID_COMPLEXITY_CEILINGS:
        raise ValueError(
            f"constraints.complexity_ceiling must be one of {sorted(_VALID_COMPLEXITY_CEILINGS)}, got {cc!r}"
        )
    da = constraints.get("decision_authority")
    if da is not None and da not in _VALID_DECISION_AUTHORITIES:
        raise ValueError(
            f"constraints.decision_authority must be one of {sorted(_VALID_DECISION_AUTHORITIES)}, got {da!r}"
        )
    ea = constraints.get("excluded_approaches")
    if ea is not None:
        if not isinstance(ea, list):
            raise ValueError(f"constraints.excluded_approaches must be a list, got {type(ea).__name__}")
        for i, item in enumerate(ea):
            if not isinstance(item, str):
                raise ValueError(f"constraints.excluded_approaches[{i}] must be a string, got {type(item).__name__}")


def _validate_affected_by(affected_by: Any) -> None:
    """Validate affected_by is None or a list of strings."""
    if affected_by is None:
        return
    if not isinstance(affected_by, list):
        raise ValueError(f"affected_by must be a list, got {type(affected_by).__name__}")
    for i, item in enumerate(affected_by):
        if not isinstance(item, str):
            raise ValueError(f"affected_by[{i}] must be a string, got {type(item).__name__}")


def _validate_provisional_until(provisional_until: Any) -> None:
    """Validate provisional_until is None or a non-empty spec ID string."""
    if provisional_until is not None:
        if not isinstance(provisional_until, str) or not provisional_until.strip():
            raise ValueError("provisional_until must be a non-empty string")


class KnowledgeDB:
    """Append-only knowledge database."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        gate_registry: GateRegistry | None = None,
        check_same_thread: bool = True,
        chroma_path: str | Path | None = None,
    ):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._chroma_path = Path(chroma_path) if chroma_path else None
        self._conn: sqlite3.Connection | None = None
        self._gate_registry = gate_registry
        self._check_same_thread = check_same_thread
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=self._check_same_thread,
            )
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

        # Migration 2: Backfill architecture_decision and design_constraint types (GOV-20 Phase 1)
        conn.execute(
            "UPDATE specifications SET type = 'architecture_decision' WHERE id LIKE 'ADR-%' AND type = 'requirement'"
        )
        conn.execute(
            "UPDATE specifications SET type = 'design_constraint' WHERE id LIKE 'DCL-%' AND type = 'requirement'"
        )
        conn.commit()

        # Migration 3: F1 Schema Enrichment — add 5 new columns to specifications
        cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)").fetchall()}
        f1_columns = {
            "authority": "TEXT",
            "provisional_until": "TEXT",
            "constraints": "TEXT",
            "affected_by": "TEXT",
            "testability": "TEXT",
        }
        for col_name, col_type in f1_columns.items():
            if col_name not in cols:
                conn.execute(f"ALTER TABLE specifications ADD COLUMN {col_name} {col_type}")
        conn.commit()

    @staticmethod
    def _auto_detect_spec_type(spec_id: str, declared_type: str) -> str:
        """Auto-detect spec type from ID prefix when declared as default 'requirement'."""
        if declared_type != "requirement":
            return declared_type
        prefix_map = {
            "GOV-": "governance",
            "PB-": "protected_behavior",
            "ADR-": "architecture_decision",
            "DCL-": "design_constraint",
        }
        for prefix, spec_type in prefix_map.items():
            if spec_id.startswith(prefix):
                return spec_type
        return declared_type

    def close(self) -> None:
        """Close the underlying SQLite connection.

        Closes the active SQLite connection and releases it. The connection
        is lazily re-opened on the next database operation, so calling
        ``close()`` does not permanently invalidate the instance. Safe to
        call multiple times — a no-op if no connection is currently open.

        Note: ``close()`` does not touch the ChromaDB client. ChromaDB
        resources are managed separately and are not released by this call.
        """
        if self._conn:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Specifications
    # ------------------------------------------------------------------

    def _next_spec_version(self, spec_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM specifications WHERE id = ?", (spec_id,)).fetchone()
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
        assertions: list[dict[str, Any]] | None = None,
        type: str = "requirement",
        validate_assertions: bool = True,
        authority: Any = _UNSET,
        provisional_until: str | None = None,
        constraints: dict[str, Any] | None = None,
        affected_by: list[str] | None = None,
        testability: str | None = None,
    ) -> dict[str, Any] | None:
        """Insert a new version of a specification.

        Args:
            type: Specification type — 'requirement', 'governance', 'protected_behavior',
                  'architecture_decision', or 'design_constraint'.
                  Auto-detected from ID prefix (GOV-*, PB-*, ADR-*, DCL-*) when left
                  as default 'requirement'.
            validate_assertions: If True (default), validate assertion definitions
                  before writing. Set False only for tested migration tooling.
            authority: Spec authority — 'stated', 'inferred', 'provisional', 'inherited',
                  or 'unknown'. Defaults to 'stated' on new insert when omitted.
            provisional_until: Spec ID this provisional spec is waiting on. Requires
                  authority='provisional' (auto-set if authority omitted).
            constraints: JSON-serializable dict of constraints metadata.
            affected_by: List of spec/ADR/DCL IDs that affect this spec.
            testability: Testability classification — 'automatable', 'observable',
                  'structural', or 'untestable'.
        """
        type = self._auto_detect_spec_type(id, type)

        # Validate assertions at write time
        if validate_assertions and assertions:
            from groundtruth_kb.assertion_schema import validate_assertion_list

            errors = validate_assertion_list(assertions)
            if errors:
                raise ValueError(f"Invalid assertions for {id}: {'; '.join(errors)}")

        # F1: Normalize provisional lifecycle FIRST (while _UNSET preserved)
        authority, provisional_until = _normalize_provisional(authority, provisional_until)
        # F1: Apply new-insert default AFTER normalization
        if authority is _UNSET:
            authority = "stated"
        # F1: Validate enriched fields
        if authority is not None:
            _validate_authority(authority)
        if testability is not None:
            _validate_testability(testability)
        _validate_constraints(constraints)
        _validate_affected_by(affected_by)
        _validate_provisional_until(provisional_until)
        # F1: Serialize JSON fields
        constraints_json = json.dumps(constraints) if constraints is not None else None
        affected_by_json = json.dumps(affected_by) if affected_by is not None else None

        # Run governance gates on initial insert (for status enforcement)
        if self._gate_registry is not None:
            spec_data: dict[str, Any] = {
                "type": type,
                "assertions": json.dumps(assertions) if assertions else None,
                "title": title,
                "status": status,
            }
            if status == "verified":
                spec_data["linked_tests"] = self.get_tests_for_spec(id)
            self._gate_registry.run_pre_promote(id, "new", status, spec_data)
        version = self._next_spec_version(id)
        assertions_json = json.dumps(assertions) if assertions else None
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, type,
                authority, provisional_until, constraints, affected_by, testability,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                description,
                priority,
                scope,
                section,
                handle,
                tags_json,
                status,
                assertions_json,
                type,
                authority,
                provisional_until,
                constraints_json,
                affected_by_json,
                testability,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            self._record_event(
                conn,
                "spec_transition",
                changed_by,
                artifact_id=id,
                artifact_type="spec",
                artifact_version=version,
                metadata={"from_status": "new", "to_status": status, "change_reason": change_reason},
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_spec(id)

    def update_spec(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        *,
        validate_assertions: bool = True,
        **fields: Any,
    ) -> dict[str, Any] | None:
        """Create a new version of a spec, carrying forward unchanged fields.

        F1 enriched fields (authority, provisional_until, constraints, affected_by,
        testability) follow the carry-forward rule: if omitted, the previous version's
        value is preserved. JSON fields (constraints, affected_by) carry forward as raw
        storage strings without re-validation or re-serialization.

        Args:
            validate_assertions: If True (default), validate assertion definitions
                  before writing. Set False only for tested migration tooling.
        """
        current = self.get_spec(id)
        if not current:
            raise ValueError(f"Spec {id} not found")

        # Validate assertions at write time if provided
        if validate_assertions and "assertions" in fields and fields["assertions"] is not None:
            from groundtruth_kb.assertion_schema import validate_assertion_list

            errors = validate_assertion_list(fields["assertions"])
            if errors:
                raise ValueError(f"Invalid assertions for {id}: {'; '.join(errors)}")

        version = self._next_spec_version(id)
        # Merge: new fields override current values
        title = fields.get("title", current["title"])
        description = fields.get("description", current["description"])
        priority = fields.get("priority", current["priority"])
        scope = fields.get("scope", current["scope"])
        section = fields.get("section", current["section"])
        handle = fields.get("handle", current["handle"])
        status = fields.get("status", current["status"])
        spec_type = self._auto_detect_spec_type(id, fields.get("type", current.get("type", "requirement")))

        # Tags and assertions: use module-level _UNSET to allow explicit [] or None
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

        # --- F1: 8-step carry-forward for enriched fields ---
        # Step 1: Already done — current = self.get_spec(id) above

        # Step 2: Extract with sentinels
        authority = fields.get("authority", _UNSET)
        provisional_until = fields.get("provisional_until", _CARRY_FORWARD)
        testability = fields.get("testability", _UNSET)

        # Step 3: Resolve carry-forward BEFORE normalization
        if authority is _UNSET:
            authority = current.get("authority")
        if provisional_until is _CARRY_FORWARD:
            provisional_until = current.get("provisional_until")
        if testability is _UNSET:
            testability = current.get("testability")

        # Step 4: INV-4 — changing authority AWAY from provisional clears provisional_until
        prev_authority = current.get("authority")
        if prev_authority == "provisional" and authority != "provisional" and authority is not None:
            provisional_until = None

        # Step 5: Normalize provisional lifecycle
        authority, provisional_until = _normalize_provisional(authority, provisional_until)

        # Step 6: Default — if still _UNSET after carry-forward, keep None (legacy rows)
        if authority is _UNSET:
            authority = None

        # Step 7: Validate all F1 fields
        if authority is not None:
            _validate_authority(authority)
        if testability is not None:
            _validate_testability(testability)
        _validate_provisional_until(provisional_until)

        # F1 JSON fields: provided → validate + serialize; omitted → raw carry-forward
        if "constraints" in fields:
            constraints_val = fields["constraints"]
            _validate_constraints(constraints_val)
            constraints_raw = json.dumps(constraints_val) if constraints_val is not None else None
        else:
            constraints_raw = current.get("constraints")  # raw JSON string from _row_to_dict

        if "affected_by" in fields:
            affected_by_val = fields["affected_by"]
            _validate_affected_by(affected_by_val)
            affected_by_raw = json.dumps(affected_by_val) if affected_by_val is not None else None
        else:
            affected_by_raw = current.get("affected_by")  # raw JSON string from _row_to_dict

        # Run governance gates before spec promotion
        if self._gate_registry is not None:
            spec_data = {
                "type": spec_type,
                "assertions": assertions_json,
                "title": title,
                "status": status,
            }
            if status == "verified":
                spec_data["linked_tests"] = self.get_tests_for_spec(id)
            self._gate_registry.run_pre_promote(id, current["status"], status, spec_data)

        # Step 8: INSERT new version row with resolved values
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO specifications
               (id, version, title, description, priority, scope, section,
                handle, tags, status, assertions, type,
                authority, provisional_until, constraints, affected_by, testability,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                description,
                priority,
                scope,
                section,
                handle,
                tags_json,
                status,
                assertions_json,
                spec_type,
                authority,
                provisional_until,
                constraints_raw,
                affected_by_raw,
                testability,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            if current["status"] != status:
                self._record_event(
                    conn,
                    "spec_transition",
                    changed_by,
                    artifact_id=id,
                    artifact_type="spec",
                    artifact_version=version,
                    metadata={"from_status": current["status"], "to_status": status, "change_reason": change_reason},
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_spec(id)

    def get_spec(self, spec_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of a specification."""
        row = self._get_conn().execute("SELECT * FROM current_specifications WHERE id = ?", (spec_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_spec_history(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all versions of a specification, newest first."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM specifications WHERE id = ? ORDER BY version DESC",
                (spec_id,),
            )
            .fetchall()
        )
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
        type: str | None = None,
        authority: str | None = None,
        testability: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current specifications with optional filters."""
        query = "SELECT * FROM current_specifications WHERE 1=1"
        params: list[Any] = []
        if type:
            query += " AND type = ?"
            params.append(type)
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
        if authority:
            query += " AND authority = ?"
            params.append(authority)
        if testability:
            query += " AND testability = ?"
            params.append(testability)
        rows = self._get_conn().execute(query, params).fetchall()
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    def get_provisional_specs(self) -> list[dict[str, Any]]:
        """Return current specs where authority='provisional' and provisional_until IS NOT NULL."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM current_specifications WHERE authority = 'provisional' AND provisional_until IS NOT NULL"
            )
            .fetchall()
        )
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    def get_specs_affected_by(self, constraint_id: str) -> list[dict[str, Any]]:
        """Return current specs whose affected_by list contains exactly constraint_id.

        Uses JSON parsing for exact containment — not SQL LIKE substring matching.
        This prevents false positives like 'ADR-1' matching 'ADR-10'.
        """
        rows = self._get_conn().execute("SELECT * FROM current_specifications WHERE affected_by IS NOT NULL").fetchall()
        result = []
        for row in rows:
            d = _row_to_dict(row)
            parsed = d.get("affected_by_parsed")
            if parsed and isinstance(parsed, list) and constraint_id in parsed:
                result.append(d)
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    # --- F3: Spec Quality Gate ---

    def score_spec_quality(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Compute quality score for a single spec.

        Returns dict with overall, d1-d5 dimension scores, tier, and flags.
        Gracefully degrades when F1 fields are absent (adjusts denominators).
        """
        flags: list[str] = []
        assertions = spec.get("assertions_parsed") or spec.get("_assertions_parsed") or []

        # Executable assertion types per assertions.py
        _EXECUTABLE = {"grep", "glob", "grep_absent", "file_exists", "count", "json_path", "all_of", "any_of"}

        has_assertions = bool(assertions)
        has_executable = (
            any(isinstance(a, dict) and a.get("type") in _EXECUTABLE for a in assertions) if has_assertions else False
        )

        if not has_assertions:
            flags.append("NO_ASSERTIONS")
        elif not has_executable:
            flags.append("NO_EXECUTABLE_ASSERTIONS")

        # D1: Clarity
        d1 = 0.0
        title = spec.get("title", "")
        if title and 40 <= len(title) <= 120:
            d1 += 0.2
        if title and any(w in title.lower() for w in ("must", "shall", "should", "requires")):
            d1 += 0.3
        if spec.get("description") and len(spec.get("description", "")) > 50:
            d1 += 0.3
        if spec.get("description") and any(
            w in spec["description"].lower() for w in ("because", "rationale", "reason", "ensures")
        ):
            d1 += 0.2

        # D2: Testability
        d2 = 0.0
        if has_assertions:
            d2 += 0.3
        if has_executable:
            d2 += 0.4
        if has_assertions and any(isinstance(a, dict) and a.get("description") for a in assertions):
            d2 += 0.15
        if has_assertions and any(isinstance(a, dict) and a.get("file") for a in assertions):
            d2 += 0.15
        # F1 bonus: testability field
        if spec.get("testability"):
            d2 = min(1.0, d2 + 0.1)

        # D3: Completeness (dynamic denominator)
        d3_checks = 0
        d3_hits = 0
        for field in ("type", "tags", "section", "scope", "priority", "description"):
            d3_checks += 1
            if spec.get(field):
                d3_hits += 1
        # F1 fields: only count if present in spec dict (graceful degradation)
        for f1_field in ("authority", "constraints", "affected_by"):
            if f1_field in spec:
                d3_checks += 1
                val = spec.get(f1_field)
                if val is not None and val != "" and val != "[]" and val != "{}":
                    d3_hits += 1
        d3 = d3_hits / max(d3_checks, 1)

        # D4: Isolation
        d4 = 0.0
        if spec.get("section"):
            d4 += 0.4
        if spec.get("handle"):
            d4 += 0.3
        if spec.get("affected_by_parsed") or spec.get("_affected_by_parsed"):
            d4 += 0.3

        # D5: Freshness (simplified — based on version existence)
        d5 = 0.5  # Base freshness
        if has_assertions:
            d5 += 0.3
        if spec.get("version", 0) > 1:
            d5 += 0.2
        d5 = min(1.0, d5)

        overall = (d1 + d2 + d3 + d4 + d5) / 5.0

        # Tier classification
        if overall >= 0.8:
            tier = "gold"
        elif overall >= 0.6:
            tier = "silver"
        elif overall >= 0.4:
            tier = "bronze"
        else:
            tier = "needs-work"

        return {
            "overall": round(overall, 4),
            "d1_clarity": round(d1, 4),
            "d2_testability": round(d2, 4),
            "d3_completeness": round(d3, 4),
            "d4_isolation": round(d4, 4),
            "d5_freshness": round(d5, 4),
            "tier": tier,
            "flags": flags,
        }

    def persist_quality_scores(self, session_id: str) -> int:
        """Score all current specs and persist to spec_quality_scores. Returns row count."""
        specs = self.list_specs()
        conn = self._get_conn()
        count = 0
        for spec in specs:
            score = self.score_spec_quality(spec)
            flags_json = json.dumps(score["flags"]) if score["flags"] else None
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO spec_quality_scores
                       (spec_id, spec_version, session_id, scored_at,
                        overall, d1_clarity, d2_testability, d3_completeness,
                        d4_isolation, d5_freshness, tier, flags)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        spec["id"],
                        spec["version"],
                        session_id,
                        _now(),
                        score["overall"],
                        score["d1_clarity"],
                        score["d2_testability"],
                        score["d3_completeness"],
                        score["d4_isolation"],
                        score["d5_freshness"],
                        score["tier"],
                        flags_json,
                    ),
                )
                count += 1
            except Exception:
                pass  # Skip on constraint violations
        conn.commit()
        return count

    def get_quality_history(self, spec_id: str) -> list[dict[str, Any]]:
        """Historical quality scores for a spec, ordered by scored_at DESC."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM spec_quality_scores WHERE spec_id = ? ORDER BY scored_at DESC",
                (spec_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def get_quality_distribution(self) -> dict[str, Any]:
        """Aggregate quality distribution across latest scores per spec.

        Uses rowid as deterministic tie-breaker when multiple scores share
        the same scored_at timestamp for one spec.
        """
        rows = (
            self._get_conn()
            .execute(
                """SELECT tier, COUNT(*) as count, AVG(overall) as avg_score
                   FROM spec_quality_scores sq
                   INNER JOIN (
                       SELECT spec_id, MAX(rowid) as latest_rowid
                       FROM spec_quality_scores GROUP BY spec_id
                   ) latest ON sq.spec_id = latest.spec_id AND sq.rowid = latest.latest_rowid
                   GROUP BY tier"""
            )
            .fetchall()
        )
        dist: dict[str, Any] = {}
        total = 0
        for row in rows:
            d = dict(row)
            dist[d["tier"]] = {"count": d["count"], "avg_score": round(d["avg_score"], 4)}
            total += d["count"]
        dist["total"] = total
        return dist

    # --- F4-A: Constraint Propagation (Phase A — Read-Only) ---

    def _find_matching_constraints(
        self, *, section: str | None = None, scope: str | None = None, tags: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Shared helper: find ADR/DCL specs whose scope overlaps the given criteria."""
        constraints: list[dict[str, Any]] = []
        for ctype in ("architecture_decision", "design_constraint"):
            for spec in self.list_specs(type=ctype):
                match = False
                if section and spec.get("section") and section.lower() in spec["section"].lower():
                    match = True
                if scope and spec.get("scope") and scope.lower() in spec["scope"].lower():
                    match = True
                if tags and spec.get("tags_parsed"):
                    spec_tags = spec["tags_parsed"] if isinstance(spec["tags_parsed"], list) else []
                    if set(tags) & set(spec_tags):
                        match = True
                if match:
                    constraints.append(spec)
        return constraints

    def check_constraints_for_spec(
        self,
        spec_id: str | None = None,
        *,
        section: str | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return ADR/DCL specs whose scope overlaps. Read-only advisory lookup.

        If spec_id is provided, uses that spec's section/scope/tags for matching.
        Otherwise uses the explicit section/scope/tags parameters.
        """
        if spec_id is not None:
            spec = self.get_spec(spec_id)
            if spec:
                section = section or spec.get("section")
                scope = scope or spec.get("scope")
                if tags is None and spec.get("tags_parsed"):
                    tags = spec["tags_parsed"] if isinstance(spec["tags_parsed"], list) else None
        return self._find_matching_constraints(section=section, scope=scope, tags=tags)

    def get_constraint_coverage(self) -> dict[str, Any]:
        """Report: which sections have ADR/DCL coverage and which don't."""
        all_specs = self.list_specs()
        constraint_specs = [s for s in all_specs if s.get("type") in ("architecture_decision", "design_constraint")]

        # Collect sections from all specs
        all_sections: set[str] = set()
        for s in all_specs:
            if s.get("section"):
                all_sections.add(s["section"])

        # Collect sections covered by constraints
        covered_sections: set[str] = set()
        for cs in constraint_specs:
            if cs.get("section"):
                covered_sections.add(cs["section"])

        uncovered = all_sections - covered_sections
        return {
            "total_sections": len(all_sections),
            "covered_sections": sorted(covered_sections),
            "uncovered_sections": sorted(uncovered),
            "coverage_ratio": len(covered_sections) / max(len(all_sections), 1),
            "constraint_count": len(constraint_specs),
        }

    # --- F4-B: Constraint Propagation (Phase B — Linkage Writes) ---

    def _find_specs_for_constraint(self, constraint: dict[str, Any]) -> list[dict[str, Any]]:
        """Inverse of _find_matching_constraints: find functional specs
        whose section/scope/tags overlap with a constraint spec.

        Excludes ADR/DCL peer specs and the source constraint itself.
        """
        c_section = constraint.get("section")
        c_scope = constraint.get("scope")
        c_tags_raw = constraint.get("tags_parsed")
        c_tags = set(c_tags_raw) if isinstance(c_tags_raw, list) else set()
        c_id = constraint.get("id")

        result: list[dict[str, Any]] = []
        for spec in self.list_specs():
            if spec.get("type") in ("architecture_decision", "design_constraint"):
                continue
            if spec["id"] == c_id:
                continue
            match = False
            if c_section and spec.get("section") and spec["section"] == c_section:
                match = True
            if c_scope and spec.get("scope") and spec["scope"] == c_scope:
                match = True
            if c_tags and not match:
                s_tags_raw = spec.get("tags_parsed")
                s_tags = set(s_tags_raw) if isinstance(s_tags_raw, list) else set()
                if c_tags & s_tags:
                    match = True
            if match:
                result.append(spec)
        return result

    def propagate_constraint(
        self,
        constraint_id: str,
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Link a constraint to all matching functional specs via affected_by.

        Each linkage creates a new spec version (append-only).
        """
        constraint = self.get_spec(constraint_id)
        if constraint is None:
            return {"error": f"Constraint {constraint_id} not found"}

        matching = self._find_specs_for_constraint(constraint)
        affected: list[dict[str, Any]] = []
        newly_linked = 0
        already_linked = 0

        for spec in matching:
            current_affected_by = spec.get("affected_by_parsed") or []
            if not isinstance(current_affected_by, list):
                current_affected_by = []

            if constraint_id in current_affected_by:
                affected.append({"id": spec["id"], "title": spec["title"], "action": "already_linked"})
                already_linked += 1
            else:
                if not dry_run:
                    new_affected_by = current_affected_by + [constraint_id]
                    self.update_spec(
                        spec["id"],
                        "constraint-propagation",
                        f"Linked constraint {constraint_id}: {constraint.get('title', '')}",
                        affected_by=new_affected_by,
                    )
                affected.append({"id": spec["id"], "title": spec["title"], "action": "linked"})
                newly_linked += 1

        return {
            "constraint_id": constraint_id,
            "constraint_title": constraint.get("title", ""),
            "dry_run": dry_run,
            "affected_specs": affected,
            "newly_linked": newly_linked,
            "already_linked": already_linked,
        }

    def remove_constraint_link(
        self,
        spec_id: str,
        constraint_id: str,
        *,
        changed_by: str = "constraint-propagation",
        change_reason: str,
    ) -> dict[str, Any]:
        """Remove a constraint from a spec's affected_by list.

        Creates a new spec version (append-only audit trail).
        """
        spec = self.get_spec(spec_id)
        if spec is None:
            return {"spec_id": spec_id, "constraint_id": constraint_id, "removed": False}

        current = spec.get("affected_by_parsed") or []
        if not isinstance(current, list):
            current = []

        if constraint_id not in current:
            return {"spec_id": spec_id, "constraint_id": constraint_id, "removed": False}

        new_affected_by = [x for x in current if x != constraint_id]
        self.update_spec(
            spec_id,
            changed_by,
            change_reason,
            affected_by=new_affected_by if new_affected_by else None,
        )
        return {"spec_id": spec_id, "constraint_id": constraint_id, "removed": True}

    # --- F2-A: Change Impact Analysis (Phase A — Advisory) ---

    def compute_impact(
        self,
        operation: str,
        spec_data: dict[str, Any],
        *,
        config: Any | None = None,
    ) -> dict[str, Any]:
        """Compute advisory change-impact analysis for a specification.

        Args:
            operation: Planned operation — "add", "modify", or "remove".
            spec_data: Spec dict (may or may not be persisted yet).
            config: Optional :class:`~groundtruth_kb.impact.ImpactConfig`.

        Delegates to :func:`groundtruth_kb.impact.compute_impact_analysis`.
        """
        from groundtruth_kb.impact import ImpactConfig, compute_impact_analysis

        if config is not None and not isinstance(config, ImpactConfig):
            msg = f"config must be an ImpactConfig instance, got {type(config).__name__}"
            raise TypeError(msg)
        return compute_impact_analysis(self, operation, spec_data, config=config)

    # --- F7: Session Health Dashboard ---

    def capture_session_snapshot(self, session_id: str) -> dict[str, Any]:
        """Capture a health snapshot of current DB state.

        Uses INSERT OR REPLACE — repeated captures for the same session_id
        replace the previous snapshot (latest-snapshot replacement contract).
        """
        data = {
            "lifecycle_metrics": self.get_lifecycle_metrics(),
            "summary": self.get_summary(),
            "quality_distribution": self.get_quality_distribution(),
            "constraint_coverage": self.get_constraint_coverage(),
            "captured_at": _now(),
        }
        data_json = json.dumps(data)
        self._get_conn().execute(
            "INSERT OR REPLACE INTO session_snapshots (session_id, captured_at, data) VALUES (?, ?, ?)",
            (session_id, data["captured_at"], data_json),
        )
        self._get_conn().commit()
        return {"session_id": session_id, **data}

    def get_session_snapshot(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve a stored snapshot by session ID."""
        row = self._get_conn().execute("SELECT * FROM session_snapshots WHERE session_id = ?", (session_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["data_parsed"] = json.loads(d["data"]) if d.get("data") else {}
        return d

    def get_snapshot_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve recent snapshots ordered by latest write.

        Uses ``(captured_at DESC, rowid DESC)`` so same-second captures
        resolve deterministically to latest-write-wins.
        """
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM session_snapshots ORDER BY captured_at DESC, rowid DESC LIMIT ?",
                (limit,),
            )
            .fetchall()
        )
        result = []
        for row in rows:
            d = dict(row)
            d["data_parsed"] = json.loads(d["data"]) if d.get("data") else {}
            result.append(d)
        return result

    def compute_session_delta(self, current_session: str | None = None) -> dict[str, Any]:
        """Compute health metric deltas.

        When current_session is None: compares live DB state with the most
        recent stored snapshot.
        When current_session is provided: compares that snapshot with the
        previous one.
        """
        if current_session is None:
            # Live state vs last snapshot
            current_data = {
                "lifecycle_metrics": self.get_lifecycle_metrics(),
                "summary": self.get_summary(),
                "quality_distribution": self.get_quality_distribution(),
                "constraint_coverage": self.get_constraint_coverage(),
            }
            history = self.get_snapshot_history(limit=1)
            if not history:
                return {"current": current_data, "previous": None, "deltas": {}, "no_prior": True}
            previous_data = history[0].get("data_parsed", {})
        else:
            snap = self.get_session_snapshot(current_session)
            if snap is None:
                return {"current": None, "previous": None, "deltas": {}, "no_prior": True}
            current_data = snap.get("data_parsed", {})
            # Find the snapshot just before this one (by rowid, not timestamp,
            # to handle same-second captures deterministically)
            rows = (
                self._get_conn()
                .execute(
                    "SELECT * FROM session_snapshots WHERE rowid < (SELECT rowid FROM session_snapshots WHERE session_id = ?) ORDER BY rowid DESC LIMIT 1",
                    (current_session,),
                )
                .fetchall()
            )
            if not rows:
                return {"current": current_data, "previous": None, "deltas": {}, "no_prior": True}
            prev = dict(rows[0])
            previous_data = json.loads(prev["data"]) if prev.get("data") else {}

        # Compute deltas for lifecycle metrics
        deltas: dict[str, Any] = {}
        cur_metrics = current_data.get("lifecycle_metrics", {})
        prev_metrics = previous_data.get("lifecycle_metrics", {})
        for key in cur_metrics:
            cur_val = cur_metrics[key].get("value") if isinstance(cur_metrics[key], dict) else None
            prev_val = prev_metrics.get(key, {}).get("value") if isinstance(prev_metrics.get(key), dict) else None
            if cur_val is not None and prev_val is not None:
                try:
                    deltas[key] = round(float(cur_val) - float(prev_val), 6)
                except (TypeError, ValueError):
                    pass

        return {"current": current_data, "previous": previous_data, "deltas": deltas, "no_prior": False}

    def list_children(self, parent_id: str) -> list[dict[str, Any]]:
        """List current specs that are direct or nested children of parent_id.

        E.g., parent_id="245" returns 245.1, 245.2, 245.1.1, etc.
        """
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM current_specifications WHERE id LIKE ?",
                (f"{parent_id}.%",),
            )
            .fetchall()
        )
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
        row = self._get_conn().execute("SELECT MAX(version) FROM test_procedures WHERE id = ?", (proc_id,)).fetchone()
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
    ) -> dict[str, Any] | None:
        """Insert a new version of a test procedure into the knowledge database.

        Test procedures are append-only — each call creates a new version row
        keyed by ``id``. The latest version is exposed via ``get_test_procedure``.

        Args:
            id: Unique test procedure identifier (e.g. ``"TP-001"``).
            title: Short descriptive title.
            changed_by: Actor responsible for this version.
            change_reason: Human-readable rationale for the change.
            type: Optional procedure type classification.
            content: Full procedure content or script text.
            assertion_count: Number of assertions in the procedure.
            last_execution_status: Result of the most recent execution
                (e.g. ``"pass"``, ``"fail"``).
            last_executed_at: ISO-8601 timestamp of the most recent execution.

        Returns:
            The newly inserted version as a dict. Schema mirrors the
            ``test_procedures`` table row, with JSON fields pre-parsed.
        """
        version = self._next_test_proc_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO test_procedures
               (id, version, title, type, content, assertion_count,
                last_execution_status, last_executed_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                type,
                content,
                assertion_count,
                last_execution_status,
                last_executed_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_test_procedure(id)

    def get_test_procedure(self, proc_id: str) -> dict[str, Any] | None:
        """Return the latest version of a test procedure, or None if not found.

        Args:
            proc_id: Test procedure identifier (e.g. ``"TP-001"``).

        Returns:
            A dict of the current test procedure row with JSON fields pre-parsed,
            or ``None`` if no procedure with that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_test_procedures WHERE id = ?", (proc_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_procedure_history(self, proc_id: str) -> list[dict[str, Any]]:
        """Return all versions of a test procedure, newest-first.

        Args:
            proc_id: Test procedure identifier (e.g. ``"TP-001"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no procedure with that ID exists.
        """
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM test_procedures WHERE id = ? ORDER BY version DESC",
                (proc_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def list_test_procedures(self, *, type: str | None = None) -> list[dict[str, Any]]:
        """List all current test procedures, optionally filtered by type.

        Args:
            type: Optional type filter. When provided, returns only procedures
                with a matching ``type`` value.

        Returns:
            A list of test procedure dicts ordered by ``id``. Returns an
            empty list if no matching procedures exist.
        """
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
        row = (
            self._get_conn()
            .execute("SELECT MAX(version) FROM operational_procedures WHERE id = ?", (proc_id,))
            .fetchone()
        )
        return (row[0] or 0) + 1

    def insert_op_procedure(
        self,
        id: str,
        title: str,
        changed_by: str,
        change_reason: str,
        *,
        type: str | None = None,
        variables: dict[str, Any] | None = None,
        steps: list[dict[str, Any]] | None = None,
        known_failure_modes: list[dict[str, Any]] | None = None,
        last_verified_at: str | None = None,
        last_corrected_at: str | None = None,
    ) -> dict[str, Any] | None:
        """Insert a new version of an operational procedure into the knowledge database.

        Operational procedures are append-only — each call creates a new version
        row keyed by ``id``. The latest version is exposed via ``get_op_procedure``.
        JSON fields (``variables``, ``steps``, ``known_failure_modes``) are
        serialized automatically.

        Args:
            id: Unique operational procedure identifier (e.g. ``"OP-001"``).
            title: Short descriptive title.
            changed_by: Actor responsible for this version.
            change_reason: Human-readable rationale for the change.
            type: Optional procedure type classification.
            variables: Optional dict of named variables used by the procedure steps.
            steps: Optional list of step dicts describing the procedure steps.
            known_failure_modes: Optional list of dicts documenting known failure
                modes and their mitigations.
            last_verified_at: ISO-8601 timestamp of the most recent verification.
            last_corrected_at: ISO-8601 timestamp of the most recent correction.

        Returns:
            The newly inserted version as a dict. Schema mirrors the
            ``operational_procedures`` table row, with JSON fields pre-parsed.
        """
        version = self._next_op_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO operational_procedures
               (id, version, title, type, variables, steps, known_failure_modes,
                last_verified_at, last_corrected_at,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                type,
                json.dumps(variables) if variables else None,
                json.dumps(steps) if steps else None,
                json.dumps(known_failure_modes) if known_failure_modes else None,
                last_verified_at,
                last_corrected_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_op_procedure(id)

    def get_op_procedure(self, proc_id: str) -> dict[str, Any] | None:
        """Return the latest version of an operational procedure, or None if not found.

        Args:
            proc_id: Operational procedure identifier (e.g. ``"OP-001"``).

        Returns:
            A dict of the current operational procedure row with JSON fields
            (``variables``, ``steps``, ``known_failure_modes``) pre-parsed,
            or ``None`` if no procedure with that ID exists.
        """
        row = (
            self._get_conn().execute("SELECT * FROM current_operational_procedures WHERE id = ?", (proc_id,)).fetchone()
        )
        return _row_to_dict(row) if row else None

    def get_op_procedure_history(self, proc_id: str) -> list[dict[str, Any]]:
        """Return all versions of an operational procedure, newest-first.

        Args:
            proc_id: Operational procedure identifier (e.g. ``"OP-001"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no procedure with that ID exists.
        """
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM operational_procedures WHERE id = ? ORDER BY version DESC",
                (proc_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def list_op_procedures(self, *, type: str | None = None) -> list[dict[str, Any]]:
        """List all current operational procedures, optionally filtered by type.

        Args:
            type: Optional type filter. When provided, returns only procedures
                with a matching ``type`` value.

        Returns:
            A list of operational procedure dicts ordered by ``id``. Returns an
            empty list if no matching procedures exist.
        """
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
        row = (
            self._get_conn()
            .execute("SELECT MAX(version) FROM environment_config WHERE id = ?", (config_id,))
            .fetchone()
        )
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
    ) -> dict[str, Any] | None:
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
            (id, version, environment, category, key, value, int(sensitive), notes, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_env_config(id)

    def update_env_config(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
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
            (id, version, environment, category, key, value, int(sensitive), notes, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_env_config(id)

    def get_env_config(self, config_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of an environment config entry."""
        row = self._get_conn().execute("SELECT * FROM current_environment_config WHERE id = ?", (config_id,)).fetchone()
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
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM environment_config WHERE id = ? ORDER BY version DESC",
                (config_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def _next_doc_version(self, doc_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM documents WHERE id = ?", (doc_id,)).fetchone()
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
    ) -> dict[str, Any] | None:
        """Insert a new version of a document."""
        version = self._next_doc_version(id)
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO documents
               (id, version, title, category, content, tags, status,
                source_path, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id, version, title, category, content, tags_json, status, source_path, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_document(id)

    def update_document(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
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
            (id, version, title, category, content, tags_json, status, source_path, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_document(id)

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Return the latest version of a document, or None if not found.

        Args:
            doc_id: Document identifier (e.g. ``"DOC-001"``).

        Returns:
            A dict of the current document row with JSON fields pre-parsed,
            or ``None`` if no document with that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_documents WHERE id = ?", (doc_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_documents(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, Any]]:
        """List all current documents, optionally filtered by category, status, or tag.

        Args:
            category: Optional category filter (e.g. ``"implementation_proposal"``).
            status: Optional status filter (e.g. ``"published"``).
            tag: Optional tag filter. Matches documents where the ``tags`` JSON
                array contains an element equal to ``tag``.

        Returns:
            A list of document dicts ordered by ``id``. Returns an empty list
            if no matching documents exist.
        """
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
    # GOV-20: Architecture Decision Governance helpers
    # ------------------------------------------------------------------

    def list_design_constraints(self, *, status: str | None = None) -> list[dict[str, Any]]:
        """List all current design constraint specs (DCL-*)."""
        return self.list_specs(type="design_constraint", status=status)

    def validate_dcl_constraints(
        self,
        dcl_id: str | None = None,
        project_root: Path | None = None,
    ) -> list[dict[str, Any]]:
        """Validate design constraint assertions against the codebase.

        If dcl_id is provided, validates only that constraint.
        Otherwise validates all implemented/verified DCL-* specs with assertions.

        Args:
            dcl_id: Optional single DCL spec ID to validate.
            project_root: Project root for file resolution. Falls back to cwd.

        Returns list of {dcl_id, title, passed, results: [...]} dicts.
        """
        from groundtruth_kb.assertions import run_single_assertion

        if project_root is None:
            project_root = Path.cwd()

        if dcl_id:
            spec = self.get_spec(dcl_id)
            if not spec:
                return [{"dcl_id": dcl_id, "error": f"DCL {dcl_id} not found"}]
            specs: list[dict[str, Any]] = [spec]
        else:
            specs = self.list_design_constraints(status="implemented")
            specs += self.list_design_constraints(status="verified")

        results = []
        for spec in specs:
            if not spec or not spec.get("assertions"):
                continue
            assertion_list = (
                json.loads(spec["assertions"]) if isinstance(spec["assertions"], str) else spec["assertions"]
            )
            spec_results = []
            all_passed = True
            for assertion in assertion_list:
                r = run_single_assertion(assertion, project_root)
                spec_results.append(r)
                if not r.get("passed") and not r.get("skipped"):
                    all_passed = False
            results.append(
                {
                    "dcl_id": spec["id"],
                    "title": spec["title"],
                    "passed": all_passed,
                    "results": spec_results,
                }
            )
        return results

    def list_implementation_proposals(self, *, wi_id: str | None = None) -> list[dict[str, Any]]:
        """List IPR-* documents (implementation proposals). Optionally filter by WI reference."""
        docs = self.list_documents(category="implementation_proposal")
        if wi_id:
            docs = [d for d in docs if wi_id in (d.get("content") or "")]
        return docs

    def list_constraint_verifications(self, *, wi_id: str | None = None) -> list[dict[str, Any]]:
        """List CVR-* documents (constraint verifications). Optionally filter by WI reference."""
        docs = self.list_documents(category="constraint_verification")
        if wi_id:
            docs = [d for d in docs if wi_id in (d.get("content") or "")]
        return docs

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
            (spec_id, test_file, test_class, test_function, confidence, match_reason, _now(), created_by),
        )
        conn.commit()

    def insert_test_coverage_batch(
        self,
        mappings: list[dict[str, Any]],
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
                (
                    m["spec_id"],
                    m["test_file"],
                    m.get("test_class"),
                    m["test_function"],
                    m.get("confidence", "high"),
                    m.get("match_reason"),
                    _now(),
                    created_by,
                ),
            )
            count += 1
        conn.commit()
        return count

    def get_test_coverage_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all test mappings for a spec."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM test_coverage WHERE spec_id = ? ORDER BY test_file, test_function",
                (spec_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def get_test_coverage_summary(self) -> dict[str, Any]:
        """Get coverage statistics."""
        conn = self._get_conn()
        total_mappings = conn.execute("SELECT COUNT(*) FROM test_coverage").fetchone()[0]
        specs_covered = conn.execute("SELECT COUNT(DISTINCT spec_id) FROM test_coverage").fetchone()[0]
        tests_mapped = conn.execute(
            "SELECT COUNT(DISTINCT test_file || ':' || test_function) FROM test_coverage"
        ).fetchone()[0]
        by_confidence = dict(
            conn.execute("SELECT confidence, COUNT(*) FROM test_coverage GROUP BY confidence").fetchall()
        )
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
        row = self._get_conn().execute("SELECT MAX(version) FROM tests WHERE id = ?", (test_id,)).fetchone()
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
    ) -> dict[str, Any] | None:
        """Insert a new version of a test artifact.

        Args:
            id: Unique identifier (e.g., "TEST-0001").
            spec_id: The specification this test verifies (required).
            test_type: 'unit', 'integration', 'e2e', 'manual', or 'assertion'.
            expected_outcome: What constitutes PASS — stated in human-readable terms.
        """
        # Run governance gates on test pass
        if last_result == "pass" and self._gate_registry is not None:
            test_data = {"test_type": test_type, "test_file": test_file, "spec_id": spec_id}
            self._gate_registry.run_pre_test_pass(id, spec_id, test_file, test_data)
        version = self._next_test_version(id)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO tests
               (id, version, title, spec_id, test_type, test_file, test_class,
                test_function, description, expected_outcome, last_result,
                last_executed_at, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                spec_id,
                test_type,
                test_file,
                test_class,
                test_function,
                description,
                expected_outcome,
                last_result,
                last_executed_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            self._record_event(
                conn,
                "test_created",
                changed_by,
                artifact_id=id,
                artifact_type="test",
                artifact_version=version,
                metadata={
                    "spec_id": spec_id,
                    "test_type": test_type,
                    "test_file": test_file,
                    "last_result": last_result,
                    "last_executed_at": last_executed_at,
                },
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_test(id)

    def update_test(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
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
        # Run governance gates on test pass
        if last_result == "pass" and self._gate_registry is not None:
            test_data = {"test_type": test_type, "test_file": test_file, "spec_id": spec_id}
            self._gate_registry.run_pre_test_pass(id, spec_id, test_file, test_data)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO tests
               (id, version, title, spec_id, test_type, test_file, test_class,
                test_function, description, expected_outcome, last_result,
                last_executed_at, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                spec_id,
                test_type,
                test_file,
                test_class,
                test_function,
                description,
                expected_outcome,
                last_result,
                last_executed_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            result_changed = last_result != current["last_result"]
            executed_changed = last_executed_at != current["last_executed_at"]
            if result_changed or executed_changed:
                self._record_event(
                    conn,
                    "test_executed",
                    changed_by,
                    artifact_id=id,
                    artifact_type="test",
                    artifact_version=version,
                    metadata={
                        "spec_id": spec_id,
                        "test_type": test_type,
                        "test_file": test_file,
                        "previous_last_result": current["last_result"],
                        "last_result": last_result,
                        "previous_last_executed_at": current["last_executed_at"],
                        "last_executed_at": last_executed_at,
                    },
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_test(id)

    def get_test(self, test_id: str) -> dict[str, Any] | None:
        """Return the latest version of a test artifact, or None if not found.

        Args:
            test_id: Test artifact identifier (e.g. ``"TEST-0001"``).

        Returns:
            A dict of the current test row with JSON fields pre-parsed,
            or ``None`` if no test with that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_tests WHERE id = ?", (test_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_history(self, test_id: str) -> list[dict[str, Any]]:
        """Return all versions of a test artifact, newest-first.

        Args:
            test_id: Test artifact identifier (e.g. ``"TEST-0001"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no test with that ID exists.
        """
        rows = self._get_conn().execute("SELECT * FROM tests WHERE id = ? ORDER BY version DESC", (test_id,)).fetchall()
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
        """Get specifications that have no tests linked to them (excludes retired)."""
        rows = (
            self._get_conn()
            .execute(
                """SELECT s.* FROM current_specifications s
               LEFT JOIN current_tests t ON t.spec_id = s.id
               WHERE t.id IS NULL AND s.status != 'retired'
               ORDER BY s.id"""
            )
            .fetchall()
        )
        result = [_row_to_dict(r) for r in rows]
        result.sort(key=lambda r: spec_sort_key(r["id"]))
        return result

    # ------------------------------------------------------------------
    # Test Plans
    # ------------------------------------------------------------------

    def _next_plan_version(self, plan_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM test_plans WHERE id = ?", (plan_id,)).fetchone()
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
    ) -> dict[str, Any] | None:
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
            (id, version, title, description, status, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan(id)

    def update_test_plan(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
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
            (id, version, title, description, status, changed_by, _now(), change_reason),
        )
        conn.commit()
        return self.get_test_plan(id)

    def get_test_plan(self, plan_id: str) -> dict[str, Any] | None:
        """Return the latest version of a test plan, or None if not found.

        Args:
            plan_id: Test plan identifier (e.g. ``"PLAN-001"``).

        Returns:
            A dict of the current test plan row with JSON fields pre-parsed,
            or ``None`` if no test plan with that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_test_plans WHERE id = ?", (plan_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_test_plan_history(self, plan_id: str) -> list[dict[str, Any]]:
        """Return all versions of a test plan, newest-first.

        Args:
            plan_id: Test plan identifier (e.g. ``"PLAN-001"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no test plan with that ID exists.
        """
        rows = (
            self._get_conn()
            .execute("SELECT * FROM test_plans WHERE id = ? ORDER BY version DESC", (plan_id,))
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def list_test_plans(self, *, status: str | None = None) -> list[dict[str, Any]]:
        """List all current test plans, optionally filtered by status.

        Args:
            status: Optional status filter (e.g. ``"active"``, ``"draft"``,
                ``"retired"``). When provided, returns only plans with a
                matching ``status`` value.

        Returns:
            A list of test plan dicts ordered by ``id``. Returns an empty
            list if no matching test plans exist.
        """
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
        row = self._get_conn().execute("SELECT MAX(version) FROM test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
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
    ) -> dict[str, Any] | None:
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
            (
                id,
                version,
                plan_id,
                phase_order,
                title,
                description,
                gate_criteria,
                test_ids_json,
                last_result,
                last_executed_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_test_plan_phase(id)

    def update_test_plan_phase(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
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
            (
                id,
                version,
                plan_id,
                phase_order,
                title,
                description,
                gate_criteria,
                test_ids_json,
                last_result,
                last_executed_at,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_test_plan_phase(id)

    def get_test_plan_phase(self, phase_id: str) -> dict[str, Any] | None:
        """Return the latest version of a test plan phase, or None if not found.

        Args:
            phase_id: Test plan phase identifier (e.g. ``"PLAN-001-P1"``).

        Returns:
            A dict of the current test plan phase row with JSON fields
            (e.g. ``test_ids``) pre-parsed, or ``None`` if no phase with
            that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_test_plan_phases(self, plan_id: str) -> list[dict[str, Any]]:
        """List current phases for a test plan, ordered by phase_order."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM current_test_plan_phases WHERE plan_id = ? ORDER BY phase_order",
                (plan_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Work Items
    # ------------------------------------------------------------------

    def _next_work_item_version(self, item_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM work_items WHERE id = ?", (item_id,)).fetchone()
        return (row[0] or 0) + 1

    # Valid stage transitions: created → tested → backlogged → implementing → resolved
    _VALID_STAGE_TRANSITIONS: dict[str, set[str]] = {
        "created": {"tested", "resolved"},
        "tested": {"backlogged", "resolved"},
        "backlogged": {"implementing", "resolved"},
        "implementing": {"resolved"},
        "resolved": {"resolved"},  # idempotent
    }

    def _validate_stage_transition(
        self,
        wi_id: str,
        current_stage: str,
        new_stage: str,
        *,
        owner_approved: bool = False,
    ) -> None:
        """Enforce valid work item stage transitions per SPEC-1602."""
        if new_stage == current_stage:
            return  # no-op
        valid = self._VALID_STAGE_TRANSITIONS.get(current_stage, set())
        if new_stage not in valid:
            raise ValueError(
                f"Invalid stage transition for {wi_id}: "
                f"'{current_stage}' → '{new_stage}'. "
                f"Valid transitions from '{current_stage}': {sorted(valid)}"
            )
        # Structural guards: tested requires linked test, implementing requires backlog
        if new_stage == "tested":
            if not self._wi_has_linked_test(wi_id):
                raise ValueError(
                    f"Cannot advance {wi_id} to 'tested': no linked test found. "
                    f"Create a test linked to this WI's source_spec_id first (GOV-12)."
                )
        if new_stage == "implementing":
            if not self._wi_in_backlog(wi_id):
                raise ValueError(
                    f"Cannot advance {wi_id} to 'implementing': not found in any "
                    f"backlog snapshot. Add to backlog first."
                )
        # Run governance gates before WI resolution
        if new_stage == "resolved" and self._gate_registry is not None:
            wi = self.get_work_item(wi_id)
            if wi:
                self._gate_registry.run_pre_resolve_work_item(
                    wi_id,
                    wi.get("origin", ""),
                    "resolved",
                    owner_approved,
                    wi,
                )

    def _wi_has_linked_test(self, wi_id: str) -> bool:
        """Check if a work item has a linked test via its source_spec_id."""
        wi = self.get_work_item(wi_id)
        if not wi or not wi.get("source_spec_id"):
            return False
        tests = self.get_tests_for_spec(wi["source_spec_id"])
        return len(tests) > 0

    def _wi_in_backlog(self, wi_id: str) -> bool:
        """Check if a work item ID appears in any backlog snapshot description."""
        rows = self._get_conn().execute("SELECT description FROM current_backlog_snapshots").fetchall()
        for row in rows:
            if row[0] and wi_id in row[0]:
                return True
        return False

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
        stage: str = "created",
    ) -> dict[str, Any] | None:
        """Insert a new version of a work item.

        Args:
            origin: 'regression', 'defect', 'new', or 'hygiene'.
            component: From the component taxonomy (e.g., 'agent_implementation', 'customer_interface').
            resolution_status: 'open', 'in_progress', 'resolved', or 'verified'.
            stage: Lifecycle stage — 'created', 'tested', 'backlogged', 'implementing', or 'resolved'.
                   Defaults to 'created'. For resolved WIs, pass stage='resolved'.
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
                resolution_status, priority, stage,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                description,
                origin,
                component,
                source_spec_id,
                source_test_id,
                failure_description,
                resolution_status,
                priority,
                stage,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            self._record_event(
                conn,
                "wi_created",
                changed_by,
                artifact_id=id,
                artifact_type="work_item",
                artifact_version=version,
                metadata={
                    "origin": origin,
                    "component": component,
                    "priority": priority,
                    "resolution_status": resolution_status,
                    "stage": stage,
                    "source_spec_id": source_spec_id,
                    "source_test_id": source_test_id,
                },
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_work_item(id)

    def update_work_item(
        self,
        id: str,
        changed_by: str,
        change_reason: str,
        *,
        owner_approved: bool = False,
        **fields: Any,
    ) -> dict[str, Any] | None:
        """Create a new version of a work item, carrying forward unchanged fields.

        Stage transitions are enforced per SPEC-1602:
        created → tested → backlogged → implementing → resolved.
        Any stage can transition to 'resolved' (early closure).

        Args:
            owner_approved: Required ``True`` for resolving defect/regression
                WIs (GOV-15 enforcement).  The caller must have received
                explicit owner approval in the conversation before setting this.
        """
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
        current_stage = current.get("stage", "created")
        new_stage = fields.get("stage", current_stage)
        # Enforce stage transitions (includes GOV-15 owner approval gate)
        self._validate_stage_transition(
            id,
            current_stage,
            new_stage,
            owner_approved=owner_approved,
        )
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO work_items
               (id, version, title, description, origin, component,
                source_spec_id, source_test_id, failure_description,
                resolution_status, priority, stage,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                title,
                description,
                origin,
                component,
                source_spec_id,
                source_test_id,
                failure_description,
                resolution_status,
                priority,
                new_stage,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        try:
            actually_resolving = resolution_status == "resolved" and current["resolution_status"] != "resolved"
            if actually_resolving:
                self._record_event(
                    conn,
                    "wi_resolved",
                    changed_by,
                    artifact_id=id,
                    artifact_type="work_item",
                    artifact_version=version,
                    metadata={
                        "origin": origin,
                        "component": component,
                        "priority": priority,
                        "resolution_status": resolution_status,
                        "stage": new_stage,
                        "previous_resolution_status": current["resolution_status"],
                        "previous_stage": current.get("stage"),
                        "source_spec_id": source_spec_id,
                        "source_test_id": source_test_id,
                    },
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.get_work_item(id)

    def get_work_item(self, item_id: str) -> dict[str, Any] | None:
        """Return the latest version of a work item, or None if not found.

        Args:
            item_id: Work item identifier (e.g. ``"WI-0042"``).

        Returns:
            A dict of the current work item row with JSON fields pre-parsed,
            or ``None`` if no work item with that ID exists.
        """
        row = self._get_conn().execute("SELECT * FROM current_work_items WHERE id = ?", (item_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_work_item_history(self, item_id: str) -> list[dict[str, Any]]:
        """Return all versions of a work item, newest-first.

        Args:
            item_id: Work item identifier (e.g. ``"WI-0042"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no work item with that ID exists.
        """
        rows = (
            self._get_conn()
            .execute("SELECT * FROM work_items WHERE id = ? ORDER BY version DESC", (item_id,))
            .fetchall()
        )
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
        rows = (
            self._get_conn()
            .execute(
                """SELECT * FROM current_work_items
               WHERE resolution_status != 'verified'
               ORDER BY priority, id"""
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Backlog Snapshots
    # ------------------------------------------------------------------

    def _next_backlog_version(self, snapshot_id: str) -> int:
        row = (
            self._get_conn()
            .execute("SELECT MAX(version) FROM backlog_snapshots WHERE id = ?", (snapshot_id,))
            .fetchone()
        )
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
        summary_by_origin: dict[str, Any] | None = None,
        summary_by_component: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
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
            (
                id,
                version,
                title,
                description,
                snapshot_at or _now(),
                json.dumps(work_item_ids),
                json.dumps(summary_by_origin) if summary_by_origin else None,
                json.dumps(summary_by_component) if summary_by_component else None,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_backlog_snapshot(id)

    def get_backlog_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        """Return the latest version of a backlog snapshot, or None if not found.

        Args:
            snapshot_id: Backlog snapshot identifier (e.g. ``"SNAP-001"``).

        Returns:
            A dict of the current backlog snapshot row with JSON fields
            (``work_item_ids``, ``summary_by_origin``, ``summary_by_component``)
            pre-parsed, or ``None`` if no snapshot with that ID exists.
        """
        row = (
            self._get_conn().execute("SELECT * FROM current_backlog_snapshots WHERE id = ?", (snapshot_id,)).fetchone()
        )
        return _row_to_dict(row) if row else None

    def get_backlog_snapshot_history(self, snapshot_id: str) -> list[dict[str, Any]]:
        """Return all versions of a backlog snapshot, newest-first.

        Args:
            snapshot_id: Backlog snapshot identifier (e.g. ``"SNAP-001"``).

        Returns:
            A list of version dicts ordered by ``version DESC``. Returns an
            empty list if no snapshot with that ID exists.
        """
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM backlog_snapshots WHERE id = ? ORDER BY version DESC",
                (snapshot_id,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def list_backlog_snapshots(self, *, limit: int = 20) -> list[dict[str, Any]]:
        """List backlog snapshots, most recent first."""
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM current_backlog_snapshots ORDER BY snapshot_at DESC LIMIT ?",
                (limit,),
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def create_backlog_snapshot_from_current(
        self,
        snapshot_id: str,
        changed_by: str,
        change_reason: str,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any] | None:
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
        results: list[dict[str, Any]],
        triggered_by: str,
    ) -> None:
        """Record the result of an assertion run for a specification.

        Inserts a row into ``assertion_runs`` capturing which spec version was
        tested, whether all assertions passed, and the per-assertion details.
        Also records a ``pipeline_event`` for audit purposes.

        Args:
            spec_id: The specification ID that was asserted (e.g. ``"SPEC-1234"``).
            spec_version: The spec version number that was evaluated.
            overall_passed: ``True`` if every assertion passed; ``False`` if any failed.
            results: List of per-assertion result dicts from the assertion runner.
            triggered_by: Actor or process that initiated the assertion run
                (e.g. ``"session-start-hook"``).
        """
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO assertion_runs
               (spec_id, spec_version, run_at, overall_passed, results, triggered_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (spec_id, spec_version, _now(), int(overall_passed), json.dumps(results), triggered_by),
        )
        try:
            self._record_event(
                conn,
                "assertion_run",
                triggered_by,
                artifact_id=spec_id,
                artifact_type="spec",
                artifact_version=spec_version,
                metadata={"overall_passed": overall_passed, "triggered_by": triggered_by, "result_count": len(results)},
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def get_latest_assertion_run(self, spec_id: str) -> dict[str, Any] | None:
        """Return the most recent assertion run for a specification, or None if none exist.

        Args:
            spec_id: The specification ID to look up (e.g. ``"SPEC-1234"``).

        Returns:
            A dict of the most recent assertion run row (including ``results`` as
            a pre-parsed list), or ``None`` if no assertion runs have been
            recorded for this spec.
        """
        row = (
            self._get_conn()
            .execute(
                """SELECT * FROM assertion_runs
               WHERE spec_id = ? ORDER BY rowid DESC LIMIT 1""",
                (spec_id,),
            )
            .fetchone()
        )
        return _row_to_dict(row) if row else None

    def get_all_latest_assertion_runs(self) -> list[dict[str, Any]]:
        """Get the most recent assertion run for each spec."""
        rows = (
            self._get_conn()
            .execute(
                """SELECT a.* FROM assertion_runs a
               INNER JOIN (
                   SELECT spec_id, MAX(rowid) AS max_rowid
                   FROM assertion_runs GROUP BY spec_id
               ) m ON a.spec_id = m.spec_id AND a.rowid = m.max_rowid
               ORDER BY a.spec_id"""
            )
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Session Prompts
    # ------------------------------------------------------------------

    def _next_session_prompt_version(self, session_id: str) -> int:
        row = (
            self._get_conn()
            .execute(
                "SELECT MAX(version) FROM session_prompts WHERE session_id = ?",
                (session_id,),
            )
            .fetchone()
        )
        return (row[0] or 0) + 1

    def insert_session_prompt(
        self,
        session_id: str,
        prompt_text: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
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
            (session_id, version, _now(), prompt_text, json.dumps(context) if context else None),
        )
        conn.commit()
        return self.get_session_prompt(session_id)

    def get_session_prompt(self, session_id: str) -> dict[str, Any] | None:
        """Get the latest event for a specific session's handoff prompt."""
        row = (
            self._get_conn()
            .execute(
                """SELECT * FROM session_prompts
               WHERE session_id = ? ORDER BY rowid DESC LIMIT 1""",
                (session_id,),
            )
            .fetchone()
        )
        return _row_to_dict(row) if row else None

    def get_next_session_prompt(self) -> dict[str, Any] | None:
        """Get the latest unconsumed handoff prompt.

        A prompt is unconsumed if its most recent event is 'created' (not 'consumed').
        Returns the most recently created prompt that hasn't been consumed.
        """
        # Find session_ids whose latest event is 'created'
        row = (
            self._get_conn()
            .execute(
                """SELECT p.* FROM session_prompts p
               INNER JOIN (
                   SELECT session_id, MAX(rowid) AS max_rowid
                   FROM session_prompts GROUP BY session_id
               ) m ON p.session_id = m.session_id AND p.rowid = m.max_rowid
               WHERE p.event_type = 'created'
               ORDER BY p.rowid DESC LIMIT 1"""
            )
            .fetchone()
        )
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
            (session_id, version, _now(), current.get("prompt_text", ""), current.get("context")),
        )
        conn.commit()

    def list_session_prompts(self, *, include_consumed: bool = False) -> list[dict[str, Any]]:
        """List session prompts, optionally including consumed ones."""
        if include_consumed:
            rows = self._get_conn().execute("SELECT * FROM session_prompts ORDER BY rowid DESC").fetchall()
        else:
            # Only show sessions whose latest event is 'created'
            rows = (
                self._get_conn()
                .execute(
                    """SELECT p.* FROM session_prompts p
                   INNER JOIN (
                       SELECT session_id, MAX(rowid) AS max_rowid
                       FROM session_prompts GROUP BY session_id
                   ) m ON p.session_id = m.session_id AND p.rowid = m.max_rowid
                   WHERE p.event_type = 'created'
                   ORDER BY p.rowid DESC"""
                )
                .fetchall()
            )
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
    # Quality Scores (SPEC-1838)
    # ------------------------------------------------------------------

    def insert_quality_score(
        self,
        session_id: str,
        spec_coverage: float,
        defect_escape_rate: float,
        assertion_strength: float,
        change_failure_rate: float,
        test_freshness: float,
        coverage_delta: float,
        composite_score: float,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert a quality score record for a session."""
        conn = self._get_conn()
        now = _now()
        conn.execute(
            """INSERT OR REPLACE INTO quality_scores
               (session_id, computed_at, spec_coverage, defect_escape_rate,
                assertion_strength, change_failure_rate, test_freshness,
                coverage_delta, composite_score, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                now,
                spec_coverage,
                defect_escape_rate,
                assertion_strength,
                change_failure_rate,
                test_freshness,
                coverage_delta,
                composite_score,
                json.dumps(details) if details else None,
            ),
        )
        conn.commit()
        return self.get_quality_score(session_id)  # type: ignore[return-value]

    def get_quality_score(self, session_id: str) -> dict[str, Any] | None:
        """Get the quality score for a specific session."""
        row = self._get_conn().execute("SELECT * FROM quality_scores WHERE session_id = ?", (session_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_quality_scores(self, *, last: int = 10) -> list[dict[str, Any]]:
        """Get the most recent quality scores, newest first."""
        rows = (
            self._get_conn()
            .execute("SELECT * FROM quality_scores ORDER BY computed_at DESC LIMIT ?", (last,))
            .fetchall()
        )
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
        from datetime import datetime

        conn = self._get_conn()
        tables = [
            "specifications",
            "test_procedures",
            "operational_procedures",
            "assertion_runs",
            "session_prompts",
            "environment_config",
            "documents",
            "test_coverage",
            "tests",
            "test_plans",
            "test_plan_phases",
            "work_items",
            "backlog_snapshots",
            "quality_scores",
            "testable_elements",
            "deliberations",
            "deliberation_specs",
            "deliberation_work_items",
            "pipeline_events",
            "spec_quality_scores",
            "session_snapshots",
        ]
        export: dict[str, Any] = {"exported_at": _now(), "tables": {}}
        for table in tables:
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
            export["tables"][table] = [_row_to_dict(r) for r in rows]

        if output_path is None:
            timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            output_path = self.db_path.parent / f"knowledge-export-{timestamp}.json"
        else:
            output_path = Path(output_path)

        output_path.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
        return str(output_path)

    # ------------------------------------------------------------------
    # Summary stats
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Testable Elements (SPEC-1652/1653)
    # ------------------------------------------------------------------

    def _next_te_version(self, te_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM testable_elements WHERE id = ?", (te_id,)).fetchone()
        return (row[0] or 0) + 1

    def insert_testable_element(
        self,
        id: str,
        subsystem: str,
        page_or_module: str,
        name: str,
        element_type: str,
        expected_behavior: str,
        applicable_dimensions: list[str],
        changed_by: str,
        change_reason: str,
        *,
        spec_id: str | None = None,
        status: str = "active",
    ) -> dict[str, Any] | None:
        """Insert a new version of a testable element.

        Args:
            id: Unique identifier (e.g., "EL-dashboard-001").
            subsystem: Categorical (dashboard, team, config, inbox, api, auth, etc.).
            page_or_module: Where this element lives (page name or module path).
            name: Human-readable element name.
            element_type: button, text, input, chart, link, endpoint, config_field, etc.
            expected_behavior: What correct behavior looks like.
            applicable_dimensions: Which test dimensions apply (exists, correct_value, etc.).
            spec_id: Linked specification ID (nullable).
            status: 'active' or 'deprecated'.
        """
        version = self._next_te_version(id)
        dims_json = json.dumps(applicable_dimensions)
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO testable_elements
               (id, version, subsystem, page_or_module, name, element_type,
                expected_behavior, spec_id, applicable_dimensions, status,
                changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                subsystem,
                page_or_module,
                name,
                element_type,
                expected_behavior,
                spec_id,
                dims_json,
                status,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()
        return self.get_testable_element(id)

    def get_testable_element(self, te_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of a testable element."""
        row = self._get_conn().execute("SELECT * FROM current_testable_elements WHERE id = ?", (te_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_testable_elements(
        self,
        *,
        subsystem: str | None = None,
        page_or_module: str | None = None,
        element_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current testable elements with optional filters."""
        query = "SELECT * FROM current_testable_elements WHERE 1=1"
        params: list[Any] = []
        if subsystem:
            query += " AND subsystem = ?"
            params.append(subsystem)
        if page_or_module:
            query += " AND page_or_module = ?"
            params.append(page_or_module)
        if element_type:
            query += " AND element_type = ?"
            params.append(element_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_element_coverage_summary(self) -> dict[str, Any]:
        """Get coverage statistics per subsystem for quality dashboard."""
        conn = self._get_conn()
        # Count elements per subsystem
        subsystem_counts = conn.execute(
            """SELECT subsystem, COUNT(*) as total,
                      SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
               FROM current_testable_elements
               GROUP BY subsystem ORDER BY subsystem"""
        ).fetchall()
        return {
            "subsystems": [
                {"subsystem": r["subsystem"], "total": r["total"], "active": r["active"]} for r in subsystem_counts
            ],
            "total_elements": sum(r["total"] for r in subsystem_counts),
            "total_active": sum(r["active"] for r in subsystem_counts),
        }

    # ------------------------------------------------------------------
    # Pipeline Events (SPEC-2099)
    # ------------------------------------------------------------------

    @staticmethod
    def _record_event(
        conn: sqlite3.Connection,
        event_type: str,
        changed_by: str,
        *,
        session_id: str | None = None,
        artifact_id: str | None = None,
        artifact_type: str | None = None,
        artifact_version: int | None = None,
        duration_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a lifecycle event WITHIN an existing transaction.

        Does NOT commit — the caller commits alongside the artifact mutation.
        """
        event_id = str(uuid.uuid4())
        now = _now()
        conn.execute(
            """INSERT INTO pipeline_events
               (id, event_type, session_id, artifact_id, artifact_type,
                artifact_version, timestamp, duration_ms, metadata, changed_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event_id,
                event_type,
                session_id,
                artifact_id,
                artifact_type,
                artifact_version,
                now,
                duration_ms,
                json.dumps(metadata) if metadata else None,
                changed_by,
            ),
        )
        return event_id

    def record_event(
        self,
        event_type: str,
        changed_by: str,
        *,
        session_id: str | None = None,
        artifact_id: str | None = None,
        artifact_type: str | None = None,
        artifact_version: int | None = None,
        duration_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a lifecycle event (public API for external callers).

        Commits immediately in its own transaction.
        """
        conn = self._get_conn()
        event_id = self._record_event(
            conn,
            event_type,
            changed_by,
            session_id=session_id,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            artifact_version=artifact_version,
            duration_ms=duration_ms,
            metadata=metadata,
        )
        conn.commit()
        return event_id

    def list_events(
        self,
        *,
        event_type: str | None = None,
        artifact_id: str | None = None,
        artifact_type: str | None = None,
        session_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query pipeline events with optional filters."""
        conn = self._get_conn()
        query = "SELECT * FROM pipeline_events WHERE 1=1"
        params: list[Any] = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if artifact_id:
            query += " AND artifact_id = ?"
            params.append(artifact_id)
        if artifact_type:
            query += " AND artifact_type = ?"
            params.append(artifact_type)
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_events_for_artifact(self, artifact_type: str, artifact_id: str) -> list[dict[str, Any]]:
        """Get all lifecycle events for a specific artifact, chronological."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT * FROM pipeline_events
               WHERE artifact_type = ? AND artifact_id = ?
               ORDER BY timestamp ASC""",
            (artifact_type, artifact_id),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Lifecycle Metrics (SPEC-2100)
    # ------------------------------------------------------------------

    @staticmethod
    def _metric(
        value: Any,
        *,
        numerator: int | None = None,
        denominator: int | None = None,
        unit: str = "ratio",
        sample_count: int | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """Build a structured metric result with metadata."""
        result: dict[str, Any] = {"value": value, "unit": unit}
        if numerator is not None:
            result["numerator"] = numerator
        if denominator is not None:
            result["denominator"] = denominator
        if sample_count is not None:
            result["sample_count"] = sample_count
        result.update(extra)
        return result

    def compute_m2_spec_revision_rounds(self) -> dict[str, Any]:
        """M2: Average spec versions before reaching 'implemented' status."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT s.id, MIN(s.version) as impl_version
               FROM specifications s
               WHERE s.status = 'implemented'
               GROUP BY s.id"""
        ).fetchall()
        if not rows:
            return self._metric(None, unit="versions", sample_count=0, status="not_applicable")
        versions = [r["impl_version"] for r in rows]
        avg = sum(versions) / len(versions)
        return self._metric(
            round(avg, 2), unit="versions", sample_count=len(versions), min=min(versions), max=max(versions)
        )

    def compute_m4_spec_to_implemented_duration(self) -> dict[str, Any]:
        """M4: Average elapsed time from first 'specified' to first 'implemented' version."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT s.id,
                      MIN(CASE WHEN s.status = 'specified' THEN s.changed_at END) as first_specified,
                      MIN(CASE WHEN s.status = 'implemented' THEN s.changed_at END) as first_implemented
               FROM specifications s
               WHERE s.status IN ('specified', 'implemented')
               GROUP BY s.id
               HAVING first_specified IS NOT NULL AND first_implemented IS NOT NULL"""
        ).fetchall()
        if not rows:
            return self._metric(None, unit="hours", sample_count=0, status="not_applicable")
        durations = []
        for r in rows:
            try:
                spec_ts = datetime.fromisoformat(r["first_specified"])
                impl_ts = datetime.fromisoformat(r["first_implemented"])
                hours = (impl_ts - spec_ts).total_seconds() / 3600
                if hours >= 0:
                    durations.append(hours)
            except (ValueError, TypeError):
                continue
        if not durations:
            return self._metric(None, unit="hours", sample_count=0, status="not_applicable")
        durations.sort()
        avg = sum(durations) / len(durations)
        median = durations[len(durations) // 2]
        return self._metric(
            round(avg, 2),
            unit="hours",
            sample_count=len(durations),
            min=round(min(durations), 2),
            max=round(max(durations), 2),
            median=round(median, 2),
        )

    def compute_m6_defect_injection_rate(self, *, last_n_days: int | None = None) -> dict[str, Any]:
        """M6: Defect WIs created / specs implemented in the same time window."""
        conn = self._get_conn()
        time_filter = ""
        if last_n_days is not None:
            cutoff = (datetime.now(UTC) - __import__("datetime").timedelta(days=last_n_days)).isoformat()
            time_filter = f" AND changed_at >= '{cutoff}'"

        defect_count = conn.execute(
            f"SELECT COUNT(DISTINCT id) FROM work_items WHERE origin = 'defect' AND version = 1{time_filter}"
        ).fetchone()[0]

        impl_count = conn.execute(
            f"""SELECT COUNT(DISTINCT id) FROM specifications
                WHERE status = 'implemented'{time_filter}
                AND id NOT IN (SELECT id FROM specifications WHERE status = 'implemented' AND version < (
                    SELECT MIN(version) FROM specifications s2 WHERE s2.id = specifications.id AND s2.status = 'implemented'{time_filter}
                ))"""
        ).fetchone()[0]
        # Simpler: count specs that first became implemented in the window
        impl_count = conn.execute(
            f"""SELECT COUNT(DISTINCT s.id) FROM specifications s
                WHERE s.status = 'implemented'{time_filter}
                AND NOT EXISTS (
                    SELECT 1 FROM specifications s2 WHERE s2.id = s.id AND s2.status = 'implemented'
                    AND s2.changed_at < s.changed_at
                )"""
        ).fetchone()[0]

        if impl_count == 0:
            return self._metric(None, numerator=defect_count, denominator=0, unit="ratio", status="not_applicable")
        rate = defect_count / impl_count
        return self._metric(round(rate, 4), numerator=defect_count, denominator=impl_count, unit="ratio")

    def compute_m10_defect_resolution_duration(self) -> dict[str, Any]:
        """M10: Average time from wi_created(defect) to wi_resolved, event-backed."""
        conn = self._get_conn()
        # Find defect WIs with both created and resolved events
        rows = conn.execute(
            """SELECT e1.artifact_id,
                      MIN(e1.timestamp) as created_at,
                      MIN(e2.timestamp) as resolved_at
               FROM pipeline_events e1
               JOIN pipeline_events e2 ON e1.artifact_id = e2.artifact_id
                    AND e2.artifact_type = 'work_item' AND e2.event_type = 'wi_resolved'
               WHERE e1.artifact_type = 'work_item' AND e1.event_type = 'wi_created'
               GROUP BY e1.artifact_id"""
        ).fetchall()
        # Filter to defects using metadata
        defect_created = conn.execute(
            """SELECT artifact_id FROM pipeline_events
               WHERE event_type = 'wi_created' AND artifact_type = 'work_item'
               AND json_extract(metadata, '$.origin') = 'defect'"""
        ).fetchall()
        defect_ids = {r["artifact_id"] for r in defect_created}

        total_defects = len(defect_ids)
        durations = []
        for r in rows:
            if r["artifact_id"] not in defect_ids:
                continue
            try:
                c = datetime.fromisoformat(r["created_at"])
                r_ts = datetime.fromisoformat(r["resolved_at"])
                hours = (r_ts - c).total_seconds() / 3600
                if hours >= 0:
                    durations.append(hours)
            except (ValueError, TypeError):
                continue

        skipped = total_defects - len(durations)
        if not durations:
            return self._metric(
                None, unit="hours", sample_count=0, skipped_missing_event_count=skipped, status="not_applicable"
            )
        durations.sort()
        avg = sum(durations) / len(durations)
        median = durations[len(durations) // 2]
        return self._metric(
            round(avg, 2),
            unit="hours",
            sample_count=len(durations),
            min=round(min(durations), 2),
            max=round(max(durations), 2),
            median=round(median, 2),
            skipped_missing_event_count=skipped,
        )

    def compute_m11_regression_rate(self) -> dict[str, Any]:
        """M11: Failed assertion runs / total assertion runs (aggregate, not per-session)."""
        conn = self._get_conn()
        stats = conn.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN overall_passed = 0 THEN 1 ELSE 0 END) as failed FROM assertion_runs"
        ).fetchone()
        total = stats["total"] or 0
        failed = stats["failed"] or 0
        if total == 0:
            return self._metric(None, numerator=0, denominator=0, unit="ratio", status="not_applicable")
        rate = failed / total
        return self._metric(round(rate, 6), numerator=failed, denominator=total, unit="ratio")

    def compute_m12_spec_retirement_rate(self) -> dict[str, Any]:
        """M12: retired / (retired + active) where active = implemented + verified + specified."""
        conn = self._get_conn()
        counts = conn.execute("SELECT status, COUNT(*) as cnt FROM current_specifications GROUP BY status").fetchall()
        status_map = {r["status"]: r["cnt"] for r in counts}
        retired = status_map.get("retired", 0)
        active = sum(status_map.get(s, 0) for s in ("specified", "implemented", "verified"))
        denom = retired + active
        if denom == 0:
            return self._metric(None, numerator=0, denominator=0, unit="ratio", status="not_applicable")
        rate = retired / denom
        return self._metric(round(rate, 4), numerator=retired, denominator=denom, unit="ratio")

    def compute_m16_verified_with_passing_tests_rate(self) -> dict[str, Any]:
        """M16: Verified specs where ALL linked tests have last_result='pass' and test_file is not null."""
        conn = self._get_conn()
        verified_specs = conn.execute("SELECT id FROM current_specifications WHERE status = 'verified'").fetchall()
        if not verified_specs:
            return self._metric(None, numerator=0, denominator=0, unit="ratio", status="not_applicable")
        verified_with_evidence = 0
        for spec_row in verified_specs:
            sid = spec_row["id"]
            tests = conn.execute(
                "SELECT last_result, test_file FROM current_tests WHERE spec_id = ?", (sid,)
            ).fetchall()
            if not tests:
                continue  # No tests = not verified with evidence
            all_pass = all(t["last_result"] == "pass" and bool((t["test_file"] or "").strip()) for t in tests)
            if all_pass:
                verified_with_evidence += 1
        denom = len(verified_specs)
        return self._metric(
            round(verified_with_evidence / denom, 4),
            numerator=verified_with_evidence,
            denominator=denom,
            unit="ratio",
        )

    def compute_m17_stale_test_ratio(self, *, now: str | None = None) -> dict[str, Any]:
        """M17: Tests with last_executed_at >30 days old or null / total tests.

        Args:
            now: ISO timestamp to use as "current time" (for deterministic tests).
                 Defaults to actual current time.
        """
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM current_tests").fetchone()[0]
        if total == 0:
            return self._metric(None, numerator=0, denominator=0, unit="ratio", status="not_applicable")
        if now is None:
            now = _now()
        cutoff = (datetime.fromisoformat(now) - __import__("datetime").timedelta(days=30)).isoformat()
        stale = conn.execute(
            "SELECT COUNT(*) FROM current_tests WHERE last_executed_at IS NULL OR last_executed_at < ?",
            (cutoff,),
        ).fetchone()[0]
        return self._metric(round(stale / total, 4), numerator=stale, denominator=total, unit="ratio")

    def compute_m18_implemented_without_test_count(self) -> dict[str, Any]:
        """M18: Implemented/verified specs with zero current linked tests."""
        conn = self._get_conn()
        total_impl = conn.execute(
            "SELECT COUNT(*) FROM current_specifications WHERE status IN ('implemented', 'verified')"
        ).fetchone()[0]
        if total_impl == 0:
            return self._metric(None, numerator=0, denominator=0, unit="count", status="not_applicable")
        rows = conn.execute(
            """SELECT s.id FROM current_specifications s
               WHERE s.status IN ('implemented', 'verified')
               AND NOT EXISTS (SELECT 1 FROM current_tests t WHERE t.spec_id = s.id)"""
        ).fetchall()
        return self._metric(len(rows), denominator=total_impl, unit="count", spec_ids=[r["id"] for r in rows])

    def get_lifecycle_metrics(self, *, last_n_days: int | None = None) -> dict[str, Any]:
        """Compute all available Phase 1 lifecycle metrics.

        Args:
            last_n_days: Time window filter (applied where supported). None = all time.

        Returns dict keyed by metric ID (M2, M4, etc.) with structured values.
        """
        return {
            "M2": self.compute_m2_spec_revision_rounds(),
            "M4": self.compute_m4_spec_to_implemented_duration(),
            "M6": self.compute_m6_defect_injection_rate(last_n_days=last_n_days),
            "M10": self.compute_m10_defect_resolution_duration(),
            "M11": self.compute_m11_regression_rate(),
            "M12": self.compute_m12_spec_retirement_rate(),
            "M16": self.compute_m16_verified_with_passing_tests_rate(),
            "M17": self.compute_m17_stale_test_ratio(),
            "M18": self.compute_m18_implemented_without_test_count(),
        }

    # ------------------------------------------------------------------
    # Deliberations
    # ------------------------------------------------------------------

    # Redaction patterns for credential/PII scanning
    _REDACTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
        ("api_key", re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w\-]{16,}['\"]?", re.IGNORECASE)),
        # Authorization header: "Authorization: Bearer <token>" or "Bearer <token>"
        ("bearer_header", re.compile(r"(?:Authorization\s*:\s*)?Bearer\s+[\w\-\.~+/]+=*", re.IGNORECASE)),
        # token=/token:/bearer=/bearer: explicit separator forms
        ("token", re.compile(r"(?:token|bearer)\s*[:=]\s*['\"]?[\w\-\.]{20,}['\"]?", re.IGNORECASE)),
        ("secret", re.compile(r"(?:secret|password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?", re.IGNORECASE)),
        ("connection_string", re.compile(r"(?:mongodb|postgres|mysql|redis|amqp)://[^\s\"']+", re.IGNORECASE)),
        # Azure SharedAccessKey connection strings (captures full key up to ; or end)
        ("azure_sas_key", re.compile(r"SharedAccessKey=[A-Za-z0-9+/=]{20,}(?:;|$)", re.IGNORECASE)),
        # GitHub PAT prefixes: ghp_, gho_, ghs_, ghr_, github_pat_
        ("github_pat", re.compile(r"(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE)),
        # OpenAI / Stripe / generic service key prefixes
        ("service_key", re.compile(r"(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", re.IGNORECASE)),
        ("phone", re.compile(r"\+\d{10,15}")),
        ("email", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
        ("ip_address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
        ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
        # Agent Red API key families (ar_live_, ar_user_, ar_spa_plat_, pk_live_, arsk_)
        # Character class includes hyphen for secrets.token_urlsafe() output
        ("ar_live_key", re.compile(r"\bar_live_[A-Za-z0-9_-]{10,}")),
        ("ar_user_key", re.compile(r"\bar_user_[A-Za-z0-9_-]{10,}")),
        ("ar_spa_plat_key", re.compile(r"\bar_spa_plat_[A-Za-z0-9_-]{10,}")),
        ("pk_live_key", re.compile(r"\bpk_live_[A-Za-z0-9_-]{10,}")),
        ("arsk_key", re.compile(r"\barsk_[A-Za-z0-9_-]{10,}")),
        # Anthropic API key family: sk-ant-api<digits>-<token>
        # Covers current form (sk-ant-api03-...) and future API version variants.
        # Case sensitive because sk-ant-api is always lowercase in Anthropic's
        # format; case-insensitive would increase false positives against prose.
        # Word-boundary anchor avoids matching inside longer URL-safe tokens.
        ("anthropic_api_key", re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}")),
    ]

    @classmethod
    def redact_content(cls, text: str) -> tuple[str, str | None]:
        """Scan text for credentials/PII and replace with [REDACTED:type] markers.

        Returns (redacted_text, redaction_notes). If nothing was redacted,
        redaction_notes is None.
        """
        notes: list[str] = []
        result = text
        for label, pattern in cls._REDACTION_PATTERNS:
            matches = pattern.findall(result)
            if matches:
                result = pattern.sub(f"[REDACTED:{label}]", result)
                notes.append(f"{label}: {len(matches)} occurrence(s)")
        return result, "; ".join(notes) if notes else None

    def _next_deliberation_version(self, delib_id: str) -> int:
        row = self._get_conn().execute("SELECT MAX(version) FROM deliberations WHERE id = ?", (delib_id,)).fetchone()
        return (row[0] or 0) + 1

    def insert_deliberation(
        self,
        id: str,
        source_type: str,
        title: str,
        summary: str,
        content: str,
        changed_by: str,
        change_reason: str,
        *,
        spec_id: str | None = None,
        work_item_id: str | None = None,
        source_ref: str | None = None,
        participants: list[str] | None = None,
        outcome: str | None = None,
        session_id: str | None = None,
        sensitivity: str = "normal",
        origin_project: str | None = None,
        origin_repo: str | None = None,
    ) -> dict[str, Any] | None:
        """Insert a new version of a deliberation record.

        Content is redacted before storage. The SHA-256 hash of the
        pre-redaction text is stored in content_hash for dedup and audit.
        """
        valid_source_types = {
            "lo_review",
            "proposal",
            "owner_conversation",
            "report",
            "session_harvest",
            "bridge_thread",
        }
        if source_type not in valid_source_types:
            raise ValueError(f"Invalid source_type '{source_type}'; must be one of {sorted(valid_source_types)}")

        valid_outcomes = {"go", "no_go", "deferred", "owner_decision", "informational", None}
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome '{outcome}'; must be one of {sorted(o for o in valid_outcomes if o)}")

        # Hash raw content before redaction (for dedup)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Redact credentials/PII
        redacted_content, redaction_notes = self.redact_content(content)
        redaction_state = "redacted" if redaction_notes else "clean"
        if redaction_notes:
            sensitivity = "contains_redacted"

        version = self._next_deliberation_version(id)
        participants_json = json.dumps(participants) if participants else None
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO deliberations
               (id, version, spec_id, work_item_id, source_type, source_ref,
                title, summary, content, content_hash, participants, outcome,
                session_id, sensitivity, redaction_state, redaction_notes,
                origin_project, origin_repo, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                id,
                version,
                spec_id,
                work_item_id,
                source_type,
                source_ref,
                title,
                summary,
                redacted_content,
                content_hash,
                participants_json,
                outcome,
                session_id,
                sensitivity,
                redaction_state,
                redaction_notes,
                origin_project,
                origin_repo,
                changed_by,
                _now(),
                change_reason,
            ),
        )
        conn.commit()

        # Sync to ChromaDB (delete stale + index current).
        # ChromaDB is optional and rebuildable — failures must not make
        # the canonical SQLite write appear failed.
        try:
            self._index_deliberation_in_chroma(id)
        except Exception:
            pass  # Index can be rebuilt later via rebuild_deliberation_index()

        return self.get_deliberation(id)

    def upsert_deliberation_source(
        self,
        source_type: str,
        source_ref: str,
        content: str,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Idempotent insert keyed on (source_ref, content_hash).

        If a deliberation with the same source_ref and content_hash already
        exists, returns the existing record without modification. Otherwise
        inserts a new deliberation.
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        conn = self._get_conn()
        existing = conn.execute(
            """SELECT id FROM current_deliberations
               WHERE source_ref = ? AND content_hash = ?""",
            (source_ref, content_hash),
        ).fetchone()
        if existing:
            return self.get_deliberation(existing["id"])

        # Generate next DELIB ID — use MAX numeric suffix, not last rowid,
        # so append-only versioning of lower IDs does not corrupt allocation.
        row = conn.execute(
            "SELECT MAX(CAST(SUBSTR(id, 7) AS INTEGER)) FROM deliberations WHERE id LIKE 'DELIB-%'"
        ).fetchone()
        if row and row[0] is not None:
            new_id = f"DELIB-{row[0] + 1:04d}"
        else:
            new_id = "DELIB-0001"

        return self.insert_deliberation(
            id=new_id,
            source_type=source_type,
            source_ref=source_ref,
            content=content,
            **kwargs,
        )

    def get_deliberation(self, delib_id: str) -> dict[str, Any] | None:
        """Get the current (latest) version of a deliberation."""
        row = self._get_conn().execute("SELECT * FROM current_deliberations WHERE id = ?", (delib_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def get_deliberation_history(self, delib_id: str) -> list[dict[str, Any]]:
        """Get all versions of a deliberation."""
        rows = (
            self._get_conn()
            .execute("SELECT * FROM deliberations WHERE id = ? ORDER BY version", (delib_id,))
            .fetchall()
        )
        return [_row_to_dict(r) for r in rows]

    def list_deliberations(
        self,
        *,
        spec_id: str | None = None,
        work_item_id: str | None = None,
        source_type: str | None = None,
        session_id: str | None = None,
        source_ref: str | None = None,
        outcome: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current deliberations with optional filters."""
        query = "SELECT * FROM current_deliberations WHERE 1=1"
        params: list[Any] = []
        if spec_id is not None:
            query += " AND spec_id = ?"
            params.append(spec_id)
        if work_item_id is not None:
            query += " AND work_item_id = ?"
            params.append(work_item_id)
        if source_type is not None:
            query += " AND source_type = ?"
            params.append(source_type)
        if session_id is not None:
            query += " AND session_id = ?"
            params.append(session_id)
        if source_ref is not None:
            query += " AND source_ref = ?"
            params.append(source_ref)
        if outcome is not None:
            query += " AND outcome = ?"
            params.append(outcome)
        query += " ORDER BY rowid DESC"
        rows = self._get_conn().execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_deliberations_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        """Get all deliberations linked to a spec (primary FK + relation table)."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT DISTINCT d.* FROM current_deliberations d
               WHERE d.spec_id = ?
               UNION
               SELECT DISTINCT d.* FROM current_deliberations d
               INNER JOIN deliberation_specs ds ON d.id = ds.deliberation_id
               WHERE ds.spec_id = ?
               ORDER BY rowid DESC""",
            (spec_id, spec_id),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_deliberations_for_work_item(self, work_item_id: str) -> list[dict[str, Any]]:
        """Get all deliberations linked to a work item (primary FK + relation table)."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT DISTINCT d.* FROM current_deliberations d
               WHERE d.work_item_id = ?
               UNION
               SELECT DISTINCT d.* FROM current_deliberations d
               INNER JOIN deliberation_work_items dw ON d.id = dw.deliberation_id
               WHERE dw.work_item_id = ?
               ORDER BY rowid DESC""",
            (work_item_id, work_item_id),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def link_deliberation_spec(self, deliberation_id: str, spec_id: str, role: str = "related") -> None:
        """Link a deliberation to an additional spec via the relation table."""
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO deliberation_specs
               (deliberation_id, spec_id, role) VALUES (?, ?, ?)""",
            (deliberation_id, spec_id, role),
        )
        conn.commit()

    def link_deliberation_work_item(self, deliberation_id: str, work_item_id: str, role: str = "related") -> None:
        """Link a deliberation to an additional work item via the relation table."""
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO deliberation_work_items
               (deliberation_id, work_item_id, role) VALUES (?, ?, ?)""",
            (deliberation_id, work_item_id, role),
        )
        conn.commit()

    # ── ChromaDB semantic search integration ──────────────────────

    def _get_chroma_collection(self) -> Any | None:
        """Get or create the ChromaDB deliberations collection.

        Returns None if ChromaDB is not installed or not configured.
        Creates the persistence directory lazily on first use.
        """
        if not HAS_CHROMADB:
            return None
        if not hasattr(self, "_chroma_client"):
            chroma_path = getattr(self, "_chroma_path", None)
            if chroma_path is None:
                chroma_path = self.db_path.parent / ".groundtruth-chroma"
            chroma_path = Path(chroma_path)
            chroma_path.mkdir(parents=True, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(path=str(chroma_path))
        return self._chroma_client.get_or_create_collection(
            name=_CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "l2"},
        )

    @staticmethod
    def _deliberation_chroma_metadata(row: dict[str, Any], *, chunk_index: int, chunk_count: int) -> dict[str, Any]:
        """Build ChromaDB metadata from a deliberation row.

        Maps SQLite ``id`` to Chroma ``delib_id``. Required fields are
        always present; optional fields are omitted when None.
        """
        metadata = {
            "delib_id": row["id"],
            "version": row["version"],
            "changed_at": row["changed_at"],
            "source_type": row["source_type"],
            "sensitivity": row.get("sensitivity", "normal"),
            "redaction_state": row.get("redaction_state", "clean"),
            "chunk_index": chunk_index,
            "chunk_count": chunk_count,
            "title": row["title"],
        }
        optional_fields = [
            "spec_id",
            "work_item_id",
            "outcome",
            "session_id",
            "source_ref",
            "origin_project",
            "origin_repo",
        ]
        metadata.update({k: row[k] for k in optional_fields if row.get(k) is not None})
        return metadata

    @staticmethod
    def _chunk_text_for_embedding(text: str) -> list[str]:
        """Split text into chunks sized for the embedding model.

        Uses sentence-boundary splitting with token-aware sizing.
        Each chunk targets CHUNK_MAX_TOKENS wordpieces with
        CHUNK_OVERLAP_TOKENS overlap from the previous chunk.

        Falls back to character estimation: ~4 chars per wordpiece for
        English prose, avoiding a hard dependency on the tokenizer.
        """
        chars_per_token = 4  # Conservative estimate for English
        max_chars = CHUNK_MAX_TOKENS * chars_per_token  # ~920 chars
        overlap_chars = CHUNK_OVERLAP_TOKENS * chars_per_token  # ~120 chars

        if len(text) <= max_chars:
            return [text]

        sentences = _SENTENCE_SPLIT_RE.split(text)
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            if sentence_len > max_chars:
                # Rare: single sentence exceeds limit — split mid-sentence
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                for i in range(0, sentence_len, max_chars - overlap_chars):
                    chunks.append(sentence[i : i + max_chars])
                current_chunk = []
                current_len = 0
                continue

            if current_len + sentence_len > max_chars and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                # Overlap: keep trailing sentences that fit in overlap budget
                overlap_parts: list[str] = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) > overlap_chars:
                        break
                    overlap_parts.insert(0, s)
                    overlap_len += len(s)
                current_chunk = overlap_parts + [sentence]
                current_len = overlap_len + sentence_len
            else:
                current_chunk.append(sentence)
                current_len += sentence_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _index_deliberation_in_chroma(self, delib_id: str) -> int:
        """Index the current version of a deliberation in ChromaDB.

        Deletes any existing entries for this delib_id first (stale chunk
        removal), then indexes the current version's chunks.

        Returns the number of chunks indexed, or 0 if ChromaDB unavailable.
        """
        collection = self._get_chroma_collection()
        if collection is None:
            return 0

        # Delete stale entries for this deliberation
        try:
            collection.delete(where={"delib_id": delib_id})
        except Exception:
            pass  # Collection may be empty or delib_id not present

        # Get current version
        row = self.get_deliberation(delib_id)
        if row is None:
            return 0

        # Only index redacted content — secrets never enter ChromaDB
        content = row["content"]
        chunks = self._chunk_text_for_embedding(content)

        ids = []
        documents = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{delib_id}::v{row['version']}::chunk-{i:03d}"
            metadata = self._deliberation_chroma_metadata(row, chunk_index=i, chunk_count=len(chunks))
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(metadata)

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return len(chunks)

    def search_deliberations(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        """Search deliberations semantically via ChromaDB with SQLite LIKE fallback.

        Uses ChromaDB semantic search if available, with distance-threshold
        filtering. Falls back to SQLite LIKE if ChromaDB is unavailable or
        if no semantic results survive the relevance filter.

        Returns list of dicts with all deliberation row fields plus:
          - search_method: "semantic" | "text_match"
          - score: float (L2 distance, lower=better) | None for text_match
          - matched_chunk_id: str | None
          - matched_chunk_preview: str | None (first 200 chars of matched chunk)
        """
        # Try semantic search first
        collection = self._get_chroma_collection()
        if collection is not None and collection.count() > 0:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=min(limit * 3, 30),  # Over-fetch for dedup
                )
                if results and results["ids"] and results["ids"][0]:
                    # Filter by distance threshold and deduplicate by delib_id
                    seen_delib_ids: dict[str, dict[str, Any]] = {}
                    for idx, (doc_id, distance) in enumerate(
                        zip(results["ids"][0], results["distances"][0], strict=True)
                    ):
                        if distance > SEMANTIC_MAX_DISTANCE:
                            continue
                        metadata = results["metadatas"][0][idx]
                        delib_id = metadata.get("delib_id", "")
                        # Keep best (lowest distance) per delib_id
                        if delib_id not in seen_delib_ids or distance < seen_delib_ids[delib_id]["score"]:
                            doc_text = results["documents"][0][idx] if results["documents"] else ""
                            seen_delib_ids[delib_id] = {
                                "score": distance,
                                "matched_chunk_id": doc_id,
                                "matched_chunk_preview": doc_text[:200] if doc_text else None,
                            }

                    if seen_delib_ids:
                        # Fetch full deliberation rows and merge semantic metadata
                        semantic_results = []
                        for delib_id, match_info in sorted(seen_delib_ids.items(), key=lambda x: x[1]["score"])[:limit]:
                            row = self.get_deliberation(delib_id)
                            if row:
                                row["search_method"] = "semantic"
                                row["score"] = match_info["score"]
                                row["matched_chunk_id"] = match_info["matched_chunk_id"]
                                row["matched_chunk_preview"] = match_info["matched_chunk_preview"]
                                semantic_results.append(row)
                        if semantic_results:
                            return semantic_results
            except Exception:
                pass  # Fall through to SQLite LIKE

        # SQLite LIKE fallback
        conn = self._get_conn()
        pattern = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM current_deliberations
               WHERE content LIKE ? OR summary LIKE ? OR title LIKE ?
               ORDER BY rowid DESC LIMIT ?""",
            (pattern, pattern, pattern, limit),
        ).fetchall()
        results_list = []
        for r in rows:
            d = _row_to_dict(r)
            d["search_method"] = "text_match"
            d["score"] = None
            d["matched_chunk_id"] = None
            d["matched_chunk_preview"] = None
            results_list.append(d)
        return results_list

    def rebuild_deliberation_index(self) -> dict[str, Any]:
        """Rebuild ChromaDB collection from SQLite canonical data.

        Drops the existing collection and re-indexes all current
        deliberations. SQLite is always the source of truth.

        Returns: {"indexed": N, "chunks": M, "errors": []}
        """
        if not HAS_CHROMADB:
            return {"indexed": 0, "chunks": 0, "errors": ["ChromaDB not installed"]}

        # Drop and recreate collection
        client = self._get_chroma_collection()
        if client is None:
            return {"indexed": 0, "chunks": 0, "errors": ["ChromaDB client unavailable"]}

        # Delete the collection and recreate
        try:
            self._chroma_client.delete_collection(_CHROMA_COLLECTION_NAME)
        except Exception:
            pass
        # Clear cached collection reference
        if hasattr(self, "_chroma_client"):
            pass  # Client persists; collection is recreated on next get_or_create

        # Re-index all current deliberations
        conn = self._get_conn()
        rows = conn.execute("SELECT id FROM current_deliberations").fetchall()
        indexed = 0
        total_chunks = 0
        errors: list[str] = []
        for row in rows:
            try:
                chunks = self._index_deliberation_in_chroma(row["id"])
                total_chunks += chunks
                indexed += 1
            except Exception as e:
                errors.append(f"{row['id']}: {e}")

        return {"indexed": indexed, "chunks": total_chunks, "errors": errors}

    def get_summary(self) -> dict[str, Any]:
        """Return a high-level count summary across all artifact types in the database.

        Queries current-view tables for spec counts by status, test artifact
        counts, procedure counts, assertion pass/fail stats, work item counts
        by resolution status, backlog snapshot count, deliberation count,
        and pipeline event count.

        Returns:
            A dict with keys:
            - ``spec_counts``: dict of ``{status: count}`` for current specs.
            - ``spec_total``: total current spec count (sum of spec_counts).
            - ``spec_total_versions``: total rows in the specs history table.
            - ``test_procedure_count``: number of current test procedures.
            - ``op_procedure_count``: number of current operational procedures.
            - ``assertions_total``: count of specs with at least one assertion run.
            - ``assertions_passed``: count where the latest assertion run passed.
            - ``assertions_failed``: count where the latest assertion run failed.
            - ``env_config_count``: number of current environment config entries.
            - ``document_count``: number of current documents.
            - ``test_artifact_count``: number of current test artifacts.
            - ``test_plan_count``: number of current test plans.
            - ``test_plan_phase_count``: number of current test plan phases.
            - ``work_item_counts``: dict of ``{resolution_status: count}``.
            - ``work_item_total``: total current work item count.
            - ``backlog_snapshot_count``: number of current backlog snapshots.
            - ``testable_element_count``: number of current testable elements.
            - ``deliberation_count``: number of current deliberations.
            - ``pipeline_event_count``: total pipeline event rows.
        """
        conn = self._get_conn()
        specs = conn.execute("SELECT status, COUNT(*) as cnt FROM current_specifications GROUP BY status").fetchall()
        spec_counts = {r["status"]: r["cnt"] for r in specs}

        test_count = conn.execute("SELECT COUNT(*) FROM current_test_procedures").fetchone()[0]

        op_count = conn.execute("SELECT COUNT(*) FROM current_operational_procedures").fetchone()[0]

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

        total_versions = conn.execute("SELECT COUNT(*) FROM specifications").fetchone()[0]

        env_count = conn.execute("SELECT COUNT(*) FROM current_environment_config").fetchone()[0]

        doc_count = conn.execute("SELECT COUNT(*) FROM current_documents").fetchone()[0]

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

        te_count = conn.execute("SELECT COUNT(*) FROM current_testable_elements").fetchone()[0]

        delib_count = conn.execute("SELECT COUNT(*) FROM current_deliberations").fetchone()[0]

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
            "testable_element_count": te_count,
            "deliberation_count": delib_count,
            "pipeline_event_count": conn.execute("SELECT COUNT(*) FROM pipeline_events").fetchone()[0],
        }


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    # Parse JSON fields — expose as both "field_parsed" (clean) and "_field_parsed" (legacy)
    for key in (
        "assertions",
        "results",
        "variables",
        "steps",
        "known_failure_modes",
        "tags",
        "context",
        "participants",
        "test_ids",
        "work_item_ids",
        "summary_by_origin",
        "summary_by_component",
        "applicable_dimensions",
        "constraints",
        "affected_by",
    ):
        if key in d and d[key] and isinstance(d[key], str):
            try:
                parsed = json.loads(d[key])
                # Defensive: handle double-encoded JSON (string instead of list/dict)
                if isinstance(parsed, str):
                    try:
                        parsed = json.loads(parsed)
                    except (json.JSONDecodeError, TypeError):
                        pass
                d[f"{key}_parsed"] = parsed
                d[f"_{key}_parsed"] = parsed  # backward compat
            except (json.JSONDecodeError, TypeError):
                pass
    return d
