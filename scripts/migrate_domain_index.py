#!/usr/bin/env python3
"""One-time migration: populate domain_index for all existing tenants.

SPEC-1851: The domain_index collection provides O(1) lookups for
Shopify domains and Stripe customer IDs. Tenants provisioned before
SPEC-1851 have no domain_index entries. This script backfills them.

Usage:
    python scripts/migrate_domain_index.py [--env staging|production] [--dry-run]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env.local for Cosmos credentials
from scripts._env import load_env_local
load_env_local()

# Suppress verbose Azure SDK logging
import logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)


async def main(env: str, dry_run: bool) -> None:
    # Set environment before any imports
    if env == "production":
        os.environ.setdefault("COSMOS_DATABASE_NAME", "agentred")
    else:
        os.environ.setdefault("COSMOS_DATABASE_NAME", "agentred-staging")

    from azure.cosmos.aio import CosmosClient

    endpoint = os.environ["COSMOS_DB_ENDPOINT"]
    key = os.environ["COSMOS_DB_KEY"]
    db_name = os.environ.get("COSMOS_DATABASE_NAME", "agentred-staging" if env == "staging" else "agentred")

    client = CosmosClient(endpoint, key)
    database = client.get_database_client(db_name)
    tenants_container = database.get_container_client("tenants")
    domain_index_container = database.get_container_client("domain_index")

    # Query ALL tenants (not just active — deactivated tenants in grace period
    # still need index entries for reactivation lookups)
    print(f"Environment: {env}")
    print(f"Dry run: {dry_run}")
    print()
    print("Querying all tenants...")

    items = []
    async for item in tenants_container.query_items(
        query="SELECT c.tenant_id, c.shopify_shop_domain, c.stripe_customer_id, c.status FROM c",
        enable_cross_partition_query=True,
    ):
        items.append(item)

    print(f"Found {len(items)} tenants.\n")

    async def lookup(domain: str) -> str | None:
        try:
            item = await domain_index_container.read_item(item=domain, partition_key=domain)
            return item.get("tenant_id")
        except Exception:
            return None

    async def upsert(domain: str, tid: str, dtype: str) -> None:
        await domain_index_container.upsert_item({
            "id": domain, "domain": domain, "tenant_id": tid, "domain_type": dtype,
        })

    created = 0
    skipped = 0

    for tenant in items:
        tenant_id = tenant.get("tenant_id", tenant.get("id", "?"))
        shop_domain = tenant.get("shopify_shop_domain", "")
        stripe_id = tenant.get("stripe_customer_id", "")
        status = tenant.get("status", "?")

        # Shopify domain index
        if shop_domain and ".myshopify.com" in shop_domain:
            existing = await lookup(shop_domain)
            if existing == tenant_id:
                print(f"  [SKIP] {shop_domain} -> {tenant_id} (already indexed)")
                skipped += 1
            elif existing:
                print(f"  [WARN] {shop_domain} -> {existing} (indexed to DIFFERENT tenant, expected {tenant_id})")
                if not dry_run:
                    await upsert(shop_domain, tenant_id, "shopify")
                    print(f"         [FIXED] Re-indexed to {tenant_id}")
                created += 1
            else:
                print(f"  [ADD]  {shop_domain} -> {tenant_id} (status={status})")
                if not dry_run:
                    await upsert(shop_domain, tenant_id, "shopify")
                created += 1

        # Stripe customer ID index
        if stripe_id and stripe_id.startswith("cus_"):
            existing = await lookup(stripe_id)
            if existing == tenant_id:
                print(f"  [SKIP] {stripe_id} -> {tenant_id} (already indexed)")
                skipped += 1
            elif existing:
                print(f"  [WARN] {stripe_id} -> {existing} (indexed to DIFFERENT tenant, expected {tenant_id})")
                if not dry_run:
                    await upsert(stripe_id, tenant_id, "stripe")
                    print(f"         [FIXED] Re-indexed to {tenant_id}")
                created += 1
            else:
                print(f"  [ADD]  {stripe_id} -> {tenant_id} (status={status})")
                if not dry_run:
                    await upsert(stripe_id, tenant_id, "stripe")
                created += 1

    await client.close()

    print()
    print(f"Results: {created} created/fixed, {skipped} skipped")
    if dry_run:
        print("(Dry run — no changes written)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill domain_index for existing tenants")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    asyncio.run(main(args.env, args.dry_run))
