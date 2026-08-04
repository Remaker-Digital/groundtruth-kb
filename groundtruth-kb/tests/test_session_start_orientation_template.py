# Ac 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused contract tests for the session-start ORIENT template (WI-5575).

WI-5575 governs the pre-existing one-line ORIENT template change that replaces
the synthetic `ORIENT S{N}` counter with the bounded canonical identifier
`ORIENT <session_id-short>`.  These tests pin that contract: they reject
synthetic counters, require the approved bounded identifier, preserve the
seven-item ORIENT block, and require unavailable-identity fail-closed wording.
"""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb import get_templates_dir

ORIENT_TEMPLATE: Path = get_templates_dir() / "rules" / "session-start-orientation.md"

SYNTHETIC_COUNTER_RE = re.compile(r"ORIENT\s+S\d+\b")
CANONICAL_IDENTIFIER = "ORIENT <session_id-short>"
ORIENT_BLOCK_ITEMS = (
    "1 bridge:",
    "2 branch:",
    "3 worktree:",
    "4 wrap:",
    "5 blockers:",
    "6 refresh:",
    "7 next:",
)


def _template_text() -> str:
    return ORIENT_TEMPLATE.read_text(encoding="utf-8")


def test_template_exists_and_uses_bounded_canonical_identifier() -> None:
    text = _template_text()
    assert CANONICAL_IDENTIFIER in text, "template must use ORIENT <session_id-short>"


def test_template_rejects_synthetic_counter() -> None:
    text = _template_text()
    assert not SYNTHETIC_COUNTER_RE.search(text), "template must not retain a synthetic ORIENT S{N} counter"


def test_template_preserves_seven_item_orient_block() -> None:
    text = _template_text()
    for item in ORIENT_BLOCK_ITEMS:
        assert item in text, f"missing seven-item ORIENT block entry {item!r}"


def test_template_has_unavailable_id_fail_closed_wording() -> None:
    text = _template_text()
    assert "UNKNOWN" in text, "template must define unavailable-identity fail-closed wording"
    assert "<session_id-short>" in text, "unavailable-id path must reference the bounded identifier"
