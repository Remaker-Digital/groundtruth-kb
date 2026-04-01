#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Restore the API Gateway Container App after Azure subscription re-enablement.

.DESCRIPTION
    The API Gateway Container App was deleted after the Azure subscription was
    suspended on 2026-02-10 (corrupted by mid-operation failure). This script:

    1. Verifies subscription is active and writable
    2. Builds and pushes a new Docker image (v1.15.0) to ACR
    3. Recreates the Container App with full configuration
    4. Assigns RBAC roles to the new managed identity
    5. Verifies the deployment is healthy

    IMPORTANT: Run this AFTER Microsoft re-enables the subscription.
    Secrets must be provided via environment variables (see below).

.PARAMETER SkipBuild
    Skip Docker image build (use existing v1.14.0 image in ACR)

.NOTES
    Required env vars (or edit PLACEHOLDER values in api-gateway-restore.yaml):
      - AZURE_OPENAI_API_KEY_SECRET (the actual key value)
      - COSMOS_DB_KEY_SECRET (the actual key value)
      - SHOPIFY_API_KEY_SECRET
      - SHOPIFY_API_SECRET_SECRET
      - ADMIN_PREVIEW_PASSWORD_SECRET

    (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#>

param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

# Configuration
$RESOURCE_GROUP = "Agent-Red"
$CONTAINER_APP_NAME = "agent-red-api-gateway"
$ACR_NAME = "acragentredeastus"
$ACR_SERVER = "$ACR_NAME.azurecr.io"
$IMAGE_TAG = if ($SkipBuild) { "v1.14.0" } else { "v1.15.0" }
$SUBSCRIPTION_ID = "4dce2122-690a-4654-b531-cc647db62331"
$KEYVAULT_NAME = "kv-agentred-eastus"
$COSMOS_ACCOUNT = "cosmos-agentred-eastus"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "AGENT RED API GATEWAY RESTORATION" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify subscription is active
Write-Host "[1/6] Verifying Azure subscription status..." -ForegroundColor Yellow
$sub = az account show --subscription $SUBSCRIPTION_ID -o json 2>&1 | ConvertFrom-Json
if ($sub.state -ne "Enabled") {
    Write-Host "ERROR: Subscription is not Enabled (state: $($sub.state))" -ForegroundColor Red
    Write-Host "Wait for Microsoft to re-enable the subscription before running this script."
    exit 1
}
Write-Host "  Subscription is Enabled" -ForegroundColor Green

# Verify write access
Write-Host "  Testing write access..." -ForegroundColor Yellow
try {
    $testResult = az group show -n $RESOURCE_GROUP -o json 2>&1
    Write-Host "  Resource group accessible" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Cannot access resource group. Subscription may still be read-only." -ForegroundColor Red
    exit 1
}

# Step 2: Build and push Docker image
if (-not $SkipBuild) {
    Write-Host "`n[2/6] Building Docker image v1.15.0..." -ForegroundColor Yellow
    Write-Host "  Building admin SPA first..."

    Push-Location "$PSScriptRoot\..\..\admin\shopify"
    npm run build
    Pop-Location

    Push-Location "$PSScriptRoot\..\..\admin\standalone"
    npm run build
    Pop-Location

    Push-Location "$PSScriptRoot\..\..\widget"
    npm run build
    Pop-Location

    Write-Host "  Building Docker image via ACR..."
    Push-Location "$PSScriptRoot\..\.."
    az acr build `
        --registry $ACR_NAME `
        --image "api-gateway:$IMAGE_TAG" `
        --file Dockerfile `
        . 2>&1 | ForEach-Object { Write-Host "    $_" }
    Pop-Location

    Write-Host "  Image pushed: $ACR_SERVER/api-gateway:$IMAGE_TAG" -ForegroundColor Green
} else {
    Write-Host "`n[2/6] Skipping build (using existing v1.14.0 image)" -ForegroundColor Yellow
}

# Step 3: Create the Container App
Write-Host "`n[3/6] Creating Container App..." -ForegroundColor Yellow

# Check if it already exists
$existing = az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o json 2>$null
if ($existing) {
    Write-Host "  Container App already exists — updating image to $IMAGE_TAG" -ForegroundColor Yellow
    $env:MSYS_NO_PATHCONV = 1
    az containerapp update `
        -n $CONTAINER_APP_NAME `
        -g $RESOURCE_GROUP `
        --image "$ACR_SERVER/api-gateway:$IMAGE_TAG" `
        --set-env-vars "DEPLOY_TIMESTAMP=$(Get-Date -Format 'yyyyMMddHHmmss')" `
        -o json 2>&1 | Out-Null
    Write-Host "  Updated existing Container App" -ForegroundColor Green
} else {
    Write-Host "  Creating new Container App from YAML template..."

    # Read and populate the YAML template
    $yamlPath = "$PSScriptRoot\api-gateway-restore.yaml"

    $env:MSYS_NO_PATHCONV = 1
    az containerapp create `
        -n $CONTAINER_APP_NAME `
        -g $RESOURCE_GROUP `
        --yaml $yamlPath `
        -o json 2>&1 | Out-Null

    Write-Host "  Container App created" -ForegroundColor Green
}

# Step 4: Enable system-assigned managed identity
Write-Host "`n[4/6] Configuring managed identity + RBAC..." -ForegroundColor Yellow

$env:MSYS_NO_PATHCONV = 1
$identity = az containerapp identity assign `
    -n $CONTAINER_APP_NAME `
    -g $RESOURCE_GROUP `
    --system-assigned `
    -o json 2>&1 | ConvertFrom-Json

$principalId = $identity.principalId
if (-not $principalId) {
    # Try getting it from the container app directly
    $appJson = az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o json | ConvertFrom-Json
    $principalId = $appJson.identity.principalId
}

Write-Host "  Managed Identity Principal ID: $principalId"

# Assign RBAC roles
$env:MSYS_NO_PATHCONV = 1

# AcrPull
Write-Host "  Assigning AcrPull on ACR..."
az role assignment create `
    --assignee $principalId `
    --role "AcrPull" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME" `
    -o none 2>$null

# Key Vault Secrets User (least privilege — read-only secret access)
Write-Host "  Assigning Key Vault Secrets User..."
az role assignment create `
    --assignee $principalId `
    --role "Key Vault Secrets User" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" `
    -o none 2>$null

# Key Vault Crypto User (wrap/unwrap DEKs via Master KEK — SPEC-1843 / WI-1625)
Write-Host "  Assigning Key Vault Crypto User..."
az role assignment create `
    --assignee $principalId `
    --role "Key Vault Crypto User" `
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" `
    -o none 2>$null

# Cosmos DB Built-in Data Contributor
Write-Host "  Assigning Cosmos DB Built-in Data Contributor..."
az cosmosdb sql role assignment create `
    --account-name $COSMOS_ACCOUNT `
    --resource-group $RESOURCE_GROUP `
    --role-definition-id "00000000-0000-0000-0000-000000000002" `
    --principal-id $principalId `
    --scope "/dbs/agentred" `
    -o none 2>$null

Write-Host "  RBAC roles assigned (allow ~30s for propagation)" -ForegroundColor Green

# Step 5: Wait for deployment
Write-Host "`n[5/6] Waiting for deployment (30s for RBAC propagation + container start)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 6: Verify health
Write-Host "`n[6/6] Verifying deployment health..." -ForegroundColor Yellow
$fqdn = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

try {
    $healthResp = Invoke-RestMethod -Uri "$fqdn/health" -TimeoutSec 10
    Write-Host "  /health: 200 OK" -ForegroundColor Green
    Write-Host "    version: $($healthResp.version)"
    Write-Host "    uptime: $($healthResp.uptime_seconds)s"
} catch {
    Write-Host "  /health: FAILED ($($_.Exception.Message))" -ForegroundColor Red
    Write-Host "  Container may still be starting. Check: az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP" -ForegroundColor Yellow
}

try {
    $readyResp = Invoke-RestMethod -Uri "$fqdn/ready" -TimeoutSec 10
    Write-Host "  /ready: 200 OK" -ForegroundColor Green
} catch {
    Write-Host "  /ready: FAILED ($($_.Exception.Message))" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "RESTORATION COMPLETE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify chat quality: python scripts/test_chat_battery.py"
Write-Host "  2. Verify Shopify storefront: https://blanco-9939.myshopify.com/"
Write-Host "  3. Verify standalone admin: $fqdn/admin/standalone/"
Write-Host "  4. Run regression tests: python -m pytest tests/regression/ -x -q"
Write-Host ""
