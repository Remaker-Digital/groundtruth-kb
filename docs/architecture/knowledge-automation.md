# Knowledge Automation Architecture

> KA-1 through KA-9 — Automated knowledge population and configuration for merchant tenants.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## Problem Statement

Session 63 proved that AI conversation quality is entirely dependent on knowledge base content. A tenant with zero KB articles scored terribly on quality tests; after seeding 12 articles, scores jumped from CONDITIONAL PASS to PASS (4.75/5.0). Merchants need guided, automated knowledge population from day one — not a blank KB and a hope that they'll fill it manually.

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Zero-effort onboarding** | First activation triggers automatic storefront ingestion |
| **No LLM cost for suggestions** | ConfigSuggestionEngine uses pure heuristic text analysis |
| **Non-blocking activation** | Ingestion runs as async background job; activation succeeds immediately |
| **Industry-specific templates** | 10 category templates provide starter content for common Shopify verticals |
| **Progressive enhancement** | Each automation feature is independently valuable |

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Admin UI (KA-7/8)                  │
│  KnowledgeBase.tsx │ Configuration.tsx │ Memory.tsx   │
└────────┬───────────┴──────────┬──────┴──────┬───────┘
         │                      │             │
    ┌────▼────┐          ┌─────▼──────┐  ┌──▼───────────┐
    │Ingestion│          │ Suggestion │  │Identification│
    │  API    │          │   API      │  │  Mode API    │
    │ (KA-2)  │          │  (KA-4)    │  │   (KA-5)     │
    └────┬────┘          └─────┬──────┘  └──────────────┘
         │                     │
    ┌────▼─────────────┐ ┌────▼──────────────┐
    │StorefrontIngest  │ │ConfigSuggestion   │
    │  Service (KA-1)  │ │  Engine (KA-4)    │
    │                  │ │ (heuristic, no LLM│
    │ Shopify GraphQL  │ │  brand, voice,    │
    │ URL crawl        │ │  escalation, etc.)│
    └───────┬──────────┘ └───────────────────┘
            │
    ┌───────▼──────────┐
    │ Template Loader   │
    │    (KA-3)         │
    │ 10 JSON templates │
    └──────────────────┘
```

## Components

### KA-1: Storefront Ingestion Service

**File:** `src/multi_tenant/storefront_ingestion.py`

Orchestrates bulk KB population from merchant storefronts.

- **Shopify path:** Uses `ShopifyGraphQLClient` with product/collection/policy queries to fetch products and convert them to KB articles
- **URL path:** Uses existing `crawl_url()` from `document_parser.py` to crawl any website
- **Job tracking:** `IngestionJobDocument` in Cosmos DB (partition: `/tenant_id`, TTL 30 days)
- **Background processing:** 4th background loop in `background.py` polls for pending jobs every 30s
- **Auto-vectorization:** Created articles are automatically vectorized via `KnowledgeVectorizer`

### KA-2: Ingestion Admin API

**File:** `src/multi_tenant/admin_ingestion_api.py`

REST endpoints for the admin UI:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/knowledge/ingest` | POST | Start ingestion job |
| `/api/admin/knowledge/ingest/status` | GET | Get latest job status |
| `/api/admin/knowledge/ingest/cancel` | POST | Cancel running job |
| `/api/admin/knowledge/templates` | GET | List category templates |
| `/api/admin/knowledge/templates/{id}/apply` | POST | Apply template to KB |
| `/api/admin/knowledge/suggestions` | GET | Get config suggestions |

### KA-3: Category Template System

**Directory:** `src/multi_tenant/knowledge_templates/`

10 industry-specific JSON template files covering the top Shopify merchant verticals:

1. Apparel & Fashion
2. Beauty & Cosmetics
3. Electronics & Gadgets
4. Home & Garden
5. Food & Beverage
6. Health & Wellness
7. Jewelry & Accessories
8. Sports & Outdoors
9. Toys & Games
10. Pet Supplies

Each template provides:
- Industry terminology glossary (FAQ articles)
- Common Q&A patterns
- Standard policy templates (returns, shipping, sizing/care)
- Suggested config values (brand_voice, escalation_keywords, greeting_message)

**Loader:** `src/multi_tenant/template_loader.py` with in-memory cache.

### KA-4: Configuration Suggestion Engine

**File:** `src/multi_tenant/config_suggestion_engine.py`

Pure heuristic engine — no LLM calls. Fast, deterministic, cost-free.

Analyzes KB articles to extract:
- `brand_name` — from vendor field frequency in product metadata
- `brand_voice` — tone analysis using keyword matching (professional, friendly, technical, caring, luxury)
- `escalation_keywords` — pattern matching against safety/complaint vocabulary
- `greeting_message` — generated from brand name + category analysis
- `widget_agent_display_name` — derived from brand name

