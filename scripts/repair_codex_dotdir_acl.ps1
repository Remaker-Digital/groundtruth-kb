param(
    [ValidateSet("Check", "Apply")]
    [string] $Mode = "Check",

    [string] $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,

    [switch] $Json
)

$ErrorActionPreference = "Stop"

function Convert-ToRelativePath {
    param(
        [Parameter(Mandatory = $true)] [string] $BasePath,
        [Parameter(Mandatory = $true)] [string] $TargetPath
    )
    $base = [System.IO.Path]::GetFullPath($BasePath).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $target = [System.IO.Path]::GetFullPath($TargetPath)
    if ($target.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $target.Substring($base.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    }
    return $target
}

function Test-RiskyDenyRule {
    param([Parameter(Mandatory = $true)] [System.Security.AccessControl.FileSystemAccessRule] $Rule)
    if ($Rule.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Deny) {
        return $false
    }
    if ($Rule.IsInherited) {
        return $false
    }
    $riskyRights =
        [System.Security.AccessControl.FileSystemRights]::Write -bor
        [System.Security.AccessControl.FileSystemRights]::Modify -bor
        [System.Security.AccessControl.FileSystemRights]::Delete -bor
        [System.Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor
        [System.Security.AccessControl.FileSystemRights]::ChangePermissions -bor
        [System.Security.AccessControl.FileSystemRights]::TakeOwnership
    return (($Rule.FileSystemRights -band $riskyRights) -ne 0)
}

function Get-AccessOnlyAcl {
    param([Parameter(Mandatory = $true)] [string] $Path)
    # Get-Acl works on BOTH Windows PowerShell 5.1 (.NET Framework) and
    # PowerShell 7 (.NET Core). The former [System.IO.Directory]::GetAccessControl
    # / [System.IO.File]::GetAccessControl statics were removed in .NET Core and
    # threw under pwsh (WI-5065), which made the ACL check falsely report
    # risky_deny_count=0 for every path. Get-Acl returns a FileSystemSecurity
    # whose .Access DACL is exactly what the risky-Deny logic inspects, and whose
    # PurgeAccessRules/AddAccessRule methods the repair path uses.
    return Get-Acl -LiteralPath $Path
}

function Set-AccessOnlyAcl {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] $Acl
    )
    # Set-Acl is the cross-version writer (PS5.1 + PS7), replacing the .NET
    # Core-removed [System.IO.Directory]/[System.IO.File]::SetAccessControl
    # statics (WI-5065). The $Acl was read via Get-Acl, so owner/group round-trip
    # unchanged and only the modified DACL is written back.
    Set-Acl -LiteralPath $Path -AclObject $Acl
}

function Invoke-Icacls {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] [string[]] $Arguments
    )
    $output = & icacls $Path @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "icacls failed for '$Path' with arguments '$($Arguments -join ' ')': $($output -join '; ')"
    }
}

function Get-RepairableDenyRules {
    param([Parameter(Mandatory = $true)] [string] $Path)
    try {
        $acl = Get-AccessOnlyAcl -Path $Path
    }
    catch {
        return @{
            Path = $Path
            Acl = $null
            Rules = @()
            Error = $_.Exception.Message
        }
    }

    $rules = @()
    foreach ($rule in $acl.Access) {
        if ($rule -is [System.Security.AccessControl.FileSystemAccessRule] -and (Test-RiskyDenyRule -Rule $rule)) {
            $rules += $rule
        }
    }
    return @{
        Path = $Path
        Acl = $acl
        Rules = $rules
        Error = $null
    }
}

function Remove-RepairableDenyRules {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [System.Security.AccessControl.FileSystemAccessRule[]] $Rules
    )
    $changed = $false
    $handledIdentities = @{}
    foreach ($rule in $Rules) {
        $identity = $rule.IdentityReference.Value
        if ($handledIdentities.ContainsKey($identity)) {
            continue
        }
        $handledIdentities[$identity] = $true
        $preservedRules = @()
        foreach ($existing in $Acl.Access) {
            if (
                $existing -is [System.Security.AccessControl.FileSystemAccessRule] -and
                (-not $existing.IsInherited) -and
                $existing.IdentityReference.Value -eq $identity -and
                (-not (Test-RiskyDenyRule -Rule $existing))
            ) {
                $preservedRules += $existing
            }
        }
        $Acl.PurgeAccessRules($rule.IdentityReference)
        foreach ($preservedRule in $preservedRules) {
            $Acl.AddAccessRule($preservedRule)
        }
        $changed = $true
    }
    if ($changed) {
        Set-AccessOnlyAcl -Path $Path -Acl $Acl
        # Re-enable inherited allows after Deny removal without depending on
        # icacls to resolve raw SID identities.
        if (Test-Path -LiteralPath $Path -PathType Container) {
            Enable-AccessInheritance -Path $Path
        }
        $postCheck = Get-RepairableDenyRules -Path $Path
        if ($postCheck.Error) {
            throw "post-removal ACL check failed: $($postCheck.Error)"
        }
        if ($postCheck.Rules.Count -gt 0) {
            $remaining = @()
            foreach ($remainingRule in $postCheck.Rules) {
                $remaining += "$($remainingRule.IdentityReference.Value):$($remainingRule.FileSystemRights)"
            }
            throw "deny removal did not persist; remaining risky Deny ACE(s): $($remaining -join '; ')"
        }
    }
    return $changed
}

