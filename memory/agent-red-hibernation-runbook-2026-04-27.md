# Agent Red Hibernation Runbook (Tier 1+ scope)

**Drafted:** 2026-04-27 (S314)
**Scope:** Azure subscription `4dce2122` / resource group `agent-red`
**Pause duration:** ~5 days (resume after GT-KB work completes)
**Author:** Prime Builder (Claude Opus 4.7), reviewed by owner before execution

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## Decision Context (DELIB-shape; lift into Deliberation Archive via `/decision-capture` if formalization desired)

**Decision:** Hibernate Agent Red prod + staging at Tier 1+ scope (Container Apps `minReplicas=0` + diagnostic settings disabled + Cosmos floor) for ~5 days starting 2026-04-27. Redis Cache, Container Registry, Cosmos DB account, and Key Vault remain intact. No deletions of resources that require IaC rebuild.

**Rationale:**
- No commercial users currently; staging has no QA traffic; switching to GT-KB-focused work for ~5 days.
- Status-quo run rate is ~$26.6/day (~$133 over 5 days) per Apr 2026 cost view.
- Tier 1+ recovers ~$100 of $133 with reversal-via-flag-flip safety.
- Tier 2 (delete Redis + test hosts) would save an additional ~$15-20 over 5 days but introduces "trust IaC for clean recreate" risk that has not been validated recently. Marginal savings does not justify marginal risk for a 5-day pause.
- Log Analytics ($192.62 / 25.7% of monthly bill) is the second-largest cost line; addressed by disabling diagnostic settings on Container Apps during hibernation. Retention of already-ingested data continues at ~$1-2/day; not addressed here.

**Rejected alternatives:**
- Tier 2 aggressive hibernation (delete Redis + test hosts): IaC-rebuild risk for $15-20 saved.
- Tier 3 full teardown: weeks-long pause threshold, not 5 days.
- Status quo (no action): forfeits ~$100 in known savings.

**Reversal owner:** owner runs the `Phase 4 — Resume` commands at the end of the pause; runbook includes verification checklist.

**Known risks:**
- ACS SMS toll-free carrier verification (App 346df3eb per `memory/MEMORY.md`) is in-flight. With Container Apps at `minReplicas=0`, an inbound carrier-verification webhook gets a 5-30s cold-start delay but should still succeed. If carrier verification times out aggressively, resume may need to precede expected webhook activity.
- Log Analytics retention continues to bill on already-ingested data; ~$1-2/day during hibernation.
- IaC drift in `infrastructure/terraform/` is NOT validated by this plan (Tier 1+ does not depend on rebuild paths).

---

## Phase 0 — Preconditions (verify before any command runs)

```bash
# Pin the correct subscription context.
az account set --subscription 4dce2122
az account show --query "{id:id, name:name, state:state}" -o table
# Expected: id == 4dce2122; state == Enabled

# Confirm the resource group exists and lists expected resource types.
az group show --name agent-red --query "{name:name, location:location, state:properties.provisioningState}" -o table
# Expected: name == agent-red; state == Succeeded

# Inventory: how many Container Apps?
az containerapp list --resource-group agent-red --query "length(@)" -o tsv
# Expected: a positive integer (per MEMORY.md "8/8 containers healthy"). Capture for later comparison.

# Inventory: Cosmos accounts, Redis caches, Log Analytics workspaces, Container Registry.
az cosmosdb list --resource-group agent-red --query "[].name" -o tsv
az redis list --resource-group agent-red --query "[].name" -o tsv
az monitor log-analytics workspace list --resource-group agent-red --query "[].name" -o tsv
az acr list --resource-group agent-red --query "[].name" -o tsv
```

If any of these return unexpected names or counts, **STOP** and investigate before continuing. The hibernation plan assumes the inventory matches MEMORY.md's "Quick Reference" section.

---

## Phase 1 — Capture pre-hibernation state

The state goes into `memory/agent-red-hibernation-state-2026-04-27.md` (template alongside this runbook). For each command below, capture the output into the matching section of the state file *before* moving to Phase 2.

