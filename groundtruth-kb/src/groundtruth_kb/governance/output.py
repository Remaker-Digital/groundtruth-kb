# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Canonical hook output builder for GroundTruth governance hooks.

All hooks use this module to emit structured JSON output to stdout.
No hook constructs raw JSON dicts directly.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
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


def emit_effect_gate_result(result: Mapping[str, object], *, diagnostic: bool = False) -> None:
    """Emit the effect checker's existing diagnostic, deny or allow JSON protocol."""
    if diagnostic:
        print(
            json.dumps(
                {
                    "decision": result.get("decision", "allow"),
                    "diagnostic": True,
                    "reason": result.get("reason", ""),
                    "would_block": result.get("decision") == "block",
                },
                sort_keys=True,
            )
        )
        return
    if result.get("decision") == "block":
        reason = result.get("reason") or "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)"
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                        "additionalContext": reason,
                    }
                },
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(result, sort_keys=True))
