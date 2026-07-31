#!/usr/bin/env pwsh
# Preflight validation for gtkb-file-move-and-rename-list.csv

$ErrorActionPreference = 'Stop'
$manifestPath = 'E:\GT-KB\gtkb-file-move-and-rename-list.csv'
$basePath = 'E:\GT-KB'

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "   PREFLIGHT VALIDATION REPORT" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "Manifest : $manifestPath"
Write-Host "Base Path: $basePath"
Write-Host ""

$csv = Import-Csv $manifestPath

# Build full paths for each row (CSV already has absolute dir paths)
$manifestRows = $csv | ForEach-Object {
    [PSCustomObject]@{
        SourcePath  = Join-Path $_.'Current home directory:' $_.'Current file name:'
        DestPath    = Join-Path $_.'New home directory:' $_.'New file name:'
        SourceDir   = $_.'Current home directory:'
        SourceFile  = $_.'Current file name:'
        DestDir     = $_.'New home directory:'
        DestFile    = $_.'New file name:'
        # Normalized relative source (strip base to compare with git ls-files output)
        RelSource   = (Join-Path $_.'Current home directory:' $_.'Current file name:') -replace "^\\?[a-zA-Z]:\\GT-KB\\", ''
    }
}

$results = @()

# ------------------------------------------------------------------
# 1. Total data rows
# ------------------------------------------------------------------
$totalRows = $manifestRows.Count
$pass = $totalRows -eq 90
$results += [PSCustomObject]@{ Check='1'; Label="Total data rows"; Got=$totalRows; Expected=90; Pass=$pass }

# ------------------------------------------------------------------
# 2. .claude\hooks sources
# ------------------------------------------------------------------
$hooksCount = ($manifestRows | Where-Object { $_.SourceDir -match '[\\/]hooks[\\/]?$' -and $_.SourceDir -match '\.claude' }).Count
$pass = $hooksCount -eq 33
$results += [PSCustomObject]@{ Check='2'; Label=".claude\hooks sources"; Got=$hooksCount; Expected=33; Pass=$pass }

# ------------------------------------------------------------------
# 3. .claude\rules sources
# ------------------------------------------------------------------
$rulesCount = ($manifestRows | Where-Object { $_.SourceDir -match '[\\/]rules[\\/]?$' -and $_.SourceDir -match '\.claude' }).Count
$pass = $rulesCount -eq 38
$results += [PSCustomObject]@{ Check='3'; Label=".claude\rules sources"; Got=$rulesCount; Expected=38; Pass=$pass }

# ------------------------------------------------------------------
# 4. config\agent-control sources
# ------------------------------------------------------------------
$configCount = ($manifestRows | Where-Object { $_.SourceDir -match 'agent-control' }).Count
$pass = $configCount -eq 19
$results += [PSCustomObject]@{ Check='4'; Label="config\agent-control sources"; Got=$configCount; Expected=19; Pass=$pass }

# ------------------------------------------------------------------
# 5. Source file existence
# ------------------------------------------------------------------
$missingSources = $manifestRows | Where-Object { -not (Test-Path -LiteralPath $_.SourcePath) }
$missingCount = $missingSources.Count
$pass = $missingCount -eq 0
$results += [PSCustomObject]@{ Check='5'; Label="Source files exist"; Got="$missingCount missing"; Expected="0 missing"; Pass=$pass }
if ($missingCount -gt 0) {
    Write-Host "   MISSING source files:" -ForegroundColor Yellow
    $missingSources | ForEach-Object { Write-Host "     ✗ $($_.SourcePath)" -ForegroundColor Yellow }
}

# ------------------------------------------------------------------
# 6. Destination collision check
# ------------------------------------------------------------------
$collisions = $manifestRows | Where-Object { Test-Path -LiteralPath $_.DestPath }
$collisionCount = $collisions.Count
$pass = $collisionCount -eq 0
$results += [PSCustomObject]@{ Check='6'; Label="Destination collisions"; Got="$collisionCount exist"; Expected="0 exist"; Pass=$pass }
if ($collisionCount -gt 0) {
    Write-Host "   COLLISION — destination already exists:" -ForegroundColor Yellow
    $collisions | ForEach-Object { Write-Host "     ✗ $($_.DestPath)" -ForegroundColor Yellow }
}

# ------------------------------------------------------------------
# 7. Runtime/state/log files (none expected)
# ------------------------------------------------------------------
$runtimePatterns = '\.(log|tmp|cache|pid|lock|bak|swp)$', 'state\.json$', 'runtime\.json$'
$runtimeFiles = $manifestRows | Where-Object {
    $r = $false
    foreach ($p in $runtimePatterns) {
        if ($_.SourceFile -match $p -or $_.DestFile -match $p) { $r = $true; break }
    }
    $r
}
$runtimeCount = $runtimeFiles.Count
$pass = $runtimeCount -eq 0
$results += [PSCustomObject]@{ Check='7'; Label="Runtime/state/log files"; Got=$runtimeCount; Expected=0; Pass=$pass }
if ($runtimeCount -gt 0) {
    Write-Host "   SUSPICIOUS runtime files:" -ForegroundColor Yellow
    $runtimeFiles | ForEach-Object { Write-Host "     ✗ $($_.SourceFile) -> $($_.DestFile)" -ForegroundColor Yellow }
}

