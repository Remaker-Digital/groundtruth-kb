# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scaffold skill-template copy (``.claude/skills/decision-capture/``)."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


def _make_options(profile: str, tmp_path: Path) -> ScaffoldOptions:
    return ScaffoldOptions(
        project_name="Skills Project",
        profile=profile,
        owner="Test Owner",
        target_dir=tmp_path / "project",
        seed_example=False,
        include_ci=False,
    )


def test_dual_agent_project_has_decision_capture_skill(tmp_path: Path) -> None:
    """dual-agent scaffold copies SKILL.md + helper with non-empty content."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    skill_md = target / ".claude" / "skills" / "decision-capture" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "decision-capture" / "helpers" / "record_decision.py"
    assert skill_md.exists(), f"SKILL.md missing at {skill_md}"
    assert helper_py.exists(), f"record_decision.py missing at {helper_py}"
    assert skill_md.read_text(encoding="utf-8").strip(), "SKILL.md is empty"
    assert helper_py.read_text(encoding="utf-8").strip(), "record_decision.py is empty"


def test_base_profile_no_skill_tree(tmp_path: Path) -> None:
    """local-only scaffold does not create the .claude/skills/ tree."""
    scaffold_project(_make_options("local-only", tmp_path))
    target = tmp_path / "project"
    skills_root = target / ".claude" / "skills"
    assert not skills_root.exists(), f".claude/skills/ must not be created for local-only profile; found {skills_root}"


def test_skill_files_copied_recursively(tmp_path: Path) -> None:
    """helpers/ subdir is present and contains record_decision.py."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    helpers_dir = target / ".claude" / "skills" / "decision-capture" / "helpers"
    assert helpers_dir.is_dir(), f"helpers/ subdir missing at {helpers_dir}"
    helper_py = helpers_dir / "record_decision.py"
    assert helper_py.exists(), f"record_decision.py missing at {helper_py}"
    content = helper_py.read_text(encoding="utf-8")
    assert "def record_decision" in content
