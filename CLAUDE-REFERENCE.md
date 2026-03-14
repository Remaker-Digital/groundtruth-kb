# CLAUDE-REFERENCE.md — Static Reference Material

> This file contains stable reference data (legal, pricing, infrastructure, AGNTCY rules) that rarely changes. It is **not** loaded automatically — read it on demand when working on billing, legal, infrastructure, or AGNTCY-related tasks.
>
> For active project guidance, see `CLAUDE.md`. For architecture and module inventory, see `CLAUDE-ARCHITECTURE.md`.

---

## Legal & IP

| Attribute | Value |
|-----------|-------|
| **Legal Entity** | VanDusen & Palmeter, LLC |
| **DBA** | Remaker Digital |
| **Jurisdiction** | Delaware, USA |
| **Entity Type** | Limited Liability Company (LLC) |
| **Website** | https://remakerdigital.com |

### IP Separation Rules

Agent Red is an independent commercial product. Its relationship to the AGNTCY open-source project is strictly arms-length.

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

**Rule:** Agent Red has no privileged access to AGNTCY. It consumes only publicly available artifacts.

---

## Upstream Dependency: AGNTCY

### Relationship

Agent Red consumes the AGNTCY open-source project as any external third party would.

- **Repository:** https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- **Visibility:** Public
- **License:** Open Source
- **SDK Package:** `agntcy-app-sdk` (PyPI)

AGNTCY SDK is the mandatory foundation for all Agent Red agent communication. Agent Red uses the `agntcy-app-sdk` for agent protocols (A2A, MCP), transport (SLIM/NATS), and factory patterns (`AgntcyFactory`). All six agents route through AGNTCY transport by default (`USE_AGENT_CONTAINERS=true`), with in-process fallback when transport is unavailable.

### How Agent Red Consumes AGNTCY

1. **SDK Package:** `pip install agntcy-app-sdk` for agent development patterns
2. **Docker Images:** Build from AGNTCY's public Dockerfiles or reference patterns
3. **Terraform Patterns:** Reference AGNTCY's published IaC for Azure deployment
4. **Architecture Patterns:** Factory singleton, BaseAgent, PII tokenization, connection pooling
5. **Evaluation Data:** Prompt templates and evaluation methodology from public repo

Agent Red does **not**: reference AGNTCY files by local path, depend on AGNTCY's uncommitted state, or require coordination for releases.

### Local Development Isolation Rules

**IMPORTANT:** The AGNTCY open-source project and Agent Red may both be active on this desktop simultaneously. They must be strictly isolated:

| Rule | Detail |
|------|--------|
| **No local file sharing** | No local path references between projects. |
| **No shared Docker containers** | Each project manages its own containers independently. |
| **No shared local artifacts** | No shared virtual environments, build artifacts, volumes, databases, or message queues. |
| **GitHub only** | Agent Red obtains AGNTCY artifacts exclusively via GitHub. |
| **SDK via PyPI** | `pip install` from PyPI, not from a local clone. |
| **Docker images via registry** | Builds own images or pulls from registry. Does not reuse AGNTCY's local images. |

If AGNTCY Docker containers are running on this machine, Agent Red must behave as if they do not exist.

### Contributing Changes Back to AGNTCY

1. Propose via GitHub Issue or Pull Request on the public AGNTCY repo
2. Wait for the change to be reviewed, merged, and published
3. Consume the published change through AGNTCY's public GitHub

---

## Production Infrastructure (Summary)

> **Canonical source:** `MEMORY.md` § Quick Reference for current values (versions, keys, FQDNs).

| Resource | Name | Key Detail |
|----------|------|------------|
| Resource Group | Agent-Red | East US |
| Azure OpenAI | aoai-agentred-eastus | S0, 3 deployments (gpt-4o, gpt-4o-mini, text-embedding-3-large) |
| Cosmos DB | cosmos-agentred-eastus | Serverless, NoSQL Vector Search, DiskANN, 20 containers (incl. platform_admins) |
| Key Vault | kv-agentred-eastus | RBAC-enabled |
| Container Registry | acragentredeastus | ACR repository: api-gateway |
| Container App Env | agent-red-cae | Domain: `orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| API Gateway | agent-red-api-gateway | FQDN: `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| NATS | agent-red-nats | Internal: `agent-red-nats.internal.orangeglacier-f566a4e7.eastus.azurecontainerapps.io:4222` |
| Redis Cache | redis-agentred-eastus | Standard C1, TLS-only (port 6380), `publicNetworkAccess=Enabled`, access key auth |

