"""Current ADVISORY routing requirements, read through native authority."""

import pytest

pytestmark = pytest.mark.integration
DCL_ID = "DCL-ADVISORY-ROUTING-001"


def test_dcl_row_structure(formal_record):
    row = formal_record(DCL_ID)
    assert row["type"] == "design_constraint"
    assert row["description"].strip()


def test_advisory_is_informational_for_both_roles(formal_record):
    constraints = formal_record(DCL_ID)["constraints"]
    assert constraints["advisory_non_dispatchable"] is True
    assert constraints["advisory_non_authoritative"] is True
    assert set(constraints["author_roles"]) == {"pb", "lo"}
    assert constraints["automatic_work_selection"] is False


def test_implementation_requires_its_own_chain(formal_record):
    constraints = formal_record(DCL_ID)["constraints"]
    assert constraints["same_chain_successors"] == ["ADVISORY"]
    assert constraints["implementation_requires_fresh_chain"] is True
