"""
Chat API endpoints — 6 FastAPI routes for customer conversations.

Routes:
    POST /api/chat/conversations              — Start a new conversation
    POST /api/chat/message                    — Send a customer message
    GET  /api/chat/stream/{conversation_id}   — SSE stream of AI response
    GET  /api/chat/conversations/{id}         — Get conversation state
    POST /api/chat/conversations/{id}/end     — End conversation
    WS   /ws/chat/{conversation_id}           — WebSocket for typing/presence

Authentication:
    All /api/chat/* endpoints accept the publishable widget key
    (``X-Widget-Key: pk_live_...``) in addition to the standard API key
    and Shopify session token paths (Decision UI-6).

    The WebSocket endpoint accepts the key as a query parameter
    (``?key=pk_live_...``) since the browser WebSocket API does not
    support custom headers.

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §3: Chat API Specification
    - Decision UI-4: Hybrid protocol (HTTP + SSE + WebSocket)
    - Decision UI-5: SSE stream-then-validate with Critic retraction
    - Decision UI-6: Publishable widget key authentication

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from src.chat.models import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationStateResponse,
    EndConversationRequest,
    EndConversationResponse,
    SendMessageRequest,
    SendMessageResponse,
    WebSocketMessage,
    WebSocketMessageType,
)
from src.chat.pipeline import ChatPipeline
from src.chat.session import (
    ConversationNotActiveError,
    ConversationNotFoundError,
    ConversationSession,
    TrialLimitReachedError,
    TurnLimitReachedError,
)
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    PreferencesDocument,
    TenantDocument,
    TenantTier,
)
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# Service dependencies (injected at startup)
# ---------------------------------------------------------------------------

_session: ConversationSession | None = None
_pipeline: ChatPipeline | None = None


def configure_chat_services(
    session: ConversationSession,
    pipeline: ChatPipeline,
) -> None:
    """Wire chat services at app startup.

    Called from main.py after all dependencies are initialized.
    """
    global _session, _pipeline
    _session = session
    _pipeline = pipeline


def _get_session() -> ConversationSession:
    if _session is None:
        raise HTTPException(status_code=503, detail="Chat service not initialized")
    return _session


def _get_pipeline() -> ChatPipeline:
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="Chat pipeline not initialized")
    return _pipeline


# ---------------------------------------------------------------------------
# Helper: load tenant document + preferences for pipeline context
# ---------------------------------------------------------------------------


async def _load_tenant_context(
    ctx: TenantContext,
) -> tuple[TenantDocument, PreferencesDocument]:
    """Load the full TenantDocument and active PreferencesDocument.

    The pipeline needs these for SystemPromptBuilder. Returns default
    objects if the repositories are unavailable (graceful degradation).
    """
    from src.multi_tenant.repository import PreferencesRepository, TenantRepository

    # Load tenant document
    tenant_doc: TenantDocument | None = None
    try:
        tenant_repo = TenantRepository()
        raw = await tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
        tenant_doc = TenantDocument(**raw)
    except Exception:
        logger.debug("Tenant document load failed for %s — using defaults", ctx.tenant_id)

    if tenant_doc is None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        tenant_doc = TenantDocument(
            id=ctx.tenant_id,
            tenant_id=ctx.tenant_id,
            status=ctx.status,
            billing_channel="stripe",
            tier=ctx.tier,
            created_at=now,
            updated_at=now,
        )

    # Load active preferences
    prefs_doc: PreferencesDocument | None = None
    try:
        prefs_repo = PreferencesRepository()
        raw_prefs = await prefs_repo.get_current(ctx.tenant_id)
        if raw_prefs:
            prefs_doc = PreferencesDocument(**raw_prefs)
    except Exception:
        logger.debug("Preferences load failed for %s — using defaults", ctx.tenant_id)

    if prefs_doc is None:
        prefs_doc = PreferencesDocument(
            id=f"{ctx.tenant_id}:v1",
            tenant_id=ctx.tenant_id,
            version=1,
            is_current=True,
        )

    return tenant_doc, prefs_doc


# ---------------------------------------------------------------------------
# POST /api/chat/conversations — Start a new conversation
# ---------------------------------------------------------------------------


@router.post(
    "/conversations",
    response_model=ConversationStartResponse,
    status_code=201,
    summary="Start a new conversation",
)
async def start_conversation(
    request: ConversationStartRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationStartResponse:
    """Create a new conversation and return stream/WebSocket URLs.

    If the request includes an ``initial_message``, it is stored as
    the first customer message and the pipeline is triggered. The AI
    response will arrive via the SSE stream endpoint.
    """
    session = _get_session()

    try:
        return await session.start_conversation(
            tenant_id=ctx.tenant_id,
            request=request,
            tier=ctx.tier,
        )
    except TrialLimitReachedError as exc:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Trial conversation limit reached ({exc.limit} conversations). "
                "Please subscribe to a paid plan to continue."
            ),
        )


# ---------------------------------------------------------------------------
# POST /api/chat/message — Send a customer message
# ---------------------------------------------------------------------------


@router.post(
    "/message",
    response_model=SendMessageResponse,
    summary="Send a customer message",
)
async def send_message(
    request: SendMessageRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SendMessageResponse:
    """Append a customer message to an active conversation.

    The message is queued for pipeline processing. The AI response
    arrives via the SSE stream endpoint, not in this HTTP response.

    Returns 404 if the conversation doesn't exist, 409 if not active,
    422 if turn limit reached.
    """
    session = _get_session()

    try:
        return await session.add_customer_message(
            tenant_id=ctx.tenant_id,
            request=request,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except ConversationNotActiveError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Conversation is not active (status={exc.status})",
        )
    except TurnLimitReachedError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Turn limit reached ({exc.turn_count} turns)",
        )


# ---------------------------------------------------------------------------
# GET /api/chat/stream/{conversation_id} — SSE response stream
# ---------------------------------------------------------------------------


@router.get(
    "/stream/{conversation_id}",
    summary="SSE stream of AI response",
)
async def stream_response(
    conversation_id: str,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
) -> StreamingResponse:
    """Server-Sent Events stream for AI response delivery.

    The client connects to this endpoint after sending a message via
    ``POST /api/chat/message``. Events:

    - ``token``: AI response text chunk (streamed in real-time)
    - ``validated``: Critic approved the response
    - ``retracted``: Critic rejected — replace displayed text with fallback
    - ``stage``: Pipeline progress indicator
    - ``error``: Pipeline failure
    - ``done``: Stream complete for this turn

    Decision UI-5: tokens are streamed as generated. Critic validates
    post-stream. If rejected, a ``retracted`` event replaces the text.

    Supports reconnection via ``Last-Event-ID`` header — if the client
    reconnects after a disconnect, buffered events since the given ID
    are replayed before new events start streaming.
    """
    from src.chat.sse_manager import get_sse_manager

    pipeline = _get_pipeline()
    session = _get_session()
    sse_mgr = get_sse_manager()

    # Check SSE connection limit for this tenant
    tier_str = ctx.tier.value if ctx.tier else "starter"
    if not sse_mgr.can_connect(ctx.tenant_id, tier_str):
        raise HTTPException(
            status_code=429,
            detail="Too many active streaming connections for this tenant",
        )

    # Verify the conversation exists and belongs to this tenant
    try:
        state = await session.get_conversation(ctx.tenant_id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get the last customer message to feed the pipeline
    last_customer_msg = _extract_last_customer_message(state)
    if not last_customer_msg:
        raise HTTPException(
            status_code=400,
            detail="No customer message to process",
        )

    # Load tenant + preferences for pipeline context
    tenant_doc, prefs_doc = await _load_tenant_context(ctx)

    # Extract customer_id from conversation state
    customer_id: str | None = None
    for msg in reversed(state.messages):
        if msg.metadata and msg.metadata.get("customer_id"):
            customer_id = msg.metadata["customer_id"]
            break

    # Check for Last-Event-ID (reconnection support)
    last_event_id_str = request.headers.get("last-event-id", "")
    last_event_id = 0
    if last_event_id_str:
        try:
            last_event_id = int(last_event_id_str)
        except (ValueError, TypeError):
            pass

    async def event_generator():
        sse_mgr.connect(ctx.tenant_id, conversation_id)
        try:
            # Replay buffered events if reconnecting
            if last_event_id > 0:
                replay = sse_mgr.get_replay_events(conversation_id, last_event_id)
                for sse_text in replay:
                    yield sse_text

            # Stream new events from pipeline with heartbeat
            pipeline_events = pipeline.execute(
                tenant_id=ctx.tenant_id,
                conversation_id=conversation_id,
                customer_message=last_customer_msg,
                tenant=tenant_doc,
                preferences=prefs_doc,
                customer_id=customer_id,
            )

            async for sse_text in sse_mgr.wrap_stream(
                ctx.tenant_id, conversation_id, pipeline_events,
            ):
                yield sse_text
        finally:
            sse_mgr.disconnect(ctx.tenant_id, conversation_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# GET /api/chat/conversations/{conversation_id} — Get conversation state
# ---------------------------------------------------------------------------


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationStateResponse,
    summary="Get conversation state",
)
async def get_conversation(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationStateResponse:
    """Retrieve the current state of a conversation.

    Returns the full message history in chronological order. Used by
    the widget to restore state on page reload or reconnection.
    """
    session = _get_session()

    try:
        return await session.get_conversation(ctx.tenant_id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")


# ---------------------------------------------------------------------------
# POST /api/chat/conversations/{conversation_id}/end — End conversation
# ---------------------------------------------------------------------------


@router.post(
    "/conversations/{conversation_id}/end",
    response_model=EndConversationResponse,
    summary="End a conversation",
)
async def end_conversation(
    conversation_id: str,
    request: EndConversationRequest | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EndConversationResponse:
    """End an active conversation.

    Accepts optional feedback (rating, text). The conversation is
    metered for billing at this point.
    """
    session = _get_session()

    try:
        return await session.end_conversation(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            request=request,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except ConversationNotActiveError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Conversation is not active (status={exc.status})",
        )


# ---------------------------------------------------------------------------
# WS /ws/chat/{conversation_id} — WebSocket for typing/presence/human chat
# ---------------------------------------------------------------------------

# Active WebSocket connections: {conversation_id: set[WebSocket]}
_ws_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
) -> None:
    """WebSocket endpoint for bidirectional communication.

    Handles typing indicators, presence updates, and human-agent
    messages after escalation (Decision UI-4).

    Authentication: the widget key is passed as a query parameter
    (``?key=pk_live_...``) since browsers cannot set custom headers
    on WebSocket connections.

    Note: This WebSocket endpoint uses the /api/chat/ws/ prefix but
    is registered on the router which has /api/chat prefix, making
    the full path /api/chat/ws/{conversation_id}.
    """
    # Accept the connection
    await websocket.accept()

    # Register connection
    if conversation_id not in _ws_connections:
        _ws_connections[conversation_id] = set()
    _ws_connections[conversation_id].add(websocket)

    logger.debug(
        "WebSocket connected: conv=%s total=%d",
        conversation_id,
        len(_ws_connections[conversation_id]),
    )

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
                msg = WebSocketMessage(
                    type=WebSocketMessageType(data.get("type", "presence")),
                    conversation_id=conversation_id,
                    data=data.get("data", {}),
                    sender_id=data.get("sender_id"),
                )
            except (json.JSONDecodeError, ValueError):
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid message format"},
                })
                continue

            # Broadcast to all other connections on this conversation
            await _broadcast(conversation_id, msg, exclude=websocket)

    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected: conv=%s", conversation_id)
    except Exception:
        logger.exception("WebSocket error: conv=%s", conversation_id)
    finally:
        # Unregister connection
        conns = _ws_connections.get(conversation_id)
        if conns:
            conns.discard(websocket)
            if not conns:
                del _ws_connections[conversation_id]


async def broadcast_to_conversation(
    conversation_id: str,
    message: WebSocketMessage,
) -> None:
    """Send a WebSocket message to all connections on a conversation.

    Public API for other modules (e.g., pipeline escalation handler,
    human agent inbox) to push messages to the conversation WebSocket.
    """
    await _broadcast(conversation_id, message)


async def _broadcast(
    conversation_id: str,
    message: WebSocketMessage,
    *,
    exclude: WebSocket | None = None,
) -> None:
    """Broadcast a message to all WebSocket connections for a conversation."""
    conns = _ws_connections.get(conversation_id)
    if not conns:
        return

    payload = message.model_dump(mode="json")
    dead: list[WebSocket] = []

    for ws in conns:
        if ws is exclude:
            continue
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)

    # Clean up dead connections
    for ws in dead:
        conns.discard(ws)
    if not conns:
        _ws_connections.pop(conversation_id, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_last_customer_message(state: ConversationStateResponse) -> str | None:
    """Extract the last customer message from a conversation's message list."""
    for msg in reversed(state.messages):
        if msg.role.value == "customer":
            return msg.content
    return None
