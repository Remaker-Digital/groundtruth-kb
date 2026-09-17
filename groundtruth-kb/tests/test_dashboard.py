"""Package dashboard routes and process records use native observations and exact launches."""

from __future__ import annotations

import json
import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from platform_tests.groundtruth_kb.test_native_authority_service import (
    history_count,
    put,
    seed,
    work_fields,
)
from platform_tests.groundtruth_kb.test_native_authority_service import (
    native as _native_fixture,
)

from groundtruth_kb import dashboard
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig

native = _native_fixture


@pytest.fixture
def selected_authority(native, tmp_path, monkeypatch):
    service, client, *_ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    config = tmp_path / "chosen.toml"
    config.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    poison = tmp_path / "groundtruth.db"
    poison.write_bytes(b"Retired authority; never open")

    def read(self, method, path, *, query=None):
        assert method == "GET"
        result = client.get(path, params={k: v for k, v in (query or {}).items() if v is not None})
        assert result.status_code == 200, result.text
        return result.json()

    monkeypatch.setattr(AuthorityClient, "request", read)
    yield config, service, client
    assert poison.read_bytes() == b"Retired authority; never open"


def test_dashboard_init_generates_sqlite_and_grafana_assets(selected_authority, tmp_path) -> None:
    config, service, _ = selected_authority
    before = history_count(service)
    result = CliRunner().invoke(main, ["--config", str(config), "dashboard", "init", "--json"])
    assert result.exit_code == 0, result.output
    runtime = tmp_path / ".groundtruth/dashboard"
    generated = json.loads((runtime / "grafana/dashboards/gtkb-dashboard.json").read_text())
    assert generated["uid"] == "groundtruth-kb-dashboard"
    assert (runtime / "index.html").is_file()
    assert (runtime / "grafana/provisioning/alerting/contact-points.yaml").is_file()
    with sqlite3.connect(runtime / "gtkb-dashboard.sqlite") as conn:
        metrics = dict(conn.execute("SELECT metric_key,value FROM kpi_snapshots"))
        assert metrics["specification_current_total"] == 1
        assert metrics["regression_release_blocker_count"] is None
        assert conn.execute("SELECT COUNT(*) FROM setup_steps").fetchone()[0] >= 6
    assert history_count(service) == before


def test_dashboard_refresh_reports_seeded_spec_counts(selected_authority, tmp_path) -> None:
    config, service, client = selected_authority
    args = ["--config", str(config), "dashboard", "refresh", "--json"]
    assert CliRunner().invoke(main, args).exit_code == 0
    assert (
        put(client, "specifications", "SPEC-2", {"title": "Another requirement", "status": "active"}).status_code == 200
    )
    before = history_count(service)
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    with sqlite3.connect(tmp_path / ".groundtruth/dashboard/gtkb-dashboard.sqlite") as conn:
        values = conn.execute(
            "SELECT value FROM kpi_snapshots WHERE metric_key='specification_current_total' ORDER BY generated_at"
        ).fetchall()
        assert values == [(1,), (2,)]
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs WHERE status='completed'").fetchone()[0] == 2
    assert history_count(service) == before


def _make_paths(tmp_path):
    config_path = tmp_path / "groundtruth.toml"
    config_path.write_text("[groundtruth]\n", encoding="utf-8")
    config = GTConfig.load(config_path=config_path, discover=False)
    paths = dashboard.resolve_dashboard_paths(config)
    paths.pids_dir.mkdir(parents=True)
    return config, paths


def _fake_install(paths):
    binary = paths.grafana_home / "bin/grafana.exe"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"fixture only; never executed")
    defaults = paths.grafana_home / "conf/defaults.ini"
    defaults.parent.mkdir()
    defaults.write_text("; fixture", encoding="utf-8")
    return binary


def test_dashboard_install_accepts_existing_grafana_home(tmp_path) -> None:
    _, paths = _make_paths(tmp_path)
    _fake_install(paths)
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(tmp_path / "groundtruth.toml"),
            "dashboard",
            "install",
            "--skip-download",
            "--skip-plugin",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    observation = json.loads((paths.grafana_home / "installed.json").read_text())
    assert observation["plugin_install_skipped"] is True
    assert observation["archive"] is None
    assert observation["archive_verified_by_this_install"] is False
    assert not paths.db_path.exists()


def test_dashboard_start_explains_missing_grafana(tmp_path) -> None:
    _make_paths(tmp_path)
    result = CliRunner().invoke(main, ["--config", str(tmp_path / "groundtruth.toml"), "dashboard", "start"])
    assert result.exit_code == 1
    assert "Grafana is not installed" in result.output
    assert not (tmp_path / ".groundtruth/dashboard/gtkb-dashboard.sqlite").exists()


