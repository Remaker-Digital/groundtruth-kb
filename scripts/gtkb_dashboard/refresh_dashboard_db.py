#!/usr/bin/env python3
"""Refresh the GT-KB Grafana dashboard SQLite database."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import multiprocessing as mp
import os
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

INCIDENTS_PATH = Path("memory") / "incidents.yaml"

_REQUIRED_MIGRATION_COLUMNS: tuple[tuple[str, str], ...] = (
    # DORA-001b Track 2 NO-GO -006 fix (S309): `environment` is referenced by
    # _ingest_canonical_pipeline_manifests INSERT and _reconcile_against_azure_revisions
    # SELECT. It must exist in both fresh-DB (schema.sql) and migration paths.
    # Listed first so pre-Track-2 production DBs gain it before the dependent
    # Track 2 columns below.
    ("environment", "TEXT NOT NULL DEFAULT ''"),
    ("event_kind", "TEXT NOT NULL DEFAULT 'change'"),
    ("deployable_change_id", "TEXT NOT NULL DEFAULT ''"),
    ("commit_range_start", "TEXT NOT NULL DEFAULT ''"),
    ("commit_range_end", "TEXT NOT NULL DEFAULT ''"),
    ("rollback_of_deploy_id", "TEXT NOT NULL DEFAULT ''"),
    ("hotfix_of_deploy_id", "TEXT NOT NULL DEFAULT ''"),
    # DORA-001b Track 2 (S308): authoritative deployment source columns.
    # Per bridge/gtkb-dora-001b-track2-implementation-003.md sec 2.1.
    # All TEXT NOT NULL DEFAULT to match the additive migration pattern.
    # Existing rows get default values; canonical-manifest-sourced rows
    # populate structured values via _ingest_canonical_pipeline_manifests().
    ("_authority_source", "TEXT NOT NULL DEFAULT 'heuristic'"),
    ("_image_ref", "TEXT NOT NULL DEFAULT ''"),
    ("_image_tag", "TEXT NOT NULL DEFAULT ''"),
    ("_revision_name", "TEXT NOT NULL DEFAULT ''"),
    ("_deployed_at", "TEXT NOT NULL DEFAULT ''"),
    ("_consistency", "TEXT NOT NULL DEFAULT 'unknown'"),
    ("_confidence", "TEXT NOT NULL DEFAULT 'low'"),
)

_ROLLBACK_LINK_WINDOW_SECONDS = 7 * 24 * 60 * 60
_TAFE_PROJECTION_TIMEOUT_SECONDS = 20
_GITHUB_WORKFLOW_REPOSITORY = "Remaker-Digital/groundtruth-kb"
_GITHUB_WORKFLOW_BRANCH = "main"
_TRUE_ENV_VALUES = {"1", "true", "yes", "on"}
_AZURE_CONTAINER_APP_MAP_ENV = "GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP"
_AZURE_RESOURCE_GROUP_ENV = "GTKB_DASHBOARD_AZURE_RESOURCE_GROUP"
_EXTERNAL_CLI_AUTH_ENV_KEYS = ("GH_CONFIG_DIR", "XDG_CONFIG_HOME")
_DEFERRAL_STATUS_KEYS = ("status", "state", "outcome", "resolution_status", "lifecycle_state")
_DEFERRAL_BOUNDARY_KEYS = (
    "expires_at",
    "expiry",
    "expiry_at",
    "expiration",
    "expiration_at",
    "defer_until",
    "deferred_until",
    "review_after",
    "review_at",
    "resume_at",
    "resume_trigger",
    "resume_condition",
    "expiry_condition",
    "time_limit",
    "trigger",
)


class IncidentIngestError(RuntimeError):
    """Raised when memory/incidents.yaml cannot be parsed or validated."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_DB_PATH = PROJECT_ROOT / "memory" / "gtkb-dashboard.sqlite"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")
SESSION_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "session_self_initialization.py"

KPI_DEFINITIONS = [
    ("backlog_active_items", "Backlog", "pressure", 1),
    ("membase_open_work_items", "MemBase Open WI", "knowledge", 1),
    ("deliberation_archive_current_total", "Deliberation Archive", "knowledge", 0),
    ("pytest_file_count", "Pytest Files", "knowledge", 0),
    ("specification_current_total", "Specifications", "knowledge", 0),
    ("drift_changed_path_count", "Drift Changed Paths", "pressure", 1),
    ("regression_release_blocker_count", "Release Blockers", "pressure", 1),
    ("contention_actionable_bridge_count", "Bridge Contention", "pressure", 1),
]

SETUP_STEPS = [
    {
        "section": "Install",
        "title": "Install GT-KB",
        "instruction": "Install the GT-KB package into a Python 3.12+ environment.",
        "command": "python -m pip install groundtruth-kb",
        "link_label": "GT-KB PyPI package",
        "link_url": "https://pypi.org/project/groundtruth-kb/",
    },
    {
        "section": "Install",
        "title": "Clone or enter the project repository",
        "instruction": "Run the dashboard from the project root so the refresh job can collect repo, CI, and governance evidence.",
        "command": "cd <groundtruth-enabled-project>",
        "link_label": "GT-KB repository",
        "link_url": "https://github.com/Remaker-Digital/groundtruth-kb",
    },
    {
        "section": "Configure",
        "title": "Create local environment file",
        "instruction": "Copy the template, then fill only local or staging values. Do not commit .env.local.",
        "command": "cp .env.example .env.local",
        "link_label": "Environment template",
        "link_url": ".env.example",
    },
    {
        "section": "Configure",
        "title": "Set dashboard refresh token",
        "instruction": "Set GTKB_DASHBOARD_REFRESH_TOKEN in .env.local. Manual refresh requests require this shared token.",
        "command": "GTKB_DASHBOARD_REFRESH_TOKEN=change-me-local-refresh-token",
        "link_label": "",
        "link_url": "",
    },
    {
        "section": "Launch",
        "title": "Install local Grafana",
        "instruction": "Install Grafana OSS into the ignored local tools directory and install the SQLite data source plugin.",
        "command": ".\\scripts\\gtkb_dashboard\\install_local_grafana.ps1",
        "link_label": "Grafana Windows install",
        "link_url": "https://grafana.com/docs/grafana/latest/installation/windows/",
    },
    {
        "section": "Launch",
        "title": "Start local dashboard",
        "instruction": "Start the local refresh service and Grafana without a container runtime.",
        "command": ".\\scripts\\gtkb_dashboard\\start_local_dashboard.ps1",
        "link_label": "Local Grafana",
        "link_url": "http://127.0.0.1:3000/",
    },
    {
        "section": "Launch",
        "title": "Refresh dashboard data",
        "instruction": "Open the refresh control when you need an on-demand data collection run outside the 60-minute interval.",
        "command": "",
        "link_label": "Refresh control",
        "link_url": "http://127.0.0.1:8766/",
    },
]

REQUIRED_TOOLS = [
    {
        "name": "Python",
        "category": "Runtime",
        "purpose": "Runs GT-KB, the dashboard refresh collector, and local tests.",
        "check_command": "python --version",
        "install_reference": "https://www.python.org/downloads/",
    },
    {
        "name": "Grafana OSS",
        "category": "Dashboard runtime",
        "purpose": "Serves the GT-KB dashboard locally without a container runtime.",
        "check_command": ".\\scripts\\gtkb_dashboard\\install_local_grafana.ps1 -SkipDownload",
        "install_reference": "https://grafana.com/docs/grafana/latest/installation/windows/",
    },
    {
        "name": "Grafana SQLite data source plugin",
        "category": "Dashboard data source",
        "purpose": "Lets Grafana query the dedicated GT-KB SQLite dashboard database directly.",
        "check_command": "Test-Path .\\memory\\grafana\\plugins\\frser-sqlite-datasource",
        "install_reference": "https://grafana.com/grafana/plugins/frser-sqlite-datasource/",
    },
    {
        "name": "Git",
        "category": "Source control",
        "purpose": "Supplies commit, branch, and delivery timeline evidence.",
        "check_command": "git --version",
        "install_reference": "https://git-scm.com/downloads",
    },
    {
        "name": "GitHub CLI",
        "category": "CI/CD CLI",
        "purpose": "Lets dashboard refresh logic inspect GitHub Actions and repository state when authenticated.",
        "check_command": "gh auth status",
        "install_reference": "https://cli.github.com/",
    },
    {
        "name": "Node.js",
        "category": "Frontend runtime",
        "purpose": "Builds widget, admin SPAs, documentation site, Playwright, and visual test assets.",
        "check_command": "node --version",
        "install_reference": "https://nodejs.org/",
    },
    {
        "name": "Azure CLI",
        "category": "Cloud CLI",
        "purpose": "Supports optional adopter-owned Azure resource inspection and deployment reconciliation.",
        "check_command": "az version",
        "install_reference": "https://learn.microsoft.com/cli/azure/install-azure-cli",
        "status": "optional",
    },
    {
        "name": "Playwright browsers",
        "category": "Test dependency",
        "purpose": "Runs visual, accessibility, and browser-level dashboard/application verification.",
        "check_command": "python -m playwright --version",
        "install_reference": "https://playwright.dev/python/docs/intro",
    },
]

