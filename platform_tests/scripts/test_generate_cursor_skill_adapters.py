"""Cursor skills derive directly from the neutral baseline, independently of peers."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "harness_projection"))
import project_harness  # noqa: E402


@pytest.fixture
def cursor_profiles(monkeypatch):
    profiles = copy.deepcopy(project_harness.load_profiles())
    profile = profiles["harnesses"]["cursor"]
    profiles["harnesses"] = {"cursor": profile}
    monkeypatch.setattr(project_harness, "load_profiles", lambda: profiles)
    return profiles


def _fixture(root: Path, names=("alpha", "beta")):
    for name in names:
        directory = root / ".harness-baseline-configuration/skills" / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_bytes(
            (
                f"---\nname: {name}\ndescription: {name} skill\n---\n\n"
                f"Run {{{{HARNESS_SKILLS_DIR}}}}/{name}/helpers/run.py and read "
                f"[notes]({{{{HARNESS_SKILLS_DIR}}}}/{name}/references/notes.md).\n"
            ).encode()
        )
        (directory / "helpers").mkdir()
        (directory / "helpers/run.py").write_bytes(b"print('ok')\r\n")
        (directory / "references").mkdir()
        (directory / "references/notes.md").write_bytes(b"Neutral notes.\n")


def _bytes(root: Path):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_cursor_plan_uses_only_neutral_sources_and_does_not_write(tmp_path, monkeypatch, cursor_profiles):
    _fixture(tmp_path)
    forbidden = [
        "config/agent-control",
        ".claude",
        ".codex",
        ".antigravity",
        "harness-state",
        ".gtkb-state",
        "groundtruth.db",
    ]
    for name in forbidden:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"Unparseable foreign bytes; no reads or mutations permitted.")
    before = _bytes(tmp_path)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    original_open = Path.open

    def guarded_open(path, *args, **kwargs):
        assert not any(path == tmp_path / name or tmp_path / name in path.parents for name in forbidden)
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as guard:
        guard.setattr(Path, "open", guarded_open)
        plan = project_harness.build_plan("cursor")
    assert not plan.gaps
    assert {path for path in plan.writes if path.endswith("/SKILL.md")} == {
        ".cursor/skills/alpha/SKILL.md",
        ".cursor/skills/beta/SKILL.md",
    }
    owned = json.loads(plan.writes[".cursor/.projection-manifest.json"])["paths"]
    assert set(owned) == set(plan.writes)
    assert _bytes(tmp_path) == before
    assert not (tmp_path / ".cursor").exists()


def test_cursor_frontmatter_resources_and_own_paths(tmp_path, monkeypatch, cursor_profiles):
    _fixture(tmp_path, ("alpha",))
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    assert project_harness.run("cursor", "write") == 0
    raw = (tmp_path / ".cursor/skills/alpha/SKILL.md").read_bytes()
    assert raw.startswith(b"---\n") and b"\r" not in raw
    text = raw.decode()
    assert yaml.safe_load(text.split("---", 2)[1]) == {"name": "alpha", "description": "alpha skill"}
    assert ".cursor/skills/alpha/helpers/run.py" in text
    assert ".cursor/skills/alpha/references/notes.md" in text
    assert "scripts/harness_projection/project_harness.py" in text
    helper = (tmp_path / ".cursor/skills/alpha/helpers/run.py").read_bytes()
    assert b"\r" not in helper
    assert ast.dump(ast.parse(helper)) == ast.dump(ast.parse("print('ok')"))
    assert "Neutral notes." in (tmp_path / ".cursor/skills/alpha/references/notes.md").read_text(encoding="utf-8")
    for peer in (".claude/", ".codex/", ".agents/", ".antigravity/", "config/agent-control"):
        assert peer not in text


def test_cursor_check_detects_crlf_without_writes(tmp_path, monkeypatch, cursor_profiles):
    _fixture(tmp_path, ("alpha",))
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    assert project_harness.run("cursor", "write") == 0
    target = tmp_path / ".cursor/skills/alpha/SKILL.md"
    target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
    before = _bytes(tmp_path)
    assert project_harness.run("cursor", "check") == 1
    assert _bytes(tmp_path) == before


def test_cursor_fresh_roots_and_second_run_are_deterministic(tmp_path, monkeypatch, cursor_profiles):
    results = []
    for name in ("left", "right"):
        root = tmp_path / name
        _fixture(root)
        monkeypatch.setattr(project_harness, "PROJECT_ROOT", root)
        assert project_harness.run("cursor", "write") == 0
        before = _bytes(root)
        assert project_harness.run("cursor", "check") == 0
        assert project_harness.run("cursor", "write") == 0
        assert _bytes(root) == before
        results.append(before)
    assert results[0] == results[1]


def test_cursor_refresh_preserves_unlisted_work_and_removes_retired_outputs(tmp_path, monkeypatch, cursor_profiles):
    _fixture(tmp_path, ("alpha",))
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    assert project_harness.run("cursor", "write") == 0
    foreign = tmp_path / ".cursor/skills/local/SKILL.md"
    foreign.parent.mkdir(parents=True)
    foreign.write_bytes(b"Locally authored work.\n")
    old = tmp_path / ".cursor/skills/MANIFEST.json"
    old.write_bytes(b"Old generated manifest.\n")
    manifest = tmp_path / ".cursor/.projection-manifest.json"
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["paths"].append(".cursor/skills/MANIFEST.json")
    manifest.write_text(json.dumps(value), encoding="utf-8")
    plan = project_harness.build_plan("cursor")
    assert not plan.gaps
    assert ".cursor/skills/MANIFEST.json" in plan.removes
    assert ".cursor/skills/local/SKILL.md" not in plan.removes
    assert project_harness.run("cursor", "write") == 0
    assert not old.exists()
    assert foreign.read_bytes() == b"Locally authored work.\n"
    assert project_harness.run("cursor", "check") == 0


@pytest.mark.parametrize("defect", ["unknown-token", "unknown-artifact"])
def test_cursor_source_gaps_refuse_all_projection_writes(tmp_path, monkeypatch, cursor_profiles, defect):
    _fixture(tmp_path, ("alpha",))
    source = tmp_path / ".harness-baseline-configuration/skills/alpha"
    if defect == "unknown-token":
        (source / "SKILL.md").write_text("{{UNKNOWN_CONTROL}}\n", encoding="utf-8")
    else:
        (source / "unclassified.bin").write_bytes(b"Unclassified bytes")
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    before = _bytes(tmp_path)
    assert project_harness.run("cursor", "write") == 2
    assert not (tmp_path / ".cursor").exists()
    assert _bytes(tmp_path) == before
