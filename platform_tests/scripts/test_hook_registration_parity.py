"""Hook registration parity for implementation-start authorization."""
# ruff: noqa: I001

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_claude_registers_implementation_start_gate_on_mutation_surfaces() -> None:
    settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    groups = settings["hooks"]["PreToolUse"]

    matches = [
        group
        for group in groups
        if any("implementation-start-gate.py" in hook.get("command", "") for hook in group.get("hooks", []))
    ]

    assert matches
    assert any(group.get("matcher") == "Write|Edit|MultiEdit|Bash" for group in matches)


def test_codex_registers_implementation_start_gate_for_bash_and_apply_patch() -> None:
    hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    groups = hooks["hooks"]["PreToolUse"]

    by_matcher = {
        group.get("matcher"): [
            hook.get("command", "")
            for hook in group.get("hooks", [])
            if "implementation-start-gate.cmd" in hook.get("command", "")
        ]
        for group in groups
        if any("implementation-start-gate.cmd" in hook.get("command", "") for hook in group.get("hooks", []))
    }

    assert by_matcher.get("Bash")
    assert by_matcher.get("apply_patch")
    wrapper = REPO_ROOT / ".codex" / "gtkb-hooks" / "implementation-start-gate.cmd"
    assert wrapper.is_file()
    assert "implementation_start_gate.py" in wrapper.read_text(encoding="utf-8")
