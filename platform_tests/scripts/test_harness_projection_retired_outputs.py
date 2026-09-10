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
