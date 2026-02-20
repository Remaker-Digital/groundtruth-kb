# Tenant Isolation Verification Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (30 passed, 0 failed — PASS)
# Last corrected: 2026-02-19 (nested config response, KB articles key, rate limit retry)

This procedure validates that the Agent Red multi-tenant architecture enforces strict data isolation between tenants at the API level. It uses two live tenants (remaker-digital-001 and test-customer-001) to verify that credentials from one tenant cannot access another tenant's data.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** pytest + httpx (same as regression suite).
> **Test code:** `tests/security/test_tenant_isolation_live.py` (created by this procedure).

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
TEST_FILE           = tests/security/test_tenant_isolation_live.py

# Tenant A: Primary production tenant
TENANT_A_ID         = remaker-digital-001
TENANT_A_API_KEY    = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
TENANT_A_WIDGET_KEY = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)

# Tenant B: Simulated customer tenant
TENANT_B_ID         = test-customer-001
TENANT_B_API_KEY    = (from logs/test_tenant_credentials.json superadmin_key; rotates on every re-seed)
TENANT_B_WIDGET_KEY = (from logs/test_tenant_credentials.json widget_key; rotates on every re-seed)

# Expected test counts
EXPECTED_PASS       = 30
EXPECTED_FAILURES   = 0
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] pytest + httpx installed                   — python -m pytest --version && python -c "import httpx"
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] Tenant A credentials valid                 — curl -H "X-API-Key: $TENANT_A_API_KEY" $PROD_URL/api/config → 200
[ ] Tenant B credentials valid                 — curl -H "X-API-Key: $TENANT_B_API_KEY" $PROD_URL/api/config → 200
[ ] Tenant A has data (conversations, KB, team) — confirmed via admin UI or API
[ ] Tenant B has data (conversations, KB, team) — confirmed via admin UI or API
[ ] Test file exists                           — ls $TEST_FILE
```

**Rule:** Both tenants must have data for cross-access tests to be meaningful. If either tenant is empty, run `seed_tenant.py` (Tenant A) or `create_test_tenant.py` (Tenant B) first.

---

## Test Categories

The procedure tests 6 isolation boundaries, each from both directions (A→B and B→A):

### Category 1: API Key Scoping (4 tests)
- Tenant A's API key used against Tenant B's known endpoints → 401 or returns only Tenant A's data
- Tenant B's API key used against Tenant A's known endpoints → 401 or returns only Tenant B's data
- Invalid API key → 401
- Missing API key on protected endpoint → 401

### Category 2: Widget Key Scoping (4 tests)
- Tenant A's widget key used to start chat → returns Tenant A's config
- Tenant B's widget key used to start chat → returns Tenant B's config
- Tenant A's widget key cannot access Tenant B's conversations
- Invalid widget key → 401

### Category 3: Conversation Isolation (6 tests)
- Tenant A lists conversations with own API key → sees only own conversations
- Tenant B lists conversations with own API key → sees only own conversations
- Tenant A's API key with Tenant B's conversation ID → 404 (not 403, to avoid ID enumeration)
- Tenant B's API key with Tenant A's conversation ID → 404
- Tenant A's conversation count matches expected (≥1)
- Tenant B's conversation count matches expected (≥1)

### Category 4: Knowledge Base Isolation (4 tests)
- Tenant A lists KB articles → sees only own articles
- Tenant B lists KB articles → sees only own articles
- Tenant A's API key with Tenant B's KB document ID → 404
- Tenant B's API key with Tenant A's KB document ID → 404

### Category 5: Team Member Isolation (4 tests)
- Tenant A lists team members → sees only own team
- Tenant B lists team members → sees only own team
- Tenant A's team member count matches expected
- Tenant B's team member count matches expected (9 per test-customer-001 spec)

### Category 6: Configuration Isolation (4 tests)
- Tenant A reads config → returns own brand_name, widget_key
- Tenant B reads config → returns own brand_name, widget_key
- Config widget_key for Tenant A ≠ Config widget_key for Tenant B
- Config tenant_id matches the authenticated tenant (no cross-leak)

### Category 7: IDOR Prevention (4 tests)
- Tenant A's API key + manipulated tenant_id parameter → rejected or returns own data only
- Direct URL path with Tenant B's ID using Tenant A's key → 404 or 403
- Conversation ID from Tenant B embedded in Tenant A's API call → 404
- KB document ID from Tenant B embedded in Tenant A's API call → 404

---

## Steps

### Step 1: Verify both tenants are accessible

```
ACTION:    PROD_URL=$PROD_URL python -c "
           import httpx, os
           url = os.environ['PROD_URL']
           # Load .env.local
           from scripts._env import load_env_local
           load_env_local()
           key_a = os.environ.get('SUPERADMIN_PREVIEW_API_KEY', '')
           resp_a = httpx.get(f'{url}/api/config', headers={'X-API-Key': key_a}, timeout=10)
           print(f'Tenant A: {resp_a.status_code}')
           # Tenant B key from credentials file
           import json
           creds = json.load(open('logs/test_tenant_credentials.json'))
           key_b = creds['superadmin_key']
           resp_b = httpx.get(f'{url}/api/config', headers={'X-API-Key': key_b}, timeout=10)
           print(f'Tenant B: {resp_b.status_code}')
           "

