from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb import dashboard as refresh_dashboard_db
from groundtruth_kb import get_templates_dir
from groundtruth_kb.dashboard import refresh_database
from groundtruth_kb.dashboard_grafana import build_dashboard

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def isolate_optional_benchmark_consumer(monkeypatch):
    """This suite qualifies dashboard rendering, not the separately reviewed benchmark."""


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


def test_native_dashboard_model_reads_complete_pages_without_retaining_record_payloads(monkeypatch, tmp_path):
    from groundtruth_kb.authority_client import AuthorityClient

    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\nauthority_url = "http://127.0.0.1:8765"\n')
    calls = []

    def request(self, method, path, *, query=None):
        calls.append((method, path, query))
        assert method == "GET"
        if path == "/v1/bridge/state-report":
            return {
                "queues": {
                    role: {"role": role, "eligible": [{}] if role == "lo" else [], "blocked": []}
                    for role in ("pb", "lo")
                }
            }
        after = query["after"]
        if path == "/v1/work-items":
            if after is None:
                return {
                    "records": [{"id": "WI-1", "resolution_status": "open", "description": "PRIVATE-PAYLOAD"}],
                    "next_after": "WI-1",
                }
            assert after == "WI-1"
            return {"records": [{"id": "WI-2", "resolution_status": "resolved"}], "next_after": None}
        if path == "/v1/specifications":
            return {
                "records": [{"id": "SPEC-1", "status": "active"}, {"id": "SPEC-2", "status": "retired"}],
                "next_after": None,
            }
        assert path == "/v1/tests"
        return {"records": [{"id": "TEST-1", "status": "passed", "description": "PRIVATE-PAYLOAD"}], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    model = refresh_dashboard_db._build_dashboard_model(tmp_path)
    assert model["metrics"]["backlog"]["active_item_count"] == 1
    assert model["metrics"]["membase"]["open_work_items"] == 1
    assert model["metrics"]["specifications"]["current_total"] == 1
    assert model["metrics"]["tests"]["test_records"] == 1
    assert model["metrics"]["contention"]["actionable_count"] == 1
    assert model["dashboard_intelligence"]["quality_rollup"] == {}
    assert model.get("role") is None and model.get("current_work_subject") is None
    assert "PRIVATE-PAYLOAD" not in json.dumps(model)
    assert len(calls) == 5


def test_default_refresh_preserves_unknowns_and_history_without_startup_state(monkeypatch, tmp_path):
    monkeypatch.setattr(refresh_dashboard_db, "_write_bridge_swimlane_safe", lambda *args: None)
    # Missing configuration and a non-Git root are unavailable observations, not empty inventories.
    before = dict(os.environ)
    path = tmp_path / "dashboard.sqlite"
    refresh_database(path, tmp_path)
    refresh_database(path, tmp_path)
    assert dict(os.environ) == before
    with sqlite3.connect(path) as conn:
        metrics = {
            key: (value, status)
            for key, value, status in conn.execute("SELECT metric_key, value, status FROM current_metrics")
        }
        for key in (
            "project_health_issues",
            "release_blockers",
            "ci_testing_failing",
            "security_scan_posture",
            "governance_bridge_items",
            "dirty_worktree_paths",
        ):
            assert metrics[key] == (None, "yellow"), key
        assert conn.execute("SELECT COUNT(DISTINCT generated_at) FROM kpi_snapshots").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM kpi_snapshots WHERE value IS NOT NULL").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM quality_rollup").fetchone()[0] == 0
        cards = dict(conn.execute("SELECT label, value FROM health_cards"))
        assert cards["Project Health"] == "Unavailable"
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()) == [
        ".groundtruth/dashboard/dashboard-data.json",
        "dashboard.sqlite",
    ]
    landing = json.loads((tmp_path / ".groundtruth/dashboard/dashboard-data.json").read_text())
    assert landing["status"] == "unavailable"
    assert all(value is None for value in landing["metrics"].values())


