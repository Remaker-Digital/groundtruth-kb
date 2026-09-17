"""Owner control of material choices without a blanket advisory interview."""

import pytest

pytestmark = pytest.mark.integration
DCL_ID = "DCL-PEER-SOLUTION-OWNER-GATE-001"


def test_dcl_row_structure(formal_record):
    row = formal_record(DCL_ID)
    assert row["type"] == "design_constraint"
    assert row["description"].strip()


def test_owner_questions_are_material_and_not_an_auq_permission_carrier(formal_record):
    constraints = formal_record(DCL_ID)["constraints"]
    assert constraints["material_owner_question_required"] is True
    assert constraints["routine_choice_requires_confirmation"] is False
    assert constraints["auq_only_evidence"] is False
    assert constraints["decision_ledger_required"] is False
    assert constraints["recommendation_is_dispatch"] is False


def test_companion_governance_requires_no_blanket_interview(formal_record):
    constraints = formal_record("GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001")["constraints"]
    assert set(constraints["author_roles"]) == {"pb", "lo"}
    assert constraints["material_owner_question_required"] is True
    assert constraints["blanket_interview_required"] is False
    assert constraints["decision_ledger_required"] is False


def test_intake_does_not_promote_work_or_require_a_grilling_heading(formal_record):
    constraints = formal_record("DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001")["constraints"]
    assert constraints["advisory_non_authoritative"] is True
    assert constraints["advisory_non_dispatchable"] is True
    assert constraints["one_material_owner_question_at_a_time"] is True
    assert constraints["decision_ledger_required"] is False
    assert constraints["mandatory_grilling_heading"] is False
    assert constraints["automatic_backlog_promotion"] is False


def test_radar_findings_use_the_same_owner_directed_advisory_boundary(formal_record):
    constraints = formal_record("SPEC-LO-OPPORTUNITY-RADAR-001")["constraints"]
    assert constraints["automatic_backlog_promotion"] is False
    assert constraints["direct_harness_dispatch"] is False
    assert constraints["role_is_harness_identity"] is False
    assert constraints["canonical_guidance"] == "universal_baseline"
