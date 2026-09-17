"""The Ollama harness governance records are current canonical records with their recorded types.

Carries the retained duty of the retired SQLite-era Ollama governance artifact cases: the five records exist and
keep their types. Their content defects noted by the 2026-09-13 trace (structural assertions naming absent
scripts) are formal reconciliation work, not test coverage.
"""

import pytest

pytestmark = pytest.mark.integration

RECORDS = {
    "ADR-OLLAMA-HARNESS-ADOPTION-001": "architecture_decision",
    "DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001": "design_constraint",
    "DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001": "design_constraint",
    "DCL-OLLAMA-TOOL-PARITY-GATE-001": "design_constraint",
    "GOV-HARNESS-ONBOARDING-CONTRACT-001": "governance",
}


@pytest.mark.parametrize("record_id", sorted(RECORDS))
def test_ollama_governance_record_is_current(formal_record, record_id):
    row = formal_record(record_id)
    assert row["type"] == RECORDS[record_id]
    assert row["authority"] == "stated"
    assert row["description"].strip()