EXPECTED:  Tenant A: 200
           Tenant B: 200
VERIFY:    Both status codes are 200
ON FAIL:   If 401: credentials are stale. Re-seed the affected tenant.
           If 503: production is unhealthy. Abort.
```

### Step 2: Run tenant isolation test suite

```
ACTION:    PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=short -x

EXPECTED:  $EXPECTED_PASS passed, 0 failed
VERIFY:    Exit code 0
           Summary line: "N passed" where N >= $EXPECTED_PASS
ON FAIL:   Any failure indicates a tenant isolation breach.
           SEVERITY: CRITICAL — do not deploy to production until resolved.
           Record the specific test that failed, the HTTP status code received,
           and the response body.
```

### Step 3: Verify no cross-tenant data leakage in responses

```
ACTION:    Review test output for any response bodies that contain
           the wrong tenant's data:
           - Tenant A's brand_name appearing in Tenant B's response
           - Tenant B's conversation IDs appearing in Tenant A's list
           - Any tenant_id field not matching the authenticated tenant

EXPECTED:  No cross-tenant data in any response
VERIFY:    Test assertions cover this, but manual review of verbose output
           provides additional confidence
ON FAIL:   Cross-tenant data leakage is a CRITICAL security finding.
           Investigate the Cosmos DB partition key enforcement and
           auth middleware tenant_id injection.
```

---

## Postconditions

```
[ ] All $EXPECTED_PASS tests passed, 0 failures
[ ] API key scoping: each key returns only its own tenant's data
[ ] Widget key scoping: each widget key resolves to correct tenant
[ ] Conversation isolation: no cross-tenant conversation access
[ ] Knowledge base isolation: no cross-tenant KB access
[ ] Team member isolation: no cross-tenant team access
[ ] Configuration isolation: config returns correct tenant's settings
[ ] IDOR prevention: manipulated IDs return 404, not other tenant's data
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All tests pass, no cross-tenant data observed |
| **FAIL** | Any test fails — indicates isolation breach. **CRITICAL severity.** |

There is no CONDITIONAL PASS for this procedure. Any failure is a security incident.

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| 401 on valid API key | Environment (stale credentials) | Re-seed tenant, update .env.local and credentials file |
| 503 on all requests | Environment (production unhealthy) | Check /health, wait for recovery, retry |
| Tenant B has no data (empty lists) | Environment (test tenant not seeded) | Run `scripts/create_test_tenant.py --execute` |
| Conversation ID format mismatch | Procedure defect | Update test to use correct ID format from API response |
| Cross-partition query returns data from both tenants | **CRITICAL** procedure finding | Cosmos DB partition key not enforced. Investigate repository layer immediately. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
