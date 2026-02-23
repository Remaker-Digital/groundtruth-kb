# run-tests-thermal-safe.ps1 — Thermal-safe batched test execution for Agent Red
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Created: 2026-02-22 (Session 74)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Usage:
#   .\scripts\run-tests-thermal-safe.ps1                         # Default: 4 workers, 30s cooling
#   .\scripts\run-tests-thermal-safe.ps1 -Workers 2 -CoolDown 60  # Hot ambient: fewer workers, longer cooling
#   .\scripts\run-tests-thermal-safe.ps1 -Fast                     # CI/cold ambient: no cooling pauses
#   .\scripts\run-tests-thermal-safe.ps1 -Batch core-a             # Run a single batch only
#   .\scripts\run-tests-thermal-safe.ps1 -SkipLive                 # Skip live/regression tests
#   .\scripts\run-tests-thermal-safe.ps1 -Coverage                 # Enable coverage collection
#   .\scripts\run-tests-thermal-safe.ps1 -DryRun                   # Print commands without executing
#
# Problem:
#   Running ~4,574 pytest tests sequentially on a single core causes sustained
#   CPU boost that triggers heat-related BSODs on Windows 11. This script
#   distributes load across cores (pytest-xdist) and inserts cooling pauses
#   between batches to allow thermal recovery.
#
# Batch Design:
#   Batch 1 (core-a):      tests/multi_tenant/                     ~2,400 tests
#   Batch 2 (core-b):      tests/unit/ + root tests + migrations   ~680 tests
#   Batch 3 (agents-chat): tests/agents/ + chat + memory + eval    ~600 tests
#   Batch 4 (integrations): tests/integrations/ + security/mocked  ~400 tests
#   Batch 5 (sequential):  tests/integration/ + regression + perf  ~120 tests (NO xdist)
#
# Prerequisites:
#   - Python 3.12+ with pytest, pytest-xdist, pytest-timeout installed
#   - pip install -r requirements-test.txt

param(
    [int]$Workers = 4,
    [int]$CoolDown = 30,
    [ValidateSet("all", "core-a", "core-b", "agents-chat", "integrations", "sequential")]
    [string]$Batch = "all",
    [switch]$SkipLive,
    [switch]$Fast,
    [switch]$Coverage,
    [switch]$StopOnFail,
    [switch]$DryRun
)

# ─── Configuration ────────────────────────────────────────────────────────────
$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

# Batch definitions: name → (directories, use_xdist, timeout, cool_seconds)
$Batches = [ordered]@{
    "core-a" = @{
        Dirs = @("tests/multi_tenant/")
        Xdist = $true
        Timeout = 30
        Cool = $CoolDown
        Label = "Multi-tenant (largest batch)"
    }
    "core-b" = @{
        Dirs = @(
            "tests/unit/",
            "tests/migrations/",
            "tests/test_conftest_smoke.py",
            "tests/test_cross_module.py",
            "tests/test_env_loader.py",
            "tests/test_error_handling.py",
            "tests/test_forgot_password.py",
            "tests/test_health.py",
            "tests/test_multi_tenant_isolation_e2e.py"
        )
        Xdist = $true
        Timeout = 30
        Cool = [math]::Max(10, [int]($CoolDown * 0.67))
        Label = "Unit + root + migrations"
    }
    "agents-chat" = @{
        Dirs = @(
            "tests/agents/",
            "tests/chat/",
            "tests/persistent_memory/",
            "tests/evaluation/"
        )
        Xdist = $true
        Timeout = 30
        Cool = [math]::Max(10, [int]($CoolDown * 0.67))
        Label = "Agents + chat + memory + eval"
    }
    "integrations" = @{
        Dirs = @(
            "tests/integrations/",
            "tests/security/test_adversarial.py"
        )
        Xdist = $true
        Timeout = 30
        Cool = [math]::Max(10, [int]($CoolDown * 0.5))
        Label = "Integrations + mocked security"
    }
    "sequential" = @{
        Dirs = @(
            "tests/integration/",
            "tests/regression/",
            "tests/performance/",
            "tests/security/test_data_integrity_live.py",
            "tests/security/test_live_penetration.py",
            "tests/security/test_rate_limiting_live.py",
            "tests/security/test_resilience_live.py",
            "tests/security/test_tenant_isolation_live.py"
        )
        Xdist = $false
        Timeout = 60
        Cool = 0
        Label = "Live endpoints (sequential only)"
    }
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

function Write-Phase {
    param([string]$Phase, [string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Phase — $Message" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-BatchHeader {
    param([string]$Name, [string]$Label, [bool]$UseXdist, [int]$WorkerCount)
    $mode = if ($UseXdist) { "$WorkerCount workers (xdist)" } else { "sequential" }
    Write-Host ""
    Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Yellow
    Write-Host "  BATCH: $Name — $Label [$mode]" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Yellow
}

function Format-Duration {
    param([TimeSpan]$Duration)
    if ($Duration.TotalMinutes -ge 1) {
        return "{0:N0}m {1:N0}s" -f [math]::Floor($Duration.TotalMinutes), $Duration.Seconds
    }
    return "{0:N1}s" -f $Duration.TotalSeconds
}

# ─── Pre-flight ───────────────────────────────────────────────────────────────

Write-Phase "PRE-FLIGHT" "Verifying test infrastructure"

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] $pythonVersion" -ForegroundColor Green

# Check pytest + xdist
$pytestCheck = python -m pytest --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] pytest not installed" -ForegroundColor Red
    exit 1
}
$hasXdist = $pytestCheck | Select-String "xdist"
if (-not $hasXdist) {
    Write-Host "  [FAIL] pytest-xdist not installed. Run: pip install pytest-xdist>=3.5.0" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] pytest with xdist plugin" -ForegroundColor Green

