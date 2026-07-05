# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for storm-watchdog scheduled-task control (WI-5023)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.dispatcher_watchdog import (  # noqa: E402
    _ps_quote,
    _script_path,
    collect_watchdog_status,
    disable_watchdog,
    enable_watchdog,
    install_watchdog,
    uninstall_watchdog,
)


def _write_watchdog_files(root: Path) -> None:
    ops = root / "scripts" / "ops"
    ops.mkdir(parents=True)
    (ops / "harness_storm_watchdog_launcher.py").write_text("# stub\n", encoding="utf-8")
    (ops / "harness_storm_watchdog.ps1").write_text("# stub\n", encoding="utf-8")


def test_collect_watchdog_status_marks_healthy_task(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Ready",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ops\harness_storm_watchdog_launcher.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_powershell", _fake_powershell)
    _write_watchdog_files(tmp_path)

    status = collect_watchdog_status(tmp_path)
    assert status["healthy"] is True
    assert status["enabled"] is True
    assert status["uses_pythonw"] is True
    assert status["uses_launcher_script"] is True
    assert status["findings"] == []


def test_collect_watchdog_status_warns_when_disabled(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Disabled",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ops\harness_storm_watchdog_launcher.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_powershell", _fake_powershell)
    _write_watchdog_files(tmp_path)

    status = collect_watchdog_status(tmp_path)
    assert status["healthy"] is False
    assert any("Disabled" in item for item in status["findings"])


def test_collect_watchdog_status_requires_hidden_task(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Ready",
        "hidden": False,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ops\harness_storm_watchdog_launcher.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_powershell", _fake_powershell)
    _write_watchdog_files(tmp_path)

    status = collect_watchdog_status(tmp_path)
    assert status["healthy"] is False
    assert any("not hidden" in item for item in status["findings"])


def test_collect_watchdog_status_requires_pythonw_and_launcher(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Ready",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe",
        "arguments": r'"E:\GT-KB\scripts\ops\harness_storm_watchdog.ps1"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_powershell", _fake_powershell)
    _write_watchdog_files(tmp_path)

    status = collect_watchdog_status(tmp_path)
    assert status["healthy"] is False
    assert any("pythonw.exe" in item for item in status["findings"])
    assert any("harness_storm_watchdog_launcher.py" in item for item in status["findings"])


def test_install_watchdog_dry_run_invokes_watchdog_installer(tmp_path, monkeypatch):
    calls: list[tuple[str, bool, list[str] | None]] = []

    def _fake_installer(project_root, script_name, *, task_name, dry_run, extra_args=None):
        calls.append((script_name, dry_run, extra_args))
        return {"stdout": "WOULD REGISTER", "stderr": "", "dry_run": dry_run, "task_name": task_name}

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_installer_script", _fake_installer)
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.collect_watchdog_status",
        lambda project_root, task_name="GTKB-HarnessStormWatchdog": {"healthy": False},
    )

    result = install_watchdog(tmp_path, task_name="GTKB-HarnessStormWatchdog-Test", dry_run=True)
    assert result["action"] == "install"
    assert calls == [("scripts/install_storm_watchdog_task.ps1", True, ["-IntervalMinutes", "1"])]


def test_watchdog_control_does_not_touch_supervisor_task(tmp_path, monkeypatch):
    captured: list[tuple[str, str]] = []

    def _fake_installer(project_root, script_name, *, task_name, dry_run, extra_args=None):
        captured.append((script_name, task_name))
        return {"stdout": "WOULD REGISTER", "stderr": "", "dry_run": dry_run, "task_name": task_name}

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_installer_script", _fake_installer)
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.collect_watchdog_status",
        lambda project_root, task_name="GTKB-HarnessStormWatchdog": {"healthy": False},
    )

    install_watchdog(tmp_path, task_name="GTKB-HarnessStormWatchdog-Test", dry_run=True)
    assert captured == [("scripts/install_storm_watchdog_task.ps1", "GTKB-HarnessStormWatchdog-Test")]
    assert all("GTKB-DispatcherDaemon" not in value for pair in captured for value in pair)


