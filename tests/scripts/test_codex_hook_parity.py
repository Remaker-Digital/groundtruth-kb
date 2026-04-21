"""Regression checks for Codex hook parity with Agent Red governance hooks."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_codex_hook_parity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_codex_hook_parity", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_codex_hook_parity"] = module
    spec.loader.exec_module(module)
    return module


def test_codex_hook_parity_passes_for_repository_configuration(capsys) -> None:
    module = _load_module()

    assert module.main(["--project-root", str(REPO_ROOT)]) == 0

    output = capsys.readouterr().out
    assert "Codex hook parity: PASS" in output
    assert "Windows shell-portable command forms" in output


def test_codex_hook_parity_requires_session_lifecycle_hook_intent() -> None:
    module = _load_module()

    errors = module.check_project(REPO_ROOT)

    assert not errors
    codex_hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    claude_settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert any(
        "agent-red-hooks" in hook["command"]
        and "session_start_dispatch.py" in hook["command"]
        for group in codex_hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert any(
        "agent-red-hooks" in hook["command"]
        and "session_wrapup_trigger_dispatch.py" in hook["command"]
        for group in codex_hooks["hooks"]["UserPromptSubmit"]
        for hook in group["hooks"]
    )
    assert "Stop" not in codex_hooks["hooks"]
    assert any(
        "session_self_initialization.py" in hook["command"]
        and "--emit-report" in hook["command"]
        and "--fast-hook" in hook["command"]
        for group in claude_settings["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert any(
        "session_self_initialization.py" in hook["command"]
        and "--emit-wrapup" in hook["command"]
        and "--fast-hook" in hook["command"]
        for group in claude_settings["hooks"]["Stop"]
        for hook in group["hooks"]
    )


def test_codex_hook_commands_avoid_shell_specific_command_substitution() -> None:
    codex_hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for groups in codex_hooks["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]

    assert commands
    assert all("$(" not in command for command in commands)
    assert any(
        "agent-red-hooks" in command
        and "session_start_dispatch.py" in command
        and command.startswith("python ")
        for command in commands
    )
    assert any(
        "agent-red-hooks" in command
        and "session_wrapup_trigger_dispatch.py" in command
        and command.startswith("python ")
        for command in commands
    )

    start_dispatcher = Path.home() / ".codex" / "agent-red-hooks" / "session_start_dispatch.py"
    if not start_dispatcher.is_file():
        assert os.environ.get("CI") == "true"
        return

    start_text = start_dispatcher.read_text(encoding="utf-8")
    assert "--emit-report" in start_text
    assert "prime-builder" in start_text
    assert "codex-loyal-opposition" not in start_text
    assert "Role: Prime Builder" in start_text
    assert "Role mapping source" in start_text
    assert "subprocess.Popen" in start_text
    assert "session-startup-report.md" in start_text
    assert "Startup First-Response Directive" in start_text
    assert "The startup disclosure must be the only assistant message for that turn" in start_text
    assert "Do not send a separate wrap-up, completion, status, or summary message" in start_text
    assert "stop and wait for Mike's next input" in start_text
    assert "Preserve the Wrap-Up Trigger Commands section" in start_text
    assert "Do not reduce it to a pass/fail summary" in start_text
    assert "Startup Disclosure first" in start_text
    assert "Each session focus option must include its specific prompt details" in start_text
    assert "Session Focus Choices second and last" in start_text
    assert "collect or confirm Mike's session focus" in start_text
    assert "choose the number shown" in start_text
    assert "provide a prompt for something else" in start_text
    assert ".session-lifecycle-guard.json" in start_text
    assert "GTKB_STARTUP_GUARD_ID" in start_text
    assert "suppress_next_wrapup" in start_text
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in start_text
    assert "Would you like to proceed with established priority actions? (Y/N)" not in start_text
    assert "Token Consumption Reduction Options second" not in start_text
    assert "Three Top Priority Actions third" not in start_text
    assert "hookSpecificOutput" in start_text
    assert "hookEventName" in start_text
    assert "SessionStart" in start_text
    assert "additionalContext" in start_text
    assert "last-session-start.json" in start_text
    assert "last-session-start.err" in start_text

    wrapup_dispatcher = Path.home() / ".codex" / "agent-red-hooks" / "session_wrapup_trigger_dispatch.py"
    wrapup_text = wrapup_dispatcher.read_text(encoding="utf-8")
    assert "--emit-wrapup" in wrapup_text
    assert "--force-wrapup" in wrapup_text
    assert "prime-builder" in wrapup_text
    assert "codex-loyal-opposition" not in wrapup_text
    assert "UserPromptSubmit" in wrapup_text
    assert "ACCEPTED_TRIGGER_PHRASES" in wrapup_text
    assert "_is_wrapup_trigger" in wrapup_text
    assert "please$" in wrapup_text
    assert "wrap up this session" in wrapup_text
    assert "start a new session" in wrapup_text
    assert "begin fresh" in wrapup_text
    assert "subprocess.run" in wrapup_text
    assert 'print("{}")' in wrapup_text
    assert "hookSpecificOutput" in wrapup_text
    assert "hookEventName" in wrapup_text
    assert "additionalContext" in wrapup_text
    assert "last-wrapup-trigger.json" in wrapup_text
    assert "last-wrapup-trigger.err" in wrapup_text
    assert "last-wrapup-trigger-input.json" in wrapup_text


def test_codex_hook_parity_reports_missing_codex_hooks(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "settings.json").parent.mkdir(exist_ok=True)
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python .claude/hooks/formal-artifact-approval-gate.py",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert any(".codex/hooks.json" in error for error in errors)


def test_codex_hook_parity_requires_bash_matcher(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts" / "session_self_initialization.py").write_text(
        "print('startup')\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python .claude/hooks/formal-artifact-approval-gate.py",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".codex" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Edit|Write",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": (
                                        "python \"$(git rev-parse --show-toplevel)/"
                                        ".claude/hooks/formal-artifact-approval-gate.py\""
                                    ),
                                    "timeout": 5,
                                }
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert "Codex formal artifact PreToolUse hook must use matcher = 'Bash'" in errors
