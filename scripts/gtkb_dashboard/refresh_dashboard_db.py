#!/usr/bin/env python3
"""Refresh the GT-KB Grafana dashboard SQLite database."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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


def refresh_database(
    db_path: Path = DEFAULT_DB_PATH,
    project_root: Path = PROJECT_ROOT,
    model: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(UTC).isoformat()
    initialize_database(db_path)
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
        _write_model_to_db(db_path, model, history)
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


def _append_snapshot(history: list[dict[str, Any]], snapshot: dict[str, Any], max_history: int = 200) -> list[dict[str, Any]]:
    filtered = [row for row in history if row.get("generated_at") != snapshot.get("generated_at")]
    filtered.append(snapshot)
    return filtered[-max_history:]


def _write_model_to_db(db_path: Path, model: dict[str, Any], history: list[dict[str, Any]]) -> None:
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
                (idx, item.get("label", ""), str(item.get("value", "")), item.get("status", ""), item.get("tooltip", ""))
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
        conn.executemany(
            """
            INSERT INTO delivery_timeline_events
            (sort_order, stage, stage_label, event, timestamp, date_label, version, commit_sha, branch,
             result, result_color, test_results, source, url, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                )
                for idx, item in enumerate(ordered_events, start=1)
            ],
        )

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
        ("project_health_issues", "Project Health Issues", _num(quality.get("failing", 0)) + _num(release.get("blocker_count", 0)), "red", "Failing checks plus release blockers."),
        ("release_blockers", "Release Blockers", release.get("blocker_count", metrics.get("regression", {}).get("release_blocker_count", 0)), "red", "Visible release blocker count."),
        ("ci_testing_failing", "CI / Testing Failing", quality.get("failing", 0), "red", "Failing integration/tool checks."),
        ("security_scan_posture", "Security Scan Posture", quality.get("ready_or_passing", 0), "green", "Ready or passing checks."),
        ("governance_bridge_items", "Governance Bridge Items", metrics.get("contention", {}).get("actionable_count", 0), "green", "Actionable bridge/contention entries."),
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
