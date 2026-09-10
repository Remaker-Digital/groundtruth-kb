"""Surviving skill-adapter contracts belong to the shared neutral projector."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "harness_projection"))
import project_harness  # noqa: E402

TARGETS = tuple(project_harness.load_profiles()["harnesses"])


@pytest.fixture(params=TARGETS)
def projection(request, tmp_path, monkeypatch):
    name = request.param
    profiles = copy.deepcopy(project_harness.load_profiles())
    # This fixture exercises the skill surface. Complete native hook/routing
    # rendering is covered by the real-baseline all-target acceptance suite.
    profiles["harnesses"][name]["routing_projection"] = False
    monkeypatch.setattr(project_harness, "load_profiles", lambda: profiles)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    baseline = tmp_path / ".harness-baseline-configuration/skills/alpha"
    baseline.mkdir(parents=True)
    (baseline / "SKILL.md").write_bytes(
        b"\xef\xbb\xbf---\r\nname: alpha\r\ndescription: Example skill.\r\n"
        b'argument-hint: "[unit|live] [options]"\r\n---\r\n\r\n'
        b"Run {{HARNESS_SKILLS_DIR}}/alpha/helpers/run.py.\r\n"
        b"Read {{HARNESS_SKILLS_DIR}}/alpha/references/notes.md.\r\n"
    )
    (baseline / "helpers").mkdir()
    (baseline / "helpers/run.py").write_bytes(b"print('example')\r\n")
    (baseline / "references").mkdir()
    (baseline / "references/notes.md").write_bytes(b"Canonical reference.\r\n")
    destination = tmp_path / profiles["harnesses"][name]["skills_dir"] / "alpha"
    return name, tmp_path, baseline, destination


def snapshots(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_neutral_skill_complete_render_is_native_and_repeatable(projection):
    name, root, baseline, destination = projection
    original = snapshots(root)
    plan = project_harness.build_plan(name)
    assert not plan.gaps
    assert snapshots(root) == original
    assert project_harness.run(name, "write") == 0
    rendered = (destination / "SKILL.md").read_bytes()
    assert rendered.startswith(b"---\n")
    assert b"\r" not in rendered
    parsed = yaml.safe_load(rendered.decode().split("---", 2)[1])
    assert parsed == {"name": "alpha", "description": "Example skill.", "argument-hint": "[unit|live] [options]"}
    assert f"{destination.relative_to(root).as_posix()}/helpers/run.py" in rendered.decode()
    assert f"{destination.relative_to(root).as_posix()}/references/notes.md" in rendered.decode()
    assert (baseline / "SKILL.md").read_bytes().startswith(b"\xef\xbb\xbf")
    for path in destination.rglob("*"):
        if path.is_file():
            content = path.read_bytes()
            assert b"\r" not in content
            assert all(line == line.rstrip() for line in content.decode().splitlines())
    manifest_path = next(p for p in plan.writes if p.endswith("/.projection-manifest.json"))
    assert set(json.loads((root / manifest_path).read_text(encoding="utf-8"))["paths"]) == set(plan.writes)
    before = snapshots(root)
    assert project_harness.run(name, "write") == 0
    assert project_harness.run(name, "check") == 0
    assert snapshots(root) == before


@pytest.mark.parametrize("relative", ["SKILL.md", "helpers/run.py", "references/notes.md"])
def test_neutral_skill_resource_drift_is_read_only_and_refresh_repairs(projection, relative):
    name, root, _, destination = projection
    assert project_harness.run(name, "write") == 0
    target = destination / relative
    original = target.read_bytes()
    target.unlink()
    missing = snapshots(root)
    assert project_harness.run(name, "check") == 1
    assert snapshots(root) == missing
    assert project_harness.run(name, "write") == 0
    assert target.read_bytes() == original
    target.write_bytes(original.replace(b"\n", b"\r\n"))
    before = snapshots(root)
    assert project_harness.run(name, "check") == 1
    assert snapshots(root) == before
    assert project_harness.run(name, "write") == 0
    assert target.read_bytes() == original


@pytest.mark.parametrize(
    "frontmatter",
    [
        "name: alpha\n",
        "name: alpha\ndescription: Example\nallowed-tools: [a] [b]\n",
        "name: alpha\ndescription: Example\nargument-hint: [unit|live] [options]\n",
        "name: alpha\ndescription: Example\nname: beta\n",
        "name: other\ndescription: Example\n",
        "name: alpha\ndescription: [Example]\n",
    ],
)
def test_neutral_skill_invalid_frontmatter_refuses_before_output(projection, frontmatter):
    name, root, baseline, _ = projection
    (baseline / "SKILL.md").write_text(f"---\n{frontmatter}---\n\nBody.\n", encoding="utf-8")
    before = snapshots(root)
    assert project_harness.run(name, "write") == 2
    assert snapshots(root) == before


@pytest.mark.parametrize(
    "text",
    [
        "name: alpha\ndescription: Example\n",
        "---\nname: alpha\ndescription: Example\n",
        "---\nname: alpha\ndescription Example\n---\n",
    ],
)
def test_neutral_skill_invalid_source_refuses_before_output(projection, text):
    name, root, baseline, _ = projection
    (baseline / "SKILL.md").write_text(text, encoding="utf-8")
    before = snapshots(root)
    assert project_harness.run(name, "write") == 2
    assert snapshots(root) == before


@pytest.mark.parametrize("relative", ["helpers/run.py", "references/notes.md"])
def test_neutral_skill_retired_resource_cleanup_preserves_unlisted_work(projection, relative):
    name, root, baseline, destination = projection
    assert project_harness.run(name, "write") == 0
    foreign = destination / "helpers/local.py"
    foreign.write_bytes(b"Local work must survive refresh.\n")
    (baseline / relative).unlink()
    source = baseline / "SKILL.md"
    text = source.read_text(encoding="utf-8-sig")
    source.write_text(
        "\n".join(line for line in text.splitlines() if relative not in line) + "\n",
        encoding="utf-8",
    )
    before = snapshots(root)
    assert project_harness.run(name, "check") == 1
    assert snapshots(root) == before
    assert project_harness.run(name, "write") == 0
    assert not (destination / relative).exists()
    assert foreign.read_bytes() == b"Local work must survive refresh.\n"
    assert project_harness.run(name, "check") == 0


def test_neutral_skill_failed_replace_preserves_target_and_foreign_temporary(projection, monkeypatch):
    name, root, _, destination = projection
    assert project_harness.run(name, "write") == 0
    target = destination / "SKILL.md"
    target.write_bytes(b"Local bytes must survive a failed replacement.\n")
    foreign = destination / ".SKILL.md.tmp"
    foreign.write_bytes(b"Independent in-progress bytes.\n")
    before = snapshots(root)

    def fail_replace(source, destination):
        raise OSError("injected replacement failure")

    monkeypatch.setattr(project_harness.os, "replace", fail_replace)
    with pytest.raises(OSError, match="injected replacement failure"):
        project_harness.run(name, "write")
    assert snapshots(root) == before
