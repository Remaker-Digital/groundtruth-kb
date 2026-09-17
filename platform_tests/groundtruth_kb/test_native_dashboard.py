"""Installed dashboard routes observe PostgreSQL without opening retired authority files."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys

import pytest
from click.testing import CliRunner
from groundtruth_kb import dashboard
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig

from platform_tests.groundtruth_kb.test_native_authority_service import (
    history_count,
    put,
    seed,
    work_fields,
)
from platform_tests.groundtruth_kb.test_native_authority_service import (
    native as _native_fixture,
)

native = _native_fixture


@pytest.mark.parametrize("command", ["init", "refresh"])
def test_native_dashboard_cli_reads_selected_authority_without_sqlite_fallback(native, monkeypatch, tmp_path, command):
    service, client, *_ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    config_path = tmp_path / "chosen.toml"
    config_path.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    poison = tmp_path / "groundtruth.db"
    poison.write_bytes(b"Retired authority bytes must not be opened or changed")
    before = history_count(service)
    requests = []

    def read(self, method, path, *, query=None):
        assert method == "GET"
        requests.append(path)
        response = client.get(path, params={k: v for k, v in (query or {}).items() if v is not None})
        assert response.status_code == 200, response.text
        return response.json()

    monkeypatch.setattr(AuthorityClient, "request", read)
    result = CliRunner().invoke(main, ["--config", str(config_path), "dashboard", command, "--json"])
    assert result.exit_code == 0, result.output
    reply = json.loads(result.output)
    runtime = tmp_path / ".groundtruth/dashboard"
    assert reply["runtime_root"] == str(runtime)
    with sqlite3.connect(runtime / "gtkb-dashboard.sqlite") as conn:
        metrics = dict(conn.execute("SELECT metric_key,value FROM kpi_snapshots"))
    assert metrics["backlog_active_items"] == 1
    assert metrics["specification_current_total"] == 1
    assert metrics["contention_actionable_bridge_count"] == 0
    assert metrics["tokens_consumed_before_user_input"] is None
    landing = json.loads((runtime / "dashboard-data.json").read_text())
    assert landing["metrics"] == metrics
    assert (runtime / "index.html").is_file()
    assert json.loads((runtime / "bridge-swimlane.json").read_text())["status"] == "observed"
    generated = json.loads((runtime / "grafana/dashboards/gtkb-dashboard.json").read_text())
    assert generated["uid"] == dashboard.GRAFANA_DASHBOARD_UID
    assert (runtime / "grafana/provisioning/alerting/contact-points.yaml").is_file()
    assert set(requests) == {"/v1/work-items", "/v1/specifications", "/v1/tests", "/v1/bridge/state-report"}
    assert history_count(service) == before
    assert poison.read_bytes() == b"Retired authority bytes must not be opened or changed"
    assert not (tmp_path / "memory").exists()


@pytest.mark.parametrize("entry", ["refresh", "schema-only", "direct-no-config"])
def test_native_dashboard_refuses_source_database_as_output_before_effects(tmp_path, entry):
    source = tmp_path / "groundtruth.db"
    source.write_bytes(b"Do not overwrite")
    config = GTConfig(project_root=tmp_path, db_path=source)
    paths = dashboard.resolve_dashboard_paths(config, db_path=source)
    with pytest.raises(ValueError, match="dashboard_db_must_be_derived"):
        if entry == "direct-no-config":
            dashboard.refresh_database(source, tmp_path)
        else:
            dashboard.initialize_dashboard(paths, config, schema_only=entry == "schema-only")
    assert source.read_bytes() == b"Do not overwrite"
    assert not (tmp_path / ".groundtruth").exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process handle and venv process-tree behavior")
def test_dashboard_stop_checks_creation_identity_and_stops_only_its_recorded_process_tree(tmp_path):
    process = subprocess.Popen(
        [sys.executable, "-c", "import os,time; print(os.getpid(),flush=True); time.sleep(120)"],
        stdout=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        worker_pid = int(process.stdout.readline())
        paths = dashboard.resolve_dashboard_paths(GTConfig(project_root=tmp_path))
        record_path = paths.pids_dir / "refresh-service.pid"
        dashboard._write_pid(record_path, process.pid)
        record = json.loads(record_path.read_text())
        assert record["pid"] == process.pid and record["created_at"] and record["executable"]
        assert dashboard._read_live_pid(record_path) == process.pid
        # Reusing the number with a different creation identity must never signal it.
        record["created_at"] += "0"
        record_path.write_text(json.dumps(record))
        assert dashboard.stop_dashboard(paths) == []
        assert process.poll() is None and dashboard._pid_alive(worker_pid)
        assert not record_path.exists()
        dashboard._write_pid(record_path, process.pid)
        assert dashboard.stop_dashboard(paths) == [process.pid]
        process.wait(timeout=10)
        assert not dashboard._pid_alive(worker_pid)
        assert not record_path.exists()
    finally:
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            process.wait(timeout=10)
        process.stdout.close()


def test_dashboard_legacy_pid_only_record_cannot_authorize_stopping(tmp_path):
    paths = dashboard.resolve_dashboard_paths(GTConfig(project_root=tmp_path))
    record_path = paths.pids_dir / "refresh-service.pid"
    record_path.parent.mkdir(parents=True)
    record_path.write_text(str(os.getpid()))
    with pytest.raises(ValueError, match="requires inspection"):
        dashboard.stop_dashboard(paths)
    assert record_path.read_text() == str(os.getpid())


def _free_port():
    import socket

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _http(url, payload=None, token=None):
    import urllib.error
    import urllib.request

    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["X-Refresh-Token"] = token
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode() if payload is not None else None, headers=headers
    )
    try:
        response = urllib.request.urlopen(request, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw) if "application/json" in response.headers.get(
            "Content-Type", ""
        ) else raw


@pytest.fixture
def dashboard_authority(native, tmp_path, monkeypatch):
    import time

    service, client, *_ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    port = _free_port()
    server_config = tmp_path / "authority.toml"
    server_config.write_text(
        '[groundtruth]\n[postgresql]\nservice="' + os.environ["GTKB_TEST_POSTGRES_SERVICE"] + '"\n'
    )
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    monkeypatch.delenv("GT_PROJECT_ROOT", raising=False)
    with (tmp_path / "authority.log").open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(server_config),
                "service",
                "serve",
                "--port",
                str(port),
            ],
            cwd=tmp_path,
            stdout=log,
            stderr=log,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    identity = dashboard._process_identity(process.pid)
    try:
        deadline = time.monotonic() + 20
        while True:
            try:
                assert _http(f"http://127.0.0.1:{port}/v1/status")[0] == 200
                break
            except OSError:
                assert time.monotonic() < deadline and process.poll() is None
                time.sleep(0.1)
        chosen = tmp_path / "selected-config.toml"
        chosen.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:' + str(port) + '"\n', encoding="utf-8")
        poison = tmp_path / "groundtruth.db"
        poison.write_bytes(b"Retired authority - do not open")
        before = history_count(service)
        yield chosen
        assert history_count(service) == before
        assert poison.read_bytes() == b"Retired authority - do not open"
    finally:
        if process.poll() is None:
            assert dashboard._terminate_pid(process.pid, identity)
        process.wait(timeout=10)


@pytest.mark.timeout(90)
def test_installed_serve_process_publishes_native_data_and_enforces_http_boundaries(dashboard_authority, tmp_path):
    config_path = dashboard_authority
    port = _free_port()
    runtime = tmp_path / "display"
    env = dict(os.environ, GTKB_DASHBOARD_REFRESH_TOKEN="test-only-refresh-token")
    with (tmp_path / "display.log").open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(config_path),
                "dashboard",
                "serve",
                "--runtime-root",
                str(runtime),
                "--port",
                str(port),
                "--grafana-port",
                "39123",
            ],
            cwd=tmp_path,
            env=env,
            stdout=log,
            stderr=log,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    identity = dashboard._process_identity(process.pid)
    try:
        base = f"http://127.0.0.1:{port}"
        dashboard._wait_dashboard_http(process.pid, base + "/health", {"runtime_root": str(runtime)}, timeout=45)
        assert _http(base + "/health")[1]["config_path"] == str(config_path)
        assert _http(base + "/dashboard-data.json")[1]["metrics"]["backlog_active_items"] == 1
        assert _http(base + "/bridge-swimlane.json")[1]["status"] == "observed"
        assert "127.0.0.1:39123/d/groundtruth-kb-dashboard" in _http(base + "/")[1]
        assert _http(base + "/control")[0] == 200
        assert _http(base + "/groundtruth.db")[0] == 404
        assert _http(base + "/../selected-config.toml")[0] == 404
        with sqlite3.connect(runtime / "gtkb-dashboard.sqlite") as conn:
            before = conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0]
        assert _http(base + "/control_plane", {"operation_id": "dashboard.refresh"})[0] == 401
        assert _http(base + "/control_plane", {"operation_id": "dashboard.refresh", "dry_run": True})[0] == 200
        assert _http(base + "/control_plane", {"operation_id": "dashboard.read", "db_path": "foreign"})[0] == 400
        assert _http(base + "/control_plane", {"operation_id": "arbitrary.command"})[0] == 404
        with sqlite3.connect(runtime / "gtkb-dashboard.sqlite") as conn:
            assert conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0] == before
        assert _http(base + "/refresh", {}, "test-only-refresh-token")[0] == 200
        with sqlite3.connect(runtime / "gtkb-dashboard.sqlite") as conn:
            assert conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0] == before + 1
        # A manual refresh preserves the selected-port links.
        assert "127.0.0.1:39123/d/groundtruth-kb-dashboard" in _http(base + "/")[1]
    finally:
        if process.poll() is None:
            assert dashboard._terminate_pid(process.pid, identity)
        process.wait(timeout=10)


@pytest.mark.timeout(90)
@pytest.mark.parametrize("grafana_fails", [False, True])
def test_launcher_reuses_ready_children_and_cleans_only_new_launches_on_failure(
    dashboard_authority, tmp_path, monkeypatch, grafana_fails
):
    config_path = dashboard_authority
    config = GTConfig.load(config_path)
    paths = dashboard.resolve_dashboard_paths(config)
    binary = paths.grafana_home / "bin" / ("grafana.exe" if sys.platform == "win32" else "grafana")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"Test-double launch placeholder")
    (paths.grafana_home / "conf").mkdir()
    (paths.grafana_home / "conf/defaults.ini").write_text("Test-double home")
    original_popen = subprocess.Popen
    launches = []
    fake_server = """import os
