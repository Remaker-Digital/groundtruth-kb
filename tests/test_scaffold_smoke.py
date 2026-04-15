# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cross-platform smoke tests for all scaffold profiles (WI-MVP-4)."""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.project.doctor import run_doctor
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

_BRIDGE_RULE_FILES = (
    "file-bridge-protocol.md",
    "bridge-essential.md",
    "deliberation-protocol.md",
)

# Patterns that must NOT appear in any generated file (product leakage)
_LEAKAGE_PATTERNS = [
    re.compile(r"Agent Red", re.IGNORECASE),
    re.compile(r"\bACS\b"),
    re.compile(r"azure-communication"),
    re.compile(r"acragentredeastus", re.IGNORECASE),
]


def _make_options(profile: str, tmp_path: Path, **kwargs: object) -> ScaffoldOptions:
    return ScaffoldOptions(
        project_name="Smoke Test Project",
        profile=profile,
        owner="Smoke Tester",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
        **kwargs,  # type: ignore[arg-type]
    )


def _scan_for_leakage(target: Path) -> list[str]:
    """Return a list of (path, pattern) violations found in all text files."""
    violations: list[str] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".json", ".toml", ".yml", ".yaml", ".txt", ".py", ".tf", ".env"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for pattern in _LEAKAGE_PATTERNS:
            if pattern.search(content):
                rel = path.relative_to(target)
                violations.append(f"{rel}: matched /{pattern.pattern}/")
    return violations


# ---------------------------------------------------------------------------
# local-only smoke
# ---------------------------------------------------------------------------


def test_smoke_local_only_scaffold(tmp_path: Path) -> None:
    """local-only scaffold creates expected files and doctor does not fail."""
    options = _make_options("local-only", tmp_path)
    scaffold_project(options)
    target = tmp_path / "project"
    assert (target / "groundtruth.toml").exists()
    assert (target / "groundtruth.db").exists()
    assert not (target / "bridge" / "INDEX.md").exists()
    assert not (target / "infrastructure").exists()


def test_smoke_local_only_no_leakage(tmp_path: Path) -> None:
    """local-only scaffold contains no product-specific leakage."""
    options = _make_options("local-only", tmp_path)
    scaffold_project(options)
    violations = _scan_for_leakage(tmp_path / "project")
    assert not violations, "Leakage found:\n" + "\n".join(violations)


def test_smoke_local_only_doctor_not_fail(tmp_path: Path) -> None:
    """local-only scaffold passes run_doctor() (no fail-level issues)."""
    options = _make_options("local-only", tmp_path)
    scaffold_project(options)
    report = run_doctor(tmp_path / "project", "local-only")
    assert report.overall != "fail", "Doctor returned fail for local-only. Checks:\n" + "\n".join(
        f"  {c.status}: {c.message}" for c in report.checks
    )


# ---------------------------------------------------------------------------
# dual-agent smoke
# ---------------------------------------------------------------------------


def test_smoke_dual_agent_scaffold(tmp_path: Path) -> None:
    """dual-agent scaffold creates bridge/INDEX.md and all bridge rule files."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    target = tmp_path / "project"
    assert (target / "bridge" / "INDEX.md").exists()
    rules_dir = target / ".claude" / "rules"
    for rule_file in _BRIDGE_RULE_FILES:
        assert (rules_dir / rule_file).exists(), f"Missing: {rule_file}"
    # No Terraform for dual-agent (no cloud provider)
    assert not (target / "infrastructure").exists()


def test_smoke_dual_agent_no_leakage(tmp_path: Path) -> None:
    """dual-agent scaffold contains no product-specific leakage."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    violations = _scan_for_leakage(tmp_path / "project")
    assert not violations, "Leakage found:\n" + "\n".join(violations)


def test_smoke_dual_agent_doctor_not_fail(tmp_path: Path) -> None:
    """dual-agent scaffold passes run_doctor() (no fail-level issues)."""
    options = _make_options("dual-agent", tmp_path)
    scaffold_project(options)
    report = run_doctor(tmp_path / "project", "dual-agent")
    assert report.overall != "fail", "Doctor returned fail for dual-agent. Checks:\n" + "\n".join(
        f"  {c.status}: {c.message}" for c in report.checks
    )


# ---------------------------------------------------------------------------
# dual-agent-webapp smoke
# ---------------------------------------------------------------------------


def test_smoke_dual_agent_webapp_scaffold(tmp_path: Path) -> None:
    """dual-agent-webapp scaffold creates bridge and Docker files."""
    options = _make_options("dual-agent-webapp", tmp_path, cloud_provider="azure")
    scaffold_project(options)
    target = tmp_path / "project"
    assert (target / "bridge" / "INDEX.md").exists()
    rules_dir = target / ".claude" / "rules"
    for rule_file in _BRIDGE_RULE_FILES:
        assert (rules_dir / rule_file).exists(), f"Missing: {rule_file}"


def test_smoke_dual_agent_webapp_terraform_stub(tmp_path: Path) -> None:
    """dual-agent-webapp with azure cloud provider creates Terraform with # stub marker."""
    options = _make_options("dual-agent-webapp", tmp_path, cloud_provider="azure")
    scaffold_project(options)
    main_tf = tmp_path / "project" / "infrastructure" / "terraform" / "main.tf"
    assert main_tf.exists(), "main.tf not created"
    content = main_tf.read_text(encoding="utf-8")
    assert "# stub" in content


def test_smoke_dual_agent_webapp_no_terraform_for_no_cloud(tmp_path: Path) -> None:
    """dual-agent-webapp with cloud_provider=none does NOT create Terraform directory."""
    options = _make_options("dual-agent-webapp", tmp_path, cloud_provider="none")
    scaffold_project(options)
    assert not (tmp_path / "project" / "infrastructure").exists()


def test_smoke_dual_agent_webapp_no_leakage(tmp_path: Path) -> None:
    """dual-agent-webapp scaffold contains no product-specific leakage."""
    options = _make_options("dual-agent-webapp", tmp_path, cloud_provider="azure")
    scaffold_project(options)
    violations = _scan_for_leakage(tmp_path / "project")
    assert not violations, "Leakage found:\n" + "\n".join(violations)


def test_smoke_dual_agent_webapp_doctor_not_fail(tmp_path: Path) -> None:
    """dual-agent-webapp scaffold passes run_doctor() (no fail-level issues)."""
    options = _make_options("dual-agent-webapp", tmp_path, cloud_provider="azure")
    scaffold_project(options)
    report = run_doctor(tmp_path / "project", "dual-agent-webapp")
    assert report.overall != "fail", "Doctor returned fail for dual-agent-webapp. Checks:\n" + "\n".join(
        f"  {c.status}: {c.message}" for c in report.checks
    )
