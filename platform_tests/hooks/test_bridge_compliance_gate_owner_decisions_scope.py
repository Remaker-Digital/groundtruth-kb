"""The Owner Decisions / Input section gate is present and vocabulary-scoped.

Owner ruling, 2026-09-07: checkpoint 2f688c4ca deleted the gate's three
OWNER_* regexes and the deny that used them, which broke `gt project doctor`
(NameError in the "Uncited owner-input bridges" check). The regexes were
restored byte-for-byte and the deny's scope is now derived from
``groundtruth_kb.bridge.vocabulary``: it applies to the Prime-authored,
Loyal-Opposition-actionable statuses and to nothing else.

This is also the compatibility evidence the protected-artifact inventory
registry requires for a change to the baseline hook (route
``compatibility_tests``).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from groundtruth_kb.bridge.vocabulary import (
    CANONICAL_STATUSES,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_GATE = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"
DENY_MARKER = "Bridge proposals/reports that claim owner-approval scope must"


@pytest.fixture(scope="module")
def gate():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_owner_scope", BASELINE_GATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gated_statuses_are_the_loyal_opposition_actionable_set(gate) -> None:
    assert gate.OWNER_DECISIONS_GATED_STATUSES == LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    assert {"NEW", "REVISED", "READY", "VERDICT-REJECTED"} == gate.OWNER_DECISIONS_GATED_STATUSES


def test_verdicts_advisories_and_closings_are_outside_the_gate(gate) -> None:
    outside = CANONICAL_STATUSES - gate.OWNER_DECISIONS_GATED_STATUSES
    assert outside == {"GO", "NO-GO", "NOT-READY", "VERIFIED", "SUPERSEDED", "ADVISORY", "WITHDRAWN", "BLOCKED"}


def test_regexes_are_defined_and_recognise_owner_approval_claims(gate) -> None:
    claims = "Scope follows the AskUserQuestion answer recorded on 2026-09-07 authorizing this change."
    assert gate._proposal_claims_owner_approval(claims) is True
    assert gate._proposal_claims_owner_approval("A routine refactor with no owner decision involved.") is False

    concrete = (
        claims
        + "\n\n## Owner Decisions / Input\n\n- AskUserQuestion 2026-09-07: restore the regexes (owner approval)\n"
    )
    assert gate._has_concrete_owner_decisions_section(concrete) is True
    placeholder = claims + "\n\n## Owner Decisions / Input\n\ntbd\n"
    assert gate._has_concrete_owner_decisions_section(placeholder) is False
    assert gate._has_concrete_owner_decisions_section(claims) is False


def test_deny_is_present_once_and_scoped_by_the_gated_set() -> None:
    text = BASELINE_GATE.read_text(encoding="utf-8")
    assert text.count(DENY_MARKER) == 1, "the Owner Decisions / Input deny must exist exactly once"
    deny_at = text.index(DENY_MARKER)
    guard_at = text.rfind("first_line in OWNER_DECISIONS_GATED_STATUSES", 0, deny_at)
    assert guard_at != -1 and deny_at - guard_at < 600, "the deny must be guarded by OWNER_DECISIONS_GATED_STATUSES"
    assert "DEFERRED_REASON_RE" not in text, "the retired DEFERRED regexes must not return"
