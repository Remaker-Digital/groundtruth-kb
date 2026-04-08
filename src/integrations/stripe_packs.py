"""
Conversation pack purchase and balance management.

Enables customers to pre-purchase conversation packs at discounted rates.
Packs provide a conversation balance that is consumed before overage billing
kicks in, giving customers a cheaper per-conversation rate.

Consumption order (applied in stripe_usage.py):
    1. Tier's included allowance (free with subscription)
    2. Pack balance (pre-purchased conversations)
    3. Overage billing (per-conversation via Stripe Billing Meter)

Pack catalog:
    - 1,000 conversations: $29  ($0.029/conv, 90-day validity)
    - 5,000 conversations: $99  ($0.020/conv, 90-day validity)
    - 20,000 conversations: $249 ($0.012/conv, 90-day validity)

Flow:
    1. Customer calls POST /api/packs/purchase with pack_id.
    2. Module creates a Stripe Checkout Session in payment mode.
    3. Customer completes payment on Stripe's hosted checkout page.
    4. Webhook (checkout.session.completed) detects pack purchase via
       metadata and calls credit_pack_balance() to add conversations.
    5. stripe_usage.py consumes pack balance before reporting overage.

Endpoints:
    POST /api/packs/purchase             — Create a checkout session for a pack
    GET  /api/packs/balance/{customer_id} — Check remaining pack balance

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
from src.integrations.stripe_portal import _resolve_stripe_customer_id

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080")

# Pack validity in seconds (90 days)
_PACK_VALIDITY_SECONDS = 90 * 24 * 60 * 60

# ---------------------------------------------------------------------------
# In-memory pack balance tracking (DEVELOPMENT ONLY)
#
# WARNING: Same caveats as stripe_usage.py in-memory counters:
#   1. Balances lost on restart.
#   2. Not shared across workers.
#   3. Non-atomic operations.
#
# Production replacement (Phase 2.2): Cosmos DB documents with:
#   - Partition key: stripe_customer_id
#   - Fields: remaining_conversations, purchased_at, expires_at
#   - TTL: 90 days (auto-expiry)
#
# Structure: { stripe_customer_id: [ { remaining, purchased_at, expires_at, pack_id }, ... ] }
# Multiple packs per customer are stored as a list, consumed FIFO (oldest first).
# ---------------------------------------------------------------------------

_pack_balances: dict[str, list[dict[str, Any]]] = {}

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/packs", tags=["packs"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class PurchasePackRequest(BaseModel):
    """Request to purchase a conversation pack.

    Provide either ``tenant_id`` (preferred — resolves the Stripe customer
    via provisioning) or ``stripe_customer_id`` (direct Stripe lookup).
    If both are supplied, ``stripe_customer_id`` takes precedence.
    """

    pack_id: str = Field(
        ...,
        description="Pack identifier: pack_1k, pack_5k, or pack_20k",
        examples=["pack_1k"],
    )
    tenant_id: str | None = Field(
        default=None,
        description=("Tenant ID (UUID). The module looks up the Stripe customer ID from the provisioning service."),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    stripe_customer_id: str | None = Field(
        default=None,
        description="Stripe customer ID (cus_...) for direct lookup.",
        examples=["cus_ABC123"],
    )
    success_url: str | None = Field(
        default=None,
        description="Custom success redirect URL.",
    )
    cancel_url: str | None = Field(
        default=None,
        description="Custom cancel redirect URL.",
    )


class PurchasePackResponse(BaseModel):
    """Response containing the Checkout Session URL for pack purchase."""

    session_id: str
    checkout_url: str
    pack_id: str
    conversations: int
    price_display: str


class PackBalanceEntry(BaseModel):
    """A single pack's remaining balance."""

    pack_id: str
    remaining: int
    purchased_at: str
    expires_at: str
    is_expired: bool


