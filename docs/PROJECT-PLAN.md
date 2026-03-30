# Agent Red Customer Experience - Launch 1.0 Project Plan

> **Project:** Agent Red Customer Experience
> **Release:** Launch 1.0
> **Timeline:** Q1 2026 (8-12 weeks)
> **Budget:** $500-1,000/month operational
> **Last Updated:** 2026-02-10

---

## Executive Summary

Agent Red Customer Experience is a commercial SaaS product built on the open-source AGNTCY Customer Engagement Platform foundation. Launch 1.0 is a fully capable product release for general availability, targeting Q1 2026.

---

## Project Progress

```mermaid
gantt
    title Agent Red Launch 1.0 — Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %m-%d

    section Phase 0: Setup
    Project setup & AGNTCY baseline       :done, p0, 2026-01-29, 1d

    section Phase 1: Foundation
    1.1 Brand Identity                    :done, p11, 2026-01-29, 1d
    1.2 Legal Documents                   :done, p12, 2026-01-29, 1d
    1.3 Website Content                   :done, p13, 2026-01-29, 1d
    1.4 Public Documentation              :done, p14, 2026-01-29, 1d

    section Phase 2: Product
    2.1 E-Commerce Store                  :done, p21, 2026-01-30, 2d
    2.2 Multi-Tenant Infrastructure       :done, p22, 2026-01-30, 2d
    2.5 Persistent Memory L1-L2           :done, p25, 2026-01-31, 1d

    section Phase 3: UI/UX
    3.0 Chat API                          :done, p31, 2026-02-01, 1d
    3.0 Widget Frontend                   :done, p32, 2026-02-01, 1d
    3.0 Shopify Theme App Extension       :done, p33, 2026-02-01, 1d
    3.0 Admin Shared Components           :done, p34, 2026-02-01, 1d
    3.0 Shopify Admin Shell               :done, p35, 2026-02-01, 1d
    3.0 Standalone Admin Shell            :done, p36, 2026-02-01, 1d

    section Phase 2.5: Memory
    Persistent Memory L3-L4              :done, p25b, 2026-02-03, 1d

    section Testing
    P0 Launch Blockers (379 tests)        :done, t1, 2026-01-31, 1d
    P1 Pre-Launch (214 tests)             :done, t2, 2026-02-01, 1d
    P2 Launch Quality (222 tests)         :done, t3, 2026-02-01, 1d
    Operational + P3 + Security + Perf    :done, t4, 2026-02-01, 2d
    Integration Tests (42 real services)  :done, t5, 2026-02-02, 1d

    section Launch Preparation
    Cosmos DB initialization              :done, r0, 2026-02-03, 1d
    Production deployment                 :active, r1, 2026-02-03, 3d
    Remaker Digital storefront setup      :r2, after r1, 2d
    UX consultant evaluation (Mazel)      :r3, after r2, 5d
    Shopify App Store submission          :r4, after r1, 7d
    GA launch                             :milestone, m8, after r4, 0d
```

```mermaid
pie title Phase Completion Status
    "Complete" : 18
    "In Progress" : 2
    "Remaining (owner-blocked)" : 3
```

---

## Project Phases

### Phase 0: Project Setup (Week 1)
**Status:** Complete ✅

| Task | Status | Notes |
|------|--------|-------|
| Create project directory structure | ✅ Done | E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement |
| Create CLAUDE.md | ✅ Done | AI assistant guidance (v14.0.0 with full knowledge transfer) |
| Create PROJECT-PLAN.md | ✅ Done | This file |
| Create GitHub repository | ✅ Done | github.com/mike-remakerdigital/agent-red |
| AGNTCY dependency model | ✅ Done | Arms-length via public GitHub (no submodule) |
| Migrate commercial materials | ✅ Done | SaaS proposal, product features, website content |
| Initial commit pushed | ✅ Done | 23 files, 5,825 lines |
| Docker dev environment | ✅ Done | Dockerfile, docker-compose.yml, requirements.txt |
| AGNTCY baseline verification (local) | ✅ Done | 15 containers healthy, 97.8% unit / 99.3% integration pass |
| AGNTCY baseline verification (Azure) | ✅ Done | All 53 resources operational |
| Set up GitHub Project board | ✅ Done | 8 milestone issues (M1-M8) |

