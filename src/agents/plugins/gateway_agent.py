# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Gateway Agent — Human Escalation Connection MCP Server (SPEC-1710).

Manages seamless handoff from AI to human support agents.  Provides
agent availability monitoring, queue management, context transfer,
skill-based routing, and agent takeover/return transitions.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

AGENT_ID = "gateway"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class QueueStatus(str, Enum):
    WAITING = "waiting"
    CONNECTED = "connected"
    TRANSFERRED = "transferred"
    ABANDONED = "abandoned"
    RETURNED_TO_AI = "returned_to_ai"


class AgentAvailability(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    OFFLINE = "offline"


@dataclass
class HumanAgent:
    """Human support agent."""

    agent_id: str
    name: str
    skills: list[str] = field(default_factory=list)
    availability: str = AgentAvailability.AVAILABLE.value
    current_conversations: int = 0
    max_conversations: int = 5


@dataclass
class QueueEntry:
    """Customer in the escalation queue."""

    queue_id: str
    tenant_id: str
    conversation_id: str
    customer_name: str = ""
    reason: str = ""
    priority: int = 0  # 0=normal, 1=high, 2=urgent
    status: str = QueueStatus.WAITING.value
    assigned_agent_id: str = ""
    context_summary: str = ""
    created_at: float = field(default_factory=time.time)
    connected_at: float = 0.0
    skills_requested: list[str] = field(default_factory=list)

    @property
    def wait_time_seconds(self) -> float:
        if self.connected_at > 0:
            return self.connected_at - self.created_at
        return time.time() - self.created_at


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------


class GatewayAgentTools:
    """Tool implementations for the Gateway Agent.

    Each method maps to an MCP tool capability defined in agents.yaml.
    """

    def __init__(self) -> None:
        self._agents: dict[str, list[HumanAgent]] = {}  # tenant_id → agents
        self._queue: list[QueueEntry] = []
        self._queue_counter = 0

    async def check_availability(
        self,
        tenant_id: str,
        *,
        skill: str | None = None,
    ) -> dict[str, Any]:
        """Check human agent availability and estimated wait time.

        Tool: gateway.check_availability
        """
        agents = self._agents.get(tenant_id, [])
        available = [
            a for a in agents
            if a.availability == AgentAvailability.AVAILABLE.value
            and a.current_conversations < a.max_conversations
        ]
        if skill:
            available = [a for a in available if skill in a.skills]

        waiting = [
            e for e in self._queue
            if e.tenant_id == tenant_id and e.status == QueueStatus.WAITING.value
        ]

        # Estimate: 3 minutes per person in queue
        estimated_wait = len(waiting) * 180 if not available else 0

        return {
            "agents_available": len(available),
            "agents_total": len(agents),
            "queue_length": len(waiting),
            "estimated_wait_seconds": estimated_wait,
            "skill_filter": skill,
        }

    async def queue_customer(
        self,
        tenant_id: str,
        conversation_id: str,
        *,
        customer_name: str = "",
        reason: str = "",
        priority: int = 0,
        skills_requested: list[str] | None = None,
        context_summary: str = "",
    ) -> dict[str, Any]:
        """Add customer to the escalation queue.

        Tool: gateway.queue_customer
        """
        self._queue_counter += 1
        queue_id = f"q-{tenant_id}-{self._queue_counter}"

        entry = QueueEntry(
            queue_id=queue_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            customer_name=customer_name,
            reason=reason,
            priority=priority,
            context_summary=context_summary,
            skills_requested=skills_requested or [],
        )
        self._queue.append(entry)

        # Attempt auto-assignment
        assigned = await self._try_assign(entry)

        position = sum(
            1 for e in self._queue
            if e.tenant_id == tenant_id
            and e.status == QueueStatus.WAITING.value
            and e.created_at <= entry.created_at
        )

        return {
            "queue_id": queue_id,
            "status": entry.status,
            "position": position,
            "assigned_agent": entry.assigned_agent_id or None,
            "estimated_wait_seconds": 0 if assigned else position * 180,
        }

    async def transfer_context(
        self,
        tenant_id: str,
        conversation_id: str,
        *,
        summary: str = "",
        intent: str = "",
        sentiment: str = "",
        customer_info: dict[str, Any] | None = None,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Transfer conversation context to the assigned human agent.

        Tool: gateway.transfer_context
        """
        entry = next(
            (e for e in self._queue if e.conversation_id == conversation_id),
            None,
        )
        if not entry:
            return {"error": "No queue entry for this conversation"}

        context = {
            "conversation_id": conversation_id,
            "summary": summary or entry.context_summary,
            "intent": intent,
            "sentiment": sentiment,
            "customer_info": customer_info or {},
            "message_count": len(conversation_history or []),
            "assigned_agent_id": entry.assigned_agent_id,
        }

        if entry.status == QueueStatus.WAITING.value and entry.assigned_agent_id:
            entry.status = QueueStatus.CONNECTED.value
            entry.connected_at = time.time()

        return {
            "transferred": True,
            "context": context,
            "status": entry.status,
            "wait_time_seconds": entry.wait_time_seconds,
        }

    async def monitor_queue(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Get queue status for monitoring/supervisor view.

        Tool: gateway.monitor_queue
        """
        tenant_entries = [e for e in self._queue if e.tenant_id == tenant_id]
        waiting = [e for e in tenant_entries if e.status == QueueStatus.WAITING.value]
        connected = [e for e in tenant_entries if e.status == QueueStatus.CONNECTED.value]

        agents = self._agents.get(tenant_id, [])
        available = [
            a for a in agents
            if a.availability == AgentAvailability.AVAILABLE.value
        ]

        return {
            "queue_length": len(waiting),
            "active_conversations": len(connected),
            "agents_available": len(available),
            "agents_total": len(agents),
            "entries": [
                {
                    "queue_id": e.queue_id,
                    "customer_name": e.customer_name,
                    "reason": e.reason,
                    "status": e.status,
                    "wait_seconds": e.wait_time_seconds,
                    "priority": e.priority,
                    "assigned_agent": e.assigned_agent_id,
                }
                for e in tenant_entries
                if e.status in (QueueStatus.WAITING.value, QueueStatus.CONNECTED.value)
            ],
        }

    # -- Internal routing ---------------------------------------------------

    async def _try_assign(self, entry: QueueEntry) -> bool:
        """Try to auto-assign an available agent to a queue entry."""
        agents = self._agents.get(entry.tenant_id, [])
        for agent in agents:
            if (
                agent.availability == AgentAvailability.AVAILABLE.value
                and agent.current_conversations < agent.max_conversations
            ):
                # Check skill match
                if entry.skills_requested:
                    if not any(s in agent.skills for s in entry.skills_requested):
                        continue

                entry.assigned_agent_id = agent.agent_id
                entry.status = QueueStatus.WAITING.value  # Still waiting for context transfer
                agent.current_conversations += 1
                return True
        return False

    # -- Test helpers -------------------------------------------------------

    def seed_agents(self, tenant_id: str, agents: list[HumanAgent]) -> None:
        """Seed human agents for testing."""
        self._agents[tenant_id] = agents
