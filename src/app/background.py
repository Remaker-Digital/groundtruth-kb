"""Background tasks for Agent Red Customer Experience.

- Idle conversation scanner — closes conversations exceeding 30-min idle timeout.
- SLA snapshot loop — persists hourly SLA snapshots and daily rollups (C-2).
- Alert evaluation loop — evaluates enabled alert rules every 5 minutes (RB-4).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging

from datetime import datetime, timezone

from fastapi import FastAPI

logger = logging.getLogger(__name__)

_idle_scanner_task: asyncio.Task[None] | None = None
_sla_snapshot_task: asyncio.Task[None] | None = None
_alert_eval_task: asyncio.Task[None] | None = None


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


# ---------------------------------------------------------------------------
# SLA snapshot loop (C-2: SLA persistence)
# ---------------------------------------------------------------------------

# Snapshot interval: 1 hour (3600 seconds)
_SLA_SNAPSHOT_INTERVAL = 3600
# Hydration: load last 24 hourly snapshots on startup
_SLA_HYDRATION_HOURS = 24
# Daily rollup check: compute once per day at midnight UTC
_last_rollup_date: str | None = None


async def _hydrate_sla_from_cosmos() -> None:
    """Load the most recent hourly snapshots and replay into the SLA monitor.

    Called once during startup to restore continuity after container restarts.
    """
    try:
        from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
        from src.multi_tenant.sla_monitoring import get_sla_monitor

        repo = SLASnapshotRepository()
        snapshots = await repo.get_recent_hourly(hours=_SLA_HYDRATION_HOURS)
        if snapshots:
            monitor = get_sla_monitor()
            injected = monitor.hydrate_from_snapshots(snapshots)
            logger.info(
                "SLA hydration complete: %d snapshots → %d synthetic samples",
                len(snapshots), injected,
            )
        else:
            logger.info("SLA hydration: no snapshots found (first run or empty collection)")
    except Exception:
        logger.warning("SLA hydration failed (non-fatal)", exc_info=True)


async def _maybe_compute_daily_rollup(
    repo: object,
    now_utc: datetime,
) -> None:
    """Compute a daily rollup if we've crossed into a new UTC day."""
    global _last_rollup_date  # noqa: PLW0603

    today = now_utc.strftime("%Y-%m-%d")
    if _last_rollup_date == today:
        return

    # Compute rollup for yesterday
    from datetime import timedelta
    yesterday = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        from src.multi_tenant.sla_monitoring import SLAMonitoringService

        hourly = await repo.get_hourly_for_date(yesterday)  # type: ignore[attr-defined]
        if hourly:
            rollup = SLAMonitoringService.compute_daily_rollup(hourly)
            await repo.save_daily_rollup(  # type: ignore[attr-defined]
                date=yesterday,
                platform_metrics=rollup["platform"],
                per_tenant=rollup["per_tenant"],
            )
            logger.info(
                "SLA daily rollup saved for %s (%d hourly snapshots)",
                yesterday, len(hourly),
            )
        else:
            logger.debug("No hourly snapshots for %s — skipping daily rollup", yesterday)
    except Exception:
        logger.warning("SLA daily rollup failed for %s", yesterday, exc_info=True)

    _last_rollup_date = today


async def _sla_snapshot_loop() -> None:
    """Periodic background task that persists SLA snapshots every hour.

    Also triggers daily rollup computation at the start of each new UTC day.
    """
    from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
    from src.multi_tenant.sla_monitoring import get_sla_monitor

    # Wait 120 seconds after startup to allow metrics to accumulate
    await asyncio.sleep(120)

    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            monitor = get_sla_monitor()
            repo = SLASnapshotRepository()

            # 1. Persist hourly snapshot
            snapshot_data = monitor.create_snapshot_data()
            period_end = now_utc
            period_start = now_utc.replace(
                minute=0, second=0, microsecond=0,
            )

            await repo.save_hourly_snapshot(
                timestamp=now_utc,
                period_start=period_start,
                period_end=period_end,
                platform_metrics=snapshot_data["platform"],
                per_tenant=snapshot_data["per_tenant"],
            )
            logger.info(
                "SLA hourly snapshot saved: %d requests, %.1f%% uptime",
                snapshot_data["platform"]["total_requests"],
                snapshot_data["platform"]["uptime_pct"],
            )

            # 2. Check for daily rollup
            await _maybe_compute_daily_rollup(repo, now_utc)

        except Exception:
            logger.warning("SLA snapshot cycle failed (non-fatal)", exc_info=True)

        # Sleep 1 hour
        await asyncio.sleep(_SLA_SNAPSHOT_INTERVAL)