# Check pytest-timeout
$hasTimeout = $pytestCheck | Select-String "timeout"
if (-not $hasTimeout) {
    Write-Host "  [WARN] pytest-timeout not detected — tests may run without timeout protection" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] pytest-timeout plugin" -ForegroundColor Green
}

# System info
$coreCount = (Get-CimInstance -ClassName Win32_Processor).NumberOfLogicalProcessors
Write-Host "  [INFO] CPU cores: $coreCount (using $Workers workers per batch)" -ForegroundColor Gray
Write-Host "  [INFO] Cooling: $(if ($Fast) { 'DISABLED (fast mode)' } else { "${CoolDown}s between batches" })" -ForegroundColor Gray

# Coverage setup
if ($Coverage) {
    # Remove stale coverage data
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
    Write-Host "  [INFO] Coverage collection: ENABLED" -ForegroundColor Gray
}

# ─── Determine which batches to run ──────────────────────────────────────────

$batchesToRun = if ($Batch -eq "all") {
    $Batches.Keys | ForEach-Object { $_ }
} else {
    @($Batch)
}

if ($SkipLive) {
    $batchesToRun = $batchesToRun | Where-Object { $_ -ne "sequential" }
    Write-Host "  [INFO] Skipping live/sequential batch" -ForegroundColor Gray
}

# ─── Print batch plan ────────────────────────────────────────────────────────

Write-Phase "BATCH PLAN" "$(($batchesToRun | Measure-Object).Count) batches queued"

foreach ($name in $batchesToRun) {
    $b = $Batches[$name]
    $mode = if ($b.Xdist) { "-n $Workers" } else { "sequential" }
    $dirCount = ($b.Dirs | Measure-Object).Count
    Write-Host "  $name — $($b.Label) ($dirCount paths, $mode, ${$b.Timeout}s timeout)" -ForegroundColor White
}

if ($DryRun) {
    Write-Host ""
    Write-Host "  DRY RUN — commands that would be executed:" -ForegroundColor Magenta
    Write-Host ""
}

# ─── Execute batches ──────────────────────────────────────────────────────────

$results = @{}
$overallStart = Get-Date
$totalPassed = 0
$totalFailed = 0
$totalSkipped = 0
$anyFailure = $false

