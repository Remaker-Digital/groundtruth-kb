# Agent Red Customer Engagement

> **AI-Powered Customer Service Platform for E-Commerce**
>
> Commercial SaaS product by [Remaker Digital](https://remakerdigital.com)

---

## Quick Links

| Resource | Link |
|----------|------|
| **Project Board** | [Agent Red Launch 1.0](https://github.com/orgs/Remaker-Digital/projects/2) |
| **Milestones** | [Issues](https://github.com/Remaker-Digital/agent-red-customer-engagement/issues) (M1-M8) |
| **Project Plan** | [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) |
| **AI Assistant Guide** | [`CLAUDE.md`](CLAUDE.md) |
| **Commercial Proposal** | [`docs/COMMERCIAL-SAAS-PROPOSAL.md`](docs/COMMERCIAL-SAAS-PROPOSAL.md) |
| **Product Features (RAG)** | [`docs/PRODUCT-FEATURES-RAG.md`](docs/PRODUCT-FEATURES-RAG.md) |
| **Baseline Verification** | [`docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md`](docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md) |

---

## Overview

Agent Red Customer Engagement is a commercial SaaS platform that helps e-commerce businesses automate customer support with intelligent AI agents. It combines six specialized AI agents that work together to understand, respond to, and resolve customer issues instantly — while seamlessly escalating complex cases to your team.

### Key Capabilities

- **Instant Responses** — P95 latency under 2 seconds
- **70%+ Automation** — Handle routine inquiries automatically
- **Smart Escalation** — Complex issues routed to humans with full context
- **Multi-Language** — English, French (CA), Spanish support
- **Shopify Native** — Deep integration with real-time order and product data
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

---

## Repository Structure

```
Agent Red Customer Engagement/
├── CLAUDE.md                       # AI assistant guidance
├── README.md                       # This file — project hub
├── Dockerfile                      # Container build
├── docker-compose.yml              # Local dev stack (API + NATS)
├── requirements.txt                # Python dependencies
│
├── src/                            # Commercial source code
│   ├── multi-tenant/               # Tenant management
│   ├── integrations/               # Enterprise integrations
│   ├── ai-features/                # Advanced AI capabilities
│   └── white-label/                # Customization engine
│
├── infrastructure/                 # Deployment infrastructure
│   └── terraform/                  # IaC for Azure
│
├── website/                        # Marketing website
│   └── content/                    # Page content (markdown)
│
├── docs/                           # Documentation
│   ├── PROJECT-PLAN.md             # Launch 1.0 milestones and tasks
│   ├── COMMERCIAL-SAAS-PROPOSAL.md # Full business analysis
│   ├── PRODUCT-FEATURES-RAG.md     # Complete feature reference
│   ├── AGNTCY-BASELINE-VERIFICATION-REPORT.md
│   ├── architecture/               # Technical architecture
│   ├── guides/                     # How-to guides
│   └── api/                        # API reference
│
├── branding/                       # Brand assets
├── legal/                          # Legal documents
│
└── scripts/                        # Automation scripts
    ├── verify-agntcy-local.ps1     # AGNTCY local verification
    └── verify-agntcy-production.ps1 # AGNTCY Azure verification
```

---

## Pricing

| Tier | Monthly | Annual | Conversations/Day |
|------|---------|--------|-------------------|
| **Starter** | $299 | $2,990 | 500 |
| **Professional** | $499 | $4,990 | 2,000 |
| **Enterprise** | $999 | $9,990 | 10,000 |

### Add-On Modules

| Module | Monthly | Available On |
|--------|---------|--------------|
| Multi-Language | $149 | Pro, Enterprise |
| Advanced Analytics | $199 | All |
| Priority Support | $99 | All |
| Custom Integrations | $299 | Pro, Enterprise |
| White-Label | $499 | Enterprise |

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
- Docker Desktop
- Git + GitHub Desktop
- Visual Studio Code

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Remaker-Digital/agent-red-customer-engagement.git
cd agent-red-customer-engagement

# Copy environment template
cp .env.example .env.local

# Start local dev stack (API + NATS JetStream)
docker compose up -d

# Verify services
curl http://localhost:8080/health    # API
curl http://localhost:8222/healthz   # NATS
```

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
| M2: Brand Ready | Week 3 | 📋 Todo |
| M3: Legal Ready | Week 4 | 📋 Todo |
| M4: Website Live | Week 5 | 📋 Todo |
| M5: Store Live | Week 7 | 📋 Todo |
| M6: Docs Complete | Week 8 | 📋 Todo |
| M7: Soft Launch | Week 10 | 📋 Todo |
| M8: Public Launch | Week 12 | 📋 Todo |

See [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md) for detailed tasks and the [project board](https://github.com/orgs/Remaker-Digital/projects/2) for live tracking.

---

## Legal

- Terms of Service — *drafting in progress*
- Privacy Policy — *drafting in progress*
- Service Level Agreement — *drafting in progress*

---

## License

This is proprietary software. All rights reserved.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## About Remaker Digital

Remaker Digital builds AI-powered tools for e-commerce businesses. A DBA of VanDusen & Palmeter, LLC (Delaware).

[remakerdigital.com](https://remakerdigital.com)
