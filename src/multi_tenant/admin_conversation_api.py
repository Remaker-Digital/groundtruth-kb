"""Admin Conversation Inbox API — merchant conversation management (WI #171).

Provides REST endpoints for the merchant admin dashboard's Conversation
Inbox component:

    GET  /api/admin/conversations              — List with filtering & pagination
    GET  /api/admin/conversations/{id}         — Full conversation detail
    GET  /api/admin/conversations/{id}/messages — Message history
    POST /api/admin/conversations/{id}/assign  — Assign to human agent
    POST /api/admin/conversations/{id}/notes   — Add internal note

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §7: WI #171 — Conversation Inbox API
    - Decision UI-7: Dual admin frontends (Shopify embedded + standalone)
    - Decision #1: TenantScopedRepository enforces tenant isolation

Dependencies:
    - repository.py: ConversationRepository (list_filtered, count_filtered,
      assign_agent, add_internal_note)
    - cosmos_schema.py: ConversationDocument, ConversationStatus
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import ConversationStatus
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import ConversationRepository, DocumentNotFoundError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AdminConversationSummary(BaseModel):
    """Compact conversation record for the admin inbox list view."""

    conversation_id: str
    status: str | None = None
    customer_id: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    last_activity_at: str | None = None
    assigned_to: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None


class AdminConversationListResponse(BaseModel):
    """Paginated list of conversations for the admin inbox."""

    tenant_id: str
    total_count: int = Field(description="Total matching conversations")
    offset: int
    limit: int
    conversations: list[AdminConversationSummary]


class AdminConversationDetailResponse(BaseModel):
    """Full conversation detail for the admin inbox."""

    conversation_id: str
    tenant_id: str
    status: str | None = None
    customer_id: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    last_activity_at: str | None = None
    assigned_to: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None
    internal_notes: list[dict[str, Any]] = Field(default_factory=list)


class MessageEntry(BaseModel):
    """A single message in the conversation transcript."""

    role: str
    content: str
    timestamp: str | None = None
    message_id: str | None = None
    metadata: dict[str, Any] | None = None


class ConversationMessagesResponse(BaseModel):
    """Full message history for a conversation."""

    conversation_id: str
    tenant_id: str
    message_count: int
    messages: list[MessageEntry]


class AssignAgentRequest(BaseModel):
    """Request body for POST /api/admin/conversations/{id}/assign."""

    agent_id: str = Field(
        min_length=1,
        max_length=200,
        description="Human agent identifier to assign",
    )


class AssignAgentResponse(BaseModel):
    """Response for successful agent assignment."""

    conversation_id: str
    assigned_to: str
    assigned_at: str


class AddNoteRequest(BaseModel):
    """Request body for POST /api/admin/conversations/{id}/notes."""

    content: str = Field(
        min_length=1,
        max_length=4000,
        description="Note text content",
    )
    author: str | None = Field(
        default=None,
        max_length=200,
        description="Note author (defaults to authenticated user)",
    )


class AddNoteResponse(BaseModel):
    """Response for successfully added note."""

    conversation_id: str
    note_id: str
    created_at: str


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_conversation_repo: ConversationRepository | None = None


def configure_admin_conversation_services(
    conversation_repo: ConversationRepository,
) -> None:
    """Wire the admin conversation API to its backing repository.

    Called during app startup after ConversationRepository is initialised.
    """
    global _conversation_repo
    _conversation_repo = conversation_repo
    logger.info("Admin conversation inbox API services configured")


def _get_repo() -> ConversationRepository:
    """Get the ConversationRepository, raising 503 if not initialised."""
    if _conversation_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin conversation services not initialised",
        )
    return _conversation_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/conversations", tags=["admin-inbox"])


# ---------------------------------------------------------------------------
# GET /api/admin/conversations — List with filtering & pagination
# ---------------------------------------------------------------------------


@router.get("", response_model=AdminConversationListResponse)
async def list_conversations(
    status: str | None = Query(
        None,
        description="Filter by status (active, completed, escalated, timed_out, error)",
    ),
    customer_id: str | None = Query(
        None,
        description="Filter by customer identifier",
    ),
    since: str | None = Query(
        None,
        description="Start date filter (ISO 8601, inclusive)",
    ),
    until: str | None = Query(
        None,
        description="End date filter (ISO 8601, exclusive)",
    ),
    assigned_to: str | None = Query(
        None,
        description="Filter by assigned agent ID",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AdminConversationListResponse:
    """List conversations for the merchant admin inbox.

    Supports filtering by status, customer, date range, and assigned agent.
    Results are ordered by most recent activity first.
    """
    repo = _get_repo()

    # Validate status if provided
    conv_status: ConversationStatus | None = None
    if status is not None:
        try:
            conv_status = ConversationStatus(status)
        except ValueError:
            valid = [s.value for s in ConversationStatus]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Valid values: {valid}",
            )

    # Get total count and page of results
    total_count = await repo.count_filtered(
        tenant_id=ctx.tenant_id,
        status=conv_status,
        customer_id=customer_id,
        since=since,
        until=until,
        assigned_to=assigned_to,
    )

    conversations_raw = await repo.list_filtered(
        tenant_id=ctx.tenant_id,
        status=conv_status,
        customer_id=customer_id,
        since=since,
        until=until,
        assigned_to=assigned_to,
        offset=offset,
        limit=limit,
    )

    conversations = [
        AdminConversationSummary(
            conversation_id=c.get("conversation_id", c.get("id", "")),
            status=c.get("status"),
            customer_id=c.get("customer_id"),
            is_billable=c.get("is_billable", False),
            message_count=c.get("message_count", 0),
            turn_count=c.get("turn_count", 0),
            started_at=c.get("started_at"),
            ended_at=c.get("ended_at"),
            last_activity_at=c.get("last_activity_at"),
            assigned_to=c.get("assigned_to"),
            agents_invoked=c.get("agents_invoked", []),
            model_used=c.get("model_used"),
            critic_passed=c.get("critic_passed"),
        )
        for c in conversations_raw
    ]

    return AdminConversationListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        conversations=conversations,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/conversations/{conversation_id} — Full detail
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}",
    response_model=AdminConversationDetailResponse,
)
async def get_conversation_detail(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AdminConversationDetailResponse:
    """Get full conversation detail including internal notes.

    Returns all conversation metadata, pipeline trace, and internal
    merchant notes. Message transcript is available via the separate
    /messages endpoint.
    """
    repo = _get_repo()

    try:
        doc = await repo.read(ctx.tenant_id, conversation_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    return AdminConversationDetailResponse(
        conversation_id=doc.get("conversation_id", doc.get("id", "")),
        tenant_id=ctx.tenant_id,
        status=doc.get("status"),
        customer_id=doc.get("customer_id"),
        is_billable=doc.get("is_billable", False),
        message_count=doc.get("message_count", 0),
        turn_count=doc.get("turn_count", 0),
        started_at=doc.get("started_at"),
        ended_at=doc.get("ended_at"),
        last_activity_at=doc.get("last_activity_at"),
        assigned_to=doc.get("assigned_to"),
        agents_invoked=doc.get("agents_invoked", []),
        model_used=doc.get("model_used"),
        critic_passed=doc.get("critic_passed"),
        internal_notes=doc.get("internal_notes", []),
    )


# ---------------------------------------------------------------------------
# GET /api/admin/conversations/{conversation_id}/messages — Message history
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
)
async def get_conversation_messages(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationMessagesResponse:
    """Get the full message history for a conversation.

    Returns all messages in chronological order, including customer
    messages, AI responses, system events, and human agent messages.
    """
    repo = _get_repo()

    try:
        doc = await repo.read(ctx.tenant_id, conversation_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    raw_messages = doc.get("messages", [])
    messages = [
        MessageEntry(
            role=m.get("role", "system"),
            content=m.get("content", ""),
            timestamp=m.get("timestamp"),
            message_id=m.get("message_id"),
            metadata=m.get("metadata"),
        )
        for m in raw_messages
    ]

    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        tenant_id=ctx.tenant_id,
        message_count=len(messages),
        messages=messages,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/assign — Assign agent
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/assign",
    response_model=AssignAgentResponse,
)
async def assign_agent(
    conversation_id: str,
    request: AssignAgentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AssignAgentResponse:
    """Assign a human agent to a conversation.

    Typically used after an escalation event. The assigned agent receives
    the conversation in their inbox and can communicate with the customer
    via the WebSocket channel.
    """
    repo = _get_repo()

    try:
        await repo.assign_agent(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            agent_id=request.agent_id,
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    now = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Agent assigned: conv=%s agent=%s tenant=%s",
        conversation_id,
        request.agent_id,
        ctx.tenant_id[:8],
    )

    return AssignAgentResponse(
        conversation_id=conversation_id,
        assigned_to=request.agent_id,
        assigned_at=now,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/notes — Add note
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/notes",
    response_model=AddNoteResponse,
    status_code=201,
)
async def add_note(
    conversation_id: str,
    request: AddNoteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AddNoteResponse:
    """Add an internal merchant note to a conversation.

    Notes are visible only to the merchant team — never shown to
    the customer. Useful for documenting context, escalation reasons,
    or follow-up actions.
    """
    repo = _get_repo()

    now = datetime.now(timezone.utc).isoformat()
    note_id = str(uuid.uuid4())

    note = {
        "note_id": note_id,
        "author": request.author or ctx.auth_method,
        "content": request.content,
        "created_at": now,
    }

    try:
        await repo.add_internal_note(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            note=note,
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    logger.info(
        "Note added: conv=%s note=%s tenant=%s",
        conversation_id,
        note_id,
        ctx.tenant_id[:8],
    )

    return AddNoteResponse(
        conversation_id=conversation_id,
        note_id=note_id,
        created_at=now,
    )
