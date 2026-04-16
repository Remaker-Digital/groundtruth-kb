#!/usr/bin/env python3
"""
SessionStart hook: governance summary.

Emits a session-start governance summary showing:
- Bridge index status (pending entries, if any)
- Reminder of active governance hooks

Hook type: SessionStart

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BRIDGE_INDEX_FILENAME = "bridge/INDEX.md"


def _parse_bridge_pending(index_path: Path) -> list[str]:
    """Return list of document names with NEW or REVISED latest status."""
    pending: list[str] = []
    if not index_path.exists():
        return pending

    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return pending

    current_doc: str | None = None
    seen_status: bool = False
    for line in lines:
        line = line.strip()
        if line.startswith("Document:"):
            current_doc = line.removeprefix("Document:").strip()
            seen_status = False
        elif current_doc and not seen_status:
            for status in ("VERIFIED", "GO", "NO-GO", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    seen_status = True
                    if status in ("NEW", "REVISED"):
                        pending.append(f"{current_doc} ({status})")
                    break
    return pending


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
            "SessionStart",
            "[Governance] Session governance hook active. Bridge index will be checked at session start.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        payload = {}

    cwd = payload.get("cwd", ".")
    index_path = Path(cwd) / BRIDGE_INDEX_FILENAME
    pending = _parse_bridge_pending(index_path)

    if pending:
        entry_list = "\n  - ".join(pending)
        msg = (
            f"[Governance] Session start: {len(pending)} bridge entry/entries pending Codex review:\n"
            f"  - {entry_list}\n"
            "Check bridge/INDEX.md and process oldest actionable entry first."
        )
    else:
        msg = (
            "[Governance] Session start: bridge index clear. "
            "All governance hooks active (deliberation gate, spec-before-code, bridge compliance, "
            "KB-not-markdown, destructive gate, credential scan)."
        )

    emit_additional_context("SessionStart", msg)
    sys.exit(0)


if __name__ == "__main__":
    main()
