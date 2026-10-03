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
    skill = root / ".harness-baseline-configuration/skills/alpha"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_bytes(
        b"\xef\xbb\xbf"
        + (FRONTMATTER + "Read .harness-baseline-configuration/skills/alpha/references/notes.md.\n")
        .replace("\n", "\r\n")
        .encode()
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
    assert ".harness-baseline-configuration/skills/alpha/SKILL.md" in rendered
    assert "Read .harness-baseline-configuration/skills/alpha/references/notes.md." not in rendered
    assert sorted(p.name for p in destination.iterdir()) == ["SKILL.md"]
    assert (source / "SKILL.md").read_bytes() == before[".harness-baseline-configuration/skills/alpha/SKILL.md"]
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
def test_native_skill_hosts_emit_only_baseline_pointer_files(name, tmp_path, monkeypatch):
    source = seed(tmp_path, monkeypatch)
    plan = project_harness.build_plan(name)
    assert not plan.gaps, plan.gaps
    catalog = {path: text for path, text in plan.writes.items() if path.startswith(".agents/skills/")}
    assert set(catalog) == {".agents/skills/alpha/SKILL.md"}
    assert catalog[".agents/skills/alpha/SKILL.md"].startswith(FRONTMATTER)
    assert (
        "Read and follow `.harness-baseline-configuration/skills/alpha/SKILL.md`"
        in catalog[".agents/skills/alpha/SKILL.md"]
    )
    assert "Authored reference." not in catalog[".agents/skills/alpha/SKILL.md"]
    assert not [path for path in plan.writes if "/helpers/" in path or "/references/" in path]
    assert (source / "helpers/run.py").read_bytes() == b"print('example')\r\n"


def test_native_profiles_share_identical_catalog_bytes_and_body_edits_are_read_in_place(tmp_path, monkeypatch):
    source = seed(tmp_path, monkeypatch)
    assert len(NATIVE_HOSTS) == 4
    first = {}
    for name in NATIVE_HOSTS:
        plan = project_harness.build_plan(name)
        assert not plan.gaps, (name, plan.gaps)
        catalog = {path: text for path, text in plan.writes.items() if path.startswith(".agents/skills/")}
        assert set(catalog) == {".agents/skills/alpha/SKILL.md"}
        manifest = json.loads(plan.writes[PROFILES["harnesses"][name]["config_dir"] + "/.projection-manifest.json"])
        assert set(catalog) <= set(manifest["paths"])
        first[name] = catalog
    assert all(catalog == first[NATIVE_HOSTS[0]] for catalog in first.values())
    (source / "SKILL.md").write_text(FRONTMATTER + "Changed authored body.\n", encoding="utf-8")
    (source / "helpers/run.py").write_text("print('changed')\n", encoding="utf-8")
    for name in NATIVE_HOSTS:
        plan = project_harness.build_plan(name)
        catalog = {path: text for path, text in plan.writes.items() if path.startswith(".agents/skills/")}
        assert catalog == first[name]


def test_only_fixed_native_catalog_sharing_is_allowed(tmp_path, monkeypatch):
    seed(tmp_path, monkeypatch)
    profiles = copy.deepcopy(PROFILES)
    first, second = NATIVE_HOSTS[:2]
    profiles["harnesses"][second]["extra_output_roots"] = [profiles["harnesses"][first]["config_dir"]]
    monkeypatch.setattr(project_harness, "load_profiles", lambda: profiles)
    plan = project_harness.build_plan(second)
    assert any("extra_output_root_overlaps" in gap for gap in plan.gaps), plan.gaps
    assert not (tmp_path / ".agents").exists()


def test_native_catalog_retires_only_named_resources_and_preserves_unmanaged_neighbors(tmp_path, monkeypatch):
    source = seed(tmp_path, monkeypatch)
    name = NATIVE_HOSTS[0]
    profile = PROFILES["harnesses"][name]
    resources = {
        ".agents/skills/gtkb-promote/references/validation-rules.md",
        ".agents/skills/gtkb-query/references/api-reference.md",
        ".agents/skills/gtkb-session-wrap/references/audit-checklist.md",
        ".agents/skills/gtkb-session-wrap/references/handoff-template.md",
        ".agents/skills/gtkb-spec-intake/helpers/spec_intake.py",
        ".agents/skills/gtkb-spec/references/assertion-format.md",
        ".agents/skills/gtkb-work-item/references/taxonomy.md",
    }
    for native in NATIVE_HOSTS:
        assert resources <= set(PROFILES["harnesses"][native]["leftover_paths"])
        assert not any(
            path.startswith(".agents/skills") for path in PROFILES["harnesses"][native].get("leftover_trees", [])
        )
    for path in resources:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"Former tracked resource.\n")
    neighbor = tmp_path / ".agents/skills/gtkb-spec-intake/helpers/local.py"
    neighbor.write_bytes(b"Unmanaged neighbor.\n")
    extra = tmp_path / ".agents/skills/local/SKILL.md"
    extra.parent.mkdir(parents=True)
    extra.write_bytes(b"Independent local skill.\n")
    before = snapshots(tmp_path)
    plan = project_harness.build_plan(name)
    assert not plan.gaps, plan.gaps
    assert resources <= set(plan.removes)
    assert neighbor.relative_to(tmp_path).as_posix() not in plan.removes
    assert extra.relative_to(tmp_path).as_posix() not in plan.removes
    assert snapshots(tmp_path) == before
    assert project_harness.run(name, "write") == 0
    assert all(not (tmp_path / path).exists() for path in resources)
    assert neighbor.read_bytes() == b"Unmanaged neighbor.\n"
    assert extra.read_bytes() == b"Independent local skill.\n"
    assert (source / "helpers/run.py").read_bytes() == b"print('example')\r\n"
    manifest = json.loads((tmp_path / profile["config_dir"] / ".projection-manifest.json").read_text())
    assert neighbor.relative_to(tmp_path).as_posix() not in manifest["paths"]
    assert extra.relative_to(tmp_path).as_posix() not in manifest["paths"]
