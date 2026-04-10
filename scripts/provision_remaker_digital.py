"""Provision the Remaker Digital smoke-test tenant on production.

Creates a single tenant with:
  - display_name: "Remaker Digital"
  - customer_email: info@remakerdigital.com
  - billing_channel: shopify
  - tier: professional

Generates API key and widget key, prints them for .env.local storage.

Usage:
    python scripts/provision_remaker_digital.py --dry-run
    python scripts/provision_remaker_digital.py --execute

Requires .env.local with COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, and
PRODUCTION_COSMOS_DB_DATABASE set.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import sys
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv(".env.local")

COSMOS_ENDPOINT = os.environ.get("COSMOS_DB_ENDPOINT", "")
COSMOS_KEY = os.environ.get("COSMOS_DB_KEY", "")
COSMOS_DB = os.environ.get("PRODUCTION_COSMOS_DB_DATABASE", "")

# Tenant configuration
DISPLAY_NAME = "Remaker Digital"
CUSTOMER_EMAIL = "info@remakerdigital.com"
BILLING_CHANNEL = "shopify"
TIER = "professional"


def run(execute: bool) -> None:
    if not COSMOS_ENDPOINT or not COSMOS_KEY or not COSMOS_DB:
        print("ERROR: COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, and PRODUCTION_COSMOS_DB_DATABASE must be set")
        sys.exit(1)

    from azure.cosmos import CosmosClient

    mode = "EXECUTE" if execute else "DRY RUN"
    print(f"=== PROVISION REMAKER DIGITAL ({mode}) ===")
    print(f"Database: {COSMOS_DB}")
    print()

    # Generate credentials
    tenant_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    # Tenant API key
    api_key = f"ar_live_rema_{secrets.token_urlsafe(24)}"
    api_key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    api_key_prefix = api_key[:16] + "..."

    # Widget key
    tid_hash = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()[:12]
    widget_random = secrets.token_hex(16)
    widget_key = f"pk_live_{tid_hash}_{widget_random}"
    widget_key_hash = hashlib.sha256(widget_key.encode("utf-8")).hexdigest()

    print(f"Tenant ID:    {tenant_id}")
    print(f"Display Name: {DISPLAY_NAME}")
    print(f"Email:        {CUSTOMER_EMAIL}")
    print(f"Channel:      {BILLING_CHANNEL}")
    print(f"Tier:         {TIER}")
    print(f"API Key:      {api_key}")
    print(f"Widget Key:   {widget_key}")
    print()

    if not execute:
        print("DRY RUN — no changes made. Use --execute to provision.")
        return

    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db = client.get_database_client(COSMOS_DB)

    # Create tenant document
    tenant_doc = {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "display_name": DISPLAY_NAME,
        "status": "active",
        "billing_channel": BILLING_CHANNEL,
        "tier": TIER,
        "interval": "month",
        "addons": [],
        "customer_email": CUSTOMER_EMAIL,
        "customer_phone": None,
        "consent_status": "granted",
        "api_key_hash": api_key_hash,
        "api_key_prefix": api_key_prefix,
        "widget_key_hash": widget_key_hash,
        "shopify_shop_domain": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    tenants = db.get_container_client("tenants")
    tenants.upsert_item(tenant_doc)
    print("Tenant document created.")

    # Create default preferences document
    prefs_doc = {
        "id": f"{tenant_id}:1",
        "tenant_id": tenant_id,
        "version": 1,
        "is_current": True,
        "config_state": "active",
        "brand_name": DISPLAY_NAME,
        "brand_voice": "professional",
        "greeting_message": f"Welcome to {DISPLAY_NAME}! How can we help you today?",
        "primary_language": "en",
        "widget_primary_color": "#ff3621",
        "widget_background_color": "#141414",
        "widget_position": "bottom-right",
        "widget_dark_mode": True,
        "widget_header_title": "Support",
        "widget_header_subtitle": "We typically reply within minutes",
        "customer_email_verification": "required",
        "widget_key": widget_key,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    preferences = db.get_container_client("preferences")
    preferences.upsert_item(prefs_doc)
    print("Preferences document created.")

    print()
    print("=== SAVE THESE KEYS TO .env.local ===")
    print(f"PRODUCTION_REMAKER_TENANT_ID={tenant_id}")
    print(f"PRODUCTION_REMAKER_TENANT_KEY={api_key}")
    print(f"PRODUCTION_REMAKER_WIDGET_KEY={widget_key}")
    print("=====================================")
    print()
    print("=== PROVISIONING COMPLETE ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision Remaker Digital tenant")
    parser.add_argument("--execute", action="store_true", help="Actually provision")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    args = parser.parse_args()

    if not args.execute:
        print("Running in DRY RUN mode. Use --execute to actually provision.\n")

    run(execute=args.execute)


if __name__ == "__main__":
    main()
