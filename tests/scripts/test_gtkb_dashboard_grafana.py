from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from scripts.gtkb_dashboard.refresh_dashboard_db import refresh_database

REPO_ROOT = Path(__file__).resolve().parents[2]


def _panel_titles(panels: list[dict]) -> list[str]:
    titles: list[str] = []
    for panel in panels:
        titles.append(panel["title"])
        titles.extend(_panel_titles(panel.get("panels", [])))
    return titles


def _sample_model() -> dict:
    return {
        "generated_at": "2026-04-21T12:00:00+00:00",
        "role": {"assumed_role": "Prime Builder"},
        "dashboard_requirements": {"scope_note": "Agent Red product/project dashboard."},
        "metrics": {
            "contention": {"actionable_count": 0},
            "drift": {"changed_path_count": 1},
            "regression": {"release_blocker_count": 2},
        },
        "dashboard_intelligence": {
            "health": [{"label": "Project Health", "value": "2 issues", "status": "red", "tooltip": "sample"}],
            "shortcuts": [{"label": "Open GitHub Actions", "target": "https://github.com/actions", "kind": "external"}],
            "action_center": [
                {
                    "action": "Repair CI",
                    "owner_lane": "Prime Builder",
                    "why": "failing workflow",
                    "remediation": "open failing workflow",
                    "shortcut": {"label": "Open", "target": "https://github.com/actions", "kind": "external"},
                    "source": "Testing",
                    "severity": "red",
                }
            ],
            "release_readiness": {"blockers": ["Resolve release blocker"], "blocker_count": 1},
            "quality_rollup": {"total": 2, "failing": 1, "manual": 0, "unknown": 0, "ready_or_passing": 1},
            "risk_register": [
                {
                    "risk": "Credential lifecycle",
                    "evidence": "release readiness",
                    "impact": "blocks release",
                    "remediation": "owner-managed decision",
                    "owner": "Owner",
                    "severity": "red",
                }
            ],
            "data_freshness": {
                "generated_at": "2026-04-21T12:00:00+00:00",
                "repo_branch": "develop",
                "repo_short_sha": "abc1234",
                "scope_version": "agent_red_v1",
                "sources": ["git", "local"],
            },
        },
        "infrastructure": {
            "delivery_timeline": {
                "stage_summary": [
                    {
                        "stage": "build",
                        "label": "Build",
                        "count": 1,
                        "latest_result": "success",
                        "latest_version": "v1.0.0",
                        "status": "green",
                    }
                ],
                "timeline": [
                    {
                        "stage": "build",
                        "stage_label": "Build",
                        "event": "Build container",
                        "timestamp": "2026-04-21T12:00:00+00:00",
                        "version": "v1.0.0",
                        "commit": "abc1234",
                        "branch": "develop",
                        "result": "success",
                        "result_color": "green",
                        "test_results": "passed",
                        "source": "local",
                    }
                ],
            },
            "testing_service_integrations": {
                "github": {
                    "order": 1,
                    "display_name": "GitHub Actions",
                    "health": "red",
                    "status": "failing",
                    "latest_run_summary": "sample failure",
                    "gate_role": "release gate",
                    "remediation": "repair workflow",
                }
            },
        },
    }


def test_refresh_database_populates_grafana_sqlite_tables(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    history = [
        {
            "generated_at": "2026-04-21T12:00:00+00:00",
            "backlog_active_items": 3,
            "membase_open_work_items": 29,
            "deliberation_archive_current_total": 324,
            "pytest_file_count": 338,
            "specification_current_total": 1847,
            "drift_changed_path_count": 1,
            "regression_release_blocker_count": 2,
            "contention_actionable_bridge_count": 0,
        }
    ]

    result = refresh_database(db_path=db_path, project_root=REPO_ROOT, model=_sample_model(), history=history)

    assert result["status"] == "completed"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs WHERE status = 'completed'").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM health_cards").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM action_center").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM kpi_snapshots").fetchone()[0] == 8
        assert conn.execute("SELECT COUNT(*) FROM setup_steps").fetchone()[0] >= 6
        assert conn.execute("SELECT COUNT(*) FROM required_tools").fetchone()[0] >= 8
        assert conn.execute("SELECT COUNT(*) FROM third_party_services").fetchone()[0] >= 10
        service_names = {row[0] for row in conn.execute("SELECT name FROM third_party_services")}
        assert {"GitHub Actions", "Azure OpenAI", "Shopify Partners", "Stripe"} <= service_names


