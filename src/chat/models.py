"""
Chat API Pydantic models — request/response schemas for the conversation API.

Defines the data contract for all 6 chat endpoints:
    POST /api/chat/conversations         — ConversationStartRequest → ConversationStartResponse
    POST /api/chat/message               — SendMessageRequest → SendMessageResponse
    GET  /api/chat/stream/{id}           — (SSE stream of StreamEvent)
    GET  /api/chat/conversations/{id}    — ConversationStateResponse
    POST /api/chat/conversations/{id}/end — EndConversationRequest → EndConversationResponse
    WS   /ws/chat/{id}                   — WebSocketMessage (bidirectional)

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §3: Chat API Specification
    - Decision UI-4: Hybrid protocol (HTTP + SSE + WebSocket)
    - Decision UI-5: SSE stream-then-validate with Critic retraction
    - Decision UI-6: Publishable widget key authentication

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MessageRole(str, Enum):
    """Who sent the message."""

    CUSTOMER = "customer"
    AI = "ai"
    SYSTEM = "system"
    HUMAN_AGENT = "human_agent"


class StreamEventType(str, Enum):
    """SSE event types emitted by the streaming endpoint.

    Lifecycle:
        1. ``stage`` events report pipeline progress (optional, for debug).
        2. ``token`` events stream response text as it's generated.
        3. ``validated`` confirms Critic approved the response.
        4. ``retracted`` replaces displayed text with SAFE_FALLBACK_MESSAGE.
        5. ``done`` signals the stream is complete.
        6. ``error`` reports a pipeline failure.
    """

    TOKEN = "token"
    VALIDATED = "validated"
    RETRACTED = "retracted"
    DONE = "done"
    ERROR = "error"
    STAGE = "stage"


class WebSocketMessageType(str, Enum):
    """WebSocket message types for bidirectional communication.

    Used after escalation to a human agent, and for presence/typing
    indicators during any conversation phase.
    """

    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    PRESENCE = "presence"
    HUMAN_MESSAGE = "human_message"
    AGENT_MESSAGE = "agent_message"
    SYSTEM_EVENT = "system_event"


# ---------------------------------------------------------------------------
# Shared models
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    """A single message in a conversation transcript.

    Used both in API responses (conversation state) and internally for
    ConversationDocument.messages storage.
    """

    role: MessageRole = Field(description="Who sent the message")
    content: str = Field(description="Message text content")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp",
    )
    message_id: str | None = Field(
        default=None,
        description="Unique message identifier (assigned server-side)",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata (agent name, model, latency_ms)",
    )


class VisitorIdentity(BaseModel):
    """Optional pre-chat visitor identity.

    If the merchant's storefront has logged-in customers, the widget can
    pass identity with an HMAC signature for server-side verification
    (Decision UI-6).
    """

    name: str | None = Field(default=None, max_length=200, description="Visitor display name")
    email: str | None = Field(default=None, max_length=320, description="Visitor email address")
    customer_id: str | None = Field(
        default=None,
        max_length=200,
        description="Merchant-side customer identifier (e.g. Shopify customer GID)",
    )
    hmac: str | None = Field(
        default=None,
        description="HMAC-SHA256(customer_id, tenant_secret) for identity verification",
    )


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ConversationStartRequest(BaseModel):
    """Request body for POST /api/chat/conversations.

    Starts a new conversation. The conversation_id is assigned server-side
    and returned in the response. An optional visitor identity can be
    provided for customer context (Layer 1) injection.
    """

    visitor: VisitorIdentity | None = Field(
        default=None,
        description="Optional visitor identity for customer context",
    )
    page_url: str | None = Field(
        default=None,
        max_length=2048,
        description="URL of the page where the widget was opened",
    )
    initial_message: str | None = Field(
        default=None,
        max_length=4000,
        description="Optional first message sent with conversation start",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Client metadata (browser, device, locale)",
    )


class SendMessageRequest(BaseModel):
    """Request body for POST /api/chat/message.

    Appends a customer message to an active conversation and triggers
    the 6-agent pipeline (IC → KR → RG → CR).
    """

    conversation_id: str = Field(description="Target conversation identifier")
    content: str = Field(
        min_length=1,
        max_length=4000,
        description="Customer message text",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Client metadata for this message",
    )


class EndConversationRequest(BaseModel):
    """Request body for POST /api/chat/conversations/{conversation_id}/end.

    Allows the customer to explicitly end a conversation. Optional
    feedback can be captured.
    """

    reason: str | None = Field(
        default=None,
        max_length=500,
        description="Optional reason for ending (e.g. 'resolved', 'gave_up')",
    )
    feedback_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Optional 1-5 star rating",
    )
    feedback_text: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional free-text feedback",
    )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ConversationStartResponse(BaseModel):
    """Response body for POST /api/chat/conversations.

    Returns the assigned conversation_id and the SSE stream URL the
    client should connect to for receiving AI responses.
    """

    conversation_id: str = Field(description="Assigned conversation identifier")
    stream_url: str = Field(description="SSE endpoint URL for this conversation")
    ws_url: str = Field(description="WebSocket endpoint URL for typing/presence")
    created_at: str = Field(description="ISO 8601 creation timestamp")


class SendMessageResponse(BaseModel):
    """Response body for POST /api/chat/message.

    Acknowledges the message was received and queued for pipeline
    processing. The AI response arrives via the SSE stream, not in
    this HTTP response.
    """

    message_id: str = Field(description="Assigned message identifier")
    conversation_id: str = Field(description="Conversation this message belongs to")
    turn_count: int = Field(description="Current turn count after this message")
    accepted: bool = Field(default=True, description="Whether the message was accepted")


class EndConversationResponse(BaseModel):
    """Response body for POST /api/chat/conversations/{id}/end."""

    conversation_id: str = Field(description="Conversation that was ended")
    status: str = Field(description="Final conversation status")
    turn_count: int = Field(description="Total turns in conversation")
    duration_seconds: int | None = Field(
        default=None,
        description="Conversation duration in seconds",
    )
    is_billable: bool = Field(description="Whether this conversation was billable")


class ConversationStateResponse(BaseModel):
    """Response body for GET /api/chat/conversations/{id}.

    Returns the current state of a conversation, including the full
    message history.
    """

    conversation_id: str = Field(description="Conversation identifier")
    status: str = Field(description="Current status (active, completed, escalated, etc.)")
    turn_count: int = Field(description="Number of customer-AI turn pairs")
    message_count: int = Field(description="Total messages in conversation")
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="Conversation messages in chronological order",
    )
    is_escalated: bool = Field(
        default=False,
        description="Whether conversation has been escalated to a human agent",
    )
    created_at: str = Field(description="When conversation started")
    last_activity_at: str = Field(description="Last message timestamp")


# ---------------------------------------------------------------------------
# SSE stream models
# ---------------------------------------------------------------------------


class StreamEvent(BaseModel):
    """A single Server-Sent Event in the response stream.

    Serialized to SSE format::

        event: token
        data: {"text": "Hello", "sequence": 1}

        event: validated
        data: {"conversation_id": "...", "critic_passed": true}

        event: retracted
        data: {"fallback_text": "I'm sorry...", "reason": "policy_violation"}
    """

    event: StreamEventType = Field(description="SSE event type")
    data: dict[str, Any] = Field(description="Event payload")

    def to_sse(self) -> str:
        """Serialize to SSE wire format (event + data lines)."""
        import json

        lines = [f"event: {self.event.value}", f"data: {json.dumps(self.data)}", "", ""]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# SSE event payload factories
# ---------------------------------------------------------------------------


def token_event(text: str, sequence: int) -> StreamEvent:
    """Create a token event for streaming a chunk of AI response text."""
    return StreamEvent(
        event=StreamEventType.TOKEN,
        data={"text": text, "sequence": sequence},
    )


def validated_event(conversation_id: str, message_id: str) -> StreamEvent:
    """Create a validated event — Critic approved the response."""
    return StreamEvent(
        event=StreamEventType.VALIDATED,
        data={
            "conversation_id": conversation_id,
            "message_id": message_id,
            "critic_passed": True,
        },
    )


def retracted_event(fallback_text: str, reason: str) -> StreamEvent:
    """Create a retracted event — Critic rejected, replace displayed text."""
    return StreamEvent(
        event=StreamEventType.RETRACTED,
        data={
            "fallback_text": fallback_text,
            "reason": reason,
            "critic_passed": False,
        },
    )


def error_event(
    message: str,
    code: str = "pipeline_error",
    *,
    recoverable: bool = True,
    tokens_sent: int | None = None,
    stage: str | None = None,
) -> StreamEvent:
    """Create an error event — pipeline failure.

    Args:
        message: Human-readable error description.
        code: Machine-readable error code.
        recoverable: Whether the client should retry (WI #131).
        tokens_sent: Number of token chunks already streamed before
            the error occurred (WI #131 — partial response tracking).
        stage: Pipeline stage where the error occurred (WI #131).
    """
    data: dict[str, Any] = {
        "message": message,
        "code": code,
        "recoverable": recoverable,
    }
    if tokens_sent is not None:
        data["tokens_sent"] = tokens_sent
    if stage is not None:
        data["stage"] = stage
    return StreamEvent(
        event=StreamEventType.ERROR,
        data=data,
    )


def done_event(conversation_id: str, turn_count: int) -> StreamEvent:
    """Create a done event — stream complete for this turn."""
    return StreamEvent(
        event=StreamEventType.DONE,
        data={"conversation_id": conversation_id, "turn_count": turn_count},
    )


def stage_event(stage: str, status: str, latency_ms: int | None = None) -> StreamEvent:
    """Create a stage event — pipeline progress indicator."""
    data: dict[str, Any] = {"stage": stage, "status": status}
    if latency_ms is not None:
        data["latency_ms"] = latency_ms
    return StreamEvent(
        event=StreamEventType.STAGE,
        data=data,
    )


# ---------------------------------------------------------------------------
# WebSocket models
# ---------------------------------------------------------------------------


class WebSocketMessage(BaseModel):
    """Bidirectional WebSocket message for typing/presence/human chat.

    Used by both the customer widget and the merchant admin inbox.
    """

    type: WebSocketMessageType = Field(description="Message type")
    conversation_id: str = Field(description="Conversation this message belongs to")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific payload",
    )
    sender_id: str | None = Field(
        default=None,
        description="Who sent this message (customer_id or agent_id)",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp",
    )
