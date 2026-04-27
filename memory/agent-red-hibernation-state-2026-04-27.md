# Agent Red Hibernation Pre-State Snapshot

**Captured:** 2026-04-27 (S314)
**Subscription:** `4dce2122-690a-4654-b531-cc647db62331` ("Azure subscription 1")
**Tenant:** `4076316e-fe40-4837-b9dc-c60d3fdcd9bf`
**Resource group:** `Agent-Red` (note canonical case)
**Companion runbook:** `memory/agent-red-hibernation-runbook-2026-04-27.md`
**State storage directory:** `C:/temp/agent-red-hibernation/` (durable across the pause)
**Lifetime:** ephemeral — delete on confirmed resume + 48h cost baseline restoration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## Execution Notes (deviations from companion runbook discovered during Phase 0+1)

The original runbook was drafted before Phase 0+1 inventory. Three findings simplify the actual execution:

1. **Cosmos is serverless** (capability `EnableServerless`). Phase 2.3 (scale to floor RU/s) is a **no-op** — serverless bills per consumed RU, not provisioned RU/s. Skip Phase 2.3 entirely. No mutation needed.

2. **Container Apps have no per-app diagnostic settings.** Logs flow through the Container Apps Environment's `appLogsConfiguration` (env: `agent-red-env`, target workspace: `workspace-gentedTYtR` / customerId `7250a88e-e806-4bde-9697-000822f75181`). The runbook's Phase 2.2 "disable per-app diagnostic settings" step **does not apply** and is replaced by either (a) doing nothing — scaling all apps to 0 stops log generation, OR (b) optional belt-and-suspenders: set daily ingestion cap on `workspace-gentedTYtR` to 0.023 GB (the minimum permitted). Owner can choose; (a) is sufficient for 5-day pause given retention is at the 30-day included floor.

3. **Container Apps current minReplicas is 1, not 2** (MEMORY.md said "2"; the live state shows 1 for all 13 apps). MEMORY.md is stale. Resume restores to `minReplicas=1` per the captured state, not `2`.

**Net Phase 2 plan (simplified):**
- 2.1: All 13 Container Apps → `--min-replicas 0 --max-replicas 1` (kept max=1 to ensure no warm-replica drift on resume)
- 2.2 (optional): `workspace-gentedTYtR` daily cap to 0.023 GB
- 2.3: SKIPPED (Cosmos serverless)

---

## Section 0 — Subscription + RG context

```
Subscription ID:   4dce2122-690a-4654-b531-cc647db62331
Subscription name: Azure subscription 1
State:             Enabled
```

```
RG name:        Agent-Red
RG location:    eastus
RG state:       Succeeded
```

Container Apps count: **13**
Cosmos accounts in RG: `cosmos-agentred-eastus` (1)
Redis caches in RG: `redis-agentred-eastus` (1)
Log Analytics workspaces in RG: `workspace-gentedTYtR`, `agent-red-logs` (2)
Container Registries in RG: `acragentredeastus` (1)

---

## Section 1.1 — Container Apps pre-hibernation state

Saved JSON: `C:/temp/agent-red-hibernation/containerapps-pre.json`

| # | App name | minReplicas | maxReplicas | Image | FQDN |
|---|---|---|---|---|---|
| 1 | agent-red-staging | 1 | 3 | api-gateway:v1.98.92 | agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io |
| 2 | agent-red-nats | 1 | 1 | nats:2.10-alpine | agent-red-nats.internal.orangeglacier-f566a4e7.eastus.azurecontainerapps.io |
| 3 | agent-red-intent-classifier | 1 | 3 | agent-intent-classifier:v1.98.92 | agent-red-intent-classifier.internal... |
| 4 | agent-red-knowledge-retrieval | 1 | 3 | agent-knowledge-retrieval:v1.98.92 | agent-red-knowledge-retrieval.internal... |
| 5 | agent-red-response-generator | 1 | 3 | agent-response-generator:v1.98.92 | agent-red-response-generator.internal... |
| 6 | agent-red-escalation-handler | 1 | 3 | agent-escalation-handler:v1.98.92 | agent-red-escalation-handler.internal... |
| 7 | agent-red-analytics-collector | 1 | 3 | agent-analytics-collector:v1.98.92 | agent-red-analytics-collector.internal... |
| 8 | agent-red-critic-supervisor | 1 | 3 | agent-critic-supervisor:v1.98.92 | agent-red-critic-supervisor.internal... |
| 9 | agent-red-co-pilot | 1 | 3 | api-gateway:v1.86.0 | agent-red-co-pilot.internal... |
| 10 | agent-red-slim | 1 | 1 | slim-gateway:v1.98.92 | agent-red-slim.internal... |
| 11 | agent-red-test-host | 1 | 1 | test-host:v1.98.92 | agent-red-test-host.internal... |
| 12 | agent-red-test-host-prod | 1 | 1 | test-host:v1.98.92 | agent-red-test-host-prod.internal... |
| 13 | agent-red-api-gateway | 1 | (per JSON) | api-gateway:v1.98.92 | agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io |

