# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for current managed skill doctor checks.

Covers helper-level checks and the full ``run_doctor()`` integration
required by Codex bridge ``-010`` Condition 1.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor import (
    _check_bridge_propose_skill_present,
    _check_spec_intake_skill_present,
    run_doctor,
)
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


def _make_dual_agent_project(tmp_path: Path) -> Path:
    options = ScaffoldOptions(
        project_name="Doctor Skill Test Project",
        profile="dual-agent",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(options)
    return tmp_path / "project"


def test_doctor_warning_when_bridge_propose_missing(tmp_path: Path) -> None:
    """Direct helper + integration check: missing bridge-propose → warning.

    Covers both the helper-level check and the ``run_doctor()`` integration
    path so a regression in either wiring surfaces.
    """
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "skills" / "gtkb-bridge-propose" / "SKILL.md").unlink()

    # Direct helper-level check.
    helper_check = _check_bridge_propose_skill_present(target, profile_name="dual-agent")
    assert helper_check.name == "skill:bridge-propose"
    assert helper_check.status == "warning"
    assert helper_check.found is False
    assert "SKILL.md" in helper_check.message
    assert "gt project upgrade --apply" in helper_check.message

    # run_doctor() integration.
    report = run_doctor(target, "dual-agent")
    bridge_propose_checks = [c for c in report.checks if c.name == "skill:bridge-propose"]
    assert len(bridge_propose_checks) == 1, (
        f"expected exactly one 'skill:bridge-propose' check; got {[c.name for c in report.checks]}"
    )
    assert bridge_propose_checks[0].status == "warning"
    assert bridge_propose_checks[0].found is False


def test_doctor_warning_when_spec_intake_missing(tmp_path: Path) -> None:
    """Direct helper check: missing spec-intake SKILL.md + helper → status=warning."""
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "skills" / "gtkb-spec-intake" / "SKILL.md").unlink()
    (target / ".claude" / "skills" / "gtkb-spec-intake" / "helpers" / "spec_intake.py").unlink()

    check = _check_spec_intake_skill_present(target, profile_name="dual-agent")
    assert check.status == "warning"
    assert check.name == "skill:spec-intake"
    assert check.found is False
    assert "SKILL.md" in check.message
    assert "spec_intake.py" in check.message
    assert "gt project upgrade --apply" in check.message


def test_doctor_pass_when_spec_intake_present(tmp_path: Path) -> None:
    """Direct helper check: fresh scaffold has spec-intake → status=pass."""
    target = _make_dual_agent_project(tmp_path)
    check = _check_spec_intake_skill_present(target, profile_name="dual-agent")
    assert check.status == "pass"
    assert check.found is True
    assert "present" in check.message.lower()


def test_run_doctor_reports_missing_spec_intake_in_dual_agent_project(tmp_path: Path) -> None:
    """Integration: run_doctor() on dual-agent project with missing spec-intake →
    DoctorReport contains a 'skill:spec-intake' check with status=warning.
    """
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "skills" / "gtkb-spec-intake" / "SKILL.md").unlink()
    (target / ".claude" / "skills" / "gtkb-spec-intake" / "helpers" / "spec_intake.py").unlink()

    report = run_doctor(target, "dual-agent")
    spec_intake_checks = [c for c in report.checks if c.name == "skill:spec-intake"]
    assert len(spec_intake_checks) == 1, (
        f"expected exactly one 'skill:spec-intake' check; got {[c.name for c in report.checks]}"
    )
    assert spec_intake_checks[0].status == "warning"
    assert spec_intake_checks[0].found is False
    assert "SKILL.md" in spec_intake_checks[0].message
    assert "spec_intake.py" in spec_intake_checks[0].message
