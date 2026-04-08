# Agent Red Customer Experience

> **AI-Powered Customer Service Platform for E-Commerce**
>
> Commercial SaaS product by [Remaker Digital](https://remakerdigital.com)

[![Python Tests](https://github.com/mike-remakerdigital/agent-red/actions/workflows/python-tests.yml/badge.svg?branch=develop)](https://github.com/mike-remakerdigital/agent-red/actions/workflows/python-tests.yml)
[![Lint](https://github.com/mike-remakerdigital/agent-red/actions/workflows/lint.yml/badge.svg?branch=develop)](https://github.com/mike-remakerdigital/agent-red/actions/workflows/lint.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-proprietary-red)

---

## Quick Links

| Resource | Link |
|----------|------|
| **Docs Site** | [agentredcx.com](https://agentredcx.com) |
| **Wiki** | [Project Wiki](https://github.com/mike-remakerdigital/agent-red/wiki) |
| **Issues** | [Issue Tracker](https://github.com/mike-remakerdigital/agent-red/issues) |
| **AI Assistant Guide** | [`CLAUDE.md`](CLAUDE.md) |

---

## Overview

Agent Red Customer Experience is a commercial SaaS platform that helps e-commerce businesses automate customer support with intelligent AI agents. A multi-agent pipeline of 20 specialized agents works together to understand, respond to, and resolve customer issues — while seamlessly escalating complex cases to your team.

### Key Capabilities

- **Instant Responses** — P95 latency under 2 seconds via SSE streaming
- **Multi-Agent Pipeline** — 6 core agents + 14 plugin agents with critic-retraction quality gate
- **Smart Escalation** — Complex issues routed to humans with full context via email bridge
- **Multi-Language** — English, French (CA), Spanish, German, Japanese, Korean, Portuguese, Chinese
- **Shopify Native** — Deep integration via App Bridge with real-time order and product data
- **Standalone Mode** — Direct-access admin for non-Shopify merchants
- **Persistent Customer Memory** — Canonical identity (ADR-004) with four-layer personalization
- **Enterprise Ready** — Per-tenant envelope encryption, usage metering, API key management

---

## Architecture

Agent Red is built on the open-source [AGNTCY Customer Engagement Platform](https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service) foundation, with proprietary commercial extensions.

### Multi-Agent Pipeline

| Agent | Purpose | Model |
|-------|---------|-------|
| Intent Classifier | Route customer queries (17 intents) | GPT-4o-mini |
| Knowledge Retrieval | Search products, FAQs, policies (RAG) | text-embedding-3-large |
| Response Generator | Craft personalized responses | GPT-4o |
| Critic/Supervisor | Validate quality, retract if below threshold | GPT-4o-mini |
| Escalation | Detect cases needing humans, email bridge | GPT-4o-mini |
| Analytics | Monitor performance metrics | GPT-4o-mini |

### Plugin Agent System (14 Additional Agents)

| Agent | Purpose |
|-------|---------|
| Sales Agent | Product search, cart management, checkout |
| Campaigns Agent | Active campaigns, discount codes, talking points |
| Schedule Agent | Follow-up scheduling, proactive notifications |
| Gateway Agent | Live agent routing, queue management |
| Bot Agent | A2A protocol, authentication, negotiation |
| External MCP | Stripe, Shopify, Square, PayPal integration |
| + 8 more | Domain-specific agents via YAML config-driven discovery |

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 / FastAPI (52 API routers) |
| AI | Azure OpenAI (GPT-4o, GPT-4o-mini, text-embedding-3-large) |
| Database | Azure Cosmos DB (20+ collections, partition-key tenant isolation) |
| Message Bus | NATS JetStream (agent-to-agent, per-tenant isolation) |
| Widget | Preact 10.25 (Shadow DOM launcher, iframe panel, 8 languages) |
| Admin SPAs | React 18.3 + Mantine UI (standalone, Shopify, provider — 3 SPAs) |
| Encryption | AES-256-GCM envelope encryption, Azure Key Vault HSM-backed KEK |
| Infrastructure | Azure Container Apps (9 containers), Terraform IaC |
| CI/CD | GitHub Actions (8 workflows, 5-shard parallel testing) |

---

## Repository Structure

```
Agent Red Customer Experience/
├── CLAUDE.md                       # AI assistant guidance
├── README.md                       # This file
├── Dockerfile                      # API gateway container
├── Dockerfile.test                 # Test host container
├── Dockerfile.ui                   # UI-only overlay (fast rebuild)
├── requirements.txt                # 35 production dependencies
├── pyproject.toml                  # pytest, coverage, ruff, mutmut config
│
├── src/                            # Backend (302 files)
│   ├── main.py                     # FastAPI composition root (52 routers)
│   ├── app/                        # App factory, lifecycle, auth, health
│   ├── agents/                     # 6 core AI agents
│   │   ├── containers/             # Per-agent Dockerfiles
│   │   └── plugins/                # 14 plugin agents (YAML config-driven)
│   ├── chat/                       # Chat endpoints, SSE, session, quality
│   │   └── pipeline/               # Orchestrator, intent router, critic
│   ├── integrations/               # Stripe, Shopify, Zendesk, Slack, Google Docs
│   ├── multi_tenant/               # Multi-tenant platform (174 files)
│   │   ├── repositories/           # 19 repository classes (TenantScopedRepository base)
│   │   ├── schema/                 # YAML-driven config validation
│   │   └── superadmin_api/         # Platform admin console
│   ├── jobs/                       # Migration/maintenance scripts
│   ├── observability/              # Langfuse exporter
│   └── quality_metrics/            # Quality scoring
│
├── admin/                          # 3 Admin SPAs
│   ├── standalone/                 # Direct-access merchant admin (15 pages)
│   ├── shopify/                    # Shopify embedded app (7 pages)
│   ├── provider/                   # Platform operator console (25+ pages)
│   └── shared/                     # Shared components, hooks, theme, types
│
├── widget/                         # Embeddable chat widget (Preact)
│   └── src/                        # 33 source files, 8 locale files
│
├── tests/                          # Test suite (605 files, 5,400+ tests)
│   ├── unit/                       # Unit tests (~950)
│   ├── multi_tenant/               # Integration tests (~3,700)
│   ├── e2e/                        # Browser E2E (Playwright)
│   ├── security/                   # Adversarial + penetration tests
│   ├── fuzzing/                    # API fuzzing (Schemathesis, 307 ops)
│   ├── property/                   # Property-based (Hypothesis)
│   └── ...                         # Contract, visual, transport, performance
│
├── infrastructure/terraform/       # Azure IaC (7 .tf files)
├── docs/                           # Architecture docs, plans, specs
├── docs-site/                      # Docusaurus admin guide
├── legal/                          # Privacy, ToS, SLA, DPA (all DRAFT)
├── branding/                       # Brand assets and logos
├── scripts/                        # Build, deploy, migration utilities
└── .github/workflows/              # 8 CI/CD workflows
```

---

## Pricing

Platform Fee + Metered AI Usage — each tier includes a monthly conversation allowance.

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
| White-Label Package | $399 | Enterprise only |
| Priority Support Upgrade | $99 | Starter, Pro |
| Custom Integration Dev | $299 | Enterprise only |
| Dedicated Model Training | $299 | Enterprise only |

---

## Production Infrastructure

Deployed on Azure (East US 2) with 9 independently scaled containers:

| Container | Resources | Scaling | Purpose |
|-----------|-----------|---------|---------|
| API Gateway | 0.5 CPU, 1 GB | 2-8 replicas (HTTP) | FastAPI entry point, SSE streaming |
| Intent Classifier | 0.5 CPU, 1 GB | 2-6 replicas (NATS) | Customer intent routing |
| Knowledge Retrieval | 0.5 CPU, 1 GB | 2-6 replicas (NATS) | RAG pipeline |
| Response Generator | 1.0 CPU, 2 GB | 2-10 replicas (NATS) | AI response generation |
| Critic Supervisor | 0.5 CPU, 1 GB | 2-4 replicas (NATS) | Quality gate |
| Escalation | 0.25 CPU, 0.5 GB | 1-3 replicas (NATS) | Human handoff |
| Analytics | 0.25 CPU, 0.5 GB | 1-2 replicas (NATS) | Metrics aggregation |
| Slim Gateway | 0.5 CPU, 1 GB | 2 (fixed) | UI-only fast-rebuild overlay |
| NATS | 0.5 CPU, 1 GB | 2 (fixed) | JetStream message bus |

**Supporting Services:** Cosmos DB, Azure OpenAI, Key Vault (HSM KEK), Redis, Azure Communication Services, Application Insights + Langfuse, Blob Storage.

---

## Development

### Prerequisites

- Windows 11
- Python 3.12+
- Node.js >= 20
- Docker Desktop
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/mike-remakerdigital/agent-red.git
cd agent-red

# Copy environment template
cp .env.example .env.local

# Build UI artifacts (required before Docker build)
cd widget && npm install && npm run build && cd ..
cd admin/standalone && npm install && npm run build && cd ..
cd admin/provider && npm install && npm run build && cd ..
cd admin/shopify && npm install && npm run build && cd ..

# Start local dev stack (API + NATS JetStream + Redis)
docker compose up -d

# Verify services
curl http://localhost:8080/health    # API
curl http://localhost:8222/healthz   # NATS monitoring
```

> **Without Docker:** Run uvicorn directly (`uvicorn src.main:app --reload --port 8000`). Vite dev servers for admin SPAs proxy to `localhost:8000`.

### Subproject Dev Servers

| Directory | Stack | Dev Server | Port |
|-----------|-------|------------|------|
| `widget/` | Preact + Vite | `npm run dev` | 5173 |
| `admin/provider/` | React + Mantine + Vite | `npm run dev` | 3400 |
| `admin/standalone/` | React + Mantine + Vite | `npm run dev` | 3300 |
| `admin/shopify/` | React + Polaris + Vite | `npm run dev` | — |
| `docs-site/` | Docusaurus | `yarn start` | 3000 |

### Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production mirror — always matches the current production deployment |
| `develop` | Continuous development — all new features and fixes land here |

All work happens on `develop`. Merge to `main` only as part of a production deployment.

---

## Testing

5,400+ tests across 10 testing methodologies, running in 5 parallel CI shards:

| Type | Count | Tooling |
|------|-------|---------|
| Unit | ~950 | pytest |
| Integration | ~3,700 | pytest |
| E2E / Browser | ~120 | Playwright |
| Contract / API | ~310 | Schemathesis (307 ops), Pact |
| Security | ~80 | Custom adversarial + pen tests |
| Performance / Load | ~50 | Locust |
| Property-based | ~200 | Hypothesis |
| Visual / A11y | ~30 | Chromatic, axe (WCAG 2.1 AA) |

Coverage gate: 75% minimum (ramping to 80%).

---

## Legal

- Terms of Service — `legal/terms/TERMS-OF-SERVICE.md` (DRAFT)
- Privacy Policy — `legal/privacy/PRIVACY-POLICY.md` (DRAFT)
- Service Level Agreement — `legal/sla/SERVICE-LEVEL-AGREEMENT.md` (v0.2.0)
- Data Processing Agreement — `legal/dpa/DATA-PROCESSING-AGREEMENT.md` (DRAFT)

---

## License

This is proprietary software. All rights reserved.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## About Remaker Digital

Remaker Digital builds AI-powered tools for e-commerce businesses. A DBA of VanDusen & Palmeter, LLC (Delaware).

[remakerdigital.com](https://remakerdigital.com)
