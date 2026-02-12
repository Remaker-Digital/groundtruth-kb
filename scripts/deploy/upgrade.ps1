# upgrade.ps1 — Non-disruptive production upgrade for Agent Red API Gateway
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Usage:
#   .\upgrade.ps1 -Version "v1.13.0" [-DryRun] [-SkipBuild] [-SkipTests]
#
# Prerequisites:
#   - Azure CLI authenticated (az login)
#   - ACR access (az acr login --name acragentredeastus2)
#   - Python 3.12+ with pytest, httpx installed
#
# This script implements a 7-phase non-disruptive upgrade:
#   Phase 1: Pre-flight checks (health, revision count, credential access)
#   Phase 2: Build and push new image to ACR
#   Phase 3: Run pre-upgrade regression tests against CURRENT production
#   Phase 4: Deploy new image (rolling update)
#   Phase 5: Wait for readiness (NATS startup, health probes)
#   Phase 6: Run post-upgrade regression tests against NEW production
#   Phase 7: Verify and finalize (deactivate old revision, tag success)
#
# Rollback: If any phase fails, the script stops and prints rollback instructions.
# The old revision remains active until Phase 7 explicitly deactivates it.

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [switch]$DryRun,
    [switch]$SkipBuild,
    [switch]$SkipTests
)

# ─── Configuration ────────────────────────────────────────────────────────────
$ACR = "acragentredeastus2"
$ACR_LOGIN_SERVER = "acragentredeastus2.azurecr.io"
$RESOURCE_GROUP = "agentred-prod-rg"
$CONTAINER_APP = "agent-red-api-gateway"
$IMAGE_NAME = "api-gateway"
$PROD_URL = "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io"
$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path
$BUILD_CONTEXT_DIR = "$env:TEMP\agentred-build-$(Get-Date -Format 'yyyyMMddHHmmss')"
$LOG_FILE = "$PROJECT_ROOT\logs\upgrade-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Timing
$HEALTH_WAIT_SECONDS = 90       # Wait for NATS startup + health probes
$HEALTH_POLL_INTERVAL = 10      # Poll interval during health wait
$REVISION_DRAIN_SECONDS = 60    # Graceful shutdown drain period

