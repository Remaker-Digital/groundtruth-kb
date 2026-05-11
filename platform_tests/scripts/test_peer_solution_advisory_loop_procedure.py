"""Regression tests for the Peer Solution Advisory Loop procedure document.

Per `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` IP-3:
asserts the procedure file exists and contains the 5 required sections
(Purpose / Classification vocabulary / Owner-dialogue workflow / Bridge
integration / Approval-gate) plus the five-state classification vocabulary
(adopt / adapt / reject / defer / monitor).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCEDURE_PATH = REPO_ROOT / ".claude" / "rules" / "peer-solution-advisory-loop.md"


def _read_procedure() -> str:
    if not PROCEDURE_PATH.is_file():
        pytest.fail(
            f"Procedure file missing: {PROCEDURE_PATH}. "
            "Per gtkb-peer-solution-advisory-loop-procedure-001 IP-1, the file "
            "must exist at .claude/rules/peer-solution-advisory-loop.md."
        )
    return PROCEDURE_PATH.read_text(encoding="utf-8")


def test_procedure_file_exists() -> None:
    """IP-1 acceptance: the procedure file is authored at the expected path."""
    assert PROCEDURE_PATH.is_file(), f"Procedure file not found at {PROCEDURE_PATH}"


def test_procedure_has_title() -> None:
    """The file leads with a top-level title matching the bridge thread name."""
    text = _read_procedure()
    assert text.startswith("# Peer Solution Advisory Loop Procedure"), (
        "Procedure file must lead with '# Peer Solution Advisory Loop Procedure' "
        "as its top-level heading."
    )


def test_procedure_has_purpose_section() -> None:
    """IP-1 §1: Purpose section defines the loop's role."""
    text = _read_procedure()
    assert "## Purpose" in text, "Procedure file missing '## Purpose' section."


def test_procedure_has_classification_vocabulary_section() -> None:
    """IP-1 §2: Classification vocabulary section defines the five states."""
    text = _read_procedure()
    assert "## Classification Vocabulary" in text, (
        "Procedure file missing '## Classification Vocabulary' section."
    )


def test_procedure_has_owner_dialogue_workflow_section() -> None:
    """IP-1 §3: Owner-dialogue workflow section defines expected Prime responses."""
    text = _read_procedure()
    assert "## Owner-Dialogue Workflow" in text, (
        "Procedure file missing '## Owner-Dialogue Workflow' section."
    )


def test_procedure_has_bridge_integration_section() -> None:
    """IP-1 §4: Bridge integration section defines how advisories enter the bridge."""
    text = _read_procedure()
    assert "## Bridge Integration" in text, (
        "Procedure file missing '## Bridge Integration' section."
    )


def test_procedure_has_approval_gate_section() -> None:
    """IP-1 §5: Approval-gate section clarifies per-protected-path packet requirement."""
    text = _read_procedure()
    assert "## Approval-Gate" in text, (
        "Procedure file missing '## Approval-Gate' section."
    )


def test_classification_vocabulary_enumerates_five_states() -> None:
    """The classification vocabulary section names all five states with backticked headings."""
    text = _read_procedure()
    # Each state appears as a level-3 heading with backticks
    required_states = ["adopt", "adapt", "reject", "defer", "monitor"]
    for state in required_states:
        marker = f"### `{state}`"
        assert marker in text, (
            f"Classification vocabulary missing '{marker}' subsection. "
            f"All five states (adopt/adapt/reject/defer/monitor) must be enumerated."
        )


def test_classification_states_define_required_followon() -> None:
    """Each classification state names a required follow-on artifact."""
    text = _read_procedure()
    # Count "Required follow-on" mentions; should be at least 5 (one per state)
    follow_on_count = text.count("Required follow-on:")
    assert follow_on_count >= 5, (
        f"Procedure file must define 'Required follow-on:' for each of the 5 "
        f"classification states; found {follow_on_count}."
    )


def test_procedure_cites_parent_thread() -> None:
    """The procedure cites its parent Slice-0 bridge thread for provenance."""
    text = _read_procedure()
    assert "gtkb-peer-solution-advisory-loop-conversion" in text, (
        "Procedure file must cite parent thread "
        "gtkb-peer-solution-advisory-loop-conversion for provenance."
    )


def test_procedure_cites_approval_packet_requirement() -> None:
    """Approval-Gate section cites GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001."""
    text = _read_procedure()
    assert "GOV-ARTIFACT-APPROVAL-001" in text, (
        "Procedure file must cite GOV-ARTIFACT-APPROVAL-001 in Approval-Gate section."
    )
    assert "DCL-ARTIFACT-APPROVAL-HOOK-001" in text, (
        "Procedure file must cite DCL-ARTIFACT-APPROVAL-HOOK-001 in Approval-Gate section."
    )


def test_procedure_distinguishes_da_from_bridge_followons() -> None:
    """Owner-dialogue workflow distinguishes DA-recorded vs bridge-tracked Prime responses."""
    text = _read_procedure()
    # Adopt/adapt go to bridge proposals
    assert "NEW bridge proposal" in text, (
        "Procedure must specify 'NEW bridge proposal' as the follow-on for adopt/adapt."
    )
    # Reject/defer/monitor go to Deliberation Archive
    assert "Deliberation Archive" in text, (
        "Procedure must specify 'Deliberation Archive' as the follow-on store for "
        "reject/defer/monitor."
    )


def test_procedure_documents_advisory_transport_convention() -> None:
    """Bridge integration section documents the NO-GO@001 transport convention until VERIFIED."""
    text = _read_procedure()
    assert "NO-GO@001" in text or "bridge_kind: loyal_opposition_advisory" in text, (
        "Procedure must document the LO advisory transport convention "
        "(NO-GO@001 status or bridge_kind: loyal_opposition_advisory)."
    )
