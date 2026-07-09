# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5071: every ``.claude/settings.json`` hook must launch headless (``pythonw``), not bare ``python``.

Reintroduction guard for ``DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS``: a dispatched,
headless Claude worker has no console to inherit, so a bare-``python`` hook child
allocates a NEW visible console window on every SessionStart / UserPromptSubmit /
PreToolUse / PostToolUse / Stop. Bringing the Claude hook-launch surface to parity
with the Codex surface (``.codex/hooks.json`` already launches its identical governance
hooks via ``pythonw``) requires every hook command to use the no-console ``pythonw``
interpreter. This test fails if any hook command reintroduces a bare ``python`` launch,
so the regression cannot silently return. Because ``platform_tests`` runs in CI, the
guard is self-enforcing without any local pre-commit hook or runtime window suppressor,
honoring the owner constraint that nothing may block manual window/GUI launches.

Spec-derived per ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` and
``ADR-CROSS-HARNESS-PARITY-001``; bridge thread
``gtkb-wi5071-claude-hook-headless-parity`` (GO at ``-002``).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SETTINGS = _REPO_ROOT / ".claude" / "settings.json"

# A hook command launches headless when its interpreter token is ``pythonw`` (the
# no-console Windows Python). A bare ``python`` / ``python.exe`` interpreter is the
# console-spawning reintroduction this guard forbids.
_BARE_PYTHON_RE = re.compile(r"^\s*python(\.exe)?\s", re.IGNORECASE)
_PYTHONW_RE = re.compile(r"^\s*pythonw(\.exe)?\s", re.IGNORECASE)


def _hook_commands() -> list[str]:
    data = json.loads(_SETTINGS.read_text(encoding="utf-8"))
    commands: list[str] = []
    for event_groups in data.get("hooks", {}).values():
        for group in event_groups:
            for hook in group.get("hooks", []):
                command = hook.get("command")
                if isinstance(command, str) and command.strip():
                    commands.append(command)
    return commands


def test_settings_json_is_valid_and_registers_hook_commands() -> None:
    commands = _hook_commands()
    assert commands, "expected at least one registered hook command in .claude/settings.json"


def test_no_hook_launches_via_bare_python() -> None:
    bare = [command for command in _hook_commands() if _BARE_PYTHON_RE.match(command)]
    assert bare == [], (
        "WI-5071: .claude/settings.json hook commands must launch via `pythonw` (no-console) so "
        "headless dispatched Claude workers do not spawn visible console windows; "
        f"bare-`python` launches found: {bare}"
    )


def test_every_hook_launches_via_pythonw() -> None:
    non_pythonw = [command for command in _hook_commands() if not _PYTHONW_RE.match(command)]
    assert non_pythonw == [], (
        "every .claude/settings.json hook command must launch via the headless `pythonw` "
        f"interpreter; non-pythonw launches: {non_pythonw}"
    )
