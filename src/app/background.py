"""Background tasks for Agent Red Customer Experience.

- Idle conversation scanner — closes conversations exceeding 30-min idle timeout.
- SLA snapshot loop — persists hourly SLA snapshots and daily rollups (C-2).
- Alert evaluation loop — evaluates enabled alert rules every 5 minutes (RB-4).
- Ingestion processor — processes pending storefront ingestion jobs (KA-1).
- Conversation archival sweep — auto-archives oldest resolved conversations when
  a tenant exceeds 1,000 non-archived conversations (WI-A7).
- Trial expiry scanner — transitions expired trial tenants from ACTIVE to
  TRIAL_EXPIRED status (WI-D1).
- Trial expiry warning emails — sends warning emails at 7, 3, and 1 day(s)
  before trial end (WI-E3).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging

from datetime import datetime, timedelta, timezone

from fastapi import FastAPI

logger = logging.getLogger(__name__)

_idle_scanner_task: asyncio.Task[None] | None = None
_sla_snapshot_task: asyncio.Task[None] | None = None
_alert_eval_task: asyncio.Task[None] | None = None
_ingestion_processor_task: asyncio.Task[None] | None = None
_archival_sweep_task: asyncio.Task[None] | None = None
_trial_scanner_task: asyncio.Task[None] | None = None


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


# ---------------------------------------------------------------------------
# Ingestion processor loop (KA-1: storefront ingestion)
# ---------------------------------------------------------------------------

# Poll interval: 30 seconds
_INGESTION_POLL_INTERVAL = 30
# Orphan detection: jobs running > 30 minutes are marked failed
_INGESTION_ORPHAN_MINUTES = 30


async def _recover_orphaned_jobs() -> None:
    """Mark running ingestion jobs >30 minutes as failed (orphan recovery).

    Called once during startup to handle jobs left in 'running' state
    after a container restart.
    """
    try:
        from src.multi_tenant.storefront_ingestion import IngestionJobRepository
        from src.multi_tenant.cosmos_schema import IngestionJobStatus

        repo = IngestionJobRepository()
        cutoff = (
            datetime.now(timezone.utc) - timedelta(minutes=_INGESTION_ORPHAN_MINUTES)
        ).isoformat()

        orphans = await repo.get_orphaned_running(cutoff)
        for job in orphans:
            try:
                now = datetime.now(timezone.utc).isoformat()
                await repo.patch(
                    job["tenant_id"],
                    job["id"],
                    [
                        {"op": "set", "path": "/status", "value": IngestionJobStatus.FAILED.value},
                        {"op": "set", "path": "/completed_at", "value": now},
                        {"op": "set", "path": "/error_message", "value": "Orphaned job recovered after container restart"},
                    ],
                )
                logger.info(
                    "Recovered orphaned ingestion job %s (tenant %s)",
                    job["id"][:8], job["tenant_id"][:8],
                )
            except Exception:
                logger.warning("Failed to recover orphaned job %s", job.get("id", "?")[:8], exc_info=True)

        if orphans:
            logger.info("Ingestion orphan recovery: marked %d jobs as failed", len(orphans))
    except Exception:
        logger.warning("Ingestion orphan recovery failed (non-fatal)", exc_info=True)


async def _ingestion_processor_loop() -> None:
    """Periodic background task that processes pending ingestion jobs.

    Runs every 30 seconds. Picks up one pending job at a time and
    executes it via StorefrontIngestionService.process_job().
    """
    # Wait 45 seconds after startup before first poll
    await asyncio.sleep(45)

    while True:
        try:
            from src.multi_tenant.storefront_ingestion import (
                IngestionJobRepository,
                StorefrontIngestionService,
            )

            repo = IngestionJobRepository()
            pending = await repo.get_pending_jobs(limit=1)

            if pending:
                job = pending[0]
                service = StorefrontIngestionService()
                await service.process_job(job["id"], job["tenant_id"])

        except RuntimeError:
            # Service not configured yet — skip this cycle
            pass
        except Exception:
            logger.warning("Ingestion processor cycle failed", exc_info=True)

        # Periodic orphan recovery — catch RUNNING jobs stuck >30 min
        # (supplements the one-time startup recovery in _recover_orphaned_jobs)
        try:
            from src.multi_tenant.storefront_ingestion import IngestionJobRepository
            from src.multi_tenant.cosmos_schema import IngestionJobStatus

            repo = IngestionJobRepository()
            cutoff = (
                datetime.now(timezone.utc)
                - timedelta(minutes=_INGESTION_ORPHAN_MINUTES)
            ).isoformat()
            orphans = await repo.get_orphaned_running(cutoff)
            for job in orphans:
                try:
                    now = datetime.now(timezone.utc).isoformat()
                    await repo.patch(
                        job["tenant_id"],
                        job["id"],
                        [
                            {
                                "op": "set",
                                "path": "/status",
                                "value": IngestionJobStatus.PENDING.value,
                            },
                            {"op": "set", "path": "/started_at", "value": None},
                            {"op": "set", "path": "/error_message", "value": None},
                        ],
                    )
                    logger.warning(
                        "Reset stale ingestion job %s to PENDING "
                        "(was RUNNING for >%d min)",
                        job["id"][:8],
                        _INGESTION_ORPHAN_MINUTES,
                    )
                except Exception:
                    logger.warning(
                        "Failed to reset stale job %s",
                        job.get("id", "?")[:8],
                        exc_info=True,
                    )
        except RuntimeError:
            pass  # Service not configured yet
        except Exception:
            logger.debug("Periodic orphan check failed (non-fatal)", exc_info=True)

        # Sleep between polls
        await asyncio.sleep(_INGESTION_POLL_INTERVAL)


async def _startup_ingestion_processor() -> None:
    """Recover orphaned jobs, then start the ingestion processor loop."""
    global _ingestion_processor_task  # noqa: PLW0603
    await _recover_orphaned_jobs()
    _ingestion_processor_task = asyncio.create_task(_ingestion_processor_loop())
    logger.info("Ingestion processor background task started (30s poll interval)")


async def _shutdown_ingestion_processor() -> None:
    """Cancel the ingestion processor background task."""
    global _ingestion_processor_task  # noqa: PLW0603
    if _ingestion_processor_task and not _ingestion_processor_task.done():
        _ingestion_processor_task.cancel()
        try:
            await _ingestion_processor_task
        except asyncio.CancelledError:
            pass
        logger.info("Ingestion processor background task stopped")
    _ingestion_processor_task = None


def register_ingestion_processor(app: FastAPI) -> None:
    """Register ingestion processor startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_ingestion_processor)
    app.on_event("shutdown")(_shutdown_ingestion_processor)


