#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Owner decision auto-capture (PostToolUse).

When a PostToolUse hook fires for an AskUserQuestion result, automatically
archives the owner decision as a Deliberation Archive row with
``source_type=owner_conversation`` and ``outcome=owner_decision``.

Fail-open: any error silently exits 0 so the hook never blocks agent work.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Sibling helper — shared DA insertion logic.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _delib_common import insert_deliberation  # noqa: E402


def _extract_auq_content(tool_input: dict, tool_result: dict) -> str | None:
    """Build a human-readable summary of an AskUserQuestion exchange."""
    questions = tool_input.get("questions", [])
    answers = tool_result.get("answers", {})
    if not questions and not answers:
        return None

    parts: list[str] = []
    for q in questions:
        q_text = q.get("question", "")
        if q_text:
            parts.append(f"Q: {q_text}")
    for key, val in answers.items():
        parts.append(f"A [{key}]: {val}")

    return "\n".join(parts) if parts else None


def main() -> int:
    """Hook entry point."""
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "AskUserQuestion":
        return 0

    tool_input = payload.get("tool_input", {})
    tool_result = payload.get("tool_result", {})
    if not tool_result:
        return 0

    content = _extract_auq_content(tool_input, tool_result)
    if not content:
        return 0

    session_id = payload.get("session_id", "")
    insert_deliberation(
        source_type="owner_conversation",
        content=content,
        outcome="owner_decision",
        session_id=session_id,
        source_ref=f"hook/owner-decision-capture/{tool_name}",
    )

    # Always pass — fail-open.
    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
