# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy bridge worker health-check and recovery fallback.

This module belongs to the archived SQLite/MCP bridge runtime and is retained
for compatibility. New dual-agent projects should use project-owned file bridge
OS pollers instead.

When called from a SessionStart hook, this script:

  1. Checks if the worker is already healthy (scheduled task running).
  2. If healthy, reports OK and exits.
  3. If not healthy, attempts to start the scheduled task.
  4. If the scheduled task is not registered, falls back to detached process
     launch (legacy behavior) and logs a warning.

For legacy deployments, install the scheduled tasks first:
  scripts/register_bridge_runtime_tasks.ps1
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _consume_stdin_if_present() -> None:
    try:
        if not sys.stdin.isatty():
            _ = sys.stdin.read()
    except Exception:  # intentional-catch: best-effort stdin consumption
        pass


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            exit_code = wintypes.DWORD()
            ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(handle)
            return int(exit_code.value) == STILL_ACTIVE
        except (OSError, AttributeError, ImportError):
            return False  # Process assumed dead on any platform-access error
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _discover_running_worker(project_dir: Path, agent: str) -> dict[str, Any] | None:
    from groundtruth_kb.bridge.worker import (
        resident_worker_health_snapshot,
        resident_worker_is_healthy,
    )

    healthy, health_state = resident_worker_is_healthy(agent, project_dir=project_dir)
    snapshot = resident_worker_health_snapshot(agent, project_dir=project_dir) or {}
    pid = int(snapshot.get("pid", 0) or 0)
    if healthy and pid > 0 and _pid_is_running(pid):
        return {
            "pid": pid,
            "agent": agent,
            "source": "health",
            "updated_at": snapshot.get("updated_at"),
            "state": health_state,
        }
    return None


def _wait_for_worker(
    project_dir: Path, *, agent: str, expected_pid: int, timeout_seconds: float
) -> dict[str, Any] | None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        running = _discover_running_worker(project_dir, agent)
        if running and running.get("pid") == expected_pid:
            return running
        if not _pid_is_running(expected_pid):
            break
        time.sleep(0.1)
    return None


