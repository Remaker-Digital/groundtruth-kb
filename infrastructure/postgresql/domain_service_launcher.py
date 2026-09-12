"""Start the GT-KB native domain service unattended.

Runs the installed package's ``service serve`` on IPv4 loopback with the service credential environment set only in
this process: ``PGSERVICEFILE`` points at the installation's credential file and the operator config selects the
PostgreSQL service under ``[postgresql]``. Every inherited ``PG*`` value, every inherited ``GT_POSTGRES_*`` override
(the configuration loader maps those onto the ``[postgresql]`` section and would redirect the service selection) and
any inherited ``GT_AUTHORITY_URL`` are dropped first. On Windows the service runs inside a job object that ends every
process in it when this launcher ends, so stopping the launcher (the scheduled task, an operator, a test) never leaves
a listener behind. Containment is established before the service executes a single instruction: the job is created
first (no job, nothing is started), the service process is created suspended, placed in the job, and only then
resumed, so no descendant can ever exist outside the job. If the service cannot be placed in the job or resumed it
is ended while still suspended and the launcher exits 3 rather than serve uncontained. Output is appended to
``infrastructure/postgresql/logs/domain-service.log``. The launcher is what the scheduled task ``GTKB-DomainService``
executes (see ``register-domain-service.ps1``); it can also be run by an operator directly. It never prints or copies
credential values.

Usage: domain_service_launcher.py --root <gt-kb root> [--port 8765] [--config <operator-config.toml>] [--print-command]
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

DROPPED_PREFIXES = ("PG", "GT_POSTGRES_", "GT_AUTHORITY_URL")
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
CREATE_SUSPENDED = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
TH32CS_SNAPTHREAD = 0x00000004
EXIT_UNCONTAINED = 3


class ContainmentError(RuntimeError):
    """The service could not be contained; it was ended before it ran."""


def build(root: Path, port: int, config: Path | None) -> tuple[list[str], dict[str, str], Path]:
    """Return (argv, environment, log path) for the service process; pure, no side effects."""
    installation = root / "infrastructure" / "postgresql"
    credentials = installation / "credentials" / "pg_service.conf"
    operator_config = config or installation / "operator-config.toml"
    log = installation / "logs" / "domain-service.log"
    interpreter = root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        interpreter = Path(sys.executable)
    argv = [
        str(interpreter),
        "-m",
        "groundtruth_kb",
        "--config",
        str(operator_config),
        "service",
        "serve",
        "--port",
        str(port),
    ]
    environment = {k: v for k, v in os.environ.items() if not k.startswith(DROPPED_PREFIXES)}
    environment["PGSERVICEFILE"] = str(credentials)
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["GT_PROJECT_ROOT"] = str(root)
    return argv, environment, log


def _kill_on_close_job() -> int | None:
    """Create a Windows job object whose processes end when its last handle closes (this launcher's exit)."""
    if os.name != "nt":
        return None
    from ctypes import wintypes

    class BasicLimit(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            (name, ctypes.c_uint64)
            for name in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )
        ]

    class ExtendedLimit(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimit),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.windll.kernel32
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None
    limits = ExtendedLimit()
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)
    ):
        kernel32.CloseHandle(job)
        return None
    return job


def _assign(job: int | None, process: subprocess.Popen) -> bool:
    if job is None or os.name != "nt":
        return False
    return bool(ctypes.windll.kernel32.AssignProcessToJobObject(job, int(process._handle)))  # noqa: SLF001


