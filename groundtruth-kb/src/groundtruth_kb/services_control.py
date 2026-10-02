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

c123 (batch design WP3 3.3): the task and service names are machine-wide, so every row is scoped by the rule the
registration scripts apply, ignoring case. A task belongs to this installation when its action names this
installation's launcher, and the PostgreSQL service when its PathName names this installation's data directory. The
Ollama task names no installation, so it belongs to the installation that owns GTKB-Home. A dashboard that answers is
this installation's only when this root's launch record exists. A row this installation does not own keeps its
observed state, offers no start or stop and names its owner, and start and stop refuse it before changing anything.
home.py is always this root's own; the GTKB-Home task is enabled or disabled only when this installation owns it.

Every mechanism runs a fixed argument vector through an injectable runner, so tests never touch real services.
"""

from __future__ import annotations

import json
import os
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


def _read_registration(result: subprocess.CompletedProcess[str], key: str) -> tuple[str, str]:
    """c123 (batch design WP3 3.3): (state, named path text) from one read; no output means missing."""
    text = (result.stdout or "").strip()
    if not text:
        return "missing", ""
    try:
        found = json.loads(text)
    except json.JSONDecodeError:
        found = None
    if not isinstance(found, dict):
        return "unknown", ""
    return str(found.get("state") or "unknown"), str(found.get(key) or "")


def _task(runner: Runner, task: str) -> tuple[str, str]:
    """c123 (batch design WP3 3.3): a scheduled task's state (Ready, Running, Disabled, or missing) and action text.

    One call reads both. The action text is each action's Execute and Arguments, as the registration scripts read it.
    """
    script = (
        f"$t = Get-ScheduledTask -TaskName {_quote(task)} -ErrorAction SilentlyContinue; "
        "if ($t) { @{ state = [string]$t.State; "
        "action = (($t.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' ') } "
        "| ConvertTo-Json -Compress }"
    )
    return _read_registration(_powershell(runner, script), "action")


def _service(runner: Runner, service: str) -> tuple[str, str]:
    """c123 (batch design WP3 3.3): a Windows service's state (Running, Stopped, ..., or missing) and PathName."""
    query = _quote(f"Name = '{service}'")
    script = (
        f"$s = Get-CimInstance Win32_Service -Filter {query} -ErrorAction SilentlyContinue; "
        "if ($s) { @{ state = [string]$s.State; path = [string]$s.PathName } | ConvertTo-Json -Compress }"
    )
    return _read_registration(_powershell(runner, script), "path")


def _owner(named: str, own: Path) -> str | None:
    """c123 (batch design WP3 3.3): None when a task or service is this installation's, otherwise who holds it.

    The registration scripts' rule, ignoring case: a task is an installation's when its action names that
    installation's launcher, and the PostgreSQL service when its PathName names that installation's data directory.
    The holder is the other registration's action text or PathName, or "" when nothing is registered.
    """
    if named and os.path.abspath(own).lower() in named.lower():
        return None
    return named


def _not_owned(owner: str) -> str:
    """c123 (batch design WP3 3.3): how the detail of a row this installation does not own ends."""
    return (f"; registered by another installation: {owner}" if owner else "") + "; status only"


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

    # c123 (batch design WP3 3.3): the paths that this installation's authority task and PostgreSQL service name.
    @property
    def authority_launcher(self) -> Path:
        return self.root / "infrastructure" / "postgresql" / "domain_service_launcher.py"

    @property
    def postgresql_data(self) -> Path:
        return self.root / "infrastructure" / "postgresql" / "data"


def _require_owned(installation: Installation, runner: Runner, name: str) -> None:
    """c123 (batch design WP3 3.3): refuse, before anything changes, to start or stop another installation's row."""
    if name == "authority":
        registration = f"task {AUTHORITY_TASK}"
        owner = _owner(_task(runner, AUTHORITY_TASK)[1], installation.authority_launcher)
    elif name == "ollama":
        # c123 (batch design WP3 3.3): the Ollama task names only ollama.exe, so Ollama follows GTKB-Home (the
        # design's owner decision 4).
        registration = f"task {OLLAMA_TASK} names no installation, and task {HOME_TASK}"
        owner = _owner(_task(runner, HOME_TASK)[1], installation.home_script)
    else:
        registration = f"Windows service {POSTGRESQL_SERVICE}"
        owner = _owner(_service(runner, POSTGRESQL_SERVICE)[1], installation.postgresql_data)
    if owner is not None:
        held = f"is registered by another installation ({owner})" if owner else "is not registered"
        raise ServiceControlError(f"{registration} {held}; this installation does not start or stop {name}")


