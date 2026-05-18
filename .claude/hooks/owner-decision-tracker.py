#!/usr/bin/env python3
"""
Claude Code Stop / UserPromptSubmit hook -- Owner-decision tracker.

Mechanically surfaces pending owner decisions across session boundaries by
maintaining a durable list at memory/pending-owner-decisions.md.

Two modes:

- Stop: parses the just-completed turn's JSONL transcript for
  AskUserQuestion tool_use entries and prose anti-pattern matches; appends
  unresolved questions to the durable file's `## Pending` section; moves
  same-turn-answered questions directly to `## Resolved`. Stop mode is
  silent for typical turns (durable-file remains the sole output; visibility
  comes from next SessionStart's startup disclosure and next
  UserPromptSubmit's nudge).

  BOUNDED EXCEPTION (per gtkb-decision-tracker-block-prose-ask-2026-04-29-003
  REVISED-1 §F3 Parent Bridge Contract Revision; Codex GO at -004): when the
  just-completed turn contains at least one prose-decision-ask AND zero
  AskUserQuestion tool_use entries, Stop mode emits a single
  `{"decision": "block", "reason": "..."}` JSON to stdout. This is a control-
  flow signal (prevents the agent from ending the turn so it can call
  AskUserQuestion to formalize the decision), NOT nudge text. The block
  emission is per-turn rate-limited to one and gated by env var
  GTKB_BLOCK_ON_PROSE_DECISION_ASK (default 1; =0 disables block emission
  while preserving detection + durable-file writes + graceful degradation).

  This bounded exception revises the original Slice 1 F3 rule "Stop writes
  durable state only" (parent GO at gtkb-gov-owner-decision-surfacing-slice1
  -004.md). For all other cases — typical turns, false-positive-guarded
  prose, prose-with-AskUserQuestion turns — Stop mode remains silent and
  exits 0.

- UserPromptSubmit: reads the durable file; if the user's prompt does NOT
  reference a pending decision (by DECISION-NNNN ID, decision keywords,
  or a recognized owner shortcut), emits a nudge to stdout (which the
  Claude Code hook contract injects into the model's context as
  additionalContext). Recognized owner shortcuts mutate the durable file
  in-place: `defer all`, `defer DECISION-NNNN`,
  `resolve DECISION-NNNN: <answer>`, `clear pending`.

Stdin: JSON hook event payload per
       https://code.claude.com/docs/en/hooks
Stdout: empty (typical Stop), block-decision JSON (Stop hard-condition),
        or markdown text (UserPromptSubmit mode)
Exit:   Always 0 (graceful degradation; never crashes the agent). Note
        that the hook control-flow signal `{"decision": "block"}` causes
        the harness to refuse to end the turn — that is NOT the same as
        a non-zero exit code.

Authority:
- bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md REVISED
- bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md GO (parent F3 rule)
- bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md REVISED-1
  (F3 bounded exception; Codex GO at -004)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# DECISION-NNNN ID prefix. The next ID is computed from the highest extant
# numeric suffix in the durable file plus 1; new tracking IDs use this
# format so they are stable across sessions and easy to reference in chat.
DECISION_ID_PREFIX = "DECISION-"

# Resolved entries older than this many days move to ## History on Stop.
# 30 days chosen to keep ## Resolved scannable while preserving recent
# decisions for cross-session reference (most decisions are referenced
# within a sprint or two of resolution).
HISTORY_AGE_DAYS = 30

# question_hash uses sha256 of question + sorted option labels, truncated
# to 16 hex chars (~64 bits). Length-collision probability is negligible
# for the durable-file scale; full sha256 would bloat the file unnecessarily.
QUESTION_HASH_LENGTH = 16

# Project root resolution: prefer CLAUDE_PROJECT_DIR env var (Claude Code
# sets this for hooks); fall back to walking up from this file's location.
PROJECT_ROOT = Path(
    os.environ.get("CLAUDE_PROJECT_DIR")
    or Path(__file__).resolve().parents[2]
).resolve()

PENDING_FILE_REL = "memory/pending-owner-decisions.md"

# Prose anti-patterns: phrasings that indicate the assistant is asking
# for an owner decision in prose rather than via AskUserQuestion. Each
# pattern is documented with the failure mode it catches; false positives
# are mitigated by T14 (abstract-decision-discussion guard) and by the
# non-blocking nature of nudges (worst case: one extra reminder).
PROSE_DECISION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # All patterns prefixed with negative lookbehind (?<!["`]) to suppress
    # quoted/backtick-bounded literals (DECISION-0001/0002 FP class, S309).
    # See bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md.
    ("offering_or_choice", re.compile(
        r'(?<!["`])\bwant me to\b[^.?!]*\bor\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("should_i_or", re.compile(
        r'(?<!["`])\bshould I\b[^.?!]*\bor\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    # Split awaiting_input into _q (interrogative) + _first_person (active wait).
    # Bare "Awaiting your X." status statements no longer match (S328 directive).
    ("awaiting_input_q", re.compile(
        r'(?<!["`])\bawaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("awaiting_input_first_person", re.compile(
        r'(?<!["`])\b(?:i am|i\'m|we are|we\'re)\s+awaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b',
        re.IGNORECASE,
    )),
    # Split standing_by_for similarly.
    ("standing_by_for_q", re.compile(
        r'(?<!["`])\bstanding by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("standing_by_for_first_person", re.compile(
        r'(?<!["`])\b(?:i am|i\'m|we are|we\'re)\s+standing by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b',
        re.IGNORECASE,
    )),
    ("your_decision_q", re.compile(
        r'(?<!["`])\b(?:your|owner)\s+(?:decision|choice|input)\b[^.?!]{0,80}\?',
        re.IGNORECASE,
    )),
)

# False-positive guard for prose detection (T14): patterns that look like
# decision asks but are actually abstract discussion or detector-describing
# text. Per Sub-slice A revision -007: applied per-match against bounded
# local window (GUARD_LOCAL_WINDOW_CHARS), not full event.
PROSE_FALSE_POSITIVE_GUARDS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdecisions are (?:hard|complex|difficult|tricky)\b", re.IGNORECASE),
    re.compile(r"\bin general,?\s+decisions?\b", re.IGNORECASE),
    re.compile(r"\babstract(?:ly)?,?\s+(?:about\s+)?decisions?\b", re.IGNORECASE),
    # Self-reference suppressor (S328 directive): suppresses match when
    # local window mentions detector internals.
    re.compile(
        r"\b(?:PROSE_DECISION_PATTERNS|owner-decision-tracker|decision-tracker|prose pattern|prose-pattern|regex tightening)\b",
        re.IGNORECASE,
    ),
    # Bridge-metadata context suppressor: bridge-state words signal
    # factual bridge-thread reporting, not a decision-ask.
    re.compile(
        r"\bCodex (?:GO|NO-GO|VERIFIED|review|`-\d+|F\d|umbrella)\b",
        re.IGNORECASE,
    ),
)

# Per Sub-slice A revision -007 §F1 (Codex -002 finding): guards are applied
# against a local window around each match, not the full assistant event.
# This prevents systematic false negatives when one event mentions bridge
# state alongside an unrelated genuine prose decision-ask.
GUARD_LOCAL_WINDOW_CHARS = 200


# Per Sub-slice A follow-up bridge -005 GO at -006 (code-fence-aware
# structural FP guards): the negative-lookbehind in PROSE_DECISION_PATTERNS
# is a single-character guard. It does not catch the same trigger phrases
# embedded inside multi-line markdown structural contexts (fenced code
# blocks, indented code blocks, blockquotes, HTML comments). With Stop-mode
# block emission live as of Sub-slice A -014 VERIFIED, the cost of those
# structural false positives is materially higher (turn-end refusal rather
# than nudge). The structural pre-check below runs BEFORE the in-window
# PROSE_FALSE_POSITIVE_GUARDS so the latter remain limited to in-window
# semantic guards (Sub-slice A -007 §F1 invariant preserved).
_FENCE_LINE_RE = re.compile(r"(?:^|\n)```")


def _is_inside_structural_context(text: str, match_start: int) -> bool:
    """Return True if ``match_start`` falls inside a markdown structural
    context where a trigger pattern should be treated as documentation
    rather than a real owner-decision-ask. Covers four contexts:

    1. Triple-backtick fenced code block (line-anchored).
    2. 4-space indented code block (line-prefix heuristic).
    3. Markdown blockquote (line starts with ``> ``).
    4. HTML comment (between unclosed ``<!--`` and the next ``-->``).
    """
    prefix = text[:match_start]

    # 1. Triple-backtick fenced code block: count line-anchored fences in
    # the prefix. Odd count means we are inside an open fence.
    fence_count = len(_FENCE_LINE_RE.findall(prefix))
    if fence_count % 2 == 1:
        return True

    # 2. HTML comment: if the most recent ``<!--`` is later than the most
    # recent ``-->`` (or there is no closing ``-->`` at all), match is
    # inside the comment.
    last_open = prefix.rfind("<!--")
    last_close = prefix.rfind("-->")
    if last_open != -1 and last_open > last_close:
        return True

    # Identify the line containing match_start.
    line_start = prefix.rfind("\n") + 1  # 0 if no preceding newline.
    next_newline = text.find("\n", match_start)
    line_full = text[line_start:] if next_newline == -1 else text[line_start:next_newline]

    # 3. Markdown blockquote.
    if line_full.startswith("> "):
        return True

    # 4. 4-space indented code block (heuristic: line prefix only; does
    # not enforce the preceding-blank-line CommonMark requirement, since
    # the false-positive cost of suppressing 4-space-indented prose is
    # low and rare in our bridge corpus).
    if line_full.startswith("    "):
        return True

    return False

# Block emission feature flag (Codex -004 GO condition 3).
# Default '1' (enabled); '=0' suppresses block JSON only — detection,
# durable-file appends, and graceful degradation are preserved.
BLOCK_EMISSION_ENV_VAR = "GTKB_BLOCK_ON_PROSE_DECISION_ASK"

# Per Codex -004 GO condition 4 + Q5 answer: cap displayed prose-pattern
# matches in the block reason text at 3 entries; if more matches were detected,
# include "(N additional matches)" suffix.
BLOCK_REASON_DISPLAYED_MATCHES_CAP = 3

# Maximum excerpt length per matched snippet in the block reason text.
# Snippets longer than this get truncated with "..." to keep the
# additionalContext block concise.
BLOCK_REASON_EXCERPT_MAX_LEN = 80


def _block_emission_enabled() -> bool:
    """Return True when block JSON emission is enabled (env var unset or != '0').

    Per Codex -004 GO condition 3: this flag suppresses ONLY the block JSON
    emission; prose detection, durable-file appends, and graceful degradation
    on malformed input are NOT suppressed.
    """
    return os.environ.get(BLOCK_EMISSION_ENV_VAR, "1") != "0"


def _build_block_decision(matches: list[tuple[str, str]]) -> dict[str, str]:
    """Construct the Stop-mode block-decision JSON.

    Per gtkb-decision-tracker-block-prose-ask-2026-04-29-003 REVISED-1 §1.4
    (output schema) + Codex -004 Q5 cap-at-3:

    - Lists the first ``BLOCK_REASON_DISPLAYED_MATCHES_CAP`` matches with
      pattern_id and a truncated excerpt.
    - If extra matches were detected, includes a "(N additional matches)"
      suffix so the count is visible.
    - Names the resolution path (call AskUserQuestion).
    - Names the disable path (env var ``GTKB_BLOCK_ON_PROSE_DECISION_ASK=0``).
    """
    displayed = matches[: BLOCK_REASON_DISPLAYED_MATCHES_CAP]
    extra_count = len(matches) - len(displayed)

    header = (
        f"Matched patterns (showing first {len(displayed)} of {len(matches)}):"
        if len(matches) > BLOCK_REASON_DISPLAYED_MATCHES_CAP
        else "Matched patterns:"
    )
    lines = [
        "Owner-decision-tracker: prose decision ask(s) detected without "
        "AskUserQuestion call this turn.",
        "",
        header,
    ]
    for name, snippet in displayed:
        excerpt = snippet[:BLOCK_REASON_EXCERPT_MAX_LEN]
        if len(snippet) > BLOCK_REASON_EXCERPT_MAX_LEN:
            excerpt = excerpt + "..."
        lines.append(f"  - {name}: '{excerpt}'")
    if extra_count > 0:
        lines.append(f"  ({extra_count} additional matches)")
    lines.extend([
        "",
        "Resolution: call AskUserQuestion with the detected questions "
        "formalized as structured options. The dialog produces a clickable "
        "popup the user can respond to inline; prose questions get lost in "
        "chat scrollback.",
        "",
        f"Disable: set env var {BLOCK_EMISSION_ENV_VAR}=0 to suppress block "
        f"emission while keeping detection + durable-file writes.",
    ])
    return {"decision": "block", "reason": "\n".join(lines)}


# ---------------------------------------------------------------------------
# Durable-file model + I/O
# ---------------------------------------------------------------------------

@dataclass
class DecisionEntry:
    """One pending or resolved owner-decision entry.

    Stored as YAML-frontmatter list shape under ## Pending / ## Resolved /
    ## History sections in memory/pending-owner-decisions.md. The hook is
    the canonical writer; manual edits should add an Edited-by-owner note.
    """
    id: str
    asked_at: str
    asked_in_session: str = ""
    thread_ref: str = ""
    question: str = ""
    options: list[str] = field(default_factory=list)
    detected_via: str = "ask_user_question"
    status: str = "pending"
    question_hash: str = ""
    notes: str = ""
    resolved_at: str = ""
    resolved_in_session: str = ""
    resolved_via: str = ""
    answer: str = ""

    def render(self) -> str:
        """Render as a markdown bullet block (YAML-frontmatter style).

        Multi-line fields are quoted; lists are inlined as `- "..."` bullets.
        """
        lines = [f"- id: {self.id}"]
        lines.append(f"  asked_at: {self.asked_at}")
        if self.asked_in_session:
            lines.append(f"  asked_in_session: {self.asked_in_session}")
        if self.thread_ref:
            lines.append(f"  thread_ref: {self.thread_ref}")
        # Quote question text to handle colons/quotes in the prose.
        lines.append(f"  question: {_quote_yaml(self.question)}")
        if self.options:
            lines.append("  options:")
            for opt in self.options:
                lines.append(f"    - {_quote_yaml(opt)}")
        lines.append(f"  detected_via: {self.detected_via}")
        lines.append(f"  status: {self.status}")
        if self.question_hash:
            lines.append(f"  question_hash: {self.question_hash}")
        if self.resolved_at:
            lines.append(f"  resolved_at: {self.resolved_at}")
        if self.resolved_in_session:
            lines.append(f"  resolved_in_session: {self.resolved_in_session}")
        if self.resolved_via:
            lines.append(f"  resolved_via: {self.resolved_via}")
        if self.answer:
            lines.append(f"  answer: {_quote_yaml(self.answer)}")
        lines.append(f"  notes: {_quote_yaml(self.notes) if self.notes else '\"\"'}")
        return "\n".join(lines)


def _quote_yaml(value: str) -> str:
    """Return a YAML-safe scalar for plain string values.

    We use double quotes and escape embedded backslashes/doublequotes; this
    handles the common cases (paths, quoted names) without pulling in a
    YAML library. Newlines in question text are folded to spaces (decision
    questions are short by convention; multi-paragraph questions belong in
    a thread_ref bridge file, not in the question field itself).
    """
    s = value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")
    return f"\"{s}\""


def _ensure_pending_file(path: Path) -> None:
    """Create the durable file from template if missing.

    Used as a graceful-degradation fallback: if a session loses the file
    (e.g., manual deletion), the hook regenerates the empty template
    rather than failing. Callers must still treat read/parse failures as
    benign (return empty pending list).
    """
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_DURABLE_TEMPLATE, encoding="utf-8")


_DURABLE_TEMPLATE = """\
# Pending Owner Decisions

