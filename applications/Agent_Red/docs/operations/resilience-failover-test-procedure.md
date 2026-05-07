# Resilience & Failover Testing Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (29 passed, 6 skipped — PASS)
# Last corrected: —

This procedure validates that the Agent Red platform degrades gracefully when internal services or external dependencies become unavailable. It tests circuit breaker behavior, error handling, recovery time, and user-facing error messages for each dependency failure mode.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** httpx (API probes), Azure CLI (service inspection), Chrome MCP (UI verification).
> **Test code:** `tests/security/test_resilience_live.py` (created by this procedure).
> **Safety:** This procedure does NOT intentionally break production services. It observes and verifies behavior under naturally occurring conditions or uses read-only probes to infer resilience posture.

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
TEST_FILE           = tests/security/test_resilience_live.py

API_KEY             = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
WIDGET_KEY          = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)
PROVIDER_KEY        = (from .env.local SUPERADMIN_PREVIEW_API_KEY; same key for provider console)

# Azure resources
RESOURCE_GROUP      = Agent-Red
CONTAINER_APP       = agent-red-api-gateway
SUBSCRIPTION        = 4dce2122-690a-4654-b531-cc647db62331

# Dependencies to test
DEPENDENCIES        = NATS, CosmosDB, AzureOpenAI, KeyVault, Stripe, Shopify, SendGrid

# Expected test counts
EXPECTED_PASS       = 35
EXPECTED_FAILURES   = 0
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] pytest + httpx installed                   — python -m pytest --version
[ ] Azure CLI authenticated                    — az account show
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] API key valid                              — curl -H "X-API-Key: $API_KEY" $PROD_URL/api/config → 200
[ ] Test file exists                           — ls $TEST_FILE
```

---

## Test Categories

### Category 1: Health Endpoint Dependency Reporting (7 tests)

These tests verify that the `/health` and `/ready` endpoints accurately report the status of each dependency.

| ID | Test | Expected |
|----|------|----------|
| RF-01 | /health returns status for each known dependency | JSON contains nats, cosmos, key_vault fields |
| RF-02 | /ready returns readiness state | 200 when core services available |
| RF-03 | /health response time < 2s under normal conditions | Response time within threshold |
| RF-04 | /health accurately reflects NATS status | nats.connected matches actual NATS state |
| RF-05 | /health accurately reflects Key Vault status | key_vault.healthy matches actual state |
| RF-06 | /health accurately reflects API version | version.product matches $PRODUCT_VERSION |
| RF-07 | /health does not leak secrets or internal IPs | No connection strings, tokens, or RFC 1918 addresses |

### Category 2: NATS Disconnection Behavior (6 tests)

NATS JetStream is the message queue for the AI chat pipeline. When disconnected, chat should fail gracefully while admin operations continue.

| ID | Test | Expected |
|----|------|----------|
| RF-08 | When NATS disconnected: /health reports nats: disconnected | Field value matches state |
| RF-09 | When NATS disconnected: /api/chat/conversations returns 503 with clear message | 503 + JSON error, not 500 |
| RF-10 | When NATS disconnected: admin endpoints (/api/config, /api/admin/conversations) still work | 200 |
| RF-11 | When NATS disconnected: Provider Console dashboard shows "Disconnected" for NATS | UI renders gracefully |
| RF-12 | When NATS disconnected: Provider Queue Health page shows error state | "Unable to load" message |
| RF-13 | When NATS disconnected: no unhandled exceptions in container logs | Zero Python tracebacks |

### Category 3: Circuit Breaker Verification (5 tests)

| ID | Test | Expected |
|----|------|----------|
| RF-14 | Circuit breaker config exists for all expected services | CIRCUIT_BREAKER_CONFIGS contains entries |
| RF-15 | /health reports circuit breaker states | circuit_breakers field present |
| RF-16 | Pipeline timeout budget is enforced (8s deadline) | PIPELINE_DEADLINE_MS = 8000 |
| RF-17 | Stage budgets sum to less than pipeline deadline | Sum of STAGE_BUDGETS_MS < PIPELINE_DEADLINE_MS |
| RF-18 | Chat request with artificial delay trigger does not exceed 8s | Response within timeout budget |

### Category 4: Graceful Error Responses (7 tests)

| ID | Test | Expected |
|----|------|----------|
| RF-19 | 503 responses have valid JSON body | {"detail": "..."} |
| RF-20 | 503 responses do not leak stack traces | No "Traceback" or ".py" in body |
| RF-21 | 500 responses (if any) have valid JSON body | {"detail": "..."} |
| RF-22 | Error responses include appropriate status codes (not generic 500 for all) | 503 for dependency, 429 for rate limit, 400 for bad input |
| RF-23 | Error response Content-Type is application/json | Header present |
| RF-24 | Widget API errors are customer-friendly (no technical jargon) | "temporarily unavailable" style messaging |
| RF-25 | Admin API errors include diagnostic info for operators | Error detail includes context |

### Category 5: Recovery Behavior (4 tests)

| ID | Test | Expected |
|----|------|----------|
| RF-26 | After container restart, /health returns 200 within 30s | Recovery time < 30s |
| RF-27 | After container restart, existing API keys still work | No auth regression |
| RF-28 | After container restart, /ready eventually returns 200 | Readiness restored |
| RF-29 | Successive /health calls during degradation don't return different schemas | Consistent response shape |

### Category 6: External Dependency Posture (6 tests)

These tests verify the system's declared integration posture without inducing failures.

| ID | Test | Expected |
|----|------|----------|
| RF-30 | Provider Integration Health page lists all expected integrations | NATS, MCP Shopify, MCP Stripe visible |
| RF-31 | Integration Health shows correct enabled/disabled state | Matches actual configuration |
| RF-32 | Stripe checkout endpoints handle Stripe API errors gracefully | 502 or 503, not 500 |
| RF-33 | Shopify billing confirm handles invalid session gracefully | 400 or 404, not 500 |
| RF-34 | SendGrid email delivery failure doesn't crash alert engine | Alert recorded, email marked failed |
| RF-35 | Azure OpenAI timeout produces pipeline timeout, not hang | Response within 8s even if OpenAI is slow |

---

## Steps

### Step 1: Assess current dependency state

```
ACTION:    curl $PROD_URL/health | python -m json.tool
           curl $PROD_URL/ready | python -m json.tool

