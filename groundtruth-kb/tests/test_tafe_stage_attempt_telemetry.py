"""Spec-derived tests for the TAFE per-stage-attempt telemetry substrate (WI-4504).

Covers SPEC-TAFE-R6 (full per-stage-attempt telemetry persistence), and the
SPEC-TAFE-R3/R4/R2 fields the record references (failure/recovery, dispatch
decision, lease context). The slice is a pure recording substrate: these tests
also assert it exposes no detection / aggregation / dashboard surface (those are
the later WI-4505 / WI-4506 slices).
"""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def _create_stage(service: TypedArtifactFlowService) -> dict:
    definition = service.create_flow_definition(
        id="FLOW-TELEMETRY-TEST",
        flow_type="implementation",
        name="Telemetry test flow",
        stages=["propose", "review"],
        required_roles={"propose": "prime-builder", "review": "loyal-opposition"},
        changed_by="test",
        change_reason="telemetry test setup",
        source_spec_ids=["SPEC-TAFE-R6", "SPEC-TAFE-R3", "SPEC-TAFE-R4", "SPEC-TAFE-R2"],
    )
    flow = service.create_flow_instance(
        id="FLOWINST-TELEMETRY-001",
        flow_definition_id=definition["id"],
        subject_type="bridge_thread",
        subject_id="gtkb-tafe-stage-attempt-telemetry",
        changed_by="test",
        change_reason="start telemetry test flow",
    )
    return service.create_stage_instance(
        id="STAGEINST-TELEMETRY-001",
        flow_instance_id=flow["id"],
        stage_id="review",
        stage_index=1,
        required_role="loyal-opposition",
        changed_by="test",
        change_reason="create telemetry test stage",
    )


_REQUIRED_R6_COLUMNS = {
    "id",
    "version",
    "flow_instance_id",
    "stage_instance_id",
    "attempt_number",
    "agent_harness_id",
    "agent_session_id",
    "agent_context_id",
    "model_identifier",
    "provider",
    "dispatch_decision",
    "lease_id",
    "lease_lifecycle",
    "started_at",
    "completed_at",
    "duration_ms",
    "token_count",
    "cost",
    "outcome",
    "verdict",
    "test_summary",
    "failure_class",
    "cleanup_result",
    "recovery_actions",
    "artifact_links",
    "status",
    "metadata",
    "changed_by",
    "changed_at",
    "change_reason",
}


def test_stage_attempt_telemetry_schema_has_columns_view_and_indexes(tmp_path) -> None:
    """SPEC-TAFE-R6: a fresh MemBase creates the telemetry table, the full R6
    column set, the latest-version current view, and the supporting indexes."""
    db, _ = _service(tmp_path)
    try:
        conn = db._get_conn()
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        views = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(stage_attempt_telemetry)").fetchall()}
        indexes = {row["name"] for row in conn.execute("PRAGMA index_list(stage_attempt_telemetry)").fetchall()}
    finally:
        db.close()

    assert "stage_attempt_telemetry" in tables
    assert "current_stage_attempt_telemetry" in views
    assert columns >= _REQUIRED_R6_COLUMNS
    assert {
        "idx_stage_attempt_telemetry_id_version",
        "idx_stage_attempt_telemetry_flow",
        "idx_stage_attempt_telemetry_stage",
        "idx_stage_attempt_telemetry_outcome",
        "idx_stage_attempt_telemetry_failure_class",
    } <= indexes


def test_stage_attempt_telemetry_round_trips_versions_view_and_json(tmp_path) -> None:
    """SPEC-TAFE-R6/R3/R4/R2: the full field set persists append-only, the
    current view returns the latest version, and the JSON columns round-trip via
    the ``*_parsed`` accessors."""
    db, service = _service(tmp_path)
    try:
        stage = _create_stage(service)
        first = service.record_stage_attempt_telemetry(
            id="TELEM-001",
            flow_instance_id=stage["flow_instance_id"],
            stage_instance_id=stage["id"],
            changed_by="test",
            change_reason="record first attempt",
            attempt_number=1,
            agent_harness_id="B",
            agent_session_id="session-001",
            agent_context_id="ctx-001",
            model_identifier="claude-opus-4-8",
            provider="anthropic",
            dispatch_decision={"selected": "B", "rationale": "precedence"},
            lease_id="LEASE-001",
            lease_lifecycle={"acquired_at": "2026-06-13T04:00:00Z", "released_at": None},
            started_at="2026-06-13T04:00:00Z",
            completed_at="2026-06-13T04:05:00Z",
            duration_ms=300000,
            token_count=12345,
            cost=0.42,
            outcome="success",
            verdict="VERIFIED",
            test_summary={"passed": 10, "failed": 0},
            cleanup_result="clean",
            recovery_actions=["none"],
            artifact_links=["bridge/x-001.md"],
            metadata={"source": "test"},
        )
        second = service.record_stage_attempt_telemetry(
            id="TELEM-001",
            flow_instance_id=stage["flow_instance_id"],
            stage_instance_id=stage["id"],
            changed_by="test",
            change_reason="record second attempt observation",
            attempt_number=2,
            outcome="failure",
            failure_class="timeout",
            recovery_actions=["retry", "escalate"],
            metadata={"source": "test", "v": 2},
        )

        assert first["version"] == 1
        assert second["version"] == 2

        current = service.get_stage_attempt_telemetry("TELEM-001")
        assert current is not None
        assert current["version"] == 2
        assert current["outcome"] == "failure"
        assert current["failure_class"] == "timeout"
        assert current["recovery_actions_parsed"] == ["retry", "escalate"]
        assert current["metadata_parsed"] == {"source": "test", "v": 2}

        history = service.get_stage_attempt_telemetry_history("TELEM-001")
        assert [r["version"] for r in history] == [2, 1]
        first_hist = history[1]
        assert first_hist["dispatch_decision_parsed"] == {"selected": "B", "rationale": "precedence"}
        assert first_hist["lease_lifecycle_parsed"]["acquired_at"] == "2026-06-13T04:00:00Z"
        assert first_hist["test_summary_parsed"] == {"passed": 10, "failed": 0}
        assert first_hist["artifact_links_parsed"] == ["bridge/x-001.md"]
        assert first_hist["cost"] == 0.42
        assert first_hist["token_count"] == 12345
        assert first_hist["lease_id"] == "LEASE-001"
    finally:
        db.close()


