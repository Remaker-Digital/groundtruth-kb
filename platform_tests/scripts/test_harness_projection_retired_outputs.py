"""Projection refresh removes retired outputs without expanding its deletion scope."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "harness_projection"))
import project_harness  # noqa: E402


def manifest(root, paths):
    target = root / ".cursor/.projection-manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "engine": "scripts/harness_projection/project_harness.py",
                "harness": "cursor",
                "baseline_root": ".harness-baseline-configuration",
                "paths": paths,
            }
        ),
        encoding="utf-8",
    )
    return target


def test_refresh_removes_retired_manifest_outputs_and_preserves_unlisted_files(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    old = ".cursor/skills/example/helpers/retired.py"
    current = ".cursor/skills/example/SKILL.md"
    foreign = ".cursor/skills/example/helpers/local.py"
    for name in (old, current, foreign):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("previous bytes", encoding="utf-8")
    manifest_file = manifest(tmp_path, [old, current, ".cursor/.projection-manifest.json"])
    updated_manifest = json.loads(manifest_file.read_text())
    updated_manifest["paths"] = [current, ".cursor/.projection-manifest.json"]
    plan = project_harness.Plan(
        writes={current: "current instructions", ".cursor/.projection-manifest.json": json.dumps(updated_manifest)}
    )
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert not plan.gaps
    assert plan.removes == [old]
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "write") == 0
    assert not (tmp_path / old).exists()
    assert (tmp_path / current).read_text() == "current instructions"
    assert (tmp_path / foreign).read_text() == "previous bytes"


@pytest.mark.parametrize(
    "harness,retired",
    [
        ("claude", [".claude/skills/gtkb-check-deliberations/SKILL.md", ".claude/hooks/advisory-router-scan.py"]),
        ("codex", [".codex/plugins/gtkb/hooks/hooks.json", ".codex/commands/registry.json"]),
    ],
)
def test_refresh_removes_classified_files_without_old_manifest(tmp_path, monkeypatch, harness, retired):
    profile = {**project_harness.load_profiles()["harnesses"][harness], "name": harness}
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    siblings = [
        ".claude/skills/gtkb-check-deliberations/local-notes.md",
        ".claude/skills/other/SKILL.md",
        ".codex/skills/gtkb-check-deliberations/SKILL.md",
        ".api-harness/skills/gtkb-check-deliberations/SKILL.md",
        ".codex/config.toml",
        ".codex/plugins/gtkb/hooks/local-notes.md",
        ".codex/commands/local.json",
    ]
    for name in (*retired, *siblings):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Preserve until explicitly selected", encoding="utf-8")
    before = {name: (tmp_path / name).read_bytes() for name in siblings}
    assert not (tmp_path / profile["config_dir"] / ".projection-manifest.json").exists()
    current = f"{profile['config_dir']}/rules/current.md"
    plan = project_harness.Plan(writes={current: "Read current canonical state.\n"})
    project_harness.apply_leftover_removes(plan, profile)
    assert not plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)

    assert project_harness.run(harness, "check") == 1
    assert project_harness.run(harness, "write") == 0
    assert all(not (tmp_path / name).exists() for name in retired)
    assert project_harness.run(harness, "check") == 0
    assert (tmp_path / current).read_text() == "Read current canonical state.\n"
    assert {name: (tmp_path / name).read_bytes() for name in siblings} == before


@pytest.mark.parametrize(
    "path",
    ["../outside.txt", ".cursor", ".codex/skills/other.md", ".harness-baseline-configuration/rules/source.md"],
)
def test_invalid_manifest_removal_scope_refuses_refresh_before_any_write(tmp_path, monkeypatch, path):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    manifest_file = manifest(tmp_path, [path])
    before = manifest_file.read_bytes()
    plan = project_harness.Plan(writes={".cursor/new.txt": "new content"})
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "write") == 2
    assert manifest_file.read_bytes() == before
    assert not (tmp_path / ".cursor/new.txt").exists()


def test_a_manifest_cannot_expand_file_cleanup_to_directories(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    directory = tmp_path / ".cursor/skills/local"
    directory.mkdir(parents=True)
    content = directory / "personal.md"
    content.write_text("Preserve this work", encoding="utf-8")
    manifest(tmp_path, [".cursor/skills/local"])
    plan = project_harness.Plan()
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert plan.gaps
    assert ".cursor/skills/local" not in plan.removes
    assert content.read_text() == "Preserve this work"


def test_linked_projection_root_cannot_remove_another_harness_file(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    other = tmp_path / ".codex"
    other.mkdir()
    target = other / "retain.txt"
    target.write_text("Keep these bytes", encoding="utf-8")
    link = tmp_path / ".cursor"
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(other)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    else:
        link.symlink_to(other, target_is_directory=True)
    manifest(tmp_path, [".cursor/retain.txt"])
    plan = project_harness.Plan(writes={".cursor/new.txt": "new content"})
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "write") == 2
    assert target.read_text() == "Keep these bytes"
    assert not (other / "new.txt").exists()


def test_openrouter_retires_its_generic_files_and_preserves_current_providers(tmp_path, monkeypatch):
    profile = {**project_harness.load_profiles()["harnesses"]["openrouter"], "name": "openrouter"}
    retired = profile["leftover_paths"]
    assert len(retired) == 121
    assert all(path.startswith(".api-harness/") for path in retired)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    retained = [f".api-harness/{name}/hooks/local.py" for name in ("openrouter", "ollama", "alibaba-cloud-studio")] + [
        ".api-harness/hooks/local.py",
        ".api-harness/skills/gtkb-benchmarks/local-notes.md",
        ".api-harness/private.json",
    ]
    for rel in retired + retained:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"Exact fixture bytes\r\n")
    before = {rel: (tmp_path / rel).read_bytes() for rel in retired + retained}
    current = ".api-harness/openrouter/rules/current.md"
    plan = project_harness.Plan(writes={current: "Current OpenRouter output\n"})
    project_harness.apply_leftover_removes(plan, profile)
    assert not plan.gaps
    assert set(plan.removes) == set(retired)
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("openrouter", "dry-run") == 0
    assert project_harness.run("openrouter", "check") == 1
    assert {rel: (tmp_path / rel).read_bytes() for rel in before} == before
    assert project_harness.run("openrouter", "write") == 0
    assert all(not (tmp_path / rel).exists() for rel in retired)
    assert {rel: (tmp_path / rel).read_bytes() for rel in retained} == {rel: before[rel] for rel in retained}
    assert (tmp_path / current).read_text() == "Current OpenRouter output\n"
    assert project_harness.run("openrouter", "check") == 0
    assert project_harness.run("openrouter", "write") == 0
    assert {rel: (tmp_path / rel).read_bytes() for rel in retained} == {rel: before[rel] for rel in retained}


@pytest.mark.parametrize(
    "relative",
    [
        ".api-harness/hooks.json",
        ".api-harness/hooks/assertion-check.py",
        ".api-harness/skills/gtkb-benchmarks/SKILL.md",
    ],
)
def test_exact_retired_file_never_expands_to_local_directory(tmp_path, monkeypatch, relative):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    directory = tmp_path / relative
    directory.mkdir(parents=True)
    payload = directory / "unlisted-local-work.txt"
    payload.write_bytes(b"Preserve local work")
    plan = project_harness.Plan(writes={".api-harness/openrouter/current.txt": "new"})
    project_harness.apply_leftover_removes(plan, {"leftover_paths": [relative]})
    assert plan.gaps
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("openrouter", "write") == 2
    assert payload.read_bytes() == b"Preserve local work"
    assert not (tmp_path / ".api-harness/openrouter/current.txt").exists()


def _seed(root, paths, text="previous bytes"):
    for name in paths:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def _previous_manifest(root, config_dir, harness, paths):
    target = root / config_dir / ".projection-manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "engine": "scripts/harness_projection/project_harness.py",
        "harness": harness,
        "baseline_root": ".harness-baseline-configuration",
        "paths": [*paths, f"{config_dir}/.projection-manifest.json"],
    }
    target.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_write_sweeps_emptied_parents_bounded_to_config_dir(tmp_path, monkeypatch):
    """M15 stage 1: retiring the copies must not leave ~240 SKILL.md-less skill directories behind."""
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    retired = [".cursor/rules/a.md", ".cursor/hooks/b.py", ".cursor/skills/x/helpers/c.py"]
    current = ".cursor/skills/x/SKILL.md"
    _seed(tmp_path, [*retired, current])
    previous = _previous_manifest(tmp_path, ".cursor", "cursor", [*retired, current])
    plan = project_harness.Plan(
        writes={current: "stub", ".cursor/.projection-manifest.json": json.dumps({**previous, "paths": [current]})}
    )
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert not plan.gaps and set(plan.removes) == set(retired)
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "write") == 0
    assert not (tmp_path / ".cursor/rules").exists()
    assert not (tmp_path / ".cursor/hooks").exists()
    assert not (tmp_path / ".cursor/skills/x/helpers").exists()
    assert (tmp_path / ".cursor").is_dir() and (tmp_path / ".cursor/skills/x").is_dir()
    assert (tmp_path / current).read_text() == "stub"


def test_sweep_keeps_directories_holding_unmanaged_files(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    retired = [".cursor/rules/a.md", ".cursor/hooks/b.py"]
    local = ".cursor/rules/local.md"
    _seed(tmp_path, [*retired, local])
    previous = _previous_manifest(tmp_path, ".cursor", "cursor", retired)
    plan = project_harness.Plan(
        writes={
            ".cursor/hooks.json": "{}",
            ".cursor/.projection-manifest.json": json.dumps({**previous, "paths": [".cursor/hooks.json"]}),
        }
    )
    project_harness.apply_leftover_removes(plan, {"name": "cursor", "config_dir": ".cursor"})
    assert not plan.gaps and set(plan.removes) == set(retired)
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "write") == 0
    assert (tmp_path / local).read_text() == "previous bytes"
    assert (tmp_path / ".cursor/rules").is_dir()
    assert not (tmp_path / ".cursor/hooks").exists()


def test_sweep_never_removes_config_dir_or_escapes_it(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    retired = [".api-harness/openrouter/rules/a.md", ".api-harness/openrouter/skills/s/SKILL.md"]
    sibling = ".api-harness/ollama/settings.json"
    _seed(tmp_path, [*retired, sibling])
    _previous_manifest(tmp_path, ".api-harness/openrouter", "openrouter", retired)
    plan = project_harness.Plan()
    project_harness.apply_leftover_removes(plan, {"name": "openrouter", "config_dir": ".api-harness/openrouter"})
    assert not plan.gaps
    assert set(plan.removes) == {*retired, ".api-harness/openrouter/.projection-manifest.json"}
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("openrouter", "write") == 0
    assert (tmp_path / ".api-harness/openrouter").is_dir()
    assert not any((tmp_path / ".api-harness/openrouter").iterdir())
    assert (tmp_path / ".api-harness").is_dir() and (tmp_path / sibling).read_text() == "previous bytes"


def test_check_mode_ignores_empty_directories(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    plan = project_harness.Plan(writes={".cursor/hooks.json": "{}"})
    _seed(tmp_path, [".cursor/hooks.json"], "{}")
    (tmp_path / ".cursor/rules").mkdir(parents=True)
    (tmp_path / ".cursor/skills/x").mkdir(parents=True)
    monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
    assert project_harness.run("cursor", "check") == 0
    assert (tmp_path / ".cursor/rules").is_dir() and (tmp_path / ".cursor/skills/x").is_dir()


@pytest.mark.parametrize("relative", [".api-harness", ".api-harness/hooks", ".api-harness/hooks/assertion-check.py"])
def test_generic_retirement_refuses_redirected_output_before_writes(tmp_path, monkeypatch, relative):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    peer = tmp_path / "foreign"
    peer.mkdir()
    payload = peer / "local.txt"
    payload.write_bytes(b"Keep foreign bytes")
    link = tmp_path / relative
    link.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(peer)], capture_output=True)
        assert result.returncode == 0
    else:
        link.symlink_to(peer, target_is_directory=True)
    try:
        profile = {**project_harness.load_profiles()["harnesses"]["openrouter"], "name": "openrouter"}
        plan = project_harness.Plan(writes={".api-harness/openrouter/current.txt": "new"})
        project_harness.apply_leftover_removes(plan, profile)
        monkeypatch.setattr(project_harness, "build_plan", lambda _: plan)
        assert project_harness.run("openrouter", "write") == 2
        assert payload.read_bytes() == b"Keep foreign bytes"
        assert not (tmp_path / ".api-harness/openrouter/current.txt").exists()
    finally:
        if sys.platform == "win32":
            link.rmdir()
        else:
            link.unlink()
