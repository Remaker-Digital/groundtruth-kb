#!/usr/bin/env python3
"""
SessionStart launcher for bridge_poller.py.

Ensures a detached poller process is running for the selected agent.
Designed for use in Claude hook commands (returns JSON {} by default).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _consume_stdin_if_present() -> None:
    try:
        if not sys.stdin.isatty():
            _ = sys.stdin.read()
    except Exception:
        pass


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not handle:
                return False
            exit_code = wintypes.DWORD()
            ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(handle)
            return int(exit_code.value) == STILL_ACTIVE
        except Exception:
            return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except Exception:
        return False
    return True


def _read_pid(pid_file: Path) -> int | None:
    try:
        data = json.loads(pid_file.read_text(encoding="utf-8"))
        return int(data.get("pid", 0))
    except Exception:
        return None


def _read_state(state_file: Path) -> dict | None:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _heartbeat_ttl_seconds(timeout_seconds: int, poll_interval_ms: int) -> float:
    poll_interval_seconds = max(1.0, poll_interval_ms / 1000.0)
    return max(30.0, float(timeout_seconds) + poll_interval_seconds + 5.0)


def _discover_running_poller(
    pid_file: Path,
    state_file: Path,
    *,
    agent: str,
    heartbeat_ttl_seconds: float,
) -> dict | None:
    state = _read_state(state_file) or {}
    state_pid = int(state.get("pid", 0) or 0)
    state_agent = state.get("agent")
    updated_at = _parse_iso(state.get("updated_at"))
    if (
        state_pid > 0
        and state_agent == agent
        and updated_at is not None
        and _pid_is_running(state_pid)
    ):
        age_seconds = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age_seconds <= heartbeat_ttl_seconds:
            return {
                "pid": state_pid,
                "agent": agent,
                "source": "heartbeat",
                "updated_at": state.get("updated_at"),
            }

    current_pid = _read_pid(pid_file)
    if current_pid and _pid_is_running(current_pid):
        return {
            "pid": current_pid,
            "agent": agent,
            "source": "pid",
            "updated_at": state.get("updated_at"),
        }
    return None


def _wait_for_heartbeat(
    pid_file: Path,
    state_file: Path,
    *,
    agent: str,
    expected_pid: int,
    timeout_seconds: float,
    heartbeat_ttl_seconds: float,
) -> dict | None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        running = _discover_running_poller(
            pid_file,
            state_file,
            agent=agent,
            heartbeat_ttl_seconds=heartbeat_ttl_seconds,
        )
        if running and running.get("pid") == expected_pid:
            return running
        if not _pid_is_running(expected_pid):
            break
        time.sleep(0.1)
    return None


def _start_detached(
    project_dir: Path,
    agent: str,
    timeout_seconds: int,
    poll_interval_ms: int,
    limit: int,
    auto_actions: bool,
) -> int:
    if os.name == "nt":
        # Start outside the current process/job via PowerShell Start-Process.
        # This survives short-lived hook process lifetimes.
        py = str(Path(sys.executable).resolve())
        script = str((project_dir / "bridge_poller.py").resolve())

        # Build argument string (not array) so paths with spaces are preserved.
        # Start-Process -ArgumentList as a single string passes it to python.exe
        # as-is, avoiding PowerShell's array-to-command-line re-splitting.
        arg_parts = [
            f'"{script}"',
            "--agent", agent,
            "--timeout-seconds", str(timeout_seconds),
            "--poll-interval-ms", str(poll_interval_ms),
            "--limit", str(limit),
        ]
        if auto_actions:
            arg_parts.append("--auto-actions")
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
        str(project_dir / "bridge_poller.py"),
        "--agent",
        agent,
        "--timeout-seconds",
        str(timeout_seconds),
        "--poll-interval-ms",
        str(poll_interval_ms),
        "--limit",
        str(limit),
    ]
    if auto_actions:
        cmd.append("--auto-actions")
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


def _run_once_poll(project_dir: Path, agent: str, limit: int, auto_actions: bool) -> tuple[bool, str]:
    cmd = [
        sys.executable,
        str(project_dir / "bridge_poller.py"),
        "--agent",
        agent,
        "--once",
        "--limit",
        str(limit),
    ]
    if auto_actions:
        cmd.append("--auto-actions")
    completed = subprocess.run(
        cmd,
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )
    ok = completed.returncode == 0
    out = (completed.stdout or "").strip()
    return ok, out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure bridge poller daemon is running")
    parser.add_argument("--agent", choices=["codex", "prime"], default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--poll-interval-ms", type=int, default=500)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--auto-actions", action="store_true")
    parser.add_argument("--json-output", action="store_true", help="Print structured JSON result")
    return parser


def main() -> int:
    _consume_stdin_if_present()
    args = build_parser().parse_args()

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parent))
    hooks_dir = project_dir / ".claude" / "hooks"
    pid_file = hooks_dir / f".bridge-poller-{args.agent}.pid"
    state_file = hooks_dir / f".bridge-poller-state-{args.agent}.json"
    heartbeat_ttl_seconds = _heartbeat_ttl_seconds(
        args.timeout_seconds,
        args.poll_interval_ms,
    )

    running = _discover_running_poller(
        pid_file,
        state_file,
        agent=args.agent,
        heartbeat_ttl_seconds=heartbeat_ttl_seconds,
    )
    if running:
        payload = {"ok": True, "running": True, **running}
        if args.json_output:
            print(json.dumps(payload))
        else:
            # Hook-safe default: no extra context injection.
            print("{}")
        return 0

    try:
        new_pid = _start_detached(
            project_dir=project_dir,
            agent=args.agent,
            timeout_seconds=args.timeout_seconds,
            poll_interval_ms=args.poll_interval_ms,
            limit=args.limit,
            auto_actions=args.auto_actions,
        )
        running = _wait_for_heartbeat(
            pid_file,
            state_file,
            agent=args.agent,
            expected_pid=new_pid,
            timeout_seconds=5.0,
            heartbeat_ttl_seconds=heartbeat_ttl_seconds,
        )
        if not running:
            running = _discover_running_poller(
                pid_file,
                state_file,
                agent=args.agent,
                heartbeat_ttl_seconds=heartbeat_ttl_seconds,
            )
        if not running:
            raise RuntimeError("bridge poller did not publish a heartbeat after launch")

        payload = {"ok": True, "running": True, **running}
        if args.json_output:
            print(json.dumps(payload))
        else:
            print("{}")
        return 0
    except Exception as exc:
        # Resilient fallback: run a one-shot poll so hooks still scan bridge activity.
        ok_once, out_once = _run_once_poll(
            project_dir,
            args.agent,
            args.limit,
            args.auto_actions,
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
        # Hook-safe: don't hard-fail session hooks on daemon launch issues.
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
