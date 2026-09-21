# rollback.ps1 - Emergency rollback for Agent Red API Gateway
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-14
# Last corrected: 2026-02-14 - Fixed stale ACR name (was acragentredeastus, now acragentredeastus)
#
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Usage:
#   .\rollback.ps1 -Image "acragentredeastus.azurecr.io/api-gateway:v1.25.1"
#   .\rollback.ps1 -Version "v1.25.1"
#
# This script:
#   1. Deploys the specified image immediately
#   2. Waits for health
#   3. Runs Tier 0 regression tests
#   4. Deactivates failed revision

param(
    [string]$Image = "",
    [string]$Version = ""
)

$ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
$RESOURCE_GROUP = "Agent-Red"
$CONTAINER_APP = "agent-red-api-gateway"
# Rotates if Container App environment changes - override via $env:PROD_URL
$PROD_URL = if ($env:PROD_URL) { $env:PROD_URL } else { "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io" }
$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path
$APP_ROOT = Join-Path $PROJECT_ROOT 'applications\Agent_Red'
$REGRESSION_TEST = Join-Path $APP_ROOT 'tests\regression\test_upgrade_regression.py'
$PYTEST_CONFIG = Join-Path $PROJECT_ROOT 'pyproject.toml'
foreach ($requiredPath in @($REGRESSION_TEST, $PYTEST_CONFIG)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        Write-Error "Required regression input is missing: $requiredPath"
        exit 1
    }
}

# Resolve image
if (-not $Image -and $Version) {
    $Image = "${ACR_LOGIN_SERVER}/api-gateway:$Version"
}
if (-not $Image) {
    Write-Host "ERROR: Provide -Image or -Version" -ForegroundColor Red
    Write-Host "  .\rollback.ps1 -Version v1.12.0"
    Write-Host "  .\rollback.ps1 -Image acragentredeastus.azurecr.io/api-gateway:v1.12.0"
    exit 1
}

Write-Host ""
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Red
Write-Host "|  EMERGENCY ROLLBACK                                         |" -ForegroundColor Red
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Red
Write-Host "|  Target image: $Image" -ForegroundColor Red
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Red
Write-Host ""

# Step 0: Verify rollback image exists in ACR
Write-Host "[0/4] Verifying rollback image exists in ACR..." -ForegroundColor Yellow
$imageParts = $Image -split ":"
$repoName = ($imageParts[0] -split "/")[-1]
$tagName = $imageParts[1]
if ($repoName -and $tagName) {
    $tagCheck = az acr repository show-tags --name acragentredeastus --repository $repoName --query "[?@=='$tagName']" -o tsv 2>&1
    if ($tagCheck -ne $tagName) {
        Write-Host "ERROR: Image tag '$tagName' not found in ACR repository '$repoName'." -ForegroundColor Red
        Write-Host "  Available tags:" -ForegroundColor Yellow
        az acr repository show-tags --name acragentredeastus --repository $repoName --top 5 --orderby time_desc -o tsv 2>&1 | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        exit 1
    }
    Write-Host "  Image verified in ACR" -ForegroundColor Green
}

# Step 1: Deploy rollback image
Write-Host "[1/4] Deploying rollback image..." -ForegroundColor Yellow
$revisionOutput = @(az containerapp update `
    --name $CONTAINER_APP `
    --resource-group $RESOURCE_GROUP `
    --image $Image `
    --query 'properties.latestRevisionName' `
    --output tsv `
    --only-show-errors)
$updateExit = $LASTEXITCODE

if ($updateExit -ne 0 -or $revisionOutput.Count -ne 1 -or
    [string]::IsNullOrWhiteSpace([string]$revisionOutput[0])) {
    Write-Error 'Rollback update failed or did not identify its revision.'
    exit 1
}
$rollbackRevision = ([string]$revisionOutput[0]).Trim()
Write-Host "  Rollback image deployed" -ForegroundColor Green

# Step 2: Wait for health (shorter timeout for rollback urgency)
Write-Host "[2/4] Waiting for health (60s timeout)..." -ForegroundColor Yellow
$elapsed = 0
$healthy = $false
while ($elapsed -lt 60) {
    Start-Sleep -Seconds 5
    $elapsed += 5
    try {
        $r = Invoke-WebRequest -Uri "$PROD_URL/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Write-Host "  /health 200 OK after ${elapsed}s" -ForegroundColor Green
            $healthy = $true
            break
        }
    } catch {
        Write-Host "  Waiting... (${elapsed}s)" -ForegroundColor Gray
    }
}

