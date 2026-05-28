"""Slice 1 regression tests for DCL-PEER-SOLUTION-OWNER-GATE-001.

Trace: ``bridge/gtkb-peer-solution-owner-gate-dcl-007.md`` (REVISED-3) IP-3
T1-T5 regression coverage; Codex GO at ``-008``.

The DCL records the Phase-1 advisory design constraint that peer-solution
adoption decisions (adopt / adapt / reject / defer / monitor classifications
per ``.claude/rules/peer-solution-advisory-loop.md`` section Classification
Vocabulary) MUST be collected via ``AskUserQuestion`` when they cross the
in-scope decision class threshold defined in
``.claude/rules/prime-builder-role.md`` section AskUserQuestion as the Only
Valid Owner-Decision Channel. In-scope classes are adopt, adapt,
reject-with-spec-impact, and defer; out-of-scope (Phase-1 narrowing) are
monitor and reject-with-no-spec-impact.

Tests:

- T1 (structural)                  -- ``test_dcl_row_structure``
- T2 (F3 closure, constraints)     -- ``test_constraints_enforcement_mode_advisory``
- T3 (constraint text)             -- ``test_description_references_auq_and_in_scope_classes``
- T4 (assertions predicate)        -- ``test_assertions_reference_in_scope_classes_predicate``
- T5 (F1 closure, vocabulary)      -- ``test_description_cites_procedure_rule_path_and_phase1_narrowing``
"""

from __future__ import annotations

import json

import pytest
from groundtruth_kb import KnowledgeDB

DCL_ID = "DCL-PEER-SOLUTION-OWNER-GATE-001"


@pytest.fixture(scope="module")
def dcl_spec() -> dict:
    db = KnowledgeDB("groundtruth.db")
    spec = db.get_spec(DCL_ID)
    assert spec is not None, f"{DCL_ID} not found in MemBase"
    return spec


def test_dcl_row_structure(dcl_spec: dict) -> None:
    """T1 (structural): DCL row exists with type='design_constraint' and status='specified'."""
    assert dcl_spec.get("type") == "design_constraint"
    assert dcl_spec.get("status") == "specified"
    desc = dcl_spec.get("description") or ""
    assert desc.strip(), "DCL description must be non-empty"


def test_constraints_enforcement_mode_advisory(dcl_spec: dict) -> None:
    """T2 (F3 closure from prior REVISED): row.constraints parses to {'enforcement_mode': 'advisory'}.

    Enforcement mode is stored under the existing ``constraints`` JSON column
    per the live ``specifications`` schema (no top-level ``enforcement_mode``
    column exists; that would require a separate schema-extension proposal).
    """
    constraints = dcl_spec.get("constraints")
    if isinstance(constraints, str):
        constraints = json.loads(constraints)
    assert isinstance(constraints, dict), (
        f"constraints must be a dict (after JSON parse if needed); "
        f"got {type(constraints).__name__}"
    )
    assert constraints.get("enforcement_mode") == "advisory", (
        f"constraints.enforcement_mode must be 'advisory'; "
        f"got {constraints.get('enforcement_mode')!r}"
    )


def test_description_references_auq_and_in_scope_classes(dcl_spec: dict) -> None:
    """T3 (constraint text): description references AskUserQuestion (or AUQ) and the in-scope decision classes (adopt / adapt / reject / defer)."""
    desc = dcl_spec.get("description") or ""
    # AUQ reference (either canonical name or the abbreviation)
    assert ("AskUserQuestion" in desc) or ("AUQ" in desc), (
        "description must reference 'AskUserQuestion' or 'AUQ'"
    )
    # Each in-scope class must appear in the description
    for cls in ("adopt", "adapt", "reject", "defer"):
        assert cls in desc, f"description must reference the in-scope class {cls!r}"


def test_assertions_reference_in_scope_classes_predicate(dcl_spec: dict) -> None:
    """T4 (assertions predicate): assertions field contains a machine-checkable predicate referencing the in-scope decision classes.

    Predicate form per proposal IP-1:

        assert (peer_solution_classification in {adopt, adapt, reject_with_spec_impact, defer}) -> auq_evidence_present
    """
    assertions = dcl_spec.get("assertions")
    if isinstance(assertions, str):
        assertions = json.loads(assertions)
    assert isinstance(assertions, list) and assertions, (
        f"assertions must be a non-empty list; got {type(assertions).__name__}"
    )
    predicate_found = False
    for entry in assertions:
        if not isinstance(entry, dict):
            continue
        pattern = str(entry.get("pattern") or "")
        if (
            "peer_solution_classification" in pattern
            and "adopt" in pattern
            and "adapt" in pattern
            and "defer" in pattern
            and "auq_evidence_present" in pattern
        ):
            predicate_found = True
            break
    assert predicate_found, (
        "at least one assertion's pattern must contain "
        "'peer_solution_classification' + the in-scope classes (adopt, adapt, "
        "defer) + 'auq_evidence_present' (T4 routing predicate)"
    )


def test_description_cites_procedure_rule_path_and_phase1_narrowing(dcl_spec: dict) -> None:
    """T5 (F1 closure, REVISED-3): description cites the procedure-rule path and documents Phase-1 narrowing.

    Closes Codex NO-GO F1 at ``bridge/gtkb-peer-solution-owner-gate-dcl-006.md``,
    which required the DCL to explicitly link to the governing peer-solution
    procedure rule and document the Phase-1 narrowing (which procedure-vocabulary
    states are in-scope vs out-of-scope of this DCL).
    """
    desc = dcl_spec.get("description") or ""
    # Procedure-rule path citation
    assert ".claude/rules/peer-solution-advisory-loop.md" in desc, (
        "description must cite the procedure-rule path "
        "'.claude/rules/peer-solution-advisory-loop.md' (F1 closure)"
    )
    # In-scope vs out-of-scope narrowing must be explicit
    # Phase-1 in-scope: adopt, adapt, reject_with_spec_impact, defer
    # Phase-1 out-of-scope: monitor, reject-with-no-spec-impact
    assert "monitor" in desc, (
        "description must document the 'monitor' classification (Phase-1 out-of-scope narrowing)"
    )
    # The "in-scope" / "out-of-scope" framing must be explicit
    assert ("in-scope" in desc.lower() or "in scope" in desc.lower()), (
        "description must explicitly identify in-scope decision classes "
        "(Phase-1 narrowing framing)"
    )
    assert ("out-of-scope" in desc.lower() or "out of scope" in desc.lower()), (
        "description must explicitly identify out-of-scope decision classes "
        "(Phase-1 narrowing framing)"
    )
