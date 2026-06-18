"""FAB-14 (WI-4426) HYG-046: Requirement Sufficiency parser.

Asserts the begin-time Requirement-Sufficiency classifier accepts h2 AND h3
headings, accepts bounded sufficiency/gap phrasing without a per-incident literal
list, and distinguishes an absent section ("missing") from a present-but-
unrecognized one ("unrecognized"). Authority: SPEC-AUQ-POLICY-ENGINE-001,
DELIB-FAB14-REMEDIATION-20260610.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "scripts"
if _SCRIPTS.is_dir() and str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from implementation_authorization import requirement_sufficiency_state  # noqa: E402


def _doc(level, body):
    return f"# Proposal\n\n{level} Requirement Sufficiency\n\n{body}\n\n## Next\n\nx\n"


def test_h3_requirement_sufficiency_is_parsed():
    md = _doc("###", "Existing requirements sufficient. Governing specs already constrain the scope.")
    assert requirement_sufficiency_state(md) == "sufficient"


def test_h2_requirement_sufficiency_sufficient():
    md = _doc("##", "Existing requirements are sufficient for this scoped correction.")
    assert requirement_sufficiency_state(md) == "sufficient"


def test_bounded_sufficiency_phrasing_variants():
    for body in [
        "Requirements remain sufficient.",
        "Existing owner direction and WI-4213 are sufficient.",
        "The existing requirements are sufficient.",
    ]:
        assert requirement_sufficiency_state(_doc("##", body)) == "sufficient", body


def test_gap_state():
    md = _doc("##", "New or revised requirement required before implementation.")
    assert requirement_sufficiency_state(md) == "gap"


def test_negated_gap_phrase_is_sufficient_not_gap():
    md = _doc(
        "##",
        "Existing requirements sufficient. No new or revised requirement is needed before implementation.",
    )
    assert requirement_sufficiency_state(md) == "sufficient"


def test_sufficiency_declaration_precedes_future_gap_context():
    proposal = _ROOT / "bridge" / "gtkb-stale-git-worktree-autogc-diagnosis-001.md"
    md = proposal.read_text(encoding="utf-8")
    assert requirement_sufficiency_state(md) == "sufficient"


def test_sufficiency_declaration_does_not_hide_present_tense_gap():
    md = _doc(
        "##",
        "Existing requirements are sufficient, but new or revised requirement required before implementation.",
    )
    assert requirement_sufficiency_state(md) == "gap"


def test_gap_declaration_precedes_later_sufficiency_context():
    md = _doc(
        "##",
        (
            "New or revised requirement required before implementation. "
            "After that requirement lands, existing requirements are sufficient."
        ),
    )
    assert requirement_sufficiency_state(md) == "gap"


def test_absent_section_is_missing():
    md = "# Proposal\n\n## Summary\n\nNo sufficiency section here.\n"
    assert requirement_sufficiency_state(md) == "missing"


def test_unrecognized_phrasing_is_distinct_from_missing():
    md = _doc("##", "We think this is probably fine to proceed with.")
    assert requirement_sufficiency_state(md) == "unrecognized"


def test_not_sufficient_is_not_classified_sufficient():
    md = _doc("##", "The requirements are not sufficient for this work.")
    assert requirement_sufficiency_state(md) != "sufficient"
