"""
Tenant provisioning service.

Channel-agnostic interface for managing tenant lifecycle. Both Stripe
(direct billing) and Shopify (App Store billing) feed into this service
to create, update, and deactivate tenants.

This abstraction ensures downstream code (usage tracking, feature gating,
API key management) doesn't need to know which billing channel the
customer uses.

Tenant lifecycle:
    1. provision_tenant()  — New subscription → create tenant record
    2. activate_tenant()   — Payment confirmed → mark tenant active
    3. update_tenant()     — Tier/interval change → update tenant record
    4. deactivate_tenant() — Cancellation → begin grace period
    5. flag_payment_issue() — Failed payment → restrict access

Billing channel mapping:
    - Stripe: customer identified by stripe_customer_id (cus_...)
    - Shopify: customer identified by shop_domain (*.myshopify.com)
    - Tenant ID: generated UUID, channel-independent

Endpoints:
    GET /api/tenants/{tenant_id}     — Get tenant status
    GET /api/tenants/lookup          — Lookup by Stripe ID or Shopify domain

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
import uuid
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class BillingChannel(str, Enum):
    """Billing channel through which the customer subscribes."""

    STRIPE = "stripe"
    SHOPIFY = "shopify"
    TRIAL = "trial"


class TenantStatus(str, Enum):
    """Lifecycle status of a tenant."""

    PROVISIONING = "provisioning"    # Checkout completed, setting up
    ACTIVE = "active"                # Payment confirmed, fully operational
    PAST_DUE = "past_due"            # Payment failed, limited access
    GRACE_PERIOD = "grace_period"    # Cancelled, data preserved (30 days)
    DEACTIVATED = "deactivated"      # Grace period expired, access revoked
    TRIAL_EXPIRED = "trial_expired"  # Trial period ended, must subscribe


# ---------------------------------------------------------------------------
# Tenant record
# ---------------------------------------------------------------------------


class TenantRecord(BaseModel):
    """A tenant's complete billing and provisioning state.

    This record is the single source of truth for a tenant's status,
    regardless of billing channel. All downstream systems (usage
    tracking, feature flags, API gateway) read from this record.
    """

    tenant_id: str = Field(description="Unique tenant identifier (UUID)")
    status: TenantStatus = Field(description="Current lifecycle status")
    billing_channel: BillingChannel = Field(description="stripe or shopify")

    # Tier & plan
    tier: str | None = Field(default=None, description="starter/professional/enterprise")
    interval: str | None = Field(default=None, description="month or year")
    addons: list[str] = Field(default_factory=list, description="Active add-on IDs")

    # Channel-specific identifiers
    stripe_customer_id: str | None = Field(default=None, description="Stripe cus_...")
    stripe_subscription_id: str | None = Field(default=None, description="Stripe sub_...")
    shopify_shop_domain: str | None = Field(default=None, description="*.myshopify.com")
    shopify_subscription_id: str | None = Field(default=None, description="Shopify gid://...")

    # Contact
    customer_email: str | None = Field(default=None, description="Primary contact email")

    # Timestamps (Unix epoch)
    created_at: int = Field(description="When tenant was provisioned")
    updated_at: int = Field(description="Last status change")
    deactivated_at: int | None = Field(default=None, description="When cancellation began")
    grace_period_ends_at: int | None = Field(default=None, description="When data will be deleted")


# ---------------------------------------------------------------------------
# In-memory tenant store (DEVELOPMENT ONLY)
#
# WARNING: Same caveats as other in-memory stores in this codebase:
#   1. Lost on restart.
#   2. Not shared across workers.
#   3. Non-atomic operations.
#
# Production replacement (Phase 2.2): Cosmos DB with:
#   - Partition key: tenant_id
#   - Secondary indexes on stripe_customer_id, shopify_shop_domain
#   - Change feed for downstream event propagation
#
# Indexes:
#   _tenants:        { tenant_id: TenantRecord }
#   _stripe_index:   { stripe_customer_id: tenant_id }
#   _shopify_index:  { shop_domain: tenant_id }
# ---------------------------------------------------------------------------

_tenants: dict[str, TenantRecord] = {}
_stripe_index: dict[str, str] = {}   # stripe_customer_id → tenant_id
_shopify_index: dict[str, str] = {}  # shop_domain → tenant_id

# Grace period in seconds (30 days, per SLA)
_GRACE_PERIOD_SECONDS = 30 * 24 * 60 * 60

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class TenantResponse(BaseModel):
    """Public tenant status response (no internal IDs exposed)."""

    tenant_id: str
    status: TenantStatus
    billing_channel: BillingChannel
    tier: str | None
    interval: str | None
    addons: list[str]
    created_at: int
    updated_at: int


class TenantLookupResponse(BaseModel):
    """Response for tenant lookup by channel identifier."""

    found: bool
    tenant_id: str | None = None
    status: TenantStatus | None = None
    tier: str | None = None
    billing_channel: BillingChannel | None = None


# ---------------------------------------------------------------------------
# Core provisioning logic
# ---------------------------------------------------------------------------


def provision_tenant(
    billing_channel: BillingChannel,
    tier: str | None = None,
    interval: str | None = None,
    addons: list[str] | None = None,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    shopify_shop_domain: str | None = None,
    shopify_subscription_id: str | None = None,
    customer_email: str | None = None,
) -> TenantRecord:
    """Provision a new tenant after checkout completion.

    Called by:
        - stripe_webhooks.handle_checkout_completed (subscription checkout)
        - shopify_billing.confirm_subscription

    If a tenant already exists for the given channel identifier (Stripe
    customer ID or Shopify domain), it is updated rather than duplicated.

    Args:
        billing_channel: stripe or shopify.
        tier: Subscription tier name.
        interval: Billing interval (month or year).
        addons: List of active add-on IDs.
        stripe_customer_id: Stripe customer ID (for Stripe channel).
        stripe_subscription_id: Stripe subscription ID.
        shopify_shop_domain: Shopify store domain (for Shopify channel).
        shopify_subscription_id: Shopify subscription GID.
        customer_email: Customer's email address.

    Returns:
        The created or updated TenantRecord.
    """
    now = int(time.time())

    # Check if tenant already exists for this channel identifier
    existing_tenant_id = None
    if billing_channel == BillingChannel.STRIPE and stripe_customer_id:
        existing_tenant_id = _stripe_index.get(stripe_customer_id)
    elif billing_channel == BillingChannel.SHOPIFY and shopify_shop_domain:
        existing_tenant_id = _shopify_index.get(shopify_shop_domain)

    if existing_tenant_id and existing_tenant_id in _tenants:
        # Update existing tenant (re-subscription or plan change)
        tenant = _tenants[existing_tenant_id]
        tenant.status = TenantStatus.PROVISIONING
        tenant.tier = tier or tenant.tier
        tenant.interval = interval or tenant.interval
        tenant.addons = addons if addons is not None else tenant.addons
        tenant.updated_at = now
        tenant.deactivated_at = None
        tenant.grace_period_ends_at = None

        # Update channel-specific fields
        if stripe_subscription_id:
            tenant.stripe_subscription_id = stripe_subscription_id
        if shopify_subscription_id:
            tenant.shopify_subscription_id = shopify_subscription_id
        if customer_email:
            tenant.customer_email = customer_email

        logger.info(
            "Tenant re-provisioned: tenant=%s channel=%s tier=%s",
            tenant.tenant_id,
            billing_channel.value,
            tier,
        )
        return tenant

    # Create new tenant
    tenant_id = str(uuid.uuid4())
    tenant = TenantRecord(
        tenant_id=tenant_id,
        status=TenantStatus.PROVISIONING,
        billing_channel=billing_channel,
        tier=tier,
        interval=interval,
        addons=addons or [],
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
        shopify_shop_domain=shopify_shop_domain,
        shopify_subscription_id=shopify_subscription_id,
        customer_email=customer_email,
        created_at=now,
        updated_at=now,
    )

    _tenants[tenant_id] = tenant

    # Build indexes
    if stripe_customer_id:
        _stripe_index[stripe_customer_id] = tenant_id
    if shopify_shop_domain:
        _shopify_index[shopify_shop_domain] = tenant_id

    logger.info(
        "Tenant provisioned: tenant=%s channel=%s tier=%s email=%s",
        tenant_id,
        billing_channel.value,
        tier,
        customer_email,
    )

    return tenant


def activate_tenant(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Mark a tenant as active after payment is confirmed.

    Called by:
        - stripe_webhooks.handle_subscription_created
        - shopify_billing.confirm_subscription (after approval)

    Args:
        tenant_id: Direct tenant ID lookup.
        stripe_customer_id: Lookup by Stripe customer ID.
        shopify_shop_domain: Lookup by Shopify shop domain.

    Returns:
        The updated TenantRecord, or None if not found.
    """
    tenant = _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    tenant.status = TenantStatus.ACTIVE
    tenant.updated_at = int(time.time())
    tenant.deactivated_at = None
    tenant.grace_period_ends_at = None

    logger.info("Tenant activated: tenant=%s", tenant.tenant_id)
    return tenant


