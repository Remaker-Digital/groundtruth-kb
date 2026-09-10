"""Canonical declaration mutations preserve scope without permission ledgers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import registry_control_plane as registry
from groundtruth_kb.project.sot_registry import SoTArtifact


def record(ident: str, path: str, **changes) -> SoTArtifact:
    return SoTArtifact(
        **{
            "id": ident,
            "domain": "control_surface",
            "lifecycle": "active",
            "storage_path": path,
            "authority_spec_id": "GOV-REGISTRY",
            "mutation_api": "gt registry amend",
            "versioning_policy": "git_tracked",
            "backup_policy": "git_tracked",
            "health_check_function": "",
            "owner_role": "shared",
            "restore_action": "git_restore",
            "coverage_mode": "exact",
            **changes,
        }
    )


@pytest.fixture
def project(tmp_path: Path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\ndb_path="groundtruth.db"\n', encoding="utf-8")
    declaration = tmp_path / "config/registry/sot-artifacts.toml"
    declaration.parent.mkdir(parents=True)
    declaration.write_bytes(registry.serialize_registry([record("registry", "config/registry/sot-artifacts.toml")]))
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_spec(
            id="GOV-REGISTRY",
            title="Current registry contract",
            status="active",
            changed_by="test",
            change_reason="Fixture",
        )
    finally:
        db.close()
    (tmp_path / "keep.txt").write_text("unrelated work", encoding="utf-8")
    return tmp_path, config, declaration


def invoke(project, *args):
    return CliRunner().invoke(main, ["--config", str(project[1]), "registry", *args])


def test_register_and_retry_change_only_the_canonical_declaration(project):
    root, _config, declaration = project
    (root / "member.py").write_text("value = 1\n", encoding="utf-8")
    database = (root / "groundtruth.db").read_bytes()
    payload = json.dumps(asdict(record("member", "member.py")))
    result = invoke(project, "register", "--record-json", payload)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["changed"] is True
    final = declaration.read_bytes()
    retry = invoke(project, "register", "--record-json", payload)
    assert retry.exit_code == 0, retry.output
    assert json.loads(retry.output)["changed"] is False
    assert declaration.read_bytes() == final
    assert (root / "groundtruth.db").read_bytes() == database
    assert (root / "keep.txt").read_text(encoding="utf-8") == "unrelated work"
    assert not (root / ".gtkb-state").exists()
    assert not (root / "groundtruth-kb").exists()


@pytest.mark.parametrize(
    "changes",
    [
        {"storage_path": "../outside.py"},
        {"coverage_mode": "recursive"},
        {"authority_spec_id": "GOV-MISSING"},
        {"domain": "invalid"},
    ],
)
def test_invalid_registration_preserves_source_and_database(project, changes):
    root, _config, declaration = project
    (root / "member.py").write_text("value = 1\n", encoding="utf-8")
    before = declaration.read_bytes(), (root / "groundtruth.db").read_bytes()
    result = invoke(project, "register", "--record-json", json.dumps(asdict(record("member", "member.py", **changes))))
    assert result.exit_code != 0
    assert (declaration.read_bytes(), (root / "groundtruth.db").read_bytes()) == before
    assert not (root / ".gtkb-state").exists()


def test_amend_refuses_identity_change_and_stale_preimage(project):
    root, _config, declaration = project
    before = declaration.read_bytes()
    wrong_kind = invoke(project, "amend", "registry", "--changes-json", '{"storage_path":"other.toml"}')
    assert wrong_kind.exit_code != 0 and "transition" in wrong_kind.output
    assert declaration.read_bytes() == before
    initial_digest = registry.load_registry_snapshot(project_root=root).declaration_digest
    changed = invoke(project, "amend", "registry", "--changes-json", '{"notes":"first update"}')
    assert changed.exit_code == 0, changed.output
    final = declaration.read_bytes()
    stale = invoke(
        project,
        "amend",
        "registry",
        "--changes-json",
        '{"notes":"stale update"}',
        "--expected-declaration-digest",
        initial_digest,
    )
    assert stale.exit_code != 0 and "changed" in stale.output
    assert declaration.read_bytes() == final


def test_registration_failure_before_replace_keeps_old_source_and_allows_retry(project, monkeypatch):
    root, _config, declaration = project
    (root / "member.py").write_text("value = 1\n", encoding="utf-8")
    before = declaration.read_bytes()
    original = registry.os.replace

    def refuse_replace(source, target):
        if Path(target) == declaration:
            raise OSError("fixture replacement failed")
        return original(source, target)

    monkeypatch.setattr(registry.os, "replace", refuse_replace)
    with pytest.raises(OSError, match="replacement failed"):
        registry.register_artifacts([record("member", "member.py")], project_root=root)
    assert declaration.read_bytes() == before
    assert not list(declaration.parent.glob("*.tmp"))
    monkeypatch.setattr(registry.os, "replace", original)
    assert registry.register_artifacts([record("member", "member.py")], project_root=root)["changed"] is True


def test_parallel_cli_registrations_preserve_each_others_additions(project):
    root, config, _declaration = project
    for index in range(4):
        (root / f"member{index}.py").write_text(f"value = {index}\n", encoding="utf-8")

    def add(index):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(config),
                "registry",
                "register",
                "--record-json",
                json.dumps(asdict(record(f"member{index}", f"member{index}.py"))),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )

    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(workers.map(add, range(4)))
    assert all(result.returncode == 0 for result in results), [(item.stdout, item.stderr) for item in results]
    assert {item.id for item in registry.load_registry_snapshot(project_root=root).records} == {
        "registry",
        *(f"member{index}" for index in range(4)),
    }


def test_fresh_process_recovers_after_writer_dies_following_atomic_replace(project):
    root, config, declaration = project
    (root / "member.py").write_text("value = 1\n", encoding="utf-8")
    payload = json.dumps(asdict(record("member", "member.py")))
    code = """import json,os,sys
