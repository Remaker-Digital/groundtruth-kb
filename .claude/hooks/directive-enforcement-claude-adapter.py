#!/usr/bin/env python3
"""PreToolUse hook for directive enforcement (DIR-ROOT-BOUNDARY-001)."""

import sys
import json
from pathlib import Path

# Add GT-KB paths to sys.path so we can import groundtruth_kb
for _parent in Path(__file__).resolve().parents:
    if (_parent / "scripts" / "validate_directive_registry.py").is_file():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        _gt_src = _parent / "groundtruth-kb" / "src"
        if _gt_src.is_dir() and str(_gt_src) not in sys.path:
            sys.path.insert(0, str(_gt_src))
        break

try:
    from groundtruth_kb.enforcement import check_path_boundary, check_bash_command
except ImportError:

    def check_path_boundary(path_str: str, project_root: Path) -> tuple[bool, str]:
        return True, ""

    def check_bash_command(command: str, project_root: Path) -> tuple[bool, str]:
        return True, ""


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
    cwd = payload.get("cwd", ".")
    project_root = Path(cwd).resolve()

    # Find the nearest groundtruth.toml to resolve canonical root
    for candidate in (project_root, *project_root.parents):
        if (candidate / "groundtruth.toml").is_file():
            project_root = candidate
            break

    # 1. Handle command execution (bash, run_command, command, etc.)
    if tool_name.lower() in {"bash", "run_command"}:
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
