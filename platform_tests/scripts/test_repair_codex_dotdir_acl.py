from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

SCRIPT_PATH = REPO_ROOT / "scripts" / "repair_codex_dotdir_acl.ps1"


def _powershell() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


def _run_ps(
    args: list[str],
    *,
    cwd: Path = REPO_ROOT,
    check: bool = False,
    no_window: bool = False,
) -> subprocess.CompletedProcess[str]:
    exe = _powershell()
    if exe is None:
        pytest.skip("PowerShell is required for ACL repair tests")
    shell_args = ["-NoProfile"]
    if Path(exe).name.lower() == "powershell.exe":
        shell_args.extend(["-ExecutionPolicy", "Bypass"])
    hidden_kwargs = no_window_subprocess_kwargs() if no_window else {}
    return subprocess.run(
        [exe, *shell_args, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=check,
        **hidden_kwargs,
    )


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_detects_and_removes_explicit_deny(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    helper_dir = codex_root / "skills" / "verify" / "helpers"
    helper_dir.mkdir(parents=True)
    (codex_root / "config.toml").write_text("# fixture\n", encoding="utf-8")
    (helper_dir / "write_verdict.py").write_text("# fixture\n", encoding="utf-8")

    add_deny = f"""
$path = '{codex_root}'
$ace = '*S-1-5-19:(W,D)'
& icacls $path /deny $ace
if ($LASTEXITCODE -ne 0) {{
    exit $LASTEXITCODE
}}
"""
    _run_ps(["-Command", add_deny], check=True)

    no_window_check = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ],
        no_window=True,
    )
    assert no_window_check.returncode == 1
    no_window_payload = json.loads(no_window_check.stdout)
    assert no_window_payload["errors"] == []
    assert no_window_payload["risky_deny_count"] >= 1

    check = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ]
    )
    assert check.returncode == 1
    check_payload = json.loads(check.stdout)
    assert check_payload["needs_repair"] is True
    assert check_payload["risky_deny_count"] >= 1

    apply = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Apply",
            "-Json",
        ]
    )
    assert apply.returncode == 0, apply.stderr
    apply_payload = json.loads(apply.stdout)
    assert apply_payload["errors"] == []
    assert apply_payload["risky_deny_count"] >= 1
    assert all(entry["applied"] is True for entry in apply_payload["removed"])
    assert apply_payload["current_identity"]["allow_present"] is True
    if apply_payload["sandbox_group"]["present"]:
        assert apply_payload["sandbox_group"]["allow_present"] is True

    clean = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ]
    )
    assert clean.returncode == 0, clean.stderr
    clean_payload = json.loads(clean.stdout)
    assert clean_payload["needs_repair"] is False
    assert clean_payload["risky_deny_count"] == 0
    assert clean_payload["current_identity"]["allow_present"] is True
    if clean_payload["sandbox_group"]["present"]:
        assert clean_payload["sandbox_group"]["allow_present"] is True


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_removes_unresolved_sid_deny(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    helper_dir = codex_root / "skills" / "verify" / "helpers"
    helper_dir.mkdir(parents=True)
    (helper_dir / "write_verdict.py").write_text("# fixture\n", encoding="utf-8")

    add_deny = f"""
$path = '{codex_root}'
$acl = [System.IO.Directory]::GetAccessControl($path)
$sid = New-Object System.Security.Principal.SecurityIdentifier('S-1-5-21-2908765920-875073000-2352713335-4168283502')
$flags = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
    [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$rights = [System.Security.AccessControl.FileSystemRights]::Write -bor
    [System.Security.AccessControl.FileSystemRights]::Delete
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $sid,
    $rights,
    $flags,
    [System.Security.AccessControl.PropagationFlags]::None,
    [System.Security.AccessControl.AccessControlType]::Deny
)
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    _run_ps(["-Command", add_deny], check=True)

    check = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ]
    )
    assert check.returncode == 1
    check_payload = json.loads(check.stdout)
    assert check_payload["needs_repair"] is True
    assert check_payload["risky_deny_count"] >= 1
    assert any(
        entry["identity"] == "S-1-5-21-2908765920-875073000-2352713335-4168283502" for entry in check_payload["removed"]
    )

    apply = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Apply",
            "-Json",
        ]
    )
    assert apply.returncode == 0, apply.stderr
    apply_payload = json.loads(apply.stdout)
    assert apply_payload["errors"] == []
    assert all(entry["applied"] is True for entry in apply_payload["removed"])

    clean = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ]
    )
    assert clean.returncode == 0, clean.stderr
    clean_payload = json.loads(clean.stdout)
    assert clean_payload["needs_repair"] is False
    assert clean_payload["risky_deny_count"] == 0


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_refuses_non_codex_target(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()

    result = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ]
    )

    assert result.returncode != 0
    assert ".codex directory not found" in (result.stderr + result.stdout)