assert os.path.isdir(os.environ["GF_PATHS_DATA"])
from http.server import HTTPServer,BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200); self.end_headers(); self.wfile.write(b'{"database":"ok"}')
HTTPServer(('127.0.0.1',int(os.environ['GF_SERVER_HTTP_PORT'])), Handler).serve_forever()
"""

    def spawn(args, **kwargs):
        if args[0] == "taskkill":
            return original_popen(args, **kwargs)
        if args[0] == str(binary):
            args = [sys.executable, "-c", "raise SystemExit(1)" if grafana_fails else fake_server]
        process = original_popen(args, **kwargs)
        launches.append((process, dashboard._process_identity(process.pid)))
        return process

    monkeypatch.setattr(dashboard.subprocess, "Popen", spawn)
    ports = {"grafana_port": _free_port(), "refresh_port": _free_port()}
    try:
        if grafana_fails:
            with pytest.raises(RuntimeError, match="exited"):
                dashboard.start_dashboard(paths, config, config_path=config_path, **ports)
            assert len(launches) == 2
            assert all(process.poll() is not None for process, _ in launches)
            assert list(paths.pids_dir.iterdir()) == []
        else:
            first = dashboard.start_dashboard(paths, config, config_path=config_path, **ports)
            second = dashboard.start_dashboard(paths, config, config_path=config_path, **ports)
            assert first == second and len(launches) == 2
            with pytest.raises(RuntimeError, match="does not match"):
                dashboard.start_dashboard(paths, config, config_path=config_path, interval_minutes=2, **ports)
            assert all(process.poll() is None for process, _ in launches)
            assert set(dashboard.stop_dashboard(paths)) == {first.refresh_pid, first.grafana_pid}
            assert dashboard.stop_dashboard(paths) == []
    finally:
        for process, identity in launches:
            if process.poll() is None:
                assert dashboard._terminate_pid(process.pid, identity)
            process.wait(timeout=10)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows archive extraction beyond MAX_PATH")
@pytest.mark.parametrize("corrupt_checksum", [False, True])
def test_grafana_download_verifies_archive_and_extracts_long_windows_paths(tmp_path, monkeypatch, corrupt_checksum):
    import hashlib
    import io
    import shutil
    import tarfile
    from pathlib import Path

    buffer = io.BytesIO()
    long_name = "grafana-13.2.1/docs/" + "/".join(["long-documentation-path"] * 9) + "/file.md"
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        directory = tarfile.TarInfo("grafana-13.2.1/docs/nested")
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        for name in ["grafana-13.2.1/bin/grafana.exe", "grafana-13.2.1/conf/defaults.ini", long_name]:
            entry = tarfile.TarInfo(name)
            content = b"fixture"
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))
    data = buffer.getvalue()
    monkeypatch.setattr(dashboard.urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(data))
    monkeypatch.setattr(
        dashboard, "GRAFANA_ARCHIVE_SHA256", "0" * 64 if corrupt_checksum else hashlib.sha256(data).hexdigest()
    )
    target = tmp_path / "installation"
    if corrupt_checksum:
        with pytest.raises(ValueError, match="checksum"):
            dashboard._download_grafana_windows(target)
        assert not target.exists()
    else:
        dashboard._download_grafana_windows(target)
        assert dashboard.find_grafana_server(target) == target / "bin/grafana.exe"
        extended = Path("\\\\?\\" + str(target.resolve()))
        try:
            assert (extended / long_name.split("/", 1)[1]).read_bytes() == b"fixture"
            with pytest.raises(ValueError, match="not empty"):
                dashboard._download_grafana_windows(target)
        finally:
            assert target.resolve().is_relative_to(tmp_path.resolve())
            shutil.rmtree(extended)
    assert list(tmp_path.glob("grafana-install-*")) == []


@pytest.mark.parametrize("wrong_version", [False, True])
def test_grafana_install_pins_plugin_and_records_observed_identity(tmp_path, monkeypatch, wrong_version):
    import hashlib

    paths = dashboard.resolve_dashboard_paths(GTConfig(project_root=tmp_path))
    binary = paths.grafana_home / "bin" / ("grafana.exe" if sys.platform == "win32" else "grafana")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"Existing installation binary")
    (paths.grafana_home / "conf").mkdir()
    (paths.grafana_home / "conf/defaults.ini").write_text("fixture")
    calls = []

    def install(command, **kwargs):
        calls.append(command)
        plugin = paths.grafana_home / "data/plugins" / dashboard.SQLITE_PLUGIN_ID
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text(
            json.dumps(
                {
                    "id": dashboard.SQLITE_PLUGIN_ID,
                    "info": {"version": "0.0.0" if wrong_version else dashboard.SQLITE_PLUGIN_VERSION},
                }
            )
        )
        (plugin / "backend.exe").write_bytes(b"Test plugin binary")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(dashboard.subprocess, "run", install)

    # This case isolates the downloader contract; signature behavior has its own
    # runtime/refusal tests in test_grafana_plugin_verification.py.
    def verified(server, plugin):
        return {
            "id": dashboard.SQLITE_PLUGIN_ID,
            "version": dashboard.SQLITE_PLUGIN_VERSION,
            "files_sha256": dashboard._plugin_file_identities(plugin),
            "signature": {"signature": "valid", "signatureType": "community", "signatureOrg": "frser"},
        }

    monkeypatch.setattr(dashboard, "_verify_sqlite_plugin", verified)
    if wrong_version:
        with pytest.raises(ValueError, match="identity differs"):
            dashboard.install_grafana(paths, skip_download=True)
        assert not (paths.grafana_home / "installed.json").exists()
    else:
        assert dashboard.install_grafana(paths, skip_download=True) == binary
        observation = json.loads((paths.grafana_home / "installed.json").read_text())
        assert observation["archive"] is None and observation["archive_verified_by_this_install"] is False
        assert observation["grafana_binary_sha256"] == hashlib.sha256(binary.read_bytes()).hexdigest()
        assert observation["plugin"]["version"] == dashboard.SQLITE_PLUGIN_VERSION
        assert observation["plugin"]["files_sha256"]["backend.exe"] == hashlib.sha256(b"Test plugin binary").hexdigest()
    assert calls[0][-4:] == ["plugins", "install", dashboard.SQLITE_PLUGIN_ID, dashboard.SQLITE_PLUGIN_VERSION]


@pytest.mark.parametrize("probe_live", [False, True])
def test_dashboard_cli_optional_probes_use_selected_config_for_every_native_read(
    native, tmp_path, monkeypatch, probe_live
):
    service, client, *_ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    selected = tmp_path / "chosen.toml"
    selected.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    conventional = tmp_path / "groundtruth.toml"
    conventional.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39898"\n', encoding="utf-8")
    workflow = tmp_path / ".github/workflows/ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: fixture\n", encoding="utf-8")
    requests, probes = [], []
    before = history_count(service)
    environment = dict(os.environ)

    def read(self, method, route, *, query=None):
        assert self.url == "http://127.0.0.1:39899", "Every native read must use the selected configuration"
        assert method == "GET"
        requests.append(route)
        response = client.get(route, params={k: v for k, v in (query or {}).items() if v is not None})
        assert response.status_code == 200, response.text
        return response.json()

    def probe(root, args, **kwargs):
        assert root == tmp_path and args[0] in ("git", "gh")
        probes.append(args)
        if args[0] == "gh":
            assert probe_live
            return subprocess.CompletedProcess(
                args, 0, json.dumps([{"status": "completed", "conclusion": "success", "workflowName": "Fixture"}]), ""
            )
        return subprocess.CompletedProcess(args, 1, "", "not a repository")

    monkeypatch.setattr(AuthorityClient, "request", read)
    monkeypatch.setattr(dashboard, "_run_release_probe", probe)
    args = ["--config", str(selected), "dashboard", "refresh", "--json"]
    if probe_live:
        args.append("--probe-live")
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "completed"
    with sqlite3.connect(tmp_path / ".groundtruth/dashboard/gtkb-dashboard.sqlite") as conn:
        metrics = dict(conn.execute("SELECT metric_key,value FROM current_metrics"))
        integrations = dict(conn.execute("SELECT key,status FROM integration_status"))
        assert metrics["native_authority_findings"] == (0 if probe_live else None)
        assert integrations.get("native_authority") == ("ready" if probe_live else None)
        assert integrations.get("github") == ("passing" if probe_live else None)
    assert ("/v1/status" in requests) is probe_live
    assert any(args[0] == "gh" for args in probes) is probe_live
    assert history_count(service) == before
    assert dict(os.environ) == environment


@pytest.mark.parametrize("explicit_db", [False, True])
def test_dashboard_schema_only_cli_never_reads_refreshes_or_publishes(tmp_path, monkeypatch, explicit_db):
    selected = tmp_path / "chosen.toml"
    selected.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    source = tmp_path / "groundtruth.db"
    source.write_bytes(b"Protected retired authority bytes")
    output = tmp_path / ("derived.sqlite" if explicit_db else ".groundtruth/dashboard/gtkb-dashboard.sqlite")

    def forbidden(*args, **kwargs):
        pytest.fail("Schema-only initialization must not read authority, probe or spawn")

    monkeypatch.setattr(AuthorityClient, "request", forbidden)
    monkeypatch.setattr(dashboard, "_run_release_probe", forbidden)
    monkeypatch.setattr(dashboard.subprocess, "Popen", forbidden)
    args = ["--config", str(selected), "dashboard", "init", "--schema-only", "--json"]
    if explicit_db:
        args += ["--db-path", str(output)]
    for iteration in range(2):
        result = CliRunner().invoke(main, args)
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["status"] == "initialized" and payload["refreshed"] is False
        assert "landing_page" not in payload and "grafana_dashboard" not in payload
        assert payload["dashboard_db"] == str(output)
        with sqlite3.connect(output) as conn:
            assert conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0] == 0
            if not iteration:
                conn.execute("INSERT INTO dashboard_metadata(key,value) VALUES ('fixture','preserve')")
            else:
                assert (
                    conn.execute("SELECT value FROM dashboard_metadata WHERE key='fixture'").fetchone()[0] == "preserve"
                )
    files = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()}
    assert files == {"chosen.toml", "groundtruth.db", output.relative_to(tmp_path).as_posix()}
    assert source.read_bytes() == b"Protected retired authority bytes"


def test_dashboard_mismatched_config_root_is_refused_before_effects(tmp_path):
    selected_root = tmp_path / "selected"
    other_root = tmp_path / "other"
    config = GTConfig(project_root=selected_root, authority_url="http://127.0.0.1:39899")
    with pytest.raises(ValueError, match="dashboard_config_root_mismatch"):
        dashboard.refresh_database(project_root=other_root, config=config)
    assert not selected_root.exists() and not other_root.exists()


@pytest.mark.parametrize("host", ["0.0.0.0", "192.0.2.20", "::1", "localhost", "127.0.0.1.example", "", "127.0.0.1/8"])
def test_refresh_service_rejects_unsupported_bind_before_state_or_socket_effects(tmp_path, monkeypatch, host):
    from groundtruth_kb import dashboard_service

    def unexpected(*args, **kwargs):
        pytest.fail("Invalid bind address reached refresh state or socket construction")

    monkeypatch.setattr(dashboard_service, "RefreshState", unexpected)
    monkeypatch.setattr(dashboard_service, "ThreadingHTTPServer", unexpected)
    with pytest.raises(ValueError, match="dashboard_host_must_be_ipv4_loopback"):
        dashboard_service.run_service(
            GTConfig(project_root=tmp_path), tmp_path / "display.sqlite", tmp_path / "display", host
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("host", ["0.0.0.0", "192.0.2.20", "::1", "localhost"])
def test_direct_refresh_entrypoint_rejects_bind_before_configuration_or_files(tmp_path, host):
    run = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "groundtruth_kb.dashboard_service",
            "--host",
            host,
            "--config",
            str(tmp_path / "absent.toml"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert run.returncode == 2, run.stdout + run.stderr
    assert "dashboard_host_must_be_ipv4_loopback" in run.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("host", ["127.0.0.1", "127.0.0.2"])
def test_refresh_bind_accepts_numeric_ipv4_loopback(host):
    from groundtruth_kb.dashboard_service import _loopback_host

    assert _loopback_host(host) == host


@pytest.mark.timeout(90)
@pytest.mark.parametrize("explicit_host", [False, True])
def test_direct_refresh_process_ignores_environment_bind_and_serves_loopback(
    dashboard_authority, tmp_path, explicit_host
):
    config_path = dashboard_authority
    port = _free_port()
    runtime = tmp_path / "direct-display"
    env = dict(os.environ, GTKB_DASHBOARD_REFRESH_HOST="192.0.2.42")
    args = [
        sys.executable,
        "-P",
        "-m",
        "groundtruth_kb.dashboard_service",
        "--config",
        str(config_path),
        "--project-root",
        str(tmp_path),
        "--runtime-root",
        str(runtime),
        "--port",
        str(port),
        "--grafana-port",
        "39123",
    ]
    if explicit_host:
        args.extend(["--host", "127.0.0.1"])
    log_path = tmp_path / "direct-display.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen(
            args,
            cwd=tmp_path,
            env=env,
            stdout=log,
            stderr=log,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    identity = dashboard._process_identity(process.pid)
    try:
        base = f"http://127.0.0.1:{port}"
        dashboard._wait_dashboard_http(process.pid, base + "/health", {"runtime_root": str(runtime)}, timeout=45)
        assert _http(base + "/health")[1]["config_path"] == str(config_path)
        assert _http(base + "/dashboard-data.json")[1]["metrics"]["backlog_active_items"] == 1
        assert _http(base + "/groundtruth.db")[0] == 404
        assert f"listening on http://127.0.0.1:{port}/" in log_path.read_text(encoding="utf-8")
        assert "192.0.2.42" not in log_path.read_text(encoding="utf-8")
    finally:
        if process.poll() is None:
            assert dashboard._terminate_pid(process.pid, identity)
        process.wait(timeout=10)


@pytest.mark.timeout(90)
def test_dashboard_children_use_http_authority_without_inherited_database_environment(
    dashboard_authority, tmp_path, monkeypatch
):
    config_path = dashboard_authority
    paths = dashboard.resolve_dashboard_paths(GTConfig.load(config_path))
    binary = paths.grafana_home / "bin" / ("grafana.exe" if sys.platform == "win32" else "grafana")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"Test-double launch placeholder")
    (paths.grafana_home / "conf").mkdir()
    (paths.grafana_home / "conf/defaults.ini").write_text("Test-double home")
    poison = tmp_path / "not-a-service-file.conf"
    poison.write_bytes(b"must remain unread and unchanged")
    inherited = {
        "PGHOST": "192.0.2.22",
        "PGPORT": "1",
        "PGDATABASE": "foreign",
        "PGPASSWORD": "test-only-not-a-real-credential",
        "PGSERVICE": "foreign",
        "PGSERVICEFILE": str(poison),
        "PGPASSFILE": str(poison),
        "GT_POSTGRES_SERVICE": "foreign",
        "GT_POSTGRES_CONNECT_TIMEOUT_SECONDS": "5",
    }
    original_environment = dict(os.environ)
    original_popen = subprocess.Popen
    launches = []
    fake_server = """import os
