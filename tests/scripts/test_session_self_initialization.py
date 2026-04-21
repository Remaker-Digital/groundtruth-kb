"""Tests for fresh-session self-initialization dashboard/report generation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_self_initialization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("session_self_initialization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization"] = module
    spec.loader.exec_module(module)
    return module


def test_startup_model_contains_role_governance_and_kpi_inventory() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT)

    assert model["role"]["assumed_role"] == "Prime Builder"
    assert model["role"]["role_assignment"] == "active AI harness assigned by owner until further notice"
    assert "Strict GOV enforcement" in model["governance_stance"][0]
    assert "Formal artifact approval" in " ".join(model["governance_stance"])
    assert model["skills"]["count"] > 0
    assert "prime-builder-role.md" in model["role"]["role_mapping_source"]
    assert "formal-artifact-approval-gate.py" in model["directives"]["hook_files"]
    assert model["dashboard_requirements"]["scope_version"] == "agent_red_v1"
    assert "GT-KB is treated as pre-existing" in model["dashboard_requirements"]["scope_note"]
    assert model["metrics"]["specifications"]["raw_current_total"] >= model["metrics"]["specifications"]["current_total"]
    assert "gtkb_framework" in model["metrics"]["specifications"]["scope_counts"]
    posture = model["infrastructure"]["gtkb_upgrade_posture"]
    assert posture["scope"] == "implementation_infrastructure"
    assert posture["package_version"]
    assert posture["scaffold_version"] == "0.6.1"
    assert posture["repo_url"] == "https://github.com/Remaker-Digital/groundtruth-kb"
    assert posture["latest_release_tag"]
    assert posture["plan_command"]
    assert posture["apply_enabled"] is False
    assert posture["upgrade_plan"]["available"] is True
    integrations = model["infrastructure"]["testing_service_integrations"]
    github = integrations["github"]
    assert github["scope"] == "implementation_infrastructure"
    assert github["remote_host"] in {"github.com", "unknown", None}
    assert github["workflow_count"] >= 1
    assert github["python_tests_workflow"] is True
    assert github["release_candidate_gate_workflow"] is True
    assert github["health"]
    assert integrations["sonarcloud"]["status"] == "ready"
    assert integrations["semgrep_sast"]["status"] == "ready"
    assert integrations["bandit"]["status"] == "ready"
    assert integrations["pip_audit"]["status"] == "ready"
    assert integrations["docker_scout"]["status"] == "ready"
    assert integrations["accessibility_axe"]["status"] == "ready"
    assert integrations["chromatic"]["status"] == "ready"
    assert integrations["docs_quality"]["status"] == "ready"
    assert integrations["openapi_compatibility"]["status"] == "ready"
    assert integrations["dependabot"]["status"] == "ready"
    assert integrations["locust_performance"]["status"] == "manual"
    assert integrations["mutation_testing"]["status"] == "manual"
    assert integrations["contract_testing"]["status"] == "manual"
    assert integrations["schemathesis_api"]["status"] == "manual"
    assert all(item["remediation"] for item in integrations.values())
    assert all(item["remediation"] for item in integrations.values() if item["health"] == "failing")
    delivery_timeline = model["infrastructure"]["delivery_timeline"]
    assert delivery_timeline["timeline"]
    assert delivery_timeline["stage_summary"]
    assert delivery_timeline["version_manifest"]["display"]
    assert {item["stage"] for item in delivery_timeline["stage_summary"]} >= {
        "commit",
        "build",
        "test",
        "staging_deployment",
        "production_deployment",
    }
    timeline_stages = {item["stage"] for item in delivery_timeline["timeline"]}
    assert "commit" in timeline_stages
    assert "build" in timeline_stages
    assert "staging_deployment" in timeline_stages
    assert "production_deployment" in timeline_stages
    intelligence = model["dashboard_intelligence"]
    assert intelligence["health"]
    assert intelligence["action_center"]
    assert "release_readiness" in intelligence
    assert "quality_rollup" in intelligence
    assert "data_freshness" in intelligence
    assert "shortcuts" in intelligence
    assert any(item["label"] == "GT-KB" for item in intelligence["health"])
    focus_options = module._session_focus_options(model)
    assert [option["label"] for option in focus_options] == [
        "Optimize Startup Token Consumption",
        "Top Priority Actions",
        "Resolve Release Blockers",
        "Repair Testing/Tool Integrations",
        "Remediate Known Risks",
        "Clear Stage/Test Release Path",
        "Continue Last Session",
        "Clean For Internal Review",
        "Pick From Standing Backlog",
    ]
    assert all(option["prompt"] for option in focus_options)
    assert "backlog" in focus_options[8]["prompt"].lower()

    subsystems = set(model["dashboard_requirements"]["subsystems"])
    assert {
        "backlog",
        "MemBase",
        "Deliberation Archive",
        "tests",
        "templates",
        "specifications",
        "drift",
        "regression",
        "contention",
        "tokens consumed before user input",
    } <= subsystems


def test_loyal_opposition_role_profile_reports_active_bridge() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT, role_profile="loyal-opposition")

    assert model["role"]["assumed_role"] == "Loyal Opposition"
    assert model["role"]["role_assignment"] == "active AI harness assigned by owner for counterpart review"
    assert "bridge/INDEX.md" in model["role"]["bridge"]
    assert model["role"]["role_mapping_source"] == "AGENTS.md"


def test_dashboard_and_report_are_written_with_time_series_kpi(tmp_path) -> None:
    module = _load_module()
    dashboard_dir = tmp_path / "dashboard"
    history_path = tmp_path / "history.json"

    result = module.write_dashboard_and_report(REPO_ROOT, dashboard_dir, history_path, generate_pdf=False)

    dashboard = Path(result["dashboard_path"])
    data = Path(result["data_path"])
    report = Path(result["report_path"])
    wrapup = Path(result["wrapup_path"])
    pdf = Path(result["pdf_path"])
    assert dashboard.is_file()
    assert data.is_file()
    assert report.is_file()
    assert wrapup.is_file()
    assert history_path.is_file()
    assert pdf.name == "agent-red-project-dashboard.pdf"
    assert result["pdf_export"]["available"] is False

    dashboard_text = dashboard.read_text(encoding="utf-8")
    report_text = report.read_text(encoding="utf-8")
    wrapup_text = wrapup.read_text(encoding="utf-8")
    dashboard_data = json.loads(data.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))

    assert "<title>Agent Red Project Dashboard</title>" in dashboard_text
    assert "<h1>Agent Red Project Dashboard</h1>" in dashboard_text
    assert "dashboard-hero" in dashboard_text
    assert "health-strip" in dashboard_text
    assert "Export PDF" in dashboard_text
    assert "agent-red-project-dashboard.pdf" in dashboard_text
    assert "Action Center" in dashboard_text
    assert "Shortcuts" in dashboard_text
    assert "Delivery Timeline" in dashboard_text
    assert 'id="deliveryTimeline"' in dashboard_text
    assert 'class="timeline-rail"' in dashboard_text
    assert 'class="timeline-event"' in dashboard_text
    assert 'class="timeline-detail"' in dashboard_text
    assert 'class="timeline-date-badge"' in dashboard_text
    assert "Calendar Date" in dashboard_text
    assert "Version / Build" in dashboard_text
    assert "Test Results" in dashboard_text
    assert "Staging Deployment" in dashboard_text
    assert "Production Deployment" in dashboard_text
    assert "scripts/deploy/build-and-deploy-staging.ps1" in dashboard_text
    assert "scripts/deploy/api-gateway-restore.yaml" in dashboard_text
    assert "Choose This Session's Focus" not in dashboard_text
    assert '<details class="drilldown" id="currentSnapshot">' in dashboard_text
    assert '<summary>Current Snapshot' in dashboard_text
    assert '<details class="drilldown" id="timeSeriesHistory">' in dashboard_text
    assert '<summary>Time-Series KPI History' in dashboard_text
    assert "Time-Series KPI History" in dashboard_text
    assert "Executive Signals" in dashboard_text
    assert "Change increment" in dashboard_text
    assert "Calendar days" in dashboard_text
    assert 'id="timeIncrement"' in dashboard_text
    assert "aggregateByCalendarDay" in dashboard_text
    assert "selectedIncrement" in dashboard_text
    assert "Trend Signals" in dashboard_text
    assert "KPI Movement" in dashboard_text
    assert "Divergence And Convergence" in dashboard_text
    assert "Work Pressure vs Knowledge Surface" in dashboard_text
    assert "Change Heatmap" in dashboard_text
    assert "Release Readiness" in dashboard_text
    assert "Quality / Security / Testing Rollup" in dashboard_text
    assert "Risk Register" in dashboard_text
    assert "Implementation Infrastructure" in dashboard_text
    assert "GT-KB is reported here only as project instrumentation" in dashboard_text
    assert "GT-KB Version / Upgrade Posture" in dashboard_text
    assert "Dry-Run Plan Command" in dashboard_text
    assert "Apply Gate" in dashboard_text
    assert "GT-KB Upgrade Plan Sample" in dashboard_text
    assert "https://github.com/Remaker-Digital/groundtruth-kb" in dashboard_text
    assert "Testing Service / Tool Integrations" in dashboard_text
    assert 'id="testingServiceIntegrations"' in dashboard_text
    assert 'class="integration-drilldown"' in dashboard_text
    assert 'class="status-dot ' in dashboard_text
    assert ".status-dot.red" in dashboard_text
    assert ".status-dot.yellow" in dashboard_text
    assert ".status-dot.green" in dashboard_text
    assert "Suggested Remediation" in dashboard_text
    assert "Open the latest failing required workflow runs" in dashboard_text
    assert "Verify the `SONAR_TOKEN` secret" in dashboard_text
    assert "Run the Ruff blocking and format checks locally" in dashboard_text
    assert "GitHub" in dashboard_text
    assert "SonarCloud" in dashboard_text
    assert "Semgrep SAST" in dashboard_text
    assert "Docker Scout" in dashboard_text
    assert "axe-core Accessibility" in dashboard_text
    assert "Chromatic" in dashboard_text
    assert "OpenAPI Compatibility" in dashboard_text
    assert "Locust Performance" in dashboard_text
    assert "Mutation Testing" in dashboard_text
    assert "release gate: yes" in dashboard_text
    assert "Data Freshness / Provenance" in dashboard_text
    assert 'id="dataFreshness"' in dashboard_text
    assert 'id="dashboardData"' in dashboard_text
    assert "renderSparklines" in dashboard_text
    assert "Backlog" in dashboard_text
    assert "MemBase Open WI" in dashboard_text
    assert "Tokens" in dashboard_text
    assert "Role being assumed: Prime Builder" in report_text
    assert "Startup Disclosure" in report_text
    assert "Agent Red Project Dashboard" in report_text
    assert "Dashboard scope:" in report_text
    assert "Current Project State" in report_text
    assert "Release blockers:" in report_text
    assert "Testing/tool rollup:" in report_text
    assert "Wrap-Up Trigger Commands" in report_text
    assert "Accepted wrap-up commands:" in report_text
    assert "`wrap up`" in report_text
    assert "`start a new session`" in report_text
    assert "`begin fresh`" in report_text
    assert "Optional leading or trailing `please`" in report_text
    assert "### File Bridge Scan" not in report_text
    assert "### Startup Pruning" not in report_text
    assert "Token Consumption Reduction Options" not in report_text
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in report_text
    assert "Three Top Priority Actions" not in report_text
    assert "Would you like to proceed with established priority actions? (Y/N)" not in report_text
    assert "Choose This Session's Focus" in report_text
    assert "Reply with the number or exact label" in report_text
    assert "Optimize Startup Token Consumption" in report_text
    assert "Use this reduction set:" in report_text
    assert "Use the dashboard link before loading large artifacts into context" in report_text
    assert "Top Priority Actions" in report_text
    assert "GTKB-GOV-006" in report_text
    assert "GTKB-GOV-006" in report_text
    assert "GTKB-GOV-007" in report_text
    assert "Current signal:" in report_text
    assert "Prompt details:" in report_text
    assert "Resolve Release Blockers" in report_text
    assert "Repair Testing/Tool Integrations" in report_text
    assert "Remediate Known Risks" in report_text
    assert "Clear Stage/Test Release Path" in report_text
    assert "Continue Last Session" in report_text
    assert "Clean For Internal Review" in report_text
    assert "Pick From Standing Backlog" in report_text
    assert "Or provide a prompt for something else." in report_text
    assert "Startup Focus Input Gate" not in report_text
    assert "Skills, Plug-ins, Directives, And Hooks" not in report_text
    assert report_text.index("## Startup Disclosure") < report_text.index("## Choose This Session's Focus")
    assert "Proactive Session Wrap-Up" in wrapup_text
    assert "should not have to explicitly instruct GT-KB" in wrapup_text
    assert ".claude/skills/kb-session-wrap/SKILL.md" in wrapup_text
    assert "Suggested Next User Actions" in wrapup_text
    assert "Safe automatic action" in wrapup_text
    assert dashboard_data["history"]
    assert dashboard_data["model"]["dashboard_requirements"]["scope_version"] == "agent_red_v1"
    intelligence = dashboard_data["model"]["dashboard_intelligence"]
    assert intelligence["health"]
    assert intelligence["action_center"]
    assert intelligence["release_readiness"]["release_gate_script"] == "scripts/release_candidate_gate.py"
    assert intelligence["quality_rollup"]["total"] >= 1
    assert intelligence["data_freshness"]["scope_version"] == "agent_red_v1"
    assert any(shortcut["label"] == "Open GitHub Actions" for shortcut in intelligence["shortcuts"])
    delivery_timeline = dashboard_data["model"]["infrastructure"]["delivery_timeline"]
    assert delivery_timeline["timeline"]
    assert any(item["stage"] == "commit" for item in delivery_timeline["timeline"])
    assert any(item["stage"] == "build" for item in delivery_timeline["timeline"])
    assert any(item["stage"] == "staging_deployment" for item in delivery_timeline["timeline"])
    assert any(item["stage"] == "production_deployment" for item in delivery_timeline["timeline"])
    posture = dashboard_data["model"]["infrastructure"]["gtkb_upgrade_posture"]
    assert posture["repo_url"] == "https://github.com/Remaker-Digital/groundtruth-kb"
    assert posture["apply_enabled"] is False
    assert posture["upgrade_plan"]["available"] is True
    github = dashboard_data["model"]["infrastructure"]["testing_service_integrations"]["github"]
    assert github["workflow_count"] >= 1
    assert github["scope"] == "implementation_infrastructure"
    assert github["remediation"]
    assert dashboard_data["model"]["infrastructure"]["testing_service_integrations"]["sonarcloud"]["scope"] == (
        "implementation_infrastructure"
    )
    assert any(row["scope_confidence"] == "agent_red_inferred" for row in dashboard_data["history"])
    assert all(row["scope_version"] == "agent_red_v1" for row in dashboard_data["history"])
    assert history[-1]["token_measurement_status"]
    assert history[-1]["scope_version"] == "agent_red_v1"


def test_startup_pruning_scan_reports_large_inputs(tmp_path) -> None:
    module = _load_module()
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text("Document: active\nGO: bridge/active-001.md\n", encoding="utf-8")
    (tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX").mkdir(parents=True)
    (tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "INSIGHTS-test.md").write_text(
        "x" * (module.STARTUP_PRUNING_LARGE_FILE_BYTES + 1),
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text("startup contract\n", encoding="utf-8")

    scan = module._startup_pruning_scan(
        tmp_path,
        {
            "inserted": 1,
            "already_archived": 0,
            "pruned_from_index": 1,
        },
    )

    assert scan["file_count"] >= 2
    assert scan["completed_count"] == 1
    assert scan["candidate_count"] >= 1
    assert any(candidate["target"] == "bridge/INDEX.md" for candidate in scan["candidates"])
    assert any(
        candidate["target"].endswith("INSIGHTS-test.md")
        for candidate in scan["candidates"]
        if candidate["type"] == "candidate"
    )


def test_emit_report_uses_session_start_hook_context_json(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )

    exit_code = module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-report",
            "--skip-bridge-maintenance",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "## Startup Disclosure" in context
    assert "### Live Project Dashboard" in context
    assert "Agent Red Project Dashboard" in context
    assert "### Current Project State" in context
    assert "Release blockers:" in context
    assert "### Wrap-Up Trigger Commands" in context
    assert "Accepted wrap-up commands:" in context
    assert "`wrap up`" in context
    assert "`start a new session`" in context
    assert "`begin fresh`" in context
    assert "### Startup Pruning" not in context
    assert "## Token Consumption Reduction Options" not in context
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in context
    assert "## Three Top Priority Actions" not in context
    assert "Would you like to proceed with established priority actions? (Y/N)" not in context
    assert "## Choose This Session's Focus" in context
    assert "Optimize Startup Token Consumption" in context
    assert "Use this reduction set:" in context
    assert "Use the dashboard link before loading large artifacts into context" in context
    assert "Top Priority Actions" in context
    assert "GTKB-GOV-006" in context
    assert "Current signal:" in context
    assert "Prompt details:" in context
    assert "Resolve Release Blockers" in context
    assert "Continue Last Session" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Choose This Session's Focus")


def test_emit_wrapup_uses_session_start_hook_context_json(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )

    exit_code = module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-wrapup",
            "--force-wrapup",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "Proactive Session Wrap-Up" in context
    assert "Agent Red Project Dashboard" in context
    assert "Suggested Next User Actions" in context


def test_emit_wrapup_suppresses_first_stop_after_startup_focus_gate(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )
    guard_path = tmp_path / "guard.json"

    assert module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-report",
            "--fast-hook",
            "--lifecycle-guard-path",
            str(guard_path),
        ]
    ) == 0
    capsys.readouterr()

    assert module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-wrapup",
            "--fast-hook",
            "--lifecycle-guard-path",
            str(guard_path),
        ]
    ) == 0

    assert json.loads(capsys.readouterr().out) == {}
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["first_wrapup_suppressed"] is True
    assert guard_state["last_suppressed_reason"] == "startup_focus_input_pending"
    assert guard_state["suppress_next_wrapup"] is False

    assert module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-wrapup",
            "--fast-hook",
            "--lifecycle-guard-path",
            str(guard_path),
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert "Proactive Session Wrap-Up" in payload["additionalContext"]


def test_fast_hook_skips_expensive_history_and_pdf_paths(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()

    def fail_historical_backfill(project_root):
        raise AssertionError("fast hook must not recompute historical backfill")

    def fail_pdf_export(dashboard_path, pdf_path):
        raise AssertionError("fast hook must not export PDF")

    monkeypatch.setattr(module, "_historical_agent_red_backfill", fail_historical_backfill)
    monkeypatch.setattr(module, "_write_dashboard_pdf", fail_pdf_export)

    exit_code = module.main(
        [
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-report",
            "--fast-hook",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "## Startup Disclosure" in context
    assert "### Wrap-Up Trigger Commands" in context
    assert "Accepted wrap-up commands:" in context
    assert "### File Bridge Scan" not in context
    assert "## Token Consumption Reduction Options" not in context
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in context
    assert "## Three Top Priority Actions" not in context
    assert "Would you like to proceed with established priority actions? (Y/N)" not in context
    assert "## Choose This Session's Focus" in context
    assert "Optimize Startup Token Consumption" in context
    assert "Use this reduction set:" in context
    assert "Use the dashboard link before loading large artifacts into context" in context
    assert "Top Priority Actions" in context
    assert "GTKB-GOV-006" in context
    assert "Current signal:" in context
    assert "Prompt details:" in context
    assert "Continue Last Session" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Choose This Session's Focus")
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert history
    assert all(row["scope_confidence"] != "agent_red_inferred" for row in history)


def test_top_priority_actions_come_from_standing_backlog() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT)
    action_ids = [item["id"] for item in model["top_priority_actions"]]

    assert len(action_ids) == 3
    assert action_ids[0] == "GTKB-GOV-006"
    assert "GTKB-GOV-002" not in action_ids
    assert "GTKB-GOV-006" in action_ids
