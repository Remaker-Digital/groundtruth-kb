#!/usr/bin/env python3
"""Hard gate protected implementation mutations unless a bridge GO packet exists."""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.implementation_authorization import AuthorizationError, normalize_relative_path, validate_targets
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import AuthorizationError, normalize_relative_path, validate_targets


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_EXACT = {
    ".claude/settings.json",
    ".codex/hooks.json",
    "pyproject.toml",
    "groundtruth.toml",
}
PROTECTED_PREFIXES = (
    "scripts/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "tests/",
    ".claude/hooks/",
    ".claude/rules/",
    ".codex/gtkb-hooks/",
    "config/",
    ".github/",
)
ALLOWED_WRITE_PREFIXES = (
    "bridge/",
    "independent-progress-assessments/",
)
SAFE_COMMAND_PREFIXES = (
    "rg ",
    "git status",
    "git diff",
    "git show",
    "git log",
    "get-content",
    "select-string",
    "get-childitem",
    "python -m pytest",
    "python -m groundtruth_kb deliberations search",
    "python -m ruff check",
    "python -m ruff format --check",
    "python scripts/bridge_applicability_preflight.py",
    "python scripts/adr_dcl_clause_preflight.py",
)
GIT_FINALIZATION_SUBCOMMANDS = {"commit", "push"}
GIT_FINALIZATION_CONTROL_MARKERS = (";", "&&", "||", "|", "$(", "`")
GIT_FINALIZATION_DENIED_FLAGS = {"-f", "--force", "--force-with-lease"}
MUTATING_COMMAND_RE = re.compile(
    r"\b("
    r"set-content|out-file|new-item|remove-item|move-item|copy-item|"
    r"apply_patch|git\s+(?:commit|reset|checkout|merge|rebase|tag|push)|"
    r"python\s+.*(?:write_text|open\(.+,\s*['\"]w|sqlite3|insert_|update_|delete_)"
    r")\b|(^|[^>])>{1,2}($|[^&])",
    re.IGNORECASE,
)
PATH_TOKEN_RE = re.compile(
    r"(?P<path>(?:\.?/?(?:scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|config|\.claude/hooks|\.codex/gtkb-hooks|\.github|bridge|independent-progress-assessments)/[^\s'\";]+|\.claude/settings\.json|\.codex/hooks\.json|pyproject\.toml|groundtruth\.toml))"
)
PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)
POWERSHELL_ENV_ASSIGNMENT_RE = re.compile(
    r"""^(?:\$env:[a-z_][\w_]*\s*=\s*(?:'[^']*'|"[^""]*"|[^\s;]+)\s*;\s*)+""",
    re.IGNORECASE,
)


