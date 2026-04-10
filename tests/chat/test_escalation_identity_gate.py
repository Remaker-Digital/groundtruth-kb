"""SPEC-1879 Phase 4: Escalation identity gate accepts verified phone OR email.

Tests that _run_escalation_side_effects allows escalation when:
- Only email is present
- Only verified phone is present (phone_verified=True)
- Both email and verified phone are present
- Phone present but NOT verified → blocks with email_required=True
- Neither → blocks with email_required=True

Also verifies:
- escalation_sent is always True after successful escalation (repeat-suppression)
- Customer-facing message adapts to identity channel (email vs phone)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


TENANT_ID = "test-tenant-001"
CONV_ID = "conv-gate-001"


def _build_mixin(conv_doc: dict | None = None, *, use_real_budget: bool = False):
    """Build a CriticEscalationMixin instance with mocked session.

    Args:
        conv_doc: Conversation document to return from _get_conversation.
        use_real_budget: When True, _call_escalation_handler is left as a real
            async method (AsyncMock) so that the budget actually awaits it.
            When False (default), it's a sync MagicMock for tests that only
            need to verify the identity gate logic.
    """
    from src.chat.pipeline.critic_escalation import CriticEscalationMixin

    obj = CriticEscalationMixin.__new__(CriticEscalationMixin)
    obj._session = AsyncMock()
    obj._session._get_conversation = AsyncMock(return_value=conv_doc)
    obj._session.escalate_conversation = AsyncMock()
    obj._session.find_best_agent_for_category = AsyncMock(return_value=None)
    obj._session.find_superadmin_email = AsyncMock(return_value=None)
    obj._session._repo = AsyncMock()
    obj._session._repo.patch_conversation = AsyncMock()
    if use_real_budget:
        # Keep _call_escalation_handler as an async callable so the budget
        # can properly await it through asyncio.wait_for().
        obj._call_escalation_handler = AsyncMock(return_value={
            "reason": "test",
            "urgency": "medium",
            "context_summary": "Budget path test",
            "category": "general_inquiry",
            "model": "test-model",
        })
    else:
        # Prevent unawaited-coroutine warning: with a MagicMock budget the
        # coroutine is never awaited, so use a sync MagicMock.
        obj._call_escalation_handler = MagicMock(return_value={"reason": "test"})
    return obj


def _make_conv_doc(
    identity_email: str | None = None,
    identity_phone: str | None = None,
    phone_verified: bool = False,
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
    if phone_verified:
        doc["phone_verified"] = True
    return doc


def _make_budget():
    return MagicMock()


def _make_real_budget(total_ms: int = 5000, stage_ms: int = 3000):
    """Create a real PipelineTimeoutBudget that awaits coroutines."""
    from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget
    return PipelineTimeoutBudget(
        total_deadline_ms=total_ms,
        stage_budgets_ms={"escalation-handler": stage_ms},
    )


def _make_trace():
    trace = MagicMock()
    trace.set_escalation = MagicMock()
    return trace


# ---------------------------------------------------------------------------
# Identity gate tests
# ---------------------------------------------------------------------------


class TestEscalationIdentityGate:
    """SPEC-1879 Phase 4: escalation gate accepts verified phone OR email."""

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
        assert "phone" in result["email_prompt"].lower()

    @pytest.mark.asyncio
    async def test_blocks_when_phone_not_verified(self):
        """Escalation blocked when phone is present but NOT verified."""
        mixin = _build_mixin(_make_conv_doc(
            identity_phone="+14155551234",
            phone_verified=False,
        ))
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
    async def test_allows_with_verified_phone_only(self):
        """Escalation proceeds when only verified phone is present (SPEC-1879 Phase 4)."""
        mixin = _build_mixin(_make_conv_doc(
            identity_phone="+14155551234",
            phone_verified=True,
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
    async def test_allows_with_both_email_and_verified_phone(self):
        """Escalation proceeds when both email and verified phone are present."""
        mixin = _build_mixin(_make_conv_doc(
            identity_email="customer@example.com",
            identity_phone="+14155551234",
            phone_verified=True,
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
        """The prompt mentions phone as an alternative when identity missing."""
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


class TestEscalationSentFlag:
    """Verify escalation_sent is always True after successful escalation."""

    @pytest.mark.asyncio
    async def test_escalation_sent_true_with_email(self):
        """escalation_sent=True when email bridge sends successfully."""
        mixin = _build_mixin(_make_conv_doc(identity_email="customer@example.com"))
        await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        # patch_conversation was called with escalation_sent=True
        patch_call = mixin._session._repo.patch_conversation
        assert patch_call.called
        patch_args = patch_call.call_args
        patch_data = patch_args[0][2] if len(patch_args[0]) > 2 else patch_args[1].get("patch", {})
        assert patch_data.get("escalation_sent") is True

    @pytest.mark.asyncio
    async def test_escalation_sent_true_with_verified_phone_only(self):
        """escalation_sent=True even when only phone (no email bridge)."""
        mixin = _build_mixin(_make_conv_doc(
            identity_phone="+14155551234",
            phone_verified=True,
        ))
        await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        patch_call = mixin._session._repo.patch_conversation
        assert patch_call.called
        patch_args = patch_call.call_args
        patch_data = patch_args[0][2] if len(patch_args[0]) > 2 else patch_args[1].get("patch", {})
        assert patch_data.get("escalation_sent") is True


class TestEscalationMessaging:
    """Customer-facing message adapts to identity channel."""

    @pytest.mark.asyncio
    async def test_email_message_mentions_email(self):
        """Email-path escalation message mentions email follow-up."""
        mixin = _build_mixin(_make_conv_doc(identity_email="customer@example.com"))
        # Mock email bridge to succeed
        with patch("src.chat.escalation_email.send_escalation_emails", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"agent": "sent"}
            mixin._session.find_superadmin_email = AsyncMock(return_value="admin@example.com")
            result = await mixin._run_escalation_side_effects(
                tenant_id=TENANT_ID,
                conversation_id=CONV_ID,
                customer_message="I need help",
                system_prompt="You are helpful.",
                budget=_make_budget(),
                trace=_make_trace(),
            )
        assert "email" in result["escalation_msg"].lower()

    @pytest.mark.asyncio
    async def test_phone_message_mentions_phone(self):
        """Phone-path escalation message mentions phone follow-up."""
        mixin = _build_mixin(_make_conv_doc(
            identity_phone="+14155551234",
            phone_verified=True,
        ))
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert "phone" in result["escalation_msg"].lower()
        assert "email" not in result["escalation_msg"].lower()

    @pytest.mark.asyncio
    async def test_no_email_bridge_generic_message(self):
        """When email exists but bridge fails, message is generic."""
        mixin = _build_mixin(_make_conv_doc(identity_email="customer@example.com"))
        # No superadmin email = no email bridge
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=_make_budget(),
            trace=_make_trace(),
        )
        assert result["email_required"] is False
        assert "as soon as possible" in result["escalation_msg"].lower()


class TestEscalationBudgetPath:
    """Exercises execute_with_budget success path with a real PipelineTimeoutBudget.

    Codex Phase 4 GO noted that existing tests use MagicMock for the budget,
    which silently discards the coroutine. These tests use a real budget so
    asyncio.wait_for actually awaits _call_escalation_handler.
    """

    @pytest.mark.asyncio
    async def test_real_budget_awaits_handler(self):
        """Real budget awaits _call_escalation_handler without coroutine warnings."""
        mixin = _build_mixin(
            _make_conv_doc(identity_email="customer@example.com"),
            use_real_budget=True,
        )
        budget = _make_real_budget()
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=budget,
            trace=_make_trace(),
        )
        # The handler was actually awaited through the budget
        mixin._call_escalation_handler.assert_awaited_once()
        assert result["email_required"] is False
        # Budget recorded the stage
        assert len(budget.stages) >= 1
        assert budget.stages[-1].stage == "escalation-handler"
        assert budget.stages[-1].succeeded is True

    @pytest.mark.asyncio
    async def test_real_budget_with_verified_phone(self):
        """Real budget path works with phone-only identity."""
        mixin = _build_mixin(
            _make_conv_doc(identity_phone="+14155551234", phone_verified=True),
            use_real_budget=True,
        )
        budget = _make_real_budget()
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=budget,
            trace=_make_trace(),
        )
        mixin._call_escalation_handler.assert_awaited_once()
        assert result["email_required"] is False
        assert "phone" in result["escalation_msg"].lower()

    @pytest.mark.asyncio
    async def test_real_budget_timeout_degrades_gracefully(self):
        """When budget expires, escalation still proceeds with defaults."""
        mixin = _build_mixin(
            _make_conv_doc(identity_email="customer@example.com"),
            use_real_budget=True,
        )

        # Make the handler take longer than the budget allows
        async def slow_handler(*args, **kwargs):
            await asyncio.sleep(10)
            return {"reason": "should not reach"}

        mixin._call_escalation_handler = slow_handler

        budget = _make_real_budget(total_ms=50, stage_ms=50)  # 50ms budget
        result = await mixin._run_escalation_side_effects(
            tenant_id=TENANT_ID,
            conversation_id=CONV_ID,
            customer_message="I need help",
            system_prompt="You are helpful.",
            budget=budget,
            trace=_make_trace(),
        )
        # Should degrade gracefully — escalation still proceeds with defaults
        assert result["email_required"] is False
