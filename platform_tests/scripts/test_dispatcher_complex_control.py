# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for dispatcher complex aggregation and controls (WI-5024)."""

from __future__ import annotations

import sys
import types
from datetime import UTC, datetime
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import dispatcher_complex as complex_mod  # noqa: E402
from groundtruth_kb.dispatcher_watchdog import DispatcherWatchdogError  # noqa: E402


def _daemon_module(tmp_path: Path, *, running: bool = True) -> types.SimpleNamespace:
    state_dir = tmp_path / ".gtkb-state" / "dispatcher-daemon"
    state_dir.mkdir(parents=True, exist_ok=True)
    status = {"running": running, "mode": "live"}
    if running:
        status["heartbeat_at"] = datetime.now(UTC).isoformat()
        status["heartbeat_age_seconds"] = 0.0
    return types.SimpleNamespace(
        PID_FILENAME="daemon.pid",
        daemon_state_dir=lambda project_root: state_dir,
        collect_daemon_status=lambda project_root: dict(status),
        read_daemon_status=lambda project_root: {"running": running},
        daemon_process_alive=lambda _state_dir: running,
        _heartbeat_stale_seconds=lambda: 180.0,
    )


def test_collect_complex_status_rolls_up_component_payloads(tmp_path, monkeypatch):
    monkeypatch.setattr(
        complex_mod,
        "collect_supervisor_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "task_name": task_name},
    )
    monkeypatch.setattr(
        complex_mod,
        "collect_watchdog_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "task_name": task_name},
    )

    status = complex_mod.collect_complex_status(
        tmp_path,
        supervisor_task_name="GTKB-Supervisor-Test",
        watchdog_task_name="GTKB-Watchdog-Test",
        daemon_module=_daemon_module(tmp_path, running=True),
    )

    assert status["aggregate_status"] == "healthy"
    assert status["healthy"] is True
    assert status["components"]["daemon"]["kind"] == "process"
    assert status["components"]["supervisor"]["status"]["task_name"] == "GTKB-Supervisor-Test"
    assert status["components"]["watchdog"]["status"]["task_name"] == "GTKB-Watchdog-Test"


def test_collect_complex_health_reports_lifecycle_findings(tmp_path, monkeypatch):
    monkeypatch.setattr(
        complex_mod,
        "collect_supervisor_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "findings": []},
    )
    monkeypatch.setattr(
        complex_mod,
        "collect_watchdog_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "findings": []},
    )

    health = complex_mod.collect_complex_health(tmp_path, daemon_module=_daemon_module(tmp_path, running=False))

    assert health["health_status"] == "WARN"
    assert health["aggregate_status"] == "degraded"
    assert "WARN daemon: dispatcher daemon is not running" in health["findings"]


def test_collect_complex_health_escalates_failed_task_state(tmp_path, monkeypatch):
    monkeypatch.setattr(
        complex_mod,
        "collect_supervisor_status",
        lambda project_root, *, task_name: {
            "healthy": False,
            "registered": False,
            "findings": ["scheduled task 'GTKB-Supervisor-Test' is not registered"],
        },
    )
    monkeypatch.setattr(
        complex_mod,
        "collect_watchdog_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "findings": []},
    )

    health = complex_mod.collect_complex_health(
        tmp_path,
        supervisor_task_name="GTKB-Supervisor-Test",
        daemon_module=_daemon_module(tmp_path, running=True),
    )

    assert health["health_status"] == "FAIL"
    assert health["components"]["supervisor"]["severity"] == "FAIL"
    assert any("FAIL supervisor: scheduled task" in finding for finding in health["findings"])


def test_collect_complex_health_warns_on_stale_watchdog_heartbeat(tmp_path, monkeypatch):
    heartbeat_dir = tmp_path / ".gtkb-state" / "ops"
    heartbeat_dir.mkdir(parents=True)
    (heartbeat_dir / "storm-watchdog-heartbeat.txt").write_text(
        "2000-01-01T00:00:00+00:00 codex=0 family=0 threshold=15\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        complex_mod,
        "collect_supervisor_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "findings": []},
    )
    monkeypatch.setattr(
        complex_mod,
        "collect_watchdog_status",
        lambda project_root, *, task_name: {"healthy": True, "state": "Ready", "findings": []},
    )

    health = complex_mod.collect_complex_health(tmp_path, daemon_module=_daemon_module(tmp_path, running=True))

    assert health["health_status"] == "WARN"
    assert health["components"]["watchdog"]["severity"] == "WARN"
    assert health["components"]["watchdog"]["heartbeat"]["fresh"] is False
    assert any("WARN watchdog: watchdog heartbeat is stale" in finding for finding in health["findings"])


