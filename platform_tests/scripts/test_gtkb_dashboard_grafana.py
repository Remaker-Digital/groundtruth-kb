from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
from pathlib import Path

from scripts.gtkb_dashboard import refresh_dashboard_db
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
        assert conn.execute("SELECT COUNT(*) FROM third_party_services").fetchone()[0] >= 8
        assert conn.execute("SELECT COUNT(*) FROM application_deployment_signals").fetchone()[0] == 6
        service_names = {row[0] for row in conn.execute("SELECT name FROM third_party_services")}
        deployment_surfaces = {row[0] for row in conn.execute("SELECT surface FROM application_deployment_signals")}
        assert {
            "GitHub Actions",
            "Application deployment connector",
            "Application security connector",
            "Application observability connector",
        } <= service_names
        assert {
            "Deployment topology",
            "Containers",
            "Security",
            "Throughput and latency",
            "Defects",
            "Infrastructure health",
        } == deployment_surfaces


def test_metric_count_status_helpers() -> None:
    from scripts.gtkb_dashboard.refresh_dashboard_db import _metric_count_status

    assert _metric_count_status(0) == "green"
    assert _metric_count_status(2) == "red"
    assert _metric_count_status("bad") == "yellow"


def test_current_metric_statuses_green_when_sources_clean(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    model = _sample_model()
    model["dashboard_intelligence"]["release_readiness"] = {"blockers": [], "blocker_count": 0}
    model["dashboard_intelligence"]["quality_rollup"]["failing"] = 0
    model["current_work_subject"] = "Demo Application"
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
    assert "Demo Application" in metadata["dashboard_subject_scope"]
    assert metadata.get("refresh_service_scope", "").startswith("loopback")


def test_release_health_findings_make_release_readiness_non_green(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    model = _sample_model()
    model["dashboard_intelligence"]["release_readiness"] = {"blockers": [], "blocker_count": 0}
    model["dashboard_intelligence"]["quality_rollup"]["failing"] = 0
    model["dashboard_intelligence"]["release_health_findings"] = [
        {"source": "dispatcher", "message": "dispatch health WARN", "severity": "red"},
        {"source": "bridge", "message": "bridge has live in-flight work", "severity": "yellow"},
        {"source": "readme-wiki", "message": "wiki page differs from source", "severity": "red"},
    ]

    refresh_database(db_path=db_path, project_root=REPO_ROOT, model=model, history=[])

    with sqlite3.connect(db_path) as conn:
        metrics = {
            row[0]: (row[1], row[2])
            for row in conn.execute(
                """
                SELECT metric_key, value, status
                FROM current_metrics
                WHERE metric_key IN (
                    'release_blockers',
                    'release_health_findings',
                    'dispatcher_health_findings',
                    'bridge_actionability_findings',
                    'readme_wiki_drift'
                )
                """
            )
        }
        blockers = [row[0] for row in conn.execute("SELECT blocker FROM release_blockers ORDER BY sort_order")]

    assert metrics == {
        "release_blockers": (3, "red"),
        "release_health_findings": (3, "red"),
        "dispatcher_health_findings": (1, "red"),
        "bridge_actionability_findings": (1, "yellow"),
        "readme_wiki_drift": (1, "red"),
    }
    assert blockers == [
        "[dispatcher] dispatch health WARN",
        "[bridge] bridge has live in-flight work",
        "[readme-wiki] wiki page differs from source",
    ]


def test_deferred_records_without_expiry_surface_release_health_warn(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    model = _sample_model()
    model["dashboard_intelligence"]["release_readiness"] = {"blockers": [], "blocker_count": 0}
    model["dashboard_intelligence"]["quality_rollup"]["failing"] = 0
    model["dashboard_intelligence"]["deferred_items"] = [
        {"id": "INTAKE-NO-EXPIRY", "status": "deferred"},
        {"id": "INTAKE-BOUNDED", "status": "deferred", "resume_trigger": "after release branch cut"},
    ]

    refresh_database(db_path=db_path, project_root=REPO_ROOT, model=model, history=[])

    with sqlite3.connect(db_path) as conn:
        metrics = {
            row[0]: (row[1], row[2])
            for row in conn.execute(
                """
                SELECT metric_key, value, status
                FROM current_metrics
                WHERE metric_key IN ('release_blockers', 'release_health_findings')
                """
            )
        }
        blockers = [row[0] for row in conn.execute("SELECT blocker FROM release_blockers ORDER BY sort_order")]

    assert metrics == {
        "release_blockers": (1, "yellow"),
        "release_health_findings": (1, "yellow"),
    }
    assert blockers == [
        "[deferral-expiry] 1 deferred record(s) lack an expiry, time limit, or resume trigger: INTAKE-NO-EXPIRY"
    ]


def test_azure_reconciliation_is_explicit_opt_in(monkeypatch, tmp_path) -> None:
    calls: list[tuple[object, list[str]]] = []

    def fake_reconcile(conn: object, environments: list[str]) -> dict[str, int]:
        calls.append((conn, environments))
        return {"rows_checked": 0, "rows_matched": 0, "rows_drift": 0, "rows_unknown": 0}

    monkeypatch.setattr(refresh_dashboard_db, "_reconcile_against_azure_revisions", fake_reconcile)
    monkeypatch.delenv("GTKB_DASHBOARD_AZURE_RECONCILE", raising=False)

    refresh_dashboard_db.refresh_database(
        db_path=tmp_path / "default.sqlite",
        project_root=REPO_ROOT,
        model=_sample_model(),
        history=[],
    )
    assert calls == []

    monkeypatch.setenv("GTKB_DASHBOARD_AZURE_RECONCILE", "1")
    refresh_dashboard_db.refresh_database(
        db_path=tmp_path / "opt-in.sqlite",
        project_root=REPO_ROOT,
        model=_sample_model(),
        history=[],
    )
    assert len(calls) == 1
    assert calls[0][1] == ["staging", "production"]


def test_azure_reconciliation_requires_application_supplied_container_app_map(monkeypatch) -> None:
    monkeypatch.delenv("GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP", raising=False)

    assert refresh_dashboard_db._azure_container_app_map(["staging", "production"]) == {}

    monkeypatch.setenv(
        "GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP",
        json.dumps({"staging": "demo-staging", "production": "demo-production", "dev": "ignored"}),
    )

    assert refresh_dashboard_db._azure_container_app_map(["staging", "production"]) == {
        "production": "demo-production",
        "staging": "demo-staging",
    }
    source_text = (REPO_ROOT / "scripts" / "gtkb_dashboard" / "refresh_dashboard_db.py").read_text(encoding="utf-8")
    assert "agent-red-api-gateway" not in source_text
    assert "agent-red-staging" not in source_text


def test_refresh_database_uses_fast_startup_model_by_default(monkeypatch, tmp_path) -> None:
    fast_hook_values: list[bool] = []

    class FakeSessionModule:
        def build_startup_model(self, project_root: Path, *, fast_hook: bool = False) -> dict:
            fast_hook_values.append(fast_hook)
            return _sample_model()

        def _snapshot_from_model(self, model: dict) -> dict:
            return {"generated_at": model["generated_at"]}

    monkeypatch.setattr(refresh_dashboard_db, "_load_session_module", lambda: FakeSessionModule())
    monkeypatch.setattr(refresh_dashboard_db, "_write_model_to_db", lambda *args, **kwargs: None)
    monkeypatch.setattr(refresh_dashboard_db, "_write_bridge_swimlane_safe", lambda project_root: None)
    monkeypatch.setattr(refresh_dashboard_db, "_refresh_tafe_projection_safe", lambda db_path, project_root: None)

    refresh_dashboard_db.refresh_database(db_path=tmp_path / "default.sqlite", project_root=REPO_ROOT)
    refresh_dashboard_db.refresh_database(
        db_path=tmp_path / "full.sqlite",
        project_root=REPO_ROOT,
        fast_startup_model=False,
    )

    assert fast_hook_values == [True, False]


def test_direct_script_swimlane_writer_uses_absolute_import_fallback(tmp_path) -> None:
    module_path = REPO_ROOT / "scripts" / "gtkb_dashboard" / "refresh_dashboard_db.py"
    spec = importlib.util.spec_from_file_location("refresh_dashboard_db_direct_script", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "sample-thread-001.md").write_text("VERIFIED\n\n# Sample\n", encoding="utf-8")

    module._write_bridge_swimlane_safe(tmp_path)

    swimlane = tmp_path / "docs" / "gtkb-dashboard" / "bridge-swimlane.json"
    assert swimlane.is_file()
    data = json.loads(swimlane.read_text(encoding="utf-8"))
    assert data["summary"]["thread_count"] == 1
    assert data["threads"][0]["document"] == "sample-thread"


def test_github_workflow_live_status_classifies_success(monkeypatch) -> None:
    def fake_probe(project_root: Path, args: list[str], *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
        assert args[:3] == ["gh", "run", "list"]
        assert "Remaker-Digital/groundtruth-kb" in args
        assert "main" in args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "workflowName": "Python Tests",
                        "status": "completed",
                        "conclusion": "success",
                        "createdAt": "2026-06-30T16:00:00Z",
                    }
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(refresh_dashboard_db, "_run_release_probe", fake_probe)

    status = refresh_dashboard_db._github_workflow_live_status(REPO_ROOT)

    assert status["health"] == "green"
    assert status["status"] == "passing"
    assert "Python Tests" in status["latest_run_summary"]


def test_github_workflow_live_status_classifies_unavailable(monkeypatch) -> None:
    def fake_probe(project_root: Path, args: list[str], *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="gh auth required")

    monkeypatch.setattr(refresh_dashboard_db, "_run_release_probe", fake_probe)

    status = refresh_dashboard_db._github_workflow_live_status(REPO_ROOT)

    assert status["health"] == "yellow"
    assert status["status"] == "live_state_unavailable"
    assert "gh auth required" in status["latest_run_summary"]


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
    assert dashboard_json["uid"] == "groundtruth-kb-dashboard"
    assert dashboard_json["title"] == "GT-KB Operations Dashboard"
    assert dashboard_json["tags"] == ["gt-kb", "operations", "sqlite"]
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
    assert "Application Deployment" in panel_titles
    assert "Application Deployment Health" in panel_titles
    assert "Application Deployment Signals" in panel_titles
    assert "Release Health Findings" in panel_titles
    assert "Dirty Worktree Paths" in panel_titles
    assert "Dispatcher Health Findings" in panel_titles
    assert "Bridge Actionability Findings" in panel_titles
    assert "README / Wiki Drift" in panel_titles
    assert "start_local_dashboard.ps1" in readme_text
    assert "scripts/update_wiki_pages.py compare" in readme_text
    assert "--check" not in readme_text
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