def test_stage_attempt_telemetry_list_filters(tmp_path) -> None:
    """SPEC-TAFE-R6: list filters by flow_instance_id, outcome, and failure_class."""
    db, service = _service(tmp_path)
    try:
        stage = _create_stage(service)
        service.record_stage_attempt_telemetry(
            id="TELEM-A",
            flow_instance_id=stage["flow_instance_id"],
            stage_instance_id=stage["id"],
            changed_by="test",
            change_reason="record A",
            outcome="success",
        )
        service.record_stage_attempt_telemetry(
            id="TELEM-B",
            flow_instance_id=stage["flow_instance_id"],
            stage_instance_id=stage["id"],
            changed_by="test",
            change_reason="record B",
            outcome="failure",
            failure_class="timeout",
        )

        flow_rows = service.list_stage_attempt_telemetry(flow_instance_id=stage["flow_instance_id"])
        assert sorted(r["id"] for r in flow_rows) == ["TELEM-A", "TELEM-B"]
        assert [r["id"] for r in service.list_stage_attempt_telemetry(outcome="failure")] == ["TELEM-B"]
        assert [r["id"] for r in service.list_stage_attempt_telemetry(failure_class="timeout")] == ["TELEM-B"]
        assert [r["id"] for r in service.list_stage_attempt_telemetry(outcome="success")] == ["TELEM-A"]
    finally:
        db.close()


def test_stage_attempt_telemetry_requires_known_stage_instance(tmp_path) -> None:
    """SPEC-TAFE-R6: referential integrity — stage_instance_id must exist
    (mirrors insert_stage_lease)."""
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError, match="unknown stage_instance_id"):
            service.record_stage_attempt_telemetry(
                id="TELEM-BAD",
                flow_instance_id="FLOWINST-MISSING",
                stage_instance_id="STAGEINST-MISSING",
                changed_by="test",
                change_reason="missing stage",
            )
    finally:
        db.close()


def test_stage_attempt_telemetry_validates_required_fields(tmp_path) -> None:
    """The recording service rejects empty required identifiers."""
    db, service = _service(tmp_path)
    try:
        stage = _create_stage(service)
        bad_cases = [
            {"id": "", "flow_instance_id": stage["flow_instance_id"], "stage_instance_id": stage["id"]},
            {"id": "TELEM-X", "flow_instance_id": "", "stage_instance_id": stage["id"]},
            {"id": "TELEM-X", "flow_instance_id": stage["flow_instance_id"], "stage_instance_id": ""},
        ]
        for case in bad_cases:
            with pytest.raises(ValueError):
                service.record_stage_attempt_telemetry(changed_by="test", change_reason="bad", **case)
    finally:
        db.close()


def test_telemetry_slice_exposes_only_recording_surface() -> None:
    """WI-4504 bounding: only a recording substrate is added. No stuck-flow
    detection (WI-4505), aggregation/rollup, or dashboard (WI-4506) method is
    exposed; the public telemetry API surface is exactly the four record/read
    methods on both the DB and the service."""
    svc_methods = {
        name for name in dir(TypedArtifactFlowService) if "stage_attempt_telemetry" in name and not name.startswith("_")
    }
    assert svc_methods == {
        "record_stage_attempt_telemetry",
        "get_stage_attempt_telemetry",
        "get_stage_attempt_telemetry_history",
        "list_stage_attempt_telemetry",
    }
    db_methods = {name for name in dir(KnowledgeDB) if "stage_attempt_telemetry" in name and not name.startswith("_")}
    assert db_methods == {
        "insert_stage_attempt_telemetry",
        "get_stage_attempt_telemetry",
        "get_stage_attempt_telemetry_history",
        "list_stage_attempt_telemetry",
    }
    forbidden = ("detect", "aggregate", "rollup", "dashboard", "stuck", "diagnos", "kpi")
    for name in svc_methods | db_methods:
        assert not any(bad in name.lower() for bad in forbidden), name
