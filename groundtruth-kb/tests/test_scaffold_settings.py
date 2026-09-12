# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scaffold settings.json generation (dual-agent profile)."""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


@pytest.fixture
def tmp_project(tmp_path):
    """Create a dual-agent scaffold in a temp dir."""
    opts = ScaffoldOptions(
        project_name="Test Project",
        profile="dual-agent",
        owner="Test Owner",
        target_dir=tmp_path / "project",
        init_git=False,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(opts)
    return tmp_path / "project"


def test_settings_json_generated(tmp_project):
    """.claude/settings.json is generated for dual-agent profile."""
    settings_path = tmp_project / ".claude" / "settings.json"
    assert settings_path.exists(), ".claude/settings.json not generated"


def test_settings_local_json_generated(tmp_project):
    """.claude/settings.local.json is generated for dual-agent profile."""
    local_settings = tmp_project / ".claude" / "settings.local.json"
    assert local_settings.exists(), ".claude/settings.local.json not generated"


def test_settings_local_json_ignored(tmp_project):
    """.claude/settings.local.json is covered by .gitignore."""
    gitignore = (tmp_project / ".gitignore").read_text(encoding="utf-8")
    assert "settings.local.json" in gitignore, ".gitignore missing settings.local.json entry"


def test_groundtruth_dir_ignored(tmp_project):
    """.groundtruth/ is in .gitignore."""
    gitignore = (tmp_project / ".gitignore").read_text(encoding="utf-8")
    assert ".groundtruth/" in gitignore, ".gitignore missing .groundtruth/ entry"


def test_settings_json_hooks_nested_schema(tmp_project):
    """settings.json uses nested hook event -> matcher group -> handler schema."""
    settings_path = tmp_project / ".claude" / "settings.json"
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    assert "hooks" in data, "settings.json missing 'hooks' key"
    hooks = data["hooks"]
    recognized_events = {"PreToolUse", "SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"}
    found_events = set(hooks.keys()) & recognized_events
    assert found_events, f"No recognized event keys in hooks: {list(hooks.keys())}"
    for event_name, matcher_groups in hooks.items():
        assert isinstance(matcher_groups, list), f"{event_name} must be a list of matcher groups"
        for group in matcher_groups:
            assert "hooks" in group, f"{event_name} group missing 'hooks' key"
            assert isinstance(group["hooks"], list), f"{event_name} group['hooks'] must be a list"


def test_settings_local_json_no_hooks(tmp_project):
    """settings.local.json must contain only permissions, no hooks."""
    local_path = tmp_project / ".claude" / "settings.local.json"
    data = json.loads(local_path.read_text(encoding="utf-8"))
    assert "hooks" not in data, (
        "settings.local.json must not contain hooks — all governance hooks belong in settings.json (tracked)"
    )
    assert "permissions" in data, "settings.local.json should contain permissions"


def test_settings_json_tracked(tmp_project):
    """.claude/settings.json is NOT in .gitignore (must be tracked in git)."""
    gitignore = (tmp_project / ".gitignore").read_text(encoding="utf-8")
    lines = [ln.strip() for ln in gitignore.splitlines() if ln.strip() and not ln.startswith("#")]
    # settings.local.json should be ignored (verified by test_settings_local_json_ignored)
    # but settings.json itself must NOT be ignored
    for line in lines:
        assert line != ".claude/settings.json", ".claude/settings.json must be tracked, not ignored"
        assert line != "settings.json", "bare settings.json ignore would hide governance hooks"
