# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared Windows headless subprocess helpers for GT-KB background hooks and services."""

from __future__ import annotations

import os
import subprocess
import sys


def windows_no_window_creationflags() -> int:
    if os.name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))


def no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    flags = windows_no_window_creationflags()
    if flags:
        kwargs["creationflags"] = flags
    return kwargs


def prefer_pythonw_executable(executable: str | None = None) -> str:
    """Return a sibling pythonw.exe when ``executable`` is python.exe on Windows."""
    command = executable or sys.executable
    if os.name != "nt":
        return command
    last_backslash = command.rfind("\\")
    last_slash = command.rfind("/")
    split_at = max(last_backslash, last_slash)
    executable_name = command[split_at + 1 :] if split_at >= 0 else command
    if executable_name.lower() != "python.exe":
        return command
    candidate = f"{command[: split_at + 1]}pythonw.exe" if split_at >= 0 else "pythonw.exe"
    return candidate if os.path.isfile(candidate) else command
