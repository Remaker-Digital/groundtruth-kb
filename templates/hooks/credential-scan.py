#!/usr/bin/env python3
"""
PreToolUse hook: credential pattern scanner.

Detects credential patterns in Bash commands to prevent accidental exposure.
Reads stdin JSON payload and emits structured deny output (exit 0 +
permissionDecision:"deny") when a credential pattern is detected.

Hook type: PreToolUse (tool: Bash)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import re
import sys

CREDENTIAL_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID (AKIA...)"),
    (re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"), "Anthropic API key (sk-ant-api...)"),
    (re.compile(r"\bsk-[a-zA-Z0-9]{20,}"), "Secret key (sk-...)"),
    (re.compile(r"\bsk_live_[a-zA-Z0-9]+"), "Stripe live secret key"),
    (re.compile(r"\bsk_test_[a-zA-Z0-9]+"), "Stripe test secret key"),
    (re.compile(r"\brk_live_[a-zA-Z0-9]+"), "Stripe restricted key"),
    (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"), "Private key block"),
    (re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"), "OpenSSH private key"),
    (re.compile(r"[Cc]onnection[Ss]tring\s*=\s*['\"]?[^\s;]+"), "Connection string assignment"),
    (re.compile(r"AccountKey=[a-zA-Z0-9+/=]{20,}"), "Azure Storage account key"),
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{50,}"), "JWT / bearer token"),
    (re.compile(r"--password\s*[=\s]\s*\S+"), "Password passed as command argument"),
    (re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s"), "Possible password flag (-p)"),
]

OUTPUT_PATTERNS = [
    (
        re.compile(
            r"(echo|printf|cat)\s+.*"
            r"(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey)"
            r".*[>|]",
            re.DOTALL,
        ),
        "Credential value piped or redirected to output",
    ),
    (
        re.compile(r"(export|set)\s+\w*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)\w*\s*=\s*\S+", re.IGNORECASE),
        "Credential exported as environment variable with literal value",
    ),
]

SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "echo sk-ant-api03-aaaaaaaaaaaaaaaa"},
    "session_id": "test",
    "cwd": "/fake",
}


def _check_command(command: str) -> str | None:
    """Return description of first credential pattern found, or None."""
    for pattern, description in CREDENTIAL_PATTERNS:
        if pattern.search(command):
            return description
    for pattern, description in OUTPUT_PATTERNS:
        if pattern.search(command):
            return description
    return None


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_deny, emit_pass
    except ImportError:

        def emit_deny(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
            print(json.dumps(out))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        description = _check_command(SELF_TEST_PAYLOAD["tool_input"]["command"])  # type: ignore[index]
        if description is None:
            print("Self-test error: test payload not detected as credential", file=sys.stderr)
            sys.exit(1)
        emit_deny("PreToolUse", f"Credential pattern blocked by governance gate: {description}")
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    if not command:
        emit_pass()
        sys.exit(0)

    description = _check_command(command)
    if description is not None:
        emit_deny(
            "PreToolUse",
            f"Credential pattern detected by governance gate: {description}. "
            "Use environment variables or secure vaults instead.",
        )
        sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
