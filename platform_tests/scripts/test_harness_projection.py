"""Verification tests for the harness projection framework.

Landed by bridge/gtkb-baseline-correction-and-goose-projector-slice-1 (GO at
-004). Maps to GOV-HARNESS-NEUTRAL-BASELINE-001:

- obligation 3 via ``test_baseline_token_census`` (ratchet: seeded at the
  measured value, may only decrease);
- obligation 2/verification bullet 2 via ``test_projection_idempotent``
  (byte-reproducible plan);
- obligation 5 via ``test_projected_markdown_stamped_after_frontmatter``;
- fail-closed token handling via ``test_unresolved_token_is_projector_gap``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = PROJECT_ROOT / "scripts" / "harness_projection"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import project_harness  # noqa: E402

BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"

HARNESS_TOKENS = [
    "codex",
    "claude",
    "cursor",
    "goose",
    "antigravity",
    "ollama",
    "openrouter",
    "alibaba",
    "api-harness",
]

# Ratchet cap seeded from the census measured at landing time (Phase A
# increment 3 state; method: case-insensitive matched lines per token over
# *.md,*.py,*.toml,*.json,*.yaml,*.txt). The number may ONLY decrease as
# Phase A relocations and Phase D formal-artifact edits land. Raising it
# requires an owner-approved bridge revision.
CENSUS_CAP = 210


def measure_census() -> int:
    total = 0
    for token in HARNESS_TOKENS:
        pattern = re.compile(re.escape(token), re.I)
        for path in BASELINE.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {
                ".md",
                ".py",
                ".toml",
                ".json",
                ".yaml",
                ".txt",
            }:
                continue
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            total += sum(1 for line in text.splitlines() if pattern.search(line))
    return total


def test_baseline_token_census():
    measured = measure_census()
    assert measured <= CENSUS_CAP, (
        f"baseline harness-token census regressed: {measured} > cap {CENSUS_CAP}. "
        "New harness references entered the neutral baseline "
        "(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 3). Remove them or, if a "
        "legitimate decrease landed, lower the cap - never raise it without an "
        "owner-approved bridge revision."
    )


def test_projection_idempotent():
    plan_a = project_harness.build_plan("goose")
    plan_b = project_harness.build_plan("goose")
    assert plan_a.writes == plan_b.writes
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"


@pytest.mark.parametrize("harness", ["antigravity", "claude", "codex", "cursor", "goose", "openrouter"])
def test_fresh_projection_does_not_launch_automatic_assertion_or_handoff_consumer(harness):
    plan = project_harness.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    assert not any(path.endswith("/assertion-check.py") for path in plan.writes)
    registrations = {path: text for path, text in plan.writes.items() if path.endswith(".json")}
    assert registrations
    assert not any("assertion-check.py" in text for text in registrations.values())
    plugin = json.loads((BASELINE / "plugins/gtkb/hooks/hooks.json").read_text(encoding="utf-8"))
    assert not any("assertion-check.py" in hook["command"] for hook in plugin["hooks"]["SessionStart"])


def test_api_harness_projection_idempotent_and_clean() -> None:
    """WI-5960 Slice 2: the shared .api-harness surface renders (TEST-11985, TEST-12488).

    Three registered identities share this config_dir; only openrouter is active,
    so it is the sole renderer. Before activation the surface was a mis-projected
    Claude tree whose ownership manifest declared the wrong harness and claimed
    __pycache__ paths as managed configuration.
    """
    plan_a = project_harness.build_plan("openrouter")
    plan_b = project_harness.build_plan("openrouter")
    assert plan_a.writes, "openrouter plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "api-harness projection is not byte-idempotent"

    manifest = json.loads(plan_a.writes[".api-harness/.projection-manifest.json"])
    assert manifest["harness"] == "openrouter", (
        "the ownership manifest does not declare the rendering identity; it previously "
        "declared a harness that does not use this surface"
    )
    assert not [p for p in manifest["paths"] if "__pycache__" in p], (
        "the manifest claims bytecode as managed configuration, blessing runtime "
        "residue as legitimate projector output (WI-6895)"
    )

    bridge_rule = plan_a.writes.get(".api-harness/rules/bridge-essential.md")
    assert bridge_rule is not None, "api-harness bridge rule not rendered"
    for token in ("{{HARNESS_RULES_DIR}}", "{{HARNESS_CONFIG_DIR}}"):
        assert token not in bridge_rule, (
            f"{token} survived substitution in the api-harness bridge rule (ADR-RULE-PROJECTION-FLOW-INVERSION-001)"
        )
    assert ".api-harness/rules/" in bridge_rule, (
        "api-harness bridge rule is not self-referential (ADR-ISOLATION-APPLICATION-PLACEMENT-001)"
    )
    assert ".claude/" not in bridge_rule, (
        "api-harness bridge rule emits a foreign harness root (ADR-CROSS-HARNESS-PARITY-001)"
    )


def test_only_one_identity_renders_the_shared_api_harness_surface() -> None:
    """Sibling identities on a shared config_dir must not both render.

    ollama, openrouter and alibaba-cloud-studio all declare config_dir
    ".api-harness". Each would substitute its own project_dir_var and
    session_id_var into the same files and overwrite the others' ownership
    manifest, whose path the engine derives from config_dir. Only the active
    identity is activated; the rest must still fail closed.
    """
    profiles = project_harness.load_profiles()["harnesses"]
    sharing = [n for n, p in profiles.items() if p.get("config_dir") == ".api-harness"]
    assert len(sharing) > 1, "expected multiple identities to share the api-harness surface"
    rendering = [n for n in sharing if profiles[n].get("status") != "profile_pending"]
    assert len(rendering) == 1, (
        f"exactly one identity may render a shared surface; {rendering} would collide "
        "on token substitution and on the ownership manifest path"
    )
    for name in sharing:
        if name in rendering:
            continue
        with pytest.raises(project_harness.ProjectionError):
            project_harness.build_plan(name)


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

    # The slice's substantive payload: .codex predated WI-6530 and lacked the
    # git check-ignore chain-integrity bypass, so a Codex-run VERIFIED
    # finalization failed closed where a Claude-run one succeeded.
    helper = plan_a.writes.get(".codex/skills/gtkb-verify/helpers/write_verdict.py")
    assert helper is not None, "codex verify helper not rendered"
    assert "check-ignore" in helper, (
        "the projected codex verify helper lacks the WI-6530 chain-integrity "
        "logic; terminal VERIFIED remains unreachable for multi-version threads"
    )


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


def test_pending_profile_fails_closed():
    # Subject repointed from "codex" to "ollama" by WI-5960 Slice 1: activating the
    # codex profile necessarily invalidated it as an example of a pending profile.
    # The invariant under test is unchanged - a profile carrying
    # status = "profile_pending" must fail closed rather than render silently -
    # and ollama remains pending, as do openrouter and alibaba-cloud-studio.
    with pytest.raises(project_harness.ProjectionError):
        project_harness.build_plan("ollama")


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
    assert "beforeSubmitPrompt" in events
    assert "sessionStart" in events
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
