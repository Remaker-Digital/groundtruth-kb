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

    AUTH-5: ``customer_token`` is an OTP-verified identity token. When
    present, the server validates the token signature and expiry. A valid
    token proves the customer verified their email → full PCM access.
    """

    visitor: VisitorIdentity | None = Field(
        default=None,
        description="Optional visitor identity for customer context",
    )
    customer_token: str | None = Field(
        default=None,
        max_length=500,
        description="OTP customer token proving email verification (AUTH-5)",
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
    target_agent_id: str | None = Field(
        default=None,
        description="Peer agent to chat with directly (team members only, SPEC-1862).",
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


class IssueReportRequest(BaseModel):
    """Request body for POST /api/chat/conversations/{conversation_id}/issue.

    Allows the customer to report an issue with the AI conversation
    to the merchant. This is NOT a bug report to Agent Red — it's a
    structured feedback mechanism from end customers to the merchant.

    C7: Report an Issue widget button.
    """

    issue_type: str = Field(
        min_length=1,
        max_length=100,
        description="Category of the issue (e.g. 'wrong_information', 'rude_response', 'not_helpful', 'other')",
    )
    details: str = Field(
        default="",
        max_length=2000,
        description="Free-text description of the issue",
    )


class IssueReportResponse(BaseModel):
    """Response body for POST /api/chat/conversations/{conversation_id}/issue."""

    conversation_id: str = Field(description="Conversation the issue was reported on")
    issue_id: str = Field(description="Assigned issue identifier")
    accepted: bool = Field(default=True, description="Whether the report was accepted")


class MessageFeedbackRequest(BaseModel):
    """Request body for POST /api/chat/conversations/{id}/messages/{message_id}/feedback.

    Allows end users to rate individual AI responses with thumbs up/down.
    SPEC-1836: User Feedback Mechanism.
    """

    rating: str = Field(
        description="Feedback rating: 'positive' (thumbs up) or 'negative' (thumbs down)",
        pattern="^(positive|negative)$",
    )
    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Optional free-text comment explaining the rating",
    )


class MessageFeedbackResponse(BaseModel):
    """Response body for POST /api/chat/conversations/{id}/messages/{message_id}/feedback."""

    conversation_id: str = Field(description="Conversation the feedback belongs to")
    message_id: str = Field(description="Message that was rated")
    rating: str = Field(description="Recorded rating (positive/negative)")
    accepted: bool = Field(default=True, description="Whether the feedback was recorded")


class QualityScore(BaseModel):
    """Per-turn or aggregate conversation quality score (CQ-1, SPEC-0180).

    Scores are on a 1.0-5.0 scale. The overall score is a weighted average:
    faithfulness (40%) + relevancy (40%) + tone (20%).
    """

    faithfulness: float = Field(ge=1.0, le=5.0, description="Faithfulness to knowledge context (1-5)")
    relevancy: float = Field(ge=1.0, le=5.0, description="Answer relevancy to customer question (1-5)")
    tone: float = Field(ge=1.0, le=5.0, description="Tone compliance — professional, no profanity (1-5)")
    overall: float = Field(ge=1.0, le=5.0, description="Weighted average: 0.4F + 0.4R + 0.2T")
    issues: list[str] = Field(default_factory=list, description="Human-readable issue descriptions")

    @property
    def passed(self) -> bool:
        """Score passes if overall >= 3.5."""
        return self.overall >= 3.5


class ConversationQualityResponse(BaseModel):
    """Response for GET /api/superadmin/conversations/{id}/quality (CQ-1)."""

    conversation_id: str = Field(description="Conversation identifier")
    turn_scores: list[QualityScore] = Field(default_factory=list, description="Per-turn quality scores")
    aggregate: QualityScore | None = Field(default=None, description="Aggregate conversation score")
    turn_count: int = Field(default=0, description="Number of scored turns")
    passed: bool = Field(default=False, description="Whether conversation meets quality threshold")


class ConsentUpdateRequest(BaseModel):
    """Request body for POST /api/chat/conversations/{conversation_id}/consent.

    Allows the customer to grant or deny consent for Persistent Customer
    Memory (Layers 2-4). This endpoint is called by the widget's consent
    banner when the tenant has consent_collection_enabled = true.

    WI #87: Widget consent collection for PCM vectorization.
    """

    consent_status: str = Field(
        description="Customer's consent choice: 'granted' or 'denied'",
    )


class ConsentUpdateResponse(BaseModel):
    """Response body for POST /api/chat/conversations/{conversation_id}/consent."""

    conversation_id: str = Field(description="Conversation this consent applies to")
    consent_status: str = Field(description="Recorded consent status")
    accepted: bool = Field(default=True, description="Whether the consent was recorded")


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
    customer_verified: bool = Field(
        default=False,
        description="Whether the customer has been verified (OTP, Shopify HMAC, etc.)",
    )
    target_agent_id: str = Field(
        default="",
        description="Peer agent targeted by team member (SPEC-1862).",
    )
    created_at: str = Field(description="When conversation started")
    last_activity_at: str = Field(description="Last message timestamp")


class StreamStatusResponse(BaseModel):
    """Response for GET /stream/{conversation_id}/status."""

    conversation_id: str = Field(description="Conversation identifier")
    is_streaming: bool = Field(description="Whether conversation is actively streaming")
    tab_count: int = Field(description="Number of tabs connected to this stream")
    can_connect: bool = Field(description="Whether tenant has capacity for more connections")
    active_connections: int = Field(description="Total active SSE connections for tenant")


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


def validated_event(
    conversation_id: str,
    message_id: str,
    sources: list[dict[str, str]] | None = None,
    blocks: list[dict] | None = None,
) -> StreamEvent:
    """Create a validated event — Critic approved the response.

    Args:
        sources: Optional structured source attribution (B1). Each entry
            has ``title`` and optionally ``url``. Included only when
            ``cite_sources_in_response`` is enabled and KR returned sources.
        blocks: Optional structured answer blocks (SPEC-1867). Each entry
            has ``type`` and type-specific fields. Included only when
            ``structured_blocks_enabled`` is true and tier >= professional.
    """
    data: dict = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "critic_passed": True,
    }
    if sources:
        data["sources"] = sources
    if blocks:
        data["blocks"] = blocks
    return StreamEvent(event=StreamEventType.VALIDATED, data=data)


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


def done_event(
    conversation_id: str,
    turn_count: int,
    trace_id: str | None = None,
    total_latency_ms: int | None = None,
) -> StreamEvent:
    """Create a done event — stream complete for this turn (SPEC-1533)."""
    data: dict[str, Any] = {
        "conversation_id": conversation_id,
        "turn_count": turn_count,
    }
    if trace_id is not None:
        data["trace_id"] = trace_id
    if total_latency_ms is not None:
        data["total_latency_ms"] = total_latency_ms
    return StreamEvent(
        event=StreamEventType.DONE,
        data=data,
    )


def stage_event(
    stage: str,
    status: str,
    latency_ms: int | None = None,
    trace_id: str | None = None,
    elapsed_ms: int | None = None,
) -> StreamEvent:
    """Create a stage event — pipeline progress indicator (SPEC-1533).

    Args:
        stage: Pipeline stage name (e.g. "intent-classifier").
        status: Stage status ("started" or "completed").
        latency_ms: Per-stage latency in milliseconds.
        trace_id: End-to-end trace identifier (SPEC-1530).
        elapsed_ms: Total pipeline elapsed time since entry.
    """
    data: dict[str, Any] = {"stage": stage, "status": status}
    if latency_ms is not None:
        data["latency_ms"] = latency_ms
    if trace_id is not None:
        data["trace_id"] = trace_id
    if elapsed_ms is not None:
        data["elapsed_ms"] = elapsed_ms
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
