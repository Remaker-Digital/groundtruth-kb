#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Lightweight process execution wrapper that writes exit code to a status file."""

import os
import subprocess
import sys


def main() -> None:
    args = sys.argv[1:]

    stdin_path = None
    stdout_path = None
    stderr_path = None

    # Parse optional stdin/stdout/stderr redirections
    while len(args) >= 2 and args[0] in ("--stdin", "--stdout", "--stderr"):
        flag = args.pop(0)
        val = args.pop(0)
        if flag == "--stdin":
            stdin_path = val
        elif flag == "--stdout":
            stdout_path = val
        else:
            stderr_path = val

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
            stdin_fh = open(stdin_path, "r", encoding="utf-8")
        else:
            stdin_fh = subprocess.DEVNULL

        if stdout_path:
            os.makedirs(os.path.dirname(os.path.abspath(stdout_path)), exist_ok=True)
            out_fh = open(stdout_path, "w", encoding="utf-8")
        else:
            out_fh = subprocess.DEVNULL

        if stderr_path:
            os.makedirs(os.path.dirname(os.path.abspath(stderr_path)), exist_ok=True)
            err_fh = open(stderr_path, "w", encoding="utf-8")
        else:
            err_fh = subprocess.DEVNULL

        if (
            os.name == "nt"
            and cmd_args
            and (cmd_args[0].lower().endswith(".cmd") or cmd_args[0].lower().endswith(".bat"))
        ):
            cmd_args = ["cmd.exe", "/c"] + cmd_args

        p = subprocess.Popen(
            cmd_args,
            stdin=stdin_fh,
            stdout=out_fh,
            stderr=err_fh,
        )

        p.wait()
        exit_code = p.returncode

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