def update_tenant(
    tier: str | None = None,
    interval: str | None = None,
    addons: list[str] | None = None,
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Update a tenant's plan details (tier change, add-on modification).

    Called by:
        - stripe_webhooks.handle_subscription_updated

    Args:
        tier: New tier name (or None to keep current).
        interval: New interval (or None to keep current).
        addons: New add-on list (or None to keep current).
        tenant_id: Direct tenant ID lookup.
        stripe_customer_id: Lookup by Stripe customer ID.
        shopify_shop_domain: Lookup by Shopify shop domain.

    Returns:
        The updated TenantRecord, or None if not found.
    """
    tenant = _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    old_tier = tenant.tier
    if tier is not None:
        tenant.tier = tier
    if interval is not None:
        tenant.interval = interval
    if addons is not None:
        tenant.addons = addons
    tenant.updated_at = int(time.time())

    logger.info(
        "Tenant updated: tenant=%s tier=%s→%s",
        tenant.tenant_id,
        old_tier,
        tenant.tier,
    )
    return tenant


def deactivate_tenant(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Begin tenant deactivation with grace period.

    Called by:
        - stripe_webhooks.handle_subscription_deleted

    The tenant enters a 30-day grace period (per SLA) during which
    data is preserved but access is restricted. After the grace period,
    the tenant is fully deactivated.

    Args:
        tenant_id: Direct tenant ID lookup.
        stripe_customer_id: Lookup by Stripe customer ID.
        shopify_shop_domain: Lookup by Shopify shop domain.

    Returns:
        The updated TenantRecord, or None if not found.
    """
    tenant = _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    now = int(time.time())
    tenant.status = TenantStatus.GRACE_PERIOD
    tenant.updated_at = now
    tenant.deactivated_at = now
    tenant.grace_period_ends_at = now + _GRACE_PERIOD_SECONDS

    logger.info(
        "Tenant deactivated: tenant=%s grace_period_ends=%d",
        tenant.tenant_id,
        tenant.grace_period_ends_at,
    )
    return tenant


def flag_payment_issue(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Flag a tenant for payment issues (failed invoice).

    Called by:
        - stripe_webhooks.handle_payment_failed

    The tenant status is set to PAST_DUE, which may trigger
    access restrictions depending on the retry count.

    Args:
        tenant_id: Direct tenant ID lookup.
        stripe_customer_id: Lookup by Stripe customer ID.
        shopify_shop_domain: Lookup by Shopify shop domain.

    Returns:
        The updated TenantRecord, or None if not found.
    """
    tenant = _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    tenant.status = TenantStatus.PAST_DUE
    tenant.updated_at = int(time.time())

    logger.info("Tenant flagged past_due: tenant=%s", tenant.tenant_id)
    return tenant


def provision_trial_tenant(
    customer_email: str | None = None,
    trial_duration_days: int = 14,
    conversation_limit: int = 50,
) -> TenantRecord:
    """Provision a free trial tenant (no billing channel required).

    Creates a tenant with TRIAL tier and ACTIVE status that expires
    after trial_duration_days. The conversation_limit is a hard cap —
    no overage billing for trial tenants.

    Called by:
        - Direct signup (website form, API)
        - Shopify app install (before subscription purchase)

    Args:
        customer_email: Contact email for the trial user.
        trial_duration_days: Number of days the trial lasts (default 14).
        conversation_limit: Max conversations during trial (default 50).

    Returns:
        The created TenantRecord.
    """
    now = int(time.time())
    tenant_id = str(uuid.uuid4())

    tenant = TenantRecord(
        tenant_id=tenant_id,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel.TRIAL,
        tier="trial",
        interval=None,
        addons=[],
        customer_email=customer_email,
        created_at=now,
        updated_at=now,
    )

    _tenants[tenant_id] = tenant

    logger.info(
        "Trial tenant provisioned: tenant=%s email=%s duration=%dd limit=%d",
        tenant_id,
        customer_email,
        trial_duration_days,
        conversation_limit,
    )

    return tenant


def get_tenant(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Lookup a tenant by any identifier.

    Args:
        tenant_id: Direct tenant ID.
        stripe_customer_id: Stripe customer ID.
        shopify_shop_domain: Shopify shop domain.

    Returns:
        The TenantRecord, or None if not found.
    """
    return _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _lookup_tenant(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Internal: lookup tenant by any identifier."""
    if tenant_id and tenant_id in _tenants:
        return _tenants[tenant_id]

    if stripe_customer_id:
        tid = _stripe_index.get(stripe_customer_id)
        if tid and tid in _tenants:
            return _tenants[tid]

    if shopify_shop_domain:
        tid = _shopify_index.get(shopify_shop_domain)
        if tid and tid in _tenants:
            return _tenants[tid]

    return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/lookup", response_model=TenantLookupResponse)
async def lookup_tenant_endpoint(
    stripe_customer_id: str | None = None,
    shop: str | None = None,
) -> TenantLookupResponse:
    """Lookup a tenant by Stripe customer ID or Shopify shop domain.

    Query parameters:
        stripe_customer_id: Stripe customer ID (cus_...)
        shop: Shopify store domain (*.myshopify.com)

    At least one parameter is required.

    NOTE: This route is declared before /{tenant_id} to prevent
    FastAPI from matching "lookup" as a tenant_id path parameter.
    """
    if not stripe_customer_id and not shop:
        raise HTTPException(
            status_code=400,
            detail="Provide 'stripe_customer_id' or 'shop' query parameter.",
        )

    tenant = get_tenant(
        stripe_customer_id=stripe_customer_id,
        shopify_shop_domain=shop,
    )

    if not tenant:
        return TenantLookupResponse(found=False)

    return TenantLookupResponse(
        found=True,
        tenant_id=tenant.tenant_id,
        status=tenant.status,
        tier=tenant.tier,
        billing_channel=tenant.billing_channel,
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant_endpoint(tenant_id: str) -> TenantResponse:
    """Get tenant status by tenant ID.

    In production, this endpoint would be authenticated via API key
    or service-to-service auth.
    """
    tenant = get_tenant(tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return TenantResponse(
        tenant_id=tenant.tenant_id,
        status=tenant.status,
        billing_channel=tenant.billing_channel,
        tier=tenant.tier,
        interval=tenant.interval,
        addons=tenant.addons,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )
