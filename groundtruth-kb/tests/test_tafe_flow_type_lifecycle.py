"""Executable-specification lifecycle coverage for the four remaining TAFE flow types.

WI-4500 (operation), WI-4501 (remediation), WI-4502 (deliberation), WI-4503
(report). The five canonical reviewed-task flow definitions are already seeded
by ``FlowDefinitionService.seed_reviewed_task_flow_definitions`` and the TAFE
runtime (``FlowRuntimeService`` / ``TypedArtifactFlowService``) is deliberately
flow-type-agnostic, so the remaining engineering work for these four flow types
is *verification* that each declared contract can be instantiated and advanced
through its stage sequence with the declared role gates, AUQ-gate positions, and
never-self-review constraints.

These tests are the executable specification of that contract. They:

1. assert each flow type's seeded definition matches its intended contract
   (the hardcoded EXPECTED table below is the spec guard — an accidental change
   to a seed definition fails the corresponding case);
2. drive each flow type through a full non-live lifecycle
   (seed -> instantiate -> create one stage instance per stage with the
   role derived from the definition -> advance -> claim/release a lease);
3. assert the AUQ-gate and never-self-review metadata reference real stages.

Bounded to test scope per ``DELIB-20263160`` (tranche-2 PAUTH): no source
mutation, no live dispatch substrate, no cutover, no schema change. All records
live in a temporary database; ``bridge/INDEX.md`` is never read or written.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

# Intended per-flow-type contract (the executable specification). Mirrors
# CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS for the four flow types covered by
# WI-4500-4503; kept independent of the source tuple so an accidental seed
# change is caught here rather than passing silently.
EXPECTED_CONTRACTS: dict[str, dict[str, object]] = {
    "operation": {
        "stage_sequence": ["plan", "execute", "verify", "complete"],
        "required_roles_by_stage": {
            "plan": "prime-builder",
            "execute": "prime-builder",
            "verify": "loyal-opposition",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["after:plan"],
        "never_self_review_stages": ["verify"],
    },
    "remediation": {
        "stage_sequence": ["diagnose", "propose_fix", "review", "implement", "verify", "complete"],
        "required_roles_by_stage": {
            "diagnose": "loyal-opposition",
            "propose_fix": "prime-builder",
            "review": "loyal-opposition",
            "implement": "prime-builder",
            "verify": "loyal-opposition",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["after:diagnose"],
        "never_self_review_stages": ["review", "verify"],
    },
    "deliberation": {
        "stage_sequence": ["surface", "investigate", "decide", "record", "complete"],
        "required_roles_by_stage": {
            "surface": "prime-builder",
            "investigate": "loyal-opposition",
            "decide": "owner",
            "record": "prime-builder",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["before:decide"],
        "never_self_review_stages": ["investigate", "record"],
    },
    "report": {
        "stage_sequence": ["investigate", "draft", "review", "finalize", "complete"],
        "required_roles_by_stage": {
            "investigate": "loyal-opposition",
            "draft": "loyal-opposition",
            "review": "prime-builder",
            "finalize": "loyal-opposition",
            "complete": "loyal-opposition",
        },
        "auq_gate_positions": ["after:review"],
        "never_self_review_stages": ["review"],
    },
}

FLOW_TYPES = sorted(EXPECTED_CONTRACTS)


def _service(tmp_path) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def _seed(service: TypedArtifactFlowService) -> None:
    service.seed_reviewed_task_flow_definitions(
        changed_by="test",
        change_reason="seed canonical reviewed-task flow definitions for lifecycle coverage",
    )


def _gate_stage(position: str) -> str:
    """Return the stage name referenced by an AUQ gate position ("after:plan")."""
    return position.split(":", 1)[1] if ":" in position else position


@pytest.mark.parametrize("flow_type", FLOW_TYPES)
def test_flow_type_definition_contract(tmp_path, flow_type: str) -> None:
    """Each seeded flow definition matches its intended per-flow-type contract."""
    db, service = _service(tmp_path)
    try:
        _seed(service)
        definition = service.get_flow_definition(flow_type)
        assert definition is not None, f"flow definition {flow_type!r} was not seeded"
        expected = EXPECTED_CONTRACTS[flow_type]

        assert definition["flow_type"] == flow_type
        assert definition["stage_sequence_parsed"] == expected["stage_sequence"]
        assert definition["required_roles_by_stage_parsed"] == expected["required_roles_by_stage"]
        assert definition["auq_gate_positions_parsed"] == expected["auq_gate_positions"]
        assert definition["never_self_review_stages_parsed"] == expected["never_self_review_stages"]
    finally:
        db.close()


@pytest.mark.parametrize("flow_type", FLOW_TYPES)
def test_flow_type_gate_metadata_references_real_stages(tmp_path, flow_type: str) -> None:
    """AUQ-gate positions and never-self-review stages reference declared stages."""
    db, service = _service(tmp_path)
    try:
        _seed(service)
        definition = service.get_flow_definition(flow_type)
        stages = set(definition["stage_sequence_parsed"])

        for position in definition["auq_gate_positions_parsed"]:
            assert position.split(":", 1)[0] in {"before", "after"}, (
                f"{flow_type}: AUQ gate {position!r} must be a before:/after: position"
            )
            assert _gate_stage(position) in stages, f"{flow_type}: AUQ gate {position!r} references an unknown stage"

        for stage in definition["never_self_review_stages_parsed"]:
            assert stage in stages, f"{flow_type}: never-self-review stage {stage!r} is not in the sequence"

        # required_roles_by_stage must cover every stage exactly.
        assert set(definition["required_roles_by_stage_parsed"]) == stages
    finally:
        db.close()


@pytest.mark.parametrize("flow_type", FLOW_TYPES)
def test_flow_type_full_lifecycle(tmp_path, flow_type: str) -> None:
    """Each flow type instantiates and advances through its full stage sequence.

    Drives the generic runtime non-live: create the flow instance, create one
    stage instance per declared stage (role derived from the definition,
    never-self-review carried as stage metadata), advance the flow to
    ``in_progress``, then claim and release a lease on the first stage.
    """
    db, service = _service(tmp_path)
    try:
        _seed(service)
        definition = service.get_flow_definition(flow_type)
        stages = definition["stage_sequence_parsed"]
        roles = definition["required_roles_by_stage_parsed"]
        never_self_review = set(definition["never_self_review_stages_parsed"])

        flow_id = f"FLOWINST-{flow_type}"
        created = service.create_flow_instance(
            id=flow_id,
            flow_definition_id=flow_type,
            subject_type="test",
            subject_id=f"{flow_type}-subject",
            status="created",
            metadata={"flow_type": flow_type},
            changed_by="test",
            change_reason=f"start {flow_type} lifecycle test flow",
        )
        assert created["flow_type"] == flow_type
        assert created["status"] == "created"
        assert created["version"] == 1

        stage_rows = []
        for index, stage_id in enumerate(stages):
            stage = service.create_stage_instance(
                id=f"STAGEINST-{flow_type}-{index}",
                flow_instance_id=flow_id,
                stage_id=stage_id,
                stage_index=index,
                required_role=roles[stage_id],
                metadata={"never_self_review": stage_id in never_self_review},
                changed_by="test",
                change_reason=f"create {flow_type} stage {stage_id}",
            )
            assert stage["stage_id"] == stage_id
            assert stage["stage_index"] == index
            assert stage["required_role"] == roles[stage_id]
            assert stage["metadata_parsed"]["never_self_review"] == (stage_id in never_self_review)
            stage_rows.append(stage)

        first_stage = stage_rows[0]

        # Advance the flow to in_progress (append-only new version, same id).
        advanced = service.create_flow_instance(
            id=flow_id,
            flow_definition_id=flow_type,
            subject_type="test",
            subject_id=f"{flow_type}-subject",
            status="in_progress",
            current_stage_instance_id=first_stage["id"],
            metadata={"flow_type": flow_type, "stage": first_stage["stage_id"]},
            changed_by="test",
            change_reason=f"advance {flow_type} flow to first stage",
        )
        assert advanced["version"] == 2
        assert advanced["status"] == "in_progress"
        assert advanced["current_stage_instance_id"] == first_stage["id"]

        # Claim then release a lease on the first stage (non-live).
        lease = service.claim_stage_lease(
            stage_instance_id=first_stage["id"],
            holder_harness_id="B",
            holder_session_id="lifecycle-test-session",
            ttl_seconds=600,
            changed_by="test",
            change_reason=f"claim {flow_type} first stage",
        )
        assert lease["lease_status"] == "active"
        assert lease["stage_instance_id"] == first_stage["id"]

        released = service.release_stage_lease(
            stage_instance_id=first_stage["id"],
            holder_harness_id="B",
            holder_session_id="lifecycle-test-session",
            changed_by="test",
            change_reason=f"release {flow_type} first stage",
        )
        assert released["lease_status"] == "released"

        # Final state assertions.
        current = service.get_flow_instance(flow_id)
        assert current["status"] == "in_progress"
        listed = service.list_stage_instances(flow_instance_id=flow_id)
        assert [row["stage_id"] for row in listed] == list(stages)
        assert {row["required_role"] for row in listed} == set(roles.values())
    finally:
        db.close()
