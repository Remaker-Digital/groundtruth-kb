"""
seed_platform_admin.py — Seed SPA platform admin credentials (SPEC-1667).

Creates a platform admin document in the platform_admins Cosmos DB collection,
completely isolated from all tenant team_members collections. The SPA has zero
permissions within any tenancy and does not exist as a user for any tenancy.

Usage:
    python scripts/seed_platform_admin.py --env production --email admin@remaker.digital --name "Platform Admin"
    python scripts/seed_platform_admin.py --env staging --email admin@remaker.digital --name "Platform Admin"

The raw API key is printed ONCE and must be saved immediately. It is never
stored in plaintext — only the SHA-256 hash is persisted in Cosmos DB.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(".env.local")

from azure.cosmos.aio import CosmosClient

from src.multi_tenant.auth import generate_spa_api_key, hash_api_key
from src.multi_tenant.cosmos_schema import COLLECTION_PLATFORM_ADMINS


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

ENVS = {
    "production": {
        "database": "agentred",
        "endpoint_var": "COSMOS_DB_ENDPOINT",
        "key_var": "COSMOS_DB_KEY",
    },
    "staging": {
        "database": "agentred-staging",
        "endpoint_var": "COSMOS_DB_ENDPOINT",
        "key_var": "COSMOS_DB_KEY",
    },
}


async def seed_platform_admin(
    env: str,
    email: str,
    display_name: str,
) -> None:
    """Create a platform admin document in Cosmos DB."""
    config = ENVS[env]
    endpoint = os.environ.get(config["endpoint_var"])
    key = os.environ.get(config["key_var"])

    if not endpoint or not key:
        print(f"ERROR: Set {config['endpoint_var']} and {config['key_var']} in .env.local")
        sys.exit(1)

    # Generate SPA API key
    raw_key = generate_spa_api_key()
    key_hash = hash_api_key(raw_key)
    admin_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    document = {
        "id": admin_id,
        "admin_id": admin_id,
        "email": email,
        "display_name": display_name,
        "api_key_hash": key_hash,
        "is_active": True,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    print(f"\n{'='*60}")
    print(f"  SPA Platform Admin Seed — {env.upper()}")
    print(f"{'='*60}")
    print(f"  Database:     {config['database']}")
    print(f"  Collection:   {COLLECTION_PLATFORM_ADMINS}")
    print(f"  Admin ID:     {admin_id}")
    print(f"  Email:        {email}")
    print(f"  Display Name: {display_name}")
    print(f"{'='*60}\n")

    async with CosmosClient(endpoint, credential=key) as client:
        database = client.get_database_client(config["database"])

        # Ensure container exists
        try:
            container = database.get_container_client(COLLECTION_PLATFORM_ADMINS)
            await container.read()
            print(f"  [OK] Container '{COLLECTION_PLATFORM_ADMINS}' exists")
        except Exception:
            # Create the container
            print(f"  [..] Creating container '{COLLECTION_PLATFORM_ADMINS}'...")
            container = await database.create_container_if_not_exists(
                id=COLLECTION_PLATFORM_ADMINS,
                partition_key={"paths": ["/admin_id"], "kind": "Hash"},
                unique_key_policy={"uniqueKeys": [{"paths": ["/email"]}]},
            )
            print(f"  [OK] Container '{COLLECTION_PLATFORM_ADMINS}' created")

        # Check for existing admin with same email
        existing = []
        async for item in container.query_items(
            query="SELECT * FROM c WHERE c.email = @email",
            parameters=[{"name": "@email", "value": email}],
            enable_cross_partition_query=True,
        ):
            existing.append(item)

        if existing:
            print(f"\n  WARNING: Platform admin with email '{email}' already exists.")
            print(f"  Existing admin_id: {existing[0].get('admin_id')}")
            print(f"  Deactivating existing record and creating new one...\n")

            # Deactivate the old record
            old_doc = existing[0]
            old_doc["is_active"] = False
            old_doc["deactivated_at"] = now_iso
            old_doc["deactivated_reason"] = "Replaced by new seed"
            await container.replace_item(
                item=old_doc["id"],
                body=old_doc,
                partition_key=old_doc["admin_id"],
            )
            print(f"  [OK] Deactivated previous admin: {old_doc['admin_id']}")

        # Create the new admin document
        await container.create_item(body=document)
        print(f"  [OK] Platform admin created: {admin_id}")

    # Print credentials — MUST BE SAVED IMMEDIATELY
    print(f"\n{'='*60}")
    print(f"  CREDENTIALS — SAVE THESE NOW")
    print(f"{'='*60}")
    print(f"  SPA API Key:  {raw_key}")
    print(f"  Key Hash:     {key_hash[:16]}...")
    print(f"  Admin ID:     {admin_id}")
    print(f"  Email:        {email}")
    print(f"{'='*60}")
    print(f"\n  This key is printed ONCE and never stored in plaintext.")
    print(f"  Store it in Azure Key Vault:")
    print(f"    az keyvault secret set --vault-name kv-agentred-eastus \\")
    print(f"      --name SPA-PLATFORM-ADMIN-KEY --value \"{raw_key}\"")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed SPA platform admin credentials (SPEC-1667)",
    )
    parser.add_argument(
        "--env",
        choices=["production", "staging"],
        required=True,
        help="Target environment",
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Platform admin email address",
    )
    parser.add_argument(
        "--name",
        default="Platform Admin",
        help="Display name (default: 'Platform Admin')",
    )
    args = parser.parse_args()

    asyncio.run(seed_platform_admin(args.env, args.email, args.name))


if __name__ == "__main__":
    main()
