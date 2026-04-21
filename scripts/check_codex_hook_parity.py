#!/usr/bin/env python3
"""Verify Codex hook intent stays aligned with Agent Red governance hooks."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMAL_APPROVAL_HOOK = ".claude/hooks/formal-artifact-approval-gate.py"
SESSION_SELF_INITIALIZATION_SCRIPT = "scripts/session_self_initialization.py"
CODEX_CONFIG = ".codex/config.toml"
CODEX_HOOKS = ".codex/hooks.json"
CLAUDE_SETTINGS = ".claude/settings.json"
CODEX_WRAPPER_DIR = Path.home() / ".codex" / "agent-red-hooks"
CODEX_FORMAL_APPROVAL_WRAPPER = CODEX_WRAPPER_DIR / "formal-artifact-approval.cmd"
CODEX_SESSION_START_WRAPPER = CODEX_WRAPPER_DIR / "session-start.cmd"
CODEX_SESSION_START_DISPATCHER = CODEX_WRAPPER_DIR / "session_start_dispatch.py"
CODEX_SESSION_STOP_DISPATCHER = CODEX_WRAPPER_DIR / "session_stop_dispatch.py"
CODEX_WRAPUP_TRIGGER_DISPATCHER = CODEX_WRAPPER_DIR / "session_wrapup_trigger_dispatch.py"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _commands_for_event(hooks_document: dict[str, Any], event_name: str) -> list[str]:
    commands: list[str] = []
    for group in hooks_document.get("hooks", {}).get(event_name, []):
        for hook in group.get("hooks", []):
            command = hook.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def _contains_hook_path(command: str, hook_path: str) -> bool:
    normalized_command = command.replace("\\", "/").lower()
    normalized_hook_path = hook_path.replace("\\", "/").lower()
    return normalized_hook_path in normalized_command


def _contains_path(command: str, path: Path) -> bool:
    normalized_command = command.replace("\\", "/").lower()
    normalized_path = path.as_posix().lower()
    return normalized_path in normalized_command


def _contains_hook_wrapper(command: str, wrapper_path: Path) -> bool:
    """Return true for the project-intended wrapper path across runner homes."""
    normalized_command = command.replace("\\", "/").lower()
    normalized_path = wrapper_path.as_posix().lower()
    wrapper_fragment = f"agent-red-hooks/{wrapper_path.name.lower()}"
    return normalized_path in normalized_command or wrapper_fragment in normalized_command


def _uses_shell_command_substitution(command: str) -> bool:
    return "$(" in command


def _wrapper_errors(wrapper_path: Path, required_terms: list[str]) -> list[str]:
    if not wrapper_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex hook wrapper: {wrapper_path}"]
    text = wrapper_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in required_terms:
        if term not in text:
            errors.append(f"Codex hook wrapper {wrapper_path.name} must include {term}")
    return errors


def _wrapup_trigger_errors(wrapper_path: Path) -> list[str]:
    dispatcher_path = CODEX_WRAPUP_TRIGGER_DISPATCHER
    if not dispatcher_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex wrap-up trigger dispatcher: {dispatcher_path}"]
    text = dispatcher_path.read_text(encoding="utf-8")
    errors = _wrapper_errors(
        dispatcher_path,
        [
            "session_self_initialization.py",
            "--emit-wrapup",
            "--force-wrapup",
            "--fast-hook",
            "prime-builder",
            "UserPromptSubmit",
            "ACCEPTED_TRIGGER_PHRASES",
            "_is_wrapup_trigger",
            "wrap up this session",
            "start a new session",
            "begin fresh",
            "subprocess.run",
            'print("{}")',
            "hookSpecificOutput",
            "hookEventName",
            "additionalContext",
        ],
    )
    for term in ("last-wrapup-trigger.json", "last-wrapup-trigger.err", "last-wrapup-trigger-input.json"):
        if term not in text:
            errors.append(f"Codex wrap-up trigger dispatcher {dispatcher_path.name} must capture diagnostics")
    if "codex-loyal-opposition" in text:
        errors.append("Codex wrap-up trigger dispatcher must not force the Loyal Opposition role profile")
    return errors


def _start_wrapper_errors(wrapper_path: Path) -> list[str]:
    dispatcher_path = CODEX_SESSION_START_DISPATCHER
    if not dispatcher_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex SessionStart hook dispatcher: {dispatcher_path}"]
    text = dispatcher_path.read_text(encoding="utf-8")
    errors = _wrapper_errors(
        dispatcher_path,
        [
            "session_self_initialization.py",
            "--emit-report",
            "--fast-hook",
            "prime-builder",
            "subprocess.Popen",
            "session-startup-report.md",
            "Startup First-Response Directive",
            "The startup disclosure must be the only assistant message for that turn",
            "Do not send a separate wrap-up, completion, status, or summary message",
            "stop and wait for Mike's next input",
            "Preserve the Wrap-Up Trigger Commands section",
            "collect or confirm Mike's session focus",
            "Each session focus option must include its specific prompt details",
            "choose the number shown",
            "provide a prompt for something else",
            ".session-lifecycle-guard.json",
            "GTKB_STARTUP_GUARD_ID",
            "suppress_next_wrapup",
            "hookSpecificOutput",
            "hookEventName",
            "SessionStart",
            "additionalContext",
        ],
    )
    for forbidden_term in (
        "Would you like to optimize token consumption now or defer to the next session? (Y/N)",
        "Would you like to proceed with established priority actions? (Y/N)",
        "Token Consumption Reduction Options second",
        "Three Top Priority Actions third",
    ):
        if forbidden_term in text:
            errors.append(
                f"Codex SessionStart hook dispatcher {dispatcher_path.name} must not include legacy first-response prompt text: {forbidden_term}"
            )
    for term in ("last-session-start.json", "last-session-start.err"):
        if term not in text:
            errors.append(f"Codex SessionStart hook dispatcher {dispatcher_path.name} must capture stdout/stderr diagnostics")
    if "codex-loyal-opposition" in text:
        errors.append("Codex SessionStart hook dispatcher must not force the Loyal Opposition role profile")
    return errors


def _codex_formal_hook_groups(codex_hooks: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group in codex_hooks.get("hooks", {}).get("PreToolUse", []):
        commands = [
            hook.get("command", "")
            for hook in group.get("hooks", [])
            if isinstance(hook.get("command"), str)
        ]
        if any(
            _contains_hook_path(command, FORMAL_APPROVAL_HOOK)
            or _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER)
            for command in commands
        ):
            groups.append(group)
    return groups


def check_project(project_root: Path = PROJECT_ROOT) -> list[str]:
    """Return parity errors for the configured project, or an empty list."""

    errors: list[str] = []
    codex_config_path = project_root / CODEX_CONFIG
    codex_hooks_path = project_root / CODEX_HOOKS
    claude_settings_path = project_root / CLAUDE_SETTINGS
    formal_hook_path = project_root / FORMAL_APPROVAL_HOOK
    session_startup_path = project_root / SESSION_SELF_INITIALIZATION_SCRIPT

    for path in (codex_config_path, codex_hooks_path, claude_settings_path, formal_hook_path, session_startup_path):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(project_root).as_posix()}")

    if errors:
        return errors

    codex_config = _load_toml(codex_config_path)
    codex_hooks = _load_json(codex_hooks_path)
    claude_settings = _load_json(claude_settings_path)

    if codex_config.get("features", {}).get("codex_hooks") is not True:
        errors.append(".codex/config.toml must set [features].codex_hooks = true")

    claude_pre_tool_commands = _commands_for_event(claude_settings, "PreToolUse")
    if not any(_contains_hook_path(command, FORMAL_APPROVAL_HOOK) for command in claude_pre_tool_commands):
        errors.append(".claude/settings.json does not register the formal artifact approval PreToolUse hook")

    claude_session_commands = _commands_for_event(claude_settings, "SessionStart")
    if not any(_contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT) for command in claude_session_commands):
        errors.append(".claude/settings.json does not register the session self-initialization SessionStart hook")
    if not any("--emit-report" in command for command in claude_session_commands):
        errors.append("Claude SessionStart hook must emit the startup report")
    if not any("--fast-hook" in command for command in claude_session_commands):
        errors.append("Claude SessionStart hook must use the fast lifecycle hook path")

    claude_stop_commands = _commands_for_event(claude_settings, "Stop")
    if not any(_contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT) for command in claude_stop_commands):
        errors.append(".claude/settings.json does not register the proactive session wrap-up Stop hook")
    if not any("--emit-wrapup" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must emit the proactive wrap-up report")
    if not any("--fast-hook" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must use the fast lifecycle hook path")

    formal_groups = _codex_formal_hook_groups(codex_hooks)
    if not formal_groups:
        errors.append(".codex/hooks.json does not register the formal artifact approval PreToolUse hook")
    for group in formal_groups:
        if group.get("matcher") != "Bash":
            errors.append("Codex formal artifact PreToolUse hook must use matcher = 'Bash'")
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if not isinstance(command, str) or not (
                _contains_hook_path(command, FORMAL_APPROVAL_HOOK)
                or _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER)
            ):
                continue
            if hook.get("type") != "command":
                errors.append("Codex formal artifact hook must be a command hook")
            if _uses_shell_command_substitution(command):
                errors.append("Codex formal artifact hook command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER):
                errors.append("Codex formal artifact hook command must call the no-space wrapper")
            timeout = hook.get("timeout")
            if not isinstance(timeout, int) or timeout > 10:
                errors.append("Codex formal artifact hook timeout must be an integer no greater than 10 seconds")

    errors.extend(_wrapper_errors(CODEX_FORMAL_APPROVAL_WRAPPER, [FORMAL_APPROVAL_HOOK.replace("/", "\\")]))
    stop_commands = _commands_for_event(codex_hooks, "Stop")
    if any(
        _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT)
        or _contains_hook_wrapper(command, CODEX_SESSION_STOP_DISPATCHER)
        or _contains_hook_wrapper(command, CODEX_WRAPUP_TRIGGER_DISPATCHER)
        for command in stop_commands
    ):
        errors.append(
            "Codex wrap-up must not be registered on Stop; use the explicit UserPromptSubmit trigger dispatcher"
        )

    lifecycle_wrappers = {
        "SessionStart": (CODEX_SESSION_START_DISPATCHER, "--emit-report"),
        "UserPromptSubmit": (CODEX_WRAPUP_TRIGGER_DISPATCHER, "--emit-wrapup"),
    }

    for event_name, (wrapper_path, _required_flag) in lifecycle_wrappers.items():
        commands = _commands_for_event(codex_hooks, event_name)
        matching_commands = [
            command
            for command in commands
            if _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT)
            or _contains_hook_wrapper(command, wrapper_path)
        ]
        if not matching_commands:
            errors.append(f".codex/hooks.json does not register the {event_name} session lifecycle hook")
        for command in matching_commands:
            if _uses_shell_command_substitution(command):
                errors.append(f"Codex {event_name} hook command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, wrapper_path):
                errors.append(f"Codex {event_name} hook command must call the no-space wrapper")
        if event_name == "UserPromptSubmit":
            errors.extend(_wrapup_trigger_errors(wrapper_path))
        else:
            errors.extend(_start_wrapper_errors(wrapper_path))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    errors = check_project(args.project_root.resolve())
    if errors:
        print("Codex hook parity: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Codex hook parity: PASS")
    print("Note: Codex hook commands are checked for Windows shell-portable command forms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
