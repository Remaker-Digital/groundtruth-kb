#!/usr/bin/env python3
"""
PreToolUse hook: bridge compliance gate.

Checks if a file being written matches a bridge proposal in NEW, REVISED, or
NO-GO status. Emits an ask checkpoint if the proposal hasn't been approved.

Uses latest-status-per-document parsing: only the first status line after
each Document: header is considered (newest-first per bridge protocol).

Hook type: PreToolUse (tools: Write, Edit)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BRIDGE_INDEX_FILENAME = "bridge/INDEX.md"
WRITE_TOOLS = {"Write", "Edit"}


def _parse_bridge_index(index_path: Path) -> dict[str, str]:
    """
    Returns {document_name: latest_status}.
    Only the first status line per document entry is considered (latest version).
    """
    result: dict[str, str] = {}
    current_doc: str | None = None
    current_doc_status_seen: bool = False

    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result

    for line in lines:
        line = line.strip()
        if line.startswith("Document:"):
            current_doc = line.removeprefix("Document:").strip()
            current_doc_status_seen = False
        elif current_doc and not current_doc_status_seen:
            for status in ("VERIFIED", "GO", "NO-GO", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    result[current_doc] = status
                    current_doc_status_seen = True
                    break

    return result


def _read_proposal_target_paths(index_path: Path, doc_name: str) -> list[str]:
    """Read target_paths from the latest proposal file's frontmatter."""
    # Find the latest proposal file path from the index
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    in_doc = False
    latest_file: str | None = None
    for line in lines:
        line = line.strip()
        if line.startswith("Document:") and line.removeprefix("Document:").strip() == doc_name:
            in_doc = True
            continue
        if in_doc and line.startswith("Document:"):
            break
        if in_doc and latest_file is None:
            for status in ("VERIFIED", "GO", "NO-GO", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    latest_file = line.split(":", 1)[1].strip()
                    break

    if not latest_file:
        return []

    proposal_path = index_path.parent.parent / latest_file
    try:
        content = proposal_path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Look for target_paths in frontmatter or proposal body
    # Simple heuristic: look for target_paths: [...] or target_paths lines
    paths: list[str] = []
    for fline in content.splitlines():
        m = re.match(r"^\s*target_paths?\s*[:=]\s*(.+)", fline, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Support JSON array or comma-separated
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    paths.extend(str(p) for p in parsed)
                else:
                    paths.append(str(parsed))
            except json.JSONDecodeError:
                for p in re.split(r"[,\s]+", raw):
                    p = p.strip("\"' ")
                    if p:
                        paths.append(p)
    return paths


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_ask, emit_pass
    except ImportError:

        def emit_ask(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
            print(json.dumps(out))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        emit_ask(
            "PreToolUse",
            "[Governance] Bridge compliance gate active. Ensure bridge proposal has GO status before implementing.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")

    if tool_name not in WRITE_TOOLS:
        emit_pass()
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        emit_pass()
        sys.exit(0)

    index_path = Path(cwd) / BRIDGE_INDEX_FILENAME
    if not index_path.exists():
        emit_pass()
        sys.exit(0)

    doc_statuses = _parse_bridge_index(index_path)
    file_path_normalized = file_path.replace("\\", "/")

    for doc_name, status in doc_statuses.items():
        if status in ("NEW", "REVISED", "NO-GO"):
            target_paths = _read_proposal_target_paths(index_path, doc_name)
            for tp in target_paths:
                tp_norm = tp.replace("\\", "/")
                if file_path_normalized.endswith(tp_norm) or tp_norm == file_path_normalized:
                    if status == "NO-GO":
                        emit_ask(
                            "PreToolUse",
                            f"[Governance] Bridge proposal for this module has NO-GO status. "
                            f"Review Codex findings at bridge/{doc_name} before implementing.",
                        )
                    else:
                        emit_ask(
                            "PreToolUse",
                            f"[Governance] Bridge proposal for {doc_name} is pending Codex review ({status}). "
                            f"Wait for GO verdict before implementing.",
                        )
                    sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
