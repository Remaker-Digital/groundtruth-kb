"""
Seed knowledge base data for the Remaker Digital demo storefront.

Loads Agent Red product knowledge into the knowledge base so the
chat widget's AI assistant can answer customer questions about the
product. Articles cover pricing, features, integrations, setup,
billing, security, support, competitive advantages, and add-ons.

Usage:
    # Print summary of seed articles (no DB required):
    python scripts/seed_knowledge_base.py

    # Load into Cosmos DB (requires Azure credentials in .env.local):
    python scripts/seed_knowledge_base.py --load

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
# Seed data
# ---------------------------------------------------------------------------

SEED_ARTICLES: list[dict] = [
    # -----------------------------------------------------------------------
    # 1. PRICING & PLANS
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Agent Red Pricing Overview",
        "content": (
            "Agent Red Customer Experience uses a Platform Fee plus Metered AI Usage "
            "pricing model. Each tier includes a monthly platform fee covering "
            "infrastructure, features, and support, along with a monthly conversation "
            "allowance. Conversations beyond the included allowance are billed at "
            "tiered overage rates.\n\n"
            "Tiers:\n"
            "- Starter: $149/month (or $124/month billed annually at $1,490/year). "
            "Includes 1,000 conversations per month. Overage rate: $0.04 per conversation.\n"
            "- Professional: $399/month (or $332/month billed annually at $3,990/year). "
            "Includes 5,000 conversations per month. Overage rate: $0.025 per conversation.\n"
            "- Enterprise: $999/month (or $832/month billed annually at $9,990/year). "
            "Includes 20,000 conversations per month. Overage rate: $0.015 per conversation.\n\n"
            "Annual billing saves 17% compared to monthly billing on all tiers."
        ),
        "tags": ["pricing", "plans", "tiers", "cost", "monthly", "annual"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Conversation Packs",
        "content": (
            "Conversation Packs let you pre-purchase conversations at discounted rates. "
            "Packs are valid for 90 days from purchase and are consumed before overage "
            "billing kicks in (FIFO: oldest pack consumed first).\n\n"
            "Available packs:\n"
            "- 1,000 conversations: $29 (effective rate: $0.029/conversation)\n"
            "- 5,000 conversations: $99 (effective rate: $0.020/conversation)\n"
            "- 20,000 conversations: $249 (effective rate: $0.012/conversation)\n\n"
            "Packs can be purchased on any tier. The consumption order is: "
            "included monthly allowance first, then pack balance (oldest first), "
            "then overage billing."
        ),
        "tags": ["pricing", "packs", "conversations", "prepaid", "overage"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Annual Billing Discount",
        "content": (
            "All Agent Red tiers offer a 17% discount when billed annually:\n\n"
            "- Starter: $124/month ($1,490/year) instead of $149/month\n"
            "- Professional: $332/month ($3,990/year) instead of $399/month\n"
            "- Enterprise: $832/month ($9,990/year) instead of $999/month\n\n"
            "You can switch between monthly and annual billing at any time. "
            "Annual billing is charged upfront for the full year."
        ),
        "tags": ["pricing", "annual", "discount", "billing"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "What Counts as a Billable Conversation?",
        "content": (
            "A billable conversation starts when a customer sends their first message "
            "and ends when any of these conditions are met:\n"
            "- 30 minutes of inactivity (idle timeout)\n"
            "- The customer explicitly ends the conversation\n"
            "- The conversation is escalated to a human agent\n"
            "- The conversation reaches 50 turns (AI message exchanges)\n\n"
            "The following are NOT billable:\n"
            "- Conversations prefixed with test_, admin_, health_, or system_\n"
            "- Conversations where no AI response was generated before an error occurred\n\n"
            "You can view detailed per-conversation billing information in the Usage "
            "Dashboard, including conversation IDs, timestamps, message counts, and "
            "which billing tier (included, pack, or overage) was applied."
        ),
        "tags": ["billing", "conversations", "metering", "usage"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 2. CORE FEATURES
    # -----------------------------------------------------------------------
    {
        "entry_type": "product",
        "title": "Six Specialized AI Agents",
        "content": (
            "Agent Red Customer Experience is powered by six specialized AI agents "
            "that work together in a pipeline to handle customer conversations:\n\n"
            "1. Intent Classification Agent: Routes customer queries across 17 intent "
            "categories with 98% accuracy. Powered by GPT-4o-mini.\n"
            "2. Knowledge Retrieval Agent: Searches your product catalog, FAQs, and "
            "policies to find relevant information. Uses text-embedding-3-large for "
            "100% retrieval accuracy.\n"
            "3. Response Generation Agent: Crafts personalized, on-brand responses "
            "using GPT-4o with 88.4% quality rating.\n"
            "4. Escalation Agent: Detects cases that need human attention with 100% "
            "precision and recall. Powered by GPT-4o-mini.\n"
            "5. Analytics Agent: Monitors performance metrics and identifies trends "
            "in customer conversations.\n"
            "6. Critic/Supervisor Agent: Validates every AI response for content safety "
            "before delivery. Fail-closed design means responses are blocked unless "
            "explicitly approved by the Critic. 0% false positive rate, 100% true "
            "positive rate.\n\n"
            "All six agents run in every conversation, ensuring consistent quality, "
            "safety, and accurate responses."
        ),
        "tags": ["features", "agents", "ai", "pipeline", "safety"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Persistent Customer Memory",
        "content": (
            "Persistent Customer Memory is Agent Red's signature differentiator. "
            "Every conversation builds on the last, creating a personalized experience "
            "that improves over time. It operates across four layers:\n\n"
            "Layer 1 - Customer Context (All tiers): Structured profile data including "
            "purchase history, cart contents, geographic region, marketing segments, "
            "jurisdiction codes, and product question history. Injected into every "
            "conversation as context (~250 tokens).\n\n"
            "Layer 2 - Conversation Memory (All tiers): Vectorized transcripts of past "
            "conversations enable semantic search across a customer's full interaction "
            "history. History depth varies by tier: Starter 90 days, Professional 365 "
            "days, Enterprise unlimited.\n\n"
            "Layer 3 - Cross-Session Learning (Professional and Enterprise): Automatically "
            "extracts patterns, preferences, and communication style from conversations. "
            "Patterns have confidence scores (0-1) and decay over time (0.05/month) to "
            "stay current.\n\n"
            "Layer 4 - Dedicated Model Training (Enterprise add-on, $299/month): "
            "Per-customer AI fine-tuning on 1,000+ historical interactions for maximum "
            "personalization. Monthly training pipeline with quality gates and A/B "
            "validation.\n\n"
            "No competitor has confirmed implementing per-customer vector RAG over "
            "historical transcripts. Marginal cost: approximately $0.01 per customer "
            "per month for Layers 1-2."
        ),
        "tags": ["features", "memory", "personalization", "differentiator", "ai"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Multi-Language Support",
        "content": (
            "Agent Red supports multi-language customer conversations. The Intent "
            "Classification Agent detects the customer's language and routes to the "
            "appropriate Response Generation Agent instance.\n\n"
            "Primary language is configured during onboarding. Additional languages "
            "can be enabled with the Multi-Language Pack add-on ($99/month), which is "
            "available on all tiers.\n\n"
            "Language priority roadmap: Spanish (Mexico) and French (Canada) near-term, "
            "Portuguese (Brazil) and UK English medium-term."
        ),
        "tags": ["features", "languages", "multi-language", "i18n", "localization"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Real-Time Analytics Dashboard",
        "content": (
            "Agent Red provides a comprehensive analytics dashboard with real-time "
            "insights into your customer service operations:\n\n"
            "- Conversation volume trends (daily, weekly, monthly)\n"
            "- Intent classification breakdown across 17 categories\n"
            "- Knowledge gap identification (questions the AI could not answer)\n"
            "- Usage metrics and billing transparency\n"
            "- Per-conversation audit trail with billing detail\n"
            "- CSV export for all billing and conversation data\n\n"
            "The Advanced Analytics add-on ($149/month, available on Professional "
            "and Enterprise tiers) provides deeper insights, custom reports, and "
            "trend analysis."
        ),
        "tags": ["features", "analytics", "dashboard", "reporting", "insights"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "AI Response Safety and Content Validation",
        "content": (
            "Agent Red uses a fail-closed Critic/Supervisor system to validate every "
            "AI response before it reaches your customers. This means:\n\n"
            "- Every response must be explicitly approved by the Critic agent\n"
            "- If the Critic rejects, times out, or encounters an error, the response "
            "is blocked and a safe fallback message is shown instead\n"
            "- The Critic's system prompt is immutable and cannot be overridden by "
            "merchant configuration or custom instructions\n"
            "- For streaming responses, tokens stream in real-time and the Critic "
            "validates post-stream. If rejected, a retraction event replaces the "
            "displayed text with the safe fallback (approximately 800ms exposure "
            "window at P50)\n\n"
            "This defense-in-depth approach ensures that your brand is never "
            "compromised by unexpected AI behavior."
        ),
        "tags": ["features", "safety", "critic", "validation", "content"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Human Agent Escalation",
        "content": (
            "Agent Red automatically detects when a conversation requires human "
            "attention using a dedicated Escalation Agent with 100% precision and "
            "recall. Escalation triggers include:\n\n"
            "- Customer sentiment indicating frustration or urgency\n"
            "- Topics requiring human judgment (refunds, complaints, complex issues)\n"
            "- Configurable escalation keywords set by the merchant\n"
            "- Configurable confidence threshold (default 0.7, adjustable 0.0-1.0)\n\n"
            "When a conversation is escalated:\n"
            "- The conversation is transferred to the human agent inbox\n"
            "- Full conversation history and customer context are available\n"
            "- WebSocket provides real-time bidirectional communication between "
            "the human agent and the customer\n"
            "- The conversation is ended for billing purposes at the point of escalation\n\n"
            "Team members can be assigned roles (Owner, Admin, Agent, Viewer) with "
            "configurable concurrent conversation limits."
        ),
        "tags": ["features", "escalation", "human", "agent", "support"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 3. SHOPIFY INTEGRATION
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Shopify Integration Overview",
        "content": (
            "Agent Red integrates directly with Shopify through the Shopify App Store. "
            "The integration uses OAuth for secure authentication and syncs the "
            "following data from your Shopify store:\n\n"
            "- Product catalog (read_products scope): Product names, descriptions, "
            "prices, variants, inventory status\n"
            "- Customer data (read_customers scope): Customer profiles, order history, "
            "contact information\n"
            "- Order data (read_orders scope): Order status, tracking, fulfillment details\n"
            "- Inventory levels (read_inventory scope): Real-time stock availability\n\n"
            "This data powers the Knowledge Retrieval Agent and Customer Context "
            "(Layer 1 of Persistent Customer Memory), enabling the AI to answer "
            "questions about your specific products, check order status, and provide "
            "personalized recommendations.\n\n"
            "The Shopify integration is included at no additional cost on all tiers."
        ),
        "tags": ["shopify", "integration", "setup", "ecommerce", "sync"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "How to Install Agent Red on Shopify",
        "content": (
            "Installing Agent Red on your Shopify store takes just a few steps:\n\n"
            "1. Find Agent Red Customer Experience in the Shopify App Store\n"
            "2. Click Install and authorize the requested permissions "
            "(read_orders, read_products, read_customers, read_inventory)\n"
            "3. Complete the 9-step onboarding wizard in the embedded admin dashboard\n"
            "4. The chat widget is delivered as a Shopify Theme App Extension (app embed "
            "block) and appears automatically on your storefront\n"
            "5. Customize the widget appearance and behavior from the Widget Configuration page\n\n"
            "No code changes to your theme are required. The widget loads in an "
            "isolated iframe with Shadow DOM for the launcher button, ensuring it "
            "does not interfere with your theme's styling.\n\n"
            "Billing for Shopify merchants goes through Shopify's native billing system. "
            "All charges appear on your regular Shopify invoice."
        ),
        "tags": ["shopify", "install", "setup", "onboarding", "widget"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 4. WIDGET CUSTOMIZATION
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Chat Widget Customization",
        "content": (
            "Agent Red's chat widget offers extensive customization through named "
            "controls in the admin dashboard. No custom CSS is needed.\n\n"
            "Visual controls:\n"
            "- Primary color (header and buttons)\n"
            "- Background color (conversation panel)\n"
            "- Position (bottom-right or bottom-left)\n"
            "- Horizontal and vertical offset from screen edge\n"
            "- Agent avatar image URL\n"
            "- Agent display name and title\n"
            "- Company logo in header\n"
            "- Powered by Agent Red badge (can be hidden)\n"
            "- Mobile display toggle\n"
            "- Dark mode / light mode / auto\n\n"
            "Behavior controls:\n"
            "- Offline message text\n"
            "- Auto-open after configurable delay\n"
            "- Operating hours schedule\n"
            "- Offline behavior (AI only, show form, or hide widget)\n"
            "- Pre-chat form with configurable fields\n"
            "- Post-chat rating (thumbs up/down with optional comment)\n"
            "- Notification sound toggle\n"
            "- File upload toggle\n\n"
            "Content controls:\n"
            "- Custom header text\n"
            "- Input placeholder text\n"
            "- Page rules (URL patterns controlling where the widget appears)\n\n"
            "All changes take effect immediately without republishing your store."
        ),
        "tags": ["widget", "customization", "appearance", "design", "branding"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Widget Dark Mode",
        "content": (
            "The Agent Red chat widget supports three color mode settings:\n\n"
            "- Light mode: Standard light background with dark text\n"
            "- Dark mode: Dark background with light text, matching dark-themed storefronts\n"
            "- Auto: Follows the visitor's system or browser dark mode preference\n\n"
            "Dark mode applies to the entire widget including the launcher button, "
            "conversation panel, message bubbles, input bar, and all forms "
            "(pre-chat, rating, offline). The color mode can be configured in the "
            "Widget Configuration page of the admin dashboard."
        ),
        "tags": ["widget", "dark-mode", "light-mode", "theme", "appearance"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 5. GETTING STARTED
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Free Trial",
        "content": (
            "Agent Red offers a 14-day free trial so you can evaluate the platform "
            "before committing to a paid plan.\n\n"
            "Trial includes:\n"
            "- 50 conversations (hard cap, no overage)\n"
            "- Layer 1 Persistent Customer Memory (Customer Context)\n"
            "- 14-day conversation history retention\n"
            "- 5 requests per minute rate limit\n"
            "- 2 concurrent conversations\n\n"
            "During the trial, you can access the full admin dashboard, configure "
            "your AI assistant's behavior, customize the widget, and test with real "
            "customer conversations. Demo data is seeded into your account so you can "
            "explore all features immediately.\n\n"
            "No credit card is required to start a trial. When the trial ends, you "
            "can upgrade to any paid tier to continue. Your configuration, knowledge "
            "base, and conversation history are preserved when you upgrade."
        ),
        "tags": ["trial", "free", "getting-started", "evaluation", "demo"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Onboarding Wizard",
        "content": (
            "Agent Red includes a 9-step onboarding wizard that guides you through "
            "initial configuration:\n\n"
            "Step 1: Brand & Voice - Set your brand name and tone (friendly, formal, etc.)\n"
            "Step 2: Languages - Choose primary and additional support languages\n"
            "Step 3: Response Style - Configure response length and formality level\n"
            "Step 4: Knowledge Base - Import products, FAQs, and policies\n"
            "Step 5: Business Policies - Add return policy and shipping information\n"
            "Step 6: Escalation Rules - Set escalation threshold and trigger keywords\n"
            "Step 7: Team Members - Invite team members for human agent escalation\n"
            "Step 8: Privacy & Memory - Configure GDPR consent and memory settings\n"
            "Step 9: Widget Appearance - Customize the chat widget look and feel\n\n"
            "You can complete the wizard at your own pace and return to any step "
            "later. All settings can be changed after onboarding through the "
            "Configuration page."
        ),
        "tags": ["onboarding", "wizard", "setup", "configuration", "getting-started"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Non-Shopify Installation (Stripe Direct)",
        "content": (
            "If you do not use Shopify, you can subscribe to Agent Red directly via "
            "Stripe. The setup process:\n\n"
            "1. Choose your plan on the Agent Red website and complete checkout via Stripe\n"
            "2. Receive your API key and widget key after tenant provisioning\n"
            "3. Log into the standalone admin dashboard using your API key\n"
            "4. Complete the onboarding wizard\n"
            "5. Add the widget to your website by pasting a JavaScript snippet:\n\n"
            '   <script src="https://cdn.agentred.com/widget.js"\n'
            '     data-widget-key="pk_live_YOUR_KEY"\n'
            '     data-position="bottom-right"></script>\n\n'
            "The widget loads as a single IIFE bundle (approximately 15-20 KB gzipped) "
            "and renders in an isolated iframe, so it will not conflict with your site's "
            "styling or scripts.\n\n"
            "Billing goes through Stripe. You can manage your subscription, view invoices, "
            "and update payment methods through the Billing page in the admin dashboard."
        ),
        "tags": ["setup", "stripe", "non-shopify", "installation", "widget", "snippet"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 6. BILLING & USAGE
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "How Metering and Billing Works",
        "content": (
            "Agent Red uses a three-tier consumption model for conversations:\n\n"
            "Tier 1 - Included Allowance: Each plan includes a monthly conversation "
            "allowance (Starter: 1,000, Professional: 5,000, Enterprise: 20,000). "
            "These conversations are included in your platform fee at no extra cost.\n\n"
            "Tier 2 - Pack Balance: If you have purchased Conversation Packs, "
            "conversations beyond your included allowance consume pack balance. "
            "Packs are consumed FIFO (oldest first) and expire after 90 days.\n\n"
            "Tier 3 - Overage: If both your included allowance and pack balance are "
            "exhausted, additional conversations are billed at the overage rate for "
            "your tier (Starter: $0.04, Professional: $0.025, Enterprise: $0.015).\n\n"
            "Metering is idempotent (each conversation is counted exactly once) and "
            "daily reconciliation runs against Stripe's billing meter to ensure accuracy. "
            "Any discrepancy greater than 5% is flagged for review."
        ),
        "tags": ["billing", "metering", "usage", "overage", "consumption"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Usage Dashboard and Billing Transparency",
        "content": (
            "Agent Red prioritizes billing transparency. The Usage Dashboard provides:\n\n"
            "- Real-time usage counters: total conversations, included remaining, "
            "pack balance, overage count\n"
            "- Daily volume charts showing conversation trends\n"
            "- Per-conversation billing detail: conversation ID, status, customer, "
            "message count, turn count, timestamps, agents invoked, model used, "
            "Critic pass/fail, and billing tier applied\n"
            "- CSV export of all billable conversations (11 columns)\n"
            "- Proactive alerts at 80% and 100% of monthly allowance\n"
            "- Pack balance low warnings\n"
            "- Volume spike detection\n\n"
            "If you believe a billing discrepancy exists, you can use the "
            "per-conversation audit trail and CSV export to identify specific "
            "conversations for dispute resolution."
        ),
        "tags": ["billing", "dashboard", "transparency", "usage", "alerts", "export"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 7. SECURITY & PRIVACY
    # -----------------------------------------------------------------------
    {
        "entry_type": "policy",
        "title": "GDPR Compliance",
        "content": (
            "Agent Red is designed for GDPR compliance with the following safeguards:\n\n"
            "Data Export: You can request a full data export of all customer data at "
            "any time through the admin dashboard (GDPR Article 20 - data portability).\n\n"
            "Data Deletion: Customer data can be deleted on request. Cascading deletion "
            "removes data in order: memory vectors, customer profiles, conversations, "
            "usage records, knowledge bases, preferences, and tenant records. "
            "Channel-specific grace periods apply: 48 hours for Shopify merchants, "
            "30 days for Stripe direct merchants.\n\n"
            "Consent Management: Persistent Customer Memory Layers 2-4 (conversation "
            "memory, cross-session learning, and dedicated model training) require "
            "explicit consent. If consent is denied, Layers 2-4 data is automatically "
            "deleted. Layer 1 (basic profile) operates without separate consent as it "
            "is necessary for service delivery.\n\n"
            "PII Scrubbing: All personally identifiable information is scrubbed from "
            "logs before storage. PII is classified at the field level (direct, indirect, "
            "sensitive) and removed from Application Insights telemetry.\n\n"
            "Mandatory Shopify GDPR webhooks (customers/data_request, customers/redact, "
            "shop/redact) are fully implemented."
        ),
        "tags": ["security", "gdpr", "privacy", "compliance", "data", "consent"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Data Security and Encryption",
        "content": (
            "Agent Red employs multiple layers of data security:\n\n"
            "PII Tokenization: Customer PII is tokenized using random UUID tokens "
            "(format: TOKEN_a7f3c9e1-4b2d-8f6a-9c3e) before being sent to any "
            "third-party AI service. Token mappings are stored in Azure Key Vault "
            "(primary) with Cosmos DB fallback.\n\n"
            "Encryption at Rest: All data is encrypted using Customer-Managed Keys "
            "(CMK) with RSA-2048 and 90-day automatic rotation via Azure Key Vault.\n\n"
            "Encryption in Transit: All communications use TLS. Agent-to-agent "
            "communication uses gRPC + TLS via SLIM transport.\n\n"
            "Tenant Isolation: Cosmos DB uses tenant_id as the partition key, ensuring "
            "data isolation at the storage layer. Every database operation is routed "
            "through the TenantScopedRepository, which validates tenant_id on every "
            "read and write.\n\n"
            "NATS Isolation: Message topics are namespaced per tenant "
            "(format: {tenant_id}.{agent}), preventing cross-tenant message leaks.\n\n"
            "Secrets Management: Per-tenant secrets are stored in Azure Key Vault "
            "with naming convention tenant-{id}-{type}."
        ),
        "tags": ["security", "encryption", "pii", "isolation", "keyvault"],
        "is_active": True,
    },
    {
        "entry_type": "policy",
        "title": "Data Retention Policies",
        "content": (
            "Agent Red uses a three-tier data retention model:\n\n"
            "Hot Storage (Cosmos DB): Active conversation data and customer profiles. "
            "Retention depends on tier-based conversation history depth:\n"
            "- Trial: 14 days\n"
            "- Starter: 90 days\n"
            "- Professional: 365 days\n"
            "- Enterprise: Unlimited\n\n"
            "Warm Storage (Azure Blob Cool tier): Archived conversations in Parquet "
            "format, moved from hot storage after the tier's history depth. Retained "
            "for 90 days.\n\n"
            "Cold Storage (Azure Blob Archive tier): Long-term archival for compliance. "
            "Retained for 7+ years.\n\n"
            "Audit Logs: Append-only, 1-year retention. Cannot be modified or deleted "
            "(survives tenant deletion).\n\n"
            "Cosmos DB Backup: Continuous 7-day point-in-time restore (PITR).\n\n"
            "Automated archival runs daily at 04:00 UTC. Data retention enforcement "
            "runs daily at 03:00 UTC."
        ),
        "tags": ["security", "retention", "data", "archival", "backup", "compliance"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 8. SUPPORT
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Getting Help and Support",
        "content": (
            "Agent Red offers support through multiple channels:\n\n"
            "- Documentation site with getting-started guides, integration guides, "
            "and API reference\n"
            "- Admin dashboard with contextual help tooltips, documentation links, "
            "and the onboarding wizard\n"
            "- Email support at support@remakerdigital.com\n"
            "- Priority Support Upgrade add-on ($99/month) available on Starter and "
            "Professional tiers for faster response times\n\n"
            "For billing questions, the Usage Dashboard provides real-time metrics, "
            "per-conversation audit trails, and CSV exports for self-service "
            "investigation."
        ),
        "tags": ["support", "help", "contact", "documentation"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "SLA Commitments",
        "content": (
            "Agent Red provides tier-based SLA commitments:\n\n"
            "Uptime:\n"
            "- Starter: 99.5%\n"
            "- Professional: 99.9%\n"
            "- Enterprise: 99.95%\n\n"
            "API Latency:\n"
            "- P50 (median): less than 1,500 milliseconds\n"
            "- P95: less than 2,000 milliseconds\n"
            "- P99: less than 5,000 milliseconds\n\n"
            "Recovery:\n"
            "- Enterprise RTO: 4 hours\n"
            "- Professional RTO: 8 hours\n"
            "- Starter RTO: 24 hours\n\n"
            "Backup: 7-day point-in-time restore plus 90-day warm archive plus "
            "7+ year cold archive.\n\n"
            "Maintenance Window: Tuesdays 02:00-04:00 UTC. Zero-downtime rolling "
            "deployments with 60-second connection draining."
        ),
        "tags": ["support", "sla", "uptime", "latency", "recovery", "performance"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 9. COMPETITIVE ADVANTAGES
    # -----------------------------------------------------------------------
    {
        "entry_type": "product",
        "title": "Agent Red Competitive Pricing Advantage",
        "content": (
            "Agent Red is 4 to 21 times cheaper than comparable AI customer service "
            "platforms. Verified competitor pricing as of February 2026:\n\n"
            "- vs Tidio: Agent Red Starter ($149/month) includes 1,000 conversations. "
            "Tidio's comparable tier with AI features costs significantly more per "
            "conversation.\n"
            "- vs Gorgias: Gorgias charges per ticket with AI automation as an add-on. "
            "Agent Red's all-inclusive pricing is dramatically lower at scale.\n"
            "- vs Zendesk: Zendesk's AI-powered tiers start at significantly higher "
            "price points with per-agent pricing.\n"
            "- vs Intercom: Intercom's Fin AI charges per resolution on top of platform "
            "fees. Agent Red's flat-rate included conversations eliminate surprise bills.\n"
            "- vs Re:amaze: Agent Red offers more included conversations at lower "
            "per-conversation rates.\n\n"
            "Agent Red's transparent pricing model (platform fee plus metered usage) "
            "means you always know what you will pay. No per-agent fees, no hidden "
            "charges, no surprise bills."
        ),
        "tags": ["competitive", "pricing", "advantage", "comparison", "value"],
        "is_active": True,
    },
    {
        "entry_type": "product",
        "title": "Why Choose Agent Red Over Competitors",
        "content": (
            "Agent Red Customer Experience stands apart from competitors in several "
            "key areas:\n\n"
            "1. Persistent Customer Memory: No competitor has confirmed implementing "
            "per-customer vector RAG over historical transcripts. Agent Red's 4-layer "
            "memory stack creates genuinely personalized experiences that improve with "
            "every conversation.\n\n"
            "2. Transparent Pricing: Platform fee plus metered AI usage with full "
            "billing transparency. Per-conversation audit trails, CSV exports, and "
            "proactive usage alerts. No hidden per-agent fees.\n\n"
            "3. Fail-Closed Safety: The Critic/Supervisor agent validates every response. "
            "If validation fails for any reason, the response is blocked. Competitors "
            "typically use fail-open designs.\n\n"
            "4. Response Speed: P50 latency target of less than 1,500 milliseconds, "
            "compared to Intercom's published P50 of 7,000 milliseconds. "
            "Approximately 4.7 times faster.\n\n"
            "5. Lightweight Widget: Approximately 15-20 KB gzipped, compared to "
            "Tidio at 40-60 KB and Intercom at 80-100 KB. Faster page loads for "
            "your customers.\n\n"
            "6. Cost: 4-21x cheaper across all comparable tiers and competitors."
        ),
        "tags": ["competitive", "advantage", "differentiator", "comparison"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # 10. ADD-ONS
    # -----------------------------------------------------------------------
    {
        "entry_type": "product",
        "title": "Available Add-On Modules",
        "content": (
            "Agent Red offers the following add-on modules to extend your plan:\n\n"
            "Multi-Language Pack - $99/month (available on all tiers):\n"
            "Enable support in additional languages beyond your primary language.\n\n"
            "Advanced Analytics - $149/month (Professional and Enterprise only):\n"
            "Deeper analytics insights, custom reports, and trend analysis beyond "
            "the standard analytics dashboard.\n\n"
            "Mailchimp Integration - $49/month (Professional and Enterprise only):\n"
            "Sync customer data with Mailchimp for targeted email campaigns based "
            "on conversation insights.\n\n"
            "Google Analytics Integration - $49/month (Professional and Enterprise only):\n"
            "Export conversation events and metrics to your GA4 property for "
            "cross-channel analytics.\n\n"
            "White-Label Package - $399/month (Enterprise only):\n"
            "Complete branding removal, custom domains, CSS theming engine, "
            "co-branding options, and reseller/agency portal.\n\n"
            "Priority Support Upgrade - $99/month (Starter and Professional only):\n"
            "Faster response times and priority issue handling.\n\n"
            "Custom Integration Development - $299/month (Enterprise only):\n"
            "Custom connector development for proprietary systems (Salesforce, SAP, "
            "ServiceNow, etc.).\n\n"
            "Dedicated Model Training - $299/month (Enterprise only):\n"
            "Per-customer AI fine-tuning on 1,000+ historical interactions (Layer 4 "
            "of Persistent Customer Memory). Monthly training pipeline with quality "
            "gates and A/B validation."
        ),
        "tags": ["addons", "modules", "pricing", "white-label", "analytics", "integrations"],
        "is_active": True,
    },

    # -----------------------------------------------------------------------
    # ADDITIONAL TOPICS
    # -----------------------------------------------------------------------
    {
        "entry_type": "faq",
        "title": "Tier Feature Comparison",
        "content": (
            "Feature availability by tier:\n\n"
            "Starter ($149/month):\n"
            "- 1,000 included conversations\n"
            "- 6 AI agents (full pipeline)\n"
            "- Persistent Customer Memory Layers 1-2\n"
            "- 90-day conversation history\n"
            "- 10 requests/minute rate limit\n"
            "- 3 concurrent conversations\n"
            "- 99.5% uptime SLA\n"
            "- 24-hour RTO\n\n"
            "Professional ($399/month):\n"
            "- 5,000 included conversations\n"
            "- 6 AI agents (full pipeline)\n"
            "- Persistent Customer Memory Layers 1-3 (includes Cross-Session Learning)\n"
            "- 365-day conversation history\n"
            "- 50 requests/minute rate limit\n"
            "- 10 concurrent conversations\n"
            "- 99.9% uptime SLA\n"
            "- 8-hour RTO\n"
            "- Access to Advanced Analytics, Mailchimp, and GA4 add-ons\n\n"
            "Enterprise ($999/month):\n"
            "- 20,000 included conversations\n"
            "- 6 AI agents (full pipeline)\n"
            "- Persistent Customer Memory Layers 1-4 (includes Dedicated Model Training add-on)\n"
            "- Unlimited conversation history\n"
            "- 200 requests/minute rate limit\n"
            "- 30 concurrent conversations\n"
            "- 99.95% uptime SLA\n"
            "- 4-hour RTO\n"
            "- Access to White-Label, Custom Integration, and Dedicated Model Training add-ons"
        ),
        "tags": ["tiers", "comparison", "features", "starter", "professional", "enterprise"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Widget Technical Details",
        "content": (
            "The Agent Red chat widget is a lightweight JavaScript application designed "
            "for minimal impact on your website's performance:\n\n"
            "- Built with Preact (approximately 4.5 KB gzipped core)\n"
            "- Total bundle size: approximately 15-20 KB gzipped (single IIFE file)\n"
            "- Shadow DOM (closed) for the launcher button, preventing style leakage\n"
            "- iframe for the conversation panel, providing full DOM isolation\n"
            "- Three communication channels: HTTP POST for messages, SSE for AI "
            "response streaming, WebSocket for typing indicators and presence\n"
            "- Auto-reconnect with exponential backoff on connection loss\n"
            "- 15-second SSE heartbeat keepalive to prevent gateway timeouts\n"
            "- Event buffering with Last-Event-ID for missed event replay\n"
            "- Mobile-responsive design with optional mobile toggle\n"
            "- Delivered via Shopify Theme App Extension (Shopify) or JavaScript "
            "snippet (non-Shopify)"
        ),
        "tags": ["widget", "technical", "performance", "bundle", "architecture"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Merchant Configuration and AI Behavior Tuning",
        "content": (
            "Agent Red provides extensive merchant control over AI behavior through "
            "the Configuration page in the admin dashboard:\n\n"
            "Brand and Tone:\n"
            "- Brand name, voice descriptor, formality level, response length preference\n\n"
            "Business Policies:\n"
            "- Return policy summary, shipping information (injected into AI context)\n\n"
            "Escalation Rules:\n"
            "- Confidence threshold (0.0-1.0, default 0.7)\n"
            "- Escalation trigger keywords\n\n"
            "Custom Instructions:\n"
            "- Freeform merchant instructions appended to the Response Generator prompt "
            "(sandboxed with safety rules taking precedence)\n\n"
            "Memory and Privacy:\n"
            "- Toggle Layers 2-4 on/off\n"
            "- GDPR consent management per customer\n\n"
            "Configuration uses a 5-layer inheritance system: platform defaults, tier "
            "defaults, then tenant overrides. Changes are versioned with full history "
            "and diff comparison. A 60-second cache with tenant-scoped invalidation "
            "ensures changes take effect quickly."
        ),
        "tags": ["configuration", "ai", "behavior", "tuning", "policies", "merchant"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "About Remaker Digital",
        "content": (
            "Agent Red Customer Experience is built and operated by Remaker Digital, "
            "a DBA of VanDusen & Palmeter, LLC, a Delaware limited liability company.\n\n"
            "Website: https://remakerdigital.com\n\n"
            "Agent Red is built on a foundation of the AGNTCY open-source multi-agent "
            "AI platform, with commercial-grade multi-tenant infrastructure, advanced "
            "AI features, enterprise integrations, and white-label capabilities added "
            "on top. The open-source foundation provides transparency and trust while "
            "the commercial layer delivers production-ready performance and security."
        ),
        "tags": ["company", "about", "remaker", "legal"],
        "is_active": True,
    },
    {
        "entry_type": "faq",
        "title": "Response Explainability",
        "content": (
            "Agent Red provides full transparency into how each AI response is generated "
            "through the Response Explainability framework. For every response, a "
            "decision trace is recorded that includes:\n\n"
            "- Which customer profile factors influenced the response\n"
            "- Which knowledge base articles were retrieved\n"
            "- Which memory signals from past conversations were used\n"
            "- Which A/B test variant was active (if applicable)\n"
            "- Timing for each pipeline stage (Intent Classification, Knowledge "
            "Retrieval, Response Generation, Critic validation)\n"
            "- The Critic agent's assessment (approved, rejected, modified)\n\n"
            "This information is available in the admin dashboard's Conversation Inbox "
            "for each conversation, helping you understand and improve your AI "
            "assistant's behavior."
        ),
        "tags": ["features", "explainability", "transparency", "trace", "debug"],
        "is_active": True,
    },
]

# ---------------------------------------------------------------------------
# Article count and summary statistics
# ---------------------------------------------------------------------------

TOTAL_ARTICLES = len(SEED_ARTICLES)


def print_summary() -> None:
    """Print a summary of the seed articles."""
    print(f"\nAgent Red Knowledge Base Seed Data")
    print(f"{'=' * 50}")
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

    # Article listing
    print("Articles:")
    print(f"  {'#':<4} {'Type':<10} {'Title'}")
    print(f"  {'='*4} {'='*10} {'='*50}")
    for i, article in enumerate(SEED_ARTICLES, 1):
        print(f"  {i:<4} {article['entry_type']:<10} {article['title']}")

    print()
    print(f"Total content size: {sum(len(a['content']) for a in SEED_ARTICLES):,} characters")
    print()


# ---------------------------------------------------------------------------
# Cosmos DB loader
# ---------------------------------------------------------------------------


async def load_to_cosmos(tenant_id: str, dry_run: bool = False) -> None:
    """Load seed articles into Cosmos DB via KnowledgeBaseRepository.

    Args:
        tenant_id: The tenant ID to associate articles with.
        dry_run: If True, build documents but do not persist.
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


async def main() -> None:
    """Entry point for loading seed data."""
    parser = argparse.ArgumentParser(
        description="Agent Red Knowledge Base Seed Data",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load articles into Cosmos DB (requires Azure credentials)",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default="remaker-digital-demo",
        help="Tenant ID for the demo storefront (default: remaker-digital-demo)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build documents but do not persist to database",
    )
    args = parser.parse_args()

    print_summary()

    if args.load or args.dry_run:
        print(f"Loading {TOTAL_ARTICLES} articles for tenant: {args.tenant_id}")
        if args.dry_run:
            print("(Dry run mode - no database writes)")
        print()
        await load_to_cosmos(tenant_id=args.tenant_id, dry_run=args.dry_run)
    else:
        print("To load into Cosmos DB, run with --load (or --dry-run to preview)")
        print("  python scripts/seed_knowledge_base.py --load --tenant-id <TENANT_ID>")
        print("  python scripts/seed_knowledge_base.py --dry-run")


if __name__ == "__main__":
    asyncio.run(main())
