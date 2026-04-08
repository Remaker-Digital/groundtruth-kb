"""Admin Preview API — conversation preview with message insights (SPEC-1872).

Provides REST endpoints for operator-visible preview/test mode:

    POST /api/admin/preview/chat               — Send preview message (SSE stream + trace)
    GET  /api/admin/preview/{id}/trace          — Get full decision trace

Preview conversations are tagged is_test_mode=True and excluded from
production analytics and billing. Professional+ tier gate enforced.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/preview", tags=["admin-preview"])

# ---------------------------------------------------------------------------
# Tier gating
# ---------------------------------------------------------------------------

_TIER_ORDER = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
_REQUIRED_TIER = "professional"

DAILY_PREVIEW_LIMIT = 50


def _enforce_tier_gate(ctx: TenantContext) -> None:
    """Require professional+ tier. Platform admins bypass."""
    if ctx.is_platform_admin:
        return
    tenant_tier = ctx.tier.value if ctx.tier and hasattr(ctx.tier, "value") else (ctx.tier or "free")
    if _TIER_ORDER.get(str(tenant_tier), 0) < _TIER_ORDER[_REQUIRED_TIER]:
        raise HTTPException(
            status_code=403,
            detail="Preview mode requires Professional tier or above.",
        )


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class PreviewChatRequest(CamelCaseModel):
    """Request body for preview chat."""

    message: str = Field(..., min_length=1, max_length=4000)
    config_overrides: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Temporary config overrides for this preview (e.g. response_tone_preset, intent_confidence_threshold). Not "
            "persisted."
        ),
    )


class PreviewTraceResponse(CamelCaseModel):
    """Full decision trace for a preview conversation."""

    conversation_id: str
    trace: dict[str, Any]


# ---------------------------------------------------------------------------
# Daily limit tracking (in-memory, per-process)
# ---------------------------------------------------------------------------

_daily_counts: dict[str, tuple[str, int]] = {}  # tenant_id -> (date_str, count)


def _check_daily_limit(tenant_id: str) -> None:
    """Enforce DAILY_PREVIEW_LIMIT per tenant per day."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = tenant_id
    date_str, count = _daily_counts.get(key, ("", 0))
    if date_str != today:
        _daily_counts[key] = (today, 1)
        return
    if count >= DAILY_PREVIEW_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Daily preview limit ({DAILY_PREVIEW_LIMIT}) reached. Try again tomorrow.",
        )
    _daily_counts[key] = (today, count + 1)


# ---------------------------------------------------------------------------
# POST /api/admin/preview/chat
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    summary="Send a preview message through the AI pipeline",
    description="Runs the full pipeline in test mode with ResponseDecisionTrace attached.",
    response_class=StreamingResponse,
)
async def preview_chat(
    body: PreviewChatRequest,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
) -> StreamingResponse:
    """Execute a preview conversation turn.

    The response is an SSE stream identical to production chat, plus a
    final ``trace`` event carrying the full ResponseDecisionTrace JSON.
    The conversation is tagged is_test_mode=True and excluded from
    production analytics and billing.
    """
    _enforce_tier_gate(ctx)
    _check_daily_limit(ctx.tenant_id)

    # Late imports to avoid circular dependencies
    from src.chat.pipeline import ChatPipeline
    from src.chat.session import ConversationSession
    from src.multi_tenant.repository import PreferencesRepository, TenantRepository

    # Resolve tenant + preferences
    tenant_repo = TenantRepository()
    prefs_repo = PreferencesRepository()

    try:
        tenant_doc = await tenant_repo.read(ctx.tenant_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Conversation Preview is the safe sandbox: use draft config if pending
    # changes exist, otherwise fall back to active.  This lets admins test
    # configuration changes *before* activating them (owner decision S259).
    try:
        prefs_doc = await prefs_repo._get_draft_or_active(ctx.tenant_id)
    except Exception:
        prefs_doc = None

    if not prefs_doc:
        raise HTTPException(status_code=400, detail="No configuration found. Save your agent configuration first.")

    # Apply config overrides (temporary, not persisted)
    if body.config_overrides and prefs_doc:
        prefs_copy = dict(prefs_doc) if isinstance(prefs_doc, dict) else prefs_doc.copy()
        for key, value in body.config_overrides.items():
            if hasattr(prefs_copy, key):
                setattr(prefs_copy, key, value)
            elif isinstance(prefs_copy, dict):
                prefs_copy[key] = value
        prefs_doc = prefs_copy

    # Create a preview conversation
    session = ConversationSession()
    conversation_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())

    try:
        await session.create_conversation(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            customer_id=f"preview-{ctx.team_member_id or 'admin'}",
            is_test_mode=True,
        )
    except Exception as exc:
        logger.warning("Failed to create preview conversation: %s", exc)
        raise HTTPException(status_code=500, detail="Could not create preview conversation")

    # Add the preview message
    try:
        await session.add_customer_message(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            content=body.message,
        )
    except Exception as exc:
        logger.warning("Failed to add preview message: %s", exc)
        raise HTTPException(status_code=500, detail="Could not add message")

    # Run the pipeline
    pipeline = ChatPipeline()

    async def _stream_with_trace():
        """Yield pipeline SSE events, then a final trace event."""
        collected_trace: dict[str, Any] = {}

        async for event in pipeline.execute(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            customer_message=body.message,
            tenant=tenant_doc,
            preferences=prefs_doc,
            customer_id=f"preview-{ctx.team_member_id or 'admin'}",
            customer_verified=False,
            conversation_history=[],
            trace_id=trace_id,
            team_member_role=None,
            target_agent_id=None,
            staff_domain_tags=None,
        ):
            yield event

            # Capture the pipeline_trace from metadata update
            # The pipeline persists trace in the done event's data

        # After pipeline completes, read the stored trace
        try:
            state = await session.get_conversation(ctx.tenant_id, conversation_id)
            metadata = getattr(state, "metadata", None) or {}
            if isinstance(metadata, dict):
                collected_trace = metadata.get("pipeline_trace", {})
            # Also try to get the full decision trace
            pt = getattr(state, "pipeline_trace", None)
            if pt:
                collected_trace = pt
        except Exception:
            logger.debug("Could not read trace for preview %s", conversation_id)

        # Emit trace as final SSE event
        trace_data = json.dumps({"trace": collected_trace, "conversation_id": conversation_id})
        yield f"event: trace\ndata: {trace_data}\n\n"

    return StreamingResponse(
        _stream_with_trace(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Preview-Mode": "true",
            "X-Conversation-Id": conversation_id,
        },
    )


# ---------------------------------------------------------------------------
# GET /api/admin/preview/{conversation_id}/trace
# ---------------------------------------------------------------------------


@router.get(
    "/{conversation_id}/trace",
    summary="Get full decision trace for a preview conversation",
    response_model=PreviewTraceResponse,
)
async def get_preview_trace(
    conversation_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> PreviewTraceResponse:
    """Return the full ResponseDecisionTrace for a preview conversation.

    Only works for conversations tagged is_test_mode=True. Returns 404
    for production conversations (prevents info leakage).
    """
    _enforce_tier_gate(ctx)

    from src.chat.session import ConversationSession, ConversationNotFoundError

    session = ConversationSession()
    try:
        state = await session.get_conversation(ctx.tenant_id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Preview conversation not found")

    # Only allow trace access for test-mode conversations
    if not getattr(state, "is_test_mode", False):
        raise HTTPException(status_code=404, detail="Preview conversation not found")

    trace = getattr(state, "pipeline_trace", None) or {}

    return PreviewTraceResponse(
        conversation_id=conversation_id,
        trace=trace,
    )
