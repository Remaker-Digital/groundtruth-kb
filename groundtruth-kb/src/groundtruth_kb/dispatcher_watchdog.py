# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Windows scheduled-task control for the GT-KB harness storm watchdog.

The storm watchdog remains a separate resilience task from the dispatcher daemon
and its supervisor. This module gives it the same governed ``gt`` control
surface as the supervisor without merging their runtimes.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_TASK_NAME = "GTKB-HarnessStormWatchdog"
INSTALL_SCRIPT = "scripts/install_storm_watchdog_task.ps1"
WATCHDOG_LAUNCHER = "scripts/ops/harness_storm_watchdog_launcher.py"
WATCHDOG_SCRIPT = "scripts/ops/harness_storm_watchdog.ps1"


class DispatcherWatchdogError(RuntimeError):
    """Raised when a watchdog scheduled-task operation fails."""


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name != "nt":
        return kwargs
    kwargs["creationflags"] = int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
    startupinfo_cls = getattr(subprocess, "STARTUPINFO", None)
    if startupinfo_cls is not None:
        startupinfo = startupinfo_cls()
        startupinfo.dwFlags |= int(getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001))
        startupinfo.wShowWindow = int(getattr(subprocess, "SW_HIDE", 0))
        kwargs["startupinfo"] = startupinfo
    return kwargs


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
        **_no_window_subprocess_kwargs(),
    )


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _powershell_json(command: str) -> Any:
    proc = _run_powershell(command)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherWatchdogError(detail or f"PowerShell failed (exit {proc.returncode})")
    raw = (proc.stdout or "").strip()
    if not raw:
        return None
    return json.loads(raw)


def collect_watchdog_status(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
) -> dict[str, Any]:
    """Return machine-readable watchdog scheduled-task state for Windows hosts."""
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
        "uses_launcher_script": False,
        "watchdog_script_present": False,
        "healthy": False,
        "findings": [],
    }
    from groundtruth_kb.dispatcher_disable_guard import disable_guard_status

    payload["disable_guard"] = disable_guard_status(root, task_name=task_name)
    if os.name != "nt":
        payload["findings"].append("storm watchdog is Windows-only; non-Windows hosts skip scheduled-task control")
        return payload

    launcher_path = root / WATCHDOG_LAUNCHER.replace("/", os.sep)
    if not launcher_path.is_file():
        payload["findings"].append(f"missing watchdog launcher: {launcher_path.as_posix()}")
    watchdog_path = root / WATCHDOG_SCRIPT.replace("/", os.sep)
    payload["watchdog_script_present"] = watchdog_path.is_file()
    if not payload["watchdog_script_present"]:
        payload["findings"].append(f"missing watchdog script: {watchdog_path.as_posix()}")

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
    except (DispatcherWatchdogError, json.JSONDecodeError) as exc:
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
    payload["uses_launcher_script"] = (
        WATCHDOG_LAUNCHER.replace("/", "\\") in arguments or WATCHDOG_LAUNCHER in arguments
    )

    if not payload["enabled"]:
        payload["findings"].append(f"scheduled task state is {state!r}; expected Ready or Running")
    if not payload["uses_pythonw"]:
        payload["findings"].append("scheduled task does not launch via pythonw.exe")
    if not payload["uses_launcher_script"]:
        payload["findings"].append(f"scheduled task does not invoke {WATCHDOG_LAUNCHER}")
    if payload["hidden"] is False:
        payload["findings"].append("scheduled task is not hidden")

    payload["healthy"] = (
        payload["registered"]
        and payload["enabled"]
        and payload["hidden"] is True
        and payload["uses_pythonw"]
        and payload["uses_launcher_script"]
        and payload["watchdog_script_present"]
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
        raise DispatcherWatchdogError("storm watchdog install is Windows-only")
    script = _script_path(project_root, script_name)
    if not script.is_file():
        raise DispatcherWatchdogError(f"missing script: {script.as_posix()}")
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
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        **_no_window_subprocess_kwargs(),
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherWatchdogError(detail or f"{script_name} failed (exit {proc.returncode})")
    return {
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "dry_run": dry_run,
        "task_name": task_name,
    }


def install_watchdog(
    project_root: Path,
    *,
    task_name: str = DEFAULT_TASK_NAME,
    interval_minutes: int = 1,
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
        ],
    )
    if not dry_run:
        enable_watchdog(task_name=task_name)
    result["action"] = "install"
    result["status"] = collect_watchdog_status(project_root, task_name=task_name)
    return result


def enable_watchdog(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherWatchdogError("storm watchdog enable is Windows-only")
    proc = _run_powershell(f"Enable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherWatchdogError(detail or f"Enable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "enable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def disable_watchdog(*, task_name: str = DEFAULT_TASK_NAME) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherWatchdogError("storm watchdog disable is Windows-only")
    proc = _run_powershell(f"Disable-ScheduledTask -TaskName {_ps_quote(task_name)} | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherWatchdogError(detail or f"Disable-ScheduledTask failed (exit {proc.returncode})")
    return {"action": "disable", "task_name": task_name, "stdout": (proc.stdout or "").strip()}


def uninstall_watchdog(*, task_name: str = DEFAULT_TASK_NAME, dry_run: bool = False) -> dict[str, Any]:
    if os.name != "nt":
        raise DispatcherWatchdogError("storm watchdog uninstall is Windows-only")
    if dry_run:
        return {
            "action": "uninstall",
            "task_name": task_name,
            "dry_run": True,
            "stdout": f"WOULD UNREGISTER TaskName={task_name}",
        }
    proc = _run_powershell(f"Unregister-ScheduledTask -TaskName {_ps_quote(task_name)} -Confirm:$false | Out-Null")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise DispatcherWatchdogError(detail or f"Unregister-ScheduledTask failed (exit {proc.returncode})")
    return {
        "action": "uninstall",
        "task_name": task_name,
        "dry_run": False,
        "stdout": (proc.stdout or "").strip(),
    }
