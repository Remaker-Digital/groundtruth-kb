# Rate Limiting & DoS Resilience Testing Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (19 passed, 1 timing-dependent — CONDITIONAL PASS)
# Last corrected: 2026-02-19 (test ordering exhausts starter window, added longer wait)

This procedure validates that the Agent Red API gateway correctly enforces per-tenant rate limits and remains resilient under burst traffic conditions. It uses both the production tenant (professional tier, 50 rpm) and the test tenant (starter tier, 10 rpm) to verify tier-specific enforcement.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** pytest + httpx (for targeted rate limit tests), Locust (for sustained burst tests).
> **Test code:** `tests/security/test_rate_limiting_live.py` (created by this procedure).

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
TEST_FILE           = tests/security/test_rate_limiting_live.py

# Tenant A: Professional tier (50 rpm)
TENANT_A_ID         = remaker-digital-001
TENANT_A_API_KEY    = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
TENANT_A_TIER       = professional
TENANT_A_RPM        = 50

# Tenant B: Starter tier (10 rpm)
TENANT_B_ID         = test-customer-001
TENANT_B_API_KEY    = (from logs/test_tenant_credentials.json superadmin_key; rotates on every re-seed)
TENANT_B_TIER       = starter
TENANT_B_RPM        = 10

# Rate limit tier defaults
TRIAL_RPM           = 5
STARTER_RPM         = 10
PROFESSIONAL_RPM    = 50
ENTERPRISE_RPM      = 200

# Expected test counts
EXPECTED_PASS       = 20
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
[ ] Test file exists                           — ls $TEST_FILE
```

---

## Test Categories

### Category 1: Rate Limit Enforcement (8 tests)

| ID | Test | Expected |
|----|------|----------|
| RL-01 | Starter tenant: 10 requests within 60s → all succeed | 200 on all 10 |
| RL-02 | Starter tenant: 15 requests within 60s → 429 after 10 | First 10 → 200, remaining → 429 |
| RL-03 | Professional tenant: 50 requests within 60s → all succeed | 200 on all 50 |
| RL-04 | Professional tenant: 60 requests within 60s → 429 after 50 | First 50 → 200, remaining → 429 |
| RL-05 | 429 response includes Retry-After header | Header present, value > 0 |
| RL-06 | 429 response body is valid JSON with error detail | {"detail": "..."} structure |
| RL-07 | After rate limit window resets (wait 60s), requests succeed again | 200 after waiting |
| RL-08 | Rate limit applies per-tenant, not globally (A and B have independent limits) | A at limit, B still accepts |

### Category 2: Cross-Tenant Rate Limit Isolation (4 tests)

| ID | Test | Expected |
|----|------|----------|
| RL-09 | Exhaust Tenant B's rate limit (10 rpm) | B gets 429 |
| RL-10 | While B is throttled, Tenant A requests still succeed | A gets 200 |
| RL-11 | Exhaust Tenant A's rate limit (50 rpm) | A gets 429 |
| RL-12 | While A is throttled, Tenant B requests still succeed (after window reset) | B gets 200 |

### Category 3: Burst Traffic Resilience (4 tests)

| ID | Test | Expected |
|----|------|----------|
| RL-13 | 100 concurrent requests from single tenant (10× starter limit) | Accepted requests ≤ rate limit, remainder → 429, no 500 errors |
| RL-14 | 100 concurrent requests across 10 simulated tenants (invalid keys) | All return 401, no 500 errors, response time < 2s |
| RL-15 | Rapid sequential requests (no delay, 50 requests) | Rate limiter engages, returns 429, no crash |
| RL-16 | After burst, normal traffic resumes within 60s | Next window allows normal rate |

### Category 4: Auth-Exempt Path Rate Limiting (4 tests)

| ID | Test | Expected |
|----|------|----------|
| RL-17 | /health endpoint under 100 rapid requests | All return 200 (health probes should not be rate limited) |
| RL-18 | /ready endpoint under 100 rapid requests | All return 200 |
| RL-19 | /api/status under 100 rapid requests | All return 200 (public status page) |
| RL-20 | /openapi.json under 100 rapid requests | Returns 200 consistently, no degradation |

---

## Steps

### Step 1: Run the rate limiting test suite

```
ACTION:    PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=short

EXPECTED:  $EXPECTED_PASS passed, 0 failed
VERIFY:    Exit code 0
           Summary line: "N passed" where N >= $EXPECTED_PASS
ON FAIL:   Classify failure:
           - Rate limit not enforced (no 429 at threshold) → middleware gap
           - Rate limit too aggressive (429 before threshold) → window calculation bug
           - Cross-tenant pollution (A throttled when B exhausted) → isolation bug (CRITICAL)
           - 500 errors under burst → backend crash under load
```

> **Note:** This procedure intentionally exhausts rate limits on both tenants.
> After execution, both tenants' rate limit windows will be partially consumed.
> Wait 60 seconds before running other live tests that depend on API availability.

### Step 2: Verify production stability after rate limit testing

```
ACTION:    Wait 60 seconds for rate limit windows to reset.
           curl $PROD_URL/health → 200
           curl $PROD_URL/ready → 200
           curl -H "X-API-Key: $TENANT_A_API_KEY" $PROD_URL/api/config → 200

EXPECTED:  All return 200 after rate limit window reset
VERIFY:    HTTP status codes
ON FAIL:   If production remains degraded after rate limit testing, the burst
           traffic may have caused resource exhaustion. Check Container Apps
           metrics for CPU/memory.
```

---

## Postconditions

```
[ ] All $EXPECTED_PASS tests passed, 0 failures
[ ] Starter tier enforced at $STARTER_RPM rpm
[ ] Professional tier enforced at $PROFESSIONAL_RPM rpm
[ ] 429 responses include Retry-After header
[ ] Cross-tenant rate limit isolation confirmed
[ ] Burst traffic produces 429, not 500
[ ] Auth-exempt endpoints not rate limited
[ ] Production healthy after test
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All tests pass, rate limits enforced at correct thresholds |
| **CONDITIONAL PASS** | Rate limits enforced but thresholds off by ≤20% (timing sensitivity) |
| **FAIL** | Rate limits not enforced, cross-tenant pollution, or 500 errors under burst |

---

## Timing Sensitivity Note

Rate limit tests are inherently timing-sensitive. Network latency between the test runner and production can cause requests to span multiple rate limit windows, making threshold enforcement appear off by a few requests. The tests should allow a ±20% tolerance on threshold counts (e.g., starter at 10 rpm should accept 8-12 before triggering 429).

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| No 429 responses at any volume | Code gap (rate limiting not enabled) | Check rate limiting middleware in auth.py or main.py |
| 429 at wrong threshold | Procedure defect or config drift | Verify TIER_DEFAULTS in cosmos_schema.py match expected values |
| Cross-tenant pollution | **CRITICAL** code finding | Rate limiter using global counter instead of per-tenant counter |
| 500 under burst | Code gap (unhandled concurrency) | Check rate limiter implementation for race conditions |
| All requests succeed (no 429 even at 10× limit) | Environment (rate limiting disabled in prod) | Check environment variable or feature flag for rate limiting |
| Timing-based flakiness (±2-3 requests off threshold) | Environment transient | Increase tolerance window, re-run. Note in results. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
