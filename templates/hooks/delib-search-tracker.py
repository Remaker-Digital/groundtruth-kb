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
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

SEARCH_LOG_FILENAME = ".groundtruth/delib-search-log.jsonl"
DELIBERATION_TOOL_PATTERNS = ["search_deliberations", "deliberations search", "deliberations list"]

# Stopwords excluded from topic normalization (common English words that
# don't carry topical signal).
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


def _is_deliberation_search(tool_name: str, tool_input: dict) -> bool:
    """Return True if this PostToolUse event is a deliberation search."""
    combined = (tool_name + " " + json.dumps(tool_input)).lower()
    return any(p in combined for p in DELIBERATION_TOOL_PATTERNS)


def _normalize_topics(text: str) -> list[str]:
    """Extract sorted, deduplicated topic words (3+ chars, no stopwords)."""
    words = re.findall(r"[a-z]{3,}", text.lower())
    return sorted({w for w in words if w not in _STOPWORDS})


def _extract_search_query(tool_input: dict) -> str:
    """Extract the human-readable search query from tool_input."""
    # Bash command: python -m groundtruth_kb deliberations search 'query here'
    command = ""
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command", ""))
    if not command:
        command = json.dumps(tool_input)
    # Try to extract the quoted query argument
    match = re.search(r"deliberations\s+(?:search|list)\s+['\"](.+?)['\"]", command)
    if match:
        return match.group(1)
    # Fallback: extract after 'search' or 'list' keyword
    match = re.search(r"deliberations\s+(?:search|list)\s+(.+?)(?:\s+--|$)", command)
    if match:
        return match.group(1).strip().strip("'\"")
    return command[:200]


def _extract_tool_response_metadata(payload: dict) -> dict | None:
    """Extract structured command metadata from a dict-shaped tool_response.

    Returns ``None`` if ``tool_response`` is absent or not a dict.  Otherwise
    returns ``{"success": bool | None, "exit_code": int | None,
    "stderr": str}``.
    """
    tr = payload.get("tool_response")
    if not isinstance(tr, dict):
        return None
    success = tr.get("success")
    exit_code = tr.get("exitCode")
    if isinstance(exit_code, str) and exit_code.isdigit():
        exit_code = int(exit_code)
    stderr = str(tr.get("stderr", "") or "")
    return {"success": success, "exit_code": exit_code, "stderr": stderr}


def _extract_result_evidence(tool_output: str, cmd_metadata: dict | None = None) -> dict:
    """Parse tool output for auditable result evidence.

    ``cmd_metadata``, when provided, carries structured command status from a
    dict-shaped ``tool_response`` (``success``, ``exit_code``, ``stderr``).
    If those fields indicate the command failed, the search is marked as
    failed regardless of stdout content.

    Success requires one of:
    - one or more parsed ``DELIB-####`` IDs,
    - a parsed positive result count,
    - an explicit zero-results / no-results marker **combined** with
      successful command metadata (no ``success=false``, no non-zero
      ``exitCode``, no failure text in ``stderr``).

    Ambiguous non-empty output that matches none of the above is treated as
    a failed/non-evidentiary search and will not satisfy the gate.
    """
    evidence: dict = {"search_success": False, "result_count": 0, "delib_ids": []}
    if not tool_output:
        return evidence

    # --- Check structured metadata for command-level failure first ---
    cmd_failed = False
    if cmd_metadata is not None:
        if cmd_metadata.get("success") is False:
            cmd_failed = True
        exit_code = cmd_metadata.get("exit_code")
        if isinstance(exit_code, int) and exit_code != 0:
            cmd_failed = True
        stderr = cmd_metadata.get("stderr", "")
        if stderr and re.search(
            r"(?:error|traceback|exception|failed|fatal|refused|unavailable)",
            stderr,
            re.IGNORECASE,
        ):
            cmd_failed = True

    if cmd_failed:
        # Structured metadata says the command failed — do not record
        evidence["search_success"] = False
        return evidence

    # Extract DELIB IDs (pattern: DELIB-NNNN)
    delib_ids = sorted(set(re.findall(r"DELIB-\d+", tool_output)))
    evidence["delib_ids"] = delib_ids
    # Try to extract result count from common output patterns
    count_match = re.search(r"(\d+)\s+(?:results?|deliberations?|entries|matches)", tool_output, re.IGNORECASE)
    if count_match:
        evidence["result_count"] = int(count_match.group(1))
    elif delib_ids:
        evidence["result_count"] = len(delib_ids)
    # Determine success: requires auditable evidence
    if evidence["result_count"] > 0 or delib_ids:
        evidence["search_success"] = True
    elif re.search(r"(?:0\s+results?|no\s+(?:results?|deliberations?|matches))", tool_output, re.IGNORECASE):
        # Explicit empty result is still a successful search
        evidence["search_success"] = True
        evidence["result_count"] = 0
    elif re.search(r"(?:error|traceback|exception|failed|not found)", tool_output, re.IGNORECASE):
        evidence["search_success"] = False
    else:
        # Ambiguous non-empty output without auditable evidence → not success
        evidence["search_success"] = False
    return evidence


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


