"""Installer refusal/publication contracts; real pinned verifier is opt-in below."""

import hashlib
import http.client
import io
import json
import os
import shutil
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb import dashboard
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig


@pytest.fixture
def verifier(tmp_path, monkeypatch):
    paths = dashboard.resolve_dashboard_paths(GTConfig(project_root=tmp_path))
    binary = paths.grafana_home / "bin" / ("grafana.exe" if sys.platform == "win32" else "grafana")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"verifier test double")
    (paths.grafana_home / "conf").mkdir()
    (paths.grafana_home / "conf/defaults.ini").write_text("fixture")
    plugin = paths.grafana_home / "data/plugins" / dashboard.SQLITE_PLUGIN_ID
    plugin.mkdir(parents=True)
    metadata = {"id": dashboard.SQLITE_PLUGIN_ID, "info": {"version": dashboard.SQLITE_PLUGIN_VERSION}}
    (plugin / "plugin.json").write_text(json.dumps(metadata))
    (plugin / "module.js").write_bytes(b"plugin test double")
    observation = paths.grafana_home / "installed.json"
    observation.write_bytes(b"prior installation observation")
    state = {
        "paths": paths,
        "plugin": plugin,
        "binary": binary,
        "observation": observation,
        "settings": {**metadata, "signature": "valid", "signatureType": "community", "signatureOrg": "frser"},
        "health": {"database": "ok", "version": dashboard.GRAFANA_VERSION},
        "spawned": [],
        "stopped": [],
        "exit": None,
        "cleanup": True,
    }

    class Process:
        pid = 123456

        def poll(self):
            return state["exit"]

        def wait(self, timeout):
            assert state["exit"] is not None
            return state["exit"]

    def spawn(args, **kwargs):
        if state.get("spawn_error"):
            raise OSError("start refused")
        state["spawned"].append((args, kwargs))
        return Process()

    def stop(pid, identity):
        state["stopped"].append(pid)
        if state["cleanup"]:
            state["exit"] = 0
            if state.get("change_on_stop"):
                (plugin / "module.js").write_bytes(b"changed after response")
        return state["cleanup"]

    class Opener:
        def open(self, request, timeout):
            assert request.full_url.startswith("http://127.0.0.1:")
            assert 0 < timeout <= 5
            if request.full_url.endswith("/api/health"):
                if state.get("unavailable"):
                    raise OSError("not ready")
                if state.get("self_connected", 0):
                    state["self_connected"] -= 1
                    raise http.client.BadStatusLine("GET /api/health HTTP/1.1")
                body = state["health"]
            else:
                if "http_error" in state:
                    raise urllib.error.HTTPError(request.full_url, state["http_error"], "refused", {}, None)
                if state.get("settings_protocol_error"):
                    raise http.client.BadStatusLine("garbled status line")
                if state.get("change"):
                    (plugin / "module.js").write_bytes(b"changed during verification")
                if state.get("change_binary"):
                    binary.write_bytes(b"changed verifier")
                body = state["settings"]
            return io.BytesIO(json.dumps(body).encode())

    monkeypatch.setattr(dashboard.subprocess, "Popen", spawn)
    monkeypatch.setattr(dashboard, "_process_identity", lambda pid: {"pid": pid})
    monkeypatch.setattr(dashboard, "_terminate_pid", stop)
    monkeypatch.setattr(dashboard.urllib.request, "build_opener", lambda *args: Opener())
    monkeypatch.setattr(dashboard, "_install_sqlite_plugin", lambda home: None)
    yield state
    assert not state["spawned"] or state["exit"] is not None or not state["cleanup"]


def refused(state, message):
    with pytest.raises((ValueError, RuntimeError, OSError), match=message):
        dashboard.install_grafana(state["paths"], skip_download=True, skip_plugin=True)
    assert state["observation"].read_bytes() == b"prior installation observation"


