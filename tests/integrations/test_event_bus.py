"""Tests for Internal Integration Event Bus (SPEC-1778).

Tests cover:
  - Handler registration (on/off)
  - Async event emission
  - Fire-and-forget error isolation
  - Singleton lifecycle
  - Emit count / error count tracking
  - drain() for testing cleanup
  - emit_sync() from sync context

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio

import pytest

from src.integrations.event_bus import (
    IntegrationEvent,
    IntegrationEventBus,
    IntegrationEventType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_bus():
    """Reset singleton between tests."""
    IntegrationEventBus.reset()
    yield
    IntegrationEventBus.reset()


@pytest.fixture
def bus() -> IntegrationEventBus:
    return IntegrationEventBus.get_instance()


def _make_event(
    event_type: IntegrationEventType = IntegrationEventType.TICKET_CREATED,
    tenant_id: str = "t-1",
    integration_id: str = "zendesk",
    **kwargs,
) -> IntegrationEvent:
    return IntegrationEvent(
        event_type=event_type,
        tenant_id=tenant_id,
        integration_id=integration_id,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_on_registers_handler(self, bus: IntegrationEventBus):
        async def handler(e: IntegrationEvent) -> None:
            pass

        bus.on(IntegrationEventType.TICKET_CREATED, handler)
        assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 1

    def test_on_multiple_handlers(self, bus: IntegrationEventBus):
        async def h1(e: IntegrationEvent) -> None:
            pass

        async def h2(e: IntegrationEvent) -> None:
            pass

        bus.on(IntegrationEventType.TICKET_CREATED, h1)
        bus.on(IntegrationEventType.TICKET_CREATED, h2)
        assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 2
        assert bus.total_handlers == 2

    def test_off_removes_handler(self, bus: IntegrationEventBus):
        async def handler(e: IntegrationEvent) -> None:
            pass

        bus.on(IntegrationEventType.TICKET_CREATED, handler)
        assert bus.off(IntegrationEventType.TICKET_CREATED, handler) is True
        assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 0

    def test_off_returns_false_for_unregistered(self, bus: IntegrationEventBus):
        async def handler(e: IntegrationEvent) -> None:
            pass

        assert bus.off(IntegrationEventType.TICKET_CREATED, handler) is False

    def test_different_event_types_isolated(self, bus: IntegrationEventBus):
        async def h1(e: IntegrationEvent) -> None:
            pass

        async def h2(e: IntegrationEvent) -> None:
            pass

        bus.on(IntegrationEventType.TICKET_CREATED, h1)
        bus.on(IntegrationEventType.SYNC_COMPLETED, h2)
        assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 1
        assert bus.handler_count(IntegrationEventType.SYNC_COMPLETED) == 1
        assert bus.total_handlers == 2


# ---------------------------------------------------------------------------
# Emission
# ---------------------------------------------------------------------------


class TestEmission:
    @pytest.mark.asyncio
    async def test_emit_dispatches_to_handler(self, bus: IntegrationEventBus):
        received: list[IntegrationEvent] = []

        async def handler(e: IntegrationEvent) -> None:
            received.append(e)

        bus.on(IntegrationEventType.TICKET_CREATED, handler)
        event = _make_event()
        count = await bus.emit(event)
        await bus.drain()

        assert count == 1
        assert len(received) == 1
        assert received[0].tenant_id == "t-1"

    @pytest.mark.asyncio
    async def test_emit_returns_zero_for_no_handlers(self, bus: IntegrationEventBus):
        event = _make_event()
        count = await bus.emit(event)
        assert count == 0

    @pytest.mark.asyncio
    async def test_emit_dispatches_to_multiple_handlers(self, bus: IntegrationEventBus):
        results: list[str] = []

        async def h1(e: IntegrationEvent) -> None:
            results.append("h1")

        async def h2(e: IntegrationEvent) -> None:
            results.append("h2")

        bus.on(IntegrationEventType.TICKET_CREATED, h1)
        bus.on(IntegrationEventType.TICKET_CREATED, h2)

        count = await bus.emit(_make_event())
        await bus.drain()

        assert count == 2
        assert sorted(results) == ["h1", "h2"]

    @pytest.mark.asyncio
    async def test_emit_only_dispatches_matching_type(self, bus: IntegrationEventBus):
        ticket_received = []
        sync_received = []

        async def ticket_handler(e: IntegrationEvent) -> None:
            ticket_received.append(e)

        async def sync_handler(e: IntegrationEvent) -> None:
            sync_received.append(e)

        bus.on(IntegrationEventType.TICKET_CREATED, ticket_handler)
        bus.on(IntegrationEventType.SYNC_COMPLETED, sync_handler)

        await bus.emit(_make_event(IntegrationEventType.TICKET_CREATED))
        await bus.drain()

        assert len(ticket_received) == 1
        assert len(sync_received) == 0

    @pytest.mark.asyncio
    async def test_emit_count_tracks(self, bus: IntegrationEventBus):
        async def handler(e: IntegrationEvent) -> None:
            pass

        bus.on(IntegrationEventType.TICKET_CREATED, handler)
        await bus.emit(_make_event())
        await bus.emit(_make_event())
        await bus.drain()

        assert bus.emit_count == 2


# ---------------------------------------------------------------------------
# Error isolation
# ---------------------------------------------------------------------------


class TestErrorIsolation:
    @pytest.mark.asyncio
    async def test_failing_handler_does_not_block_others(self, bus: IntegrationEventBus):
        results: list[str] = []

        async def failing(e: IntegrationEvent) -> None:
            raise ValueError("boom")

        async def succeeding(e: IntegrationEvent) -> None:
            results.append("ok")

        bus.on(IntegrationEventType.TICKET_CREATED, failing)
        bus.on(IntegrationEventType.TICKET_CREATED, succeeding)

        count = await bus.emit(_make_event())
        await bus.drain()

        assert count == 2
        assert results == ["ok"]
        assert bus.error_count == 1

    @pytest.mark.asyncio
    async def test_error_count_increments(self, bus: IntegrationEventBus):
        async def failing(e: IntegrationEvent) -> None:
            raise RuntimeError("fail")

        bus.on(IntegrationEventType.TICKET_CREATED, failing)
        await bus.emit(_make_event())
        await bus.emit(_make_event())
        await bus.drain()

        assert bus.error_count == 2


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_instance_returns_same(self):
        a = IntegrationEventBus.get_instance()
        b = IntegrationEventBus.get_instance()
        assert a is b

    def test_reset_creates_new_instance(self):
        a = IntegrationEventBus.get_instance()
        IntegrationEventBus.reset()
        b = IntegrationEventBus.get_instance()
        assert a is not b


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------


class TestEventModel:
    def test_event_is_frozen(self):
        event = _make_event()
        with pytest.raises(AttributeError):
            event.tenant_id = "changed"  # type: ignore[misc]

    def test_event_has_timestamp(self):
        event = _make_event()
        assert event.timestamp > 0

    def test_all_event_types_exist(self):
        assert len(IntegrationEventType) == 10

    def test_event_type_values(self):
        assert IntegrationEventType.TICKET_CREATED.value == "ticket.created"
        assert IntegrationEventType.SYNC_FAILED.value == "sync.failed"
        assert IntegrationEventType.INTEGRATION_CONNECTED.value == "integration.connected"


# ---------------------------------------------------------------------------
# Drain
# ---------------------------------------------------------------------------


class TestDrain:
    @pytest.mark.asyncio
    async def test_drain_returns_pending_count(self, bus: IntegrationEventBus):
        async def slow_handler(e: IntegrationEvent) -> None:
            await asyncio.sleep(0.1)

        bus.on(IntegrationEventType.TICKET_CREATED, slow_handler)
        await bus.emit(_make_event())
        count = await bus.drain(timeout=2.0)
        assert count >= 1

    @pytest.mark.asyncio
    async def test_drain_with_no_pending(self, bus: IntegrationEventBus):
        count = await bus.drain()
        assert count == 0
