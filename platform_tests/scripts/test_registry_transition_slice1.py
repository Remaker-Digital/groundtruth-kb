"""Coverage transitions reconcile the current declaration and preserve artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict

import pytest
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot, serialize_registry

from platform_tests.groundtruth_kb.cli.test_registry_current_mutation_cli import invoke, record
from platform_tests.groundtruth_kb.cli.test_registry_current_mutation_cli import project as project


def test_coverage_transition_preserves_files_and_remaining_membership(project):
    root, _config, declaration = project
    members = root / "members"
    members.mkdir()
    child = members / "child.py"
    child.write_bytes(b"uncommitted = True\n")
    foreign = root / "keep.txt"
    original_files = {path: path.read_bytes() for path in (child, foreign, root / "groundtruth.db")}
    for item in (
        record("container", "members/", coverage_mode="opaque_container"),
        record("child", "members/child.py"),
    ):
        registered = invoke(project, "register", "--record-json", json.dumps(asdict(item)))
        assert registered.exit_code == 0, registered.output

    before = declaration.read_bytes()
    incomplete = invoke(project, "transition", "container", "--changes-json", '{"coverage_mode":"recursive"}')
    assert incomplete.exit_code != 0 and "overlap" in incomplete.output
    assert declaration.read_bytes() == before

    transitioned = invoke(
        project, "transition", "container", "--changes-json", '{"coverage_mode":"recursive"}', "--removal", "child"
    )
    assert transitioned.exit_code == 0, transitioned.output

    current = load_registry_snapshot(project_root=root)
    assert {item.id for item in current.records} == {"registry", "container"}
    assert current.resolver.resolve("members/child.py").id == "container"
    assert {path: path.read_bytes() for path in original_files} == original_files
    assert declaration.is_file()
    assert not (root / ".gtkb-state").exists()
    assert not (root / "groundtruth-kb/src/groundtruth_kb/data/registry/sot-artifacts.toml").exists()


def test_removals_file_exceeds_windows_argv_limit_and_matches_repeated_flags(project):
    root, config, declaration = project
    members = root / "members"
    members.mkdir()
    records = [
        record("registry", "config/registry/sot-artifacts.toml"),
        record("container", "members/", coverage_mode="opaque_container"),
    ]
    ids = []
    for index in range(180):
        ident = f"member-{'x' * 190}-{index}"
        relative = f"members/{index}.py"
        (root / relative).write_bytes(b"preserve = True\n")
        records.append(record(ident, relative))
        ids.append(ident)
    declaration.write_bytes(serialize_registry(records))
    before = declaration.read_bytes()
    list_path = root / "removals.json"
    list_path.write_text(json.dumps(ids), encoding="utf-8")
    assert list_path.stat().st_size > 32767
    fields = ["container", "--changes-json", '{"coverage_mode":"recursive"}']
    preview = invoke(
        project, "transition", *fields, "--dry-run", *[part for ident in ids for part in ("--removal", ident)]
    )
    assert preview.exit_code == 0, preview.output
    assert declaration.read_bytes() == before
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb",
            "--config",
            str(config),
            "registry",
            "transition",
            *fields,
            "--removals-file",
            str(list_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {**json.loads(preview.output), "dry_run": False}
    snapshot = load_registry_snapshot(project_root=root)
    assert {item.id for item in snapshot.records} == {"registry", "container"}
    assert all((members / f"{index}.py").read_bytes() == b"preserve = True\n" for index in range(180))


@pytest.mark.parametrize("file_value", [{}, [False], [["child"]], [""], ["missing"], ["registry"], ["child", "child"]])
def test_invalid_related_removals_preserve_the_entire_declaration(project, file_value):
    root, _config, declaration = project
    (root / "child.py").write_text("keep = True\n", encoding="utf-8")
    registered = invoke(project, "register", "--record-json", json.dumps(asdict(record("child", "child.py"))))
    assert registered.exit_code == 0, registered.output
    before = declaration.read_bytes()
    removals = root / "removals.json"
    removals.write_text(json.dumps(file_value), encoding="utf-8")
    result = invoke(
        project, "transition", "registry", "--changes-json", '{"notes":"current"}', "--removals-file", str(removals)
    )
    assert result.exit_code != 0, result.output
    assert declaration.read_bytes() == before
    assert (root / "child.py").read_text(encoding="utf-8") == "keep = True\n"
