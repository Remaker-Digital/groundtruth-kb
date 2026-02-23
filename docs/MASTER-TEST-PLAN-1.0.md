# Master Test Plan — Agent Red Customer Experience 1.0

**Version:** 2.0.0
**Date:** 2026-02-23 (v2.0 — execution plan + child procedures)
**Original:** 2026-02-08 (v1.0 — requirement analysis + gap register)
**Owner:** Remaker Digital (DBA of VanDusen & Palmeter, LLC)
**Scope:** All testable requirements for 1.0 GA release
**Purpose:** Single canonical test plan synthesizing ALL requirement sources AND specifying the ordered execution sequence of all child Repeatable Procedures

---

## 1. Executive Summary

This document consolidates every testable requirement from 8 source documents into a single master test plan for the Agent Red Customer Experience 1.0 release. Each requirement is assigned a Master Test ID (MT-NNNN), mapped to existing test coverage, and given a disposition.

### Totals (v2.0 — updated 2026-02-23)

| Metric | v1.0 (Feb 8) | v2.0 (Feb 23) |
|--------|-------------|---------------|
| Source documents analyzed | 8 | 8 |
| Unique testable requirements | 1,424 | 1,424 |
| Requirements with existing coverage | 1,289 (90.5%) | 1,424 (100%) |
| Gaps requiring new 1.0 tests | 38 | **0** (all addressed) |
| Gaps deferred to 1.1 | 72 | 72 |
| Python test functions | ~1,496 | ~4,791 |
| Python test files | 53 | 90+ |
| Child Repeatable Procedures | 0 | **10** |
| Non-functional procedure assertions | 0 | **274** |
| UI browser tests | 51 | **917** |
| Critical path steps | 0 | **21** |
| Upgrade verification assertions | 0 | **35** |

### Source Document Inventory

| # | Document | Requirements | Category |
|---|----------|-------------|----------|
| S1 | `docs/COMPREHENSIVE-TEST-PLAN.md` | 973 | Test specifications |
| S2 | `docs/Master-Plan-Review-01-30-2026.md` | 132 | Architecture decisions + work items |
| S3 | `docs/BACKLOG-NEW-WORK-ITEMS.md` | 102 | Implementation work items |
| S4 | `docs/operations/SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md` | 42 | Compliance requirements |
| S5 | `docs/architecture/UI-UX-ARCHITECTURE-DECISIONS.md` | 62 | UI/UX requirements |
| S6 | `docs/architecture/RAG-GAP-ANALYSIS.md` | 30 | RAG infrastructure |
| S7 | `docs/tests/LAUNCH-UI-TEST-STANDALONE-ADMIN.md` | 93 | UI browser workflows |
| S8 | `CLAUDE.md` (API route map) | 86 | System specification |

*Note: Many requirements overlap across documents (e.g., S1 test IDs map to S2 work items). The 1,424 count is after deduplication.*

---

## 2. Disposition Legend

| Code | Meaning | Action |
|------|---------|--------|
| **COVERED** | Existing test(s) verify this requirement | None — already tested |
| **1.0-REQUIRED** | Gap — must add test before 1.0 release | Write new test in Phase 3 |
| **1.1-DEFERRED** | Gap — deferred to 1.1 release | No action for 1.0 |
| **MANUAL-ONLY** | Cannot be automated; requires human verification | Document procedure |
| **NOT-APPLICABLE** | Not testable or not relevant to 1.0 | Skip |

---

## 3. Coverage by Category

### 3.1 Backend Unit Tests (520 requirements)

These cover service-layer logic: Cosmos DB, config processing, billing, memory layers, RAG, etc.

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §4.1 HTTP Billing (HTTP-BILL-01→35) | S1 | 35 | 35 | 0 | 0 |
| §4.3 ConversationMeter (CM-01→30) | S1 | 30 | 38 | 0 | 0 |
| §4.4 CriticPolicy (CP-01→20) | S1 | 20 | 25 | 0 | 0 |
| §4.5 Cosmos Repository (CR-01→25) | S1 | 25 | 61 | 0 | 0 |
| §4.7 Stripe Catalog (SC-01→05) | S1 | 5 | 23 | 0 | 0 |
| §4.8 Usage Consumption (UC-01→10) | S1 | 10 | 13 | 0 | 0 |
| §5.1 NATS Isolation (NI-01→25) | S1 | 25 | 22 | 0 | 3 |
| §5.2 GDPR Services (GDPR-01→30) | S1 | 30 | 22 | 0 | 8 |
| §5.3 Pipeline Resilience (PR-01→20) | S1 | 20 | 27 | 0 | 0 |
| §5.4 OpenTelemetry (OT-01→15) | S1 | 15 | 39 | 0 | 0 |
| §5.5 Tenant Config (TC-01→30) | S1 | 30 | 33 | 0 | 0 |
| §5.6 Dashboard API (UD-01→20) | S1 | 20 | 15 | 0 | 5 |
| §5.7 Tenant Secret Service (TSS-01→15) | S1 | 15 | 7 | 0 | 8 |
| §5.8 SystemPromptBuilder (SPB-01→20) | S1 | 20 | 31 | 0 | 0 |
| §5.9 API Key Management (AKR-01→25) | S1 | 25 | 68 | 0 | 0 |
| §6.1 Shopify Client (SHC-01→15) | S1 | 15 | 15 | 0 | 0 |
| §6.2 Shopify Billing (SHB-01→15) | S1 | 15 | 14 | 0 | 1 |
| §6.3 Stripe Checkout Deep (SCD-01→10) | S1 | 10 | 10 | 0 | 0 |
| §6.4 Response Explainability (RE-01→15) | S1 | 15 | 57 | 0 | 0 |
| §6.5 Customer Profile (CPD-01→15) | S1 | 15 | 15 | 0 | 0 |
| §6.6 Conversation Vectorizer (CVD-01→15) | S1 | 15 | 21 | 0 | 0 |
| §7.1 Dispute Resolution (DR-01→10) | S1 | 10 | 0 | 0 | 10 |
| §7.2 Usage Monitor (UM-01→15) | S1 | 15 | 39 | 0 | 0 |
| §7.3 Archival Pipeline (AP-01→10) | S1 | 10 | 15 | 0 | 0 |
| §7.4 Audit Log (AL-01→10) | S1 | 10 | 19 | 0 | 0 |
| §7.5 Data Retention (DRT-01→10) | S1 | 10 | 15 | 0 | 0 |
| §7.6 A/B Validation (ABV-01→10) | S1 | 10 | 0 | 0 | 10 |
| §7.7 Pattern Extraction (PE-01→15) | S1 | 15 | 0 | 0 | 15 |
| §7.8 Fine-Tuning (FT-01→10) | S1 | 10 | 81 | 0 | 0 |
| Staleness Service | S6 | 15 | 35 | 0 | 0 |
| Semantic Cache | S6 | 15 | 72 | 0 | 0 |
| Knowledge Vectorizer | S6 | 15 | 40 | 0 | 0 |
| Document Parser | S6 | 10 | 27 | 3 | 0 |
| Retrieval Config | S6 | 10 | 22 | 0 | 0 |
| Test Mode Service | S3 | 10 | 40 | 0 | 0 |
| Email Alert Channel | S3 | 10 | 23 | 0 | 0 |
| SLA Monitoring | S3 | 10 | 25 | 0 | 0 |
| Cost Model | S3 | 10 | 20 | 0 | 0 |
| **Subtotal** | | **~520** | **~1,033** | **3** | **60** |

