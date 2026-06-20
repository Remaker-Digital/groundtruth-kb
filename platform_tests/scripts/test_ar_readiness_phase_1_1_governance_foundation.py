from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.governance.approval_packet import validate_packet  # noqa: E402

ADR_ID = "ADR-APPLICATION-ISOLATION-CONTRACT-001"
DCL_ID = "DCL-APP-ROOT-MINIMIZATION-001"
APP_REGISTRY = REPO_ROOT / "applications" / "Agent_Red" / ".gtkb-app-isolation.json"
CONTENT_DIR = REPO_ROOT / ".gtkb-state" / "formal-artifact-content" / "agent-red-readiness-phase-1-1"
APP_ROOT = REPO_ROOT / "applications" / "Agent_Red"


def _db() -> KnowledgeDB:
    return KnowledgeDB(REPO_ROOT / "groundtruth.db")


def _spec(spec_id: str) -> dict:
    db = _db()
    try:
        row = db.get_spec(spec_id)
    finally:
        db.close()
    assert row is not None, f"{spec_id} must exist in MemBase"
    return row


def _packet(spec_id: str) -> dict:
    packet_path = REPO_ROOT / ".groundtruth" / "formal-artifact-approvals" / f"2026-06-19-{spec_id}.json"
    assert packet_path.is_file(), f"{packet_path} must exist"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert validate_packet(packet).is_valid is True
    assert packet["artifact_id"] == spec_id
    assert packet["full_content"] == (CONTENT_DIR / f"{spec_id}.md").read_text(encoding="utf-8")
    return packet


def _registry_entries() -> list[dict]:
    registry = json.loads(APP_REGISTRY.read_text(encoding="utf-8"))
    entries = registry.get("top_level_artifacts")
    assert isinstance(entries, list) and entries, "Agent Red registry must list top-level artifacts"
    return entries


def test_phase_1_1_formal_specs_exist_with_required_sections() -> None:
    adr = _spec(ADR_ID)
    dcl = _spec(DCL_ID)

    assert adr["type"] == "architecture_decision"
    assert adr["status"] == "specified"
    for heading in ("## Decision", "## Rationale", "## Consequences", "## Rejected Alternatives"):
        assert heading in adr["description"]

    assert dcl["type"] == "design_constraint"
    assert dcl["status"] == "specified"
    for heading in (
        "## Constraint",
        "## Application Scope Vocabulary",
        "## App-Root Registry Assertions",
        "## Downstream Enforcement Context",
    ):
        assert heading in dcl["description"]


def test_phase_1_1_specs_carry_owner_decision_and_source_metadata() -> None:
    for spec_id in (ADR_ID, DCL_ID):
        spec = _spec(spec_id)
        assert "DELIB-20265227" in (spec["affected_by"] or "")
        assert "gtkb-ar-readiness-phase-1-1-governance-foundation-003.md" in (spec["source_paths"] or "")
        assert spec["testability"] == "structural"


def test_phase_1_1_approval_packets_validate_and_match_content() -> None:
    adr_packet = _packet(ADR_ID)
    dcl_packet = _packet(DCL_ID)

    assert adr_packet["artifact_type"] == "architecture_decision"
    assert dcl_packet["artifact_type"] == "design_constraint"
    assert "AUQ DELIB-20265227" in adr_packet["explicit_change_request"]
    assert "AUQ DELIB-20265227" in dcl_packet["explicit_change_request"]


def test_dcl_assertions_match_live_agent_red_registry_schema() -> None:
    dcl = _spec(DCL_ID)
    assertion_ids = {item["id"] for item in dcl["assertions_parsed"]}
    assert assertion_ids == {
        "DCL-APP-ROOT-MINIMIZATION-001.A1",
        "DCL-APP-ROOT-MINIMIZATION-001.A2",
        "DCL-APP-ROOT-MINIMIZATION-001.A3",
        "DCL-APP-ROOT-MINIMIZATION-001.A4",
        "DCL-APP-ROOT-MINIMIZATION-001.A5",
    }

    description = dcl["description"]
    assert "non-empty `name`, `type`, and `bucket`" in description
    assert "non-empty `path`, `kind`, and `bucket`" not in description

    entries = _registry_entries()
    for entry in entries:
        assert entry.get("name")
        assert entry.get("type")
        assert entry.get("bucket")
        if entry["bucket"] == "A":
            assert entry.get("purpose")
        elif entry["bucket"] == "B":
            assert entry.get("tool")
            assert entry.get("justification")
        else:
            raise AssertionError(f"unexpected app-root bucket {entry['bucket']!r} for {entry['name']}")


def test_phase_1_1_did_not_modify_agent_red_app_root_source_or_config() -> None:
    approved_app_root_evidence = {APP_REGISTRY}
    current_files = {path for path in APP_ROOT.rglob("*") if path.is_file()}
    assert approved_app_root_evidence <= current_files

    dcl = _spec(DCL_ID)
    assert "work-subject write guard" in dcl["description"]
    assert "does not implement" in dcl["description"]
