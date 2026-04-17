#!/usr/bin/env python3
"""
PreToolUse hook: scanner-safe-writer.

Intercepts Write tool invocations whose target ``file_path`` resolves to a
file directly under a ``bridge/`` directory (e.g. ``bridge/foo-001.md``) and
scans the proposed ``content`` against the canonical credential catalog.
When any canonical credential-class regex matches, the hook emits a
``permissionDecision=deny`` via the structured path and records a
deny record to ``.claude/hooks/scanner-safe-writer.log`` for the metrics
collector (Tier A #6).

Scope
-----
- **In scope:** ``Write`` tool events whose ``file_path`` matches
  ``bridge/<single-segment>.md`` anywhere in the path, case-insensitively.
- **Out of scope:** non-Write tools (Bash, Edit, etc. — scanned by other
  hooks), files nested more than one level under ``bridge/``, non-``.md``
  files in ``bridge/``, and paths like ``bridgelike/`` that only start with
  the substring.
- **Policy:** credential-class only. PII patterns (phone, email, ipv4) are
  intentionally excluded so operators may reference redacted samples in
  bridge proposals without triggering denials.

Hook type: PreToolUse (tool: Write)

Catalog sourcing
----------------
The pattern catalog is sourced from
``groundtruth_kb.governance.credential_patterns`` (``CREDENTIAL_PATTERNS`` +
``BASH_EXTRAS``, excluding ``PII_PATTERNS``) when the canonical package is
importable. When the hook runs in a standalone environment that cannot
import ``groundtruth_kb`` (for example an isolated adopter project whose
Python interpreter does not have the GT-KB wheel installed), the hook falls
back to the inline catalog defined below. The inline catalog is kept in sync
with the canonical module by the
``test_scanner_safe_writer_fallback_exact_canonical_mirror`` parity test in
``tests/test_scanner_safe_writer.py`` — drift fails the build.

On every run the hook writes one of two markers to stderr so tests and
operators can tell which catalog was used:

- ``CANONICAL_CATALOG_USED`` when the canonical import succeeded.
- ``FALLBACK_CATALOG_USED`` when the inline fallback catalog was used.

Deny record schema (version 1)
------------------------------
When a write is denied the hook appends a single-line JSON record to
``.claude/hooks/scanner-safe-writer.log``. Fields (``schema_version`` first):

- ``schema_version`` (int, always ``1``)
- ``timestamp_utc`` (ISO-8601 UTC ``Z``)
- ``hook`` (string, always ``"scanner-safe-writer"``)
- ``event`` (string, always ``"deny"``)
- ``file_path`` (string — the target path that was blocked)
- ``catalog_source`` (string, ``"canonical"`` or ``"fallback"``)
- ``hits`` (list of ``{"pattern_name": str, "pattern_description": str, "span": [int,int]}``)
- ``session_id`` (string or ``null``)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

try:
    from groundtruth_kb.governance.credential_patterns import (
        BASH_EXTRAS,
        CREDENTIAL_PATTERNS,
    )

    _CATALOG: list[tuple[re.Pattern[str], str, str]] = [
        (spec.pattern, spec.name, spec.description) for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
    ]
    _catalog_source = "canonical"
    print("CANONICAL_CATALOG_USED", file=sys.stderr)
except ImportError:
    # Inline standalone fallback.
    #
    # Kept in sync with
    # ``CREDENTIAL_PATTERNS + BASH_EXTRAS`` (excluding ``PII_PATTERNS``)
    # from ``groundtruth_kb.governance.credential_patterns`` via
    # ``test_scanner_safe_writer_fallback_exact_canonical_mirror`` in
    # ``tests/test_scanner_safe_writer.py``. Drift fails the build.
    _CATALOG = [
        # DB scope — credential entries (15)
        (
            re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w\-]{16,}['\"]?", re.IGNORECASE),
            "api_key",
            "Generic api_key/apikey assignment",
        ),
        (
            re.compile(r"(?:Authorization\s*:\s*)?Bearer\s+[\w\-\.~+/]+=*", re.IGNORECASE),
            "bearer_header",
            "Authorization: Bearer <token> or standalone Bearer <token>",
        ),
        (
            re.compile(r"(?:token|bearer)\s*[:=]\s*['\"]?[\w\-\.]{20,}['\"]?", re.IGNORECASE),
            "token",
            "token=/token: or bearer=/bearer: explicit assignment",
        ),
        (
            re.compile(r"(?:secret|password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?", re.IGNORECASE),
            "secret",
            "secret/password/passwd assignment",
        ),
        (
            re.compile(r"(?:mongodb|postgres|mysql|redis|amqp)://[^\s\"']+", re.IGNORECASE),
            "connection_string",
            "Database connection string URI",
        ),
        (
            re.compile(r"SharedAccessKey=[A-Za-z0-9+/=]{20,}(?:;|$)", re.IGNORECASE),
            "azure_sas_key",
            "Azure SharedAccessKey connection-string segment",
        ),
        (
            re.compile(r"(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
            "github_pat",
            "GitHub personal-access-token prefixes",
        ),
        (
            re.compile(r"(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", re.IGNORECASE),
            "service_key",
            "Generic sk_/pk_ live/test/prod service key",
        ),
        (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_key", "AWS access key ID (AKIA...)"),
        (
            re.compile(r"\bar_live_[A-Za-z0-9_-]{10,}"),
            "ar_live_key",
            "Tenant-scoped live key (ar_live_...)",
        ),
        (
            re.compile(r"\bar_user_[A-Za-z0-9_-]{10,}"),
            "ar_user_key",
            "User API key (ar_user_...)",
        ),
        (
            re.compile(r"\bar_spa_plat_[A-Za-z0-9_-]{10,}"),
            "ar_spa_plat_key",
            "SPA platform key (ar_spa_plat_...)",
        ),
        (
            re.compile(r"\bpk_live_[A-Za-z0-9_-]{10,}"),
            "pk_live_key",
            "Public live widget key (pk_live_...)",
        ),
        (
            re.compile(r"\barsk_[A-Za-z0-9_-]{10,}"),
            "arsk_key",
            "Service key (arsk_...)",
        ),
        (
            re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}"),
            "anthropic_api_key",
            "Anthropic API key (sk-ant-api<version>-<token>)",
        ),
        # Bash credential scope (13)
        (re.compile(r"AKIA[0-9A-Z]{16}"), "bash_aws_key", "AWS access key ID (AKIA...)"),
        (
            re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"),
            "bash_anthropic_api_key",
            "Anthropic API key (sk-ant-api...)",
        ),
        (re.compile(r"\bsk-[a-zA-Z0-9]{20,}"), "bash_secret_key", "Secret key (sk-...)"),
        (re.compile(r"\bsk_live_[a-zA-Z0-9]+"), "bash_stripe_live", "Stripe live secret key"),
        (re.compile(r"\bsk_test_[a-zA-Z0-9]+"), "bash_stripe_test", "Stripe test secret key"),
        (re.compile(r"\brk_live_[a-zA-Z0-9]+"), "bash_stripe_restricted", "Stripe restricted key"),
        (
            re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
            "bash_private_key_block",
            "Private key block",
        ),
        (
            re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"),
            "bash_openssh_private_key",
            "OpenSSH private key",
        ),
        (
            re.compile(r"[Cc]onnection[Ss]tring\s*=\s*['\"]?[^\s;]+"),
            "bash_connection_string",
            "Connection string assignment",
        ),
        (
            re.compile(r"AccountKey=[a-zA-Z0-9+/=]{20,}"),
            "bash_azure_account_key",
            "Azure Storage account key",
        ),
        (re.compile(r"\beyJ[a-zA-Z0-9_-]{50,}"), "bash_jwt_token", "JWT / bearer token"),
        (
            re.compile(r"--password\s*[=\s]\s*\S+"),
            "bash_password_arg",
            "Password passed as command argument",
        ),
        (
            re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s"),
            "bash_password_flag_p",
            "Possible password flag (-p)",
        ),
        # Bash output scope (2)
        (
            re.compile(
                r"(echo|printf|cat)\s+.*"
                r"(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey)"
                r".*[>|]",
                re.DOTALL,
            ),
            "bash_credential_piped_output",
            "Credential value piped or redirected to output",
        ),
        (
            re.compile(
                r"(export|set)\s+\w*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)\w*\s*=\s*\S+",
                re.IGNORECASE,
            ),
            "bash_credential_exported_env_var",
            "Credential exported as environment variable with literal value",
        ),
    ]
    _catalog_source = "fallback"
    print("FALLBACK_CATALOG_USED", file=sys.stderr)


# Case-insensitive direct-bridge file detector. Matches exactly one segment
# below a ``bridge`` directory with a ``.md`` suffix. Nested paths like
# ``bridge/sub/foo.md`` are deliberately not matched (the proposal scopes
# enforcement to direct bridge artifacts).
BRIDGE_PATH_PATTERN = re.compile(
    r"(^|[/\\])bridge[/\\][^/\\]+\.md$",
    re.IGNORECASE,
)

DENY_LOG_PATH = Path(".claude/hooks/scanner-safe-writer.log")
SCHEMA_VERSION = 1


def _is_in_scope(file_path: str) -> bool:
    """Return True when ``file_path`` resolves to a direct ``bridge/*.md`` file.

    Handles both POSIX and Windows separators, absolute and relative paths.
    The case-insensitive regex rejects ``bridgelike/foo.md`` (which only starts
    with the substring) and ``bridge/sub/foo.md`` (nested below the bridge
    directory).
    """
    if not file_path:
        return False
    return BRIDGE_PATH_PATTERN.search(file_path) is not None


def _scan_content(content: str) -> list[tuple[str, str, tuple[int, int]]]:
    """Return first-match hits ordered by catalog position.

    For each catalog entry, returns the first span that matches (or skip if
    no match). This preserves the first-match ordering specified in the
    proposal — a sample that matches multiple specs surfaces every matching
    spec in catalog order, with the earliest catalog-order match first.

    Returns a list of ``(pattern_name, pattern_description, (start, end))``
    tuples. An empty list means the content is clean.
    """
    hits: list[tuple[str, str, tuple[int, int]]] = []
    for pattern, name, description in _CATALOG:
        m = pattern.search(content)
        if m is not None:
            hits.append((name, description, (m.start(), m.end())))
    return hits


def _write_deny_record(
    file_path: str,
    hits: list[tuple[str, str, tuple[int, int]]],
    session_id: str | None,
) -> None:
    """Append a single-line JSON deny record to the deny log.

    Best-effort: if the log cannot be written (permission error, disk full,
    etc.) the hook still returns the structured deny output — logging
    failure must not convert a deny into a pass.
    """
    record = {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": datetime.datetime.now(tz=datetime.UTC).isoformat().replace("+00:00", "Z"),
        "hook": "scanner-safe-writer",
        "event": "deny",
        "file_path": file_path,
        "catalog_source": _catalog_source,
        "hits": [
            {
                "pattern_name": name,
                "pattern_description": description,
                "span": [span[0], span[1]],
            }
            for name, description, span in hits
        ],
        "session_id": session_id,
    }
    try:
        DENY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DENY_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        # Logging failure must not convert a deny into a pass. The structured
        # deny output is still emitted by the caller.
        pass


SELF_TEST_FILE_PATH = "bridge/self-test-001.md"
SELF_TEST_CONTENT = "Example payload with an " + "AK" + "IA" + "ABCDEFGHIJKLMNOP key."


def _self_test() -> None:
    """Run the built-in self-test and emit a deny record then exit 0."""
    # Parity with credential-scan.py: lazy-import emit_deny so self-test works
    # even when groundtruth_kb isn't available on sys.path.
    try:
        from groundtruth_kb.governance.output import emit_deny
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

    if not _is_in_scope(SELF_TEST_FILE_PATH):
        print("Self-test error: SELF_TEST_FILE_PATH not in scope", file=sys.stderr)
        sys.exit(1)
    hits = _scan_content(SELF_TEST_CONTENT)
    if not hits:
        print(
            "Self-test error: SELF_TEST_CONTENT did not match any catalog entry",
            file=sys.stderr,
        )
        sys.exit(1)
    _write_deny_record(SELF_TEST_FILE_PATH, hits, session_id="self-test")
    first_name = hits[0][0]
    emit_deny(
        "PreToolUse",
        f"Bridge write blocked by scanner-safe-writer: {first_name} detected.",
    )
    sys.exit(0)


def main() -> None:
    """Hook entry point. Reads stdin, decides deny or pass."""
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
        _self_test()
        return

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw else {}
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name != "Write":
        # Only intercept Write. Other tools are scanned by sibling hooks.
        emit_pass()
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        emit_pass()
        sys.exit(0)

    file_path = tool_input.get("file_path", "") or ""
    if not _is_in_scope(file_path):
        emit_pass()
        sys.exit(0)

    content = tool_input.get("content", "") or ""
    if not isinstance(content, str) or not content:
        emit_pass()
        sys.exit(0)

    hits = _scan_content(content)
    if not hits:
        emit_pass()
        sys.exit(0)

    session_id = payload.get("session_id")
    _write_deny_record(file_path, hits, session_id)
    first_name, first_description, _ = hits[0]
    emit_deny(
        "PreToolUse",
        (
            f"Bridge write blocked by scanner-safe-writer: {first_name} "
            f"({first_description}) detected in {file_path}. Redact credential "
            "values before retrying. See .claude/hooks/scanner-safe-writer.log "
            "for the full deny record."
        ),
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