---

### Phase 1: Foundation (Weeks 2-4)
**Status:** Complete ✅

#### 1.1 Brand Identity

| Task | Status |
|------|--------|
| Logo concepts (primary, icon, wordmark) | ✅ Done — "The Beacon" AR monogram approved |
| Color palette selection | ✅ Done — 15 colors, WCAG AA/AAA, primary #C41E2A |
| Typography selection | ✅ Done — Inter + JetBrains Mono |
| Brand guidelines document | ✅ Done — branding/guidelines/BRAND-GUIDELINES.md |
| Favicon and app icons | 📋 Todo — derive from branding/logo/PNG/icon-master.png |

#### 1.2 Legal Documents

| Task | Status |
|------|--------|
| Draft Terms of Service | ✅ Done — legal/terms/TERMS-OF-SERVICE.md |
| Draft Privacy Policy | ✅ Done — legal/privacy/PRIVACY-POLICY.md |
| Draft SLA document | ✅ Done — legal/sla/SERVICE-LEVEL-AGREEMENT.md (v0.2.0) |
| Draft Data Processing Agreement | ✅ Done — legal/dpa/DATA-PROCESSING-AGREEMENT.md |
| Validate via iubenda | 📋 Deferred to pre-launch |

#### 1.3 Website Content

**Website strategy (decided 2026-02-03):**
- **1.0:** Agent Red pages hosted within https://remakerdigital.com under an "Applications" category. Opportunistic — not blocking 1.0 release.
- **1.1:** Standalone Agent Red website hosted on Azure. Target: polished, dedicated web presence.

| Task | Status |
|------|--------|
| Write homepage (commercial buyer focus) | ✅ Done |
| Write features page | ✅ Done |
| Write pricing page | ✅ Done — $149/$399/$999 base + metered AI usage |
| Write integrations page | ✅ Done |
| Write about page | ✅ Done |
| Write contact page | ✅ Done |
| Host within remakerdigital.com (Applications category) | 📋 1.0 — opportunistic, not blocking |
| Standalone agentredcx.com website (GitHub Pages + Docusaurus) | ✅ Done — deployed, DNS configured |

#### 1.4 Public Documentation

| Task | Status |
|------|--------|
| Set up Docusaurus | ✅ Done — docs-site/ with Agent Red branding, Mermaid support |
| Documentation quality framework | ✅ Done — Vale, markdownlint, alex, link-check, CI pipeline |
| Write getting-started guide | ✅ Done — 3 pages, 14 Mermaid diagrams |
| Write Shopify integration guide | ✅ Done — OAuth, sync, field mapping, 6 Mermaid diagrams |
| API authentication guide | 📋 Deferred to Phase 2 |
| API endpoint documentation | 📋 Deferred to Phase 2 |

---

### Phase 2: Product & Infrastructure (Weeks 5-8)
**Status:** Complete ✅ (E-Commerce ~98%, Multi-Tenant 100%, Memory ALL 4 LAYERS 100%)

#### 2.1 E-Commerce Store
**Platform:** Dual-channel — Shopify App Store (primary) + Stripe (direct). Decision documented in `docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md`.

| Task | Status |
|------|--------|
| Evaluate Shopify vs Stripe vs Paddle | ✅ Done — Three-way evaluation, dual-channel |
| Create Stripe Products/Prices/Coupons (test mode) | ✅ Done — 27 objects (config/stripe_product_ids.json) |
| Implement Stripe Checkout | ✅ Done — stripe_checkout.py |
| Implement Stripe webhook handler (7 events) | ✅ Done — stripe_webhooks.py |
| Implement metered usage reporting (3-tier) | ✅ Done — stripe_usage.py |
| Implement Shopify Billing API | ✅ Done — shopify_billing.py + shopify_client.py |
| Implement conversation pack purchase flow | ✅ Done — stripe_packs.py (FIFO, 90-day validity) |
| Implement unified webhook handler | ✅ Done — provisioning.py (channel-agnostic) |
| Implement Stripe Customer Portal | ✅ Done — stripe_portal.py |
| Set up Stripe Tax | ✅ Done — automatic_tax, txcd_10103001, exclusive pricing |
| Set up Rewardful affiliate integration | ✅ Done — client_reference_id (live connection deferred) |
| Implement GDPR compliance webhooks (3 Shopify endpoints) | ✅ Done — shopify_gdpr_webhooks.py |
| Implement session token authentication | ✅ Done — auth.py (Shopify JWT verification) |
| Implement App Bridge Save Bar API | ✅ Done — admin/shopify/hooks/useSaveBar.ts |
| Shopify App Store listing copy | ✅ Done — docs/shopify/APP-STORE-LISTING.md |
| Creative assets (icon, screenshots, demo video) | 📋 Todo — blocked on design |
| Submit for Shopify App Store review | 📋 Todo — blocked by creative assets |
| Test checkout flows (both channels) | 📋 Todo — integration testing |

