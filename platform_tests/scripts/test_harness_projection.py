"""Verification tests for the harness projection framework.

Current authored derivation behavior under GOV-HARNESS-NEUTRAL-BASELINE-001.
Native host invocation and complete baseline acceptance remain separate:

- obligations 3 and 4 via actual projected output without peer-harness paths;
- obligation 2/verification bullet 2 via ``test_projection_idempotent``
  (byte-reproducible plan);
- obligation 5 via ``test_projected_markdown_stamped_after_frontmatter``;
- fail-closed token handling via ``test_unresolved_token_is_projector_gap``.

M15 stage 1 (owner ruling D15 as amended by R3; D34 rulings R1-R15): a projection
is registrations and pointers only. Skills are pointer stubs rendered from the one
skills source ``.agents/skills`` (or nothing, where the host reads it natively),
hook scripts run in place from ``.harness-baseline-configuration/hooks`` with
``--harness <profile>`` appended to every registration (R10), rules are never
projected, and the only rendered pointer outside the stub tree is a declared
``[pointer_files]`` entry (antigravity, R4/R14 (b)). The three API profiles keep
the native hook settings registration; routing is read directly from the baseline.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = PROJECT_ROOT / "scripts" / "harness_projection"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import project_harness  # noqa: E402

BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"
SKILLS_ROOT = ".agents/skills"
HOOKS_ROOT = ".harness-baseline-configuration/hooks"
SHARED_GATE = "scripts/implementation_start_gate.py"
IMPLEMENTED = [
    name
    for name, profile in project_harness.load_profiles()["harnesses"].items()
    if profile.get("status") != "profile_pending"
]
STUB_HOSTS = ("claude", "cursor", "goose", "antigravity")


def _commands(payload) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        if isinstance(payload.get("command"), str):
            found.append(payload["command"])
        for child in payload.values():
            found.extend(_commands(child))
    elif isinstance(payload, list):
        for child in payload:
            found.extend(_commands(child))
    return found


def _registration_commands(plan, harness: str) -> list[str]:
    profile = project_harness.load_profiles()["harnesses"][harness]
    commands = _commands(json.loads(plan.writes[profile["hooks_json_path"]]))
    assert commands, f"{harness}: no registered commands"
    return commands


def _hook_targets() -> list[tuple[str, str]]:
    """(script, host-root-relative target) for every manifest hook: baseline hooks run in place."""
    manifest = tomllib.loads((BASELINE / "hooks/manifest.toml").read_text(encoding="utf-8"))
    return [
        (
            h["script"],
            f"scripts/{h['script']}" if h.get("script_root") == "project_scripts" else f"{HOOKS_ROOT}/{h['script']}",
        )
        for h in manifest["hook"]
    ]


def _stubs(plan, stub_dir: str) -> dict[str, str]:
    prefix = f"{stub_dir}/"
    return {
        rel[len(prefix) :].split("/")[0]: text
        for rel, text in plan.writes.items()
        if rel.startswith(prefix) and rel.count("/") == prefix.count("/") + 1 and rel.endswith("/SKILL.md")
    }


@pytest.mark.parametrize(
    "harness",
    [
        name
        for name, profile in project_harness.load_profiles()["harnesses"].items()
        if profile.get("status") != "profile_pending"
    ],
)
def test_projection_contains_no_peer_harness_paths(harness):
    """Inspect actual generated directions, not vendor words in unrelated source files."""
    profiles = project_harness.load_profiles()["harnesses"]
    own_root = profiles[harness]["config_dir"]
    foreign_roots = {profile["config_dir"] for profile in profiles.values()} - {own_root}
    plan = project_harness.build_plan(harness)
    assert not plan.gaps, plan.gaps
    offenders = []
    for path, content in plan.writes.items():
        normalized = content.replace("\\", "/")
        for foreign in foreign_roots:
            if foreign + "/" in normalized:
                offenders.append((path, foreign))
    assert not offenders, f"Projected configuration refers to another harness: {offenders}"


def test_projection_idempotent():
    plan_a = project_harness.build_plan("goose")
    plan_b = project_harness.build_plan("goose")
    assert plan_a.writes == plan_b.writes
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"


def test_projection_format_uses_selected_project_config_from_foreign_cwd(tmp_path, monkeypatch):
    selected = tmp_path / "selected"
    foreign = tmp_path / "foreign"
    selected.mkdir()
    foreign.mkdir()
    selected_config = selected / "ruff.toml"
    foreign_config = foreign / "ruff.toml"
    selected_config.write_text("line-length = 120\n", encoding="utf-8")
    foreign_config.write_text("line-length = 40\n", encoding="utf-8")
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", selected)
    text = 'result = function("first_argument", "second_argument", "third_argument", "fourth_argument")\n'
    before = {path: path.read_bytes() for path in (selected_config, foreign_config)}
    gaps = []
    monkeypatch.chdir(selected)
    local = project_harness.ruff_format(text, ".goose/hooks/example.py", gaps)
    monkeypatch.chdir(foreign)
    external = project_harness.ruff_format(text, ".goose/hooks/example.py", gaps)

    assert not gaps, gaps
    assert external == local == text
    assert {path: path.read_bytes() for path in before} == before
    assert not (selected / ".goose").exists()
    assert not (foreign / ".goose").exists()


@pytest.mark.parametrize("harness", ["antigravity", "claude", "codex", "cursor", "goose", "openrouter"])
def test_fresh_projection_does_not_launch_automatic_assertion_or_handoff_consumer(harness):
    plan = project_harness.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    assert not any(path.endswith("/assertion-check.py") for path in plan.writes)
    registrations = {path: text for path, text in plan.writes.items() if path.endswith(".json")}
    assert registrations
    assert not any("assertion-check.py" in text for text in registrations.values())
    assert not (BASELINE / "plugins/gtkb/hooks/hooks.json").exists()


@pytest.mark.parametrize(
    "relative",
    [
        ".projection-manifest.json",
        "commands/registry.json",
        "config.toml",
        "gtkb-hooks/runtime.jsonl",
        "hooks.json",
        "plugins/gtkb/hooks/hooks.json",
    ],
)
def test_misplaced_native_output_refuses_before_changing_a_projection(tmp_path, monkeypatch, relative):
    baseline = tmp_path / ".harness-baseline-configuration"
    contaminant = baseline / relative
    contaminant.parent.mkdir(parents=True)
    contaminant.write_text("not neutral source", encoding="utf-8")
    target = tmp_path / ".goose/rules/foreign.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"preserve unrelated output")
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)

    plan = project_harness.build_plan("goose")
    assert not plan.writes and not plan.removes
    assert any("misplaced_native_output" in gap and relative.split("/")[0] in gap for gap in plan.gaps)
    assert project_harness.run("goose", "write") == 2
    assert target.read_bytes() == b"preserve unrelated output"
    assert contaminant.read_text(encoding="utf-8") == "not neutral source"


def test_empty_removed_output_directories_do_not_block_projection(tmp_path, monkeypatch):
    baseline = tmp_path / ".harness-baseline-configuration"
    remnants = baseline / "plugins/gtkb/hooks"
    remnants.mkdir(parents=True)
    (tmp_path / SKILLS_ROOT).mkdir(parents=True)  # D15: the projector fails closed without the skills root
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)

    plan = project_harness.build_plan("goose")
    assert not plan.gaps and plan.writes
    assert remnants.is_dir()


def test_api_harness_projection_idempotent_and_clean() -> None:
    """The provider projection is reproducible and refers only to its own output."""
    plan_a = project_harness.build_plan("openrouter")
    plan_b = project_harness.build_plan("openrouter")
    assert plan_a.writes, "openrouter plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "api-harness projection is not byte-idempotent"

    manifest = json.loads(plan_a.writes[".api-harness/openrouter/.projection-manifest.json"])
    assert manifest["harness"] == "openrouter", (
        "the ownership manifest does not declare the rendering identity; it previously "
        "declared a harness that does not use this surface"
    )
    assert not [p for p in manifest["paths"] if "__pycache__" in p], (
        "the manifest claims bytecode as managed configuration, blessing runtime "
        "residue as legitimate projector output (WI-6895)"
    )

    # D15: GT-KB is the runtime for the API profiles, so nothing is copied. The
    # R6 (ii): the runtime reads the baseline routing source directly.
    assert set(plan_a.writes) == {
        ".api-harness/openrouter/settings.json",
        ".api-harness/openrouter/.projection-manifest.json",
    }
    assert manifest["classes"] == {
        "registration": [".api-harness/openrouter/settings.json"],
        "ownership": [".api-harness/openrouter/.projection-manifest.json"],
        "pointer": [],
    }
    assert not [p for p in plan_a.writes if "/rules/" in p or "/skills/" in p or "/hooks/" in p]
    for command in _registration_commands(plan_a, "openrouter"):
        assert f"$GTKB_PROJECT_ROOT/{HOOKS_ROOT}/" in command or f"$GTKB_PROJECT_ROOT/{SHARED_GATE}" in command
        assert command.endswith(" --harness openrouter"), command
        assert ".claude/" not in command, "api-harness registration emits a foreign harness root"


def test_provider_projection_roots_are_distinct() -> None:
    profiles = project_harness.load_profiles()["harnesses"]
    roots = [profiles[name]["config_dir"] for name in ("ollama", "openrouter", "alibaba-cloud-studio")]
    assert len(set(roots)) == 3
    for left in roots:
        for right in roots:
            if left != right:
                assert not Path(left).is_relative_to(Path(right))


def test_codex_projection_idempotent_and_clean() -> None:
    """WI-5960 Slice 1: the codex profile renders from the baseline (TEST-11985).

    Before activation the projector refused this profile with
    'profile is pending its own projector slice', so a baseline change reached
    four of six surfaces. This asserts the render is deterministic, gap-free and
    carries no foreign-harness references.
    """
    plan_a = project_harness.build_plan("codex")
    plan_b = project_harness.build_plan("codex")
    assert plan_a.writes, "codex plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "codex projection is not byte-idempotent"

    # R14 (a): Codex discovers .agents/skills natively, so the plan is registration
    # and ownership only - no stub tree, no rules, no hook copies.
    assert set(plan_a.writes) == {".codex/hooks.json", ".codex/config.toml", ".codex/.projection-manifest.json"}
    assert not [p for p in plan_a.writes if p.startswith(".codex/skills/")]
    verification_skill = (PROJECT_ROOT / SKILLS_ROOT / "gtkb-verify/SKILL.md").read_text(encoding="utf-8")
    assert "gt bridge deliver" in verification_skill
    assert "gt bridge artifacts" in verification_skill
    manifest = json.loads(plan_a.writes[".codex/.projection-manifest.json"])
    assert manifest["classes"]["pointer"] == []
    for command in _registration_commands(plan_a, "codex"):
        assert f"\"'{HOOKS_ROOT}/" in command or f"\"'{SHARED_GATE}'\"" in command, command
        assert command.endswith("\"'--harness'\" \"'codex'\""), command
        assert ".." not in command, "codex adapter refuses parent-relative targets (R12)"
        assert ".claude/" not in command, "codex registration emits a foreign harness root"


def test_antigravity_projection_idempotent_and_clean() -> None:
    plan_a = project_harness.build_plan("antigravity")
    plan_b = project_harness.build_plan("antigravity")
    assert plan_a.writes, "antigravity plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "antigravity projection is not byte-idempotent"

    profile = project_harness.load_profiles()["harnesses"]["antigravity"]
    stubs = _stubs(plan_a, ".agent/skills")
    assert len(stubs) == 38, sorted(stubs)
    assert set(stubs) == {p.parent.name for p in (PROJECT_ROOT / SKILLS_ROOT).glob("*/SKILL.md")}
    # R4 / R14 (b): the one declared pointer in the host's rules directory, declared
    # bytes verbatim, and nothing else under rules/ (the 24 rule copies retire).
    pointer = plan_a.writes[".agent/rules/gtkb-pointer.md"]
    assert pointer == profile["pointer_files"]["rules/gtkb-pointer.md"]
    assert [p for p in plan_a.writes if p.startswith(".agent/rules/")] == [".agent/rules/gtkb-pointer.md"]
    assert not [p for p in plan_a.writes if p.startswith(".agent/hooks/")]
    for command in _registration_commands(plan_a, "antigravity"):
        assert f" {HOOKS_ROOT}/" in command or f" {SHARED_GATE} " in command, command
        assert command.endswith(" --harness antigravity"), command
        assert ".claude/" not in command, "antigravity registration emits a foreign harness root"


def test_projected_markdown_stamped_after_frontmatter():
    plan = project_harness.build_plan("goose")
    skill_paths = [p for p in plan.writes if p.endswith("SKILL.md")]
    assert skill_paths, "no SKILL.md files in the goose plan"
    for rel in skill_paths:
        content = plan.writes[rel]
        assert "THIS FILE IS A PROJECTION, NOT CANONICAL." in content, rel
        if content.startswith("---"):
            close = content.index("\n---", 3)
            frontmatter = content[: close + 4]
            assert "PROJECTION" not in frontmatter, (
                f"{rel}: stamp landed inside YAML frontmatter, which breaks "
                "skill discovery (obligation 5 placement rule)"
            )


def _assert_optional_hook_registration(harness: str, native_event: str, *, event: str = "turn_end") -> None:
    """Check manifest-driven registration without enabling or invoking a host hook."""
    profiles = project_harness.load_profiles()
    profile = dict(profiles["harnesses"][harness], name=harness)
    tokens = project_harness.token_map(profile, profiles["baseline"])
    manifest = tomllib.loads((BASELINE / "hooks/manifest.toml").read_text(encoding="utf-8"))
    assert {hook["event"] for hook in manifest["hook"]} == {"pre_tool_use"}
    original = json.dumps(manifest, sort_keys=True)
    gaps: list[str] = []
    before = project_harness.render_hooks_registration(profile, manifest, tokens, gaps)
    assert before is not None and not gaps, gaps
    before_hooks = json.loads(before[1])["hooks"]
    assert native_event not in before_hooks
    notification = {"event": event, "script": "qualification-notification.py", "blocking": False}
    added = project_harness.render_hooks_registration(
        profile, {**manifest, "hook": [*manifest["hook"], notification]}, tokens, gaps
    )
    assert added is not None and not gaps, gaps
    after_hooks = json.loads(added[1])["hooks"]
    assert {event: entries for event, entries in after_hooks.items() if event != native_event} == before_hooks
    entries = after_hooks[native_event]
    assert len(entries) == 1 and "qualification-notification.py" in entries[0]["command"]
    assert not entries[0].get("blocking") and not entries[0].get("failClosed")
    assert json.dumps(manifest, sort_keys=True) == original


def test_projected_hooks_registration_is_native():
    plan = project_harness.build_plan("goose")
    hooks_json = plan.writes.get(".goose/plugins/gtkb/hooks/hooks.json")
    assert hooks_json is not None, "goose plugin hooks.json not rendered"
    assert set(json.loads(hooks_json)["hooks"]) == {"PreToolUse"}
    _assert_optional_hook_registration("goose", "Stop")
    _assert_optional_hook_registration("goose", "PostToolUse", event="post_tool_use")
    assert "$CLAUDE_PROJECT_DIR" not in hooks_json
    for command in _commands(json.loads(hooks_json)):
        assert f" -B {HOOKS_ROOT}/" in command or f" -B {SHARED_GATE} " in command, command
        assert command.endswith(" --harness goose"), command


def test_unresolved_token_is_projector_gap(tmp_path, monkeypatch):
    plan = project_harness.Plan()
    result = project_harness.substitute("path is {{HARNESS_UNKNOWN_TOKEN}}", {"HARNESS_NAME": "x"}, "f.md", plan.gaps)
    assert "{{HARNESS_UNKNOWN_TOKEN}}" in result
    assert plan.gaps and "unresolved token" in plan.gaps[0]


def test_pending_profile_fails_closed(monkeypatch):
    profiles = project_harness.load_profiles()
    profiles["harnesses"]["fixture-pending"] = {"config_dir": ".fixture-pending", "status": "profile_pending"}
    monkeypatch.setattr(project_harness, "load_profiles", lambda: profiles)
    with pytest.raises(project_harness.ProjectionError):
        project_harness.build_plan("fixture-pending")


def test_normalize_planned_rel_strips_dot_slash_without_lstripping_baseline_dot():
    assert (
        project_harness.normalize_planned_rel("./.harness-baseline-configuration/skills/x.md")
        == ".harness-baseline-configuration/skills/x.md"
    )
    assert (
        project_harness.normalize_planned_rel(".harness-baseline-configuration\\skills\\x.md")
        == ".harness-baseline-configuration/skills/x.md"
    )
    assert not project_harness.is_baseline_destination("scripts/harness_projection/project_harness.py")


def test_write_mode_rejects_baseline_destination_and_writes_nothing(tmp_path, monkeypatch):
    plan = project_harness.Plan()
    dest = ".harness-baseline-configuration/skills/wi6539-injected.md"
    plan.writes[dest] = "should-not-land\n"
    monkeypatch.setattr(project_harness, "build_plan", lambda harness: plan)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    with pytest.raises(project_harness.ProjectionError, match="harness-baseline-configuration"):
        project_harness.run("goose", "write")
    assert not (tmp_path / dest).exists()


def test_write_mode_rejects_dot_slash_and_backslash_baseline_destinations(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    for dest in (
        "./.harness-baseline-configuration/skills/wi6539-dot-slash.md",
        ".harness-baseline-configuration\\skills\\wi6539-backslash.md",
    ):
        plan = project_harness.Plan()
        plan.writes[dest] = "should-not-land\n"
        monkeypatch.setattr(project_harness, "build_plan", lambda harness, _plan=plan: _plan)
        with pytest.raises(project_harness.ProjectionError, match="harness-baseline-configuration"):
            project_harness.run("goose", "write")
        assert not (tmp_path / project_harness.normalize_planned_rel(dest)).exists()


def test_projected_timeout_applies_cursor_floor() -> None:
    cursor = {"hook_timeout_floor_seconds": 30}
    other = {}
    assert project_harness._projected_timeout(cursor, {}) == 30
    assert project_harness._projected_timeout(cursor, {"timeout_seconds": 5}) == 30
    assert project_harness._projected_timeout(cursor, {"timeout_seconds": 60}) == 60
    assert project_harness._projected_timeout(other, {}) is None
    assert project_harness._projected_timeout(other, {"timeout_seconds": 5}) == 5


def test_cursor_plan_maps_native_events_and_wraps_adapters() -> None:
    plan = project_harness.build_plan("cursor")
    hooks = json.loads(plan.writes[".cursor/hooks.json"])
    events = set(hooks["hooks"])
    assert "preToolUse" in events
    assert "postToolUse" not in events
    assert "stop" not in events
    _assert_optional_hook_registration("cursor", "stop")
    _assert_optional_hook_registration("cursor", "postToolUse", event="post_tool_use")
    assert "beforeSubmitPrompt" not in events
    assert "sessionStart" not in events
    assert "sessionStop" not in events
    commands = [entry["command"] for entries in hooks["hooks"].values() for entry in entries]
    assert commands
    assert all("cursor_hook_adapter.py" in command for command in commands)
    assert all("python.exe" in command for command in commands)
    assert all("pythonw.exe" not in command for command in commands)
    for command in commands:
        assert f" {HOOKS_ROOT}/" in command or f" {SHARED_GATE} " in command, command
        assert command.endswith(" --harness cursor"), command
    assert any(entry.get("failClosed") is True for entries in hooks["hooks"].values() for entry in entries)
    leftovers = set(plan.removes)
    assert ".cursor/settings.json" in leftovers
    assert ".cursor/gtkb-hooks" in leftovers
    assert ".cursor/hooks.json.disabled" in leftovers
    assert ".cursor/skills/gtkb-skill-rollout" not in leftovers

    fail_closed = [
        entry
        for event, entries in hooks["hooks"].items()
        if event in {"preToolUse", "beforeSubmitPrompt", "stop", "beforeShellExecution"}
        for entry in entries
        if entry.get("failClosed") is True
    ]
    assert fail_closed
    assert all(int(entry.get("timeout") or 0) >= 30 for entry in fail_closed)
    assert all(entry.get("timeout") != 5 for entries in hooks["hooks"].values() for entry in entries)

    write_only = (
        "kb-not-markdown.py",
        "destructive-gate.py",
        "credential-scan.py",
        "scanner-safe-writer.py",
    )
    for script in write_only:
        matching = [
            entry
            for entries in hooks["hooks"].values()
            for entry in entries
            if script in str(entry.get("command") or "")
        ]
        assert matching, f"missing projected Cursor hook for {script}"
        assert all(str(entry.get("matcher") or "").strip() for entry in matching), (
            f"{script} must have a non-empty Cursor matcher (must not fire on Read)"
        )


def test_is_projection_junk_skips_bytecode_and_session_caches(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    cache = src_root / "__pycache__" / "x.pyc"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"x")
    session = src_root / ".claude" / "session" / "role.json"
    session.parent.mkdir(parents=True)
    session.write_text("{}", encoding="utf-8")
    lock = src_root / "foo.lock"
    lock.write_text("", encoding="utf-8")
    keep = src_root / "hooks" / "gate.py"
    keep.parent.mkdir(parents=True)
    keep.write_text("x\n", encoding="utf-8")
    assert project_harness.is_projection_junk(cache, src_root)
    assert project_harness.is_projection_junk(session, src_root)
    assert project_harness.is_projection_junk(lock, src_root)
    assert not project_harness.is_projection_junk(keep, src_root)


def test_write_mode_deletes_leftovers(tmp_path: Path, monkeypatch) -> None:
    leftover = tmp_path / ".cursor" / "gtkb-hooks" / "x.cmd"
    leftover.parent.mkdir(parents=True)
    leftover.write_text("x", encoding="utf-8")
    plan = project_harness.Plan()
    plan.writes[".cursor/hooks.json"] = '{"version":1,"hooks":{}}\n'
    plan.removes = [".cursor/gtkb-hooks"]
    monkeypatch.setattr(project_harness, "build_plan", lambda harness: plan)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    assert project_harness.run("cursor", "write") == 0
    assert not leftover.exists()
    assert (tmp_path / ".cursor" / "hooks.json").is_file()


@pytest.mark.parametrize("harness", ["claude", "codex", "cursor", "goose", "antigravity", "openrouter"])
def test_projected_advisory_guidance_has_no_ledger_producer_or_grilling_hook(tmp_path, monkeypatch, harness):
    """Project authored inputs in isolation, preserving unrelated local runtime files."""
    import subprocess

    relative_paths = (
        subprocess.check_output(["git", "ls-files", "-z", "--", ".harness-baseline-configuration"], cwd=PROJECT_ROOT)
        .decode("utf-8")
        .split("\0")
    )
    for relative in relative_paths:
        source = PROJECT_ROOT / relative
        if relative and source.is_file():
            target = tmp_path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    # The skills source travels beside the baseline (working-tree bytes: the draft's
    # index lists nothing under .agents/skills until the gated commit stages the move).
    shutil.copytree(
        PROJECT_ROOT / SKILLS_ROOT, tmp_path / SKILLS_ROOT, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    for relative in ("AGENTS.md", "CLAUDE.md", ".goosehints"):
        shutil.copyfile(PROJECT_ROOT / relative, tmp_path / relative)
    shutil.copyfile(PROJECT_ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    (tmp_path / "scripts").mkdir()
    shutil.copyfile(
        PROJECT_ROOT / "scripts/implementation_start_gate.py", tmp_path / "scripts/implementation_start_gate.py"
    )
    for name in ("codex_hook_adapter.py", "antigravity_hook_adapter.py"):
        shutil.copyfile(PROJECT_ROOT / "scripts" / name, tmp_path / "scripts" / name)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    plan = project_harness.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    for relative, content in plan.writes.items():
        assert "advisory-router-scan.py" not in relative and "advisory_grilling_gate_lint.py" not in relative
        if relative.endswith(".json"):
            assert "advisory-router-scan.py" not in content and "advisory_grilling_gate_lint.py" not in content
    source_text = (tmp_path / SKILLS_ROOT / "gtkb-advisory-proposal/SKILL.md").read_text(encoding="utf-8")
    advisory = [text for path, text in plan.writes.items() if path.endswith("/gtkb-advisory-proposal/SKILL.md")]
    if harness in STUB_HOSTS:
        assert len(advisory) == 1, harness
        assert project_harness.frontmatter_block(advisory[0]) == project_harness.frontmatter_block(source_text)
        assert f"Read and follow `{SKILLS_ROOT}/gtkb-advisory-proposal/SKILL.md`" in advisory[0]
    else:
        assert advisory == [], f"{harness} reads {SKILLS_ROOT} natively; no skill output is projected"
    # Canon-content assertions belong to the SOURCE skill, not to a projection of it.
    assert "Either" in source_text and "no work-item reservation" in source_text
    assert "governance_advisory" in source_text
    assert not (tmp_path / ".gtkb-state").exists()


def _expected_command(harness: str, profile: dict, target: str, timeout: int | None) -> re.Pattern[str]:
    """The exact registration shape of projector item 7 for one host and one hook target."""
    mode = profile["hooks_projection"]
    var = profile["project_dir_var"]
    if mode == "settings_json":
        shape = f'"${var}/groundtruth-kb/.venv/Scripts/pythonw.exe" -B "${var}/{target}" --harness {harness}'
        return re.compile("^" + re.escape(shape) + "$")
    if mode == "plugin_hooks_json":
        return re.compile(
            "^" + re.escape(f'"groundtruth-kb/.venv/Scripts/python.exe" -B {target} --harness {harness}') + "$"
        )
    if mode == "hooks_json":
        adapter = profile["stdin_adapter"]
        shape = f'"groundtruth-kb/.venv/Scripts/python.exe" -B {adapter} {target} --harness {harness}'
        return re.compile("^" + re.escape(shape) + "$")
    if mode == "antigravity_hooks_json":
        adapter = profile["stdin_adapter"]
        head = f'"groundtruth-kb/.venv/Scripts/pythonw.exe" -B {adapter} --event PreToolUse --timeout '
        return re.compile("^" + re.escape(head) + r"\d+ " + re.escape(f"{target} --harness {harness}") + "$")
    assert mode == "native_cwd_hooks_json", mode
    adapter = profile["stdin_adapter"]
    tail = f"\"'{adapter}'\" \"'{target}'\" \"'PreToolUse'\" \"'"
    return re.compile(
        r'^powershell\.exe -NoProfile -NonInteractive -Command ".*" '
        + re.escape(tail)
        + r"\d+"
        + re.escape(f"'\" \"'--harness'\" \"'{harness}'\"")
        + "$"
    )


@pytest.mark.parametrize("harness", IMPLEMENTED)
def test_hook_targets_and_identity_args_per_host(harness):
    """Projector item 7: baseline scripts run in place, ``--harness <profile>`` last, no copies (D15, R10)."""
    profile = project_harness.load_profiles()["harnesses"][harness]
    plan = project_harness.build_plan(harness)
    assert not plan.gaps, plan.gaps
    commands = _registration_commands(plan, harness)
    assert not [p for p in plan.writes if p.startswith(f"{profile['config_dir']}/hooks/")]
    for script, target in _hook_targets():
        matching = [command for command in commands if target in command]
        assert matching, f"{harness}: no registration names {target}"
        for command in matching:
            assert _expected_command(harness, profile, target, None).fullmatch(command), (harness, script, command)
            assert f"{profile['config_dir']}/hooks/{script}" not in command


@pytest.mark.parametrize("harness", ["claude", "goose", "cursor", "antigravity", "codex"])
def test_application_projection_targets(tmp_path, monkeypatch, harness):
    """R12: hosted applications get ``../../`` pointer targets, host-root-relative adapter targets."""
    monkeypatch.setattr(project_harness, "APPLICATION_NAME", "Agent_Red")
    monkeypatch.setattr(project_harness, "output_root", lambda: tmp_path)
    profile = project_harness.load_profiles()["harnesses"][harness]
    plan = project_harness.build_plan(harness)
    assert not plan.gaps, plan.gaps
    if profile["skills_discovery"] == "pointer_stubs":
        stubs = _stubs(plan, profile["skills_stub_dir"])
        assert len(stubs) == 38
        for name, text in stubs.items():
            assert f"Read and follow `../../{SKILLS_ROOT}/{name}/SKILL.md`" in text, name
            assert f"Canonical source: {SKILLS_ROOT}/{name}/SKILL.md" in text, name
    commands = _registration_commands(plan, harness)
    adapter_host = bool(profile.get("stdin_adapter"))
    for _script, target in _hook_targets():
        matching = [command for command in commands if target in command]
        assert matching, (harness, target)
        for command in matching:
            if adapter_host:
                assert f"../../{target}" not in command, (harness, command)
                assert f"'{target}'" in command or f" {target} " in command, (harness, command)
            else:
                assert f"../../{target}" in command, (harness, command)
    if harness == "codex":
        assert all("Join-Path $root $hook;" in command for command in commands)
        assert all("Join-Path $applicationRoot $hook" not in command for command in commands)
    assert not any(tmp_path.iterdir()), "build_plan writes nothing"


def test_pointer_files_rendered_verbatim_without_stamp():
    profiles = project_harness.load_profiles()
    declared = {
        (name, key): value
        for name, profile in profiles["harnesses"].items()
        for key, value in (profile.get("pointer_files") or {}).items()
    }
    assert set(declared) == {("antigravity", "rules/gtkb-pointer.md")}, sorted(declared)
    assert declared[("antigravity", "rules/gtkb-pointer.md")] == profiles["root_pointers"][".goosehints"]
    plan = project_harness.build_plan("antigravity")
    rendered = plan.writes[".agent/rules/gtkb-pointer.md"]
    assert rendered == declared[("antigravity", "rules/gtkb-pointer.md")]
    assert "PROJECTION" not in rendered and "{{" not in rendered
    assert (
        rendered
        == "Follow ./AGENTS.md (GT-KB session instructions). This file is only a pointer; do not add guidance here.\n"
    )
    manifest = json.loads(plan.writes[".agent/.projection-manifest.json"])
    assert ".agent/rules/gtkb-pointer.md" in manifest["classes"]["pointer"]


@pytest.mark.parametrize("harness", IMPLEMENTED)
def test_manifest_classes_partition_paths(harness):
    """The additive ``classes`` map partitions ``paths`` (registration / ownership / pointer)."""
    profile = project_harness.load_profiles()["harnesses"][harness]
    plan = project_harness.build_plan(harness)
    manifest_rel = f"{profile['config_dir']}/.projection-manifest.json"
    manifest = json.loads(plan.writes[manifest_rel])
    classes = manifest["classes"]
    assert set(classes) == {"registration", "ownership", "pointer"}
    listed = [rel for rels in classes.values() for rel in rels]
    assert len(listed) == len(set(listed)), "a path carries two classes"
    assert set(listed) == set(manifest["paths"]) == set(plan.writes)
    assert classes["ownership"] == [manifest_rel]
    assert profile["hooks_json_path"] in classes["registration"]
    for rel in classes["pointer"]:
        assert rel.endswith("/SKILL.md") or rel in {
            f"{profile['config_dir']}/{k}" for k in profile.get("pointer_files") or {}
        }
    for rel in plan.writes:
        assert project_harness.classify_write(rel, {**profile, "name": harness}) in classes
