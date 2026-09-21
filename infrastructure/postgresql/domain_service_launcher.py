"""Start the GT-KB native domain service unattended.

Runs the installed package's ``service serve`` on IPv4 loopback with the service credential environment set only in
this process: ``PGSERVICEFILE`` points at the installation's credential file and the operator config selects the
PostgreSQL service under ``[postgresql]``. Every inherited ``PG*`` value, every inherited ``GT_POSTGRES_*`` override
(the configuration loader maps those onto the ``[postgresql]`` section and would redirect the service selection) and
any inherited ``GT_AUTHORITY_URL`` are dropped first. On Windows the service runs inside a named kill-on-close job
object for this installation root (``Local\\gtkb-domain-service-<first 24 hex digits of the sha256 of the normalized
--root>``, created through ``groundtruth_kb.job_containment``, the mechanics shared with ``gt dashboard`` under owner
ruling D27); the job handle is not inherited, so it ends every process in the job when this launcher ends, and
stopping the launcher (the scheduled task, an operator, a test) never leaves a listener behind. Containment is
established before the service executes a single instruction: the job is created first (no job, or a name already
held by another launcher for the same root: nothing is started, exit 3), the service process is created suspended,
placed in the job, and only then resumed, so no descendant can ever exist outside the job. If the service cannot be
placed in the job or resumed it is ended while still suspended and the launcher exits 3 rather than serve
uncontained. An interpreter that cannot import ``groundtruth_kb`` (the scheduled task uses the project venv's
pythonw.exe, see ``register-domain-service.ps1``), or whose installation raises while importing it, still
composes and prints the command but refuses to serve (exit 3) with the failure written to the log - never a
silent exit. Output is appended to
``infrastructure/postgresql/logs/domain-service.log``. The launcher is what the scheduled task ``GTKB-DomainService``
executes (see ``register-domain-service.ps1``); it can also be run by an operator directly. It never prints or copies
credential values.

Usage: domain_service_launcher.py --root <gt-kb root> [--port 8765] [--config <operator-config.toml>] [--print-command]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

IMPORT_FAILURE: str | None = None
try:
    from groundtruth_kb import job_containment
except Exception as error:  # build() and --print-command need no containment; serve() refuses with exit 3
    # Any failure, not only ImportError: under the scheduled task's pythonw.exe a traceback reaches nobody, so the
    # reason is kept for the log line serve() writes before refusing.
    job_containment = None  # type: ignore[assignment]
    IMPORT_FAILURE = f"{type(error).__name__}: {error}"

DROPPED_PREFIXES = ("PG", "GT_POSTGRES_", "GT_AUTHORITY_URL")
DOMAIN_SERVICE_JOB_PREFIX = "Local\\gtkb-domain-service-"
EXIT_UNCONTAINED = 3


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


def _job_name(root: Path) -> str:
    """The session-local kill-on-close job of the domain service for this installation root."""
    return job_containment.job_name(DOMAIN_SERVICE_JOB_PREFIX, root)


def _kill_on_close_job(name: str) -> int | None:
    """Create the named job whose processes end when its last handle closes (this launcher's exit); None when the
    job cannot be created or the name is already held by another launcher for this root."""
    if os.name != "nt":
        return None
    try:
        return job_containment.create_job(name, inheritable=False)
    except (job_containment.JobAlreadyExists, OSError):
        return None


def _job_held(name: str) -> bool:
    """True when a job of this name exists; the handle opened to look is closed at once (it must not keep it alive).

    A name that exists but cannot be opened (an access-denied open of a job created under another account) counts as
    held: the probe only explains a refusal already decided by ``_kill_on_close_job`` and must never raise from it.
    """
    try:
        handle = job_containment.open_job(name)
    except OSError:
        return True
    if handle is None:
        return False
    job_containment.close_handle(handle)
    return True


def _assign(job: int | None, process: subprocess.Popen) -> bool:
    if job is None or os.name != "nt":
        return False
    return job_containment.assign_to_job(job, process)


def _resume(process: subprocess.Popen) -> bool:
    if os.name != "nt":
        return True
    return job_containment.resume_primary_thread(process)


def _end(process: subprocess.Popen) -> None:
    job_containment.end_suspended(process)


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
    """Create the service suspended, place it in the job, then let it run (groundtruth_kb.job_containment).

    The job handle is not inherited, so this launcher's exit closes the last handle and ends the tree. If the service
    cannot be placed in the job or resumed it is ended while still suspended and job_containment.ContainmentError is
    raised. ``assign``/``resume`` are the test seams.
    """
    return job_containment.start_contained(
        argv, environment, job, inherit_job=False, cwd=cwd, stdout=stdout, stderr=stderr, assign=assign, resume=resume
    )


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def serve(
    argv: list[str],
    environment: dict[str, str],
    log: Path,
    port: int,
    *,
    root: Path,
    cwd: Path | None = None,
    job_factory: Callable[[], int | None] | None = None,
    assign: Callable[[int | None, subprocess.Popen], bool] = _assign,
    resume: Callable[[subprocess.Popen], bool] = _resume,
) -> int:
    """Run the service to completion under job containment; refuse (exit 3) when containment cannot be established.

    On Windows nothing is started unless a kill-on-close job exists, and the service is created suspended, placed in
    that job and only then resumed. The job is named for ``root``; a name already held by another launcher for the
    same root is refused (exit 3) before anything starts; the job handle is closed when the service exits.
    Elsewhere there is no job containment and the service simply runs.
    """
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as stream:
        stream.write(f"[{_stamp()}] starting domain service on 127.0.0.1:{port}\n".encode())
        stream.flush()
        if os.name == "nt":
            if job_containment is None:
                stream.write(
                    f"[{_stamp()}] refused: job containment unavailable (groundtruth_kb is not importable by "
                    f"{sys.executable}: {IMPORT_FAILURE}); nothing started; exit {EXIT_UNCONTAINED}\n".encode()
                )
                return EXIT_UNCONTAINED
            job_name = _job_name(root)
            job = job_factory() if job_factory is not None else _kill_on_close_job(job_name)
            if job is None:
                reason = (
                    f"job {job_name} is held by another launcher for this root"
                    if _job_held(job_name)
                    else "job object unavailable"
                )
                stream.write(f"[{_stamp()}] refused: {reason}; nothing started; exit {EXIT_UNCONTAINED}\n".encode())
                return EXIT_UNCONTAINED
            try:
                try:
                    process = _start_contained(
                        argv, environment, job, cwd=cwd, stdout=stream, stderr=stream, assign=assign, resume=resume
                    )
                except job_containment.ContainmentError as error:
                    stream.write(f"[{_stamp()}] refused: {error}; exit {EXIT_UNCONTAINED}\n".encode())
                    return EXIT_UNCONTAINED
                stream.write(
                    f"[{_stamp()}] service process {process.pid} contained by a kill-on-close job before it ran; "
                    f"job {job_name}\n".encode()
                )
                stream.flush()
                code = process.wait()
            finally:
                job_containment.close_handle(job)
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
    return serve(argv, environment, log, args.port, root=root, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
