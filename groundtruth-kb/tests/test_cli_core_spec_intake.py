"""CLI tests for read-only core-spec intake commands."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.core_spec_intake import mark_slot_complete, slot_names

PROJECT_ID = "PROJECT-CORE-SPEC-APP"
PROJECT_NAME = "Core Spec App"


def _config_path(project_dir: Path) -> Path:
    return project_dir / "groundtruth.toml"


def _runner_result(project_dir: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(_config_path(project_dir)), *args])


def _seed_project(project_dir: Path, *, completed_slots: tuple[str, ...] = ()) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_project(PROJECT_NAME, "test", "seed", id=PROJECT_ID)
        for slot in completed_slots:
            mark_slot_complete(db, PROJECT_ID, slot, f"value for {slot}", source="owner_stated")
    finally:
        db.close()


def _core_spec_count(project_dir: Path) -> int:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        return len(db.list_specs(tag="core-spec-intake"))
    finally:
        db.close()


def test_core_specs_status_json_reports_incomplete_by_project_id(project_dir: Path) -> None:
    names = slot_names()
    _seed_project(project_dir, completed_slots=(names[0],))

    result = _runner_result(project_dir, "core-specs", "status", "--project-id", PROJECT_ID, "--json", "--no-fail")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project"]["id"] == PROJECT_ID
    assert payload["complete"] is False
    assert payload["completed_slots"] == 1
    assert payload["total_slots"] == len(names)
    assert payload["next_slot"] == names[1]
    assert payload["slots"][0]["complete"] is True
    assert payload["slots"][0]["source"] == "owner_stated"
    assert payload["slots"][1]["complete"] is False


def test_core_specs_status_fails_when_incomplete_without_no_fail(project_dir: Path) -> None:
    _seed_project(project_dir)

    result = _runner_result(project_dir, "core-specs", "status", "--project-id", PROJECT_ID, "--json")

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["complete"] is False
    assert payload["next_slot"] == slot_names()[0]


def test_core_specs_status_ignores_inferred_slot_evidence(project_dir: Path) -> None:
    _seed_project(project_dir)
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_spec(
            id="SPEC-INFERRED-CORE-SLOT",
            title="Inferred core spec slot",
            status="specified",
            changed_by="test",
            change_reason="Seed non-owner-stated core spec evidence",
            description="Project: PROJECT-CORE-SPEC-APP\nSlot: product_identity\nSource: inferred\n\nMaybe App",
            priority="P1",
            scope=PROJECT_ID,
            section="Core Spec Intake",
            handle="core-spec-intake:PROJECT-CORE-SPEC-APP:product_identity",
            tags=[
                "core-spec-intake",
                f"project:{PROJECT_ID}",
                "slot:product_identity",
                "source:inferred",
            ],
            type="requirement",
            authority="inferred",
            testability="observable",
        )
    finally:
        db.close()

    result = _runner_result(project_dir, "core-specs", "status", "--project-id", PROJECT_ID, "--json", "--no-fail")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["next_slot"] == "product_identity"
    assert payload["slots"][0]["complete"] is False


def test_core_specs_next_question_by_project_name_is_read_only(project_dir: Path) -> None:
    _seed_project(project_dir)
    before_count = _core_spec_count(project_dir)

    result = _runner_result(project_dir, "core-specs", "next-question", "--project-name", PROJECT_NAME)

    assert result.exit_code == 0, result.output
    assert "Product identity (product_identity)" in result.output
    assert "What product or application are we building" in result.output
    assert _core_spec_count(project_dir) == before_count


def test_core_specs_next_question_json_reports_completion(project_dir: Path) -> None:
    _seed_project(project_dir, completed_slots=slot_names())

    result = _runner_result(project_dir, "core-specs", "next-question", "--project-id", PROJECT_ID, "--json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["complete"] is True
    assert payload["slot"] is None
    assert payload["question"] is None


def test_core_specs_status_text_reports_complete(project_dir: Path) -> None:
    _seed_project(project_dir, completed_slots=slot_names())

    result = _runner_result(project_dir, "core-specs", "status", "--project-name", PROJECT_NAME)

    assert result.exit_code == 0, result.output
    assert f"{PROJECT_ID}: complete" in result.output


def test_core_specs_help_lists_read_only_commands(project_dir: Path) -> None:
    result = _runner_result(project_dir, "core-specs", "--help")

    assert result.exit_code == 0, result.output
    assert "status" in result.output
    assert "next-question" in result.output
