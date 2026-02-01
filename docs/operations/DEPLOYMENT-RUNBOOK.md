# Agent Red Customer Experience — Deployment, DR & Maintenance Runbook

Operational procedures for deploying, recovering, and maintaining the Agent Red Customer Experience production environment.

**Work Items:** WI #148 (Deployment), WI #149 (Disaster Recovery), WI #150 (Maintenance)

**Architecture References:** Decision #18 (Backup), Decision #19 (Zero-downtime deployment), Decision #20 (CMK), Decision #21 (Maintenance window)

---

## Table of Contents

1. [Environment Reference](#1-environment-reference)
2. [Deployment Procedure (WI #148)](#2-deployment-procedure-wi-148)
3. [Disaster Recovery (WI #149)](#3-disaster-recovery-wi-149)
4. [Maintenance Procedure (WI #150)](#4-maintenance-procedure-wi-150)
5. [Contact Information](#5-contact-information)
6. [Revision History](#6-revision-history)

---

## 1. Environment Reference

### Azure Resources

| Resource | Name | Region |
|----------|------|--------|
| Resource Group | `agntcy-prod-rg` | East US 2 |
| Container Registry | `acragntcycsprodrc6vcp.azurecr.io` | East US 2 |
| Cosmos DB | `cosmos-agntcy-cs-prod-rc6vcp` (Serverless) | East US 2 |
| Key Vault | `kv-agntcy-cs-prod-rc6vcp` | East US 2 |
| Application Insights | `agntcy-cs-prod-appinsights-rc6vcp` | East US 2 |
| Application Gateway | `agntcy-cs-prod-appgw` (IP: `20.110.214.55`) | East US 2 |
| Virtual Network | `agntcy-cs-prod-vnet` (`10.0.0.0/16`) | East US 2 |
| Container App Environment | `agent-red-cae` | East US 2 |

### Container Inventory (9 services)

| Container | Image Tag | Private IP | Port | Min/Max | Critical |
|-----------|-----------|------------|------|---------|----------|
| API Gateway | `api-gateway:v1.1.2-openai` | assigned | 8080 | 2/8 | Yes |
| Intent Classifier | `intent-classifier:v1.1.0-openai` | 10.0.1.10 | 8080 | 2/6 | Yes |
| Knowledge Retrieval | `knowledge-retrieval:v1.1.1-fix` | 10.0.1.6 | 8080 | 2/6 | Yes |
| Response Generator | `response-generator:v1.1.0-openai` | 10.0.1.8 | 8080 | 2/10 | Yes |
| Critic/Supervisor | `critic-supervisor:v1.1.0-openai` | 10.0.1.7 | 8080 | 2/4 | Yes |
| Escalation | `escalation:v1.1.0-openai` | 10.0.1.11 | 8080 | 1/3 | No |
| Analytics | `analytics:v1.1.0-openai` | 10.0.1.9 | 8080 | 1/2 | No |
| SLIM Gateway | `slim-gateway:latest` | 10.0.1.4 | 8443 | 2/2 | Yes |
| NATS JetStream | `nats:2.10-alpine` | 10.0.1.5 | 4222 | 2/2 | Yes |

### Health Probe Paths

| Container | Liveness | Readiness | Notes |
|-----------|----------|-----------|-------|
| API Gateway | `GET /health` | `GET /ready` | Full dependency check |
| Agent containers (6) | `GET /health` | `GET /ready` | Per-agent dependency checks |
| SLIM Gateway | `GET /healthz:8443` | `GET /healthz:8443` | gRPC health service |
| NATS | `GET /healthz:8222` | `GET /healthz:8222` | NATS monitoring port |

### Terraform Working Directory

```
infrastructure/terraform/
  main.tf                    # 9 container apps, environment, scaling
  variables.tf               # All input variables
  dr_security.tf             # Backup, CMK, archival, health probes, rolling deploy
  scaling_profiles.tf        # KEDA profiles, night scaling, validation
  production.tfvars.example  # Template for production variables
```

---

## 2. Deployment Procedure (WI #148)

### 2.1 Pre-Deployment Checklist

Complete every item before proceeding. Any failure is a stop-ship.

```
[ ] All tests pass locally: python -m pytest tests/ --tb=short
[ ] CI pipeline green on the PR branch (GitHub Actions)
[ ] Git tag created for the release: vX.Y.Z
[ ] CHANGELOG or commit log reviewed for breaking changes
[ ] Database migration check: no schema changes OR migration script tested
[ ] Scaling check: verify current replica counts before deployment
[ ] Secrets check: no new Key Vault secrets needed OR secrets pre-provisioned
[ ] Terraform plan reviewed (if infra changes): no unexpected destroys
[ ] Notification sent to #ops channel (if applicable)
[ ] SSE connection count checked (avoid deploying during peak active sessions)
```

**Run the pre-flight validation:**

```bash
# 1. Run the full test suite
cd E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
python -m pytest tests/ --tb=short -q

# 2. Tag the release
git tag -a v1.2.0 -m "Release 1.2.0: <summary>"
git push origin v1.2.0

# 3. Check current container state
az containerapp list \
  --resource-group agntcy-prod-rg \
  --output table \
  --query "[].{Name:name, Status:properties.runningStatus, Replicas:properties.template.scale.minReplicas}"

# 4. Check active SSE connections (via API Gateway)
curl -s https://20.110.214.55/ready | python -m json.tool | grep sse_connections
```

### 2.2 Build and Push Docker Images

Build images for only the containers that changed. Use the git tag as the image tag.

```bash
# Set variables
export ACR="acragntcycsprodrc6vcp.azurecr.io"
export TAG="v1.2.0"

# Authenticate to ACR
az acr login --name acragntcycsprodrc6vcp

# Build and push the changed container(s)
# Replace <container-name> with the actual container directory name.
docker build -t ${ACR}/api-gateway:${TAG} -f docker/api-gateway/Dockerfile .
docker push ${ACR}/api-gateway:${TAG}

# Repeat for each changed container:
# docker build -t ${ACR}/intent-classifier:${TAG} -f docker/intent-classifier/Dockerfile .
# docker push ${ACR}/intent-classifier:${TAG}
# docker build -t ${ACR}/knowledge-retrieval:${TAG} -f docker/knowledge-retrieval/Dockerfile .
# docker push ${ACR}/knowledge-retrieval:${TAG}
# docker build -t ${ACR}/response-generator:${TAG} -f docker/response-generator/Dockerfile .
# docker push ${ACR}/response-generator:${TAG}
# docker build -t ${ACR}/critic-supervisor:${TAG} -f docker/critic-supervisor/Dockerfile .
# docker push ${ACR}/critic-supervisor:${TAG}
# docker build -t ${ACR}/escalation:${TAG} -f docker/escalation/Dockerfile .
# docker push ${ACR}/escalation:${TAG}
# docker build -t ${ACR}/analytics:${TAG} -f docker/analytics/Dockerfile .
# docker push ${ACR}/analytics:${TAG}

# Verify the image is in ACR
az acr repository show-tags \
  --name acragntcycsprodrc6vcp \
  --repository api-gateway \
  --orderby time_desc \
  --top 5 \
  --output table
```

### 2.3 Deploy via Azure CLI (Per-Container Rolling Update)

Deploy one container at a time. Start with non-critical containers (Escalation, Analytics), then agent containers, then API Gateway last.

**Recommended deployment order:**

1. Analytics (non-critical, lowest traffic)
2. Escalation (non-critical)
3. Knowledge Retrieval
4. Intent Classifier
5. Response Generator
6. Critic/Supervisor
7. SLIM Gateway (only if changed)
8. NATS (only if changed -- coordinate carefully)
9. API Gateway (last -- external-facing)

**Deploy a single container:**

```bash
export ACR="acragntcycsprodrc6vcp.azurecr.io"
export TAG="v1.2.0"
export RG="agntcy-prod-rg"
export CONTAINER_NAME="api-gateway"  # Change per container

az containerapp update \
  --name "agent-red-${CONTAINER_NAME}" \
  --resource-group ${RG} \
  --image "${ACR}/${CONTAINER_NAME}:${TAG}"
```

**What happens during the rolling update (Decision #19, WI #59):**

1. Azure Container Apps creates a new revision with the updated image.
2. The new revision starts and must pass the readiness probe (`/ready`) before receiving traffic.
3. Once the new revision is healthy, traffic shifts from the old revision to the new revision (100% traffic weight on latest revision, as configured in `main.tf`).
4. The old revision enters a draining state for 60 seconds (`GRACEFUL_SHUTDOWN_TIMEOUT=60`), allowing in-flight HTTP requests and NATS message processing to complete.
5. After the draining period, the old revision terminates.

Because `revision_mode = "Single"` is set in Terraform, Azure automatically deactivates the old revision after the new one is live. The `min_replicas` setting ensures capacity is maintained throughout the transition (critical containers always have at least 2 replicas).

**Deploy via Terraform (for infrastructure-level changes):**

```bash
cd infrastructure/terraform

# Plan first -- review every change
terraform plan -var-file="production.tfvars" -out=deploy.tfplan

# Review the plan output carefully:
# - No unexpected resource deletions (especially Cosmos DB -- prevent_destroy is set)
# - Image tags match the intended release
# - Replica counts unchanged unless intentional
# - No changes to backup or CMK configuration unless planned

# Apply the plan
terraform apply deploy.tfplan

# Clean up the plan file
rm deploy.tfplan
```

### 2.4 Post-Deployment Validation

Run these checks within 5 minutes of deployment completion. If any check fails, proceed to Section 2.5 (Rollback).

```bash
export RG="agntcy-prod-rg"
export GW_IP="20.110.214.55"

# 1. Verify container status -- all should show "Running"
az containerapp list \
  --resource-group ${RG} \
  --output table \
  --query "[].{Name:name, Status:properties.runningStatus}"

# 2. Liveness probe -- should return {"status": "healthy", "version": "1.0.0"}
curl -s https://${GW_IP}/health | python -m json.tool

# 3. Readiness probe -- should return "ready" with all dependencies connected
curl -s https://${GW_IP}/ready | python -m json.tool

# 4. Verify NATS connectivity (from readiness output)
curl -s https://${GW_IP}/ready | python -c "
import json, sys
data = json.load(sys.stdin)
nats = data.get('nats', {})
if not nats.get('connected'):
    print('FAIL: NATS not connected')
    sys.exit(1)
print(f'OK: NATS connected, {nats.get(\"active_streams\", 0)} active streams')
"

# 5. Verify circuit breakers (none should be OPEN)
curl -s https://${GW_IP}/ready | python -c "
import json, sys
data = json.load(sys.stdin)
breakers = data.get('circuit_breakers', {})
for name, state in breakers.items():
    if state == 'OPEN':
        print(f'FAIL: Circuit breaker {name} is OPEN')
        sys.exit(1)
print(f'OK: {len(breakers)} circuit breakers healthy')
"

# 6. Check container revision and restart count
az containerapp revision list \
  --name agent-red-api-gateway \
  --resource-group ${RG} \
  --output table \
  --query "[].{Name:name, Active:properties.active, Replicas:properties.replicas, Created:properties.createdTime}"

# 7. Check Application Insights for error spikes (last 5 minutes)
az monitor app-insights query \
  --app agntcy-cs-prod-appinsights-rc6vcp \
  --resource-group ${RG} \
  --analytics-query "
    requests
    | where timestamp > ago(5m)
    | summarize total=count(), failed=countif(success == false)
    | extend error_rate = round(todouble(failed) / todouble(total) * 100, 2)
  " \
  --output table

# 8. Smoke test -- send a test API request (use a test tenant API key)
# curl -s -H "X-API-Key: <test-tenant-api-key>" https://${GW_IP}/api/chat/conversations | python -m json.tool
```

**Post-deployment success criteria:**

- All containers show "Running" status with 0 restarts
- `/health` returns `{"status": "healthy"}` with the expected version
- `/ready` returns `{"status": "ready"}` with NATS connected
- No circuit breakers in OPEN state
- Error rate < 1% over 5 minutes
- P95 latency < 2,000ms

### 2.5 Rollback Procedure

If post-deployment validation fails, roll back to the previous image tag.

**Rollback a single container to the previous image:**

```bash
export ACR="acragntcycsprodrc6vcp.azurecr.io"
export PREVIOUS_TAG="v1.1.0"  # The tag that was running before the deployment
export RG="agntcy-prod-rg"
export CONTAINER_NAME="api-gateway"

az containerapp update \
  --name "agent-red-${CONTAINER_NAME}" \
  --resource-group ${RG} \
  --image "${ACR}/${CONTAINER_NAME}:${PREVIOUS_TAG}"
```

**Rollback all containers (full release rollback):**

```bash
export ACR="acragntcycsprodrc6vcp.azurecr.io"
export PREVIOUS_TAG="v1.1.0"
export RG="agntcy-prod-rg"

for CONTAINER in api-gateway intent-classifier knowledge-retrieval response-generator critic-supervisor escalation analytics; do
  echo "Rolling back agent-red-${CONTAINER} to ${PREVIOUS_TAG}..."
  az containerapp update \
    --name "agent-red-${CONTAINER}" \
    --resource-group ${RG} \
    --image "${ACR}/${CONTAINER}:${PREVIOUS_TAG}"
done
```

**Rollback Terraform changes:**

```bash
cd infrastructure/terraform

# Revert to the previous commit's Terraform state
git checkout HEAD~1 -- main.tf variables.tf dr_security.tf scaling_profiles.tf

# Plan and apply the rollback
terraform plan -var-file="production.tfvars" -out=rollback.tfplan
terraform apply rollback.tfplan

# Restore the working tree (the failed changes are still in git)
git checkout HEAD -- main.tf variables.tf dr_security.tf scaling_profiles.tf
```

**Database rollback (if applicable):**

If the deployment included Cosmos DB schema changes (new collections, new indexes), and the rollback requires removing them:

```bash
# Cosmos DB collections are additive -- old code ignores new collections.
# Only rollback if a collection was REMOVED or an index was CHANGED in a
# way that breaks the previous version.
#
# Point-in-time restore (last resort -- restores entire account):
az cosmosdb sql database restore \
  --account-name cosmos-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --name agent-red-prod \
  --restore-timestamp "2026-02-01T12:00:00Z"
```

**After rollback:**

1. Rerun all post-deployment validation checks from Section 2.4.
2. Create a post-incident issue documenting: what failed, root cause hypothesis, rollback time.
3. Do not reattempt the deployment until the root cause is identified and fixed.

### 2.6 Hotfix Procedure

For critical production issues requiring an immediate patch (security vulnerability, data corruption, complete service outage).

**Abbreviated process:**

1. Create a `hotfix/` branch from the latest production tag.
2. Apply the minimal fix. Run the test suite.
3. Tag as `vX.Y.Z-hotfix.1`.
4. Build and push only the affected container(s).
5. Deploy the affected container(s) using the process in Section 2.3.
6. Run post-deployment validation (Section 2.4).
7. Merge the hotfix branch back into `main`.

```bash
# Create hotfix branch from production tag
git checkout -b hotfix/critical-fix v1.2.0

# Apply the fix, commit, tag
git add <files>
git commit -m "Hotfix: <description>"
git tag -a v1.2.0-hotfix.1 -m "Hotfix: <description>"
git push origin hotfix/critical-fix --tags

# Build and deploy only the affected container
export ACR="acragntcycsprodrc6vcp.azurecr.io"
docker build -t ${ACR}/api-gateway:v1.2.0-hotfix.1 -f docker/api-gateway/Dockerfile .
docker push ${ACR}/api-gateway:v1.2.0-hotfix.1

az containerapp update \
  --name agent-red-api-gateway \
  --resource-group agntcy-prod-rg \
  --image "${ACR}/api-gateway:v1.2.0-hotfix.1"

# Merge back to main after validation
git checkout main
git merge hotfix/critical-fix
git push origin main
```

**Hotfix approval:** Hotfixes bypass the normal PR review process but require post-merge review within 24 hours.

---

## 3. Disaster Recovery (WI #149)

### 3.1 Architecture Overview

Agent Red runs DR Option A: single region (East US 2) with Cosmos DB continuous backup.

| Component | DR Strategy | Recovery Method |
|-----------|-------------|-----------------|
| Cosmos DB | 7-day continuous PITR | Self-service point-in-time restore |
| Container Apps | Container images in ACR | Redeploy from ACR |
| Key Vault | Azure-managed redundancy | Soft-delete + purge protection |
| Blob Storage (archival) | LRS with 30-day soft delete | Undelete or restore from archive |
| Application Gateway | Stateless | Terraform redeploy |
| NATS JetStream | Ephemeral (7-day retention) | Recreate streams from tenant config |
| Configuration | Terraform state + git | Reapply from Terraform + production.tfvars |

### 3.2 Recovery Time Objectives (SLA Commitments)

| Tier | RTO | RPO | SLA Uptime |
|------|-----|-----|------------|
| Enterprise | 4 hours | 0 (continuous backup) | 99.95% |
| Professional | 8 hours | 0 (continuous backup) | 99.9% |
| Starter | 24 hours | 0 (continuous backup) | 99.5% |

RPO is effectively zero for Cosmos DB data because continuous backup captures every write. NATS messages are ephemeral and may be lost (acceptable -- messages are redelivered on consumer restart).

### 3.3 Scenario 1: Individual Container Failure

**Symptoms:** Container repeatedly restarting, liveness probe failures, readiness probe failures.

**Automatic recovery:** Azure Container Apps automatically restarts failed containers after 3 consecutive liveness probe failures (30s interval, so detection takes ~90s). If `min_replicas >= 2` (all critical containers), traffic is served by the healthy replica during restart.

**Manual intervention (if auto-recovery fails):**

```bash
export RG="agntcy-prod-rg"
export CONTAINER="api-gateway"  # The failing container

# 1. Check the current state
az containerapp show \
  --name "agent-red-${CONTAINER}" \
  --resource-group ${RG} \
  --query "properties.runningStatus" \
  --output tsv

# 2. Check container logs for the root cause
az containerapp logs show \
  --name "agent-red-${CONTAINER}" \
  --resource-group ${RG} \
  --tail 100

# 3. Force a new revision (restart with the same image)
az containerapp update \
  --name "agent-red-${CONTAINER}" \
  --resource-group ${RG} \
  --set-env-vars "FORCE_RESTART=$(date +%s)=true"

# 4. If the container still fails, redeploy from the last known good image
az containerapp update \
  --name "agent-red-${CONTAINER}" \
  --resource-group ${RG} \
  --image "acragntcycsprodrc6vcp.azurecr.io/${CONTAINER}:<last-good-tag>"

# 5. Verify recovery
curl -s https://20.110.214.55/health | python -m json.tool
curl -s https://20.110.214.55/ready | python -m json.tool
```

**Expected recovery time:** 1-5 minutes (auto), 10-15 minutes (manual).

### 3.4 Scenario 2: Data Corruption

**Symptoms:** Incorrect data returned by API, missing tenant records, corrupted conversation history, inconsistent billing counters.

**Recovery using Cosmos DB point-in-time restore (7-day window):**

```bash
# 1. Identify the point in time BEFORE the corruption
#    Check audit logs and Application Insights to determine the exact time.
export RESTORE_TIME="2026-02-01T10:30:00Z"  # UTC timestamp before corruption

# 2. Restore the database to a new account (non-destructive)
#    This creates a COPY -- the production account is not modified.
az cosmosdb restore \
  --account-name cosmos-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --target-database-account-name cosmos-agntcy-cs-restore-temp \
  --restore-timestamp "${RESTORE_TIME}" \
  --location "East US 2"

# 3. Verify the restored data
#    Connect to the restored account and validate:
#    - Tenant documents exist and are correct
#    - Conversation data intact
#    - Usage counters consistent

# 4. Option A: Copy corrected data from restored account to production
#    Use Azure Data Factory or a custom script to copy specific documents.
#    Recommended for targeted corruption (single tenant, single collection).

# 5. Option B: Swap DNS / connection strings to the restored account
#    Recommended only for catastrophic corruption affecting all data.
#    Update Terraform variables:
#      cosmos_db_endpoint = "https://cosmos-agntcy-cs-restore-temp.documents.azure.com:443/"
#      cosmos_db_account_name = "cosmos-agntcy-cs-restore-temp"
#    Then: terraform apply -var-file="production.tfvars"

# 6. Clean up the temporary restored account after verification
az cosmosdb delete \
  --name cosmos-agntcy-cs-restore-temp \
  --resource-group agntcy-prod-rg \
  --yes
```

**Partial restore (single collection):**

Cosmos DB PITR restores the entire database. For single-collection corruption, restore to a temporary account and then copy only the affected collection's documents:

```bash
# Copy documents from restored account to production using a script.
# Example: restore only the 'conversations' collection for tenant-123
python scripts/ops/copy_cosmos_documents.py \
  --source-endpoint "https://cosmos-agntcy-cs-restore-temp.documents.azure.com:443/" \
  --target-endpoint "https://cosmos-agntcy-cs-prod-rc6vcp.documents.azure.com:443/" \
  --database "agent-red-prod" \
  --collection "conversations" \
  --partition-key "tenant-123"
```

**Expected recovery time:** 30-60 minutes for targeted restore, 2-4 hours for full database restore.

### 3.5 Scenario 3: Region Outage (East US 2)

**Impact:** Complete service unavailability. All containers, Cosmos DB, Key Vault, Application Gateway offline.

**Current capability (Option A):** Wait for the region to recover. Azure region outages historically resolve within 1-4 hours. Cosmos DB data is safe (LRS replication within the region, continuous backup stored in paired region).

**Recovery steps:**

```bash
# 1. Confirm the outage is regional (not service-specific)
az status  # Check Azure status page

# 2. Monitor Azure status for East US 2 recovery
#    https://status.azure.com/

# 3. Once the region recovers, verify all resources
az containerapp list --resource-group agntcy-prod-rg --output table
curl -s https://20.110.214.55/health | python -m json.tool
curl -s https://20.110.214.55/ready | python -m json.tool

# 4. Check Cosmos DB account status
az cosmosdb show \
  --name cosmos-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --query "properties.provisioningState" \
  --output tsv

# 5. Verify NATS streams were recreated
curl -s https://20.110.214.55/ready | python -c "
import json, sys
data = json.load(sys.stdin)
nats = data.get('nats', {})
print(f'NATS connected: {nats.get(\"connected\")}')
print(f'Active streams: {nats.get(\"active_streams\", 0)}')
"

# 6. If NATS streams were lost, tenant provisioning will recreate them
#    on the next request for each tenant. No manual intervention needed
#    because TenantNATSManager.provision_tenant_topics() is idempotent.
```

**Communication during outage:**

1. Post status update to customers within 15 minutes of detection.
2. Update every 30 minutes until resolution.
3. Post resolution summary within 2 hours of recovery.

**If the region does not recover within the RTO window:**

Proceed to emergency cross-region deployment. This requires manual effort because Option A does not include pre-provisioned secondary infrastructure.

```bash
# Emergency: deploy to a secondary region (e.g., Central US)
# This is a manual process -- Terraform files need location overrides.

# 1. Restore Cosmos DB to the secondary region
az cosmosdb restore \
  --account-name cosmos-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --target-database-account-name cosmos-agntcy-cs-dr-centralus \
  --restore-timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --location "Central US"

# 2. Create a new Container App Environment in Central US
#    Update Terraform variables and apply:
#    location = "centralus"
#    cosmos_db_endpoint = "<restored account endpoint>"
#    Requires: new subnet, new App Gateway IP, DNS update

# 3. Deploy all containers from ACR (images are geo-replicated if ACR
#    Premium is enabled; otherwise, push images to a new ACR in Central US)

# 4. Update DNS to point to the new Application Gateway IP
```

**Expected recovery time:** 2-8 hours depending on region recovery speed. Cross-region emergency deployment: 4-8 hours.

### 3.6 Scenario 4: Key Vault Unavailability

**Symptoms:** Secret retrieval failures, new tenant provisioning fails, API key validation fails.

**Recovery:**

```bash
# 1. Check Key Vault status
az keyvault show \
  --name kv-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --query "properties.provisioningState" \
  --output tsv

# 2. Key Vault has soft-delete enabled (90-day retention).
#    If a secret was accidentally deleted:
az keyvault secret recover \
  --vault-name kv-agntcy-cs-prod-rc6vcp \
  --name "<secret-name>"

# 3. The TenantSecretService has a 5-minute in-memory cache.
#    Existing sessions continue working during brief outages.
#    Check the /ready endpoint for Key Vault health:
curl -s https://20.110.214.55/ready | python -c "
import json, sys
data = json.load(sys.stdin)
print('Key Vault:', json.dumps(data.get('key_vault', {}), indent=2))
"
```

### 3.7 Option C Upgrade Trigger (WI #156)

**When to upgrade from Option A to Option C (geo-replication):**

- Tenant count reaches 50+
- Monthly revenue exceeds $15,000
- Any Enterprise customer signs an SLA requiring 99.99% uptime
- Any region outage lasting >2 hours is experienced

**Option C components:**

| Component | Change |
|-----------|--------|
| Cosmos DB | Enable multi-region writes (East US 2 + Central US) |
| Container Apps | Deploy to both regions with Azure Front Door |
| Blob Storage | GRS replication (instead of LRS) |
| Application Gateway | Replace with Azure Front Door (global load balancing) |
| Key Vault | Premium SKU with HSM-backed keys |
| ACR | Premium with geo-replication |

**Estimated monthly cost increase:** ~$200-400/month (Cosmos DB multi-region writes + Front Door + GRS storage).

---

## 4. Maintenance Procedure (WI #150)

### 4.1 Maintenance Window

| Attribute | Value |
|-----------|-------|
| Day | Tuesdays |
| Time | 02:00 -- 04:00 UTC |
| Duration | 2 hours maximum |
| Frequency | As needed (not weekly) |

### 4.2 Notification Schedule

| When | Action | Channel |
|------|--------|---------|
| T-72 hours | Send advance notice with scope and expected impact | Email to affected tenants, status page |
| T-24 hours | Send reminder with confirmed window | Email to affected tenants, status page |
| T-1 hour | Post start notice | Status page |
| T+0 (start) | Begin maintenance | Status page updated to "In Progress" |
| T+completion | Post completion notice | Email to all tenants, status page |

**Notification template (72-hour advance):**

```
Subject: Scheduled Maintenance — Agent Red Customer Experience

Scheduled maintenance window:
  Date: Tuesday, [DATE]
  Time: 02:00 — 04:00 UTC
  Expected impact: [Brief description, e.g., "Brief interruptions to API
    responses during container updates. Active conversations may experience
    1-2 second delays."]

What we are doing:
  [Description of maintenance work]

What you need to do:
  No action required. Active chat sessions will be preserved.

Questions? Contact support@remakerdigital.com
```

### 4.3 Planned Maintenance Types

#### Type A: Container Image Update (Most Common)

Infrastructure updates, dependency patches, minor feature releases.

```bash
# Follow the full deployment procedure (Section 2).
# Rolling updates cause zero downtime for most container updates.
# API Gateway deployment last to minimize external-facing disruption.
```

#### Type B: Cosmos DB Maintenance

Index changes, collection configuration updates, throughput adjustments.

```bash
# 1. Verify current Cosmos DB metrics
az cosmosdb sql database show \
  --account-name cosmos-agntcy-cs-prod-rc6vcp \
  --resource-group agntcy-prod-rg \
  --name agent-red-prod \
  --output table

# 2. Index updates are performed online -- no downtime.
#    New composite indexes build asynchronously.
#    Monitor progress via Azure portal > Cosmos DB > Indexing Progress.

# 3. Collection creation is online -- no downtime.
#    New collections are immediately available.

# 4. Vector index (DiskANN) changes require reindexing.
#    Schedule during maintenance window due to RU consumption spike.
```

#### Type C: NATS JetStream Maintenance

Stream configuration changes, NATS version upgrades.

```bash
# NATS upgrades require rolling restart of NATS replicas.
# NATS JetStream with 2 replicas supports rolling restart:

# 1. Update NATS image tag
az containerapp update \
  --name agent-red-nats \
  --resource-group agntcy-prod-rg \
  --image "acragntcycsprodrc6vcp.azurecr.io/nats:2.11-alpine"

# 2. NATS consumers reconnect automatically (nats-py client).
#    TenantNATSManager has built-in reconnection with circuit breaker.
#    Messages queued in JetStream are redelivered after reconnection.

# 3. Verify NATS health
curl -s https://20.110.214.55/ready | python -m json.tool | grep -A5 nats
```

#### Type D: Terraform Infrastructure Changes

Scaling adjustments, networking changes, new Azure resources.

```bash
cd infrastructure/terraform

# 1. Plan changes
terraform plan -var-file="production.tfvars" -out=maintenance.tfplan

# 2. Review the plan -- NO unexpected destroys
# 3. Apply during maintenance window
terraform apply maintenance.tfplan

# 4. Clean up
rm maintenance.tfplan
```

#### Type E: Key Vault Secret Rotation

API keys, connection strings, or certificate rotation.

```bash
# 1. Secrets are rotated via Azure CLI or portal
az keyvault secret set \
  --vault-name kv-agntcy-cs-prod-rc6vcp \
  --name "<secret-name>" \
  --value "<new-value>"

# 2. TenantSecretService cache TTL is 5 minutes.
#    Containers will pick up new secrets within 5 minutes.
#    No restart required.

# 3. CMK auto-rotation is handled by Key Vault (90-day cycle).
#    No manual intervention needed for encryption key rotation.
```

### 4.4 Unplanned Maintenance (Emergency Fixes)

For issues that cannot wait for the scheduled window. Follow the Hotfix Procedure (Section 2.6) with these additions:

1. Post an immediate status update: "Unplanned maintenance in progress."
2. Do not wait for the 72-hour notification cycle.
3. Apply the minimal fix required to restore service.
4. Complete the full fix in the next scheduled maintenance window.
5. Post a post-incident report within 24 hours.

### 4.5 Rollback Criteria

Abort the maintenance and roll back if ANY of the following conditions occur during or within 15 minutes after the maintenance:

| Condition | Threshold | Detection |
|-----------|-----------|-----------|
| Error rate spike | > 5% of requests returning 5xx | Application Insights |
| Latency spike | P95 > 3x baseline (> 6,000ms) | Application Insights |
| Tenant reports | > 1 tenant reporting issues | Support channel |
| Container restarts | Any critical container restarting > 2 times | Container App logs |
| Circuit breaker | Any circuit breaker stuck in OPEN for > 2 minutes | `/ready` endpoint |
| NATS disconnection | NATS showing disconnected for > 1 minute | `/ready` endpoint |
| Critic unavailable | Critic/Supervisor failing health checks | `/ready` endpoint |

**Automated monitoring during maintenance:**

```bash
# Run this in a loop during maintenance to monitor health
while true; do
  echo "=== $(date -u +%H:%M:%S) ==="

  # Health check
  HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://20.110.214.55/health)
  echo "Health: ${HEALTH}"

  # Readiness check (extract key fields)
  READY=$(curl -s https://20.110.214.55/ready)
  echo "Ready: $(echo ${READY} | python -c "
import json, sys
d = json.load(sys.stdin)
nats = d.get('nats', {}).get('connected', False)
breakers = d.get('circuit_breakers', {})
open_breakers = [k for k,v in breakers.items() if v == 'OPEN']
print(f'NATS={nats}, OpenBreakers={open_breakers or \"none\"}')" 2>/dev/null || echo "UNREACHABLE")"

  # Error rate from App Insights (requires az CLI auth)
  # az monitor app-insights query ...

  sleep 15
done
```

### 4.6 Post-Maintenance Validation Checklist

Complete every item after maintenance concludes. Do not close the maintenance window until all items pass.

```
[ ] /health returns 200 with correct version
[ ] /ready returns 200 with all dependencies connected
[ ] NATS connected with expected active streams
[ ] All circuit breakers in CLOSED state
[ ] Key Vault health check passing
[ ] Usage monitor health check passing
[ ] SSE connection manager health check passing
[ ] Error rate < 1% over 5 minutes (Application Insights)
[ ] P95 latency < 2,000ms over 5 minutes (Application Insights)
[ ] All 9 containers running with 0 restarts since maintenance
[ ] Spot-check: API request succeeds with test tenant API key
[ ] Status page updated to "Operational"
[ ] Completion notification sent to affected tenants
```

```bash
# Automated post-maintenance validation script
export GW_IP="20.110.214.55"
export RG="agntcy-prod-rg"

echo "=== Post-Maintenance Validation ==="

# Health
echo -n "1. Health endpoint: "
curl -sf https://${GW_IP}/health > /dev/null && echo "PASS" || echo "FAIL"

# Readiness
echo -n "2. Readiness endpoint: "
curl -sf https://${GW_IP}/ready > /dev/null && echo "PASS" || echo "FAIL"

# Container status
echo "3. Container status:"
az containerapp list \
  --resource-group ${RG} \
  --output table \
  --query "[].{Name:name, Status:properties.runningStatus}" 2>/dev/null

# Detailed readiness
echo "4. Dependency health:"
curl -s https://${GW_IP}/ready | python -m json.tool 2>/dev/null

echo "=== Validation Complete ==="
```

---

## 5. Contact Information

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| On-Call Engineer | _TBD_ | _TBD_ | First responder |
| Engineering Lead | _TBD_ | _TBD_ | Escalation for rollback decisions |
| Product Owner | _TBD_ | _TBD_ | Customer communication approval |
| Azure Support | Microsoft | Azure Support Portal | Severity A for production outages |

**Escalation path:**

1. On-call engineer assesses the situation (0-15 minutes).
2. If rollback is needed, on-call engineer executes without waiting for approval.
3. If data loss or extended outage, escalate to Engineering Lead (15-30 minutes).
4. If customer-facing impact > 30 minutes, escalate to Product Owner for communication.
5. For Azure platform issues, open Azure Support ticket (Severity A for full outage, Severity B for degraded service).

---

## 6. Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-02-01 | 1.0.0 | Initial | Deployment, DR (Option A), Maintenance procedures |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
