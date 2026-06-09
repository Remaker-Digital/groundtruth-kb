# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Child 4 governance-artifact tests for Phase-1 Ollama integration (WI-4324/WI-4325).

Authority: bridge/gtkb-ollama-integration-phase-1-governance-impl-002.md (Codex
GO). Owner anchor DELIB-20260663.

Covers the Child 4 Specification-Derived Verification Plan:

- WI-4324: the five formal MemBase specs are present with the expected
  type/status, are packet-gated (change_reason cites the approval packet), and
  carry the fail-closed guard-adapter contract.
- WI-4325: the three canonical-terminology glossary entries and the
  operating-model section 3 status text are present and correct (registered /
  no-active-role / not a dispatch target).
- Approval-packet evidence: the five formal-artifact-approval packets and the
  two narrative-artifact-approval packets exist, validate, and (for narrative)
  match the current protected-file content.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

OLLAMA_SPECS = {
    "ADR-OLLAMA-HARNESS-ADOPTION-001": "architecture_decision",
    "DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001": "design_constraint",
    "DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001": "design_constraint",
    "DCL-OLLAMA-TOOL-PARITY-GATE-001": "design_constraint",
    "GOV-HARNESS-ONBOARDING-CONTRACT-001": "governance",
}

_PACKET_DIR = PROJECT_ROOT / ".groundtruth" / "formal-artifact-approvals"
FORMAL_PACKETS = {spec_id: _PACKET_DIR / f"2026-06-05-{spec_id}.json" for spec_id in OLLAMA_SPECS}
NARRATIVE_PACKETS = {
    ".claude/rules/canonical-terminology.md": _PACKET_DIR / "2026-06-09-claude-rules-canonical-terminology-md.json",
    ".claude/rules/operating-model.md": _PACKET_DIR / "2026-06-05-operating-model-ollama-narrative.json",
}

CT_PATH = PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md"
OM_PATH = PROJECT_ROOT / ".claude" / "rules" / "operating-model.md"


# ──────────────────────────────────────────────────────────────────────────
# WI-4324: MemBase spec rows present with the right type/status
# ──────────────────────────────────────────────────────────────────────────


def _row(spec_id: str) -> dict:
    """Return the latest version row for spec_id from groundtruth.db."""
    db_path = PROJECT_ROOT / "groundtruth.db"
    assert db_path.is_file(), f"MemBase missing at {db_path}"
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT id, type, status, title, description, change_reason "
            "FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1",
            (spec_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    assert row is not None, f"MemBase has no row for {spec_id}"
    return {
        "id": row[0],
        "type": row[1],
        "status": row[2],
        "title": row[3],
        "description": row[4] or "",
        "change_reason": row[5] or "",
    }


def test_all_five_ollama_specs_present_with_expected_type_and_status() -> None:
    for spec_id, expected_type in OLLAMA_SPECS.items():
        row = _row(spec_id)
        assert row["type"] == expected_type, f"{spec_id}: type {row['type']} != {expected_type}"
        assert row["status"] == "specified", f"{spec_id}: status {row['status']} != specified"


def test_tool_parity_spec_carries_fail_closed_guard_adapter_contract() -> None:
    row = _row("DCL-OLLAMA-TOOL-PARITY-GATE-001")
    desc = row["description"]
    assert "fail-closed" in desc.lower(), "tool-parity DCL must state the fail-closed rule"
    assert "guard adapter" in desc.lower(), "tool-parity DCL must reference the guard adapter"
    # The canonical six-tool set must be named.
    for tool in ("Read", "Write", "Edit", "Grep", "Glob", "Bash"):
        assert tool in desc, f"tool-parity DCL must name canonical tool {tool}"


def test_adoption_adr_records_framework_free_decision_and_guard_consequence() -> None:
    desc = _row("ADR-OLLAMA-HARNESS-ADOPTION-001")["description"]
    assert "harness identity D" in desc or "identity D" in desc
    assert "fail-closed" in desc.lower()
    # Rejected alternatives recorded (decision-log discipline).
    assert "LangChain" in desc and "CLI pass-through" in desc


def test_onboarding_gov_declares_capability_floor_with_guard_field() -> None:
    desc = _row("GOV-HARNESS-ONBOARDING-CONTRACT-001")["description"]
    assert "tool_guard_adapter_fail_closed = true" in desc
    assert "advertised_tool_subset" in desc


def test_each_spec_is_packet_gated_via_change_reason() -> None:
    """Packet-gated evidence: each spec's change_reason cites its approval packet."""
    for spec_id in OLLAMA_SPECS:
        change_reason = _row(spec_id)["change_reason"]
        expected_packet = f".groundtruth/formal-artifact-approvals/2026-06-05-{spec_id}.json"
        assert expected_packet in change_reason, f"{spec_id}: change_reason does not cite {expected_packet}"


# ──────────────────────────────────────────────────────────────────────────
# WI-4325: protected narrative edits present and correct
# ──────────────────────────────────────────────────────────────────────────


def test_canonical_terminology_has_three_ollama_glossary_entries() -> None:
    src = CT_PATH.read_text(encoding="utf-8")
    assert "### ollama" in src
    assert "### routing.toml" in src
    assert "### task-to-model routing" in src


def test_ollama_glossary_entries_cite_authorities() -> None:
    src = CT_PATH.read_text(encoding="utf-8")
    assert "ADR-OLLAMA-HARNESS-ADOPTION-001" in src
    assert "DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001" in src
    assert "DELIB-20260663" in src


def test_operating_model_section_3_records_registered_no_active_role() -> None:
    src = OM_PATH.read_text(encoding="utf-8")
    assert "Ollama harness" in src
    assert "ADR-OLLAMA-HARNESS-ADOPTION-001" in src
    # Registered / no-active-role / no dispatch routing language present.
    assert "no active role" in src
    assert "no bridge dispatch routing" in src
    assert "no role promotion until a later approved bridge" in src
    # Phase 2+ recorded as intended-but-partial.
    assert "Ollama harness Phase 2+" in src


# ──────────────────────────────────────────────────────────────────────────
# Approval-packet evidence: formal + narrative packets exist and validate
# ──────────────────────────────────────────────────────────────────────────


def test_five_formal_approval_packets_exist_and_validate() -> None:
    from groundtruth_kb.governance.approval_packet import validate_packet

    for spec_id, packet_path in FORMAL_PACKETS.items():
        assert packet_path.is_file(), f"formal packet missing for {spec_id}: {packet_path}"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        result = validate_packet(packet)
        assert result.is_valid, f"{spec_id} packet invalid: {result.errors}"
        assert packet["artifact_id"] == spec_id
        assert packet.get("approved_by") == "owner" or packet.get("acknowledged_by") == "owner"


def test_two_narrative_packets_exist_and_match_current_file_content() -> None:
    from groundtruth_kb.governance.narrative_artifact_packet import (
        read_lf_normalized,
        validate_narrative_packet,
    )

    for rel_path, packet_path in NARRATIVE_PACKETS.items():
        assert packet_path.is_file(), f"narrative packet missing: {packet_path}"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        proposed = read_lf_normalized(PROJECT_ROOT / rel_path)
        result = validate_narrative_packet(packet, rel_path=rel_path, proposed_content=proposed)
        assert result.is_valid, f"narrative packet for {rel_path} invalid or content mismatch: {result.errors}"
        assert packet["target_path"] == rel_path
