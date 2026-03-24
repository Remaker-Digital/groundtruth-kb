# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""DEK Rotation Cron Job — SPEC-1843 / WI-1630.

Rotates tenant Data Encryption Keys every 90 days:
1. Generate new DEK for the tenant
2. Re-encrypt all tenant documents with the new DEK
3. Store new wrapped DEK, retire old DEK

Designed to run as a scheduled job (Azure Container App Job or cron).

Usage:
    python -m src.jobs.run_dek_rotation [--dry-run] [--tenant TENANT_ID] [--max-age-days 90]
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import logging
import time
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

DEK_ROTATION_INTERVAL_DAYS = 90

# Same collection map as migration job — must stay in sync
ENCRYPTED_COLLECTIONS: dict[str, list[str]] = {
    "conversations": ["messages", "customer_intent", "escalation_reason", "transcript"],
    "knowledge_bases": ["content", "title", "description", "source_text"],
    "customer_profiles": ["name", "email", "phone", "address", "notes"],
    "memory_vectors": ["text", "context", "summary"],
}


def _looks_encrypted(value: str) -> bool:
    """Check if a string value looks like base64-encoded AES-256-GCM ciphertext."""
    if len(value) < 40:
        return False
    try:
        decoded = base64.b64decode(value, validate=True)
        return len(decoded) >= 29
    except Exception:
        return False


async def _get_dek_age_days(tenant_id: str) -> float | None:
    """Return the age of the tenant's DEK in days, or None if no DEK exists."""
    from src.multi_tenant.tenant_secret_service import get_secret_service

    secret_svc = get_secret_service()
    secrets = await secret_svc.list_tenant_secrets(tenant_id)
    for s in secrets:
        if s.get("type") == "dek":
            updated = s.get("updated") or s.get("created")
            if updated:
                last_rotated = datetime.fromisoformat(updated)
                age = datetime.now(timezone.utc) - last_rotated
                return age.total_seconds() / 86400.0
    return None


async def rotate_tenant_dek(tenant_id: str, *, dry_run: bool = False) -> dict:
    """Rotate the DEK for a single tenant.

    Steps:
        1. Retrieve current wrapped DEK and unwrap it (old DEK)
        2. Generate a new DEK
        3. For each document: decrypt with old DEK, encrypt with new DEK
        4. Store new wrapped DEK in Key Vault (replaces old version)

    Returns:
        Dict with counts: documents_reencrypted, fields_reencrypted, errors.
    """
    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
    from src.multi_tenant.tenant_secret_service import (
        TenantSecretType,
        get_secret_service,
    )

    svc = get_envelope_encryption_service()
    secret_svc = get_secret_service()
    if svc is None or secret_svc is None:
        logger.error("Encryption or secret service not initialized")
        return {"documents_reencrypted": 0, "fields_reencrypted": 0, "errors": 1}

    stats = {"documents_reencrypted": 0, "fields_reencrypted": 0, "errors": 0}

    # Step 1: Get current (old) wrapped DEK
    old_wrapped_b64 = await secret_svc.get_secret(tenant_id, TenantSecretType.DEK)
    if old_wrapped_b64 is None:
        logger.warning("Tenant %s has no DEK — skipping rotation", tenant_id)
        return stats

    old_wrapped_dek = base64.b64decode(old_wrapped_b64)
    # Unwrap the old DEK (pre-warm cache)
    await svc.unwrap_key_async(old_wrapped_dek, tenant_id)

    if dry_run:
        logger.info("[DRY RUN] Would rotate DEK for tenant %s", tenant_id)
        # Still count what would be re-encrypted for reporting
    else:
        logger.info("Rotating DEK for tenant %s", tenant_id)

    # Step 2: Generate new DEK
    if not dry_run:
        new_wrapped_dek = await svc.create_tenant_dek(tenant_id)
    else:
        new_wrapped_dek = None

    # Step 3: Re-encrypt all documents
    cosmos = get_cosmos_manager()
    for collection_name, fields in ENCRYPTED_COLLECTIONS.items():
        container = cosmos.get_container(collection_name)

        async for doc in container.query_items(
            query="SELECT * FROM c WHERE c.tenant_id = @tid",
            parameters=[{"name": "@tid", "value": tenant_id}],
            partition_key=tenant_id,
        ):
            doc_id = doc.get("id", "unknown")
            fields_rotated = 0

            for field in fields:
                value = doc.get(field)
                if value is None or value == "" or not isinstance(value, str):
                    continue
                if not _looks_encrypted(value):
                    # Plaintext field — should have been migrated first
                    logger.warning(
                        "Plaintext field found during rotation: %s.%s in %s (tenant %s)",
                        collection_name, field, doc_id, tenant_id,
                    )
                    continue

                if dry_run:
                    stats["fields_reencrypted"] += 1
                    fields_rotated += 1
                    continue

                # Decrypt with old DEK, re-encrypt with new DEK
                try:
                    plaintext = svc.decrypt_field(
                        old_wrapped_dek, value,
                        tenant_id=tenant_id, doc_id=doc_id,
                    )
                    doc[field] = svc.encrypt_field(
                        new_wrapped_dek, plaintext,
                        tenant_id=tenant_id, doc_id=doc_id,
                    )
                    stats["fields_reencrypted"] += 1
                    fields_rotated += 1
                except Exception:
                    logger.error(
                        "Failed to re-encrypt %s.%s in %s for tenant %s",
                        collection_name, field, doc_id, tenant_id,
                        exc_info=True,
                    )
                    stats["errors"] += 1

            if fields_rotated > 0:
                if not dry_run:
                    try:
                        await container.replace_item(item=doc_id, body=doc)
                    except Exception:
                        logger.error(
                            "Failed to write back %s/%s for tenant %s",
                            collection_name, doc_id, tenant_id,
                            exc_info=True,
                        )
                        stats["errors"] += 1
                stats["documents_reencrypted"] += 1

    # Step 4: Store new wrapped DEK (replaces old version in Key Vault)
    if not dry_run and new_wrapped_dek is not None and stats["errors"] == 0:
        new_wrapped_b64 = base64.b64encode(new_wrapped_dek).decode("ascii")
        await secret_svc.set_secret(tenant_id, TenantSecretType.DEK, new_wrapped_b64)
        logger.info("New DEK stored for tenant %s", tenant_id)
    elif stats["errors"] > 0 and not dry_run:
        logger.error(
            "DEK rotation had %d errors for tenant %s — old DEK retained",
            stats["errors"], tenant_id,
        )

    action = "DRY RUN" if dry_run else "Rotation"
    logger.info("%s complete for tenant %s: %s", action, tenant_id, stats)
    return stats


