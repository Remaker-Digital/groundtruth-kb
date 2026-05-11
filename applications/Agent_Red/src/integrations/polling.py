# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Polling Scheduler & Cursor Management (SPEC-1767).

Background polling scheduler for integrations that use polling or hybrid
sync strategies.  Manages cursor state, adaptive intervals with
exponential backoff, and automatic pause after consecutive failures.

Sync state stored in Cosmos integration_sync_state container:
  - PK: tenant_id
  - id: {tenant_id}:{integration_id}
  - Fields: last_cursor, last_sync_at, sync_status, error_count, etc.

Strategies:
  - incremental: Cursor-based, fetches only new data since last cursor.
  - full: Daily full sweep, ignores cursor.
  - hybrid: Webhook primary + periodic poll for verification/catch-up.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import enum
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_POLL_INTERVAL = 300  # 5 minutes
MAX_BACKOFF_SECONDS = 3600  # 1 hour
MAX_CONSECUTIVE_FAILURES = 5
BASE_BACKOFF_SECONDS = 30


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PollStrategy(str, enum.Enum):
    """Polling strategy for an integration."""

    INCREMENTAL = "incremental"
    FULL = "full"
    HYBRID = "hybrid"


class SyncStatus(str, enum.Enum):
    """Current sync status for a tenant-integration pair."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"  # Paused due to consecutive failures
    ERROR = "error"


# ---------------------------------------------------------------------------
# Sync State
# ---------------------------------------------------------------------------


class SyncState:
    """Per-(tenant, integration) sync state.

    In production, persisted to Cosmos integration_sync_state container.
    """

    __slots__ = (
        "tenant_id",
        "integration_id",
        "last_cursor",
        "last_sync_at",
        "sync_status",
        "error_count",
        "last_error",
        "next_poll_at",
        "poll_interval",
        "strategy",
        "total_syncs",
        "total_items",
    )

    def __init__(
        self,
        tenant_id: str,
        integration_id: str,
        strategy: PollStrategy = PollStrategy.INCREMENTAL,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ) -> None:
        self.tenant_id = tenant_id
        self.integration_id = integration_id
        self.last_cursor: str = ""
        self.last_sync_at: float = 0.0
        self.sync_status = SyncStatus.IDLE
        self.error_count: int = 0
        self.last_error: str = ""
        self.next_poll_at: float = 0.0
        self.poll_interval = poll_interval
        self.strategy = strategy
        self.total_syncs: int = 0
        self.total_items: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": f"{self.tenant_id}:{self.integration_id}",
            "tenant_id": self.tenant_id,
            "integration_id": self.integration_id,
            "last_cursor": self.last_cursor,
            "last_sync_at": self.last_sync_at,
            "sync_status": self.sync_status.value,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "next_poll_at": self.next_poll_at,
            "poll_interval": self.poll_interval,
            "strategy": self.strategy.value,
            "total_syncs": self.total_syncs,
            "total_items": self.total_items,
        }


# ---------------------------------------------------------------------------
# Poll result
# ---------------------------------------------------------------------------


class PollResult:
    """Result from a poll execution."""

    __slots__ = ("items", "new_cursor", "has_more")

    def __init__(
        self,
        items: list[Any] | None = None,
        new_cursor: str = "",
        has_more: bool = False,
    ) -> None:
        self.items = items or []
        self.new_cursor = new_cursor
        self.has_more = has_more


# Poll function type: takes (tenant_id, integration_id, cursor) -> PollResult
PollFunction = Callable[
    [str, str, str], Coroutine[Any, Any, PollResult]
]


# ---------------------------------------------------------------------------
# PollingScheduler
# ---------------------------------------------------------------------------


class PollingScheduler:
    """Background polling scheduler with cursor management.

    Manages asyncio tasks that periodically call poll functions for
    each registered (tenant, integration) pair.

    Usage:
        scheduler = PollingScheduler()

        async def my_poller(tenant_id, integration_id, cursor):
            items = await fetch_new_items(cursor)
            return PollResult(items=items, new_cursor=items[-1].id)

        scheduler.schedule("t-1", "zendesk", my_poller)
        # ... later:
        scheduler.cancel("t-1", "zendesk")
    """

    def __init__(self) -> None:
        self._states: dict[tuple[str, str], SyncState] = {}
        self._poll_fns: dict[tuple[str, str], PollFunction] = {}
        self._tasks: dict[tuple[str, str], asyncio.Task[None]] = {}
        self._on_pause_callbacks: list[
            Callable[[str, str, str], Coroutine[Any, Any, None]]
        ] = []

    def schedule(
        self,
        tenant_id: str,
        integration_id: str,
        poll_fn: PollFunction,
        *,
        strategy: PollStrategy = PollStrategy.INCREMENTAL,
        interval: float = DEFAULT_POLL_INTERVAL,
        initial_cursor: str = "",
    ) -> SyncState:
        """Schedule polling for a tenant-integration pair.

        If already scheduled, cancels the existing task and reschedules.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Integration identifier.
            poll_fn: Async callable that performs the poll.
            strategy: Polling strategy.
            interval: Base poll interval in seconds.
            initial_cursor: Starting cursor value.

        Returns:
            The SyncState for this schedule.
        """
        key = (tenant_id, integration_id)

        # Cancel existing if any
        if key in self._tasks:
            self._tasks[key].cancel()

        state = SyncState(
            tenant_id=tenant_id,
            integration_id=integration_id,
            strategy=strategy,
            poll_interval=interval,
        )
        if initial_cursor:
            state.last_cursor = initial_cursor

        self._states[key] = state
        self._poll_fns[key] = poll_fn

        # Start background task
        task = asyncio.create_task(self._poll_loop(key))
        self._tasks[key] = task
        task.add_done_callback(lambda t: self._tasks.pop(key, None))

        logger.info(
            "Polling scheduled: tenant=%s integration=%s strategy=%s interval=%ds",
            tenant_id,
            integration_id,
            strategy.value,
            interval,
        )
        return state

    def cancel(self, tenant_id: str, integration_id: str) -> bool:
        """Cancel polling for a tenant-integration pair.

        Returns True if a schedule was cancelled.
        """
        key = (tenant_id, integration_id)
        task = self._tasks.pop(key, None)
        if task:
            task.cancel()
            self._poll_fns.pop(key, None)
            state = self._states.get(key)
            if state:
                state.sync_status = SyncStatus.IDLE
            logger.info(
                "Polling cancelled: tenant=%s integration=%s",
                tenant_id,
                integration_id,
            )
            return True
        return False

    def get_state(
        self, tenant_id: str, integration_id: str
    ) -> SyncState | None:
        """Get the current sync state."""
        return self._states.get((tenant_id, integration_id))

    def on_pause(
        self,
        callback: Callable[[str, str, str], Coroutine[Any, Any, None]],
    ) -> None:
        """Register a callback for when polling is paused due to errors.

        Callback receives (tenant_id, integration_id, last_error).
        """
        self._on_pause_callbacks.append(callback)

    async def execute_poll(
        self, tenant_id: str, integration_id: str
    ) -> PollResult | None:
        """Execute a single poll immediately (manual trigger).

        Returns the PollResult, or None if not scheduled.
        """
        key = (tenant_id, integration_id)
        poll_fn = self._poll_fns.get(key)
        state = self._states.get(key)

        if not poll_fn or not state:
            return None

        return await self._do_poll(key, state, poll_fn)

    # -- Internal -----------------------------------------------------------

    async def _poll_loop(self, key: tuple[str, str]) -> None:
        """Background loop that polls at the configured interval."""
        state = self._states[key]
        poll_fn = self._poll_fns[key]

        while True:
            try:
                # Wait until next poll time
                now = time.time()
                wait_time = max(0, state.next_poll_at - now)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

                if state.sync_status == SyncStatus.PAUSED:
                    # Paused — sleep and recheck
                    await asyncio.sleep(state.poll_interval)
                    continue

                await self._do_poll(key, state, poll_fn)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(
                    "Poll loop error: tenant=%s integration=%s error=%s",
                    key[0],
                    key[1],
                    exc,
                )
                await asyncio.sleep(state.poll_interval)

    async def _do_poll(
        self,
        key: tuple[str, str],
        state: SyncState,
        poll_fn: PollFunction,
    ) -> PollResult:
        """Execute a single poll and update state."""
        state.sync_status = SyncStatus.RUNNING

        try:
            # For full strategy, don't pass cursor
            cursor = (
                "" if state.strategy == PollStrategy.FULL else state.last_cursor
            )
            result = await poll_fn(key[0], key[1], cursor)

            # Success — update state
            state.last_sync_at = time.time()
            state.error_count = 0
            state.last_error = ""
            state.total_syncs += 1
            state.total_items += len(result.items)
            state.sync_status = SyncStatus.IDLE

            # Update cursor if incremental/hybrid
            if result.new_cursor and state.strategy != PollStrategy.FULL:
                state.last_cursor = result.new_cursor

            # Schedule next poll at base interval
            state.next_poll_at = time.time() + state.poll_interval

            logger.debug(
                "Poll success: tenant=%s integration=%s items=%d cursor=%s",
                key[0],
                key[1],
                len(result.items),
                result.new_cursor or "(none)",
            )
            return result

        except Exception as exc:
            state.error_count += 1
            state.last_error = str(exc)

            if state.error_count >= MAX_CONSECUTIVE_FAILURES:
                # Pause after too many failures
                state.sync_status = SyncStatus.PAUSED
                logger.error(
                    "Polling PAUSED after %d failures: "
                    "tenant=%s integration=%s error=%s",
                    state.error_count,
                    key[0],
                    key[1],
                    exc,
                )
                # Notify callbacks
                for cb in self._on_pause_callbacks:
                    try:
                        await cb(key[0], key[1], str(exc))
                    except Exception as cb_exc:
                        logger.warning("Pause callback error: %s", cb_exc)
            else:
                state.sync_status = SyncStatus.ERROR
                # Exponential backoff
                backoff = min(
                    BASE_BACKOFF_SECONDS * (2 ** (state.error_count - 1)),
                    MAX_BACKOFF_SECONDS,
                )
                state.next_poll_at = time.time() + backoff
                logger.warning(
                    "Poll failed (attempt %d/%d): tenant=%s integration=%s "
                    "backoff=%ds error=%s",
                    state.error_count,
                    MAX_CONSECUTIVE_FAILURES,
                    key[0],
                    key[1],
                    backoff,
                    exc,
                )

            raise

    def resume(self, tenant_id: str, integration_id: str) -> bool:
        """Resume a paused poll schedule.

        Resets error count and sets status back to IDLE.
        Returns True if the schedule was paused and is now resumed.
        """
        key = (tenant_id, integration_id)
        state = self._states.get(key)
        if not state or state.sync_status != SyncStatus.PAUSED:
            return False

        state.error_count = 0
        state.last_error = ""
        state.sync_status = SyncStatus.IDLE
        state.next_poll_at = time.time()

        logger.info(
            "Polling resumed: tenant=%s integration=%s",
            tenant_id,
            integration_id,
        )
        return True

    # -- Stats / cleanup ----------------------------------------------------

    @property
    def active_schedules(self) -> int:
        """Number of active poll schedules."""
        return len(self._tasks)

    def list_states(
        self, tenant_id: str | None = None
    ) -> list[dict[str, Any]]:
        """List sync states, optionally filtered by tenant."""
        results = []
        for state in self._states.values():
            if tenant_id and state.tenant_id != tenant_id:
                continue
            results.append(state.to_dict())
        return results

    async def cancel_all(self) -> int:
        """Cancel all polling tasks. Returns count cancelled."""
        count = len(self._tasks)
        for task in list(self._tasks.values()):
            task.cancel()
        self._tasks.clear()
        self._poll_fns.clear()
        return count
