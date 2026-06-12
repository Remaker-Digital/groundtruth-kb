"""FAB-14 HYG-042: PowerShell and Codex directive hook coverage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SETTINGS = _ROOT / ".claude" / "settings.json"
_CODEX_HOOKS = _ROOT / ".codex" / "hooks.json"
_CLAUDE_ADAPTER = _ROOT / ".claude" / "hooks" / "directive-enforcement-claude-adapter.py"
_CODEX_ADAPTER = _ROOT / ".codex" / "gtkb-hooks" / "directive-enforcement-adapter.py"


def _run_hook(path: Path, payload: dict, telemetry: Path) -> dict:
    env = os.environ.copy()
    env["GTKB_GATE_DENIALS_PATH"] = str(telemetry)
    proc = subprocess.run(
        [sys.executable, str(path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        cwd=str(_ROOT),
        check=True,
    )
    return json.loads(proc.stdout)


def test_claude_directive_matcher_includes_powershell() -> None:
    settings = json.loads(_CLAUDE_SETTINGS.read_text(encoding="utf-8"))
    matchers = [
        group.get("matcher", "")
        for group in settings["hooks"]["PreToolUse"]
        if any("directive-enforcement-claude-adapter.py" in hook.get("command", "") for hook in group.get("hooks", []))
    ]

    assert any("PowerShell" in matcher.split("|") for matcher in matchers)


def test_codex_registers_directive_adapter_for_bash_and_apply_patch() -> None:
    hooks = json.loads(_CODEX_HOOKS.read_text(encoding="utf-8"))
    registrations = [
        group.get("matcher", "")
        for group in hooks["hooks"]["PreToolUse"]
        if any("directive-enforcement.cmd" in hook.get("command", "") for hook in group.get("hooks", []))
    ]

    assert "Bash" in registrations
    assert "apply_patch" in registrations


def test_powershell_command_false_positive_passes(tmp_path: Path) -> None:
    payload = {
        "tool_name": "PowerShell",
        "tool_input": {"command": "Get-Content bridge/INDEX.md"},
        "cwd": str(_ROOT),
    }

    assert _run_hook(_CLAUDE_ADAPTER, payload, tmp_path / "denials.jsonl") == {}


def test_codex_apply_patch_in_root_path_passes(tmp_path: Path) -> None:
    payload = {
        "tool_name": "apply_patch",
        "tool_input": {
            "patch": "*** Begin Patch\n*** Update File: bridge/INDEX.md\n@@\n*** End Patch\n",
        },
        "cwd": str(_ROOT),
    }

    assert _run_hook(_CODEX_ADAPTER, payload, tmp_path / "denials.jsonl") == {}


def test_codex_bash_out_of_root_blocks_and_logs(tmp_path: Path) -> None:
    telemetry = tmp_path / "denials.jsonl"
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": r"type C:\Users\micha\secret.txt"},
        "cwd": str(_ROOT),
    }

    result = _run_hook(_CODEX_ADAPTER, payload, telemetry)

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    record = json.loads(telemetry.read_text(encoding="utf-8").splitlines()[0])
    assert record["gate"] == "codex-directive-enforcement"
    assert record["pattern_id"] == "root-boundary-command"
    assert len(record["command_hash"]) == 64
