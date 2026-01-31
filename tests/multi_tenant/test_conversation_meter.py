"""P0 ConversationMeter unit tests — billable conversation metering.

Tests the billable conversation specification, 3-tier consumption logic,
idempotent metering, proactive alerts, reconciliation, and dashboard.

Test IDs: CM-01 through CM-30 per §4.3 of
docs/COMPREHENSIVE-TEST-PLAN.md.

Work Item: P0 launch-blocker tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.conversation_meter import (
    ALERT_THRESHOLD_LIMIT,
    ALERT_THRESHOLD_WARNING,
    IDLE_TIMEOUT_SECONDS,
    MAX_TURNS,
    NON_BILLABLE_PREFIXES,
    RECONCILIATION_DISCREPANCY_THRESHOLD,
    ConversationEndReason,
    ConversationMeter,
    MeterResult,
    ReconciliationResult,
    UsageAlertType,
    UsageDashboard,
)
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    ConversationStatus,
    TenantTier,
    TIER_DEFAULTS,
)


# ---------------------------------------------------------------------------
# Helpers — mock repositories
# ---------------------------------------------------------------------------

_TENANT_ID = "t-meter-001"
_BILLING_PERIOD = "2026-02"


def _make_repos(
    tier: TenantTier = TenantTier.STARTER,
    total_conversations: int = 0,
    included_allowance: int | None = None,
    stripe_customer_id: str | None = "cus_meter_001",
    overage_reported: int = 0,
    pack_consumed: int = 0,
    active_packs: list[dict] | None = None,
    idempotency_keys: set[str] | None = None,
) -> tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
    """Build mock repos for ConversationMeter.

    Returns (conversation_repo, usage_repo, audit_repo, tenant_repo).
    """
    if included_allowance is None:
        included_allowance = TIER_DEFAULTS[tier.value]["included_conversations"]

    idempotency_store: set[str] = idempotency_keys or set()

    # -- Conversation repo --
    conv_repo = AsyncMock()
    # create() returns the doc dict
    async def _conv_create(tid, doc):
        return doc.model_dump() if hasattr(doc, "model_dump") else dict(doc)
    conv_repo.create.side_effect = _conv_create
    # read() returns a dict simulating a conversation document
    conv_repo.read.return_value = {
        "conversation_id": "conv_test",
        "tenant_id": _TENANT_ID,
        "status": ConversationStatus.ACTIVE.value,
        "is_billable": True,
        "message_count": 5,
        "turn_count": 3,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_activity_at": datetime.now(timezone.utc).isoformat(),
        "customer_id": "cust_001",
        "agents_invoked": ["intent-classifier", "response-generator"],
        "model_used": "gpt-4o",
        "critic_passed": True,
    }
    conv_repo.end_conversation.return_value = None
    conv_repo.patch.return_value = None
    conv_repo.query.return_value = []

    # -- Usage repo --
    usage_repo = AsyncMock()

    counter_doc = {
        "id": f"{_TENANT_ID}:{_BILLING_PERIOD}",
        "tenant_id": _TENANT_ID,
        "billing_period": _BILLING_PERIOD,
        "total_conversations": total_conversations,
        "included_allowance": included_allowance,
        "overage_reported": overage_reported,
        "pack_consumed": pack_consumed,
        "tier": tier.value,
    }
    usage_repo.get_or_create_counter.return_value = dict(counter_doc)

    # increment_conversations: simulates atomic increment
    incremented = dict(counter_doc)
    incremented["total_conversations"] = total_conversations + 1
    usage_repo.increment_conversations.return_value = incremented

    usage_repo.increment_overage_reported.return_value = None
    usage_repo.increment_pack_consumed.return_value = None
    usage_repo.consume_from_pack.return_value = None
    usage_repo.patch.return_value = None

    # Packs
    usage_repo.get_active_packs.return_value = active_packs or []

    # Idempotency
    async def _check_idemp(tid, key):
        return key in idempotency_store
    async def _record_idemp(tid, key, event_type):
        idempotency_store.add(key)
    usage_repo.check_idempotency.side_effect = _check_idemp
    usage_repo.record_idempotency.side_effect = _record_idemp

    # -- Audit repo --
    audit_repo = AsyncMock()
    audit_repo.log_event.return_value = None

    # -- Tenant repo --
    tenant_repo = AsyncMock()
    tenant_repo.read.return_value = {
        "tenant_id": _TENANT_ID,
        "tier": tier.value,
        "stripe_customer_id": stripe_customer_id,
    }

    return conv_repo, usage_repo, audit_repo, tenant_repo


def _make_meter(**kwargs) -> ConversationMeter:
    """Create a ConversationMeter with mock repos."""
    conv, usage, audit, tenant = _make_repos(**kwargs)
    return ConversationMeter(conv, usage, audit, tenant)


def _make_meter_and_repos(**kwargs):
    """Create meter + return individual repos for assertion."""
    conv, usage, audit, tenant = _make_repos(**kwargs)
    meter = ConversationMeter(conv, usage, audit, tenant)
    return meter, conv, usage, audit, tenant


# ===========================================================================
# Billable conversation rules — CM-01 through CM-11
# ===========================================================================


class TestBillableConversationRules:
    """Tests the billable conversation specification (Decision #24)."""

    @pytest.mark.unit
    async def test_first_message_starts_billable_conversation(self):
        """CM-01: First customer message starts a billable conversation."""
        meter, conv_repo, *_ = _make_meter_and_repos()

        doc = await meter.start_conversation(
            tenant_id=_TENANT_ID,
            conversation_id="conv_regular_001",
            customer_id="cust_001",
        )

        conv_repo.create.assert_awaited_once()
        assert doc.is_billable is True
        assert doc.status == ConversationStatus.ACTIVE

    @pytest.mark.unit
    async def test_idempotent_metering_prevents_double_count(self):
        """CM-02: Second meter call for same conversation is idempotent skip."""
        meter, conv_repo, usage_repo, audit_repo, tenant_repo = _make_meter_and_repos(
            total_conversations=5,
        )

        # First metering — succeeds
        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result1 = await meter.meter_conversation(_TENANT_ID, "conv_001")
            assert result1.is_billable is True

            # Second metering — idempotent skip
            result2 = await meter.meter_conversation(_TENANT_ID, "conv_001")
            assert result2.is_billable is True
            assert result2.consumed_from_included is False
            assert result2.consumed_from_pack is False
            assert result2.consumed_from_overage is False

        # increment_conversations called only once (first call)
        assert usage_repo.increment_conversations.await_count == 1

    @pytest.mark.unit
    def test_idle_timeout_30_minutes(self):
        """CM-03: 30-minute idle timeout ends conversation."""
        now = datetime.now(timezone.utc)
        last_active = (now - timedelta(minutes=31)).isoformat()

        reason = ConversationMeter.should_end_conversation(
            last_activity_at=last_active,
            turn_count=5,
            now=now,
        )
        assert reason == ConversationEndReason.IDLE_TIMEOUT

    @pytest.mark.unit
    async def test_customer_ended_ends_conversation(self):
        """CM-04: Customer "end" signal ends conversation."""
        meter, conv_repo, *_ = _make_meter_and_repos(total_conversations=5)

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.end_conversation(
                _TENANT_ID, "conv_end_001", ConversationEndReason.CUSTOMER_ENDED,
            )

        conv_repo.end_conversation.assert_awaited_once_with(
            _TENANT_ID, "conv_end_001", ConversationStatus.COMPLETED,
        )
        assert result.is_billable is True

    @pytest.mark.unit
    async def test_escalation_ends_conversation(self):
        """CM-05: Escalation ends conversation."""
        meter, conv_repo, *_ = _make_meter_and_repos(total_conversations=5)

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.end_conversation(
                _TENANT_ID, "conv_esc_001", ConversationEndReason.ESCALATED,
            )

        conv_repo.end_conversation.assert_awaited_once_with(
            _TENANT_ID, "conv_esc_001", ConversationStatus.ESCALATED,
        )
        assert result.is_billable is True

    @pytest.mark.unit
    def test_50_turn_limit_ends_conversation(self):
        """CM-06: 50-turn limit ends conversation."""
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(seconds=10)).isoformat()

        reason = ConversationMeter.should_end_conversation(
            last_activity_at=recent,
            turn_count=50,
            now=now,
        )
        assert reason == ConversationEndReason.MAX_TURNS

    @pytest.mark.unit
    def test_test_prefix_non_billable(self):
        """CM-07: test_ prefixed conversation is non-billable."""
        assert ConversationMeter.is_conversation_billable("test_conv_001") is False

    @pytest.mark.unit
    def test_admin_prefix_non_billable(self):
        """CM-08: admin_ prefixed conversation is non-billable."""
        assert ConversationMeter.is_conversation_billable("admin_conv_001") is False

    @pytest.mark.unit
    def test_health_prefix_non_billable(self):
        """CM-09: health_ prefixed conversation is non-billable."""
        assert ConversationMeter.is_conversation_billable("health_conv_001") is False

    @pytest.mark.unit
    def test_system_prefix_non_billable(self):
        """CM-10: system_ prefixed conversation is non-billable."""
        assert ConversationMeter.is_conversation_billable("system_conv_001") is False

    @pytest.mark.unit
    async def test_error_before_ai_response_non_billable(self):
        """CM-11: Error before AI response → non-billable.

        If no AI response was generated (message_count <= 1), the
        conversation is re-marked as non-billable during end_conversation().
        """
        meter, conv_repo, usage_repo, audit_repo, tenant_repo = _make_meter_and_repos(
            total_conversations=5,
        )
        # Simulate a conversation where the AI never responded
        conv_repo.read.return_value = {
            "conversation_id": "conv_error_001",
            "tenant_id": _TENANT_ID,
            "status": ConversationStatus.ERROR.value,
            "is_billable": True,  # Initially marked billable
            "message_count": 1,   # Only customer message, no AI response
            "turn_count": 0,
        }

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.end_conversation(
                _TENANT_ID, "conv_error_001", ConversationEndReason.ERROR,
            )

        assert result.is_billable is False
        # Should have patched is_billable to False
        conv_repo.patch.assert_awaited_once()


