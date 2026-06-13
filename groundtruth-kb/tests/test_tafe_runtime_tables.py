from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def _define_flow(service: TypedArtifactFlowService) -> dict:
    return service.create_flow_definition(
        id="FLOW-IMPLEMENTATION",
        flow_type="implementation",
        name="Implementation flow",
        stages=["propose", "review", "implement", "verify"],
        required_roles={
            "propose": "prime-builder",
            "review": "loyal-opposition",
            "implement": "prime-builder",
            "verify": "loyal-opposition",
        },
        changed_by="test",
        change_reason="runtime test setup",
        source_spec_ids=["SPEC-TAFE-R1", "SPEC-TAFE-R7"],
    )


def test_runtime_schema_contains_phase_0_tables_and_views(tmp_path) -> None:
    db, _ = _service(tmp_path)
    try:
        conn = db._get_conn()
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        views = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
        flow_columns = {row["name"] for row in conn.execute("PRAGMA table_info(flow_instances)").fetchall()}
        stage_columns = {row["name"] for row in conn.execute("PRAGMA table_info(stage_instances)").fetchall()}
        event_columns = {row["name"] for row in conn.execute("PRAGMA table_info(flow_events)").fetchall()}
        artifact_columns = {row["name"] for row in conn.execute("PRAGMA table_info(flow_artifacts)").fetchall()}
    finally:
        db.close()

    assert {"flow_instances", "stage_instances", "flow_events", "flow_artifacts"} <= tables
    assert {"current_flow_instances", "current_stage_instances"} <= views
    assert {
        "id",
        "version",
        "flow_definition_id",
        "flow_definition_version",
        "flow_type",
        "subject_type",
        "subject_id",
        "status",
        "current_stage_instance_id",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    } <= flow_columns
    assert {
        "id",
        "version",
        "flow_instance_id",
        "stage_id",
        "stage_index",
        "required_role",
        "status",
        "claim_status",
        "claimed_by_harness_id",
        "claimed_by_session_id",
        "metadata",
    } <= stage_columns
    assert {"id", "flow_instance_id", "stage_instance_id", "event_type", "event_payload"} <= event_columns
    assert {
        "id",
        "flow_instance_id",
        "stage_instance_id",
        "artifact_type",
        "artifact_ref",
        "relationship",
        "metadata",
    } <= artifact_columns


def test_runtime_service_round_trips_current_history_events_and_artifacts(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        definition = _define_flow(service)
        first_instance = service.create_flow_instance(
            id="FLOWINST-001",
            flow_definition_id=definition["id"],
            subject_type="bridge_thread",
            subject_id="gtkb-tafe-runtime-tables-schema",
            status="created",
            metadata={"bridge_id": "gtkb-tafe-runtime-tables-schema"},
            changed_by="test",
            change_reason="start runtime test flow",
        )
        stage = service.create_stage_instance(
            id="STAGEINST-001",
            flow_instance_id=first_instance["id"],
            stage_id="review",
            stage_index=1,
            required_role="loyal-opposition",
            status="pending",
            metadata={"never_self_review": True},
            changed_by="test",
            change_reason="create review stage",
        )
        second_instance = service.create_flow_instance(
            id="FLOWINST-001",
            flow_definition_id=definition["id"],
            subject_type="bridge_thread",
            subject_id="gtkb-tafe-runtime-tables-schema",
            status="in_progress",
            current_stage_instance_id=stage["id"],
            metadata={"bridge_id": "gtkb-tafe-runtime-tables-schema", "stage": "review"},
            changed_by="test",
            change_reason="advance to review stage",
        )
        second_stage = service.create_stage_instance(
            id="STAGEINST-001",
            flow_instance_id=first_instance["id"],
            stage_id="review",
            stage_index=1,
            required_role="loyal-opposition",
            status="in_progress",
            claim_status="claimable",
            metadata={"never_self_review": True, "claim_ready": True},
            changed_by="test",
            change_reason="mark stage claimable",
        )
        event = service.record_flow_event(
            id="FLOWEVENT-001",
            flow_instance_id=first_instance["id"],
            stage_instance_id=stage["id"],
            event_type="stage_created",
            event_payload={"stage_id": "review"},
            changed_by="test",
            change_reason="record stage creation",
        )
        artifact = service.link_flow_artifact(
            id="FLOWART-001",
            flow_instance_id=first_instance["id"],
            stage_instance_id=stage["id"],
            artifact_type="bridge",
            artifact_ref="bridge/gtkb-tafe-runtime-tables-schema-001.md",
            relationship="proposal",
            metadata={"authority": "bridge-index"},
            changed_by="test",
            change_reason="link proposal artifact",
        )

        assert first_instance["version"] == 1
        assert second_instance["version"] == 2
        assert service.get_flow_instance("FLOWINST-001")["status"] == "in_progress"
        assert [row["version"] for row in service.get_flow_instance_history("FLOWINST-001")] == [2, 1]
        assert service.list_flow_instances(flow_definition_id=definition["id"])[0]["metadata_parsed"] == {
            "bridge_id": "gtkb-tafe-runtime-tables-schema",
            "stage": "review",
        }

        assert stage["version"] == 1
        assert second_stage["version"] == 2
        assert service.get_stage_instance("STAGEINST-001")["claim_status"] == "claimable"
        assert service.get_stage_instance("STAGEINST-001")["metadata_parsed"] == {
            "never_self_review": True,
            "claim_ready": True,
        }
        assert [row["version"] for row in service.get_stage_instance_history("STAGEINST-001")] == [2, 1]
        assert [row["id"] for row in service.list_stage_instances(flow_instance_id="FLOWINST-001")] == ["STAGEINST-001"]

        assert event["event_payload_parsed"] == {"stage_id": "review"}
        assert [row["id"] for row in service.list_flow_events(flow_instance_id="FLOWINST-001")] == ["FLOWEVENT-001"]
        assert artifact["metadata_parsed"] == {"authority": "bridge-index"}
        assert [row["artifact_ref"] for row in service.list_flow_artifacts(artifact_type="bridge")] == [
            "bridge/gtkb-tafe-runtime-tables-schema-001.md"
        ]
    finally:
        db.close()


def test_runtime_service_rejects_unanchored_rows(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError, match="unknown flow_definition_id"):
            service.create_flow_instance(
                id="FLOWINST-BAD",
                flow_definition_id="FLOW-MISSING",
                subject_type="bridge_thread",
                subject_id="missing",
                changed_by="test",
                change_reason="missing definition",
            )

        definition = _define_flow(service)
        flow = service.create_flow_instance(
            id="FLOWINST-OK",
            flow_definition_id=definition["id"],
            subject_type="bridge_thread",
            subject_id="gtkb-tafe-runtime-tables-schema",
            changed_by="test",
            change_reason="valid flow",
        )

        with pytest.raises(ValueError, match="unknown flow_instance_id"):
            service.create_stage_instance(
                id="STAGEINST-BAD",
                flow_instance_id="FLOWINST-MISSING",
                stage_id="review",
                stage_index=1,
                required_role="loyal-opposition",
                changed_by="test",
                change_reason="missing flow instance",
            )

        with pytest.raises(ValueError, match="non-negative"):
            service.create_stage_instance(
                id="STAGEINST-BAD",
                flow_instance_id=flow["id"],
                stage_id="review",
                stage_index=-1,
                required_role="loyal-opposition",
                changed_by="test",
                change_reason="bad stage index",
            )
    finally:
        db.close()
