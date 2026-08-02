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
    # Windows PowerShell can fail module auto-loading when launched with
    # CREATE_NO_WINDOW; use .NET ACL statics there and fall back for PowerShell 7,
    # where those statics were removed.
    try {
        $sections = [System.Security.AccessControl.AccessControlSections]::All
        if (Test-Path -LiteralPath $Path -PathType Container) {
            $acl = [System.IO.Directory]::GetAccessControl($Path, $sections)
        }
        else {
            $acl = [System.IO.File]::GetAccessControl($Path, $sections)
        }
        $acl | Add-Member -NotePropertyName GtkbAuditReadable -NotePropertyValue $true -Force
        return $acl
    }
    catch {
        $methodUnavailable = $_.Exception.Message -match "does not contain a method named 'GetAccessControl'"
        $auditUnavailable = (
            $_.Exception -is [System.Security.AccessControl.PrivilegeNotHeldException] -or
            $_.Exception -is [System.UnauthorizedAccessException] -or
            $_.Exception.InnerException -is [System.Security.AccessControl.PrivilegeNotHeldException] -or
            $_.Exception.Message -match "SeSecurityPrivilege"
        )
        if (-not $methodUnavailable -and -not $auditUnavailable) {
            throw
        }
        if ($auditUnavailable) {
            if (Test-Path -LiteralPath $Path -PathType Container) {
                $acl = [System.IO.Directory]::GetAccessControl($Path)
            }
            else {
                $acl = [System.IO.File]::GetAccessControl($Path)
            }
            $acl | Add-Member -NotePropertyName GtkbAuditReadable -NotePropertyValue $false -Force
            return $acl
        }
    }
    try {
        $acl = Get-Acl -LiteralPath $Path -Audit
        $acl | Add-Member -NotePropertyName GtkbAuditReadable -NotePropertyValue $true -Force
        return $acl
    }
    catch [System.Security.AccessControl.PrivilegeNotHeldException] {
        $acl = Get-Acl -LiteralPath $Path
        $acl | Add-Member -NotePropertyName GtkbAuditReadable -NotePropertyValue $false -Force
        return $acl
    }
}

function Set-AccessOnlyAcl {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] $Acl
    )
    try {
        [System.IO.Directory]::SetAccessControl($Path, $Acl)
        return
    }
    catch {
        if ($_.Exception.Message -notmatch "does not contain a method named 'SetAccessControl'") {
            throw
        }
    }
    Set-Acl -LiteralPath $Path -AclObject $Acl
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

function Get-RuleIdentitySid {
    param([Parameter(Mandatory = $true)] $Rule)
    try {
        return $Rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value
    }
    catch {
        return $Rule.IdentityReference.Value
    }
}

function Get-RuleFingerprint {
    param([Parameter(Mandatory = $true)] $Rule)
    return "{0}|{1}|{2}|{3}|{4}|{5}" -f @(
        (Get-RuleIdentitySid -Rule $Rule),
        [int] $Rule.AccessControlType,
        [int64] $Rule.FileSystemRights,
        [int] $Rule.InheritanceFlags,
        [int] $Rule.PropagationFlags,
        [bool] $Rule.IsInherited
    )
}

function Get-AclPrincipal {
    param(
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [ValidateSet("Owner", "Group")] [string] $Kind
    )
    try {
        if ($Kind -eq "Owner") {
            return $Acl.GetOwner([System.Security.Principal.SecurityIdentifier]).Value
        }
        return $Acl.GetGroup([System.Security.Principal.SecurityIdentifier]).Value
    }
    catch {
        if ($Kind -eq "Owner") {
            return $Acl.Owner
        }
        return $Acl.Group
    }
}

