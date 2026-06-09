"""
Reset the admin API key for an existing Agent Red tenant.

Generates a new API key, updates the SHA-256 hash in Cosmos DB,
and prints the new key. The raw key is shown ONCE and cannot be
retrieved later.

Usage:
    # Preview only (no DB writes):
    python scripts/reset_api_key.py --tenant-id remaker-digital-001

    # Actually update Cosmos DB:
    python scripts/reset_api_key.py --tenant-id remaker-digital-001 --apply

Requires Azure credentials in .env.local:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import secrets
import string
import sys

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()


API_KEY_PREFIX = "ar_live_"
API_KEY_RANDOM_LENGTH = 32
API_KEY_ALPHABET = string.ascii_letters + string.digits


def generate_api_key(tenant_id: str) -> str:
    """Generate a new API key: ar_live_{tenant_prefix}_{random}."""
    tenant_prefix = tenant_id[:8].replace("-", "")
    random_part = "".join(secrets.choice(API_KEY_ALPHABET) for _ in range(API_KEY_RANDOM_LENGTH))
    return f"{API_KEY_PREFIX}{tenant_prefix}_{random_part}"


def hash_key(key: str) -> str:
    """SHA-256 hash a key for storage."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


async def reset(tenant_id: str, apply: bool = False) -> None:
    """Generate a new API key and update the tenant document."""

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.repository import TenantRepository

    new_key = generate_api_key(tenant_id)
    new_hash = hash_key(new_key)

    print()
    print("=" * 65)
    print("  AGENT RED -- API KEY RESET")
    print("=" * 65)
    print()
    print(f"  Tenant ID:      {tenant_id}")
    print(f"  New API Key:    {new_key}")
    print(f"  New Hash:       {new_hash}")
    print()

    if not apply:
        print("  [DRY RUN] No changes written. Pass --apply to update Cosmos DB.")
        return

    # Connect to Cosmos DB
    mgr = get_cosmos_manager()
    await mgr.initialize()
    repo = TenantRepository()

    # Read existing tenant to verify it exists
    existing = await repo.read(tenant_id, tenant_id)
    if not existing:
        print(f"  [ERROR] Tenant '{tenant_id}' not found in Cosmos DB.")
        return

    print(f"  Found tenant: {existing.get('shopify_shop_domain', '(no domain)')}")
    print(f"  Current hash: {existing.get('api_key_hash', '(none)')}")
    print()

    # Update the api_key_hash
    await repo.patch(
        tenant_id,
        tenant_id,
        [{"op": "set", "path": "/api_key_hash", "value": new_hash}],
    )

    print("  [SUCCESS] API key hash updated in Cosmos DB.")
    print()
    print("-" * 65)
    print("  SAVE THIS KEY -- it cannot be retrieved later:")
    print(f"  {new_key}")
    print("-" * 65)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset API key for an Agent Red tenant")
    parser.add_argument("--tenant-id", required=True, help="Tenant ID to reset")
    parser.add_argument("--apply", action="store_true", help="Actually write to Cosmos DB")
    args = parser.parse_args()

    asyncio.run(reset(args.tenant_id, apply=args.apply))
