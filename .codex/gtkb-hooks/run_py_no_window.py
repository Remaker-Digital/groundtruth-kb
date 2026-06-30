# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run a Python hook script without creating a visible Windows console."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from windows_subprocess import no_window_subprocess_kwargs, prefer_pythonw_executable  # noqa: E402

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


def _kill_process_tree(pid: int) -> None:
    if sys.platform != "win32":
        return
    subprocess.run(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        **no_window_subprocess_kwargs(),
    )


def _run_child(command: list[str], payload: bytes) -> tuple[int, bytes, bytes]:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **no_window_subprocess_kwargs(),
    )
    try:
        stdout, stderr = process.communicate(input=payload, timeout=_child_timeout_seconds())
    except subprocess.TimeoutExpired:
        _kill_process_tree(process.pid)
        try:
            process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            process.kill()
        return 124, b"", f"hook child timed out: {command[1] if len(command) > 1 else command[0]}\n".encode()
    return int(process.returncode), stdout or b"", stderr or b""


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: run_py_no_window.py <hook.py> [args...]", file=sys.stderr)
        return 2
    script = Path(argv[0])
    if script.suffix.lower() != ".py":
        print(f"refusing non-.py hook target: {script}", file=sys.stderr)
        return 2
    hook_payload = _read_hook_payload()
    returncode, stdout, stderr = _run_child(
        [prefer_pythonw_executable(sys.executable), str(script), *argv[1:]],
        hook_payload,
    )
    if stdout:
        sys.stdout.buffer.write(stdout)
    if stderr:
        sys.stderr.buffer.write(stderr)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
