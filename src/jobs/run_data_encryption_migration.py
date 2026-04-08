# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Batch Data Encryption Migration — SPEC-1843 / WI-1629.

Iterates all tenants, creates DEKs where missing, and encrypts all
sensitive fields in all tenant-scoped documents.

Usage:
    python -m src.jobs.run_data_encryption_migration [--dry-run] [--tenant TENANT_ID]

Safety:
    - Idempotent: already-encrypted fields detected by base64 probe
    - Resumable: processes one tenant at a time, logs progress
    - Checkpoint: tenant completion logged for resume after failure
    - Bypasses repository hooks to avoid double-encryption
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import os
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Collections and their sensitive fields — MUST match repository _encryption_fields.
# Per architecture plan section 4.1.3 + SPEC-1843 full scope.
ENCRYPTED_COLLECTIONS: dict[str, list[str]] = {
    "conversations": ["messages", "customer_intent", "escalation_reason", "transcript"],
    "knowledge_bases": ["content", "title", "description", "source_text"],
    "customer_profiles": ["name", "email", "phone", "address", "notes", "preferences"],
    "memory_vectors": ["chunk_text", "source_conversation_id"],
    "tenants": ["customer_email", "shopify_shop_domain", "brand_name"],
    "team_members": ["email", "display_name"],
    "preferences": ["custom_instructions", "return_policy", "shipping_info",
                     "webhook_urls", "notification_settings"],
}


def _looks_encrypted(value: str) -> bool:
    """Check if a string value looks like base64-encoded AES-256-GCM ciphertext.

    Encrypted fields are base64(nonce(12) || ciphertext || tag(16)), so the
    decoded output is at least 29 bytes and the string is valid base64.
    """
    if len(value) < 40:
        return False
    try:
        decoded = base64.b64decode(value, validate=True)
        return len(decoded) >= 29
    except Exception:
        return False


def _serialize_for_encryption(value: Any) -> str | None:
    """Serialize a field value to string for encryption.

    Strings pass through. Lists/dicts get a ``json:`` prefix so they
    can be deserialized after decryption. Returns None for empty/None.
    """
    import json as _json
    if value is None:
        return None
    if isinstance(value, str):
        return value if value else None
    if isinstance(value, (list, dict)):
        return "json:" + _json.dumps(value, separators=(",", ":"), default=str)
    return str(value)


async def _get_or_create_tenant_dek(
    tenant_id: str,
    *,
    dry_run: bool = False,
) -> bytes | None:
    """Retrieve or create a DEK for the tenant. Returns wrapped DEK bytes."""
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
    from src.multi_tenant.tenant_secret_service import (
        TenantSecretType,
        get_secret_service,
    )

    svc = get_envelope_encryption_service()
    secret_svc = get_secret_service()
    if svc is None or secret_svc is None:
        logger.error("Encryption or secret service not initialized")
        return None

    # Check if DEK already exists and is valid (unwrappable with current KEK)
    existing = await secret_svc.get_secret(tenant_id, TenantSecretType.DEK)
    if existing is not None:
        try:
            wrapped_dek = base64.b64decode(existing)
            # Pre-warm the cache by unwrapping
            await svc.unwrap_key_async(wrapped_dek, tenant_id)
            logger.info("Existing DEK found for tenant %s", tenant_id)
            return wrapped_dek
        except Exception as exc:
            # DEK is stale (e.g., wrapped with old CMK) — recreate
            logger.warning(
                "Existing DEK for %s is invalid (will recreate): %s",
                tenant_id, str(exc)[:80],
            )

    if dry_run:
        logger.info("[DRY RUN] Would create DEK for tenant %s", tenant_id)
        return None

    # Create new DEK
    wrapped_dek = await svc.create_tenant_dek(tenant_id)
    # Store wrapped DEK in Key Vault
    wrapped_b64 = base64.b64encode(wrapped_dek).decode("ascii")
    await secret_svc.store_secret(tenant_id, TenantSecretType.DEK, wrapped_b64)
    logger.info("Created and stored new DEK for tenant %s", tenant_id)
    return wrapped_dek


