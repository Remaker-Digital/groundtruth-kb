"""Current bridge kinds reject retired aliases without rewriting old payloads."""

import pytest
from groundtruth_kb.bridge.taxonomy import BridgeKind

from scripts.lint_bridge_proposals import lint_file_content


def test_bridge_kind_enum_values():
    assert {kind.value for kind in BridgeKind} == {
        "implementation_proposal",
        "lo_verdict",
        "implementation_report",
        "governance_review",
        "governance_advisory",
        "index_reconciliation",
        "operational_state_change",
    }


@pytest.mark.parametrize("kind", [kind.value for kind in BridgeKind])
def test_lint_accepts_current_kind(kind):
    assert lint_file_content(f"NEW\nbridge_kind: {kind}\nDocument: test\nVersion: 001\n") is None


@pytest.mark.parametrize("kind", ["prime_proposal", "unknown", "loyal_opposition_verdict"])
def test_lint_rejects_retired_or_unknown_kind(kind):
    original = f"NEW\nbridge_kind: {kind}\nDocument: test\nVersion: 001\n"
    assert "Invalid bridge_kind" in lint_file_content(original)
    assert kind in original


def test_historical_inspection_does_not_invent_a_missing_kind():
    # Read-time lint remains diagnostic. The current writer requires the full
    # header and never normalizes or repairs historic payloads.
    assert lint_file_content("NEW\nDocument: historic\nVersion: 001\n") is None