This file is owned by .claude/hooks/owner-decision-tracker.py.

---

## Pending

(none)

## Resolved

(none)

## History

(none)
"""


def _read_pending_file(path: Path) -> dict[str, list[DecisionEntry]]:
    """Parse the durable file into per-section lists.

    Returns {"pending": [...], "resolved": [...], "history": [...]}.
    Malformed files trigger a corruption-preservation fallback: the
    malformed file is renamed to .corrupted-<timestamp>; a fresh template
    replaces it; the returned dict has empty lists.

    Parse strategy is line-based (no YAML library): scan for `## Pending`
    / `## Resolved` / `## History` headings; within each section, parse
    bullet blocks starting with `- id: DECISION-...`. Each block ends at
    blank line, next bullet, or next heading. Field values are read as
    rest-of-line for plain strings; quoted values strip surrounding
    double quotes; option list items are nested under `  options:` and
    each starts with `    - `.
    """
    if not path.exists():
        return {"pending": [], "resolved": [], "history": []}

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"owner-decision-tracker: read failed: {exc}\n")
        return {"pending": [], "resolved": [], "history": []}

    sections: dict[str, list[DecisionEntry]] = {"pending": [], "resolved": [], "history": []}
    current_section: str | None = None
    current_entry: DecisionEntry | None = None
    in_options = False

    try:
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            stripped = line.strip()

            if stripped.startswith("## "):
                # Flush the in-flight entry to the OLD section before
                # changing to the new heading; otherwise the entry's
                # contents (which belong to the prior section) land in
                # the section we're transitioning into.
                _flush_entry(sections, current_section, current_entry)
                current_entry = None
                in_options = False
                heading = stripped[3:].strip().lower()
                if heading in sections:
                    current_section = heading
                else:
                    current_section = None
                continue

            if current_section is None:
                continue

            if stripped.startswith("- id: "):
                _flush_entry(sections, current_section, current_entry)
                current_entry = DecisionEntry(
                    id=stripped[len("- id: "):].strip(),
                    asked_at="",
                    status="pending" if current_section == "pending" else "resolved",
                )
                in_options = False
                continue

            if current_entry is None:
                continue

            if line.startswith("  options:"):
                in_options = True
                continue

            if in_options and line.startswith("    - "):
                current_entry.options.append(_unquote_yaml(line[len("    - "):]))
                continue

            if line.startswith("  ") and ":" in stripped:
                in_options = False
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = _unquote_yaml(val.strip())
                _set_entry_field(current_entry, key, val)

        _flush_entry(sections, current_section, current_entry)
    except Exception as exc:
        # Preserve the malformed file for forensics; replace with template.
        sys.stderr.write(f"owner-decision-tracker: parse failed ({exc}); preserving as .corrupted\n")
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        try:
            path.rename(path.with_suffix(path.suffix + f".corrupted-{ts}"))
        except OSError:
            pass
        path.write_text(_DURABLE_TEMPLATE, encoding="utf-8")
        return {"pending": [], "resolved": [], "history": []}

    return sections


def _flush_entry(
    sections: dict[str, list[DecisionEntry]],
    section: str | None,
    entry: DecisionEntry | None,
) -> None:
    """Append a parsed entry to its section if both are valid."""
    if section is None or entry is None:
        return
    if not entry.id.startswith(DECISION_ID_PREFIX):
        return
    sections[section].append(entry)


def _unquote_yaml(value: str) -> str:
    """Strip surrounding double quotes and unescape; pass-through otherwise."""
    if value.startswith("\"") and value.endswith("\"") and len(value) >= 2:
        body = value[1:-1]
        return body.replace("\\\"", "\"").replace("\\\\", "\\")
    return value


def _set_entry_field(entry: DecisionEntry, key: str, val: str) -> None:
    """Apply a parsed key:val pair to the entry. Unknown keys are ignored."""
    field_map = {
        "asked_at": "asked_at",
        "asked_in_session": "asked_in_session",
        "thread_ref": "thread_ref",
        "question": "question",
        "detected_via": "detected_via",
        "status": "status",
        "question_hash": "question_hash",
        "notes": "notes",
        "resolved_at": "resolved_at",
        "resolved_in_session": "resolved_in_session",
        "resolved_via": "resolved_via",
        "answer": "answer",
    }
    attr = field_map.get(key)
    if attr is not None:
        setattr(entry, attr, val)


def _write_pending_file(path: Path, sections: dict[str, list[DecisionEntry]]) -> None:
    """Render and atomically write the durable file.

    Atomic-ish: write to .tmp sibling, then os.replace. Preserves the
    file across crashes during write.
    """
    parts = [
        "# Pending Owner Decisions",
        "",
        "This file is owned by .claude/hooks/owner-decision-tracker.py.",
        "",
        "---",
        "",
    ]
    for section in ("Pending", "Resolved", "History"):
        parts.append(f"## {section}")
        parts.append("")
        entries = sections.get(section.lower(), [])
        if not entries:
            parts.append("(none)")
        else:
            for entry in entries:
                parts.append(entry.render())
        parts.append("")
    text = "\n".join(parts).rstrip() + "\n"

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _next_decision_id(sections: dict[str, list[DecisionEntry]]) -> str:
    """Compute the next DECISION-NNNN id based on highest extant suffix.

    Stable across all three sections so a resolved entry's id is never
    reused for a new pending entry.
    """
    highest = 0
    for entries in sections.values():
        for entry in entries:
            if entry.id.startswith(DECISION_ID_PREFIX):
                tail = entry.id[len(DECISION_ID_PREFIX):]
                try:
                    highest = max(highest, int(tail))
                except ValueError:
                    continue
    return f"{DECISION_ID_PREFIX}{highest + 1:04d}"


def _question_hash(question: str, options: list[str]) -> str:
    """Stable hash of question text + sorted option labels.

    Used for idempotence: the same question asked twice in one turn (or
    re-asked across sessions) collides on hash and is deduped.
    """
    payload = question + "␟" + "␟".join(sorted(options))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:QUESTION_HASH_LENGTH]


# ---------------------------------------------------------------------------
# Stop mode -- transcript JSONL parsing
# ---------------------------------------------------------------------------

def _parse_stop_payload(stdin_text: str) -> dict[str, Any]:
    """Parse the Stop hook event payload from stdin.

    Returns empty dict on parse failure (graceful degradation).
    """
    try:
        return json.loads(stdin_text or "{}")
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"owner-decision-tracker: stop payload decode failed: {exc}\n")
        return {}


def _read_transcript_tail(path: Path, max_events: int = 500) -> list[dict[str, Any]]:
    """Read the last N JSONL events from the transcript file.

    Memory-bounded: transcripts can be MB-scale; we only need recent
    events to identify the just-completed turn. Returns events in
    file order (oldest first within the tail). Truncated/corrupt lines
    are skipped silently with a stderr log.

    The 500-event tail is sized for typical Claude Code sessions (a
    long single turn is rarely above 100 events; 500 covers multi-turn
    context with margin while staying well under the file size at
    which line-by-line read becomes slow).
    """
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        sys.stderr.write(f"owner-decision-tracker: transcript read failed: {exc}\n")
        return []

    tail_lines = lines[-max_events:] if len(lines) > max_events else lines
    events: list[dict[str, Any]] = []
    for line in tail_lines:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _find_just_completed_turn(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify the assistant events of the just-completed turn.

    Scans backwards for the most recent real-user event (type=="user"
    with non-tool_result content); returns every event from there to
    the end of the list. Tool-result-only continuations from agent
    loops are skipped because their type=="user" but their content is
    a tool_result list.

    Empty list when no real user event is found (corrupt or pre-turn
    transcript).
    """
    boundary_idx = -1
    for idx in range(len(events) - 1, -1, -1):
        ev = events[idx]
        if ev.get("type") != "user":
            continue
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            boundary_idx = idx
            break
        if isinstance(content, list):
            # Real user turn has a leading text part; tool_result-only
            # continuations have a leading tool_result part.
            first_part = content[0] if content else {}
            part_type = first_part.get("type") if isinstance(first_part, dict) else None
            if part_type and part_type != "tool_result":
                boundary_idx = idx
                break
    if boundary_idx < 0:
        return []
    return events[boundary_idx:]


