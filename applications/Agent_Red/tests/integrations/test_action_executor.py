"""Tests for Action Executor with HITL Gating (SPEC-1769).

Tests cover: HITL policy evaluation, action submission with auto-approve and
pending states, approval/rejection flow, dispatch routing, audit logging,
rate limit handling, and tenant-level HITL overrides.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.integrations.action_executor import (
    AIAction,
    ActionExecutor,
    ActionStatus,
    ActionType,
    HITLPolicy,
)
from src.integrations.manifest import (
    Capability,
    IntegrationCategory,
    IntegrationManifest,
)
from src.integrations.models import (
    MessageDirection,
    NormalizedContact,
    NormalizedMessage,
    NormalizedOrder,
    NormalizedTicket,
    OrderStatus,
    RateLimitError,
    TicketStatus,
)
from src.integrations.registry import IntegrationRegistry


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset the singleton registry between tests."""
    IntegrationRegistry.reset()
    yield
    IntegrationRegistry.reset()


def _make_helpdesk_adapter() -> AsyncMock:
    """Create a mock helpdesk adapter with standard responses."""
    adapter = AsyncMock()
    adapter.get_ticket.return_value = NormalizedTicket(
        external_id="T-100", source="zendesk", subject="Test ticket",
        status=TicketStatus.OPEN,
    )
    adapter.add_reply.return_value = NormalizedMessage(
        external_id="M-200", source="zendesk",
        direction=MessageDirection.OUTBOUND, body_text="Reply sent",
    )
    adapter.update_status.return_value = NormalizedTicket(
        external_id="T-100", source="zendesk", subject="Test ticket",
        status=TicketStatus.RESOLVED,
    )
    adapter.add_tags.return_value = NormalizedTicket(
        external_id="T-100", source="zendesk", tags=["vip"],
    )
    adapter.assign_ticket.return_value = NormalizedTicket(
        external_id="T-100", source="zendesk",
        assignee=NormalizedContact(external_id="A-1", source="zendesk", name="Agent"),
    )
    adapter.create_ticket.return_value = NormalizedTicket(
        external_id="T-201", source="zendesk", subject="New ticket",
    )
    adapter.search_tickets.return_value = []
    adapter.health_check.return_value = True
    return adapter


def _make_ecommerce_adapter() -> AsyncMock:
    """Create a mock e-commerce adapter with standard responses."""
    adapter = AsyncMock()
    adapter.lookup_order.return_value = NormalizedOrder(
        external_id="ORD-500", source="shopify", order_number="#1001",
        status=OrderStatus.CONFIRMED, total=49.99,
    )
    adapter.lookup_customer.return_value = NormalizedContact(
        external_id="C-300", source="shopify", name="Jane Doe",
        email="jane@example.com",
    )
    adapter.search_products.return_value = [
        {"id": "P-1", "title": "Widget", "price": 9.99}
    ]
    adapter.process_refund.return_value = {
        "refund_id": "R-100", "amount": 49.99, "status": "processed",
    }
    return adapter


def _make_channel_adapter() -> AsyncMock:
    """Create a mock channel adapter."""
    adapter = AsyncMock()
    adapter.send_message.return_value = NormalizedMessage(
        external_id="SM-1", source="slack",
        direction=MessageDirection.OUTBOUND, body_text="Hello",
    )
    return adapter


def _register_mock(registry: IntegrationRegistry, integration_id: str, adapter: Any):
    """Register a mock adapter with a manifest."""
    category_map = {
        "zendesk": IntegrationCategory.HELPDESK,
        "shopify": IntegrationCategory.ECOMMERCE,
        "slack": IntegrationCategory.CHANNEL,
    }
    cat = category_map.get(integration_id, IntegrationCategory.HELPDESK)
    manifest = IntegrationManifest(
        integration_id=integration_id,
        display_name=integration_id.title(),
        category=cat,
        capabilities=frozenset(Capability),
    )
    registry.register(manifest, lambda tid: adapter)


