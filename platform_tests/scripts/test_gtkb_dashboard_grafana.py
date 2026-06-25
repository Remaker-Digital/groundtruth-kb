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
        "dashboard_requirements": {"scope_note": "GroundTruth-KB project dashboard."},
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
                "scope_version": "gtkb_v1",
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


def test_metric_count_status_helpers() -> None:
    from scripts.gtkb_dashboard.refresh_dashboard_db import _metric_count_status

    assert _metric_count_status(0) == "green"
    assert _metric_count_status(2) == "red"
    assert _metric_count_status("bad") == "yellow"


def test_current_metric_statuses_green_when_sources_clean(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    model = _sample_model()
    model["dashboard_intelligence"]["release_readiness"]["blocker_count"] = 0
    model["dashboard_intelligence"]["quality_rollup"]["failing"] = 0
    model["current_work_subject"] = "Agent Red"
    history = [
        {
            "generated_at": "2026-04-21T12:00:00+00:00",
            "backlog_active_items": 0,
            "membase_open_work_items": 0,
            "deliberation_archive_current_total": 0,
            "pytest_file_count": 0,
            "specification_current_total": 0,
            "drift_changed_path_count": 0,
            "regression_release_blocker_count": 0,
            "contention_actionable_bridge_count": 0,
        }
    ]

    refresh_database(db_path=db_path, project_root=REPO_ROOT, model=model, history=history)

    with sqlite3.connect(db_path) as conn:
        statuses = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT metric_key, status FROM current_metrics WHERE metric_key IN (?, ?, ?)",
                (
                    "project_health_issues",
                    "release_blockers",
                    "ci_testing_failing",
                ),
            )
        }
        metadata = dict(conn.execute("SELECT key, value FROM dashboard_metadata"))

    assert statuses == {
        "project_health_issues": "green",
        "release_blockers": "green",
        "ci_testing_failing": "green",
    }
    assert "dashboard_subject_scope" in metadata
    assert "Combined operations" in metadata["dashboard_subject_scope"]
    assert "Agent Red" in metadata["dashboard_subject_scope"]
    assert metadata.get("refresh_service_scope", "").startswith("loopback")


def test_shortcuts_panel_uses_copy_path_link_title() -> None:
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    shortcuts = next(p for p in flat if p.get("title") == "Shortcuts")
    overrides = shortcuts["fieldConfig"]["overrides"]
    target_override = next(o for o in overrides if o["matcher"]["options"] == "target")
    link_title = target_override["properties"][0]["value"][0]["title"]
    assert link_title == "Copy path"


