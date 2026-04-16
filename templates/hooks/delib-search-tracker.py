#!/usr/bin/env python3
"""
PostToolUse hook: deliberation search tracker.

Records successful deliberation searches to .groundtruth/delib-search-log.jsonl
so that delib-search-gate.py knows a search was performed recently.

Hook type: PostToolUse

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

SEARCH_LOG_FILENAME = ".groundtruth/delib-search-log.jsonl"
DELIBERATION_TOOL_PATTERNS = ["search_deliberations", "deliberations search", "deliberations list"]


def _is_deliberation_search(tool_name: str, tool_input: dict) -> bool:
    """Return True if this PostToolUse event is a deliberation search."""
    combined = (tool_name + " " + json.dumps(tool_input)).lower()
    return any(p in combined for p in DELIBERATION_TOOL_PATTERNS)


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_pass
    except ImportError:

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        emit_pass()
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")

    if not _is_deliberation_search(tool_name, tool_input):
        emit_pass()
        sys.exit(0)

    # Record the search
    log_path = Path(cwd) / SEARCH_LOG_FILENAME
    log_path.parent.mkdir(parents=True, exist_ok=True)

    prompt_context = json.dumps(tool_input)[:100]
    raw = (cwd + ":" + prompt_context).encode("utf-8")
    doc_topic_hash = hashlib.sha256(raw).hexdigest()[:16]

    entry = {
        "timestamp": datetime.now(tz=UTC).timestamp(),
        "doc_topic_hash": doc_topic_hash,
        "tool_name": tool_name,
        "cwd": cwd,
    }
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
