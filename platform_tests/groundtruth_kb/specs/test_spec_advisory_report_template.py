"""Slice 1 regression tests for SPEC-ADVISORY-REPORT-TEMPLATE-001.

Trace: ``bridge/gtkb-advisory-report-template-spec-005.md`` (REVISED-2)
IP-3 T1-T5 regression coverage; Codex GO at ``-006``.

The SPEC records the standard template (header fields + body sections)
every ADVISORY-status bridge document must include. The ``## Classification
Slot`` carries literal ``pending`` at LO filing time; Prime MUST NOT edit
the original ADVISORY report. Classification is recorded in the response
artifact per ``.claude/rules/peer-solution-advisory-loop.md``
Owner-Dialogue Workflow (NEW bridge proposal for adopt/adapt; DA record
for reject/defer/monitor).

Tests:

- T1 (structural)                 -- ``test_spec_row_structure``
- T2 (header fields)              -- ``test_required_header_fields_enumerated``
- T3 (body sections)              -- ``test_required_body_sections_enumerated``
- T4 (vocabulary enumeration)     -- ``test_classification_vocabulary_closed``
- T5 (F1 source-of-truth phrases) -- ``test_source_of_truth_boundary_phrases``
"""

from __future__ import annotations

import pytest
from groundtruth_kb import KnowledgeDB

SPEC_ID = "SPEC-ADVISORY-REPORT-TEMPLATE-001"


@pytest.fixture(scope="module")
def spec() -> dict:
    db = KnowledgeDB("groundtruth.db")
    row = db.get_spec(SPEC_ID)
    assert row is not None, f"{SPEC_ID} not found in MemBase"
    return row


def test_spec_row_structure(spec: dict) -> None:
    """T1 (structural): SPEC row exists with type='requirement', status='specified', non-empty description."""
    assert spec.get("type") == "requirement"
    assert spec.get("status") == "specified"
    desc = spec.get("description") or ""
    assert desc.strip(), "SPEC description must be non-empty"


def test_required_header_fields_enumerated(spec: dict) -> None:
    """T2 (header fields): description enumerates the five required header fields per IP-1 item 1."""
    desc = spec.get("description") or ""
    required = ("bridge_kind", "Document", "Version", "Author", "Date")
    missing = [f for f in required if f not in desc]
    assert not missing, f"description must enumerate all required header fields; missing: {missing}"
    # Closed-set hint: the spec's required header fields must be exactly five.
    # We do not enforce ordering or uniqueness here (different sections may
    # reference these tokens), but we do anchor on the IP-1 enumeration phrase
    # so future drift requires an explicit spec amendment.
    assert "five header fields" in desc, (
        "description must declare the closed-set count via the phrase 'five header fields'"
    )


def test_required_body_sections_enumerated(spec: dict) -> None:
    """T3 (body sections): description enumerates the five required body sections per IP-1 item 2."""
    desc = spec.get("description") or ""
    required = (
        "## Source",
        "## Claim",
        "## Owner Decision Needed",
        "## Recommended Prime Action",
        "## Classification Slot",
    )
    missing = [s for s in required if s not in desc]
    assert not missing, f"description must enumerate all required body sections; missing: {missing}"
    assert "five body sections" in desc, (
        "description must declare the closed-set count via the phrase 'five body sections'"
    )


def test_classification_vocabulary_closed(spec: dict) -> None:
    """T4 (vocabulary enumeration): description enumerates exactly the 5-state classification vocabulary;
    no superset, no subset.

    Source-of-truth: ``.claude/rules/peer-solution-advisory-loop.md`` Classification
    Vocabulary. The closed enumeration phrase asserted here anchors the
    canonical list and prevents silent drift to a 4- or 6-state vocabulary.
    """
    desc = spec.get("description") or ""
    vocab = ("adopt", "adapt", "reject", "defer", "monitor")
    missing = [v for v in vocab if v not in desc]
    assert not missing, f"description must enumerate all five classification states; missing: {missing}"
    # Closed-vocabulary anchor phrase: prevents silent superset/subset drift.
    assert "five classification states are: adopt, adapt, reject, defer, monitor" in desc, (
        "description must include the closed-vocabulary enumeration "
        "'five classification states are: adopt, adapt, reject, defer, monitor'"
    )


def test_source_of_truth_boundary_phrases(spec: dict) -> None:
    """T5 (F1 closure): description contains both literal source-of-truth-boundary phrases.

    Closes Codex NO-GO F1 at ``bridge/gtkb-advisory-report-template-spec-004.md``,
    which rejected the prior REVISED-1 wording for blurring the LO-authored
    audit boundary. The two phrases asserted here are the mechanical proof
    that the boundary is recorded in the spec text.
    """
    desc = spec.get("description") or ""
    assert "Prime MUST NOT edit the original ADVISORY report" in desc, (
        "description must include the LO-authored-audit-boundary phrase "
        "'Prime MUST NOT edit the original ADVISORY report' "
        "(F1 closure)"
    )
    assert "classification is recorded in the response artifact" in desc, (
        "description must include the disposition-in-response-artifact phrase "
        "'classification is recorded in the response artifact' "
        "(F1 closure)"
    )
