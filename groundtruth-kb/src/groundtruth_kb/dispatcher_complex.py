# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Aggregate control surface for the dispatcher daemon complex.

The complex surface coordinates the existing daemon process, dispatcher
supervisor task, and storm-watchdog task without merging their runtimes.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import importlib.util
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from groundtruth_kb.dispatcher_supervisor import (
    DEFAULT_TASK_NAME as DEFAULT_SUPERVISOR_TASK_NAME,
)
from groundtruth_kb.dispatcher_supervisor import (
    DispatcherSupervisorError,
    collect_supervisor_status,
    disable_supervisor,
    enable_supervisor,
)
from groundtruth_kb.dispatcher_watchdog import (
    DEFAULT_TASK_NAME as DEFAULT_WATCHDOG_TASK_NAME,
)
from groundtruth_kb.dispatcher_watchdog import (
    DispatcherWatchdogError,
    collect_watchdog_status,
    disable_watchdog,
    enable_watchdog,
)

WATCHDOG_HEARTBEAT_RELATIVE_PATH = Path(".gtkb-state") / "ops" / "storm-watchdog-heartbeat.txt"
DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0
HEALTH_STATUS_ORDER = {"PASS": 0, "WARN": 1, "FAIL": 2}


class DispatcherComplexError(RuntimeError):
    """Raised when a dispatcher-complex control action cannot complete."""

    def __init__(self, message: str, *, payload: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.payload = payload or {"ok": False, "error": message}


def load_daemon_module(project_root: Path) -> Any:
    """Load the repo-local dispatcher daemon script as a module."""
    script = project_root.resolve() / "scripts" / "gtkb_dispatcher_daemon.py"
    spec = importlib.util.spec_from_file_location("gtkb_dispatcher_daemon_complex", script)
    if spec is None or spec.loader is None:
        raise DispatcherComplexError(f"dispatcher daemon script missing: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prefer_windows_gui_python(command: str) -> str:
    if os.name != "nt":
        return command
    split_at = max(command.rfind("\\"), command.rfind("/"))
    executable_name = command[split_at + 1 :] if split_at >= 0 else command
    if executable_name.lower() != "python.exe":
        return command
    candidate = f"{command[: split_at + 1]}pythonw.exe" if split_at >= 0 else "pythonw.exe"
    return candidate if os.path.isfile(candidate) else command


def _component_payload(
    *,
    name: str,
    kind: str,
    status: dict[str, Any] | None,
    healthy: bool,
    severity: str = "PASS",
    finding: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "kind": kind,
        "healthy": healthy,
        "severity": severity,
        "status": status,
    }
    if finding:
        payload["finding"] = finding
    if error:
        payload["error"] = error
    return payload


def _health_status_from_components(components: dict[str, dict[str, Any]]) -> str:
    status = "PASS"
    for component in components.values():
        severity = str(component.get("severity") or "PASS").upper()
        if HEALTH_STATUS_ORDER.get(severity, 0) > HEALTH_STATUS_ORDER[status]:
            status = severity
    return status


def _daemon_heartbeat_stale_seconds(daemon_module: Any) -> float:
    resolver = getattr(daemon_module, "_heartbeat_stale_seconds", None)
    if callable(resolver):
        try:
            value = float(resolver())
            return value if value > 0 else DEFAULT_HEARTBEAT_STALE_SECONDS
        except (TypeError, ValueError):
            pass
    return DEFAULT_HEARTBEAT_STALE_SECONDS


def _heartbeat_finding(
    *,
    component: str,
    status: dict[str, Any],
    stale_seconds: float,
) -> str | None:
    if not status.get("running") and component == "daemon":
        return "dispatcher daemon is not running"
    age = status.get("heartbeat_age_seconds")
    if age is None:
        return f"{component} heartbeat is absent or unreadable"
    try:
        age_float = float(age)
    except (TypeError, ValueError):
        return f"{component} heartbeat age is not numeric"
    if age_float > stale_seconds:
        return f"{component} heartbeat is stale ({age_float:.1f}s > {stale_seconds:.1f}s)"
    return None


def _daemon_component_severity(status: dict[str, Any], daemon_module: Any) -> tuple[str, str | None]:
    finding = _heartbeat_finding(
        component="daemon",
        status=status,
        stale_seconds=_daemon_heartbeat_stale_seconds(daemon_module),
    )
    if finding is None:
        return "PASS", None
    return "WARN", finding


def _scheduled_task_severity(status: dict[str, Any], *, component: str) -> tuple[str, str | None]:
    findings = status.get("findings")
    finding = str(findings[0]) if isinstance(findings, list) and findings else f"{component} is not healthy"
    if status.get("healthy"):
        return "PASS", None
    if status.get("supported") is False:
        return "WARN", finding
    severe_markers = ("not registered", "missing ", "probe failed")
    if any(marker in finding for marker in severe_markers):
        return "FAIL", finding
    return "WARN", finding


def _watchdog_heartbeat_path(project_root: Path) -> Path:
    return project_root.resolve() / WATCHDOG_HEARTBEAT_RELATIVE_PATH


def _parse_heartbeat_threshold(line: str) -> float:
    match = re.search(r"\bthreshold=(?P<value>\d+(?:\.\d+)?)\b", line)
    if match is None:
        return DEFAULT_HEARTBEAT_STALE_SECONDS
    try:
        value = float(match.group("value"))
    except ValueError:
        return DEFAULT_HEARTBEAT_STALE_SECONDS
    return value if value > 0 else DEFAULT_HEARTBEAT_STALE_SECONDS


def _read_watchdog_heartbeat(project_root: Path, *, now: dt.datetime | None = None) -> dict[str, Any]:
    path = _watchdog_heartbeat_path(project_root)
    payload: dict[str, Any] = {
        "path": str(path),
        "present": False,
        "heartbeat_at": None,
        "age_seconds": None,
        "stale_seconds": DEFAULT_HEARTBEAT_STALE_SECONDS,
        "fresh": False,
        "finding": "watchdog heartbeat is absent",
    }
    try:
        line = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return payload
    except OSError as exc:
        payload["finding"] = f"watchdog heartbeat is unreadable: {exc}"
        return payload
    payload["present"] = True
    payload["raw"] = line
    token = line.split()[0] if line.split() else ""
    payload["stale_seconds"] = _parse_heartbeat_threshold(line)
    try:
        parsed = dt.datetime.fromisoformat(token.replace("Z", "+00:00"))
    except ValueError:
        payload["finding"] = "watchdog heartbeat timestamp is unparsable"
        return payload
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    now_utc = now or dt.datetime.now(dt.UTC)
    age = (now_utc - parsed.astimezone(dt.UTC)).total_seconds()
    payload["heartbeat_at"] = token
    payload["age_seconds"] = age
    payload["fresh"] = age <= float(payload["stale_seconds"])
    payload["finding"] = (
        None
        if payload["fresh"]
        else (f"watchdog heartbeat is stale ({age:.1f}s > {float(payload['stale_seconds']):.1f}s)")
    )
    return payload


def _daemon_component_status(project_root: Path, daemon_module: Any | None) -> dict[str, Any]:
    daemon = daemon_module or load_daemon_module(project_root)
    try:
        status = daemon.collect_daemon_status(project_root)
    except Exception as exc:  # noqa: BLE001 - aggregate status must isolate component failures
        return _component_payload(
            name="daemon",
            kind="process",
            status=None,
            healthy=False,
            severity="FAIL",
            finding=f"daemon status probe failed: {exc}",
            error=str(exc),
        )
    severity, finding = _daemon_component_severity(status, daemon)
    return _component_payload(
        name="daemon",
        kind="process",
        status=status,
        healthy=bool(status.get("running")),
        severity=severity,
        finding=finding,
    )


def _scheduled_task_component_status(
    *,
    name: str,
    task_name: str,
    collector: Callable[..., dict[str, Any]],
    project_root: Path,
) -> dict[str, Any]:
    try:
        status = collector(project_root, task_name=task_name)
    except Exception as exc:  # noqa: BLE001 - aggregate status must isolate component failures
        return _component_payload(
            name=name,
            kind="scheduled_task",
            status=None,
            healthy=False,
            severity="FAIL",
            finding=f"{name} status probe failed: {exc}",
            error=str(exc),
        )
    severity, finding = _scheduled_task_severity(status, component=name)
    return _component_payload(
        name=name,
        kind="scheduled_task",
        status=status,
        healthy=bool(status.get("healthy")),
        severity=severity,
        finding=finding,
    )


def _aggregate_status(components: dict[str, dict[str, Any]]) -> str:
    if all(component.get("healthy") for component in components.values()):
        return "healthy"
    if not any(component.get("healthy") for component in components.values()):
        return "inactive"
    return "degraded"


def _component_findings(components: dict[str, dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for name, component in components.items():
        if component.get("severity") == "PASS":
            continue
        severity = str(component.get("severity") or "WARN").upper()
        prefix = f"{severity} {name}: "
        finding = component.get("finding")
        if isinstance(finding, str) and finding:
            findings.append(prefix + finding)
            continue
        error = component.get("error")
        if error:
            findings.append(prefix + str(error))
            continue
        status = component.get("status")
        if not isinstance(status, dict):
            findings.append(prefix + "no status payload")
            continue
        nested_findings = status.get("findings")
        if isinstance(nested_findings, list) and nested_findings:
            findings.extend(prefix + str(item) for item in nested_findings)
        elif name == "daemon":
            findings.append(prefix + "dispatcher daemon is not running")
        else:
            findings.append(prefix + "component is not healthy")
    return findings


def collect_complex_status(
    project_root: Path,
    *,
    supervisor_task_name: str = DEFAULT_SUPERVISOR_TASK_NAME,
    watchdog_task_name: str = DEFAULT_WATCHDOG_TASK_NAME,
    daemon_module: Any | None = None,
) -> dict[str, Any]:
    """Return a deterministic rollup over daemon, supervisor, and watchdog state."""
    root = project_root.resolve()
    components = {
        "daemon": _daemon_component_status(root, daemon_module),
        "supervisor": _scheduled_task_component_status(
            name="supervisor",
            task_name=supervisor_task_name,
            collector=collect_supervisor_status,
            project_root=root,
        ),
        "watchdog": _scheduled_task_component_status(
            name="watchdog",
            task_name=watchdog_task_name,
            collector=collect_watchdog_status,
            project_root=root,
        ),
    }
    watchdog_heartbeat = _read_watchdog_heartbeat(root)
    watchdog = components["watchdog"]
    if watchdog.get("severity") == "PASS" and not watchdog_heartbeat.get("fresh"):
        watchdog["severity"] = "WARN"
        watchdog["finding"] = watchdog_heartbeat.get("finding") or "watchdog heartbeat is not fresh"
    watchdog["heartbeat"] = watchdog_heartbeat
    aggregate = _aggregate_status(components)
    return {
        "project_root": str(root),
        "aggregate_status": aggregate,
        "healthy": aggregate == "healthy",
        "health_status": _health_status_from_components(components),
        "components": components,
        "findings": _component_findings(components),
    }


def collect_complex_health(
    project_root: Path,
    *,
    supervisor_task_name: str = DEFAULT_SUPERVISOR_TASK_NAME,
    watchdog_task_name: str = DEFAULT_WATCHDOG_TASK_NAME,
    daemon_module: Any | None = None,
) -> dict[str, Any]:
    """Return lifecycle health for the dispatcher complex.

    This is intentionally separate from bridge routing/config health.
    """
    status = collect_complex_status(
        project_root,
        supervisor_task_name=supervisor_task_name,
        watchdog_task_name=watchdog_task_name,
        daemon_module=daemon_module,
    )
    aggregate = status["aggregate_status"]
    if "health_status" not in status:
        status["health_status"] = "PASS" if aggregate == "healthy" else "FAIL" if aggregate == "inactive" else "WARN"
    return status


def _run_scheduled_task_controls(
    action: str,
    controls: list[tuple[str, Callable[[], dict[str, Any]]]],
) -> dict[str, Any]:
    components: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for name, callback in controls:
        order.append(name)
        try:
            result = callback()
        except (DispatcherSupervisorError, DispatcherWatchdogError, OSError) as exc:
            components[name] = {
                "action": action,
                "ok": False,
                "error": str(exc),
            }
            continue
        components[name] = {
            "action": action,
            "ok": True,
            "result": result,
        }
    ok = all(component["ok"] for component in components.values())
    return {
        "action": action,
        "ok": ok,
        "aggregate_status": "ok" if ok else "error",
        "order": order,
        "components": components,
    }


def enable_complex(
    *,
    supervisor_task_name: str = DEFAULT_SUPERVISOR_TASK_NAME,
    watchdog_task_name: str = DEFAULT_WATCHDOG_TASK_NAME,
) -> dict[str, Any]:
    """Enable only the scheduled-task components of the dispatcher complex."""
    return _run_scheduled_task_controls(
        "enable",
        [
            ("supervisor", lambda: enable_supervisor(task_name=supervisor_task_name)),
            ("watchdog", lambda: enable_watchdog(task_name=watchdog_task_name)),
        ],
    )


def disable_complex(
    *,
    supervisor_task_name: str = DEFAULT_SUPERVISOR_TASK_NAME,
    watchdog_task_name: str = DEFAULT_WATCHDOG_TASK_NAME,
) -> dict[str, Any]:
    """Disable only the scheduled-task components of the dispatcher complex."""
    return _run_scheduled_task_controls(
        "disable",
        [
            ("supervisor", lambda: disable_supervisor(task_name=supervisor_task_name)),
            ("watchdog", lambda: disable_watchdog(task_name=watchdog_task_name)),
        ],
    )


def start_complex(
    project_root: Path,
    *,
    interval: int = 30,
    daemon_module: Any | None = None,
    popen_factory: Callable[..., Any] = subprocess.Popen,
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Start the daemon process through the existing daemon lifecycle contract."""
    root = project_root.resolve()
    daemon = daemon_module or load_daemon_module(root)
    state_dir = daemon.daemon_state_dir(root)
    if daemon.read_daemon_status(root).get("running") or daemon.daemon_process_alive(state_dir):
        payload = {
            "action": "start",
            "ok": False,
            "aggregate_status": "error",
            "components": {
                "daemon": {
                    "action": "start",
                    "ok": False,
                    "error": "dispatcher daemon already running",
                }
            },
            "untouched_components": ["supervisor", "watchdog"],
        }
        raise DispatcherComplexError("dispatcher daemon already running", payload=payload)

    script = root / "scripts" / "gtkb_dispatcher_daemon.py"
    popen_kwargs: dict[str, object] = {
        "cwd": str(root),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = (
            getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        popen_kwargs["start_new_session"] = True
    proc = popen_factory(
        [
            _prefer_windows_gui_python(python_executable or sys.executable),
            str(script),
            "--loop",
            "--project-root",
            str(root),
            "--tick-seconds",
            str(interval),
        ],
        **popen_kwargs,
    )
    return {
        "action": "start",
        "ok": True,
        "aggregate_status": "ok",
        "components": {
            "daemon": {
                "action": "start",
                "ok": True,
                "pid": proc.pid,
                "interval": interval,
            }
        },
        "untouched_components": ["supervisor", "watchdog"],
    }


def stop_complex(
    project_root: Path,
    *,
    daemon_module: Any | None = None,
    terminate_fn: Callable[[int], Any] | None = None,
) -> dict[str, Any]:
    """Stop the daemon process through the existing daemon lifecycle contract."""
    from groundtruth_kb.bridge_dispatch_reset import terminate_pid_tree

    root = project_root.resolve()
    daemon = daemon_module or load_daemon_module(root)
    state_dir = daemon.daemon_state_dir(root)
    terminator = terminate_fn or terminate_pid_tree
    pid_path = state_dir / daemon.PID_FILENAME
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pid = 0

    candidate_pids: list[int] = []
    if pid > 0 and (
        daemon.daemon_pid_provenance_verified(state_dir) or daemon.daemon_pid_matches_legacy_loop(state_dir, pid)
    ):
        candidate_pids.append(pid)
    if hasattr(daemon, "matching_daemon_loop_pids"):
        for loop_pid in daemon.matching_daemon_loop_pids(state_dir):
            if loop_pid > 0 and loop_pid not in candidate_pids:
                candidate_pids.append(loop_pid)

    reaped_workers = 0
    if hasattr(daemon, "_reap_dispatched_workers"):
        try:
            reaped_workers = int(daemon._reap_dispatched_workers(root) or 0)
        except Exception:  # noqa: BLE001 - stop remains best-effort
            reaped_workers = 0

    for candidate_pid in candidate_pids:
        terminator(candidate_pid)
        try:
            expected_create_time = daemon._read_pid_create_time_sidecar(state_dir)
            if expected_create_time is not None and daemon._pid_create_time_matches(
                candidate_pid, expected_create_time
            ):
                import psutil  # noqa: PLC0415

                proc = psutil.Process(candidate_pid)
                for child in proc.children(recursive=True):
                    with contextlib.suppress(Exception):
                        child.kill()
                with contextlib.suppress(Exception):
                    proc.kill()
        except Exception:  # noqa: BLE001 - stop remains best-effort
            pass
    if hasattr(daemon, "_clear_daemon_pid_record"):
        daemon._clear_daemon_pid_record(state_dir)
    else:
        with contextlib.suppress(OSError):
            pid_path.unlink()
    daemon.release_daemon_lock(state_dir, force=True)

    if candidate_pids:
        outcome = "terminated"
    elif pid > 0:
        outcome = "cleared_unverified_pid"
    else:
        outcome = "lock_released"
    return {
        "action": "stop",
        "ok": True,
        "aggregate_status": "ok",
        "components": {
            "daemon": {
                "action": "stop",
                "ok": True,
                "outcome": outcome,
                "candidate_pids": candidate_pids,
                "reaped_workers": reaped_workers,
            }
        },
        "untouched_components": ["supervisor", "watchdog"],
    }