def test_enable_complex_fans_out_in_order_and_keeps_error_payload(monkeypatch):
    calls: list[str] = []

    def _enable_supervisor(*, task_name):
        calls.append(f"supervisor:{task_name}")
        return {"action": "enable", "task_name": task_name}

    def _enable_watchdog(*, task_name):
        calls.append(f"watchdog:{task_name}")
        raise DispatcherWatchdogError("watchdog unavailable")

    monkeypatch.setattr(complex_mod, "enable_supervisor", _enable_supervisor)
    monkeypatch.setattr(complex_mod, "enable_watchdog", _enable_watchdog)

    result = complex_mod.enable_complex(
        supervisor_task_name="GTKB-Supervisor-Test",
        watchdog_task_name="GTKB-Watchdog-Test",
    )

    assert result["ok"] is False
    assert result["order"] == ["supervisor", "watchdog"]
    assert calls == ["supervisor:GTKB-Supervisor-Test", "watchdog:GTKB-Watchdog-Test"]
    assert result["components"]["supervisor"]["ok"] is True
    assert result["components"]["watchdog"]["ok"] is False
    assert "watchdog unavailable" in result["components"]["watchdog"]["error"]


def test_disable_complex_fans_out_only_to_scheduled_task_controls(monkeypatch):
    calls: list[str] = []

    monkeypatch.setattr(
        complex_mod,
        "disable_supervisor",
        lambda *, task_name: calls.append(f"supervisor:{task_name}") or {"action": "disable"},
    )
    monkeypatch.setattr(
        complex_mod,
        "disable_watchdog",
        lambda *, task_name: calls.append(f"watchdog:{task_name}") or {"action": "disable"},
    )

    result = complex_mod.disable_complex(
        supervisor_task_name="GTKB-Supervisor-Test",
        watchdog_task_name="GTKB-Watchdog-Test",
    )

    assert result["ok"] is True
    assert calls == ["supervisor:GTKB-Supervisor-Test", "watchdog:GTKB-Watchdog-Test"]
    assert sorted(result["components"]) == ["supervisor", "watchdog"]


def test_start_complex_spawns_daemon_without_touching_task_controls(tmp_path, monkeypatch):
    captured: dict[str, object] = {}
    daemon = _daemon_module(tmp_path, running=False)

    monkeypatch.setattr(complex_mod, "enable_supervisor", lambda **kwargs: pytest.fail("supervisor touched"))
    monkeypatch.setattr(complex_mod, "enable_watchdog", lambda **kwargs: pytest.fail("watchdog touched"))

    class _FakePopen:
        def __init__(self, args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            self.pid = 4242

    result = complex_mod.start_complex(
        tmp_path,
        interval=9,
        daemon_module=daemon,
        popen_factory=_FakePopen,
        python_executable=sys.executable,
    )

    assert result["ok"] is True
    assert result["components"]["daemon"]["pid"] == 4242
    assert result["untouched_components"] == ["supervisor", "watchdog"]
    assert "--tick-seconds" in captured["args"]
    assert captured["args"][captured["args"].index("--tick-seconds") + 1] == "9"
    assert captured["kwargs"]["stdin"] == complex_mod.subprocess.DEVNULL


def test_stop_complex_terminates_daemon_without_touching_task_controls(tmp_path, monkeypatch):
    state_dir = tmp_path / ".gtkb-state" / "dispatcher-daemon"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "daemon.pid").write_text("4242\n", encoding="utf-8")
    terminated: list[int] = []
    released: list[bool] = []
    cleared: list[Path] = []
    daemon = types.SimpleNamespace(
        PID_FILENAME="daemon.pid",
        daemon_state_dir=lambda project_root: state_dir,
        daemon_pid_provenance_verified=lambda _state_dir: True,
        daemon_pid_matches_legacy_loop=lambda _state_dir, pid: False,
        matching_daemon_loop_pids=lambda _state_dir: [],
        _reap_dispatched_workers=lambda project_root: 2,
        _read_pid_create_time_sidecar=lambda _state_dir: None,
        _pid_create_time_matches=lambda pid, expected: False,
        _clear_daemon_pid_record=lambda _state_dir: cleared.append(_state_dir) or (_state_dir / "daemon.pid").unlink(),
        release_daemon_lock=lambda _state_dir, *, force: released.append(force),
    )

    monkeypatch.setattr(complex_mod, "disable_supervisor", lambda **kwargs: pytest.fail("supervisor touched"))
    monkeypatch.setattr(complex_mod, "disable_watchdog", lambda **kwargs: pytest.fail("watchdog touched"))

    result = complex_mod.stop_complex(tmp_path, daemon_module=daemon, terminate_fn=terminated.append)

    assert result["ok"] is True
    assert result["components"]["daemon"]["candidate_pids"] == [4242]
    assert result["components"]["daemon"]["reaped_workers"] == 2
    assert result["untouched_components"] == ["supervisor", "watchdog"]
    assert terminated == [4242]
    assert released == [True]
    assert cleared == [state_dir]