THIRD_PARTY_SERVICES = [
    {
        "name": "GitHub Actions",
        "category": "CI/CD",
        "purpose": "Runs build, test, docs quality, security, and release candidate workflows.",
        "required_env_vars": "GROUND_TRUTH_GITHUB_REPO; gh authentication for local inspection",
        "setup_summary": "Authenticate gh, confirm repository access, and verify required workflows under .github/workflows.",
        "console_url": "https://github.com/Remaker-Digital/groundtruth-kb/actions",
        "health_signal": "workflow run status and local gh availability",
    },
    {
        "name": "Application deployment connector",
        "category": "Application-owned integration",
        "purpose": "Supplies live deployment topology, container, infrastructure, and runtime health rows to the GT-KB dashboard.",
        "required_env_vars": "Application-defined; GT-KB ships mock data and table contracts only",
        "setup_summary": "Implement in the application repository for the chosen deployment environment.",
        "console_url": "",
        "health_signal": "application-provided deployment signal freshness",
    },
    {
        "name": "Application security connector",
        "category": "Application-owned integration",
        "purpose": "Supplies security posture summaries such as vulnerability, dependency, auth, and policy signals.",
        "required_env_vars": "Application-defined",
        "setup_summary": "Map the application's selected scanners and policy systems into dashboard rows.",
        "console_url": "",
        "health_signal": "application-provided security signal freshness",
    },
    {
        "name": "Application observability connector",
        "category": "Application-owned integration",
        "purpose": "Supplies throughput, latency, error-rate, defect, incident, and infrastructure summaries.",
        "required_env_vars": "Application-defined",
        "setup_summary": "Map the application's selected telemetry platform into dashboard rows.",
        "console_url": "",
        "health_signal": "application-provided observability signal freshness",
    },
    {
        "name": "Langfuse",
        "category": "Observability",
        "purpose": "Captures trace and evaluation telemetry for AI workflows.",
        "required_env_vars": "LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL",
        "setup_summary": "Create project keys, set base URL, and enable exporter only for intended environments.",
        "console_url": "https://cloud.langfuse.com/",
        "health_signal": "exporter configuration and trace delivery",
    },
    {
        "name": "Chromatic",
        "category": "Visual testing",
        "purpose": "Runs visual regression checks for Storybook and Playwright surfaces.",
        "required_env_vars": "CHROMATIC_PROJECT_TOKEN",
        "setup_summary": "Create a project token, configure GitHub Actions secret, and verify visual-regression workflows.",
        "console_url": "https://www.chromatic.com/",
        "health_signal": "Chromatic workflow result",
    },
    {
        "name": "SonarCloud",
        "category": "Code quality",
        "purpose": "Runs static quality analysis as part of release readiness.",
        "required_env_vars": "SONAR_TOKEN",
        "setup_summary": "Configure project binding and GitHub Actions secret before enforcing the scan.",
        "console_url": "https://sonarcloud.io/",
        "health_signal": "SonarCloud workflow result",
    },
    {
        "name": "Docker Scout",
        "category": "Container security",
        "purpose": "Scans container images and registry artifacts for vulnerabilities.",
        "required_env_vars": "ACR_SCOUT_USERNAME, ACR_SCOUT_PASSWORD, DOCKER_SCOUT_HUB_USER, DOCKER_SCOUT_HUB_PAT",
        "setup_summary": "Configure registry and Docker Hub integration credentials as CI secrets or local-only env values.",
        "console_url": "https://scout.docker.com/",
        "health_signal": "Docker Scout workflow result",
    },
]

APPLICATION_DEPLOYMENT_SIGNALS = [
    (
        "Deployment topology",
        "Mock service topology",
        "web -> api -> worker -> datastore",
        "green",
        "application_deployment.topology",
    ),
    ("Containers", "Mock running containers", "4 healthy / 0 degraded", "green", "application_deployment.containers"),
    ("Security", "Mock vulnerability posture", "0 critical / 2 medium", "yellow", "application_security.summary"),
    (
        "Throughput and latency",
        "Mock request SLO",
        "p95 240 ms / 1.2k rpm",
        "green",
        "application_observability.latency",
    ),
    ("Defects", "Mock active defects", "1 release-scoped defect", "yellow", "application_quality.defects"),
    (
        "Infrastructure health",
        "Mock infrastructure summary",
        "compute green / data green / queue yellow",
        "yellow",
        "application_infrastructure.summary",
    ),
]


def _load_session_module() -> Any:
    spec = importlib.util.spec_from_file_location("session_self_initialization", SESSION_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SESSION_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization"] = module
    spec.loader.exec_module(module)
    return module


def initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _migrate_schema(db_path: Path) -> None:
    """Apply idempotent ALTER TABLE migrations under SQLite RESERVED lock.

    The fresh-DB path is handled by `CREATE TABLE IF NOT EXISTS` in `schema.sql`;
    this function adds the columns listed in `_REQUIRED_MIGRATION_COLUMNS` to any
    pre-existing `delivery_timeline_events` table that predates them. Each entry
    is checked against `PRAGMA table_info` and ALTER-added only if missing.

    Concurrency: the probe + ALTER sequence runs inside a single explicit
    BEGIN IMMEDIATE / COMMIT transaction. BEGIN IMMEDIATE acquires a RESERVED
    lock at the database-file level; a second concurrent writer blocks on its
    own BEGIN IMMEDIATE until the first COMMITs, at which point its probe sees
    the already-added columns and the ALTER branch is skipped. No
    duplicate-column race.
    """
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = {row[1] for row in conn.execute("PRAGMA table_info('delivery_timeline_events')").fetchall()}
            for col_name, col_decl in _REQUIRED_MIGRATION_COLUMNS:
                if col_name not in existing:
                    conn.execute(f"ALTER TABLE delivery_timeline_events ADD COLUMN {col_name} {col_decl}")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


# =============================================================================
# WI-4506: TAFE Observability projection (read-only narrowed projection of
# canonical TAFE state from groundtruth.db into the dashboard SQLite).
# Tables are created at runtime via CREATE TABLE IF NOT EXISTS so the additive
# WI-4506 surface lands without modifying schema.sql. All columns NULL-tolerant
# so fresh-install / pre-TAFE adopters render "No data" rather than error.
# SPEC-TAFE-R7: dashboard SQLite is a derived cache; canonical TAFE state
# remains in groundtruth.db. No PK/FK to the canonical store.
# =============================================================================

_TAFE_PROJECTION_TABLE_DDL: tuple[tuple[str, str], ...] = (
    (
        "tafe_stage_attempt_telemetry",
        """
        CREATE TABLE IF NOT EXISTS tafe_stage_attempt_telemetry (
            id TEXT,
            version INTEGER,
            flow_instance_id TEXT,
            stage_instance_id TEXT,
            attempt_number INTEGER,
            agent_harness_id TEXT,
            model_identifier TEXT,
            provider TEXT,
            started_at TEXT,
            completed_at TEXT,
            duration_ms INTEGER,
            outcome TEXT,
            verdict TEXT,
            failure_class TEXT,
            cleanup_result TEXT,
            status TEXT
        )
        """,
    ),
    (
        "tafe_flow_instances",
        """
        CREATE TABLE IF NOT EXISTS tafe_flow_instances (
            id TEXT,
            version INTEGER,
            flow_definition_id TEXT,
            flow_type TEXT,
            subject_type TEXT,
            subject_id TEXT,
            status TEXT,
            current_stage_instance_id TEXT,
            started_at TEXT,
            completed_at TEXT
        )
        """,
    ),
    (
        "tafe_stage_instances",
        """
        CREATE TABLE IF NOT EXISTS tafe_stage_instances (
            id TEXT,
            version INTEGER,
            flow_instance_id TEXT,
            stage_id TEXT,
            stage_index INTEGER,
            required_role TEXT,
            status TEXT,
            claim_status TEXT,
            claimed_by_harness_id TEXT,
            started_at TEXT,
            completed_at TEXT
        )
        """,
    ),
    (
        "tafe_stage_leases",
        """
        CREATE TABLE IF NOT EXISTS tafe_stage_leases (
            id TEXT,
            version INTEGER,
            stage_instance_id TEXT,
            holder_harness_id TEXT,
            holder_session_id TEXT,
            lease_status TEXT,
            acquired_at TEXT,
            heartbeat_at TEXT,
            expires_at TEXT,
            released_at TEXT
        )
        """,
    ),
    (
        "tafe_agent_capability_snapshots",
        """
        CREATE TABLE IF NOT EXISTS tafe_agent_capability_snapshots (
            id TEXT,
            version INTEGER,
            harness_id TEXT,
            harness_name TEXT,
            role TEXT,
            subject_scope TEXT,
            health_status TEXT,
            reviewer_precedence INTEGER,
            workspace_availability TEXT,
            model_identifier TEXT,
            captured_at TEXT,
            status TEXT
        )
        """,
    ),
)

TAFE_PROJECTION_TABLE_NAMES: tuple[str, ...] = tuple(name for name, _ddl in _TAFE_PROJECTION_TABLE_DDL)


def _migrate_tafe_projection_schema(db_path: Path) -> None:
    """Create the WI-4506 TAFE projection tables in the dashboard SQLite.

    Idempotent via CREATE TABLE IF NOT EXISTS. Uses the same BEGIN IMMEDIATE
    lock pattern as `_migrate_schema` so concurrent dashboard refreshes do not
    race the migration.
    """
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            for _name, ddl in _TAFE_PROJECTION_TABLE_DDL:
                conn.execute(ddl)
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


def _project_tafe_row_subset(row: dict[str, Any], columns: tuple[str, ...]) -> tuple[Any, ...]:
    """Return a value tuple for the named columns from a TAFE row, defaulting to None.

    The canonical row dicts from `KnowledgeDB.list_*` may omit columns the
    dashboard projection does not require; the dashboard projection is
    NULL-tolerant by design.
    """
    return tuple(row.get(col) for col in columns)


# Projection column lists per table — kept aligned with the DDL above.
_TAFE_PROJECTION_COLUMNS: dict[str, tuple[str, ...]] = {
    "tafe_stage_attempt_telemetry": (
        "id",
        "version",
        "flow_instance_id",
        "stage_instance_id",
        "attempt_number",
        "agent_harness_id",
        "model_identifier",
        "provider",
        "started_at",
        "completed_at",
        "duration_ms",
        "outcome",
        "verdict",
        "failure_class",
        "cleanup_result",
        "status",
    ),
    "tafe_flow_instances": (
        "id",
        "version",
        "flow_definition_id",
        "flow_type",
        "subject_type",
        "subject_id",
        "status",
        "current_stage_instance_id",
        "started_at",
        "completed_at",
    ),
    "tafe_stage_instances": (
        "id",
        "version",
        "flow_instance_id",
        "stage_id",
        "stage_index",
        "required_role",
        "status",
        "claim_status",
        "claimed_by_harness_id",
        "started_at",
        "completed_at",
    ),
    "tafe_stage_leases": (
        "id",
        "version",
        "stage_instance_id",
        "holder_harness_id",
        "holder_session_id",
        "lease_status",
        "acquired_at",
        "heartbeat_at",
        "expires_at",
        "released_at",
    ),
    "tafe_agent_capability_snapshots": (
        "id",
        "version",
        "harness_id",
        "harness_name",
        "role",
        "subject_scope",
        "health_status",
        "reviewer_precedence",
        "workspace_availability",
        "model_identifier",
        "captured_at",
        "status",
    ),
}


def _refresh_tafe_projection(db_path: Path, project_root: Path) -> dict[str, int]:
    """Project the canonical TAFE rows from `groundtruth.db` into the dashboard SQLite.

    Read-only against the canonical store; reuses the existing GT-KB Python
    API (`KnowledgeDB`) so the projection tracks the canonical schema surface
    without raw SQL. Truncate-and-insert per table (`_replace_table` pattern),
    so a rerun yields the same row set (idempotence).
    """
    counts: dict[str, int] = {name: 0 for name in TAFE_PROJECTION_TABLE_NAMES}

    kb_path = project_root / "groundtruth.db"
    if not kb_path.exists():
        logger.info("groundtruth.db absent at %s; TAFE projection emits zero rows", kb_path)
        return counts

    # Local import: the dashboard refresh runs in adopter contexts where the
    # canonical `groundtruth_kb` package may not be importable until very
    # late in startup; deferring the import keeps the module loadable.
    from groundtruth_kb.db import KnowledgeDB

    kb = KnowledgeDB(kb_path)
    try:
        list_fns: dict[str, Any] = {
            "tafe_stage_attempt_telemetry": kb.list_stage_attempt_telemetry,
            "tafe_flow_instances": kb.list_flow_instances,
            "tafe_stage_instances": kb.list_stage_instances,
            "tafe_stage_leases": kb.list_stage_leases,
            "tafe_agent_capability_snapshots": kb.list_agent_capability_snapshots,
        }
    except AttributeError:
        # Pre-TAFE adopter: one or more list_* methods missing.
        logger.info("KnowledgeDB lacks one or more TAFE list_* methods; projection emits zero rows")
        try:
            kb.close()
        except Exception:
            pass
        return counts

    rows_by_table: dict[str, list[dict[str, Any]]] = {}
    try:
        for table_name, list_fn in list_fns.items():
            try:
                rows_by_table[table_name] = list(list_fn())
            except Exception:
                logger.warning("TAFE list_* failed for %s; emitting zero rows", table_name, exc_info=True)
                rows_by_table[table_name] = []
    finally:
        try:
            kb.close()
        except Exception:
            pass

    with sqlite3.connect(db_path) as conn:
        for table_name, rows in rows_by_table.items():
            columns = _TAFE_PROJECTION_COLUMNS[table_name]
            _replace_table(conn, table_name)
            placeholders = ",".join("?" for _ in columns)
            column_list = ",".join(columns)
            insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
            for row in rows:
                conn.execute(insert_sql, _project_tafe_row_subset(row, columns))
            counts[table_name] = len(rows)
        conn.commit()

    return counts


def _refresh_tafe_projection_worker(db_path: str, project_root: str, queue: mp.Queue) -> None:
    try:
        db = Path(db_path)
        root = Path(project_root)
        _migrate_tafe_projection_schema(db)
        counts = _refresh_tafe_projection(db, root)
        queue.put({"status": "completed", "counts": counts})
    except Exception as exc:
        queue.put({"status": "failed", "error": repr(exc)})


def _refresh_tafe_projection_safe(db_path: Path, project_root: Path) -> None:
    """Run `_refresh_tafe_projection` but never abort the dashboard refresh on failure.

    Same defensive pattern as `_write_bridge_swimlane_safe`: the TAFE
    observability panels are an additive surface; their absence must not
    break the rest of the dashboard refresh.
    """
    queue: mp.Queue = mp.Queue()
    process = mp.Process(
        target=_refresh_tafe_projection_worker,
        args=(str(db_path), str(project_root), queue),
        daemon=True,
    )
    process.start()
    process.join(_TAFE_PROJECTION_TIMEOUT_SECONDS)
    if process.is_alive():
        process.terminate()
        process.join(5)
        logger.warning("TAFE projection refresh timed out; dashboard refresh continues")
        return
    if process.exitcode not in (0, None):
        logger.warning("TAFE projection refresh exited %s; dashboard refresh continues", process.exitcode)
        return
    try:
        result = queue.get_nowait()
    except Exception:
        logger.warning("TAFE projection refresh produced no result; dashboard refresh continues")
        return
    if result.get("status") != "completed":
        logger.warning(
            "TAFE projection refresh failed: %s; dashboard refresh continues", result.get("error", "unknown")
        )


def refresh_database(
    db_path: Path = DEFAULT_DB_PATH,
    project_root: Path = PROJECT_ROOT,
    model: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
    *,
    fast_startup_model: bool = True,
    probe_live: bool = False,
) -> dict[str, Any]:
    started_at = datetime.now(UTC).isoformat()
    probe_live_release_health = model is None and probe_live
    initialize_database(db_path)
    _migrate_schema(db_path)
    run_id: int | None = None
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO refresh_runs (started_at, status) VALUES (?, ?)",
            (started_at, "running"),
        )
        run_id = int(cursor.lastrowid)

    try:
        session_module = None
        if model is None:
            session_module = _load_session_module()
            external_cli_auth_env = _snapshot_external_cli_auth_env()
            try:
                model = session_module.build_startup_model(project_root, fast_hook=fast_startup_model)
            finally:
                _restore_external_cli_auth_env(external_cli_auth_env)
        if history is None:
            if session_module is None:
                session_module = _load_session_module()
            snapshot = session_module._snapshot_from_model(model)
            previous_history = _read_existing_history(db_path)
            history = _append_snapshot(previous_history, snapshot)
        _write_model_to_db(
            db_path,
            model,
            history,
            project_root,
            probe_live_release_health=probe_live_release_health,
            probe_live_workflows=probe_live_release_health,
        )
        _write_bridge_swimlane_safe(project_root)
        _refresh_tafe_projection_safe(db_path, project_root)
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE refresh_runs SET completed_at = ?, status = ? WHERE id = ?",
                (completed_at, "completed", run_id),
            )
        return {"status": "completed", "run_id": run_id, "started_at": started_at, "completed_at": completed_at}
    except Exception as exc:
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE refresh_runs SET completed_at = ?, status = ?, error = ? WHERE id = ?",
                (completed_at, "failed", str(exc), run_id),
            )
        raise


