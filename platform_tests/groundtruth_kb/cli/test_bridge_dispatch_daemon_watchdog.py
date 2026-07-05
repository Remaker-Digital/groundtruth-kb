# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI tests for storm-watchdog governed control parity (WI-5023)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))


def test_watchdog_group_exposes_supervisor_parity_verbs() -> None:
    from groundtruth_kb.cli import main

    runner = CliRunner()
    env = {"GTKB_PROJECT_ROOT": str(_REPO_ROOT)}

    watchdog = runner.invoke(main, ["bridge", "dispatch", "daemon", "watchdog", "--help"], env=env)
    supervisor = runner.invoke(main, ["bridge", "dispatch", "daemon", "supervisor", "--help"], env=env)

    assert watchdog.exit_code == 0, watchdog.output
    assert supervisor.exit_code == 0, supervisor.output
    for verb in ("status", "install", "enable", "disable", "uninstall"):
        assert verb in watchdog.output
        assert verb in supervisor.output


def test_cli_watchdog_status_json(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.collect_watchdog_status",
        lambda project_root, task_name="GTKB-HarnessStormWatchdog": {
            "healthy": True,
            "registered": True,
            "state": "Ready",
            "findings": [],
        },
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["bridge", "dispatch", "daemon", "watchdog", "status", "--json"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["healthy"] is True


def test_cli_watchdog_control_commands_dispatch(monkeypatch) -> None:
    from groundtruth_kb.cli import main

    calls: list[str] = []
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.install_watchdog",
        lambda project_root, *, task_name, interval_minutes, dry_run: (
            calls.append(f"install:{task_name}:{interval_minutes}:{dry_run}")
            or {"action": "install", "task_name": task_name, "dry_run": dry_run}
        ),
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.enable_watchdog",
        lambda *, task_name: calls.append(f"enable:{task_name}") or {"action": "enable", "task_name": task_name},
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.disable_watchdog",
        lambda *, task_name: calls.append(f"disable:{task_name}") or {"action": "disable", "task_name": task_name},
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.uninstall_watchdog",
        lambda *, task_name, dry_run: (
            calls.append(f"uninstall:{task_name}:{dry_run}")
            or {"action": "uninstall", "task_name": task_name, "dry_run": dry_run}
        ),
    )

    runner = CliRunner()
    env = {"GTKB_PROJECT_ROOT": str(_REPO_ROOT)}
    commands = [
        ["bridge", "dispatch", "daemon", "watchdog", "install", "--task-name", "GTKB-WD-Test", "--dry-run"],
        ["bridge", "dispatch", "daemon", "watchdog", "enable", "--task-name", "GTKB-WD-Test"],
        ["bridge", "dispatch", "daemon", "watchdog", "disable", "--task-name", "GTKB-WD-Test"],
        ["bridge", "dispatch", "daemon", "watchdog", "uninstall", "--task-name", "GTKB-WD-Test", "--dry-run"],
    ]

    for command in commands:
        result = runner.invoke(main, command, env=env)
        assert result.exit_code == 0, result.output

    assert calls == [
        "install:GTKB-WD-Test:1:True",
        "enable:GTKB-WD-Test",
        "disable:GTKB-WD-Test",
        "uninstall:GTKB-WD-Test:True",
    ]
