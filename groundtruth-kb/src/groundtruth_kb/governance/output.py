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


def _coded_reason(result: Mapping[str, object]) -> str:
    """The block's reason led by its reason code, once (c123; batch design WP1, B148).

    The code used to stay inside the process: hosts saw the text alone. A reason that already starts with
    "<code>:" is not prefixed again.
    """
    reason = str(result.get("reason") or "")
    code = result.get("reason_code")
    if isinstance(code, str) and code and reason and not reason.startswith(f"{code}:"):
        return f"{code}: {reason}"
    return reason


def emit_effect_gate_result(result: Mapping[str, object], *, diagnostic: bool = False) -> None:
    """Emit the effect checker's existing diagnostic, deny or allow JSON protocol."""
    if diagnostic:
        report: dict[str, object] = {
            "decision": result.get("decision", "allow"),
            "diagnostic": True,
            "reason": result.get("reason", ""),
            "would_block": result.get("decision") == "block",
        }
        # c123 (B148): a result that carries a code shows it; a code-less result keeps its exact bytes.
        code = result.get("reason_code")
        if isinstance(code, str) and code:
            report["reason_code"] = code
        print(json.dumps(report, sort_keys=True))
        return
    if result.get("decision") == "block":
        reason = _coded_reason(result) or "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)"
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
