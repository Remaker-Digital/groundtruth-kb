"""
Billable conversation metering service.

Implements Decision #24 (billable conversation definition) and Decision #25
(three-layer usage transparency) from the architecture review.

Billable conversation specification:
    Starts:  First customer message (new conversation_id assigned).
    Ends:    30-min idle timeout | customer explicitly ends | escalated to
             human | 50-turn limit reached.
    Billing: 1 conversation = 1 billable unit regardless of message count.

    NOT billable:
        - Health checks and admin interactions
        - Test conversations (conversation_id prefix "test_")
        - Platform errors occurring before the first AI response

Consumption order (3-tier):
    1. Included allowance (free with subscription tier)
    2. Pack balance (pre-purchased conversations, FIFO oldest-first)
    3. Overage → Stripe Billing Meter (per-conversation billing)

Proactive alerts:
    - 80% of included allowance used
    - 100% of included allowance used
    - Pack balance low (< 10% remaining)
    - Volume spike (>2x daily average over trailing 7 days)

Reconciliation:
    - Daily comparison of local counter vs Stripe Billing Meter total
    - Discrepancy logged as audit event; manual review for delta > 5%

Architecture references:
    - Decision #24: Billable conversation definition
    - Decision #25: Three-layer usage transparency
    - Decision #26: Proactive billing alerts
    - Work Items #71-72

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import stripe

from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    AuditEventType,
    ConversationDocument,
    ConversationStatus,
    TenantTier,
    UsageCounterDocument,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — Billable conversation spec (Decision #24)
# ---------------------------------------------------------------------------

# A conversation is considered idle after this many seconds of inactivity.
IDLE_TIMEOUT_SECONDS = 30 * 60  # 30 minutes

# Maximum turns (customer–AI pairs) before a conversation is force-ended.
MAX_TURNS = 50

# Conversation ID prefixes that are never billable.
NON_BILLABLE_PREFIXES = ("test_", "admin_", "health_", "system_")

# Alert thresholds (percentage of included allowance).
ALERT_THRESHOLD_WARNING = 0.80   # 80%
ALERT_THRESHOLD_LIMIT = 1.00     # 100%

# Pack balance low threshold (percentage of total purchased).
PACK_LOW_THRESHOLD = 0.10  # 10%

# Volume spike multiplier (current day vs 7-day trailing average).
VOLUME_SPIKE_MULTIPLIER = 2.0

# Reconciliation discrepancy threshold (percentage).
RECONCILIATION_DISCREPANCY_THRESHOLD = 0.05  # 5%

# Stripe Billing Meter event name (must match Stripe dashboard config).
STRIPE_METER_EVENT_NAME = "conversation_overage"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ConversationEndReason(str, Enum):
    """Why a conversation ended."""

    IDLE_TIMEOUT = "idle_timeout"
    CUSTOMER_ENDED = "customer_ended"
    ESCALATED = "escalated"
    MAX_TURNS = "max_turns"
    ERROR = "error"


class UsageAlertType(str, Enum):
    """Types of proactive usage alerts."""

    ALLOWANCE_80_PERCENT = "allowance_80_percent"
    ALLOWANCE_100_PERCENT = "allowance_100_percent"
    PACK_BALANCE_LOW = "pack_balance_low"
    VOLUME_SPIKE = "volume_spike"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeterResult:
    """Result of metering a single conversation.

    Returned by ConversationMeter.meter_conversation() to inform the
    caller what happened with billing.
    """

    conversation_id: str
    tenant_id: str
    is_billable: bool
    billing_period: str

    # Consumption breakdown
    consumed_from_included: bool
    consumed_from_pack: bool
    consumed_from_overage: bool
    pack_doc_id: str | None  # Which pack was consumed (if any)

    # Current usage snapshot
    total_conversations: int
    included_allowance: int
    remaining_included: int
    usage_percent: float

    # Stripe meter event
    meter_event_sent: bool

    # Alerts triggered by this conversation
    alerts: list[UsageAlertType]


@dataclass(frozen=True)
class ReconciliationResult:
    """Result of daily reconciliation against Stripe."""

    tenant_id: str
    billing_period: str
    local_overage: int
    stripe_meter_total: int
    discrepancy: int
    discrepancy_percent: float
    needs_review: bool
    reconciled_at: str


@dataclass(frozen=True)
class UsageDashboard:
    """Three-layer usage transparency data (Decision #25, Layer 1).

    Real-time dashboard data for a tenant's current billing period.
    """

    tenant_id: str
    billing_period: str

    # Counters
    total_conversations: int
    included_allowance: int
    remaining_included: int
    pack_balance: int
    overage_conversations: int
    overage_reported: int

    # Calculated
    usage_percent: float
    estimated_overage_cost: float

    # Alerts
    active_alerts: list[UsageAlertType]


# ---------------------------------------------------------------------------
# ConversationMeter — Core metering service
# ---------------------------------------------------------------------------


class ConversationMeter:
    """Billable conversation metering service.

    This service is the single point of truth for conversation billing.
    All conversation lifecycle events flow through this service, which:

    1. Determines whether a conversation is billable (Decision #24 rules)
    2. Tracks the conversation in the usage counter (atomic increments)
    3. Applies 3-tier consumption: included → packs → Stripe overage
    4. Fires proactive usage alerts at configured thresholds
    5. Supports daily reconciliation against Stripe Billing Meter

    Dependencies:
        - ConversationRepository: conversation lifecycle persistence
        - UsageRepository: counter increments, pack balances, idempotency
        - AuditLogRepository: alert and reconciliation audit trail
        - TenantRepository: tenant lookup for tier/billing info
    """

    def __init__(
        self,
        conversation_repo: Any,
        usage_repo: Any,
        audit_repo: Any,
        tenant_repo: Any,
    ) -> None:
        self._conversations = conversation_repo
        self._usage = usage_repo
        self._audit = audit_repo
        self._tenants = tenant_repo

        # Lazy-initialized Stripe client
        self._stripe_client: stripe.StripeClient | None = None

    # -------------------------------------------------------------------
    # Billable conversation rules (Decision #24)
    # -------------------------------------------------------------------

    @staticmethod
    def is_conversation_billable(
        conversation_id: str,
        has_ai_response: bool = True,
    ) -> bool:
        """Determine whether a conversation is billable.

        A conversation is NOT billable if:
        - Its conversation_id starts with a non-billable prefix
          (test_, admin_, health_, system_)
        - No AI response was generated (platform error before first response)

        Everything else is billable: 1 conversation = 1 unit.

        Args:
            conversation_id: The conversation identifier.
            has_ai_response: Whether at least one AI response was generated.

        Returns:
            True if the conversation should be billed.
        """
        # Check non-billable prefixes
        if any(conversation_id.startswith(prefix) for prefix in NON_BILLABLE_PREFIXES):
            return False

        # Must have generated at least one AI response
        if not has_ai_response:
            return False

        return True

    @staticmethod
    def should_end_conversation(
        last_activity_at: str,
        turn_count: int,
        now: datetime | None = None,
    ) -> ConversationEndReason | None:
        """Check whether a conversation should be ended.

        Args:
            last_activity_at: ISO 8601 timestamp of last activity.
            turn_count: Current customer–AI turn count.
            now: Current time (defaults to utcnow).

        Returns:
            The end reason, or None if the conversation should continue.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        # 30-minute idle timeout
        try:
            last_active = datetime.fromisoformat(last_activity_at)
            if last_active.tzinfo is None:
                last_active = last_active.replace(tzinfo=timezone.utc)
            idle_seconds = (now - last_active).total_seconds()
            if idle_seconds >= IDLE_TIMEOUT_SECONDS:
                return ConversationEndReason.IDLE_TIMEOUT
        except (ValueError, TypeError):
            logger.warning(
                "Invalid last_activity_at timestamp: %s", last_activity_at
            )

        # 50-turn limit
        if turn_count >= MAX_TURNS:
            return ConversationEndReason.MAX_TURNS

        return None

    # -------------------------------------------------------------------
    # Conversation lifecycle
    # -------------------------------------------------------------------

    async def start_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_id: str | None = None,
    ) -> ConversationDocument:
        """Start a new conversation.

        Creates the conversation document in Cosmos DB. The conversation
        is not yet metered — metering happens when the conversation ends
        (or is explicitly metered via meter_conversation).

        Args:
            tenant_id: Tenant partition key.
            conversation_id: Unique conversation identifier.
            customer_id: Optional tokenized customer identifier.

        Returns:
            The created ConversationDocument.
        """
        now = datetime.now(timezone.utc).isoformat()
        is_billable = self.is_conversation_billable(conversation_id)

        doc = ConversationDocument(
            id=conversation_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            status=ConversationStatus.ACTIVE,
            customer_id=customer_id,
            is_billable=is_billable,
            message_count=0,
            turn_count=0,
            started_at=now,
            last_activity_at=now,
        )

        await self._conversations.create(tenant_id, doc)
        logger.info(
            "Conversation started: id=%s tenant=%s billable=%s",
            conversation_id, tenant_id, is_billable,
        )
        return doc

    async def end_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        reason: ConversationEndReason,
    ) -> MeterResult:
        """End a conversation and meter it if billable.

        This is the primary metering entry point. When a conversation ends:
        1. Mark it as ended in the conversations collection
        2. If billable, run the 3-tier consumption logic
        3. Return the MeterResult with billing details

        Args:
            tenant_id: Tenant partition key.
            conversation_id: Conversation to end.
            reason: Why the conversation is ending.

        Returns:
            MeterResult with complete billing information.
        """
        # Map end reason to conversation status
        status_map = {
            ConversationEndReason.IDLE_TIMEOUT: ConversationStatus.TIMED_OUT,
            ConversationEndReason.CUSTOMER_ENDED: ConversationStatus.RESOLVED,
            ConversationEndReason.ESCALATED: ConversationStatus.ESCALATED,
            ConversationEndReason.MAX_TURNS: ConversationStatus.RESOLVED,
            ConversationEndReason.ERROR: ConversationStatus.ERROR,
        }

        status = status_map.get(reason, ConversationStatus.RESOLVED)
        await self._conversations.end_conversation(
            tenant_id, conversation_id, status,
        )

        # P3-1: Quality aggregate + regression alert at meter closeout
        try:
            from src.chat.quality_closeout import evaluate_quality_and_alert
            await evaluate_quality_and_alert(tenant_id, conversation_id, self._conversations)
        except Exception:
            logger.warning(
                "Quality closeout failed (non-fatal): conv=%s", conversation_id,
                exc_info=True,
            )

        # Read the conversation to check billability
        conv = await self._conversations.read(tenant_id, conversation_id)
        is_billable = conv.get("is_billable", False)
        has_ai_response = conv.get("message_count", 0) > 1  # At least 1 customer + 1 AI

        # Re-check billability with the has_ai_response flag
        if is_billable and not has_ai_response:
            is_billable = False
            await self._conversations.patch(
                tenant_id, conversation_id,
                [{"op": "set", "path": "/is_billable", "value": False}],
            )

        if is_billable:
            return await self.meter_conversation(tenant_id, conversation_id)

        # Not billable — return a zero-impact result
        billing_period = self._current_billing_period()
        return MeterResult(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            is_billable=False,
            billing_period=billing_period,
            consumed_from_included=False,
            consumed_from_pack=False,
            consumed_from_overage=False,
            pack_doc_id=None,
            total_conversations=0,
            included_allowance=0,
            remaining_included=0,
            usage_percent=0.0,
            meter_event_sent=False,
            alerts=[],
        )

    # -------------------------------------------------------------------
    # WI #132: First-chunk delivery tracking
    # -------------------------------------------------------------------

    async def record_first_chunk(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> None:
        """Record that the first AI token has been streamed to the client.

        Called by the SSE manager's metering callback when the first
        non-heartbeat event is emitted. Updates the conversation document
        with ``first_chunk_at`` for billing-at-first-chunk and TTFB
        latency tracking.

        This method is idempotent — if ``first_chunk_at`` is already set,
        the update is skipped (handles SSE reconnection gracefully).

        Args:
            tenant_id: Tenant partition key.
            conversation_id: Conversation receiving its first chunk.
        """
        now = datetime.now(timezone.utc).isoformat()
        try:
            await self._conversations.patch(
                tenant_id=tenant_id,
                document_id=conversation_id,
                operations=[
                    # Only set if not already set (idempotent for reconnect)
                    {"op": "set", "path": "/first_chunk_at", "value": now},
                ],
            )
            logger.debug(
                "First chunk recorded: conv=%s tenant=%s at=%s",
                conversation_id, tenant_id, now,
            )
        except Exception:
            # Non-fatal — metering continues on conversation end
            logger.warning(
                "Failed to record first chunk: conv=%s tenant=%s",
                conversation_id, tenant_id,
                exc_info=True,
            )

    # -------------------------------------------------------------------
    # Core metering logic (3-tier consumption)
    # -------------------------------------------------------------------

    async def meter_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> MeterResult:
        """Meter a single billable conversation.

        Implements the 3-tier consumption order:
            1. Included allowance (free with tier)
            2. Pack balance (FIFO, oldest-first, 90-day validity)
            3. Overage → Stripe Billing Meter

        This method is idempotent: it checks the idempotency key store
        before processing. Duplicate calls for the same conversation_id
        are safely ignored.

        Args:
            tenant_id: Tenant partition key.
            conversation_id: Conversation to meter.

        Returns:
            MeterResult with complete billing breakdown.
        """
        # Idempotency check — prevent double-counting
        already_metered = await self._usage.check_idempotency(
            tenant_id, f"meter:{conversation_id}",
        )
        if already_metered:
            logger.info(
                "Conversation already metered (idempotent skip): id=%s tenant=%s",
                conversation_id, tenant_id,
            )
            # Return a minimal result for idempotent replay
            billing_period = self._current_billing_period()
            return MeterResult(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                is_billable=True,
                billing_period=billing_period,
                consumed_from_included=False,
                consumed_from_pack=False,
                consumed_from_overage=False,
                pack_doc_id=None,
                total_conversations=0,
                included_allowance=0,
                remaining_included=0,
                usage_percent=0.0,
                meter_event_sent=False,
                alerts=[],
            )

        # Get tenant info for tier
        tenant = await self._tenants.read(tenant_id, tenant_id)
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None

        billing_period = self._current_billing_period()

        # Get or create the usage counter for this period
        counter = await self._usage.get_or_create_counter(
            tenant_id, billing_period, tier,
        )

        # Atomically increment total conversations
        updated_counter = await self._usage.increment_conversations(
            tenant_id, billing_period,
        )

        total = updated_counter.get("total_conversations", 0)
        included = updated_counter.get("included_allowance", 0)

        # Determine which tier of consumption absorbs this conversation
        consumed_from_included = False
        consumed_from_pack = False
        consumed_from_overage = False
        pack_doc_id = None
        meter_event_sent = False

        if total <= included:
            # Tier 1: Within included allowance
            consumed_from_included = True
        else:
            # Beyond included allowance — try packs first
            now_iso = datetime.now(timezone.utc).isoformat()
            active_packs = await self._usage.get_active_packs(tenant_id, now_iso)

            if active_packs:
                # Tier 2: Consume from oldest pack (FIFO)
                pack = active_packs[0]
                if pack.get("remaining", 0) > 0:
                    await self._usage.consume_from_pack(
                        tenant_id, pack["id"], 1,
                    )
                    await self._usage.increment_pack_consumed(
                        tenant_id, billing_period, 1,
                    )
                    consumed_from_pack = True
                    pack_doc_id = pack["id"]
                else:
                    # Pack exhausted — fall through to overage
                    consumed_from_overage = True
                    meter_event_sent = await self._report_overage(
                        tenant_id, billing_period, updated_counter,
                    )
            else:
                # Tier 3: No packs available — report overage to Stripe
                consumed_from_overage = True
                meter_event_sent = await self._report_overage(
                    tenant_id, billing_period, updated_counter,
                )

        # Record idempotency key
        await self._usage.record_idempotency(
            tenant_id, f"meter:{conversation_id}", "conversation_metered",
        )

        # Check for alerts
        remaining = max(0, included - total)
        usage_pct = (total / included * 100) if included > 0 else 0.0
        alerts = await self._check_alerts(
            tenant_id, billing_period, total, included, tier,
        )

        return MeterResult(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            is_billable=True,
            billing_period=billing_period,
            consumed_from_included=consumed_from_included,
            consumed_from_pack=consumed_from_pack,
            consumed_from_overage=consumed_from_overage,
            pack_doc_id=pack_doc_id,
            total_conversations=total,
            included_allowance=included,
            remaining_included=remaining,
            usage_percent=round(usage_pct, 1),
            meter_event_sent=meter_event_sent,
            alerts=alerts,
        )

    # -------------------------------------------------------------------
    # Stripe Billing Meter integration
    # -------------------------------------------------------------------

    async def _report_overage(
        self,
        tenant_id: str,
        billing_period: str,
        counter: dict[str, Any],
    ) -> bool:
        """Report an overage conversation to Stripe Billing Meter.

        Returns True if the meter event was successfully sent.
        """
        tenant = await self._tenants.read(tenant_id, tenant_id)
        stripe_customer_id = tenant.get("stripe_customer_id")

        if not stripe_customer_id:
            logger.warning(
                "Cannot report overage: no Stripe customer ID for tenant=%s",
                tenant_id,
            )
            return False

        try:
            client = self._get_stripe_client()

            overage_reported = counter.get("overage_reported", 0)
            event_identifier = f"{tenant_id}_overage_{overage_reported + 1}"

            client.v1.billing.meter_events.create({
                "event_name": STRIPE_METER_EVENT_NAME,
                "payload": {
                    "stripe_customer_id": stripe_customer_id,
                    "value": "1",
                },
                "timestamp": int(time.time()),
                "identifier": event_identifier,
            })

            # Atomically increment overage_reported counter
            await self._usage.increment_overage_reported(
                tenant_id, billing_period, 1,
            )

            logger.info(
                "Overage meter event sent: tenant=%s customer=%s period=%s",
                tenant_id, stripe_customer_id, billing_period,
            )
            return True

        except Exception:
            logger.exception(
                "Failed to report overage to Stripe: tenant=%s period=%s",
                tenant_id, billing_period,
            )
            return False

    def _get_stripe_client(self) -> stripe.StripeClient:
        """Lazy-initialize the Stripe client."""
        if self._stripe_client is None:
            api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            if not api_key:
                raise RuntimeError(
                    "STRIPE_SECRET_KEY is not set — cannot report overage."
                )
            self._stripe_client = stripe.StripeClient(api_key)
        return self._stripe_client

    # -------------------------------------------------------------------
    # Proactive usage alerts (Decision #26)
    # -------------------------------------------------------------------

    async def _check_alerts(
        self,
        tenant_id: str,
        billing_period: str,
        total: int,
        included: int,
        tier: TenantTier | None,
    ) -> list[UsageAlertType]:
        """Check whether usage thresholds have been crossed.

        Fires alerts at:
        - 80% of included allowance
        - 100% of included allowance

        Each alert fires only once per billing period (idempotency via
        the usage collection's idempotency key mechanism).

        Returns:
            List of alert types that were triggered by this conversation.
        """
        triggered: list[UsageAlertType] = []

        if included <= 0:
            return triggered

        usage_ratio = total / included

        # 80% warning
        if usage_ratio >= ALERT_THRESHOLD_WARNING:
            alert_key = f"alert:{billing_period}:80pct"
            already_sent = await self._usage.check_idempotency(tenant_id, alert_key)
            if not already_sent:
                await self._usage.record_idempotency(
                    tenant_id, alert_key, "usage_alert",
                )
                await self._audit.log_event(
                    event_type=AuditEventType.SUBSCRIPTION_CHANGED,
                    tenant_id=tenant_id,
                    actor="conversation_meter",
                    actor_type="system",
                    payload={
                        "alert_type": UsageAlertType.ALLOWANCE_80_PERCENT.value,
                        "billing_period": billing_period,
                        "total_conversations": total,
                        "included_allowance": included,
                        "usage_percent": round(usage_ratio * 100, 1),
                    },
                )
                triggered.append(UsageAlertType.ALLOWANCE_80_PERCENT)
                logger.info(
                    "Usage alert: 80%% threshold — tenant=%s period=%s "
                    "total=%d included=%d",
                    tenant_id, billing_period, total, included,
                )

        # 100% limit
        if usage_ratio >= ALERT_THRESHOLD_LIMIT:
            alert_key = f"alert:{billing_period}:100pct"
            already_sent = await self._usage.check_idempotency(tenant_id, alert_key)
            if not already_sent:
                await self._usage.record_idempotency(
                    tenant_id, alert_key, "usage_alert",
                )
                await self._audit.log_event(
                    event_type=AuditEventType.SUBSCRIPTION_CHANGED,
                    tenant_id=tenant_id,
                    actor="conversation_meter",
                    actor_type="system",
                    payload={
                        "alert_type": UsageAlertType.ALLOWANCE_100_PERCENT.value,
                        "billing_period": billing_period,
                        "total_conversations": total,
                        "included_allowance": included,
                        "usage_percent": round(usage_ratio * 100, 1),
                    },
                )
                triggered.append(UsageAlertType.ALLOWANCE_100_PERCENT)
                logger.info(
                    "Usage alert: 100%% threshold — tenant=%s period=%s "
                    "total=%d included=%d",
                    tenant_id, billing_period, total, included,
                )

        return triggered

    # -------------------------------------------------------------------
    # Usage dashboard (Decision #25 — Layer 1: real-time dashboard)
    # -------------------------------------------------------------------

    async def get_usage_dashboard(
        self,
        tenant_id: str,
        billing_period: str | None = None,
    ) -> UsageDashboard:
        """Get the real-time usage dashboard for a tenant.

        Layer 1 of the three-layer usage transparency model (Decision #25).

        Args:
            tenant_id: Tenant partition key.
            billing_period: Period to query (default: current period).

        Returns:
            UsageDashboard with current usage data.
        """
        if billing_period is None:
            billing_period = self._current_billing_period()

        tenant = await self._tenants.read(tenant_id, tenant_id)
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None

        # Get usage counter
        counter = await self._usage.get_or_create_counter(
            tenant_id, billing_period, tier,
        )

        total = counter.get("total_conversations", 0)
        included = counter.get("included_allowance", 0)
        overage_reported = counter.get("overage_reported", 0)
        pack_consumed = counter.get("pack_consumed", 0)

        remaining = max(0, included - total)
        usage_pct = (total / included * 100) if included > 0 else 0.0

        # Get pack balance
        now_iso = datetime.now(timezone.utc).isoformat()
        active_packs = await self._usage.get_active_packs(tenant_id, now_iso)
        pack_balance = sum(p.get("remaining", 0) for p in active_packs)

        # Calculate overage cost
        overage_count = max(0, total - included - pack_consumed)
        overage_rate = 0.0
        if tier:
            from src.multi_tenant.entitlement_service import get_entitlement_service
            defaults = await get_entitlement_service().get_tier_config(tier.value)
            overage_rate = defaults.get("overage_rate", 0.0)
        estimated_cost = overage_count * overage_rate

        # Determine active alerts
        active_alerts: list[UsageAlertType] = []
        if included > 0:
            ratio = total / included
            if ratio >= ALERT_THRESHOLD_LIMIT:
                active_alerts.append(UsageAlertType.ALLOWANCE_100_PERCENT)
            elif ratio >= ALERT_THRESHOLD_WARNING:
                active_alerts.append(UsageAlertType.ALLOWANCE_80_PERCENT)

        return UsageDashboard(
            tenant_id=tenant_id,
            billing_period=billing_period,
            total_conversations=total,
            included_allowance=included,
            remaining_included=remaining,
            pack_balance=pack_balance,
            overage_conversations=overage_count,
            overage_reported=overage_reported,
            usage_percent=round(usage_pct, 1),
            estimated_overage_cost=round(estimated_cost, 2),
            active_alerts=active_alerts,
        )

    # -------------------------------------------------------------------
    # Daily reconciliation (Decision #25 — Layer 3: dispute resolution)
    # -------------------------------------------------------------------

    async def reconcile_billing_period(
        self,
        tenant_id: str,
        billing_period: str | None = None,
    ) -> ReconciliationResult:
        """Reconcile local usage counter against Stripe Billing Meter.

        Runs daily (scheduled). Compares the local overage_reported count
        with the Stripe Billing Meter's total for the same period. Logs
        discrepancies as audit events and flags tenants with delta > 5%
        for manual review.

        Args:
            tenant_id: Tenant partition key.
            billing_period: Period to reconcile (default: current).

        Returns:
            ReconciliationResult with comparison data.
        """
        if billing_period is None:
            billing_period = self._current_billing_period()

        tenant = await self._tenants.read(tenant_id, tenant_id)
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None
        stripe_customer_id = tenant.get("stripe_customer_id")

        # Get local counter
        counter = await self._usage.get_or_create_counter(
            tenant_id, billing_period, tier,
        )
        local_overage = counter.get("overage_reported", 0)

        # Get Stripe meter total
        stripe_total = 0
        if stripe_customer_id:
            stripe_total = await self._fetch_stripe_meter_total(
                stripe_customer_id, billing_period,
            )

        discrepancy = abs(local_overage - stripe_total)
        discrepancy_pct = (
            discrepancy / max(local_overage, 1)
        ) if local_overage > 0 else 0.0

        needs_review = discrepancy_pct > RECONCILIATION_DISCREPANCY_THRESHOLD

        now = datetime.now(timezone.utc).isoformat()

        # Update the counter with reconciliation data
        doc_id = f"{tenant_id}:{billing_period}"
        await self._usage.patch(
            tenant_id, doc_id,
            operations=[
                {"op": "set", "path": "/last_reconciled_at", "value": now},
                {"op": "set", "path": "/stripe_meter_total", "value": stripe_total},
            ],
        )

        # Log reconciliation event
        await self._audit.log_event(
            event_type=AuditEventType.SUBSCRIPTION_CHANGED,
            tenant_id=tenant_id,
            actor="reconciliation_service",
            actor_type="system",
            payload={
                "action": "billing_reconciliation",
                "billing_period": billing_period,
                "local_overage": local_overage,
                "stripe_meter_total": stripe_total,
                "discrepancy": discrepancy,
                "discrepancy_percent": round(discrepancy_pct * 100, 1),
                "needs_review": needs_review,
            },
        )

        if needs_review:
            logger.warning(
                "Reconciliation discrepancy: tenant=%s period=%s "
                "local=%d stripe=%d delta=%d (%.1f%%)",
                tenant_id, billing_period, local_overage, stripe_total,
                discrepancy, discrepancy_pct * 100,
            )

        result = ReconciliationResult(
            tenant_id=tenant_id,
            billing_period=billing_period,
            local_overage=local_overage,
            stripe_meter_total=stripe_total,
            discrepancy=discrepancy,
            discrepancy_percent=round(discrepancy_pct * 100, 1),
            needs_review=needs_review,
            reconciled_at=now,
        )

        return result

    async def _fetch_stripe_meter_total(
        self,
        stripe_customer_id: str,
        billing_period: str,
    ) -> int:
        """Fetch the Stripe Billing Meter total for a customer.

        Uses Stripe's Billing Meter Event Summary API to get the
        total metered events for the billing period.

        Args:
            stripe_customer_id: Stripe customer ID.
            billing_period: Period string (e.g. "2026-02").

        Returns:
            Total metered events from Stripe.
        """
        try:
            client = self._get_stripe_client()

            # Parse billing period to get start/end timestamps
            year, month = billing_period.split("-")
            start = datetime(int(year), int(month), 1, tzinfo=timezone.utc)
            if int(month) == 12:
                end = datetime(int(year) + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = datetime(int(year), int(month) + 1, 1, tzinfo=timezone.utc)

            # Stripe Billing Meter Event Summaries
            summaries = client.v1.billing.meters.list_event_summaries(
                "conversation_overage",  # meter ID
                {
                    "customer": stripe_customer_id,
                    "start_time": int(start.timestamp()),
                    "end_time": int(end.timestamp()),
                },
            )

            total = 0
            for summary in summaries.auto_paging_iter():
                total += int(summary.aggregated_value)

            return total

        except Exception:
            logger.exception(
                "Failed to fetch Stripe meter total: customer=%s period=%s",
                stripe_customer_id, billing_period,
            )
            return 0

    # -------------------------------------------------------------------
    # Idle conversation scanner
    # -------------------------------------------------------------------

    async def scan_idle_conversations(
        self,
        tenant_id: str,
    ) -> list[MeterResult]:
        """Scan for and close idle conversations for a tenant.

        Called periodically (e.g., every 5 minutes) to find conversations
        that have exceeded the 30-minute idle timeout.

        Returns:
            List of MeterResults for conversations that were closed.
        """
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(seconds=IDLE_TIMEOUT_SECONDS)).isoformat()

        # Find active conversations with last_activity before the cutoff
        idle_conversations = await self._conversations.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.status = @status "
                "AND c.last_activity_at < @cutoff"
            ),
            parameters=[
                {"name": "@status", "value": ConversationStatus.ACTIVE.value},
                {"name": "@cutoff", "value": cutoff},
            ],
        )

        results: list[MeterResult] = []
        for conv in idle_conversations:
            try:
                result = await self.end_conversation(
                    tenant_id=tenant_id,
                    conversation_id=conv["conversation_id"],
                    reason=ConversationEndReason.IDLE_TIMEOUT,
                )
                results.append(result)
            except Exception:
                logger.exception(
                    "Failed to close idle conversation: id=%s tenant=%s",
                    conv.get("conversation_id"), tenant_id,
                )

        if results:
            logger.info(
                "Closed %d idle conversations for tenant=%s",
                len(results), tenant_id,
            )

        return results

    # -------------------------------------------------------------------
    # Per-conversation audit trail (Decision #25 — Layer 2)
    # -------------------------------------------------------------------

    async def get_conversation_billing_detail(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> dict[str, Any]:
        """Get billing detail for a single conversation.

        Layer 2 of the three-layer usage transparency model:
        per-conversation audit trail with full billing attribution.

        Returns:
            Dict with conversation metadata, billing attribution, and
            metering timestamps.
        """
        conv = await self._conversations.read(tenant_id, conversation_id)

        return {
            "conversation_id": conversation_id,
            "tenant_id": tenant_id,
            "status": conv.get("status"),
            "is_billable": conv.get("is_billable", False),
            "message_count": conv.get("message_count", 0),
            "turn_count": conv.get("turn_count", 0),
            "started_at": conv.get("started_at"),
            "ended_at": conv.get("ended_at"),
            "customer_id": conv.get("customer_id"),
            "agents_invoked": conv.get("agents_invoked", []),
            "model_used": conv.get("model_used"),
            "critic_passed": conv.get("critic_passed"),
        }

    # -------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------

    @staticmethod
    def _current_billing_period() -> str:
        """Get the current billing period string (YYYY-MM)."""
        return datetime.now(timezone.utc).strftime("%Y-%m")


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_conversation_meter_instance: ConversationMeter | None = None


def configure_conversation_meter(meter: ConversationMeter) -> None:
    """Store a configured ConversationMeter instance as the module singleton.

    Called during application startup after repos are initialized.
    """
    global _conversation_meter_instance  # noqa: PLW0603
    _conversation_meter_instance = meter


def get_conversation_meter() -> ConversationMeter:
    """Return the module-level ConversationMeter singleton.

    Raises:
        RuntimeError: If ``configure_conversation_meter()`` has not been
            called yet (startup ordering issue).
    """
    if _conversation_meter_instance is None:
        raise RuntimeError(
            "ConversationMeter not configured — call "
            "configure_conversation_meter() during startup"
        )
    return _conversation_meter_instance
