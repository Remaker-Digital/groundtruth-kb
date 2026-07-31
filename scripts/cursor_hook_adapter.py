#!/usr/bin/env python3
"""Adapt Cursor hook stdin/stdout to GT-KB Claude/Codex hook contracts.

Uses the shared lo_file_safety_payloads normalization layer for Shell and
Write payload shapes while preserving Cursor's existing deny-response
translation and metadata defaults.

Specifications: ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_SCRIPTS = PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from lo_file_safety_payloads import normalize_cursor
except ImportError:
    normalize_cursor = None  # type: ignore[assignment]


def _windows_no_window_creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.buffer.read()
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8-sig"))


def _to_claude_pretooluse(payload: dict[str, Any]) -> dict[str, Any]:
    # Use shared normalizer when available
    if normalize_cursor is not None:
        normalized = normalize_cursor(payload)
        if normalized.mutation_class.value in ("shell", "opaque") and normalized.command:
            return {"tool_name": "Bash", "tool_input": {"command": normalized.command}}
        if normalized.tool_name in ("Write", "Edit", "MultiEdit"):
            return {
                "tool_name": normalized.tool_name,
                "tool_input": payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {},
            }

    # Fallback
    command = payload.get("command")
    if isinstance(command, str) and command.strip():
        return {"tool_name": "Bash", "tool_input": {"command": command}}

    tool_name = payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or payload.get("input") or {}
    if isinstance(tool_name, str):
        return {"tool_name": tool_name, "tool_input": tool_input if isinstance(tool_input, dict) else {}}

    hook_event = os.environ.get("CURSOR_HOOK_EVENT", "")
    if hook_event in {"beforeShellExecution", "afterShellExecution"}:
        command = payload.get("command")
        if isinstance(command, str):
            return {"tool_name": "Bash", "tool_input": {"command": command}}

    return payload


def _from_claude_response(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("decision") == "block":
        reason = payload.get("reason") or payload.get("systemMessage") or "blocked by GT-KB hook"
        return {"permission": "deny", "user_message": reason, "agent_message": reason}
    if payload.get("systemMessage"):
        return {"additional_context": payload["systemMessage"]}
    if payload.get("hookSpecificOutput"):
        return {"additional_context": json.dumps(payload["hookSpecificOutput"])}
    return {}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: cursor_hook_adapter.py <target-hook-script> [args...]", file=sys.stderr)
        return 2

    target = Path(sys.argv[1])
    if not target.is_file():
        print(f"cursor_hook_adapter: missing hook script {target}", file=sys.stderr)
        return 1

    payload = _read_payload()
    adapted_in = _to_claude_pretooluse(payload)
    env = os.environ.copy()
    env.setdefault("GTKB_HARNESS_NAME", "cursor")
    env.setdefault("GTKB_HARNESS_ID", "E")
    env.setdefault("GTKB_AUTHOR_MODEL", "Composer")
    env.setdefault("GTKB_AUTHOR_MODEL_VERSION", "cursor-agent")
    env.setdefault(
        "GTKB_AUTHOR_MODEL_CONFIGURATION",
        "Cursor interactive; cursor_hook_adapter; bridge author metadata runtime envelope",
    )

    run_kwargs: dict[str, Any] = {
        "input": json.dumps(adapted_in),
        "capture_output": True,
        "text": True,
        "cwd": str(PROJECT_ROOT),
        "env": env,
        "check": False,
    }
    creationflags = _windows_no_window_creationflags()
    if creationflags:
        run_kwargs["creationflags"] = creationflags

    completed = subprocess.run([sys.executable, str(target), *sys.argv[2:]], **run_kwargs)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    stdout = completed.stdout.strip()
    if stdout:
        try:
            hook_payload = json.loads(stdout)
        except json.JSONDecodeError:
            print(stdout)
            return completed.returncode
        adapted_out = _from_claude_response(hook_payload if isinstance(hook_payload, dict) else {})
        if adapted_out:
            print(json.dumps(adapted_out))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