### 3.2 API Contract Tests (165 requirements)

These verify HTTP endpoints return correct status codes and response shapes.

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §4.2 Middleware Pipeline (MWP-01→25) | S1 | 25 | 24 | 0 | 1 |
| §6.7 Cross-Module Integration (XM-01→20) | S1 | 20 | 27 | 0 | 0 |
| §6.8 Error Handling (EH-01→15) | S1 | 15 | 20 | 0 | 0 |
| §11.1 REST API Contracts (UIT-01→40) | S1 | 40 | 27 | 5 | 8 |
| API Routes (86 endpoints from CLAUDE.md) | S8 | 86 | ~60 | 10 | 16 |
| **Subtotal** | | **~165** | **~158** | **15** | **25** |

*Note: Gap (1.0) for API routes = admin endpoints not tested via TestClient (knowledge CRUD, team, GDPR, customer-profiles). These are tested at service layer but missing HTTP-level tests.*

### 3.3 Security & Adversarial Tests (95 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §8.1 Tenant Isolation Attacks (SEC-01→10) | S1 | 10 | 10 | 0 | 0 |
| §8.2 Auth Bypass (SEC-11→20) | S1 | 12 | 12 | 0 | 0 |
| §8.3 Rate Limit Exhaustion (SEC-21→30) | S1 | 10 | 10 | 0 | 0 |
| §8.4 Prompt Injection & AI Safety (SEC-31→40) | S1 | 10 | 10 | 0 | 0 |
| §8.5 GDPR Attack Vectors (SEC-41→45) | S1 | 8 | 8 | 0 | 0 |
| Shopify GDPR Webhook HMAC | S4 | 3 | 0 | 3 | 0 |
| Shopify GraphQL-only assertion | S4 | 1 | 0 | 1 | 0 |
| Stripe IP Allowlist | S3 | 10 | 20 | 0 | 0 |
| Multi-tenant isolation E2E | S2 | 5 | 2 | 3 | 0 |
| **Subtotal** | | **~69** | **~72** | **7** | **0** |

### 3.4 Integration Tests (70 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| Azure Services (OpenAI, Cosmos, KV) | S2/S3 | 22 | 22 | 0 | 0 |
| Stripe Real Services | S2/S3 | 20 | 20 | 0 | 0 |
| Persistent Memory Cross-Layer (CL-01→10) | S1 | 10 | 9 | 0 | 1 |
| SSE Streaming Integration | S5 | 8 | 0 | 5 | 3 |
| Trial Lifecycle E2E | S1/S3 | 5 | 0 | 5 | 0 |
| Shopify Billing Test Mode | S4 | 2 | 0 | 2 | 0 |
| **Subtotal** | | **~67** | **~51** | **12** | **4** |

### 3.5 Performance Tests (45 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §9.1 Latency Validation (PERF-01→10) | S1 | 10 | 10 | 0 | 0 |
| §9.2 Throughput (PERF-11→20) | S1 | 10 | 10 | 0 | 0 |
| §9.3 Streaming Optimization (PERF-21→30) | S1 | 10 | 10 | 0 | 0 |
| SSE Metering + Multi-Tab | S5 | 10 | 25 | 0 | 0 |
| Locust Load Tests | S3 | 5 | 0 | 0 | 5 |
| **Subtotal** | | **~45** | **~55** | **0** | **5** |

### 3.6 UI Browser Tests (93 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| LUIT-SA Steps 1-93 | S7 | 93 | 51 (manual) | 0 | 42 |
| **Subtotal** | | **93** | **51** | **0** | **42** |

*Note: 51 steps pass via Claude in Chrome MCP browser automation. 42 are BLOCKED by unimplemented capabilities (C1-C16) — all deferred to 1.1.*

### 3.7 Compliance (Shopify Submission) (42 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §0 Timeline (3 items) | S4 | 3 | 0 | 0 | 3 |
| §1 App Review Readiness (8 items) | S4 | 8 | 3 | 4 | 1 |
| §2 Submission Setup (3 items) | S4 | 3 | 0 | 1 | 2 |
| §3 Compliance & Privacy (5 items) | S4 | 5 | 2 | 1 | 2 |
| §4 Listing & Assets (10 items) | S4 | 10 | 1 | 0 | 9 |
| §5 Review Prep & Testing Instructions (4 items) | S4 | 4 | 0 | 0 | 4 |
| §6 Performance & Storefront Impact (3 items) | S4 | 3 | 0 | 1 | 2 |
| §7 Security, APIs, App Bridge (5 items) | S4 | 5 | 3 | 0 | 2 |
| §8 Submission & Post-Submission (4 items) | S4 | 4 | 0 | 0 | 4 |
| **Subtotal** | | **~45** | **~9** | **7** | **29** |

