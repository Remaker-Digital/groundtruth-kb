"""P0 3-Tier Usage Consumption integration tests — §4.8 of COMPREHENSIVE-TEST-PLAN.md.

Test IDs: UC-01 through UC-10.

Validates the full 3-tier consumption pipeline:
    1. Included allowance (free with subscription tier)
    2. Pack balance (pre-purchased, FIFO oldest-first, 90-day expiry)
    3. Overage billing (Stripe Billing Meter)

Tests exercise stripe_usage.record_conversation(), stripe_packs.consume_pack_balance(),
and stripe_packs.credit_pack_balance() together to verify end-to-end metering.

Uses in-memory dev stores (stripe_usage._usage_counters, stripe_packs._pack_balances).
Stripe API calls are mocked out to avoid hitting the real Stripe API.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

import src.integrations.stripe_packs as packs_mod
import src.integrations.stripe_usage as usage_mod
from src.integrations.stripe_packs import (
    credit_pack_balance,
    consume_pack_balance,
    get_pack_balance,
)
from src.integrations.stripe_usage import (
    record_conversation,
    get_usage_summary,
    reset_usage,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CUSTOMER = "cus_usage_test_001"


# ---------------------------------------------------------------------------
# Fixture: clean in-memory stores before each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_stores():
    """Reset in-memory usage counters and pack balances before each test."""
    usage_mod._usage_counters.clear()
    packs_mod._pack_balances.clear()
    yield
    usage_mod._usage_counters.clear()
    packs_mod._pack_balances.clear()


@pytest.fixture
def mock_stripe_client():
    """Mock the Stripe client to prevent real API calls for meter events."""
    client_mock = MagicMock()
    client_mock.v1.billing.meter_events.create = MagicMock(return_value={"id": "evt_mock"})
    with patch.object(usage_mod, "_stripe_client", client_mock):
        with patch.object(usage_mod, "_get_client", return_value=client_mock):
            yield client_mock


# ===================================================================
# UC-01: Fresh Starter — first 1,000 conversations free
# ===================================================================


class TestIncludedAllowance:
    """UC-01, UC-04, UC-05: Conversations within included allowance are free."""

    @pytest.mark.unit
    async def test_starter_first_1000_free(self, mock_stripe_client):
        """UC-01: Starter tier — first 1,000 conversations consume no packs or overage."""
        # Record 999 conversations (within included 1,000)
        for _ in range(10):
            result = await record_conversation(_CUSTOMER, "starter", count=99)

        # 990 total — still within included allowance
        assert result.total_conversations == 990
        assert result.overage_conversations == 0
        assert result.pack_consumed == 0
        assert result.meter_event_sent is False

    @pytest.mark.unit
    async def test_professional_5000_included(self, mock_stripe_client):
        """UC-04: Professional tier — 5,000 included conversations."""
        result = await record_conversation(_CUSTOMER, "professional", count=5000)
        assert result.total_conversations == 5000
        assert result.overage_conversations == 0
        assert result.pack_consumed == 0
        assert result.meter_event_sent is False

    @pytest.mark.unit
    async def test_enterprise_20000_included(self, mock_stripe_client):
        """UC-05: Enterprise tier — 20,000 included conversations."""
        result = await record_conversation(_CUSTOMER, "enterprise", count=20000)
        assert result.total_conversations == 20000
        assert result.overage_conversations == 0
        assert result.meter_event_sent is False


# ===================================================================
# UC-02: Pack consumption after included allowance
# ===================================================================


class TestPackConsumption:
    """UC-02, UC-06, UC-07, UC-08: Pack balance consumed after included."""

    @pytest.mark.unit
    async def test_starter_1001_consumes_pack(self, mock_stripe_client):
        """UC-02: Starter at 1,001 — 1 conversation consumed from pack."""
        # Credit a pack
        credit_pack_balance(_CUSTOMER, "pack_1k", 1000)

        # Use up included allowance
        await record_conversation(_CUSTOMER, "starter", count=1000)

        # 1,001st conversation should consume from pack
        result = await record_conversation(_CUSTOMER, "starter", count=1)
        assert result.total_conversations == 1001
        assert result.pack_consumed == 1
        assert result.overage_conversations == 0
        assert result.meter_event_sent is False

    @pytest.mark.unit
    async def test_fifo_oldest_pack_consumed_first(self, mock_stripe_client):
        """UC-06: FIFO — oldest pack consumed before newer pack."""
        now = int(time.time())

        # Manually create two packs with different ages
        packs_mod._pack_balances[_CUSTOMER] = [
            {
                "pack_id": "pack_1k",
                "remaining": 100,
                "purchased_at": now - 86400 * 60,  # 60 days ago (older)
                "expires_at": now + 86400 * 30,     # 30 days left
            },
            {
                "pack_id": "pack_5k",
                "remaining": 500,
                "purchased_at": now - 86400 * 10,  # 10 days ago (newer)
                "expires_at": now + 86400 * 80,     # 80 days left
            },
        ]

        # Consume 150 — should take 100 from first (deplete), 50 from second
        consumed = consume_pack_balance(_CUSTOMER, 150)
        assert consumed == 150

        entries = packs_mod._pack_balances[_CUSTOMER]
        assert entries[0]["remaining"] == 0    # First pack depleted
        assert entries[1]["remaining"] == 450  # Second pack reduced by 50

    @pytest.mark.unit
    async def test_expired_pack_skipped(self, mock_stripe_client):
        """UC-07: 90-day-old expired pack is skipped during consumption."""
        now = int(time.time())

        packs_mod._pack_balances[_CUSTOMER] = [
            {
                "pack_id": "pack_1k",
                "remaining": 500,
                "purchased_at": now - 86400 * 100,  # 100 days ago
                "expires_at": now - 86400 * 10,      # Expired 10 days ago
            },
            {
                "pack_id": "pack_5k",
                "remaining": 200,
                "purchased_at": now - 86400 * 5,
                "expires_at": now + 86400 * 85,
            },
        ]

        consumed = consume_pack_balance(_CUSTOMER, 100)
        assert consumed == 100

        entries = packs_mod._pack_balances[_CUSTOMER]
        # Expired pack untouched
        assert entries[0]["remaining"] == 500
        # Active pack consumed
        assert entries[1]["remaining"] == 100

    @pytest.mark.unit
    async def test_multiple_packs_balance_tracking(self, mock_stripe_client):
        """UC-08: Multiple packs — correct balance tracking."""
        # Credit two packs
        credit_pack_balance(_CUSTOMER, "pack_1k", 1000)
        credit_pack_balance(_CUSTOMER, "pack_5k", 5000)

        balance = get_pack_balance(_CUSTOMER)
        assert balance["total_remaining"] == 6000
        assert len(balance["active_packs"]) == 2

        # Consume 1,200 (100% of first pack + 200 of second)
        consumed = consume_pack_balance(_CUSTOMER, 1200)
        assert consumed == 1200

        balance = get_pack_balance(_CUSTOMER)
        assert balance["total_remaining"] == 4800


# ===================================================================
# UC-03, UC-09: Overage billing to Stripe
# ===================================================================


class TestOverageBilling:
    """UC-03, UC-09: Stripe Billing Meter receives overage."""

    @pytest.mark.unit
    async def test_all_packs_expired_overage_to_stripe(self, mock_stripe_client):
        """UC-03: All packs expired → overage reported to Stripe Meter."""
        now = int(time.time())

        # Create an expired pack
        packs_mod._pack_balances[_CUSTOMER] = [
            {
                "pack_id": "pack_1k",
                "remaining": 500,
                "purchased_at": now - 86400 * 100,
                "expires_at": now - 86400 * 10,  # Expired
            },
        ]

        # Use up included allowance
        await record_conversation(_CUSTOMER, "starter", count=1000)

        # Next conversation should go to overage (no valid packs)
        result = await record_conversation(_CUSTOMER, "starter", count=1)
        assert result.total_conversations == 1001
        assert result.pack_consumed == 0
        assert result.overage_conversations == 1
        assert result.meter_event_sent is True

    @pytest.mark.unit
    async def test_stripe_meter_event_sent(self, mock_stripe_client):
        """UC-09: Stripe Billing Meter receives the overage report."""
        # Use up included allowance
        await record_conversation(_CUSTOMER, "starter", count=1000)

        # Trigger overage (no packs)
        result = await record_conversation(_CUSTOMER, "starter", count=5)
        assert result.overage_conversations == 5
        assert result.meter_event_sent is True

        # Verify the Stripe client was called
        mock_stripe_client.v1.billing.meter_events.create.assert_called_once()
        call_args = mock_stripe_client.v1.billing.meter_events.create.call_args[0][0]
        assert call_args["event_name"] == "conversation_overage"
        assert call_args["payload"]["stripe_customer_id"] == _CUSTOMER
        assert call_args["payload"]["value"] == "5"

    @pytest.mark.unit
    async def test_no_packs_overage_direct(self, mock_stripe_client):
        """UC-03 variant: No packs at all → direct overage after included."""
        await record_conversation(_CUSTOMER, "starter", count=1003)
        assert usage_mod._usage_counters[_CUSTOMER]["total"] == 1003

        summary = get_usage_summary(_CUSTOMER, "starter")
        assert summary.total_conversations == 1003
        assert summary.included_allowance == 1000
        assert summary.overage_conversations == 3
        assert summary.remaining_included == 0
        assert summary.usage_percent == 100.3


# ===================================================================
# UC-10: Cross-billing-period counter reset
# ===================================================================


class TestBillingPeriodReset:
    """UC-10: Billing period boundary resets counters."""

    @pytest.mark.unit
    async def test_counter_reset_at_period_boundary(self, mock_stripe_client):
        """UC-10: reset_usage() clears counters for new billing period."""
        # Accumulate usage
        await record_conversation(_CUSTOMER, "starter", count=500)
        assert usage_mod._usage_counters[_CUSTOMER]["total"] == 500

        # Reset (called by webhook on subscription renewal)
        reset_usage(_CUSTOMER)

        # Verify counters are zeroed
        counter = usage_mod._usage_counters[_CUSTOMER]
        assert counter["total"] == 0
        assert counter["reported"] == 0

        # New period starts fresh
        result = await record_conversation(_CUSTOMER, "starter", count=1)
        assert result.total_conversations == 1
        assert result.overage_conversations == 0

    @pytest.mark.unit
    async def test_reset_nonexistent_customer_no_error(self, mock_stripe_client):
        """UC-10 supplement: Resetting a customer with no usage is safe."""
        reset_usage("cus_nonexistent")  # Should not raise

    @pytest.mark.unit
    async def test_usage_summary_after_reset(self, mock_stripe_client):
        """UC-10 supplement: Summary reflects zero usage after reset."""
        await record_conversation(_CUSTOMER, "starter", count=800)
        reset_usage(_CUSTOMER)

        summary = get_usage_summary(_CUSTOMER, "starter")
        assert summary.total_conversations == 0
        assert summary.remaining_included == 1000
        assert summary.usage_percent == 0.0
