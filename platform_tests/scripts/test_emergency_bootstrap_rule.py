"""The emergency-bootstrap rule bounds restoration of defective foundational controls (current wording).

Carries the retained duties of the retired protocol-document cases: the rule exists and names its governing
record; sanctioned conditions are narrow; the owner's bounded repair direction is applied directly to current
records without a decision or permission ledger; the defective gate is disclosed and independently verified.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE = REPO_ROOT / ".harness-baseline-configuration/rules/governance-emergency-bootstrap-protocol.md"


def _rule() -> str:
    text = RULE.read_text(encoding="utf-8")
    assert text.strip()
    return " ".join(text.split())


def test_rule_names_its_governing_record() -> None:
    assert "GOV-GTKB-EMERGENCY-BOOTSTRAP-001" in _rule()


def test_sanctioned_conditions_are_narrow() -> None:
    text = _rule()
    assert "demonstrated foundational defect that prevents its own ordinary repair" in text
    assert "ordinary friction or unrelated work does not qualify" in text


def test_owner_direction_is_applied_directly_without_a_ledger() -> None:
    text = _rule()
    assert "bounded repair direction in the interactive session" in text
    assert "Do not create an owner decision, permission, bundle or operational-event ledger" in text


def test_defective_gate_is_disclosed_and_independently_verified() -> None:
    text = _rule()
    assert "A defective gate is disclosed and corrected, not silently treated as current canon" in text
    assert "a different context independently verifies their result" in text
    assert "A restored-route component test does not qualify an actual emergency operation" in text
