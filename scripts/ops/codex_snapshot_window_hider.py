#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Hide only Codex Desktop's transient Git snapshot console window on Windows.

The monitor is intentionally non-interfering: it observes window-show events,
requires exact process provenance, and calls only ``ShowWindowAsync(SW_HIDE)``.
It never terminates, suspends, reprioritizes, or intercepts a process.
"""

from __future__ import annotations

import ctypes
import ntpath
import os
from collections.abc import Callable, Sequence
from ctypes import wintypes
from typing import Any

import psutil

EVENT_OBJECT_SHOW = 0x8002
OBJID_WINDOW = 0
WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002
SW_HIDE = 0
ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\GTKB-CodexSnapshotWindowHider-v1"

SNAPSHOT_GIT_ARGUMENTS = (
    "-c",
    "core.hooksPath=NUL",
    "-c",
    "core.fsmonitor=",
    "add",
    "-u",
)


def is_target_window_show_event(
    event: int,
    hwnd: int,
    object_id: int,
    child_id: int,
) -> bool:
    """Return true only for a top-level window becoming visible."""

    return event == EVENT_OBJECT_SHOW and bool(hwnd) and object_id == OBJID_WINDOW and child_id == 0


def is_snapshot_git_commandline(commandline: Sequence[str]) -> bool:
    """Return true only for Codex Desktop's exact working-tree snapshot Git call."""

    if len(commandline) != len(SNAPSHOT_GIT_ARGUMENTS) + 1:
        return False
    executable = ntpath.basename(str(commandline[0]).strip('"')).casefold()
    return executable == "git.exe" and tuple(commandline[1:]) == SNAPSHOT_GIT_ARGUMENTS


def is_qualifying_console_process(
    pid: int,
    *,
    process_factory: Callable[[int], Any] = psutil.Process,
) -> bool:
    """Require conhost -> exact snapshot Git -> ChatGPT ancestry.

    Process inspection races and access failures deliberately fail open: the
    window remains visible and no process or window is changed.
    """

    try:
        console = process_factory(pid)
        if console.name().casefold() != "conhost.exe":
            return False

        snapshot_git = console.parent()
        if snapshot_git is None or not is_snapshot_git_commandline(snapshot_git.cmdline()):
            return False

        ancestor = snapshot_git.parent()
        for _ in range(6):
            if ancestor is None:
                return False
            if ancestor.name().casefold() == "chatgpt.exe":
                return True
            ancestor = ancestor.parent()
    except (AttributeError, TypeError, psutil.Error, OSError, RuntimeError, ValueError):
        return False
    return False


def hide_qualifying_window(
    hwnd: int,
    *,
    pid_resolver: Callable[[int], int],
    hide_window: Callable[[int], bool],
    process_factory: Callable[[int], Any] = psutil.Process,
) -> bool:
    """Hide *hwnd* only when every provenance predicate is satisfied."""

    try:
        pid = int(pid_resolver(hwnd))
    except (OSError, RuntimeError, TypeError, ValueError):
        return False
    if pid <= 0 or not is_qualifying_console_process(pid, process_factory=process_factory):
        return False
    try:
        return bool(hide_window(hwnd))
    except (OSError, RuntimeError, TypeError, ValueError):
        return False


def _run_windows_monitor() -> int:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not mutex:
        return 2
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(mutex)
        return 0

    callback_type = ctypes.WINFUNCTYPE(
        None,
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.HWND,
        wintypes.LONG,
        wintypes.LONG,
        wintypes.DWORD,
        wintypes.DWORD,
    )

    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindowAsync.restype = wintypes.BOOL
    user32.SetWinEventHook.argtypes = [
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HMODULE,
        callback_type,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
    ]
    user32.SetWinEventHook.restype = wintypes.HANDLE
    user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
    user32.UnhookWinEvent.restype = wintypes.BOOL

    def _pid_for_window(hwnd: int) -> int:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(pid.value)

    def _hide_window(hwnd: int) -> bool:
        return bool(user32.ShowWindowAsync(hwnd, SW_HIDE))

    @callback_type
    def _on_window_event(
        _hook: int,
        event: int,
        hwnd: int,
        object_id: int,
        child_id: int,
        _event_thread: int,
        _event_time: int,
    ) -> None:
        if not is_target_window_show_event(event, hwnd, object_id, child_id):
            return
        hide_qualifying_window(
            int(hwnd),
            pid_resolver=_pid_for_window,
            hide_window=_hide_window,
        )

    hook = user32.SetWinEventHook(
        EVENT_OBJECT_SHOW,
        EVENT_OBJECT_SHOW,
        None,
        _on_window_event,
        0,
        0,
        WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
    )
    if not hook:
        kernel32.CloseHandle(mutex)
        return 3

    try:
        message = wintypes.MSG()
        while True:
            result = user32.GetMessageW(ctypes.byref(message), None, 0, 0)
            if result <= 0:
                return 0 if result == 0 else 4
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
    finally:
        user32.UnhookWinEvent(hook)
        kernel32.CloseHandle(mutex)


def main() -> int:
    if os.name != "nt":
        return 0
    return _run_windows_monitor()


if __name__ == "__main__":
    raise SystemExit(main())
