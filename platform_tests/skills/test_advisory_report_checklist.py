"""The advisory report checklist states the unresolved-material-choice duty (GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 v2).

Carries the retained duty of the retired owner-grilling-gate cases: an advisory identifies only unresolved
material owner choices with options and consequences, is informational and queue-free, and owner-directed
changes are applied through canonical writers without a permission ledger, mandatory interview or AUQ-only receipt.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = REPO_ROOT / ".harness-baseline-configuration/rules/loyal-opposition-review-checklists.md"
PROJECTED = REPO_ROOT / ".claude/rules/loyal-opposition-review-checklists.md"


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_advisory_report_checklist_states_the_unresolved_choice_duty() -> None:
    text = _text(CHECKLIST)
    assert "## Advisory Report Checklist" in CHECKLIST.read_text(encoding="utf-8")
    assert "identify only unresolved material owner choices, with practical options and consequences" in text
    assert "Is the advisory informational, absent from both role queues" in text
    assert "without a permission ledger, mandatory interview or AUQ-only receipt" in text


def test_checklist_is_a_deferred_baseline_rule_not_a_projection() -> None:
    # Deferred rules load on `::open <activity>` from the baseline; a projected copy would defeat the deferral.
    assert not PROJECTED.exists()
