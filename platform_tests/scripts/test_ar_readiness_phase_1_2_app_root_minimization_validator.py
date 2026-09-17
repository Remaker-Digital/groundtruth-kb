"""Application registry classification and read-only boundary checks."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization

REPO_ROOT = Path(__file__).resolve().parents[2]


def _entry(name, kind="FILE", classification="authoritative_input", purpose="Application-owned input."):
    return {"name": name, "type": kind, "classification": classification, "purpose": purpose}


def _write_registry(app_root, entries=None, **fields):
    payload = {
        "schema_version": "2.0",
        "application": app_root.name,
        "top_level_artifacts": [_entry(".gtkb-app-isolation.json"), *(entries or [])],
        **fields,
    }
    path = app_root / ".gtkb-app-isolation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_raw_filesystem_validator_passes_when_entries_match(tmp_path):
    app_root = tmp_path / "applications" / "Example_App"
    (app_root / "src").mkdir(parents=True)
    (app_root / "CLAUDE.md").write_text("Application-owned instructions\n", encoding="utf-8")
    _write_registry(app_root, [_entry("src", "DIR"), _entry("CLAUDE.md")])
    result = validate_app_root_minimization(app_root, project_root=tmp_path)
    assert result.ok, result.first_error_message()
    assert {entry.name for entry in result.actual_entries} == {".gtkb-app-isolation.json", "CLAUDE.md", "src"}
    assert result.to_dict()["status"] == "pass"


def test_raw_filesystem_validator_fails_unregistered_top_level_entry(tmp_path):
    (tmp_path / "EXTRA.md").write_text("unregistered", encoding="utf-8")
    _write_registry(tmp_path)
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok
    assert "unregistered_top_level_artifact" in {f.code for f in result.findings}
    assert "EXTRA.md" in result.first_error_message()


def test_validator_enforces_classification_metadata_and_rejects_retired_buckets(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "tool.json").write_text("{}", encoding="utf-8")
    (tmp_path / "future").mkdir()
    _write_registry(
        tmp_path,
        [
            _entry("docs", "DIR", purpose=""),
            {"name": "tool.json", "type": "FILE", "bucket": "B", "tool": "Example", "justification": "Old model"},
            _entry("future", "DIR", classification="C"),
        ],
    )
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok
    assert {f.code for f in result.findings} >= {
        "entry_missing_purpose",
        "entry_invalid_classification",
        "entry_retired_bucket",
    }


def test_live_agent_red_registry_passes_complete_app_root():
    result = validate_app_root_minimization(REPO_ROOT / "applications" / "Agent_Red", project_root=REPO_ROOT)
    assert result.ok, result.first_error_message(limit=10)


def test_project_doctor_registered_application_checks_pass():
    from groundtruth_kb.project.doctor import _check_registered_application_roots

    check = _check_registered_application_roots(REPO_ROOT)
    assert check.status == "pass", check.message


@pytest.mark.parametrize(
    "classification", ["authoritative_input", "generated_output", "runtime_data", "bounded_temporary_output"]
)
def test_all_current_classifications_are_accepted_without_deleting_content(tmp_path, classification):
    artifact = tmp_path / "payload.bin"
    artifact.write_bytes(b"owned application bytes\x00\xff")
    registry = _write_registry(
        tmp_path,
        [
            _entry(
                "payload.bin",
                classification=classification,
                purpose="Fixture retained only until this test ends."
                if classification == "bounded_temporary_output"
                else "Application-owned artifact.",
            )
        ],
    )
    before = {p.name: p.read_bytes() for p in (artifact, registry)}
    result = validate_app_root_minimization(tmp_path)
    assert result.ok, result.first_error_message()
    assert before == {p.name: p.read_bytes() for p in (artifact, registry)}


@pytest.mark.parametrize("classification", ["generated_output", "runtime_data", "bounded_temporary_output"])
def test_unmaterialized_outputs_do_not_require_recreating_runtime_state(tmp_path, classification):
    _write_registry(tmp_path, [_entry("output", "DIR", classification, "Owned output; absent before producer runs.")])
    assert validate_app_root_minimization(tmp_path).ok
    assert not (tmp_path / "output").exists()


def test_missing_declared_authoritative_input_fails(tmp_path):
    _write_registry(tmp_path, [_entry("required.txt")])
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok
    assert "registry_entry_without_artifact" in {f.code for f in result.findings}


def test_git_ignore_and_tracking_never_hide_unclassified_material(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("ignored.bin\n", encoding="utf-8")
    ignored = tmp_path / "ignored.bin"
    ignored.write_bytes(b"ignored but unclassified")
    _write_registry(tmp_path, [_entry(".git", "DIR", "runtime_data"), _entry(".gitignore")])

    def deny_git(*args, **kwargs):
        raise AssertionError("classification must not consult Git")

    monkeypatch.setattr(subprocess, "run", deny_git)
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok and "ignored.bin" in result.first_error_message()
    assert ignored.read_bytes() == b"ignored but unclassified"


@pytest.mark.parametrize(
    "fields,code",
    [
        ({"schema_version": "1.0"}, "registry_schema_unsupported"),
        ({"schema_version": "next"}, "registry_schema_unsupported"),
        ({"application": "Different"}, "application_mismatch"),
        ({"application": ""}, "application_missing"),
        ({"top_level_artifacts": []}, "top_level_artifacts_invalid"),
        ({"top_level_artifacts": [None]}, "registry_entry_not_object"),
    ],
)
def test_invalid_registry_contract_is_reported(tmp_path, fields, code):
    path = _write_registry(tmp_path, **fields)
    before = path.read_bytes()
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok and code in {f.code for f in result.findings}
    assert path.read_bytes() == before


@pytest.mark.parametrize("name", ["../outside", "nested/path", "nested\\path", "E:outside", "..", ".", ""])
def test_registry_names_cannot_escape_top_level(tmp_path, name):
    _write_registry(tmp_path, [_entry(name)])
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok and "entry_invalid_name" in {f.code for f in result.findings}


def test_duplicate_names_and_type_mismatch_fail(tmp_path):
    (tmp_path / "content").mkdir()
    _write_registry(tmp_path, [_entry("content"), _entry("content", "DIR")])
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok
    assert {f.code for f in result.findings} >= {"entry_duplicate", "registry_entry_without_artifact"}


@pytest.mark.parametrize(
    "data,code",
    [
        (b"{", "registry_unreadable"),
        (b"\xff", "registry_unreadable"),
        (b"[]", "registry_root_not_object"),
        (b'{"application":"a","application":"b"}', "registry_unreadable"),
    ],
)
def test_unreadable_registry_never_becomes_a_pass(tmp_path, data, code):
    path = tmp_path / ".gtkb-app-isolation.json"
    path.write_bytes(data)
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok and code in {f.code for f in result.findings}
    assert path.read_bytes() == data


def test_missing_registry_and_root_are_reported(tmp_path):
    result = validate_app_root_minimization(tmp_path / "absent")
    assert {f.code for f in result.findings} >= {"registry_missing", "app_root_missing"}


def test_external_top_level_link_is_refused_without_touching_target(tmp_path):
    app = tmp_path / "Example"
    app.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "owned.txt").write_bytes(b"outside data")
    link = app / "linked"
    if os.name == "nt":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "New-Item -ItemType Junction -Path $env:GTKB_TEST_LINK -Target $env:GTKB_TEST_TARGET | Out-Null",
            ],
            env=dict(os.environ, GTKB_TEST_LINK=str(link), GTKB_TEST_TARGET=str(outside)),
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    else:
        link.symlink_to(outside, target_is_directory=True)
    _write_registry(app, [_entry("linked", "DIR")])
    result = validate_app_root_minimization(app)
    assert not result.ok and "artifact_outside_application" in {f.code for f in result.findings}
    assert (outside / "owned.txt").read_bytes() == b"outside data"


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("classification", " authoritative_input ", "entry_invalid_classification"),
        ("type", " DIR ", "entry_invalid_type"),
    ],
)
def test_noncanonical_enum_values_cannot_hide_missing_inputs(tmp_path, field, value, code):
    entry = _entry("missing")
    entry[field] = value
    _write_registry(tmp_path, [entry])
    result = validate_app_root_minimization(tmp_path)
    assert not result.ok and code in {f.code for f in result.findings}
