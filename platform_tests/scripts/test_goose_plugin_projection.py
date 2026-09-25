"""Declared extra output roots (owner ruling D52): Goose's GT-KB plugin renders at .agents/plugins/gtkb/.

Goose 1.45.0 discovers project plugins only at .agents/plugins/<name>/ through a plugin.json manifest, with nested
hooks/hooks.json (finding F9). The projector owns that one declared root under the same containment, cleanup and redirect
checks as a host's config directory; everything else under .agents/ (the one skills source, other plugins) stays foreign.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "harness_projection"))
import project_harness  # noqa: E402

PROFILES = project_harness.load_profiles()
GOOSE = {**PROFILES["harnesses"]["goose"], "name": "goose"}
OLD = ".goose/plugins/gtkb/hooks/hooks.json"
NEW_HOOKS = ".agents/plugins/gtkb/hooks/hooks.json"
NEW_MANIFEST = ".agents/plugins/gtkb/plugin.json"
OWNERSHIP = ".goose/.projection-manifest.json"


def _seed(root: Path, rels, text: str = "previous bytes") -> None:
    for rel in rels:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _previous(root: Path, paths) -> dict:
    record = {
        "engine": "scripts/harness_projection/project_harness.py",
        "harness": "goose",
        "baseline_root": ".harness-baseline-configuration",
        "paths": list(paths),
    }
    (root / OWNERSHIP).parent.mkdir(parents=True, exist_ok=True)
    (root / OWNERSHIP).write_text(json.dumps(record), encoding="utf-8")
    return record


def _link(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    else:
        link.symlink_to(target, target_is_directory=True)


def test_goose_owns_exactly_one_declared_extra_root():
    assert project_harness.owned_roots(GOOSE) == [".goose", ".agents/plugins/gtkb"]
    assert project_harness.owning_root(NEW_HOOKS, GOOSE) == ".agents/plugins/gtkb"
    assert project_harness.owning_root(OLD, GOOSE) == ".goose"
    for foreign in (
        ".agents/skills/gtkb-query/SKILL.md",
        ".agents/plugins/other/plugin.json",
        ".agents/plugins/gtkbx/a",
    ):
        assert project_harness.owning_root(foreign, GOOSE) is None, foreign
    for name, profile in PROFILES["harnesses"].items():
        if name != "goose":
            assert project_harness.owned_roots(profile) == [profile["config_dir"]], name
    assert not project_harness.build_plan("goose").gaps


def test_refresh_retires_the_undiscovered_registration_and_keeps_foreign_agents_content(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    foreign = [".agents/skills/gtkb-query/SKILL.md", ".agents/plugins/other/plugin.json"]
    _seed(tmp_path, [OLD, NEW_HOOKS, *foreign])
    previous = _previous(tmp_path, [OLD, NEW_HOOKS, OWNERSHIP])
    writes = {
        NEW_HOOKS: '{"hooks": {}}\n',
        NEW_MANIFEST: '{"name": "gtkb", "version": "1.0.0"}\n',
        OWNERSHIP: json.dumps({**previous, "paths": [NEW_HOOKS, NEW_MANIFEST, OWNERSHIP]}),
    }
    plan = project_harness.Plan(writes=dict(writes))
    project_harness.apply_leftover_removes(plan, GOOSE)
    assert not plan.gaps, plan.gaps
    assert OLD in plan.removes and NEW_HOOKS not in plan.removes
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("goose", "write") == 0
    assert not (tmp_path / OLD).exists()
    assert not (tmp_path / ".goose/plugins").exists(), "emptied parents are swept up to .goose"
    assert (tmp_path / ".goose").is_dir()
    assert (tmp_path / NEW_HOOKS).read_text(encoding="utf-8") == writes[NEW_HOOKS]
    assert (tmp_path / NEW_MANIFEST).read_text(encoding="utf-8") == writes[NEW_MANIFEST]
    for rel in foreign:
        assert (tmp_path / rel).read_text(encoding="utf-8") == "previous bytes", rel


def test_a_retired_file_in_the_extra_root_sweeps_only_up_to_that_root(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    _seed(tmp_path, [NEW_HOOKS, NEW_MANIFEST])
    previous = _previous(tmp_path, [NEW_HOOKS, NEW_MANIFEST, OWNERSHIP])
    plan = project_harness.Plan(
        writes={NEW_MANIFEST: "{}\n", OWNERSHIP: json.dumps({**previous, "paths": [NEW_MANIFEST, OWNERSHIP]})}
    )
    project_harness.apply_leftover_removes(plan, GOOSE)
    assert not plan.gaps and NEW_HOOKS in plan.removes
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("goose", "write") == 0
    assert not (tmp_path / ".agents/plugins/gtkb/hooks").exists()
    assert (tmp_path / ".agents/plugins/gtkb").is_dir(), "the owned root itself is never removed"
    assert (tmp_path / NEW_MANIFEST).is_file()


@pytest.mark.parametrize(
    "outside",
    [
        ".agents/skills/gtkb-query/SKILL.md",
        ".agents/plugins/other/plugin.json",
        ".agents/plugins/gtkb-evil/x.json",
        "README.md",
    ],
)
def test_a_manifest_path_outside_every_owned_root_still_refuses(tmp_path, monkeypatch, outside):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    _seed(tmp_path, [outside])
    _previous(tmp_path, [outside, OWNERSHIP])
    plan = project_harness.Plan(writes={NEW_MANIFEST: "{}\n"})
    project_harness.apply_leftover_removes(plan, GOOSE)
    assert any("outside this harness's output directory" in gap for gap in plan.gaps), plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("goose", "write") == 2
    assert (tmp_path / outside).read_text(encoding="utf-8") == "previous bytes"
    assert not (tmp_path / NEW_MANIFEST).exists(), "nothing is written when a gap exists"


def test_a_linked_extra_root_cannot_remove_foreign_files(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    (foreign / "retain.txt").write_text("Keep these bytes", encoding="utf-8")
    _link(tmp_path / ".agents/plugins/gtkb", foreign)
    _previous(tmp_path, [".agents/plugins/gtkb/retain.txt", OWNERSHIP])
    plan = project_harness.Plan(writes={OWNERSHIP: "{}"})
    project_harness.apply_leftover_removes(plan, GOOSE)
    assert any("linked" in gap for gap in plan.gaps), plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("goose", "write") == 2
    assert (foreign / "retain.txt").read_text(encoding="utf-8") == "Keep these bytes"


def test_bytecode_in_the_extra_root_is_swept(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    _seed(tmp_path, [".agents/plugins/gtkb/hooks/__pycache__/x.cpython-314.pyc", ".agents/skills/s/__pycache__/y.pyc"])
    plan = project_harness.Plan()
    project_harness.apply_leftover_removes(plan, GOOSE)
    assert ".agents/plugins/gtkb/hooks/__pycache__" in plan.removes
    assert not [rel for rel in plan.removes if rel.startswith(".agents/skills")], "foreign bytecode is not swept"


@pytest.mark.parametrize(
    ("declared", "fragment"),
    [
        ([".agents/skills"], "overlaps .agents/skills"),
        ([".agents"], "overlaps .agents/skills"),
        ([".agents/skills/gtkb-plugin"], "overlaps .agents/skills"),
        ([".harness-baseline-configuration/plugins"], "overlaps .harness-baseline-configuration"),
        ([".git/hooks"], "overlaps .git"),
        ([".claude/plugins"], "overlaps .claude"),
        ([".goose/extra"], "overlaps .goose"),
        (["../outside"], "invalid_extra_output_root"),
        (["E:/outside"], "invalid_extra_output_root"),
        (["a\\b"], "invalid_extra_output_root"),
        ([""], "invalid_extra_output_root"),
        (".agents/plugins/gtkb", "invalid_extra_output_roots"),
        ([7], "invalid_extra_output_roots"),
    ],
)
def test_extra_root_declarations_fail_closed(declared, fragment):
    plan = project_harness.Plan()
    project_harness.validate_profile({**GOOSE, "extra_output_roots": declared}, plan)
    assert any(fragment in gap for gap in plan.gaps), plan.gaps


def test_two_harnesses_cannot_declare_overlapping_extra_roots(monkeypatch):
    profiles = project_harness.load_profiles()
    profiles["harnesses"]["fixture-host"] = {"config_dir": ".fixture-host", "extra_output_roots": [".agents/plugins"]}
    monkeypatch.setattr(project_harness, "load_profiles", lambda: profiles)
    plan = project_harness.Plan()
    project_harness.validate_profile(dict(GOOSE), plan)
    assert any("overlaps .agents/plugins" in gap for gap in plan.gaps), plan.gaps


def test_the_registration_must_lie_in_an_owned_root():
    plan = project_harness.Plan()
    project_harness.validate_profile({**GOOSE, "hooks_json_path": ".agents/plugins/other/hooks/hooks.json"}, plan)
    assert any("hooks_json_path_outside_owned_roots" in gap for gap in plan.gaps), plan.gaps
    for name, profile in PROFILES["harnesses"].items():
        clean = project_harness.Plan()
        project_harness.validate_profile({**profile, "name": name}, clean)
        assert not clean.gaps, (name, clean.gaps)


def test_the_plugin_manifest_carries_only_documented_fields():
    plan = project_harness.Plan()
    project_harness.render_plugin_manifest(GOOSE, plan)
    assert not plan.gaps
    assert json.loads(plan.writes[NEW_MANIFEST]) == dict(GOOSE["plugin_manifest"])
    assert project_harness.classify_write(NEW_MANIFEST, GOOSE) == "registration"


@pytest.mark.parametrize(
    "change",
    [
        {"plugin_manifest": {**GOOSE["plugin_manifest"], "author": "x"}},
        {"plugin_manifest": {"name": "gtkb"}},
        {"plugin_manifest": {**GOOSE["plugin_manifest"], "version": ""}},
        {"plugin_manifest": {**GOOSE["plugin_manifest"], "version": 1}},
        {"plugin_manifest_path": ".agents/plugins/other/plugin.json"},
        {"plugin_manifest_path": "../plugin.json"},
    ],
)
def test_an_invalid_plugin_manifest_is_a_gap(change):
    plan = project_harness.Plan()
    project_harness.render_plugin_manifest({**GOOSE, **change}, plan)
    assert plan.gaps and not plan.writes


def test_commands_anchor_on_the_plugin_root_only_where_declared():
    assert project_harness._plugin_root_anchor(GOOSE) == "${PLUGIN_ROOT}/../../.."
    for name, profile in PROFILES["harnesses"].items():
        if name != "goose":
            assert project_harness._plugin_root_anchor(profile) == "", name


def test_on_failure_is_rendered_on_pre_tool_use_only_and_needs_a_policy():
    tokens = project_harness.token_map(GOOSE, PROFILES["baseline"])
    manifest = {
        "hook": [
            {"event": "pre_tool_use", "script": "gate.py", "blocking": True},
            {"event": "pre_tool_use", "script": "note.py", "blocking": False},
            {"event": "turn_end", "script": "stop.py", "blocking": True},
        ]
    }
    gaps: list[str] = []
    rel, text = project_harness.render_hooks_registration(GOOSE, manifest, tokens, gaps)
    assert not gaps and rel == NEW_HOOKS
    hooks = json.loads(text)["hooks"]
    assert set(json.loads(text)) == {"hooks"}
    pre = [rule["hooks"][0] for rule in hooks["PreToolUse"]]
    assert [action.get("on_failure") for action in pre] == ["block", None]
    assert [set(rule) for rule in hooks["PreToolUse"] + hooks["Stop"]] == [{"hooks"}] * 3
    assert "on_failure" not in hooks["Stop"][0]["hooks"][0], "Goose applies on_failure to PreToolUse only"
    missing: list[str] = []
    project_harness.render_hooks_registration({**GOOSE, "blocking_failure_policy": None}, manifest, tokens, missing)
    assert any("needs the profile's blocking_failure_policy" in gap for gap in missing), missing


def test_each_command_hands_the_adapter_a_deadline_below_its_projected_timeout():
    """Goose 1.45.0 lets a timed-out hook's call run (F9), so the adapter refuses at its own earlier deadline (B68)."""
    tokens = project_harness.token_map(GOOSE, PROFILES["baseline"])
    manifest = {
        "hook": [
            {"event": "pre_tool_use", "script": "gate.py", "blocking": True, "timeout_seconds": 15},
            {"event": "pre_tool_use", "script": "quick.py", "blocking": True, "timeout_seconds": 5},
            {"event": "pre_tool_use", "script": "open.py", "blocking": True},
        ]
    }
    gaps: list[str] = []
    _rel, text = project_harness.render_hooks_registration(GOOSE, manifest, tokens, gaps)
    assert not gaps
    actions = [rule["hooks"][0] for rule in json.loads(text)["hooks"]["PreToolUse"]]
    adapter = '"${PLUGIN_ROOT}/../../../scripts/goose_hook_adapter.py"'
    assert [action.get("timeout") for action in actions] == [15, 5, None]
    assert f"{adapter} --deadline 13 " in actions[0]["command"]
    assert f"{adapter} --deadline 3 " in actions[1]["command"]
    assert "--deadline" not in actions[2]["command"], "no projected timeout, no adapter deadline"
    assert GOOSE["adapter_deadline_margin_seconds"] == 2
    assert project_harness._adapter_deadline({**GOOSE, "adapter_deadline_margin_seconds": 20}, manifest["hook"][0]) == 1
    for name in ("claude", "codex", "cursor", "antigravity", "ollama", "openrouter", "alibaba-cloud-studio"):
        assert "adapter_deadline_margin_seconds" not in PROFILES["harnesses"][name], name
