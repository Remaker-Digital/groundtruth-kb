# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for WI-4882 Slice 1: dispatcher daemon supervision + log.

Covers DELIB-20266276 D2 (daemon death auto-recovers) and D3 (dedicated
idempotent ensure-alive supervisor), plus the persistent-log diagnosability
prerequisite. Daemon liveness and the detached spawn are simulated via
monkeypatch — no real background daemon or Task Scheduler mutation.
"""

from __future__ import annotations

import importlib.util
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


def _load_watchdog_launcher():
    path = _SCRIPTS_DIR / "ops" / "harness_storm_watchdog_launcher.py"
    spec = importlib.util.spec_from_file_location("harness_storm_watchdog_launcher_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _clear_daemon_logger_handlers() -> None:
    logger = logging.getLogger("gtkb.dispatcher_daemon")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass


@pytest.fixture(autouse=True)
def _reset_daemon_logger():
    """The daemon logger is a module-level singleton; clear its handlers between
    tests so each test's RotatingFileHandler points at its own tmp dir."""
    _clear_daemon_logger_handlers()
    yield
    _clear_daemon_logger_handlers()


# --- D3: idempotent ensure-alive ---------------------------------------------


def test_ensure_is_idempotent_noop_when_alive(tmp_path, monkeypatch):
    """When the daemon is alive, ensure no-ops and spawns nothing (D3)."""
    spawn_calls = []
    monkeypatch.setattr(
        ensure.daemon,
        "read_daemon_status",
        lambda root: {
            "running": True,
            "generation_match": True,
            "loaded_generation": "sha256:current",
        },
    )
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
    monkeypatch.setattr(
        ensure.daemon,
        "dispatch_quiescence",
        lambda root: {"known": True, "live_worker_count": 0, "live_document_lease_count": 0},
    )
    monkeypatch.setattr(
        ensure.daemon,
        "current_runtime_generation",
        lambda root: {"generation": "sha256:current", "errors": []},
    )
    monkeypatch.setattr(
        ensure,
        "_wait_for_successor_generation",
        lambda root, expected: {
            "running": True,
            "generation_match": True,
            "loaded_generation": expected,
            "current_generation": expected,
            "lock": {"pid": 12345},
        },
    )

    def _fake_spawn(root, interval):
        spawn_calls.append((root, interval))
        return 12345

    monkeypatch.setattr(ensure, "_spawn_detached_daemon", _fake_spawn)
    result = ensure.ensure_daemon_running(tmp_path, 45)
    assert result["action"] == "spawned"
    assert result["pid"] == 12345
    assert len(spawn_calls) == 1
    assert spawn_calls[0][1] == 45


def _stale_daemon_status(*, handoff_state: str | None = None, provenance: bool = True):
    status = {
        "running": True,
        "generation_match": False,
        "loaded_generation": "sha256:loaded",
        "current_generation": "sha256:current",
        "pid_provenance_verified": provenance,
        "lock": {
            "pid": 4242,
            "pid_create_time_epoch": 1234.5,
            "loaded_generation": "sha256:loaded",
        },
    }
    if handoff_state:
        status["generation_handoff"] = {"state": handoff_state}
    return status


def _handoff_request(*, phase: str = "requested"):
    return {
        "schema_version": 1,
        "phase": phase,
        "requested_at": "2026-07-17T00:00:00Z",
        "daemon_pid": 4242,
        "daemon_pid_create_time_epoch": 1234.5,
        "observed_loaded_generation": "sha256:loaded",
        "target_generation": "sha256:current",
    }


def test_ensure_fails_closed_when_live_generation_is_unknown(tmp_path, monkeypatch):
    spawn_calls = []
    monkeypatch.setattr(
        ensure.daemon,
        "read_daemon_status",
        lambda root: {
            "running": True,
            "generation_match": False,
            "loaded_generation": None,
            "current_generation": "sha256:current",
        },
    )
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: spawn_calls.append((root, interval)) or 99
    )

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result["action"] == "generation_handoff_failed"
    assert result["reason"] == "runtime_generation_unknown"
    assert spawn_calls == []
    assert ensure.daemon.read_generation_handoff_request(tmp_path) is None


