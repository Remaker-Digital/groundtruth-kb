# rollback.ps1 — Emergency rollback for Agent Red API Gateway
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-14
# Last corrected: 2026-02-14 — Fixed stale ACR name (was acragentredeastus, now acragentredeastus)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
$PROD_URL = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path

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
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║  EMERGENCY ROLLBACK                                         ║" -ForegroundColor Red
Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Red
Write-Host "║  Target image: $Image" -ForegroundColor Red
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Red
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
az containerapp update `
    --name $CONTAINER_APP `
    --resource-group $RESOURCE_GROUP `
    --image $Image 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

if ($LASTEXITCODE -ne 0) {
    Write-Host "CRITICAL: Rollback deployment command failed!" -ForegroundColor Red
    Write-Host "Manual intervention required. Contact Azure support if needed." -ForegroundColor Red
    exit 1
}
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
    Write-Host "WARNING: /health not responding after 60s — NATS may still be starting" -ForegroundColor Yellow
    Write-Host "  Check again in 30s: curl $PROD_URL/health" -ForegroundColor Yellow
}

# Step 3: Run Tier 0 regression
Write-Host "[3/4] Running Tier 0 regression tests..." -ForegroundColor Yellow
Push-Location $PROJECT_ROOT
$env:PROD_URL = $PROD_URL
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
$testResult = $LASTEXITCODE
Pop-Location

if ($testResult -ne 0) {
    Write-Host "  Tier 0 tests FAILED after rollback — investigate immediately" -ForegroundColor Red
} else {
    Write-Host "  Tier 0 tests passed" -ForegroundColor Green
}

# Step 4: Deactivate old revisions
Write-Host "[4/4] Cleaning up old revisions..." -ForegroundColor Yellow
$allRevisions = az containerapp revision list `
    --name $CONTAINER_APP `
    --resource-group $RESOURCE_GROUP `
    --query "[?properties.active==``true``].name" -o tsv 2>&1
$revList = $allRevisions -split "`n" | Where-Object { $_ -ne "" }
if ($revList.Count -gt 1) {
    $newest = $revList[-1]
    foreach ($rev in $revList) {
        if ($rev -ne $newest) {
            Write-Host "  Deactivating: $rev" -ForegroundColor Gray
            az containerapp revision deactivate --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --revision $rev 2>&1 | Out-Null
        }
    }
}

# Summary
$currentImage = az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" -o tsv 2>&1
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ROLLBACK COMPLETE                                          ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Image now serving: $currentImage" -ForegroundColor Green
Write-Host "║  Tier 0 tests: $(if($testResult -eq 0){'PASSED'}else{'FAILED'})" -ForegroundColor $(if($testResult -eq 0){'Green'}else{'Red'})
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

# ─── Known Failure Modes ─────────────────────────────────────────────────────
# See docs/operations/REPEATABLE-PROCEDURES.md Section 2.6
#
# | Failure                                   | Classification        | Resolution                                                    |
# |-------------------------------------------|-----------------------|---------------------------------------------------------------|
# | ACR name was acragentredeastus2            | Procedure defect      | Corrected 2026-02-14: now acragentredeastus (no trailing "2") |
# | az containerapp update stderr on Windows   | Environment (Windows) | PowerShell treats az CLI progress output as error stream.     |
# |                                           |                       | Check exit code / output table — command likely succeeded.    |
