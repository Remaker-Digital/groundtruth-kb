from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def _define_flow(service: TypedArtifactFlowService) -> dict:
    return service.create_flow_definition(
        id="FLOW-LEASE-TEST",
        flow_type="implementation",
        name="Lease test flow",
        stages=["propose", "review"],
        required_roles={
            "propose": "prime-builder",
            "review": "loyal-opposition",
        },
        changed_by="test",
        change_reason="lease test setup",
        source_spec_ids=["SPEC-TAFE-R2", "SPEC-TAFE-R3", "SPEC-TAFE-R7"],
    )


def _create_stage(service: TypedArtifactFlowService) -> dict:
    definition = _define_flow(service)
    flow = service.create_flow_instance(
        id="FLOWINST-LEASE-001",
        flow_definition_id=definition["id"],
        subject_type="bridge_thread",
        subject_id="gtkb-tafe-stage-leases-schema",
        changed_by="test",
        change_reason="start lease test flow",
    )
    return service.create_stage_instance(
        id="STAGEINST-LEASE-001",
        flow_instance_id=flow["id"],
        stage_id="review",
        stage_index=1,
        required_role="loyal-opposition",
        changed_by="test",
        change_reason="create lease test stage",
    )


def test_stage_lease_schema_contains_required_columns_and_view(tmp_path) -> None:
    db, _ = _service(tmp_path)
    try:
        conn = db._get_conn()
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        views = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(stage_leases)").fetchall()}
        indexes = {row["name"] for row in conn.execute("PRAGMA index_list(stage_leases)").fetchall()}
    finally:
        db.close()

    assert "stage_leases" in tables
    assert "current_stage_leases" in views
    assert {
        "id",
        "version",
        "stage_instance_id",
        "holder_harness_id",
        "holder_session_id",
        "lease_status",
        "acquired_at",
        "heartbeat_at",
        "ttl_seconds",
        "expires_at",
        "released_at",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    } <= columns
    assert {
        "idx_stage_leases_id_version",
        "idx_stage_leases_stage",
        "idx_stage_leases_status",
        "idx_stage_leases_holder",
        "idx_stage_leases_heartbeat",
    } <= indexes