class PackBalanceResponse(BaseModel):
    """Pack balance summary for a customer."""

    stripe_customer_id: str
    total_remaining: int
    active_packs: list[PackBalanceEntry]
    expired_packs: int


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _get_pack_entries(customer_id: str) -> list[dict[str, Any]]:
    """Get the list of pack entries for a customer."""
    if customer_id not in _pack_balances:
        _pack_balances[customer_id] = []
    return _pack_balances[customer_id]


def credit_pack_balance(
    stripe_customer_id: str,
    pack_id: str,
    conversations: int,
) -> dict[str, Any]:
    """Credit a conversation pack to a customer's balance.

    Called by the webhook handler when a pack purchase completes
    (checkout.session.completed with agent_red_pack metadata).

    Args:
        stripe_customer_id: Stripe customer ID (cus_...).
        pack_id: Pack identifier (pack_1k, pack_5k, pack_20k).
        conversations: Number of conversations in the pack.

    Returns:
        Dict with credit details.
    """
    now = int(time.time())
    expires_at = now + _PACK_VALIDITY_SECONDS

    entry = {
        "pack_id": pack_id,
        "remaining": conversations,
        "purchased_at": now,
        "expires_at": expires_at,
    }

    entries = _get_pack_entries(stripe_customer_id)
    entries.append(entry)

    total_remaining = sum(e["remaining"] for e in entries if e["expires_at"] > now and e["remaining"] > 0)

    logger.info(
        "Pack credited: customer=%s pack=%s conversations=%d total_remaining=%d",
        stripe_customer_id,
        pack_id,
        conversations,
        total_remaining,
    )

    return {
        "stripe_customer_id": stripe_customer_id,
        "pack_id": pack_id,
        "conversations_credited": conversations,
        "total_remaining": total_remaining,
        "expires_at": expires_at,
    }


def consume_pack_balance(
    stripe_customer_id: str,
    count: int,
) -> int:
    """Consume conversations from pack balance (FIFO, oldest first).

    Called by stripe_usage.record_conversation() after the tier's included
    allowance is exhausted but before reporting overage to Stripe.

    Args:
        stripe_customer_id: Stripe customer ID (cus_...).
        count: Number of conversations to consume.

    Returns:
        Number of conversations actually consumed from packs.
        This may be less than `count` if pack balance is insufficient.
    """
    entries = _get_pack_entries(stripe_customer_id)
    now = int(time.time())

    consumed = 0
    remaining_to_consume = count

    for entry in entries:
        if remaining_to_consume <= 0:
            break

        # Skip expired packs
        if entry["expires_at"] <= now:
            continue

        # Skip depleted packs
        if entry["remaining"] <= 0:
            continue

        # Consume from this pack
        take = min(entry["remaining"], remaining_to_consume)
        entry["remaining"] -= take
        consumed += take
        remaining_to_consume -= take

    if consumed > 0:
        logger.info(
            "Pack balance consumed: customer=%s consumed=%d requested=%d",
            stripe_customer_id,
            consumed,
            count,
        )

    return consumed


