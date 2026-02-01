"""
Scheduled job: Archival pipeline (Cosmos DB → Blob Parquet).

Invoked by Azure Container App Job (cron: daily at 04:00 UTC).
Runs ArchivalPipelineService.run_archival_scan() across all tenants,
then exits with code 0 (success) or 1 (errors encountered).

Usage:
    python -m src.jobs.run_archival

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    """Run archival pipeline and return exit code."""
    from src.multi_tenant.repository import (
        AuditLogRepository,
        ConversationRepository,
        CustomerProfileRepository,
        MemoryVectorRepository,
        TenantRepository,
    )
    from src.multi_tenant.archival_pipeline import ArchivalPipelineService

    logger.info("Archival pipeline job starting")

    # Wire Blob Storage client if connection string available
    blob_client = None
    blob_conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if blob_conn:
        try:
            from azure.storage.blob import BlobServiceClient

            blob_client = BlobServiceClient.from_connection_string(blob_conn)
            logger.info("Azure Blob Storage client connected")
        except Exception:
            logger.warning("Blob Storage client creation failed — running in dry-run mode")

    service = ArchivalPipelineService(
        tenant_repo=TenantRepository(),
        conversation_repo=ConversationRepository(),
        profile_repo=CustomerProfileRepository(),
        vector_repo=MemoryVectorRepository(),
        audit_repo=AuditLogRepository(),
        blob_client=blob_client,
    )

    result = await service.run_archival_scan()

    logger.info(
        "Archival pipeline job complete: tenants=%d archived=%d bytes=%d errors=%d",
        result.tenants_scanned,
        result.documents_archived,
        result.bytes_written,
        result.errors,
    )

    return 1 if result.errors > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
