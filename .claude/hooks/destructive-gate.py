#!/usr/bin/env python3
"""
Claude Code PreToolUse hook — Destructive Operation Gate.

Intercepts Bash tool calls before execution and blocks commands that match
destructive patterns (file deletion, git history rewriting, force pushes,
database drops, etc.) unless the command targets a known-safe path.

Also detects potential secret exfiltration patterns (credentials in URLs,
piping secrets to network commands).

Stdin:  JSON {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}
Stdout: JSON {"decision": "block", "reason": "..."} or {}
Exit:   Always 0

This hook is FAIL-CLOSED for recognized destructive patterns — if pattern
matching raises an exception, the command is blocked with an error reason.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import re
import sys


# ---------------------------------------------------------------------------
# Destructive command patterns (compiled for performance)
# ---------------------------------------------------------------------------

# File deletion — Windows and Unix
_DELETE_PATTERNS = [
    re.compile(r'\bdel\s+/[sfq]', re.IGNORECASE),        # del /S, /F, /Q (recursive/force)
    re.compile(r'\bdel\s+"?[^"]*\*', re.IGNORECASE),       # del with wildcards
    re.compile(r'\brmdir\s+/s', re.IGNORECASE),            # rmdir /S (recursive)
    re.compile(r'\brm\s+-r', re.IGNORECASE),               # rm -r, rm -rf, rm -ri
    re.compile(r'\brm\s+--recursive', re.IGNORECASE),
    re.compile(r'\bRemove-Item\b.*-Recurse', re.IGNORECASE),
    # Python recursive-deletion forms (parity with bash forms; per
    # bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-002.md GO).
    # Catches inline `python -c "..."` invocations from the Bash tool.
    re.compile(r'\bshutil\.rmtree\b', re.IGNORECASE),
    re.compile(r'\bos\.removedirs\b', re.IGNORECASE),
    # subprocess wrappers around bash recursive-deletion (e.g.,
    # `subprocess.run(['rm', '-rf', 'x'])`).
    re.compile(r'subprocess\.\w+\([^)]*[\'"]rm[\'"][^)]*[\'"]-r[a-z]*[\'"]', re.IGNORECASE),
    re.compile(r'subprocess\.\w+\([^)]*[\'"]Remove-Item[\'"][^)]*[\'"]-Recurse[\'"]', re.IGNORECASE),
]

# Git destructive operations
_GIT_DESTRUCTIVE = [
    re.compile(r'\bgit\s+push\s+.*--force', re.IGNORECASE),
    re.compile(r'\bgit\s+push\s+-f\b', re.IGNORECASE),
    re.compile(r'\bgit\s+reset\s+--hard', re.IGNORECASE),
    re.compile(r'\bgit\s+clean\s+-[dfx]', re.IGNORECASE),
    re.compile(r'\bgit\s+rm\b', re.IGNORECASE),
    re.compile(r'\bgit\s+checkout\s+--\s+\.', re.IGNORECASE),  # git checkout -- .
    re.compile(r'\bgit\s+restore\s+--staged\s+\.', re.IGNORECASE),
    re.compile(r'\bgit\s+branch\s+-[dD]\b', re.IGNORECASE),
]

# Hook bypass — prevents Claude from skipping pre-commit guardrails
_HOOK_BYPASS = [
    re.compile(r'\bgit\s+commit\b.*--no-verify', re.IGNORECASE),
    re.compile(r'\bgit\s+commit\b.*-n\b', re.IGNORECASE),  # -n is short for --no-verify
    re.compile(r'\bgit\s+push\b.*--no-verify', re.IGNORECASE),
    re.compile(r'\bgit\s+merge\b.*--no-verify', re.IGNORECASE),
]

# Database destructive operations
_DB_DESTRUCTIVE = [
    re.compile(r'\bDROP\s+(TABLE|DATABASE|INDEX|SCHEMA)\b', re.IGNORECASE),
    re.compile(r'\bTRUNCATE\s+TABLE\b', re.IGNORECASE),
    re.compile(r'\bDELETE\s+FROM\b(?!.*WHERE)', re.IGNORECASE),  # DELETE without WHERE
]

# Azure resource destructive operations (S254 hardening)
_AZURE_DESTRUCTIVE = [
    re.compile(r'\baz\s+keyvault\s+key\s+(delete|purge)\b', re.IGNORECASE),
    re.compile(r'\baz\s+keyvault\s+secret\s+(delete|purge)\b', re.IGNORECASE),
    re.compile(r'\baz\s+keyvault\s+delete\b', re.IGNORECASE),
    re.compile(r'\baz\s+containerapp\s+delete\b', re.IGNORECASE),
    re.compile(r'\baz\s+cosmosdb\b.*\bdelete\b', re.IGNORECASE),
    re.compile(r'\baz\s+group\s+delete\b', re.IGNORECASE),
    re.compile(r'\bcontainer\.delete_item\b', re.IGNORECASE),         # Cosmos SDK
    re.compile(r'\bcontainer\.delete_all_items\b', re.IGNORECASE),    # Cosmos SDK
    re.compile(r'\baz\s+role\s+assignment\s+delete\b', re.IGNORECASE),
]

# Production environment targeting (S254 + S270 hardening)
# ANY operation touching production infrastructure requires owner approval.
# This catches accidental production targeting when staging was intended.
_PROD_ENV_PATTERNS = [
    # Python commands writing to production Cosmos (DB_NAME = 'agentred' without '-staging')
    re.compile(r"""DB_NAME\s*=\s*['"]agentred['"](?!-)""", re.IGNORECASE),
    # az CLI targeting production Cosmos database directly
    re.compile(r'\baz\s+cosmosdb\b.*\bagentred\b(?!-staging)', re.IGNORECASE),
    # Production FQDN in any command (API calls, curl, deploy, etc.)
    re.compile(r'agent-red-api-gateway\.orangeglacier', re.IGNORECASE),
    # Production Cosmos database name in Python code
    re.compile(r"""['"]agentred['"](?![-_])"""),
    # Production container app name
    re.compile(r'\bagent-red-api-gateway\b(?!.*staging)', re.IGNORECASE),
    # deploy.py targeting production
    re.compile(r'deploy\.py\b.*--env\s+prod', re.IGNORECASE),
]

