"""Package dashboard routes and process records use native observations and exact launches."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from platform_tests.groundtruth_kb.native_fixtures import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import native as _native_fixture

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
    paths.runtime_root.mkdir(parents=True)
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


def test_pid_alive_returns_false_after_child_exit() -> None:
    process = subprocess.Popen([sys.executable, "-c", "pass"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    process.wait(timeout=10)
    assert not dashboard._pid_alive(process.pid)


# ---------------------------------------------------------------------------
# Launch record: written atomically, validated on read, never rewritten when malformed
# ---------------------------------------------------------------------------


def _member(role, pid, **changes):
    identity = dashboard._process_identity(pid) or {"pid": pid, "created_at": "fixture", "executable": "fixture"}
    return {"role": role, **identity, **changes}


def _record(paths, members, job="fixture-job"):
    record = {
        "job": job,
        "members": members,
        "grafana_port": 3000,
        "refresh_port": 8766,
        "interval_seconds": 3600,
        "config_path": str(paths.project_root / "groundtruth.toml"),
        "started_at": "2026-09-17T00:00:00+00:00",
    }
    dashboard._write_launch_record(paths.launch_record, record)
    return record


def test_write_launch_record_is_atomic_and_wellformed(tmp_path) -> None:
    _, paths = _make_paths(tmp_path)
    record = _record(paths, [_member("refresh-service", os.getpid())])
    assert json.loads(paths.launch_record.read_text(encoding="utf-8")) == record
    assert list(paths.runtime_root.iterdir()) == [paths.launch_record]
    assert dashboard._read_launch_record(paths.launch_record) == record


def test_read_launch_record_missing_file_returns_none(tmp_path) -> None:
    assert dashboard._read_launch_record(tmp_path / "absent.json") is None


def test_launch_record_unparseable_requires_inspection(tmp_path) -> None:
    record = tmp_path / dashboard.LAUNCH_RECORD_NAME
    record.write_bytes(b"not-a-record\n")
    with pytest.raises(ValueError, match="requires inspection"):
        dashboard._read_launch_record(record)
    assert record.read_bytes() == b"not-a-record\n"


@pytest.mark.parametrize(
    "changes",
    [{"pid": True}, {"pid": 1.5}, {"pid": -1}, {"created_at": None}, {"executable": 7}, {"extra": "unrecognized"}],
)
def test_invalid_launch_record_is_refused_without_rewrite(tmp_path, changes):
    path = tmp_path / dashboard.LAUNCH_RECORD_NAME
    member = {"role": "grafana", "pid": 17, "created_at": "123", "executable": "fixture.exe", **changes}
    path.write_text(json.dumps({"job": None, "members": [member]}), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="requires inspection"):
        dashboard._read_launch_record(path)
    assert path.read_bytes() == before


def test_inaccessible_job_inspection_preserves_launch_record(tmp_path, monkeypatch) -> None:
    """When the job cannot even be inspected, the stop refuses and leaves the record for the operator."""
    _, paths = _make_paths(tmp_path)
    _record(paths, [_member("refresh-service", os.getpid())])
    before = paths.launch_record.read_bytes()

    def denied(*args):
        raise PermissionError("fixture access denial")

    monkeypatch.setattr(dashboard, "_open_dashboard_job", denied)
    monkeypatch.setattr(dashboard, "_process_identity", denied)
    with pytest.raises(PermissionError, match="fixture access denial"):
        dashboard.stop_dashboard(paths)
    assert paths.launch_record.read_bytes() == before


# ---------------------------------------------------------------------------
# Launch and stop through the named kill-on-close job (Windows); the record decides nothing about signalling
# ---------------------------------------------------------------------------

WINDOWS_ONLY = pytest.mark.skipif(sys.platform != "win32", reason="job containment is a Windows mechanism")


def _fake_runtime(monkeypatch, paths):
    """Process creation and containment are captured; the job primitives are replaced per test."""
    _fake_install(paths)
    identities = {
        pid: {"pid": pid, "created_at": "fixture-" + str(pid), "executable": "fixture"}
        for pid in (4321, 8765, 999000, 999001)
    }
    monkeypatch.setattr(dashboard, "_process_identity", identities.get)
    calls, health = [], []

    def contained(args, cwd, env, log, job):
        calls.append({"args": args, "cwd": cwd, "env": env, "log": log.name, "job": job})
        return SimpleNamespace(pid=999000 + len(calls) - 1, poll=lambda: None, wait=lambda **kw: 0)

    def forbidden(*args, **kwargs):
        pytest.fail("A launch on Windows must be contained; plain Popen is not a launch route")

    monkeypatch.setattr(dashboard, "_start_contained", contained)
    monkeypatch.setattr(dashboard.subprocess, "Popen", forbidden)
    monkeypatch.setattr(dashboard, "_wait_dashboard_http", lambda *args, **kwargs: health.append((args, kwargs)))
    monkeypatch.setattr(dashboard, "_close_handle", lambda handle: None)
    return identities, calls, health


def _free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


@WINDOWS_ONLY
def test_start_dashboard_idempotent_reuses_live_job_members(tmp_path, monkeypatch) -> None:
    config, paths = _make_paths(tmp_path)
    _, calls, health = _fake_runtime(monkeypatch, paths)
    job_name = dashboard._dashboard_job_name(paths.runtime_root)
    _record(paths, [_member("refresh-service", 4321), _member("grafana", 8765)], job=job_name)
    before = paths.launch_record.read_bytes()
    monkeypatch.setattr(dashboard, "_open_dashboard_job", lambda name: 1 if name == job_name else None)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda job: [4321, 8765, 424242])
    monkeypatch.setattr(dashboard, "_create_dashboard_job", lambda name: pytest.fail("no second job is created"))
    info = dashboard.start_dashboard(paths, config)
    assert (info.refresh_pid, info.grafana_pid, info.job) == (4321, 8765, job_name)
    assert calls == [] and {args[0] for args, _ in health} == {4321, 8765}
    assert paths.launch_record.read_bytes() == before


@WINDOWS_ONLY
def test_start_dashboard_spawns_when_record_is_stale_and_no_job_exists(tmp_path, monkeypatch) -> None:
    """A record without a job names nothing that runs: it is removed, a job is created and both children start
    contained in it, and the new record names the job and the launched processes."""
    config, paths = _make_paths(tmp_path)
    _, calls, health = _fake_runtime(monkeypatch, paths)
    job_name = dashboard._dashboard_job_name(paths.runtime_root)
    _record(paths, [_member("refresh-service", 4321), _member("grafana", 8765)], job=job_name)
    created = []
    monkeypatch.setattr(dashboard, "_open_dashboard_job", lambda name: None)
    monkeypatch.setattr(dashboard, "_create_dashboard_job", lambda name: created.append(name) or 77)
    info = dashboard.start_dashboard(paths, config, grafana_port=_free_port(), refresh_port=_free_port())
    assert created == [job_name] and [call["job"] for call in calls] == [77, 77]
    assert (info.refresh_pid, info.grafana_pid, info.job) == (999000, 999001, job_name)
    assert {args[0] for args, _ in health} == {999000, 999001}
    assert calls[0]["log"].endswith("refresh-service.log") and calls[1]["log"].endswith("grafana.log")
    grafana_env = calls[1]["env"]
    assert {key: grafana_env[key] for key in dashboard.GRAFANA_LAUNCH_PINS} == dashboard.GRAFANA_LAUNCH_PINS
    record = dashboard._read_launch_record(paths.launch_record)
    assert record["job"] == job_name
    assert [(m["role"], m["pid"]) for m in record["members"]] == [("grafana", 999001), ("refresh-service", 999000)]
    assert not (paths.runtime_root / "pids").exists()


@WINDOWS_ONLY
def test_start_dashboard_refuses_a_running_job_without_its_record(tmp_path, monkeypatch) -> None:
    config, paths = _make_paths(tmp_path)
    _, calls, _ = _fake_runtime(monkeypatch, paths)
    monkeypatch.setattr(dashboard, "_open_dashboard_job", lambda name: 1)
    monkeypatch.setattr(dashboard, "_job_member_pids", lambda job: [4321])
    with pytest.raises(dashboard.DashboardIdentityError, match="without a matching launch record"):
        dashboard.start_dashboard(paths, config)
    assert calls == []


@WINDOWS_ONLY
def test_stop_dashboard_without_job_cleans_stale_record_and_signals_nothing(tmp_path, monkeypatch) -> None:
    _, paths = _make_paths(tmp_path)
    _record(paths, [_member("refresh-service", os.getpid())], job=dashboard._dashboard_job_name(paths.runtime_root))
    monkeypatch.setattr(dashboard, "_open_dashboard_job", lambda name: None)

    def forbidden(*args, **kwargs):
        pytest.fail("A stale launch record must not signal a process")

    monkeypatch.setattr(dashboard, "_stop_job", forbidden)
    monkeypatch.setattr(dashboard, "_terminate_pid", forbidden)
    assert dashboard.stop_dashboard(paths) == []
    assert not list(paths.runtime_root.iterdir())


@WINDOWS_ONLY
def test_stop_dashboard_terminates_the_job_and_cleans_record(tmp_path) -> None:
    """A real child contained in this runtime's job is ended by the stop, which reports it and removes the record;
    afterwards the job no longer exists and a second stop finds nothing."""
    _, paths = _make_paths(tmp_path)
    paths.logs_dir.mkdir()
    job_name = dashboard._dashboard_job_name(paths.runtime_root)
    job = dashboard._create_dashboard_job(job_name)
    process = None
    try:
        with (paths.logs_dir / "child.log").open("ab") as log:
            process = dashboard._start_contained(
                [sys.executable, "-c", "import time; time.sleep(120)"], tmp_path, dict(os.environ), log, job
            )
        _record(paths, [_member("refresh-service", process.pid)], job=job_name)
        dashboard._close_handle(job)
        job = None
        stopped = dashboard.stop_dashboard(paths)
        assert any(entry.pid == process.pid and entry.outcome == "terminated" for entry in stopped)
        assert all(entry.executable for entry in stopped if entry.outcome == "terminated")
        assert process.wait(timeout=10) is not None
        assert not paths.launch_record.exists()
        assert dashboard._open_dashboard_job(job_name) is None
        assert dashboard.stop_dashboard(paths) == []
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        if job is not None:
            dashboard._close_handle(job)


@WINDOWS_ONLY
def test_terminate_pid_distinguishes_identity_mismatch_from_termination_failures(monkeypatch, caplog) -> None:
    """The three stop failures are distinct classes: a number that no longer identifies the launch is never signalled;
    a refused taskkill with the process still alive; an accepted taskkill whose handle stays unsignalled. A non-zero
    taskkill exit with the process gone is a warning, not a failure."""
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(120)"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    identity = dashboard._process_identity(process.pid)
    original_run = subprocess.run
    kernel = dashboard._kernel32()
    original_wait = kernel.WaitForSingleObject
    try:
        with pytest.raises(dashboard.DashboardIdentityError, match="nothing was signalled"):
            dashboard._terminate_pid(process.pid, {**identity, "created_at": identity["created_at"] + "0"})
        assert process.poll() is None

        def refusing(args, **kwargs):
            return subprocess.CompletedProcess(args, 1, b"", b"ERROR: fixture refusal")

        monkeypatch.setattr(dashboard.subprocess, "run", refusing)
        monkeypatch.setattr(kernel, "WaitForSingleObject", lambda handle, ms: 0x102 if ms else original_wait(handle, 0))
        with pytest.raises(dashboard.DashboardTerminationRefused, match="fixture refusal"):
            dashboard._terminate_pid(process.pid, identity)
        assert process.poll() is None

        accepted = lambda args, **kwargs: subprocess.CompletedProcess(args, 0, b"", b"")  # noqa: E731
        monkeypatch.setattr(dashboard.subprocess, "run", accepted)
        with pytest.raises(dashboard.DashboardTerminationUnconfirmed, match="had not ended"):
            dashboard._terminate_pid(process.pid, identity)
        assert process.poll() is None
        monkeypatch.setattr(kernel, "WaitForSingleObject", original_wait)

        def ended_but_nonzero(args, **kwargs):
            original_run(args, **kwargs)
            return subprocess.CompletedProcess(args, 128, b"", b"ERROR: a tree member had already ended")

        monkeypatch.setattr(dashboard.subprocess, "run", ended_but_nonzero)
        with caplog.at_level(logging.WARNING, logger="groundtruth_kb.dashboard"):
            assert dashboard._terminate_pid(process.pid, identity) is True
        assert process.wait(timeout=10) is not None
        assert any("taskkill exited 128" in record.getMessage() for record in caplog.records)
        assert dashboard._terminate_pid(process.pid, identity) is True  # already gone: nothing to signal
    finally:
        monkeypatch.setattr(kernel, "WaitForSingleObject", original_wait)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)


# ---------------------------------------------------------------------------
# Derived-schema guard: a legacy or foreign derived database is moved aside and rebuilt, never refused
# ---------------------------------------------------------------------------

LEGACY_JULY_9_SCHEMA = """
CREATE TABLE kpi_snapshots (
    id TEXT PRIMARY KEY, metric TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL,
    captured_at TEXT NOT NULL, source TEXT NOT NULL
);
CREATE TABLE dashboard_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE refresh_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL,
    error TEXT NOT NULL DEFAULT ''
);
INSERT INTO kpi_snapshots VALUES ('k1', 'backlog', 4.0, 'items', '2026-07-09T23:32:29Z', 'legacy');
INSERT INTO dashboard_metadata VALUES ('generated_at', '2026-07-09T23:32:29Z', '2026-07-09T23:32:29Z');
INSERT INTO refresh_runs (started_at, status) VALUES ('2026-07-09T23:32:29Z', 'failed');
"""


def _legacy_database(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(sqlite3.connect(path)) as conn:  # closed now: the file must be movable afterwards
        conn.executescript(LEGACY_JULY_9_SCHEMA)


def test_refresh_rebuilds_legacy_derived_database_and_moves_it_aside(tmp_path, monkeypatch, caplog) -> None:
    monkeypatch.setattr(dashboard, "_write_bridge_swimlane_safe", lambda *args: None)
    runtime = tmp_path / ".groundtruth/dashboard"
    output = runtime / "gtkb-dashboard.sqlite"
    _legacy_database(output)
    legacy_bytes = output.read_bytes()
    model = {"dashboard_intelligence": {"shortcuts": [{"label": "Copy", "target": "x", "kind": "local"}]}}
    with caplog.at_level(logging.WARNING, logger="groundtruth_kb.dashboard"):
        result = dashboard.refresh_database(output, tmp_path, model=model)
    assert result["status"] == "completed"
    moved = Path(result["legacy_database_moved_to"])
    assert moved.parent == runtime and moved.name.startswith("gtkb-dashboard.sqlite.legacy-")
    assert moved.name[len("gtkb-dashboard.sqlite.legacy-") :].endswith("Z")
    assert moved.read_bytes() == legacy_bytes
    with sqlite3.connect(output) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info('kpi_snapshots')")}
        assert {"generated_at", "metric_key", "metric_label", "value", "metric_group"} <= columns
        assert {row[1] for row in conn.execute("PRAGMA table_info('dashboard_metadata')")} == {"key", "value"}
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs WHERE status='completed'").fetchone()[0] == 1
        assert conn.execute("SELECT label FROM shortcuts").fetchall() == [("Copy",)]
    messages = [record.getMessage() for record in caplog.records if record.name == "groundtruth_kb.dashboard"]
    assert any("moved aside" in m and "a legacy or foreign derived schema is no history" in m for m in messages)
    # The first disqualifying table in name order is named; the July-9 file has two (dashboard_metadata, kpi_snapshots).
    assert any("dashboard_metadata carries NOT NULL column(s) without a default" in m for m in messages)
    # The rebuilt file carries the current schema: a second refresh keeps it and moves nothing.
    again = dashboard.refresh_database(output, tmp_path, model=model)
    assert "legacy_database_moved_to" not in again
    assert sorted(p.name for p in runtime.iterdir() if p.name.startswith("gtkb-dashboard.sqlite")) == sorted(
        ["gtkb-dashboard.sqlite", moved.name]
    )


@pytest.mark.parametrize(
    ("shape", "reason"),
    [
        ("legacy-kpi", "kpi_snapshots lacks the expected column(s) generated_at, lower_is_better, metric_group"),
        ("not-null-extra", "dashboard_metadata carries NOT NULL column(s) without a default"),
        ("foreign-table", "carries table operating_state_components, which the current derived schema does not define"),
        ("not-a-database", "is not a database this package can read"),
        ("current", None),
        ("pre-migration", None),
        ("nullable-extra", None),
        ("defaulted-extra", None),
    ],
)
def test_derived_schema_mismatch_names_the_disqualifying_shape(tmp_path, shape, reason) -> None:
    path = tmp_path / "derived.sqlite"
    if shape == "not-a-database":
        path.write_bytes(b"Retired authority bytes; never a derived database")
    else:
        dashboard.initialize_database(path)
        with sqlite3.connect(path) as conn:
            if shape == "legacy-kpi":
                conn.executescript(
                    "DROP TABLE kpi_snapshots; CREATE TABLE kpi_snapshots (id TEXT PRIMARY KEY, metric TEXT NOT NULL, "
                    "value REAL NOT NULL, unit TEXT NOT NULL, captured_at TEXT NOT NULL, source TEXT NOT NULL);"
                )
            elif shape == "not-null-extra":
                conn.executescript(
                    "DROP TABLE dashboard_metadata; CREATE TABLE dashboard_metadata "
                    "(key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);"
                )
            elif shape == "foreign-table":
                conn.execute("CREATE TABLE operating_state_components (name TEXT PRIMARY KEY)")
            elif shape == "pre-migration":
                conn.executescript(
                    "DROP TABLE delivery_timeline_events; CREATE TABLE delivery_timeline_events "
                    "(id INTEGER PRIMARY KEY AUTOINCREMENT, sort_order INTEGER NOT NULL, stage TEXT NOT NULL, "
                    "stage_label TEXT NOT NULL, event TEXT NOT NULL, timestamp TEXT NOT NULL, "
                    "date_label TEXT NOT NULL, version TEXT NOT NULL, commit_sha TEXT NOT NULL, branch TEXT NOT NULL, "
                    "result TEXT NOT NULL, result_color TEXT NOT NULL, test_results TEXT NOT NULL, "
                    "source TEXT NOT NULL, url TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', "
                    "environment TEXT NOT NULL DEFAULT '');"
                )
            elif shape == "nullable-extra":
                conn.execute("ALTER TABLE shortcuts ADD COLUMN icon TEXT")
            elif shape == "defaulted-extra":
                dashboard._migrate_schema(path)
    before = path.read_bytes()
    verdict = dashboard._derived_schema_mismatch(path)
    assert path.read_bytes() == before, "the inspection is read-only"
    if reason is None:
        assert verdict is None
    else:
        assert verdict is not None and reason in verdict


def test_schema_only_init_moves_a_legacy_derived_database_aside(tmp_path) -> None:
    selected = tmp_path / "chosen.toml"
    selected.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:39899"\n', encoding="utf-8")
    output = tmp_path / ".groundtruth/dashboard/gtkb-dashboard.sqlite"
    _legacy_database(output)
    result = CliRunner().invoke(main, ["--config", str(selected), "dashboard", "init", "--schema-only", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "initialized" and payload["refreshed"] is False
    assert Path(payload["legacy_database_moved_to"]).parent == output.parent
    with sqlite3.connect(output) as conn:
        assert conn.execute("SELECT COUNT(*) FROM refresh_runs").fetchone()[0] == 0
        assert {row[1] for row in conn.execute("PRAGMA table_info('dashboard_metadata')")} == {"key", "value"}
    second = CliRunner().invoke(main, ["--config", str(selected), "dashboard", "init", "--schema-only", "--json"])
    assert second.exit_code == 0, second.output
    assert "legacy_database_moved_to" not in json.loads(second.output)


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
