"""
Shopify Billing API integration.

Manages subscription billing for merchants who install Agent Red from
the Shopify App Store. Uses Shopify's AppSubscription API (GraphQL Admin)
to create recurring + usage-based billing plans.

Billing model:
    - Recurring base fee: Platform subscription (Starter/Professional/Enterprise)
    - Usage charges: Per-conversation overage beyond the tier's included allowance
    - Shopify handles all payment collection, invoicing, and payouts

Important: Shopify does NOT support usage billing with ANNUAL interval.
    - Monthly subscriptions: recurring base + usage overage (full support)
    - Annual subscriptions: recurring base ONLY (overage handled separately)

Flow:
    1. Merchant clicks "Install" → Shopify OAuth → app installed
    2. App calls POST /api/shopify/billing/subscribe with tier + interval
    3. Module creates an AppSubscription via GraphQL with:
       - appRecurringPricingDetails (base platform fee)
       - appUsagePricingDetails (metered overage — monthly only)
    4. Merchant approves the charge on Shopify's confirmation page
    5. App receives the confirmation via GET /api/shopify/billing/confirm
    6. After each conversation, record_shopify_usage() reports overage

Endpoints:
    POST /api/shopify/billing/subscribe    — Create subscription charge
    GET  /api/shopify/billing/confirm      — Handle merchant approval redirect
    GET  /api/shopify/billing/status       — Get current billing status

Shopify Billing API reference:
    https://shopify.dev/docs/apps/billing

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from src.integrations.provisioning import (
    BillingChannel,
    activate_tenant,
    provision_tenant,
)
from src.integrations.shopify_client import (
    ShopifyAPIError,
    ShopifyGraphQLError,
    get_shopify_client,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080")

# Shopify billing intervals
_INTERVAL_MAP = {
    "month": "EVERY_30_DAYS",
    "year": "ANNUAL",
}

# ---------------------------------------------------------------------------
# Pricing catalog (mirrors Stripe catalog for the Shopify channel)
#
# Shopify Billing API does not use Stripe Price IDs — it takes amounts
# directly. This mapping ensures pricing parity between channels.
# ---------------------------------------------------------------------------

_TIER_PRICING: dict[str, dict[str, Any]] = {
    "starter": {
        "name": "Agent Red Starter",
        "monthly": Decimal("149.00"),
        "annual_total": Decimal("1490.00"),
        "overage_rate": Decimal("0.04"),
        "included_conversations": 1000,
        "capped_amount": Decimal("500.00"),  # Max $500/mo overage (12,500 extra conversations)
    },
    "professional": {
        "name": "Agent Red Professional",
        "monthly": Decimal("399.00"),
        "annual_total": Decimal("3990.00"),
        "overage_rate": Decimal("0.025"),
        "included_conversations": 5000,
        "capped_amount": Decimal("1000.00"),  # Max $1,000/mo overage (40,000 extra conversations)
    },
    "enterprise": {
        "name": "Agent Red Enterprise",
        "monthly": Decimal("999.00"),
        "annual_total": Decimal("9990.00"),
        "overage_rate": Decimal("0.015"),
        "included_conversations": 20000,
        "capped_amount": Decimal("2000.00"),  # Max $2,000/mo overage (133,333 extra conversations)
    },
}

VALID_TIERS = frozenset(_TIER_PRICING.keys())
VALID_INTERVALS = frozenset({"month", "year"})

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/shopify/billing", tags=["shopify-billing"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class SubscribeRequest(BaseModel):
    """Request to create a Shopify app subscription."""

    tier: str = Field(
        ...,
        description="Subscription tier: starter, professional, or enterprise",
        examples=["starter"],
    )
    interval: str = Field(
        ...,
        description="Billing interval: month or year",
        examples=["month"],
    )
    shop_domain: str = Field(
        ...,
        description="The merchant's Shopify store domain (e.g. my-store.myshopify.com)",
        examples=["my-store.myshopify.com"],
    )


class SubscribeResponse(BaseModel):
    """Response containing the Shopify approval URL."""

    confirmation_url: str
    subscription_name: str
    tier: str
    interval: str
    base_price: float
    overage_cap: float


class BillingStatusResponse(BaseModel):
    """Current billing status for a Shopify merchant."""

    shop_domain: str
    has_active_subscription: bool
    subscription_name: str | None = None
    status: str | None = None
    created_at: str | None = None
    current_period_end: str | None = None


class UsageRecordResponse(BaseModel):
    """Response after recording a usage charge."""

    shop_domain: str
    amount: float
    description: str
    idempotency_key: str
    success: bool


# ---------------------------------------------------------------------------
# GraphQL mutations & queries
# ---------------------------------------------------------------------------

# Create a recurring + usage-based app subscription
_CREATE_SUBSCRIPTION_MUTATION = """
mutation appSubscriptionCreate(
    $name: String!
    $returnUrl: URL!
    $trialDays: Int
    $test: Boolean
    $lineItems: [AppSubscriptionLineItemInput!]!
) {
    appSubscriptionCreate(
        name: $name
        returnUrl: $returnUrl
        trialDays: $trialDays
        test: $test
        lineItems: $lineItems
    ) {
        appSubscription {
            id
            name
            status
            createdAt
            currentPeriodEnd
        }
        confirmationUrl
        userErrors {
            field
            message
        }
    }
}
"""

# Record a usage charge against an active subscription
_CREATE_USAGE_RECORD_MUTATION = """
mutation appUsageRecordCreate(
    $subscriptionLineItemId: ID!
    $price: MoneyInput!
    $description: String!
    $idempotencyKey: String!
) {
    appUsageRecordCreate(
        subscriptionLineItemId: $subscriptionLineItemId
        price: $price
        description: $description
        idempotencyKey: $idempotencyKey
    ) {
        appUsageRecord {
            id
            createdAt
        }
        userErrors {
            field
            message
        }
    }
}
"""

# Query the current active subscription
_ACTIVE_SUBSCRIPTION_QUERY = """
query {
    currentAppInstallation {
        activeSubscriptions {
            id
            name
            status
            createdAt
            currentPeriodEnd
            lineItems {
                id
                plan {
                    pricingDetails {
                        __typename
                        ... on AppRecurringPricing {
                            price {
                                amount
                                currencyCode
                            }
                            interval
                        }
                        ... on AppUsagePricing {
                            cappedAmount {
                                amount
                                currencyCode
                            }
                            terms
                        }
                    }
                }
            }
        }
    }
}
"""


# ---------------------------------------------------------------------------
# In-memory subscription tracking (DEVELOPMENT ONLY)
#
# WARNING: Same caveats as stripe_usage.py in-memory counters.
# Production replacement (Phase 2.2): Cosmos DB with tenant partitioning.
#
# Structure: { shop_domain: { subscription_id, usage_line_item_id, tier, ... } }
# ---------------------------------------------------------------------------

_shop_subscriptions: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _get_tier_pricing(tier: str) -> dict[str, Any]:
    """Get pricing config for a tier, raising ValueError if invalid."""
    if tier not in VALID_TIERS:
        raise ValueError(
            f"Invalid tier '{tier}'. Must be one of: {sorted(VALID_TIERS)}"
        )
    return _TIER_PRICING[tier]


def _is_test_mode() -> bool:
    """Check if we should create test subscriptions.

    Test subscriptions are not billed to the merchant and are useful
    for development and app review.
    """
    return os.environ.get("SHOPIFY_BILLING_TEST", "true").lower() == "true"


async def create_subscription(
    shop_domain: str,
    tier: str,
    interval: str,
    return_url: str | None = None,
) -> dict[str, Any]:
    """Create a Shopify app subscription for a merchant.

    Creates a subscription using Shopify's appSubscriptionCreate mutation.

    For monthly subscriptions:
        - Recurring base fee + usage-based overage line item (combined plan)

    For annual subscriptions:
        - Recurring base fee ONLY (Shopify does not support usage billing
          with ANNUAL interval). Overage for annual subscribers must be
          handled separately — see TODO below.

    Args:
        shop_domain: Merchant's .myshopify.com domain.
        tier: Subscription tier (starter, professional, enterprise).
        interval: Billing interval (month or year).
        return_url: URL to redirect after merchant approval.

    Returns:
        Dict with confirmation_url, subscription details.

    Raises:
        ValueError: If tier or interval is invalid.
        ShopifyGraphQLError: If the mutation returns user errors.
    """
    pricing = _get_tier_pricing(tier)

    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval '{interval}'. Must be 'month' or 'year'."
        )

    shopify_interval = _INTERVAL_MAP[interval]

    # Determine base price based on interval
    if interval == "year":
        base_price = pricing["annual_total"]
    else:
        base_price = pricing["monthly"]

    # Build subscription name
    interval_label = "Annual" if interval == "year" else "Monthly"
    subscription_name = f"{pricing['name']} ({interval_label})"

    # Build the return URL for post-approval redirect
    if return_url is None:
        return_url = (
            f"{_BASE_URL}/api/shopify/billing/confirm"
            f"?shop={shop_domain}&tier={tier}&interval={interval}"
        )

    # Build line items
    #
    # IMPORTANT: Shopify does NOT support usage billing with ANNUAL interval.
    # Annual subscriptions get only the recurring base fee line item.
    # Monthly subscriptions get both recurring base + usage overage.
    line_items: list[dict[str, Any]] = [
        {
            "plan": {
                "appRecurringPricingDetails": {
                    "price": {
                        "amount": str(base_price),
                        "currencyCode": "USD",
                    },
                    "interval": shopify_interval,
                },
            },
        },
    ]

    overage_cap = Decimal("0.00")

    if interval == "month":
        # Add usage-based overage line item (monthly only)
        overage_cap = pricing["capped_amount"]
        line_items.append({
            "plan": {
                "appUsagePricingDetails": {
                    "cappedAmount": {
                        "amount": str(overage_cap),
                        "currencyCode": "USD",
                    },
                    "terms": (
                        f"Overage billing: ${pricing['overage_rate']} per conversation "
                        f"beyond {pricing['included_conversations']:,} included conversations "
                        f"per billing cycle. Maximum overage charge: "
                        f"${overage_cap} per cycle."
                    ),
                },
            },
        })
    else:
        # Annual plan — no usage line item
        # TODO (Phase 2.2): Handle annual overage via one-time app charges
        # (appPurchaseOneTimeCreate) at 30-day intervals, or encourage
        # annual merchants to pre-purchase conversation packs via Stripe.
        logger.info(
            "Annual subscription for shop=%s — usage billing not included "
            "(Shopify does not support usage charges with ANNUAL interval). "
            "Overage must be handled separately.",
            shop_domain,
        )

    # Execute the mutation
    client = get_shopify_client()

    variables = {
        "name": subscription_name,
        "returnUrl": return_url,
        "test": _is_test_mode(),
        "lineItems": line_items,
    }

    data = await client.execute(_CREATE_SUBSCRIPTION_MUTATION, variables)
    result = data.get("appSubscriptionCreate", {})

    # Check for user errors
    user_errors = result.get("userErrors", [])
    if user_errors:
        error_messages = [e.get("message", str(e)) for e in user_errors]
        logger.error(
            "Shopify subscription creation failed: shop=%s errors=%s",
            shop_domain,
            error_messages,
        )
        raise ShopifyGraphQLError(error_messages)

    subscription = result.get("appSubscription", {})
    confirmation_url = result.get("confirmationUrl", "")

    # Store subscription info for later usage recording
    _shop_subscriptions[shop_domain] = {
        "subscription_id": subscription.get("id"),
        "tier": tier,
        "interval": interval,
        "status": "pending_approval",
        "pricing": pricing,
    }

    logger.info(
        "Shopify subscription created: shop=%s tier=%s interval=%s sub_id=%s",
        shop_domain,
        tier,
        interval,
        subscription.get("id"),
    )

    return {
        "confirmation_url": confirmation_url,
        "subscription_name": subscription_name,
        "subscription": subscription,
        "tier": tier,
        "interval": interval,
        "base_price": float(base_price),
        "overage_cap": float(overage_cap),
    }


async def confirm_subscription(
    shop_domain: str,
    charge_id: str | None = None,
) -> dict[str, Any]:
    """Handle post-approval confirmation.

    After the merchant approves the charge on Shopify's confirmation
    page, they are redirected back to our return_url. This function
    queries the current active subscription to confirm activation and
    retrieves the usage line item ID needed for recording overage.

    Args:
        shop_domain: Merchant's .myshopify.com domain.
        charge_id: Optional charge_id from Shopify redirect query params.

    Returns:
        Dict with subscription status and line item IDs.
    """
    client = get_shopify_client()
    data = await client.execute(_ACTIVE_SUBSCRIPTION_QUERY)

    installation = data.get("currentAppInstallation", {})
    subscriptions = installation.get("activeSubscriptions", [])

    if not subscriptions:
        logger.warning(
            "No active subscription found after confirmation: shop=%s",
            shop_domain,
        )
        return {
            "shop_domain": shop_domain,
            "status": "no_active_subscription",
            "subscriptions": [],
        }

    # Take the most recent active subscription
    active_sub = subscriptions[0]

    # Find the usage line item (for recording overage charges)
    usage_line_item_id = None
    for line_item in active_sub.get("lineItems", []):
        pricing_details = line_item.get("plan", {}).get("pricingDetails", {})
        if pricing_details.get("__typename") == "AppUsagePricing":
            usage_line_item_id = line_item["id"]
            break

    # Update local tracking
    if shop_domain in _shop_subscriptions:
        _shop_subscriptions[shop_domain].update({
            "subscription_id": active_sub["id"],
            "usage_line_item_id": usage_line_item_id,
            "status": "active",
        })
    else:
        _shop_subscriptions[shop_domain] = {
            "subscription_id": active_sub["id"],
            "usage_line_item_id": usage_line_item_id,
            "status": "active",
            "tier": None,  # Unknown if not created through our flow
            "interval": None,
        }

    logger.info(
        "Shopify subscription confirmed: shop=%s sub_id=%s usage_item=%s",
        shop_domain,
        active_sub["id"],
        usage_line_item_id,
    )

    # Provision and activate tenant via channel-agnostic provisioning service.
    # Shopify confirmation is both provisioning AND activation in one step
    # (payment is already confirmed by the time the merchant is redirected back).
    sub_info = _shop_subscriptions.get(shop_domain, {})
    tenant = provision_tenant(
        billing_channel=BillingChannel.SHOPIFY,
        tier=sub_info.get("tier"),
        interval=sub_info.get("interval"),
        shopify_shop_domain=shop_domain,
        shopify_subscription_id=active_sub["id"],
    )

    # Immediately activate — Shopify collects payment during approval
    activated = activate_tenant(shopify_shop_domain=shop_domain)

    result = {
        "shop_domain": shop_domain,
        "status": "active",
        "subscription_id": active_sub["id"],
        "subscription_name": active_sub.get("name"),
        "usage_line_item_id": usage_line_item_id,
        "created_at": active_sub.get("createdAt"),
        "current_period_end": active_sub.get("currentPeriodEnd"),
        "tenant_id": tenant.tenant_id,
        "tenant_status": (activated.status.value if activated else tenant.status.value),
    }

    return result


async def record_shopify_usage(
    shop_domain: str,
    overage_count: int,
    idempotency_key: str,
) -> dict[str, Any]:
    """Record conversation overage as a Shopify usage charge.

    Called when a merchant's conversation count exceeds their tier's
    included allowance. Only overage conversations are charged.

    Args:
        shop_domain: Merchant's .myshopify.com domain.
        overage_count: Number of overage conversations to bill.
        idempotency_key: Unique key to prevent duplicate charges.

    Returns:
        Dict with usage record details.

    Raises:
        ValueError: If no active subscription or usage line item found.
    """
    sub_info = _shop_subscriptions.get(shop_domain)
    if not sub_info:
        raise ValueError(
            f"No subscription found for shop '{shop_domain}'. "
            "Merchant must subscribe first."
        )

    usage_line_item_id = sub_info.get("usage_line_item_id")
    if not usage_line_item_id:
        raise ValueError(
            f"No usage line item found for shop '{shop_domain}'. "
            "Subscription may not have a usage component."
        )

    pricing = sub_info.get("pricing", {})
    overage_rate = pricing.get("overage_rate", Decimal("0.04"))  # Default to Starter rate
    # Use Decimal arithmetic to avoid floating-point precision issues in billing
    charge_amount = Decimal(str(overage_count)) * Decimal(str(overage_rate))
    charge_amount = charge_amount.quantize(Decimal("0.01"))  # Round to cents

    tier_name = sub_info.get("tier", "unknown")
    included = pricing.get("included_conversations", 0)

    description = (
        f"{overage_count} conversation(s) beyond {included:,} included "
        f"({tier_name} tier) @ ${overage_rate}/conversation"
    )

    client = get_shopify_client()

    # Shopify MoneyInput.amount is type Decimal! — pass as string
    variables = {
        "subscriptionLineItemId": usage_line_item_id,
        "price": {
            "amount": str(charge_amount),
            "currencyCode": "USD",
        },
        "description": description,
        "idempotencyKey": idempotency_key,
    }

    data = await client.execute(_CREATE_USAGE_RECORD_MUTATION, variables)
    result = data.get("appUsageRecordCreate", {})

    user_errors = result.get("userErrors", [])
    if user_errors:
        error_messages = [e.get("message", str(e)) for e in user_errors]
        logger.error(
            "Shopify usage record failed: shop=%s errors=%s",
            shop_domain,
            error_messages,
        )
        return {
            "shop_domain": shop_domain,
            "amount": float(charge_amount),
            "description": description,
            "idempotency_key": idempotency_key,
            "success": False,
            "errors": error_messages,
        }

    usage_record = result.get("appUsageRecord", {})

    logger.info(
        "Shopify usage recorded: shop=%s amount=$%s overage=%d key=%s",
        shop_domain,
        charge_amount,
        overage_count,
        idempotency_key,
    )

    return {
        "shop_domain": shop_domain,
        "amount": float(charge_amount),
        "description": description,
        "idempotency_key": idempotency_key,
        "success": True,
        "record_id": usage_record.get("id"),
        "created_at": usage_record.get("createdAt"),
    }


async def get_billing_status(shop_domain: str) -> dict[str, Any]:
    """Get the current billing status for a merchant.

    Queries Shopify for the active subscription and returns
    a summary of the billing state.

    Args:
        shop_domain: Merchant's .myshopify.com domain.

    Returns:
        Dict with billing status details.
    """
    client = get_shopify_client()
    data = await client.execute(_ACTIVE_SUBSCRIPTION_QUERY)

    installation = data.get("currentAppInstallation", {})
    subscriptions = installation.get("activeSubscriptions", [])

    if not subscriptions:
        return {
            "shop_domain": shop_domain,
            "has_active_subscription": False,
        }

    active_sub = subscriptions[0]

    return {
        "shop_domain": shop_domain,
        "has_active_subscription": True,
        "subscription_name": active_sub.get("name"),
        "status": active_sub.get("status"),
        "created_at": active_sub.get("createdAt"),
        "current_period_end": active_sub.get("currentPeriodEnd"),
        "subscription_id": active_sub["id"],
        "line_items": [
            {
                "id": li["id"],
                "pricing_type": li.get("plan", {}).get("pricingDetails", {}).get("__typename"),
            }
            for li in active_sub.get("lineItems", [])
        ],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/subscribe",
    response_model=SubscribeResponse,
    status_code=200,
    summary="Create a Shopify app subscription",
    description="Creates a Shopify app subscription for a merchant. The merchant will be redirected to Shopify's confirmation page to approve the charge.",
    responses={
        400: {"description": "Invalid tier or billing interval"},
        502: {"description": "Shopify GraphQL API error during subscription creation"},
    },
)
async def subscribe_endpoint(body: SubscribeRequest) -> SubscribeResponse:
    """Create a Shopify app subscription for a merchant.

    The merchant will be redirected to Shopify's confirmation page
    to approve the charge. After approval, they are redirected back
    to /api/shopify/billing/confirm.
    """
    # Validate inputs
    if body.tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{body.tier}'. Must be one of: {sorted(VALID_TIERS)}",
        )

    if body.interval not in VALID_INTERVALS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval '{body.interval}'. Must be 'month' or 'year'.",
        )

    try:
        result = await create_subscription(
            shop_domain=body.shop_domain,
            tier=body.tier,
            interval=body.interval,
        )
    except (ShopifyAPIError, ShopifyGraphQLError) as exc:
        logger.error("Shopify subscription creation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to create Shopify subscription. Please try again.",
        ) from exc

    return SubscribeResponse(
        confirmation_url=result["confirmation_url"],
        subscription_name=result["subscription_name"],
        tier=result["tier"],
        interval=result["interval"],
        base_price=result["base_price"],
        overage_cap=result["overage_cap"],
    )


@router.get(
    "/confirm",
    status_code=200,
    summary="Handle Shopify post-approval redirect",
    description="Handles Shopify's post-approval redirect after a merchant approves the subscription charge. Confirms the subscription is active and provisions the tenant.",
    responses={
        400: {"description": "Missing shop query parameter"},
        502: {"description": "Shopify API error during subscription confirmation"},
    },
)
async def confirm_endpoint(request: Request) -> JSONResponse:
    """Handle Shopify's post-approval redirect.

    After the merchant approves the charge on Shopify, they are
    redirected here. We confirm the subscription is active and
    store the usage line item ID for overage recording.

    In production, this would redirect to a branded onboarding page.
    """
    shop_domain = request.query_params.get("shop", "")
    charge_id = request.query_params.get("charge_id")

    if not shop_domain:
        raise HTTPException(
            status_code=400,
            detail="Missing 'shop' query parameter.",
        )

    try:
        result = await confirm_subscription(
            shop_domain=shop_domain,
            charge_id=charge_id,
        )
    except (ShopifyAPIError, ShopifyGraphQLError) as exc:
        logger.error("Shopify subscription confirmation failed: %s", exc)
        return JSONResponse(
            status_code=502,
            content={
                "status": "error",
                "message": "Could not confirm subscription. Please contact support.",
                "shop": shop_domain,
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "confirmed",
            "message": "Your Agent Red subscription is now active!",
            "shop": shop_domain,
            "subscription_name": result.get("subscription_name"),
        },
    )


@router.get(
    "/status",
    response_model=BillingStatusResponse,
    status_code=200,
    summary="Get Shopify merchant billing status",
    description="Returns the current billing status for a Shopify merchant, including active subscription details and line items.",
    responses={
        400: {"description": "Missing shop query parameter"},
        502: {"description": "Shopify API error during status retrieval"},
    },
)
async def status_endpoint(shop: str) -> BillingStatusResponse:
    """Get the current billing status for a Shopify merchant.

    Query parameters:
        shop: The merchant's Shopify store domain (required).
    """
    if not shop:
        raise HTTPException(
            status_code=400,
            detail="Missing 'shop' query parameter.",
        )

    try:
        result = await get_billing_status(shop_domain=shop)
    except (ShopifyAPIError, ShopifyGraphQLError) as exc:
        logger.error("Shopify billing status check failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve billing status from Shopify.",
        ) from exc

    return BillingStatusResponse(
        shop_domain=result["shop_domain"],
        has_active_subscription=result["has_active_subscription"],
        subscription_name=result.get("subscription_name"),
        status=result.get("status"),
        created_at=result.get("created_at"),
        current_period_end=result.get("current_period_end"),
    )
