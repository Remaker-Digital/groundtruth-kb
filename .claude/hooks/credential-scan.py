#!/usr/bin/env python3
"""
Claude Code PreToolUse hook -- Hardcoded Credential & FQDN Scanner.

Intercepts Write and Edit tool calls and blocks content that contains
hardcoded credentials, API keys, FQDNs, or other environment-specific
values that should be sourced from environment variables.

SPEC-0058: All transient keys, values, URLs, and variables that change
between builds or tenant environments MUST NOT be hardcoded.

Stdin:  JSON {"tool_name": "Write"|"Edit", "tool_input": {...}, ...}
Stdout: JSON {"decision": "block", "reason": "..."} or {}
Exit:   Always 0

This hook is FAIL-OPEN for parse errors (only blocks on positive match).

WI-3142: Replaced blanket test-file exclusions with value-scoped
suppression. Unified key detection covers quoted, assignment-form, and
bare contexts with hyphen-aware character classes and negative-lookahead
boundaries. Reviewed inventory: 52 fixture values, 5 source examples.
Session S281. Codex GO: bridge/credential-scan-narrowing-012.md.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
    re.compile(r'["\']https?://[a-z0-9-]+\.redis\.cache\.windows\.net[^"\']*["\']'),
    re.compile(r'["\']https?://[a-z0-9-]+\.documents\.azure\.com[^"\']*["\']'),
    re.compile(r'["\']https?://[a-z0-9-]+\.vault\.azure\.net[^"\']*["\']'),
]

# ---------------------------------------------------------------------------
# Agent Red API key detection -- unified quoted/unquoted/bare detector
# ---------------------------------------------------------------------------

# Valid key body characters: alphanumeric, underscore, hyphen
# (secrets.token_urlsafe produces base64url which includes hyphens)
_KEY_CHARS = r"[A-Za-z0-9_-]"
# Negative lookahead: next char must NOT be a valid key char
_KEY_BOUNDARY = rf"(?!{_KEY_CHARS})"

# Unified patterns match quoted ("key"), assignment (KEY=key, value: key),
# and bare (key at word boundary) contexts. Named capture extracts the value.
_AR_KEY_PATTERNS = [
    # ar_* family (user, live, spa_plat, spa, tenant, widget)
    re.compile(
        rf'(?:["\':=]|\b)'
        rf"(?P<value>ar_(?:spa_plat|spa|tenant|widget|live|user)_{_KEY_CHARS}{{10,}})"
        rf"{_KEY_BOUNDARY}"
    ),
    # arsk_* family
    re.compile(
        rf'(?:["\':=]|\b)'
        rf"(?P<value>arsk_{_KEY_CHARS}{{10,}})"
        rf"{_KEY_BOUNDARY}"
    ),
    # pk_live_* family
    re.compile(
        rf'(?:["\':=]|\b)'
        rf"(?P<value>pk_live_{_KEY_CHARS}{{10,}})"
        rf"{_KEY_BOUNDARY}"
    ),
]

# Azure subscription/resource IDs (UUIDs in assignment context)
_AZURE_ID_PATTERNS = [
    re.compile(
        r"(?:subscription|client.id|tenant.id|managed.identity)\s*[:=]\s*"
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
# Value-scoped suppression -- approved fixture and example values
# ---------------------------------------------------------------------------

# 52 deterministic test fixture values (Groups A+B+C from reviewed inventory)
# Reviewed S281, Codex GO bridge/credential-scan-narrowing-012.md
_FIXTURE_VALUES = frozenset(
    {
        # Group A: tests/conftest.py (6 values)
        "ar_spa_plat_test_spa_key_001",
        "ar_user_test_user_key_001",
        "arsk_test_ent_key_003",
        "arsk_test_pro_key_002",
        "arsk_test_starter_key_001",
        "pk_live_abcd1234efgh_5678ijkl9012mnop",
        # Group A: tests/multi_tenant/test_middleware_pipeline.py (3, 1 shared)
        "ar_spa_plat_INVALID_STALE_TOKEN",
        "arsk_completely_invalid_key",
        "arsk_test_status_",
        # Group B: 35 other test files (42 unique after dedup)
        "ar_live_abc123def456",
        "ar_live_abc123def456_ghijklm",
        "ar_live_garbage_key_does_not_exist",
        "ar_live_invalid_garbage_key",
        "ar_live_tenant_AbCdEf",
        "ar_live_tenant_AbCdEfGhIjKlMnOpQrStUvWxYz012345",
        "ar_live_test_MYKEY123",
        "ar_live_test_abc123",
        "ar_live_test_abc123def456",
        "ar_live_test_key123",
        "ar_spa_new_key_12345",
        "ar_spa_test1234567890",
        "ar_tenant_removes_all",
        "ar_user_fake_AAAAAAAAAAAAA_BBBBB",
        "ar_user_fake_notadmin",
        "ar_user_new_key_rotated",
        "ar_user_rema_test123",
        "ar_user_t001_TESTKEY",
        "ar_user_test_12345678",
        "ar_user_test_FAKEKEY123456789",
        "ar_user_test_NEWKEY999999999",
        "ar_user_test_abc123",
        "ar_user_test_abc123_secretkey",
        "ar_user_test_key_123456",
        "arsk_fake_nonexistent_key",
        "pk_live_00000000_00000000",
        "pk_live_51abc123XYZ",
        "pk_live_abc123_def456",
        "pk_live_abc123def456",
        "pk_live_abc123def456_ghijklm",
        "pk_live_abcdefghijklmnop",
        "pk_live_invalid_00000000_00000000",
        "pk_live_invalid_key_12345",
        "pk_live_mock_key_12345",
        "pk_live_mock_test_key_for_e2e",
        "pk_live_tenant_aaa",
        "pk_live_tenant_bbb",
        "pk_live_test1234_abcdefgh",
        "pk_live_test123_abc456",
        "pk_live_test_abc123_widgetkey",
        "pk_live_test_placeholder",
        "pk_live_test_widget",
        # Group C: scripts/test_* (1 value)
        "pk_live_invalid_key_00000000",
    }
)

# 5 source code docstring/comment example values (Group D)
_DOCSTRING_EXAMPLE_VALUES = frozenset(
    {
        "ar_live_tn8f3c_AbCdEf",
        "ar_spa_plat_yZR6wMzdVDlVJhbdRPW1Vh01TkytKcQ3",
        "ar_user_rema_yZR6wMzdVDlVJhbdRPW1Vh01TkytKcQ3",
        "pk_live_a7f3c9e1_x8k2m5p9",
        "pk_live_a7f3c9e1b2c3_d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
    }
)

# Paths where fixture values are approved
_FIXTURE_FILE_PATTERNS = [
    re.compile(r"tests[/\\]"),
    re.compile(r"scripts[/\\]test_"),
]

# Paths where docstring example values are approved
_DOCSTRING_EXAMPLE_PATHS = [
    re.compile(r"src[/\\]multi_tenant[/\\]auth\.py$"),
    re.compile(r"src[/\\]multi_tenant[/\\]admin_apikey_api\.py$"),
]


def _is_fixture_suppressed(value: str, file_path: str) -> bool:
    """Return True if this key value is an approved fixture in an approved path."""
    if value in _FIXTURE_VALUES:
        return any(p.search(file_path) for p in _FIXTURE_FILE_PATTERNS)
    if value in _DOCSTRING_EXAMPLE_VALUES:
        return any(p.search(file_path) for p in _DOCSTRING_EXAMPLE_PATHS)
    return False


# ---------------------------------------------------------------------------
# Exclusions -- files where FQDN/conn-string patterns are expected
# (API key detection uses value-scoped suppression instead)
# ---------------------------------------------------------------------------

_EXCLUDED_PATHS = [
    # Memory/documentation files (not deployed code)
    re.compile(r"memory[/\\]"),
    re.compile(r"MEMORY\.md$"),
    re.compile(r"CLAUDE\.md$"),
    re.compile(r"CLAUDE-REFERENCE\.md$"),
    re.compile(r"CLAUDE-ARCHITECTURE\.md$"),
    re.compile(r"CLAUDE_ARCHIVE\.md$"),
    # Hook files themselves
    re.compile(r"\.claude[/\\]hooks[/\\]"),
    # Wiki and docs (reference material)
    re.compile(r"wiki[/\\]"),
    re.compile(r"docs-site[/\\]"),
    # Historical artifacts (reports, logs)
    re.compile(r"container-load-results[/\\]"),
    re.compile(r"\.html$"),
    # Independent assessments (Codex reports)
    re.compile(r"independent-progress-assessments[/\\]"),
    # Environment config files (where env vars are DEFINED)
    re.compile(r"\.env"),
    re.compile(r"\.local$"),
    # Deploy scripts that reference Azure resource names (not FQDNs)
    re.compile(r"deploy[/\\].*\.(ps1|sh)$"),
    # Docker/container config
    re.compile(r"Dockerfile"),
    re.compile(r"docker-compose"),
    # Security penetration tests (intentionally contain fake credentials)
    re.compile(r"tests[/\\]security[/\\]test_live_penetration"),
    # Visual evidence artifacts (must record actual URLs tested)
    re.compile(r"logs[/\\]visual-evidence[/\\]"),
    # Bridge protocol files (proposals/reviews reference key patterns)
    re.compile(r"bridge[/\\]"),
]


def _is_excluded(file_path: str) -> bool:
    """Check if the file path is excluded from scanning."""
    return any(p.search(file_path) for p in _EXCLUDED_PATHS)


def _scan_content(content: str, file_path: str) -> list[str]:
    """Scan content for hardcoded credentials/FQDNs. Returns list of findings."""
    findings = []

    for pattern in _FQDN_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            for match in matches:
                findings.append(f"Hardcoded Azure FQDN: {match[:80]}...")

    for pattern in _AR_KEY_PATTERNS:
        for match in pattern.finditer(content):
            value = match.group("value")
            if not _is_fixture_suppressed(value, file_path):
                findings.append(f"Hardcoded API key ({value[:20]}...)")

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
        # Can't parse -- fail OPEN (don't block on parse error)
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
        findings = _scan_content(content, file_path)
    except Exception:
        # Pattern matching failed -- fail OPEN
        print(json.dumps({}))
        sys.exit(0)

    if findings:
        # Deduplicate findings
        unique_findings = list(dict.fromkeys(findings))
        reason = (
            f"BLOCKED (SPEC-0058): Hardcoded environment-specific values "
            f"detected in {file_path}:\n"
            + "\n".join(f"  - {f}" for f in unique_findings[:5])
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
