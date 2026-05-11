# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Scheduled job: Data retention enforcement.

Invoked by Azure Container App Job (cron: daily at 03:00 UTC).
Runs DataRetentionService.enforce_retention() across all tenants,
then exits with code 0 (success) or 1 (errors encountered).

Usage:
    python -m src.jobs.run_retention

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    """Run data retention enforcement and return exit code."""
    from src.multi_tenant.data_retention import DataRetentionService
    from src.multi_tenant.repository import (
        AuditLogRepository,
        ConversationRepository,
        CustomerProfileRepository,
        MemoryVectorRepository,
        TenantRepository,
    )

    logger.info("Data retention job starting")

    service = DataRetentionService(
        tenant_repo=TenantRepository(),
        conversation_repo=ConversationRepository(),
        profile_repo=CustomerProfileRepository(),
        vector_repo=MemoryVectorRepository(),
        audit_repo=AuditLogRepository(),
    )

    result = await service.enforce_retention()

    logger.info(
        "Data retention job complete: tenants=%d deleted=%d errors=%d",
        result.tenants_scanned,
        result.documents_deleted,
        result.errors,
    )

    return 1 if result.errors > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
