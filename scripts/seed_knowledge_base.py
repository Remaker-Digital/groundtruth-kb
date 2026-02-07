"""
Seed knowledge base data for the Remaker Digital demo storefront.

Loads Agent Red product knowledge into the knowledge base so the
chat widget's AI assistant can answer customer questions about the
product. Articles cover pricing, features, integrations, setup,
billing, security, support, competitive advantages, and add-ons.

v2.0 — Optimized for hybrid retrieval (vector + BM25):
  - Long articles split into focused chunks (~300-600 chars each)
  - Q&A pairs added for question-to-answer embedding alignment
  - Remaker Digital store product data included
  - Auto-embedding via KnowledgeVectorizer after load

Usage:
    # Print summary of seed articles (no DB required):
    python scripts/seed_knowledge_base.py

    # Load into Cosmos DB (requires Azure credentials):
    python scripts/seed_knowledge_base.py --load

    # Load + embed (requires Azure OpenAI credentials):
    python scripts/seed_knowledge_base.py --load --embed

Schema reference:
    - KnowledgeBaseDocument in src/multi_tenant/cosmos_schema.py
    - KnowledgeBaseRepository in src/multi_tenant/repository.py
    - entry_type: product | faq | policy | custom

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed data — optimized for retrieval (focused chunks + Q&A pairs)
# ---------------------------------------------------------------------------

SEED_ARTICLES: list[dict] = [
    # ===================================================================
    # SECTION 1: PRICING & PLANS (focused chunks)
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Agent Red Pricing Overview",
        "content": (
            "Agent Red Customer Experience uses a Platform Fee plus Metered AI Usage "
            "pricing model. Each tier includes a monthly platform fee covering "
            "infrastructure, features, and support, along with a monthly conversation "
            "allowance. Conversations beyond the included allowance are billed at "
            "tiered overage rates. Annual billing saves 17% compared to monthly."
        ),
        "tags": ["pricing", "plans", "tiers", "cost"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Starter Plan Details",
        "content": (
            "The Starter plan costs $149 per month (or $124/month billed annually "
            "at $1,490/year). It includes 1,000 conversations per month. Overage "
            "rate: $0.04 per conversation. Starter includes all 6 AI agents, "
            "Persistent Customer Memory Layers 1-2, 90-day conversation history, "
            "10 requests/minute rate limit, 3 concurrent conversations, 99.5% "
            "uptime SLA, and 24-hour RTO."
        ),
        "tags": ["pricing", "starter", "plans", "cost", "monthly"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Professional Plan Details",
        "content": (
            "The Professional plan costs $399 per month (or $332/month billed "
            "annually at $3,990/year). It includes 5,000 conversations per month. "
            "Overage rate: $0.025 per conversation. Professional includes all 6 "
            "AI agents, Persistent Customer Memory Layers 1-3 (with Cross-Session "
            "Learning), 365-day conversation history, 50 requests/minute rate limit, "
            "10 concurrent conversations, 99.9% uptime SLA, and 8-hour RTO. "
            "Access to Advanced Analytics, Mailchimp, and GA4 add-ons."
        ),
        "tags": ["pricing", "professional", "plans", "cost", "monthly"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Enterprise Plan Details",
        "content": (
            "The Enterprise plan costs $999 per month (or $832/month billed "
            "annually at $9,990/year). It includes 20,000 conversations per month. "
            "Overage rate: $0.015 per conversation. Enterprise includes all 6 AI "
            "agents, Persistent Customer Memory Layers 1-4 (with Dedicated Model "
            "Training add-on), unlimited conversation history, 200 requests/minute "
            "rate limit, 30 concurrent conversations, 99.95% uptime SLA, and "
            "4-hour RTO. Access to White-Label, Custom Integration, and Dedicated "
            "Model Training add-ons."
        ),
        "tags": ["pricing", "enterprise", "plans", "cost", "monthly"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Annual Billing Discount",
        "content": (
            "All Agent Red tiers offer a 17% discount when billed annually. "
            "Starter: $124/month ($1,490/year) instead of $149/month. "
            "Professional: $332/month ($3,990/year) instead of $399/month. "
            "Enterprise: $832/month ($9,990/year) instead of $999/month. "
            "You can switch between monthly and annual billing at any time. "
            "Annual billing is charged upfront for the full year."
        ),
        "tags": ["pricing", "annual", "discount", "billing"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Conversation Packs",
        "content": (
            "Conversation Packs let you pre-purchase conversations at discounted "
            "rates. Packs are valid for 90 days and consumed before overage billing "
            "(FIFO: oldest pack first). Available packs: 1,000 conversations for "
            "$29 ($0.029/conv), 5,000 for $99 ($0.020/conv), 20,000 for $249 "
            "($0.012/conv). Consumption order: included allowance first, then "
            "pack balance (oldest first), then overage billing."
        ),
        "tags": ["pricing", "packs", "conversations", "prepaid", "overage"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "What Counts as a Billable Conversation?",
        "content": (
            "A billable conversation starts when a customer sends their first "
            "message and ends on: 30 minutes of inactivity, customer explicitly "
            "ends the conversation, escalation to a human agent, or 50 turns "
            "reached. NOT billable: conversations prefixed with test_, admin_, "
            "health_, or system_, and conversations where no AI response was "
            "generated before an error occurred."
        ),
        "tags": ["billing", "conversations", "metering", "usage"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 2: CORE FEATURES (split into focused chunks)
    # ===================================================================
    {
        "entry_type": "product",
        "title": "Six Specialized AI Agents",
        "content": (
            "Agent Red is powered by six AI agents that work together: "
            "1) Intent Classification (GPT-4o-mini, 98% accuracy, 17 intents), "
            "2) Knowledge Retrieval (text-embedding-3-large, 100% retrieval), "
            "3) Response Generation (GPT-4o, 88.4% quality), "
            "4) Escalation (GPT-4o-mini, 100% precision/recall), "
            "5) Analytics (performance monitoring), "
            "6) Critic/Supervisor (fail-closed content safety, 0% FP, 100% TP). "
            "All six agents run in every conversation."
        ),
        "tags": ["features", "agents", "ai", "pipeline", "safety"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Persistent Customer Memory — Layer 1: Customer Context",
        "content": (
            "Layer 1 (available on all tiers): Structured profile data including "
            "purchase history, cart contents, geographic region, marketing segments, "
            "jurisdiction codes, and product question history. Injected into every "
            "conversation as context (~250 tokens). This is the foundation of "
            "Agent Red's personalized experience."
        ),
        "tags": ["features", "memory", "personalization", "layer-1", "context"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Persistent Customer Memory — Layer 2: Conversation Memory",
        "content": (
            "Layer 2 (available on all tiers): Vectorized transcripts of past "
            "conversations enable semantic search across a customer's full "
            "interaction history. History depth: Starter 90 days, Professional "
            "365 days, Enterprise unlimited. Uses text-embedding-3-large with "
            "3072-dimensional embeddings and Cosmos DB DiskANN vector index."
        ),
        "tags": ["features", "memory", "personalization", "layer-2", "vector"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Persistent Customer Memory — Layer 3: Cross-Session Learning",
        "content": (
            "Layer 3 (Professional and Enterprise only): Automatically extracts "
            "patterns, preferences, and communication style from conversations "
            "using GPT-4o-mini post-conversation analysis. Patterns have confidence "
            "scores (0-1) and decay over time (0.05/month) to stay current. "
            "Injected as ~100 tokens of context."
        ),
        "tags": ["features", "memory", "personalization", "layer-3", "patterns"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Persistent Customer Memory — Layer 4: Dedicated Model Training",
        "content": (
            "Layer 4 (Enterprise add-on, $299/month): Per-customer AI fine-tuning "
            "on 1,000+ historical interactions for maximum personalization. Monthly "
            "training pipeline with 5 quality gates (hallucination, format, tone, "
            "facts, BLEU/ROUGE), A/B validation (80/20 split), model versioning "
            "(max 3 kept), and rollback with reason tracking."
        ),
        "tags": ["features", "memory", "personalization", "layer-4", "fine-tuning"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "AI Response Safety — Fail-Closed Critic System",
        "content": (
            "Agent Red uses a fail-closed Critic/Supervisor system. Every response "
            "must be explicitly approved. If the Critic rejects, times out, or "
            "encounters an error, the response is blocked and a safe fallback "
            "message is shown. The Critic prompt is immutable and cannot be "
            "overridden by merchant configuration. For streaming, tokens stream "
            "in real-time and Critic validates post-stream — rejected responses "
            "trigger a retraction event (~800ms exposure at P50)."
        ),
        "tags": ["features", "safety", "critic", "validation", "content"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Human Agent Escalation",
        "content": (
            "Agent Red automatically detects when a conversation needs human "
            "attention (100% precision/recall). Triggers: customer frustration, "
            "topics requiring judgment (refunds, complaints), configurable keywords, "
            "configurable confidence threshold (default 0.7). On escalation: "
            "conversation transfers to human inbox with full history and context, "
            "WebSocket bidirectional communication activates, conversation ends "
            "for billing."
        ),
        "tags": ["features", "escalation", "human", "agent", "support"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Real-Time Analytics Dashboard",
        "content": (
            "Comprehensive analytics: conversation volume trends (daily/weekly/"
            "monthly), intent classification breakdown (17 categories), knowledge "
            "gap identification, usage metrics, per-conversation audit trail, "
            "CSV export. Advanced Analytics add-on ($149/month, Professional+ "
            "only) provides deeper insights, custom reports, and trend analysis."
        ),
        "tags": ["features", "analytics", "dashboard", "reporting"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Multi-Language Support",
        "content": (
            "Agent Red supports multi-language conversations. Primary language "
            "configured during onboarding. Additional languages via Multi-Language "
            "Pack add-on ($99/month, all tiers). Language roadmap: Spanish (Mexico) "
            "and French (Canada) near-term, Portuguese (Brazil) and UK English "
            "medium-term."
        ),
        "tags": ["features", "languages", "multi-language", "i18n"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Response Explainability",
        "content": (
            "For every AI response, a decision trace records: which customer "
            "profile factors influenced the response, which knowledge base "
            "articles were retrieved, which memory signals from past conversations "
            "were used, which A/B test variant was active, timing for each "
            "pipeline stage, and the Critic's assessment. Available in the "
            "admin Conversation Inbox."
        ),
        "tags": ["features", "explainability", "transparency", "trace"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 3: SHOPIFY & SETUP
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Shopify Integration Overview",
        "content": (
            "Agent Red integrates directly through the Shopify App Store via "
            "OAuth. It syncs: product catalog (read_products), customer profiles "
            "(read_customers), order data (read_orders), and inventory levels "
            "(read_inventory). This data powers Knowledge Retrieval and Customer "
            "Context (Layer 1). The Shopify integration is included on all tiers "
            "at no additional cost."
        ),
        "tags": ["shopify", "integration", "setup", "ecommerce"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "How to Install Agent Red on Shopify",
        "content": (
            "1) Find Agent Red in the Shopify App Store. "
            "2) Click Install and authorize permissions. "
            "3) Complete the 9-step onboarding wizard. "
            "4) The chat widget appears automatically via Theme App Extension. "
            "5) Customize appearance in Widget Configuration. "
            "No code changes required. Billing through Shopify's native system."
        ),
        "tags": ["shopify", "install", "setup", "onboarding"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Non-Shopify Installation (Stripe Direct)",
        "content": (
            "Without Shopify: 1) Choose plan and checkout via Stripe. "
            "2) Receive API key and widget key. 3) Log into standalone admin. "
            "4) Complete onboarding wizard. 5) Paste JavaScript snippet: "
            '<script src="https://cdn.agentred.com/widget.js" '
            'data-widget-key="pk_live_YOUR_KEY" '
            'data-position="bottom-right"></script>. '
            "Bundle: ~15-20 KB gzipped IIFE. Billing through Stripe."
        ),
        "tags": ["setup", "stripe", "non-shopify", "installation", "snippet"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Free Trial",
        "content": (
            "14-day free trial with: 50 conversations (hard cap), Layer 1 "
            "Persistent Customer Memory, 14-day history, 5 req/min rate limit, "
            "2 concurrent conversations. Full admin dashboard access. Demo data "
            "seeded. No credit card required. Configuration and KB preserved "
            "on upgrade."
        ),
        "tags": ["trial", "free", "getting-started", "evaluation"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Onboarding Wizard",
        "content": (
            "9-step guided setup: 1) Brand & Voice, 2) Languages, 3) Response "
            "Style, 4) Knowledge Base import, 5) Business Policies, 6) Escalation "
            "Rules, 7) Team Members, 8) Privacy & Memory, 9) Widget Appearance. "
            "Complete at your own pace. All settings changeable afterwards via "
            "Configuration page."
        ),
        "tags": ["onboarding", "wizard", "setup", "configuration"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 4: WIDGET CUSTOMIZATION
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Chat Widget Visual Customization",
        "content": (
            "Visual controls (no CSS needed): primary color, background color, "
            "position (bottom-right/left), horizontal/vertical offset, agent "
            "avatar, agent name/title, company logo, powered-by badge toggle, "
            "mobile display toggle, dark/light/auto mode. All changes take "
            "effect immediately."
        ),
        "tags": ["widget", "customization", "appearance", "design"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Chat Widget Behavior Settings",
        "content": (
            "Behavior controls: offline message text, auto-open after delay, "
            "operating hours schedule, offline behavior (AI only / form / hide), "
            "pre-chat form with configurable fields, post-chat rating "
            "(thumbs up/down + comment), notification sound toggle, "
            "file upload toggle."
        ),
        "tags": ["widget", "customization", "behavior", "settings"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Widget Technical Details",
        "content": (
            "Built with Preact (~4.5 KB core). Total: ~15-20 KB gzipped IIFE. "
            "Shadow DOM (closed) for launcher. iframe for conversation panel. "
            "Three channels: HTTP POST (messages), SSE (AI streaming), WebSocket "
            "(typing/presence). Auto-reconnect with exponential backoff. 15s SSE "
            "heartbeat. Event buffering with Last-Event-ID replay."
        ),
        "tags": ["widget", "technical", "performance", "architecture"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 5: BILLING & USAGE
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Three-Tier Consumption Model",
        "content": (
            "Tier 1 — Included Allowance: conversations included in platform "
            "fee at no extra cost. Tier 2 — Pack Balance: pre-purchased packs "
            "consumed FIFO (oldest first, 90-day expiry). Tier 3 — Overage: "
            "billed at tier rate (Starter $0.04, Professional $0.025, Enterprise "
            "$0.015). Metering is idempotent with daily Stripe reconciliation."
        ),
        "tags": ["billing", "metering", "usage", "consumption"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Usage Dashboard and Billing Transparency",
        "content": (
            "Real-time usage counters, daily volume charts, per-conversation "
            "billing detail (11-column CSV export), proactive alerts at 80%/100% "
            "of allowance, pack balance warnings, volume spike detection. "
            "Dispute resolution via per-conversation audit trail."
        ),
        "tags": ["billing", "dashboard", "transparency", "alerts"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 6: SECURITY & PRIVACY
    # ===================================================================
    {
        "entry_type": "policy",
        "title": "GDPR Compliance",
        "content": (
            "GDPR safeguards: full data export (Article 20), cascading data "
            "deletion (vectors, profiles, conversations, usage, KB, preferences, "
            "tenants), channel-specific grace periods (48hr Shopify, 30d Stripe), "
            "consent management for Memory Layers 2-4, PII scrubbing from logs "
            "(field-level classification), mandatory Shopify GDPR webhooks."
        ),
        "tags": ["security", "gdpr", "privacy", "compliance", "consent"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Data Security and Encryption",
        "content": (
            "PII tokenization (UUID tokens, Key Vault storage). Encryption at "
            "rest (CMK RSA-2048, 90-day rotation). TLS in transit. gRPC+TLS "
            "agent communication. Cosmos DB tenant_id partition key isolation. "
            "TenantScopedRepository validation on every read/write. NATS "
            "topic namespacing ({tenant_id}.{agent}). Per-tenant Key Vault "
            "secrets (tenant-{id}-{type})."
        ),
        "tags": ["security", "encryption", "pii", "isolation"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Data Retention Policies",
        "content": (
            "Three-tier retention: Hot (Cosmos DB, tier-based depth: Trial 14d, "
            "Starter 90d, Professional 365d, Enterprise unlimited), Warm (Blob "
            "Cool, Parquet, 90 days), Cold (Blob Archive, 7+ years). Audit logs: "
            "append-only, 1-year retention. Cosmos DB continuous 7-day PITR. "
            "Archival daily at 04:00 UTC, retention enforcement at 03:00 UTC."
        ),
        "tags": ["security", "retention", "data", "archival", "backup"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 7: SUPPORT & SLA
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Getting Help and Support",
        "content": (
            "Documentation site, admin dashboard contextual tooltips, email "
            "support at support@remakerdigital.com, Priority Support add-on "
            "($99/month, Starter/Professional). Usage Dashboard provides "
            "self-service billing investigation with real-time metrics, "
            "audit trails, and CSV exports."
        ),
        "tags": ["support", "help", "contact", "documentation"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "SLA Commitments",
        "content": (
            "Uptime: Starter 99.5%, Professional 99.9%, Enterprise 99.95%. "
            "API latency: P50 <1,500ms, P95 <2,000ms, P99 <5,000ms. "
            "RTO: Enterprise 4hr, Professional 8hr, Starter 24hr. "
            "Backup: 7-day PITR + 90-day warm + 7-year cold. "
            "Maintenance: Tuesdays 02:00-04:00 UTC, zero-downtime rolling deploy."
        ),
        "tags": ["support", "sla", "uptime", "latency", "performance"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 8: COMPETITIVE ADVANTAGES
    # ===================================================================
    {
        "entry_type": "product",
        "title": "Agent Red Pricing Advantage vs Competitors",
        "content": (
            "Agent Red is 4-21x cheaper than comparable platforms. Verified "
            "February 2026: vs Tidio (Starter $149 includes 1,000 conversations "
            "vs Tidio's higher per-conversation cost), vs Gorgias (per-ticket + "
            "AI add-on much more expensive at scale), vs Zendesk (higher base + "
            "per-agent pricing), vs Intercom (Fin AI per-resolution on top of "
            "platform fees), vs Re:amaze (fewer conversations at higher rates). "
            "Transparent model: no per-agent fees, no hidden charges."
        ),
        "tags": ["competitive", "pricing", "advantage", "comparison"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Why Choose Agent Red Over Competitors",
        "content": (
            "1) Persistent Customer Memory: 4-layer memory, no competitor "
            "confirmed per-customer vector RAG. 2) Transparent pricing with "
            "per-conversation audit. 3) Fail-closed safety (competitors "
            "typically fail-open). 4) P50 <1,500ms vs Intercom's 7,000ms "
            "(4.7x faster). 5) ~15-20 KB widget vs Tidio 40-60 KB, Intercom "
            "80-100 KB. 6) 4-21x cheaper across all tiers."
        ),
        "tags": ["competitive", "advantage", "differentiator"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 9: ADD-ONS
    # ===================================================================
    {
        "entry_type": "product",
        "title": "Available Add-On Modules",
        "content": (
            "Multi-Language Pack $99/mo (all tiers). Advanced Analytics $149/mo "
            "(Pro+). Mailchimp Integration $49/mo (Pro+). Google Analytics "
            "Integration $49/mo (Pro+). White-Label Package $399/mo (Enterprise). "
            "Priority Support $99/mo (Starter/Pro). Custom Integration Dev "
            "$299/mo (Enterprise). Dedicated Model Training $299/mo (Enterprise, "
            "Layer 4 fine-tuning)."
        ),
        "tags": ["addons", "modules", "pricing", "integrations"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 10: CONFIGURATION
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Merchant AI Configuration Controls",
        "content": (
            "Brand/Tone: name, voice, formality, response length. Policies: "
            "return policy, shipping info (injected into AI context). "
            "Escalation: threshold (0.0-1.0, default 0.7), trigger keywords. "
            "Custom Instructions: freeform (sandboxed, safety rules take "
            "precedence). Memory: toggle Layers 2-4, GDPR consent per customer. "
            "5-layer inheritance: platform > tier > tenant overrides. "
            "60-second cache with tenant-scoped invalidation."
        ),
        "tags": ["configuration", "ai", "behavior", "tuning", "merchant"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 11: ABOUT
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "About Remaker Digital",
        "content": (
            "Agent Red Customer Experience is built by Remaker Digital, "
            "a DBA of VanDusen & Palmeter, LLC (Delaware). Website: "
            "remakerdigital.com. Built on the AGNTCY open-source multi-agent "
            "platform with commercial multi-tenant infrastructure, advanced AI, "
            "enterprise integrations, and white-label capabilities."
        ),
        "tags": ["company", "about", "remaker", "legal"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 12: Q&A PAIRS — question-format entries for better vector
    # retrieval alignment (customer questions → direct answers)
    # ===================================================================
    {
        "entry_type": "faq",
        "title": "Q: How much does Agent Red cost?",
        "content": (
            "Agent Red has three pricing tiers: Starter at $149/month "
            "(1,000 conversations included), Professional at $399/month "
            "(5,000 conversations included), and Enterprise at $999/month "
            "(20,000 conversations included). All tiers get 17% off with "
            "annual billing. Overage rates: $0.04, $0.025, and $0.015 "
            "per conversation respectively."
        ),
        "tags": ["pricing", "cost", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: Do you offer a free trial?",
        "content": (
            "Yes! Agent Red offers a 14-day free trial. No credit card "
            "required. The trial includes 50 conversations, Layer 1 "
            "Persistent Customer Memory, and full admin dashboard access. "
            "Your configuration and knowledge base are preserved when you "
            "upgrade to a paid plan."
        ),
        "tags": ["trial", "free", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: What makes Agent Red different from Tidio or Gorgias?",
        "content": (
            "Three key differentiators: 1) Persistent Customer Memory — "
            "4-layer system where every conversation builds on the last, "
            "no competitor offers per-customer vector RAG. 2) Fail-closed "
            "safety — every AI response validated by Critic before delivery. "
            "3) Price — Agent Red is 4-21x cheaper than Tidio, Gorgias, "
            "Zendesk, Intercom, and Re:amaze."
        ),
        "tags": ["competitive", "comparison", "tidio", "gorgias", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: How do I install Agent Red on my Shopify store?",
        "content": (
            "Find Agent Red in the Shopify App Store, click Install, "
            "authorize the permissions, and complete the 9-step onboarding "
            "wizard. The chat widget appears automatically on your storefront "
            "via Shopify Theme App Extension. No code changes to your theme "
            "are needed. Billing goes through your regular Shopify invoice."
        ),
        "tags": ["shopify", "install", "setup", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: Can I use Agent Red without Shopify?",
        "content": (
            "Yes. Subscribe directly via Stripe on the Agent Red website. "
            "You will receive an API key and widget key. Log into the "
            "standalone admin dashboard, complete onboarding, and paste "
            "a JavaScript snippet onto your website. The widget works on "
            "any website — WordPress, Squarespace, custom sites, etc."
        ),
        "tags": ["stripe", "non-shopify", "installation", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: Is Agent Red GDPR compliant?",
        "content": (
            "Yes. Agent Red provides full GDPR compliance: data export "
            "(Article 20 portability), data deletion with cascading cleanup, "
            "consent management for AI memory features, PII scrubbing from "
            "all logs, and mandatory Shopify GDPR webhooks. Persistent "
            "Customer Memory Layers 2-4 require explicit consent."
        ),
        "tags": ["gdpr", "privacy", "compliance", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: How fast are Agent Red's AI responses?",
        "content": (
            "Agent Red targets P50 (median) latency under 1,500 milliseconds, "
            "P95 under 2,000ms, and P99 under 5,000ms. For comparison, "
            "Intercom's published P50 is 7,000ms — Agent Red is approximately "
            "4.7 times faster. Responses stream in real-time via SSE so "
            "customers see text appearing immediately."
        ),
        "tags": ["performance", "latency", "speed", "sla", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: What is Persistent Customer Memory?",
        "content": (
            "Agent Red's signature feature. Every conversation builds on "
            "previous ones. Layer 1: Customer profile (purchase history, "
            "preferences). Layer 2: Vectorized conversation history for "
            "semantic search. Layer 3: Extracted patterns and communication "
            "style. Layer 4: Per-customer AI fine-tuning. No competitor "
            "offers this level of personalization."
        ),
        "tags": ["memory", "personalization", "differentiator", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: How do I customize the chat widget?",
        "content": (
            "In the admin dashboard, go to Widget Configuration. You can "
            "change colors, position, agent name/avatar, greeting text, "
            "dark/light mode, auto-open behavior, pre-chat form fields, "
            "operating hours, and more — all through named controls, no "
            "CSS coding needed. Changes take effect immediately."
        ),
        "tags": ["widget", "customization", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: What happens when the AI can't answer a question?",
        "content": (
            "Agent Red's Escalation Agent detects when human help is needed "
            "(100% precision/recall). The conversation is automatically "
            "transferred to your human agent inbox with full history and "
            "context. Your team can respond via WebSocket in real-time. "
            "You can also set custom escalation keywords and confidence "
            "thresholds."
        ),
        "tags": ["escalation", "human", "support", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: Can I cancel my subscription anytime?",
        "content": (
            "Yes. You can cancel your Agent Red subscription at any time. "
            "For Shopify merchants, cancellation goes through Shopify's "
            "standard app uninstall process. For Stripe direct customers, "
            "cancel from the Billing page in the admin dashboard. Your "
            "data is retained per the channel-specific grace period "
            "(48 hours Shopify, 30 days Stripe)."
        ),
        "tags": ["billing", "cancel", "subscription", "qa"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Q: What add-ons are available?",
        "content": (
            "8 add-ons: Multi-Language ($99/mo, all tiers), Advanced Analytics "
            "($149/mo, Pro+), Mailchimp ($49/mo, Pro+), Google Analytics "
            "($49/mo, Pro+), White-Label ($399/mo, Enterprise), Priority "
            "Support ($99/mo, Starter/Pro), Custom Integration ($299/mo, "
            "Enterprise), Dedicated Model Training ($299/mo, Enterprise)."
        ),
        "tags": ["addons", "modules", "pricing", "qa"],
        "is_active": True,
    },

    # ===================================================================
    # SECTION 13: REMAKER DIGITAL STORE PRODUCT DATA
    # ===================================================================
    {
        "entry_type": "product",
        "title": "Remaker Digital — Company Overview",
        "content": (
            "Remaker Digital builds AI-powered tools for e-commerce merchants. "
            "Our flagship product is Agent Red Customer Experience, an AI "
            "customer service platform that provides 24/7 automated support "
            "with persistent customer memory. Based in Delaware, USA. "
            "Website: remakerdigital.com."
        ),
        "tags": ["remaker", "company", "products", "store"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Remaker Digital — Products We Sell",
        "content": (
            "Remaker Digital sells Agent Red Customer Experience, an AI "
            "customer service SaaS platform. Available in three tiers "
            "(Starter $149/mo, Professional $399/mo, Enterprise $999/mo) "
            "plus 8 add-on modules. Purchase via Shopify App Store or "
            "directly via Stripe. 14-day free trial available."
        ),
        "tags": ["remaker", "products", "store", "purchase"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Remaker Digital — Refund and Cancellation Policy",
        "content": (
            "You can cancel your Agent Red subscription at any time. "
            "Shopify: cancellation via app uninstall, prorated to current "
            "billing cycle. Stripe: cancel from admin dashboard Billing page. "
            "Annual prepaid subscriptions are non-refundable but service "
            "continues until end of paid period. Conversation packs are "
            "non-refundable but remain valid for 90 days."
        ),
        "tags": ["refund", "cancellation", "policy", "store"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Remaker Digital — Shipping and Delivery",
        "content": (
            "Agent Red is a cloud-based SaaS product. There is no physical "
            "shipping. Access is instant: after completing checkout (Shopify "
            "or Stripe), your account is provisioned immediately and you "
            "can begin configuring your AI assistant right away. API keys "
            "and widget keys are delivered electronically."
        ),
        "tags": ["shipping", "delivery", "saas", "access", "store"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Remaker Digital — Contact and Support",
        "content": (
            "Email: support@remakerdigital.com. Documentation available at "
            "docs.agentred.com. In-app contextual help tooltips throughout "
            "the admin dashboard. Priority Support add-on ($99/month) for "
            "faster response times (Starter and Professional tiers)."
        ),
        "tags": ["contact", "support", "store", "help"],
        "is_active": True,
    },
]

# ---------------------------------------------------------------------------
# Article count and summary statistics
# ---------------------------------------------------------------------------

TOTAL_ARTICLES = len(SEED_ARTICLES)


def print_summary() -> None:
    """Print a summary of the seed articles."""
    print(f"\nAgent Red Knowledge Base Seed Data (v2.0 — Optimized)")
    print(f"{'=' * 55}")
    print(f"Total articles: {TOTAL_ARTICLES}")
    print()

    # Count by entry_type
    type_counts: dict[str, int] = {}
    for article in SEED_ARTICLES:
        t = article["entry_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print("By entry type:")
    for entry_type, count in sorted(type_counts.items()):
        print(f"  {entry_type}: {count}")
    print()

    # Count by section
    qa_count = sum(1 for a in SEED_ARTICLES if a["title"].startswith("Q:"))
    store_count = sum(1 for a in SEED_ARTICLES if "store" in a.get("tags", []))
    reference_count = TOTAL_ARTICLES - qa_count - store_count

    print(f"By content type:")
    print(f"  Reference articles: {reference_count}")
    print(f"  Q&A pairs: {qa_count}")
    print(f"  Store product data: {store_count}")
    print()

    # Count by tag
    tag_counts: dict[str, int] = {}
    for article in SEED_ARTICLES:
        for tag in article.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print(f"Unique tags: {len(tag_counts)}")
    print("Top 15 tags:")
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:15]:
        print(f"  {tag}: {count}")
    print()

    # Content statistics
    content_lengths = [len(a["content"]) for a in SEED_ARTICLES]
    total_chars = sum(content_lengths)
    avg_chars = total_chars // TOTAL_ARTICLES
    min_chars = min(content_lengths)
    max_chars = max(content_lengths)

    print(f"Content statistics:")
    print(f"  Total: {total_chars:,} characters")
    print(f"  Average: {avg_chars} chars/article")
    print(f"  Range: {min_chars}-{max_chars} chars/article")
    print()

    # Article listing
    print("Articles:")
    print(f"  {'#':<4} {'Type':<10} {'Chars':<7} {'Title'}")
    print(f"  {'='*4} {'='*10} {'='*7} {'='*50}")
    for i, article in enumerate(SEED_ARTICLES, 1):
        print(f"  {i:<4} {article['entry_type']:<10} {len(article['content']):<7} {article['title']}")
    print()


# ---------------------------------------------------------------------------
# Cosmos DB loader
# ---------------------------------------------------------------------------


async def load_to_cosmos(
    tenant_id: str,
    dry_run: bool = False,
    embed: bool = False,
) -> None:
    """Load seed articles into Cosmos DB via KnowledgeBaseRepository.

    Args:
        tenant_id: The tenant ID to associate articles with.
        dry_run: If True, build documents but do not persist.
        embed: If True, embed all articles after loading (requires Azure OpenAI).
    """
    # Add src to path so we can import the multi_tenant modules
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument
    from src.multi_tenant.repository import KnowledgeBaseRepository
    from src.multi_tenant.knowledge_vectorizer import compute_content_hash

    repo = KnowledgeBaseRepository()
    now = datetime.now(timezone.utc).isoformat()

    # Idempotency: fetch existing active titles to avoid duplicates
    existing = await repo.list_active(tenant_id)
    existing_titles = {e.get("title", "") for e in existing}
    if existing_titles:
        print(f"  Found {len(existing_titles)} existing active entries — will skip duplicates", flush=True)

    created = 0
    skipped = 0
    errors = 0

    for article in SEED_ARTICLES:
        # Skip articles that already exist (title-based dedup)
        if article["title"] in existing_titles:
            print(f"  [SKIP] Already exists: {article['title']}")
            skipped += 1
            continue

        entry_id = str(uuid.uuid4())
        content_hash = compute_content_hash(article["title"], article["content"])
        doc = KnowledgeBaseDocument(
            id=entry_id,
            tenant_id=tenant_id,
            entry_type=article["entry_type"],
            title=article["title"],
            content=article["content"],
            metadata=article.get("metadata", {}),
            tags=article.get("tags", []),
            language=article.get("language", "en"),
            is_active=article.get("is_active", True),
            content_hash=content_hash,
            created_at=now,
            updated_at=now,
        )

        if dry_run:
            print(f"  [DRY RUN] Would create: {article['title']} ({entry_id})")
            created += 1
            continue

        try:
            await repo.create(tenant_id, doc)
            print(f"  Created: {article['title']} ({entry_id})")
            created += 1
        except Exception as e:
            print(f"  ERROR creating '{article['title']}': {e}")
            errors += 1
            logger.exception("Failed to create knowledge entry: %s", article["title"])

    print(f"\nLoad complete: {created} created, {skipped} skipped, {errors} errors")

    # Embed all unembedded articles if requested
    if embed and not dry_run and created > 0:
        print(f"\nEmbedding {created} new articles...")
        try:
            from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

            vectorizer = get_knowledge_vectorizer()
            if not vectorizer._configured:
                # Try to configure with Azure OpenAI
                from src.chat.pipeline import _create_openai_client
                openai_client = _create_openai_client()
                vectorizer.configure(kb_repo=repo, openai_client=openai_client)

            embedded = await vectorizer.embed_unembedded(tenant_id)
            print(f"Embedding complete: {embedded} articles embedded")
        except Exception as e:
            print(f"Embedding failed: {e}")
            print("Articles loaded but not embedded. Run with Azure OpenAI "
                  "credentials to enable vector search.")


async def main() -> None:
    """Entry point for loading seed data."""
    parser = argparse.ArgumentParser(
        description="Agent Red Knowledge Base Seed Data (v2.0)",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load articles into Cosmos DB (requires Azure credentials)",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default="remaker-digital-001",
        help="Tenant ID (default: remaker-digital-001)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build documents but do not persist to database",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Embed all articles after loading (requires Azure OpenAI)",
    )
    args = parser.parse_args()

    print_summary()

    if args.load or args.dry_run:
        print(f"Loading {TOTAL_ARTICLES} articles for tenant: {args.tenant_id}")
        if args.dry_run:
            print("(Dry run mode - no database writes)")
        if args.embed:
            print("(Embedding enabled — will vectorize after loading)")
        print()
        await load_to_cosmos(
            tenant_id=args.tenant_id,
            dry_run=args.dry_run,
            embed=args.embed,
        )
    else:
        print("To load into Cosmos DB, run with --load (or --dry-run to preview)")
        print("  python scripts/seed_knowledge_base.py --load --tenant-id <TENANT_ID>")
        print("  python scripts/seed_knowledge_base.py --load --embed")
        print("  python scripts/seed_knowledge_base.py --dry-run")


if __name__ == "__main__":
    asyncio.run(main())