def _scan_askuserquestion(turn_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract every (tool_use, tool_result|None) pair for AskUserQuestion calls.

    tool_result is matched by tool_use_id. Same-turn unanswered calls
    have tool_result=None and become Pending entries; same-turn answered
    calls have a matching tool_result and become Resolved.
    """
    tool_uses: list[dict[str, Any]] = []
    tool_results_by_id: dict[str, dict[str, Any]] = {}

    for ev in turn_events:
        message = ev.get("message") or {}
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            ptype = part.get("type")
            if ptype == "tool_use" and part.get("name") == "AskUserQuestion":
                tool_uses.append(part)
            elif ptype == "tool_result":
                tu_id = part.get("tool_use_id")
                if tu_id:
                    tool_results_by_id[tu_id] = part

    pairs: list[dict[str, Any]] = []
    for tu in tool_uses:
        tr = tool_results_by_id.get(tu.get("id", ""))
        pairs.append({"tool_use": tu, "tool_result": tr})
    return pairs


def _extract_question_snippet(full_text: str, match: re.Match[str]) -> str:
    """Extract just the matched question, sentence-bounded.

    Per DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001:
    capture the matched group itself, optionally extending forward to the
    nearest sentence terminator within a 60-char window if the match doesn't
    already end at one. Cap total length at 120 chars. Decorative prefix/
    suffix bytes (markdown structural artifacts outside the match) are
    not captured.
    """
    matched = match.group(0)
    end = match.end()
    if not matched.rstrip().endswith(("?", "!", ".")):
        forward_window = full_text[end:end + 60]
        terminator_match = re.search(r"[.?!]", forward_window)
        if terminator_match:
            matched = matched + forward_window[:terminator_match.end()]
    matched = matched.strip()
    if len(matched) > 120:
        matched = matched[:117] + "..."
    return matched


# Boilerplate stoplist for discriminating-token correlation per
# DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 Signal A. Conservative
# (biases toward false-negatives so unrelated decisions are not silently
# auto-resolved). After stoplist removal, the remaining tokens carry the
# discriminating semantic.
_CORRELATION_STOPLIST: frozenset[str] = frozenset({
    "want", "me", "to", "or", "wait", "should", "i", "now", "approve", "the",
    "defer", "do", "you", "we", "is", "this", "are", "go", "stop", "yes", "no",
    "any", "of", "in", "on", "at", "for", "with", "and", "but", "as", "be",
    "have", "has", "had", "did", "does", "can", "could", "will", "would",
    "shall", "must", "may", "might",
})


_CORRELATION_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _normalize_question_text(text: str) -> str:
    """Lower-case, whitespace-collapse, strip non-alphanumeric punctuation.

    Used as the basis for substring containment (B1) and text identity (B3)
    correlation signals.
    """
    lowered = text.lower()
    # Collapse all non-alphanumeric runs (including punctuation) to single space.
    collapsed = re.sub(r"[^a-z0-9]+", " ", lowered).strip()
    return collapsed


def _tokenize_with_stoplist(text: str) -> set[str]:
    """Tokenize on alphanumeric word boundaries; remove stoplist tokens.

    Returns the discriminating-token set used by Signal A (Jaccard).
    """
    tokens = {m.group(0).lower() for m in _CORRELATION_TOKEN_RE.finditer(text)}
    return tokens - _CORRELATION_STOPLIST


def _discriminating_jaccard(prose_tokens: set[str], auq_tokens: set[str]) -> tuple[float, bool]:
    """Compute discriminating-token Jaccard + has-min-length-noun-or-verb flag.

    Returns ``(J_d, has_min_length_token)`` where:

    - ``J_d = |prose ∩ auq| / |prose ∪ auq|``, or 0.0 if union is empty.
    - ``has_min_length_token = True`` iff at least one shared token has
      length ≥ 4 chars and is not pure-numeric (heuristic noun/verb gate).
    """
    union = prose_tokens | auq_tokens
    if not union:
        return (0.0, False)
    intersection = prose_tokens & auq_tokens
    j_d = len(intersection) / len(union)
    has_min_length = any(
        len(tok) >= 4 and not tok.isdigit() for tok in intersection
    )
    return (j_d, has_min_length)


def _substring_containment_min_length(a: str, b: str, min_chars: int = 20) -> bool:
    """Signal B1: normalized substring containment with minimum substantive length.

    After normalization, one is a substring of the other AND the shared
    substring length is ≥ ``min_chars``.
    """
    norm_a = _normalize_question_text(a)
    norm_b = _normalize_question_text(b)
    if not norm_a or not norm_b:
        return False
    shorter, longer = (norm_a, norm_b) if len(norm_a) <= len(norm_b) else (norm_b, norm_a)
    if len(shorter) < min_chars:
        return False
    return shorter in longer


def _option_label_overlap(prose: str, auq_options: list[str]) -> bool:
    """Signal B2: at least one AUQ option label appears verbatim (lower-cased)
    in the prose snippet OR vice versa.
    """
    prose_norm = _normalize_question_text(prose)
    if not prose_norm:
        return False
    for opt in auq_options:
        opt_norm = _normalize_question_text(opt)
        if not opt_norm:
            continue
        if opt_norm in prose_norm or prose_norm in opt_norm:
            return True
    return False


def _correlate_prose_to_auq(
    prose_snippet: str,
    auq_question: str,
    auq_options: list[str],
) -> tuple[bool, str | None]:
    """Two-signal-required correlation per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.

    Returns ``(correlated, b_signal_name | None)``. Correlated iff
    Signal A (discriminating-token Jaccard ≥ 0.5 with ≥1 shared token of
    length ≥ 4 chars) AND at least one of Signal B1 / B2 / B3.
    """
    prose_tokens = _tokenize_with_stoplist(prose_snippet)
    auq_tokens = _tokenize_with_stoplist(auq_question)
    j_d, has_min_length = _discriminating_jaccard(prose_tokens, auq_tokens)
    if j_d < 0.5 or not has_min_length:
        return (False, None)
    # Signal A passed; check B signals (any one suffices).
    norm_prose = _normalize_question_text(prose_snippet)
    norm_auq = _normalize_question_text(auq_question)
    if norm_prose and norm_prose == norm_auq:
        return (True, "text_identity")  # B3
    if _substring_containment_min_length(prose_snippet, auq_question):
        return (True, "normalized_substring")  # B1
    if _option_label_overlap(prose_snippet, auq_options):
        return (True, "option_label_overlap")  # B2
    return (False, None)


def _scan_prose_decisions(turn_events: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Find prose anti-pattern matches in assistant text content.

    Returns (pattern_name, snippet) tuples. False-positive guard
    suppresses matches that also match the abstract-discussion guard
    patterns (T14 case).
    """
    matches: list[tuple[str, str]] = []
    for ev in turn_events:
        if ev.get("type") != "assistant":
            continue
        message = ev.get("message") or {}
        content = message.get("content")
        text_parts: list[str] = []
        if isinstance(content, str):
            text_parts.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(str(part.get("text") or ""))
        full_text = "\n".join(text_parts)
        # Per Sub-slice A -007 §F1: guards applied per-match against bounded
        # local window (GUARD_LOCAL_WINDOW_CHARS), not full_text. Switch from
        # pattern.search() (first match only) to pattern.finditer() (all
        # matches) so multiple genuine asks in one event are detected, and
        # an unrelated guard-region elsewhere in the event does not suppress
        # them. T-mixed-event-1 + T-mixed-event-2 verify this behavior.
        for name, pattern in PROSE_DECISION_PATTERNS:
            for m in pattern.finditer(full_text):
                # Structural pre-check (Sub-slice A follow-up -006 GO):
                # skip matches inside fenced/indented/blockquoted/HTML-
                # commented contexts. Runs before the in-window guards so
                # the latter remain limited to semantic in-window checks.
                if _is_inside_structural_context(full_text, m.start()):
                    continue
                window_start = max(0, m.start() - GUARD_LOCAL_WINDOW_CHARS)
                window_end = min(len(full_text), m.end() + GUARD_LOCAL_WINDOW_CHARS)
                window = full_text[window_start:window_end]
                if any(g.search(window) for g in PROSE_FALSE_POSITIVE_GUARDS):
                    continue
                snippet = _extract_question_snippet(full_text, m)
                matches.append((name, snippet))
    return matches


def _stop_handler(stdin_text: str) -> dict[str, str] | None:
    """Stop mode entry point.

    Reads transcript, identifies turn boundary, scans AskUserQuestion +
    prose patterns, mutates the durable file.

    Returns:
        ``None`` for typical turns (Stop mode silent; durable-file is the
        sole output).

        A dict ``{"decision": "block", "reason": "..."}`` when ALL of the
        following hold (per gtkb-decision-tracker-block-prose-ask-2026-04-29
        -003 REVISED-1 §F3 Parent Bridge Contract Revision):

        1. The just-completed turn contained at least one FRESH prose-decision-
           ask matching one of the PROSE_DECISION_PATTERNS (after T14 false-
           positive guards and the WI-3332 known-relay filter -- a match that
           merely relays an already-recorded owner decision is not block-
           eligible).
        2. The same turn contained ZERO AskUserQuestion tool_use entries
           (askuserquestion_count is per just-completed turn, not session-
           cumulative — per Codex -004 Q1 answer).
        3. The env var ``GTKB_BLOCK_ON_PROSE_DECISION_ASK`` is not '0'.

        The block decision is per-turn rate-limited to one (single return
        value; caller emits exactly one JSON to stdout). Detection +
        durable-file appends + graceful degradation are preserved regardless
        of the env-var setting.
    """
    payload = _parse_stop_payload(stdin_text)
    transcript_path_str = payload.get("transcript_path", "")
    if not transcript_path_str:
        return None  # No transcript; nothing to scan.

    transcript_path = Path(transcript_path_str)
    events = _read_transcript_tail(transcript_path)
    turn_events = _find_just_completed_turn(events)
    if not turn_events:
        return None

    pending_path = PROJECT_ROOT / PENDING_FILE_REL
    _ensure_pending_file(pending_path)
    sections = _read_pending_file(pending_path)

    # Build a set of existing question hashes for idempotence.
    existing_hashes: set[str] = set()
    for entries in sections.values():
        for e in entries:
            if e.question_hash:
                existing_hashes.add(e.question_hash)

    # Known-decision identity snapshot for startup-relay suppression (WI-3332).
    # A prose match that merely relays an already-recorded owner decision
    # (e.g. a startup disclosure echoing the Pending Owner Decisions section)
    # must not be treated as a fresh owner-decision-ask. This snapshot is built
    # once from all sections (Pending / Resolved / History) and is NOT mutated
    # during the scan, so freshness is judged only against decisions recorded
    # before this turn. Exact hash identity and exact normalized-text identity
    # only -- no fuzzy matching (per the -004 GO scope constraint).
    known_decision_hashes: set[str] = set(existing_hashes)
    known_decision_norms: set[str] = set()
    for entries in sections.values():
        for e in entries:
            if e.question:
                known_decision_hashes.add(_question_hash(e.question, []))
                norm = _normalize_question_text(e.question)
                if norm:
                    known_decision_norms.add(norm)

    asked_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    session_hint = _session_hint()
    mutated = False

    # Scan A -- AskUserQuestion pairs. Track per-turn count for block-emission
    # decision (per Codex -004 Q1: per just-completed turn, not session-cumulative).
    # Also accumulate question/option pairs for same-turn correlation with
    # prose matches per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.
    askuserquestion_count = 0
    auq_questions_this_turn: list[tuple[str, list[str]]] = []
    for pair in _scan_askuserquestion(turn_events):
        askuserquestion_count += 1
        tu = pair["tool_use"]
        tu_input = tu.get("input") or {}
        questions = tu_input.get("questions") or []
        for q in questions:
            if not isinstance(q, dict):
                continue
            question_text = str(q.get("question") or "").strip()
            options = [
                str(opt.get("label") or "")
                for opt in (q.get("options") or [])
                if isinstance(opt, dict)
            ]
            if not question_text:
                continue
            auq_questions_this_turn.append((question_text, options))
            qhash = _question_hash(question_text, options)
            if qhash in existing_hashes:
                continue
            existing_hashes.add(qhash)
            new_id = _next_decision_id(sections)
            entry = DecisionEntry(
                id=new_id,
                asked_at=asked_at,
                asked_in_session=session_hint,
                question=question_text,
                options=options,
                detected_via="ask_user_question",
                status="pending",
                question_hash=qhash,
            )
            tr = pair["tool_result"]
            if tr is not None:
                entry.status = "resolved"
                entry.resolved_at = asked_at
                entry.resolved_in_session = session_hint
                entry.answer = _extract_answer_text(tr)
                sections["resolved"].append(entry)
            else:
                sections["pending"].append(entry)
            mutated = True

    # Scan B -- prose anti-patterns. ``prose_matches_this_turn`` is the raw
    # scan result feeding the durable-file append/correlation path (which uses
    # idempotence to avoid duplicates). ``fresh_prose_matches_this_turn`` is the
    # block-eligible subset: matches that do NOT relay an already-recorded owner
    # decision. Only fresh matches drive Stop-block emission (WI-3332) --
    # relaying a known pending/resolved/history decision during a startup
    # disclosure or status update must not refuse turn-end.
    #
    # Per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001: if the same
    # turn contains a correlated AskUserQuestion (two-signal-required:
    # discriminating-token Jaccard ≥ 0.5 AND one of substring / option-label /
    # text-identity), auto-resolve the prose entry to ## Resolved instead of
    # appending to ## Pending. Correlation is fail-closed (biases toward
    # leaving prose pending; never silently auto-resolves an unrelated decision).
    prose_matches_this_turn: list[tuple[str, str]] = []
    fresh_prose_matches_this_turn: list[tuple[str, str]] = []
    for name, snippet in _scan_prose_decisions(turn_events):
        prose_matches_this_turn.append((name, snippet))
        prose_hash = _question_hash(snippet, [])
        # Startup-relay suppression (WI-3332): a prose match whose identity
        # matches an already-recorded decision is a relay, not a fresh ask. It
        # is excluded from Stop-block eligibility but still flows through the
        # durable-append/correlation path below (idempotence dedups it).
        snippet_norm = _normalize_question_text(snippet)
        is_known_relay = prose_hash in known_decision_hashes or (
            bool(snippet_norm) and snippet_norm in known_decision_norms
        )
        if not is_known_relay:
            fresh_prose_matches_this_turn.append((name, snippet))
        if prose_hash in existing_hashes:
            continue
        existing_hashes.add(prose_hash)
        new_id = _next_decision_id(sections)
        # Two-signal correlation against AUQ questions in this turn.
        b_signal: str | None = None
        for auq_question, auq_options in auq_questions_this_turn:
            correlated, signal_name = _correlate_prose_to_auq(
                snippet, auq_question, auq_options
            )
            if correlated:
                b_signal = signal_name
                break
        if b_signal is not None:
            entry = DecisionEntry(
                id=new_id,
                asked_at=asked_at,
                asked_in_session=session_hint,
                question=snippet,
                detected_via=f"prose:{name}",
                status="resolved",
                question_hash=prose_hash,
                resolved_at=asked_at,
                resolved_in_session=session_hint,
                resolved_via="same_turn_auq_formalization",
                notes=(
                    "Prose pattern detected; same turn contained correlated "
                    f"AskUserQuestion (signals: A=true, B={b_signal}); "
                    "auto-resolved per DCL-OWNER-DECISION-TRACKER-SAME-TURN-"
                    "AUQ-RESOLUTION-001."
                ),
            )
            sections["resolved"].append(entry)
        else:
            entry = DecisionEntry(
                id=new_id,
                asked_at=asked_at,
                asked_in_session=session_hint,
                question=snippet,
                detected_via=f"prose:{name}",
                status="pending",
                question_hash=prose_hash,
                notes="auto-detected prose anti-pattern; review and convert to AskUserQuestion if applicable",
            )
            sections["pending"].append(entry)
        mutated = True

    # 30-day archival: move resolved entries older than HISTORY_AGE_DAYS to history.
    cutoff = datetime.now(UTC) - timedelta(days=HISTORY_AGE_DAYS)
    keep_resolved: list[DecisionEntry] = []
    for entry in sections["resolved"]:
        ts = _parse_iso_timestamp(entry.resolved_at or entry.asked_at)
        if ts is not None and ts < cutoff:
            sections["history"].append(entry)
            mutated = True
        else:
            keep_resolved.append(entry)
    if len(keep_resolved) != len(sections["resolved"]):
        sections["resolved"] = keep_resolved

    if mutated:
        _write_pending_file(pending_path, sections)

    # F3 bounded exception: emit block JSON when the hard condition holds AND
    # the env-var feature flag is enabled. The flag suppresses ONLY this
    # emission — detection (above) and durable-file appends (above) already
    # ran regardless. Only FRESH prose matches are block-eligible: a turn that
    # merely relays already-recorded owner decisions (WI-3332) does not refuse
    # turn-end, even though the relay was still scanned and idempotence-checked.
    if fresh_prose_matches_this_turn and askuserquestion_count == 0 and _block_emission_enabled():
        return _build_block_decision(fresh_prose_matches_this_turn)
    return None


def _extract_answer_text(tool_result: dict[str, Any]) -> str:
    """Pull the user's selected option label(s) out of an AskUserQuestion tool_result."""
    content = tool_result.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "tool_result":
                inner = part.get("content")
                if isinstance(inner, str):
                    return inner.strip()
            if isinstance(part, dict) and part.get("type") == "text":
                return str(part.get("text") or "").strip()
    return ""


def _parse_iso_timestamp(value: str) -> datetime | None:
    """Parse ISO 8601 (with Z or +00:00) into UTC datetime; None on failure."""
    if not value:
        return None
    candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate).astimezone(UTC)
    except ValueError:
        return None


