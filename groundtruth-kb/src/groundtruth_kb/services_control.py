"""GT-KB's local services as one inventory with status, start and stop (owner rulings D58, D59: GT-KB Home controls).

The Home UI's controls call only `gt services`; this module holds the inventory and the Windows mechanics:

- authority   The native domain service on its configured URL, kept running by the logon task GTKB-DomainService (at
              logon and every five minutes). Stopping disables that task first, so the stop holds, then ends only the
              positively identified launcher of this installation (its kill-on-close job ends the service). Starting
              re-enables the task, runs it and waits for readiness.
- home        The GT-KB Home server (infrastructure/deepseek-web/home.py), kept running by the logon task GTKB-Home.
              Stopping disables that task and stops the server; the Home UI itself never offers this action.
- dashboard   The local dashboard (refresh service and Grafana), started and stopped through `gt dashboard`.
- ollama      The local Ollama server started by the logon task GTKB-Ollama-Serve.
- postgresql  The Windows service gtkb-postgresql. Starting or stopping it usually needs an administrator; a refusal
              is reported, never worked around.

Every mechanism runs a fixed argument vector through an injectable runner, so tests never touch real services.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

Runner = Callable[[list[str], float], subprocess.CompletedProcess[str]]
SERVICES = ("authority", "home", "dashboard", "ollama", "postgresql")
AUTHORITY_TASK = "GTKB-DomainService"
HOME_TASK = "GTKB-Home"
OLLAMA_TASK = "GTKB-Ollama-Serve"
POSTGRESQL_SERVICE = "gtkb-postgresql"
DASHBOARD_HEALTH = "http://127.0.0.1:8766/health"
OLLAMA_VERSION = "http://127.0.0.1:11434/api/version"
READY_SECONDS = 60


class ServiceControlError(RuntimeError):
    pass


@dataclass
class ServiceState:
    name: str
    state: str  # running | stopped | unknown
    detail: str
    can_start: bool
    can_stop: bool


def default_runner(argv: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def _powershell(runner: Runner, script: str, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    return runner(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], timeout)


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _get_ok(url: str, timeout: float = 5) -> bool:
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=timeout) as response:
            return bool(200 <= response.status < 300)
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _task_state(runner: Runner, task: str) -> str:
    """Scheduled task state: Ready, Running, Disabled, or missing."""
    result = _powershell(runner, f"(Get-ScheduledTask -TaskName {_quote(task)} -ErrorAction SilentlyContinue).State")
    state = (result.stdout or "").strip()
    return state or "missing"


def _set_task(runner: Runner, task: str, *, enabled: bool) -> None:
    verb = "Enable-ScheduledTask" if enabled else "Disable-ScheduledTask"
    result = _powershell(runner, f"{verb} -TaskName {_quote(task)} -ErrorAction Stop | Out-Null")
    if result.returncode != 0:
        raise ServiceControlError(f"{verb} {task} failed: {(result.stderr or result.stdout).strip()[-800:]}")


def _run_task(runner: Runner, task: str) -> None:
    result = _powershell(runner, f"Start-ScheduledTask -TaskName {_quote(task)} -ErrorAction Stop")
    if result.returncode != 0:
        raise ServiceControlError(
            f"Start-ScheduledTask {task} failed: {(result.stderr or result.stdout).strip()[-800:]}"
        )


def _end_processes(runner: Runner, *fragments: str) -> list[int]:
    """End every process tree whose command line contains all fragments; return the PIDs ended."""
    conditions = " -and ".join(f"$_.CommandLine -like {_quote('*' + fragment + '*')}" for fragment in fragments)
    script = (
        f"$targets = Get-CimInstance Win32_Process | Where-Object {{ $_.CommandLine -and {conditions} }}; "
        "foreach ($t in $targets) { taskkill /PID $t.ProcessId /T /F | Out-Null; $t.ProcessId }"
    )
    result = _powershell(runner, script)
    return [int(line) for line in (result.stdout or "").split() if line.strip().isdigit()]


def _wait(predicate: Callable[[], bool], seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(1)
    return predicate()


@dataclass
class Installation:
    root: Path
    authority_url: str
    python: Path

    @property
    def home_script(self) -> Path:
        return self.root / "infrastructure" / "deepseek-web" / "home.py"


def _home(installation: Installation, runner: Runner, action: str) -> dict[str, Any]:
    result = runner([str(installation.python), "-B", str(installation.home_script), action], 180)
    try:
        outcome: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ServiceControlError(
            f"home.py {action} gave no JSON: {(result.stderr or result.stdout)[-800:]}"
        ) from error
    return outcome


def status(installation: Installation, runner: Runner = default_runner, only: str | None = None) -> list[ServiceState]:
    selected = [only] if only else list(SERVICES)
    states: list[ServiceState] = []
    for name in selected:
        if name == "authority":
            ready = _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status")
            task = _task_state(runner, AUTHORITY_TASK)
            states.append(
                ServiceState(
                    name,
                    "running" if ready else "stopped",
                    f"{installation.authority_url}; task {task}",
                    can_start=not ready,
                    can_stop=ready,
                )
            )
        elif name == "home":
            report = _home(installation, runner, "status")
            running = bool(report.get("running")) and bool(report.get("live"))
            task = _task_state(runner, HOME_TASK)
            detail = f"127.0.0.1:{report.get('port', 3080)}; task {task}" if running else f"not running; task {task}"
            states.append(
                ServiceState(name, "running" if running else "stopped", detail, can_start=not running, can_stop=running)
            )
        elif name == "dashboard":
            ready = _get_ok(DASHBOARD_HEALTH)
            states.append(
                ServiceState(
                    name, "running" if ready else "stopped", DASHBOARD_HEALTH, can_start=not ready, can_stop=ready
                )
            )
        elif name == "ollama":
            ready = _get_ok(OLLAMA_VERSION)
            task = _task_state(runner, OLLAMA_TASK)
            states.append(
                ServiceState(
                    name,
                    "running" if ready else "stopped",
                    f"127.0.0.1:11434; task {task}",
                    can_start=not ready and task != "missing",
                    can_stop=ready,
                )
            )
        elif name == "postgresql":
            result = _powershell(
                runner, f"(Get-Service -Name {_quote(POSTGRESQL_SERVICE)} -ErrorAction SilentlyContinue).Status"
            )
            value = (result.stdout or "").strip()
            state = {"Running": "running", "Stopped": "stopped"}.get(value, "unknown")
            states.append(
                ServiceState(
                    name,
                    state,
                    f"Windows service {POSTGRESQL_SERVICE}: {value or 'not registered'}",
                    can_start=state == "stopped",
                    can_stop=state == "running",
                )
            )
        else:
            raise ServiceControlError(f"Unknown service {name!r}; known: {', '.join(SERVICES)}")
    return states


def start(installation: Installation, name: str, runner: Runner = default_runner) -> dict[str, Any]:
    if name == "authority":
        _set_task(runner, AUTHORITY_TASK, enabled=True)
        _run_task(runner, AUTHORITY_TASK)
        ready = _wait(lambda: _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status"), READY_SECONDS)
        return {"service": name, "started": ready, "detail": "ready" if ready else "task started; not ready yet"}
    if name == "home":
        if _task_state(runner, HOME_TASK) not in ("missing",):
            _set_task(runner, HOME_TASK, enabled=True)
        report = _home(installation, runner, "start")
        return {"service": name, "started": bool(report.get("ok")), "detail": report}
    if name == "dashboard":
        result = runner([str(installation.python), "-m", "groundtruth_kb", "dashboard", "start", "--json"], 300)
        return {"service": name, "started": result.returncode == 0, "detail": (result.stdout or result.stderr)[-800:]}
    if name == "ollama":
        _set_task(runner, OLLAMA_TASK, enabled=True)
        _run_task(runner, OLLAMA_TASK)
        ready = _wait(lambda: _get_ok(OLLAMA_VERSION), READY_SECONDS)
        return {"service": name, "started": ready, "detail": "ready" if ready else "task started; not ready yet"}
    if name == "postgresql":
        result = _powershell(runner, f"Start-Service -Name {_quote(POSTGRESQL_SERVICE)} -ErrorAction Stop")
        if result.returncode != 0:
            raise ServiceControlError(
                f"Starting {POSTGRESQL_SERVICE} failed (an administrator may be required): "
                f"{(result.stderr or result.stdout).strip()[-600:]}"
            )
        return {"service": name, "started": True, "detail": "started"}
    raise ServiceControlError(f"Unknown service {name!r}; known: {', '.join(SERVICES)}")


def stop(installation: Installation, name: str, runner: Runner = default_runner) -> dict[str, Any]:
    if name == "authority":
        _set_task(runner, AUTHORITY_TASK, enabled=False)
        launcher = str(installation.root / "infrastructure" / "postgresql" / "domain_service_launcher.py")
        ended = _end_processes(runner, launcher, "--root")
        stopped = _wait(lambda: not _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status"), 30)
        return {"service": name, "stopped": stopped, "ended_pids": ended, "detail": f"task {AUTHORITY_TASK} disabled"}
    if name == "home":
        if _task_state(runner, HOME_TASK) not in ("missing",):
            _set_task(runner, HOME_TASK, enabled=False)
        report = _home(installation, runner, "stop")
        return {"service": name, "stopped": bool(report.get("ok")), "detail": report}
    if name == "dashboard":
        result = runner([str(installation.python), "-m", "groundtruth_kb", "dashboard", "stop", "--json"], 120)
        return {"service": name, "stopped": result.returncode == 0, "detail": (result.stdout or result.stderr)[-800:]}
    if name == "ollama":
        _set_task(runner, OLLAMA_TASK, enabled=False)
        ended = _end_processes(runner, "ollama", "serve")
        stopped = _wait(lambda: not _get_ok(OLLAMA_VERSION), 30)
        return {"service": name, "stopped": stopped, "ended_pids": ended, "detail": f"task {OLLAMA_TASK} disabled"}
    if name == "postgresql":
        result = _powershell(runner, f"Stop-Service -Name {_quote(POSTGRESQL_SERVICE)} -ErrorAction Stop")
        if result.returncode != 0:
            raise ServiceControlError(
                f"Stopping {POSTGRESQL_SERVICE} failed (an administrator may be required): "
                f"{(result.stderr or result.stdout).strip()[-600:]}"
            )
        return {"service": name, "stopped": True, "detail": "stopped; the authority is unavailable until it restarts"}
    raise ServiceControlError(f"Unknown service {name!r}; known: {', '.join(SERVICES)}")


def as_json(states: list[ServiceState]) -> list[dict[str, Any]]:
    return [asdict(state) for state in states]


def installation_from_config(project_root: Path, authority_url: str | None) -> Installation:
    python = project_root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    return Installation(
        root=project_root,
        authority_url=authority_url or "http://127.0.0.1:8765",
        python=python if python.is_file() else Path(sys.executable),
    )
