# Changelog

All notable changes to Agent Red Customer Experience will be documented in this file.

This project uses [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2026-02-08

### Summary

First general availability release of Agent Red Customer Experience. A multi-tenant AI customer service platform for Shopify and Stripe-direct merchants.

### Platform

- FastAPI application with 21 routers, 78+ routes, 9 middleware layers
- Python 3.12+ with async/await throughout
- Azure Container Apps deployment (9 containers, East US 2)
- Terraform-managed infrastructure (16 resources)

### Multi-Tenant Infrastructure (45 modules, ~34,000 lines)

- Cosmos DB Serverless with partition-key tenant isolation (9 containers)
- Triple authentication: Shopify JWT, API key, publishable widget key
- Per-tenant rate limiting (Starter 10rpm, Professional 50rpm, Enterprise 200rpm)
- Per-tenant concurrency limits with progressive throttling (Watch/Warn/Throttle/Isolate)
- Pipeline timeout budgets (8s hard deadline, per-stage budgets)
- Circuit breakers for Azure OpenAI, Cosmos DB, NATS
- Fail-closed Critic policy (responses blocked unless explicitly approved)
- GDPR compliance (PII scrubbing, data export/deletion, consent management)
- OpenTelemetry tenant tracing with correlation ID propagation
- Append-only audit log (12 event types, 1-year retention)

### AI Pipeline

- 4-stage pipeline: Intent Classification, Knowledge Retrieval, Response Generation, Critic Validation
- Direct Azure OpenAI integration (GPT-4o, GPT-4o-mini, text-embedding-3-large)
- SSE streaming with stream-then-validate pattern
- Hybrid knowledge retrieval (BM25 + vector search + Reciprocal Rank Fusion)
- 3-tier semantic caching (embedding, search results, semantic similarity)
- Document upload and parsing (PDF, DOCX, CSV, TXT, HTML)
- Knowledge base staleness detection and auto re-embedding
- Escalation detection with human handoff

### Persistent Customer Memory (4 layers)

- Layer 1: Customer profile with 6 data sources (all tiers)
- Layer 2: Conversation vectorization and semantic search (all tiers, tier-gated depth)
- Layer 3: Cross-session pattern extraction with confidence scoring (Professional+)
- Layer 4: Per-customer fine-tuning pipeline with quality gates (Enterprise add-on)
- Response explainability framework (per-response decision trace)

### Billing

- Dual-channel: Shopify App Store + Stripe direct
- 3-tier consumption: included allowance, conversation packs (FIFO), Stripe overage
- Metered usage with proactive alerts (80%/100% thresholds)
- Trial tier (14-day, 50 conversations, GPT-4o-mini)

### Admin Dashboard

- Standalone admin SPA (React + Mantine v7, password-gated)
- Shopify embedded admin SPA (React + Polaris + App Bridge)
- 9 shared components across both shells
- 10-step onboarding wizard with state persistence
- Knowledge base CRUD with document upload
- Conversation inbox with assignment
- Analytics overview with charts
- Widget configurator with live preview
- Team management
- Billing portal

### Chat Widget

- Preact + TypeScript, ~17KB gzip IIFE bundle
- Shadow DOM launcher + iframe panel (full DOM isolation)
- SSE streaming with auto-reconnect and retraction support
- WebSocket typing indicators and presence
- Pre-chat form, chat rating, offline form
- Light/dark mode, configurable via merchant settings
- Shopify Theme App Extension delivery

### Shopify Integration

- GraphQL Admin API client (no REST)
- Shopify Billing API (subscriptions + usage charges)
- 3 mandatory GDPR webhooks with HMAC-SHA256 verification
- Theme App Extension for widget delivery
- Session token authentication for embedded admin

### Security

- Input sanitization, CORS, CSP headers
- Request body size limits (1MB), JSON depth validation (50 levels)
- Stripe webhook IP allowlisting
- API key rotation with SHA-256 hash-only storage
- OWASP security headers on all responses

### Operations

- Structured JSON logging (production) with colored dev formatter
- SLA monitoring (P50/P95/P99 latency tracking)
- Data retention enforcement (tier-based, scheduled)
- Archival pipeline (Hot to Warm Parquet, Azure Blob Storage)
- Multi-channel alert delivery (webhook, dashboard, email, log)
- Cost model calculator with margin projections

### Testing

- 1,806 unit tests, 0 failures (pytest, ~6 min)
- 22 Azure integration tests (real OpenAI, Cosmos DB, Key Vault)
- 51 browser UI test steps, 100% pass rate (LUIT-SA)
- 50 adversarial security tests
- 47 performance/SLA validation tests
- Coverage gate: 70% minimum (~73% actual)

### Pricing

| Tier | Monthly | Included Conversations |
|------|---------|----------------------|
| Trial | Free | 50 (14 days) |
| Starter | $149 | 1,000 |
| Professional | $399 | 5,000 |
| Enterprise | $999 | 20,000 |

---

## [Unreleased]

### Planned for 1.1

- Full Test Mode infrastructure (population targeting, readiness checks)
- Period filtering and real-time stat deltas in dashboard
- AI persona live preview chat
- Widget embed code generator and domain allowlist
- Frontend component tests (Jest/JSDOM)
- WebSocket transport tests
- Locust load test execution in staging
- Staging environment for parallel development

---

*For full release details, see `docs/MASTER-TEST-PLAN-1.0.md` and `docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md`.*

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
