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

Aggregate start/stop discovers installed controllers before changing anything. It includes optional Dashboard/Ollama
when installed, even when down; an installed component without a supported controller refuses preflight. The
aggregate captures initial process/task states, uses dependency order, and reports partial failure and bounded
compensation explicitly. Its scope is the installation's default controller paths, excluding custom Dashboard
runtimes, one-shot maintenance and qualification services. Individual authority/Ollama stops share its PID/creation/
executable identity proof and never stop processes selected by substring.

An optional before_effect callback checks the bounded invocation before each task, process and controller mutation,
including compensation. Initial state and attempted changes stay local to this call. The module retains no permission;
the caller supplies fresh authority checks, including the exact last-live check before a foundational shutdown.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    import ctypes

    from groundtruth_kb.job_containment import ProcessIdentity
from urllib.parse import urlsplit

Runner = Callable[[list[str], float], subprocess.CompletedProcess[str]]
BeforeEffect = Callable[[str, list[str], list[dict[str, str]], str], Any]
OnComplete = Callable[[], Any]
SERVICES = ("authority", "home", "dashboard", "ollama", "postgresql")
AUTHORITY_TASK = "GTKB-DomainService"
HOME_TASK = "GTKB-Home"
OLLAMA_TASK = "GTKB-Ollama-Serve"
POSTGRESQL_SERVICE = "gtkb-postgresql"
DASHBOARD_HEALTH = "http://127.0.0.1:8766/health"
OLLAMA_VERSION = "http://127.0.0.1:11434/api/version"
READY_SECONDS = 60
# Dependencies start first; Home starts last because it exposes and uses the other controllers.
START_ORDER = ("postgresql", "authority", "ollama", "dashboard", "home")


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


def _get_health(url: str, timeout: float = 5) -> tuple[bool, dict[str, Any] | None]:
    """Read the existing health payload once, retaining an answering endpoint with unusable JSON as unknown."""
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                return False, None
            try:
                payload = json.load(response)
            except (OSError, ValueError):
                return True, None
            return True, payload if isinstance(payload, dict) else None
    except (urllib.error.URLError, OSError, ValueError):
        return False, None


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
    config_path: Path | None = None

    @property
    def dashboard_config_path(self) -> Path:
        return self.config_path if self.config_path is not None else self.root / "groundtruth.toml"

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
    if not isinstance(outcome, dict):
        raise ServiceControlError(f"home.py {action} gave no JSON object")
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


def start(
    installation: Installation,
    name: str,
    runner: Runner = default_runner,
    *,
    before_effect: BeforeEffect | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    if name == "all":
        return start_all(installation, runner, before_effect=before_effect, on_complete=on_complete)
    if before_effect is not None or on_complete is not None:
        return _controlled_single(installation, name, "start", runner, before_effect, on_complete=on_complete)
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
        result = runner(
            [
                str(installation.python),
                "-m",
                "groundtruth_kb",
                "--config",
                str(installation.dashboard_config_path),
                "dashboard",
                "start",
                "--json",
            ],
            300,
        )
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


def stop(
    installation: Installation,
    name: str,
    runner: Runner = default_runner,
    *,
    before_effect: BeforeEffect | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    if name == "all":
        return stop_all(installation, runner, before_effect=before_effect, on_complete=on_complete)
    if before_effect is not None or on_complete is not None:
        return _controlled_single(installation, name, "stop", runner, before_effect, on_complete=on_complete)
    if name == "authority":
        _require_owned(installation, runner, name)
        controller, processes = _task_stop_plan(installation, runner, name)
        _set_task(runner, AUTHORITY_TASK, enabled=False)
        _end_identified(runner, processes)
        stopped = _wait(lambda: not _get_ok(f"{installation.authority_url.rstrip('/')}/v1/status"), 30)
        return {
            "service": name,
            "stopped": stopped,
            "ended_pids": [item["pid"] for item in processes],
            "detail": f"task {controller.task} disabled",
        }
    if name == "home":
        before = _home_stop_state(installation, runner)
        # c123 (batch design WP3 3.3): the task is paused only when this installation registered it.
        with _hold_identified(before.processes) as held_processes:
            if _owner(_task(runner, HOME_TASK)[1], installation.home_script) is None:
                _set_task(runner, HOME_TASK, enabled=False)
            report = _home(installation, runner, "stop")
            unconfirmed = [
                expected["pid"]
                for expected, (kernel, handle) in zip(before.processes, held_processes, strict=True)
                if kernel.WaitForSingleObject(handle, 5000) != 0
            ]
            stopped = bool(report.get("ok")) and not unconfirmed
            if unconfirmed:
                report = {
                    **report,
                    "stop_confirmed": False,
                    "unconfirmed_pids": unconfirmed,
                    "stop_error": "The identified Home process exit was not confirmed",
                }
        return {"service": name, "stopped": stopped, "detail": report}
    if name == "dashboard":
        result = runner(
            [
                str(installation.python),
                "-m",
                "groundtruth_kb",
                "--config",
                str(installation.dashboard_config_path),
                "dashboard",
                "stop",
                "--json",
            ],
            120,
        )
        return {"service": name, "stopped": result.returncode == 0, "detail": (result.stdout or result.stderr)[-800:]}
    if name == "ollama":
        _require_owned(installation, runner, name)
        controller, processes = _task_stop_plan(installation, runner, name)
        _set_task(runner, OLLAMA_TASK, enabled=False)
        _end_identified(runner, processes)
        stopped = _wait(lambda: not _get_ok(OLLAMA_VERSION), 30)
        return {
            "service": name,
            "stopped": stopped,
            "ended_pids": [item["pid"] for item in processes],
            "detail": f"task {controller.task} disabled",
        }
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


@dataclass(frozen=True)
class _Controller:
    """One existing installation controller, held only for this invocation."""

    name: str
    task: str | None = None
    executable: str = ""
    arguments: tuple[str, ...] = ()
    registration: str = ""


@dataclass(frozen=True)
class _Observed:
    running: bool
    ready: bool
    enabled: bool | None = None
    processes: tuple[ProcessIdentity, ...] = ()


def _read_json(result: subprocess.CompletedProcess[str], subject: str) -> Any:
    if result.returncode:
        raise ServiceControlError(f"Cannot inspect {subject}: {(result.stderr or result.stdout)[-800:]}")
    try:
        return json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError) as error:
        raise ServiceControlError(f"Cannot inspect {subject}: no valid JSON") from error


def _path_equal(left: str | Path, right: str | Path) -> bool:
    return os.path.abspath(left).casefold() == os.path.abspath(right).casefold()


def _arguments(command: str) -> tuple[str, ...]:
    """Use Windows' own command-line parser, rather than substring ownership matching."""
    import ctypes
    from ctypes import wintypes

    shell = ctypes.WinDLL("shell32", use_last_error=True)
    shell.CommandLineToArgvW.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int))
    shell.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.LocalFree.argtypes = (wintypes.HLOCAL,)
    kernel.LocalFree.restype = wintypes.HLOCAL
    count = ctypes.c_int()
    values = shell.CommandLineToArgvW(command, ctypes.byref(count))
    if not values:
        raise ServiceControlError("Cannot parse the registered Windows command line")
    try:
        return tuple(values[index] for index in range(count.value))
    finally:
        kernel.LocalFree(ctypes.cast(values, wintypes.HLOCAL))


