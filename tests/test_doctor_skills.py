# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the decision-capture skill doctor check.

Covers helper-level checks and the full ``run_doctor()`` integration
required by Codex bridge ``-010`` Condition 1.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor import _check_skill_present, run_doctor
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


def test_doctor_warning_when_decision_capture_missing(tmp_path: Path) -> None:
    """Direct helper check: missing SKILL.md → status=warning."""
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "skills" / "decision-capture" / "SKILL.md").unlink()

    check = _check_skill_present(target, profile_name="dual-agent")
    assert check.status == "warning"
    assert check.name == "skill:decision-capture"
    assert check.found is False
    assert "SKILL.md" in check.message
    assert "gt project upgrade --apply" in check.message


def test_doctor_pass_when_decision_capture_present(tmp_path: Path) -> None:
    """Direct helper check: fresh scaffold → status=pass."""
    target = _make_dual_agent_project(tmp_path)
    check = _check_skill_present(target, profile_name="dual-agent")
    assert check.status == "pass"
    assert check.found is True
    assert "present" in check.message.lower()


def test_run_doctor_reports_missing_skill_in_dual_agent_project(tmp_path: Path) -> None:
    """Integration: run_doctor() on dual-agent project with missing skill →
    DoctorReport contains a 'skill:decision-capture' check with status=warning.

    This is the Codex ``-010`` Condition 1 integration test.
    """
    target = _make_dual_agent_project(tmp_path)
    (target / ".claude" / "skills" / "decision-capture" / "SKILL.md").unlink()
    (target / ".claude" / "skills" / "decision-capture" / "helpers" / "record_decision.py").unlink()

    report = run_doctor(target, "dual-agent")
    skill_checks = [c for c in report.checks if c.name == "skill:decision-capture"]
    assert len(skill_checks) == 1, (
        f"expected exactly one 'skill:decision-capture' check; got {[c.name for c in report.checks]}"
    )
    assert skill_checks[0].status == "warning"
    assert skill_checks[0].found is False
    assert "SKILL.md" in skill_checks[0].message
    assert "record_decision.py" in skill_checks[0].message
