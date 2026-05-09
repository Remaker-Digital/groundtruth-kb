#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook — Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION).

Implements ``DCL-CONCEPT-ON-CONTACT-001`` Stage A: detects glossary-term
overlap with the owner prompt and emits matched glossary entries as a
``{"systemMessage": ...}`` injection. For prompt tokens that do NOT match
the glossary but appear concept-shaped, a low-distance DA semantic search
produces candidate prior-deliberation entries flagged
``[candidate for promotion]``.

The hook is non-mutating, fail-closed, and never blocks the prompt.
Semantic-search fan-out is mechanically bounded.

Bridge: bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md (REVISED-2; GO at -006).
Specs: GOV-GLOSSARY-AS-DA-READ-SURFACE-001, ADR-DA-READ-SURFACE-PLACEMENT-001, DCL-CONCEPT-ON-CONTACT-001.

Stdin:  JSON {"prompt": "...", "session_id": "...", ...}
Stdout: JSON {"systemMessage": "..."} when matches; {} when none/skip.
Exit:   Always 0 (Claude Code hook contract; never blocks).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration (engineering choices settled within bridge scope per
# bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md)
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
GLOSSARY_PATH = PROJECT_DIR / ".claude" / "rules" / "canonical-terminology.md"
AUDIT_LOG_DIR = PROJECT_DIR / ".gtkb-state" / "glossary-expansion" / "invocations"

MAX_GLOSSARY_MATCHES = 5
MAX_SEMANTIC_CANDIDATES = 3
SEMANTIC_MAX_DISTANCE = 1.5  # L2 distance ceiling; lower-is-better; matches groundtruth-kb/src/groundtruth_kb/db.py:49
TOKEN_BUDGET_BYTES = int(os.environ.get("GTKB_GLOSSARY_EXPANSION_CAP_BYTES") or "2048")
DA_SEMANTIC_LIMIT = 2  # per-phrase limit; max 6 results across all phrases

# Skip-rule prefixes for automated dispatch / session-lifecycle prompts.
# Configurable via env var (newline-separated).
_DEFAULT_SKIP_PREFIXES = [
    "Generate 0 to ",
    "Bridge auto-dispatch",
    "File bridge scan:",
    "Smart-poller notification",
    "Codex skill adapters:",
]


def _skip_prefixes() -> list[str]:
    env = os.environ.get("GTKB_GLOSSARY_EXPANSION_SKIP_PREFIXES")
    if env:
        return [line for line in env.splitlines() if line.strip()]
    return _DEFAULT_SKIP_PREFIXES


# Tokenization stop-words.
_STOP_WORDS = frozenset(
    [
        "the",
        "is",
        "at",
        "of",
        "and",
        "or",
        "to",
        "for",
        "with",
        "as",
        "that",
        "this",
        "it",
        "a",
        "an",
        "in",
        "on",
        "by",
        "be",
        "can",
        "do",
        "does",
        "was",
        "were",
        "has",
        "have",
        "had",
        "been",
        "being",
        "but",
        "if",
        "then",
        "else",
        "not",
        "no",
        "yes",
        "you",
        "we",
        "they",
        "he",
        "she",
        "them",
        "us",
        "our",
        "your",
        "their",
        "are",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
    ]
)

# Word regex: lowercase tokens (used for n-gram generation).
_WORD_RE = re.compile(r"[a-z][a-z0-9-]+")

# Glossary heading regex.
_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")


# ---------------------------------------------------------------------------
# Glossary index (mtime-cached at module level)
# ---------------------------------------------------------------------------

_GLOSSARY_INDEX_CACHE: dict[str, Any] = {"mtime": None, "index": {}, "entries": {}}


def _build_glossary_index() -> tuple[dict[str, str], dict[str, str]]:
    """Return ``(term_lower → heading_text, heading_text → entry_lines)``.

    The glossary is parsed at every invocation but mtime-cached so identical
    file content is parsed once per process.
    """
    try:
        mtime = GLOSSARY_PATH.stat().st_mtime
    except OSError:
        return {}, {}

    if _GLOSSARY_INDEX_CACHE["mtime"] == mtime and _GLOSSARY_INDEX_CACHE["index"]:
        return _GLOSSARY_INDEX_CACHE["index"], _GLOSSARY_INDEX_CACHE["entries"]

    try:
        content = GLOSSARY_PATH.read_text(encoding="utf-8")
    except OSError:
        return {}, {}

    lines = content.splitlines()
    index: dict[str, str] = {}  # lowercase term → heading
    entries: dict[str, str] = {}  # heading → entry text (heading line through next heading or section)

    current_heading: str | None = None
    current_lines: list[str] = []

    def _flush_entry() -> None:
        if current_heading is not None:
            entries[current_heading] = "\n".join(current_lines)

    in_canonical_section = False

    for line in lines:
        stripped = line.strip()
        # Top-level section gate: only index entries within ## Canonical Terms,
        # ## GT-KB Platform & Lifecycle Terms, ## GT-KB DA Read-Surface and
        # Operational Vocabulary, or any other top-level section that contains
        # ### entries we recognize. Conservative: include any ## section.
        if stripped.startswith("## ") and not stripped.startswith("### "):
            _flush_entry()
            current_heading = None
            current_lines = []
            in_canonical_section = True
            continue
        m = _HEADING_RE.match(line)
        if m and in_canonical_section:
            _flush_entry()
            current_heading = m.group(1).strip()
            current_lines = [line]
            # Index by lowercase heading text.
            index[current_heading.lower()] = current_heading
            continue
        # Look for "**Canonical alias:** ..." or "**Allowed synonyms:** ..." within current entry.
        if current_heading is not None:
            current_lines.append(line)
            if stripped.startswith("**Canonical alias:**") or stripped.startswith("**Allowed synonyms:**"):
                # Extract comma- or semicolon-separated tokens.
                value = stripped.split("**", 2)[-1].strip()
                # Strip trailing punctuation.
                value = value.rstrip(".")
                # Split on common separators.
                for tok in re.split(r"[;,]|\s+or\s+", value):
                    tok = tok.strip(" .;:`*")
                    if tok and len(tok) >= 2:
                        index.setdefault(tok.lower(), current_heading)

    _flush_entry()

    _GLOSSARY_INDEX_CACHE["mtime"] = mtime
    _GLOSSARY_INDEX_CACHE["index"] = index
    _GLOSSARY_INDEX_CACHE["entries"] = entries
    return index, entries


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------


def _tokenize_prompt(prompt: str) -> list[str]:
    """Extract 1- to 3-word candidate phrases (lowercase, deduped, all n-grams).

    Uses overlapping n-gram extraction so single-word terms like ``isolation``
    are still surfaced when they appear inside a longer phrase like
    ``discuss isolation in``.
    """
    text = prompt.lower()
    words = _WORD_RE.findall(text)
    seen: set[str] = set()
    out: list[str] = []
    for n in (3, 2, 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            if phrase in seen:
                continue
            phrase_words = phrase.split()
            if all(w in _STOP_WORDS for w in phrase_words):
                continue
            if len(phrase_words) == 1 and phrase_words[0] in _STOP_WORDS:
                continue
            seen.add(phrase)
            out.append(phrase)
    # F2 fix per `-001-008`: deterministic priority is "longer phrases
    # first, alphabetical tiebreaker" per the GO'd proposal. Sorting here
    # rather than relying on the (3,2,1) loop ensures equal-length phrases
    # are alphabetically ordered, which matters when MAX_SEMANTIC_CANDIDATES
    # caps the forwarded set under long prompts.
    out.sort(key=lambda p: (-len(p.split()), p))
    return out


# ---------------------------------------------------------------------------
# Semantic search (auto-DB-open per Phase 2 pattern)
# ---------------------------------------------------------------------------


def _try_open_default_db() -> Any | None:
    """Open the default ``KnowledgeDB`` for semantic search.

    Returns ``None`` on any failure (graceful degradation).
    Set env ``GTKB_GLOSSARY_EXPANSION_DB=false`` to explicitly disable.
    """
    if (os.environ.get("GTKB_GLOSSARY_EXPANSION_DB") or "").lower() == "false":
        return None
    try:
        # Add groundtruth-kb/src to sys.path if needed.
        gtkb_src = PROJECT_DIR / "groundtruth-kb" / "src"
        if gtkb_src.is_dir() and str(gtkb_src) not in sys.path:
            sys.path.insert(0, str(gtkb_src))
        from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

        return KnowledgeDB(str(PROJECT_DIR / "groundtruth.db"))
    except Exception:  # noqa: BLE001 - graceful degradation
        return None


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_glossary_entry(entry_text: str) -> str:
    """Return the entry text as-is (already includes its ### heading)."""
    return entry_text.rstrip()


def _format_semantic_candidate(row: dict[str, Any]) -> str:
    """Format a semantic candidate as a single bullet."""
    rid = row.get("id", "")
    title = (row.get("title") or "").strip()[:80]
    method = row.get("search_method")
    score = row.get("score")
    if method == "semantic" and isinstance(score, (int, float)):
        suffix = f"(distance ≈ {score:.3f})"
    else:
        suffix = "(text-match fallback)"
    return f"- [candidate for promotion] `{rid}`: {title} {suffix}"


def _truncate_to_budget(parts: list[str], budget: int) -> list[str]:
    """Trim ``parts`` to fit within ``budget`` bytes (utf-8).

    Drops trailing parts first. If a single part exceeds the budget, truncate
    its tail with an ellipsis so the entry's heading is always preserved.
    """
    out: list[str] = []
    used = 0
    sep = "\n\n"
    sep_bytes = len(sep.encode("utf-8"))
    for i, part in enumerate(parts):
        part_bytes = len(part.encode("utf-8"))
        added = part_bytes + (sep_bytes if i > 0 else 0)
        if used + added <= budget:
            out.append(part)
            used += added
        else:
            # If first part alone exceeds budget, truncate it.
            if not out and part_bytes > budget:
                # Preserve heading + first 200 chars + ellipsis.
                first_line, _, _rest = part.partition("\n")
                truncated = first_line + "\n\n" + (part[len(first_line) + 1 : 200] if len(part) > 200 else part) + "..."
                out.append(truncated[:budget])
            break
    return out


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def _write_audit_log(record: dict[str, Any]) -> None:
    try:
        AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = record.get("timestamp", datetime.now(UTC).isoformat()).replace(":", "-")
        path = AUDIT_LOG_DIR / f"{ts}.json"
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Hook entry point
# ---------------------------------------------------------------------------


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload))


