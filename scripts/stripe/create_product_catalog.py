#!/usr/bin/env python3
"""
Create the Agent Red product catalog in Stripe (test or live mode).

Idempotent: safe to re-run. Looks up existing products by metadata key
`agent_red_id` before creating. Outputs a JSON mapping file to
config/stripe_product_ids.json for use by downstream integration code.

Usage:
    # Ensure STRIPE_SECRET_KEY is set (test key: sk_test_...)
    export STRIPE_SECRET_KEY=sk_test_...
    python scripts/stripe/create_product_catalog.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import stripe
except ImportError:
    print("ERROR: stripe package not installed. Run: pip install stripe")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    print("ERROR: STRIPE_SECRET_KEY environment variable is not set.")
    print("  For test mode: export STRIPE_SECRET_KEY=sk_test_...")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "config" / "stripe_product_ids.json"

# Metadata key used to make lookups idempotent
META_KEY = "agent_red_id"

# ---------------------------------------------------------------------------
# Product catalog definition
# ---------------------------------------------------------------------------

# Subscription tiers: monthly + annual prices
SUBSCRIPTION_TIERS = [
    {
        "agent_red_id": "tier_starter",
        "name": "Agent Red Starter",
        "description": (
            "AI customer engagement for small Shopify stores. "
            "Includes 1,000 conversations/month."
        ),
        "monthly_price_cents": 14900,  # $149/mo
        "annual_price_cents": 149000,  # $1,490/yr ($124/mo, ~17% off)
        "overage_decimal": "4",  # $0.04 per conversation
        "included_conversations": 1000,
    },
    {
        "agent_red_id": "tier_professional",
        "name": "Agent Red Professional",
        "description": (
            "Advanced AI engagement with cross-session learning. "
            "Includes 5,000 conversations/month."
        ),
        "monthly_price_cents": 39900,  # $399/mo
        "annual_price_cents": 399000,  # $3,990/yr ($332/mo, ~17% off)
        "overage_decimal": "2.5",  # $0.025 per conversation
        "included_conversations": 5000,
    },
    {
        "agent_red_id": "tier_enterprise",
        "name": "Agent Red Enterprise",
        "description": (
            "Full-featured AI engagement with white-label support. "
            "Includes 20,000 conversations/month."
        ),
        "monthly_price_cents": 99900,  # $999/mo
        "annual_price_cents": 999000,  # $9,990/yr ($832/mo, ~17% off)
        "overage_decimal": "1.5",  # $0.015 per conversation
        "included_conversations": 20000,
    },
]

# Conversation packs: one-time purchases, 90-day validity
CONVERSATION_PACKS = [
    {
        "agent_red_id": "pack_1k",
        "name": "Conversation Pack — 1,000",
        "description": "1,000 additional conversations. Valid for 90 days.",
        "price_cents": 2900,  # $29
        "conversations": 1000,
    },
    {
        "agent_red_id": "pack_5k",
        "name": "Conversation Pack — 5,000",
        "description": "5,000 additional conversations. Valid for 90 days.",
        "price_cents": 9900,  # $99
        "conversations": 5000,
    },
    {
        "agent_red_id": "pack_20k",
        "name": "Conversation Pack — 20,000",
        "description": "20,000 additional conversations. Valid for 90 days.",
        "price_cents": 24900,  # $249
        "conversations": 20000,
    },
]

# Add-on modules: recurring monthly
ADDONS = [
    {
        "agent_red_id": "addon_multi_language",
        "name": "Multi-Language Pack",
        "description": "AI responses in multiple languages. Available on all tiers.",
        "price_cents": 9900,  # $99
        "available_on": ["starter", "professional", "enterprise"],
    },
    {
        "agent_red_id": "addon_advanced_analytics",
        "name": "Advanced Analytics",
        "description": "Deep performance insights and custom reports.",
        "price_cents": 14900,  # $149
        "available_on": ["professional", "enterprise"],
    },
    {
        "agent_red_id": "addon_mailchimp",
        "name": "Mailchimp Integration",
        "description": "Sync customer data and trigger email campaigns.",
        "price_cents": 4900,  # $49
        "available_on": ["professional", "enterprise"],
    },
    {
        "agent_red_id": "addon_google_analytics",
        "name": "Google Analytics Integration",
        "description": "Export engagement metrics to GA4.",
        "price_cents": 4900,  # $49
        "available_on": ["professional", "enterprise"],
    },
    {
        "agent_red_id": "addon_white_label",
        "name": "White-Label Package",
        "description": "Complete branding removal with custom domains and CSS theming.",
        "price_cents": 39900,  # $399
        "available_on": ["enterprise"],
    },
    {
        "agent_red_id": "addon_priority_support",
        "name": "Priority Support Upgrade",
        "description": "4-hour response SLA with dedicated support channel.",
        "price_cents": 9900,  # $99
        "available_on": ["starter", "professional"],
    },
    {
        "agent_red_id": "addon_custom_integration",
        "name": "Custom Integration Development",
        "description": "Bespoke integrations built by the Agent Red team.",
        "price_cents": 29900,  # $299
        "available_on": ["enterprise"],
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_existing_product(agent_red_id: str) -> stripe.Product | None:
    """Look up a product by our custom metadata key."""
    products = stripe.Product.search(
        query=f"metadata['{META_KEY}']:'{agent_red_id}'",
        limit=1,
    )
    if products.data:
        return products.data[0]
    return None


def find_existing_price(product_id: str, lookup_key: str) -> stripe.Price | None:
    """Find an active price on a product by lookup_key."""
    prices = stripe.Price.list(
        product=product_id,
        lookup_keys=[lookup_key],
        active=True,
        limit=1,
    )
    if prices.data:
        return prices.data[0]
    return None


def ensure_product(
    agent_red_id: str,
    name: str,
    description: str,
    extra_metadata: dict | None = None,
) -> stripe.Product:
    """Create a product if it doesn't already exist."""
    existing = find_existing_product(agent_red_id)
    if existing:
        print(f"  ✓ Product exists: {name} ({existing.id})")
        return existing

    metadata = {META_KEY: agent_red_id}
    if extra_metadata:
        metadata.update(extra_metadata)

    product = stripe.Product.create(
        name=name,
        description=description,
        metadata=metadata,
    )
    print(f"  + Created product: {name} ({product.id})")
    return product


