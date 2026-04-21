"""
Local operations dashboard support for GroundTruth KB projects.

The dashboard is intentionally generated from the pip-installed package so an
adopter can evaluate a project without copying repository-local scripts.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb import __version__
from groundtruth_kb.config import GTConfig

SQLITE_PLUGIN_ID = "frser-sqlite-datasource"
SQLITE_DATASOURCE_UID = "gtkb-dashboard-sqlite"
GRAFANA_DASHBOARD_UID = "groundtruth-kb"
DEFAULT_GRAFANA_PORT = 3000
DEFAULT_REFRESH_PORT = 8766
DEFAULT_REFRESH_INTERVAL_MINUTES = 60


@dataclass(frozen=True)
class DashboardPaths:
    """Resolved local paths used by the dashboard runtime."""

    project_root: Path
    db_path: Path
    runtime_root: Path
    grafana_home: Path
    provisioning_dir: Path
    dashboards_dir: Path
    logs_dir: Path
    pids_dir: Path


@dataclass(frozen=True)
class DashboardProcessInfo:
    """Process IDs and user-facing URLs produced by ``start_dashboard``."""

    grafana_pid: int
    refresh_pid: int
    grafana_url: str
    refresh_url: str


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dashboard_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS health_cards (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    value TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS shortcuts (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    target TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS action_center (
    id TEXT PRIMARY KEY,
    priority TEXT NOT NULL,
    title TEXT NOT NULL,
    owner TEXT NOT NULL,
    next_action TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS release_blockers (
    id TEXT PRIMARY KEY,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    evidence TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS quality_rollup (
    id TEXT PRIMARY KEY,
    area TEXT NOT NULL,
    status TEXT NOT NULL,
    command TEXT NOT NULL,
    last_result TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_register (
    id TEXT PRIMARY KEY,
    severity TEXT NOT NULL,
    risk TEXT NOT NULL,
    mitigation TEXT NOT NULL,
    owner TEXT NOT NULL,
    status TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS integration_status (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    purpose TEXT NOT NULL,
    required_for TEXT NOT NULL,
    setup_status TEXT NOT NULL,
    verification_command TEXT NOT NULL,
    notes TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS kpi_snapshots (
    id TEXT PRIMARY KEY,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS current_metrics (
    key TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS data_freshness (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    last_refreshed TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS setup_steps (
    id TEXT PRIMARY KEY,
    step_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    command TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    troubleshooting TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS required_tools (
    id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    required TEXT NOT NULL,
    purpose TEXT NOT NULL,
    install_command TEXT NOT NULL,
    verify_command TEXT NOT NULL,
    notes TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS third_party_services (
    id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    required_for TEXT NOT NULL,
    credentials_needed TEXT NOT NULL,
    data_shared TEXT NOT NULL,
    setup_notes TEXT NOT NULL,
    operational_owner TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);
"""


SETUP_STEPS = [
    (
        "install-package",
        1,
        "Install the package",
        "pip install groundtruth-kb",
        "The gt command is available and gt --version prints the installed version.",
        "Use python -m pip install --upgrade pip if pip is stale.",
    ),
    (
        "create-project",
        2,
        "Create a project",
        "gt project init my-project --profile local-only",
        "groundtruth.toml, groundtruth.db, and scaffold files are created.",
        "Use --dir for an explicit target directory.",
    ),
    (
        "doctor",
        3,
        "Verify workstation readiness",
        "gt project doctor",
        "Required checks pass; optional integrations are reported clearly.",
        "Install missing required tools before continuing.",
    ),
    (
        "dashboard-init",
        4,
        "Generate dashboard assets",
        "gt dashboard init",
        ".groundtruth/dashboard contains Grafana provisioning and dashboard JSON.",
        "Run from the project root or pass --dir.",
    ),
    (
        "dashboard-install",
        5,
        "Install local Grafana",
        "gt dashboard install",
        "Grafana OSS is present with the SQLite datasource plugin.",
        "If corporate policy blocks download, install Grafana and the plugin manually.",
    ),
    (
        "dashboard-start",
        6,
        "Start the dashboard",
        "gt dashboard start",
        "Grafana opens at http://127.0.0.1:3000/d/groundtruth-kb/groundtruth-kb-dashboard.",
        "Run gt dashboard refresh if the panels look stale.",
    ),
]