def _task_definition(runner: Runner, task: str) -> dict[str, Any] | None:
    script = (
        f"try {{ $t = Get-ScheduledTask -TaskName {_quote(task)} -ErrorAction Stop; "
        "@{ enabled = [bool]$t.Settings.Enabled; actions = @($t.Actions | ForEach-Object { "
        "@{ execute = [string]$_.Execute; arguments = [string]$_.Arguments } }) } | ConvertTo-Json -Depth 4 -Compress "
        "} catch { if ($_.CategoryInfo.Category -eq 'ObjectNotFound') { '{\"missing\":true}' } else { throw } }"
    )
    found = _read_json(_powershell(runner, script), f"task {task}")
    if isinstance(found, dict) and found.get("missing") is True:
        return None
    if not (
        isinstance(found, dict)
        and type(found.get("enabled")) is bool
        and isinstance(found.get("actions"), list)
        and len(found["actions"]) == 1
        and isinstance(found["actions"][0], dict)
        and isinstance(found["actions"][0].get("execute"), str)
        and isinstance(found["actions"][0].get("arguments"), str)
    ):
        raise ServiceControlError(f"Task {task} has no unambiguous supported action")
    return found


def _service_definition(runner: Runner) -> dict[str, Any] | None:
    query = _quote(f"Name = '{POSTGRESQL_SERVICE}'")
    script = (
        "$ErrorActionPreference = 'Stop'; "
        f"$s = Get-CimInstance Win32_Service -Filter {query}; "
        "if ($s) { $p = if ($s.ProcessId) { Get-CimInstance Win32_Process -Filter ('ProcessId=' + $s.ProcessId) }; "
        "@{ state = [string]$s.State; path = [string]$s.PathName; pid = [int]$s.ProcessId; "
        "created_at = if ($p) { [string]$p.CreationDate.ToFileTimeUtc() } else { '' } } "
        "| ConvertTo-Json -Compress } else { '{\"missing\":true}' }"
    )
    found = _read_json(_powershell(runner, script), f"service {POSTGRESQL_SERVICE}")
    if isinstance(found, dict) and found.get("missing") is True:
        return None
    if not isinstance(found, dict) or not isinstance(found.get("path"), str):
        raise ServiceControlError(f"Cannot inspect service {POSTGRESQL_SERVICE}")
    return found


def _task_controller(name: str, task: str, definition: dict[str, Any], expected: tuple[str, ...]) -> _Controller:
    action = definition["actions"][0]
    arguments = _arguments("task " + action["arguments"])[1:]
    if tuple(value.casefold() for value in arguments) != tuple(value.casefold() for value in expected):
        raise ServiceControlError(f"Task {task} does not name this installation's exact supported {name} action")
    executable = action["execute"]
    if not Path(executable).is_file():
        raise ServiceControlError(f"Task {task} names an executable that is not installed: {executable}")
    return _Controller(name, task, executable, arguments)


def _process_rows(runner: Runner) -> list[dict[str, Any]]:
    script = (
        "$ErrorActionPreference = 'Stop'; $rows = @(Get-CimInstance Win32_Process | ForEach-Object { "
        "@{ pid = [int]$_.ProcessId; executable = [string]$_.ExecutablePath; command = [string]$_.CommandLine; "
        "created_at = if ($_.CreationDate) { [string]$_.CreationDate.ToFileTimeUtc() } else { '' } } }); "
        "ConvertTo-Json -InputObject $rows -Compress"
    )
    found = _read_json(_powershell(runner, script), "live process identities")
    if not isinstance(found, list) or not all(isinstance(row, dict) for row in found):
        raise ServiceControlError("Cannot inspect live process identities")
    return found


def _identity(row: dict[str, Any], runner: Runner = default_runner) -> ProcessIdentity | None:
    from groundtruth_kb import job_containment

    pid = row.get("pid")
    if type(pid) is not int or pid <= 0:
        raise ServiceControlError("Process inventory has no valid process identifier")
    with job_containment.windows_process(pid) as (identity, held):
        if identity is None:
            return None
        if held is None or not _path_equal(identity["executable"], row.get("executable", "")):
            raise ServiceControlError(f"Process {pid} changed creation/executable identity while being inspected")
        # Re-read argv and the first-read CIM creation stamp while the native process object is held. Compare
        # CIM stamps to CIM stamps; their precision can differ from the native FILETIME used in stop identities.
        script = (
            "$ErrorActionPreference = 'Stop'; "
            f"$p = Get-CimInstance Win32_Process -Filter 'ProcessId={pid}'; "
            "if ($p) { @{ executable = [string]$p.ExecutablePath; command = [string]$p.CommandLine; "
            "created_at = [string]$p.CreationDate.ToFileTimeUtc() } | ConvertTo-Json -Compress } else { 'null' }"
        )
        fresh = _read_json(_powershell(runner, script), f"held process {pid}")
        if fresh is None:
            return None
        if not isinstance(fresh, dict) or (
            not _path_equal(fresh.get("executable", ""), identity["executable"])
            or not row.get("created_at")
            or fresh.get("created_at") != row["created_at"]
            or ("command" in row and fresh.get("command") != row["command"])
        ):
            raise ServiceControlError(f"Process {pid} changed creation/executable identity while being inspected")
        return identity


def _python_images(installation: Installation) -> set[str]:
    scripts = installation.root / "groundtruth-kb" / ".venv" / "Scripts"
    candidates = [scripts / "python.exe", scripts / "pythonw.exe"]
    # A Windows venv redirector's child uses the base interpreter. Its installed venv names that interpreter.
    config = scripts.parent / "pyvenv.cfg"
    if config.is_file():
        for line in config.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == "home":
                candidates.extend(Path(value.strip()) / name for name in ("python.exe", "pythonw.exe"))
    return {os.path.abspath(path).casefold() for path in candidates if path.is_file()}


def _task_processes(
    installation: Installation, controller: _Controller, rows: list[dict[str, Any]], runner: Runner
) -> tuple[ProcessIdentity, ...]:
    images = (
        _python_images(installation)
        if controller.name == "authority"
        else {os.path.abspath(controller.executable).casefold()}
    )
    expected = tuple(value.casefold() for value in controller.arguments)
    selected = []
    for row in rows:
        command = row.get("command") or ""
        arguments = _arguments(command) if command else ()
        matches = tuple(value.casefold() for value in arguments[1:]) == expected
        if not matches:
            if (
                controller.name == "ollama"
                and Path(row.get("executable") or "").name.casefold() == "ollama.exe"
                and (not command or (len(arguments) > 1 and arguments[1].casefold() == "serve"))
            ):
                raise ServiceControlError("An Ollama server has no identity matching the registered controller")
            continue
        if os.path.abspath(row.get("executable") or "").casefold() not in images:
            raise ServiceControlError(f"The {controller.name} command is running under an unrecognized executable")
        identity = _identity(row, runner)
        if identity is not None:
            selected.append(identity)
    return tuple(sorted(selected, key=lambda item: item["pid"]))


