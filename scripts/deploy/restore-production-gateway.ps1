#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Restore the production API Gateway Container App (WI-3027).

.DESCRIPTION
    The production gateway (agent-red-api-gateway) is missing from the Azure
    Container Apps inventory. This script recreates it by exporting the
    staging configuration and adapting it for production.

    Steps:
      1. Export staging container app as YAML
      2. Modify for production (name, env vars, scaling, ingress)
      3. Create the production container app
      4. Update image to the correct production tag
      5. Assign managed identity + RBAC
      6. Verify health

    PREREQUISITE: You must be logged into Azure CLI with a subscription
    that has write access to the Agent-Red resource group.

.PARAMETER ImageTag
    Image tag to deploy (default: v1.98.73 - last known production)

.PARAMETER DryRun
    Show what would be done without making changes

.NOTES
    (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
#>

param(
    [string]$ImageTag = "v1.98.73",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RESOURCE_GROUP = "Agent-Red"
$PROD_APP_NAME = "agent-red-api-gateway"
$STAGING_APP_NAME = "agent-red-staging"
$ACR_SERVER = "acragentredeastus.azurecr.io"
$SUBSCRIPTION_ID = "4dce2122-690a-4654-b531-cc647db62331"
$KEYVAULT_NAME = "kv-agentred-eastus"
$COSMOS_ACCOUNT = "cosmos-agentred-eastus"

Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "PRODUCTION API GATEWAY RESTORATION (WI-3027)" -ForegroundColor Cyan
Write-Host "  Image: $ACR_SERVER/api-gateway:$ImageTag" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

# -----------------------------------------------------------------------
# Step 1: Verify staging exists (source of truth for config)
# -----------------------------------------------------------------------
Write-Host "`n[1/7] Verifying staging container exists..." -ForegroundColor Yellow
$stagingExists = az containerapp show -n $STAGING_APP_NAME -g $RESOURCE_GROUP -o json 2>$null
if (-not $stagingExists) {
    Write-Host "ERROR: Staging container ($STAGING_APP_NAME) not found. Cannot derive production config." -ForegroundColor Red
    exit 1
}
Write-Host "  Staging container found" -ForegroundColor Green

# -----------------------------------------------------------------------
# Step 2: Verify production does NOT exist
# -----------------------------------------------------------------------
Write-Host "`n[2/7] Checking production container status..." -ForegroundColor Yellow
$ErrorActionPreference = "Continue"
$prodExists = az containerapp show -n $PROD_APP_NAME -g $RESOURCE_GROUP -o json 2>$null
$ErrorActionPreference = "Stop"
if ($prodExists) {
    Write-Host "  Production container already exists!" -ForegroundColor Yellow
    Write-Host "  Updating image to $ImageTag instead of recreating..." -ForegroundColor Yellow
    if (-not $DryRun) {
        az containerapp update `
            -n $PROD_APP_NAME `
            -g $RESOURCE_GROUP `
            --image "$ACR_SERVER/api-gateway:$ImageTag" `
            -o none
    }
    Write-Host "  Updated. Skipping to health verification." -ForegroundColor Green
    # Jump to health check
    Start-Sleep -Seconds 15
    $fqdn = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
    try {
        $h = Invoke-RestMethod -Uri "$fqdn/health" -TimeoutSec 15
        Write-Host "  /health: 200 OK (v$($h.product_version))" -ForegroundColor Green
    } catch {
        Write-Host "  /health: FAILED - container may still be starting" -ForegroundColor Red
    }
    exit 0
}
Write-Host "  Production container is MISSING (confirmed)" -ForegroundColor Red

# -----------------------------------------------------------------------
# Step 3: Verify image exists in ACR
# -----------------------------------------------------------------------
Write-Host "`n[3/7] Verifying image in ACR..." -ForegroundColor Yellow
$tags = az acr repository show-tags --name acragentredeastus --repository api-gateway -o tsv 2>&1
$tagList = $tags -split "`n" | ForEach-Object { $_.Trim() }
if ($tagList -notcontains $ImageTag) {
    Write-Host "ERROR: Image api-gateway:$ImageTag not found in ACR" -ForegroundColor Red
    exit 1
}
Write-Host "  api-gateway:$ImageTag found in ACR" -ForegroundColor Green

# -----------------------------------------------------------------------
# Step 4: Export staging YAML and adapt for production
# -----------------------------------------------------------------------
Write-Host "`n[4/7] Exporting staging config as base..." -ForegroundColor Yellow
$yamlPath = "$PSScriptRoot\production-gateway-generated.yaml"
az containerapp show -n $STAGING_APP_NAME -g $RESOURCE_GROUP -o yaml > $yamlPath
Write-Host "  Exported to $yamlPath" -ForegroundColor Green

Write-Host "  You must manually edit this YAML before creating:" -ForegroundColor Yellow
Write-Host "    - Change name: agent-red-staging -> agent-red-api-gateway" -ForegroundColor Yellow
Write-Host "    - Change ENVIRONMENT value: staging -> production" -ForegroundColor Yellow
Write-Host "    - Change COSMOS_DB_DATABASE: agentred-staging -> agentred" -ForegroundColor Yellow
Write-Host "    - Change KEY_VAULT_URL: kv-agentred-staging -> kv-agentred-eastus" -ForegroundColor Yellow
Write-Host "    - Change image tag: v1.98.75 -> $ImageTag" -ForegroundColor Yellow
Write-Host "    - Change minReplicas: 0 -> 2" -ForegroundColor Yellow
Write-Host "    - Change maxReplicas: 3 -> 8" -ForegroundColor Yellow
Write-Host "    - Update APP_CORS_ORIGINS for production domains" -ForegroundColor Yellow
Write-Host "    - Remove staging-specific vars: DISABLE_RATE_LIMITING, PRE_AUTH_RATE_LIMIT_EXEMPT_IPS" -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "`n  [DRY RUN] Would create container app from edited YAML" -ForegroundColor Cyan
    Write-Host "  [DRY RUN] Would assign managed identity + RBAC" -ForegroundColor Cyan
    exit 0
}

Write-Host "`n  Press Enter after editing the YAML, or Ctrl+C to abort..."
Read-Host

# -----------------------------------------------------------------------
# Step 5: Create the production container app
# -----------------------------------------------------------------------
Write-Host "`n[5/7] Creating production container app..." -ForegroundColor Yellow
$env:MSYS_NO_PATHCONV = 1
az containerapp create `
    -n $PROD_APP_NAME `
    -g $RESOURCE_GROUP `
    --yaml $yamlPath `
    -o json 2>&1 | Out-Null
Write-Host "  Container app created" -ForegroundColor Green

# -----------------------------------------------------------------------
# Step 6: Managed identity + RBAC
# -----------------------------------------------------------------------
Write-Host "`n[6/7] Configuring managed identity + RBAC..." -ForegroundColor Yellow

$env:MSYS_NO_PATHCONV = 1
$identity = az containerapp identity assign `
    -n $PROD_APP_NAME `
    -g $RESOURCE_GROUP `
    --system-assigned `
    -o json 2>&1 | ConvertFrom-Json

$principalId = $identity.principalId
if (-not $principalId) {
    $appJson = az containerapp show -n $PROD_APP_NAME -g $RESOURCE_GROUP -o json | ConvertFrom-Json
    $principalId = $appJson.identity.principalId
}
Write-Host "  Principal ID: $principalId"

# AcrPull
Write-Host "  Assigning AcrPull..."
az role assignment create `
    --assignee $principalId `
    --role "AcrPull" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/acragentredeastus" `
    -o none 2>$null

# Key Vault Secrets User
Write-Host "  Assigning Key Vault Secrets User..."
az role assignment create `
    --assignee $principalId `
    --role "Key Vault Secrets User" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" `
    -o none 2>$null

# Key Vault Crypto User
Write-Host "  Assigning Key Vault Crypto User..."
az role assignment create `
    --assignee $principalId `
    --role "Key Vault Crypto User" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" `
    -o none 2>$null

# Cosmos DB Built-in Data Contributor
Write-Host "  Assigning Cosmos DB Data Contributor..."
az cosmosdb sql role assignment create `
    --account-name $COSMOS_ACCOUNT `
    --resource-group $RESOURCE_GROUP `
    --role-definition-id "00000000-0000-0000-0000-000000000002" `
    --principal-id $principalId `
    --scope "/dbs/agentred" `
    -o none 2>$null

Write-Host "  RBAC assigned (30s propagation)" -ForegroundColor Green
Start-Sleep -Seconds 30

# -----------------------------------------------------------------------
# Step 7: Verify health
# -----------------------------------------------------------------------
Write-Host "`n[7/7] Verifying production health..." -ForegroundColor Yellow
$fqdn = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

$healthy = $false
for ($i = 0; $i -lt 6; $i++) {
    try {
        $h = Invoke-RestMethod -Uri "$fqdn/health" -TimeoutSec 15
        Write-Host "  /health: 200 OK (v$($h.product_version))" -ForegroundColor Green
        $healthy = $true
        break
    } catch {
        Write-Host "  /health: waiting... ($($i + 1)/6)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

if ($healthy) {
    # Verify widget.js
    try {
        $w = Invoke-WebRequest -Uri "$fqdn/widget.js" -TimeoutSec 10
        $wSize = $w.Content.Length
        $wStatus = $w.StatusCode
        Write-Host "  /widget.js: $wStatus - $wSize bytes" -ForegroundColor Green
    } catch {
        Write-Host "  /widget.js: FAILED" -ForegroundColor Red
    }
}

$separator = "=" * 70
Write-Host "`n$separator" -ForegroundColor Cyan
if ($healthy) {
    Write-Host "RESTORATION SUCCESSFUL" -ForegroundColor Green
} else {
    Write-Host "RESTORATION INCOMPLETE - container may need more time" -ForegroundColor Yellow
}
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify: curl $fqdn/health"
Write-Host "  2. Verify widget: curl $fqdn/widget.js | head -1"
Write-Host "  3. Browser test: pytest tests/e2e_live/test_widget_readiness_live.py -v"
Write-Host "  4. Update MEMORY.md with new managed identity principal_id: $principalId"
Write-Host ""
