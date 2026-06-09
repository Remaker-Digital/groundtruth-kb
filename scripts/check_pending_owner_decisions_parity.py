#!/usr/bin/env python3
"""Surface pending owner decisions in a harness-agnostic way.

Reads memory/pending-owner-decisions.md and prints any pending entries
to stdout in the same shape the .claude/hooks/owner-decision-tracker.py
SessionStart-disclosure section uses. Always exits 0.

Wired into scripts/release_candidate_gate.py so any session running the
release gate (Claude or Codex) sees pending decisions surfaced even when
the Claude hook is not active. Mirrors the established
scripts/check_codex_hook_parity.py forward-compatibility pattern from
ADR-CODEX-HOOK-PARITY-FALLBACK-001.

Authority:
- bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md REVISED §2.7
- bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md GO

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PENDING_FILE = PROJECT_ROOT / "memory" / "pending-owner-decisions.md"


def _extract_pending_block(text: str) -> str:
    """Return the lines under `## Pending` up to the next `## ` heading.

    Handles the simple case sufficient for human-readable surfacing; the
    full parser lives in the hook script. Empty string when the section
    is missing or contains only the literal `(none)` placeholder.
    """
    lines = text.splitlines()
    in_section = False
    captured: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading == "pending":
                in_section = True
                continue
            if in_section:
                break
            continue
        if in_section:
            captured.append(line)
    body = "\n".join(captured).strip()
    if body in ("", "(none)"):
        return ""
    return body


def _summarize_pending(body: str) -> str:
    """Build a compact, human-readable summary of pending entries.

    Pulls the `id:` and `question:` lines out of each bullet block; ignores
    other fields. Keeps the verifier output small enough to fit in the
    release-candidate gate output without bloat.
    """
    entries: list[tuple[str, str]] = []
    current_id = ""
    current_question = ""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id: "):
            if current_id:
                entries.append((current_id, current_question))
            current_id = stripped[len("- id: ") :].strip()
            current_question = ""
        elif stripped.startswith("question: "):
            current_question = _unquote(stripped[len("question: ") :].strip())
    if current_id:
        entries.append((current_id, current_question))

    if not entries:
        return ""
    lines = [f"### Pending Owner Decisions ({len(entries)})", ""]
    for entry_id, question in entries:
        lines.append(f"- **{entry_id}**: {question}")
    return "\n".join(lines)


def _unquote(value: str) -> str:
    """Strip surrounding double quotes from a YAML-flat scalar."""
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def main() -> int:
    """Always returns 0; informational only."""
    if not PENDING_FILE.exists():
        return 0
    try:
        text = PENDING_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"check_pending_owner_decisions_parity: read failed: {exc}\n")
        return 0
    body = _extract_pending_block(text)
    if not body:
        return 0
    summary = _summarize_pending(body)
    if summary:
        print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