def ensure_price(
    product_id: str,
    lookup_key: str,
    unit_amount: int,
    currency: str = "usd",
    recurring: dict | None = None,
) -> stripe.Price:
    """Create a price if it doesn't already exist for this lookup_key."""
    existing = find_existing_price(product_id, lookup_key)
    if existing:
        print(f"  ✓ Price exists: {lookup_key} ({existing.id})")
        return existing

    params: dict = {
        "product": product_id,
        "currency": currency,
        "lookup_key": lookup_key,
        "transfer_lookup_key": True,
        "metadata": {META_KEY: lookup_key},
    }

    if recurring:
        params["recurring"] = recurring
        params["unit_amount"] = unit_amount
    else:
        params["unit_amount"] = unit_amount

    price = stripe.Price.create(**params)
    print(f"  + Created price: {lookup_key} ({price.id})")
    return price


def ensure_billing_meter(client: stripe.StripeClient) -> str:
    """Create or find the conversation usage Billing Meter.

    Stripe API version 2025-03-31.basil+ requires metered prices to be
    backed by a Billing Meter object. We create one shared meter for
    conversation overage; all tier-specific overage prices reference it.

    Returns the meter ID.
    """
    # Check for an existing meter by event_name
    meters = client.v1.billing.meters.list({"status": "active"})
    for meter in meters.data:
        if meter.event_name == "conversation_overage":
            print(f"  ✓ Billing Meter exists: conversation_overage ({meter.id})")
            return meter.id

    meter = client.v1.billing.meters.create({
        "display_name": "Conversation Overage",
        "event_name": "conversation_overage",
        "default_aggregation": {"formula": "sum"},
        "customer_mapping": {
            "type": "by_id",
            "event_payload_key": "stripe_customer_id",
        },
        "value_settings": {
            "event_payload_key": "value",
        },
    })
    print(f"  + Created Billing Meter: conversation_overage ({meter.id})")
    return meter.id


def ensure_metered_price(
    product_id: str,
    lookup_key: str,
    unit_amount_decimal: str,
    meter_id: str,
) -> stripe.Price:
    """Create a metered (usage-based) price for conversation overage.

    Uses unit_amount_decimal (string) to support fractional cents
    (e.g. "2.5" for $0.025 per conversation). Linked to a Billing Meter
    as required by Stripe API version 2025-03-31.basil+.
    """
    existing = find_existing_price(product_id, lookup_key)
    if existing:
        print(f"  ✓ Metered price exists: {lookup_key} ({existing.id})")
        return existing

    price = stripe.Price.create(
        product=product_id,
        currency="usd",
        unit_amount_decimal=unit_amount_decimal,
        recurring={
            "interval": "month",
            "usage_type": "metered",
            "meter": meter_id,
        },
        lookup_key=lookup_key,
        transfer_lookup_key=True,
        metadata={META_KEY: lookup_key},
    )
    print(f"  + Created metered price: {lookup_key} ({price.id})")
    return price


# ---------------------------------------------------------------------------
# Catalog creation
# ---------------------------------------------------------------------------


