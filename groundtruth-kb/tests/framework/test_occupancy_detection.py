"""Application presence, shared marker schema and catalog diagnostics."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.isolation.doctor_verdicts import evaluate_isolation_state
from groundtruth_kb.isolation.occupancy_detector import detect_occupancy
from groundtruth_kb.isolation.registry_check import (
    ApplicationRegistryError,
    application_slot_path,
    has_registry_entry,
    load_application_catalog,
    resolve_project_repository,
)
from groundtruth_kb.isolation.validation import ValidationError, check_slot_markers, validate_self_completion_preflight


def write_registry(root, names):
    apps = root / "applications"
    apps.mkdir(parents=True, exist_ok=True)
    (apps / "registry.toml").write_text(
        "[applications]\n" + "".join(f'{name} = {{slot="{name}"}}\n' for name in names), encoding="utf-8"
    )


def _repository_git(root, *args):
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=root,
        env={key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
        check=True,
    ).stdout.strip()


@pytest.fixture
def repository_host(tmp_path):
    host = tmp_path / "host"
    host.mkdir()
    _repository_git(host, "init", "-q")
    write_registry(host, ["Alpha", "Beta"])
    for name in ("Alpha", "Beta"):
        root = application(host, name)
        _repository_git(root, "init", "-q")
    return host


@pytest.mark.parametrize("reference", ["platform", "application:Alpha", "application:Beta"])
def test_project_repository_resolves_only_explicit_catalog_identity(repository_host, reference):
    root = repository_host if reference == "platform" else repository_host / "applications" / reference.split(":")[1]
    assert resolve_project_repository(repository_host, reference) == root
    assert _repository_git(root, "rev-parse", "--show-toplevel") == root.as_posix()


@pytest.mark.parametrize(
    "reference",
    [None, "", "Platform", "application:alpha", "application:Missing", "application:../Alpha", "E:/somewhere"],
)
def test_invalid_project_repository_reference_never_falls_back_to_platform(repository_host, reference):
    before = _repository_git(repository_host, "worktree", "list", "--porcelain")
    with pytest.raises(ApplicationRegistryError):
        resolve_project_repository(repository_host, reference)
    assert _repository_git(repository_host, "worktree", "list", "--porcelain") == before


@pytest.mark.parametrize("marker", ["", '[application]\nname="Beta"\n', "[malformed"])
def test_project_repository_requires_current_matching_markers(repository_host, marker):
    root = repository_host / "applications/Alpha"
    (root / "application.toml").write_text(marker, encoding="utf-8")
    with pytest.raises(ApplicationRegistryError, match="markers"):
        resolve_project_repository(repository_host, "application:Alpha")


def test_catalog_registration_does_not_make_a_platform_subdirectory_an_application_repository(repository_host):
    application(repository_host, "Uninitialized")
    write_registry(repository_host, ["Alpha", "Beta", "Uninitialized"])
    with pytest.raises(ApplicationRegistryError, match="independent Git repository"):
        resolve_project_repository(repository_host, "application:Uninitialized")


def test_project_repository_revalidates_catalog_without_cached_path_fallback(repository_host):
    assert resolve_project_repository(repository_host, "application:Alpha").name == "Alpha"
    write_registry(repository_host, ["Beta"])
    with pytest.raises(ApplicationRegistryError, match="catalog entry"):
        resolve_project_repository(repository_host, "application:Alpha")


def test_inherited_git_environment_does_not_redirect_project_repository_resolution(repository_host, monkeypatch):
    other = repository_host / "applications/Beta"
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    assert resolve_project_repository(repository_host, "application:Alpha") == repository_host / "applications/Alpha"


def application(root, name="Example", **overrides):
    app = root / "applications" / name
    app.mkdir(parents=True)
    (app / "application.toml").write_text(f'[application]\nname="{name}"\n', encoding="utf-8")
    payload = {
        "schema_version": "2.0",
        "application": name,
        "top_level_artifacts": [
            {
                "name": value,
                "type": "FILE",
                "classification": "authoritative_input",
                "purpose": "Application-owned input.",
            }
            for value in ("application.toml", ".gtkb-app-isolation.json")
        ],
        **overrides,
    }
    (app / ".gtkb-app-isolation.json").write_text(json.dumps(payload), encoding="utf-8")
    return app


def test_non_marker_blocks_register(tmp_path, monkeypatch):
    app = tmp_path / "applications" / "foo"
    app.mkdir(parents=True)
    secret = app / ".env.local"
    secret.write_text("PRIVATE_VALUE=do-not-read", encoding="utf-8")
    original = Path.read_text

    def no_content_read(path, *args, **kwargs):
        assert path != secret
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", no_content_read)
    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] and status["trigger"] == "existing_content"
    assert ".env.local" in status["entries"]
    assert "PRIVATE_VALUE" not in json.dumps(status)


@pytest.mark.parametrize(
    "name,content",
    [
        ("README.md", "<!-- gtkb-application-slot-cleanup-marker -->\nhistorical cleanup text"),
        ("README.md", "ordinary application documentation"),
        (".gitkeep", ""),
        ("desktop.ini", "application data"),
    ],
)
def test_filename_and_cleanup_marker_never_make_content_disposable(tmp_path, name, content):
    app = tmp_path / "applications" / "foo"
    app.mkdir(parents=True)
    path = app / name
    path.write_text(content, encoding="utf-8")
    before = path.read_bytes()
    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] and status["entries"] == [name]
    assert path.read_bytes() == before


def test_registry_only_conflict(tmp_path):
    write_registry(tmp_path, ["foo"])
    status = detect_occupancy(tmp_path, "foo")
    assert status["occupied"] and status["trigger"] == "registry_entry"
    assert status["details"] == "Registry entry exists but no application directory"
    assert any(v["verdict"] == "Registry drift" for v in evaluate_isolation_state(tmp_path)["verdicts"])


def test_empty_slot_observation_has_no_write_or_cleanup_side_effect(tmp_path):
    app = tmp_path / "applications" / "Empty"
    app.mkdir(parents=True)
    assert not detect_occupancy(tmp_path, "Empty")["occupied"]
    diagnostic = evaluate_isolation_state(tmp_path)
    assert any(v["verdict"] == "Empty unregistered slot" for v in diagnostic["verdicts"])
    assert app.is_dir() and not list(app.iterdir())
    assert "rm -r" not in json.dumps(diagnostic)


def test_multiple_registered_applications_are_checked_independently(tmp_path):
    write_registry(tmp_path, ["First", "Second"])
    first = application(tmp_path, "First")
    second = application(tmp_path, "Second")
    before = {str(p): p.read_bytes() for app in (first, second) for p in app.iterdir()}
    result = evaluate_isolation_state(tmp_path)
    assert result["verdicts"] == []
    assert set(result["slots_status"]) == {"First", "Second"}
    (second / "unclassified.bin").write_bytes(b"must be reported")
    result = evaluate_isolation_state(tmp_path)
    assert len(result["verdicts"]) == 1
    assert "Second" in result["verdicts"][0]["details"] and "unclassified.bin" in result["verdicts"][0]["details"]
    assert all(Path(p).read_bytes() == b for p, b in before.items())


def test_doctor_reports_malformed_mismatched_and_partial_markers(tmp_path):
    assert evaluate_isolation_state(tmp_path)["verdicts"] == []
    write_registry(tmp_path, ["Example"])
    app = application(tmp_path)
    marker = app / ".gtkb-app-isolation.json"
    valid = marker.read_bytes()
    marker.write_text("invalid {", encoding="utf-8")
    assert any(v["verdict"] == "Malformed markers" for v in evaluate_isolation_state(tmp_path)["verdicts"])
    marker.write_text('{"application":"Different"}', encoding="utf-8")
    assert any(v["verdict"] == "Mismatched markers" for v in evaluate_isolation_state(tmp_path)["verdicts"])
    marker.write_bytes(valid)
    (app / "application.toml").unlink()
    assert any(v["verdict"] == "Partial slot registration" for v in evaluate_isolation_state(tmp_path)["verdicts"])


def test_current_schema_is_understood_by_both_readers_without_best_effort_warning(tmp_path, capsys):
    application(tmp_path)
    result = check_slot_markers(tmp_path, "Example")
    assert result["consistent"] and result["malformed"] == result["mismatched"] == []
    validate_self_completion_preflight(tmp_path, "Example")
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("version", ["1.0", "3.0", "nonsense", 2, True, None, {}])
def test_unsupported_registry_versions_are_refused_by_both_readers(tmp_path, version):
    app = application(tmp_path, schema_version=version)
    before = (app / ".gtkb-app-isolation.json").read_bytes()
    result = check_slot_markers(tmp_path, "Example")
    assert not result["consistent"]
    assert any("registry_schema_unsupported" in row["error"] for row in result["malformed"])
    with pytest.raises(ValidationError, match="registry_schema_unsupported"):
        validate_self_completion_preflight(tmp_path, "Example")
    assert (app / ".gtkb-app-isolation.json").read_bytes() == before


@pytest.mark.parametrize(
    "data",
    [
        b"[]",
        b"\xff",
        b'{"application":"Example","application":"Other"}',
        b'{"schema_version":"2.0","application":{},"top_level_artifacts":[]}',
    ],
)
def test_malformed_registry_markers_are_reported_without_crashing(tmp_path, data):
    app = application(tmp_path)
    path = app / ".gtkb-app-isolation.json"
    path.write_bytes(data)
    assert not check_slot_markers(tmp_path, "Example")["consistent"]
    with pytest.raises(ValidationError):
        validate_self_completion_preflight(tmp_path, "Example")
    assert path.read_bytes() == data


@pytest.mark.parametrize(
    "data",
    [
        'name="Other"\n',
        '[application]\nname="Other"\n',
        'name="Example"\n[application]\nname="Other"\n',
        "application=[]\n",
        "name=1\n",
    ],
)
def test_application_marker_names_cannot_conflict_or_mismatch(tmp_path, data):
    app = application(tmp_path)
    (app / "application.toml").write_text(data, encoding="utf-8")
    assert not check_slot_markers(tmp_path, "Example")["consistent"]
    with pytest.raises(ValidationError):
        validate_self_completion_preflight(tmp_path, "Example")


@pytest.mark.parametrize(
    "text",
    [
        "not toml [",
        "applications=[]\n",
        '[applications]\nExample="bad"\n',
        '[applications]\nExample={slot="Other"}\n',
        '[applications]\n"../escape"={slot="../escape"}\n',
        '[applications]\nExample={slot="Example"}\nexample={slot="example"}\n',
    ],
)
def test_malformed_catalog_is_never_treated_as_absent_registration(tmp_path, text):
    write_registry(tmp_path, [])
    path = tmp_path / "applications" / "registry.toml"
    path.write_text(text, encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ApplicationRegistryError):
        has_registry_entry(tmp_path, "Example")
    result = evaluate_isolation_state(tmp_path)
    assert any(v["verdict"] == "Application catalog invalid" for v in result["verdicts"])
    assert path.read_bytes() == before


@pytest.mark.parametrize("name", ["../escape", "nested/name", "nested\\name", "E:escape", ".", "..", ""])
def test_slot_names_cannot_redirect_marker_reads(tmp_path, name):
    with pytest.raises(ApplicationRegistryError):
        application_slot_path(tmp_path, name)
    with pytest.raises(ValidationError):
        validate_self_completion_preflight(tmp_path, name)


def test_catalog_slot_and_directory_paths_are_not_package_inferred(tmp_path):
    write_registry(tmp_path, ["Example"])
    app = application(tmp_path)
    assert application_slot_path(tmp_path, "Example") == app
    assert load_application_catalog(tmp_path) == {"Example": {"slot": "Example"}}
    assert evaluate_isolation_state(tmp_path)["verdicts"] == []


def test_redirected_slot_is_reported_without_reading_foreign_content(tmp_path):
    write_registry(tmp_path, ["Example"])
    outside = tmp_path / "outside"
    outside.mkdir()
    data = outside / "application.toml"
    data.write_bytes(b"invalid private content")
    link = tmp_path / "applications" / "Example"
    if os.name == "nt":
        run = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "New-Item -ItemType Junction -Path $env:GTKB_TEST_LINK -Target $env:GTKB_TEST_TARGET | Out-Null",
            ],
            env=dict(os.environ, GTKB_TEST_LINK=str(link), GTKB_TEST_TARGET=str(outside)),
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        assert run.returncode == 0, run.stderr
    else:
        link.symlink_to(outside, target_is_directory=True)
    result = evaluate_isolation_state(tmp_path)
    assert any(v["verdict"] == "Application slot invalid" for v in result["verdicts"])
    assert "invalid private content" not in json.dumps(result)
    assert data.read_bytes() == b"invalid private content"


@pytest.mark.parametrize("filename", [".gitignore", "metadata.json"])
def test_parent_metadata_files_are_not_application_slots(tmp_path, filename):
    write_registry(tmp_path, ["Example"])
    application(tmp_path)
    path = tmp_path / "applications" / filename
    path.write_bytes(b"parent namespace metadata")
    result = evaluate_isolation_state(tmp_path)
    assert result["verdicts"] == [] and set(result["slots_status"]) == {"Example"}
    assert path.read_bytes() == b"parent namespace metadata"


def test_catalog_entry_pointing_at_file_still_fails(tmp_path):
    write_registry(tmp_path, ["FileSlot"])
    path = tmp_path / "applications" / "FileSlot"
    path.write_bytes(b"existing user content")
    result = evaluate_isolation_state(tmp_path)
    assert any(row["verdict"] == "Application slot invalid" for row in result["verdicts"])
    assert path.read_bytes() == b"existing user content"
