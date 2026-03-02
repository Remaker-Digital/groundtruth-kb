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
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from src.chat.models import (
    ConsentUpdateRequest,
    ConsentUpdateResponse,
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationStateResponse,
    EndConversationRequest,
    EndConversationResponse,
    IssueReportRequest,
    IssueReportResponse,
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
from src.multi_tenant.repository import PreferencesRepository

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
    description="Creates a new conversation and returns stream/WebSocket URLs. If an initial_message is included, it is stored as the first customer message and the pipeline is triggered.",
    responses={
        403: {"description": "Trial conversation limit reached"},
        503: {"description": "Chat service not initialized"},
    },
)
async def start_conversation(
    request: ConversationStartRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConversationStartResponse:
    """Create a new conversation and return stream/WebSocket URLs.

    If the request includes an ``initial_message``, it is stored as
    the first customer message and the pipeline is triggered. The AI
    response will arrive via the SSE stream endpoint.

    Returns 403 if the tenant's configuration is not active (never
    activated or explicitly deactivated). This prevents the widget
    from creating phantom conversation documents.
    """
    # --- Activation gate ---
    # Block conversation creation if the tenant has never activated or
    # has explicitly deactivated their configuration.
    try:
        prefs_repo = PreferencesRepository()
        active_prefs = await prefs_repo.get_active(ctx.tenant_id)
    except Exception:
        active_prefs = None

    if not active_prefs or not active_prefs.get("activated_at"):
        raise HTTPException(
            status_code=403,
            detail={"type": "not_active", "message": "This store has not been configured yet."},
        )

    if active_prefs.get("deactivated_at"):
        raise HTTPException(
            status_code=403,
            detail={"type": "not_active", "message": "Chat is currently disabled for this store."},
        )

    # --- Identity verification (AUTH-4 Shopify HMAC + AUTH-5 OTP token) ---
    # Track whether the customer's identity has been cryptographically verified.
    # Verified customers get full PCM access; unverified get limited context.
    customer_verified = False

    # AUTH-4: Shopify HMAC verification
    if request.visitor and request.visitor.hmac and request.visitor.customer_id:
        try:
            from src.multi_tenant.shopify_customer_verification import (
                verify_shopify_customer_hmac,
            )

            is_valid = await verify_shopify_customer_hmac(
                tenant_id=ctx.tenant_id,
                customer_id=request.visitor.customer_id,
                provided_hmac=request.visitor.hmac,
            )
            if is_valid:
                customer_verified = True
            else:
                logger.warning(
                    "Shopify HMAC failed: tenant=%s customer_id=%s — stripping identity",
                    ctx.tenant_id,
                    request.visitor.customer_id,
                )
                request.visitor = None
        except Exception:
            logger.exception("Shopify HMAC verification error — stripping identity")
            request.visitor = None

    # AUTH-5: OTP customer token verification
    if request.customer_token and not customer_verified:
        try:
            from src.multi_tenant.widget_otp_verification import decode_customer_token

            payload = decode_customer_token(request.customer_token)
            if payload and payload.get("tenant_id") == ctx.tenant_id:
                customer_verified = True
                # Ensure visitor identity matches the verified token
                if request.visitor:
                    token_email = payload.get("email", "")
                    if token_email and not request.visitor.email:
                        request.visitor.email = token_email
                    token_name = payload.get("name", "")
                    if token_name and not request.visitor.name:
                        request.visitor.name = token_name
                else:
                    # Create visitor from token claims
                    from src.chat.models import VisitorIdentity
                    request.visitor = VisitorIdentity(
                        email=payload.get("email"),
                        name=payload.get("name"),
                    )
                logger.info(
                    "OTP token verified: tenant=%s email=%s",
                    ctx.tenant_id,
                    payload.get("email", "?"),
                )
            else:
                logger.warning(
                    "OTP token invalid or tenant mismatch: tenant=%s",
                    ctx.tenant_id,
                )
        except Exception:
            logger.exception("OTP token verification error")

    # Attach verification status for session.start_conversation()
    request.metadata = request.metadata or {}
    request.metadata["customer_verified"] = customer_verified

    session = _get_session()

    try:
        response = await session.start_conversation(
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

    # WI-0771: Fire-and-forget profile warm-up.
    # Pre-fetch the customer profile into the pipeline cache while the
    # customer is still composing their first message. When execute()
    # runs, _load_customer_profile() will find a cache hit instead of
    # making a Cosmos DB round-trip.
    customer_id_for_warmup = (
        (request.visitor.customer_id or request.visitor.email)
        if request.visitor else None
    )
    if customer_id_for_warmup:
        try:
            pipeline = _get_pipeline()
            asyncio.create_task(
                pipeline.warm_up(ctx.tenant_id, customer_id_for_warmup, ctx.tier),
            )
        except Exception:
            pass  # Non-fatal — pipeline may not be initialized in tests

    return response


# ---------------------------------------------------------------------------
# POST /api/chat/message — Send a customer message
# ---------------------------------------------------------------------------


@router.post(
    "/message",
    response_model=SendMessageResponse,
    summary="Send a customer message",
    description="Appends a customer message to an active conversation. The AI response arrives via the SSE stream endpoint, not in this HTTP response.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation is not active"},
        422: {"description": "Turn limit reached"},
        503: {"description": "Chat service not initialized"},
    },
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
    description="Server-Sent Events stream for real-time AI response delivery. Supports reconnection via Last-Event-ID header. Events include token, validated, retracted, stage, error, and done.",
    responses={
        400: {"description": "No customer message to process"},
        404: {"description": "Conversation not found"},
        429: {"description": "Too many active streaming connections for tenant"},
        503: {"description": "Chat pipeline not initialized"},
    },
)
async def stream_response(
    conversation_id: str,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
    tab_id: str | None = Query(
        default=None,
        max_length=64,
        description="Browser tab identifier for multi-tab coordination (WI #133). "
        "Multiple tabs streaming the same conversation share a single connection "
        "slot. The widget generates a unique tab_id per browser tab.",
    ),
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

    WI #133: Pass ``tab_id`` query parameter for multi-tab coordination.
    Multiple tabs streaming the same conversation share one connection
    slot for concurrency limit purposes.
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

    # --- "Not configured" guard ---
    # If the tenant has never activated their configuration, return an
    # error event so the widget can show a friendly message.  Auto-activated
    # new tenants (provisioned with activated_at) won't trigger this.
    if not getattr(prefs_doc, "activated_at", None):
        logger.info(
            "Tenant %s has not activated config — returning not_configured",
            ctx.tenant_id[:8],
        )
        import json as _json

        async def _not_configured_stream():
            yield (
                f"event: error\n"
                f"data: {_json.dumps({'type': 'not_configured', 'message': 'This store has not been configured yet.'})}\n\n"
            )

        return StreamingResponse(
            _not_configured_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # P0-AUTH-FIX: Identity preprocessor — intercept email/OTP messages
    # before the AI pipeline. This keeps OTP mechanics deterministic.
    try:
        from src.chat.identity_preprocessor import preprocess_identity

        identity_result = await preprocess_identity(
            conversation_id=conversation_id,
            tenant_id=ctx.tenant_id,
            content=last_customer_msg,
        )

        if identity_result.action != "none":
            # Identity message handled — return system response via SSE
            # without invoking the AI pipeline.
            import json as _json_id

            sys_msg = identity_result.system_message or ""

            # Append system response to conversation as an AI message
            try:
                await session.add_system_identity_message(
                    tenant_id=ctx.tenant_id,
                    conversation_id=conversation_id,
                    content=sys_msg,
                )
            except Exception as exc:
                logger.warning("Failed to persist identity system message: %s", exc)

            async def _identity_stream():
                # Emit a synthetic stage event so the widget creates a
                # message bubble before we stream the token content.
                yield (
                    f"event: stage\n"
                    f"data: {_json_id.dumps({'stage': 'response-generator', 'status': 'started'})}\n\n"
                )
                yield f"event: token\ndata: {_json_id.dumps({'text': sys_msg})}\n\n"
                yield f"event: done\ndata: {_json_id.dumps({'reason': 'identity_preprocessor'})}\n\n"

            return StreamingResponse(
                _identity_stream(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        # If preprocessor returned a system_message with action="none",
        # it's an informational note (e.g., OTP send failure) — let AI handle
        # but we could inject context. For now, proceed normally.
    except ImportError:
        pass  # identity_preprocessor not available — proceed normally
    except Exception as exc:
        logger.warning("Identity preprocessor error (non-fatal): %s", exc)

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

    # Extract conversation history for multi-turn context
    conversation_history = _extract_conversation_history(state, max_messages=20)

    # SPEC-1530: Generate trace_id at API entry point for end-to-end tracing
    trace_id = uuid.uuid4().hex

    async def event_generator():
        sse_mgr.connect(ctx.tenant_id, conversation_id, tab_id=tab_id)
        try:
            # Replay buffered events if reconnecting
            if last_event_id > 0:
                replay = sse_mgr.get_replay_events(conversation_id, last_event_id)
                for sse_text in replay:
                    yield sse_text

            # Stream new events from pipeline with heartbeat
            # P0-AUTH-FIX: Pass customer_verified so the orchestrator can
            # determine if in-conversation OTP verification has already
            # identified this customer (suppresses identity collection rules).
            pipeline_events = pipeline.execute(
                tenant_id=ctx.tenant_id,
                conversation_id=conversation_id,
                customer_message=last_customer_msg,
                tenant=tenant_doc,
                preferences=prefs_doc,
                customer_id=customer_id,
                customer_verified=getattr(state, "customer_verified", False),
                conversation_history=conversation_history,
                trace_id=trace_id,  # SPEC-1530: end-to-end trace
                team_member_role=(
                    ctx.team_member_role.value
                    if ctx.team_member_role else None
                ),  # SPEC-1558: Co-pilot routing for team members
            )

            async for sse_text in sse_mgr.wrap_stream(
                ctx.tenant_id, conversation_id, pipeline_events,
            ):
                yield sse_text
        finally:
            sse_mgr.disconnect(ctx.tenant_id, conversation_id, tab_id=tab_id)

    # WI #133: Include tab count in response headers so the widget knows
    # whether other tabs are already streaming this conversation.
    tab_count = sse_mgr.get_tab_count(ctx.tenant_id, conversation_id)
    response_headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "X-Trace-Id": trace_id,  # SPEC-1530: trace ID in response headers
    }
    if tab_id is not None:
        response_headers["X-Tab-Count"] = str(tab_count + 1)  # Include this tab

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=response_headers,
    )


# ---------------------------------------------------------------------------
# GET /api/chat/stream/{conversation_id}/status — Stream status (WI #133)
# ---------------------------------------------------------------------------


@router.get(
    "/stream/{conversation_id}/status",
    summary="Check SSE stream status for a conversation",
    description="Returns the current streaming status for a conversation, including active tab count. "
    "Used by the widget for multi-tab coordination — a tab can check if another tab is already "
    "streaming before opening its own SSE connection.",
    responses={
        503: {"description": "SSE manager not initialized"},
    },
)
async def stream_status(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Check SSE stream status for multi-tab coordination (WI #133).

    Returns whether the conversation is actively streaming, how many
    tabs are connected, and whether the tenant has capacity for more
    connections.

    This is a lightweight poll endpoint — no database queries. The widget
    can call this before opening an SSE connection to decide whether to
    connect (new stream) or piggyback (share existing stream via
    BroadcastChannel API or localStorage).
    """
    from src.chat.sse_manager import get_sse_manager

    sse_mgr = get_sse_manager()
    tier_str = ctx.tier.value if ctx.tier else "starter"

    return {
        "conversation_id": conversation_id,
        "is_streaming": sse_mgr.is_conversation_active(ctx.tenant_id, conversation_id),
        "tab_count": sse_mgr.get_tab_count(ctx.tenant_id, conversation_id),
        "can_connect": sse_mgr.can_connect(ctx.tenant_id, tier_str),
        "active_connections": sse_mgr.get_active_count(ctx.tenant_id),
    }


# ---------------------------------------------------------------------------
# GET /api/chat/conversations/{conversation_id} — Get conversation state
# ---------------------------------------------------------------------------


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationStateResponse,
    summary="Get conversation state",
    description="Retrieves the current state of a conversation including the full message history in chronological order. Used by the widget to restore state on page reload.",
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Chat service not initialized"},
    },
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
    description="Ends an active conversation with optional feedback (rating, text). The conversation is metered for billing at this point.",
    responses={
        404: {"description": "Conversation not found"},
        409: {"description": "Conversation is not active"},
        503: {"description": "Chat service not initialized"},
    },
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
# POST /api/chat/conversations/{conversation_id}/issue — Report an issue
# ---------------------------------------------------------------------------


@router.post(
    "/conversations/{conversation_id}/issue",
    response_model=IssueReportResponse,
    summary="Report an issue with the conversation",
    description=(
        "Allows the customer to report an issue with the AI conversation "
        "to the merchant. This is a structured feedback mechanism — NOT a "
        "bug report to Agent Red (C7)."
    ),
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Chat service not initialized"},
    },
)
async def report_issue(
    conversation_id: str,
    request: IssueReportRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> IssueReportResponse:
    """Report an issue with an active or ended conversation.

    Stores the issue as a system message on the conversation and
    creates an audit log entry for the merchant to review.
    """
    import uuid
    from datetime import datetime, timezone

    session = _get_session()

    # Verify conversation exists for this tenant
    try:
        state = await session.get_state(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Generate issue ID
    issue_id = f"issue_{uuid.uuid4().hex[:12]}"

    # Store as a system message on the conversation
    from src.chat.models import ChatMessage, MessageRole

    issue_message = ChatMessage(
        role=MessageRole.SYSTEM,
        content=f"[Issue Report] Type: {request.issue_type} | Details: {request.details}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        message_id=issue_id,
        metadata={
            "type": "issue_report",
            "issue_type": request.issue_type,
            "details": request.details,
        },
    )

    # Persist via conversation repository (best-effort — don't fail the request)
    try:
        if session._conversation_repo:
            await session._conversation_repo.patch(
                ctx.tenant_id,
                conversation_id,
                [
                    {
                        "op": "add",
                        "path": "/messages/-",
                        "value": issue_message.model_dump(mode="json"),
                    }
                ],
            )
    except Exception:
        logger.warning(
            "Failed to persist issue report: conv=%s issue=%s",
            conversation_id,
            issue_id,
        )

    # Audit log entry
    try:
        from src.multi_tenant.repository import AuditLogRepository
        from src.multi_tenant.cosmos_schema import AuditEventType

        audit_repo = AuditLogRepository()
        await audit_repo.log_event(
            tenant_id=ctx.tenant_id,
            event_type=AuditEventType.SECURITY_EVENT,
            actor_id=f"customer:{conversation_id}",
            resource_type="conversation",
            resource_id=conversation_id,
            details={
                "action": "issue_reported",
                "issue_id": issue_id,
                "issue_type": request.issue_type,
                "details": request.details[:500],
            },
        )
    except Exception:
        logger.warning(
            "Failed to write audit log for issue report: conv=%s",
            conversation_id,
        )

    # SPEC-1611: Issue reports are handled as escalation requests.
    # Fire-and-forget — delivery failure must not block the response.
    try:
        import asyncio
        from src.multi_tenant.alert_delivery import send_escalation_alert

        _issue_label = request.issue_type.replace("_", " ").title()
        asyncio.ensure_future(
            send_escalation_alert(
                tenant_id=ctx.tenant_id,
                conversation_id=conversation_id,
                reason=f"Customer issue report: {_issue_label}",
                urgency="medium",
                context_summary=request.details[:500] if request.details else "",
            )
        )
    except Exception:
        logger.debug("Issue-report escalation alert skipped (alert service not configured)")

    return IssueReportResponse(
        conversation_id=conversation_id,
        issue_id=issue_id,
        accepted=True,
    )


# ---------------------------------------------------------------------------
# POST /api/chat/conversations/{conversation_id}/consent — Update consent (WI #87)
# ---------------------------------------------------------------------------


@router.post(
    "/conversations/{conversation_id}/consent",
    response_model=ConsentUpdateResponse,
    summary="Update customer memory consent",
    description=(
        "Records the customer's explicit consent choice for Persistent Customer "
        "Memory (Layers 2-4). Called by the widget consent banner when the tenant "
        "has consent_collection_enabled = true (WI #87)."
    ),
    responses={
        404: {"description": "Conversation not found"},
        503: {"description": "Chat service not initialized"},
    },
)
async def update_consent(
    conversation_id: str,
    request: ConsentUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConsentUpdateResponse:
    """Record customer consent choice for PCM vectorization.

    Updates the customer's consent_status on their CustomerProfileDocument.
    If the conversation has a verified customer_id, consent is stored
    permanently on the profile. Otherwise, consent is only recorded on
    the conversation document for this session.
    """
    from datetime import datetime, timezone

    from src.multi_tenant.cosmos_schema import ConsentStatus

    session = _get_session()

    # Validate consent_status value
    try:
        consent = ConsentStatus(request.consent_status)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid consent_status: must be 'granted' or 'denied'",
        )

    # Verify conversation exists
    try:
        state = await session.get_state(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now_iso = datetime.now(timezone.utc).isoformat()

    # Update customer profile if we have a customer_id
    customer_id = state.customer_id if hasattr(state, "customer_id") else None
    if customer_id:
        try:
            from src.multi_tenant.repository import CustomerProfileRepository

            profile_repo = CustomerProfileRepository()
            await profile_repo.patch(
                tenant_id=ctx.tenant_id,
                document_id=f"profile:{customer_id}",
                operations=[
                    {"op": "set", "path": "/consent_status", "value": consent.value},
                    {"op": "set", "path": "/consent_updated_at", "value": now_iso},
                ],
            )
        except Exception:
            logger.warning(
                "Failed to update customer consent on profile: tenant=%s customer=%s",
                ctx.tenant_id, customer_id,
            )

    # Also record on the conversation document
    try:
        if session._conversation_repo:
            await session._conversation_repo.patch(
                ctx.tenant_id,
                conversation_id,
                [
                    {"op": "set", "path": "/consent_status", "value": consent.value},
                    {"op": "set", "path": "/consent_updated_at", "value": now_iso},
                ],
            )
    except Exception:
        logger.warning(
            "Failed to record consent on conversation: conv=%s", conversation_id,
        )

    # Audit log
    try:
        from src.multi_tenant.cosmos_schema import AuditEventType
        from src.multi_tenant.repository import AuditLogRepository

        audit_repo = AuditLogRepository()
        await audit_repo.log_event(
            tenant_id=ctx.tenant_id,
            event_type=AuditEventType.CONSENT_CHANGED,
            actor_id=f"customer:{customer_id or conversation_id}",
            resource_type="customer_profile",
            resource_id=customer_id or conversation_id,
            details={
                "action": "consent_updated",
                "consent_status": consent.value,
                "conversation_id": conversation_id,
                "source": "widget_banner",
            },
        )
    except Exception:
        logger.warning("Failed to write consent audit log: conv=%s", conversation_id)

    return ConsentUpdateResponse(
        conversation_id=conversation_id,
        consent_status=consent.value,
        accepted=True,
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


def _extract_conversation_history(
    state: ConversationStateResponse,
    max_messages: int = 20,
) -> list[dict[str, str]]:
    """Extract prior conversation messages for multi-turn context.

    Returns a list of {"role": "user"|"assistant", "content": "..."} dicts
    suitable for inclusion in an OpenAI chat completion request.

    Excludes the LAST customer message (which is passed separately as the
    current turn) and caps at ``max_messages`` most recent messages to
    stay within token budget (~10 turns of conversation).

    Maps widget roles to OpenAI roles:
        customer → user
        ai       → assistant
        system   → (skipped — system messages are UI chrome, not conversation)
    """
    if not state.messages:
        return []

    # Find and exclude the last customer message (it's the current turn)
    all_msgs = list(state.messages)
    last_customer_idx = None
    for i in range(len(all_msgs) - 1, -1, -1):
        if all_msgs[i].role.value == "customer":
            last_customer_idx = i
            break

    # Build history from all messages except the last customer message
    history: list[dict[str, str]] = []
    for i, msg in enumerate(all_msgs):
        if i == last_customer_idx:
            continue  # Skip the current turn's message
        if msg.role.value == "customer":
            history.append({"role": "user", "content": msg.content})
        elif msg.role.value == "ai":
            history.append({"role": "assistant", "content": msg.content})
        # Skip "system" role messages — they are UI-level, not conversation

    # Cap to the most recent messages
    if len(history) > max_messages:
        history = history[-max_messages:]

    return history
