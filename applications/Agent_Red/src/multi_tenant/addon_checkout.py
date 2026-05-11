# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Add-on subscription checkout — WI#138 capability.

Provides endpoints for listing available add-ons for the tenant's tier,
and initiating Stripe Checkout sessions for add-on subscriptions.

Routes:
    GET  /api/billing/addons          — List available add-ons for current tier
    POST /api/billing/addons/checkout — Start Stripe Checkout for an add-on

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.multi_tenant.middleware import TenantContext, get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class AddonInfo(BaseModel):
    """Information about an available add-on."""

    addon_id: str
    name: str
    description: str
    price_monthly: int = Field(description="Monthly price in cents")
    available_on_current_tier: bool = True


class AddonListResponse(BaseModel):
    """Response for add-on listing."""

    tenant_tier: str
    addons: list[AddonInfo]
    total: int


class AddonCheckoutRequest(BaseModel):
    """Request to start add-on checkout."""

    addon_id: str = Field(description="Add-on ID from the catalog")


class AddonCheckoutResponse(BaseModel):
    """Response for add-on checkout initiation."""

    success: bool
    checkout_url: str | None = None
    addon_id: str = ""
    message: str = ""


# ---------------------------------------------------------------------------
# Add-on metadata (static, mirrors stripe_catalog.py structure)
# ---------------------------------------------------------------------------

ADDON_META: dict[str, dict[str, Any]] = {
    "advanced_analytics": {
        "name": "Advanced Analytics",
        "description": "Deep conversation analytics, sentiment tracking, and custom reports.",
        "price_monthly": 2900,  # $29/mo
    },
    "priority_support": {
        "name": "Priority Support",
        "description": "24/7 priority support with dedicated account manager.",
        "price_monthly": 4900,  # $49/mo
    },
    "custom_branding": {
        "name": "Custom Branding",
        "description": "White-label widget with custom domain and branding removal.",
        "price_monthly": 1900,  # $19/mo
    },
    "multi_language": {
        "name": "Multi-Language Pack",
        "description": "AI responses in 20+ languages with automatic detection.",
        "price_monthly": 3900,  # $39/mo
    },
}


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/billing/addons", tags=["billing-addons"])


@router.get("", response_model=AddonListResponse)
async def list_addons(
    ctx: TenantContext = Depends(get_tenant_context),
) -> AddonListResponse:
    """List available add-ons for the tenant's current tier."""
    current_tier = ctx.tier or "starter"

    # Try loading the Stripe catalog for tier availability
    tier_available: dict[str, list[str]] = {}
    try:
        from src.integrations.stripe_catalog import load_catalog
        catalog = load_catalog()
        for addon_id, addon in catalog.addons.items():
            tier_available[addon_id] = addon.available_on
    except Exception:
        # Catalog not loaded — all add-ons shown as available
        pass

    addons = []
    for addon_id, meta in ADDON_META.items():
        available_tiers = tier_available.get(addon_id, [])
        # If catalog has availability data, check it; otherwise assume available
        is_available = (
            current_tier in available_tiers if available_tiers
            else True
        )
        addons.append(AddonInfo(
            addon_id=addon_id,
            name=meta["name"],
            description=meta["description"],
            price_monthly=meta["price_monthly"],
            available_on_current_tier=is_available,
        ))

    return AddonListResponse(
        tenant_tier=current_tier,
        addons=addons,
        total=len(addons),
    )


@router.post("/checkout", response_model=AddonCheckoutResponse)
async def checkout_addon(
    body: AddonCheckoutRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AddonCheckoutResponse:
    """Start a Stripe Checkout session for an add-on subscription.

    Creates a subscription-mode checkout session with the add-on's
    price ID from the Stripe catalog.
    """
    if body.addon_id not in ADDON_META:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown add-on '{body.addon_id}'. Available: {list(ADDON_META.keys())}",
        )

    # Load Stripe catalog for the price ID
    try:
        from src.integrations.stripe_catalog import load_catalog

        catalog = load_catalog()
        addon_catalog = catalog.get_addon(body.addon_id)

        # Check tier availability
        current_tier = ctx.tier or "starter"
        if current_tier not in addon_catalog.available_on:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Add-on '{body.addon_id}' is not available on the "
                    f"{current_tier} tier. Available on: {addon_catalog.available_on}"
                ),
            )

        price_id = addon_catalog.price_id

    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Stripe catalog not available for add-on checkout: %s", exc)
        return AddonCheckoutResponse(
            success=False,
            addon_id=body.addon_id,
            message="Stripe catalog is not configured. Contact support.",
        )

    # Create Stripe Checkout session
    try:
        import stripe

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "tenant_id": ctx.tenant_id,
                "addon_id": body.addon_id,
                "type": "addon",
            },
            success_url=f"https://{ctx.shop_domain or 'app'}/admin?addon=success",
            cancel_url=f"https://{ctx.shop_domain or 'app'}/admin?addon=cancelled",
        )

        logger.info(
            "Add-on checkout initiated: tenant=%s addon=%s session=%s",
            ctx.tenant_id[:8], body.addon_id, session.id[:20],
        )

        return AddonCheckoutResponse(
            success=True,
            checkout_url=session.url,
            addon_id=body.addon_id,
            message=f"Checkout session created for {ADDON_META[body.addon_id]['name']}.",
        )

    except Exception as exc:
        logger.error("Stripe add-on checkout failed: %s", exc)
        return AddonCheckoutResponse(
            success=False,
            addon_id=body.addon_id,
            message=f"Failed to create checkout session: {str(exc)[:100]}",
        )
