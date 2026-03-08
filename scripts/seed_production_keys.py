"""
seed_production_keys.py — Seed API keys for existing production tenants.

Surgical script: reads existing tenant and team_member documents from
production Cosmos DB, generates API keys + widget keys for any documents
with null hashes, and updates ONLY the key-related fields (no document
recreation, no data loss).

Usage:
    # Survey (read-only) — show all tenants and their key status
    python scripts/seed_production_keys.py --env production --survey

    # Dry run — show what would be changed
    python scripts/seed_production_keys.py --env production --dry-run

    # Execute — generate and persist keys
    python scripts/seed_production_keys.py --env production --execute

    # Single tenant only
    python scripts/seed_production_keys.py --env production --execute --tenant remaker-digital-001

    # Staging (for testing the script itself)
    python scripts/seed_production_keys.py --env staging --survey

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(".env.local")

from azure.cosmos.aio import CosmosClient

from src.multi_tenant.auth import (
    generate_user_api_key,
    generate_widget_key,
    hash_api_key,
    hash_widget_key,
)


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


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


async def _get_all_tenants(db) -> list[dict]:
    """Read all tenant documents from the tenants collection."""
    container = db.get_container_client("tenants")
    query = "SELECT * FROM c"
    items = container.query_items(
        query=query,
        partition_key=None,
    )
    results = []
    async for item in items:
        results.append(item)
    return results


async def _get_team_members(db, tenant_id: str) -> list[dict]:
    """Read all team member documents for a tenant."""
    container = db.get_container_client("team_members")
    query = "SELECT * FROM c WHERE c.tenant_id = @tid"
    params = [{"name": "@tid", "value": tenant_id}]
    items = container.query_items(
        query=query,
        parameters=params,
        partition_key=tenant_id,
    )
    results = []
    async for item in items:
        results.append(item)
    return results


async def survey(db, tenant_filter: str | None = None) -> None:
    """Read-only survey of all tenants and their key status."""
    print()
    print("=" * 70)
    print("  PRODUCTION TENANT SURVEY (read-only)")
    print("=" * 70)

    tenants = await _get_all_tenants(db)
    print(f"\n  Total tenants: {len(tenants)}")

    active_count = 0
    null_api_key_count = 0
    null_widget_key_count = 0

    for t in sorted(tenants, key=lambda x: x.get("tenant_id", "")):
        tid = t.get("tenant_id", t.get("id", "???"))
        if tenant_filter and tid != tenant_filter:
            continue

        status = t.get("status", "unknown")
        tier = t.get("tier", "unknown")
        email = t.get("customer_email", "")
        has_api_key = t.get("api_key_hash") is not None
        has_widget_key = t.get("widget_key_hash") is not None
        shop = t.get("shopify_shop_domain", "")
        created = t.get("created_at", "")[:19]

        if status == "active":
            active_count += 1
        if not has_api_key:
            null_api_key_count += 1
        if not has_widget_key:
            null_widget_key_count += 1

        api_status = "OK" if has_api_key else "NULL"
        widget_status = "OK" if has_widget_key else "NULL"

        print(f"\n  [{status.upper():8s}] {tid}")
        print(f"           tier={tier}, email={email}")
        print(f"           shop={shop}, created={created}")
        print(f"           api_key_hash={api_status}, widget_key_hash={widget_status}")

        # Check team members
        members = await _get_team_members(db, tid)
        members_with_keys = sum(
            1 for m in members if m.get("user_api_key_hash") is not None
        )
        print(
            f"           team_members={len(members)} "
            f"(with keys: {members_with_keys}, "
            f"without: {len(members) - members_with_keys})"
        )

    print(f"\n  Summary:")
    print(f"    Active tenants:       {active_count}")
    print(f"    Missing API key:      {null_api_key_count}")
    print(f"    Missing widget key:   {null_widget_key_count}")
    print(f"    Total tenants:        {len(tenants)}")


async def seed_keys(
    db,
    *,
    dry_run: bool = True,
    tenant_filter: str | None = None,
    active_only: bool = True,
) -> dict[str, dict]:
    """Generate and persist API keys for tenants missing them.

    SPEC-1673: Raw keys are NEVER returned, printed, or saved.
    Only SHA-256 hashes are persisted in Cosmos DB. The raw keys
    exist only in memory during generation and are discarded after
    hashing. Future: deliver raw keys via email (WI-1106).

    Returns:
        dict mapping tenant_id -> {seeded_api_key: bool, seeded_widget_key: bool,
                                    seeded_user_keys: [email, ...]}
    """
    print()
    mode = "DRY RUN" if dry_run else "EXECUTE"
    print("=" * 70)
    print(f"  PRODUCTION KEY SEEDING ({mode})")
    print("=" * 70)

    tenants = await _get_all_tenants(db)
    generated: dict[str, dict] = {}

    for t in sorted(tenants, key=lambda x: x.get("tenant_id", "")):
        tid = t.get("tenant_id", t.get("id", "???"))
        status = t.get("status", "unknown")

        if tenant_filter and tid != tenant_filter:
            continue
        if active_only and status != "active":
            print(f"\n  [SKIP] {tid} — status={status} (not active)")
            continue

        has_api_key = t.get("api_key_hash") is not None
        has_widget_key = t.get("widget_key_hash") is not None

        if has_api_key and has_widget_key:
            print(f"\n  [OK] {tid} — already has both keys")
            continue

        print(f"\n  [SEED] {tid} (status={status}, tier={t.get('tier', '?')})")
        tenant_result: dict = {
            "tenant_id": tid,
            "seeded_api_key": False,
            "seeded_widget_key": False,
            "seeded_user_keys": [],
        }

        # --- Tenant-level API key ---
        import secrets

        if not has_api_key:
            api_key = "ar_" + secrets.token_hex(24)
            api_hash = hash_api_key(api_key)
            # SPEC-1673: Raw key is NOT stored in any dict or variable
            # beyond this scope. Only the hash is persisted.
            print(f"    Tenant API key: [generated, hash ready]")

            if not dry_run:
                container = db.get_container_client("tenants")
                t["api_key_hash"] = api_hash
                t["updated_at"] = datetime.now(timezone.utc).isoformat()
                await container.upsert_item(body=t)
                print(f"    [WRITTEN] api_key_hash updated in Cosmos")
                tenant_result["seeded_api_key"] = True
            # Raw key goes out of scope here — never retained
            del api_key
        else:
            print(f"    Tenant API key: already present")

        # --- Widget key ---
        if not has_widget_key:
            widget_key = generate_widget_key(tid)
            widget_hash = hash_widget_key(widget_key)
            print(f"    Widget key: [generated, hash ready]")

            if not dry_run:
                container = db.get_container_client("tenants")
                t["widget_key_hash"] = widget_hash
                t["updated_at"] = datetime.now(timezone.utc).isoformat()
                await container.upsert_item(body=t)
                print(f"    [WRITTEN] widget_key_hash updated in Cosmos")
                tenant_result["seeded_widget_key"] = True
            del widget_key
        else:
            print(f"    Widget key: already present")

        # --- Team member user API keys ---
        members = await _get_team_members(db, tid)
        for m in members:
            email = m.get("email", "unknown")
            if m.get("user_api_key_hash") is not None:
                continue

            user_key = generate_user_api_key(tid)
            user_hash = hash_api_key(user_key)
            key_prefix = user_key[:12] + "..."
            print(f"    User key for {email}: [generated, hash ready]")

            if not dry_run:
                member_container = db.get_container_client("team_members")
                m["user_api_key_hash"] = user_hash
                m["user_api_key_prefix"] = key_prefix
                m["updated_at"] = datetime.now(timezone.utc).isoformat()
                await member_container.upsert_item(body=m)
                print(f"    [WRITTEN] user_api_key_hash for {email}")
                tenant_result["seeded_user_keys"].append(email)
            del user_key

        if tenant_result["seeded_api_key"] or tenant_result["seeded_widget_key"] or tenant_result["seeded_user_keys"]:
            generated[tid] = tenant_result

    return generated


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed production API keys")
    parser.add_argument(
        "--env",
        choices=["production", "staging"],
        required=True,
        help="Target environment",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--survey", action="store_true", help="Read-only survey")
    group.add_argument("--dry-run", action="store_true", help="Show what would change")
    group.add_argument("--execute", action="store_true", help="Actually seed keys")
    parser.add_argument("--tenant", help="Filter to a single tenant ID")
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Also seed keys for inactive tenants",
    )
    args = parser.parse_args()

    config = ENVS[args.env]
    endpoint = os.environ.get(config["endpoint_var"])
    key = os.environ.get(config["key_var"])

    if not endpoint or not key:
        print(f"ERROR: Set {config['endpoint_var']} and {config['key_var']} in .env.local")
        sys.exit(1)

    print(f"\n  Environment: {args.env}")
    print(f"  Database:    {config['database']}")
    print(f"  Endpoint:    {endpoint[:40]}...")

    async with CosmosClient(endpoint, credential=key) as client:
        db = client.get_database_client(config["database"])

        if args.survey:
            await survey(db, tenant_filter=args.tenant)
        else:
            generated = await seed_keys(
                db,
                dry_run=args.dry_run,
                tenant_filter=args.tenant,
                active_only=not args.include_inactive,
            )

            # SPEC-1673: Provider MUST NOT see raw tenant API keys.
            # Keys are generated and hashed in-memory. The raw keys are
            # discarded after hashing. Future: deliver via email (WI-1106).
            if generated:
                print()
                print("=" * 70)
                print("  KEYS GENERATED AND HASHED (SPEC-1673)")
                print("=" * 70)
                for tid, keys in generated.items():
                    print(f"\n  Tenant: {tid}")
                    if "api_key" in keys:
                        print(f"    API Key:    [GENERATED — hash stored in Cosmos]")
                    if "widget_key" in keys:
                        print(f"    Widget Key: [GENERATED — hash stored in Cosmos]")
                    for email in keys.get("user_keys", {}):
                        print(f"    User Key ({email}): [GENERATED — hash stored in Cosmos]")
                print()
                print("  Raw keys are NOT displayed or saved (SPEC-1673).")
                print("  Tenant superadmins will receive keys via email (WI-1106).")
                print("  Until WI-1106 is implemented, tenants use magic link email auth.")
            else:
                print("\n  No keys needed — all tenants have keys.")


if __name__ == "__main__":
    asyncio.run(main())
