"""Seed entitlement v1 documents into platform_config (SPEC-1814, WI-1406).

Standalone script to upsert the comprehensive entitlement documents into
staging or production Cosmos DB. Safe to run multiple times — uses upsert.

Usage:
    # Dry run (default — shows what would be written)
    python scripts/seed_entitlements.py

    # Execute against staging
    python scripts/seed_entitlements.py --execute

    # Execute against production
    python scripts/seed_entitlements.py --execute --database agentred

Environment:
    COSMOS_DB_ENDPOINT  — Cosmos DB account endpoint
    COSMOS_DB_KEY       — Cosmos DB account key (or use managed identity)
    COSMOS_USE_MANAGED_ID — Set to "true" for managed identity auth

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed entitlement v1 documents into platform_config",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write to Cosmos DB (default: dry run)",
    )
    parser.add_argument(
        "--database",
        default="agentred-staging",
        help="Cosmos DB database name (default: agentred-staging)",
    )
    args = parser.parse_args()
    dry_run = not args.execute

    from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS
    from src.multi_tenant.cosmos_schema import PlatformConfigDocument

    now = datetime.now(timezone.utc).isoformat()

    # Build the document list
    documents: list[tuple[str, str, dict]] = [
        ("tier_config", "all_tiers", FROZEN_ENTITLEMENTS["tiers"]),
        ("entitlements", "pricing", FROZEN_ENTITLEMENTS["pricing"]),
        ("entitlements", "pack_pricing", FROZEN_ENTITLEMENTS["pack_pricing"]),
        ("entitlements", "sla_targets", FROZEN_ENTITLEMENTS["sla_targets"]),
        ("entitlements", "website_limits", FROZEN_ENTITLEMENTS["website_limits"]),
        ("entitlements", "integration_gates", FROZEN_ENTITLEMENTS["integration_gates"]),
        ("entitlements", "field_gates", FROZEN_ENTITLEMENTS["field_gates"]),
        ("entitlements", "global_config", FROZEN_ENTITLEMENTS["global_config"]),
    ]

    print("=" * 65)
    print(f"  Seed Entitlements v1 -> {args.database}")
    print(f"  Mode: {'EXECUTE' if not dry_run else 'DRY RUN'}")
    print(f"  Documents: {len(documents)}")
    print("=" * 65)

    if not dry_run:
        # Initialize Cosmos client
        os.environ.setdefault("COSMOS_DB_DATABASE", args.database)
        from src.multi_tenant.cosmos_client import get_cosmos_manager

        manager = get_cosmos_manager()
        await manager.initialize()
        from src.multi_tenant.repositories.platform import PlatformConfigRepository

        repo = PlatformConfigRepository()

    success = 0
    errors = 0

    for config_type, config_key, value in documents:
        doc = PlatformConfigDocument(
            id=f"{config_type}:{config_key}",
            config_type=config_type,
            config_key=config_key,
            value=value,
            version=1,
            updated_at=now,
            updated_by="seed_entitlements.py",
        )

        # Summary
        if isinstance(value, dict):
            entry_count = len(value)
            summary = f"{entry_count} entries"
        else:
            summary = str(value)[:60]

        print(f"\n  {config_type}:{config_key} — {summary}")

        if dry_run:
            # Show document content
            body = doc.model_dump(by_alias=True)
            print(f"    Would upsert: {json.dumps(body, indent=2, default=str)[:200]}...")
        else:
            try:
                await repo.set_config(doc)
                print(f"    [OK] Upserted.")
                success += 1
            except Exception as e:
                print(f"    [ERROR] {e}")
                errors += 1

    print("\n" + "=" * 65)
    if dry_run:
        print(f"  DRY RUN complete — {len(documents)} documents would be written.")
        print(f"  Re-run with --execute to write to {args.database}.")
    else:
        print(f"  DONE — {success} success, {errors} errors.")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
