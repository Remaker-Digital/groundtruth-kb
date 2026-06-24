"""SPEC-1778 coverage for the internal integration event bus."""

from __future__ import annotations

import asyncio
import json
from dataclasses import FrozenInstanceError

import pytest

from src.integrations.event_bus import (
    IntegrationEvent,
    IntegrationEventBus,
    IntegrationEventType,
)


@pytest.fixture(autouse=True)
def _reset_event_bus():
    IntegrationEventBus.reset()
    yield
    IntegrationEventBus.reset()


@pytest.fixture
def bus() -> IntegrationEventBus:
    return IntegrationEventBus.get_instance()


def _event(
    event_type: IntegrationEventType = IntegrationEventType.TICKET_CREATED,
    *,
    tenant_id: str = "tenant-1",
    integration_id: str = "integration-1",
    payload: dict[str, object] | None = None,
    correlation_id: str = "corr-1",
) -> IntegrationEvent:
    return IntegrationEvent(
        event_type=event_type,
        tenant_id=tenant_id,
        integration_id=integration_id,
        payload=payload or {"source": "spec-1778"},
        correlation_id=correlation_id,
    )


def test_spec1778_declares_complete_event_taxonomy() -> None:
    assert {event_type.value for event_type in IntegrationEventType} == {
        "ticket.created",
        "ticket.updated",
        "article.created",
        "article.updated",
        "message.received",
        "action.completed",
        "integration.connected",
        "integration.disconnected",
        "sync.completed",
        "sync.failed",
    }


def test_spec1778_registers_unregisters_counts_and_isolates_event_types(
    bus: IntegrationEventBus,
) -> None:
    async def ticket_handler(event: IntegrationEvent) -> None:
        del event

    async def sync_handler(event: IntegrationEvent) -> None:
        del event

    bus.on(IntegrationEventType.TICKET_CREATED, ticket_handler)
    bus.on(IntegrationEventType.SYNC_COMPLETED, sync_handler)

    assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 1
    assert bus.handler_count(IntegrationEventType.SYNC_COMPLETED) == 1
    assert bus.handler_count(IntegrationEventType.SYNC_FAILED) == 0
    assert bus.total_handlers == 2

    assert bus.off(IntegrationEventType.SYNC_COMPLETED, ticket_handler) is False
    assert bus.off(IntegrationEventType.TICKET_CREATED, ticket_handler) is True
    assert bus.handler_count(IntegrationEventType.TICKET_CREATED) == 0
    assert bus.total_handlers == 1


@pytest.mark.asyncio
async def test_spec1778_emit_dispatches_background_tasks_and_drains(
    bus: IntegrationEventBus,
) -> None:
    release_handlers = asyncio.Event()
    received: list[str] = []

    async def first_handler(event: IntegrationEvent) -> None:
        await release_handlers.wait()
        received.append(f"first:{event.correlation_id}")

    async def second_handler(event: IntegrationEvent) -> None:
        await release_handlers.wait()
        received.append(f"second:{event.correlation_id}")

    bus.on(IntegrationEventType.TICKET_CREATED, first_handler)
    bus.on(IntegrationEventType.TICKET_CREATED, second_handler)

    dispatched = await bus.emit(_event())

    assert dispatched == 2
    assert bus.emit_count == 1
    assert bus.pending_tasks == 2

    release_handlers.set()
    pending_before_drain = await bus.drain(timeout=2.0)

    assert pending_before_drain == 2
    assert sorted(received) == ["first:corr-1", "second:corr-1"]
    assert bus.pending_tasks == 0


@pytest.mark.asyncio
async def test_spec1778_handler_failures_do_not_block_siblings(
    bus: IntegrationEventBus,
) -> None:
    received: list[str] = []

    async def failing_handler(event: IntegrationEvent) -> None:
        del event
        raise RuntimeError("handler failed")

    async def succeeding_handler(event: IntegrationEvent) -> None:
        received.append(event.tenant_id)

    bus.on(IntegrationEventType.TICKET_UPDATED, failing_handler)
    bus.on(IntegrationEventType.TICKET_UPDATED, succeeding_handler)

    dispatched = await bus.emit(_event(IntegrationEventType.TICKET_UPDATED))
    await bus.drain()

    assert dispatched == 2
    assert received == ["tenant-1"]
    assert bus.error_count == 1


