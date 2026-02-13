# CLAUDE.md - Agent Red Customer Experience

This document provides context and guidance for AI assistants working on the Agent Red Customer Experience commercial project.

> **📁 Historical Archive:** Session-by-session development logs, detailed technical decisions, completed phase checklists, AGNTCY architecture patterns, and infrastructure provisioning details have been moved to `CLAUDE_ARCHIVE.md` to reduce context window usage. Consult the archive when investigating historical decisions or implementation details.
>
> **📁 Session Memory:** Operational patterns, lessons learned, and quick-reference data are maintained in the Claude Code memory files at `~/.claude/projects/.../memory/` — see `MEMORY.md` for the index.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Experience |
| **Brand Name** | Agent Red Customer Experience |
| **Release** | Launch 1.0 |
| **Type** | Commercial SaaS Product |
| **Status** | Save→Activate architecture COMPLETE — production v1.22.0, session 11 UI polish + tooltip audit NOT YET DEPLOYED (v1.23.0). 2,301 tests (0 failures), chat quality 12/12, admin UI 86/86. P0: deploy v1.23.0, then creative assets (owner/designer) for Shopify App Store submission. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |

---

## Legal & IP

| Attribute | Value |
|-----------|-------|
| **Legal Entity** | VanDusen & Palmeter, LLC |
| **DBA** | Remaker Digital |
| **Jurisdiction** | Delaware, USA |
| **Entity Type** | Limited Liability Company (LLC) |
| **Website** | https://remakerdigital.com |

### Copyright Notice

All new work in this repository must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

### IP Separation Rules

Agent Red is an independent commercial product. Its relationship to the AGNTCY open-source project is strictly arms-length, identical to how any third-party commercial product would consume a public GitHub project.

| Content Type | Location | License |
|--------------|----------|---------|
| AGNTCY core platform | Public GitHub (third-party) | Open Source |
| Multi-tenant infrastructure | Agent Red (this repo) | Proprietary |
| Commercial integrations | Agent Red (this repo) | Proprietary |
| White-label features | Agent Red (this repo) | Proprietary |
| Advanced AI features | Agent Red (this repo) | Proprietary |
| Marketing materials | Agent Red (this repo) | Proprietary |
| Legal documents | Agent Red (this repo) | Proprietary |
| Brand assets | Agent Red (this repo) | Proprietary |

**Rule:** Agent Red has no privileged access to AGNTCY. It consumes only publicly available artifacts (published releases, public GitHub content, public documentation). There are no cross-project file references, no shared state, and no assumed coordination.

---

## Upstream Dependency: AGNTCY Customer Engagement Platform

### Relationship

Agent Red consumes the AGNTCY open-source project as any external third party would. The AGNTCY project is maintained independently at:

- **Repository:** https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- **Visibility:** Public
- **License:** Open Source
- **SDK Package:** `agntcy-app-sdk` (PyPI)

### What AGNTCY Provides

AGNTCY is a multi-agent AI customer service platform built on the AGNTCY SDK. Agent Red builds commercial capabilities on top of this open-source foundation. Six specialized AI agents: Intent Classification (GPT-4o-mini), Knowledge Retrieval (text-embedding-3-large), Response Generation (GPT-4o), Escalation (GPT-4o-mini), Analytics (GPT-4o-mini), Critic/Supervisor (GPT-4o-mini).

**Note:** Agent Red bypasses AGNTCY agent containers (`USE_AGENT_CONTAINERS=false`) and calls Azure OpenAI directly via the API Gateway pipeline. AGNTCY containers show ActivationFailed — this is expected (demo mode images).

### How Agent Red Consumes AGNTCY

Agent Red integrates with AGNTCY through these public interfaces:

1. **SDK Package:** `pip install agntcy-app-sdk` for agent development patterns
2. **Docker Images:** Build from AGNTCY's public Dockerfiles or reference patterns
3. **Terraform Patterns:** Reference AGNTCY's published IaC for Azure deployment
4. **Architecture Patterns:** Factory singleton, BaseAgent, PII tokenization, connection pooling
5. **Evaluation Data:** Prompt templates and evaluation methodology from public repo