```bash
# 1.1 — Container Apps full state (saves minReplicas/maxReplicas + image tags)
az containerapp list --resource-group agent-red \
  --query "[].{name:name, minReplicas:properties.template.scale.minReplicas, maxReplicas:properties.template.scale.maxReplicas, image:properties.template.containers[0].image, fqdn:properties.configuration.ingress.fqdn}" \
  -o json > /tmp/containerapps-pre.json
cat /tmp/containerapps-pre.json
# Paste into state file § Container Apps — pre-hibernation state.

# 1.2 — Diagnostic settings (saves the JSON we'll need to re-attach)
APPS=$(az containerapp list --resource-group agent-red --query "[].name" -o tsv)
mkdir -p /tmp/agent-red-diag-settings
for APP in $APPS; do
  RID=$(az containerapp show --resource-group agent-red --name "$APP" --query id -o tsv)
  az monitor diagnostic-settings list --resource "$RID" -o json \
    > "/tmp/agent-red-diag-settings/${APP}.json"
done
ls -la /tmp/agent-red-diag-settings/
# Paste the full file list + per-app JSON sizes into the state file § Diagnostic settings.
# CRITICAL: keep these JSON files for the resume step.

# 1.3 — Cosmos throughput (per database)
COSMOS=$(az cosmosdb list --resource-group agent-red --query "[0].name" -o tsv)
az cosmosdb sql database list --account-name "$COSMOS" --resource-group agent-red \
  --query "[].name" -o tsv > /tmp/cosmos-dbs.txt
for DB in $(cat /tmp/cosmos-dbs.txt); do
  echo "DB: $DB"
  az cosmosdb sql database throughput show --account-name "$COSMOS" --resource-group agent-red --name "$DB" \
    --query "{db:'$DB', current:resource.throughput, autoMaxThroughput:resource.autoscaleSettings.maxThroughput}" -o json
done
# Paste into state file § Cosmos throughput pre-state.

# 1.4 — Redis SKU + version (no scale change planned, but capture for completeness)
REDIS=$(az redis list --resource-group agent-red --query "[0].name" -o tsv)
az redis show --resource-group agent-red --name "$REDIS" \
  --query "{name:name, sku:sku.name, capacity:sku.capacity, family:sku.family, version:redisVersion}" -o table
# Paste into state file § Redis pre-state.

# 1.5 — Log Analytics retention + ingestion cap
LAW=$(az monitor log-analytics workspace list --resource-group agent-red --query "[0].name" -o tsv)
az monitor log-analytics workspace show --resource-group agent-red --workspace-name "$LAW" \
  --query "{name:name, retentionInDays:retentionInDays, dailyQuotaGb:workspaceCapping.dailyQuotaGb}" -o table
# Paste into state file § Log Analytics pre-state.

# 1.6 — Cost baseline screenshot (Azure Portal → Cost analysis → save current view)
# Attach to state file § Cost baseline screenshot.
```

**Verification gate**: every section of `memory/agent-red-hibernation-state-2026-04-27.md` is filled in, OR you have explicitly noted "n/a — no resource of this type." Do NOT proceed to Phase 2 if any section is blank.

---

## Phase 2 — Hibernate

### 2.1 Container Apps → `minReplicas=0`

```bash
APPS=$(az containerapp list --resource-group agent-red --query "[].name" -o tsv)
for APP in $APPS; do
  echo ">>> Scaling $APP to min=0 max=1"
  az containerapp update --resource-group agent-red --name "$APP" \
    --min-replicas 0 --max-replicas 1
  # Verify after each:
  az containerapp show --resource-group agent-red --name "$APP" \
    --query "{name:name, min:properties.template.scale.minReplicas, max:properties.template.scale.maxReplicas}" \
    -o table
done
```

**Expected outcome:** every app shows `min: 0, max: 1`. Active replicas drop to 0 within a few minutes.

### 2.2 Disable Container Apps diagnostic settings (Log Analytics ingestion stop)

```bash
for APP in $APPS; do
  RID=$(az containerapp show --resource-group agent-red --name "$APP" --query id -o tsv)
  DSNAMES=$(az monitor diagnostic-settings list --resource "$RID" --query "value[].name" -o tsv)
  for DS in $DSNAMES; do
    echo ">>> Removing diagnostic setting '$DS' from '$APP'"
    az monitor diagnostic-settings delete --resource "$RID" --name "$DS"
  done
done
```

**Expected outcome:** subsequent `az monitor diagnostic-settings list --resource <RID>` returns empty `value` array for each app. Ingestion to Log Analytics stops within minutes.

### 2.3 Cosmos to floor RU/s (likely no-op per cost data)

```bash
COSMOS=$(az cosmosdb list --resource-group agent-red --query "[0].name" -o tsv)
for DB in $(cat /tmp/cosmos-dbs.txt); do
  CURRENT=$(az cosmosdb sql database throughput show --account-name "$COSMOS" \
    --resource-group agent-red --name "$DB" --query "resource.throughput" -o tsv 2>/dev/null || echo "serverless")
  echo "DB $DB current: $CURRENT"
  if [ "$CURRENT" != "serverless" ] && [ "$CURRENT" -gt 400 ]; then
    echo ">>> Lowering $DB to 400 RU/s"
    az cosmosdb sql database throughput update --account-name "$COSMOS" \
      --resource-group agent-red --name "$DB" --throughput 400
  else
    echo "DB $DB already at floor or serverless — no change"
  fi
done
```