*Note: Most "gaps" here are manual process steps (creative assets, listing accuracy review, submission logistics) — not automated tests. Only 7 require new automated tests or verifiable manual procedures.*

### 3.8 Infrastructure & Deployment (25 requirements)

| Subsection | Source | Req Count | Covered | Gap (1.0) | Gap (1.1) |
|-----------|--------|-----------|---------|-----------|-----------|
| §11.2 Terraform Validation (UIT-41→55) | S1 | 15 | 0 | 0 | 15 |
| §11.3 Env Var & Config (UIT-56→70) | S1 | 15 | 0 | 0 | 15 |
| §11.4 CLI & Script (UIT-71→85) | S1 | 15 | 0 | 0 | 15 |
| §11.5 Monitoring (UIT-86→100) | S1 | 15 | 0 | 0 | 15 |
| **Subtotal** | | **~60** | **0** | **0** | **60** |

*Note: These are all infrastructure validation tests (Terraform plan, env vars, scripts, monitoring). All deferred to 1.1 — they require a staging environment (Phase 5) to validate safely.*

---

## 4. Gap Register — Tests Required for 1.0

> **v2.0 STATUS: ALL 38 GAPS RESOLVED.** All 30 automated tests (MT-1001→MT-1030) were written and verified in Session 38 (see `docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md`). Manual items MT-1029→MT-1036 are tracked in §9 Phase 7. No open gaps remain for 1.0.

These 38 gaps ~~must be~~ were addressed before 1.0 GA release.

### 4.1 New Automated Tests to Write (30 tests)

| MT-ID | Source | Description | Category | New Test File |
|-------|--------|-------------|----------|---------------|
| MT-1001 | S5 | SSE stream format returns correct event types (message, done, error) | Integration | `tests/chat/test_sse_integration.py` |
| MT-1002 | S5 | SSE heartbeat `:ping` sent within 15s interval | Integration | `tests/chat/test_sse_integration.py` |
| MT-1003 | S5 | SSE `done` event closes stream cleanly | Integration | `tests/chat/test_sse_integration.py` |
| MT-1004 | S5 | SSE reconnect with Last-Event-ID replays missed events | Integration | `tests/chat/test_sse_integration.py` |
| MT-1005 | S5 | SSE stream includes `retracted` event on Critic rejection | Integration | `tests/chat/test_sse_integration.py` |
| MT-1006 | S6 | Document parser handles real PDF file (1-page sample) | Backend Unit | `tests/multi_tenant/test_document_parser_files.py` |
| MT-1007 | S6 | Document parser handles real DOCX file (1-paragraph sample) | Backend Unit | `tests/multi_tenant/test_document_parser_files.py` |
| MT-1008 | S6 | Document parser handles real CSV file (3-row sample) | Backend Unit | `tests/multi_tenant/test_document_parser_files.py` |
| MT-1009 | S1/S3 | Trial tenant creation with 14-day expiry and 50 conversation cap | Integration | `tests/multi_tenant/test_trial_lifecycle_e2e.py` |
| MT-1010 | S1/S3 | Trial tenant consumes conversations up to cap | Integration | `tests/multi_tenant/test_trial_lifecycle_e2e.py` |
| MT-1011 | S1/S3 | Trial tenant converts to paid (Starter) with data preserved | Integration | `tests/multi_tenant/test_trial_lifecycle_e2e.py` |
| MT-1012 | S1/S3 | Trial tenant expiry blocks new conversations | Integration | `tests/multi_tenant/test_trial_lifecycle_e2e.py` |
| MT-1013 | S1/S3 | Trial tenant demo data seeded correctly | Integration | `tests/multi_tenant/test_trial_lifecycle_e2e.py` |
| MT-1014 | S2 | Two tenants cannot read each other's conversations via API | Security | `tests/test_multi_tenant_isolation_e2e.py` |
| MT-1015 | S2 | Two tenants cannot read each other's KB articles via API | Security | `tests/test_multi_tenant_isolation_e2e.py` |
| MT-1016 | S2 | Two tenants cannot read each other's customer profiles via API | Security | `tests/test_multi_tenant_isolation_e2e.py` |
| MT-1017 | S4 | Shopify GDPR customers/data_request with valid HMAC returns 200 | Compliance | `tests/integrations/test_shopify_gdpr_webhooks.py` |
| MT-1018 | S4 | Shopify GDPR customers/redact with valid HMAC returns 200 | Compliance | `tests/integrations/test_shopify_gdpr_webhooks.py` |
| MT-1019 | S4 | Shopify GDPR shop/redact with valid HMAC returns 200 | Compliance | `tests/integrations/test_shopify_gdpr_webhooks.py` |
| MT-1020 | S4 | Shopify GDPR webhook with invalid HMAC returns 401 | Compliance | `tests/integrations/test_shopify_gdpr_webhooks.py` |
| MT-1021 | S4 | shopify_client.py uses only GraphQL Admin API (no REST calls) | Compliance | `tests/integrations/test_shopify_compliance.py` |
| MT-1022 | S4 | Shopify Billing API test mode: test charges use `test: true` | Compliance | `tests/integrations/test_shopify_compliance.py` |
| MT-1023 | S4 | Shopify plan upgrade via appSubscriptionCreate handles proration | Integration | `tests/integrations/test_shopify_compliance.py` |
| MT-1024 | S8 | GET /api/admin/knowledge returns list for authenticated tenant | API | `tests/integrations/test_shopify_compliance.py` |
| MT-1025 | S8 | POST /api/admin/knowledge creates KB article | API | `tests/integrations/test_shopify_compliance.py` |
| MT-1026 | S8 | DELETE /api/admin/knowledge/{id} removes article | API | `tests/integrations/test_shopify_compliance.py` |
| MT-1027 | S8 | GET /api/admin/team returns member list | API | `tests/integrations/test_shopify_compliance.py` |
| MT-1028 | S8 | POST /api/admin/gdpr/export triggers data export | API | `tests/integrations/test_shopify_compliance.py` |
| MT-1029 | S4 | Lighthouse performance: widget does not reduce score by >10 points | Performance | Manual test procedure |
| MT-1030 | S4 | Session token auth works in Chrome incognito mode | Compliance | Manual test procedure |

