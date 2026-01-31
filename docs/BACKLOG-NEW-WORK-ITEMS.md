# New Work Items Backlog — Agent Red Customer Engagement

> **Status:** Unprioritized backlog — items inferred from Test Coverage Audit (2026-01-31)
> **Project:** Agent Red Customer Engagement
> **Owner:** Remaker Digital (DBA of VanDusen & Palmeter, LLC)
> **Created:** 2026-01-31
> **Numbering:** Continues from Master Plan Review WI #1-100
> **Review Status:** Pending prioritization and refinement

---

## Table of Contents

1. [Test Infrastructure](#1-test-infrastructure-wi-101-107)
2. [Merchant Web UI](#2-merchant-web-ui-wi-108-118)
3. [Trial / Demo Environment](#3-trial--demo-environment-wi-119-128)
4. [Response Streaming (SSE)](#4-response-streaming-sse-wi-129-133)
5. [Pipeline Optimization](#5-pipeline-optimization-wi-134-139)
6. [API Completeness](#6-api-completeness-wi-140-147)
7. [Operational Readiness](#7-operational-readiness-wi-148-156)
8. [Security Hardening](#8-security-hardening-wi-157-163)
9. [Summary](#9-summary)

---

## 1. Test Infrastructure (WI #101-107)

These work items address the complete absence of test infrastructure beyond the test files themselves.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 101 | Create pytest configuration (pyproject.toml with markers, asyncio mode, coverage settings) | High | No pytest.ini/pyproject.toml exists. Tests discovered by convention only. No markers (unit, integration, e2e, slow) defined. |
| 102 | Create test requirements file (requirements-test.txt: pytest, pytest-asyncio, pytest-cov, httpx for TestClient) | High | Test dependencies not separated from production dependencies. pytest-asyncio needed for all async tests. |
| 103 | Create shared test fixtures (tests/conftest.py: FastAPI TestClient, mock Cosmos DB, mock NATS, mock Key Vault, authenticated request helpers, tenant context factories) | High | Every planned HTTP-level test requires TestClient. Currently 0 HTTP endpoint tests exist. Fixtures duplicated across test files (tenant context helpers in test_auth_middleware.py only). |
| 104 | Create GitHub Actions CI workflow for pytest (run on PR, run on push to main, fail on test failure) | High | No CI pipeline exists for Python tests. All 125 tests run locally only. No automated quality gate on PRs. |
| 105 | Configure coverage reporting and gate (target: 80%+ line coverage, fail PR below threshold) | Medium | No coverage measurement. Current estimated coverage ~25-30% of public interfaces. |
| 106 | Extract and centralize tenant context factory functions from test_auth_middleware.py into conftest.py | Medium | _starter_context(), _pro_context(), _enterprise_context() helpers are defined in one test file but needed by most planned test files. |
| 107 | Create performance test infrastructure (Locust or k6 configuration, separate from pytest) | Medium | Zero load/performance tests exist. SLA commitments (P50 < 1,500ms, P95 < 2,000ms) are unvalidated. |

---

## 2. Merchant Web UI (WI #108-118)

The platform currently has **no web UI**. All 30 REST API endpoints, 10 config endpoints, and 5 dashboard endpoints are API-only. Merchants must interact via direct API calls, Stripe Dashboard, Shopify Partner Dashboard, or Azure Portal across 9+ interface types. This is the single largest gap identified in the audit.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 108 | Evaluate and select frontend framework for merchant dashboard (React, Next.js, or similar) | High | No web UI exists. Merchants currently cannot configure their tenant, view usage, manage billing, or perform any self-service operation through a unified interface. |
| 109 | Implement merchant authentication UI (login page, API key display, Shopify OAuth flow) | High | Merchants currently have no way to authenticate to their dashboard without raw API calls. |
| 110 | Implement usage dashboard UI (real-time counters, daily volume chart, allowance remaining, overage estimate) | High | 5 dashboard API endpoints exist (GET /api/dashboard/*) but have no frontend consumer. Usage transparency (Decision #25) requires merchant-facing presentation. |
| 111 | Implement conversation audit trail UI (paginated list, detail view, CSV export button) | Medium | Per-conversation audit trail (Decision #25, Layer 2) is API-only. Merchants cannot browse or export billing details without curl/Postman. |
| 112 | Implement tenant configuration UI with 9-step onboarding wizard | Medium | 10 config API endpoints exist (GET/PUT/PATCH/POST/DELETE /api/config/*) but have no frontend. Decision #22 calls for "pervasive tooltips, documentation links, live preview, contextual data adjacent to every decision." None of this can be delivered without a UI. |
| 113 | Implement billing management UI (current plan, upgrade/downgrade, pack purchase, payment method via Stripe Portal redirect) | Medium | Stripe Customer Portal handles payment details, but there's no merchant-facing page to trigger it, view current plan, or purchase conversation packs. |
| 114 | Implement GDPR consent management UI (consent status, data export request, data deletion request) | Medium | ConsentManager, DataExportService, and DataDeletionService exist as services (gdpr_services.py) but have no API endpoints or UI for merchants/customers to exercise their GDPR rights. |
| 115 | Implement customer profile viewer UI (Layer 1 profile data, Layer 3 patterns if Professional+) | Low | CustomerProfileService exists but merchants cannot view individual customer profiles or the data driving personalization. |
| 116 | Implement response explainability viewer UI (per-response decision trace) | Low | ResponseDecisionTrace (response_explainability.py) captures detailed per-response reasoning but there's no way for merchants to view it outside of API calls. |
| 117 | Implement alert notification UI (billing alerts, usage warnings, system status) | Medium | ConversationMeter generates alerts at 80%/100% thresholds but alerts have no delivery mechanism (no email, no UI banner, no webhook to merchant). |
| 118 | Implement brand/theme customization UI (white-label settings, logo upload, color picker) | Low | White-label features listed as Enterprise-only commercial differentiator but no implementation exists. |

---

## 3. Trial / Demo Environment (WI #119-128)

No trial or demo capability exists. Prospective customers cannot evaluate the product before purchasing.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 119 | Add TenantTier.TRIAL to TenantTier enum and TIER_DEFAULTS | High | cosmos_schema.py defines Starter/Professional/Enterprise but no Trial tier. Trial tenants need distinct rate limits, concurrency, and feature access. |
| 120 | Implement trial provisioning flow (14-day trial creation without billing) | High | No way to create a tenant without a Stripe/Shopify subscription. Shopify convention is 14-day trials. |
| 121 | Implement trial expiry mechanism (trial_expires_at field, expiry scanner job) | High | No scheduled job infrastructure exists. Trials must expire automatically and transition through GRACE_PERIOD → DEACTIVATED. |
| 122 | Implement trial conversation cap (50-100 conversations during trial) | Medium | Trial tenants need a hard cap to prevent abuse. ConversationMeter currently only supports tier-based included allowances (1K/5K/20K). |
| 123 | Implement trial model routing (GPT-4o-mini for all agents during trial) | Medium | Cost containment: trial conversations should use cheaper model. SystemPromptBuilder and pipeline routing need tier-aware model selection. |
| 124 | Implement trial → paid conversion flow (preserve data, upgrade tier, start billing) | High | No upgrade path exists. Trial data (conversations, profiles, config) must carry over to paid subscription. |
| 125 | Implement demo data seeder (sample conversations, customer profiles, usage data for empty trial tenants) | Medium | Empty dashboard provides poor first impression. Seeded demo data shows merchants what the product looks like with real traffic. |
| 126 | Implement trial-specific dashboard view (trial days remaining, conversation cap usage, upgrade CTA) | Medium | Dashboard API returns Starter/Professional/Enterprise counters. Trial tenants need distinct UI showing trial-specific constraints and conversion prompt. |
| 127 | Implement expired trial data cleanup (30 days after expiry, delete all tenant data) | Low | GDPR requires data minimization. Expired trial tenants should not persist indefinitely. |
| 128 | Implement trial metrics isolation (exclude trial conversations from platform-wide benchmarks) | Low | Trial traffic should not contaminate analytics, cost reporting, or performance benchmarks used for paid tenant SLAs. |

---

## 4. Response Streaming (SSE) (WI #129-133)

Agent Red currently returns complete responses only. SSE streaming would reduce perceived latency by 70-85% (from 1,500ms P50 to ~200-400ms time-to-first-token) at zero marginal cost.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 129 | Implement SSE (Server-Sent Events) streaming endpoint for conversation responses | High | Highest-impact P50 reduction option. Zero infrastructure cost. Azure OpenAI supports streaming natively. Current pipeline returns full response only after all 4 stages complete (~1,500ms). Streaming would deliver first token after IC + KR + RG first-token (~200-400ms). |
| 130 | Implement streaming-compatible Critic validation (validate chunks or post-stream) | High | Fail-closed Critic policy (Decision #16) requires all responses pass safety validation. Streaming requires either chunk-level validation or hold-and-release pattern (buffer → validate → stream). Design decision needed. |
| 131 | Implement SSE error handling (mid-stream errors, connection drops, retry logic) | Medium | Streaming connections can fail mid-response. Need graceful error events, client retry guidance, and partial response cleanup. |
| 132 | Update conversation metering for streaming (billable at first chunk, not response completion) | Medium | ConversationMeter starts billing on first AI response. With streaming, this is the first chunk, not the completed response. |
| 133 | Implement SSE connection management (concurrent stream limits per tenant, keepalive) | Medium | Streaming connections are long-lived. Need per-tenant limits aligned with concurrency settings (Starter 3, Professional 10, Enterprise 30). |

---

## 5. Pipeline Optimization (WI #134-139)

Optimization opportunities identified during P50 reduction analysis. All are zero-cost or cost-reducing.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 134 | Implement IC + KR parallelization (Intent Classification and Knowledge Retrieval run concurrently) | Medium | Currently sequential. Both can start on customer message receipt. Saves ~800ms (IC 800ms budget runs in parallel with KR 1,000ms instead of sequential). Zero cost. Requires NATS topic publish parallelization. |
| 135 | Implement prompt optimization and prefix caching for Response Generator | Medium | Response Generator (3,000ms budget, 94.5% of AI cost) has the most optimization headroom. Azure OpenAI supports prompt caching for repeated prefixes (system prompt + tenant config). Could reduce RG latency 15-25% and token cost 20-35%. |
| 136 | Implement model routing — GPT-4o-mini for simple queries (FAQ, order status) | Low | Intent Classifier identifies query complexity. Simple queries (FAQ lookup, order status) don't need GPT-4o quality. GPT-4o-mini is 85%+ cheaper and 40-60% faster. Requires quality validation per intent type. |
| 137 | Implement semantic response caching (cache responses for semantically similar queries) | Low | Post-launch optimization. At 70% cache hit rate, reduces latency 60-70% and AI cost proportionally. Requires embedding-based similarity matching and TTL/invalidation strategy. Only viable after sufficient conversation volume for cache warm-up. |
| 138 | Implement pre-computation / warm-up for customer context (Layer 1 profile pre-loaded on session start) | Low | CustomerProfileService.get_profile() is called on each conversation start. For repeat customers, profile can be pre-cached when customer connects (before first message). Saves ~50-100ms per conversation. |
| 139 | Investigate Azure OpenAI Provisioned Throughput Units (PTU) for cost/latency at scale | Low | Defer to 50+ tenants. PTU minimum ~$3,300/month. Not cost-effective at launch. Document threshold for re-evaluation. |

---

## 6. API Completeness (WI #140-147)

API gaps identified in the UI-type × task-type matrix analysis.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 140 | Implement GDPR compliance REST endpoints (data export request, data deletion request, consent management) | High | DataExportService, DataDeletionService, and ConsentManager exist as services but have no API endpoints. Merchants/customers cannot exercise GDPR rights via API. Required for Shopify App Store review (3 mandatory webhooks: customers/data_request, customers/redact, shop/redact — WI #35). |
| 141 | Implement audit log query API (GET /api/audit with filtering by event type, tenant, date range) | Medium | AuditLogRepository exists with 12 event types. No query API for compliance reporting. WI #43 in Master Plan — status: Pending. |
| 142 | Implement customer profile REST endpoints (CRUD for Layer 1 profiles, Shopify sync trigger) | Medium | CustomerProfileService has full CRUD but no API endpoints. Merchants cannot view, edit, or trigger sync of customer profiles via API. |
| 143 | Implement knowledge base management REST endpoints (upload, query, delete knowledge documents) | Medium | KnowledgeBaseDocument model exists in cosmos_schema.py. No API for merchants to manage their knowledge base content. |
| 144 | Implement alert delivery mechanism (webhook to merchant URL, email notification, or both) | Medium | ConversationMeter generates billing alerts but they're stored in-memory only. No delivery to merchants. Need at least one notification channel. |
| 145 | Add rate limit headers to all API responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset) | Medium | RateLimitMiddleware enforces limits but does not communicate remaining quota to callers. Clients cannot proactively manage their request rate. |
| 146 | Add request-id / correlation-id to all API response headers | Medium | CorrelationMiddleware sets correlation context internally but does not expose it in response headers. Callers cannot trace their requests through the system. |
| 147 | Implement OpenAPI schema completeness (all response models, error schemas, authentication schemes documented) | Low | FastAPI auto-generates /openapi.json but quality depends on complete Pydantic models and response_model declarations on all endpoints. Not currently validated. |

---

## 7. Operational Readiness (WI #148-156)

Infrastructure and operational gaps that affect production readiness.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 148 | Create deployment runbook (step-by-step production deployment procedure, rollback steps) | High | No deployment documentation exists. Zero-downtime rolling deployment is configured in Terraform (WI #59) but no runbook for operators. |
| 149 | Create DR runbook — Option A (manual region redeploy procedure) | Medium | WI #61 in Master Plan — status: Pending. Single-region deployment needs documented recovery procedure. |
| 150 | Create maintenance runbook (operation types, notification procedure, rollback criteria) | Medium | WI #60 in Master Plan — status: Pending. Maintenance window defined (Tuesdays 02:00-04:00 UTC) but no procedure documented. |
| 151 | Implement SLA monitoring dashboard (P50/P95/P99 latency, uptime, per-tenant metrics) | Medium | WI #79 in Master Plan — status: Pending. SLA commitments exist (99.5-99.95% uptime, P50 < 1,500ms) but no monitoring dashboard to track compliance. |
| 152 | Implement KEDA scaling profiles for all 9 containers | High | WI #47-48 in Master Plan — status: Pending. Container scaling triggers defined in Decision #16 but not implemented in Terraform. |
| 153 | Implement archival pipeline (Change Feed → Parquet → Blob) | Medium | WI #53 in Master Plan — status: Pending. Blob storage lifecycle rules configured (WI #54) but the pipeline that moves data from Cosmos DB to Blob is not built. |
| 154 | Implement data retention policy enforcement (automated cleanup jobs) | Medium | WI #37 in Master Plan — status: Pending. Tier-based history depth defined (90d/365d/unlimited) but no automated enforcement. |
| 155 | Implement parameterized cost model calculator | Low | WI #82 in Master Plan — status: Pending. Cost basis validated at ~$0.0073/conversation but no calculator for projecting costs at different tenant/volume scenarios. |
| 156 | Document Option C upgrade path (geo-replication trigger: 50+ tenants) | Low | WI #62 in Master Plan — status: Pending. Upgrade criteria defined but path not documented. |

---

## 8. Security Hardening (WI #157-163)

Security gaps identified in the adversarial testing analysis.

| # | Work Item | Priority | Rationale |
|---|-----------|----------|-----------|
| 157 | Implement request body size limits (reject payloads > 1MB) | High | No explicit body size limit configured. Oversized payloads could cause memory pressure or slow processing. FastAPI/Starlette default is unlimited. |
| 158 | Implement JSON depth limit (reject deeply nested payloads, >50 levels) | Medium | Recursive JSON parsing can cause stack overflow or excessive memory use. No depth limit configured. |
| 159 | Implement API key rotation endpoint and mechanism (generate new key, grace period for old key) | Medium | API keys can be created (via TenantSecretService) but no rotation mechanism exists. Compromised keys cannot be replaced without service interruption. |
| 160 | Implement input sanitization for tenant_id and other path parameters (reject non-alphanumeric, path traversal, null bytes) | Medium | TenantScopedRepository enforces tenant_id on queries but does not validate tenant_id format. Malformed IDs could cause unexpected behavior. |
| 161 | Implement output sanitization for AI responses (strip markdown injection, HTML, executable content) | Medium | Critic validates safety but does not sanitize output format. Responses containing markdown/HTML could be rendered as executable in merchant UIs. |
| 162 | Implement Stripe webhook IP allowlisting (optional, restrict to Stripe's published IP ranges) | Low | Stripe webhook signature verification exists but IP filtering adds defense-in-depth. Stripe publishes their webhook IP ranges. |
| 163 | Implement rate limiting on authentication endpoints (prevent brute-force API key guessing) | Medium | Per-tenant rate limiting exists but applies after authentication. Failed auth attempts before tenant resolution are not rate-limited. |

---

## 9. Summary

### Work Item Counts

| Category | Count | IDs |
|----------|-------|-----|
| Test Infrastructure | 7 | #101-107 |
| Merchant Web UI | 11 | #108-118 |
| Trial / Demo Environment | 10 | #119-128 |
| Response Streaming (SSE) | 5 | #129-133 |
| Pipeline Optimization | 6 | #134-139 |
| API Completeness | 8 | #140-147 |
| Operational Readiness | 9 | #148-156 |
| Security Hardening | 7 | #157-163 |
| **Total New Work Items** | **63** | **#101-163** |

### Relationship to Existing Master Plan

These 63 new work items complement the existing 100 work items in `docs/Master-Plan-Review-01-30-2026.md`. Some overlap with existing pending items:

| New WI | Overlaps With | Notes |
|--------|---------------|-------|
| #140 (GDPR API) | #35 (GDPR webhooks) | #140 is broader (full GDPR API); #35 is the Shopify-specific subset |
| #141 (Audit log API) | #43 (Audit log query API) | Identical scope — #141 supersedes |
| #149 (DR runbook) | #61 (DR runbook Option A) | Identical scope — #149 supersedes |
| #150 (Maintenance runbook) | #60 (Maintenance runbook) | Identical scope — #150 supersedes |
| #151 (SLA dashboard) | #79 (SLA monitoring dashboard) | Identical scope — #151 supersedes |
| #152 (KEDA scaling) | #47-48 (KEDA profiles + Terraform) | Identical scope — #152 supersedes |
| #153 (Archival pipeline) | #53 (Archival pipeline) | Identical scope — #153 supersedes |
| #154 (Data retention) | #37 (Data retention enforcement) | Identical scope — #154 supersedes |
| #155 (Cost calculator) | #82 (Cost model calculator) | Identical scope — #155 supersedes |
| #156 (Option C docs) | #62 (Option C upgrade path) | Identical scope — #156 supersedes |

**Net new items (no overlap): 53**
**Superseding items (overlap with Master Plan): 10**

### Priority Distribution (Suggested — Pending Review)

| Priority | Count | Work Items |
|----------|-------|------------|
| High | 18 | #101-104, #108-110, #119-121, #124, #129-130, #140, #148, #152, #157 |
| Medium | 29 | #105-107, #111-114, #117, #122-123, #125-126, #131-133, #134-135, #141-146, #149-151, #153-154, #158-161, #163 |
| Low | 16 | #115-116, #118, #127-128, #136-139, #147, #155-156, #162 |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
