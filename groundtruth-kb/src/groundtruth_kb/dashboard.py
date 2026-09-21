#!/usr/bin/env python3
"""Refresh the GT-KB Grafana dashboard SQLite database."""

from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import logging
import math
import os
import secrets
import shutil
import socket
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

import yaml

from groundtruth_kb import dashboard_link, get_templates_dir, job_containment
from groundtruth_kb.config import GTConfig

logger = logging.getLogger(__name__)


_ProcessIdentity = job_containment.ProcessIdentity


class _LaunchedProcess(TypedDict):
    role: str
    pid: int
    created_at: str
    executable: str


class DashboardStopError(RuntimeError):
    """The dashboard could not be stopped cleanly; the message names the process and the reason."""


class DashboardIdentityError(DashboardStopError):
    """The process a record names is not the process that was launched; nothing was signalled."""


class DashboardTerminationRefused(DashboardStopError):
    """The termination request failed (taskkill non-zero with the process still running, or the job refused it)."""


class DashboardTerminationUnconfirmed(DashboardStopError):
    """The termination request was accepted but a held process handle stayed unsignalled within the wait."""


LAUNCH_RECORD_NAME = "dashboard-launch.json"
DASHBOARD_JOB_PREFIX = "Local\\gtkb-dashboard-"
CREATE_SUSPENDED = job_containment.CREATE_SUSPENDED
# Grafana launch environment pins (conf/defaults.ini of the pinned 13.2.1 release: [analytics], [plugins], [news],
# [log]). The background plugin installer (preinstall + preinstall_auto_update) reached grafana.com during a
# production start and wrote plugin updates into the Grafana home; every check, download and update path the
# server itself initiates is off, plugin administration from the UI is off, the embedded signing key is used
# without retrieval, and Grafana logs to its console only so the launcher's redirect is grafana.log's single writer.
GRAFANA_LAUNCH_PINS: dict[str, str] = {
    "GF_ANALYTICS_REPORTING_ENABLED": "false",
    "GF_ANALYTICS_CHECK_FOR_UPDATES": "false",
    "GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES": "false",
    "GF_ANALYTICS_FEEDBACK_LINKS_ENABLED": "false",
    "GF_PLUGINS_PREINSTALL_DISABLED": "true",
    "GF_PLUGINS_PREINSTALL_AUTO_UPDATE": "false",
    "GF_PLUGINS_PLUGIN_ADMIN_ENABLED": "false",
    "GF_PLUGINS_PUBLIC_KEY_RETRIEVAL_DISABLED": "true",
    "GF_NEWS_NEWS_FEED_ENABLED": "false",
    "GF_LOG_MODE": "console",
}

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
_GITHUB_WORKFLOW_REPOSITORY = "Remaker-Digital/groundtruth-kb"
_GITHUB_WORKFLOW_BRANCH = "main"
_TRUE_ENV_VALUES = {"1", "true", "yes", "on"}
_AZURE_CONTAINER_APP_MAP_ENV = "GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP"
_AZURE_RESOURCE_GROUP_ENV = "GTKB_DASHBOARD_AZURE_RESOURCE_GROUP"
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


DEFAULT_DB_RELATIVE_PATH = Path(".groundtruth/dashboard/gtkb-dashboard.sqlite")
SCHEMA_PATH = get_templates_dir() / "dashboard/schema.sql"
SQLITE_PLUGIN_ID = "frser-sqlite-datasource"
SQLITE_PLUGIN_VERSION = "4.0.6"
GRAFANA_VERSION = "13.2.1"
SQLITE_DATASOURCE_UID = "gtkb-dashboard-sqlite"
GRAFANA_DASHBOARD_UID = dashboard_link.GRAFANA_DASHBOARD_UID
DEFAULT_GRAFANA_PORT = dashboard_link.DEFAULT_GRAFANA_PORT
DEFAULT_REFRESH_PORT = dashboard_link.DEFAULT_REFRESH_PORT
DEFAULT_REFRESH_INTERVAL_MINUTES = 60
GRAFANA_ARCHIVE_URL = "https://dl.grafana.com/grafana/release/13.2.1/grafana_13.2.1_33191028959_windows_amd64.tar.gz"
GRAFANA_ARCHIVE_SHA256 = "b6d7060b8d133930742a9326a6065f90e629b173188e041696856b337754a02b"


