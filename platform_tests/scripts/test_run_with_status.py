# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the run_with_status.py dispatch wrapper Windows creationflags discipline (WI-4529).

Spec linkage: GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (the spawn decision derives from a
fresh os.name check at spawn time) + REQ-HARNESS-REGISTRY-001 (the wrapper carries
the registry-defined argv vector through to the child). The wrapper must pass
creationflags=CREATE_NO_WINDOW on Windows so dispatched harness runs do not flash
an empty console window, and must pass 0 (a no-op) off Windows.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import run_with_status

EXPECTED_WINDOWS_FLAG = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


class _RecordingProcess:
    returncode = 0

    def wait(self) -> int:
        return 0


def _invoke(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, os_name: str) -> dict[str, object]:
    """Run run_with_status.main() with Popen stubbed, returning the captured Popen kwargs."""
    captured: dict[str, object] = {}

    def fake_popen(cmd_args, **kwargs):  # noqa: ANN001, ANN003 - test stub
        captured["cmd_args"] = cmd_args
        captured["kwargs"] = kwargs
        return _RecordingProcess()

    monkeypatch.setattr(run_with_status.os, "name", os_name)
    monkeypatch.setattr(run_with_status.subprocess, "Popen", fake_popen)

    status_file = tmp_path / "status.txt"
    with pytest.raises(SystemExit) as exc_info:
        run_with_status.main([str(status_file), sys.executable, "--version"])

    captured["exit_code"] = exc_info.value.code
    captured["status_file"] = status_file
    return captured


def test_popen_uses_create_no_window_on_windows_via_monkeypatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured = _invoke(monkeypatch, tmp_path, "nt")

    kwargs = captured["kwargs"]
    assert "creationflags" in kwargs, "wrapper must pass creationflags to Popen"
    assert kwargs["creationflags"] == EXPECTED_WINDOWS_FLAG
    # CREATE_NO_WINDOW bit must be set.
    assert kwargs["creationflags"] & 0x08000000 == 0x08000000
    assert captured["exit_code"] == 0


def test_popen_uses_no_creationflags_off_windows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = _invoke(monkeypatch, tmp_path, "posix")

    kwargs = captured["kwargs"]
    assert kwargs.get("creationflags") == 0, "off Windows creationflags must be a no-op (0)"
    assert captured["exit_code"] == 0


def test_status_file_records_exit_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = _invoke(monkeypatch, tmp_path, "posix")

    status_file = captured["status_file"]
    assert isinstance(status_file, Path)
    assert status_file.read_text(encoding="utf-8").strip() == "0"
