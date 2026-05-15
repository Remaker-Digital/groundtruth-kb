"""Tests for scripts/assertion_retirement_workflow.py (Slice 3 IP-2 / IP-4b).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md``
(Codex GO at -008) and ``SPEC-1662 (GOV-18: Assertion Quality Standard)`` retirement flow.

Tests are deterministic: fixture triage dirs and in-memory SQLite groundtruth.db.
Each test exercises one observable behavior of the retirement workflow:

- candidate enumeration (review-candidates)
- AUQ question envelope construction (ask)
- packet validation (apply-decision input gating)
- retire refusal pending governed follow-on bridge
- decision record persistence for accept/keep paths
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "assertion_retirement_workflow.py"


@pytest.fixture(scope="module")
def retirement_module():
    """Load assertion_retirement_workflow.py without executing main()."""
    spec = importlib.util.spec_from_file_location("assertion_retirement_workflow", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_category(triage_dir: Path, record: dict[str, Any]) -> Path:
    categories_dir = triage_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    target = categories_dir / f"{record['assertion_id']}.json"
    target.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return target


def _make_chronic_record(
    assertion_id: str,
    spec_id: str,
    description: str = "stub assertion",
    spec_status: str = "implemented",
) -> dict[str, Any]:
    return {
        "assertion_id": assertion_id,
        "spec_id": spec_id,
        "spec_status": spec_status,
        "assertion_index": 0,
        "description": description,
        "category": "chronic_noise",
        "rationale": "5 consecutive FAIL runs",
        "confidence": 0.9,
        "latest_passed": False,
        "latest_detail": "still failing",
        "history_length": 5,
        "categorized_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }


def _make_groundtruth_db(tmp_path: Path, spec_id: str, *, status: str = "implemented") -> Path:
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE specifications (
                id TEXT,
                version INTEGER,
                status TEXT,
                title TEXT,
                changed_by TEXT,
                changed_at TEXT,
                change_reason TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO specifications (id, version, status, title, changed_by, changed_at, change_reason) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                spec_id,
                1,
                status,
                "fixture spec",
                "fixture",
                dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "fixture init",
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _make_packet(
    tmp_path: Path,
    assertion_id: str,
    decision: str,
    *,
    tool: str = "AskUserQuestion",
    approved_by: str = "owner",
) -> Path:
    packet = {
        "tool": tool,
        "assertion_id": assertion_id,
        "decision": decision,
        "approved_by": approved_by,
        "approved_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }
    path = tmp_path / f"packet-{assertion_id}.json"
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _transition_marker(spec_id: str, from_status: str, to_status: str, version: int) -> str:
    """Canonical formal-packet full_content transition marker per REVISED-2 F1."""
    return f"spec_id={spec_id};from_status={from_status};to_status={to_status};current_version={version}"


def _make_formal_packet(
    tmp_path: Path,
    artifact_id: str,
    full_content: str,
    *,
    artifact_type: str = "governance",
    action: str = "retire",
    approval_mode: str = "approve",
    approved_by: str = "owner",
    presented_to_user: bool = True,
    transcript_captured: bool = True,
    explicit_change_request: str = "Retire spec via assertion triage workflow",
    omit_field: str | None = None,
) -> Path:
    """Construct a formal-artifact approval packet file for retire-path tests."""
    import hashlib
    content_sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    packet: dict[str, Any] = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "action": action,
        "source_ref": "test://fixture",
        "full_content": full_content,
        "full_content_sha256": content_sha,
        "approval_mode": approval_mode,
        "presented_to_user": presented_to_user,
        "transcript_captured": transcript_captured,
        "explicit_change_request": explicit_change_request,
        "changed_by": "test",
        "change_reason": "test fixture",
        "approved_by": approved_by,
    }
    if omit_field is not None and omit_field in packet:
        del packet[omit_field]
    path = tmp_path / f"formal-packet-{artifact_id}.json"
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _make_kb_with_spec(
    tmp_path: Path,
    spec_id: str,
    *,
    spec_type: str = "governance",
    status: str = "specified",
) -> Path:
    """Construct a fixture groundtruth.db using KnowledgeDB.insert_spec.

    Required for tests that exercise _retire_spec, which calls KnowledgeDB.get_spec
    and KnowledgeDB.update_spec internally. Returns the groundtruth.db path.
    """
    import sys as _sys
    db_path = tmp_path / "groundtruth.db"
    _sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB
    db = KnowledgeDB(str(db_path))
    try:
        db.insert_spec(
            id=spec_id,
            title="fixture spec for retirement",
            description="Test fixture for governed spec retirement",
            type=spec_type,
            status=status,
            changed_by="fixture",
            change_reason="fixture init for retire test",
        )
    finally:
        db.close()
    return db_path


# ---------------------------------------------------------------------------
# review-candidates
# ---------------------------------------------------------------------------


def test_review_candidates_empty_triage_dir(retirement_module, tmp_path):
    """An empty triage dir produces zero candidates with valid markdown shell."""
    result = retirement_module.review_candidates(tmp_path)
    assert result["total_candidates"] == 0
    assert result["shown"] == 0
    assert "Chronic Noise Retirement Candidates" in result["markdown"]


def test_review_candidates_lists_only_chronic_noise(retirement_module, tmp_path):
    """Only chronic_noise records appear; healthy/flaky records are filtered out."""
    _write_category(tmp_path, _make_chronic_record("aid-1", "SPEC-100"))
    _write_category(
        tmp_path,
        {
            **_make_chronic_record("aid-2", "SPEC-200"),
            "category": "healthy",
        },
    )
    _write_category(tmp_path, _make_chronic_record("aid-3", "SPEC-300"))
    result = retirement_module.review_candidates(tmp_path)
    assert result["total_candidates"] == 2
    assertion_ids = [c["assertion_id"] for c in result["candidates"]]
    assert assertion_ids == ["aid-1", "aid-3"]


def test_review_candidates_respects_max_show(retirement_module, tmp_path):
    """max_show caps the candidates returned and the markdown 'Showing top N' line."""
    for i in range(5):
        _write_category(tmp_path, _make_chronic_record(f"aid-{i}", f"SPEC-{i}"))
    result = retirement_module.review_candidates(tmp_path, max_show=2)
    assert result["total_candidates"] == 5
    assert result["shown"] == 2
    assert len(result["candidates"]) == 2
    assert "Showing top 2" in result["markdown"]


# ---------------------------------------------------------------------------
# ask (AUQ envelope construction)
# ---------------------------------------------------------------------------


def test_build_question_envelope_for_chronic_assertion(retirement_module, tmp_path):
    """A chronic_noise record yields an AskUserQuestion envelope with 3 options."""
    _write_category(tmp_path, _make_chronic_record("aid-99", "SPEC-999"))
    envelope = retirement_module.build_question_envelope("aid-99", tmp_path)
    assert envelope["tool"] == "AskUserQuestion"
    assert envelope["assertion_id"] == "aid-99"
    assert envelope["spec_id"] == "SPEC-999"
    options = envelope["question"]["options"]
    assert len(options) == 3
    labels = {o["label"] for o in options}
    assert "Retire the assertion" in labels
    assert "Accept the failure as expected" in labels
    assert "Keep and schedule repair" in labels


def test_build_question_envelope_rejects_non_chronic_category(retirement_module, tmp_path):
    """A non-chronic category returns an explicit error with the observed category."""
    _write_category(
        tmp_path,
        {**_make_chronic_record("aid-flaky", "SPEC-100"), "category": "flaky"},
    )
    envelope = retirement_module.build_question_envelope("aid-flaky", tmp_path)
    assert "error" in envelope
    assert "flaky" in envelope["error"]


def test_build_question_envelope_rejects_missing_assertion(retirement_module, tmp_path):
    """An unknown assertion_id returns an error message."""
    envelope = retirement_module.build_question_envelope("aid-missing", tmp_path)
    assert "error" in envelope
    assert "aid-missing" in envelope["error"]


# ---------------------------------------------------------------------------
# _validate_packet (apply-decision input gating)
# ---------------------------------------------------------------------------


def test_validate_packet_rejects_missing_fields(retirement_module, tmp_path):
    """Packet without a required field raises SystemExit citing 'missing'."""
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"tool": "AskUserQuestion"}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        retirement_module._validate_packet(path)
    assert "missing required" in str(exc.value).lower()


def test_validate_packet_rejects_wrong_tool(retirement_module, tmp_path):
    """Packet with tool != AskUserQuestion is rejected."""
    path = _make_packet(tmp_path, "aid-1", "retire", tool="OtherTool")
    with pytest.raises(SystemExit) as exc:
        retirement_module._validate_packet(path)
    assert "AskUserQuestion" in str(exc.value)


def test_validate_packet_rejects_non_owner_approver(retirement_module, tmp_path):
    """Packet approved_by != 'owner' is rejected."""
    path = _make_packet(tmp_path, "aid-1", "retire", approved_by="prime-builder")
    with pytest.raises(SystemExit) as exc:
        retirement_module._validate_packet(path)
    assert "owner" in str(exc.value)


def test_validate_packet_rejects_invalid_decision(retirement_module, tmp_path):
    """Packet decision outside {retire, accept, keep} is rejected."""
    path = _make_packet(tmp_path, "aid-1", "delete")
    with pytest.raises(SystemExit) as exc:
        retirement_module._validate_packet(path)
    assert "decision must be one of" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# apply_decision: retire path mutates spec; non-retire paths don't
# ---------------------------------------------------------------------------


def test_apply_decision_retire_refuses_without_formal_packet(retirement_module, tmp_path):
    """decision='retire' without --formal-approval-packet raises SystemExit naming the missing flag."""
    spec_id = "SPEC-CHRONIC-1"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-1", spec_id))
    packet_path = _make_packet(tmp_path, "aid-1", "retire")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path,
            triage_dir=tmp_path,
            assertion_id="aid-1",
            decision="retire",
            packet_path=packet_path,
        )
    assert "retire decision requires --formal-approval-packet" in str(exc.value)


def test_apply_decision_retire_promotes_spec_to_retired_via_governed_api(retirement_module, tmp_path):
    """decision='retire' with valid AUQ + formal packets inserts a new spec row at status='retired'."""
    spec_id = "SPEC-CHRONIC-2"
    _make_kb_with_spec(tmp_path, spec_id, spec_type="governance", status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-2", spec_id))
    packet_path = _make_packet(tmp_path, "aid-2", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, artifact_type="governance")

    result = retirement_module.apply_decision(
        project_root=tmp_path,
        triage_dir=tmp_path,
        assertion_id="aid-2",
        decision="retire",
        packet_path=packet_path,
        formal_packet_path=formal_path,
    )

    assert result["spec_update_result"] is not None
    assert result["spec_update_result"]["new_status"] == "retired"
    assert result["spec_update_result"]["new_version"] == 2

    conn = sqlite3.connect(str(tmp_path / "groundtruth.db"))
    try:
        row = conn.execute(
            "SELECT status, version FROM specifications WHERE id = ? AND version = 2",
            (spec_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row == ("retired", 2)


def test_apply_decision_retire_calls_update_spec_with_expected_kwargs(retirement_module, tmp_path):
    """Positive path: verify changed_by + change_reason recorded in the new spec row."""
    spec_id = "SPEC-CHRONIC-3"
    _make_kb_with_spec(tmp_path, spec_id, spec_type="governance", status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-3", spec_id))
    packet_path = _make_packet(tmp_path, "aid-3", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, artifact_type="governance")

    retirement_module.apply_decision(
        project_root=tmp_path,
        triage_dir=tmp_path,
        assertion_id="aid-3",
        decision="retire",
        packet_path=packet_path,
        formal_packet_path=formal_path,
    )

    conn = sqlite3.connect(str(tmp_path / "groundtruth.db"))
    try:
        row = conn.execute(
            "SELECT changed_by, change_reason FROM specifications WHERE id = ? AND version = 2",
            (spec_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == "assertion-retirement-workflow@2.0"
    assert "Retired via assertion_retirement_workflow.py for assertion aid-3" in row[1]
    assert "chronic_noise category" in row[1]


def test_apply_decision_retire_rejects_missing_formal_packet_file(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-4"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-4", spec_id))
    packet_path = _make_packet(tmp_path, "aid-4", "retire")
    nonexistent = tmp_path / "does-not-exist.json"

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-4",
            decision="retire", packet_path=packet_path, formal_packet_path=nonexistent,
        )
    assert "Formal-approval packet file not found" in str(exc.value)


def test_apply_decision_retire_rejects_invalid_formal_packet_json(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-5"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-5", spec_id))
    packet_path = _make_packet(tmp_path, "aid-5", "retire")
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-5",
            decision="retire", packet_path=packet_path, formal_packet_path=bad_json,
        )
    assert "not valid JSON" in str(exc.value)


def test_apply_decision_retire_rejects_formal_packet_missing_fields(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-6"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-6", spec_id))
    packet_path = _make_packet(tmp_path, "aid-6", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, omit_field="action")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-6",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "missing required fields" in str(exc.value)


def test_apply_decision_retire_rejects_wrong_artifact_type(retirement_module, tmp_path):
    """F1 binding companion: packet artifact_type != spec's type."""
    spec_id = "SPEC-CHRONIC-7"
    _make_kb_with_spec(tmp_path, spec_id, spec_type="governance", status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-7", spec_id))
    packet_path = _make_packet(tmp_path, "aid-7", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, artifact_type="design_constraint")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-7",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "artifact_type mismatch" in str(exc.value)


def test_apply_decision_retire_rejects_packet_presented_to_user_false(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-8"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-8", spec_id))
    packet_path = _make_packet(tmp_path, "aid-8", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, presented_to_user=False)

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-8",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "presented_to_user" in str(exc.value)


