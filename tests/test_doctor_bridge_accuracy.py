# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for gt project doctor bridge-readiness accuracy fixes (WI-MVP-5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import _check_file_bridge_setup, run_doctor
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

_BRIDGE_RULE_FILES = (
    "file-bridge-protocol.md",
    "bridge-essential.md",
    "deliberation-protocol.md",
)


def _make_dual_agent_project(tmp_path: Path) -> Path:
    """Scaffold a minimal dual-agent project and return the project path."""
    options = ScaffoldOptions(
        project_name="Doctor Test Project",
        profile="dual-agent",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return tmp_path / "project"


def _make_local_only_project(tmp_path: Path) -> Path:
    """Scaffold a minimal local-only project and return the project path."""
    options = ScaffoldOptions(
        project_name="Local Only Project",
        profile="local-only",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return tmp_path / "project"


# ---------------------------------------------------------------------------
# bridge/INDEX.md absent → WARN
# ---------------------------------------------------------------------------


def test_doctor_warns_when_bridge_index_absent(tmp_path: Path) -> None:
    """run_doctor() with dual-agent profile warns when bridge/INDEX.md is absent."""
    target = _make_dual_agent_project(tmp_path)
    (target / "bridge" / "INDEX.md").unlink()

    report = run_doctor(target, "dual-agent")
    bridge_checks = [c for c in report.checks if "Bridge" in c.name or "bridge" in c.message.lower()]
    warn_checks = [c for c in bridge_checks if c.status == "warning"]
    assert warn_checks, "Expected a warning check about missing bridge/INDEX.md"
    assert any("INDEX.md" in c.message for c in warn_checks)


def test_direct_check_warns_when_bridge_index_absent(tmp_path: Path) -> None:
    """_check_file_bridge_setup() returns WARN when bridge/INDEX.md is absent."""
    target = _make_dual_agent_project(tmp_path)
    (target / "bridge" / "INDEX.md").unlink()

    result = _check_file_bridge_setup(target)
    assert result.status == "warning"
    assert "INDEX.md" in result.message


# ---------------------------------------------------------------------------
# Required bridge rule file absent → WARN
# ---------------------------------------------------------------------------


def test_doctor_warns_when_required_rule_file_absent(tmp_path: Path) -> None:
    """run_doctor() with dual-agent profile warns when a required bridge rule is absent."""
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "rules" / "file-bridge-protocol.md").unlink()

    report = run_doctor(target, "dual-agent")
    bridge_checks = [c for c in report.checks if "Bridge" in c.name]
    warn_checks = [c for c in bridge_checks if c.status == "warning"]
    assert warn_checks, "Expected a warning check about missing bridge rule file"
    assert any("file-bridge-protocol.md" in c.message for c in warn_checks)


def test_direct_check_warns_when_rule_file_absent(tmp_path: Path) -> None:
    """_check_file_bridge_setup() returns WARN when a required bridge rule file is absent."""
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "rules" / "bridge-essential.md").unlink()

    result = _check_file_bridge_setup(target)
    assert result.status == "warning"
    assert "bridge-essential.md" in result.message


# ---------------------------------------------------------------------------
# local-only profile → no bridge WARN
# ---------------------------------------------------------------------------


def test_local_only_doctor_no_bridge_index_warn(tmp_path: Path) -> None:
    """run_doctor() for local-only profile does not emit bridge/INDEX.md warnings."""
    target = _make_local_only_project(tmp_path)
    report = run_doctor(target, "local-only")
    bridge_checks = [c for c in report.checks if "Bridge" in c.name or "INDEX.md" in c.message]
    # local-only never runs _check_file_bridge_setup; no bridge checks expected
    assert not bridge_checks, f"Unexpected bridge checks for local-only: {bridge_checks}"


# ---------------------------------------------------------------------------
# Regression guard: doctor does NOT pass when INDEX.md absent
# ---------------------------------------------------------------------------


def test_doctor_does_not_pass_when_index_absent(tmp_path: Path) -> None:
    """Doctor overall is not 'pass' when bridge/INDEX.md is absent (regression guard)."""
    target = _make_dual_agent_project(tmp_path)
    (target / "bridge" / "INDEX.md").unlink()

    report = run_doctor(target, "dual-agent")
    assert report.overall != "pass", (
        "Doctor should not return 'pass' when bridge/INDEX.md is absent"
    )


# ---------------------------------------------------------------------------
# Doctor passes when INDEX.md + all rule files present
# ---------------------------------------------------------------------------


def test_doctor_bridge_check_passes_when_complete(tmp_path: Path) -> None:
    """_check_file_bridge_setup() returns pass when bridge/INDEX.md and all rule files are present."""
    target = _make_dual_agent_project(tmp_path)
    result = _check_file_bridge_setup(target)
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# Claude Code check is labeled as availability (not auth)
# ---------------------------------------------------------------------------


def test_claude_code_check_labeled_as_availability(tmp_path: Path) -> None:
    """The Claude Code doctor check is labeled as availability, not auth validation."""
    from groundtruth_kb.project.doctor import _check_claude_code

    check = _check_claude_code()
    assert "availability" in check.name.lower() or "availability" in (check.message or "").lower()
    assert "auth" not in check.name.lower()
