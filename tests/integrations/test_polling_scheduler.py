"""Tests for Polling Scheduler & Cursor Management (SPEC-1767).

Tests cover: schedule/cancel, cursor management, poll strategies,
exponential backoff, pause after consecutive failures, resume,
manual poll execution, stats.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from src.integrations.polling import (
    BASE_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
    MAX_CONSECUTIVE_FAILURES,
    PollResult,
    PollStrategy,
    PollingScheduler,
    SyncState,
    SyncStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def scheduler() -> PollingScheduler:
    return PollingScheduler()


async def success_poller(
    tenant_id: str, integration_id: str, cursor: str
) -> PollResult:
    """Test poller that returns items with new cursor."""
    items = [{"id": f"item-{cursor or '0'}-1"}, {"id": f"item-{cursor or '0'}-2"}]
    new_cursor = f"cursor-{int(cursor.split('-')[1]) + 1}" if cursor.startswith("cursor-") else "cursor-1"
    return PollResult(items=items, new_cursor=new_cursor)


async def failure_poller(
    tenant_id: str, integration_id: str, cursor: str
) -> PollResult:
    """Test poller that always fails."""
    raise ConnectionError("API unavailable")


# ===================================================================
# SyncState
# ===================================================================


class TestSyncState:
    """SPEC-1767: Sync state model."""

    def test_default_values(self) -> None:
        state = SyncState("t-1", "zendesk")
        assert state.tenant_id == "t-1"
        assert state.integration_id == "zendesk"
        assert state.sync_status == SyncStatus.IDLE
        assert state.error_count == 0
        assert state.last_cursor == ""

    def test_to_dict(self) -> None:
        state = SyncState("t-1", "zendesk", PollStrategy.HYBRID)
        state.last_cursor = "cur-42"
        d = state.to_dict()
        assert d["id"] == "t-1:zendesk"
        assert d["strategy"] == "hybrid"
        assert d["last_cursor"] == "cur-42"


# ===================================================================
# Schedule / Cancel
# ===================================================================


class TestScheduleCancel:
    """SPEC-1767: Schedule and cancel operations."""

    @pytest.mark.asyncio
    async def test_schedule_creates_state(self, scheduler: PollingScheduler) -> None:
        """Scheduling creates a SyncState and starts a task."""
        state = scheduler.schedule("t-1", "zendesk", success_poller, interval=1.0)
        assert state.tenant_id == "t-1"
        assert state.integration_id == "zendesk"
        assert scheduler.active_schedules == 1
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_cancel(self, scheduler: PollingScheduler) -> None:
        """Cancel removes the polling task."""
        scheduler.schedule("t-1", "zendesk", success_poller, interval=1.0)
        result = scheduler.cancel("t-1", "zendesk")
        assert result is True
        assert scheduler.active_schedules == 0

    @pytest.mark.asyncio
    async def test_cancel_nonexistent(self, scheduler: PollingScheduler) -> None:
        """Cancelling a nonexistent schedule returns False."""
        assert scheduler.cancel("t-1", "nonexistent") is False

    @pytest.mark.asyncio
    async def test_reschedule_replaces(self, scheduler: PollingScheduler) -> None:
        """Rescheduling the same pair replaces the existing task."""
        scheduler.schedule("t-1", "zendesk", success_poller, interval=1.0)
        scheduler.schedule("t-1", "zendesk", success_poller, interval=2.0)
        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.poll_interval == 2.0
        assert scheduler.active_schedules == 1
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_initial_cursor(self, scheduler: PollingScheduler) -> None:
        """Initial cursor is set on state."""
        state = scheduler.schedule(
            "t-1", "zendesk", success_poller, initial_cursor="start-here"
        )
        assert state.last_cursor == "start-here"
        scheduler.cancel("t-1", "zendesk")


# ===================================================================
# Poll Execution
# ===================================================================


class TestPollExecution:
    """SPEC-1767: Manual poll execution and cursor updates."""

    @pytest.mark.asyncio
    async def test_execute_poll_success(self, scheduler: PollingScheduler) -> None:
        """Manual poll returns items and updates cursor."""
        scheduler.schedule(
            "t-1", "zendesk", success_poller,
            interval=999,  # Won't auto-poll during test
            initial_cursor="cursor-0",
        )
        result = await scheduler.execute_poll("t-1", "zendesk")
        assert result is not None
        assert len(result.items) == 2

        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.last_cursor == "cursor-1"
        assert state.total_syncs == 1
        assert state.total_items == 2
        assert state.sync_status == SyncStatus.IDLE
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_execute_poll_nonexistent(self, scheduler: PollingScheduler) -> None:
        """Polling a nonexistent schedule returns None."""
        result = await scheduler.execute_poll("t-1", "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_full_strategy_ignores_cursor(self, scheduler: PollingScheduler) -> None:
        """Full strategy does not pass cursor to poll function."""
        received_cursors: list[str] = []

        async def tracking_poller(tid: str, iid: str, cursor: str) -> PollResult:
            received_cursors.append(cursor)
            return PollResult(items=[1], new_cursor="ignored")

        scheduler.schedule(
            "t-1", "zendesk", tracking_poller,
            strategy=PollStrategy.FULL,
            initial_cursor="old-cursor",
        )
        await scheduler.execute_poll("t-1", "zendesk")
        assert received_cursors == [""]  # Cursor not passed
        scheduler.cancel("t-1", "zendesk")


# ===================================================================
# Error Handling & Backoff
# ===================================================================


class TestErrorHandling:
    """SPEC-1767: Exponential backoff and pause after failures."""

    @pytest.mark.asyncio
    async def test_single_failure_sets_error(self, scheduler: PollingScheduler) -> None:
        """Single failure sets ERROR status with backoff."""
        scheduler.schedule("t-1", "zendesk", failure_poller, interval=999)
        with pytest.raises(ConnectionError):
            await scheduler.execute_poll("t-1", "zendesk")

        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.error_count == 1
        assert state.sync_status == SyncStatus.ERROR
        assert state.last_error == "API unavailable"
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_consecutive_failures_pause(self, scheduler: PollingScheduler) -> None:
        """After MAX_CONSECUTIVE_FAILURES, status is PAUSED."""
        scheduler.schedule("t-1", "zendesk", failure_poller, interval=999)

        for _ in range(MAX_CONSECUTIVE_FAILURES):
            with pytest.raises(ConnectionError):
                await scheduler.execute_poll("t-1", "zendesk")

        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.sync_status == SyncStatus.PAUSED
        assert state.error_count == MAX_CONSECUTIVE_FAILURES
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_pause_callback(self, scheduler: PollingScheduler) -> None:
        """Pause callback is invoked when polling is paused."""
        paused_info: list[tuple[str, str, str]] = []

        async def on_pause(tid: str, iid: str, err: str) -> None:
            paused_info.append((tid, iid, err))

        scheduler.on_pause(on_pause)
        scheduler.schedule("t-1", "zendesk", failure_poller, interval=999)

        for _ in range(MAX_CONSECUTIVE_FAILURES):
            with pytest.raises(ConnectionError):
                await scheduler.execute_poll("t-1", "zendesk")

        assert len(paused_info) == 1
        assert paused_info[0][0] == "t-1"
        assert paused_info[0][1] == "zendesk"
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_success_resets_error_count(self, scheduler: PollingScheduler) -> None:
        """Successful poll resets error count."""
        call_count = 0

        async def flaky_poller(tid: str, iid: str, cursor: str) -> PollResult:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("intermittent")
            return PollResult(items=[1])

        scheduler.schedule("t-1", "zendesk", flaky_poller, interval=999)

        # Two failures
        for _ in range(2):
            with pytest.raises(ConnectionError):
                await scheduler.execute_poll("t-1", "zendesk")

        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.error_count == 2

        # Now success
        await scheduler.execute_poll("t-1", "zendesk")
        assert state.error_count == 0
        assert state.sync_status == SyncStatus.IDLE
        scheduler.cancel("t-1", "zendesk")


# ===================================================================
# Resume
# ===================================================================


class TestResume:
    """SPEC-1767: Resume paused schedules."""

    @pytest.mark.asyncio
    async def test_resume_paused(self, scheduler: PollingScheduler) -> None:
        """Paused schedule can be resumed."""
        scheduler.schedule("t-1", "zendesk", failure_poller, interval=999)
        for _ in range(MAX_CONSECUTIVE_FAILURES):
            with pytest.raises(ConnectionError):
                await scheduler.execute_poll("t-1", "zendesk")

        state = scheduler.get_state("t-1", "zendesk")
        assert state is not None
        assert state.sync_status == SyncStatus.PAUSED

        result = scheduler.resume("t-1", "zendesk")
        assert result is True
        assert state.sync_status == SyncStatus.IDLE
        assert state.error_count == 0
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_resume_not_paused(self, scheduler: PollingScheduler) -> None:
        """Resume on non-paused schedule returns False."""
        scheduler.schedule("t-1", "zendesk", success_poller, interval=999)
        assert scheduler.resume("t-1", "zendesk") is False
        scheduler.cancel("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_resume_nonexistent(self, scheduler: PollingScheduler) -> None:
        """Resume on nonexistent schedule returns False."""
        assert scheduler.resume("t-1", "nonexistent") is False


# ===================================================================
# List States / Cancel All
# ===================================================================


class TestListAndCleanup:
    """SPEC-1767: State listing and cleanup."""

    @pytest.mark.asyncio
    async def test_list_states(self, scheduler: PollingScheduler) -> None:
        scheduler.schedule("t-1", "zendesk", success_poller, interval=999)
        scheduler.schedule("t-1", "slack", success_poller, interval=999)
        scheduler.schedule("t-2", "zendesk", success_poller, interval=999)

        all_states = scheduler.list_states()
        assert len(all_states) == 3

        t1_states = scheduler.list_states("t-1")
        assert len(t1_states) == 2

        await scheduler.cancel_all()

    @pytest.mark.asyncio
    async def test_cancel_all(self, scheduler: PollingScheduler) -> None:
        scheduler.schedule("t-1", "zendesk", success_poller, interval=999)
        scheduler.schedule("t-2", "slack", success_poller, interval=999)
        count = await scheduler.cancel_all()
        assert count == 2
        assert scheduler.active_schedules == 0


# ===================================================================
# PollResult
# ===================================================================


class TestPollResult:
    """SPEC-1767: PollResult model."""

    def test_defaults(self) -> None:
        r = PollResult()
        assert r.items == []
        assert r.new_cursor == ""
        assert r.has_more is False

    def test_with_data(self) -> None:
        r = PollResult(items=[1, 2, 3], new_cursor="c-42", has_more=True)
        assert len(r.items) == 3
        assert r.new_cursor == "c-42"
        assert r.has_more is True
