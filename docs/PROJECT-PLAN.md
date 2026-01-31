# Agent Red Customer Engagement - Launch 1.0 Project Plan

> **Project:** Agent Red Customer Engagement
> **Release:** Launch 1.0
> **Timeline:** Q1 2026 (8-12 weeks)
> **Budget:** $500-1,000/month operational

---

## Executive Summary

Agent Red Customer Engagement is a commercial SaaS product built on the open-source AGNTCY Customer Engagement Platform foundation. Launch 1.0 targets MVP delivery within Q1 2026, focusing on core commercial infrastructure and Phase 1-2 marketing materials.

---

## Project Phases

### Phase 0: Project Setup (Week 1)
**Status:** Complete ✅

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| Create project directory structure | ✅ Done | - | E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement |
| Create CLAUDE.md | ✅ Done | - | AI assistant guidance (v2.0 with full knowledge transfer) |
| Create PROJECT-PLAN.md | ✅ Done | - | This file |
| Create GitHub private repository | ✅ Done | - | github.com/Remaker-Digital/agent-red-customer-engagement |
| AGNTCY dependency model | ✅ Done | - | Arms-length via public GitHub (no submodule) |
| Migrate commercial materials | ✅ Done | - | SaaS proposal, product features, website content |
| Initial commit pushed | ✅ Done | - | 23 files, 5,825 lines |
| Docker dev environment | ✅ Done | - | Dockerfile, docker-compose.yml, requirements.txt |
| AGNTCY baseline verification (local) | ✅ Done | - | 15 containers healthy, 97.8% unit / 99.3% integration pass |
| AGNTCY baseline verification (Azure) | ✅ Done | - | All 53 resources operational, evaluation 94% intent / 100% escalation precision |
| Set up GitHub Project board | ✅ Done | - | [Project #2](https://github.com/orgs/Remaker-Digital/projects/2), 8 milestone issues (M1-M8) |

---

### Phase 1: Foundation (Weeks 2-4)

#### 1.1 Brand Identity *(can start immediately)*
**Direction:** Bold/Corporate — dark reds, navy/charcoal accents, strong sans-serif typography
**Approach:** AI-generated concepts and full brand system drafted in-house

| Task | Effort | Status |
|------|--------|--------|
| Logo concepts (primary, icon, wordmark) | 8 hrs | ✅ Done — "The Beacon" AR monogram approved |
| Color palette selection | 2 hrs | ✅ Done — 15 colors, WCAG AA/AAA verified |
| Typography selection | 2 hrs | ✅ Done — Inter + JetBrains Mono |
| Brand guidelines document | 4 hrs | ✅ Done — branding/guidelines/BRAND-GUIDELINES.md |
| Favicon and app icons | 2 hrs | 📋 Todo — spec defined in LOGO-SPEC.md |

#### 1.2 Legal Documents *(can run parallel with 1.1)*
**Approach:** AI-draft all documents first. Termly/iubenda deferred until closer to launch.

| Task | Effort | Status |
|------|--------|--------|
| Draft Terms of Service | 4 hrs | ✅ Done — legal/terms/TERMS-OF-SERVICE.md |
| Draft Privacy Policy | 2 hrs | ✅ Done — legal/privacy/PRIVACY-POLICY.md |
| Draft SLA document | 4 hrs | ✅ Done — legal/sla/SERVICE-LEVEL-AGREEMENT.md |
| Draft Data Processing Agreement | 2 hrs | ✅ Done — legal/dpa/DATA-PROCESSING-AGREEMENT.md |
| Validate via Termly/iubenda | 2 hrs | 📋 Deferred to pre-launch |

#### 1.3 Website Content *(depends on 1.1 brand identity)*
**Status:** Complete ✅
**Approach:** Full rewrite for commercial buyer audience. Existing AGNTCY content used as technical reference only.
**Platform:** Deferred — content written in markdown, hosting platform chosen later.
**Key Decisions:** Pricing model redesigned from flat-rate ($299/$499/$999) to platform fee + metered AI usage ($149/$399/$999 base + per-conversation overage). All fabricated social proof removed and replaced with verified AGNTCY evaluation metrics.

| Task | Effort | Status |
|------|--------|--------|
| Write homepage (commercial buyer focus) | 4 hrs | ✅ Done — Outcome-driven hero, verified performance metrics, removed fake social proof |
| Write features page | 3 hrs | ✅ Done — Rebranded, 6-category scrollspy layout preserved |
| Write pricing page | 2 hrs | ✅ Done — Complete redesign: base + AI usage model, competitor research, cost modeling |
| Write integrations page | 3 hrs | ✅ Done — Rebranded, Mailchimp/GA moved to add-on pricing ($49/mo) |
| Write about page | 2 hrs | ✅ Done — Honesty pass: removed all fabricated content, added open-source foundation story |
| Write contact page | 2 hrs | ✅ Done — New page: form, channels, partner program teaser, URL parameter support |

#### 1.4 Public Documentation *(can start alongside 1.3)*
**Status:** Complete ✅
**Approach:** Docusaurus scaffold + conceptual guides + quality framework. API-specific docs deferred to Phase 2.
**Key Decisions:** Mermaid diagrams adopted as standard for all technical illustrations (Eraser.io evaluated but deferred to Phase 2.2 for architecture diagrams). Documentation quality CI pipeline established (Vale, markdownlint, link-check, coverage audit). Diataxis framework adopted for content classification. Feature inventory system created for coverage tracking.

| Task | Effort | Status |
|------|--------|--------|
| Set up Docusaurus | 4 hrs | ✅ Done — docs-site/ with Agent Red branding, Mermaid support, strict build mode |
| Documentation quality framework | 6 hrs | ✅ Done — Vale, markdownlint, alex, link-check, coverage audit, CI pipeline, feedback widget |
| Write getting-started guide | 4 hrs | ✅ Done — 3 pages (overview, how-it-works, setup), 14 Mermaid diagrams |
| Write Shopify integration guide | 3 hrs | ✅ Done — OAuth, sync, field mapping, order lookups, troubleshooting, 6 Mermaid diagrams |
| Write API authentication guide | 2 hrs | 📋 Deferred to Phase 2 |
| Document API endpoints | 8 hrs | 📋 Deferred to Phase 2 |

---

### Phase 2: Product & Infrastructure (Weeks 5-8)

#### 2.1 E-Commerce Store
**Platform:** Dual-channel — Shopify App Store (primary distribution) + Stripe (direct sales). Decision documented in `docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md`. Paddle evaluated and rejected (no marketplace, higher fees, redundant with Shopify tax handling).

| Task | Effort | Status |
|------|--------|--------|
| Evaluate Shopify vs Stripe vs Paddle for SaaS subscriptions | 4 hrs | ✅ Done — Three-way evaluation complete, dual-channel recommended and approved |
| Create Stripe account (live + test mode) | 1 hr | ✅ Done — Test mode configured, catalog script created |
| Create Products, Prices, Coupons in Stripe (test mode) | 2 hrs | ✅ Done — 27 Stripe objects (config/stripe_product_ids.json) |
| Implement Stripe Checkout for plan selection | 4 hrs | ✅ Done — src/integrations/stripe_checkout.py |
| Implement Stripe webhook handler (subscription lifecycle) | 8 hrs | ✅ Done — src/integrations/stripe_webhooks.py (7 events) |
| Implement metered usage reporting to Stripe | 4 hrs | ✅ Done — src/integrations/stripe_usage.py (3-tier consumption) |
| Add Shopify Billing API integration to existing Shopify app code | 8 hrs | ✅ Done — src/integrations/shopify_billing.py + shopify_client.py |
| Create Shopify App Store listing (description, screenshots, demo) | 4 hrs | 🔄 In Progress — listing copy drafted (docs/shopify/APP-STORE-LISTING.md), creative assets pending |
| Implement GDPR compliance webhooks (customers/data_request, customers/redact, shop/redact) | 4 hrs | 📋 Todo — Required for Shopify App Store submission |
| Implement session token authentication for embedded Shopify app | 4 hrs | 📋 Todo — Required since 2025, replaces cookie-based auth |
| Implement App Bridge Save Bar API integration | 2 hrs | 📋 Todo — Required for embedded app save functions |
| Submit for Shopify App Store review | 1 hr | 📋 Todo — Blocked by: GDPR webhooks, session tokens, App Bridge Save Bar, creative assets |
| Implement Stripe Customer Portal link | 1 hr | ✅ Done — src/integrations/stripe_portal.py |
| Implement conversation pack purchase flow | 4 hrs | ✅ Done — src/integrations/stripe_packs.py (FIFO, 90-day validity) |
| Build unified webhook handler (both channels → provisioning) | 8 hrs | ✅ Done — src/integrations/provisioning.py (channel-agnostic) |
| Set up Stripe Tax | 2 hrs | ✅ Done — automatic_tax on Checkout, tax_code on Products, tax_behavior on Prices, finalization_failed handler, migration script |
| Set up Rewardful for affiliate program | 4 hrs | ✅ Done — client_reference_id integration, live connection deferred (Rewardful requires live Stripe) |
| Test checkout flows (both channels) | 4 hrs | 📋 Todo |

#### 2.2 Multi-Tenant Infrastructure
**Status:** Tier 1 Critical + Tier 2 High COMPLETE (21 modules, ~9,500 lines). Architecture review: 32 decisions, 100 work items (`docs/Master-Plan-Review-01-30-2026.md`).

| Task | Effort | Status |
|------|--------|--------|
| Architecture review (32 decisions, 100 work items) | 8 hrs | ✅ Done — docs/Master-Plan-Review-01-30-2026.md |
| Cosmos DB schema + TenantScopedRepository (WI #13-14, #24-25) | 16 hrs | ✅ Done — cosmos_schema.py, cosmos_client.py, repository.py |
| Dual auth + middleware (WI #18, #27-28) | 8 hrs | ✅ Done — auth.py, middleware.py |
| Billable conversation spec + ConversationMeter (WI #71-72) | 12 hrs | ✅ Done — conversation_meter.py |
| Fail-closed Critic policy (WI #50) | 8 hrs | ✅ Done — critic_policy.py |
| NATS tenant isolation (WI #15-17, #26) | 8 hrs | ✅ Done — nats_isolation.py |
| GDPR services (WI #30-34, #36) | 12 hrs | ✅ Done — gdpr_services.py |
| OpenTelemetry tracing (WI #39-41) | 8 hrs | ✅ Done — otel_tracing.py |
| Pipeline resilience (WI #44-46) | 8 hrs | ✅ Done — pipeline_resilience.py |
| SystemPromptBuilder (WI #70) | 8 hrs | ✅ Done — system_prompt_builder.py |
| Usage Dashboard API (WI #73-74) | 6 hrs | ✅ Done — usage_dashboard_api.py |
| Tenant config schema/processor/API (WI #63-65) | 12 hrs | ✅ Done — tenant_config_schema.py, tenant_config_processor.py, tenant_config_api.py |
| TenantSecretService (WI #29) | 4 hrs | ✅ Done — tenant_secret_service.py |
| DR + security Terraform (WI #52, #55, #58-59) | 4 hrs | ✅ Done — dr_security.tf |
| Billing doc + SLA updates (WI #77-78) | 4 hrs | ✅ Done — billable-conversation-spec.md, SLA v0.2.0 |
| TenantUsageMonitor — progressive throttling (WI #51) | 8 hrs | 📋 Todo |
| KEDA auto-scaling deployment (WI #47-48) | 8 hrs | 📋 Todo |

#### 2.5 Persistent Customer Memory *(depends on 2.2 multi-tenant infrastructure)*
**Status:** Layers 1-2 COMPLETE (3 modules + 30 passing tests). Architecture research complete. Metrics framework defined.

| Task | Effort | Status |
|------|--------|--------|
| CustomerProfileService — Layer 1 (WI #83-85) | 16 hrs | ✅ Done — customer_profile_service.py |
| ConversationVectorizer — Layer 2 (WI #87-88) | 40 hrs | ✅ Done — conversation_vectorizer.py |
| Response explainability framework (WI #86) | 8 hrs | ✅ Done — response_explainability.py |
| Test fixtures + 20 unit tests + 10 integration tests (WI #97-98, #100) | 16 hrs | ✅ Done — tests/persistent_memory/ (30 tests passing) |
| PatternExtractionService — Layer 3 (WI #90-92) | 60 hrs | 📋 Todo — Professional+ |
| Fine-tuning pipeline — Layer 4 (WI #93-96) | 60 hrs | 📋 Todo — Enterprise add-on |
| 5 A/B production tests (WI #99) | 16 hrs | 📋 Todo |
| Create metrics dashboard | 40 hrs | 📋 Todo |

#### 2.3 Admin Guides *(deferred — requires working product)*
| Task | Effort | Status |
|------|--------|--------|
| Initial setup guide | 4 hrs | 📋 Todo |
| Shopify connection guide | 2 hrs | 📋 Todo |
| Knowledge base setup guide | 3 hrs | 📋 Todo |
| Monitoring and alerts guide | 3 hrs | 📋 Todo |

#### 2.4 Demo Videos *(deferred — requires working product)*
| Task | Effort | Status |
|------|--------|--------|
| Platform overview (2-3 min) | 4 hrs | 📋 Todo |
| Quick start tutorial (3-5 min) | 4 hrs | 📋 Todo |

---

### Phase 3: Launch Preparation (Weeks 9-12)

#### 3.1 Testing & QA
| Task | Effort | Status |
|------|--------|--------|
| End-to-end checkout testing | 8 hrs | 📋 Todo |
| Multi-tenant isolation testing | 8 hrs | 📋 Todo |
| Load testing | 8 hrs | 📋 Todo |
| Security review | 8 hrs | 📋 Todo |

#### 3.2 Deployment
| Task | Effort | Status |
|------|--------|--------|
| Set up production environment | 8 hrs | 📋 Todo |
| Configure monitoring | 4 hrs | 📋 Todo |
| Set up alerting | 4 hrs | 📋 Todo |
| Document runbooks | 8 hrs | 📋 Todo |

#### 3.3 Launch Readiness
| Task | Effort | Status |
|------|--------|--------|
| Final website review | 4 hrs | 📋 Todo |
| Final documentation review | 4 hrs | 📋 Todo |
| Soft launch (beta users) | - | 📋 Todo |
| Address beta feedback | 16 hrs | 📋 Todo |
| Public launch | - | 📋 Todo |

---

## Budget Allocation

### Monthly Operational Costs

| Category | Service | Monthly Cost |
|----------|---------|--------------|
| **Infrastructure** | Azure (production) | $300-500 |
| **E-commerce** | Stripe (~3.5% variable) + Shopify App Store ($0 commission < $1M) + Rewardful (~$49-99/mo affiliates) | $49-99 + variable |
| **Legal** | Termly + iubenda (deferred to pre-launch) | $0-52 |
| **Marketing** | Buffer (future) | $0-30 |
| **Documentation** | Docusaurus (Vercel) | $0 |
| **Domain/DNS** | Cloudflare | $0-20 |
| **Total** | | **$371-681** |

### One-Time Costs

| Item | Estimated Cost |
|------|----------------|
| Logo design (if outsourced) | $0-500 |
| Stock imagery | $0-100 |
| **Total** | **$0-600** |

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline slip | High | Medium | MVP scope, prioritize core features |
| Budget overrun | Medium | Low | Aggressive cost monitoring, lean approach |
| Multi-tenant complexity | High | Medium | Start simple, iterate |
| Brand confusion with AGNTCY | Medium | Low | Clear differentiation messaging, full website rewrite |
| E-commerce platform fit | Medium | Medium | Evaluate Shopify vs Stripe before committing |

---

## Success Criteria

### Launch 1.0 Minimum Viable

| Criterion | Target |
|-----------|--------|
| Website live | ✅ Yes |
| Documentation published | ✅ Yes |
| Legal documents published | ✅ Yes |
| Shopify store operational | ✅ Yes |
| First trial signup | ✅ Yes |
| Platform stable for 48 hrs | ✅ Yes |

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
| Shopify App Store | E-commerce (primary distribution) | Low |
| Stripe | E-commerce (direct billing) | Low |
| Rewardful | Affiliate program | Low |
| Termly/iubenda services | Legal | Low |

### Internal Dependencies

| Item | Depends On |
|------|------------|
| Website launch | Brand identity, content |
| E-commerce store | Pricing finalized, products defined, platform decision ✅ (Shopify App Store + Stripe) |
| Multi-tenant infra | Architecture design document approved |
| Persistent Customer Memory | Multi-tenant infrastructure (tenant-partitioned data) |
| API documentation | Multi-tenant infrastructure built, API surface defined |
| Conceptual docs | Product features known (can start Phase 1) |
| Admin guides | Working product to document |
| Demo videos | Working product to demonstrate |

---

## Team & Responsibilities

| Role | Responsibilities |
|------|------------------|
| Product Owner | Scope decisions, prioritization, acceptance |
| Technical Lead | Architecture, code review, technical decisions |
| Developer | Implementation, testing, deployment |
| Content | Website copy, documentation, guides |
| Design | Brand identity, UI/UX (if applicable) |

---

## Communication

### Status Updates

| Meeting | Frequency | Purpose |
|---------|-----------|---------|
| Sprint planning | Weekly | Plan next week's work |
| Standup | Daily | Progress, blockers |
| Demo | Bi-weekly | Show completed work |
| Retrospective | Bi-weekly | Process improvement |

### Documentation

| Document | Update Frequency |
|----------|------------------|
| PROJECT-PLAN.md | Weekly |
| CLAUDE.md | As needed |
| GitHub Issues | Daily |
| Project Board | Daily |

---

## Milestones

| Milestone | Target Date | Deliverables |
|-----------|-------------|--------------|
| **M1: Setup Complete** | Week 1 | Repo, project board ✅ |
| **M2: Brand Ready** | Week 3 | Logo concepts, color palette, typography, brand guidelines |
| **M3: Legal Ready** | Week 4 | AI-drafted ToS, Privacy, SLA, DPA (Termly/iubenda deferred) |
| **M4: Website Live** | Week 5 | Marketing site deployed |
| **M5: Store Live** | Week 7 | E-commerce store operational (platform TBD) |
| **M6: Docs Complete** | Week 8 | Documentation published |
| **M7: Soft Launch** | Week 10 | Beta users invited |
| **M8: Public Launch** | Week 12 | General availability |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial project plan |
| 1.1.0 | 2026-01-29 | Phase 0 complete: GitHub repo created, initial commit pushed, arms-length dependency model established |
| 1.2.0 | 2026-01-29 | Docker dev environment added, AGNTCY baseline verified (local Docker + production Azure) |
| 1.3.0 | 2026-01-29 | Work priority review complete: brand direction (Bold/Corporate), legal approach (AI-draft first), website (full rewrite), docs (conceptual now, API later), e-commerce platform deferred, multi-tenant architecture doc required, admin guides/videos deferred |
| 1.4.0 | 2026-01-29 | Phase 1.1 Brand Identity complete (logo, colors, typography, guidelines). Phase 1.2 Legal Documents complete (ToS, Privacy Policy, SLA, DPA — all AI-drafted, pending legal review) |
| 1.5.0 | 2026-01-29 | Phase 1.3 Website Content complete — 6 pages rewritten for Agent Red commercial brand. Major pricing model redesign: flat-rate → platform fee + metered AI usage ($149/$399/$999 base, included conversations, tiered overage). Honesty pass removed all fabricated social proof. New contact page added. Content principles established: honesty, accuracy, correctness. |
| 1.6.0 | 2026-01-29 | Phase 1.4 Public Documentation complete — Docusaurus site scaffolded with Agent Red branding and Mermaid diagram support. Documentation quality framework added: Vale prose linting (Google style + custom Agent Red rules), markdownlint, alex (inclusivity), markdown-link-check, coverage audit system (Diataxis-based feature inventory). GitHub Actions CI pipeline for docs quality. 5 content pages written: Platform Overview, How It Works, Initial Setup, Shopify Integration, Welcome. 20 Mermaid diagrams total. Coverage: 26% actionable slots documented (52% explanation, 21% how-to). "Was this helpful?" feedback widget added. Eraser.io evaluated, deferred to Phase 2.2. |
| 1.7.0 | 2026-01-30 | Phase 2.1 platform decision complete — Three-way evaluation (Stripe vs Shopify App Store vs Paddle) documented in `docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md`. Decision: Dual-channel (Shopify App Store as primary distribution + Stripe for direct sales). Paddle rejected (no marketplace, higher fees, redundant tax handling). Phase 2.1 task list updated with 15 implementation tasks (~75 hrs). Strategic alignment confirmed: Shopify App Store provides established competitor ecosystem for price disruption strategy. |
| 1.8.0 | 2026-01-30 | Persistent Customer Memory added as 5th commercial differentiator. Phase 2.5 added with 9 implementation tasks (~344 hrs). Metrics framework and test cases documented in `docs/architecture/PERSISTENT-CUSTOMER-MEMORY-METRICS.md`. Research foundation in `docs/architecture/PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md`. Feature propagated across all 18 project files (business docs, marketing, docs-site, legal, brand). Dedicated Model Training add-on added ($299/mo, Enterprise only). |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
