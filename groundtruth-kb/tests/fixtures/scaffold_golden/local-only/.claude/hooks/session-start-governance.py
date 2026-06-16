#!/usr/bin/env python3
"""
SessionStart hook: governance summary.

Emits a session-start governance summary showing:
- Bridge status (pending entries, if any)
- Reminder of active governance hooks

Hook type: SessionStart

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BRIDGE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)


def _parse_bridge_pending(cwd: Path) -> list[str]:
    """Return list of document names with NEW or REVISED latest status."""
    bridge_dir = cwd / "bridge"
    if not bridge_dir.is_dir():
        return []
    latest: dict[str, tuple[int, str]] = {}
    for path in bridge_dir.glob("*.md"):
        match = re.match(r"(?P<doc>.+)-(?P<version>\d{3})\.md$", path.name)
        if not match:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        status = ""
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            status_match = BRIDGE_STATUS_RE.match(stripped)
            status = status_match.group(1).upper() if status_match else ""
            break
        version = int(match.group("version"))
        doc = match.group("doc")
        if status and version > latest.get(doc, (-1, ""))[0]:
            latest[doc] = (version, status)
    return [f"{doc} ({status})" for doc, (_, status) in sorted(latest.items()) if status in ("NEW", "REVISED")]


def _refresh_core_spec_intake(cwd: str) -> None:
    """Best-effort: re-emit the next missing core-spec question into MEMORY.md.

    Cross-session prompt driver (SPEC-CORE-INTAKE-001 / SPEC-CORE-INTAKE-002):
    on each adopter session start, reconcile MEMORY.md to the current intake
    state for the enrolled project (re-emit the next missing slot, or clear the
    block once complete). Fail-safe by construction: any resolution, import, or
    I/O failure is a silent no-op so this hook never breaks a session start.
    Respects the explicit opt-out (DCL-CORE-INTAKE-001).
    """
    try:
        root = Path(cwd)
        db_path = root / "groundtruth.db"
        memory_path = root / "MEMORY.md"
        if not db_path.exists() or not memory_path.exists():
            return

        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.project.core_spec_intake import (
            find_enrolled_project_id,
            intake_enabled,
            refresh_intake_prompt,
        )

        if not intake_enabled(root):
            return
        db = KnowledgeDB(db_path)
        try:
            project_id = find_enrolled_project_id(db)
            if project_id is None:
                return
            refresh_intake_prompt(db, project_id, memory_path)
        finally:
            db.close()
    except Exception:  # intentional-catch: hook must never break session start
        return


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
            "[Governance] Session governance hook active. Canonical bridge state will be checked at session start.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        payload = {}

    cwd = payload.get("cwd", ".")
    _refresh_core_spec_intake(cwd)
    cwd_path = Path(cwd)
    pending = _parse_bridge_pending(cwd_path)

    if pending:
        entry_list = "\n  - ".join(pending)
        msg = (
            f"[Governance] Session start: {len(pending)} bridge entry/entries pending Codex review:\n"
            f"  - {entry_list}\n"
            "Check canonical bridge state and process oldest actionable entry first."
        )
    else:
        msg = (
            "[Governance] Session start: bridge queue clear. "
            "All governance hooks active (deliberation gate, spec-before-code, bridge compliance, "
            "KB-not-markdown, destructive gate, credential scan)."
        )

    emit_additional_context("SessionStart", msg)
    sys.exit(0)


if __name__ == "__main__":
    main()
