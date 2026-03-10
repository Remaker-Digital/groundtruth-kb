"""Real-time subprocess output streaming with simultaneous capture.

Replaces subprocess.run(capture_output=True) throughout all automation
scripts.  Every line of subprocess output appears on the owner's terminal
in real time while being captured for log files and result parsing.

Usage:
    from scripts._subprocess_stream import stream_subprocess, SubprocessResult

    result = stream_subprocess(
        ["pytest", "tests/", "-v"],
        cwd=PROJECT_ROOT,
        prefix="  [pytest] ",
    )
    if result.returncode != 0:
        print(f"FAILED in {result.duration:.1f}s")
    # result.stdout contains the complete captured output

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SubprocessResult:
    """Result of a streamed subprocess execution."""

    returncode: int
    stdout: str
    duration: float
    timed_out: bool = False


def stream_subprocess(
    cmd: list[str] | str,
    *,
    cwd: Path | str | None = None,
    timeout: int = 600,
    prefix: str = "",
    env: dict[str, str] | None = None,
) -> SubprocessResult:
    """Run a subprocess with real-time line-by-line output streaming.

    All output (stdout + stderr merged) is printed to the terminal in real
    time AND captured in the returned SubprocessResult.stdout for log files
    and parsing.

    On Windows, list commands are converted via list2cmdline + shell=True
    because az/node/npm are .cmd wrappers that cannot be found by
    CreateProcess directly.

    Args:
        cmd: Command as list or string.
        cwd: Working directory.
        timeout: Maximum execution time in seconds.
        prefix: String prepended to each output line (e.g. "  [build] ").
        env: Environment variables (defaults to current env if None).

    Returns:
        SubprocessResult with returncode, captured stdout, duration, timed_out.
    """
    # Windows .cmd wrapper fix: list2cmdline + shell=True
    if isinstance(cmd, list) and sys.platform == "win32":
        cmd_str: str | list[str] = subprocess.list2cmdline(cmd)
        use_shell = True
    elif isinstance(cmd, str):
        cmd_str = cmd
        use_shell = True
    else:
        cmd_str = cmd
        use_shell = False

    t0 = time.time()
    lines: list[str] = []
    timed_out = False

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

    # Force UTF-8 on subprocess stdout so pytest/node/az emit valid UTF-8
    # regardless of the Windows console codepage (cp1252).
    sub_env = (env if env is not None else os.environ.copy())
    if sys.platform == "win32":
        sub_env.setdefault("PYTHONIOENCODING", "utf-8")

    proc = subprocess.Popen(
        cmd_str,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=use_shell,
        cwd=str(cwd) if cwd else None,
        env=sub_env,
        creationflags=creation_flags,
    )

    # Ensure our own stdout can handle arbitrary Unicode (belt-and-suspenders
    # for the print() call inside _reader — if PYTHONIOENCODING didn't take
    # effect on the subprocess, decoded replacement chars must not crash us).
    _safe_stdout = sys.stdout
    if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
        try:
            _safe_stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
                line_buffering=True,
            )
        except Exception:
            pass  # fall back to original stdout

    def _reader():
        """Read lines from proc.stdout and print + capture each one."""
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            try:
                line = raw_line.decode("utf-8", errors="replace")
            except Exception:
                line = raw_line.decode("cp1252", errors="replace")
            line = line.rstrip("\n\r")
            lines.append(line)
            try:
                print(f"{prefix}{line}", flush=True, file=_safe_stdout)
            except (UnicodeEncodeError, OSError, ValueError):
                # Last resort: ASCII-safe output so the thread never dies.
                # ValueError = "I/O operation on closed file" (background tasks).
                try:
                    safe = line.encode("ascii", errors="replace").decode()
                    print(f"{prefix}{safe}", flush=True)
                except (OSError, ValueError):
                    pass  # stdout completely gone — still captured in lines[]
        proc.stdout.close()

    reader_thread = threading.Thread(target=_reader, daemon=True)
    reader_thread.start()

    # Timeout enforcement
    def _timeout_kill():
        nonlocal timed_out
        timed_out = True
        try:
            if sys.platform == "win32":
                # S164: On Windows with shell=True, proc.kill() only kills
                # the shell (cmd.exe), not child processes (pytest/playwright).
                # Use taskkill /T to kill the entire process tree.
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True, timeout=10,
                )
            else:
                proc.kill()
        except (OSError, subprocess.TimeoutExpired):
            pass

    timer = threading.Timer(timeout, _timeout_kill)
    timer.start()

    try:
        proc.wait()
    finally:
        timer.cancel()
        reader_thread.join(timeout=5)

    # Detach the temporary TextIOWrapper so its __del__ does not close the
    # underlying sys.stdout.buffer when the local variable goes out of scope.
    if _safe_stdout is not sys.stdout and hasattr(_safe_stdout, "detach"):
        try:
            _safe_stdout.detach()
        except Exception:
            pass

    duration = time.time() - t0
    stdout = "\n".join(lines)

    return SubprocessResult(
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=stdout,
        duration=duration,
        timed_out=timed_out,
    )
