"""WI-4458: structural test for the governance emergency-bootstrap protocol rule.

Bridge thread: bridge/gtkb-wi4458-governance-emergency-bootstrap-protocol-001.md
(Cursor-LO GO at -002).

Asserts the rule document exists and carries the three WI-4458 acceptance
elements plus the WI-4449 precedent citation.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_PATH = REPO_ROOT / ".claude" / "rules" / "governance-emergency-bootstrap-protocol.md"


def _text() -> str:
    assert RULE_PATH.is_file(), f"rule document missing: {RULE_PATH}"
    return RULE_PATH.read_text(encoding="utf-8")


def test_rule_document_exists_and_nonempty() -> None:
    text = _text()
    assert text.strip(), "rule document is empty"
    assert "Emergency-Bootstrap" in text


def test_sanctioned_conditions_section_present() -> None:
    """(a) sanctioned-conditions element."""
    text = _text()
    assert "(a) Sanctioned Conditions" in text
    # Narrowing intent must be explicit.
    assert "minimal repair" in text.lower()


def test_after_action_withdrawn_entry_required() -> None:
    """(b) after-action WITHDRAWN audit-trail entry citing commit SHA + verification."""
    text = _text()
    assert "(b) After-Action Audit-Trail Entry" in text
    assert "WITHDRAWN" in text
    assert "commit SHA" in text
    assert "verification evidence" in text.lower()


def test_retroactive_owner_approval_required() -> None:
    """(c) retroactive owner-approval capture via DELIB."""
    text = _text()
    assert "(c) Retroactive Owner-Approval Capture" in text
    assert "GOV-ARTIFACT-APPROVAL-001" in text
    assert "Deliberation" in text or "DELIB" in text


def test_precedent_citation_present() -> None:
    """References the WI-4449 precedent (commit + bridge entry)."""
    text = _text()
    assert "WI-4449" in text
    assert "gtkb-commit-untracked-governance-hooks-002.md" in text
