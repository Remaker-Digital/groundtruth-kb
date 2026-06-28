#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Headless Task Scheduler entrypoint for the storm watchdog (WI-4896 residual).

The legacy path (wscript -> powershell.exe -WindowStyle Hidden) still flashes a
visible console on Windows 11 when Task Scheduler fires every minute. This
launcher is invoked directly via pythonw.exe and spawns the tracked PowerShell
script with CREATE_NO_WINDOW so no console is allocated.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCHDOG_PS1 = ROOT / "scripts" / "ops" / "harness_storm_watchdog.ps1"


def main() -> int:
    if not WATCHDOG_PS1.is_file():
        print(f"storm watchdog script missing: {WATCHDOG_PS1}", file=sys.stderr)
        return 2

    popen_kwargs: dict[str, object] = {
        "cwd": str(ROOT),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-File",
            str(WATCHDOG_PS1),
        ],
        **popen_kwargs,
    )
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