**Expected outcome:** all databases at 400 RU/s or already serverless. Capture diff in state file.

### 2.4 What deliberately stays running

- **Redis Cache** — kept; ~$3/day for 5 days = $16. Avoids IaC-rebuild dependency.
- **Container Registry** — kept; storage is cheap; preserves deployed image tags for resumption.
- **Key Vault** — kept; per-operation billing, ~$0/day when idle.
- **Cosmos DB account** — kept (only RU/s adjusted).
- **Log Analytics workspace** — kept; only ingestion stopped via diagnostic-setting removal.
- **Public IPs / Front Door / API Management** — kept as-is.

---

## Phase 3 — Verify hibernation took effect

Wait at least **24 hours** after Phase 2 completion, then check the cost trend.

```bash
# Confirm no Container Apps replicas are running.
for APP in $APPS; do
  az containerapp replica list --resource-group agent-red --container-app-name "$APP" \
    --query "length(@)" -o tsv
done
# Expected: 0 for every app (after a few minutes).

# Confirm diagnostic settings still empty.
for APP in $APPS; do
  RID=$(az containerapp show --resource-group agent-red --name "$APP" --query id -o tsv)
  COUNT=$(az monitor diagnostic-settings list --resource "$RID" --query "length(value)" -o tsv)
  echo "$APP diagnostic settings: $COUNT"
done
# Expected: 0 for every app.

# Cost view: open Azure Portal → Cost Management → Cost analysis → scope = agent-red
# The accumulated cost line should bend sharply downward starting on the hibernation day.
# If cost continues at >$10/day after 48h, hibernation did not take — investigate.
```

**Expected daily run-rate after hibernation:** $1-3/day (Redis ~$3, ACR <$1, Log Analytics retention floor ~$1-2, ambient platform <$1).

If the cost line does not bend, **STOP** and investigate before assuming the hibernation worked.

---

## Phase 4 — Resume

Run after GT-KB work completes and Agent Red is needed again.

### 4.1 Restore Container Apps replica counts

Use the values captured in `memory/agent-red-hibernation-state-2026-04-27.md` § Container Apps — pre-hibernation state. The original prod minReplicas was 2, staging was 1 per MEMORY.md, but verify against the captured state for each individual app.

```bash
# For each app, restore to its captured pre-hibernation min/max.
# Read from /tmp/containerapps-pre.json:
for APP in $APPS; do
  PRE_MIN=$(jq -r ".[] | select(.name==\"$APP\") | .minReplicas" /tmp/containerapps-pre.json)
  PRE_MAX=$(jq -r ".[] | select(.name==\"$APP\") | .maxReplicas" /tmp/containerapps-pre.json)
  echo ">>> Restoring $APP to min=$PRE_MIN max=$PRE_MAX"
  az containerapp update --resource-group agent-red --name "$APP" \
    --min-replicas "$PRE_MIN" --max-replicas "$PRE_MAX"
done
```

### 4.2 Restore Cosmos throughput

If Phase 2.3 changed any database, re-set to the captured pre-state value.

```bash
# Per database, check the pre-state file for original throughput; re-set if changed.
for DB in $(cat /tmp/cosmos-dbs.txt); do
  PRE_RU=$(grep -A2 "DB: $DB" /path/to/state-snapshot.md | grep "current:" | awk '{print $2}')
  # OR read from saved JSON. Adjust accordingly.
  if [ -n "$PRE_RU" ] && [ "$PRE_RU" != "400" ]; then
    az cosmosdb sql database throughput update --account-name "$COSMOS" \
      --resource-group agent-red --name "$DB" --throughput "$PRE_RU"
  fi
done
```

### 4.3 Restore diagnostic settings

```bash
for APP in $APPS; do
  RID=$(az containerapp show --resource-group agent-red --name "$APP" --query id -o tsv)
  SAVED="/tmp/agent-red-diag-settings/${APP}.json"
  if [ ! -f "$SAVED" ]; then
    echo "WARN: no saved diagnostic settings for $APP; skip"
    continue
  fi
  # Each saved file has one or more diagnostic settings under .value[].
  # Re-create each one.
  jq -c '.value[]' "$SAVED" | while read -r ENTRY; do
    DS_NAME=$(echo "$ENTRY" | jq -r '.name')
    LAW_ID=$(echo "$ENTRY" | jq -r '.properties.workspaceId')
    LOGS=$(echo "$ENTRY" | jq -c '.properties.logs')
    METRICS=$(echo "$ENTRY" | jq -c '.properties.metrics')
    echo ">>> Re-attaching '$DS_NAME' to '$APP'"
    az monitor diagnostic-settings create \
      --resource "$RID" --name "$DS_NAME" \
      --workspace "$LAW_ID" \
      --logs "$LOGS" \
      --metrics "$METRICS"
  done
done
```