def _dashboard_launch_record(installation: Installation) -> Path:
    """c123 (batch design WP3 3.3): this root's dashboard launch record, under the runtime root `gt dashboard` uses."""
    from groundtruth_kb.dashboard import LAUNCH_RECORD_NAME
    from groundtruth_kb.dashboard_link import default_dashboard_runtime_root

    return default_dashboard_runtime_root(installation.root) / LAUNCH_RECORD_NAME


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
            task, action = _task(runner, AUTHORITY_TASK)
            owner = _owner(action, installation.authority_launcher)
            states.append(
                ServiceState(
                    name,
                    "running" if ready else "stopped",
                    f"{installation.authority_url}; task {task}" + ("" if owner is None else _not_owned(owner)),
                    can_start=owner is None and not ready,
                    can_stop=owner is None and ready,
                )
            )
        elif name == "home":
            report = _home(installation, runner, "status")
            running = bool(report.get("running")) and bool(report.get("live"))
            task, action = _task(runner, HOME_TASK)
            detail = f"127.0.0.1:{report.get('port', 3080)}; task {task}" if running else f"not running; task {task}"
            # c123 (batch design WP3 3.3): home.py is this root's own, so its actions stay; another installation's
            # GTKB-Home task is named here, and start and stop leave it alone.
            owner = _owner(action, installation.home_script)
            if owner:
                detail += f"; registered by another installation: {owner}"
            states.append(
                ServiceState(name, "running" if running else "stopped", detail, can_start=not running, can_stop=running)
            )
        elif name == "dashboard":
            ready = _get_ok(DASHBOARD_HEALTH)
            record = _dashboard_launch_record(installation)
            # c123 (batch design WP3 3.3): `gt dashboard` acts only on this root's own launch, so a dashboard that
            # answers without this root's launch record is another installation's.
            if ready and not record.is_file():
                state = "unknown"
                detail = f"{DASHBOARD_HEALTH} answers without this installation's launch record {record}; status only"
            else:
                state = "running" if ready else "stopped"
                detail = DASHBOARD_HEALTH
            states.append(ServiceState(name, state, detail, can_start=not ready, can_stop=state == "running"))
        elif name == "ollama":
            ready = _get_ok(OLLAMA_VERSION)
            task, _ = _task(runner, OLLAMA_TASK)
            # c123 (batch design WP3 3.3): the Ollama task names only ollama.exe, so Ollama is this installation's
            # only when GTKB-Home is (the design's owner decision 4).
            owner = _owner(_task(runner, HOME_TASK)[1], installation.home_script)
            detail = f"127.0.0.1:11434; task {task}"
            if owner is not None:
                detail += f"; controlled by the installation that owns task {HOME_TASK}" + _not_owned(owner)
            states.append(
                ServiceState(
                    name,
                    "running" if ready else "stopped",
                    detail,
                    can_start=owner is None and not ready and task != "missing",
                    can_stop=owner is None and ready,
                )
            )
        elif name == "postgresql":
            value, path = _service(runner, POSTGRESQL_SERVICE)
            state = {"Running": "running", "Stopped": "stopped"}.get(value, "unknown")
            owner = _owner(path, installation.postgresql_data)
            detail = f"Windows service {POSTGRESQL_SERVICE}: {'not registered' if value == 'missing' else value}"
            states.append(
                ServiceState(
                    name,
                    state,
                    detail + ("" if owner is None else _not_owned(owner)),
                    can_start=owner is None and state == "stopped",
                    can_stop=owner is None and state == "running",
                )
            )
        else:
            raise ServiceControlError(f"Unknown service {name!r}; known: {', '.join(SERVICES)}")
    return states


def start(installation: Installation, name: str, runner: Runner = default_runner) -> dict[str, Any]:
    if name == "authority":
        _require_owned(installation, runner, name)
        _set_task(runner, AUTHORITY_TASK, enabled=True)
        _run_task(runner, AUTHORITY_TASK)
        ready = _wait(lambda: _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status"), READY_SECONDS)
        return {"service": name, "started": ready, "detail": "ready" if ready else "task started; not ready yet"}
    if name == "home":
        # c123 (batch design WP3 3.3): the task is resumed only when this installation registered it.
        if _owner(_task(runner, HOME_TASK)[1], installation.home_script) is None:
            _set_task(runner, HOME_TASK, enabled=True)
        report = _home(installation, runner, "start")
        return {"service": name, "started": bool(report.get("ok")), "detail": report}
    if name == "dashboard":
        result = runner([str(installation.python), "-m", "groundtruth_kb", "dashboard", "start", "--json"], 300)
        return {"service": name, "started": result.returncode == 0, "detail": (result.stdout or result.stderr)[-800:]}
    if name == "ollama":
        _require_owned(installation, runner, name)
        _set_task(runner, OLLAMA_TASK, enabled=True)
        _run_task(runner, OLLAMA_TASK)
        ready = _wait(lambda: _get_ok(OLLAMA_VERSION), READY_SECONDS)
        return {"service": name, "started": ready, "detail": "ready" if ready else "task started; not ready yet"}
    if name == "postgresql":
        _require_owned(installation, runner, name)
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
        _require_owned(installation, runner, name)
        _set_task(runner, AUTHORITY_TASK, enabled=False)
        ended = _end_processes(runner, str(installation.authority_launcher), "--root")
        stopped = _wait(lambda: not _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status"), 30)
        return {"service": name, "stopped": stopped, "ended_pids": ended, "detail": f"task {AUTHORITY_TASK} disabled"}
    if name == "home":
        # c123 (batch design WP3 3.3): the task is paused only when this installation registered it.
        if _owner(_task(runner, HOME_TASK)[1], installation.home_script) is None:
            _set_task(runner, HOME_TASK, enabled=False)
        report = _home(installation, runner, "stop")
        return {"service": name, "stopped": bool(report.get("ok")), "detail": report}
    if name == "dashboard":
        result = runner([str(installation.python), "-m", "groundtruth_kb", "dashboard", "stop", "--json"], 120)
        return {"service": name, "stopped": result.returncode == 0, "detail": (result.stdout or result.stderr)[-800:]}
    if name == "ollama":
        _require_owned(installation, runner, name)
        _set_task(runner, OLLAMA_TASK, enabled=False)
        ended = _end_processes(runner, "ollama", "serve")
        stopped = _wait(lambda: not _get_ok(OLLAMA_VERSION), 30)
        return {"service": name, "stopped": stopped, "ended_pids": ended, "detail": f"task {OLLAMA_TASK} disabled"}
    if name == "postgresql":
        _require_owned(installation, runner, name)
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
