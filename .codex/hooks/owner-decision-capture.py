#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project codex`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
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


def _acknowledge_completed_auq(session_id: object) -> None:
    """Clear only the matching startup gate without passing owner content."""
    if not isinstance(session_id, str) or not session_id.strip():
        return
    try:
        project_root = Path(__file__).resolve().parents[2]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from scripts.workstream_focus import acknowledge_startup_owner_input

        acknowledge_startup_owner_input(session_id.strip(), project_root)
    except Exception:
        # PostToolUse is advisory/fail-open; a capture failure cannot block the
        # completed tool result or alter a different session's guard.
        return


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

    session_id = payload.get("session_id", "")
    _acknowledge_completed_auq(session_id)

    content = _extract_auq_content(tool_input, tool_result)
    if not content:
        return 0

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
