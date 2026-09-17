"""FAB-12 regression checks for Agent Red residue removal from platform surfaces."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _read_toml(relative_path: str) -> dict:
    return tomllib.loads(_read_text(relative_path))


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

    # Owner ruling D2 (2026-09-16): the Agent Red shard workflows are application-owned and retired from the
    # platform repository; the residue check is that none of them exists here any more.
    for retired_workflow in ("python-tests.yml", "accessibility.yml", "visual-regression.yml"):
        assert not (ROOT / ".github" / "workflows" / retired_workflow).exists(), retired_workflow

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
