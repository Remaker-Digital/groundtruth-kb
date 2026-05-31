#!/usr/bin/env python3
"""Advisory PreToolUse hook for bridge proposal work-item ID collisions."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

from scripts.bridge_proposal_wi_id_collision_check import check_content, format_markdown  # noqa: E402

BRIDGE_PROPOSAL_RE = re.compile(r"(?:^|/)bridge/[^/]+-\d{3}\.md$")
WRITE_TOOLS = {"Write", "Edit"}


def emit_additional_context(text: str) -> None:
    try:
        from groundtruth_kb.governance.output import emit_additional_context as _emit

        _emit("PreToolUse", text)
    except Exception:  # noqa: BLE001 - hook output must remain fail-open
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "additionalContext": text,
                    }
                }
            )
        )


def emit_pass() -> None:
    print("{}")


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def _is_bridge_proposal_file(file_path: str) -> bool:
    normalized = _normalize_path(file_path)
    if BRIDGE_PROPOSAL_RE.search(normalized):
        return True
    try:
        resolved = Path(file_path)
        if not resolved.is_absolute():
            resolved = PROJECT_ROOT / resolved
        rel = resolved.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        return False
    return bool(BRIDGE_PROPOSAL_RE.search(rel))


def _content_for_payload(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "Write":
        value = tool_input.get("content")
    elif tool_name == "Edit":
        value = tool_input.get("new_string")
    else:
        value = None
    return value if isinstance(value, str) else ""


def _load_payload() -> dict[str, Any]:
    try:
        value = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def main() -> int:
    payload = _load_payload()
    tool_name = str(payload.get("tool_name") or "")
    if tool_name not in WRITE_TOOLS:
        emit_pass()
        return 0

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        emit_pass()
        return 0
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not _is_bridge_proposal_file(file_path):
        emit_pass()
        return 0

    content = _content_for_payload(tool_name, tool_input)
    if not content:
        emit_pass()
        return 0

    try:
        result = check_content(content)
    except Exception as exc:  # noqa: BLE001 - never block bridge writes on infra errors
        emit_additional_context(f"[Governance] WI-ID collision gate skipped for {file_path}: {exc}")
        return 0

    if result.has_collisions:
        emit_additional_context(
            f"[Governance] Bridge proposal WI-ID collision warning for {file_path}:\n\n{format_markdown(result)}"
        )
        return 0

    emit_pass()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
