# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI tests for the dispatcher complex command group (WI-5024)."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))


def test_complex_group_exposes_slice_two_verbs() -> None:
    from groundtruth_kb.cli import main

    result = CliRunner().invoke(
        main,
        ["bridge", "dispatch", "complex", "--help"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code == 0, result.output
    for verb in ("status", "health", "enable", "disable", "start", "stop"):
        assert verb in result.output


def test_cli_complex_status_json(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.collect_complex_status",
        lambda project_root, *, supervisor_task_name, watchdog_task_name: {
            "aggregate_status": "healthy",
            "healthy": True,
            "components": {
                "daemon": {"healthy": True, "status": {"running": True}},
                "supervisor": {"healthy": True, "status": {"state": "Ready"}},
                "watchdog": {"healthy": True, "status": {"state": "Ready"}},
            },
            "findings": [],
        },
    )

    result = CliRunner().invoke(
        main,
        ["bridge", "dispatch", "complex", "status", "--json"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["aggregate_status"] == "healthy"
    assert sorted(payload["components"]) == ["daemon", "supervisor", "watchdog"]


def test_cli_complex_health_json_is_lifecycle_health(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.collect_complex_health",
        lambda project_root, *, supervisor_task_name, watchdog_task_name: {
            "aggregate_status": "degraded",
            "health_status": "WARN",
            "healthy": False,
            "components": {
                "daemon": {"healthy": False, "status": {"running": False}},
                "supervisor": {"healthy": True, "status": {"state": "Ready"}},
                "watchdog": {"healthy": True, "status": {"state": "Ready"}},
            },
            "findings": ["daemon: dispatcher daemon is not running"],
        },
    )

    result = CliRunner().invoke(
        main,
        ["bridge", "dispatch", "complex", "health", "--json"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["health_status"] == "WARN"
    assert "selected_by_role" not in payload


def test_cli_complex_enable_disable_dispatch(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    calls: list[str] = []
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.enable_complex",
        lambda *, supervisor_task_name, watchdog_task_name: (
            calls.append(f"enable:{supervisor_task_name}:{watchdog_task_name}")
            or {
                "action": "enable",
                "ok": True,
                "components": {"supervisor": {"ok": True}, "watchdog": {"ok": True}},
            }
        ),
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.disable_complex",
        lambda *, supervisor_task_name, watchdog_task_name: (
            calls.append(f"disable:{supervisor_task_name}:{watchdog_task_name}")
            or {
                "action": "disable",
                "ok": True,
                "components": {"supervisor": {"ok": True}, "watchdog": {"ok": True}},
            }
        ),
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_disable_guard.record_guarded_disable",
        lambda project_root, **kwargs: {"ok": True, "records": [{"task_name": item} for item in kwargs["task_names"]]},
    )
    runner = CliRunner()
    env = {"GTKB_PROJECT_ROOT": str(_REPO_ROOT)}

    enable = runner.invoke(
        main,
        [
            "bridge",
            "dispatch",
            "complex",
            "enable",
            "--supervisor-task-name",
            "GTKB-Supervisor-Test",
            "--watchdog-task-name",
            "GTKB-Watchdog-Test",
        ],
        env=env,
    )
    disable = runner.invoke(
        main,
        [
            "bridge",
            "dispatch",
            "complex",
            "disable",
            "--supervisor-task-name",
            "GTKB-Supervisor-Test",
            "--watchdog-task-name",
            "GTKB-Watchdog-Test",
            "--ttl-seconds",
            "60",
            "--reason",
            "maintenance",
        ],
        env=env,
    )

    assert enable.exit_code == 0, enable.output
    assert disable.exit_code == 0, disable.output
    assert calls == [
        "enable:GTKB-Supervisor-Test:GTKB-Watchdog-Test",
        "disable:GTKB-Supervisor-Test:GTKB-Watchdog-Test",
    ]


def test_cli_complex_disable_refuses_unbounded_disable(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.disable_complex",
        lambda *, supervisor_task_name, watchdog_task_name: (_ for _ in ()).throw(
            AssertionError("disable should be guarded first")
        ),
    )

    result = CliRunner().invoke(
        main,
        ["bridge", "dispatch", "complex", "disable"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code != 0
    assert "requires --ttl-seconds or --owner-quiesce-record" in result.output


def test_cli_complex_start_stop_dispatch_only_daemon(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    calls: list[str] = []
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.start_complex",
        lambda project_root, *, interval: (
            calls.append(f"start:{interval}")
            or {
                "action": "start",
                "ok": True,
                "components": {"daemon": {"ok": True, "pid": 4242}},
                "untouched_components": ["supervisor", "watchdog"],
            }
        ),
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_complex.stop_complex",
        lambda project_root: (
            calls.append("stop")
            or {
                "action": "stop",
                "ok": True,
                "components": {"daemon": {"ok": True, "candidate_pids": [4242]}},
                "untouched_components": ["supervisor", "watchdog"],
            }
        ),
    )
    runner = CliRunner()
    env = {"GTKB_PROJECT_ROOT": str(_REPO_ROOT)}

    start = runner.invoke(main, ["bridge", "dispatch", "complex", "start", "--interval", "7"], env=env)
    stop = runner.invoke(main, ["bridge", "dispatch", "complex", "stop"], env=env)

    assert start.exit_code == 0, start.output
    assert stop.exit_code == 0, stop.output
    assert calls == ["start:7", "stop"]


def _write_watchdog_heartbeat(project_root: Path, *, heartbeat_at: dt.datetime) -> None:
    from groundtruth_kb.dispatcher_complex import WATCHDOG_HEARTBEAT_RELATIVE_PATH

    heartbeat_path = project_root / WATCHDOG_HEARTBEAT_RELATIVE_PATH
    heartbeat_path.parent.mkdir(parents=True)
    heartbeat_path.write_text(
        f"{heartbeat_at.isoformat()} codex=11 family=24 wrapped=6 threshold=15 mode=liveness-aware",
        encoding="utf-8",
    )


def test_watchdog_heartbeat_threshold_process_count_does_not_override_freshness(tmp_path: Path) -> None:
    from groundtruth_kb.dispatcher_complex import (
        DEFAULT_HEARTBEAT_STALE_SECONDS,
        _read_watchdog_heartbeat,
    )

    now = dt.datetime(2026, 7, 6, 12, 0, tzinfo=dt.UTC)
    _write_watchdog_heartbeat(tmp_path, heartbeat_at=now - dt.timedelta(seconds=120))

    payload = _read_watchdog_heartbeat(tmp_path, now=now)

    assert payload["fresh"] is True
    assert payload["finding"] is None
    assert payload["stale_seconds"] == DEFAULT_HEARTBEAT_STALE_SECONDS
    assert payload["age_seconds"] == 120


def test_watchdog_heartbeat_above_freshness_window_stays_stale(tmp_path: Path) -> None:
    from groundtruth_kb.dispatcher_complex import (
        DEFAULT_HEARTBEAT_STALE_SECONDS,
        _read_watchdog_heartbeat,
    )

    now = dt.datetime(2026, 7, 6, 12, 0, tzinfo=dt.UTC)
    _write_watchdog_heartbeat(
        tmp_path,
        heartbeat_at=now - dt.timedelta(seconds=DEFAULT_HEARTBEAT_STALE_SECONDS + 1),
    )

    payload = _read_watchdog_heartbeat(tmp_path, now=now)

    assert payload["fresh"] is False
    assert payload["stale_seconds"] == DEFAULT_HEARTBEAT_STALE_SECONDS
    assert payload["finding"] == "watchdog heartbeat is stale (181.0s > 180.0s)"
