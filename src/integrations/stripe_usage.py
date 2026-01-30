"""
Stripe metered usage reporting.

Reports conversation usage to the Stripe Billing Meter so overage charges
appear on customer invoices. Only conversations exceeding the tier's
included allowance AND any pre-purchased pack balance are reported as
billable meter events.

Consumption order:
    1. Tier's included allowance (free with subscription)
    2. Pack balance (pre-purchased conversations, FIFO oldest-first)
    3. Overage billing (per-conversation via Stripe Billing Meter)

Flow:
    1. Application calls record_conversation() after each AI conversation.
    2. Module tracks per-customer usage for the current billing period.
    3. When usage exceeds the tier's included allowance, pack balance
       is consumed first (via stripe_packs.consume_pack_balance).
    4. Any remaining overage beyond pack balance is sent to Stripe
       Billing Meter for per-conversation billing.

Endpoints:
    POST /api/usage/record          — Record a conversation (internal API)
    GET  /api/usage/{customer_id}   — Get usage summary for a customer

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.integrations.stripe_catalog import load_catalog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# StripeClient is required for Billing Meters API (v1 namespace)
_stripe_client: stripe.StripeClient | None = None


def _get_client() -> stripe.StripeClient:
    """Lazy-initialize the StripeClient."""
    global _stripe_client
    if _stripe_client is None:
        api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not api_key:
            raise RuntimeError(
                "STRIPE_SECRET_KEY is not set — cannot report usage."
            )
        _stripe_client = stripe.StripeClient(api_key)
    return _stripe_client


# ---------------------------------------------------------------------------
# In-memory usage tracking (DEVELOPMENT ONLY)
#
# WARNING: This in-memory implementation is NOT safe for production:
#   1. Counters are lost on process restart.
#   2. Not shared across multiple workers (uvicorn --workers N).
#   3. Non-atomic read-modify-write on counters — concurrent async
#      requests for the same customer may race.
#
# Production replacement (Phase 2.2): Cosmos DB counters with atomic
# increments, partitioned by tenant ID, with TTL aligned to billing
# periods. The in-memory version enables local development and testing.
#
# Structure: { stripe_customer_id: { "total": int, "reported": int } }
# - total: all conversations this billing period
# - reported: conversations already sent to Stripe Meter (overage only)
# ---------------------------------------------------------------------------

_usage_counters: dict[str, dict[str, int]] = {}

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/usage", tags=["usage"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class RecordConversationRequest(BaseModel):
    """Request to record one or more conversations for a customer."""

    stripe_customer_id: str = Field(
        ...,
        description="The Stripe Customer ID (cus_...)",
        examples=["cus_ABC123"],
    )
    tier: str = Field(
        ...,
        description="Customer's subscription tier",
        examples=["starter"],
    )
    count: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Number of conversations to record (default 1)",
    )


class RecordConversationResponse(BaseModel):
    """Response after recording conversation usage.

    Fields:
        total_conversations: Total conversations this billing period.
        included_allowance: Conversations included free with the tier.
        pack_consumed: Conversations absorbed by pack balance in this call.
        overage_conversations: Billable overage from this call (sent to Stripe).
        newly_reported: Conversations newly reported to Stripe Billing Meter.
        meter_event_sent: Whether a Stripe meter event was successfully sent.
    """

    stripe_customer_id: str
    total_conversations: int
    included_allowance: int
    pack_consumed: int
    overage_conversations: int
    newly_reported: int
    meter_event_sent: bool


class UsageSummaryResponse(BaseModel):
    """Current usage summary for a customer."""

    stripe_customer_id: str
    total_conversations: int
    included_allowance: int
    pack_balance: int
    overage_conversations: int
    overage_reported: int
    remaining_included: int
    usage_percent: float


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _get_counter(customer_id: str) -> dict[str, int]:
    """Get or create the usage counter for a customer."""
    if customer_id not in _usage_counters:
        _usage_counters[customer_id] = {"total": 0, "reported": 0}
    return _usage_counters[customer_id]


async def record_conversation(
    stripe_customer_id: str,
    tier: str,
    count: int = 1,
) -> RecordConversationResponse:
    """Record conversations and report overage to Stripe Billing Meter.

    This is the primary function called by the conversation pipeline
    after each AI interaction completes.

    Consumption order:
        1. Tier's included allowance (free)
        2. Pack balance (pre-purchased, consumed FIFO)
        3. Overage → Stripe Billing Meter

    Args:
        stripe_customer_id: Stripe customer ID (cus_...)
        tier: Subscription tier name (starter, professional, enterprise)
        count: Number of conversations to record (usually 1)

    Returns:
        RecordConversationResponse with usage details.
    """
    # Import here to avoid circular imports (stripe_packs imports stripe_catalog,
    # and this module also imports stripe_catalog — but no circular dependency
    # exists since neither module imports the other at module level).
    from src.integrations.stripe_packs import consume_pack_balance

    catalog = load_catalog()
    tier_info = catalog.get_tier(tier)
    included = tier_info.included_conversations

    # Update counter
    counter = _get_counter(stripe_customer_id)
    counter["total"] += count

    total = counter["total"]
    reported = counter["reported"]

    # Calculate raw overage (conversations beyond included allowance)
    raw_overage = max(0, total - included)
    unreported_raw = raw_overage - reported

    # Consume from pack balance before reporting overage to Stripe.
    # Only try to consume the NEW overage (not previously reported).
    pack_consumed = 0
    if unreported_raw > 0:
        pack_consumed = consume_pack_balance(stripe_customer_id, unreported_raw)

    # Billable overage = raw overage minus what packs absorbed
    billable_overage = unreported_raw - pack_consumed

    # Track pack-absorbed conversations as "reported" so they don't
    # get double-counted on the next call.
    if pack_consumed > 0:
        counter["reported"] += pack_consumed

    meter_event_sent = False

    # Report remaining billable overage to Stripe
    if billable_overage > 0:
        try:
            client = _get_client()
            # Update the high-water mark for idempotency identifier.
            # reported now includes pack-consumed + previously-reported.
            new_reported_total = counter["reported"] + billable_overage
            event_identifier = f"{stripe_customer_id}_overage_{new_reported_total}"
            client.v1.billing.meter_events.create({
                "event_name": "conversation_overage",
                "payload": {
                    "stripe_customer_id": stripe_customer_id,
                    "value": str(billable_overage),
                },
                "timestamp": int(time.time()),
                "identifier": event_identifier,
            })
            counter["reported"] = new_reported_total
            meter_event_sent = True

            logger.info(
                "Meter event sent: customer=%s billable_overage=%d "
                "pack_consumed=%d total=%d included=%d",
                stripe_customer_id,
                billable_overage,
                pack_consumed,
                total,
                included,
            )
        except Exception:
            # Log but don't fail the conversation — usage will be reported
            # on the next call when unreported overage accumulates.
            logger.exception(
                "Failed to report meter event: customer=%s overage=%d",
                stripe_customer_id,
                billable_overage,
            )

    # overage_conversations = conversations billed (or pending billing) to
    # Stripe this period, excluding those absorbed by pack balance.
    # This equals counter["reported"] minus what packs absorbed.
    billed_overage = counter["reported"] - pack_consumed if pack_consumed > 0 else counter["reported"]
    # Simpler: it's just the billable overage from THIS call.
    # But for the summary view, report cumulative billable = reported total.
    return RecordConversationResponse(
        stripe_customer_id=stripe_customer_id,
        total_conversations=total,
        included_allowance=included,
        pack_consumed=pack_consumed,
        overage_conversations=billable_overage,
        newly_reported=billable_overage if meter_event_sent else 0,
        meter_event_sent=meter_event_sent,
    )


def get_usage_summary(
    stripe_customer_id: str,
    tier: str,
) -> UsageSummaryResponse:
    """Get the current usage summary for a customer.

    Args:
        stripe_customer_id: Stripe customer ID (cus_...)
        tier: Subscription tier name

    Returns:
        UsageSummaryResponse with current period usage details.
    """
    from src.integrations.stripe_packs import get_pack_balance

    catalog = load_catalog()
    tier_info = catalog.get_tier(tier)
    included = tier_info.included_conversations

    counter = _get_counter(stripe_customer_id)
    total = counter["total"]
    overage = max(0, total - included)
    remaining = max(0, included - total)
    usage_pct = (total / included * 100) if included > 0 else 0.0

    # Get current pack balance
    pack_info = get_pack_balance(stripe_customer_id)
    pack_remaining = pack_info["total_remaining"]

    return UsageSummaryResponse(
        stripe_customer_id=stripe_customer_id,
        total_conversations=total,
        included_allowance=included,
        pack_balance=pack_remaining,
        overage_conversations=overage,
        overage_reported=counter["reported"],
        remaining_included=remaining,
        usage_percent=round(usage_pct, 1),
    )


def reset_usage(stripe_customer_id: str) -> None:
    """Reset usage counters for a new billing period.

    Called by the webhook handler when invoice.payment_succeeded fires
    for a subscription renewal (billing_reason = "subscription_cycle").

    In production, this is handled by Cosmos DB TTL on the usage
    documents, aligned with the billing period timestamps from Stripe.
    """
    if stripe_customer_id in _usage_counters:
        _usage_counters[stripe_customer_id] = {"total": 0, "reported": 0}
        logger.info("Usage reset for customer: %s", stripe_customer_id)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/record", response_model=RecordConversationResponse)
async def record_usage_endpoint(body: RecordConversationRequest) -> RecordConversationResponse:
    """Record conversation usage for a customer.

    This endpoint is called internally by the conversation pipeline.
    In production, it would be authenticated via an internal API key
    or service-to-service auth (not exposed publicly).
    """
    try:
        return await record_conversation(
            stripe_customer_id=body.stripe_customer_id,
            tier=body.tier,
            count=body.count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{customer_id}", response_model=UsageSummaryResponse)
async def get_usage_endpoint(customer_id: str, tier: str) -> UsageSummaryResponse:
    """Get current usage summary for a customer.

    Query parameters:
        tier: The customer's subscription tier (required)
    """
    try:
        return get_usage_summary(
            stripe_customer_id=customer_id,
            tier=tier,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