@pytest.mark.asyncio
async def test_spec1778_representative_handler_categories_receive_events(
    bus: IntegrationEventBus,
) -> None:
    received: list[tuple[str, str]] = []

    async def ai_pipeline_handler(event: IntegrationEvent) -> None:
        received.append(("ai-pipeline", event.event_type.value))

    async def knowledge_ingestion_handler(event: IntegrationEvent) -> None:
        received.append(("knowledge-ingestion", event.event_type.value))

    async def analytics_handler(event: IntegrationEvent) -> None:
        received.append(("analytics", event.event_type.value))

    async def notification_handler(event: IntegrationEvent) -> None:
        received.append(("notification", event.event_type.value))

    bus.on(IntegrationEventType.MESSAGE_RECEIVED, ai_pipeline_handler)
    bus.on(IntegrationEventType.ARTICLE_CREATED, knowledge_ingestion_handler)
    bus.on(IntegrationEventType.ACTION_COMPLETED, analytics_handler)
    bus.on(
        IntegrationEventType.INTEGRATION_DISCONNECTED,
        notification_handler,
    )

    for event_type in (
        IntegrationEventType.MESSAGE_RECEIVED,
        IntegrationEventType.ARTICLE_CREATED,
        IntegrationEventType.ACTION_COMPLETED,
        IntegrationEventType.INTEGRATION_DISCONNECTED,
    ):
        assert await bus.emit(_event(event_type)) == 1

    await bus.drain()

    assert sorted(received) == [
        ("ai-pipeline", "message.received"),
        ("analytics", "action.completed"),
        ("knowledge-ingestion", "article.created"),
        ("notification", "integration.disconnected"),
    ]


def test_spec1778_event_payload_is_immutable_and_pubsub_serializable() -> None:
    event = _event(
        IntegrationEventType.SYNC_FAILED,
        tenant_id="tenant-42",
        integration_id="zendesk-main",
        payload={"reason": "timeout", "attempt": 3},
        correlation_id="sync-42",
    )

    with pytest.raises(FrozenInstanceError):
        event.tenant_id = "changed"  # type: ignore[misc]

    pubsub_payload = {
        "event_type": event.event_type.value,
        "tenant_id": event.tenant_id,
        "integration_id": event.integration_id,
        "payload": event.payload,
        "timestamp": event.timestamp,
        "correlation_id": event.correlation_id,
    }

    encoded = json.dumps(pubsub_payload)
    decoded = json.loads(encoded)

    assert decoded == {
        "event_type": "sync.failed",
        "tenant_id": "tenant-42",
        "integration_id": "zendesk-main",
        "payload": {"reason": "timeout", "attempt": 3},
        "timestamp": event.timestamp,
        "correlation_id": "sync-42",
    }


@pytest.mark.asyncio
async def test_spec1778_emit_sync_schedules_when_loop_is_running(
    bus: IntegrationEventBus,
) -> None:
    received: list[str] = []

    async def handler(event: IntegrationEvent) -> None:
        received.append(event.event_type.value)

    bus.on(IntegrationEventType.INTEGRATION_CONNECTED, handler)

    result = bus.emit_sync(_event(IntegrationEventType.INTEGRATION_CONNECTED))
    await asyncio.sleep(0)
    await bus.drain()

    assert result == 0
    assert received == ["integration.connected"]
    assert bus.emit_count == 1


def test_spec1778_emit_sync_fails_closed_without_running_loop(
    bus: IntegrationEventBus,
) -> None:
    bus.on(IntegrationEventType.SYNC_COMPLETED, lambda event: asyncio.sleep(0))

    assert bus.emit_sync(_event(IntegrationEventType.SYNC_COMPLETED)) == 0
    assert bus.emit_count == 0
    assert bus.pending_tasks == 0
