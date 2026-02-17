"""
Cleanup demo/phantom data from Cosmos DB for a tenant.

Removes demo conversations, customer profiles, memory vectors, and
resets the usage counter. Also patches preferences to DRAFT state
with empty brand_name so the admin must configure before activation.

Usage:
    # Dry run (default):
    python scripts/cleanup_demo_data.py

    # Execute:
    python scripts/cleanup_demo_data.py --execute

Requires Azure credentials in .env.local:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Suppress verbose Azure SDK logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)

TENANT_ID = "remaker-digital-001"

# Containers to purge all documents for this tenant
PURGE_CONTAINERS = [
    ("conversations", "/tenant_id"),
    ("customer_profiles", "/tenant_id"),
    ("memory_vectors", "/tenant_id"),
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main(dry_run: bool) -> None:
    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.cosmos_schema import DATABASE_NAME

    cosmos = get_cosmos_manager()
    database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)

    await cosmos._ensure_client()
    assert cosmos._client is not None

    db = cosmos._client.get_database_client(database_name)

    print()
    print("=" * 65)
    print("  Agent Red — Demo Data Cleanup")
    print(f"  Tenant: {TENANT_ID}")
    print(f"  Mode:   {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("=" * 65)

    # --- Phase 1: Purge demo data containers ---

    for container_name, pk_path in PURGE_CONTAINERS:
        print(f"\n  [{container_name}]")
        container = db.get_container_client(container_name)

        # Query all document IDs for this tenant
        query = f"SELECT c.id FROM c WHERE c.tenant_id = '{TENANT_ID}'"
        items = []
        async for item in container.query_items(
            query=query,
            partition_key=TENANT_ID,
        ):
            items.append(item["id"])

        print(f"    Found {len(items)} document(s)")

        if dry_run:
            print(f"    [DRY RUN] Would delete {len(items)} documents")
            continue

        deleted = 0
        for doc_id in items:
            try:
                await container.delete_item(item=doc_id, partition_key=TENANT_ID)
                deleted += 1
            except Exception as e:
                print(f"    [ERROR] Failed to delete {doc_id}: {e}")
        print(f"    Deleted {deleted}/{len(items)} documents")

    # --- Phase 2: Reset usage counter ---

    print(f"\n  [usage]")
    usage_container = db.get_container_client("usage")
    usage_query = f"SELECT c.id FROM c WHERE c.tenant_id = '{TENANT_ID}'"
    usage_items = []
    async for item in usage_container.query_items(
        query=usage_query,
        partition_key=TENANT_ID,
    ):
        usage_items.append(item["id"])

    print(f"    Found {len(usage_items)} usage document(s)")

    if dry_run:
        print(f"    [DRY RUN] Would delete {len(usage_items)} usage documents")
    else:
        for doc_id in usage_items:
            try:
                await usage_container.delete_item(item=doc_id, partition_key=TENANT_ID)
            except Exception as e:
                print(f"    [ERROR] Failed to delete usage {doc_id}: {e}")
        print(f"    Deleted {len(usage_items)} usage documents")

    # --- Phase 3: Patch preferences to DRAFT state ---

    print(f"\n  [preferences]")
    prefs_container = db.get_container_client("preferences")

    # Find the current preferences document
    prefs_query = (
        f"SELECT * FROM c WHERE c.tenant_id = '{TENANT_ID}' "
        f"AND c.is_current = true"
    )
    prefs_doc = None
    async for item in prefs_container.query_items(
        query=prefs_query,
        partition_key=TENANT_ID,
    ):
        prefs_doc = item
        break

    if prefs_doc is None:
        print("    [WARN] No current preferences document found")
    else:
        current_state = prefs_doc.get("config_state", "unknown")
        current_brand = prefs_doc.get("brand_name", "")
        print(f"    Current: config_state={current_state}, brand_name='{current_brand}'")

        if dry_run:
            print("    [DRY RUN] Would patch to config_state=draft, brand_name=''")
        else:
            patch_ops = [
                {"op": "set", "path": "/config_state", "value": "draft"},
                {"op": "set", "path": "/brand_name", "value": ""},
                {"op": "set", "path": "/activated_at", "value": None},
                {"op": "set", "path": "/activated_by", "value": None},
            ]
            try:
                await prefs_container.patch_item(
                    item=prefs_doc["id"],
                    partition_key=TENANT_ID,
                    patch_operations=patch_ops,
                )
                print("    Patched: config_state=draft, brand_name='', activated_at=null")
            except Exception as e:
                print(f"    [ERROR] Patch failed: {e}")

    # --- Summary ---

    print()
    print("=" * 65)
    if dry_run:
        print("  DRY RUN complete. Re-run with --execute to apply changes.")
    else:
        print("  Cleanup complete. Tenant is now in clean DRAFT state.")
        print("  Admin must configure brand_name and activate before going live.")
    print("=" * 65)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean demo data from Cosmos DB")
    parser.add_argument("--execute", action="store_true", help="Actually delete (default: dry run)")
    args = parser.parse_args()

    asyncio.run(main(dry_run=not args.execute))