foreach ($name in $batchesToRun) {
    $b = $Batches[$name]
    Write-BatchHeader -Name $name -Label $b.Label -UseXdist $b.Xdist -WorkerCount $Workers

    # Build pytest command
    $args = @()
    $args += $b.Dirs
    if ($b.Xdist -and $Workers -gt 0) {
        $args += "-n"
        $args += "$Workers"
    }
    $args += "--timeout=$($b.Timeout)"
    $args += "-q"
    $args += "--tb=short"
    $args += "--no-header"

    if ($Coverage) {
        $args += "--cov=src"
        $args += "--cov-append"
        $args += "--no-cov-on-fail"
    }

    $cmdStr = "python -m pytest $($args -join ' ')"

    if ($DryRun) {
        Write-Host "  CMD: $cmdStr" -ForegroundColor Magenta
        $results[$name] = @{ Status = "DRY_RUN"; Passed = 0; Failed = 0; Skipped = 0; Duration = [TimeSpan]::Zero }
        continue
    }

    # Execute
    $batchStart = Get-Date
    Write-Host "  CMD: $cmdStr" -ForegroundColor DarkGray

    # Run pytest and capture output
    $output = & python -m pytest @args 2>&1
    $exitCode = $LASTEXITCODE
    $batchDuration = (Get-Date) - $batchStart

    # Parse summary line (e.g., "1234 passed, 1 failed, 5 skipped in 12.34s")
    $summaryLine = ($output | Select-String -Pattern "\d+ passed" | Select-Object -Last 1)
    $passed = 0; $failed = 0; $skipped = 0
    if ($summaryLine) {
        if ($summaryLine -match "(\d+) passed") { $passed = [int]$Matches[1] }
        if ($summaryLine -match "(\d+) failed") { $failed = [int]$Matches[1] }
        if ($summaryLine -match "(\d+) skipped") { $skipped = [int]$Matches[1] }
        if ($summaryLine -match "(\d+) deselected") { $skipped += [int]$Matches[1] }
    }

    $totalPassed += $passed
    $totalFailed += $failed
    $totalSkipped += $skipped

    $status = if ($exitCode -eq 0) { "PASS" } elseif ($exitCode -eq 5) { "SKIP" } else { "FAIL" }

    if ($status -eq "FAIL") {
        $anyFailure = $true
        Write-Host "  RESULT: $status — $passed passed, $failed FAILED, $skipped skipped ($(Format-Duration $batchDuration))" -ForegroundColor Red
        # Show failure details
        $failureLines = $output | Select-String -Pattern "FAILED|ERROR|AssertionError|assert "
        $failureLines | Select-Object -First 10 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor Red
        }
    } elseif ($status -eq "SKIP") {
        Write-Host "  RESULT: $status — all tests skipped ($(Format-Duration $batchDuration))" -ForegroundColor Yellow
    } else {
        Write-Host "  RESULT: $status — $passed passed, $skipped skipped ($(Format-Duration $batchDuration))" -ForegroundColor Green
    }

    $results[$name] = @{
        Status = $status
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Duration = $batchDuration
        ExitCode = $exitCode
    }

    # Stop on failure if requested
    if ($anyFailure -and $StopOnFail) {
        Write-Host ""
        Write-Host "  STOPPING — -StopOnFail is set and batch '$name' failed" -ForegroundColor Red
        break
    }

    # Cooling pause (skip for last batch, fast mode, or sequential batch)
    $coolTime = if ($Fast) { 0 } else { $b.Cool }
    if ($coolTime -gt 0 -and $name -ne ($batchesToRun | Select-Object -Last 1)) {
        Write-Host "  COOLING: ${coolTime}s thermal recovery pause..." -ForegroundColor DarkGray
        Start-Sleep -Seconds $coolTime
    }
}

# ─── Summary ──────────────────────────────────────────────────────────────────

$overallDuration = (Get-Date) - $overallStart

Write-Phase "SUMMARY" "Test execution complete"

Write-Host ""
Write-Host "  Batch Results:" -ForegroundColor White
Write-Host "  ─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

foreach ($name in $batchesToRun) {
    $r = $results[$name]
    $color = switch ($r.Status) {
        "PASS" { "Green" }
        "SKIP" { "Yellow" }
        "FAIL" { "Red" }
        "DRY_RUN" { "Magenta" }
        default { "White" }
    }
    $detail = "$($r.Passed) passed, $($r.Failed) failed, $($r.Skipped) skipped"
    $dur = Format-Duration $r.Duration
    Write-Host ("  {0,-15} {1,-6} {2} ({3})" -f $name, $r.Status, $detail, $dur) -ForegroundColor $color
}

Write-Host "  ─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ("  TOTAL:         {0} passed, {1} failed, {2} skipped" -f $totalPassed, $totalFailed, $totalSkipped) -ForegroundColor White
Write-Host ("  ELAPSED:       {0}" -f (Format-Duration $overallDuration)) -ForegroundColor White
Write-Host ""

# Coverage report
if ($Coverage -and -not $DryRun) {
    Write-Host "  Coverage Report:" -ForegroundColor White
    & python -m coverage report --fail-under=70 2>&1 | ForEach-Object { Write-Host "    $_" }
    Write-Host ""
}

# Overall verdict
if ($DryRun) {
    Write-Host "  OVERALL: DRY RUN — no tests executed" -ForegroundColor Magenta
    exit 0
} elseif ($anyFailure) {
    Write-Host "  OVERALL: FAIL" -ForegroundColor Red
    Write-Host ""
    Write-Host "  To re-run a failed batch:" -ForegroundColor Yellow
    Write-Host "    .\scripts\run-tests-thermal-safe.ps1 -Batch <batch-name> -Workers 2" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  OVERALL: PASS" -ForegroundColor Green
    exit 0
}
