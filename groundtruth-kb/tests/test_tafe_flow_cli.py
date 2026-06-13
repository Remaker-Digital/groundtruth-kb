from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.typed_artifact_flow import FlowDefinitionService, TypedArtifactFlowService

EXPECTED_FLOW_IDS = ["deliberation", "implementation", "operation", "remediation", "report"]


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _db(project_dir: Path) -> KnowledgeDB:
    return KnowledgeDB(project_dir / "groundtruth.db")


def _json_output(result) -> dict:
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def _create_cli_stage(project_dir: Path) -> str:
    db = _db(project_dir)
    try:
        service = TypedArtifactFlowService(db)
        definition = service.create_flow_definition(
            id="FLOW-CLI-LEASE",
            flow_type="implementation",
            name="CLI lease flow",
            stages=["propose", "review"],
            required_roles={
                "propose": "prime-builder",
                "review": "loyal-opposition",
            },
            changed_by="test",
            change_reason="seed CLI lease definition",
            source_spec_ids=["SPEC-TAFE-R2", "SPEC-TAFE-R3", "SPEC-TAFE-R7"],
        )
        flow = service.create_flow_instance(
            id="FLOWINST-CLI-LEASE",
            flow_definition_id=definition["id"],
            subject_type="bridge-thread",
            subject_id="gtkb-tafe-flow-lease-commands",
            changed_by="test",
            change_reason="seed CLI lease flow",
        )
        stage = service.create_stage_instance(
            id="STAGEINST-CLI-LEASE",
            flow_instance_id=flow["id"],
            stage_id="review",
            stage_index=1,
            required_role="loyal-opposition",
            changed_by="test",
            change_reason="seed CLI lease stage",
        )
        return stage["id"]
    finally:
        db.close()


def test_flow_help_lists_phase_0_skeleton_commands(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "--help"])

    assert result.exit_code == 0, result.output
    for command in [
        "define",
        "list",
        "show",
        "status",
        "start",
        "claim",
        "release",
        "heartbeat",
        "recover-leases",
        "advance",
        "dispatch",
        "render",
        "pilot",
    ]:
        assert command in result.output


def test_flow_define_reports_canonical_definitions_without_seeding(runner: CliRunner, project_dir: Path) -> None:
    db = _db(project_dir)
    try:
        assert db.list_flow_definitions(status="active") == []
    finally:
        db.close()

    payload = _json_output(runner.invoke(main, [*_config_args(project_dir), "flow", "define", "--json"]))

    assert payload["mutated"] is False
    assert payload["status"] == "phase0_read_only"
    assert sorted(row["id"] for row in payload["definitions"]) == EXPECTED_FLOW_IDS
    assert {row["seeded"] for row in payload["definitions"]} == {False}

    db = _db(project_dir)
    try:
        assert db.list_flow_definitions(status="active") == []
    finally:
        db.close()


def test_flow_recover_leases_dry_run_and_recover_stage(runner: CliRunner, project_dir: Path) -> None:
    stage_id = _create_cli_stage(project_dir)
    config_args = _config_args(project_dir)

    claimed = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "claim",
                stage_id,
                "--holder-harness-id",
                "A",
                "--holder-session-id",
                "session-expired",
                "--ttl-seconds",
                "600",
                "--json",
            ],
        )
    )

    assert claimed["status"] == "active"
    dry_run = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "recover-leases",
                "--as-of",
                "2999-01-01T00:00:00Z",
                "--dry-run",
                "--json",
            ],
        )
    )

    assert dry_run["mutated"] is False
    assert dry_run["status"] == "dry_run"
    assert dry_run["recovered_count"] == 0
    assert [row["id"] for row in dry_run["candidates"]] == [claimed["lease_id"]]

    db = _db(project_dir)
    try:
        service = TypedArtifactFlowService(db)
        current_stage = service.get_stage_instance(stage_id)
        assert current_stage is not None
        assert current_stage["claim_status"] == "claimed"
    finally:
        db.close()

    recovered = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "recover-leases",
                "--as-of",
                "2999-01-01T00:00:00Z",
                "--json",
            ],
        )
    )

    assert recovered["mutated"] is True
    assert recovered["status"] == "recovered"
    assert recovered["recovered_count"] == 1
    assert recovered["recovered"][0]["lease_status"] == "recovered"

    db = _db(project_dir)
    try:
        service = TypedArtifactFlowService(db)
        current_stage = service.get_stage_instance(stage_id)
        assert current_stage is not None
        assert current_stage["claim_status"] == "unclaimed"
        assert current_stage["claimed_by_harness_id"] is None
        assert current_stage["claimed_by_session_id"] is None
    finally:
        db.close()

    repeated = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "recover-leases",
                "--as-of",
                "2999-01-01T00:00:00Z",
                "--json",
            ],
        )
    )

    assert repeated["mutated"] is False
    assert repeated["status"] == "no_expired_leases"
    assert repeated["recovered_count"] == 0


