#!/usr/bin/env python3
"""Refresh the GT-KB Grafana dashboard SQLite database."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
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


class IncidentIngestError(RuntimeError):
    """Raised when memory/incidents.yaml cannot be parsed or validated."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
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
        "command": "cd agent-red-customer-engagement",
        "link_label": "Agent Red repository",
        "link_url": "https://github.com/Remaker-Digital/agent-red-customer-engagement",
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
        "purpose": "Supports Azure resource inspection, deployments, and staging/production environment checks.",
        "check_command": "az version",
        "install_reference": "https://learn.microsoft.com/cli/azure/install-azure-cli",
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
        "required_env_vars": "AGENT_RED_GITHUB_REPO, GROUND_TRUTH_GITHUB_REPO; gh authentication for local inspection",
        "setup_summary": "Authenticate gh, confirm repository access, and verify required workflows under .github/workflows.",
        "console_url": "https://github.com/Remaker-Digital/agent-red-customer-engagement/actions",
        "health_signal": "workflow run status and local gh availability",
    },
    {
        "name": "Azure OpenAI",
        "category": "AI service",
        "purpose": "Provides chat/completion and embedding deployments for Agent Red runtime behavior.",
        "required_env_vars": "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION",
        "setup_summary": "Create or select Azure OpenAI deployments and map deployment names into .env.local.",
        "console_url": "https://portal.azure.com/",
        "health_signal": "environment variables plus application health checks",
    },
    {
        "name": "Azure Cosmos DB",
        "category": "Database",
        "purpose": "Stores tenant, conversation, configuration, memory, and operational records.",
        "required_env_vars": "COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE",
        "setup_summary": "Use staging by default; production database values require explicit release approval.",
        "console_url": "https://portal.azure.com/",
        "health_signal": "API readiness and Cosmos connectivity checks",
    },
    {
        "name": "Azure Key Vault",
        "category": "Secrets and encryption",
        "purpose": "Holds HSM-backed key encryption keys and tenant secret material.",
        "required_env_vars": "AZURE_KEYVAULT_URL, MASTER_KEK_KEY_ID",
        "setup_summary": "Create staging and production vault references and grant the runtime identity read/use permissions.",
        "console_url": "https://portal.azure.com/",
        "health_signal": "runtime secret access and envelope encryption tests",
    },
    {
        "name": "Shopify Partners",
        "category": "Commerce integration",
        "purpose": "Supports embedded Shopify admin install, storefront data, billing, and merchant workflows.",
        "required_env_vars": "SHOPIFY_STORE_URL, SHOPIFY_API_KEY, SHOPIFY_API_SECRET, SHOPIFY_ACCESS_TOKEN",
        "setup_summary": "Create or configure the Shopify custom app, callback URLs, scopes, and test store credentials.",
        "console_url": "https://partners.shopify.com/",
        "health_signal": "Shopify app/auth integration tests",
    },
    {
        "name": "Stripe",
        "category": "Billing",
        "purpose": "Handles subscription, checkout, catalog, overage, and webhook billing flows.",
        "required_env_vars": "STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET",
        "setup_summary": "Create test products/prices, configure webhook endpoint, and store test keys in .env.local.",
        "console_url": "https://dashboard.stripe.com/",
        "health_signal": "Stripe catalog and webhook tests",
    },
    {
        "name": "Zendesk",
        "category": "Support integration",
        "purpose": "Connects escalation and customer support handoff workflows.",
        "required_env_vars": "ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN",
        "setup_summary": "Create API token, confirm support subdomain, and validate escalation credentials.",
        "console_url": "https://www.zendesk.com/login/",
        "health_signal": "integration configuration and escalation tests",
    },
    {
        "name": "Mailchimp",
        "category": "Marketing integration",
        "purpose": "Supports customer communication and marketing integration surfaces.",
        "required_env_vars": "MAILCHIMP_API_KEY",
        "setup_summary": "Create API key in the target Mailchimp account and set it only in local/staging secrets.",
        "console_url": "https://mailchimp.com/",
        "health_signal": "integration configuration checks",
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


def refresh_database(
    db_path: Path = DEFAULT_DB_PATH,
    project_root: Path = PROJECT_ROOT,
    model: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(UTC).isoformat()
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
            model = session_module.build_startup_model(project_root)
        if history is None:
            if session_module is None:
                session_module = _load_session_module()
            snapshot = session_module._snapshot_from_model(model)
            previous_history = _read_existing_history(db_path)
            history = _append_snapshot(previous_history, snapshot)
        _write_model_to_db(db_path, model, history, project_root)
        _write_bridge_swimlane_safe(project_root)
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
        from .generate_bridge_swimlane import write_swimlane

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
) -> None:
    metrics = model.get("metrics", {})
    intelligence = model.get("dashboard_intelligence", {})
    infrastructure = model.get("infrastructure", {})
    delivery = infrastructure.get("delivery_timeline", {})

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

        metadata = {
            "generated_at": model.get("generated_at", ""),
            "role": model.get("role", {}).get("assumed_role", ""),
            "scope_note": model.get("dashboard_requirements", {}).get("scope_note", ""),
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
                for idx, item in enumerate(intelligence.get("health", []), start=1)
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
        # structured deployment evidence + reconcile against Azure revisions
        # for the deployed-state cross-check. Both functions are graceful-
        # degradation by design: ingest skips invalid manifests; reconciliation
        # catches all subprocess/auth/network failures and degrades affected
        # rows to _consistency='unknown' without affecting refresh_runs.status.
        # Per bridge/gtkb-dora-001b-track2-implementation-003.md sec 2.4-2.5
        # (Codex GO at -004).
        _ingest_canonical_pipeline_manifests(conn, project_root)
        _reconcile_against_azure_revisions(conn, ["staging", "production"])

        release = intelligence.get("release_readiness", {})
        conn.executemany(
            "INSERT INTO release_blockers (sort_order, blocker) VALUES (?, ?)",
            [(idx, blocker) for idx, blocker in enumerate(release.get("blockers", []), start=1)],
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
            [
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
                for idx, (key, details) in enumerate(integrations.items(), start=1)
            ],
        )

        conn.executemany(
            "INSERT INTO kpi_snapshots (generated_at, metric_key, metric_label, value, metric_group, lower_is_better) VALUES (?, ?, ?, ?, ?, ?)",
            _kpi_rows(history),
        )
        conn.executemany(
            "INSERT INTO current_metrics (metric_key, metric_label, value, status, description) VALUES (?, ?, ?, ?, ?)",
            _current_metric_rows(metrics, intelligence),
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

    azure_revisions: dict[str, list[dict[str, Any]]] = {}
    az_failure_logged = False
    for env in environments:
        try:
            # Map env to gateway container app name. Hardcoded here to avoid
            # importing scripts/lib/scaling_targets.py from the dashboard module
            # (separate concern); keep the mapping explicit.
            container_app = {
                "production": "agent-red-api-gateway",
                "staging": "agent-red-staging",
            }.get(env)
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
                    "Agent-Red",
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


def _current_metric_rows(metrics: dict[str, Any], intelligence: dict[str, Any]) -> list[tuple[Any, ...]]:
    release = intelligence.get("release_readiness", {})
    quality = intelligence.get("quality_rollup", {})
    return [
        (
            "project_health_issues",
            "Project Health Issues",
            _num(quality.get("failing", 0)) + _num(release.get("blocker_count", 0)),
            "red",
            "Failing checks plus release blockers.",
        ),
        (
            "release_blockers",
            "Release Blockers",
            release.get("blocker_count", metrics.get("regression", {}).get("release_blocker_count", 0)),
            "red",
            "Visible release blocker count.",
        ),
        (
            "ci_testing_failing",
            "CI / Testing Failing",
            quality.get("failing", 0),
            "red",
            "Failing integration/tool checks.",
        ),
        (
            "security_scan_posture",
            "Security Scan Posture",
            quality.get("ready_or_passing", 0),
            "green",
            "Ready or passing checks.",
        ),
        (
            "governance_bridge_items",
            "Governance Bridge Items",
            metrics.get("contention", {}).get("actionable_count", 0),
            "green",
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
    args = parser.parse_args(argv)

    if args.init_only:
        initialize_database(args.db_path)
        print(f"Initialized {args.db_path}")
        return 0

    result = refresh_database(args.db_path, args.project_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
