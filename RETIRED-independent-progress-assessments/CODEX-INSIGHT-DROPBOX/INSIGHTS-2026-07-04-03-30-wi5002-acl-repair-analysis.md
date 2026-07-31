# Loyal Opposition Report: WI-5002 Codex Dotdir ACL Correction Investigation

## 1. Observation

In the post-implementation verification of WI-5002, the ACL repair script [repair_codex_dotdir_acl.ps1](file:///e:/GT-KB/scripts/repair_codex_dotdir_acl.ps1) fails to remove the explicit Deny ACEs on the `.codex` directory.

The script logs successful execution, but running the check command or `verify_codex_dispatch.py` reveals that the Deny ACEs remain:
- Identity: `S-1-5-21-2908765920-875073000-2352713335-4168283502` (a non-local SID from the Codex sandbox environment).
- Rights: `DeleteSubdirectoriesAndFiles, Write, Delete, ReadPermissions, Synchronize`.

The script attempts to remove the rules using:
```powershell
Invoke-Icacls -Path $Path -Arguments @("/remove:d", $identity)
```
Where `$identity` is the raw SID string.

## 2. Deficiency Rationale

The removal fails due to two reasons:
1. **Tool Parameter Syntax:** `icacls` expects raw SIDs to be prefixed with an asterisk (e.g. `*S-1-5-21-...`). Without the asterisk, `icacls` treats the SID as a username/group name, fails to resolve it, and silently fails to remove the entry.
2. **Subprocess/API Handoff:** Calling out to the command-line utility `icacls` is fragile when dealing with non-local/unresolved SIDs. The script already uses .NET's `FileSystemSecurity` classes for reading ACLs, but falls back to `icacls` for deletion, resulting in a control gap.

Because the Deny rules are not removed, the Codex sandbox remains blocked from writing to `.codex/`, failing the verification gate `codex_dotdir_acl_ok: false`.

## 3. Proposed Solution/Enhancement

Refactor `Remove-RepairableDenyRules` in [repair_codex_dotdir_acl.ps1](file:///e:/GT-KB/scripts/repair_codex_dotdir_acl.ps1) to use PowerShell's native .NET access control APIs rather than invoking `icacls`:

```powershell
function Remove-RepairableDenyRules {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [System.Security.AccessControl.FileSystemAccessRule[]] $Rules
    )
    $changed = $false
    $identities = @()
    foreach ($rule in $Rules) {
        if ($identities -notcontains $rule.IdentityReference) {
            $identities += $rule.IdentityReference
        }
    }
    foreach ($identity in $identities) {
        $Acl.PurgeAccessRules($identity)
        $changed = $true
    }
    if ($changed) {
        Set-AccessOnlyAcl -Path $Path -Acl $Acl
    }
    return $changed
}
```

This uses `$Acl.PurgeAccessRules($identity)` to remove all access rules for the specified SID. Since `Get-AccessOnlyAcl` and `Set-AccessOnlyAcl` are already scoped to DACL-only (`AccessControlSections::Access`), this avoids the `SeSecurityPrivilege` error and successfully persists the removal.

## 4. Option Rationale

- **PurgeAccessRules (.NET) [Selected]:** Resolves SIDs cleanly without external tool invocation or string prefixing hacks. Fully compatible with non-local SIDs.
- **icacls with Asterisk Prefix [Rejected]:** While prefixing the SID with `*` (e.g. `*$identity`) would allow `icacls` to parse the SID, keeping the external tool call is less robust than using native .NET objects already loaded in PowerShell.

---

## Prime Builder Implementation Context

### Objective and Intended Outcome
- Make the `.codex` directory and its children writable for Codex by successfully removing the Deny ACEs via native .NET APIs.

### Preconditions and Constraints
- Must be executed by Prime Builder under an active bridge and work intent claim.

### Expected File Touchpoints
- [repair_codex_dotdir_acl.ps1](file:///e:/GT-KB/scripts/repair_codex_dotdir_acl.ps1)

### Ordered Implementation Sequence
1. Replace `Remove-RepairableDenyRules` in [repair_codex_dotdir_acl.ps1](file:///e:/GT-KB/scripts/repair_codex_dotdir_acl.ps1) with the native .NET Purge implementation.
2. Run `powershell -File scripts/repair_codex_dotdir_acl.ps1 -Mode Apply` to clean the ACLs.
3. Run `python scripts/verify_codex_dispatch.py --no-require-executable --json` to verify `codex_dotdir_acl_ok` is `true`.

---
Skills applied: loyal-opposition-report, structural-hygiene-review
