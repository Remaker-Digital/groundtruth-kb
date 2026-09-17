"""Public core-intake behavior against disposable PostgreSQL and real native HTTP."""

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
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main
from groundtruth_kb.project.core_spec_intake import intake_status, mark_slot_complete, slot_names

PROJECT_ID = "PROJECT-Alpha"
PROJECT_NAME = "Alpha App"
pytestmark = [pytest.mark.integration, pytest.mark.timeout(180)]


@pytest.fixture
def project_dir(native_app_authority):
    return native_app_authority


def _runner_result(project_dir, *args):
    return CliRunner().invoke(main, ["--config", str(project_dir["config"]), *args])


def _seed_project(project_dir, *, completed_slots=()):
    for slot in completed_slots:
        mark_slot_complete(
            project_dir["client"],
            PROJECT_ID,
            slot,
            f"value for {slot}",
            expected_version=0,
            actor="qualification",
            reason="Explicit answer fixture",
        )


def _core_spec_count(project_dir):
    return len(project_dir["client"].request("GET", "/v1/specifications", query={"scope": PROJECT_ID})["records"])


def test_core_specs_status_json_reports_incomplete_by_project_id(project_dir) -> None:
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


def test_core_specs_status_fails_when_incomplete_without_no_fail(project_dir) -> None:
    _seed_project(project_dir)

    result = _runner_result(project_dir, "core-specs", "status", "--project-id", PROJECT_ID, "--json")

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["complete"] is False
    assert payload["next_slot"] == slot_names()[0]


def test_core_specs_status_ignores_inferred_slot_evidence(project_dir) -> None:
    _seed_project(project_dir)
    project_dir["client"].request(
        "PUT",
        "/v1/specifications/SPEC-INFERRED-CORE-SLOT",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "An inference does not complete intake",
            "fields": {
                "title": "Inferred core spec slot",
                "status": "active",
                "description": "Maybe App",
                "scope": PROJECT_ID,
                "section": "Core Spec Intake",
                "handle": f"core-spec-intake:{PROJECT_ID}:product_identity",
                "tags": ["core-spec-intake", f"project:{PROJECT_ID}", "slot:product_identity", "source:inferred"],
                "type": "requirement",
                "authority": "inferred",
                "application_scope": "application:Alpha",
            },
        },
    )

    result = _runner_result(project_dir, "core-specs", "status", "--project-id", PROJECT_ID, "--json", "--no-fail")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["next_slot"] == "product_identity"
    assert payload["slots"][0]["complete"] is False


def test_core_specs_next_question_by_project_name_is_read_only(project_dir) -> None:
    _seed_project(project_dir)
    before_count = _core_spec_count(project_dir)

    result = _runner_result(project_dir, "core-specs", "next-question", "--project-name", PROJECT_NAME)

    assert result.exit_code == 0, result.output
    assert "Product identity (product_identity)" in result.output
    assert "What product or application are we building" in result.output
    assert _core_spec_count(project_dir) == before_count


