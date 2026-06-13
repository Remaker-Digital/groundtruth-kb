from __future__ import annotations

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import (
    FlowDefinitionService,
    canonical_reviewed_task_flow_definitions,
)

EXPECTED_FLOW_IDS = ["deliberation", "implementation", "operation", "remediation", "report"]


def _service(tmp_path):
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, FlowDefinitionService(db)


def _canonical_by_id(flow_id: str) -> dict:
    return {seed["id"]: seed for seed in canonical_reviewed_task_flow_definitions()}[flow_id]


def test_canonical_seed_definitions_are_copy_safe() -> None:
    first = canonical_reviewed_task_flow_definitions()
    first[0]["stage_sequence"].append("mutated")

    second = canonical_reviewed_task_flow_definitions()

    assert "mutated" not in second[0]["stage_sequence"]


def test_seed_reviewed_task_flow_definitions_inserts_and_then_noops(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        first = service.seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="initial seed",
        )
        assert first["inserted"] == ["implementation", "operation", "remediation", "deliberation", "report"]
        assert first["updated"] == []
        assert first["unchanged"] == []
        assert sorted(row["id"] for row in first["definitions"]) == EXPECTED_FLOW_IDS

        rows = service.list()
        assert sorted(row["id"] for row in rows) == EXPECTED_FLOW_IDS
        assert {row["version"] for row in rows} == {1}

        for row in rows:
            seed = _canonical_by_id(row["id"])
            assert row["flow_type"] == seed["flow_type"]
            assert row["title"] == seed["title"]
            assert row["stage_sequence_parsed"] == seed["stage_sequence"]
            assert row["required_roles_by_stage_parsed"] == seed["required_roles_by_stage"]
            assert row["auq_gate_positions_parsed"] == seed["auq_gate_positions"]
            assert row["auq_gate_positions_parsed"]
            assert row["never_self_review_stages_parsed"] == seed["never_self_review_stages"]
            assert row["never_self_review_stages_parsed"]
            assert row["deterministic_carve_outs_parsed"] == seed["deterministic_carve_outs"]
            assert row["workspace_isolation_parsed"] == seed["workspace_isolation"]
            assert row["source_spec_ids_parsed"] == [
                "SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA",
                "SPEC-TAFE-R1",
                "SPEC-TAFE-R7",
            ]

        second = service.seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="repeat seed",
        )
        assert second["inserted"] == []
        assert second["updated"] == []
        assert second["unchanged"] == ["implementation", "operation", "remediation", "deliberation", "report"]
        assert {row["id"]: row["version"] for row in service.list()} == {
            "deliberation": 1,
            "implementation": 1,
            "operation": 1,
            "remediation": 1,
            "report": 1,
        }
    finally:
        db.close()


def test_seed_reviewed_task_flow_definitions_converges_drift_with_one_version(tmp_path) -> None:
    db, service = _service(tmp_path)
    try:
        service.seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="initial seed",
        )
        operation = _canonical_by_id("operation")
        service.define(
            id=operation["id"],
            flow_type=operation["flow_type"],
            title="Operation Flow Drift",
            description=operation["description"],
            stage_sequence=operation["stage_sequence"],
            required_roles_by_stage=operation["required_roles_by_stage"],
            auq_gate_positions=operation["auq_gate_positions"],
            never_self_review_stages=operation["never_self_review_stages"],
            deterministic_carve_outs=operation["deterministic_carve_outs"],
            workspace_isolation=operation["workspace_isolation"],
            source_spec_ids=operation["source_spec_ids"],
            changed_by="test",
            change_reason="simulate drift",
        )
        assert service.get("operation")["title"] == "Operation Flow Drift"
        assert [row["version"] for row in service.history("operation")] == [2, 1]

        converged = service.seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="converge drift",
        )

        assert converged["inserted"] == []
        assert converged["updated"] == ["operation"]
        assert sorted(converged["unchanged"]) == ["deliberation", "implementation", "remediation", "report"]
        assert service.get("operation")["title"] == operation["title"]
        assert [row["version"] for row in service.history("operation")] == [3, 2, 1]

        no_op = service.seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="repeat after convergence",
        )
        assert no_op["inserted"] == []
        assert no_op["updated"] == []
        assert sorted(no_op["unchanged"]) == EXPECTED_FLOW_IDS
        assert [row["version"] for row in service.history("operation")] == [3, 2, 1]
    finally:
        db.close()
