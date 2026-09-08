# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Presence-regression test for canonical NO-ACTION bridge status documentation.

Guards WI-5081 / DCL-NO-ACTION-STATUS-SEMANTICS-001: the NO-ACTION status and its
advisory-misuse constraint must remain documented on the two authority surfaces.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / ".claude/rules/file-bridge-protocol.md"
GLOSSARY = ROOT / ".claude/rules/canonical-terminology.md"


def test_no_action_status_section_documented_in_protocol() -> None:
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "## NO-ACTION Status" in text, "NO-ACTION semantics section missing from file-bridge-protocol.md"
    assert "NO-ACTION" in text


def test_no_action_advisory_misuse_constraint_documented() -> None:
    text = PROTOCOL.read_text(encoding="utf-8")
    # The distinctive anti-misuse phrase must be present so the constraint is not silently dropped.
    assert "with no verdict to correct" in text, "NO-ACTION advisory-misuse constraint missing"


def test_no_action_glossary_entry_documented() -> None:
    text = GLOSSARY.read_text(encoding="utf-8")
    assert "### NO-ACTION" in text, "NO-ACTION glossary entry missing from canonical-terminology.md"