Each suggestion carries a confidence score (0.0–1.0) and source description.

### KA-5: PCM Authentication Incentive

**Modified files:** `cosmos_schema.py`, `system_prompt_builder.py`, `tenant_config_schema.py`

New `customer_identification_mode` field on `PreferencesDocument` with 4 modes:

| Mode | Behavior |
|------|----------|
| `off` | No identification prompt |
| `gentle` | Casual mention that logging in helps personalization |
| `standard` | First response suggests login/email for order history access |
| `aggressive` | First response must include strong auth suggestion + probing questions |

Injected into the Response Generator system prompt based on mode value. PCM-building instructions are gated on `memory_enabled`.

### KA-6: First-Activation Ingestion Hook

**Modified file:** `src/multi_tenant/activation_service.py`

Wires ingestion into the activation lifecycle:
- On first activation (no prior `activated_at`), checks for `shopify_shop_domain`
- If Shopify: dispatches async ingestion job via `StorefrontIngestionService`
- Non-blocking: warnings added to `ActivationResult`, but activation always succeeds
- Subsequent activations do NOT re-trigger ingestion

### KA-7: Knowledge Automation Admin UI

**New frontend files:**
- `admin/shared/hooks/useIngestion.ts` — 5 hooks for ingestion CRUD
- `admin/shared/hooks/useSuggestions.ts` — config suggestion fetching
- `admin/shared/components/IngestionPanel.tsx` — job progress display
- `admin/shared/components/CategoryTemplateSelector.tsx` — template picker
- `admin/shared/components/SuggestionBadge.tsx` — inline suggestion badges

**Modified pages:**
- `KnowledgeBase.tsx` — Automation section with template selector, scan button, ingestion status
- `Configuration.tsx` — Suggestion badges on brand_name, brand_voice, refund_policy, shipping_policy fields

### KA-8: PCM Identification UI

**Modified file:** `admin/standalone/pages/MemoryPrivacy.tsx`

New "Customer Identification" section with Mantine `SegmentedControl` (off/gentle/standard/aggressive). Mode descriptions update dynamically. Disabled when customer context (memory) is turned off.

## Data Flow

### First Activation Flow

```
Merchant clicks "Activate"
  → ActivationService.activate()
    → Validation passes → Config committed
    → active is None? (first activation)
      → _maybe_start_ingestion(tenant_id)
        → Read TenantDocument for shopify_shop_domain
        → If domain: start_ingestion(tenant_id, {type: shopify, domain})
        → Return warnings: ["Knowledge base population is in progress"]
    → ActivationResult(success=true, warnings=[...])
```

### Suggestion Flow

```
Admin opens Configuration page
  → useConfigSuggestions(apiFetch) → GET /api/admin/knowledge/suggestions
    → ConfigSuggestionEngine.generate_suggestions(tenant_id)
      → Fetch published KB articles
      → Extract brand_name (vendor field frequency)
      → Analyze brand_voice (tone keyword matching)
      → Extract escalation_keywords (pattern matching)
      → Generate greeting_message (brand + category)
      → Suggest display_name (brand + "Support")
    → Return SuggestionMap
  → LabelWithSuggestion renders "Suggested" badge on empty fields
  → Click badge → applies suggestion value to form field
```

## Test Coverage

| Component | Test File | Tests |
|-----------|-----------|-------|
| KA-1: Ingestion Service | `tests/multi_tenant/test_storefront_ingestion.py` | ~40 |
| KA-2: Admin API | `tests/multi_tenant/test_admin_ingestion_api.py` | ~15 |
| KA-3: Template System | `tests/multi_tenant/test_template_loader.py` | ~30 |
| KA-4: Suggestion Engine | `tests/multi_tenant/test_config_suggestion_engine.py` | 41 |
| KA-5: PCM Auth | `tests/multi_tenant/test_pcm_identification.py` | ~15 |
| KA-6: Activation Hook | `tests/multi_tenant/test_activation_service.py` | 9 |
| **Total** | | **~150** |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Shopify API rate limits | Cursor pagination with delay; cap at 250 products |
| Low-quality articles from noisy HTML | `parse_url()` strips nav/footer; 100-char minimum filter |
| Category templates becoming stale | Version-controlled JSON; `template_version` field |
| Orphaned ingestion jobs | Startup scan marks `running` jobs >30min as `failed` |
| Non-Shopify merchants | URL-based ingestion + category templates work for all |

---

*Last updated: 2026-02-20*
