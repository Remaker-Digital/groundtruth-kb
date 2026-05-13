"""Tests for fresh-session self-initialization dashboard/report generation."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_self_initialization.py"


@pytest.fixture(autouse=True)
def _isolate_lifecycle_guard_env(tmp_path, monkeypatch) -> None:
    """Keep startup generator tests away from live harness input-gate state."""

    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "session-lifecycle-guard.json"))


def _load_module(*, live_dashboard_probes: bool = False):
    spec = importlib.util.spec_from_file_location("session_self_initialization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization"] = module
    spec.loader.exec_module(module)
    if not live_dashboard_probes:
        module._dashboard_reachability_probes = lambda: [
            {
                "source": "Grafana health endpoint",
                "kind": "live_probe",
                "required": False,
                "status": "queried",
                "queried_at": "2026-05-13T00:00:00Z",
                "detail": module.GRAFANA_HEALTH_URL,
                "http_status": 200,
            },
            {
                "source": "GT-KB dashboard URL",
                "kind": "live_probe",
                "required": False,
                "status": "queried",
                "queried_at": "2026-05-13T00:00:00Z",
                "detail": module.GRAFANA_DASHBOARD_URL,
                "http_status": 200,
            },
        ]
    return module


def _make_synthetic_doctor_check(status: str = "pass", message: str = "synthetic"):
    """Return a function replacing ``_check_smart_bridge_poller`` for orient tests.

    Per ``bridge/smart-poller-orient-verification-2026-04-29-005.md`` §3
    (carry-forward of ``-003 §3.3``): most existing smart-poller orient tests
    don't care about doctor state — they just need the doctor to return
    ``pass`` so the notification path executes. New diagnostic tests use
    ``status='warning'`` or ``'fail'`` to exercise the
    diagnostic-supersedes-notification path.
    """
    from groundtruth_kb.project.doctor import ToolCheck

    def _fn(target):
        return ToolCheck(
            name="Smart bridge poller",
            required=False,
            found=True,
            status=status,
            message=message,
        )

    return _fn


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
    dashboard_url = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"

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
        model["role"]["role_assignment"] == "active AI harness assigned by owner through the single role assignment map"
    )
    assert model["role"]["bridge"] == "always available through bridge/INDEX.md and checked at session startup"
    assert "cross-harness event-driven trigger" in model["role"]["bridge_dispatch"]
    assert "retired smart poller and OS poller remain archived" in model["role"]["bridge_dispatch"]
    assert "gtkb-bridge" in model["role"]["bridge_operation_instructions"]
    assert "scripts/cross_harness_bridge_trigger.py" in model["role"]["bridge_operation_instructions"]
    assert "two complementary axes" in model["role"]["bridge_operation_instructions"]
    assert "DISPATCHABLE WORK" in model["role"]["bridge_operation_instructions"]
    assert "NON-DISPATCHABLE WORK" in model["role"]["bridge_operation_instructions"]
    assert "Both axes are required" in model["role"]["bridge_operation_instructions"]
    assert "Do NOT create new bridge automations" in model["role"]["bridge_operation_instructions"]
    assert "Strict GOV enforcement" in model["governance_stance"][0]
    assert "Formal artifact approval" in " ".join(model["governance_stance"])
    assert model["skills"]["count"] > 0
    assert "role-assignments.json" in model["role"]["role_mapping_source"]
    assert "formal-artifact-approval-gate.py" in model["directives"]["hook_files"]
    assert model["workstream_focus"]["default_label"] == "GT-KB Infrastructure Focus"
    assert model["workstream_focus"]["current_label"] == "GT-KB Infrastructure Focus"
    assert model["workstream_focus"]["application_label"] == "Agent Red demo adopter"
    assert model["dashboard_requirements"]["scope_version"] == "gtkb_v1"
    assert model["dashboard_requirements"]["scope_note"] == "GroundTruth-KB project dashboard."
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
    dev_inventory = model["infrastructure"]["dev_environment_inventory"]
    assert dev_inventory["public_json"] == "docs/release/dev-environment-inventory.json"
    assert dev_inventory["full_inventory_loaded"] is False
    assert dev_inventory["latest_verification_command"]
    harness_parity = model["infrastructure"]["harness_parity"]
    assert harness_parity["status"] in {"pass", "warn", "fail", "unavailable"}
    assert harness_parity["verification_command"]
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
        "dev environment inventory",
        "tokens consumed before user input",
    } <= subsystems


def test_prime_focus_top_priority_uses_go_no_go_bridge_signal() -> None:
    module = _load_module()
    model = {
        "metrics": {
            "regression": {"release_blocker_count": 0, "blockers": []},
            "drift": {"changed_path_count": 0},
            "contention": {"raw_latest_status_counts": {"NEW": 4, "GO": 1, "NO-GO": 1}},
        },
        "dashboard_intelligence": {"risk_register": [], "action_center": []},
        "startup_pruning": {},
        "token_reduction_options": [],
        "infrastructure": {"testing_service_integrations": {}},
        "top_priority_actions": [{"id": "GTKB-ENV-INVENTORY-001", "title": "Harness inventory"}],
    }

    top_priority = module._session_focus_options(model)[1]

    assert "2 latest GO/NO-GO bridge responses" in top_priority["reason"]
    assert "NEW/REVISED" not in top_priority["reason"]


def test_session_focus_recommendations_rank_release_blockers_first() -> None:
    module = _load_module()
    model = {
        "metrics": {
            "regression": {"release_blocker_count": 2, "blockers": ["release gate stale"]},
            "drift": {"changed_path_count": 0},
            "contention": {"raw_latest_status_counts": {}},
            "membase": {"project_state_rollup": {}},
        },
        "dashboard_intelligence": {"risk_register": [], "action_center": []},
        "startup_pruning": {},
        "token_reduction_options": [],
        "infrastructure": {"testing_service_integrations": {}},
        "top_priority_actions": [],
    }

    recommendations = module._rank_session_focus_options(model, module._session_focus_options(model))

    assert [item["label"] for item in recommendations][:2] == [
        "Resolve Release Blockers",
        "Clear Stage/Test Release Path",
    ]
    assert "release gate stale" in recommendations[0]["reason"]


def test_session_focus_recommendations_rank_live_bridge_and_integrations() -> None:
    module = _load_module()
    model = {
        "metrics": {
            "regression": {"release_blocker_count": 0, "blockers": []},
            "drift": {"changed_path_count": 0},
            "contention": {
                "raw_latest_status_counts": {"GO": 2, "NO-GO": 1},
                "raw_prime_response_queue_count": 3,
            },
            "membase": {"project_state_rollup": {}},
        },
        "dashboard_intelligence": {"risk_register": [], "action_center": []},
        "startup_pruning": {},
        "token_reduction_options": [],
        "infrastructure": {
            "testing_service_integrations": {
                "github": {"health": "failing", "display_name": "GitHub Actions", "remediation": "repair CI"}
            }
        },
        "top_priority_actions": [{"id": "GTKB-ENV-INVENTORY-001", "title": "Harness inventory"}],
    }

    recommendations = module._rank_session_focus_options(model, module._session_focus_options(model))
    rendered = module._render_session_focus_options(module._session_focus_options(model), model)

    assert [item["label"] for item in recommendations][:3] == [
        "Repair Testing/Tool Integrations",
        "Continue Last Session",
        "Top Priority Actions",
    ]
    assert "A. **Repair Testing/Tool Integrations**" in rendered
    assert "B. **Continue Last Session**" in rendered
    assert "C. **Top Priority Actions**" in rendered
    assert "D. **Full Focus List**" in rendered
    assert "   - Push staged-and-tested build to production, then smoke test" in rendered


def test_startup_model_discovers_durable_operating_role() -> None:
    module = _load_module()
    discovered_role = module.discover_role_profile(REPO_ROOT)

    assert discovered_role in module.ROLE_PROFILES

    model = module.build_startup_model(REPO_ROOT)
    report = module.render_report(model, "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard", REPO_ROOT)

    assert model["role_profile"] == discovered_role
    assert model["role"]["assumed_role"] == module.ROLE_PROFILES[discovered_role]["assumed_role"]
    assert "role-assignments.json" in model["role"]["role_mapping_source"]
    if discovered_role == "loyal-opposition":
        assert "## Loyal Opposition Startup Task" not in report
        assert "## Session Startup" not in report
    else:
        assert "## Loyal Opposition Startup Task" not in report
        assert "## Session Startup" in report
        assert "### Recommended Session Focus" in report
        assert "D. **Full Focus List**" in report
        assert "   - Continue Last Session" in report


def test_fast_hook_startup_model_skips_optional_live_network_probes(monkeypatch) -> None:
    module = _load_module()

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError("fast-hook startup must not call optional live network probes")

    monkeypatch.setattr(module, "_latest_remote_semver_tag", _fail_if_called)
    monkeypatch.setattr(module, "_remote_branch_sha", _fail_if_called)
    monkeypatch.setattr(module, "_gh_auth_status", _fail_if_called)
    monkeypatch.setattr(module, "_latest_github_workflow_runs", _fail_if_called)

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder", fast_hook=True)
    posture = model["infrastructure"]["gtkb_upgrade_posture"]
    github = model["infrastructure"]["testing_service_integrations"]["github"]

    assert posture["latest_release_probe_error"] == "skipped_fast_hook"
    assert posture["latest_main_probe_error"] == "skipped_fast_hook"
    assert github["gh_auth_status"] == "skipped_fast_hook"
    assert github["latest_run_source"] == "skipped_fast_hook"


def test_dashboard_probe_returns_queried_when_endpoint_returns_200(monkeypatch) -> None:
    module = _load_module(live_dashboard_probes=True)
    observed: dict[str, object] = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def getcode(self):
            return 200

    def fake_urlopen(request, *, timeout):
        observed["url"] = request.full_url
        observed["user_agent"] = request.get_header("User-agent")
        observed["timeout"] = timeout
        return Response()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    result = module._probe_http_url("Grafana health endpoint", module.GRAFANA_HEALTH_URL)

    assert result["status"] == "queried"
    assert result["http_status"] == 200
    assert observed == {
        "url": module.GRAFANA_HEALTH_URL,
        "user_agent": "gtkb-startup-reachability-probe/1.0",
        "timeout": 3.0,
    }


def test_dashboard_probe_returns_unavailable_on_connection_refused(monkeypatch) -> None:
    module = _load_module(live_dashboard_probes=True)

    def fake_urlopen(_request, *, timeout):
        assert timeout == 3.0
        raise module.urllib.error.URLError(ConnectionRefusedError("refused"))

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)

    result = module._probe_http_url("GT-KB dashboard URL", module.GRAFANA_DASHBOARD_URL)

    assert result["status"] == "unavailable"
    assert result["required"] is False
    assert result["timeout_seconds"] == 3.0
    assert "refused" in result["error"]


def test_dashboard_reachability_probes_feed_payload_and_disclosure(monkeypatch) -> None:
    module = _load_module(live_dashboard_probes=True)
    monkeypatch.setattr(
        module,
        "_dashboard_reachability_probes",
        lambda: [
            {
                "source": "Grafana health endpoint",
                "kind": "live_probe",
                "required": False,
                "status": "queried",
                "queried_at": "2026-05-13T00:00:00Z",
                "detail": module.GRAFANA_HEALTH_URL,
                "http_status": 200,
            },
            {
                "source": "GT-KB dashboard URL",
                "kind": "live_probe",
                "required": False,
                "status": "unavailable",
                "queried_at": "2026-05-13T00:00:00Z",
                "detail": module.GRAFANA_DASHBOARD_URL,
                "error": "connection refused",
            },
        ],
    )

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    report = module.render_report(model, module.GRAFANA_DASHBOARD_URL, REPO_ROOT)
    freshness = module._startup_freshness_metadata(
        project_root=REPO_ROOT,
        model=model,
        request_started_at=model["generated_at"],
        payload_emitted_at=model["generated_at"],
        report_origin="in_memory_model_render",
    )

    probes = model["infrastructure"]["dashboard_reachability"]
    assert [probe["source"] for probe in probes] == ["Grafana health endpoint", "GT-KB dashboard URL"]
    assert "Dashboard reachability: Grafana health endpoint: queried (HTTP 200)" in report
    assert "Dashboard reachability: GT-KB dashboard URL: unavailable" in report
    assert "Dashboard recovery hint:" in report
    assert "GT-KB dashboard URL" in freshness["validation"]["live_probe_gaps"]
    assert freshness["validation"]["status"] == "fresh_with_gaps"


def test_harness_role_assignment_map_is_startup_source_of_truth(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    state_root = tmp_path / "harness-state"
    codex_dir = state_root / "codex"
    codex_dir.mkdir(parents=True)
    role_path = state_root / "role-assignments.json"
    guard_path = codex_dir / "session-lifecycle-guard.json"
    role_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"harness_type": "codex", "role": "loyal-opposition"},
                    "B": {"harness_type": "claude", "role": "prime-builder"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setitem(module.HARNESS_LIFECYCLE_GUARDS, "codex", guard_path)
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_path))
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
            "--harness-id",
            "A",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    context = payload["additionalContext"]
    assert "Role being assumed: Loyal Opposition" in context
    assert f"Role mapping source: {role_path}" in context
    assert "Harness self-identification: A" in context
    assert "Harness identity source: harness-state/harness-identities.json" in context
    assert guard_path.exists()


def test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude() -> None:
    """Regression test for harness-state-authority-migration-2026-04-27.

    Verifies session_self_initialization resolves Codex and Claude harness-local
    authority records under harness-state/, not Path.home().
    Closes bridge/s317-working-tree-triage-005.md F5 deferral. Does NOT close
    bridge/generator-hardening-002-008.md (skills/plugin-cache sites remain
    out of scope).
    """
    module = _load_module()
    expected_root = REPO_ROOT / "harness-state"

    # Constant-level invariant: the authority root resolves under PROJECT_ROOT.
    assert expected_root == module.GTKB_HARNESS_STATE_ROOT
    for harness_name in ("codex", "claude"):
        assert module.HARNESS_LIFECYCLE_GUARDS[harness_name].is_relative_to(expected_root)
    assert module.DEFAULT_USER_STARTUP_PREFERENCES_PATH.is_relative_to(expected_root)

    # Behavior-level invariant: operating_role_path() with --harness-name resolves
    # to the in-root role assignment map (not the legacy guidance file
    # repo fallback). prefer_local=False forces the function to gate on
    # local_path.is_file(), which requires the authority files to be tracked
    # (Commit 1 in this thread). If this assertion fails with the repo-fallback
    # path, the migration is incomplete (likely Commit 1 missing).
    for harness_name in ("codex", "claude"):
        role_path = module.operating_role_path(REPO_ROOT, harness_name=harness_name, prefer_local=False)
        assert role_path == expected_root / "role-assignments.json", (
            f"--harness-name {harness_name} must resolve to the single role map, got {role_path}"
        )


def test_project_root_rejects_drive_relative_path_to_prevent_doubling() -> None:
    """Regression test for bridge/session-self-init-project-root-path-doubling-fix-2026-04-27.

    Drive-relative paths like 'E:GT-KB' (no slash after the colon) on Windows
    silently produce doubled output paths via Path.resolve() when CWD is on the
    same drive. The fix raises SystemExit instead of allowing the silent
    corruption.

    Verified at the pathlib level that the input shape is non-absolute, then
    invokes the script via subprocess and asserts non-zero exit + informative
    error message. Pre-fix behavior: subprocess returns 0 and creates nested
    output. Post-fix: subprocess returns non-zero with "absolute" in the error.
    """
    drive_relative_input = "E:GT-KB"
    # Confirm the failing input shape: drive-relative is non-absolute.
    assert not Path(drive_relative_input).is_absolute(), (
        "Drive-relative path must be identified as non-absolute by pathlib; "
        "this is the input shape the fix must reject."
    )
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "session_self_initialization.py"),
            "--project-root",
            drive_relative_input,
            "--emit-startup-service-payload",
            "--fast-hook",
            "--harness-name",
            "codex",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode != 0, (
        f"Script must reject drive-relative --project-root, but exited 0. "
        f"stdout={result.stdout[:200]!r} stderr={result.stderr[:200]!r}"
    )
    combined = (result.stderr + result.stdout).lower()
    assert "absolute" in combined, (
        f"Error message must mention 'absolute path' requirement; "
        f"got stderr={result.stderr[:200]!r} stdout={result.stdout[:200]!r}"
    )


def test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins(monkeypatch) -> None:
    """Regression test for bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28.

    Default behavior (env var unset) must NOT scan home-directory locations for
    skills or plugin-cache. Closes GH-002 row-17 default-secure contract.
    """
    module = _load_module()
    monkeypatch.delenv("GTKB_DISCOVER_USER_EXTENSIONS", raising=False)

    # Sentinel: monkeypatch Path.home to raise if called from within the gated
    # discovery functions. If _discover_skill_files() or _plugin_inventory()
    # accidentally call Path.home() in the default branch, this test fails.
    def _raise_if_called():
        raise AssertionError(
            "Path.home() called in default discovery path; opt-in gate is missing. "
            "Per bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-004.md, "
            "GTKB_DISCOVER_USER_EXTENSIONS=1 must be set to trigger home-dir scan."
        )

    monkeypatch.setattr(module.Path, "home", _raise_if_called)

    skill_files = module._discover_skill_files(REPO_ROOT)
    plugin_list = module._plugin_inventory()

    # Default behavior: skill discovery includes only project-root skills.
    project_skill_root = REPO_ROOT / ".claude" / "skills"
    if project_skill_root.is_dir():
        expected_skills = sorted(project_skill_root.rglob("SKILL.md"), key=lambda p: str(p).lower())
        assert sorted(skill_files, key=lambda p: str(p).lower()) == expected_skills, (
            "Default skill discovery must equal project-root scan only"
        )

    # Default behavior: plugin inventory is empty (home-dir plugin cache not scanned).
    assert plugin_list == [], f"Default plugin inventory must be empty (no home-dir scan); got {plugin_list}"


def test_opt_in_invocation_scans_home_directory_for_skills_and_plugins(monkeypatch, tmp_path) -> None:
    """Regression test for bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28.

    Opt-in behavior (GTKB_DISCOVER_USER_EXTENSIONS=1) must scan synthetic
    home-dir skill + plugin fixtures. Verifies the opt-in path is functional.
    """
    module = _load_module()
    monkeypatch.setenv("GTKB_DISCOVER_USER_EXTENSIONS", "1")
    # Mock Path.home() to point at tmp_path with synthetic skills/plugins inside.
    monkeypatch.setattr(module.Path, "home", lambda: tmp_path)

    # Synthetic home-dir skill fixture
    synthetic_skill_dir = tmp_path / ".codex" / "skills" / "synthetic-skill"
    synthetic_skill_dir.mkdir(parents=True)
    (synthetic_skill_dir / "SKILL.md").write_text("# synthetic-skill", encoding="utf-8")

    # Synthetic home-dir plugin fixture
    plugin_cache_dir = tmp_path / ".codex" / "plugins" / "cache" / "synthetic-cache" / "synthetic-plugin"
    plugin_cache_dir.mkdir(parents=True)

    skill_files = module._discover_skill_files(REPO_ROOT)
    plugin_list = module._plugin_inventory()

    found_synthetic_skill = any("synthetic-skill" in str(p) for p in skill_files)
    assert found_synthetic_skill, f"Opt-in must scan home-dir skills; got {[str(p) for p in skill_files]}"

    assert "synthetic-plugin" in plugin_list, f"Opt-in must scan home-dir plugin cache; got {plugin_list}"


def test_startup_payload_marks_user_extension_discovery_state(monkeypatch) -> None:
    """Regression test for bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28.

    Per Codex GO -004 condition 3: when opt-in discovery is active, startup
    output must make that visible with a concise marker. The model exposes
    a 'user_extension_discovery' field; default = 'default_root_contained',
    opt-in = 'opt_in_active'.
    """
    module = _load_module()

    monkeypatch.delenv("GTKB_DISCOVER_USER_EXTENSIONS", raising=False)
    default_model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    assert default_model.get("user_extension_discovery") == "default_root_contained"

    monkeypatch.setenv("GTKB_DISCOVER_USER_EXTENSIONS", "1")
    opt_in_model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    assert opt_in_model.get("user_extension_discovery") == "opt_in_active"


def test_startup_report_treats_first_owner_message_as_session_start_stimulus() -> None:
    module = _load_module()

    prime_model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    prime_report = module.render_report(
        prime_model,
        "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard",
        REPO_ROOT,
    )

    assert "### Fresh-Session Input Semantics" not in prime_report
    assert "The first owner message in a fresh session is a session-start stimulus only" not in prime_report
    assert "do not interpret it as a focus choice, task prompt, approval, answer" not in prime_report
    assert "wait for Mike's next message before choosing or mapping session work" not in prime_report

    prime_context = module._startup_service_context({"report_text": prime_report, "model": prime_model})
    assert "## Session Startup Instructions" in prime_context
    assert "### Fresh-Session Input Semantics" in prime_context
    assert "### Codex Operating Resource Map" in prime_context
    assert "role records may be list-valued role sets" in prime_context
    assert "read `bridge/INDEX.md` directly before bridge queue claims" in prime_context
    assert "routes the first owner message through the init-keyword matcher" in prime_context
    assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in prime_context
    assert "on no-match, process the prompt as normal task content" in prime_context
    assert "wait for Mike's next message before choosing or mapping session work" in prime_context
    assert prime_context.index("## Session Startup Instructions") < prime_context.index(
        "## User-Visible Startup Message"
    )
    prime_user_visible = prime_context.split("## User-Visible Startup Message", 1)[1]
    assert "### Fresh-Session Input Semantics" not in prime_user_visible
    assert "The first owner message in a fresh session is a session-start stimulus only" not in prime_user_visible

    loyal_model = module.build_startup_model(REPO_ROOT, role_profile="loyal-opposition")
    loyal_report = module.render_report(
        loyal_model,
        "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard",
        REPO_ROOT,
    )

    assert "### Fresh-Session Input Semantics" not in loyal_report
    assert "The first owner message in a fresh session is a session-start stimulus only" not in loyal_report
    assert "execute the harness-only Loyal Opposition startup action before ordinary task work" not in loyal_report
    assert "wait for Mike's next message before choosing or mapping session work" not in loyal_report

    loyal_context = module._startup_service_context({"report_text": loyal_report, "model": loyal_model})
    assert "## Session Startup Instructions" in loyal_context
    assert "### Fresh-Session Input Semantics" in loyal_context
    assert "routes the first owner message through the init-keyword matcher" in loyal_context
    assert "DCL-SESSION-START-INIT-KEYWORD-MATCHING-001" in loyal_context
    assert "execute the harness-only Loyal Opposition startup action before ordinary task work" in loyal_context
    loyal_user_visible = loyal_context.split("## User-Visible Startup Message", 1)[1]
    assert "### Fresh-Session Input Semantics" not in loyal_user_visible
    assert "The first owner message in a fresh session is a session-start stimulus only" not in loyal_user_visible
    assert (
        "execute the harness-only Loyal Opposition startup action before ordinary task work" not in loyal_user_visible
    )


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

    report = module.render_report(model, "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard", REPO_ROOT)
    assert "### Session Overlay Status (Non-Authoritative)" not in report
    assert "non-authoritative by construction" not in report
    assert "no current session overlay" not in report

    context = module._startup_service_context({"report_text": report, "model": model})
    assert "## Session Startup Instructions" in context
    assert "### Session Overlay Status (Non-Authoritative)" in context
    assert "non-authoritative by construction" in context
    assert context.index("### Session Overlay Status (Non-Authoritative)") < context.index(
        "### Fresh-Session Input Semantics"
    )
    assert context.index("## Session Startup Instructions") < context.index("## User-Visible Startup Message")
    user_visible_context = context.split("## User-Visible Startup Message", 1)[1]
    assert "### Session Overlay Status (Non-Authoritative)" not in user_visible_context
    assert "non-authoritative by construction" not in user_visible_context
    assert "no current session overlay" not in user_visible_context


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

    model = module.build_startup_model(REPO_ROOT, role_profile="loyal-opposition", harness_name="claude")
    report = module.render_report(model, "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard", REPO_ROOT)

    assert model["role"]["assumed_role"] == "Loyal Opposition"
    assert (
        model["role"]["role_assignment"]
        == "active AI harness assigned by owner through single role map entry for harness `B`"
    )
    assert model["role"]["bridge"] == "always available through bridge/INDEX.md and checked at session startup"
    assert "cross-harness event-driven trigger" in model["role"]["bridge_dispatch"]
    assert "retired smart poller and OS poller remain archived" in model["role"]["bridge_dispatch"]
    assert model["role"]["role_mapping_source"] == "harness-state/role-assignments.json"
    assert model["role"]["harness_id"] == "B"
    assert "## Loyal Opposition Startup Task" not in report
    assert "## Session Startup" not in report
    assert "### Project State Rollup" in report
    assert "MemBase table: current_work_items" in report
    assert "active projects:" in report
    assert "Strategic self-improvement directive" in report
    assert "review/consideration backlog items" in report
    assert "in MemBase, not MEMORY.md" in report
    assert "implementation-approved backlog items require AskUserQuestion evidence" in report
    assert "presenting insight/options" in report
    assert "AskUserQuestion approval before implementation proposal work" in report
    assert "Commit and push to GitHub" not in report
    assert "Default session purpose: process Prime Builder reviews and verifications on the file bridge." not in report
    assert "Session-focus menu: not presented in Loyal Opposition mode" not in report
    assert "Bridge/poller distinction: the file bridge is the durable role handoff and review mechanism" not in report
    assert (
        "Bridge startup rule: check the file bridge in both Prime Builder and Loyal Opposition startup." not in report
    )
    assert "current bridge state must be determined only from a fresh read of live `bridge/INDEX.md`" not in report
    assert (
        "Mandatory direct-read rule: before reporting the live bridge scan count, read `bridge/INDEX.md` directly"
        not in report
    )
    assert (
        "startup reports, dashboard JSON, cached documents, copied excerpts, summary counts, or hook-generated summaries"
        not in report
    )
    assert "do not display this checklist as a substitute for performing the verification" not in report
    assert "Bridge dispatch startup rule: rely on the cross-harness event-driven trigger" not in report
    assert "First task: verify that the Prime Builder / Loyal Opposition file bridge is functioning." not in report
    assert "permanent owner permission to diagnose and repair bridge function/use" not in report
    assert (
        "report the live scan result and ask Mike whether to begin processing reviews and verifications" not in report
    )

    context = module._startup_service_context({"report_text": report, "model": model})
    assert "## Harness-Only Loyal Opposition Startup Action" in context
    assert "Do not relay this section to Mike as user-visible startup content." in context
    assert "Default session purpose: process Prime Builder reviews and verifications on the file bridge." in context
    assert (
        "Mandatory direct-read rule: before reporting the live bridge scan count, read `bridge/INDEX.md` directly"
        in context
    )
    assert "Project-state startup rule: include a compact current-state report" in context
    assert context.index("## Harness-Only Loyal Opposition Startup Action") < context.index(
        "## User-Visible Startup Message"
    )
    assert "Bridge operation instructions: Bridge automation has two complementary axes" in context
    assert "DISPATCHABLE WORK" in context
    assert "NON-DISPATCHABLE WORK" in context
    assert "Both axes are required" in context
    assert "Do NOT create new bridge automations" in context
    user_visible_context = context.split("## User-Visible Startup Message", 1)[1]
    assert "## Loyal Opposition Startup Task" not in user_visible_context
    assert "### Project State Rollup" in user_visible_context
    assert (
        "Default session purpose: process Prime Builder reviews and verifications on the file bridge."
        not in user_visible_context
    )


def test_project_state_rollup_groups_active_membase_projects() -> None:
    module = _load_module()

    rollup = module._project_state_rollup(
        [
            {
                "id": "WI-1",
                "project_name": "GTKB-A",
                "title": "Second item",
                "resolution_status": "open",
                "priority": "P2",
                "implementation_order": 20,
            },
            {
                "id": "WI-2",
                "project_name": "GTKB-A",
                "title": "First item",
                "resolution_status": "in_progress",
                "priority": "P0",
                "implementation_order": 1,
            },
            {
                "id": "WI-3",
                "project_name": "GTKB-B",
                "title": "Single item",
                "resolution_status": "deferred",
                "priority": "low",
                "implementation_order": None,
            },
            {
                "id": "WI-4",
                "project_name": "GTKB-C",
                "title": "Done item",
                "resolution_status": "resolved",
                "priority": "P0",
                "implementation_order": 0,
            },
            {
                "id": "WI-5",
                "project_name": "",
                "title": "Ungrouped item",
                "resolution_status": "open",
                "priority": "P1",
                "implementation_order": 2,
            },
        ]
    )

    assert rollup["source"] == "MemBase table: current_work_items"
    assert rollup["total_current_work_items"] == 5
    assert rollup["non_terminal_work_items"] == 4
    assert rollup["active_project_count"] == 2
    assert rollup["ungrouped_non_terminal_count"] == 1
    assert [project["project"] for project in rollup["projects"]] == ["GTKB-A", "GTKB-B"]
    assert rollup["projects"][0]["top_id"] == "WI-2"

    rendered = module._render_project_state_rollup({"metrics": {"membase": {"project_state_rollup": rollup}}})
    assert "Current work items: 5; non-terminal: 4; active projects: 2" in rendered
    assert "`GTKB-A`: 2 non-terminal" in rendered
    assert "top: `WI-2` - First item [in_progress, P0, order 1]." in rendered


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
    assert contention["raw_prime_response_queue_count"] == 0
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
    assert contention["raw_prime_response_queue_count"] == 1
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
    assert result["dashboard_url"] == "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
    assert not legacy_static_dashboard.exists()
    assert data.is_file()
    assert report.is_file()
    assert wrapup.is_file()
    assert history_path.is_file()
    assert pdf.name == "groundtruth-kb-project-dashboard.pdf"
    assert result["pdf_export"]["available"] is False
    assert result["pdf_export"]["error"] == "Static dashboard PDF export is disabled."

    dashboard_json = json.loads(dashboard.read_text(encoding="utf-8"))
    report_text = report.read_text(encoding="utf-8")
    wrapup_text = wrapup.read_text(encoding="utf-8")
    dashboard_data = json.loads(data.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))

    panel_titles = set(_panel_titles(dashboard_json["panels"]))
    assert dashboard_json["title"] == "GroundTruth-KB Dashboard"
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
    assert "Bridge dispatch: cross-harness event-driven trigger registered as PostToolUse and Stop hooks" in report_text
    assert "Bridge operation instructions: Bridge automation has two complementary axes" in report_text
    assert "DISPATCHABLE WORK" in report_text
    assert "NON-DISPATCHABLE WORK" in report_text
    assert "Both axes are required" in report_text
    assert "Do NOT create new bridge automations" in report_text
    assert "scripts/cross_harness_bridge_trigger.py" in report_text
    assert "retired smart poller and OS poller remain archived" in report_text
    assert "Startup Disclosure" in report_text
    assert "Strategic self-improvement directive" in report_text
    assert "review/consideration backlog items" in report_text
    assert "in MemBase, not MEMORY.md" in report_text
    assert "implementation-approved backlog items require AskUserQuestion evidence" in report_text
    assert "presenting insight/options" in report_text
    assert "AskUserQuestion approval before implementation proposal work" in report_text
    assert "GroundTruth-KB Project Dashboard" in report_text
    assert "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard" in report_text
    assert "Browser opening: use the harness-controlled browser" in report_text
    assert "system_default_browser" in report_text
    assert "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard" in wrapup_text
    assert str(dashboard.resolve()) not in report_text
    assert "file:///" not in report_text
    assert "file:///" not in wrapup_text
    assert "Dashboard scope:" in report_text
    assert "Current Project State" in report_text
    assert "GT-KB release blockers:" in report_text
    assert "Bridge role slot:" in report_text
    assert "Harness topology:" in report_text
    assert "Testing/tool rollup:" in report_text
    assert "GT-KB dev environment inventory:" in report_text
    assert "Harness parity:" in report_text
    assert "Active Work Subject" in report_text
    assert "Default work subject: GT-KB Infrastructure Focus" in report_text
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
    assert "Session Startup" in report_text
    assert "Recommended Session Focus" in report_text
    assert "Reply with A, B, C, D" in report_text
    assert "Optimize Startup Token Consumption" in report_text
    assert "Top Priority Actions" in report_text
    assert "GTKB-GOV-006" not in report_text
    assert "GTKB-GOV-007" not in report_text
    top_action_ids = [item["id"] for item in dashboard_data["model"]["top_priority_actions"]]
    assert top_action_ids
    for action_id in top_action_ids:
        assert action_id in report_text
    assert "Evidence:" in report_text
    assert "Expected work:" in report_text
    assert "Resolve Release Blockers" in report_text
    assert "Repair Testing/Tool Integrations" in report_text
    assert "Remediate Known Risks" in report_text
    assert "Clear Stage/Test Release Path" in report_text
    assert "Continue Last Session" in report_text
    assert "Clean For Internal Review" in report_text
    assert "Pick From Standing Backlog" in report_text
    assert "D. **Full Focus List**" in report_text
    assert "   - Commit and push to GitHub" in report_text
    assert "   - Merge to main, build and push to the staging environment" in report_text
    assert "   - Execute end-to-end tests in the staging environment" in report_text
    assert "   - Push staged-and-tested build to production, then smoke test" in report_text
    assert "   - Continue Last Session" in report_text
    assert "Or provide a prompt for something else." in report_text
    assert "Startup Focus Input Gate" not in report_text
    assert "Skills, Plug-ins, Directives, And Hooks" not in report_text
    assert report_text.index("## Startup Disclosure") < report_text.index("## Session Startup")
    assert "Proactive Session Wrap-Up" in wrapup_text
    assert "should not have to explicitly instruct GT-KB" in wrapup_text
    assert ".claude/skills/kb-session-wrap/SKILL.md" in wrapup_text
    assert "Suggested Next User Actions" in wrapup_text
    assert "Safe automatic action" in wrapup_text
    assert dashboard_data["history"]
    assert dashboard_data["model"]["dashboard_requirements"]["scope_version"] == "gtkb_v1"
    intelligence = dashboard_data["model"]["dashboard_intelligence"]
    assert intelligence["health"]
    assert intelligence["action_center"]
    assert intelligence["release_readiness"]["release_gate_script"] == "scripts/release_candidate_gate.py"
    assert intelligence["quality_rollup"]["total"] >= 1
    assert intelligence["data_freshness"]["scope_version"] == "gtkb_v1"
    assert "docs/release/dev-environment-inventory.json" in intelligence["data_freshness"]["sources"]
    assert any(shortcut["label"] == "Open GitHub Actions" for shortcut in intelligence["shortcuts"])
    assert any(shortcut["label"] == "Open dev environment inventory" for shortcut in intelligence["shortcuts"])
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
    # Per S330 Slice 8.6 row-24 fix: history may contain `gtkb_inferred`
    # rows (back-fill from MemBase version history of past days) AND/OR
    # `gtkb_current_heuristic` rows (the current snapshot). In CI's clean
    # environment the seeded MemBase records all carry today's
    # `changed_at`, so back-fill produces no rows < today; the only
    # history row is the current snapshot tagged
    # `gtkb_current_heuristic`. Locally where the DB has multi-day
    # history, both tags appear. The assertion the test cares about is
    # that scope_confidence is set on every row.
    assert all(
        row.get("scope_confidence") in ("gtkb_inferred", "gtkb_current_heuristic") for row in dashboard_data["history"]
    )
    assert all(row["scope_version"] == "gtkb_v1" for row in dashboard_data["history"])
    assert history[-1]["token_measurement_status"]
    assert history[-1]["scope_version"] == "gtkb_v1"


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
    assert "GroundTruth-KB Project Dashboard" in context
    assert "Browser opening: use the harness-controlled browser" in context
    assert "### Current Project State" in context
    assert "GT-KB release blockers:" in context
    assert "### Active Work Subject" in context
    assert "Default work subject: GT-KB Infrastructure Focus" in context
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
    assert "## Session Startup" in context
    assert "### Recommended Session Focus" in context
    assert "Optimize Startup Token Consumption" in context
    assert "Top Priority Actions" in context
    assert "GTKB-GOV-006" not in context
    assert "GTKB-GOV-007" not in context
    assert "Evidence:" in context
    assert "Expected work:" in context
    assert "Resolve Release Blockers" in context
    assert "Continue Last Session" in context
    assert "D. **Full Focus List**" in context
    assert "   - Commit and push to GitHub" in context
    assert "   - Push staged-and-tested build to production, then smoke test" in context
    assert "   - Continue Last Session" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Session Startup")


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
    assert "gtkb-startup-service-v2" in context
    assert (
        "User-visible startup content below was generated programmatically by the startup service and cached for lazy injection."
        in context
    )
    assert "relay the generated startup message verbatim as the first durable assistant answer" not in context
    assert "Do not summarize, paraphrase, shorten, reorder, or omit any startup section" in context
    assert (
        "Preserve every generated heading, bullet, A/B/C/D option, `Evidence`, `Expected work`, and compact full-list label"
        in context
    )
    assert "the A/B/C recommendations and D full focus list must remain present" in context
    assert "routes the first owner message through the init-keyword matcher" in context
    assert "The startup disclosure is generated at SessionStart time and cached for lazy injection" in context
    assert "Only an init-keyword match relays startup disclosure" in context
    assert "a non-matching first owner message is ordinary task input and may be mapped normally" in context
    assert "Codex Desktop durability rule" not in context
    assert "first durable assistant answer" not in context
    assert "not in transient progress/intermediary output" not in context
    assert "When the init-keyword path renders cached startup content" in context
    assert "do not replace the startup message with a shorter final answer" in context
    assert "The AI harness is not responsible for composing role, mode, bridge, process, or focus content" in context
    assert "## User-Visible Startup Message" in context
    assert "## Startup Disclosure" in context
    assert "## Session Startup" in context
    assert "D. **Full Focus List**" in context
    assert "   - Continue Last Session" in context
    assert "Startup First-Response Directive" not in context
    assert "Mandatory Direct Live Bridge Index Read" not in context
    assert "SHA-256:" not in context
    assert freshness["contract_version"] == "gtkb-startup-freshness-v1"
    assert freshness["request_started_at"] == "2026-04-23T13:20:00Z"
    assert freshness["report_origin"] == "in_memory_model_render"
    assert freshness["validation"]["startup_payload_fresh"] is True
    assert freshness["validation"]["status"] in {"fresh", "fresh_with_gaps"}
    assert freshness["required_local_sources"]
    assert any(item["source"] == "bridge/INDEX.md" for item in freshness["required_local_sources"])
    assert any(item["source"] == "GitHub Actions via gh" for item in freshness["live_probes"])
    assert freshness["repo"]["sha"]


def test_startup_payload_tests_do_not_touch_live_lifecycle_guards(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    live_guard_paths = [
        REPO_ROOT / "harness-state" / "codex" / "session-lifecycle-guard.json",
        REPO_ROOT / "harness-state" / "claude" / "session-lifecycle-guard.json",
    ]
    before = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in live_guard_paths}
    sandbox_guard = Path(os.environ["GTKB_LIFECYCLE_GUARD_PATH"])
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
            "--emit-startup-service-payload",
            "--fast-hook",
            "--skip-bridge-maintenance",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert sandbox_guard.exists()
    after = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in live_guard_paths}
    assert after == before


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
    assert "## Session Startup" in context
    assert "## Loyal Opposition Startup Task" not in context


def test_claude_code_startup_discovers_durable_role_without_forced_profile(tmp_path, capsys, monkeypatch) -> None:
    module = _load_module()
    discovered_role = module.discover_role_profile(REPO_ROOT, harness_name="claude")
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
    assert all("--harness-id B" not in command for command in session_commands)
    assert any("--harness-name claude" in command for command in stop_commands)
    assert all("--harness-id B" not in command for command in stop_commands)
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
    assert "Bridge dispatch: cross-harness event-driven trigger registered as PostToolUse and Stop hooks" in context
    assert "Bridge operation instructions: Bridge automation has two complementary axes" in context
    assert "DISPATCHABLE WORK" in context
    assert "NON-DISPATCHABLE WORK" in context
    assert "Both axes are required" in context
    assert "Do NOT create new bridge automations" in context
    assert "scripts/cross_harness_bridge_trigger.py" in context
    assert "retired smart poller and OS poller remain archived" in context
    assert "Role mapping source: harness-state/role-assignments.json" in context
    assert "Harness self-identification: B" in context
    assert "Harness identity source: harness-state/harness-identities.json" in context
    if discovered_role == "loyal-opposition":
        if "## User-Visible Startup Message" in context:
            assert "## Harness-Only Loyal Opposition Startup Action" in context
            user_visible_context = context.split("## User-Visible Startup Message", 1)[1]
            assert "## Loyal Opposition Startup Task" not in user_visible_context
        else:
            assert "## Harness-Only Loyal Opposition Startup Action" not in context
        assert "## Session Startup" not in context
        assert "Commit and push to GitHub" not in context
        assert guard_path.exists()
        guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
        assert guard_state["discard_next_user_prompt"] is True
        assert guard_state["suppress_next_wrapup"] is False
    else:
        assert "## Loyal Opposition Startup Task" not in context
        assert "## Session Startup" in context
        assert "   - Commit and push to GitHub" in context
        assert "   - Continue Last Session" in context
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
    assert "GroundTruth-KB Project Dashboard" in context
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
    assert "Default work subject: GT-KB Infrastructure Focus" in context
    assert "### Wrap-Up Trigger Commands" in context
    assert "Accepted wrap-up commands:" in context
    assert "### File Bridge Scan" not in context
    assert "## Token Consumption Reduction Options" not in context
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in context
    assert "## Three Top Priority Actions" not in context
    assert "Would you like to proceed with established priority actions? (Y/N)" not in context
    assert "## Session Startup" in context
    assert "Optimize Startup Token Consumption" in context
    assert "Top Priority Actions" in context
    assert "GTKB-GOV-006" not in context
    assert "GTKB-GOV-007" not in context
    assert "Evidence:" in context
    assert "Expected work:" in context
    assert "Continue Last Session" in context
    assert "D. **Full Focus List**" in context
    assert "   - Commit and push to GitHub" in context
    assert "   - Push staged-and-tested build to production, then smoke test" in context
    assert "   - Continue Last Session" in context
    assert "Or provide a prompt for something else." in context
    assert "## Startup Focus Input Gate" not in context
    assert "## Skills, Plug-ins, Directives, And Hooks" not in context
    assert context.index("## Startup Disclosure") < context.index("## Session Startup")
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert history
    assert all(row["scope_confidence"] != "gtkb_inferred" for row in history)


def test_top_priority_actions_come_from_standing_backlog() -> None:
    module = _load_module()

    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder")
    action_ids = [item["id"] for item in model["top_priority_actions"]]
    _, expected_top_actions = module._backlog_metrics(REPO_ROOT)
    expected_action_ids = [item["id"] for item in expected_top_actions]

    # Per S330 Slice 8.6 row-36 fix: assert top-priority discipline rather than
    # exact list equality. Production code returns visible_items[:3] from the
    # standing backlog (scripts/session_self_initialization.py:934). The test
    # should not pin whichever item is currently first in that governed list;
    # it should pin the invariants: actions come from active standing-backlog
    # ordering, historically-closed items don't reappear, and the cap is 3.
    assert action_ids == expected_action_ids
    assert len(action_ids) <= 3, f"top_priority_actions must cap at 3 (visible_items[:3]); got {action_ids}"
    assert "GTKB-ISOLATION-007" not in action_ids
    assert "GTKB-GOV-012" not in action_ids
    assert "GTKB-GOV-007" not in action_ids
    assert "GTKB-GOV-002" not in action_ids
    assert "GTKB-GOV-006" not in action_ids


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
    assert "gtkb-startup-service-v2" in hook_output["additionalContext"]


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
    then reads what the writer wrote — no synthetic fixture JSON.
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
    role_map = tmp_path / "role-assignments.json"
    role_map.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"harness_type": "codex", "role": "loyal-opposition"},
                    "B": {"harness_type": "claude", "role": "prime-builder"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

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
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    monkeypatch.setattr(
        focus_module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    focus_module.save_state(focus_module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = focus_module.detect_counterpart_state()
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
# Smart-poller orient section retirement (Slice 4, 2026-05-09)
# The smart-poller mechanism was retired; _render_smart_poller_section
# is now a stub returning []. Bridge dispatch is governed by the
# cross-harness event-driven trigger.
# =====================================================================


def test_smart_poller_section_returns_empty_after_retirement(tmp_path) -> None:
    """Post-Slice-4: ``_render_smart_poller_section`` is unconditionally empty.

    The smart-poller runtime was archived to ``archive/smart-poller-2026-05-09/``
    in Slice 4 D1; the orient-renderer helper now returns ``[]`` regardless of
    role, project state, or doctor verdict. This test pins that contract.
    """
    module = _load_module()
    for role_name in ("Prime Builder", "Loyal Opposition", "Some Other Role"):
        role = {"assumed_role": role_name}
        assert module._render_smart_poller_section(tmp_path, role) == [], (
            f"_render_smart_poller_section must be empty for role {role_name!r} post-Slice-4 retirement"
        )


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
    (fake_root / "harness-state").mkdir()
    (fake_root / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"A": {"harness_type": "codex", "role": "prime-builder"}},
            }
        )
        + "\n",
        encoding="utf-8",
    )

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


def test_user_preferences_path_cli_arg_sets_env_when_unset(tmp_path, monkeypatch) -> None:
    """Per bridge/harness-state-preferences-path-cli-2026-04-28-002.md Codex GO condition 1+3.

    --user-preferences-path must affect the generator's preference reader.
    Candidate B implementation bridges the CLI arg into the
    GTKB_STARTUP_PREFERENCES_PATH env var via os.environ.setdefault, so
    _user_startup_preferences_path() returns the CLI-supplied value when
    no pre-existing env var is set.

    The setdefault mutation bypasses monkeypatch's auto-restore tracking, so
    the test uses a try/finally to clean up the env var explicitly after
    the assertion.
    """
    monkeypatch.delenv("GTKB_STARTUP_PREFERENCES_PATH", raising=False)
    project_root = tmp_path / "project"
    project_root.mkdir()
    cli_pref_path = tmp_path / "sandbox-prefs.json"

    module = _load_module()
    try:
        module.main(
            [
                "--project-root",
                str(project_root),
                "--dashboard-dir",
                str(tmp_path / "out_dash"),
                "--history-path",
                str(tmp_path / "out_history.json"),
                "--user-preferences-path",
                str(cli_pref_path),
                "--harness-name",
                "claude",
                "--skip-bridge-maintenance",
                "--fast-hook",
            ]
        )

        resolved_path = module._user_startup_preferences_path()
        assert resolved_path == cli_pref_path.resolve()
    finally:
        os.environ.pop("GTKB_STARTUP_PREFERENCES_PATH", None)


def test_user_preferences_path_existing_env_var_wins_over_cli(tmp_path, monkeypatch) -> None:
    """Per bridge/harness-state-preferences-path-cli-2026-04-28-002.md GO condition 2.

    Existing GTKB_STARTUP_PREFERENCES_PATH env var must take precedence over
    the CLI argument. Implementation uses os.environ.setdefault, which only
    sets when the key is absent. monkeypatch.setenv tracks and restores the
    env var automatically here.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    pre_existing_pref = tmp_path / "from-env.json"
    cli_pref = tmp_path / "from-cli.json"
    monkeypatch.setenv("GTKB_STARTUP_PREFERENCES_PATH", str(pre_existing_pref))

    module = _load_module()
    module.main(
        [
            "--project-root",
            str(project_root),
            "--dashboard-dir",
            str(tmp_path / "out_dash"),
            "--history-path",
            str(tmp_path / "out_history.json"),
            "--user-preferences-path",
            str(cli_pref),
            "--harness-name",
            "claude",
            "--skip-bridge-maintenance",
            "--fast-hook",
        ]
    )

    # Pre-existing env var unchanged; CLI arg did NOT override it.
    assert os.environ.get("GTKB_STARTUP_PREFERENCES_PATH") == str(pre_existing_pref)
    resolved_path = module._user_startup_preferences_path()
    assert resolved_path == pre_existing_pref


