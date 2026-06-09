"""Production database reset — delete all tenants and related data.

OWNER APPROVED: 2026-04-08 S270.
Reason: P0 encryption incident destroyed all tenant contact data.
All beta tenants are in an unrecoverable state.

Usage:
    python scripts/reset_production_tenants.py --dry-run
    python scripts/reset_production_tenants.py --execute

Requires .env.local with COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, and
PRODUCTION_COSMOS_DB_DATABASE set.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv(".env.local")

COSMOS_ENDPOINT = os.environ.get("COSMOS_DB_ENDPOINT", "")
COSMOS_KEY = os.environ.get("COSMOS_DB_KEY", "")
COSMOS_DB = os.environ.get("PRODUCTION_COSMOS_DB_DATABASE", "")

COLLECTIONS_TO_CLEAN = [
    "tenants",
    "preferences",
    "conversations",
    "usage",
    "customer_profiles",
    "knowledge_bases",
    "memory_vectors",
    "team_members",
    "alert_rules",
    "alert_history",
    "verification_tokens",
    "domain_index",
    "sla_snapshots",
]


def run(execute: bool) -> None:
    if not COSMOS_ENDPOINT or not COSMOS_KEY or not COSMOS_DB:
        print("ERROR: COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, and PRODUCTION_COSMOS_DB_DATABASE must be set")
        sys.exit(1)

    from azure.cosmos import CosmosClient

    mode = "EXECUTE" if execute else "DRY RUN"
    print(f"=== PRODUCTION RESET ({mode}) ===")
    print(f"Database: {COSMOS_DB}")
    print()

    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db = client.get_database_client(COSMOS_DB)

    total_deleted = 0

    for coll_name in COLLECTIONS_TO_CLEAN:
        try:
            container = db.get_container_client(coll_name)
            items = list(
                container.query_items(
                    query="SELECT c.id, c.tenant_id FROM c",
                    enable_cross_partition_query=True,
                )
            )

            if not items:
                print(f"  {coll_name}: empty")
                continue

            print(f"  {coll_name}: {len(items)} items", end="")

            if execute:
                count = 0
                for item in items:
                    pk = item.get("tenant_id", item["id"])
                    try:
                        container.delete_item(item=item["id"], partition_key=pk)
                        count += 1
                    except Exception:
                        pass
                print(f" -- {count} deleted")
                total_deleted += count
            else:
                print(" -- would delete")
                total_deleted += len(items)

        except Exception as e:
            print(f"  {coll_name}: skipped ({str(e)[:50]})")

    print()
    print(f"Total: {total_deleted} items {'deleted' if execute else 'would be deleted'}")
    print(f"=== {'DONE' if execute else 'DRY RUN COMPLETE -- use --execute to apply'} ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset production tenant data")
    parser.add_argument("--execute", action="store_true", help="Actually delete (default: dry run)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    args = parser.parse_args()

    if not args.execute:
        print("Running in DRY RUN mode. Use --execute to actually delete.\n")

    run(execute=args.execute)


if __name__ == "__main__":
    main()
