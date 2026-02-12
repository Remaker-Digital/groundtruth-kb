# cosmos-pitr-restore.ps1 - Cosmos DB Point-in-Time Restore for Agent Red
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Usage:
#   .\cosmos-pitr-restore.ps1 -RestoreTime "2026-02-12T15:00:00Z"
#   .\cosmos-pitr-restore.ps1 -RestoreTime "2026-02-12T15:00:00Z" -Collections "team_members","preferences"
#   .\cosmos-pitr-restore.ps1 -RestoreTime "2026-02-12T15:00:00Z" -DryRun
#   .\cosmos-pitr-restore.ps1 -RestoreTime "2026-02-12T15:00:00Z" -SwapEndpoint
#   .\cosmos-pitr-restore.ps1 -CleanupAccount "cosmos-agentred-restore-20260212"
#
# This script:
#   Phase 1: Pre-flight checks (auth, account health, PITR window validation)
#   Phase 2: Capture pre-restore baseline (document counts per collection)
#   Phase 3: Initiate PITR restore to temporary Cosmos DB account
#   Phase 4: Wait for restore completion
#   Phase 5: Verify restored data (count comparison, sample queries)
#   Phase 6: (Optional) Swap API Gateway to restored account
#   Phase 7: (Optional) Cleanup temporary account
#
# IMPORTANT:
#   - Restore creates a NEW Cosmos DB account (non-destructive to production)
#   - The temporary account costs money while it exists -- clean up when done
#   - Swapping the endpoint causes a brief outage (Container App restart)
#   - Always run without -SwapEndpoint first to verify data before swapping

param(
    [Parameter(Mandatory=$false)]
    [string]$RestoreTime = "",

    [Parameter(Mandatory=$false)]
    [string[]]$Collections = @(),

    [Parameter(Mandatory=$false)]
    [switch]$SwapEndpoint,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun,

    [Parameter(Mandatory=$false)]
    [string]$CleanupAccount = "",

    [Parameter(Mandatory=$false)]
    [string]$TargetAccountName = ""
)

# ============================================================================
# Configuration
# ============================================================================
$RESOURCE_GROUP = "agentred-prod-rg"
$SOURCE_ACCOUNT = "cosmos-agentred-eastus2"
$DATABASE_NAME = "agentred"
$LOCATION = "East US 2"
$CONTAINER_APP = "agent-red-api-gateway"
$PROD_URL = "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io"
$PROJECT_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path
$SUBSCRIPTION_ID = "828eb521-88bb-4b01-ac3e-7ba779c55212"

# All 10 containers in the agentred database
$ALL_CONTAINERS = @(
    "tenants",
    "preferences",
    "team_members",
    "conversations",
    "knowledge_bases",
    "customer_profiles",
    "memory_vectors",
    "usage",
    "audit_log",
    "platform_config"
)

# Critical containers -- data loss here is unacceptable
$CRITICAL_CONTAINERS = @(
    "tenants",
    "preferences",
    "team_members",
    "conversations",
    "knowledge_bases"
)

$LOG_DIR = Join-Path $PROJECT_ROOT "logs"
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LOG_FILE = Join-Path $LOG_DIR "pitr-restore-$timestamp.log"

