#!/usr/bin/env python3
"""Codex apply_patch adapter for the GT-KB bridge-compliance gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
SKIPPED_DIAGNOSTIC = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "last-bridge-audit-apply-patch-skipped.json"
BRIDGE_VERSIONED_FILE_RE = re.compile(r"^bridge/.+-\d{3}\.md$")
BRIDGE_LO_VERDICT_FILE_RE = re.compile(r"^bridge/.+\.lo-verdict\.md$", re.IGNORECASE)
_RETIRED_BRIDGE_AGGREGATE_FILE = ("bridge", "INDEX.md")


@dataclass(frozen=True)
class BridgeWrite:
    file_path: str
    content: str


def _load_payload() -> dict[str, Any]:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        return tool_input
    arguments = payload.get("arguments")
    if isinstance(arguments, dict):
        return arguments
    return {}


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_string_values(item))
        return values
    if isinstance(value, list | tuple):
        values: list[str] = []
        for item in value:
            values.extend(_string_values(item))
        return values
    return []


def extract_patch_text(payload: dict[str, Any]) -> str:
    """Extract raw apply_patch text from known Codex payload shapes."""
    tool_input = _tool_input(payload)
    priority_candidates: list[Any] = [
        tool_input.get("patch"),
        tool_input.get("input"),
        tool_input.get("content"),
        payload.get("patch"),
        payload.get("input"),
        payload.get("content"),
    ]
    arguments = tool_input.get("arguments")
    if isinstance(arguments, dict):
        priority_candidates.extend([arguments.get("patch"), arguments.get("input"), arguments.get("payload")])
    for candidate in priority_candidates:
        if isinstance(candidate, str) and "*** Begin Patch" in candidate:
            return candidate
    for candidate in _string_values(payload):
        if "*** Begin Patch" in candidate:
            return candidate
    return ""


def _write_skipped(reason: str, patch_text: str) -> None:
    # Telemetry-only: a diagnostic-write failure must not block apply_patch
    # pass-through. Bridge-target writes remain strict; only the skipped-audit
    # path is best-effort.
    try:
        SKIPPED_DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)
        SKIPPED_DIAGNOSTIC.write_text(
            json.dumps({"skipped": True, "reason": reason, "patch": patch_text}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(
            f"warning: could not write skipped-audit diagnostic at {SKIPPED_DIAGNOSTIC}: {exc}",
            file=sys.stderr,
        )


def _normalize_rel_path(path_text: str, root: Path) -> str | None:
    cleaned = path_text.strip().strip("\"'`").replace("\\", "/")
    if not cleaned:
        return None
    path = Path(cleaned)
    try:
        absolute = path if path.is_absolute() else root / path
        return absolute.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return cleaned.lstrip("./")


def _is_bridge_target(path_text: str) -> bool:
    normalized = path_text.replace("\\", "/").lstrip("./")
    parts = tuple(Path(normalized).parts)
    retired_aggregate = len(parts) >= 2 and parts[-2:] == _RETIRED_BRIDGE_AGGREGATE_FILE
    return (
        retired_aggregate
        or bool(BRIDGE_VERSIONED_FILE_RE.match(normalized))
        or bool(BRIDGE_LO_VERDICT_FILE_RE.match(normalized))
    )


def _is_patch_file_header(line: str) -> bool:
    return bool(re.match(r"^\*\*\* (?:Add|Update|Delete) File:\s+.+$", line)) or line == "*** End Patch"


def _find_subsequence(lines: list[str], needle: list[str], start: int) -> int:
    for index in range(start, len(lines) - len(needle) + 1):
        if lines[index : index + len(needle)] == needle:
            return index
    for index in range(0, len(lines) - len(needle) + 1):
        if lines[index : index + len(needle)] == needle:
            return index
    return -1


def _apply_patch_hunks(existing: str, hunk_lines: list[str]) -> str:
    lines = existing.splitlines()
    cursor = 0
    old_part: list[str] = []
    new_part: list[str] = []
    hunks: list[tuple[list[str], list[str]]] = []
    for line in hunk_lines:
        if line.startswith("@@"):
            if old_part or new_part:
                hunks.append((old_part, new_part))
            old_part = []
            new_part = []
            continue
        if line == "*** End of File" or not line:
            continue
        prefix = line[0]
        value = line[1:]
        if prefix == " ":
            old_part.append(value)
            new_part.append(value)
        elif prefix == "-":
            old_part.append(value)
        elif prefix == "+":
            new_part.append(value)
    if old_part or new_part:
        hunks.append((old_part, new_part))
    for old, new in hunks:
        if old:
            index = _find_subsequence(lines, old, cursor)
            if index < 0:
                raise ValueError("patch hunk context was not found")
            lines[index : index + len(old)] = new
            cursor = index + len(new)
        else:
            lines[cursor:cursor] = new
            cursor += len(new)
    return "\n".join(lines) + ("\n" if existing.endswith("\n") or hunk_lines else "")


def extract_bridge_writes(patch_text: str, *, root: Path = PROJECT_ROOT) -> list[BridgeWrite]:
    """Return post-patch bridge contents for versioned files and retired aggregate attempts."""
    if "*** Begin Patch" not in patch_text:
        return []
    lines = patch_text.splitlines()
    writes: list[BridgeWrite] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        add_match = re.match(r"^\*\*\* Add File:\s+(.+)$", line)
        update_match = re.match(r"^\*\*\* Update File:\s+(.+)$", line)
        delete_match = re.match(r"^\*\*\* Delete File:\s+(.+)$", line)
        if add_match:
            path = _normalize_rel_path(add_match.group(1), root)
            content_lines: list[str] = []
            idx += 1
            while idx < len(lines) and not _is_patch_file_header(lines[idx]):
                if lines[idx].startswith("+"):
                    content_lines.append(lines[idx][1:])
                idx += 1
            if path and _is_bridge_target(path):
                writes.append(BridgeWrite(path, "\n".join(content_lines) + ("\n" if content_lines else "")))
            continue
        if update_match:
            source_path = _normalize_rel_path(update_match.group(1), root)
            target_path = source_path
            hunk_lines: list[str] = []
            idx += 1
            while idx < len(lines) and not _is_patch_file_header(lines[idx]):
                move_match = re.match(r"^\*\*\* Move to:\s+(.+)$", lines[idx])
                if move_match:
                    target_path = _normalize_rel_path(move_match.group(1), root)
                else:
                    hunk_lines.append(lines[idx])
                idx += 1
            if target_path and _is_bridge_target(target_path):
                existing_path = root / source_path if source_path else root / target_path
                try:
                    content = _apply_patch_hunks(existing_path.read_text(encoding="utf-8"), hunk_lines)
                except (OSError, ValueError):
                    content = ""
                writes.append(BridgeWrite(target_path, content))
            continue
        if delete_match:
            path = _normalize_rel_path(delete_match.group(1), root)
            if path and _is_bridge_target(path):
                writes.append(BridgeWrite(path, ""))
        idx += 1
    return writes


def synthetic_claude_payload(payload: dict[str, Any], file_path: str, content: str) -> dict[str, Any]:
    """Build a synthetic Claude-shape Write payload for the canonical hook."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
        "session_id": payload.get("session_id", "codex-bridge-compliance-apply-patch"),
        "cwd": payload.get("cwd") or str(PROJECT_ROOT),
    }


