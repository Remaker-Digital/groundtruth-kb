"""Native application initialization: profiles, CI/container/cloud viability, starter specifications.

These cases carry the retained duties of the retired SQLite-era scaffold,
desktop bootstrap and golden-fixture tests. Every application is created for an
explicitly selected execution project against real native HTTP on the
disposable database; providers and harness names never assign a role.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import groundtruth_kb
from groundtruth_kb.authority_client import AuthorityClientError
from groundtruth_kb.project import scaffold as scaffold_module
from groundtruth_kb.project.core_spec_intake import mark_slot_complete
from groundtruth_kb.project.profiles import get_profile
from groundtruth_kb.project.scaffold import (
    ci_tier,
    enumerate_scaffold_outputs,
    initialize_application,
    package_name_slug,
    plan_scaffold,
    scaffold_project,
)
from groundtruth_kb.project.spec_scaffold import scaffold_config, scaffold_specs
from groundtruth_kb.providers.schema import get_provider, list_providers

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]
# Every hosted case runs for a host at a plain location and at a nested location with a space (M04 second host
# location); the pure helper case has no host.
both_host_locations = pytest.mark.parametrize(
    "native_app_authority", ["first-host", "relocated location/second host"], indirect=True
)
PROFILES = ("local-only", "dual-agent", "dual-agent-webapp")
LEAK_PREFIXES = (
    ".gtkb-state/",
    ".claude/worktrees/",
    "groundtruth-kb/",
    "harness-state/",
    "independent-progress-assessments/",
)


def _created(target: Path) -> dict[str, bytes]:
    """Files created by initialization; the registration marker and Git metadata are excluded."""
    return {
        p.relative_to(target).as_posix(): p.read_bytes()
        for p in target.rglob("*")
        if p.is_file() and ".git" not in p.parts and p.relative_to(target).as_posix() != "application.toml"
    }


def _steps(text: str) -> list[str]:
    parsed = yaml.safe_load(text)
    return [json.dumps(step).lower() for job in parsed["jobs"].values() for step in job["steps"]]


def _workflows(target: Path) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in (target / ".github/workflows").glob("*.yml")}


# ---------------------------------------------------------------------------
# Profiles, CI tiers, containers and cloud stubs (retained test_scaffold_ci_tiers /
# test_scaffold_smoke / test_scaffold_project duties)
# ---------------------------------------------------------------------------


def test_ci_tier_and_slug_helpers() -> None:
    assert ci_tier(get_profile("local-only")) == "minimal"
    assert ci_tier(get_profile("dual-agent")) == "standard"
    assert ci_tier(get_profile("dual-agent-webapp")) == "full"
    assert package_name_slug("My Test Project") == "my-test-project"
    assert package_name_slug("  Alpha__App!! ") == "alpha-app"


@pytest.mark.parametrize("profile", PROFILES)
@both_host_locations
def test_profile_creates_minimum_files_and_viable_ci_workflows(native_application, profile) -> None:
    target = native_application.scaffold("Alpha", profile=profile, include_ci=True, python_version="3.12")
    created = _created(target)
    assert set(enumerate_scaffold_outputs(profile)) <= set(created)
    workflows = _workflows(target)
    tier = ci_tier(get_profile(profile))
    expected = {"minimal": {"test.yml"}, "standard": {"test.yml"}, "full": {"test.yml", "build.yml", "deploy.yml"}}
    assert set(workflows) == expected[tier]
    for name, text in workflows.items():
        assert isinstance(yaml.safe_load(text), dict), name
        assert not re.search(r"\{\{[A-Z_]+\}\}", text), name
        if name == "test.yml":
            assert 'python-version: "3.12"' in text
    test_steps = _steps(workflows["test.yml"])
    assert any("ruff check" in step for step in test_steps)
    if tier == "minimal":
        assert not any("docker" in step or "pytest" in step or "mypy" in step for step in test_steps)
    if tier == "standard":
        assert not any("docker" in step for step in test_steps)
    if tier == "full":
        assert any("pytest" in step for step in test_steps)
        assert any("docker" in step for step in _steps(workflows["build.yml"]))
    profile_files = set(created)
    bridge_files = {"BRIDGE-INVENTORY.md", "bridge-os-poller-setup-prompt.md", "bridge/.gitkeep", "groundtruth.db"}
    assert not bridge_files & profile_files, "retired SQLite-era bridge files must not be created"
    if get_profile(profile).includes_docker:
        assert {"Dockerfile", "docker-compose.yml", ".env.example", "tests/test_smoke.py"} <= profile_files
        for name in ("Dockerfile", "docker-compose.yml", ".env.example"):
            assert b"{{" not in created[name], name
    else:
        assert "Dockerfile" not in profile_files
    for name, body in created.items():
        assert not any(name.startswith(prefix) for prefix in LEAK_PREFIXES), name
        assert b"Agent Red" not in body and b"remaker" not in body.lower(), name


@both_host_locations
def test_no_include_ci_and_integration_files(native_application) -> None:
    plain = native_application.scaffold("Alpha", include_ci=False, integrations=False)
    assert not (plain / ".github").exists()
    integrated = native_application.scaffold("Beta", include_ci=False, integrations=True)
    assert (integrated / ".github/dependabot.yml").is_file()
    assert (integrated / ".coderabbitai.yaml").is_file()
    assert "{{" not in (integrated / ".github/dependabot.yml").read_text(encoding="utf-8")


@both_host_locations
def test_seed_example_and_webapp_stubs(native_application) -> None:
    seeded = native_application.scaffold("Alpha", seed_example=True)
    assert "def create_task" in (seeded / "src/tasks.py").read_text(encoding="utf-8")
    assert (seeded / "tests/test_tasks.py").is_file()
    plain = native_application.scaffold("Beta", profile="dual-agent-webapp", seed_example=False)
    assert not (plain / "src/tasks.py").exists()
    assert (plain / "tests/test_smoke.py").is_file() and (plain / "src/__init__.py").is_file()
    assert (plain / "pyproject.toml").read_text(encoding="utf-8").startswith('[project]\nname = "beta"')


@both_host_locations
def test_webapp_scaffold_pytest_exits_zero(native_application) -> None:
    target = native_application.scaffold("Alpha", profile="dual-agent-webapp", seed_example=True)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "pytest",
            "tests/",
            "-q",
            "--tb=short",
            "-p",
            "no:cacheprovider",
            "-o",
            "addopts=",
        ],
        cwd=target,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout


@both_host_locations
def test_cloud_provider_stubs_only_for_cloud_profiles(native_application) -> None:
    for provider in ("azure", "aws", "gcp"):
        assert "infrastructure/terraform/main.tf" in enumerate_scaffold_outputs(
            "dual-agent-webapp", cloud_provider=provider
        )
    with pytest.raises(ValueError, match="cloud deployment"):
        enumerate_scaffold_outputs("local-only", cloud_provider="azure")
    with pytest.raises(ValueError, match="cloud deployment"):
        plan_scaffold(native_application.options("Alpha", cloud_provider="aws"))
    assert _created(native_application.target("Alpha")) == {}
    target = native_application.scaffold("Alpha", profile="dual-agent-webapp", cloud_provider="gcp")
    main_tf = (target / "infrastructure/terraform/main.tf").read_text(encoding="utf-8")
    assert 'provider "google"' in main_tf and "{{" not in main_tf
    assert (target / "infrastructure/terraform/variables.tf").is_file()
    plain = native_application.scaffold("Beta", profile="dual-agent-webapp", cloud_provider="none")
    assert not (plain / "infrastructure").exists()
    assert 'cloud_provider = "gcp"' in (target / "groundtruth.toml").read_text(encoding="utf-8")


@both_host_locations
def test_equal_inputs_produce_identical_bytes(native_application) -> None:
    """Deterministic output replaces the retired golden fixtures."""
    first = _created(native_application.scaffold("Alpha", profile="dual-agent", include_ci=True))
    second = _created(native_application.scaffold("Beta", profile="dual-agent", include_ci=True))
    different = {name for name in first if first[name] != second.get(name)}
    assert different <= {
        "groundtruth.toml",
        "README.md",
        "pyproject.toml",
        "src/__init__.py",
        ".gtkb-app-isolation.json",
    }
    for name in ("groundtruth.toml", "README.md", ".gtkb-app-isolation.json"):
        assert first[name].replace(b"Alpha", b"Beta").replace(b"alpha", b"beta") == second[name]


# ---------------------------------------------------------------------------
# Refusals (retained test_scaffold_isolation / desktop-bootstrap duties)
# ---------------------------------------------------------------------------


@both_host_locations
def test_refuses_target_outside_the_registered_application_root(native_application, tmp_path) -> None:
    before = native_application.facts()
    for target in (tmp_path / "elsewhere", native_application.host / "applications/Gamma"):
        target.mkdir(exist_ok=True)
        with pytest.raises(ValueError, match="registered application root|Register the application"):
            scaffold_project(native_application.options("Alpha", target_dir=target))
        assert not (target / "groundtruth.toml").exists()
    with pytest.raises(ValueError, match="exact registered application root"):
        scaffold_project(native_application.options("Gamma", project_id="PROJECT-Alpha"))
    assert native_application.facts() == before


@both_host_locations
def test_cli_refuses_mismatched_host_root_and_unknown_project(native_application, tmp_path) -> None:
    other = tmp_path / "other-host"
    other.mkdir()
    subprocess.run(["git", "init", "-q", str(other)], check=True)
    refused = native_application.invoke(
        "project", "init", "Alpha", "--project-id", "PROJECT-Alpha", "--host-root", str(other), "--owner", "Q", "--json"
    )
    assert refused.exit_code == 1
    assert json.loads(refused.output)["status"] == "refused"
    assert not (other / "applications").exists()
    missing = native_application.invoke(
        "project",
        "init",
        "Alpha",
        "--project-id",
        "PROJECT-Missing",
        "--host-root",
        str(native_application.host),
        "--owner",
        "Q",
        "--json",
    )
    assert missing.exit_code == 1 and json.loads(missing.output)["error"]["code"] == "not_found"
    assert _created(native_application.target("Alpha")) == {}


@both_host_locations
def test_existing_application_and_nonempty_target_are_refused(native_application) -> None:
    target = native_application.scaffold("Alpha")
    with pytest.raises(ValueError, match="gt project upgrade"):
        scaffold_project(native_application.options("Alpha"))
    refused = native_application.invoke(
        "project",
        "init",
        "Alpha",
        "--project-id",
        "PROJECT-Alpha",
        "--host-root",
        str(native_application.host),
        "--owner",
        "Q",
        "--json",
    )
    assert refused.exit_code == 1 and "upgrade" in json.loads(refused.output)["error"]["message"]
    occupied = native_application.target("Beta")
    (occupied / "notes.txt").write_text("already here", encoding="utf-8")
    with pytest.raises(ValueError, match="not empty"):
        scaffold_project(native_application.options("Beta"))
    assert sorted(p.name for p in occupied.iterdir()) == [".git", "application.toml", "notes.txt"]
    assert (target / "groundtruth.toml").is_file()


@both_host_locations
def test_providers_select_configuration_never_roles(native_application) -> None:
    """Provider records remain a catalog; nothing generated maps a provider to Prime Builder or Loyal Opposition."""
    assert get_provider("claude-code").provider_id == "claude-code"
    assert {provider.provider_id for provider in list_providers()} >= {"claude-code", "codex"}
    with pytest.raises(ValueError):
        get_provider("unknown-provider")
    native_application.stage_baseline()
    target = native_application.scaffold("Alpha", harnesses=("claude",))
    created = _created(target)
    assert any(name.startswith(".claude/") for name in created)
    assert "AGENTS.md" not in created and "CLAUDE.md" not in created
    for name, body in created.items():
        text = body.decode("utf-8", errors="replace")
        assert "PRIME_PROVIDER" not in text and "LO_PROVIDER" not in text, name
    readme = created["README.md"].decode("utf-8")
    assert "The selected harness does not determine that role" in readme
    assert ".claude/" in created[".gitignore"].decode("utf-8")


def _hook_commands(settings: dict) -> list[str]:
    return [
        handler.get("command", "")
        for groups in settings.get("hooks", {}).values()
        for group in groups
        for handler in group.get("hooks", [])
    ]


@both_host_locations
def test_selected_claude_harness_registers_no_automatic_intake_hook(native_application) -> None:
    """Intake stays an explicit CLI step: no emitted registration classifies prompts automatically."""
    native_application.stage_baseline()
    created = native_application.init("Alpha", "--profile", "dual-agent", "--harness", "claude")
    assert ".claude/settings.json" in created["generated_paths"]
    settings = json.loads((native_application.target("Alpha") / ".claude/settings.json").read_text(encoding="utf-8"))
    commands = _hook_commands(settings)
    assert commands, "the selected harness registers its hooks"
    assert not any("intake" in command.lower() for command in commands), commands


RECOGNIZED_HOOK_EVENTS = {"PreToolUse", "SessionStart", "UserPromptSubmit", "PostToolUse", "Stop"}
BRIDGE_RULE_FILES = ("file-bridge-protocol.md", "bridge-essential.md", "deliberation-protocol.md")
RETIRED_OWNER_INPUT_PATHS = (
    ".claude/hooks/owner-decision-capture.py",
    "memory/pending-owner-decisions.md",
    ".claude/skills/gtkb-decision-capture",
    ".claude/skills/decision-capture",
    ".groundtruth/formal-artifact-approvals",
    ".codex/hooks.json",
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX",
)


@pytest.fixture()
def claude_application(native_application):
    """Alpha initialized through the CLI with the Claude harness selected on the dual-agent profile."""
    native_application.stage_baseline()
    created = native_application.init("Alpha", "--profile", "dual-agent", "--harness", "claude")
    return native_application, created, native_application.target("Alpha")


@both_host_locations
def test_selected_claude_harness_settings_keep_the_nested_schema_and_safety_gates(claude_application) -> None:
    """settings.json keeps event -> matcher group -> handler lists and registers the independent safety gates;
    it registers no owner-decision capture and no automatic intake, and no local settings file is written."""
    _, created, target = claude_application
    assert ".claude/settings.json" in created["generated_paths"]
    settings_text = (target / ".claude/settings.json").read_text(encoding="utf-8")
    settings = json.loads(settings_text)
    assert set(settings["hooks"]) & RECOGNIZED_HOOK_EVENTS, list(settings["hooks"])
    for event, groups in settings["hooks"].items():
        assert isinstance(groups, list), event
        assert all(isinstance(group.get("hooks"), list) for group in groups), event
    commands = _hook_commands(settings)
    assert any("credential-scan.py" in command for command in commands)
    assert any("destructive-gate.py" in command for command in commands)
    # No automatic prompt or startup producer: intake, gov09 capture and approval gates are retired.
    assert not settings["hooks"].get("SessionStart") and not settings["hooks"].get("UserPromptSubmit")
    assert not any("artifact-approval" in command for command in commands)
    assert not list((target / ".claude/hooks").glob("*classifier.py"))
    assert not list((target / ".claude/hooks").glob("*artifact-approval*"))
    assert not (target / ".claude/hooks/gov09-capture.py").exists()
    assert "owner-decision" not in settings_text
    for retired in RETIRED_OWNER_INPUT_PATHS:
        assert not (target / retired).exists(), retired
    assert not list((target / ".claude/rules").glob("CODEX-*.md"))
    assert not (target / ".claude/settings.local.json").exists()


@both_host_locations
def test_selected_claude_harness_projects_current_skills_and_bridge_rules(claude_application) -> None:
    """The projected skills are the neutral baseline: native bridge proposals without a file writer, spec intake
    with its helper and the bridge rule files; authored files and bridge rules never name the platform's own app."""
    _, created, target = claude_application
    skill = target / ".claude/skills/gtkb-bridge-propose/SKILL.md"
    assert "gt bridge deliver" in skill.read_text(encoding="utf-8")
    assert not (target / ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py").exists()
    assert (target / ".claude/skills/gtkb-spec-intake/SKILL.md").read_text(encoding="utf-8").strip()
    helper = (target / ".claude/skills/gtkb-spec-intake/helpers/spec_intake.py").read_text(encoding="utf-8")
    assert all(f"def {name}(" in helper for name in ("capture_candidate", "confirm_candidate", "reject_candidate"))
    for rule in BRIDGE_RULE_FILES:
        text = (target / ".claude/rules" / rule).read_text(encoding="utf-8")
        assert "Agent Red" not in text, rule
    generated = set(created["generated_paths"])
    for name, body in _created(target).items():
        if name not in generated:
            assert "Agent Red" not in body.decode("utf-8", errors="replace"), name


@both_host_locations
def test_derived_harness_configuration_is_ignored_and_the_derived_cache_too(claude_application) -> None:
    """The host-specific projection is regenerated by upgrade, never tracked; the search cache is derived."""
    _, _, target = claude_application
    lines = [line.strip() for line in (target / ".gitignore").read_text(encoding="utf-8").splitlines()]
    assert ".claude/" in lines and ".groundtruth-chroma/" in lines
    assert ".githooks/" not in lines and "settings.json" not in lines


@both_host_locations
def test_initialization_leaves_package_templates_unchanged(native_application) -> None:
    """Creating an application reads the package templates and never writes into them."""
    templates = groundtruth_kb.get_templates_dir()
    before = {p.relative_to(templates).as_posix(): p.read_bytes() for p in templates.rglob("*") if p.is_file()}
    native_application.scaffold("Beta", profile="dual-agent-webapp")
    after = {p.relative_to(templates).as_posix(): p.read_bytes() for p in templates.rglob("*") if p.is_file()}
    assert after == before


@both_host_locations
def test_application_without_a_selected_harness_owns_no_harness_settings(native_application) -> None:
    """Without a selected harness nothing can register hooks: no .claude, .codex or settings.local.json exists."""
    target = native_application.scaffold("Beta", profile="local-only")
    created = _created(target)
    assert created
    assert not any(name.startswith((".claude/", ".codex/")) or name.endswith("settings.local.json") for name in created)
    assert not (target / ".claude").exists()


# ---------------------------------------------------------------------------
# Starter specifications (retained minimal/full spec-scaffold duties)
# ---------------------------------------------------------------------------


def _project_specs(native_application, project_id="PROJECT-Alpha"):
    return native_application.client.request("GET", "/v1/specifications", query={"scope": project_id})["records"]


@both_host_locations
def test_minimal_and_full_starter_specifications_are_inferred_and_skipped_on_repeat(native_application) -> None:
    client = native_application.client
    preview = scaffold_specs(client, "PROJECT-Alpha", scaffold_config("minimal"))
    assert preview.dry_run and len(preview.generated) == 4 and preview.canonical_writes == 0
    assert _project_specs(native_application) == []
    applied = scaffold_specs(client, "PROJECT-Alpha", scaffold_config("minimal"), dry_run=False)
    assert applied.canonical_writes == 4
    records = _project_specs(native_application)
    assert len(records) == 4
    assert {row["handle"] for row in records} == {
        "scaffold:PROJECT-Alpha:test-discipline",
        "scaffold:PROJECT-Alpha:readme-exists",
        "scaffold:PROJECT-Alpha:ci-config",
        "scaffold:PROJECT-Alpha:no-aws-keys",
    }
    assert all(row["authority"] == "inferred" and row["application_scope"] == "application:Alpha" for row in records)
    assert all(row["scope"] == "PROJECT-Alpha" for row in records)
    repeated = scaffold_specs(client, "PROJECT-Alpha", scaffold_config("full"), dry_run=False)
    assert len(repeated.skipped) == 4 and len(repeated.generated) == 2
    assert {row["template_id"] if "template_id" in row else row["id"].split(":")[0] for row in repeated.generated} == {
        "AI-SCAFFOLD-01",
        "COMP-SCAFFOLD-01",
    }
    assert len(_project_specs(native_application)) == 6
    assert _project_specs(native_application, "PROJECT-Beta") == []
    assert set(applied.quality_summary) == {"gold", "silver", "bronze", "needs-work"}
    with pytest.raises(ValueError, match="minimal or full"):
        scaffold_config("azure-enterprise")


@both_host_locations
def test_init_with_spec_scaffold_populates_the_authority_and_keeps_intake_open(native_application) -> None:
    result = native_application.init("Alpha", "--spec-scaffold", "minimal")
    assert result["status"] == "created" and result["canonical_writes"] == 4
    assert result["specifications"]["profile"] == "minimal" and len(result["specifications"]["generated"]) == 4
    assert result["initial_question"]["name"] == "product_identity", "inferred records never answer intake"
    assert len(_project_specs(native_application)) == 4
    preview = native_application.init("Beta", "--spec-scaffold", "full", "--dry-run")
    assert preview["status"] == "preview" and len(preview["specifications"]) == 6 and preview["canonical_writes"] == 0
    assert _project_specs(native_application, "PROJECT-Beta") == []
    assert not (native_application.target("Beta") / "groundtruth.toml").exists()


@both_host_locations
def test_fresh_scaffold_assertions_pass_against_the_authority(native_application) -> None:
    """The retained ``gt assert`` viability duty: starter assertions hold on the fresh files."""
    target = native_application.scaffold("Alpha", include_ci=True, seed_example=True, spec_scaffold="minimal")
    result = native_application.invoke("assert", "--json", config=target / "groundtruth.toml")
    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    assert summary["aggregate_result"] == "PASS"
    assert summary["total_specs"] == 4 and summary["passed"] == 4 and summary["failed"] == 0
    for command in (["scaffold", "specs", "--project-id", "PROJECT-Alpha", "--profile", "minimal", "--json"],):
        report = native_application.invoke(*command)
        assert report.exit_code == 0, report.output
        assert len(json.loads(report.output)["skipped"]) == 4


# ---------------------------------------------------------------------------
# Initial question freshness and truthful reporting after effects
# ---------------------------------------------------------------------------


@both_host_locations
def test_initial_question_is_read_after_creation_not_from_the_preview(native_application) -> None:
    options = native_application.options("Alpha")
    plan = plan_scaffold(options)
    assert plan.initial_question["name"] == "product_identity"
    mark_slot_complete(
        native_application.client,
        "PROJECT-Alpha",
        "product_identity",
        "Answered while files were being created",
        expected_version=0,
        actor="owner",
        reason="Concurrent explicit answer",
    )
    created = initialize_application(options, plan=plan)
    assert created.initial_question["name"] == "application_type"
    assert created.intake == {"status": "incomplete", "completed_slots": 1, "total_slots": 12}
    follow_up = native_application.invoke(
        "core-specs",
        "next-question",
        "--project-id",
        "PROJECT-Alpha",
        "--json",
        config=created.target / "groundtruth.toml",
    )
    assert json.loads(follow_up.output)["slot"] == "application_type"


@both_host_locations
def test_created_files_are_reported_when_the_later_intake_read_fails(native_application, monkeypatch) -> None:
    options = native_application.options("Alpha")
    plan = plan_scaffold(options)
    original = scaffold_module.intake_status

    def failing(client, project_id):
        raise AuthorityClientError("authority_unavailable", "simulated outage after creation")

    monkeypatch.setattr(scaffold_module, "intake_status", failing)
    created = initialize_application(options, plan=plan)
    monkeypatch.setattr(scaffold_module, "intake_status", original)
    assert created.initial_question is None
    assert created.intake["status"] == "unavailable" and created.intake["error"]["code"] == "authority_unavailable"
    assert created.warnings and "core-specs next-question" in created.warnings[0]
    assert set(created.paths) == set(_created(created.target))
    assert (created.target / "groundtruth.toml").is_file()


@both_host_locations
def test_created_files_are_reported_when_starter_specifications_fail(native_application, monkeypatch) -> None:
    options = native_application.options("Alpha", spec_scaffold="minimal")
    plan = plan_scaffold(options)

    def failing(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "simulated outage while writing starter specifications")

    monkeypatch.setattr(scaffold_module, "scaffold_specs", failing)
    created = initialize_application(options, plan=plan)
    assert created.specifications is None and created.canonical_writes == 0
    assert created.specification_error["code"] == "authority_unavailable"
    assert any("gt scaffold specs --apply" in warning for warning in created.warnings)
    assert created.initial_question["name"] == "product_identity", "the intake read still ran"
    assert set(created.paths) == set(_created(created.target))
    assert _project_specs(native_application) == []


@both_host_locations
def test_cli_init_reports_created_files_and_warning_when_intake_read_fails(native_application, monkeypatch) -> None:
    calls = {"count": 0}
    original = scaffold_module.intake_status

    def flaky(client, project_id):
        calls["count"] += 1
        if calls["count"] > 1:
            raise AuthorityClientError("authority_unavailable", "simulated outage after creation")
        return original(client, project_id)

    monkeypatch.setattr(scaffold_module, "intake_status", flaky)
    result = native_application.init("Alpha")
    assert result["status"] == "created" and result["initial_question"] is None
    assert result["intake"]["status"] == "unavailable"
    assert result["warnings"] == ["The intake read after initialization failed; run core-specs next-question"]
    assert set(result["paths"]) == set(_created(native_application.target("Alpha")))


@both_host_locations
def test_dry_run_creates_nothing_and_reports_the_preview(native_application) -> None:
    before = native_application.facts()
    preview = native_application.init("Alpha", "--dry-run", "--spec-scaffold", "full", "--seed-example")
    assert preview["status"] == "preview" and preview["initial_question"]["name"] == "product_identity"
    assert "src/tasks.py" in preview["paths"] and len(preview["specifications"]) == 6
    assert _created(native_application.target("Alpha")) == {}
    assert native_application.facts() == before


@both_host_locations
def test_fresh_context_reads_the_same_question_through_the_installed_cli(native_application) -> None:
    created = native_application.init("Alpha")
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PG", "GT_", "GTKB_", "GIT_"))}
    env.update(
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "groundtruth_kb",
            "--config",
            str(native_application.target("Alpha") / "groundtruth.toml"),
            "core-specs",
            "next-question",
            "--project-id",
            "PROJECT-Alpha",
            "--json",
        ],
        env=env,
        cwd=native_application.target("Beta"),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["question"] == created["initial_question"]["prompt"]
