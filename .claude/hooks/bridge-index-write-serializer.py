#!/usr/bin/env python3
"""PreToolUse hook: Bridge INDEX atomic-write guard (WI-4481).

Blocks any agent Write/Edit/MultiEdit/Bash/apply_patch operation that would
mutate ``bridge/INDEX.md`` directly, and directs the agent to the serialized
``gt bridge index`` CLI (``add-document`` / ``set-status``). That CLI holds a
file lock and performs an atomic temp-then-replace read-modify-merge
(``scripts/bridge_index_writer.py``); raw tool-writes bypass the lock and cause
the lost/duplicated Document blocks recorded in WI-4481 (recurring manual owner
repair).

Role-agnostic by design: both Prime Builder and Loyal Opposition raw-writes
clobber the canonical workflow state, so the guard applies to every session.
The serialized CLI writes INDEX inside Python under the lock and names a
versioned ``bridge/<slug>-NNN.md`` path (never ``INDEX.md``) with no shell
redirect, so it is not matched. Reads of INDEX (``cat``/``grep``) carry no write
operator and pass through.

Bridge: bridge/gtkb-bridge-index-atomic-write-guard-002.md (GO)
Specs: GOV-FILE-BRIDGE-AUTHORITY-001 (CLAUSE-INDEX-IS-CANONICAL),
       ADR-CODEX-HOOK-PARITY-FALLBACK-001 (.claude + .codex parity)
Work Item: WI-4481

Stdin: JSON hook payload. Stdout: ``{}`` or a block decision. Exit: always 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

INDEX_REL = "bridge/INDEX.md"

# Bash write to INDEX: a redirect (> / >>) immediately preceding the INDEX path,
# or a PowerShell/Unix write command naming the INDEX path within one command
# segment. A leading quote after the redirect is tolerated (> "bridge/INDEX.md").
# A bare `>` followed by a non-path token (e.g. grep ">" bridge/INDEX.md) does
# NOT match because the redirect form requires the INDEX path to follow directly.
_BASH_WRITE_INDEX_RE = re.compile(
    r">>?\s*['\"]?bridge[/\\]INDEX\.md"
    r"|\b(?:Set-Content|Add-Content|Out-File|tee)\b[^\n;&|]*?bridge[/\\]INDEX\.md",
    re.IGNORECASE,
)

# apply_patch hunk header targeting INDEX (Add/Update/Delete File: ... INDEX.md).
_PATCH_TARGET_INDEX_RE = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s+.*bridge[/\\]INDEX\.md\s*$",
    re.IGNORECASE | re.MULTILINE,
)

_BLOCK_MSG = (
    "BLOCKED (GTKB-INDEX-WRITE-GUARD, WI-4481): bridge/INDEX.md is canonical, "
    "append-only bridge workflow state and must only be mutated through the "
    "serialized writer, which holds a file lock and performs an atomic "
    "read-modify-merge. A raw Write/Edit/Bash/apply_patch to INDEX bypasses the "
    "lock and clobbers concurrent Document blocks (WI-4481). Use the serialized "
    "CLI instead:\n"
    "  - new document block:  python -m groundtruth_kb bridge index add-document "
    "<slug> --status <STATUS> --path bridge/<slug>-NNN.md\n"
    "  - status/verdict line: python -m groundtruth_kb bridge index set-status "
    "<slug> --status <STATUS> --path bridge/<slug>-NNN.md\n"
    "(GOV-FILE-BRIDGE-AUTHORITY-001 / CLAUSE-INDEX-IS-CANONICAL.)"
)


def _emit(decision: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(decision, sort_keys=True))


def _block() -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": _BLOCK_MSG,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": _BLOCK_MSG,
            "additionalContext": _BLOCK_MSG,
        },
    }


def _load_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _project_root(payload: dict[str, Any]) -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return Path(str(root)).resolve()


def _tool_name(payload: dict[str, Any]) -> str:
    return str(payload.get("tool_name") or payload.get("tool") or "")


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input")
    if isinstance(value, dict):
        return value
    arguments = payload.get("arguments")
    return arguments if isinstance(arguments, dict) else {}


def _targets_index_path(file_path: str, root: Path) -> bool:
    """Return True when file_path resolves to bridge/INDEX.md under the project root."""
    if not file_path or file_path.startswith("<"):
        return False
    try:
        raw = Path(file_path)
        absolute = raw if raw.is_absolute() else root / raw
        rel = absolute.resolve().relative_to(root.resolve()).as_posix()
        return rel == INDEX_REL
    except (OSError, ValueError):
        # Unresolvable path: fall back to a suffix match so an INDEX target still trips.
        return file_path.replace("\\", "/").endswith(INDEX_REL)


def _command_text(tool_input: dict[str, Any]) -> str:
    for key in ("command", "script", "cmd"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def _patch_text(payload: dict[str, Any], tool_input: dict[str, Any]) -> str:
    for value in (
        tool_input.get("patch"),
        tool_input.get("input"),
        payload.get("patch"),
        payload.get("input"),
    ):
        if isinstance(value, str) and "*** " in value:
            return value
    return ""


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a block decision when the tool call would mutate bridge/INDEX.md, else {}."""
    root = _project_root(payload)
    tool = _tool_name(payload)
    tool_input = _tool_input(payload)

    if tool in {"Write", "Edit", "MultiEdit"}:
        file_path = tool_input.get("file_path")
        if isinstance(file_path, str) and _targets_index_path(file_path, root):
            return _block()
        return {}

    if tool == "Bash":
        if _BASH_WRITE_INDEX_RE.search(_command_text(tool_input)):
            return _block()
        return {}

    if tool in {"apply_patch", "functions.apply_patch"}:
        if _PATCH_TARGET_INDEX_RE.search(_patch_text(payload, tool_input)):
            return _block()
        return {}

    return {}


def main() -> int:
    if "--self-test" in sys.argv:
        _emit({})
        return 0
    _emit(gate_decision(_load_payload()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
