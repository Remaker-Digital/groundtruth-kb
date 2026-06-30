# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/windows_subprocess.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import windows_subprocess as ws  # noqa: E402


def test_no_window_subprocess_kwargs_sets_create_no_window_on_windows() -> None:
    if sys.platform != "win32":
        return
    kwargs = ws.no_window_subprocess_kwargs()
    assert kwargs.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def test_prefer_pythonw_executable_rewrites_python_exe() -> None:
    if sys.platform != "win32":
        return
    python_exe = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    if not python_exe.is_file():
        return
    preferred = ws.prefer_pythonw_executable(str(python_exe))
    assert preferred.endswith("pythonw.exe")
    assert Path(preferred).is_file()
