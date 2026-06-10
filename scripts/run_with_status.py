#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Lightweight process execution wrapper that writes exit code to a status file."""

import os
import subprocess
import sys


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python run_with_status.py <status_file_path> <cmd> [args...]", file=sys.stderr)
        sys.exit(1)

    status_file_path = sys.argv[1]
    cmd_args = sys.argv[2:]

    status_path = os.path.abspath(status_file_path)
    os.makedirs(os.path.dirname(status_path), exist_ok=True)

    exit_code = 127
    try:
        # Run subprocess and let it output directly to stdout/stderr of this process
        result = subprocess.run(cmd_args)
        exit_code = result.returncode
    except Exception as exc:
        print(f"run_with_status.py failed to run subprocess: {exc}", file=sys.stderr)
    finally:
        try:
            with open(status_path, "w", encoding="utf-8") as fh:
                fh.write(str(exit_code))
        except Exception as exc:
            print(f"run_with_status.py failed to write status to {status_path}: {exc}", file=sys.stderr)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
