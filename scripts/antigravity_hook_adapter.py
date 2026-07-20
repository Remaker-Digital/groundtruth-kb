#!/usr/bin/env python3
"""Antigravity adapter for the canonical Loyal Opposition file-safety gate.

Translates native Antigravity run_command, write_to_file,
replace_file_content, and multi_replace_file_content payloads into
the canonical gate's expected format and translates the response back
to Antigravity-compatible output.

This adapter does NOT register itself in harness configuration.
Registration is owned by the later ops child WI-5498.

Specifications: GOV-WORK-TREE-HYGIENE-001, ADR-CROSS-HARNESS-PARITY-001.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "lo-file-safety-gate.py"


def _no_window_creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _to_claude_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert Antigravity payload to Claude-style PreToolUse."""
    tool_name = payload.get("tool_name") or payload.get("tool") or ""

    if tool_name == "run_command":
        tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
        command = tool_input.get("command") or payload.get("command") or ""
        return {"tool_name": "Bash", "tool_input": {"command": command}}

    if tool_name in ("write_to_file", "replace_file_content"):
        tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
        file_path = tool_input.get("file_path") or tool_input.get("path") or ""
        content = tool_input.get("content") or ""
        return {"tool_name": "Write", "tool_input": {"file_path": file_path, "content": content}}

    if tool_name == "multi_replace_file_content":
        tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
        file_path = tool_input.get("file_path") or ""
        edits = tool_input.get("edits") or []
        return {"tool_name": "MultiEdit", "tool_input": {"file_path": file_path, "edits": edits}}

    return payload


def _from_claude_response(claude_response: dict[str, Any]) -> dict[str, Any]:
    """Translate Claude gate response to Antigravity-compatible output."""
    if claude_response.get("decision") == "block":
        reason = claude_response.get("reason") or "blocked by GT-KB LO file-safety gate"
        return {
            "decision": "block",
            "reason": reason,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    return {"decision": "allow"}


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    adapted = _to_claude_payload(payload)

    env = os.environ.copy()
    env.setdefault("GTKB_HARNESS_NAME", "antigravity")
    env.setdefault("GTKB_HARNESS_ID", "C")

    run_kwargs: dict[str, Any] = {
        "input": json.dumps(adapted),
        "capture_output": True,
        "text": True,
        "cwd": str(PROJECT_ROOT),
        "env": env,
        "check": False,
    }
    creationflags = _no_window_creationflags()
    if creationflags:
        run_kwargs["creationflags"] = creationflags

    result = subprocess.run([sys.executable, str(CANONICAL_HOOK)], **run_kwargs)

    if result.stderr:
        sys.stderr.write(result.stderr)

    stdout = result.stdout.strip()
    if stdout:
        try:
            hook_output = json.loads(stdout)
        except json.JSONDecodeError:
            print(stdout)
            return result.returncode
        translated = _from_claude_response(hook_output if isinstance(hook_output, dict) else {})
        print(json.dumps(translated))

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
