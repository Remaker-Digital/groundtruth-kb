"""Register multiple applications through the selected platform's existing catalog."""

import json
import os
import shutil
import subprocess
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main

ROOT = Path(__file__).resolve().parents[3]


def make_host(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    controls = path / "config/governance/operational-controls.toml"
    controls.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "config/governance/operational-controls.toml", controls)
    (path / "groundtruth.db").write_bytes(b"Do not open or change this legacy sentinel")
    (path / "unrelated.txt").write_bytes(b"Keep these exact unrelated bytes\r\n")
    return path


@pytest.fixture
def host(tmp_path, monkeypatch):
    def no_sqlite(*args, **kwargs):
        pytest.fail("Application registration must not open a local governance database")

    monkeypatch.setattr("sqlite3.connect", no_sqlite)
    return make_host(tmp_path / "host")


def snapshot(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and p.name != "gtkb-sot-registry.lock"
    }


def register(host, name, *, json_output=True):
    args = ["application", "register", name, "--host-root", str(host)]
    if json_output:
        args.append("--json")
    return CliRunner().invoke(main, args)


def test_register_command_success(host):
    before = snapshot(host)
    result = register(host, "foo", json_output=False)
    assert result.exit_code == 0, result.output
    assert "Successfully registered" in result.output
    assert tomllib.loads((host / "applications/registry.toml").read_text())["applications"] == {"foo": {"slot": "foo"}}
    marker = host / "applications/foo/application.toml"
    assert tomllib.loads(marker.read_text())["application"]["name"] == "foo"
    after = snapshot(host)
    assert all(after[path] == data for path, data in before.items())
    assert set(after) - set(before) == {"applications/registry.toml", "applications/foo/application.toml"}


def test_register_mismatched_markers_fails(host):
    app = host / "applications/foo"
    app.mkdir(parents=True)
    (app / ".gtkb-app-isolation.json").write_text('{"application":"Different"}', encoding="utf-8")
    before = snapshot(host)
    result = register(host, "foo")
    assert result.exit_code == 1 and "mismatch" in result.output.lower()
    assert json.loads(result.output)["status"] == "refused"
    assert snapshot(host) == before


def test_register_multiple_applications_preserves_existing_entries(host):
    assert register(host, "foo").exit_code == 0
    catalog = host / "applications/registry.toml"
    catalog.write_text(
        '# Keep this operator comment\n[applications]\nfoo={slot="foo",note="original"}\n\n[metadata]\nlabel="keep"\n',
        encoding="utf-8",
    )
    marker = host / "applications/foo/application.toml"
    before = marker.read_bytes()
    result = register(host, "bar")
    assert result.exit_code == 0, result.output
    payload = tomllib.loads(catalog.read_text())
    assert payload == {
        "applications": {"foo": {"slot": "foo", "note": "original"}, "bar": {"slot": "bar"}},
        "metadata": {"label": "keep"},
    }
    assert catalog.read_text().startswith("# Keep this operator comment\n")
    assert marker.read_bytes() == before
    assert json.loads(result.output)["repository_ref"] == "application:bar"
    before = snapshot(host)
    repeated = register(host, "bar")
    assert repeated.exit_code == 0 and json.loads(repeated.output)["status"] == "already_registered"
    assert json.loads(repeated.output)["changed_paths"] == []
    assert snapshot(host) == before


@pytest.mark.parametrize("name", ["", "../outside", "A/B", "A:B", "application:Alpha", "9starts_wrong"])
def test_invalid_registration_name_refuses_before_application_effects(host, name):
    before = snapshot(host)
    result = register(host, name)
    assert result.exit_code == 1 and json.loads(result.output)["status"] == "refused"
    assert snapshot(host) == before


@pytest.mark.parametrize(
    "payload", ["not valid TOML = [", "[unrelated]\nvalue=1\n", '[applications]\nfoo={slot="other"}\n']
)
def test_invalid_catalog_refuses_without_repairing_or_replacing_it(host, payload):
    catalog = host / "applications/registry.toml"
    catalog.parent.mkdir()
    catalog.write_text(payload, encoding="utf-8")
    before = snapshot(host)
    result = register(host, "bar")
    assert result.exit_code == 1 and json.loads(result.output)["status"] == "refused"
    assert snapshot(host) == before


