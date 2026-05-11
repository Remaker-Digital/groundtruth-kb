"""W1's SKIP_DIRS + SCAN_ROOTS configuration is correctly honored.

Fixture-based: creates temp project tree with files in scanned and skipped
locations; asserts the scanner walks the included paths and skips the
configured surfaces. Fast (<1s); deterministic; not affected by live repo
size. In the release-candidate gate.

Per WRAPUP -011 §3.1 + -012 GO conditions.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import wrap_scan_hygiene as w1  # noqa: E402


OLD_ROOT_TOKEN = "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\foo"


def _make_fake_project(base: Path) -> Path:
    project = base / "fake_project"
    project.mkdir()
    return project


def test_scan_includes_scripts_dir(tmp_path: Path) -> None:
    project = _make_fake_project(tmp_path)
    (project / "scripts").mkdir()
    (project / "scripts" / "real.py").write_text(f"# {OLD_ROOT_TOKEN}\n")
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert any("scripts/real.py" in p or "scripts\\real.py" in p for p in paths), (
        f"Expected scripts/real.py in findings; got {paths}"
    )


def test_scan_excludes_test_results_dir(tmp_path: Path) -> None:
    project = _make_fake_project(tmp_path)
    (project / "test-results").mkdir()
    (project / "test-results" / "report.py").write_text(f"# {OLD_ROOT_TOKEN}\n")
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert not any("test-results" in p for p in paths), (
        f"test-results/ should be in SKIP_DIRS; got {paths}"
    )


def test_scan_excludes_bridge_dir(tmp_path: Path) -> None:
    """bridge/ is not in SCAN_ROOTS — proposal prose may legitimately quote
    old paths in historical context."""
    project = _make_fake_project(tmp_path)
    (project / "bridge").mkdir()
    (project / "bridge" / "old-thread-001.md").write_text(f"Quoting: {OLD_ROOT_TOKEN}\n")
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert not any("bridge/" in p or "bridge\\" in p for p in paths), (
        f"bridge/ should be excluded from SCAN_ROOTS; got {paths}"
    )


def test_scan_includes_root_governance_files(tmp_path: Path) -> None:
    """CLAUDE.md and AGENTS.md should be scanned per WRAPUP -011 §4."""
    project = _make_fake_project(tmp_path)
    (project / "CLAUDE.md").write_text(f"# Root governance\n{OLD_ROOT_TOKEN}\n")
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert any("CLAUDE.md" in p for p in paths), (
        f"CLAUDE.md should be in SCAN_ROOT_FILES; got {paths}"
    )


def test_scan_includes_claude_skills(tmp_path: Path) -> None:
    """`.claude/skills/` is in SCAN_ROOTS per WRAPUP -011 §4."""
    project = _make_fake_project(tmp_path)
    skill_dir = project / ".claude" / "skills" / "fake-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"# Skill\n{OLD_ROOT_TOKEN}\n")
    findings = w1.check_hardcoded_old_project_root(project)
    paths = [f["path"] for f in findings]
    assert any("skills" in p for p in paths), (
        f".claude/skills/ should be in SCAN_ROOTS; got {paths}"
    )


def test_scan_clean_when_no_old_root_references(tmp_path: Path) -> None:
    project = _make_fake_project(tmp_path)
    (project / "scripts").mkdir()
    (project / "scripts" / "clean.py").write_text("# clean source\nx = 1\n")
    findings = w1.check_hardcoded_old_project_root(project)
    assert findings == []
