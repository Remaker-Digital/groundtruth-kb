"""Tests for the generated GroundTruth KB operations dashboard."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb import dashboard
from groundtruth_kb.cli import main
from groundtruth_kb.dashboard import (
    DashboardPaths,
    DashboardProcessInfo,
    _pid_alive,
    _read_live_pid,
    _write_pid,
    start_dashboard,
    stop_dashboard,
)
from groundtruth_kb.db import KnowledgeDB


def test_dashboard_init_generates_sqlite_and_grafana_assets(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "dashboard", "init"])

    assert result.exit_code == 0, result.output
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    dashboard_json = (
        project_dir / ".groundtruth" / "dashboard" / "grafana" / "dashboards" / "groundtruth-kb-dashboard.json"
    )
    assert dashboard_db.exists()
    assert dashboard_json.exists()

    dashboard = json.loads(dashboard_json.read_text(encoding="utf-8"))
    assert dashboard["uid"] == "groundtruth-kb"
    assert dashboard["title"].startswith("Test Project")
    assert any(panel["title"] == "Operating State" for panel in dashboard["panels"])

    with sqlite3.connect(dashboard_db) as conn:
        setup_steps = conn.execute("SELECT COUNT(*) FROM setup_steps").fetchone()[0]
        services = conn.execute("SELECT COUNT(*) FROM third_party_services").fetchone()[0]
        openai = conn.execute(
            "SELECT service_name FROM third_party_services WHERE id = 'openai'",
        ).fetchone()[0]
        operating_components = conn.execute("SELECT COUNT(*) FROM operating_state_components").fetchone()[0]
        operating_schema = conn.execute(
            "SELECT value FROM dashboard_metadata WHERE key = 'operating_state_schema_version'",
        ).fetchone()[0]

    assert setup_steps >= 6
    assert services >= 7
    assert openai == "OpenAI Codex"
    assert operating_components >= 8
    assert operating_schema == "1"


def test_dashboard_refresh_reports_seeded_spec_counts(runner: CliRunner, project_dir: Path) -> None:
    config_flag = ["--config", str(project_dir / "groundtruth.toml")]
    seed_result = runner.invoke(main, [*config_flag, "seed"])
    assert seed_result.exit_code == 0, seed_result.output

    result = runner.invoke(main, [*config_flag, "dashboard", "refresh"])

    assert result.exit_code == 0, result.output
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    with sqlite3.connect(dashboard_db) as conn:
        specs_total = conn.execute("SELECT value FROM current_metrics WHERE key = 'specs-total'").fetchone()[0]
        failed_assertions = conn.execute(
            "SELECT value FROM current_metrics WHERE key = 'assertions-failed'",
        ).fetchone()[0]

    assert specs_total == "5"
    assert failed_assertions == "0"


def test_dashboard_install_accepts_existing_grafana_home(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()
    grafana_home = tmp_path / "grafana"
    bin_dir = grafana_home / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "grafana-server.exe").write_text("", encoding="utf-8")
    (bin_dir / "grafana-server").write_text("", encoding="utf-8")

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "dashboard",
            "install",
            "--grafana-home",
            str(grafana_home),
            "--skip-download",
            "--skip-plugin",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Grafana ready" in result.output


def test_dashboard_start_explains_missing_grafana(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "dashboard", "start"])

    assert result.exit_code == 1
    assert "Grafana is not installed" in result.output


# ---------------------------------------------------------------------------
# WI-3413: dashboard launcher idempotence + PID-liveness tracking regressions.
# bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-002.md (GO).
# ---------------------------------------------------------------------------


class _RecordingPopen:
    """Stand-in for ``subprocess.Popen`` that records calls and yields a PID."""

    def __init__(self, next_pid: int = 999000) -> None:
        self.calls: list = []
        self._next_pid = next_pid

    def __call__(self, *args, **kwargs):  # noqa: ANN002, ANN003 - test double
        self.calls.append((args, kwargs))
        pid = self._next_pid
        self._next_pid += 1
        return _FakeProc(pid)


class _FakeProc:
    def __init__(self, pid: int) -> None:
        self.pid = pid


def _make_paths(tmp_path: Path) -> DashboardPaths:
    runtime_root = tmp_path / "runtime"
    paths = DashboardPaths(
        project_root=tmp_path,
        db_path=tmp_path / "groundtruth.db",
        runtime_root=runtime_root,
        grafana_home=tmp_path / "grafana",
        provisioning_dir=runtime_root / "provisioning",
        dashboards_dir=runtime_root / "dashboards",
        logs_dir=runtime_root / "logs",
        pids_dir=runtime_root / "pids",
    )
    paths.pids_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    paths.grafana_home.mkdir(parents=True, exist_ok=True)
    return paths


def _stub_launch_environment(monkeypatch: pytest.MonkeyPatch, paths: DashboardPaths) -> _RecordingPopen:
    """Neutralize the heavy launch dependencies so ``start_dashboard`` runs.

    Returns the recording Popen double so a test can assert spawn behavior.
    """
    recorder = _RecordingPopen()
    monkeypatch.setattr(dashboard, "initialize_dashboard", lambda *a, **k: None)
    monkeypatch.setattr(dashboard, "find_grafana_server", lambda *a, **k: paths.grafana_home / "grafana-server")
    monkeypatch.setattr(dashboard.subprocess, "Popen", recorder)
    return recorder


def test_pid_alive_true_for_current_process() -> None:
    assert _pid_alive(os.getpid()) is True


def test_pid_alive_nonpositive_returns_false() -> None:
    assert _pid_alive(0) is False
    assert _pid_alive(-1) is False


def test_pid_alive_win32_branch_parses_tasklist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dashboard.sys, "platform", "win32")

    class _Completed:
        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    monkeypatch.setattr(
        dashboard.subprocess,
        "run",
        lambda *a, **k: _Completed("grafana-server.exe          4321 Console                1    50,000 K\n"),
    )
    assert _pid_alive(4321) is True

    monkeypatch.setattr(
        dashboard.subprocess,
        "run",
        lambda *a, **k: _Completed("INFO: No tasks are running which match the specified criteria.\n"),
    )
    assert _pid_alive(4321) is False


def test_pid_alive_win32_access_denied_assumes_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    """A hardened Windows host can return 'ERROR: Access denied.' from tasklist.

    The liveness probe must not misclassify a possibly-live tracked PID as dead
    in that indeterminate case (WI-3413 follow-up; NO-GO -004). The safe failure
    mode for an idempotence guard is "alive" - a false "dead" would trigger a
    duplicate dashboard start and stale-PID cleanup of a running process.
    """
    monkeypatch.setattr(dashboard.sys, "platform", "win32")

    class _DeniedCompleted:
        def __init__(self) -> None:
            self.stdout = ""
            self.stderr = "ERROR: Access denied.\n"
            self.returncode = 1

    monkeypatch.setattr(dashboard.subprocess, "run", lambda *a, **k: _DeniedCompleted())
    # 4321 is not the current process, so the win32 branch is exercised.
    assert _pid_alive(4321) is True


def test_pid_alive_posix_branch_uses_signal_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dashboard.sys, "platform", "linux")

    monkeypatch.setattr(dashboard.os, "kill", lambda pid, sig: None)
    assert _pid_alive(4321) is True

    def _raise_lookup(pid: int, sig: int) -> None:
        raise ProcessLookupError

    monkeypatch.setattr(dashboard.os, "kill", _raise_lookup)
    assert _pid_alive(4321) is False


def test_write_pid_is_atomic_and_wellformed(tmp_path: Path) -> None:
    pid_file = tmp_path / "grafana.pid"
    _write_pid(pid_file, 4321)
    assert pid_file.read_text(encoding="utf-8") == "4321\n"
    # No temp file should linger after a successful atomic replace.
    leftovers = [p for p in tmp_path.iterdir() if p.name != "grafana.pid"]
    assert leftovers == []


def test_read_live_pid_returns_pid_when_alive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pid_file = tmp_path / "refresh-service.pid"
    pid_file.write_text("4321\n", encoding="utf-8")
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: True)
    assert _read_live_pid(pid_file) == 4321
    assert pid_file.exists()


def test_read_live_pid_clears_stale_dead_pid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pid_file = tmp_path / "refresh-service.pid"
    pid_file.write_text("4321\n", encoding="utf-8")
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: False)
    assert _read_live_pid(pid_file) is None
    assert not pid_file.exists()


def test_read_live_pid_unparseable_returns_none(tmp_path: Path) -> None:
    pid_file = tmp_path / "grafana.pid"
    pid_file.write_text("not-a-pid\n", encoding="utf-8")
    assert _read_live_pid(pid_file) is None
    assert not pid_file.exists()


def test_read_live_pid_missing_file_returns_none(tmp_path: Path) -> None:
    assert _read_live_pid(tmp_path / "absent.pid") is None


def test_start_dashboard_idempotent_reuses_live_pids(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _make_paths(tmp_path)
    (paths.pids_dir / "refresh-service.pid").write_text("4321\n", encoding="utf-8")
    (paths.pids_dir / "grafana.pid").write_text("8765\n", encoding="utf-8")
    recorder = _stub_launch_environment(monkeypatch, paths)
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: True)

    info = start_dashboard(paths, object())

    assert isinstance(info, DashboardProcessInfo)
    # No duplicate process spawned when both tracked PIDs are live.
    assert recorder.calls == []
    assert info.refresh_pid == 4321
    assert info.grafana_pid == 8765
    # Tracked PIDs preserved (not overwritten).
    assert (paths.pids_dir / "refresh-service.pid").read_text(encoding="utf-8") == "4321\n"
    assert (paths.pids_dir / "grafana.pid").read_text(encoding="utf-8") == "8765\n"


def test_start_dashboard_spawns_when_pids_stale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _make_paths(tmp_path)
    (paths.pids_dir / "refresh-service.pid").write_text("4321\n", encoding="utf-8")
    (paths.pids_dir / "grafana.pid").write_text("8765\n", encoding="utf-8")
    recorder = _stub_launch_environment(monkeypatch, paths)
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: False)

    info = start_dashboard(paths, object())

    # Both processes spawned afresh because the tracked PIDs were dead.
    assert len(recorder.calls) == 2
    # Fresh PIDs written by the recording Popen (>= 999000).
    assert info.refresh_pid >= 999000
    assert info.grafana_pid >= 999000
    assert int((paths.pids_dir / "refresh-service.pid").read_text(encoding="utf-8")) == info.refresh_pid
    assert int((paths.pids_dir / "grafana.pid").read_text(encoding="utf-8")) == info.grafana_pid


def test_stop_dashboard_skips_dead_pid_and_cleans_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _make_paths(tmp_path)
    (paths.pids_dir / "refresh-service.pid").write_text("4321\n", encoding="utf-8")
    (paths.pids_dir / "grafana.pid").write_text("8765\n", encoding="utf-8")
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: False)
    terminated: list[int] = []
    monkeypatch.setattr(dashboard, "_terminate_pid", lambda pid: terminated.append(pid) or True)

    stopped = stop_dashboard(paths)

    assert stopped == []
    assert terminated == []  # dead PIDs are never signalled
    assert not (paths.pids_dir / "refresh-service.pid").exists()
    assert not (paths.pids_dir / "grafana.pid").exists()


def test_stop_dashboard_terminates_live_pid_and_cleans_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _make_paths(tmp_path)
    (paths.pids_dir / "refresh-service.pid").write_text("4321\n", encoding="utf-8")
    monkeypatch.setattr(dashboard, "_pid_alive", lambda pid: True)
    terminated: list[int] = []
    monkeypatch.setattr(dashboard, "_terminate_pid", lambda pid: terminated.append(pid) or True)

    stopped = stop_dashboard(paths)

    assert stopped == [4321]
    assert terminated == [4321]
    assert not (paths.pids_dir / "refresh-service.pid").exists()


def test_dashboard_shortcuts_use_copyable_path_labels(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "dashboard", "init"])
    assert result.exit_code == 0, result.output

    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    with sqlite3.connect(dashboard_db) as conn:
        descriptions = [row[0] for row in conn.execute("SELECT description FROM shortcuts ORDER BY sort_order")]

    assert descriptions
    assert all("Copy local path" in text for text in descriptions)
    assert not any(text.lower().startswith("open the") for text in descriptions)
