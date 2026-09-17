"""Current conformance: canonical sources, exact output, containment and honest gaps."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from scripts import check_harness_parity as parity

ROOT = Path(__file__).resolve().parents[2]
PROFILE = """
schema_version = 1
[baseline]
root = ".harness-baseline-configuration"
tokens = []
hook_manifest = "hooks/manifest.toml"
shared_helpers_dir = "scripts/skill-helpers"
[stamp]
text = "Derived from {baseline_root} for {harness}."
[harnesses.example]
config_dir = ".example"
skills_dir = ".example/skills"
rules_dir = ".example/rules"
hooks_dir = ".example/hooks"
project_dir_var = "EXAMPLE_PROJECT_DIR"
session_id_var = "EXAMPLE_SESSION_ID"
skill_body = "full"
rules_projection = true
hooks_projection = "settings_json"
hooks_json_path = ".example/settings.json"
[harnesses.example.hook_events]
pre_tool_use = "PreToolUse"
[harnesses.example.intent_matchers]
file_write = "Write|Edit"
"""
MANIFEST = """
schema_version = 1
[[hook]]
event = "pre_tool_use"
intents = ["file_write"]
script = "gate.py"
blocking = true
"""
SKILL = "---\nname: inspect-work\ndescription: Inspect current work.\n---\n\nUse the CLI.\n"


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


@pytest.fixture
def tree(tmp_path):
    engine = tmp_path / parity.ENGINE
    engine.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / parity.ENGINE, engine)
    write(tmp_path, "scripts/harness_projection/profiles.toml", PROFILE)
    write(tmp_path, f"{parity.BASELINE}/skills/inspect-work/SKILL.md", SKILL)
    write(tmp_path, f"{parity.BASELINE}/hooks/manifest.toml", MANIFEST)
    write(tmp_path, f"{parity.BASELINE}/hooks/gate.py", "print('gate')\n")
    write(tmp_path, f"{parity.BASELINE}/rules/work.md", "Use the CLI.\n")
    return tmp_path


def derive(tree):
    return parity._load_projector(tree).build_plan("example")


def install(tree):
    plan = derive(tree)
    assert not plan.gaps
    for rel, text in plan.writes.items():
        write(tree, rel, text)
    return plan


def report(tree, *, installed=True):
    return parity.check_harness_parity(tree, harness="example", installed=installed)


def codes(result):
    return {i["code"] for i in result["issues"]} | {
        i["code"] for target in result["harnesses"].values() for i in target["issues"]
    }


def test_exact_projection_passes_without_runtime_or_waiver_registry(tree):
    install(tree)
    result = report(tree)
    assert result["status"] == "pass", result
    assert result["operational_readiness"] == "not_evaluated"
    assert result["harnesses"]["example"]["skills"] == 1


def test_derivability_is_distinct_from_installation(tree):
    assert report(tree, installed=False)["status"] == "pass"
    assert report(tree)["status"] == "fail"
    assert "missing_output" in codes(report(tree))
    assert not (tree / ".example").exists()


@pytest.mark.parametrize("shared", [False, True])
def test_projector_refuses_a_registration_without_its_source(tree, shared):
    manifest = tree / parity.BASELINE / "hooks/manifest.toml"
    if shared:
        manifest.write_text(MANIFEST + 'script_root = "project_scripts"\n', encoding="utf-8")
    else:
        (tree / parity.BASELINE / "hooks/gate.py").unlink()
    plan = derive(tree)
    assert any("missing_hook_source" in gap and "gate.py" in gap for gap in plan.gaps)
    assert not (tree / ".example").exists()


@pytest.mark.parametrize(
    "rel", [".example/skills/inspect-work/SKILL.md", ".example/settings.json", ".example/hooks/gate.py"]
)
def test_body_tamper_with_unchanged_metadata_is_detected(tree, rel):
    install(tree)
    path = tree / rel
    path.write_bytes(path.read_bytes() + b"\nforeign mutation\n")
    before = path.read_bytes()
    result = report(tree)
    assert result["status"] == "fail"
    assert "changed_output" in codes(result)
    assert path.read_bytes() == before


def test_new_baseline_bytes_invalidate_previously_matching_output(tree):
    install(tree)
    write(tree, f"{parity.BASELINE}/rules/work.md", "Changed current obligation.\n")
    assert "changed_output" in codes(report(tree))


def test_unmanaged_output_is_reported_and_preserved(tree):
    install(tree)
    foreign = write(tree, ".example/local.txt", "unrelated bytes")
    assert "unmanaged_output" in codes(report(tree))
    assert foreign.read_text() == "unrelated bytes"


@pytest.mark.parametrize("existing", [False, True])
def test_native_toml_configuration_is_derived_and_checked(tree, existing):
    settings = 'approval_policy = "on-request"\n[features]\nhooks = true\n'
    profile_path = tree / "scripts/harness_projection/profiles.toml"
    profile_path.write_text(
        PROFILE.replace(
            'hooks_json_path = ".example/settings.json"',
            'hooks_json_path = ".example/settings.json"\nconfig_toml = """\n' + settings + '"""',
        ),
        encoding="utf-8",
    )
    config = tree / ".example/config.toml"
    if existing:
        write(tree, ".example/config.toml", "# Earlier local representation\n" + settings)
    neighbor = write(tree, "unrelated.txt", "Preserve this work")
    engine = parity._load_projector(tree)
    before = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert engine.run("example", "validate") == 0
    assert engine.run("example", "dry-run") == 0
    assert {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()} == before
    assert engine.run("example", "write") == 0
    import tomllib

    assert config.is_file()
    assert tomllib.loads(config.read_text(encoding="utf-8")) == tomllib.loads(settings)
    assert "Derived from" in config.read_text(encoding="utf-8")
    assert ".example/config.toml" in json.loads((tree / ".example/.projection-manifest.json").read_text())["paths"]
    assert report(tree)["status"] == "pass"
    first = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert engine.run("example", "write") == 0
    assert {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()} == first
    assert neighbor.read_text() == "Preserve this work"
    config.write_text(settings.replace("true", "false"), encoding="utf-8")
    assert "changed_output" in codes(report(tree))
    assert engine.run("example", "check") == 1


@pytest.mark.parametrize("value", ["false", "{}", '"""broken = ["""', "'mode = \"{{UNKNOWN}}\"'"])
def test_invalid_native_configuration_refuses_without_effects(tree, value):
    profile_path = tree / "scripts/harness_projection/profiles.toml"
    profile_path.write_text(
        PROFILE.replace(
            'hooks_json_path = ".example/settings.json"',
            'hooks_json_path = ".example/settings.json"\nconfig_toml = ' + value,
        ),
        encoding="utf-8",
    )
    write(tree, ".example/config.toml", 'existing = "preserve"\n')
    engine = parity._load_projector(tree)
    before = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert engine.build_plan("example").gaps
    assert engine.run("example", "write") == 2
    assert {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()} == before
    assert report(tree)["status"] == "fail"


def test_removed_baseline_output_is_detected_without_deleting_it(tree):
    install(tree)
    (tree / parity.BASELINE / "rules/work.md").unlink()
    result = report(tree)
    assert "retired_output" in codes(result)
    assert (tree / ".example/rules/work.md").is_file()


@pytest.mark.parametrize("failure", ["missing_source", "missing_event", "no_registration", "wrong_root"])
def test_declared_hook_obligations_cannot_disappear(tree, failure):
    profile = tree / "scripts/harness_projection/profiles.toml"
    if failure == "missing_source":
        (tree / parity.BASELINE / "hooks/gate.py").unlink()
    elif failure == "missing_event":
        profile.write_text(PROFILE.replace('pre_tool_use = "PreToolUse"', ""), encoding="utf-8")
    elif failure == "no_registration":
        profile.write_text(PROFILE.replace('hooks_projection = "settings_json"', ""), encoding="utf-8")
    else:
        profile.write_text(
            PROFILE.replace('hooks_dir = ".example/hooks"', 'hooks_dir = ".peer/hooks"'), encoding="utf-8"
        )
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"missing_hook_source", "missing_hook_registration", "projector_gap", "invalid_projection"}


@pytest.mark.parametrize("correction", ["renamed", "duplicate", "missing_description", "missing_header", "empty"])
def test_skill_identity_and_frontmatter_cannot_be_supplied_by_aliases(tree, correction):
    path = tree / parity.BASELINE / "skills/inspect-work/SKILL.md"
    text = SKILL
    if correction == "renamed":
        text = text.replace("name: inspect-work", "name: alias")
    elif correction == "duplicate":
        text = text.replace("name: inspect-work", "name: inspect-work\nname: alias")
    elif correction == "missing_description":
        text = text.replace("description: Inspect current work.\n", "")
    elif correction == "missing_header":
        text = text.removeprefix("---\n")
    else:
        path.unlink()
    if correction != "empty":
        path.write_text(text, encoding="utf-8")
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"skill_identity", "invalid_projection", "empty_baseline"}


@pytest.mark.parametrize("defect", ["missing", "syntax", "import"])
def test_unavailable_projector_is_typed_failure(tree, defect):
    path = tree / parity.ENGINE
    if defect == "missing":
        path.unlink()
    else:
        path.write_text("def broken(\n" if defect == "syntax" else "raise ImportError('local defect')\n")
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert "unavailable_projector" in codes(result)


def test_cached_module_does_not_replace_selected_projector(tree, monkeypatch):
    forged = ModuleType("_gtkb_parity_projector")
    forged.load_profiles = lambda: (_ for _ in ()).throw(AssertionError("forged cache used"))
    monkeypatch.setitem(sys.modules, "_gtkb_parity_projector", forged)
    assert report(tree, installed=False)["status"] == "pass"


def test_pending_target_is_included_and_blocks_all_target_result(tree):
    path = tree / "scripts/harness_projection/profiles.toml"
    path.write_text(PROFILE + '\n[harnesses.pending]\nstatus = "profile_pending"\nconfig_dir = ".pending"\n')
    result = parity.check_harness_parity(tree, harness="all", installed=False)
    assert set(result["harnesses"]) == {"example", "pending"}
    assert result["status"] == "fail"
    assert result["harnesses"]["example"]["status"] == "pass"


@pytest.mark.parametrize("target", ["", "unknown"])
def test_no_implicit_or_fallback_target(tree, target):
    result = parity.check_harness_parity(tree, harness=target, installed=False)
    assert result["status"] == "fail"
    assert not result["harnesses"]


@pytest.mark.parametrize(
    "command,expected",
    [
        ('python -B ".example/hooks/gate.py"', True),
        ('python -B "$EXAMPLE_PROJECT_DIR/.example/hooks/gate.py"', True),
        ('python -B ".example/hooks/gate.py.backup"', False),
        ('python -B "foreign/.example/hooks/gate.py"', False),
        ('python -B ".peer/hooks/gate.py"', False),
    ],
)
def test_hook_registration_matches_full_path_argument(command, expected):
    assert parity._references_script(command, ".example/hooks/gate.py", "EXAMPLE_PROJECT_DIR") is expected


def test_hook_in_unrelated_json_or_wrong_event_does_not_prove_registration(tree, monkeypatch):
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    original = plan.writes[".example/settings.json"]
    settings = json.loads(original)
    settings["hooks"]["Stop"] = settings["hooks"].pop("PreToolUse")
    plan.writes[".example/settings.json"] = json.dumps(settings)
    plan.writes[".example/unrelated.json"] = original
    monkeypatch.setattr(engine, "build_plan", lambda _: plan)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    assert "missing_hook_registration" in codes(report(tree, installed=False))


def test_plan_cannot_write_into_peer_root(tree, monkeypatch):
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    plan.writes[".peer/private.md"] = "wrong destination"
    monkeypatch.setattr(engine, "build_plan", lambda _: plan)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    assert "invalid_projection" in codes(report(tree, installed=False))
    assert not (tree / ".peer").exists()


def test_direct_cli_ignores_conflicting_scripts_package(tree):
    shadow = tree / "shadow"
    write(shadow, "scripts/__init__.py", "raise ImportError('foreign scripts package')\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(shadow)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_harness_parity.py"),
            "--project-root",
            str(tree),
            "--harness",
            "example",
            "--validate",
            "--json",
        ],
        env=env,
        cwd=tree,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout)["status"] == "pass"


@pytest.mark.parametrize("value", ["42", '["gate.py"]', '"../gate.py"', '"/gate.py"', '"C:/gate.py"', '""'])
def test_invalid_declared_hook_source_is_a_plan_gap_without_registration(tree, value):
    manifest = tree / ".harness-baseline-configuration/hooks/manifest.toml"
    manifest.write_text(MANIFEST.replace('script = "gate.py"', f"script = {value}"), encoding="utf-8")
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    assert any("invalid_hook_source" in gap for gap in plan.gaps)
    assert not json.loads(plan.writes[".example/settings.json"])["hooks"]


def test_cli_requires_explicit_target():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_harness_parity.py")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2


def test_declared_former_file_is_drift_until_projector_removes_it(tree, monkeypatch):
    install(tree)
    old = write(tree, ".former/hooks/retired.py", "obsolete output")
    neighbor = write(tree, ".former/hooks/local.py", "preserve local work")
    engine = parity._load_projector(tree)
    profiles = engine.load_profiles()
    profiles["harnesses"]["example"]["leftover_paths"] = [".former/hooks/retired.py"]
    monkeypatch.setattr(engine, "load_profiles", lambda: profiles)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    assert report(tree, installed=False)["status"] == "pass"
    assert codes(report(tree)) == {"retired_output"}
    assert old.read_text() == "obsolete output"
    assert engine.run("example", "write") == 0
    assert report(tree)["status"] == "pass"
    assert not old.exists()
    assert neighbor.read_text() == "preserve local work"


@pytest.mark.parametrize("path,declared", [(".peer/private.md", True), (".peer", True), (".former/local.md", False)])
def test_retired_removal_cannot_escape_into_peer_or_unlisted_material(tree, monkeypatch, path, declared):
    engine = parity._load_projector(tree)
    profiles = engine.load_profiles()
    profiles["harnesses"]["peer"] = {"config_dir": ".peer"}
    if declared:
        profiles["harnesses"]["example"]["leftover_paths"] = [path]
    monkeypatch.setattr(engine, "load_profiles", lambda: profiles)
    plan = engine.build_plan("example")
    plan.removes = [path]
    monkeypatch.setattr(engine, "build_plan", lambda _: plan)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    assert "invalid_projection" in codes(report(tree, installed=False))
    assert not (tree / ".peer").exists()