# ============================================================================
# Logging
# ============================================================================
function Log {
    param([string]$Level, [string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Add-Content -Path $LOG_FILE -Value $line

    switch ($Level) {
        "PHASE" { Write-Host $Message -ForegroundColor Cyan }
        "PASS"  { Write-Host "  [PASS] $Message" -ForegroundColor Green }
        "FAIL"  { Write-Host "  [FAIL] $Message" -ForegroundColor Red }
        "WARN"  { Write-Host "  [WARN] $Message" -ForegroundColor Yellow }
        "INFO"  { Write-Host "  [INFO] $Message" -ForegroundColor Gray }
        default { Write-Host "  $Message" }
    }
}

# ============================================================================
# Cleanup-only mode
# ============================================================================
if ($CleanupAccount) {
    Write-Host ""
    Write-Host "--- Cleanup: Deleting temporary restore account ---" -ForegroundColor Yellow
    Write-Host "  Account: $CleanupAccount" -ForegroundColor Gray
    Write-Host "  Resource Group: $RESOURCE_GROUP" -ForegroundColor Gray
    Write-Host ""

    $confirm = Read-Host "Type 'DELETE' to confirm deletion of $CleanupAccount"
    if ($confirm -ne "DELETE") {
        Write-Host "Aborted. Account NOT deleted." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "  Deleting account (this takes 1-5 minutes)..." -ForegroundColor Yellow
    az cosmosdb delete --name $CleanupAccount --resource-group $RESOURCE_GROUP --yes 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Account $CleanupAccount deleted." -ForegroundColor Green
    } else {
        Write-Host "  Failed to delete account. Check Azure portal." -ForegroundColor Red
    }
    exit 0
}

# ============================================================================
# Parameter validation
# ============================================================================
if (-not $RestoreTime) {
    Write-Host "ERROR: -RestoreTime is required (UTC format: 2026-02-12T15:00:00Z)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\cosmos-pitr-restore.ps1 -RestoreTime '2026-02-12T15:00:00Z'" -ForegroundColor Gray
    Write-Host "  .\cosmos-pitr-restore.ps1 -RestoreTime '2026-02-12T15:00:00Z' -Collections 'team_members','preferences'" -ForegroundColor Gray
    Write-Host "  .\cosmos-pitr-restore.ps1 -RestoreTime '2026-02-12T15:00:00Z' -DryRun" -ForegroundColor Gray
    Write-Host "  .\cosmos-pitr-restore.ps1 -CleanupAccount 'cosmos-agentred-restore-20260212'" -ForegroundColor Gray
    exit 1
}

# Validate RestoreTime format
try {
    $restoreDt = [DateTime]::Parse($RestoreTime).ToUniversalTime()
} catch {
    Write-Host "ERROR: Invalid timestamp format. Use ISO 8601 UTC: 2026-02-12T15:00:00Z" -ForegroundColor Red
    exit 1
}

# Resolve target collections
if ($Collections.Count -eq 0) {
    $targetCollections = $ALL_CONTAINERS
    $restoreScope = "FULL DATABASE (all 10 containers)"
} else {
    # Validate collection names
    foreach ($c in $Collections) {
        if ($c -notin $ALL_CONTAINERS) {
            Write-Host "ERROR: Unknown collection '$c'. Valid collections:" -ForegroundColor Red
            $ALL_CONTAINERS | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            exit 1
        }
    }
    $targetCollections = $Collections
    $restoreScope = "TARGETED ($($Collections.Count) containers: $($Collections -join ', '))"
}

# Generate target account name
$dateSuffix = Get-Date -Format "yyyyMMdd"
if (-not $TargetAccountName) {
    $TargetAccountName = "cosmos-agentred-restore-$dateSuffix"
}

# ============================================================================
# Banner
# ============================================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  COSMOS DB POINT-IN-TIME RESTORE" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  Source:      $SOURCE_ACCOUNT" -ForegroundColor Magenta
Write-Host "  Target:      $TargetAccountName" -ForegroundColor Magenta
Write-Host "  Restore to:  $RestoreTime" -ForegroundColor Magenta
Write-Host "  Scope:       $restoreScope" -ForegroundColor Magenta
Write-Host "  Swap:        $(if($SwapEndpoint){'YES -- will update API Gateway'}else{'NO -- verify only'})" -ForegroundColor $(if($SwapEndpoint){'Red'}else{'Magenta'})
Write-Host "  DryRun:      $DryRun" -ForegroundColor Magenta
Write-Host "  Log:         $LOG_FILE" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

Log "PHASE" "--- Log started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ---"
Log "INFO" "RestoreTime: $RestoreTime"
Log "INFO" "Target: $TargetAccountName"
Log "INFO" "Scope: $restoreScope"
Log "INFO" "SwapEndpoint: $SwapEndpoint"
Log "INFO" "DryRun: $DryRun"

# ============================================================================
# PHASE 1: Pre-flight checks
# ============================================================================
Log "PHASE" "--- PHASE 1: Pre-flight checks ---"

# 1a. Azure CLI auth
Log "INFO" "Checking Azure CLI authentication..."
$acctShow = az account show -o json 2>&1
if ($LASTEXITCODE -ne 0) {
    Log "FAIL" "Azure CLI not authenticated. Run: az login"
    exit 1
}
Log "PASS" "Azure CLI authenticated"

# 1b. Source account exists and is accessible
Log "INFO" "Checking source Cosmos DB account..."
$sourceInfo = az cosmosdb show --name $SOURCE_ACCOUNT --resource-group $RESOURCE_GROUP -o json 2>&1
if ($LASTEXITCODE -ne 0) {
    Log "FAIL" "Source account $SOURCE_ACCOUNT not found or not accessible"
    exit 1
}
Log "PASS" "Source account accessible"

# 1c. Check PITR window
Log "INFO" "Checking PITR restore window..."
$restorableAccounts = az cosmosdb restorable-database-account list --query "[?accountName=='$SOURCE_ACCOUNT'].oldestRestorableTime" -o tsv 2>&1
if ($restorableAccounts) {
    $oldestRestore = [DateTime]::Parse($restorableAccounts).ToUniversalTime()
    $now = [DateTime]::UtcNow

    if ($restoreDt -lt $oldestRestore) {
        Log "FAIL" "Restore time $RestoreTime is before oldest available: $($oldestRestore.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        Log "FAIL" "PITR window: $($oldestRestore.ToString('yyyy-MM-ddTHH:mm:ssZ')) to now"
        exit 1
    }
    if ($restoreDt -gt $now) {
        Log "FAIL" "Restore time $RestoreTime is in the future"
        exit 1
    }

    Log "PASS" "Restore time within PITR window (oldest: $($oldestRestore.ToString('yyyy-MM-dd')))"
} else {
    Log "WARN" "Could not determine PITR window -- proceeding (Azure will reject invalid timestamps)"
}

# 1d. Check target account does not already exist
Log "INFO" "Checking target account name availability..."
$existingTarget = az cosmosdb show --name $TargetAccountName --resource-group $RESOURCE_GROUP -o json 2>$null
if ($existingTarget) {
    Log "FAIL" "Target account $TargetAccountName already exists."
    Log "INFO" "To clean up: .\cosmos-pitr-restore.ps1 -CleanupAccount '$TargetAccountName'"
    Log "INFO" "Or specify a different name: -TargetAccountName 'cosmos-agentred-restore-custom'"
    exit 1
}
Log "PASS" "Target account name available"

# 1e. Production health (informational -- restore works even if prod is down)
Log "INFO" "Checking production API health..."
try {
    $healthResp = Invoke-WebRequest -Uri "$PROD_URL/health" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    if ($healthResp.StatusCode -eq 200) {
        Log "PASS" "Production /health 200"
    }
} catch {
    Log "WARN" "Production /health not responding -- proceeding with restore anyway"
}

Log "PASS" "Phase 1 complete -- pre-flight checks passed"

# ============================================================================
# PHASE 2: Capture pre-restore baseline
# ============================================================================
Log "PHASE" "--- PHASE 2: Capture pre-restore baseline ---"

$sourceKey = az cosmosdb keys list --name $SOURCE_ACCOUNT --resource-group $RESOURCE_GROUP --query "primaryMasterKey" -o tsv 2>&1
$sourceEndpoint = "https://${SOURCE_ACCOUNT}.documents.azure.com:443/"

$baseline = @{}
foreach ($container in $ALL_CONTAINERS) {
    Log "INFO" "Counting documents in $container..."
    if ($DryRun) {
        Log "INFO" "[DRY RUN] Would count documents in $container"
        $baseline[$container] = "[dry-run]"
    } else {
        try {
            $countQuery = "SELECT VALUE COUNT(1) FROM c"
            $countResult = az cosmosdb sql query --account-name $SOURCE_ACCOUNT --resource-group $RESOURCE_GROUP --database-name $DATABASE_NAME --container-name $container --query-text $countQuery -o json 2>&1
            $parsed = $countResult | ConvertFrom-Json
            if ($parsed -and $parsed.Count -gt 0) {
                $docCount = $parsed[0]
                $baseline[$container] = $docCount
                Log "INFO" "  $container : $docCount documents"
            } else {
                $baseline[$container] = "error"
                Log "WARN" "  $container : could not count (query returned empty)"
            }
        } catch {
            $baseline[$container] = "error"
            Log "WARN" "  $container : count failed ($($_.Exception.Message))"
        }
    }
}

Log "INFO" "Baseline captured:"
foreach ($key in $baseline.Keys | Sort-Object) {
    Log "INFO" "  $key = $($baseline[$key])"
}
Log "PASS" "Phase 2 complete -- baseline captured"

# ============================================================================
# PHASE 3: Initiate PITR restore
# ============================================================================
Log "PHASE" "--- PHASE 3: Initiate PITR restore ---"
Log "INFO" "Target account: $TargetAccountName"
Log "INFO" "Restore timestamp: $RestoreTime"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would execute:"

    if ($targetCollections.Count -lt $ALL_CONTAINERS.Count) {
        $dbRestoreArg = "--databases-to-restore name=$DATABASE_NAME collections=$($targetCollections -join ' ')"
        Log "INFO" "  az cosmosdb restore -a $SOURCE_ACCOUNT -g $RESOURCE_GROUP -n $TargetAccountName -t $RestoreTime -l '$LOCATION' $dbRestoreArg"
    } else {
        Log "INFO" "  az cosmosdb restore -a $SOURCE_ACCOUNT -g $RESOURCE_GROUP -n $TargetAccountName -t $RestoreTime -l '$LOCATION'"
    }
    Log "PASS" "Phase 3 complete -- [DRY RUN] restore command prepared"
} else {
    Log "INFO" "Initiating restore (this takes 5-30 minutes)..."
    Log "WARN" "Do NOT cancel this process. The restore account will be created regardless."

    $restoreArgs = @(
        "cosmosdb", "restore",
        "--account-name", $SOURCE_ACCOUNT,
        "--resource-group", $RESOURCE_GROUP,
        "--target-database-account-name", $TargetAccountName,
        "--restore-timestamp", $RestoreTime,
        "--location", $LOCATION
    )

    # Targeted collection restore
    if ($targetCollections.Count -lt $ALL_CONTAINERS.Count) {
        $restoreArgs += "--databases-to-restore"
        $restoreArgs += "name=$DATABASE_NAME"
        $collectionsStr = $targetCollections -join " "
        $restoreArgs += "collections=$collectionsStr"
        Log "INFO" "Targeted restore: $DATABASE_NAME / $($targetCollections -join ', ')"
    } else {
        Log "INFO" "Full database restore: all 10 containers"
    }

    $startTime = Get-Date
    az @restoreArgs 2>&1 | ForEach-Object { Log "INFO" $_ }
    $restoreExitCode = $LASTEXITCODE
    $duration = (Get-Date) - $startTime

    if ($restoreExitCode -ne 0) {
        Log "FAIL" "PITR restore command failed (exit code: $restoreExitCode)"
        Log "FAIL" "Check Azure portal: https://portal.azure.com/#resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts"
        Log "INFO" "Common causes:"
        Log "INFO" "  - Timestamp outside PITR window"
        Log "INFO" "  - Target account name already taken globally"
        Log "INFO" "  - Insufficient permissions"
        exit 1
    }

    Log "PASS" "Restore initiated successfully (took $([math]::Round($duration.TotalMinutes, 1)) minutes)"
    Log "PASS" "Phase 3 complete -- restore account created"
}

# ============================================================================
# PHASE 4: Wait for restore completion and verify account
# ============================================================================
Log "PHASE" "--- PHASE 4: Verify restore account ---"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would verify restored account $TargetAccountName is online"
    Log "PASS" "Phase 4 complete -- [DRY RUN]"
} else {
    Log "INFO" "Verifying restored account is accessible..."

    $retries = 0
    $maxRetries = 12
    $accountReady = $false
    while ($retries -lt $maxRetries) {
        $targetInfo = az cosmosdb show --name $TargetAccountName --resource-group $RESOURCE_GROUP --query "provisioningState" -o tsv 2>&1
        if ($targetInfo -eq "Succeeded") {
            $accountReady = $true
            break
        }
        $retries++
        Log "INFO" "Account provisioning state: $targetInfo (attempt $retries/$maxRetries, waiting 30s...)"
        Start-Sleep -Seconds 30
    }

    if (-not $accountReady) {
        Log "FAIL" "Restored account not ready after $([math]::Round($maxRetries * 30 / 60, 0)) minutes"
        Log "INFO" "Check Azure portal. Account may still be provisioning."
        Log "INFO" "Cleanup: .\cosmos-pitr-restore.ps1 -CleanupAccount '$TargetAccountName'"
        exit 1
    }

    Log "PASS" "Restored account provisioned successfully"

    # Get restored account endpoint and key
    $targetEndpoint = "https://${TargetAccountName}.documents.azure.com:443/"
    $targetKey = az cosmosdb keys list --name $TargetAccountName --resource-group $RESOURCE_GROUP --query "primaryMasterKey" -o tsv 2>&1
    if ($LASTEXITCODE -ne 0) {
        Log "FAIL" "Could not retrieve keys for restored account"
        exit 1
    }
    Log "PASS" "Restored account keys retrieved"
    Log "INFO" "Restored endpoint: $targetEndpoint"

    Log "PASS" "Phase 4 complete -- restore account verified"
}

# ============================================================================
# PHASE 5: Data verification
# ============================================================================
Log "PHASE" "--- PHASE 5: Data verification ---"

if ($DryRun) {
    Log "INFO" "[DRY RUN] Would compare document counts: source vs restored"
    Log "PASS" "Phase 5 complete -- [DRY RUN]"
} else {
    $restoredCounts = @{}
    $mismatches = @()

    foreach ($container in $targetCollections) {
        Log "INFO" "Counting restored documents in $container..."
        try {
            $countQuery = "SELECT VALUE COUNT(1) FROM c"
            $countResult = az cosmosdb sql query --account-name $TargetAccountName --resource-group $RESOURCE_GROUP --database-name $DATABASE_NAME --container-name $container --query-text $countQuery -o json 2>&1
            $parsed = $countResult | ConvertFrom-Json
            if ($parsed -and $parsed.Count -gt 0) {
                $restoredCount = $parsed[0]
                $restoredCounts[$container] = $restoredCount
            } else {
                $restoredCounts[$container] = "error"
            }
        } catch {
            $restoredCounts[$container] = "error"
            Log "WARN" "  $container : count failed"
        }
    }

    # Compare
    Log "INFO" ""
    Log "INFO" "=== Document Count Comparison ==="
    Log "INFO" "Container            | Source (now)  | Restored ($RestoreTime)"
    Log "INFO" "---------------------|--------------|------------------------"

    foreach ($container in $targetCollections | Sort-Object) {
        $src = $baseline[$container]
        $rst = $restoredCounts[$container]

        $status = ""
        if ($src -is [int] -and $rst -is [int]) {
            $diff = $src - $rst
            if ($diff -eq 0) {
                $status = "MATCH"
            } elseif ($diff -gt 0) {
                $status = "+$diff since restore point"
            } else {
                $status = "$diff FEWER NOW (possible data loss)"
                $mismatches += $container
            }
        } else {
            $status = "(could not compare)"
        }

        $srcStr = "$src".PadLeft(12)
        $rstStr = "$rst".PadLeft(12)
        Log "INFO" "  $($container.PadRight(20)) | $srcStr | $rstStr | $status"
    }
    Log "INFO" ""

    # Check critical containers
    $criticalLoss = $mismatches | Where-Object { $_ -in $CRITICAL_CONTAINERS }
    if ($criticalLoss.Count -gt 0) {
        Log "FAIL" "CRITICAL DATA LOSS DETECTED in: $($criticalLoss -join ', ')"
        Log "FAIL" "Current production has FEWER documents than the restore point."
        Log "FAIL" "The restored account contains the correct data."
        Log "INFO" ""
        Log "INFO" "RECOMMENDED ACTIONS:"
        Log "INFO" "  1. Keep the restored account ($TargetAccountName) as your recovery source"
        Log "INFO" "  2. If swapping: re-run with -SwapEndpoint to point API Gateway at restored data"
        Log "INFO" "  3. Or: manually copy missing documents from restored to production"
    } elseif ($mismatches.Count -gt 0) {
        Log "WARN" "Non-critical collections have fewer documents now: $($mismatches -join ', ')"
        Log "INFO" "This may indicate data loss in non-critical collections (audit, usage)."
    } else {
        Log "PASS" "All restored collections have equal or fewer documents than current (expected)"
        Log "INFO" "Current counts >= restored counts means no data loss since restore point."
    }

    Log "PASS" "Phase 5 complete -- data verification done"
}

