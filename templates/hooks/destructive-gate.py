#!/usr/bin/env python3
"""
PreToolUse hook: destructive command gate.

Blocks dangerous Bash commands that could cause irreversible damage.
Reads stdin JSON payload (hook_event_name, tool_name, tool_input) and emits
structured deny output (exit 0 + permissionDecision:"deny") when a destructive
command is detected.

Hook type: PreToolUse (tool: Bash)

Usage:
  Called by Claude Code via stdin JSON.
  Run --self-test to verify detection logic: exits 0, emits deny JSON.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json

# Patterns that indicate destructive operations.
# Each tuple: (compiled regex, human-readable description).
import re
import sys

DESTRUCTIVE_PATTERNS = [
    (re.compile(r"\bgit\s+rm\b"), "git rm (file removal from repository)"),
    (re.compile(r"\bgit\s+push\s+--force\b"), "git push --force (force push)"),
    (re.compile(r"\bgit\s+push\s+-f\b"), "git push -f (force push)"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard (hard reset)"),
    (re.compile(r"\bgit\s+clean\s+-[a-z]*f"), "git clean -f (force clean)"),
    (re.compile(r"\bgit\s+branch\s+-D\b"), "git branch -D (force delete branch)"),
    (re.compile(r"\brm\s+-[a-z]*r[a-z]*f"), "rm -rf (recursive force delete)"),
    (re.compile(r"\brm\s+-[a-z]*f[a-z]*r"), "rm -rf (recursive force delete)"),
    (re.compile(r"\bdel\s+/s\b", re.IGNORECASE), "del /s (recursive delete on Windows)"),
    (re.compile(r"\brmdir\s+/s\b", re.IGNORECASE), "rmdir /s (recursive directory delete)"),
    (re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE), "DROP TABLE (table deletion)"),
    (re.compile(r"\bDROP\s+DATABASE\b", re.IGNORECASE), "DROP DATABASE (database deletion)"),
    (re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE), "DELETE FROM (row deletion)"),
    (re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE), "TRUNCATE TABLE (table truncation)"),
]

SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "git reset --hard"},
    "session_id": "test",
    "cwd": "/fake",
}


def _check_command(command: str) -> str | None:
    """Return description of first destructive pattern found, or None."""
    for pattern, description in DESTRUCTIVE_PATTERNS:
        if pattern.search(command):
            return description
    return None


def main() -> None:
    # Import here so the module can be imported without the governance package
    # being on the path during template copying
    try:
        from groundtruth_kb.governance.output import emit_deny, emit_pass
    except ImportError:
        # Fallback inline implementation for environments without groundtruth_kb installed
        def emit_deny(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
            print(json.dumps(out))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        description = _check_command(SELF_TEST_PAYLOAD["tool_input"]["command"])  # type: ignore[index]
        if description is None:
            print("Self-test error: test payload not detected as destructive", file=sys.stderr)
            sys.exit(1)
        emit_deny("PreToolUse", f"Destructive command blocked by governance gate: {description}")
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    if not command:
        emit_pass()
        sys.exit(0)

    description = _check_command(command)
    if description is not None:
        emit_deny(
            "PreToolUse",
            f"Destructive command blocked by governance gate: {description}. "
            "Request owner approval before running destructive operations.",
        )
        sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