# ─── Logging ──────────────────────────────────────────────────────────────────
function Log {
    param([string]$Level, [string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    Write-Host $line -ForegroundColor $(switch($Level) {
        "INFO" { "Cyan" }
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        "PHASE" { "Magenta" }
        default { "White" }
    })
    # Ensure log directory exists
    $logDir = Split-Path $LOG_FILE -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    Add-Content -Path $LOG_FILE -Value $line
}

function Abort {
    param([string]$Message, [string]$RollbackImage = "")
    Log "FAIL" "ABORT: $Message"
    if ($RollbackImage) {
        Log "FAIL" ""
        Log "FAIL" "╔══════════════════════════════════════════════════════════════╗"
        Log "FAIL" "║  ROLLBACK INSTRUCTIONS                                      ║"
        Log "FAIL" "╠══════════════════════════════════════════════════════════════╣"
        Log "FAIL" "║  az containerapp update ``                                  ║"
        Log "FAIL" "║    --name $CONTAINER_APP ``                                 ║"
        Log "FAIL" "║    --resource-group $RESOURCE_GROUP ``                      ║"
        Log "FAIL" "║    --image $RollbackImage                                   ║"
        Log "FAIL" "╚══════════════════════════════════════════════════════════════╝"
    }
    exit 1
}

# ─── Helper: HTTP check ──────────────────────────────────────────────────────
function Test-Endpoint {
    param([string]$Url, [int]$ExpectedStatus = 200, [int]$TimeoutSec = 10)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
        return $response.StatusCode -eq $ExpectedStatus
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) { return $true }
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: Pre-flight checks
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 1: Pre-flight checks ═══"

# Validate version format
if ($Version -notmatch '^v\d+\.\d+\.\d+$') {
    Abort "Version must be in format vX.Y.Z (got: $Version)"
}

Log "INFO" "Target version: $Version"
Log "INFO" "Production URL: $PROD_URL"
Log "INFO" "DryRun: $DryRun | SkipBuild: $SkipBuild | SkipTests: $SkipTests"

# Check Azure CLI authentication
Log "INFO" "Checking Azure CLI authentication..."
$azAccount = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Abort "Azure CLI not authenticated. Run: az login"
}
Log "PASS" "Azure CLI authenticated"

# Check current production health
Log "INFO" "Checking current production health..."
if (-not (Test-Endpoint "$PROD_URL/health")) {
    Abort "Production /health endpoint is not responding 200. Investigate before upgrading."
}
Log "PASS" "/health returns 200"

if (-not (Test-Endpoint "$PROD_URL/ready")) {
    Log "WARN" "/ready is not 200 — dependencies may be degraded. Proceeding with caution."
} else {
    Log "PASS" "/ready returns 200"
}

# Capture current image for rollback
Log "INFO" "Capturing current revision for rollback..."
$currentImage = az containerapp show `
    --name $CONTAINER_APP `
    --resource-group $RESOURCE_GROUP `
    --query "properties.template.containers[0].image" -o tsv 2>&1
if ($LASTEXITCODE -ne 0) {
    Abort "Cannot read current container image. Check Azure permissions."
}
Log "INFO" "Current image: $currentImage"
$rollbackImage = $currentImage

# Check for pending revisions (should be exactly 1 active)
$activeRevisions = az containerapp revision list `
    --name $CONTAINER_APP `
    --resource-group $RESOURCE_GROUP `
    --query "[?properties.active==``true``].name" -o tsv 2>&1
$revCount = ($activeRevisions -split "`n" | Where-Object { $_ -ne "" }).Count
if ($revCount -gt 1) {
    Log "WARN" "Multiple active revisions detected ($revCount). Expected 1. Old revisions may be lingering."
}
Log "INFO" "Active revisions: $revCount"

# Capture pre-upgrade metrics
Log "INFO" "Capturing pre-upgrade baseline metrics..."
try {
    $readyResponse = Invoke-WebRequest -Uri "$PROD_URL/ready" -Method GET -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    $readyData = $readyResponse.Content | ConvertFrom-Json
    Log "INFO" "Pre-upgrade NATS: connected=$($readyData.nats.connected)"
    Log "INFO" "Pre-upgrade circuit breakers: $($readyData.circuit_breakers | ConvertTo-Json -Compress)"
} catch {
    Log "WARN" "Could not capture pre-upgrade metrics from /ready"
}

# Verify admin SPA builds exist (required for frontend changes to take effect)
Log "INFO" "Checking admin SPA build artifacts..."
$missingDists = @()
foreach ($spa in @("admin\standalone\dist", "admin\shopify\dist", "widget\dist")) {
    $distPath = "$PROJECT_ROOT\$spa"
    if (-not (Test-Path $distPath)) {
        $missingDists += $spa
        Log "WARN" "MISSING: $spa — frontend changes will NOT be included in this deploy"
    } else {
        $distAge = (Get-Date) - (Get-Item $distPath).LastWriteTime
        if ($distAge.TotalHours -gt 24) {
            Log "WARN" "$spa is $([math]::Round($distAge.TotalHours, 1)) hours old — may be stale. Run 'npm run build' in the respective directory."
        } else {
            Log "PASS" "$spa exists (built $([math]::Round($distAge.TotalMinutes, 0)) min ago)"
        }
    }
}
if ($missingDists.Count -gt 0) {
    Log "WARN" "Missing dist directories: $($missingDists -join ', '). Build them first if this deploy includes frontend changes."
}

# Check if version tag already exists in ACR (prevent accidental overwrite)
if (-not $SkipBuild) {
    Log "INFO" "Checking if ${IMAGE_NAME}:$Version already exists in ACR..."
    $existingTags = az acr repository show-tags --name $ACR --repository $IMAGE_NAME --query "[?@=='$($Version)']" -o tsv 2>&1
    if ($existingTags -and $existingTags -eq $Version) {
        Log "WARN" "Image ${IMAGE_NAME}:$Version already exists in ACR. The build will overwrite it."
        Log "WARN" "If this is unintentional, press Ctrl+C within 5 seconds..."
        if (-not $DryRun) { Start-Sleep -Seconds 5 }
    }
}

Log "PASS" "Phase 1 complete — pre-flight checks passed"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: Build and push new image
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 2: Build and push image ═══"

if ($SkipBuild) {
    Log "WARN" "Skipping build (SkipBuild). Image $ACR_LOGIN_SERVER/${IMAGE_NAME}:$Version must already exist in ACR."
} else {
    # Create minimal build context
    Log "INFO" "Creating build context at $BUILD_CONTEXT_DIR..."

    if ($DryRun) {
        Log "INFO" "[DRY RUN] Would create build context and run az acr build"
    } else {
        New-Item -ItemType Directory -Path $BUILD_CONTEXT_DIR -Force | Out-Null

        # Copy only what Dockerfile needs
        Copy-Item "$PROJECT_ROOT\Dockerfile" "$BUILD_CONTEXT_DIR\"
        Copy-Item "$PROJECT_ROOT\requirements.txt" "$BUILD_CONTEXT_DIR\"
        Copy-Item -Recurse "$PROJECT_ROOT\src" "$BUILD_CONTEXT_DIR\src"
        Copy-Item -Recurse "$PROJECT_ROOT\config" "$BUILD_CONTEXT_DIR\config"

        # Admin SPAs (pre-built) — abort if standalone is missing (required for admin UI)
        if (-not (Test-Path "$PROJECT_ROOT\admin\standalone\dist")) {
            Abort "admin/standalone/dist is missing. Run 'cd admin/standalone && npm run build' before deploying."
        }
        New-Item -ItemType Directory -Path "$BUILD_CONTEXT_DIR\admin\standalone" -Force | Out-Null
        Copy-Item -Recurse "$PROJECT_ROOT\admin\standalone\dist" "$BUILD_CONTEXT_DIR\admin\standalone\dist"

        if (Test-Path "$PROJECT_ROOT\admin\shopify\dist") {
            New-Item -ItemType Directory -Path "$BUILD_CONTEXT_DIR\admin\shopify" -Force | Out-Null
            Copy-Item -Recurse "$PROJECT_ROOT\admin\shopify\dist" "$BUILD_CONTEXT_DIR\admin\shopify\dist"
        } else {
            Log "WARN" "admin/shopify/dist missing — Shopify embedded admin will not be updated"
        }

        # Widget bundle
        if (Test-Path "$PROJECT_ROOT\widget\dist") {
            New-Item -ItemType Directory -Path "$BUILD_CONTEXT_DIR\widget" -Force | Out-Null
            Copy-Item -Recurse "$PROJECT_ROOT\widget\dist" "$BUILD_CONTEXT_DIR\widget\dist"
        } else {
            Log "WARN" "widget/dist missing — widget bundle will not be updated"
        }

        # Source integrity check: verify critical files made it into the build context
        $criticalFiles = @(
            "src\main.py",
            "src\multi_tenant\cosmos_schema.py",
            "src\multi_tenant\auth.py",
            "src\multi_tenant\middleware.py",
            "src\chat\pipeline.py",
            "Dockerfile",
            "requirements.txt"
        )
        foreach ($f in $criticalFiles) {
            if (-not (Test-Path "$BUILD_CONTEXT_DIR\$f")) {
                Abort "Critical file missing from build context: $f"
            }
        }
        Log "PASS" "Build context integrity verified ($($criticalFiles.Count) critical files present)"

        $contextSize = (Get-ChildItem -Recurse $BUILD_CONTEXT_DIR | Measure-Object -Property Length -Sum).Sum / 1MB
        Log "INFO" "Build context size: $([math]::Round($contextSize, 1)) MB"

        # Build on ACR
        Log "INFO" "Building image on ACR: ${IMAGE_NAME}:$Version ..."
        az acr build `
            --registry $ACR `
            --image "${IMAGE_NAME}:$Version" `
            --build-arg "BUILD_VERSION=$Version" `
            --file "$BUILD_CONTEXT_DIR\Dockerfile" `
            $BUILD_CONTEXT_DIR 2>&1 | Tee-Object -Variable buildOutput

        # Note: Windows az CLI may crash with UnicodeEncodeError — check ACR for success
        $buildRun = az acr task list-runs --registry $ACR --top 1 --query "[0].status" -o tsv 2>&1
        if ($buildRun -ne "Succeeded") {
            Abort "ACR build failed or did not succeed (status: $buildRun). Check ACR portal."
        }
        Log "PASS" "Image built and pushed: ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:$Version"

        # Verify image is actually in ACR
        $verifyTag = az acr repository show-tags --name $ACR --repository $IMAGE_NAME --query "[?@=='$($Version)']" -o tsv 2>&1
        if ($verifyTag -ne $Version) {
            Abort "Image tag $Version not found in ACR after build. Check ACR portal for build status."
        }
        Log "PASS" "Verified ${IMAGE_NAME}:$Version exists in ACR"

        # Cleanup build context
        Remove-Item -Recurse -Force $BUILD_CONTEXT_DIR -ErrorAction SilentlyContinue
    }
}

Log "PASS" "Phase 2 complete — image ready"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Pre-upgrade regression tests
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 3: Pre-upgrade regression tests ═══"

if ($SkipTests) {
    Log "WARN" 'Skipping pre-upgrade regression tests (--SkipTests)'
} else {
    Log "INFO" "Running regression tests against CURRENT production..."

    if ($DryRun) {
        Log "INFO" "[DRY RUN] Would run: python -m pytest tests/regression/ -x -q --prod-url=$PROD_URL"
    } else {
        Push-Location $PROJECT_ROOT
        $env:PROD_URL = $PROD_URL
        $testResult = python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short 2>&1
        $testExitCode = $LASTEXITCODE
        Pop-Location

        $testResult | ForEach-Object { Log "INFO" "  $_" }

        if ($testExitCode -ne 0) {
            Abort "Pre-upgrade regression tests FAILED. Production may already be degraded. Investigate before upgrading." $rollbackImage
        }
        Log "PASS" "Pre-upgrade regression tests passed — current production is healthy"
    }
}

Log "PASS" "Phase 3 complete"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: Deploy new image (rolling update)
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 4: Deploy new image ═══"

$newImage = "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:$Version"
Log "INFO" "Deploying: $newImage"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would run: az containerapp update --image $newImage"
} else {
    az containerapp update `
        --name $CONTAINER_APP `
        --resource-group $RESOURCE_GROUP `
        --image $newImage 2>&1 | ForEach-Object { Log "INFO" "  $_" }

    if ($LASTEXITCODE -ne 0) {
        Abort "Container App update command failed. Old revision is still serving traffic." $rollbackImage
    }
    Log "PASS" "Update command accepted by Azure"
}

Log "PASS" "Phase 4 complete — deployment initiated"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: Wait for readiness
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 5: Wait for readiness `($HEALTH_WAIT_SECONDS seconds`) ═══"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would wait $HEALTH_WAIT_SECONDS seconds for new revision to become healthy"
} else {
    $elapsed = 0
    $healthy = $false

    while ($elapsed -lt $HEALTH_WAIT_SECONDS) {
        Start-Sleep -Seconds $HEALTH_POLL_INTERVAL
        $elapsed += $HEALTH_POLL_INTERVAL

        $healthOk = Test-Endpoint "$PROD_URL/health"
        $readyOk = Test-Endpoint "$PROD_URL/ready"

        if ($healthOk -and $readyOk) {
            Log "PASS" "Health + Ready both 200 after ${elapsed}s"
            $healthy = $true
            break
        } elseif ($healthOk) {
            Log "INFO" "Health OK, Ready not yet... [${elapsed}s / ${HEALTH_WAIT_SECONDS}s]"
        } else {
            Log "INFO" "Waiting for new revision... [${elapsed}s / ${HEALTH_WAIT_SECONDS}s]"
        }
    }

    if (-not $healthy) {
        # Check if health alone is OK (ready can be false due to lazy NATS)
        if (Test-Endpoint "$PROD_URL/health") {
            Log "WARN" "/health OK but /ready not 200 after ${HEALTH_WAIT_SECONDS}s. NATS may still be initializing."
            Log "WARN" "Proceeding — NATS lazy init is expected behavior."
        } else {
            Abort "New revision not healthy after ${HEALTH_WAIT_SECONDS}s. Immediate rollback recommended." $rollbackImage
        }
    }

    # Verify the new image is actually serving
    $currentImageAfter = az containerapp show `
        --name $CONTAINER_APP `
        --resource-group $RESOURCE_GROUP `
        --query "properties.template.containers[0].image" -o tsv 2>&1
    Log "INFO" "Image now serving: $currentImageAfter"

    if ($currentImageAfter -ne $newImage) {
        Log "WARN" "Expected $newImage but got $currentImageAfter - revision may still be transitioning"
    }
}

Log "PASS" "Phase 5 complete - new revision responsive"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: Post-upgrade regression tests
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 6: Post-upgrade regression tests ═══"

if ($SkipTests) {
    Log "WARN" 'Skipping post-upgrade regression tests (--SkipTests)'
} else {
    Log "INFO" "Running regression tests against NEW production..."

    if ($DryRun) {
        Log "INFO" "[DRY RUN] Would run: python -m pytest tests/regression/ -x -q --prod-url=$PROD_URL"
    } else {
        Push-Location $PROJECT_ROOT
        $env:PROD_URL = $PROD_URL
        $testResult = python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short 2>&1
        $testExitCode = $LASTEXITCODE
        Pop-Location

        $testResult | ForEach-Object { Log "INFO" "  $_" }

        if ($testExitCode -ne 0) {
            Abort "Post-upgrade regression tests FAILED. Rollback to previous image immediately." $rollbackImage
        }
        Log "PASS" "Post-upgrade regression tests passed — new version is healthy"
    }
}

Log "PASS" "Phase 6 complete"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: Finalize
# ═══════════════════════════════════════════════════════════════════════════════
Log "PHASE" "═══ PHASE 7: Finalize ═══"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would deactivate old revisions and finalize"
} else {
    # Deactivate old revisions (in Single mode Azure should handle this, but be explicit)
    $allRevisions = az containerapp revision list `
        --name $CONTAINER_APP `
        --resource-group $RESOURCE_GROUP `
        --query "[?properties.active==``true``].name" -o tsv 2>&1

    $revList = $allRevisions -split "`n" | Where-Object { $_ -ne "" }
    if ($revList.Count -gt 1) {
        Log "INFO" "Deactivating $($revList.Count - 1) old revision(s)..."
        # Keep the newest (last in list), deactivate the rest
        $newest = $revList[-1]
        foreach ($rev in $revList) {
            if ($rev -ne $newest) {
                Log "INFO" "  Deactivating: $rev"
                az containerapp revision deactivate `
                    --name $CONTAINER_APP `
                    --resource-group $RESOURCE_GROUP `
                    --revision $rev 2>&1 | Out-Null
            }
        }
    }
    Log "PASS" "Old revisions deactivated"
}

# ─── Summary ──────────────────────────────────────────────────────────────────
Log "PHASE" ""
Log "PHASE" "╔══════════════════════════════════════════════════════════════╗"
Log "PHASE" "║  UPGRADE COMPLETE                                           ║"
Log "PHASE" "╠══════════════════════════════════════════════════════════════╣"
Log "PHASE" "║  Version:    $Version"
Log "PHASE" "║  Image:      $newImage"
Log "PHASE" "║  Previous:   $rollbackImage"
Log "PHASE" "║  Log:        $LOG_FILE"
Log "PHASE" "╚══════════════════════════════════════════════════════════════╝"
Log "PHASE" ""

if ($DryRun) {
    Log "WARN" "This was a DRY RUN — no changes were made to production."
}
