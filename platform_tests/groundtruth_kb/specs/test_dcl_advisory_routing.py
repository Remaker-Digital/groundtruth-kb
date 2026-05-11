"""Slice 1 regression tests for DCL-ADVISORY-ROUTING-001.

Trace: ``bridge/gtkb-advisory-routing-dcl-003.md`` (REVISED-1) IP-3 T1-T5
regression coverage; Codex GO at ``-004``.

The DCL records the design constraint that ADVISORY-status bridge entries
SHOULD route via Axis-2 (non-dispatchable), that the cross-harness
event-driven trigger SHOULD exclude them from actionable-signature
computation, and that ADVISORY surfacing into the interactive chat session
is via the in-session AXIS 2 UserPromptSubmit hook instead. The SHOULD
(not MUST) wording matches the now-VERIFIED sibling protocol-extension at
``bridge/gtkb-advisory-report-protocol-extension-006.md``; the
``constraints={"enforcement_mode": "advisory"}`` JSON storage is the live
specifications-schema-compatible mapping for enforcement mode.

Tests:

- T1 (structural)         -- ``test_dcl_row_structure``
- T2 (F3 closure)         -- ``test_constraints_enforcement_mode_advisory``
- T3 (constraint text)    -- ``test_constraint_text_references_axis_2_surface``
- T4 (F2 closure)         -- ``test_should_not_must_wording``
- T5 (assertions)         -- ``test_assertions_reference_advisory_precondition``
"""

from __future__ import annotations

import json

import pytest

from groundtruth_kb import KnowledgeDB

DCL_ID = "DCL-ADVISORY-ROUTING-001"


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
    """T2 (F3 closure): row.constraints parses to {'enforcement_mode': 'advisory'}.

    Enforcement mode is stored under the existing ``constraints`` JSON column
    per the live ``specifications`` schema. A first-class ``enforcement_mode``
    column would require a separate schema-extension bridge proposal.
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


def test_constraint_text_references_axis_2_surface(dcl_spec: dict) -> None:
    """T3 (constraint text): description references Axis-2, non-dispatchable, actionable-signature, and the AXIS 2 surface (UserPromptSubmit hook)."""
    desc = dcl_spec.get("description") or ""
    for needle in ("Axis-2", "non-dispatchable", "actionable-signature"):
        assert needle in desc, f"description must reference {needle!r}"
    # T3 alternative tokens for the AXIS 2 surface, per the proposal wording
    assert ("UserPromptSubmit" in desc) or ("AXIS 2 surface" in desc), (
        "description must reference 'UserPromptSubmit' or 'AXIS 2 surface' "
        "(the in-session AXIS 2 surfacing path)"
    )


def test_should_not_must_wording(dcl_spec: dict) -> None:
    """T4 (F2 closure): description uses SHOULD-not-MUST wording matching the sibling protocol-extension VERIFIED text.

    Closes Codex NO-GO F2 at ``bridge/gtkb-advisory-routing-dcl-002.md``,
    which rejected ``MUST be routed`` / ``MUST exclude`` as over-hardening
    the sibling's verified ``SHOULD`` wording at
    ``bridge/gtkb-advisory-report-protocol-extension-006.md``.
    """
    desc = dcl_spec.get("description") or ""
    assert "SHOULD be routed" in desc, (
        "description must include 'SHOULD be routed' "
        "(matching sibling protocol-extension VERIFIED wording)"
    )
    assert "SHOULD exclude" in desc, (
        "description must include 'SHOULD exclude' "
        "(matching sibling protocol-extension VERIFIED wording)"
    )
    # Negative checks: MUST-form must not appear in the normative-constraint
    # phrasing. Deferred to a future bridge slice gated on parallel runtime
    # thread per-parser empirical evidence.
    assert "MUST be routed" not in desc, (
        "description must not use 'MUST be routed' wording; SHOULD-to-MUST "
        "promotion is deferred"
    )
    assert "MUST exclude" not in desc, (
        "description must not use 'MUST exclude' wording; SHOULD-to-MUST "
        "promotion is deferred"
    )


def test_assertions_reference_advisory_precondition(dcl_spec: dict) -> None:
    """T5 (assertions predicate): at least one assertion describes the routing predicate with the ADVISORY precondition.

    The predicate form per proposal IP-1 is::

        assert (latest_status == "ADVISORY") -> (
            recipient_actionable_signature_excludes_entry_by_default
            AND axis_2_surface_notifies_in_session
        )
    """
    assertions = dcl_spec.get("assertions")
    if isinstance(assertions, str):
        assertions = json.loads(assertions)
    assert isinstance(assertions, list) and assertions, (
        f"assertions must be a non-empty list; got {type(assertions).__name__}"
    )
    advisory_predicate_found = False
    for entry in assertions:
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("description") or "")
        if "ADVISORY" in text and "latest_status" in text:
            advisory_predicate_found = True
            break
    assert advisory_predicate_found, (
        "at least one assertion must reference the 'latest_status == ADVISORY' "
        "precondition (T5 routing predicate)"
    )
