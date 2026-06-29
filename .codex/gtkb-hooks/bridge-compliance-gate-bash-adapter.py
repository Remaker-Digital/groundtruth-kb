#!/usr/bin/env python3
"""Codex Bash adapter for the GT-KB bridge-compliance gate."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
SKIPPED_DIAGNOSTIC = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "last-bridge-audit-skipped.json"
BRIDGE_FILE_WRITE_PATTERNS = (
    re.compile(
        r"(?P<cmd>cat|printf|echo)\b(?P<body>.*?)(?:>\s*|>>\s*)"
        r"(?P<path>bridge/[^\s\"']+(?:-\d{3}|\.lo-verdict)\.md)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\btee\s+(?P<path>bridge/[^\s\"']+(?:-\d{3}|\.lo-verdict)\.md)", re.IGNORECASE),
    re.compile(
        r"(?:Path\(|open\()\s*[\"'](?P<path>bridge/[^\"']+(?:-\d{3}|\.lo-verdict)\.md)[\"']"
        r".*?write(?:_text)?\((?P<body>.*?)\)",
        re.IGNORECASE | re.DOTALL,
    ),
)


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


def _load_payload() -> dict[str, Any]:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def _bash_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input") or {}
    for key in ("command", "script", "cmd"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def _extract_heredoc(command: str) -> tuple[str, str] | None:
    match = re.search(
        r"cat\s*(?:>\s*|>>\s*)"
        r"(?P<path>bridge/[^\s\"']+(?:-\d{3}|\.lo-verdict)\.md)\s*"
        r"<<\s*['\"]?(?P<tag>[A-Za-z0-9_:-]+)['\"]?\s*\n",
        command,
        re.IGNORECASE,
    )
    if not match:
        return None
    tag = match.group("tag")
    body_start = match.end()
    close = re.search(rf"(?m)^{re.escape(tag)}\s*$", command[body_start:])
    if not close:
        _write_skipped("unclosed heredoc", command)
        return None
    body = command[body_start : body_start + close.start()]
    return match.group("path"), body


def _unquote_literal(value: str) -> str:
    stripped = value.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")):
        stripped = stripped[1:-1]
    return stripped.replace("\\n", "\n")


def extract_bridge_write(command: str) -> tuple[str, str] | None:
    """Extract bridge target and candidate content from common Bash write shapes."""
    if re.search(
        r"cat\s*(?:>\s*|>>\s*)bridge/[^\s\"']+(?:-\d{3}|\.lo-verdict)\.md\s*<<",
        command,
        re.IGNORECASE,
    ):
        return _extract_heredoc(command)
    heredoc = _extract_heredoc(command)
    if heredoc:
        return heredoc
    for pattern in BRIDGE_FILE_WRITE_PATTERNS:
        match = pattern.search(command)
        if not match:
            continue
        path = match.group("path")
        body = match.groupdict().get("body") or ""
        return path, _unquote_literal(body.strip())
    if re.search(r"bridge/[^\s\"']+(?:-\d{3}|\.lo-verdict)\.md", command):
        _write_skipped("bridge file write content extraction failed", command)
    return None


def _write_skipped(reason: str, command: str) -> None:
    SKIPPED_DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)
    SKIPPED_DIAGNOSTIC.write_text(
        json.dumps({"skipped": True, "reason": reason, "command": command}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def synthetic_claude_payload(payload: dict[str, Any], file_path: str, content: str) -> dict[str, Any]:
    """Build a synthetic Claude-shape Write payload for the canonical hook."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
        "session_id": payload.get("session_id", "codex-bridge-compliance"),
        "cwd": payload.get("cwd") or str(PROJECT_ROOT),
    }


def main() -> int:
    payload = _load_payload()
    command = _bash_command(payload)
    extracted = extract_bridge_write(command)
    if extracted is None:
        print("{}")
        return 0
    file_path, content = extracted
    synthetic = synthetic_claude_payload(payload, file_path, content)
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(synthetic),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=False,
        **_no_window_subprocess_kwargs(),
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