if (-not $healthy) {
    Write-Error 'Rollback health check failed; revisions were not deactivated.'
    exit 1
}

# Step 3: Run Tier 0 regression
Write-Host "[3/4] Running Tier 0 regression tests..." -ForegroundColor Yellow
$reportPath = Join-Path $APP_ROOT ('.rollback-regression-' + [guid]::NewGuid().ToString('N') + '.xml')
$previousProdUrl = $env:PROD_URL
Push-Location $APP_ROOT
try {
    $env:PROD_URL = $PROD_URL
    python -m pytest -c $PYTEST_CONFIG $REGRESSION_TEST -x -q -m tier0 --tb=short "--junitxml=$reportPath"
    $testResult = $LASTEXITCODE
    if ($testResult -ne 0) {
        throw 'Tier 0 regression failed; revisions were not deactivated.'
    }
    [xml]$report = Get-Content -LiteralPath $reportPath -Raw -ErrorAction Stop
    $failed = $report.SelectNodes('//testcase/failure | //testcase/error').Count
    $passed = $report.SelectNodes('//testcase[not(skipped) and not(failure) and not(error)]').Count
    $skipped = $report.SelectNodes('//testcase/skipped').Count
    if ($failed -ne 0 -or $skipped -ne 0 -or $passed -eq 0) {
        throw 'Tier 0 regression verification is incomplete or failed; revisions were not deactivated.'
    }
} catch {
    Write-Error $_
    exit 1
} finally {
    $env:PROD_URL = $previousProdUrl
    Pop-Location
    if (Test-Path -LiteralPath $reportPath) {
        Remove-Item -LiteralPath $reportPath -Force
    }
}
Write-Host "  Tier 0 tests passed" -ForegroundColor Green

# Step 4: Deactivate old revisions
Write-Host "[4/4] Cleaning up old revisions..." -ForegroundColor Yellow
try {
    $currentJson = az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP `
        --query 'properties.{latest:latestRevisionName,ready:latestReadyRevisionName,image:template.containers[0].image}' -o json
    if ($LASTEXITCODE -ne 0) { throw 'Cannot confirm the current rollback revision.' }
    $current = $currentJson | ConvertFrom-Json -ErrorAction Stop
    if ($current.latest -cne $rollbackRevision -or $current.ready -cne $rollbackRevision -or $current.image -cne $Image) {
        throw 'The current ready revision does not match this rollback; revisions were not deactivated.'
    }
    $allRevisions = az containerapp revision list `
        --name $CONTAINER_APP `
        --resource-group $RESOURCE_GROUP `
        --query "[?properties.active==``true``].name" -o json
    if ($LASTEXITCODE -ne 0) { throw 'Cannot list active revisions.' }
    $revList = ConvertFrom-Json -InputObject ($allRevisions -join "`n") -ErrorAction Stop
    if ($rollbackRevision -cnotin $revList) {
        throw 'The rollback revision is absent from the active revisions; revisions were not deactivated.'
    }
    foreach ($rev in $revList) {
        if ($rev -cne $rollbackRevision) {
            Write-Host "  Deactivating: $rev" -ForegroundColor Gray
            az containerapp revision deactivate --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --revision $rev | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "Could not deactivate revision: $rev" }
        }
    }
} catch {
    Write-Error $_
    exit 1
}

# Summary
$currentImage = $current.image
Write-Host ""
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Green
Write-Host "|  ROLLBACK COMPLETE                                          |" -ForegroundColor Green
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Green
Write-Host "|  Image now serving: $currentImage" -ForegroundColor Green
Write-Host "|  Tier 0 tests: $(if($testResult -eq 0){'PASSED'}else{'FAILED'})" -ForegroundColor $(if($testResult -eq 0){'Green'}else{'Red'})
Write-Host "+--------------------------------------------------------------+" -ForegroundColor Green

# --- Known Failure Modes -----------------------------------------------------
# See docs/operations/REPEATABLE-PROCEDURES.md Section 2.6
#
# | Failure                                   | Classification        | Resolution                                                    |
# |-------------------------------------------|-----------------------|---------------------------------------------------------------|
# | ACR name was acragentredeastus2            | Procedure defect      | Corrected 2026-02-14: now acragentredeastus (no trailing "2") |
# | az containerapp update stderr on Windows   | Environment (Windows) | PowerShell treats az CLI progress output as error stream.     |
# |                                           |                       | Check exit code / output table - command likely succeeded.    |
