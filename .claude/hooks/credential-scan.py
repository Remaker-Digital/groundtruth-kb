#!/usr/bin/env python3
"""
Claude Code PreToolUse hook â€” Hardcoded Credential & FQDN Scanner.

Intercepts Write and Edit tool calls and blocks content that contains
hardcoded credentials, API keys, FQDNs, or other environment-specific
values that should be sourced from environment variables.

SPEC-0058: All transient keys, values, URLs, and variables that change
between builds or tenant environments MUST NOT be hardcoded.

Stdin:  JSON {"tool_name": "Write"|"Edit", "tool_input": {...}, ...}
Stdout: JSON {"decision": "block", "reason": "..."} or {}
Exit:   Always 0

This hook is FAIL-OPEN for parse errors (only blocks on positive match).

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import re
import sys


# ---------------------------------------------------------------------------
# Patterns that indicate hardcoded environment-specific values
# ---------------------------------------------------------------------------

# Azure Container Apps FQDNs (the most common violation)
_FQDN_PATTERNS = [
    re.compile(
        r'["\']https?://agent-red-[a-z0-9-]+\.'
        r'[a-z0-9-]+\.[a-z0-9]+\.azurecontainerapps\.io[^"\']*["\']'
    ),
    re.compile(
        r'["\']https?://[a-z0-9-]+\.redis\.cache\.windows\.net[^"\']*["\']'
    ),
    re.compile(
        r'["\']https?://[a-z0-9-]+\.documents\.azure\.com[^"\']*["\']'
    ),
    re.compile(
        r'["\']https?://[a-z0-9-]+\.vault\.azure\.net[^"\']*["\']'
    ),
]

# API key patterns (ar_spa_, ar_tenant_, ar_widget_ prefixes)
_API_KEY_PATTERNS = [
    re.compile(r'["\']ar_(spa|tenant|widget)_[A-Za-z0-9]{16,}["\']'),
    re.compile(r'["\']ar_spa_plat_[A-Za-z0-9]{16,}["\']'),
]

# Azure subscription/resource IDs (UUIDs in assignment context)
_AZURE_ID_PATTERNS = [
    re.compile(
        r'(?:subscription|client.id|tenant.id|managed.identity)\s*[:=]\s*'
        r'["\'][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}["\']',
        re.IGNORECASE,
    ),
]

# Connection strings
_CONN_STRING_PATTERNS = [
    re.compile(r'["\']AccountEndpoint=https://[^"\']+;AccountKey=[^"\']+["\']'),
    re.compile(r'["\']DefaultEndpointsProtocol=https;[^"\']+["\']'),
    re.compile(r'["\']Server=tcp:[^"\']+\.database\.windows\.net[^"\']*["\']'),
]


# ---------------------------------------------------------------------------
# Exclusions â€” files where these patterns are expected
# ---------------------------------------------------------------------------

_EXCLUDED_PATHS = [
    # Memory/documentation files (not deployed code)
    re.compile(r'memory[/\\]'),
    re.compile(r'MEMORY\.md$'),
    re.compile(r'CLAUDE\.md$'),
    re.compile(r'CLAUDE-REFERENCE\.md$'),
    re.compile(r'CLAUDE-ARCHITECTURE\.md$'),
    re.compile(r'CLAUDE_ARCHIVE\.md$'),
    # Hook files themselves
    re.compile(r'\.claude[/\\]hooks[/\\]'),
    # Wiki and docs (reference material)
    re.compile(r'wiki[/\\]'),
    re.compile(r'docs-site[/\\]'),
    # Historical artifacts (reports, logs)
    re.compile(r'container-load-results[/\\]'),
    re.compile(r'\.html$'),
    # Independent assessments (Codex reports)
    re.compile(r'independent-progress-assessments[/\\]'),
    # Environment config files (where env vars are DEFINED)
    re.compile(r'\.env'),
    re.compile(r'\.local$'),
    # Deploy scripts that reference Azure resource names (not FQDNs)
    re.compile(r'deploy[/\\].*\.(ps1|sh)$'),
    # Docker/container config
    re.compile(r'Dockerfile'),
    re.compile(r'docker-compose'),
    # Security penetration tests (intentionally contain fake credentials)
    re.compile(r'tests[/\\]security[/\\]test_live_penetration'),
]


def _is_excluded(file_path: str) -> bool:
    """Check if the file path is excluded from scanning."""
    return any(p.search(file_path) for p in _EXCLUDED_PATHS)


def _scan_content(content: str) -> list[str]:
    """Scan content for hardcoded credentials/FQDNs. Returns list of findings."""
    findings = []

    for pattern in _FQDN_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            # Don't flag if it's inside a comment explaining the pattern
            for match in matches:
                findings.append(f"Hardcoded Azure FQDN: {match[:80]}...")

    for pattern in _API_KEY_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            findings.append("Hardcoded API key (ar_* prefix)")

    for pattern in _AZURE_ID_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            findings.append("Hardcoded Azure resource ID")

    for pattern in _CONN_STRING_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            findings.append("Hardcoded connection string")

    return findings


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        # Can't parse â€” fail OPEN (don't block on parse error)
        print(json.dumps({}))
        sys.exit(0)

    tool_name = data.get("tool_name", "")

    # Only scan Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({}))
        sys.exit(0)

    tool_input = data.get("tool_input", {})

    # Get the file path
    file_path = tool_input.get("file_path", "")
    if not file_path or _is_excluded(file_path):
        print(json.dumps({}))
        sys.exit(0)

    # Get content to scan
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")
    else:
        content = ""

    if not content:
        print(json.dumps({}))
        sys.exit(0)

    try:
        findings = _scan_content(content)
    except Exception:
        # Pattern matching failed â€” fail OPEN
        print(json.dumps({}))
        sys.exit(0)

    if findings:
        reason = (
            f"BLOCKED (SPEC-0058): Hardcoded environment-specific values detected "
            f"in {file_path}:\n"
            + "\n".join(f"  â€¢ {f}" for f in findings[:5])
            + "\n\nAll FQDNs, API keys, connection strings, and resource IDs "
            "MUST come from environment variables. "
            "Use os.environ.get() or equivalent."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
    else:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()

