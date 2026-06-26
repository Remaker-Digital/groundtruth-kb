# (c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""Activation tests for the WI-4788 black-box dispatcher gate (slice 2).

Slice 1 unit-tested the gate decision logic in the gate module's own suite. This
slice verifies the *activation*: that ``scripts/dispatch_blackbox_gate.py`` is
registered as a Claude PreToolUse hook covering Write/Edit, and that the
registered command actually denies a protected dispatcher write when invoked the
way the hook invokes it (a JSON payload on stdin) while allowing a benign write.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SETTINGS = _REPO_ROOT / ".claude" / "settings.json"
_GATE = _REPO_ROOT / "scripts" / "dispatch_blackbox_gate.py"


def _pretooluse_blocks() -> list[dict]:
    settings = json.loads(_SETTINGS.read_text(encoding="utf-8"))
    return settings.get("hooks", {}).get("PreToolUse", []) or []


def test_blackbox_gate_registered() -> None:
    """The gate is registered under a PreToolUse matcher covering Write and Edit."""
    matchers = []
    for block in _pretooluse_blocks():
        cmds = [h.get("command", "") for h in block.get("hooks", [])]
        if any("dispatch_blackbox_gate.py" in c for c in cmds):
            matchers.append(block.get("matcher", ""))
    assert matchers, "dispatch_blackbox_gate.py is not registered in any PreToolUse block"
    assert any("Write" in m and "Edit" in m for m in matchers), (
        f"gate registered but no matcher covers Write+Edit: {matchers}"
    )


def _invoke_gate(payload: dict, tmp_path: Path) -> dict:
    """Invoke the gate exactly as the PreToolUse hook does: JSON payload on stdin."""
    env = {**os.environ, "GTKB_GATE_DENIALS_PATH": str(tmp_path / "denials.jsonl")}
    proc = subprocess.run(
        [sys.executable, str(_GATE)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout or "{}")


def test_registered_gate_denies_protected_write(tmp_path: Path) -> None:
    """The registered command denies a Write to dispatcher config; allows a benign write."""
    denied = _invoke_gate(
        {"tool_name": "Write", "tool_input": {"file_path": "config/dispatcher/rules.toml"}},
        tmp_path,
    )
    deny = denied.get("hookSpecificOutput", {})
    assert deny.get("permissionDecision") == "deny", denied
    assert "WI-4788" in (deny.get("permissionDecisionReason") or "")

    allowed = _invoke_gate(
        {"tool_name": "Write", "tool_input": {"file_path": "README.md"}},
        tmp_path,
    )
    assert allowed == {}, allowed


_CURSOR_HOOKS = _REPO_ROOT / ".cursor" / "hooks.json"


def test_blackbox_gate_registered_on_cursor() -> None:
    """The gate is registered on Cursor's preToolUse Write surface via cursor_hook_adapter (WI-4788 s3)."""
    cfg = json.loads(_CURSOR_HOOKS.read_text(encoding="utf-8"))
    pretooluse = cfg.get("hooks", {}).get("preToolUse", []) or []
    matched = [
        entry
        for entry in pretooluse
        if "dispatch_blackbox_gate.py" in entry.get("command", "")
        and "cursor_hook_adapter.py" in entry.get("command", "")
    ]
    assert matched, "dispatch_blackbox_gate.py not registered in .cursor/hooks.json preToolUse"
    assert any(entry.get("matcher") == "Write" for entry in matched), (
        f"gate registered on Cursor but not under a Write matcher: {matched}"
    )