Staging: `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` (3 tenants, Redis connected, scales to zero).

**Third-Party Service Accounts:** Azure OpenAI (pay-per-token), Shopify Partner (developer), Zendesk (sandbox), Mailchimp (free tier), Google Analytics (GA4).

---

## Commercial Differentiators

These features are **exclusive to Agent Red** (not in open-source):

1. **Multi-Tenant SaaS Infrastructure** — Tenant isolation, subscription management, usage metering, self-service portal, API key management
2. **Advanced AI Features** — Premium model access, fine-tuned models, advanced analytics, custom training pipelines, A/B testing
3. **Enterprise Integrations** — Salesforce, SAP, ServiceNow, custom connector framework, Enterprise SSO
4. **White-Label & Customization** — Complete branding removal, custom domains, CSS theming, co-branding, reseller portal
5. **Persistent Customer Memory** — Four-layer personalization stack:
   - L1: Customer Context (All tiers) — structured profile injected into every interaction
   - L2: Conversation Memory (All tiers) — vectorized transcripts, semantic search via Cosmos DB
   - L3: Cross-Session Learning (Professional+) — extracted patterns, preferences, communication style
   - L4: Dedicated Model Training (Enterprise add-on, $299/mo) — per-customer AI fine-tuning

No competitor has confirmed implementing per-customer vector RAG over historical transcripts. Marginal cost: ~$0.01/customer/month for Layers 1-2.

---

## Pricing Structure

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

**Per-conversation AI cost:** ~$0.0073 (GPT-4o = 94.5%, plus Cosmos DB RU + archival)

**Infrastructure costs (shared, multi-tenant):** ~$252-436/mo total. Per-tenant marginal: ~$13-41/mo at 10+ tenants.

**Gross margin at list price:** 76-90% across all scenarios.

**Pricing design principles:** Transparent usage pricing, start granular (add-ons) bundle later, 50% below nearest competitor, higher affiliate payouts ($30-37/mo), pricing stability.

---

## Launch 1.0 Scope

- **Target:** Q1 2026 (8-12 weeks)
- **Budget:** $500-1,000/month, lean startup
- **Out-of-Scope:** Developer community, technical presentations, social media automation, compliance certifications, license management

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

**Association Rule:** The repository `mike-remakerdigital/agent-red` is the canonical home for this project.

---

## CI/CD Strategy

| Stage | Platform | Purpose |
|-------|----------|---------|
| Development | GitHub Actions | PR validation, unit tests, linting |
| Staging | Azure DevOps | Integration tests, staging deployment |
| Production | Azure DevOps | Production deployment, monitoring |

---

## Brand Requirements

**Core brand system complete** (Phase 1.1). Primary color: `#ff3621`.

- Logo: `{r}` curly brace design with `#ff3621`
- Palette: 15 colors, WCAG AA/AAA verified
- Typography: Inter + JetBrains Mono
- Guidelines: `branding/guidelines/BRAND-GUIDELINES.md`
- Admin UI: Mantine v7 (standalone) + Polaris 12 (Shopify)
- Dark mode: chrome `#0a0a0a` → page `#141414` → surface `#1f1f1f` → border `#272727`
- Prototype: `cd prototype && npm run dev` (port 3000) — frozen
- Documentation: https://agentredcx.com (Docusaurus + GitHub Pages)

**Brand Name Usage:** Full: "Agent Red Customer Experience" | Short: "Agent Red"

---

## Self-Service Legal Tools

**Plan-of-record:** iubenda (Advanced plan) + LegalZoom for SLA/DPA reviews.

| Document | Tool |
|----------|------|
| Terms of Service | iubenda |
| Privacy Policy | iubenda |
| Cookie Policy | iubenda |
| Data Processing Agreement | iubenda |
| SLA / DPA Reviews | LegalZoom (ad-hoc) |

**Language priorities:** Spanish (Mexico), French (Canada) near-term. Portuguese (Brazil), UK English medium-term.

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
| Brand assets | Core system complete; `{r}` logo with `#ff3621` |
| CI/CD | Hybrid (GitHub Actions + Azure DevOps) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-03-13*
