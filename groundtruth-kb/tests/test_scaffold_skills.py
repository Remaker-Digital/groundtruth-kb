# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scaffold delivery of current managed skills."""

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


def test_base_profile_has_shared_skill_without_bridge_profile_skills(tmp_path: Path) -> None:
    """Scaffold and upgrade deliver the same selected profile's skills."""
    scaffold_project(_make_options("local-only", tmp_path))
    target = tmp_path / "project"
    skills_root = target / ".claude" / "skills"
    assert {p.relative_to(skills_root).as_posix() for p in skills_root.rglob("*") if p.is_file()} == {
        "gtkb-baseline-audit/SKILL.md"
    }


def test_dual_agent_project_has_bridge_propose_skill(tmp_path: Path) -> None:
    """Scaffold installs current native authoring instructions without a file writer."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    skill_md = target / ".claude" / "skills" / "gtkb-bridge-propose" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "gtkb-bridge-propose" / "helpers" / "write_bridge.py"
    assert skill_md.exists(), f"bridge-propose SKILL.md missing at {skill_md}"
    assert not helper_py.exists()
    assert "gt bridge deliver" in skill_md.read_text(encoding="utf-8")


def test_dual_agent_project_has_spec_intake_skill(tmp_path: Path) -> None:
    """dual-agent scaffold copies spec-intake SKILL.md + helper with non-empty content."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    skill_md = target / ".claude" / "skills" / "gtkb-spec-intake" / "SKILL.md"
    helper_py = target / ".claude" / "skills" / "gtkb-spec-intake" / "helpers" / "spec_intake.py"
    assert skill_md.exists(), f"spec-intake SKILL.md missing at {skill_md}"
    assert helper_py.exists(), f"spec_intake.py missing at {helper_py}"
    assert skill_md.read_text(encoding="utf-8").strip(), "spec-intake SKILL.md is empty"
    helper_content = helper_py.read_text(encoding="utf-8")
    assert helper_content.strip(), "spec_intake.py is empty"


def test_spec_intake_skill_recursively_copied(tmp_path: Path) -> None:
    """helpers/ subdir is present under spec-intake/ and contains spec_intake.py."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    helpers_dir = target / ".claude" / "skills" / "gtkb-spec-intake" / "helpers"
    assert helpers_dir.is_dir(), f"helpers/ subdir missing at {helpers_dir}"
    helper_py = helpers_dir / "spec_intake.py"
    assert helper_py.exists(), f"spec_intake.py missing at {helper_py}"
    content = helper_py.read_text(encoding="utf-8")
    assert "def capture_candidate" in content
    assert "def confirm_candidate" in content
    assert "def reject_candidate" in content


def test_dual_agent_project_has_bridge_skill(tmp_path: Path) -> None:
    """Scaffold installs native workflow instructions and the remaining read helpers."""
    scaffold_project(_make_options("dual-agent", tmp_path))
    target = tmp_path / "project"
    skill_md = target / ".claude" / "skills" / "gtkb-bridge" / "SKILL.md"
    helpers_dir = target / ".claude" / "skills" / "gtkb-bridge" / "helpers"
    helper_names = {
        "scan_bridge.py",
        "show_thread_bridge.py",
    }

    assert skill_md.exists(), f"bridge SKILL.md missing at {skill_md}"
    assert skill_md.read_text(encoding="utf-8").strip(), "bridge SKILL.md is empty"
    assert helpers_dir.is_dir(), f"helpers/ subdir missing at {helpers_dir}"
    for helper_name in helper_names:
        helper_path = helpers_dir / helper_name
        assert helper_path.exists(), f"{helper_name} missing at {helper_path}"
        assert helper_path.read_text(encoding="utf-8").strip(), f"{helper_name} is empty"
    assert not (helpers_dir / "revise_bridge.py").exists()
    assert not (helpers_dir / "impl_report_bridge.py").exists()
    assert "gt projects commit" in skill_md.read_text(encoding="utf-8")