def _resume(process: subprocess.Popen) -> bool:
    """Resume the primary thread of a process created suspended.

    ``subprocess.Popen`` keeps no thread handle, so the thread is found through a Toolhelp snapshot by its owning
    process. A process created suspended has exactly that one thread until it is resumed.
    """
    if os.name != "nt":
        return True
    from ctypes import wintypes

    class ThreadEntry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThreadEntry)]
    kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThreadEntry)]
    kernel32.OpenThread.restype = wintypes.HANDLE
    kernel32.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.ResumeThread.restype = wintypes.DWORD
    kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if not snapshot or snapshot == ctypes.c_void_p(-1).value:
        return False
    resumed = False
    try:
        entry = ThreadEntry()
        entry.dwSize = ctypes.sizeof(entry)
        found = kernel32.Thread32First(snapshot, ctypes.byref(entry))
        while found:
            if entry.th32OwnerProcessID == process.pid:
                thread = kernel32.OpenThread(THREAD_SUSPEND_RESUME, False, entry.th32ThreadID)
                if thread:
                    previous = kernel32.ResumeThread(thread)
                    kernel32.CloseHandle(thread)
                    resumed = resumed or previous != 0xFFFFFFFF
            found = kernel32.Thread32Next(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return resumed


def _end(process: subprocess.Popen) -> None:
    """End a process that has not been allowed to run (or must not continue) and reap it."""
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.wait(timeout=15)


def _start_contained(
    argv: list[str],
    environment: dict[str, str],
    job: int,
    *,
    cwd: Path | None = None,
    stdout=None,
    stderr=None,
    assign: Callable[[int | None, subprocess.Popen], bool] = _assign,
    resume: Callable[[subprocess.Popen], bool] = _resume,
) -> subprocess.Popen:
    """Create the service suspended, place it in the job, then let it run.

    The service cannot execute (and so cannot create a descendant) before it is in the job. If it cannot be placed in
    the job or resumed it is ended while still suspended, leaving no child and no descendant, and ContainmentError is
    raised.
    """
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=environment,
        stdout=stdout,
        stderr=stderr,
        creationflags=CREATE_SUSPENDED | getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if not assign(job, process):
        _end(process)
        raise ContainmentError(f"service process {process.pid} could not be placed in the job; ended before it ran")
    if not resume(process):
        _end(process)
        raise ContainmentError(f"service process {process.pid} could not be resumed; ended before it ran")
    return process


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def serve(
    argv: list[str],
    environment: dict[str, str],
    log: Path,
    port: int,
    *,
    cwd: Path | None = None,
    job_factory: Callable[[], int | None] = _kill_on_close_job,
    assign: Callable[[int | None, subprocess.Popen], bool] = _assign,
    resume: Callable[[subprocess.Popen], bool] = _resume,
) -> int:
    """Run the service to completion under job containment; refuse (exit 3) when containment cannot be established.

    On Windows nothing is started unless a kill-on-close job exists, and the service is created suspended, placed in
    that job and only then resumed. Elsewhere there is no job containment and the service simply runs.
    """
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as stream:
        stream.write(f"[{_stamp()}] starting domain service on 127.0.0.1:{port}\n".encode())
        stream.flush()
        if os.name == "nt":
            job = job_factory()
            if job is None:
                stream.write(
                    f"[{_stamp()}] refused: job object unavailable; nothing started; exit {EXIT_UNCONTAINED}\n".encode()
                )
                return EXIT_UNCONTAINED
            try:
                process = _start_contained(
                    argv, environment, job, cwd=cwd, stdout=stream, stderr=stream, assign=assign, resume=resume
                )
            except ContainmentError as error:
                stream.write(f"[{_stamp()}] refused: {error}; exit {EXIT_UNCONTAINED}\n".encode())
                return EXIT_UNCONTAINED
            stream.write(
                f"[{_stamp()}] service process {process.pid} contained by a kill-on-close job before it ran\n".encode()
            )
        else:
            process = subprocess.Popen(argv, cwd=cwd, env=environment, stdout=stream, stderr=stream)
            stream.write(
                f"[{_stamp()}] service process {process.pid} started (no job containment on this platform)\n".encode()
            )
        stream.flush()
        code = process.wait()
        stream.write(f"[{_stamp()}] domain service exited with {code}\n".encode())
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument(
        "--print-command", action="store_true", help="Show the command and environment keys; start nothing."
    )
    args = parser.parse_args()
    root = args.root.resolve()
    argv, environment, log = build(root, args.port, args.config)
    if args.print_command:
        print(" ".join(argv))
        print("environment keys:", ", ".join(sorted(k for k in environment if k.startswith(("PG", "GT_", "PYTHON")))))
        print("log:", log)
        return 0
    for required, message in (
        (Path(environment["PGSERVICEFILE"]), "credential file"),
        (Path(argv[4]), "operator config"),
    ):
        if not required.is_file():
            print(f"{message} missing: {required}", file=sys.stderr)
            return 2
    return serve(argv, environment, log, args.port, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