def create_subscription_tiers(catalog: dict, meter_id: str) -> None:
    """Create the 3 subscription tier products with monthly, annual, and overage prices."""
    print("\n── Subscription Tiers ──")
    catalog["tiers"] = {}

    for tier in SUBSCRIPTION_TIERS:
        aid = tier["agent_red_id"]
        short_name = aid.replace("tier_", "")

        product = ensure_product(
            agent_red_id=aid,
            name=tier["name"],
            description=tier["description"],
            extra_metadata={"included_conversations": str(tier["included_conversations"])},
        )

        monthly = ensure_price(
            product_id=product.id,
            lookup_key=f"{aid}_monthly",
            unit_amount=tier["monthly_price_cents"],
            recurring={"interval": "month"},
        )

        annual = ensure_price(
            product_id=product.id,
            lookup_key=f"{aid}_annual",
            unit_amount=tier["annual_price_cents"],
            recurring={"interval": "year"},
        )

        overage = ensure_metered_price(
            product_id=product.id,
            lookup_key=f"{aid}_overage",
            unit_amount_decimal=tier["overage_decimal"],
            meter_id=meter_id,
        )

        catalog["tiers"][short_name] = {
            "product_id": product.id,
            "monthly_price_id": monthly.id,
            "annual_price_id": annual.id,
            "overage_price_id": overage.id,
            "included_conversations": tier["included_conversations"],
        }


def create_conversation_packs(catalog: dict) -> None:
    """Create conversation pack products with one-time prices."""
    print("\n── Conversation Packs ──")
    catalog["packs"] = {}

    for pack in CONVERSATION_PACKS:
        aid = pack["agent_red_id"]

        product = ensure_product(
            agent_red_id=aid,
            name=pack["name"],
            description=pack["description"],
            extra_metadata={"conversations": str(pack["conversations"])},
        )

        price = ensure_price(
            product_id=product.id,
            lookup_key=aid,
            unit_amount=pack["price_cents"],
        )

        catalog["packs"][aid] = {
            "product_id": product.id,
            "price_id": price.id,
            "conversations": pack["conversations"],
        }


def create_addons(catalog: dict) -> None:
    """Create add-on module products with recurring monthly prices."""
    print("\n── Add-On Modules ──")
    catalog["addons"] = {}

    for addon in ADDONS:
        aid = addon["agent_red_id"]

        product = ensure_product(
            agent_red_id=aid,
            name=addon["name"],
            description=addon["description"],
            extra_metadata={"available_on": ",".join(addon["available_on"])},
        )

        price = ensure_price(
            product_id=product.id,
            lookup_key=aid,
            unit_amount=addon["price_cents"],
            recurring={"interval": "month"},
        )

        catalog["addons"][aid] = {
            "product_id": product.id,
            "price_id": price.id,
            "available_on": addon["available_on"],
        }


def create_coupon(catalog: dict) -> None:
    """Create a promotional coupon for annual discount."""
    print("\n── Coupons ──")
    coupon_id = "annual_17pct_off"

    try:
        existing = stripe.Coupon.retrieve(coupon_id)
        print(f"  ✓ Coupon exists: {coupon_id} ({existing.id})")
        catalog["coupons"] = {coupon_id: {"coupon_id": existing.id}}
        return
    except stripe.InvalidRequestError:
        pass

    coupon = stripe.Coupon.create(
        id=coupon_id,
        percent_off=17,
        duration="forever",
        name="Annual Plan — 17% Off",
        metadata={META_KEY: coupon_id},
    )
    print(f"  + Created coupon: {coupon_id} ({coupon.id})")
    catalog["coupons"] = {coupon_id: {"coupon_id": coupon.id}}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    mode = "LIVE" if stripe.api_key.startswith("sk_live") else "TEST"
    print(f"Agent Red — Stripe Product Catalog Setup ({mode} mode)")
    print("=" * 55)

    # StripeClient is required for Billing Meters API
    client = stripe.StripeClient(stripe.api_key)

    catalog: dict = {"mode": mode.lower()}

    # Create the shared Billing Meter for conversation overage
    print("\n── Billing Meter ──")
    meter_id = ensure_billing_meter(client)
    catalog["meter"] = {"conversation_overage": {"meter_id": meter_id}}

    create_subscription_tiers(catalog, meter_id=meter_id)
    create_conversation_packs(catalog)
    create_addons(catalog)
    create_coupon(catalog)

    # Write output mapping
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    print(f"\n✓ Catalog written to {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  1 meter, {len(catalog['tiers'])} tiers, "
          f"{len(catalog['packs'])} packs, "
          f"{len(catalog['addons'])} add-ons, "
          f"{len(catalog['coupons'])} coupons")


if __name__ == "__main__":
    main()
