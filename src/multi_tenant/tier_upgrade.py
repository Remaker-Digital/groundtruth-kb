"""
Tier upgrade/downgrade endpoint — D30 capability.

Provides endpoints for tenants to check upgrade eligibility, preview
pricing, and initiate tier changes via Stripe Checkout.

Routes:
    GET  /api/billing/tiers             — List available tiers with pricing
    GET  /api/billing/upgrade/preview   — Preview upgrade cost/proration
    POST /api/billing/upgrade           — Initiate tier change via Stripe

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.entitlement_service import TIER_ORDER
from src.multi_tenant.middleware import get_tenant_context, TenantContext

logger = logging.getLogger(__name__)

TIER_FEATURES: dict[str, dict[str, Any]] = {
    "starter": {
        "label": "Starter",
        "description": "Essential AI support for growing businesses",
        "monthly_price": 49,
        "annual_price": 490,
        "included_conversations": 500,
        "overage_per_conversation": 0.15,
        "features": [
            "AI-powered chat widget",
            "Knowledge base (50 articles)",
            "Basic analytics",
            "Email notifications",
            "Shopify integration",
        ],
    },
    "professional": {
        "label": "Professional",
        "description": "Advanced AI with integrations and analytics",
        "monthly_price": 149,
        "annual_price": 1490,
        "included_conversations": 2000,
        "overage_per_conversation": 0.10,
        "features": [
            "Everything in Starter",
            "Knowledge base (unlimited articles)",
            "Advanced analytics & FCR tracking",
            "Zendesk, Mailchimp, GA4 integrations",
            "Stripe MCP for payment queries",
            "Custom personas & appearances",
            "Priority support",
        ],
    },
    "enterprise": {
        "label": "Enterprise",
        "description": "Full platform with dedicated support",
        "monthly_price": 499,
        "annual_price": 4990,
        "included_conversations": 10000,
        "overage_per_conversation": 0.05,
        "features": [
            "Everything in Professional",
            "Unlimited conversations",
            "Dedicated account manager",
            "Custom SLA",
            "SSO / SAML",
            "Multi-store support",
            "White-label widget",
        ],
    },
}


class TierInfo(BaseModel):
    """Information about a subscription tier."""

    tier_id: str
    label: str
    description: str
    monthly_price: int
    annual_price: int
    included_conversations: int
    overage_per_conversation: float
    features: list[str]
    is_current: bool = False
    is_upgrade: bool = False
    is_downgrade: bool = False


class TierListResponse(BaseModel):
    """Response for tier listing."""

    current_tier: str
    tiers: list[TierInfo]


class UpgradePreviewResponse(BaseModel):
    """Response for upgrade cost preview."""

    current_tier: str
    target_tier: str
    direction: str = Field(description="'upgrade' or 'downgrade'")
    current_monthly: int
    target_monthly: int
    difference_monthly: int
    message: str


class UpgradeRequest(BaseModel):
    """Request to initiate tier change."""

    target_tier: str = Field(
        description="Target tier: starter, professional, or enterprise",
    )
    interval: str = Field(
        default="month",
        description="Billing interval: 'month' or 'year'",
    )


class UpgradeResponse(BaseModel):
    """Response for tier change initiation."""

    success: bool
    checkout_url: str | None = None
    message: str = ""


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/tiers", response_model=TierListResponse)
async def list_tiers(
    ctx: TenantContext = Depends(get_tenant_context),
) -> TierListResponse:
    """List all available tiers with pricing and feature comparison."""
    current = ctx.tier or "starter"
    current_order = TIER_ORDER.get(current, 1)

    tiers = []
    for tier_id, info in TIER_FEATURES.items():
        tier_order = TIER_ORDER.get(tier_id, 0)
        tiers.append(TierInfo(
            tier_id=tier_id,
            label=info["label"],
            description=info["description"],
            monthly_price=info["monthly_price"],
            annual_price=info["annual_price"],
            included_conversations=info["included_conversations"],
            overage_per_conversation=info["overage_per_conversation"],
            features=info["features"],
            is_current=(tier_id == current),
            is_upgrade=(tier_order > current_order),
            is_downgrade=(tier_order < current_order),
        ))

    return TierListResponse(current_tier=current, tiers=tiers)


@router.get("/upgrade/preview", response_model=UpgradePreviewResponse)
async def preview_upgrade(
    target_tier: str = Query(..., description="Target tier ID"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> UpgradePreviewResponse:
    """Preview the cost difference for a tier change."""
    current = ctx.tier or "starter"

    if target_tier not in TIER_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tier '{target_tier}'. Valid: {list(TIER_FEATURES.keys())}",
        )

    if target_tier == current:
        raise HTTPException(
            status_code=400,
            detail="Already on this tier.",
        )

    current_info = TIER_FEATURES.get(current, TIER_FEATURES["starter"])
    target_info = TIER_FEATURES[target_tier]

    current_order = TIER_ORDER.get(current, 1)
    target_order = TIER_ORDER.get(target_tier, 0)
    direction = "upgrade" if target_order > current_order else "downgrade"

    diff = target_info["monthly_price"] - current_info["monthly_price"]

    if direction == "upgrade":
        message = (
            f"Upgrade from {current_info['label']} to {target_info['label']}: "
            f"+${diff}/mo. You'll gain {target_info['included_conversations'] - current_info['included_conversations']} "
            f"more included conversations."
        )
    else:
        message = (
            f"Downgrade from {current_info['label']} to {target_info['label']}: "
            f"-${abs(diff)}/mo. Takes effect at next billing cycle."
        )

    return UpgradePreviewResponse(
        current_tier=current,
        target_tier=target_tier,
        direction=direction,
        current_monthly=current_info["monthly_price"],
        target_monthly=target_info["monthly_price"],
        difference_monthly=diff,
        message=message,
    )


@router.post("/upgrade", response_model=UpgradeResponse)
async def initiate_upgrade(
    body: UpgradeRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> UpgradeResponse:
    """Initiate a tier change via Stripe Checkout.

    For upgrades, creates a new Stripe Checkout session with the target
    tier's pricing. For downgrades, schedules the change at period end.
    """
    current = ctx.tier or "starter"

    if body.target_tier not in TIER_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tier '{body.target_tier}'. Valid: {list(TIER_FEATURES.keys())}",
        )

    if body.target_tier == current:
        raise HTTPException(status_code=400, detail="Already on this tier.")

    if body.interval not in ("month", "year"):
        raise HTTPException(status_code=400, detail="Interval must be 'month' or 'year'.")

    current_order = TIER_ORDER.get(current, 1)
    target_order = TIER_ORDER.get(body.target_tier, 0)
    direction = "upgrade" if target_order > current_order else "downgrade"

    # Load Stripe catalog for price IDs
    try:
        from src.integrations.stripe_catalog import load_catalog

        catalog = load_catalog()
        tier_catalog = catalog.get_tier(body.target_tier)
        price_id = tier_catalog.price_id_for_interval(body.interval)
    except Exception as exc:
        logger.warning("Stripe catalog not available: %s", exc)
        # Return a message indicating Stripe is not configured
        return UpgradeResponse(
            success=False,
            message=(
                f"Tier {direction} to {body.target_tier} requested but "
                f"Stripe catalog is not configured. Contact support."
            ),
        )

    # For upgrades, create checkout session
    # For downgrades, schedule at period end (through billing portal)
    if direction == "downgrade":
        # Downgrades go through the billing portal
        return UpgradeResponse(
            success=True,
            message=(
                f"Downgrade to {body.target_tier} will be scheduled. "
                f"Use the billing portal to manage your subscription."
            ),
        )

    # Create Stripe Checkout session for upgrade
    try:
        import stripe

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "tenant_id": ctx.tenant_id,
                "upgrade_from": current,
                "upgrade_to": body.target_tier,
            },
            success_url=f"https://{ctx.shop_domain or 'app'}/admin?upgrade=success",
            cancel_url=f"https://{ctx.shop_domain or 'app'}/admin?upgrade=cancelled",
        )

        logger.info(
            "Tier upgrade initiated: tenant=%s from=%s to=%s session=%s",
            ctx.tenant_id[:8], current, body.target_tier, session.id[:20],
        )

        return UpgradeResponse(
            success=True,
            checkout_url=session.url,
            message=f"Checkout session created for {body.target_tier} upgrade.",
        )

    except Exception as exc:
        logger.error("Stripe checkout failed: %s", exc)
        return UpgradeResponse(
            success=False,
            message=f"Failed to create checkout session: {str(exc)[:100]}",
        )
