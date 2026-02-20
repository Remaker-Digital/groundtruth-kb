# Data Integrity & Backup Verification Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (25 passed, 0 failed — PASS)
# Last corrected: 2026-02-19 (from_cache volatile field, conversationId camelCase key)

This procedure validates that the Agent Red data layer preserves integrity across container restarts, that Cosmos DB backup/restore mechanisms are functional, and that critical data structures survive lifecycle events without corruption.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** Azure CLI (Cosmos DB queries, Container Apps inspection), httpx (API probes), pytest.
> **Test code:** `tests/security/test_data_integrity_live.py` (created by this procedure).

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io

API_KEY_A           = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
API_KEY_B           = (from logs/test_tenant_credentials.json superadmin_key; rotates on every re-seed)

# Azure resources
COSMOS_ACCOUNT      = cosmos-agentred-eastus
COSMOS_DATABASE     = agentred
RESOURCE_GROUP      = Agent-Red
SUBSCRIPTION        = 4dce2122-690a-4654-b531-cc647db62331
CONTAINER_APP       = agent-red-api-gateway

# Cosmos DB containers to verify
CONTAINERS          = tenants, preferences, team_members, conversations, knowledge_base, customer_profiles, quick_actions, analytics_events, audit_log, incidents, alert_rules, alert_history, api_keys, deployment_events, sla_metrics, cost_records, abuse_events, config_store

# Expected counts (minimum per tenant — adjust after data changes)
TENANT_A_ID         = remaker-digital-001
TENANT_B_ID         = test-customer-001
MIN_CONVERSATIONS_A = 1
MIN_CONVERSATIONS_B = 19
MIN_KB_DOCS_B       = 7
MIN_TEAM_MEMBERS_B  = 9

# Expected test counts
EXPECTED_PASS       = 25
EXPECTED_FAILURES   = 0
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] Azure CLI authenticated                    — az account show
[ ] Cosmos DB accessible                       — az cosmosdb show --name $COSMOS_ACCOUNT -g $RESOURCE_GROUP
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] Both tenant API keys valid                 — Both return 200 on /api/config
[ ] Test file exists                           — ls $TEST_FILE
```

---

## Test Categories

### Category 1: Cosmos DB Container Existence & Schema (6 tests)

| ID | Test | Expected |
|----|------|----------|
| DI-01 | All 18 expected Cosmos DB containers exist | az cosmosdb sql container list returns all |
| DI-02 | Each container has a valid partition key configured | Partition key path is non-empty |
| DI-03 | Tenants container has documents for both test tenants | ≥ 2 documents |
| DI-04 | Preferences container has documents for both tenants | ≥ 2 documents |
| DI-05 | Conversations container has expected document count for Tenant B | ≥ $MIN_CONVERSATIONS_B |
| DI-06 | Knowledge base container has expected document count for Tenant B | ≥ $MIN_KB_DOCS_B |

### Category 2: API Data Consistency (7 tests)

These tests verify that API responses match the underlying Cosmos DB state.

| ID | Test | Expected |
|----|------|----------|
| DI-07 | GET /api/config for Tenant A returns valid configuration | brand_name non-empty, widget_key present |
| DI-08 | GET /api/config for Tenant B returns valid configuration | brand_name non-empty, widget_key present |
| DI-09 | GET /api/admin/conversations for Tenant B returns ≥ $MIN_CONVERSATIONS_B | Count matches expected |
| DI-10 | GET /api/admin/knowledge for Tenant B returns ≥ $MIN_KB_DOCS_B | Count matches expected |
| DI-11 | GET /api/team for Tenant B returns ≥ $MIN_TEAM_MEMBERS_B | Count matches expected |
| DI-12 | GET /api/dashboard/usage returns numeric values (no NaN, no null) | Valid numbers in response |
| DI-13 | Conversation list items have required fields (id, status, created_at) | Schema validation |

### Category 3: Data Persistence Across Requests (4 tests)

| ID | Test | Expected |
|----|------|----------|
| DI-14 | Read config, wait 5s, read config again — values identical | No drift between reads |
| DI-15 | List conversations, wait 5s, list again — counts identical | No spontaneous deletion |
| DI-16 | List KB docs, wait 5s, list again — counts identical | No spontaneous deletion |
| DI-17 | List team members, wait 5s, list again — counts identical | No spontaneous deletion |

### Category 4: ConfigState Integrity (4 tests)

| ID | Test | Expected |
|----|------|----------|
| DI-18 | Tenant A config_state is ACTIVE or DRAFT (valid enum) | Valid ConfigState value |
| DI-19 | Tenant B config_state is ACTIVE (test tenant was activated) | ConfigState.ACTIVE |
| DI-20 | Tenant B activated_at is non-null (since config_state is ACTIVE) | ISO 8601 timestamp |
| DI-21 | Config fields match saved values (brand_name matches seed data) | Exact value match |

### Category 5: Backup Verification (4 tests)

| ID | Test | Expected |
|----|------|----------|
| DI-22 | Cosmos DB account has continuous backup policy enabled | Backup policy type = "Continuous" or periodic backup configured |
| DI-23 | Backup retention period ≥ 7 days | Retention meets minimum |
| DI-24 | Cosmos DB account has point-in-time restore capability | PITR feature available |
| DI-25 | Last backup timestamp is within 24 hours (if periodic) | Recent backup confirmed |

---

## Steps

### Step 1: Verify Cosmos DB infrastructure

```
ACTION:    az cosmosdb sql database show --account-name $COSMOS_ACCOUNT -g $RESOURCE_GROUP --name $COSMOS_DATABASE -o json
           az cosmosdb sql container list --account-name $COSMOS_ACCOUNT -g $RESOURCE_GROUP --database-name $COSMOS_DATABASE --query "[].name" -o tsv

