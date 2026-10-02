"""Root and registration identity for authored hooks running in place.

Runtime roots come from the event, the native adapter, or a project marker.
An unmarked current working directory never becomes the installation root.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def resolve_root(payload: Mapping[str, Any] | None = None) -> Path:
    payload = payload or {}
    for value in (payload.get("project_root"), os.environ.get("GTKB_PROJECT_ROOT")):
        if isinstance(value, str) and value.strip():
            path = Path(value).expanduser()
            if path.is_absolute():
                return path.resolve()
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip() and Path(cwd).is_absolute():
        start = Path(cwd).resolve()
        for candidate in (start, *start.parents):
            if (candidate / "groundtruth.toml").is_file():
                return candidate
    return Path(__file__).absolute().parents[2]


def harness_name(argv: Sequence[str]) -> str | None:
    for index, value in enumerate(argv):
        if value == "--harness" and index + 1 < len(argv):
            candidate = argv[index + 1]
            return candidate if candidate and not candidate.startswith("-") else None
    return None


# c123 (batch design WP2, G38): every route now sends Claude's PreToolUse shape (file_path, content, old_string and
# new_string, edits, patch, command), but adapters and payloads have used other keys. These readers accept each key a
# route has used, so a content check never reads an empty value for a call that carries one.
_PATH_KEYS = ("file_path", "path", "notebook_path", "target_file", "TargetFile", "AbsolutePath")
_WRITE_KEYS = ("content", "contents", "file_text", "CodeContent")
_NEW_TEXT_KEYS = ("new_string", "new_text", "new_str", "after", "ReplacementContent", "new_source")


def tool_input_of(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """The payload's tool input, under any of the names a route has used."""
    value = payload.get("tool_input") or payload.get("input") or payload.get("parameters") or {}
    return value if isinstance(value, Mapping) else {}


def _first_text(tool_input: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def tool_path(tool_input: Mapping[str, Any]) -> str:
    """The file a tool call names (file_path, else a route's name for it); empty when it names none."""
    return _first_text(tool_input, _PATH_KEYS)


def write_content(tool_input: Mapping[str, Any]) -> str:
    """The text a Write writes (content, else a route's name for it)."""
    return _first_text(tool_input, _WRITE_KEYS)


def edit_new_text(tool_input: Mapping[str, Any]) -> str:
    """The text an edit writes: new_string (or a route's name for it), and each MultiEdit edit's, joined."""
    single = _first_text(tool_input, _NEW_TEXT_KEYS)
    edits = tool_input.get("edits")
    if not isinstance(edits, list):
        return single
    parts = [_first_text(edit, _NEW_TEXT_KEYS) for edit in edits if isinstance(edit, Mapping)]
    return "\n".join(part for part in (single, *parts) if part)


def patch_text(payload: Mapping[str, Any]) -> str:
    """An apply_patch call's patch text from any key a route has used (Codex puts it in the command)."""
    tool_input = tool_input_of(payload)
    candidates: list[Any] = [
        tool_input.get("patch"),
        tool_input.get("input"),
        tool_input.get("content"),
        tool_input.get("command"),
        payload.get("patch"),
    ]
    arguments = tool_input.get("arguments")
    if isinstance(arguments, Mapping):
        candidates.extend([arguments.get("patch"), arguments.get("input"), arguments.get("payload")])
    for candidate in candidates:
        if isinstance(candidate, str) and "*** Begin Patch" in candidate:
            return candidate
    return ""
