"""Schedule Agent — Follow-up Activities and Event Notifications (SPEC-1711).

Manages scheduled follow-up actions (callback reminders, order check-ins,
appointment confirmations) and reacts to external events (shipping updates,
payment confirmations) by proactively notifying customers.

Supports one-time and recurring schedules with timezone awareness.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

AGENT_ID = "schedule"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class FollowupStatus(str, Enum):
    PENDING = "pending"
    TRIGGERED = "triggered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class FollowupType(str, Enum):
    CALLBACK_REMINDER = "callback_reminder"
    ORDER_CHECKIN = "order_checkin"
    APPOINTMENT_CONFIRM = "appointment_confirm"
    SHIPPING_UPDATE = "shipping_update"
    PAYMENT_CONFIRM = "payment_confirm"
    CUSTOM = "custom"


class RecurrenceRule(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduledFollowup:
    """A scheduled follow-up action."""

    followup_id: str
    tenant_id: str
    conversation_id: str
    customer_id: str = ""
    followup_type: str = FollowupType.CUSTOM.value
    message: str = ""
    channel: str = "chat"  # chat, email, sms
    scheduled_at: float = 0.0  # UTC timestamp
    timezone: str = "UTC"
    recurrence: str = RecurrenceRule.ONCE.value
    status: str = FollowupStatus.PENDING.value
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    triggered_at: float = 0.0


@dataclass
class ExternalEvent:
    """An ingested external event that may trigger a notification."""

    event_id: str
    tenant_id: str
    event_type: str  # shipping.delivered, payment.confirmed, etc.
    reference_id: str = ""  # order_id, payment_id, etc.
    customer_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    processed: bool = False


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------


class ScheduleAgentTools:
    """Tool implementations for the Schedule Agent.

    Each method maps to an MCP tool capability defined in agents.yaml.
    """

    def __init__(self) -> None:
        self._followups: dict[str, ScheduledFollowup] = {}
        self._events: list[ExternalEvent] = []
        self._counter = 0

    async def create_followup(
        self,
        tenant_id: str,
        conversation_id: str,
        *,
        followup_type: str = "custom",
        message: str = "",
        channel: str = "chat",
        scheduled_at: float = 0.0,
        timezone: str = "UTC",
        recurrence: str = "once",
        customer_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a scheduled follow-up action.

        Tool: schedule.create_followup
        """
        self._counter += 1
        followup_id = f"fu-{tenant_id}-{self._counter}"

        if scheduled_at <= 0:
            scheduled_at = time.time() + 3600  # Default: 1 hour from now

        followup = ScheduledFollowup(
            followup_id=followup_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            followup_type=followup_type,
            message=message,
            channel=channel,
            scheduled_at=scheduled_at,
            timezone=timezone,
            recurrence=recurrence,
            metadata=metadata or {},
        )
        self._followups[followup_id] = followup

        logger.info(
            "Scheduled followup: %s type=%s at=%s",
            followup_id, followup_type, scheduled_at,
        )

        return {
            "followup_id": followup_id,
            "status": followup.status,
            "scheduled_at": scheduled_at,
            "timezone": timezone,
            "recurrence": recurrence,
            "channel": channel,
        }

    async def list_pending(
        self,
        tenant_id: str,
        *,
        conversation_id: str | None = None,
        customer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List pending follow-up actions.

        Tool: schedule.list_pending
        """
        results = []
        for fu in self._followups.values():
            if fu.tenant_id != tenant_id:
                continue
            if fu.status != FollowupStatus.PENDING.value:
                continue
            if conversation_id and fu.conversation_id != conversation_id:
                continue
            if customer_id and fu.customer_id != customer_id:
                continue
            results.append({
                "followup_id": fu.followup_id,
                "type": fu.followup_type,
                "message": fu.message,
                "channel": fu.channel,
                "scheduled_at": fu.scheduled_at,
                "timezone": fu.timezone,
                "recurrence": fu.recurrence,
                "conversation_id": fu.conversation_id,
            })
        return sorted(results, key=lambda r: r["scheduled_at"])

    async def cancel_followup(
        self,
        tenant_id: str,
        followup_id: str,
    ) -> dict[str, Any]:
        """Cancel a pending follow-up.

        Tool: schedule.cancel_followup
        """
        fu = self._followups.get(followup_id)
        if not fu or fu.tenant_id != tenant_id:
            return {"error": "Follow-up not found"}

        if fu.status != FollowupStatus.PENDING.value:
            return {"error": f"Cannot cancel: status is {fu.status}"}

        fu.status = FollowupStatus.CANCELLED.value
        return {"followup_id": followup_id, "status": "cancelled"}

    async def ingest_event(
        self,
        tenant_id: str,
        event_type: str,
        *,
        reference_id: str = "",
        customer_id: str = "",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Ingest an external event for processing.

        Tool: schedule.ingest_event

        Events trigger matching follow-ups or create proactive notifications.
        """
        event = ExternalEvent(
            event_id=f"evt-{tenant_id}-{int(time.time())}",
            tenant_id=tenant_id,
            event_type=event_type,
            reference_id=reference_id,
            customer_id=customer_id,
            payload=payload or {},
        )
        self._events.append(event)

        # Check if any pending followups match this event
        triggered = []
        for fu in self._followups.values():
            if (
                fu.tenant_id == tenant_id
                and fu.status == FollowupStatus.PENDING.value
                and fu.customer_id == customer_id
                and fu.followup_type in event_type
            ):
                fu.status = FollowupStatus.TRIGGERED.value
                fu.triggered_at = time.time()
                triggered.append(fu.followup_id)

        event.processed = True

        return {
            "event_id": event.event_id,
            "event_type": event_type,
            "processed": True,
            "triggered_followups": triggered,
        }

    async def send_notification(
        self,
        tenant_id: str,
        customer_id: str,
        *,
        message: str = "",
        channel: str = "chat",
        conversation_id: str = "",
    ) -> dict[str, Any]:
        """Send a proactive notification to a customer.

        Tool: schedule.send_notification

        In production, routes through the appropriate channel
        (chat widget, email, SMS).
        """
        logger.info(
            "Notification: tenant=%s customer=%s channel=%s",
            tenant_id, customer_id, channel,
        )

        return {
            "sent": True,
            "customer_id": customer_id,
            "channel": channel,
            "message_preview": message[:100] if message else "",
            "conversation_id": conversation_id,
        }

    # -- Query helpers ------------------------------------------------------

    @property
    def pending_count(self) -> int:
        """Count of pending followups."""
        return sum(
            1 for fu in self._followups.values()
            if fu.status == FollowupStatus.PENDING.value
        )

    @property
    def total_events(self) -> int:
        """Total ingested events."""
        return len(self._events)
