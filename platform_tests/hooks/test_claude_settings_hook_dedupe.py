"""WI-5480 (W0.3 item 5): `.claude/settings.json` duplicate-registration regression.

Four retained hook commands were registered twice within the same event, each via a
redundant matcher-less group appended after the primary group. Every duplicate
cost one extra process spawn per event with no added enforcement, because the
second registration was byte-identical to the first.

This module pins the deduped state and, critically, also pins that dedupe did
not become removal: each retained gate keeps exactly one registration.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 5 (GO at -002).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SETTINGS_PATH = _ROOT / ".claude" / "settings.json"

# Retained duplicate-prone commands; automatic assertion startup was retired.
_DEDUPED_REGISTRATIONS = (
    ("PostToolUse", "owner-decision-capture.py"),
    ("PostToolUse", "spec-event-surfacer.py"),
    ("UserPromptSubmit", "intake-classifier.py"),
    ("UserPromptSubmit", "gov09-capture.py"),
)


def _settings_document() -> dict:
    return json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))


def _commands_for_event(event: str) -> list[str]:
    groups = _settings_document().get("hooks", {}).get(event, [])
    return [str(hook.get("command", "")) for group in groups for hook in group.get("hooks", [])]


def test_claude_settings_is_valid_json() -> None:
    document = _settings_document()
    assert isinstance(document.get("hooks"), dict), ".claude/settings.json must carry a `hooks` object"


@pytest.mark.parametrize(("event", "script"), _DEDUPED_REGISTRATIONS)
def test_deduped_hook_registered_exactly_once(event: str, script: str) -> None:
    matching = [command for command in _commands_for_event(event) if script in command]
    assert len(matching) == 1, (
        f"WI-5480 regression: {script} must be registered exactly once under {event} "
        f"(found {len(matching)}). A duplicate registration spawns the hook twice per "
        f"event with no added enforcement; zero means the dedupe dropped the gate."
    )


def test_no_hook_command_is_duplicated_within_an_event() -> None:
    """General invariant: no event may register the same command string twice."""
    document = _settings_document()
    duplicates: dict[str, dict[str, int]] = {}
    for event in document.get("hooks", {}):
        counts = Counter(_commands_for_event(event))
        repeated = {command: count for command, count in counts.items() if count > 1}
        if repeated:
            duplicates[event] = repeated
    assert not duplicates, f"Duplicate hook registrations within a single Claude event: {duplicates}"