# ---------------------------------------------------------------------------
# Conversation archival sweep (WI-A7: auto-archival at 1,000 limit)
# ---------------------------------------------------------------------------

# Sweep interval: 1 hour (3600 seconds)
_ARCHIVAL_SWEEP_INTERVAL = 3600
# Maximum non-archived conversations per tenant before auto-archival kicks in
_MAX_NON_ARCHIVED = 1000
# Number of conversations to archive per sweep iteration (batch size)
_ARCHIVAL_BATCH_SIZE = 100


async def _archival_sweep_loop() -> None:
    """Periodic background task that auto-archives old conversations.

    Runs every hour. For each active tenant, checks whether non-archived
    conversation count exceeds the limit (1,000). If so, archives the
    oldest resolved/timed-out conversations until the count is within
    the limit.
    """
    from src.multi_tenant.repositories.conversation import ConversationRepository
    from src.multi_tenant.repository import TenantRepository

    # Wait 180 seconds after startup before first sweep
    await asyncio.sleep(180)

    while True:
        try:
            tenant_repo = TenantRepository()
            conv_repo = ConversationRepository()
            tenant_ids = await tenant_repo.list_active_tenant_ids()
            total_archived = 0

            for tid in tenant_ids:
                try:
                    count = await conv_repo.count_non_archived(tid)
                    if count <= _MAX_NON_ARCHIVED:
                        continue

                    excess = count - _MAX_NON_ARCHIVED
                    to_archive = min(excess, _ARCHIVAL_BATCH_SIZE)

                    candidates = await conv_repo.list_oldest_archivable(
                        tid, limit=to_archive,
                    )

                    now = datetime.now(timezone.utc).isoformat()
                    archived_count = 0
                    for conv in candidates:
                        try:
                            doc_id = conv.get("id") or conv.get("conversation_id")
                            if not doc_id:
                                continue
                            await conv_repo.patch(
                                tenant_id=tid,
                                document_id=doc_id,
                                operations=[
                                    {"op": "set", "path": "/archived_at", "value": now},
                                ],
                            )
                            archived_count += 1
                        except Exception:
                            logger.debug(
                                "Auto-archive failed for conv %s tenant %s",
                                conv.get("conversation_id", "?")[:8],
                                tid[:8],
                                exc_info=True,
                            )

                    if archived_count > 0:
                        logger.info(
                            "Auto-archival: archived %d conversations for tenant %s "
                            "(was %d, limit %d)",
                            archived_count, tid[:8], count, _MAX_NON_ARCHIVED,
                        )
                        total_archived += archived_count

                except Exception:
                    logger.debug(
                        "Archival sweep failed for tenant %s",
                        tid[:8], exc_info=True,
                    )

            if total_archived > 0:
                logger.info(
                    "Archival sweep: archived %d conversations across %d tenants",
                    total_archived, len(tenant_ids),
                )
        except Exception:
            logger.debug("Archival sweep cycle failed", exc_info=True)

        # Sleep 1 hour between sweeps
        await asyncio.sleep(_ARCHIVAL_SWEEP_INTERVAL)


