from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.intake import capture_requirement, confirm_intake, ensure_backlog_for_confirmed_spec


def _db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(tmp_path / "groundtruth.db")


def _seed_owner_deliberation(db: KnowledgeDB, delib_id: str) -> None:
    db.insert_deliberation(
        delib_id,
        "owner_conversation",
        "Owner confirmed implementation-bearing specification",
        "Owner confirmed the specification should be tracked.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )


def test_confirmed_requirement_creates_one_canonical_backlog_item(tmp_path: Path) -> None:
    db = _db(tmp_path)
    try:
        intake = capture_requirement(
            db,
            "The system must create a backlog item when a functional spec is confirmed.",
            proposed_title="Auto backlog on functional spec confirmation",
            proposed_section="backlog",
            proposed_scope="spec intake",
            proposed_type="requirement",
            changed_by="test",
        )

        confirmed = confirm_intake(db, intake["deliberation_id"], changed_by="test")
        auto_backlog = confirmed["auto_backlog"]

        assert auto_backlog["action"] == "created"
        assert auto_backlog["project_attachment"] == {
            "action": "unassigned",
            "reason": "no deterministic project fit",
        }
        work_item = db.get_work_item(auto_backlog["work_item"]["id"])
        assert work_item["source_spec_id"] == confirmed["confirmed_spec_id"]
        assert work_item["stage"] == "backlogged"
        assert work_item["related_deliberation_ids_parsed"] == [intake["deliberation_id"]]

        duplicate = confirm_intake(db, intake["deliberation_id"], changed_by="test")
        assert duplicate == {"already_confirmed": True, "confirmed_spec_id": confirmed["confirmed_spec_id"]}
        assert len(db.list_work_items(source_spec_id=confirmed["confirmed_spec_id"])) == 1
    finally:
        db.close()


def test_confirmed_architecture_decision_does_not_create_backlog_item_by_default(tmp_path: Path) -> None:
    db = _db(tmp_path)
    try:
        intake = capture_requirement(
            db,
            "Record the architectural decision without creating implementation work.",
            proposed_title="Architecture-only decision",
            proposed_section="architecture",
            proposed_scope="governance",
            proposed_type="architecture_decision",
            changed_by="test",
        )

        confirmed = confirm_intake(db, intake["deliberation_id"], changed_by="test")

        assert confirmed["auto_backlog"]["action"] == "skipped"
        assert confirmed["auto_backlog"]["reason"] == "spec is not implementation-bearing"
        assert db.list_work_items(source_spec_id=confirmed["confirmed_spec_id"]) == []
    finally:
        db.close()


def test_project_fit_attaches_only_with_one_explicit_project_constraint(tmp_path: Path) -> None:
    db = _db(tmp_path)
    try:
        _seed_owner_deliberation(db, "DELIB-PROJECT-FIT")
        db.insert_project("Explicit Fit Project", "test", "seed project", id="PROJECT-FIT")
        spec = db.insert_spec(
            "SPEC-PROJECT-FIT",
            "Spec with explicit project fit",
            "specified",
            "test",
            "seed implementation-bearing spec",
            constraints={"implementation_bearing": True, "project_id": "PROJECT-FIT"},
        )

        auto_backlog = ensure_backlog_for_confirmed_spec(
            db,
            spec,
            deliberation_id="DELIB-PROJECT-FIT",
            changed_by="test",
        )

        assert auto_backlog["action"] == "created"
        assert auto_backlog["project_attachment"]["action"] == "attached"
        assert auto_backlog["project_attachment"]["project_id"] == "PROJECT-FIT"
        memberships = db.list_project_work_items("PROJECT-FIT")
        assert [row["work_item_id"] for row in memberships] == [auto_backlog["work_item"]["id"]]
    finally:
        db.close()


def test_project_fit_uses_existing_spec_artifact_link(tmp_path: Path) -> None:
    db = _db(tmp_path)
    try:
        _seed_owner_deliberation(db, "DELIB-ARTIFACT-FIT")
        db.insert_project("Artifact Fit Project", "test", "seed project", id="PROJECT-ARTIFACT-FIT")
        spec = db.insert_spec(
            "SPEC-ARTIFACT-FIT",
            "Spec with artifact project fit",
            "specified",
            "test",
            "seed implementation-bearing spec",
            tags=["implementation-bearing"],
        )
        db.add_project_artifact_link(
            "PROJECT-ARTIFACT-FIT",
            "spec",
            "SPEC-ARTIFACT-FIT",
            "test",
            "seed deterministic spec fit",
        )

        auto_backlog = ensure_backlog_for_confirmed_spec(
            db,
            spec,
            deliberation_id="DELIB-ARTIFACT-FIT",
            changed_by="test",
        )

        assert auto_backlog["project_attachment"]["action"] == "attached"
        assert auto_backlog["project_attachment"]["project_id"] == "PROJECT-ARTIFACT-FIT"
    finally:
        db.close()


def test_ambiguous_project_fit_leaves_work_item_unassigned(tmp_path: Path) -> None:
    db = _db(tmp_path)
    try:
        _seed_owner_deliberation(db, "DELIB-AMBIGUOUS-FIT")
        for project_id in ("PROJECT-A", "PROJECT-B"):
            db.insert_project(project_id, "test", "seed project", id=project_id)
        spec = db.insert_spec(
            "SPEC-AMBIGUOUS-FIT",
            "Spec with ambiguous project fit",
            "specified",
            "test",
            "seed implementation-bearing spec",
            constraints={"implementation_bearing": True, "project_ids": ["PROJECT-A", "PROJECT-B"]},
        )

        auto_backlog = ensure_backlog_for_confirmed_spec(
            db,
            spec,
            deliberation_id="DELIB-AMBIGUOUS-FIT",
            changed_by="test",
        )

        assert auto_backlog["project_attachment"] == {
            "action": "unassigned",
            "reason": "ambiguous deterministic project fit",
            "project_ids": ["PROJECT-A", "PROJECT-B"],
        }
        assert db.list_project_work_items("PROJECT-A") == []
        assert db.list_project_work_items("PROJECT-B") == []
        assert json.loads(auto_backlog["work_item"]["related_spec_ids_at_creation"]) == ["SPEC-AMBIGUOUS-FIT"]
    finally:
        db.close()
