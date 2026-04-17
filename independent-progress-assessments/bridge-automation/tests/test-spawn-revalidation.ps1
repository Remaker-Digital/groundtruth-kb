# test-spawn-revalidation.ps1
#
# Integration test for the spawn revalidation guard defined in
# bridge-scan-common.ps1. Exercises the seven-case mutate-between-snapshot-
# and-guard matrix from bridge/bridge-spawn-revalidation-005.md (approved
# at -006).
#
# Usage:
#   powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass `
#     -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
#
# Exits 0 on all-pass, 1 on any failure. Prints one line per case.
#
# Every case follows the five-step deterministic flow from the proposal:
#   1. Create a temp INDEX.md with a known initial state.
#   2. Capture a snapshot from the temp INDEX via Get-IndexEntryTopVersion.
#   3. Mutate the temp INDEX to a new state (or leave it alone for fresh cases).
#   4. Invoke Invoke-GuardedLaunch with a no-op launch scriptblock.
#   5. Assert on Launched / Reason / Result and the stale-log presence.
#
# No live bridge/INDEX.md is read or mutated. All fixtures live under
# a per-run temp directory that is removed when the test exits.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "..\bridge-scan-common.ps1")

$script:Failures = New-Object System.Collections.Generic.List[string]
$script:Passes   = 0

function New-TempWorkspace {
    $guid   = [guid]::NewGuid().ToString("N")
    $root   = Join-Path ([System.IO.Path]::GetTempPath()) "spawn-revalidation-$guid"
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    return $root
}

function Write-TempIndex {
    param(
        [Parameter(Mandatory)] [string] $IndexPath,
        [Parameter(Mandatory)] [string] $Body
    )
    # Normalize line endings so the regex-based parser sees one entry per line.
    $normalized = $Body -replace "`r`n", "`n"
    Set-Content -LiteralPath $IndexPath -Value $normalized -Encoding UTF8 -NoNewline
}

function Invoke-TestCase {
    param(
        [Parameter(Mandatory)] [string]      $Name,
        [Parameter(Mandatory)] [string]      $InitialIndex,
        [Parameter(Mandatory)] [string]      $DocumentName,
        [Parameter(Mandatory)] [scriptblock] $Mutate,
        [Parameter(Mandatory)] [bool]        $ExpectLaunched,
        [Parameter(Mandatory)] [string]      $ExpectReason
    )

    $workspace = New-TempWorkspace
    $indexPath = Join-Path $workspace "INDEX.md"
    $stalePath = Join-Path $workspace "logs\bridge-snapshot-stale.log"

    try {
        Write-TempIndex -IndexPath $indexPath -Body $InitialIndex

        $snapshotRow = Get-IndexEntryTopVersion -IndexPath $indexPath -DocumentName $DocumentName
        if ($null -eq $snapshotRow) {
            throw "setup error: initial INDEX has no top version for document '$DocumentName'"
        }
        $snapshot = [pscustomobject]@{
            DocumentName = $DocumentName
            Status       = $snapshotRow.Status
            File         = $snapshotRow.Path
        }

        & $Mutate $indexPath

        $invoked = $false
        $launchBlock = {
            $script:invoked = $true
            return 'LAUNCH_SENTINEL'
        }

        $result = Invoke-GuardedLaunch `
            -SelectedSnapshot $snapshot `
            -IndexPath        $indexPath `
            -LaunchAction     $launchBlock `
            -StaleLogPath     $stalePath

        # Assertions
        if ($result.Launched -ne $ExpectLaunched) {
            throw "Launched=$($result.Launched), expected $ExpectLaunched"
        }
        if ($result.Reason -ne $ExpectReason) {
            throw "Reason='$($result.Reason)', expected '$ExpectReason'"
        }
        if ($ExpectLaunched) {
            if (-not $script:invoked) {
                throw "LaunchAction was not invoked on fresh snapshot"
            }
            if ($result.Result -ne 'LAUNCH_SENTINEL') {
                throw "Result='$($result.Result)', expected 'LAUNCH_SENTINEL'"
            }
            if (Test-Path -LiteralPath $stalePath) {
                throw "stale log unexpectedly written on fresh snapshot"
            }
        }
        else {
            if ($script:invoked) {
                throw "LaunchAction was invoked despite stale snapshot"
            }
            if (-not (Test-Path -LiteralPath $stalePath)) {
                throw "stale log missing after stale snapshot"
            }
            $staleContent = Get-Content -LiteralPath $stalePath -Raw
            if ($staleContent -notmatch 'SNAPSHOT-STALE') {
                throw "stale log missing SNAPSHOT-STALE marker; got: $staleContent"
            }
            if ($staleContent -notmatch [regex]::Escape($DocumentName)) {
                throw "stale log missing document name; got: $staleContent"
            }
        }

        Write-Host "  PASS : $Name"
        $script:Passes += 1
    }
    catch {
        $msg = "$Name : $($_.Exception.Message)"
        Write-Host "  FAIL : $msg"
        $script:Failures.Add($msg)
    }
    finally {
        # Reset the shared invoked flag so subsequent cases are not tainted.
        Set-Variable -Name invoked -Scope Script -Value $false
        if (Test-Path -LiteralPath $workspace) {
            Remove-Item -LiteralPath $workspace -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Spawn revalidation matrix"
Write-Host "-------------------------"

# ---------------------------------------------------------------------------
# Case 1: no mutation — snapshot stays the top version, launch proceeds.
Invoke-TestCase `
    -Name "1 no-mutation (fresh)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate { param($indexPath) } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

# ---------------------------------------------------------------------------
# Case 2: status promotion NEW->GO above the captured line.
Invoke-TestCase `
    -Name "2 status promotion (NEW->GO, stale)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# Case 3: file revision (REVISED line replaces the top version file path).
Invoke-TestCase `
    -Name "3 file revision (same document, new file, stale)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
REVISED: bridge/widget-refactor-003.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# Case 4: same status, different path (e.g., renumbered NEW).
Invoke-TestCase `
    -Name "4 same-status different-path (stale)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
NEW: bridge/widget-refactor-999.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# Case 5: entry removed entirely.
Invoke-TestCase `
    -Name "5 entry removed (stale)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: some-other
NEW: bridge/some-other-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# Case 6: unrelated document prepended above — target document's top line
# unchanged, so snapshot is still fresh.
Invoke-TestCase `
    -Name "6 unrelated document added (fresh)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: auth-overhaul
NEW: bridge/auth-overhaul-001.md
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

# ---------------------------------------------------------------------------
# Case 7: unrelated document below mutated (REVISED added) — target entry's
# top version is unchanged, so fresh.
Invoke-TestCase `
    -Name "7 unrelated document below mutated (fresh)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
Document: auth-overhaul
NEW: bridge/auth-overhaul-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
Document: auth-overhaul
REVISED: bridge/auth-overhaul-003.md
NEW: bridge/auth-overhaul-001.md
"@
    } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

Write-Host ""
Write-Host ("Summary: {0} passed, {1} failed" -f $script:Passes, $script:Failures.Count)
if ($script:Failures.Count -gt 0) {
    Write-Host "Failures:"
    foreach ($f in $script:Failures) {
        Write-Host "  - $f"
    }
    exit 1
}

exit 0