def _make_executor(**kwargs) -> tuple[ActionExecutor, IntegrationRegistry]:
    """Create an ActionExecutor with registered mock adapters."""
    registry = IntegrationRegistry.get_instance()
    helpdesk = _make_helpdesk_adapter()
    ecommerce = _make_ecommerce_adapter()
    channel = _make_channel_adapter()
    _register_mock(registry, "zendesk", helpdesk)
    _register_mock(registry, "shopify", ecommerce)
    _register_mock(registry, "slack", channel)
    executor = ActionExecutor(registry, **kwargs)
    return executor, registry


# ---------------------------------------------------------------------------
# HITL policy tests
# ---------------------------------------------------------------------------


class TestHITLPolicy:
    """Tests for HITL policy evaluation."""

    def test_read_actions_never_require_hitl(self):
        executor, _ = _make_executor()
        for at in [
            ActionType.TICKET_LOOKUP,
            ActionType.ORDER_LOOKUP,
            ActionType.CUSTOMER_LOOKUP,
            ActionType.ARTICLE_SEARCH,
            ActionType.PRODUCT_SEARCH,
        ]:
            action = AIAction(
                tenant_id="t1", integration_id="zendesk", action_type=at,
            )
            assert not executor.requires_approval(action), f"{at} should not require approval"

    def test_write_actions_default_require_hitl(self):
        executor, _ = _make_executor()
        for at in [
            ActionType.REPLY_SEND,
            ActionType.STATUS_UPDATE,
            ActionType.TICKET_CREATE,
            ActionType.MESSAGE_SEND,
        ]:
            action = AIAction(
                tenant_id="t1", integration_id="zendesk", action_type=at,
            )
            assert executor.requires_approval(action), f"{at} should require approval"

    def test_refund_always_requires_hitl(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.REFUND_PROCESS,
        )
        assert executor.requires_approval(action)

    def test_refund_cannot_bypass_hitl_with_override(self):
        """ALWAYS policy cannot be downgraded by explicit hitl_required=False."""
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.REFUND_PROCESS,
            hitl_required=False,
        )
        assert executor.requires_approval(action)

    def test_explicit_hitl_required_true_overrides_never(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.TICKET_LOOKUP,
            hitl_required=True,
        )
        assert executor.requires_approval(action)

    def test_tenant_override_can_relax_default_policy(self):
        executor, _ = _make_executor(
            tenant_hitl_overrides={
                "t1": {ActionType.REPLY_SEND.value: HITLPolicy.NEVER}
            }
        )
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
        )
        assert not executor.requires_approval(action)

    def test_tenant_override_cannot_relax_always_policy(self):
        executor, _ = _make_executor(
            tenant_hitl_overrides={
                "t1": {ActionType.REFUND_PROCESS.value: HITLPolicy.NEVER}
            }
        )
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.REFUND_PROCESS,
        )
        assert executor.requires_approval(action)

    def test_optional_actions_default_no_hitl(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.NOTE_ADD,
        )
        assert not executor.requires_approval(action)


# ---------------------------------------------------------------------------
# Submission & execution tests
# ---------------------------------------------------------------------------


