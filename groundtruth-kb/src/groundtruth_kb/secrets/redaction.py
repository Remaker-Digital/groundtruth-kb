# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Redaction helpers — fingerprint a matched secret value without exposing it.

Anchored: SPEC-SEC-SCAN-REDACTION-001 v1 (S333).

The fingerprint is a SHA-256 prefix (first 8 hex chars) computed from the
matched value. It is a stable identifier that lets reviewers correlate
findings across runs without revealing the value itself. Raw values must
never appear in any scanner output path: stdout, JSON reports, CI artifacts,
doctor alert summaries, log files.

Tests in tests/secrets/test_redaction.py assert that for every output mode
the raw fixture value never appears in the output text.
"""

from __future__ import annotations

import hashlib

FINGERPRINT_PREFIX_LEN = 8


def fingerprint(value: str) -> str:
    """Return ``sha256:<8-hex>`` identifier for ``value``. Never returns ``value`` itself."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:FINGERPRINT_PREFIX_LEN]}"


def redact_for_output(value: str) -> str:
    """Return the redacted form suitable for any human-or-machine output.

    The redacted form embeds the fingerprint and the value's length but never
    the value itself.
    """
    return f"<redacted len={len(value)} {fingerprint(value)}>"