#### 2.2 Multi-Tenant Infrastructure
**Status:** COMPLETE — 41 modules, ~28,000 lines. Architecture review: 32 decisions, 100 work items.

| Task | Status |
|------|--------|
| Architecture review (32 decisions, 100 WIs) | ✅ Done — docs/Master-Plan-Review-01-30-2026.md |
| Cosmos DB schema + TenantScopedRepository (#13-14, #24-25) | ✅ Done — cosmos_schema.py, cosmos_client.py, repository.py |
| Dual auth + middleware (#18, #27-28) | ✅ Done — auth.py, middleware.py |
| Billable conversation + ConversationMeter (#71-72) | ✅ Done — conversation_meter.py |
| Fail-closed Critic policy (#50) | ✅ Done — critic_policy.py |
| NATS tenant isolation (#15-17, #26) | ✅ Done — nats_isolation.py |
| GDPR services (#30-34, #36) | ✅ Done — gdpr_services.py |
| OpenTelemetry tracing (#39-41) | ✅ Done — otel_tracing.py |
| Pipeline resilience (#44-46) | ✅ Done — pipeline_resilience.py |
| SystemPromptBuilder (#70) | ✅ Done — system_prompt_builder.py |
| Usage Dashboard API (#73-74) | ✅ Done — usage_dashboard_api.py |
| Tenant config schema/processor/API (#63-65) | ✅ Done — tenant_config_*.py (3 modules) |
| TenantSecretService (#29) | ✅ Done — tenant_secret_service.py |
| DR + security Terraform (#52, #55, #58-59) | ✅ Done — dr_security.tf |
| Billing doc + SLA updates (#77-78) | ✅ Done — billable-conversation-spec.md, SLA v0.2.0 |
| TenantUsageMonitor progressive throttling (#51) | ✅ Done — tenant_usage_monitor.py |
| KEDA auto-scaling profiles (#47-48) | ✅ Done — dr_security.tf (KEDA + night scaling) |
| Security middleware (#157-159) | ✅ Done — security_middleware.py |
| Security hardening (#160-163) | ✅ Done — security_hardening.py |
| Structured logging (#149) | ✅ Done — structured_logging.py |
| API versioning (#140) | ✅ Done — api_versioning.py |
| Trial management (#119-128) | ✅ Done — trial_management.py (~1,200 lines) |
| SLA monitoring (#151) | ✅ Done — sla_monitoring.py (~390 lines) |
| Data retention (#154) | ✅ Done — data_retention.py (~380 lines) |
| Archival pipeline (#153) | ✅ Done — archival_pipeline.py (~750 lines) |
| Cost model calculator (#155) | ✅ Done — cost_model.py (~370 lines) |
| Alert delivery (#192) | ✅ Done — alert_delivery.py (~695 lines) |
| KB conflict/duplication scanner (#239) | ✅ Done — kb_conflict_scanner.py (~705 lines), 85 tests, docs page |

#### 2.5 Persistent Customer Memory
**Status:** ALL 4 LAYERS COMPLETE — 6 modules, 111 passing tests. Launch pillar differentiator.

| Task | Status |
|------|--------|
| CustomerProfileService — Layer 1 (#83-85) | ✅ Done — customer_profile_service.py (~520 lines) |
| ConversationVectorizer — Layer 2 (#87-88) | ✅ Done — conversation_vectorizer.py (~520 lines) |
| Response explainability framework (#86) | ✅ Done — response_explainability.py (~510 lines) |
| PatternExtractionService — Layer 3 (#90-92) | ✅ Done — pattern_extraction.py (~1,060 lines) |
| Admin Customer Profile API (#92) | ✅ Done — admin_customer_profile_api.py (~450 lines) |
| Fine-tuning pipeline — Layer 4 (#93-96) | ✅ Done — fine_tuning_pipeline.py (~1,870 lines) |
| Test fixtures + 111 tests (#97-98, #100) | ✅ Done — tests/persistent_memory/ (30 unit/integration + 81 fine-tuning) |
| 5 A/B production tests (#99) | 📋 Todo — requires sufficient production conversation volume |

#### 2.3 Admin Guides *(deferred — requires working product)*
| Task | Status |
|------|--------|
| Initial setup guide | 📋 Todo |
| Shopify connection guide | 📋 Todo |
| Knowledge base setup guide | 📋 Todo |
| Monitoring and alerts guide | 📋 Todo |

#### 2.4 Demo Videos *(deferred — requires working product)*
| Task | Status |
|------|--------|
| Platform overview (2-3 min) | 📋 Todo |
| Quick start tutorial (3-5 min) | 📋 Todo |

---

### Phase 3: UI/UX Frontend (Weeks 9-10)
**Status:** ALL BUILD PHASES COMPLETE ✅

```mermaid
flowchart LR
    subgraph "Build Phase 1"
        A[Chat API<br/>6 endpoints + SSE]
    end
    subgraph "Build Phase 2"
        B[Widget Frontend<br/>20 files, ~3,200 lines]
    end
    subgraph "Build Phase 3"
        C[Shopify Theme<br/>App Extension]
    end
    subgraph "Build Phase 4"
        D[Admin Shared<br/>9 components]
    end
    subgraph "Build Phase 5"
        E[Shopify Admin<br/>Polaris + App Bridge]
    end
    subgraph "Build Phase 6"
        F[Standalone Admin<br/>API key login]
    end

    A --> B --> C --> D --> E & F

    style A fill:#d4edda
    style B fill:#d4edda
    style C fill:#d4edda
    style D fill:#d4edda
    style E fill:#d4edda
    style F fill:#d4edda
```

| Deliverable | Files | Lines | Status |
|-------------|-------|-------|--------|
| Chat API (models, session, pipeline, endpoints, SSE manager) | 6 modules | ~2,800 | ✅ Complete |
| Widget frontend (Preact, Shadow DOM, iframe, 3-channel transport) | 20 files | ~3,200 | ✅ Complete |
| Shopify Theme App Extension (Liquid template, manifest) | 3 files | ~200 | ✅ Complete |
| Admin shared components (9 components + hooks + types) | 11 files | ~5,400 | ✅ Complete |
| Shopify admin shell (Polaris + App Bridge, 7 pages) | 10 files | ~2,700 | ✅ Complete (build validated) |
| Standalone admin shell (API key login, 7 pages) | 10 files | ~2,800 | ✅ Complete (build validated) |

**Admin Build Validation:**
- admin/shopify: 0 TS errors, 599.57 KB bundle (146.67 KB gzip)
- admin/standalone: 0 TS errors, 304.74 KB bundle (87.63 KB gzip)

---

### Phase 4: Testing & QA
**Status:** ALL PRIORITIES COMPLETE — 1,974 tests (1,889 unit + 42 integration + 43 regression), 0 failures ✅

```mermaid
xychart-beta
    title "Test Coverage by Priority"
    x-axis ["P0 Blockers", "P1 Pre-Launch", "P2 Quality", "Operational", "P3 Post", "Security", "Perf/Load", "Integration"]
    y-axis "Tests" 0 --> 400
    bar [379, 214, 222, 75, 40, 50, 47, 42]
```

| Suite | Tests | Status |
|-------|-------|--------|
| P0 — Launch blockers (HTTP billing, middleware, meter, Critic, Cosmos, health, catalog, usage) | 379 | ✅ Complete |
| P1 — Pre-launch (NATS, GDPR, OTEL, resilience, prompts, config, Shopify, memory, dashboard) | 214 | ✅ Complete |
| P2 — Launch quality (Shopify client, billing, checkout, explainability, profiles, vectors, cross-module, errors) | 222 | ✅ Complete |
| Operational (archival, retention, SLA, cost model) | 75 | ✅ Complete |
| P3 — Post-launch (tenant config deep, usage dashboard deep, audit log, usage monitor) | ~40 | ✅ Complete |
| Adversarial / security (injection, auth bypass, data isolation, rate limiting, input abuse) | 50 | ✅ Complete |
| Performance / load (SLA latency, pipeline timeout, circuit breakers, SSE, cost model) | 47 | ✅ Complete |
| Persistent Memory (L1-L4 unit + integration + fine-tuning) | 111 | ✅ Complete |
| Conftest smoke + health + pre-existing | 97 | ✅ Complete |
| Integration — real Stripe test mode (20 tests) | 20 | ✅ Complete |
| Integration — real Azure services (22 tests: OpenAI, Cosmos DB, Key Vault, E2E) | 22 | ✅ Complete |
| KB Conflict Scanner (similarity, overlap, classification, full scan, caching) | 85 | ✅ Complete |

| Metric | Value |
|--------|-------|
| Unit tests | 1,889 |
| Integration tests (real services) | 42 |
| Regression tests | 43 |
| Total tests | 1,974 |
| Failures | 0 |
| CI pipeline | GitHub Actions (Python 3.12/3.14) |

---

### Phase 5: Operational Readiness
**Status:** Complete ✅

| Task | Status |
|------|--------|
| Deployment runbook | ✅ Done — docs/operations/DEPLOYMENT-RUNBOOK.md |
| DR runbook — Option A | ✅ Done — docs/operations/DEPLOYMENT-RUNBOOK.md |
| Maintenance runbook | ✅ Done — docs/operations/DEPLOYMENT-RUNBOOK.md |
| Option C upgrade path documentation | ✅ Done — docs/operations/OPTION-C-UPGRADE-PATH.md |
| SLA monitoring service | ✅ Done — sla_monitoring.py |
| Data retention enforcement | ✅ Done — data_retention.py |
| Archival pipeline (Hot→Warm Parquet) | ✅ Done — archival_pipeline.py |
| Cost model calculator | ✅ Done — cost_model.py |
| Alert delivery service | ✅ Done — alert_delivery.py |
| KEDA night scaling | ✅ Done — dr_security.tf |
| Scheduled Container App Jobs (cron) | ✅ Done — run_retention.py, run_archival.py |

---

### Phase 6: Launch Preparation
**Status:** Partially Complete — triaged S234 🔄

> **Triage note (S234, 2026-03-30):** Items below annotated with current status after S234 triage.
> Production/deployment claims are owner-reported via MEMORY.md; formal deployment closure
> artifacts (GOV-16 record, stability verification) should be linked when available.

#### 6.1 Infrastructure & Deployment
| Task | WI | Status |
|------|-----|--------|
| Cosmos DB full initialization (10 containers, DiskANN) | — | ✅ Done — scripts/init_cosmos_containers.py, all 10 verified |
| Azure OpenAI custom subdomain | — | ✅ Done (S234 triage) — Azure OpenAI on all 6 agent containers, 150K TPM GlobalStandard |
| Build Docker container images + push to ACR | #196 | ✅ Done (owner-reported) — v1.98.73, 10 images built and pushed via build.py |
| Production deployment (Terraform apply) | #197 | 🔶 Owner-reported — v1.98.73 deployed per MEMORY.md S233; GOV-16 closure artifact pending |
| Widget bundle deployment | #198 | ✅ Done (S234 triage) — widget delivered via CDN/API, not TAE asset copy (architecture changed) |

#### 6.2 Remaker Digital Storefront (Sales Channel + Live Demo)
**Strategy (decided 2026-02-03):** Create a Remaker Digital Shopify storefront to serve dual purpose: (1) sell Agent Red subscriptions via Stripe-direct, (2) deploy Agent Red as the store's own chat system as a live product demo. Agent Red becomes tenant #1.

| Task | WI | Status |
|------|-----|--------|
| Create Remaker Digital Shopify storefront | #199 | ✅ Done (S234 triage) — blanco-9939.myshopify.com operational, widget verified S226 |
| Onboard Remaker Digital as tenant #1 | #200 | ✅ Done (S234 triage) — tenant seeded, 20 tenants total |
| Seed knowledge base with Agent Red product data | #201 | ✅ Done — SPEC-0201 implemented |
| Deploy widget on storefront | #202 | ✅ Done (S234 triage) — widget live on blanco-9939, verified S226 |
| UX consultant evaluation — Mazel (onboarding, Shopify integration, widget testing, escalation) | #203 | 📋 Blocked — owner prerequisite (consultant scheduling) |

#### 6.3 Shopify App Store Submission
| Task | WI | Status |
|------|-----|--------|
| App icon (1200x1200) | — | 📋 Blocked — owner/designer task |
| Key benefit images (3x 1600x1200) | — | 📋 Blocked — owner task |
| Screenshots (desktop + mobile, 1600x900) | — | 📋 Blocked — requires creative assets |
| Demo video (optional) | — | 📋 Blocked — requires creative assets |
| Submit for Shopify App Store review | — | 📋 Blocked — requires creative assets + owner decision |

#### 6.4 Creative Assets
| Task | WI | Status |
|------|-----|--------|
| Favicon and app icons (from icon-master.png) | #204 | 📋 Blocked — owner/designer task |
| Admin UI color palette refinement | — | 📋 Blocked — owner/designer task |
| OG image for social sharing (1200x630) | — | 📋 Blocked — owner/designer task |

#### 6.5 Launch Readiness
| Task | WI | Status |
|------|-----|--------|
| Final documentation review | — | 📋 Active — agentredcx.com docs need update for extensibility |
| Production stability validation (48 hrs) | — | 🔶 Owner-reported — production operational since v1.98.41 (S221); formal 48-hr validation artifact pending |
| GA launch | — | 📋 Blocked — requires creative assets + Shopify submission |

---

## Budget Allocation

### Monthly Operational Costs

| Category | Service | Monthly Cost |
|----------|---------|--------------|
| **Infrastructure** | Azure (production) | $252-436 |
| **E-commerce** | Stripe (~3.5% variable) + Shopify ($0 < $1M) + Rewardful (~$49/mo) | $49 + variable |
| **Legal** | iubenda (Advanced plan) | $0-52 |
| **Documentation** | Docusaurus (Vercel) | $0 |
| **Domain/DNS** | Cloudflare | $0-20 |
| **Total** | | **$301-557** |

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline slip | High | Medium | MVP scope, aggressive optimization |
| Budget overrun | Medium | Low | Cost model validated ($252-436/mo infra) |
| Multi-tenant complexity | High | Low | 42+ modules complete, 1,974 tests passing |
| Shopify App Store rejection | Medium | Medium | GDPR webhooks, session tokens, Save Bar all implemented |
| Creative asset delays | Medium | High | App Store submission blocked on icon/screenshots |

---

## Success Criteria

### Launch 1.0 Minimum Viable

| Criterion | Target | Status |
|-----------|--------|--------|
| Website content ready | Yes | ✅ |
| Documentation published | Yes | ✅ |
| Legal documents drafted | Yes | ✅ |
| Multi-tenant infrastructure | Yes | ✅ (42+ modules, 1,974 tests) |
| Chat widget functional | Yes | ✅ (20 files, build validated) |
| Admin dashboard functional | Yes | ✅ (2 shells, build validated) |
| E-commerce billing functional | Yes | ✅ (dual-channel) |
| Persistent Customer Memory (all 4 layers) | Yes | ✅ (6 modules, 111 tests) |
| Remaker Digital storefront (live demo) | Yes | 📋 Pending (production deployment) |
| Shopify App Store listed | Yes | 📋 Pending (creative assets + deployment) |
| First trial signup | Yes | 📋 Pending |
| Platform stable 48 hrs | Yes | 📋 Pending (production deployment) |

### Post-Launch (30 days)

| Metric | Target |
|--------|--------|
| Trial signups | 10+ |
| Paid conversions | 2+ |
| Uptime | 99.5%+ |
| Support ticket resolution | <24 hrs |

---

## Dependencies

### External Dependencies

| Dependency | Type | Risk |
|------------|------|------|
| AGNTCY open-source stability | Technical | Medium |
| Azure service availability | Infrastructure | Low |
| Shopify App Store review | E-commerce (primary) | Low |
| Stripe | E-commerce (direct) | Low |
| Rewardful | Affiliate program | Low |
| iubenda | Legal document generation | Low |

---

## Milestones

```mermaid
flowchart LR
    M1[M1: Setup<br/>✅ Week 1] --> M2[M2: Brand<br/>✅ Week 2]
    M2 --> M3[M3: Legal<br/>✅ Week 3]
    M3 --> M4[M4: Website<br/>✅ Week 4]
    M4 --> M5[M5: Backend<br/>✅ Week 5-6]
    M5 --> M6[M6: Frontend<br/>✅ Week 7-8]
    M6 --> M7[M7: Testing<br/>✅ Week 9]
    M7 --> M8[M8: Launch<br/>🔄 Week 10-12]

    style M1 fill:#d4edda
    style M2 fill:#d4edda
    style M3 fill:#d4edda
    style M4 fill:#d4edda
    style M5 fill:#d4edda
    style M6 fill:#d4edda
    style M7 fill:#d4edda
    style M8 fill:#fff3cd
```

| Milestone | Deliverables | Status |
|-----------|--------------|--------|
| **M1: Setup Complete** | Repo, project board | ✅ Complete |
| **M2: Brand Ready** | Logo, color palette, typography, guidelines | ✅ Complete |
| **M3: Legal Ready** | ToS, Privacy, SLA, DPA (AI-drafted) | ✅ Complete |
| **M4: Website Ready** | Marketing site content (6 pages) | ✅ Complete |
| **M5: Backend Complete** | Multi-tenant (41 modules), billing (11 modules), memory (6 modules) | ✅ Complete |
| **M6: Frontend Complete** | Chat API, widget, Shopify extension, admin (2 shells), prototype approved | ✅ Complete |
| **M7: Testing Complete** | 1,974 tests (P0-P3 + security + perf + 42 integration + 43 regression + 85 scanner), CI pipeline | ✅ Complete |
| **M8: Production Deployment** | Azure deployment, storefront setup, UX evaluation | 🔄 In Progress |
| **M9: GA Launch** | App Store listed, first trial signup, 48hr stability | 📋 Pending |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial project plan |
| 1.1.0 | 2026-01-29 | Phase 0 complete |
| 1.2.0 | 2026-01-29 | Docker dev environment, AGNTCY baseline verified |
| 1.3.0 | 2026-01-29 | Work priority review complete |
| 1.4.0 | 2026-01-29 | Phase 1.1 + 1.2 complete |
| 1.5.0 | 2026-01-29 | Phase 1.3 website content complete |
| 1.6.0 | 2026-01-29 | Phase 1.4 documentation complete |
| 1.7.0 | 2026-01-30 | Phase 2.1 platform decision, dual-channel |
| 1.8.0 | 2026-01-30 | Phase 2.5 Persistent Customer Memory added |
| 2.0.0 | 2026-02-02 | **Major update:** Phase 2.1-2.2 complete (38 multi_tenant modules, 11 integration modules). Phase 2.5 Layers 1-2 complete. Phase 3.0 ALL BUILD PHASES complete (chat API, widget, admin shells). 999 tests passing. Operational readiness, security hardening, pipeline optimization, trial environment all complete. PROJECT-PLAN restructured to reflect actual phase completion. |
| 3.0.0 | 2026-02-03 | **Launch preparation update:** Phase 2.5 ALL 4 LAYERS COMPLETE (6 modules, 111 tests). Test suite updated: 1,235 unit + 42 integration = 1,277 total, 0 failures. P3, adversarial, performance tests all complete. Cosmos DB 10 containers initialized and verified. Prototype approved by owner (frozen as production reference). Remaker Digital storefront strategy approved (dual-purpose: sales + live demo). UX consultant (Mazel) engaged. New WIs #196-204 added for launch preparation. Phase 6 restructured: Infrastructure, Storefront, App Store, Creative Assets, Launch Readiness. No beta/soft launch — 1.0 is full GA release. |
| 3.1.0 | 2026-02-10 | **KB quality tools:** KB Conflict/Duplication Scanner (WI #239) — `kb_conflict_scanner.py` (~705 lines), 4-phase detection algorithm, 2 API endpoints, admin UI, 85 tests, documentation page. Test suite: 1,889 unit + 42 integration + 43 regression = 1,974 total, 0 failures. Scanner role in ongoing chat quality testing lifecycle documented across memory files and project docs. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
