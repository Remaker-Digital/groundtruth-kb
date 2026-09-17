"""Retained core-intake duties through native authority and ordinary public commands."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

import groundtruth_kb
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.cli import main
from groundtruth_kb.project.core_spec_intake import (
    intake_enabled,
    intake_status,
    is_complete,
    mark_slot_complete,
    next_missing_slot,
    next_question,
    slot_names,
)
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project

pytestmark = [pytest.mark.integration, pytest.mark.timeout(180)]
PROJECT = "PROJECT-Alpha"


@pytest.fixture
def application(native_app_authority):
    item = native_app_authority
    hook = item["host"] / ".githooks/reference-transaction"
    hook.parent.mkdir()
    shutil.copyfile(Path(__file__).resolve().parents[2] / ".githooks/reference-transaction", hook)
    return item


def _target(item):
    return item["host"] / "applications/Alpha"


def _scaffold(item, *, opt_out=False):
    return scaffold_project(
        ScaffoldOptions(
            project_name="Alpha App",
            profile="local-only",
            owner="Qualification",
            target_dir=_target(item),
            gt_kb_root=item["host"],
            project_id=PROJECT,
            authority_url=item["client"].url,
            seed_example=False,
            include_ci=False,
            opt_out_core_spec_intake=opt_out,
        )
    )


def _initialize(item, *, opt_out=False):
    args = [
        "--config",
        str(item["config"]),
        "project",
        "init",
        "Alpha",
        "--project-id",
        PROJECT,
        "--host-root",
        str(item["host"]),
        "--owner",
        "Qualification",
        "--no-include-ci",
        "--json",
    ]
    if opt_out:
        args.append("--opt-out-core-spec-intake")
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def _files(item):
    return {
        p.relative_to(item["host"]).as_posix(): p.read_bytes()
        for p in item["host"].rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


def _facts(item):
    return (item["client"].request("GET", "/v1/projects"), item["client"].request("GET", "/v1/specifications"))


def _read(item, *, project=PROJECT, fresh=False):
    config = _target(item) / "groundtruth.toml"
    if not config.exists():
        config = item["config"]
    args = ["--config", str(config), "core-specs", "next-question", "--project-id", project, "--json"]
    before, facts = _files(item), _facts(item)
    if fresh:
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PG", "GT_", "GTKB_", "GIT_"))}
        env.update(
            PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
            PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
        )
        result = subprocess.run(
            [sys.executable, "-P", "-m", "groundtruth_kb", *args],
            env=env,
            cwd=item["host"] / "applications/Beta",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        output = result.stdout
    else:
        result = CliRunner().invoke(main, args)
        assert result.exit_code == 0, result.output
        output = result.output
    assert _files(item) == before
    assert _facts(item) == facts
    return json.loads(output)


def _answer(item, slot, value="Application requirement", *, source="owner_stated", project=PROJECT):
    return mark_slot_complete(
        item["client"],
        project,
        slot,
        value,
        source,
        expected_version=0,
        actor="owner",
        reason="Explicit test owner answer",
    )


def _complete(item, *, source="owner_stated"):
    for slot in slot_names():
        _answer(item, slot, "" if source == "not_applicable" else "Required " + slot, source=source)


def test_next_missing_slot_returns_baseline_order(application):
    client = application["client"]
    assert next_missing_slot(client, PROJECT) == slot_names()[0]
    _answer(application, slot_names()[0])
    assert next_missing_slot(client, PROJECT) == slot_names()[1]


def test_is_complete_false_while_incomplete(application):
    assert is_complete(application["client"], PROJECT) is False


def test_is_complete_true_when_all_slots_resolved(application):
    _complete(application)
    assert is_complete(application["client"], PROJECT) is True
    assert next_missing_slot(application["client"], PROJECT) is None


def test_not_applicable_satisfies_slot(application):
    _answer(application, slot_names()[0], "", source="not_applicable")
    assert next_missing_slot(application["client"], PROJECT) == slot_names()[1]


def test_slot_state_from_canonical_specification_evidence(application):
    created = _answer(application, slot_names()[0], "Evidence App")
    fetched = AuthorityClient(application["client"].url).request("GET", "/v1/specifications/" + created["id"])
    assert fetched == created
    assert {"core-spec-intake", "project:" + PROJECT, "slot:product_identity", "source:owner_stated"} <= set(
        fetched["tags"]
    )
    assert fetched["scope"] == PROJECT and fetched["application_scope"] == "application:Alpha"
    assert fetched["authority"] == "stated" and fetched["description"] == "Evidence App"


def test_default_on_new_project_init(application):
    facts = _facts(application)
    target = _scaffold(application)
    assert intake_enabled(target)
    assert _read(application)["slot"] == "product_identity"
    assert _facts(application) == facts


def test_opt_out_flag_disables_intake(application):
    facts = _facts(application)
    target = _scaffold(application, opt_out=True)
    assert not intake_enabled(target)
    assert _read(application) == {"status": "disabled"}
    assert _facts(application) == facts


def test_project_init_opt_out_flag_disables_intake(application):
    facts = _facts(application)
    result = _initialize(application, opt_out=True)
    assert result["initial_question"] is None
    assert result["canonical_writes"] == result["commits"] == 0
    assert _read(application, fresh=True) == {"status": "disabled"}
    assert _facts(application) == facts


def test_project_init_default_reads_existing_project_and_emits_prompt(application):
    facts = _facts(application)
    result = _initialize(application)
    assert result["initial_question"]["name"] == "product_identity"
    assert result["initial_question"]["prompt"].count("?") == 1
    assert result["canonical_writes"] == 0 and _facts(application) == facts


def test_initial_prompt_is_returned_without_a_memory_file(application):
    result = _initialize(application)
    assert (
        result["initial_question"]["prompt"]
        == "What product or application are we building, and what should it be called?"
    )
    assert not (_target(application) / "MEMORY.md").exists()
    assert not list(application["host"].rglob("*.db"))


def test_repeated_prompt_reads_are_idempotent(application):
    first = _read(application)
    second = _read(application)
    assert first == second
    assert isinstance(first["question"], str) and first["question"].count("?") == 1


def test_successor_emits_one_question_and_is_idempotent(application):
    _scaffold(application)
    first = _read(application, fresh=True)
    second = _read(application, fresh=True)
    assert first == second
    assert first["slot"] == "product_identity" and first["question"].count("?") == 1


def test_successor_advances_to_next_slot(application):
    first = _read(application, fresh=True)
    _answer(application, "product_identity", "Acme")
    second = _read(application, fresh=True)
    assert first["slot"] == "product_identity"
    assert second["slot"] == "application_type" and second["question"] != first["question"]


def test_successor_ceases_at_completion(application):
    assert _read(application, fresh=True)["question"] is not None
    _complete(application)
    result = _read(application, fresh=True)
    assert result["complete"] and result["slot"] is result["question"] is None


def test_successor_not_applicable_counts_complete(application):
    _complete(application, source="not_applicable")
    result = _read(application, fresh=True)
    assert result["complete"] and result["question"] is None


@pytest.mark.parametrize("source", ["inferred", "needs_clarification"])
def test_unconfirmed_candidate_does_not_suppress_successor_question(application, source):
    application["client"].request(
        "PUT",
        "/v1/specifications/SPEC-CANDIDATE",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "Unconfirmed candidate",
            "fields": {
                "title": "Unconfirmed identity",
                "description": "Maybe this app",
                "status": "active",
                "scope": PROJECT,
                "type": "requirement",
                "authority": "stated",
                "handle": "core-spec-intake:" + PROJECT + ":product_identity",
                "tags": ["source:" + source],
                "application_scope": "application:Alpha",
            },
        },
    )
    assert next_missing_slot(application["client"], PROJECT) == "product_identity"
    assert _read(application, fresh=True)["slot"] == "product_identity"


def test_successor_uses_persisted_canonical_evidence(application):
    _complete(application)
    reader = AuthorityClient(application["client"].url)
    assert next_question(reader, PROJECT) is None
    assert _read(application, fresh=True)["complete"] is True


def test_disabled_successor_makes_no_write(application):
    _scaffold(application, opt_out=True)
    memory = _target(application) / "MEMORY.md"
    memory.write_text("# Unrelated owner notes\n", encoding="utf-8")
    assert _read(application, fresh=True) == {"status": "disabled"}
    assert memory.read_text(encoding="utf-8") == "# Unrelated owner notes\n"


def test_intake_enabled_env_opt_out(tmp_path, monkeypatch):
    monkeypatch.setenv("GTKB_CORE_SPEC_INTAKE_OPT_OUT", "1")
    assert intake_enabled(tmp_path) is False
    monkeypatch.delenv("GTKB_CORE_SPEC_INTAKE_OPT_OUT", raising=False)
    assert intake_enabled(tmp_path) is True


def test_intake_enabled_toml_opt_out(tmp_path):
    (tmp_path / "groundtruth.toml").write_text("[core_spec_intake]\nenabled = false\n", encoding="utf-8")
    assert intake_enabled(tmp_path) is False


def test_successor_preserves_unrelated_legacy_prompt_bytes(application):
    _scaffold(application)
    memory = _target(application) / "MEMORY.md"
    original = "# Owner notes\n## Pending Core Spec Intake\nLegacy application_type question\n"
    memory.write_text(original, encoding="utf-8")
    result = _read(application, fresh=True)
    assert result["slot"] == "product_identity"
    assert result["question"].count("?") == 1
    assert memory.read_text(encoding="utf-8") == original


def test_explicit_project_selection_does_not_pick_first_project(application):
    _scaffold(application)
    _answer(application, "product_identity", project="PROJECT-Beta")
    assert _read(application, project="PROJECT-Beta")["slot"] == "application_type"
    assert _read(application)["slot"] == "product_identity"
    before = _facts(application)
    result = CliRunner().invoke(main, ["--config", str(application["config"]), "core-specs", "next-question"])
    assert result.exit_code != 0 and "exactly one" in result.output
    assert _facts(application) == before


def test_doctor_check_warns_when_incomplete(application):
    from groundtruth_kb.project.doctor import _check_core_spec_intake

    target = _scaffold(application)
    check = _check_core_spec_intake(target, project_id=PROJECT, client=application["client"])
    assert check.status == "warning" and "product_identity" in check.message


def test_doctor_check_passes_when_complete(application):
    from groundtruth_kb.project.doctor import _check_core_spec_intake

    target = _scaffold(application)
    _complete(application)
    check = _check_core_spec_intake(target, project_id=PROJECT, client=AuthorityClient(application["client"].url))
    assert check.status == "pass"


def test_unavailable_authority_does_not_create_local_fallback(application):
    target = _scaffold(application)
    config = target / "groundtruth.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(application["client"].url, "http://127.0.0.1:1"), encoding="utf-8"
    )
    before = _files(application)
    result = CliRunner().invoke(
        main, ["--config", str(config), "core-specs", "next-question", "--project-id", PROJECT, "--json"]
    )
    assert result.exit_code != 0 and "authority_unavailable" in result.output
    assert _files(application) == before
    assert not list(application["host"].rglob("*.db"))


def test_startup_guidance_uses_current_cli_for_selected_project(application):
    _scaffold(application)
    rule = (
        Path(__file__).resolve().parents[2] / ".harness-baseline-configuration/rules/session-bootstrap.md"
    ).read_text(encoding="utf-8")
    assert (
        "gt --config <application-root>/groundtruth.toml core-specs next-question --project-id <project-id> --json"
        in rule
    )
    result = _read(application, fresh=True)
    assert result["project"]["id"] == PROJECT and result["slot"] == "product_identity"


def test_clean_adopter_end_to_end_intake_journey(application):
    initialized = _initialize(application)
    assert initialized["initial_question"]["name"] == "product_identity"
    assert _read(application, fresh=True)["slot"] == "product_identity"
    for index, slot in enumerate(slot_names()):
        _answer(application, slot, "Explicit " + slot)
        successor = _read(application, fresh=True)
        if index + 1 < len(slot_names()):
            assert successor["slot"] == slot_names()[index + 1]
        else:
            assert successor["complete"] and successor["question"] is None
    status = intake_status(application["client"], PROJECT)
    assert status["completed_slots"] == status["total_slots"] == 12
    assert intake_status(application["client"], "PROJECT-Beta")["completed_slots"] == 0
    assert not (_target(application) / "MEMORY.md").exists()
    assert not list(application["host"].rglob("*.db"))
