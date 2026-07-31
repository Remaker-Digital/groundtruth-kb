# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Configuration validation tests for dispatcher-only hook registration.

WI-4885 retires harness-owned bridge dispatch hooks. Claude and Codex hooks may
still run governance, session, backlog-reconcile, and advisory helpers, but
they must not launch bridge workers, dispatcher runtime cycles, or retired
single-harness dispatchers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
CODEX_HOOKS_PATH = REPO_ROOT / ".codex" / "hooks.json"

DISPATCH_HOOK_MARKERS = (
    "cross_" + "harness_" + "bridge_" + "trigger.py",
    "dispatcher_runtime.py",
    "gtkb_dispatcher_daemon.py",
    "single_" + "harness_" + "bridge_" + "automation.py",
    "single_" + "harness_" + "bridge_" + "dispatcher.py",
    "bridge-" + "dispatch-trigger.cmd",
    "dispatcher-daemon.cmd",
)


def _load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def claude_settings() -> dict[str, Any]:
    return _load_json(CLAUDE_SETTINGS_PATH)


@pytest.fixture(scope="module")
def codex_hooks() -> dict[str, Any]:
    return _load_json(CODEX_HOOKS_PATH)


def _hook_commands(value: object) -> list[str]:
    commands: list[str] = []
    if isinstance(value, dict):
        command = value.get("command")
        if isinstance(command, str):
            commands.append(command)
        for child in value.values():
            commands.extend(_hook_commands(child))
    elif isinstance(value, list):
        for child in value:
            commands.extend(_hook_commands(child))
    return commands


def _offending_dispatch_commands(config: dict[str, Any]) -> list[str]:
    offenders: list[str] = []
    for command in _hook_commands(config.get("hooks", {})):
        normalized = command.replace("\\", "/")
        if any(marker in normalized for marker in DISPATCH_HOOK_MARKERS):
            offenders.append(command)
    return offenders


def test_claude_hooks_do_not_launch_bridge_dispatch(claude_settings: dict[str, Any]) -> None:
    offenders = _offending_dispatch_commands(claude_settings)
    assert not offenders, "Claude hooks must not launch bridge dispatch automation:\n" + "\n".join(offenders)


def test_codex_hooks_do_not_launch_bridge_dispatch(codex_hooks: dict[str, Any]) -> None:
    offenders = _offending_dispatch_commands(codex_hooks)
    assert not offenders, "Codex hooks must not launch bridge dispatch automation:\n" + "\n".join(offenders)


def test_codex_hooks_file_may_be_empty(codex_hooks: dict[str, Any]) -> None:
    assert "hooks" in codex_hooks
    assert isinstance(codex_hooks["hooks"], dict)


def test_claude_keeps_non_dispatch_governance_hooks(claude_settings: dict[str, Any]) -> None:
    commands = _hook_commands(claude_settings.get("hooks", {}))
    expected_fragments = (
        ".claude/hooks/implementation-start-gate.py",
        ".claude/hooks/bridge-compliance-gate.py",
        "scripts/session_self_initialization.py",
    )
    for fragment in expected_fragments:
        assert any(fragment in command.replace("\\", "/") for command in commands), fragment
