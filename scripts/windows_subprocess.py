# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared Windows headless subprocess helpers for GT-KB background hooks and services."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid

_PRIVATE_DESKTOP_HANDLES: dict[str, int] = {}


def windows_no_window_creationflags(*, force_windows: bool = False) -> int:
    if os.name != "nt" and not force_windows:
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))


def no_window_subprocess_kwargs(*, force_windows: bool = False) -> dict[str, object]:
    kwargs: dict[str, object] = {}
    flags = windows_no_window_creationflags(force_windows=force_windows)
    if flags:
        kwargs["creationflags"] = flags
    startupinfo = hidden_startupinfo(force_windows=force_windows)
    if startupinfo is not None:
        kwargs["startupinfo"] = startupinfo
    return kwargs


def hidden_process_popen_kwargs(
    *,
    new_process_group: bool = False,
    detached: bool = False,
    desktop: str | None = None,
    force_windows: bool = False,
) -> dict[str, object]:
    """Return Popen kwargs for a Windows child that must stay headless."""
    kwargs: dict[str, object] = {}
    flags = windows_hidden_process_creationflags(
        new_process_group=new_process_group,
        detached=detached,
        force_windows=force_windows,
    )
    if flags:
        kwargs["creationflags"] = flags
    startupinfo = hidden_startupinfo(force_windows=force_windows, desktop=desktop)
    if startupinfo is not None:
        kwargs["startupinfo"] = startupinfo
    return kwargs


def windows_hidden_process_creationflags(
    *,
    new_process_group: bool = False,
    detached: bool = False,
    force_windows: bool = False,
) -> int:
    """Return Windows creation flags for a hidden child process."""
    if os.name != "nt" and not force_windows:
        return 0
    flags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
    if new_process_group:
        flags |= int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200))
    if detached:
        flags |= int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))
    return flags


def hidden_startupinfo(*, force_windows: bool = False, desktop: str | None = None) -> object | None:
    """Return STARTUPINFO configured to hide any Windows child window."""
    if os.name != "nt" and not force_windows:
        return None
    startupinfo_cls = getattr(subprocess, "STARTUPINFO", None)
    if startupinfo_cls is None:
        return None
    startupinfo = startupinfo_cls()
    startupinfo.dwFlags |= int(getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001))
    startupinfo.wShowWindow = int(getattr(subprocess, "SW_HIDE", 0))
    if desktop:
        startupinfo.lpDesktop = desktop
    return startupinfo


def create_private_desktop_name(prefix: str = "gtkb-codex") -> str:
    """Return a unique Windows desktop name for a contained process tree."""
    safe_prefix = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in prefix).strip("-_")
    return f"{safe_prefix or 'gtkb-codex'}-{uuid.uuid4().hex[:12]}"


def ensure_private_desktop(name: str) -> str | None:
    """Create and retain a Windows desktop handle, returning ``name`` on success.

    The handle is intentionally retained for the process lifetime so a spawned
    process tree can continue using the desktop after the helper returns.
    """
    if os.name != "nt":
        return None
    if name in _PRIVATE_DESKTOP_HANDLES:
        return name
    try:
        import ctypes

        user32 = ctypes.windll.user32
        user32.CreateDesktopW.restype = ctypes.c_void_p
        # DESKTOP_* rights needed by child GUI/console surfaces on that desktop.
        desktop_all_access = 0x000F01FF
        handle = user32.CreateDesktopW(name, None, None, 0, desktop_all_access, None)
    except Exception:
        return None
    if not handle:
        return None
    _PRIVATE_DESKTOP_HANDLES[name] = int(handle)
    return name


def private_desktop_popen_kwargs(
    *,
    desktop_name: str,
    new_process_group: bool = False,
    detached: bool = False,
) -> dict[str, object]:
    """Return hidden Popen kwargs that launch a Windows child on a private desktop."""
    desktop = ensure_private_desktop(desktop_name)
    if desktop is None:
        return hidden_process_popen_kwargs(new_process_group=new_process_group, detached=detached)
    return hidden_process_popen_kwargs(
        new_process_group=new_process_group,
        detached=detached,
        desktop=desktop,
        force_windows=True,
    )


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