REQUIRED_TOOLS = [
    (
        "python",
        "Python 3.11+",
        "yes",
        "Runs the package and gt CLI.",
        "Install from https://www.python.org/downloads/ or your enterprise package manager.",
        "python --version",
        "Use the same Python environment for pip and gt.",
    ),
    ("pip", "pip", "yes", "Installs groundtruth-kb from PyPI.", "Bundled with Python.", "python -m pip --version", ""),
    (
        "git",
        "Git",
        "yes",
        "Provides version control and project provenance.",
        "Install from https://git-scm.com/downloads.",
        "git --version",
        "",
    ),
    (
        "grafana",
        "Grafana OSS",
        "dashboard",
        "Renders the operations dashboard from the generated SQLite reporting DB.",
        "gt dashboard install",
        "grafana-server --version",
        "The local installer keeps Grafana under .groundtruth/tools/grafana by default.",
    ),
    (
        "sqlite-plugin",
        "frser SQLite datasource",
        "dashboard",
        "Lets Grafana query the generated gtkb-dashboard.sqlite file.",
        "gt dashboard install",
        "grafana-cli plugins ls",
        "Plugin ID: frser-sqlite-datasource.",
    ),
    (
        "claude-code",
        "Claude Code",
        "dual-agent",
        "Common Prime Builder harness for implementation sessions.",
        "Install and authenticate from Anthropic's current Claude Code instructions.",
        "claude --version",
        "Not bundled or credential-managed by GroundTruth-KB.",
    ),
    (
        "codex",
        "Codex",
        "dual-agent",
        "Common Loyal Opposition harness for independent review sessions.",
        "Install and authenticate using OpenAI's current Codex instructions.",
        "codex --version",
        "Not required for local-only evaluation.",
    ),
]

THIRD_PARTY_SERVICES = [
    (
        "pypi",
        "PyPI",
        "package registry",
        "Installing groundtruth-kb with pip.",
        "None for public package install.",
        "Package name, version, and installer telemetry handled by PyPI/pip.",
        "Use an enterprise package proxy if policy requires it.",
        "Adopter IT or development lead",
    ),
    (
        "github",
        "GitHub",
        "source control and CI",
        "Repository hosting, pull requests, GitHub Actions, CodeQL, Dependabot.",
        "GitHub account/token for private repositories or pushing changes.",
        "Repository contents, workflow logs, dependency manifests.",
        "Local-only mode can run without GitHub; team mode normally uses it.",
        "Repository owner",
    ),
    (
        "sonarcloud",
        "SonarCloud",
        "quality analysis",
        "Quality gate badge and hosted code-quality analysis for this package.",
        "Sonar token when running analysis from CI.",
        "Source metadata and analysis results.",
        "Optional for adopters; use equivalent internal quality tooling if required.",
        "Engineering lead",
    ),
    (
        "grafana",
        "Grafana OSS",
        "local dashboard runtime",
        "Rendering the GT-KB operations dashboard.",
        "No cloud credential for local OSS runtime.",
        "Local dashboard SQLite data; remains on workstation unless exposed.",
        "The packaged installer downloads Grafana and the SQLite datasource plugin.",
        "Evaluator workstation owner",
    ),
    (
        "chromadb",
        "ChromaDB",
        "local vector search",
        "Optional semantic search for the Deliberation Archive.",
        "None for local embedded use.",
        "Derived local embeddings/index content.",
        'Install with pip install "groundtruth-kb[search]" when semantic search is needed.',
        "Project owner",
    ),
    (
        "anthropic",
        "Anthropic Claude Code",
        "AI coding harness",
        "Prime Builder sessions in the default dual-agent setup.",
        "Anthropic account/API authentication managed outside GroundTruth-KB.",
        "Prompts, tool context, and files you expose to Claude Code.",
        "GroundTruth-KB scaffolds instructions; it does not manage credentials.",
        "Harness user",
    ),
    (
        "openai",
        "OpenAI Codex",
        "AI review harness",
        "Loyal Opposition sessions in the default dual-agent setup.",
        "OpenAI account/API authentication managed outside GroundTruth-KB.",
        "Prompts, tool context, and files you expose to Codex.",
        "GroundTruth-KB scaffolds instructions; it does not manage credentials.",
        "Harness user",
    ),
]


