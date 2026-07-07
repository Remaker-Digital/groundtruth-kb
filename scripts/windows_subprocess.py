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


def windows_hidden_process_creationflags(*, new_process_group: bool = False, detached: bool = False) -> int:
    """Return Windows creation flags for a hidden child process."""
    if os.name != "nt":
        return 0
    flags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
    if new_process_group:
        flags |= int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200))
    if detached:
        flags |= int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))
    return flags


def hidden_startupinfo() -> object | None:
    """Return STARTUPINFO configured to hide any Windows child window."""
    if os.name != "nt":
        return None
    startupinfo_cls = getattr(subprocess, "STARTUPINFO", None)
    if startupinfo_cls is None:
        return None
    startupinfo = startupinfo_cls()
    startupinfo.dwFlags |= int(getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001))
    startupinfo.wShowWindow = int(getattr(subprocess, "SW_HIDE", 0))
    return startupinfo


def hidden_process_popen_kwargs(*, new_process_group: bool = False, detached: bool = False) -> dict[str, object]:
    """Return Popen kwargs for a Windows child that must stay headless."""
    kwargs: dict[str, object] = {}
    flags = windows_hidden_process_creationflags(new_process_group=new_process_group, detached=detached)
    if flags:
        kwargs["creationflags"] = flags
    startupinfo = hidden_startupinfo()
    if startupinfo is not None:
        kwargs["startupinfo"] = startupinfo
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