def test_pid_alive_true_for_current_process() -> None:
    assert dashboard._pid_alive(os.getpid()) is True


def test_pid_alive_nonpositive_returns_false() -> None:
    assert dashboard._pid_alive(0) is False
    assert dashboard._pid_alive(-1) is False


def test_pid_identity_uses_creation_identity_without_tasklist(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail("Process identity must not depend on parsing tasklist output")

    monkeypatch.setattr(dashboard.subprocess, "run", forbidden)
    identity = dashboard._process_identity(os.getpid())
    assert identity["pid"] == os.getpid() and identity["created_at"]
    assert Path(identity["executable"]).is_file()
    assert dashboard._process_identity(os.getpid()) == identity


def test_inaccessible_process_identity_preserves_record_and_refuses_reuse(tmp_path, monkeypatch) -> None:
    record = tmp_path / "grafana.pid"
    dashboard._write_pid(record, os.getpid())
    before = record.read_bytes()

    def denied(pid):
        raise PermissionError("fixture access denial")

    monkeypatch.setattr(dashboard, "_process_identity", denied)
    with pytest.raises(PermissionError, match="fixture access denial"):
        dashboard._read_live_pid(record)
    assert record.read_bytes() == before


def test_pid_alive_returns_false_after_child_exit() -> None:
    process = subprocess.Popen([sys.executable, "-c", "pass"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    process.wait(timeout=10)
    assert not dashboard._pid_alive(process.pid)


def test_write_pid_is_atomic_and_wellformed(tmp_path) -> None:
    record = tmp_path / "grafana.pid"
    dashboard._write_pid(record, os.getpid())
    assert json.loads(record.read_text()) == dashboard._process_identity(os.getpid())
    assert list(tmp_path.iterdir()) == [record]


def test_read_live_pid_returns_pid_when_alive(tmp_path) -> None:
    record = tmp_path / "refresh-service.pid"
    dashboard._write_pid(record, os.getpid())
    assert dashboard._read_live_pid(record) == os.getpid()
    assert record.exists()


def test_read_live_pid_clears_stale_dead_pid(tmp_path, monkeypatch) -> None:
    record = tmp_path / "refresh-service.pid"
    dashboard._write_pid(record, os.getpid())
    monkeypatch.setattr(dashboard, "_process_identity", lambda pid: None)
    assert dashboard._read_live_pid(record) is None
    assert not record.exists()


def test_read_live_pid_unparseable_requires_inspection(tmp_path) -> None:
    record = tmp_path / "grafana.pid"
    record.write_bytes(b"not-a-pid\n")
    with pytest.raises(ValueError, match="requires inspection"):
        dashboard._read_live_pid(record)
    assert record.read_bytes() == b"not-a-pid\n"


def test_read_live_pid_missing_file_returns_none(tmp_path) -> None:
    assert dashboard._read_live_pid(tmp_path / "absent.pid") is None


def _fake_runtime(monkeypatch, paths):
    _fake_install(paths)
    identities = {
        pid: {"pid": pid, "created_at": "fixture-" + str(pid), "executable": "fixture"}
        for pid in (4321, 8765, 999000, 999001)
    }
    monkeypatch.setattr(dashboard, "_process_identity", identities.get)
    calls, health = [], []

    def launch(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(pid=999000 + len(calls) - 1)

    monkeypatch.setattr(dashboard.subprocess, "Popen", launch)
    monkeypatch.setattr(dashboard, "_wait_dashboard_http", lambda *args, **kwargs: health.append((args, kwargs)))
    return identities, calls, health


def _free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def test_start_dashboard_idempotent_reuses_live_pids(tmp_path, monkeypatch) -> None:
    config, paths = _make_paths(tmp_path)
    _, calls, health = _fake_runtime(monkeypatch, paths)
    dashboard._write_pid(paths.pids_dir / "refresh-service.pid", 4321)
    dashboard._write_pid(paths.pids_dir / "grafana.pid", 8765)
    before = {p.name: p.read_bytes() for p in paths.pids_dir.iterdir()}
    info = dashboard.start_dashboard(paths, config)
    assert (info.refresh_pid, info.grafana_pid) == (4321, 8765)
    assert calls == [] and {args[0] for args, _ in health} == {4321, 8765}
    assert {p.name: p.read_bytes() for p in paths.pids_dir.iterdir()} == before


def test_start_dashboard_spawns_when_pids_stale(tmp_path, monkeypatch) -> None:
    config, paths = _make_paths(tmp_path)
    identities, calls, health = _fake_runtime(monkeypatch, paths)
    dashboard._write_pid(paths.pids_dir / "refresh-service.pid", 4321)
    dashboard._write_pid(paths.pids_dir / "grafana.pid", 8765)
    identities.pop(4321)
    identities.pop(8765)
    info = dashboard.start_dashboard(paths, config, grafana_port=_free_port(), refresh_port=_free_port())
    assert len(calls) == 2 and (info.refresh_pid, info.grafana_pid) == (999000, 999001)
    assert {args[0] for args, _ in health} == {999000, 999001}
    assert dashboard._read_live_pid(paths.pids_dir / "refresh-service.pid") == 999000
    assert dashboard._read_live_pid(paths.pids_dir / "grafana.pid") == 999001


def test_stop_dashboard_skips_dead_pid_and_cleans_file(tmp_path, monkeypatch) -> None:
    _, paths = _make_paths(tmp_path)
    dashboard._write_pid(paths.pids_dir / "refresh-service.pid", os.getpid())
    monkeypatch.setattr(dashboard, "_process_identity", lambda pid: None)

    def forbidden(*args):
        pytest.fail("A stale process record must not signal a process")

    monkeypatch.setattr(dashboard, "_terminate_pid", forbidden)
    assert dashboard.stop_dashboard(paths) == []
    assert not list(paths.pids_dir.iterdir())


def test_stop_dashboard_terminates_live_pid_and_cleans_file(tmp_path) -> None:
    _, paths = _make_paths(tmp_path)
    process = subprocess.Popen(
        [sys.executable, "-c", "import time;time.sleep(120)"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    identity = dashboard._process_identity(process.pid)
    try:
        dashboard._write_pid(paths.pids_dir / "refresh-service.pid", process.pid)
        assert dashboard.stop_dashboard(paths) == [process.pid]
        process.wait(timeout=10)
        assert not list(paths.pids_dir.iterdir())
    finally:
        if process.poll() is None:
            dashboard._terminate_pid(process.pid, identity)
            process.wait(timeout=10)


def test_dashboard_shortcuts_preserve_copyable_path_labels(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(dashboard, "_write_bridge_swimlane_safe", lambda *args: None)
    local = str(tmp_path / "file with spaces.txt")
    model = {"dashboard_intelligence": {"shortcuts": [{"label": "Copy local path", "target": local, "kind": "local"}]}}
    output = tmp_path / "derived.sqlite"
    dashboard.refresh_database(output, tmp_path, model=model)
    with sqlite3.connect(output) as conn:
        assert conn.execute("SELECT label,target,kind FROM shortcuts").fetchall() == [
            ("Copy local path", local, "local")
        ]


@pytest.mark.parametrize("kind", [["canonical_deploy"], {"kind": "canonical_deploy"}, 1, None])
def test_non_string_manifest_kind_cannot_supply_event_classification(kind):
    row = {"_authority_source": "canonical_manifest", "event_kind": kind, "source": "git log", "result": "ok"}
    assert dashboard._classify_event_kind(row) == "change"


@pytest.mark.parametrize(
    "changes",
    [{"pid": True}, {"pid": 1.5}, {"pid": -1}, {"created_at": None}, {"executable": 7}, {"extra": "unrecognized"}],
)
def test_invalid_process_record_is_refused_without_rewrite(tmp_path, changes):
    path = tmp_path / "pid.json"
    path.write_text(
        json.dumps({"pid": 17, "created_at": "123", "executable": "fixture.exe", **changes}), encoding="utf-8"
    )
    before = path.read_bytes()
    with pytest.raises(ValueError, match="requires inspection"):
        dashboard._read_pid_record(path)
    assert path.read_bytes() == before


def test_refresh_run_without_insert_identity_refuses_before_model_work(tmp_path, monkeypatch):
    original_connect = sqlite3.connect
    model_reads = []

    class Connection:
        def __init__(self, *args, **kwargs):
            self.connection = original_connect(*args, **kwargs)

        def __enter__(self):
            self.connection.__enter__()
            return self

        def __exit__(self, *args):
            return self.connection.__exit__(*args)

        def __getattr__(self, name):
            return getattr(self.connection, name)

        def execute(self, sql, *args):
            cursor = self.connection.execute(sql, *args)
            return SimpleNamespace(lastrowid=None) if sql.startswith("INSERT INTO refresh_runs") else cursor

    monkeypatch.setattr(dashboard.sqlite3, "connect", Connection)
    monkeypatch.setattr(dashboard, "_build_dashboard_model", lambda *args: model_reads.append(args))
    path = tmp_path / "display.sqlite"
    with pytest.raises(RuntimeError, match="dashboard_refresh_run_identity_unavailable"):
        dashboard.refresh_database(path, tmp_path)
    assert model_reads == []
    with original_connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0] == 0
