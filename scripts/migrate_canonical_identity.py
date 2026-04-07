#!/usr/bin/env python3
"""ADR-004 Migration: Generate canonical_id for all existing customer profiles.

For each tenant:
  1. Query all CustomerProfileDocuments without canonical_id
  2. Generate cid_<uuid> for each
  3. Infer contact attribute type from existing customer_id value
  4. Write canonical_id + contact_attributes to the profile
  5. Back-fill canonical_customer_id on all conversations for that customer

Idempotent: skips profiles that already have a canonical_id.

Usage:
    python scripts/migrate_canonical_identity.py [--dry-run] [--tenant TENANT_ID]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import re
import sys
from datetime import datetime, timezone

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.multi_tenant.cosmos_schema import ContactAttributeType
from src.multi_tenant.repositories.customer import generate_canonical_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Patterns for inferring attribute type from legacy customer_id
EMAIL_PATTERN = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
SHOPIFY_GID_PATTERN = re.compile(r"^gid://shopify/Customer/\d+$")


def infer_attribute_type(customer_id: str) -> ContactAttributeType:
    """Infer the contact attribute type from a legacy customer_id value."""
    if SHOPIFY_GID_PATTERN.match(customer_id):
        return ContactAttributeType.SHOPIFY_CUSTOMER_GID
    if EMAIL_PATTERN.match(customer_id):
        return ContactAttributeType.EMAIL
    return ContactAttributeType.EXTERNAL_ID


async def migrate_tenant(
    tenant_id: str,
    *,
    dry_run: bool = False,
) -> dict[str, int]:
    """Migrate all customer profiles in a tenant to canonical identity.

    Returns:
        Stats dict: {profiles_found, profiles_migrated, profiles_skipped,
                      conversations_updated}
    """
    from src.multi_tenant.repositories.customer import CustomerProfileRepository
    from src.multi_tenant.repository import ConversationRepository

    profile_repo = CustomerProfileRepository()
    conv_repo = ConversationRepository()

    stats = {
        "profiles_found": 0,
        "profiles_migrated": 0,
        "profiles_skipped": 0,
        "conversations_updated": 0,
    }

    # Query all profiles in tenant
    profiles = await profile_repo.query(
        tenant_id=tenant_id,
        query_text="SELECT * FROM c",
        parameters=[],
    )
    stats["profiles_found"] = len(profiles)
    logger.info("Tenant %s: found %d profiles", tenant_id, len(profiles))

    now = datetime.now(timezone.utc).isoformat()

    for profile in profiles:
        old_customer_id = profile.get("customer_id", "")
        existing_canonical = profile.get("canonical_id", "")

        # Idempotent: skip if already migrated
        if existing_canonical and existing_canonical.startswith("cid_"):
            stats["profiles_skipped"] += 1
            continue

        # Generate canonical_id
        canonical_id = generate_canonical_id()

        # Infer attribute type
        attr_type = infer_attribute_type(old_customer_id)
        contact_attribute = {
            "attribute_type": attr_type.value,
            "value": old_customer_id,
            "verified": False,
            "source": "migration",
            "added_at": now,
        }

        if dry_run:
            logger.info(
                "  [DRY RUN] %s → %s (attr: %s=%s)",
                old_customer_id, canonical_id, attr_type.value, old_customer_id,
            )
            stats["profiles_migrated"] += 1
            continue

        # Update profile with canonical_id + contact_attributes
        doc_id = profile.get("id", f"{tenant_id}:{old_customer_id}")
        try:
            await profile_repo.patch(
                tenant_id=tenant_id,
                document_id=doc_id,
                operations=[
                    {"op": "set", "path": "/canonical_id", "value": canonical_id},
                    {"op": "set", "path": "/contact_attributes", "value": [contact_attribute]},
                    {"op": "set", "path": "/updated_at", "value": now},
                ],
            )
            stats["profiles_migrated"] += 1
            logger.info(
                "  Migrated %s → %s (attr: %s)",
                old_customer_id, canonical_id, attr_type.value,
            )
        except Exception as exc:
            logger.error("  FAILED to migrate profile %s: %s", old_customer_id, exc)
            continue

        # Back-fill canonical_customer_id on conversations
        try:
            conversations = await conv_repo.query(
                tenant_id=tenant_id,
                query_text="SELECT c.id FROM c WHERE c.customer_id = @cid",
                parameters=[{"name": "@cid", "value": old_customer_id}],
            )
            for conv in conversations:
                conv_id = conv.get("id", "")
                try:
                    await conv_repo.patch(
                        tenant_id=tenant_id,
                        document_id=conv_id,
                        operations=[
                            {"op": "set", "path": "/canonical_customer_id", "value": canonical_id},
                        ],
                    )
                    stats["conversations_updated"] += 1
                except Exception as exc:
                    logger.warning("  FAILED to update conversation %s: %s", conv_id, exc)
        except Exception as exc:
            logger.warning("  FAILED to query conversations for %s: %s", old_customer_id, exc)

    return stats


async def main(args: argparse.Namespace) -> None:
    """Run migration for specified or all tenants."""
    if args.tenant:
        tenant_ids = [args.tenant]
    else:
        # Query all active tenants
        from src.multi_tenant.repository import TenantRepository
        tenant_repo = TenantRepository()
        tenants = await tenant_repo.query(
            tenant_id="",  # platform-wide
            query_text="SELECT c.tenant_id FROM c WHERE c.status = 'active'",
            parameters=[],
        )
        tenant_ids = [t["tenant_id"] for t in tenants]

    logger.info(
        "%s migration for %d tenant(s)%s",
        "DRY RUN" if args.dry_run else "LIVE",
        len(tenant_ids),
        f": {tenant_ids}" if len(tenant_ids) <= 10 else "",
    )

    totals = {
        "profiles_found": 0,
        "profiles_migrated": 0,
        "profiles_skipped": 0,
        "conversations_updated": 0,
    }

    for tenant_id in tenant_ids:
        stats = await migrate_tenant(tenant_id, dry_run=args.dry_run)
        for k in totals:
            totals[k] += stats[k]

    logger.info("=" * 60)
    logger.info("Migration complete:")
    logger.info("  Profiles found:         %d", totals["profiles_found"])
    logger.info("  Profiles migrated:      %d", totals["profiles_migrated"])
    logger.info("  Profiles skipped:       %d", totals["profiles_skipped"])
    logger.info("  Conversations updated:  %d", totals["conversations_updated"])
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ADR-004 Canonical Identity Migration")
    parser.add_argument("--dry-run", action="store_true", help="Log changes without applying")
    parser.add_argument("--tenant", type=str, help="Migrate a specific tenant only")
    args = parser.parse_args()
    asyncio.run(main(args))
