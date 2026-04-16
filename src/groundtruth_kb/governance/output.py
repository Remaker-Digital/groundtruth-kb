# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Canonical hook output builder for GroundTruth governance hooks.

All hooks use this module to emit structured JSON output to stdout.
No hook constructs raw JSON dicts directly.
"""

from __future__ import annotations

import json
from typing import Literal

EventName = Literal["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"]


def emit_additional_context(event: EventName, text: str) -> None:
    """Inject text into Claude's context."""
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


def emit_ask(event: EventName, reason: str) -> None:
    """Pause and ask user whether to proceed, AND inject reason into Claude's context."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
        )
    )


def emit_deny(event: EventName, reason: str) -> None:
    """Hard-block tool execution. Structured path: caller must exit 0 after calling this.

    Claude Code docs define two mutually exclusive blocking mechanisms:
    - Structured path: hookSpecificOutput.permissionDecision="deny" + exit 0
    - Exit-code path: stderr + exit 2 (ignores JSON output)

    This function uses the STRUCTURED PATH. Do NOT exit 2 after calling emit_deny().
    """
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def emit_pass() -> None:
    """Silent pass — no output to Claude's context."""
    print("{}")
