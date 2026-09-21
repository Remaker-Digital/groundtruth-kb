"""Loyal Opposition review evidence comes from inspection, never from speculative source changes.

Carries the retained duty of the retired file-safety clarification cases against the neutral baseline rule and its
projection: read-only review preparation, no speculative source modification, NO-GO when a proposal claims what
does not exist, and owner-authorized experiments isolated and reverted on NO-GO.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE = REPO_ROOT / ".harness-baseline-configuration/rules/loyal-opposition.md"
PROJECTION = REPO_ROOT / ".claude/rules/loyal-opposition.md"


def _one_line(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_review_evidence_is_inspection_not_modification() -> None:
    rule = _one_line(BASELINE)
    assert "Review evidence comes from inspecting the proposal and the current state" in rule
    assert "not from changing the sources under review" in rule
    assert "Do not make speculative source changes" in rule
    assert "self-fulfilling evidence" in rule


def test_nonexistent_claims_are_no_go_and_experiments_are_isolated_and_reverted() -> None:
    rule = _one_line(BASELINE)
    assert "When a proposal claims something that does not exist, answer NO-GO and name the gap" in rule
    assert "explicit owner authorization" in rule and "isolated checkout" in rule
    assert "reverted when the verdict is NO-GO" in rule


def test_rule_is_authored_once_without_a_projected_copy() -> None:
    assert not PROJECTION.exists(), "rules are read on demand from the authored baseline"
