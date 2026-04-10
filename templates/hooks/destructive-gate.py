#!/usr/bin/env python3
"""
PreToolUse hook: destructive command gate.

Blocks dangerous Bash commands that could cause irreversible damage.
Reads TOOL_INPUT env var (JSON with "command" key) and exits 2 if the
command matches a destructive pattern.

Hook type: PreToolUse (tool: Bash)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import json
import os
import re
import sys


# Patterns that indicate destructive operations.
# Each tuple: (compiled regex, human-readable description).
DESTRUCTIVE_PATTERNS = [
    # Git destructive operations
    (re.compile(r"\bgit\s+rm\b"), "git rm (file removal from repository)"),
    (re.compile(r"\bgit\s+push\s+--force\b"), "git push --force (force push)"),
    (re.compile(r"\bgit\s+push\s+-f\b"), "git push -f (force push)"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard (hard reset)"),
    (re.compile(r"\bgit\s+clean\s+-[a-z]*f"), "git clean -f (force clean)"),
    (re.compile(r"\bgit\s+branch\s+-D\b"), "git branch -D (force delete branch)"),
    # File system destructive operations
    (re.compile(r"\brm\s+-[a-z]*r[a-z]*f"), "rm -rf (recursive force delete)"),
    (re.compile(r"\brm\s+-[a-z]*f[a-z]*r"), "rm -rf (recursive force delete)"),
    (re.compile(r"\bdel\s+/s\b", re.IGNORECASE), "del /s (recursive delete on Windows)"),
    (re.compile(r"\brmdir\s+/s\b", re.IGNORECASE), "rmdir /s (recursive directory delete)"),
    # Database destructive operations
    (re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE), "DROP TABLE (table deletion)"),
    (re.compile(r"\bDROP\s+DATABASE\b", re.IGNORECASE), "DROP DATABASE (database deletion)"),
    (re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE), "DELETE FROM (row deletion)"),
    (re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE), "TRUNCATE TABLE (table truncation)"),
]


def main():
    tool_input_raw = os.environ.get("TOOL_INPUT", "")
    if not tool_input_raw:
        sys.exit(0)

    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    for pattern, description in DESTRUCTIVE_PATTERNS:
        if pattern.search(command):
            print(
                f"Hook PreToolUse:Bash denied this tool\n"
                f"Blocked destructive command: {description}\n"
                f"Command: {command}\n"
                f"Request owner approval before running destructive operations."
            )
            sys.exit(2)

    # Command is safe to proceed.
    sys.exit(0)


if __name__ == "__main__":
    main()
