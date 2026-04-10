#!/usr/bin/env python3
"""
PreToolUse hook: credential pattern scanner.

Detects credential patterns in Bash commands to prevent accidental exposure.
Reads TOOL_INPUT env var (JSON with "command" key) and exits 2 if the
command contains suspicious credential patterns.

Hook type: PreToolUse (tool: Bash)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import json
import os
import re
import sys

# Credential patterns to detect.
# Each tuple: (compiled regex, human-readable description).
CREDENTIAL_PATTERNS = [
    # AWS access keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID (AKIA...)"),
    # Generic secret key prefixes
    (re.compile(r"\bsk-[a-zA-Z0-9]{20,}"), "Secret key (sk-...)"),
    (re.compile(r"\bsk_live_[a-zA-Z0-9]+"), "Stripe live secret key"),
    (re.compile(r"\bsk_test_[a-zA-Z0-9]+"), "Stripe test secret key"),
    (re.compile(r"\brk_live_[a-zA-Z0-9]+"), "Stripe restricted key"),
    # Private key markers
    (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"), "Private key block"),
    (re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"), "OpenSSH private key"),
    # Connection strings
    (
        re.compile(r"[Cc]onnection[Ss]tring\s*=\s*['\"]?[^\s;]+"),
        "Connection string assignment",
    ),
    (
        re.compile(r"AccountKey=[a-zA-Z0-9+/=]{20,}"),
        "Azure Storage account key",
    ),
    # Azure / cloud tokens
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{50,}"), "JWT / bearer token"),
    # Generic password in command
    (
        re.compile(r"--password\s*[=\s]\s*\S+"),
        "Password passed as command argument",
    ),
    (
        re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s"),
        "Possible password flag (-p)",
    ),
]

# Patterns indicating credential output to files or pipes.
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


def main():
    tool_input_raw = os.environ.get("TOOL_INPUT", "")
    if not tool_input_raw:
        sys.exit(0)

    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    # Check for credential patterns in the command.
    for pattern, description in CREDENTIAL_PATTERNS:
        if pattern.search(command):
            print(
                f"Hook PreToolUse:Bash denied this tool\n"
                f"Detected credential pattern: {description}\n"
                f"Commands containing credentials must not be executed.\n"
                f"Use environment variables or secure vaults instead."
            )
            sys.exit(2)

    # Check for credential output/redirection patterns.
    for pattern, description in OUTPUT_PATTERNS:
        if pattern.search(command):
            print(
                f"Hook PreToolUse:Bash denied this tool\n"
                f"Detected credential exposure risk: {description}\n"
                f"Do not pipe, redirect, or echo credential values.\n"
                f"Use environment variables or secure vaults instead."
            )
            sys.exit(2)

    # No credential patterns detected.
    sys.exit(0)


if __name__ == "__main__":
    main()