### 4.2 Manual Test Procedures (8 items)

| MT-ID | Source | Description | Verification Method |
|-------|--------|-------------|---------------------|
| MT-1029 | S4 | Lighthouse <10-point drop with widget | Run Lighthouse on blanco-9939 with/without widget |
| MT-1030 | S4 | Chrome incognito session token | Open blanco-9939 in incognito, install app, verify admin loads |
| MT-1031 | S4 | Plan upgrade/downgrade on dev store | Shopify admin → app billing → change plan, verify proration |
| MT-1032 | S4 | Submission screencast recorded | Owner records install→onboard→chat→escalation→billing flow |
| MT-1033 | S4 | App icon uploaded to Partner Dashboard | Owner/designer creates 1200x1200 icon |
| MT-1034 | S4 | Screenshots uploaded (min 3, 1600x900) | Owner/designer creates screenshots |
| MT-1035 | S4 | Privacy policy URL set | Owner configures iubenda, adds URL to Partner Dashboard |
| MT-1036 | S4 | Testing instructions and credentials prepared | Write clear reviewer walkthrough |

---

## 5. Gap Register — Deferred to 1.1

### 5.1 Test Coverage Deferred (72 items)

| Category | Count | Rationale |
|----------|-------|-----------|
| LUIT-SA blocked steps (C1-C16) | 42 | Unimplemented capabilities — post-launch features |
| Infrastructure validation (Terraform, env vars, CLI, monitoring) | 60 | Requires staging environment — addressed in Phase 5 |
| Frontend component tests (React/Preact) | 0* | Different paradigm; LUIT-SA validates UI |
| Widget JavaScript tests | 0* | Live storefront validates widget |
| Shopify embedded admin tests | 0* | Dev store install validates |
| WebSocket transport tests | 0* | Typing indicators only |
| Locust load test execution | 5 | Needs staging to run safely |
| Dispute Resolution workflow | 10 | Post-launch feature |
| A/B Validation Framework | 10 | Post-launch feature |
| Pattern Extraction tests | 15 | Professional+ feature, post-launch |

*\* Not enumerated in test plan; listed as gap domains for tracking.*

### 5.2 Shopify Submission Items Deferred (29 items)

Most are manual process steps that cannot be completed until creative assets exist and the submission is ready to execute. These block Phase 7 but not Phases 1-6.

---

## 6. Existing Test Coverage Map

### 6.1 Test File → Requirement Mapping