function Get-StringSha256 {
    param([Parameter(Mandatory = $true)] [AllowEmptyString()] [string] $Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-ByteArraySha256 {
    param([Parameter(Mandatory = $true)] [byte[]] $Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($Value))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-AclSnapshot {
    param([Parameter(Mandatory = $true)] $Acl)
    $auditReadable = (
        $Acl.PSObject.Properties.Name -contains "GtkbAuditReadable" -and
        [bool] $Acl.GtkbAuditReadable
    )
    $fingerprints = @(
        foreach ($rule in $Acl.Access) {
            if ($rule -is [System.Security.AccessControl.FileSystemAccessRule]) {
                Get-RuleFingerprint -Rule $rule
            }
        }
    ) | Sort-Object
    return @{
        fingerprints = @($fingerprints)
        fingerprint_count = $fingerprints.Count
        fingerprint_sha256 = Get-StringSha256 -Value ($fingerprints -join "`n")
        owner = Get-AclPrincipal -Acl $Acl -Kind Owner
        group = Get-AclPrincipal -Acl $Acl -Kind Group
        access_rules_protected = [bool] $Acl.AreAccessRulesProtected
        audit_readable = $auditReadable
        audit_sddl_sha256 = if ($auditReadable) {
            Get-StringSha256 -Value $Acl.GetSecurityDescriptorSddlForm(
                [System.Security.AccessControl.AccessControlSections]::Audit
            )
        } else { $null }
        descriptor_binary_sha256 = Get-ByteArraySha256 -Value $Acl.GetSecurityDescriptorBinaryForm()
    }
}

function Test-StringArrayEqual {
    param(
        [Parameter(Mandatory = $true)] [string[]] $Left,
        [Parameter(Mandatory = $true)] [string[]] $Right
    )
    if ($Left.Count -ne $Right.Count) {
        return $false
    }
    for ($index = 0; $index -lt $Left.Count; $index += 1) {
        if ($Left[$index] -cne $Right[$index]) {
            return $false
        }
    }
    return $true
}

function Test-AclSnapshotEqual {
    param(
        [Parameter(Mandatory = $true)] $Left,
        [Parameter(Mandatory = $true)] $Right
    )
    return (
        (Test-StringArrayEqual -Left $Left.fingerprints -Right $Right.fingerprints) -and
        $Left.owner -eq $Right.owner -and
        $Left.group -eq $Right.group -and
        $Left.access_rules_protected -eq $Right.access_rules_protected -and
        $Left.audit_readable -eq $Right.audit_readable -and
        $Left.audit_sddl_sha256 -eq $Right.audit_sddl_sha256 -and
        $Left.descriptor_binary_sha256 -eq $Right.descriptor_binary_sha256
    )
}

function Copy-AccessAcl {
    param([Parameter(Mandatory = $true)] $Acl)
    $copy = New-Object System.Security.AccessControl.DirectorySecurity
    $sections =
        [System.Security.AccessControl.AccessControlSections]::Access -bor
        [System.Security.AccessControl.AccessControlSections]::Owner -bor
        [System.Security.AccessControl.AccessControlSections]::Group
    $auditReadable = (
        $Acl.PSObject.Properties.Name -contains "GtkbAuditReadable" -and
        [bool] $Acl.GtkbAuditReadable
    )
    if ($auditReadable) {
        $sections = $sections -bor [System.Security.AccessControl.AccessControlSections]::Audit
    }
    $copy.SetSecurityDescriptorBinaryForm($Acl.GetSecurityDescriptorBinaryForm(), $sections)
    $copy | Add-Member -NotePropertyName GtkbAuditReadable -NotePropertyValue $auditReadable -Force
    return $copy
}

function Remove-FingerprintOccurrences {
    param(
        [Parameter(Mandatory = $true)] [string[]] $Fingerprints,
        [Parameter(Mandatory = $true)] [string[]] $RemovedFingerprints
    )
    $remaining = New-Object System.Collections.ArrayList
    foreach ($fingerprint in $Fingerprints) {
        [void] $remaining.Add($fingerprint)
    }
    foreach ($fingerprint in $RemovedFingerprints) {
        $index = $remaining.IndexOf($fingerprint)
        if ($index -lt 0) {
            throw "selected ACL fingerprint is absent from the authoritative preimage: $fingerprint"
        }
        $remaining.RemoveAt($index)
    }
    return @($remaining | Sort-Object)
}

function Test-ModifyAllow {
    param(
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [System.Security.Principal.SecurityIdentifier] $IdentitySid,
        [Parameter(Mandatory = $true)] [string] $IdentityName
    )
    $hasAllow = $false
    foreach ($existing in $acl.Access) {
        if (
            (Get-RuleIdentitySid -Rule $existing) -eq $IdentitySid.Value -and
            $existing.AccessControlType -eq [System.Security.AccessControl.AccessControlType]::Allow -and
            (($existing.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Modify) -eq
                [System.Security.AccessControl.FileSystemRights]::Modify) -and
            (($existing.PropagationFlags -band [System.Security.AccessControl.PropagationFlags]::InheritOnly) -eq 0)
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

function Get-LocalPrincipalSid {
    param([Parameter(Mandatory = $true)] [string] $IdentityName)
    $candidates = @($IdentityName)
    if ($env:COMPUTERNAME) {
        $candidates += "$env:COMPUTERNAME\$IdentityName"
    }
    foreach ($candidate in $candidates) {
        try {
            $account = New-Object System.Security.Principal.NTAccount($candidate)
            return $account.Translate([System.Security.Principal.SecurityIdentifier])
        }
        catch {
        }
    }
    try {
        $group = Get-LocalGroup -Name $IdentityName -ErrorAction SilentlyContinue
        if ($null -ne $group) {
            return $group.SID
        }
    }
    catch {
    }
    return $null
}

function Get-CodexSandboxAllowStatus {
    param([Parameter(Mandatory = $true)] $Acl)
    $sid = Get-LocalPrincipalSid -IdentityName "CodexSandboxUsers"
    if ($null -eq $sid) {
        return @{
            present = $false
            allow_present = $false
            changed = $false
            identity = "CodexSandboxUsers"
            sid = $null
        }
    }
    return Test-ModifyAllow -Acl $Acl -IdentitySid $sid -IdentityName "CodexSandboxUsers"
}

function Get-CurrentIdentityAllowStatus {
    param([Parameter(Mandatory = $true)] $Acl)
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    return Test-ModifyAllow -Acl $Acl -IdentitySid $identity.User -IdentityName $identity.Name
}

function Test-AllowStatusEqual {
    param(
        [Parameter(Mandatory = $true)] $Left,
        [Parameter(Mandatory = $true)] $Right
    )
    return (
        $Left.present -eq $Right.present -and
        $Left.allow_present -eq $Right.allow_present -and
        $Left.sid -eq $Right.sid
    )
}

function New-ExactAclTransform {
    param(
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [System.Security.AccessControl.FileSystemAccessRule[]] $Rules,
        [Parameter(Mandatory = $true)] $CurrentIdentity,
        [Parameter(Mandatory = $true)] $SandboxGroup
    )
    $preSnapshot = Get-AclSnapshot -Acl $Acl
    $workingAcl = Copy-AccessAcl -Acl $Acl
    $targetFingerprints = @($Rules | ForEach-Object { Get-RuleFingerprint -Rule $_ })
    $expectedFingerprints = Remove-FingerprintOccurrences `
        -Fingerprints $preSnapshot.fingerprints `
        -RemovedFingerprints $targetFingerprints
    foreach ($rule in $Rules) {
        $workingAcl.RemoveAccessRuleSpecific($rule)
    }
    $transformedSnapshot = Get-AclSnapshot -Acl $workingAcl
    if (-not (Test-StringArrayEqual -Left $expectedFingerprints -Right $transformedSnapshot.fingerprints)) {
        throw "prewrite_invariant_mismatch: transformed ACE multiset differs from exact selected-rule removal"
    }
    if (
        $preSnapshot.owner -ne $transformedSnapshot.owner -or
        $preSnapshot.group -ne $transformedSnapshot.group -or
        $preSnapshot.access_rules_protected -ne $transformedSnapshot.access_rules_protected -or
        $preSnapshot.audit_readable -ne $transformedSnapshot.audit_readable -or
        $preSnapshot.audit_sddl_sha256 -ne $transformedSnapshot.audit_sddl_sha256
    ) {
        throw "prewrite_invariant_mismatch: owner, group, or access-rule protection changed"
    }
    $currentSid = New-Object System.Security.Principal.SecurityIdentifier($CurrentIdentity.sid)
    $sandboxSid = New-Object System.Security.Principal.SecurityIdentifier($SandboxGroup.sid)
    $transformedCurrent = Test-ModifyAllow `
        -Acl $workingAcl -IdentitySid $currentSid -IdentityName $CurrentIdentity.identity
    $transformedSandbox = Test-ModifyAllow `
        -Acl $workingAcl -IdentitySid $sandboxSid -IdentityName $SandboxGroup.identity
    if (
        -not (Test-AllowStatusEqual -Left $CurrentIdentity -Right $transformedCurrent) -or
        -not (Test-AllowStatusEqual -Left $SandboxGroup -Right $transformedSandbox)
    ) {
        throw "prewrite_invariant_mismatch: required Modify allow state changed"
    }
    return @{
        acl = $workingAcl
        expected_snapshot = $transformedSnapshot
        pre_snapshot = $preSnapshot
        target_fingerprints = @($targetFingerprints)
    }
}

function Invoke-ExactRootAclApply {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] $Acl,
        [Parameter(Mandatory = $true)] [System.Security.AccessControl.FileSystemAccessRule[]] $Rules,
        [Parameter(Mandatory = $true)] $CurrentIdentity,
        [Parameter(Mandatory = $true)] $SandboxGroup
    )
    $outcome = [ordered]@{
        success = $false
        error = $null
        target_fingerprints = @()
        pre_snapshot = Get-AclSnapshot -Acl $Acl
        expected_snapshot = $null
        post_snapshot = $null
        apply_write_count = 0
        rollback_write_count = 0
        descendant_write_count = 0
        rollback = [ordered]@{
            attempted = $false
            proven = $false
            error = $null
            expected_fingerprint_sha256 = $null
            observed_fingerprint_sha256 = $null
            expected_descriptor_sha256 = $null
            observed_descriptor_sha256 = $null
            owner_equal = $false
            group_equal = $false
            protection_equal = $false
        }
    }
    try {
        $transform = New-ExactAclTransform `
            -Acl $Acl -Rules $Rules `
            -CurrentIdentity $CurrentIdentity -SandboxGroup $SandboxGroup
        $outcome.target_fingerprints = $transform.target_fingerprints
        $outcome.expected_snapshot = $transform.expected_snapshot
    }
    catch {
        $outcome.error = $_.Exception.Message
        return $outcome
    }
    try {
        Set-AccessOnlyAcl -Path $Path -Acl $transform.acl
        $outcome.apply_write_count = 1
        $postAcl = Get-AccessOnlyAcl -Path $Path
        $outcome.post_snapshot = Get-AclSnapshot -Acl $postAcl
        if (-not (Test-AclSnapshotEqual -Left $transform.expected_snapshot -Right $outcome.post_snapshot)) {
            throw "postwrite_invariant_mismatch: root descriptor readback differs from the proven candidate"
        }
        $outcome.success = $true
        return $outcome
    }
    catch {
        $outcome.error = $_.Exception.Message
        if ($outcome.apply_write_count -eq 0) {
            return $outcome
        }
        $outcome.rollback.attempted = $true
        try {
            $rollbackAclObject = Copy-AccessAcl -Acl $Acl
            Set-AccessOnlyAcl -Path $Path -Acl $rollbackAclObject
            $outcome.rollback_write_count = 1
            $rollbackAcl = Get-AccessOnlyAcl -Path $Path
            $rollbackSnapshot = Get-AclSnapshot -Acl $rollbackAcl
            $outcome.rollback.expected_fingerprint_sha256 = $outcome.pre_snapshot.fingerprint_sha256
            $outcome.rollback.observed_fingerprint_sha256 = $rollbackSnapshot.fingerprint_sha256
            $outcome.rollback.expected_descriptor_sha256 = $outcome.pre_snapshot.descriptor_binary_sha256
            $outcome.rollback.observed_descriptor_sha256 = $rollbackSnapshot.descriptor_binary_sha256
            $outcome.rollback.owner_equal = $outcome.pre_snapshot.owner -eq $rollbackSnapshot.owner
            $outcome.rollback.group_equal = $outcome.pre_snapshot.group -eq $rollbackSnapshot.group
            $outcome.rollback.protection_equal = (
                $outcome.pre_snapshot.access_rules_protected -eq $rollbackSnapshot.access_rules_protected
            )
            $outcome.rollback.proven = Test-AclSnapshotEqual `
                -Left $outcome.pre_snapshot -Right $rollbackSnapshot
            if (-not $outcome.rollback.proven) {
                $outcome.rollback.error = "rollback_invariant_mismatch"
            }
        }
        catch {
            $outcome.rollback.error = $_.Exception.Message
        }
        return $outcome
    }
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
$applyOutcome = [ordered]@{
    success = $false
    error = $null
    target_fingerprints = @()
    pre_snapshot = $null
    post_snapshot = $null
    apply_write_count = 0
    rollback_write_count = 0
    descendant_write_count = 0
    rollback = [ordered]@{
        attempted = $false
        proven = $false
        error = $null
        expected_fingerprint_sha256 = $null
        observed_fingerprint_sha256 = $null
        expected_descriptor_sha256 = $null
        observed_descriptor_sha256 = $null
        owner_equal = $false
        group_equal = $false
        protection_equal = $false
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
            fingerprint = Get-RuleFingerprint -Rule $rule
            applied = $false
        }
    }
}

if (-not $rootCheck.Error) {
    $currentIdentity = Get-CurrentIdentityAllowStatus -Acl $rootCheck.Acl
    $sandboxGroup = Get-CodexSandboxAllowStatus -Acl $rootCheck.Acl
}

if ($Mode -eq "Apply" -and (-not $rootCheck.Error)) {
    if (-not $currentIdentity.allow_present -or -not $sandboxGroup.present -or -not $sandboxGroup.allow_present) {
        $errors += @{
            path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
            error = "required_modify_allow_missing: Apply requires unchanged current-user and CodexSandboxUsers Modify allows"
        }
    }
    elseif ($rootCheck.Rules.Count -gt 0) {
        $applyOutcome = Invoke-ExactRootAclApply `
            -Path $target -Acl $rootCheck.Acl -Rules $rootCheck.Rules `
            -CurrentIdentity $currentIdentity -SandboxGroup $sandboxGroup
        if ($applyOutcome.success) {
            foreach ($entry in $removed) {
                $entry.applied = $true
            }
        }
        else {
            $errors += @{
                path = Convert-ToRelativePath -BasePath $resolvedRoot -TargetPath $target
                error = "exact root deny removal failed: $($applyOutcome.error)"
            }
        }
    }
}

if (-not $rootCheck.Error -and $Mode -eq "Check") {
    # After repairing the root, recursive child access may become available.
    # Check descendants for explicit Deny ACEs too; if root ACL access itself
    # fails, avoid emitting the same launcher/capability error for every child.
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
                fingerprint = Get-RuleFingerprint -Rule $rule
                applied = $false
            }
            $childEntries += $entry
            $removed += $entry
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
    target_fingerprints = $applyOutcome.target_fingerprints
    pre_non_target_fingerprint_sha256 = if ($applyOutcome.expected_snapshot) { $applyOutcome.expected_snapshot.fingerprint_sha256 } else { $null }
    post_non_target_fingerprint_sha256 = if ($applyOutcome.post_snapshot) { $applyOutcome.post_snapshot.fingerprint_sha256 } else { $null }
    pre_non_target_fingerprint_count = if ($applyOutcome.expected_snapshot) { $applyOutcome.expected_snapshot.fingerprint_count } else { $null }
    post_non_target_fingerprint_count = if ($applyOutcome.post_snapshot) { $applyOutcome.post_snapshot.fingerprint_count } else { $null }
    owner_equal = [bool] $applyOutcome.success
    group_equal = [bool] $applyOutcome.success
    protection_equal = [bool] $applyOutcome.success
    required_allows_equal = [bool] $applyOutcome.success
    sacl_readable = if ($applyOutcome.pre_snapshot) { $applyOutcome.pre_snapshot.audit_readable } else { $null }
    sacl_equal = if ($applyOutcome.success -and $applyOutcome.pre_snapshot.audit_readable) {
        $applyOutcome.pre_snapshot.audit_readable -eq $applyOutcome.post_snapshot.audit_readable -and
        $applyOutcome.pre_snapshot.audit_sddl_sha256 -eq $applyOutcome.post_snapshot.audit_sddl_sha256
    } elseif ($applyOutcome.success) { $null } else { $false }
    pre_descriptor_sha256 = if ($applyOutcome.pre_snapshot) { $applyOutcome.pre_snapshot.descriptor_binary_sha256 } else { $null }
    expected_descriptor_sha256 = if ($applyOutcome.expected_snapshot) { $applyOutcome.expected_snapshot.descriptor_binary_sha256 } else { $null }
    post_descriptor_sha256 = if ($applyOutcome.post_snapshot) { $applyOutcome.post_snapshot.descriptor_binary_sha256 } else { $null }
    apply_write_count = $applyOutcome.apply_write_count
    rollback_write_count = $applyOutcome.rollback_write_count
    root_write_count = $applyOutcome.apply_write_count + $applyOutcome.rollback_write_count
    descendant_write_count = 0
    rollback = $applyOutcome.rollback
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