def test_stage_lease_service_round_trips_current_history_and_filters(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        stage = _create_stage(service)
        first = service.create_stage_lease(
            id="LEASE-001",
            stage_instance_id=stage["id"],
            holder_harness_id="A",
            holder_session_id="session-001",
            ttl_seconds=600,
            acquired_at="2026-06-13T04:00:00Z",
            heartbeat_at="2026-06-13T04:01:00Z",
            expires_at="2026-06-13T04:11:00Z",
            metadata={"source": "test"},
            changed_by="test",
            change_reason="create lease substrate row",
        )
        second = service.create_stage_lease(
            id="LEASE-001",
            stage_instance_id=stage["id"],
            holder_harness_id="A",
            holder_session_id="session-001",
            ttl_seconds=900,
            lease_status="observed",
            acquired_at="2026-06-13T04:00:00Z",
            heartbeat_at="2026-06-13T04:05:00Z",
            expires_at="2026-06-13T04:20:00Z",
            metadata={"source": "test", "version": 2},
            changed_by="test",
            change_reason="append observed lease state",
        )

        assert first["version"] == 1
        assert second["version"] == 2
        current = service.get_stage_lease("LEASE-001")
        assert current is not None
        assert current["lease_status"] == "observed"
        assert current["heartbeat_at"] == "2026-06-13T04:05:00Z"
        assert current["ttl_seconds"] == 900
        assert current["metadata_parsed"] == {"source": "test", "version": 2}
        assert [row["version"] for row in service.get_stage_lease_history("LEASE-001")] == [2, 1]
        assert [row["id"] for row in service.list_stage_leases(stage_instance_id=stage["id"])] == ["LEASE-001"]
        assert [row["id"] for row in service.list_stage_leases(lease_status="observed")] == ["LEASE-001"]
        assert [row["id"] for row in service.list_stage_leases(holder_harness_id="A")] == ["LEASE-001"]

        current_stage = service.get_stage_instance(stage["id"])
        assert current_stage is not None
        assert current_stage["claim_status"] == "unclaimed"
        assert current_stage["claimed_by_harness_id"] is None
        assert current_stage["claimed_by_session_id"] is None
    finally:
        db.close()


def test_stage_lease_service_rejects_unanchored_or_invalid_rows(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError, match="unknown stage_instance_id"):
            service.create_stage_lease(
                id="LEASE-BAD-STAGE",
                stage_instance_id="STAGEINST-MISSING",
                holder_harness_id="A",
                holder_session_id="session-001",
                ttl_seconds=600,
                changed_by="test",
                change_reason="missing stage",
            )

        stage = _create_stage(service)
        with pytest.raises(ValueError, match="ttl_seconds must be positive"):
            service.create_stage_lease(
                id="LEASE-BAD-TTL",
                stage_instance_id=stage["id"],
                holder_harness_id="A",
                holder_session_id="session-001",
                ttl_seconds=0,
                changed_by="test",
                change_reason="bad ttl",
            )
    finally:
        db.close()


def test_stage_lease_claim_release_and_heartbeat_enforce_single_holder(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        stage = _create_stage(service)

        claimed = service.claim_stage_lease(
            stage_instance_id=stage["id"],
            holder_harness_id="A",
            holder_session_id="session-001",
            ttl_seconds=600,
            acquired_at="2026-06-13T05:00:00Z",
            changed_by="test",
            change_reason="claim lease",
        )

        assert claimed["id"] == "LEASE-STAGEINST-LEASE-001"
        assert claimed["version"] == 1
        assert claimed["lease_status"] == "active"
        assert claimed["heartbeat_at"] == "2026-06-13T05:00:00Z"
        assert claimed["expires_at"] == "2026-06-13T05:10:00+00:00"
        current_stage = service.get_stage_instance(stage["id"])
        assert current_stage is not None
        assert current_stage["claim_status"] == "claimed"
        assert current_stage["claimed_by_harness_id"] == "A"
        assert current_stage["claimed_by_session_id"] == "session-001"

        with pytest.raises(ValueError, match="already has active lease"):
            service.claim_stage_lease(
                stage_instance_id=stage["id"],
                holder_harness_id="B",
                holder_session_id="session-002",
                ttl_seconds=600,
                changed_by="test",
                change_reason="duplicate claim",
            )

        heartbeat = service.heartbeat_stage_lease(
            stage_instance_id=stage["id"],
            holder_harness_id="A",
            holder_session_id="session-001",
            ttl_seconds=900,
            heartbeat_at="2026-06-13T05:05:00Z",
            changed_by="test",
            change_reason="heartbeat lease",
        )

        assert heartbeat["version"] == 2
        assert heartbeat["lease_status"] == "active"
        assert heartbeat["ttl_seconds"] == 900
        assert heartbeat["heartbeat_at"] == "2026-06-13T05:05:00Z"
        assert heartbeat["expires_at"] == "2026-06-13T05:20:00+00:00"

        with pytest.raises(ValueError, match="lease holder mismatch"):
            service.release_stage_lease(
                stage_instance_id=stage["id"],
                holder_harness_id="B",
                holder_session_id="session-002",
                changed_by="test",
                change_reason="wrong holder release",
            )

        released = service.release_stage_lease(
            stage_instance_id=stage["id"],
            holder_harness_id="A",
            holder_session_id="session-001",
            released_at="2026-06-13T05:06:00Z",
            changed_by="test",
            change_reason="release lease",
        )

        assert released["version"] == 3
        assert released["lease_status"] == "released"
        assert released["released_at"] == "2026-06-13T05:06:00Z"
        current_stage = service.get_stage_instance(stage["id"])
        assert current_stage is not None
        assert current_stage["claim_status"] == "unclaimed"
        assert current_stage["claimed_by_harness_id"] is None
        assert current_stage["claimed_by_session_id"] is None
        assert [row["version"] for row in service.get_stage_lease_history(claimed["id"])] == [3, 2, 1]

        reclaimed = service.claim_stage_lease(
            stage_instance_id=stage["id"],
            holder_harness_id="B",
            holder_session_id="session-002",
            ttl_seconds=300,
            acquired_at="2026-06-13T05:07:00Z",
            changed_by="test",
            change_reason="reclaim after release",
        )

        assert reclaimed["version"] == 4
        assert reclaimed["lease_status"] == "active"
        assert reclaimed["holder_harness_id"] == "B"
        assert reclaimed["holder_session_id"] == "session-002"
    finally:
        db.close()