def _write_bridge_swimlane_safe(project_root: Path) -> None:
    """Generate the bridge swimlane JSON; never abort refresh on failure.

    Slice 2.1 of GTKB-DASHBOARD-002. The dashboard landing page reads
    ``docs/gtkb-dashboard/bridge-swimlane.json``; failure to write it logs a
    warning and returns silently so the rest of the refresh is unaffected.
    """
    try:
        try:
            from .generate_bridge_swimlane import write_swimlane
        except ImportError:
            from scripts.gtkb_dashboard.generate_bridge_swimlane import write_swimlane

        out_path = project_root / "docs" / "gtkb-dashboard" / "bridge-swimlane.json"
        write_swimlane(project_root, out_path)
    except Exception:
        logger.warning("bridge swimlane write failed; refresh continues", exc_info=True)


def _read_existing_history(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT generated_at,
                   MAX(CASE WHEN metric_key = 'backlog_active_items' THEN value END) AS backlog_active_items,
                   MAX(CASE WHEN metric_key = 'membase_open_work_items' THEN value END) AS membase_open_work_items,
                   MAX(CASE WHEN metric_key = 'deliberation_archive_current_total' THEN value END) AS deliberation_archive_current_total,
                   MAX(CASE WHEN metric_key = 'pytest_file_count' THEN value END) AS pytest_file_count,
                   MAX(CASE WHEN metric_key = 'specification_current_total' THEN value END) AS specification_current_total,
                   MAX(CASE WHEN metric_key = 'drift_changed_path_count' THEN value END) AS drift_changed_path_count,
                   MAX(CASE WHEN metric_key = 'regression_release_blocker_count' THEN value END) AS regression_release_blocker_count,
                   MAX(CASE WHEN metric_key = 'contention_actionable_bridge_count' THEN value END) AS contention_actionable_bridge_count
            FROM kpi_snapshots
            GROUP BY generated_at
            ORDER BY generated_at
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _append_snapshot(
    history: list[dict[str, Any]], snapshot: dict[str, Any], max_history: int = 200
) -> list[dict[str, Any]]:
    filtered = [row for row in history if row.get("generated_at") != snapshot.get("generated_at")]
    filtered.append(snapshot)
    return filtered[-max_history:]


def _write_model_to_db(
    db_path: Path,
    model: dict[str, Any],
    history: list[dict[str, Any]],
    project_root: Path = PROJECT_ROOT,
    *,
    probe_live_release_health: bool = False,
    probe_live_workflows: bool = False,
) -> None:
    metrics = model.get("metrics", {})
    intelligence = model.get("dashboard_intelligence", {})
    infrastructure = model.get("infrastructure", {})
    delivery = infrastructure.get("delivery_timeline", {})
    release_health_findings = _release_health_findings(
        project_root,
        intelligence,
        model=model,
        probe_live=probe_live_release_health,
    )

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _replace_table(conn, "dashboard_metadata")
        _replace_table(conn, "health_cards")
        _replace_table(conn, "shortcuts")
        _replace_table(conn, "action_center")
        _replace_table(conn, "delivery_timeline_summary")
        _replace_table(conn, "delivery_timeline_events")
        _replace_table(conn, "release_blockers")
        _replace_table(conn, "quality_rollup")
        _replace_table(conn, "risk_register")
        _replace_table(conn, "integration_status")
        _replace_table(conn, "kpi_snapshots")
        _replace_table(conn, "current_metrics")
        _replace_table(conn, "data_freshness")
        _replace_table(conn, "setup_steps")
        _replace_table(conn, "required_tools")
        _replace_table(conn, "third_party_services")
        _replace_table(conn, "application_deployment_signals")

        metadata = {
            "generated_at": model.get("generated_at", ""),
            "role": model.get("role", {}).get("assumed_role", ""),
            "scope_note": model.get("dashboard_requirements", {}).get("scope_note", ""),
            "dashboard_subject_scope": _dashboard_subject_scope_label(model),
            "dashboard_subject_badge": "GT-KB platform + active adopter",
            "refresh_service_scope": "loopback/local-only (127.0.0.1)",
            "raw_model_json": json.dumps(model, sort_keys=True),
        }
        conn.executemany(
            "INSERT INTO dashboard_metadata (key, value) VALUES (?, ?)",
            metadata.items(),
        )

        conn.executemany(
            "INSERT INTO health_cards (sort_order, label, value, status, tooltip) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    idx,
                    item.get("label", ""),
                    str(item.get("value", "")),
                    item.get("status", ""),
                    item.get("tooltip", ""),
                )
                for idx, item in enumerate(
                    _reconciled_health_cards(metrics, intelligence, release_health_findings), start=1
                )
            ],
        )

        conn.executemany(
            "INSERT INTO shortcuts (sort_order, label, target, kind) VALUES (?, ?, ?, ?)",
            [
                (idx, item.get("label", ""), item.get("target", ""), item.get("kind", "file"))
                for idx, item in enumerate(intelligence.get("shortcuts", []), start=1)
            ],
        )

        conn.executemany(
            """
            INSERT INTO action_center
            (sort_order, action, owner_lane, why, remediation, shortcut_label, shortcut_target, shortcut_kind, source, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    idx,
                    item.get("action", ""),
                    item.get("owner_lane", ""),
                    item.get("why", ""),
                    item.get("remediation", ""),
                    (item.get("shortcut") or {}).get("label", ""),
                    (item.get("shortcut") or {}).get("target", ""),
                    (item.get("shortcut") or {}).get("kind", "file"),
                    item.get("source", ""),
                    item.get("severity", ""),
                )
                for idx, item in enumerate(intelligence.get("action_center", []), start=1)
            ],
        )

        conn.executemany(
            """
            INSERT INTO delivery_timeline_summary
            (sort_order, stage, label, event_count, latest_result, latest_version, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    idx,
                    item.get("stage", ""),
                    item.get("label", ""),
                    int(item.get("count", 0) or 0),
                    item.get("latest_result", ""),
                    item.get("latest_version", ""),
                    item.get("status", ""),
                )
                for idx, item in enumerate(delivery.get("stage_summary", []), start=1)
            ],
        )

        ordered_events = sorted(delivery.get("timeline", []), key=lambda row: str(row.get("timestamp") or ""))
        enriched_events = _enrich_timeline_events(ordered_events)
        conn.executemany(
            """
            INSERT INTO delivery_timeline_events
            (sort_order, stage, stage_label, event, timestamp, date_label, version, commit_sha, branch,
             result, result_color, test_results, source, url, notes,
             event_kind, deployable_change_id, commit_range_start, commit_range_end,
             rollback_of_deploy_id, hotfix_of_deploy_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    idx,
                    item.get("stage", ""),
                    item.get("stage_label", ""),
                    item.get("event", ""),
                    item.get("timestamp", ""),
                    str(item.get("timestamp", ""))[:10] or "configuration",
                    item.get("version", ""),
                    item.get("commit", ""),
                    item.get("branch", ""),
                    item.get("result", ""),
                    item.get("result_color", ""),
                    item.get("test_results", ""),
                    item.get("source", ""),
                    item.get("url", ""),
                    item.get("notes", ""),
                    item["_event_kind"],
                    item["_deployable_change_id"],
                    item["_commit_range_start"],
                    item["_commit_range_end"],
                    item["_rollback_of_deploy_id"],
                    item["_hotfix_of_deploy_id"],
                )
                for idx, item in enumerate(enriched_events, start=1)
            ],
        )

        known_deploy_ids = {item["_deployable_change_id"] for item in enriched_events if item["_deployable_change_id"]}
        _load_incidents(project_root, conn, known_deploy_ids)

        # DORA-001b Track 2 (S308): ingest canonical pipeline manifests as
        # structured deployment evidence. Live Azure Container Apps
        # reconciliation is an optional adopter diagnostic and is disabled
        # by default for GT-KB release-health refreshes.
        # Per bridge/gtkb-dora-001b-track2-implementation-003.md sec 2.4-2.5
        # (Codex GO at -004).
        _ingest_canonical_pipeline_manifests(conn, project_root)
        if _azure_reconciliation_enabled():
            _reconcile_against_azure_revisions(conn, ["staging", "production"])

        release = intelligence.get("release_readiness", {})
        release_blockers = _release_blocker_messages(release, release_health_findings)
        conn.executemany(
            "INSERT INTO release_blockers (sort_order, blocker) VALUES (?, ?)",
            [(idx, blocker) for idx, blocker in enumerate(release_blockers, start=1)],
        )

        quality = intelligence.get("quality_rollup", {})
        quality_rows = [
            ("Total", quality.get("total", 0), "green"),
            ("Failing", quality.get("failing", 0), "red"),
            ("Manual", quality.get("manual", 0), "yellow"),
            ("No Recent / Unknown", quality.get("unknown", 0), "yellow"),
            ("Ready / Passing", quality.get("ready_or_passing", 0), "green"),
        ]
        conn.executemany(
            "INSERT INTO quality_rollup (sort_order, label, value, status) VALUES (?, ?, ?, ?)",
            [(idx, label, int(value or 0), status) for idx, (label, value, status) in enumerate(quality_rows, start=1)],
        )

        conn.executemany(
            """
            INSERT INTO risk_register
            (sort_order, risk, evidence, impact, remediation, owner, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    idx,
                    item.get("risk", ""),
                    item.get("evidence", ""),
                    item.get("impact", ""),
                    item.get("remediation", ""),
                    item.get("owner", ""),
                    item.get("severity", ""),
                )
                for idx, item in enumerate(intelligence.get("risk_register", []), start=1)
            ],
        )

        integrations = infrastructure.get("testing_service_integrations", {})
        conn.executemany(
            """
            INSERT INTO integration_status
            (sort_order, key, display_name, health, status, latest_run_summary, gate_role, remediation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            _integration_status_rows(integrations, project_root, probe_live_workflows=probe_live_workflows),
        )

        conn.executemany(
            "INSERT INTO kpi_snapshots (generated_at, metric_key, metric_label, value, metric_group, lower_is_better) VALUES (?, ?, ?, ?, ?, ?)",
            _kpi_rows(history),
        )
        conn.executemany(
            "INSERT INTO current_metrics (metric_key, metric_label, value, status, description) VALUES (?, ?, ?, ?, ?)",
            _current_metric_rows(metrics, intelligence, release_health_findings),
        )
        conn.executemany(
            "INSERT INTO data_freshness (key, label, value) VALUES (?, ?, ?)",
            _data_freshness_rows(intelligence.get("data_freshness", {})),
        )
        conn.executemany(
            """
            INSERT INTO setup_steps
            (sort_order, section, title, instruction, command, link_label, link_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _setup_step_rows(),
        )
        conn.executemany(
            """
            INSERT INTO required_tools
            (sort_order, name, category, purpose, check_command, install_reference, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _required_tool_rows(),
        )
        conn.executemany(
            """
            INSERT INTO third_party_services
            (sort_order, name, category, purpose, required_env_vars, setup_summary, console_url, health_signal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            _third_party_service_rows(),
        )
        conn.executemany(
            """
            INSERT INTO application_deployment_signals
            (sort_order, surface, signal, mock_value, status, source_contract)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            _application_deployment_signal_rows(),
        )


def _replace_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(f"DELETE FROM {table_name}")


_DORA_DEPLOYMENT_EVENT_KINDS: frozenset[str] = frozenset({"canonical_deploy"})

_DORA_AUTHORITATIVE_EVENT_KINDS: frozenset[str] = frozenset(
    {
        "canonical_deploy",
        "canonical_deploy_attempted_failed",
        "canonical_pipeline_run",
        "canonical_pipeline_dry_run",
    }
)


def _is_deployment_event(event_kind: str) -> bool:
    """Per Codex GO -006 condition 2: only `canonical_deploy` counts as a deployment.

    Used by `GTKB-DORA-002` deployment-frequency math (when it lands) to
    exclude `canonical_pipeline_run` and `canonical_pipeline_dry_run` from
    deployment counts. Exposed at module scope so KPI queries can import it.
    """
    return event_kind in _DORA_DEPLOYMENT_EVENT_KINDS


def _classify_manifest(manifest: dict[str, Any]) -> str:
    """Classify a `logs/deploy-result-*.json` manifest into a canonical event kind.

    Implements the contract specified in
    `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md` sec 5.5.
    Filters non-deployments before they enter the DORA event stream.
    Uses structured fields only; never parses free-text phase names.

    Returns one of:
      - canonical_deploy
      - canonical_deploy_attempted_failed
      - canonical_pipeline_run
      - canonical_pipeline_dry_run
    """
    # 1. Dry-runs are not deployments.
    if manifest.get("dry_run") is True:
        return "canonical_pipeline_dry_run"

    # 2. Look up phase 8 (deploy) by integer phase number, not free-text name.
    # Per scripts/deploy_pipeline.py:540, phase_8_deploy() returns
    # PhaseResult(9, ...) — the integer 9 (not 8) identifies the deploy phase.
    phases = manifest.get("phases", []) or []
    phase_8 = next((p for p in phases if p.get("phase") == 9), None)

    # 3. No deploy phase = not a deployment.
    if phase_8 is None:
        return "canonical_pipeline_run"

    # 4. Phase 8 status semantics per scripts/deploy_pipeline.py:117 (PASS/FAIL/SKIP).
    status = phase_8.get("status", "")
    if status == "PASS":
        # Track 1 enhanced manifest: prefer the explicit booleans.
        evidence = manifest.get("deploy_evidence", {}) or {}
        if evidence.get("target_update_attempted") is True:
            if evidence.get("target_update_succeeded") is True:
                return "canonical_deploy"
            return "canonical_deploy_attempted_failed"
        # Pre-Track-1 manifest: phase-8 PASS without evidence block.
        # Status PASS without dry_run is sufficient signal that target update
        # succeeded (deploy_pipeline returns FAIL when az update returncode is
        # nonzero). _confidence='medium' until Track 1 supplies the explicit
        # booleans (per scoping sec 7.2 ceiling + Codex -006 condition 3).
        return "canonical_deploy"
    if status == "FAIL":
        return "canonical_deploy_attempted_failed"
    if status == "SKIP":
        return "canonical_pipeline_run"
    return "canonical_pipeline_run"  # Unknown status: conservative.


def _confidence_for_canonical_deploy(manifest: dict[str, Any]) -> str:
    """Compute provisional _confidence for a canonical_deploy row.

    Per Codex -006 condition 3: pre-Track-1 deploy rows must not exceed
    'medium'. Even with full deploy_evidence, ingest emits provisional
    'medium'; reconciliation upgrades to 'high' only when Azure revision
    matches (per `_reconcile_against_azure_revisions` confidence-upgrade rule).
    """
    return "medium"


def _ingest_canonical_pipeline_manifests(
    conn: sqlite3.Connection,
    project_root: Path,
) -> dict[str, int]:
    """Walk `logs/deploy-result-*.json` and ingest each as a delivery_timeline_events row.

    Idempotent via query-before-insert using the `source` column as stable
    manifest identity (relative path of the manifest file). Per Codex GO
    `-004` on `bridge/gtkb-dora-001b-track2-implementation-003.md` sec 2.4.

    Returns counts dict: manifests_seen, rows_inserted, rows_skipped, rows_invalid.
    """
    counts = {
        "manifests_seen": 0,
        "rows_inserted": 0,
        "rows_skipped": 0,
        "rows_invalid": 0,
    }
    logs_dir = project_root / "logs"
    if not logs_dir.is_dir():
        return counts

    for manifest_path in sorted(logs_dir.glob("deploy-result-*.json")):
        counts["manifests_seen"] += 1
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            counts["rows_invalid"] += 1
            continue
        if not isinstance(manifest, dict):
            counts["rows_invalid"] += 1
            continue

        # Stable manifest identity in the existing `source` column.
        # Forward-slash normalization for cross-platform stability.
        relative_source = str(manifest_path.relative_to(project_root)).replace("\\", "/")

        # Query-before-insert dedup (no DB-level UNIQUE per scoping
        # design; the per-row WHERE clause filters by _authority_source
        # so non-manifest rows with overlapping `source` strings are
        # not affected).
        existing = conn.execute(
            "SELECT 1 FROM delivery_timeline_events "
            "WHERE _authority_source = 'canonical_manifest' "
            "AND source = ? LIMIT 1",
            (relative_source,),
        ).fetchone()
        if existing is not None:
            counts["rows_skipped"] += 1
            continue

        # Classify, then build the row.
        event_kind = _classify_manifest(manifest)
        evidence = manifest.get("deploy_evidence", {}) or {}
        commit_sha = str(manifest.get("repo_commit") or "")
        version = str(manifest.get("version") or "")
        timestamp = str(manifest.get("started_at") or "")

        # Confidence per scoping sec 7.2: ingest emits provisional
        # 'medium' for canonical_deploy; non-deployment kinds get 'low'.
        if event_kind == "canonical_deploy":
            confidence = _confidence_for_canonical_deploy(manifest)
        elif event_kind == "canonical_deploy_attempted_failed":
            confidence = "medium"
        else:
            confidence = "low"

        image_ref = str(evidence.get("image") or "")
        image_tag = str(evidence.get("image_tag") or version)
        revision_name = str(evidence.get("revision_name") or "")
        deployed_at = str(evidence.get("target_verified_at") or "")
        environment = str(manifest.get("environment") or "")

        # DORA-001b Track 2 NO-GO -006 follow-on (S309): production
        # `delivery_timeline_events` declares NOT NULL on multiple legacy
        # columns (sort_order, stage, stage_label, date_label, version,
        # branch, result_color, test_results). The S308 implementation
        # omitted them from this INSERT, which only worked in unit tests
        # because the bespoke `_make_conn()` fixture relaxed the constraints.
        # Production reproduction (per Codex `-006` F1 + new test T14):
        #   sqlite3.IntegrityError: NOT NULL constraint failed: sort_order
        # Supply schema-compatible values: stage="deploy" matches the
        # canonical_deploy semantic; date_label is the timestamp's date
        # prefix consistent with the legacy ingest pattern at
        # _write_model_to_db's executemany (`str(timestamp)[:10] or "configuration"`);
        # result_color follows status convention (green for SUCCESS).
        manifest_status = str(manifest.get("status") or "")
        result_color = "green" if manifest_status == "SUCCESS" else "red"
        date_label = (timestamp[:10] if timestamp else "") or "configuration"

        conn.execute(
            """
            INSERT INTO delivery_timeline_events (
                sort_order, stage, stage_label, event, timestamp, date_label,
                version, commit_sha, branch, result, result_color, test_results,
                source, environment, notes,
                event_kind, deployable_change_id, commit_range_start, commit_range_end,
                rollback_of_deploy_id, hotfix_of_deploy_id,
                _authority_source, _image_ref, _image_tag, _revision_name,
                _deployed_at, _consistency, _confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                0,  # sort_order: canonical_manifest rows are an additive overlay; consumers sort by timestamp.
                "deploy",
                "Deploy",
                f"canonical_pipeline_run version={version}",
                timestamp,
                date_label,
                version,
                commit_sha,
                "",  # branch: not recorded in deploy-result manifests.
                manifest_status,
                result_color,
                "",  # test_results: separate concern; canonical_manifest doesn't carry this.
                relative_source,
                environment,
                f"deploy-result manifest; phases={manifest.get('phases_completed', 0)}/{manifest.get('phases_total', 0)}",
                event_kind,
                "",  # deployable_change_id; populated by _enrich_timeline_events when relevant
                commit_sha,
                commit_sha,
                "",
                "",
                "canonical_manifest",
                image_ref,
                image_tag,
                revision_name,
                deployed_at,
                "unknown",  # _consistency upgraded by reconciliation
                confidence,
            ),
        )
        counts["rows_inserted"] += 1

    return counts


def _azure_reconciliation_enabled() -> bool:
    """Return true only when live Azure reconciliation is explicitly enabled."""
    return os.environ.get("GTKB_DASHBOARD_AZURE_RECONCILE", "").strip().lower() in _TRUE_ENV_VALUES


def _azure_container_app_map(environments: list[str]) -> dict[str, str]:
    """Return an application-supplied environment -> container-app map.

    GT-KB owns only the dashboard contract. The active application owns the
    concrete deployment environment and supplies this mapping when it opts into
    Azure reconciliation.
    """
    raw = os.environ.get(_AZURE_CONTAINER_APP_MAP_ENV, "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    allowed = set(environments)
    return {str(env): str(app).strip() for env, app in payload.items() if str(env) in allowed and str(app).strip()}


def _reconcile_against_azure_revisions(
    conn: sqlite3.Connection,
    environments: list[str],
) -> dict[str, int]:
    """Cross-check canonical_deploy rows against Azure Container Apps revision history.

    Per Codex GO `-004` on `bridge/gtkb-dora-001b-track2-implementation-003.md`
    sec 2.5 + scoping sec 6 graceful-degradation contract:

      - All exceptions caught (subprocess errors, FileNotFoundError if az CLI
        missing, JSONDecodeError, generic Exception).
      - Per-row degradation: failed rows get _consistency='unknown'.
      - Single WARNING per pass, not per row.
      - refresh_runs.status UNAFFECTED by reconciliation outcome.

    Confidence upgrade: when reconciliation confirms an Azure revision matches
    the manifest's recorded image AND the manifest has full deploy_evidence,
    upgrade _confidence from provisional 'medium' to 'high'.

    Returns counts dict: rows_checked, rows_matched, rows_drift, rows_unknown.
    """
    counts = {
        "rows_checked": 0,
        "rows_matched": 0,
        "rows_drift": 0,
        "rows_unknown": 0,
    }
    if not environments:
        return counts

    container_apps = _azure_container_app_map(environments)
    resource_group = os.environ.get(_AZURE_RESOURCE_GROUP_ENV, "").strip()
    if not container_apps or not resource_group:
        print(
            "[refresh_dashboard_db] WARNING: Azure reconciliation skipped; "
            f"application-owned {_AZURE_CONTAINER_APP_MAP_ENV} and {_AZURE_RESOURCE_GROUP_ENV} are required.",
            file=sys.stderr,
        )
        return counts

    azure_revisions: dict[str, list[dict[str, Any]]] = {}
    az_failure_logged = False
    for env in environments:
        try:
            container_app = container_apps.get(env)
            if container_app is None:
                continue
            result = subprocess.run(
                [
                    "az",
                    "containerapp",
                    "revision",
                    "list",
                    "--name",
                    container_app,
                    "--resource-group",
                    resource_group,
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode != 0:
                if not az_failure_logged:
                    print(
                        f"[refresh_dashboard_db] WARNING: Azure reconciliation "
                        f"degraded; az containerapp revision list returned "
                        f"{result.returncode} for {env}",
                        file=sys.stderr,
                    )
                    az_failure_logged = True
                continue
            azure_revisions[env] = json.loads(result.stdout)
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            json.JSONDecodeError,
            Exception,  # noqa: BLE001  # graceful-degradation contract requires catching all
        ) as exc:
            if not az_failure_logged:
                print(
                    f"[refresh_dashboard_db] WARNING: Azure reconciliation "
                    f"degraded; {type(exc).__name__} querying revisions for "
                    f"{env}: {exc}",
                    file=sys.stderr,
                )
                az_failure_logged = True
            continue

    # Pull canonical_deploy rows that are still 'unknown' or could be upgraded.
    rows = conn.execute(
        "SELECT rowid, environment, _image_ref, _image_tag, _revision_name, "
        "_consistency, _confidence "
        "FROM delivery_timeline_events "
        "WHERE _authority_source = 'canonical_manifest' "
        "AND event_kind = 'canonical_deploy'"
    ).fetchall()

    for row in rows:
        counts["rows_checked"] += 1
        rowid, environment, image_ref, image_tag, revision_name, _, _ = row

        if environment not in azure_revisions:
            # Reconciliation unavailable for this row's environment.
            conn.execute(
                "UPDATE delivery_timeline_events SET _consistency = ? WHERE rowid = ?",
                ("unknown", rowid),
            )
            counts["rows_unknown"] += 1
            continue

        # Look for a matching revision by image (full ref) or image_tag.
        match = None
        for revision in azure_revisions[environment]:
            try:
                rev_image = (
                    revision.get("properties", {}).get("template", {}).get("containers", [{}])[0].get("image", "")
                )
            except (AttributeError, IndexError, TypeError):
                continue
            if image_ref and rev_image == image_ref:
                match = revision
                break
            if image_tag and image_tag in rev_image:
                match = revision
                break

        if match is not None:
            new_revision_name = match.get("name", revision_name) or revision_name
            new_confidence = "high" if image_ref and revision_name else "medium"
            conn.execute(
                "UPDATE delivery_timeline_events "
                "SET _consistency = ?, _revision_name = ?, _confidence = ? "
                "WHERE rowid = ?",
                ("both_match", new_revision_name, new_confidence, rowid),
            )
            counts["rows_matched"] += 1
        else:
            conn.execute(
                "UPDATE delivery_timeline_events SET _consistency = ?, _confidence = ? WHERE rowid = ?",
                ("manifest_only", "medium", rowid),
            )
            counts["rows_drift"] += 1

    return counts


def _classify_event_kind(row: dict[str, Any]) -> str:
    """Classify a timeline row into a DORA event kind.

    Source-based rules (checked in order). Pure; depends only on ``source`` and
    ``result`` fields of the row.

    Pre-check (DORA-001b Track 2): canonical_manifest-sourced rows already
    carry an event_kind from `_classify_manifest()`; preserve it instead of
    falling through to the string-heuristic logic below.
    """
    # Track 2 pre-check: respect _authority_source from manifest ingest path.
    if row.get("_authority_source") == "canonical_manifest":
        kind = row.get("event_kind") or row.get("_event_kind")
        if kind in _DORA_AUTHORITATIVE_EVENT_KINDS:
            return kind

    source = str(row.get("source") or "")
    result = str(row.get("result") or "")
    if source == "git log":
        return "change"
    if source.startswith(".github/workflows/"):
        if result == "configured":
            return "config"
        return "workflow_run"
    lowered = source.lower()
    if lowered.startswith("scripts/deploy/"):
        if "rollback" in lowered:
            return "rollback"
        if "hotfix" in lowered:
            return "hotfix"
        if "restore" in lowered:
            return "restore"
        if lowered.endswith((".ps1", ".yaml", ".yml")):
            return "config"
    if source.startswith("scripts/") and lowered.endswith((".ps1", ".yaml", ".yml")):
        return "config"
    if source == "GitHub Actions":
        return "workflow_run"
    return "change"


def _timestamp_unix(ts: Any) -> int:
    """Best-effort ISO-8601 timestamp -> epoch seconds. 0 for unparseable."""
    if not ts:
        return 0
    text = str(ts).strip()
    if not text:
        return 0
    normalized = text.replace("Z", "+00:00") if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return int(parsed.timestamp())


def _deployable_change_id(row: dict[str, Any]) -> str:
    """Stable ID for the change this row represents.

    Commit-linked rows produce ``<sha8>-<unix>``; deploy-like rows without a
    commit produce ``derived-<kind>-<sha1_12>``; commits-without-SHA and
    unclassified rows produce ``''``.
    """
    commit = str(row.get("commit") or "").strip()
    if commit:
        return f"{commit[:8]}-{_timestamp_unix(row.get('timestamp'))}"
    event_kind = _classify_event_kind(row)
    if event_kind in {"workflow_run", "config", "rollback", "hotfix", "restore"}:
        basis = f"{row.get('source', '')}|{row.get('timestamp', '')}|{row.get('event', '')}"
        digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
        return f"derived-{event_kind}-{digest}"
    return ""


def _link_rollback_hotfix(rows: list[dict[str, Any]]) -> None:
    """Mutates ``rows`` in place: set ``_rollback_of_deploy_id`` /
    ``_hotfix_of_deploy_id`` on rollback/hotfix events by finding the nearest
    preceding ``workflow_run`` row within a 7-day window.
    """
    runs = sorted(
        (row for row in rows if row["_event_kind"] == "workflow_run" and row["_deployable_change_id"]),
        key=lambda r: _timestamp_unix(r.get("timestamp")),
    )
    for row in rows:
        kind = row["_event_kind"]
        if kind not in ("rollback", "hotfix"):
            continue
        target_ts = _timestamp_unix(row.get("timestamp"))
        if not target_ts:
            continue
        best: dict[str, Any] | None = None
        best_delta = _ROLLBACK_LINK_WINDOW_SECONDS + 1
        for run in runs:
            run_ts = _timestamp_unix(run.get("timestamp"))
            if run_ts <= 0 or run_ts > target_ts:
                continue
            delta = target_ts - run_ts
            if delta > _ROLLBACK_LINK_WINDOW_SECONDS:
                continue
            if delta < best_delta:
                best = run
                best_delta = delta
        if best is not None:
            if kind == "rollback":
                row["_rollback_of_deploy_id"] = best["_deployable_change_id"]
            else:
                row["_hotfix_of_deploy_id"] = best["_deployable_change_id"]


def _enrich_timeline_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of ``rows`` with the six DORA-telemetry fields populated."""
    enriched: list[dict[str, Any]] = []
    for row in rows:
        enriched_row = dict(row)
        enriched_row["_event_kind"] = _classify_event_kind(row)
        enriched_row["_deployable_change_id"] = _deployable_change_id(row)
        commit_sha = str(row.get("commit") or "").strip()
        enriched_row["_commit_range_start"] = commit_sha
        enriched_row["_commit_range_end"] = commit_sha
        enriched_row["_rollback_of_deploy_id"] = ""
        enriched_row["_hotfix_of_deploy_id"] = ""
        enriched.append(enriched_row)
    _link_rollback_hotfix(enriched)
    return enriched


_INCIDENT_REQUIRED_FIELDS = ("incident_id", "title", "severity", "detected_at")


def _load_incidents(
    project_root: Path,
    conn: sqlite3.Connection,
    known_deploy_ids: set[str],
) -> None:
    """Replace rows in ``incidents`` from ``memory/incidents.yaml``.

    Absent file => empty table. Malformed YAML raises ``IncidentIngestError``.
    Entries referencing a ``caused_by_deploy_id`` not seen in the current
    timeline are still inserted; a warning is logged for visibility.
    """
    _replace_table(conn, "incidents")
    incidents_path = project_root / INCIDENTS_PATH
    if not incidents_path.is_file():
        return
    try:
        raw = incidents_path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(raw)
    except (OSError, yaml.YAMLError) as exc:
        raise IncidentIngestError(f"Failed to read or parse {incidents_path}: {exc}") from exc
    if parsed is None:
        return
    if not isinstance(parsed, list):
        raise IncidentIngestError(f"{incidents_path} must be a YAML list of incident objects")
    rows: list[tuple[Any, ...]] = []
    for index, entry in enumerate(parsed):
        if not isinstance(entry, dict):
            raise IncidentIngestError(f"{incidents_path}[{index}] must be a mapping, got {type(entry).__name__}")
        missing = [field for field in _INCIDENT_REQUIRED_FIELDS if not entry.get(field)]
        if missing:
            raise IncidentIngestError(f"{incidents_path}[{index}] is missing required fields: {missing}")
        caused_by = str(entry.get("caused_by_deploy_id") or "")
        if caused_by and caused_by not in known_deploy_ids:
            logger.warning(
                "Incident %s references unknown deploy id %s; inserting anyway.",
                entry.get("incident_id"),
                caused_by,
            )
        rows.append(
            (
                str(entry["incident_id"]),
                str(entry["title"]),
                str(entry["severity"]),
                caused_by,
                str(entry["detected_at"]),
                entry.get("mitigated_at"),
                entry.get("closed_at"),
                str(entry.get("description") or ""),
                str(entry.get("source") or str(incidents_path)),
            )
        )
    if rows:
        conn.executemany(
            """
            INSERT INTO incidents
            (incident_id, title, severity, caused_by_deploy_id, detected_at,
             mitigated_at, closed_at, description, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def _kpi_rows(history: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    definitions = {key: (label, group, lower) for key, label, group, lower in KPI_DEFINITIONS}
    rows = []
    for snapshot in history:
        generated_at = snapshot.get("generated_at", "")
        for key, (label, group, lower) in definitions.items():
            value = snapshot.get(key)
            rows.append((generated_at, key, label, value, group, lower))
    return rows


def _metric_count_status(value: Any, *, zero: str = "green", positive: str = "red") -> str:
    """Map a numeric counter to a dashboard status color."""
    try:
        count = int(value)
    except (TypeError, ValueError):
        return "yellow"
    return zero if count == 0 else positive


def _dashboard_subject_scope_label(model: dict[str, Any]) -> str:
    """Render combined GT-KB + adopter scope for dashboard metadata."""
    work_subject = model.get("current_work_subject")
    if not work_subject:
        work_subject = model.get("metrics", {}).get("work_subject", {}).get("current_subject")
    if work_subject and work_subject not in {"platform", "GT-KB", "gt-kb"}:
        return f"Combined operations: GT-KB platform + {work_subject}"
    return "Combined operations: GT-KB platform + active adopter/application"


def _normalize_release_finding(item: Any, *, default_source: str = "release-health") -> dict[str, str]:
    if isinstance(item, str):
        return {"source": default_source, "message": item, "severity": "red"}
    if not isinstance(item, dict):
        return {"source": default_source, "message": str(item), "severity": "yellow"}
    message = str(item.get("message") or item.get("finding") or item.get("summary") or "").strip()
    if not message:
        message = json.dumps(item, sort_keys=True)
    return {
        "source": str(item.get("source") or item.get("category") or default_source).strip() or default_source,
        "message": message,
        "severity": str(item.get("severity") or item.get("status") or "red").strip().lower() or "red",
    }


def _explicit_release_health_findings(intelligence: dict[str, Any]) -> list[dict[str, str]]:
    raw_findings: list[Any] = []
    raw_findings.extend(intelligence.get("release_health_findings") or [])
    release_health = intelligence.get("release_health") or {}
    if isinstance(release_health, dict):
        raw_findings.extend(release_health.get("findings") or [])
    return [_normalize_release_finding(item) for item in raw_findings]


def _has_deferral_boundary(record: dict[str, Any]) -> bool:
    for key in _DEFERRAL_BOUNDARY_KEYS:
        if str(record.get(key) or "").strip():
            return True
    nested = record.get("deferral")
    if isinstance(nested, dict):
        return _has_deferral_boundary(nested)
    return False


def _is_deferred_record(record: dict[str, Any]) -> bool:
    return any(str(record.get(key) or "").strip().lower() == "deferred" for key in _DEFERRAL_STATUS_KEYS)


def _deferred_records_missing_expiry(value: Any, *, path: str = "$", out: list[str] | None = None) -> list[str]:
    missing = [] if out is None else out
    if isinstance(value, dict):
        if _is_deferred_record(value) and not _has_deferral_boundary(value):
            identifier = (
                value.get("id")
                or value.get("work_item_id")
                or value.get("spec_id")
                or value.get("document")
                or value.get("title")
                or path
            )
            missing.append(str(identifier))
        for key, nested in value.items():
            if key == "raw_model_json":
                continue
            _deferred_records_missing_expiry(nested, path=f"{path}.{key}", out=missing)
    elif isinstance(value, list):
        for idx, nested in enumerate(value):
            _deferred_records_missing_expiry(nested, path=f"{path}[{idx}]", out=missing)
    return missing


def _deferral_expiry_findings(model: dict[str, Any] | None) -> list[dict[str, str]]:
    if not model:
        return []
    missing = _deferred_records_missing_expiry(model)
    if not missing:
        return []
    examples = ", ".join(missing[:5])
    suffix = f": {examples}" if examples else ""
    return [
        {
            "source": "deferral-expiry",
            "message": (f"{len(missing)} deferred record(s) lack an expiry, time limit, or resume trigger{suffix}"),
            "severity": "yellow",
        }
    ]


def _run_release_probe(
    project_root: Path, args: list[str], *, timeout: int = 20
) -> subprocess.CompletedProcess[str] | None:
    resolved_args = list(args)
    if resolved_args and resolved_args[0] == "gt":
        resolved_args = [sys.executable, "-m", "groundtruth_kb.cli", *resolved_args[1:]]
    try:
        return subprocess.run(
            resolved_args,
            cwd=project_root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("release-health probe failed: %s", " ".join(args), exc_info=True)
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr=str(exc))


def _run_release_json_probe(project_root: Path, args: list[str], *, timeout: int = 20) -> dict[str, Any] | None:
    result = _run_release_probe(project_root, args, timeout=timeout)
    if result is None:
        return None
    if result.returncode != 0:
        return {"_probe_error": (result.stderr or result.stdout or f"exit {result.returncode}").strip()}
    try:
        return json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        return {"_probe_error": f"invalid JSON from {' '.join(args)}: {exc}"}


def _snapshot_external_cli_auth_env() -> dict[str, str | None]:
    return {key: os.environ.get(key) for key in _EXTERNAL_CLI_AUTH_ENV_KEYS}


def _restore_external_cli_auth_env(snapshot: dict[str, str | None]) -> None:
    for key, value in snapshot.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _github_workflow_live_status(project_root: Path) -> dict[str, Any]:
    workflow_dir = project_root / ".github" / "workflows"
    workflow_files = (
        sorted(path for path in workflow_dir.glob("*.yml") if path.is_file())
        + sorted(path for path in workflow_dir.glob("*.yaml") if path.is_file())
        if workflow_dir.is_dir()
        else []
    )
    base = {
        "order": 1,
        "display_name": "GitHub Actions",
        "gate_role": "release gate",
    }
    if not workflow_files:
        return {
            **base,
            "health": "red",
            "status": "not_wired",
            "latest_run_summary": "No local GitHub Actions workflow files found.",
            "remediation": "Add or restore required workflows under .github/workflows before release signoff.",
        }

    result = _run_release_probe(
        project_root,
        [
            "gh",
            "run",
            "list",
            "--repo",
            _GITHUB_WORKFLOW_REPOSITORY,
            "--branch",
            _GITHUB_WORKFLOW_BRANCH,
            "--limit",
            "20",
            "--json",
            "status,conclusion,workflowName,displayTitle,headBranch,event,createdAt",
        ],
        timeout=20,
    )
    if result is None or result.returncode != 0:
        detail = "probe did not return" if result is None else (result.stderr or result.stdout or "gh run list failed")
        return {
            **base,
            "health": "yellow",
            "status": "live_state_unavailable",
            "latest_run_summary": detail.strip(),
            "remediation": "Authenticate gh and rerun dashboard refresh to collect live workflow state.",
        }
    try:
        runs = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        return {
            **base,
            "health": "yellow",
            "status": "live_state_unavailable",
            "latest_run_summary": f"Invalid gh run list JSON: {exc}",
            "remediation": "Inspect gh CLI output before using workflow state for release signoff.",
        }
    if not isinstance(runs, list) or not runs:
        return {
            **base,
            "health": "yellow",
            "status": "no_recent_run",
            "latest_run_summary": f"No recent runs returned for {_GITHUB_WORKFLOW_REPOSITORY}@{_GITHUB_WORKFLOW_BRANCH}.",
            "remediation": "Trigger or inspect required main-branch workflows before release signoff.",
        }

    latest = runs[0] if isinstance(runs[0], dict) else {}
    workflow_name = str(latest.get("workflowName") or latest.get("displayTitle") or "GitHub Actions")
    status = str(latest.get("status") or "").lower()
    conclusion = str(latest.get("conclusion") or "").lower()
    created_at = str(latest.get("createdAt") or "").strip()
    summary = f"{workflow_name}: status={status or 'unknown'} conclusion={conclusion or 'none'}"
    if created_at:
        summary += f" created_at={created_at}"
    if status and status != "completed":
        return {
            **base,
            "health": "yellow",
            "status": "running",
            "latest_run_summary": summary,
            "remediation": "Wait for in-progress main-branch workflow runs to finish before release signoff.",
        }
    if conclusion == "success":
        return {
            **base,
            "health": "green",
            "status": "passing",
            "latest_run_summary": summary,
            "remediation": "No action required for latest returned main-branch run.",
        }
    return {
        **base,
        "health": "red",
        "status": "failing",
        "latest_run_summary": summary,
        "remediation": "Inspect and repair failing main-branch workflow runs before release signoff.",
    }


def _dispatcher_supervisor_live_status(project_root: Path) -> dict[str, Any]:
    base = {
        "order": 2,
        "display_name": "Dispatcher Daemon Supervisor",
        "gate_role": "release infrastructure",
    }
    status = _run_release_json_probe(
        project_root,
        ["gt", "bridge", "dispatch", "daemon", "supervisor", "status", "--json"],
        timeout=20,
    )
    if not status:
        return {
            **base,
            "health": "yellow",
            "status": "live_state_unavailable",
            "latest_run_summary": "Supervisor status probe did not return.",
            "remediation": "Rerun the dispatcher supervisor status probe before release signoff.",
        }
    probe_error = status.get("_probe_error")
    if probe_error:
        return {
            **base,
            "health": "yellow",
            "status": "live_state_unavailable",
            "latest_run_summary": str(probe_error),
            "remediation": "Repair the dispatcher supervisor status probe before release signoff.",
        }
    registered = bool(status.get("registered"))
    enabled = bool(status.get("enabled"))
    hidden = bool(status.get("hidden"))
    uses_pythonw = bool(status.get("uses_pythonw"))
    healthy = bool(status.get("healthy"))
    summary = f"registered={registered} enabled={enabled} hidden={hidden} uses_pythonw={uses_pythonw} healthy={healthy}"
    if healthy and registered and enabled and hidden and uses_pythonw:
        return {
            **base,
            "health": "green",
            "status": "healthy_headless",
            "latest_run_summary": summary,
            "remediation": "No supervisor action required; route/runtime WARNs are tracked separately.",
        }
    return {
        **base,
        "health": "red",
        "status": "unhealthy_or_visible",
        "latest_run_summary": summary,
        "remediation": "Register and enable the dispatcher supervisor as a hidden pythonw-backed task.",
    }


def _integration_status_rows(
    integrations: dict[str, Any],
    project_root: Path,
    *,
    probe_live_workflows: bool = False,
) -> list[tuple[Any, ...]]:
    merged: dict[str, dict[str, Any]] = {}
    for key, details in integrations.items():
        merged[key] = dict(details) if isinstance(details, dict) else {"display_name": str(details)}
    if probe_live_workflows:
        merged["github"] = {**merged.get("github", {}), **_github_workflow_live_status(project_root)}
        merged["dispatcher_supervisor"] = {
            **merged.get("dispatcher_supervisor", {}),
            **_dispatcher_supervisor_live_status(project_root),
        }
    return [
        (
            int(details.get("order", idx)),
            key,
            details.get("display_name", key),
            details.get("health", ""),
            details.get("status", ""),
            details.get("latest_run_summary", ""),
            details.get("gate_role", ""),
            details.get("remediation", ""),
        )
        for idx, (key, details) in enumerate(merged.items(), start=1)
    ]


def _live_release_health_findings(project_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    git_status = _run_release_probe(project_root, ["git", "status", "--short", "--branch"], timeout=15)
    if git_status and git_status.returncode == 0:
        dirty_paths = [line for line in git_status.stdout.splitlines() if line and not line.startswith("## ")]
        findings.append(
            {
                "source": "git",
                "message": f"Live git dirty worktree path count: {len(dirty_paths)}",
                "severity": "green" if not dirty_paths else "red",
                "metric_key": "dirty_worktree_paths",
                "metric_value": len(dirty_paths),
                "release_visible": False,
            }
        )
        if dirty_paths:
            findings.append(
                {
                    "source": "git",
                    "message": f"Dirty worktree has {len(dirty_paths)} path(s); classify before release commit/push.",
                    "severity": "red",
                }
            )
    elif git_status:
        findings.append(
            {
                "source": "git",
                "message": f"git status probe failed: {(git_status.stderr or git_status.stdout).strip()}",
                "severity": "yellow",
            }
        )

    dispatch_health = _run_release_json_probe(
        project_root, ["gt", "bridge", "dispatch", "health", "--json"], timeout=30
    )
    if dispatch_health:
        probe_error = dispatch_health.get("_probe_error")
        health_status = str(dispatch_health.get("health_status") or "").upper()
        if probe_error:
            findings.append({"source": "dispatcher", "message": probe_error, "severity": "yellow"})
        elif health_status and health_status not in {"PASS", "GREEN", "OK", "HEALTHY"}:
            health_findings = dispatch_health.get("findings") or []
            detail = "; ".join(str(item) for item in health_findings[:3]) or f"status {health_status}"
            findings.append(
                {
                    "source": "dispatcher",
                    "message": f"Dispatcher health is {health_status}: {detail}",
                    "severity": "red" if health_status in {"FAIL", "WARN"} else "yellow",
                }
            )

    daemon_status = _run_release_json_probe(
        project_root, ["gt", "bridge", "dispatch", "daemon", "status", "--json"], timeout=20
    )
    if daemon_status:
        probe_error = daemon_status.get("_probe_error")
        if probe_error:
            findings.append({"source": "dispatcher-daemon", "message": probe_error, "severity": "yellow"})
        else:
            running = bool(daemon_status.get("running"))
            heartbeat_age = daemon_status.get("heartbeat_age_seconds")
            try:
                heartbeat_age_float = float(heartbeat_age)
            except (TypeError, ValueError):
                heartbeat_age_float = None
            if not running:
                findings.append(
                    {"source": "dispatcher-daemon", "message": "Dispatcher daemon is not running.", "severity": "red"}
                )
            elif heartbeat_age_float is not None and heartbeat_age_float > 120:
                findings.append(
                    {
                        "source": "dispatcher-daemon",
                        "message": f"Dispatcher daemon heartbeat is stale ({heartbeat_age_float:.0f}s).",
                        "severity": "red",
                    }
                )

    supervisor_status = _run_release_json_probe(
        project_root, ["gt", "bridge", "dispatch", "daemon", "supervisor", "status", "--json"], timeout=20
    )
    if supervisor_status:
        probe_error = supervisor_status.get("_probe_error")
        if probe_error:
            findings.append({"source": "dispatcher-supervisor", "message": probe_error, "severity": "yellow"})
        else:
            supervisor_unhealthy = not (
                bool(supervisor_status.get("healthy"))
                and bool(supervisor_status.get("registered"))
                and bool(supervisor_status.get("enabled"))
                and bool(supervisor_status.get("hidden"))
                and bool(supervisor_status.get("uses_pythonw"))
            )
            if supervisor_unhealthy:
                findings.append(
                    {
                        "source": "dispatcher-supervisor",
                        "message": "Dispatcher daemon supervisor is not healthy, enabled, and headless.",
                        "severity": "red",
                    }
                )

    dispatch_status = _run_release_json_probe(
        project_root, ["gt", "bridge", "dispatch", "status", "--json"], timeout=30
    )
    if dispatch_status:
        probe_error = dispatch_status.get("_probe_error")
        if probe_error:
            findings.append({"source": "bridge", "message": probe_error, "severity": "yellow"})
        else:
            runtime = dispatch_status.get("runtime_classifications") or []
            pending = sum(int(item.get("pending_count") or 0) for item in runtime if isinstance(item, dict))
            live = sum(int(item.get("live_inflight_dispatch_count") or 0) for item in runtime if isinstance(item, dict))
            if pending or live:
                findings.append(
                    {
                        "source": "bridge",
                        "message": f"Bridge dispatch still has {pending} pending and {live} live in-flight item(s).",
                        "severity": "yellow",
                    }
                )

    return findings[:12]


def _release_health_findings(
    project_root: Path,
    intelligence: dict[str, Any],
    *,
    model: dict[str, Any] | None = None,
    probe_live: bool,
) -> list[dict[str, Any]]:
    findings = _explicit_release_health_findings(intelligence)
    findings.extend(_deferral_expiry_findings(model))
    if probe_live:
        findings.extend(_live_release_health_findings(project_root))
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for finding in findings:
        key = (finding.get("source", ""), finding.get("message", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _release_blocker_messages(release: dict[str, Any], findings: list[dict[str, str]]) -> list[str]:
    messages: list[str] = [str(blocker) for blocker in release.get("blockers", []) if str(blocker).strip()]
    messages.extend(f"[{item['source']}] {item['message']}" for item in _visible_release_findings(findings))
    deduped: list[str] = []
    seen: set[str] = set()
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        deduped.append(message)
    return deduped


def _visible_release_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [finding for finding in findings if finding.get("release_visible", True)]


def _finding_count(findings: list[dict[str, Any]], *sources: str) -> int:
    wanted = set(sources)
    return sum(1 for finding in _visible_release_findings(findings) if finding.get("source") in wanted)


def _finding_status(findings: list[dict[str, Any]]) -> str:
    visible_findings = _visible_release_findings(findings)
    if not visible_findings:
        return "green"
    severities = {str(finding.get("severity") or "").strip().lower() for finding in visible_findings}
    if severities & {"red", "fail", "failed", "failure", "blocker", "critical"}:
        return "red"
    return "yellow"


def _finding_metric_value(findings: list[dict[str, Any]], metric_key: str) -> int | None:
    for finding in findings:
        if finding.get("metric_key") == metric_key:
            return _num(finding.get("metric_value"))
    return None


def _status_rank(status: str) -> int:
    return {"green": 0, "yellow": 1, "red": 2}.get(str(status).strip().lower(), 1)


def _format_count(value: Any, singular: str, plural: str) -> str:
    count = _num(value)
    return f"{count} {singular if count == 1 else plural}"


def _reconciled_health_cards(
    metrics: dict[str, Any],
    intelligence: dict[str, Any],
    release_health_findings: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    cards = [dict(item) for item in intelligence.get("health", []) if isinstance(item, dict)]
    metric_rows = {
        row[0]: {"label": row[1], "value": row[2], "status": row[3], "description": row[4]}
        for row in _current_metric_rows(metrics, intelligence, release_health_findings)
    }

    def upsert(label: str, metric_key: str, singular: str, plural: str, tooltip: str) -> None:
        metric = metric_rows.get(metric_key)
        if not metric:
            return
        replacement = {
            "label": label,
            "value": _format_count(metric["value"], singular, plural),
            "status": metric["status"],
            "tooltip": tooltip,
        }
        for card in cards:
            if str(card.get("label") or "").strip().lower() == label.lower():
                card.update(replacement)
                return
        cards.append(replacement)

    upsert(
        "Project Health",
        "project_health_issues",
        "issue",
        "issues",
        "Failing checks plus visible release blockers.",
    )
    upsert(
        "Release Readiness",
        "release_blockers",
        "blocker",
        "blockers",
        "Visible release blockers from release readiness and live release-health findings.",
    )
    cards.sort(
        key=lambda card: (_status_rank(str(card.get("status") or "")), str(card.get("label") or "")), reverse=True
    )
    return cards


def _current_metric_rows(
    metrics: dict[str, Any],
    intelligence: dict[str, Any],
    release_health_findings: list[dict[str, Any]] | None = None,
) -> list[tuple[Any, ...]]:
    release_health_findings = release_health_findings or []
    visible_findings = _visible_release_findings(release_health_findings)
    release = intelligence.get("release_readiness", {})
    quality = intelligence.get("quality_rollup", {})
    release_blocker_messages = _release_blocker_messages(release, release_health_findings)
    release_blockers = max(
        _num(release.get("blocker_count", metrics.get("regression", {}).get("release_blocker_count", 0))),
        len(release_blocker_messages),
    )
    explicit_release_blockers = bool(release.get("blockers")) or _num(
        release.get("blocker_count", metrics.get("regression", {}).get("release_blocker_count", 0))
    )
    release_health_status = _finding_status(release_health_findings)
    release_blocker_status = (
        "green"
        if release_blockers == 0
        else "red"
        if explicit_release_blockers or release_health_status == "red"
        else "yellow"
    )
    project_health = _num(quality.get("failing", 0)) + _num(release_blockers)
    ci_failing = quality.get("failing", 0)
    bridge_actionable = metrics.get("contention", {}).get("actionable_count", 0)
    live_dirty_paths = _finding_metric_value(release_health_findings, "dirty_worktree_paths")
    dirty_paths = (
        live_dirty_paths if live_dirty_paths is not None else metrics.get("drift", {}).get("changed_path_count", 0)
    )
    dirty_path_description = (
        "Changed paths from live git status; release prep must classify dirty paths before push."
        if live_dirty_paths is not None
        else "Changed paths from the current dashboard model; release prep must classify dirty paths before push."
    )
    dispatcher_findings = _finding_count(
        release_health_findings, "dispatcher", "dispatcher-daemon", "dispatcher-supervisor"
    )
    bridge_findings = _finding_count(release_health_findings, "bridge")
    docs_drift_findings = _finding_count(release_health_findings, "readme", "wiki", "docs", "readme-wiki")
    return [
        (
            "project_health_issues",
            "Project Health Issues",
            project_health,
            _metric_count_status(project_health),
            "Failing checks plus release blockers.",
        ),
        (
            "release_blockers",
            "Release Blockers",
            release_blockers,
            release_blocker_status,
            "Visible release blocker count.",
        ),
        (
            "release_health_findings",
            "Release Health Findings",
            len(visible_findings),
            release_health_status,
            "Live release-health findings from git, bridge, dispatcher, README/wiki, and supplied model evidence.",
        ),
        (
            "dirty_worktree_paths",
            "Dirty Worktree Paths",
            dirty_paths,
            _metric_count_status(dirty_paths),
            dirty_path_description,
        ),
        (
            "dispatcher_health_findings",
            "Dispatcher Health Findings",
            dispatcher_findings,
            _metric_count_status(dispatcher_findings),
            "Dispatcher daemon/control-surface findings that block a clean release-health read.",
        ),
        (
            "bridge_actionability_findings",
            "Bridge Actionability Findings",
            bridge_findings,
            _metric_count_status(bridge_findings, positive="yellow"),
            "Live bridge actionability or in-flight dispatch findings.",
        ),
        (
            "readme_wiki_drift",
            "README / Wiki Drift",
            docs_drift_findings,
            _metric_count_status(docs_drift_findings),
            "README/wiki drift findings from the governed wiki comparison source.",
        ),
        (
            "ci_testing_failing",
            "CI / Testing Failing",
            ci_failing,
            _metric_count_status(ci_failing),
            "Failing integration/tool checks.",
        ),
        (
            "security_scan_posture",
            "Security Scan Posture",
            quality.get("ready_or_passing", 0),
            "green" if _num(quality.get("failing", 0)) == 0 else "yellow",
            "Ready or passing checks.",
        ),
        (
            "governance_bridge_items",
            "Governance Bridge Items",
            bridge_actionable,
            "green" if _num(bridge_actionable) == 0 else "yellow",
            "Actionable bridge/contention entries.",
        ),
        ("data_freshness", "Data Freshness", 1, "green", "Live probe freshness status."),
    ]


def _data_freshness_rows(freshness: dict[str, Any]) -> list[tuple[str, str, str]]:
    values = {
        "generated_at": ("Generated At", freshness.get("generated_at", "")),
        "groundtruth_db_modified_at": ("GroundTruth DB Modified", freshness.get("groundtruth_db_modified_at", "")),
        "repo_branch": ("Repo Branch", freshness.get("repo_branch", "")),
        "repo_short_sha": ("Repo SHA", freshness.get("repo_short_sha", "")),
        "scope_version": ("Scope Version", freshness.get("scope_version", "")),
        "sources": ("Sources", ", ".join(str(source) for source in freshness.get("sources", []))),
    }
    return [(key, label, str(value)) for key, (label, value) in values.items()]


def _setup_step_rows() -> list[tuple[Any, ...]]:
    return [
        (
            idx,
            item["section"],
            item["title"],
            item["instruction"],
            item["command"],
            item["link_label"],
            item["link_url"],
        )
        for idx, item in enumerate(SETUP_STEPS, start=1)
    ]


def _required_tool_rows() -> list[tuple[Any, ...]]:
    return [
        (
            idx,
            item["name"],
            item["category"],
            item["purpose"],
            item["check_command"],
            item["install_reference"],
            item.get("status", "documented"),
        )
        for idx, item in enumerate(REQUIRED_TOOLS, start=1)
    ]


def _third_party_service_rows() -> list[tuple[Any, ...]]:
    return [
        (
            idx,
            item["name"],
            item["category"],
            item["purpose"],
            item["required_env_vars"],
            item["setup_summary"],
            item["console_url"],
            item["health_signal"],
        )
        for idx, item in enumerate(THIRD_PARTY_SERVICES, start=1)
    ]


def _application_deployment_signal_rows() -> list[tuple[Any, ...]]:
    return [
        (
            idx,
            surface,
            signal,
            mock_value,
            status,
            source_contract,
        )
        for idx, (surface, signal, mock_value, status, source_contract) in enumerate(
            APPLICATION_DEPLOYMENT_SIGNALS, start=1
        )
    ]


def _num(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--init-only", action="store_true", help="Initialize schema without collecting fresh data.")
    parser.add_argument(
        "--full-startup-model",
        action="store_true",
        help="Use the full startup model path instead of the bounded fast-hook dashboard refresh path.",
    )
    parser.add_argument(
        "--probe-live",
        action="store_true",
        help="Run live git, bridge dispatcher, and GitHub workflow probes during refresh.",
    )
    args = parser.parse_args(argv)

    if args.init_only:
        initialize_database(args.db_path)
        print(f"Initialized {args.db_path}")
        return 0

    result = refresh_database(
        args.db_path,
        args.project_root,
        fast_startup_model=not args.full_startup_model,
        probe_live=args.probe_live,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