def _session_hint() -> str:
    """Best-effort session ID (S<N>) for asked_in_session field.

    Read from CLAUDE_SESSION_ID env var if set; otherwise empty. The
    field is informational; no logic depends on it being populated.
    """
    return os.environ.get("CLAUDE_SESSION_ID", "")


# ---------------------------------------------------------------------------
# UserPromptSubmit mode
# ---------------------------------------------------------------------------

# Recognized owner shortcuts; precedence: clear > resolve > defer-id > defer-all.
_DEFER_ALL_RE = re.compile(r"^\s*defer all\b", re.IGNORECASE)
_DEFER_ID_RE = re.compile(r"^\s*defer\s+(DECISION-\d+)\b", re.IGNORECASE)
_RESOLVE_RE = re.compile(r"^\s*resolve\s+(DECISION-\d+)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.DOTALL)
_CLEAR_RE = re.compile(r"^\s*clear pending\b", re.IGNORECASE)


def _user_prompt_handler(stdin_text: str) -> str:
    """UserPromptSubmit mode entry point.

    Returns the markdown text to inject as additionalContext (empty
    string means no nudge). Owner shortcuts mutate the durable file and
    return an acknowledgement string.
    """
    try:
        payload = json.loads(stdin_text or "{}")
    except json.JSONDecodeError:
        return ""
    prompt = str(payload.get("prompt") or "")

    pending_path = PROJECT_ROOT / PENDING_FILE_REL
    _ensure_pending_file(pending_path)
    sections = _read_pending_file(pending_path)

    # Shortcut handlers (owner mutating the durable state from chat).
    if _CLEAR_RE.search(prompt):
        moved = len(sections["pending"])
        for entry in sections["pending"]:
            entry.status = "resolved"
            entry.resolved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
            entry.answer = "owner cleared without specific answer"
            sections["resolved"].append(entry)
        sections["pending"] = []
        _write_pending_file(pending_path, sections)
        return f"[owner-decision-tracker] cleared {moved} pending decision(s)."

    m = _RESOLVE_RE.match(prompt)
    if m:
        target_id, answer = m.group(1).upper(), m.group(2).strip()
        for idx, entry in enumerate(sections["pending"]):
            if entry.id.upper() == target_id:
                entry.status = "resolved"
                entry.resolved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
                entry.answer = answer
                sections["resolved"].append(entry)
                del sections["pending"][idx]
                _write_pending_file(pending_path, sections)
                return f"[owner-decision-tracker] resolved {target_id}."
        return f"[owner-decision-tracker] {target_id} not found in pending."

    m = _DEFER_ID_RE.match(prompt)
    if m:
        target_id = m.group(1).upper()
        ts = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        for entry in sections["pending"]:
            if entry.id.upper() == target_id:
                entry.notes = (entry.notes + " " if entry.notes else "") + f"Acknowledged: {ts}"
                _write_pending_file(pending_path, sections)
                return f"[owner-decision-tracker] acknowledged {target_id}; remains pending."
        return f"[owner-decision-tracker] {target_id} not found in pending."

    if _DEFER_ALL_RE.search(prompt):
        ts = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        for entry in sections["pending"]:
            entry.notes = (entry.notes + " " if entry.notes else "") + f"Acknowledged: {ts}"
        _write_pending_file(pending_path, sections)
        return f"[owner-decision-tracker] acknowledged {len(sections['pending'])} pending decision(s); they remain in the queue."

    # No shortcut; emit nudge if pending exist and prompt doesn't reference them.
    if not sections["pending"]:
        return ""
    if _prompt_references_pending(prompt, sections["pending"]):
        return ""
    return _format_nudge(sections["pending"])


def _prompt_references_pending(prompt: str, pending: list[DecisionEntry]) -> bool:
    """Heuristic: does the user's prompt acknowledge any pending decision?

    True if the prompt contains a DECISION-NNNN ID, the substring
    "pending decision", "decision queue", or a high-overlap word match
    against any pending question. Conservative bias: false negatives
    (extra nudges) are cheaper than false positives (suppressed nudges).
    """
    prompt_lower = prompt.lower()
    if "decision-" in prompt_lower:
        return True
    if any(kw in prompt_lower for kw in ("pending decision", "decision queue", "pending owner")):
        return True
    for entry in pending:
        # Word overlap of the question's distinctive tokens.
        tokens = [t for t in re.split(r"\W+", entry.question.lower()) if len(t) > 5]
        hits = sum(1 for t in tokens if t in prompt_lower)
        if tokens and hits >= max(2, len(tokens) // 4):
            return True
    return False


def _format_nudge(pending: list[DecisionEntry]) -> str:
    """Render the UserPromptSubmit nudge.

    Markdown-formatted; the Claude Code hook contract injects this as
    additionalContext, so it is visible to the model on each user turn.
    Limited to top-3 by recency to avoid context bloat; full list is in
    the durable file.
    """
    n = len(pending)
    most_recent = pending[-3:] if n > 3 else pending
    lines = [
        f"### Pending Owner Decisions ({n})",
        "",
        f"{n} owner decision{'s' if n != 1 else ''} await{'s' if n == 1 else ''} a response. "
        "Address one by quoting its DECISION-NNNN ID, type "
        "`resolve DECISION-NNNN: <answer>` to record an answer, "
        "`defer all` to acknowledge without resolving, or "
        "`clear pending` to dismiss intentionally.",
        "",
    ]
    for entry in reversed(most_recent):  # newest first
        opts_blurb = ""
        if entry.options:
            opts = ", ".join(entry.options[:4])
            if len(entry.options) > 4:
                opts += ", ..."
            opts_blurb = f" Options: {opts}."
        lines.append(f"- **{entry.id}**: {entry.question}{opts_blurb}")
    if n > 3:
        lines.append(f"- ... and {n - 3} older pending decision(s) in `{PENDING_FILE_REL}`.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main / mode dispatch
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Hook entry point. Always returns 0 (graceful degradation)."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("stop", "user-prompt-submit"),
        required=True,
        help="Hook event mode dispatcher.",
    )
    args = parser.parse_args(argv)

    try:
        stdin_text = sys.stdin.read()
    except Exception as exc:
        sys.stderr.write(f"owner-decision-tracker: stdin read failed: {exc}\n")
        return 0

    try:
        if args.mode == "stop":
            block_decision = _stop_handler(stdin_text)
            if block_decision is not None:
                # F3 bounded exception per gtkb-decision-tracker-block-prose-ask
                # -2026-04-29-003 REVISED-1: emit one JSON control-flow signal
                # to stdout. Per-turn rate-limited (single emit). Hook control-
                # flow blocks turn termination, agent receives reason text as
                # additionalContext, and on next iteration can call
                # AskUserQuestion to satisfy the requirement.
                sys.stdout.write(json.dumps(block_decision))
                sys.stdout.flush()
        elif args.mode == "user-prompt-submit":
            output = _user_prompt_handler(stdin_text)
            if output:
                sys.stdout.write(output)
    except Exception as exc:
        # Catch-all per T13 graceful-degradation contract; never raise.
        sys.stderr.write(f"owner-decision-tracker: handler {args.mode} raised: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
