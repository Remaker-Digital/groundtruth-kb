"""Hook registration parity for implementation-start authorization."""
# ruff: noqa: I001

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py"


def _load_codex_hook_wrapper():
    spec = importlib.util.spec_from_file_location("codex_run_py_no_window_parity", WRAPPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _batch_for_command(command: str) -> str | None:
    match = re.search(r"--batch\s+([A-Za-z0-9_-]+)", command)
    return match.group(1) if match else None


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
    wrapper = _load_codex_hook_wrapper()

    by_matcher = {
        group.get("matcher"): [
            _batch_for_command(hook.get("command", ""))
            for hook in group.get("hooks", [])
            if _batch_for_command(hook.get("command", ""))
        ]
        for group in groups
        if any(_batch_for_command(hook.get("command", "")) for hook in group.get("hooks", []))
    }

    assert by_matcher.get("Bash") == ["pretooluse-bash"]
    assert by_matcher.get("apply_patch") == ["pretooluse-apply-patch"]
    assert any("implementation-start-gate.cmd" in " ".join(entry) for entry in wrapper.BATCHES["pretooluse-bash"])
    assert any(
        "implementation-start-gate.cmd" in " ".join(entry) for entry in wrapper.BATCHES["pretooluse-apply-patch"]
    )
    wrapper = REPO_ROOT / ".codex" / "gtkb-hooks" / "implementation-start-gate.cmd"
    assert wrapper.is_file()
    assert "implementation_start_gate.py" in wrapper.read_text(encoding="utf-8")