async def migrate_tenant(tenant_id: str, *, dry_run: bool = False) -> dict:
    """Encrypt all sensitive fields for a single tenant.

    Reads documents directly from Cosmos (bypassing repository _post_read hooks
    which would attempt decryption on plaintext data). Encrypts each sensitive
    field, then writes back via replace_item.

    Returns:
        Dict with counts: documents_processed, fields_encrypted, errors, skipped.
    """
    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

    svc = get_envelope_encryption_service()
    if svc is None:
        logger.error("EnvelopeEncryptionService not initialized")
        return {"documents_processed": 0, "fields_encrypted": 0, "errors": 1, "skipped": 0}

    stats = {"documents_processed": 0, "fields_encrypted": 0, "errors": 0, "skipped": 0}

    # Step 1: Get or create tenant DEK
    wrapped_dek = await _get_or_create_tenant_dek(tenant_id, dry_run=dry_run)
    if wrapped_dek is None:
        if dry_run:
            logger.info("[DRY RUN] No DEK available — skipping encryption for tenant %s", tenant_id)
        else:
            logger.error("Failed to obtain DEK for tenant %s", tenant_id)
            stats["errors"] += 1
        return stats

    cosmos = get_cosmos_manager()

    # Step 2: Iterate each collection with encrypted fields
    for collection_name, fields in ENCRYPTED_COLLECTIONS.items():
        container = cosmos.get_container(collection_name)
        logger.info(
            "Migrating %s for tenant %s (fields: %s)",
            collection_name, tenant_id, fields,
        )

        # Query all documents for this tenant (raw — no repository hooks)
        doc_count = 0
        async for doc in container.query_items(
            query="SELECT * FROM c WHERE c.tenant_id = @tid",
            parameters=[{"name": "@tid", "value": tenant_id}],
            partition_key=tenant_id,
        ):
            doc_id = doc.get("id", "unknown")
            fields_encrypted_this_doc = 0

            for field in fields:
                value = doc.get(field)
                if value is None or value == "":
                    continue
                # Already-encrypted string values: skip (idempotency)
                if isinstance(value, str) and _looks_encrypted(value):
                    stats["skipped"] += 1
                    continue

                # Serialize for encryption (handles str, list, dict)
                plaintext = _serialize_for_encryption(value)
                if plaintext is None:
                    continue

                if dry_run:
                    logger.debug(
                        "[DRY RUN] Would encrypt %s.%s in doc %s (type=%s)",
                        collection_name, field, doc_id, type(value).__name__,
                    )
                    stats["fields_encrypted"] += 1
                    fields_encrypted_this_doc += 1
                    continue

                # Encrypt the serialized field
                try:
                    doc[field] = svc.encrypt_field(
                        wrapped_dek, plaintext,
                        tenant_id=tenant_id, doc_id=doc_id,
                    )
                    stats["fields_encrypted"] += 1
                    fields_encrypted_this_doc += 1
                except Exception:
                    logger.error(
                        "Failed to encrypt %s.%s in doc %s for tenant %s",
                        collection_name, field, doc_id, tenant_id,
                        exc_info=True,
                    )
                    stats["errors"] += 1

            # Write back if any fields were encrypted (and not dry run)
            if fields_encrypted_this_doc > 0 and not dry_run:
                try:
                    await container.replace_item(item=doc_id, body=doc)
                except Exception:
                    logger.error(
                        "Failed to write back %s/%s for tenant %s",
                        collection_name, doc_id, tenant_id,
                        exc_info=True,
                    )
                    stats["errors"] += 1

            doc_count += 1
            stats["documents_processed"] += 1

        logger.info(
            "  %s: %d documents processed for tenant %s",
            collection_name, doc_count, tenant_id,
        )

    action = "DRY RUN" if dry_run else "Migration"
    logger.info(
        "%s complete for tenant %s: %s",
        action, tenant_id, stats,
    )
    return stats


async def run_migration(*, dry_run: bool = False, tenant_id: str | None = None) -> None:
    """Run encryption migration for all tenants (or a single tenant)."""
    from src.multi_tenant.repositories.tenant import TenantRepository

    logger.info(
        "Starting data encryption migration (dry_run=%s, tenant=%s)",
        dry_run, tenant_id or "ALL",
    )
    start = time.monotonic()

    if tenant_id:
        await migrate_tenant(tenant_id, dry_run=dry_run)
    else:
        # Iterate all active tenants
        repo = TenantRepository()
        tenant_ids = await repo.list_active_tenant_ids()
        logger.info("Found %d active tenants to migrate", len(tenant_ids))

        totals = {"documents_processed": 0, "fields_encrypted": 0, "errors": 0, "skipped": 0}
        for i, tid in enumerate(tenant_ids, 1):
            logger.info("--- Tenant %d/%d: %s ---", i, len(tenant_ids), tid)
            stats = await migrate_tenant(tid, dry_run=dry_run)
            for key in totals:
                totals[key] += stats.get(key, 0)

        logger.info("All tenants complete: %s", totals)

    elapsed = time.monotonic() - start
    logger.info("Migration finished in %.1f seconds", elapsed)


async def _bootstrap() -> None:
    """Initialize Cosmos DB and encryption service for standalone CLI usage."""
    import os
    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.envelope_encryption import (
        EnvelopeEncryptionService,
        set_envelope_encryption_service,
    )
    from src.multi_tenant.tenant_secret_service import get_secret_service

    # Initialize Cosmos (connect only — skip container creation for migration jobs)
    cosmos = get_cosmos_manager()
    await cosmos._ensure_client()

    # Initialize encryption service
    kek_key_id = os.environ.get("MASTER_KEK_KEY_ID", "")
    vault_url = os.environ.get("AZURE_KEYVAULT_URL", "")
    dev_mode = not kek_key_id
    svc = EnvelopeEncryptionService(
        dev_mode=dev_mode,
        kek_key_id=kek_key_id or None,
        vault_url=vault_url or None,
    )
    set_envelope_encryption_service(svc)

    # Initialize secret service
    secret_svc = get_secret_service()
    await secret_svc.initialize()


async def _main_async(dry_run: bool, tenant_id: str | None, *, force: bool = False) -> None:
    """Async main: bootstrap services then run migration."""
    # Safety gate: prevent accidental production encryption from local machine
    db_name = os.environ.get("COSMOS_DB_DATABASE", "")
    logger.info("Target database: %s", db_name or "(not set)")
    if not dry_run and not force:
        if "staging" not in db_name and "dev" not in db_name:
            logger.error(
                "SAFETY GATE: COSMOS_DB_DATABASE=%s looks like production. "
                "Pass --force to confirm, or set COSMOS_DB_DATABASE to the staging DB.",
                db_name,
            )
            return
    await _bootstrap()
    await run_migration(dry_run=dry_run, tenant_id=tenant_id)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Encrypt tenant data at rest")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--tenant", type=str, help="Migrate a single tenant")
    parser.add_argument("--force", action="store_true", help="Bypass production database safety gate")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_main_async(dry_run=args.dry_run, tenant_id=args.tenant, force=args.force))


if __name__ == "__main__":
    main()