def _extract_tool_output(payload: dict) -> str:
    """Extract tool output text from a PostToolUse payload.

    Claude Code's documented PostToolUse input uses ``tool_response`` for the
    tool's result.  The value may be a string or a dict whose shape depends on
    the tool (e.g. Bash returns ``{"stdout": ..., "stderr": ...}``).

    Legacy test payloads may use ``tool_output`` or ``output`` instead.  We
    check ``tool_response`` first, then fall back for backward compatibility.
    """
    # --- Primary: documented tool_response field ---
    tr = payload.get("tool_response")
    if tr is not None:
        if isinstance(tr, str):
            return tr
        if isinstance(tr, dict):
            # Adapt known dict shapes: prefer stdout, then output/text/content
            for key in ("stdout", "output", "text", "content"):
                val = tr.get(key)
                if val and isinstance(val, str):
                    return val
            # Last resort: serialise the whole dict so regex can still match
            return json.dumps(tr)
        return str(tr)

    # --- Fallback: legacy / test compatibility ---
    return str(payload.get("tool_output", "") or payload.get("output", "") or "")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


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
    # Primary: tool_response (documented PostToolUse field in Claude Code).
    # Fallback: tool_output / output (legacy/test compatibility).
    tool_output = _extract_tool_output(payload)
    cwd = payload.get("cwd", ".")

    if not _is_deliberation_search(tool_name, tool_input):
        emit_pass()
        sys.exit(0)

    # Extract structured command metadata (success/exitCode/stderr) if present
    cmd_metadata = _extract_tool_response_metadata(payload)

    # Extract auditable result evidence from tool output
    result_evidence = _extract_result_evidence(str(tool_output), cmd_metadata=cmd_metadata)

    # Do not record failed searches — they cannot satisfy the gate
    if not result_evidence["search_success"]:
        emit_pass()
        sys.exit(0)

    # Record the search using bridge-doc-based context key
    log_path = Path(cwd) / SEARCH_LOG_FILENAME
    log_path.parent.mkdir(parents=True, exist_ok=True)

    doc_topic_hash = _compute_context_key(cwd)
    search_query = _extract_search_query(tool_input)
    search_topics = _normalize_topics(search_query)

    entry = {
        "timestamp": datetime.now(tz=UTC).timestamp(),
        "doc_topic_hash": doc_topic_hash,
        "tool_name": tool_name,
        "cwd": cwd,
        "active_bridge_docs": _read_active_bridge_docs(cwd),
        "search_query": search_query[:200],
        "search_topics": search_topics,
        "result_count": result_evidence["result_count"],
        "delib_ids": result_evidence["delib_ids"],
        "search_success": result_evidence["search_success"],
        "source_event": "PostToolUse",
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