def _start_detached(
    project_dir: Path,
    *,
    agent: str,
    cadence_minutes: int,
    timeout_seconds: int,
    poll_interval_ms: int,
    limit: int,
    max_dispatch_targets: int,
    exec_timeout_seconds: int,
    error_backoff_seconds: int,
) -> int:
    if os.name == "nt":
        py = str(Path(sys.executable).resolve())
        # Use -m to run the worker module instead of a script path
        arg_parts = [
            "-m",
            "groundtruth_kb.bridge.worker",
            "--agent",
            agent,
            "--project-dir",
            str(project_dir),
            "--cadence-minutes",
            str(cadence_minutes),
            "--timeout-seconds",
            str(timeout_seconds),
            "--poll-interval-ms",
            str(poll_interval_ms),
            "--limit",
            str(limit),
            "--max-dispatch-targets",
            str(max_dispatch_targets),
            "--exec-timeout-seconds",
            str(exec_timeout_seconds),
            "--error-backoff-seconds",
            str(error_backoff_seconds),
        ]
        arg_string = " ".join(arg_parts)

        def _q(value: str) -> str:
            return value.replace("'", "''")

        ps = (
            f"$p = Start-Process -FilePath '{_q(py)}' "
            f"-ArgumentList '{_q(arg_string)}' "
            "-WindowStyle Hidden -PassThru; "
            "Write-Output $p.Id"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in (completed.stdout or "").splitlines() if line.strip()]
        if not lines:
            raise RuntimeError("launcher did not receive child PID")
        return int(lines[-1])

    cmd = [
        sys.executable,
        "-m",
        "groundtruth_kb.bridge.worker",
        "--agent",
        agent,
        "--project-dir",
        str(project_dir),
        "--cadence-minutes",
        str(cadence_minutes),
        "--timeout-seconds",
        str(timeout_seconds),
        "--poll-interval-ms",
        str(poll_interval_ms),
        "--limit",
        str(limit),
        "--max-dispatch-targets",
        str(max_dispatch_targets),
        "--exec-timeout-seconds",
        str(exec_timeout_seconds),
        "--error-backoff-seconds",
        str(error_backoff_seconds),
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(project_dir),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
    return int(proc.pid)


def _run_once_wake(
    project_dir: Path,
    *,
    agent: str,
    cadence_minutes: int,
    exec_timeout_seconds: int,
) -> tuple[bool, str]:
    cmd = [
        sys.executable,
        str(project_dir / "scripts" / "codex_bridge_wake.py"),
        "--agent",
        agent,
        "--cadence-minutes",
        str(cadence_minutes),
        "--timeout-seconds",
        str(exec_timeout_seconds),
        "--trigger",
        "resident-worker-launcher-fallback",
    ]
    completed = subprocess.run(
        cmd,
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0, (completed.stdout or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure resident bridge worker daemon is running")
    parser.add_argument("--agent", choices=["codex", "prime"], default="codex")
    parser.add_argument("--cadence-minutes", type=int, default=9)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--poll-interval-ms", type=int, default=100)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-dispatch-targets", type=int, default=6)
    parser.add_argument("--exec-timeout-seconds", type=int, default=900)
    parser.add_argument("--error-backoff-seconds", type=int, default=5)
    parser.add_argument("--auto-actions", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--json-output", action="store_true", help="Print structured JSON result")
    parser.add_argument(
        "--project-dir", type=str, default=None, help="Project directory (defaults to CLAUDE_PROJECT_DIR or cwd)"
    )
    return parser


def _try_start_scheduled_task(agent: str) -> bool:
    """Try to start the Windows Scheduled Task for the bridge worker.

    Returns True if the task exists and was started (or is already running).
    Returns False if the task is not registered.
    """
    if os.name != "nt":
        return False
    task_name = f"GroundTruthBridgeWorker-{agent}"
    try:
        result = subprocess.run(
            ["schtasks.exe", "/Run", "/TN", task_name],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:  # intentional-catch: schtasks fallback, returns False
        return False


def _scheduled_task_exists(agent: str) -> bool:
    """Check if the Windows Scheduled Task is registered."""
    if os.name != "nt":
        return False
    task_name = f"GroundTruthBridgeWorker-{agent}"
    try:
        result = subprocess.run(
            ["schtasks.exe", "/Query", "/TN", task_name],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:  # intentional-catch: schtasks query fallback, returns False
        return False


def main() -> int:
    from groundtruth_kb._logging import _setup_bridge_logging

    _consume_stdin_if_present()
    args = build_parser().parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
    # Launcher diagnostics go to a dedicated log file
    hooks_dir = project_dir / ".claude" / "hooks"
    _setup_bridge_logging(hooks_dir / f".bridge-launcher-{args.agent}.log")

    # Step 1: Check if worker is already healthy
    running = _discover_running_worker(project_dir, args.agent)
    if running:
        payload = {"ok": True, "running": True, **running}
        if args.json_output:
            print(json.dumps(payload))
        else:
            print("{}")
        return 0

    # Step 2 (Phase B): Try scheduled task first -- canonical runtime
    if _scheduled_task_exists(args.agent):
        _try_start_scheduled_task(args.agent)
        # Wait briefly for health to appear
        time.sleep(3)
        running = _discover_running_worker(project_dir, args.agent)
        if running:
            payload = {"ok": True, "running": True, "source": "scheduled-task", **running}
            if args.json_output:
                print(json.dumps(payload))
            else:
                print("{}")
            return 0

    # Step 3: Fallback -- detached process launch (legacy, pre-Phase B)
    try:
        new_pid = _start_detached(
            project_dir,
            agent=args.agent,
            cadence_minutes=args.cadence_minutes,
            timeout_seconds=args.timeout_seconds,
            poll_interval_ms=args.poll_interval_ms,
            limit=args.limit,
            max_dispatch_targets=args.max_dispatch_targets,
            exec_timeout_seconds=args.exec_timeout_seconds,
            error_backoff_seconds=args.error_backoff_seconds,
        )
        running = _wait_for_worker(
            project_dir,
            agent=args.agent,
            expected_pid=new_pid,
            timeout_seconds=5.0,
        )
        if not running:
            running = _discover_running_worker(project_dir, args.agent)
        if not running:
            raise RuntimeError("resident worker did not publish healthy state after launch")

        payload = {"ok": True, "running": True, "source": "detached-fallback", **running}
        if args.json_output:
            print(json.dumps(payload))
        else:
            print("{}")
        return 0
    except Exception as exc:  # intentional-catch: detached launch fallback, logged
        ok_once, out_once = _run_once_wake(
            project_dir,
            agent=args.agent,
            cadence_minutes=args.cadence_minutes,
            exec_timeout_seconds=args.exec_timeout_seconds,
        )
        payload = {
            "ok": ok_once,
            "running": False,
            "mode": "oneshot-fallback",
            "error": str(exc),
            "agent": args.agent,
            "oneshot_output": out_once,
        }
        if args.json_output:
            print(json.dumps(payload))
        else:
            print("{}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
