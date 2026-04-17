# bridge-scan-common.ps1
#
# Shared helper functions for the file-bridge scanners. Dot-sourced by
# codex-file-bridge-scan.ps1, claude-file-bridge-scan.ps1, and
# tests/test-spawn-revalidation.ps1.
#
# SIDE-EFFECT-FREE AT LOAD. Defines functions only; does not run any
# poller logic or read any operational state. Safe to dot-source from
# tests without triggering bridge activity.
#
# Functions:
#   Get-IndexEntryTopVersion  — read the top-of-list status/file pair for a
#                               specific Document: entry in bridge/INDEX.md.
#                               Pure read. Returns $null if entry not found.
#
#   Test-SnapshotStillFresh   — compare a captured snapshot against the
#                               current INDEX.md state for the same document.
#                               Returns $true only on exact status+file match.
#
#   Invoke-GuardedLaunch      — the pre-spawn TOCTOU guard. Re-reads INDEX.md,
#                               invokes the caller's LaunchAction scriptblock
#                               only if the snapshot is still the top entry.
#                               On staleness: appends a SNAPSHOT-STALE record to
#                               StaleLogPath and returns without launching.
#
# Contract: the SelectedSnapshot pscustomobject carries three fields:
#   DocumentName : string — the bridge document name (value after "Document:")
#   Status       : string — one of NEW REVISED GO NO-GO VERIFIED
#   File         : string — the path after the status line (e.g., bridge/x-002.md)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Set-StrictMode -Version Latest

function Get-IndexEntryTopVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $IndexPath,
        [Parameter(Mandatory)] [string] $DocumentName
    )

    if (-not (Test-Path -LiteralPath $IndexPath)) {
        return $null
    }

    $lines = Get-Content -LiteralPath $IndexPath
    $inEntry = $false
    foreach ($line in $lines) {
        if ($line -match '^Document:\s*(.+?)\s*$') {
            $inEntry = ($Matches[1] -eq $DocumentName)
            continue
        }

        if ($inEntry -and $line -match '^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(.+?)\s*$') {
            return [pscustomobject]@{
                Status = $Matches[1]
                Path   = $Matches[2]
            }
        }
    }

    return $null
}

function Test-SnapshotStillFresh {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $DocumentName,
        [Parameter(Mandatory)] [string] $ExpectedStatus,
        [Parameter(Mandatory)] [string] $ExpectedFile,
        [Parameter(Mandatory)] [string] $IndexPath
    )

    $current = Get-IndexEntryTopVersion -IndexPath $IndexPath -DocumentName $DocumentName
    if ($null -eq $current) {
        return $false
    }
    return ($current.Status -eq $ExpectedStatus -and $current.Path -eq $ExpectedFile)
}

function Invoke-GuardedLaunch {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $SelectedSnapshot,
        [Parameter(Mandatory)] [string]         $IndexPath,
        [Parameter(Mandatory)] [scriptblock]    $LaunchAction,
        [Parameter(Mandatory)] [string]         $StaleLogPath
    )

    $fresh = Test-SnapshotStillFresh `
        -DocumentName   $SelectedSnapshot.DocumentName `
        -ExpectedStatus $SelectedSnapshot.Status `
        -ExpectedFile   $SelectedSnapshot.File `
        -IndexPath      $IndexPath

    if (-not $fresh) {
        $staleDir = Split-Path -Parent $StaleLogPath
        if ($staleDir -and -not (Test-Path -LiteralPath $staleDir)) {
            New-Item -ItemType Directory -Force -Path $staleDir | Out-Null
        }
        $record = [ordered]@{
            event           = 'SNAPSHOT-STALE'
            document        = $SelectedSnapshot.DocumentName
            expected_status = $SelectedSnapshot.Status
            expected_file   = $SelectedSnapshot.File
            timestamp_utc   = (Get-Date).ToUniversalTime().ToString('o')
        }
        Add-Content -LiteralPath $StaleLogPath -Value ($record | ConvertTo-Json -Compress)
        return [pscustomobject]@{
            Launched = $false
            Reason   = 'stale'
            Result   = $null
        }
    }

    $result = & $LaunchAction
    return [pscustomobject]@{
        Launched = $true
        Reason   = 'fresh'
        Result   = $result
    }
}
