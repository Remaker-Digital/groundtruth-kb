# Comprehensive Test Plan — Agent Red Customer Engagement

> **Status:** Living document — tracks all existing and planned tests
> **Project:** Agent Red Customer Engagement
> **Owner:** Remaker Digital (DBA of VanDusen & Palmeter, LLC)
> **Created:** 2026-01-31
> **Last Updated:** 2026-01-31
> **Baseline:** 125 tests passing (audit date: 2026-01-31)
> **Target:** ~750-875 tests at launch readiness

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Existing Test Inventory (125 Tests)](#2-existing-test-inventory-125-tests)
3. [Test Infrastructure Requirements](#3-test-infrastructure-requirements)
4. [P0 — Launch Blockers (~180 Tests)](#4-p0--launch-blockers-180-tests)
5. [P1 — Pre-Launch Required (~200 Tests)](#5-p1--pre-launch-required-200-tests)
6. [P2 — Launch Quality (~150 Tests)](#6-p2--launch-quality-150-tests)
7. [P3 — Post-Launch / Continuous (~100 Tests)](#7-p3--post-launch--continuous-100-tests)
8. [Adversarial & Security Tests (~45 Tests)](#8-adversarial--security-tests-45-tests)
9. [Performance & Load Tests (~30 Tests)](#9-performance--load-tests-30-tests)
10. [Trial / Demo Environment Tests (~20 Tests)](#10-trial--demo-environment-tests-20-tests)
11. [UI-Type × Task-Type Validation Tests (~100 Tests)](#11-ui-type--task-type-validation-tests-100-tests)
12. [Summary & Metrics](#12-summary--metrics)

---

## 1. Executive Summary

### Current State

| Metric | Value |
|--------|-------|
| Tests passing | 125 |
| Test files | 5 (3 test files + 1 fixtures + 2 __init__.py) |
| Source modules | 29 (19 multi_tenant + 10 integrations) |
| Modules with tests | 4 of 29 (14%) |
| API endpoints | 30 across 9 routers |
| Endpoints with HTTP tests | 0 of 30 (0%) |
| HTTP-level tests (TestClient) | 0 |
| Config endpoints tested | 0 of 10 |
| Middleware integration tests | 0 |
| Load / performance tests | 0 |
| Adversarial / security tests | 0 |
| CI pipeline | None |

### Gap Analysis

| Category | Existing | Planned | Gap |
|----------|----------|---------|-----|
| Unit tests (service layer) | 125 | ~350 | ~225 |
| HTTP endpoint tests (TestClient) | 0 | ~150 | ~150 |
| Integration tests (cross-module) | 10 | ~80 | ~70 |
| Middleware pipeline tests | 0 | ~40 | ~40 |
| Adversarial / security tests | 0 | ~45 | ~45 |
| Performance / load tests | 0 | ~30 | ~30 |
| Trial / demo environment tests | 0 | ~20 | ~20 |
| UI-type validation tests | 0 | ~100 | ~100 |
| **Total** | **125** | **~815** | **~690** |

---

## 2. Existing Test Inventory (125 Tests)

### 2.1 Auth & Middleware — `tests/multi_tenant/test_auth_middleware.py` (57 tests)

| Test Class | ID Range | Count | Module Under Test |
|------------|----------|-------|-------------------|
| TestExtractBearerToken | AUTH-01 | 7 | auth.py |
| TestIsAuthExempt | AUTH-02 | 9 | auth.py |
| TestHashApiKey | AUTH-03 | 5 | auth.py |
| TestExtractShopDomain | AUTH-04 | 4 | auth.py |
| TestValidateTenantStatus | AUTH-05 | 7 | auth.py |
| TestVerifyApiKey | AUTH-06 | 4 | auth.py |
| TestGetTenantContext | MW-01 | 2 | middleware.py |
| TestRequireTier | MW-02 | 5 | middleware.py |
| TestRateLimitGetLimit | MW-03 | 4 | middleware.py |
| TestRateLimitSlidingWindow | MW-04 | 3 | middleware.py |
| TestConfigureTenantResolution | MW-05 | 1 | middleware.py |
| TestTenantContext | AUTH-07 | 3 | auth.py |
| **Subtotal** | | **57** | |

### 2.2 Provisioning & Webhooks — `tests/integrations/test_provisioning_webhooks.py` (38 tests)

| Test Class | ID Range | Count | Module Under Test |
|------------|----------|-------|-------------------|
| TestProvisioningService | PROV-01 to PROV-07 | 12 | provisioning.py |
| TestStripeWebhookHandler | WH-01 to WH-09 | 15 | stripe_webhooks.py |
| TestWebhookIdempotency | IDEMP-01 to IDEMP-04 | 6 | stripe_webhooks.py |
| TestCrossChannelIsolation | XISO-01 to XISO-05 | 5 | provisioning.py |
| **Subtotal** | | **38** | |

### 2.3 Persistent Customer Memory — Unit Tests — `tests/persistent_memory/test_unit_layers.py` (20 tests)

| Test Class | ID Range | Count | Module Under Test |
|------------|----------|-------|-------------------|
| TestLayer1CustomerProfile | L1-01 to L1-06 | 6 | customer_profile_service.py |
| TestLayer2ConversationMemory | L2-01 to L2-06 | 6 | conversation_vectorizer.py |
| TestLayer3CrossSessionLearning | L3-01 to L3-04 | 4 | (interface contracts — not yet implemented) |
| TestLayer4DedicatedTraining | L4-01 to L4-04 | 4 | (interface contracts — not yet implemented) |
| **Subtotal** | | **20** | |

### 2.4 Persistent Customer Memory — Integration Tests — `tests/persistent_memory/test_integration_layers.py` (10 tests)

| Test Class | ID Range | Count | Scope |
|------------|----------|-------|-------|
| TestCrossLayerIntegration | CL-01 to CL-10 | 10 | Full stack Enterprise, graceful degradation, layer conflict, new customer, tier upgrade, GDPR deletion, cross-tenant isolation, consent lifecycle, prompt assembly, explainability completeness |
| **Subtotal** | | **10** | |

---

## 3. Test Infrastructure Requirements

Before new tests can be created, the following infrastructure must be in place:

### 3.1 pytest Configuration

| Item | File | Status |
|------|------|--------|
| pytest config | `pyproject.toml` or `pytest.ini` | **Missing** |
| Test markers (unit, integration, e2e, slow) | pyproject.toml `[tool.pytest.ini_options]` | **Missing** |
| Async test support | `pytest-asyncio` in test requirements | **Missing** |
| Coverage reporting | `pytest-cov` in test requirements | **Missing** |
| Test requirements file | `requirements-test.txt` | **Missing** |

### 3.2 Shared Test Fixtures

| Fixture | File | Status |
|---------|------|--------|
| FastAPI TestClient | `tests/conftest.py` | **Missing** |
| Mock Cosmos DB | `tests/conftest.py` | **Missing** |
| Mock NATS connection | `tests/conftest.py` | **Missing** |
| Mock Key Vault | `tests/conftest.py` | **Missing** |
| Authenticated request helpers | `tests/conftest.py` | **Missing** |
| Tenant context factories (all tiers) | `tests/conftest.py` | Partial (in test_auth_middleware.py) |
| Persistent memory fixtures | `tests/persistent_memory/fixtures.py` | **Exists** |

### 3.3 CI/CD Pipeline

| Item | Status |
|------|--------|
| GitHub Actions workflow for pytest | **Missing** |
| Test matrix (Python 3.12+, OS) | **Missing** |
| Coverage gate (target: 80%+) | **Missing** |
| PR check enforcement | **Missing** |

---

## 4. P0 — Launch Blockers (~180 Tests)

These tests must pass before any production deployment.

### 4.1 HTTP Endpoint Tests — Billing & Checkout (35 tests)

All tests use FastAPI TestClient. Module: `tests/integrations/test_http_billing.py`

| ID | Test | Endpoint | Module |
|----|------|----------|--------|
| HTTP-BILL-01 | POST /api/checkout/session — valid Starter plan | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-02 | POST /api/checkout/session — valid Professional plan | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-03 | POST /api/checkout/session — valid Enterprise plan | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-04 | POST /api/checkout/session — annual billing discount applied | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-05 | POST /api/checkout/session — invalid plan ID returns 400 | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-06 | POST /api/checkout/session — Rewardful client_reference_id included | POST /api/checkout/session | stripe_checkout.py |
| HTTP-BILL-07 | GET /api/checkout/success — valid session_id | GET /api/checkout/success | stripe_checkout.py |
| HTTP-BILL-08 | GET /api/checkout/success — missing session_id returns 400 | GET /api/checkout/success | stripe_checkout.py |
| HTTP-BILL-09 | GET /api/checkout/cancel — returns redirect/message | GET /api/checkout/cancel | stripe_checkout.py |
| HTTP-BILL-10 | POST /api/packs/purchase — 1K pack | POST /api/packs/purchase | stripe_packs.py |
| HTTP-BILL-11 | POST /api/packs/purchase — 5K pack | POST /api/packs/purchase | stripe_packs.py |
| HTTP-BILL-12 | POST /api/packs/purchase — 20K pack | POST /api/packs/purchase | stripe_packs.py |
| HTTP-BILL-13 | POST /api/packs/purchase — invalid pack size returns 400 | POST /api/packs/purchase | stripe_packs.py |
| HTTP-BILL-14 | GET /api/packs/balance/{customer_id} — returns FIFO balance | GET /api/packs/balance/{id} | stripe_packs.py |
| HTTP-BILL-15 | GET /api/packs/balance/{customer_id} — unknown customer returns empty | GET /api/packs/balance/{id} | stripe_packs.py |
| HTTP-BILL-16 | POST /api/billing/portal — returns portal URL | POST /api/billing/portal | stripe_portal.py |
| HTTP-BILL-17 | POST /api/billing/portal — unauthenticated returns 401 | POST /api/billing/portal | stripe_portal.py |
| HTTP-BILL-18 | POST /api/usage/record — records billable conversation | POST /api/usage/record | stripe_usage.py |
| HTTP-BILL-19 | POST /api/usage/record — deduplicates on conversation_id | POST /api/usage/record | stripe_usage.py |
| HTTP-BILL-20 | GET /api/usage/{customer_id} — returns usage summary | GET /api/usage/{id} | stripe_usage.py |
| HTTP-BILL-21 | POST /api/webhooks/stripe — checkout.session.completed | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-22 | POST /api/webhooks/stripe — customer.subscription.updated | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-23 | POST /api/webhooks/stripe — customer.subscription.deleted | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-24 | POST /api/webhooks/stripe — invoice.payment_succeeded | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-25 | POST /api/webhooks/stripe — invoice.payment_failed | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-26 | POST /api/webhooks/stripe — invoice.finalization_failed | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-27 | POST /api/webhooks/stripe — invalid signature returns 400 | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-28 | POST /api/webhooks/stripe — idempotent replay returns 200 | POST /api/webhooks/stripe | stripe_webhooks.py |
| HTTP-BILL-29 | POST /api/shopify/billing/subscribe — creates subscription | POST /api/shopify/billing/subscribe | shopify_billing.py |
| HTTP-BILL-30 | GET /api/shopify/billing/confirm — confirms billing | GET /api/shopify/billing/confirm | shopify_billing.py |
| HTTP-BILL-31 | GET /api/shopify/billing/status — returns subscription status | GET /api/shopify/billing/status | shopify_billing.py |
| HTTP-BILL-32 | POST /api/shopify/billing/subscribe — annual plan no usage pricing | POST /api/shopify/billing/subscribe | shopify_billing.py |
| HTTP-BILL-33 | Shopify Decimal arithmetic — no floating-point rounding errors | N/A (unit) | shopify_billing.py |
| HTTP-BILL-34 | GET /api/tenants/lookup — returns tenant by domain | GET /api/tenants/lookup | provisioning.py |
| HTTP-BILL-35 | GET /api/tenants/{tenant_id} — returns tenant detail | GET /api/tenants/{id} | provisioning.py |

### 4.2 Middleware Pipeline Integration Tests (25 tests)

Full middleware stack tests through HTTP. Module: `tests/multi_tenant/test_middleware_pipeline.py`

| ID | Test | Validates |
|----|------|-----------|
| MWP-01 | Unauthenticated request to protected endpoint → 401 | TenantAuthMiddleware |
| MWP-02 | Valid API key → TenantContext set → 200 | Auth + pipeline |
| MWP-03 | Valid Shopify session token → TenantContext set → 200 | Auth + pipeline |
| MWP-04 | Expired Shopify session token → 401 | Auth rejection |
| MWP-05 | Invalid API key → 401 | Auth rejection |
| MWP-06 | Auth-exempt path (GET /health) → 200 without auth | Auth exemption |
| MWP-07 | Auth-exempt path (POST /api/webhooks/stripe) → 200 without auth | Auth exemption |
| MWP-08 | Starter tenant rate limit — 10 requests pass, 11th → 429 | RateLimitMiddleware |
| MWP-09 | Professional tenant rate limit — 50 requests pass | RateLimitMiddleware |
| MWP-10 | Enterprise tenant rate limit — 200 requests pass | RateLimitMiddleware |
| MWP-11 | Rate limit sliding window — expired entries cleaned | RateLimitMiddleware |
| MWP-12 | Rate limit 429 includes Retry-After header | RateLimitMiddleware |
| MWP-13 | Starter concurrency limit — 3 concurrent, 4th queued | TenantConcurrencyMiddleware |
| MWP-14 | Professional concurrency limit — 10 concurrent | TenantConcurrencyMiddleware |
| MWP-15 | Enterprise concurrency limit — 30 concurrent | TenantConcurrencyMiddleware |
| MWP-16 | Queue overflow → 429 | TenantConcurrencyMiddleware |
| MWP-17 | Correlation ID generated for each request | CorrelationMiddleware |
| MWP-18 | Correlation ID propagated through response headers | CorrelationMiddleware |
| MWP-19 | TenantContext available in all downstream handlers | Full stack |
| MWP-20 | Middleware execution order verified (auth → rate → concurrency → correlation) | Full stack |
| MWP-21 | PROVISIONING status tenant → 403 | Auth + tenant status |
| MWP-22 | DEACTIVATED status tenant → 403 | Auth + tenant status |
| MWP-23 | PAST_DUE status tenant → 200 (allowed) | Auth + tenant status |
| MWP-24 | GRACE_PERIOD status tenant → 403 on write, 200 on read (when allow_readonly) | Auth + tenant status |
| MWP-25 | Request with both API key and Shopify token — API key takes precedence (or explicit priority) | Auth method resolution |

### 4.3 ConversationMeter Unit Tests (30 tests)

Module: `tests/multi_tenant/test_conversation_meter.py`

| ID | Test | Validates |
|----|------|-----------|
| CM-01 | First customer message starts billable conversation | Conversation start |
| CM-02 | Second message in same conversation does not double-count | Idempotent counting |
| CM-03 | 30-minute idle timeout ends conversation | Idle timeout |
| CM-04 | Customer "end" signal ends conversation | Customer end |
| CM-05 | Escalation ends conversation | Escalation end |
| CM-06 | 50-turn limit ends conversation | Turn limit |
| CM-07 | test_ prefixed conversation → non-billable | Prefix exclusion |
| CM-08 | admin_ prefixed conversation → non-billable | Prefix exclusion |
| CM-09 | health_ prefixed conversation → non-billable | Prefix exclusion |
| CM-10 | system_ prefixed conversation → non-billable | Prefix exclusion |
| CM-11 | Error before AI response → non-billable | Error exclusion |
| CM-12 | Included allowance consumed first (Starter 1,000) | 3-tier tier 1 |
| CM-13 | Included allowance consumed first (Professional 5,000) | 3-tier tier 1 |
| CM-14 | Included allowance consumed first (Enterprise 20,000) | 3-tier tier 1 |
| CM-15 | Pack balance consumed after included allowance | 3-tier tier 2 |
| CM-16 | FIFO pack consumption — oldest pack first | Pack ordering |
| CM-17 | Expired pack (90-day) skipped | Pack expiry |
| CM-18 | Stripe overage reported after packs exhausted | 3-tier tier 3 |
| CM-19 | 80% allowance alert fires once per period | Alert threshold |
| CM-20 | 100% allowance alert fires once per period | Alert threshold |
| CM-21 | Pack balance low alert fires | Alert threshold |
| CM-22 | Alert does not re-fire in same billing period (idempotent) | Alert idempotency |
| CM-23 | Daily reconciliation — no discrepancy | Reconciliation |
| CM-24 | Daily reconciliation — >5% discrepancy flagged | Reconciliation |
| CM-25 | get_usage_dashboard() returns correct counters | Dashboard data |
| CM-26 | get_conversation_billing_detail() returns full attribution | Audit trail |
| CM-27 | Idle conversation scanner finds stale conversations | Scanner |
| CM-28 | Idle conversation scanner ends stale conversations | Scanner |
| CM-29 | Concurrent metering calls — no race conditions | Thread safety |
| CM-30 | Meter reset at billing period boundary | Period management |

### 4.4 CriticPolicy Unit Tests (20 tests)

Module: `tests/multi_tenant/test_critic_policy.py`

| ID | Test | Validates |
|----|------|-----------|
| CP-01 | Critic approves → response passes through | Happy path |
| CP-02 | Critic rejects → response blocked, SAFE_FALLBACK_MESSAGE returned | Rejection |
| CP-03 | Critic timeout (>800ms) → response blocked | Timeout |
| CP-04 | Critic error → response blocked | Error handling |
| CP-05 | Critic unavailable → response blocked | Unavailability |
| CP-06 | require_critic_approval() returns (True, text, result) on approval | Wrapper API |
| CP-07 | require_critic_approval() returns (False, fallback, result) on rejection | Wrapper API |
| CP-08 | SAFE_FALLBACK_MESSAGE is the only text delivered when Critic fails | Fallback content |
| CP-09 | SECURITY_EVENT audit logged on blocked response | Audit logging |
| CP-10 | ESCALATION_TRIGGERED when Critic replicas unavailable | Escalation |
| CP-11 | Circuit breaker CLOSED → OPEN after 5 failures in 30s | CB state transition |
| CP-12 | Circuit breaker OPEN → HALF_OPEN after 15s recovery | CB state transition |
| CP-13 | Circuit breaker HALF_OPEN → CLOSED on success | CB state transition |
| CP-14 | Circuit breaker HALF_OPEN → OPEN on failure | CB state transition |
| CP-15 | CriticResult dataclass frozen | Data integrity |
| CP-16 | CriticResult captures latency | Metrics |
| CP-17 | Health check returns circuit breaker state | Health reporting |
| CP-18 | Connection pooling reused across calls (httpx) | Resource management |
| CP-19 | 800ms timeout budget enforced | Budget adherence |
| CP-20 | Critic modifies response text → modified text returned | Modification handling |

### 4.5 Cosmos DB Schema & Repository Tests (25 tests)

Module: `tests/multi_tenant/test_cosmos_repository.py`

| ID | Test | Validates |
|----|------|-----------|
| CR-01 | TenantScopedRepository.create() sets tenant_id | Write enforcement |
| CR-02 | TenantScopedRepository.create() rejects mismatched tenant_id | Write validation |
| CR-03 | TenantScopedRepository.read() verifies tenant_id on result | Read verification |
| CR-04 | TenantScopedRepository.read() returns None for cross-tenant doc | Read isolation |
| CR-05 | TenantScopedRepository.query() filters by tenant_id | Query enforcement |
| CR-06 | TenantScopedRepository.query() result verification | Query result filtering |
| CR-07 | TenantScopedRepository.delete() requires tenant_id | Delete enforcement |
| CR-08 | TenantScopedRepository.patch() validates tenant_id | Patch enforcement |
| CR-09 | TenantScopedRepository.upsert() sets tenant_id | Upsert enforcement |
| CR-10 | Atomic counter increment (no read-modify-write) | Atomic operations |
| CR-11 | TenantDocument model validation (required fields) | Schema validation |
| CR-12 | ConversationDocument model validation | Schema validation |
| CR-13 | UsageCounterDocument model validation | Schema validation |
| CR-14 | PackBalanceDocument with FIFO ordering | Schema validation |
| CR-15 | CustomerProfileDocument with PII classification | Schema validation |
| CR-16 | MemoryVectorDocument with 3072d embedding | Schema validation |
| CR-17 | AuditLogDocument with all 12 event types | Schema validation |
| CR-18 | TIER_DEFAULTS completeness (all 3 tiers, all required fields) | Configuration |
| CR-19 | TenantTier enum values | Enum completeness |
| CR-20 | TenantStatus enum values | Enum completeness |
| CR-21 | CosmosManager singleton pattern | Singleton |
| CR-22 | CosmosManager health check | Health |
| CR-23 | 9 collection configurations with correct partition keys | Collection setup |
| CR-24 | DiskANN vector index configuration | Vector search |
| CR-25 | PlatformConfig and AuditLog repos are NOT tenant-scoped | Platform repos |

### 4.6 Health Endpoint Tests (10 tests)

Module: `tests/test_health.py`

| ID | Test | Validates |
|----|------|-----------|
| HE-01 | GET /health → 200 {"status": "healthy"} | Liveness probe |
| HE-02 | GET /ready → 200 with NATS status | Readiness probe |
| HE-03 | GET /ready → includes circuit_breakers field | CB health |
| HE-04 | GET /ready → includes key_vault field | KV health |
| HE-05 | GET /ready → NATS disconnected shows connected: false | Degraded NATS |
| HE-06 | GET /health does not require authentication | Auth exemption |
| HE-07 | GET /ready does not require authentication | Auth exemption |
| HE-08 | Startup: tenant resolution configured | Startup event |
| HE-09 | Startup: tracing configured | Startup event |
| HE-10 | Startup: circuit breakers registered | Startup event |

### 4.7 Stripe Catalog Model Tests (5 tests)

Module: `tests/integrations/test_stripe_catalog.py`

| ID | Test | Validates |
|----|------|-----------|
| SC-01 | StripeCatalog loads from stripe_product_ids.json | Config loading |
| SC-02 | All 3 tier product IDs present | Completeness |
| SC-03 | All 3 tier monthly price IDs present | Completeness |
| SC-04 | All 3 tier annual price IDs present | Completeness |
| SC-05 | Pack price IDs present (1K, 5K, 20K) | Completeness |

### 4.8 3-Tier Usage Consumption Integration Tests (10 tests)

Module: `tests/integrations/test_usage_consumption.py`

| ID | Test | Validates |
|----|------|-----------|
| UC-01 | Fresh Starter tenant — first 1,000 conversations free | Included tier |
| UC-02 | Starter tenant at 1,001 — pack consumed | Pack tier |
| UC-03 | Starter tenant — all packs expired → Stripe overage | Overage tier |
| UC-04 | Professional tenant — 5,000 included | Included tier |
| UC-05 | Enterprise tenant — 20,000 included | Included tier |
| UC-06 | Pack FIFO — oldest pack consumed first | Pack ordering |
| UC-07 | Pack expiry — 90-day-old pack skipped | Pack validity |
| UC-08 | Multiple packs — correct balance tracking | Pack balance |
| UC-09 | Stripe Billing Meter receives overage report | Stripe integration |
| UC-10 | Cross-billing-period counter reset | Period boundary |

**P0 Subtotal: 160 tests**

---

## 5. P1 — Pre-Launch Required (~200 Tests)

### 5.1 NATS Tenant Isolation Tests (25 tests)

Module: `tests/multi_tenant/test_nats_isolation.py`

| ID | Test | Validates |
|----|------|-----------|
| NI-01 | Topic namespace format: {tenant_id}.{agent} | Topic naming |
| NI-02 | All 6 agent topics created for each tenant | Topic completeness |
| NI-03 | provision_tenant_topics() creates JetStream stream | Provisioning |
| NI-04 | deprovision_tenant_topics() purges and deletes stream | Deprovisioning |
| NI-05 | update_tenant_stream() adjusts queue depth on tier change | Tier change |
| NI-06 | authorize_subject() validates tenant_id prefix | Authorization |
| NI-07 | authorize_subject() rejects cross-tenant access | Isolation |
| NI-08 | NATSAuthorizationError raised on cross-tenant publish | Security |
| NI-09 | NATSAuthorizationError raised on cross-tenant subscribe | Security |
| NI-10 | build_correlation_headers() populates NATS headers | Correlation |
| NI-11 | extract_correlation_headers() reads NATS headers | Correlation |
| NI-12 | NATSCircuitBreaker — 3 failures → OPEN | Circuit breaker |
| NI-13 | NATSCircuitBreaker — recovery after 5s | Circuit breaker |
| NI-14 | Health check returns connection status | Health |
| NI-15 | init_nats_manager() establishes connection | Lifecycle |
| NI-16 | close_nats_manager() drains and closes | Lifecycle |
| NI-17 | Non-fatal startup when NATS unavailable | Graceful degradation |
| NI-18 | WorkQueue retention policy set correctly | Stream config |
| NI-19 | Tier-aware queue depth from TIER_DEFAULTS | Config |
| NI-20 | Publish with circuit breaker protection | Resilience |
| NI-21 | Subscribe returns tenant-filtered messages only | Isolation |
| NI-22 | Multiple tenants — independent streams | Multi-tenant |
| NI-23 | Stream name format: tenant-{tenant_id} | Naming |
| NI-24 | Wildcard subject: {tenant_id}.> | Config |
| NI-25 | Singleton pattern — get_nats_manager() | Singleton |

### 5.2 GDPR Services Tests (30 tests)

Module: `tests/multi_tenant/test_gdpr_services.py`

| ID | Test | Validates |
|----|------|-----------|
| GDPR-01 | PiiScrubber — email address detected and scrubbed | PII detection |
| GDPR-02 | PiiScrubber — phone number detected and scrubbed | PII detection |
| GDPR-03 | PiiScrubber — nested dict recursion | Recursive scrub |
| GDPR-04 | PiiScrubber — list items scrubbed | List handling |
| GDPR-05 | PiiScrubber — DIRECT classification fields scrubbed | Classification |
| GDPR-06 | PiiScrubber — INDIRECT classification fields scrubbed | Classification |
| GDPR-07 | PiiScrubber — SENSITIVE classification fields scrubbed | Classification |
| GDPR-08 | PiiScrubber — non-destructive (original dict unchanged) | Immutability |
| GDPR-09 | PiiScrubber — scrub_text() for log messages | Text scrubbing |
| GDPR-10 | GracePeriodManager — Shopify 48hr grace period | Channel-specific |
| GDPR-11 | GracePeriodManager — Stripe 30-day grace period | Channel-specific |
| GDPR-12 | GracePeriodManager — is_grace_expired() before expiry | Timing |
| GDPR-13 | GracePeriodManager — is_grace_expired() after expiry | Timing |
| GDPR-14 | DataStoreRegistry — register and retrieve adapter | Registry pattern |
| GDPR-15 | DataExportService — tenant-level export across all stores | Export |
| GDPR-16 | DataExportService — customer-level export | Export |
| GDPR-17 | DataExportService — audit log created (DATA_EXPORTED) | Audit trail |
| GDPR-18 | DataDeletionService — tenant deletion cascades across all stores | Deletion |
| GDPR-19 | DataDeletionService — customer deletion | Deletion |
| GDPR-20 | DataDeletionService — grace period enforced (GracePeriodActiveError) | Grace period |
| GDPR-21 | DataDeletionService — audit log created (DATA_DELETED) | Audit trail |
| GDPR-22 | ConsentManager — grant consent | Consent |
| GDPR-23 | ConsentManager — deny consent | Consent |
| GDPR-24 | ConsentManager — deny triggers Layer 2-4 data deletion | Auto-deletion |
| GDPR-25 | ConsentManager — audit log created (CONSENT_CHANGED) | Audit trail |
| GDPR-26 | CosmosDataStoreAdapter — export from 7 collections | Adapter |
| GDPR-27 | CosmosDataStoreAdapter — delete from 7 collections | Adapter |
| GDPR-28 | NATSDataStoreAdapter — stream purge | Adapter |
| GDPR-29 | NATSDataStoreAdapter — stream delete | Adapter |
| GDPR-30 | Cascading deletion order enforced | Order |

### 5.3 Pipeline Resilience Tests (20 tests)

Module: `tests/multi_tenant/test_pipeline_resilience.py`

| ID | Test | Validates |
|----|------|-----------|
| PR-01 | PipelineTimeoutBudget — 8,000ms hard deadline | Total budget |
| PR-02 | PipelineTimeoutBudget — IC stage 800ms budget | Stage budget |
| PR-03 | PipelineTimeoutBudget — KR stage 1,000ms budget | Stage budget |
| PR-04 | PipelineTimeoutBudget — RG stage 3,000ms budget | Stage budget |
| PR-05 | PipelineTimeoutBudget — CR stage 800ms budget | Stage budget |
| PR-06 | PipelineTimeoutBudget — ESC stage 1,400ms budget | Stage budget |
| PR-07 | PipelineTimeoutBudget — AN stage 800ms budget | Stage budget |
| PR-08 | PipelineTimeoutBudget — exceeding total raises PipelineTimeoutError | Timeout error |
| PR-09 | StageResult tracks per-stage duration | Metrics |
| PR-10 | ServiceCircuitBreaker — Azure OpenAI config (5 failures/30s, 15s recovery) | Config |
| PR-11 | ServiceCircuitBreaker — Cosmos DB config (3 failures/15s, 10s recovery) | Config |
| PR-12 | ServiceCircuitBreaker — CLOSED → OPEN transition | State machine |
| PR-13 | ServiceCircuitBreaker — OPEN → HALF_OPEN transition | State machine |
| PR-14 | ServiceCircuitBreaker — HALF_OPEN → CLOSED on success | State machine |
| PR-15 | call_with_breaker() — success passes through | Happy path |
| PR-16 | call_with_breaker() — OPEN raises ServiceUnavailableError | Failure path |
| PR-17 | ServiceCircuitBreakerRegistry — named breaker management | Registry |
| PR-18 | ServiceCircuitBreakerRegistry — health_summary() | Health |
| PR-19 | ServiceCircuitBreakerRegistry — reset_all() | Reset |
| PR-20 | get_circuit_breaker_registry() singleton | Singleton |

### 5.4 OpenTelemetry Tracing Tests (15 tests)

Module: `tests/multi_tenant/test_otel_tracing.py`

| ID | Test | Validates |
|----|------|-----------|
| OT-01 | TenantSpanProcessor injects tenant_id on span | Span attributes |
| OT-02 | TenantSpanProcessor injects conversation_id on span | Span attributes |
| OT-03 | TenantSpanProcessor injects trace_id on span | Span attributes |
| OT-04 | TenantLogFilter injects tenant context into log records | Log filtering |
| OT-05 | CorrelationContext frozen dataclass | Data integrity |
| OT-06 | CorrelationContext via contextvars — async-safe | Async safety |
| OT-07 | CorrelationMiddleware sets context from TenantContext | Middleware |
| OT-08 | CorrelationMiddleware clears context on request completion | Cleanup |
| OT-09 | correlation_to_nats_headers() populates headers | NATS integration |
| OT-10 | nats_headers_to_correlation() reads headers | NATS integration |
| OT-11 | restore_correlation_from_nats() sets contextvars | NATS integration |
| OT-12 | trace_agent_operation() creates correctly named span | Convenience |
| OT-13 | configure_tracing() initializes without error | Setup |
| OT-14 | configure_logging() initializes without error | Setup |
| OT-15 | Console exporter in development mode | Default config |

### 5.5 Tenant Config Tests (30 tests)

Module: `tests/multi_tenant/test_tenant_config.py`

| ID | Test | Validates |
|----|------|-----------|
| TC-01 | TenantConfigSchema validation — valid config accepted | Schema |
| TC-02 | TenantConfigSchema validation — missing required fields rejected | Schema |
| TC-03 | TenantConfigSchema — tier-aware field limits enforced | Tier limits |
| TC-04 | TenantConfigSchema — 9-step onboarding model validation | Onboarding |
| TC-05 | TenantConfigProcessor — platform defaults applied | Layer 1 |
| TC-06 | TenantConfigProcessor — tier defaults override platform | Layer 2 |
| TC-07 | TenantConfigProcessor — tenant overrides top layer | Layer 3 |
| TC-08 | TenantConfigProcessor — merge order correct (platform → tier → tenant) | Merge |
| TC-09 | TenantConfigProcessor — 60s cache works | Caching |
| TC-10 | TenantConfigProcessor — cache invalidation per tenant | Cache invalidation |
| TC-11 | HTTP GET /api/config — returns resolved config | Endpoint |
| TC-12 | HTTP PUT /api/config — replaces config | Endpoint |
| TC-13 | HTTP PATCH /api/config — partial update | Endpoint |
| TC-14 | HTTP POST /api/config/onboarding — wizard submit | Endpoint |
| TC-15 | HTTP DELETE /api/config — reset to defaults | Endpoint |
| TC-16 | HTTP GET /api/config/preview — returns merged preview | Endpoint |
| TC-17 | HTTP GET /api/config/history — returns version history | Endpoint |
| TC-18 | HTTP GET /api/config/diff — returns diff between versions | Endpoint |
| TC-19 | Config endpoint — tenant isolation (no cross-tenant access) | Isolation |
| TC-20 | Config endpoint — unauthenticated → 401 | Auth |
| TC-21 | Config endpoint — Starter tier cannot access Pro-only fields | Tier enforcement |
| TC-22 | Config rollback to previous version | Versioning |
| TC-23 | Config validation rejects dangerous custom_instructions | Safety |
| TC-24 | Config change creates audit log entry | Audit |
| TC-25 | Onboarding wizard — step 1 through step 9 validation | Wizard |
| TC-26 | Onboarding wizard — partial progress saved | Wizard |
| TC-27 | Config with brand voice settings | Feature |
| TC-28 | Config with escalation rules | Feature |
| TC-29 | Config with response length preferences | Feature |
| TC-30 | Config with custom policies | Feature |

### 5.6 Dashboard & Usage API Tests (20 tests)

Module: `tests/multi_tenant/test_usage_dashboard.py`

| ID | Test | Validates |
|----|------|-----------|
| UD-01 | HTTP GET /api/dashboard/usage — returns usage counters | Endpoint |
| UD-02 | HTTP GET /api/dashboard/usage — includes allowance remaining | Data |
| UD-03 | HTTP GET /api/dashboard/usage — includes overage estimate | Data |
| UD-04 | HTTP GET /api/dashboard/usage — includes pack balance | Data |
| UD-05 | HTTP GET /api/dashboard/usage — includes active alerts | Data |
| UD-06 | HTTP GET /api/dashboard/usage/daily — per-day counts | Endpoint |
| UD-07 | HTTP GET /api/dashboard/usage/daily — aggregation correct | Data |
| UD-08 | HTTP GET /api/dashboard/conversations — paginated list | Endpoint |
| UD-09 | HTTP GET /api/dashboard/conversations — offset/limit params | Pagination |
| UD-10 | HTTP GET /api/dashboard/conversations — max 200 limit | Limit enforcement |
| UD-11 | HTTP GET /api/dashboard/conversations/{id} — full detail | Endpoint |
| UD-12 | HTTP GET /api/dashboard/conversations/{id} — unknown ID → 404 | Error |
| UD-13 | HTTP GET /api/dashboard/conversations/export — CSV format | Endpoint |
| UD-14 | HTTP GET /api/dashboard/conversations/export — 11 columns | CSV schema |
| UD-15 | HTTP GET /api/dashboard/conversations/export — StreamingResponse | Response type |
| UD-16 | Dashboard — tenant isolation enforced | Isolation |
| UD-17 | Dashboard — unauthenticated → 401 | Auth |
| UD-18 | Dashboard — services not wired → 503 | Startup guard |
| UD-19 | UsageDashboardResponse Pydantic model validation | Response model |
| UD-20 | ConversationDetailResponse Pydantic model validation | Response model |

### 5.7 Tenant Secret Service Tests (15 tests)

Module: `tests/multi_tenant/test_tenant_secret_service.py`

| ID | Test | Validates |
|----|------|-----------|
| TSS-01 | Create secret with tenant-{id}-{type} naming | CRUD |
| TSS-02 | Read secret from cache (within 5-min TTL) | Caching |
| TSS-03 | Read secret from Key Vault (cache miss) | Fallback |
| TSS-04 | Update secret invalidates cache | Cache invalidation |
| TSS-05 | Delete secret removes from Key Vault and cache | CRUD |
| TSS-06 | All 7 secret types supported (shopify_api_key, shopify_api_secret, zendesk_api_token, mailchimp_api_key, custom_integration, webhook_secret, encryption_key) | Type enum |
| TSS-07 | Cross-tenant secret access prevented | Isolation |
| TSS-08 | Health check — Key Vault reachable | Health |
| TSS-09 | Health check — Key Vault unreachable | Degraded health |
| TSS-10 | Initialize + close lifecycle | Lifecycle |
| TSS-11 | Singleton pattern — get_secret_service() | Singleton |
| TSS-12 | Cache TTL expiry triggers re-fetch | Cache behavior |
| TSS-13 | DefaultAzureCredential used | Authentication |
| TSS-14 | Secret naming validation — rejects invalid characters | Validation |
| TSS-15 | Concurrent access — thread-safe cache | Thread safety |

### 5.8 SystemPromptBuilder Tests (20 tests)

Module: `tests/multi_tenant/test_system_prompt_builder.py`

| ID | Test | Validates |
|----|------|-----------|
| SPB-01 | 4-layer assembly: platform → tier → tenant → customer | Layer ordering |
| SPB-02 | Platform base prompt present for all 6 agents | Platform layer |
| SPB-03 | Response Generator gets full persona + customer context | RG specialization |
| SPB-04 | Escalation Handler gets escalation rules + customer summary | ESC specialization |
| SPB-05 | Intent Classifier gets language support | IC specialization |
| SPB-06 | Critic/Supervisor prompt entirely immutable (no tenant config) | Critic safety |
| SPB-07 | custom_instructions sandboxed with advisory header | Safety |
| SPB-08 | Safety guardrails cannot be overridden by merchant config | Safety invariant |
| SPB-09 | build_all() returns dict[AgentRole, str] for all 6 agents | Convenience method |
| SPB-10 | explain() returns structured trace without prompt text | Explainability |
| SPB-11 | Starter tier capabilities section | Tier differentiation |
| SPB-12 | Professional tier capabilities section | Tier differentiation |
| SPB-13 | Enterprise tier capabilities section | Tier differentiation |
| SPB-14 | Customer context injection ~250 token budget | Token budget |
| SPB-15 | Empty customer profile → graceful degradation | Edge case |
| SPB-16 | Empty tenant config → platform defaults only | Edge case |
| SPB-17 | AgentRole enum covers all 6 pipeline agents | Enum completeness |
| SPB-18 | Stateless — same config produces identical prompts | Determinism |
| SPB-19 | PreferencesDocument compatibility | Input contract |
| SPB-20 | get_prompt_builder() singleton | Singleton |

**P1 Subtotal: 175 tests**

---

## 6. P2 — Launch Quality (~150 Tests)

### 6.1 Shopify Client Tests (15 tests)

Module: `tests/integrations/test_shopify_client.py`

| ID | Test | Validates |
|----|------|-----------|
| SHC-01 | GraphQL query construction | Query building |
| SHC-02 | GraphQL mutation construction | Mutation building |
| SHC-03 | httpx async client initialization | Client setup |
| SHC-04 | Shopify API version header | Version header |
| SHC-05 | Access token authorization header | Auth header |
| SHC-06 | Rate limit handling (429 → retry) | Rate limiting |
| SHC-07 | Network error → exception | Error handling |
| SHC-08 | GraphQL error response parsing | Error parsing |
| SHC-09 | Successful response parsing | Response parsing |
| SHC-10 | Connection pooling configuration | Performance |
| SHC-11 | Timeout configuration | Timeout |
| SHC-12 | Bulk operation support | Bulk ops |
| SHC-13 | Webhook HMAC verification | Security |
| SHC-14 | Pagination (cursor-based) | Pagination |
| SHC-15 | Session token API call | Auth flow |

### 6.2 Shopify Billing Tests (15 tests)

Module: `tests/integrations/test_shopify_billing.py`

| ID | Test | Validates |
|----|------|-----------|
| SHB-01 | appSubscriptionCreate — monthly Starter | Subscription creation |
| SHB-02 | appSubscriptionCreate — monthly Professional | Subscription creation |
| SHB-03 | appSubscriptionCreate — monthly Enterprise | Subscription creation |
| SHB-04 | appSubscriptionCreate — annual (no usage pricing) | Annual limitation |
| SHB-05 | Usage record creation — Decimal arithmetic | Billing precision |
| SHB-06 | Usage record — float rejected (must be Decimal) | Type safety |
| SHB-07 | Billing confirmation callback | Callback handling |
| SHB-08 | Subscription status check | Status query |
| SHB-09 | Subscription cancellation webhook | Lifecycle |
| SHB-10 | Tier upgrade mid-cycle | Tier change |
| SHB-11 | Tier downgrade mid-cycle | Tier change |
| SHB-12 | appPurchaseOneTimeCreate for annual overage | Annual workaround |
| SHB-13 | Billing error handling | Error paths |
| SHB-14 | Test mode vs production mode | Environment |
| SHB-15 | Return URL construction | URL building |

### 6.3 Stripe Checkout Deep Tests (10 tests)

Module: `tests/integrations/test_stripe_checkout_deep.py`

| ID | Test | Validates |
|----|------|-----------|
| SCD-01 | automatic_tax enabled on all sessions | Tax compliance |
| SCD-02 | tax_id_collection enabled | Tax ID capture |
| SCD-03 | Subscription mode for plans | Checkout mode |
| SCD-04 | Payment mode for packs | Checkout mode |
| SCD-05 | Success URL construction | URL building |
| SCD-06 | Cancel URL construction | URL building |
| SCD-07 | Metadata includes tier and channel | Metadata |
| SCD-08 | Annual discount pricing applied | Pricing |
| SCD-09 | Coupon application | Discounts |
| SCD-10 | Currency handling (USD) | Currency |

### 6.4 Response Explainability Tests (15 tests)

Module: `tests/multi_tenant/test_response_explainability.py`

| ID | Test | Validates |
|----|------|-----------|
| RE-01 | ResponseDecisionTrace captures profile factors | Trace content |
| RE-02 | ResponseDecisionTrace captures knowledge sources | Trace content |
| RE-03 | ResponseDecisionTrace captures memory signals | Trace content |
| RE-04 | ResponseDecisionTrace captures A/B variant | Trace content |
| RE-05 | ResponseDecisionTrace captures Critic assessment | Trace content |
| RE-06 | ResponseDecisionTrace captures stage attributions | Trace content |
| RE-07 | DecisionTraceBuilder fluent API | Builder pattern |
| RE-08 | DecisionTraceBuilder incremental construction | Builder pattern |
| RE-09 | to_dict() serialization | Serialization |
| RE-10 | from_dict() deserialization | Deserialization |
| RE-11 | Roundtrip (to_dict → from_dict) preserves all fields | Roundtrip |
| RE-12 | KnowledgeSource dataclass | Data model |
| RE-13 | MemorySignal dataclass | Data model |
| RE-14 | CriticAssessment dataclass | Data model |
| RE-15 | StageAttribution dataclass | Data model |

### 6.5 Customer Profile Service Deep Tests (15 tests)

Module: `tests/multi_tenant/test_customer_profile_deep.py`

| ID | Test | Validates |
|----|------|-----------|
| CPD-01 | Shopify sync adapter — order data mapping | Sync |
| CPD-02 | Shopify sync adapter — customer data mapping | Sync |
| CPD-03 | Shopify sync adapter — product question mapping | Sync |
| CPD-04 | get_available_layers() — Starter (L1, L2) | Tier awareness |
| CPD-05 | get_available_layers() — Professional (L1, L2, L3) | Tier awareness |
| CPD-06 | get_available_layers() — Enterprise (L1, L2, L3, L4) | Tier awareness |
| CPD-07 | get_history_depth_days() — Starter 90d | History depth |
| CPD-08 | get_history_depth_days() — Professional 365d | History depth |
| CPD-09 | get_history_depth_days() — Enterprise unlimited | History depth |
| CPD-10 | is_consent_granted() — granted | Consent |
| CPD-11 | is_consent_granted() — denied | Consent |
| CPD-12 | is_consent_granted() — not_asked | Consent |
| CPD-13 | Stale profile detection | Profile quality |
| CPD-14 | Empty profile detection | Profile quality |
| CPD-15 | get_profile_service() singleton | Singleton |

### 6.6 Conversation Vectorizer Deep Tests (15 tests)

Module: `tests/multi_tenant/test_conversation_vectorizer_deep.py`

| ID | Test | Validates |
|----|------|-----------|
| CVD-01 | Transcript chunking — 200-300 token chunks | Chunking |
| CVD-02 | Transcript chunking — short transcript single chunk | Edge case |
| CVD-03 | PII scrubbing before embedding | PII |
| CVD-04 | Embedding dimension — 3072 (text-embedding-3-large) | Embedding config |
| CVD-05 | Cosmos DB storage of vectors | Storage |
| CVD-06 | Semantic search — top-K retrieval | Search |
| CVD-07 | Semantic search — tier-gated depth (Starter 90d) | Tier restriction |
| CVD-08 | Semantic search — tier-gated depth (Professional 365d) | Tier restriction |
| CVD-09 | Semantic search — tier-gated depth (Enterprise unlimited) | Tier restriction |
| CVD-10 | compress_for_prompt() within ~300 token budget | Compression |
| CVD-11 | Consent-gated — vectorization skips when denied | Consent |
| CVD-12 | Consent-gated — search skips when denied | Consent |
| CVD-13 | Post-conversation pipeline end-to-end | Pipeline |
| CVD-14 | Multiple conversations — distinct vectors | Isolation |
| CVD-15 | Empty transcript → no vectors stored | Edge case |

### 6.7 Cross-Module Integration Tests (20 tests)

Module: `tests/test_cross_module.py`

| ID | Test | Validates |
|----|------|-----------|
| XM-01 | Auth → Rate Limit → Concurrency → Handler — full request | Full pipeline |
| XM-02 | Webhook → Provisioning → Tenant creation → Config defaults | Lifecycle |
| XM-03 | Checkout → Webhook → Provision → Usage meter ready | Onboarding |
| XM-04 | Tier upgrade → Rate limit change → Concurrency change | Tier change |
| XM-05 | Tier downgrade → Limits reduced | Tier change |
| XM-06 | Deactivation → All endpoints blocked (except health) | Deactivation |
| XM-07 | Reactivation → All endpoints restored | Reactivation |
| XM-08 | GDPR deletion → All data removed across stores | GDPR cascade |
| XM-09 | Consent denial → Layer 2-4 data auto-deleted | Consent |
| XM-10 | Profile update → SystemPromptBuilder reflects change | Profile → prompt |
| XM-11 | Config update → SystemPromptBuilder reflects change | Config → prompt |
| XM-12 | Conversation → Vectorize → Search → Prompt injection | L2 pipeline |
| XM-13 | Billing alert → Dashboard reflects alert | Alert visibility |
| XM-14 | Secret rotation → Cached secret invalidated | Secret lifecycle |
| XM-15 | Circuit breaker trip → /ready reports degraded | Health reporting |
| XM-16 | NATS disconnect → /ready reports disconnected | Health reporting |
| XM-17 | Rate limit hit → Usage dashboard shows limit | Visibility |
| XM-18 | Multi-tenant: 3 tenants, no data leakage | Isolation |
| XM-19 | Multi-tenant: 3 tiers, correct rate limits | Tier enforcement |
| XM-20 | Startup sequence — all events fire without error | Boot sequence |

### 6.8 Error Handling & Edge Cases (15 tests)

Module: `tests/test_error_handling.py`

| ID | Test | Validates |
|----|------|-----------|
| EH-01 | Cosmos DB unavailable → appropriate error response | Graceful degradation |
| EH-02 | Key Vault unavailable → appropriate error response | Graceful degradation |
| EH-03 | NATS unavailable → non-fatal, endpoints still work | Graceful degradation |
| EH-04 | Azure OpenAI unavailable → circuit breaker opens | Circuit breaker |
| EH-05 | Malformed JSON body → 422 | Input validation |
| EH-06 | Missing required headers → 400 | Input validation |
| EH-07 | Oversized request body → 413 | Limit enforcement |
| EH-08 | Invalid UUID format in path params → 400 | Input validation |
| EH-09 | Database timeout → 504 or retry | Timeout handling |
| EH-10 | Duplicate webhook delivery → idempotent (200) | Idempotency |
| EH-11 | Expired pack in FIFO → skipped, next pack used | Edge case |
| EH-12 | All packs expired → overage triggered | Edge case |
| EH-13 | Zero-conversation billing period → no alerts | Edge case |
| EH-14 | Config change during active conversation → applied to next | Consistency |
| EH-15 | Startup with missing env vars → graceful warnings | Boot resilience |

**P2 Subtotal: 135 tests**

---

## 7. P3 — Post-Launch / Continuous (~100 Tests)

### 7.1 Dispute Resolution Workflow Tests (10 tests)

Module: `tests/multi_tenant/test_dispute_resolution.py`

| ID | Test | Validates |
|----|------|-----------|
| DR-01 | Customer flags billing dispute | Initiation |
| DR-02 | Auto-review within 1 hour | SLA |
| DR-03 | Auto-credit on confirmed metering error | Resolution |
| DR-04 | Manual escalation within 24 hours | Escalation |
| DR-05 | Resolution within 48 hours | SLA |
| DR-06 | Dispute creates audit log entry | Audit |
| DR-07 | Dispute status tracking | Status |
| DR-08 | Multiple disputes from same tenant | Multi-dispute |
| DR-09 | Dispute on already-credited conversation | Idempotency |
| DR-10 | Dispute notification to merchant | Notification |

### 7.2 TenantUsageMonitor Tests (15 tests)

Module: `tests/multi_tenant/test_usage_monitor.py`

| ID | Test | Validates |
|----|------|-----------|
| TUM-01 | Watch state — normal usage | State machine |
| TUM-02 | Warn state — threshold exceeded | State machine |
| TUM-03 | Throttle state — rate reduced | State machine |
| TUM-04 | Isolate state — tenant isolated | State machine |
| TUM-05 | Progressive escalation: Watch → Warn → Throttle → Isolate | Full progression |
| TUM-06 | De-escalation when usage normalizes | Recovery |
| TUM-07 | Latency tracking (tenant causing high latency) | Metric |
| TUM-08 | Cosmos RU consumption tracking | Metric |
| TUM-09 | OpenAI token consumption tracking | Metric |
| TUM-10 | Error rate tracking | Metric |
| TUM-11 | Payload size tracking | Metric |
| TUM-12 | 5-minute rolling window | Window |
| TUM-13 | Multiple tenants — independent monitors | Multi-tenant |
| TUM-14 | Throttled tenant can still access health endpoints | Partial access |
| TUM-15 | Isolation creates audit log entry | Audit |

### 7.3 Archival Pipeline Tests (10 tests)

Module: `tests/multi_tenant/test_archival.py`

| ID | Test | Validates |
|----|------|-----------|
| AR-01 | Change Feed → Parquet conversion | Pipeline |
| AR-02 | Hot → Warm (Blob Cool) at 90 days | Lifecycle |
| AR-03 | Warm → Cold (Blob Archive) at 90+ days | Lifecycle |
| AR-04 | Cold → Delete at 7+ years | Lifecycle |
| AR-05 | Tenant-level purge cascades across all tiers | GDPR |
| AR-06 | Parquet format includes required fields | Format |
| AR-07 | CMK encryption on archived data | Encryption |
| AR-08 | Archive rehydration for ML training | Access |
| AR-09 | Archival does not include PII | Privacy |
| AR-10 | Daily Change Feed trigger fires | Scheduling |

### 7.4 Audit Log Query Tests (10 tests)

Module: `tests/multi_tenant/test_audit_log.py`

| ID | Test | Validates |
|----|------|-----------|
| AL-01 | All 12 event types can be created | Event types |
| AL-02 | Audit log is append-only (no delete/update) | Immutability |
| AL-03 | Time-partitioned queries | Performance |
| AL-04 | Query by event type | Filtering |
| AL-05 | Query by tenant_id | Filtering |
| AL-06 | Query by date range | Filtering |
| AL-07 | 1-year retention enforced | Retention |
| AL-08 | Audit log survives tenant deletion | Durability |
| AL-09 | Audit log API returns paginated results | API |
| AL-10 | Audit log export for compliance reporting | Export |

### 7.5 Data Retention Enforcement Tests (10 tests)

Module: `tests/multi_tenant/test_data_retention.py`

| ID | Test | Validates |
|----|------|-----------|
| DRT-01 | Starter 90-day history enforced | Tier retention |
| DRT-02 | Professional 365-day history enforced | Tier retention |
| DRT-03 | Enterprise unlimited history | Tier retention |
| DRT-04 | Automated cleanup job runs on schedule | Scheduling |
| DRT-05 | Cleanup respects consent status | Consent |
| DRT-06 | Cleanup creates audit log entries | Audit |
| DRT-07 | Cleanup deletes vectors but not profiles | Selective |
| DRT-08 | Cleanup handles large datasets (pagination) | Scale |
| DRT-09 | Cleanup idempotent on re-run | Idempotency |
| DRT-10 | Cleanup reports removed count | Metrics |

### 7.6 A/B Validation Framework Tests (10 tests)

Module: `tests/multi_tenant/test_ab_validation.py`

| ID | Test | Validates |
|----|------|-----------|
| AB-01 | Deterministic customer segmentation via hash | Segmentation |
| AB-02 | Control vs test group assignment | Group assignment |
| AB-03 | Test group receives variant config | Config routing |
| AB-04 | Control group receives baseline config | Config routing |
| AB-05 | 95% confidence interval calculation | Statistics |
| AB-06 | 5% minimum effect size detection | Statistics |
| AB-07 | Experiment lifecycle (start → monitor → end) | Lifecycle |
| AB-08 | Experiment results persistence | Storage |
| AB-09 | Auto-promotion on positive results | Automation |
| AB-10 | Rollback on negative results | Safety |

### 7.7 Layer 3 PatternExtractionService Tests (15 tests)

Module: `tests/persistent_memory/test_pattern_extraction.py`

| ID | Test | Validates |
|----|------|-----------|
| PE-01 | Communication style extraction | Extraction |
| PE-02 | Product preferences extraction | Extraction |
| PE-03 | Issue patterns extraction | Extraction |
| PE-04 | Satisfaction drivers extraction | Extraction |
| PE-05 | Decision-making style extraction | Extraction |
| PE-06 | Temporal patterns extraction | Extraction |
| PE-07 | Confidence scoring 0-1 range | Scoring |
| PE-08 | Patterns below 0.5 stored but not injected | Threshold |
| PE-09 | Monthly decay — 0.05/month without reinforcement | Decay |
| PE-10 | Pattern reinforcement resets decay | Reinforcement |
| PE-11 | Patterns merged into profile | Profile merge |
| PE-12 | ~100 token injection budget | Budget |
| PE-13 | Professional+ only (Starter blocked) | Tier gate |
| PE-14 | GPT-4o-mini used for extraction | Model selection |
| PE-15 | Consent-gated (denied → no extraction) | Consent |

### 7.8 Layer 4 Fine-Tuning Tests (10 tests)

Module: `tests/persistent_memory/test_fine_tuning.py`

| ID | Test | Validates |
|----|------|-----------|
| FT-01 | Data selection — quality filters applied | Pipeline |
| FT-02 | PII scrubbing before fine-tuning | Privacy |
| FT-03 | Minimum 1,000 conversations required | Quality gate |
| FT-04 | Azure OpenAI fine-tuning API call | API integration |
| FT-05 | Quality gate — model evaluation pass | Quality |
| FT-06 | Quality gate — model evaluation fail → abort | Safety |
| FT-07 | A/B validation — 20/80 split for 7 days | Deployment |
| FT-08 | Promotion on positive A/B results | Lifecycle |
| FT-09 | Rollback on negative A/B results | Safety |
| FT-10 | Enterprise add-on only ($299/mo gate) | Tier gate |

**P3 Subtotal: 90 tests**

---

## 8. Adversarial & Security Tests (~45 Tests)

Module: `tests/security/test_adversarial.py`

### 8.1 Tenant Isolation Attacks (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| SEC-01 | Tenant A's API key cannot access Tenant B's data | Data isolation |
| SEC-02 | Tenant A's token cannot query Tenant B's conversations | Query isolation |
| SEC-03 | Tenant A cannot subscribe to Tenant B's NATS topics | NATS isolation |
| SEC-04 | Tenant A cannot publish to Tenant B's NATS topics | NATS isolation |
| SEC-05 | Manipulated tenant_id in request body ignored (server-derived only) | Auth integrity |
| SEC-06 | Cosmos DB query injection attempt → blocked by tenant_id filter | Query safety |
| SEC-07 | Path traversal in tenant_id parameter → rejected | Input validation |
| SEC-08 | Config API — cross-tenant config read → 403/404 | Config isolation |
| SEC-09 | Dashboard API — cross-tenant usage read → 403/404 | Dashboard isolation |
| SEC-10 | Secret Service — cross-tenant secret read → denied | Secret isolation |

### 8.2 Authentication Bypass Attempts (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| SEC-11 | Missing Authorization header → 401 | Auth required |
| SEC-12 | Expired JWT → 401 | Token validation |
| SEC-13 | JWT signed with wrong secret → 401 | Signature validation |
| SEC-14 | JWT with non-.myshopify.com domain → 401 | Domain validation |
| SEC-15 | API key with valid hash but deactivated tenant → 403 | Status check |
| SEC-16 | Replay of old API key (after rotation) → 401 | Key rotation |
| SEC-17 | Bearer token with SQL injection payload → rejected | Input sanitization |
| SEC-18 | Bearer token with XXE payload → rejected | Input sanitization |
| SEC-19 | Extremely long API key (>10KB) → rejected | Length validation |
| SEC-20 | null bytes in API key → rejected | Input sanitization |

### 8.3 Rate Limit & Resource Exhaustion (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| SEC-21 | Burst of 100 requests in 1 second → rate limited | Burst protection |
| SEC-22 | Concurrent connections at 2x concurrency limit → queued/rejected | Concurrency |
| SEC-23 | Extremely large request body (>1MB) → rejected | Body limit |
| SEC-24 | Slowloris-style slow request → timeout | Timeout |
| SEC-25 | Rapid API key rotation attempts → rate limited | Rate limit |
| SEC-26 | Webhook replay attack (same event_id) → deduplicated | Idempotency |
| SEC-27 | Invalid Stripe webhook signature → rejected | Signature verification |
| SEC-28 | Oversized webhook payload → rejected | Size limit |
| SEC-29 | Recursive/nested JSON (1000 levels) → rejected | Depth limit |
| SEC-30 | Unicode normalization attack in tenant_id → rejected | Input normalization |

### 8.4 Prompt Injection & AI Safety (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| SEC-31 | custom_instructions with "ignore all rules" → sandboxed | Prompt safety |
| SEC-32 | custom_instructions with system prompt extraction → sandboxed | Prompt safety |
| SEC-33 | Customer message with prompt injection → Critic catches | Critic validation |
| SEC-34 | Customer message requesting PII of other customers → blocked | Privacy |
| SEC-35 | Response containing PII → Critic flags | PII detection |
| SEC-36 | Critic bypass attempt (spoofed approval) → fail-closed | Critic integrity |
| SEC-37 | SystemPromptBuilder — platform base cannot be overridden | Immutability |
| SEC-38 | SystemPromptBuilder — Critic prompt has zero merchant content | Critic isolation |
| SEC-39 | Response with markdown/HTML injection → sanitized | Output sanitization |
| SEC-40 | Jailbreak pattern in customer context → does not alter system prompt | Context isolation |

### 8.5 GDPR Attack Vectors (5 tests)

| ID | Test | Validates |
|----|------|-----------|
| SEC-41 | Data export request for different tenant → denied | Export isolation |
| SEC-42 | Data deletion request for different tenant → denied | Deletion isolation |
| SEC-43 | Consent change for different customer → denied | Consent isolation |
| SEC-44 | PII appears in Application Insights logs → not found (scrubbed) | Log privacy |
| SEC-45 | Deleted customer's data not returned by any API → confirmed | Deletion verification |

**Adversarial Subtotal: 45 tests**

---

## 9. Performance & Load Tests (~30 Tests)

Module: `tests/performance/` (requires separate runner, not standard pytest)

### 9.1 Latency Validation (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| PERF-01 | P50 latency < 1,500ms (single request, warm) | SLA: P50 |
| PERF-02 | P95 latency < 2,000ms (single request, warm) | SLA: P95 |
| PERF-03 | P99 latency < 5,000ms (single request, warm) | SLA: P99 |
| PERF-04 | Per-stage: Intent Classifier < 800ms | Stage budget |
| PERF-05 | Per-stage: Knowledge Retrieval < 1,000ms | Stage budget |
| PERF-06 | Per-stage: Response Generator < 3,000ms | Stage budget |
| PERF-07 | Per-stage: Critic < 800ms | Stage budget |
| PERF-08 | Cold start latency < 5,000ms (first request after deploy) | Cold start |
| PERF-09 | Health check latency < 100ms | Health probe |
| PERF-10 | Config endpoint latency < 200ms (cached) | Cache performance |

### 9.2 Throughput & Concurrency (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| PERF-11 | 10 concurrent users — no errors | Base concurrency |
| PERF-12 | 50 concurrent users — P95 within SLA | Medium load |
| PERF-13 | 100 concurrent users — P95 within SLA | Target load |
| PERF-14 | 3 tenants × 10 concurrent each — no cross-tenant degradation | Multi-tenant |
| PERF-15 | Starter tenant at concurrency limit (3) — others unaffected | Noisy neighbor |
| PERF-16 | Sustained 100 req/min for 10 minutes — no memory leak | Stability |
| PERF-17 | Auto-scale trigger — replicas increase under load | KEDA scaling |
| PERF-18 | Scale-down — replicas decrease after load | KEDA scaling |
| PERF-19 | Rate limit enforcement under load — 429 at correct threshold | Rate limiting |
| PERF-20 | Circuit breaker — trips under sustained external failure | Resilience |

### 9.3 Streaming & Optimization (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| PERF-21 | SSE streaming — first token < 500ms (time-to-first-token) | Streaming TTFT |
| PERF-22 | SSE streaming — connection kept alive for full response | Streaming stability |
| PERF-23 | SSE streaming — error mid-stream handled gracefully | Streaming error |
| PERF-24 | SSE streaming — multiple concurrent streams | Streaming concurrency |
| PERF-25 | IC + KR parallelization — latency reduction measured | Parallelization |
| PERF-26 | Prompt prefix caching — cache hit rate measured | Caching |
| PERF-27 | Semantic caching — cache hit returns < 100ms | Caching |
| PERF-28 | Semantic caching — cache miss falls through to full pipeline | Caching fallthrough |
| PERF-29 | Prompt optimization — response quality not degraded | Quality regression |
| PERF-30 | Model routing — GPT-4o-mini for simple queries | Routing |

**Performance Subtotal: 30 tests**

---

## 10. Trial / Demo Environment Tests (~20 Tests)

Module: `tests/test_trial_environment.py`

### 10.1 Trial Lifecycle (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| TRIAL-01 | Trial creation — TenantTier.TRIAL set | Provisioning |
| TRIAL-02 | Trial — 14-day expiry enforced | Duration |
| TRIAL-03 | Trial — conversation cap (50-100) enforced | Limits |
| TRIAL-04 | Trial — GPT-4o-mini model routing (not GPT-4o) | Cost containment |
| TRIAL-05 | Trial expiry → GRACE_PERIOD → DEACTIVATED | Lifecycle |
| TRIAL-06 | Trial → Paid conversion (tier upgrade) | Conversion |
| TRIAL-07 | Trial → Paid — conversation history preserved | Data continuity |
| TRIAL-08 | Trial expiry scanner detects expired trials | Scanner |
| TRIAL-09 | Trial — no billing events generated | Billing isolation |
| TRIAL-10 | Trial — dashboard shows trial-specific counters | UI |

### 10.2 Demo & Sandbox (10 tests)

| ID | Test | Validates |
|----|------|-----------|
| DEMO-01 | Demo data seeder — creates realistic sample data | Data seeding |
| DEMO-02 | Demo data — includes sample conversations | Sample data |
| DEMO-03 | Demo data — includes sample customer profiles | Sample data |
| DEMO-04 | Trial tenant isolation from paid tenants | Isolation |
| DEMO-05 | Trial rate limits (lower than Starter) | Rate limits |
| DEMO-06 | Trial concurrency limits (lower than Starter) | Concurrency |
| DEMO-07 | Trial metrics excluded from platform-wide reporting | Metric isolation |
| DEMO-08 | Expired trial data cleanup (30 days after expiry) | Cleanup |
| DEMO-09 | Trial — all Professional features accessible (preview) | Feature preview |
| DEMO-10 | Trial — Persistent Memory Layers 1-2 enabled | Feature preview |

**Trial Subtotal: 20 tests**

---

## 11. UI-Type × Task-Type Validation Tests (~100 Tests)

These tests validate that all operational tasks are achievable through their current interface types, and that the API contracts support future UI development.

Module: `tests/test_ui_task_matrix.py`

### 11.1 REST API Contract Tests (40 tests)

| ID | Test | Validates |
|----|------|-----------|
| UIT-01 | All 30 endpoints return correct Content-Type | API contract |
| UIT-02 | All endpoints return structured error responses (not raw exceptions) | Error format |
| UIT-03 | All endpoints include request-id in response headers | Traceability |
| UIT-04 | Pagination endpoints accept offset + limit params | Pagination |
| UIT-05 | Pagination endpoints return total count | Pagination |
| UIT-06 | CSV export returns correct Content-Type (text/csv) | Export format |
| UIT-07 | All POST endpoints validate request body schema | Input validation |
| UIT-08 | All endpoints return 401 for unauthenticated requests | Auth consistency |
| UIT-09 | All endpoints return 403 for insufficient tier | Tier consistency |
| UIT-10 | All endpoints accept and propagate correlation ID | Traceability |
| UIT-11 | GET /api/config returns JSON schema metadata (for UI rendering) | UI support |
| UIT-12 | GET /api/config/preview returns diff-friendly format | UI support |
| UIT-13 | GET /api/dashboard/usage returns chart-friendly format | UI support |
| UIT-14 | GET /api/dashboard/usage/daily returns time-series format | UI support |
| UIT-15 | Webhook endpoints return 200 within 5 seconds | Webhook SLA |
| UIT-16 | Stripe webhook signature validation before processing | Security |
| UIT-17 | OpenAPI schema generated correctly (/openapi.json in dev) | Documentation |
| UIT-18 | /docs endpoint available in development mode | Documentation |
| UIT-19 | /docs endpoint hidden in production mode | Security |
| UIT-20 | /redoc endpoint available in development mode | Documentation |
| UIT-21 | All Pydantic response models serializable | Serialization |
| UIT-22 | All endpoints handle Accept-Language header (future i18n) | i18n readiness |
| UIT-23 | CORS headers present on all responses | CORS |
| UIT-24 | CORS restricted to APP_CORS_ORIGINS in production | CORS security |
| UIT-25 | All 10 config endpoints accessible via REST | Config API |
| UIT-26 | All 5 dashboard endpoints accessible via REST | Dashboard API |
| UIT-27 | Billing portal URL returned for Stripe merchants | Billing |
| UIT-28 | Shopify billing confirmation URL returned | Billing |
| UIT-29 | Tenant lookup supports both domain and API key | Lookup |
| UIT-30 | Checkout session returns redirect URL | Checkout |
| UIT-31 | Pack purchase returns checkout URL | Packs |
| UIT-32 | Usage record accepts conversation_id | Usage |
| UIT-33 | Conversation detail returns full billing attribution | Audit |
| UIT-34 | Config history returns versioned snapshots | History |
| UIT-35 | Config diff returns field-level changes | Diff |
| UIT-36 | Onboarding wizard accepts partial submission | Wizard |
| UIT-37 | Config reset returns new default state | Reset |
| UIT-38 | All endpoints handle empty database gracefully | Empty state |
| UIT-39 | Rate limit headers (X-RateLimit-Remaining, X-RateLimit-Limit) in responses | Rate limit visibility |
| UIT-40 | 429 responses include Retry-After header | Rate limit feedback |

### 11.2 Terraform / Infrastructure Validation (15 tests)

These are infrastructure-as-code validation tests (run via `terraform validate` + `terraform plan`).

| ID | Test | Validates |
|----|------|-----------|
| UIT-41 | Terraform validates without errors | IaC syntax |
| UIT-42 | Terraform plan — no unexpected destroys | Safety |
| UIT-43 | Health probes configured for all 9 containers | Health |
| UIT-44 | Rolling deployment with 60s drain configured | Deployment |
| UIT-45 | CMK key vault access policy configured | Encryption |
| UIT-46 | Cosmos DB continuous backup enabled | DR |
| UIT-47 | Archival storage lifecycle rules configured | Lifecycle |
| UIT-48 | Container min replicas match Option B+ | Scaling |
| UIT-49 | KEDA scaling profiles defined | Scaling |
| UIT-50 | Network security rules — no public Cosmos DB access | Network security |
| UIT-51 | Key Vault firewall rules configured | Secret security |
| UIT-52 | Application Insights connection configured | Observability |
| UIT-53 | Container resource limits defined (CPU, memory) | Resource mgmt |
| UIT-54 | Environment variables template complete | Configuration |
| UIT-55 | prevent_destroy on Cosmos DB account | Safety |

### 11.3 Environment Variable & Configuration Tests (15 tests)

| ID | Test | Validates |
|----|------|-----------|
| UIT-56 | ENVIRONMENT=development enables /docs | Feature flag |
| UIT-57 | ENVIRONMENT=production disables /docs | Feature flag |
| UIT-58 | APP_CORS_ORIGINS restricts CORS | Security config |
| UIT-59 | LOG_LEVEL controls logging verbosity | Logging config |
| UIT-60 | NATS_URL configures NATS connection | Service config |
| UIT-61 | AZURE_KEYVAULT_URL configures Key Vault | Service config |
| UIT-62 | OTEL_EXPORTER_TYPE=console for development | Tracing config |
| UIT-63 | APPLICATIONINSIGHTS_CONNECTION_STRING for production | Tracing config |
| UIT-64 | STRIPE_WEBHOOK_SECRET configures signature verification | Billing config |
| UIT-65 | SHOPIFY_API_KEY + SHOPIFY_API_SECRET for Shopify auth | Billing config |
| UIT-66 | Missing required env var → startup warning (not crash) | Resilience |
| UIT-67 | .env.example contains all required variables | Documentation |
| UIT-68 | No secrets in .env.example | Security |
| UIT-69 | Config inheritance: env var → default value | Precedence |
| UIT-70 | Invalid env var value → appropriate error/warning | Validation |

### 11.4 CLI & Script Validation Tests (15 tests)

| ID | Test | Validates |
|----|------|-----------|
| UIT-71 | create_product_catalog.py — creates all 27 Stripe objects | Catalog script |
| UIT-72 | create_product_catalog.py — idempotent (re-run safe) | Idempotency |
| UIT-73 | update_tax_codes.py — updates existing products | Tax script |
| UIT-74 | stripe_product_ids.json — valid JSON schema | Config file |
| UIT-75 | stripe_product_ids.json — all 27 IDs present | Completeness |
| UIT-76 | uvicorn startup command works | App boot |
| UIT-77 | uvicorn with --reload for development | Dev mode |
| UIT-78 | pip install -r requirements.txt succeeds | Dependencies |
| UIT-79 | All imports resolve without error | Import validation |
| UIT-80 | pytest discovery finds all test files | Test discovery |
| UIT-81 | pytest markers recognized (unit, integration, e2e) | Test config |
| UIT-82 | Docker build succeeds | Container build |
| UIT-83 | Docker compose up starts all services | Container orchestration |
| UIT-84 | Health check passes after Docker compose up | Container health |
| UIT-85 | Git hooks (if configured) run without error | Dev workflow |

### 11.5 Monitoring & Observability Validation (15 tests)

| ID | Test | Validates |
|----|------|-----------|
| UIT-86 | Structured logs include tenant_id | Log format |
| UIT-87 | Structured logs include conversation_id | Log format |
| UIT-88 | Structured logs include trace_id | Log format |
| UIT-89 | No PII in structured logs | Privacy |
| UIT-90 | OpenTelemetry spans have tenant_id attribute | Span attributes |
| UIT-91 | OpenTelemetry spans have correct operation names | Span naming |
| UIT-92 | Circuit breaker state changes logged | Event logging |
| UIT-93 | Rate limit events logged (with tenant_id) | Event logging |
| UIT-94 | Authentication failures logged (without credentials) | Security logging |
| UIT-95 | Startup events logged | Boot logging |
| UIT-96 | Shutdown events logged | Shutdown logging |
| UIT-97 | Health check does not generate excessive logs | Log volume |
| UIT-98 | Audit events include all required fields (12 event types) | Audit completeness |
| UIT-99 | Correlation ID appears in all related log entries | Correlation |
| UIT-100 | Application Insights custom dimensions populated | APM |

**UI-Type Subtotal: 100 tests**

---

## 12. Summary & Metrics

### Test Count by Priority

| Priority | Category | Test Count | Status |
|----------|----------|------------|--------|
| — | Existing tests | 125 | ✅ Passing |
| P0 | Launch blockers | 160 | ❌ Not started |
| P1 | Pre-launch required | 175 | ❌ Not started |
| P2 | Launch quality | 135 | ❌ Not started |
| P3 | Post-launch / continuous | 90 | ❌ Not started |
| — | Adversarial & security | 45 | ❌ Not started |
| — | Performance & load | 30 | ❌ Not started |
| — | Trial / demo environment | 20 | ❌ Not started |
| — | UI-type × task-type | 100 | ❌ Not started |
| **Total** | | **~880** | |

### Test Count by Module Under Test

| Module | Existing | Planned | Total |
|--------|----------|---------|-------|
| auth.py + middleware.py | 57 | ~25 (MWP) | ~82 |
| provisioning.py + stripe_webhooks.py | 38 | ~35 (HTTP-BILL) | ~73 |
| customer_profile_service.py | 6 | ~15 (CPD) | ~21 |
| conversation_vectorizer.py | 6 | ~15 (CVD) | ~21 |
| response_explainability.py | ~8 | ~15 (RE) | ~23 |
| conversation_meter.py | 0 | ~30 (CM) | ~30 |
| critic_policy.py | 0 | ~20 (CP) | ~20 |
| nats_isolation.py | 0 | ~25 (NI) | ~25 |
| gdpr_services.py | 0 | ~30 (GDPR) | ~30 |
| pipeline_resilience.py | 0 | ~20 (PR) | ~20 |
| otel_tracing.py | 0 | ~15 (OT) | ~15 |
| tenant_config_*.py | 0 | ~30 (TC) | ~30 |
| usage_dashboard_api.py | 0 | ~20 (UD) | ~20 |
| tenant_secret_service.py | 0 | ~15 (TSS) | ~15 |
| system_prompt_builder.py | 0 | ~20 (SPB) | ~20 |
| cosmos_schema.py + repository.py + cosmos_client.py | 0 | ~25 (CR) | ~25 |
| stripe_checkout.py | 0 | ~20 (HTTP-BILL + SCD) | ~20 |
| stripe_packs.py | 0 | ~10 (HTTP-BILL) | ~10 |
| stripe_portal.py | 0 | ~5 (HTTP-BILL) | ~5 |
| stripe_usage.py | 0 | ~10 (HTTP-BILL + UC) | ~10 |
| shopify_billing.py + shopify_client.py | 0 | ~30 (SHB + SHC) | ~30 |
| stripe_catalog.py | 0 | ~5 (SC) | ~5 |
| main.py (app, startup, health) | 0 | ~10 (HE) | ~10 |
| Cross-module integration | 10 | ~20 (XM) | ~30 |
| Adversarial / security | 0 | ~45 (SEC) | ~45 |
| Performance / load | 0 | ~30 (PERF) | ~30 |
| Trial / demo | 0 | ~20 (TRIAL/DEMO) | ~20 |
| UI-type / infrastructure | 0 | ~100 (UIT) | ~100 |
| Error handling | 0 | ~15 (EH) | ~15 |
| Post-launch (dispute, monitor, archival, audit, retention, A/B, L3, L4) | 0 | ~90 (P3) | ~90 |

### Test File Organization (Proposed)

```
tests/
├── conftest.py                           # Shared fixtures, TestClient, mocks
├── test_health.py                        # HE-01 to HE-10
├── test_cross_module.py                  # XM-01 to XM-20
├── test_error_handling.py                # EH-01 to EH-15
├── test_trial_environment.py             # TRIAL-01 to TRIAL-10, DEMO-01 to DEMO-10
├── test_ui_task_matrix.py                # UIT-01 to UIT-100
├── integrations/
│   ├── test_provisioning_webhooks.py     # EXISTING (38 tests)
│   ├── test_http_billing.py             # HTTP-BILL-01 to HTTP-BILL-35
│   ├── test_usage_consumption.py        # UC-01 to UC-10
│   ├── test_shopify_client.py           # SHC-01 to SHC-15
│   ├── test_shopify_billing.py          # SHB-01 to SHB-15
│   ├── test_stripe_checkout_deep.py     # SCD-01 to SCD-10
│   └── test_stripe_catalog.py           # SC-01 to SC-05
├── multi_tenant/
│   ├── test_auth_middleware.py           # EXISTING (57 tests)
│   ├── test_middleware_pipeline.py       # MWP-01 to MWP-25
│   ├── test_conversation_meter.py       # CM-01 to CM-30
│   ├── test_critic_policy.py            # CP-01 to CP-20
│   ├── test_cosmos_repository.py        # CR-01 to CR-25
│   ├── test_nats_isolation.py           # NI-01 to NI-25
│   ├── test_gdpr_services.py            # GDPR-01 to GDPR-30
│   ├── test_pipeline_resilience.py      # PR-01 to PR-20
│   ├── test_otel_tracing.py             # OT-01 to OT-15
│   ├── test_tenant_config.py            # TC-01 to TC-30
│   ├── test_usage_dashboard.py          # UD-01 to UD-20
│   ├── test_tenant_secret_service.py    # TSS-01 to TSS-15
│   ├── test_system_prompt_builder.py    # SPB-01 to SPB-20
│   ├── test_customer_profile_deep.py    # CPD-01 to CPD-15
│   ├── test_conversation_vectorizer_deep.py  # CVD-01 to CVD-15
│   ├── test_response_explainability.py  # RE-01 to RE-15
│   ├── test_dispute_resolution.py       # DR-01 to DR-10
│   ├── test_usage_monitor.py            # TUM-01 to TUM-15
│   ├── test_archival.py                 # AR-01 to AR-10
│   ├── test_audit_log.py               # AL-01 to AL-10
│   ├── test_data_retention.py           # DRT-01 to DRT-10
│   └── test_ab_validation.py            # AB-01 to AB-10
├── persistent_memory/
│   ├── fixtures.py                      # EXISTING
│   ├── test_unit_layers.py              # EXISTING (20 tests)
│   ├── test_integration_layers.py       # EXISTING (10 tests)
│   ├── test_pattern_extraction.py       # PE-01 to PE-15
│   └── test_fine_tuning.py              # FT-01 to FT-10
├── security/
│   └── test_adversarial.py              # SEC-01 to SEC-45
└── performance/
    └── (load test configs — Locust/k6)  # PERF-01 to PERF-30
```

### Implementation Order Recommendation

1. **Infrastructure first:** conftest.py, pyproject.toml, requirements-test.txt, GitHub Actions workflow
2. **P0 launch blockers:** HTTP billing tests, middleware pipeline, ConversationMeter, CriticPolicy, Cosmos repository, health endpoints
3. **P1 pre-launch:** NATS, GDPR, pipeline resilience, tracing, config, dashboard, secrets, prompt builder
4. **Security:** Adversarial tests (can run in parallel with P1)
5. **P2 launch quality:** Shopify client/billing, Stripe deep tests, explainability, profile, vectorizer, cross-module, error handling
6. **Performance:** Load tests (requires staging environment)
7. **Trial/demo:** After trial environment implementation
8. **UI-type validation:** API contract and infrastructure tests
9. **P3 post-launch:** Dispute resolution, usage monitor, archival, audit, retention, A/B, L3/L4

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
