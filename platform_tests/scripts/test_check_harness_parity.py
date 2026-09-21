"""Current conformance: canonical sources, exact output, containment and honest gaps.

M15 stage 1 (owner ruling D15 as amended by R3; D34 rulings R1-R15): a projection is
the minimum a host's limitation requires - registrations and pointers only, never
copies. The fixture declares the D15 shape (one skills source at ``.agents/skills``,
hook scripts run in place from the baseline, tracked root pointers declared in
``[root_pointers]``) and the cases pin every finding the acceptance checker reports:
the classification pass (``unclassified_output``), the stub contract
(``skill_frontmatter_drift``, ``skill_stub_body``, ``skill_identity``,
``unexpected_skill_copy``), the registration identity argument
(``missing_identity_argument``, R10), ``baseline_token_residue`` (scoped to the skills
source in stage 1) and ``declared_pointer_drift`` (R1 option B, both modes).
``missing_hook_output`` is gone: nothing copies a hook any more.
"""

from __future__ import annotations

import hashlib
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
SKILLS_ROOT = ".agents/skills"
HOOKS_ROOT = ".harness-baseline-configuration/hooks"
PROFILE_PATH = "scripts/harness_projection/profiles.toml"
SOURCE = f"{SKILLS_ROOT}/inspect-work/SKILL.md"
STUB = ".example/skills/inspect-work/SKILL.md"
REGISTRATION = ".example/settings.json"
OWNERSHIP = ".example/.projection-manifest.json"
POINTER_FILE = ".example/rules/gtkb-pointer.md"
CLAUDE_POINTER = "@AGENTS.md\n"
GOOSE_POINTER = (
    "Follow ./AGENTS.md (GT-KB session instructions). This file is only a pointer; do not add guidance here.\n"
)
PROFILE = """
schema_version = 1
[baseline]
root = ".harness-baseline-configuration"
skills_root = ".agents/skills"
hooks_root = ".harness-baseline-configuration/hooks"
hook_manifest = "hooks/manifest.toml"
[root_pointers]
"CLAUDE.md" = "@AGENTS.md\\n"
".goosehints" = "Follow ./AGENTS.md (GT-KB session instructions). This file is only a pointer; do not add guidance here.\\n"
[stamp]
text = "Derived from {baseline_root} for {harness}."
[harnesses.example]
config_dir = ".example"
project_dir_var = "EXAMPLE_PROJECT_DIR"
skills_discovery = "pointer_stubs"
skills_stub_dir = ".example/skills"
hooks_projection = "settings_json"
hooks_json_path = ".example/settings.json"
[harnesses.example.hook_events]
pre_tool_use = "PreToolUse"
[harnesses.example.intent_matchers]
file_write = "Write|Edit"
"""
AGENTS_SKILLS_PROFILE = PROFILE.replace(
    'skills_discovery = "pointer_stubs"\nskills_stub_dir = ".example/skills"\n', 'skills_discovery = "agents_skills"\n'
)
POINTER_FILE_TABLE = '[harnesses.example.pointer_files]\n"{key}" = "Follow ./AGENTS.md.\\n"\n'
MANIFEST = """
schema_version = 1
[[hook]]
event = "pre_tool_use"
intents = ["file_write"]
script = "gate.py"
blocking = true
"""
ROUTING = """
schema_version = 1
[models.example-default]
provider = "example"
[routing.example]
default_model = "example-default"
"""
SKILL = "---\nname: inspect-work\ndescription: Inspect current work.\n---\n\nUse the CLI.\n"
RICH_SKILL = (
    "---\n"
    "name: inspect-work\n"
    "description: Inspect current work.\n"
    'license: "Proprietary - (c) 2026 Remaker Digital"\n'
    "metadata:\n"
    "  project: groundtruth-kb\n"
    "  category: review\n"
    "allowed-tools: Bash(gt:*) Read\n"
    'argument-hint: "[work-item]"\n'
    "compatibility: Requires the gt CLI.\n"
    "---\n"
    "\n"
    "Use the CLI.\n"
)
POINTER_LINE = (
    "Read and follow `.agents/skills/inspect-work/SKILL.md` - this stub only registers the skill "
    "`inspect-work` for the example host; the skill body, helpers and references live there.\n"
)
EXPECTED_COMMAND = (
    '"$EXAMPLE_PROJECT_DIR/groundtruth-kb/.venv/Scripts/pythonw.exe" -B '
    '"$EXAMPLE_PROJECT_DIR/.harness-baseline-configuration/hooks/gate.py" --harness example'
)


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def link(path: Path, target_dir: Path) -> None:
    """Redirect ``path`` at a directory: a junction on Windows, a symlink elsewhere (skip-safe)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(path), str(target_dir)], capture_output=True, text=True
        )
        if result.returncode != 0:
            pytest.skip(f"junctions unavailable here: {result.stderr.strip()}")
    else:
        path.symlink_to(target_dir, target_is_directory=True)


@pytest.fixture
def tree(tmp_path):
    engine = tmp_path / parity.ENGINE
    engine.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / parity.ENGINE, engine)
    write(tmp_path, PROFILE_PATH, PROFILE)
    write(tmp_path, SOURCE, SKILL)
    write(tmp_path, f"{parity.BASELINE}/hooks/manifest.toml", MANIFEST)
    write(tmp_path, f"{parity.BASELINE}/hooks/gate.py", "print('gate')\n")
    write(tmp_path, f"{parity.BASELINE}/rules/work.md", "Use the CLI.\n")
    write(tmp_path, "AGENTS.md", "# Session instructions\n\nUse the CLI.\n")
    write(tmp_path, "CLAUDE.md", CLAUDE_POINTER)
    write(tmp_path, ".goosehints", GOOSE_POINTER)
    return tmp_path


def set_profile(tree, text):
    (tree / PROFILE_PATH).write_text(text, encoding="utf-8")


def derive(tree):
    return parity._load_projector(tree).build_plan("example")


def install(tree):
    plan = derive(tree)
    assert not plan.gaps, plan.gaps
    for rel, text in plan.writes.items():
        write(tree, rel, text)
    return plan


def planned(tree, monkeypatch, mutate):
    """Derive, let ``mutate`` edit the plan, and pin the checker to the edited plan."""
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    mutate(plan)
    monkeypatch.setattr(engine, "build_plan", lambda _: plan)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    return plan


def report(tree, *, installed=True):
    return parity.check_harness_parity(tree, harness="example", installed=installed)


def codes(result):
    return {i["code"] for i in result["issues"]} | {
        i["code"] for target in result["harnesses"].values() for i in target["issues"]
    }


def target(result):
    return result["harnesses"]["example"]


def registration_commands(plan):
    settings = json.loads(plan.writes[REGISTRATION])
    return [entry["command"] for group in settings["hooks"]["PreToolUse"] for entry in group["hooks"]]


def rewrite_commands(plan, old, new):
    settings = json.loads(plan.writes[REGISTRATION])
    for group in settings["hooks"]["PreToolUse"]:
        for entry in group["hooks"]:
            assert old in entry["command"], entry["command"]
            entry["command"] = entry["command"].replace(old, new)
    plan.writes[REGISTRATION] = json.dumps(settings, indent=2) + "\n"


def test_exact_projection_passes_without_runtime_or_waiver_registry(tree):
    install(tree)
    result = report(tree)
    assert result["status"] == "pass", result
    assert result["operational_readiness"] == "not_evaluated"
    assert target(result)["skills"] == 1


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


@pytest.mark.parametrize("rel", [STUB, REGISTRATION])
def test_body_tamper_with_unchanged_metadata_is_detected(tree, rel):
    install(tree)
    path = tree / rel
    path.write_bytes(path.read_bytes() + b"\nforeign mutation\n")
    before = path.read_bytes()
    result = report(tree)
    assert result["status"] == "fail"
    assert "changed_output" in codes(result)
    assert path.read_bytes() == before


def test_new_source_frontmatter_invalidates_previously_matching_stub(tree):
    install(tree)
    write(tree, SOURCE, SKILL.replace("description: Inspect current work.", "description: Inspect changed work."))
    assert "changed_output" in codes(report(tree))


def test_body_only_source_edit_changes_no_stub_byte(tree):
    """Ruling line 12: the stub carries the frontmatter block only, so the body never re-projects."""
    before = install(tree).writes[STUB]
    write(tree, SOURCE, SKILL + "\nMore body text that no host needs re-projected.\n")
    assert derive(tree).writes[STUB] == before
    assert report(tree)["status"] == "pass"


def test_unmanaged_output_is_reported_and_preserved(tree):
    install(tree)
    foreign = write(tree, ".example/local.txt", "unrelated bytes")
    assert "unmanaged_output" in codes(report(tree))
    assert foreign.read_text() == "unrelated bytes"


@pytest.mark.parametrize("existing", [False, True])
def test_native_toml_configuration_is_derived_and_checked(tree, existing):
    settings = 'approval_policy = "on-request"\n[features]\nhooks = true\n'
    set_profile(
        tree,
        PROFILE.replace(
            'hooks_json_path = ".example/settings.json"',
            'hooks_json_path = ".example/settings.json"\nconfig_toml = """\n' + settings + '"""',
        ),
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
    assert ".example/config.toml" in json.loads((tree / OWNERSHIP).read_text())["paths"]
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
    set_profile(
        tree,
        PROFILE.replace(
            'hooks_json_path = ".example/settings.json"',
            'hooks_json_path = ".example/settings.json"\nconfig_toml = ' + value,
        ),
    )
    write(tree, ".example/config.toml", 'existing = "preserve"\n')
    engine = parity._load_projector(tree)
    before = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert engine.build_plan("example").gaps
    assert engine.run("example", "write") == 2
    assert {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()} == before
    assert report(tree)["status"] == "fail"


def test_removed_skill_source_retires_its_stub_without_deleting_it(tree):
    install(tree)
    (tree / SOURCE).unlink()
    result = report(tree)
    assert "retired_output" in codes(result)
    assert (tree / STUB).is_file()


@pytest.mark.parametrize("failure", ["missing_source", "missing_event", "no_registration", "wrong_root"])
def test_declared_hook_obligations_cannot_disappear(tree, failure):
    if failure == "missing_source":
        (tree / parity.BASELINE / "hooks/gate.py").unlink()
    elif failure == "missing_event":
        set_profile(tree, PROFILE.replace('pre_tool_use = "PreToolUse"', ""))
    elif failure == "no_registration":
        set_profile(tree, PROFILE.replace('hooks_projection = "settings_json"', ""))
    else:
        set_profile(
            tree,
            PROFILE.replace('hooks_json_path = ".example/settings.json"', 'hooks_json_path = ".peer/settings.json"'),
        )
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"missing_hook_source", "missing_hook_registration", "projector_gap", "invalid_projection"}
    assert not (tree / ".peer").exists()


@pytest.mark.parametrize("correction", ["renamed", "duplicate", "missing_description", "missing_header", "empty"])
def test_skill_identity_and_frontmatter_cannot_be_supplied_by_aliases(tree, correction):
    path = tree / SOURCE
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
    set_profile(tree, PROFILE + '\n[harnesses.pending]\nstatus = "profile_pending"\nconfig_dir = ".pending"\n')
    result = parity.check_harness_parity(tree, harness="all", installed=False)
    assert set(result["harnesses"]) == {"example", "pending"}
    assert result["status"] == "fail"
    assert result["harnesses"]["example"]["status"] == "pass"


@pytest.mark.parametrize("target_name", ["", "unknown"])
def test_no_implicit_or_fallback_target(tree, target_name):
    result = parity.check_harness_parity(tree, harness=target_name, installed=False)
    assert result["status"] == "fail"
    assert not result["harnesses"]


@pytest.mark.parametrize(
    "command,expected",
    [
        ('python -B ".harness-baseline-configuration/hooks/gate.py"', True),
        ('python -B "$EXAMPLE_PROJECT_DIR/.harness-baseline-configuration/hooks/gate.py"', True),
        ('python -B ".harness-baseline-configuration/hooks/gate.py" --harness example', True),
        ('python -B ".harness-baseline-configuration/hooks/gate.py.backup"', False),
        ('python -B "foreign/.harness-baseline-configuration/hooks/gate.py"', False),
        ('python -B ".example/hooks/gate.py"', False),
        ('python -B ".peer/hooks/gate.py"', False),
    ],
)
def test_hook_registration_matches_full_path_argument(command, expected):
    assert parity._references_script(command, f"{HOOKS_ROOT}/gate.py", "EXAMPLE_PROJECT_DIR") is expected


def test_hook_in_unrelated_json_or_wrong_event_does_not_prove_registration(tree, monkeypatch):
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    original = plan.writes[REGISTRATION]
    settings = json.loads(original)
    settings["hooks"]["Stop"] = settings["hooks"].pop("PreToolUse")
    plan.writes[REGISTRATION] = json.dumps(settings)
    plan.writes[".example/unrelated.json"] = original
    monkeypatch.setattr(engine, "build_plan", lambda _: plan)
    monkeypatch.setattr(parity, "_load_projector", lambda _: engine)
    assert "missing_hook_registration" in codes(report(tree, installed=False))


def test_plan_cannot_write_into_peer_root(tree, monkeypatch):
    planned(tree, monkeypatch, lambda plan: plan.writes.__setitem__(".peer/private.md", "wrong destination"))
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
    assert not json.loads(plan.writes[REGISTRATION])["hooks"]


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


# --- M15 stage 1: the D15 projection shape ---------------------------------------


def test_stage_one_plan_is_registration_pointer_and_ownership_only(tree):
    """Nothing under <config_dir>/hooks or /rules is planned; ``missing_hook_output`` no longer exists."""
    plan = derive(tree)
    assert not plan.gaps, plan.gaps
    assert set(plan.writes) == {STUB, REGISTRATION, OWNERSHIP}
    result = report(tree, installed=False)
    assert result["status"] == "pass", result
    assert "missing_hook_output" not in codes(result)
    assert target(result)["files"] == 3
    assert target(result)["classes"] == {"registration": 1, "ownership": 1, "pointer": 1}
    manifest = json.loads(plan.writes[OWNERSHIP])
    assert {name: len(paths) for name, paths in manifest["classes"].items()} == target(result)["classes"]
    assert sorted(manifest["paths"]) == sorted({STUB, REGISTRATION, OWNERSHIP})
    assert "(registration 1, ownership 1, pointer 1)" in parity.format_markdown(result)


def test_registration_names_the_baseline_hook_and_the_host_identity(tree):
    """R10: every registration runs the baseline script in place and passes ``--harness <profile>``."""
    commands = registration_commands(derive(tree))
    assert commands == [EXPECTED_COMMAND]
    assert not [rel for rel in derive(tree).writes if rel.startswith(".example/hooks/")]


@pytest.mark.parametrize(
    "old,new,expected",
    [
        (" --harness example", "", "missing_identity_argument"),
        (" --harness example", " --harness other", "missing_identity_argument"),
        (" --harness example", " \"'--harness'\" \"'example'\"", None),
    ],
)
def test_identity_argument_must_follow_the_hook_path(tree, monkeypatch, old, new, expected):
    planned(tree, monkeypatch, lambda plan: rewrite_commands(plan, old, new))
    result = report(tree, installed=False)
    if expected is None:
        assert result["status"] == "pass", result
    else:
        assert result["status"] == "fail"
        assert expected in codes(result)


def test_stub_carries_the_source_frontmatter_block_verbatim(tree):
    """R2: block byte-for-byte + stamp + one pointer line + adapter block hashing the block only."""
    write(tree, SOURCE, RICH_SKILL)
    engine = parity._load_projector(tree)
    plan = engine.build_plan("example")
    assert not plan.gaps, plan.gaps
    block = engine.frontmatter_block(RICH_SKILL)
    assert block == RICH_SKILL[: RICH_SKILL.index("\n---\n", 4) + 5]
    stub = plan.writes[STUB]
    assert stub.startswith(block)
    assert engine.frontmatter_block(stub) == block
    assert engine.skill_fields(stub) == engine.skill_fields(RICH_SKILL)
    body = stub[len(block) :]
    assert body.startswith("<!--\nDerived from .harness-baseline-configuration for example.\n-->\n")
    assert POINTER_LINE in body
    digest = hashlib.sha256(block.encode("utf-8")).hexdigest()
    assert f"Canonical source sha256: {digest}" in body
    assert f"Canonical source: {SOURCE}" in body
    assert "GTKB-EXAMPLE-SKILL-ADAPTER-BEGIN" in body and "GTKB-EXAMPLE-SKILL-ADAPTER-END" in body
    assert "Use the CLI." not in body
    assert "{{" not in stub and "\r" not in stub
    assert report(tree, installed=False)["status"] == "pass"


def test_stub_bytes_do_not_depend_on_the_source_newline_style(tree):
    lf = derive(tree).writes[STUB]
    (tree / SOURCE).write_bytes(SKILL.replace("\n", "\r\n").encode("utf-8"))
    assert derive(tree).writes[STUB] == lf
    (tree / SOURCE).write_bytes(b"\xef\xbb\xbf" + SKILL.encode("utf-8"))
    assert derive(tree).writes[STUB] == lf


def _drop_pointer_line(text: str) -> str:
    lines = [line for line in text.splitlines() if not line.startswith("Read and follow ")]
    assert len(lines) < len(text.splitlines())
    return "\n".join(lines) + "\n"


def _swap(old: str, new: str):
    def mutate(text: str) -> str:
        assert old in text, text
        return text.replace(old, new, 1)

    return mutate


@pytest.mark.parametrize(
    "mutate,code",
    [
        (_swap("description: Inspect current work.", "description: Inspect other work."), "skill_frontmatter_drift"),
        (
            _swap(
                "name: inspect-work\ndescription: Inspect current work.",
                "description: Inspect current work.\nname: inspect-work",
            ),
            "skill_frontmatter_drift",
        ),
        (_drop_pointer_line, "skill_stub_body"),
        (_swap("name: inspect-work", "name: alias"), "skill_identity"),
    ],
)
def test_stub_frontmatter_pointer_line_and_identity_are_pinned(tree, monkeypatch, mutate, code):
    planned(tree, monkeypatch, lambda plan: plan.writes.__setitem__(STUB, mutate(plan.writes[STUB])))
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert code in codes(result)


@pytest.mark.parametrize(
    "rel",
    [".example/rules/copy.md", ".example/hooks/gate.py", ".example/routing.toml", ".example/skills/a/b/SKILL.md"],
)
def test_unclassified_output_fails_the_classification_pass(tree, monkeypatch, rel):
    planned(tree, monkeypatch, lambda plan: plan.writes.__setitem__(rel, "copied bytes\n"))
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert "unclassified_output" in codes(result)


def test_provider_routing_is_never_a_projection_registration(tree):
    """R6 (ii): stale profile keys cannot reintroduce a routing projection."""
    write(tree, f"{parity.BASELINE}/routing.toml", ROUTING)
    set_profile(
        tree,
        PROFILE.replace(
            'hooks_projection = "settings_json"',
            'routing_projection = true\nhooks_projection = "settings_json"',
        ),
    )
    plan = derive(tree)
    assert not plan.gaps, plan.gaps
    assert ".example/routing.toml" not in plan.writes
    result = report(tree, installed=False)
    assert result["status"] == "pass", result
    assert target(result)["classes"] == {"registration": 1, "ownership": 1, "pointer": 1}


def test_native_skills_discovery_plans_no_skill_output(tree):
    set_profile(tree, AGENTS_SKILLS_PROFILE)
    plan = derive(tree)
    assert not plan.gaps, plan.gaps
    assert not [rel for rel in plan.writes if rel.startswith(".example/skills/")]
    result = report(tree, installed=False)
    assert result["status"] == "pass", result
    assert target(result)["skills"] == 0
    assert target(result)["classes"] == {"registration": 1, "ownership": 1, "pointer": 0}


def test_skill_copy_under_native_discovery_is_unexpected(tree, monkeypatch):
    set_profile(tree, AGENTS_SKILLS_PROFILE)
    planned(tree, monkeypatch, lambda plan: plan.writes.__setitem__(STUB, SKILL))
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert "unexpected_skill_copy" in codes(result)
    assert target(result)["skills"] == 0


@pytest.mark.parametrize(
    "profile",
    [
        PROFILE.replace('skills_discovery = "pointer_stubs"', 'skills_discovery = "copies"'),
        PROFILE.replace('skills_stub_dir = ".example/skills"\n', ""),
        PROFILE.replace('skills_stub_dir = ".example/skills"', 'skills_stub_dir = ".peer/skills"'),
        AGENTS_SKILLS_PROFILE.replace(
            'skills_discovery = "agents_skills"',
            'skills_discovery = "agents_skills"\nskills_stub_dir = ".example/skills"',
        ),
    ],
)
def test_invalid_skills_discovery_declaration_fails_closed(tree, profile):
    set_profile(tree, profile)
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"invalid_projection", "projector_gap"}
    assert not (tree / ".example").exists() and not (tree / ".peer").exists()


@pytest.mark.parametrize(
    "baseline",
    [
        ('skills_root = ".agents/skills"', 'skills_root = ".other/skills"'),
        ('hooks_root = ".harness-baseline-configuration/hooks"', 'hooks_root = ".example/hooks"'),
    ],
)
def test_baseline_roots_are_read_by_name_and_pinned(tree, baseline):
    set_profile(tree, PROFILE.replace(*baseline))
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"unavailable_projector", "invalid_projection"}


def test_missing_skills_source_fails_closed_rather_than_pruning(tree):
    shutil.rmtree(tree / ".agents")
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert codes(result) & {"unavailable_projector", "invalid_projection", "empty_baseline"}


@pytest.mark.parametrize("where", ["body", "frontmatter"])
def test_baseline_token_residue_in_the_skills_source_is_reported(tree, where):
    if where == "body":
        text = SKILL + "\nRun `gt harness project {{HARNESS_NAME}} --validate`.\n"
    else:
        text = SKILL.replace(
            "description: Inspect current work.\n",
            'description: Inspect current work.\nargument-hint: "{{HARNESS_NAME}}"\n',
        )
    write(tree, SOURCE, text)
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert "baseline_token_residue" in codes(result)
    if where == "frontmatter":
        assert "projector_gap" in codes(result)


@pytest.mark.parametrize("installed", [False, True])
@pytest.mark.parametrize("defect", ["missing", "extra_line", "no_newline", "directory", "link", "agents_missing"])
def test_declared_root_pointer_drift_is_reported_in_both_modes(tree, defect, installed):
    """R1 (B): the tracked root pointers are pinned by the checker, not by the commit hook."""
    if installed:
        install(tree)
    pointer = tree / "CLAUDE.md"
    if defect == "missing":
        pointer.unlink()
    elif defect == "extra_line":
        pointer.write_bytes(b"@AGENTS.md\n\n")
    elif defect == "no_newline":
        pointer.write_bytes(b"@AGENTS.md")
    elif defect == "directory":
        pointer.unlink()
        pointer.mkdir()
    elif defect == "link":
        pointer.unlink()
        link(pointer, tree / "elsewhere")
    else:
        (tree / "AGENTS.md").unlink()
    result = report(tree, installed=installed)
    assert result["status"] == "fail"
    assert "declared_pointer_drift" in codes(result)


@pytest.mark.parametrize("installed", [False, True])
def test_exact_root_pointer_bytes_pass_in_both_modes(tree, installed):
    if installed:
        install(tree)
    assert (tree / "CLAUDE.md").read_bytes() == CLAUDE_POINTER.encode("utf-8")
    assert (tree / ".goosehints").read_bytes() == GOOSE_POINTER.encode("utf-8")
    result = report(tree, installed=installed)
    assert result["status"] == "pass", result


def test_declared_pointer_file_is_rendered_verbatim_and_classified_pointer(tree):
    set_profile(tree, PROFILE + POINTER_FILE_TABLE.format(key="rules/gtkb-pointer.md"))
    plan = derive(tree)
    assert not plan.gaps, plan.gaps
    assert plan.writes[POINTER_FILE] == "Follow ./AGENTS.md.\n"
    result = report(tree, installed=False)
    assert result["status"] == "pass", result
    assert target(result)["classes"] == {"registration": 1, "ownership": 1, "pointer": 2}
    manifest = json.loads(plan.writes[OWNERSHIP])
    assert POINTER_FILE in manifest["classes"]["pointer"]
    assert {name: len(paths) for name, paths in manifest["classes"].items()} == target(result)["classes"]


def test_declared_pointer_file_bytes_are_pinned_in_both_modes(tree, monkeypatch):
    set_profile(tree, PROFILE + POINTER_FILE_TABLE.format(key="rules/gtkb-pointer.md"))
    install(tree)
    (tree / POINTER_FILE).write_bytes(b"Follow ./AGENTS.md.\n\nLocal guidance grew back.\n")
    installed = report(tree)
    assert installed["status"] == "fail"
    assert {"changed_output", "declared_pointer_drift"} <= codes(installed)
    planned(tree, monkeypatch, lambda plan: plan.writes.__setitem__(POINTER_FILE, "Follow ./AGENTS.md.\n\nstamped\n"))
    derived = report(tree, installed=False)
    assert derived["status"] == "fail"
    assert "declared_pointer_drift" in codes(derived)


@pytest.mark.parametrize("key", ["../x.md", "/x.md", "C:/x.md", "rules\\\\x.md"])
def test_pointer_file_key_cannot_escape_the_configuration_root(tree, key):
    set_profile(tree, PROFILE + POINTER_FILE_TABLE.format(key=key))
    result = report(tree, installed=False)
    assert result["status"] == "fail"
    assert "invalid_projection" in codes(result)
    assert not (tree / "x.md").exists() and not (tree / ".example").exists()


@pytest.mark.parametrize("declaration", ["missing", "malformed"])
def test_missing_or_malformed_source_declaration_is_a_doctor_failure(tree, declaration):
    from groundtruth_kb.project.doctor import _check_harness_projection_conformance

    source = tree / PROFILE_PATH
    if declaration == "missing":
        source.unlink()
    else:
        source.write_text("[baseline\n", encoding="utf-8")
    checker = tree / "scripts/check_harness_parity.py"
    shutil.copyfile(ROOT / "scripts/check_harness_parity.py", checker)
    result = _check_harness_projection_conformance(tree)
    assert result.status == "fail" and result.required
    assert "Required source declaration" in result.message
    assert "profiles.toml" in result.message


def test_projector_rejects_a_redirected_authored_source_before_writes(tree):
    skills = tree / SKILLS_ROOT
    moved = tree / "foreign-skills"
    skills.rename(moved)
    link(skills, moved)
    engine = parity._load_projector(tree)
    with pytest.raises(engine.ProjectionError, match="skills_root is redirected"):
        engine.build_plan("example")
    assert not (tree / ".example").exists()
