#!/usr/bin/env python3
"""Translate native Antigravity tool/Stop events for selected GT-KB hooks.

Targets are shared platform scripts or this harness's own projected hooks.
The adapter verifies and translates; it never executes the proposed tool.
See https://antigravity.google/docs/hooks for the native stdin/stdout contract.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).absolute().parent.parent


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate field: {key}")
        result[key] = value
    return result


def _decode(raw: str) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=_object)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def _string(data: dict, key: str, *, empty=False) -> str:
    value = data.get(key)
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"Missing or invalid native field: {key}")
    return value


def _absolute(raw: Any) -> Path:
    if not isinstance(raw, str) or not raw.strip() or not Path(raw).is_absolute():
        raise ValueError("Native paths must be absolute")
    return Path(raw)


def _edit(data: dict) -> dict:
    multiple = data.get("AllowMultiple", False)
    if not isinstance(multiple, bool):
        raise ValueError("AllowMultiple must be boolean")
    return {
        "old_string": _string(data, "TargetContent", empty=True),
        "new_string": _string(data, "ReplacementContent", empty=True),
        "replace_all": multiple,
    }


def _native_payload(payload: dict, event: str) -> dict:
    native = _string(payload, "conversationId")
    workspaces = payload.get("workspacePaths")
    if not isinstance(workspaces, list) or not workspaces:
        raise ValueError("Native workspacePaths is required")
    roots = [_absolute(value) for value in workspaces]
    if PROJECT_ROOT not in roots:
        raise ValueError("This hook installation is not a mounted native workspace")
    adapted = {
        **payload,
        "project_root": str(PROJECT_ROOT),
        "cwd": str(PROJECT_ROOT),
        "session_id": native,
        "hook_event_name": event,
    }
    if event == "Stop":
        if not isinstance(payload.get("fullyIdle"), bool):
            raise ValueError("Native Stop requires fullyIdle")
        return adapted
    call = payload.get("toolCall")
    if not isinstance(call, dict) or not isinstance(call.get("args"), dict):
        raise ValueError("Native toolCall.name and toolCall.args are required")
    name, args = _string(call, "name"), call["args"]
    if name == "run_command":
        adapted["cwd"] = str(_absolute(args.get("Cwd")))
        tool, data = "Bash", {"command": _string(args, "CommandLine")}
    elif name in {"write_to_file", "replace_file_content", "multi_replace_file_content"}:
        data = {"file_path": str(_absolute(args.get("TargetFile")))}
        if name == "write_to_file":
            tool = "Write"
            data["content"] = _string(args, "CodeContent", empty=True)
        elif name == "replace_file_content":
            tool = "Edit"
            data.update(_edit(args))
        else:
            tool = "MultiEdit"
            chunks = args.get("ReplacementChunks")
            if not isinstance(chunks, list) or not chunks or not all(isinstance(c, dict) for c in chunks):
                raise ValueError("ReplacementChunks must contain native edits")
            data["edits"] = [_edit(chunk) for chunk in chunks]
    elif name == "view_file":
        tool, data = "Read", {"file_path": str(_absolute(args.get("AbsolutePath")))}
    elif name == "list_dir":
        tool, data = "Glob", {"path": str(_absolute(args.get("DirectoryPath")))}
    elif name == "find_by_name":
        tool, data = (
            "Glob",
            {
                "path": str(_absolute(args.get("SearchDirectory"))),
                "pattern": _string(args, "Pattern"),
            },
        )
    elif name == "grep_search":
        tool, data = (
            "Grep",
            {
                "path": str(_absolute(args.get("SearchPath"))),
                "pattern": _string(args, "Query"),
            },
        )
    else:
        raise ValueError(f"Unclassified native tool effect: {name}; use an explicit supported tool or CLI operation")
    adapted.update(tool_name=tool, tool_input=data)
    return adapted


def _target(raw: str) -> Path:
    path = Path(raw)
    if ".." in path.parts:
        raise ValueError("Redirected hook target")
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    rel = path.relative_to(PROJECT_ROOT)
    if not (rel.is_relative_to("scripts") or rel.is_relative_to(".agent/hooks")):
        raise ValueError("Hook target must be platform code or this harness's own projected hook")
    if not path.is_file() or path.resolve() != path:
        raise ValueError("Hook target is missing or redirected")
    return path


def _block_reason(response: dict) -> str | None:
    decision = response.get("decision")
    if decision not in {None, "allow", "block"}:
        raise ValueError("Unrecognized hook decision")
    native = response.get("hookSpecificOutput", {})
    if not isinstance(native, dict):
        raise ValueError("Invalid hookSpecificOutput")
    permission = native.get("permissionDecision")
    if permission not in {None, "allow", "deny", "ask"}:
        raise ValueError("Unrecognized hook permission decision")
    continuing = response.get("continue", True)
    if not isinstance(continuing, bool):
        raise ValueError("Invalid hook continuation result")
    if decision == "block" or permission in {"deny", "ask"} or not continuing:
        return str(
            response.get("reason")
            or native.get("permissionDecisionReason")
            or response.get("stopReason")
            or "The selected GT-KB hook refused"
        )
    return None


def _emit(event: str, reason: str | None) -> int:
    if event == "PostToolUse":
        print("{}")
        if reason:
            print(reason, file=sys.stderr)
        return 1 if reason else 0
    output = {"decision": ("continue" if event == "Stop" else "deny") if reason else "allow"}
    if reason:
        output["reason"] = reason
    # Antigravity gates on JSON decision. No undocumented exit-code mapping.
    print(json.dumps(output, ensure_ascii=False), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=("PreToolUse", "PostToolUse", "Stop"), required=True)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("script")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    event = "PreToolUse"
    try:
        options = parser.parse_args()
        event = options.event
        if not math.isfinite(options.timeout) or options.timeout <= 0:
            raise ValueError("Hook timeout must be finite and positive")
        target = _target(options.script)
        payload = _native_payload(_decode(sys.stdin.read()), event)
        env = dict(os.environ)
        env.update(
            GTKB_HARNESS_NAME="antigravity",
            GTKB_PROJECT_ROOT=str(PROJECT_ROOT),
            GT_PROJECT_ROOT=str(PROJECT_ROOT),
            GTKB_NATIVE_CONTEXT_ID=payload["session_id"],
            ANTIGRAVITY_PROJECT_DIR=str(PROJECT_ROOT),
            ANTIGRAVITY_SESSION_ID=payload["session_id"],
            PYTHONIOENCODING="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, "-B", str(target), *options.args],
            input=json.dumps(payload),
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=options.timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.stderr:
            sys.stderr.write(completed.stderr[:2000])
        if completed.returncode:
            raise ValueError(f"Selected hook failed with exit {completed.returncode}")
        response = _decode(completed.stdout) if completed.stdout.strip() else {}
        return _emit(event, _block_reason(response))
    except (OSError, ValueError, TypeError, UnicodeError, subprocess.TimeoutExpired) as error:
        return _emit(event, f"Antigravity hook refused: {str(error)[:2000]}")
    except SystemExit as error:
        if error.code == 0:
            return 0
        return _emit(event, "Antigravity hook configuration is invalid")


if __name__ == "__main__":
    raise SystemExit(main())
