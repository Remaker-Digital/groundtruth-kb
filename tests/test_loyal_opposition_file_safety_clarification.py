# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Content assertion: LO file safety rule clarification subsection lands.

Per bridge `gtkb-lo-file-safety-rule-clarification-001` GO at -002, IP-1 adds
a "Reviewer-Evidence-Preparation vs Speculative Source Modification"
subsection to ``.claude/rules/loyal-opposition.md`` that distinguishes:

- Permitted: read-only review preparation.
- Prohibited: speculative source modification during review.
- Permitted-with-authorization: speculative source modification with explicit
  owner AskUserQuestion authorization in the same session.

This test asserts the section landed with the load-bearing wording so future
edits cannot silently strip the clarification.

Spec: T-LO-FILESAFETY-clarification-section-present (proposal IP-1 +
``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``).
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RULE_FILE = REPO_ROOT / ".claude" / "rules" / "loyal-opposition.md"


@pytest.fixture(scope="module")
def rule_text() -> str:
    return RULE_FILE.read_text(encoding="utf-8")


def test_clarification_section_header_present(rule_text: str) -> None:
    assert (
        "## Reviewer-Evidence-Preparation vs Speculative Source Modification"
        in rule_text
    ), "subsection header missing from .claude/rules/loyal-opposition.md"


def test_permitted_read_only_review_prep_subsection(rule_text: str) -> None:
    assert "### Permitted: read-only review preparation" in rule_text


def test_prohibited_speculative_source_modification_subsection(
    rule_text: str,
) -> None:
    assert "### Prohibited: speculative source modification during review" in rule_text


def test_self_fulfilling_evidence_pattern_wording(rule_text: str) -> None:
    assert "self-fulfilling-evidence pattern" in rule_text, (
        "load-bearing 'self-fulfilling-evidence pattern' wording missing; "
        "this is the diagnostic frame for the prohibited LO behavior class."
    )


def test_inspection_only_validation_wording(rule_text: str) -> None:
    # Tolerate either single-line or wrapped form; key phrase is the contrast
    # of "inspection of the proposal text + current state" vs "hands-on
    # modification".
    normalized = " ".join(rule_text.split())
    expected_normalized = (
        "must be by inspection of the proposal text + current state, not by "
        "hands-on modification"
    )
    assert expected_normalized in normalized, (
        "validation-by-inspection wording missing"
    )


def test_owner_authorization_exception_subsection(rule_text: str) -> None:
    assert (
        "### Permitted: speculative source modification with explicit owner authorization"
        in rule_text
    )


def test_revert_on_no_go_clause(rule_text: str) -> None:
    assert "reverted if the proposal is NO-GO" in rule_text, (
        "owner-authorized exception must require revert-on-NO-GO so audit "
        "trail does not include LO-authored speculative state"
    )


def test_what_to_do_when_proposal_claims_something_doesnt_exist(
    rule_text: str,
) -> None:
    assert "What to do when the proposal claims something exists that doesn't" in rule_text
    assert "MUST NOT add X to file Y as part of" in rule_text