KPI_DEFINITIONS = [
    ("backlog_active_items", "Backlog", "pressure", 1),
    ("membase_open_work_items", "Native Open Work Items", "knowledge", 1),
    ("deliberation_archive_current_total", "Deliberation Archive", "knowledge", 0),
    ("pytest_file_count", "Pytest Files", "knowledge", 0),
    ("specification_current_total", "Active Formal Records", "knowledge", 0),
    *[
        (f"{kind}_template_count", f"Baseline {kind.title()} Templates", "knowledge", 0)
        for kind in ("skill", "rule", "hook")
    ],
    ("tokens_consumed_before_user_input", "Startup Tokens", "measurement", 1),
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
        "instruction": (
            "Select the project with gt --config <path-to-groundtruth.toml> before "
            "initializing or refreshing its dashboard."
        ),
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
        "instruction": "Set GTKB_DASHBOARD_REFRESH_TOKEN in the service environment for manual refresh requests.",
        "command": "GTKB_DASHBOARD_REFRESH_TOKEN=change-me-local-refresh-token",
        "link_label": "",
        "link_url": "",
    },
    {
        "section": "Launch",
        "title": "Install local Grafana",
        "instruction": (
            "Install Grafana OSS into the ignored local tools directory and install the SQLite data source plugin."
        ),
        "command": "gt dashboard install",
        "link_label": "Grafana Windows install",
        "link_url": "https://grafana.com/docs/grafana/latest/installation/windows/",
    },
    {
        "section": "Launch",
        "title": "Start local dashboard",
        "instruction": "Start the local refresh service and Grafana without a container runtime.",
        "command": "gt dashboard start",
        "link_label": "Local Grafana",
        "link_url": "http://127.0.0.1:3000/",
    },
    {
        "section": "Launch",
        "title": "Refresh dashboard data",
        "instruction": (
            "Open the refresh control when you need an on-demand data collection run outside the 60-minute interval."
        ),
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
        "check_command": "gt dashboard install --skip-download",
        "install_reference": "https://grafana.com/docs/grafana/latest/installation/windows/",
    },
    {
        "name": "Grafana SQLite data source plugin",
        "category": "Dashboard data source",
        "purpose": "Lets Grafana query the dedicated GT-KB SQLite dashboard database directly.",
        "check_command": "gt dashboard install --skip-download",
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
        "setup_summary": (
            "Authenticate gh, confirm repository access, and verify required workflows under .github/workflows."
        ),
        "console_url": "https://github.com/Remaker-Digital/groundtruth-kb/actions",
        "health_signal": "workflow run status and local gh availability",
    },
    {
        "name": "Application deployment connector",
        "category": "Application-owned integration",
        "purpose": (
            "Supplies live deployment topology, container, infrastructure, and runtime "
            "health rows to the GT-KB dashboard."
        ),
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
        "setup_summary": (
            "Create a project token, configure GitHub Actions secret, and verify visual-regression workflows."
        ),
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
        "setup_summary": (
            "Configure registry and Docker Hub integration credentials as CI secrets or local-only env values."
        ),
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


def _native_dashboard_records(client: Any, domain: str) -> list[dict[str, Any]]:
    """Read every page; a partial or repeated page is never a complete inventory."""
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    after = None
    while True:
        page = client.request("GET", f"/v1/{domain}", query={"after": after, "limit": 1000})
        if not isinstance(page, dict) or not isinstance(page.get("records"), list) or "next_after" not in page:
            raise ValueError("invalid_native_page")
        for row in page["records"]:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
                raise ValueError("invalid_native_record")
            if row["id"] in seen or (records and row["id"] <= records[-1]["id"]):
                raise ValueError("invalid_native_pagination")
            seen.add(row["id"])
            records.append(row)
        following = page["next_after"]
        if following is None:
            return records
        if not page["records"] or following != page["records"][-1]["id"]:
            raise ValueError("invalid_native_pagination")
        after = following


def _build_dashboard_model(project_root: Path, config: GTConfig | None = None) -> dict[str, Any]:
    """Collect display observations without session initialization or local authority fallbacks.

    Domain pages are separate reads during this refresh, not one cross-domain
    database snapshot. Record inventories do not establish test execution,
    release readiness, host capability, agent role or selected work.
    """
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
    from groundtruth_kb.config import GTConfig, GTConfigError

    started_at = datetime.now(UTC).isoformat()
    sources: list[str] = []
    client = None
    try:
        config = config or GTConfig.load(config_path=project_root.resolve() / "groundtruth.toml", discover=False)
        if config.authority_url:
            client = AuthorityClient(config.authority_url, timeout=20)
    except (OSError, GTConfigError, ValueError):
        pass
    inventories: dict[str, list[dict[str, Any]] | None] = {}
    for domain in ("work-items", "specifications", "tests"):
        rows = None
        if client is not None:
            try:
                rows = _native_dashboard_records(client, domain)
                field = {"work-items": "resolution_status", "specifications": "status"}.get(domain)
                if field and any(not isinstance(row.get(field), str) or not row[field] for row in rows):
                    raise ValueError("invalid_native_record")
            except (AuthorityClientError, ValueError):
                rows = None
        inventories[domain] = rows
        sources.append(f"native/{domain}: {'observed' if rows is not None else 'unavailable'}")

    actionable = None
    if client is not None:
        try:
            report = client.request("GET", "/v1/bridge/state-report")
            queues = report.get("queues") if isinstance(report, dict) else None
            if isinstance(queues, dict) and all(
                isinstance(queues.get(role), dict)
                and queues[role].get("role") == role
                and all(isinstance(queues[role].get(key), list) for key in ("eligible", "blocked"))
                for role in ("pb", "lo")
            ):
                actionable = sum(len(queues[role]["eligible"]) for role in ("pb", "lo"))
        except AuthorityClientError:
            pass
    sources.append(f"native/bridge eligibility: {'observed' if actionable is not None else 'unavailable'}")

    git_root = _run_release_probe(project_root, ["git", "rev-parse", "--show-toplevel"])
    exact_root = (
        git_root is not None
        and git_root.returncode == 0
        and Path(git_root.stdout.strip()).resolve() == project_root.resolve()
    )
    tracked = _run_release_probe(
        project_root,
        ["git", "ls-files", "-z", "--", "platform_tests", "groundtruth-kb/tests", ".harness-baseline-configuration"],
    )
    paths = (
        None
        if not exact_root or tracked is None or tracked.returncode
        else [Path(name) for name in tracked.stdout.split("\0") if name and (project_root / name).is_file()]
    )
    dirty = _run_release_probe(project_root, ["git", "status", "--porcelain=v1", "--untracked-files=all"])
    dirty_count = None if not exact_root or dirty is None or dirty.returncode else len(dirty.stdout.splitlines())
    sources.append(f"tracked test/baseline files: {'observed' if paths is not None else 'unavailable'}")
    sources.append(f"git working tree: {'observed' if dirty_count is not None else 'unavailable'}")
    work = inventories["work-items"]
    specs = inventories["specifications"]
    tests = inventories["tests"]
    open_count = None if work is None else sum(row["resolution_status"] == "open" for row in work)
    template_counts = {
        f"{kind}_template_count": None
        if paths is None
        else sum(
            path.parts[:2] == (".harness-baseline-configuration", folder)
            and path.suffix == suffix
            and (kind != "skill" or path.name == "SKILL.md")
            for path in paths
        )
        for kind, folder, suffix in (("skill", "skills", ".md"), ("rule", "rules", ".md"), ("hook", "hooks", ".py"))
    }
    generated_at = datetime.now(UTC).isoformat()
    return {
        "generated_at": generated_at,
        "dashboard_requirements": {
            "scope_note": "GT-KB platform observations; no selected agent role, work item or adopter is inferred."
        },
        "metrics": {
            "backlog": {"active_item_count": open_count},
            "membase": {"open_work_items": open_count},
            "deliberation_archive": {"current_total": None},
            "tests": {
                "test_records": None if tests is None else len(tests),
                "pytest_file_count": None
                if paths is None
                else sum(path.name.startswith("test_") and path.suffix == ".py" for path in paths),
            },
            "templates": template_counts,
            "specifications": {
                "current_total": None if specs is None else sum(row["status"] == "active" for row in specs)
            },
            "drift": {"changed_path_count": dirty_count},
            "regression": {"release_blocker_count": None},
            "contention": {"actionable_count": actionable},
            "tokens": {"tokens_consumed_before_user_input": None, "measurement_status": "unavailable"},
        },
        "dashboard_intelligence": {
            "quality_rollup": {},
            "release_readiness": {"blocker_count": None, "blockers": []},
            "data_freshness": {
                "generated_at": generated_at,
                "started_at": started_at,
                "status": "partial",
                "sources": sources
                + [
                    (
                        "Deliberation Archive, execution results, release readiness and context "
                        "token measurements: unavailable"
                    )
                ],
            },
        },
        "infrastructure": {},
    }


def _snapshot_from_model(model: dict[str, Any]) -> dict[str, Any]:
    metrics = model.get("metrics", {})
    fields = {
        "backlog_active_items": ("backlog", "active_item_count"),
        "membase_open_work_items": ("membase", "open_work_items"),
        "deliberation_archive_current_total": ("deliberation_archive", "current_total"),
        "pytest_file_count": ("tests", "pytest_file_count"),
        "specification_current_total": ("specifications", "current_total"),
        "drift_changed_path_count": ("drift", "changed_path_count"),
        "regression_release_blocker_count": ("regression", "release_blocker_count"),
        "contention_actionable_bridge_count": ("contention", "actionable_count"),
        "tokens_consumed_before_user_input": ("tokens", "tokens_consumed_before_user_input"),
        **{f"{kind}_template_count": ("templates", f"{kind}_template_count") for kind in ("skill", "rule", "hook")},
    }
    return {
        "generated_at": model.get("generated_at", ""),
        **{key: metrics.get(group, {}).get(field) for key, (group, field) in fields.items()},
    }


def initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _expected_derived_schema() -> dict[str, set[str]]:
    """Column names per table that ``schema.sql`` creates, derived by executing it in memory."""
    with sqlite3.connect(":memory:") as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        tables = [
            str(name)
            for (name,) in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        return {table: {str(row[1]) for row in conn.execute(f'PRAGMA table_info("{table}")')} for table in tables}


def _derived_schema_mismatch(db_path: Path) -> str | None:
    """Why the existing derived database cannot carry this package's refresh, or None when it can.

    A legacy or foreign derived schema is no history: a table the current ``schema.sql`` does not create, a table
    missing an expected column, a NOT NULL column without a default that the refresh never writes (the July-9
    ``dashboard_metadata.updated_at`` shape), or a file SQLite cannot open, each disqualifies the whole file. Extra
    columns that are nullable or carry a default are the additive migrations ``_migrate_schema`` applies and are
    accepted; tables that do not exist yet are created by ``schema.sql``.
    """
    expected = _expected_derived_schema()
    uri = "file:" + urllib.parse.quote(db_path.as_posix(), safe="/:") + "?mode=ro"
    try:
        with contextlib.closing(sqlite3.connect(uri, uri=True)) as conn:
            existing = [
                str(name)
                for (name,) in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )
            ]
            for table in existing:
                if table not in expected:
                    return f"carries table {table}, which the current derived schema does not define"
                info = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
                columns = {str(row[1]) for row in info}
                missing = sorted(expected[table] - columns)
                if missing:
                    return f"table {table} lacks the expected column(s) {', '.join(missing)}"
                blocking = sorted(
                    str(row[1]) for row in info if str(row[1]) not in expected[table] and row[3] and row[4] is None
                )
                if blocking:
                    return (
                        f"table {table} carries NOT NULL column(s) without a default that the refresh does not "
                        f"write: {', '.join(blocking)}"
                    )
    except sqlite3.DatabaseError as error:
        return f"is not a database this package can read ({error})"
    return None


def _move_legacy_database_aside(db_path: Path, runtime_root: Path, reason: str) -> Path:
    """Move a legacy or foreign derived database (and its SQLite sidecars) aside under the runtime root."""
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    runtime_root.mkdir(parents=True, exist_ok=True)
    target = runtime_root / f"{db_path.name}.legacy-{stamp}"
    counter = 1
    while target.exists():
        target = runtime_root / f"{db_path.name}.legacy-{stamp}-{counter}"
        counter += 1
    os.replace(db_path, target)
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = db_path.with_name(db_path.name + suffix)
        if sidecar.exists():
            os.replace(sidecar, target.with_name(target.name + suffix))
    logger.warning(
        "derived dashboard database %s %s; it was moved aside to %s and is rebuilt from the current schema "
        "(a legacy or foreign derived schema is no history)",
        db_path,
        reason,
        target,
    )
    return target


def _ensure_derived_schema(db_path: Path, runtime_root: Path) -> Path | None:
    """Make ``db_path`` carry the current derived schema; return where a legacy/foreign file was moved, if any."""
    moved = None
    if db_path.exists():
        reason = _derived_schema_mismatch(db_path)
        if reason is not None:
            moved = _move_legacy_database_aside(db_path, runtime_root, reason)
    initialize_database(db_path)
    _migrate_schema(db_path)
    return moved


def _landing_snapshot_from_model(model: dict[str, Any]) -> dict[str, Any]:
    """Project only this refresh's display values, never model/session/history payloads."""
    snapshot = _snapshot_from_model(model)
    values = {
        key: value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None
        for key, value in snapshot.items()
        if key != "generated_at"
    }
    freshness = model.get("dashboard_intelligence", {}).get("data_freshness", {})
    started_at = freshness.get("started_at")
    generated_at = snapshot["generated_at"]
    try:
        start, end = (datetime.fromisoformat(value) for value in (started_at, generated_at))
        valid_interval = start.utcoffset() is not None and end.utcoffset() is not None and start <= end
    except (TypeError, ValueError):
        valid_interval = False
    if not valid_interval:
        started_at = generated_at = None
        values = dict.fromkeys(values)
    return {
        "status": "partial" if any(value is not None for value in values.values()) else "unavailable",
        "started_at": started_at,
        "generated_at": generated_at,
        "metrics": values,
    }


def _write_landing_snapshot(project_root: Path, model: dict[str, Any], runtime_root: Path | None = None) -> None:
    """Atomically replace the existing page projection, including unavailable observations."""
    target = (runtime_root or project_root / ".groundtruth/dashboard") / "dashboard-data.json"
    payload = json.dumps(_landing_snapshot_from_model(model), indent=2, sort_keys=True, allow_nan=False) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=target.parent,
            prefix=target.name + ".",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


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


def refresh_database(
    db_path: Path | None = None,
    project_root: Path | None = None,
    model: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
    *,
    probe_live: bool = False,
    config: GTConfig | None = None,
    runtime_root: Path | None = None,
) -> dict[str, Any]:
    project_root = (project_root or (config.project_root if config else Path.cwd())).resolve()
    if config is not None and project_root != config.project_root.resolve():
        raise ValueError("dashboard_config_root_mismatch")
    runtime_root = (runtime_root or project_root / ".groundtruth/dashboard").resolve()
    db_path = (db_path or runtime_root / "gtkb-dashboard.sqlite").resolve()
    source_db = config.db_path if config is not None else project_root / "groundtruth.db"
    if db_path == source_db.resolve():
        raise ValueError("dashboard_db_must_be_derived")
    started_at = datetime.now(UTC).isoformat()
    probe_live_release_health = model is None and probe_live
    moved_aside = _ensure_derived_schema(db_path, runtime_root)
    run_id: int | None = None
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO refresh_runs (started_at, status) VALUES (?, ?)",
            (started_at, "running"),
        )
        run_id = cursor.lastrowid
        if run_id is None:
            raise RuntimeError("dashboard_refresh_run_identity_unavailable")

    try:
        if model is None:
            model = _build_dashboard_model(project_root, config)
        if history is None:
            snapshot = _snapshot_from_model(model)
            previous_history = _read_existing_history(db_path)
            history = _append_snapshot(previous_history, snapshot)
        _write_model_to_db(
            db_path,
            model,
            history,
            project_root,
            probe_live_release_health=probe_live_release_health,
            probe_live_workflows=probe_live_release_health,
            config=config,
        )
        _write_landing_snapshot(project_root, model, runtime_root)
        _write_bridge_swimlane_safe(project_root, runtime_root, config)
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE refresh_runs SET completed_at = ?, status = ? WHERE id = ?",
                (completed_at, "completed", run_id),
            )
        result: dict[str, Any] = {
            "status": "completed",
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": completed_at,
        }
        if moved_aside is not None:
            result["legacy_database_moved_to"] = str(moved_aside)
        return result
    except Exception as exc:
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE refresh_runs SET completed_at = ?, status = ?, error = ? WHERE id = ?",
                (completed_at, "failed", str(exc), run_id),
            )
        raise


