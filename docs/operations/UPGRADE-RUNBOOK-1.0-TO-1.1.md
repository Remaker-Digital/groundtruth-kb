# Upgrade Runbook: Agent Red 1.0 → 1.1

**Document Status:** Living document — updated with each upgrade practice run
**Last Updated:** 2026-02-09
**Audience:** DevOps / Owner
**Supersedes:** Previous version of this document (2026-02-08), relevant sections of DEPLOYMENT-RUNBOOK.md (stale resource names), RELEASE-MANAGEMENT.md (Phase 6 procedures)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Context](#architecture-context)
3. [Prerequisites](#prerequisites)
4. [Automation Tooling](#automation-tooling)
5. [Non-Disruptive Upgrade Procedure (Automated)](#non-disruptive-upgrade-procedure-automated)
6. [Non-Disruptive Upgrade Procedure (Manual)](#non-disruptive-upgrade-procedure-manual)
7. [Emergency Rollback Procedure](#emergency-rollback-procedure)
8. [Regression Test Package](#regression-test-package)
9. [Schema Migration Framework](#schema-migration-framework)
10. [Staging Upgrade Test Procedure](#staging-upgrade-test-procedure)
11. [Pre-Upgrade Checklist](#pre-upgrade-checklist)
12. [Rollback Decision Criteria](#rollback-decision-criteria)
13. [Post-Upgrade Monitoring](#post-upgrade-monitoring)
14. [Upgrade Test Results](#upgrade-test-results)
15. [Troubleshooting](#troubleshooting)
16. [Appendix: Migration File Template](#appendix-migration-file-template)
17. [Appendix: Resource Reference](#appendix-resource-reference)

---

## Overview

This runbook describes the **non-disruptive upgrade procedure** from Agent Red 1.0 to 1.1. It is the single canonical reference for all upgrade operations. The procedure is:

1. **Zero downtime:** Azure Container Apps rolling update with `min_replicas=2` ensures at least one replica is always serving traffic. New revision must pass the readiness probe (`/ready`) before receiving traffic. Old revision drains connections for 60 seconds.
2. **Backward compatible:** All schema changes are additive (new fields with default values). v1.0 code reads v1.1 documents safely (ignores unknown fields). v1.1 code reads v1.0 documents safely (defaults for missing fields).
3. **Rollback safe:** Instant revert by deploying the previous image version. Schema migrations are forward-only but backward-compatible — no schema rollback needed.
4. **Data safe:** Cosmos DB continuous backup provides 30-day point-in-time restore (PITR) as the ultimate safety net.
5. **Tested before production:** Every upgrade is practiced in staging first. The 43-test regression suite validates health, functionality, and performance after each deployment.

### What Changes Between Releases

**Only the API Gateway image changes.** The 6 agent containers, SLIM Gateway, and NATS are AGNTCY upstream images in demo mode (`ActivationFailed` — expected and accepted). The pipeline calls Azure OpenAI directly (`USE_AGENT_CONTAINERS=false`).

| Component | Changes? | Notes |
|-----------|----------|-------|
| `agent-red-api-gateway` | **YES** | The only container updated between releases |
| `agent-red-nats` | No | `nats:2.10-alpine` — upstream image |
| `agent-red-slim-gateway` | No | `slim-gateway:latest` — upstream image |
| 6 agent containers | No | AGNTCY demo mode images — `ActivationFailed` expected |
| Cosmos DB schema | Maybe | Only if release includes migrations (additive, backward-compatible) |
| Key Vault secrets | Rarely | Only if new integration credentials are added |
| Terraform config | Rarely | Only if scaling/networking changes are needed |

---

## Architecture Context

### How Azure Container Apps Rolling Updates Work

Azure Container Apps with `revision_mode = "Single"` (our configuration) follows this sequence:

1. `az containerapp update --image <new>` creates a **new revision** with the new image
2. The new revision starts and must pass the **readiness probe** (`GET /ready` returning 200)
3. Once the new revision is ready, Azure **routes all new traffic** to it
4. The old revision enters a **drain period** (60 seconds, configured via `GRACEFUL_SHUTDOWN_TIMEOUT`)
5. After drain completes, the old revision **stops** (but remains available for reactivation)

Because `min_replicas = 2`, the old revision has at least 2 running replicas while the new revision starts. At no point is there zero capacity.

### NATS Startup Delay

The API Gateway connects to NATS lazily at first pipeline execution. After a new deployment:

- `/health` returns 200 within 5-10 seconds (liveness — no external dependencies)
- `/ready` may show `NATS: connected=false` for 30-90 seconds (normal lazy init)
- The first chat conversation triggers the NATS connection
- This is expected behavior, not a deployment failure

### What Happens to In-Flight Requests

- **HTTP requests:** Completed normally during the 60s drain period
- **SSE streams:** Closed when the old revision shuts down; widget auto-reconnects to the new revision
- **WebSocket connections:** Closed; widget auto-reconnects with new WebSocket
- **Chat conversations:** The conversation state is in Cosmos DB, not in-memory. Clients reconnect seamlessly.

---

## Prerequisites

### Hard Requirements (Must Be True)

| # | Requirement | How to Verify | Why |
|---|-------------|---------------|-----|
| 1 | v1.0 running and healthy | `curl /health` returns 200 with current version | Baseline confirmation |
| 2 | Cosmos DB continuous backup active | Azure Portal → cosmos-agentred-eastus2 → Backup Policy | PITR safety net |
| 3 | v1.1 image built and tested locally | `python -m pytest tests/ -x -q` passes (1,700+ tests, 0 failures) | Code quality gate |
| 4 | Regression tests pass against staging | `pytest tests/regression/ -x -q -m tier0` all pass | Environment validation |
| 5 | Azure CLI authenticated | `az account show` returns Remaker Digital subscription | Deploy permissions |
| 6 | ACR credentials valid | `az acr show --name acragentredeastus2` succeeds | Image push permission |
| 7 | Current revision name recorded | See Pre-Upgrade Checklist | Rollback target |

### Soft Requirements (Strongly Recommended)

| # | Requirement | Rationale |
|---|-------------|-----------|
| 1 | Off-peak hours (UTC 02:00-06:00 Tuesday) | Maintenance window per SLA |
| 2 | No active customer conversations | Minimize SSE disconnects |
| 3 | Application Insights open in browser | Real-time error rate monitoring |
| 4 | Staging upgrade rehearsed within 7 days | Confidence that procedure works |

---

## Automation Tooling

Three automation assets work together to execute and validate upgrades:

### 1. `scripts/deploy/upgrade.ps1` — Automated 7-Phase Upgrade

Full upgrade orchestrator that builds, deploys, validates, and finalizes in one command.

```powershell
# Standard upgrade
.\scripts\deploy\upgrade.ps1 -Version "v1.1.0"

# Dry run (shows commands without executing)
.\scripts\deploy\upgrade.ps1 -Version "v1.1.0" -DryRun

# Skip build (use pre-built ACR image)
.\scripts\deploy\upgrade.ps1 -Version "v1.1.0" -SkipBuild

# Skip regression tests (emergency only)
.\scripts\deploy\upgrade.ps1 -Version "v1.1.0" -SkipTests
```

**7 Phases:**

| Phase | Action | Duration | Failure Response |
|-------|--------|----------|------------------|
| 1 | Pre-flight checks (health, revision capture) | 15s | Abort with diagnostic |
| 2 | Build and push image to ACR | 2-4 min | Abort — no deployment made |
| 3 | Pre-upgrade regression (Tier 0 against current) | 30s | Abort — confirms baseline health |
| 4 | Deploy new image (`az containerapp update`) | 30s | Print rollback command |
| 5 | Wait for readiness (`/health` poll, 90s max) | 30-90s | Print rollback command |
| 6 | Post-upgrade regression (Tier 0 + Tier 1) | 60s | Print rollback command |
| 7 | Finalize (deactivate old revision) | 15s | Non-fatal — manual cleanup |

**Logs:** Written to `logs/upgrade-<timestamp>.log` for post-incident review.

**On failure at Phase 4+:** The script prints the exact rollback command:
```
ROLLBACK: az containerapp update --name agent-red-api-gateway --resource-group agentred-prod-rg --image <previous-image>
```

### 2. `scripts/deploy/rollback.ps1` — Emergency Rollback

Standalone rollback script for when quick recovery is needed:

```powershell
# Rollback by version tag
.\scripts\deploy\rollback.ps1 -Version "v1.0.0"

# Rollback by full image URI
.\scripts\deploy\rollback.ps1 -Image "acragentredeastus2.azurecr.io/api-gateway:v1.0.0"
```

**4 Steps:**

| Step | Action | Duration |
|------|--------|----------|
| 1 | Deploy rollback image | 30s |
| 2 | Wait for health (60s timeout) | 30-60s |
| 3 | Run Tier 0 regression tests | 30s |
| 4 | Deactivate failed revision | 15s |

### 3. `tests/regression/test_upgrade_regression.py` — 43 Production Regression Tests

Three-tier test suite designed to run against a live production endpoint:

```bash
# Tier 0 only (blocking — must pass before proceeding)
PROD_URL=https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io \
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short

# Tier 0 + Tier 1 (pre-launch gate)
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m "tier0 or tier1" --tb=short

# All tiers (comprehensive validation)
python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short
```

See [Regression Test Package](#regression-test-package) for full test inventory.

---

## Non-Disruptive Upgrade Procedure (Automated)

This is the **primary upgrade path** — use the automated script for all routine upgrades.

### Before You Start

1. Open Application Insights live metrics in a browser tab
2. Have the rollback script path ready: `scripts\deploy\rollback.ps1`
3. Ensure you're in the project root: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

### Execute

```powershell
# Full automated upgrade (build + deploy + test + finalize)
.\scripts\deploy\upgrade.ps1 -Version "v1.1.0"
```

### Expected Output (Success)

```
╔══════════════════════════════════════════════════════════════╗
║  AGENT RED NON-DISRUPTIVE UPGRADE                           ║
║  v1.0.0 → v1.1.0                                           ║
╚══════════════════════════════════════════════════════════════╝

[1/7] Pre-flight checks...
  /health: 200 (version: v1.0.0)
  Current revision: agent-red-api-gateway--abc123
  Current image: acragentredeastus2.azurecr.io/api-gateway:v1.0.0

[2/7] Building image api-gateway:v1.1.0...
  Build context created
  ACR build submitted
  Image pushed to acragentredeastus2.azurecr.io

[3/7] Pre-upgrade regression (Tier 0)...
  17 passed

[4/7] Deploying api-gateway:v1.1.0...
  Container App update submitted

[5/7] Waiting for health (90s timeout)...
  /health 200 OK after 35s

[6/7] Post-upgrade regression (Tier 0 + Tier 1)...
  33 passed

[7/7] Finalizing (deactivating old revision)...
  Deactivated: agent-red-api-gateway--abc123

╔══════════════════════════════════════════════════════════════╗
║  UPGRADE COMPLETE                                           ║
║  Image: acragentredeastus2.azurecr.io/api-gateway:v1.1.0   ║
║  Tier 0: PASSED (17/17)                                     ║
║  Tier 1: PASSED (16/16)                                     ║
║  Duration: 4m 32s                                           ║
╚══════════════════════════════════════════════════════════════╝
```

### If the Script Fails

| Phase | What Happened | What to Do |
|-------|---------------|------------|
| 1 (Pre-flight) | Production is unhealthy | Fix current deployment before attempting upgrade |
| 2 (Build) | Image build failed | Check Dockerfile / code. No deployment was made. |
| 3 (Pre-regression) | Current deployment failing tests | Investigate — production may already have issues |
| 4 (Deploy) | `az containerapp update` failed | No traffic routed to new image. Azure Portal to check. |
| 5 (Health wait) | New image not healthy after 90s | Execute rollback (script prints the command) |
| 6 (Post-regression) | Tests fail against new image | Execute rollback (script prints the command) |
| 7 (Finalize) | Old revision deactivation failed | Non-critical — manually deactivate later |

---

## Non-Disruptive Upgrade Procedure (Manual)

Use this procedure when the automated script cannot run (e.g., PowerShell not available, script bugs, unusual deployment scenario).

### Step 1: Pre-Upgrade Verification (5 min)

```bash
# Record current state
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  -o table

# Record current health
curl -s https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/health | python -m json.tool

# Verify Cosmos DB backup is active
az cosmosdb show \
  --name cosmos-agentred-eastus2 \
  --resource-group agentred-prod-rg \
  --query "backupPolicy" -o json
```

**Write down the current revision name** (e.g., `agent-red-api-gateway--abc123`). This is your rollback target.

### Step 2: Apply Schema Migrations If Needed (5 min)

Only if this release includes new migrations in `src/migrations/`:

```bash
# Apply to production Cosmos DB
# MUST be tested in staging first
COSMOS_DB_ENDPOINT=https://cosmos-agentred-eastus2.documents.azure.com:443/ \
python -m src.migrations.apply

# Verify: should show "Successfully applied N migration(s)."
```

Migrations are backward-compatible — the running v1.0 app is unaffected. New fields have defaults; v1.0 code ignores unknown fields.

### Step 3: Run Pre-Upgrade Regression (2 min)

```bash
# Confirm current deployment is healthy before changing anything
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short
```

**All 17 Tier 0 tests must pass.** If any fail, stop — investigate current production issues before proceeding.

### Step 4: Build and Push New Image (3-5 min)

```powershell
# Option A: Use build-context script (recommended for large repos)
powershell -ExecutionPolicy Bypass -File C:\Users\micha\AppData\Local\Temp\build-context.ps1
az acr build `
  --registry acragentredeastus2 `
  --image api-gateway:v1.1.0 `
  --file <context-dir>\Dockerfile <context-dir>

# Option B: Build from project root (may be slow for large repos)
az acr build `
  --registry acragentredeastus2 `
  --image api-gateway:v1.1.0 `
  --file Dockerfile .
```

**Note:** Windows `az` CLI may crash with `UnicodeEncodeError` during pip log streaming — this is cosmetic. Verify the build succeeded: `az acr task list-runs --registry acragentredeastus2 -o table`

### Step 5: Deploy New Image (30 seconds)

```bash
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.1.0
```

**Start a timer.** The new revision should be healthy within 90 seconds.

### Step 6: Wait for Health (30-90 seconds)

```bash
BASE="https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io"

# Poll health every 10 seconds
while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
  if [ "$STATUS" = "200" ]; then
    echo "Healthy!"
    curl -s "$BASE/health" | python -m json.tool
    break
  fi
  echo "Waiting... (status: $STATUS)"
  sleep 10
done
```

**If `/health` does not return 200 within 90 seconds:** Execute rollback immediately.

### Step 7: Run Post-Upgrade Regression (2 min)

```bash
# Tier 0 (blocking)
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short

# If Tier 0 passes, run Tier 1
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m "tier0 or tier1" --tb=short
```

**If any Tier 0 test fails:** Execute rollback immediately.
**If Tier 1 tests fail:** Assess severity. Rollback if core chat flow is broken.

### Step 8: Deactivate Old Revision (30 seconds)

```bash
# Only after confirming new revision is healthy and tests pass
az containerapp revision deactivate \
  --revision <old-revision-name> \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg
```

### Step 9: Run Full Regression (Optional, 3 min)

```bash
# All 43 tests including Tier 2 performance smoke
python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short
```

---

## Emergency Rollback Procedure

### Automated Rollback (Preferred)

```powershell
# Rollback to the last known good version
.\scripts\deploy\rollback.ps1 -Version "v1.0.0"
```

The script deploys the specified image, waits for health, runs Tier 0 tests, and cleans up old revisions.

### Manual Rollback (If Script Unavailable)

```bash
# Deploy the previous image
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.0.0

# Wait for health (60 seconds)
sleep 60
curl -s https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/health

# Run Tier 0 regression
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short

# Deactivate the failed revision
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --query "[?properties.active==\`true\`].name" -o tsv
# Deactivate the newer (failed) revision
az containerapp revision deactivate \
  --revision <failed-revision-name> \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg
```

### Schema After Rollback

- **No schema rollback needed.** Migrations are additive and backward-compatible. v1.0 code ignores new fields.
- **New fields persist with their defaults.** They'll be used when v1.1 is re-deployed successfully.
- **If data corruption occurred** (extremely unlikely), use Cosmos DB PITR:

```bash
az cosmosdb restore \
  --account-name cosmos-agentred-eastus2 \
  --resource-group agentred-prod-rg \
  --target-database-account-name cosmos-agentred-restore \
  --restore-timestamp "2026-02-09T12:00:00Z" \
  --location "East US 2"
```

**Note:** PITR restores to a NEW account name. You must then update the Container App env vars to point to the restored account, or migrate data back to the original account.

---

## Regression Test Package

### Test Inventory (43 Tests, 3 Tiers)

#### Tier 0: Blocking (17 tests) — `pytest -m tier0`

These tests **must all pass** before and after any deployment. A single Tier 0 failure is an immediate rollback trigger.

| ID | Group | Test | Validates |
|----|-------|------|-----------|
| T0-01 | Health | `/health` returns 200 | Liveness probe |
| T0-02 | Health | `/ready` returns 200 | Readiness probe |
| T0-03 | Health | Circuit breakers present in `/ready` | Resilience infrastructure |
| T0-04 | Health | `X-API-Version` header present | Versioning middleware |
| T0-05 | Health | Security headers present (CSP, XFO, etc.) | Security middleware |
| T0-06 | Auth | Protected endpoints return 401 | Auth middleware active |
| T0-07 | Auth | Public endpoints reachable (no 401) | Auth exempt paths correct |
| T0-08 | Auth | Widget key authentication works | Chat API accessible |
| T0-09 | Auth | Invalid auth returns 401 | No auth bypass |
| T0-10 | Auth | Webhook endpoint reachable | Billing integration |
| T0-11 | Assets | `/widget.js` returns 200 | Widget bundle served |
| T0-12 | Assets | `/admin/standalone/` returns 200 | Standalone admin served |
| T0-13 | Assets | `/admin/shopify/` returns 200 | Shopify admin served |
| T0-14 | Assets | `/docs` returns 200 | OpenAPI docs served |
| T0-15 | Tenant | `/api/tenants/lookup` returns 200 | Tenant lookup operational |
| T0-16 | Tenant | Lookup returns valid JSON | Response format correct |
| T0-17 | Tenant | `/api/checkout/session` reachable | Checkout flow operational |

#### Tier 1: Pre-Launch Gate (16 tests) — `pytest -m tier1`

These tests validate core functionality. Failures require assessment — rollback if chat flow is broken.

| ID | Group | Test | Validates |
|----|-------|------|-----------|
| T1-01 | Chat | Start conversation returns 201 | Chat API creates sessions |
| T1-02 | Chat | Send message returns 200 | Pipeline processes messages |
| T1-03 | Chat | SSE stream connects | Streaming infrastructure |
| T1-04 | Chat | Conversation state retrievable | State persistence |
| T1-05 | Chat | End conversation works | Session cleanup |
| T1-06 | Chat | Rate limiting enforced | Abuse protection |
| T1-07 | Admin | Dashboard API returns data | Billing dashboard |
| T1-08 | Admin | Knowledge API operational | KB management |
| T1-09 | Admin | Inbox API returns conversations | Conversation inbox |
| T1-10 | Admin | Analytics API operational | Reporting |
| T1-11 | Admin | Config API operational | Tenant configuration |
| T1-12 | Admin | Audit log API operational | Compliance trail |
| T1-13 | GDPR | GDPR webhook endpoints respond | Privacy compliance |
| T1-14 | GDPR | API key reset endpoint accessible | Account recovery |
| T1-15 | Isolation | Widget key scoped to tenant | Cross-tenant prevention |
| T1-16 | Isolation | Forged tenant_id rejected | Data isolation |

#### Tier 2: Performance Smoke (10 tests) — `pytest -m tier2`

These tests catch performance regressions. Failures warrant investigation but not immediate rollback.

| ID | Group | Test | Validates |
|----|-------|------|-----------|
| T2-01 | Latency | `/health` < 500ms | Liveness response time |
| T2-02 | Latency | `/ready` < 2000ms | Readiness response time |
| T2-03 | Latency | P95 of 10 health checks < 200ms | Consistent performance |
| T2-04 | Concurrency | 5 concurrent health checks all 200 | No single-threaded bottleneck |
| T2-05 | Size | `widget.js` < 100KB | Bundle size regression |
| T2-06 | Safety | No "error" in health body | No diagnostic leaks |
| T2-07 | State | Dependency states present | Health reporting complete |
| T2-08 | Cache | Semantic cache in `/ready` | Caching infrastructure |
| T2-09 | Version | Version string well-formed | Release tagging |
| T2-10 | Stability | 10 consecutive checks identical | No flapping |

### Running Tests

```bash
# Configuration (defaults to production FQDN)
export PROD_URL=https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io
export WIDGET_KEY=pk_live_c79a2bd0_dcbf0c6f
# Optional: export AGENTRED_API_KEY=<key> for admin API tests

# Tier 0 only (fast, blocking)
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short

# Tier 0 + Tier 1 (standard post-upgrade)
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m "tier0 or tier1" --tb=short

# All tiers (comprehensive)
python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short
```

### Test Design Principles

- **Read-only where possible:** Tests check responses, not create data. Tier 1 chat tests create minimal data and don't clean up (conversations auto-expire).
- **Safe against production:** No destructive operations (no deletes, no config changes, no admin mutations).
- **Idempotent:** Running tests multiple times produces the same result.
- **Fast:** Full 43-test suite completes in < 60 seconds.
- **Independent:** Each test class is self-contained. Individual tiers can be run separately.

---

## Schema Migration Framework

### How Migrations Work

1. Each migration is a Python module in `src/migrations/` (e.g., `001_add_widget_theme.py`)
2. Module defines: `VERSION` (str), `DESCRIPTION` (str), `async up(cosmos_manager)`
3. Applied migrations are tracked in the `_migrations` Cosmos DB container
4. Forward-only — no `down()` method (PITR is the rollback mechanism)
5. At startup, unapplied migrations log a WARNING but do **not** auto-apply

### Migration Rules

| Rule | Rationale |
|------|-----------|
| Additive only | New fields with default values. Never rename or remove fields. |
| Backward compatible | v1.0 code must read v1.1 documents (ignores unknown fields) |
| Idempotent | Running `up()` twice must be safe (no-op or upsert) |
| Tested in staging first | Never apply untested migrations to production |
| No auto-apply | Startup warns but does not apply — explicit `python -m src.migrations.apply` required |

### Applying Migrations

```bash
# In staging first:
COSMOS_DB_ENDPOINT=https://cosmos-agentred-staging.documents.azure.com:443/ \
python -m src.migrations.apply

# Then in production (only after staging succeeds):
COSMOS_DB_ENDPOINT=https://cosmos-agentred-eastus2.documents.azure.com:443/ \
python -m src.migrations.apply
```

### Checking for Pending Migrations

At app startup, if unapplied migrations exist:

```
WARNING: Found 1 unapplied migration(s): ['001']. Run 'python -m src.migrations.apply' to apply.
```

The app continues to run — migrations are informational only at startup.

---

## Staging Upgrade Test Procedure

**Every production upgrade must be rehearsed in staging first.** This validates the complete upgrade path including migration, deployment, regression, and rollback.

### Overview

| Step | Action | Duration |
|------|--------|----------|
| 1 | Deploy v1.0.0 to staging | 3 min |
| 2 | Seed test data (tenant, KB, demo data) | 2 min |
| 3 | Run Tier 0 baseline against v1.0.0 | 1 min |
| 4 | Apply schema migrations | 1 min |
| 5 | Deploy v1.1.0 to staging | 3 min |
| 6 | Run full regression against v1.1.0 | 2 min |
| 7 | Verify data integrity (tenant, KB, conversations) | 3 min |
| 8 | Test rollback to v1.0.0 | 3 min |
| 9 | Verify data intact after rollback | 2 min |
| 10 | Record results | 2 min |
| | **Total** | **~22 min** |

### Detailed Steps

#### 1. Deploy v1.0.0 to Staging

```bash
az containerapp update \
  --name agent-red-staging-gateway \
  --resource-group agentred-staging-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.0.0

# Wait for health
sleep 60
curl -s https://agent-red-staging-gateway.<staging-domain>/health
```

#### 2. Seed Test Data

```bash
python scripts/provision_tenant_one.py --environment staging
python scripts/seed_knowledge_base.py --load --tenant-id test-staging-001
python scripts/seed_demo_data.py --environment staging
```

#### 3. Verify v1.0.0 Baseline

```bash
PROD_URL=https://agent-red-staging-gateway.<staging-domain> \
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short
```

All 17 Tier 0 tests must pass.

#### 4. Apply Migrations

```bash
COSMOS_DB_ENDPOINT=https://cosmos-agentred-staging.documents.azure.com:443/ \
python -m src.migrations.apply
```

#### 5. Deploy v1.1.0

```bash
az containerapp update \
  --name agent-red-staging-gateway \
  --resource-group agentred-staging-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.1.0

# Wait for health
sleep 60
```

#### 6. Run Full Regression

```bash
PROD_URL=https://agent-red-staging-gateway.<staging-domain> \
python -m pytest tests/regression/test_upgrade_regression.py -x -q --tb=short
```

All 43 tests must pass.

#### 7. Verify Data Integrity

```bash
STAGING="https://agent-red-staging-gateway.<staging-domain>"

# Tenant data survived
curl -s -H "X-API-Key: <test-key>" "$STAGING/api/dashboard/usage"

# KB entries survived
curl -s -H "X-API-Key: <test-key>" "$STAGING/api/admin/knowledge"

# Conversations accessible
curl -s -H "X-API-Key: <test-key>" "$STAGING/api/admin/conversations"
```

#### 8. Test Rollback

```bash
az containerapp update \
  --name agent-red-staging-gateway \
  --resource-group agentred-staging-rg \
  --image acragentredeastus2.azurecr.io/api-gateway:v1.0.0

sleep 60

# Run Tier 0 after rollback
PROD_URL=https://agent-red-staging-gateway.<staging-domain> \
python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short
```

#### 9. Verify Data Intact After Rollback

```bash
# Same queries as Step 7 — data must be identical
curl -s -H "X-API-Key: <test-key>" "$STAGING/api/dashboard/usage"
curl -s -H "X-API-Key: <test-key>" "$STAGING/api/admin/knowledge"
```

#### 10. Record Results

Fill in the [Upgrade Test Results](#upgrade-test-results) table.

---

## Pre-Upgrade Checklist

Print this checklist and check off each item before executing a production upgrade.

```
PRE-UPGRADE CHECKLIST — Agent Red v____ → v____
Date: ____________  Operator: ____________

[ ] 1. Staging rehearsal completed within last 7 days
       Staging date: __________  Result: PASS / FAIL

[ ] 2. All unit tests pass locally
       python -m pytest tests/ -x -q --tb=short
       Total: ____  Failures: ____

[ ] 3. Current production health confirmed
       curl /health → 200  version: ________

[ ] 4. Current revision name recorded
       Revision: ________________________________

[ ] 5. Current image recorded (rollback target)
       Image: __________________________________

[ ] 6. Cosmos DB backup verified active
       az cosmosdb show → backupPolicy.type: "Continuous"

[ ] 7. Migrations (if any) applied to staging first
       Migrations in this release: Y / N / NA
       Staging migration result: PASS / FAIL / NA

[ ] 8. Off-peak timing (UTC 02:00-06:00 Tuesday preferred)
       Current UTC time: __________

[ ] 9. Application Insights open in browser
       Live metrics URL bookmarked: Y / N

[ ] 10. Rollback command ready
        .\scripts\deploy\rollback.ps1 -Version "v________"
```

---

## Rollback Decision Criteria

### Immediate Rollback (No Discussion)

| Condition | Detection Method | Max Response Time |
|-----------|-----------------|-------------------|
| `/health` not 200 within 90 seconds | upgrade.ps1 Phase 5 or manual poll | < 2 minutes |
| Tier 0 regression failure | upgrade.ps1 Phase 6 or manual `pytest` | < 2 minutes |
| Error rate > 5% in first 5 minutes | Application Insights live metrics | < 5 minutes |
| Data corruption (wrong tenant data) | Manual spot-check or Tier 1 isolation tests | < 5 minutes |
| Chat pipeline completely broken | T1-01 through T1-05 failures | < 2 minutes |

### Assess Before Rollback

| Condition | Assessment |
|-----------|------------|
| Single Tier 1 test failure (non-chat) | Check if admin-only endpoint — may not be customer-facing |
| Tier 2 performance degradation | Check if caused by cold start (NATS reconnection) — wait 5 min and retest |
| NATS `connected=false` in `/ready` | Normal for 30-90s after deploy — wait and recheck |
| Single 5xx from one endpoint | Transient — recheck 3 times before rollback decision |

### Do NOT Rollback

| Condition | Reason |
|-----------|--------|
| Agent containers `ActivationFailed` | Expected — AGNTCY demo mode images |
| NATS `connected=false` for first 90s | Lazy initialization — expected |
| Slower response time in first minute | Cold-start JIT + NATS connection — normalizes |

---

## Post-Upgrade Monitoring

### First 15 Minutes

| Minute | Check | Expected |
|--------|-------|----------|
| 0 | `/health` returns 200 | version = new version |
| 1 | `/ready` returns 200 | All subsystems healthy (NATS may be false) |
| 2 | NATS connects | `/ready` shows NATS connected=true |
| 5 | Error rate stable | Application Insights: < 1% error rate |
| 5 | First chat conversation | SSE stream works, AI response generated |
| 10 | Application Insights | No new exception types |
| 15 | Widget on storefront | Chat widget loads and responds |

### First 24 Hours

| Check | Tool | Expected |
|-------|------|----------|
| Error rate | Application Insights | < 1% sustained |
| Latency P95 | Application Insights | < 2,000ms |
| Chat completion rate | Admin dashboard | > 95% |
| SSE disconnects | Application Insights | No increase vs. baseline |
| Cosmos DB RU consumption | Azure Portal | Within normal range |
| Container restart count | Azure Portal → Container App | 0 restarts after stabilization |

---

## Upgrade Test Results

| Date | From | To | Env | Upgrade | Tests | Rollback | Post-Rollback | Operator | Notes |
|------|------|----|-----|---------|-------|----------|---------------|----------|-------|
| _Pending_ | 1.0.0 | 1.1.0 | Staging | — | — | — | — | — | First rehearsal |
| _Pending_ | 1.0.0 | 1.1.0 | Prod | — | — | — | — | — | First production upgrade |

**Legend:** PASS = all steps succeeded | FAIL = failure (describe in Notes) | SKIP = step not performed

---

## Troubleshooting

### `/health` returns 404 after deployment

**Cause:** NATS connection retry loop delays app startup. All routes return 404 until the FastAPI app is fully initialized.

**Fix:** Wait 30-90 seconds. If still 404 after 90s, check Container App logs:

```bash
az containerapp logs show \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --tail 50
```

### `az acr build` crashes with `UnicodeEncodeError`

**Cause:** Windows CLI `charmap` codec cannot encode pip install output characters.

**Fix:** This is cosmetic — the remote build succeeds. Verify:

```bash
az acr task list-runs --registry acragentredeastus2 -o table
# Look for "Succeeded" status on the latest run
```

### Container enters restart loop after deployment

**Cause:** Usually a missing environment variable or configuration issue.

**Fix:** Check logs for the specific error, then:

```bash
# Force a new revision with a deploy timestamp to break the loop
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --set-env-vars "DEPLOY_TIMESTAMP=$(date +%s)"
```

### Multiple active revisions splitting traffic

**Cause:** `az containerapp update` creates a new revision but does NOT deactivate old ones.

**Fix:** List and deactivate old revisions:

```bash
# List all active revisions
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --query "[?properties.active==\`true\`].[name, properties.template.containers[0].image]" -o table

# Deactivate the old one
az containerapp revision deactivate \
  --revision <old-revision-name> \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg
```

### Tier 1 chat tests fail with 401

**Cause:** Widget key `pk_live_c79a2bd0_dcbf0c6f` may not match the widget key hash in Cosmos DB after a migration or data change.

**Fix:** Verify the widget key in Cosmos DB matches the test fixture:

```bash
# Check the tenant document in Cosmos DB
# The widget_key_hash must match SHA-256 of the widget key
```

### Cosmos DB PITR Restore

In the catastrophic scenario where data corruption requires a full restore:

```bash
# 1. Restore to a new account
az cosmosdb restore \
  --account-name cosmos-agentred-eastus2 \
  --resource-group agentred-prod-rg \
  --target-database-account-name cosmos-agentred-restore \
  --restore-timestamp "2026-02-09T12:00:00Z" \
  --location "East US 2"

# 2. Update Container App to point to restored account
az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agentred-prod-rg \
  --set-env-vars "COSMOS_DB_ENDPOINT=https://cosmos-agentred-restore.documents.azure.com:443/"

# 3. Verify health
curl -s https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/health

# 4. Once verified, migrate data back to original account or update DNS
```

---

## Appendix: Migration File Template

```python
"""Migration NNN: Brief description.

What this migration does and why.

2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

VERSION = "001"
DESCRIPTION = "Add widget_theme field to preferences"


async def up(cosmos_manager: Any) -> None:
    """Apply migration."""
    database = cosmos_manager._client.get_database_client(
        cosmos_manager._database_name
    )
    container = database.get_container_client("preferences")

    # Query documents that need migration
    query = "SELECT * FROM c WHERE NOT IS_DEFINED(c.widget_theme)"
    items = container.query_items(
        query=query,
        enable_cross_partition_query=True,
    )

    count = 0
    async for item in items:
        item["widget_theme"] = "auto"  # Default value
        await container.upsert_item(item)
        count += 1

    logger.info("Migrated %d preference documents", count)
```

---

## Appendix: Resource Reference

| Resource | Name | Value |
|----------|------|-------|
| Resource Group | Production | `agentred-prod-rg` |
| Resource Group | Staging | `agentred-staging-rg` |
| Container Registry | ACR | `acragentredeastus2.azurecr.io` |
| Container App | API Gateway | `agent-red-api-gateway` |
| Container App Env | Production | `agent-red-cae` (domain: `lemonriver-f59f94b7.eastus2.azurecontainerapps.io`) |
| Cosmos DB | Production | `cosmos-agentred-eastus2` (database: `agentred`) |
| Cosmos DB | Staging | `cosmos-agentred-staging` |
| Key Vault | Production | `kv-agentred-eastus2` |
| Azure OpenAI | Shared | `aoai-agentred-eastus2` |
| API Gateway FQDN | Production | `agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io` |
| NATS FQDN | Internal | `agent-red-nats.internal.lemonriver-f59f94b7.eastus2.azurecontainerapps.io:4222` |
| Static IP | Production | `20.97.131.247` |
| Current Image | API Gateway | `api-gateway:v1.12.0` |
| Widget Key | remaker-digital-001 | `pk_live_c79a2bd0_dcbf0c6f` |
| Region | All resources | East US 2 |

### File Locations

| File | Purpose |
|------|---------|
| `scripts/deploy/upgrade.ps1` | Automated 7-phase upgrade script |
| `scripts/deploy/rollback.ps1` | Emergency rollback script |
| `tests/regression/test_upgrade_regression.py` | 43 production regression tests |
| `tests/regression/conftest.py` | Regression test fixtures and configuration |
| `src/migrations/` | Schema migration modules |
| `docs/operations/UPGRADE-RUNBOOK-1.0-TO-1.1.md` | This document |
| `docs/operations/RELEASE-MANAGEMENT.md` | Release management (branching, staging, versioning) |

---

*This runbook is the canonical reference for Agent Red production upgrades. All other documents (DEPLOYMENT-RUNBOOK.md, RELEASE-MANAGEMENT.md) defer to this document for upgrade procedures.*

*2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
