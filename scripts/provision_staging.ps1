# Agent Red Customer Experience — Staging Environment Provisioning
#
# Creates the staging Azure resource group and core resources:
#   1. Resource Group: agentred-staging-rg
#   2. Cosmos DB: cosmos-agentred-staging (Serverless, EnableNoSQLVectorSearch)
#   3. Key Vault: kv-agentred-staging (RBAC-enabled)
#   4. Container App Environment: agent-red-staging-cae
#   5. NATS Container App: agent-red-staging-nats
#   6. API Gateway Container App: agent-red-staging-gateway
#
# Estimated cost: ~$30-50/month
#
# Prerequisites:
#   - az CLI logged in (az login)
#   - Subscription: 828eb521-88bb-4b01-ac3e-7ba779c55212
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/provision_staging.ps1
#
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

$ErrorActionPreference = "Stop"

$SUBSCRIPTION = "828eb521-88bb-4b01-ac3e-7ba779c55212"
$RG = "agentred-staging-rg"
$LOCATION = "eastus2"

Write-Host "=== Agent Red Staging Environment Provisioning ===" -ForegroundColor Cyan

# 1. Resource Group
Write-Host "`n[1/6] Creating resource group: $RG" -ForegroundColor Yellow
az group create --name $RG --location $LOCATION --subscription $SUBSCRIPTION --output table

# 2. Cosmos DB (Serverless + Vector Search)
Write-Host "`n[2/6] Creating Cosmos DB: cosmos-agentred-staging" -ForegroundColor Yellow
az cosmosdb create `
  --name cosmos-agentred-staging `
  --resource-group $RG `
  --kind GlobalDocumentDB `
  --capabilities EnableServerless EnableNoSQLVectorSearch `
  --default-consistency-level Session `
  --locations regionName=eastus2 failoverPriority=0 `
  --backup-policy-type Continuous `
  --continuous-tier Continuous30Days `
  --subscription $SUBSCRIPTION `
  --output table

# Create database
az cosmosdb sql database create `
  --account-name cosmos-agentred-staging `
  --resource-group $RG `
  --name agentred-staging `
  --subscription $SUBSCRIPTION `
  --output table

# 3. Key Vault (RBAC-enabled)
Write-Host "`n[3/6] Creating Key Vault: kv-agentred-staging" -ForegroundColor Yellow
az keyvault create `
  --name kv-agentred-staging `
  --resource-group $RG `
  --location $LOCATION `
  --enable-rbac-authorization true `
  --sku standard `
  --subscription $SUBSCRIPTION `
  --output table

# Assign Key Vault Secrets Officer to current user
$CURRENT_USER = az ad signed-in-user show --query id -o tsv
$env:MSYS_NO_PATHCONV = 1
az role assignment create `
  --role "Key Vault Secrets Officer" `
  --assignee $CURRENT_USER `
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/kv-agentred-staging" `
  --output table

# 4. Container App Environment
Write-Host "`n[4/6] Creating Container App Environment: agent-red-staging-cae" -ForegroundColor Yellow
az containerapp env create `
  --name agent-red-staging-cae `
  --resource-group $RG `
  --location $LOCATION `
  --subscription $SUBSCRIPTION `
  --output table

# 5. NATS Container App
Write-Host "`n[5/6] Creating NATS Container App" -ForegroundColor Yellow
$NATS_BOOTSTRAP = @'
cat > /tmp/nats.conf <<'EOF'
jetstream {
  store_dir: "/tmp/nats/jetstream"
}
http: 8222
websocket {
  port: 8080
  no_tls: true
}
EOF
exec nats-server -c /tmp/nats.conf
'@
az containerapp create `
  --name agent-red-staging-nats `
  --resource-group $RG `
  --environment agent-red-staging-cae `
  --image nats:2.10-alpine `
  --min-replicas 1 --max-replicas 1 `
  --target-port 8080 `
  --ingress internal `
  --transport auto `
  --command /bin/sh `
  --args -c $NATS_BOOTSTRAP `
  --subscription $SUBSCRIPTION `
  --output table

# 6. API Gateway Container App
Write-Host "`n[6/6] Creating API Gateway Container App" -ForegroundColor Yellow

az containerapp create `
  --name agent-red-staging-gateway `
  --resource-group $RG `
  --environment agent-red-staging-cae `
  --image acragentredeastus2.azurecr.io/api-gateway:v1.0.0 `
  --registry-server acragentredeastus2.azurecr.io `
  --min-replicas 1 --max-replicas 2 `
  --target-port 8000 `
  --ingress external `
  --env-vars `
    ENVIRONMENT=staging `
    AZURE_OPENAI_ENDPOINT=https://aoai-agentred-eastus2.openai.azure.com/ `
    COSMOS_DB_ENDPOINT=https://cosmos-agentred-staging.documents.azure.com:443/ `
    COSMOS_DB_DATABASE=agentred-staging `
    KEY_VAULT_URL=https://kv-agentred-staging.vault.azure.net/ `
    AZURE_KEYVAULT_URL=https://kv-agentred-staging.vault.azure.net/ `
    USE_AZURE_OPENAI=true `
    USE_REAL_APIS=true `
    USE_AGENT_CONTAINERS=false `
    NATS_URL=ws://agent-red-staging-nats `
    GRACEFUL_SHUTDOWN_TIMEOUT=60 `
    MASTER_KEK_KEY_ID=https://kv-agentred-staging.vault.azure.net/keys/agent-red-cmk `
  --subscription $SUBSCRIPTION `
  --output table

# RBAC for API Gateway managed identity
Write-Host "`n=== Assigning RBAC roles ===" -ForegroundColor Yellow

$GATEWAY_ID = az containerapp show `
  --name agent-red-staging-gateway `
  --resource-group $RG `
  --query "identity.principalId" -o tsv

# AcrPull
az role assignment create `
  --role AcrPull `
  --assignee $GATEWAY_ID `
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/agentred-prod-rg/providers/Microsoft.ContainerRegistry/registries/acragentredeastus2" `
  --output table

# Key Vault Secrets User (least privilege — read-only secret access)
az role assignment create `
  --role "Key Vault Secrets User" `
  --assignee $GATEWAY_ID `
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/kv-agentred-staging" `
  --output table

# Key Vault Crypto User (wrap/unwrap DEKs via Master KEK — SPEC-1843 / WI-1625)
az role assignment create `
  --role "Key Vault Crypto User" `
  --assignee $GATEWAY_ID `
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/kv-agentred-staging" `
  --output table

# Cosmos DB Built-in Data Contributor
az role assignment create `
  --role "00000000-0000-0000-0000-000000000002" `
  --assignee $GATEWAY_ID `
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-agentred-staging" `
  --output table

Write-Host "`n=== Staging environment provisioned ===" -ForegroundColor Green
Write-Host "API Gateway URL: check 'az containerapp show --name agent-red-staging-gateway -g $RG --query properties.configuration.ingress.fqdn'"
Write-Host "Wait 60-90s for NATS startup, then verify: curl <gateway-url>/health"
