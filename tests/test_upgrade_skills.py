# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for skill upgrade delivery (plan_upgrade + execute_upgrade).

Covers both the unconditional missing-file repair path (handled by
``_plan_missing_managed_files`` at any scaffold version) and the
version-gated hash-drift path (handled by ``_plan_managed_skills``).
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb import __version__
from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

_SKILL_MD = ".claude/skills/decision-capture/SKILL.md"
_SKILL_HELPER = ".claude/skills/decision-capture/helpers/record_decision.py"


def _write_minimal_toml(target: Path, profile: str, version: str) -> None:
    """Minimal groundtruth.toml with a [project] section — mirrors test_upgrade helper."""
    (target / "groundtruth.toml").write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "{profile}"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Unconditional missing-file repair (same-version path)
# ---------------------------------------------------------------------------


def test_plan_upgrade_adds_missing_skill_at_same_version(tmp_path: Path) -> None:
    """dual-agent project at current version with SKILL.md missing → add action."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    actions = plan_upgrade(tmp_path)
    skill_adds = [a for a in actions if a.action == "add" and a.file == _SKILL_MD]
    assert skill_adds, (
        f"expected add action for missing {_SKILL_MD} at same version; got: {[(a.action, a.file) for a in actions]}"
    )


def test_plan_upgrade_adds_missing_skill_helper_at_same_version(tmp_path: Path) -> None:
    """dual-agent project at current version with helper missing → add action."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    actions = plan_upgrade(tmp_path)
    helper_adds = [a for a in actions if a.action == "add" and a.file == _SKILL_HELPER]
    assert helper_adds, (
        f"expected add action for missing {_SKILL_HELPER} at same version; got: {[(a.action, a.file) for a in actions]}"
    )


def test_execute_creates_missing_skill_files_at_same_version(tmp_path: Path) -> None:
    """End-to-end: plan at same version → execute → skill files landed on disk."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    actions = plan_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=False)
    skill_md = tmp_path / _SKILL_MD
    helper_py = tmp_path / _SKILL_HELPER
    assert skill_md.exists(), "SKILL.md should be copied by execute_upgrade"
    assert helper_py.exists(), "record_decision.py should be copied by execute_upgrade"
    assert skill_md.read_text(encoding="utf-8").strip(), "SKILL.md is empty"
    helper_content = helper_py.read_text(encoding="utf-8")
    assert "def record_decision" in helper_content


# ---------------------------------------------------------------------------
# Version-gated hash-drift tests
# ---------------------------------------------------------------------------


def _write_skill_files(target: Path, *, customized: bool) -> None:
    """Write SKILL.md and helper.py to the target. If customized=True, SKILL.md
    gets a sentinel tail; otherwise the template content is copied verbatim.

    Uses byte-level copy rather than ``write_text`` so Windows newline
    translation cannot trigger a spurious hash mismatch against the
    template during the at-template-drift test.
    """
    from groundtruth_kb import get_templates_dir

    templates = get_templates_dir()
    skill_src = templates / "skills" / "decision-capture" / "SKILL.md"
    helper_src = templates / "skills" / "decision-capture" / "helpers" / "record_decision.py"

    skill_dst = target / _SKILL_MD
    helper_dst = target / _SKILL_HELPER
    skill_dst.parent.mkdir(parents=True, exist_ok=True)
    helper_dst.parent.mkdir(parents=True, exist_ok=True)

    skill_bytes = skill_src.read_bytes()
    if customized:
        skill_bytes = skill_bytes + b"\n\n# customized sentinel\n"
    skill_dst.write_bytes(skill_bytes)
    helper_dst.write_bytes(helper_src.read_bytes())


def test_plan_upgrade_skips_customized_skill_at_version_mismatch(tmp_path: Path) -> None:
    """Customized SKILL.md at older scaffold_version → skip action with customized reason."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    _write_skill_files(tmp_path, customized=True)
    actions = plan_upgrade(tmp_path)
    skill_skips = [a for a in actions if a.action == "skip" and a.file == _SKILL_MD]
    assert len(skill_skips) == 1, f"expected exactly one skip for {_SKILL_MD}; got {skill_skips}"
    assert "customized" in skill_skips[0].reason.lower() or "force" in skill_skips[0].reason.lower()


def test_execute_upgrade_applies_customized_skill_with_force(tmp_path: Path) -> None:
    """execute_upgrade(..., force=True) overwrites customized SKILL.md from template."""
    import hashlib

    from groundtruth_kb import get_templates_dir

    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    _write_skill_files(tmp_path, customized=True)
    skill_path = tmp_path / _SKILL_MD
    assert b"customized sentinel" in skill_path.read_bytes()

    actions = plan_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=True)

    # Hash comparison avoids newline-translation false negatives on
    # Windows. execute_upgrade uses shutil.copy2 which preserves bytes.
    templates = get_templates_dir()
    template_bytes = (templates / "skills" / "decision-capture" / "SKILL.md").read_bytes()
    assert hashlib.sha256(skill_path.read_bytes()).hexdigest() == hashlib.sha256(template_bytes).hexdigest()


def test_plan_upgrade_silent_on_at_template_skill_at_version_mismatch(tmp_path: Path) -> None:
    """Template-matching skill file at older version → no skip action (no drift to surface)."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version="0.0.1")
    _write_skill_files(tmp_path, customized=False)
    actions = plan_upgrade(tmp_path)
    skill_actions = [a for a in actions if a.file == _SKILL_MD and a.action == "skip"]
    assert not skill_actions, f"expected no skip action for at-template SKILL.md; got {skill_actions}"
    helper_actions = [a for a in actions if a.file == _SKILL_HELPER and a.action == "skip"]
    assert not helper_actions, f"expected no skip action for at-template helper; got {helper_actions}"


# ---------------------------------------------------------------------------
# Profile gating
# ---------------------------------------------------------------------------


def test_base_profile_no_skill_actions(tmp_path: Path) -> None:
    """local-only profile: no skill-related actions (neither add nor skip)."""
    _write_minimal_toml(tmp_path, profile="local-only", version=__version__)
    actions = plan_upgrade(tmp_path)
    skill_actions = [a for a in actions if a.file.startswith(".claude/skills/")]
    assert not skill_actions, f"local-only profile should emit no skill actions; got {skill_actions}"
