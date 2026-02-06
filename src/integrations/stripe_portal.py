"""
Stripe Customer Portal session management.

Creates Stripe Billing Portal sessions so customers can self-service
their subscription: update payment methods, view invoices, cancel or
resume, and switch between plans.

The portal's available features (plan switching, cancellation, invoice
history, etc.) are configured in the Stripe Dashboard under
Settings → Billing → Customer Portal, not in code.

Endpoint:
    POST /api/billing/portal  — Create a Customer Portal session

Flow:
    1. Frontend sends POST /api/billing/portal with customer identifier
       (tenant_id or stripe_customer_id).
    2. Module looks up the Stripe customer ID (via provisioning service
       if tenant_id is provided).
    3. Creates a Stripe Billing Portal session with a return_url.
    4. Returns the portal URL for frontend redirect.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.integrations.provisioning import get_tenant

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

# Base URL for the return redirect after the customer exits the portal
_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080")

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/billing", tags=["billing"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class PortalRequest(BaseModel):
    """Request to create a Stripe Customer Portal session.

    Provide either tenant_id (channel-agnostic) or stripe_customer_id
    (direct Stripe lookup). If both are provided, stripe_customer_id
    takes precedence.
    """

    tenant_id: str | None = Field(
        default=None,
        description=(
            "Tenant ID (UUID). The module looks up the Stripe customer ID "
            "from the provisioning service."
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    stripe_customer_id: str | None = Field(
        default=None,
        description="Stripe customer ID (cus_...) for direct lookup.",
        examples=["cus_ABC123"],
    )
    return_url: str | None = Field(
        default=None,
        description=(
            "URL to redirect the customer back to after they exit the portal. "
            "Defaults to the application base URL."
        ),
    )


class PortalResponse(BaseModel):
    """Response containing the Customer Portal session URL."""

    portal_url: str = Field(description="URL to redirect the customer to.")
    stripe_customer_id: str = Field(description="The Stripe customer ID used.")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _resolve_stripe_customer_id(
    tenant_id: str | None,
    stripe_customer_id: str | None,
) -> str:
    """Resolve a Stripe customer ID from the provided identifiers.

    Priority:
        1. stripe_customer_id (if provided directly)
        2. tenant_id → lookup via provisioning service → stripe_customer_id

    Args:
        tenant_id: Tenant UUID for provisioning lookup.
        stripe_customer_id: Direct Stripe customer ID.

    Returns:
        Resolved Stripe customer ID string.

    Raises:
        HTTPException: If no identifier is provided, tenant not found,
            or tenant has no Stripe customer ID.
    """
    if stripe_customer_id:
        return stripe_customer_id

    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'tenant_id' or 'stripe_customer_id'.",
        )

    tenant = get_tenant(tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant '{tenant_id}' not found.",
        )

    if not tenant.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tenant '{tenant_id}' does not have a Stripe customer ID. "
                "This tenant may use Shopify billing. The Customer Portal "
                "is only available for Stripe-billed customers."
            ),
        )

    return tenant.stripe_customer_id


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/portal",
    response_model=PortalResponse,
    status_code=200,
    summary="Create a Customer Portal session",
    description="Creates a Stripe Customer Portal session where the customer can manage their subscription, update payment methods, view invoices, and cancel or resume.",
    responses={
        400: {"description": "Missing tenant_id and stripe_customer_id, or tenant has no Stripe billing"},
        404: {"description": "Tenant not found"},
        502: {"description": "Stripe API error during portal session creation"},
    },
)
async def create_portal_session(body: PortalRequest) -> PortalResponse:
    """Create a Stripe Customer Portal session.

    The customer is redirected to Stripe's hosted portal where they can:
    - Update their payment method
    - View and download invoices
    - Cancel or resume their subscription
    - Switch between plans (if configured in Stripe Dashboard)

    Accepts either a tenant_id (looked up via provisioning) or a direct
    stripe_customer_id. Returns the portal URL for frontend redirect.
    """
    customer_id = _resolve_stripe_customer_id(
        tenant_id=body.tenant_id,
        stripe_customer_id=body.stripe_customer_id,
    )

    return_url = body.return_url or _BASE_URL

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
    except stripe.StripeError as exc:
        logger.error(
            "Stripe portal session creation failed: customer=%s error=%s",
            customer_id,
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail="Failed to create Customer Portal session. Please try again.",
        ) from exc

    logger.info(
        "Portal session created: customer=%s url=%s",
        customer_id,
        session.url,
    )

    return PortalResponse(
        portal_url=session.url,
        stripe_customer_id=customer_id,
    )
