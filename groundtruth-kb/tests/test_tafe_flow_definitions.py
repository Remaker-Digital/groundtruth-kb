from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import FlowDefinitionService


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, FlowDefinitionService(db)


def test_flow_definitions_schema_contains_phase_0_fields(tmp_path) -> None:
    db, _ = _service(tmp_path)
    try:
        columns = {row["name"] for row in db._get_conn().execute("PRAGMA table_info(flow_definitions)").fetchall()}
    finally:
        db.close()

    assert {
        "id",
        "version",
        "flow_type",
        "title",
        "status",
        "stage_sequence",
        "required_roles_by_stage",
        "auq_gate_positions",
        "never_self_review_stages",
        "deterministic_carve_outs",
        "workspace_isolation",
        "changed_by",
        "changed_at",
        "change_reason",
    } <= columns

    # Compatibility aliases preserve the parallel draft's naming without
    # making those names the canonical service API.
    assert {
        "name",
        "lifecycle_status",
        "stages",
        "required_roles",
        "never_self_review_points",
        "deterministic_carveouts",
        "source_spec_ids",
    } <= columns


def test_flow_definition_service_round_trips_current_and_history(tmp_path) -> None:
    db, service = _service(tmp_path)
    stages = ["propose", "review", "implement", "verify"]
    roles = {
        "propose": "prime-builder",
        "review": "loyal-opposition",
        "implement": "prime-builder",
        "verify": "loyal-opposition",
    }
    try:
        first = service.define(
            id="FLOW-IMPLEMENTATION",
            flow_type="implementation",
            title="Implementation flow",
            description="Initial implementation-flow template.",
            stage_sequence=stages,
            required_roles_by_stage=roles,
            auq_gate_positions=["review"],
            never_self_review_stages=["verify"],
            deterministic_carve_outs=["index-render"],
            workspace_isolation={"requires_separate_worktree": True},
            source_spec_ids=["SPEC-TAFE-R1", "SPEC-TAFE-R7"],
            changed_by="test",
            change_reason="test setup",
        )
        second = service.define(
            id="FLOW-IMPLEMENTATION",
            flow_type="implementation",
            title="Implementation flow v2",
            stage_sequence=stages,
            required_roles_by_stage=roles,
            auq_gate_positions=["review", "verify"],
            never_self_review_stages=["review", "verify"],
            deterministic_carve_outs={"bridge_view": "generated"},
            workspace_isolation={"requires_separate_worktree": True, "mode": "strict"},
            source_spec_ids=["SPEC-TAFE-R1", "SPEC-TAFE-R7"],
            changed_by="test",
            change_reason="append revised template",
        )

        assert first is not None
        assert second is not None
        assert first["version"] == 1
        assert second["version"] == 2

        current = service.get("FLOW-IMPLEMENTATION")
        assert current is not None
        assert current["title"] == "Implementation flow v2"
        assert current["name"] == "Implementation flow v2"
        assert current["stage_sequence_parsed"] == stages
        assert current["stages_parsed"] == stages
        assert current["required_roles_by_stage_parsed"] == roles
        assert current["required_roles_parsed"] == roles
        assert current["auq_gate_positions_parsed"] == ["review", "verify"]
        assert current["never_self_review_stages_parsed"] == ["review", "verify"]
        assert current["never_self_review_points_parsed"] == ["review", "verify"]
        assert current["deterministic_carve_outs_parsed"] == {"bridge_view": "generated"}
        assert current["deterministic_carveouts_parsed"] == {"bridge_view": "generated"}
        assert current["workspace_isolation_parsed"] == {
            "requires_separate_worktree": True,
            "mode": "strict",
        }
        assert current["source_spec_ids_parsed"] == ["SPEC-TAFE-R1", "SPEC-TAFE-R7"]

        assert [row["version"] for row in service.history("FLOW-IMPLEMENTATION")] == [2, 1]
        assert [row["id"] for row in service.list(flow_type="implementation")] == ["FLOW-IMPLEMENTATION"]
        assert service.list(flow_type="operation") == []
    finally:
        db.close()


def test_flow_definition_service_rejects_bad_stage_metadata(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError, match="duplicate"):
            service.define(
                id="FLOW-BAD",
                flow_type="bad",
                title="Bad flow",
                stage_sequence=["review", "review"],
                required_roles_by_stage={"review": "loyal-opposition"},
                changed_by="test",
                change_reason="test duplicate stage",
            )

        with pytest.raises(ValueError, match="unknown stages"):
            service.define(
                id="FLOW-BAD",
                flow_type="bad",
                title="Bad flow",
                stage_sequence=["review"],
                required_roles_by_stage={
                    "review": "loyal-opposition",
                    "verify": "loyal-opposition",
                },
                changed_by="test",
                change_reason="test unknown role stage",
            )
    finally:
        db.close()