def _emit_empty() -> None:
    sys.stdout.write("{}")


def _process(prompt: str) -> dict[str, Any]:
    """Compute the injection (and audit-log entry) for a prompt.

    Returns the dict to emit on stdout (either ``{}`` or
    ``{"systemMessage": "..."}``).
    """
    audit: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_length": len(prompt),
        "skipped": False,
        "skip_reason": None,
        "matched_glossary_terms": [],
        "candidate_phrases_forwarded": [],
        "semantic_hit_ids": [],
        "semantic_search_attempted": False,
        "injection_size_bytes": 0,
        "caps": {
            "MAX_GLOSSARY_MATCHES": MAX_GLOSSARY_MATCHES,
            "MAX_SEMANTIC_CANDIDATES": MAX_SEMANTIC_CANDIDATES,
            "SEMANTIC_MAX_DISTANCE": SEMANTIC_MAX_DISTANCE,
            "TOKEN_BUDGET_BYTES": TOKEN_BUDGET_BYTES,
        },
    }

    # Skip-rule check.
    stripped = prompt.strip()
    if not stripped or len(stripped) < 20:
        audit["skipped"] = True
        audit["skip_reason"] = "short_or_empty"
        return {}
    for prefix in _skip_prefixes():
        if prompt.startswith(prefix):
            audit["skipped"] = True
            audit["skip_reason"] = f"prefix_match:{prefix[:30]}"
            return {}

    # Tokenize.
    phrases = _tokenize_prompt(prompt)

    # Build glossary index.
    index, entries = _build_glossary_index()
    if not index:
        # Glossary unavailable; fail closed.
        audit["skipped"] = True
        audit["skip_reason"] = "glossary_unavailable"
        _write_audit_log(audit)
        return {}

    # Glossary match (capped).
    matched_headings: list[str] = []
    matched_set: set[str] = set()
    for phrase in phrases:
        if len(matched_headings) >= MAX_GLOSSARY_MATCHES:
            break
        heading = index.get(phrase)
        if heading and heading not in matched_set:
            matched_headings.append(heading)
            matched_set.add(heading)
    audit["matched_glossary_terms"] = matched_headings

    # Concept-shaped non-match filter.
    forwarded: list[str] = []
    for phrase in phrases:
        if len(forwarded) >= MAX_SEMANTIC_CANDIDATES:
            break
        if phrase in index:
            continue
        words = phrase.split()
        if len(words) >= 2 or len(phrase) >= 8:
            forwarded.append(phrase)
    audit["candidate_phrases_forwarded"] = forwarded

    # Semantic search (default-on; auto-DB-open).
    semantic_rows: list[dict[str, Any]] = []
    if forwarded:
        db = _try_open_default_db()
        audit["semantic_search_attempted"] = db is not None
        if db is not None:
            seen_ids: set[str] = set()
            for phrase in forwarded:
                try:
                    rows = db.search_deliberations(phrase, limit=DA_SEMANTIC_LIMIT) or []
                except Exception:  # noqa: BLE001 - graceful degradation
                    rows = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    method = row.get("search_method")
                    score = row.get("score")
                    # Distance contract: accept score is None (text-match) OR
                    # score <= SEMANTIC_MAX_DISTANCE (semantic; lower-is-better).
                    if method == "semantic" and isinstance(score, (int, float)):
                        if score > SEMANTIC_MAX_DISTANCE:
                            continue
                    rid = row.get("id")
                    if not isinstance(rid, str) or not rid or rid in seen_ids:
                        continue
                    seen_ids.add(rid)
                    semantic_rows.append(row)
    # Sort accepted semantic rows ascending by score (None sorts last).
    semantic_rows.sort(key=lambda r: (r.get("score") is None, r.get("score") or 0.0))
    audit["semantic_hit_ids"] = [r.get("id", "") for r in semantic_rows]

    # If nothing to inject, emit empty.
    if not matched_headings and not semantic_rows:
        _write_audit_log(audit)
        return {}

    # Format injection.
    parts: list[str] = []
    if matched_headings:
        parts.append("**Glossary matches:**")
        for heading in matched_headings:
            entry = entries.get(heading, "")
            if entry:
                parts.append(_format_glossary_entry(entry))
    if semantic_rows:
        sem_lines = ["### Candidate concepts (not yet in glossary)"]
        for row in semantic_rows:
            sem_lines.append(_format_semantic_candidate(row))
        parts.append("\n".join(sem_lines))

    # Apply token-budget cap (drop semantic-candidates section first).
    glossary_parts = parts[: 1 + len(matched_headings)] if matched_headings else []
    semantic_parts = parts[1 + len(matched_headings) :] if matched_headings else parts

    # F1 fix per `-001-008`: subtract the wrapper overhead before fitting
    # parts so the final emitted `systemMessage` bytes (including the
    # `<system-reminder>` wrapper + header line) stay within
    # `TOKEN_BUDGET_BYTES`. Capping only inner parts let total output
    # exceed the configured budget by ~110 bytes of wrapper overhead.
    _WRAPPER_PREFIX = "<system-reminder>\n**Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION):**\n\n"
    _WRAPPER_SUFFIX = "\n</system-reminder>"
    wrapper_overhead = len(_WRAPPER_PREFIX.encode("utf-8")) + len(_WRAPPER_SUFFIX.encode("utf-8"))
    inner_budget = max(0, TOKEN_BUDGET_BYTES - wrapper_overhead)

    fitted = _truncate_to_budget(glossary_parts, inner_budget) if glossary_parts else []
    remaining = inner_budget - sum(len(p.encode("utf-8")) + 2 for p in fitted)
    if remaining > 0 and semantic_parts:
        fitted += _truncate_to_budget(semantic_parts, remaining)

    if not fitted:
        _write_audit_log(audit)
        return {}

    body = _WRAPPER_PREFIX + "\n\n".join(fitted) + _WRAPPER_SUFFIX
    audit["injection_size_bytes"] = len(body.encode("utf-8"))
    _write_audit_log(audit)
    return {"systemMessage": body}


def main() -> int:
    try:
        try:
            payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
        except (json.JSONDecodeError, ValueError):
            payload = {}
        prompt = payload.get("prompt") or payload.get("user_prompt") or ""
        if not isinstance(prompt, str):
            prompt = str(prompt or "")
        result = _process(prompt)
        if result:
            _emit(result)
        else:
            _emit_empty()
        return 0
    except Exception as exc:  # noqa: BLE001 - never block the prompt
        sys.stderr.write(f"glossary-expansion hook error: {exc}\n")
        _emit_empty()
        return 0


if __name__ == "__main__":
    sys.exit(main())
