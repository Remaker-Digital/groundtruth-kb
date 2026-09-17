"""Owner decisions are asked through an explicit question and applied to canonical records (baseline guidance).

Carries the retained duty of the retired AskUserQuestion-enforcement cases: the standing priorities keep the
owner-question gate for implementation approval; no hook, tracker or decision ledger is asserted because owner
decisions live in the governed records they change, not in permission records.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRIORITIES = REPO_ROOT / ".harness-baseline-configuration/rules/standing-priorities.md"


def test_standing_priorities_keep_the_owner_question_gate() -> None:
    text = " ".join(PRIORITIES.read_text(encoding="utf-8").split())
    assert "Implementation-approved backlog items must be protected by AskUserQuestion evidence" in text
    assert "an explicit AskUserQuestion dialog for owner selection and approval" in text
    assert "It does not authorize implementation by itself" in text