def test_grafana_provisioning_targets_sqlite_database() -> None:
    datasource = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "datasources" / "gtkb-dashboard-sqlite.yml"
    dashboard_provider = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "dashboards" / "gtkb-dashboard.yml"
    dashboard = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json"
    readme = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "README.md"
    package_integration = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "PACKAGE-INTEGRATION.md"

    datasource_text = datasource.read_text(encoding="utf-8")
    dashboard_provider_text = dashboard_provider.read_text(encoding="utf-8")
    dashboard_json = json.loads(dashboard.read_text(encoding="utf-8"))
    readme_text = readme.read_text(encoding="utf-8")
    package_integration_text = package_integration.read_text(encoding="utf-8")
    panel_titles = set(_panel_titles(dashboard_json["panels"]))

    assert "frser-sqlite-datasource" in datasource_text
    assert "$GTKB_DASHBOARD_SQLITE_PATH" in datasource_text
    assert "$GTKB_DASHBOARD_DASHBOARDS_PATH" in dashboard_provider_text
    assert dashboard_json["uid"] == "agent-red-gtkb"
    assert dashboard_json["links"] == []
    assert [panel["title"] for panel in dashboard_json["panels"][:10]] == [
        "GT-KB Dashboard",
        "Project Health Issues",
        "Release Blockers",
        "CI / Testing Failing",
        "Governance Bridge Items",
        "Refresh Age",
        "Documented Setup Steps",
        "Health Signals",
        "Action Severity Mix",
        "Delivery Events By Stage",
    ]
    assert [panel["type"] for panel in dashboard_json["panels"][1:13]] == [
        "stat",
        "stat",
        "stat",
        "stat",
        "stat",
        "stat",
        "bargauge",
        "piechart",
        "bargauge",
        "bargauge",
        "bargauge",
        "timeseries",
    ]
    assert all(
        panel.get("collapsed") is True
        for panel in dashboard_json["panels"]
        if panel["title"] in {
            "Setup Details",
            "Action Center Details",
            "Delivery Timeline Details",
            "KPI History Details",
            "Integration Status Details",
            "Data Freshness Details",
        }
    )
    assert "Step-by-Step Setup" in panel_titles
    assert "Required Tools, CLIs, and SDKs" in panel_titles
    assert "Third-Party Test Services" in panel_titles
    assert "start_local_dashboard.ps1" in readme_text
    assert "docker compose" not in readme_text.lower()
    assert "gtkb dashboard install" in package_integration_text
    assert "gtkb dashboard start" in package_integration_text
    assert "Docker Desktop" in package_integration_text


def test_dashboard_launch_path_does_not_require_docker_desktop() -> None:
    compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    index_text = (REPO_ROOT / "docs" / "gtkb-dashboard" / "index.html").read_text(encoding="utf-8")
    refresh_text = (REPO_ROOT / "scripts" / "gtkb_dashboard" / "refresh_dashboard_db.py").read_text(encoding="utf-8")

    assert "gtkb-dashboard-refresh" not in compose_text
    assert "container_name: gtkb-grafana" not in compose_text
    assert "docker compose up grafana" not in index_text
    assert "Docker Desktop" not in refresh_text
    assert "start_local_dashboard.ps1" in index_text
    assert "Grafana OSS" in refresh_text
