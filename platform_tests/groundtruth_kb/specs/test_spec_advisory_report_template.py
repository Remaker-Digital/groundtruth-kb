"""Current advisory authoring contract, independent of historical file shapes."""

import pytest

pytestmark = pytest.mark.integration
SPEC_ID = "SPEC-ADVISORY-REPORT-TEMPLATE-001"


def test_spec_row_structure(formal_record):
    row = formal_record(SPEC_ID)
    assert row["type"] == "requirement"
    assert row["description"].strip()


def test_template_names_either_author_role_without_a_recipient(formal_record):
    constraints = formal_record(SPEC_ID)["constraints"]
    assert set(constraints["author_roles"]) == {"pb", "lo"}
    assert constraints["bridge_kind"] == "governance_advisory"
    assert constraints["recipient_required"] is False


def test_report_prose_does_not_create_permission_or_disposition_state(formal_record):
    constraints = formal_record(SPEC_ID)["constraints"]
    assert constraints["classification_slot_required"] is False
    assert constraints["decision_ledger_required"] is False
    assert constraints["body_is_dispatch_authority"] is False