def test_ensure_requests_stale_generation_handoff_without_terminating(tmp_path, monkeypatch):
    spawn_calls = []
    monkeypatch.setattr(ensure.daemon, "read_daemon_status", lambda root: _stale_daemon_status())
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: spawn_calls.append((root, interval)) or 99
    )

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result["action"] == "generation_handoff_deferred"
    assert result["reason"] == "handoff_requested"
    assert spawn_calls == []
    request = ensure.daemon.read_generation_handoff_request(tmp_path)
    assert request is not None
    assert request["phase"] == "requested"
    assert request["daemon_pid"] == 4242
    assert request["target_generation"] == "sha256:current"


def test_ensure_retargets_same_daemon_handoff_when_current_generation_changes(tmp_path, monkeypatch):
    request = _handoff_request()
    ensure.daemon.write_generation_handoff_request(tmp_path, request)
    changed_status = _stale_daemon_status()
    changed_status["current_generation"] = "sha256:new-current"
    monkeypatch.setattr(ensure.daemon, "read_daemon_status", lambda root: changed_status)
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: pytest.fail("retargeting must not spawn")
    )

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result["action"] == "generation_handoff_deferred"
    assert result["reason"] == "handoff_retargeted"
    updated = ensure.daemon.read_generation_handoff_request(tmp_path)
    assert updated["phase"] == "requested"
    assert updated["target_generation"] == "sha256:new-current"
    assert updated["supersedes_target_generation"] == "sha256:current"


def test_ensure_ready_handoff_defers_when_dispatch_work_reappears(tmp_path, monkeypatch):
    ensure.daemon.write_generation_handoff_request(tmp_path, _handoff_request())
    monkeypatch.setattr(
        ensure.daemon,
        "read_daemon_status",
        lambda root: _stale_daemon_status(handoff_state="generation_handoff_ready"),
    )
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure.daemon,
        "dispatch_quiescence",
        lambda root: {"known": True, "live_worker_count": 1, "live_document_lease_count": 1},
    )
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: pytest.fail("active work must block spawn")
    )

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result["action"] == "generation_handoff_deferred"
    assert result["reason"] == "dispatch_work_active"
    assert ensure.daemon.read_generation_handoff_request(tmp_path)["phase"] == "requested"


def test_ensure_completes_ready_handoff_once_and_attests_successor(tmp_path, monkeypatch):
    ensure.daemon.write_generation_handoff_request(tmp_path, _handoff_request())
    spawn_calls = []
    monkeypatch.setattr(
        ensure.daemon,
        "read_daemon_status",
        lambda root: _stale_daemon_status(handoff_state="generation_handoff_ready"),
    )
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)
    monkeypatch.setattr(
        ensure.daemon,
        "dispatch_quiescence",
        lambda root: {"known": True, "live_worker_count": 0, "live_document_lease_count": 0},
    )
    monkeypatch.setattr(ensure, "_wait_for_daemon_exit", lambda root, state_dir: True)
    monkeypatch.setattr(
        ensure, "_spawn_detached_daemon", lambda root, interval: spawn_calls.append((root, interval)) or 8181
    )
    monkeypatch.setattr(
        ensure,
        "_wait_for_successor_generation",
        lambda root, expected: {
            "running": True,
            "generation_match": True,
            "loaded_generation": expected,
            "current_generation": expected,
            "lock": {"pid": 8181},
        },
    )

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result == {
        "action": "generation_handoff_completed",
        "running": True,
        "old_pid": 4242,
        "pid": 8181,
        "loaded_generation": "sha256:current",
    }
    assert spawn_calls == [(tmp_path, 30)]
    assert ensure.daemon.read_generation_handoff_request(tmp_path) is None


def test_ensure_refuses_stale_daemon_without_pid_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(
        ensure.daemon,
        "read_daemon_status",
        lambda root: _stale_daemon_status(provenance=False),
    )
    monkeypatch.setattr(ensure.daemon, "daemon_process_alive", lambda state_dir: True)

    result = ensure.ensure_daemon_running(tmp_path, 30)

    assert result["action"] == "generation_handoff_failed"
    assert result["reason"] == "daemon_pid_provenance_unverified"
    assert ensure.daemon.read_generation_handoff_request(tmp_path) is None