Agent Red does **not**:
- Reference AGNTCY files by local path
- Depend on AGNTCY's uncommitted state
- Require coordination for releases

### Local Development Isolation Rules

**IMPORTANT:** The AGNTCY open-source project and Agent Red may both be active on this desktop simultaneously. They must be strictly isolated:

| Rule | Detail |
|------|--------|
| **No local file sharing** | Agent Red must never read, reference, or depend on any local AGNTCY files. No local path references between projects. |
| **No shared Docker containers** | Agent Red must not interact with, inspect, start, stop, or depend on any Docker containers belonging to the AGNTCY project. Each project manages its own containers independently. |
| **No shared local artifacts** | No shared virtual environments, no shared build artifacts, no shared volumes, no shared databases or message queues. |
| **GitHub only** | When Agent Red needs AGNTCY code, documentation, patterns, or artifacts, it must obtain them exclusively via the AGNTCY GitHub repository (repo, project board, wiki, releases, issues, PRs). |
| **SDK via PyPI** | Agent Red consumes `agntcy-app-sdk` via `pip install` from PyPI, not from a local clone. |
| **Docker images via registry** | Agent Red builds its own Docker images or pulls published images from a registry. It does not reference or reuse AGNTCY's local Docker images. |

If AGNTCY Docker containers are running on this machine, Agent Red must behave as if they do not exist. Agent Red treats AGNTCY as a remote third-party project at all times.

### Contributing Changes Back to AGNTCY

If Agent Red development reveals a bug fix or enhancement needed in the AGNTCY core:

1. Propose via GitHub Issue or Pull Request on the public AGNTCY repo
2. Wait for the change to be reviewed, merged, and published
3. Consume the published change through AGNTCY's public GitHub

There is no shortcut. All interaction between projects occurs through AGNTCY's public GitHub.

### Production Infrastructure (Summary)

> **Detailed tables:** Container Apps, RBAC assignments, Terraform state, env vars, Key Vault secrets, and Azure admin notes are in `CLAUDE_ARCHIVE.md` § "Production Infrastructure Ownership". Operational patterns are in `memory/deployment.md`.

| Resource | Name | Key Detail |
|----------|------|------------|
| Resource Group | agentred-prod-rg | East US 2, 17 resources |
| Azure OpenAI | aoai-agentred-eastus2 | S0, 3 deployments (gpt-4o, gpt-4o-mini, text-embedding-3-large) |
| Cosmos DB | cosmos-agentred-eastus2 | Serverless, NoSQL Vector Search, DiskANN, 10 containers |
| Key Vault | kv-agentred-eastus2 | RBAC-enabled |
| Container Registry | acragentredeastus2 | 9 repositories |
| Container App Env | agent-red-cae | Domain: `lemonriver-f59f94b7.eastus2.azurecontainerapps.io` |
| API Gateway | agent-red-api-gateway | v1.20.1 (deployed), FQDN: `agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io` |
| NATS | agent-red-nats | Internal: `agent-red-nats.internal.lemonriver-f59f94b7.eastus2.azurecontainerapps.io:4222` |

**9 Container Apps deployed.** 27 RBAC assignments (9 AcrPull + 9 KV + 9 Cosmos DB). Terraform state clean. NATS connected=false (lazy init — expected).

**Third-Party Service Accounts:** Azure OpenAI (pay-per-token), Shopify Partner (developer), Zendesk (sandbox), Mailchimp (free tier), Google Analytics (GA4).

---

## Commercial Differentiators

These features are **exclusive to Agent Red** (not in open-source):

### 1. Multi-Tenant SaaS Infrastructure
- Tenant isolation and data segregation
- Subscription management and billing
- Usage metering and quota enforcement
- Self-service customer portal
- API key management

### 2. Advanced AI Features
- Premium model access (GPT-4o, Claude)
- Fine-tuned models for specific industries
- Advanced analytics and insights
- Custom model training pipelines
- A/B testing framework