function Enable-AccessInheritance {
    param([Parameter(Mandatory = $true)] [string] $Path)
    Invoke-Icacls -Path $Path -Arguments @("/inheritance:e")
}

function Get-RuleIdentitySid {
    param([Parameter(Mandatory = $true)] $Rule)
    try {
        return $Rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value
    }
    catch {
        return $Rule.IdentityReference.Value
    }
}

function Test-ModifyAllow {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] [System.Security.Principal.SecurityIdentifier] $IdentitySid,
        [Parameter(Mandatory = $true)] [string] $IdentityName
    )
    $acl = Get-AccessOnlyAcl -Path $Path
    $hasAllow = $false
    foreach ($existing in $acl.Access) {
        if (
            (Get-RuleIdentitySid -Rule $existing) -eq $IdentitySid.Value -and
            $existing.AccessControlType -eq [System.Security.AccessControl.AccessControlType]::Allow -and
            (($existing.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Modify) -ne 0)
        ) {
            $hasAllow = $true
            break
        }
    }
    return @{
        present = $true
        allow_present = $hasAllow
        changed = $false
        identity = $IdentityName
        sid = $IdentitySid.Value
    }
}

function Ensure-ModifyAllow {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] [System.Security.Principal.SecurityIdentifier] $IdentitySid,
        [Parameter(Mandatory = $true)] [string] $IdentityName
    )
    $status = Test-ModifyAllow -Path $Path -IdentitySid $IdentitySid -IdentityName $IdentityName
    if ($status.allow_present) {
        return $status
    }

    $acl = Get-AccessOnlyAcl -Path $Path
    $flags = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $IdentitySid,
        [System.Security.AccessControl.FileSystemRights]::Modify,
        $flags,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $acl.AddAccessRule($rule)
    Set-AccessOnlyAcl -Path $Path -Acl $acl
    $status.allow_present = $true
    $status.changed = $true
    return $status
}

function Get-CodexSandboxAllowStatus {
    param([Parameter(Mandatory = $true)] [string] $Path)
    $group = Get-LocalGroup -Name "CodexSandboxUsers" -ErrorAction SilentlyContinue
    if ($null -eq $group) {
        return @{
            present = $false
            allow_present = $false
            changed = $false
            identity = "CodexSandboxUsers"
            sid = $null
        }
    }
    return Test-ModifyAllow -Path $Path -IdentitySid $group.SID -IdentityName "CodexSandboxUsers"
}

function Ensure-CodexSandboxAllow {
    param([Parameter(Mandatory = $true)] [string] $Path)
    $group = Get-LocalGroup -Name "CodexSandboxUsers" -ErrorAction SilentlyContinue
    if ($null -eq $group) {
        return @{
            present = $false
            allow_present = $false
            changed = $false
            identity = "CodexSandboxUsers"
            sid = $null
        }
    }
    return Ensure-ModifyAllow -Path $Path -IdentitySid $group.SID -IdentityName "CodexSandboxUsers"
}

function Get-CurrentIdentityAllowStatus {
    param([Parameter(Mandatory = $true)] [string] $Path)
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    return Test-ModifyAllow -Path $Path -IdentitySid $identity.User -IdentityName $identity.Name
}

function Ensure-CurrentIdentityAllow {
    param([Parameter(Mandatory = $true)] [string] $Path)
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    return Ensure-ModifyAllow -Path $Path -IdentitySid $identity.User -IdentityName $identity.Name
}

$resolvedRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$target = [System.IO.Path]::GetFullPath((Join-Path $resolvedRoot ".codex"))

if (-not $target.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw ".codex target resolved outside project root: $target"
}
if ((Split-Path -Leaf $target) -ne ".codex") {
    throw "refusing to repair any path other than a .codex directory: $target"
}
if (-not (Test-Path -LiteralPath $target -PathType Container)) {
    throw ".codex directory not found: $target"
}

