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
    find_enrolled_project_id,
    intake_enabled,
    is_complete,
    mark_slot_complete,
    next_missing_slot,
    next_question,
    project_id_for_name,
    refresh_intake_prompt,
    slot_names,
    slot_spec_id,
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


# ── Phase 4: cross-session prompt driver ──────────────────────────────

_INTAKE_START = "<!-- gtkb:core-spec-intake:start -->"
_INTAKE_END = "<!-- gtkb:core-spec-intake:end -->"


def _load_session_start_hook():
    import importlib.util

    hook_path = _GT_KB_HOST_ROOT / "groundtruth-kb" / "templates" / "hooks" / "session-start-governance.py"
    spec = importlib.util.spec_from_file_location("_session_start_hook_under_test", hook_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_refresh_emits_single_block_and_is_idempotent(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-001: re-emit exactly one next-missing-slot question; idempotent.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    try:
        result = refresh_intake_prompt(db, "PROJECT-REFRESH", memory)
        assert result == {"status": "prompted", "slot": slot_names()[0]}
        text = memory.read_text(encoding="utf-8")
        assert text.count(_INTAKE_START) == 1
        assert text.count(_INTAKE_END) == 1
        assert text.count("## Pending Core Spec Intake") == 1
        assert "Product identity (`product_identity`)" in text

        refresh_intake_prompt(db, "PROJECT-REFRESH", memory)
        text2 = memory.read_text(encoding="utf-8")
        assert text2.count(_INTAKE_START) == 1
        assert text2 == text
    finally:
        db.close()


def test_refresh_advances_to_next_slot(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-001: after a slot is completed, re-emit the *next* missing slot.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    names = slot_names()
    try:
        refresh_intake_prompt(db, "PROJECT-ADV", memory)
        assert f"`{names[0]}`" in memory.read_text(encoding="utf-8")

        mark_slot_complete(db, "PROJECT-ADV", names[0], "Acme", source="owner_stated")
        result = refresh_intake_prompt(db, "PROJECT-ADV", memory)
        assert result == {"status": "prompted", "slot": names[1]}
        text = memory.read_text(encoding="utf-8")
        assert f"`{names[1]}`" in text
        assert text.count(_INTAKE_START) == 1
        assert f"`{names[0]}`" not in text
    finally:
        db.close()


def test_refresh_ceases_at_completion(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-002: stop prompting (remove block) once all slots complete.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    try:
        refresh_intake_prompt(db, "PROJECT-CEASE", memory)
        assert _INTAKE_START in memory.read_text(encoding="utf-8")

        for slot in slot_names():
            mark_slot_complete(db, "PROJECT-CEASE", slot, f"value {slot}", source="owner_stated")
        result = refresh_intake_prompt(db, "PROJECT-CEASE", memory)
        assert result == {"status": "complete"}
        text = memory.read_text(encoding="utf-8")
        assert _INTAKE_START not in text
        assert "## Pending Core Spec Intake" not in text
    finally:
        db.close()


def test_refresh_not_applicable_counts_complete(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-002: explicit not_applicable counts as complete.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    try:
        for slot in slot_names():
            mark_slot_complete(db, "PROJECT-NA-ALL", slot, "", source="not_applicable")
        result = refresh_intake_prompt(db, "PROJECT-NA-ALL", memory)
        assert result == {"status": "complete"}
        assert "## Pending Core Spec Intake" not in memory.read_text(encoding="utf-8")
    finally:
        db.close()


def test_refresh_inferred_candidate_does_not_suppress(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-002: inferred (not owner-confirmed) candidate must not suppress prompting.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    names = slot_names()
    try:
        db.insert_spec(
            id=slot_spec_id("PROJECT-INFERRED", names[0]),
            title="Inferred candidate",
            status="specified",
            changed_by="test",
            change_reason="inferred candidate fixture",
            description="inferred",
            priority="P1",
            scope="PROJECT-INFERRED",
            section="Core Spec Intake",
            handle=f"core-spec-intake:PROJECT-INFERRED:{names[0]}",
            tags=["core-spec-intake", "project:PROJECT-INFERRED", f"slot:{names[0]}", "source:inferred"],
            type="requirement",
            authority="stated",
            testability="observable",
        )
        assert next_missing_slot(db, "PROJECT-INFERRED") == names[0]
        result = refresh_intake_prompt(db, "PROJECT-INFERRED", memory)
        assert result == {"status": "prompted", "slot": names[0]}
    finally:
        db.close()


def test_refresh_uses_persisted_membase_evidence(tmp_path: Path) -> None:
    # ADR-CORE-INTAKE-001: completion derives from persisted MemBase evidence, not session state.
    db_path = tmp_path / "groundtruth.db"
    writer = KnowledgeDB(db_path)
    try:
        for slot in slot_names():
            mark_slot_complete(writer, "PROJECT-PERSIST", slot, f"value {slot}", source="owner_stated")
    finally:
        writer.close()

    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    reader = KnowledgeDB(db_path)  # fresh handle, no shared session state
    try:
        assert next_question(reader, "PROJECT-PERSIST") is None
        result = refresh_intake_prompt(reader, "PROJECT-PERSIST", memory)
        assert result == {"status": "complete"}
    finally:
        reader.close()


def test_refresh_disabled_makes_no_write(tmp_path: Path) -> None:
    # DCL-CORE-INTAKE-001: opt-out path makes no file I/O.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    try:
        result = refresh_intake_prompt(db, "PROJECT-DISABLED", memory, enabled=False)
        assert result == {"status": "disabled"}
        assert memory.read_text(encoding="utf-8") == "# Memory\n"
    finally:
        db.close()


def test_intake_enabled_env_opt_out(tmp_path: Path, monkeypatch) -> None:
    # DCL-CORE-INTAKE-001: env opt-out disables intake; default enabled.
    monkeypatch.setenv("GTKB_CORE_SPEC_INTAKE_OPT_OUT", "1")
    assert intake_enabled(tmp_path) is False
    monkeypatch.delenv("GTKB_CORE_SPEC_INTAKE_OPT_OUT", raising=False)
    assert intake_enabled(tmp_path) is True


def test_intake_enabled_toml_opt_out(tmp_path: Path) -> None:
    # DCL-CORE-INTAKE-001: groundtruth.toml opt-out disables intake.
    (tmp_path / "groundtruth.toml").write_text("[core_spec_intake]\nenabled = false\n", encoding="utf-8")
    assert intake_enabled(tmp_path) is False


def test_refresh_migrates_legacy_block_without_duplication(tmp_path: Path) -> None:
    # DCL-CORE-INTAKE-001 (backward compat): Slice-1 block migrates to delimited form, no duplication.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    memory = tmp_path / "MEMORY.md"
    memory.write_text("# Memory\n", encoding="utf-8")
    append_initial_prompt(memory, slot_names()[0])  # legacy un-delimited block
    assert _INTAKE_START not in memory.read_text(encoding="utf-8")
    try:
        refresh_intake_prompt(db, "PROJECT-MIGRATE", memory)
        text = memory.read_text(encoding="utf-8")
        assert text.count("## Pending Core Spec Intake") == 1
        assert text.count(_INTAKE_START) == 1
        assert text.startswith("# Memory")
    finally:
        db.close()


def test_find_enrolled_project_id(tmp_path: Path) -> None:
    target = _scaffold(tmp_path)
    db = _db(target)
    try:
        assert find_enrolled_project_id(db) == project_id_for_name("Core Spec App")
    finally:
        db.close()


def test_doctor_check_warns_when_incomplete(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-001: doctor-style health surface reports the next missing slot.
    from groundtruth_kb.project.doctor import _check_core_spec_intake

    target = _scaffold(tmp_path)
    check = _check_core_spec_intake(target)
    assert check.status == "warning"
    assert "product_identity" in check.message


def test_doctor_check_passes_when_complete(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_core_spec_intake

    target = _scaffold(tmp_path)
    db = _db(target)
    try:
        pid = project_id_for_name("Core Spec App")
        for slot in slot_names():
            mark_slot_complete(db, pid, slot, f"value {slot}", source="owner_stated")
    finally:
        db.close()
    check = _check_core_spec_intake(target)
    assert check.status == "pass"


def test_session_start_hook_no_op_on_missing_db(tmp_path: Path) -> None:
    # DCL-CORE-INTAKE-001 (fail-safe): hook must not raise when groundtruth.db is absent.
    hook = _load_session_start_hook()
    (tmp_path / "MEMORY.md").write_text("# Memory\n", encoding="utf-8")
    hook._refresh_core_spec_intake(str(tmp_path))  # must not raise
    assert "## Pending Core Spec Intake" not in (tmp_path / "MEMORY.md").read_text(encoding="utf-8")


def test_session_start_hook_refreshes_enrolled_project(tmp_path: Path) -> None:
    # SPEC-CORE-INTAKE-001 + adopter wiring: hook re-emits the prompt and migrates the legacy block.
    target = _scaffold(tmp_path)
    hook = _load_session_start_hook()
    hook._refresh_core_spec_intake(str(target))
    text = (target / "MEMORY.md").read_text(encoding="utf-8")
    assert text.count("## Pending Core Spec Intake") == 1
    assert _INTAKE_START in text


def test_clean_adopter_end_to_end_intake_journey(tmp_path: Path) -> None:
    # GTKB-CORE-001 Phase 5 adoption evidence (SPEC-CORE-INTAKE-001/002): full clean-adopter
    # journey — init enrolls + emits the initial prompt; later sessions re-prompt and advance to
    # the next slot; completion ceases prompting.
    target = _scaffold(tmp_path)
    memory = target / "MEMORY.md"
    pid = project_id_for_name("Core Spec App")
    hook = _load_session_start_hook()
    names = slot_names()

    # Init: enrolled, initial prompt for the first slot present.
    db = _db(target)
    try:
        assert find_enrolled_project_id(db) == pid
    finally:
        db.close()
    assert "## Pending Core Spec Intake" in memory.read_text(encoding="utf-8")
    assert f"`{names[0]}`" in memory.read_text(encoding="utf-8")

    # Later session: the hook re-emits (migrating the legacy block to delimited form), still slot 0.
    hook._refresh_core_spec_intake(str(target))
    text = memory.read_text(encoding="utf-8")
    assert _INTAKE_START in text
    assert text.count("## Pending Core Spec Intake") == 1
    assert f"`{names[0]}`" in text

    # Owner answers the first slot; the next session advances to the second slot.
    db = _db(target)
    try:
        mark_slot_complete(db, pid, names[0], "Acme Widgets", source="owner_stated")
    finally:
        db.close()
    hook._refresh_core_spec_intake(str(target))
    text = memory.read_text(encoding="utf-8")
    assert f"`{names[1]}`" in text
    assert f"`{names[0]}`" not in text

    # Owner completes the remaining slots; the next session ceases prompting.
    db = _db(target)
    try:
        for slot in names[1:]:
            mark_slot_complete(db, pid, slot, f"value {slot}", source="owner_stated")
    finally:
        db.close()
    hook._refresh_core_spec_intake(str(target))
    final = memory.read_text(encoding="utf-8")
    assert "## Pending Core Spec Intake" not in final
    assert _INTAKE_START not in final
