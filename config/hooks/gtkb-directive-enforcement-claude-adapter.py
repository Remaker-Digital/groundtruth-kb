#!/usr/bin/env python3
"""PreToolUse hook for directive enforcement (DIR-ROOT-BOUNDARY-001)."""

import datetime as _dt
import hashlib
import json
import os
import sys
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
    from groundtruth_kb.enforcement import check_bash_command, check_path_boundary
except ImportError:

    def check_path_boundary(path_str: str, project_root: Path) -> tuple[bool, str]:
        return True, ""

    def check_bash_command(command: str, project_root: Path) -> tuple[bool, str]:
        return True, ""


def _project_root_from_env() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def _record_gate_denial(pattern_id: str, subject: str, reason: str) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    if not path.is_absolute():
        path = _project_root_from_env() / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "directive-enforcement-claude-adapter",
        "pattern_id": pattern_id,
        "command_hash": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
        "reason": reason,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def emit_deny(reason: str, *, pattern_id: str = "root-boundary", subject: str = "") -> None:
    _record_gate_denial(pattern_id, subject or reason, reason)
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
    if tool_name.lower() in {"bash", "powershell", "run_command"}:
        command = tool_input.get("command") or tool_input.get("CommandLine") or ""
        if command:
            allowed, reason = check_bash_command(command, project_root)
            if not allowed:
                emit_deny(
                    f"Command blocked by directive: {reason}",
                    pattern_id="root-boundary-command",
                    subject=command,
                )
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
            emit_deny(
                f"Tool execution blocked: {reason}",
                pattern_id="root-boundary-path",
                subject=path_str,
            )

    emit_pass()


if __name__ == "__main__":
    main()
