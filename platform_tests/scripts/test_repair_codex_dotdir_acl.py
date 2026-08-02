from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
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
    executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    exe = executable or _powershell()
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


def _seed_required_modify_allows(path: Path) -> None:
    command = f"""
$path = '{path}'
$group = Get-LocalGroup -Name 'CodexSandboxUsers' -ErrorAction SilentlyContinue
if ($null -eq $group) {{ exit 42 }}
$acl = [System.IO.Directory]::GetAccessControl($path)
$flags = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
    [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$sids = @([System.Security.Principal.WindowsIdentity]::GetCurrent().User, $group.SID)
foreach ($sid in $sids) {{
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $sid,
        [System.Security.AccessControl.FileSystemRights]::Modify,
        $flags,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $acl.AddAccessRule($rule)
}}
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    result = _run_ps(["-Command", command])
    if result.returncode == 42:
        pytest.skip("CodexSandboxUsers is required for exact Apply precondition tests")
    assert result.returncode == 0, result.stderr


def _add_unresolved_risky_deny(path: Path, sid: str) -> None:
    command = f"""
$path = '{path}'
$acl = [System.IO.Directory]::GetAccessControl($path)
$sid = New-Object System.Security.Principal.SecurityIdentifier('{sid}')
$rights = [System.Security.AccessControl.FileSystemRights]::Write -bor
    [System.Security.AccessControl.FileSystemRights]::Delete
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $sid,
    $rights,
    [System.Security.AccessControl.InheritanceFlags]::None,
    [System.Security.AccessControl.PropagationFlags]::None,
    [System.Security.AccessControl.AccessControlType]::Deny
)
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    _run_ps(["-Command", command], check=True)


def _acl_sddl(path: Path) -> str:
    command = f"""
$acl = [System.IO.Directory]::GetAccessControl('{path}')
$sections = [System.Security.AccessControl.AccessControlSections]::Access -bor
    [System.Security.AccessControl.AccessControlSections]::Owner -bor
    [System.Security.AccessControl.AccessControlSections]::Group
$acl.GetSecurityDescriptorSddlForm($sections)
"""
    result = _run_ps(["-Command", command], check=True)
    return result.stdout.strip()


def _acl_fingerprints(path: Path) -> list[str]:
    command = f"""
$acl = [System.IO.Directory]::GetAccessControl('{path}')
$fingerprints = @(
    foreach ($rule in $acl.Access) {{
        try {{
            $sid = $rule.IdentityReference.Translate(
                [System.Security.Principal.SecurityIdentifier]
            ).Value
        }} catch {{
            $sid = $rule.IdentityReference.Value
        }}
        "{{0}}|{{1}}|{{2}}|{{3}}|{{4}}|{{5}}" -f @(
            $sid,
            [int] $rule.AccessControlType,
            [int64] $rule.FileSystemRights,
            [int] $rule.InheritanceFlags,
            [int] $rule.PropagationFlags,
            [bool] $rule.IsInherited
        )
    }}
) | Sort-Object
ConvertTo-Json -InputObject @($fingerprints)
"""
    result = _run_ps(["-Command", command], check=True)
    payload = json.loads(result.stdout)
    return [payload] if isinstance(payload, str) else payload