$checked = @()
$removed = @()
$errors = @()
$rootCheck = Get-RepairableDenyRules -Path $target
$checked += $target
if ($rootCheck.Error) {
    $errors += @{
        path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
        error = $rootCheck.Error
    }
}
elseif ($rootCheck.Rules.Count -gt 0) {
    foreach ($rule in $rootCheck.Rules) {
        $removed += @{
            path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
            identity = $rule.IdentityReference.Value
            rights = $rule.FileSystemRights.ToString()
            inheritance = $rule.InheritanceFlags.ToString()
            propagation = $rule.PropagationFlags.ToString()
            applied = $false
        }
    }
    if ($Mode -eq "Apply") {
        try {
            [void](Remove-RepairableDenyRules -Path $target -Acl $rootCheck.Acl -Rules $rootCheck.Rules)
            foreach ($entry in $removed) {
                $entry.applied = $true
            }
        }
        catch {
            $errors += @{
                path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
                error = "deny removal failed: $($_.Exception.Message)"
            }
        }
    }
}

$sandboxGroup = @{
    present = $false
    allow_present = $false
    changed = $false
    identity = "CodexSandboxUsers"
    sid = $null
}
$currentIdentity = @{
    present = $true
    allow_present = $false
    changed = $false
    identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
}
if (-not $rootCheck.Error) {
    if ($Mode -eq "Apply") {
        try {
            $currentIdentity = Ensure-CurrentIdentityAllow -Path $target
        }
        catch {
            $errors += @{
                path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
                error = "current identity allow update failed: $($_.Exception.Message)"
            }
        }
        try {
            $sandboxGroup = Ensure-CodexSandboxAllow -Path $target
        }
        catch {
            $errors += @{
                path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
                error = "CodexSandboxUsers allow update failed: $($_.Exception.Message)"
            }
        }
    }
    else {
        $currentIdentity = Get-CurrentIdentityAllowStatus -Path $target
        $sandboxGroup = Get-CodexSandboxAllowStatus -Path $target
    }
}

# After repairing the root, recursive child access may become available. Check
# descendants for explicit Deny ACEs too; ignore inaccessible children in Check
# mode and report them as errors.
$children = @()
try {
    $children = Get-ChildItem -LiteralPath $target -Recurse -Force -ErrorAction Stop
}
catch {
    $errors += @{
        path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
        error = "child enumeration failed: $($_.Exception.Message)"
    }
}

foreach ($child in $children) {
    $checked += $child.FullName
    $childCheck = Get-RepairableDenyRules -Path $child.FullName
    if ($childCheck.Error) {
        $errors += @{
            path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $child.FullName
            error = $childCheck.Error
        }
        continue
    }
    if ($childCheck.Rules.Count -eq 0) {
        continue
    }
    $childEntries = @()
    foreach ($rule in $childCheck.Rules) {
        $entry = @{
            path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $child.FullName
            identity = $rule.IdentityReference.Value
            rights = $rule.FileSystemRights.ToString()
            inheritance = $rule.InheritanceFlags.ToString()
            propagation = $rule.PropagationFlags.ToString()
            applied = $false
        }
        $childEntries += $entry
        $removed += $entry
    }
    if ($Mode -eq "Apply") {
        try {
            [void](Remove-RepairableDenyRules -Path $child.FullName -Acl $childCheck.Acl -Rules $childCheck.Rules)
            foreach ($entry in $childEntries) {
                $entry.applied = $true
            }
        }
        catch {
            $errors += @{
                path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $child.FullName
                error = "deny removal failed: $($_.Exception.Message)"
            }
        }
    }
}

$result = [ordered]@{
    mode = $Mode
    project_root = $resolvedRoot
    target = $target
    checked_count = $checked.Count
    risky_deny_count = $removed.Count
    removed = $removed
    sandbox_group = $sandboxGroup
    current_identity = $currentIdentity
    errors = $errors
    needs_repair = (($removed.Count -gt 0) -or ($errors.Count -gt 0))
    repaired = (($Mode -eq "Apply") -and ($removed.Count -gt 0) -and ($errors.Count -eq 0))
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
}
else {
    if ($result.needs_repair) {
        Write-Output ".codex ACL repair needed: risky_deny_count=$($result.risky_deny_count), errors=$($errors.Count)"
    }
    else {
        Write-Output ".codex ACL already clean"
    }
}

if ($Mode -eq "Check" -and $result.needs_repair) {
    exit 1
}
if ($errors.Count -gt 0) {
    exit 2
}
exit 0
