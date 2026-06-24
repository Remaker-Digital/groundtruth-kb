"""SPEC-1872 conversation preview endpoint coverage."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.chat.session import ConversationNotFoundError
from src.multi_tenant.admin_preview_api import (
    PreviewChatRequest,
    _daily_counts,
    get_preview_trace,
    preview_chat,
)
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier

TENANT_ID = "t-preview-spec1872"


@dataclass
class PreviewPreferences:
    response_tone_preset: str = "friendly"
    intent_confidence_threshold: float = 0.65

    def copy(self) -> PreviewPreferences:
        return replace(self)


def _tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        tier=TenantTier.PROFESSIONAL,
        status=TenantStatus.ACTIVE,
        auth_method="user_api_key",
        team_member_id="admin-123",
    )


async def _collect_stream(response) -> str:
    chunks: list[str] = []
    async for chunk in response.body_iterator:
        if isinstance(chunk, bytes):
            chunks.append(chunk.decode("utf-8"))
        else:
            chunks.append(str(chunk))
    return "".join(chunks)


def _patch_preview_collaborators(
    *,
    prefs: PreviewPreferences | None = None,
    conversation_state: object | None = None,
):
    tenant_repo = MagicMock()
    tenant_repo.read = AsyncMock(return_value={"tenant_id": TENANT_ID, "name": "Preview Tenant"})

    prefs_repo = MagicMock()
    prefs_repo._get_draft_or_active = AsyncMock(return_value=prefs or PreviewPreferences())

    session = MagicMock()
    session.create_conversation = AsyncMock()
    session.add_customer_message = AsyncMock()
    session.get_conversation = AsyncMock(
        return_value=conversation_state
        or SimpleNamespace(
            is_test_mode=True,
            metadata={"pipeline_trace": {"detected_intent": "metadata_trace"}},
            pipeline_trace={
                "detected_intent": "shipping_question",
                "confidence": 0.91,
                "route_target": "knowledge_retrieval",
                "stage_latencies_ms": {"classify": 12, "generate": 44},
            },
        ),
    )

    pipeline = MagicMock()

    async def events():
        yield 'event: stage\ndata: {"stage":"classify"}\n\n'
        yield 'event: token\ndata: {"text":"Hello"}\n\n'

    pipeline.execute = MagicMock(return_value=events())

    return tenant_repo, prefs_repo, session, pipeline


@pytest.mark.asyncio
async def test_preview_chat_creates_test_mode_conversation_and_streams_trace() -> None:
    """Preview chat should exercise the live route while avoiding external IO."""
    _daily_counts.clear()
    original_prefs = PreviewPreferences()
    tenant_repo, prefs_repo, session, pipeline = _patch_preview_collaborators(
        prefs=original_prefs,
    )

    with (
        patch("src.multi_tenant.repository.TenantRepository", return_value=tenant_repo),
        patch("src.multi_tenant.repository.PreferencesRepository", return_value=prefs_repo),
        patch("src.chat.session.ConversationSession", return_value=session),
        patch("src.chat.pipeline.ChatPipeline", return_value=pipeline),
        patch(
            "src.multi_tenant.admin_preview_api.uuid.uuid4",
            side_effect=["conv-preview-123", "trace-preview-123"],
        ),
    ):
        response = await preview_chat(
            PreviewChatRequest(
                message="How long does shipping take?",
                config_overrides={
                    "response_tone_preset": "casual",
                    "intent_confidence_threshold": 0.8,
                },
            ),
            request=MagicMock(),
            ctx=_tenant_context(),
        )
        stream = await _collect_stream(response)

    session.create_conversation.assert_awaited_once_with(
        tenant_id=TENANT_ID,
        conversation_id="conv-preview-123",
        customer_id="preview-admin-123",
        is_test_mode=True,
    )
    session.add_customer_message.assert_awaited_once_with(
        tenant_id=TENANT_ID,
        conversation_id="conv-preview-123",
        content="How long does shipping take?",
    )

    execute_kwargs = pipeline.execute.call_args.kwargs
    assert execute_kwargs["tenant_id"] == TENANT_ID
    assert execute_kwargs["conversation_id"] == "conv-preview-123"
    assert execute_kwargs["customer_message"] == "How long does shipping take?"
    assert execute_kwargs["customer_id"] == "preview-admin-123"
    assert execute_kwargs["customer_verified"] is False
    assert execute_kwargs["conversation_history"] == []
    assert execute_kwargs["trace_id"] == "trace-preview-123"
    assert execute_kwargs["preferences"].response_tone_preset == "casual"
    assert execute_kwargs["preferences"].intent_confidence_threshold == 0.8
    assert original_prefs.response_tone_preset == "friendly"
    assert original_prefs.intent_confidence_threshold == 0.65

    assert response.headers["X-Preview-Mode"] == "true"
    assert response.headers["X-Conversation-Id"] == "conv-preview-123"
    assert "event: stage" in stream
    assert "event: token" in stream
    assert "event: trace" in stream
    assert '"conversation_id": "conv-preview-123"' in stream
    assert '"detected_intent": "shipping_question"' in stream
    assert '"stage_latencies_ms": {"classify": 12, "generate": 44}' in stream


@pytest.mark.asyncio
async def test_get_preview_trace_returns_trace_for_test_mode_conversation() -> None:
    trace = {
        "detected_intent": "order_status",
        "confidence": 0.87,
        "route_target": "support_agent",
    }
    _, _, session, _ = _patch_preview_collaborators(
        conversation_state=SimpleNamespace(is_test_mode=True, pipeline_trace=trace),
    )

    with patch("src.chat.session.ConversationSession", return_value=session):
        result = await get_preview_trace("conv-preview-123", ctx=_tenant_context())

    session.get_conversation.assert_awaited_once_with(TENANT_ID, "conv-preview-123")
    assert result.conversation_id == "conv-preview-123"
    assert result.trace == trace


@pytest.mark.asyncio
async def test_get_preview_trace_hides_production_conversations() -> None:
    _, _, session, _ = _patch_preview_collaborators(
        conversation_state=SimpleNamespace(
            is_test_mode=False,
            pipeline_trace={"detected_intent": "order_status"},
        ),
    )

    with (
        patch("src.chat.session.ConversationSession", return_value=session),
        pytest.raises(HTTPException) as exc_info,
    ):
        await get_preview_trace("conv-prod-123", ctx=_tenant_context())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_preview_trace_hides_missing_conversations() -> None:
    _, _, session, _ = _patch_preview_collaborators()
    session.get_conversation.side_effect = ConversationNotFoundError(
        "conv-missing",
        TENANT_ID,
    )

    with (
        patch("src.chat.session.ConversationSession", return_value=session),
        pytest.raises(HTTPException) as exc_info,
    ):
        await get_preview_trace("conv-missing", ctx=_tenant_context())

    assert exc_info.value.status_code == 404
