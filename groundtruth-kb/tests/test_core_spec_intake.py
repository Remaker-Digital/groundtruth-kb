# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
# All rights reserved.
"""Spec-derived tests for core application specification intake."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.core_spec_intake import (
    append_initial_prompt,
    is_complete,
    mark_slot_complete,
    next_missing_slot,
    project_id_for_name,
    slot_names,
)
from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT, ScaffoldOptions, scaffold_project


def _db(path: Path) -> KnowledgeDB:
    return KnowledgeDB(path / "groundtruth.db")


def _scaffold(tmp_path: Path, *, opt_out: bool = False) -> Path:
    target = tmp_path / ("opt-out" if opt_out else "enrolled")
    scaffold_project(
        ScaffoldOptions(
            project_name="Core Spec App",
            profile="local-only",
            owner="Owner",
            target_dir=target,
            seed_example=False,
            include_ci=False,
            opt_out_core_spec_intake=opt_out,
        )
    )
    return target


def test_next_missing_slot_returns_baseline_order(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        project_id = "PROJECT-CORE-SPEC-APP"
        names = slot_names()

        assert next_missing_slot(db, project_id) == names[0]
        mark_slot_complete(db, project_id, names[0], "Remaker Ops", source="owner_stated")

        assert next_missing_slot(db, project_id) == names[1]
    finally:
        db.close()


def test_is_complete_false_while_incomplete(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        assert is_complete(db, "PROJECT-INCOMPLETE") is False
    finally:
        db.close()


def test_is_complete_true_when_all_slots_resolved(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        project_id = "PROJECT-COMPLETE"
        for slot in slot_names():
            mark_slot_complete(db, project_id, slot, f"value for {slot}", source="owner_stated")

        assert is_complete(db, project_id) is True
        assert next_missing_slot(db, project_id) is None
    finally:
        db.close()


def test_not_applicable_satisfies_slot(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        names = slot_names()
        project_id = "PROJECT-NA"
        mark_slot_complete(db, project_id, names[0], "", source="not_applicable")

        assert next_missing_slot(db, project_id) == names[1]
    finally:
        db.close()


def test_slot_state_from_membase_evidence(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        project_id = "PROJECT-EVIDENCE"
        slot = slot_names()[0]
        created = mark_slot_complete(db, project_id, slot, "Evidence App", source="owner_stated")

        assert created is not None
        fetched = db.get_spec(created["id"])
        assert fetched is not None
        assert "core-spec-intake" in fetched["tags_parsed"]
        assert f"project:{project_id}" in fetched["tags_parsed"]
        assert f"slot:{slot}" in fetched["tags_parsed"]
        assert "source:owner_stated" in fetched["tags_parsed"]
    finally:
        db.close()


def test_default_on_new_project_init(tmp_path: Path) -> None:
    target = _scaffold(tmp_path)
    db = _db(target)
    try:
        project = db.get_project(project_id_for_name("Core Spec App"))
        assert project is not None
        notes = json.loads(project["notes"])
        assert notes["core_spec_intake_enabled"] is True
    finally:
        db.close()


def test_opt_out_flag_disables_intake(tmp_path: Path) -> None:
    target = _scaffold(tmp_path, opt_out=True)
    db = _db(target)
    try:
        assert db.get_project(project_id_for_name("Core Spec App")) is None
    finally:
        db.close()
    assert "## Pending Core Spec Intake" not in (target / "MEMORY.md").read_text(encoding="utf-8")


def test_project_init_opt_out_flag_disables_intake() -> None:
    runner = CliRunner()
    sandbox_name = f"_test_core_intake_{uuid.uuid4().hex[:8]}"
    target = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    try:
        result = runner.invoke(
            main,
            [
                "project",
                "init",
                sandbox_name,
                "--opt-out-core-spec-intake",
                "--no-include-ci",
                "--no-seed-example",
            ],
        )
        assert result.exit_code == 0, f"init failed: output={result.output!r} exc={result.exception!r}"
        db = KnowledgeDB(target / "groundtruth.db")
        try:
            assert db.get_project(project_id_for_name(sandbox_name)) is None
        finally:
            db.close()
        assert "## Pending Core Spec Intake" not in (target / "MEMORY.md").read_text(encoding="utf-8")
    finally:
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)


def test_project_init_default_enrolls_and_emits_prompt() -> None:
    runner = CliRunner()
    sandbox_name = f"_test_core_intake_{uuid.uuid4().hex[:8]}"
    target = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    try:
        result = runner.invoke(
            main,
            [
                "project",
                "init",
                sandbox_name,
                "--no-include-ci",
                "--no-seed-example",
            ],
        )
        assert result.exit_code == 0, f"init failed: output={result.output!r} exc={result.exception!r}"
        db = KnowledgeDB(target / "groundtruth.db")
        try:
            project = db.get_project(project_id_for_name(sandbox_name))
            assert project is not None
            assert json.loads(project["notes"])["core_spec_intake_enabled"] is True
        finally:
            db.close()
        assert "## Pending Core Spec Intake" in (target / "MEMORY.md").read_text(encoding="utf-8")
    finally:
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)


def test_initial_prompt_emitted_into_memory_md(tmp_path: Path) -> None:
    target = _scaffold(tmp_path)
    memory_text = (target / "MEMORY.md").read_text(encoding="utf-8")

    assert "## Pending Core Spec Intake" in memory_text
    assert "Product identity (`product_identity`)" in memory_text
    assert "What product or application are we building" in memory_text


def test_append_initial_prompt_is_idempotent(tmp_path: Path) -> None:
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")

    append_initial_prompt(memory, slot_names()[0])
    append_initial_prompt(memory, slot_names()[0])

    assert memory.read_text(encoding="utf-8").count("## Pending Core Spec Intake") == 1
