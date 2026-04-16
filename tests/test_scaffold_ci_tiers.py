# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for G3 CI template profile-tiering, scaffold stubs, and integrations.

Covers the full test matrix (a through t) from the gtkb-adoption-gap-closure
implementation proposal.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from groundtruth_kb.project.profiles import get_profile
from groundtruth_kb.project.scaffold import (
    ScaffoldOptions,
    _ci_tier,
    _package_name_slug,
    scaffold_project,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scaffold(
    tmp_path: Path,
    profile: str,
    *,
    include_ci: bool = True,
    seed_example: bool = False,
    integrations: bool = False,
    python_version: str = "3.11",
) -> Path:
    """Scaffold a project and return the resolved target path."""
    target = tmp_path / "project"
    options = ScaffoldOptions(
        project_name="My Test Project",
        profile=profile,
        owner="Test Owner",
        target_dir=target,
        include_ci=include_ci,
        seed_example=seed_example,
        integrations=integrations,
        python_version=python_version,
    )
    scaffold_project(options)
    return target.resolve()


def _read_workflow(target: Path, name: str) -> str:
    return (target / ".github" / "workflows" / name).read_text(encoding="utf-8")


def _workflow_exists(target: Path, name: str) -> bool:
    return (target / ".github" / "workflows" / name).exists()


# ---------------------------------------------------------------------------
# a: Generated workflows are valid YAML
# ---------------------------------------------------------------------------


def test_a_generated_workflows_are_valid_yaml(tmp_path: Path) -> None:
    """All generated workflow files parse as valid YAML."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        target = _scaffold(tmp_path / profile, profile)
        workflows = list((target / ".github" / "workflows").glob("*.yml"))
        assert workflows, f"{profile}: no workflows generated"
        for wf in workflows:
            content = wf.read_text(encoding="utf-8")
            parsed = yaml.safe_load(content)
            assert isinstance(parsed, dict), f"{profile}/{wf.name}: not a YAML mapping"


# ---------------------------------------------------------------------------
# b: {{PACKAGE_NAME}} resolves to correct slug
# ---------------------------------------------------------------------------


def test_b_package_name_placeholder_resolved(tmp_path: Path) -> None:
    """{{PACKAGE_NAME}} is replaced with the slug; no literal braces remain."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    for wf in (target / ".github" / "workflows").glob("*.yml"):
        content = wf.read_text(encoding="utf-8")
        assert "{{PACKAGE_NAME}}" not in content, f"{wf.name}: {{PACKAGE_NAME}} not resolved"


def test_b_package_name_slug_helper() -> None:
    """_package_name_slug() produces correct kebab-case."""
    assert _package_name_slug("My Test Project") == "my-test-project"
    assert _package_name_slug("Hello World!") == "hello-world"
    assert _package_name_slug("  leading-trailing  ") == "leading-trailing"
    assert _package_name_slug("ABC123") == "abc123"


# ---------------------------------------------------------------------------
# c: {{PYTHON_VERSION}} resolves to "3.11"
# ---------------------------------------------------------------------------


def test_c_python_version_placeholder_resolved(tmp_path: Path) -> None:
    """{{PYTHON_VERSION}} is replaced with '3.11'; no literal braces remain in any workflow."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        target = _scaffold(tmp_path / profile, profile, python_version="3.11")
        for wf in (target / ".github" / "workflows").glob("*.yml"):
            content = wf.read_text(encoding="utf-8")
            assert "{{PYTHON_VERSION}}" not in content, f"{profile}/{wf.name}: not resolved"
            # Only test.yml contains {{PYTHON_VERSION}}; build/deploy use Docker tags, not Python versions
            if wf.name == "test.yml":
                assert "3.11" in content, f"{profile}/{wf.name}: version not present in test.yml"


# ---------------------------------------------------------------------------
# d: local-only → minimal/test.yml only
# ---------------------------------------------------------------------------


def test_d_local_only_generates_minimal_test_only(tmp_path: Path) -> None:
    """local-only profile generates only minimal test.yml; no build.yml, no deploy.yml."""
    target = _scaffold(tmp_path, "local-only")
    assert _workflow_exists(target, "test.yml"), "local-only: test.yml absent"
    assert not _workflow_exists(target, "build.yml"), "local-only: unexpected build.yml"
    assert not _workflow_exists(target, "deploy.yml"), "local-only: unexpected deploy.yml"


# ---------------------------------------------------------------------------
# e: dual-agent → standard/test.yml only
# ---------------------------------------------------------------------------


def test_e_dual_agent_generates_standard_test_only(tmp_path: Path) -> None:
    """dual-agent profile generates only standard test.yml; no build.yml, no deploy.yml."""
    target = _scaffold(tmp_path, "dual-agent")
    assert _workflow_exists(target, "test.yml"), "dual-agent: test.yml absent"
    assert not _workflow_exists(target, "build.yml"), "dual-agent: unexpected build.yml"
    assert not _workflow_exists(target, "deploy.yml"), "dual-agent: unexpected deploy.yml"


# ---------------------------------------------------------------------------
# f: dual-agent-webapp → full tier (test + build + deploy)
# ---------------------------------------------------------------------------


def test_f_dual_agent_webapp_generates_full_tier(tmp_path: Path) -> None:
    """dual-agent-webapp generates test.yml, build.yml, and deploy.yml."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    assert _workflow_exists(target, "test.yml"), "dual-agent-webapp: test.yml absent"
    assert _workflow_exists(target, "build.yml"), "dual-agent-webapp: build.yml absent"
    assert _workflow_exists(target, "deploy.yml"), "dual-agent-webapp: deploy.yml absent"


# ---------------------------------------------------------------------------
# g: --no-include-ci suppresses all CI for any profile
# ---------------------------------------------------------------------------


def test_g_no_include_ci_suppresses_all_workflows(tmp_path: Path) -> None:
    """--no-include-ci with any profile produces no .github/workflows/ directory."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        target = _scaffold(tmp_path / profile, profile, include_ci=False)
        workflows_dir = target / ".github" / "workflows"
        if workflows_dir.exists():
            workflows = list(workflows_dir.glob("*.yml"))
            assert not workflows, f"{profile}: workflows generated despite --no-include-ci"


# ---------------------------------------------------------------------------
# h: minimal/test.yml has no Docker, pytest, mypy steps
# ---------------------------------------------------------------------------


def test_h_minimal_workflow_has_no_docker_pytest_mypy(tmp_path: Path) -> None:
    """minimal/test.yml contains no active Docker, pytest, or mypy steps (comments ok)."""
    target = _scaffold(tmp_path, "local-only")
    content = _read_workflow(target, "test.yml")
    # Check no active (non-comment) lines reference docker, pytest, or mypy
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue  # comments are fine
        assert "docker" not in stripped.lower(), f"minimal: active docker line: {line!r}"
        assert "pytest" not in stripped.lower(), f"minimal: active pytest line: {line!r}"
        assert "mypy" not in stripped.lower(), f"minimal: active mypy line: {line!r}"


# ---------------------------------------------------------------------------
# i: standard/test.yml no Docker; pytest/mypy only as comments
# ---------------------------------------------------------------------------


def test_i_standard_workflow_no_docker_advisory_comments(tmp_path: Path) -> None:
    """standard/test.yml has no active Docker; pytest/mypy appear only in YAML comments."""
    target = _scaffold(tmp_path, "dual-agent")
    content = _read_workflow(target, "test.yml")

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue  # comments are fine
        # No active docker steps
        assert "docker" not in stripped.lower(), f"standard: active docker line: {line!r}"
        # pytest and mypy only allowed in comments
        assert "pytest" not in stripped.lower(), f"standard: active pytest line found: {line!r}"
        assert "mypy" not in stripped.lower(), f"standard: active mypy line found: {line!r}"


# ---------------------------------------------------------------------------
# j: full/test.yml has pytest; build.yml has docker/build-push-action
# ---------------------------------------------------------------------------


def test_j_full_workflow_has_pytest_and_build_has_docker(tmp_path: Path) -> None:
    """full/test.yml contains pytest steps; build.yml contains docker/build-push-action."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    test_content = _read_workflow(target, "test.yml")
    build_content = _read_workflow(target, "build.yml")

    # Find non-comment pytest line
    has_active_pytest = any(
        "pytest" in line.lower() and not line.strip().startswith("#") for line in test_content.splitlines()
    )
    assert has_active_pytest, "full/test.yml: no active pytest step found"
    assert "docker/build-push-action" in build_content, "build.yml: no docker/build-push-action"


# ---------------------------------------------------------------------------
# k: dual-agent-webapp generates src/__init__.py, pyproject.toml, requirements.txt
# ---------------------------------------------------------------------------


def test_k_dual_agent_webapp_generates_stub_files(tmp_path: Path) -> None:
    """dual-agent-webapp scaffold generates src/__init__.py, pyproject.toml, requirements.txt."""
    target = _scaffold(tmp_path, "dual-agent-webapp")
    assert (target / "src" / "__init__.py").exists(), "src/__init__.py absent"
    assert (target / "pyproject.toml").exists(), "pyproject.toml absent"
    assert (target / "requirements.txt").exists(), "requirements.txt absent"


# ---------------------------------------------------------------------------
# l: No hard-coded "agent-red" or "remaker" strings in any generated workflow
# ---------------------------------------------------------------------------


def test_l_no_agent_red_or_remaker_in_workflows(tmp_path: Path) -> None:
    """Generated workflows must not contain hard-coded 'agent-red' or 'remaker' strings."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        target = _scaffold(tmp_path / profile, profile)
        for wf in (target / ".github" / "workflows").glob("*.yml"):
            content = wf.read_text(encoding="utf-8").lower()
            assert "agent-red" not in content, f"{profile}/{wf.name}: contains 'agent-red'"
            assert "remaker" not in content, f"{profile}/{wf.name}: contains 'remaker'"


# ---------------------------------------------------------------------------
# m: --integrations generates dependabot.yml and .coderabbitai.yaml
# ---------------------------------------------------------------------------


def test_m_integrations_flag_generates_files(tmp_path: Path) -> None:
    """--integrations generates .github/dependabot.yml and .coderabbitai.yaml."""
    target = _scaffold(tmp_path / "with-int", "local-only", integrations=True)
    assert (target / ".github" / "dependabot.yml").exists(), "dependabot.yml absent"
    assert (target / ".coderabbitai.yaml").exists(), ".coderabbitai.yaml absent"


def test_m_no_integrations_flag_absent(tmp_path: Path) -> None:
    """Without --integrations, integration files are not generated."""
    target = _scaffold(tmp_path / "no-int", "local-only", integrations=False)
    assert not (target / ".github" / "dependabot.yml").exists(), "unexpected dependabot.yml"
    assert not (target / ".coderabbitai.yaml").exists(), "unexpected .coderabbitai.yaml"


# ---------------------------------------------------------------------------
# n: Fresh local-only scaffold → gt assert exits 0
# ---------------------------------------------------------------------------


def test_n_local_only_assert_exits_zero(tmp_path: Path) -> None:
    """Fresh local-only scaffold with seed_example=True → gt assert exits 0."""
    target = _scaffold(tmp_path, "local-only", seed_example=True)
    result = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "--config", "groundtruth.toml", "assert"],
        cwd=str(target),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"gt assert failed on fresh local-only scaffold.\n"
        f"stdout: {result.stdout[-400:]}\nstderr: {result.stderr[-400:]}"
    )


# ---------------------------------------------------------------------------
# o: Fresh dual-agent scaffold → gt assert exits 0
# ---------------------------------------------------------------------------


def test_o_dual_agent_assert_exits_zero(tmp_path: Path) -> None:
    """Fresh dual-agent scaffold with seed_example=True → gt assert exits 0."""
    target = _scaffold(tmp_path, "dual-agent", seed_example=True)
    result = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "--config", "groundtruth.toml", "assert"],
        cwd=str(target),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"gt assert failed on fresh dual-agent scaffold.\n"
        f"stdout: {result.stdout[-400:]}\nstderr: {result.stderr[-400:]}"
    )


# ---------------------------------------------------------------------------
# p: Fresh dual-agent-webapp scaffold → pytest exits 0
# ---------------------------------------------------------------------------


def test_p_dual_agent_webapp_pytest_exits_zero(tmp_path: Path) -> None:
    """Fresh dual-agent-webapp scaffold → pytest tests/ exits 0."""
    target = _scaffold(tmp_path, "dual-agent-webapp", seed_example=False)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
        cwd=str(target),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"pytest failed on fresh dual-agent-webapp scaffold.\n"
        f"stdout: {result.stdout[-400:]}\nstderr: {result.stderr[-400:]}"
    )


# ---------------------------------------------------------------------------
# q: --no-seed-example → no src/tasks.py
# ---------------------------------------------------------------------------


def test_q_no_seed_example_no_tasks_stub(tmp_path: Path) -> None:
    """--no-seed-example scaffold (any profile) → no src/tasks.py generated."""
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        target = _scaffold(tmp_path / profile, profile, seed_example=False)
        assert not (target / "src" / "tasks.py").exists(), (
            f"{profile}: src/tasks.py generated despite --no-seed-example"
        )


# ---------------------------------------------------------------------------
# r: src/tasks.py stub content verification
# ---------------------------------------------------------------------------


def test_r_tasks_stub_content(tmp_path: Path) -> None:
    """src/tasks.py stub contains required functions and status='open'."""
    target = _scaffold(tmp_path, "local-only", seed_example=True)
    tasks = target / "src" / "tasks.py"
    assert tasks.exists(), "src/tasks.py not generated with seed_example=True"
    content = tasks.read_text(encoding="utf-8")
    assert "def create_task" in content, "create_task function missing"
    assert '"status": "open"' in content or "status='open'" in content, (
        "status='open' pattern missing — assertion will fail"
    )
    assert "def list_tasks" in content, "list_tasks function missing"


# ---------------------------------------------------------------------------
# s: dual-agent-webapp generates tests/__init__.py and tests/test_smoke.py
# ---------------------------------------------------------------------------


def test_s_dual_agent_webapp_test_files(tmp_path: Path) -> None:
    """dual-agent-webapp generates tests/__init__.py and tests/test_smoke.py."""
    target = _scaffold(tmp_path, "dual-agent-webapp", seed_example=False)
    assert (target / "tests" / "__init__.py").exists(), "tests/__init__.py absent"
    assert (target / "tests" / "test_smoke.py").exists(), "tests/test_smoke.py absent"


# ---------------------------------------------------------------------------
# t: --no-seed-example dual-agent-webapp → no src/tasks.py; test_smoke.py present
# ---------------------------------------------------------------------------


def test_t_no_seed_example_webapp_no_tasks_but_smoke(tmp_path: Path) -> None:
    """dual-agent-webapp --no-seed-example → no src/tasks.py; tests/test_smoke.py still generated."""
    target = _scaffold(tmp_path, "dual-agent-webapp", seed_example=False)
    assert not (target / "src" / "tasks.py").exists(), "src/tasks.py generated despite --no-seed-example"
    assert (target / "tests" / "test_smoke.py").exists(), (
        "tests/test_smoke.py absent even though it should always be generated"
    )


# ---------------------------------------------------------------------------
# ci_tier helper
# ---------------------------------------------------------------------------


def test_ci_tier_local_only() -> None:
    """_ci_tier() returns 'minimal' for local-only."""
    assert _ci_tier(get_profile("local-only")) == "minimal"


def test_ci_tier_dual_agent() -> None:
    """_ci_tier() returns 'standard' for dual-agent."""
    assert _ci_tier(get_profile("dual-agent")) == "standard"


def test_ci_tier_dual_agent_webapp() -> None:
    """_ci_tier() returns 'full' for dual-agent-webapp."""
    assert _ci_tier(get_profile("dual-agent-webapp")) == "full"
