"""SPEC-1879 Phase 4: Escalation identity gate accepts phone OR email.

Tests that _run_escalation_side_effects allows escalation when:
- Only email is present
- Only phone is present
- Both email and phone are present
- Neither → blocks with email_required=True

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


TENANT_ID = "test-tenant-001"
CONV_ID = "conv-gate-001"


def _build_mixin(conv_doc: dict | None = None):
    """Build a CriticEscalationMixin instance with mocked session."""
    from src.chat.pipeline.critic_escalation import CriticEscalationMixin

    obj = CriticEscalationMixin.__new__(CriticEscalationMixin)
    obj._session = AsyncMock()
    obj._session._get_conversation = AsyncMock(return_value=conv_doc)
    obj._session.escalate_conversation = AsyncMock()
    obj._session.find_best_agent_for_category = AsyncMock(return_value=None)
    return obj


def _make_conv_doc(
    identity_email: str | None = None,
    identity_phone: str | None = None,
) -> dict:
    """Create a minimal conversation document."""
    doc: dict = {
        "id": CONV_ID,
        "tenant_id": TENANT_ID,
        "messages": [],
    }
    if identity_email is not None:
        doc["identity_email"] = identity_email
    if identity_phone is not None:
        doc["identity_phone"] = identity_phone
    return doc


def _make_budget():
    return MagicMock()


def _make_trace():
    trace = MagicMock()
    trace.set_escalation = MagicMock()
    return trace


# ---------------------------------------------------------------------------
# Identity gate tests
# ---------------------------------------------------------------------------


class TestEscalationIdentityGate:
    """SPEC-1879 Phase 4: escalation gate accepts phone OR email."""

    @pytest.mark.asyncio
    async def test_blocks_when_no_identity(self):
        """Escalation blocked when neither email nor phone collected."""
        mixin = _build_mixin(_make_conv_doc())
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is True
        assert "email" in result["email_prompt"].lower() or "phone" in result["email_prompt"].lower()

    @pytest.mark.asyncio
    async def test_allows_with_email_only(self):
        """Escalation proceeds when only email is present."""
        mixin = _build_mixin(_make_conv_doc(identity_email="customer@example.com"))
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is False

    @pytest.mark.asyncio
    async def test_allows_with_phone_only(self):
        """Escalation proceeds when only phone is present (SPEC-1879 Phase 4)."""
        mixin = _build_mixin(_make_conv_doc(identity_phone="+14155551234"))
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is False

    @pytest.mark.asyncio
    async def test_allows_with_both_email_and_phone(self):
        """Escalation proceeds when both email and phone are present."""
        mixin = _build_mixin(_make_conv_doc(
            identity_email="customer@example.com",
            identity_phone="+14155551234",
        ))
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is False

    @pytest.mark.asyncio
    async def test_blocks_when_conv_doc_missing(self):
        """Escalation blocked when conversation document cannot be read."""
        mixin = _build_mixin(None)
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is True

    @pytest.mark.asyncio
    async def test_prompt_mentions_phone(self):
        """The email prompt now mentions phone as an alternative."""
        mixin = _build_mixin(_make_conv_doc())
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert "phone" in result["email_prompt"].lower()
