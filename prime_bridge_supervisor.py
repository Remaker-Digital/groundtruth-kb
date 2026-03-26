"""
Prime Bridge MCP Server Supervisor
===================================
Wraps prime_bridge_runtime.py with crash detection, stderr logging,
and automatic restart.  The .mcp.json "command" points here instead
of directly at the runtime.

Supervision features:
  - Captures runtime stderr → .prime-bridge-mcp.log (rotating, 1 MB max)
  - Detects unexpected exit and auto-restarts (up to MAX_RESTARTS in RESTART_WINDOW)
  - Logs startup/exit/restart events with timestamps
  - Proxies stdin/stdout transparently for MCP stdio transport
  - Health breadcrumb file: .prime-bridge-mcp-health.json

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RUNTIME_SCRIPT = Path(__file__).resolve().parent / "prime_bridge_runtime.py"
PYTHON_EXE = sys.executable  # Same Python that launched us
LOG_DIR = Path(__file__).resolve().parent / ".claude" / "hooks"
LOG_FILE = LOG_DIR / ".prime-bridge-mcp.log"
HEALTH_FILE = Path(__file__).resolve().parent / ".prime-bridge-mcp-health.json"
MAX_LOG_BYTES = 1_048_576  # 1 MB
MAX_RESTARTS = 5
RESTART_WINDOW = 300  # seconds — max 5 restarts in 5 minutes
RESTART_BACKOFF_BASE = 2  # seconds — exponential backoff base

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rotate_log() -> None:
    """Rotate log if it exceeds MAX_LOG_BYTES."""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_BYTES:
        rotated = LOG_FILE.with_suffix(".log.1")
        if rotated.exists():
            rotated.unlink()
        LOG_FILE.rename(rotated)


def _log(msg: str) -> None:
    """Append a timestamped line to the supervisor log."""
    _rotate_log()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{_now_iso()}] [supervisor] {msg}\n")


def _write_health(status: str, pid: int | None = None, restarts: int = 0,
                   last_exit: str | None = None) -> None:
    """Write a health breadcrumb for external monitoring."""
    doc = {
        "status": status,
        "pid": pid,
        "supervisor_pid": os.getpid(),
        "restarts": restarts,
        "last_exit_reason": last_exit,
        "updated_at": _now_iso(),
    }
    try:
        with open(HEALTH_FILE, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
    except OSError:
        pass  # Non-fatal — health file is advisory


# ---------------------------------------------------------------------------
# Stderr reader thread
# ---------------------------------------------------------------------------

def _stderr_reader(proc: subprocess.Popen) -> None:
    """Read stderr from the child process and write to the log file."""
    try:
        assert proc.stderr is not None
        for line in proc.stderr:
            _log(f"[runtime-stderr] {line.rstrip()}")
    except (ValueError, OSError):
        pass  # Pipe closed


# ---------------------------------------------------------------------------
# Stdin proxy thread
# ---------------------------------------------------------------------------

def _stdin_proxy(proc: subprocess.Popen) -> None:
    """
    Read from our stdin (which the MCP host writes to) and forward
    to the child process stdin.  This is the MCP stdio transport's
    inbound path.
    """
    try:
        assert proc.stdin is not None
        while True:
            data = sys.stdin.buffer.read(4096)
            if not data:
                proc.stdin.close()
                break
            proc.stdin.write(data)
            proc.stdin.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass  # Parent or child closed


# ---------------------------------------------------------------------------
# Stdout proxy (main thread)
# ---------------------------------------------------------------------------

def _stdout_proxy(proc: subprocess.Popen) -> str | None:
    """
    Read from child stdout and write to our stdout (which the MCP
    host reads from).  Returns exit reason string when child exits
    or pipe breaks.
    """
    try:
        assert proc.stdout is not None
        while True:
            data = proc.stdout.read(4096)
            if not data:
                return "stdout-eof"
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    except (BrokenPipeError, OSError):
        return "stdout-broken-pipe"
    except ValueError:
        return "stdout-closed"


# ---------------------------------------------------------------------------
# Main supervisor loop
# ---------------------------------------------------------------------------

def main() -> None:
    restart_times: list[float] = []
    restart_count = 0

    _log(f"Supervisor starting. Runtime: {RUNTIME_SCRIPT}")
    _log(f"Python: {PYTHON_EXE}, PID: {os.getpid()}")

    # Forward PRIME_BRIDGE_DB env var
    env = os.environ.copy()

    while True:
        # Check restart budget
        now = time.monotonic()
        restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
        if len(restart_times) >= MAX_RESTARTS:
            _log(f"FATAL: {MAX_RESTARTS} restarts in {RESTART_WINDOW}s — giving up.")
            _write_health("crashed", restarts=restart_count,
                          last_exit="restart-budget-exhausted")
            sys.exit(1)

        # Launch the runtime
        _log(f"Launching runtime (restart #{restart_count})...")
        try:
            proc = subprocess.Popen(
                [PYTHON_EXE, str(RUNTIME_SCRIPT)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                bufsize=0,  # Unbuffered for real-time proxy
            )
        except OSError as e:
            _log(f"Failed to launch runtime: {e}")
            _write_health("launch-failed", restarts=restart_count, last_exit=str(e))
            time.sleep(RESTART_BACKOFF_BASE ** min(restart_count, 5))
            restart_count += 1
            restart_times.append(time.monotonic())
            continue

        _log(f"Runtime launched, PID={proc.pid}")
        _write_health("running", pid=proc.pid, restarts=restart_count)

        # Start stderr reader thread
        stderr_thread = threading.Thread(
            target=_stderr_reader, args=(proc,), daemon=True
        )
        stderr_thread.start()

        # Start stdin proxy thread
        stdin_thread = threading.Thread(
            target=_stdin_proxy, args=(proc,), daemon=True
        )
        stdin_thread.start()

        # Main thread: proxy stdout
        exit_reason = _stdout_proxy(proc)

        # Child exited — collect return code
        proc.wait()
        rc = proc.returncode
        _log(f"Runtime exited: rc={rc}, reason={exit_reason}")

        # If our own stdin is closed (parent MCP host exited), don't restart
        if exit_reason == "stdout-broken-pipe":
            _log("Parent pipe broken — MCP host likely exited. Shutting down.")
            _write_health("stopped", pid=None, restarts=restart_count,
                          last_exit="parent-pipe-broken")
            sys.exit(0)

        # Normal exit (rc=0) — don't restart
        if rc == 0:
            _log("Runtime exited cleanly (rc=0). Shutting down.")
            _write_health("stopped", pid=None, restarts=restart_count,
                          last_exit="clean-exit")
            sys.exit(0)

        # Abnormal exit — restart with backoff
        backoff = RESTART_BACKOFF_BASE ** min(restart_count, 5)
        _log(f"Abnormal exit (rc={rc}). Restarting in {backoff}s...")
        _write_health("restarting", pid=None, restarts=restart_count,
                      last_exit=f"rc={rc}")
        time.sleep(backoff)
        restart_count += 1
        restart_times.append(time.monotonic())


if __name__ == "__main__":
    # Graceful shutdown on SIGTERM/SIGINT
    def _shutdown(signum, frame):
        _log(f"Supervisor received signal {signum}. Exiting.")
        _write_health("stopped", last_exit=f"signal-{signum}")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    main()
