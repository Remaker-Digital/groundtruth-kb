# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for dispatcher supervisor status and CLI (WI-4937)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.dispatcher_supervisor import (  # noqa: E402
    _ps_quote,
    _script_path,
    collect_supervisor_status,
    disable_supervisor,
    enable_supervisor,
    install_supervisor,
    uninstall_supervisor,
)


def test_collect_supervisor_status_marks_healthy_task(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Ready",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ensure_dispatcher_daemon.py" --project-root "E:\GT-KB"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ensure_dispatcher_daemon.py").write_text("# stub\n", encoding="utf-8")

    status = collect_supervisor_status(tmp_path)
    assert status["healthy"] is True
    assert status["enabled"] is True
    assert status["uses_pythonw"] is True
    assert status["findings"] == []


def test_collect_supervisor_status_accepts_running_task(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Running",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ensure_dispatcher_daemon.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ensure_dispatcher_daemon.py").write_text("# stub\n", encoding="utf-8")

    status = collect_supervisor_status(tmp_path)
    assert status["healthy"] is True
    assert status["enabled"] is True


def test_collect_supervisor_status_warns_when_disabled(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Disabled",
        "hidden": True,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ensure_dispatcher_daemon.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ensure_dispatcher_daemon.py").write_text("# stub\n", encoding="utf-8")

    status = collect_supervisor_status(tmp_path)
    assert status["healthy"] is False
    assert any("Disabled" in item for item in status["findings"])


def test_collect_supervisor_status_requires_hidden_task(tmp_path, monkeypatch):
    payload = {
        "registered": True,
        "state": "Ready",
        "hidden": False,
        "execute": r"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe",
        "arguments": r'"E:\GT-KB\scripts\ensure_dispatcher_daemon.py"',
    }

    def _fake_powershell(command: str):
        class _Proc:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ensure_dispatcher_daemon.py").write_text("# stub\n", encoding="utf-8")

    status = collect_supervisor_status(tmp_path)
    assert status["healthy"] is False
    assert any("not hidden" in item for item in status["findings"])


def test_install_supervisor_dry_run_invokes_installer(tmp_path, monkeypatch):
    calls: list[tuple[str, bool]] = []

    def _fake_installer(project_root, script_name, *, task_name, dry_run, extra_args=None):
        calls.append((script_name, dry_run))
        return {"stdout": "WOULD REGISTER", "stderr": "", "dry_run": dry_run, "task_name": task_name}

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_installer_script", _fake_installer)
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.collect_supervisor_status",
        lambda project_root, task_name="GTKB-DispatcherDaemon": {"healthy": False},
    )

    result = install_supervisor(tmp_path, dry_run=True)
    assert result["action"] == "install"
    assert calls == [("scripts/install_dispatcher_daemon_task.ps1", True)]


def test_script_path_accepts_repo_relative_scripts_prefix(tmp_path):
    script = _script_path(tmp_path, "scripts/install_dispatcher_daemon_task.ps1")
    assert script == tmp_path / "scripts" / "install_dispatcher_daemon_task.ps1"


def test_enable_supervisor_calls_powershell(monkeypatch):
    captured: list[str] = []

    def _fake_powershell(command: str, *, timeout: int = 120):
        captured.append(command)

        class _Proc:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    enable_supervisor()
    assert "Enable-ScheduledTask" in captured[0]


def test_disable_supervisor_calls_powershell(monkeypatch):
    captured: list[str] = []

    def _fake_powershell(command: str, *, timeout: int = 120):
        captured.append(command)

        class _Proc:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Proc()

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_powershell", _fake_powershell)
    disable_supervisor()
    assert "Disable-ScheduledTask" in captured[0]


def test_task_name_is_powershell_quoted():
    assert _ps_quote("GTKB-O'Brien") == "'GTKB-O''Brien'"


def test_uninstall_supervisor_dry_run_invokes_installer(tmp_path, monkeypatch):
    calls: list[tuple[str, bool]] = []

    def _fake_installer(project_root, script_name, *, task_name, dry_run, extra_args=None):
        calls.append((script_name, dry_run))
        return {"stdout": "WOULD UNREGISTER", "stderr": "", "dry_run": dry_run, "task_name": task_name}

    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor.os.name", "nt")
    monkeypatch.setattr("groundtruth_kb.dispatcher_supervisor._run_installer_script", _fake_installer)
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.collect_supervisor_status",
        lambda project_root, task_name="GTKB-DispatcherDaemon": {"healthy": False},
    )

    result = uninstall_supervisor(tmp_path, dry_run=True)
    assert result["action"] == "uninstall"
    assert calls == [("scripts/uninstall_dispatcher_daemon_task.ps1", True)]


def test_cli_supervisor_status_json(monkeypatch):
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.collect_supervisor_status",
        lambda project_root, task_name="GTKB-DispatcherDaemon": {
            "healthy": True,
            "registered": True,
            "state": "Ready",
            "findings": [],
        },
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["bridge", "dispatch", "daemon", "supervisor", "status", "--json"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["healthy"] is True


def test_cli_supervisor_disable_refuses_unbounded_disable(monkeypatch):
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.disable_supervisor",
        lambda *, task_name: (_ for _ in ()).throw(AssertionError("disable should be guarded first")),
    )

    result = CliRunner().invoke(
        main,
        ["bridge", "dispatch", "daemon", "supervisor", "disable"],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code != 0
    assert "requires --ttl-seconds or --owner-quiesce-record" in result.output


def test_cli_supervisor_disable_accepts_ttl_guard(monkeypatch):
    from groundtruth_kb.cli import main

    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_supervisor.disable_supervisor",
        lambda *, task_name: {"action": "disable", "task_name": task_name},
    )
    monkeypatch.setattr(
        "groundtruth_kb.dispatcher_disable_guard.record_guarded_disable",
        lambda project_root, **kwargs: {"ok": True, "records": [{"task_name": kwargs["task_names"][0]}]},
    )

    result = CliRunner().invoke(
        main,
        [
            "bridge",
            "dispatch",
            "daemon",
            "supervisor",
            "disable",
            "--ttl-seconds",
            "60",
            "--reason",
            "maintenance",
            "--json",
        ],
        env={"GTKB_PROJECT_ROOT": str(_REPO_ROOT)},
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["disable_guard"]["ok"] is True
    assert payload["disable_guard"]["records"][0]["task_name"] == "GTKB-DispatcherDaemon"