def resolve_dashboard_paths(
    config: GTConfig,
    *,
    db_path: Path | None = None,
    runtime_root: Path | None = None,
    grafana_home: Path | None = None,
) -> DashboardPaths:
    """Resolve dashboard paths relative to a GroundTruth project."""
    project_root = config.project_root.resolve()
    runtime = (runtime_root or project_root / ".groundtruth" / "dashboard").resolve()
    grafana = (grafana_home or project_root / ".groundtruth" / "tools" / "grafana").resolve()
    reporting_db = (db_path or runtime / "gtkb-dashboard.sqlite").resolve()
    provisioning = runtime / "grafana" / "provisioning"
    dashboards = runtime / "grafana" / "dashboards"
    return DashboardPaths(
        project_root=project_root,
        db_path=reporting_db,
        runtime_root=runtime,
        grafana_home=grafana,
        provisioning_dir=provisioning,
        dashboards_dir=dashboards,
        logs_dir=runtime / "logs",
        pids_dir=runtime / "pids",
    )


def initialize_dashboard(paths: DashboardPaths, config: GTConfig) -> None:
    """Create dashboard directories, refresh data, and write Grafana assets."""
    for directory in (
        paths.db_path.parent,
        paths.runtime_root,
        paths.provisioning_dir / "datasources",
        paths.provisioning_dir / "dashboards",
        paths.dashboards_dir,
        paths.logs_dir,
        paths.pids_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    refresh_dashboard_db(paths, config)
    write_grafana_assets(paths, config)


def refresh_dashboard_db(paths: DashboardPaths, config: GTConfig) -> None:
    """Refresh the generated reporting SQLite DB used by Grafana."""
    paths.db_path.parent.mkdir(parents=True, exist_ok=True)
    captured_at = _now()
    source_counts = _source_counts(config.db_path)
    git_state = _git_state(paths.project_root)

    with sqlite3.connect(paths.db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        for table in (
            "dashboard_metadata",
            "health_cards",
            "shortcuts",
            "action_center",
            "release_blockers",
            "quality_rollup",
            "risk_register",
            "integration_status",
            "kpi_snapshots",
            "current_metrics",
            "data_freshness",
            "setup_steps",
            "required_tools",
            "third_party_services",
        ):
            conn.execute(f"DELETE FROM {table}")

        metadata = {
            "package_version": __version__,
            "app_title": config.app_title,
            "project_root": str(paths.project_root),
            "source_db": str(config.db_path),
            "dashboard_db": str(paths.db_path),
            "git_branch": git_state.get("branch", "unknown"),
            "git_commit": git_state.get("commit", "unknown"),
            "captured_at": captured_at,
        }
        conn.executemany(
            "INSERT INTO dashboard_metadata(key, value, updated_at) VALUES (?, ?, ?)",
            [(key, value, captured_at) for key, value in metadata.items()],
        )

        _insert_health_cards(conn, source_counts)
        _insert_shortcuts(conn, paths)
        _insert_action_center(conn, source_counts)
        _insert_release_blockers(conn, config)
        _insert_quality_rollup(conn)
        _insert_risks(conn)
        _insert_integrations(conn)
        _insert_current_metrics(conn, source_counts)
        _insert_kpis(conn, source_counts, captured_at)
        _insert_freshness(conn, config, paths, captured_at)
        _insert_setup(conn)
        _insert_required_tools(conn)
        _insert_third_party_services(conn)


def write_grafana_assets(paths: DashboardPaths, config: GTConfig) -> None:
    """Write Grafana provisioning files and dashboard JSON."""
    datasource_dir = paths.provisioning_dir / "datasources"
    dashboard_provider_dir = paths.provisioning_dir / "dashboards"
    datasource_dir.mkdir(parents=True, exist_ok=True)
    dashboard_provider_dir.mkdir(parents=True, exist_ok=True)
    paths.dashboards_dir.mkdir(parents=True, exist_ok=True)

    datasource = f"""\
apiVersion: 1
datasources:
  - name: GroundTruth KB Dashboard
    uid: {SQLITE_DATASOURCE_UID}
    type: {SQLITE_PLUGIN_ID}
    access: proxy
    isDefault: true
    jsonData:
      path: "{paths.db_path.as_posix()}"
"""
    (datasource_dir / "gtkb-dashboard-sqlite.yml").write_text(datasource, encoding="utf-8")

    provider = f"""\
apiVersion: 1
providers:
  - name: GroundTruth KB
    orgId: 1
    folder: GroundTruth KB
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 30
    options:
      path: "{paths.dashboards_dir.as_posix()}"
"""
    (dashboard_provider_dir / "gtkb-dashboard.yml").write_text(provider, encoding="utf-8")
    (paths.dashboards_dir / "groundtruth-kb-dashboard.json").write_text(
        json.dumps(_dashboard_json(config), indent=2),
        encoding="utf-8",
    )


def install_grafana(paths: DashboardPaths, *, skip_download: bool = False, skip_plugin: bool = False) -> Path:
    """Install Grafana OSS locally and install the SQLite datasource plugin."""
    paths.grafana_home.mkdir(parents=True, exist_ok=True)
    grafana_bin = find_grafana_server(paths.grafana_home)
    if grafana_bin is None and skip_download:
        raise FileNotFoundError(
            f"Grafana was not found under {paths.grafana_home}. "
            "Run without --skip-download or set --grafana-home to an existing installation."
        )
    if grafana_bin is None:
        _download_grafana_windows(paths.grafana_home)
        grafana_bin = find_grafana_server(paths.grafana_home)
    if grafana_bin is None:
        raise FileNotFoundError(f"Grafana server executable was not found under {paths.grafana_home}")
    if not skip_plugin:
        _install_sqlite_plugin(paths.grafana_home)
    return grafana_bin


def start_dashboard(
    paths: DashboardPaths,
    config: GTConfig,
    *,
    grafana_port: int = DEFAULT_GRAFANA_PORT,
    refresh_port: int = DEFAULT_REFRESH_PORT,
    interval_minutes: int = DEFAULT_REFRESH_INTERVAL_MINUTES,
) -> DashboardProcessInfo:
    """Start the refresh service and Grafana using local dashboard assets."""
    initialize_dashboard(paths, config)
    grafana_bin = find_grafana_server(paths.grafana_home) or shutil.which("grafana-server")
    if grafana_bin is None:
        raise FileNotFoundError("Grafana is not installed. Run `gt dashboard install` first.")

    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    paths.pids_dir.mkdir(parents=True, exist_ok=True)
    refresh_log = (paths.logs_dir / "refresh-service.log").open("a", encoding="utf-8")
    grafana_log = (paths.logs_dir / "grafana.log").open("a", encoding="utf-8")

    refresh_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.dashboard_service",
            "--config",
            str(config_path_for_project(paths.project_root)),
            "--db-path",
            str(paths.db_path),
            "--runtime-root",
            str(paths.runtime_root),
            "--port",
            str(refresh_port),
            "--interval-minutes",
            str(interval_minutes),
        ],
        cwd=paths.project_root,
        stdout=refresh_log,
        stderr=subprocess.STDOUT,
    )
    grafana_env = os.environ.copy()
    grafana_env.update(
        {
            "GF_PATHS_DATA": str(paths.runtime_root / "grafana-data"),
            "GF_PATHS_LOGS": str(paths.logs_dir),
            "GF_PATHS_PLUGINS": str(paths.grafana_home / "data" / "plugins"),
            "GF_PATHS_PROVISIONING": str(paths.provisioning_dir),
            "GF_SERVER_HTTP_PORT": str(grafana_port),
            "GF_SERVER_HTTP_ADDR": "127.0.0.1",
            "GF_ANALYTICS_REPORTING_ENABLED": "false",
            "GF_ANALYTICS_CHECK_FOR_UPDATES": "false",
        }
    )
    grafana_proc = subprocess.Popen(
        [str(grafana_bin), "--homepath", str(paths.grafana_home)],
        cwd=paths.grafana_home,
        env=grafana_env,
        stdout=grafana_log,
        stderr=subprocess.STDOUT,
    )
    _write_pid(paths.pids_dir / "refresh-service.pid", refresh_proc.pid)
    _write_pid(paths.pids_dir / "grafana.pid", grafana_proc.pid)
    return DashboardProcessInfo(
        grafana_pid=grafana_proc.pid,
        refresh_pid=refresh_proc.pid,
        grafana_url=f"http://127.0.0.1:{grafana_port}/d/{GRAFANA_DASHBOARD_UID}/groundtruth-kb-dashboard",
        refresh_url=f"http://127.0.0.1:{refresh_port}/",
    )