def test_enable_disable_uninstall_watchdog_call_powershell(monkeypatch):
    captured: list[str] = []

    def _fake_powershell(command: str, *, timeout: int = 120):
        captured.append(command)

        class _Proc:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog._run_powershell", _fake_powershell)

    enable_watchdog(task_name="GTKB-HarnessStormWatchdog-Test")
    disable_watchdog(task_name="GTKB-HarnessStormWatchdog-Test")
    uninstall_watchdog(task_name="GTKB-HarnessStormWatchdog-Test")

    assert "Enable-ScheduledTask" in captured[0]
    assert "Disable-ScheduledTask" in captured[1]
    assert "Unregister-ScheduledTask" in captured[2]
    assert all("GTKB-HarnessStormWatchdog-Test" in item for item in captured)


def test_uninstall_watchdog_dry_run_skips_powershell(monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "nt")
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog._run_powershell",
        lambda command, *, timeout=120: captured.append(command),
    )

    result = uninstall_watchdog(task_name="GTKB-HarnessStormWatchdog-Test", dry_run=True)
    assert result["stdout"] == "WOULD UNREGISTER TaskName=GTKB-HarnessStormWatchdog-Test"
    assert captured == []


def test_task_name_is_powershell_quoted():
    assert _ps_quote("GTKB-O'Brien") == "'GTKB-O''Brien'"


def test_script_path_accepts_repo_relative_scripts_prefix(tmp_path):
    script = _script_path(tmp_path, "scripts/install_storm_watchdog_task.ps1")
    assert script == tmp_path / "scripts" / "install_storm_watchdog_task.ps1"


def test_collect_watchdog_status_non_windows(tmp_path, monkeypatch):
    monkeypatch.setattr("groundtruth_kb.dispatcher_watchdog.os.name", "posix")
    status = collect_watchdog_status(tmp_path)
    assert status["supported"] is False
    assert status["healthy"] is False


def test_doctor_watchdog_task_reports_healthy(monkeypatch, tmp_path):
    from groundtruth_kb.project import doctor as doctor_mod

    (tmp_path / "harness-state").mkdir()
    (tmp_path / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(doctor_mod.os, "name", "nt")
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.collect_watchdog_status",
        lambda target: {"healthy": True, "registered": True, "findings": []},
    )

    check = doctor_mod._check_dispatcher_daemon_watchdog_task(tmp_path)
    assert check.status == "pass"
    assert "GTKB-HarnessStormWatchdog" in check.message
    assert "pythonw.exe" in check.message


def test_doctor_watchdog_task_warns_with_install_hint(monkeypatch, tmp_path):
    from groundtruth_kb.project import doctor as doctor_mod

    (tmp_path / "harness-state").mkdir()
    (tmp_path / "harness-state" / "bridge-substrate.json").write_text(
        json.dumps({"substrate": "dispatcher_daemon"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(doctor_mod.os, "name", "nt")
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_watchdog.collect_watchdog_status",
        lambda target: {
            "healthy": False,
            "registered": True,
            "findings": ["scheduled task does not launch via pythonw.exe"],
        },
    )

    check = doctor_mod._check_dispatcher_daemon_watchdog_task(tmp_path)
    assert check.status == "warning"
    assert "gt bridge dispatch daemon watchdog install" in check.message


@pytest.mark.skipif(sys.platform != "win32", reason="PowerShell installer is Windows-only")
def test_install_watchdog_task_dry_run_renders_launcher_command() -> None:
    install = _REPO_ROOT / "scripts" / "install_storm_watchdog_task.ps1"
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
            "GTKB-HarnessStormWatchdog-Test-pytest",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "WOULD REGISTER TaskName=GTKB-HarnessStormWatchdog-Test-pytest" in proc.stdout
    assert "harness_storm_watchdog_launcher.py" in proc.stdout
    assert "pythonw.exe" in proc.stdout
