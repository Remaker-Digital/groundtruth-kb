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


def test_apply_decision_retire_refuses_pending_governed_path(retirement_module, tmp_path):
    """decision='retire' raises SystemExit naming the governed follow-on bridge."""
    spec_id = "SPEC-CHRONIC-1"
    _make_groundtruth_db(tmp_path, spec_id)
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
    assert "gtkb-governed-spec-retirement-001" in str(exc.value)
    assert "refusing retire" in str(exc.value).lower()

    # No new specifications row was inserted (only the fixture row at version 1).
    conn = sqlite3.connect(str(tmp_path / "groundtruth.db"))
    try:
        rows = conn.execute(
            "SELECT version, status FROM specifications WHERE id = ?",
            (spec_id,),
        ).fetchall()
    finally:
        conn.close()
    assert rows == [(1, "implemented")]

    # No decision record was written (refusal aborts before write).
    decision_path = tmp_path / "decisions" / "aid-1.json"
    assert not decision_path.is_file()


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
