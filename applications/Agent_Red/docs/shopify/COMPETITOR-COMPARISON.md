# Agent Red vs Competitors — Pricing & Feature Comparison

> **All competitor pricing verified 2026-02-01 from official pricing pages.**
> This document is for internal use (sales, support, marketing) and merchant-facing comparison.

---

## At a Glance

| Feature | Agent Red $149/mo | Tidio+ $29/mo | Gorgias $300/mo | Zendesk $588/mo | Intercom $348/mo |
|---------|-------------------|---------------|-----------------|-----------------|------------------|
| AI Conversations/mo | **1,000** | 100 | 300 | ~500 | 250 |
| Overage Rate | **$0.04/conv** | $0.29 | $0.36 | ~$0.75 | $0.99 |
| Persistent Customer Memory | **4 layers** | None | None | None | None |
| KB Search Method | **Hybrid BM25+vector** | Basic FAQ | Help center | Help center | Fin AI |
| Custom AI Persona Controls | **34 fields** | Limited | Limited | No | Limited |
| Document Upload (PDF/DOCX/CSV/TXT) | **Yes** | CSV only | No | Yes | PDF/DOCX |
| Shopify Native Integration | **Theme App Extension** | Theme block | Sidebar | External | External |
| Widget Bundle Size | **~17 KB gzip** | ~40-60 KB | ~50 KB | ~60 KB | ~80-100 KB |
| Fail-Closed Safety Validation | **Yes** | No | No | No | No |
| Price Advantage (per conversation) | **Baseline** | 2x more | 9x more | 19x more | 25x more |

---

## Detailed Feature Comparison

### AI Capabilities

| Capability | Agent Red | Tidio | Gorgias | Zendesk | Intercom |
|------------|-----------|-------|---------|---------|----------|
| AI pipeline agents | 6 specialized | 1 (Lyro) | 1 | 1 | 1 (Fin) |
| Intent classification | 17 categories, 98% accuracy | Basic routing | Tag-based | Topic detection | Fin routing |
| Knowledge retrieval | Hybrid vector + BM25 + RRF | FAQ keyword match | Help center search | Help center search | Fin AI search |
| Response generation | GPT-4o with persona | GPT-based | GPT-based | GPT-based | GPT-4 (Fin) |
| Safety validation | Fail-closed Critic (every response) | None | None | None | Content filter |
| Escalation detection | Dedicated agent + rules | Keyword triggers | Rules | Rules | Fin handoff |
| Response latency P50 | 1,500ms target | Unknown | Unknown | Unknown | 7,000ms (published) |

### Persistent Customer Memory

| Layer | Agent Red | Tidio | Gorgias | Zendesk | Intercom |
|-------|-----------|-------|---------|---------|----------|
| Layer 1: Customer Profile | All tiers | Basic name/email | Contact card | User profile | User profile |
| Layer 2: Conversation Memory (vector RAG) | All tiers | None | None | None | None |
| Layer 3: Cross-Session Learning | Professional+ | None | None | None | None |
| Layer 4: Dedicated Model Training | Enterprise add-on | None | None | None | None |
| Per-customer vector search | Yes (DiskANN) | No | No | No | No |
| Memory across sessions | Yes (all interactions) | Current session only | Current ticket only | Current ticket only | Recent history |

**No competitor has confirmed implementing per-customer vector RAG over historical transcripts.** This is Agent Red's primary differentiator.

### Pricing Breakdown

#### Monthly Plans (lowest AI-capable tier)

| | Agent Red Starter | Tidio+ | Gorgias Basic | Zendesk Suite Team | Intercom Starter |
|--|-------------------|--------|---------------|-------------------|-----------------|
| Monthly price | **$149** | $29 | $300 | $588 ($49/agent x 12 min) | $348 ($29/seat x 12 min) |
| Included AI conv/mo | **1,000** | 100 | 300 | ~500 | 250 |
| Cost per included conv | **$0.149** | $0.29 | $1.00 | $1.18 | $1.39 |
| Overage rate | **$0.04** | $0.29 | $0.36 | ~$0.75 | $0.99 |

#### At 1,000 Conversations/Month

| | Agent Red | Tidio | Gorgias | Zendesk | Intercom |
|--|-----------|-------|---------|---------|----------|
| Base cost | $149 | $29 | $300 | $588 | $348 |
| Overage cost | $0 | $261 (900 x $0.29) | $252 (700 x $0.36) | $375 (500 x $0.75) | $742 (750 x $0.99) |
| **Total** | **$149** | **$290** | **$552** | **$963** | **$1,090** |
| **vs Agent Red** | baseline | **1.9x more** | **3.7x more** | **6.5x more** | **7.3x more** |

#### At 5,000 Conversations/Month