assert not any(k.upper().startswith(('PG','GT_POSTGRES_')) for k in os.environ)
assert os.environ['GTKB_CHILD_TEST_SENTINEL']=='preserved'
assert os.path.isdir(os.environ['GF_PATHS_DATA'])
from http.server import HTTPServer,BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200); self.end_headers(); self.wfile.write(b'{"database":"ok"}')
HTTPServer(('127.0.0.1',int(os.environ['GF_SERVER_HTTP_PORT'])),Handler).serve_forever()
"""

    def spawn(args, **kwargs):
        if args[0] == "taskkill":
            return original_popen(args, **kwargs)
        child = kwargs["env"]
        leaked_keys = [key for key in child if key.upper().startswith(("PG", "GT_POSTGRES_"))]
        assert not leaked_keys
        assert child["GTKB_CHILD_TEST_SENTINEL"] == "preserved"
        assert child["GTKB_DASHBOARD_REFRESH_TOKEN"] == "test-only-n11-token"
        assert child["PATH"] == original_environment["PATH"]
        if args[0] == str(binary):
            args = [sys.executable, "-P", "-c", fake_server]
        process = original_popen(args, **kwargs)
        launches.append((process, dashboard._process_identity(process.pid)))
        return process

    ports = {"grafana_port": _free_port(), "refresh_port": _free_port()}
    with monkeypatch.context() as selected:
        for key, value in inherited.items():
            selected.setenv(key, value)
        selected.setenv("GTKB_CHILD_TEST_SENTINEL", "preserved")
        selected.setenv("GTKB_DASHBOARD_REFRESH_TOKEN", "test-only-n11-token")
        selected.setattr(dashboard.subprocess, "Popen", spawn)
        try:
            config = GTConfig.load(config_path)
            started = dashboard.start_dashboard(paths, config, config_path=config_path, **ports)
            assert len(launches) == 2
            base = f"http://127.0.0.1:{ports['refresh_port']}"
            assert _http(base + "/dashboard-data.json")[1]["metrics"]["backlog_active_items"] == 1
            assert _http(base + "/refresh", {}, "test-only-n11-token")[0] == 200
            assert set(dashboard.stop_dashboard(paths)) == {started.refresh_pid, started.grafana_pid}
            assert all(os.environ[key] == value for key, value in inherited.items())
        finally:
            for process, identity in launches:
                if process.poll() is None:
                    assert dashboard._terminate_pid(process.pid, identity)
                process.wait(timeout=10)
    changed_keys = [
        key
        for key in set(os.environ) | set(original_environment)
        if os.environ.get(key) != original_environment.get(key)
    ]
    assert not changed_keys
    assert poison.read_bytes() == b"must remain unread and unchanged"


def test_refresh_scheduler_logs_both_failures_and_continues(caplog, capsys):
    import logging
    from types import SimpleNamespace

    from groundtruth_kb import dashboard_service

    triggers, intervals = [], []

    def refresh(trigger):
        triggers.append(trigger)
        raise RuntimeError("fixture-" + trigger)

    def wait(interval):
        intervals.append(interval)
        return len(intervals) == 2

    with caplog.at_level(logging.ERROR, logger="groundtruth_kb.dashboard_service"):
        dashboard_service._run_scheduler(
            SimpleNamespace(refresh_now=refresh, interval_seconds=60), SimpleNamespace(wait=wait)
        )
    records = [r for r in caplog.records if r.name == "groundtruth_kb.dashboard_service"]
    assert [r.getMessage() for r in records] == [
        "Startup dashboard refresh failed: fixture-startup",
        "Scheduled dashboard refresh failed: fixture-scheduled",
    ]
    assert all(r.levelno == logging.ERROR for r in records)
    assert triggers == ["startup", "scheduled"] and intervals == [60, 60]
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""


@pytest.mark.parametrize("preconfigured", [False, True])
@pytest.mark.timeout(90)
def test_actual_refresh_service_logs_readiness_and_access_to_stderr(dashboard_authority, tmp_path, preconfigured):
    port = _free_port()
    runtime = tmp_path / "logging-display"
    arguments = [
        "--config",
        str(dashboard_authority),
        "--project-root",
        str(tmp_path),
        "--runtime-root",
        str(runtime),
        "--port",
        str(port),
        "--grafana-port",
        "39123",
    ]
    if preconfigured:
        command = [
            sys.executable,
            "-P",
            "-c",
            'import logging; logging.basicConfig(level=logging.INFO, format="OWNER:%(message)s"); from groundtruth_kb.dashboard_service import main; raise SystemExit(main())',
            *arguments,
        ]
    else:
        command = [sys.executable, "-P", "-m", "groundtruth_kb.dashboard_service", *arguments]
    stdout_path, stderr_path = tmp_path / "display.stdout", tmp_path / "display.stderr"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=tmp_path,
            env=dict(os.environ),
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    identity = dashboard._process_identity(process.pid)
    try:
        base = f"http://127.0.0.1:{port}"
        dashboard._wait_dashboard_http(process.pid, base + "/health", {"runtime_root": str(runtime)}, timeout=45)
        assert _http(base + "/dashboard-data.json")[1]["metrics"]["backlog_active_items"] == 1
        assert _http(base + "/groundtruth.db")[0] == 404
        logs = stderr_path.read_text(encoding="utf-8")
        assert f"listening on http://127.0.0.1:{port}/" in logs
        assert "GET /health HTTP/1.1" in logs
        if preconfigured:
            assert "OWNER:GT-KB dashboard service listening" in logs
        assert stdout_path.read_bytes() == b""
    finally:
        if process.poll() is None:
            assert dashboard._terminate_pid(process.pid, identity)
        process.wait(timeout=10)
