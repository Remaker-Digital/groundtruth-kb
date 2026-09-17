#!/usr/bin/env python3
"""PreToolUse adapter for checkout containment and command checks."""

import json
import os
import sys
from pathlib import Path

from groundtruth_kb.enforcement import check_bash_command, check_path_boundary


def _project_root_from_env() -> Path:
    return Path(os.environ.get("{{HARNESS_PROJECT_DIR_VAR}}") or os.getcwd()).resolve()


def emit_deny(reason: str) -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "additionalContext": reason,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


def emit_pass() -> None:
    print("{}")
    sys.exit(0)


def main() -> None:
    if "--self-test" in sys.argv:
        emit_deny("[Enforcement] Self-test active.")

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd") or str(_project_root_from_env())
    project_root = Path(cwd).resolve()

    # Find the nearest groundtruth.toml to resolve canonical root
    for candidate in (project_root, *project_root.parents):
        if (candidate / "groundtruth.toml").is_file():
            project_root = candidate
            break

    # 1. Handle command execution (bash, run_command, command, etc.)
    if tool_name.lower() in {"bash", "powershell", "run_command"}:
        command = tool_input.get("command") or tool_input.get("CommandLine") or ""
        if command:
            allowed, reason = check_bash_command(command, project_root)
            if not allowed:
                emit_deny(f"Command blocked by directive: {reason}")
        emit_pass()

    # 2. Extract potential paths from tool_input
    path_args = []
    keys_to_check = {
        "file_path",
        "target_file",
        "TargetFile",
        "path",
        "AbsolutePath",
        "source",
        "destination",
        "target",
        "source_file",
        "dest_file",
    }

    for key in keys_to_check:
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            path_args.append(val.strip())
        elif isinstance(val, list):
            for v in val:
                if isinstance(v, str) and v.strip():
                    path_args.append(v.strip())

    # 3. Check each path argument
    for path_str in path_args:
        allowed, reason = check_path_boundary(path_str, project_root)
        if not allowed:
            emit_deny(f"Tool execution blocked: {reason}")

    emit_pass()


if __name__ == "__main__":
    main()