@pytest.mark.parametrize("skip_plugin", [False, True])
def test_success_requires_fresh_signature_and_preserves_original_plugin(verifier, monkeypatch, skip_plugin):
    state = verifier
    before = dashboard._plugin_file_identities(state["plugin"])
    monkeypatch.setenv("GF_DEFAULT_APP_MODE", "development")
    monkeypatch.setenv("GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS", dashboard.SQLITE_PLUGIN_ID)
    monkeypatch.setenv("GT_POSTGRES_PASSWORD", "must-not-inherit")
    assert dashboard.install_grafana(state["paths"], skip_download=True, skip_plugin=skip_plugin) == state["binary"]
    record = json.loads(state["observation"].read_text())
    assert record["plugin_verification"] == "verified"
    assert record["plugin"]["signature"] == {
        "signature": "valid",
        "signatureType": "community",
        "signatureOrg": "frser",
    }
    assert record["plugin"]["verifier_version"] == dashboard.GRAFANA_VERSION
    assert record["plugin"]["verifier_binary_sha256"] == hashlib.sha256(state["binary"].read_bytes()).hexdigest()
    assert record["plugin"]["files_sha256"] == before == dashboard._plugin_file_identities(state["plugin"])
    assert len(state["spawned"]) == 1 and state["stopped"] == [123456]
    args, kwargs = state["spawned"][0]
    assert "development" not in kwargs["env"].values()
    assert "GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS" not in kwargs["env"]
    assert "GT_POSTGRES_PASSWORD" not in kwargs["env"]
    assert kwargs["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)
    assert not list(state["paths"].grafana_home.glob("plugin-verification-*"))
    assert kwargs["env"]["GF_SECURITY_ADMIN_PASSWORD"] not in state["observation"].read_text()


@pytest.mark.parametrize(
    "field,value",
    [
        ("signature", "unsigned"),
        ("signature", "modified"),
        ("signature", "invalid"),
        ("signatureType", "commercial"),
        ("signatureOrg", "different"),
        ("id", "other-plugin"),
        ("info", {"version": "0.0.0"}),
        ("info", None),
    ],
)
def test_verdict_must_match_pinned_identity_and_expected_signature(verifier, field, value):
    verifier["settings"][field] = value
    refused(verifier, "signature_or_identity_mismatch")
    assert verifier["stopped"] == [123456]


@pytest.mark.parametrize("code", [401, 404, 500])
def test_runtime_signature_or_authentication_error_preserves_previous_observation(verifier, code):
    verifier["http_error"] = code
    refused(verifier, f"verification_http_{code}")
    assert verifier["stopped"] == [123456]


@pytest.mark.parametrize(
    "metadata",
    [
        [],
        {"id": "other", "info": {"version": "4.0.6"}},
        {"id": dashboard.SQLITE_PLUGIN_ID, "info": None},
        {"id": dashboard.SQLITE_PLUGIN_ID, "info": {"version": "0.0.0"}},
    ],
)
def test_skipping_download_never_skips_plugin_identity(verifier, metadata):
    (verifier["plugin"] / "plugin.json").write_text(json.dumps(metadata))
    refused(verifier, "identity differs")
    assert verifier["spawned"] == []


@pytest.mark.parametrize("change", ["change", "change_on_stop", "change_binary"])
def test_observation_cannot_describe_changed_bytes(verifier, change):
    verifier[change] = True
    refused(verifier, "changed")


def test_a_self_connected_readiness_probe_is_retried_not_failed(verifier):
    """c112-full-20260924T2040 installed #161: before Grafana binds its port, a loopback connect can land on its own
    ephemeral source port and read its own request line back as the status line. That is "not ready yet"."""
    verifier["self_connected"] = 2
    assert dashboard.install_grafana(verifier["paths"], skip_download=True, skip_plugin=True) == verifier["binary"]
    assert verifier["self_connected"] == 0
    assert json.loads(verifier["observation"].read_text())["plugin_verification"] == "verified"
    assert len(verifier["spawned"]) == 1 and verifier["stopped"] == [123456]


def test_a_malformed_settings_response_is_a_legible_refusal(verifier):
    verifier["settings_protocol_error"] = True
    refused(verifier, "grafana_plugin_verification_unavailable")


def test_verifier_version_must_match_pin(verifier):
    verifier["health"]["version"] = "0.0.0"
    refused(verifier, "version_differs_from_pin")


@pytest.mark.parametrize("failure", ["spawn", "exit", "timeout", "cleanup"])
def test_verifier_failures_do_not_publish_success(verifier, failure, monkeypatch):
    if failure == "spawn":
        verifier["spawn_error"] = True
    elif failure == "exit":
        verifier["exit"] = 1
    elif failure == "timeout":
        verifier["unavailable"] = True
        original = dashboard._verify_sqlite_plugin
        monkeypatch.setattr(dashboard, "_verify_sqlite_plugin", lambda *a: original(*a, timeout=0.001))
    else:
        verifier["cleanup"] = False
    refused(
        verifier,
        {
            "spawn": "start refused",
            "exit": "exited_before",
            "timeout": "readiness_timeout",
            "cleanup": "cleanup_unconfirmed: pid=123456",
        }[failure],
    )
    remnants = list(verifier["paths"].grafana_home.glob("plugin-verification-*"))
    assert bool(remnants) is (failure == "cleanup")


def test_absent_plugin_is_explicitly_unverified_when_fetching_is_skipped(verifier):
    plugin = verifier["plugin"].resolve()
    assert plugin.is_relative_to(verifier["paths"].project_root)
    shutil.rmtree(plugin)
    dashboard.install_grafana(verifier["paths"], skip_download=True, skip_plugin=True)
    record = json.loads(verifier["observation"].read_text())
    assert record["plugin"] is None and record["plugin_verification"] == "absent_unverified"
    assert verifier["spawned"] == []


@pytest.mark.parametrize("absent", [False, True])
def test_cli_install_reports_installation_without_claiming_dashboard_readiness(verifier, absent):
    paths = verifier["paths"]
    if absent:
        assert verifier["plugin"].resolve().is_relative_to(paths.project_root)
        shutil.rmtree(verifier["plugin"])
    config = paths.project_root / "groundtruth.toml"
    config.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    result = CliRunner().invoke(
        main, ["--config", str(config), "dashboard", "install", "--skip-download", "--skip-plugin", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "Grafana installed"
    record = json.loads(verifier["observation"].read_text())
    assert record["plugin_verification"] == ("absent_unverified" if absent else "verified")


@pytest.mark.parametrize("corruption", ["intact", "modified", "missing", "invalid"])
def test_real_pinned_verifier_through_installer(tmp_path, monkeypatch, corruption):
    """Opt-in local release fixture; never install into or start production."""
    supplied = os.environ.get("GTKB_TEST_GRAFANA_HOME")
    if not supplied:
        pytest.skip("Set GTKB_TEST_GRAFANA_HOME to the qualified disposable pinned distribution")
    home = Path(supplied).resolve(strict=True)
    source = home / "data/plugins" / dashboard.SQLITE_PLUGIN_ID
    original = dashboard._plugin_file_identities(source)
    binary = dashboard.find_grafana_server(home)
    assert binary is not None
    paths = dashboard.resolve_dashboard_paths(GTConfig(project_root=tmp_path))
    plugin = paths.grafana_home / "data/plugins" / dashboard.SQLITE_PLUGIN_ID
    shutil.copytree(source, plugin)
    if corruption == "modified":
        with (plugin / "module.js").open("ab") as stream:
            stream.write(b"\n// deliberately modified qualification copy\n")
    elif corruption == "missing":
        (plugin / "MANIFEST.txt").unlink()
    elif corruption == "invalid":
        manifest = plugin / "MANIFEST.txt"
        body = manifest.read_text(encoding="utf-8")
        assert '"signedByOrgName": "frser"' in body
        manifest.write_text(
            body.replace('"signedByOrgName": "frser"', '"signedByOrgName": "fixture"', 1), encoding="utf-8"
        )
    before = dashboard._plugin_file_identities(plugin)
    # Reuse only the immutable distribution; data and plugin copies are disposable.
    monkeypatch.setattr(dashboard, "find_grafana_server", lambda selected: binary)
    monkeypatch.setenv("GF_DEFAULT_APP_MODE", "development")
    monkeypatch.setenv("GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS", dashboard.SQLITE_PLUGIN_ID)
    observation = paths.grafana_home / "installed.json"
    observation.write_bytes(b"prior observation")
    if corruption == "intact":
        dashboard.install_grafana(paths, skip_download=True, skip_plugin=True)
        record = json.loads(observation.read_text())
        assert record["plugin_verification"] == "verified"
        assert record["plugin"]["signature"]["signature"] == "valid"
    else:
        with pytest.raises(ValueError, match="verification_http_500"):
            dashboard.install_grafana(paths, skip_download=True, skip_plugin=True)
        assert observation.read_bytes() == b"prior observation"
    assert dashboard._plugin_file_identities(source) == original
    assert dashboard._plugin_file_identities(plugin) == before
    assert not list(home.glob("plugin-verification-*"))