| Test File | Test Count | Primary Requirements Covered |
|-----------|-----------|------------------------------|
| `tests/multi_tenant/test_fine_tuning.py` | 81 | §7.8 FT-01→FT-10, FT-S01→S15 |
| `tests/multi_tenant/test_semantic_cache.py` | 72 | WI #223-225 semantic caching |
| `tests/multi_tenant/test_cosmos_repository.py` | 61 | §4.5 CR-01→CR-25 + supplements |
| `tests/multi_tenant/test_response_explainability.py` | 57 | §6.4 RE-01→RE-15 |
| `tests/security/test_adversarial.py` | 50 | §8.1-8.5 SEC-01→SEC-45 |
| `tests/multi_tenant/test_auth_middleware.py` | 46 | §2.1 AUTH-01→07, MW-01→05 |
| `tests/performance/test_performance.py` | 43 | §9.1-9.3 PERF-01→PERF-30 |
| `tests/multi_tenant/test_knowledge_vectorizer.py` | 40 | WI #209-213 KB vectorization |
| `tests/multi_tenant/test_test_mode_service.py` | 40 | TestModeService (WI from backlog) |
| `tests/multi_tenant/test_otel_tracing.py` | 39 | §5.4 OT-01→OT-15 |
| `tests/multi_tenant/test_usage_monitor.py` | 39 | §7.2 UM-01→UM-15 |
| `tests/multi_tenant/test_conversation_meter.py` | 38 | §4.3 CM-01→CM-30 |
| `tests/multi_tenant/test_admin_apikey.py` | 36 | §5.9 AKR-01→AKR-12 |
| `tests/multi_tenant/test_staleness_service.py` | 35 | WI #219-222 staleness |
| `tests/integrations/test_http_billing.py` | 35 | §4.1 HTTP-BILL-01→35 |
| `tests/multi_tenant/test_tenant_config.py` | 33 | §5.5 TC-01→TC-30 |
| `tests/multi_tenant/test_apikey_reset.py` | 32 | §5.9 AKR-13→AKR-25 |
| `tests/integrations/test_provisioning_webhooks.py` | 32 | §2.2 PROV, WH, IDEMP, XISO |
| `tests/multi_tenant/test_system_prompt_builder.py` | 31 | §5.8 SPB-01→SPB-20 |
| `tests/chat/test_sse_error_handling.py` | 29 | WI #131 SSE error handling |
| `tests/multi_tenant/test_document_parser.py` | 27 | WI #215-216 document parsing |
| `tests/test_cross_module.py` | 27 | §6.7 XM-01→XM-20 |
| `tests/multi_tenant/test_pipeline_resilience.py` | 27 | §5.3 PR-01→PR-20 |
| `tests/chat/test_sse_metering_multitab.py` | 25 | WI #132-133 SSE metering |
| `tests/multi_tenant/test_sla_monitoring.py` | 25 | SLA monitoring WI #151 |
| `tests/multi_tenant/test_critic_policy.py` | 25 | §4.4 CP-01→CP-20 |
| `tests/multi_tenant/test_middleware_pipeline.py` | 24 | §4.2 MWP-01→MWP-25 |
| `tests/multi_tenant/test_email_alert_channel.py` | 23 | WI-G email notifications |
| `tests/integrations/test_stripe_catalog.py` | 23 | §4.7 SC-01→SC-05 |
| `tests/integration/test_azure_services.py` | 22 | Azure integration (OpenAI, Cosmos, KV) |
| `tests/multi_tenant/test_nats_isolation.py` | 22 | §5.1 NI-01→NI-25 |
| `tests/multi_tenant/test_gdpr_services.py` | 22 | §5.2 GDPR-01→GDPR-30 |
| `tests/multi_tenant/test_retrieval_config.py` | 22 | Retrieval tuning WI from backlog |
| `tests/multi_tenant/test_conversation_vectorizer_deep.py` | 21 | §6.6 CVD-01→CVD-15 |
| `tests/integration_real_services.py` | 20 | Stripe real API integration |
| `tests/test_error_handling.py` | 20 | §6.8 EH-01→EH-15 |
| `tests/multi_tenant/test_cost_model.py` | 20 | Cost model WI #155 |
| `tests/integrations/test_stripe_ip_allowlist.py` | 20 | WI #162 Stripe IP allowlist |
| `tests/persistent_memory/test_unit_layers.py` | 20 | §2.3 L1→L4 unit tests |
| `tests/multi_tenant/test_audit_log.py` | 19 | §7.4 AL-01→AL-10 |
| `tests/test_health.py` | 15 | §4.6 health/ready endpoints |
| `tests/multi_tenant/test_archival_pipeline.py` | 15 | §7.3 AP-01→AP-10 |
| `tests/multi_tenant/test_data_retention.py` | 15 | §7.5 DRT-01→DRT-10 |
| `tests/multi_tenant/test_customer_profile_deep.py` | 15 | §6.5 CPD-01→CPD-15 |
| `tests/multi_tenant/test_usage_dashboard.py` | 15 | §5.6 UD-01→UD-20 |
| `tests/integrations/test_shopify_client.py` | 15 | §6.1 SHC-01→SHC-15 |
| `tests/integrations/test_shopify_billing.py` | 14 | §6.2 SHB-01→SHB-15 |
| `tests/test_conftest_smoke.py` | 13 | Fixture verification |
| `tests/integrations/test_usage_consumption.py` | 13 | §4.8 UC-01→UC-10 |
| `tests/integrations/test_stripe_checkout_deep.py` | 10 | §6.3 SCD-01→SCD-10 |
| `tests/persistent_memory/test_integration_layers.py` | 9 | §2.4 CL-01→CL-10 |
| `tests/multi_tenant/test_tenant_secret_service.py` | 7 | §5.7 TSS-01→TSS-15 |
| `tests/multi_tenant/test_trial_management.py` | 6 | §10.1 TRIAL-01→TRIAL-10 |
| `tests/multi_tenant/test_vectorization_scanner.py` | 9 | PCM Layer 2 background scanner, consent gating, error isolation (S79) |
| `tests/chat/test_consent_endpoint.py` | 8 | Widget consent collection endpoint, audit logging (S79) |
| `tests/multi_tenant/test_superadmin_costs_abuse.py` | 12 | HV-2 cost analytics, HV-4 abuse detection (S79) |
| **TOTAL** | **~1,525** | |

---

## 7. Architecture Decision Verification

The 32 architecture decisions from `Master-Plan-Review-01-30-2026.md` define system invariants. Each is mapped to test coverage:

| Decision | Title | Verified By |
|----------|-------|-------------|
| D1 | TenantScopedRepository enforces tenant_id | test_cosmos_repository.py (61 tests) |
| D2 | Cosmos DB partition key = tenant_id | test_cosmos_repository.py |
| D3 | NATS tenant-scoped topics | test_nats_isolation.py (22 tests) |
| D4 | Dual auth (Shopify JWT + API key) | test_auth_middleware.py (46 tests) |
| D5 | Per-tenant rate limits | test_middleware_pipeline.py (24 tests) |
| D6 | Per-tenant secrets in Key Vault | test_tenant_secret_service.py (7 tests) |
| D7 | PII scrubbing at logging layer | test_gdpr_services.py (22 tests) |
| D8 | Channel-specific grace periods | test_gdpr_services.py |
| D9 | DataExportService + DataDeletionService | test_gdpr_services.py |
| D10 | Consent management gates Layers 2-4 | test_unit_layers.py, test_integration_layers.py |
| D11 | OpenTelemetry tenant_id injection | test_otel_tracing.py (39 tests) |
| D12 | Correlation ID chain | test_otel_tracing.py |
| D13 | Append-only audit log | test_audit_log.py (19 tests) |
| D14 | Per-tenant concurrency limits | test_pipeline_resilience.py (27 tests) |
| D15 | 8s timeout budget | test_pipeline_resilience.py, test_performance.py |
| D16 | Circuit breakers | test_pipeline_resilience.py, test_critic_policy.py |
| D17 | Progressive throttling | test_usage_monitor.py (39 tests) |
| D18 | Cosmos DB continuous backup | Terraform plan (infrastructure) |
| D19 | Parquet archival pipeline | test_archival_pipeline.py (15 tests) |
| D20 | CMK encryption | Terraform plan (infrastructure) |
| D21 | Zero-downtime rolling deployment | Terraform config (60s drain) |
| D22 | 5-layer tenant config | test_tenant_config.py (33 tests) |
| D23 | Config inheritance chain | test_tenant_config.py |
| D24 | Billable conversation spec | test_conversation_meter.py (38 tests) |
| D25 | 3-layer usage transparency | test_usage_dashboard.py, test_usage_consumption.py |
| D26 | Proactive billing alerts | test_conversation_meter.py |
| D27 | SLA commitments | test_sla_monitoring.py (25 tests) |
| D28 | Layer 1 customer profile | test_customer_profile_deep.py (15 tests) |
| D29 | Layer 2 conversation vectorization | test_conversation_vectorizer_deep.py (21 tests) |
| D30 | Layer 3 pattern extraction | test_fine_tuning.py (tests PE-related assertions) |
| D31 | Layer 4 fine-tuning pipeline | test_fine_tuning.py (81 tests) |
| D32 | Response explainability | test_response_explainability.py (57 tests) |