def test_user_preferences_path_omitted_falls_back_to_default(tmp_path, monkeypatch) -> None:
    """Per bridge/harness-state-preferences-path-cli-2026-04-28-002.md GO condition 2.

    When both --user-preferences-path AND GTKB_STARTUP_PREFERENCES_PATH are
    absent, _user_startup_preferences_path() must return the canonical
    DEFAULT_USER_STARTUP_PREFERENCES_PATH (production default preserved).
    """
    monkeypatch.delenv("GTKB_STARTUP_PREFERENCES_PATH", raising=False)
    module = _load_module()

    resolved_path = module._user_startup_preferences_path()
    assert resolved_path == module.DEFAULT_USER_STARTUP_PREFERENCES_PATH


def test_git_checkout_info_returns_degraded_when_outside_project_root(tmp_path, monkeypatch) -> None:
    """Per bridge/generator-hardening-cross-repo-005.md GO conditions.

    GO condition 3: 'The test must prove no git subprocess is spawned for a
    checkout path outside project_root.' Monkeypatch _command_output to fail
    loudly if invoked; the scope-check guard must short-circuit before any
    git call. Verifies the degrade-only contract from the project-root-
    boundary directive (.claude/rules/project-root-boundary.md).
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_checkout = tmp_path / "outside" / "fake-repo"
    outside_checkout.mkdir(parents=True)

    module = _load_module()

    def _fail_on_git(*_args, **_kwargs) -> None:
        raise AssertionError("git subprocess invoked for checkout outside project_root; scope-check guard regressed")

    monkeypatch.setattr(module, "_command_output", _fail_on_git)

    result = module._git_checkout_info(outside_checkout, project_root)

    assert result["available"] is False, "outside-root checkout must report unavailable"
    assert result["error"] == "checkout_outside_project_root"
    assert "scope_diagnostic" in result
    assert "outside" in result["scope_diagnostic"].lower()


def test_session_self_initialization_writes_session_start_json(tmp_path) -> None:
    """Per Slice A of GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY (bridge -006 GO):
    SessionStart writes ``.claude/session/session-start.json`` so the
    spec-event-surfacer hook has a per-session timestamp lower bound.
    """
    module = _load_module()

    request_started_at = "2026-04-29T18:30:00.000000+00:00"
    module._write_session_start_json(
        project_root=tmp_path,
        request_started_at=request_started_at,
        harness="test-harness",
    )

    target = tmp_path / ".claude" / "session" / "session-start.json"
    assert target.exists(), "session-start.json must be written by the writer"
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["session_started_at"] == request_started_at
    assert payload["harness"] == "test-harness"
    assert "session_id" in payload


def test_write_session_start_json_handles_filesystem_errors_gracefully(tmp_path, monkeypatch) -> None:
    """Per F2 fix: graceful degradation. The surfacer's now() - 1 hour
    fallback is the safety net when the writer fails."""
    module = _load_module()

    # Point at a path that cannot be created (e.g., a file masquerading as dir)
    blocker = tmp_path / "blocker"
    blocker.write_text("not-a-directory", encoding="utf-8")
    fake_root = blocker  # using a regular file as project_root will make .claude/session/ creation fail

    # Should NOT raise
    module._write_session_start_json(
        project_root=fake_root,
        request_started_at="2026-04-29T18:30:00.000000+00:00",
        harness="test",
    )

    # File doesn't exist (write failed gracefully)
    target = fake_root / ".claude" / "session" / "session-start.json"
    assert not target.exists()


# ---------------------------------------------------------------------------
# Tests for GTKB-STARTUP-PRIORITY-RECOMMENDER-DEFECT-001 Slice 1
# Bridge GO at bridge/gtkb-startup-priority-recommender-defect-001-002.md
# ---------------------------------------------------------------------------


def _make_recommender_fixture(tmp_path, work_list_text: str, index_text: str) -> Path:
    """Build a synthetic project root with memory/work_list.md and bridge/INDEX.md."""
    (tmp_path / "memory").mkdir(parents=True, exist_ok=True)
    (tmp_path / "memory" / "work_list.md").write_text(work_list_text, encoding="utf-8")
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / "bridge" / "INDEX.md").write_text(index_text, encoding="utf-8")
    return tmp_path


def test_recommender_1_top_priority_excludes_verified_bridge_thread(tmp_path) -> None:
    """T-recommender-1: items whose mapped bridge thread is VERIFIED are filtered."""
    module = _load_module()
    work_list = (
        "## Active Items\n\n"
        "### GTKB-SHIPPED-ITEM-001 - Already shipped\n\n"
        "Body of done item.\n\n"
        "### GTKB-ACTIVE-ITEM-002 - Still in flight\n\n"
        "Body of active item.\n\n"
        "### GTKB-ACTIVE-ITEM-003 - Also in flight\n\n"
        "Body of third item.\n\n"
    )
    index = (
        "Document: gtkb-shipped-item-001\n"
        "VERIFIED: bridge/gtkb-shipped-item-001-004.md\n\n"
        "Document: gtkb-active-item-002\n"
        "GO: bridge/gtkb-active-item-002-002.md\n"
    )
    root = _make_recommender_fixture(tmp_path, work_list, index)
    module.classify_dashboard_scope = lambda row: "gtkb"
    module.AGENT_RED_PRIMARY_SCOPE_INCLUDED = {"gtkb"}
    module.AGENT_RED_SCOPE_INCLUDED = {"gtkb"}

    metrics, top = module._backlog_metrics(root)
    top_ids = [item["id"] for item in top]
    assert "GTKB-SHIPPED-ITEM-001" not in top_ids
    assert "GTKB-ACTIVE-ITEM-002" in top_ids
    assert "GTKB-ACTIVE-ITEM-003" in top_ids
    assert metrics["filtered_verified_ids"] == ["GTKB-SHIPPED-ITEM-001"]


def test_recommender_2_work_item_id_maps_to_bridge_document_name() -> None:
    """T-recommender-2: deterministic lowercase mapping."""
    module = _load_module()
    assert module._work_item_id_to_bridge_document("GTKB-ENV-INVENTORY-001") == "gtkb-env-inventory-001"
    assert (
        module._work_item_id_to_bridge_document("GTKB-SYSTEMS-TERMINOLOGY-MAP-001")
        == "gtkb-systems-terminology-map-001"
    )
    assert module._work_item_id_to_bridge_document("AGENT-RED-RUFF-CLEANUP-001") == "agent-red-ruff-cleanup-001"


def test_recommender_3_unmapped_work_item_treated_as_active(tmp_path) -> None:
    """T-recommender-3: items with no matching bridge Document remain eligible."""
    module = _load_module()
    work_list = "## Active Items\n\n### GTKB-NO-BRIDGE-001 - Item without a bridge thread\n\nBody.\n\n"
    index = "Document: gtkb-other-thread\nGO: bridge/gtkb-other-thread-002.md\n"
    root = _make_recommender_fixture(tmp_path, work_list, index)
    module.classify_dashboard_scope = lambda row: "gtkb"
    module.AGENT_RED_PRIMARY_SCOPE_INCLUDED = {"gtkb"}
    module.AGENT_RED_SCOPE_INCLUDED = {"gtkb"}

    metrics, top = module._backlog_metrics(root)
    assert "GTKB-NO-BRIDGE-001" in [item["id"] for item in top]
    assert metrics["filtered_verified_ids"] == []


def test_recommender_4_residual_override_keeps_verified_item_active(tmp_path) -> None:
    """T-recommender-4: **Status:** VERIFIED (residual: ...) marker keeps item recommended."""
    module = _load_module()
    work_list = (
        "## Active Items\n\n"
        "### GTKB-VERIFIED-WITH-RESIDUAL-001 - Verified but residual work\n\n"
        "**Status:** VERIFIED (residual: SonarCloud URL still unverified)\n\n"
        "Body explaining the residual work.\n\n"
    )
    index = "Document: gtkb-verified-with-residual-001\nVERIFIED: bridge/gtkb-verified-with-residual-001-004.md\n"
    root = _make_recommender_fixture(tmp_path, work_list, index)
    module.classify_dashboard_scope = lambda row: "gtkb"
    module.AGENT_RED_PRIMARY_SCOPE_INCLUDED = {"gtkb"}
    module.AGENT_RED_SCOPE_INCLUDED = {"gtkb"}

    metrics, top = module._backlog_metrics(root)
    assert "GTKB-VERIFIED-WITH-RESIDUAL-001" in [item["id"] for item in top]
    assert metrics["filtered_verified_ids"] == []


def test_recommender_5_index_parser_captures_only_latest_status_per_document(tmp_path) -> None:
    """T-recommender-5: per-document parser returns first (latest) status line only."""
    module = _load_module()
    index = (
        "Document: gtkb-multi-version\n"
        "VERIFIED: bridge/gtkb-multi-version-008.md\n"
        "NEW: bridge/gtkb-multi-version-007.md\n"
        "GO: bridge/gtkb-multi-version-006.md\n"
        "REVISED: bridge/gtkb-multi-version-005.md\n\n"
        "Document: gtkb-no-go-thread\n"
        "NO-GO: bridge/gtkb-no-go-thread-002.md\n"
        "NEW: bridge/gtkb-no-go-thread-001.md\n"
    )
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / "bridge" / "INDEX.md").write_text(index, encoding="utf-8")

    status_map = module._bridge_index_latest_status(tmp_path)
    assert status_map == {
        "gtkb-multi-version": "VERIFIED",
        "gtkb-no-go-thread": "NO-GO",
    }


def test_recommender_6_live_regression_excludes_known_stale_priorities() -> None:
    """T-recommender-6: against the live tree, the two known-stale VERIFIED items
    must not appear in top_priority_actions. Per Codex GO -002 condition 1 and 5.
    """
    module = _load_module()
    repo_root = REPO_ROOT
    metrics, top = module._backlog_metrics(repo_root)
    top_ids = [item["id"] for item in top]
    # The session that motivated this work observed both these items in the
    # top_priority_actions surface despite being VERIFIED at -004 on 2026-05-06.
    # The fix must drop them.
    assert "GTKB-SYSTEMS-TERMINOLOGY-MAP-001" not in top_ids, (
        f"systems-terminology-map (VERIFIED 2026-05-06) leaked into top_priority_actions={top_ids}; "
        f"filtered_verified_ids={metrics.get('filtered_verified_ids')}"
    )
    assert "GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001" not in top_ids, (
        f"resource-reference-disambiguation (VERIFIED 2026-05-06) leaked into top_priority_actions={top_ids}"
    )


# ---------------------------------------------------------------------------
# Acting-Prime compatibility contract (T-compat-3, T-compat-4)
# Per bridge gtkb-role-session-lifecycle-simplification-003.md GO at -004:
#   Slice B/D: startup rendering for the acting-prime-builder profile MUST
#   contain the compatibility/provenance label. ROLE_PROFILES enumeration
#   retains the profile for backward-compat readability.
# ---------------------------------------------------------------------------


def test_t_compat_3_acting_prime_profile_renders_compatibility_label() -> None:
    """T-compat-3: ROLE_PROFILES['acting-prime-builder']['assumed_role'] +
    'role_assignment' fields contain the compatibility/provenance label.

    Linked spec: GOV-SESSION-SELF-INITIALIZATION-001 (correct disclosure).
    """
    module = _load_module()
    profile = module.ROLE_PROFILES["acting-prime-builder"]
    assert "compatibility/provenance" in profile["assumed_role"], (
        "acting-prime-builder profile 'assumed_role' must contain the "
        "'compatibility/provenance' label so startup rendering surfaces the "
        "legacy/compatibility framing per the Acting-Prime Compatibility Contract."
    )
    assert "compatibility" in profile["role_assignment"].lower(), (
        "acting-prime-builder profile 'role_assignment' must reference the compatibility framing."
    )
    assert "not a new role-switch target" in profile["role_assignment"].lower(), (
        "acting-prime-builder profile must clarify it is not a role-switch target."
    )


def test_t_compat_4_role_profiles_enumeration_retains_acting_prime_builder() -> None:
    """T-compat-4: ROLE_PROFILES enumeration retains the acting-prime-builder
    profile (loadable and references the rule file).

    Linked spec: GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 (install-time profile set).
    """
    module = _load_module()
    assert "acting-prime-builder" in module.ROLE_PROFILES, (
        "ROLE_PROFILES must retain the acting-prime-builder entry for "
        "backward compatibility with prior session role-map values."
    )
    profile = module.ROLE_PROFILES["acting-prime-builder"]
    assert profile["role_mapping_source"] == ".claude/rules/acting-prime-builder.md", (
        "acting-prime-builder profile must continue to reference its rule file "
        "for narrative continuity (the rule file is the historical authority "
        "record; the durable role record is harness-state/role-assignments.json)."
    )