def stop_dashboard(paths: DashboardPaths) -> list[int]:
    """Stop dashboard processes started by ``start_dashboard``."""
    stopped: list[int] = []
    for pid_file in (paths.pids_dir / "refresh-service.pid", paths.pids_dir / "grafana.pid"):
        if not pid_file.exists():
            continue
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pid_file.unlink(missing_ok=True)
            continue
        if _terminate_pid(pid):
            stopped.append(pid)
        pid_file.unlink(missing_ok=True)
    return stopped


def config_path_for_project(project_root: Path) -> Path:
    """Return the conventional config path for a project root."""
    return project_root / "groundtruth.toml"


def find_grafana_server(grafana_home: Path) -> Path | None:
    """Find a Grafana server executable in an install root."""
    candidates = [
        grafana_home / "bin" / "grafana-server.exe",
        grafana_home / "bin" / "grafana-server",
        grafana_home / "bin" / "grafana.exe",
        grafana_home / "bin" / "grafana",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    nested = list(grafana_home.glob("grafana-*/bin/grafana-server.exe"))
    if nested:
        return nested[0]
    nested = list(grafana_home.glob("grafana-*/bin/grafana-server"))
    return nested[0] if nested else None


def _dashboard_json(config: GTConfig) -> dict[str, Any]:
    datasource = {"type": SQLITE_PLUGIN_ID, "uid": SQLITE_DATASOURCE_UID}
    panels = [
        _table_panel(
            1, "Current Metrics", 0, 0, "SELECT label, value, status, source FROM current_metrics ORDER BY sort_order"
        ),
        _table_panel(
            2,
            "Setup Steps",
            12,
            0,
            "SELECT step_number, title, command, expected_result, status FROM setup_steps ORDER BY step_number",
        ),
        _table_panel(
            3,
            "Third-Party Services",
            0,
            9,
            "SELECT service_name, service_type, required_for, credentials_needed, data_shared "
            "FROM third_party_services ORDER BY sort_order",
        ),
        _table_panel(
            4,
            "Integration Status",
            12,
            9,
            "SELECT name, category, purpose, required_for, setup_status, verification_command "
            "FROM integration_status ORDER BY sort_order",
        ),
        _table_panel(
            5,
            "Action Center",
            0,
            18,
            "SELECT priority, title, owner, next_action, status FROM action_center ORDER BY sort_order",
        ),
        _table_panel(
            6,
            "Risks",
            12,
            18,
            "SELECT severity, risk, mitigation, owner, status FROM risk_register ORDER BY sort_order",
        ),
    ]
    for panel in panels:
        panel["targets"][0]["datasource"] = datasource
    return {
        "uid": GRAFANA_DASHBOARD_UID,
        "title": f"{config.app_title} - GroundTruth KB Dashboard",
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "5m",
        "tags": ["groundtruth-kb", "operations"],
        "panels": panels,
    }


def _table_panel(panel_id: int, title: str, x: int, y: int, sql: str) -> dict[str, Any]:
    return {
        "id": panel_id,
        "type": "table",
        "title": title,
        "gridPos": {"h": 9, "w": 12, "x": x, "y": y},
        "targets": [{"refId": "A", "format": "table", "rawSql": sql}],
        "options": {"showHeader": True, "cellHeight": "sm"},
        "fieldConfig": {"defaults": {}, "overrides": []},
    }


def _source_counts(db_path: Path) -> dict[str, int]:
    counts = {
        "specs_total": 0,
        "specs_verified": 0,
        "specs_implemented": 0,
        "work_items_open": 0,
        "work_items_total": 0,
        "deliberations_total": 0,
        "assertions_total": 0,
        "assertions_failed": 0,
    }
    if not db_path.exists():
        return counts
    with sqlite3.connect(db_path) as conn:
        counts["specs_total"] = _safe_count(conn, "SELECT COUNT(*) FROM current_specifications")
        counts["specs_verified"] = _safe_count(
            conn, "SELECT COUNT(*) FROM current_specifications WHERE status = 'verified'"
        )
        counts["specs_implemented"] = _safe_count(
            conn,
            "SELECT COUNT(*) FROM current_specifications WHERE status IN ('implemented', 'verified')",
        )
        counts["work_items_open"] = _safe_count(
            conn,
            "SELECT COUNT(*) FROM current_work_items WHERE resolution_status IN ('open', 'in_progress', 'blocked')",
        )
        counts["work_items_total"] = _safe_count(conn, "SELECT COUNT(*) FROM current_work_items")
        counts["deliberations_total"] = _safe_count(conn, "SELECT COUNT(*) FROM current_deliberations")
        counts["assertions_total"] = _safe_count(conn, "SELECT COUNT(*) FROM assertion_runs")
        counts["assertions_failed"] = _safe_count(
            conn,
            "SELECT COUNT(*) FROM assertion_runs WHERE overall_passed = 0",
        )
    return counts


def _safe_count(conn: sqlite3.Connection, sql: str) -> int:
    try:
        row = conn.execute(sql).fetchone()
    except sqlite3.Error:
        return 0
    return int(row[0]) if row and row[0] is not None else 0


def _insert_health_cards(conn: sqlite3.Connection, counts: dict[str, int]) -> None:
    cards = [
        ("specs", "Specifications", str(counts["specs_total"]), "ok", "Current specification count.", 1),
        ("verified", "Verified specs", str(counts["specs_verified"]), "ok", "Specs at verified lifecycle status.", 2),
        (
            "open-wi",
            "Open work items",
            str(counts["work_items_open"]),
            "review",
            "Known gaps that still need action.",
            3,
        ),
        (
            "assertions-failed",
            "Failed assertions",
            str(counts["assertions_failed"]),
            "blocker" if counts["assertions_failed"] else "ok",
            "Latest assertion-run failures.",
            4,
        ),
    ]
    conn.executemany("INSERT INTO health_cards VALUES (?, ?, ?, ?, ?, ?)", cards)


def _insert_shortcuts(conn: sqlite3.Connection, paths: DashboardPaths) -> None:
    rows = [
        ("project-root", "Project root", str(paths.project_root), "Open the evaluated project.", 1),
        ("source-db", "MemBase", str(paths.project_root / "groundtruth.db"), "Canonical GroundTruth database.", 2),
        ("dashboard-db", "Dashboard DB", str(paths.db_path), "Generated reporting database for Grafana.", 3),
        ("dashboard-assets", "Dashboard assets", str(paths.dashboards_dir), "Generated Grafana dashboard JSON.", 4),
    ]
    conn.executemany("INSERT INTO shortcuts VALUES (?, ?, ?, ?, ?)", rows)


def _insert_action_center(conn: sqlite3.Connection, counts: dict[str, int]) -> None:
    rows = [
        ("doctor", "P1", "Run workstation doctor", "Evaluator", "gt project doctor", "required", 1),
        ("assert", "P1", "Run governed assertions", "Evaluator", "gt assert", "required", 2),
        (
            "open-wi",
            "P2",
            "Review open work items",
            "Prime Builder",
            f"{counts['work_items_open']} open work items currently reported.",
            "review",
            3,
        ),
        (
            "wrap-up",
            "P2",
            "Complete session wrap-up",
            "Prime Builder",
            "Record session summary, assertions, and next action before committing.",
            "required",
            4,
        ),
    ]
    conn.executemany("INSERT INTO action_center VALUES (?, ?, ?, ?, ?, ?, ?)", rows)


def _insert_release_blockers(conn: sqlite3.Connection, config: GTConfig) -> None:
    source_db_status = "present" if config.db_path.exists() else "missing"
    rows = [
        (
            "source-db",
            "P1",
            "GroundTruth DB",
            str(config.db_path),
            "Create or restore groundtruth.db.",
            source_db_status,
            1,
        ),
        (
            "doctor",
            "P1",
            "Workstation doctor",
            "gt project doctor",
            "Resolve required-tool failures.",
            "manual-verification",
            2,
        ),
        (
            "assertions",
            "P1",
            "Assertions",
            "gt assert",
            "Resolve failed assertions before release.",
            "manual-verification",
            3,
        ),
    ]
    conn.executemany("INSERT INTO release_blockers VALUES (?, ?, ?, ?, ?, ?, ?)", rows)


def _insert_quality_rollup(conn: sqlite3.Connection) -> None:
    rows = [
        ("doctor", "Workstation readiness", "manual", "gt project doctor", "Run locally before evaluation.", 1),
        ("assert", "Spec assertions", "manual", "gt assert", "Run locally before commit.", 2),
        ("tests", "Package tests", "manual", "python -m pytest -q --tb=short", "Maintainer verification gate.", 3),
        ("lint", "Lint", "manual", "python -m ruff check .", "Maintainer verification gate.", 4),
    ]
    conn.executemany("INSERT INTO quality_rollup VALUES (?, ?, ?, ?, ?, ?)", rows)


def _insert_risks(conn: sqlite3.Connection) -> None:
    rows = [
        (
            "dashboard-runtime",
            "P2",
            "Grafana is an external runtime, not a Python dependency.",
            "Use gt dashboard install or install Grafana/plugin through enterprise tooling.",
            "Evaluator",
            "managed",
            1,
        ),
        (
            "credentials",
            "P1",
            "AI harness and GitHub credentials are outside GT-KB scope.",
            "Authenticate each service directly; keep credentials out of project files.",
            "Owner/IT",
            "manual",
            2,
        ),
        (
            "local-data",
            "P2",
            "The dashboard reads local SQLite data.",
            "Keep .groundtruth/ and groundtruth.db out of public commits unless intentionally shared.",
            "Project owner",
            "managed",
            3,
        ),
    ]
    conn.executemany("INSERT INTO risk_register VALUES (?, ?, ?, ?, ?, ?, ?)", rows)


def _insert_integrations(conn: sqlite3.Connection) -> None:
    rows = [
        (
            "pypi",
            "PyPI",
            "Package registry",
            "Install groundtruth-kb.",
            "base install",
            "external",
            "pip install groundtruth-kb",
            "Public package download.",
            1,
        ),
        (
            "github-actions",
            "GitHub Actions",
            "CI",
            "Run generated CI templates.",
            "team mode",
            "optional",
            "gh run list",
            "Not needed for local-only evaluation.",
            2,
        ),
        (
            "codeql",
            "CodeQL",
            "Security scanning",
            "Static analysis in GitHub.",
            "package repo",
            "optional",
            "GitHub Security tab",
            "Enabled in this package repo.",
            3,
        ),
        (
            "dependabot",
            "Dependabot",
            "Dependency updates",
            "Automated dependency update PRs.",
            "team mode",
            "optional",
            ".github/dependabot.yml",
            "Generated when integrations are enabled.",
            4,
        ),
        (
            "sonarcloud",
            "SonarCloud",
            "Quality analysis",
            "Hosted code quality gate.",
            "package repo",
            "optional",
            "SonarCloud dashboard",
            "Badge is visible in README.",
            5,
        ),
        (
            "grafana",
            "Grafana OSS",
            "Dashboard",
            "Local evaluation dashboard.",
            "dashboard",
            "local",
            "gt dashboard start",
            "Uses SQLite datasource plugin.",
            6,
        ),
        (
            "chromadb",
            "ChromaDB",
            "Semantic search",
            "Deliberation Archive search.",
            "search extra",
            "optional",
            'pip install "groundtruth-kb[search]"',
            "SQLite LIKE fallback works without it.",
            7,
        ),
        (
            "claude",
            "Claude Code",
            "AI harness",
            "Prime Builder sessions.",
            "dual-agent",
            "external",
            "claude --version",
            "Credential lifecycle is outside GT-KB.",
            8,
        ),
        (
            "codex",
            "Codex",
            "AI harness",
            "Loyal Opposition sessions.",
            "dual-agent",
            "external",
            "codex --version",
            "Credential lifecycle is outside GT-KB.",
            9,
        ),
    ]
    conn.executemany("INSERT INTO integration_status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def _insert_current_metrics(conn: sqlite3.Connection, counts: dict[str, int]) -> None:
    rows = [
        ("specs-total", "Specifications", str(counts["specs_total"]), "ok", "current_specifications", 1),
        (
            "specs-implemented",
            "Implemented or verified specs",
            str(counts["specs_implemented"]),
            "ok",
            "current_specifications",
            2,
        ),
        ("work-items-open", "Open work items", str(counts["work_items_open"]), "review", "current_work_items", 3),
        ("work-items-total", "Total work items", str(counts["work_items_total"]), "ok", "current_work_items", 4),
        ("deliberations", "Deliberations", str(counts["deliberations_total"]), "ok", "current_deliberations", 5),
        (
            "assertions-failed",
            "Failed assertion runs",
            str(counts["assertions_failed"]),
            "blocker" if counts["assertions_failed"] else "ok",
            "assertion_runs",
            6,
        ),
    ]
    conn.executemany("INSERT INTO current_metrics VALUES (?, ?, ?, ?, ?, ?)", rows)


def _insert_kpis(conn: sqlite3.Connection, counts: dict[str, int], captured_at: str) -> None:
    rows = [
        ("specs-total", "Specifications", float(counts["specs_total"]), "count", captured_at, "current_specifications"),
        (
            "verified-specs",
            "Verified specs",
            float(counts["specs_verified"]),
            "count",
            captured_at,
            "current_specifications",
        ),
        (
            "open-work-items",
            "Open work items",
            float(counts["work_items_open"]),
            "count",
            captured_at,
            "current_work_items",
        ),
        (
            "failed-assertions",
            "Failed assertions",
            float(counts["assertions_failed"]),
            "count",
            captured_at,
            "assertion_runs",
        ),
    ]
    conn.executemany("INSERT INTO kpi_snapshots VALUES (?, ?, ?, ?, ?, ?)", rows)


def _insert_freshness(conn: sqlite3.Connection, config: GTConfig, paths: DashboardPaths, captured_at: str) -> None:
    rows = [
        (
            "source-db",
            str(config.db_path),
            _mtime_or_missing(config.db_path),
            "ok" if config.db_path.exists() else "missing",
            "Canonical MemBase.",
        ),
        ("dashboard-db", str(paths.db_path), captured_at, "ok", "Generated reporting database."),
        ("dashboard-assets", str(paths.dashboards_dir), captured_at, "ok", "Grafana JSON and provisioning files."),
    ]
    conn.executemany("INSERT INTO data_freshness VALUES (?, ?, ?, ?, ?)", rows)


def _insert_setup(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO setup_steps VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(*row, "not-run") for row in SETUP_STEPS],
    )


def _insert_required_tools(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO required_tools VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [(*row, idx + 1) for idx, row in enumerate(REQUIRED_TOOLS)],
    )


def _insert_third_party_services(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO third_party_services VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(*row, idx + 1) for idx, row in enumerate(THIRD_PARTY_SERVICES)],
    )


