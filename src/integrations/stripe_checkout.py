"""
Stripe Checkout session management.

Provides FastAPI endpoints for creating Stripe Checkout Sessions
(subscription signup), and handling success/cancel redirects.

Tax handling (Stripe Tax):
    All Checkout Sessions are created with ``automatic_tax={"enabled": True}``.
    Stripe Tax calculates the applicable sales tax / VAT based on the
    customer's billing address (which is collected as required). Tax is
    exclusive (added on top of the listed price), matching US B2B SaaS
    convention. Products carry tax code ``txcd_10103001`` (SaaS — Business
    Use). Tax ID collection is enabled so business customers can provide
    their VAT / tax ID at checkout.

    Prerequisites (Stripe Dashboard):
      1. Origin address set to Delaware, USA.
      2. Default tax behavior set to "Exclusive".
      3. Tax registrations added for nexus states.

Affiliate tracking (Rewardful):
    When a visitor arrives via an affiliate link (?via=token), the
    Rewardful JavaScript snippet stores a referral UUID in a first-party
    cookie. The frontend reads `Rewardful.referral` and passes it as the
    `referral` field in the checkout request. This module sets it as
    `client_reference_id` on the Stripe Checkout Session. Rewardful's
    Stripe webhook integration reads this field to attribute the
    conversion to the affiliate.

    Rewardful connection requires live Stripe — test mode is not
    supported by Rewardful. However, the `client_reference_id` field
    works in both test and live mode, so the code path is safe to
    exercise during development.

Endpoints:
    POST /api/checkout/session  — Create a Checkout Session
    GET  /api/checkout/success  — Post-payment success landing
    GET  /api/checkout/cancel   — User-cancelled checkout landing

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os

import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.integrations.stripe_catalog import StripeCatalog, load_catalog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
if not stripe.api_key:
    logger.warning("STRIPE_SECRET_KEY is not set — all Stripe API calls will fail.")

# Base URL for redirect targets — override in production
_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080")

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/checkout", tags=["checkout"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class CheckoutRequest(BaseModel):
    """Request body for creating a Checkout Session."""

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
    addons: list[str] = Field(
        default_factory=list,
        description="Optional add-on IDs to include in the subscription",
        examples=[["addon_multi_language", "addon_mailchimp"]],
    )
    success_url: str | None = Field(
        default=None,
        description="Custom success redirect URL. Defaults to /api/checkout/success.",
    )
    cancel_url: str | None = Field(
        default=None,
        description="Custom cancel redirect URL. Defaults to /api/checkout/cancel.",
    )
    referral: str | None = Field(
        default=None,
        description=(
            "Rewardful referral UUID for affiliate attribution. The frontend "
            "reads this from Rewardful.referral (set by the Rewardful JS "
            "snippet when a visitor arrives via an affiliate link). Passed "
            "to Stripe as client_reference_id."
        ),
        examples=["98288128-0d5f-45a9-88b3-ef95b229f798"],
    )


class CheckoutResponse(BaseModel):
    """Response containing the Checkout Session URL."""

    session_id: str
    checkout_url: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_line_items(
    catalog: StripeCatalog,
    tier_name: str,
    interval: str,
    addon_ids: list[str],
) -> list[dict]:
    """Build the Stripe Checkout line_items list.

    Includes:
      1. The base tier price (monthly or annual)
      2. The tier's metered overage price (for usage-based billing)
      3. Any selected add-on prices
    """
    tier = catalog.get_tier(tier_name)
    items: list[dict] = []

    # 1. Base subscription price
    items.append(
        {
            "price": tier.price_id_for_interval(interval),
            "quantity": 1,
        }
    )

    # 2. Metered overage — no quantity (usage reported via Billing Meter)
    items.append(
        {
            "price": tier.overage_price_id,
        }
    )

    # 3. Add-ons
    for addon_id in addon_ids:
        catalog.validate_addon_for_tier(addon_id, tier_name)
        addon = catalog.get_addon(addon_id)
        items.append(
            {
                "price": addon.price_id,
                "quantity": 1,
            }
        )

    return items


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/session",
    response_model=CheckoutResponse,
    status_code=200,
    summary="Create a Stripe Checkout session",
    description=(
        "Creates a Stripe Checkout Session for subscription signup including base tier price, metered overage price, "
        "and any selected add-on prices as recurring line items."
    ),
    responses={
        400: {"description": "Invalid tier, billing interval, or add-on configuration"},
        502: {"description": "Stripe API error during session creation"},
    },
)
async def create_checkout_session(body: CheckoutRequest) -> CheckoutResponse:
    """Create a Stripe Checkout Session for subscription signup.

    The session includes the base tier price, metered overage price,
    and any selected add-on prices as recurring line items.
    """
    # Validate inputs
    catalog = load_catalog()

    if body.tier not in catalog.VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{body.tier}'. Must be one of: {sorted(catalog.VALID_TIERS)}",
        )

    if body.interval not in catalog.VALID_INTERVALS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval '{body.interval}'. Must be 'month' or 'year'.",
        )

    # Validate add-ons
    for addon_id in body.addons:
        try:
            catalog.validate_addon_for_tier(addon_id, body.tier)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Build line items
    line_items = _build_line_items(catalog, body.tier, body.interval, body.addons)

    # Redirect URLs
    success_url = body.success_url or f"{_BASE_URL}/api/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = body.cancel_url or f"{_BASE_URL}/api/checkout/cancel"

    # Build Checkout Session parameters
    checkout_params: dict = {
        "mode": "subscription",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
        # Store tier info for webhook processing
        "metadata": {
            "agent_red_tier": body.tier,
            "agent_red_interval": body.interval,
            "agent_red_addons": ",".join(body.addons) if body.addons else "",
        },
        "subscription_data": {
            "metadata": {
                "agent_red_tier": body.tier,
                "agent_red_interval": body.interval,
            },
        },
        # Let Stripe collect billing address for tax
        "billing_address_collection": "required",
        # Allow promotion codes at checkout
        "allow_promotion_codes": True,
        # Stripe Tax: calculate sales tax / VAT automatically based on
        # the customer's billing address. Requires origin address and
        # tax registrations to be configured in Stripe Dashboard.
        "automatic_tax": {"enabled": True},
        # Allow business customers to provide their tax ID (VAT, etc.)
        # at checkout. Stripe validates the ID format automatically.
        "tax_id_collection": {"enabled": True},
    }

    # Rewardful affiliate tracking: pass the referral UUID as
    # client_reference_id so Rewardful can attribute the conversion.
    # Stripe raises an error if client_reference_id is empty string,
    # so only include it when a referral is actually present.
    if body.referral:
        checkout_params["client_reference_id"] = body.referral
        logger.info("Affiliate referral attached: referral=%s", body.referral)

    # Create the Checkout Session
    try:
        session = stripe.checkout.Session.create(**checkout_params)
    except stripe.StripeError as exc:
        logger.error("Stripe Checkout Session creation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to create checkout session. Please try again.",
        ) from exc

    logger.info(
        "Checkout session created: session=%s tier=%s interval=%s addons=%s referral=%s",
        session.id,
        body.tier,
        body.interval,
        body.addons,
        body.referral or "none",
    )

    return CheckoutResponse(
        session_id=session.id,
        checkout_url=session.url,
    )


@router.get(
    "/success",
    status_code=200,
    summary="Handle successful checkout redirect",
    description=(
        "Handles the post-payment success redirect from Stripe. Returns session details or a thank-you message."
    ),
)
async def checkout_success(request: Request) -> JSONResponse:
    """Handle successful checkout redirect.

    In production, this would redirect to a branded thank-you page
    or trigger tenant provisioning. For now, returns session details.
    """
    session_id = request.query_params.get("session_id")

    if not session_id:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thank you for subscribing to Agent Red!",
            },
        )

    try:
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=["subscription", "customer"],
        )
    except stripe.StripeError as exc:
        logger.warning("Failed to retrieve checkout session %s: %s", session_id, exc)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thank you for subscribing to Agent Red!",
                "session_id": session_id,
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Thank you for subscribing to Agent Red!",
            "session_id": session.id,
            "customer_email": session.customer_details.email if session.customer_details else None,
            "subscription_id": session.subscription.id if session.subscription else None,
            "tier": session.metadata.get("agent_red_tier"),
        },
    )


@router.get(
    "/cancel",
    status_code=200,
    summary="Handle cancelled checkout redirect",
    description="Handles the cancelled checkout redirect. Returns a message indicating checkout was not completed.",
)
async def checkout_cancel() -> JSONResponse:
    """Handle cancelled checkout redirect.

    Returns a message indicating the checkout was not completed.
    In production, this would redirect to the pricing page.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "cancelled",
            "message": "Checkout was cancelled. No charges were made.",
            "next": f"{_BASE_URL}/pricing",
        },
    )
