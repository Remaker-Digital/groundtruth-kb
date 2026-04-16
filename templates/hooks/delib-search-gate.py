#!/usr/bin/env python3
"""
UserPromptSubmit hook: deliberation search gate.

Checks if a deliberation search has been performed recently for the active
document context. Emits an advisory if no recent search is recorded.

The .groundtruth/delib-search-log.jsonl file is written by delib-search-tracker.py
when a deliberation search completes.

Hook type: UserPromptSubmit

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

SEARCH_LOG_FILENAME = ".groundtruth/delib-search-log.jsonl"
MAX_AGE_SECONDS = 86400  # 24 hours


def _get_project_root(cwd: str) -> Path:
    return Path(cwd)


def _load_recent_searches(log_path: Path) -> list[dict]:
    """Load search log entries, ignoring corrupt lines."""
    entries = []
    if not log_path.exists():
        return entries
    try:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return entries


def _has_recent_search(entries: list[dict], doc_topic_hash: str, now_ts: float) -> bool:
    for entry in entries:
        try:
            if entry.get("doc_topic_hash") == doc_topic_hash:
                age = now_ts - float(entry.get("timestamp", 0))
                if age < MAX_AGE_SECONDS:
                    return True
        except (TypeError, ValueError):
            continue
    return False


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_additional_context, emit_pass
    except ImportError:

        def emit_additional_context(event: str, text: str) -> None:  # type: ignore[misc]
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        # Self-test: emit an advisory (no log file present in test env)
        emit_additional_context(
            "UserPromptSubmit",
            "[Governance] Deliberation search gate active. Run search_deliberations() before proposing or reviewing.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    cwd = payload.get("cwd", ".")
    prompt = payload.get("prompt") or payload.get("user_prompt", "")
    log_path = _get_project_root(cwd) / SEARCH_LOG_FILENAME

    # Derive a simple topic hash from the prompt's first 100 chars + cwd
    import hashlib

    raw = (cwd + ":" + prompt[:100]).encode("utf-8")
    doc_topic_hash = hashlib.sha256(raw).hexdigest()[:16]

    now_ts = datetime.now(tz=UTC).timestamp()
    entries = _load_recent_searches(log_path)

    if _has_recent_search(entries, doc_topic_hash, now_ts):
        emit_pass()
        sys.exit(0)

    emit_additional_context(
        "UserPromptSubmit",
        "[Governance] No deliberation search recorded for this context in the last 24 hours. "
        "Run search_deliberations() before proposing or reviewing to check prior decisions.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
