#!/usr/bin/env python3
"""Codex adapter for DIR-ROOT-BOUNDARY-001 directive enforcement.

Codex PreToolUse exposes command execution as ``Bash`` and file edits as
``apply_patch``. The canonical Claude adapter covers Bash-like commands and
direct tool path arguments; this adapter adds Codex patch parsing so both live
Codex mutation surfaces route through the same root-boundary policy.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GT_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GT_SRC) not in sys.path:
    sys.path.insert(0, str(GT_SRC))

try:
    from groundtruth_kb.enforcement import check_bash_command, check_path_boundary
except ImportError:  # pragma: no cover - hook fail-soft fallback for partial installs

    def check_bash_command(command: str, project_root: Path) -> tuple[bool, str]:
        return True, ""

    def check_path_boundary(path_str: str, project_root: Path) -> tuple[bool, str]:
        return True, ""


PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+?)\s*$", re.MULTILINE)


def _load_payload() -> dict[str, Any]:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _emit_pass() -> int:
    print("{}")
    return 0


def _record_gate_denial(pattern_id: str, subject: str, reason: str) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "codex-directive-enforcement",
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


def _emit_deny(pattern_id: str, subject: str, reason: str) -> int:
    _record_gate_denial(pattern_id, subject, reason)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "additionalContext": reason,
        }
    }
    print(json.dumps(out, sort_keys=True))
    return 0


def _tool_name(payload: dict[str, Any]) -> str:
    return str(payload.get("tool_name") or payload.get("tool") or "").lower()


def _tool_input(payload: dict[str, Any]) -> Any:
    return payload.get("tool_input") or payload.get("input") or {}


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_string_values(item))
        return values
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            values.extend(_string_values(item))
        return values
    return []


def _bash_command(payload: dict[str, Any]) -> str:
    data = _tool_input(payload)
    if isinstance(data, dict):
        for key in ("command", "script", "cmd", "CommandLine"):
            value = data.get(key)
            if isinstance(value, str):
                return value
    return ""


def _patch_text(payload: dict[str, Any]) -> str:
    data = _tool_input(payload)
    for candidate in _string_values(data) + _string_values(payload):
        if "*** Begin Patch" in candidate:
            return candidate
    return ""


def _patch_paths(payload: dict[str, Any]) -> list[str]:
    text = _patch_text(payload)
    if not text:
        return []
    return [match.group("path").strip() for match in PATCH_PATH_RE.finditer(text)]


def _direct_path_args(payload: dict[str, Any]) -> list[str]:
    data = _tool_input(payload)
    if not isinstance(data, dict):
        return []
    keys = {
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
    paths: list[str] = []
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value.strip())
        elif isinstance(value, list):
            paths.extend(str(item).strip() for item in value if isinstance(item, str) and item.strip())
    return paths


def main() -> int:
    if "--self-test" in sys.argv:
        return _emit_deny("self-test", "self-test", "[Enforcement] Self-test active.")

    payload = _load_payload()
    tool_name = _tool_name(payload)
    project_root = Path(str(payload.get("cwd") or PROJECT_ROOT)).resolve()
    for candidate in (project_root, *project_root.parents):
        if (candidate / "groundtruth.toml").is_file():
            project_root = candidate
            break

    if tool_name in {"bash", "shell_command", "shell", "run_command"}:
        command = _bash_command(payload)
        if command:
            allowed, reason = check_bash_command(command, project_root)
            if not allowed:
                return _emit_deny("root-boundary-command", command, f"Command blocked by directive: {reason}")
        return _emit_pass()

    candidate_paths = _patch_paths(payload) if tool_name == "apply_patch" else _direct_path_args(payload)
    for path_text in candidate_paths:
        allowed, reason = check_path_boundary(path_text, project_root)
        if not allowed:
            return _emit_deny("root-boundary-path", path_text, f"Tool execution blocked: {reason}")

    return _emit_pass()


if __name__ == "__main__":
    raise SystemExit(main())