### 3. Enterprise Integrations
- Salesforce CRM
- SAP ERP
- ServiceNow
- Custom connector framework
- Enterprise SSO (SAML, OIDC)

### 4. White-Label & Customization
- Complete branding removal
- Custom domains
- CSS theming engine
- Co-branding options
- Reseller/agency portal

### 5. Persistent Customer Memory
Four-layer personalization stack — every conversation builds on the last:
- **Customer Context (All tiers):** Structured profile (preferences, account state, integration data) injected into every interaction
- **Conversation Memory (All tiers):** Vectorized transcripts enable semantic search across a customer's full interaction history via Cosmos DB vector search
- **Cross-Session Learning (Professional+):** Memory framework extracts and persists patterns, preferences, and communication style across sessions
- **Dedicated Model Training (Enterprise add-on, $299/mo):** Per-customer AI fine-tuning on 1,000+ historical interactions for maximum personalization

No competitor has confirmed implementing per-customer vector RAG over historical transcripts. Marginal cost: ~$0.01/customer/month for Layers 1-2.

---

## Pricing Structure

### Model: Platform Fee + Metered AI Usage

Each tier includes a platform fee (infrastructure, features, support) and an included monthly conversation allowance. Conversations beyond the included allowance are billed at tiered overage rates. This model separates fixed infrastructure costs (shared across tenants) from variable AI costs (per-conversation).

### Tiers

| Tier | Monthly | Annual (17% off) | Included Conv/mo | Overage Rate |
|------|---------|-------------------|------------------|--------------|
| **Starter** | $149 | $124/mo ($1,490/yr) | 1,000 | $0.04/conv |
| **Professional** | $399 | $332/mo ($3,990/yr) | 5,000 | $0.025/conv |
| **Enterprise** | $999 | $832/mo ($9,990/yr) | 20,000 | $0.015/conv |

### Conversation Packs (pre-purchase, 90-day validity)

| Pack | Price | Effective Rate |
|------|-------|----------------|
| 1,000 conversations | $29 | $0.029/conv |
| 5,000 conversations | $99 | $0.020/conv |
| 20,000 conversations | $249 | $0.012/conv |

### Add-On Modules

| Module | Monthly | Available On |
|--------|---------|--------------|
| Multi-Language Pack | $99 | All |
| Advanced Analytics | $149 | Pro, Enterprise |
| Mailchimp Integration | $49 | Pro, Enterprise |
| Google Analytics Integration | $49 | Pro, Enterprise |
| White-Label Package | $399 | Enterprise only |
| Priority Support Upgrade | $99 | Starter, Pro |
| Custom Integration Dev | $299 | Enterprise only |
| Dedicated Model Training | $299 | Enterprise only |

### Cost Basis & Margin

**Per-conversation AI cost:** ~$0.0073 (GPT-4o response generation = 94.5% of total, plus Cosmos DB RU + archival)

**Infrastructure costs (shared, multi-tenant, post-architecture review):**
- Shared platform (Container Apps Option B+, Cosmos DB, App Gateway, etc.): ~$252-436/mo total
- Per-tenant marginal cost at 10+ tenants: ~$13-41/mo

**Gross margin at list price:** 76-90% across all scenarios (base fee + overage, validated Jan 2026 architecture review)

**Pricing design principles:**
- Transparent usage pricing as competitive advantage
- Start granular (add-ons), bundle later — never change list prices
- 50% below nearest comparable competitor (Gorgias, Tidio Pro)
- Higher affiliate payouts ($30-37/mo recurring) justify creator content investment
- Pricing stability for affiliate/promoter confidence

---

## Launch 1.0 Scope

### Timeline
- **Target:** Q1 2026 (8-12 weeks)
- **Approach:** MVP focus, aggressive timeline

### Budget
- **Monthly Operations:** $500-1,000
- **Strategy:** Lean startup, bootstrap, aggressive optimization

### Out-of-Scope for Launch 1.0

- Developer community setup
- Technical presentations
- Social media automation
- Compliance certifications (SOC 2, ISO)
- License management system
- ~~Affiliate program~~ (Rewardful integration built, deferred live connection to launch)

---

