"""FAB-12 regression checks for Agent Red residue removal from platform surfaces."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _read_toml(relative_path: str) -> dict:
    return tomllib.loads(_read_text(relative_path))


def test_platform_identity_and_memory_authority_are_explicit() -> None:
    config = _read_toml("groundtruth.toml")

    assert config["project"]["project_name"] == "GroundTruth-KB Platform"
    assert config["project"]["profile"] == "dual-agent"
    assert config["scoped_service"]["application_id"] == "agent-red"

    assert _read_text("memory/MEMORY.md").splitlines()[0] == "# GroundTruth-KB Platform Memory"

    claude_text = _read_text("CLAUDE.md")
    memory_line = next(line for line in claude_text.splitlines() if "Platform session memory" in line)
    assert "memory/MEMORY.md" in memory_line
    assert "in-repo GT-KB notepad is authoritative" in memory_line
    assert "home-directory auto-memory is a non-authoritative harness cache" in memory_line
    assert len(claude_text.splitlines()) <= 300


def test_claude_md_narrative_approval_packet_matches_current_file() -> None:
    packet_path = (
        ROOT / ".groundtruth" / "formal-artifact-approvals" / "2026-06-13-claude-md-antigravity-startup-opt-s438.json"
    )
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    claude_text = _read_text("CLAUDE.md")

    assert packet["artifact_type"] == "narrative_artifact"
    assert packet["target_path"] == "CLAUDE.md"
    assert packet["source_ref"] == "owner-AUQ-2026-06-13-S438-antigravity-startup-optimization"
    assert packet["presented_to_user"] is True
    assert packet["transcript_captured"] is True
    assert packet["full_content"] == claude_text
    assert packet["full_content_sha256"] == hashlib.sha256(claude_text.encode("utf-8")).hexdigest()


def test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant() -> None:
    pyproject = _read_toml("pyproject.toml")
    pytest_options = pyproject["tool"]["pytest"]["ini_options"]
    coverage_options = pyproject["tool"]["coverage"]["run"]

    assert "tool" not in pyproject or "mutmut" not in pyproject["tool"]
    assert "tests/**" not in pyproject["tool"]["ruff"]["lint"]["per-file-ignores"]

    for relative_path in pytest_options["testpaths"]:
        assert (ROOT / relative_path).exists(), relative_path
    for relative_path in pytest_options["pythonpath"]:
        assert (ROOT / relative_path).exists(), relative_path

    ignore_paths = re.findall(r"--ignore=([^ ]+)", pytest_options["addopts"])
    for relative_path in ignore_paths:
        assert (ROOT / relative_path).exists(), relative_path

    assert coverage_options["source"] == ["groundtruth-kb/src", "scripts"]
    assert all("applications/Agent_Red" not in relative_path for relative_path in coverage_options["source"])
    for relative_path in coverage_options["source"]:
        assert (ROOT / relative_path).exists(), relative_path

    assert coverage_options["omit"] == [
        "groundtruth-kb/src/**/__init__.py",
        "scripts/**/__init__.py",
    ]
    assert all("applications/Agent_Red" not in relative_path for relative_path in coverage_options["omit"])
    for relative_glob in coverage_options["omit"]:
        root_path = relative_glob.split("/**/", maxsplit=1)[0]
        assert (ROOT / root_path).exists(), relative_glob

    groundtruth_workflow = _read_text(".github/workflows/groundtruth-kb-tests.yml")
    assert "python -m pytest tests/" in groundtruth_workflow
    assert "python -m pytest platform_tests/" not in groundtruth_workflow

    python_workflow = _read_text(".github/workflows/python-tests.yml")
    assert "platform_tests/test_conftest_smoke.py" not in python_workflow
    assert "applications/Agent_Red/tests/test_conftest_smoke.py" in python_workflow

    sonar_workflow = _read_text(".github/workflows/sonarcloud.yml")
    assert 'pip install "./groundtruth-kb[dev,search]" pytest pytest-cov pytest-timeout' in sonar_workflow
    assert "python -m pytest --cov=groundtruth-kb/src --cov=scripts" in sonar_workflow

    sonar_properties = _read_text("sonar-project.properties")
    assert "sonar.tests=groundtruth-kb/tests,platform_tests\n" in sonar_properties
    assert "sonar.tests=groundtruth-kb/tests,platform_tests,tests" not in sonar_properties


def test_dependabot_and_templates_no_longer_point_at_deleted_root_app_dirs() -> None:
    dependabot = _read_text(".github/dependabot.yml")

    assert 'directory: "/widget"' not in dependabot
    assert 'directory: "/admin"' not in dependabot
    for directory in re.findall(r'directory:\s*"([^"]+)"', dependabot):
        assert (ROOT / directory.lstrip("/")).exists(), directory

    bug_template = _read_text(".github/ISSUE_TEMPLATE/bug_report.md")
    feature_template = _read_text(".github/ISSUE_TEMPLATE/feature_request.md")
    pull_request_template = _read_text(".github/pull_request_template.md")

    assert "Widget / Standalone Admin / Shopify Admin" not in bug_template
    assert "GT-KB platform / Agent Red application / Other adopter" in bug_template
    assert "specifications, or bridge threads" in feature_template
    assert "Platform configuration, governance, bridge, dashboard, or workflow change" in pull_request_template


def test_agent_red_tooling_files_live_under_application_scope() -> None:
    moved_files = [
        ".claude/skills/deploy/SKILL.md",
        ".claude/skills/run-tests/SKILL.md",
        ".claude/skills/seed-tenant/SKILL.md",
        ".claude/agents/code-reviewer.md",
        ".claude/agents/security-analyzer.md",
        ".claude/commands/preflight.md",
        ".claude/commands/refresh-creds.md",
        ".claude/commands/check-db.md",
        ".claude/commands/quick-review.md",
        ".claude/commands/check-security.md",
        "scripts/seed_tenant.py",
    ]
    for relative_path in moved_files:
        assert not (ROOT / relative_path).is_file(), relative_path

    app_files = [
        "applications/Agent_Red/.claude/skills/deploy/SKILL.md",
        "applications/Agent_Red/.claude/skills/run-tests/SKILL.md",
        "applications/Agent_Red/.claude/skills/seed-tenant/SKILL.md",
        "applications/Agent_Red/.claude/agents/code-reviewer.md",
        "applications/Agent_Red/.claude/agents/security-analyzer.md",
        "applications/Agent_Red/.claude/commands/preflight.md",
        "applications/Agent_Red/.claude/commands/refresh-creds.md",
        "applications/Agent_Red/.claude/commands/check-db.md",
        "applications/Agent_Red/.claude/commands/quick-review.md",
        "applications/Agent_Red/.claude/commands/check-security.md",
        "applications/Agent_Red/scripts/seed_tenant.py",
    ]
    for relative_path in app_files:
        assert (ROOT / relative_path).is_file(), relative_path

    seed_skill = _read_text("applications/Agent_Red/.claude/skills/seed-tenant/SKILL.md")
    assert "python applications/Agent_Red/scripts/seed_tenant.py $ARGUMENTS" in seed_skill


def test_session_self_initialization_is_subject_gated_for_platform_mode(monkeypatch) -> None:
    session_init = importlib.import_module("scripts.session_self_initialization")
    package_json_calls: list[str] = []

    def fail_on_package_json(_project_root: Path, relative_path: str) -> dict:
        package_json_calls.append(relative_path)
        return {}

    monkeypatch.setattr(
        session_init,
        "_active_work_subject",
        lambda _project_root: session_init.FOCUS_GTKB_INFRASTRUCTURE,
    )
    monkeypatch.setattr(session_init, "_package_json", fail_on_package_json)

    manifest = session_init._current_version_manifest(ROOT)
    integrations = session_init._testing_service_integrations(ROOT, [], fast_hook=True)

    assert manifest["versions"]["groundtruth_kb_package"] == "0.7.0rc1"
    assert not any(key.startswith("agent_red") for key in manifest["versions"])
    assert package_json_calls == []
    assert integrations["github"]["queried_work_subject"] == session_init.FOCUS_GTKB_INFRASTRUCTURE

    metrics = {
        "regression": {"release_blocker_count": 0},
        "contention": {"actionable_count": 0, "raw_advisory_documents": []},
        "drift": {"changed_path_count": 0},
        "work_subject": {"current_subject": session_init.FOCUS_GTKB_INFRASTRUCTURE},
    }
    infrastructure = {
        "testing_service_integrations": {
            "github": {
                "health": "failing",
                "display_name": "GitHub Actions",
                "latest_run_summary": "failing test run",
                "remediation": "rerun",
                "queried_work_subject": session_init.FOCUS_GTKB_INFRASTRUCTURE,
            }
        },
        "gtkb_upgrade_posture": {"upgrade_plan": {"mutating_action_count": 0}},
        "dev_environment_inventory": {"health": "green"},
    }

    dashboard = session_init._dashboard_intelligence(
        project_root=ROOT,
        generated_at="2026-06-12T00:00:00Z",
        metrics=metrics,
        top_actions=[],
        blockers=[],
        infrastructure=infrastructure,
    )

    shortcuts = dashboard["shortcuts"]
    assert any(shortcut["target"].endswith("/groundtruth-kb/actions") for shortcut in shortcuts)
    assert not any(shortcut["target"].endswith("/agent-red-customer-engagement/actions") for shortcut in shortcuts)


def test_hygiene_sweep_scans_root_claude_files_for_agent_red_recurrence() -> None:
    patterns = _read_toml("config/governance/hygiene-sweep-patterns.toml")
    agent_red_pattern = next(pattern for pattern in patterns["patterns"] if pattern["id"] == "agent-red-config-drift")

    assert ".claude/**/*.md" in agent_red_pattern["file_globs"]
    assert ".claude/**/*.json" in agent_red_pattern["file_globs"]
    assert ".claude/**" not in agent_red_pattern["exclusion_globs"]
