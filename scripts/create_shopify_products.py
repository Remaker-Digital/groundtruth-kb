"""
Create Agent Red product catalog on the Shopify storefront.

Creates products representing Agent Red subscription tiers, conversation
packs, and add-on modules. These products serve as the browsable catalog
on the agent-red.myshopify.com storefront — the AI assistant uses the
knowledge base (not these products) to answer pricing questions.

Note: Actual billing flows through Stripe or Shopify Billing API.
These Shopify products are for storefront display and SEO only.
Prices are set to $0 with "Contact for pricing" or the product
description contains the real price — we do NOT process checkout
through Shopify's native cart for these items.

Usage:
    # Preview products (no API calls):
    python scripts/create_shopify_products.py

    # Create products on Shopify:
    python scripts/create_shopify_products.py --create

Requires in .env.local:
    SHOPIFY_STORE_URL=agent-red.myshopify.com
    SHOPIFY_ACCESS_TOKEN=shpat_...

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Product definitions
# ---------------------------------------------------------------------------

PRODUCTS = [
    # --- Subscription Tiers ---
    {
        "title": "Agent Red Starter",
        "body_html": (
            "<h2>AI Customer Service for Growing Stores</h2>"
            "<p><strong>$149/month</strong> or <strong>$124/month</strong> billed annually ($1,490/year &mdash; save $298)</p>"
            "<p>The full six-agent AI platform with everything you need to automate customer service. "
            "No artificial limits on AI capability &mdash; every tier gets the same AI engine.</p>"
            "<h3>Included</h3>"
            "<ul>"
            "<li><strong>1,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents (classify, research, respond, validate, escalate, analyze)</li>"
            "<li>Shopify integration</li>"
            "<li>English language support</li>"
            "<li>Knowledge base (up to 50 articles + Shopify product sync)</li>"
            "<li>Basic brand voice configuration</li>"
            "<li>Real-time analytics dashboard</li>"
            "<li>TLS 1.3, AES-256 encryption, PII tokenization, GDPR/CCPA compliance</li>"
            "<li>Email support (48hr response)</li>"
            "<li>99.5% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.04 per conversation beyond 1,000/month</p>"
            "<p><em>14 days free &middot; No credit card required</em></p>"
        ),
        "product_type": "Subscription",
        "vendor": "Remaker Digital",
        "tags": ["tier", "starter", "subscription", "ai-customer-service"],
    },
    {
        "title": "Agent Red Professional",
        "body_html": (
            "<h2>Advanced AI Customer Service for Scaling Businesses</h2>"
            "<p><strong>$399/month</strong> or <strong>$332/month</strong> billed annually ($3,990/year &mdash; save $798)</p>"
            "<p>Higher volume, more integrations, and advanced customization including "
            "Persistent Customer Memory Layers 1-3 for growing e-commerce businesses.</p>"
            "<h3>Included</h3>"
            "<ul>"
            "<li><strong>5,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents (same AI engine as every tier)</li>"
            "<li>Shopify + Zendesk integrations</li>"
            "<li>English + 1 additional language</li>"
            "<li>Knowledge base (up to 500 articles + Shopify product sync)</li>"
            "<li>Full brand voice configuration</li>"
            "<li>Custom escalation rules</li>"
            "<li><strong>Persistent Customer Memory (Layers 1-3)</strong> &mdash; "
            "customer profiles, conversation history search, cross-session learning</li>"
            "<li>Full analytics with data export (CSV)</li>"
            "<li>Read-only API access + Audit logging</li>"
            "<li>Chat + email support (24hr response)</li>"
            "<li>Onboarding session (1 call)</li>"
            "<li>99.9% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.025 per conversation beyond 5,000/month</p>"
            "<p><strong>MOST POPULAR</strong></p>"
        ),
        "product_type": "Subscription",
        "vendor": "Remaker Digital",
        "tags": ["tier", "professional", "subscription", "ai-customer-service", "most-popular"],
    },
    {
        "title": "Agent Red Enterprise",
        "body_html": (
            "<h2>Full-Platform AI Customer Service</h2>"
            "<p><strong>$999/month</strong> or <strong>$832/month</strong> billed annually ($9,990/year &mdash; save $1,998)</p>"
            "<p>The complete Agent Red platform with all integrations, all memory layers, "
            "unlimited history, white-label options, and dedicated support.</p>"
            "<h3>Included</h3>"
            "<ul>"
            "<li><strong>20,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents (same AI engine as every tier)</li>"
            "<li>Shopify + Zendesk + Mailchimp + Google Analytics integrations</li>"
            "<li>English + 3 additional languages</li>"
            "<li>Knowledge base (unlimited articles + Shopify product sync)</li>"
            "<li>Full brand voice + custom AI behavior tuning</li>"
            "<li>Custom escalation rules + priority routing</li>"
            "<li><strong>Persistent Customer Memory (All 4 Layers)</strong> &mdash; "
            "profiles, history search, cross-session learning, dedicated model training</li>"
            "<li>Advanced analytics, custom reports, real-time API</li>"
            "<li>Full API access (read + write) + Audit logging + Data export</li>"
            "<li>Dedicated support (4hr response) + Slack channel</li>"
            "<li>Onboarding program (3 sessions)</li>"
            "<li>99.95% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.015 per conversation beyond 20,000/month</p>"
        ),
        "product_type": "Subscription",
        "vendor": "Remaker Digital",
        "tags": ["tier", "enterprise", "subscription", "ai-customer-service"],
    },
    # --- Conversation Packs ---
    {
        "title": "Conversation Pack - 1,000",
        "body_html": (
            "<h2>1,000 Additional AI Conversations</h2>"
            "<p><strong>$29</strong> (one-time purchase)</p>"
            "<p>Pre-purchase 1,000 additional AI conversations at $0.029 each &mdash; "
            "27% cheaper than Starter overage rates. Valid for 90 days. "
            "Pack balance is consumed before overage billing (FIFO).</p>"
            "<p>Available on all tiers.</p>"
        ),
        "product_type": "Conversation Pack",
        "vendor": "Remaker Digital",
        "tags": ["pack", "conversations", "1000"],
    },
    {
        "title": "Conversation Pack - 5,000",
        "body_html": (
            "<h2>5,000 Additional AI Conversations</h2>"
            "<p><strong>$99</strong> (one-time purchase)</p>"
            "<p>Pre-purchase 5,000 additional AI conversations at $0.020 each &mdash; "
            "50% cheaper than Starter overage rates. Valid for 90 days. "
            "Pack balance is consumed before overage billing (FIFO).</p>"
            "<p>Available on all tiers. Best value for seasonal traffic spikes.</p>"
        ),
        "product_type": "Conversation Pack",
        "vendor": "Remaker Digital",
        "tags": ["pack", "conversations", "5000"],
    },
    {
        "title": "Conversation Pack - 20,000",
        "body_html": (
            "<h2>20,000 Additional AI Conversations</h2>"
            "<p><strong>$249</strong> (one-time purchase)</p>"
            "<p>Pre-purchase 20,000 additional AI conversations at $0.012 each &mdash; "
            "70% cheaper than Starter overage rates. Valid for 90 days. "
            "Pack balance is consumed before overage billing (FIFO).</p>"
            "<p>Available on all tiers. Ideal for high-volume stores and peak seasons.</p>"
        ),
        "product_type": "Conversation Pack",
        "vendor": "Remaker Digital",
        "tags": ["pack", "conversations", "20000"],
    },
    # --- Add-On Modules ---
    {
        "title": "Multi-Language Pack",
        "body_html": (
            "<h2>Expand Your AI to New Markets</h2>"
            "<p><strong>$99/month</strong> add-on</p>"
            "<p>Add support for additional languages beyond your tier's included allowance. "
            "Agent Red's AI responds naturally in each language &mdash; not machine translation, "
            "but native-quality responses powered by GPT-4o.</p>"
            "<p>Available on all tiers.</p>"
        ),
        "product_type": "Add-On",
        "vendor": "Remaker Digital",
        "tags": ["addon", "multi-language", "internationalization"],
    },
    {
        "title": "Advanced Analytics",
        "body_html": (
            "<h2>Deeper Insights Into Customer Interactions</h2>"
            "<p><strong>$149/month</strong> add-on</p>"
            "<p>Custom reports, trend analysis, intent gap detection, and exportable data. "
            "Understand what your customers ask, where the AI excels, and where "
            "human attention adds the most value.</p>"
            "<p>Available on Professional and Enterprise tiers.</p>"
        ),
        "product_type": "Add-On",
        "vendor": "Remaker Digital",
        "tags": ["addon", "analytics", "reporting"],
    },
    {
        "title": "White-Label Package",
        "body_html": (
            "<h2>Make It Entirely Yours</h2>"
            "<p><strong>$399/month</strong> add-on</p>"
            "<p>Complete removal of Agent Red branding. Custom domain support, "
            "CSS theming engine, and co-branding options. Your customers see "
            "only your brand &mdash; the AI assistant appears as a native part "
            "of your store.</p>"
            "<p>Available on Enterprise tier only.</p>"
        ),
        "product_type": "Add-On",
        "vendor": "Remaker Digital",
        "tags": ["addon", "white-label", "branding", "enterprise"],
    },
    {
        "title": "Dedicated Model Training",
        "body_html": (
            "<h2>AI That Learns Your Business</h2>"
            "<p><strong>$299/month</strong> add-on</p>"
            "<p>Persistent Customer Memory Layer 4 &mdash; per-customer AI fine-tuning. "
            "After 1,000+ conversations, Agent Red trains a dedicated model on your "
            "specific products, policies, and communication style. Monthly retraining "
            "with quality gates and A/B validation ensures the model improves safely.</p>"
            "<p>Available on Enterprise tier only. Requires 1,000+ historical conversations.</p>"
        ),
        "product_type": "Add-On",
        "vendor": "Remaker Digital",
        "tags": ["addon", "fine-tuning", "ai-training", "enterprise", "persistent-memory"],
    },
]


# ---------------------------------------------------------------------------
# GraphQL mutation
# ---------------------------------------------------------------------------

CREATE_PRODUCT_MUTATION = """
mutation productCreate($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      handle
      status
    }
    userErrors {
      field
      message
    }
  }
}
"""


async def create_products(dry_run: bool = True) -> None:
    """Create all products on the Shopify storefront."""

    print()
    print("=" * 65)
    print("  AGENT RED SHOPIFY PRODUCT CATALOG")
    print("=" * 65)
    print(f"  Products to create: {len(PRODUCTS)}")
    print()

    for i, product in enumerate(PRODUCTS, 1):
        tags_str = ", ".join(product["tags"])
        print(f"  {i:2d}. {product['title']}")
        print(f"      Type: {product['product_type']}  |  Tags: {tags_str}")

    print()

    if dry_run:
        print("[DRY RUN] No API calls made. Run with --create to create products.")
        print()
        return

    store_url = os.environ.get("SHOPIFY_STORE_URL", "")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

    if not store_url or not access_token:
        print("[ERROR] SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env.local")
        sys.exit(1)

    from src.integrations.shopify_client import ShopifyGraphQLClient

    async with ShopifyGraphQLClient(store_url, access_token) as client:
        created = 0
        errors = 0

        for product in PRODUCTS:
            variables = {
                "input": {
                    "title": product["title"],
                    "descriptionHtml": product["body_html"],
                    "productType": product["product_type"],
                    "vendor": product["vendor"],
                    "tags": product["tags"],
                    "status": "ACTIVE",
                }
            }

            try:
                result = await client.execute(CREATE_PRODUCT_MUTATION, variables)

                if "productCreate" in result:
                    user_errors = result["productCreate"].get("userErrors", [])
                    if user_errors:
                        print(f"  [WARN] {product['title']}: {user_errors}")
                        errors += 1
                    else:
                        p = result["productCreate"]["product"]
                        print(f"  [OK] {p['title']} (handle: {p['handle']})")
                        created += 1
                else:
                    print(f"  [ERROR] {product['title']}: unexpected response: {result}")
                    errors += 1

            except Exception as e:
                print(f"  [ERROR] {product['title']}: {e}")
                errors += 1

    print()
    print(f"  Created: {created}  |  Errors: {errors}")
    print("=" * 65)
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Agent Red product catalog on Shopify storefront",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create products via Shopify API (omit for dry run preview)",
    )
    args = parser.parse_args()

    await create_products(dry_run=not args.create)


if __name__ == "__main__":
    asyncio.run(main())
