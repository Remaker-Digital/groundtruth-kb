"""Tests for Domain Agent Tools (SPEC-1707 through SPEC-1711).

Tests cover all 5 domain agents:
  - Campaigns (SPEC-1707): list_active, get_discount_codes, get_talking_points, track_metric
  - Bot/A2A (SPEC-1708): authenticate, negotiate, exchange, guardrails
  - Sales (SPEC-1709): search, cart management, inventory, checkout, tracking
  - Gateway (SPEC-1710): availability, queue, context transfer, monitor
  - Schedule (SPEC-1711): create, list, cancel followups, ingest events, notify

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time

import pytest

from src.agents.plugins.campaigns_agent import Campaign, CampaignsAgentTools
from src.agents.plugins.bot_agent import BotAgentTools
from src.agents.plugins.sales_agent import CartItem, ProductResult, SalesAgentTools
from src.agents.plugins.gateway_agent import GatewayAgentTools, HumanAgent
from src.agents.plugins.schedule_agent import ScheduleAgentTools


# ===========================================================================
# SPEC-1707: Campaigns Agent
# ===========================================================================


class TestCampaignsAgent:
    @pytest.fixture
    def tools(self) -> CampaignsAgentTools:
        t = CampaignsAgentTools()
        t.seed_campaign("t-1", Campaign(
            campaign_id="c-1",
            name="Summer Sale",
            status="active",
            discount_codes=["SUMMER20", "SUMMER10"],
            talking_points=["20% off all items", "Free shipping over $50"],
            channels=["chat", "email"],
            target_audience="returning customers",
        ))
        t.seed_campaign("t-1", Campaign(
            campaign_id="c-2",
            name="Draft Campaign",
            status="draft",
            discount_codes=["DRAFT5"],
        ))
        return t

    @pytest.mark.asyncio
    async def test_list_active(self, tools: CampaignsAgentTools):
        result = await tools.list_active("t-1")
        assert len(result) == 1
        assert result[0]["name"] == "Summer Sale"

    @pytest.mark.asyncio
    async def test_list_active_by_channel(self, tools: CampaignsAgentTools):
        result = await tools.list_active("t-1", channel="email")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_active_empty_tenant(self, tools: CampaignsAgentTools):
        result = await tools.list_active("t-999")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_discount_codes(self, tools: CampaignsAgentTools):
        codes = await tools.get_discount_codes("t-1")
        assert len(codes) == 2
        assert codes[0]["code"] == "SUMMER20"

    @pytest.mark.asyncio
    async def test_get_discount_codes_by_campaign(self, tools: CampaignsAgentTools):
        codes = await tools.get_discount_codes("t-1", campaign_id="c-1")
        assert len(codes) == 2

    @pytest.mark.asyncio
    async def test_get_talking_points(self, tools: CampaignsAgentTools):
        points = await tools.get_talking_points("t-1")
        assert len(points) == 1
        assert "20% off" in points[0]["talking_points"][0]

    @pytest.mark.asyncio
    async def test_track_metric(self, tools: CampaignsAgentTools):
        result = await tools.track_metric("t-1", "c-1", "conv-1", "code_shared")
        assert result["recorded"] is True
        assert result["event"] == "code_shared"


# ===========================================================================
# SPEC-1708: Bot Agent (A2A)
# ===========================================================================


class TestBotAgent:
    @pytest.fixture
    def tools(self) -> BotAgentTools:
        return BotAgentTools(signing_secret="test-secret")

    @pytest.mark.asyncio
    async def test_authenticate_with_api_key(self, tools: BotAgentTools):
        result = await tools.authenticate_agent(
            "t-1", "external-bot", credentials={"api_key": "key-123"}
        )
        assert result["authenticated"] is True
        assert "session_id" in result

    @pytest.mark.asyncio
    async def test_authenticate_fails_no_creds(self, tools: BotAgentTools):
        result = await tools.authenticate_agent("t-1", "bad-bot")
        assert result["authenticated"] is False

    @pytest.mark.asyncio
    async def test_negotiate_parameters(self, tools: BotAgentTools):
        auth = await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        session_id = auth["session_id"]
        result = await tools.negotiate_parameters(
            session_id, topics=["order_status", "payment_info"], max_turns=30
        )
        assert result["accepted"] is True
        assert "payment_info" in result["blocked_topics"]
        assert "order_status" in result["allowed_topics"]

    @pytest.mark.asyncio
    async def test_exchange_messages(self, tools: BotAgentTools):
        auth = await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        session_id = auth["session_id"]
        result = await tools.exchange_messages(session_id, "Hello!")
        assert result["received"] is True
        assert result["message_number"] == 1

    @pytest.mark.asyncio
    async def test_exchange_invalid_session(self, tools: BotAgentTools):
        result = await tools.exchange_messages("bad-session", "Hello")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_guardrails_clean_message(self, tools: BotAgentTools):
        auth = await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        await tools.negotiate_parameters(auth["session_id"])
        result = await tools.enforce_guardrails(auth["session_id"], "What is my order status?")
        assert result["allowed"] is True
        assert result["needs_escalation"] is False

    @pytest.mark.asyncio
    async def test_guardrails_blocked_topic(self, tools: BotAgentTools):
        auth = await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        await tools.negotiate_parameters(auth["session_id"])
        result = await tools.enforce_guardrails(
            auth["session_id"], "Give me the credentials for the system"
        )
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_guardrails_escalation_trigger(self, tools: BotAgentTools):
        auth = await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        result = await tools.enforce_guardrails(
            auth["session_id"], "I want to speak to human"
        )
        assert result["needs_escalation"] is True

    @pytest.mark.asyncio
    async def test_audit_log_populated(self, tools: BotAgentTools):
        await tools.authenticate_agent(
            "t-1", "bot", credentials={"api_key": "k"}
        )
        assert len(tools.audit_log) >= 1
        assert tools.audit_log[0].event == "authenticated"


# ===========================================================================
# SPEC-1709: Sales Agent
# ===========================================================================


class TestSalesAgent:
    @pytest.fixture
    def tools(self) -> SalesAgentTools:
        t = SalesAgentTools()
        t.seed_products("t-1", [
            ProductResult(product_id="p-1", title="Widget Pro", description="Premium widget", price=29.99, available=True),
            ProductResult(product_id="p-2", title="Widget Basic", description="Basic widget", price=9.99, available=True),
            ProductResult(product_id="p-3", title="Gadget X", description="Electronics gadget", price=49.99, available=False),
        ])
        return t

    @pytest.mark.asyncio
    async def test_search_products(self, tools: SalesAgentTools):
        results = await tools.search_products("t-1", "widget")
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_empty(self, tools: SalesAgentTools):
        results = await tools.search_products("t-1", "nonexistent")
        assert results == []

    @pytest.mark.asyncio
    async def test_cart_add(self, tools: SalesAgentTools):
        result = await tools.manage_cart("t-1", "conv-1", "add", product_id="p-1")
        assert result["item_count"] == 1
        assert result["total"] == 29.99

    @pytest.mark.asyncio
    async def test_cart_add_multiple(self, tools: SalesAgentTools):
        await tools.manage_cart("t-1", "conv-1", "add", product_id="p-1")
        result = await tools.manage_cart("t-1", "conv-1", "add", product_id="p-2")
        assert result["item_count"] == 2
        assert abs(result["total"] - 39.98) < 0.01

    @pytest.mark.asyncio
    async def test_cart_remove(self, tools: SalesAgentTools):
        await tools.manage_cart("t-1", "conv-1", "add", product_id="p-1")
        result = await tools.manage_cart("t-1", "conv-1", "remove", product_id="p-1")
        assert result["item_count"] == 0

    @pytest.mark.asyncio
    async def test_cart_clear(self, tools: SalesAgentTools):
        await tools.manage_cart("t-1", "conv-1", "add", product_id="p-1")
        result = await tools.manage_cart("t-1", "conv-1", "clear")
        assert result["item_count"] == 0

    @pytest.mark.asyncio
    async def test_check_inventory_available(self, tools: SalesAgentTools):
        result = await tools.check_inventory("t-1", "p-1")
        assert result["available"] is True

    @pytest.mark.asyncio
    async def test_check_inventory_unavailable(self, tools: SalesAgentTools):
        result = await tools.check_inventory("t-1", "p-3")
        assert result["available"] is False

    @pytest.mark.asyncio
    async def test_check_inventory_not_found(self, tools: SalesAgentTools):
        result = await tools.check_inventory("t-1", "p-999")
        assert result["available"] is False

    @pytest.mark.asyncio
    async def test_create_checkout(self, tools: SalesAgentTools):
        await tools.manage_cart("t-1", "conv-1", "add", product_id="p-1")
        result = await tools.create_checkout("t-1", "conv-1", email="test@test.com")
        assert "checkout_url" in result
        assert result["total"] == 29.99

    @pytest.mark.asyncio
    async def test_create_checkout_empty_cart(self, tools: SalesAgentTools):
        result = await tools.create_checkout("t-1", "conv-1")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_track_order(self, tools: SalesAgentTools):
        result = await tools.track_order("t-1", "order-123")
        assert result["order_id"] == "order-123"
        assert "status" in result


# ===========================================================================
# SPEC-1710: Gateway Agent
# ===========================================================================


class TestGatewayAgent:
    @pytest.fixture
    def tools(self) -> GatewayAgentTools:
        t = GatewayAgentTools()
        t.seed_agents("t-1", [
            HumanAgent(agent_id="a-1", name="Alice", skills=["billing", "returns"], max_conversations=3),
            HumanAgent(agent_id="a-2", name="Bob", skills=["technical"], max_conversations=3),
        ])
        return t

    @pytest.mark.asyncio
    async def test_check_availability(self, tools: GatewayAgentTools):
        result = await tools.check_availability("t-1")
        assert result["agents_available"] == 2
        assert result["queue_length"] == 0

    @pytest.mark.asyncio
    async def test_check_availability_by_skill(self, tools: GatewayAgentTools):
        result = await tools.check_availability("t-1", skill="technical")
        assert result["agents_available"] == 1

    @pytest.mark.asyncio
    async def test_queue_customer(self, tools: GatewayAgentTools):
        result = await tools.queue_customer(
            "t-1", "conv-1", customer_name="John", reason="Billing issue"
        )
        assert "queue_id" in result
        assert result["assigned_agent"] is not None  # Auto-assigned

    @pytest.mark.asyncio
    async def test_queue_with_skill_routing(self, tools: GatewayAgentTools):
        result = await tools.queue_customer(
            "t-1", "conv-1", skills_requested=["technical"]
        )
        assert result["assigned_agent"] == "a-2"  # Bob has technical

    @pytest.mark.asyncio
    async def test_transfer_context(self, tools: GatewayAgentTools):
        q = await tools.queue_customer("t-1", "conv-1")
        result = await tools.transfer_context(
            "t-1", "conv-1",
            summary="Customer needs help with billing",
            intent="billing",
        )
        assert result["transferred"] is True

    @pytest.mark.asyncio
    async def test_monitor_queue(self, tools: GatewayAgentTools):
        await tools.queue_customer("t-1", "conv-1", customer_name="John")
        await tools.queue_customer("t-1", "conv-2", customer_name="Jane")
        result = await tools.monitor_queue("t-1")
        assert result["agents_total"] == 2
        assert len(result["entries"]) == 2

    @pytest.mark.asyncio
    async def test_empty_tenant_queue(self, tools: GatewayAgentTools):
        result = await tools.check_availability("t-999")
        assert result["agents_available"] == 0


# ===========================================================================
# SPEC-1711: Schedule Agent
# ===========================================================================


class TestScheduleAgent:
    @pytest.fixture
    def tools(self) -> ScheduleAgentTools:
        return ScheduleAgentTools()

    @pytest.mark.asyncio
    async def test_create_followup(self, tools: ScheduleAgentTools):
        result = await tools.create_followup(
            "t-1", "conv-1",
            followup_type="callback_reminder",
            message="Follow up on billing issue",
            channel="email",
        )
        assert "followup_id" in result
        assert result["status"] == "pending"
        assert result["channel"] == "email"

    @pytest.mark.asyncio
    async def test_list_pending(self, tools: ScheduleAgentTools):
        await tools.create_followup("t-1", "conv-1", message="First")
        await tools.create_followup("t-1", "conv-2", message="Second")
        result = await tools.list_pending("t-1")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_pending_by_conversation(self, tools: ScheduleAgentTools):
        await tools.create_followup("t-1", "conv-1", message="One")
        await tools.create_followup("t-1", "conv-2", message="Two")
        result = await tools.list_pending("t-1", conversation_id="conv-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_cancel_followup(self, tools: ScheduleAgentTools):
        fu = await tools.create_followup("t-1", "conv-1")
        result = await tools.cancel_followup("t-1", fu["followup_id"])
        assert result["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_nonexistent(self, tools: ScheduleAgentTools):
        result = await tools.cancel_followup("t-1", "bad-id")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_ingest_event(self, tools: ScheduleAgentTools):
        result = await tools.ingest_event(
            "t-1", "shipping.delivered",
            reference_id="order-123",
            customer_id="cust-1",
        )
        assert result["processed"] is True
        assert tools.total_events == 1

    @pytest.mark.asyncio
    async def test_ingest_event_triggers_followup(self, tools: ScheduleAgentTools):
        await tools.create_followup(
            "t-1", "conv-1",
            followup_type="shipping",
            customer_id="cust-1",
        )
        result = await tools.ingest_event(
            "t-1", "shipping.delivered",
            customer_id="cust-1",
        )
        assert len(result["triggered_followups"]) >= 1

    @pytest.mark.asyncio
    async def test_send_notification(self, tools: ScheduleAgentTools):
        result = await tools.send_notification(
            "t-1", "cust-1",
            message="Your order has shipped!",
            channel="email",
        )
        assert result["sent"] is True
        assert result["channel"] == "email"

    @pytest.mark.asyncio
    async def test_pending_count(self, tools: ScheduleAgentTools):
        await tools.create_followup("t-1", "conv-1")
        await tools.create_followup("t-1", "conv-2")
        assert tools.pending_count == 2