def test_registration_preserves_custom_existing_marker_and_files(host):
    app = host / "applications/Alpha"
    app.mkdir(parents=True)
    marker = b'# Operator marker\r\n[application]\r\nname="Alpha"\r\n[custom]\r\nvalue="keep"\r\n'
    (app / "application.toml").write_bytes(marker)
    (app / "code.py").write_bytes(b"original_application = True\n")
    before = snapshot(host)
    result = register(host, "Alpha")
    assert result.exit_code == 0, result.output
    after = snapshot(host)
    assert all(after[path] == data for path, data in before.items())
    assert set(after) - set(before) == {"applications/registry.toml"}


def test_registration_rejects_case_alias_without_creating_another_entry(host):
    assert register(host, "Alpha").exit_code == 0
    before = snapshot(host)
    result = register(host, "alpha")
    assert result.exit_code == 1 and "case" in result.output.lower()
    assert snapshot(host) == before


@pytest.mark.parametrize("existing", [False, True])
def test_failed_catalog_publication_removes_only_its_new_marker(host, monkeypatch, existing):
    if existing:
        assert register(host, "Existing").exit_code == 0
    before = snapshot(host)

    def refuse(*args, **kwargs):
        raise OSError("Injected catalog publication failure")

    monkeypatch.setattr("groundtruth_kb.project.registry_control_plane._atomic_replace", refuse)
    result = register(host, "New")
    assert result.exit_code == 1 and "Injected catalog publication failure" in result.output
    assert snapshot(host) == before
    assert not (host / "applications/New").exists()


def test_registration_uses_selected_host_despite_inherited_git_overrides(host, tmp_path, monkeypatch):
    foreign = make_host(tmp_path / "foreign")
    before = snapshot(foreign)
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    result = register(host, "Alpha")
    assert result.exit_code == 0, result.output
    assert snapshot(foreign) == before
    assert not (foreign / ".git/gtkb-sot-registry.lock").exists()
    assert (host / "applications/Alpha/application.toml").is_file()


def test_failed_catalog_publication_preserves_an_existing_marker(host, monkeypatch):
    app = host / "applications/Existing"
    app.mkdir(parents=True)
    (app / "application.toml").write_text('[application]\nname="Existing"\n', encoding="utf-8")
    before = snapshot(host)

    def refuse(*args, **kwargs):
        raise OSError("Injected catalog publication failure")

    monkeypatch.setattr("groundtruth_kb.project.registry_control_plane._atomic_replace", refuse)
    result = register(host, "Existing")
    assert result.exit_code == 1 and "Injected catalog publication failure" in result.output
    assert snapshot(host) == before


def test_post_publication_failure_keeps_consistent_marker_for_retry(host, monkeypatch):
    from groundtruth_kb.project import registry_control_plane

    replace = registry_control_plane._atomic_replace

    def replace_then_fail(path, payload):
        replace(path, payload)
        raise OSError("Injected failure after catalog replacement")

    monkeypatch.setattr(registry_control_plane, "_atomic_replace", replace_then_fail)
    result = register(host, "Alpha")
    assert result.exit_code == 1 and "Injected failure after catalog replacement" in result.output
    catalog = tomllib.loads((host / "applications/registry.toml").read_text())
    assert catalog["applications"] == {"Alpha": {"slot": "Alpha"}}
    assert tomllib.loads((host / "applications/Alpha/application.toml").read_text())["application"]["name"] == "Alpha"
    before = snapshot(host)
    monkeypatch.setattr(registry_control_plane, "_atomic_replace", replace)
    repeated = register(host, "Alpha")
    assert repeated.exit_code == 0 and json.loads(repeated.output)["status"] == "already_registered"
    assert snapshot(host) == before


def test_concurrent_cli_registration_preserves_both_applications(host):
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PG", "GT_POSTGRES_", "GIT_"))}

    def invoke(name):
        return subprocess.run(
            [
                sys.executable,
                "-P",
                "-m",
                "groundtruth_kb",
                "application",
                "register",
                name,
                "--host-root",
                str(host),
                "--json",
            ],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(invoke, ("Alpha", "Beta")))
    assert all(result.returncode == 0 for result in results), [(result.stdout, result.stderr) for result in results]
    entries = tomllib.loads((host / "applications/registry.toml").read_text())["applications"]
    assert entries == {"Alpha": {"slot": "Alpha"}, "Beta": {"slot": "Beta"}}
    for name in entries:
        assert (host / "applications" / name / "application.toml").is_file()
    assert (host / "groundtruth.db").read_bytes() == b"Do not open or change this legacy sentinel"
    assert not any((host / "applications").rglob("groundtruth.db"))


def test_registration_requires_explicit_host_selection(host):
    before = snapshot(host)
    result = CliRunner().invoke(main, ["application", "register", "Alpha"])
    assert result.exit_code == 2 and "--host-root" in result.output
    assert snapshot(host) == before
