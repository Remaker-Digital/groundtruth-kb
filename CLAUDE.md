# CLAUDE.md - Agent Red Customer Engagement

This document provides context and guidance for AI assistants working on the Agent Red Customer Engagement commercial project.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Engagement |
| **Brand Name** | Agent Red Customer Engagement |
| **Release** | Launch 1.0 |
| **Type** | Commercial SaaS Product |
| **Status** | Phase 2.5 Planning Complete — Persistent Customer Memory Documented |
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

**Per-conversation AI cost:** ~$0.007 (GPT-4o response generation = 94.5% of total)

**Infrastructure costs (shared, multi-tenant):**
- Shared platform (Container Apps, Cosmos DB, App Gateway, etc.): ~$200-400/mo total
- Per-tenant marginal cost at 10+ tenants: ~$13-41/mo

**Gross margin at list price:** 82-93% across all scenarios (base fee + overage)

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
- Affiliate program

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
- [ ] Favicon and app icons — spec defined in LOGO-SPEC.md
- [ ] Social media assets
- [ ] Email templates

### Brand Name Usage
- **Full:** Agent Red Customer Engagement
- **Short:** Agent Red
- **Product Line:** Agent Red (parent) → Customer Engagement (product)

---

## Project Structure

```
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\
│
├── CLAUDE.md                       # This file - AI assistant guidance
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
│
├── src/                            # Commercial source code
│   ├── multi-tenant/               # Tenant management
│   ├── integrations/               # Enterprise integrations
│   ├── ai-features/                # Advanced AI
│   └── white-label/                # Customization
│
├── infrastructure/                 # Deployment infrastructure
│   └── terraform/                  # IaC for Azure
│
├── website/                        # Marketing website
│   └── content/                    # Page content (markdown)
│
├── docs/                           # Documentation
│   ├── architecture/               # Technical architecture
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
| PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md | docs/architecture/ | Persistent Customer Memory research foundation |
| PERSISTENT-CUSTOMER-MEMORY-METRICS.md | docs/architecture/ | Test cases, metrics, and A/B testing framework |

---

## Self-Service Legal Tools

| Document | Tool | Cost |
|----------|------|------|
| Terms of Service | Termly | $15-25/mo |
| Privacy Policy | Termly | Included |
| Cookie Policy | Termly | Included |
| Data Processing Agreement | iubenda | $27/mo |

---

## Working with This Project

### Starting a New Session

```
Continue work on Agent Red Customer Engagement commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, docs/PROJECT-PLAN.md
Current status: Phases 0-1.4 complete. Phase 2.1 platform decision complete (dual-channel: Shopify App Store + Stripe). Persistent Customer Memory feature fully documented and propagated across all 19 files (Phase 2.5 planning complete). Implementation tasks next.
Next up: Phase 2.1 implementation — Stripe account setup, product catalog, Checkout integration, webhook handler, Shopify Billing API integration, App Store listing.
Please review PROJECT-PLAN.md (Phase 2.1 task list) and proceed with the next implementation item, presenting one work item at a time for review per the iterative working style documented in CLAUDE.md.
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

### Adding Commercial Features

1. Create features in `src/` exclusively
2. Document in `docs/architecture/`
3. Add copyright notice to all new files
4. Test integration patterns independently
5. Never commit AGNTCY source code into this repo

---

## Current Status (2026-01-30)

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

**Phase 2.1: E-Commerce Store (In Progress)**
- [x] Three-way platform evaluation (Stripe vs Shopify App Store vs Paddle) — docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md
- [x] Decision: Dual-channel (Shopify App Store primary + Stripe direct). Paddle rejected.
- [x] Approval process and partner growth path documented (Appendices A & B)
- [ ] Stripe account setup, Products, Prices, Coupons in test mode
- [ ] Stripe Checkout integration for plan selection
- [ ] Stripe webhook handler (subscription lifecycle → tenant provisioning)
- [ ] Metered usage reporting to Stripe
- [ ] Shopify Billing API integration
- [ ] Shopify App Store listing (description, screenshots, demo)
- [ ] App Store review submission
- [ ] Conversation pack purchase flow
- [ ] Unified webhook handler (both channels → provisioning)
- [ ] Stripe Tax, Stripe Customer Portal, Rewardful affiliate setup
- [ ] Test checkout flows (both channels)

**Phase 2.5: Persistent Customer Memory (Planned)**
- [ ] Design customer preference profile schema
- [ ] Implement dynamic system prompt builder (Layer 1)
- [ ] Build tenant-partitioned vector index for transcripts (Layer 2)
- [ ] Integrate memory framework — Mem0 or custom (Layer 3)
- [ ] Build profile extraction pipeline
- [ ] Implement few-shot example retrieval
- [ ] Build fine-tuning pipeline (Layer 4, Enterprise add-on)
- [ ] Create metrics dashboard (KPIs from PERSISTENT-CUSTOMER-MEMORY-METRICS.md)
- [ ] A/B testing framework integration

### Pending
- [ ] Phase 2.2: Multi-tenant infrastructure (architecture doc required first)

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
*Last Updated: 2026-01-30*
*Version: 4.3.0*
