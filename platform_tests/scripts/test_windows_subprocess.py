# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/windows_subprocess.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import windows_subprocess as ws  # noqa: E402


class _FakeStartupInfo:
    def __init__(self) -> None:
        self.dwFlags = 0
        self.wShowWindow = None


def test_no_window_subprocess_kwargs_sets_create_no_window_on_windows() -> None:
    if sys.platform != "win32":
        return
    kwargs = ws.no_window_subprocess_kwargs()
    assert kwargs.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    startupinfo = kwargs.get("startupinfo")
    assert startupinfo is not None
    assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
    assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


def test_no_window_subprocess_kwargs_force_windows_returns_hidden_startupinfo(monkeypatch) -> None:
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    monkeypatch.setattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001, raising=False)
    monkeypatch.setattr(subprocess, "SW_HIDE", 0, raising=False)
    monkeypatch.setattr(subprocess, "STARTUPINFO", _FakeStartupInfo, raising=False)

    kwargs = ws.no_window_subprocess_kwargs(force_windows=True)

    assert kwargs.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    startupinfo = kwargs.get("startupinfo")
    assert isinstance(startupinfo, _FakeStartupInfo)
    assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
    assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


def test_hidden_process_popen_kwargs_hides_and_detaches_on_windows() -> None:
    if sys.platform != "win32":
        return
    kwargs = ws.hidden_process_popen_kwargs(new_process_group=True, detached=True)
    creationflags = int(kwargs.get("creationflags", 0))
    assert creationflags & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    assert creationflags & getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    assert creationflags & getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
    startupinfo = kwargs.get("startupinfo")
    assert startupinfo is not None
    assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
    assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


def test_prefer_pythonw_executable_rewrites_python_exe() -> None:
    if sys.platform != "win32":
        return
    python_exe = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    if not python_exe.is_file():
        return
    preferred = ws.prefer_pythonw_executable(str(python_exe))
    assert preferred.endswith("pythonw.exe")
    assert Path(preferred).is_file()
