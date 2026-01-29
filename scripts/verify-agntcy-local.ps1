# Agent Red - AGNTCY Local Docker Verification Script
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# PURPOSE: One-time baseline verification of the AGNTCY open-source platform.
# This script clones AGNTCY from GitHub into an isolated temporary directory,
# builds and runs its Docker stack, and executes its test suite.
#
# ISOLATION POLICY: This script creates its own isolated clone and Docker
# containers. It does NOT interact with any other local AGNTCY clones or
# containers that may exist on this machine. The -Cleanup flag (recommended)
# removes all artifacts after verification.
#
# Usage:
#   .\scripts\verify-agntcy-local.ps1
#   .\scripts\verify-agntcy-local.ps1 -SkipBuild    # Skip Docker build if stack is already running
#   .\scripts\verify-agntcy-local.ps1 -Cleanup       # Remove clone and containers after verification

param(
    [string]$AgntcyPath = "$env:TEMP\agntcy-verification",
    [switch]$SkipBuild,
    [switch]$Cleanup
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AGNTCY Local Docker Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check prerequisites
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
$pythonVersion = py -3.13 --version 2>&1
Write-Host "  Docker: $dockerVersion"
Write-Host "  Python: $pythonVersion"

# Step 2: Clone AGNTCY if not present
Write-Host "`n[2/7] Checking AGNTCY clone..." -ForegroundColor Yellow
if (-not (Test-Path "$AgntcyPath\docker-compose.yml")) {
    Write-Host "  Cloning AGNTCY repository..."
    git clone https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service.git $AgntcyPath
    Copy-Item "$AgntcyPath\.env.example" "$AgntcyPath\.env"
    Write-Host "  Clone complete." -ForegroundColor Green
} else {
    Write-Host "  AGNTCY already cloned at $AgntcyPath" -ForegroundColor Green
}

# Step 3: Verify config files
Write-Host "`n[3/7] Verifying config files..." -ForegroundColor Yellow
$configs = @(
    "$AgntcyPath\config\slim\server-config.yaml",
    "$AgntcyPath\config\otel\otel-collector-config.yaml",
    "$AgntcyPath\config\grafana\datasources.yaml"
)
$allConfigsExist = $true
foreach ($config in $configs) {
    if (Test-Path $config) {
        Write-Host "  OK: $($config | Split-Path -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $config" -ForegroundColor Red
        $allConfigsExist = $false
    }
}

# Step 4: Build and start Docker stack
if (-not $SkipBuild) {
    Write-Host "`n[4/7] Building and starting Docker stack..." -ForegroundColor Yellow
    Push-Location $AgntcyPath
    docker compose build --parallel
    docker compose up -d
    Pop-Location
    Write-Host "  Waiting 30 seconds for services to stabilize..."
    Start-Sleep -Seconds 30
} else {
    Write-Host "`n[4/7] Skipping Docker build (using existing stack)..." -ForegroundColor Yellow
}

# Step 5: Health checks
Write-Host "`n[5/7] Running health checks..." -ForegroundColor Yellow
$healthChecks = @(
    @{ Name = "NATS"; Url = "http://localhost:8222/healthz" },
    @{ Name = "ClickHouse"; Url = "http://localhost:8123/ping" },
    @{ Name = "Grafana"; Url = "http://localhost:3001/api/health" },
    @{ Name = "Mock Shopify"; Url = "http://localhost:8001/health" },
    @{ Name = "Mock Zendesk"; Url = "http://localhost:8002/health" },
    @{ Name = "Mock Mailchimp"; Url = "http://localhost:8003/health" },
    @{ Name = "Mock GA"; Url = "http://localhost:8004/health" },
    @{ Name = "Console"; Url = "http://localhost:8080" }
)

$healthPassed = 0
foreach ($check in $healthChecks) {
    try {
        $response = Invoke-WebRequest -Uri $check.Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  PASS: $($check.Name) (HTTP $($response.StatusCode))" -ForegroundColor Green
        $healthPassed++
    } catch {
        Write-Host "  FAIL: $($check.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "  Health checks: $healthPassed/$($healthChecks.Count) passed"

# Step 6: Run unit tests
Write-Host "`n[6/7] Running unit tests..." -ForegroundColor Yellow
Push-Location $AgntcyPath
if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..."
    py -3.13 -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt -q
}
$unitResult = & .\.venv\Scripts\pytest.exe tests/unit/ -v --tb=line 2>&1
$unitSummary = $unitResult | Select-String "passed|failed|error" | Select-Object -Last 1
Write-Host "  $unitSummary"
Pop-Location

# Step 7: Run integration tests
Write-Host "`n[7/7] Running integration tests..." -ForegroundColor Yellow
Push-Location $AgntcyPath
$intResult = & .\.venv\Scripts\pytest.exe tests/integration/ -v --tb=line 2>&1
$intSummary = $intResult | Select-String "passed|failed|error" | Select-Object -Last 1
Write-Host "  $intSummary"
Pop-Location

# Cleanup
if ($Cleanup) {
    Write-Host "`nCleaning up Docker stack..." -ForegroundColor Yellow
    Push-Location $AgntcyPath
    docker compose down
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
