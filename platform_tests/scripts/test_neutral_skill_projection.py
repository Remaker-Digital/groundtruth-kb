"""Shared authored skills and minimal host pointers preserve discovery and atomicity."""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from scripts.harness_projection import project_harness

PROFILES = project_harness.load_profiles()
STUB_HOSTS = tuple(name for name, row in PROFILES["harnesses"].items() if row["skills_discovery"] == "pointer_stubs")
NATIVE_HOSTS = tuple(name for name, row in PROFILES["harnesses"].items() if row["skills_discovery"] == "agents_skills")
FRONTMATTER = '---\nname: alpha\ndescription: Example skill.\nargument-hint: "[unit|live] [options]"\nallowed-tools: [Read, Bash]\n---\n'


def seed(root, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", root)
    monkeypatch.setattr(project_harness, "load_profiles", lambda: copy.deepcopy(PROFILES))
    (root / ".harness-baseline-configuration/hooks").mkdir(parents=True)
    skill = root / ".agents/skills/alpha"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_bytes(
        b"\xef\xbb\xbf"
        + (FRONTMATTER + "Read .agents/skills/alpha/references/notes.md.\n").replace("\n", "\r\n").encode()
    )
    (skill / "helpers").mkdir()
    (skill / "helpers/run.py").write_bytes(b"print('example')\r\n")
    (skill / "references").mkdir()
    (skill / "references/notes.md").write_bytes(b"Authored reference.\r\n")
    return skill


@pytest.fixture(params=STUB_HOSTS)
def projection(request, tmp_path, monkeypatch):
    source = seed(tmp_path, monkeypatch)
    name = request.param
    destination = tmp_path / PROFILES["harnesses"][name]["skills_stub_dir"] / "alpha"
    return name, tmp_path, source, destination


def snapshots(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_pointer_preserves_frontmatter_and_never_copies_body_or_resources(projection):
    name, root, source, destination = projection
    before = snapshots(root)
    plan = project_harness.build_plan(name)
    assert not plan.gaps, plan.gaps
    assert snapshots(root) == before
    assert project_harness.run(name, "write") == 0
    rendered = (destination / "SKILL.md").read_text(encoding="utf-8")
    assert rendered.startswith(FRONTMATTER)
    assert yaml.safe_load(rendered.split("---", 2)[1])["allowed-tools"] == ["Read", "Bash"]
    assert ".agents/skills/alpha/SKILL.md" in rendered
    assert "Read .agents/skills/alpha/references/notes.md." not in rendered
    assert sorted(p.name for p in destination.iterdir()) == ["SKILL.md"]
    assert (source / "SKILL.md").read_bytes() == before[".agents/skills/alpha/SKILL.md"]
    manifest_path = next(p for p in plan.writes if p.endswith("/.projection-manifest.json"))
    manifest = json.loads((root / manifest_path).read_text(encoding="utf-8"))
    assert set(manifest["paths"]) == set(plan.writes)
    after = snapshots(root)
    assert project_harness.run(name, "write") == 0
    assert project_harness.run(name, "check") == 0
    assert snapshots(root) == after


def test_body_and_helper_edits_do_not_change_registration_bytes(projection):
    name, root, source, _ = projection
    assert project_harness.run(name, "write") == 0
    first = dict(project_harness.build_plan(name).writes)
    (source / "SKILL.md").write_text(FRONTMATTER + "Changed body read in place.\n", encoding="utf-8")
    (source / "helpers/run.py").write_text("print('changed')\n", encoding="utf-8")
    (source / "references/notes.md").unlink()
    assert project_harness.build_plan(name).writes == first
    assert project_harness.run(name, "check") == 0


def test_frontmatter_edit_changes_pointer_and_check_is_read_only(projection):
    name, root, source, destination = projection
    assert project_harness.run(name, "write") == 0
    old = (destination / "SKILL.md").read_bytes()
    (source / "SKILL.md").write_text(
        FRONTMATTER.replace("Example skill.", "New discovery description.") + "Body.\n", encoding="utf-8"
    )
    before = snapshots(root)
    assert project_harness.run(name, "check") == 1
    assert snapshots(root) == before
    assert project_harness.run(name, "write") == 0
    assert (destination / "SKILL.md").read_bytes() != old


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
def test_invalid_frontmatter_refuses_before_output(projection, frontmatter):
    name, root, source, _ = projection
    (source / "SKILL.md").write_text(f"---\n{frontmatter}---\nBody.\n", encoding="utf-8")
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
def test_invalid_source_refuses_before_output(projection, text):
    name, root, source, _ = projection
    (source / "SKILL.md").write_text(text, encoding="utf-8")
    before = snapshots(root)
    assert project_harness.run(name, "write") == 2
    assert snapshots(root) == before


def test_retired_skill_pointer_cleanup_preserves_unlisted_work(projection):
    name, root, source, destination = projection
    assert project_harness.run(name, "write") == 0
    foreign = destination / "local.txt"
    foreign.write_bytes(b"Unlisted work must survive.\n")
    (source / "SKILL.md").unlink()
    before = snapshots(root)
    assert project_harness.run(name, "check") == 1
    assert snapshots(root) == before
    assert project_harness.run(name, "write") == 0
    assert not (destination / "SKILL.md").exists()
    assert foreign.read_bytes() == b"Unlisted work must survive.\n"


def test_failed_replace_preserves_target_and_foreign_temporary(projection, monkeypatch):
    name, root, _, destination = projection
    assert project_harness.run(name, "write") == 0
    (destination / "SKILL.md").write_bytes(b"Preserve until atomic replacement.\n")
    (destination / ".SKILL.md.tmp").write_bytes(b"Independent temporary work.\n")
    before = snapshots(root)

    def fail_replace(source, destination):
        raise OSError("injected replacement failure")

    monkeypatch.setattr(project_harness.os, "replace", fail_replace)
    with pytest.raises(OSError, match="injected replacement failure"):
        project_harness.run(name, "write")
    assert snapshots(root) == before


@pytest.mark.parametrize("name", NATIVE_HOSTS)
def test_native_skill_hosts_emit_no_skill_tree(name, tmp_path, monkeypatch):
    source = seed(tmp_path, monkeypatch)
    plan = project_harness.build_plan(name)
    assert not plan.gaps, plan.gaps
    assert not [path for path in plan.writes if "/skills/" in path]
    assert (source / "helpers/run.py").read_bytes() == b"print('example')\r\n"
