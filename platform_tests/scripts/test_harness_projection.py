"""Verification tests for the harness projection framework.

Landed by bridge/gtkb-baseline-correction-and-goose-projector-slice-1 (GO at
-004). Maps to GOV-HARNESS-NEUTRAL-BASELINE-001:

- obligations 3 and 4 via actual projected output without peer-harness paths;
- obligation 2/verification bullet 2 via ``test_projection_idempotent``
  (byte-reproducible plan);
- obligation 5 via ``test_projected_markdown_stamped_after_frontmatter``;
- fail-closed token handling via ``test_unresolved_token_is_projector_gap``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = PROJECT_ROOT / "scripts" / "harness_projection"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import project_harness  # noqa: E402

BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"


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

    bridge_rule = plan_a.writes.get(".api-harness/openrouter/rules/bridge-essential.md")
    assert bridge_rule is not None, "api-harness bridge rule not rendered"
    for token in ("{{HARNESS_RULES_DIR}}", "{{HARNESS_CONFIG_DIR}}"):
        assert token not in bridge_rule, (
            f"{token} survived substitution in the api-harness bridge rule (ADR-RULE-PROJECTION-FLOW-INVERSION-001)"
        )
    assert ".api-harness/openrouter/rules/" in bridge_rule, (
        "api-harness bridge rule is not self-referential (ADR-ISOLATION-APPLICATION-PLACEMENT-001)"
    )
    assert ".claude/" not in bridge_rule, (
        "api-harness bridge rule emits a foreign harness root (ADR-CROSS-HARNESS-PARITY-001)"
    )


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

    bridge_rule = plan_a.writes.get(".codex/rules/bridge-essential.md")
    assert bridge_rule is not None, "codex bridge rule not rendered"
    for token in ("{{HARNESS_RULES_DIR}}", "{{HARNESS_CONFIG_DIR}}"):
        assert token not in bridge_rule, (
            f"{token} survived substitution in the codex bridge rule "
            "(ADR-RULE-PROJECTION-FLOW-INVERSION-001: the projection carries no "
            "unsubstituted harness tokens)"
        )
    assert ".codex/rules/" in bridge_rule, (
        "codex bridge rule is not self-referential; it must point at its own "
        "projection root (ADR-ISOLATION-APPLICATION-PLACEMENT-001)"
    )
    assert ".claude/" not in bridge_rule, (
        "codex bridge rule emits a foreign harness root; each projection "
        "references only its own config surface (ADR-CROSS-HARNESS-PARITY-001)"
    )

    skill = plan_a.writes[".codex/skills/gtkb-verify/SKILL.md"]
    assert "gt bridge deliver" in skill and "gt bridge artifacts" in skill
    assert ".codex/skills/gtkb-verify/helpers/write_verdict.py" not in plan_a.writes


def test_antigravity_projection_idempotent_and_clean() -> None:
    plan_a = project_harness.build_plan("antigravity")
    plan_b = project_harness.build_plan("antigravity")
    assert plan_a.writes, "antigravity plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "antigravity projection is not byte-idempotent"

    bridge_rule = plan_a.writes.get(".agent/rules/bridge-essential.md")
    assert bridge_rule is not None, "antigravity bridge rule not rendered"
    for token in ("{{HARNESS_RULES_DIR}}", "{{HARNESS_CONFIG_DIR}}"):
        assert token not in bridge_rule, (
            f"{token} survived substitution in the antigravity bridge rule "
            "(ADR-RULE-PROJECTION-FLOW-INVERSION-001: the projection carries no "
            "unsubstituted harness tokens)"
        )
    assert ".agent/rules/" in bridge_rule, (
        "antigravity bridge rule is not self-referential; it must point at its own "
        "projection root (ADR-ISOLATION-APPLICATION-PLACEMENT-001)"
    )
    assert ".claude/" not in bridge_rule, (
        "antigravity bridge rule emits a foreign harness root; each projection "
        "references only its own config surface (ADR-CROSS-HARNESS-PARITY-001)"
    )


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


def test_projected_hooks_registration_is_native():
    plan = project_harness.build_plan("goose")
    hooks_json = plan.writes.get(".goose/plugins/gtkb/hooks/hooks.json")
    assert hooks_json is not None, "goose plugin hooks.json not rendered"
    assert "PreToolUse" in hooks_json and "Stop" in hooks_json
    assert "$CLAUDE_PROJECT_DIR" not in hooks_json


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
    assert "postToolUse" in events
    assert "stop" in events
    assert "beforeSubmitPrompt" not in events
    assert "sessionStart" not in events
    assert "sessionStop" not in events
    commands = [entry["command"] for entries in hooks["hooks"].values() for entry in entries]
    assert commands
    assert all("cursor_hook_adapter.py" in command for command in commands)
    assert all("python.exe" in command for command in commands)
    assert all("pythonw.exe" not in command for command in commands)
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
        "spec-before-code.py",
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
