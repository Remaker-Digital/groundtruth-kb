# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Encryption Monitoring Scan — SPEC-1843 / WI-1633.

Periodic job that checks for unencrypted documents in tenant-scoped
containers. Alerts if any documents are found without encrypted fields
after migration is complete.

This catches encryption bypass bugs — for example, a code path that
writes directly to Cosmos without going through repository hooks.

Usage:
    python -m src.jobs.run_encryption_monitor [--dry-run] [--tenant TENANT_ID]
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import logging
import time

logger = logging.getLogger(__name__)

# Collections with encrypted fields (must match WI-1627 declarations)
ENCRYPTED_COLLECTIONS: dict[str, list[str]] = {
    "conversations": ["messages", "customer_intent", "escalation_reason", "transcript"],
    "knowledge_bases": ["content", "title", "description", "source_text"],
    "customer_profiles": ["name", "email", "phone", "address", "notes"],
    "memory_vectors": ["text", "context", "summary"],
}


def _looks_encrypted(value: str) -> bool:
    """Check if a string value looks like base64-encoded AES-256-GCM ciphertext.

    Encrypted fields are base64(nonce(12) || ciphertext || tag(16)), so
    the decoded output is at least 29 bytes and the string is valid base64.
    """
    if len(value) < 40:
        return False
    try:
        decoded = base64.b64decode(value, validate=True)
        return len(decoded) >= 29
    except Exception:
        return False


async def scan_tenant(tenant_id: str, *, dry_run: bool = False) -> dict:
    """Scan a tenant's documents for unencrypted fields.

    Reads directly from Cosmos containers (no repository hooks) and
    checks whether sensitive fields appear to be encrypted.

    Returns:
        Dict with: collections_scanned, documents_scanned,
        unencrypted_found, unencrypted_details.
    """
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    cosmos = get_cosmos_manager()
    stats = {
        "collections_scanned": 0,
        "documents_scanned": 0,
        "unencrypted_found": 0,
        "unencrypted_details": [],
    }

    for collection_name, fields in ENCRYPTED_COLLECTIONS.items():
        container = cosmos.get_container(collection_name)
        stats["collections_scanned"] += 1

        async for doc in container.query_items(
            query="SELECT * FROM c WHERE c.tenant_id = @tid",
            parameters=[{"name": "@tid", "value": tenant_id}],
            partition_key=tenant_id,
        ):
            doc_id = doc.get("id", "unknown")
            stats["documents_scanned"] += 1
            doc_has_plaintext = False

            for field in fields:
                value = doc.get(field)
                if value is None or value == "":
                    continue
                if not isinstance(value, str):
                    continue
                if not _looks_encrypted(value):
                    doc_has_plaintext = True
                    stats["unencrypted_details"].append({
                        "collection": collection_name,
                        "doc_id": doc_id,
                        "field": field,
                        "value_preview": value[:30] + "..." if len(value) > 30 else value,
                    })

            if doc_has_plaintext:
                stats["unencrypted_found"] += 1

        logger.info(
            "Scanned %s for tenant %s", collection_name, tenant_id,
        )

    if dry_run:
        logger.info("[DRY RUN] Scan results for tenant %s: %s", tenant_id, {
            k: v for k, v in stats.items() if k != "unencrypted_details"
        })
    else:
        logger.info("Scan results for tenant %s: %d documents, %d unencrypted",
                     tenant_id, stats["documents_scanned"], stats["unencrypted_found"])

    if stats["unencrypted_found"] > 0:
        for detail in stats["unencrypted_details"]:
            logger.warning(
                "  PLAINTEXT: %s/%s field=%s preview=%s",
                detail["collection"], detail["doc_id"],
                detail["field"], detail["value_preview"],
            )

    return stats


async def run_scan(*, dry_run: bool = False, tenant_id: str | None = None) -> None:
    """Run encryption monitoring scan."""
    from src.multi_tenant.repositories.tenant import TenantRepository

    logger.info(
        "Starting encryption monitor (dry_run=%s, tenant=%s)",
        dry_run, tenant_id or "ALL",
    )
    start = time.monotonic()

    if tenant_id:
        results = await scan_tenant(tenant_id, dry_run=dry_run)
        if results["unencrypted_found"] > 0:
            logger.warning(
                "ALERT: %d unencrypted documents found for tenant %s",
                results["unencrypted_found"], tenant_id,
            )
    else:
        # Iterate all active tenants
        repo = TenantRepository()
        tenant_ids = await repo.list_active_tenant_ids()
        logger.info("Found %d active tenants to scan", len(tenant_ids))

        total_unencrypted = 0
        total_docs = 0
        for i, tid in enumerate(tenant_ids, 1):
            logger.info("--- Scanning tenant %d/%d: %s ---", i, len(tenant_ids), tid)
            results = await scan_tenant(tid, dry_run=dry_run)
            total_unencrypted += results["unencrypted_found"]
            total_docs += results["documents_scanned"]

        logger.info(
            "Full scan complete: %d documents scanned, %d unencrypted across %d tenants",
            total_docs, total_unencrypted, len(tenant_ids),
        )
        if total_unencrypted > 0:
            logger.warning("ALERT: %d unencrypted documents found!", total_unencrypted)

    elapsed = time.monotonic() - start
    logger.info("Encryption monitor complete in %.1f seconds", elapsed)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Scan for unencrypted tenant documents")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tenant", type=str)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(run_scan(dry_run=args.dry_run, tenant_id=args.tenant))


if __name__ == "__main__":
    main()