async def _startup_sla_snapshots() -> None:
    """Hydrate SLA data from Cosmos, then start the snapshot loop."""
    global _sla_snapshot_task  # noqa: PLW0603
    await _hydrate_sla_from_cosmos()
    _sla_snapshot_task = asyncio.create_task(_sla_snapshot_loop())
    logger.info("SLA snapshot background task started (1-hour interval)")


async def _shutdown_sla_snapshots() -> None:
    """Cancel the SLA snapshot background task."""
    global _sla_snapshot_task  # noqa: PLW0603
    if _sla_snapshot_task and not _sla_snapshot_task.done():
        _sla_snapshot_task.cancel()
        try:
            await _sla_snapshot_task
        except asyncio.CancelledError:
            pass
        logger.info("SLA snapshot background task stopped")
    _sla_snapshot_task = None


def register_sla_snapshots(app: FastAPI) -> None:
    """Register SLA snapshot startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_sla_snapshots)
    app.on_event("shutdown")(_shutdown_sla_snapshots)


# ---------------------------------------------------------------------------
# Alert evaluation loop (RB-4: alerting)
# ---------------------------------------------------------------------------

# Evaluation interval: 5 minutes (300 seconds)
_ALERT_EVAL_INTERVAL = 300


async def _alert_evaluation_loop() -> None:
    """Periodic background task that evaluates enabled alert rules.

    Runs every 5 minutes. Imports the AlertEngine singleton and calls
    evaluate_all(), which checks each enabled rule against its metric
    collector and fires alerts when conditions are met.
    """
    # Wait 90 seconds after startup before first evaluation
    await asyncio.sleep(90)

    while True:
        try:
            from src.multi_tenant.alert_engine import get_alert_engine

            engine = get_alert_engine()
            result = await engine.evaluate_all()

            if result.get("alerts_fired", 0) > 0:
                logger.info(
                    "Alert evaluation: %d rules evaluated, %d alerts fired, "
                    "%d skipped (cooldown), %d errors",
                    result["rules_evaluated"],
                    result["alerts_fired"],
                    result["skipped_cooldown"],
                    result["errors"],
                )
            else:
                logger.debug(
                    "Alert evaluation: %d rules evaluated, 0 fired",
                    result.get("rules_evaluated", 0),
                )
        except RuntimeError:
            # AlertEngine not configured yet — skip this cycle
            pass
        except Exception:
            logger.debug("Alert evaluation cycle failed", exc_info=True)

        # Sleep 5 minutes between evaluations
        await asyncio.sleep(_ALERT_EVAL_INTERVAL)


async def _startup_alert_evaluation() -> None:
    """Start the alert evaluation background task."""
    global _alert_eval_task  # noqa: PLW0603
    _alert_eval_task = asyncio.create_task(_alert_evaluation_loop())
    logger.info("Alert evaluation background task started (5-min interval)")


async def _shutdown_alert_evaluation() -> None:
    """Cancel the alert evaluation background task."""
    global _alert_eval_task  # noqa: PLW0603
    if _alert_eval_task and not _alert_eval_task.done():
        _alert_eval_task.cancel()
        try:
            await _alert_eval_task
        except asyncio.CancelledError:
            pass
        logger.info("Alert evaluation background task stopped")
    _alert_eval_task = None


def register_alert_evaluation(app: FastAPI) -> None:
    """Register alert evaluation startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_alert_evaluation)
    app.on_event("shutdown")(_shutdown_alert_evaluation)
