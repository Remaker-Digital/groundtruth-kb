# Agent Red - AGNTCY Production Azure Verification Script
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Usage:
#   .\scripts\verify-agntcy-production.ps1
#   .\scripts\verify-agntcy-production.ps1 -RunEvaluation    # Also run the evaluation framework

param(
    [string]$ResourceGroup = "agntcy-prod-rg",
    [string]$KeyVaultName = "kv-agntcy-cs-prod-rc6vcp",
    [string]$AgntcyPath = "E:\Claude-Playground\AGNTCY-upstream",
    [switch]$RunEvaluation
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AGNTCY Production Azure Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Azure CLI authentication
Write-Host "[1/7] Verifying Azure CLI authentication..." -ForegroundColor Yellow
$account = az account show --query "{name:name, id:id, state:state}" --output json 2>&1 | ConvertFrom-Json
if ($account.state -eq "Enabled") {
    Write-Host "  PASS: Subscription '$($account.name)' ($($account.id))" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Not authenticated. Run 'az login'" -ForegroundColor Red
    exit 1
}

# Step 2: Resource group
Write-Host "`n[2/7] Verifying resource group..." -ForegroundColor Yellow
$rg = az group show --name $ResourceGroup --query "{location:location, state:properties.provisioningState}" --output json 2>&1 | ConvertFrom-Json
Write-Host "  Resource Group: $ResourceGroup ($($rg.location), $($rg.state))" -ForegroundColor Green

# Step 3: Container Registry
Write-Host "`n[3/7] Verifying Container Registry..." -ForegroundColor Yellow
$repos = az acr repository list --name acragntcycsprodrc6vcp --output json 2>&1 | ConvertFrom-Json
Write-Host "  ACR repositories: $($repos.Count)" -ForegroundColor Green
foreach ($repo in $repos) {
    Write-Host "    - $repo"
}

# Step 4: Container Instances
Write-Host "`n[4/7] Verifying Container Instances..." -ForegroundColor Yellow
$containers = az container list --resource-group $ResourceGroup --query "[].{name:name, ip:ipAddress.ip}" --output json 2>&1 | ConvertFrom-Json
Write-Host "  Container groups: $($containers.Count)" -ForegroundColor Green
foreach ($c in $containers) {
    Write-Host "    - $($c.name) ($($c.ip))"
}

# Step 5: Key Vault
Write-Host "`n[5/7] Verifying Key Vault..." -ForegroundColor Yellow
$secrets = az keyvault secret list --vault-name $KeyVaultName --query "[].name" --output json 2>&1 | ConvertFrom-Json
Write-Host "  Secrets: $($secrets.Count)" -ForegroundColor Green
foreach ($s in $secrets) {
    Write-Host "    - $s"
}

# Step 6: Application Gateway
Write-Host "`n[6/7] Verifying Application Gateway..." -ForegroundColor Yellow
$appgw = az network application-gateway show --resource-group $ResourceGroup --name agntcy-cs-prod-appgw --query "{state:operationalState, sku:sku.name}" --output json 2>&1 | ConvertFrom-Json
Write-Host "  State: $($appgw.state), SKU: $($appgw.sku)" -ForegroundColor Green

# Step 7: Azure OpenAI
Write-Host "`n[7/7] Verifying Azure OpenAI..." -ForegroundColor Yellow
$deployments = az cognitiveservices account deployment list --name myOAIResource3aa68d --resource-group myAOAIResourceGroup3aa68d --query "[].{name:name, model:properties.model.name}" --output json 2>&1 | ConvertFrom-Json
Write-Host "  Deployments: $($deployments.Count)" -ForegroundColor Green
foreach ($d in $deployments) {
    Write-Host "    - $($d.name) ($($d.model))"
}

# Optional: Run evaluation framework
if ($RunEvaluation) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Running Evaluation Framework" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan

    if (-not (Test-Path "$AgntcyPath\.venv")) {
        Write-Host "  ERROR: AGNTCY venv not found. Run verify-agntcy-local.ps1 first." -ForegroundColor Red
        exit 1
    }

    # Retrieve API key from Key Vault
    $apiKey = az keyvault secret show --vault-name $KeyVaultName --name azure-openai-api-key --query "value" --output tsv 2>&1

    # Create .env.phase3.5
    @"
AZURE_OPENAI_ENDPOINT=https://remaker.openai.azure.com/
AZURE_OPENAI_API_KEY=$apiKey
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_GPT4O_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
"@ | Set-Content -Path "$AgntcyPath\.env.phase3.5" -NoNewline

    Push-Location $AgntcyPath
    & .\.venv\Scripts\python.exe -c @"
import os
for key in ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_API_VERSION']:
    os.environ.pop(key, None)
from evaluation.test_harness import TestHarness
harness = TestHarness.from_env()
harness.run_all()
harness.generate_all_reports()
print('Evaluation complete. Results in evaluation/results/')
"@
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
