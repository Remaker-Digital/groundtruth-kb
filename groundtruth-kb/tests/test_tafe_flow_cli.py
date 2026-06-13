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
    commands = [
        ["flow", "start", "implementation", "--subject-type", "bridge-thread", "--subject-id", "sample", "--json"],
        ["flow", "claim", "STAGE-1", "--json"],
        ["flow", "release", "STAGE-1", "--json"],
        ["flow", "heartbeat", "STAGE-1", "--json"],
        ["flow", "advance", "STAGE-1", "--to-stage", "verify", "--json"],
        ["flow", "dispatch", "tick", "--json"],
        ["flow", "dispatch", "health", "--json"],
        ["flow", "render", "bridge-view", "--json"],
        ["flow", "pilot", "--json"],
    ]

    for command in commands:
        payload = _json_output(runner.invoke(main, [*_config_args(project_dir), *command]))
        assert payload["mutated"] is False
        assert payload["status"] == "phase0_noop"

    assert index_path.read_text(encoding="utf-8") == index_before
    assert not db_path.exists()
