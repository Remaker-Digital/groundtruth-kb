"""The peer-solution advisory rule states the amended contract (ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001 v3).

Carries the duties of the retired procedure-structure tests: the rule exists in
the neutral baseline, is projected unchanged, names its governing records, and
describes native ADVISORY authoring with no disposition lifecycle, approval
packet or advisory-only implementation path.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / ".harness-baseline-configuration/rules/peer-solution-advisory-loop.md"
PROJECTION = REPO_ROOT / ".claude/rules/peer-solution-advisory-loop.md"
GOVERNING = (
    "ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001",
    "DCL-ADVISORY-ROUTING-001",
    "DCL-PEER-SOLUTION-OWNER-GATE-001",
    "GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001",
)


def _rule() -> str:
    assert BASELINE.is_file(), BASELINE
    return BASELINE.read_text(encoding="utf-8")


def test_rule_is_authored_once_without_a_projected_copy() -> None:
    assert not PROJECTION.exists(), "rules are read on demand from the authored baseline"


def test_rule_names_the_governing_records() -> None:
    body = _rule()
    for record in GOVERNING:
        assert record in body, record


def test_rule_describes_native_advisory_authoring_without_a_disposition_lifecycle() -> None:
    body = _rule()
    assert "ADVISORY through the native bridge CLI" in body
    assert "no recipient_role" in body and "::init or ::open" in body
    assert "they do not create a disposition lifecycle" in body
    assert "Only ADVISORY follows ADVISORY on the same chain" in body
    assert "Do not create an approval packet" in body
    for retired in ("NO-GO@001", "Required follow-on:", "## Approval-Gate", "## Classification Vocabulary"):
        assert retired not in body, retired