def _installed_ollama(runner: Runner) -> list[str]:
    """The executable locations the existing Ollama task installer supports, independent of HTTP state."""
    script = (
        "$ErrorActionPreference = 'Stop'; $paths = @(); "
        "$command = Get-Command 'ollama.exe' -ErrorAction SilentlyContinue; "
        "if ($command -and $command.Source) { $paths += $command.Source }; "
        "if ($env:LOCALAPPDATA) { $candidate = Join-Path $env:LOCALAPPDATA 'Programs\\Ollama\\ollama.exe'; "
        "if (Test-Path -LiteralPath $candidate -PathType Leaf) "
        "{ $paths += (Resolve-Path -LiteralPath $candidate).Path } }; "
        "ConvertTo-Json -InputObject @($paths | Select-Object -Unique) -Compress"
    )
    found = _read_json(_powershell(runner, script), "installed Ollama executable")
    if not isinstance(found, list) or not all(isinstance(path, str) for path in found):
        raise ServiceControlError("Cannot determine whether Ollama is installed")
    return found


def _require_home_installation(installation: Installation) -> None:
    source = installation.home_script.parent
    launcher = source / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
    try:
        release = json.loads((source / "release.json").read_text(encoding="utf-8"))
        installed = json.loads((source / "installed.json").read_text(encoding="utf-8"))
        matches = all(installed.get(key) == release[key] for key in ("lockfile_sha256", "version"))
    except (OSError, ValueError, AttributeError, KeyError, TypeError) as error:
        raise ServiceControlError("Home's existing installation manifests require inspection") from error
    if not installation.home_script.is_file() or not launcher.is_file() or not matches:
        raise ServiceControlError("Home is not installed at its pinned release; use its existing install controller")


def _postgresql_controller(installation: Installation, runner: Runner) -> _Controller:
    service = _service_definition(runner)
    if service is None:
        raise ServiceControlError(f"Required installation controller service {POSTGRESQL_SERVICE} is not registered")
    argv = _arguments(service["path"])
    try:
        data = argv[argv.index("-D") + 1]
        service_name = argv[argv.index("-N") + 1]
        binary = Path(argv[0]).resolve()
        binary.relative_to((installation.root / "infrastructure" / "postgresql" / "runtime").resolve())
    except (IndexError, ValueError) as error:
        raise ServiceControlError(
            "PostgreSQL service does not name this installation's supported controller"
        ) from error
    if not (
        _path_equal(data, installation.postgresql_data)
        and service_name == POSTGRESQL_SERVICE
        and "runservice" in argv
        and binary.name.casefold() == "pg_ctl.exe"
        and binary.is_file()
    ):
        raise ServiceControlError("PostgreSQL service does not name this installation's installed data/controller")
    return _Controller("postgresql", executable=str(binary), registration=service["path"])


def _inventory(installation: Installation, runner: Runner) -> tuple[list[_Controller], dict[str, str]]:
    """Discover installed controllers, including optional components while they are down. No registration is written."""
    if sys.platform != "win32":
        raise ServiceControlError("Aggregate installed-service control is supported only on Windows")
    definitions = {task: _task_definition(runner, task) for task in (AUTHORITY_TASK, HOME_TASK, OLLAMA_TASK)}
    for task in (AUTHORITY_TASK, HOME_TASK):
        if definitions[task] is None:
            raise ServiceControlError(f"Required installation controller task {task} is not registered")
    pythonw = installation.root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
    port = str(urlsplit(installation.authority_url).port or 80)
    authority = _task_controller(
        "authority",
        AUTHORITY_TASK,
        cast(dict[str, Any], definitions[AUTHORITY_TASK]),
        (str(installation.authority_launcher), "--root", str(installation.root), "--port", port),
    )
    home = _task_controller(
        "home", HOME_TASK, cast(dict[str, Any], definitions[HOME_TASK]), ("-B", str(installation.home_script), "start")
    )
    if not all(_path_equal(controller.executable, pythonw) for controller in (authority, home)):
        raise ServiceControlError("Authority/Home task executable is not this installation's registered pythonw.exe")
    if not installation.authority_launcher.is_file():
        raise ServiceControlError("Authority's registered launcher is not installed")
    _require_home_installation(installation)
    controllers = [_postgresql_controller(installation, runner), authority, home]
    excluded = {
        "maintenance-backup": "One-shot maintenance task; outside persistent service controls",
        "qualification-services": "Ports 8770 and 55434 belong to qualification, outside installed service controls",
    }
    rows = _process_rows(runner)
    ollama = definitions[OLLAMA_TASK]
    if ollama is not None:
        controller = _task_controller("ollama", OLLAMA_TASK, ollama, ("serve",))
        if Path(controller.executable).name.casefold() != "ollama.exe":
            raise ServiceControlError("Ollama task does not name an installed ollama.exe")
        controllers.append(controller)
    else:
        if (
            _installed_ollama(runner)
            or _get_ok(OLLAMA_VERSION)
            or any(Path(row.get("executable") or "").name.casefold() == "ollama.exe" for row in rows)
        ):
            raise ServiceControlError(
                "Ollama is installed or present, but its supported task is missing; cannot include it safely"
            )
        excluded["ollama"] = "Absent from the existing task installer's executable locations and live process inventory"
    from groundtruth_kb.dashboard import find_grafana_server

    grafana_home = installation.root / ".groundtruth" / "tools" / "grafana"
    binary = find_grafana_server(grafana_home)
    if binary is not None:
        controllers.append(_Controller("dashboard", executable=str(binary)))
    else:
        if grafana_home.exists() or _dashboard_launch_record(installation).exists() or _get_ok(DASHBOARD_HEALTH):
            raise ServiceControlError("Dashboard installation/runtime is present without one supported Grafana binary")
        excluded["dashboard"] = (
            "No Grafana installation or launch in this installation's default dashboard controller paths"
        )
    return sorted(controllers, key=lambda controller: START_ORDER.index(controller.name)), excluded


