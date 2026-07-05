# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Aggregate control surface for the dispatcher daemon complex.

The complex surface coordinates the existing daemon process, dispatcher
supervisor task, and storm-watchdog task without merging their runtimes.
"""

from __future__ import annotations

import contextlib
import importlib.util
import os
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
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "kind": kind,
        "healthy": healthy,
        "status": status,
    }
    if error:
        payload["error"] = error
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
            error=str(exc),
        )
    return _component_payload(
        name="daemon",
        kind="process",
        status=status,
        healthy=bool(status.get("running")),
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
            error=str(exc),
        )
    return _component_payload(
        name=name,
        kind="scheduled_task",
        status=status,
        healthy=bool(status.get("healthy")),
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
        if component.get("healthy"):
            continue
        error = component.get("error")
        if error:
            findings.append(f"{name}: {error}")
            continue
        status = component.get("status")
        if not isinstance(status, dict):
            findings.append(f"{name}: no status payload")
            continue
        nested_findings = status.get("findings")
        if isinstance(nested_findings, list) and nested_findings:
            findings.extend(f"{name}: {item}" for item in nested_findings)
        elif name == "daemon":
            findings.append("daemon: dispatcher daemon is not running")
        else:
            findings.append(f"{name}: component is not healthy")
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
    aggregate = _aggregate_status(components)
    return {
        "project_root": str(root),
        "aggregate_status": aggregate,
        "healthy": aggregate == "healthy",
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