EXPECTED:  Database exists
           All 18 containers listed
VERIFY:    Container count ≥ 18
           All expected container names present
ON FAIL:   Missing containers indicate incomplete deployment or database migration failure.
           Check deployment logs.
```

### Step 2: Run the data integrity test suite

```
ACTION:    PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=short

EXPECTED:  $EXPECTED_PASS passed, 0 failed
VERIFY:    Exit code 0
ON FAIL:   Classify failure:
           - Missing documents → data loss (CRITICAL)
           - Schema validation failure → migration or code regression
           - Count mismatch → data was modified outside normal operations
           - ConfigState invalid → activation model bug
```

### Step 3: Verify backup configuration

```
ACTION:    az cosmosdb show --name $COSMOS_ACCOUNT -g $RESOURCE_GROUP --query "backupPolicy" -o json

EXPECTED:  Backup policy shows:
           - type: "Continuous" or "Periodic"
           - If Periodic: intervalInMinutes ≤ 240 (4 hours), retentionIntervalInHours ≥ 168 (7 days)
           - If Continuous: tier "Continuous7Days" or "Continuous30Days"
VERIFY:    Parse JSON output for backup policy fields
ON FAIL:   If no backup policy → CRITICAL finding. Data is not backed up.
           Configure backup via Azure Portal or az cosmosdb update.
```

### Step 4: Verify data consistency between API and direct Cosmos query

```
ACTION:    Compare API response counts with direct Cosmos DB queries:

           # API count
           curl -s -H "X-API-Key: $API_KEY_B" $PROD_URL/api/admin/conversations | python -c "import sys,json; d=json.load(sys.stdin); print(f'API conversations: {len(d.get(\"conversations\", d.get(\"items\", [])))}')"

           # Direct Cosmos count (requires az cosmosdb sql query or Data Explorer)
           az cosmosdb sql query -a $COSMOS_ACCOUNT -g $RESOURCE_GROUP -d $COSMOS_DATABASE -c conversations --query-text "SELECT VALUE COUNT(1) FROM c WHERE c.tenant_id = 'test-customer-001'" -o json

EXPECTED:  Counts match between API and direct query
VERIFY:    API count == Cosmos count (within ±1 for eventual consistency)
ON FAIL:   Mismatch indicates either:
           - API is filtering documents the query doesn't (check API logic)
           - Cosmos has orphaned documents (check partition key)
           - Eventual consistency delay (retry after 5s)
```

---

## Postconditions

```
[ ] All 18 Cosmos DB containers exist
[ ] All $EXPECTED_PASS tests passed, 0 failures
[ ] Document counts match expected minimums for both tenants
[ ] API responses consistent with Cosmos DB state
[ ] ConfigState values valid for both tenants
[ ] Data persists identically across sequential reads
[ ] Backup policy configured with ≥ 7 day retention
[ ] No data loss or corruption detected
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All tests pass, backup configured, data consistent |
| **CONDITIONAL PASS** | All API tests pass, but backup policy is periodic (not continuous) with < 30 day retention |
| **FAIL** | Document counts below minimum (data loss), ConfigState invalid, no backup policy, or API/Cosmos count mismatch |

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| az cosmosdb sql query times out | Environment transient | Cosmos DB serverless has cold start latency. Retry after 30s. |
| Container count < 18 | Code gap or deployment failure | Check which container is missing. May need migration script. |
| Document count dropped below minimum | **CRITICAL** data loss | Investigate audit log for delete operations. Check TTL policies. |
| Backup policy not found | **CRITICAL** configuration gap | Configure backup immediately via Azure Portal. |
| ConfigState is null or unknown value | Code gap | Pydantic model not enforcing enum validation. Fix schema. |
| API returns different count than Cosmos | Code gap or consistency issue | Check API query filter logic. May be filtering by status or TTL. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