def _observe(installation: Installation, controller: _Controller, runner: Runner) -> _Observed:
    """Revalidate controller identity and read process identity separately from readiness."""
    enabled = None
    if controller.task is not None:
        definition = _task_definition(runner, controller.task)
        if definition is None:
            raise ServiceControlError(f"Task {controller.task} disappeared")
        current_controller = _task_controller(controller.name, controller.task, definition, controller.arguments)
        if not _path_equal(current_controller.executable, controller.executable):
            raise ServiceControlError(f"Task {controller.task} changed installation controller")
        enabled = definition["enabled"]
    if controller.name == "postgresql":
        service = _service_definition(runner)
        if (
            service is None
            or service["path"] != controller.registration
            or service.get("state") not in ("Running", "Stopped")
        ):
            raise ServiceControlError("PostgreSQL controller changed or has an unresolved transition")
        if service["state"] == "Running":
            identity = _identity(
                {
                    "pid": service.get("pid"),
                    "executable": controller.executable,
                    "created_at": service.get("created_at"),
                },
                runner,
            )
            if identity is None:
                raise ServiceControlError("Running PostgreSQL has no positively identified service process")
            return _Observed(True, True, processes=(identity,))
        return _Observed(False, False)
    rows = _process_rows(runner)
    if controller.name in ("authority", "ollama"):
        task_processes = _task_processes(installation, controller, rows, runner)
        url = (
            f"{installation.authority_url.rstrip('/')}/v1/status" if controller.name == "authority" else OLLAMA_VERSION
        )
        ready = _get_ok(url)
        if ready and not task_processes:
            raise ServiceControlError(
                f"{controller.name} answers without this installation's identified server process"
            )
        return _Observed(bool(task_processes), ready, enabled, task_processes)
    if controller.name == "home":
        report = _home(installation, runner, "status")
        if not report.get("ok"):
            raise ServiceControlError(f"Home status refused: {report.get('error', 'unknown reason')}")
        launcher = str(installation.home_script.parent / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js")
        candidates = [row for row in rows if row.get("command") and launcher.casefold() in row["command"].casefold()]
        processes: list[ProcessIdentity] = []
        for row in candidates:
            argv = _arguments(row["command"])
            if len(argv) < 4 or not _path_equal(argv[1], launcher) or argv[2:4] != ("--profile", "gtkb"):
                raise ServiceControlError("Home has an unrecognized command for this installation's launcher")
            if Path(row.get("executable") or "").name.casefold() != "node.exe":
                raise ServiceControlError("Home's launcher is running under an unrecognized executable")
            identity = _identity(row, runner)
            if identity is not None:
                processes.append(identity)
        if bool(processes) != bool(report.get("running")) or (
            processes and {item["pid"] for item in processes} != {report.get("pid")}
        ):
            raise ServiceControlError("Home process inventory and its existing launch record disagree")
        if not processes and _get_ok(f"http://127.0.0.1:{report.get('port', 3080)}/favicon.svg"):
            raise ServiceControlError("Home port answers without this installation's identified Home process")
        return _Observed(
            bool(processes), bool(report.get("live")), enabled, tuple(sorted(processes, key=lambda item: item["pid"]))
        )
    from groundtruth_kb import dashboard, job_containment

    record_path = _dashboard_launch_record(installation)
    record = dashboard._read_launch_record(record_path)
    processes = []
    roles = set()
    row_by_pid = {row.get("pid"): row for row in rows}
    job_name = dashboard._dashboard_job_name(record_path.parent)
    job = dashboard._open_dashboard_job(job_name) if sys.platform == "win32" else None
    try:
        if job is not None and (record is None or record.get("job") != job_name):
            raise ServiceControlError("Dashboard job has no matching installation launch record")
        contained = set(dashboard._job_member_pids(job)) if job is not None else set()
        if contained and (
            record is None
            or record.get("grafana_port") != dashboard.DEFAULT_GRAFANA_PORT
            or record.get("refresh_port") != dashboard.DEFAULT_REFRESH_PORT
            or record.get("interval_seconds") != dashboard.DEFAULT_REFRESH_INTERVAL_MINUTES * 60
            or not isinstance(record.get("config_path"), str)
            or not _path_equal(record["config_path"], installation.dashboard_config_path)
        ):
            raise ServiceControlError("Dashboard live launch settings are custom or unknown; use its owner controller")
        for member in (record or {}).get("members", []):
            current = job_containment.process_identity(member["pid"])
            if current is not None and (current != dashboard._identity_of(member) or member["pid"] not in contained):
                raise ServiceControlError("Dashboard launch record has a reused or uncontained process identity")
        images = _python_images(installation)
        for row in rows:
            argv = _arguments(row["command"]) if row.get("command") else ()
            is_grafana = bool(row.get("executable")) and _path_equal(row["executable"], controller.executable)
            is_refresh = (
                "groundtruth_kb.dashboard_service" in argv
                and str(installation.dashboard_config_path) in argv
                and str(record_path.parent) in argv
                and os.path.abspath(row.get("executable") or "").casefold() in images
            )
            if row.get("pid") not in contained:
                if (is_grafana or is_refresh) and _identity(row, runner) is not None:
                    raise ServiceControlError("Dashboard process is present outside this controller's identified job")
                continue
            if is_refresh:
                expected = (
                    "-m",
                    "groundtruth_kb.dashboard_service",
                    "--config",
                    str(installation.dashboard_config_path),
                    "--db-path",
                    str(record_path.parent / "gtkb-dashboard.sqlite"),
                    "--runtime-root",
                    str(record_path.parent),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(dashboard.DEFAULT_REFRESH_PORT),
                    "--grafana-port",
                    str(dashboard.DEFAULT_GRAFANA_PORT),
                    "--interval-minutes",
                    str(dashboard.DEFAULT_REFRESH_INTERVAL_MINUTES),
                )
                path_values = {3, 5, 7}
                actual = argv[1:]
                if len(actual) != len(expected) or any(
                    not _path_equal(value, expected[index]) if index in path_values else value != expected[index]
                    for index, value in enumerate(actual)
                ):
                    raise ServiceControlError(
                        "Dashboard live refresh arguments are custom or unknown; use its owner controller"
                    )
            current = _identity(row, runner)
            if current is not None:
                processes.append(current)
                if is_grafana:
                    roles.add("grafana")
                if is_refresh:
                    roles.add("refresh-service")
        for pid in contained - set(row_by_pid):
            if job_containment.process_identity(pid) is not None:
                raise ServiceControlError("Dashboard job member has no inspectable process identity")
        if job is not None and not {item["pid"] for item in processes}.issubset(set(dashboard._job_member_pids(job))):
            raise ServiceControlError("Dashboard job membership changed during observation")
    finally:
        if job is not None:
            dashboard._close_handle(job)
    refresh_answers, health = _get_health(DASHBOARD_HEALTH)
    grafana_ready = _get_ok(f"http://127.0.0.1:{dashboard.DEFAULT_GRAFANA_PORT}/api/health")
    if (refresh_answers and "refresh-service" not in roles) or (grafana_ready and "grafana" not in roles):
        raise ServiceControlError("Dashboard ports answer without this installation's identified members")
    if processes:
        path_fields = {
            "project_root": installation.root,
            "runtime_root": record_path.parent,
            "dashboard_db": record_path.parent / "gtkb-dashboard.sqlite",
            "config_path": installation.dashboard_config_path,
        }
        if (
            health is None
            or any(
                not isinstance(health.get(key), str) or not _path_equal(health[key], path)
                for key, path in path_fields.items()
            )
            or (
                health.get("interval_seconds") != dashboard.DEFAULT_REFRESH_INTERVAL_MINUTES * 60
                or health.get("grafana_port") != dashboard.DEFAULT_GRAFANA_PORT
            )
        ):
            raise ServiceControlError("Dashboard live health settings are custom or unknown; use its owner controller")
    last_result = (health or {}).get("last_result")
    refresh_ready = (
        refresh_answers
        and bool(health)
        and cast(dict[str, Any], health).get("status") == "ok"
        and not cast(dict[str, Any], health).get("last_error")
        and (isinstance(last_result, dict) and last_result.get("status") == "completed")
    )
    ready = refresh_ready and grafana_ready
    return _Observed(bool(processes), ready, processes=tuple(sorted(processes, key=lambda item: item["pid"])))


def _home_stop_state(installation: Installation, runner: Runner) -> _Observed:
    return _observe(installation, _Controller("home"), runner)


@contextmanager
def _hold_identified(
    processes: tuple[ProcessIdentity, ...],
) -> Iterator[list[tuple[ctypes.WinDLL, int]]]:
    """Keep the exact observed process objects alive across a controller's PID-based fallback."""
    from groundtruth_kb import job_containment

    with ExitStack() as handles:
        held_processes = []
        for expected in processes:
            current, held = handles.enter_context(job_containment.windows_process(expected["pid"]))
            if current != expected or held is None:
                raise ServiceControlError(f"Process {expected['pid']} changed identity before controller delegation")
            held_processes.append(held)
        yield held_processes


def _task_stop_plan(
    installation: Installation, runner: Runner, name: str
) -> tuple[_Controller, tuple[ProcessIdentity, ...]]:
    """Individual task-backed stops use the same identity proof as aggregate stops."""
    task = AUTHORITY_TASK if name == "authority" else OLLAMA_TASK
    definition = _task_definition(runner, task)
    if definition is None:
        raise ServiceControlError(f"Task {task} is not registered")
    if name == "authority":
        expected = (
            str(installation.authority_launcher),
            "--root",
            str(installation.root),
            "--port",
            str(urlsplit(installation.authority_url).port or 80),
        )
        controller = _task_controller(name, task, definition, expected)
        if not _path_equal(
            controller.executable, installation.root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
        ):
            raise ServiceControlError("Authority task names another installation's interpreter")
    else:
        home = _task_definition(runner, HOME_TASK)
        if home is None:
            raise ServiceControlError("Ollama has no owning GTKB-Home installation controller")
        owner = _task_controller("home", HOME_TASK, home, ("-B", str(installation.home_script), "start"))
        if not _path_equal(
            owner.executable, installation.root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
        ):
            raise ServiceControlError("Ollama's owning Home task names another installation's interpreter")
        controller = _task_controller(name, task, definition, ("serve",))
        if Path(controller.executable).name.casefold() != "ollama.exe":
            raise ServiceControlError("Ollama task does not name an installed ollama.exe")
    return controller, _observe(installation, controller, runner).processes


@dataclass(frozen=True)
class _EffectScope:
    """Invocation-local callback arguments. This holds no permission or durable authority."""

    callback: BeforeEffect
    operation: str
    targets: tuple[str, ...]
    phase: str = "forward"
    controllers: tuple[_Controller, ...] = ()
    runtime_attempts: set[str] | None = None

    def in_phase(self, phase: str) -> _EffectScope:
        return _EffectScope(self.callback, self.operation, self.targets, phase, self.controllers, self.runtime_attempts)

    def check(self, effects: list[dict[str, str]]) -> None:
        try:
            answer = self.callback(self.operation, list(self.targets), [dict(effect) for effect in effects], self.phase)
        except ServiceControlError:
            raise
        except Exception as error:  # intentional-catch: convert callback failure to pre-effect refusal
            raise ServiceControlError(f"{self.operation} effect check refused: {error}") from error
        if answer is False:
            raise ServiceControlError(f"{self.operation} effect check refused")


def _effects(controller: _Controller, *names: str) -> list[dict[str, str]]:
    return [{"target": f"service:{controller.name}", "effect": name} for name in names]


def _runtime_effects(controller: _Controller, action: str) -> list[dict[str, str]]:
    # SCM is the PostgreSQL effect boundary; its service.* operation includes its process lifecycle.
    names = (f"service.{action}",) if controller.name == "postgresql" else (f"service.{action}", f"process.{action}")
    return _effects(controller, *names)


def _planned_effects(controller: _Controller, action: str, state: _Observed) -> list[dict[str, str]]:
    desired = action == "start"
    effects = []
    if controller.task is not None and state.enabled != desired:
        effects.extend(_effects(controller, "task.enable" if desired else "task.disable"))
    if state.running != desired:
        effects.extend(_runtime_effects(controller, action))
        if desired and controller.name in ("authority", "ollama"):
            effects.extend(_effects(controller, "task.start"))
    return effects


def _restoration_effects(
    controller: _Controller, original: _Observed, current: _Observed, task_changed: bool
) -> list[dict[str, str]]:
    effects = []
    enabled = current.enabled
    if current.running != original.running:
        action = "start" if original.running else "stop"
        effects.extend(_planned_effects(controller, action, current))
        if controller.task is not None:
            task_changed = task_changed or enabled != original.running
            enabled = original.running
    if task_changed and controller.task is not None and enabled != original.enabled:
        effects.extend(_effects(controller, "task.enable" if original.enabled else "task.disable"))
    return effects


def _projected_state(controller: _Controller, state: _Observed, action: str) -> _Observed:
    desired = action == "start"
    return _Observed(desired, desired, desired if controller.task is not None else state.enabled)


def _unique_effects(effects: list[dict[str, str]]) -> list[dict[str, str]]:
    return list({(effect["target"], effect["effect"]): effect for effect in effects}.values())


def _check_controller_set(installation: Installation, runner: Runner, scope: _EffectScope) -> None:
    # After the last live-authority check, use only the already selected controllers. Rollback also stays in scope.
    if scope.controllers and scope.phase == "forward":
        current, _ = _inventory(installation, runner)
        if tuple(current) != scope.controllers:
            raise ServiceControlError(
                "Installed controller set changed after aggregate preflight; no new targets were selected"
            )


def _guard_effect(
    installation: Installation,
    controller: _Controller,
    runner: Runner,
    scope: _EffectScope,
    effects: list[dict[str, str]],
    expected: _Observed | None = None,
) -> _Observed:
    _check_controller_set(installation, runner, scope)
    observed = _observe(installation, controller, runner)
    if expected is not None and observed != expected:
        raise ServiceControlError(f"{controller.name} changed before its effect; request refused")
    scope.check(effects)
    # A canonical check is read-only, but may take time. Revalidate the installation and held process preimage after it.
    _check_controller_set(installation, runner, scope)
    if _observe(installation, controller, runner) != observed:
        raise ServiceControlError(f"{controller.name} changed during its effect check; request refused")
    return observed


def _single_controller(installation: Installation, name: str, runner: Runner) -> _Controller:
    if name in ("authority", "ollama"):
        return _task_stop_plan(installation, runner, name)[0]
    if name == "postgresql":
        return _postgresql_controller(installation, runner)
    if name == "home":
        _require_home_installation(installation)
        definition = _task_definition(runner, HOME_TASK)
        if definition is not None and _owner(_task(runner, HOME_TASK)[1], installation.home_script) is None:
            controller = _task_controller(name, HOME_TASK, definition, ("-B", str(installation.home_script), "start"))
            if not _path_equal(
                controller.executable, installation.root / "groundtruth-kb" / ".venv" / "Scripts" / "pythonw.exe"
            ):
                raise ServiceControlError("Home task names another installation's interpreter")
            return controller
        return _Controller(name)
    if name == "dashboard":
        from groundtruth_kb.dashboard import find_grafana_server

        binary = find_grafana_server(installation.root / ".groundtruth" / "tools" / "grafana")
        if binary is None:
            raise ServiceControlError("Dashboard has no supported installed Grafana controller")
        return _Controller(name, executable=str(binary))
    raise ServiceControlError(f"Unknown service {name!r}; known: {', '.join(SERVICES)}")


def _controlled_single(
    installation: Installation,
    name: str,
    action: str,
    runner: Runner,
    before_effect: BeforeEffect | None,
    *,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    return _service_operation(installation, action, runner, before_effect, single=name, on_complete=on_complete)


def observe_targets(installation: Installation, targets: list[str], runner: Runner = default_runner) -> dict[str, Any]:
    """Fresh local controller identities and states for an already selected service target set.

    This does not discover additional targets, call the native effect gate, or retain any permission. Browser and
    shortcut observations belong to their existing CLI boundaries. Dashboard names its actual installed Grafana
    controller; its observer also verifies the owned refresh/Grafana launch and processes when running.
    """
    if len(targets) != len(set(targets)):
        raise ServiceControlError("Duplicate service observation target")
    paths = {}
    states = {}
    for target in targets:
        if target not in {f"service:{name}" for name in SERVICES}:
            raise ServiceControlError(f"Unknown service observation target {target!r}")
        name = target.split(":", 1)[1]
        controller = _single_controller(installation, name, runner)
        state = _observe(installation, controller, runner)
        path = {
            "authority": installation.authority_launcher,
            "home": installation.home_script,
            "postgresql": installation.postgresql_data,
        }.get(name, Path(controller.executable))
        paths[target] = str(path.resolve())
        states[target] = _state_result(state)
    return {
        "installation_root": str(installation.root.resolve()),
        "config_path": str(installation.dashboard_config_path.resolve()),
        "observed_controller_paths": paths,
        "states": states,
    }


def _end_identified(
    runner: Runner,
    processes: tuple[ProcessIdentity, ...],
    *,
    before_terminate: Callable[[ProcessIdentity], None] | None = None,
) -> None:
    from groundtruth_kb import job_containment

    for expected in processes:
        # Holding the Windows process object prevents PID reuse between inspection and taskkill.
        with job_containment.windows_process(expected["pid"]) as (current, held):
            if current is None:
                continue
            if current != expected or held is None:
                raise ServiceControlError(f"Process {expected['pid']} changed identity; nothing was signalled")
            if before_terminate is not None:
                before_terminate(expected)
            result = runner(["taskkill", "/PID", str(expected["pid"]), "/T", "/F"], 15)
            kernel, handle = held
            if kernel.WaitForSingleObject(handle, 5000) != 0:
                raise ServiceControlError(
                    f"Process {expected['pid']} termination was not confirmed: "
                    f"{(result.stderr or result.stdout)[-800:]}"
                )


def _aggregate_action(
    installation: Installation,
    controller: _Controller,
    action: str,
    before: _Observed,
    runner: Runner,
    task_changes: set[str] | None = None,
    *,
    effect_scope: _EffectScope | None = None,
) -> None:
    if effect_scope is not None:
        _controlled_action(installation, controller, action, before, runner, task_changes, effect_scope)
        return
    if controller.name in ("authority", "ollama"):
        if controller.task is None:
            raise ServiceControlError(f"{controller.name} has no task controller")
        desired = action == "start"
        if before.enabled != desired:
            if task_changes is not None:
                task_changes.add(controller.name)
            _set_task(runner, controller.task, enabled=desired)
        if desired and not before.running:
            _run_task(runner, controller.task)
        elif not desired and before.running:
            _end_identified(runner, before.processes)
    else:
        # Home and Dashboard retain their existing identity-aware launch/stop controllers; PostgreSQL uses SCM.
        if controller.task is not None and before.enabled != (action == "start"):
            if task_changes is not None:
                task_changes.add(controller.name)
            _set_task(runner, controller.task, enabled=action == "start")
        if before.running != (action == "start"):
            if controller.name == "home" and action == "stop":
                with _hold_identified(before.processes):
                    outcome = stop(installation, controller.name, runner)
            else:
                outcome = (start if action == "start" else stop)(installation, controller.name, runner)
            if not outcome.get("started" if action == "start" else "stopped"):
                raise ServiceControlError(f"{controller.name} {action} failed: {outcome.get('detail')}")

    def confirmed() -> bool:
        state = _observe(installation, controller, runner)
        return (state.ready if action == "start" else not state.running) and (
            state.enabled is None or state.enabled == (action == "start")
        )

    if not _wait(confirmed, READY_SECONDS if action == "start" else 30):
        raise ServiceControlError(f"{controller.name} {action} did not reach its readback condition")


def _controlled_action(
    installation: Installation,
    controller: _Controller,
    action: str,
    before: _Observed,
    runner: Runner,
    task_changes: set[str] | None,
    scope: _EffectScope,
) -> None:
    """Use the existing controllers with a fresh check at each requested host-effect boundary."""
    desired = action == "start"
    current = before
    if controller.task is not None and current.enabled != desired:
        _guard_effect(
            installation,
            controller,
            runner,
            scope,
            _effects(controller, "task.enable" if desired else "task.disable"),
            current,
        )
        if task_changes is not None:
            task_changes.add(controller.name)  # Only a change whose setter we actually attempt belongs to us.
        _set_task(runner, controller.task, enabled=desired)
        current = _observe(installation, controller, runner)
        if current.enabled != desired:
            raise ServiceControlError(f"{controller.name} task enabled-state change was not confirmed")
    if current.running != desired:

        def attempted() -> None:
            if scope.runtime_attempts is not None:
                scope.runtime_attempts.add(controller.name)

        if controller.name in ("authority", "ollama"):
            if controller.task is None:
                raise ServiceControlError(f"{controller.name} has no task controller")
            if desired:
                _guard_effect(
                    installation,
                    controller,
                    runner,
                    scope,
                    _effects(controller, "service.start", "task.start", "process.start"),
                    current,
                )
                attempted()
                _run_task(runner, controller.task)
            else:
                processes = current.processes

                def before_terminate(expected: ProcessIdentity) -> None:
                    observed = _observe(installation, controller, runner)
                    if expected not in observed.processes or any(
                        process not in processes for process in observed.processes
                    ):
                        raise ServiceControlError(f"{controller.name} process set changed before termination")
                    _guard_effect(
                        installation,
                        controller,
                        runner,
                        scope,
                        _effects(controller, "service.stop", "process.stop"),
                        observed,
                    )
                    attempted()

                _end_identified(runner, processes, before_terminate=before_terminate)
        elif controller.name == "home":
            if desired:
                _guard_effect(
                    installation,
                    controller,
                    runner,
                    scope,
                    _effects(controller, "service.start", "process.start"),
                    current,
                )
                attempted()
                report = _home(installation, runner, "start")
            else:
                # Retain the exact Windows objects through Home's PID-based fallback and confirm their exits.
                with _hold_identified(current.processes) as held:
                    _guard_effect(
                        installation,
                        controller,
                        runner,
                        scope,
                        _effects(controller, "service.stop", "process.stop"),
                        current,
                    )
                    attempted()
                    report = _home(installation, runner, "stop")
                    unconfirmed = [
                        expected["pid"]
                        for expected, (kernel, handle) in zip(current.processes, held, strict=True)
                        if kernel.WaitForSingleObject(handle, 5000) != 0
                    ]
                    if unconfirmed:
                        raise ServiceControlError(f"Home process exit was not confirmed: {unconfirmed}")
            if not report.get("ok"):
                raise ServiceControlError(f"Home {action} failed: {report}")
        elif controller.name == "dashboard":
            _guard_effect(
                installation,
                controller,
                runner,
                scope,
                _effects(controller, f"service.{action}", f"process.{action}"),
                current,
            )
            attempted()
            result = runner(
                [
                    str(installation.python),
                    "-m",
                    "groundtruth_kb",
                    "--config",
                    str(installation.dashboard_config_path),
                    "dashboard",
                    action,
                    "--json",
                ],
                300 if desired else 120,
            )
            if result.returncode != 0:
                raise ServiceControlError(f"Dashboard {action} failed: {(result.stderr or result.stdout)[-800:]}")
        elif controller.name == "postgresql":
            _guard_effect(installation, controller, runner, scope, _runtime_effects(controller, action), current)
            attempted()
            result = _powershell(
                runner, f"{'Start' if desired else 'Stop'}-Service -Name {_quote(POSTGRESQL_SERVICE)} -ErrorAction Stop"
            )
            if result.returncode != 0:
                raise ServiceControlError(f"PostgreSQL {action} failed: {(result.stderr or result.stdout)[-800:]}")
        else:
            raise ServiceControlError(f"Unknown controller {controller.name!r}")

    def confirmed() -> bool:
        state = _observe(installation, controller, runner)
        return (state.ready if desired else not state.running) and (state.enabled is None or state.enabled == desired)

    if not _wait(confirmed, READY_SECONDS if desired else 30):
        raise ServiceControlError(f"{controller.name} {action} did not reach its readback condition")


def _apply_controller_action(
    installation: Installation,
    controller: _Controller,
    action: str,
    before: _Observed,
    runner: Runner,
    task_changes: set[str],
    scope: _EffectScope | None,
) -> None:
    if scope is None:
        _aggregate_action(installation, controller, action, before, runner, task_changes)
    else:
        _aggregate_action(installation, controller, action, before, runner, task_changes, effect_scope=scope)


def _state_result(state: _Observed) -> dict[str, Any]:
    return {
        "running": state.running,
        "ready": state.ready,
        "task_enabled": state.enabled,
        "processes": list(state.processes),
    }


def _restore_task_enabled(
    controller: _Controller, enabled: bool, runner: Runner, *, effect_scope: _EffectScope | None = None
) -> None:
    """Restore our task change even when a server's runtime readback fails; revalidate registration first."""
    if controller.task is None:
        return
    definition = _task_definition(runner, controller.task)
    if definition is None:
        raise ServiceControlError(f"Task {controller.task} disappeared during compensation")
    current = _task_controller(controller.name, controller.task, definition, controller.arguments)
    if not _path_equal(current.executable, controller.executable):
        raise ServiceControlError(f"Task {controller.task} changed controller; task restoration refused")
    if definition["enabled"] != enabled:
        if effect_scope is not None:
            effect_scope.check(_effects(controller, "task.enable" if enabled else "task.disable"))
            fresh = _task_definition(runner, controller.task)
            if fresh is None or fresh != definition:
                raise ServiceControlError(f"Task {controller.task} changed during its restoration effect check")
            confirmed = _task_controller(controller.name, controller.task, fresh, controller.arguments)
            if not _path_equal(confirmed.executable, controller.executable):
                raise ServiceControlError(f"Task {controller.task} changed controller; restoration refused")
        _set_task(runner, controller.task, enabled=enabled)
    readback = _task_definition(runner, controller.task)
    if readback is None or readback["enabled"] != enabled:
        raise ServiceControlError(f"Task {controller.task} enabled-state restoration was not confirmed")
    confirmed = _task_controller(controller.name, controller.task, readback, controller.arguments)
    if not _path_equal(confirmed.executable, controller.executable):
        raise ServiceControlError(f"Task {controller.task} changed controller during restoration readback")


def _terminal_effects(
    installation: Installation,
    runner: Runner,
    remaining: list[_Controller],
    touched: list[_Controller],
    initial: dict[str, _Observed],
    after: dict[str, _Observed],
    task_changes: set[str],
) -> list[dict[str, str]]:
    """Exact forward suffix and bounded inverse actions, prepared while authority is still live."""
    effects = []
    for controller in touched:
        current = _observe(installation, controller, runner)
        if controller.name not in after or current != after[controller.name]:
            raise ServiceControlError("Captured state changed before the terminal shutdown boundary")
        effects.extend(
            _restoration_effects(controller, initial[controller.name], current, controller.name in task_changes)
        )
    for controller in remaining:
        if controller.name not in ("authority", "postgresql"):
            raise ServiceControlError("Terminal shutdown cannot select another controller after authority")
        current = _observe(installation, controller, runner)
        if current != initial[controller.name]:
            raise ServiceControlError(f"{controller.name} changed before terminal shutdown")
        planned = _planned_effects(controller, "stop", current)
        effects.extend(planned)
        if planned:
            effects.extend(
                _restoration_effects(
                    controller,
                    current,
                    _projected_state(controller, current, "stop"),
                    controller.task is not None and current.enabled is not False,
                )
            )
    return _unique_effects(effects)


def aggregate(
    installation: Installation,
    action: str,
    runner: Runner = default_runner,
    *,
    before_effect: BeforeEffect | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    """Start/stop installed persistent controllers, compensating only changes made by this call.

    This is a service operation, not an atomic host transaction. Readback and any incomplete compensation are
    returned explicitly. Maintenance/qualification controllers and custom Dashboard runtimes are outside this API.
    """
    return _service_operation(installation, action, runner, before_effect, on_complete=on_complete)


def _service_operation(
    installation: Installation,
    action: str,
    runner: Runner,
    before_effect: BeforeEffect | None,
    *,
    single: str | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    if action not in ("start", "stop"):
        raise ServiceControlError(f"Unknown aggregate service action {action!r}")
    outcome_key = "started" if action == "start" else "stopped"
    result: dict[str, Any] = {
        "service": single or "all",
        "ok": False,
        outcome_key: False,
        "scope": "this installation's supported persistent controllers"
        if single is None
        else "this installation's selected controller",
        "restoration_scope": "running and task-enabled states; restarted processes receive new identities",
    }
    scope = None
    try:
        if single is None:
            controllers, excluded = _inventory(installation, runner)
        else:
            controllers, excluded = [_single_controller(installation, single, runner)], {}
        initial = {controller.name: _observe(installation, controller, runner) for controller in controllers}
        if action == "start":
            degraded = [name for name, state in initial.items() if state.running and not state.ready]
            if degraded:
                raise ServiceControlError(
                    f"Already-running controllers require repair before aggregate start: {', '.join(degraded)}"
                )
        dashboard = initial.get("dashboard")
        if action == "stop" and dashboard is not None and dashboard.running and not dashboard.ready:
            raise ServiceControlError(
                "Partial Dashboard launch cannot be restored as the same initial member set; "
                "use its individual stop controller"
            )
        if before_effect is not None:
            scope = _EffectScope(
                before_effect,
                f"services.{action}" + ("-all" if single is None else ""),
                tuple(f"service:{controller.name}" for controller in controllers),
                controllers=tuple(controllers) if single is None else (),
                runtime_attempts=set(),
            )
            planned = []
            for controller in controllers:
                state = initial[controller.name]
                forward = _planned_effects(controller, action, state)
                planned.extend(forward)
                if forward:
                    planned.extend(
                        _restoration_effects(
                            controller,
                            state,
                            _projected_state(controller, state, action),
                            controller.task is not None and state.enabled != (action == "start"),
                        )
                    )
            scope.in_phase("preflight").check(_unique_effects(planned))
    except (ServiceControlError, OSError, ValueError, subprocess.SubprocessError) as error:
        result.update(phase="preflight", detail=str(error), attempted=[], changed=[], initial_state_restored=True)
        return result
    result.update(
        supported=[controller.name for controller in controllers],
        excluded=excluded,
        initial={name: _state_result(state) for name, state in initial.items()},
    )
    ordered = controllers if action == "start" else list(reversed(controllers))
    touched: list[_Controller] = []
    task_changes: set[str] = set()
    after: dict[str, _Observed] = {}

    def ours(controller: _Controller) -> bool:
        return scope is None or controller.name in task_changes or controller.name in (scope.runtime_attempts or set())

    failed = ""
    try:
        for index, controller in enumerate(ordered):
            failed = controller.name
            if scope is not None:
                _check_controller_set(installation, runner, scope)
            before = _observe(installation, controller, runner)
            if before != initial[controller.name]:
                raise ServiceControlError(f"{controller.name} changed after preflight; aggregate operation stopped")
            desired = action == "start"
            if before.running == desired and (before.enabled is None or before.enabled == desired):
                continue
            terminal_boundary = controller.name == "authority" or (
                single == "postgresql" and controller.name == "postgresql"
            )
            if scope is not None and action == "stop" and terminal_boundary and before.running:
                terminal = scope.in_phase("terminal_shutdown")
                terminal.check(
                    _terminal_effects(installation, runner, ordered[index:], touched, initial, after, task_changes)
                )
                _check_controller_set(installation, runner, scope)
                scope = terminal  # Later checks retain this terminal phase and the full already selected target set.
            touched.append(controller)  # Include a controller whose request changes a task and then fails.
            try:
                _apply_controller_action(installation, controller, action, before, runner, task_changes, scope)
            finally:
                after[controller.name] = _observe(installation, controller, runner)
        failed = "all"
        final = {controller.name: _observe(installation, controller, runner) for controller in controllers}
        if not all(
            (state.ready if action == "start" else not state.running)
            and (state.enabled is None or state.enabled == (action == "start"))
            for state in final.values()
        ):
            raise ServiceControlError("Final aggregate readback differs from the requested service state")
        if on_complete is not None:
            failed = "completion"
            try:
                completed = on_complete()
            except ServiceControlError:
                raise
            except Exception as error:  # intentional-catch: failed completion enters captured compensation
                raise ServiceControlError(f"Completion callback failed: {error}") from error
            if completed is False:
                raise ServiceControlError("Completion callback reported failure")
            final = {controller.name: _observe(installation, controller, runner) for controller in controllers}
            if not all(
                (state.ready if action == "start" else not state.running)
                and (state.enabled is None or state.enabled == (action == "start"))
                for state in final.values()
            ):
                raise ServiceControlError("Service state changed during the completion callback")
        changed = [item.name for item in touched if ours(item) and after[item.name] != initial[item.name]]
        result.update(
            ok=True,
            **{outcome_key: True},
            phase="complete",
            attempted=[item.name for item in touched],
            changed=changed,
            final={name: _state_result(state) for name, state in final.items()},
        )
        return result
    except (ServiceControlError, OSError, ValueError, subprocess.SubprocessError) as error:
        result.update(phase="compensation", failed_service=failed, detail=str(error))
    compensation_errors: dict[str, str] = {}
    rollback = scope.in_phase("rollback") if scope is not None else None
    for controller in reversed(touched):
        original = initial[controller.name]
        issues = []
        try:
            current = _observe(installation, controller, runner)
            if controller.name not in after or current != after[controller.name]:
                raise ServiceControlError("State changed outside the captured request; compensation cannot safely act")
            if current.running != original.running:
                if scope is not None and controller.name not in (scope.runtime_attempts or set()):
                    raise ServiceControlError(
                        "Runtime changed before any controller effect was attempted; compensation cannot change it"
                    )
                _apply_controller_action(
                    installation,
                    controller,
                    "start" if original.running else "stop",
                    current,
                    runner,
                    task_changes,
                    rollback,
                )
        except (ServiceControlError, OSError, ValueError, subprocess.SubprocessError) as error:
            issues.append(str(error))
        try:
            if controller.name in task_changes and controller.task is not None and original.enabled is not None:
                if rollback is None:
                    _restore_task_enabled(controller, original.enabled, runner)
                else:
                    _restore_task_enabled(controller, original.enabled, runner, effect_scope=rollback)
            restored = _observe(installation, controller, runner)
            if restored.running != original.running or restored.enabled != original.enabled:
                raise ServiceControlError("Initial running/task-enabled state was not restored")
        except (ServiceControlError, OSError, ValueError, subprocess.SubprocessError) as error:
            issues.append(str(error))
        if issues:
            compensation_errors[controller.name] = "; ".join(issues)
    final_result: dict[str, Any] = {}
    restored_all = not compensation_errors
    for controller in controllers:
        try:
            state = _observe(installation, controller, runner)
            final_result[controller.name] = _state_result(state)
            original = initial[controller.name]
            restored_all = restored_all and state.running == original.running and state.enabled == original.enabled
        except (ServiceControlError, OSError, ValueError, subprocess.SubprocessError) as error:
            final_result[controller.name] = {"unknown": str(error)}
            restored_all = False
    changed = [
        item.name for item in touched if ours(item) and item.name in after and after[item.name] != initial[item.name]
    ]
    result.update(
        attempted=[item.name for item in touched],
        changed=changed,
        unconfirmed_changes=[item.name for item in touched if ours(item) and item.name not in after],
        compensation_errors=compensation_errors,
        initial_state_restored=restored_all,
        final=final_result,
    )
    return result


def start_all(
    installation: Installation,
    runner: Runner = default_runner,
    *,
    before_effect: BeforeEffect | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    return aggregate(installation, "start", runner, before_effect=before_effect, on_complete=on_complete)


def stop_all(
    installation: Installation,
    runner: Runner = default_runner,
    *,
    before_effect: BeforeEffect | None = None,
    on_complete: OnComplete | None = None,
) -> dict[str, Any]:
    return aggregate(installation, "stop", runner, before_effect=before_effect, on_complete=on_complete)


def as_json(states: list[ServiceState]) -> list[dict[str, Any]]:
    return [asdict(state) for state in states]


def installation_from_config(
    project_root: Path, authority_url: str | None, config_path: Path | None = None
) -> Installation:
    python = project_root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    return Installation(
        root=project_root,
        authority_url=authority_url or "http://127.0.0.1:8765",
        python=python if python.is_file() else Path(sys.executable),
        config_path=config_path.resolve() if config_path is not None else None,
    )
