#!/usr/bin/env python3
"""Fix lost-DEK encryption: overwrite unrecoverable ciphertext with known plaintext.

Root cause: S263 encryption migration ran in dev-mode (MASTER_KEK_KEY_ID and
AZURE_KEYVAULT_URL absent from .env.local). DEKs were created in-memory (dev store)
and lost when the script exited. A subsequent DEK provisioning step stored NEW
RSA-wrapped DEKs in KV, but these don't match the DEKs used to encrypt the data.

Remediation: since ALL affected data is seeded test/demo data with known values,
overwrite encrypted fields with the original plaintext values.

Usage:
    # Dry run:
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py --dry-run --force

    # Execute:
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py --force

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env.local
_env_local = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(_env_local):
    with open(_env_local, "rb") as _f:
        for _line in _f:
            _line = _line.decode("utf-8", errors="replace").strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

logger = logging.getLogger("fix_lost_dek")

# Known plaintext values for seeded tenants.
# These are the original values from seed_tenant.py.
TENANT_FIXES: dict[str, dict[str, str]] = {
    "remaker-digital-001": {
        "customer_email": "mike@remakerdigital.com",
        "shopify_shop_domain": "blanco-9939.myshopify.com",
        "brand_name": "",  # Was empty before encryption
    },
    "test-customer-001": {
        "customer_email": "test-customer@remakerdigital.com",
        "shopify_shop_domain": "",
        "brand_name": "",
    },
}

# Known plaintext for team_members (seeded by seed_tenant.py)
TEAM_MEMBER_FIXES: dict[str, dict[str, dict[str, str]]] = {
    "remaker-digital-001": {
        # There's one team member per tenant from seeding
        "_all_": {"email": "mike@remakerdigital.com", "display_name": "Mike"},
    },
    "test-customer-001": {
        "_all_": {"email": "test-customer@remakerdigital.com", "display_name": "Test Customer"},
    },
}


def _looks_encrypted(value: str) -> bool:
    """Check if value looks like base64 ciphertext."""
    if not value or len(value) < 20:
        return False
    try:
        raw = base64.b64decode(value)
        return len(raw) >= 29  # nonce(12) + min ct + tag(16)
    except Exception:
        return False


async def fix_tenants(dry_run: bool) -> int:
    """Fix encrypted tenant fields. Returns count of fields fixed."""
    from azure.cosmos import CosmosClient

    client = CosmosClient(os.environ["COSMOS_DB_ENDPOINT"], os.environ["COSMOS_DB_KEY"])
    db = client.get_database_client(os.environ["COSMOS_DB_DATABASE"])
    fixed = 0

    # Fix tenants collection
    container = db.get_container_client("tenants")
    for tenant_id, field_fixes in TENANT_FIXES.items():
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id=@id",
            parameters=[{"name": "@id", "value": tenant_id}],
            partition_key=tenant_id,
        ))
        if not items:
            logger.warning("Tenant %s not found — skipping", tenant_id)
            continue

        doc = items[0]
        changes = {}
        for field, plaintext in field_fixes.items():
            current = doc.get(field, "")
            if _looks_encrypted(current):
                changes[field] = plaintext
                logger.info(
                    "  tenants/%s.%s: %d chars ciphertext -> '%s'",
                    tenant_id, field, len(current),
                    plaintext[:20] if plaintext else "(empty)",
                )

        if changes:
            if dry_run:
                logger.info("  [DRY RUN] Would fix %d fields in tenants/%s", len(changes), tenant_id)
            else:
                for field, plaintext in changes.items():
                    doc[field] = plaintext
                container.replace_item(item=doc["id"], body=doc)
                logger.info("  Fixed %d fields in tenants/%s", len(changes), tenant_id)
            fixed += len(changes)
        else:
            logger.info("  tenants/%s: no encrypted fields found", tenant_id)

    # Fix team_members collection
    tm_container = db.get_container_client("team_members")
    for tenant_id, member_fixes in TEAM_MEMBER_FIXES.items():
        items = list(tm_container.query_items(
            query="SELECT * FROM c",
            partition_key=tenant_id,
        ))
        for doc in items:
            changes = {}
            fix_data = member_fixes.get("_all_", {})
            for field, plaintext in fix_data.items():
                current = doc.get(field, "")
                if _looks_encrypted(current):
                    changes[field] = plaintext
                    logger.info(
                        "  team_members/%s/%s.%s: ciphertext -> '%s'",
                        tenant_id, doc["id"][:12], field, plaintext[:20],
                    )

            if changes:
                if dry_run:
                    logger.info("  [DRY RUN] Would fix %d fields in team_members/%s/%s",
                                len(changes), tenant_id, doc["id"][:12])
                else:
                    for field, plaintext in changes.items():
                        doc[field] = plaintext
                    tm_container.replace_item(item=doc["id"], body=doc)
                    logger.info("  Fixed %d fields", len(changes))
                fixed += len(changes)

    # Fix remaining 8 tenants that only have encrypted email
    # These are auto-generated tenants from testing with template emails
    all_tenants = list(container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True,
    ))
    for doc in all_tenants:
        tid = doc["id"]
        if tid in TENANT_FIXES:
            continue  # Already handled above

        changes = {}
        for field in ["customer_email", "shopify_shop_domain", "brand_name"]:
            current = doc.get(field, "")
            if _looks_encrypted(current):
                # For unknown tenants, clear the encrypted field since we can't recover it
                # These are test tenants with generated data
                changes[field] = ""
                logger.info(
                    "  tenants/%s.%s: clearing unrecoverable ciphertext (%d chars)",
                    tid, field, len(current),
                )

        if changes:
            if dry_run:
                logger.info("  [DRY RUN] Would clear %d fields in tenants/%s", len(changes), tid)
            else:
                for field, plaintext in changes.items():
                    doc[field] = plaintext
                container.replace_item(item=doc["id"], body=doc)
                logger.info("  Cleared %d fields in tenants/%s", len(changes), tid)
            fixed += len(changes)

    return fixed


async def cleanup_stale_deks(dry_run: bool) -> int:
    """Delete stale DEKs from KV that don't match any data."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.secrets.aio import SecretClient

    vault_url = os.environ.get("PRODUCTION_AZURE_KEYVAULT_URL", os.environ.get("AZURE_KEYVAULT_URL", ""))
    cred = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=cred)
    deleted = 0

    try:
        async for prop in client.list_properties_of_secrets():
            if prop.name.startswith("tenant-") and prop.name.endswith("-dek"):
                if dry_run:
                    logger.info("  [DRY RUN] Would delete stale DEK: %s", prop.name)
                else:
                    await client.delete_secret(prop.name)
                    logger.info("  Deleted stale DEK: %s", prop.name)
                deleted += 1
    finally:
        await client.close()
        await cred.close()

    return deleted


async def main_async(dry_run: bool, force: bool) -> None:
    db_name = os.environ.get("COSMOS_DB_DATABASE", "")
    logger.info("Target database: %s", db_name or "(not set)")

    if not force:
        if "staging" not in db_name and "dev" not in db_name:
            logger.error(
                "SAFETY GATE: COSMOS_DB_DATABASE=%s looks like production. "
                "Pass --force to confirm.",
                db_name,
            )
            return

    logger.info("Step 1: Restoring plaintext values...")
    fixed = await fix_tenants(dry_run)
    logger.info("Step 1 complete: %d fields %s", fixed, "would be fixed" if dry_run else "fixed")

    logger.info("Step 2: Cleaning up stale DEKs from KV...")
    deleted = await cleanup_stale_deks(dry_run)
    logger.info("Step 2 complete: %d DEKs %s", deleted, "would be deleted" if dry_run else "deleted")

    logger.info("DONE. After re-running the encryption migration with correct env vars,")
    logger.info("data will be properly encrypted with recoverable DEKs.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix lost-DEK encrypted fields")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main_async(dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
