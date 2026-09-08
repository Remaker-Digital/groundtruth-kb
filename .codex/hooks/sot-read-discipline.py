#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project codex`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
"""SoT Read-Discipline canonical hook.

Authority: DCL-SOT-READ-HOOK-CONTRACT-001 v1; GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2
(clauses a-d of the Read-Discipline Extension); DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v2
(forbidden_substitutes column).

Two-surface harness-specific contract:

- Native-tool branch: tool_name in {Read, Grep, Glob}; extract target from tool_input;
  consult registry; block on match.
- Shell-command branch: tool_name == Bash; parse tool_input.command for known read/search
  verbs (Get-Content, Select-String, Get-ChildItem incl. -Recurse, aliases gc/gci/cat,
  rg, grep); extract path; consult registry; block on match.

Bypass: set GTKB_SOT_READ_DISCIPLINE_BYPASS=1 for owner-authorized single-command
exceptions per .codex/rules/sot-read-discipline.md.

Fail-closed: registry authority failures emit an explicit block. A missing,
mixed-generation, or unreadable registry cannot silently disable read discipline.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from groundtruth_kb.project.registry_control_plane import load_registry_snapshot  # noqa: E402

BYPASS_ENV_VAR = "GTKB_SOT_READ_DISCIPLINE_BYPASS"

NATIVE_READ_TOOLS = {"Read", "Grep", "Glob"}

# WI-7289: the shell surface is not one tool name. The projector renders
# shell_exec to "Bash|PowerShell" for Claude and "Shell|Bash" for Cursor, and
# Goose registers every PreToolUse hook without a matcher at all, so a payload
# can arrive under any of these names. Matching only "Bash" left the specified
# shell surface of DCL-SOT-READ-HOOK-CONTRACT-001 unenforced on the harnesses
# that do not use that name, even once the intent is declared.
SHELL_COMMAND_TOOLS = frozenset({"Bash", "PowerShell", "Shell", "shell", "bash", "powershell"})
# Retained for callers and tests that referenced the single-name constant.
SHELL_COMMAND_TOOL = "Bash"

# Per-verb extractor table for the shell-command branch.
# Returns the path argument(s) extracted from a token list, or [] if no match.

_PATH_FLAGS = {"-Path", "-LiteralPath", "--path"}


def _extract_path_after_flag(tokens: list[str], flags: set[str]) -> list[str]:
    out: list[str] = []
    for i, tok in enumerate(tokens):
        if tok in flags and i + 1 < len(tokens):
            out.append(tokens[i + 1])
    return out


def _first_positional(tokens: list[str], skip: int = 1) -> list[str]:
    """Return the first positional argument after `skip` tokens, skipping flags."""
    seen = 0
    i = skip
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            # skip flag + value if value follows
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                i += 2
            else:
                i += 1
            continue
        return [tok]
        seen += 1
    return []


def _last_positional(tokens: list[str], skip: int = 1) -> list[str]:
    """Return the last positional argument (rg/grep convention: PATTERN PATH)."""
    positionals = []
    i = skip
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            i += 1
            # heuristic: don't consume value for boolean flags
            continue
        positionals.append(tok)
        i += 1
    return [positionals[-1]] if len(positionals) >= 2 else []


def _extract_paths_from_bash(command: str) -> list[str]:
    """Parse a Bash/PowerShell command for known read/search verbs.

    Returns a list of extracted path arguments. Empty list when no recognized
    verb is present.
    """
    if not command:
        return []
    try:
        tokens = shlex.split(command, posix=False)
    except ValueError:
        return []
    if not tokens:
        return []
    verb = tokens[0].lstrip(".\\/")
    verb_lower = verb.lower()

    # First-positional verbs (path is first non-flag arg)
    if verb_lower in {"get-content", "gc", "cat"}:
        return _first_positional(tokens)
    # -Path-flag verbs
    if verb_lower in {"select-string", "sls"}:
        paths = _extract_path_after_flag(tokens, _PATH_FLAGS)
        return paths or _first_positional(tokens)
    if verb_lower in {"get-childitem", "gci"}:
        paths = _extract_path_after_flag(tokens, _PATH_FLAGS)
        return paths or _first_positional(tokens)
    # Last-positional verbs (rg/grep convention)
    if verb_lower in {"rg", "grep"}:
        return _last_positional(tokens)
    return []


def _normalize_relative(raw_path: str, root: Path) -> str | None:
    if not raw_path:
        return None
    cleaned = raw_path.strip().strip("'\"`").replace("\\", "/")
    try:
        absolute = Path(cleaned).resolve()
    except (OSError, ValueError):
        # Treat unresolvable paths as project-relative literal
        return cleaned.lstrip("./")
    try:
        rel = absolute.relative_to(root)
    except ValueError:
        # Outside project root: keep the literal for substring matching
        return cleaned.lstrip("./")
    return rel.as_posix()


def _load_registry_projection(root: Path) -> list[dict[str, Any]]:
    """Load one coherent registry generation as hook-friendly dictionaries."""
    snapshot = load_registry_snapshot(project_root=root)
    out: list[dict[str, Any]] = []
    for record in snapshot.records:
        if record.forbidden_substitutes:
            out.append(
                {
                    "id": record.id,
                    "storage_path": record.storage_path,
                    "forbidden_substitutes": list(record.forbidden_substitutes),
                }
            )
    return out


def _normalize_substitute(sub: str) -> str:
    """Normalize a forbidden_substitute string to compare against normalized targets.

    Uses the same convention as _normalize_relative: replace backslashes with
    forward slashes, strip surrounding whitespace, and remove a leading "./"
    prefix (but NOT a leading "." that begins a dotfile name like ".groundtruth").
    """
    cleaned = sub.strip().replace("\\", "/")
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def _check_against_registry(target: str, projection: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not target or not projection:
        return None
    for record in projection:
        for sub in record["forbidden_substitutes"]:
            sub_norm = _normalize_substitute(sub)
            # Match via prefix OR glob-style wildcard
            if sub_norm.endswith("/**"):
                if target == sub_norm[:-3] or target.startswith(sub_norm[:-2]):
                    return record
            elif sub_norm.endswith("/*"):
                target_parent = target.rsplit("/", 1)[0] + "/" if "/" in target else ""
                if target_parent == sub_norm[:-1]:
                    return record
            elif target == sub_norm or target.endswith("/" + sub_norm):
                return record
    return None


def _emit(decision: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(decision))


def _block_reason(target: str, record: dict[str, Any]) -> str:
    return (
        f"BLOCKED (DCL-SOT-READ-HOOK-CONTRACT-001): reading {target!r} as a "
        f"current-state substitute for canonical SoT {record['storage_path']!r} "
        f"(registry id {record['id']!r}) is forbidden. "
        f"Read the canonical path or use the registry's canonical reader. "
        f"To bypass for exceptional cases (audit/debug only), set "
        f"GTKB_SOT_READ_DISCIPLINE_BYPASS=1 for the single command and document "
        f"the rationale per .codex/rules/sot-read-discipline.md."
    )


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    # Bypass check
    if os.environ.get(BYPASS_ENV_VAR, "").strip() == "1":
        return {}
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return {}
    tool_name = payload.get("tool_name") or payload.get("tool") or ""

    targets: list[str] = []
    if tool_name in NATIVE_READ_TOOLS:
        if tool_name == "Read":
            raw = tool_input.get("file_path") or ""
            if isinstance(raw, str) and raw:
                targets.append(raw)
        elif tool_name == "Grep":
            raw = tool_input.get("path") or ""
            if isinstance(raw, str) and raw:
                targets.append(raw)
        elif tool_name == "Glob":
            raw = tool_input.get("pattern") or ""
            if isinstance(raw, str) and raw:
                # For glob, treat the base directory of the pattern as the target
                base = re.split(r"[*?\[]", raw, maxsplit=1)[0]
                if base:
                    targets.append(base)
    elif tool_name in SHELL_COMMAND_TOOLS:
        command = tool_input.get("command") or ""
        if isinstance(command, str) and command:
            targets.extend(_extract_paths_from_bash(command))
    else:
        return {}

    if not targets:
        return {}

    projection = _load_registry_projection(PROJECT_ROOT)
    if not projection:
        return {}

    for raw_target in targets:
        normalized = _normalize_relative(raw_target, PROJECT_ROOT)
        if normalized is None:
            continue
        record = _check_against_registry(normalized, projection)
        if record is not None:
            return {
                "decision": "block",
                "reason": _block_reason(normalized, record),
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
    except Exception as exc:  # noqa: BLE001 - every authority failure blocks
        decision = {
            "decision": "block",
            "reason": (f"BLOCKED (DCL-SOT-READ-HOOK-CONTRACT-001): coherent registry authority unavailable: {exc}"),
        }
    _emit(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