from pathlib import Path
from groundtruth_kb.project import registry_control_plane as r
from groundtruth_kb.project.sot_registry import _parse_record
original=r._atomic_replace
def exit_after_replace(path,payload):
    original(path,payload)
    os._exit(97)
r._atomic_replace=exit_after_replace
r.register_artifacts([_parse_record(json.loads(sys.argv[2]))],project_root=Path(sys.argv[1]))
"""
    crashed = subprocess.run(
        [sys.executable, "-c", code, str(root), payload],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    assert crashed.returncode == 97, crashed.stderr
    final = declaration.read_bytes()
    retried = subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb",
            "--config",
            str(config),
            "registry",
            "register",
            "--record-json",
            payload,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    assert retried.returncode == 0, retried.stderr
    assert json.loads(retried.stdout)["changed"] is False
    assert declaration.read_bytes() == final
    assert not (root / ".gtkb-state").exists()


def test_dry_run_preserves_all_bytes_and_amend_preserves_comments(project):
    root, _config, declaration = project
    original = declaration.read_text(encoding="utf-8").replace('notes = ""', 'notes = ""  # retain this explanation')
    original = "# Owner-authored context\n" + original
    declaration.write_text(original, encoding="utf-8", newline="\n")

    # SQLite may create its own WAL coordination files even for mode=ro.
    # Preserve every authored file and database byte; do not disable live WAL reads.
    def files():
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and path.name not in {"groundtruth.db-wal", "groundtruth.db-shm"}
        }

    before = files()
    preview = invoke(project, "amend", "registry", "--changes-json", '{"notes":"updated"}', "--dry-run")
    assert preview.exit_code == 0, preview.output
    assert json.loads(preview.output)["dry_run"] is True
    assert files() == before
    applied = invoke(project, "amend", "registry", "--changes-json", '{"notes":"updated"}')
    assert applied.exit_code == 0, applied.output
    assert declaration.read_text(encoding="utf-8") == original.replace('notes = ""', 'notes = "updated"')


def test_transition_reconciles_actual_rename_and_refuses_uncovered_content(project):
    root, _config, declaration = project
    old, new = root / "old.py", root / "new.py"
    old.write_text("value = 1\n", encoding="utf-8")
    assert registry.register_artifacts([record("member", "old.py")], project_root=root)["changed"]
    before = declaration.read_bytes()
    removal = invoke(project, "transition", "member", "--remove")
    assert removal.exit_code != 0 and "lose coverage" in removal.output
    assert declaration.read_bytes() == before and old.is_file()
    old.resolve().relative_to(root.resolve())
    new.resolve().relative_to(root.resolve())
    old.rename(new)
    moved = invoke(project, "transition", "member", "--changes-json", '{"storage_path":"new.py"}')
    assert moved.exit_code == 0, moved.output
    assert (
        next(
            item for item in registry.load_registry_snapshot(project_root=root).records if item.id == "member"
        ).storage_path
        == "new.py"
    )
    assert new.read_text(encoding="utf-8") == "value = 1\n"


def test_identical_retry_cannot_report_success_after_requested_object_disappears(project):
    root, _config, declaration = project
    target = root / "member.py"
    target.write_text("value = 1\n", encoding="utf-8")
    requested = record("member", "member.py")
    registry.register_artifacts([requested], project_root=root)
    before = declaration.read_bytes()
    target.unlink()
    with pytest.raises(registry.RegistryCoverageError, match="actual lifecycle"):
        registry.register_artifacts([requested], project_root=root)
    assert declaration.read_bytes() == before


def test_registry_self_coverage_cannot_be_removed(project):
    _root, _config, declaration = project
    before = declaration.read_bytes()
    result = invoke(project, "transition", "registry", "--remove")
    assert result.exit_code != 0 and "own coverage" in result.output
    assert declaration.read_bytes() == before


@pytest.mark.parametrize("lifecycle,present", [("generated", False), ("deprecated", False), ("archive", True)])
def test_registration_refuses_lifecycle_that_disagrees_with_existence(project, lifecycle, present):
    root, _config, declaration = project
    if present:
        (root / "member.py").write_text("actual artifact", encoding="utf-8")
    before = declaration.read_bytes()
    result = invoke(
        project, "register", "--record-json", json.dumps(asdict(record("member", "member.py", lifecycle=lifecycle)))
    )
    assert result.exit_code != 0, result.output
    assert declaration.read_bytes() == before


@pytest.mark.parametrize(
    "old,new",
    [
        ("active", "generated"),
        ("generated", "active"),
        ("active", "deprecated"),
        ("deprecated", "active"),
        ("active", "archive"),
        ("generated", "archive"),
        ("deprecated", "archive"),
    ],
)
def test_legal_lifecycle_changes_reconcile_actual_surface(project, old, new):
    root, _config, declaration = project
    member = root / "member.py"
    member.write_text("actual artifact", encoding="utf-8")
    registry.register_artifacts([record("member", "member.py", lifecycle=old)], project_root=root)
    if new == "archive":
        member.unlink()
    result = invoke(project, "transition", "member", "--changes-json", json.dumps({"lifecycle": new}))
    assert result.exit_code == 0, result.output
    snapshot = registry.load_registry_snapshot(project_root=root)
    changed = next(item for item in snapshot.records if item.id == "member")
    assert changed.lifecycle == new
    assert (snapshot.resolver.resolve("member.py") is None) == (new == "archive")
    assert registry.registry_identity_state(snapshot, project_root=root)["current"]


@pytest.mark.parametrize(
    "old,new",
    [
        ("active", "active"),
        ("generated", "deprecated"),
        ("deprecated", "generated"),
        ("archive", "active"),
        ("archive", "archive"),
    ],
)
def test_undefined_or_noop_lifecycle_changes_refuse_without_writes(project, old, new):
    root, _config, declaration = project
    member = root / "member.py"
    if old != "archive":
        member.write_text("actual artifact", encoding="utf-8")
    registry.register_artifacts([record("member", "member.py", lifecycle=old)], project_root=root)
    if new != "archive" and not member.exists():
        member.write_text("replacement artifact", encoding="utf-8")
    before = declaration.read_bytes()
    result = invoke(project, "transition", "member", "--changes-json", json.dumps({"lifecycle": new}))
    assert result.exit_code != 0, result.output
    assert "lifecycle" in result.output.lower()
    assert declaration.read_bytes() == before


def test_archived_surface_reenters_through_registration(project):
    root, _config, declaration = project
    registry.register_artifacts([record("member", "member.py", lifecycle="archive")], project_root=root)
    (root / "member.py").write_text("new current surface", encoding="utf-8")
    result = invoke(project, "register", "--record-json", json.dumps(asdict(record("member", "member.py"))))
    assert result.exit_code == 0, result.output
    snapshot = registry.load_registry_snapshot(project_root=root)
    assert snapshot.resolver.resolve("member.py").lifecycle == "active"
    assert len([item for item in snapshot.records if item.id == "member"]) == 1


@pytest.mark.parametrize(
    "coverage,path,probe",
    [
        ("exact", "old/member.py", "old/member.py"),
        ("recursive", "old/", "old/member.py"),
        ("opaque_container", "old", "old/member.py"),
        ("glob", "old/*.py", "old/member.py"),
    ],
)
def test_archived_declarations_provide_no_membership_or_structural_coverage(coverage, path, probe):
    archived = record("gone", path, lifecycle="archive", coverage_mode=coverage)
    resolver = registry.RegistryResolver([archived])
    assert resolver.resolve(probe) is None
    assert resolver.resolve_operation_path(probe) is None
    assert not resolver.is_structural_ancestor("old")
    replacement = record("replacement", probe)
    assert registry.RegistryResolver([archived, replacement]).resolve(probe) == replacement


@pytest.mark.parametrize(
    "changes",
    [
        {"id": []},
        {"domain": []},
        {"notes": 7},
        {"storage_path": 7},
        {"mutation_api": False},
    ],
)
def test_malformed_record_fields_fail_with_usable_cli_error(project, changes):
    root, _config, declaration = project
    (root / "member.py").write_text("artifact", encoding="utf-8")
    before = declaration.read_bytes()
    payload = {**asdict(record("member", "member.py")), **changes}
    result = invoke(project, "register", "--record-json", json.dumps(payload))
    assert result.exit_code != 0
    assert "Error:" in result.output and "string" in result.output, result.output
    assert declaration.read_bytes() == before


@pytest.mark.parametrize("kind", ["inside", "existing", "outside"])
def test_reconcile_batch_output_is_explicit_json_and_never_clobbers(project, monkeypatch, kind):
    from groundtruth_kb.project import artifact_membership_reconciliation as membership

    root, _config, declaration = project
    (root / "member.py").write_text("actual artifact", encoding="utf-8")
    requested = asdict(record("member", "member.py"))
    # Isolate the output contract from the five independent inventory observers.
    monkeypatch.setattr(
        membership, "reconcile_artifact_membership", lambda *args, **kwargs: {"batch_records": [requested]}
    )
    output = root / "batch.json" if kind != "outside" else root.parent / (root.name + "-outside.json")
    if kind == "existing":
        output.write_text("owner content", encoding="utf-8")
    before = declaration.read_bytes()
    result = invoke(project, "reconcile", "--json", "--batch-output", str(output))
    assert declaration.read_bytes() == before
    if kind == "inside":
        assert result.exit_code == 0, result.output
        assert json.loads(output.read_text(encoding="utf-8")) == json.loads(json.dumps([requested]))
        registered = invoke(project, "register", "--batch-file", str(output))
        assert registered.exit_code == 0, registered.output
        assert registry.load_registry_snapshot(project_root=root).resolver.resolve("member.py").id == "member"
    else:
        assert result.exit_code != 0, result.output
        if kind == "existing":
            assert output.read_text(encoding="utf-8") == "owner content"
        else:
            assert not output.exists()


def test_registration_refuses_link_escape_and_preserves_external_file(project):
    root, _config, declaration = project
    outside = root.parent / (root.name + "-outside")
    outside.mkdir()
    external = outside / "member.py"
    external.write_text("outside content", encoding="utf-8")
    target = root / "members"
    if os.name == "nt":
        # Junction creation is available without the symbolic-link privilege.
        subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(outside)], check=True, capture_output=True)
    else:
        target.symlink_to(outside, target_is_directory=True)
    before = declaration.read_bytes()
    result = invoke(
        project,
        "register",
        "--record-json",
        json.dumps(asdict(record("members", "members/", coverage_mode="recursive"))),
    )
    assert result.exit_code != 0 and "escapes" in result.output, result.output
    assert declaration.read_bytes() == before
    assert target.exists() and external.read_text(encoding="utf-8") == "outside content"


def test_coverage_shrink_cannot_abandon_present_descendant(project):
    root, _config, declaration = project
    directory = root / "members"
    directory.mkdir()
    child = directory / "child.py"
    child.write_text("descendant", encoding="utf-8")
    registry.register_artifacts([record("members", "members/", coverage_mode="recursive")], project_root=root)
    before = declaration.read_bytes()
    result = invoke(
        project, "transition", "members", "--changes-json", '{"storage_path":"members","coverage_mode":"exact"}'
    )
    assert result.exit_code != 0 and "lose coverage" in result.output, result.output
    assert declaration.read_bytes() == before
    assert child.read_text(encoding="utf-8") == "descendant"


@pytest.mark.parametrize("missing_member", [False, True])
def test_current_registered_inventory_reports_missing_members_without_mutation(project, missing_member):
    from groundtruth_kb.inventory.string_scan import registered_artifact_inventory

    root, _config, declaration = project
    baseline = root / ".harness-baseline-configuration/rules/current.md"
    baseline.parent.mkdir(parents=True)
    baseline.write_text("current baseline", encoding="utf-8")
    member = root / "member.py"
    member.write_text("current artifact", encoding="utf-8")
    registry.register_artifacts(
        [
            record("baseline", ".harness-baseline-configuration/", coverage_mode="recursive"),
            record("configuration", "groundtruth.toml"),
            record("database", "groundtruth.db"),
            record("keep", "keep.txt"),
            record("member", "member.py"),
        ],
        project_root=root,
    )
    if missing_member:
        member.unlink()
    before = declaration.read_bytes(), (root / "groundtruth.db").read_bytes()
    snapshot = registry.load_registry_snapshot(project_root=root)
    report = registry.inspect_registry(project_root=root, include_census=True)
    _artifacts, paths, missing, _expansions = registered_artifact_inventory(root, snapshot=snapshot)
    assert report["coherent"] is True
    assert report["identity_state"]["current"] is (not missing_member)
    assert bool(missing) is missing_member
    if not missing_member:
        assert "member.py" in paths and "config/registry/sot-artifacts.toml" in paths
    assert (declaration.read_bytes(), (root / "groundtruth.db").read_bytes()) == before
    assert not (root / ".gtkb-state").exists()
    assert not (root / "groundtruth-kb").exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows byte-range locks enforce writes to a locked empty file")
def test_contended_empty_declaration_lock_waits_without_writing(project):
    root, _config, _declaration = project
    lock = registry._declaration_lock_path(root)
    holder_code = """import msvcrt,sys
