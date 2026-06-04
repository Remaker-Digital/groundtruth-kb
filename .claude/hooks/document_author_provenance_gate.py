#!/usr/bin/env python3
"""PreToolUse gate for new governed Markdown document author provenance."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

for _parent in Path(__file__).resolve().parents:
    if (_parent / "scripts" / "document_author_metadata.py").is_file():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from scripts.check_document_author_metadata import load_config  # noqa: E402
from scripts.document_author_metadata import (  # noqa: E402
    is_governed_document_path,
    relative_path,
    validate_author_metadata,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADD_FILE_RE = re.compile(r"^\*\*\* Add File: (?P<path>.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Candidate:
    rel_path: str
    content: str
    new_file: bool


def _emit_block(message: str) -> int:
    print(json.dumps({"decision": "block", "reason": message}, sort_keys=True))
    return 2


def _emit_pass() -> int:
    print("{}")
    return 0


def _tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name") or payload.get("tool") or payload.get("name") or ""
    return str(value)


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("input") or payload.get("parameters") or {}
    return value if isinstance(value, dict) else {}


def _extract_patch_text(payload: dict[str, Any]) -> str:
    tool_input = _tool_input(payload)
    candidates: list[Any] = [
        tool_input.get("patch"),
        tool_input.get("input"),
        tool_input.get("content"),
        payload.get("patch"),
    ]
    arguments = tool_input.get("arguments")
    if isinstance(arguments, dict):
        candidates.extend([arguments.get("patch"), arguments.get("input"), arguments.get("payload")])
    for candidate in candidates:
        if isinstance(candidate, str) and "*** Begin Patch" in candidate:
            return candidate
    return ""


def _content_from_add_hunk(patch_lines: list[str], start_index: int) -> str:
    content_lines: list[str] = []
    for line in patch_lines[start_index + 1 :]:
        if line.startswith("*** "):
            break
        if line.startswith("+"):
            content_lines.append(line[1:])
    return "\n".join(content_lines) + ("\n" if content_lines else "")


def _candidates_from_patch(payload: dict[str, Any], project_root: Path) -> list[Candidate]:
    patch = _extract_patch_text(payload)
    if not patch:
        return []
    lines = patch.splitlines()
    candidates: list[Candidate] = []
    for index, line in enumerate(lines):
        match = ADD_FILE_RE.match(line)
        if not match:
            continue
        rel = relative_path(project_root, match.group("path").strip())
        candidates.append(Candidate(rel, _content_from_add_hunk(lines, index), new_file=True))
    return candidates


def _candidate_from_write(payload: dict[str, Any], project_root: Path) -> Candidate | None:
    tool_name = _tool_name(payload)
    if tool_name != "Write":
        return None
    tool_input = _tool_input(payload)
    file_path = tool_input.get("file_path")
    content = tool_input.get("content")
    if not isinstance(file_path, str) or not isinstance(content, str):
        return None
    absolute = Path(file_path)
    if not absolute.is_absolute():
        absolute = project_root / absolute
    rel = relative_path(project_root, absolute)
    return Candidate(rel, content, new_file=not absolute.exists())


def _candidate_changes(payload: dict[str, Any], project_root: Path) -> list[Candidate]:
    direct = _candidate_from_write(payload, project_root)
    if direct is not None:
        return [direct]
    tool_name = _tool_name(payload)
    if tool_name in {"apply_patch", "functions.apply_patch"} or "*** Begin Patch" in json.dumps(payload):
        return _candidates_from_patch(payload, project_root)
    return []


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return _emit_pass()
    if not isinstance(payload, dict):
        return _emit_pass()
    project_root = Path(payload.get("cwd") or payload.get("project_root") or PROJECT_ROOT).resolve()
    config = load_config(project_root)
    for candidate in _candidate_changes(payload, project_root):
        if not candidate.new_file or not is_governed_document_path(candidate.rel_path, config):
            continue
        result = validate_author_metadata(candidate.content)
        if result.is_valid:
            continue
        return _emit_block(
            "new governed Markdown document is missing document-author provenance metadata: "
            f"{candidate.rel_path}; gaps: {', '.join(result.gaps)}. "
            "Required fields: author_identity, author_harness_id, author_session_context_id, "
            "author_model, author_model_version, author_model_configuration. "
            "Use document_author_provenance_waiver: DELIB-... <reason> only when a durable "
            "owner decision or governance artifact explicitly authorizes the exception."
        )
    return _emit_pass()


if __name__ == "__main__":
    raise SystemExit(main())
