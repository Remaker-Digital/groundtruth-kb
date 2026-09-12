"""Current registry reads use their canonical declaration without side effects."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.project.artifact_membership_reconciliation import observe_governed_knowledge
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot, validate_registry
from groundtruth_kb.project.sot_registry import load_toml


def test_registry_read_requires_an_explicit_project_or_declaration(tmp_path, monkeypatch):
    from groundtruth_kb.project.registry_control_plane import RegistryControlPlaneError, inspect_registry
    from groundtruth_kb.project.sot_registry import default_registry_path

    _config, declaration = _seed(tmp_path)
    monkeypatch.chdir(tmp_path)
    before = _files(tmp_path)
    with pytest.raises(ValueError, match="project_root is required"):
        default_registry_path()
    for reader in (load_registry_snapshot, inspect_registry):
        with pytest.raises(RegistryControlPlaneError, match="project_root or registry_path is required"):
            reader()
    assert default_registry_path(tmp_path) == declaration
    assert load_registry_snapshot(registry_path=declaration).records[0].id == "sample"
    assert _files(tmp_path) == before


def _declaration(notes: str) -> str:
    return f'''[[artifacts]]
id = "sample"
domain = "control_surface"
lifecycle = "active"
storage_path = "scripts/sample.py"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "governed implementation edit"
versioning_policy = "git_tracked"
backup_policy = "git_tracked"
health_check_function = ""
owner_role = "shared"
restore_action = "git_restore"
coverage_mode = "exact"
notes = "{notes}"
'''


def _seed(root: Path) -> tuple[Path, Path]:
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root = "."\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    declaration = root / "config/registry/sot-artifacts.toml"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(_declaration("current source"), encoding="utf-8")
    member = root / "scripts/sample.py"
    member.parent.mkdir()
    member.write_text("pass\n", encoding="utf-8")
    return config, declaration


def _files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("command", [["list"], ["show", "sample"]])
def test_ordinary_registry_cli_reads_without_database_or_packaged_copy(tmp_path: Path, command: list[str]) -> None:
    config, _ = _seed(tmp_path)
    before = _files(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "registry", *command, "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    record = data[0] if isinstance(data, list) else data
    assert record["id"] == "sample"
    assert record["notes"] == "current source"
    assert _files(tmp_path) == before
    assert not (tmp_path / ".gtkb-state").exists()


@pytest.mark.parametrize("reader", ["toml", "snapshot", "cli"])
def test_current_registry_read_ignores_stale_companions_without_repairing_them(tmp_path: Path, reader: str) -> None:
    config, declaration = _seed(tmp_path)
    packaged = tmp_path / "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"
    packaged.parent.mkdir(parents=True)
    packaged.write_text(_declaration("obsolete copy"), encoding="utf-8")
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        conn.execute("CREATE TABLE historical_marker (value TEXT)")
        conn.execute("INSERT INTO historical_marker VALUES ('preserve existing database')")
    before = _files(tmp_path)

    if reader == "toml":
        notes = load_toml(declaration)[0].notes
    elif reader == "snapshot":
        notes = load_registry_snapshot(project_root=tmp_path).records[0].notes
    else:
        result = CliRunner().invoke(main, ["--config", str(config), "registry", "show", "sample", "--json"])
        assert result.exit_code == 0, result.output
        notes = json.loads(result.output)["notes"]

    assert notes == "current source"
    assert _files(tmp_path) == before
    assert not (tmp_path / ".gtkb-state").exists()


def test_invalid_canonical_registry_is_not_replaced_by_valid_packaged_copy(tmp_path: Path) -> None:
    config, declaration = _seed(tmp_path)
    packaged = tmp_path / "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"
    packaged.parent.mkdir(parents=True)
    packaged.write_text(_declaration("obsolete copy"), encoding="utf-8")
    declaration.write_text("[[invalid TOML", encoding="utf-8")
    before = _files(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "list", "--json"])

    assert result.exit_code != 0
    assert "TOML" in result.output
    assert "obsolete copy" not in result.output
    assert _files(tmp_path) == before
    assert not (tmp_path / ".gtkb-state").exists()


def test_successive_registry_reads_observe_current_declaration(tmp_path: Path) -> None:
    _, declaration = _seed(tmp_path)
    first = load_registry_snapshot(project_root=tmp_path)
    declaration.write_text(_declaration("updated source"), encoding="utf-8")
    second = load_registry_snapshot(project_root=tmp_path)

    assert first.records[0].notes == "current source"
    assert second.records[0].notes == "updated source"
    assert first.declaration_digest != second.declaration_digest


def test_config_file_selects_registry_root_when_project_root_is_omitted(tmp_path: Path) -> None:
    config, _ = _seed(tmp_path)
    config.write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    before = _files(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "show", "sample", "--json"])

    assert result.exit_code == 0, result.output[:500]
    assert json.loads(result.output)["notes"] == "current source"
    assert _files(tmp_path) == before


def test_registry_inspection_reports_current_identity_without_replica_metadata(tmp_path: Path) -> None:
    config, _ = _seed(tmp_path)
    before = _files(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "inspect", "--no-census", "--json"])

    assert result.exit_code == 0, result.output[:500]
    report = json.loads(result.output)
    assert report["record_count"] == 1
    assert report["identity_state"]["current"] is True
    assert not {"packaged_digest", "projection_digest", "currentness"} & report.keys()
    assert _files(tmp_path) == before
    assert not (tmp_path / ".gtkb-state").exists()


def test_registry_validation_still_reports_missing_registered_object(tmp_path: Path) -> None:
    _seed(tmp_path)
    (tmp_path / "scripts/sample.py").unlink()
    before = _files(tmp_path)

    report = validate_registry(project_root=tmp_path, require_reverse_closure=False)

    assert report["valid"] is False
    assert "registry_identity_failure" in report["errors"]
    assert report["identity_state"]["missing"] == [{"id": "sample", "path": "scripts/sample.py"}]
    assert _files(tmp_path) == before


def test_knowledge_inventory_does_not_create_a_missing_authority(tmp_path: Path) -> None:
    _seed(tmp_path)
    snapshot = load_registry_snapshot(project_root=tmp_path)
    before = _files(tmp_path)

    result = observe_governed_knowledge(tmp_path, snapshot, tmp_path / "groundtruth.db")

    assert result.succeeded is False
    assert result.diagnostics
    assert _files(tmp_path) == before


def test_knowledge_inventory_does_not_upgrade_an_old_database(tmp_path: Path) -> None:
    _seed(tmp_path)
    with sqlite3.connect(tmp_path / "groundtruth.db") as conn:
        conn.execute("CREATE TABLE historical_marker (value TEXT)")
        conn.execute("INSERT INTO historical_marker VALUES ('preserve this schema')")
    snapshot = load_registry_snapshot(project_root=tmp_path)
    before = _files(tmp_path)

    result = observe_governed_knowledge(tmp_path, snapshot, tmp_path / "groundtruth.db")

    assert result.succeeded is False
    assert result.diagnostics
    assert _files(tmp_path) == before


def test_knowledge_inventory_reports_unavailable_selected_authority_without_sqlite_fallback(tmp_path: Path) -> None:
    config, _ = _seed(tmp_path)
    config.write_text('[groundtruth]\nauthority_url = "http://127.0.0.1:1"\n', encoding="utf-8")
    before = _files(tmp_path)

    result = observe_governed_knowledge(
        tmp_path, load_registry_snapshot(project_root=tmp_path), tmp_path / "groundtruth.db"
    )

    assert result.succeeded is False
    assert any("configured authority is unavailable" in item for item in result.diagnostics)
    assert _files(tmp_path) == before


def test_native_registry_cli_exposes_current_reads_and_reports_failed_knowledge_inventory(tmp_path: Path) -> None:
    config, _ = _seed(tmp_path)
    config.write_text('[groundtruth]\nauthority_url = "http://127.0.0.1:1"\n', encoding="utf-8")
    before = _files(tmp_path)
    runner = CliRunner()

    listed = runner.invoke(main, ["--config", str(config), "registry", "list", "--json"])
    assert listed.exit_code == 0, listed.output[:500]
    assert json.loads(listed.output)[0]["id"] == "sample"
    inspected = runner.invoke(main, ["--config", str(config), "registry", "reconcile", "--json"])
    report = json.loads(inspected.output)
    governed = next(item for item in report["observers"] if item["observer_class"] == "governed_knowledge")
    assert governed["succeeded"] is False
    assert any("configured authority is unavailable" in item for item in governed["diagnostics"])
    assert report["sweep_eligible"] is False
    assert report["release_eligible"] is False
    assert _files(tmp_path) == before


def test_doctor_reports_actual_inventory_failure_without_revision_audit(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_sot_registry_completeness

    _seed(tmp_path)
    # Make three independent inventory failures deterministic regardless of
    # whether the runner places its temporary directory inside a Git checkout.
    (tmp_path / "pyproject.toml").write_text("[invalid", encoding="utf-8")
    before = _files(tmp_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail"
    assert "membership incomplete" in result.message
    assert "capability_inventory inventory failed" in result.message
    assert "package_and_entrypoint inventory failed" in result.message
    assert "governed_knowledge inventory failed" in result.message
    assert "+1 more" not in result.message
    assert "audit" not in result.message
    assert _files(tmp_path) == before


def test_inventory_honors_environment_authority_without_loading_callers_project(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "target"
    root.mkdir()
    config, _ = _seed(root)
    config.unlink()
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "wrong-project.db"\n', encoding="utf-8")
    monkeypatch.chdir(caller)
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:1")
    before = _files(tmp_path)
    result = observe_governed_knowledge(root, load_registry_snapshot(project_root=root), root / "groundtruth.db")
    assert result.succeeded is False
    assert any("configured authority is unavailable" in item for item in result.diagnostics)
    assert _files(tmp_path) == before


def test_registry_cli_starts_without_repository_script_imports(tmp_path: Path) -> None:
    config, _ = _seed(tmp_path)
    source = Path(__file__).resolve().parents[3] / "groundtruth-kb/src"
    before = _files(tmp_path)
    program = """