from pathlib import Path
with Path(sys.argv[1]).open('a+b') as handle:
    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    print('held', flush=True)
    sys.stdin.readline()
    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
"""
    holder = subprocess.Popen(
        [sys.executable, "-c", holder_code, str(lock)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        assert holder.stdout.readline().strip() == "held"
        assert lock.stat().st_size == 0
        with (
            pytest.raises(registry.RegistryFileLockAcquisitionTimeout),
            registry._RegistryFileLock(lock, timeout=0.1),
        ):
            pytest.fail("A second context acquired an already held byte-range lock")
        assert lock.stat().st_size == 0
    finally:
        stdout, stderr = holder.communicate("release\n", timeout=5)
        assert holder.returncode == 0, (stdout, stderr)
    with registry._RegistryFileLock(lock, timeout=1):
        assert lock.stat().st_size == 0


def test_unrelated_archived_metadata_does_not_block_a_current_declaration_change(project):
    root, _config, declaration = project
    current = registry.load_registry_snapshot(project_root=root).records
    archived = record("retired", "retired.py", lifecycle="archive", mutation_api="", restore_action="noop")
    declaration.write_bytes(registry.serialize_registry([*current, archived]))
    before_archived = asdict(archived)
    db_before = (root / "groundtruth.db").read_bytes()
    changed = invoke(project, "amend", "registry", "--changes-json", '{"notes":"current correction"}')
    assert changed.exit_code == 0, changed.output
    after = registry.load_registry_snapshot(project_root=root)
    assert asdict(next(row for row in after.records if row.id == "retired")) == before_archived
    assert after.resolver.resolve("retired.py") is None
    assert (root / "groundtruth.db").read_bytes() == db_before
    before = declaration.read_bytes()
    invalid = invoke(project, "amend", "registry", "--changes-json", '{"mutation_api":""}')
    assert invalid.exit_code != 0 and "mutation_api must not be empty" in invalid.output
    assert declaration.read_bytes() == before
