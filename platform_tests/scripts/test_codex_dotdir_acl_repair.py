# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5065: durable fix for recurring `.codex` ACL drift.

Covers the three scope-A components:
- `.driveignore` excludes `.codex/` (stops Google Drive re-materializing the
  foreign-SID Deny ACEs at the source).
- `repair_codex_dotdir_acl.ps1` is PowerShell-7 compatible (Get-Acl/Set-Acl,
  not the .NET Core-removed `[System.IO.Directory]::GetAccessControl` statics
  that falsely reported `risky_deny_count=0` under pwsh).
- `verify_codex_dispatch._check_codex_dotdir_acl(..., repair=True)` escalates a
  Check to Apply when removable risky-Deny ACEs are found (opt-in, idempotent).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.verify_codex_dispatch as verify  # noqa: E402


def test_driveignore_excludes_codex_dir():
    lines = {ln.strip() for ln in (ROOT / ".driveignore").read_text(encoding="utf-8").splitlines()}
    assert ".codex/" in lines


def _fake_powershell(_name: str) -> str:
    # A name ending in powershell.exe exercises the ExecutionPolicy branch too.
    return r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"


def _mode_capturing_run(modes: list[str], needs_repair_first: bool):
    def fake_run(command, **_kwargs):
        mode = command[command.index("-Mode") + 1]
        modes.append(mode)
        needs = needs_repair_first and mode == "Check" and modes.count("Check") == 1
        payload = {"ok": not needs, "needs_repair": needs, "risky_deny_count": 1 if needs else 0, "errors": []}
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    return fake_run


def test_auto_repair_escalates_check_to_apply(monkeypatch):
    monkeypatch.setattr(verify.sys, "platform", "win32")
    monkeypatch.setattr(verify.shutil, "which", _fake_powershell)
    modes: list[str] = []
    monkeypatch.setattr(verify.subprocess, "run", _mode_capturing_run(modes, needs_repair_first=True))
    verify._check_codex_dotdir_acl(Path("E:/GT-KB"), repair=True)
    # Check found a removable deny -> Apply -> re-Check confirms clean.
    assert modes == ["Check", "Apply", "Check"]


def test_default_check_is_read_only(monkeypatch):
    monkeypatch.setattr(verify.sys, "platform", "win32")
    monkeypatch.setattr(verify.shutil, "which", _fake_powershell)
    modes: list[str] = []
    monkeypatch.setattr(verify.subprocess, "run", _mode_capturing_run(modes, needs_repair_first=True))
    verify._check_codex_dotdir_acl(Path("E:/GT-KB"), repair=False)
    # Without repair, the readiness probe never mutates: Check only.
    assert modes == ["Check"]


def test_no_apply_when_check_is_clean(monkeypatch):
    monkeypatch.setattr(verify.sys, "platform", "win32")
    monkeypatch.setattr(verify.shutil, "which", _fake_powershell)
    modes: list[str] = []
    monkeypatch.setattr(verify.subprocess, "run", _mode_capturing_run(modes, needs_repair_first=False))
    verify._check_codex_dotdir_acl(Path("E:/GT-KB"), repair=True)
    # repair requested but nothing to repair -> no Apply escalation.
    assert modes == ["Check"]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows .codex ACL script")
def test_repair_script_check_mode_is_pwsh7_compatible(tmp_path):
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh (PowerShell 7) not available")
    codex = tmp_path / ".codex"
    codex.mkdir()
    (codex / "file.txt").write_text("x", encoding="utf-8")
    script = ROOT / "scripts" / "repair_codex_dotdir_acl.ps1"
    completed = subprocess.run(
        [pwsh, "-NoProfile", "-File", str(script), "-ProjectRoot", str(tmp_path), "-Mode", "Check", "-Json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = (completed.stdout or "") + (completed.stderr or "")
    # The .NET Core-removed statics raised "does not contain a method named
    # 'GetAccessControl'" under pwsh (WI-5065); Get-Acl must not.
    assert "GetAccessControl" not in combined
    payload = json.loads(completed.stdout)
    assert isinstance(payload.get("risky_deny_count"), int)
    assert payload.get("errors") == []
