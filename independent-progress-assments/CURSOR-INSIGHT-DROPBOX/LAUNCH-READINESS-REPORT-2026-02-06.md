# Launch Readiness Report — Agent Red Customer Experience

**Date:** 2026-02-06  
**Purpose:** Pre-GA readiness assessment across architecture, implementation, usability, compliance, and cost.  
**Scope:** Strengths and weaknesses for commercial SaaS launch.  
**Author:** Loyal Opposition (Cursor), per CURSOR-LOYAL-OPPOSITION-ROLE.md  
**Evidence:** CLAUDE.md, docs/, src/, admin/, widget/, tests/, legal/, config/

---

## Executive Summary

Agent Red Customer Experience is in the final stage of readiness-testing before GA. The codebase is **technically mature**: 1,624 tests passing, 21 routers / 78+ routes, 9 middleware layers, production deployment on Azure Container Apps, dual admin frontends (Shopify + standalone) and chat widget build-validated. **Strengths** include strong architecture (tenant isolation, security middleware, cost model), comprehensive test coverage, and clear documentation. **Gaps** center on: (1) production env vars not yet set on API Gateway (WI #198b), blocking tenant lookup and chat in production; (2) doc inconsistencies (GDPR webhooks implemented in code but listed as incomplete in checklists); (3) legal docs and Shopify App Store checklist items still pending (creative assets, session-token/Save Bar doc alignment); (4) no formal performance/load test execution; (5) Privacy Policy and legal docs marked draft / pending legal review. **Recommendation:** Complete WI #198b and doc sync, then run end-to-end chat and UX evaluation on production; treat legal review and creative assets as parallel tracks.

---

## 1. Architecture

### 1.1 Technology Choices

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Backend | FastAPI, Python 3.12+, Starlette ASGI, 21 routers, 78+ routes | **Strength:** Modern async stack, clear route map in CLAUDE.md. |
| AI pipeline | Azure OpenAI (GPT-4o, GPT-4o-mini, text-embedding-3-large), direct API Gateway calls (USE_AGENT_CONTAINERS=false) | **Strength:** Single vendor (Azure), pay-per-token; fallback path documented. |
| Data | Cosmos DB Serverless, 9 collections, partition key tenant_id, DiskANN vector index | **Strength:** Tenant-scoped schema, vector search for RAG and Persistent Memory. |
| Messaging | NATS JetStream (internal), lazy init; optional for launch | **Neutral:** Agent containers not used in default path; NATS connected=false in /ready accepted. |
| Frontend | Widget: Preact + Shadow DOM; Admin: React, Polaris + App Bridge (Shopify), custom (standalone) | **Strength:** Appropriate split; both admin shells build-validated. |
| Infra | Azure Container Apps, Key Vault (RBAC), Terraform (16 resources, clean plan) | **Strength:** Managed identities, no secrets in env where avoidable. |

**Weakness:** No single “architecture decision record” index linking decisions to files; decisions live in Master-Plan-Review and CLAUDE.md. Acceptable for launch if CLAUDE.md remains canonical.

### 1.2 Reliability

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Health probes | /health, /ready; Key Vault and circuit breakers in /ready | **Strength:** Production verification (2026-02-03): /health 200, /ready 200. |
| Fail-closed Critic | critic_policy.py; pipeline does not deliver unvalidated responses | **Strength:** Documented and tested. |
| Graceful shutdown | GRACEFUL_SHUTDOWN_TIMEOUT=60, startup/shutdown events in main.py | **Strength:** Present. |
| Agent containers | ActivationFailed state documented as expected (demo-mode images) | **Neutral:** Not used in default path; no impact if Azure OpenAI path is used. |

**Weakness:** No explicit SLO/SLA validation in CI (e.g., P95 latency gates). SLA doc exists (legal/sla/); operational monitoring is documented but not automated in this repo.

### 1.3 Performance

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Latency | AGNTCY baseline: P95 <2s; SSE streaming (WI #129–133) complete | **Strength:** Design targets documented; first-chunk metering, multi-tab coordination in place. |
| Connection pooling | httpx AsyncClient with limits (max_connections, keepalive) in upstream patterns | **Strength:** Documented in CLAUDE.md. |
| Caching | Semantic cache (WI #223–225): 3-tier, LRU+TTL, per-tenant | **Strength:** Implemented; cost savings tracking. |
| Body/JSON limits | RequestBodyLimitMiddleware (1 MB), JsonDepthValidationMiddleware (depth 50) | **Strength:** DoS mitigation. |

**Weakness:** COMPREHENSIVE-TEST-PLAN lists performance/load tests (~30) as “Remaining Gap”; no evidence of executed load runs in repo. Recommendation: run at least one baseline load test before GA and record results.

### 1.4 Security

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Auth | Triple auth: Shopify JWT (HS256), API key (hashed, Key Vault), widget key (pk_live_); auth exemption list explicit | **Strength:** auth.py and middleware well-documented; AUTH_EXEMPT_PREFIXES for webhooks and admin SPA. |
| Security headers | security_middleware.py: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, HSTS when HTTPS | **Strength:** OWASP-aligned; CSP noted for future (frame-ancestors for Shopify). |
| Webhook verification | Stripe (signature), Shopify GDPR (HMAC-SHA256 in shopify_gdpr_webhooks.py) | **Strength:** HMAC verification before processing. |
| Pre-auth rate limit | PreAuthRateLimitMiddleware (WI #157–163) | **Strength:** Hardening in place. |
| Audit | AuditLogRepository, security.event for API key actions | **Strength:** Documented. |

**Weakness:** CORS defaults to `*` when APP_CORS_ORIGINS unset; production should set explicit origins. CLAUDE.md notes “restrict in production via APP_CORS_ORIGINS.”

### 1.5 Multitenancy (Tenant Isolation)

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Data access | TenantScopedRepository; tenant_id mandatory; Cosmos partition key tenant_id | **Strength:** 7 tenant-scoped collections; repository pattern consistent. |
| NATS | Tenant-scoped topics `{tenant_id}.{agent}` (nats_isolation.py) | **Strength:** Documented; not in critical path when USE_AGENT_CONTAINERS=false. |
| Secrets | Key Vault per-tenant naming (tenant-{id}-{type}) | **Strength:** tenant_secret_service. |
| Rate limits | Per-tenant sliding window (Starter 10/min, Pro 50/min, Enterprise 200/min) | **Strength:** RateLimitMiddleware with headers. |

**No material weakness identified** for tenant isolation at launch.

### 1.6 Scalability

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Horizontal scaling | Container Apps min/max replicas; KEDA triggers referenced | **Strength:** API Gateway 2–8, agents 2–10; scaling strategy documented. |
| Stateless API | FastAPI stateless; TenantContext per request | **Strength:** No in-memory tenant state in gateway. |
| Cosmos | Serverless, pay-per-request | **Strength:** Scales with load. |

**Weakness:** No load-test evidence to validate scaling behavior under target concurrency.

### 1.7 Resiliency

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Circuit breakers | Referenced in /ready; pipeline_resilience.py (timeout budgets, per-tenant concurrency) | **Strength:** Documented. |
| Azure OpenAI fallback | ChatPipeline direct Azure OpenAI (WI #207); no dependency on agent containers for default path | **Strength:** Reduces failure surface. |
| Retries | SSE error handling, first-chunk metering (WI #129–133) | **Strength:** Chat layer covered. |

**Weakness:** No chaos or failure-injection tests observed; acceptable for v1 if runbooks exist.

### 1.8 Supportability

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Logging | structured_logging.py; PII scrubbing at logging layer (Decision #7) | **Strength:** No customer data in Application Insights per design. |
| Tracing | OpenTelemetry; tenant_id in telemetry | **Strength:** Documented. |
| Admin APIs | 5 routers, 25 endpoints (conversations, knowledge, analytics, team, GDPR, audit, profiles) | **Strength:** Enables support workflows. |
| Runbooks | docs/operations/DEPLOYMENT-RUNBOOK.md, LAUNCH-CHECKLIST.md | **Strength:** Present. |

**Weakness:** No in-app “Support” or “Help” link to docs or contact in the reviewed UI paths; consider adding for GA.

### 1.9 Maintainability

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Structure | src/ by domain (integrations, multi_tenant, chat, jobs); admin/shared + shopify + standalone | **Strength:** Clear separation; 45+ multi_tenant modules. |
| Docs | CLAUDE.md canonical; docs/architecture/, docs/operations/, Master-Plan-Review | **Strength:** Architecture and decisions traceable. |
| Dependencies | requirements.txt, package.json per frontend; AGNTCY via PyPI only | **Strength:** No local AGNTCY coupling. |

**Weakness:** Some checklist/status docs out of date vs. code (e.g., GDPR webhooks); see §2.8.

---

## 2. Implementation

### 2.1 Code and Script Best Practices

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Python | Type hints, dataclasses, Pydantic models; async/await consistent | **Strength:** main.py, auth.py, shopify_gdpr_webhooks.py, cost_model.py sampled; docstrings and copyright present. |
| API design | REST, consistent prefixes (/api/...), tags in OpenAPI | **Strength:** Route map in CLAUDE.md; 401/403/429/503 responses declared. |
| Error handling | Global exception handler in main.py (500, no stack to client); HMAC/logging in webhooks | **Strength:** Safe default. |

**Weakness:** CORS and APP_CORS_ORIGINS not validated for production value in code review.

### 2.2 Depth and Quality of Comments

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Module docstrings | main.py, auth.py, shopify_gdpr_webhooks.py, security_middleware.py, cost_model.py | **Strength:** Purpose, auth flow, constants, and copyright; suitable for onboarding. |
| Inline comments | Security middleware constants, HMAC steps, exempt paths | **Strength:** Where complex, comments present. |
| Frontend | HelpTooltip.tsx JSDoc; component purpose clear | **Strength:** Admin shared components documented. |

**No material weakness** for comment depth at launch.

### 2.3 Code Errors or Inconsistencies

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Test results | 1,624 tests collected (pytest --co); CLAUDE.md: 0 failures | **Strength:** Large suite; CI (GitHub Actions) referenced. |
| Status vs. code | GDPR webhooks: implemented in shopify_gdpr_webhooks.py (3 endpoints, HMAC); CLAUDE.md Phase 2.1 and APP-STORE-LISTING §11 say “not yet implemented” | **Weakness:** Doc inconsistency; recommend updating checklists to “implemented, verify in production.” |
| Session token / Save Bar | CLAUDE.md: “Session tokens, App Bridge Save Bar — completed during Build Phase 5” vs. “[ ] Implement session token…” and “[ ] Implement App Bridge Save Bar” in same file | **Weakness:** Resolve checklist vs. status line; if implemented, mark complete and remove from “blocked by.” |

### 2.4 Compute/Memory Resource Efficiency

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Body limit | 1 MB default; streaming endpoints exempt where needed | **Strength:** Prevents oversized payloads. |
| JSON depth | 50 levels max | **Strength:** Prevents deep recursion. |
| Connection pooling | Documented for Azure OpenAI (upstream) | **Strength.** |

**No material weakness** for resource efficiency in API layer.

### 2.5 Storage Use Efficiency

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Cosmos | Serverless; partition key tenant_id; 9 collections | **Strength:** Model documented in cosmos_schema.py. |
| Archival | archival_pipeline.py; Parquet to Azure Blob | **Strength:** Retention and archival documented. |
| Semantic cache | LRU+TTL, per-tenant | **Strength:** Bounded growth. |

**No material weakness** identified.

### 2.6 AI Model Service Use and Efficiency

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Cost per conversation | cost_model.py: ~$0.0073; GPT-4o response ~94.5% | **Strength:** Validated in architecture review; single number for margin calc. |
| Model choice | GPT-4o-mini for IC/critic; GPT-4o for RG | **Strength:** Right-sizing documented in AGNTCY lessons. |
| Caching | Semantic cache (embedding, search, similarity) reduces repeat calls | **Strength:** WI #223–225. |

**No material weakness** for AI efficiency at launch.

### 2.7 Documentation Depth and Coverage

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| CLAUDE.md | Project identity, upstream AGNTCY, pricing, route map, status, decisions | **Strength:** Single source of truth; dense but complete. |
| docs/ | architecture/, operations/, shopify/, workflows/, Master-Plan-Review, COMPREHENSIVE-TEST-PLAN, BACKLOG | **Strength:** Good coverage. |
| README, LAUNCH-CHECKLIST | Setup and launch steps | **Strength:** Actionable. |
| API docs | OpenAPI; /docs and /redoc in development | **Strength:** Standard FastAPI. |

**Weakness:** Executive Summary / third-party validation (Kiro) noted test count discrepancy (777 vs 930); COMPREHENSIVE-TEST-PLAN and CLAUDE.md now show 1,624. Ensure any external report uses a dated snapshot and source (e.g., “1,624 tests, pyproject.toml, 2026-02-06”).

### 2.8 Design Documents (e.g., GitHub Wiki) Coverage and Quality

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Architecture | Master-Plan-Review (32 decisions, 100 work items), UI-UX-ARCHITECTURE-DECISIONS, RAG-GAP-ANALYSIS, PERSISTENT-CUSTOMER-MEMORY-METRICS | **Strength:** Mermaid diagrams; decisions traceable. |
| Operations | DEPLOYMENT-RUNBOOK, LAUNCH-CHECKLIST, OPTION-C-UPGRADE-PATH | **Strength:** Deployment and launch steps clear. |
| Shopify | APP-STORE-LISTING, COMPETITOR-COMPARISON, testing instructions | **Strength:** Listing copy and reviewer instructions ready. |

**Weakness:** APP-STORE-LISTING §11 and §12 (Technical Requirements / Pre-Submission) still list “GDPR compliance webhooks (3 endpoints)” as not implemented; code has them. Update to “Implemented; verify URLs and HMAC in production.”

### 2.9 Test Plan and Execution Coverage and Completeness

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Count | 1,624 tests collected (pytest --co); CLAUDE.md: 1,582 unit + 42 integration, 0 failures | **Strength:** Target exceeded; P0–P3 complete per CLAUDE.md. |
| Plan | COMPREHENSIVE-TEST-PLAN: P0–P3, adversarial, performance, trial; gap table | **Strength:** Structured; IDs and modules mapped. |
| CI | GitHub Actions (Python 3.12/3.14) referenced | **Strength.** |
| Integration | Real Stripe test mode, Shopify partner sandbox, Azure services — COMPLETE per CLAUDE.md | **Strength.** |
| Performance/load | Plan lists ~30 tests; “Remaining Gap” for execution | **Weakness:** No evidence of executed load/performance run; recommend one baseline before GA. |
| Adversarial | ~20 in P2 §6.8; plan targets ~45 | **Neutral:** Partial coverage; acceptable if security tests run in CI. |

---

## 3. Usability

### 3.1 Completeness and Functionality of User Interfaces (Chat + Admin)

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Chat widget | 20 files, ~3,200 lines; Launcher, Panel, MessageList, MessageBubble, InputBar, PreChatForm, ChatRating, OfflineForm; SSE/WS | **Strength:** Component list and transport in CLAUDE.md and UI-UX-ARCHITECTURE-DECISIONS; build validated. |
| Admin shared | 9 components: OnboardingWizard, ConfigEditor, UsageDashboard, ConversationInbox, KnowledgeBaseManager, AnalyticsOverview, BillingPortal, WidgetConfigurator, TeamManager | **Strength:** Both shells use them; build validated. |
| Shopify admin | 7 pages (Dashboard, Billing, Configuration, Inbox, KnowledgeBase, Settings, Widget); Polaris + App Bridge | **Strength:** Documented; useSaveBar.ts present. |
| Standalone admin | 7 pages + Onboarding, API key login; password-gated at /admin/standalone/ | **Strength:** Preview URL and password in CLAUDE.md. |

**Weakness:** Production chat not yet exercised end-to-end until WI #198b (env vars) is done; storefront onboarding (WI #199–202) and UX evaluation (WI #203) follow.

### 3.2 Completeness of Tooltips

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Admin | HelpTooltip.tsx: shared component with text + optional docLink; used across shared components; aria-label and role=button | **Strength:** Consistent pattern; keyboard and hover. |
| Widget | Greeting, labels, placeholders in locale/en.ts; no dedicated HelpTooltip in widget | **Neutral:** Chat UI is compact; tooltips may be less critical than in admin. |

**No critical weakness**; consider adding brief tooltips for launcher and “Send” where helpful for accessibility.

### 3.3 Consistency with Documentation

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| API vs. docs | Route map in CLAUDE.md matches main.py mount order; OpenAPI tags align | **Strength.** |
| Checklist vs. code | GDPR webhooks and session token/Save Bar status inconsistent (see §2.3) | **Weakness:** Sync Phase 2.1 checklist and APP-STORE-LISTING with implementation. |

### 3.4 Administrative Workflows Best-Practices Adherence

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Onboarding | OnboardingWizard component; LAUNCH-CHECKLIST: provision tenant, seed KB, embed KB | **Strength:** Scripts and steps documented. |
| Config | tenant_config_api (10 endpoints); ConfigEditor, preview, reset, history | **Strength.** |
| Billing | Stripe Customer Portal, usage dashboard, conversation export | **Strength.** |
| Knowledge base | Admin CRUD, upload, bulk-import/export, verify, re-embed, stale list | **Strength.** |

**No material weakness** for admin workflow design.

### 3.5 Administrative Access Control

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Shopify admin | Session token (JWT); tenant from shop domain | **Strength:** Auth flow in auth.py. |
| Standalone | API key; password gate for /admin/standalone/ (documented) | **Strength:** Explicit gate. |
| API | Bearer (Shopify), X-API-Key, X-Widget-Key; 401 on auth failure | **Strength.** |

**Weakness:** Standalone password is in CLAUDE.md; ensure it is changed for production or replaced by proper auth (e.g., API key or SSO) before GA if that path is public.

### 3.6 Error Handling

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| API | Global 500, no stack leak; 401/403/429/503 in OpenAPI | **Strength.** |
| SSE | Error handling, fallback messages (chat tests) | **Strength.** |
| Widget | OfflineForm, retraction, streaming cursor (MessageBubble) | **Strength:** Documented in UI spec. |

**No material weakness** for error-handling design.

### 3.7 Visual Style Consistency with Modern SaaS Standards

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Brand | BRAND-GUIDELINES, color palette (WCAG AA/AAA), Inter + JetBrains Mono; dark mode palette (chrome #0a0a0a → border #272727) | **Strength:** Designer-refined, frozen. |
| Admin | Mantine components, 13 global CSS rules, Remaker Digital logo in sidebar | **Strength:** Consistent with design. |
| Widget | theme/tokens.ts, locale/en.ts | **Strength:** Theming and i18n hook. |

**No material weakness** for visual consistency.

### 3.8–3.10 Usability on Mobile, Tablet, Desktop (Chrome, Edge, Firefox)

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Responsive | UI-UX-ARCHITECTURE-DECISIONS: mobile detection, auto-open rules; APP-STORE-LISTING: mobile screenshot spec 750×1334 | **Strength:** Specs exist; prototype approved. |
| Browsers | No explicit compatibility matrix in reviewed docs | **Neutral:** Recommend one pass in Chrome, Edge, Firefox on desktop and one mobile browser before GA; document in LAUNCH-CHECKLIST or test plan. |

**Weakness:** No written “tested on” matrix; add to post-launch verification or test plan.

---

## 4. Compliance

### 4.1 GDPR

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Data export/deletion | gdpr_services.py; DataExportService, DataDeletionService; admin_gdpr_api (export, delete, consent) | **Strength:** Backend support. |
| Shopify GDPR webhooks | shopify_gdpr_webhooks.py: POST customers-data-request, customers-redact, shop-redact; HMAC-SHA256 verification | **Strength:** Implemented; endpoints mounted under /api/shopify/gdpr. |
| Consent | consent_status (granted/denied/not_asked) gating Persistent Memory Layers 2–4; ConsentManager (Decision #34) | **Strength:** Documented. |
| PII | Scrubbing at logging; tokenization for external AI (per AGNTCY); Azure OpenAI in-perimeter | **Strength.** |
| Legal | PRIVACY-POLICY.md, DATA-PROCESSING-AGREEMENT.md — draft, “Legal Review Required” | **Weakness:** Must be reviewed by counsel and published before GA in EU/markets requiring it. |

**Recommendation:** (1) Update all checklists to state GDPR webhooks are implemented; (2) Confirm Shopify GDPR URLs in shopify.app.toml and production env (SHOPIFY_API_SECRET for HMAC); (3) Complete legal review and publish Privacy Policy and DPA.

### 4.2 Shopify Standards for App Approval

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| GDPR webhooks | 3 endpoints implemented; HMAC verification | **Strength.** |
| Session token | Auth path in auth.py (JWT HS256); App Bridge in admin/shopify | **Strength** (if checklist updated). |
| Save Bar | useSaveBar.ts in admin/shopify | **Strength** (if checklist updated). |
| Listing copy | APP-STORE-LISTING: name, tagline, description, benefits, features, pricing, search terms, testing instructions | **Strength.** |
| Creative assets | Icon, screenshots, key benefit images, optional video — pending (LAUNCH-CHECKLIST, APP-STORE-LISTING §9, §12) | **Weakness:** Blocking submission until produced. |
| Performance | “<500ms P95” in checklist; no evidence of validation run | **Weakness:** Run and record before submission. |
| Privacy policy URL | Must be public for submission | **Weakness:** Depends on legal review and publication. |

**Recommendation:** Align APP-STORE-LISTING §11–§12 and CLAUDE.md Phase 2.1 with actual implementation; then focus on creative assets, privacy policy URL, and one performance validation.

---

## 5. Cost

### 5.1 Accuracy of Cost Estimates

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Per-conversation AI | cost_model.py: $0.0073; breakdown (response_generator 94.5%, etc.) | **Strength:** Matches CLAUDE.md and architecture review. |
| Infrastructure | INFRA_COST_LOW/HIGH $252–436/mo; PER_TENANT_MARGINAL $13–41/mo | **Strength:** Documented; Option B+ redundancy included. |
| Tier pricing | TIER_PRICING in cost_model.py matches CLAUDE.md ($149/$399/$999, overage rates) | **Strength.** |

**Weakness:** No automated “cost vs. actual” reconciliation (e.g., Azure billing vs. model); recommend a quarterly check post-launch.

### 5.2 Current Pricing and Gross Margin Target

| Aspect | Evidence | Assessment |
|--------|----------|------------|
| Margins | CLAUDE.md and cost_model: 76–90% gross margin at list price (validated Jan 2026) | **Strength:** Cost basis and pricing aligned in docs. |
| Competitive | “4–21x cheaper” vs. 5 competitors (2026-02-01); pricing design principles in CLAUDE.md | **Strength.** |

**No material weakness** for launch; ongoing monitoring recommended.

---

## 6. Summary: Strengths and Weaknesses

### Strengths

- **Architecture:** Clear multi-tenant model, tenant isolation (data, NATS, secrets, rate limits), security middleware, and cost model; production deployment and health verified.
- **Implementation:** 1,624 tests, strong module docstrings, consistent error handling; GDPR webhooks and session/Save Bar implemented in code.
- **Usability:** Chat widget and dual admin (Shopify + standalone) build-validated; HelpTooltip pattern; onboarding and config workflows documented.
- **Compliance:** GDPR webhook endpoints and HMAC verification in place; consent and PII handling designed.
- **Cost:** Transparent cost model and margin range; pricing validated against competitors.

### Weaknesses and Actions

| # | Weakness | Suggested action |
|---|----------|------------------|
| 1 | WI #198b not done: SHOPIFY_API_KEY, SHOPIFY_API_SECRET, AZURE_OPENAI_* not set on API Gateway | Set env vars per LAUNCH-CHECKLIST; verify /health and tenant lookup + one chat request. |
| 2 | Doc inconsistency: GDPR webhooks and session/Save Bar marked incomplete in checklists but implemented in code | Update CLAUDE.md Phase 2.1 and APP-STORE-LISTING §11–§12 to “implemented; verify in production.” |
| 3 | No executed performance/load test | Run one baseline load test (e.g., COMPREHENSIVE-TEST-PLAN §9), record P95 and document in repo or ops doc. |
| 4 | Legal docs (Privacy Policy, DPA) draft; “Legal Review Required” | Complete legal review and publish before GA in relevant markets. |
| 5 | Creative assets (icon, screenshots, video) pending | Owner/designer track; blocks Shopify App Store submission. |
| 6 | CORS defaults to * | Set APP_CORS_ORIGINS in production to explicit origins. |
| 7 | Standalone admin password in docs | Change for production or replace with proper auth if path is public. |
| 8 | No “tested on” browser/device matrix | Add one-pass verification (Chrome, Edge, Firefox, one mobile) to LAUNCH-CHECKLIST or test plan. |

---

## 7. Recommendation

- **Before GA:** Complete **WI #198b** (env vars on API Gateway), then run **end-to-end chat** and **storefront onboarding** (WI #199–202) and **UX evaluation** (WI #203). Sync **documentation** (GDPR, session token, Save Bar) with implementation. Run **one performance/load baseline** and publish **legal** docs after review.
- **Parallel:** Proceed with **creative assets** and **CORS/production auth** hardening so Shopify submission and production security are ready when technical and legal gates are met.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
