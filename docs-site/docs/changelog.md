---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

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
