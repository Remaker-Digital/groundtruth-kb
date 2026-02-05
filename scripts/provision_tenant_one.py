"""
Provision agent-red.myshopify.com as Agent Red tenant #1.

Creates the tenant document in Cosmos DB with Professional tier,
generates API key and publishable widget key, and stores credential
hashes in the tenant record.

Usage:
    # Preview only (no DB writes):
    python scripts/provision_tenant_one.py

    # Provision to Cosmos DB:
    python scripts/provision_tenant_one.py --provision

    # Also seed the knowledge base:
    python scripts/provision_tenant_one.py --provision --seed-kb

Requires Azure credentials in .env.local:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import os
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local
_env_path = PROJECT_ROOT / ".env.local"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tenant #1 configuration
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
SHOP_DOMAIN = "blanco-9939.myshopify.com"
CUSTOMER_EMAIL = "mike@remakerdigital.com"
TIER = "professional"
BILLING_CHANNEL = "shopify"
INTERVAL = "month"


def generate_api_key() -> str:
    """Generate a 48-character hex API key."""
    return "ar_" + secrets.token_hex(24)


def generate_widget_key(tenant_id: str) -> str:
    """Generate a publishable widget key.

    Format: pk_live_{tenant_hash_8}_{random_8}
    """
    tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:8]
    random_part = secrets.token_hex(4)  # 8 hex chars
    return f"pk_live_{tenant_hash}_{random_part}"


def hash_key(key: str) -> str:
    """SHA-256 hash a key for storage."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


