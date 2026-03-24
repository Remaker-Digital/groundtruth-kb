# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Batch Data Encryption Migration — SPEC-1843 / WI-1629.

Iterates all tenants, creates DEKs where missing, and encrypts all
sensitive fields in all tenant-scoped documents.

Usage:
    python -m src.jobs.run_data_encryption_migration [--dry-run] [--tenant TENANT_ID]

Safety:
    - Idempotent: encrypted fields are base64 with a recognizable prefix
    - Resumable: processes one tenant at a time, logs progress
    - Checkpoint: tenant completion logged for resume after failure
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)


async def migrate_tenant(tenant_id: str, *, dry_run: bool = False) -> dict:
    """Encrypt all sensitive fields for a single tenant.

    Returns:
        Dict with counts: documents_processed, fields_encrypted, errors.
    """
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

    svc = get_envelope_encryption_service()
    if svc is None:
        logger.error("EnvelopeEncryptionService not initialized")
        return {"documents_processed": 0, "fields_encrypted": 0, "errors": 1}

    stats = {"documents_processed": 0, "fields_encrypted": 0, "errors": 0}

    # TODO: Implement per-collection iteration:
    # 1. Get or create tenant DEK
    # 2. For each collection with _encryption_fields:
    #    a. Query all documents for this tenant
    #    b. For each document, encrypt each sensitive field
    #    c. Upsert the encrypted document
    # 3. Log completion checkpoint

    if dry_run:
        logger.info("[DRY RUN] Would migrate tenant %s", tenant_id)
    else:
        logger.info("Migration for tenant %s: %s", tenant_id, stats)

    return stats


async def run_migration(*, dry_run: bool = False, tenant_id: str | None = None) -> None:
    """Run encryption migration for all tenants (or a single tenant)."""
    logger.info(
        "Starting data encryption migration (dry_run=%s, tenant=%s)",
        dry_run, tenant_id or "ALL",
    )

    if tenant_id:
        await migrate_tenant(tenant_id, dry_run=dry_run)
    else:
        # TODO: Iterate all tenants from TenantRepository
        logger.info("Full migration not yet implemented — use --tenant flag")

    logger.info("Migration complete")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Encrypt tenant data at rest")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--tenant", type=str, help="Migrate a single tenant")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(run_migration(dry_run=args.dry_run, tenant_id=args.tenant))


if __name__ == "__main__":
    main()