EXPECTED:  JSON output showing status of each dependency
VERIFY:    Both return 200
           Record which dependencies are currently healthy/degraded
NOTE:      Some dependencies (e.g., NATS) may already be disconnected.
           This is not a precondition failure — the tests verify behavior
           under both connected and disconnected states.
```

### Step 2: Run the resilience test suite

```
ACTION:    PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=short

EXPECTED:  $EXPECTED_PASS passed, 0 failed
VERIFY:    Exit code 0
ON FAIL:   Classify failure:
           - Error response not JSON → error handling middleware gap
           - 500 instead of 503 → unhandled exception in dependency call
           - Stack trace in response body → error sanitization gap
           - Recovery timeout exceeded → startup probe misconfigured
```

### Step 3: Verify Provider Console under current dependency state

```
ACTION:    Using Chrome MCP, navigate to Provider Console:
           1. Inject auth (sessionStorage)
           2. Check Dashboard — system health indicators
           3. Check Integration Health — dependency states
           4. Check Queue Health — NATS-dependent page
           5. Check Abuse Detection — NATS-dependent page

EXPECTED:  All pages render without console errors
           Degraded dependencies show appropriate warning badges/messages
           No "undefined" or "NaN" in UI text
VERIFY:    Chrome MCP screenshot + console error check per page
ON FAIL:   UI rendering failure under degraded state → null-safety gap.
           Reference Provider Console null-safety pattern (session 54).
```

### Step 4: Verify container restart recovery (non-disruptive)

```
ACTION:    Record current revision:
           az containerapp show -n $CONTAINER_APP -g $RESOURCE_GROUP --query "properties.latestRevisionName" -o tsv

           Check current replica count:
           az containerapp revision show -n $CONTAINER_APP -g $RESOURCE_GROUP --revision <revision_name> --query "properties.replicas" -o tsv

           NOTE: Do NOT restart the container. Instead, verify recovery posture
           by confirming the health endpoint response time and schema consistency
           across 10 rapid sequential calls.

           for i in {1..10}; do
             curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" $PROD_URL/health
           done

EXPECTED:  All 10 calls return 200
           Response time < 500ms for all calls
           No intermittent 503 or connection refused
VERIFY:    All HTTP codes are 200, all times < 0.5s
ON FAIL:   Intermittent failures suggest the container is unhealthy or scaling
           unpredictably. Check Container Apps metrics.
```

---

## Postconditions

```
[ ] All $EXPECTED_PASS tests passed, 0 failures
[ ] /health accurately reports all dependency states
[ ] Error responses are valid JSON without leaked internals
[ ] NATS disconnection: admin endpoints unaffected, chat returns 503
[ ] Provider Console renders gracefully under degraded dependencies
[ ] Circuit breaker configuration validated
[ ] Pipeline timeout budget enforced (8s)
[ ] Container health probe responds consistently
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All tests pass, graceful degradation confirmed for all observed failure modes |
| **CONDITIONAL PASS** | All API tests pass, but Provider Console shows minor rendering issues under degradation (known null-safety gaps) |
| **FAIL** | 500 errors instead of 503, stack traces in responses, admin endpoints affected by chat dependency failures, or container instability |

---

## Dependency Failure Impact Matrix

| Dependency | Chat API | Admin API | Provider Console | /health | /ready |
|------------|----------|-----------|------------------|---------|--------|
| **NATS** | ❌ 503 | ✅ Works | ✅ Graceful degraded | ✅ Reports disconnected | ✅ (may report degraded) |
| **Cosmos DB** | ❌ 503 | ❌ 503 | ❌ Empty data | ❌ Degraded | ❌ Not ready |
| **Azure OpenAI** | ❌ 503 (after timeout) | ✅ Works | ✅ Works | ✅ (may not detect) | ✅ Works |
| **Key Vault** | ✅ (cached secrets) | ✅ (cached secrets) | ✅ Works | ✅ Reports degraded | ✅ Works |
| **Stripe** | ✅ Works | ✅ (billing pages error) | ✅ Shows error | ✅ Works | ✅ Works |
| **Shopify** | ✅ Works | ✅ Works | ✅ Works | ✅ Works | ✅ Works |
| **SendGrid** | ✅ Works | ✅ (alerts not emailed) | ✅ Works | ✅ Works | ✅ Works |

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| NATS always shows "disconnected" | Environment (NATS not provisioned/connected in current infra) | This is expected if NATS is not deployed. Tests verify graceful handling of this state. |
| /health returns different schema intermittently | Procedure defect or race condition | Check health endpoint implementation for concurrent access issues |
| 500 error with stack trace in response | **CRITICAL** code finding | Error handling middleware not catching the exception. Fix middleware, add test. |
| Provider Console page crashes on null data | Code gap (null-safety) | Apply `?? {}` pattern per session 54 lesson |
| Container restart takes > 30s | Environment (cold start) | Check startup probe configuration in Container Apps |
| Circuit breaker states not exposed in /health | Code gap | Add circuit breaker registry to health endpoint response |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
