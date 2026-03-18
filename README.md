# Agent Red Customer Experience

> **AI-Powered Customer Service Platform for E-Commerce**
>
> Commercial SaaS product by [Remaker Digital](https://remakerdigital.com)

---

## Quick Links

| Resource | Link |
|----------|------|
| **Repository** | [mike-remakerdigital/agent-red](https://github.com/mike-remakerdigital/agent-red) |
| **Milestones** | [Issues](https://github.com/mike-remakerdigital/agent-red/issues) (M1-M8) |
| **Project Plan** | [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) |
| **AI Assistant Guide** | [`CLAUDE.md`](CLAUDE.md) |
| **Commercial Proposal** | [`docs/COMMERCIAL-SAAS-PROPOSAL.md`](docs/COMMERCIAL-SAAS-PROPOSAL.md) |
| **Product Features (RAG)** | [`docs/PRODUCT-FEATURES-RAG.md`](docs/PRODUCT-FEATURES-RAG.md) |
| **Baseline Verification** | [`docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md`](docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md) |

---

## Overview

Agent Red Customer Experience is a commercial SaaS platform that helps e-commerce businesses automate customer support with intelligent AI agents. It combines six specialized AI agents that work together to understand, respond to, and resolve customer issues instantly — while seamlessly escalating complex cases to your team.

### Key Capabilities

- **Instant Responses** — P95 latency under 2 seconds
- **70%+ Automation** — Handle routine inquiries automatically
- **Smart Escalation** — Complex issues routed to humans with full context
- **Multi-Language** — English, French (CA), Spanish support
- **Shopify Native** — Deep integration with real-time order and product data
- **Persistent Customer Memory** — Every conversation builds on the last; four-layer personalization from context injection to dedicated model training
- **Enterprise Ready** — Multi-tenant isolation, usage metering, API key management

---

## Architecture

Agent Red is built on the open-source [AGNTCY Customer Engagement Platform](https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service) foundation, with proprietary commercial extensions. The relationship is strictly arms-length — Agent Red consumes AGNTCY only through its public GitHub repository and published SDK (`agntcy-app-sdk` on PyPI).

### Six Specialized AI Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| Intent Classification | Route customer queries (17 intents) | GPT-4o-mini |
| Knowledge Retrieval | Search products, FAQs, policies | text-embedding-3-large |
| Response Generation | Craft personalized responses | GPT-4o |
| Escalation | Detect cases needing humans | GPT-4o-mini |
| Analytics | Monitor performance metrics | GPT-4o-mini |
| Critic/Supervisor | Validate content safety | GPT-4o-mini |

### Commercial Differentiators (Agent Red Exclusive)

| Feature | Description |
|---------|-------------|
| **Multi-Tenant SaaS** | Tenant isolation, subscription management, usage metering |
| **Advanced AI** | Premium model access, fine-tuned models, A/B testing |
| **Enterprise Integrations** | Salesforce, SAP, ServiceNow, custom connectors, SSO |
| **White-Label** | Complete branding removal, custom domains, CSS theming |
| **Persistent Customer Memory** | Four-layer personalization: context injection, conversation RAG, cross-session learning, per-customer fine-tuning |

---

## Repository Structure

```
Agent Red Customer Experience/
├── CLAUDE.md                       # AI assistant guidance (canonical status)
├── README.md                       # This file — project hub
├── Dockerfile                      # Container build
├── docker-compose.yml              # Local dev stack (API + NATS)
├── requirements.txt                # Python dependencies
│
├── src/                            # Commercial source code
│   ├── main.py                     # FastAPI app entrypoint (9 routers, 30 endpoints)
│   ├── integrations/               # Billing & platform integrations (Stripe, Shopify)
│   ├── multi_tenant/               # Multi-tenant infrastructure (21 modules)
│   ├── ai-features/                # Advanced AI capabilities (future)
│   └── white-label/                # Customization engine (future)
│
├── tests/                          # Test suites
│   └── persistent_memory/          # Persistent Customer Memory tests (30 tests)
│
├── config/                         # Configuration files
│   └── stripe_product_ids.json     # Stripe test-mode product/price IDs
│
├── infrastructure/                 # Deployment infrastructure
│   └── terraform/                  # IaC for Azure
│
├── website/                        # Marketing website
│   └── content/                    # Page content (markdown)
│
├── docs/                           # Documentation
│   ├── PROJECT-PLAN.md             # Launch 1.0 milestones and tasks
│   ├── Master-Plan-Review-01-30-2026.md  # Architecture review (32 decisions, 100 work items)
│   ├── COMMERCIAL-SAAS-PROPOSAL.md # Full business analysis
│   ├── PRODUCT-FEATURES-RAG.md     # Complete feature reference
│   ├── architecture/               # Technical architecture
│   ├── shopify/                    # Shopify App Store materials
│   ├── guides/                     # How-to guides
│   └── api/                        # API reference
│
├── docs-site/                      # Docusaurus documentation site
│
├── branding/                       # Brand assets
├── legal/                          # Legal documents (ToS, Privacy, SLA, DPA)
│
└── scripts/                        # Automation scripts
    ├── stripe/                     # Stripe catalog + tax migration scripts
    └── deploy/                     # Deployment scripts
```

---

## Pricing

Platform Fee + Metered AI Usage — each tier includes a monthly conversation allowance with per-conversation overage.

| Tier | Monthly | Annual (17% off) | Included Conv/mo | Overage Rate |
|------|---------|-------------------|------------------|--------------|
| **Starter** | $149 | $124/mo ($1,490/yr) | 1,000 | $0.04/conv |
| **Professional** | $399 | $332/mo ($3,990/yr) | 5,000 | $0.025/conv |
| **Enterprise** | $999 | $832/mo ($9,990/yr) | 20,000 | $0.015/conv |

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

---

## Production Infrastructure

Deployed on Azure (East US 2):

| Resource | Service |
|----------|---------|
| Compute | Azure Container Apps + Container Instances |
| Database | Cosmos DB (Serverless, vector search) |
| AI | Azure OpenAI Service (GPT-4o, GPT-4o-mini, text-embedding-3-large) |
| Networking | Application Gateway (TLS, WAF) |
| Monitoring | Application Insights (OpenTelemetry) |
| Secrets | Key Vault (Managed Identity) |
| Registry | Azure Container Registry |

**Verified Performance:** 3,071 req/s throughput, <2s P95 latency, 99.95% uptime SLA.

---

## Development

### Prerequisites

- Windows 11
- Python 3.12+
- Node.js >= 20 (required for widget and admin SPA builds)
- Docker Desktop
- Git + GitHub Desktop
- Visual Studio Code

### Local Setup

```bash
# Clone the repository
git clone https://github.com/mike-remakerdigital/agent-red.git
cd agent-red

# Copy environment template
cp .env.example .env.local

# Build UI artifacts (required before Docker build — no Node.js in container)
cd widget && npm install && npm run build && cd ..
cd admin/standalone && npm install && npm run build && cd ..
cd admin/provider && npm install && npm run build && cd ..
cd admin/shopify && npm install && npm run build && cd ..

# Start local dev stack (API + NATS JetStream + Redis)
docker compose up -d

# Verify services
curl http://localhost:8080/health    # API (host:8080 → container:8000)
curl http://localhost:8222/healthz   # NATS monitoring
```

> **Without Docker:** Run uvicorn directly on port 8000 (`uvicorn src.main:app --reload --port 8000`). Vite dev servers for admin SPAs proxy to `localhost:8000` by default.

### Subproject Setup

| Directory | Stack | Dev Server | Package Manager |
|-----------|-------|------------|-----------------|
| `widget/` | Preact + Vite | `npm run dev` (port 5173) | npm |
| `admin/provider/` | React + Mantine + Vite | `npm run dev` (port 3400) | npm |
| `admin/standalone/` | React + Mantine + Vite | `npm run dev` (port 3300) | npm |
| `admin/shopify/` | React + Polaris + Vite | `npm run dev` | npm |
| `docs-site/` | Docusaurus | `yarn start` (port 3000) | yarn |

Each admin SPA has a `predev` hook that runs `sync-env` (PowerShell). For non-Windows, set `VITE_API_URL` manually.

### AGNTCY Isolation Policy

Agent Red and AGNTCY are strictly isolated projects. Even if both are active on the same machine:

- No shared local files, Docker containers, virtual environments, or build artifacts
- Agent Red accesses AGNTCY exclusively via its [public GitHub repository](https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service)
- SDK consumed via `pip install agntcy-app-sdk` from PyPI
- Docker images built independently or pulled from registry

---

## Launch 1.0 Roadmap

**Target:** Q1 2026 (8-12 weeks) | **Budget:** $500-1,000/month

| Milestone | Target | Status |
|-----------|--------|--------|
| M1: Setup Complete | Week 1 | ✅ Done |
| M2: Brand Ready | Week 3 | ✅ Done |
| M3: Legal Ready | Week 4 | ✅ Done (pending iubenda validation) |
| M4: Website Content | Week 5 | ✅ Done |
| M5: Backend Complete | Week 7 | ✅ Done (38 multi-tenant modules, 11 billing modules, 999 tests) |
| M6: Frontend Complete | Week 8 | ✅ Done (chat API, widget, admin shells — both build validated) |
| M7: Testing Complete | Week 9 | ✅ Done (P0+P1+P2, CI pipeline) |
| M8: Public Launch | Week 12 | 🔄 In Progress (integration testing, Shopify App Store submission) |

See [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) for detailed tasks and the [issues board](https://github.com/mike-remakerdigital/agent-red/issues) for live tracking.

---

## Legal

- Terms of Service — `legal/terms/TERMS-OF-SERVICE.md` (AI-drafted, pending iubenda validation)
- Privacy Policy — `legal/privacy/PRIVACY-POLICY.md` (AI-drafted, pending iubenda validation)
- Service Level Agreement — `legal/sla/SERVICE-LEVEL-AGREEMENT.md` (v0.2.0)
- Data Processing Agreement — `legal/dpa/DATA-PROCESSING-AGREEMENT.md` (AI-drafted)

---

## License

This is proprietary software. All rights reserved.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## About Remaker Digital

Remaker Digital builds AI-powered tools for e-commerce businesses. A DBA of VanDusen & Palmeter, LLC (Delaware).

[remakerdigital.com](https://remakerdigital.com)