def test_core_specs_next_question_json_reports_completion(project_dir) -> None:
    _seed_project(project_dir, completed_slots=slot_names())

    result = _runner_result(project_dir, "core-specs", "next-question", "--project-id", PROJECT_ID, "--json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["complete"] is True
    assert payload["slot"] is None
    assert payload["question"] is None


def test_core_specs_status_text_reports_complete(project_dir) -> None:
    _seed_project(project_dir, completed_slots=slot_names())

    result = _runner_result(project_dir, "core-specs", "status", "--project-name", PROJECT_NAME)

    assert result.exit_code == 0, result.output
    assert f"{PROJECT_ID}: complete" in result.output


def test_core_specs_help_lists_read_only_commands(project_dir) -> None:
    result = _runner_result(project_dir, "core-specs", "--help")

    assert result.exit_code == 0, result.output
    assert "status" in result.output
    assert "next-question" in result.output


def test_explicit_answer_writes_only_canonical_specification_and_preserves_projects(project_dir):
    client = project_dir["client"]
    before = client.request("GET", "/v1/projects/" + PROJECT_ID)
    result = _runner_result(
        project_dir,
        "core-specs",
        "answer",
        "--project-id",
        PROJECT_ID,
        "--slot",
        "product_identity",
        "--value",
        "Owner named product",
        "--expected-version",
        "0",
        "--actor",
        "owner",
        "--reason",
        "State the intended product",
        "--json",
    )
    assert result.exit_code == 0, result.output
    answer = json.loads(result.output)
    assert answer["description"] == "Owner named product" and answer["version"] == 1
    assert answer["application_scope"] == "application:Alpha" and answer["scope"] == PROJECT_ID
    assert answer["authority"] == "stated"
    assert client.request("GET", "/v1/specifications/" + answer["id"]) == answer
    assert client.request("GET", "/v1/projects/" + PROJECT_ID) == before
    assert not list(project_dir["host"].rglob("*.db"))
    assert not list(project_dir["host"].rglob("MEMORY.md"))


def test_stale_answer_cannot_overwrite_current_value_or_history(project_dir):
    from psycopg import sql

    def history():
        with project_dir["service"].kernel.transaction(read_only=True) as transaction:
            transaction.cursor.execute(
                sql.SQL("SELECT * FROM {}.record_history ORDER BY history_id").format(
                    sql.Identifier(transaction.schema)
                )
            )
            return transaction.cursor.fetchall()

    client = project_dir["client"]
    created = mark_slot_complete(
        client, PROJECT_ID, "product_identity", "First", expected_version=0, actor="owner", reason="First answer"
    )
    before_history = history()
    with pytest.raises(AuthorityClientError) as caught:
        mark_slot_complete(
            client, PROJECT_ID, "product_identity", "Stale", expected_version=0, actor="owner", reason="Stale attempt"
        )
    assert caught.value.code == "cas_conflict"
    assert client.request("GET", "/v1/specifications/" + created["id"]) == created
    assert history() == before_history
    amended = mark_slot_complete(
        client, PROJECT_ID, "product_identity", "Revised", expected_version=1, actor="owner", reason="Revise answer"
    )
    assert amended["version"] == 2 and amended["description"] == "Revised"
    after_history = history()
    assert after_history[:-1] == before_history and len(after_history) == len(before_history) + 1


def test_explicit_not_applicable_completes_without_an_inferred_answer(project_dir):
    row = mark_slot_complete(
        project_dir["client"],
        PROJECT_ID,
        "product_identity",
        "",
        source="not_applicable",
        expected_version=0,
        actor="owner",
        reason="Not applicable",
    )
    assert "source:not_applicable" in row["tags"] and row["authority"] == "stated"
    state = intake_status(project_dir["client"], PROJECT_ID)
    assert state["completed_slots"] == 1 and state["next_slot"] == "application_type"


@pytest.mark.parametrize("source,value", [("inferred", "Maybe"), ("owner_stated", "")])
def test_invalid_completion_source_or_empty_answer_writes_nothing(project_dir, source, value):
    before = _core_spec_count(project_dir)
    with pytest.raises(ValueError):
        mark_slot_complete(
            project_dir["client"],
            PROJECT_ID,
            "product_identity",
            value,
            source=source,
            expected_version=0,
            actor="owner",
            reason="Reject invalid answer",
        )
    assert _core_spec_count(project_dir) == before


def test_repeated_reads_use_current_facts_and_never_write_prompt_files(project_dir):
    _seed_project(project_dir, completed_slots=("product_identity",))
    before = {p: p.read_bytes() for p in project_dir["host"].rglob("*") if p.is_file()}
    for _ in range(2):
        result = _runner_result(project_dir, "core-specs", "next-question", "--project-id", PROJECT_ID, "--json")
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["slot"] == "application_type"
    assert {p: p.read_bytes() for p in project_dir["host"].rglob("*") if p.is_file()} == before


def test_retired_or_inferred_same_slot_requires_an_answer(project_dir):
    client = project_dir["client"]
    first = mark_slot_complete(
        client, PROJECT_ID, "product_identity", "Old", expected_version=0, actor="owner", reason="Old answer"
    )
    client.request(
        "PUT",
        "/v1/specifications/" + first["id"],
        body={"expected_version": 1, "actor": "owner", "reason": "Retire answer", "fields": {"status": "retired"}},
    )
    assert intake_status(client, PROJECT_ID)["next_slot"] == "product_identity"


def test_duplicate_current_slots_refuse_instead_of_selecting_one(project_dir):
    client = project_dir["client"]
    first = mark_slot_complete(
        client, PROJECT_ID, "product_identity", "One", expected_version=0, actor="owner", reason="One answer"
    )
    fields = {k: first[k] for k in ("title", "description", "scope", "tags", "authority", "application_scope")}
    client.request(
        "PUT",
        "/v1/specifications/SPEC-SECOND",
        body={"expected_version": 0, "actor": "owner", "reason": "Conflicting fixture", "fields": fields},
    )
    with pytest.raises(AuthorityClientError) as caught:
        intake_status(client, PROJECT_ID)
    assert caught.value.code == "ambiguous_core_spec"
    assert set(caught.value.details["ids"]) == {first["id"], "SPEC-SECOND"}


def test_other_project_specification_cannot_be_repurposed(project_dir):
    client = project_dir["client"]
    beta = mark_slot_complete(
        client, "PROJECT-Beta", "product_identity", "Beta", expected_version=0, actor="owner", reason="Beta answer"
    )
    with pytest.raises(AuthorityClientError) as caught:
        mark_slot_complete(
            client,
            PROJECT_ID,
            "product_identity",
            "Alpha",
            expected_version=1,
            actor="owner",
            reason="Wrong identity",
            spec_id=beta["id"],
        )
    assert caught.value.code == "core_spec_identity_conflict"
    assert client.request("GET", "/v1/specifications/" + beta["id"]) == beta
    assert _core_spec_count(project_dir) == 0


def test_opt_out_is_noninteractive_and_needs_no_authority(tmp_path):
    result = CliRunner().invoke(main, ["core-specs", "next-question", "--opt-out-core-spec-intake", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"status": "disabled"}
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "tags,authority,completed",
    [
        ([], "stated", 1),
        (["source:owner_stated"], "stated", 1),
        (["source:not_applicable"], "stated", 1),
        (["source:owner_stated", "source:needs_clarity"], "stated", 0),
        (["source:owner_stated", "source:inferred"], "stated", 0),
        (["source:owner_stated"], "inferred", 0),
    ],
)
def test_current_handle_and_authority_decide_completion_without_session_flags(project_dir, tags, authority, completed):
    client = project_dir["client"]
    record = client.request(
        "PUT",
        "/v1/specifications/SPEC-EXISTING-ANSWER",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "Existing canonical answer",
            "fields": {
                "title": "Existing answer",
                "description": "Owner product description",
                "scope": PROJECT_ID,
                "handle": f"core-spec-intake:{PROJECT_ID}:product_identity",
                "tags": tags,
                "authority": authority,
                "application_scope": "application:Alpha",
            },
        },
    )
    state = intake_status(client, PROJECT_ID)
    assert state["completed_slots"] == completed
    assert state["next_slot"] == ("application_type" if completed else "product_identity")
    assert client.request("GET", "/v1/specifications/" + record["id"]) == record


