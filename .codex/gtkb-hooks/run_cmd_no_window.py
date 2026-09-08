# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run a Codex .cmd hook without creating a visible Windows console."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000
DEFAULT_TIMEOUT_SECONDS = 4.0
DEFAULT_STDIN_TIMEOUT_SECONDS = 0.2


def _child_timeout_seconds() -> float:
    raw = os.environ.get("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS")
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_TIMEOUT_SECONDS


def _stdin_timeout_seconds() -> float:
    raw = os.environ.get("GTKB_CODEX_HOOK_STDIN_TIMEOUT_SECONDS")
    if not raw:
        return DEFAULT_STDIN_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_STDIN_TIMEOUT_SECONDS
    return value if value >= 0 else DEFAULT_STDIN_TIMEOUT_SECONDS


def _read_hook_payload() -> bytes:
    if sys.stdin is None or sys.stdin.closed:
        return b""
    if sys.stdin.isatty():
        return b""
    payload: list[bytes] = []

    def _reader() -> None:
        payload.append(sys.stdin.buffer.read())

    thread = threading.Thread(target=_reader, daemon=True)
    thread.start()
    thread.join(_stdin_timeout_seconds())
    if thread.is_alive():
        return b""
    return payload[0] if payload else b""


def _no_window_flags() -> int:
    if sys.platform != "win32":
        return 0
    return CREATE_NO_WINDOW | int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))


def _kill_process_tree(pid: int) -> None:
    if sys.platform != "win32":
        return
    subprocess.run(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        creationflags=CREATE_NO_WINDOW,
    )


def _run_child(command: list[str], payload: bytes) -> tuple[int, bytes, bytes]:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=_no_window_flags(),
    )
    try:
        stdout, stderr = process.communicate(input=payload, timeout=_child_timeout_seconds())
    except subprocess.TimeoutExpired:
        _kill_process_tree(process.pid)
        try:
            process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            process.kill()
        return 124, b"", f"hook child timed out: {command[0]}\n".encode()
    return int(process.returncode), stdout or b"", stderr or b""


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: run_cmd_no_window.py <hook.cmd> [args...]", file=sys.stderr)
        return 2
    script = Path(argv[0])
    if script.suffix.lower() != ".cmd":
        print(f"refusing non-.cmd hook target: {script}", file=sys.stderr)
        return 2
    hook_payload = _read_hook_payload()
    returncode, stdout, stderr = _run_child([str(script), *argv[1:]], hook_payload)
    if stdout:
        sys.stdout.buffer.write(stdout)
    if stderr:
        sys.stderr.buffer.write(stderr)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
