#!/usr/bin/env python3
"""
UserPromptSubmit hook: deliberation search gate.

Checks if a deliberation search has been performed recently for the active
bridge document context AND the current prompt topic. Emits an advisory if
no topically relevant recent search is recorded.

The .groundtruth/delib-search-log.jsonl file is written by delib-search-tracker.py
(a PostToolUse hook) when a deliberation search completes successfully.

Hook type: UserPromptSubmit

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

SEARCH_LOG_FILENAME = ".groundtruth/delib-search-log.jsonl"
MAX_AGE_SECONDS = 86400  # 24 hours

# Stopwords excluded from topic normalization — must match the tracker's set.
_STOPWORDS = frozenset(
    [
        "the",
        "and",
        "for",
        "this",
        "that",
        "with",
        "from",
        "are",
        "was",
        "has",
        "have",
        "been",
        "will",
        "can",
        "may",
        "could",
        "should",
        "would",
        "not",
        "but",
        "its",
        "all",
        "any",
        "each",
        "let",
        "run",
        "use",
        "now",
        "how",
        "who",
        "what",
        "where",
        "when",
        "why",
        "which",
        "our",
        "into",
        "also",
        "just",
        "got",
        "get",
        "set",
        "did",
        "does",
        "one",
        "two",
        "some",
        "more",
        "about",
        "them",
        "then",
        "than",
        "only",
        "been",
        "over",
        "such",
    ]
)


def _normalize_topics(text: str) -> list[str]:
    """Extract sorted, deduplicated topic words (3+ chars, no stopwords)."""
    words = re.findall(r"[a-z]{3,}", text.lower())
    return sorted({w for w in words if w not in _STOPWORDS})


# ---------------------------------------------------------------------------
# Shared context key derivation (duplicated from governance.context for
# template self-containment — both gate and tracker must produce identical
# keys from the same bridge/INDEX.md state).
# ---------------------------------------------------------------------------


def _read_active_bridge_docs(cwd: str) -> list[str]:
    """Extract active (non-terminal) bridge document names from INDEX.md."""
    index_path = Path(cwd) / "bridge" / "INDEX.md"
    if not index_path.exists():
        return []
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        return []

    active: list[str] = []
    current_doc: str | None = None
    latest_status: str | None = None

    for line in text.splitlines():
        line = line.strip()
        doc_match = re.match(r"^Document:\s*(.+)$", line, re.IGNORECASE)
        if doc_match:
            if current_doc and latest_status in ("NEW", "REVISED", "NO-GO"):
                active.append(current_doc)
            current_doc = doc_match.group(1).strip()
            latest_status = None
            continue
        status_match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):", line, re.IGNORECASE)
        if status_match and latest_status is None:
            latest_status = status_match.group(1).upper()

    if current_doc and latest_status in ("NEW", "REVISED", "NO-GO"):
        active.append(current_doc)
    return sorted(active)


def _compute_context_key(cwd: str) -> str:
    """Compute governance context key from active bridge documents."""
    active_docs = _read_active_bridge_docs(cwd)
    if active_docs:
        raw = (cwd + ":" + ",".join(active_docs)).encode("utf-8")
    else:
        raw = (cwd + ":_no_active_docs").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Log reader
# ---------------------------------------------------------------------------


def _load_recent_searches(log_path: Path) -> list[dict]:
    """Load search log entries, ignoring corrupt lines."""
    entries: list[dict] = []
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


def _has_recent_topical_search(
    entries: list[dict],
    doc_topic_hash: str,
    prompt_topics: list[str],
    now_ts: float,
) -> bool:
    """Check for a recent search matching both bridge context AND topic.

    A search matches if:
    1. Same doc_topic_hash (same active bridge documents)
    2. Within MAX_AGE_SECONDS
    3. search_success is True (or absent for backward compatibility)
    4. Topic overlap: at least one word in common between the search_topics
       and prompt_topics. If the prompt has no extractable topics (e.g.,
       very short prompt), any successful search under the same bridge
       context satisfies the gate.
    """
    prompt_set = set(prompt_topics)
    for entry in entries:
        try:
            if entry.get("doc_topic_hash") != doc_topic_hash:
                continue
            age = now_ts - float(entry.get("timestamp", 0))
            if age >= MAX_AGE_SECONDS:
                continue
            # Reject failed searches (new field; absent = backward-compat pass)
            if entry.get("search_success") is False:
                continue
            # Topic overlap check
            search_topics = set(entry.get("search_topics", []))
            if not prompt_set or not search_topics:
                # No topic discrimination possible — bridge context match suffices
                return True
            if prompt_set & search_topics:
                return True
        except (TypeError, ValueError):
            continue
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_additional_context, emit_pass
    except ImportError:

        def emit_additional_context(event: str, text: str) -> None:  # type: ignore[misc]
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
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
    prompt = payload.get("prompt", "")
    log_path = Path(cwd) / SEARCH_LOG_FILENAME
    doc_topic_hash = _compute_context_key(cwd)
    prompt_topics = _normalize_topics(prompt)

    now_ts = datetime.now(tz=UTC).timestamp()
    entries = _load_recent_searches(log_path)

    if _has_recent_topical_search(entries, doc_topic_hash, prompt_topics, now_ts):
        emit_pass()
        sys.exit(0)

    emit_additional_context(
        "UserPromptSubmit",
        "[Governance] No deliberation search recorded for this context/topic in the last 24 hours. "
        "Run search_deliberations() before proposing or reviewing to check prior decisions.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
