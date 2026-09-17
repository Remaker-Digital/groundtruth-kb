#!/usr/bin/env python3
"""Guard declared substitute paths using the selected project's current registry.

This authored baseline is projected independently into each harness. The guard
handles normalized native read/search events and explicit simple shell read
arguments. An empty result neither proves currentness nor qualifies host hook
invocation. Current facts still require their canonical CLI/domain readers.
"""

from __future__ import annotations

import fnmatch
import json
import os
import shlex
import sys
from pathlib import Path, PurePosixPath
from typing import Any

HOOKS_DIR = "{{HARNESS_HOOKS_DIR}}"
if "{{" in HOOKS_DIR:
    HOOKS_DIR = ".harness-baseline-configuration/hooks"
# Derive the root from this exact authored/projected location, not cwd, a
# neighbouring harness, an environment fallback or a fixed directory depth.
PROJECT_ROOT = Path(__file__).absolute().parents[len(PurePosixPath(HOOKS_DIR).parts)]
BYPASS_ENV_VAR = "GTKB_SOT_READ_DISCIPLINE_BYPASS"
SHELL_COMMAND_TOOLS = frozenset({"Bash", "PowerShell", "Shell", "shell", "bash", "powershell"})
_PATH_FLAGS = frozenset({"-path", "-literalpath", "--path"})
_VALUE_FLAGS = frozenset(
    {
        "-encoding",
        "-filter",
        "-include",
        "-exclude",
        "-pattern",
        "-totalcount",
        "-tail",
        "-readcount",
        "-context",
        "--glob",
        "-g",
        "--iglob",
        "-t",
        "--type",
        "-T",
        "--type-not",
        "--max-count",
        "-m",
        "--max-depth",
        "--encoding",
        "-f",
        "--file",
    }
)


def _shell_read(command: str) -> tuple[list[str], bool]:
    """Extract explicit paths from one simple read command without executing it.

    This is not a shell interpreter: assignments, command substitution, pipelines,
    compound commands and unknown verbs do not establish evaluated coverage.
    """
    try:
        tokens = [value.strip("'\"") for value in shlex.split(command, posix=False)]
    except ValueError:
        return [], False
    if not tokens:
        return [], False
    verb = tokens[0].lower()
    if verb not in {"get-content", "gc", "cat", "select-string", "sls", "get-childitem", "gci", "rg", "grep"}:
        return [], False
    paths, positionals = [], []
    expression = False
    files = False
    index = 1
    literal = False
    while index < len(tokens):
        token = tokens[index]
        lower = token.lower()
        if not literal and token == "--":
            literal = True
        elif not literal and lower in _PATH_FLAGS:
            index += 1
            if index < len(tokens):
                paths.append(tokens[index])
        elif not literal and token in {"-e", "--regexp"}:
            expression = True
            index += 1
        elif not literal and lower == "--files":
            files = True
        elif not literal and (lower in _VALUE_FLAGS or token in _VALUE_FLAGS):
            if lower == "-pattern":
                expression = True
            index += 1
        elif not literal and token.startswith("-"):
            # Boolean flags do not consume the following positional path.
            pass
        else:
            positionals.append(token)
        index += 1
    search = (
        verb == "rg"
        or (
            verb == "grep"
            and any(value == "--recursive" or value.startswith("-r") or value.startswith("-R") for value in tokens[1:])
        )
        or (verb in {"get-childitem", "gci"} and any(value.lower() == "-recurse" for value in tokens[1:]))
    )
    if verb in {"rg", "grep", "select-string", "sls"}:
        if not expression and not files and positionals:
            positionals = positionals[1:]
        paths.extend(positionals)
    else:
        paths.extend(positionals)
    if verb in {"get-childitem", "gci"} and not search:
        paths.extend(value.rstrip("/") + "/*" for value in list(paths))
    return paths, search