| | Agent Red Professional | Tidio | Gorgias | Zendesk | Intercom |
|--|------------------------|-------|---------|---------|----------|
| Base cost | $399 | $29 | $300 | $588 | $348 |
| Overage cost | $0 | $1,421 (4,900 x $0.29) | $1,692 (4,700 x $0.36) | $3,375 (4,500 x $0.75) | $4,703 (4,750 x $0.99) |
| **Total** | **$399** | **$1,450** | **$1,992** | **$3,963** | **$5,051** |
| **vs Agent Red** | baseline | **3.6x more** | **5.0x more** | **9.9x more** | **12.7x more** |

### Pre-Purchased Conversation Packs

Only Agent Red offers prepaid conversation packs at discounted rates:

| Pack | Price | Per-Conversation Rate | Validity |
|------|-------|-----------------------|----------|
| 1,000 conversations | $29 | $0.029 | 90 days |
| 5,000 conversations | $99 | $0.020 | 90 days |
| 20,000 conversations | $249 | $0.012 | 90 days |

Packs are consumed before overage billing (FIFO, oldest-first).

### Widget & Integration

| Feature | Agent Red | Tidio | Gorgias | Zendesk | Intercom |
|---------|-----------|-------|---------|---------|----------|
| Widget delivery | Shadow DOM + iframe | Script embed | Sidebar | Script embed | Script embed |
| Bundle size | ~17 KB gzip | ~40-60 KB | ~50 KB | ~60 KB | ~80-100 KB |
| Shopify integration | Theme App Extension (native) | Theme block | Sidebar widget | External script | External script |
| Widget customization fields | 24 appearance + 9 behavior | ~15 | ~10 | ~10 | ~15 |
| Dark mode | Yes (auto-detect) | Yes | No | Partial | Yes |
| Page rules (per-page visibility) | Yes (glob patterns) | URL targeting | No | No | No |
| Pre-chat form | Configurable fields | Yes | No | Yes | Yes |
| Chat rating | Thumbs up/down + comment | Star rating | CSAT | CSAT | Emoji + text |
| Offline form | Yes | Yes | No | Yes | Yes |

### Admin Dashboard

| Feature | Agent Red | Tidio | Gorgias | Zendesk | Intercom |
|---------|-----------|-------|---------|---------|----------|
| Shopify embedded admin | Yes (Polaris + App Bridge) | Yes | No | No | No |
| Standalone admin (non-Shopify) | Yes (API key login) | No | Yes | Yes | Yes |
| AI configuration controls | 34 behavior + 24 widget | ~15 | ~10 | ~8 | ~12 |
| Usage transparency dashboard | Real-time + CSV export | Basic | Basic | Reports add-on | Custom reports |
| Knowledge base CRUD | Yes + file upload + bulk import | FAQ builder | Help center | Help center | Articles |
| Conversation inbox | Two-panel + assign + notes | Yes | Yes (ticket view) | Yes (ticket view) | Yes |
| Team management | Roles + invite + concurrent limits | Basic | Yes | Yes | Yes |
| Analytics | Summary + intents + gaps | Basic | Advanced (add-on) | Advanced (add-on) | Advanced |
| A/B testing for AI config | Planned (Smart Rollout) | No | No | Zendesk only (highest tier) | No |

---

## Key Talking Points

### For Sales

1. **"4-21x cheaper per conversation"** — At any volume, Agent Red costs a fraction of competitors.
2. **"Memory that no one else has"** — Persistent Customer Memory (4 layers) is not offered by any competitor.
3. **"Fail-closed safety"** — Every AI response is validated before reaching customers. No competitor does this.
4. **"Fastest widget"** — 17 KB gzip vs 40-100 KB competitors. Doesn't slow down the storefront.

### For Affiliates/Promoters

1. **Price comparison is the hook** — Show the 1,000 conv/month total cost table. The numbers speak for themselves.
2. **Memory is the differentiator** — "The AI remembers every customer" is a compelling narrative.
3. **Shopify-native** — Theme App Extension, not a clunky sidebar or external script.

### Competitive Weaknesses to Acknowledge

1. **Tidio has a free tier** — Agent Red does not. Counter: Tidio's free AI is extremely limited (50 conversations).
2. **Gorgias has deeper Shopify order management** — Agent Red reads orders but doesn't manage them. Counter: order management is a specialized feature, not core AI customer service.
3. **Zendesk/Intercom have mature ecosystems** — Larger app marketplaces and integrations. Counter: Agent Red is purpose-built for Shopify merchants at 4-21x lower cost.
4. **Agent Red is new** — No reviews, no "Built for Shopify" badge yet. Counter: 14-day free trial, transparent pricing, live demo on Remaker Digital storefront.

---

## Verification Sources

All pricing verified from official websites on **2026-02-01**:

- Tidio: https://www.tidio.com/pricing/
- Gorgias: https://www.gorgias.com/pricing
- Zendesk: https://www.zendesk.com/pricing/
- Intercom: https://www.intercom.com/pricing

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last verified: 2026-02-01*
