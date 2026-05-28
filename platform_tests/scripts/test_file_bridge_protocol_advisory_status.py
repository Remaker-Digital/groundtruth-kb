"""Slice 1 regression tests for the ADVISORY bridge status extension in
``.claude/rules/file-bridge-protocol.md``.

Trace: ``bridge/gtkb-advisory-report-protocol-extension-003.md`` (REVISED-1)
IP-4 (T1-T3); Codex GO at ``-004``.

These tests assert the protocol-text contract only. Runtime parser/router
behavior for the ADVISORY status is owned by the parallel
``gtkb-bridge-advisory-status-001`` thread; tests for that behavior live
elsewhere.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = PROJECT_ROOT / ".claude" / "rules" / "file-bridge-protocol.md"


def _read_protocol_text() -> str:
    assert PROTOCOL_PATH.is_file(), f"protocol file missing: {PROTOCOL_PATH}"
    return PROTOCOL_PATH.read_text(encoding="utf-8")


def test_advisory_row_in_statuses_table() -> None:
    """T1: Statuses table contains an ADVISORY row with Loyal Opposition as the
    ``Set by`` value."""
    text = _read_protocol_text()
    pattern = re.compile(
        r"^\|\s*ADVISORY\s*\|\s*Loyal Opposition\s*\|.+?\|\s*$",
        re.MULTILINE,
    )
    matches = pattern.findall(text)
    assert matches, "ADVISORY row missing from Statuses table in .claude/rules/file-bridge-protocol.md"
    assert len(matches) == 1, f"expected exactly one ADVISORY row; found {len(matches)}: {matches!r}"


def test_advisory_reports_subsection_exists() -> None:
    """T2: A ``## Advisory Reports`` (or ``### Advisory Reports``) subsection
    exists."""
    text = _read_protocol_text()
    pattern = re.compile(r"^#{2,3}\s+Advisory Reports\s*$", re.MULTILINE)
    assert pattern.search(text), (
        "## Advisory Reports (or ### Advisory Reports) subsection missing from .claude/rules/file-bridge-protocol.md"
    )


def test_advisory_reports_subsection_mentions_axis_2_routing() -> None:
    """T3: The Advisory Reports subsection mentions the Axis-2 routing rule."""
    text = _read_protocol_text()
    # Locate the section and only inspect its body.
    section_match = re.search(
        r"^#{2,3}\s+Advisory Reports\s*\n(?P<body>.+?)(?=^#{2,3}\s+\S|^---|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert section_match, "Advisory Reports section anchor not located"
    body = section_match.group("body")
    assert re.search(r"axis[- ]?2", body, re.IGNORECASE), "Advisory Reports subsection does not mention Axis-2 routing"