async def provision(dry_run: bool = True, seed_kb: bool = False) -> None:
    """Create the tenant document in Cosmos DB."""

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.cosmos_schema import (
        BillingChannel,
        ConsentStatus,
        TenantDocument,
        TenantStatus,
        TenantTier,
    )
    from src.multi_tenant.repository import TenantRepository

    # Generate credentials
    api_key = generate_api_key()
    widget_key = generate_widget_key(TENANT_ID)
    now = datetime.now(timezone.utc).isoformat()

    tenant_doc = TenantDocument(
        id=TENANT_ID,
        tenant_id=TENANT_ID,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel.SHOPIFY,
        tier=TenantTier.PROFESSIONAL,
        interval=INTERVAL,
        addons=[],
        shopify_shop_domain=SHOP_DOMAIN,
        customer_email=CUSTOMER_EMAIL,
        consent_status=ConsentStatus.GRANTED,
        api_key_hash=hash_key(api_key),
        widget_key_hash=hash_key(widget_key),
        rate_limit_rpm=50,
        max_concurrent=10,
        created_at=now,
        updated_at=now,
    )

    print()
    print("=" * 65)
    print("  AGENT RED — TENANT #1 PROVISIONING")
    print("=" * 65)
    print()
    print(f"  Tenant ID:      {TENANT_ID}")
    print(f"  Shop domain:    {SHOP_DOMAIN}")
    print(f"  Tier:           {TIER}")
    print(f"  Channel:        {BILLING_CHANNEL}")
    print(f"  Status:         active")
    print(f"  Email:          {CUSTOMER_EMAIL}")
    print(f"  Consent:        granted")
    print(f"  Rate limit:     50 rpm")
    print(f"  Concurrency:    10")
    print()
    print("-" * 65)
    print("  CREDENTIALS (save these — they cannot be retrieved later)")
    print("-" * 65)
    print()
    print(f"  API Key:        {api_key}")
    print(f"  Widget Key:     {widget_key}")
    print()
    print(f"  API Key Hash:   {hash_key(api_key)}")
    print(f"  Widget Key Hash:{hash_key(widget_key)}")
    print()

    if dry_run:
        print("[DRY RUN] No database writes. Run with --provision to create.")
        print()
        return

    # Initialize Cosmos DB connection
    cosmos = get_cosmos_manager()
    await cosmos.initialize()

    from src.multi_tenant.repository import DocumentConflictError

    repo = TenantRepository()
    try:
        await repo.create(TENANT_ID, tenant_doc)
        print("[OK] Tenant document created in Cosmos DB.")
    except (DocumentConflictError, Exception) as e:
        if "Conflict" in str(e) or "409" in str(e) or "already exists" in str(e):
            print(f"[SKIP] Tenant {TENANT_ID} already exists. Updating...")
            await repo.upsert(TENANT_ID, tenant_doc)
            print("[OK] Tenant document updated (upsert).")
        else:
            print(f"[ERROR] Failed to create tenant: {e}")
            raise

    # Also create a default preferences document
    from src.multi_tenant.cosmos_schema import PreferencesDocument
    from src.multi_tenant.repository import PreferencesRepository

    prefs_repo = PreferencesRepository()
    prefs_doc = PreferencesDocument(
        id=f"{TENANT_ID}:1",
        tenant_id=TENANT_ID,
        version=1,
        is_current=True,
        # Brand & tone
        brand_name="Agent Red",
        brand_voice="helpful, professional, and knowledgeable",
        # Languages
        primary_language="en",
        additional_languages=[],
        # Response style
        response_length="standard",
        formality_level="balanced",
        # Business policies
        return_policy="Agent Red subscriptions can be cancelled at any time. Monthly subscriptions end at the close of the current billing period. Annual subscriptions are non-refundable but can be cancelled to prevent renewal.",
        shipping_info="Agent Red is a cloud-hosted SaaS product. No shipping required. Access is provisioned immediately upon subscription activation.",
        # Escalation rules
        escalation_threshold=0.7,
        escalation_keywords=["speak to a person", "human agent", "manager", "refund", "cancel subscription"],
        # Memory & privacy
        memory_enabled=True,
        # Custom instructions
        custom_instructions=(
            "You are the Agent Red AI assistant on the Agent Red Customer Experience "
            "storefront. Your role is to help visitors and merchants understand "
            "Agent Red's features, pricing, setup process, and competitive advantages. "
            "You are a live demonstration of the product itself — your responses showcase "
            "Persistent Customer Memory, fail-closed safety validation, and the six-agent "
            "pipeline. When asked about competitors, be factual and specific about Agent Red's "
            "advantages (4-21x cheaper, 4.7x faster P50, lightweight 15-20KB widget) without "
            "disparaging other products. For returning visitors, reference their previous "
            "interactions to demonstrate the memory capability."
        ),
        # Widget appearance — visual
        widget_primary_color="#C41E2A",
        widget_background_color="#141414",
        widget_position="bottom-right",
        widget_offset_x=20,
        widget_offset_y=20,
        widget_agent_display_name="Agent Red AI",
        widget_agent_title="Customer Experience Assistant",
        widget_show_branding=True,
        widget_mobile_enabled=True,
        widget_dark_mode=True,
        # Widget behavior
        widget_offline_message="We're currently offline, but our AI assistant is available 24/7. Leave a message and we'll follow up!",
        widget_auto_open=True,
        widget_auto_open_delay=5,
        widget_offline_behavior="ai_only",
        widget_chat_rating_enabled=True,
        widget_sound_enabled=True,
        widget_file_upload_enabled=False,
        # Widget content
        widget_header_text="Agent Red Support",
        widget_input_placeholder="Ask about features, pricing, or setup...",
        widget_page_rules=[],
        # Metadata
        created_at=now,
        created_by="provision_tenant_one.py",
    )

    try:
        await prefs_repo.create(TENANT_ID, prefs_doc)
        print("[OK] Preferences document created.")
    except (DocumentConflictError, Exception) as e:
        if "Conflict" in str(e) or "409" in str(e) or "already exists" in str(e):
            await prefs_repo.upsert(TENANT_ID, prefs_doc)
            print("[OK] Preferences document updated (upsert).")
        else:
            print(f"[ERROR] Failed to create preferences: {e}")

    print()

    # Optionally seed knowledge base
    if seed_kb:
        print("Seeding knowledge base...")
        print()
        from scripts.seed_knowledge_base import TOTAL_ARTICLES, load_to_cosmos
        await load_to_cosmos(tenant_id=TENANT_ID)
        print()

    print("=" * 65)
    print("  PROVISIONING COMPLETE")
    print("=" * 65)
    print()
    print("  Next steps:")
    print("  1. Copy the Widget Key above")
    print("  2. Go to Shopify Admin > Online Store > Themes > Customize")
    print("  3. Click the App embeds icon (puzzle piece)")
    print("  4. Toggle 'Agent Red Chat' ON")
    print("  5. Paste the Widget Key into the configuration")
    print("  6. Save the theme")
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision agent-red.myshopify.com as Agent Red tenant #1",
    )
    parser.add_argument(
        "--provision",
        action="store_true",
        help="Write tenant document to Cosmos DB (omit for dry run)",
    )
    parser.add_argument(
        "--seed-kb",
        action="store_true",
        help="Also seed the knowledge base with 32 Agent Red articles",
    )
    args = parser.parse_args()

    dry_run = not args.provision
    await provision(dry_run=dry_run, seed_kb=args.seed_kb)


if __name__ == "__main__":
    asyncio.run(main())