# ============================================================================
# PHASE 6: (Optional) Swap API Gateway endpoint
# ============================================================================
Log "PHASE" "--- PHASE 6: Endpoint swap ---"

if (-not $SwapEndpoint) {
    Log "INFO" "Swap not requested (-SwapEndpoint not set)"
    Log "INFO" "To swap API Gateway to restored data, re-run with -SwapEndpoint"
    Log "INFO" ""
    Log "INFO" "Manual swap command:"
    Log "INFO" "  az containerapp update --name $CONTAINER_APP --resource-group $RESOURCE_GROUP \"
    Log "INFO" "    --set-env-vars 'COSMOS_DB_ENDPOINT=https://${TargetAccountName}.documents.azure.com:443/'"
    Log "PASS" "Phase 6 complete -- no swap"
} elseif ($DryRun) {
    Log "INFO" "[DRY RUN] Would update API Gateway COSMOS_DB_ENDPOINT to:"
    Log "INFO" "  https://${TargetAccountName}.documents.azure.com:443/"
    Log "PASS" "Phase 6 complete -- [DRY RUN]"
} else {
    Log "WARN" "SWAPPING API GATEWAY TO RESTORED ACCOUNT"
    Log "WARN" "This will cause a brief outage (container restart, 30-90s)"
    Log "INFO" ""

    # Capture current endpoint for rollback
    $currentEndpoint = az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].env[?name=='COSMOS_DB_ENDPOINT'].value | [0]" -o tsv 2>&1
    Log "INFO" "Current endpoint: $currentEndpoint"
    Log "INFO" "New endpoint:     https://${TargetAccountName}.documents.azure.com:443/"
    Log "INFO" ""
    Log "INFO" "ROLLBACK COMMAND (save this):"
    Log "INFO" "  az containerapp update --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --set-env-vars 'COSMOS_DB_ENDPOINT=$currentEndpoint'"

    # Get restored account key
    $targetKey = az cosmosdb keys list --name $TargetAccountName --resource-group $RESOURCE_GROUP --query "primaryMasterKey" -o tsv 2>&1

    # Update both endpoint and key
    az containerapp update `
        --name $CONTAINER_APP `
        --resource-group $RESOURCE_GROUP `
        --set-env-vars "COSMOS_DB_ENDPOINT=https://${TargetAccountName}.documents.azure.com:443/" "COSMOS_DB_KEY=$targetKey" 2>&1 | ForEach-Object { Log "INFO" $_ }

    if ($LASTEXITCODE -ne 0) {
        Log "FAIL" "Endpoint swap failed. API Gateway may be in inconsistent state."
        Log "FAIL" "ROLLBACK: az containerapp update --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --set-env-vars 'COSMOS_DB_ENDPOINT=$currentEndpoint'"
        exit 1
    }

    # Wait for health
    Log "INFO" "Waiting for API Gateway health (90s timeout)..."
    $elapsed = 0
    $healthy = $false
    while ($elapsed -lt 90) {
        Start-Sleep -Seconds 5
        $elapsed += 5
        try {
            $r = Invoke-WebRequest -Uri "$PROD_URL/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($r.StatusCode -eq 200) {
                Log "PASS" "/health 200 OK after ${elapsed}s"
                $healthy = $true
                break
            }
        } catch {
            Log "INFO" "Waiting... (${elapsed}s)"
        }
    }

    if (-not $healthy) {
        Log "WARN" "/health not responding after 90s -- NATS lazy init may need more time"
        Log "INFO" "Check: curl $PROD_URL/health"
    }

    Log "PASS" "Phase 6 complete -- endpoint swapped"
}

# ============================================================================
# PHASE 7: Summary
# ============================================================================
Log "PHASE" "--- PHASE 7: Summary ---"
Log "PHASE" ""

if ($DryRun) {
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "  DRY RUN COMPLETE -- no changes made" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
} else {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  PITR RESTORE COMPLETE" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  Source:       $SOURCE_ACCOUNT" -ForegroundColor Green
    Write-Host "  Restored to:  $TargetAccountName" -ForegroundColor Green
    Write-Host "  Timestamp:    $RestoreTime" -ForegroundColor Green
    Write-Host "  Endpoint:     https://${TargetAccountName}.documents.azure.com:443/" -ForegroundColor Green
    if ($SwapEndpoint) {
        Write-Host "  API Gateway:  SWAPPED to restored account" -ForegroundColor Yellow
    } else {
        Write-Host "  API Gateway:  NOT swapped (verify data first)" -ForegroundColor Green
    }
    Write-Host "  Log:          $LOG_FILE" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  NEXT STEPS:" -ForegroundColor Yellow
    if (-not $SwapEndpoint) {
        Write-Host "    1. Review the count comparison above" -ForegroundColor Gray
        Write-Host "    2. If data looks correct, swap: .\cosmos-pitr-restore.ps1 -RestoreTime '$RestoreTime' -SwapEndpoint -TargetAccountName '$TargetAccountName'" -ForegroundColor Gray
        Write-Host "    3. Or copy specific documents manually using the restored endpoint" -ForegroundColor Gray
    } else {
        Write-Host "    1. Verify production is healthy: curl $PROD_URL/health" -ForegroundColor Gray
        Write-Host "    2. Run data integrity audit (see memory/data-integrity-audit.md)" -ForegroundColor Gray
        Write-Host "    3. Run Tier 0 regression: python -m pytest tests/regression/ -x -q -m tier0" -ForegroundColor Gray
    }
    Write-Host "    - Cleanup temp account: .\cosmos-pitr-restore.ps1 -CleanupAccount '$TargetAccountName'" -ForegroundColor Gray
    Write-Host "    - IMPORTANT: Temp account costs money while it exists" -ForegroundColor Yellow
    Write-Host ""
}

Log "INFO" "Script completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
