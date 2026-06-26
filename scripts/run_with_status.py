#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Lightweight process execution wrapper that writes exit code to a status file."""

import os
import signal
import subprocess
import sys

# Phase 0 reliability fix (WI-4806, GO at bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md):
# a bare p.wait() let a hung wrapped harness (cloud non-JSON body, HTTP 502, stuck socket)
# leave this wrapper immortal, accumulating into the storm-watchdog threshold (WI-4670 root cause).
# A fixed module-level default keeps this a pure defect fix with no new config surface; tests
# monkeypatch the constant, and the Phase 2 daemon makes it configurable.
DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600  # 10-minute generous Phase 0 baseline (LO GO -002)
TIMEOUT_EXIT_CODE = 124  # coreutils `timeout` convention; distinguishes a lifetime-timeout kill
TERMINATE_GRACE_SECONDS = 10


def _terminate_process_tree(proc: subprocess.Popen) -> None:
    """Best-effort termination of the wrapped process AND its descendants.

    ``Popen.terminate()``/``kill()`` only signal the immediate child, so a hung
    harness's node/python grandchildren would be orphaned and keep accumulating
    (the WI-4670 immortal-worker leak). On Windows use ``taskkill /T`` to walk and
    kill the whole tree; on POSIX kill the process group (the child is spawned with
    ``start_new_session=True``). Reap the root afterward so no zombie remains.
    """
    if proc.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    try:
        proc.wait(timeout=TERMINATE_GRACE_SECONDS)
    except Exception:
        pass


def _parse_lifetime(value: str) -> int:
    """Parse and validate a ``--lifetime <seconds>`` argument (WI-4845).

    Returns a positive integer second count. Fails closed (exit 2) on a
    non-positive or non-numeric value so a malformed dispatch cannot silently
    run unbounded.
    """
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        print(
            f"run_with_status.py: --lifetime must be a positive integer, got {value!r}",
            file=sys.stderr,
        )
        raise SystemExit(2) from None
    if parsed <= 0:
        print(
            f"run_with_status.py: --lifetime must be a positive integer, got {value!r}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return parsed


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    stdin_path = None
    stdout_path = None
    stderr_path = None
    # WI-4845: dispatched Loyal Opposition / verification reviews need a longer
    # lifetime than the 600s default to complete a full multi-turn bridge review.
    # The dispatcher passes --lifetime; absent it, the module default applies.
    lifetime_seconds: int = DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS

    # Parse optional stdin/stdout/stderr/lifetime arguments
    while len(args) >= 2 and args[0] in ("--stdin", "--stdout", "--stderr", "--lifetime"):
        flag = args.pop(0)
        val = args.pop(0)
        if flag == "--stdin":
            stdin_path = val
        elif flag == "--stdout":
            stdout_path = val
        elif flag == "--stderr":
            stderr_path = val
        else:  # --lifetime
            lifetime_seconds = _parse_lifetime(val)

    if len(args) < 2:
        print(
            "Usage: python run_with_status.py [--stdin <file>] [--stdout <file>] [--stderr <file>] <status_file_path> <cmd> [args...]",
            file=sys.stderr,
        )
        sys.exit(1)

    status_file_path = args[0]
    cmd_args = args[1:]

    exit_code = 127
    stdin_fh = None
    out_fh = None
    err_fh = None
    try:
        if stdin_path:
            stdin_fh = open(stdin_path, encoding="utf-8")  # noqa: SIM115
        else:
            stdin_fh = subprocess.DEVNULL

        if stdout_path:
            os.makedirs(os.path.dirname(os.path.abspath(stdout_path)), exist_ok=True)
            out_fh = open(stdout_path, "w", encoding="utf-8")  # noqa: SIM115
        else:
            out_fh = subprocess.DEVNULL

        if stderr_path:
            os.makedirs(os.path.dirname(os.path.abspath(stderr_path)), exist_ok=True)
            err_fh = open(stderr_path, "w", encoding="utf-8")  # noqa: SIM115
        else:
            err_fh = subprocess.DEVNULL

        if (
            os.name == "nt"
            and cmd_args
            and (cmd_args[0].lower().endswith(".cmd") or cmd_args[0].lower().endswith(".bat"))
        ):
            cmd_args = ["cmd.exe", "/c"] + cmd_args

        # On Windows, suppress the per-child console window. Without this flag
        # the wrapped harness — which lives for the entire dispatched run —
        # allocates an empty console window (stdout/stderr are redirected to
        # log files). Mirrors the cross-harness trigger's outer Popen sites
        # (scripts/cross_harness_bridge_trigger.py). No-op (0) off Windows.
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0

        popen_kwargs: dict[str, object] = {
            "stdin": stdin_fh,
            "stdout": out_fh,
            "stderr": err_fh,
            "creationflags": creationflags,
        }
        if os.name != "nt":
            # New POSIX session/process group so the whole tree can be reaped via
            # os.killpg on a lifetime timeout. No-op on Windows (taskkill /T walks
            # the tree); not passed on Windows where the kwarg is unsupported.
            popen_kwargs["start_new_session"] = True

        p = subprocess.Popen(cmd_args, **popen_kwargs)

        try:
            p.wait(timeout=lifetime_seconds)
            exit_code = p.returncode
        except subprocess.TimeoutExpired:
            _terminate_process_tree(p)
            exit_code = TIMEOUT_EXIT_CODE
            timeout_msg = (
                f"run_with_status.py: worker exceeded the "
                f"{lifetime_seconds}s lifetime timeout; "
                f"terminated process tree (pid={p.pid}).\n"
            )
            if err_fh and err_fh != subprocess.DEVNULL:
                try:
                    err_fh.write(timeout_msg)
                    err_fh.flush()
                except Exception:
                    pass
            print(timeout_msg, file=sys.stderr)

    except Exception as exc:
        msg = f"run_with_status.py failed to run subprocess (args={cmd_args}): {exc}\n"
        if stderr_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(stderr_path)), exist_ok=True)
                with open(stderr_path, "a", encoding="utf-8") as fh:
                    fh.write(msg)
            except Exception:
                pass
        print(msg, file=sys.stderr)
    finally:
        if stdin_fh and stdin_fh != subprocess.DEVNULL:
            try:
                stdin_fh.close()
            except Exception:
                pass
        if out_fh and out_fh != subprocess.DEVNULL:
            try:
                out_fh.close()
            except Exception:
                pass
        if err_fh and err_fh != subprocess.DEVNULL:
            try:
                err_fh.close()
            except Exception:
                pass
        try:
            status_path = os.path.abspath(status_file_path)
            os.makedirs(os.path.dirname(status_path), exist_ok=True)
            with open(status_path, "w", encoding="utf-8") as fh:
                fh.write(str(exit_code))
        except Exception:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