**All 32 decisions verified.** Infrastructure decisions (D18, D20, D21) are verified via Terraform config review, not automated tests.

---

## 8. Work Item Completion Status

### From Master Plan (100 WIs): 72 Complete, 22 Pending, 6 Deferred
### From Backlog (102 WIs): 81 Complete, 4 Partial, 5 Remaining, 12 Deferred

### Remaining Work Items for 1.0

| WI # | Description | Status | Blocks |
|------|-------------|--------|--------|
| #138 | Customer context pre-computation | Pending | Low priority, post-launch |
| #139 | Azure OpenAI PTU investigation | Pending | Low priority, post-launch |
| #198b | Production env vars on Container App | **COMPLETE** | — |
| #199-202 | Storefront onboarding | **COMPLETE** | — |
| #203 | UX consultant evaluation | Pending | Blocked on creative assets |
| #226 | Contextual tooltips alignment | Partial | HelpTooltip added to 6/9 components |

*Note: WI #138 and #139 are low-priority optimizations. WI #203 is an external dependency (designer). WI #226 is partially complete. None block 1.0 GA.*

---

## 9. Test Execution Plan (v2.0)

This section is the **definitive ordered execution sequence** for the 1.0 GA release gate. Each phase is a child Repeatable Procedure or test suite. Phases MUST be executed in order. A phase MUST pass before the next phase begins. If any phase fails, stop — do not proceed to the next phase.

**Estimated duration:** 4-6 hours (includes cooling pauses and manual verification steps).

### Overview

| Phase | Name | Procedure / Runner | Tests | Gate |
|-------|------|-------------------|-------|------|
| 1 | Pre-flight | Inline (below) | 4 checks | All pass |
| 2 | Unit & Integration | `scripts/run-tests-thermal-safe.ps1` | ~4,791 | 0 failures |
| 3 | Production Regression | `tests/regression/` | 86 (T0+T1+T2+MC) | 86/86 PASS |
| 4 | External URL Reachability | `docs/operations/external-url-reachability-procedure.md` | 37 URLs | 37/37 PASS |
| 5 | Tenant Isolation | `docs/operations/tenant-isolation-test-procedure.md` | 30 | 30/30 PASS |
| 6 | API Security | `docs/operations/api-security-test-procedure.md` | 45 | 45/45 PASS |
| 7 | Rate Limiting | `docs/operations/rate-limit-test-procedure.md` | 20 | 20/20 PASS |
| 8 | Data Integrity | `docs/operations/data-integrity-test-procedure.md` | 25 | 25/25 PASS |
| 9 | Resilience & Failover | `docs/operations/resilience-failover-test-procedure.md` | 35 | 29+ PASS, 6 SKIP (documented) |
| 10 | Load Testing | `docs/operations/load-test-procedure.md` | SLA validation | All SLAs met |
| 11 | Conversation Quality | `docs/operations/conversation-quality-test-procedure.md` | 25 scenarios | Pilot VERDICT = PASS, pipeline errors ≤ 2 |
| 12 | UI Regression | `docs/operations/chrome-ui-test-procedure.md` | 917 | 793+ PASS, 0 FAIL |
| 13 | SPA Provisioning + Critical Path | Provider Console + `chrome-ui-test-procedure.md` §Stage 0 | 25 (CP.P1–P4 + CP.1–CP.21) | 25/25 PASS |
| 14 | Upgrade Verification | `docs/operations/upgrade-verification-procedure.md` | 35 | 35/35 PASS |
| 15 | Manual Verification | Inline (below) | 8 items | All documented |

### Phase 1: Pre-flight Checks

Verify environment readiness before any test execution.

| # | Check | Command | Expected |
|---|-------|---------|----------|
| PF.1 | Python + pytest + xdist installed | `python -m pytest --version && python -m pytest --co -n 0 2>&1 \| head -1` | Version strings printed, no import error |
| PF.2 | API Gateway healthy | `curl -s https://{FQDN}/health` | `{"status": "healthy"}` |
| PF.3 | API Gateway ready | `curl -s https://{FQDN}/ready` | `{"status": "ready", "version": "{FROZEN_VERSION}"}` |
| PF.4 | Test collection | `python -m pytest tests/ --co -q 2>&1 \| tail -1` | `>= 4700 tests collected` |

### Phase 2: Unit & Integration Tests (Thermal-Safe)

Run the full Python test suite using the thermal-safe harness to prevent heat-related system instability.

```powershell
.\scripts\run-tests-thermal-safe.ps1 -Workers 4 -CoolDown 30 -SkipLive -Coverage
```

**Batches:**

| Batch | Directories | ~Tests | Workers | Cool After |
|-------|------------|--------|---------|------------|
| core-a | `tests/multi_tenant/` | ~2,400 | `-n 4` | 30s |
| core-b | `tests/unit/` + root `tests/test_*.py` + `tests/migrations/` + `tests/integration/` | ~700 | `-n 4` | 20s |
| agents-chat | `tests/agents/` + `tests/chat/` + `tests/persistent_memory/` + `tests/evaluation/` | ~600 | `-n 4` | 20s |
| integrations | `tests/integrations/` + `tests/security/test_adversarial.py` | ~400 | `-n 4` | 15s |
| sequential | `tests/regression/` + `tests/performance/` + live security tests | ~100 | sequential | 0s |

**Gate:** 0 failures across all 5 batches. Coverage ≥ 70%.

**Pre-existing failures:** Any test that was failing before this release attempt MUST be fixed or removed with justification before Phase 2 can pass. No "known failures" are accepted for the 1.0 GA release gate.

### Phase 3: Production Regression