def _run_repair(script: Path, project_root: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return _run_ps(
        [
            "-File",
            str(script),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            mode,
            "-Json",
        ]
    )


def _faulted_script(tmp_path: Path, replacements: list[tuple[str, str]]) -> Path:
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    for old, new in replacements:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    path = tmp_path / "repair_codex_dotdir_acl.fault.ps1"
    path.write_text(source, encoding="utf-8")
    return path


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_detects_and_removes_explicit_deny(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    helper_dir = codex_root / "skills" / "verify" / "helpers"
    helper_dir.mkdir(parents=True)
    (codex_root / "config.toml").write_text("# fixture\n", encoding="utf-8")
    (helper_dir / "write_verdict.py").write_text("# fixture\n", encoding="utf-8")
    _seed_required_modify_allows(codex_root)

    add_deny = f"""
$path = '{codex_root}'
$ace = '*S-1-5-19:(W,D)'
& icacls $path /deny $ace
if ($LASTEXITCODE -ne 0) {{
    exit $LASTEXITCODE
}}
"""
    _run_ps(["-Command", add_deny], check=True)
    before_check = _acl_sddl(codex_root)

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
    assert _acl_sddl(codex_root) == before_check

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
    assert _acl_sddl(codex_root) == before_check

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
    assert apply.returncode == 0, apply.stdout + apply.stderr
    apply_payload = json.loads(apply.stdout)
    assert apply_payload["errors"] == []
    assert apply_payload["risky_deny_count"] >= 1
    assert all(entry["applied"] is True for entry in apply_payload["removed"])
    assert apply_payload["current_identity"]["allow_present"] is True
    assert apply_payload["sandbox_group"]["allow_present"] is True
    assert apply_payload["target_fingerprints"]
    assert apply_payload["pre_non_target_fingerprint_sha256"] == apply_payload["post_non_target_fingerprint_sha256"]
    assert apply_payload["pre_non_target_fingerprint_count"] == apply_payload["post_non_target_fingerprint_count"]
    assert apply_payload["owner_equal"] is True
    assert apply_payload["group_equal"] is True
    assert apply_payload["protection_equal"] is True
    assert apply_payload["required_allows_equal"] is True
    if apply_payload["sacl_readable"]:
        assert apply_payload["sacl_equal"] is True
    else:
        assert apply_payload["sacl_equal"] is None
    assert apply_payload["pre_descriptor_sha256"]
    assert apply_payload["expected_descriptor_sha256"] == apply_payload["post_descriptor_sha256"]
    assert apply_payload["apply_write_count"] == 1
    assert apply_payload["rollback_write_count"] == 0
    assert apply_payload["root_write_count"] == 1
    assert apply_payload["descendant_write_count"] == 0
    assert apply_payload["rollback"]["attempted"] is False
    assert apply_payload["rollback"]["proven"] is False
    assert apply_payload["rollback"]["error"] is None

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
    _seed_required_modify_allows(codex_root)

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
    assert apply.returncode == 0, apply.stdout + apply.stderr
    apply_payload = json.loads(apply.stdout)
    assert apply_payload["errors"] == []
    assert all(entry["applied"] is True for entry in apply_payload["removed"])
    assert any(
        fingerprint.startswith("S-1-5-21-2908765920-875073000-2352713335-4168283502|")
        for fingerprint in apply_payload["target_fingerprints"]
    )
    assert apply_payload["root_write_count"] == 1
    assert apply_payload["descendant_write_count"] == 0

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
def test_repair_codex_dotdir_acl_apply_does_not_enumerate_or_write_descendants(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    child = codex_root / "child"
    child.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283503")
    _add_unresolved_risky_deny(child, "S-1-5-21-2908765920-875073000-2352713335-4168283504")
    child_before = _acl_sddl(child)

    apply = _run_repair(SCRIPT_PATH, project_root, "Apply")

    assert apply.returncode == 0, apply.stdout + apply.stderr
    payload = json.loads(apply.stdout)
    assert payload["checked_count"] == 1
    assert payload["root_write_count"] == 1
    assert payload["descendant_write_count"] == 0
    assert _acl_sddl(child) == child_before
    check = _run_repair(SCRIPT_PATH, project_root, "Check")
    assert check.returncode == 1
    assert any(entry["path"] == ".codex\\child" for entry in json.loads(check.stdout)["removed"])


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_missing_required_allow_fails_without_write(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    codex_root.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283505")
    remove_sandbox_allow = f"""
$path = '{codex_root}'
$group = Get-LocalGroup -Name 'CodexSandboxUsers' -ErrorAction Stop
$acl = [System.IO.Directory]::GetAccessControl($path)
$acl.SetAccessRuleProtection($true, $true)
$acl.PurgeAccessRules($group.SID)
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    _run_ps(["-Command", remove_sandbox_allow], check=True)
    before = _acl_sddl(codex_root)

    apply = _run_repair(SCRIPT_PATH, project_root, "Apply")

    assert apply.returncode == 2
    payload = json.loads(apply.stdout)
    assert payload["apply_write_count"] == 0
    assert payload["rollback_write_count"] == 0
    assert payload["root_write_count"] == 0
    assert payload["sandbox_group"]["present"] is True
    assert payload["sandbox_group"]["allow_present"] is False
    assert "required_modify_allow_missing" in payload["errors"][0]["error"]
    assert _acl_sddl(codex_root) == before


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_prewrite_drift_fails_without_write(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    codex_root.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283506")
    before = _acl_sddl(codex_root)
    script = _faulted_script(
        tmp_path,
        [
            (
                "$transformedSnapshot = Get-AclSnapshot -Acl $workingAcl",
                "$transformedSnapshot = Get-AclSnapshot -Acl $workingAcl\n"
                '$transformedSnapshot.fingerprints = @("injected-prewrite-drift")',
            )
        ],
    )

    apply = _run_repair(script, project_root, "Apply")

    assert apply.returncode == 2
    payload = json.loads(apply.stdout)
    assert "prewrite_invariant_mismatch" in payload["errors"][0]["error"]
    assert payload["root_write_count"] == 0
    assert _acl_sddl(codex_root) == before


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_readback_drift_rolls_back_once(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    codex_root.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283507")
    before = _acl_sddl(codex_root)
    script = _faulted_script(
        tmp_path,
        [
            (
                "$outcome.post_snapshot = Get-AclSnapshot -Acl $postAcl",
                "$outcome.post_snapshot = Get-AclSnapshot -Acl $postAcl\n"
                '$outcome.post_snapshot.fingerprints = @("injected-postwrite-drift")',
            )
        ],
    )

    apply = _run_repair(script, project_root, "Apply")

    assert apply.returncode == 2
    payload = json.loads(apply.stdout)
    assert payload["apply_write_count"] == 1
    assert payload["rollback_write_count"] == 1
    assert payload["root_write_count"] == 2
    assert payload["rollback"]["attempted"] is True
    assert payload["rollback"]["proven"] is True, json.dumps(payload["rollback"], indent=2)
    assert payload["rollback"]["error"] is None
    assert payload["rollback"]["expected_descriptor_sha256"] == payload["rollback"]["observed_descriptor_sha256"]
    assert _acl_sddl(codex_root) == before


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_rollback_failure_is_visible_and_not_retried(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    codex_root.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283508")
    script = _faulted_script(
        tmp_path,
        [
            (
                "$outcome.post_snapshot = Get-AclSnapshot -Acl $postAcl",
                "$outcome.post_snapshot = Get-AclSnapshot -Acl $postAcl\n"
                '$outcome.post_snapshot.fingerprints = @("injected-postwrite-drift")',
            ),
            (
                "Set-AccessOnlyAcl -Path $Path -Acl $rollbackAclObject",
                'throw "injected_rollback_failure"',
            ),
        ],
    )

    apply = _run_repair(script, project_root, "Apply")

    assert apply.returncode == 2
    payload = json.loads(apply.stdout)
    assert payload["apply_write_count"] == 1
    assert payload["rollback_write_count"] == 0
    assert payload["root_write_count"] == 1
    assert payload["rollback"]["attempted"] is True
    assert payload["rollback"]["proven"] is False
    assert "injected_rollback_failure" in payload["rollback"]["error"]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_preserves_same_identity_non_targets(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    project_root.mkdir(parents=True)
    sid = "S-1-5-21-2908765920-875073000-2352713335-4168283509"
    seed_parent_deny = f"""
$ErrorActionPreference = 'Stop'
$path = '{project_root}'
$acl = [System.IO.Directory]::GetAccessControl($path)
$sid = New-Object System.Security.Principal.SecurityIdentifier('{sid}')
$inherit = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
    [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $sid, [System.Security.AccessControl.FileSystemRights]::ReadData, $inherit,
    [System.Security.AccessControl.PropagationFlags]::None,
    [System.Security.AccessControl.AccessControlType]::Deny
)
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    _run_ps(["-Command", seed_parent_deny], check=True)
    codex_root.mkdir(parents=True)
    _seed_required_modify_allows(codex_root)
    seed_rules = f"""
$ErrorActionPreference = 'Stop'
$path = '{codex_root}'
$acl = [System.IO.Directory]::GetAccessControl($path)
$sid = New-Object System.Security.Principal.SecurityIdentifier('{sid}')
$none = [System.Security.AccessControl.InheritanceFlags]::None
$containerAndObject = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
    [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$rules = @(
    (New-Object System.Security.AccessControl.FileSystemAccessRule(
        $sid, [System.Security.AccessControl.FileSystemRights]::Write, $none,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Deny
    )),
    (New-Object System.Security.AccessControl.FileSystemAccessRule(
        $sid, [System.Security.AccessControl.FileSystemRights]::Delete, $containerAndObject,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Deny
    )),
    (New-Object System.Security.AccessControl.FileSystemAccessRule(
        $sid, [System.Security.AccessControl.FileSystemRights]::ReadAndExecute, $none,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow
    ))
)
foreach ($rule in $rules) {{ $acl.AddAccessRule($rule) }}
[System.IO.Directory]::SetAccessControl($path, $acl)
"""
    _run_ps(["-Command", seed_rules], check=True)
    before = _acl_fingerprints(codex_root)
    assert sum(fingerprint.startswith(f"{sid}|") for fingerprint in before) == 4

    apply = _run_repair(SCRIPT_PATH, project_root, "Apply")

    assert apply.returncode == 0, apply.stdout + apply.stderr
    payload = json.loads(apply.stdout)
    targets = payload["target_fingerprints"]
    after = _acl_fingerprints(codex_root)
    assert len(targets) == 2, json.dumps({"before": before, "payload": payload}, indent=2)
    assert all(fingerprint.startswith(f"{sid}|") for fingerprint in targets)
    assert Counter(after) == Counter(before) - Counter(targets)
    assert sum(fingerprint.startswith(f"{sid}|") for fingerprint in after) == 2


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_check_never_invokes_writer(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    codex_root = project_root / ".codex"
    codex_root.mkdir(parents=True)
    _add_unresolved_risky_deny(codex_root, "S-1-5-21-2908765920-875073000-2352713335-4168283510")
    before = _acl_sddl(codex_root)
    script = _faulted_script(
        tmp_path,
        [
            (
                "[System.IO.Directory]::SetAccessControl($Path, $Acl)",
                'throw "injected_writer_invocation"',
            ),
            (
                "Set-Acl -LiteralPath $Path -AclObject $Acl",
                'throw "injected_fallback_writer_invocation"',
            ),
        ],
    )

    check = _run_repair(script, project_root, "Check")

    assert check.returncode == 1, check.stdout + check.stderr
    payload = json.loads(check.stdout)
    assert payload["errors"] == []
    assert payload["root_write_count"] == 0
    assert _acl_sddl(codex_root) == before


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL semantics only")
def test_repair_codex_dotdir_acl_check_runs_under_powershell_7(tmp_path: Path) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is not installed")
    project_root = tmp_path / "repo"
    (project_root / ".codex").mkdir(parents=True)

    check = _run_ps(
        [
            "-File",
            str(SCRIPT_PATH),
            "-ProjectRoot",
            str(project_root),
            "-Mode",
            "Check",
            "-Json",
        ],
        executable=pwsh,
    )

    assert check.returncode == 0, check.stdout + check.stderr
    payload = json.loads(check.stdout)
    assert payload["errors"] == []
    assert payload["root_write_count"] == 0
    assert payload["descendant_write_count"] == 0


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