def test_flow_list_show_and_status_read_existing_instances(runner: CliRunner, project_dir: Path) -> None:
    db = _db(project_dir)
    try:
        service = TypedArtifactFlowService(db)
        FlowDefinitionService(db).seed_reviewed_task_flow_definitions(
            changed_by="test",
            change_reason="seed test definitions",
        )
        service.create_flow_instance(
            id="FLOW-1",
            flow_definition_id="implementation",
            subject_type="bridge-thread",
            subject_id="gtkb-example",
            changed_by="test",
            change_reason="seed test flow instance",
            status="created",
        )
    finally:
        db.close()

    listed = _json_output(runner.invoke(main, [*_config_args(project_dir), "flow", "list", "--json"]))
    assert listed["mutated"] is False
    assert [row["id"] for row in listed["flow_instances"]] == ["FLOW-1"]

    shown = _json_output(runner.invoke(main, [*_config_args(project_dir), "flow", "show", "FLOW-1", "--json"]))
    assert shown["found"] is True
    assert shown["flow_instance"]["subject_id"] == "gtkb-example"

    status = _json_output(runner.invoke(main, [*_config_args(project_dir), "flow", "status", "--json"]))
    assert status["flow_instance_count"] == 1
    assert status["status_counts"] == {"created": 1}


def test_flow_phase_0_noop_commands_do_not_mutate_db_or_bridge(runner: CliRunner, project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_path = bridge_dir / "INDEX.md"
    index_before = "Document: sample\nVERIFIED: bridge/sample-001.md\n"
    index_path.write_text(index_before, encoding="utf-8")

    db_path = project_dir / "groundtruth.db"
    # Genuine phase-0 no-op commands report "phase0_noop", create no database,
    # and leave the canonical bridge index untouched.
    phase0_noop_commands = [
        ["flow", "start", "implementation", "--subject-type", "bridge-thread", "--subject-id", "sample", "--json"],
        ["flow", "advance", "STAGE-1", "--to-stage", "verify", "--json"],
        ["flow", "render", "bridge-view", "--json"],
        ["flow", "pilot", "--json"],
    ]
    for command in phase0_noop_commands:
        payload = _json_output(runner.invoke(main, [*_config_args(project_dir), *command]))
        assert payload["mutated"] is False
        assert payload["status"] == "phase0_noop"

    # No phase-0 no-op command may create the database or alter the bridge index.
    assert not db_path.exists()
    assert index_path.read_text(encoding="utf-8") == index_before

    # The dispatch tick/health commands graduated to phase-1 evaluate-only
    # (WI-4499). They open the database read-only to evaluate dispatch readiness
    # and report "phase1_evaluate_only", but perform no logical mutation and
    # never write the canonical bridge index.
    phase1_evaluate_only_commands = [
        ["flow", "dispatch", "tick", "--json"],
        ["flow", "dispatch", "health", "--json"],
    ]
    for command in phase1_evaluate_only_commands:
        payload = _json_output(runner.invoke(main, [*_config_args(project_dir), *command]))
        assert payload["mutated"] is False
        assert payload["status"] == "phase1_evaluate_only"

    # Bridge authority (GOV-FILE-BRIDGE-AUTHORITY-001) is preserved: evaluate-only
    # dispatch commands never mutate the canonical index.
    assert index_path.read_text(encoding="utf-8") == index_before


def test_flow_lease_commands_claim_heartbeat_and_release_stage(runner: CliRunner, project_dir: Path) -> None:
    stage_id = _create_cli_stage(project_dir)
    config_args = _config_args(project_dir)

    claimed = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "claim",
                stage_id,
                "--holder-harness-id",
                "A",
                "--holder-session-id",
                "session-001",
                "--ttl-seconds",
                "600",
                "--json",
            ],
        )
    )

    assert claimed["mutated"] is True
    assert claimed["phase"] == "phase-1"
    assert claimed["status"] == "active"
    assert claimed["lease_id"] == "LEASE-STAGEINST-CLI-LEASE"
    assert claimed["holder_harness_id"] == "A"
    assert claimed["holder_session_id"] == "session-001"

    duplicate = runner.invoke(
        main,
        [
            *config_args,
            "flow",
            "claim",
            stage_id,
            "--holder-harness-id",
            "B",
            "--holder-session-id",
            "session-002",
            "--json",
        ],
    )
    assert duplicate.exit_code == 1
    duplicate_payload = json.loads(duplicate.output)
    assert duplicate_payload["mutated"] is False
    assert duplicate_payload["status"] == "error"
    assert "already has active lease" in duplicate_payload["summary"]

    heartbeat = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "heartbeat",
                stage_id,
                "--holder-harness-id",
                "A",
                "--holder-session-id",
                "session-001",
                "--ttl-seconds",
                "900",
                "--json",
            ],
        )
    )
    assert heartbeat["mutated"] is True
    assert heartbeat["status"] == "active"
    assert heartbeat["lease"]["version"] == 2
    assert heartbeat["lease"]["ttl_seconds"] == 900

    wrong_holder = runner.invoke(
        main,
        [
            *config_args,
            "flow",
            "release",
            stage_id,
            "--holder-harness-id",
            "B",
            "--holder-session-id",
            "session-002",
            "--json",
        ],
    )
    assert wrong_holder.exit_code == 1
    wrong_holder_payload = json.loads(wrong_holder.output)
    assert wrong_holder_payload["status"] == "error"
    assert "lease holder mismatch" in wrong_holder_payload["summary"]

    released = _json_output(
        runner.invoke(
            main,
            [
                *config_args,
                "flow",
                "release",
                stage_id,
                "--holder-harness-id",
                "A",
                "--holder-session-id",
                "session-001",
                "--json",
            ],
        )
    )
    assert released["mutated"] is True
    assert released["status"] == "released"
    assert released["lease"]["version"] == 3

    db = _db(project_dir)
    try:
        service = TypedArtifactFlowService(db)
        current_stage = service.get_stage_instance(stage_id)
        assert current_stage is not None
        assert current_stage["claim_status"] == "unclaimed"
        assert current_stage["claimed_by_harness_id"] is None
        assert current_stage["claimed_by_session_id"] is None
    finally:
        db.close()