def test_apply_decision_retire_rejects_packet_transcript_captured_false(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-9"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-9", spec_id))
    packet_path = _make_packet(tmp_path, "aid-9", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, transcript_captured=False)

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-9",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "transcript_captured" in str(exc.value)


def test_apply_decision_retire_rejects_packet_invalid_approval_mode(retirement_module, tmp_path):
    spec_id = "SPEC-CHRONIC-10"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-10", spec_id))
    packet_path = _make_packet(tmp_path, "aid-10", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, approval_mode="custom-invalid")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-10",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "approval_mode" in str(exc.value)


def test_apply_decision_retire_rejects_formal_packet_wrong_artifact_id(retirement_module, tmp_path):
    """F1 binding: packet artifact_id != target spec_id."""
    spec_id = "SPEC-CHRONIC-11"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-11", spec_id))
    packet_path = _make_packet(tmp_path, "aid-11", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, "SPEC-OTHER", marker, artifact_type="governance")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-11",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "artifact_id mismatch" in str(exc.value)


def test_apply_decision_retire_rejects_formal_packet_wrong_action(retirement_module, tmp_path):
    """F1 binding: packet action != 'retire'."""
    spec_id = "SPEC-CHRONIC-12"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-12", spec_id))
    packet_path = _make_packet(tmp_path, "aid-12", "retire")
    marker = _transition_marker(spec_id, "specified", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, action="create")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-12",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "action mismatch" in str(exc.value)


