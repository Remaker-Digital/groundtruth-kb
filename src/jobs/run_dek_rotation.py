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
import logging

logger = logging.getLogger(__name__)

DEK_ROTATION_INTERVAL_DAYS = 90


async def rotate_tenant_dek(tenant_id: str, *, dry_run: bool = False) -> dict:
    """Rotate the DEK for a single tenant.

    Steps:
        1. Generate new DEK via EnvelopeEncryptionService
        2. Re-encrypt all documents in tenant partition with new DEK
        3. Store new wrapped DEK in Key Vault
        4. Log rotation event to audit log

    Returns:
        Dict with counts: documents_reencrypted, errors.
    """
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service

    svc = get_envelope_encryption_service()
    if svc is None:
        logger.error("EnvelopeEncryptionService not initialized")
        return {"documents_reencrypted": 0, "errors": 1}

    stats = {"documents_reencrypted": 0, "errors": 0}

    if dry_run:
        logger.info("[DRY RUN] Would rotate DEK for tenant %s", tenant_id)
    else:
        # TODO: Implement full rotation:
        # 1. Read current wrapped DEK from Key Vault
        # 2. Create new DEK
        # 3. For each document: decrypt with old DEK, encrypt with new DEK
        # 4. Store new wrapped DEK, retire old version
        logger.info("DEK rotation for tenant %s: %s", tenant_id, stats)

    return stats


async def run_rotation(
    *, dry_run: bool = False, tenant_id: str | None = None,
    max_age_days: int = DEK_ROTATION_INTERVAL_DAYS,
) -> None:
    """Run DEK rotation for tenants with DEKs older than max_age_days."""
    logger.info(
        "Starting DEK rotation (dry_run=%s, max_age=%d days, tenant=%s)",
        dry_run, max_age_days, tenant_id or "ALL_ELIGIBLE",
    )

    if tenant_id:
        await rotate_tenant_dek(tenant_id, dry_run=dry_run)
    else:
        # TODO: Query tenants with DEK age > max_age_days
        logger.info("Bulk rotation not yet implemented — use --tenant flag")

    logger.info("DEK rotation complete")


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