@pytest.mark.parametrize(
    "page",
    [
        None,
        [],
        {"records": []},
        {"records": [], "next_after": "x"},
        {"records": [{"id": "a"}, {"id": "a"}], "next_after": None},
        {"records": [{"id": "b"}, {"id": "a"}], "next_after": None},
        {"records": [{"id": "a"}], "next_after": "b"},
        {"records": [{"id": True}], "next_after": None},
    ],
)
def test_native_dashboard_rejects_incomplete_or_invalid_inventory_pages(page):
    class Client:
        def request(self, *args, **kwargs):
            return page

    with pytest.raises(ValueError):
        refresh_dashboard_db._native_dashboard_records(Client(), "tests")


def test_native_dashboard_failure_discards_partial_counts_and_redacts_errors(monkeypatch, tmp_path):
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\nauthority_url="http://127.0.0.1:8765"\n')

    def request(self, method, path, *, query=None):
        if path == "/v1/work-items" and query["after"] is None:
            return {"records": [{"id": "WI-1", "resolution_status": "open"}], "next_after": "WI-1"}
        if path == "/v1/specifications":
            return {"records": [], "next_after": None}
        raise AuthorityClientError("authority_unavailable", "PRIVATE-ENDPOINT-DETAIL")

    monkeypatch.setattr(AuthorityClient, "request", request)
    model = refresh_dashboard_db._build_dashboard_model(tmp_path)
    assert model["metrics"]["backlog"]["active_item_count"] is None
    assert model["metrics"]["specifications"]["current_total"] == 0
    assert model["metrics"]["tests"]["test_records"] is None
    assert model["metrics"]["contention"]["actionable_count"] is None
    assert "PRIVATE-ENDPOINT-DETAIL" not in json.dumps(model)


def test_native_dashboard_counts_current_tracked_sources_and_baseline_only(tmp_path):
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    names = [
        "platform_tests/test_kept.py",
        "platform_tests/test_deleted.py",
        ".harness-baseline-configuration/skills/example/SKILL.md",
        ".harness-baseline-configuration/rules/example.md",
        ".harness-baseline-configuration/hooks/example.py",
        ".claude/rules/extra.md",
    ]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n")
    subprocess.run(["git", "add", "--", *names], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "platform_tests/test_deleted.py").unlink()
    model = refresh_dashboard_db._build_dashboard_model(tmp_path)
    assert model["metrics"]["tests"]["pytest_file_count"] == 1
    assert model["metrics"]["templates"] == {f"{kind}_template_count": 1 for kind in ("skill", "rule", "hook")}
    snapshot = refresh_dashboard_db._snapshot_from_model(model)
    assert all(snapshot[f"{kind}_template_count"] == 1 for kind in ("skill", "rule", "hook"))
    assert snapshot["tokens_consumed_before_user_input"] is None


