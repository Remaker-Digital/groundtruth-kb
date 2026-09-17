"""The cross-harness parity foundation (WI-4875 F1) exists in the native authority with its required structure."""

from __future__ import annotations

ADR_ID = "ADR-CROSS-HARNESS-PARITY-001"
DCL_ID = "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001"
ADR_REQUIRED_SECTIONS = ("## Decision", "## Context", "## Rejected alternatives", "## Consequences", "## Rationale")
DCL_REQUIRED_STATEMENTS = (
    "the same canonical baseline",
    "report precisely which result it measured",
    "Select targets explicitly",
    "Compare the complete engine plan with installed output",
)


def test_parity_adr_is_active_with_its_decision_sections(formal_record):
    adr = formal_record(ADR_ID)
    assert adr["type"] == "architecture_decision"
    body = adr["description"] or ""
    missing = [section for section in ADR_REQUIRED_SECTIONS if section not in body]
    assert not missing, f"{ADR_ID} body missing required sections {missing}"
    assert adr["source_paths"], f"{ADR_ID} names no live enforcement source"


def test_parity_dcl_is_active_with_stated_assertions(formal_record):
    dcl = formal_record(DCL_ID)
    assert dcl["type"] == "design_constraint"
    assert dcl["assertions"], f"{DCL_ID} states no assertion"
    body = dcl["description"] or ""
    missing = [statement for statement in DCL_REQUIRED_STATEMENTS if statement not in body]
    assert not missing, f"{DCL_ID} body missing conformance statements {missing}"