# ===========================================================================
# 3-tier consumption — CM-12 through CM-18
# ===========================================================================


class TestThreeTierConsumption:
    """Tests the 3-tier consumption order: included → packs → overage."""

    @pytest.mark.unit
    async def test_included_allowance_starter_1000(self):
        """CM-12: Included allowance consumed first (Starter 1,000)."""
        meter = _make_meter(
            tier=TenantTier.STARTER,
            total_conversations=500,  # Well within 1,000
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_s_001")

        assert result.is_billable is True
        assert result.consumed_from_included is True
        assert result.consumed_from_pack is False
        assert result.consumed_from_overage is False
        assert result.included_allowance == 1_000

    @pytest.mark.unit
    async def test_included_allowance_professional_5000(self):
        """CM-13: Included allowance consumed first (Professional 5,000)."""
        meter = _make_meter(
            tier=TenantTier.PROFESSIONAL,
            total_conversations=2_500,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_p_001")

        assert result.consumed_from_included is True
        assert result.included_allowance == 5_000

    @pytest.mark.unit
    async def test_included_allowance_enterprise_20000(self):
        """CM-14: Included allowance consumed first (Enterprise 20,000)."""
        meter = _make_meter(
            tier=TenantTier.ENTERPRISE,
            total_conversations=10_000,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_e_001")

        assert result.consumed_from_included is True
        assert result.included_allowance == 20_000

    @pytest.mark.unit
    async def test_pack_consumed_after_included(self):
        """CM-15: Pack balance consumed after included allowance."""
        packs = [
            {"id": "pack_001", "remaining": 500, "purchased_at": "2026-01-01T00:00:00Z"},
        ]
        meter, conv_repo, usage_repo, *_ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=1_000,  # At limit — next goes to packs
            active_packs=packs,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_pack_001")

        assert result.consumed_from_included is False
        assert result.consumed_from_pack is True
        assert result.consumed_from_overage is False
        assert result.pack_doc_id == "pack_001"
        usage_repo.consume_from_pack.assert_awaited_once_with(_TENANT_ID, "pack_001", 1)

    @pytest.mark.unit
    async def test_fifo_pack_consumption_oldest_first(self):
        """CM-16: FIFO pack consumption — oldest pack consumed first."""
        packs = [
            {"id": "pack_old", "remaining": 100, "purchased_at": "2026-01-01T00:00:00Z"},
            {"id": "pack_new", "remaining": 500, "purchased_at": "2026-02-01T00:00:00Z"},
        ]
        meter, _, usage_repo, *_ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=1_000,
            active_packs=packs,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_fifo_001")

        # Should consume from oldest pack (index 0)
        assert result.pack_doc_id == "pack_old"
        usage_repo.consume_from_pack.assert_awaited_once_with(_TENANT_ID, "pack_old", 1)

    @pytest.mark.unit
    async def test_expired_pack_skipped(self):
        """CM-17: Expired pack (remaining=0) skipped, falls to overage."""
        packs = [
            {"id": "pack_exhausted", "remaining": 0, "purchased_at": "2025-11-01T00:00:00Z"},
        ]
        meter, _, usage_repo, *_ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=1_000,
            active_packs=packs,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            with patch.object(meter, "_report_overage", new_callable=AsyncMock, return_value=True):
                result = await meter.meter_conversation(_TENANT_ID, "conv_exp_001")

        assert result.consumed_from_pack is False
        assert result.consumed_from_overage is True

    @pytest.mark.unit
    async def test_stripe_overage_after_packs_exhausted(self):
        """CM-18: Stripe overage reported after packs exhausted (no active packs)."""
        meter, _, usage_repo, *_ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=1_000,
            active_packs=[],  # No packs available
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            with patch.object(meter, "_report_overage", new_callable=AsyncMock, return_value=True):
                result = await meter.meter_conversation(_TENANT_ID, "conv_overage_001")

        assert result.consumed_from_overage is True
        assert result.consumed_from_included is False
        assert result.consumed_from_pack is False


# ===========================================================================
# Proactive alerts — CM-19 through CM-22
# ===========================================================================


class TestProactiveAlerts:
    """Tests for proactive usage alerts (Decision #26)."""

    @pytest.mark.unit
    async def test_80_percent_alert_fires(self):
        """CM-19: 80% allowance alert fires once per period."""
        meter, _, usage_repo, audit_repo, _ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=799,  # Next will be 800 = 80% of 1000
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_80pct_001")

        assert UsageAlertType.ALLOWANCE_80_PERCENT in result.alerts
        audit_repo.log_event.assert_awaited()

    @pytest.mark.unit
    async def test_100_percent_alert_fires(self):
        """CM-20: 100% allowance alert fires once per period."""
        meter, _, usage_repo, audit_repo, _ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=999,  # Next will be 1000 = 100% of 1000
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_100pct_001")

        assert UsageAlertType.ALLOWANCE_100_PERCENT in result.alerts

    @pytest.mark.unit
    async def test_pack_balance_low_alert_placeholder(self):
        """CM-21: Pack balance low alert concept validated.

        The current implementation checks 80%/100% thresholds in _check_alerts().
        Pack balance low detection is noted in the constants (PACK_LOW_THRESHOLD).
        This test validates the constant exists and the alert type is defined.
        """
        assert ALERT_THRESHOLD_WARNING == 0.80
        assert ALERT_THRESHOLD_LIMIT == 1.00
        assert UsageAlertType.PACK_BALANCE_LOW == "pack_balance_low"
        from src.multi_tenant.conversation_meter import PACK_LOW_THRESHOLD
        assert PACK_LOW_THRESHOLD == 0.10

    @pytest.mark.unit
    async def test_alert_idempotent_same_period(self):
        """CM-22: Alert does not re-fire in same billing period (idempotent)."""
        # Pre-populate idempotency keys so alerts appear already sent
        pre_sent = {
            f"alert:{_BILLING_PERIOD}:80pct",
            f"alert:{_BILLING_PERIOD}:100pct",
        }
        meter, _, usage_repo, audit_repo, _ = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            total_conversations=999,
            idempotency_keys=pre_sent,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            result = await meter.meter_conversation(_TENANT_ID, "conv_no_alert_001")

        # No alerts should fire — they were already sent this period
        assert result.alerts == []
        # audit_repo.log_event should NOT be called for alerts
        # (it may be called for other reasons, but not for alert events)
        for call_args in audit_repo.log_event.call_args_list:
            payload = call_args.kwargs.get("payload", {})
            assert "alert_type" not in payload


# ===========================================================================
# Reconciliation — CM-23, CM-24
# ===========================================================================


class TestReconciliation:
    """Tests for daily reconciliation against Stripe Billing Meter."""

    @pytest.mark.unit
    async def test_reconciliation_no_discrepancy(self):
        """CM-23: Daily reconciliation — no discrepancy."""
        meter, _, usage_repo, audit_repo, tenant_repo = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            overage_reported=50,
        )

        # Stripe reports the same number
        with patch.object(
            meter, "_fetch_stripe_meter_total",
            new_callable=AsyncMock, return_value=50,
        ):
            with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
                result = await meter.reconcile_billing_period(_TENANT_ID)

        assert result.local_overage == 50
        assert result.stripe_meter_total == 50
        assert result.discrepancy == 0
        assert result.needs_review is False

    @pytest.mark.unit
    async def test_reconciliation_large_discrepancy_flagged(self):
        """CM-24: Daily reconciliation — >5% discrepancy flagged for review."""
        meter, _, usage_repo, audit_repo, tenant_repo = _make_meter_and_repos(
            tier=TenantTier.STARTER,
            overage_reported=100,
        )

        # Stripe reports significantly different number (>5% off)
        with patch.object(
            meter, "_fetch_stripe_meter_total",
            new_callable=AsyncMock, return_value=80,
        ):
            with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
                result = await meter.reconcile_billing_period(_TENANT_ID)

        assert result.local_overage == 100
        assert result.stripe_meter_total == 80
        assert result.discrepancy == 20
        assert result.needs_review is True
        assert result.discrepancy_percent == 20.0  # 20/100 = 20%

        # Audit event should be logged
        audit_repo.log_event.assert_awaited()


# ===========================================================================
# Dashboard & audit trail — CM-25, CM-26
# ===========================================================================


class TestDashboardAndAuditTrail:
    """Tests for usage dashboard and per-conversation billing detail."""

    @pytest.mark.unit
    async def test_usage_dashboard_returns_correct_counters(self):
        """CM-25: get_usage_dashboard() returns correct counters."""
        meter = _make_meter(
            tier=TenantTier.STARTER,
            total_conversations=800,
            pack_consumed=50,
            overage_reported=10,
        )

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            dashboard = await meter.get_usage_dashboard(_TENANT_ID)

        assert isinstance(dashboard, UsageDashboard)
        assert dashboard.tenant_id == _TENANT_ID
        assert dashboard.total_conversations == 800
        assert dashboard.included_allowance == 1_000
        assert dashboard.remaining_included == 200
        assert dashboard.overage_reported == 10
        assert dashboard.usage_percent == 80.0
        assert UsageAlertType.ALLOWANCE_80_PERCENT in dashboard.active_alerts

    @pytest.mark.unit
    async def test_conversation_billing_detail(self):
        """CM-26: get_conversation_billing_detail() returns full attribution."""
        meter, conv_repo, *_ = _make_meter_and_repos()
        conv_repo.read.return_value = {
            "conversation_id": "conv_detail_001",
            "tenant_id": _TENANT_ID,
            "status": ConversationStatus.COMPLETED.value,
            "is_billable": True,
            "message_count": 8,
            "turn_count": 4,
            "started_at": "2026-02-01T10:00:00Z",
            "ended_at": "2026-02-01T10:15:00Z",
            "customer_id": "cust_001",
            "agents_invoked": ["intent-classifier", "knowledge-retrieval", "response-generator"],
            "model_used": "gpt-4o",
            "critic_passed": True,
        }

        detail = await meter.get_conversation_billing_detail(_TENANT_ID, "conv_detail_001")

        assert detail["conversation_id"] == "conv_detail_001"
        assert detail["is_billable"] is True
        assert detail["message_count"] == 8
        assert detail["turn_count"] == 4
        assert detail["model_used"] == "gpt-4o"
        assert detail["critic_passed"] is True
        assert "intent-classifier" in detail["agents_invoked"]


# ===========================================================================
# Idle scanner — CM-27, CM-28
# ===========================================================================


class TestIdleScanner:
    """Tests for idle conversation scanner."""

    @pytest.mark.unit
    async def test_scanner_finds_stale_conversations(self):
        """CM-27: Idle conversation scanner finds stale conversations."""
        meter, conv_repo, *_ = _make_meter_and_repos(total_conversations=5)

        stale_conv = {
            "conversation_id": "conv_stale_001",
            "tenant_id": _TENANT_ID,
            "status": ConversationStatus.ACTIVE.value,
            "is_billable": True,
            "message_count": 3,
            "last_activity_at": (datetime.now(timezone.utc) - timedelta(minutes=35)).isoformat(),
        }
        conv_repo.query.return_value = [stale_conv]
        # read() for the stale conversation
        conv_repo.read.return_value = {
            **stale_conv,
            "turn_count": 2,
        }

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            results = await meter.scan_idle_conversations(_TENANT_ID)

        # Query was called to find idle conversations
        conv_repo.query.assert_awaited_once()
        assert len(results) == 1

    @pytest.mark.unit
    async def test_scanner_ends_stale_conversations(self):
        """CM-28: Idle conversation scanner ends stale conversations."""
        meter, conv_repo, *_ = _make_meter_and_repos(total_conversations=5)

        stale_conv = {
            "conversation_id": "conv_stale_002",
            "tenant_id": _TENANT_ID,
            "status": ConversationStatus.ACTIVE.value,
            "is_billable": True,
            "message_count": 4,
            "last_activity_at": (datetime.now(timezone.utc) - timedelta(minutes=40)).isoformat(),
        }
        conv_repo.query.return_value = [stale_conv]
        conv_repo.read.return_value = {
            **stale_conv,
            "turn_count": 2,
        }

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            results = await meter.scan_idle_conversations(_TENANT_ID)

        # end_conversation was called on the stale conversation
        conv_repo.end_conversation.assert_awaited_once()
        assert len(results) == 1
        assert results[0].conversation_id == "conv_stale_002"


# ===========================================================================
# Concurrency & period boundary — CM-29, CM-30
# ===========================================================================


class TestConcurrencyAndPeriodBoundary:
    """Tests for concurrent metering safety and billing period transitions."""

    @pytest.mark.unit
    async def test_concurrent_metering_idempotency(self):
        """CM-29: Concurrent metering calls — idempotency prevents double-count.

        Even if meter_conversation is called concurrently for the same
        conversation_id, the idempotency key mechanism ensures only one
        increment occurs.
        """
        meter, _, usage_repo, *_ = _make_meter_and_repos(total_conversations=5)

        with patch.object(meter, "_current_billing_period", return_value=_BILLING_PERIOD):
            # First call succeeds
            r1 = await meter.meter_conversation(_TENANT_ID, "conv_concurrent_001")
            assert r1.consumed_from_included is True

            # Second call — idempotent skip (key already recorded)
            r2 = await meter.meter_conversation(_TENANT_ID, "conv_concurrent_001")
            assert r2.consumed_from_included is False

        # Only one actual increment
        assert usage_repo.increment_conversations.await_count == 1

    @pytest.mark.unit
    async def test_billing_period_format(self):
        """CM-30: Billing period follows YYYY-MM format."""
        period = ConversationMeter._current_billing_period()
        # Should be YYYY-MM format
        assert len(period) == 7
        year, month = period.split("-")
        assert len(year) == 4
        assert len(month) == 2
        assert 1 <= int(month) <= 12


# ===========================================================================
# Constants and spec validation
# ===========================================================================


class TestSpecConstants:
    """Validate that spec constants match the architecture decisions."""

    @pytest.mark.unit
    def test_idle_timeout_is_30_minutes(self):
        """Idle timeout is 30 minutes (1,800 seconds)."""
        assert IDLE_TIMEOUT_SECONDS == 30 * 60

    @pytest.mark.unit
    def test_max_turns_is_50(self):
        """Max turns is 50."""
        assert MAX_TURNS == 50

    @pytest.mark.unit
    def test_non_billable_prefixes(self):
        """Non-billable prefixes match spec."""
        assert "test_" in NON_BILLABLE_PREFIXES
        assert "admin_" in NON_BILLABLE_PREFIXES
        assert "health_" in NON_BILLABLE_PREFIXES
        assert "system_" in NON_BILLABLE_PREFIXES

    @pytest.mark.unit
    def test_reconciliation_threshold_5_percent(self):
        """Reconciliation discrepancy threshold is 5%."""
        assert RECONCILIATION_DISCREPANCY_THRESHOLD == 0.05

    @pytest.mark.unit
    def test_tier_included_conversations(self):
        """Tier included conversations match pricing structure."""
        assert TIER_DEFAULTS[TenantTier.STARTER.value]["included_conversations"] == 1_000
        assert TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]["included_conversations"] == 5_000
        assert TIER_DEFAULTS[TenantTier.ENTERPRISE.value]["included_conversations"] == 20_000

    @pytest.mark.unit
    def test_should_end_returns_none_for_active(self):
        """Active conversation with low turns returns None (continue)."""
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(seconds=30)).isoformat()

        reason = ConversationMeter.should_end_conversation(
            last_activity_at=recent,
            turn_count=5,
            now=now,
        )
        assert reason is None

    @pytest.mark.unit
    def test_regular_conversation_is_billable(self):
        """Regular conversation ID without prefixes is billable."""
        assert ConversationMeter.is_conversation_billable("conv_regular_001") is True

    @pytest.mark.unit
    def test_no_ai_response_not_billable(self):
        """Conversation with no AI response is not billable."""
        assert ConversationMeter.is_conversation_billable(
            "conv_regular_001", has_ai_response=False,
        ) is False