async def _startup_archival_sweep() -> None:
    """Start the conversation archival sweep background task."""
    global _archival_sweep_task  # noqa: PLW0603
    _archival_sweep_task = asyncio.create_task(_archival_sweep_loop())
    logger.info("Conversation archival sweep started (1-hour interval, limit %d)", _MAX_NON_ARCHIVED)


async def _shutdown_archival_sweep() -> None:
    """Cancel the conversation archival sweep background task."""
    global _archival_sweep_task  # noqa: PLW0603
    if _archival_sweep_task and not _archival_sweep_task.done():
        _archival_sweep_task.cancel()
        try:
            await _archival_sweep_task
        except asyncio.CancelledError:
            pass
        logger.info("Conversation archival sweep stopped")
    _archival_sweep_task = None


def register_archival_sweep(app: FastAPI) -> None:
    """Register conversation archival sweep startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_archival_sweep)
    app.on_event("shutdown")(_shutdown_archival_sweep)


# ---------------------------------------------------------------------------
# Trial expiry scanner (WI-D1)
# ---------------------------------------------------------------------------

# Scan interval — every 1 hour
_TRIAL_SCAN_INTERVAL = 3600
# Startup delay before first scan — 120 seconds
_TRIAL_SCAN_STARTUP_DELAY = 120


async def _trial_scanner_loop() -> None:
    """Periodic background task that expires overdue trial tenants.

    Runs every hour. Queries for active trial tenants whose
    trial_expires_at timestamp is in the past, then transitions
    them to TRIAL_EXPIRED status.

    Middleware already rejects requests from expired trials
    (middleware._check_trial_expiry), but this scanner ensures the
    tenant status is updated proactively — important for accurate
    dashboard metrics, billing reports, and preventing stale data.
    """
    from src.multi_tenant.repository import TenantRepository

    # Wait before first scan to allow startup to complete
    await asyncio.sleep(_TRIAL_SCAN_STARTUP_DELAY)

    while True:
        try:
            tenant_repo = TenantRepository()
            expired_trials = await tenant_repo.list_expired_trials()
            expired_count = 0

            for tenant_doc in expired_trials:
                tid = tenant_doc.get("tenant_id")
                if not tid:
                    continue

                try:
                    now_iso = datetime.now(timezone.utc).isoformat()
                    await tenant_repo.patch(
                        tenant_id=tid,
                        document_id=tid,
                        operations=[
                            {"op": "set", "path": "/status", "value": "trial_expired"},
                            {"op": "set", "path": "/updated_at", "value": now_iso},
                            {"op": "set", "path": "/trial_expired_at", "value": now_iso},
                        ],
                    )
                    expired_count += 1
                    logger.info(
                        "Trial expired: tenant=%s trial_expires_at=%s",
                        tid[:8],
                        tenant_doc.get("trial_expires_at", "?"),
                    )
                except Exception:
                    logger.debug(
                        "Trial expiry failed for tenant %s",
                        tid[:8],
                        exc_info=True,
                    )

            if expired_count > 0:
                logger.info(
                    "Trial scanner: expired %d trial tenants",
                    expired_count,
                )
        except Exception:
            logger.debug("Trial scanner cycle failed", exc_info=True)

        await asyncio.sleep(_TRIAL_SCAN_INTERVAL)


async def _startup_trial_scanner() -> None:
    """Start the trial expiry scanner background task."""
    global _trial_scanner_task  # noqa: PLW0603
    _trial_scanner_task = asyncio.create_task(_trial_scanner_loop())
    logger.info("Trial expiry scanner started (1-hour interval)")


async def _shutdown_trial_scanner() -> None:
    """Cancel the trial expiry scanner background task."""
    global _trial_scanner_task  # noqa: PLW0603
    if _trial_scanner_task and not _trial_scanner_task.done():
        _trial_scanner_task.cancel()
        try:
            await _trial_scanner_task
        except asyncio.CancelledError:
            pass
        logger.info("Trial expiry scanner stopped")
    _trial_scanner_task = None


def register_trial_scanner(app: FastAPI) -> None:
    """Register trial expiry scanner startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_trial_scanner)
    app.on_event("shutdown")(_shutdown_trial_scanner)


