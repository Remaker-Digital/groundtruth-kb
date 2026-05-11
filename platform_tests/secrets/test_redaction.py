# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Test SPEC-SEC-SCAN-REDACTION-001 v1: raw secret values never appear in scanner output.

Per the Codex -002 F1 fix on bridge/gtkb-sec-redaction-commit-gate-001-002.md,
all fixture values are runtime-assembled and never written to tracked files
as provider-shaped contiguous text.
"""

from __future__ import annotations

import re

from groundtruth_kb.secrets.redaction import FINGERPRINT_PREFIX_LEN, fingerprint, redact_for_output


def _runtime_assembled_secret() -> str:
    """Build a fake provider-shaped value at runtime so the literal does not live in source."""
    head = "sk" + "_" + "test" + "_"
    body = "Z" * 24
    return head + body


def test_fingerprint_is_stable_and_does_not_contain_value() -> None:
    secret = _runtime_assembled_secret()
    fp = fingerprint(secret)
    assert fp.startswith("sha256:")
    assert len(fp) == len("sha256:") + FINGERPRINT_PREFIX_LEN
    assert secret not in fp


def test_redact_for_output_never_contains_raw_value() -> None:
    secret = _runtime_assembled_secret()
    redacted = redact_for_output(secret)
    assert secret not in redacted
    assert "len=" in redacted
    assert "sha256:" in redacted


def test_fingerprint_prefix_length_constant() -> None:
    assert FINGERPRINT_PREFIX_LEN == 8


def test_fingerprint_format_regex() -> None:
    fp = fingerprint(_runtime_assembled_secret())
    assert re.fullmatch(r"sha256:[0-9a-f]{8}", fp)


def test_redact_for_output_does_not_leak_under_format() -> None:
    secret = _runtime_assembled_secret()
    formatted = f"finding: {redact_for_output(secret)}"
    assert secret not in formatted


def test_fingerprint_differs_across_inputs() -> None:
    a = _runtime_assembled_secret()
    b = a + "X"
    assert fingerprint(a) != fingerprint(b)
