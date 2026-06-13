from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def test_agent_capability_snapshot_schema_contains_required_columns_and_view(tmp_path) -> None:
    db, _ = _service(tmp_path)
    try:
        conn = db._get_conn()
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        views = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(agent_capability_snapshots)").fetchall()}
        indexes = {row["name"] for row in conn.execute("PRAGMA index_list(agent_capability_snapshots)").fetchall()}
    finally:
        db.close()

    assert "agent_capability_snapshots" in tables
    assert "current_agent_capability_snapshots" in views
    assert {
        "id",
        "version",
        "harness_id",
        "harness_name",
        "role",
        "subject_scope",
        "health_status",
        "reviewer_precedence",
        "workspace_availability",
        "model_identifier",
        "capabilities",
        "captured_at",
        "source",
        "status",
        "metadata",
        "changed_by",
        "changed_at",
        "change_reason",
    } <= columns
    assert {
        "idx_agent_capability_snapshots_id_version",
        "idx_agent_capability_snapshots_harness",
        "idx_agent_capability_snapshots_health",
        "idx_agent_capability_snapshots_captured",
    } <= indexes


def test_agent_capability_snapshot_service_round_trips_current_history_and_filters(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        first = service.record_capability_snapshot(
            id="CAP-A",
            harness_id="A",
            role="loyal-opposition",
            harness_name="codex",
            subject_scope="gtkb_infrastructure",
            health_status="active",
            reviewer_precedence=20,
            workspace_availability="available",
            model_identifier="gpt-5",
            capabilities={"can_review": True, "supported_flow_types": ["implementation", "report"]},
            captured_at="2026-06-13T04:00:00Z",
            source="registry_projection",
            metadata={"note": "first"},
            changed_by="test",
            change_reason="initial capability snapshot",
        )
        second = service.record_capability_snapshot(
            id="CAP-A",
            harness_id="A",
            role="loyal-opposition",
            harness_name="codex",
            subject_scope="gtkb_infrastructure",
            health_status="degraded",
            reviewer_precedence=20,
            workspace_availability="available",
            model_identifier="gpt-5",
            capabilities={"can_review": True, "supported_flow_types": ["implementation"]},
            captured_at="2026-06-13T05:00:00Z",
            source="registry_projection",
            metadata={"note": "second"},
            changed_by="test",
            change_reason="observed degraded health",
        )
        # Second harness snapshot to exercise the list filters.
        service.record_capability_snapshot(
            id="CAP-B",
            harness_id="B",
            role="prime-builder",
            health_status="active",
            captured_at="2026-06-13T04:30:00Z",
            changed_by="test",
            change_reason="prime builder snapshot",
        )

        assert first["version"] == 1
        assert second["version"] == 2

        current = service.get_capability_snapshot("CAP-A")
        assert current is not None
        assert current["health_status"] == "degraded"
        assert current["captured_at"] == "2026-06-13T05:00:00Z"
        assert current["reviewer_precedence"] == 20
        assert current["capabilities_parsed"] == {
            "can_review": True,
            "supported_flow_types": ["implementation"],
        }
        assert current["metadata_parsed"] == {"note": "second"}

        assert [row["version"] for row in service.get_capability_snapshot_history("CAP-A")] == [2, 1]
        assert [row["id"] for row in service.list_capability_snapshots(harness_id="A")] == ["CAP-A"]
        assert [row["id"] for row in service.list_capability_snapshots(health_status="degraded")] == ["CAP-A"]
        assert {row["id"] for row in service.list_capability_snapshots(status="active")} == {"CAP-A", "CAP-B"}
    finally:
        db.close()


def test_agent_capability_snapshot_service_validates_required_fields(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError):
            service.record_capability_snapshot(
                id="CAP-BAD",
                harness_id="   ",
                role="loyal-opposition",
                changed_by="test",
                change_reason="empty harness id",
            )
        with pytest.raises(ValueError):
            service.record_capability_snapshot(
                id="CAP-BAD",
                harness_id="A",
                role="",
                changed_by="test",
                change_reason="empty role",
            )
    finally:
        db.close()


def test_agent_capability_snapshot_slice_does_not_expose_dispatch_policy_api(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        for forbidden_name in (
            "score_candidates",
            "rank_candidates",
            "select_dispatch_target",
            "evaluate_eligibility",
            "compute_dispatch_score",
            "dispatch_tick",
            "dispatch_health",
        ):
            assert not hasattr(service, forbidden_name)
    finally:
        db.close()