def _download_grafana_windows(target: Path) -> None:
    if sys.platform != "win32":
        raise RuntimeError("Automatic Grafana download is currently implemented for Windows only.")
    api_url = "https://api.github.com/repos/grafana/grafana/releases/latest"
    with urllib.request.urlopen(api_url, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))
    asset_url = ""
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".windows-amd64.zip") or ("windows-amd64" in name and name.endswith(".zip")):
            asset_url = asset["browser_download_url"]
            break
    if not asset_url:
        raise RuntimeError("Could not locate a Windows Grafana ZIP asset in the latest release.")
    zip_path = target / "grafana-windows-amd64.zip"
    urllib.request.urlretrieve(asset_url, zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target)
    zip_path.unlink(missing_ok=True)
    extracted = sorted(target.glob("grafana-*"))
    if extracted:
        for child in extracted[-1].iterdir():
            destination = target / child.name
            if destination.exists():
                continue
            child.rename(destination)


def _install_sqlite_plugin(grafana_home: Path) -> None:
    grafana_cli = grafana_home / "bin" / "grafana-cli.exe"
    if not grafana_cli.exists():
        grafana_cli = grafana_home / "bin" / "grafana-cli"
    if not grafana_cli.exists():
        grafana_cli_path = shutil.which("grafana-cli")
        if grafana_cli_path is None:
            raise FileNotFoundError("grafana-cli was not found; install the SQLite datasource plugin manually.")
        grafana_cli = Path(grafana_cli_path)
    plugins_dir = grafana_home / "data" / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(grafana_cli), "--pluginsDir", str(plugins_dir), "plugins", "install", SQLITE_PLUGIN_ID],
        cwd=grafana_home,
        check=True,
    )


def _git_state(project_root: Path) -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=project_root,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return "unknown"
        return completed.stdout.strip() if completed.returncode == 0 else "unknown"

    return {
        "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": run(["rev-parse", "--short", "HEAD"]),
    }


def _write_pid(path: Path, pid: int) -> None:
    path.write_text(f"{pid}\n", encoding="utf-8")


def _terminate_pid(pid: int) -> bool:
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
        else:
            os.kill(pid, 15)
    except OSError:
        return False
    return True


def _mtime_or_missing(path: Path) -> str:
    if not path.exists():
        return "missing"
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(path.stat().st_mtime))


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
