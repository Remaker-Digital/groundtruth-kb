"""WI-5480 (W0.3 item 6): `.cursor/hooks.json` single-invocation regression.

Three gates were registered under BOTH `beforeShellExecution` and `preToolUse`,
so every Cursor shell event spawned each of them twice. This module pins the
deduped state: the three gates are reachable only through `preToolUse`.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 6 (GO at -002);
DCL-CROSS-HARNESS-ENFORCEMENT-001.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_CURSOR_HOOKS_PATH = _ROOT / ".cursor" / "hooks.json"

# The three gates the W0.3 GO deduped out of `beforeShellExecution`.
_DEDUPED_GATES = (
    "destructive-gate.py",
    "credential-scan.py",
    "bridge-compliance-gate.py",
)


def _hooks_document() -> dict:
    return json.loads(_CURSOR_HOOKS_PATH.read_text(encoding="utf-8"))


def _commands_for_event(event: str) -> list[str]:
    entries = _hooks_document().get("hooks", {}).get(event, [])
    return [str(entry.get("command", "")) for entry in entries]


def test_cursor_hooks_json_is_valid_json() -> None:
    document = _hooks_document()
    assert isinstance(document.get("hooks"), dict), ".cursor/hooks.json must carry a `hooks` object"


@pytest.mark.parametrize("gate", _DEDUPED_GATES)
def test_deduped_gate_absent_from_before_shell_execution(gate: str) -> None:
    matching = [command for command in _commands_for_event("beforeShellExecution") if gate in command]
    assert not matching, (
        f"WI-5480 regression: {gate} is registered under beforeShellExecution again. "
        f"It must be reachable only via preToolUse so Cursor shell events do not "
        f"double-spawn it. Offending entries: {matching}"
    )


@pytest.mark.parametrize("gate", _DEDUPED_GATES)
def test_deduped_gate_still_registered_under_pre_tool_use(gate: str) -> None:
    """Dedupe must not become removal: each gate keeps exactly one preToolUse entry."""
    matching = [command for command in _commands_for_event("preToolUse") if gate in command]
    assert len(matching) == 1, (
        f"{gate} must have exactly one preToolUse registration (found {len(matching)}). "
        f"Removing the beforeShellExecution duplicate must not drop the retained gate."
    )


def test_no_command_is_registered_twice_within_an_event() -> None:
    """No event may list the same command string more than once."""
    document = _hooks_document()
    duplicates: dict[str, list[str]] = {}
    for event, entries in document.get("hooks", {}).items():
        seen: set[str] = set()
        repeated = []
        for entry in entries:
            command = str(entry.get("command", ""))
            key = f"{command}::{entry.get('matcher', '')}"
            if key in seen:
                repeated.append(command)
            seen.add(key)
        if repeated:
            duplicates[event] = repeated
    assert not duplicates, f"Duplicate hook registrations within a single Cursor event: {duplicates}"
