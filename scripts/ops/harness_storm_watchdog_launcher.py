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
SNAPSHOT_WINDOW_HIDER = ROOT / "scripts" / "ops" / "codex_snapshot_window_hider.py"
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from windows_subprocess import no_window_subprocess_kwargs  # noqa: E402


def _pythonw_executable() -> Path:
    current = Path(sys.executable)
    candidate = current.with_name("pythonw.exe")
    return candidate if candidate.is_file() else current


def ensure_snapshot_window_hider() -> bool:
    """Start the mutex-guarded hide-only monitor without impairing watchdog work."""

    if os.name != "nt" or not SNAPSHOT_WINDOW_HIDER.is_file():
        return False
    kwargs: dict[str, object] = {
        "cwd": str(ROOT),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    kwargs.update(no_window_subprocess_kwargs())
    kwargs["creationflags"] = (
        int(kwargs.get("creationflags", 0))
        | int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))
        | int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200))
    )
    try:
        subprocess.Popen([str(_pythonw_executable()), str(SNAPSHOT_WINDOW_HIDER)], **kwargs)
    except OSError:
        return False
    return True


def main() -> int:
    if not WATCHDOG_PS1.is_file():
        print(f"storm watchdog script missing: {WATCHDOG_PS1}", file=sys.stderr)
        return 2

    ensure_snapshot_window_hider()

    popen_kwargs: dict[str, object] = {
        "cwd": str(ROOT),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        popen_kwargs.update(no_window_subprocess_kwargs())

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