def _permission_decision(output: str) -> str:
    try:
        parsed = json.loads(output.strip() or "{}")
    except json.JSONDecodeError:
        return ""
    if str(parsed.get("decision") or "").lower() in {"block", "deny", "ask"}:
        return str(parsed.get("decision")).lower()
    hook_output = parsed.get("hookSpecificOutput")
    if isinstance(hook_output, dict):
        return str(hook_output.get("permissionDecision") or "").lower()
    return ""


def _run_canonical(payload: dict[str, Any], write: BridgeWrite) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(synthetic_claude_payload(payload, write.file_path, write.content)),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if result.returncode != 0:
        return result.returncode, stdout, stderr
    if _permission_decision(stdout) in {"deny", "ask", "block"}:
        return 2, stdout, stderr
    return 0, stdout, stderr


def main() -> int:
    payload = _load_payload()
    patch_text = extract_patch_text(payload)
    if not patch_text:
        _write_skipped("no apply_patch envelope found", json.dumps(payload, sort_keys=True))
        print("{}")
        return 0
    writes = extract_bridge_writes(patch_text, root=Path(str(payload.get("cwd") or PROJECT_ROOT)).resolve())
    if not writes:
        print("{}")
        return 0
    for write in writes:
        code, stdout, stderr = _run_canonical(payload, write)
        if stderr:
            print(stderr, file=sys.stderr, end="")
        if code != 0:
            print(stdout or "{}", end="")
            return code
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
