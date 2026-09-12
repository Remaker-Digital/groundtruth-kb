"""Doctor checks real declaration/identity without replica or audit debt.

The membership census is isolated here; native inventory tests exercise the
five actual observers. Parsing and filesystem identity remain real below.
"""

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.project import registry_control_plane
from groundtruth_kb.project.doctor import _check_sot_registry_completeness


@pytest.fixture
def census(monkeypatch):
    membership = {
        "membership_complete": True,
        "counts": {"registered": 1, "unregistered_load_bearing": 0, "unregistered_disposable": 0, "invalid_unknown": 0},
        "observer_failures": [],
    }
    inspect = registry_control_plane.inspect_registry

    def selected_inspection(**kwargs):
        report = inspect(**{**kwargs, "include_census": False})
        report["membership_reconciliation"] = membership
        return report

    monkeypatch.setattr(registry_control_plane, "inspect_registry", selected_inspection)
    return membership


def _write_registry(root, path="x", lifecycle="active", coverage="exact"):
    declaration = root / "config/registry/sot-artifacts.toml"
    declaration.parent.mkdir(parents=True)
    fields = dict(
        id="sample",
        domain="control_surface",
        lifecycle=lifecycle,
        storage_path=path,
        coverage_mode=coverage,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="governed implementation edit; source config/registry/sot-artifacts.toml",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        restore_action="git_restore",
        health_check_function="",
        owner_role="shared",
    )
    import json

    declaration.write_text(
        "[[artifacts]]\n" + "".join(f"{k} = {json.dumps(v)}\n" for k, v in fields.items()), encoding="utf-8"
    )
    return declaration


def _files(root: Path):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_registry_missing_returns_info_skip(tmp_path, census):
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "info" and "not present" in result.message
    assert _files(tmp_path) == {}


@pytest.mark.parametrize("companion", ["absent", "empty_database", "stale_database", "invalid_packaged_copy"])
def test_canonical_registry_passes_without_replica_agreement(tmp_path, census, companion):
    _write_registry(tmp_path)
    (tmp_path / "x").write_bytes(b"current member")
    if companion in {"empty_database", "stale_database"}:
        with sqlite3.connect(tmp_path / "groundtruth.db") as db:
            db.execute("CREATE TABLE sot_artifacts (id TEXT, lifecycle TEXT)")
            if companion == "stale_database":
                db.execute("INSERT INTO sot_artifacts VALUES ('sample', 'deprecated')")
    elif companion == "invalid_packaged_copy":
        other = tmp_path / "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"
        other.parent.mkdir(parents=True)
        other.write_bytes(b"[[not valid TOML")
    before = _files(tmp_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", result.message
    assert _files(tmp_path) == before


@pytest.mark.parametrize("lifecycle", ["active", "generated", "deprecated"])
def test_every_present_lifecycle_requires_its_declared_object(tmp_path, census, lifecycle):
    _write_registry(tmp_path, lifecycle=lifecycle)
    before = _files(tmp_path)
    missing = _check_sot_registry_completeness(tmp_path)
    assert missing.status == "fail" and missing.required
    assert "registry identity failed: 1 missing locators" in missing.message
    assert _files(tmp_path) == before
    (tmp_path / "x").write_bytes(b"present")
    present = _check_sot_registry_completeness(tmp_path)
    assert present.status == "pass", present.message


def test_archived_object_must_be_absent(tmp_path, census):
    _write_registry(tmp_path, lifecycle="archive")
    assert _check_sot_registry_completeness(tmp_path).status == "pass"
    (tmp_path / "x").write_bytes(b"unexpectedly present; do not erase")
    before = _files(tmp_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail" and "registry identity failed" in result.message
    assert "1 archived objects still present" in result.message
    assert "archived objects still present: sample (x)" in result.message
    assert _files(tmp_path) == before


@pytest.mark.parametrize("path", ["membase:specifications", "windows-scheduled-task:example"])
def test_explicit_virtual_locator_has_no_filesystem_identity(tmp_path, census, path):
    _write_registry(tmp_path, path, coverage="virtual")
    before = _files(tmp_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "pass", result.message
    assert _files(tmp_path) == before


def test_glob_coverage_requires_an_actual_match(tmp_path, census):
    _write_registry(tmp_path, "members/*.toml", coverage="glob")
    assert _check_sot_registry_completeness(tmp_path).status == "fail"
    (tmp_path / "members").mkdir()
    (tmp_path / "members/one.toml").write_text("current = true\n", encoding="utf-8")
    assert _check_sot_registry_completeness(tmp_path).status == "pass"


@pytest.mark.parametrize("broken", ["[[not TOML", '[[artifacts]]\nid = "incomplete"\n'])
def test_invalid_canonical_declaration_fails_without_fallback(tmp_path, census, broken):
    _write_registry(tmp_path).write_text(broken, encoding="utf-8")
    before = _files(tmp_path)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail" and result.required
    assert "failed to load" in result.message
    assert _files(tmp_path) == before


def test_membership_failure_reports_record_and_gap_counts(tmp_path, census):
    _write_registry(tmp_path)
    (tmp_path / "x").write_bytes(b"present")
    census["membership_complete"] = False
    census["counts"].update(unregistered_load_bearing=2, invalid_unknown=1)
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail" and "1 SoT records" in result.message
    assert "2 load-bearing gaps, 1 invalid unknowns" in result.message


def test_unavailable_inventory_cannot_report_complete(tmp_path, census):
    _write_registry(tmp_path)
    (tmp_path / "x").write_bytes(b"present")
    census["membership_complete"] = False
    census["observer_failures"] = [{"observer_class": "governed_knowledge", "diagnostics": ["authority unavailable"]}]
    result = _check_sot_registry_completeness(tmp_path)
    assert result.status == "fail"
    assert "governed_knowledge inventory failed: authority unavailable" in result.message
