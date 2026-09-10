"""Remove obsolete managed startup handlers without altering adopter work."""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project
from groundtruth_kb.project.upgrade import _apply_file_actions, _plan_settings_registration


@pytest.mark.parametrize(
    ("filename", "event"),
    [
        ("session-start-governance.py", "SessionStart"),
        ("formal-artifact-approval-gate.py", "PreToolUse"),
        ("narrative-artifact-approval-gate.py", "PreToolUse"),
        ("delib-search-gate.py", "UserPromptSubmit"),
        ("intake-classifier.py", "UserPromptSubmit"),
        ("gov09-capture.py", "UserPromptSubmit"),
        ("spec-classifier.py", "UserPromptSubmit"),
        ("delib-search-tracker.py", "PostToolUse"),
    ],
)
@pytest.mark.parametrize("mixed", [False, True])
def test_upgrade_removes_only_exact_retired_managed_handler(tmp_path, filename, event, mixed):
    settings = tmp_path / ".claude/settings.json"
    settings.parent.mkdir()
    command = f"python .claude/hooks/{filename}"
    retired = {"type": "command", "command": command, "timeout": 5}
    custom = {"type": "command", "command": command + " --custom"}
    foreign = {"type": "command", "command": "python local-handler.py", "timeout": 7}
    group = {"matcher": "Write", "custom": {"preserve": True}, "hooks": [retired, foreign] if mixed else [retired]}
    other = {"hooks": [custom] if mixed else [custom, foreign]}
    settings.write_text(json.dumps({"hooks": {event: [group, other]}, "permissions": {"allow": ["Read"]}}))
    old_hook = settings.parent / "hooks" / filename
    old_hook.parent.mkdir()
    old_hook.write_bytes(b"# adopter modification\r\n\xffpreserve\r\n")
    before = old_hook.read_bytes()

    actions = _plan_settings_registration(tmp_path, "dual-agent")
    assert any(action.event == event for action in actions)
    _apply_file_actions(tmp_path, actions, update_manifest=False)
    result = json.loads(settings.read_text())
    groups = result["hooks"][event]
    handlers = [handler for item in groups for handler in item["hooks"]]
    assert retired not in handlers
    assert handlers.count(custom) == handlers.count(foreign) == 1
    assert other in groups
    assert {**group, "hooks": [foreign]} in groups if mixed else group not in groups
    assert result["permissions"] == {"allow": ["Read"]}
    assert old_hook.read_bytes() == before
    post = settings.read_bytes()
    assert _plan_settings_registration(tmp_path, "dual-agent") == []
    assert settings.read_bytes() == post


@pytest.mark.parametrize("profile", ["dual-agent", "dual-agent-webapp"])
def test_fresh_scaffold_has_no_automatic_prompt_or_startup_producer(tmp_path, profile):
    target = tmp_path / "project"
    scaffold_project(
        ScaffoldOptions(
            project_name="Startup consumer test",
            profile=profile,
            owner="Test",
            target_dir=target,
            init_git=False,
            seed_example=False,
            include_ci=False,
        )
    )
    hooks = json.loads((target / ".claude/settings.json").read_text())["hooks"]
    assert not hooks.get("SessionStart")
    assert not hooks.get("UserPromptSubmit")
    commands = [handler["command"] for groups in hooks.values() for group in groups for handler in group["hooks"]]
    assert any("credential-scan.py" in command for command in commands)
    assert any("destructive-gate.py" in command for command in commands)
    assert not any((target / ".claude/hooks").glob("*classifier.py"))
    assert not (target / ".claude/hooks/gov09-capture.py").exists()
    assert not any("artifact-approval" in command for command in commands)
    assert not list((target / ".claude/hooks").glob("*artifact-approval*"))


def test_retired_handler_cleanup_preserves_malformed_settings_for_repair(tmp_path):
    settings = tmp_path / ".claude/settings.json"
    settings.parent.mkdir()
    raw = b'{"hooks": {"UserPromptSubmit": broken content\r\n'
    settings.write_bytes(raw)
    actions = _plan_settings_registration(tmp_path, "dual-agent")
    assert len(actions) == 1 and actions[0].action == "skip"
    assert "Malformed JSON" in actions[0].reason
    _apply_file_actions(tmp_path, actions, update_manifest=False)
    assert settings.read_bytes() == raw