def test_apply_decision_retire_rejects_formal_packet_wrong_transition_marker(retirement_module, tmp_path):
    """F1 binding: packet full_content does not match canonical transition marker."""
    spec_id = "SPEC-CHRONIC-13"
    _make_kb_with_spec(tmp_path, spec_id, status="specified")
    _write_category(tmp_path, _make_chronic_record("aid-13", spec_id))
    packet_path = _make_packet(tmp_path, "aid-13", "retire")
    wrong_marker = _transition_marker(spec_id, "specified", "superseded", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, wrong_marker, artifact_type="governance")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-13",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "full_content does not match expected transition marker" in str(exc.value)


def test_apply_decision_retire_refuses_already_retired_spec(retirement_module, tmp_path):
    """Spec already at status='retired' refuses re-retirement."""
    spec_id = "SPEC-CHRONIC-14"
    _make_kb_with_spec(tmp_path, spec_id, status="retired")
    _write_category(tmp_path, _make_chronic_record("aid-14", spec_id))
    packet_path = _make_packet(tmp_path, "aid-14", "retire")
    marker = _transition_marker(spec_id, "retired", "retired", 1)
    formal_path = _make_formal_packet(tmp_path, spec_id, marker, artifact_type="governance")

    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path, triage_dir=tmp_path, assertion_id="aid-14",
            decision="retire", packet_path=packet_path, formal_packet_path=formal_path,
        )
    assert "already retired" in str(exc.value)


