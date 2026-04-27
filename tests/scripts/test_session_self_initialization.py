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


def _panel_titles(panels: list[dict]) -> list[str]:
    titles: list[str] = []
    for panel in panels:
        titles.append(panel["title"])
        titles.extend(_panel_titles(panel.get("panels", [])))
    return titles


def test_user_local_preference_controls_startup_dashboard_open(tmp_path, monkeypatch) -> None:
    module = _load_module()
    preference_path = tmp_path / "session-startup-preferences.json"
    opened: list[str] = []
    dashboard_url = "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard"

    monkeypatch.setenv("GTKB_STARTUP_PREFERENCES_PATH", str(preference_path))
    monkeypatch.delenv("GTKB_OPEN_DASHBOARD_ON_SESSION_START", raising=False)
    monkeypatch.delenv("GTKB_DASHBOARD_OPEN_MODE", raising=False)
    monkeypatch.setattr(module, "_open_dashboard_url_in_system_browser", lambda url: opened.append(url) or True)

    assert module._maybe_open_dashboard_on_session_start(dashboard_url) is False
    assert opened == []

    preference_path.write_text(
        json.dumps({"open_dashboard_on_session_start": True}) + "\n",
        encoding="utf-8",
    )

    assert module._maybe_open_dashboard_on_session_start(dashboard_url) is True
    assert opened == []

    preference_path.write_text(
        json.dumps({"open_dashboard_on_session_start": False}) + "\n",
        encoding="utf-8",
    )

    assert module._maybe_open_dashboard_on_session_start(dashboard_url) is False
    assert opened == []

    preference_path.write_text(
        json.dumps(
            {
                "open_dashboard_on_session_start": True,
                "dashboard_open_mode": "system_default_browser",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert module._maybe_open_dashboard_on_session_start(dashboard_url) is True
    assert opened == [dashboard_url]


def test_startup_model_contains_role_governance_and_kpi_inventory(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")

    assert model["role"]["assumed_role"] == "Prime Builder"
    assert (
        model["role"]["role_assignment"] == "active AI harness assigned by owner through durable operating-role record"
    )
    assert model["role"]["bridge"] == "always available through bridge/INDEX.md and checked at session startup"
    assert "separate harnesses" in model["role"]["poller"]
    assert "Strict GOV enforcement" in model["governance_stance"][0]
    assert "Formal artifact approval" in " ".join(model["governance_stance"])
    assert model["skills"]["count"] > 0
    assert "operating-role.md" in model["role"]["role_mapping_source"]
    assert "formal-artifact-approval-gate.py" in model["directives"]["hook_files"]
    assert model["workstream_focus"]["default_label"] == "Application Focus"
    assert model["workstream_focus"]["current_label"] == "Application Focus"
    assert model["workstream_focus"]["application_label"] == "Agent Red"
    assert model["dashboard_requirements"]["scope_version"] == "agent_red_v1"
    assert model["dashboard_requirements"]["scope_note"] == "Agent Red product/project dashboard."
    assert (
        model["metrics"]["specifications"]["raw_current_total"] >= model["metrics"]["specifications"]["current_total"]
    )
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
    assert intelligence["data_freshness"]["generated_at"] == model["generated_at"]
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
        "Clean For Internal Review",
        "Pick From Standing Backlog",
        "Commit and push to GitHub",
        "Merge to main, build and push to the staging environment",
        "Execute end-to-end tests in the staging environment",
        "Push staged-and-tested build to production, then smoke test",
        "Continue Last Session",
    ]
    assert all(option["prompt"] for option in focus_options)
    assert "GO/NO-GO bridge" in focus_options[12]["prompt"]
    assert "backlog" in focus_options[7]["prompt"].lower()
    assert "push" in focus_options[8]["prompt"].lower()
    assert "staging" in focus_options[9]["prompt"].lower()
    assert "end-to-end" in focus_options[10]["label"].lower()
    assert "production" in focus_options[11]["prompt"].lower()

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


def test_startup_model_discovers_durable_operating_role() -> None:
    module = _load_module()
    discovered_role = module.discover_role_profile(REPO_ROOT)

    assert discovered_role in module.ROLE_PROFILES

    model = module.build_startup_model(REPO_ROOT)
    report = module.render_report(model, "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard", REPO_ROOT)

    assert model["role_profile"] == discovered_role
    assert model["role"]["assumed_role"] == module.ROLE_PROFILES[discovered_role]["assumed_role"]
    assert "operating-role.md" in model["role"]["role_mapping_source"]
    if discovered_role == "loyal-opposition":
        assert "## Loyal Opposition Startup Task" in report
        assert "## Choose This Session's Focus" not in report
    else:
        assert "## Loyal Opposition Startup Task" not in report
        assert "## Choose This Session's Focus" in report
        assert "13. **Continue Last Session**" in report


def test_harness_local_role_record_overrides_repo_default_for_startup(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    codex_dir = tmp_path / ".codex" / "agent-red-hooks"
    codex_dir.mkdir(parents=True)
    role_path = codex_dir / "operating-role.md"
    guard_path = codex_dir / "session-lifecycle-guard.json"
    role_path.write_text("active_role: loyal-opposition\n", encoding="utf-8")
    monkeypatch.setitem(module.HARNESS_ROLE_RECORDS, "codex", role_path)
    monkeypatch.setitem(module.HARNESS_LIFECYCLE_GUARDS, "codex", guard_path)
    monkeypatch.delenv("GTKB_OPERATING_ROLE_PATH", raising=False)
    monkeypatch.delenv("GTKB_LIFECYCLE_GUARD_PATH", raising=False)
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
            "--fast-hook",
            "--skip-bridge-maintenance",
            "--harness-name",
            "codex",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "Role being assumed: Loyal Opposition" in context
    assert f"Role mapping source: {role_path}" in context
    assert guard_path.exists()


def test_startup_report_treats_first_owner_message_as_session_start_stimulus() -> None:
    module = _load_module()

    prime_model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    prime_report = module.render_report(
        prime_model,
        "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard",
        REPO_ROOT,
    )

    assert "### Fresh-Session Input Semantics" in prime_report
    assert "The first owner message in a fresh session is a session-start stimulus only" in prime_report
    assert "do not interpret it as a focus choice, task prompt, approval, answer" in prime_report
    assert "wait for Mike's next message before choosing or mapping session work" in prime_report
    assert prime_report.index("### Fresh-Session Input Semantics") < prime_report.index(
        "## Choose This Session's Focus"
    )

    loyal_model = module.build_startup_model(REPO_ROOT, role_profile="loyal-opposition")
    loyal_report = module.render_report(
        loyal_model,
        "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard",
        REPO_ROOT,
    )

    assert "### Fresh-Session Input Semantics" in loyal_report
    assert "The first owner message in a fresh session is a session-start stimulus only" in loyal_report
    assert "wait for Mike's next message before choosing or mapping session work" in loyal_report


def test_startup_report_surfaces_session_overlay_status_as_non_authoritative(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")

    overlay = model["session_overlay"]
    assert overlay["authoritative"] is False
    assert "overlay_root" in overlay
    # The live repo has no overlay unless a prior run created one; either
    # shape is acceptable, but the non-authoritative contract must hold.
    assert isinstance(overlay.get("is_stale"), bool)
    assert isinstance(overlay.get("entries_total"), int)
    assert isinstance(overlay.get("notes"), list)
    assert any("non-authoritative" in note or "no current session overlay" in note for note in overlay["notes"])

    report = module.render_report(model, "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard", REPO_ROOT)
    assert "### Session Overlay Status (Non-Authoritative)" in report
    assert "non-authoritative by construction" in report
    # The overlay section must appear before the input-semantics section so
    # startup readers see the overlay disclaimer before any focus-choice wording.
    assert report.index("### Session Overlay Status (Non-Authoritative)") < report.index(
        "### Fresh-Session Input Semantics"
    )


def test_workflow_run_can_prefer_release_branch_over_newer_pr_run() -> None:
    module = _load_module()
    workflows = {"docs-quality.yml": {"name": "Docs Quality"}}
    runs = {
        "runs": [
            {
                "workflowName": "Docs Quality",
                "headBranch": "dependabot/github_actions/actions/setup-node-6",
                "conclusion": "failure",
            },
            {"workflowName": "Docs Quality", "headBranch": "main", "conclusion": "success"},
        ],
        "runs_by_workflow": {
            "Docs Quality": {
                "workflowName": "Docs Quality",
                "headBranch": "dependabot/github_actions/actions/setup-node-6",
                "conclusion": "failure",
            }
        },
    }

    assert module._workflow_run(runs, workflows, "docs-quality.yml")["conclusion"] == "failure"
    release_run = module._workflow_run(runs, workflows, "docs-quality.yml", branch="main")

    assert release_run["headBranch"] == "main"
    assert release_run["conclusion"] == "success"


def test_loyal_opposition_role_profile_reports_active_bridge() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT, role_profile="loyal-opposition")
    report = module.render_report(model, "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard", REPO_ROOT)

    assert model["role"]["assumed_role"] == "Loyal Opposition"
    assert model["role"]["role_assignment"] == "active AI harness assigned by owner for counterpart review"
    assert model["role"]["bridge"] == "always available through bridge/INDEX.md and checked at session startup"
    assert "separate harnesses" in model["role"]["poller"]
    assert model["role"]["role_mapping_source"] == ".claude/rules/operating-role.md"
    assert "## Loyal Opposition Startup Task" in report
    assert "## Choose This Session's Focus" not in report
    assert "Commit and push to GitHub" not in report
    assert "Default session purpose: process Prime Builder reviews and verifications on the file bridge." in report
    assert "Session-focus menu: not presented in Loyal Opposition mode" in report
    assert "Bridge/poller distinction: the file bridge is the durable role handoff and review mechanism" in report
    assert "Bridge startup rule: check the file bridge in both Prime Builder and Loyal Opposition startup." in report
    assert "current bridge state must be determined only from a fresh read of live `bridge/INDEX.md`" in report
    assert (
        "Mandatory direct-read rule: before reporting the live bridge scan count, read `bridge/INDEX.md` directly"
        in report
    )
    assert (
        "startup reports, dashboard JSON, cached documents, copied excerpts, summary counts, or hook-generated summaries"
        in report
    )
    assert "do not display this checklist as a substitute for performing the verification" in report
    assert "Poller startup rule: activate a poller only when the roles are running in separate harnesses" in report
    assert "First task: verify that the Prime Builder / Loyal Opposition file bridge is functioning." in report
    assert "permanent owner permission to diagnose and repair bridge function/use" in report
    assert "report the live scan result and ask Mike whether to begin processing reviews and verifications" in report
    assert "yes` to begin processing the bridge queue" in report


def test_loyal_opposition_bridge_scan_uses_unscoped_protocol_queue(tmp_path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "\n".join(
            [
                "# Bridge Index",
                "",
                "Document: gtkb-tier-a-current-main-integration",
                "NEW: bridge/gtkb-tier-a-current-main-integration-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bridge_dir / "gtkb-tier-a-current-main-integration-001.md").write_text(
        "# GT-KB Current Main Integration\n\nGroundTruth-KB bridge proposal.",
        encoding="utf-8",
    )

    contention = module._bridge_metrics(tmp_path)

    assert contention["latest_status_counts"] == {}
    assert contention["actionable_count"] == 0
    assert contention["raw_latest_status_counts"] == {"NEW": 1}
    assert contention["raw_review_queue_count"] == 1
    assert contention["source"] == "bridge/INDEX.md"
    assert contention["source_read_mode"] == "direct_file_read"
    assert contention["derived_artifacts_authoritative"] is False
    assert contention["live_index_available"] is True
    assert (
        module._render_file_bridge_scan({"metrics": {"contention": contention}})
        == "- Generated-time file bridge scan, non-authoritative after report generation: 1 latest NEW/REVISED entry identified."
    )


def test_bridge_metrics_ignore_cached_startup_report_counts(tmp_path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    dashboard_dir = tmp_path / "docs" / "gtkb-dashboard"
    bridge_dir.mkdir(parents=True)
    dashboard_dir.mkdir(parents=True)
    (bridge_dir / "INDEX.md").write_text(
        "\n".join(
            [
                "# Bridge Index",
                "",
                "Document: cached-report-must-not-win",
                "GO: bridge/cached-report-must-not-win-002.md",
                "NEW: bridge/cached-report-must-not-win-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bridge_dir / "cached-report-must-not-win-002.md").write_text("Approved.", encoding="utf-8")
    (dashboard_dir / "session-startup-report.md").write_text(
        "- Generated-time file bridge scan, non-authoritative after report generation: 99 latest NEW/REVISED entries identified.\n",
        encoding="utf-8",
    )
    (dashboard_dir / "dashboard-data.json").write_text(
        json.dumps({"model": {"metrics": {"contention": {"raw_review_queue_count": 99}}}}),
        encoding="utf-8",
    )

    contention = module._bridge_metrics(tmp_path)

    assert contention["raw_latest_status_counts"] == {"GO": 1}
    assert contention["raw_review_queue_count"] == 0
    assert contention["source_read_mode"] == "direct_file_read"


def test_dashboard_and_report_are_written_with_time_series_kpi(tmp_path) -> None:
    module = _load_module()
    dashboard_dir = tmp_path / "dashboard"
    history_path = tmp_path / "history.json"

    result = module.write_dashboard_and_report(
        REPO_ROOT,
        dashboard_dir,
        history_path,
        generate_pdf=False,
        role_profile="prime-builder",
    )

    dashboard = Path(result["dashboard_path"])
    data = Path(result["data_path"])
    report = Path(result["report_path"])
    wrapup = Path(result["wrapup_path"])
    pdf = Path(result["pdf_path"])
    legacy_static_dashboard = dashboard_dir / "index.html"
    assert dashboard.name == "gtkb-dashboard.json"
    assert dashboard.is_file()
    assert result["dashboard_url"] == "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard"
    assert not legacy_static_dashboard.exists()
    assert data.is_file()
    assert report.is_file()
    assert wrapup.is_file()
    assert history_path.is_file()
    assert pdf.name == "agent-red-project-dashboard.pdf"
    assert result["pdf_export"]["available"] is False
    assert result["pdf_export"]["error"] == "Static dashboard PDF export is disabled."

    dashboard_json = json.loads(dashboard.read_text(encoding="utf-8"))
    report_text = report.read_text(encoding="utf-8")
    wrapup_text = wrapup.read_text(encoding="utf-8")
    dashboard_data = json.loads(data.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))

    panel_titles = set(_panel_titles(dashboard_json["panels"]))
    assert dashboard_json["title"] == "Agent Red GT-KB Dashboard"
    assert "Shortcuts" in panel_titles
    assert "Health Signals" in panel_titles
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
    assert "GT-KB Install and Setup" in panel_titles
    assert "Step-by-Step Setup" in panel_titles
    assert "Required Tools, CLIs, and SDKs" in panel_titles
    assert "Third-Party Test Services" in panel_titles
    assert "Action Center" in panel_titles
    assert "Delivery Timeline" in panel_titles
    assert "Delivery Timeline Details" in panel_titles
    assert "Release Readiness" in panel_titles
    assert "KPI History Details" in panel_titles
    assert "Integration Status Details" in panel_titles
    assert "Data Freshness" in panel_titles
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
    all_panels = list(dashboard_json["panels"])
    for panel in dashboard_json["panels"]:
        all_panels.extend(panel.get("panels", []))
    assert any(
        "setup_steps" in target.get("queryText", "") for panel in all_panels for target in panel.get("targets", [])
    )
    assert any(
        "third_party_services" in target.get("queryText", "")
        for panel in all_panels
        for target in panel.get("targets", [])
    )
    assert "Role being assumed: Prime Builder" in report_text
    assert "Bridge: always available through bridge/INDEX.md and checked at session startup" in report_text
    assert "Poller: activate only when Prime Builder and Loyal Opposition run in separate harnesses" in report_text
    assert "Startup Disclosure" in report_text
    assert "Agent Red Project Dashboard" in report_text
    assert "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard" in report_text
    assert "Browser opening: use the harness-controlled browser" in report_text
    assert "system_default_browser" in report_text
    assert "http://127.0.0.1:3000/d/agent-red-gtkb/agent-red-gt-kb-dashboard" in wrapup_text
    assert str(dashboard.resolve()) not in report_text
    assert "file:///" not in report_text
    assert "file:///" not in wrapup_text
    assert "Dashboard scope:" in report_text
    assert "Current Project State" in report_text
    assert "Application release blockers:" in report_text
    assert "Bridge role slot:" in report_text
    assert "Harness topology:" in report_text
    assert "Testing/tool rollup:" in report_text
    assert "Active Work Subject" in report_text
    assert "Default work subject: Application Focus" in report_text
    assert "Application work subject commands:" in report_text
    assert "`work subject application`" in report_text
    assert "`work subject GT-KB`" in report_text
    assert "`GT-KB mode`" in report_text
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
    assert "GTKB-GOV-006" not in report_text
    assert "GTKB-GOV-007" not in report_text
    assert "GTKB-GOV-010" in report_text
    assert "Current signal:" in report_text
    assert "Prompt details:" in report_text
    assert "Resolve Release Blockers" in report_text
    assert "Repair Testing/Tool Integrations" in report_text
    assert "Remediate Known Risks" in report_text
    assert "Clear Stage/Test Release Path" in report_text
    assert "Continue Last Session" in report_text
    assert "Clean For Internal Review" in report_text
    assert "Pick From Standing Backlog" in report_text
    assert "9. **Commit and push to GitHub**" in report_text
    assert "10. **Merge to main, build and push to the staging environment**" in report_text
    assert "11. **Execute end-to-end tests in the staging environment**" in report_text
    assert "12. **Push staged-and-tested build to production, then smoke test**" in report_text
    assert "13. **Continue Last Session**" in report_text
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
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")
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
    assert "Browser opening: use the harness-controlled browser" in context
    assert "### Current Project State" in context
    assert "Application release blockers:" in context
    assert "### Active Work Subject" in context
    assert "Default work subject: Application Focus" in context
    assert "`work subject application`" in context
    assert "`work subject GT-KB`" in context
    assert "`application mode`" in context
    assert "`GT-KB mode`" in context
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
    assert "GTKB-GOV-006" not in context
    assert "GTKB-GOV-007" not in context
    assert "Current signal:" in context
    assert "Prompt details:" in context
    assert "Resolve Release Blockers" in context
    assert "Continue Last Session" in context
    assert "9. **Commit and push to GitHub**" in context
    assert "12. **Push staged-and-tested build to production, then smoke test**" in context
    assert "13. **Continue Last Session**" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Choose This Session's Focus")


def test_emit_startup_service_payload_returns_full_codex_session_start_contract(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")
    monkeypatch.setenv("GTKB_STARTUP_REQUESTED_AT", "2026-04-23T13:20:00Z")
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
            "--emit-startup-service-payload",
            "--fast-hook",
            "--skip-bridge-maintenance",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    hook_output = payload["hookSpecificOutput"]
    context = hook_output["additionalContext"]
    freshness = hook_output["startupFreshness"]
    assert hook_output["hookEventName"] == "SessionStart"
    assert "Programmatic Startup Payload" in context
    assert "agent-red-startup-service-v2" in context
    assert "User-visible startup content below was generated programmatically by the startup service." in context
    assert "relay the generated startup message verbatim as the first durable assistant answer" in context
    assert "Do not summarize, paraphrase, shorten, reorder, or omit any startup section" in context
    assert (
        "Preserve every generated heading, bullet, numbered item, `Current signal`, and `Prompt details` line"
        in context
    )
    assert "all 13 numbered options must remain present in order with their per-option summaries intact" in context
    assert "The first durable assistant answer should be the startup disclosure itself" in context
    assert "The first owner message after SessionStart is discarded startup stimulus only" in context
    assert "Never map the first owner message to `Continue Last Session` or any other focus option." in context
    assert "Codex Desktop durability rule" in context
    assert "first durable assistant answer" in context
    assert "not in transient progress/intermediary output" in context
    assert "Do not replace the startup message with a shorter final answer" in context
    assert "The AI harness is not responsible for composing role, mode, bridge, process, or focus content" in context
    assert "## User-Visible Startup Message" in context
    assert "## Startup Disclosure" in context
    assert "## Choose This Session's Focus" in context
    assert "13. **Continue Last Session**" in context
    assert "Startup First-Response Directive" not in context
    assert "Mandatory Direct Live Bridge Index Read" not in context
    assert "SHA-256:" not in context
    assert freshness["contract_version"] == "agent-red-startup-freshness-v1"
    assert freshness["request_started_at"] == "2026-04-23T13:20:00Z"
    assert freshness["report_origin"] == "in_memory_model_render"
    assert freshness["validation"]["startup_payload_fresh"] is True
    assert freshness["validation"]["status"] in {"fresh", "fresh_with_gaps"}
    assert freshness["required_local_sources"]
    assert any(item["source"] == "bridge/INDEX.md" for item in freshness["required_local_sources"])
    assert any(item["source"] == "GitHub Actions via gh" for item in freshness["live_probes"])
    assert freshness["repo"]["sha"]


def test_emit_report_arms_first_prompt_discard_gate(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    guard_path = tmp_path / "guard.json"
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )

    assert (
        module.main(
            [
                "--project-root",
                str(REPO_ROOT),
                "--dashboard-dir",
                str(tmp_path / "dashboard"),
                "--history-path",
                str(tmp_path / "history.json"),
                "--emit-report",
                "--fast-hook",
                "--skip-bridge-maintenance",
                "--lifecycle-guard-path",
                str(guard_path),
            ]
        )
        == 0
    )
    capsys.readouterr()

    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is True
    assert guard_state["startup_prompt_discarded"] is False
    assert guard_state["startup_response_pending"] is False
    assert guard_state["suppress_next_wrapup"] is True


def test_loyal_opposition_startup_arms_first_prompt_discard_without_wrapup_suppression(
    tmp_path, capsys, monkeypatch
) -> None:
    module = _load_module()
    guard_path = tmp_path / "guard.json"
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "loyal-opposition")
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )

    assert (
        module.main(
            [
                "--project-root",
                str(REPO_ROOT),
                "--dashboard-dir",
                str(tmp_path / "dashboard"),
                "--history-path",
                str(tmp_path / "history.json"),
                "--emit-report",
                "--fast-hook",
                "--skip-bridge-maintenance",
                "--lifecycle-guard-path",
                str(guard_path),
            ]
        )
        == 0
    )
    capsys.readouterr()

    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is True
    assert guard_state["startup_prompt_discarded"] is False
    assert guard_state["startup_response_pending"] is False
    assert guard_state["suppress_next_wrapup"] is False


def test_emit_report_ignores_forced_role_profile_and_uses_durable_toggle(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")
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
            "--fast-hook",
            "--skip-bridge-maintenance",
            "--role-profile",
            "loyal-opposition",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "Role being assumed: Prime Builder" in context
    assert "## Choose This Session's Focus" in context
    assert "## Loyal Opposition Startup Task" not in context


def test_claude_code_startup_discovers_durable_role_without_forced_profile(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    discovered_role = module.discover_role_profile(REPO_ROOT)
    monkeypatch.setattr(
        module,
        "_write_dashboard_pdf",
        lambda dashboard_path, pdf_path: {
            "available": False,
            "path": str(pdf_path),
            "error": "PDF export skipped by test.",
        },
    )
    claude_settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    session_commands = [
        hook["command"] for group in claude_settings["hooks"]["SessionStart"] for hook in group["hooks"]
    ]
    stop_commands = [hook["command"] for group in claude_settings["hooks"]["Stop"] for hook in group["hooks"]]
    assert any("session_self_initialization.py" in command for command in session_commands)
    assert any("--harness-name claude" in command for command in session_commands)
    assert any("--harness-name claude" in command for command in stop_commands)
    assert all("--role-profile" not in command for command in session_commands + stop_commands)

    guard_path = tmp_path / "guard.json"
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
            "--skip-bridge-maintenance",
            "--harness-name",
            "claude",
            "--lifecycle-guard-path",
            str(guard_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert f"Role being assumed: {module.ROLE_PROFILES[discovered_role]['assumed_role']}" in context
    assert "Bridge: always available through bridge/INDEX.md and checked at session startup" in context
    assert "Poller: activate only when Prime Builder and Loyal Opposition run in separate harnesses" in context
    assert "Role mapping source: .claude/rules/operating-role.md" in context
    if discovered_role == "loyal-opposition":
        assert "## Loyal Opposition Startup Task" in context
        assert "## Choose This Session's Focus" not in context
        assert "Commit and push to GitHub" not in context
        assert guard_path.exists()
        guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
        assert guard_state["discard_next_user_prompt"] is True
        assert guard_state["suppress_next_wrapup"] is False
    else:
        assert "## Loyal Opposition Startup Task" not in context
        assert "## Choose This Session's Focus" in context
        assert "9. **Commit and push to GitHub**" in context
        assert "13. **Continue Last Session**" in context
        assert guard_path.exists()
        guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
        assert guard_state["discard_next_user_prompt"] is True
        assert guard_state["suppress_next_wrapup"] is True


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
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")
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

    assert (
        module.main(
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
        )
        == 0
    )
    capsys.readouterr()

    assert (
        module.main(
            [
                "--project-root",
                str(REPO_ROOT),
                "--dashboard-dir",
                str(tmp_path / "dashboard"),
                "--history-path",
                str(tmp_path / "history.json"),
                "--emit-wrapup",
                "--fast-hook",
                "--role-profile",
                "prime-builder",
                "--lifecycle-guard-path",
                str(guard_path),
            ]
        )
        == 0
    )

    assert json.loads(capsys.readouterr().out) == {}
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["first_wrapup_suppressed"] is True
    assert guard_state["last_suppressed_reason"] == "startup_focus_input_pending"
    assert guard_state["suppress_next_wrapup"] is False

    assert (
        module.main(
            [
                "--project-root",
                str(REPO_ROOT),
                "--dashboard-dir",
                str(tmp_path / "dashboard"),
                "--history-path",
                str(tmp_path / "history.json"),
                "--emit-wrapup",
                "--fast-hook",
                "--role-profile",
                "prime-builder",
                "--lifecycle-guard-path",
                str(guard_path),
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert "Proactive Session Wrap-Up" in payload["additionalContext"]


def test_fast_hook_skips_expensive_history_and_pdf_paths(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "discover_role_profile", lambda project_root, **kwargs: "prime-builder")

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
    assert "### Active Work Subject" in context
    assert "Default work subject: Application Focus" in context
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
    assert "GTKB-GOV-006" not in context
    assert "GTKB-GOV-007" not in context
    assert "Current signal:" in context
    assert "Prompt details:" in context
    assert "Continue Last Session" in context
    assert "9. **Commit and push to GitHub**" in context
    assert "12. **Push staged-and-tested build to production, then smoke test**" in context
    assert "13. **Continue Last Session**" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Choose This Session's Focus")
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert history
    assert all(row["scope_confidence"] != "agent_red_inferred" for row in history)


def test_top_priority_actions_come_from_standing_backlog() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    action_ids = [item["id"] for item in model["top_priority_actions"]]

    assert action_ids == ["GTKB-GOV-010"]
    assert "GTKB-ISOLATION-007" not in action_ids
    assert "GTKB-GOV-012" not in action_ids
    assert "GTKB-GOV-007" not in action_ids
    assert "GTKB-GOV-002" not in action_ids
    assert "GTKB-GOV-006" not in action_ids
    assert "GTKB-GOV-010" in action_ids


def test_direct_script_execution_emits_startup_payload(tmp_path):
    """Regression guard for Phase 6 NO-GO -004 F2.

    The SessionStart hook executes `python scripts/session_self_initialization.py
    --emit-startup-service-payload --fast-hook` directly, which exercises a
    different import path than `importlib.util.spec_from_file_location(...)`.
    An `ImportError: cannot import name 'gtkb_overlay' from 'scripts'` regression
    in that direct-execution path escaped the spec-loader tests. This subprocess
    test exercises the actual hook command form.
    """
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--project-root",
            str(REPO_ROOT),
            "--dashboard-dir",
            str(tmp_path / "dashboard"),
            "--history-path",
            str(tmp_path / "history.json"),
            "--emit-startup-service-payload",
            "--fast-hook",
            "--skip-bridge-maintenance",
            "--lifecycle-guard-path",
            str(tmp_path / "guard.json"),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"Direct script execution failed with exit {result.returncode}.\n"
        f"stdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
    )
    # Payload must be valid JSON with the expected hook-output shape.
    payload = json.loads(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "SessionStart"
    assert "agent-red-startup-service-v2" in hook_output["additionalContext"]


# ---- GTKB-ISOLATION-015 Slice 1 §A integration coverage ----------------


def _minimal_model(
    *,
    current_focus: str = "application",
    subject_readiness: dict | None = None,
    dual_scope_declared: bool = False,
) -> dict:
    intelligence: dict = {
        "release_readiness": {"blocker_count": 0},
        "quality_rollup": {"failing": 0, "manual": 0, "ready_or_passing": 0},
    }
    if subject_readiness is not None:
        intelligence["subject_readiness"] = subject_readiness
    intelligence["dual_scope_declared"] = dual_scope_declared
    return {
        "metrics": {
            "regression": {"release_blocker_count": 0},
            "backlog": {"active_item_count": 0},
            "membase": {"open_work_items": 0},
            "contention": {"actionable_count": 0},
            "drift": {"changed_path_count": 0},
        },
        "dashboard_intelligence": intelligence,
        "infrastructure": {"gtkb_upgrade_posture": {"package_version": "x", "upgrade_plan": {}}},
        "workstream_focus": {
            "current_focus": current_focus,
            "role_slot": "shared",
            "topology_mode": "single_harness",
        },
    }


def test_render_current_project_state_labels_application_headers() -> None:
    module = _load_module()
    rendered = module._render_current_project_state(_minimal_model(current_focus="application"))
    assert "Application release blockers:" in rendered
    assert "Application Testing/tool rollup:" in rendered
    assert "Bridge role slot:" in rendered
    assert "Harness topology:" in rendered


def test_render_current_project_state_labels_gtkb_headers() -> None:
    module = _load_module()
    rendered = module._render_current_project_state(_minimal_model(current_focus="gtkb_infrastructure"))
    assert "GT-KB release blockers:" in rendered
    assert "GT-KB Testing/tool rollup:" in rendered


def test_render_current_project_state_hard_rejects_unlabeled_combined_green() -> None:
    module = _load_module()
    import pytest

    with pytest.raises(module.SubjectScopeError, match="combined application \\+ GT-KB"):
        module._render_current_project_state(
            _minimal_model(
                subject_readiness={"application_green": True, "gtkb_green": True},
                dual_scope_declared=False,
            )
        )


def test_render_current_project_state_permits_dual_scope_combined_green() -> None:
    module = _load_module()
    rendered = module._render_current_project_state(
        _minimal_model(
            subject_readiness={"application_green": True, "gtkb_green": True},
            dual_scope_declared=True,
        )
    )
    assert "release blockers:" in rendered


def test_render_current_project_state_permits_single_subject_green() -> None:
    module = _load_module()
    # Only application green; no combined claim.
    rendered = module._render_current_project_state(
        _minimal_model(
            subject_readiness={"application_green": True, "gtkb_green": False},
            dual_scope_declared=False,
        )
    )
    assert "Application release blockers:" in rendered


def test_arm_startup_interaction_guard_persists_current_subject_live_path(tmp_path, monkeypatch) -> None:
    """Live-runtime §E: writer persists current_subject into lifecycle guard.

    Exercises the real writer path introduced for bridge -012 P1 fix.
    The counterpart subject-divergence check in detect_counterpart_state()
    then reads what the writer wrote — no synthetic fixture JSON.
    """
    session_module = _load_module()
    import importlib.util

    focus_spec = importlib.util.spec_from_file_location(
        "workstream_focus_live", REPO_ROOT / "scripts" / "workstream_focus.py"
    )
    assert focus_spec and focus_spec.loader
    focus_module = importlib.util.module_from_spec(focus_spec)
    focus_spec.loader.exec_module(focus_module)

    canonical = tmp_path / "work-subject.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(canonical))
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_LEGACY_STATE", str(tmp_path / "legacy.json"))

    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_role = tmp_path / ".codex" / "operating-role.md"
    claude_role = tmp_path / ".claude" / "operating-role.md"
    for path, role in ((codex_role, "loyal-opposition"), (claude_role, "prime-builder")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"active_role: {role}\n", encoding="utf-8")

    # Counterpart harness (codex) runs startup with GT-KB subject.
    session_module._arm_startup_interaction_guard(
        codex_guard,
        "codex-guard-id",
        suppress_next_wrapup=False,
        current_subject=focus_module.FOCUS_GTKB_INFRASTRUCTURE,
    )
    # Active harness (claude) runs startup with application subject.
    session_module._arm_startup_interaction_guard(
        claude_guard,
        "claude-guard-id",
        suppress_next_wrapup=True,
        current_subject=focus_module.FOCUS_APPLICATION,
    )

    # Assert the writer actually populated current_subject (Codex -012 evidence:
    # prior versions of the writer omitted this field).
    codex_data = json.loads(codex_guard.read_text(encoding="utf-8"))
    claude_data = json.loads(claude_guard.read_text(encoding="utf-8"))
    assert codex_data["current_subject"] == focus_module.FOCUS_GTKB_INFRASTRUCTURE
    assert claude_data["current_subject"] == focus_module.FOCUS_APPLICATION

    # Now route detect_counterpart_state through the files the writer produced.
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setattr(
        focus_module,
        "HARNESS_ROLE_RECORDS",
        {"codex": codex_role, "claude": claude_role},
    )
    monkeypatch.setattr(
        focus_module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    focus_module.save_state(focus_module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = focus_module.detect_counterpart_state(REPO_ROOT)
    assert result["subject_mismatch"] is True
    assert any(
        focus_module.FOCUS_GTKB_INFRASTRUCTURE in msg and focus_module.FOCUS_APPLICATION in msg
        for msg in result["warnings"]
    )


# ---------------------------------------------------------------------------
# Pending-owner-decisions surfacing -- F1 fixture coverage
# Per bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md §2.6
# Codex GO -004 condition: visibility through this script, not a separate hook.
# ---------------------------------------------------------------------------


def test_pending_owner_decisions_loaded_from_durable_file(tmp_path) -> None:
    """T5a equivalent: _load_pending_owner_decisions parses the durable file's
    ## Pending section into a list of decision dicts."""
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "pending-owner-decisions.md").write_text(
        """\
# Pending Owner Decisions
---
## Pending

- id: DECISION-0042
  asked_at: 2026-04-25T09:00:00Z
  thread_ref: bridge/example-001.md
  question: "Phase 8 rehearsal target child root path"
  options:
    - "Sibling under E:\\\\Claude-Playground\\\\"
    - "Fresh top-level workspace"
  detected_via: ask_user_question
  status: pending

## Resolved

(none)

## History

(none)
""",
        encoding="utf-8",
    )
    module = _load_module()
    decisions = module._load_pending_owner_decisions(tmp_path)
    assert len(decisions) == 1
    assert decisions[0]["id"] == "DECISION-0042"
    assert decisions[0]["question"] == "Phase 8 rehearsal target child root path"
    # Options collapse to "; " joined string for downstream consumers.
    assert "Sibling under" in decisions[0]["options"]
    assert "Fresh top-level workspace" in decisions[0]["options"]


def test_pending_owner_decisions_empty_when_section_missing_or_empty(tmp_path) -> None:
    """T5b equivalent: empty list when file missing or ## Pending says (none)."""
    module = _load_module()
    # File missing: empty list, no raise.
    assert module._load_pending_owner_decisions(tmp_path) == []
    # File present but ## Pending section says (none).
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "pending-owner-decisions.md").write_text(
        "# Pending Owner Decisions\n\n## Pending\n\n(none)\n\n## Resolved\n\n(none)\n",
        encoding="utf-8",
    )
    assert module._load_pending_owner_decisions(tmp_path) == []


def test_render_pending_decisions_block_omits_section_when_empty() -> None:
    """T5b additional: renderer returns empty string for empty list."""
    module = _load_module()
    assert module._render_pending_decisions_block([]) == ""


def test_render_pending_decisions_block_includes_id_question_options() -> None:
    """T5a additional: renderer markdown includes id, question, options."""
    module = _load_module()
    decisions = [
        {
            "id": "DECISION-0001",
            "question": "Test?",
            "options": "Yes; No",
            "asked_at": "2026-04-25T09:00:00Z",
            "thread_ref": "bridge/foo-001.md",
        }
    ]
    block = module._render_pending_decisions_block(decisions)
    assert "**DECISION-0001**" in block
    assert "Test?" in block
    assert "Yes; No" in block
    assert "bridge/foo-001.md" in block


# =====================================================================
# REVISED-1 (S315): public-CLI partial-arg regression test
# Per bridge/generator-hardening-001-003.md §5.2 + Codex -004 GO
# =====================================================================


def test_main_with_only_project_root_writes_under_that_root(tmp_path, monkeypatch, capsys) -> None:
    """Per bridge/generator-hardening-001-003.md §5.2 + Codex -004 GO:

    `--project-root <tmp-root>` without explicit `--dashboard-dir` /
    `--history-path` MUST write all output under <tmp-root>, not under
    the canonical PROJECT_ROOT. This is the contract test that would
    have caught the bug Codex -002 flagged (dashboard/history defaults
    bound to PROJECT_ROOT-based module constants).

    Sentinel: capture mtimes of canonical PROJECT_ROOT-bound paths
    before the run; assert they are unchanged after.
    """
    module = _load_module()

    fake_root = tmp_path / "fake-project"
    fake_root.mkdir()
    # Seed minimal project structure expected by the generator.
    (fake_root / "memory").mkdir()
    (fake_root / "docs").mkdir()
    (fake_root / ".claude" / "rules").mkdir(parents=True)
    (fake_root / ".claude" / "rules" / "operating-role.md").write_text("active_role: prime-builder\n", encoding="utf-8")

    # Capture canonical-path sentinels (must remain untouched).
    canonical_dashboard_dir = REPO_ROOT / "docs" / "gtkb-dashboard"
    canonical_history_path = REPO_ROOT / "memory" / "gtkb-dashboard-history.json"
    pre_dashboard_mtime = canonical_dashboard_dir.stat().st_mtime if canonical_dashboard_dir.exists() else None
    pre_history_mtime = canonical_history_path.stat().st_mtime if canonical_history_path.exists() else None

    rc = module.main(
        [
            "--project-root",
            str(fake_root),
            # Deliberately omit --dashboard-dir and --history-path.
            "--fast-hook",
        ]
    )
    assert rc == 0, f"main() returned {rc}"

    # All outputs MUST land under fake_root.
    assert (fake_root / "docs" / "gtkb-dashboard" / "dashboard-data.json").exists(), (
        "dashboard-data.json was not written under fake_root"
    )
    assert (fake_root / "memory" / "gtkb-dashboard-history.json").exists(), (
        "history file was not written under fake_root"
    )

    # Sentinel: canonical paths must NOT have been touched.
    if pre_dashboard_mtime is not None:
        post_dashboard_mtime = canonical_dashboard_dir.stat().st_mtime if canonical_dashboard_dir.exists() else None
        assert post_dashboard_mtime == pre_dashboard_mtime, (
            "Canonical PROJECT_ROOT/docs/gtkb-dashboard mtime changed during run; "
            "this means the generator wrote to the canonical path despite --project-root override"
        )
    if pre_history_mtime is not None:
        post_history_mtime = canonical_history_path.stat().st_mtime if canonical_history_path.exists() else None
        assert post_history_mtime == pre_history_mtime, (
            "Canonical PROJECT_ROOT/memory/gtkb-dashboard-history.json mtime changed; "
            "generator leaked a write to the canonical path"
        )