def get_pack_balance(stripe_customer_id: str) -> dict[str, Any]:
    """Get the current pack balance for a customer.

    Args:
        stripe_customer_id: Stripe customer ID (cus_...).

    Returns:
        Dict with balance details including active and expired packs.
    """
    entries = _get_pack_entries(stripe_customer_id)
    now = int(time.time())

    active_packs = []
    expired_count = 0
    total_remaining = 0

    for entry in entries:
        is_expired = entry["expires_at"] <= now
        has_remaining = entry["remaining"] > 0

        if is_expired:
            expired_count += 1
        elif has_remaining:
            total_remaining += entry["remaining"]
            active_packs.append(
                {
                    "pack_id": entry["pack_id"],
                    "remaining": entry["remaining"],
                    "purchased_at": entry["purchased_at"],
                    "expires_at": entry["expires_at"],
                    "is_expired": False,
                }
            )

    return {
        "stripe_customer_id": stripe_customer_id,
        "total_remaining": total_remaining,
        "active_packs": active_packs,
        "expired_packs": expired_count,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/purchase",
    response_model=PurchasePackResponse,
    status_code=200,
    summary="Purchase a conversation pack",
    description=(
        "Creates a Stripe Checkout Session for a one-time conversation pack purchase. Pack metadata is attached so the "
        "webhook handler can credit the balance on completion."
    ),
    responses={
        400: {"description": "Invalid pack_id"},
        502: {"description": "Stripe API error during session creation"},
    },
)
async def purchase_pack_endpoint(body: PurchasePackRequest) -> PurchasePackResponse:
    """Create a Stripe Checkout Session for a one-time pack purchase.

    The session uses mode="payment" (not subscription) since packs are
    one-time purchases. Pack metadata is attached to the session so the
    webhook handler can identify and credit the purchase.
    """
    catalog = load_catalog()

    # Validate pack_id
    if body.pack_id not in catalog.packs:
        raise HTTPException(
            status_code=400,
            detail=(f"Invalid pack_id '{body.pack_id}'. Valid packs: {sorted(catalog.packs.keys())}"),
        )

    pack = catalog.packs[body.pack_id]

    # Resolve Stripe customer ID from tenant_id or stripe_customer_id
    customer_id = await _resolve_stripe_customer_id(
        tenant_id=body.tenant_id,
        stripe_customer_id=body.stripe_customer_id,
    )

    # Build redirect URLs
    success_url = body.success_url or (f"{_BASE_URL}/api/packs/purchase/success?session_id={{CHECKOUT_SESSION_ID}}")
    cancel_url = body.cancel_url or f"{_BASE_URL}/api/packs/purchase/cancel"

    # Create Checkout Session in payment mode
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            customer=customer_id,
            line_items=[
                {
                    "price": pack.price_id,
                    "quantity": 1,
                },
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "agent_red_pack": body.pack_id,
                "agent_red_pack_conversations": str(pack.conversations),
            },
            # Stripe Tax: calculate sales tax / VAT automatically.
            automatic_tax={"enabled": True},
            # Persist the billing address entered during checkout back
            # to the Customer object for future invoice tax calculations.
            customer_update={"address": "auto"},
        )
    except stripe.StripeError as exc:
        logger.error("Pack checkout session creation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to create pack checkout session. Please try again.",
        ) from exc

    # Format price for display
    price_display = f"${session.amount_total / 100:.2f}" if session.amount_total else "N/A"

    logger.info(
        "Pack checkout session created: session=%s pack=%s customer=%s",
        session.id,
        body.pack_id,
        customer_id,
    )

    return PurchasePackResponse(
        session_id=session.id,
        checkout_url=session.url,
        pack_id=body.pack_id,
        conversations=pack.conversations,
        price_display=price_display,
    )


@router.get(
    "/balance/{customer_id}",
    response_model=PackBalanceResponse,
    status_code=200,
    summary="Get customer pack balance",
    description=(
        "Returns the current pack balance for a customer, including active packs with remaining conversations and "
        "expiry dates."
    ),
)
async def get_balance_endpoint(customer_id: str) -> PackBalanceResponse:
    """Get the current pack balance for a customer.

    Returns active packs with remaining conversations and expiry dates.
    """
    result = get_pack_balance(stripe_customer_id=customer_id)

    return PackBalanceResponse(
        stripe_customer_id=result["stripe_customer_id"],
        total_remaining=result["total_remaining"],
        active_packs=[
            PackBalanceEntry(
                pack_id=p["pack_id"],
                remaining=p["remaining"],
                purchased_at=str(p["purchased_at"]),
                expires_at=str(p["expires_at"]),
                is_expired=p["is_expired"],
            )
            for p in result["active_packs"]
        ],
        expired_packs=result["expired_packs"],
    )
