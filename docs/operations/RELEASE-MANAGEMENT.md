# Agent Red Customer Experience — Release Management

Procedures for releasing, upgrading, staging, branching, and regression testing
Agent Red in production. This document supersedes and corrects the deployment
procedures in `DEPLOYMENT-RUNBOOK.md` (which contains stale resource references).

**Created:** 2026-02-07
**Version:** 1.0.0

---

## Table of Contents

1. [Production Environment Reference](#1-production-environment-reference)
2. [Non-Disruptive Upgrade Procedure](#2-non-disruptive-upgrade-procedure)
3. [Staging Environment for Parallel Testing](#3-staging-environment-for-parallel-testing)
4. [Git Branching and Backport Process](#4-git-branching-and-backport-process)
5. [Regression Testing for Non-Disruptive Upgrades](#5-regression-testing-for-non-disruptive-upgrades)
6. [Quick Reference: Common Operations](#6-quick-reference-common-operations)
7. [Revision History](#7-revision-history)

---

## 1. Production Environment Reference

**These are the correct, current production resource names.** The DEPLOYMENT-RUNBOOK.md
references legacy AGNTCY resource names which are incorrect for Agent Red operations.

### Azure Resources (agentred-prod-rg, East US 2)

| Resource | Name | Access |
|----------|------|--------|
| Resource Group | `agentred-prod-rg` | East US 2 |
| Container Registry | `acragentredeastus2` (`acragentredeastus2.azurecr.io`) | East US 2 |
| Container App Environment | `agent-red-cae` | Domain: `lemonriver-f59f94b7.eastus2.azurecontainerapps.io` |
| API Gateway FQDN | `agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io` | External HTTPS |
| Cosmos DB | `cosmos-agentred-eastus2` (Serverless) | Database: `agentred` |
| Key Vault | `kv-agentred-eastus2` (RBAC) | Managed Identity |
| Azure OpenAI | `aoai-agentred-eastus2` | S0, 3 deployments |
| Static IP | `20.97.131.247` | Container App Environment |
| NATS (internal) | `agent-red-nats.internal.lemonriver-f59f94b7.eastus2.azurecontainerapps.io:4222` | TCP |

### Current Production State

| Container App | Current Image | Port | Min/Max |
|---------------|---------------|------|---------|
| agent-red-api-gateway | `api-gateway:v1.9.5` | 8000 | 2/8 |
| agent-red-intent-classifier | `intent-classifier:v1.1.0-openai` | 8080 | 2/6 |
| agent-red-knowledge-retrieval | `knowledge-retrieval:v1.1.1-fix` | 8080 | 2/6 |
| agent-red-response-generator | `response-generator:v1.1.0-openai` | 8080 | 2/10 |
| agent-red-critic-supervisor | `critic-supervisor:v1.1.0-openai` | 8080 | 2/4 |
| agent-red-escalation | `escalation:v1.1.0-openai` | 8080 | 1/3 |
| agent-red-analytics | `analytics:v1.1.0-openai` | 8080 | 1/2 |
| agent-red-slim-gateway | `slim-gateway:latest` | 8443 | 2/2 |
| agent-red-nats | `nats:2.10-alpine` | 4222 | 2/2 |

**Note:** Only the API Gateway image changes between releases. The 6 agent containers,
SLIM Gateway, and NATS are AGNTCY upstream images in demo mode (ActivationFailed — expected).
The ChatPipeline calls Azure OpenAI directly (`USE_AGENT_CONTAINERS=false`).

### Shell Variables (Set Once Per Session)

```bash
export RG="agentred-prod-rg"
export ACR="acragentredeastus2"
export ACR_URL="acragentredeastus2.azurecr.io"
export GW_FQDN="agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io"
```

---

## 2. Non-Disruptive Upgrade Procedure

### 2.1 How Azure Container Apps Rolling Updates Work

Agent Red uses `revision_mode = "Single"` in Terraform. When a container image is
updated:

1. Azure creates a **new revision** with the updated image.
2. The new revision must pass the **readiness probe** (`GET /ready`) before receiving traffic.
3. Once healthy, traffic shifts 100% to the new revision.
4. The old revision enters a **60-second draining period** (`GRACEFUL_SHUTDOWN_TIMEOUT=60`),
   allowing in-flight HTTP requests and SSE connections to complete.
5. The old revision is **deactivated** automatically (Single mode).

**Zero-downtime guarantee:** Because `min_replicas = 2` for the API Gateway, at least
one replica of the old revision continues serving traffic while the new revision starts.
The readiness probe prevents traffic from reaching the new revision until NATS connects
and all startup events complete (30-90 seconds).

### 2.2 Pre-Upgrade Checklist

Complete every item. Any failure is a stop-ship.

```
[ ] All tests pass: python -m pytest tests/ -x -q --tb=short
[ ] CI pipeline green on the commit being deployed
[ ] Git tag created: git tag -a v1.X.Y -m "Release 1.X.Y: <summary>"
[ ] Image tag matches git tag (e.g., api-gateway:v1.10.0 for git tag v1.10.0)
[ ] No Cosmos DB schema changes OR migration tested (schema is additive — new fields
    default to None, old code ignores new fields)
[ ] No new Key Vault secrets needed OR secrets pre-provisioned
[ ] Admin SPAs rebuilt if frontend changed:
      cd admin/standalone && npx vite build
      cd admin/shopify && npx vite build
[ ] Widget rebuilt if widget changed:
      cd widget && npm run build
      cp widget/dist/agent-red-widget.iife.js extensions/agent-red-chat/assets/
```

### 2.3 Build and Push

Agent Red uses `az acr build` (remote build in ACR) because `docker build` on Windows
has path and encoding issues. A build context script creates a minimal ~12MB directory.

```powershell
# Step 1: Create minimal build context (Windows PowerShell)
powershell -ExecutionPolicy Bypass -File C:\Users\micha\AppData\Local\Temp\build-context.ps1
# Output: build context created at C:\Users\micha\AppData\Local\Temp\agentred-build-XXXXXXXX

# Step 2: Build remotely in ACR
# NOTE: Windows az CLI may crash with UnicodeEncodeError during pip install
#       log streaming — the remote build succeeds. Verify via Step 3.
az acr build `
  --registry acragentredeastus2 `
  --image api-gateway:v1.10.0 `
  --file C:\Users\micha\AppData\Local\Temp\agentred-build-XXXXXXXX\Dockerfile `
  C:\Users\micha\AppData\Local\Temp\agentred-build-XXXXXXXX

# Step 3: Verify image exists in ACR
az acr repository show-tags --name acragentredeastus2 --repository api-gateway --orderby time_desc --top 5 --output table

# Step 4: If CLI crashed, verify via task runs
az acr task list-runs --registry acragentredeastus2 --top 3 --output table
```

### 2.4 Deploy

```bash
# Update the API Gateway container to the new image
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.10.0
```

**What happens next (automatic):**
- New revision created → readiness probe starts → NATS connects (30-90s) →
  `/ready` returns 200 → traffic shifts → old revision drains (60s) → old revision
  deactivated.

**IMPORTANT: Revision deactivation.** In Single mode, Azure should deactivate the old
revision automatically. However, if multiple revisions remain active (verify with the
command below), manually deactivate the old one to prevent traffic splitting:

```bash
# List active revisions
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --output table \
  --query "[].{Name:name, Active:properties.active, Replicas:properties.replicas, Created:properties.createdTime}"

# If old revision is still active, deactivate it
az containerapp revision deactivate \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --revision <old-revision-name>
```

### 2.5 Post-Upgrade Validation

Wait 60-90 seconds for NATS startup, then run:

```bash
# 1. Health check (liveness)
curl -sf https://${GW_FQDN}/health && echo "PASS: /health" || echo "FAIL: /health"

# 2. Readiness check (all dependencies)
curl -s https://${GW_FQDN}/ready | python -m json.tool

# 3. Verify expected version (check image tag in revision)
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --query "[?properties.active].name" \
  --output tsv

# 4. Smoke test: start a chat conversation (requires widget key)
curl -sf -X POST \
  -H "X-Widget-Key: pk_live_c79a2bd0_dcbf0c6f" \
  -H "Content-Type: application/json" \
  -d '{}' \
  https://${GW_FQDN}/api/chat/conversations \
  && echo "PASS: chat API" || echo "FAIL: chat API"

# 5. Verify storefront widget is loading
curl -sf https://${GW_FQDN}/widget.js -o /dev/null \
  && echo "PASS: widget.js" || echo "FAIL: widget.js"

# 6. Verify admin panels
curl -sf https://${GW_FQDN}/admin/standalone/ -o /dev/null \
  && echo "PASS: standalone admin" || echo "FAIL: standalone admin"
curl -sf https://${GW_FQDN}/admin/shopify/ -o /dev/null \
  && echo "PASS: shopify admin" || echo "FAIL: shopify admin"
```

**Success criteria:**
- `/health` returns 200
- `/ready` returns 200 (NATS `connected=false` is acceptable — lazy init)
- Chat conversation creation returns 200/201
- widget.js returns 200
- Both admin panels return 200
- Only one active revision visible

### 2.6 Rollback

If validation fails, roll back to the previous image tag:

```bash
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.9.5

# Deactivate the failed revision after rollback
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --output table

az containerapp revision deactivate \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --revision <failed-revision-name>
```

All previous image tags remain in ACR indefinitely. Rollback is always possible.

---

## 3. Staging Environment for Parallel Testing

### 3.1 Architecture: Isolated Staging in the Same Azure Subscription

Staging reuses the same Cosmos DB account and Azure OpenAI service (to avoid
duplication costs) but with separate databases and Container App names. This provides
functional equivalence to production at minimal incremental cost.

```
Production                          Staging
─────────────────────               ─────────────────────
agentred-prod-rg                    agentred-staging-rg
  agent-red-api-gateway               agent-red-staging-gw
  agent-red-nats                      agent-red-staging-nats
  cosmos-agentred-eastus2             cosmos-agentred-eastus2
    database: agentred                  database: agentred-staging
  kv-agentred-eastus2                 kv-agentred-eastus2
    secret: tenant-*                    secret: staging-tenant-*
  aoai-agentred-eastus2               aoai-agentred-eastus2
    (shared — same models)              (shared — same models)
```

### 3.2 What Staging Shares with Production

| Resource | Shared? | Why |
|----------|---------|-----|
| Azure OpenAI | Yes | Same models, same endpoint. No duplication cost. Staging uses the same `AZURE_OPENAI_ENDPOINT`. |
| Cosmos DB account | Yes | Same account, **different database** (`agentred-staging`). Partition isolation. Zero additional account cost (Serverless = pay per RU). |
| Key Vault | Yes | Same vault, staging secrets use `staging-` prefix. |
| Container Registry | Yes | Same ACR. Staging pulls the same images (or staging-tagged images). |
| Container App Environment | **No** | Separate CAE in `agentred-staging-rg`. Independent scaling, networking, and FQDN. |

### 3.3 Provisioning Staging (One-Time Setup)

```bash
# 1. Create staging resource group
az group create --name agentred-staging-rg --location eastus2

# 2. Create staging Cosmos DB database (on existing account)
az cosmosdb sql database create \
  --account-name cosmos-agentred-eastus2 \
  --resource-group agentred-prod-rg \
  --name agentred-staging

# 3. Initialize staging database containers
# Use the existing init script with COSMOS_DB_DATABASE=agentred-staging
COSMOS_DB_DATABASE=agentred-staging python scripts/init_cosmos_containers.py

# 4. Create staging.tfvars (copy from production.tfvars and modify)
cp infrastructure/terraform/production.tfvars infrastructure/terraform/staging.tfvars
# Edit staging.tfvars:
#   resource_group_name         = "agentred-staging-rg"
#   environment                 = "staging"
#   container_app_environment_name = "agent-red-staging-cae"
#   cosmos_db_database          = "agentred-staging"
#   # Container apps: prefix with "agent-red-staging-" instead of "agent-red-"
#   # Min replicas: 1 for all containers (cost savings)
#   # Max replicas: 2 for all containers

# 5. Deploy staging Container App Environment + API Gateway
cd infrastructure/terraform
terraform workspace new staging
terraform init
terraform plan -var-file="staging.tfvars"
terraform apply -var-file="staging.tfvars"
```

### 3.4 Deploying a Release Candidate to Staging

```bash
# Build with a staging-specific image tag
az acr build \
  --registry acragentredeastus2 \
  --image api-gateway:v1.10.0-rc1 \
  --file <build-context>/Dockerfile \
  <build-context>

# Deploy to staging
az containerapp update \
  --name agent-red-staging-gw \
  --resource-group agentred-staging-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.10.0-rc1
```

### 3.5 Testing in Staging

Staging has its own FQDN (assigned when the Container App Environment is created).
Run the same validation suite as production (Section 2.5) against the staging FQDN.

Additionally, run the full integration test suite against staging:

```bash
# Set staging endpoint
export STAGING_FQDN="<staging-fqdn-from-terraform-output>"

# Run integration tests against staging
AGENT_RED_API_URL=https://${STAGING_FQDN} \
  python -m pytest tests/integration/ -x -q --tb=short
```

### 3.6 Promoting Staging to Production

Once staging validation passes:

```bash
# The staging image (v1.10.0-rc1) is already in ACR.
# Re-tag it as the release version:
az acr import \
  --name acragentredeastus2 \
  --source acragentredeastus2.azurecr.io/api-gateway:v1.10.0-rc1 \
  --image api-gateway:v1.10.0

# Deploy the promoted image to production (Section 2.4)
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.10.0
```

### 3.7 Staging Cost Estimate

| Resource | Incremental Cost |
|----------|-----------------|
| Container App Environment | ~$0 (Consumption plan, pay per vCPU-second) |
| API Gateway (1 replica, idle) | ~$5-15/mo |
| NATS (1 replica) | ~$5-10/mo |
| Cosmos DB (staging database, idle) | ~$0 (Serverless, pay per RU) |
| **Total** | **~$10-25/mo** |

Staging can be scaled to 0 when not in active use to eliminate compute costs entirely.

---

## 4. Git Branching and Backport Process

### 4.1 Branching Model

```
main ──────────────────────────────────────────────────────────► (v1.1 development)
  │
  ├── tag: v1.0.0 (immutable snapshot)
  │
  └── release/1.0 ──── (UX fixes, Shopify review feedback) ──► (hotfixes only)
        │
        ├── tag: v1.0.1 (if backport deployed)
        └── tag: v1.0.2 (if another backport deployed)
```

| Branch | Purpose | Merge Direction |
|--------|---------|-----------------|
| `main` | Active development (v1.1 features) | Forward only |
| `release/1.0` | Stabilization branch for the 1.0 release | Cherry-pick FROM main, never merge INTO main |
| `v1.0.0` (tag) | Immutable snapshot of the submitted 1.0 build | Reference only |

### 4.2 Creating the 1.0 Freeze

```bash
cd "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"

# 1. Tag current main HEAD as v1.0.0
git tag -a v1.0.0 -m "Release 1.0.0: Agent Red Customer Experience initial release

1,656 tests passing. API Gateway v1.9.5 deployed.
9 Container Apps on Azure Container Apps (East US 2).
Shopify storefront integration complete (blanco-9939.myshopify.com).
ChatPipeline with direct Azure OpenAI fallback.
4-layer Persistent Customer Memory.
Hybrid retrieval (BM25 + vector + RRF).
3-tier semantic cache."

# 2. Push the tag
git push origin v1.0.0

# 3. Create release/1.0 branch from the tag
git branch release/1.0 v1.0.0
git push origin release/1.0

# 4. main continues as v1.1 development — commit v1.1 work-in-progress
git add <v1.1 files>
git commit -m "Begin v1.1 development: RAG config enhancements, strategic assessment"
git push origin main
```

### 4.3 Working on release/1.0 (Backports)

Backports are **cherry-picks from main**, not direct commits to release/1.0.
This ensures every fix originates on main and is tested there first.

**Workflow:**

```bash
# 1. Fix the issue on main first
git checkout main
# ... make the fix, commit, test ...
git commit -m "Fix: <description of the fix>"
git push origin main

# 2. Cherry-pick to release/1.0
git checkout release/1.0
git cherry-pick <commit-hash>

# 3. If cherry-pick has conflicts:
#    - Resolve conflicts manually
#    - Run tests on release/1.0: python -m pytest tests/ -x -q --tb=short
#    - git cherry-pick --continue

# 4. Tag the backport release
git tag -a v1.0.1 -m "Release 1.0.1: <summary of backported fix>"
git push origin release/1.0 --tags

# 5. Build and deploy v1.0.1 to production (Section 2)
```

**When to backport:**

| Scenario | Backport? |
|----------|-----------|
| Shopify App Store review requires a change | Yes |
| UX specialist identifies a bug | Yes |
| Security vulnerability | Yes |
| New feature (webhook, integration) | No — this goes into v1.1 |
| Test-only fix | No — release/1.0 is the deployed code |
| Documentation fix | Depends — if it affects in-app text, yes |

### 4.4 When v1.1 Replaces v1.0

If v1.1 is complete before Shopify approves v1.0, there are two scenarios:

**Scenario A: v1.0 has not been submitted yet.**
- Merge release/1.0 backports (if any) into main.
- Tag main as v1.1.0.
- Submit v1.1 to Shopify App Store instead.
- release/1.0 becomes historical.

**Scenario B: v1.0 is under Shopify review.**
- Continue developing on main (v1.1).
- When Shopify approves v1.0, deploy the approved image.
- Immediately plan v1.1 deployment (Section 2) as an upgrade.
- release/1.0 continues receiving hotfixes until v1.1 is deployed.

**Scenario C: v1.0 is deployed and serving merchants.**
- Deploy v1.1 to staging first (Section 3).
- Run full regression suite (Section 5).
- Promote to production (Section 3.6).
- release/1.0 becomes historical.

### 4.5 Branch Hygiene

- **Never merge main into release/1.0.** Only cherry-pick individual commits.
- **Never commit directly to release/1.0.** All fixes originate on main.
- **Tag every release/1.0 deployment** with incrementing patch versions (v1.0.1, v1.0.2, ...).
- **Delete release/1.0 after v1.1 is deployed** to avoid confusion.

---

## 5. Regression Testing for Non-Disruptive Upgrades

### 5.1 Test Levels

An upgrade from v1.0 to v1.1 must pass all 4 test levels before production deployment.

| Level | What | Where | Pass Criteria |
|-------|------|-------|---------------|
| L1: Unit tests | Full pytest suite | Local / CI | 0 failures, coverage ≥ 70% |
| L2: Build validation | Docker image builds | ACR remote build | Exit code 0, image appears in ACR |
| L3: Staging validation | Deployed to staging | Staging environment | All Section 2.5 checks pass |
| L4: Production smoke test | Immediately post-deploy | Production | All Section 2.5 checks pass |

### 5.2 L1: Unit + Integration Tests

```bash
# Run the full test suite (currently 1,688 tests)
python -m pytest tests/ -x -q --tb=short

# Run with coverage
python -m pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-fail-under=70 \
  --ignore=tests/integration_real_services.py \
  --ignore=tests/integration
```

**L1 pass criteria:**
- 0 test failures
- Coverage ≥ 70%
- No new deprecation warnings from Python standard library

### 5.3 L2: Build Validation

```bash
# Build the image (Section 2.3)
# Success = image tag appears in ACR

# Verify
az acr repository show-tags \
  --name acragentredeastus2 \
  --repository api-gateway \
  --orderby time_desc \
  --top 3 \
  --output table
```

### 5.4 L3: Staging Validation

Deploy to staging (Section 3.4) and run:

```bash
# Automated validation script
export STAGING_FQDN="<staging-fqdn>"

echo "=== L3 Staging Validation ==="

# Health
echo -n "Health: "
curl -sf https://${STAGING_FQDN}/health > /dev/null && echo "PASS" || echo "FAIL"

# Readiness
echo -n "Ready: "
curl -sf https://${STAGING_FQDN}/ready > /dev/null && echo "PASS" || echo "FAIL"

# Widget.js
echo -n "Widget: "
curl -sf https://${STAGING_FQDN}/widget.js -o /dev/null && echo "PASS" || echo "FAIL"

# Admin panels
echo -n "Standalone admin: "
curl -sf https://${STAGING_FQDN}/admin/standalone/ -o /dev/null && echo "PASS" || echo "FAIL"
echo -n "Shopify admin: "
curl -sf https://${STAGING_FQDN}/admin/shopify/ -o /dev/null && echo "PASS" || echo "FAIL"

# Chat API (requires a widget key provisioned in staging)
echo -n "Chat API: "
curl -sf -X POST \
  -H "X-Widget-Key: <staging-widget-key>" \
  -H "Content-Type: application/json" \
  -d '{}' \
  https://${STAGING_FQDN}/api/chat/conversations > /dev/null \
  && echo "PASS" || echo "FAIL"

# API auth enforcement (should return 401)
echo -n "Auth enforcement: "
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" https://${STAGING_FQDN}/api/dashboard/usage)
[ "$HTTP_CODE" = "401" ] && echo "PASS (401)" || echo "FAIL ($HTTP_CODE)"

echo "=== L3 Complete ==="
```

**L3 also includes:**
- Run integration tests against staging Cosmos DB / Azure OpenAI (Section 3.5)
- Manual UX verification: open the storefront, interact with chat widget, verify
  AI responds, verify admin dashboards render

### 5.5 L4: Production Smoke Test

After production deployment (Section 2.4), run the same validation checks from
Section 2.5. Additionally:

```bash
# Verify the live storefront widget works
# Open in browser: https://blanco-9939.myshopify.com/
# 1. Widget launcher button visible (bottom-right)
# 2. Click to open — chat panel renders
# 3. Send a message — AI responds within 5 seconds
# 4. Close and reopen — conversation persists

# Verify the admin panels
# 1. https://${GW_FQDN}/admin/standalone/ — login page renders
# 2. https://${GW_FQDN}/admin/shopify/ — loads (outside Shopify iframe, may show error — expected)
```

### 5.6 Regression Test Matrix

The following table defines which tests cover which upgrade risks:

| Risk | Test Coverage | Level |
|------|--------------|-------|
| New code breaks existing API endpoints | 1,688 unit tests | L1 |
| Docker image fails to build | ACR remote build | L2 |
| New code breaks with real Azure services | 42 integration tests | L1 (local) / L3 (staging) |
| New code breaks SSE streaming | `test_sse_error_handling.py`, `test_sse_metering_multitab.py` | L1 |
| New code breaks auth/middleware | `test_auth_middleware.py`, `test_middleware_pipeline.py` | L1 |
| New code breaks billing | `test_http_billing.py`, `test_usage_consumption.py` | L1 |
| Widget doesn't load on storefront | Manual browser check | L3/L4 |
| Admin SPA doesn't render | `curl` check + manual browser check | L3/L4 |
| Chat pipeline produces incorrect responses | `test_retrieval_config.py`, pipeline tests | L1/L3 |
| Critic blocks valid responses | `test_critic_policy.py`, adversarial tests | L1 |
| Database schema incompatibility | `test_cosmos_repository.py` | L1 |
| Rate limiting regression | `test_adversarial.py` | L1 |
| Security header regression | `test_adversarial.py`, `test_cross_module.py` | L1 |

### 5.7 Upgrade Compatibility Rules

Agent Red uses **additive schema evolution** — new fields default to `None`, old code
ignores new fields. This means:

| Change Type | Backward Compatible? | Action Required |
|-------------|---------------------|-----------------|
| New field on existing document | Yes | None — defaults to None |
| New Cosmos DB collection | Yes | Old code doesn't query it |
| New API endpoint | Yes | Old clients don't call it |
| New config field | Yes | `_PREFS_DIRECT_FIELDS` handles unknown gracefully |
| Renamed field | **No** | Migration script + coordinate deploy |
| Removed field | **No** | Migration script + coordinate deploy |
| Changed field type | **No** | Migration script + coordinate deploy |
| New required env var | **Caution** | Must be set on Container App before deploy |

**For v1.0 → v1.1 specifically:** All v1.1 enhancements (RAG config, webhooks,
integrations) are additive. No migration scripts are needed. The v1.1 image can be
deployed as a drop-in replacement for v1.0.

### 5.8 Pre-Upgrade Diff Review

Before any upgrade, review the diff between the current production tag and the
target release:

```bash
# What changed between v1.0.0 and the current state of main?
git diff v1.0.0..main --stat

# Review changes to critical files
git diff v1.0.0..main -- src/main.py           # Router/middleware changes
git diff v1.0.0..main -- src/multi_tenant/auth.py  # Auth changes
git diff v1.0.0..main -- src/chat/pipeline.py  # Pipeline changes
git diff v1.0.0..main -- Dockerfile             # Build changes
git diff v1.0.0..main -- requirements.txt       # Dependency changes

# List new files (potential new dependencies or config requirements)
git diff v1.0.0..main --diff-filter=A --name-only
```

---

## 6. Quick Reference: Common Operations

### Tag and Freeze a Release

```bash
git tag -a v1.X.0 -m "Release 1.X.0: <summary>"
git push origin v1.X.0
git branch release/1.X v1.X.0
git push origin release/1.X
```

### Deploy to Production

```bash
# Build → Deploy → Validate (3 commands)
az acr build --registry acragentredeastus2 --image api-gateway:v1.X.0 --file <ctx>/Dockerfile <ctx>
az containerapp update --name agent-red-api-gateway --resource-group agentred-prod-rg --image acragentredeastus2.azurecr.io/api-gateway:v1.X.0
curl -sf https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/health && echo "OK"
```

### Rollback

```bash
az containerapp update --name agent-red-api-gateway --resource-group agentred-prod-rg --image acragentredeastus2.azurecr.io/api-gateway:<previous-tag>
```

### Cherry-Pick to Release Branch

```bash
git checkout release/1.0
git cherry-pick <commit-hash>
git tag -a v1.0.X -m "Backport: <summary>"
git push origin release/1.0 --tags
```

### Run Full Regression

```bash
python -m pytest tests/ -x -q --tb=short --cov=src --cov-fail-under=70 --ignore=tests/integration_real_services.py --ignore=tests/integration
```

---

## 7. Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-07 | 1.0.0 | Initial release management document. Covers all 4 procedures: non-disruptive upgrade, staging environment, branching/backport, regression testing. Corrects stale resource references from DEPLOYMENT-RUNBOOK.md. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