import importlib.abc
import sys
class NoRepositoryScripts(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts" or fullname.startswith("scripts."):
            raise ModuleNotFoundError("Repository-only scripts are unavailable")
sys.meta_path.insert(0, NoRepositoryScripts())
sys.path.insert(0, sys.argv[1])
from groundtruth_kb.cli import main
main(["--config", sys.argv[2], "registry", "list"], standalone_mode=False)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(source), str(config)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "sample" in result.stdout
    assert _files(tmp_path) == before


def test_capability_observer_reads_only_current_baseline_sources(tmp_path: Path) -> None:
    from groundtruth_kb.project.artifact_membership_reconciliation import observe_capability_inventory

    _config, _ = _seed(tmp_path)
    baseline = tmp_path / ".harness-baseline-configuration"
    rule = baseline / "rules/current.md"
    rule.parent.mkdir(parents=True)
    rule.write_text("current guidance", encoding="utf-8")
    generated = tmp_path / "unrelated-output/current.md"
    generated.parent.mkdir()
    generated.write_text("unrelated generated output", encoding="utf-8")
    cache = baseline / "hooks/__pycache__/helper.pyc"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"bytecode")
    (baseline / ".projection-manifest.json").write_text("{}", encoding="utf-8")
    snapshot = load_registry_snapshot(project_root=tmp_path)
    before = _files(tmp_path)
    result = observe_capability_inventory(tmp_path, snapshot, tmp_path / "absent.db")
    assert result.succeeded, result.diagnostics
    assert {item.relative_path for item in result.observations} == {".harness-baseline-configuration/rules/current.md"}
    assert _files(tmp_path) == before
    added = baseline / "rules/new.md"
    added.write_text("new current guidance", encoding="utf-8")
    refreshed = observe_capability_inventory(tmp_path, snapshot, tmp_path / "absent.db")
    assert {item.relative_path for item in refreshed.observations} == {
        ".harness-baseline-configuration/rules/current.md",
        ".harness-baseline-configuration/rules/new.md",
    }


