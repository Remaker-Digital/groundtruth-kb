#!/usr/bin/env python3
"""
One-time migration: add tax_code to existing Agent Red Stripe Products.

Reads product IDs from config/stripe_product_ids.json and updates each
Product with tax_code="txcd_10103001" (SaaS — Business Use). Safe to
re-run — idempotent (Stripe accepts the same value without error).

After running this script, the create_product_catalog.py script will
handle tax_code on new Products automatically.

Usage:
    export STRIPE_SECRET_KEY=sk_test_...
    python scripts/stripe/update_tax_codes.py

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
CATALOG_PATH = PROJECT_ROOT / "config" / "stripe_product_ids.json"

# SaaS — Business Use tax code
TAX_CODE_SAAS_B2B = "txcd_10103001"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    mode = "LIVE" if stripe.api_key.startswith("sk_live") else "TEST"
    print(f"Agent Red — Update Tax Codes on Existing Products ({mode} mode)")
    print("=" * 60)

    if not CATALOG_PATH.exists():
        print(f"ERROR: Catalog file not found: {CATALOG_PATH}")
        print("  Run create_product_catalog.py first.")
        sys.exit(1)

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    # Collect all product IDs from tiers, packs, and addons
    products: list[tuple[str, str]] = []  # (category/name, product_id)

    for tier_name, tier_data in catalog.get("tiers", {}).items():
        products.append((f"tier/{tier_name}", tier_data["product_id"]))

    for pack_name, pack_data in catalog.get("packs", {}).items():
        products.append((f"pack/{pack_name}", pack_data["product_id"]))

    for addon_name, addon_data in catalog.get("addons", {}).items():
        products.append((f"addon/{addon_name}", addon_data["product_id"]))

    print(f"\nFound {len(products)} products to update.\n")

    updated = 0
    skipped = 0
    errors = 0

    for label, product_id in products:
        try:
            product = stripe.Product.retrieve(product_id)

            if product.tax_code == TAX_CODE_SAAS_B2B:
                print(f"  ✓ {label} ({product_id}) — tax_code already set")
                skipped += 1
                continue

            stripe.Product.modify(product_id, tax_code=TAX_CODE_SAAS_B2B)
            old_code = product.tax_code or "none"
            print(f"  ↻ {label} ({product_id}) — tax_code: {old_code} → {TAX_CODE_SAAS_B2B}")
            updated += 1

        except stripe.StripeError as exc:
            print(f"  ✗ {label} ({product_id}) — ERROR: {exc}")
            errors += 1

    print(f"\nDone: {updated} updated, {skipped} already set, {errors} errors.")


if __name__ == "__main__":
    main()