def test_apply_decision_accept_does_not_touch_spec(retirement_module, tmp_path):
    """decision='accept' records the decision but does NOT mutate specifications."""
    spec_id = "SPEC-CHRONIC-2"
    _make_groundtruth_db(tmp_path, spec_id)
    _write_category(tmp_path, _make_chronic_record("aid-2", spec_id))
    packet_path = _make_packet(tmp_path, "aid-2", "accept")

    result = retirement_module.apply_decision(
        project_root=tmp_path,
        triage_dir=tmp_path,
        assertion_id="aid-2",
        decision="accept",
        packet_path=packet_path,
    )
    assert result["spec_update_result"] is None

    conn = sqlite3.connect(str(tmp_path / "groundtruth.db"))
    try:
        rows = conn.execute(
            "SELECT version, status FROM specifications WHERE id = ?",
            (spec_id,),
        ).fetchall()
    finally:
        conn.close()
    # Only the fixture row at version 1 with status='implemented' should remain.
    assert rows == [(1, "implemented")]


def test_apply_decision_keep_does_not_touch_spec(retirement_module, tmp_path):
    """decision='keep' records the decision but does NOT mutate specifications."""
    spec_id = "SPEC-CHRONIC-3"
    _make_groundtruth_db(tmp_path, spec_id)
    _write_category(tmp_path, _make_chronic_record("aid-3", spec_id))
    packet_path = _make_packet(tmp_path, "aid-3", "keep")

    result = retirement_module.apply_decision(
        project_root=tmp_path,
        triage_dir=tmp_path,
        assertion_id="aid-3",
        decision="keep",
        packet_path=packet_path,
    )
    assert result["spec_update_result"] is None

    conn = sqlite3.connect(str(tmp_path / "groundtruth.db"))
    try:
        rows = conn.execute(
            "SELECT version, status FROM specifications WHERE id = ?",
            (spec_id,),
        ).fetchall()
    finally:
        conn.close()
    assert rows == [(1, "implemented")]