def test_mismatched_application_scope_does_not_complete_the_project_slot(project_dir):
    client = project_dir["client"]
    client.request(
        "PUT",
        "/v1/specifications/SPEC-WRONG-APPLICATION",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "Wrong application fixture",
            "fields": {
                "title": "Wrong scope",
                "description": "Wrong application",
                "scope": PROJECT_ID,
                "handle": f"core-spec-intake:{PROJECT_ID}:product_identity",
                "authority": "stated",
                "application_scope": "application:Beta",
            },
        },
    )
    assert intake_status(client, PROJECT_ID)["completed_slots"] == 0


def test_configured_opt_out_preserves_files_and_avoids_authority(tmp_path):
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="{tmp_path.as_posix()}"\n[core_spec_intake]\nenabled=false\n', encoding="utf-8"
    )
    before = config.read_bytes()
    result = CliRunner().invoke(main, ["--config", str(config), "core-specs", "status", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"status": "disabled"}
    assert config.read_bytes() == before and list(tmp_path.iterdir()) == [config]


@pytest.mark.parametrize("native_app_authority", ["first-host", "relocated/second-host"], indirect=True)
@pytest.mark.parametrize("application", ["Alpha", "Beta"])
def test_fresh_cli_then_successor_uses_each_application_at_both_roots(native_app_authority, application):
    item = native_app_authority
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PG", "GT_", "GTKB_", "GIT_"))}
    env.update(
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
    )
    command = [sys.executable, "-P", "-m", "groundtruth_kb", "--config", str(item["config"]), "core-specs"]
    answered = subprocess.run(
        [
            *command,
            "answer",
            "--project-id",
            "PROJECT-" + application,
            "--slot",
            "product_identity",
            "--value",
            application,
            "--expected-version",
            "0",
            "--actor",
            "owner",
            "--reason",
            "Explicit answer",
            "--json",
        ],
        env=env,
        cwd=item["host"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert answered.returncode == 0, answered.stdout + answered.stderr
    assert json.loads(answered.stdout)["application_scope"] == "application:" + application
    successor = subprocess.run(
        [*command, "next-question", "--project-id", "PROJECT-" + application, "--json"],
        env=env,
        cwd=item["host"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert successor.returncode == 0, successor.stdout + successor.stderr
    assert json.loads(successor.stdout)["slot"] == "application_type"
    assert not list(item["host"].rglob("*.db"))
    other = "Beta" if application == "Alpha" else "Alpha"
    assert intake_status(AuthorityClient(item["client"].url), "PROJECT-" + other)["completed_slots"] == 0


@pytest.fixture
def native_scaffold(native_app_authority):
    item = native_app_authority
    # Test-owned host inputs come from this selected checkout, never production.
    source = Path(__file__).resolve().parents[2]
    hook = item["host"] / ".githooks/reference-transaction"
    hook.parent.mkdir()
    shutil.copyfile(source / ".githooks/reference-transaction", hook)
    return item


def _initialize(item, application="Alpha", *options):
    return CliRunner().invoke(
        main,
        [
            "--config",
            str(item["config"]),
            "project",
            "init",
            application,
            "--project-id",
            "PROJECT-" + application,
            "--host-root",
            str(item["host"]),
            "--owner",
            "Qualification",
            "--no-include-ci",
            "--json",
            *options,
        ],
    )


def _files(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts
    }


@pytest.mark.parametrize("native_app_authority", ["first-host", "relocated/second-host"], indirect=True)
@pytest.mark.parametrize("application", ["Alpha", "Beta"])
def test_native_initialization_and_successor_preserve_authority_and_other_application(native_scaffold, application):
    item = native_scaffold
    client = item["client"]
    target = item["host"] / "applications" / application
    other = item["host"] / "applications" / ("Beta" if application == "Alpha" else "Alpha")
    protected = _files(other)
    project = client.request("GET", "/v1/projects/PROJECT-" + application)
    specs = client.request("GET", "/v1/specifications")
    result = _initialize(item, application)
    assert result.exit_code == 0, result.output
    value = json.loads(result.output)
    assert value["initial_question"]["name"] == "product_identity"
    assert value["canonical_writes"] == value["commits"] == 0
    assert client.request("GET", "/v1/projects/PROJECT-" + application) == project
    assert client.request("GET", "/v1/specifications") == specs
    assert _files(other) == protected
    assert not list(item["host"].rglob("*.db"))
    assert not (target / "MEMORY.md").exists()
    assert (target / ".githooks/reference-transaction").read_bytes() == (
        item["host"] / ".githooks/reference-transaction"
    ).read_bytes()
    git = subprocess.run(
        ["git", "-C", str(target), "config", "--get", "core.hooksPath"], capture_output=True, text=True, check=True
    )
    assert git.stdout.strip() == ".githooks"
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PG", "GT_", "GTKB_", "GIT_"))}
    env.update(
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
    )
    successor = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "groundtruth_kb",
            "--config",
            str(target / "groundtruth.toml"),
            "core-specs",
            "next-question",
            "--project-id",
            "PROJECT-" + application,
            "--json",
        ],
        env=env,
        cwd=other,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert successor.returncode == 0, successor.stdout + successor.stderr
    assert json.loads(successor.stdout)["slot"] == "product_identity"


def test_native_initialization_opt_out_and_dry_run_do_not_create_answers(native_scaffold):
    item = native_scaffold
    before = _files(item["host"])
    preview = _initialize(item, "Alpha", "--dry-run", "--opt-out-core-spec-intake")
    assert preview.exit_code == 0, preview.output
    assert json.loads(preview.output)["status"] == "preview"
    assert json.loads(preview.output)["initial_question"] is None
    assert _files(item["host"]) == before
    created = _initialize(item, "Alpha", "--opt-out-core-spec-intake")
    assert created.exit_code == 0, created.output
    assert json.loads(created.output)["initial_question"] is None
    config = item["host"] / "applications/Alpha/groundtruth.toml"
    answer = CliRunner().invoke(main, ["--config", str(config), "core-specs", "next-question", "--json"])
    assert answer.exit_code == 0 and json.loads(answer.output) == {"status": "disabled"}
    assert client_specifications(item) == []


def client_specifications(item):
    return item["client"].request("GET", "/v1/specifications")["records"]


@pytest.mark.parametrize("problem", ["nonempty", "marker", "hook", "foreign-project"])
def test_native_initialization_refuses_invalid_inputs_without_partial_files(native_scaffold, problem):
    item = native_scaffold
    target = item["host"] / "applications/Alpha"
    if problem == "nonempty":
        (target / "user.txt").write_text("Keep user work", encoding="utf-8")
    elif problem == "marker":
        (target / "application.toml").write_text("[malformed", encoding="utf-8")
    elif problem == "hook":
        (item["host"] / ".githooks/reference-transaction").unlink()
    options = ("--project-id", "PROJECT-Beta") if problem == "foreign-project" else ()
    before = _files(item["host"])
    result = _initialize(item, "Alpha", *options)
    assert result.exit_code != 0, result.output
    assert json.loads(result.output)["status"] == "refused"
    assert _files(item["host"]) == before
    assert client_specifications(item) == []


def test_native_doctor_reports_current_question_then_completion(native_scaffold):
    item = native_scaffold
    initialized = _initialize(item)
    assert initialized.exit_code == 0, initialized.output
    args = [
        "--config",
        str(item["config"]),
        "project",
        "doctor",
        "--project-id",
        PROJECT_ID,
        "--host-root",
        str(item["host"]),
        "--json",
    ]
    before = _files(item["host"])
    incomplete = CliRunner().invoke(main, args)
    assert incomplete.exit_code == 0, incomplete.output
    value = json.loads(incomplete.output)
    assert value["status"] == "warning"
    assert "product_identity" in value["checks"][-1]["message"]
    _seed_project(item, completed_slots=slot_names())
    complete = CliRunner().invoke(main, args)
    assert complete.exit_code == 0, complete.output
    assert json.loads(complete.output)["status"] == "pass"
    assert _files(item["host"]) == before


def _install_test_baseline(item):
    import tomllib

    source = Path(__file__).resolve().parents[2]
    host = item["host"]
    shutil.copytree(source / ".harness-baseline-configuration", host / ".harness-baseline-configuration")
    shutil.copytree(source / "scripts/harness_projection", host / "scripts/harness_projection")
    shutil.copyfile(source / "pyproject.toml", host / "pyproject.toml")
    profiles = tomllib.loads((source / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))
    manifest = tomllib.loads(
        (source / ".harness-baseline-configuration/hooks/manifest.toml").read_text(encoding="utf-8")
    )
    names = {"scripts/" + row["script"] for row in manifest["hook"] if row.get("script_root") == "project_scripts"}
    names.update(row["stdin_adapter"] for row in profiles["harnesses"].values() if row.get("stdin_adapter"))
    for name in names:
        target = host / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    return profiles


@pytest.mark.parametrize("harness", ["claude", "codex"])
def test_native_scaffold_projects_selected_baseline_without_assigning_role(native_scaffold, harness):
    item = native_scaffold
    profiles = _install_test_baseline(item)
    host_before = _files(item["host"])
    result = _initialize(item, "Alpha", "--harness", harness)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    target = item["host"] / "applications/Alpha"
    config_dir = profiles["harnesses"][harness]["config_dir"]
    manifest = json.loads((target / config_dir / ".projection-manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["paths"]) == set(payload["generated_paths"])
    assert all((target / name).is_file() for name in manifest["paths"])
    assert all(
        not (target / name).exists()
        for name in ("MEMORY.md", "groundtruth.db", "bridge", ".harness-baseline-configuration")
    )
    assert all((item["host"] / name).read_bytes() == body for name, body in host_before.items())
    native_config = target / profiles["harnesses"][harness].get("hooks_json_path", ".claude/settings.json")
    registered = native_config.read_text(encoding="utf-8")
    if harness == "codex":
        assert "applicationRoot" in registered and "Alpha" in registered
    else:
        assert "../../groundtruth-kb/.venv/Scripts/pythonw.exe" in registered
    assert "spec-before-code.py" not in registered
    assert config_dir.split("/")[0] + "/" in (target / ".gitignore").read_text(encoding="utf-8")


def test_projection_input_gap_refuses_before_scaffold_files(native_scaffold):
    item = native_scaffold
    _install_test_baseline(item)
    manifest = item["host"] / ".harness-baseline-configuration/hooks/manifest.toml"
    manifest.write_text('[[hook]]\nevent="PreToolUse"\nscript="absent-test-hook.py"\n', encoding="utf-8")
    before = _files(item["host"])
    result = _initialize(item, "Alpha", "--harness", "claude")
    assert result.exit_code != 0, result.output
    assert json.loads(result.output)["status"] == "refused"
    assert _files(item["host"]) == before


@pytest.mark.parametrize("changed", ["project", "hook", "target"])
def test_stale_scaffold_preview_refuses_without_effects(native_scaffold, changed):
    from groundtruth_kb.project.scaffold import ScaffoldOptions, apply_scaffold, plan_scaffold

    item = native_scaffold
    host = item["host"]
    options = ScaffoldOptions(
        project_name="Alpha",
        profile="local-only",
        owner="Owner",
        target_dir=host / "applications/Alpha",
        gt_kb_root=host,
        project_id=PROJECT_ID,
        authority_url=item["client"].url,
        include_ci=False,
    )
    plan = plan_scaffold(options)
    if changed == "project":
        item["client"].request(
            "PUT",
            "/v1/projects/" + PROJECT_ID,
            body={
                "kind": "project",
                "expected_version": plan.project["version"],
                "actor": "qualification",
                "reason": "Changed after preview",
                "fields": {"name": "New name"},
            },
        )
    elif changed == "hook":
        (host / ".githooks/reference-transaction").write_text("# replaced", encoding="utf-8")
    else:
        (options.target_dir / "new-user-file.txt").write_text("Preserve", encoding="utf-8")
    before = _files(host)
    with pytest.raises(ValueError):
        apply_scaffold(plan)
    assert _files(host) == before
