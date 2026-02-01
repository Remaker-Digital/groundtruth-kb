# CLAUDE.md - Agent Red Customer Experience

This document provides context and guidance for AI assistants working on the Agent Red Customer Experience commercial project.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Experience |
| **Brand Name** | Agent Red Customer Experience |
| **Release** | Launch 1.0 |
| **Type** | Commercial SaaS Product |
| **Status** | Phase 2.1 E-Commerce ~85% complete. Phase 2.2 COMPLETE — 38 multi_tenant modules (~25,000 lines). Phase 2.5 Layers 1-2 COMPLETE (3 modules). All middleware wired in main.py (8 middleware layers). **777 tests passing, 0 warnings.** P0 + P1 tests COMPLETE. Test infrastructure complete (WI #101-104). Architecture review complete (32 decisions, 100+ work items). **Phase 3.0 UI/UX: ALL BUILD PHASES COMPLETE — Chat API (6 endpoints + SSE manager), Admin APIs (5 routers, 25 endpoints), Widget frontend (20 files, ~3,200 lines), Shopify Theme App Extension (3 files), Admin shared components (9 + 2 util modules, ~5,400 lines), Shopify admin shell (8 files, ~2,700 lines), Standalone admin shell (9 files, ~2,800 lines).** Operational readiness COMPLETE (WI #148-156). Security hardening COMPLETE (WI #157-163). Pipeline optimization COMPLETE (WI #134-139). Trial environment COMPLETE (WI #119-128). **Competitive pricing VERIFIED (all 5 competitors, 2026-02-01) — Agent Red 4-21x cheaper.** Product renamed Customer Experience. Brand primary #C41E2A. |
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

AGNTCY is a multi-agent AI customer service platform built on the AGNTCY SDK. Agent Red builds commercial capabilities on top of this open-source foundation. Key capabilities provided by AGNTCY:

**Six Specialized AI Agents:**

| Agent | Purpose | Model | Key Metric |
|-------|---------|-------|------------|
| Intent Classification | Route customer queries (17 intents) | GPT-4o-mini | 98% accuracy |
| Knowledge Retrieval | Search products, FAQs, policies | text-embedding-3-large | 100% retrieval@1 |
| Response Generation | Craft personalized responses | GPT-4o | 88.4% quality |
| Escalation | Detect cases needing humans | GPT-4o-mini | 100% precision/recall |
| Analytics | Monitor performance metrics | GPT-4o-mini | Batch processing |
| Critic/Supervisor | Validate content safety | GPT-4o-mini | 0% FP, 100% TP |

**Technology Stack:**
- AGNTCY SDK (`agntcy-app-sdk` on PyPI, requires Python 3.12+)
- SLIM transport (gRPC + TLS, secure agent communication)
- NATS JetStream (event bus, 7-day retention)
- A2A protocol (agent-to-agent communication)
- MCP protocol (external tool integrations)

**Azure Infrastructure Patterns:**
- Azure Container Apps with KEDA auto-scaling
- Cosmos DB Serverless (real-time + vector search)
- Azure OpenAI Service (GPT-4o, GPT-4o-mini, text-embedding-3-large)
- Application Insights (7-day retention, OpenTelemetry)
- Key Vault (secrets management, Managed Identity)
- Application Gateway (TLS termination, WAF)

**Proven Performance (from AGNTCY Phase 3-5 evaluation):**

| Metric | Result | Notes |
|--------|--------|-------|
| Response latency P95 | < 2 seconds | Under load |
| Throughput | 3,071 req/s | 100 concurrent users |
| Daily capacity | 10,000 users | With auto-scaling |
| Uptime SLA | 99.95% | Azure infrastructure |
| Test coverage | 85% (1,351 tests) | 95%+ on security code |
| Budget | ~$214-285/month | Within $310-360 limit |

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

### Production Infrastructure Ownership

Agent Red owns the production Azure deployment and all associated credentials. The following accounts, subscriptions, and deployed resources belong to Agent Red:

**Azure Subscription & Resources:**

| Resource | Name | Region |
|----------|------|--------|
| Resource Group | agntcy-prod-rg | East US 2 |
| Container Registry | acragntcycsprodrc6vcp.azurecr.io | East US 2 |
| Cosmos DB | cosmos-agntcy-cs-prod-rc6vcp (Serverless) | East US 2 |
| Key Vault | kv-agntcy-cs-prod-rc6vcp | East US 2 |
| Application Insights | agntcy-cs-prod-appinsights-rc6vcp | East US 2 |
| App Configuration | agntcy-cs-prod-config | East US 2 |
| Application Gateway | agntcy-cs-prod-appgw (Public IP: 20.110.214.55) | East US 2 |
| Virtual Network | agntcy-cs-prod-vnet (10.0.0.0/16) | East US 2 |

**Deployed Containers (all running, 0 restarts):**

| Container | Private IP | Port | Image |
|-----------|------------|------|-------|
| SLIM Gateway | 10.0.1.4 | 8443 | slim-gateway:latest |
| NATS JetStream | 10.0.1.5 | 4222 | nats:2.10-alpine |
| Knowledge Retrieval | 10.0.1.6 | 8080 | knowledge-retrieval:v1.1.1-fix |
| Critic/Supervisor | 10.0.1.7 | 8080 | critic-supervisor:v1.1.0-openai |
| Response Generator | 10.0.1.8 | 8080 | response-generator:v1.1.0-openai |
| Analytics | 10.0.1.9 | 8080 | analytics:v1.1.0-openai |
| Intent Classifier | 10.0.1.10 | 8080 | intent-classifier:v1.1.0-openai |
| Escalation | 10.0.1.11 | 8080 | escalation:v1.1.0-openai |
| API Gateway | (assigned) | 8080 | api-gateway:v1.1.2-openai |

**Third-Party Service Accounts (Agent Red owned):**

| Service | Account Type | Status |
|---------|-------------|--------|
| Azure OpenAI Service | Pay-per-token | Active |
| Shopify Partner | Developer account | Active |
| Zendesk | Developer sandbox | Active |
| Mailchimp | Free tier (250 contacts) | Active |
| Google Analytics | GA4 property | Active |

**Key Vault Secrets (credentials stored):**
- azure-openai-api-key
- slim-gateway-password
- cosmos-db-connection-string
- shopify-api-key, shopify-api-secret
- zendesk-api-token
- mailchimp-api-key
- google-analytics-service-account

**Environment Variables (production):**
```bash
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<stored in Key Vault>
USE_AZURE_OPENAI=true
USE_REAL_APIS=true
```

No new account creation, API keys, or credential changes are required. Agent Red deploys to this existing production environment as-is.

### Key AGNTCY Architecture Patterns for Reuse

These patterns from the AGNTCY public repository are relevant for Agent Red's commercial extensions:

**Factory Singleton Pattern:**
```python
# Thread-safe, lazy-initialized access to AGNTCY SDK components
from agntcy_app_sdk.factory import AgntcyFactory
factory = AgntcyFactory(enable_tracing=True)  # Single instance per app
```

**BaseAgent Pattern:**
```python
# All agents extend a base class providing shared boilerplate
# Reduces ~42% code duplication across agents
# Provides: lifecycle management, health checks, graceful shutdown
```

**A2A Message Format:**
```python
# Conversation threading with contextId, workflow tracking with taskId
Message(
    messageId="unique-id",
    role="user",
    parts=[Part(TextPart(text="content"))],
    contextId="conversation-thread-id",
    taskId="workflow-tracking-id",
    metadata={"language": "en", "sentiment": "neutral"}
)
```

**Topic-Based Routing:**
```
intent-classifier      → Intent Classification Agent
knowledge-retrieval    → Knowledge Retrieval Agent
response-generator-en  → Response Generation (English)
response-generator-fr-ca → Response Generation (French-CA)
escalation-handler     → Escalation Agent
analytics-collector    → Analytics Agent
critic-supervisor      → Critic/Supervisor Agent
```

**Connection Pooling (production-grade):**
```python
# Azure OpenAI with httpx connection pool
client = AsyncAzureOpenAI(
    http_client=httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20
        )
    )
)
```

**PII Tokenization:**
```python
# Random UUID tokens for external AI calls
# Format: TOKEN_a7f3c9e1-4b2d-8f6a-9c3e
# Storage: Key Vault (primary), Cosmos DB (fallback if latency >100ms)
# Scope: All PII before third-party AI services
# Exempt: Azure OpenAI Service (within Azure perimeter)
```

### AGNTCY Cost Optimization Lessons

These findings from AGNTCY development inform Agent Red budgeting:

| Decision | Savings | Rationale |
|----------|---------|-----------|
| Cosmos DB Serverless vs provisioned | $85-120/mo | Pay-per-request, no idle costs |
| Container Apps vs AKS | $70-100/mo | No control plane overhead |
| GPT-4o-mini for classification | vs GPT-4o | 98% accuracy at ~$0.15/1M tokens |
| Analytics agent right-sizing (0.25 CPU) | ~$4/mo | Batch workload, low compute need |
| 7-day log retention vs 30-day | ~$15/mo | Sufficient for operational needs |
| Auto-scale to zero (nights) | ~$20-30/mo | KEDA scheduled scaling profiles |

### Integration Patterns Proven in AGNTCY

| Integration | Method | Auth | AGNTCY Scope |
|-------------|--------|------|-------------|
| Shopify | REST API + webhooks | OAuth / access token | read_orders, read_products, read_customers, read_inventory |
| Zendesk | REST API | Email + API token | tickets:write, users:read |
| Mailchimp | REST API | API key + server prefix | lists:read, campaigns:read |
| Google Analytics | GA4 Data API | Service account JSON | Property reports, event export |

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

### In-Scope Deliverables (Phase 1-2)

| Category | Deliverables | Status |
|----------|--------------|--------|
| **Branding** | Logo, colors, typography, guidelines | ✅ Phase 1.1 complete |
| **Legal** | Terms of Service, Privacy Policy, SLA, DPA | ✅ Phase 1.2 complete (AI-drafted, pending legal review) |
| **Website** | Homepage, Features, Pricing, Integrations, About, Contact | ✅ Phase 1.3 complete (6 pages, v2.0) |
| **Documentation** | Docusaurus site with getting-started, integrations, quality CI | ✅ Phase 1.4 complete (5 pages, 20 Mermaid diagrams, quality framework) |
| **E-commerce** | Dual-channel: Shopify App Store (primary) + Stripe (direct) | 🔄 Phase 2.1 in progress (platform decision complete, implementation next) |
| **Guides** | Admin how-to guides (core set) | 📋 Phase 2.3 deferred |
| **Video** | Platform overview, Quick start tutorial | 📋 Phase 2.4 deferred |

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
| **Organization** | Remaker-Digital |
| **Repository** | agent-red-customer-engagement (private) |
| **Visibility** | Private |
| **Branch Protection** | main (require PR, require reviews) |
| **Project Board** | [Agent Red Launch 1.0](https://github.com/orgs/Remaker-Digital/projects/2) (Project #2) |

**Association Rule:** The repository `Remaker-Digital/agent-red-customer-engagement` is strictly associated with GitHub Project #2 (`Agent Red Launch 1.0`) and vice-versa. All issues, tracking, and project management for this repository use that project board exclusively.

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
**Core brand system complete** (Phase 1.1)

### Required Assets
- [x] Logo (primary, icon, wordmark) — "The Beacon" AR monogram
- [x] Color palette — 15 colors, WCAG AA/AAA verified
- [x] Typography selection — Inter + JetBrains Mono
- [x] Brand guidelines document — branding/guidelines/BRAND-GUIDELINES.md
- [ ] Favicon and app icons — derive from branding/logo/PNG/icon-master.png
- [ ] Social media assets
- [ ] Email templates

### Brand Name Usage
- **Full:** Agent Red Customer Experience
- **Short:** Agent Red
- **Product Line:** Agent Red (parent) → Customer Experience (product)

---

## Project Structure

```
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\
│
├── CLAUDE.md                       # This file - AI assistant guidance
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
│
├── config/                         # Configuration files
│   └── stripe_product_ids.json     # Stripe test-mode product/price IDs (27 objects)
│
├── src/                            # Commercial source code
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entrypoint (17 routers, 66 routes, 8 middleware, ~830 lines)
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
│   ├── multi_tenant/               # Multi-tenant infrastructure (38 modules, ~25,000 lines)
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
│   │   ├── tenant_config_api.py    # Config REST API (10 endpoints, /api/config)
│   │   ├── tenant_secret_service.py # Key Vault per-tenant secret management
│   │   ├── customer_profile_service.py # Layer 1 customer profile CRUD, Shopify sync
│   │   ├── conversation_vectorizer.py # Layer 2 vectorization pipeline, semantic search
│   │   ├── response_explainability.py # Per-response decision trace, explainability framework
│   │   ├── admin_conversation_api.py # Conversation inbox admin API (5 endpoints)
│   │   ├── admin_knowledge_api.py  # Knowledge base CRUD admin API (5 endpoints)
│   │   ├── admin_analytics_api.py  # Analytics summary/intents/gaps admin API (3 endpoints)
│   │   ├── admin_team_api.py       # Team member management admin API (5 endpoints)
│   │   ├── admin_gdpr_api.py       # GDPR data export/deletion/consent admin API (5 endpoints)
│   │   ├── admin_audit_api.py      # Audit log query + CSV export admin API (2 endpoints)
│   │   ├── tenant_usage_monitor.py # Progressive throttling (Watch→Warn→Throttle→Isolate)
│   │   ├── security_middleware.py  # Body size limit, JSON depth, security headers, SLA latency recording
│   │   ├── api_versioning.py       # API version headers middleware (X-API-Version)
│   │   ├── structured_logging.py   # JSON structured logging (prod) + colored dev formatter
│   │   ├── trial_management.py     # Trial tier lifecycle, expiry, conversion, demo data (~1,200 lines)
│   │   ├── security_hardening.py   # Input sanitization, CORS, CSP, session validation (~570 lines)
│   │   ├── data_retention.py       # Tier-based data retention enforcement (~380 lines)
│   │   ├── sla_monitoring.py       # P50/P95/P99 latency tracking, uptime, compliance (~390 lines)
│   │   ├── cost_model.py           # Parameterized cost model calculator, projections (~370 lines)
│   │   ├── archival_pipeline.py    # Hot→Warm Parquet archival to Azure Blob Storage (~750 lines)
│   │   └── alert_delivery.py       # Multi-channel alert routing: webhook, dashboard, log (~695 lines)
│   ├── chat/                       # Chat API (Phase 3.0 — IMPLEMENTED)
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
├── tests/                          # Test suites (777 tests total, 0 warnings)
│   ├── conftest.py                 # Shared fixtures: TestClient, MockCosmos, MockNATS, MockKV, auth helpers
│   ├── test_conftest_smoke.py      # 19 fixture smoke tests
│   ├── test_health.py              # 15 health/ready endpoint + startup event tests (§4.6)
│   ├── persistent_memory/          # Persistent Customer Memory tests (30 tests)
│   │   ├── fixtures.py             # Synthetic profiles, conversations, vector data
│   │   ├── test_unit_layers.py     # 20 unit tests (L1-L4)
│   │   └── test_integration_layers.py # 10 cross-layer integration tests
│   ├── multi_tenant/               # Multi-tenant infrastructure tests (~590 tests)
│   │   ├── test_auth_middleware.py  # 57 auth + middleware unit tests
│   │   ├── test_middleware_pipeline.py # 25 full middleware stack tests (§4.2)
│   │   ├── test_conversation_meter.py # 38 ConversationMeter unit tests (§4.3)
│   │   ├── test_critic_policy.py   # 25 CriticPolicy unit tests (§4.4)
│   │   ├── test_cosmos_repository.py # 61 schema + repository tests (§4.5)
│   │   ├── test_gdpr_services.py   # GDPR services tests (P1 §5.2)
│   │   ├── test_nats_isolation.py  # NATS tenant isolation tests (P1 §5.1)
│   │   ├── test_otel_tracing.py    # OpenTelemetry tracing tests (P1 §5.3)
│   │   ├── test_pipeline_resilience.py # Pipeline resilience + circuit breaker tests (P1 §5.4)
│   │   ├── test_system_prompt_builder.py # SystemPromptBuilder tests (P1 §5.5)
│   │   ├── test_tenant_config.py   # Tenant config schema/processor/API tests (P1 §5.6)
│   │   ├── test_tenant_secret_service.py # Key Vault integration tests
│   │   ├── test_usage_dashboard.py # Dashboard API tests (P1 §5.10)
│   │   ├── test_trial_management.py # Trial tier lifecycle tests
│   │   ├── test_sla_monitoring.py  # 25 SLA monitoring tests
│   │   ├── test_cost_model.py      # 20 cost model calculator tests
│   │   ├── test_data_retention.py  # 15 data retention enforcement tests
│   │   └── test_archival_pipeline.py # 15 archival pipeline tests
│   └── integrations/               # Billing integration tests (109 tests)
│       ├── test_provisioning_webhooks.py # 38 tenant lifecycle + webhook tests
│       ├── test_http_billing.py    # 35 HTTP billing endpoint tests (§4.1)
│       ├── test_stripe_catalog.py  # 23 Stripe catalog model tests (§4.7)
│       └── test_usage_consumption.py # 13 3-tier usage consumption tests (§4.8)
│
├── widget/                         # Chat widget frontend (Phase 3.0 Build Phase 2)
│   ├── package.json                # Preact 10.25+, Vite 6, TypeScript 5.7
│   ├── tsconfig.json               # ES2020, Preact JSX, strict mode
│   ├── vite.config.ts              # IIFE single-file build, terser minification
│   ├── dev.html                    # Local dev page with SDK controls
│   └── src/
│       ├── index.ts                # Entry point: boot, Shadow DOM, iframe, SDK
│       ├── theme/tokens.ts         # Design tokens, light/dark, WCAG contrast
│       ├── locale/en.ts            # 34 user-visible strings (i18n-ready)
│       ├── state/store.ts          # Reactive store, message management
│       ├── transport/
│       │   ├── http.ts             # Widget key auth, API client (5 methods)
│       │   ├── sse.ts              # SSE streaming (6 events, auto-reconnect)
│       │   └── ws.ts               # WebSocket typing/presence, ping keepalive
│       └── components/
│           ├── Launcher.tsx         # Shadow DOM floating button, unread badge
│           ├── Panel.tsx            # Root panel, lifecycle, SSE/WS management
│           ├── Header.tsx           # Agent info, avatar, status, close
│           ├── MessageList.tsx      # Auto-scroll, day separators, typing dots
│           ├── MessageBubble.tsx    # Customer/agent/system, streaming cursor
│           ├── InputBar.tsx         # Auto-grow textarea, send, file, branding
│           ├── PreChatForm.tsx      # Configurable fields, validation
│           ├── ChatRating.tsx       # Thumbs up/down, comment, thank-you
│           └── OfflineForm.tsx      # Leave-a-message form
│
├── extensions/                     # Shopify Theme App Extension (Build Phase 3)
│   └── agent-red-chat/
│       ├── shopify.extension.toml  # Extension manifest
│       ├── blocks/
│       │   └── agent-red-chat.liquid # Liquid template (app embed block)
│       └── assets/
│           └── agent-red-widget.iife.js # Placeholder for built widget bundle
│
├── admin/                          # Admin dashboard frontends (Build Phases 4-6, 31 files, ~10,900 lines)
│   ├── shared/                     # 9 shared components + 2 util modules (~5,400 lines)
│   │   ├── OnboardingWizard.tsx    # 9-step merchant onboarding
│   │   ├── ConfigEditor.tsx        # AI behavior configuration
│   │   ├── UsageDashboard.tsx      # Usage metrics + billing charts
│   │   ├── ConversationInbox.tsx   # Conversation list + detail + assignment
│   │   ├── KnowledgeBaseManager.tsx # Knowledge base CRUD
│   │   ├── AnalyticsOverview.tsx   # Analytics summary + charts
│   │   ├── BillingPortal.tsx       # Billing management + Stripe portal
│   │   ├── WidgetConfigurator.tsx  # Widget appearance + behavior config
│   │   ├── TeamManager.tsx         # Team member management
│   │   ├── hooks/index.ts          # Shared API hooks (useApi, useTenantConfig, useSSE, etc.)
│   │   └── types/index.ts          # Shared TypeScript interfaces
│   ├── shopify/                    # Shopify embedded admin (Polaris + App Bridge, 8 files, ~2,700 lines)
│   │   ├── index.tsx               # App entry with AppProvider + AppBridge
│   │   ├── layouts/ShopifyAppLayout.tsx # Navigation + Save Bar integration
│   │   ├── hooks/useSaveBar.ts     # App Bridge Save Bar hook
│   │   └── pages/                  # 7 pages (Dashboard, Inbox, KnowledgeBase, Configuration, Widget, Billing, Settings)
│   └── standalone/                 # Standalone admin (API key login, 9 files, ~2,800 lines)
│       ├── index.tsx               # App entry with BrowserRouter
│       ├── layouts/StandaloneLayout.tsx # Sidebar + header layout
│       ├── login/ApiKeyLogin.tsx   # API key authentication page
│       └── pages/                  # 7 pages (Dashboard, Inbox, KnowledgeBase, Configuration, Widget, Billing, Settings)
│
├── infrastructure/                 # Deployment infrastructure
│   └── terraform/                  # IaC for Azure (variables, main, scaling, DR/security, KEDA jobs)
│
├── website/                        # Marketing website
│   └── content/                    # Page content (markdown)
│
├── docs/                           # Documentation
│   ├── architecture/               # Technical architecture
│   │   ├── ECOMMERCE-PLATFORM-EVALUATION.md
│   │   ├── REWARDFUL-INTEGRATION.md
│   │   ├── PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md
│   │   ├── PERSISTENT-CUSTOMER-MEMORY-METRICS.md
│   │   └── UI-UX-ARCHITECTURE-DECISIONS.md  # 7 UI/UX decisions, chat/widget/admin specs, 24 WIs
│   ├── research/                   # Competitive research
│   │   └── UI-UX-COMPETITIVE-ANALYSIS.md    # 5-competitor feature matrix (10 dimensions)
│   ├── COMPREHENSIVE-TEST-PLAN.md  # ~880 enumerated tests, prioritized (P0-P3 + security + perf)
│   ├── BACKLOG-NEW-WORK-ITEMS.md   # 63 new work items (WI #101-163) from test audit
│   ├── shopify/                    # Shopify App Store materials
│   │   └── APP-STORE-LISTING.md    # Listing copy, specs, and pre-submission checklist
│   ├── guides/                     # How-to guides
│   └── api/                        # API reference
│
├── branding/                       # Brand assets
│   ├── logo/                       # Logo files
│   ├── colors/                     # Color palette
│   └── guidelines/                 # Brand guidelines
│
├── legal/                          # Legal documents
│   ├── terms/                      # Terms of Service
│   ├── privacy/                    # Privacy Policy
│   └── contracts/                  # Customer contracts
│
└── scripts/                        # Automation scripts
    ├── setup/                      # Project setup
    ├── stripe/                     # Stripe catalog creation + tax migration scripts
    ├── build/                      # Build automation
    └── deploy/                     # Deployment scripts
```

---

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| CLAUDE.md | Root | AI assistant guidance (this file) |
| README.md | Root | Project overview |
| PROJECT-PLAN.md | docs/ | Launch 1.0 milestones and tasks |
| COMMERCIAL-SAAS-PROPOSAL.md | docs/ | Full business analysis (A-P deliverables) |
| PRODUCT-FEATURES-RAG.md | docs/ | Complete feature reference for RAG |
| ECOMMERCE-PLATFORM-EVALUATION.md | docs/architecture/ | Three-way platform evaluation (Stripe/Shopify/Paddle) |
| REWARDFUL-INTEGRATION.md | docs/architecture/ | Rewardful affiliate setup guide and checklist |
| PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md | docs/architecture/ | Persistent Customer Memory research foundation |
| PERSISTENT-CUSTOMER-MEMORY-METRICS.md | docs/architecture/ | Test cases, metrics, and A/B testing framework |
| stripe_product_ids.json | config/ | Stripe test-mode product/price/coupon IDs (27 objects) |
| APP-STORE-LISTING.md | docs/shopify/ | Shopify App Store listing copy, asset specs, pre-submission checklist |
| Master-Plan-Review-01-30-2026.md | docs/ | Architecture review: 32 decisions, 100 work items, SLA validation, cost model |
| COMPREHENSIVE-TEST-PLAN.md | docs/ | ~880 enumerated tests with IDs, priorities (P0-P3), security, performance, trial, UI-type matrix |
| BACKLOG-NEW-WORK-ITEMS.md | docs/ | 63 new work items (WI #101-163): test infra, merchant UI, trial env, streaming, optimization, API, ops, security |
| UI-UX-ARCHITECTURE-DECISIONS.md | docs/architecture/ | 7 UI/UX decisions, chat API/widget/admin specs, build order, 24 new work items (WI #164-187) |
| UI-UX-COMPETITIVE-ANALYSIS.md | docs/research/ | 5-competitor feature matrix (Tidio, Gorgias, Zendesk, Intercom, Re:amaze) across 10 dimensions — **ALL PRICING VERIFIED 2026-02-01** |
| DEPLOYMENT-RUNBOOK.md | docs/operations/ | Deployment procedure, DR Option A, maintenance runbook |
| OPTION-C-UPGRADE-PATH.md | docs/operations/ | Geo-replication trigger criteria, migration steps, cost impact |

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
Key files: CLAUDE.md, docs/architecture/UI-UX-ARCHITECTURE-DECISIONS.md, docs/COMPREHENSIVE-TEST-PLAN.md, docs/BACKLOG-NEW-WORK-ITEMS.md
Current status: Phases 0-2.2 COMPLETE. Phase 2.5 Layers 1-2 COMPLETE. Phase 3.0 ALL BUILD PHASES COMPLETE (Chat API, widget frontend, Shopify Theme App Extension, admin shared components, Shopify admin shell, standalone admin shell). Operational readiness COMPLETE. Security hardening COMPLETE. Pipeline optimization COMPLETE. Trial environment COMPLETE. Competitive pricing VERIFIED (all 5 competitors — Agent Red 4-21x cheaper). 777 tests passing, 0 warnings. 38 multi_tenant modules (~25,000 lines). 31 admin frontend files (~10,900 lines). 20 widget files (~3,200 lines). 17 routers, 66 routes, 8 middleware layers.
Next priority: Please prepare an order of priority for all known outstanding work issues in this project and follow this order when proposing tasks for completion. Remaining major areas: (1) Admin frontend build validation (npm install, TypeScript compile, bundle check for admin/shopify and admin/standalone), (2) Widget bundle → Theme App Extension copy, (3) P2 launch quality tests (~135 tests, COMPREHENSIVE-TEST-PLAN.md §6), (4) Integration testing with real Stripe test mode and Shopify partner sandbox, (5) Creative assets for Shopify App Store (icon, screenshots, demo video — blocked on design), (6) Phase 2.5 Layer 3 PatternExtractionService (Professional+, WI #90-92), (7) Remaining backlog items (CI improvements #105-107, SSE enhancements #131-133, API completeness #142-146).
Important context: Tidio is the primary functional reference. Zapier is the visual styling reference. Persistent Customer Memory (Layers 1-2) is the launch pillar differentiator. All competitor pricing now verified — use updated figures from docs/research/UI-UX-COMPETITIVE-ANALYSIS.md. Iterative working style: one item at a time, honest assessment, approval before implementation, aggressive scope cutting.
Please review CLAUDE.md, then proceed with the highest-priority remaining technical work item, presenting one item at a time for review per the iterative working style documented in CLAUDE.md.
```

### Referencing AGNTCY

When you need information about the AGNTCY open-source foundation:
- Read the public repository at https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- Reference the SDK documentation for `agntcy-app-sdk`
- Do **not** reference local AGNTCY files by path
- The "Upstream Dependency" section of this CLAUDE.md contains transferred architectural knowledge

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

### Work Priority Bias

**Technical work has elevated priority over creative/content work.** Technical gap identification, test case creation, testing/results analysis, and implementation of new capabilities should always be prioritized above creative assets, marketing content, and cosmetic work. The rationale: the technical implementation is the foundation for cost estimates, which are in turn the basis for pricing and licensing decisions. Cost estimates and pricing decisions cannot be validated without comprehensive test data from a working implementation.

### Adding Commercial Features

1. Create features in `src/` exclusively
2. Document in `docs/architecture/`
3. Add copyright notice to all new files
4. Test integration patterns independently
5. Never commit AGNTCY source code into this repo

---

## Current Status (2026-02-01)

### Completed

**Phase 0: Project Setup**
- [x] Project requirements gathered (12 questions answered)
- [x] Directory structure created
- [x] CLAUDE.md created with full knowledge transfer
- [x] README.md created
- [x] .gitignore configured
- [x] PROJECT-PLAN.md with milestones
- [x] Commercial proposal migrated (COMMERCIAL-SAAS-PROPOSAL.md)
- [x] Product features for RAG migrated (PRODUCT-FEATURES-RAG.md)
- [x] Website content migrated (5 pages)
- [x] GitHub private repository created (Remaker-Digital/agent-red-customer-engagement)
- [x] Initial commit pushed
- [x] Docker development environment (Dockerfile, docker-compose.yml, requirements.txt)
- [x] AGNTCY baseline verified - local Docker (15 containers, 97.8% unit tests, 99.3% integration tests)
- [x] AGNTCY baseline verified - production Azure (53 resources, evaluation framework passed)
- [x] Verification scripts created (scripts/verify-agntcy-local.ps1, scripts/verify-agntcy-production.ps1)
- [x] GitHub Project board set up (#2, 8 milestone issues)

**Phase 1.1: Brand Identity**
- [x] Logo concepts — "The Beacon" AR monogram approved
- [x] Color palette — 15 colors, WCAG AA/AAA verified
- [x] Typography — Inter + JetBrains Mono
- [x] Brand guidelines document — branding/guidelines/BRAND-GUIDELINES.md

**Phase 1.2: Legal Documents**
- [x] Terms of Service — legal/terms/TERMS-OF-SERVICE.md
- [x] Privacy Policy — legal/privacy/PRIVACY-POLICY.md
- [x] SLA — legal/sla/SERVICE-LEVEL-AGREEMENT.md
- [x] Data Processing Agreement — legal/dpa/DATA-PROCESSING-AGREEMENT.md
- [ ] Termly/iubenda validation — deferred to pre-launch

**Phase 1.3: Website Content**
- [x] Homepage — full rewrite for commercial buyer focus
- [x] Features — rebranded, 6-category scrollspy layout
- [x] Pricing — complete redesign: platform fee + metered AI usage model
- [x] Integrations — rebranded, Mailchimp/GA moved to add-on pricing
- [x] About — honesty pass, open-source foundation story, verified metrics
- [x] Contact — new page with form, channels, partner program teaser
- [x] Content README index updated

**Phase 1.4: Public Documentation**
- [x] Docusaurus scaffold — docs-site/ with Agent Red branding, Mermaid diagram support
- [x] Documentation quality framework — Vale, markdownlint, alex, link-check, coverage audit, GitHub Actions CI
- [x] Diataxis framework adopted — feature inventory YAML with 21 features × 4 content types
- [x] Getting-started guide — 3 pages (overview, how-it-works, setup) with 14 Mermaid diagrams
- [x] Shopify integration guide — OAuth, sync, field mapping, order lookups, troubleshooting, 6 Mermaid diagrams
- [x] "Was this helpful?" feedback widget — stub connected to DocItem footer
- [x] Eraser.io evaluated — deferred to Phase 2.2 for architecture diagrams (API token available)
- [x] Coverage baseline: 26% actionable slots documented (52% explanation, 21% how-to, 0% tutorial/reference)

### Key Findings
- **Azure OpenAI Endpoint:** `https://remaker.openai.azure.com/` (not the placeholder in AGNTCY's `.env.azure.example`)
- **Per-conversation AI cost:** ~$0.007 (GPT-4o response generation = 94.5% of total)
- **Original cost basis was wrong:** CLAUDE.md v1 stated $30/$50/$100 per tier. Actual single-tenant costs are $235-520/$777-1,005/$2,733-2,887. Multi-tenant economics (shared infrastructure) make it viable.
- **Content principles established:** Honesty, accuracy, and correctness are central concerns. Transparent pricing as competitive advantage. Open-source foundation as trust mechanism.
- **E-commerce platform decision:** Dual-channel (Shopify App Store + Stripe). Shopify provides discovery among ~5M merchants with 0% commission on first $1M revenue. Stripe provides direct billing for non-Shopify merchants at ~3.5% per transaction. Paddle rejected (no marketplace, higher fees, redundant tax handling). Existing Shopify integration is ~80% of what the App Store requires. Agent Red's price advantage (2–13x cheaper per interaction than Gorgias, Intercom, Zendesk) positions it as a disruptive value entrant in an established ecosystem.
- **Neither Shopify nor Stripe have formal named partner tiers.** Benefits scale informally with growth. Shopify: "Built for Shopify" badge at ~3-6 months, partner manager at ~10K installs. Stripe: "Verified Partner" badge after production integration review, custom pricing at ~$80K+/mo volume.
- **Persistent Customer Memory validated as differentiator.** No competitor confirmed doing per-customer vector RAG over historical transcripts. Sierra AI (Agent Data Platform) is closest but not customer-facing. Marginal cost ~$0.005-$0.011/customer/month for Layers 1-2. Research, metrics framework, test cases, and A/B methodology documented. Feature propagated across all 18 project files (business, marketing, docs-site, legal, brand). Privacy reconciliation complete — default "no training" preserved with opt-in carve-out for Layer 4.
- **Rewardful does not support Stripe test mode.** Trial account created. OAuth connection requires live Stripe with admin permissions. Backend code integration (client_reference_id on Checkout Sessions) works identically in test/live mode. Recommended plan: Starter ($49/mo, $7,500/mo affiliate revenue cap). Setup checklist documented in docs/architecture/REWARDFUL-INTEGRATION.md.
- **Shopify annual billing limitation discovered.** Shopify's AppSubscription API does not support `appUsagePricingDetails` with `ANNUAL` interval — only `EVERY_30_DAYS`. Annual subscribers get recurring base only; overage must be handled via `appPurchaseOneTimeCreate` or conversation packs (Phase 2.2).

**Phase 2.1: E-Commerce Store (In Progress — ~85% Code Complete)**
- [x] Three-way platform evaluation (Stripe vs Shopify App Store vs Paddle) — docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md
- [x] Decision: Dual-channel (Shopify App Store primary + Stripe direct). Paddle rejected.
- [x] Approval process and partner growth path documented (Appendices A & B)
- [x] Stripe account setup, Products, Prices, Coupons in test mode — scripts/stripe/create_product_catalog.py (27 Stripe objects), config/stripe_product_ids.json
- [x] Stripe Checkout integration for plan selection — src/integrations/stripe_checkout.py (POST /api/checkout/session, success/cancel redirects)
- [x] Stripe webhook handler (subscription lifecycle → tenant provisioning) — src/integrations/stripe_webhooks.py (6 events: checkout.session.completed, subscription CRUD, invoice payment success/failure)
- [x] Metered usage reporting to Stripe — src/integrations/stripe_usage.py (3-tier consumption: included → pack balance → Stripe Billing Meter overage)
- [x] Shopify Billing API integration — src/integrations/shopify_billing.py + shopify_client.py (GraphQL Admin API, appSubscriptionCreate, usage records, Decimal arithmetic)
- [x] Conversation pack purchase flow — src/integrations/stripe_packs.py (1K/5K/20K packs, 90-day validity, FIFO consumption, Stripe Checkout mode=payment)
- [x] Unified webhook handler (both channels → provisioning) — src/integrations/provisioning.py (BillingChannel enum, TenantStatus lifecycle, channel-agnostic provision/activate/update/deactivate/flag)
- [x] Stripe Customer Portal — src/integrations/stripe_portal.py (POST /api/billing/portal, tenant lookup for Stripe customer ID resolution)
- [x] Rewardful affiliate integration — client_reference_id on Checkout Sessions, docs/architecture/REWARDFUL-INTEGRATION.md (live Stripe connection deferred — Rewardful does not support test mode)
- [x] Stripe Tax setup — automatic_tax on Checkout Sessions (subscription + payment mode), tax_code `txcd_10103001` (SaaS — Business Use) on Products, tax_behavior `exclusive` on new Prices, tax_id_collection for business VAT/tax IDs, invoice.finalization_failed webhook handler, migration script for existing Products (scripts/stripe/update_tax_codes.py)
- [x] Shopify App Store listing copy — docs/shopify/APP-STORE-LISTING.md (app name, tagline, description, key benefits, feature list, pricing config, search terms, testing instructions, pre-submission checklist). Creative assets (icon, screenshots, video, demo store) pending.
- [ ] Implement GDPR compliance webhooks — 3 mandatory Shopify endpoints (customers/data_request, customers/redact, shop/redact)
- [ ] Implement session token authentication for embedded Shopify app (required since 2025, replaces cookie-based auth)
- [ ] Implement App Bridge Save Bar API integration (required for embedded app save functions)
- [ ] App Store review submission — blocked by: GDPR webhooks, session tokens, App Bridge Save Bar, creative assets
- [ ] Test checkout flows (both channels)

**API Route Map (17 routers, 66 routes, 8 middleware):**

| Prefix | Module | Endpoints |
|--------|--------|-----------|
| `/api/tenants` | provisioning | GET /lookup, GET /{tenant_id} |
| `/api/checkout` | stripe_checkout | POST /session, GET /success, GET /cancel |
| `/api/packs` | stripe_packs | POST /purchase, GET /balance/{customer_id} |
| `/api/billing` | stripe_portal | POST /portal |
| `/api/usage` | stripe_usage | POST /record, GET /{customer_id} |
| `/api/webhooks` | stripe_webhooks | POST /stripe |
| `/api/shopify/billing` | shopify_billing | POST /subscribe, GET /confirm, GET /status |
| `/api/shopify/gdpr` | shopify_gdpr_webhooks | POST /customers-data-request, POST /customers-redact, POST /shop-redact |
| `/api/dashboard` | usage_dashboard_api | GET /usage, GET /usage/daily, GET /conversations, GET /conversations/{id}, GET /conversations/export |
| `/api/config` | tenant_config_api | GET/PUT/PATCH/POST/DELETE config, onboarding wizard, preview, reset, history, diff (10 endpoints) |
| `/api/chat` | chat endpoints | POST /conversations, POST /message, GET /stream/{id}, GET /conversations/{id}, POST /conversations/{id}/end, WS /ws/{id} |
| `/api/admin/conversations` | admin_conversation_api | GET list, GET /{id}, GET /{id}/messages, POST /{id}/assign, POST /{id}/notes |
| `/api/admin/knowledge` | admin_knowledge_api | GET list, POST create, GET /{id}, PUT /{id}, DELETE /{id} |
| `/api/analytics` | admin_analytics_api | GET /summary, GET /intents, GET /gaps |
| `/api/admin/team` | admin_team_api | GET list, POST invite, GET /{id}, PUT /{id}, DELETE /{id} |
| `/api/admin/gdpr` | admin_gdpr_api | POST /export, POST /delete, GET /consent/{id}, PUT /consent/{id}, GET /consent |
| `/api/audit` | admin_audit_api | GET (paginated query), GET /export (CSV) |

**Phase 2.1 Key Technical Decisions:**
- **Shopify annual billing limitation:** Shopify does not support usage billing with ANNUAL interval. Annual subscriptions get recurring base only; overage deferred to Phase 2.2 (one-time app charges).
- **Decimal arithmetic for billing:** All Shopify billing amounts use Python `Decimal` to avoid floating-point precision errors.
- **3-tier conversation consumption:** Included allowance (free) → Pack balance (FIFO, oldest-first, 90-day expiry) → Stripe Billing Meter (overage).
- **In-memory dev stores:** All state (usage counters, pack balances, tenant records) uses in-memory dicts with DEVELOPMENT ONLY warnings. Production replacement: Cosmos DB with tenant partitioning (Phase 2.2).
- **Rewardful requires live Stripe:** OAuth connection deferred to launch. Code integration (client_reference_id) works in test mode.
- **Stripe Tax: exclusive pricing, SaaS B2B tax code:** All Checkout Sessions enable `automatic_tax`. Products carry `txcd_10103001` (SaaS — Business Use). Prices use `tax_behavior="exclusive"` (tax added on top, US B2B standard). `tax_id_collection` enabled for business VAT/tax IDs. Dashboard prerequisites: origin address (Delaware), default tax behavior, nexus state registrations. Cost: $0.50/transaction (Stripe Tax Basic).
- **invoice.finalization_failed handler added:** Catches cases where Stripe Tax cannot determine customer location (invalid/missing address). Flags tenant for payment issue and logs for investigation.

**Phase 2.5: Persistent Customer Memory (Layers 1-2 COMPLETE — Layers 3-4 Pending)**
- [x] Design customer profile schema — 6 data sources validated (purchase history, cart, geography, marketing, jurisdiction, product questions)
- [x] Design Layer 1 injection — ~250 token prompt context block
- [x] Design Layer 2 vectorization — text-embedding-3-large, Cosmos DB DiskANN, tier-gated depth
- [x] Design Layer 3 extraction — PatternExtractionService, confidence scoring, decay
- [x] Design Layer 4 fine-tuning pipeline — quality gates, A/B deployment, rollback
- [x] Design explainability framework — per-response decision trace
- [x] Design test framework — 20 unit, 10 integration, 5 A/B production tests
- [x] Implement Layer 1: CustomerProfileService + SystemPromptBuilder injection (work items 83-85)
- [x] Implement Layer 2: Vectorization pipeline + semantic search (work items 87-88)
- [x] Implement explainability framework (work item 86)
- [x] Implement test suites + fixtures (work items 97-98, 100) — 30 tests passing
- [ ] Implement Layer 3: PatternExtractionService + decay + admin UI (work items 90-92)
- [ ] Implement Layer 4: Fine-tuning pipeline + deployment + rollback (work items 93-96)
- [ ] Create metrics dashboard (KPIs from PERSISTENT-CUSTOMER-MEMORY-METRICS.md)

**Phase 2.2: Multi-Tenant Architecture (Designed — 32 Decisions, 100 Work Items)**

Full architecture review completed 2026-01-30. All decisions documented in `docs/Master-Plan-Review-01-30-2026.md`. Key design outcomes:

**Infrastructure (Option B+ — 7 critical components at min=2 replicas):**
- API Gateway, Intent Classifier, Response Generator, Knowledge Retrieval, NATS, SLIM Gateway, Critic/Supervisor: min=2
- Escalation, Analytics: min=1
- Fail-closed Critic policy: pipeline never delivers responses that skip safety validation
- KEDA auto-scaling with per-agent triggers
- Monthly infrastructure: ~$252-436 (up from ~$200-400, within $500-1,000 budget)

**Security / Tenant Isolation (Decisions 1-6):**
- TenantScopedRepository: mandatory data access layer enforcing tenant_id on every DB operation
- Cosmos DB: 9 collections, partition key = tenant_id (7 tenant-scoped, 2 platform-wide)
- NATS: tenant-scoped topics `{tenant_id}.{agent}`
- Dual authentication: Shopify session tokens + API keys, both resolving to server-derived tenant_id
- Per-tenant rate limits: Starter 10/min, Professional 50/min, Enterprise 200/min
- Per-tenant secrets in Key Vault: `tenant-{id}-{type}` naming convention

**GDPR Compliance (Decisions 7-10):**
- PII scrubbing at logging layer (no customer data in Application Insights)
- Channel-specific grace periods: 48hr Shopify, 30-day Stripe
- DataExportService + DataDeletionService with data store registry pattern
- Consent management: `consent_status` (granted/denied/not_asked) gating Persistent Customer Memory Layers 2-4

**Tracing / Observability (Decisions 11-13):**
- OpenTelemetry: tenant_id injected as custom dimension on all telemetry
- Correlation ID chain: conversation_id + tenant_id + trace_id across all 6 agents
- Append-only audit log: 12 event types, time-partitioned, 1-year retention

**Performance / Noisy Neighbor (Decisions 14-17):**
- Per-tenant concurrency limits: Starter 3, Professional 10, Enterprise 30
- Layered timeout budget: 8s hard deadline (Intent 800ms, Knowledge 1000ms, Response 3000ms, Critic 800ms)
- Circuit breakers: Azure OpenAI (5 failures/30s), Cosmos DB (3/15s), NATS (3/10s)
- TenantUsageMonitor: progressive throttling Watch → Warn → Throttle → Isolate

**Disaster Recovery / Maintenance (Decisions 18-21):**
- Cosmos DB continuous 7-day backup (~$4-6/month)
- Long-term archival: Hot (Cosmos) → Warm (Blob Cool, 90d) → Cold (Blob Archive, 7+ years)
- Customer-Managed Keys (CMK) for encryption at rest with auto-rotation
- Parquet format for ML training corpus (daily Change Feed → Azure Function → Blob)
- Zero-downtime rolling deployment with 60s connection draining
- Maintenance window: Tuesdays 02:00-04:00 UTC
- DR: Option A (single region + backup) for launch, Option C (geo-replication) at 50+ tenants

**Per-Merchant Behavior Tuning (Decisions 22-23):**
- 5-layer tenant config system: TenantConfigProcessor → A/B Framework → Config API (10 endpoints) → Merchant UI (9-step onboarding) → Contextual Data Service
- Config inheritance: platform defaults → tier defaults → tenant overrides (60s cache)
- Merchant UI: pervasive tooltips, documentation links, live preview, adjacent contextual data
- SystemPromptBuilder: dynamic prompt assembly per-agent from tenant config with immutable safety guardrails
- **Smart Rollout (Phase 3 design decision, 2026-01-30):** A/B testing for AI prompts is niche — only Zendesk offers it natively (behind highest-priced tier). Gorgias, Tidio, Intercom have no native support. Agent Red's approach: AI-assisted configuration changes with controlled rollout. A foundation model analyses conversation data, identifies improvement opportunities, generates config variants (persona descriptions, escalation thresholds, response styles, segmentation tags), and the merchant's role is narrowly scoped to editorial review and test approval. Merchant answers 5 simple questions: who's in the test group, when does it start, when does it end, which variant to apply, which KPIs to track. The SystemPromptBuilder's resolved-config pattern enables this without modification — the caller swaps which PreferencesDocument is passed based on test group membership. No experiment-specific code in the prompt builder. Implementation deferred to Phase 3 (requires conversation data from Layer 2 + platform benchmarks from sufficient tenants).

**Metering / SLA Validation (Decisions 24-27):**
- Billable conversation: starts on first message, ends on 30-min idle / customer end / escalation / 50 turns
- ConversationMeter: idempotent counting (dedup on conversation_id), daily reconciliation vs Stripe
- 3-layer usage transparency: real-time dashboard, per-conversation audit trail (CSV export), dispute resolution workflow
- Proactive billing alerts: 80%/100% allowance, pack balance low, volume spikes
- Billable conversation spec published as binding reference document
- SLA gaps resolved: P50 revised to 1,500ms, maintenance window aligned, backup retention clarified (7d PITR + 90d archive)
- Cost basis validated: per-conversation ~$0.0073, margins 76-90%, break-even at 2 Starter tenants

**Persistent Customer Memory Implementation (Decisions 28-32):**
- Layer 1: Customer profile with 6 data sources (purchase history, cart, geography, marketing segments, jurisdiction codes, product questions). ~250 token prompt injection. All tiers.
- Layer 2: Conversation vectorization (text-embedding-3-large, 3072d, Cosmos DB DiskANN). ~300 token injection. History depth: Starter 90d, Professional 365d, Enterprise unlimited. All tiers.
- Layer 3: PatternExtractionService (GPT-4o-mini post-conversation). Confidence scoring 0-1, decay 0.05/month. ~100 token injection. Professional+ only.
- Layer 4: Fine-tuning GPT-4o-mini on 1,000+ conversations. Monthly pipeline with quality gates and A/B validation. Enterprise add-on $299/mo.
- Response explainability: per-response decision trace (profile factors, knowledge sources, memory signals, A/B variant, Critic assessment)
- Test framework: 20 unit tests, 10 integration tests, 5 A/B production tests

**SLA Commitments (post-review):**
- Uptime: Starter 99.5%, Professional 99.9%, Enterprise 99.95%
- API latency: P50 < 1,500ms, P95 < 2,000ms, P99 < 5,000ms
- Backup: 7-day point-in-time restore + 90-day warm archive + 7+ year cold archive
- RTO: 4hr Enterprise, 8hr Professional, 24hr Starter

**Phase 2.2: Multi-Tenant Infrastructure (Tier 1 Critical — COMPLETE)**

All four Tier 1 Critical work item groups implemented 2026-01-30. Seven modules created in `src/multi_tenant/` (~3,500 total lines).

- [x] **#13-14/#24-25: Cosmos DB Schema + TenantScopedRepository** — `cosmos_schema.py` (~560 lines) + `cosmos_client.py` (~150 lines) + `repository.py` (~650 lines)
  - 9 collection configurations with partition keys, unique keys, composite indexes, DiskANN vector index
  - 11 Pydantic document models: TenantDocument, ConversationDocument, UsageCounterDocument, PackBalanceDocument, IdempotencyKeyDocument, CustomerProfileDocument, KnowledgeBaseDocument, MemoryVectorDocument, PreferencesDocument, PlatformConfigDocument, AuditLogDocument
  - 7 enums: TenantTier, TenantStatus, BillingChannel, ConsentStatus, ConversationStatus, AuditEventType, PiiClassification
  - TIER_DEFAULTS with rate limits, concurrency, history depth, memory layers per tier
  - CosmosManager singleton (lazy init, account key + Managed Identity support, container caching, health check)
  - TenantScopedRepository base class: create/read/upsert/patch/delete/query/query_count — all enforce tenant_id
  - Defense-in-depth: validation on every write, verification on every read, query result filtering
  - 7 tenant-scoped repos + 2 platform-scoped repos (PlatformConfig, AuditLog)
  - Atomic counter increments via Cosmos DB patch "incr" (no read-modify-write races)

- [x] **#18/#27: Dual Auth + Tenant Resolution** — `auth.py` (~280 lines) + `middleware.py` (~290 lines)
  - Shopify session token verification (JWT HS256, PyJWT, 10s leeway, required claims, .myshopify.com domain enforcement)
  - API key authentication (SHA-256 hash + async lookup)
  - TenantContext frozen dataclass (tenant_id, tier, status, auth_method, shop_domain, user_id, session_id)
  - TenantAuthMiddleware (Starlette): authenticates every request, stores TenantContext in request.state
  - RateLimitMiddleware: per-tenant sliding window (Starter 10rpm, Professional 50rpm, Enterprise 200rpm)
  - get_tenant_context() and require_tier() FastAPI dependencies
  - Auth-exempt paths: health, webhooks, checkout callbacks, docs

- [x] **#71-72: Billable Conversation Definition + ConversationMeter** — `conversation_meter.py` (~605 lines)
  - Billable conversation spec as code: start on first message, end on 30-min idle / customer ends / escalation / 50 turns
  - Non-billable: test_, admin_, health_, system_ prefixes; no AI response before error
  - ConversationMeter service: idempotent metering (dedup on conversation_id via idempotency keys)
  - 3-tier consumption: included allowance → pack balance (FIFO) → Stripe Billing Meter overage
  - Proactive alerts at 80%/100% thresholds (once per period, idempotent)
  - Daily reconciliation against Stripe Billing Meter (flags >5% discrepancy for review)
  - UsageDashboard (Decision #25 Layer 1), per-conversation billing detail (Layer 2)
  - Idle conversation scanner for periodic timeout enforcement

- [x] **#50: Fail-Closed Critic Policy** — `critic_policy.py` (~450 lines)
  - CriticPolicy: fail-closed safety gate — response blocked unless Critic explicitly approves
  - Critic rejection, timeout, error, unavailability all result in blocking
  - SAFE_FALLBACK_MESSAGE: only unvalidated text deliverable to customers
  - require_critic_approval() pipeline wrapper: returns (approved, safe_text, result)
  - CircuitBreaker: CLOSED → OPEN (5 failures/30s) → HALF_OPEN (15s recovery) state machine
  - CriticResult frozen dataclass: verdict, flags, modifications, latency, tracing
  - SECURITY_EVENT audit on every blocked response
  - ESCALATION_TRIGGERED when Critic replicas unavailable
  - Health monitoring for /ready endpoint integration
  - 800ms timeout budget per Decision #15
  - httpx connection pooling for Critic HTTP calls

**Phase 2.2 Tier 2 (High) — COMPLETE:**

- [x] **#15-17/#26: NATS Tenant Isolation** — `nats_isolation.py` (~600 lines)
  - TenantNATSManager: singleton managing per-tenant topic namespaces and subscriptions
  - Topic namespace: `{tenant_id}.{agent}` for all 6 agents (intent-classifier, knowledge-retrieval, response-generator, escalation-handler, analytics-collector, critic-supervisor)
  - JetStream stream per tenant: `tenant-{tenant_id}` with wildcard subject `{tenant_id}.>`
  - Subscription authorization: `authorize_subject()` validates tenant_id prefix before publish/subscribe
  - NATSAuthorizationError raised on cross-tenant access attempts
  - provision_tenant_topics(): creates JetStream stream on tenant creation, tier-aware queue depth from TIER_DEFAULTS
  - update_tenant_stream(): adjusts queue depth on tier change without disrupting subscriptions
  - deprovision_tenant_topics(): purges messages and deletes stream on tenant deletion
  - NATSCircuitBreaker: 3 failures / 10s window, 5s recovery (Decision #15)
  - Correlation ID propagation: build_correlation_headers() / extract_correlation_headers() for Decision #12
  - Health monitoring for /ready endpoint integration
  - Module-level singleton with init_nats_manager() / close_nats_manager() lifecycle
  - Wired into main.py startup/shutdown events

- [x] **#30-34: GDPR Core Services** — `gdpr_services.py` (~800 lines)
  - PiiScrubber (#30): recursive dict/list scrubbing with field-level classification (DIRECT/INDIRECT/SENSITIVE), regex email/phone detection in free text, scrub_text() for log messages
  - GracePeriodManager (#31): channel-specific grace periods (Shopify 48hr, Stripe 30d), calculate_grace_period(), is_grace_expired(), GracePeriodResult dataclass
  - DataStoreRegistry + adapters (#32-33): registry pattern with DataStoreAdapter protocol, CosmosDataStoreAdapter (7 collections), NATSDataStoreAdapter (stream purge/delete)
  - DataExportService (#32): tenant-level and customer-level export across all registered stores, ExportResult dataclass, audit logging (DATA_EXPORTED)
  - DataDeletionService (#33): cascading deletion across all stores, grace period enforcement, GracePeriodActiveError, tenant and customer deletion, audit logging (DATA_DELETED)
  - ConsentManager (#34): consent_status gating for Persistent Customer Memory Layers 2-4, tenant-level and customer-level consent updates, automatic Layer 2-4 data deletion on consent denial, audit logging (CONSENT_CHANGED)
  - All services integrate with AuditLogRepository for compliance trail

- [x] **#39-40 (+#41): OpenTelemetry Tenant Tracing** — `otel_tracing.py` (~400 lines)
  - TenantSpanProcessor (#39): injects tenant_id, conversation_id, trace_id, auth_method, tier as span attributes on every span start. Application Insights custom dimensions.
  - TenantLogFilter (#39): Python logging.Filter injecting tenant context into every log record. Structured log format: `[tenant=X conv=Y trace=Z]`.
  - CorrelationContext (#40): frozen dataclass carrying the correlation triple (tenant_id + conversation_id + trace_id) via async-safe contextvars.ContextVar.
  - CorrelationMiddleware (#40): ASGI middleware reading TenantContext from auth and setting CorrelationContext for the request lifecycle. Clears on request completion.
  - NATS correlation helpers (#40): correlation_to_nats_headers(), nats_headers_to_correlation(), restore_correlation_from_nats() for agent-to-agent propagation.
  - trace_agent_operation(): convenience span factory for instrumenting agent pipeline steps.
  - configure_tracing() + configure_logging(): one-call setup wired into main.py startup.
  - #41 (audit log): already fully implemented in cosmos_schema.py + repository.py (AuditLogDocument, 12 AuditEventType values, AuditLogRepository) — confirmed complete.

- [x] **#44-46: Pipeline Resilience / Performance Noisy Neighbor** — `pipeline_resilience.py` (~500 lines)
  - TenantConcurrencyMiddleware (#44): per-tenant asyncio.Semaphore + queue depth from TIER_DEFAULTS (Starter 3/5, Professional 10/20, Enterprise 30/50). Returns HTTP 429 when both active slots and waiting queue are full. Lazy _TenantGate creation on first request per tenant.
  - PipelineTimeoutBudget (#45): layered timeout across 6-agent pipeline with 8,000ms hard deadline. Stage budgets: IC=800ms, KR=1000ms, RG=3000ms, CR=800ms, ESC=1400ms, AN=800ms. StageResult dataclass tracks per-stage duration. PipelineTimeoutError raised on budget exhaustion.
  - ServiceCircuitBreaker (#46): configurable per-service circuit breaker. Default configs: Azure OpenAI (5 failures/30s window, 15s recovery), Cosmos DB (3/15s, 10s recovery). NATS breaker already in nats_isolation.py.
  - ServiceCircuitBreakerRegistry: named breaker management with health_summary() and reset_all(). Module-level singleton via get_circuit_breaker_registry().
  - call_with_breaker(): async helper wrapping any coroutine with circuit breaker protection. Raises ServiceUnavailableError when breaker is OPEN.
  - Wired into main.py: TenantConcurrencyMiddleware in middleware stack, circuit breaker health in /ready endpoint, registry startup logging.

- [x] **#70: SystemPromptBuilder — per-agent prompt composition** — `system_prompt_builder.py` (~450 lines)
  - 4-layer prompt assembly: platform base (immutable) → tier capabilities → tenant config → customer context.
  - AgentRole enum for 6 pipeline agents (intent-classifier, knowledge-retrieval, response-generator, escalation-handler, analytics-collector, critic-supervisor).
  - Per-agent specialisation: Response Generator gets full persona + customer context + policies; Escalation Handler gets escalation rules + customer summary; Intent Classifier gets language support; Critic/Supervisor prompt is entirely immutable (no tenant config injected).
  - Platform base prompts: hardcoded safety guardrails per agent, cannot be overridden by merchant config.
  - Tenant config injection: brand, voice, formality, response length, policies, escalation rules, custom instructions (sandboxed).
  - Customer context (Layer 1, ~250 token budget): compact summaries from 6 data sources (purchase history, product questions, geography, marketing segments, jurisdiction, cart).
  - Safety invariant: custom_instructions sandboxed with "advisory — safety rules take precedence" header. Critic prompt immutable.
  - explain() method for response explainability framework (Decision #32): returns structured trace of layers, config fields, and data sources without exposing prompt text.
  - build_all() convenience method for pipeline orchestration — returns dict[AgentRole, str].
  - Stateless builder — receives resolved PreferencesDocument. Agnostic to whether config is live or test-group override (compatible with future Smart Rollout / AI-assisted A/B).
  - Module-level singleton via get_prompt_builder().

- [x] **#73-74: Usage Dashboard API + Per-Conversation Audit Trail** — `usage_dashboard_api.py` (~350 lines)
  - Layer 1 (real-time dashboard): GET /api/dashboard/usage — surfaces ConversationMeter.get_usage_dashboard() data (counters, allowance, overage estimate, pack balance, active alerts).
  - Layer 1 supplement: GET /api/dashboard/usage/daily — per-day total/billable counts for chart rendering, aggregated from ConversationRepository queries.
  - Layer 2 (audit trail): GET /api/dashboard/conversations — paginated billable conversation list with offset/limit (max 200), total count for pagination metadata.
  - Layer 2 (detail): GET /api/dashboard/conversations/{id} — full billing attribution via ConversationMeter.get_conversation_billing_detail().
  - Layer 2 (export): GET /api/dashboard/conversations/export — CSV export of all billable conversations (11 columns: ID, status, customer, billable, messages, turns, timestamps, agents, model, Critic pass/fail).
  - All endpoints derive tenant_id from TenantContext auth — tenant isolation enforced, no tenant_id in query params.
  - Pydantic response models: UsageDashboardResponse, DailyVolumeResponse, ConversationListResponse, ConversationDetailResponse.
  - Service injection via configure_dashboard_services() — wired at app startup after Cosmos DB bootstrap.
  - CSV uses Python csv + io.StringIO → StreamingResponse (no new pip packages).
  - Router mounted at /api/dashboard in main.py (8th router, 20 total endpoints).

- [x] **#63-65: Tenant Configuration Schema + Processor + API** — `tenant_config_schema.py` (~300 lines) + `tenant_config_processor.py` (~350 lines) + `tenant_config_api.py` (~400 lines)
  - TenantConfigSchema: Pydantic schema with full validation, 9-step onboarding model, tier-aware field limits.
  - TenantConfigProcessor: validates, cleanses, merges platform defaults → tier defaults → tenant overrides.
  - TenantConfigAPI: 10 REST endpoints (GET/PUT/PATCH/POST/DELETE config, onboarding wizard, preview, reset, history, diff).
  - 60s cache with tenant-scoped invalidation. Router mounted at /api/config in main.py (9th router, 30 total endpoints).

- [x] **#29: TenantSecretService — Key Vault Integration** — `tenant_secret_service.py` (~350 lines)
  - Per-tenant secret CRUD with `tenant-{id}-{type}` naming convention.
  - Azure Key Vault (DefaultAzureCredential) with in-memory cache (5-min TTL).
  - Secret types: shopify_api_key, shopify_api_secret, zendesk_api_token, mailchimp_api_key, custom_integration, webhook_secret, encryption_key.
  - Health check, wired into main.py startup/shutdown/ready.

- [x] **#52/55/58-59: DR & Security Infrastructure** — `infrastructure/terraform/dr_security.tf` (~300 lines)
  - WI #52: Cosmos DB continuous 7-day backup (azurerm_cosmosdb_account with continuous backup policy, prevent_destroy).
  - WI #55: Customer-Managed Keys (RSA-2048, 90-day rotation, Key Vault access policy for Cosmos DB + Blob Storage).
  - WI #52: Three-tier archival storage (warm-archive + cold-archive containers, lifecycle: warm→cool 30d, cool→archive 90d, delete ~7 years).
  - WI #58: Per-container health probes (liveness + readiness, custom paths/ports for NATS 8222, SLIM Gateway 8443/healthz).
  - WI #59: Zero-downtime rolling deployment (60s connection draining, maintenance window Tuesday 02:00-04:00 UTC).
  - All resources gated by boolean variables (enable_cmk, enable_archival_storage, manage_cosmos_db_account).
  - Updated variables.tf, main.tf health probes, production.tfvars.example.

- [x] **#77-78: Billing Documentation + SLA Updates**
  - WI #77: Published billable conversation spec — `docs-site/docs/billing/billable-conversation-spec.md`. Customer-facing transparency page: conversation definition, start/end conditions, non-billable prefixes, 3-tier consumption, tier allowances, pack pricing, overage rates, alerts, audit trail, dispute resolution.
  - WI #78: Updated SLA document to v0.2.0 — P50 revised to 1,500ms (was 500ms), maintenance window aligned to Tuesday 02:00-04:00 UTC (was Sunday), backup retention updated to continuous PITR with 3-tier archival.
  - Added Billing category to docs-site/sidebars.js.

**Phase 2.5: Persistent Customer Memory — Layers 1-2 Implementation (COMPLETE):**

- [x] **#83-85: CustomerProfileService (Layer 1)** — `customer_profile_service.py` (~520 lines)
  - Profile CRUD, 6 data source update methods, Shopify sync adapter.
  - Consent management (is_consent_granted), stale/empty detection.
  - Tier-aware layer availability (get_available_layers), history depth (get_history_depth_days).
  - Module-level singleton via get_profile_service().

- [x] **#87-88: ConversationVectorizer (Layer 2)** — `conversation_vectorizer.py` (~520 lines)
  - Post-conversation pipeline: transcript → chunking (200-300 tokens) → PII scrub → embedding (text-embedding-3-large, 3072d) → Cosmos DB storage.
  - Semantic search (search_history) with tier-gated depth (Starter 90d, Professional 365d, Enterprise unlimited).
  - Prompt compression (compress_for_prompt) within ~300 token budget.
  - Consent-gated: vectorization and search skip when consent != GRANTED.

- [x] **#86: Response Explainability Framework** — `response_explainability.py` (~510 lines)
  - ResponseDecisionTrace: per-response decision capture (profile, knowledge, memory signals, A/B variant, stages, Critic assessment).
  - DecisionTraceBuilder: fluent builder for incremental trace construction during pipeline execution.
  - Full serialization roundtrip (to_dict/from_dict) for Cosmos DB storage.
  - Data classes: KnowledgeSource, MemorySignal, CriticAssessment, StageAttribution.

- [x] **#97-98/100: Persistent Memory Test Suite** — `tests/persistent_memory/` (3 files, ~1,350 lines)
  - WI #100: Test fixtures — 7 customer IDs, 4 tenant IDs, 6 factory functions (make_profile, make_conversation_messages, make_conversation_doc, make_vector_results, make_preferences, make_bulk_conversations), sample data constants.
  - WI #97: 20 unit tests across 4 layers — L1-01→L1-06 (profile CRUD, tier awareness, Shopify sync, prompt injection, empty/stale detection), L2-01→L2-06 (chunking, compression, consent gating, tier depth), L3-01→L3-04 (trace signals, consent, tier availability, roundtrip), L4-01→L4-04 (enterprise gating, model attribution, consent for training, A/B variant).
  - WI #98: 10 integration tests — CL-01→CL-10 (full stack Enterprise, graceful degradation, layer conflict, new customer, tier upgrade, GDPR deletion, cross-tenant isolation, consent lifecycle, prompt assembly, explainability completeness).
  - All 30 tests passing.

**Session 2026-01-31: Independent Audit Remediation + Test Coverage**

Cursor-generated independent assessment (`independent-progress-assments/cursor-assessment-report.md`) identified 7 findings. All 6 actionable items resolved:

- [x] **CRITICAL: Middleware not wired in main.py** — TenantAuthMiddleware, RateLimitMiddleware were implemented but never registered. All tenant-scoped endpoints (/api/dashboard/*, /api/config/*) would have failed at runtime. Fixed: middleware stack now registers 4 middleware in correct Starlette reverse order (TenantAuthMiddleware → RateLimitMiddleware → TenantConcurrencyMiddleware → CorrelationMiddleware). Added `_startup_tenant_resolution()` event wiring TenantRepository resolvers. Added `api_key_hash` field to TenantDocument and `find_by_api_key_hash()` to TenantRepository.
- [x] **HIGH: Master Plan document lag** — ~45 work items updated from "Pending" to "✅ Complete" with module references.
- [x] **HIGH: PROJECT-PLAN.md stale** — Phase 2.2 expanded from 6 generic rows to 17 specific rows (15 Done, 2 Todo). Phase 2.5 expanded from 9 to 8 rows (4 Done, 4 Todo).
- [x] **HIGH: README.md outdated** — Pricing corrected ($149/$399/$999), add-ons updated (8 items), repo structure fixed (`multi_tenant/`), roadmap milestones synced, legal section updated.
- [x] **MEDIUM: No integration tests** — 95 new tests across 2 suites: `tests/multi_tenant/test_auth_middleware.py` (57 tests: bearer token, auth exemption, API key hashing, shop domain, tenant status, API key verification, tenant context dependency, tier enforcement, rate limiting, config resolution, frozen dataclass). `tests/integrations/test_provisioning_webhooks.py` (38 tests: tenant CRUD lifecycle, idempotency, webhook event handlers, grace periods).
- [x] **LOW: multi-tenant vs multi_tenant directory** — Removed stale `src/multi-tenant/.gitkeep` placeholder.

**Test suite total: 125 tests passing** (30 persistent memory + 57 auth/middleware + 38 provisioning/webhooks).

**Phase 2.2 Key Technical Decisions (Implementation):**
- **multi_tenant (underscore) package:** Created as `multi_tenant/` (valid Python package name). Original `multi-tenant/` placeholder directory removed.
- **PyJWT added to requirements.txt:** `PyJWT>=2.9.0` for Shopify session token verification (HS256).
- **httpx reused:** Already in requirements.txt for Shopify client; now also used for Critic HTTP calls with connection pooling.
- **Atomic counters:** Cosmos DB patch "incr" operations eliminate race conditions present in the Phase 2.1 in-memory stores.
- **Idempotent alerts:** Each usage alert fires once per billing period via the same idempotency key mechanism used for webhook dedup.
- **nats-py reused:** Already in requirements.txt (`nats-py>=2.9.0`). JetStream API used for stream management (WorkQueue retention, file storage, per-subject message limits).
- **Non-fatal NATS startup:** NATS connection failure at startup is logged as warning, not fatal — allows development without NATS running.
- **WorkQueue retention:** JetStream streams use WorkQueue retention (each message consumed once) matching the pipeline's exactly-once processing semantics.
- **DataStoreAdapter protocol:** Uses Python Protocol (structural subtyping) so adapters don't need to inherit a base class — Key Vault and external service adapters can be added later without modifying existing code.
- **Cascading deletion order:** memory_vectors → customer_profiles → conversations → usage → knowledge_bases → preferences → tenants. Dependent data deleted first to maintain referential consistency.
- **Consent denial triggers deletion:** When a customer's consent changes to DENIED, the ConsentManager automatically invokes DataDeletionService to erase Layer 2-4 data, satisfying GDPR Article 17 without manual intervention.
- **PII scrubbing is non-destructive:** PiiScrubber.scrub() returns a new dict — the original payload is never modified, ensuring upstream code can still use the full data internally.
- **contextvars for correlation:** CorrelationContext uses Python `contextvars.ContextVar` for async-safe per-request propagation. Each asyncio task inherits its parent's context, so correlation flows naturally through `await` chains.
- **ASGI-level middleware:** CorrelationMiddleware is a raw ASGI middleware (not Starlette BaseHTTPMiddleware) to avoid the double-read issue and minimize overhead on every request.
- **Console exporter for dev:** Default OTEL_EXPORTER_TYPE="console" in development. Azure Monitor exporter (azure-monitor-opentelemetry) configured at deployment layer via APPLICATIONINSIGHTS_CONNECTION_STRING env var.
- **BaseHTTPMiddleware for concurrency:** TenantConcurrencyMiddleware uses Starlette BaseHTTPMiddleware (not raw ASGI) since it needs to read request.state.tenant_context set by TenantAuthMiddleware — acceptable trade-off as the middleware only reads context, not the body.
- **Lazy tenant gates:** _TenantGate instances (semaphore + queue counter) are created lazily on first request per tenant and cached in a dict. No upfront allocation for tenants that never send traffic.
- **Queue depth as waiting counter:** Queue depth is not a second semaphore but an atomic counter (asyncio primitives) tracking how many requests are waiting to acquire the concurrency semaphore. When waiting count exceeds queue_depth, new requests are immediately rejected with 429.
- **Stage budget vs wall-clock:** PipelineTimeoutBudget tracks both per-stage elapsed time and total wall-clock against the 8s deadline. A stage can complete under its budget but the pipeline still aborts if total time is exhausted.
- **Resolved config pattern:** SystemPromptBuilder receives a resolved PreferencesDocument — it doesn't know whether it's the live config or a test-group override. This keeps the builder single-responsibility and makes it natively compatible with future AI-assisted config rollout ("Smart Rollout") without carrying experiment-specific code.
- **Critic prompt immutability:** The Critic/Supervisor agent's platform base prompt is the only content it receives — _build_tenant_config_section() returns empty string for AgentRole.CRITIC_SUPERVISOR. No merchant config, custom instructions, or customer context can alter Critic behaviour. Combined with CriticPolicy (fail-closed gate), this is defence-in-depth.
- **Custom instructions sandboxed:** Merchant custom_instructions appear only in Response Generator prompts, in a clearly delimited section labelled "advisory — safety rules take precedence". Platform base rules and Critic validation override anything in this block.
- **A/B testing deferred by design:** Market research confirmed A/B testing for AI prompts is niche (only Zendesk offers it natively, behind their highest-priced tier). Agent Red's approach: the builder accepts resolved config, and a future "Smart Rollout" service (Phase 3) can swap which PreferencesDocument is passed based on test group membership. The builder carries zero experiment-specific logic.
- **Dashboard service injection:** usage_dashboard_api.py uses configure_dashboard_services() rather than importing singletons directly. This allows the services (ConversationMeter, ConversationRepository) to be fully initialised with Cosmos DB connections before the dashboard API uses them. Returns HTTP 503 if services aren't wired yet.
- **Tenant isolation on all dashboard endpoints:** tenant_id is always derived from TenantContext (set by TenantAuthMiddleware), never from query parameters or path segments. A merchant cannot query another merchant's usage data.
- **CSV export in-memory:** For launch volumes (≤20K conversations/month for Enterprise), building the CSV in io.StringIO is sufficient. For future high-volume tenants, this can be replaced with streaming chunked responses or async blob generation.

**Session 2026-01-31: Test Coverage Audit + Comprehensive Test Plan + New Work Items Backlog**

Full test coverage audit conducted across all 29 source modules, 30 API endpoints, 4 middleware, and 100 existing work items. Key findings:

- [x] **Test coverage audit report** — 125 tests exist covering ~25-30% of public interfaces. 0 HTTP-level endpoint tests (no FastAPI TestClient). 0 config/dashboard endpoint tests. 0 adversarial/security tests. 0 load/performance tests. 19 of 29 source modules have no tests.
- [x] **Comprehensive test plan created** — `docs/COMPREHENSIVE-TEST-PLAN.md` (~880 tests enumerated with IDs). Organized by priority: P0 launch blockers (~160), P1 pre-launch (~175), P2 launch quality (~135), P3 post-launch (~90), adversarial/security (~45), performance/load (~30), trial/demo (~20), UI-type validation (~100). Proposed test file organization (30 files). Implementation order recommendation.
- [x] **New work items backlog created** — `docs/BACKLOG-NEW-WORK-ITEMS.md` (63 items, WI #101-163). Categories: test infrastructure (#101-107), merchant web UI (#108-118), trial/demo environment (#119-128), SSE streaming (#129-133), pipeline optimization (#134-139), API completeness (#140-147), operational readiness (#148-156), security hardening (#157-163). 10 items overlap with existing Master Plan WIs (superseding). 53 net-new.
- [x] **Competitor P50 benchmarking** — Only Intercom publishes actual latency (7,000ms P50 TTFT). Agent Red target of 1,500ms is 4.7x faster but unvalidated.
- [x] **P50 reduction analysis** — 8 approaches evaluated. SSE streaming highest priority (70-85% perceived reduction, $0 cost). IC+KR parallelization (-800ms, $0). PTU and self-hosting not cost-effective at launch.
- [x] **UI gap analysis** — Platform has NO merchant web UI. All operations require direct API calls across 9+ interface types. Identified as largest gap for merchant experience.
- [x] **Trial/demo environment gap** — No trial tier exists. Prospective customers cannot evaluate product pre-purchase. 14-day trial with conversation cap recommended.

**Key findings from this session:**
- **Competitor latency opacity:** AI customer service industry does not publish latency benchmarks. Only Intercom has a public P50 (7,000ms). This makes Agent Red's 1,500ms target a strong differentiator if validated.
- **SSE streaming is the highest-ROI optimization:** Zero cost, 70-85% perceived latency reduction, Azure OpenAI supports it natively. Must design Critic validation strategy for streaming (WI #130).
- **Merchant web UI is the largest product gap:** All 30 API endpoints, 10 config endpoints, and 5 dashboard endpoints exist but have no frontend. Self-service operations require curl/Postman.
- **Test infrastructure is the prerequisite for all testing work:** No pyproject.toml, no conftest.py, no CI pipeline. Must be built first (WI #101-104).

**Session 2026-01-31 (cont.): P0 Test Suite Implementation — 379 tests passing**

Test infrastructure (WI #101-104) and all 8 P0 launch-blocker test groups implemented. 254 new tests created across 10 new test files.

- [x] **WI #101: pyproject.toml** — pytest configuration with asyncio_mode=auto, testpaths, markers (unit, integration, slow)
- [x] **WI #102: requirements-test.txt** — pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx
- [x] **WI #103: conftest.py** — MockContainerProxy (CRUD + patch incr), MockCosmosManager, MockQueryIterator, mock_cosmos/mock_nats/mock_keyvault/mock_circuit_breakers fixtures, FastAPI app_client with full middleware stack, AuthenticatedClient wrapper, tenant context + document factories, API key helpers
- [x] **WI #104: GitHub Actions CI** — .github/workflows/python-tests.yml (Python 3.12/3.14, pip cache, pytest with JUnit XML)
- [x] **§4.1: test_http_billing.py (35 tests)** — All 9 billing routers (checkout, packs, portal, usage, webhooks, Shopify billing, provisioning), request validation, error handling
- [x] **§4.2: test_middleware_pipeline.py (25 tests)** — Full middleware stack via TestClient (auth, rate limit, concurrency, correlation), tier status validation, auth exemption
- [x] **§4.3: test_conversation_meter.py (38 tests)** — Billable conversation spec (CM-01→CM-30 + 8 spec constants), 3-tier consumption, idempotent metering, alerts, reconciliation, idle scanner
- [x] **§4.4: test_critic_policy.py (25 tests)** — Fail-closed gate (CP-01→CP-20 + 5 extras), circuit breaker state machine, SAFE_FALLBACK_MESSAGE, audit logging, timeout budget
- [x] **§4.5: test_cosmos_repository.py (61 tests)** — TenantScopedRepository CRUD enforcement (CR-01→CR-25 + 36 supplements), all 11 document models, 7 enums, TIER_DEFAULTS, 9 collections, DiskANN vector index, PlatformScopedRepository
- [x] **§4.6: test_health.py (15 tests)** — /health liveness, /ready readiness (NATS, circuit breakers, Key Vault), auth exemption, startup events
- [x] **§4.7: test_stripe_catalog.py (23 tests)** — StripeCatalog from JSON, tier/pack/addon models, price_id_for_interval(), addon tier validation
- [x] **§4.8: test_usage_consumption.py (13 tests)** — End-to-end 3-tier flow (included → pack FIFO → Stripe overage), pack expiry, billing period reset

**Key technical decisions from this session:**
- **pytest-asyncio asyncio_mode=auto:** All `async def` test methods run automatically without `@pytest.mark.asyncio`. Required for Python 3.14 compatibility (asyncio.get_event_loop() deprecated in MainThread).
- **MockContainerProxy with patch "incr":** In-memory mock supports Cosmos DB atomic counter increments, avoiding need for real database in unit tests.
- **app_client fixture pattern:** FastAPI TestClient with full middleware stack active (auth → rate limit → concurrency → correlation). External services (NATS, Key Vault, circuit breakers) patched at module level. Tenant resolution wired after TestClient startup to avoid race with mocked _startup_tenant_resolution.
- **AuthenticatedClient wrapper:** Convenience class injecting API key headers on every request. Starter/Professional/Enterprise pre-authenticated clients via fixtures.
- **inspect.iscoroutinefunction over asyncio.iscoroutinefunction:** Python 3.14 deprecates the asyncio version; using inspect module avoids DeprecationWarning.

**Test suite total: 379 tests passing in ~2s** (10 test files created this session + 3 pre-existing).

**Session 2026-01-31: UI/UX Competitive Analysis + Design Specification**

Full UI/UX design session covering competitive analysis, architecture decisions, and detailed specifications for all three frontend deliverables (chat API, widget, admin dashboard). 7 architecture decisions approved. 24 new work items identified (WI #164-187).

- [x] **Competitive analysis:** 5 highest-install Shopify AI customer service apps (Tidio, Gorgias, Zendesk, Intercom, Re:amaze) analysed across 10 dimensions. Full feature matrices in `docs/research/UI-UX-COMPETITIVE-ANALYSIS.md`. Critical finding: Agent Red has zero frontend — the most critical gap despite having the most sophisticated AI backend.
- [x] **Decision UI-1: Frontend framework selection** — Preact for widget (~4.5KB gzip), React + Polaris + App Bridge for Shopify admin, React + custom design system for standalone admin. Shared component library between both admin shells.
- [x] **Decision UI-2: Widget delivery** — Shopify Theme App Extension (app embed block) for Shopify merchants + universal JS snippet for non-Shopify.
- [x] **Decision UI-3: Widget DOM isolation** — Shadow DOM (closed) for launcher button + iframe for conversation panel. Same architecture as Zendesk.
- [x] **Decision UI-4: Hybrid communication protocol** — HTTP POST (client→server messages) + SSE (server→client AI streaming) + WebSocket (bidirectional for typing, presence, human-agent chat). All three required at launch — human-agent chat after escalation needs a bidirectional channel.
- [x] **Decision UI-5: SSE stream-then-validate** — Stream AI tokens to customer in real-time, Critic validates post-stream. Rejection triggers `event: retracted` replacing displayed text with safe fallback. ~800ms exposure window at P50. Alternative (buffer until Critic approves) penalizes >99% of valid responses.
- [x] **Decision UI-6: Publishable widget key** — `pk_live_{hash}_{random}` for client-side auth scoped to `/api/chat/*` only. Third auth path alongside Shopify JWT and API keys. Optional HMAC customer identity verification.
- [x] **Decision UI-7: Dual admin frontends** — Shopify embedded admin (Polaris + App Bridge) AND standalone admin (React + custom design) required because Stripe-direct merchants have no Shopify account.
- [x] **Chat API specification (Phase 1):** `src/chat/` — models.py, session.py, pipeline.py, endpoints.py. 6 endpoints: start conversation, send message, SSE stream, get state, end conversation, WebSocket.
- [x] **Widget specification (Phase 2):** Preact + TypeScript, Shadow DOM launcher + iframe panel, ~15-20KB gzip bundle. Component tree, state management, transport layer, JavaScript SDK public API, Shopify Liquid template for Theme App Extension.
- [x] **Admin dashboard specification (Phases 4-6):** 9 shared components (OnboardingWizard, ConfigEditor, UsageDashboard, ConversationInbox, KnowledgeBaseManager, AnalyticsOverview, BillingPortal, WidgetConfigurator, TeamManager). Shopify shell (7 nav items, App Bridge integration). Standalone shell (API key login, custom sidebar, Stripe billing). Page-to-API mapping complete — 4 of 9 components fully supported by existing endpoints; 4 need new backend APIs.
- [x] **Architecture decisions document:** `docs/architecture/UI-UX-ARCHITECTURE-DECISIONS.md` — all 7 decisions, full specifications, 24 new work items (WI #164-187), build order.
- [x] **CLAUDE.md working style addition:** "Option Evaluation Criteria" subsection — prioritize (1) implementation quality, (2) desirability, (3) downstream confidence. Avoid "simpler/harder" generalizations. Token/time usage not meaningful concerns.

**Key findings from this session:**
- **Agent Red has zero UI** — the most critical product gap. All 30+ API endpoints have no frontend. Merchants cannot self-serve any operation without curl/Postman.
- **Human-agent chat is not optional** — escalated conversations need a bidirectional channel. WebSocket required at launch, not a future enhancement.
- **Two admin frontends required** — Stripe-direct merchants cannot access Shopify embedded admin. Both shells share a component library to avoid duplication.
- **4 existing endpoints groups fully support admin pages** — Onboarding, Config Editor, Usage Dashboard, and Billing Portal need zero new backend work. ConversationInbox, KnowledgeBase, Analytics, and Team need new APIs.
- **Bundle size competitive advantage** — Widget at ~15-20KB gzip vs Tidio ~40-60KB, Intercom ~80-100KB.
- **Only Intercom publishes latency** — 7,000ms P50 TTFT. Agent Red target 1,500ms is 4.7x faster.

**Session 2026-01-31: Backend Implementation Sprint (Chat API + Admin APIs + Security + Streaming)**

Implemented 20+ work items across 3 sessions. Major deliverables:

- [x] **WI #164-169/#182: Chat API (Phase 3.0 Build Phase 1)** — `src/chat/` package (4 modules, ~1,700 lines). models.py (StreamEvent SSE format, 7 event types), session.py (ConversationSession lifecycle), pipeline.py (6-agent orchestrator with stream-then-validate), endpoints.py (6 routes: start, message, SSE stream, state, end, WebSocket).
- [x] **WI #170: Widget key authentication** — `pk_live_{hash}_{random}` publishable keys scoped to `/api/chat/*`. Third auth path in auth.py. find_by_widget_key_hash() in TenantRepository.
- [x] **WI #119: Trial tier** — TenantTier.TRIAL enum, TIER_DEFAULTS for trial (25 conv, 2 rpm, 1 concurrent, 7-day history, Layer 1 only), TrialConfigDocument schema, trial-aware provisioning in provisioning.py.
- [x] **WI #171: Admin Conversation Inbox API** — `admin_conversation_api.py` (5 endpoints: list, detail, messages, assign, notes).
- [x] **WI #175: Admin Knowledge Base API** — `admin_knowledge_api.py` (5 endpoints: CRUD + search).
- [x] **WI #176-178: Admin Analytics API** — `admin_analytics_api.py` (3 endpoints: summary, intents, gaps).
- [x] **WI #179: Admin Team Management API** — `admin_team_api.py` (5 endpoints: list, invite, detail, update, remove). TeamMemberDocument + TeamMemberRepository added.
- [x] **WI #180: Admin GDPR API** — `admin_gdpr_api.py` (5 endpoints: export, delete, consent CRUD).
- [x] **WI #35: Shopify GDPR webhooks** — `shopify_gdpr_webhooks.py` (3 mandatory endpoints with HMAC-SHA256 verification).
- [x] **WI #51: TenantUsageMonitor** — `tenant_usage_monitor.py` (~500 lines). Progressive throttling: Watch→Warn→Throttle→Isolate. 5-min rolling window, sticky de-escalation.
- [x] **WI #157-159: Security middleware** — `security_middleware.py` (~297 lines). RequestBodyLimitMiddleware (1MB, ASGI), JsonDepthValidationMiddleware (50 levels), SecurityHeadersMiddleware (OWASP).
- [x] **WI #158: Rate limit response headers** — X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset on every response.
- [x] **WI #140: API versioning** — `api_versioning.py`. ApiVersionMiddleware (X-API-Version: 1.0.0), deprecation notice support.
- [x] **WI #141: Audit log query API** — `admin_audit_api.py` (2 endpoints: paginated query + CSV export).
- [x] **WI #148: Health check enhancements** — /health and /ready include API version, usage monitor health, SSE connection stats.
- [x] **WI #149: Structured logging** — `structured_logging.py`. StructuredJsonFormatter (prod JSON-per-line), DevelopmentFormatter (colored). Replaces basicConfig in main.py.
- [x] **WI #129: SSE streaming infrastructure** — `sse_manager.py` (~280 lines). SSEConnectionManager: 15s heartbeat keepalive, Last-Event-ID reconnection, per-tenant connection limits, event buffering (100 events/conversation).
- [x] **WI #130: Critic validation for streaming** — Stream-then-validate pattern already in pipeline.py (Decision UI-5). Tokens stream in real-time, Critic validates post-stream, retracted event replaces text on rejection.
- [x] **WI #47: KEDA auto-scaling Terraform profiles** — Night schedule cron scaler for non-critical containers (Escalation, Analytics → 0 replicas 22:00-06:00 UTC). Gated by enable_night_scaling variable. Scaling metrics summary locals.

**Key technical decisions from this session:**
- **8 middleware layers**: TenantAuth → RateLimit → Concurrency → JsonDepth → Correlation → BodyLimit → ApiVersion → SecurityHeaders. Starlette reverse registration order.
- **ASGI vs BaseHTTPMiddleware**: Raw ASGI for body size limit (intercept before full read) and security headers (no body read needed). BaseHTTPMiddleware for JSON depth (needs request.body()).
- **SSE heartbeat interval**: 15s `:ping` comments to prevent Azure App Gateway 60s idle timeout.
- **SSE reconnection**: Events buffered per conversation with monotonic sequence IDs. Last-Event-ID header replays missed events. Buffer expires after 5 minutes of inactivity.
- **Night scaling gated**: `enable_night_scaling = false` by default. Non-critical containers scale to 0 during 22:00-06:00 UTC when enabled. ~$20-30/mo savings.
- **Structured logging replaces basicConfig**: Production uses JSON-per-line format for Application Insights ingestion. Development uses colored human-readable format. Controlled by ENVIRONMENT env var.
- **Progressive throttling sticky de-escalation**: Escalation level drops by at most one step per evaluation cycle to prevent rapid oscillation between Normal and Isolate.

**Session 2026-02-01: Widget Frontend Build + Product Rename + Brand Correction**

Comprehensive widget frontend implementation session. Product renamed from "Customer Engagement" to "Customer Experience" across 65+ files. Brand primary color corrected to #C41E2A. 24 widget customization fields added to backend config. Full widget frontend built (20 files, ~3,200 lines). Tidio audit completed with ~70 controls cataloged.

- [x] **Tidio competitive audit** — ~70 merchant-facing controls, 6 workflows, pricing analysis, docs style review. All items that could not be verified from training data marked [VERIFY] for live-source validation.
- [x] **Widget config gap analysis** — Existing 34 config fields were all AI behavior controls with ZERO widget appearance controls. 22 launch-blocking widget customization fields identified, deferral list agreed upon.
- [x] **Widget customization schema (24 fields)** — Added to tenant_config_schema.py (OnboardingStep.WIDGET_APPEARANCE = step 9), cosmos_schema.py (PreferencesDocument), tenant_config_processor.py (_PREFS_DIRECT_FIELDS). Visual (12 fields), behavior (9 fields), content/targeting (3 fields).
- [x] **Product rename: Customer Engagement → Customer Experience** — Executed across 65+ files (source, config, infra, legal, branding, website, docs, CLAUDE.md). Preserved: AGNTCY upstream name, GitHub repo slugs, directory paths.
- [x] **Brand primary color correction** — #C83232 → #C41E2A (canonical from color-palette.html).
- [x] **New logo assets acknowledged** — Horizontal lockup (PNG/SVG/WebP), no-margin variant, AR monogram, dark-background white-text variant.
- [x] **WI #172-174: Widget frontend (Build Phase 2)** — Complete `widget/` project (20 files, ~3,200 lines):
  - Project scaffold: package.json (Preact + Vite + TypeScript), tsconfig.json, vite.config.ts (IIFE build, terser, ~15-20KB gzip target)
  - Theme system: tokens.ts (~70 design tokens, WidgetConfig→DesignTokens resolution, light/dark modes, WCAG contrast utilities, Zapier-derived spacing/typography)
  - Locale: en.ts (34 strings in Locale interface, merchant-overridable, i18n-ready)
  - State: store.ts (reactive Store class, Message/WidgetState interfaces, streaming/retraction support)
  - Transport: http.ts (widget key auth, 5 API methods), sse.ts (6 SSE event types, auto-reconnect with exponential backoff), ws.ts (WebSocket typing/presence, ping keepalive, debounced typing indicator)
  - Components: Launcher.tsx (Shadow DOM, unread badge), Panel.tsx (root container, SSE/WS lifecycle, view routing), Header.tsx (agent info, avatar, status dot), MessageList.tsx (auto-scroll, day separators, typing dots, greeting), MessageBubble.tsx (customer/agent/system, streaming cursor, retraction), InputBar.tsx (auto-grow textarea, Enter-to-send, file attach, branding), PreChatForm.tsx (configurable fields, validation), ChatRating.tsx (thumbs up/down, comment), OfflineForm.tsx (name/email/message form)
  - Entry: index.ts (boot from script tag data attributes, Shadow DOM launcher mount, iframe panel creation, page rules, mobile detection, auto-open, sound notification, AgentRed SDK on window)
  - Dev: dev.html (simulated storefront with SDK controls)

**Key technical decisions from this session:**
- **Tidio is the primary functional reference** — completeness, language, merchant workflows, widget customization controls.
- **Zapier is the visual styling reference** — layouts, buttons, forms, spacing, font sizes, borders.
- **Persistent Customer Memory is the launch pillar** — one key differentiator to drive affiliate/promoter narrative.
- **Full breadth of named controls, no arbitrary CSS at launch** — match Tidio control count without custom CSS injection.
- **Shadow DOM (closed) for launcher** — merchant CSS cannot leak into widget styling.
- **iframe for conversation panel** — full DOM isolation, same architecture as Zendesk (Decision UI-3).
- **3-channel transport** — HTTP POST (messages), SSE (AI streaming), WebSocket (typing/presence) all implemented.
- **Stream-then-validate** — tokens stream in real-time, Critic retraction replaces text with `retracted` SSE event (Decision UI-5).
- **SDK on `window.AgentRed`** — open/close/toggle/hide/show/destroy/setUnreadCount/isOpen.
- **Page rules** — glob pattern matching on window.location.pathname for per-page widget visibility.
- **Sound notification** — AudioContext beep (800Hz, 150ms) when unread messages arrive while widget is closed.
- **Design tokens only** — components never hardcode visual values; theme layer cleanly separated for future design specialist.
- **Locale separation** — all strings in en.ts, merchant overrides applied at boot; translator adds new locale files without touching components.

**Key design decisions confirmed with owner:**
- **Merchant widget customization** is the primary UX concern (not Agent Red's own UI). Merchants must be able to style the widget to suit their own storefront.
- **Equal Tidio in every aspect** — retain one key differentiator (Persistent Customer Memory) and substantially lower prices.
- **Iterative working style confirmed** — one item at a time, honest assessment, concrete deliverables with approval before implementation, aggressive scope cutting.

**593 backend tests passing.** Widget is ready for `npm install && npm run dev`.

**Sessions 2026-02-01: Autonomous Implementation Sprint — Widget Build + P1 Tests + Frontend + Operational Readiness**

Three consecutive autonomous sessions completed all remaining high-priority work items. Summary of completed work:

- [x] **Widget build validation** — `npm install && npm run build` successful. IIFE bundle output confirmed. TypeScript compilation clean.
- [x] **P1 pre-launch tests COMPLETE** — 214 new tests across 10 groups (NATS isolation, GDPR services, OpenTelemetry, pipeline resilience, SystemPromptBuilder, tenant config, provisioning lifecycle, Shopify billing, persistent memory, dashboard API). All passing.
- [x] **Phase 3.0 Build Phase 3: Shopify Theme App Extension** — `extensions/agent-red-chat/` with Liquid template, extension manifest, placeholder widget bundle.
- [x] **Phase 3.0 Build Phase 4: Shared admin components** — `admin/shared/` with 9 components + hooks + types (~5,400 lines). OnboardingWizard, ConfigEditor, UsageDashboard, ConversationInbox, KnowledgeBaseManager, AnalyticsOverview, BillingPortal, WidgetConfigurator, TeamManager.
- [x] **Phase 3.0 Build Phase 5: Shopify admin shell** — `admin/shopify/` with Polaris + App Bridge integration, 7 pages, Save Bar hook (~2,700 lines).
- [x] **Phase 3.0 Build Phase 6: Standalone admin shell** — `admin/standalone/` with API key login, custom sidebar layout, 7 pages (~2,800 lines).
- [x] **Phase 2.1 remaining** — Session tokens, App Bridge Save Bar — completed during Build Phase 5 (useSaveBar.ts hook, session token auth already in auth.py).
- [x] **Trial environment COMPLETE (WI #119-128)** — `trial_management.py` (~1,200 lines): trial tier in TIER_DEFAULTS, 14-day trial lifecycle, demo data seeding, conversion flow, expiry notifications, trial-to-paid upgrade path.
- [x] **Security hardening COMPLETE (WI #157-163)** — `security_hardening.py` (~570 lines): input sanitization, CORS configuration, CSP headers, session validation. Plus security_middleware.py enhancements (body size, JSON depth, security headers, rate limit headers, SLA latency recording).
- [x] **Pipeline optimization COMPLETE (WI #134-139)** — IC+KR parallelization, response caching, connection pool tuning in pipeline_resilience.py.
- [x] **Operational readiness COMPLETE (WI #148-156)**:
  - WI #148-150: Deployment, DR, and maintenance runbooks (`docs/operations/`)
  - WI #151: SLA monitoring service (`sla_monitoring.py`, ~390 lines)
  - WI #152: KEDA night scaling profiles in Terraform
  - WI #153: Archival pipeline — Hot→Warm Parquet to Azure Blob (`archival_pipeline.py`, ~750 lines)
  - WI #154: Data retention enforcement (`data_retention.py`, ~380 lines)
  - WI #155: Cost model calculator (`cost_model.py`, ~370 lines)
  - WI #156: Option C geo-replication upgrade path (`docs/operations/OPTION-C-UPGRADE-PATH.md`)
- [x] **Additional work items (WI #188-195)**:
  - WI #188: Competitive pricing verification — ALL 5 competitors verified against live pricing pages. Agent Red pricing advantage corrected from 2-14x to **4-21x** (Gorgias and Zendesk original estimates were drastically low).
  - WI #189/193: Azure Blob Storage + pyarrow dependencies added to requirements.txt
  - WI #190: Scheduled Container App Jobs (cron) for retention (03:00 UTC) and archival (04:00 UTC)
  - WI #191: SLA latency recording in SecurityHeadersMiddleware + Server-Timing response header
  - WI #192: Alert delivery service (`alert_delivery.py`, ~695 lines) — webhook, dashboard, log channels
  - WI #194: Test coverage for archival (15), retention (15), SLA (25), cost model (20) — 75 new tests
  - WI #195: Unawaited coroutine warnings fixed in test_pipeline_resilience.py

**777 tests passing, 0 warnings.** All middleware wired in main.py. All Terraform updated.

### Pending
- [ ] Phase 2.1: Creative assets (Shopify App Store icon, screenshots, demo video) — blocked on design
- [ ] Phase 2.5: Layer 3 — PatternExtractionService (Professional+, work items #90-92)
- [ ] Phase 2.5: Layer 4 — Fine-tuning pipeline (Enterprise add-on, work items #93-96)
- [ ] Phase 2.5: 5 A/B production tests (work items from Decision #32)
- [ ] **Backlog items (WI #101-163) — remaining:** #105-107 (CI improvements: coverage reports, parallel test jobs, branch protection rules), #108-118 (merchant web UI — now largely covered by admin/ frontend), #131-133 (SSE enhancements: client-side retry, event compression, multi-tab coordination), #142-146 (API completeness: pagination standardization, bulk operations, webhook retry, API rate limit headers — partially done)
- [ ] **P2 launch quality tests (~135 tests):** See COMPREHENSIVE-TEST-PLAN.md §6
- [ ] **P3 post-launch tests (~90 tests):** See COMPREHENSIVE-TEST-PLAN.md §7
- [ ] **Adversarial/security tests (~45 tests):** See COMPREHENSIVE-TEST-PLAN.md §8
- [ ] **Performance/load tests (~30 tests):** See COMPREHENSIVE-TEST-PLAN.md §9
- [ ] **Integration testing** — End-to-end flows with real Stripe test mode, Shopify partner sandbox
- [ ] **Admin frontend build validation** — Install dependencies, TypeScript compilation, bundle output for admin/shopify and admin/standalone
- [ ] **Widget bundle → Theme App Extension** — Copy built widget IIFE into extensions/agent-red-chat/assets/
- [ ] **Shopify App Store submission** — Requires: creative assets, GDPR webhooks (done), session tokens (done), App Bridge Save Bar (done)

---

## Requirements Summary

| Question | Answer |
|----------|--------|
| AGNTCY relationship | Arms-length, third-party consumer |
| Commercial differentiators | All 5 (multi-tenant, AI, integrations, white-label, persistent customer memory) |
| Timeline | Q1 2026 (8-12 weeks) |
| Budget | $500-1,000/month |
| Pricing | $149/$399/$999 base + metered AI usage (82-93% gross margin) |
| Legal entity | VanDusen & Palmeter, LLC (Delaware) |
| DBA | Remaker Digital |
| GitHub org | Remaker-Digital (private repo) |
| Dev environment | Windows 11, VS Code, Docker, Python 3.12+ |
| Materials scope | Phase 1-2 only (MVP) |
| Brand assets | Core system complete (Phase 1.1); favicon, social, email templates pending |
| CI/CD | Hybrid (GitHub Actions + Azure DevOps) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-01*
*Version: 13.0.0*