def _write_bridge_swimlane_safe(
    project_root: Path, runtime_root: Path | None = None, config: GTConfig | None = None
) -> None:
    """Publish the native bridge display independently of the KPI refresh."""
    try:
        from groundtruth_kb.dashboard_swimlane import write_swimlane

        target = (runtime_root or project_root / ".groundtruth/dashboard") / "bridge-swimlane.json"
        write_swimlane(project_root, target, config=config)
    except Exception:  # intentional-catch: derived bridge view; a failed write is logged, the refresh continues
        logger.warning("bridge swimlane write failed; refresh continues", exc_info=True)


def _read_existing_history(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        columns = ", ".join(
            f"MAX(CASE WHEN metric_key = '{key}' THEN value END) AS {key}" for key, *_ in KPI_DEFINITIONS
        )
        rows = conn.execute(
            f"SELECT generated_at, {columns} FROM kpi_snapshots GROUP BY generated_at ORDER BY generated_at"
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
    project_root: Path | None = None,
    *,
    probe_live_release_health: bool = False,
    probe_live_workflows: bool = False,
    config: GTConfig | None = None,
) -> None:
    project_root = (project_root or Path.cwd()).resolve()
    metrics = model.get("metrics", {})
    intelligence = model.get("dashboard_intelligence", {})
    infrastructure = model.get("infrastructure", {})
    delivery = infrastructure.get("delivery_timeline", {})
    release_health_findings = _release_health_findings(
        project_root,
        intelligence,
        model=model,
        probe_live=probe_live_release_health,
        config=config,
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
            "dashboard_subject_badge": _dashboard_subject_scope_label(model),
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
                    _reconciled_health_cards(metrics, intelligence, release_health_findings, project_root=project_root),
                    start=1,
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
            (sort_order, action, owner_lane, why, remediation, shortcut_label,
             shortcut_target, shortcut_kind, source, severity)
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
            ("Total", quality.get("total"), "green"),
            ("Failing", quality.get("failing"), "red"),
            ("Manual", quality.get("manual"), "yellow"),
            ("No Recent / Unknown", quality.get("unknown"), "yellow"),
            ("Ready / Passing", quality.get("ready_or_passing"), "green"),
        ]
        conn.executemany(
            "INSERT INTO quality_rollup (sort_order, label, value, status) VALUES (?, ?, ?, ?)",
            [
                (idx, label, int(value), status)
                for idx, (label, value, status) in enumerate(quality_rows, start=1)
                if value is not None
            ],
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
            _integration_status_rows(
                integrations, project_root, probe_live_workflows=probe_live_workflows, config=config
            ),
        )

        conn.executemany(
            (
                "INSERT INTO kpi_snapshots (generated_at, metric_key, metric_label, value, "
                "metric_group, lower_is_better) VALUES (?, ?, ?, ?, ?, ?)"
            ),
            _kpi_rows(history),
        )
        conn.executemany(
            "INSERT INTO current_metrics (metric_key, metric_label, value, status, description) VALUES (?, ?, ?, ?, ?)",
            _current_metric_rows(metrics, intelligence, release_health_findings),
        )
        # GTKB-DORA-002: four-keys metrics derived from the authoritative
        # deployment/incident telemetry ingested above (canonical manifests +
        # incidents). Runs after _ingest_canonical_pipeline_manifests so
        # canonical_deploy rows are present.
        conn.executemany(
            "INSERT INTO current_metrics (metric_key, metric_label, value, status, description) VALUES (?, ?, ?, ?, ?)",
            _dora_four_keys_metric_rows(conn),
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
                f"deploy-result manifest; phases={manifest.get('phases_completed', 0)}/"
                f"{manifest.get('phases_total', 0)}",
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
        logger.warning(
            "[refresh_dashboard_db] WARNING: Azure reconciliation skipped; "
            f"application-owned {_AZURE_CONTAINER_APP_MAP_ENV} and {_AZURE_RESOURCE_GROUP_ENV} are required."
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
                    logger.warning(
                        f"[refresh_dashboard_db] WARNING: Azure reconciliation "
                        f"degraded; az containerapp revision list returned "
                        f"{result.returncode} for {env}"
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
                logger.warning(
                    f"[refresh_dashboard_db] WARNING: Azure reconciliation "
                    f"degraded; {type(exc).__name__} querying revisions for "
                    f"{env}: {exc}"
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
        if isinstance(kind, str) and kind in _DORA_AUTHORITATIVE_EVENT_KINDS:
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
    return "GT-KB platform; adopter context unavailable"


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
    try:
        return subprocess.run(
            args,
            cwd=project_root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("release-health probe failed: %s", " ".join(args), exc_info=True)
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr=str(exc))


def _native_dashboard_probe(
    project_root: Path, route: str, *, config: GTConfig | None = None, timeout: int = 20
) -> Any:
    """Read through the supplied authority configuration without another CLI discovery."""
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
    from groundtruth_kb.config import GTConfigError

    try:
        selected = config or GTConfig.load(config_path=project_root / "groundtruth.toml", discover=False)
        if not selected.authority_url:
            return None
        return AuthorityClient(selected.authority_url, timeout=timeout).request("GET", route)
    except (AuthorityClientError, GTConfigError, OSError, ValueError):
        return None


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
            "latest_run_summary": (
                f"No recent runs returned for {_GITHUB_WORKFLOW_REPOSITORY}@{_GITHUB_WORKFLOW_BRANCH}."
            ),
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


def _native_authority_live_status(project_root: Path, config: GTConfig | None = None) -> dict[str, Any]:
    """Report the configured native authority without querying a retired daemon."""
    base = {"order": 2, "display_name": "Native Authority", "gate_role": "canonical data availability"}
    status = _native_dashboard_probe(project_root, "/v1/status", config=config)
    if (
        not isinstance(status, dict)
        or status.get("_probe_error")
        or any(type(status.get(key)) is not bool for key in ("reachable", "ready", "schema_catalog_matches"))
    ):
        return {
            **base,
            "health": "yellow",
            "status": "live_state_unavailable",
            "latest_run_summary": "Native authority status is unavailable or malformed.",
            "remediation": "Read gt service status --json and resolve its current diagnostic.",
        }
    ready = all(status[key] for key in ("reachable", "ready", "schema_catalog_matches"))
    return {
        **base,
        "health": "green" if ready else "red",
        "status": "ready" if ready else "not_ready",
        "latest_run_summary": "Configured native authority is ready."
        if ready
        else "Configured native authority is not ready.",
        "remediation": "Availability does not qualify runtime behavior or Dispatcher Next activation."
        if ready
        else "Resolve the native service/schema diagnostic; do not use a legacy fallback.",
    }


def _integration_status_rows(
    integrations: dict[str, Any],
    project_root: Path,
    *,
    probe_live_workflows: bool = False,
    config: GTConfig | None = None,
) -> list[tuple[Any, ...]]:
    merged: dict[str, dict[str, Any]] = {}
    for key, details in integrations.items():
        if key in {"dispatcher_supervisor", "dispatcher", "tafe"}:
            continue
        merged[key] = dict(details) if isinstance(details, dict) else {"display_name": str(details)}
    if probe_live_workflows:
        merged["github"] = {**merged.get("github", {}), **_github_workflow_live_status(project_root)}
        merged["native_authority"] = _native_authority_live_status(project_root, config)
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


def _live_release_health_findings(project_root: Path, config: GTConfig | None = None) -> list[dict[str, Any]]:
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

    authority = _native_authority_live_status(project_root, config)
    ready = authority["status"] == "ready"
    findings.append(
        {
            "source": "native-authority",
            "message": authority["latest_run_summary"],
            "severity": authority["health"],
            "metric_key": "native_authority_findings",
            "metric_value": 0 if ready else 1,
            "release_visible": not ready,
        }
    )

    report = _native_dashboard_probe(project_root, "/v1/bridge/state-report", config=config, timeout=30)
    if not isinstance(report, dict) or report.get("_probe_error"):
        findings.append({"source": "bridge", "message": "Native bridge state is unavailable.", "severity": "yellow"})
    else:
        claims = report.get("active_claim_count")
        queues = report.get("queues")
        valid = type(claims) is int and claims >= 0 and isinstance(queues, dict)
        queue_counts = {"eligible": 0, "blocked": 0}
        for role in ("pb", "lo"):
            queue = queues.get(role) if isinstance(queues, dict) else None
            if not isinstance(queue, dict) or queue.get("role") != role:
                valid = False
                continue
            for key in ("eligible", "blocked"):
                entries = queue.get(key)
                if isinstance(entries, list):
                    queue_counts[key] += len(entries)
                else:
                    valid = False
        if not valid:
            findings.append({"source": "bridge", "message": "Native bridge state is malformed.", "severity": "yellow"})
        else:
            eligible = queue_counts["eligible"]
            blocked = queue_counts["blocked"]
            findings.append(
                {
                    "source": "bridge",
                    "message": f"Native bridge: {claims} active next-artifact claim(s), "
                    f"{eligible} eligible and {blocked} blocked action(s). "
                    "Queue observation does not dispatch work or establish release readiness.",
                    "severity": "yellow" if claims or blocked else "green",
                    "release_visible": bool(claims or blocked),
                }
            )

    return findings[:12]


def _release_health_findings(
    project_root: Path,
    intelligence: dict[str, Any],
    *,
    model: dict[str, Any] | None = None,
    probe_live: bool,
    config: GTConfig | None = None,
) -> list[dict[str, Any]]:
    findings = _explicit_release_health_findings(intelligence)
    findings.extend(_deferral_expiry_findings(model))
    if probe_live:
        findings.extend(_live_release_health_findings(project_root, config))
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
    if value is None:
        return "Unavailable"
    count = _num(value)
    return f"{count} {singular if count == 1 else plural}"


def _reconciled_health_cards(
    metrics: dict[str, Any],
    intelligence: dict[str, Any],
    release_health_findings: list[dict[str, Any]] | None = None,
    *,
    project_root: Path | None = None,
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
    observed_blockers = release.get("blocker_count", metrics.get("regression", {}).get("release_blocker_count"))
    release_blockers = (
        None if observed_blockers is None else max(_num(observed_blockers), len(release_blocker_messages))
    )
    explicit_release_blockers = bool(release.get("blockers")) or _num(observed_blockers)
    release_health_status = _finding_status(release_health_findings) if release_health_findings else "yellow"
    release_blocker_status = (
        "yellow"
        if release_blockers is None
        else "green"
        if release_blockers == 0
        else "red"
        if explicit_release_blockers or release_health_status == "red"
        else "yellow"
    )
    ci_failing = quality.get("failing")
    project_health = None if ci_failing is None or release_blockers is None else _num(ci_failing) + release_blockers
    bridge_actionable = metrics.get("contention", {}).get("actionable_count")
    live_dirty_paths = _finding_metric_value(release_health_findings, "dirty_worktree_paths")
    dirty_paths = (
        live_dirty_paths if live_dirty_paths is not None else metrics.get("drift", {}).get("changed_path_count")
    )
    dirty_path_description = (
        "Changed paths from live git status; release prep must classify dirty paths before push."
        if live_dirty_paths is not None
        else "Changed paths from the current dashboard model; release prep must classify dirty paths before push."
    )
    native_findings = _finding_metric_value(release_health_findings, "native_authority_findings")
    if native_findings is None:
        count = _finding_count(release_health_findings, "native-authority")
        native_findings = count if count else None
    bridge_findings = (
        _finding_count(release_health_findings, "bridge")
        if any(item.get("source") == "bridge" for item in release_health_findings)
        else None
    )
    docs_drift_findings = (
        _finding_count(release_health_findings, "readme", "wiki", "docs", "readme-wiki")
        if any(item.get("source") in {"readme", "wiki", "docs", "readme-wiki"} for item in release_health_findings)
        else None
    )
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
            len(visible_findings) if release_health_findings else None,
            release_health_status,
            "Live release-health findings from git, native bridge/authority, README/wiki, and supplied model evidence.",
        ),
        (
            "dirty_worktree_paths",
            "Dirty Worktree Paths",
            dirty_paths,
            _metric_count_status(dirty_paths),
            dirty_path_description,
        ),
        (
            "native_authority_findings",
            "Native Authority Findings",
            native_findings,
            _metric_count_status(native_findings),
            "Configured native authority availability; unknown when no current observation is supplied.",
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
            quality.get("ready_or_passing"),
            "green" if ci_failing == 0 and quality.get("ready_or_passing") is not None else "yellow",
            "Ready or passing checks.",
        ),
        (
            "governance_bridge_items",
            "Governance Bridge Items",
            bridge_actionable,
            _metric_count_status(bridge_actionable, positive="yellow"),
            "Actionable bridge/contention entries.",
        ),
        (
            "data_freshness",
            "Data Freshness",
            None,
            "yellow",
            "Consult the timestamped source observations; refresh time alone does not establish complete telemetry.",
        ),
    ]


# GTKB-DORA-002: DORA four-keys consumer of the DORA-001 telemetry foundation.
# Status is informational (the four keys are not simple good/bad counters); the
# stat-panel color comes from the panel thresholds, not this column. A value of
# None renders a null/annotated state per GOV-SESSION-SELF-INITIALIZATION-001 (no
# fabricated telemetry) and the DORA-002 acceptance criteria.
_DORA_PRESENT_STATUS = "green"
_DORA_INSUFFICIENT_STATUS = "yellow"


def _dora_deploy_kind_placeholders() -> tuple[str, tuple[str, ...]]:
    """SQL ``IN`` placeholders + ordered params for authoritative deploy kinds."""
    kinds = tuple(sorted(_DORA_DEPLOYMENT_EVENT_KINDS))
    placeholders = ", ".join("?" for _ in kinds)
    return placeholders, kinds


def _dora_deployment_frequency(conn: sqlite3.Connection) -> int | None:
    """Count authoritative deployment events (``canonical_deploy``).

    Returns ``None`` when no authoritative deployment telemetry exists so the
    dashboard renders a null/annotated state instead of a fabricated zero
    (``_is_deployment_event`` defines the authoritative deploy kind set).
    """
    placeholders, kinds = _dora_deploy_kind_placeholders()
    row = conn.execute(
        f"SELECT COUNT(*) FROM delivery_timeline_events WHERE event_kind IN ({placeholders})",
        kinds,
    ).fetchone()
    count = int(row[0]) if row and row[0] is not None else 0
    return count if count > 0 else None


def _dora_change_failure_rate(conn: sqlite3.Connection) -> float | None:
    """Percent of deployed changes linked to a rollback, hotfix, or incident.

    Denominator is the set of distinct ``deployable_change_id`` values on
    authoritative deploy events; numerator is that set intersected with the
    deploy ids referenced by rollback/hotfix linkage or incident causation.
    Returns ``None`` when no attributable deployment telemetry exists.
    """
    placeholders, kinds = _dora_deploy_kind_placeholders()
    deploy_ids = {
        str(r[0]).strip()
        for r in conn.execute(
            f"SELECT deployable_change_id FROM delivery_timeline_events WHERE event_kind IN ({placeholders})",
            kinds,
        )
        if str(r[0] or "").strip()
    }
    if not deploy_ids:
        return None
    reverted: set[str] = set()
    for column in ("rollback_of_deploy_id", "hotfix_of_deploy_id"):
        reverted |= {
            str(r[0]).strip()
            for r in conn.execute(f"SELECT {column} FROM delivery_timeline_events")
            if str(r[0] or "").strip()
        }
    incident_ids = {
        str(r[0]).strip() for r in conn.execute("SELECT caused_by_deploy_id FROM incidents") if str(r[0] or "").strip()
    }
    failed = deploy_ids & (reverted | incident_ids)
    return round(100.0 * len(failed) / len(deploy_ids), 1)


def _dora_mttr_hours(conn: sqlite3.Connection) -> float | None:
    """Mean hours from incident detection to mitigation (falls back to closure).

    Returns ``None`` when no incident carries both a detection timestamp and a
    resolution timestamp, so the panel renders a null/annotated state.
    """
    durations: list[float] = []
    for detected_at, mitigated_at, closed_at in conn.execute(
        "SELECT detected_at, mitigated_at, closed_at FROM incidents"
    ):
        start = _timestamp_unix(detected_at)
        end = _timestamp_unix(mitigated_at) or _timestamp_unix(closed_at)
        if start and end and end >= start:
            durations.append((end - start) / 3600.0)
    if not durations:
        return None
    return round(sum(durations) / len(durations), 1)


def _dora_four_keys_metric_rows(conn: sqlite3.Connection) -> list[tuple[Any, ...]]:
    """Return the four DORA keys as ``current_metrics`` rows (GTKB-DORA-002).

    Consumes the DORA-001 telemetry foundation persisted in
    ``delivery_timeline_events`` + ``incidents``. Each metric renders a
    null/annotated state when its underlying telemetry is insufficient, per the
    DORA-002 acceptance criteria and ``GOV-SESSION-SELF-INITIALIZATION-001``.
    Lead time is not yet computable because the foundation persists commit SHAs
    (``commit_range_start`` / ``commit_range_end``) but not per-commit authored
    timestamps; it is emitted null with an explanatory annotation rather than a
    fabricated value.
    """
    deployment_frequency = _dora_deployment_frequency(conn)
    change_failure_rate = _dora_change_failure_rate(conn)
    mttr_hours = _dora_mttr_hours(conn)
    lead_time_hours: float | None = None

    def status_for(value: Any) -> str:
        return _DORA_PRESENT_STATUS if value is not None else _DORA_INSUFFICIENT_STATUS

    return [
        (
            "dora_deployment_frequency",
            "Deployment Frequency",
            deployment_frequency,
            status_for(deployment_frequency),
            "Authoritative canonical_deploy events in the retained delivery timeline "
            "(DORA-001 foundation). Null when no deployment telemetry exists.",
        ),
        (
            "dora_lead_time_hours",
            "Lead Time for Changes (h)",
            lead_time_hours,
            status_for(lead_time_hours),
            "Median hours from change to deployment. Null/annotated: the DORA-001 "
            "timeline foundation persists commit SHAs but not per-commit authored "
            "timestamps, so lead time is not yet computable.",
        ),
        (
            "dora_change_failure_rate",
            "Change Failure Rate (%)",
            change_failure_rate,
            status_for(change_failure_rate),
            "Percent of deployed changes linked to a rollback, hotfix, or caused "
            "incident. Null when no attributable deployment telemetry exists.",
        ),
        (
            "dora_mttr_hours",
            "MTTR (h)",
            mttr_hours,
            status_for(mttr_hours),
            "Mean hours from incident detection to mitigation (falls back to "
            "closure). Null when no resolved incidents exist.",
        ),
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
    launch_record: Path


@dataclass(frozen=True)
class DashboardProcessInfo:
    """Process IDs, user-facing URLs and the containing job produced by ``start_dashboard``."""

    grafana_pid: int
    refresh_pid: int
    grafana_url: str
    refresh_url: str
    job: str | None = None


StoppedProcess = job_containment.StoppedProcess


def resolve_dashboard_paths(
    config: GTConfig,
    *,
    db_path: Path | None = None,
    runtime_root: Path | None = None,
    grafana_home: Path | None = None,
) -> DashboardPaths:
    """Resolve dashboard paths relative to a GroundTruth project."""
    project_root = config.project_root.resolve()
    runtime = (runtime_root or dashboard_link.default_dashboard_runtime_root(project_root)).resolve()
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
        launch_record=runtime / LAUNCH_RECORD_NAME,
    )


def refresh_dashboard_db(paths: DashboardPaths, config: GTConfig, *, probe_live: bool = False) -> dict[str, Any]:
    """Refresh installed observations and explicitly requested live probes."""
    return refresh_database(
        paths.db_path, paths.project_root, config=config, runtime_root=paths.runtime_root, probe_live=probe_live
    )


def write_grafana_assets(
    paths: DashboardPaths, config: GTConfig, *, grafana_port: int = 3000, refresh_port: int = 8766
) -> None:
    """Derive Grafana assets from installed sources, independently of source checkout files."""
    from groundtruth_kb.dashboard_grafana import build_dashboard

    datasource_dir = paths.provisioning_dir / "datasources"
    provider_dir = paths.provisioning_dir / "dashboards"
    for directory in (datasource_dir, provider_dir, paths.dashboards_dir):
        directory.mkdir(parents=True, exist_ok=True)
    datasource = {
        "apiVersion": 1,
        "datasources": [
            {
                "name": "GT-KB Dashboard SQLite",
                "uid": SQLITE_DATASOURCE_UID,
                "type": SQLITE_PLUGIN_ID,
                "access": "proxy",
                "isDefault": True,
                "editable": False,
                "jsonData": {"path": paths.db_path.as_posix()},
            }
        ],
    }
    provider = {
        "apiVersion": 1,
        "providers": [
            {
                "name": "GT-KB",
                "orgId": 1,
                "folder": "GT-KB",
                "type": "file",
                "disableDeletion": False,
                "editable": False,
                "updateIntervalSeconds": 30,
                "options": {"path": paths.dashboards_dir.as_posix()},
            }
        ],
    }
    (datasource_dir / "gtkb-dashboard-sqlite.yml").write_text(
        yaml.safe_dump(datasource, sort_keys=False), encoding="utf-8"
    )
    (provider_dir / "gtkb-dashboard.yml").write_text(yaml.safe_dump(provider, sort_keys=False), encoding="utf-8")
    dashboard = build_dashboard()
    dashboard = json.loads(json.dumps(dashboard).replace("127.0.0.1:8766", f"127.0.0.1:{refresh_port}"))
    dashboard["title"] = config.app_title + " — GT-KB Dashboard"
    (paths.dashboards_dir / "gtkb-dashboard.json").write_text(
        json.dumps(dashboard, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    sources = get_templates_dir() / "dashboard"
    (paths.runtime_root / "index.html").write_text(
        (sources / "index.html").read_text(encoding="utf-8").replace("127.0.0.1:3000", f"127.0.0.1:{grafana_port}"),
        encoding="utf-8",
    )
    alerting = paths.provisioning_dir / "alerting"
    alerting.mkdir(parents=True, exist_ok=True)
    for source in (sources / "alerting").glob("*.yaml"):
        shutil.copyfile(source, alerting / source.name)


def initialize_dashboard(
    paths: DashboardPaths,
    config: GTConfig,
    *,
    grafana_port: int = 3000,
    refresh_port: int = 8766,
    schema_only: bool = False,
    probe_live: bool = False,
) -> dict[str, Any]:
    """Initialize reporting schema or refresh observations and materialize display assets."""
    if paths.db_path.resolve() == config.db_path.resolve():
        raise ValueError("dashboard_db_must_be_derived")
    if schema_only:
        if probe_live:
            raise ValueError("schema_only_cannot_probe_live")
        moved_aside = _ensure_derived_schema(paths.db_path, paths.runtime_root)
        initialized: dict[str, Any] = {"status": "initialized", "refreshed": False}
        if moved_aside is not None:
            initialized["legacy_database_moved_to"] = str(moved_aside)
        return initialized
    result = refresh_dashboard_db(paths, config, probe_live=probe_live)
    write_grafana_assets(paths, config, grafana_port=grafana_port, refresh_port=refresh_port)
    return result


def install_grafana(paths: DashboardPaths, *, skip_download: bool = False, skip_plugin: bool = False) -> Path:
    """Install Grafana OSS locally and install the SQLite datasource plugin."""
    paths.grafana_home.mkdir(parents=True, exist_ok=True)
    grafana_bin = find_grafana_server(paths.grafana_home)
    downloaded = False
    if grafana_bin is None and skip_download:
        raise FileNotFoundError(
            f"Grafana was not found under {paths.grafana_home}. "
            "Run without --skip-download or set --grafana-home to an existing installation."
        )
    if grafana_bin is None:
        _download_grafana_windows(paths.grafana_home)
        downloaded = True
        grafana_bin = find_grafana_server(paths.grafana_home)
    if grafana_bin is None:
        raise FileNotFoundError(f"Grafana server executable was not found under {paths.grafana_home}")
    if not skip_plugin:
        _install_sqlite_plugin(paths.grafana_home)
    plugin_root = paths.grafana_home / "data/plugins" / SQLITE_PLUGIN_ID
    plugin = None
    if plugin_root.exists():
        plugin = _verify_sqlite_plugin(grafana_bin, plugin_root)
    elif not skip_plugin:
        raise ValueError("grafana_plugin_missing_after_install")
    observation = {
        "observed_at": datetime.now(UTC).isoformat(),
        "grafana_binary": str(grafana_bin),
        "grafana_binary_sha256": hashlib.sha256(grafana_bin.read_bytes()).hexdigest(),
        "archive": {"url": GRAFANA_ARCHIVE_URL, "sha256": GRAFANA_ARCHIVE_SHA256} if downloaded else None,
        "archive_verified_by_this_install": downloaded,
        "plugin": plugin,
        "plugin_verification": "verified" if plugin else "absent_unverified",
        "plugin_install_skipped": skip_plugin,
        "purpose": "Installation provenance observation; no runtime or canonical authority depends on this file.",
    }
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=paths.grafana_home, delete=False) as output:
            temporary = Path(output.name)
            json.dump(observation, output, indent=2, allow_nan=False)
            output.write("\n")
        temporary.replace(paths.grafana_home / "installed.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return grafana_bin


def _plugin_file_identities(root: Path) -> dict[str, str]:
    """Inspect ordinary files only; a redirected entry cannot identify this plugin."""
    identities = {}
    for path in [root, *sorted(root.rglob("*"))]:
        if path.is_symlink() or path.is_junction():
            raise ValueError("grafana_plugin_redirected_path")
        if path.is_file():
            identities[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError("grafana_plugin_invalid_file")
    return identities


def _verify_sqlite_plugin(grafana_bin: Path, plugin_root: Path, *, timeout: float = 60) -> dict[str, Any]:
    """Ask the pinned Grafana runtime to verify exactly these bytes, then stop it.

    This installation observation is neither dashboard readiness nor a review
    of plugin behavior. Temporary credentials and data never become runtime state.
    """
    before = _plugin_file_identities(plugin_root)
    metadata = json.loads((plugin_root / "plugin.json").read_text(encoding="utf-8"))
    if (
        not isinstance(metadata, dict)
        or metadata.get("id") != SQLITE_PLUGIN_ID
        or not isinstance(metadata.get("info"), dict)
        or metadata["info"].get("version") != SQLITE_PLUGIN_VERSION
    ):
        raise ValueError("Installed SQLite plugin identity differs from the pinned version")
    binary_hash = hashlib.sha256(grafana_bin.read_bytes()).hexdigest()
    home = grafana_bin.parent.parent.resolve()
    temporary = Path(tempfile.mkdtemp(prefix="plugin-verification-", dir=home)).resolve()
    process = None
    identity = None
    cleanup_confirmed = True
    try:
        copied = temporary / "plugins" / SQLITE_PLUGIN_ID
        shutil.copytree(plugin_root, copied)
        if _plugin_file_identities(copied) != before:
            raise ValueError("grafana_plugin_changed_during_copy")
        for leaf in ("data", "logs", "provisioning"):
            (temporary / leaf).mkdir()
        config = temporary / "grafana.ini"
        config.write_text(
            "app_mode = production\n[server]\nhttp_addr = 127.0.0.1\n"
            "[analytics]\nreporting_enabled = false\ncheck_for_updates = false\n"
            "check_for_plugin_updates = false\n[plugins]\npreinstall_disabled = true\n"
            "allow_loading_unsigned_plugins =\npublic_key_retrieval_disabled = true\n"
            "[log]\nmode = console\nlevel = error\n",
            encoding="utf-8",
        )
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        username, password = "plugin-verifier", secrets.token_urlsafe(32)
        env = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "PATHEXT", "COMSPEC", "TEMP", "TMP"}
        }
        env.update(GF_SECURITY_ADMIN_USER=username, GF_SECURITY_ADMIN_PASSWORD=password)
        args = [
            str(grafana_bin),
            *(["server"] if grafana_bin.stem == "grafana" else []),
            "--homepath",
            str(home),
            "--config",
            str(config),
            *[f"cfg:default.paths.{leaf}={temporary / leaf}" for leaf in ("data", "logs", "plugins", "provisioning")],
            f"cfg:server.http_port={port}",
        ]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        authorization = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()

        def request(route: str, seconds: float) -> dict[str, Any]:
            query = urllib.request.Request(f"http://127.0.0.1:{port}{route}", headers={"Authorization": authorization})
            with opener.open(query, timeout=seconds) as response:
                body = json.loads(response.read(65537))
            if not isinstance(body, dict):
                raise ValueError("grafana_verifier_invalid_response")
            return body

        with (temporary / "verifier.log").open("wb") as log:
            process = subprocess.Popen(
                args,
                cwd=home,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        cleanup_confirmed = False
        identity = _process_identity(process.pid)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("grafana_verifier_exited_before_readiness")
            try:
                health = request("/api/health", min(2, max(0.1, deadline - time.monotonic())))
            except (OSError, ValueError):
                time.sleep(0.1)
                continue
            if health.get("database") == "ok":
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("grafana_verifier_readiness_timeout")
        if health.get("version") != GRAFANA_VERSION:
            raise ValueError("grafana_verifier_version_differs_from_pin")
        try:
            settings = request(f"/api/plugins/{SQLITE_PLUGIN_ID}/settings", 5)
        except urllib.error.HTTPError as error:
            raise ValueError(f"grafana_plugin_verification_http_{error.code}") from None
        except (OSError, ValueError):
            raise ValueError("grafana_plugin_verification_unavailable") from None
        expected = {"id": SQLITE_PLUGIN_ID, "signature": "valid", "signatureType": "community", "signatureOrg": "frser"}
        if (
            any(settings.get(key) != value for key, value in expected.items())
            or not isinstance(settings.get("info"), dict)
            or settings["info"].get("version") != SQLITE_PLUGIN_VERSION
        ):
            raise ValueError("grafana_plugin_signature_or_identity_mismatch")
        if process.poll() is not None:
            raise RuntimeError("grafana_verifier_exited_during_verification")
        if _plugin_file_identities(copied) != before or _plugin_file_identities(plugin_root) != before:
            raise ValueError("grafana_plugin_changed_during_verification")
        if hashlib.sha256(grafana_bin.read_bytes()).hexdigest() != binary_hash:
            raise ValueError("grafana_verifier_binary_changed")
        result = {
            "id": SQLITE_PLUGIN_ID,
            "version": SQLITE_PLUGIN_VERSION,
            "files_sha256": before,
            "signature": {key: settings[key] for key in ("signature", "signatureType", "signatureOrg")},
            "verifier_version": health["version"],
            "verifier_binary_sha256": binary_hash,
            "verified_at": datetime.now(UTC).isoformat(),
        }
    finally:
        if process is not None:
            try:
                if process.poll() is None and (identity is None or not _terminate_pid(process.pid, identity)):
                    raise RuntimeError("termination_not_confirmed")
                process.wait(timeout=10)
                cleanup_confirmed = True
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                raise RuntimeError(
                    f"grafana_verifier_cleanup_unconfirmed: pid={process.pid}; inspect {temporary}"
                ) from None
        if cleanup_confirmed:
            if temporary.parent != home or not temporary.name.startswith("plugin-verification-"):
                raise RuntimeError("grafana_verifier_temporary_path_changed")
            shutil.rmtree(temporary)
    if _plugin_file_identities(plugin_root) != before:
        raise ValueError("grafana_plugin_changed_during_verification")
    if hashlib.sha256(grafana_bin.read_bytes()).hexdigest() != binary_hash:
        raise ValueError("grafana_verifier_binary_changed")
    return result


def start_dashboard(
    paths: DashboardPaths,
    config: GTConfig,
    *,
    grafana_port: int = DEFAULT_GRAFANA_PORT,
    refresh_port: int = DEFAULT_REFRESH_PORT,
    interval_minutes: int = DEFAULT_REFRESH_INTERVAL_MINUTES,
    config_path: Path | None = None,
) -> DashboardProcessInfo:
    """Start the selected local display under kill-on-close job containment, confirming readiness first.

    On Windows both launches - the refresh service (a venv redirector and its child) and Grafana (grafana.exe and
    its plugin children) - are created suspended, placed in one named kill-on-close job for this runtime root and
    only then resumed, so no descendant ever exists outside the job. The children inherit the job handle, which
    keeps the job alive exactly as long as one of them lives; ``stop_dashboard`` opens the job by name and ends
    every member. The launch record under the runtime root names the job and the launched processes for
    reporting; on Windows it decides nothing about what is signalled. Elsewhere there is no job: the record
    carries each process's creation identity and ``stop_dashboard`` signals only a process whose identity still
    matches.
    """
    if not all(0 < p < 65536 for p in (grafana_port, refresh_port)) or grafana_port == refresh_port:
        raise ValueError("Dashboard ports must be different and in 1..65535")
    if interval_minutes < 1:
        raise ValueError("interval_minutes must be positive")
    grafana_bin = find_grafana_server(paths.grafana_home)
    if grafana_bin is None:
        raise FileNotFoundError("Grafana is not installed. Run `gt dashboard install` first.")
    selected_config = (config_path or config_path_for_project(paths.project_root)).resolve()
    selected = GTConfig.load(config_path=selected_config, discover=False)
    if selected != config:
        raise ValueError("Selected configuration differs from the dashboard launch configuration")
    record = _read_launch_record(paths.launch_record)
    job_name = _dashboard_job_name(paths.runtime_root) if sys.platform == "win32" else None
    job: int | None = None
    live: dict[str, _LaunchedProcess] = {}
    if sys.platform == "win32":
        job = _open_dashboard_job(job_name or "")
        if job is not None:
            contained = set(_job_member_pids(job))
            if record is None or record.get("job") != job_name:
                _close_handle(job)
                raise DashboardIdentityError(
                    f"dashboard job {job_name} is running for {paths.runtime_root} without a matching launch "
                    "record; run `gt dashboard stop` before starting"
                )
            live = {m["role"]: m for m in record["members"] if m["pid"] in contained}
        elif record is not None:
            paths.launch_record.unlink()  # nothing runs under this record any more
            record = None
    elif record is not None:
        live = {m["role"]: m for m in record["members"] if _process_identity(m["pid"]) == _identity_of(m)}
    refresh_pid = live["refresh-service"]["pid"] if "refresh-service" in live else None
    grafana_pid = live["grafana"]["pid"] if "grafana" in live else None
    try:
        for pid, port in ((refresh_pid, refresh_port), (grafana_pid, grafana_port)):
            if pid is None:
                with socket.socket() as probe:
                    probe.bind(("127.0.0.1", port))
        # A launch for the same runtime must use its selected configuration and interval.
        expected = {
            "project_root": str(paths.project_root),
            "runtime_root": str(paths.runtime_root),
            "dashboard_db": str(paths.db_path),
            "interval_seconds": interval_minutes * 60,
            "config_path": str(selected_config),
            "grafana_port": grafana_port,
        }
        if refresh_pid is not None:
            _wait_dashboard_http(refresh_pid, f"http://127.0.0.1:{refresh_port}/health", expected, timeout=2)
        if grafana_pid is not None:
            _wait_dashboard_http(
                grafana_pid, f"http://127.0.0.1:{grafana_port}/api/health", {"database": "ok"}, timeout=2
            )
    except BaseException:
        if job is not None:
            _close_handle(job)
        raise
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    paths.runtime_root.mkdir(parents=True, exist_ok=True)
    created_job = False
    if sys.platform == "win32" and job is None and (refresh_pid is None or grafana_pid is None):
        job = _create_dashboard_job(job_name or "")
        created_job = True
    started: list[tuple[subprocess.Popen[bytes], str, _ProcessIdentity]] = []

    def launch(args: list[str], cwd: Path, env: dict[str, str], role: str, log_name: str) -> int:
        # Dashboard children observe HTTP authority and never inherit database credentials or overrides.
        env = {key: value for key, value in env.items() if not key.upper().startswith(("PG", "GT_POSTGRES_"))}
        with (paths.logs_dir / log_name).open("a", encoding="utf-8") as log:
            if job is not None:
                process = _start_contained(args, cwd, env, log, job)
            else:
                process = subprocess.Popen(
                    args,
                    cwd=cwd,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        identity = _process_identity(process.pid)
        if identity is None:
            process.wait(timeout=5)
            raise RuntimeError(f"Dashboard process exited during launch; inspect {log_name}")
        started.append((process, role, identity))
        return process.pid

    try:
        # The service generates assets on startup; the parent never races its writer.
        if refresh_pid is None:
            refresh_pid = launch(
                [
                    sys.executable,
                    "-m",
                    "groundtruth_kb.dashboard_service",
                    "--config",
                    str(selected_config),
                    "--db-path",
                    str(paths.db_path),
                    "--runtime-root",
                    str(paths.runtime_root),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(refresh_port),
                    "--grafana-port",
                    str(grafana_port),
                    "--interval-minutes",
                    str(interval_minutes),
                ],
                paths.project_root,
                os.environ.copy(),
                "refresh-service",
                "refresh-service.log",
            )
        _wait_dashboard_http(refresh_pid, f"http://127.0.0.1:{refresh_port}/health", expected)
        if grafana_pid is None:
            (paths.runtime_root / "grafana-data").mkdir(parents=True, exist_ok=True)
            grafana_env = os.environ.copy()
            grafana_env.update(
                {
                    "GF_PATHS_DATA": str(paths.runtime_root / "grafana-data"),
                    "GF_PATHS_LOGS": str(paths.logs_dir),
                    "GF_PATHS_PLUGINS": str(paths.grafana_home / "data/plugins"),
                    "GF_PATHS_PROVISIONING": str(paths.provisioning_dir),
                    "GF_SERVER_HTTP_PORT": str(grafana_port),
                    "GF_SERVER_HTTP_ADDR": "127.0.0.1",
                    **GRAFANA_LAUNCH_PINS,
                }
            )
            grafana_pid = launch(
                [
                    str(grafana_bin),
                    *(["server"] if grafana_bin.stem == "grafana" else []),
                    "--homepath",
                    str(grafana_bin.parent.parent),
                ],
                grafana_bin.parent.parent,
                grafana_env,
                "grafana",
                "grafana.log",
            )
        _wait_dashboard_http(grafana_pid, f"http://127.0.0.1:{grafana_port}/api/health", {"database": "ok"})
        if started:  # a launch that reused every running member leaves its record as it is
            members: list[_LaunchedProcess] = list(live.values())
            for _process, role, identity in started:
                members.append(
                    {
                        "role": role,
                        "pid": identity["pid"],
                        "created_at": identity["created_at"],
                        "executable": identity["executable"],
                    }
                )
            started_at = (record or {}).get("started_at") if live else None
            _write_launch_record(
                paths.launch_record,
                {
                    "job": job_name,
                    "members": sorted(members, key=lambda m: m["role"]),
                    "grafana_port": grafana_port,
                    "refresh_port": refresh_port,
                    "interval_seconds": interval_minutes * 60,
                    "config_path": str(selected_config),
                    "started_at": started_at or datetime.now(UTC).isoformat(),
                },
            )
    except BaseException:
        try:
            if created_job and job is not None:
                _stop_job(job, job_name or "")
            else:
                for process, _role, identity in reversed(started):
                    if process.poll() is None:
                        _terminate_pid(process.pid, identity)
                        process.wait(timeout=10)
        except (DashboardStopError, OSError, subprocess.TimeoutExpired) as cleanup:
            raise RuntimeError(f"Dashboard startup failed and process cleanup needs inspection: {cleanup}") from None
        raise
    finally:
        if job is not None:
            _close_handle(job)
    return DashboardProcessInfo(
        grafana_pid=grafana_pid,
        refresh_pid=refresh_pid,
        grafana_url=dashboard_link.grafana_dashboard_url(grafana_port),
        refresh_url=dashboard_link.refresh_service_url(refresh_port),
        job=job_name,
    )


def _wait_dashboard_http(pid: int, url: str, expected: dict[str, Any], *, timeout: float = 60) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _pid_alive(pid):
            raise RuntimeError(f"Dashboard process {pid} exited before readiness; inspect dashboard logs")
        try:
            with urllib.request.urlopen(url, timeout=min(2, max(0.1, deadline - time.monotonic()))) as response:
                payload = json.loads(response.read())
        except (OSError, ValueError):
            time.sleep(0.1)
            continue
        if not isinstance(payload, dict) or any(payload.get(k) != v for k, v in expected.items()):
            raise RuntimeError("Dashboard endpoint does not match the requested runtime; inspect the existing launch")
        if "last_result" in payload:
            result = payload["last_result"]
            if payload.get("last_error") or (isinstance(result, dict) and result.get("status") == "failed"):
                raise RuntimeError("Dashboard startup refresh failed; inspect the refresh-service log")
            if result is None or payload.get("refreshing"):
                time.sleep(0.1)
                continue
        if _pid_alive(pid):
            return
    raise RuntimeError("Dashboard readiness timed out; inspect dashboard logs")


def stop_dashboard(paths: DashboardPaths) -> list[StoppedProcess]:
    """End the dashboard launched for this runtime and report exactly what was ended.

    Windows: this runtime's kill-on-close job is opened by name, a handle to every member is held, the job is
    terminated and the stop waits until every held handle is signalled and the job counts no active process.
    Nothing outside the job is ever touched and no recorded number decides what is signalled; a member that
    exited on its own before the stop is reported as ``exited``. Failures are distinguishable:
    ``DashboardTerminationRefused`` (the job refused termination) and ``DashboardTerminationUnconfirmed``
    (a member outlived the wait); the launch record is kept for inspection in both cases. Elsewhere the launch
    record's members are signalled only while their creation identity still matches
    (``DashboardIdentityError`` otherwise).
    """
    record = _read_launch_record(paths.launch_record)
    stopped: list[StoppedProcess] = []
    if sys.platform == "win32":
        job_name = _dashboard_job_name(paths.runtime_root)
        job = _open_dashboard_job(job_name)
        if job is not None:
            try:
                stopped = _stop_job(job, job_name)
            finally:
                _close_handle(job)
    elif record is not None:
        for member in record["members"]:
            if _process_identity(member["pid"]) is None:
                stopped.append(StoppedProcess(member["pid"], member["executable"], "exited"))
                continue
            _terminate_pid(member["pid"], _identity_of(member))
            stopped.append(StoppedProcess(member["pid"], member["executable"], "signalled"))
    paths.launch_record.unlink(missing_ok=True)
    return stopped


def config_path_for_project(project_root: Path) -> Path:
    """Return the conventional config path for a project root."""
    return project_root / "groundtruth.toml"


def find_grafana_server(grafana_home: Path) -> Path | None:
    """Find one unambiguous installation, accepting current and legacy binary names."""
    names = ("grafana.exe", "grafana-server.exe") if sys.platform == "win32" else ("grafana", "grafana-server")
    roots = [grafana_home, *sorted(grafana_home.glob("grafana-*"))]
    matches = []
    for root in roots:
        for name in names:
            candidate = root / "bin" / name
            if candidate.is_file() and (root / "conf/defaults.ini").is_file():
                matches.append(candidate)
                break
    if len(matches) > 1:
        raise ValueError("Multiple Grafana installations found; select one with --grafana-home")
    return matches[0] if matches else None


def _download_grafana_windows(target: Path) -> None:
    """Install the pinned OSS Windows AMD64 release from Grafana's official distribution."""
    if sys.platform != "win32":
        raise RuntimeError("Automatic Grafana download is implemented for Windows AMD64 only; use --grafana-home.")
    if target.exists() and any(target.iterdir()):
        raise ValueError("Grafana installation target is not empty; inspect it or select an existing --grafana-home")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Use the extended path for the entire temporary directory lifecycle,
    # including cleanup when validation or extraction fails.
    parent = str(target.parent.resolve())
    if not parent.startswith("\\\\?\\"):
        parent = "\\\\?\\" + parent
    with tempfile.TemporaryDirectory(prefix="grafana-install-", dir=parent) as temporary:
        staging = Path(temporary).resolve()
        archive_path = staging / "release.tar.gz"
        digest = hashlib.sha256()
        with urllib.request.urlopen(GRAFANA_ARCHIVE_URL, timeout=30) as response, archive_path.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != GRAFANA_ARCHIVE_SHA256:
            raise ValueError("Grafana archive checksum does not match the pinned release")
        extracted = staging / "extracted"

        def windows_member(member: tarfile.TarInfo, destination: str) -> tarfile.TarInfo:
            filtered = tarfile.data_filter(member, destination)
            # Extended Windows paths require backslashes, including directory
            # entries when tarfile subsequently restores their attributes.
            return filtered.replace(name=filtered.name.replace("/", "\\"))

        with tarfile.open(archive_path) as archive:
            archive.extractall(extracted, filter=windows_member)
        binary = find_grafana_server(extracted)
        if binary is None:
            raise ValueError("Grafana archive does not contain the expected installation")
        source = binary.parent.parent.resolve()
        if not source.is_relative_to(staging) or target.resolve() == staging:
            raise ValueError("Invalid Grafana extraction path")
        if target.exists():
            target.rmdir()  # Empty only; an existing installation is never replaced.
        source.rename(target)


def _install_sqlite_plugin(grafana_home: Path) -> None:
    server = find_grafana_server(grafana_home)
    if server is None:
        raise FileNotFoundError("Grafana was not found; select its installation with --grafana-home")
    home = server.parent.parent
    if server.stem == "grafana":
        command = [str(server), "cli"]
    else:
        cli = home / "bin" / ("grafana-cli.exe" if sys.platform == "win32" else "grafana-cli")
        if not cli.is_file():
            raise FileNotFoundError("Grafana CLI was not found in the selected installation")
        command = [str(cli)]
    plugins = grafana_home / "data/plugins"
    plugins.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            *command,
            "--homepath",
            str(home),
            "--pluginsDir",
            str(plugins),
            "plugins",
            "install",
            SQLITE_PLUGIN_ID,
            SQLITE_PLUGIN_VERSION,
        ],
        cwd=home,
        check=True,
        timeout=180,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    metadata = json.loads((plugins / SQLITE_PLUGIN_ID / "plugin.json").read_text(encoding="utf-8"))
    if metadata.get("id") != SQLITE_PLUGIN_ID or metadata.get("info", {}).get("version") != SQLITE_PLUGIN_VERSION:
        raise ValueError("Installed SQLite plugin identity differs from the pinned version")


if sys.platform == "win32":
    _kernel32 = job_containment.kernel32


_close_handle = job_containment.close_handle
_windows_process = job_containment.windows_process
_process_identity = job_containment.process_identity


def _pid_alive(pid: int) -> bool:
    return _process_identity(pid) is not None


def _identity_of(member: _LaunchedProcess) -> _ProcessIdentity:
    return {"pid": member["pid"], "created_at": member["created_at"], "executable": member["executable"]}


def _read_launch_record(path: Path) -> dict[str, Any] | None:
    """The launch record under the runtime root, or None when there is none; a malformed record needs inspection."""
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise ValueError("dashboard launch record requires inspection before reuse") from error
    if not isinstance(record, dict) or not isinstance(record.get("members"), list):
        raise ValueError("dashboard launch record requires inspection before reuse")
    for member in record["members"]:
        if not (
            isinstance(member, dict)
            and set(member) == {"role", "pid", "created_at", "executable"}
            and type(member["pid"]) is int
            and member["pid"] > 0
            and all(isinstance(member[key], str) and member[key] for key in ("role", "created_at", "executable"))
        ):
            raise ValueError("dashboard launch record requires inspection before reuse")
    return record


def _write_launch_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _dashboard_job_name(runtime_root: Path) -> str:
    """The session-local kill-on-close job that contains every process launched for this runtime root."""
    return job_containment.job_name(DASHBOARD_JOB_PREFIX, runtime_root)


def _create_dashboard_job(name: str) -> int:
    """Create the named kill-on-close job with an inheritable handle; refuse a name that already exists."""
    try:
        return job_containment.create_job(name, inheritable=True)
    except job_containment.JobAlreadyExists:
        raise DashboardIdentityError(
            f"dashboard job {name} already exists (another launch is in progress or the name is held elsewhere); "
            "run `gt dashboard stop` and retry"
        ) from None


_open_dashboard_job = job_containment.open_job
_job_member_pids = job_containment.job_member_pids
_assign_to_job = job_containment.assign_to_job
_resume_primary_thread = job_containment.resume_primary_thread


def _start_contained(args: list[str], cwd: Path, env: dict[str, str], log: Any, job: int) -> subprocess.Popen[bytes]:
    """Create a dashboard process suspended, place it in the job, then let it run (groundtruth_kb.job_containment).

    The process inherits the job handle so the job outlives this launcher; a process that cannot be placed in the
    job or resumed is ended while still suspended and job_containment.ContainmentError is raised. The module-level
    ``_assign_to_job``/``_resume_primary_thread`` names are passed at call time: they are the seam the tests patch.
    """
    return job_containment.start_contained(
        args,
        env,
        job,
        inherit_job=True,
        cwd=cwd,
        stdout=log,
        stderr=subprocess.STDOUT,
        assign=_assign_to_job,
        resume=_resume_primary_thread,
    )


def _stop_job(job: int, name: str, *, timeout: float = 15.0) -> list[StoppedProcess]:
    """Terminate every member of an open job and confirm each one ended; report what was accounted for."""
    try:
        return job_containment.stop_job(job, name, timeout=timeout, members=_job_member_pids)
    except job_containment.JobTerminationRefused as error:
        raise DashboardTerminationRefused(str(error)) from error
    except job_containment.JobTerminationUnconfirmed as error:
        raise DashboardTerminationUnconfirmed(str(error)) from error


def _terminate_pid(pid: int, expected: _ProcessIdentity) -> bool:
    """End the process tree rooted at ``pid`` if it is still the launched process; True once it is gone.

    Windows: the process is opened and held so its number cannot be reused during the request; ``taskkill /T``
    ends the tree (a venv redirector's child included) and the held handle decides: a signalled handle confirms
    termination even when taskkill reports a non-zero exit for a member (logged as a warning with its output).
    Failures are distinguishable: ``DashboardIdentityError`` (the number now belongs to another process;
    nothing is signalled), ``DashboardTerminationRefused`` (taskkill failed and the process still runs) and
    ``DashboardTerminationUnconfirmed`` (taskkill succeeded but the handle stayed unsignalled for 5 s).
    """
    if sys.platform == "win32":
        with _windows_process(pid) as (current, held):
            if current is None:
                return True
            if current != expected:
                raise DashboardIdentityError(
                    f"process {pid} is now {current['executable']} created at {current['created_at']}, not the "
                    f"launched {expected['executable']} created at {expected['created_at']}; nothing was signalled"
                )
            if held is None:
                raise RuntimeError("dashboard process handle unavailable")
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            output = (result.stdout + result.stderr).decode("utf-8", "replace").strip()
            kernel, handle = held
            if kernel.WaitForSingleObject(handle, 5000) == 0:
                if result.returncode != 0:
                    logger.warning(
                        "taskkill exited %s for dashboard process %s although the process ended: %s",
                        result.returncode,
                        pid,
                        output,
                    )
                return True
            if result.returncode != 0:
                raise DashboardTerminationRefused(
                    f"taskkill exited {result.returncode} for dashboard process {pid} and the process still runs: "
                    f"{output}"
                )
            raise DashboardTerminationUnconfirmed(
                f"taskkill accepted the request for dashboard process {pid} but the process had not ended after 5 s"
            )
    import signal

    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise RuntimeError("qualified dashboard process stopping is unavailable on this host")
    try:
        descriptor = os.pidfd_open(pid)
    except ProcessLookupError:
        return True
    try:
        current = _process_identity(pid)
        if current != expected:
            raise DashboardIdentityError(f"process {pid} is not the launched process; nothing was signalled")
        signal.pidfd_send_signal(descriptor, signal.SIGTERM)
        return True
    finally:
        os.close(descriptor)
