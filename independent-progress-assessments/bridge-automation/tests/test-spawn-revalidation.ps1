# test-spawn-revalidation.ps1
#
# Integration test for the spawn revalidation guard defined in
# bridge-scan-common.ps1. Exercises the approved seven-case SEMANTIC
# matrix from bridge/bridge-spawn-revalidation-003.md:111-119 (retained
# in -005 and accepted at -006), using the five-step deterministic flow:
#
#   1. Create a temp INDEX.md with a known initial state.
#   2. Capture a snapshot from the temp INDEX via Get-IndexEntryTopVersion.
#   3. Mutate the temp INDEX to a new state (or leave it alone for fresh
#      cases).
#   4. Invoke Invoke-GuardedLaunch with a no-op launch scriptblock.
#   5. Assert on Launched / Reason / Result and the stale-log presence.
#
# The seven approved semantic cases map to real Codex/Prime scanner
# outcomes:
#
#   1. Codex NEW -> NEW fresh          (unchanged NEW; review proceeds)
#   2. Codex NEW -> VERIFIED stale     (review already completed elsewhere)
#   3. Codex REVISED -> later NEW stale (Prime filed post-impl after
#                                        Codex captured REVISED for review)
#   4. Prime GO -> GO fresh            (unchanged GO; impl proceeds)
#   5. Prime NO-GO -> NO-GO fresh      (unchanged NO-GO; revise proceeds)
#   6. Prime GO -> NO-GO stale         (owner/Codex objection arrived)
#   7. Prime GO -> VERIFIED stale      (S299 Azure replay: VERIFIED
#                                        landed while spawn queued)
#
# Additional cases 8-10 are supplementary coverage (entry removed,
# unrelated-document fresh) and may be dropped without losing approved-
# matrix coverage.
#
# Usage:
#   powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass `
#     -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
#
# Exits 0 on all-pass, 1 on any failure. Prints one line per case.
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

Write-Host "Spawn revalidation semantic matrix (bridge-spawn-revalidation-003:111-119)"
Write-Host "-----------------------------------------------------------------------"

# ---------------------------------------------------------------------------
# CASE 1 — Codex NEW -> NEW fresh.
# Scenario: scanner captured NEW, nothing changes, review proceeds.
Invoke-TestCase `
    -Name "1 Codex NEW -> NEW (fresh)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate { param($indexPath) } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

# ---------------------------------------------------------------------------
# CASE 2 — Codex NEW -> VERIFIED stale.
# Scenario: scanner captured NEW, but another reviewer or post-impl cycle
# landed VERIFIED on top before this scanner reached launch. Abort.
Invoke-TestCase `
    -Name "2 Codex NEW -> VERIFIED (stale)" `
    -InitialIndex @"
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
VERIFIED: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# CASE 3 — Codex captured REVISED -> later NEW stale.
# Scenario: scanner captured REVISED for review, then Prime filed a post-
# implementation NEW before the review spawn ran. Abort; Prime's NEW
# supersedes Codex's pending REVISED work.
Invoke-TestCase `
    -Name "3 Codex captured REVISED -> later NEW (stale)" `
    -InitialIndex @"
Document: widget-refactor
REVISED: bridge/widget-refactor-003.md
NO-GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
NEW: bridge/widget-refactor-004.md
REVISED: bridge/widget-refactor-003.md
NO-GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# CASE 4 — Prime GO -> GO fresh.
# Scenario: scanner captured GO, nothing changes, implementation proceeds.
Invoke-TestCase `
    -Name "4 Prime GO -> GO (fresh)" `
    -InitialIndex @"
Document: widget-refactor
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate { param($indexPath) } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

# ---------------------------------------------------------------------------
# CASE 5 — Prime NO-GO -> NO-GO fresh.
# Scenario: scanner captured NO-GO, nothing changes, revise spawn proceeds.
Invoke-TestCase `
    -Name "5 Prime NO-GO -> NO-GO (fresh)" `
    -InitialIndex @"
Document: widget-refactor
NO-GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate { param($indexPath) } `
    -ExpectLaunched $true `
    -ExpectReason "fresh"

# ---------------------------------------------------------------------------
# CASE 6 — Prime GO -> NO-GO stale.
# Scenario: scanner captured GO for implementation, but owner/Codex
# objection landed NO-GO on top before launch. Abort.
Invoke-TestCase `
    -Name "6 Prime GO -> NO-GO (stale)" `
    -InitialIndex @"
Document: widget-refactor
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
NO-GO: bridge/widget-refactor-003.md
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# CASE 7 — Prime GO -> VERIFIED stale (S299 Azure replay).
# Scenario: scanner captured GO, but VERIFIED landed before launch.
# This is the specific incident that motivated the A1 work: Azure
# taxonomy GO at -002 was dispatched to a headless spawn after Codex
# had already landed VERIFIED at -004, producing duplicate work
# (commit 98563fc). Abort.
Invoke-TestCase `
    -Name "7 Prime GO -> VERIFIED (stale, S299 Azure replay)" `
    -InitialIndex @"
Document: widget-refactor
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@ `
    -DocumentName "widget-refactor" `
    -Mutate {
        param($indexPath)
        Write-TempIndex -IndexPath $indexPath -Body @"
Document: widget-refactor
VERIFIED: bridge/widget-refactor-004.md
NEW: bridge/widget-refactor-003.md
GO: bridge/widget-refactor-002.md
NEW: bridge/widget-refactor-001.md
"@
    } `
    -ExpectLaunched $false `
    -ExpectReason "stale"

# ---------------------------------------------------------------------------
# Supplementary coverage (not required by approved matrix).
# ---------------------------------------------------------------------------

# CASE 8 — Entry removed entirely.
# Scenario: INDEX maintenance removed the captured entry between
# snapshot and launch. Abort.
Invoke-TestCase `
    -Name "8 entry removed (stale)" `
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

# CASE 9 — Unrelated document added above; target top unchanged.
# Scenario: other work filed a new entry at the top while this scanner
# was running. Target doc's top line is unchanged -> still fresh.
Invoke-TestCase `
    -Name "9 unrelated document above (fresh)" `
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

# CASE 10 — Unrelated document below mutated; target top unchanged.
Invoke-TestCase `
    -Name "10 unrelated document below mutated (fresh)" `
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
