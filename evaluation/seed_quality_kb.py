"""Seed KB articles required by conversation quality golden scenarios.

This script creates the knowledge base articles that the 25 golden
evaluation scenarios (response_quality.json) depend on.  It targets
the tenant identified by WIDGET_KEY — currently remaker-digital-001.

The articles are the *merchant's store content* (shipping policies,
product info, order tracking, etc.) that the AI assistant needs in
order to answer customer questions faithfully.

Preconditions:
    - Production API gateway healthy (/health 200)
    - Valid superadmin API key for the target tenant

Usage:
    # Dry run — list articles that would be created
    python evaluation/seed_quality_kb.py

    # Execute — create articles via admin API
    python evaluation/seed_quality_kb.py --execute

    # Wipe existing KB first, then seed (clean slate)
    python evaluation/seed_quality_kb.py --execute --clean

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROD_URL = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
API_KEY = "ar_user_rema_qcHQpv0bhGwXpEou14WH3fnE_RZMvI_N"

# ---------------------------------------------------------------------------
# KB Articles — derived from response_quality.json knowledge_context fields
# ---------------------------------------------------------------------------

QUALITY_KB_ARTICLES: list[dict] = [
    # --- Shipping ---
    {
        "entryType": "policy",
        "title": "Shipping Policy",
        "content": (
            "Shipping Timeframes:\n"
            "- US domestic: 3-5 business days\n"
            "- Canada: 7-10 business days\n"
            "- International: 10-21 business days\n\n"
            "Shipping Options:\n"
            "- Standard: 5-7 business days, free on all orders\n"
            "- Express: 2-3 business days, $12.99\n"
            "- Overnight: next business day, $29.99\n\n"
            "Express Shipping Guarantee: Express shipping is guaranteed "
            "within 2-3 business days. If your express order is not "
            "delivered within this window, you are eligible for a full "
            "shipping refund."
        ),
        "category": "Shipping",
        "status": "published",
        "tags": ["shipping", "delivery", "express", "overnight", "canada", "international"],
    },
    # --- Returns & Refunds ---
    {
        "entryType": "policy",
        "title": "Return and Refund Policy",
        "content": (
            "We accept returns within 30 days of purchase. Items must be "
            "in original condition.\n\n"
            "Damaged Items: If your item arrived damaged, you are eligible "
            "for a full refund within 14 days. Please contact support with "
            "photos of the damage.\n\n"
            "Important: We only process returns for items purchased "
            "directly from our store. Items purchased from other retailers "
            "cannot be returned to us.\n\n"
            "Refunds are processed within 5-7 business days after we "
            "receive the returned item."
        ),
        "category": "Returns",
        "status": "published",
        "tags": ["returns", "refunds", "policy", "damaged", "30-day"],
    },
    # --- Payment Methods ---
    {
        "entryType": "faq",
        "title": "Payment Methods",
        "content": (
            "We accept Visa, Mastercard, American Express, PayPal, "
            "and Apple Pay. All payment processing is handled securely "
            "through our encrypted payment gateway."
        ),
        "category": "General",
        "status": "published",
        "tags": ["payment", "visa", "mastercard", "paypal", "apple pay"],
    },
    # --- Order Tracking ---
    {
        "entryType": "faq",
        "title": "Order Tracking",
        "content": (
            "Customers can track their orders at ourstore.com/track. "
            "Simply enter your order number to see the current status "
            "and estimated delivery date. Our support team can also "
            "look up orders by number if you need assistance."
        ),
        "category": "Orders",
        "status": "published",
        "tags": ["order", "tracking", "status", "delivery"],
    },
    # --- Order Modifications ---
    {
        "entryType": "faq",
        "title": "Order Modifications",
        "content": (
            "Shipping address can be changed within 2 hours of placing "
            "the order. After 2 hours, please contact our support team "
            "for assistance — we will do our best to accommodate changes "
            "before the order ships."
        ),
        "category": "Orders",
        "status": "published",
        "tags": ["order", "modification", "address", "change"],
    },
    # --- Complaint Handling (internal guidance) ---
    {
        "entryType": "policy",
        "title": "Complaint Handling Guidelines",
        "content": (
            "When handling customer complaints:\n"
            "1. Acknowledge the customer's frustration\n"
            "2. Apologize sincerely for the inconvenience\n"
            "3. Offer a concrete resolution or next steps\n"
            "4. Escalate repeat complaints to a supervisor\n\n"
            "Repeat complaints (customer mentions multiple issues or "
            "prior unresolved problems) should always be escalated to "
            "ensure proper resolution."
        ),
        "category": "Internal",
        "status": "published",
        "tags": ["complaint", "escalation", "handling", "guidelines"],
    },
    # --- Response Times ---
    {
        "entryType": "faq",
        "title": "Customer Support Response Times",
        "content": (
            "We aim to respond to all customer inquiries within 24-48 "
            "hours. During peak periods (holidays, major sales events), "
            "responses may take up to 72 hours. We appreciate your "
            "patience and will get back to you as soon as possible."
        ),
        "category": "Support",
        "status": "published",
        "tags": ["response", "time", "support", "wait"],
    },
    # --- Privacy ---
    {
        "entryType": "policy",
        "title": "Privacy Policy Summary",
        "content": (
            "We use industry-standard encryption to protect your data. "
            "Your personal information is never sold to third parties. "
            "We are GDPR compliant and follow strict data protection "
            "practices. For full details, see our privacy policy at "
            "ourstore.com/privacy."
        ),
        "category": "Legal",
        "status": "published",
        "tags": ["privacy", "gdpr", "encryption", "data", "security"],
    },
    # --- Products ---
    {
        "entryType": "product",
        "title": "Classic T-Shirt",
        "content": (
            "The Classic T-Shirt is available in sizes S, M, L, and XL. "
            "Made from 100% cotton for comfort and durability. "
            "Price: $29.99."
        ),
        "category": "Products",
        "status": "published",
        "tags": ["product", "t-shirt", "classic", "cotton"],
    },
    {
        "entryType": "product",
        "title": "Organic Face Cream",
        "content": (
            "The Organic Face Cream is made with natural ingredients. "
            "It is vegan-friendly and cruelty-free certified. "
            "Size: 50ml. Price: $45.00."
        ),
        "category": "Products",
        "status": "published",
        "tags": ["product", "face cream", "organic", "vegan", "cruelty-free"],
    },
    {
        "entryType": "product",
        "title": "Garden Collection",
        "content": (
            "Our Garden Collection includes:\n"
            "- Garden Tool Set: Premium 5-piece set, $49.99\n"
            "- Herb Garden Kit: Indoor starter kit, $24.99\n"
            "- Garden Gloves: Leather gardening gloves, $19.99\n\n"
            "Perfect gifts for gardening enthusiasts."
        ),
        "category": "Products",
        "status": "published",
        "tags": ["product", "garden", "tools", "gift"],
    },
    # --- Technology ---
    {
        "entryType": "article",
        "title": "Our Technology",
        "content": (
            "Agent Red uses AI-powered personalization with semantic "
            "search, customer memory, and adaptive learning to provide "
            "tailored product recommendations. Our technology learns "
            "from each interaction to deliver increasingly relevant "
            "suggestions over time."
        ),
        "category": "About",
        "status": "published",
        "tags": ["technology", "AI", "personalization", "recommendations"],
    },
]


def list_existing(api_key: str) -> list[dict]:
    """Fetch all existing KB entries."""
    r = requests.get(
        f"{PROD_URL}/api/admin/knowledge",
        headers={"X-API-Key": api_key},
        timeout=15,
    )
    if r.status_code != 200:
        print(f"  [WARN] Failed to list KB: {r.status_code}")
        return []
    data = r.json()
    if isinstance(data, list):
        return data
    return data.get("articles", data.get("items", data.get("entries", [])))


def delete_entry(api_key: str, entry_id: str) -> bool:
    """Delete a single KB entry."""
    r = requests.delete(
        f"{PROD_URL}/api/admin/knowledge/{entry_id}",
        headers={"X-API-Key": api_key},
        timeout=15,
    )
    return r.status_code in (200, 204)


def create_entry(api_key: str, article: dict) -> tuple[int, dict]:
    """Create a single KB entry via admin API."""
    r = requests.post(
        f"{PROD_URL}/api/admin/knowledge",
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        json=article,
        timeout=15,
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"error": r.text[:200]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed KB for quality tests")
    parser.add_argument("--execute", action="store_true", help="Actually create articles")
    parser.add_argument("--clean", action="store_true", help="Delete existing KB first")
    args = parser.parse_args()

    print("=" * 60)
    print("Conversation Quality KB Seeder")
    print(f"Target: {PROD_URL}")
    print(f"Articles: {len(QUALITY_KB_ARTICLES)}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print("=" * 60)

    if not args.execute:
        print("\nArticles to create:")
        for i, art in enumerate(QUALITY_KB_ARTICLES, 1):
            print(f"  {i:2d}. [{art['entryType']:8s}] {art['title']}")
            print(f"      Category: {art.get('category', '-')}, Tags: {art.get('tags', [])}")
            print(f"      Content: {art['content'][:80]}...")
        print(f"\nRun with --execute to create these {len(QUALITY_KB_ARTICLES)} articles.")
        return

    # Clean existing KB if requested
    if args.clean:
        print("\n--- Cleaning existing KB ---")
        existing = list_existing(API_KEY)
        if existing:
            deleted = 0
            for entry in existing:
                eid = entry.get("id", "")
                title = entry.get("title", "?")
                if delete_entry(API_KEY, eid):
                    print(f"  [DEL] {title} ({eid[:12]}...)")
                    deleted += 1
                else:
                    print(f"  [FAIL] Could not delete {title} ({eid})")
            print(f"  Deleted {deleted}/{len(existing)} entries")
        else:
            print("  No existing entries to delete")
        time.sleep(1)  # Brief pause for consistency

    # Create articles
    print(f"\n--- Creating {len(QUALITY_KB_ARTICLES)} KB articles ---")
    created = 0
    failed = 0

    for art in QUALITY_KB_ARTICLES:
        status, body = create_entry(API_KEY, art)
        if status == 201:
            entry_id = body.get("id", "?")
            print(f"  [OK]   {art['title']} (id={entry_id[:12] if len(entry_id) > 12 else entry_id}...)")
            created += 1
        else:
            print(f"  [FAIL] {art['title']}: {status} — {body}")
            failed += 1
        time.sleep(0.3)  # Avoid rate limiting

    # Verify
    print(f"\n--- Verification ---")
    time.sleep(1)
    existing = list_existing(API_KEY)
    print(f"  KB entries in tenant: {len(existing)}")
    for entry in existing:
        print(f"    [{entry.get('status', '?'):10s}] {entry.get('title', '?')}")

    # Summary
    print(f"\n{'=' * 60}")
    verdict = "PASS" if created == len(QUALITY_KB_ARTICLES) and failed == 0 else "FAIL"
    print(f"Created: {created}/{len(QUALITY_KB_ARTICLES)} | Failed: {failed}")
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