def test_spawn_detached_daemon_runs_headless_on_windows(tmp_path, monkeypatch):
    """The supervisor's Windows fallback must not create a visible console window."""
    expected_no_window = 0x08000000
    expected_detached = 0x00000008
    expected_new_group = 0x00000200
    python_dir = tmp_path / "venv" / "Scripts"
    python_dir.mkdir(parents=True)
    python_exe = python_dir / "python.exe"
    pythonw_exe = python_dir / "pythonw.exe"
    python_exe.write_text("", encoding="utf-8")
    pythonw_exe.write_text("", encoding="utf-8")
    captured: dict[str, object] = {}

    class _FakePopen:
        def __init__(self, args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            self.pid = 2468

    monkeypatch.setattr(ensure.os, "name", "nt")
    monkeypatch.setattr(ensure.subprocess, "CREATE_NO_WINDOW", expected_no_window, raising=False)
    monkeypatch.setattr(ensure.subprocess, "DETACHED_PROCESS", expected_detached, raising=False)
    monkeypatch.setattr(ensure.subprocess, "CREATE_NEW_PROCESS_GROUP", expected_new_group, raising=False)
    monkeypatch.setattr(ensure.subprocess, "Popen", _FakePopen)
    monkeypatch.setattr(ensure.sys, "executable", str(python_exe))

    assert ensure._spawn_detached_daemon(tmp_path, 30) == 2468
    assert captured["args"][0] == str(pythonw_exe)
    kwargs = captured["kwargs"]
    flags = int(kwargs.get("creationflags", 0))
    assert flags & expected_no_window
    assert flags & expected_detached
    assert flags & expected_new_group
    assert kwargs.get("stdin") == subprocess.DEVNULL
    assert kwargs.get("stdout") == subprocess.DEVNULL
    assert kwargs.get("stderr") == subprocess.DEVNULL


def test_spawn_detached_daemon_falls_back_when_pythonw_missing(tmp_path, monkeypatch):
    """The supervisor should keep spawning with python.exe when pythonw.exe is not installed."""
    python_dir = tmp_path / "venv" / "Scripts"
    python_dir.mkdir(parents=True)
    python_exe = python_dir / "python.exe"
    python_exe.write_text("", encoding="utf-8")
    captured: dict[str, object] = {}

    class _FakePopen:
        def __init__(self, args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            self.pid = 3579

    monkeypatch.setattr(ensure.os, "name", "nt")
    monkeypatch.setattr(ensure.sys, "executable", str(python_exe))
    monkeypatch.setattr(ensure.subprocess, "Popen", _FakePopen)

    assert ensure._spawn_detached_daemon(tmp_path, 30) == 3579
    assert captured["args"][0] == str(python_exe)


def test_storm_watchdog_launcher_runs_powershell_headless_on_windows(monkeypatch):
    """The scheduled watchdog launcher must invoke PowerShell without a console."""
    launcher = _load_watchdog_launcher()
    expected_no_window = 0x08000000
    captured: dict[str, object] = {}

    def _fake_run(args, **kwargs):  # noqa: ANN001, ANN202
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr(launcher.os, "name", "nt")
    monkeypatch.setattr(launcher.subprocess, "CREATE_NO_WINDOW", expected_no_window, raising=False)
    monkeypatch.setattr(launcher, "ensure_snapshot_window_hider", lambda: True)
    monkeypatch.setattr(launcher.subprocess, "run", _fake_run)

    assert launcher.main() == 0
    args = captured["args"]
    kwargs = captured["kwargs"]
    assert args[0] == "powershell.exe"
    assert "-NonInteractive" in args
    assert args[args.index("-WindowStyle") + 1] == "Hidden"
    assert kwargs["stdin"] == subprocess.DEVNULL
    assert kwargs["stdout"] == subprocess.DEVNULL
    assert kwargs["stderr"] == subprocess.DEVNULL
    assert int(kwargs["creationflags"]) & expected_no_window
    startupinfo = kwargs.get("startupinfo")
    if sys.platform == "win32":
        assert startupinfo is not None
        assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
        assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


def test_storm_watchdog_launcher_starts_snapshot_hider_detached_and_headless(tmp_path, monkeypatch):
    """Window containment starts via pythonw and never gates watchdog execution."""
    launcher = _load_watchdog_launcher()
    expected_no_window = 0x08000000
    expected_detached = 0x00000008
    expected_new_group = 0x00000200
    python_dir = tmp_path / "venv" / "Scripts"
    python_dir.mkdir(parents=True)
    python_exe = python_dir / "python.exe"
    pythonw_exe = python_dir / "pythonw.exe"
    python_exe.write_text("", encoding="utf-8")
    pythonw_exe.write_text("", encoding="utf-8")
    hider = tmp_path / "codex_snapshot_window_hider.py"
    hider.write_text("", encoding="utf-8")
    captured: dict[str, object] = {}

    class _FakePopen:
        def __init__(self, args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs

    monkeypatch.setattr(launcher.os, "name", "nt")
    monkeypatch.setattr(launcher.sys, "executable", str(python_exe))
    monkeypatch.setattr(launcher, "SNAPSHOT_WINDOW_HIDER", hider)
    monkeypatch.setattr(launcher.subprocess, "CREATE_NO_WINDOW", expected_no_window, raising=False)
    monkeypatch.setattr(launcher.subprocess, "DETACHED_PROCESS", expected_detached, raising=False)
    monkeypatch.setattr(launcher.subprocess, "CREATE_NEW_PROCESS_GROUP", expected_new_group, raising=False)
    monkeypatch.setattr(launcher.subprocess, "Popen", _FakePopen)

    assert launcher.ensure_snapshot_window_hider() is True
    assert captured["args"] == [str(pythonw_exe), str(hider)]
    kwargs = captured["kwargs"]
    flags = int(kwargs["creationflags"])
    assert flags & expected_no_window
    assert flags & expected_detached
    assert flags & expected_new_group
    assert kwargs["stdin"] == subprocess.DEVNULL
    assert kwargs["stdout"] == subprocess.DEVNULL
    assert kwargs["stderr"] == subprocess.DEVNULL


def test_storm_watchdog_continues_when_snapshot_hider_cannot_start(monkeypatch):
    launcher = _load_watchdog_launcher()
    calls: list[str] = []

    monkeypatch.setattr(launcher, "ensure_snapshot_window_hider", lambda: False)
    monkeypatch.setattr(
        launcher.subprocess,
        "run",
        lambda args, **kwargs: calls.append(args[0]) or subprocess.CompletedProcess(args, 0),
    )

    assert launcher.main() == 0
    assert calls == ["powershell.exe"]


def test_dispatcher_supervisor_powershell_probe_runs_headless_on_windows(monkeypatch):
    """The supervisor status probe must invoke PowerShell without a console."""
    from groundtruth_kb import dispatcher_supervisor as supervisor

    expected_no_window = 0x08000000
    captured: dict[str, object] = {}

    def _fake_run(args, **kwargs):  # noqa: ANN001, ANN202
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(supervisor.os, "name", "nt")
    monkeypatch.setattr(supervisor.subprocess, "CREATE_NO_WINDOW", expected_no_window, raising=False)
    monkeypatch.setattr(supervisor.subprocess, "run", _fake_run)

    supervisor._run_powershell("Get-Date")
    args = captured["args"]
    kwargs = captured["kwargs"]
    assert args[0] == "powershell.exe"
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert int(kwargs["creationflags"]) & expected_no_window
    startupinfo = kwargs.get("startupinfo")
    if sys.platform == "win32":
        assert startupinfo is not None
        assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
        assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


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
    _clear_daemon_logger_handlers()
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


def test_dispatcher_installer_registers_startup_and_interval_triggers():
    """The supervisor task must recover after workstation startup and on interval."""
    install = _SCRIPTS_DIR / "install_dispatcher_daemon_task.ps1"
    body = install.read_text(encoding="utf-8")

    assert "New-ScheduledTaskTrigger -AtStartup" in body
    assert "New-ScheduledTaskTrigger -Once" in body
    assert "$triggers = @($startupTrigger, $intervalTrigger)" in body
    assert "-Trigger $triggers" in body
    assert "-Force `" in body
    assert "Unregister-ScheduledTask" not in body


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


def test_collect_supervisor_status_non_windows(tmp_path, monkeypatch):
    from groundtruth_kb.dispatcher_supervisor import collect_supervisor_status

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "posix")
    status = collect_supervisor_status(tmp_path)
    assert status["supported"] is False
    assert status["healthy"] is False


# ---------------------------------------------------------------------------
# WI-5429: generation-admission-aware recovery
# ---------------------------------------------------------------------------


class TestAdmissionAwareSpawnSource:
    """_resolve_daemon_spawn_source prefers admitted generations."""

    def test_falls_back_to_working_tree_when_no_admission(self, tmp_path, monkeypatch):
        """When no admitted generation exists, spawn from working-tree scripts."""
        monkeypatch.setattr(
            ensure.admission,
            "candidate_admission_status",
            lambda root: {
                "last_admitted_generation": None,
                "last_admitted_materialization_ok": False,
                "no_admitted_generation_exists": True,
                "current_working_tree_generation": "sha256:abc",
                "current_already_admitted": False,
                "current_unfinalized": False,
                "working_tree_errors": [],
            },
        )
        script_path, gen_id, meta = ensure._resolve_daemon_spawn_source(tmp_path)
        assert meta["source"] == "working_tree"
        assert gen_id is None

    def test_prefers_admitted_generation_when_materialization_intact(self, tmp_path, monkeypatch):
        """When a valid admitted generation exists, prefer it."""
        mat_dir = tmp_path / ".gtkb-state" / "dispatcher-generations" / "sha256-test"
        (mat_dir / "scripts").mkdir(parents=True)
        (mat_dir / "scripts" / "gtkb_dispatcher_daemon.py").write_text("# test")
        mat_dir_str = str(mat_dir)

        monkeypatch.setattr(
            ensure.admission,
            "candidate_admission_status",
            lambda root: {
                "last_admitted_generation": "sha256:test",
                "last_admitted_materialization_ok": True,
                "no_admitted_generation_exists": False,
                "current_working_tree_generation": "sha256:other",
                "current_already_admitted": False,
                "current_unfinalized": True,
                "working_tree_errors": [],
            },
        )
        monkeypatch.setattr(
            ensure.admission,
            "read_last_admitted",
            lambda root: {
                "generation": "sha256:test",
                "materialization_dir": mat_dir_str,
            },
        )

        script_path, gen_id, meta = ensure._resolve_daemon_spawn_source(tmp_path)
        assert meta["source"] == "admitted_generation"
        assert gen_id == "sha256:test"
        assert meta["unfinalized_rejected"] is True

    def test_falls_back_when_materialization_missing_file(self, tmp_path, monkeypatch):
        """When admitted generation materialization directory has no daemon
        script, fall back to working tree."""
        mat_dir = tmp_path / ".gtkb-state" / "dispatcher-generations" / "sha256-broken"
        mat_dir.mkdir(parents=True)
        # No scripts/ subdir created

        monkeypatch.setattr(
            ensure.admission,
            "candidate_admission_status",
            lambda root: {
                "last_admitted_generation": "sha256:broken",
                "last_admitted_materialization_ok": True,
                "no_admitted_generation_exists": False,
                "current_working_tree_generation": "sha256:abc",
                "current_already_admitted": False,
                "current_unfinalized": False,
                "working_tree_errors": [],
            },
        )
        monkeypatch.setattr(
            ensure.admission,
            "read_last_admitted",
            lambda root: {
                "generation": "sha256:broken",
                "materialization_dir": str(mat_dir),
            },
        )

        script_path, gen_id, meta = ensure._resolve_daemon_spawn_source(tmp_path)
        assert meta["source"] == "working_tree"


class TestUnfinalizedRejection:
    """Supervisor reports unfinalized_generation_rejected."""

    def test_unfinalized_flag_in_recovery_result(self, tmp_path, monkeypatch):
        """When daemon is dead and working tree has unfinalized changes,
        the recovery result includes the rejection flag."""
        monkeypatch.setattr(
            ensure.daemon,
            "read_daemon_status",
            lambda root: {"running": False},
        )
        monkeypatch.setattr(
            ensure.daemon, "daemon_process_alive", lambda state_dir: False
        )
        monkeypatch.setattr(
            ensure.admission,
            "candidate_admission_status",
            lambda root: {
                "last_admitted_generation": "sha256:prev",
                "last_admitted_materialization_ok": True,
                "no_admitted_generation_exists": False,
                "current_working_tree_generation": "sha256:new",
                "current_already_admitted": False,
                "current_unfinalized": True,
                "working_tree_errors": [],
            },
        )
        # Simulate an admitted generation materialization
        mat_dir = tmp_path / ".gtkb-state" / "dispatcher-generations" / "sha256-prev"
        (mat_dir / "scripts").mkdir(parents=True)
        (mat_dir / "scripts" / "gtkb_dispatcher_daemon.py").write_text("# test")
        monkeypatch.setattr(
            ensure.admission,
            "read_last_admitted",
            lambda root: {
                "generation": "sha256:prev",
                "materialization_dir": str(mat_dir),
            },
        )
        monkeypatch.setattr(
            ensure.daemon,
            "dispatch_quiescence",
            lambda root: {"known": True, "live_worker_count": 0, "live_document_lease_count": 0},
        )
        monkeypatch.setattr(
            ensure.daemon, "read_generation_handoff_request", lambda root: None
        )
        monkeypatch.setattr(
            ensure.daemon, "clear_generation_handoff_request", lambda root: None
        )
        monkeypatch.setattr(
            ensure.daemon,
            "current_runtime_generation",
            lambda root: {"generation": "sha256:prev"},
        )

        spawn_pid = [0]

        def fake_spawn(root, interval):
            spawn_pid[0] = 99999
            return 99999

        monkeypatch.setattr(ensure, "_spawn_detached_daemon", fake_spawn)
        monkeypatch.setattr(
            ensure,
            "_wait_for_successor_generation",
            lambda root, expected: {
                "running": True,
                "pid_provenance_verified": True,
                "loaded_generation": expected,
                "current_generation": expected,
                "generation_match": True,
                "lock": {"pid": 99999},
            },
        )

        result = ensure.ensure_daemon_running(tmp_path, 30)
        assert "admission" in result
        assert result["admission"] == "unfinalized_generation_rejected"

    def test_empty_admission_no_flag_when_already_admitted(self, tmp_path, monkeypatch):
        """When working tree matches admitted generation, no rejection flag."""
        monkeypatch.setattr(
            ensure.daemon,
            "read_daemon_status",
            lambda root: {"running": False},
        )
        monkeypatch.setattr(
            ensure.daemon, "daemon_process_alive", lambda state_dir: False
        )
        monkeypatch.setattr(
            ensure.admission,
            "candidate_admission_status",
            lambda root: {
                "last_admitted_generation": "sha256:same",
                "last_admitted_materialization_ok": True,
                "no_admitted_generation_exists": False,
                "current_working_tree_generation": "sha256:same",
                "current_already_admitted": True,
                "current_unfinalized": False,
                "working_tree_errors": [],
            },
        )
        mat_dir = tmp_path / ".gtkb-state" / "dispatcher-generations" / "sha256-same"
        (mat_dir / "scripts").mkdir(parents=True)
        (mat_dir / "scripts" / "gtkb_dispatcher_daemon.py").write_text("# test")
        monkeypatch.setattr(
            ensure.admission,
            "read_last_admitted",
            lambda root: {
                "generation": "sha256:same",
                "materialization_dir": str(mat_dir),
            },
        )
        monkeypatch.setattr(
            ensure.daemon,
            "dispatch_quiescence",
            lambda root: {"known": True, "live_worker_count": 0, "live_document_lease_count": 0},
        )
        monkeypatch.setattr(
            ensure.daemon, "read_generation_handoff_request", lambda root: None
        )
        monkeypatch.setattr(
            ensure.daemon, "clear_generation_handoff_request", lambda root: None
        )
        monkeypatch.setattr(
            ensure.daemon,
            "current_runtime_generation",
            lambda root: {"generation": "sha256:same"},
        )

        def fake_spawn(root, interval):
            return 99999

        monkeypatch.setattr(ensure, "_spawn_detached_daemon", fake_spawn)
        monkeypatch.setattr(
            ensure,
            "_wait_for_successor_generation",
            lambda root, expected: {
                "running": True,
                "pid_provenance_verified": True,
                "loaded_generation": expected,
                "current_generation": expected,
                "generation_match": True,
                "lock": {"pid": 99999},
            },
        )

        result = ensure.ensure_daemon_running(tmp_path, 30)
        assert result.get("admission") == "current_already_admitted"
