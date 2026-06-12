#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Lightweight process execution wrapper that writes exit code to a status file."""

import os
import subprocess
import sys


def main() -> None:
    args = sys.argv[1:]

    stdout_path = None
    stderr_path = None

    # Parse optional stdout/stderr redirections
    while len(args) >= 2 and args[0] in ("--stdout", "--stderr"):
        flag = args.pop(0)
        val = args.pop(0)
        if flag == "--stdout":
            stdout_path = val
        else:
            stderr_path = val

    if len(args) < 2:
        print(
            "Usage: python run_with_status.py [--stdout <file>] [--stderr <file>] <status_file_path> <cmd> [args...]",
            file=sys.stderr,
        )
        sys.exit(1)

    status_file_path = args[0]
    cmd_args = args[1:]

    exit_code = 127
    out_fh = None
    err_fh = None
    try:
        if stdout_path:
            os.makedirs(os.path.dirname(os.path.abspath(stdout_path)), exist_ok=True)
            out_fh = open(stdout_path, "w", encoding="utf-8")
        if stderr_path:
            os.makedirs(os.path.dirname(os.path.abspath(stderr_path)), exist_ok=True)
            err_fh = open(stderr_path, "w", encoding="utf-8")

        result = subprocess.run(cmd_args, stdout=out_fh, stderr=err_fh)
        exit_code = result.returncode
    except Exception as exc:
        msg = f"run_with_status.py failed to run subprocess: {exc}\n"
        if err_fh:
            err_fh.write(msg)
        else:
            print(msg, file=sys.stderr)
    finally:
        if out_fh:
            out_fh.close()
        if err_fh:
            err_fh.close()
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