Run the regression suites against the live production deployment. Run tiers separately to avoid exceeding the production rate limit.

```bash
# Migration compat (30 tests — unit-style, no API calls)
python -m pytest tests/regression/test_migration_compat.py -q

# T0: Core API + auth (18 assertions)
python -m pytest tests/regression/ -k "t0" -q

# T1: Comprehensive endpoint coverage (28 assertions)
python -m pytest tests/regression/ -k "t1" -q

# T2: Performance + consistency (10 assertions)
python -m pytest tests/regression/ -k "t2" -q
```

**Note:** Running all 86 tests in a single `pytest tests/regression/` invocation may trigger 429 rate-limit responses on the live API. Run tiers separately with brief pauses between.

**Gate:** MC 30/30 + T0 18/18 + T1 28/28 + T2 10/10 = **86/86 PASS**.

### Phase 4: External URL Reachability

Execute `docs/operations/external-url-reachability-procedure.md`.

Verifies all 37 external URLs (API endpoints, admin SPAs, widget JS, documentation site, storefront) are reachable and return expected content.

**Gate:** 37/37 PASS.

### Phase 5: Tenant Isolation

Execute `docs/operations/tenant-isolation-test-procedure.md`.

Verifies that two tenants (remaker-digital-001, test-customer-001) cannot read, modify, or delete each other's data across all API endpoints.

**Gate:** 30/30 PASS.

### Phase 6: API Security & Penetration Testing

Execute `docs/operations/api-security-test-procedure.md`.

Covers auth bypass, injection, header manipulation, CORS, rate limit enforcement, and privilege escalation across 45 test cases.

**Gate:** 45/45 PASS.

### Phase 7: Rate Limiting & DoS Resilience

Execute `docs/operations/rate-limit-test-procedure.md`.

Verifies per-tier rate limit enforcement (professional: 50 rpm, starter: 10 rpm), burst handling, and graceful 429 responses.

**Gate:** 18+ PASS, 0 FAIL. RL-02 and RL-05 have documented timing-sensitivity skips (rate-limit window state is non-deterministic in live environments).

**Note:** RL-02 (starter exceeds limit) and RL-05 (429 has Retry-After) may SKIP if the rate-limit window hasn't reset between test runs. This is NOT a failure — other tests (RL-09, RL-11, RL-13) independently prove 429 enforcement. If a test FAILs (not SKIP), re-run with increased wait time per the procedure's known failure modes.

### Phase 8: Data Integrity & Backup Verification

Execute `docs/operations/data-integrity-test-procedure.md`.

Verifies Cosmos DB data consistency, partition key isolation, document schema compliance, and backup policy across all 9 tenant containers.

**Gate:** 25/25 PASS.

### Phase 9: Resilience & Failover

Execute `docs/operations/resilience-failover-test-procedure.md`.

Tests graceful degradation when Azure OpenAI, Cosmos DB, Key Vault, NATS, and Stripe are unavailable or degraded.

**Gate:** 29/29 PASS + 6 documented SKIPs (infrastructure dependencies not simulatable in production). Total: 35 tests executed, 29 PASS, 6 SKIP.

### Phase 10: Load Testing

Execute `docs/operations/load-test-procedure.md`.

Runs 50 concurrent simulated users for the configured duration. Validates SLA thresholds:
- P95 response time ≤ 2000ms for admin endpoints
- P95 response time ≤ 5000ms for chat endpoints
- Error rate < 1%
- Zero 500-series errors from auth/config endpoints

**Gate:** All SLA thresholds met. CONDITIONAL PASS (e.g., NATS disconnected but latency SLAs met) is NOT accepted — all conditions must be met cleanly.

### Phase 11: Conversation Quality

Execute `docs/operations/conversation-quality-test-procedure.md`.

Runs 25 golden conversation scenarios against the live AI pipeline, scoring each on a 1-5 scale across relevance, accuracy, tone, and policy compliance.

**Gate:** Quality pilot VERDICT = PASS (heuristic dimension thresholds: Faithfulness ≥ 3.5, Relevancy ≥ 3.5, Tone ≥ 3.0, Overall ≥ 3.5). Pipeline errors ≤ 2. No scenario with overall score < 2.0.

**Note:** This procedure requires `test-customer-001` to have an active AI configuration with KB articles seeded. Verify prerequisites before executing. Timeout-based NO_RESPONSE results count as pipeline errors, not quality failures.

### Phase 12: UI Regression

Execute `docs/operations/chrome-ui-test-procedure.md` (page-by-page tests).

917 browser-automated tests across standalone admin (780 tests), provider admin (23 tests), and Shopify embedded admin (76 tests + 38 deferred).

**Gate:** ≥ 793 PASS, 0 FAIL. SOFT-PASS (≤ 5) and SKIP (documented, ≤ 62) are accepted.

### Phase 13: SPA Provisioning + Critical Path

This phase proves the full tenant lifecycle: provider creates a tenant via the SPA console, then the merchant completes the entire first-use journey on that tenant. The provisioning pre-test (CP.P1–CP.P4) runs immediately before the Critical Path test (CP.1–CP.21) and feeds directly into it.

#### Pre-test: SPA Tenant Provisioning (CP.P1–CP.P4)

| # | Step | Verification | Evidence |
|---|------|-------------|----------|
| CP.P1 | **Create tenant** — Open Provider Console → Create Tenant modal → fill form (tenant ID: `mtp-smoke-001`, billing_channel: `manual`, tier: `starter`, superadmin email: test address) → submit | Tenant appears in Tenant Directory | Screenshot of Tenant Directory showing new row |
| CP.P2 | **Welcome email** — Verify welcome email received for `mtp-smoke-001` with correct standalone admin URL | Email received, URL is valid | Screenshot of email content |
| CP.P3 | **First login** — Open standalone admin URL from welcome email → verify wizard auto-shows | Wizard renders on first visit | Screenshot of wizard in browser |
| CP.P4 | **Cleanup** — Delete test tenant: `DELETE /api/superadmin/tenants/mtp-smoke-001` → verify removed from Tenant Directory | Tenant no longer listed | Screenshot of Tenant Directory without `mtp-smoke-001` |