def test_missing_baseline_is_reported_without_legacy_fallback(tmp_path: Path) -> None:
    from groundtruth_kb.project.artifact_membership_reconciliation import observe_capability_inventory

    _seed(tmp_path)
    before = _files(tmp_path)
    result = observe_capability_inventory(
        tmp_path, load_registry_snapshot(project_root=tmp_path), tmp_path / "absent.db"
    )
    assert not result.succeeded
    assert any("baseline root" in item.lower() for item in result.diagnostics)
    assert _files(tmp_path) == before


def test_baseline_observer_refuses_unreadable_subtree_without_partial_success(tmp_path: Path, monkeypatch) -> None:
    from groundtruth_kb.project.artifact_membership_reconciliation import observe_capability_inventory

    _seed(tmp_path)
    baseline = tmp_path / ".harness-baseline-configuration"
    blocked = baseline / "rules"
    blocked.mkdir(parents=True)
    original = Path.iterdir

    def unreadable(path):
        if path == blocked:
            raise PermissionError("Unreadable baseline rules")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", unreadable)
    result = observe_capability_inventory(
        tmp_path, load_registry_snapshot(project_root=tmp_path), tmp_path / "absent.db"
    )
    assert not result.succeeded
    assert any("Unreadable baseline rules" in item for item in result.diagnostics)


@pytest.mark.parametrize("storage", ["../escape.py", "scripts/./sample.py", "scripts//sample.py"])
def test_public_toml_reader_rejects_unsafe_or_unnormalized_locators(tmp_path: Path, storage: str) -> None:
    _config, declaration = _seed(tmp_path)
    declaration.write_text(_declaration("bad locator").replace("scripts/sample.py", storage), encoding="utf-8")
    with pytest.raises(ValueError, match="locator|relative"):
        load_toml(declaration)


def test_baseline_observer_does_not_follow_linked_tree(tmp_path: Path) -> None:
    from groundtruth_kb.project.artifact_membership_reconciliation import observe_capability_inventory

    _seed(tmp_path)
    baseline = tmp_path / ".harness-baseline-configuration"
    baseline.mkdir()
    outside = tmp_path.parent / (tmp_path.name + "-outside")
    outside.mkdir()
    (outside / "private.txt").write_text("outside baseline", encoding="utf-8")
    linked = baseline / "linked"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(outside)], check=True, capture_output=True)
    else:
        linked.symlink_to(outside, target_is_directory=True)
    result = observe_capability_inventory(
        tmp_path, load_registry_snapshot(project_root=tmp_path), tmp_path / "absent.db"
    )
    assert not result.succeeded
    assert not result.observations
    assert any("Cannot follow" in item for item in result.diagnostics)