def _normalize_relative(raw_path: str, root: Path, cwd: Path | None = None) -> str | None:
    if not raw_path:
        return None
    path = Path(raw_path.strip().strip("'\"`").replace("\\", "/"))
    if not path.is_absolute():
        path = (cwd or Path.cwd()) / path
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _load_registry_projection(root: Path) -> list[dict[str, Any]]:
    from groundtruth_kb.project.registry_control_plane import load_registry_snapshot

    rows = []
    for record in load_registry_snapshot(project_root=root).records:
        if record.lifecycle == "archive" or not record.forbidden_substitutes:
            continue
        patterns = []
        for value in record.forbidden_substitutes:
            value = value.replace("\\", "/")
            relative = PurePosixPath(value)
            if relative.is_absolute() or ".." in relative.parts or ":" in value or str(relative) == ".":
                raise ValueError(f"Invalid substitute locator in registry declaration {record.id}")
            patterns.append(relative.as_posix())
        rows.append({"id": record.id, "storage_path": record.storage_path, "forbidden_substitutes": patterns})
    return rows


def _matches(pattern: str, target: str) -> bool:
    """Match path segments; '*' never crosses '/', while '**' may do so."""
    pattern_parts = os.path.normcase(pattern).replace("\\", "/").split("/")
    target_parts = os.path.normcase(target).replace("\\", "/").split("/")

    def match(patterns, parts):
        if not patterns:
            return not parts
        if patterns[0] == "**":
            return any(match(patterns[1:], parts[index:]) for index in range(len(parts) + 1))
        return bool(parts) and fnmatch.fnmatchcase(parts[0], patterns[0]) and match(patterns[1:], parts[1:])

    return match(pattern_parts, target_parts)


def _check_against_registry(target: str, rows: list[dict[str, Any]], recursive=False) -> dict[str, Any] | None:
    for row in rows:
        for pattern in row["forbidden_substitutes"]:
            if _matches(pattern, target) or _matches(target, pattern):
                return row
            if recursive and (
                target == "." or os.path.normcase(pattern).startswith(os.path.normcase(target.rstrip("/") + "/"))
            ):
                return row
    return None


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    if os.environ.get(BYPASS_ENV_VAR, "").strip() == "1":
        return {}
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return {}
    tool = payload.get("tool_name") or payload.get("tool") or ""
    targets = []
    recursive = False
    if tool == "Read":
        targets = [tool_input.get("file_path") or tool_input.get("path")]
    elif tool == "Grep":
        targets = [tool_input.get("path") or "."]
        recursive = True
    elif tool == "Glob":
        base = tool_input.get("path") or "."
        pattern = tool_input.get("pattern") or "*"
        if isinstance(base, str) and isinstance(pattern, str):
            targets = [str(Path(base) / pattern)]
    elif tool in SHELL_COMMAND_TOOLS:
        command = tool_input.get("command")
        if isinstance(command, str):
            targets, recursive = _shell_read(command)
    else:
        return {}
    targets = [value for value in targets if isinstance(value, str) and value]
    if not targets:
        return {}
    installed = PROJECT_ROOT / HOOKS_DIR / "sot-read-discipline.py"
    if installed != Path(__file__).absolute() or installed.resolve() != installed:
        raise ValueError("Read hook installation is missing or redirected")
    cwd = payload.get("cwd") or str(Path.cwd())
    if not isinstance(cwd, str):
        raise ValueError("Read event cwd must be a path")
    cwd_path = Path(cwd).absolute()
    rows = _load_registry_projection(PROJECT_ROOT)
    for value in targets:
        target = _normalize_relative(value, PROJECT_ROOT, cwd_path)
        if target is None:
            continue
        row = _check_against_registry(target, rows, recursive)
        if row is not None:
            return {
                "decision": "block",
                "reason": (
                    f"BLOCKED (DCL-SOT-READ-HOOK-CONTRACT-001): {target!r} is a registered substitute for "
                    f"{row['storage_path']!r} (registry id {row['id']!r}). Use the current canonical CLI/domain reader. "
                    "For an owner-directed historical inspection or hook diagnosis, apply the existing "
                    "GTKB_SOT_READ_DISCIPLINE_BYPASS=1 exception to that command only."
                ),
            }
    return {}


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
    except json.JSONDecodeError:
        payload = {}
    try:
        decision = gate_decision(payload)
    except Exception as error:  # noqa: BLE001 - unavailable current input cannot permit a covered read
        decision = {
            "decision": "block",
            "reason": (
                f"BLOCKED (DCL-SOT-READ-HOOK-CONTRACT-001): coherent registry/read input unavailable "
                f"({type(error).__name__}). Inspect the selected project's registry through its CLI; "
                "no current read-discipline result is available."
            ),
        }
    sys.stdout.write(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
