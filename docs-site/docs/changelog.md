---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

---

## v1.17.0 — 2026-02-11

### Admin security
- Email-based forgot-password flow replaces the old change-password endpoint
- HMAC-signed reset tokens work across multiple replicas without shared state
- 15-minute token expiry, single-use enforcement, rate limiting (3 requests per 5 minutes)
- Branded HTML email with reset link delivered via SMTP (Titan Email)

### Widget
- Quick Action prompt buttons: configurable pill buttons in the widget greeting area that send pre-defined prompts
- Template variable substitution (`\{\{product_name\}\}`, `\{\{collection_name\}\}`, `\{\{page_handle\}\}`) for page-aware prompts
- Improved panel drop-shadow (dual-layer) for visibility on busy storefront backgrounds

### Admin dashboard
- Quick Action CRUD: 8-endpoint API for creating, editing, ordering, and assigning prompts to page types
- Conversation search endpoint (previously returned 405)
- Fixed audit log 500 error (Cosmos DB query initialization)
- Fixed customer profile list 503 error

### Logo
- Fixed corrupted logo on forgot-password pages (replaced invalid PNG data URI with SVG)

---

## v1.15.2 — 2026-02-10

### Bug fixes
- Fixed FastAPI route ordering: static routes (`/stale`, `/export`, `/staleness`) now registered before the `/{entry_id}` catch-all in the knowledge base API
- Widget config loading: Shopify Liquid template no longer overrides API-fetched tenant configuration with default values
- Widget default API URL corrected to production FQDN

### Infrastructure
- API Gateway restored after Azure subscription suspension and recovery
- Admin UI validation: 86/86 endpoints passing

---

## v1.14.0 — 2026-02-09

### Bug fixes
- Fixed hybrid search score filtering: `rrf_score` key mismatch caused all search results to be filtered out by the minimum score check
- Improved Critic prompt engineering to reduce false blocks on product feature descriptions

### Knowledge base
- Conflict scanner: 4-phase detection (embedding similarity, title trigrams, content overlap, factual conflict regex) with HIGH/MEDIUM/LOW severity ratings
- Admin UI "Scan for conflicts" button in the knowledge base manager toolbar

### App Store preparation
- Listing accuracy review: 8 inaccurate claims corrected to verifiable facts
- Non-disruptive upgrade infrastructure: automated upgrade/rollback scripts with 43-test regression suite

---

## v1.0.0 — 2026-02-09

**Initial release**

### AI pipeline
- Six specialized AI agents: intent classification, knowledge retrieval, response generation, escalation detection, analytics, and content safety (Critic/Supervisor)
- Direct Azure OpenAI integration (GPT-4o for responses, GPT-4o-mini for classification)
- Stream-then-validate pattern: AI responses stream in real-time, Critic validates post-stream

### Persistent customer memory
- **Layer 1 — Customer context:** Structured profiles with purchase history, geography, preferences, and account state injected into every interaction
- **Layer 2 — Conversation memory:** Vectorized transcripts with semantic search across full interaction history (Cosmos DB DiskANN)
- **Layer 3 — Cross-session learning:** Pattern extraction with confidence scoring and monthly decay (Professional and Enterprise tiers)
- **Layer 4 — Dedicated model training:** Per-customer fine-tuning on 1,000+ interactions (Enterprise add-on)

### Knowledge base
- Hybrid retrieval: BM25 keyword matching + vector similarity with Reciprocal Rank Fusion
- Document upload: PDF, DOCX, CSV, TXT, HTML parsing with automatic chunking
- Staleness detection with 3-factor scoring (age, embedding drift, verification recency)
- 3-tier semantic caching (embedding, search results, semantic similarity)

### Chat widget
- Preact-based widget (~17KB gzip) with Shadow DOM isolation
- SSE streaming for real-time AI responses
- WebSocket for typing indicators and presence
- Light and dark mode support
- Configurable appearance, greeting, pre-chat form, and offline form
- Shopify Theme App Extension delivery

### Admin dashboard
- Embedded Shopify admin (Polaris + App Bridge)
- Standalone admin with API key authentication
- Conversation inbox with message threading
- Knowledge base manager with document upload
- Analytics overview with intent breakdown
- Widget configurator with live preview
- Team management with role-based access
- 9-step onboarding wizard

### Billing
- Shopify Billing API integration (subscriptions + usage charges)
- 3-tier consumption: included allowance → conversation packs → overage
- Usage dashboard with real-time metrics and CSV export
- 14-day free trial on all tiers

### Security and compliance
- GDPR: 3 mandatory Shopify webhooks, PII scrubbing, data export/deletion, consent management
- Fail-closed Critic policy: responses blocked unless explicitly approved
- Per-tenant data isolation (Cosmos DB partition keys)
- Rate limiting per tier (Starter 10/min, Professional 50/min, Enterprise 200/min)

### Infrastructure
- 9 Azure Container Apps (East US 2)
- Cosmos DB Serverless with DiskANN vector index
- KEDA auto-scaling with night profiles
- Zero-downtime rolling deployment

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
