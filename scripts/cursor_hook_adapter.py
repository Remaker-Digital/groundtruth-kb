#!/usr/bin/env python3
"""Adapt Cursor hook stdin/stdout to GT-KB Claude/Codex hook contracts.

Uses the shared lo_file_safety_payloads normalization layer for Shell and
Write payload shapes while preserving Cursor's existing deny-response
translation and metadata defaults.

Cursor failClosed treats empty stdout and non-0/non-2 exit codes as hook
failure. This adapter therefore always emits a permission JSON object and
maps allow to exit 0 and deny to exit 2, even when the inner Claude-style
hook exits 0 with a block decision or exits 1 with a block JSON.

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


def _deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": reason,
                "agent_message": reason,
            }
        ),
        flush=True,
    )
    return 2


def _allow(extra: dict[str, Any] | None = None) -> int:
    out: dict[str, Any] = {"permission": "allow"}
    if extra:
        out.update(extra)
        out["permission"] = "allow"
    print(json.dumps(out), flush=True)
    return 0


def _emit_cursor(adapted_out: dict[str, Any]) -> int:
    if adapted_out.get("permission") == "deny":
        print(json.dumps(adapted_out), flush=True)
        return 2
    extra = {k: v for k, v in adapted_out.items() if k != "permission"}
    return _allow(extra or None)


def _resolve_target(raw: str) -> Path:
    target = Path(raw)
    if target.is_file():
        return target
    rooted = (PROJECT_ROOT / raw).resolve()
    if rooted.is_file():
        return rooted
    return target


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.buffer.read()
    if not raw:
        return {}
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_claude_pretooluse(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return _to_claude_pretooluse_inner(payload)
    except Exception:
        return payload


def _to_claude_pretooluse_inner(payload: dict[str, Any]) -> dict[str, Any]:
    # Use shared normalizer when available
    if normalize_cursor is not None:
        normalized = normalize_cursor(payload)
        if not normalized.tool_name:
            return payload
        if normalized.mutation_class.value in ("shell", "opaque") and normalized.command:
            return {"tool_name": "Bash", "tool_input": {"command": normalized.command}}
        if normalized.mutation_class.value in ("write", "edit", "delete"):
            tool_input: dict[str, Any] = {}
            if normalized.target_paths:
                tool_input["file_path"] = normalized.target_paths[0]
                tool_input["path"] = normalized.target_paths[0]
            claude_tool = {
                "Write": "Write",
                "StrReplace": "Edit",
                "Edit": "Edit",
                "MultiEdit": "MultiEdit",
                "Delete": "Delete",
            }.get(normalized.tool_name, normalized.tool_name)
            return {"tool_name": claude_tool, "tool_input": tool_input}
        if normalized.mutation_class.value == "read_only":
            raw_input: dict[str, Any] = {}
            if isinstance(normalized.raw_payload, dict):
                candidate = normalized.raw_payload.get("tool_input") or normalized.raw_payload.get("toolInput")
                if isinstance(candidate, dict):
                    raw_input = dict(candidate)
            path = ""
            if normalized.target_paths:
                path = normalized.target_paths[0]
            else:
                path = str(raw_input.get("file_path") or raw_input.get("path") or "")
            if path:
                raw_input["file_path"] = path
                raw_input["path"] = path
            return {"tool_name": normalized.tool_name, "tool_input": raw_input}

    # Fallback
    command = payload.get("command")
    if isinstance(command, str) and command.strip():
        return {"tool_name": "Bash", "tool_input": {"command": command}}

    tool_name = payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or payload.get("input") or {}
    if isinstance(tool_name, str):
        rewritten = dict(tool_input) if isinstance(tool_input, dict) else {}
        path = rewritten.get("file_path") or rewritten.get("path") or payload.get("path")
        if isinstance(path, str) and path.strip():
            rewritten["file_path"] = path
            rewritten["path"] = path
        claude_tool = {"StrReplace": "Edit"}.get(tool_name, tool_name)
        return {"tool_name": claude_tool, "tool_input": rewritten}

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
    extra: dict[str, Any] = {"permission": "allow"}
    if payload.get("systemMessage"):
        extra["additional_context"] = payload["systemMessage"]
    elif payload.get("hookSpecificOutput"):
        extra["additional_context"] = json.dumps(payload["hookSpecificOutput"])
    return extra


def main() -> int:
    if len(sys.argv) < 2:
        return _deny("cursor_hook_adapter: missing target hook script")

    target = _resolve_target(sys.argv[1])
    if not target.is_file():
        return _deny(f"cursor_hook_adapter: missing hook script {sys.argv[1]}")

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
        "encoding": "utf-8",
        "errors": "replace",
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
    stdout = (completed.stdout or "").strip()
    if stdout:
        try:
            hook_payload = json.loads(stdout)
        except json.JSONDecodeError:
            if completed.returncode == 0:
                return _allow()
            reason = stdout.splitlines()[-1] if stdout.splitlines() else "blocked by GT-KB hook"
            return _deny(reason)
        adapted_out = _from_claude_response(hook_payload if isinstance(hook_payload, dict) else {})
        return _emit_cursor(adapted_out)

    if completed.returncode == 0:
        return _allow()
    reason = "blocked by GT-KB hook"
    if completed.stderr:
        lines = [line.strip() for line in completed.stderr.splitlines() if line.strip()]
        if lines:
            reason = lines[-1]
    return _deny(reason)


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:
        code = _deny(f"cursor_hook_adapter: {type(exc).__name__}: {exc}")
    raise SystemExit(code)