# ------------------------------------------------------------------
# 8. Typo check in destination paths+names
# ------------------------------------------------------------------
$typoPatterns = 'conytol', 'gtbk(?!\-)', 'ageny', 'contol(?!l)', 'contorl', 'hoooks', 'reles', 'agnt-control'
# Note: 'gtbk' destination filenames ARE expected (e.g. gtkb-*.py) — only flag typos in directory names or misspellings
# We specifically look for: conytol, ageny, contol, contorl in ANY field; and malformed directory spellings
$dirTypoPatterns = 'conytol', 'ageny', 'contol(?!l)', 'contorl', 'hoooks', 'reles', 'agnt-control'
$typos = $manifestRows | Where-Object {
    $hit = $false
    foreach ($p in $dirTypoPatterns) {
        if ($_.DestDir -match $p -or $_.DestFile -match $p) { $hit = $true; break }
    }
    $hit
}
$typoCount = $typos.Count
$pass = $typoCount -eq 0
$results += [PSCustomObject]@{ Check='8'; Label="Destination typos"; Got=$typoCount; Expected=0; Pass=$pass }
if ($typoCount -gt 0) {
    Write-Host "   TYPO hits:" -ForegroundColor Yellow
    $typos | ForEach-Object { Write-Host "     ✗ $($_.DestDir)\$($_.DestFile)" -ForegroundColor Yellow }
}

# ------------------------------------------------------------------
# 9. Git-tracked files NOT in manifest (will remain in place)
# ------------------------------------------------------------------
Push-Location $basePath
try {
    $gitFilesRaw = git ls-files '.claude/hooks/' '.claude/rules/' 'config/agent-control/' 2>$null
    # Normalize to Windows backslash paths
    $gitFiles = $gitFilesRaw | ForEach-Object { $_ -replace '/', '\' }

    $manifestRelSources = $manifestRows | ForEach-Object { $_.RelSource }

    $untracked = $gitFiles | Where-Object { $_ -notin $manifestRelSources }
    $untrackedCount = $untracked.Count
} finally {
    Pop-Location
}

# Check 9 is informational — not a PASS/FAIL, but we report it
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# PRINT TABULAR RESULTS
# ------------------------------------------------------------------
Write-Host ""
Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  CHECK RESULTS" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
Write-Host ("{0,-3} {1,-33} {2,-20} {3,-16} {4}" -f "#", "Check", "Got", "Expected", "Result")
Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan

$overallPass = $true
foreach ($r in $results) {
    $color = if ($r.Pass) { "Green" } else { "Red"; $overallPass = $false }
    $tag   = if ($r.Pass) { "PASS" } else { "FAIL" }
    Write-Host ("{0,-3} {1,-33} {2,-20} {3,-16} " -f $r.Check, $r.Label, $r.Got, $r.Expected) -NoNewline
    Write-Host $tag -ForegroundColor $color
}

Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "CHECK 9 — Git-tracked files NOT in manifest (informational)" -ForegroundColor Cyan
Write-Host "  Files that will remain in place after the move: $untrackedCount" -ForegroundColor $(if ($untrackedCount -eq 0) { "Green" } else { "Yellow" })
if ($untrackedCount -gt 0) {
    Write-Host ""
    # Group by directory
    $grouped = $untracked | Group-Object { Split-Path $_ -Parent } | Sort-Object Name
    foreach ($g in $grouped) {
        $dirLabel = $g.Name -replace '\\', '/'
        Write-Host "  $dirLabel/ ($($g.Count) file(s)):" -ForegroundColor Yellow
        $g.Group | Sort-Object | ForEach-Object {
            $fname = Split-Path $_ -Leaf
            Write-Host "    • $fname" -ForegroundColor Gray
        }
    }
}

# ------------------------------------------------------------------
# FINAL VERDICT
# ------------------------------------------------------------------
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
if ($overallPass) {
    Write-Host "  PREFLIGHT VERDICT:  P A S S" -ForegroundColor Green -BackgroundColor Black
    Write-Host "  All 8 validation checks passed." -ForegroundColor Green
    if ($untrackedCount -gt 0) {
        Write-Host "  Note: $untrackedCount git-tracked file(s) will remain in place (not in manifest)." -ForegroundColor Yellow
    }
} else {
    $failCount = ($results | Where-Object { -not $_.Pass }).Count
    Write-Host "  PREFLIGHT VERDICT:  F A I L" -ForegroundColor Red -BackgroundColor Black
    Write-Host "  $failCount check(s) failed. Review red items above before proceeding." -ForegroundColor Red
}
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
