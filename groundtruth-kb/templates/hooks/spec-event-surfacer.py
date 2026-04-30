#!/usr/bin/env python3
"""
PostToolUse hook: spec/intake event surfacer.

Watches ``groundtruth.db`` for new spec rows since session start and emits
chat-visible event lines so the owner can observe spec creation/update
activity in real time without polling the dashboard or querying the DB.

Per-session ledger at ``.claude/session/spec-events-seen.jsonl`` prevents
duplicate emission across multiple PostToolUse invocations within the same
session. Atomic-rename writes prevent partial-state corruption under
concurrent invocations.

Implements bridge ``gtkb-membase-effective-use-recovery-slice-a-event-
surfacer-2026-04-29`` GO at ``-006``. Serves ``SPEC-INTAKE-2485e9``
("Surface spec creation/update events in owner chat view").

Read-only against ``groundtruth.db``: the hook NEVER executes
INSERT/UPDATE/DELETE SQL. Per acceptance criterion 7 from the GO'd
proposal.

Hook type: PostToolUse

Stdin: JSON hook event payload per https://code.claude.com/docs/en/hooks
Stdout: JSON ``additionalContext`` block when new spec events are detected,
        else empty ``{}``.
Exit:   Always 0 (graceful degradation; never blocks the agent).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Per-session ledger location. New session implies fresh ledger; the hook
# initializes the file lazily on first invocation if absent.
LEDGER_REL_PATH = ".claude/session/spec-events-seen.jsonl"

# Session-start timestamp source written by the SessionStart hook.
SESSION_START_REL_PATH = ".claude/session/session-start.json"

# Conservative fallback window when session-start file is missing/malformed.
# 1 hour balances "don't miss in-session writes" against "don't surface
# stale historical rows on a fresh session". Per F2 fix in REVISED-1
# (NOT current_time, which would silently suppress already-created rows).
FALLBACK_LOOKBACK = timedelta(hours=1)

# Database location relative to project root.
DB_REL_PATH = "groundtruth.db"

# Per-event emission format. Plain-text marker (not emoji) for grep-ability.
EVENT_FORMAT = (
    "[KB-SPEC-EVENT] {spec_id} v{version} -- {kind} -- {title} "
    "[type={type} status={status} section={section}]"
)


def _resolve_session_started_at(cwd: Path) -> tuple[str, bool]:
    """Return (ISO8601 lower-bound timestamp, used_fallback flag).

    Primary source: ``.claude/session/session-start.json`` (written by the
    existing SessionStart hook in ``scripts/session_self_initialization.py``
    per slice A REVISED-2 §1.3).

    Fallback (file missing or malformed): ``datetime.now(UTC) -
    FALLBACK_LOOKBACK``. NOT current_time per Codex F2 fix from
    NO-GO ``-002``.
    """
    session_start_path = cwd / SESSION_START_REL_PATH
    if session_start_path.exists():
        try:
            data = json.loads(session_start_path.read_text(encoding="utf-8"))
            ts = data.get("session_started_at")
            if isinstance(ts, str) and ts:
                return ts, False
        except (json.JSONDecodeError, OSError):
            pass
    fallback_ts = (datetime.now(UTC) - FALLBACK_LOOKBACK).isoformat(timespec="microseconds")
    return fallback_ts, True


def _load_ledger(cwd: Path) -> set[tuple[str, int]]:
    """Load the per-session ledger as a set of ``(spec_id, version)`` tuples."""
    ledger_path = cwd / LEDGER_REL_PATH
    if not ledger_path.exists():
        return set()
    seen: set[tuple[str, int]] = set()
    try:
        with ledger_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                spec_id = entry.get("spec_id")
                version = entry.get("version")
                if isinstance(spec_id, str) and isinstance(version, int):
                    seen.add((spec_id, version))
    except OSError:
        pass
    return seen


def _query_new_spec_rows(
    cwd: Path,
    session_started_at: str,
    seen: set[tuple[str, int]],
) -> list[dict[str, Any]]:
    """Query ``current_specifications`` for rows with ``changed_at >= session_started_at``
    that are not already in the per-session ledger.

    Returns a list of dicts with keys: ``id``, ``version``, ``title``, ``type``,
    ``status``, ``section``, ``changed_at``. Sorted by ``changed_at`` ascending.

    The query is READ-ONLY (SELECT only). Per acceptance criterion 7 from the
    GO'd proposal: zero INSERT/UPDATE/DELETE SQL.
    """
    db_path = cwd / DB_REL_PATH
    if not db_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        # Open in read-only mode via URI (mode=ro) to enforce the contract.
        uri = f"file:{db_path}?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=2.0) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT id, version, title, type, status, section, changed_at
                FROM current_specifications
                WHERE changed_at >= ?
                ORDER BY changed_at ASC
                """,
                (session_started_at,),
            )
            for row in cur.fetchall():
                key = (row["id"], int(row["version"]))
                if key in seen:
                    continue
                rows.append(
                    {
                        "id": row["id"],
                        "version": int(row["version"]),
                        "title": row["title"] or "",
                        "type": row["type"] or "",
                        "status": row["status"] or "",
                        "section": row["section"] or "",
                        "changed_at": row["changed_at"] or "",
                    }
                )
    except sqlite3.Error:
        # Database may be locked, missing, or schema-incompatible during
        # migration. Graceful degradation: surface no events this turn.
        return []
    return rows