# Secret exfiltration patterns
_EXFIL_PATTERNS = [
    re.compile(r'curl\s+.*(-d|--data)\s+.*(["\']?[A-Za-z0-9_]{20,})', re.IGNORECASE),
    re.compile(r'\b(curl|wget|Invoke-WebRequest)\b.*\b(password|secret|key|token)\b', re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Safe-path exceptions (these paths are always OK to delete)
# ---------------------------------------------------------------------------

_SAFE_DELETE_PATHS = [
    re.compile(r'__pycache__', re.IGNORECASE),
    re.compile(r'\.pyc$', re.IGNORECASE),
    re.compile(r'node_modules', re.IGNORECASE),
    re.compile(r'\.pytest_cache', re.IGNORECASE),
    re.compile(r'dist[\\/]', re.IGNORECASE),
    re.compile(r'build[\\/]', re.IGNORECASE),
    re.compile(r'\.egg-info', re.IGNORECASE),
    re.compile(r'storybook-static', re.IGNORECASE),
    re.compile(r'temp_', re.IGNORECASE),
    re.compile(r'\.tmp$', re.IGNORECASE),
]


def _is_safe_path(command: str) -> bool:
    """Check if the delete target is a known-safe path (caches, temp files)."""
    return any(p.search(command) for p in _SAFE_DELETE_PATHS)


def _check_destructive(command: str) -> str | None:
    """
    Returns a block reason if the command matches destructive patterns.
    Returns None if the command is safe to execute.
    """
    # Hook bypass checks (highest priority — prevents guardrail circumvention)
    for pattern in _HOOK_BYPASS:
        if pattern.search(command):
            return (
                f"BLOCKED: Pre-commit hook bypass detected. "
                f"Pattern: {pattern.pattern}. "
                f"Quality guardrails (assertion ratchet, test deletion guard, arch guards, "
                f"TSX gate) cannot be bypassed without owner approval."
            )

    # File deletion checks (with safe-path exception)
    for pattern in _DELETE_PATTERNS:
        if pattern.search(command) and not _is_safe_path(command):
            return (
                f"BLOCKED: Destructive file operation detected. "
                f"Pattern: {pattern.pattern}. "
                f"Ask the owner for approval before deleting files."
            )

    # Git destructive checks (no exceptions)
    for pattern in _GIT_DESTRUCTIVE:
        if pattern.search(command):
            return (
                f"BLOCKED: Destructive git operation detected. "
                f"Pattern: {pattern.pattern}. "
                f"Ask the owner for approval before rewriting history or removing tracked files."
            )

    # Database destructive checks (no exceptions)
    for pattern in _DB_DESTRUCTIVE:
        if pattern.search(command):
            return (
                f"BLOCKED: Destructive database operation detected. "
                f"Pattern: {pattern.pattern}. "
                f"Ask the owner for approval before modifying database schema or bulk-deleting data."
            )

    # Azure resource destructive checks (S254 hardening)
    for pattern in _AZURE_DESTRUCTIVE:
        if pattern.search(command):
            return (
                f"BLOCKED: Destructive Azure operation detected. "
                f"Pattern: {pattern.pattern}. "
                f"Ask the owner for approval before deleting Azure resources, "
                f"Key Vault keys/secrets, or Cosmos DB documents."
            )

    # Production environment targeting checks (S254 hardening)
    for pattern in _PROD_ENV_PATTERNS:
        if pattern.search(command):
            return (
                f"BLOCKED: Production environment targeting detected. "
                f"Pattern: {pattern.pattern}. "
                f"Verify you intend to target production (not staging). "
                f"Ask the owner for approval before running commands against production data."
            )

    # Secret exfiltration checks
    for pattern in _EXFIL_PATTERNS:
        if pattern.search(command):
            return (
                f"BLOCKED: Potential secret exfiltration detected. "
                f"Pattern: {pattern.pattern}. "
                f"Verify this command does not transmit credentials to external services."
            )

    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        # Can't parse input — fail closed (block)
        print(json.dumps({
            "decision": "block",
            "reason": "PreToolUse gate: failed to parse hook input. Blocking as precaution."
        }))
        sys.exit(0)

    tool_name = data.get("tool_name", "")

    # Only gate Bash commands
    if tool_name != "Bash":
        print(json.dumps({}))
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        print(json.dumps({}))
        sys.exit(0)

    try:
        reason = _check_destructive(command)
    except Exception as exc:
        # Pattern matching failed — fail CLOSED
        reason = f"PreToolUse gate: pattern check error ({exc}). Blocking as precaution."

    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    else:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()