def _project_root(payload: dict[str, Any]) -> Path:
    root = payload.get("project_root") or payload.get("cwd")
    if isinstance(root, str) and root.strip():
        return Path(root).resolve()
    return PROJECT_ROOT


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "tool", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _tool_input(payload: dict[str, Any]) -> Any:
    for key in ("tool_input", "input", "parameters"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return value
    return payload


def _normalize(root: Path, path_text: str) -> str | None:
    cleaned = path_text.strip().strip("'\"`").replace("\\", "/")
    if not cleaned:
        return None
    try:
        return normalize_relative_path(root, cleaned)
    except AuthorizationError:
        return cleaned


def is_protected_path(relative_path: str) -> bool:
    rel = relative_path.replace("\\", "/").lstrip("./")
    if rel in PROTECTED_EXACT:
        return True
    if rel.startswith(ALLOWED_WRITE_PREFIXES):
        return False
    return any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def _paths_from_apply_patch(root: Path, text: str) -> list[str]:
    normalized = (text or "").replace("`r`n", "\n").replace("`n", "\n").replace("\\r\\n", "\n").replace("\\n", "\n")
    paths = PATCH_PATH_RE.findall(normalized)
    paths.extend(PATCH_MOVE_RE.findall(normalized))
    return [rel for raw in paths if (rel := _normalize(root, raw))]


def _paths_from_shell(root: Path, command: str) -> list[str]:
    paths = [rel for raw in PATH_TOKEN_RE.findall(command or "") if (rel := _normalize(root, raw))]
    try:
        tokens = shlex.split(command, posix=False)
    except ValueError:
        tokens = []
    for token in tokens:
        if any(marker in token for marker in ("/", "\\")) or token in PROTECTED_EXACT:
            rel = _normalize(root, token)
            if rel and (is_protected_path(rel) or rel.startswith(ALLOWED_WRITE_PREFIXES)):
                paths.append(rel)
    return sorted(set(paths))


def _is_safe_command(command: str) -> bool:
    normalized = " ".join(command.strip().split()).lower()
    if _is_simple_git_finalization_command(command):
        return True
    if any(normalized.startswith(prefix) for prefix in SAFE_COMMAND_PREFIXES):
        return True
    without_env_prefix = POWERSHELL_ENV_ASSIGNMENT_RE.sub("", normalized)
    return without_env_prefix != normalized and any(
        without_env_prefix.startswith(prefix) for prefix in SAFE_COMMAND_PREFIXES
    )


def _is_simple_git_finalization_command(command: str) -> bool:
    if any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS):
        return False
    try:
        tokens = [_clean_shell_token(token).lower() for token in shlex.split(command, posix=False)]
    except ValueError:
        return False
    tokens = [token for token in tokens if token]
    if len(tokens) < 2 or tokens[0] != "git" or tokens[1] not in GIT_FINALIZATION_SUBCOMMANDS:
        return False
    return not (tokens[1] == "push" and any(token in GIT_FINALIZATION_DENIED_FLAGS for token in tokens[2:]))


def _clean_shell_token(token: str) -> str:
    return token.strip().strip("'\"")


def _is_mutating_command(command: str) -> bool:
    return bool(MUTATING_COMMAND_RE.search(command or ""))


def _is_apply_patch_tool(tool: str) -> bool:
    return tool == "apply_patch" or tool.endswith(".apply_patch")


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_string_values(item))
        return strings
    if isinstance(value, list | tuple):
        strings: list[str] = []
        for item in value:
            strings.extend(_string_values(item))
        return strings
    return []


def _apply_patch_text(payload: dict[str, Any], data: Any) -> str:
    candidates: list[str] = []
    candidates.extend(_string_values(data))
    for key in ("patch", "input", "content", "tool_input"):
        candidates.extend(_string_values(payload.get(key)))
    candidates.extend(_string_values(payload))
    for candidate in candidates:
        if "*** Begin Patch" in candidate and candidate.strip():
            return candidate
    for candidate in candidates:
        if candidate.strip():
            return candidate
    return ""


def changed_paths(payload: dict[str, Any]) -> tuple[list[str], bool]:
    root = _project_root(payload)
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)

    if tool in {"write", "edit", "multiedit"}:
        path = data.get("file_path") or data.get("path")
        rel = _normalize(root, str(path)) if path else None
        return ([rel] if rel else []), True

    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        text = _apply_patch_text(payload, data)
        return _paths_from_apply_patch(root, text), True

    if tool in {"bash", "shell_command", "shell"} or (isinstance(data, dict) and "command" in data):
        command = str((data.get("command") if isinstance(data, dict) else None) or payload.get("command") or "")
        if _is_safe_command(command):
            return [], False
        paths = _paths_from_shell(root, command)
        return paths, _is_mutating_command(command)

    return [], False


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    root = _project_root(payload)
    paths, mutating = changed_paths(payload)
    if not mutating:
        return {}
    if not paths:
        protected = ["<unknown-mutating-target>"]
    else:
        protected = [path for path in paths if is_protected_path(path)]
    if not protected:
        return {}
    try:
        validate_targets(root, protected)
    except AuthorizationError as exc:
        return {
            "decision": "block",
            "reason": (
                "BLOCKED (GTKB-IMPLEMENTATION-START-GATE): protected implementation mutation requires "
                f"a live bridge GO authorization packet. {exc}"
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
    result = gate_decision(payload)
    if result.get("decision") == "block":
        reason = result.get("reason") or "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)"
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                        "additionalContext": reason,
                    }
                },
                sort_keys=True,
            )
        )
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