---

## Phase 5 — Resume verification

```bash
# 5.1 — All apps have non-zero minReplicas
for APP in $APPS; do
  CURR_MIN=$(az containerapp show --resource-group agent-red --name "$APP" \
    --query "properties.template.scale.minReplicas" -o tsv)
  echo "$APP minReplicas: $CURR_MIN"
done
# Expected: matches captured pre-state for every app (no zero values).

# 5.2 — Active replicas exist (after warm-up time, ~2-5 min per app)
for APP in $APPS; do
  COUNT=$(az containerapp replica list --resource-group agent-red --container-app-name "$APP" \
    --query "length(@)" -o tsv)
  echo "$APP active replicas: $COUNT"
done
# Expected: COUNT >= captured pre-state minReplicas for every app.

# 5.3 — Diagnostic settings re-attached
for APP in $APPS; do
  RID=$(az containerapp show --resource-group agent-red --name "$APP" --query id -o tsv)
  COUNT=$(az monitor diagnostic-settings list --resource "$RID" --query "length(value)" -o tsv)
  echo "$APP diagnostic settings: $COUNT"
done
# Expected: matches pre-state count.

# 5.4 — Smoke /health on each app's FQDN (read FQDNs from /tmp/containerapps-pre.json)
for FQDN in $(jq -r '.[].fqdn' /tmp/containerapps-pre.json); do
  if [ -n "$FQDN" ]; then
    echo "Checking https://$FQDN/health"
    curl -sSf -o /dev/null -w "%{http_code}\n" "https://$FQDN/health" --max-time 30
  fi
done
# Expected: 200 from every FQDN that exposes a /health endpoint. Cold-start may add 5-30s on first hit.

# 5.5 — Watch cost trend for 48h after resume to confirm it returns to baseline ~$26/day.
# 5.6 — ACS SMS toll-free verification (App 346df3eb): check status manually if pause overlapped a verification step.
```

**Expected outcome:** every app reachable, diagnostic settings attached, cost trend climbs back to status-quo baseline. If any check fails, refer to **Risk Register** below.

---

## Risk Register

| Risk | Likelihood | Detection | Mitigation |
|---|---|---|---|
| Cold-start latency on first request post-resume | high (expected) | Phase 5.4 takes >2s | Warm-up via 2-3 sequential requests; expected behavior, not a defect |
| Diagnostic setting re-attach fails (jq parse mismatch on some apps) | medium | Phase 5.3 shows `0` for any app | Re-attach manually using saved JSON; az monitor diagnostic-settings create accepts inline arguments |
| Container App image tag missing from ACR (someone deleted images during pause) | low | Phase 5.2 shows containers stuck in failed state | Re-deploy via `scripts/deploy.py` with last-known-good tag; ACR is preserved by design |
| Cosmos DB throughput restoration fails (db not at 400 due to pre-existing autoscale) | medium | Phase 4.2 returns "no change needed" but cost stays low | Re-check via `az cosmosdb sql database throughput show`; if autoscale, no manual restore needed |
| ACS toll-free verification timed out during pause | low-medium | ACS console shows verification status changed | Re-submit verification application; not blocking for general resume |
| Log Analytics workspace marked inactive due to no ingestion for 31+ days | low (pause is 5 days, far below threshold) | New Application Insights / KQL queries fail | Inactive workspaces auto-reactivate on first ingestion; no manual action needed |

---

## Out of Scope

- IaC validation (Terraform plan/apply): not required for Tier 1+; would be required for Tier 2+
- Database backups beyond Azure's automatic Cosmos backup: not modified by this runbook
- Network security group changes: none planned
- DNS/CDN modifications: none planned
- Monitor alerts: leave existing alerts in place; the hibernation will trigger some "no replicas" alerts which is expected behavior
- ACR image cleanup: leave alone; storage is cheap and removal during pause risks resume

---

## Lifecycle

1. **Filled-in state snapshot exists** at `memory/agent-red-hibernation-state-2026-04-27.md` — required precondition for execution.
2. **DELIB formalization** (optional): run `/decision-capture` with the Decision Context section above as input; produces a Deliberation Archive record for permanent governance trail.
3. **On confirmed resume + 48h cost-baseline confirmation**: delete `memory/agent-red-hibernation-state-2026-04-27.md` (ephemeral evidence) and consider promoting this runbook to a KB operational_procedure artifact for reuse on future hibernations.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