## Development Environment

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 11 |
| **IDE** | Visual Studio Code |
| **Container Platform** | Docker Desktop for Windows |
| **Version Control** | Git + GitHub Desktop |
| **Python Version** | 3.12+ |
| **Primary Language** | US English |

---

## GitHub Configuration

| Attribute | Value |
|-----------|-------|
| **Account** | mike-remakerdigital |
| **Repository** | [agent-red](https://github.com/mike-remakerdigital/agent-red) |
| **Plan** | Professional |
| **Branch Protection** | main (require PR, require reviews) |
| **Project Board** | TBD — create on new repo |

**Association Rule:** The repository `mike-remakerdigital/agent-red` is the canonical home for this project. All issues, tracking, and project management for this repository use that repo exclusively.

---

## CI/CD Strategy

### Hybrid Approach

| Stage | Platform | Purpose |
|-------|----------|---------|
| Development | GitHub Actions | PR validation, unit tests, linting |
| Staging | Azure DevOps | Integration tests, staging deployment |
| Production | Azure DevOps | Production deployment, monitoring |

---

## Brand Requirements

### Status
**Core brand system complete** (Phase 1.1). Brand primary color: `#ff3621`.

### Required Assets
- [x] Logo (primary, icon, wordmark) — `{r}` curly brace design with `#ff3621`
- [x] Color palette — 15 colors, WCAG AA/AAA verified
- [x] Typography selection — Inter + JetBrains Mono
- [x] Brand guidelines document — branding/guidelines/BRAND-GUIDELINES.md
- [x] Favicon and app icons — generated from new `{r}` icon-master
- [ ] Social media assets
- [ ] Email templates

### Brand Name Usage
- **Full:** Agent Red Customer Experience
- **Short:** Agent Red
- **Product Line:** Agent Red (parent) → Customer Experience (product)

### Admin UI Design Reference
- **Prototype:** `cd prototype && npm run dev` (port 3000) — Owner-approved, designer-refined, frozen
- **Dark mode palette:** chrome `#0a0a0a` → page `#141414` → surface `#1f1f1f` → border `#272727`
- **Frameworks:** Mantine v7 (standalone admin) + Polaris 12 (Shopify admin)
- **Documentation site:** https://agentredcx.com (GitHub Pages + Docusaurus)

---

## Project Structure

```
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\
│
├── CLAUDE.md                       # This file - AI assistant guidance
├── CLAUDE_ARCHIVE.md               # Historical session logs and detailed technical decisions
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env.local                      # Local credentials (git-ignored): Stripe, Shopify, env vars
├── package.json                    # Root package.json for Shopify CLI
├── shopify.app.toml                # Shopify Partner app config (client_id, scopes, GDPR URLs)
│
├── config/                         # Configuration files
│   └── stripe_product_ids.json     # Stripe test-mode product/price IDs (27 objects)
│
├── src/                            # Commercial source code
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entrypoint (21 routers, 79 routes, 9 middleware, ~1,000 lines)
│   ├── integrations/               # Billing & platform integrations
│   │   ├── __init__.py
│   │   ├── provisioning.py         # Channel-agnostic tenant provisioning service
│   │   ├── stripe_catalog.py       # Typed Pydantic models for Stripe product catalog
│   │   ├── stripe_checkout.py      # Stripe Checkout session management + Rewardful referral
│   │   ├── stripe_packs.py         # Conversation pack purchase & FIFO balance tracking
│   │   ├── stripe_portal.py        # Stripe Customer Portal session management
│   │   ├── stripe_usage.py         # Metered usage reporting (3-tier: included→packs→overage)
│   │   ├── stripe_webhooks.py      # Stripe webhook handler (7 events → provisioning + tax)
│   │   ├── shopify_client.py       # Async Shopify GraphQL API client (httpx)
│   │   ├── shopify_billing.py      # Shopify Billing API (subscriptions + usage charges)
│   │   └── shopify_gdpr_webhooks.py # Shopify GDPR mandatory webhooks (3 endpoints, HMAC verification)
│   ├── multi_tenant/               # Multi-tenant infrastructure (47 modules, ~38,000 lines)
│   │   ├── __init__.py             # Package init with import hints
│   │   ├── cosmos_schema.py        # 9 collections, 12 document models, 8 enums, tier defaults (incl. trial)
│   │   ├── cosmos_client.py        # CosmosManager singleton (lazy init, Managed Identity, health)
│   │   ├── repository.py           # TenantScopedRepository + 10 collection repositories
│   │   ├── auth.py                 # Triple auth: Shopify JWT + API key + publishable widget key
│   │   ├── middleware.py           # TenantAuthMiddleware + RateLimitMiddleware (with headers) + dependencies
│   │   ├── conversation_meter.py   # ConversationMeter: billable conv spec, 3-tier metering, alerts
│   │   ├── critic_policy.py        # Fail-closed Critic enforcement, circuit breaker, health
│   │   ├── nats_isolation.py       # NATS tenant isolation, topic namespace, subscription auth
│   │   ├── gdpr_services.py        # PII scrubbing, data export/deletion, consent management
│   │   ├── otel_tracing.py         # OpenTelemetry tenant tracing, correlation ID propagation
│   │   ├── pipeline_resilience.py  # Per-tenant concurrency, timeout budgets, circuit breakers
│   │   ├── system_prompt_builder.py # Dynamic per-agent prompt assembly (4-layer)
│   │   ├── usage_dashboard_api.py  # Billing transparency REST API (Decision #25)
│   │   ├── tenant_config_schema.py # Tenant config validation, onboarding model
│   │   ├── tenant_config_processor.py # Config merge: platform → tier → tenant overrides
│   │   ├── tenant_config_api.py    # Config REST API (12+ endpoints, /api/config)
│   │   ├── tenant_secret_service.py # Key Vault per-tenant secret management
│   │   ├── customer_profile_service.py # Layer 1 customer profile CRUD, Shopify sync
│   │   ├── conversation_vectorizer.py # Layer 2 vectorization pipeline, semantic search
│   │   ├── response_explainability.py # Per-response decision trace, explainability framework
│   │   ├── admin_conversation_api.py # Conversation inbox admin API (5 endpoints)
│   │   ├── admin_knowledge_api.py  # Knowledge base CRUD + upload + scan admin API (13 endpoints)
│   │   ├── admin_analytics_api.py  # Analytics summary/intents/gaps admin API (3 endpoints)
│   │   ├── admin_team_api.py       # Team member management admin API (5 endpoints)
│   │   ├── admin_gdpr_api.py       # GDPR data export/deletion/consent admin API (5 endpoints)
│   │   ├── admin_audit_api.py      # Audit log query + CSV export admin API (2 endpoints)
│   │   ├── tenant_usage_monitor.py # Progressive throttling (Watch→Warn→Throttle→Isolate)
│   │   ├── security_middleware.py  # Body size limit, JSON depth, security headers, SLA latency recording
│   │   ├── api_versioning.py       # API version headers middleware (X-API-Version)
│   │   ├── structured_logging.py   # JSON structured logging (prod) + colored dev formatter
│   │   ├── activation_service.py   # Save→Activate two-phase commit: draft, activate, restore (~757 lines)
│   │   ├── trial_management.py     # Trial tier lifecycle, expiry, conversion, demo data (~1,200 lines)
│   │   ├── security_hardening.py   # Input sanitization, CORS, CSP, session validation (~570 lines)
│   │   ├── data_retention.py       # Tier-based data retention enforcement (~380 lines)
│   │   ├── sla_monitoring.py       # P50/P95/P99 latency tracking, uptime, compliance (~390 lines)
│   │   ├── cost_model.py           # Parameterized cost model calculator, projections (~370 lines)
│   │   ├── archival_pipeline.py    # Hot→Warm Parquet archival to Azure Blob Storage (~750 lines)
│   │   ├── alert_delivery.py       # Multi-channel alert routing: webhook, dashboard, email, log (~695 lines)
│   │   ├── pattern_extraction.py   # Layer 3 cross-session learning, pattern decay (~1,060 lines)
│   │   ├── fine_tuning_pipeline.py # Layer 4 fine-tuning pipeline, quality gates, A/B (~1,870 lines)
│   │   ├── admin_customer_profile_api.py # Customer profile admin API (~450 lines)
│   │   ├── admin_apikey_api.py     # API key management: generate, rotate, revoke, reset (~350 lines)
│   │   ├── knowledge_vectorizer.py # KB embedding pipeline, hybrid search (BM25+vector+RRF) (~520 lines)
│   │   ├── document_parser.py     # Document upload parsing: PDF, DOCX, CSV, TXT, HTML (~480 lines)
│   │   ├── staleness_service.py   # KB entry staleness detection + scoring (~540 lines)
│   │   ├── semantic_cache.py      # 3-tier semantic cache: embedding, search, response (~530 lines)
│   │   └── kb_conflict_scanner.py # KB conflict/duplication scanner: 4-phase detection (~705 lines)
│   ├── chat/                       # Chat API
│   │   ├── __init__.py
│   │   ├── models.py              # Request/response Pydantic models + StreamEvent SSE format (~200 lines)
│   │   ├── session.py             # Conversation lifecycle management (~350 lines)
│   │   ├── pipeline.py            # 6-agent pipeline orchestrator + SSE streaming (~800 lines)
│   │   ├── endpoints.py           # 6 FastAPI routes: conversations, message, stream, end, WS (~350 lines)
│   │   └── sse_manager.py         # SSE connection manager: heartbeat, reconnection, tenant limits (~280 lines)
│   ├── jobs/                       # Scheduled job entry points (Azure Container App Jobs)
│   │   ├── __init__.py
│   │   ├── run_retention.py        # Cron entry: data retention enforcement (03:00 UTC daily)
│   │   └── run_archival.py         # Cron entry: archival pipeline (04:00 UTC daily)
│   ├── ai-features/                # Advanced AI (Phase 2.5)
│   └── white-label/                # Customization (future)
│
├── tests/                          # Test suites (2,031 unit + 42 integration + 73 regression = 2,301 total, 0 failures)
│   ├── conftest.py                 # Shared fixtures: TestClient, MockCosmos, MockNATS, MockKV, auth helpers
│   ├── test_conftest_smoke.py      # Fixture smoke tests
│   ├── test_health.py              # Health/ready endpoint tests
│   ├── persistent_memory/          # Persistent Customer Memory tests
│   ├── multi_tenant/               # Multi-tenant infrastructure tests
│   ├── integrations/               # Billing integration tests
│   ├── security/                   # Adversarial/security tests
│   ├── performance/                # Performance/load tests + Locust config
│   ├── chat/                       # SSE/streaming tests
│   ├── regression/                 # 43 regression tests (3-tier upgrade validation)
│   └── integration/                # Azure service integration tests
│
├── widget/                         # Chat widget frontend (Preact + TypeScript, ~17KB gzip)
├── prototype/                      # Admin dashboard prototype (Mantine + Polaris, owner-approved)
├── extensions/                     # Shopify Theme App Extension
├── admin/                          # Admin dashboard frontends
│   ├── shared/                     # 11 shared components + hooks + types (~6,250 lines, incl. ActivationBanner/Dialog/RestoreDialog)
│   ├── shopify/                    # Shopify embedded admin (Polaris + App Bridge, ~2,700 lines)
│   └── standalone/                 # Standalone admin (API key login, ~2,800 lines)
│
├── infrastructure/terraform/       # IaC for Azure
├── website/content/                # Marketing website content
├── docs/                           # Documentation (architecture, research, operations, shopify, guides, api)
├── docs-site/                      # Docusaurus documentation site (https://agentredcx.com)
├── branding/                       # Brand assets (logo, colors, guidelines)
├── legal/                          # Legal documents (terms, privacy, contracts)
└── scripts/                        # Automation (setup, stripe, build, deploy)
```

---

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| CLAUDE.md | Root | AI assistant guidance (this file) |
| CLAUDE_ARCHIVE.md | Root | Historical session logs and detailed technical decisions |
| README.md | Root | Project overview |
| PROJECT-PLAN.md | docs/ | Launch 1.0 milestones and tasks |
| APP-STORE-LISTING.md | docs/shopify/ | Shopify App Store listing copy, asset specs |
| COMPETITOR-COMPARISON.md | docs/shopify/ | Agent Red vs 5 competitors (pricing verified 2026-02-01) |
| **SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md** | **docs/operations/** | **Canonical checklist** for Shopify App Store submission |
| LAUNCH-CHECKLIST.md | docs/operations/ | 10-step launch process (owner tasks) |
| DEPLOYMENT-RUNBOOK.md | docs/operations/ | Deployment procedure, DR, maintenance |
| UPGRADE-RUNBOOK-1.0-TO-1.1.md | docs/operations/ | Non-disruptive upgrade procedure |
| COMPREHENSIVE-TEST-PLAN.md | docs/ | ~880 enumerated tests (P0-P3 + security + performance) |
| BACKLOG-NEW-WORK-ITEMS.md | docs/ | Work items backlog (WI #101-225) |
| Master-Plan-Review-01-30-2026.md | docs/ | Architecture review: 32 decisions, 100+ work items |

---

## Self-Service Legal Tools

**Plan-of-record:** iubenda (Advanced plan) for automated legal document generation with multi-language support. LegalZoom retained for SLA/DPA reviews and ad-hoc legal questions.

| Document | Tool | Cost |
|----------|------|------|
| Terms of Service | iubenda | Advanced plan |
| Privacy Policy | iubenda | Included |
| Cookie Policy | iubenda | Included |
| Data Processing Agreement | iubenda | Included |
| SLA / DPA Reviews | LegalZoom | Ad-hoc |

**Language priorities:** Spanish (Mexico), French (Canada) near-term. Portuguese (Brazil), UK English medium-term.

---

## Working with This Project

### Starting a New Session

```
Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md, memory/admin-ui.md, docs/operations/SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md
Current status: Production v1.22.0 healthy. Session 11 changes (UI polish + tooltip audit + 4 new doc pages) NOT YET DEPLOYED as v1.23.0. 2,301 tests (0 failures). P0: build and deploy v1.23.0, then owner manual UI functional testing on all pages.
```

### Referencing AGNTCY

When you need information about the AGNTCY open-source foundation:
- Read the public repository at https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- Reference the SDK documentation for `agntcy-app-sdk`
- Do **not** reference local AGNTCY files by path
- Historical AGNTCY architecture patterns are in `CLAUDE_ARCHIVE.md`

### Preferred Way of Working

For planning, prioritization, and multi-step decision-making, use an **iterative review process**:

1. Present one work item (or clarification) at a time with relevant context, options, and a recommendation
2. Pause for the owner's input before proceeding to the next item
3. Incorporate feedback immediately and adjust subsequent items as needed
4. Do not batch multiple decisions into a single prompt

This applies to: work priority reviews, architecture decisions, scope changes, milestone planning, and any situation where multiple choices must be made. The goal is collaborative decision-making with full visibility, not fire-and-forget task lists.

### Option Evaluation Criteria

When evaluating options (architecture, technology, design, implementation approach), prioritize these concerns in order:

1. **Implementation quality:** Can this option be implemented with high efficiency, robustness, reliability, and usability? Favor approaches where confident, complete, production-grade implementation is achievable.
2. **Desirability:** Is this option competitively strong, differentiating, or obviously superior in usability compared to alternatives?
3. **Downstream confidence:** Can documentation, maintenance, and testing for this option be fully accounted for? Avoid options where downstream work is uncertain or likely to be incomplete.

**Avoid vague generalizations** such as "simpler," "harder," "more complex," or "easier" when describing trade-offs. Instead, state specifically what is gained or lost: which protocols, which failure modes, which components, which test coverage implications. Token usage and elapsed time for Claude to perform a task are not meaningful concerns — do not use them as justification for scope reduction or option selection.

### Continuous Improvement Feedback

The owner values active feedback on their communication effectiveness. When processing user messages, Claude should provide brief inline coaching notes when it observes:

- **Terminology inconsistency:** Flag when terms drift (e.g., "task" vs "work item" vs "WI" vs "issue"). Standard terms: "WI #NNN" for numbered work items, "work item" for generic, "task" for ad-hoc session actions, "issue" for GitHub Issues.
- **Bare approvals that could carry steering:** If an approval like "Yes" or "OK" would benefit from a one-sentence clarification of priority or constraint, suggest it.
- **Approve-then-constrain pattern:** If a constraint arrives as a follow-up message immediately after an approval, note that combining them into one message is more efficient.
- **Open-ended questions:** If a question would get a more useful answer with a specified format (table, list, yes/no with evidence), suggest the reframe.
- **Credential exposure:** Flag any credentials, tokens, or secrets pasted into the chat — reference env files instead.
- **Missing structure:** If a multi-part instruction would benefit from bullets or numbers, suggest it.

**Format:** Feedback should appear as a brief parenthetical note (1-2 sentences) at the end of the response, prefixed with "💡 **Feedback:**". It should never interrupt the primary work output. Skip feedback when the message is already clear and well-structured — only flag genuine opportunities, not every message.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.** Technical gap identification, test case creation, testing/results analysis, and implementation of new capabilities should always be prioritized above creative assets, marketing content, and cosmetic work. The rationale: the technical implementation is the foundation for cost estimates, which are in turn the basis for pricing and licensing decisions. Cost estimates and pricing decisions cannot be validated without comprehensive test data from a working implementation.

### Adding Commercial Features

1. Create features in `src/` exclusively
2. Document in `docs/architecture/`
3. Add copyright notice to all new files
4. Test integration patterns independently
5. Never commit AGNTCY source code into this repo

---

## Remaining Work (Priority Order, as of 2026-02-12)

### P0 — Deploy & Validate
1. Build and deploy v1.22.0 (session 8 role model + session 9 Save→Activate + deploy safeguards)
2. Verify /health 200, run Tier 0 regression, verify team members and activation flow

### P1 — Blocking Submission (Owner/Designer Tasks)
3. App icon (1200×1200 JPEG/PNG) — designer
4. Screenshots (3-6 at 1600×900, at least one showing actual app UI) — designer
5. Submission screencast (install → features → billing → uninstall) — owner
6. Remove storefront password on blanco-9939
7. Storefront content refinement (product descriptions, company pages)
8. Lighthouse performance test (must not reduce score by >10 points)

### P2 — Should Fix Before Submission
9. Chrome incognito session token test
10. Plan upgrade/downgrade E2E test
11. Test billing flow (test: true → false)

### P3 — Nice to Have
12. Feature/promotional video for listing
13. UX consultant evaluation (WI #203)

### P4 — Post-Launch
14. Blocked capabilities C1-C16 (42 UI steps)
15. Widget-side config reads (WI #250, #252, #254, #257)
16. Code modularization (OnboardingWizard removed; Configuration.tsx, StandaloneLayout.tsx still large)
17. Customer context pre-computation (#138)
18. Azure OpenAI PTU investigation (#139)
19. Persistent Memory metrics dashboard
20. Zendesk/Mailchimp/GA4 backend API clients

---

## Requirements Summary

| Question | Answer |
|----------|--------|
| AGNTCY relationship | Arms-length, third-party consumer |
| Commercial differentiators | All 5 (multi-tenant, AI, integrations, white-label, persistent customer memory) |
| Timeline | Q1 2026 (8-12 weeks) |
| Budget | $500-1,000/month |
| Pricing | $149/$399/$999 base + metered AI usage (76-90% gross margin) |
| Legal entity | VanDusen & Palmeter, LLC (Delaware) |
| DBA | Remaker Digital |
| GitHub org | Remaker-Digital (private repo) |
| Dev environment | Windows 11, VS Code, Docker, Python 3.12+ |
| Materials scope | Phase 1-2 only (MVP) |
| Brand assets | Core system complete; `{r}` logo with `#ff3621` |
| CI/CD | Hybrid (GitHub Actions + Azure DevOps) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-12*
*Version: 35.0.0*
