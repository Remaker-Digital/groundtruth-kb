# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Windows scheduled-task supervisor for the GT-KB dispatcher daemon (WI-4937).

Wraps the WI-4882 PowerShell installers with a governed CLI surface and
machine-readable status probes. The supervisor uses ``pythonw.exe`` and
``scripts/ensure_dispatcher_daemon.py`` so the daemon survives IDE/terminal
closure without a visible console window.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_TASK_NAME = "GTKB-DispatcherDaemon"
INSTALL_SCRIPT = "scripts/install_dispatcher_daemon_task.ps1"
UNINSTALL_SCRIPT = "scripts/uninstall_dispatcher_daemon_task.ps1"
ENSURE_SCRIPT = "scripts/ensure_dispatcher_daemon.py"


class DispatcherSupervisorError(RuntimeError):
    """Raised when a supervisor operation fails."""


def _scripts_dir(project_root: Path) -> Path:
    return project_root.resolve() / "scripts"


def _script_path(project_root: Path, script_name: str) -> Path:
    script = Path(script_name.replace("/", os.sep))
    if script.is_absolute():
        return script
    if script.parts and script.parts[0].lower() == "scripts":
        return project_root.resolve() / script
    return _scripts_dir(project_root) / script


def _run_powershell(command: str, *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _powershell_json(command: str) -> Any:
    proc = _run_powershell(command)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherSupervisorError(detail or f"PowerShell failed (exit {proc.returncode})")
    raw = (proc.stdout or "").strip()
    if not raw:
        return None
    return json.loads(raw)


def collect_supervisor_status(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
) -> dict[str, Any]:
    """Return machine-readable supervisor/task state for Windows hosts."""
    root = project_root.resolve()
    payload: dict[str, Any] = {
        "platform": os.name,
        "task_name": task_name,
        "project_root": str(root),
        "supported": os.name == "nt",
        "registered": False,
        "state": None,
        "enabled": False,
        "hidden": None,
        "execute": None,
        "arguments": None,
        "uses_pythonw": False,
        "uses_ensure_script": False,
        "healthy": False,
        "findings": [],
    }
    from groundtruth_kb.dispatcher_disable_guard import disable_guard_status

    payload["disable_guard"] = disable_guard_status(root, task_name=task_name)
    if os.name != "nt":
        payload["findings"].append("supervisor is Windows-only; non-Windows hosts use manual daemon lifecycle")
        return payload

    ensure_path = root / ENSURE_SCRIPT.replace("/", os.sep)
    if not ensure_path.is_file():
        payload["findings"].append(f"missing ensure script: {ensure_path.as_posix()}")

    quoted_task_name = _ps_quote(task_name)
    query = (
        f"$t = Get-ScheduledTask -TaskName {quoted_task_name} -ErrorAction SilentlyContinue; "
        "if ($null -eq $t) { @{ registered = $false } | ConvertTo-Json -Compress } "
        "else { "
        "@{ registered = $true; state = [string]$t.State; "
        "hidden = [bool]$t.Settings.Hidden; "
        "execute = [string]$t.Actions[0].Execute; "
        "arguments = [string]$t.Actions[0].Arguments } | ConvertTo-Json -Compress }"
    )
    try:
        doc = _powershell_json(query)
    except (DispatcherSupervisorError, json.JSONDecodeError) as exc:
        payload["findings"].append(f"scheduled-task probe failed: {exc}")
        return payload

    if not isinstance(doc, dict) or not doc.get("registered"):
        payload["findings"].append(f"scheduled task {task_name!r} is not registered")
        return payload

    payload["registered"] = True
    payload["state"] = doc.get("state")
    payload["hidden"] = doc.get("hidden")
    payload["execute"] = doc.get("execute")
    payload["arguments"] = doc.get("arguments")
    state = str(payload["state"] or "").strip()
    payload["enabled"] = state.lower() in {"ready", "running"}
    execute = str(payload["execute"] or "")
    arguments = str(payload["arguments"] or "")
    payload["uses_pythonw"] = execute.lower().endswith("pythonw.exe")
    payload["uses_ensure_script"] = ENSURE_SCRIPT.replace("/", "\\") in arguments or ENSURE_SCRIPT in arguments

    if not payload["enabled"]:
        payload["findings"].append(f"scheduled task state is {state!r}; expected Ready or Running")
    if not payload["uses_pythonw"]:
        payload["findings"].append("scheduled task does not launch via pythonw.exe")
    if not payload["uses_ensure_script"]:
        payload["findings"].append(f"scheduled task does not invoke {ENSURE_SCRIPT}")
    if payload["hidden"] is False:
        payload["findings"].append("scheduled task is not hidden")

    payload["healthy"] = (
        payload["registered"]
        and payload["enabled"]
        and payload["hidden"] is True
        and payload["uses_pythonw"]
        and payload["uses_ensure_script"]
    )
    return payload


def _run_installer_script(
    project_root: Path,
    script_name: str,
    *,
    task_name: str,
    dry_run: bool,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherSupervisorError("dispatcher supervisor install/uninstall is Windows-only")
    script = _script_path(project_root, script_name)
    if not script.is_file():
        raise DispatcherSupervisorError(f"missing script: {script.as_posix()}")
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-ProjectRoot",
        str(project_root.resolve()),
        "-TaskName",
        task_name,
    ]
    if dry_run:
        cmd.append("-DryRun")
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherSupervisorError(detail or f"{script_name} failed (exit {proc.returncode})")
    return {
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "dry_run": dry_run,
        "task_name": task_name,
    }


def install_supervisor(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
    interval_minutes: int = 1,
    daemon_tick_seconds: int = 30,
    dry_run: bool = False,
) -> dict[str, Any]:
    result = _run_installer_script(
        project_root,
        INSTALL_SCRIPT,
        task_name=task_name,
        dry_run=dry_run,
        extra_args=[
            "-IntervalMinutes",
            str(interval_minutes),
            "-DaemonTickSeconds",
            str(daemon_tick_seconds),
        ],
    )
    if not dry_run:
        enable_supervisor(task_name=task_name)
    result["action"] = "install"
    result["status"] = collect_supervisor_status(project_root, task_name=task_name)
    return result


def enable_supervisor(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherSupervisorError("dispatcher supervisor enable is Windows-only")
    proc = _run_powershell(f"Enable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherSupervisorError(detail or f"Enable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "enable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def disable_supervisor(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherSupervisorError("dispatcher supervisor disable is Windows-only")
    proc = _run_powershell(f"Disable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherSupervisorError(detail or f"Disable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "disable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def uninstall_supervisor(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
    dry_run: bool = False,
) -> dict[str, Any]:
    result = _run_installer_script(
        project_root,
        UNINSTALL_SCRIPT,
        task_name=task_name,
        dry_run=dry_run,
    )
    result["action"] = "uninstall"
    result["status"] = collect_supervisor_status(project_root, task_name=task_name)
    return result