# ---------------------------------------------------------------------------
# Trial expiry warning emails (WI-E3)
# ---------------------------------------------------------------------------

# Warning tiers: days before expiry → warning label
_WARNING_TIERS = [
    (7, "7d"),
    (3, "3d"),
    (1, "1d"),
]

# Scan interval — every 12 hours (twice daily covers daily granularity)
_WARNING_SCAN_INTERVAL = 43200
# Startup delay — 180 seconds (after trial scanner)
_WARNING_SCAN_STARTUP_DELAY = 180

_trial_warning_task: asyncio.Task | None = None


async def _trial_warning_loop() -> None:
    """Periodic background task that sends trial expiry warning emails.

    Runs every 12 hours. For each warning tier (7d, 3d, 1d), queries
    for active trial tenants expiring within that window, checks the
    trial_warnings_sent field for deduplication, sends the email,
    and patches the sent marker.
    """
    from src.multi_tenant.repository import TenantRepository

    await asyncio.sleep(_WARNING_SCAN_STARTUP_DELAY)

    while True:
        try:
            tenant_repo = TenantRepository()
            warnings_sent = 0

            for days, tier_label in _WARNING_TIERS:
                within_iso = (
                    datetime.now(timezone.utc) + timedelta(days=days)
                ).isoformat()

                try:
                    expiring = await tenant_repo.list_expiring_trials(within_iso)
                except Exception:
                    logger.debug(
                        "Trial warning query failed for tier %s",
                        tier_label,
                        exc_info=True,
                    )
                    continue

                for tenant_doc in expiring:
                    tid = tenant_doc.get("tenant_id")
                    email = tenant_doc.get("customer_email")
                    already_sent = tenant_doc.get("trial_warnings_sent", [])

                    if not tid or not email:
                        continue
                    if tier_label in already_sent:
                        continue

                    try:
                        from src.multi_tenant.trial_expiry_email import (
                            send_trial_expiry_warning,
                        )

                        sent = await send_trial_expiry_warning(
                            to_email=email,
                            tenant_id=tid,
                            warning_tier=tier_label,
                        )

                        if sent:
                            # Mark warning as sent to prevent duplicates
                            new_warnings = already_sent + [tier_label]
                            now_iso = datetime.now(timezone.utc).isoformat()
                            await tenant_repo.patch(
                                tenant_id=tid,
                                document_id=tid,
                                operations=[
                                    {
                                        "op": "set",
                                        "path": "/trial_warnings_sent",
                                        "value": new_warnings,
                                    },
                                    {
                                        "op": "set",
                                        "path": "/updated_at",
                                        "value": now_iso,
                                    },
                                ],
                            )
                            warnings_sent += 1
                    except Exception:
                        logger.debug(
                            "Trial warning failed for tenant %s tier %s",
                            tid[:8],
                            tier_label,
                            exc_info=True,
                        )

            if warnings_sent > 0:
                logger.info(
                    "Trial warning scanner: sent %d expiry warnings",
                    warnings_sent,
                )
        except Exception:
            logger.debug("Trial warning scanner cycle failed", exc_info=True)

        await asyncio.sleep(_WARNING_SCAN_INTERVAL)


async def _startup_trial_warning() -> None:
    """Start the trial expiry warning background task."""
    global _trial_warning_task  # noqa: PLW0603
    _trial_warning_task = asyncio.create_task(_trial_warning_loop())
    logger.info("Trial expiry warning scanner started (12-hour interval)")


async def _shutdown_trial_warning() -> None:
    """Cancel the trial expiry warning background task."""
    global _trial_warning_task  # noqa: PLW0603
    if _trial_warning_task and not _trial_warning_task.done():
        _trial_warning_task.cancel()
        try:
            await _trial_warning_task
        except asyncio.CancelledError:
            pass
        logger.info("Trial expiry warning scanner stopped")
    _trial_warning_task = None


def register_trial_warning(app: FastAPI) -> None:
    """Register trial expiry warning startup/shutdown handlers on the FastAPI app."""
    app.on_event("startup")(_startup_trial_warning)
    app.on_event("shutdown")(_shutdown_trial_warning)