def test_grafana_provisioning_targets_sqlite_database() -> None:
    datasource = (
        REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "datasources" / "gtkb-dashboard-sqlite.yml"
    )
    dashboard_provider = (
        REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "dashboards" / "gtkb-dashboard.yml"
    )
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
    # Drift cleanup: the generator hard-codes "agent-red-gtkb" in
    # build_dashboard(); the previously committed JSON had "gtkb", a stale
    # artifact from before the generator change. The idempotent WI-4506 regen
    # surfaced the drift; updating the assertion to match the SoT (the
    # generator) is in scope of WI-4506's target_paths (this test file is
    # listed) and is a one-line drift cleanup, not a scope expansion.
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
        if panel["title"]
        in {
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


def test_stat_panels_surface_per_panel_freshness_secondary_value() -> None:
    """GTKB-DASHBOARD-001 §C: each value-bearing stat panel must emit a
    `last_refreshed_at` secondary value (target `F`) sourced from refresh_runs.
    The Refresh Age panel itself is exempt — its primary value already is the
    freshness reading, so a second freshness target would be redundant."""
    dashboard = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json"
    dashboard_json = json.loads(dashboard.read_text(encoding="utf-8"))

    def _all_panels(panels: list[dict]) -> list[dict]:
        out: list[dict] = []
        for p in panels:
            out.append(p)
            out.extend(_all_panels(p.get("panels", [])))
        return out

    stat_panels = [p for p in _all_panels(dashboard_json["panels"]) if p.get("type") == "stat"]
    assert stat_panels, "generator must produce at least one stat panel"

    freshness_sql_marker = "FROM refresh_runs"
    freshness_refid = "F"

    for panel in stat_panels:
        title = panel["title"]
        targets = panel.get("targets", [])
        if title == "Refresh Age":
            # Refresh Age exemption: primary value already IS the freshness reading.
            assert all(t.get("refId") != freshness_refid for t in targets), (
                "Refresh Age panel must not carry a secondary F target; primary is already the freshness value"
            )
            continue
        freshness_targets = [t for t in targets if t.get("refId") == freshness_refid]
        assert freshness_targets, f"stat panel {title!r} is missing a freshness secondary target"
        ft = freshness_targets[0]
        assert freshness_sql_marker in ft["rawQueryText"], (
            f"stat panel {title!r} freshness target must query refresh_runs, got: {ft['rawQueryText']!r}"
        )
        # Panel must also expose a description explaining the freshness anchor so
        # reviewers can see where the timestamp comes from without reading JSON.
        description = panel.get("description", "")
        assert "refresh_runs" in description and "Freshness" in description, (
            f"stat panel {title!r} must describe its freshness anchor in `description`; got: {description!r}"
        )


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


# =============================================================================
# WI-4506: TAFE Observability panel assertions on the generated dashboard.
# =============================================================================

_TAFE_PANEL_TITLES: tuple[str, ...] = (
    "Stage Attempt Outcomes (TAFE)",
    "Failure Class Distribution (TAFE)",
    "Active Flow Instances (TAFE)",
    "Active Stage Leases (TAFE)",
    "Capability Snapshot Readiness by Role (TAFE)",
)

_TAFE_PROJECTION_TABLES: tuple[str, ...] = (
    "tafe_stage_attempt_telemetry",
    "tafe_flow_instances",
    "tafe_stage_instances",
    "tafe_stage_leases",
    "tafe_agent_capability_snapshots",
)


def _load_generated_dashboard() -> dict:
    dashboard_path = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json"
    return json.loads(dashboard_path.read_text(encoding="utf-8"))


def _walk_panels(panels: list[dict]) -> list[dict]:
    """Flat list of all panels in the dashboard, recursively through rows."""
    out: list[dict] = []
    for panel in panels:
        out.append(panel)
        out.extend(_walk_panels(panel.get("panels", [])))
    return out


def test_tafe_observability_row_exists() -> None:
    dashboard = _load_generated_dashboard()
    titles = _panel_titles(dashboard["panels"])
    assert "TAFE Observability" in titles, "TAFE Observability row missing from generated dashboard"


def test_all_tafe_panel_titles_present() -> None:
    dashboard = _load_generated_dashboard()
    titles = set(_panel_titles(dashboard["panels"]))
    for title in _TAFE_PANEL_TITLES:
        assert title in titles, f"TAFE panel {title!r} missing from generated dashboard"


def test_tafe_panels_use_sqlite_datasource() -> None:
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    tafe_panels = [p for p in flat if p.get("title") in _TAFE_PANEL_TITLES]
    assert len(tafe_panels) == len(_TAFE_PANEL_TITLES), "Expected all TAFE panels to be present"
    for panel in tafe_panels:
        for target in panel.get("targets", []):
            ds = target.get("datasource", {})
            assert ds.get("uid") == "gtkb-dashboard-sqlite", (
                f"TAFE panel {panel['title']!r} uses non-SQLite datasource: {ds}"
            )


def test_tafe_panel_queries_are_read_only() -> None:
    """No TAFE panel query may issue a write (INSERT/UPDATE/DELETE/DROP/CREATE)."""
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    forbidden = ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "CREATE ")
    for panel in flat:
        if panel.get("title") not in _TAFE_PANEL_TITLES:
            continue
        for target in panel.get("targets", []):
            sql_upper = target.get("rawQueryText", "").upper()
            for verb in forbidden:
                assert verb not in sql_upper, (
                    f"TAFE panel {panel['title']!r} contains forbidden SQL verb {verb!r}: {sql_upper!r}"
                )


def test_tafe_panel_queries_reference_projection_tables() -> None:
    """Each TAFE panel's query must read from one of the projection tables, not
    from any canonical `groundtruth.db` table name. The dashboard datasource
    points at the dashboard SQLite, so a canonical-table reference would be a
    silent miss."""
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    for panel in flat:
        if panel.get("title") not in _TAFE_PANEL_TITLES:
            continue
        for target in panel.get("targets", []):
            sql = target.get("rawQueryText", "")
            assert any(table in sql for table in _TAFE_PROJECTION_TABLES), (
                f"TAFE panel {panel['title']!r} references no projection table; SQL: {sql!r}"
            )


def test_panel_ids_are_monotonically_unique() -> None:
    """Adding the TAFE row + 5 panels must not collide with existing panel IDs."""
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    ids = [p.get("id") for p in flat if "id" in p]
    assert len(ids) == len(set(ids)), f"duplicate panel IDs found: {sorted(ids)}"


def test_no_alert_rule_references_a_tafe_panel() -> None:
    """The WI-4506 PAUTH forbids alert-rule scope creep. No alert rule may
    reference a TAFE panel by id or by title."""
    alerting_dir = REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "provisioning" / "alerting"
    if not alerting_dir.exists():
        return
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    tafe_panel_ids = {str(p.get("id")) for p in flat if p.get("title") in _TAFE_PANEL_TITLES}

    for alert_file in alerting_dir.glob("*.yaml"):
        text = alert_file.read_text(encoding="utf-8")
        for title in _TAFE_PANEL_TITLES:
            assert title not in text, f"alert file {alert_file.name} references TAFE panel title {title!r}"
        for panel_id in tafe_panel_ids:
            # Match panelId: NN exactly (alert-rule schema field).
            assert f"panelId: {panel_id}" not in text, (
                f"alert file {alert_file.name} references TAFE panel id {panel_id}"
            )
