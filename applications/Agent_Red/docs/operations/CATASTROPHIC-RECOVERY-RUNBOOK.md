# Agent Red — Catastrophic Recovery Runbook
#
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-13
# Last corrected: 2026-02-19 — Added AZURE_KEYVAULT_URL and NATS_URL to env-vars (discovered S62)

> Full-environment rebuild from scratch when the Azure subscription or infrastructure is
> completely lost. Based on the actual recovery performed on 2026-02-13 (session 15)
> after Microsoft terminated the production subscription.

**Last tested:** 2026-02-13 (full production rebuild — successful)
**Estimated time:** 2–3 hours (including Cosmos DB capability propagation delays)
**Prerequisite:** Access to the Agent Red source repository with all scripts intact

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## Table of Contents

1. [Impact Assessment](#1-impact-assessment)
2. [Prerequisites](#2-prerequisites)
3. [Phase 1: Azure Subscription & Resource Group](#3-phase-1-azure-subscription--resource-group)
4. [Phase 2: Core Azure Resources](#4-phase-2-core-azure-resources)
5. [Phase 3: Container App Environment & API Gateway](#5-phase-3-container-app-environment--api-gateway)
6. [Phase 4: ACR Build & Deploy](#6-phase-4-acr-build--deploy)
7. [Phase 5: Cosmos DB Seeding](#7-phase-5-cosmos-db-seeding)
8. [Phase 6: Verification](#8-phase-6-verification)
9. [Phase 7: Customer Key Rotation](#9-phase-7-customer-key-rotation)
10. [Key Invalidation Impact](#10-key-invalidation-impact)
11. [Resource Reference](#11-resource-reference)
12. [Lessons Learned](#12-lessons-learned)

---

## 1. Impact Assessment

### What is lost in a catastrophic failure

| Resource | Lost? | Recovery method |
|----------|-------|-----------------|
| Source code | No | Git repository (GitHub) |
| Docker images | Yes | Rebuilt from source via ACR |
| Cosmos DB data | Yes | Re-seeded from `scripts/seed_tenant.py` |
| Azure OpenAI models | Yes | Re-deployed (same model names, new keys) |
| Key Vault secrets | Yes | Re-created from new resource keys |
| Container App | Yes | Re-created with full env var config |
| ACR registry | Yes | Re-created, images rebuilt |
| Managed Identity | Yes | New identity, new RBAC assignments |
| **Customer API keys** | **YES** | **NEW keys generated — old keys permanently invalid** |
| **Customer widget keys** | **YES** | **NEW keys generated — storefront widget breaks** |
| **User API keys** | **YES** | **NEW keys generated — admin access breaks** |
| Customer conversation history | Yes | Lost unless Cosmos PITR backup exists |
| Knowledge base articles | No | Re-seeded from `scripts/seed_knowledge_base.py` (source of truth is code) |
| Customer memory vectors | Yes | Re-seeded with demo data; real customer memories lost |

### Critical customer impact

**⚠️ ALL API KEYS AND WIDGET KEYS ARE INVALIDATED BY A FULL REBUILD.**

This means:
- **Shopify storefronts** with the embedded widget will fail to authenticate (widget returns 401)
- **Admin users** with saved API keys cannot access the admin panel
- **Any external integrations** using tenant API keys will fail

**Mitigation strategy:** See [Phase 7: Customer Key Rotation](#9-phase-7-customer-key-rotation).

---

## 2. Prerequisites

### Required tools

```
az          — Azure CLI (latest)
git         — Git client
python 3.11 — With project dependencies installed
node 20+    — For admin SPA builds
```

### Required credentials

- Azure account with Owner or Contributor role on target subscription
- GitHub access to the Agent Red repository
- `.env.local` file (or knowledge of all environment variable values)

### Required files from source repository

| File | Purpose |
|------|---------|
| `scripts/seed_tenant.py` | Unified 8-phase Cosmos DB seeder |
| `scripts/seed_knowledge_base.py` | 54 KB articles |
| `scripts/seed_demo_data.py` | Demo conversations & profiles |
| `scripts/deploy/upgrade.ps1` | Automated deploy pipeline |
| `scripts/deploy/rollback.ps1` | Emergency rollback |
| `Dockerfile` | Container image build |
| `requirements.txt` | Python dependencies |
| `admin/standalone/` | Admin SPA source (must build before Docker) |
| `admin/shopify/` | Shopify admin SPA source (must build before Docker) |

---

## 3. Phase 1: Azure Subscription & Resource Group

### 1a. Verify or create subscription

```powershell
# Check current subscription
az account show --output table

# If needed, create new subscription via Azure Portal
# Then set it as active:
az account set --subscription "<SUBSCRIPTION_ID>"
```

### 1b. Register required providers

```powershell
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DocumentDB
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.CognitiveServices

# Wait for all to complete (check status):
az provider show --namespace Microsoft.App --query registrationState
```

### 1c. Create resource group

```powershell
az group create --name Agent-Red --location eastus
```

---

## 4. Phase 2: Core Azure Resources

### 2a. Azure OpenAI

```powershell
# Create OpenAI resource
az cognitiveservices account create `
    --name Agent-Red-OpenAI `
    --resource-group Agent-Red `
    --kind OpenAI `
    --sku S0 `
    --location eastus

# Deploy models (all Standard, 30K TPM):
az cognitiveservices account deployment create `
    --name Agent-Red-OpenAI `
    --resource-group Agent-Red `
    --deployment-name gpt-4o-mini `
    --model-name gpt-4o-mini `
    --model-version "2024-07-18" `
    --model-format OpenAI `
    --sku-name Standard `
    --sku-capacity 30

az cognitiveservices account deployment create `
    --name Agent-Red-OpenAI `
    --resource-group Agent-Red `
    --deployment-name gpt-4o `
    --model-name gpt-4o `
    --model-version "2024-08-06" `
    --model-format OpenAI `
    --sku-name Standard `
    --sku-capacity 30

az cognitiveservices account deployment create `
    --name Agent-Red-OpenAI `
    --resource-group Agent-Red `
    --deployment-name text-embedding-3-large `
    --model-name text-embedding-3-large `
    --model-version "1" `
    --model-format OpenAI `
    --sku-name Standard `
    --sku-capacity 30

# Get endpoint and key:
az cognitiveservices account show --name Agent-Red-OpenAI --resource-group Agent-Red --query properties.endpoint -o tsv
az cognitiveservices account keys list --name Agent-Red-OpenAI --resource-group Agent-Red --query key1 -o tsv
```

### 2b. Azure Container Registry (ACR)

```powershell
az acr create --name acragentredeastus --resource-group Agent-Red --sku Basic --admin-enabled true
```

### 2c. Cosmos DB

```powershell
# Create account (serverless)
az cosmosdb create `
    --name cosmos-agentred-eastus `
    --resource-group Agent-Red `
    --default-consistency-level Session `
    --capabilities EnableServerless

# CRITICAL: Enable vector search capability
az cosmosdb update `
    --name cosmos-agentred-eastus `
    --resource-group Agent-Red `
    --capabilities EnableNoSQLVectorSearch EnableServerless
```

**⚠️ IMPORTANT:** The `EnableNoSQLVectorSearch` capability takes **~15 minutes to propagate** to the data plane after the control plane reports success. The `seed_tenant.py` script handles this gracefully — vector-dependent containers (knowledge_bases, memory_vectors) will fail initially. Re-run the seed script after 15 minutes.

```powershell
# Get Cosmos DB endpoint and key:
az cosmosdb show --name cosmos-agentred-eastus --resource-group Agent-Red --query documentEndpoint -o tsv
az cosmosdb keys list --name cosmos-agentred-eastus --resource-group Agent-Red --query primaryMasterKey -o tsv
```

### 2d. Key Vault

```powershell
az keyvault create --name kv-agentred-eastus --resource-group Agent-Red --location eastus --enable-rbac-authorization true
```

---

## 5. Phase 3: Container App Environment & API Gateway

### 3a. Create Container Apps Environment

```powershell
az containerapp env create `
    --name agent-red-env `
    --resource-group Agent-Red `
    --location eastus
```

### 3b. Create Container App

```powershell
# First, build and push the image (see Phase 4)
# Then create the app:

az containerapp create `
    --name agent-red-api-gateway `
    --resource-group Agent-Red `
    --environment agent-red-env `
    --image acragentredeastus.azurecr.io/api-gateway:v1.25.0 `
    --target-port 8080 `
    --ingress external `
    --min-replicas 1 `
    --max-replicas 2 `
    --cpu 1 `
    --memory 2Gi `
    --registry-server acragentredeastus.azurecr.io `
    --env-vars `
        "COSMOS_DB_ENDPOINT=<COSMOS_ENDPOINT>" `
        "COSMOS_DB_KEY=<COSMOS_KEY>" `
        "COSMOS_DB_DATABASE=agentred" `
        "AZURE_OPENAI_ENDPOINT=<OPENAI_ENDPOINT>" `
        "AZURE_OPENAI_API_KEY=<OPENAI_KEY>" `
        "AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini" `
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large" `
        "USE_AGENT_CONTAINERS=false" `
        "ADMIN_PREVIEW_API_KEY=<WILL_BE_SET_AFTER_SEEDING>" `
        "SMTP_HOST=smtp.titan.email" `
        "SMTP_PORT=465" `
        "SMTP_USER=<SMTP_USER>" `
        "SMTP_PASSWORD=<SMTP_PASSWORD>" `
        "AZURE_KEYVAULT_URL=https://kv-agentred-eastus.vault.azure.net/" `
        "NATS_URL=<NATS_URL_IF_USING_AGENT_CONTAINERS>" `
        "ADMIN_RESET_EMAIL=<ADMIN_EMAIL>"
```

**Note:** Use CLI `--env-vars` arguments, NOT `--yaml`. The Azure CLI has a known bug where `--yaml` fails with "JSON value could not be converted to System.Boolean" for YAML boolean values.

### 3c. Assign Managed Identity RBAC roles

```powershell
# Get the managed identity principal ID:
$PRINCIPAL_ID = az containerapp show --name agent-red-api-gateway --resource-group Agent-Red --query identity.principalId -o tsv

# ACR Pull (use REST API to avoid az cli MissingSubscription bug):
$SUBSCRIPTION_ID = az account show --query id -o tsv
$ACR_ID = az acr show --name acragentredeastus --resource-group Agent-Red --query id -o tsv

az rest --method put `
    --url "https://management.azure.com${ACR_ID}/providers/Microsoft.Authorization/roleAssignments/$(New-Guid)?api-version=2022-04-01" `
    --body "{\"properties\":{\"roleDefinitionId\":\"/subscriptions/${SUBSCRIPTION_ID}/providers/Microsoft.Authorization/roleDefinitions/7f951dda-4ed3-4680-a7ca-43fe172d538d\",\"principalId\":\"${PRINCIPAL_ID}\",\"principalType\":\"ServicePrincipal\"}}"

# Key Vault Secrets Officer:
$KV_ID = az keyvault show --name kv-agentred-eastus --query id -o tsv

az rest --method put `
    --url "https://management.azure.com${KV_ID}/providers/Microsoft.Authorization/roleAssignments/$(New-Guid)?api-version=2022-04-01" `
    --body "{\"properties\":{\"roleDefinitionId\":\"/subscriptions/${SUBSCRIPTION_ID}/providers/Microsoft.Authorization/roleDefinitions/b86a8fe4-44ce-4948-aee5-eccb2c155cd7\",\"principalId\":\"${PRINCIPAL_ID}\",\"principalType\":\"ServicePrincipal\"}}"

# Cosmos DB Built-in Data Contributor (requires special command):
$COSMOS_ID = az cosmosdb show --name cosmos-agentred-eastus --resource-group Agent-Red --query id -o tsv

# Use MSYS_NO_PATHCONV=1 in Git Bash to prevent path mangling:
MSYS_NO_PATHCONV=1 az cosmosdb sql role assignment create `
    --account-name cosmos-agentred-eastus `
    --resource-group Agent-Red `
    --scope "/" `
    --principal-id $PRINCIPAL_ID `
    --role-definition-id "00000000-0000-0000-0000-000000000002"
```

---

## 6. Phase 4: ACR Build & Deploy

### 4a. Build admin SPAs (CRITICAL — do not skip)

```powershell
cd admin/standalone && npm install && npm run build
cd ../shopify && npm install && npm run build
cd ../..
```

**⚠️ The admin `dist/` directories are `.gitignore`'d.** If you skip this step, Docker will copy stale or empty dist directories and the admin UI will not work.

### 4b. Create build context and push to ACR

```powershell
# Create minimal build context:
$CTX = "$env:TEMP\agentred-build-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $CTX -Force
Copy-Item Dockerfile $CTX/
Copy-Item requirements.txt $CTX/
Copy-Item -Recurse src $CTX/src
Copy-Item -Recurse config $CTX/config
New-Item -ItemType Directory "$CTX/admin/standalone" -Force
Copy-Item -Recurse admin/standalone/dist "$CTX/admin/standalone/dist"
New-Item -ItemType Directory "$CTX/admin/shopify" -Force
Copy-Item -Recurse admin/shopify/dist "$CTX/admin/shopify/dist"
New-Item -ItemType Directory "$CTX/widget" -Force
Copy-Item -Recurse widget/dist "$CTX/widget/dist"

# Build (Windows: az acr build may crash with UnicodeEncodeError — build still succeeds)
az acr build --registry acragentredeastus --image api-gateway:v1.25.0 --file "$CTX/Dockerfile" $CTX

# Verify build succeeded:
az acr task list-runs --registry acragentredeastus --output table
```

### 4c. Update Container App image

```powershell
az containerapp update `
    --name agent-red-api-gateway `
    --resource-group Agent-Red `
    --image acragentredeastus.azurecr.io/api-gateway:v1.25.0
```

### 4d. Initial health verification (before data seeding)

```powershell
# Wait 30-90s for NATS startup, then:
$FQDN = az containerapp show --name agent-red-api-gateway --resource-group Agent-Red --query properties.configuration.ingress.fqdn -o tsv
Invoke-WebRequest -Uri "https://$FQDN/health" -UseBasicParsing
Invoke-WebRequest -Uri "https://$FQDN/ready" -UseBasicParsing
```

---

## 7. Phase 5: Cosmos DB Seeding

### 5a. Update `.env.local` with new resource credentials

Ensure `.env.local` contains:

```
COSMOS_DB_ENDPOINT=https://cosmos-agentred-eastus.documents.azure.com:443/
COSMOS_DB_KEY=<new_cosmos_key>
COSMOS_DB_DATABASE=agentred
AZURE_OPENAI_ENDPOINT=https://agent-red-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=<new_openai_key>
```

### 5b. Run the unified seed script

```powershell
# Dry-run first:
python scripts/seed_tenant.py

# Execute with demo data:
python scripts/seed_tenant.py --execute --demo
```

**Expected output:** 8 phases, all `[OK]`. If vector-dependent containers fail (knowledge_bases, memory_vectors), wait 15 minutes for `EnableNoSQLVectorSearch` propagation and re-run.

**⚠️ CRITICAL: SAVE THE CREDENTIALS OUTPUT.** The seed script prints API keys, widget keys, and user API keys that CANNOT be retrieved later (only hashes are stored in Cosmos DB).

### 5c. Update Container App with new admin key

```powershell
# Use the superadmin user API key from seed output:
az containerapp update `
    --name agent-red-api-gateway `
    --resource-group Agent-Red `
    --set-env-vars "ADMIN_PREVIEW_API_KEY=<new_superadmin_api_key>"
```

### 5d. Update `.env.local` with new admin key

```
ADMIN_PREVIEW_API_KEY=<new_superadmin_api_key>
```

---

## 8. Phase 6: Verification

### 6a. Health checks

```powershell
$base = "https://<FQDN>"
Invoke-WebRequest -Uri "$base/health" -UseBasicParsing     # Expect: 200
Invoke-WebRequest -Uri "$base/ready" -UseBasicParsing      # Expect: 200
Invoke-WebRequest -Uri "$base/admin/standalone/" -UseBasicParsing  # Expect: 200
Invoke-WebRequest -Uri "$base/widget.js" -UseBasicParsing  # Expect: 200
```

### 6b. Regression tests

```powershell
$env:PROD_URL = "https://<FQDN>"
$env:WIDGET_KEY = "<new_widget_key>"
$env:AGENTRED_API_KEY = "<new_superadmin_api_key>"

python -m pytest tests/regression/ -x -q --tb=short
```

### 6c. Admin UI validation

```powershell
python scripts/test_admin_ui_validation.py --base-url "https://<FQDN>" --api-key "<new_superadmin_api_key>"
```

---

## 9. Phase 7: Customer Key Rotation

### Impact summary

After a full rebuild, **all previously issued credentials are invalid**:

| Credential type | Who holds it | Where it's used | Recovery action |
|----------------|-------------|-----------------|-----------------|
| Widget key (`pk_live_*`) | Shopify storefront themes | Embedded in theme app blocks | Update Shopify theme → App embeds → Agent Red Chat → Widget Key field |
| Tenant API key (`ar_*`) | Backend integrations (if any) | X-API-Key header in API calls | Communicate new key to integration owners |
| User API keys (`ar_user_*`) | Admin team members | X-API-Key header for admin access | Each team member must receive their new key |

### Step-by-step key rotation for customers

**For each affected tenant (currently: remaker-digital-001):**

1. **Shopify widget key:**
   - Go to Shopify Admin → Online Store → Themes → Customize
   - Click the App embeds icon (puzzle piece)
   - Click "Agent Red Chat" to expand settings
   - Paste the **new widget key** from seed output
   - Save the theme

2. **Admin access keys:**
   - Distribute new user API keys to all team members
   - Team members update their stored API keys

3. **External integrations:**
   - Identify any systems using the old tenant API key
   - Update them with the new tenant API key

### Minimizing key invalidation impact (future improvement)

**Current behavior:** `scripts/seed_tenant.py` always generates NEW keys on every run, even on re-seed. This means every re-run invalidates all previously issued keys.

**Recommended enhancement (TODO):** Add a `--preserve-keys` flag that:
1. Reads the existing tenant document from Cosmos DB before seeding
2. If the tenant exists and has valid key hashes, reuses them instead of generating new ones
3. Only generates new keys for net-new tenants
4. Prints "KEYS PRESERVED" instead of new credentials for existing tenants

This would allow re-seeding without customer impact for scenarios where Cosmos DB data is corrupted but the account/containers still exist.

---

## 10. Key Invalidation Impact

### Severity matrix

| Scenario | Keys invalidated? | Customer action required? |
|----------|-------------------|--------------------------|
| Normal deploy (code update) | No | No |
| Cosmos DB re-seed (same infra) | **Yes** (current behavior) | **Yes** — all keys must be rotated |
| Full infrastructure rebuild | **Yes** | **Yes** — all keys must be rotated |
| Cosmos PITR restore | No (data restored) | No |
| Container App restart | No | No |
| Azure OpenAI key rotation | No (only backend) | No |

### Customer communication template

```
Subject: Agent Red — Service Maintenance Complete — Action Required

Dear [Customer],

We've completed infrastructure maintenance on Agent Red. Your service is
fully operational, but your authentication keys have been rotated as part
of the process.

ACTION REQUIRED:
1. Update your widget key in Shopify: Go to Online Store → Themes →
   Customize → App embeds → Agent Red Chat → paste this new key:
   [NEW_WIDGET_KEY]

2. Your new admin API key: [NEW_USER_API_KEY]

Your conversation history and knowledge base have been preserved/restored.

If you have questions, contact support@remakerdigital.com.

Best regards,
Agent Red Team
```

---

## 11. Resource Reference

### Current production (as of 2026-02-13)

| Resource | Name | Region |
|----------|------|--------|
| Subscription | Azure subscription 1 (`4dce2122-690a-4654-b531-cc647db62331`) | — |
| Resource Group | `Agent-Red` | East US |
| Azure OpenAI | `Agent-Red-OpenAI` | East US |
| ACR | `acragentredeastus` (Basic) | East US |
| Cosmos DB | `cosmos-agentred-eastus` (Serverless) | East US |
| Key Vault | `kv-agentred-eastus` | East US |
| Container Apps Env | `agent-red-env` (`orangeglacier-f566a4e7`) | East US |
| Container App | `agent-red-api-gateway` | East US |
| FQDN | `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | — |

### Previous production (terminated 2026-02-13)

| Resource | Name | Region |
|----------|------|--------|
| Subscription | `828eb521-88bb-4b01-ac3e-7ba779c55212` | — |
| Resource Group | `agentred-prod-rg` | East US 2 |
| ACR | `acragentredeastus2` | East US 2 |
| Cosmos DB | `cosmos-agentred-eastus2` | East US 2 |
| Key Vault | `kv-agentred-eastus2` | East US 2 |
| FQDN | `agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io` | — |

---

## 12. Lessons Learned

### From the 2026-02-13 rebuild

1. **`EnableNoSQLVectorSearch` propagation delay:** The Cosmos DB vector search capability takes ~15 minutes to propagate after `az cosmosdb update`. The control plane immediately shows success, but container creation with vector policies fails until propagation completes. The seed script handles this gracefully with per-container try/except.

2. **Azure CLI YAML boolean bug:** `az containerapp create --yaml` fails parsing YAML booleans. Always use `--env-vars` CLI arguments instead.

3. **Azure CLI `az role assignment create` MissingSubscription:** Workaround: use `az rest --method put` with the ARM REST API directly.

4. **Git Bash path mangling:** Forward slashes in Cosmos DB scope paths get mangled by MSYS. Use `MSYS_NO_PATHCONV=1` prefix or run from PowerShell.

5. **ACR build UnicodeEncodeError on Windows:** `az acr build` crashes the local CLI with `UnicodeEncodeError: 'charmap'` during pip install log streaming. The remote build still succeeds. Verify via `az acr task list-runs`.

6. **Admin SPA dist is gitignored:** Docker COPY picks up whatever is on disk. Always run `npm run build` in both `admin/standalone/` and `admin/shopify/` before any ACR build.

7. **Key regeneration on re-seed:** Every run of `seed_tenant.py` generates new keys and upserts them, invalidating previously issued credentials. This is by design for initial provisioning but problematic for re-seeding existing tenants.

8. **Provider registration:** New subscriptions need all resource providers registered before first use. This adds 1–2 minutes to the initial setup.

---

*Last updated: 2026-02-13 (session 15)*
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