def test_apply_decision_rejects_packet_assertion_id_mismatch(retirement_module, tmp_path):
    """Packet whose assertion_id != CLI assertion_id is rejected."""
    spec_id = "SPEC-CHRONIC-4"
    _make_groundtruth_db(tmp_path, spec_id)
    _write_category(tmp_path, _make_chronic_record("aid-4", spec_id))
    # Build a packet for a DIFFERENT assertion_id.
    packet_path = _make_packet(tmp_path, "aid-other", "retire")
    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path,
            triage_dir=tmp_path,
            assertion_id="aid-4",
            decision="retire",
            packet_path=packet_path,
        )
    assert "assertion_id mismatch" in str(exc.value).lower()


def test_apply_decision_rejects_packet_decision_mismatch(retirement_module, tmp_path):
    """Packet whose decision != CLI decision is rejected."""
    spec_id = "SPEC-CHRONIC-5"
    _make_groundtruth_db(tmp_path, spec_id)
    _write_category(tmp_path, _make_chronic_record("aid-5", spec_id))
    # Packet says 'accept' but CLI says 'retire'.
    packet_path = _make_packet(tmp_path, "aid-5", "accept")
    with pytest.raises(SystemExit) as exc:
        retirement_module.apply_decision(
            project_root=tmp_path,
            triage_dir=tmp_path,
            assertion_id="aid-5",
            decision="retire",
            packet_path=packet_path,
        )
    assert "decision mismatch" in str(exc.value).lower()