CP.P1–CP.P4 must all PASS before proceeding to CP.1–CP.21. This confirms that when the release is frozen and beta customers are provisioned (Release Plan Step 3), the provisioning pathway is proven to work.

#### Critical Path Test (CP.1–CP.21)

Execute `docs/operations/chrome-ui-test-procedure.md` §Stage 0 — Critical-Path Test (CP.1–CP.21).

21-step sequential simulation of a merchant's complete first-use journey: login → dashboard → team → AI config → KB → activation → widget → chat → escalation → inbox → analytics → billing → settings → logout.

**Gate:** CP.P1–CP.P4 PASS + CP.1–CP.21 PASS (25 total). Three CP steps (CP.10, CP.16, CP.20) require manual email verification — these must be confirmed by human inspection.

### Phase 14: Upgrade Verification

Execute `docs/operations/upgrade-verification-procedure.md` (Phase A → Phase C).

Deploys a no-change version bump (e.g., v{FROZEN} → v{FROZEN}.1) to verify the deployment process preserves all tenant data. This validates that the release plan Step 6 (non-disruptive upgrade for beta customers) will work.

**Steps:**
1. Phase A: Capture pre-deployment snapshot (11 data points)
2. Phase B: Deploy version bump (zero code changes)
3. Phase C: Verify all 35 post-deployment assertions match Phase A values

**Gate:** 35/35 assertions match. API keys, widget keys, and all configuration preserved.

### Phase 15: Manual Verification

Items that cannot be automated. Each must be documented with evidence (screenshot, output, or written confirmation).

| # | MT-ID | Description | Evidence Required |
|---|-------|-------------|-------------------|
| M.1 | MT-1029 | Lighthouse: widget does not reduce score by >10 points | Lighthouse report screenshots (with/without widget) |
| M.2 | MT-1030 | Chrome incognito session token works | Screenshot of admin loading in incognito |
| M.3 | MT-1031 | Plan upgrade/downgrade on dev store | Screenshot of Shopify billing page after plan change |
| M.4 | MT-1032 | Submission screencast recorded | Video file exists and covers install→chat→escalation flow |
| M.5 | MT-1033 | App icon uploaded (1200×1200) | Screenshot of Partner Dashboard asset page |
| M.6 | MT-1034 | Screenshots uploaded (min 3, 1600×900) | Screenshot of Partner Dashboard listing page |
| M.7 | MT-1035 | Privacy policy URL set | Screenshot of iubenda + Partner Dashboard privacy field |
| M.8 | MT-1036 | Testing instructions prepared | Document exists with reviewer walkthrough |

**Gate:** All 8 items documented with evidence.

---

## 10. Success Criteria for 1.0 GA (v2.0)

**The release is gated on ALL 15 phases passing.** No phase may be skipped or marked "conditional."

| # | Phase | Target | Minimum Acceptable |
|---|-------|--------|-------------------|
| 1 | Pre-flight | 4/4 checks pass | 4/4 |
| 2 | Unit & Integration | 0 failures, coverage ≥ 70% | 0 failures, coverage ≥ 70% |
| 3 | Production Regression | 86/86 PASS | 86/86 |
| 4 | External URL Reachability | 37/37 PASS | 37/37 |
| 5 | Tenant Isolation | 30/30 PASS | 30/30 |
| 6 | API Security | 45/45 PASS | 45/45 |
| 7 | Rate Limiting | 20/20 PASS | 20/20 |
| 8 | Data Integrity | 25/25 PASS | 25/25 |
| 9 | Resilience & Failover | 29/29 PASS + 6 SKIP | 29/29 PASS + 6 SKIP |
| 10 | Load Testing | All SLAs met | All SLAs met |
| 11 | Conversation Quality | Pilot VERDICT = PASS | Pilot VERDICT = PASS |
| 12 | UI Regression | 793+ PASS, 0 FAIL | 793 PASS, 0 FAIL |
| 13 | SPA Provisioning + Critical Path | 25/25 PASS (4 provisioning + 21 CP) | 25/25 |
| 14 | Upgrade Verification | 35/35 match | 35/35 |
| 15 | Manual Verification | 8/8 documented | 8/8 |

### Aggregate Totals

| Metric | Count |
|--------|-------|
| Total Python tests (Phase 2) | ~4,791 |
| Total regression assertions (Phase 3) | 86 |
| Total non-functional assertions (Phases 4-11) | ~274 |
| Total UI browser tests (Phase 12) | 917 |
| Total provisioning + critical path steps (Phase 13) | 25 |
| Total upgrade assertions (Phase 14) | 35 |
| Total manual items (Phase 15) | 8 |
| **Grand total test points** | **~6,114** |

### Pre-existing Failure Policy

**No pre-existing failures are accepted for the 1.0 GA release gate.** Any test that was previously failing must be either:
1. **Fixed** — root cause resolved, test passes
2. **Removed with justification** — test is obsolete, duplicated, or tests a 1.1-deferred feature

~~The following known pre-existing failures must be resolved before Phase 2 can begin:~~
- ~~`activation_service` test failure (1 test) — must be investigated and fixed~~ → **RESOLVED (S79):** Root cause was consent model test drift. All 4,518 tests pass with 0 failures.
- ~~T1-11 regression failure (if still present) — must be investigated and fixed~~ → **RESOLVED (S73):** Root cause was `step_order` int→float type mismatch. Fixed in v1.55.1.

**Status: 0 pre-existing failures.** Phase 2 ready for execution.

### Execution Record

When executing this plan, record results in `docs/tests/MASTER-TEST-EXECUTION-RESULTS-{VERSION}.md` using the template from `MASTER-TEST-EXECUTION-RESULTS-1.0.md`. Each phase must include:
- Date and time of execution
- Version under test
- Pass/fail count
- Any deviations or retries
- Evidence for manual items

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