class TestActionSubmission:
    """Tests for action submission and execution flow."""

    @pytest.mark.asyncio
    async def test_auto_approved_read_executes_immediately(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.TICKET_LOOKUP,
            params={"ticket_id": "T-100"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED
        assert result.result["external_id"] == "T-100"

    @pytest.mark.asyncio
    async def test_hitl_gated_action_returns_pending(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-100", "body": "Hello"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.PENDING_APPROVAL

    @pytest.mark.asyncio
    async def test_order_lookup_returns_order_data(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.ORDER_LOOKUP,
            params={"order_id": "ORD-500"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED
        assert result.result["order_number"] == "#1001"

    @pytest.mark.asyncio
    async def test_customer_lookup(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.CUSTOMER_LOOKUP,
            params={"email": "jane@example.com"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED
        assert result.result["email"] == "jane@example.com"

    @pytest.mark.asyncio
    async def test_product_search(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.PRODUCT_SEARCH,
            params={"query": "widget"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED
        assert len(result.result["products"]) == 1

    @pytest.mark.asyncio
    async def test_unregistered_integration_fails(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="nonexistent",
            action_type=ActionType.TICKET_LOOKUP,
            params={"ticket_id": "T-1"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.FAILED
        assert "not registered" in result.error_message

    @pytest.mark.asyncio
    async def test_rate_limit_error_captured(self):
        registry = IntegrationRegistry.get_instance()
        adapter = AsyncMock()
        adapter.get_ticket.side_effect = RateLimitError(
            "Too many requests", integration_id="zendesk", retry_after_seconds=30.0,
        )
        _register_mock(registry, "zendesk", adapter)
        executor = ActionExecutor(registry)

        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.TICKET_LOOKUP,
            params={"ticket_id": "T-1"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.FAILED
        assert "Rate limited" in result.error_message


# ---------------------------------------------------------------------------
# Approval / rejection flow
# ---------------------------------------------------------------------------


class TestApprovalFlow:
    """Tests for approve/reject lifecycle."""

    @pytest.mark.asyncio
    async def test_approve_executes_pending_action(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-100", "body": "Approved reply"},
        )
        pending = await executor.submit(action)
        assert pending.status == ActionStatus.PENDING_APPROVAL

        result = await executor.approve(action.action_id, approved_by="agent@co.com")
        assert result.status == ActionStatus.COMPLETED
        assert result.approved_by == "agent@co.com"

    @pytest.mark.asyncio
    async def test_reject_marks_action_rejected(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.STATUS_UPDATE,
            params={"ticket_id": "T-100", "status": "resolved"},
        )
        await executor.submit(action)
        result = await executor.reject(
            action.action_id, rejected_by="supervisor", reason="Not appropriate",
        )
        assert result.status == ActionStatus.REJECTED
        assert "Not appropriate" in result.error_message

    @pytest.mark.asyncio
    async def test_approve_nonexistent_action_fails(self):
        executor, _ = _make_executor()
        result = await executor.approve("nonexistent-id")
        assert result.status == ActionStatus.FAILED
        assert "not found" in result.error_message

    @pytest.mark.asyncio
    async def test_reject_nonexistent_action_fails(self):
        executor, _ = _make_executor()
        result = await executor.reject("nonexistent-id")
        assert result.status == ActionStatus.FAILED

    @pytest.mark.asyncio
    async def test_get_pending_returns_only_unapproved(self):
        executor, _ = _make_executor()
        a1 = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-1", "body": "a"},
        )
        a2 = AIAction(
            tenant_id="t2", integration_id="zendesk",
            action_type=ActionType.TICKET_CREATE,
            params={"subject": "s", "body": "b"},
        )
        await executor.submit(a1)
        await executor.submit(a2)

        all_pending = executor.get_pending()
        assert len(all_pending) == 2

        t1_pending = executor.get_pending(tenant_id="t1")
        assert len(t1_pending) == 1
        assert t1_pending[0].action_id == a1.action_id

    @pytest.mark.asyncio
    async def test_approved_action_removed_from_pending(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-1", "body": "x"},
        )
        await executor.submit(action)
        assert len(executor.get_pending()) == 1

        await executor.approve(action.action_id)
        assert len(executor.get_pending()) == 0


# ---------------------------------------------------------------------------
# Dispatch routing tests
# ---------------------------------------------------------------------------


class TestDispatchRouting:
    """Tests for action dispatch to correct adapter methods."""

    @pytest.mark.asyncio
    async def test_note_add_calls_internal_reply(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.NOTE_ADD,
            params={"ticket_id": "T-100", "body": "Internal note"},
        )
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_tag_add_dispatches_correctly(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.TAG_ADD,
            params={"ticket_id": "T-100", "tags": ["vip", "urgent"]},
        )
        # TAG_ADD has OPTIONAL policy — auto-approved
        result = await executor.submit(action)
        assert result.status == ActionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_message_send_dispatches_to_channel(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="slack",
            action_type=ActionType.MESSAGE_SEND,
            params={"channel_id": "C123", "body": "Hello slack"},
        )
        # MESSAGE_SEND is DEFAULT HITL — goes to pending
        result = await executor.submit(action)
        assert result.status == ActionStatus.PENDING_APPROVAL

        # Approve and verify dispatch
        result = await executor.approve(action.action_id)
        assert result.status == ActionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_refund_requires_approval_then_executes(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="shopify",
            action_type=ActionType.REFUND_PROCESS,
            params={"order_id": "ORD-500", "amount": 49.99, "reason": "Defective"},
        )
        pending = await executor.submit(action)
        assert pending.status == ActionStatus.PENDING_APPROVAL

        result = await executor.approve(action.action_id, approved_by="manager")
        assert result.status == ActionStatus.COMPLETED
        assert result.result["refund_id"] == "R-100"


# ---------------------------------------------------------------------------
# Audit logging tests
# ---------------------------------------------------------------------------


class TestAuditLogging:
    """Tests for audit trail completeness."""

    @pytest.mark.asyncio
    async def test_auto_approved_action_has_audit_entries(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.TICKET_LOOKUP,
            params={"ticket_id": "T-100"},
        )
        await executor.submit(action)

        log = executor.get_audit_log(action_id=action.action_id)
        events = [e.event for e in log]
        assert "requested" in events
        assert "executed" in events

    @pytest.mark.asyncio
    async def test_hitl_action_has_full_lifecycle_audit(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-100", "body": "msg"},
        )
        await executor.submit(action)
        await executor.approve(action.action_id, approved_by="admin")

        log = executor.get_audit_log(action_id=action.action_id)
        events = [e.event for e in log]
        assert "requested" in events
        assert "pending_approval" in events
        assert "approved" in events
        assert "executed" in events

    @pytest.mark.asyncio
    async def test_rejected_action_audit(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="zendesk",
            action_type=ActionType.REPLY_SEND,
            params={"ticket_id": "T-100", "body": "msg"},
        )
        await executor.submit(action)
        await executor.reject(action.action_id, reason="Not allowed")

        log = executor.get_audit_log(action_id=action.action_id)
        events = [e.event for e in log]
        assert "rejected" in events

    @pytest.mark.asyncio
    async def test_failed_action_audit(self):
        executor, _ = _make_executor()
        action = AIAction(
            tenant_id="t1", integration_id="nonexistent",
            action_type=ActionType.TICKET_LOOKUP,
            params={"ticket_id": "T-1"},
        )
        await executor.submit(action)

        log = executor.get_audit_log(action_id=action.action_id)
        events = [e.event for e in log]
        assert "failed" in events

    @pytest.mark.asyncio
    async def test_audit_log_tenant_filter(self):
        executor, _ = _make_executor()
        for tid in ["t1", "t2"]:
            action = AIAction(
                tenant_id=tid, integration_id="zendesk",
                action_type=ActionType.TICKET_LOOKUP,
                params={"ticket_id": "T-100"},
            )
            await executor.submit(action)

        t1_log = executor.get_audit_log(tenant_id="t1")
        assert all(e.tenant_id == "t1" for e in t1_log)
        assert len(t1_log) >= 2  # requested + executed

    @pytest.mark.asyncio
    async def test_audit_log_limit(self):
        executor, _ = _make_executor()
        for _ in range(10):
            action = AIAction(
                tenant_id="t1", integration_id="zendesk",
                action_type=ActionType.TICKET_LOOKUP,
                params={"ticket_id": "T-100"},
            )
            await executor.submit(action)

        limited = executor.get_audit_log(limit=5)
        assert len(limited) == 5


# ---------------------------------------------------------------------------
# AIAction model tests
# ---------------------------------------------------------------------------


class TestAIActionModel:
    """Tests for the AIAction Pydantic model."""

    def test_action_id_auto_generated(self):
        a1 = AIAction(
            tenant_id="t1", integration_id="z", action_type=ActionType.TICKET_LOOKUP,
        )
        a2 = AIAction(
            tenant_id="t1", integration_id="z", action_type=ActionType.TICKET_LOOKUP,
        )
        assert a1.action_id != a2.action_id

    def test_default_values(self):
        action = AIAction(
            tenant_id="t1", integration_id="z",
            action_type=ActionType.TICKET_LOOKUP,
        )
        assert action.requested_by == "ai_agent"
        assert action.priority == "normal"
        assert action.hitl_required is None
        assert action.conversation_id == ""
        assert isinstance(action.created_at, datetime)
