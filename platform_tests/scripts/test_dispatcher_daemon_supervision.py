# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for WI-4882 Slice 1: dispatcher daemon supervision + log.

Covers DELIB-20266276 D2 (daemon death auto-recovers) and D3 (dedicated
idempotent ensure-alive supervisor), plus the persistent-log diagnosability
prerequisite. Daemon liveness and the detached spawn are simulated via
monkeypatch — no real background daemon or Task Scheduler mutation.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import ensure_dispatcher_daemon as ensure  # noqa: E402
import gtkb_dispatcher_daemon as daemon  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_daemon_logger():
    """The daemon logger is a module-level singleton; clear its handlers between
    tests so each test's RotatingFileHandler points at its own tmp dir."""
    logger = logging.getLogger("gtkb.dispatcher_daemon")
    saved = list(logger.handlers)
    for handler in saved:
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass
    yield
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass


# --- D3: idempotent ensure-alive ---------------------------------------------


def test_ensure_is_idempotent_noop_when_alive(tmp_path, monkeypatch):
    """When the daemon is alive, ensure no-ops and spawns nothing (D3)."""
    spawn_calls = []
    monkeypatch.setattr(ensure.daemon, "read_daemon_status", lambda root: {"running": True})
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: spawn_calls.append((root, interval)) or 0
    )
    result = ensure.ensure_daemon_running(tmp_path, 30)
    assert result["action"] == "noop"
    assert result["running"] is True
    assert spawn_calls == []


def test_ensure_restarts_dead_daemon(tmp_path, monkeypatch):
    """When the daemon is dead, ensure spawns a detached daemon (D2/D3)."""
    spawn_calls = []
    monkeypatch.setattr(ensure.daemon, "read_daemon_status", lambda root: {"running": False})
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: False)

    def _fake_spawn(root, interval):
        spawn_calls.append((root, interval))
        return 12345

    monkeypatch.setattr(ensure, "_spawn_detached_daemon", _fake_spawn)
    result = ensure.ensure_daemon_running(tmp_path, 45)
    assert result["action"] == "spawned"
    assert result["pid"] == 12345
    assert len(spawn_calls) == 1
    assert spawn_calls[0][1] == 45


# --- Persistent log + diagnosability -----------------------------------------


def test_daemon_log_written_on_activity(tmp_path):
    """get_daemon_logger writes an INFO record to a persistent daemon.log."""
    state_dir = tmp_path / "dispatcher-daemon"
    logger = daemon.get_daemon_logger(state_dir)
    daemon._safe_log(logger, "info", "tick completed pid=%s", 999)
    for handler in logger.handlers:
        handler.flush()
    log_path = state_dir / daemon.DAEMON_LOG_FILENAME
    assert log_path.is_file()
    assert "tick completed pid=999" in log_path.read_text(encoding="utf-8")


def test_fatal_exception_logged(tmp_path, monkeypatch):
    """A fatal exception in the loop body is logged (with traceback) before the
    loop dies — the diagnosability fix for the unsupervised-death gap."""
    monkeypatch.setattr(daemon, "acquire_daemon_lock", lambda state_dir: True)
    monkeypatch.setattr(daemon, "release_daemon_lock", lambda state_dir: None)
    monkeypatch.setattr(daemon, "_reap_dispatched_workers", lambda root: 0)

    def _boom(project_root, *, max_items=2):
        raise RuntimeError("injected tick failure")

    monkeypatch.setattr(daemon, "run_tick", _boom)
    with pytest.raises(RuntimeError, match="injected tick failure"):
        daemon.run_loop(tmp_path, tick_seconds=1)
    log_path = daemon._daemon_state_dir(tmp_path) / daemon.DAEMON_LOG_FILENAME
    assert log_path.is_file()
    body = log_path.read_text(encoding="utf-8")
    assert "fatal exception in daemon tick" in body
    assert "RuntimeError: injected tick failure" in body  # traceback captured


def test_logging_failure_does_not_break_tick(tmp_path):
    """_safe_log swallows a logging-handler error (fail-soft)."""

    class _BrokenLogger:
        def info(self, *args, **kwargs):
            raise OSError("disk full")

    # Must not raise.
    daemon._safe_log(_BrokenLogger(), "info", "should not propagate")


# --- D3: scheduled-task supervisor installer ---------------------------------


@pytest.mark.skipif(sys.platform != "win32", reason="PowerShell installer is Windows-only")
def test_install_task_dry_run_renders_command(tmp_path):
    """install_dispatcher_daemon_task.ps1 -DryRun renders the ensure-script
    invocation and makes no Task Scheduler call."""
    install = _SCRIPTS_DIR / "install_dispatcher_daemon_task.ps1"
    proc = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(install),
            "-DryRun",
            "-ProjectRoot",
            str(_REPO_ROOT),
            "-TaskName",
            "GTKB-DispatcherDaemon-Test-pytest",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "WOULD REGISTER TaskName=GTKB-DispatcherDaemon-Test-pytest" in proc.stdout
    assert "ensure_dispatcher_daemon.py" in proc.stdout