def _format_event_line(row: dict[str, Any]) -> str:
    """Render one spec row as a chat-visible event line."""
    kind = "created" if int(row.get("version", 1)) == 1 else "updated"
    return EVENT_FORMAT.format(
        spec_id=row.get("id", ""),
        version=row.get("version", ""),
        kind=kind,
        title=str(row.get("title", "")),
        type=str(row.get("type", "")),
        status=str(row.get("status", "")),
        section=str(row.get("section", "")),
    )


def _append_to_ledger(cwd: Path, rows: list[dict[str, Any]]) -> None:
    """Atomically append new ledger entries.

    Uses a tmp-file plus ``os.replace`` pattern: read the existing ledger,
    concatenate the new entries, write to ``<ledger>.tmp.<pid>``, then rename
    onto the ledger path. Atomic at the filesystem level; safe under concurrent
    PostToolUse invocations.
    """
    if not rows:
        return
    ledger_path = cwd / LEDGER_REL_PATH
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if ledger_path.exists():
        try:
            existing = ledger_path.read_text(encoding="utf-8")
            if existing and not existing.endswith("\n"):
                existing += "\n"
        except OSError:
            existing = ""
    seen_at = datetime.now(UTC).isoformat(timespec="microseconds")
    new_lines = []
    for row in rows:
        kind = "created" if int(row.get("version", 1)) == 1 else "updated"
        new_lines.append(
            json.dumps(
                {
                    "spec_id": row.get("id"),
                    "version": int(row.get("version", 0)),
                    "seen_at": seen_at,
                    "kind": kind,
                }
            )
        )
    new_text = existing + "\n".join(new_lines) + "\n"
    tmp_path = ledger_path.with_name(f"{ledger_path.name}.tmp.{os.getpid()}")
    try:
        tmp_path.write_text(new_text, encoding="utf-8")
        os.replace(tmp_path, ledger_path)
    except OSError:
        # Best-effort cleanup of tmp file on any error.
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass


def _build_event_message(rows: list[dict[str, Any]], used_fallback: bool) -> str:
    """Format the additionalContext message for the owner chat view."""
    lines = [_format_event_line(row) for row in rows]
    body = "\n".join(lines)
    if used_fallback:
        return (
            "[KB-SPEC-EVENT] WARN: session-start.json missing or malformed; "
            "using conservative 1-hour lookback. Some events may be from a "
            "prior session.\n" + body
        )
    return body


def main() -> None:
    """Hook entrypoint."""
    try:
        from groundtruth_kb.governance.output import emit_additional_context, emit_pass
    except ImportError:

        def emit_additional_context(event: str, text: str) -> None:  # type: ignore[misc]
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": event,
                            "additionalContext": text,
                        }
                    }
                )
            )

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

    cwd_str = payload.get("cwd", ".")
    cwd = Path(cwd_str).resolve()

    # Resolve lower-bound timestamp + load ledger
    session_started_at, used_fallback = _resolve_session_started_at(cwd)
    seen = _load_ledger(cwd)

    # Query new spec rows
    new_rows = _query_new_spec_rows(cwd, session_started_at, seen)

    if not new_rows:
        emit_pass()
        sys.exit(0)

    # Append to ledger BEFORE emit so a crash mid-emit doesn't cause
    # re-emission on the next invocation.
    _append_to_ledger(cwd, new_rows)

    # Emit chat-visible event message
    message = _build_event_message(new_rows, used_fallback)
    emit_additional_context("PostToolUse", message)
    sys.exit(0)


if __name__ == "__main__":
    main()