def test_missing_metric_queries_reach_stat_panels_as_explicit_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(refresh_dashboard_db, "_write_bridge_swimlane_safe", lambda *args: None)
    db = tmp_path / "dashboard.sqlite"
    refresh_database(db, tmp_path)

    def walk(panels):
        for panel in panels:
            yield panel
            yield from walk(panel.get("panels", []))

    checked = []
    with sqlite3.connect(db) as connection:
        for panel in walk(build_dashboard()["panels"]):
            if panel["type"] != "stat":
                continue
            query = panel["targets"][0]["rawQueryText"]
            if "current_metrics" not in query:
                continue
            assert connection.execute(query).fetchone()[0] is None
            defaults = panel["fieldConfig"]["defaults"]
            assert defaults.get("noValue") == "Unavailable"
            nulls = [
                m["options"]["result"]
                for m in defaults.get("mappings", [])
                if m["type"] == "special" and m["options"]["match"] == "null"
            ]
            assert any(m["text"] == "Unavailable" and m["color"] == "yellow" for m in nulls)
            checked.append(panel["title"])
    assert {
        "Project Health Issues",
        "Release Blockers",
        "CI / Testing Failing",
        "Native Authority Findings",
        "MTTR",
    } <= set(checked)


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

    result = refresh_database(db_path=db_path, project_root=tmp_path, model=_sample_model(), history=history)

    assert result["status"] == "completed"
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs WHERE status = 'completed'").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM health_cards").fetchone()[0] >= 2
        assert conn.execute("SELECT COUNT(*) FROM action_center").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM kpi_snapshots").fetchone()[0] == len(
            refresh_dashboard_db.KPI_DEFINITIONS
        )
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
    from groundtruth_kb.dashboard import _metric_count_status

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

    refresh_database(db_path=db_path, project_root=tmp_path, model=model, history=history)

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
    model["dashboard_intelligence"]["health"] = [
        {"label": "Project Health", "value": "0 issues", "status": "green", "tooltip": "stale"},
        {"label": "Release Readiness", "value": "0 blockers", "status": "green", "tooltip": "stale"},
    ]
    model["dashboard_intelligence"]["release_health_findings"] = [
        {"source": "native-authority", "message": "native authority not ready", "severity": "red"},
        {"source": "bridge", "message": "bridge has live in-flight work", "severity": "yellow"},
        {"source": "readme-wiki", "message": "wiki page differs from source", "severity": "red"},
    ]

    refresh_database(db_path=db_path, project_root=tmp_path, model=model, history=[])

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
                    'native_authority_findings',
                    'bridge_actionability_findings',
                    'readme_wiki_drift'
                )
                """
            )
        }
        blockers = [row[0] for row in conn.execute("SELECT blocker FROM release_blockers ORDER BY sort_order")]
        health_cards = {
            row[0]: (row[1], row[2])
            for row in conn.execute(
                "SELECT label, value, status FROM health_cards WHERE label IN (?, ?)",
                (
                    "Project Health",
                    "Release Readiness",
                ),
            )
        }

    assert metrics == {
        "release_blockers": (3, "red"),
        "release_health_findings": (3, "red"),
        "native_authority_findings": (1, "red"),
        "bridge_actionability_findings": (1, "yellow"),
        "readme_wiki_drift": (1, "red"),
    }
    assert blockers == [
        "[native-authority] native authority not ready",
        "[bridge] bridge has live in-flight work",
        "[readme-wiki] wiki page differs from source",
    ]
    assert health_cards == {
        "Project Health": ("3 issues", "red"),
        "Release Readiness": ("3 blockers", "red"),
    }


def test_live_dirty_worktree_count_overrides_startup_model_count() -> None:
    rows = {
        row[0]: row
        for row in refresh_dashboard_db._current_metric_rows(
            {"drift": {"changed_path_count": 8}, "regression": {"release_blocker_count": 0}, "contention": {}},
            {"release_readiness": {"blockers": [], "blocker_count": 0}, "quality_rollup": {"failing": 0}},
            [
                {
                    "source": "git",
                    "message": "Live git dirty worktree path count: 305",
                    "severity": "red",
                    "metric_key": "dirty_worktree_paths",
                    "metric_value": 305,
                    "release_visible": False,
                }
            ],
        )
    }

    dirty = rows["dirty_worktree_paths"]

    assert dirty[2] == 305
    assert dirty[3] == "red"
    assert "live git status" in dirty[4]


def test_deferred_records_without_expiry_surface_release_health_warn(tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    model = _sample_model()
    model["dashboard_intelligence"]["release_readiness"] = {"blockers": [], "blocker_count": 0}
    model["dashboard_intelligence"]["quality_rollup"]["failing"] = 0
    model["dashboard_intelligence"]["deferred_items"] = [
        {"id": "INTAKE-NO-EXPIRY", "status": "deferred"},
        {"id": "INTAKE-BOUNDED", "status": "deferred", "resume_trigger": "after release branch cut"},
    ]

    refresh_database(db_path=db_path, project_root=tmp_path, model=model, history=[])

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
        project_root=tmp_path,
        model=_sample_model(),
        history=[],
    )
    assert calls == []

    monkeypatch.setenv("GTKB_DASHBOARD_AZURE_RECONCILE", "1")
    refresh_dashboard_db.refresh_database(
        db_path=tmp_path / "opt-in.sqlite",
        project_root=tmp_path,
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
    source_text = Path(refresh_dashboard_db.__file__).read_text(encoding="utf-8")
    assert "agent-red-api-gateway" not in source_text
    assert "agent-red-staging" not in source_text


def test_refresh_database_builds_native_model_and_supplied_models_need_no_native_read(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(
        refresh_dashboard_db, "_build_dashboard_model", lambda root, config=None: calls.append(root) or _sample_model()
    )
    monkeypatch.setattr(refresh_dashboard_db, "_write_bridge_swimlane_safe", lambda *args: None)
    refresh_database(tmp_path / "default.sqlite", tmp_path)
    refresh_database(tmp_path / "supplied.sqlite", tmp_path, model=_sample_model())
    assert calls == [tmp_path]


def test_installed_swimlane_writer_preserves_legacy_bridge_files(tmp_path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    legacy = bridge_dir / "sample-thread-001.md"
    legacy.write_text("VERIFIED\n\n# Sample\n", encoding="utf-8")
    before = legacy.read_bytes()
    refresh_dashboard_db._write_bridge_swimlane_safe(tmp_path)
    swimlane = tmp_path / ".groundtruth/dashboard/bridge-swimlane.json"
    data = json.loads(swimlane.read_text(encoding="utf-8"))
    assert data["status"] == "unavailable"
    assert data["summary"] is None and data["threads"] == []
    assert legacy.read_bytes() == before


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


def test_probe_live_uses_host_github_cli_auth_env_with_native_model(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "gtkb-dashboard.sqlite"
    original_gh_config = str(tmp_path / "host-gh-config")
    captured_env: dict[str, str | None] = {}

    def fake_github_status(project_root: Path) -> dict:
        captured_env["XDG_CONFIG_HOME"] = os.environ.get("XDG_CONFIG_HOME")
        captured_env["GH_CONFIG_DIR"] = os.environ.get("GH_CONFIG_DIR")
        return {
            "order": 1,
            "display_name": "GitHub Actions",
            "health": "green",
            "status": "passing",
            "latest_run_summary": "Python Tests: status=completed conclusion=success",
            "gate_role": "release gate",
            "remediation": "No action required.",
        }

    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("GH_CONFIG_DIR", original_gh_config)
    monkeypatch.setattr(refresh_dashboard_db, "_build_dashboard_model", lambda root, config=None: _sample_model())
    monkeypatch.setattr(refresh_dashboard_db, "_live_release_health_findings", lambda project_root, config=None: [])
    monkeypatch.setattr(refresh_dashboard_db, "_github_workflow_live_status", fake_github_status)
    monkeypatch.setattr(
        refresh_dashboard_db,
        "_native_authority_live_status",
        lambda project_root, config=None: {
            "order": 2,
            "display_name": "Native Authority",
            "health": "green",
            "status": "ready",
            "latest_run_summary": "healthy",
            "gate_role": "release infrastructure",
            "remediation": "No action required.",
        },
    )
    monkeypatch.setattr(refresh_dashboard_db, "_write_bridge_swimlane_safe", lambda *args: None)

    refresh_dashboard_db.refresh_database(db_path=db_path, project_root=tmp_path, probe_live=True)

    with sqlite3.connect(db_path) as conn:
        github_status = conn.execute("SELECT status FROM integration_status WHERE key = 'github'").fetchone()[0]

    assert captured_env == {"XDG_CONFIG_HOME": None, "GH_CONFIG_DIR": original_gh_config}
    assert github_status == "passing"


def test_probe_live_adds_native_authority_status_without_a_dispatcher(monkeypatch) -> None:
    from groundtruth_kb.authority_client import AuthorityClient
    from groundtruth_kb.config import GTConfig

    monkeypatch.setattr(refresh_dashboard_db, "_github_workflow_live_status", lambda root: {"status": "unavailable"})
    calls = []

    def read(self, method, route):
        calls.append((self.url, method, route))
        return {"ready": True, "reachable": True, "schema_catalog_matches": True}

    monkeypatch.setattr(AuthorityClient, "request", read)
    config = GTConfig(project_root=REPO_ROOT, authority_url="http://127.0.0.1:39899")
    rows = refresh_dashboard_db._integration_status_rows(
        {"dispatcher_supervisor": {"status": "stale"}}, REPO_ROOT, probe_live_workflows=True, config=config
    )
    by_key = {row[1]: row for row in rows}
    assert "dispatcher_supervisor" not in by_key
    assert by_key["native_authority"][3:5] == ("green", "ready")
    assert calls == [(config.authority_url, "GET", "/v1/status")]


def test_shortcuts_panel_uses_copy_path_link_title() -> None:
    dashboard = _load_generated_dashboard()
    flat = _walk_panels(dashboard["panels"])
    shortcuts = next(p for p in flat if p.get("title") == "Shortcuts")
    overrides = shortcuts["fieldConfig"]["overrides"]
    target_override = next(o for o in overrides if o["matcher"]["options"] == "target")
    link_title = target_override["properties"][0]["value"][0]["title"]
    assert link_title == "Copy path"


def test_grafana_provisioning_targets_sqlite_database(tmp_path) -> None:
    import yaml
    from groundtruth_kb.config import GTConfig

    config = GTConfig(project_root=tmp_path)
    paths = refresh_dashboard_db.resolve_dashboard_paths(config)
    refresh_dashboard_db.write_grafana_assets(paths, config)
    datasource = paths.provisioning_dir / "datasources/gtkb-dashboard-sqlite.yml"
    dashboard_provider = paths.provisioning_dir / "dashboards/gtkb-dashboard.yml"
    datasource_text = datasource.read_text(encoding="utf-8")
    dashboard_provider_text = dashboard_provider.read_text(encoding="utf-8")
    assert yaml.safe_load(datasource_text)["datasources"][0]["jsonData"]["path"] == paths.db_path.as_posix()
    assert yaml.safe_load(dashboard_provider_text)["providers"][0]["options"]["path"] == paths.dashboards_dir.as_posix()
    dashboard_json = build_dashboard()
    readme_text = (REPO_ROOT / "groundtruth-kb/README.md").read_text(encoding="utf-8")
    panel_titles = set(_panel_titles(dashboard_json["panels"]))

    assert "frser-sqlite-datasource" in datasource_text
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
    assert "Native Authority Findings" in panel_titles
    assert "Bridge Actionability Findings" in panel_titles
    assert "README / Wiki Drift" in panel_titles
    # GTKB-DORA-002: four-keys panels pinned in the generated dashboard JSON.
    assert "DORA Four Keys (Delivery Performance)" in panel_titles
    for _dora_title in ("Deployment Frequency", "Lead Time for Changes", "Change Failure Rate", "MTTR"):
        assert _dora_title in panel_titles

    def _flatten(panels: list[dict]) -> list[dict]:
        out: list[dict] = []
        for panel in panels:
            out.append(panel)
            out.extend(_flatten(panel.get("panels", [])))
        return out

    _panels_by_title = {panel["title"]: panel for panel in _flatten(dashboard_json["panels"])}
    _dora_metric_keys = {
        "Deployment Frequency": "dora_deployment_frequency",
        "Lead Time for Changes": "dora_lead_time_hours",
        "Change Failure Rate": "dora_change_failure_rate",
        "MTTR": "dora_mttr_hours",
    }
    for _title, _metric_key in _dora_metric_keys.items():
        _panel = _panels_by_title[_title]
        assert _panel["type"] == "stat"
        assert _panel["datasource"] == {"type": "frser-sqlite-datasource", "uid": "gtkb-dashboard-sqlite"}
        assert f"metric_key = '{_metric_key}'" in _panel["targets"][0]["rawQueryText"]
    assert "gt dashboard install" in readme_text
    assert "gt dashboard start" in readme_text
    assert "gt dashboard stop" in readme_text


def test_stat_panels_surface_per_panel_freshness_secondary_value() -> None:
    """GTKB-DASHBOARD-001 Â§C: each value-bearing stat panel must emit a
    `last_refreshed_at` secondary value (target `F`) sourced from refresh_runs.
    The Refresh Age panel itself is exempt â€” its primary value already is the
    freshness reading, so a second freshness target would be redundant."""
    dashboard_json = build_dashboard()

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
    index_text = (get_templates_dir() / "dashboard/index.html").read_text(encoding="utf-8")
    refresh_text = Path(refresh_dashboard_db.__file__).read_text(encoding="utf-8")

    assert "gtkb-dashboard-refresh" not in compose_text
    assert "container_name: gtkb-grafana" not in compose_text
    assert "docker compose up grafana" not in index_text
    assert "Docker Desktop" not in refresh_text
    assert "gt dashboard start" in index_text
    assert "Grafana OSS" in refresh_text


def _load_generated_dashboard() -> dict:
    return build_dashboard()


def _walk_panels(panels: list[dict]) -> list[dict]:
    out: list[dict] = []
    for panel in panels:
        out.append(panel)
        out.extend(_walk_panels(panel.get("panels", [])))
    return out


def test_retired_observability_panels_are_absent() -> None:
    dashboard = build_dashboard()
    assert "tafe" not in json.dumps(dashboard).lower()
    titles = _panel_titles(dashboard["panels"])
    assert "Native Authority Findings" in titles
    assert "Dispatcher Health Findings" not in titles
    assert "DORA Four Keys (Delivery Performance)" in titles


def test_current_panel_queries_are_read_only_and_use_the_derived_datasource() -> None:
    targets = [target for panel in _walk_panels(build_dashboard()["panels"]) for target in panel.get("targets", [])]
    assert targets
    for target in targets:
        assert target["datasource"]["uid"] == "gtkb-dashboard-sqlite"
        query = target["rawQueryText"].upper()
        assert query.startswith(("SELECT", "WITH"))
        assert all(verb not in query for verb in ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "CREATE "))


def test_panel_ids_are_monotonically_unique() -> None:
    ids = [panel["id"] for panel in _walk_panels(build_dashboard()["panels"]) if "id" in panel]
    assert ids and len(ids) == len(set(ids))


def test_alert_rules_do_not_reference_removed_observability() -> None:
    alerting_dir = get_templates_dir() / "dashboard/alerting"
    for alert_file in alerting_dir.glob("*.yaml"):
        assert "tafe" not in alert_file.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize(
    "key",
    [
        "dora_deployment_frequency",
        "dora_lead_time_hours",
        "dora_change_failure_rate",
        "dora_mttr_hours",
        "project_health_issues",
        "release_blockers",
        "ci_testing_failing",
        "governance_bridge_items",
        "release_health_findings",
        "dirty_worktree_paths",
        "native_authority_findings",
        "bridge_actionability_findings",
        "readme_wiki_drift",
    ],
)
def test_metric_query_selects_only_its_declared_metric(key):
    from groundtruth_kb.dashboard_grafana import _metric_query

    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE current_metrics(metric_key TEXT, value INTEGER)")
        connection.executemany("INSERT INTO current_metrics VALUES (?, ?)", [(key, 7), ("unrelated", 19)])
        assert connection.execute(_metric_query(key)).fetchall() == [(7,)]


@pytest.mark.parametrize(
    "key",
    [
        "",
        "unknown_metric",
        "release_blockers' OR 1=1 --",
        "release_blockers'; DROP TABLE current_metrics;--",
        None,
        42,
        [],
    ],
)
def test_metric_query_rejects_undeclared_keys_before_constructing_sql(key):
    from groundtruth_kb.dashboard_grafana import _metric_query

    with pytest.raises(ValueError, match="unsupported_dashboard_metric_key"):
        _metric_query(key)
