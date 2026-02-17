"""Background tasks for Agent Red Customer Experience.

Idle conversation scanner — periodic background task that closes
conversations exceeding the 30-minute idle timeout.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

_idle_scanner_task: asyncio.Task[None] | None = None


async def _idle_scanner_loop() -> None:
    """Periodic background task that closes idle conversations.

    Runs every 5 minutes. For each active tenant, calls
    ConversationMeter.scan_idle_conversations() to find and close
    conversations that have exceeded the 30-minute idle timeout.
    """
    from src.multi_tenant.conversation_meter import get_conversation_meter
    from src.multi_tenant.repository import TenantRepository

    # Wait 60 seconds after startup before first scan
    await asyncio.sleep(60)

    while True:
        try:
            meter = get_conversation_meter()
            tenant_repo = TenantRepository()
            tenant_ids = await tenant_repo.list_active_tenant_ids()
            total_closed = 0
            for tid in tenant_ids:
                try:
                    results = await meter.scan_idle_conversations(tid)
                    total_closed += len(results)
                except Exception:
                    logger.debug("Idle scan failed for tenant %s", tid[:8], exc_info=True)
            if total_closed > 0:
                logger.info("Idle scanner: closed %d conversations across %d tenants", total_closed, len(tenant_ids))
        except RuntimeError:
            # ConversationMeter not configured yet — skip this cycle
            pass
        except Exception:
            logger.debug("Idle scanner cycle failed", exc_info=True)

        # Sleep 5 minutes between scans
        await asyncio.sleep(300)


async def _startup_idle_scanner() -> None:
    """Start the idle conversation scanner background task."""
    global _idle_scanner_task  # noqa: PLW0603
    _idle_scanner_task = asyncio.create_task(_idle_scanner_loop())
    logger.info("Idle conversation scanner started (5-min interval)")


async def _shutdown_idle_scanner() -> None:
    """Cancel the idle conversation scanner background task."""
    global _idle_scanner_task  # noqa: PLW0603
    if _idle_scanner_task and not _idle_scanner_task.done():
        _idle_scanner_task.cancel()
        try:
            await _idle_scanner_task
        except asyncio.CancelledError:
            pass
        logger.info("Idle conversation scanner stopped")
    _idle_scanner_task = None


def register_idle_scanner(app: FastAPI) -> None:
    """Register idle scanner startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_idle_scanner)
    app.on_event("shutdown")(_shutdown_idle_scanner)
