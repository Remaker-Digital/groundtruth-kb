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

``line_identity`` hashes a whole scanned line (not only the matched value). It
is the key of the commit gate's synthetic allowlist and is only printed for a
line that allowlist has already attested as synthetic.
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


def line_identity(line: str) -> str:
    """Return the full SHA-256 hex digest of one line of scanned text.

    The line is hashed exactly as the scanner saw it: its UTF-8 bytes without the
    line terminator, so an LF index blob and a CRLF working-tree copy of the same
    line share one identity. Callers must not print it for a finding that has not
    been attested as synthetic; the scanner's JSON report never includes it.
    """
    return hashlib.sha256(line.encode("utf-8")).hexdigest()