async def run_rotation(
    *, dry_run: bool = False, tenant_id: str | None = None,
    max_age_days: int = DEK_ROTATION_INTERVAL_DAYS,
) -> None:
    """Run DEK rotation for tenants with DEKs older than max_age_days."""
    from src.multi_tenant.repositories.tenant import TenantRepository

    logger.info(
        "Starting DEK rotation (dry_run=%s, max_age=%d days, tenant=%s)",
        dry_run, max_age_days, tenant_id or "ALL_ELIGIBLE",
    )
    start = time.monotonic()

    if tenant_id:
        age = await _get_dek_age_days(tenant_id)
        if age is not None and age < max_age_days:
            logger.info(
                "Tenant %s DEK age is %.1f days (< %d) — skipping",
                tenant_id, age, max_age_days,
            )
        else:
            await rotate_tenant_dek(tenant_id, dry_run=dry_run)
    else:
        # Iterate all active tenants, check DEK age
        repo = TenantRepository()
        tenant_ids = await repo.list_active_tenant_ids()
        logger.info("Checking %d active tenants for DEK rotation eligibility", len(tenant_ids))

        rotated = 0
        skipped = 0
        for i, tid in enumerate(tenant_ids, 1):
            age = await _get_dek_age_days(tid)
            if age is None:
                logger.info("Tenant %s has no DEK — skipping", tid)
                skipped += 1
                continue
            if age < max_age_days:
                logger.debug("Tenant %s DEK age %.1f days — not due", tid, age)
                skipped += 1
                continue

            logger.info("--- Rotating tenant %d/%d: %s (age: %.1f days) ---", i, len(tenant_ids), tid, age)
            await rotate_tenant_dek(tid, dry_run=dry_run)
            rotated += 1

        logger.info("Rotation pass: %d rotated, %d skipped", rotated, skipped)

    elapsed = time.monotonic() - start
    logger.info("DEK rotation finished in %.1f seconds", elapsed)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Rotate tenant DEKs")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--tenant", type=str, help="Rotate a single tenant")
    parser.add_argument("--max-age-days", type=int, default=DEK_ROTATION_INTERVAL_DAYS)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(run_rotation(dry_run=args.dry_run, tenant_id=args.tenant, max_age_days=args.max_age_days))


if __name__ == "__main__":
    main()
