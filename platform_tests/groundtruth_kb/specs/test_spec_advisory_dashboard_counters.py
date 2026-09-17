"""Read-only canonical retirement checks; this does not qualify live delivery."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("identifier", ["SPEC-ADVISORY-DASHBOARD-COUNTERS-001", "SPEC-INTAKE-2485e9"])
def test_directed_counter_and_event_contracts_are_retired(formal_record, identifier):
    row = formal_record(identifier, expected_status="retired")
    assert row["status"] == "retired"
    assert row["retired_at"]
    assert row["description"]
