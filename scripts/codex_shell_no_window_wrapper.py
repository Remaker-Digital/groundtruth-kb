#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""No-window subprocess wrapper for Codex shell-containment experiments."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402


def run_wrapped(command: list[str]) -> int:
    if not command:
        raise ValueError("command must not be empty")
    completed = subprocess.run(command, check=False, **no_window_subprocess_kwargs())
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute after an optional -- separator.")
    args = parser.parse_args(argv)
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("missing command after --")
    return run_wrapped(command)


if __name__ == "__main__":
    raise SystemExit(main())
