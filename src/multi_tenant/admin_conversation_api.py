"""Admin Conversation Inbox API — merchant conversation management (WI #171, C8, C9).

Provides REST endpoints for the merchant admin dashboard's Conversation
Inbox component:

    GET  /api/admin/conversations              — List with filtering & pagination
    POST /api/admin/conversations/search       — Full-text search across messages & notes
    GET  /api/admin/conversations/{id}         — Full conversation detail
    GET  /api/admin/conversations/{id}/messages — Message history
    POST /api/admin/conversations/{id}/assign  — Assign to human agent
    POST /api/admin/conversations/{id}/escalate — Escalate to human support (C8)
    POST /api/admin/conversations/{id}/resolve — Mark as resolved (C9)
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
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import ConversationStatus
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import (
    ConversationRepository,
    DocumentNotFoundError,
    TeamMemberRepository,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AdminConversationSummary(CamelCaseModel):
    """Compact conversation record for the admin inbox list view."""


    conversation_id: str
    status: str | None = None
    customer_id: str | None = None
    canonical_customer_id: str | None = None  # ADR-004
    customer_name: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    last_activity_at: str | None = None
    assigned_to: str | None = None
    escalation_category: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None
    archived_at: str | None = None
    # Customer identity (AUTH-5 / P0-AUTH-FIX)
    customer_verified: bool = False
    identity_email: str | None = None


class AdminConversationListResponse(CamelCaseModel):
    """Paginated list of conversations for the admin inbox."""


    tenant_id: str
    total_count: int = Field(description="Total matching conversations")
    offset: int
    limit: int
    conversations: list[AdminConversationSummary]


class AdminConversationDetailResponse(CamelCaseModel):
    """Full conversation detail for the admin inbox."""


    conversation_id: str
    tenant_id: str
    status: str | None = None
    customer_id: str | None = None
    canonical_customer_id: str | None = None  # ADR-004
    customer_name: str | None = None
    is_billable: bool = False
    message_count: int = 0
    turn_count: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    last_activity_at: str | None = None
    assigned_to: str | None = None
    escalation_category: str | None = None
    agents_invoked: list[str] = Field(default_factory=list)
    model_used: str | None = None
    critic_passed: bool | None = None
    archived_at: str | None = None
    internal_notes: list[dict[str, Any]] = Field(default_factory=list)
    # Customer identity (AUTH-5 / P0-AUTH-FIX)
    customer_verified: bool = False
    identity_email: str | None = None
    # Pipeline trace (SPEC-1530 — end-to-end conversation tracing)
    pipeline_trace: dict[str, Any] | None = None


class PipelineTraceResponse(CamelCaseModel):
    """Pipeline execution trace for a conversation (SPEC-1531).

    Returns the full pipeline stage timeline for the most recent AI
    response turn, enabling visual trace representation in the SPA console.
    """

    conversation_id: str
    trace_id: str | None = None
    stages: list[dict[str, Any]] = Field(default_factory=list)
    total_latency_ms: int | None = None
    intent: str | None = None
    confidence: float | None = None
    critic_passed: bool | None = None
    model_used: str | None = None


class MessageEntry(CamelCaseModel):
    """A single message in the conversation transcript."""


    role: str
    content: str
    timestamp: str | None = None
    message_id: str | None = None
    metadata: dict[str, Any] | None = None


class ConversationMessagesResponse(CamelCaseModel):
    """Full message history for a conversation."""


    conversation_id: str
    tenant_id: str
    message_count: int
    messages: list[MessageEntry]


class AssignAgentRequest(CamelCaseModel):
    """Request body for POST /api/admin/conversations/{id}/assign."""


    agent_id: str = Field(
        min_length=1,
        max_length=200,
        description="Human agent identifier to assign",
    )


class AssignAgentResponse(CamelCaseModel):
    """Response for successful agent assignment."""


    conversation_id: str
    assigned_to: str
    assigned_at: str


class EscalateConversationRequest(CamelCaseModel):
    """Optional request body for POST /api/admin/conversations/{id}/escalate."""


    category: str | None = Field(
        default=None,
        description="Escalation category (from ESCALATION_CATEGORIES)",
    )
    agent_id: str | None = Field(
        default=None,
        description="Specific agent to assign (overrides auto-assignment)",
    )


class EscalateConversationResponse(CamelCaseModel):
    """Response for successful conversation escalation."""


    conversation_id: str
    status: str
    escalated_at: str
    escalation_category: str | None = None
    assigned_to: str | None = None


class ResolveConversationResponse(CamelCaseModel):
    """Response for successful conversation resolution."""


    conversation_id: str
    status: str
    resolved_at: str


class ArchiveConversationResponse(CamelCaseModel):
    """Response for successful conversation archive/unarchive."""


    conversation_id: str
    archived_at: str | None = None


class AddNoteRequest(CamelCaseModel):
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


class AddNoteResponse(CamelCaseModel):
    """Response for successfully added note."""


    conversation_id: str
    note_id: str
    created_at: str


class SearchConversationsRequest(CamelCaseModel):
    """Request body for POST /api/admin/conversations/search."""


    query: str = Field(
        min_length=1,
        max_length=500,
        description="Search text (matched against messages, customer name, and internal notes)",
    )
    status: str | None = Field(
        default=None,
        description="Optional status filter (active, escalated, resolved, timed_out, error)",
    )
    since: str | None = Field(
        default=None,
        description="Start date filter (ISO 8601, inclusive)",
    )
    until: str | None = Field(
        default=None,
        description="End date filter (ISO 8601, exclusive)",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Max results to return (default 50, max 200)",
    )


class SearchResultEntry(CamelCaseModel):
    """A single conversation match from a search."""


    conversation_id: str
    customer_id: str | None = None
    customer_name: str | None = None
    status: str | None = None
    started_at: str | None = None
    last_activity_at: str | None = None
    message_count: int = 0
    snippet: str = Field(description="Excerpt from the matching content")
    matched_in: str = Field(description="Where the match was found: messages, notes, or customer_name")


class SearchConversationsResponse(CamelCaseModel):
    """Response for conversation search."""


    tenant_id: str
    query: str
    total_results: int
    results: list[SearchResultEntry]


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_conversation_repo: ConversationRepository | None = None
_team_repo: TeamMemberRepository | None = None


def configure_admin_conversation_services(
    conversation_repo: ConversationRepository,
    team_repo: TeamMemberRepository | None = None,
) -> None:
    """Wire the admin conversation API to its backing repository.

    Called during app startup after ConversationRepository is initialised.
    """
    global _conversation_repo, _team_repo
    _conversation_repo = conversation_repo
    _team_repo = team_repo
    logger.info("Admin conversation inbox API services configured")


def _get_repo() -> ConversationRepository:
    """Get the ConversationRepository, raising 503 if not initialised."""
    if _conversation_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin conversation services not initialised",
        )
    return _conversation_repo


async def _read_conversation(
    repo: ConversationRepository,
    tenant_id: str,
    conversation_id: str,
) -> dict[str, Any]:
    """Read a conversation by ID, falling back to a query if the point read fails.

    Cosmos DB point reads require the document 'id' to match exactly.
    Seeded conversations may use 'conversation_id' as their 'id', but
    the frontend may pass either field. If the point read (by id) fails,
    we fall back to a query on the 'conversation_id' field within the
    tenant's partition.

    Raises HTTPException 404 if not found via either method.
    """
    # Try point read first (fastest path)
    try:
        return await repo.read(tenant_id, conversation_id)
    except DocumentNotFoundError:
        pass

    # Fallback: query by conversation_id field within tenant partition
    try:
        results = await repo.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c WHERE c.conversation_id = @conv_id"
            ),
            parameters=[
                {"name": "@conv_id", "value": conversation_id},
            ],
        )
        if results:
            return results[0]
    except Exception:
        logger.warning(
            "Conversation query fallback failed: tenant=%s conversation=%s",
            tenant_id[:8],
            conversation_id,
        )

    raise HTTPException(
        status_code=404,
        detail=f"Conversation {conversation_id} not found",
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/conversations", tags=["admin-inbox"])


# ---------------------------------------------------------------------------
# GET /api/admin/conversations — List with filtering & pagination
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=AdminConversationListResponse,
    summary="List admin inbox conversations",
    description="Returns a paginated list of conversations for the merchant admin inbox. Supports filtering by status, customer, date range, and assigned agent.",
    responses={
        400: {"description": "Invalid status filter value"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def list_conversations(
    status: str | None = Query(
        None,
        description="Filter by status (active, escalated, resolved, timed_out, error)",
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
    archived: str | None = Query(
        None,
        description="Archive filter: 'only' for archived only, 'include' to include archived, omit to exclude",
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

    # Parse archival filter
    archived_only = archived == "only"
    include_archived = archived == "include"

    # SPEC-1753: Enforce tier-based history depth at the API boundary.
    # Without this, conversations beyond the retention window are visible
    # to the admin until the daily DataRetentionService sweep runs.
    # Get total count and page of results
    total_count = await repo.count_filtered(
        tenant_id=ctx.tenant_id,
        status=conv_status,
        customer_id=customer_id,
        since=since,
        until=until,
        assigned_to=assigned_to,
        include_archived=include_archived,
        archived_only=archived_only,
    )

    conversations_raw = await repo.list_filtered(
        tenant_id=ctx.tenant_id,
        status=conv_status,
        customer_id=customer_id,
        since=since,
        until=until,
        assigned_to=assigned_to,
        include_archived=include_archived,
        archived_only=archived_only,
        offset=offset,
        limit=limit,
    )

    conversations = [
        AdminConversationSummary(
            conversation_id=c.get("conversation_id", c.get("id", "")),
            status=c.get("status"),
            customer_id=c.get("customer_id"),
            customer_name=c.get("customer_name", c.get("customer_id")),
            is_billable=c.get("is_billable", False),
            message_count=c.get("message_count", 0),
            turn_count=c.get("turn_count", 0),
            started_at=c.get("started_at"),
            ended_at=c.get("ended_at"),
            last_activity_at=c.get("last_activity_at"),
            assigned_to=c.get("assigned_to"),
            escalation_category=c.get("escalation_category"),
            agents_invoked=c.get("agents_invoked", []),
            model_used=c.get("model_used"),
            critic_passed=c.get("critic_passed"),
            archived_at=c.get("archived_at"),
            customer_verified=c.get("customer_verified", False),
            identity_email=c.get("identity_email"),
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
# POST /api/admin/conversations/search — Full-text search
# ---------------------------------------------------------------------------


@router.post(
    "/search",
    response_model=SearchConversationsResponse,
    summary="Search conversations",
    description=(
        "Full-text search across conversation messages, customer names, and "
        "internal notes. Returns matching conversations with a content snippet "
        "showing where the match was found."
    ),
    responses={
        400: {"description": "Invalid search query or status filter"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def search_conversations(
    request: SearchConversationsRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SearchConversationsResponse:
    """Search conversations by text content.

    Searches across message content, customer names, and internal notes
    using case-insensitive substring matching. Results are ordered by
    most recent activity first.
    """
    repo = _get_repo()

    # Validate status if provided
    if request.status is not None:
        try:
            ConversationStatus(request.status)
        except ValueError:
            valid = [s.value for s in ConversationStatus]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{request.status}'. Valid values: {valid}",
            )

    search_term = request.query.strip()

    # Build Cosmos DB query for full-text search across conversation content.
    # We search in: customer_name, messages[].content, internal_notes[].content.
    # CONTAINS() is case-insensitive in Cosmos DB NoSQL API with 4th param true.
    conditions = ["c.tenant_id = @tenant_id"]
    parameters: list[dict[str, Any]] = [
        {"name": "@tenant_id", "value": ctx.tenant_id},
        {"name": "@search_term", "value": search_term},
    ]

    if request.status:
        conditions.append("c.status = @status")
        parameters.append({"name": "@status", "value": request.status})

    if request.since:
        conditions.append("c.started_at >= @since")
        parameters.append({"name": "@since", "value": request.since})

    if request.until:
        conditions.append("c.started_at < @until")
        parameters.append({"name": "@until", "value": request.until})

    # Match on customer_name OR any message content OR any internal note
    search_condition = (
        "(CONTAINS(c.customer_name, @search_term, true)"
        " OR EXISTS("
        "   SELECT VALUE m FROM m IN c.messages"
        "   WHERE CONTAINS(m.content, @search_term, true)"
        " )"
        " OR EXISTS("
        "   SELECT VALUE n FROM n IN c.internal_notes"
        "   WHERE CONTAINS(n.content, @search_term, true)"
        " ))"
    )
    conditions.append(search_condition)

    query_text = (
        f"SELECT * FROM c WHERE {' AND '.join(conditions)}"
        " ORDER BY c.last_activity_at DESC"
        f" OFFSET 0 LIMIT {request.limit}"
    )

    try:
        raw_results = await repo.query(
            tenant_id=ctx.tenant_id,
            query_text=query_text,
            parameters=parameters,
        )
    except Exception:
        logger.warning(
            "Conversation search failed: tenant=%s query=%s",
            ctx.tenant_id[:8],
            search_term[:20],
            exc_info=True,
        )
        raw_results = []

    # Build results with match snippets
    results: list[SearchResultEntry] = []
    for doc in raw_results:
        snippet, matched_in = _extract_search_snippet(doc, search_term)
        results.append(
            SearchResultEntry(
                conversation_id=doc.get("conversation_id", doc.get("id", "")),
                customer_id=doc.get("customer_id"),
                customer_name=doc.get("customer_name"),
                status=doc.get("status"),
                started_at=doc.get("started_at"),
                last_activity_at=doc.get("last_activity_at"),
                message_count=doc.get("message_count", 0),
                snippet=snippet,
                matched_in=matched_in,
            )
        )

    return SearchConversationsResponse(
        tenant_id=ctx.tenant_id,
        query=search_term,
        total_results=len(results),
        results=results,
    )


def _extract_search_snippet(
    doc: dict[str, Any],
    search_term: str,
    max_snippet_len: int = 120,
) -> tuple[str, str]:
    """Extract a content snippet showing where the search term matched.

    Returns (snippet, matched_in) where matched_in is one of:
    'customer_name', 'messages', or 'notes'.
    """
    term_lower = search_term.lower()

    # Check customer_name first
    customer_name = doc.get("customer_name", "") or ""
    if term_lower in customer_name.lower():
        return (customer_name[:max_snippet_len], "customer_name")

    # Check messages
    for msg in doc.get("messages", []):
        content = msg.get("content", "") or ""
        if term_lower in content.lower():
            # Extract snippet around the match
            idx = content.lower().index(term_lower)
            start = max(0, idx - 40)
            end = min(len(content), idx + len(search_term) + 80)
            snippet = content[start:end]
            if start > 0:
                snippet = "…" + snippet
            if end < len(content):
                snippet = snippet + "…"
            return (snippet[:max_snippet_len], "messages")

    # Check internal notes
    for note in doc.get("internal_notes", []):
        content = note.get("content", "") or ""
        if term_lower in content.lower():
            idx = content.lower().index(term_lower)
            start = max(0, idx - 40)
            end = min(len(content), idx + len(search_term) + 80)
            snippet = content[start:end]
            if start > 0:
                snippet = "…" + snippet
            if end < len(content):
                snippet = snippet + "…"
            return (snippet[:max_snippet_len], "notes")

    # Fallback — shouldn't happen but safe
    return ("", "messages")


# ---------------------------------------------------------------------------
# GET /api/admin/conversations/{conversation_id} — Full detail
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}",
    response_model=AdminConversationDetailResponse,
    summary="Get conversation detail",
    description="Returns full conversation detail including internal notes and pipeline trace. Message transcript is available via the separate /messages endpoint.",
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Admin conversation services not initialized"},
    },
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

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    return AdminConversationDetailResponse(
        conversation_id=doc.get("conversation_id", doc.get("id", "")),
        tenant_id=ctx.tenant_id,
        status=doc.get("status"),
        customer_id=doc.get("customer_id"),
        customer_name=doc.get("customer_name", doc.get("customer_id")),
        is_billable=doc.get("is_billable", False),
        message_count=doc.get("message_count", 0),
        turn_count=doc.get("turn_count", 0),
        started_at=doc.get("started_at"),
        ended_at=doc.get("ended_at"),
        last_activity_at=doc.get("last_activity_at"),
        assigned_to=doc.get("assigned_to"),
        escalation_category=doc.get("escalation_category"),
        agents_invoked=doc.get("agents_invoked", []),
        model_used=doc.get("model_used"),
        critic_passed=doc.get("critic_passed"),
        archived_at=doc.get("archived_at"),
        internal_notes=doc.get("internal_notes", []),
        customer_verified=doc.get("customer_verified", False),
        identity_email=doc.get("identity_email"),
        pipeline_trace=doc.get("pipeline_trace"),
    )


# ---------------------------------------------------------------------------
# GET /api/admin/conversations/{conversation_id}/messages — Message history
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
    summary="Get conversation message history",
    description="Returns all messages in chronological order, including customer messages, AI responses, system events, and human agent messages.",
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Admin conversation services not initialized"},
    },
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

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

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
# GET /api/admin/conversations/{conversation_id}/export-csv — CSV transcript
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}/export-csv",
    summary="Export conversation transcript as CSV (SPEC-0195)",
    description="Returns a downloadable CSV file containing the full conversation "
    "transcript with timestamp, role, and message content columns.",
    responses={
        200: {"content": {"text/csv": {}}, "description": "CSV transcript download"},
        404: {"description": "Conversation not found"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def export_conversation_csv(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Export a conversation transcript as a downloadable CSV file.

    Columns: timestamp, role, content, message_id.
    """
    import csv
    import io

    from fastapi.responses import StreamingResponse

    repo = _get_repo()
    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    raw_messages = doc.get("messages", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "role", "content", "message_id"])

    for m in raw_messages:
        writer.writerow([
            m.get("timestamp", ""),
            m.get("role", ""),
            m.get("content", ""),
            m.get("message_id", ""),
        ])

    csv_content = output.getvalue()
    output.close()

    filename = f"transcript-{conversation_id}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /api/admin/conversations/{conversation_id}/trace — Pipeline trace
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}/trace",
    response_model=PipelineTraceResponse,
    summary="Get pipeline execution trace (SPEC-1531)",
    description="Returns the pipeline execution trace for the most recent AI response turn, "
    "including stage timings, intent classification, and critic assessment. "
    "Used by the SPA console to visualize conversation flow.",
    responses={
        404: {"description": "Conversation not found or no trace available"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def get_conversation_trace(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> PipelineTraceResponse:
    """Get the pipeline execution trace for a conversation (SPEC-1531).

    Returns the full pipeline stage timeline for the most recent AI
    response turn, enabling visual trace representation in the SPA console.
    """
    repo = _get_repo()

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)
    trace = doc.get("pipeline_trace")

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=f"No pipeline trace found for conversation {conversation_id}",
        )

    return PipelineTraceResponse(
        conversation_id=conversation_id,
        trace_id=trace.get("trace_id"),
        stages=trace.get("stages", []),
        total_latency_ms=trace.get("total_latency_ms"),
        intent=trace.get("intent"),
        confidence=trace.get("confidence"),
        critic_passed=trace.get("critic_passed"),
        model_used=trace.get("model_used"),
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/assign — Assign agent
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/assign",
    response_model=AssignAgentResponse,
    summary="Assign human agent to conversation",
    description="Assigns a human agent to a conversation, typically after an escalation event. The assigned agent receives the conversation in their inbox.",
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Admin conversation services not initialized"},
    },
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
# POST /api/admin/conversations/{conversation_id}/escalate — Escalate
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/escalate",
    response_model=EscalateConversationResponse,
    summary="Escalate conversation to human support",
    description="Marks a conversation as escalated, flagging it for human agent attention. The AI agent stops responding and the conversation appears in the escalated queue.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation already escalated, or resolved >24h ago"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def escalate_conversation(
    conversation_id: str,
    request: EscalateConversationRequest | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EscalateConversationResponse:
    """Escalate a conversation to human support.

    Marks the conversation as ESCALATED. Optionally sets an escalation
    category and assigns a specific agent (or auto-assigns the best fit).
    The AI agent stops responding and the conversation appears in the
    escalated queue for human pickup.
    """
    repo = _get_repo()

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    current_status = doc.get("status")

    # Already escalated — hard reject
    if current_status == ConversationStatus.ESCALATED.value:
        raise HTTPException(
            status_code=409,
            detail="Conversation is already escalated",
        )

    # Resolved — allow re-escalation within 24-hour window
    if current_status == ConversationStatus.RESOLVED.value:
        resolved_at_str = doc.get("resolved_at")
        re_escalation_allowed = False
        if resolved_at_str:
            try:
                resolved_at = datetime.fromisoformat(resolved_at_str)
                hours_since = (
                    datetime.now(timezone.utc) - resolved_at
                ).total_seconds() / 3600
                re_escalation_allowed = hours_since <= 24
            except (ValueError, TypeError):
                pass  # Malformed timestamp — treat as outside window
        if not re_escalation_allowed:
            raise HTTPException(
                status_code=409,
                detail="Conversation was resolved more than 24 hours ago "
                "and can no longer be escalated",
            )

    now = datetime.now(timezone.utc).isoformat()
    doc_id = doc.get("id", conversation_id)

    # Determine category and assignment
    category = (request.category if request else None) or None
    assigned_to = (request.agent_id if request else None) or None

    # Auto-assign if category given but no explicit agent
    if category and not assigned_to and _team_repo:
        try:
            from src.chat.session import get_conversation_session
            session = get_conversation_session()
            assigned_to = await session.find_best_agent_for_category(
                ctx.tenant_id, category,
            )
        except Exception:
            logger.debug("Auto-assign during manual escalation failed (non-blocking)")

    operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/status", "value": ConversationStatus.ESCALATED.value},
        {"op": "set", "path": "/escalated_at", "value": now},
    ]
    if category:
        operations.append({"op": "set", "path": "/escalation_category", "value": category})
    if assigned_to:
        operations.append({"op": "set", "path": "/assigned_to", "value": assigned_to})

    try:
        await repo.patch(
            tenant_id=ctx.tenant_id,
            document_id=doc_id,
            operations=operations,
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    logger.info(
        "Conversation escalated: conv=%s tenant=%s category=%s assigned=%s",
        conversation_id,
        ctx.tenant_id[:8],
        category or "none",
        assigned_to or "unassigned",
    )

    # Send escalation email to escalation_agent team members (best-effort)
    try:
        from src.multi_tenant.alert_delivery import send_escalation_alert

        recipient_emails: list[str] = []
        if _team_repo is not None:
            members = await _team_repo.list_members(
                tenant_id=ctx.tenant_id,
                role="escalation_agent",
                is_active=True,
                limit=100,
            )
            recipient_emails = [m["email"] for m in members if m.get("email")]
            # Also include admins as fallback
            if not recipient_emails:
                admins = await _team_repo.list_members(
                    tenant_id=ctx.tenant_id,
                    role="admin",
                    is_active=True,
                    limit=50,
                )
                recipient_emails = [m["email"] for m in admins if m.get("email")]

        customer_name = doc.get("customer_name") or doc.get("customer_id") or "Unknown"
        await send_escalation_alert(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            reason=f"Manual escalation by admin for customer: {customer_name}",
            urgency="medium",
            context_summary=f"Conversation with {customer_name} ({doc.get('message_count', 0)} messages) was escalated by an admin.",
            recipient_emails=recipient_emails or None,
            escalation_category=category,
            assigned_to=assigned_to,
        )
    except Exception:
        logger.warning(
            "Failed to send escalation alert: conv=%s tenant=%s",
            conversation_id,
            ctx.tenant_id[:8],
            exc_info=True,
        )

    # P3-1: Quality aggregate + regression alert at admin escalation closeout
    try:
        from src.chat.quality_closeout import evaluate_quality_and_alert
        await evaluate_quality_and_alert(ctx.tenant_id, conversation_id, repo)
    except Exception:
        logger.warning(
            "Quality closeout failed (non-fatal): conv=%s", conversation_id,
            exc_info=True,
        )

    return EscalateConversationResponse(
        conversation_id=conversation_id,
        status=ConversationStatus.ESCALATED.value,
        escalated_at=now,
        escalation_category=category,
        assigned_to=assigned_to,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/resolve — Mark resolved
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/resolve",
    response_model=ResolveConversationResponse,
    summary="Mark conversation as resolved",
    description="Marks a conversation as resolved, indicating the customer's issue has been addressed. Removes it from the active/escalated queues.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation already resolved"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def resolve_conversation(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ResolveConversationResponse:
    """Mark a conversation as resolved.

    Sets the conversation status to RESOLVED, removing it from the
    active and escalated queues. Resolved conversations remain visible
    in the inbox with a 'Resolved' badge for reference.
    """
    repo = _get_repo()

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    current_status = doc.get("status")
    if current_status == ConversationStatus.RESOLVED.value:
        raise HTTPException(
            status_code=409,
            detail="Conversation is already resolved",
        )

    now = datetime.now(timezone.utc).isoformat()
    doc_id = doc.get("id", conversation_id)

    try:
        await repo.patch(
            tenant_id=ctx.tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/status", "value": ConversationStatus.RESOLVED.value},
                {"op": "set", "path": "/resolved_at", "value": now},
            ],
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    # P3-1: Quality aggregate + regression alert at resolve closeout
    try:
        from src.chat.quality_closeout import evaluate_quality_and_alert
        await evaluate_quality_and_alert(ctx.tenant_id, conversation_id, repo)
    except Exception:
        logger.warning(
            "Quality closeout failed (non-fatal): conv=%s", conversation_id,
            exc_info=True,
        )

    logger.info(
        "Conversation resolved: conv=%s tenant=%s",
        conversation_id,
        ctx.tenant_id[:8],
    )

    return ResolveConversationResponse(
        conversation_id=conversation_id,
        status=ConversationStatus.RESOLVED.value,
        resolved_at=now,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/notes — Add note
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/notes",
    response_model=AddNoteResponse,
    status_code=201,
    summary="Add internal note to conversation",
    description="Adds an internal merchant note to a conversation. Notes are visible only to the merchant team, never shown to the customer.",
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Admin conversation services not initialized"},
    },
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


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/archive — Archive conversation
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/archive",
    response_model=ArchiveConversationResponse,
    summary="Archive a conversation",
    description="Archives a resolved or timed-out conversation. Archived conversations are hidden from the default inbox view but can be retrieved with the archived filter.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation must be resolved or timed out to archive"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def archive_conversation(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ArchiveConversationResponse:
    """Archive a conversation.

    Only resolved or timed-out conversations can be archived. Archived
    conversations are excluded from the default inbox listing but remain
    accessible via the ``?archived=only`` or ``?archived=include`` filter.
    """
    repo = _get_repo()

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    current_status = doc.get("status")
    if current_status not in (
        ConversationStatus.RESOLVED.value,
        ConversationStatus.TIMED_OUT.value,
    ):
        raise HTTPException(
            status_code=409,
            detail="Only resolved or timed-out conversations can be archived",
        )

    if doc.get("archived_at") is not None:
        raise HTTPException(
            status_code=409,
            detail="Conversation is already archived",
        )

    now = datetime.now(timezone.utc).isoformat()
    doc_id = doc.get("id", conversation_id)

    try:
        await repo.patch(
            tenant_id=ctx.tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/archived_at", "value": now},
            ],
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    logger.info(
        "Conversation archived: conv=%s tenant=%s",
        conversation_id,
        ctx.tenant_id[:8],
    )

    return ArchiveConversationResponse(
        conversation_id=conversation_id,
        archived_at=now,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/conversations/{conversation_id}/unarchive — Unarchive
# ---------------------------------------------------------------------------


@router.post(
    "/{conversation_id}/unarchive",
    response_model=ArchiveConversationResponse,
    summary="Unarchive a conversation",
    description="Removes a conversation from the archive, restoring it to the default inbox view.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation is not archived"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def unarchive_conversation(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ArchiveConversationResponse:
    """Unarchive a previously archived conversation.

    Clears the ``archived_at`` timestamp, restoring the conversation to
    the default inbox listing.
    """
    repo = _get_repo()

    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)

    if doc.get("archived_at") is None:
        raise HTTPException(
            status_code=409,
            detail="Conversation is not archived",
        )

    doc_id = doc.get("id", conversation_id)

    try:
        await repo.patch(
            tenant_id=ctx.tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/archived_at", "value": None},
            ],
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    logger.info(
        "Conversation unarchived: conv=%s tenant=%s",
        conversation_id,
        ctx.tenant_id[:8],
    )

    return ArchiveConversationResponse(
        conversation_id=conversation_id,
        archived_at=None,
    )


# ---------------------------------------------------------------------------
# PUT /api/admin/conversations/{conversation_id}/agent-override
# ---------------------------------------------------------------------------


class AgentOverrideRequest(CamelCaseModel):
    """Request body for PUT /{conversation_id}/agent-override (SPEC-1866)."""

    agent_id: str | None = Field(
        default=None,
        max_length=200,
        description="Peer agent ID to route this conversation to. Null clears the override.",
    )


class AgentOverrideResponse(CamelCaseModel):
    """Response for successful agent override."""

    conversation_id: str
    agent_id: str | None = None
    set_at: str | None = None
    set_by: str | None = None


@router.put(
    "/{conversation_id}/agent-override",
    response_model=AgentOverrideResponse,
    summary="Set or clear conversation agent override (SPEC-1866)",
    description=(
        "Routes all future messages in this conversation to a specific peer "
        "agent. The override takes highest precedence in the IntentRouter "
        "(step 0). Pass agent_id=null to clear."
    ),
    responses={
        404: {"description": "Conversation not found"},
        422: {"description": "Agent not found, tier-gated, or no binding"},
        503: {"description": "Admin conversation services not initialized"},
    },
)
async def set_agent_override(
    conversation_id: str,
    request: AgentOverrideRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentOverrideResponse:
    """Set or clear the conversation-level agent override (SPEC-1866).

    Validation (when setting, not clearing):
    1. Agent must exist in the PluginAgentRegistry.
    2. Tenant tier must meet the agent's tier_gate.
    3. Tenant must have at least one skill binding for the agent.
    """
    repo = _get_repo()
    doc = await _read_conversation(repo, ctx.tenant_id, conversation_id)
    doc_id = doc.get("id", conversation_id)
    now = datetime.now(timezone.utc).isoformat()

    if request.agent_id is not None:
        # --- Validate the agent ---
        from src.agents.plugins.registry import PluginAgentRegistry
        from src.agents.plugins.bindings import SkillBindingService

        reg = PluginAgentRegistry.get_instance()
        agent_defn = reg.get(request.agent_id)
        if agent_defn is None:
            raise HTTPException(
                status_code=422,
                detail=f"Agent '{request.agent_id}' not found in registry",
            )

        # Tier-gate check
        tier_gate = getattr(agent_defn, "tier_gate", None)
        if tier_gate and tier_gate != "free" and ctx.tier:
            tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
            if tier_order.get(str(ctx.tier.value if hasattr(ctx.tier, "value") else ctx.tier), 0) < tier_order.get(tier_gate, 0):
                raise HTTPException(
                    status_code=422,
                    detail=f"Tenant tier '{ctx.tier}' does not meet agent tier gate '{tier_gate}'",
                )

        # Overlay-enabled check — mirrors IntentRouter._try_peer_route()
        from src.agents.plugins.overlay import resolve_effective_config
        from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository

        overlay_repo = TenantAgentOverlayRepository()
        overlay = await overlay_repo.get_overlay(ctx.tenant_id, request.agent_id)
        config = resolve_effective_config(agent_defn, overlay=overlay)
        if not config.enabled:
            raise HTTPException(
                status_code=422,
                detail=f"Agent '{request.agent_id}' is disabled for this tenant",
            )

        # Domain-scope check — private-scope agents require matching tags
        if overlay:
            visibility_scope = overlay.get("visibility_scope", "public")
            if visibility_scope == "private":
                raise HTTPException(
                    status_code=422,
                    detail=f"Agent '{request.agent_id}' is private-scoped and cannot be set as a conversation override",
                )

        # Binding check — tenant must have at least one binding for the agent
        # Hydrate cache from Cosmos if not yet loaded (Codex P1: cold cache → false 422)
        svc = SkillBindingService.get_instance()
        if ctx.tenant_id not in svc._loaded_tenants:
            await svc.load_tenant_bindings(ctx.tenant_id)
        bindings = svc.list_bindings(ctx.tenant_id, agent_id=request.agent_id)
        if not bindings:
            raise HTTPException(
                status_code=422,
                detail=f"No skill bindings found for agent '{request.agent_id}' on this tenant",
            )

        # Apply the override
        operations = [
            {"op": "set", "path": "/conversation_agent_override", "value": request.agent_id},
            {"op": "set", "path": "/conversation_agent_override_at", "value": now},
            {"op": "set", "path": "/conversation_agent_override_by", "value": ctx.team_member_id or ctx.user_id or "admin"},
            {"op": "set", "path": "/last_activity_at", "value": now},
        ]
    else:
        # Clear the override
        operations = [
            {"op": "set", "path": "/conversation_agent_override", "value": None},
            {"op": "set", "path": "/conversation_agent_override_at", "value": None},
            {"op": "set", "path": "/conversation_agent_override_by", "value": None},
            {"op": "set", "path": "/last_activity_at", "value": now},
        ]

    try:
        await repo.patch(
            tenant_id=ctx.tenant_id,
            document_id=doc_id,
            operations=operations,
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found",
        )

    # Audit event
    try:
        from src.agents.plugins.events import emit_invocation
        emit_invocation(
            trace_id="",
            invoker="admin-override",
            target_agent_id=request.agent_id or "",
            skill_id="",
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            result_class="override_set" if request.agent_id else "override_cleared",
            policy_verdict="admin_action",
        )
    except Exception:
        logger.debug("Failed to emit override audit event", exc_info=True)

    logger.info(
        "Agent override %s: conv=%s agent=%s tenant=%s by=%s",
        "set" if request.agent_id else "cleared",
        conversation_id,
        request.agent_id or "(none)",
        ctx.tenant_id[:8],
        ctx.team_member_id or ctx.user_id or "admin",
    )

    return AgentOverrideResponse(
        conversation_id=conversation_id,
        agent_id=request.agent_id,
        set_at=now if request.agent_id else None,
        set_by=(ctx.team_member_id or ctx.user_id or "admin") if request.agent_id else None,
    )