All apps in single environment: `agent-red-env`.

**Resume action:** restore each app to its captured `minReplicas=1` and original `maxReplicas` per saved JSON.

---

## Section 1.2 — Container Apps Environment logging config

Env name: `agent-red-env`
Env location: `East US`

```json
{
  "appLogs": {
    "destination": "log-analytics",
    "logAnalyticsConfiguration": {
      "customerId": "7250a88e-e806-4bde-9697-000822f75181",
      "sharedKey": null
    }
  }
}
```

**Mapped target workspace:** `workspace-gentedTYtR` (customerId match).

Per-app diagnostic settings: **none exist** (HTTP 400 from `az monitor diagnostic-settings list` — Container Apps don't support that resource type for individual apps; env-level config is the only logging mechanism).

**Hibernation action for env logging config:** none. Stays attached. Logs simply stop generating because apps will be at 0 replicas.

---

## Section 1.3 — Cosmos pre-state

Account: `cosmos-agentred-eastus`
Kind: `GlobalDocumentDB`
Capabilities: `EnableServerless`, `EnableNoSQLVectorSearch`
Locations: `East US` only
Provisioning state: `Succeeded`

Databases:
- `agentred-staging`
- `agentred`

**Throughput show:** failed with `BadRequest: Reading or replacing offers is not supported for serverless accounts.` This is **expected and correct for serverless** — there are no provisioned RU/s to capture or change.

**Hibernation action for Cosmos:** none. Serverless bills per consumed RU; when no traffic flows (apps at 0 replicas), Cosmos cost approaches zero automatically. Phase 2.3 of original runbook = **NO-OP, SKIPPED**.

---

## Section 1.4 — Redis pre-state

```json
{
  "name": "redis-agentred-eastus",
  "sku": "Standard",
  "capacity": 1,
  "family": "C",
  "version": "6.0",
  "hostName": "redis-agentred-eastus.redis.cache.windows.net",
  "sslPort": 6380,
  "provisioningState": "Succeeded"
}
```

SKU = Standard C1 (1 GB Standard tier, hourly billed at ~$0.10/hr → ~$2.40/day → ~$72/month).

**Hibernation action for Redis:** none. Cache stays running per Tier 1+ plan (~$12 over 5 days; avoids IaC-rebuild dependency for Tier 2 deletion).

---

## Section 1.5 — Log Analytics pre-state

### Workspace `agent-red-logs` (NOT used by Container Apps env)

```json
{
  "name": "agent-red-logs",
  "customerId": "47aa64ec-703f-49ef-96d3-0b1bed143559",
  "retentionInDays": 30,
  "dailyQuotaGb": -1.0,
  "sku": "PerGB2018"
}
```

`dailyQuotaGb = -1.0` means **no daily cap** (unlimited ingestion).
`retentionInDays = 30` is the included floor for PerGB2018; **no retention overage billing**.

### Workspace `workspace-gentedTYtR` (Container Apps env logs target)

```json
{
  "name": "workspace-gentedTYtR",
  "customerId": "7250a88e-e806-4bde-9697-000822f75181",
  "retentionInDays": 30,
  "dailyQuotaGb": -1.0,
  "sku": "PerGB2018"
}
```

Same shape: no daily cap, 30-day retention floor.

**Hibernation action for Log Analytics:**
- **Required:** none. With Container Apps at 0 replicas, log volume → 0; ingestion charge → 0; retention is at floor.
- **Optional (belt-and-suspenders):** set `workspace-gentedTYtR` daily cap to `0.023` GB during hibernation. Reversal: `--quota -1`. This is the minimum permitted cap; effectively throttles any stray ingestion to <23 MB/day. Cost: zero.

Owner choice: do nothing (sufficient) OR add the optional cap (zero-cost insurance). Recommendation: **add the optional cap** — it's a single command, fully reversible, and protects against future apps in the env being added without the operator realizing.

---

## Section 1.6 — Cost baseline (from Apr 2026 cost view, captured 2026-04-27)

**Subscription scope: 4dce2122 (Azure subscription 1)**

Apr-to-date through Apr 27: $747.41
April forecast (full month): $846.00
Daily average: ~$27.68/day

**Per-service breakdown** (subscription scope, Apr 2026):

| Service | Apr-to-date $ | % of total | Notes |
|---|---|---|---|
| Azure Container Apps | $409.31 | 54.7% | Primary hibernation target |
| Log Analytics | $192.62 | 25.7% | Drops to ~0 when no replicas generate logs |
| Redis Cache | $87.08 | 11.6% | Kept running per Tier 1+ |
| Container Registry | $24.76 | 3.3% | Not modified |
| (Other Microsoft purchases) | $29.00 | 3.9% | Personal subscription fee, NOT Agent Red |
| Cosmos DB + remainder | ~$5 | <1% | Already serverless; no change |

**Per-RG breakdown** (Apr 2026):

| Resource group | Apr-to-date $ |
|---|---|
| `agent-red` (RG) | $718.41 |
| Other Microsoft purchases (subscription fee) | $29.00 |

The agent-red RG is 96.1% of the bill; remainder is a recurring personal subscription fee not relevant to this hibernation.

---

## Section 2 — Hibernate execution log

**Owner approval:** "Execute 2.1 + 2.2 (Recommended)" via AskUserQuestion at S314.
**Execution log:** `C:/temp/agent-red-hibernation/phase2-execution-log.txt`

### 2.1 Container Apps scaling — COMPLETED 2026-04-27T14:41:00Z → 14:45:11Z (4m 11s)

All 13 apps scaled to `min=0, max=1` and immediately verified post-update.

| Timestamp (UTC) | App name | Pre min/max | Post min/max | Immediate verify |
|---|---|---|---|---|
| 14:41:04 | agent-red-staging | 1/3 | 0/1 | 0/1 ✓ |
| 14:41:26 | agent-red-nats | 1/1 | 0/1 | 0/1 ✓ |
| 14:41:45 | agent-red-intent-classifier | 1/3 | 0/1 | 0/1 ✓ |
| 14:42:05 | agent-red-knowledge-retrieval | 1/3 | 0/1 | 0/1 ✓ |
| 14:42:23 | agent-red-response-generator | 1/3 | 0/1 | 0/1 ✓ |
| 14:42:43 | agent-red-escalation-handler | 1/3 | 0/1 | 0/1 ✓ |
| 14:43:00 | agent-red-analytics-collector | 1/3 | 0/1 | 0/1 ✓ |
| 14:43:20 | agent-red-critic-supervisor | 1/3 | 0/1 | 0/1 ✓ |
| 14:43:39 | agent-red-co-pilot | 1/3 | 0/1 | 0/1 ✓ |
| 14:43:58 | agent-red-slim | 1/1 | 0/1 | 0/1 ✓ |
| 14:44:17 | agent-red-test-host | 1/1 | 0/1 | 0/1 ✓ |
| 14:44:35 | agent-red-test-host-prod | 1/1 | 0/1 | 0/1 ✓ |
| 14:44:52 | agent-red-api-gateway | 1/3 | 0/1 | 0/1 ✓ |

### 2.2 Daily cap on `workspace-gentedTYtR` — COMPLETED 2026-04-27T14:45:22Z → 14:46:00Z

| Timestamp (UTC) | Pre dailyQuotaGb | Post dailyQuotaGb |
|---|---|---|
| 14:45:22 | -1.0 (unlimited) | 0.023 |

### 2.3 Cosmos throughput change

**SKIPPED** — Cosmos is serverless; no provisioned RU/s to scale.

---

## Section 3 — 24h post-hibernation cost confirmation

| Day | Daily cost | Notes |
|---|---|---|
| Day 0 (hibernate day, 2026-04-27) | $[?] | partial day; expect status quo first half, drop after |
| Day 1 (2026-04-28) | $[?] | first full hibernation day; expected $1-3 |
| Day 2 (2026-04-29) | $[?] | confirm trend; expected $1-3 |
| Day 3 (2026-04-30) | $[?] | |
| Day 4 (2026-05-01) | $[?] | |
| Day 5 (resume day) | $[?] | partial day; ramps back |

**If Day 1 cost > $10**, hibernation did NOT take effect — investigate per Risk Register before continuing the pause.

---

## Section 4 — Resume execution log

(Filled in DURING Phase 4 execution.)

### 4.1 Container Apps replica restoration (target: each app's captured pre-state min/max)

| Timestamp (UTC) | App name | Restored min/max | Active replicas after 5 min |
|---|---|---|---|
| | | | |

### 4.2 Optional cap removal on `workspace-gentedTYtR`

| Timestamp (UTC) | Restored dailyQuotaGb (target: -1.0) |
|---|---|
| | |

### 4.3 Smoke /health checks

| App FQDN | HTTP status | Latency (s) | Notes |
|---|---|---|---|
| agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io | | | |
| agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io | | | |

(Internal apps have no public FQDN; verified via prod gateway responding correctly.)

---

## Section 5 — Resume signoff

- [ ] All Container Apps active replicas match pre-hibernation state (minReplicas=1, original maxReplicas)
- [ ] Optional cap removed from `workspace-gentedTYtR` (back to `-1.0`) if applied
- [ ] All public FQDNs return 200 on /health (or N/A if no /health endpoint)
- [ ] 48h post-resume cost trend climbs back to ~$26/day baseline
- [ ] ACS SMS toll-free verification status checked (App 346df3eb)
- [ ] No unexpected errors in Log Analytics during resume window

**Owner signoff:** _________ **Date:** _________

**Action on signoff:** delete this file (ephemeral evidence). The runbook itself stays for future reuse.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
