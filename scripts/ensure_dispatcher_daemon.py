#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Idempotent ensure-alive entrypoint for the GT-KB dispatcher daemon (WI-4882).

Invoked by the ``GTKB-DispatcherDaemon`` Windows scheduled task on a fixed
interval. Unlike ``gt bridge dispatch daemon start`` (cli.py), which RAISES
"already running" (non-zero exit) when the daemon is alive, this entrypoint is
idempotent: it no-ops and exits 0 when the daemon is alive, and spawns a
detached daemon and exits 0 when it is dead. This is the D3 supervision
mechanism from the Daemon Resilience scope-lock (DELIB-20266276): a dedicated
scheduled task, separate from the storm-watchdog, that keeps the daemon alive
unattended.

The detached-spawn mirrors the cli ``daemon start`` path so the daemon survives
its launching task (WI-4855 true-detach semantics).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import gtkb_dispatcher_daemon as daemon  # noqa: E402


def _spawn_detached_daemon(project_root: Path, interval: int) -> int:
    """Spawn the detached daemon loop, mirroring the cli start spawn (WI-4855 true detach)."""
    script = _SCRIPTS_DIR / "gtkb_dispatcher_daemon.py"
    popen_kwargs: dict[str, object] = {"cwd": str(project_root)}
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
    else:
        popen_kwargs["start_new_session"] = True
    proc = subprocess.Popen(
        [
            sys.executable,
            str(script),
            "--loop",
            "--project-root",
            str(project_root),
            "--tick-seconds",
            str(interval),
        ],
        **popen_kwargs,
    )
    return int(proc.pid)


def ensure_daemon_running(project_root: Path, interval: int) -> dict[str, object]:
    """Idempotently ensure the dispatcher daemon is running.

    Returns a result dict describing the action taken. Never raises on the
    already-running path: when the daemon is alive this is a pure no-op.
    """
    state_dir = daemon.daemon_state_dir(project_root)
    running = bool(daemon.read_daemon_status(project_root).get("running"))
    alive = running or daemon.daemon_process_alive(state_dir)
    if alive:
        return {"action": "noop", "running": True}
    pid = _spawn_detached_daemon(project_root, interval)
    return {"action": "spawned", "running": True, "pid": pid}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Idempotently ensure the GT-KB dispatcher daemon is running (WI-4882 supervisor)."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--interval", type=int, default=30, help="Daemon tick interval seconds.")
    args = parser.parse_args(argv)
    result = ensure_daemon_running(args.project_root.resolve(), args.interval)
    suffix = f" pid={result['pid']}" if "pid" in result else ""
    print(f"ensure-dispatcher-daemon: {result['action']} running={result['running']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
