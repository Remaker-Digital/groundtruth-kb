"""The baseline directs complete project finalization through the installed CLI."""

from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main

ROOT = Path(__file__).resolve().parents[2]


def test_project_commit_instructions_match_the_native_cli():
    skill = (ROOT / ".agents/skills/gtkb-sweep-commit/SKILL.md").read_text(encoding="utf-8")
    assert "gt projects commit" in skill
    result = CliRunner().invoke(main, ["projects", "commit", "--help"])
    assert result.exit_code == 0, result.output
    for option in ["--native-context-id", "--expected-version", "--message-file"]:
        assert option in skill
        assert option in result.output
    assert "groundtruth_kb.git_lifecycle" not in skill
    assert "preserve --work-item-id" not in skill


def test_project_commit_guidance_preserves_review_and_foreign_work_boundaries():
    skill = (ROOT / ".agents/skills/gtkb-sweep-commit/SKILL.md").read_text(encoding="utf-8").lower()
    skill = " ".join(skill.split())
    for concept in ["every", "verified", "mode", "object", "foreign", "same uncommitted work item", "normal", "hooks"]:
        assert concept in skill
    assert "git add -a" not in skill
    assert "git add --all" not in skill
    assert "delib-" not in skill
