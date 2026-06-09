"""WI-0930 — Staging data cleanup: patch orphaned conversations to non-billable.

One-time cleanup script to fix historical data pollution from Locust load tests
and verification scripts. Uses DIRECT Cosmos DB access because the admin API
(SPEC-1607) filters out zero-message conversations — making orphans invisible
through the API layer.

Targets:
  1. is_billable=True AND message_count=0 (abandoned/rate-limited connections)
  2. is_billable=True AND conversation_id starts with non-billable prefix
  3. is_billable=True AND conversation_type='admin_assistance'

Usage:
    python scripts/cleanup_orphaned_conversations.py --env staging --dry-run
    python scripts/cleanup_orphaned_conversations.py --env staging

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

# Windows cp1252 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts._env import load_env_local

load_env_local()

from azure.cosmos import CosmosClient  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

STAGING_TENANTS = ["staging-001", "staging-002"]
# Staging uses a separate Cosmos database (agentred-staging) from production
# (agentred). This script only targets staging data — use the staging database.
STAGING_DATABASE = "agentred-staging"
CONTAINER_NAME = "conversations"

# Non-billable conversation ID prefixes (per SPEC-1606)
NON_BILLABLE_PREFIXES = ("test_", "admin_", "health_", "system_")


def get_cosmos_client() -> CosmosClient:
    """Create Cosmos client from environment variables."""
    endpoint = os.environ["COSMOS_DB_ENDPOINT"]
    key = os.environ["COSMOS_DB_KEY"]
    return CosmosClient(endpoint, credential=key)


def find_orphaned_conversations(container, tenant_id: str) -> list[dict]:
    """Find conversations that are billable but shouldn't be.

    Uses direct Cosmos query because the admin API (SPEC-1607) filters
    out zero-message conversations, making them invisible through the
    API layer. Direct access is required for data cleanup.
    """
    query = """
    SELECT c.id, c.conversation_id, c.tenant_id, c.is_billable,
           c.message_count, c.status, c.conversation_type, c.started_at
    FROM c
    WHERE c.is_billable = true
      AND c.tenant_id = @tenant_id
      AND (
          c.message_count = 0
          OR STARTSWITH(c.conversation_id, 'test_')
          OR STARTSWITH(c.conversation_id, 'admin_')
          OR STARTSWITH(c.conversation_id, 'health_')
          OR STARTSWITH(c.conversation_id, 'system_')
          OR c.conversation_type = 'admin_assistance'
      )
    """
    params = [{"name": "@tenant_id", "value": tenant_id}]
    items = list(
        container.query_items(
            query=query,
            parameters=params,
            partition_key=tenant_id,
        )
    )
    return items


def count_all_conversations(container, tenant_id: str) -> dict[str, int]:
    """Get conversation counts for reporting."""
    query = """
    SELECT
        COUNT(1) AS total,
        SUM(c.is_billable ? 1 : 0) AS billable,
        SUM(c.message_count = 0 ? 1 : 0) AS zero_messages,
        SUM(c.is_billable = true AND c.message_count = 0 ? 1 : 0) AS billable_zero_msg
    FROM c
    WHERE c.tenant_id = @tenant_id
    """
    params = [{"name": "@tenant_id", "value": tenant_id}]
    results = list(
        container.query_items(
            query=query,
            parameters=params,
            partition_key=tenant_id,
        )
    )
    if results:
        return results[0]
    return {"total": 0, "billable": 0, "zero_messages": 0, "billable_zero_msg": 0}


def patch_to_non_billable(container, item: dict, dry_run: bool = True) -> bool:
    """Patch a single conversation to is_billable=False."""
    if dry_run:
        return True

    try:
        container.patch_item(
            item=item["id"],
            partition_key=item["tenant_id"],
            patch_operations=[
                {"op": "set", "path": "/is_billable", "value": False},
            ],
        )
        return True
    except Exception as e:
        print(f"  x Failed to patch {item['conversation_id']}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="WI-0930: Cleanup orphaned conversations")
    parser.add_argument("--env", choices=["staging"], required=True, help="Target environment (staging only)")
    parser.add_argument("--tenant", help="Specific tenant ID (default: all staging tenants)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Report only, do not patch")
    args = parser.parse_args()

    tenants = [args.tenant] if args.tenant else STAGING_TENANTS

    print(f"\nWI-0930: Staging Data Cleanup")
    print(f"{'=' * 60}")
    print(f"  Environment: {args.env}")
    print(f"  Tenants:     {', '.join(tenants)}")
    print(f"  Mode:        {'DRY RUN' if args.dry_run else 'LIVE PATCH'}")
    print(f"{'=' * 60}\n")

    client = get_cosmos_client()
    database = client.get_database_client(STAGING_DATABASE)
    container = database.get_container_client(CONTAINER_NAME)

    total_found = 0
    total_patched = 0
    total_errors = 0

    for tenant_id in tenants:
        print(f"--- {tenant_id} ---")

        # Pre-cleanup counts
        counts = count_all_conversations(container, tenant_id)
        print(f"  Before cleanup:")
        print(f"    Total conversations:     {counts.get('total', 0)}")
        print(f"    Billable:                {counts.get('billable', 0)}")
        print(f"    Zero-message:            {counts.get('zero_messages', 0)}")
        print(f"    Billable + zero-message: {counts.get('billable_zero_msg', 0)}")
        print()

        # Find orphans
        orphans = find_orphaned_conversations(container, tenant_id)
        print(f"  Orphaned billable conversations: {len(orphans)}")

        if not orphans:
            print(f"  No cleanup needed.\n")
            continue

        # Categorize
        zero_msg = [o for o in orphans if o.get("message_count", 0) == 0]
        prefixed = [
            o
            for o in orphans
            if any(o.get("conversation_id", "").startswith(p) for p in NON_BILLABLE_PREFIXES)
            and o.get("message_count", 0) > 0
        ]
        admin_asst = [
            o
            for o in orphans
            if o.get("conversation_type") == "admin_assistance"
            and o.get("message_count", 0) > 0
            and not any(o.get("conversation_id", "").startswith(p) for p in NON_BILLABLE_PREFIXES)
        ]

        print(f"    Zero-message (abandoned):     {len(zero_msg)}")
        print(f"    Non-billable prefix:          {len(prefixed)}")
        print(f"    Admin assistance:             {len(admin_asst)}")
        print()

        # Patch each orphan
        patched = 0
        errors = 0
        for o in orphans:
            reason = (
                "zero_msg"
                if o.get("message_count", 0) == 0
                else (
                    "prefix"
                    if any(o.get("conversation_id", "").startswith(p) for p in NON_BILLABLE_PREFIXES)
                    else "admin_assistance"
                )
            )
            status = o.get("status", "?")
            msg_count = o.get("message_count", 0)
            conv_id = o.get("conversation_id", "?")[:50]

            success = patch_to_non_billable(container, o, dry_run=args.dry_run)
            if success:
                patched += 1
            else:
                errors += 1

            action = "would patch" if args.dry_run else ("patched" if success else "FAILED")
            print(f"    {action}: {conv_id}  (reason={reason}, status={status}, msgs={msg_count})")

        total_found += len(orphans)
        total_patched += patched
        total_errors += errors

        # Post-cleanup counts (only if not dry run)
        if not args.dry_run:
            print()
            counts_after = count_all_conversations(container, tenant_id)
            print(f"  After cleanup:")
            print(f"    Total conversations:     {counts_after.get('total', 0)}")
            print(f"    Billable:                {counts_after.get('billable', 0)}")
            print(f"    Zero-message:            {counts_after.get('zero_messages', 0)}")
            print(f"    Billable + zero-message: {counts_after.get('billable_zero_msg', 0)}")

        print()

    print(f"{'=' * 60}")
    print(f"Summary")
    print(f"{'=' * 60}")
    print(f"  Total found:   {total_found}")
    print(f"  Total {'would patch' if args.dry_run else 'patched'}:  {total_patched}")
    print(f"  Total errors:  {total_errors}")
    if args.dry_run:
        print(f"\n  Re-run without --dry-run to apply patches.")
    print()


if __name__ == "__main__":
    main()
