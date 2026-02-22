"""
Tenant provisioning service.

Channel-agnostic interface for managing tenant lifecycle. Both Stripe
(direct billing) and Shopify (App Store billing) feed into this service
to create, update, and deactivate tenants.

This abstraction ensures downstream code (usage tracking, feature gating,
API key management) doesn't need to know which billing channel the
customer uses.

Persistence: Cosmos DB ``tenants`` collection via TenantRepository.
All core functions are async — callers must ``await`` them.

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

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

# Canonical enums from Cosmos DB schema — re-exported for backward compatibility.
# Callers may continue to ``from src.integrations.provisioning import BillingChannel``.
from src.multi_tenant.cosmos_schema import (  # noqa: F401  — re-export
    BillingChannel,
    TenantStatus,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cosmos DB repositories (wired at startup via configure_provisioning_repo)
# ---------------------------------------------------------------------------

_tenant_repo = None
_team_repo = None


# ---------------------------------------------------------------------------
# Tenant record — returned by all core functions
# ---------------------------------------------------------------------------


class TenantRecord(BaseModel):
    """A tenant's complete billing and provisioning state.

    This record is the single source of truth for a tenant's status,
    regardless of billing channel. All downstream systems (usage
    tracking, feature flags, API gateway) read from this record.

    Timestamps are ISO 8601 strings (matching TenantDocument schema).
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

    # Timestamps (ISO 8601 strings)
    created_at: str = Field(description="When tenant was provisioned")
    updated_at: str = Field(description="Last status change")
    deactivated_at: str | None = Field(default=None, description="When cancellation began")
    grace_period_ends_at: str | None = Field(default=None, description="When data will be deleted")


# Grace period duration (30 days, per SLA)
_GRACE_PERIOD = timedelta(days=30)

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
    created_at: str | int | None = None
    updated_at: str | int | None = None


class TenantLookupResponse(BaseModel):
    """Response for tenant lookup by channel identifier."""

    found: bool
    tenant_id: str | None = None
    status: TenantStatus | None = None
    tier: str | None = None
    billing_channel: BillingChannel | None = None
    has_stripe_billing: bool = False
    shopify_shop_domain: str | None = None


# ---------------------------------------------------------------------------
# Repository configuration (called at startup from lifecycle.py)
# ---------------------------------------------------------------------------


def configure_provisioning_repo(tenant_repo: Any, team_repo: Any = None) -> None:
    """Wire Cosmos DB repositories as the primary persistence layer.

    Called from lifecycle.py startup to enable all provisioning operations
    and tenant lookup endpoints.

    Args:
        tenant_repo: TenantRepository for tenant CRUD and lookups.
        team_repo: TeamMemberRepository for per-user API key lookups.
    """
    global _tenant_repo, _team_repo  # noqa: PLW0603
    _tenant_repo = tenant_repo
    _team_repo = team_repo
    logger.info("Provisioning repos configured (team_repo=%s)", "yes" if team_repo else "no")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _doc_to_record(doc: dict[str, Any]) -> TenantRecord:
    """Convert a Cosmos DB tenant document dict to a TenantRecord."""
    tier_val = doc.get("tier")
    # TenantDocument.tier is TenantTier enum — extract string value
    if hasattr(tier_val, "value"):
        tier_val = tier_val.value
    status_val = doc.get("status", "provisioning")
    if hasattr(status_val, "value"):
        status_val = status_val.value
    channel_val = doc.get("billing_channel", "stripe")
    if hasattr(channel_val, "value"):
        channel_val = channel_val.value

    return TenantRecord(
        tenant_id=doc.get("tenant_id") or doc.get("id"),
        status=status_val,
        billing_channel=channel_val,
        tier=tier_val,
        interval=doc.get("interval"),
        addons=doc.get("addons", []),
        stripe_customer_id=doc.get("stripe_customer_id"),
        stripe_subscription_id=doc.get("stripe_subscription_id"),
        shopify_shop_domain=doc.get("shopify_shop_domain"),
        shopify_subscription_id=doc.get("shopify_subscription_id"),
        customer_email=doc.get("customer_email"),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        deactivated_at=doc.get("deactivated_at"),
        grace_period_ends_at=doc.get("grace_period_ends_at"),
    )


async def _lookup_tenant(
    tenant_id: str | None = None,
    stripe_customer_id: str | None = None,
    shopify_shop_domain: str | None = None,
) -> TenantRecord | None:
    """Internal: lookup tenant by any identifier via Cosmos DB."""
    if _tenant_repo is None:
        logger.warning("Tenant repo not configured — cannot look up tenant")
        return None

    doc: dict[str, Any] | None = None

    if tenant_id:
        try:
            doc = await _tenant_repo.read(tenant_id, tenant_id)
        except Exception:
            doc = None

    if doc is None and stripe_customer_id:
        try:
            doc = await _tenant_repo.find_by_stripe_customer_id(stripe_customer_id)
        except Exception:
            doc = None

    if doc is None and shopify_shop_domain:
        try:
            doc = await _tenant_repo.find_by_shopify_domain(shopify_shop_domain)
        except Exception:
            doc = None

    if doc is None:
        return None

    return _doc_to_record(doc)


# ---------------------------------------------------------------------------
# Core provisioning logic (all async — callers must await)
# ---------------------------------------------------------------------------


async def provision_tenant(
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

    Raises:
        RuntimeError: If the tenant repository is not configured.
    """
    if _tenant_repo is None:
        raise RuntimeError("Tenant repository not configured")

    now_iso = datetime.now(timezone.utc).isoformat()

    # Check if tenant already exists for this channel identifier
    existing_doc: dict[str, Any] | None = None
    if billing_channel == BillingChannel.STRIPE and stripe_customer_id:
        try:
            existing_doc = await _tenant_repo.find_by_stripe_customer_id(stripe_customer_id)
        except Exception:
            existing_doc = None
    elif billing_channel == BillingChannel.SHOPIFY and shopify_shop_domain:
        try:
            existing_doc = await _tenant_repo.find_by_shopify_domain(shopify_shop_domain)
        except Exception:
            existing_doc = None

    if existing_doc:
        # Re-provision existing tenant (re-subscription or plan change)
        existing_id = existing_doc.get("tenant_id") or existing_doc.get("id")
        operations: list[dict[str, Any]] = [
            {"op": "set", "path": "/status", "value": TenantStatus.PROVISIONING.value},
            {"op": "set", "path": "/updated_at", "value": now_iso},
            {"op": "set", "path": "/deactivated_at", "value": None},
            {"op": "set", "path": "/grace_period_ends_at", "value": None},
        ]
        if tier is not None:
            operations.append({"op": "set", "path": "/tier", "value": tier})
        if interval is not None:
            operations.append({"op": "set", "path": "/interval", "value": interval})
        if addons is not None:
            operations.append({"op": "set", "path": "/addons", "value": addons})
        if stripe_subscription_id:
            operations.append({"op": "set", "path": "/stripe_subscription_id", "value": stripe_subscription_id})
        if shopify_subscription_id:
            operations.append({"op": "set", "path": "/shopify_subscription_id", "value": shopify_subscription_id})
        if customer_email:
            operations.append({"op": "set", "path": "/customer_email", "value": customer_email})

        updated_doc = await _tenant_repo.patch(existing_id, existing_id, operations)

        logger.info(
            "Tenant re-provisioned: tenant=%s channel=%s tier=%s",
            existing_id,
            billing_channel.value,
            tier,
        )
        return _doc_to_record(updated_doc)

    # Create new tenant
    tenant_id = str(uuid.uuid4())

    from src.multi_tenant.cosmos_schema import TenantDocument

    doc = TenantDocument(
        id=tenant_id,
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
        created_at=now_iso,
        updated_at=now_iso,
    )

    await _tenant_repo.upsert(tenant_id, doc)

    logger.info(
        "Tenant provisioned: tenant=%s channel=%s tier=%s email=%s",
        tenant_id,
        billing_channel.value,
        tier,
        customer_email,
    )

    return TenantRecord(
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
        created_at=now_iso,
        updated_at=now_iso,
    )


async def auto_provision_superadmin(
    tenant_id: str,
    customer_email: str,
) -> str | None:
    """Create a superadmin team member for a newly provisioned tenant.

    Called after tenant provisioning to ensure the tenant owner has
    a per-user API key with superadmin privileges.

    Args:
        tenant_id: The new tenant's ID.
        customer_email: The tenant owner's email address.

    Returns:
        The raw API key (shown once) or None if provisioning failed.
    """
    if not customer_email:
        logger.warning("No customer email — skipping superadmin provisioning for %s", tenant_id)
        return None

    try:
        from src.multi_tenant.auth import generate_user_api_key, hash_api_key
        from src.multi_tenant.cosmos_schema import TeamMemberDocument, TeamMemberRole
        from src.multi_tenant.repository import TeamMemberRepository

        repo = TeamMemberRepository()
        member_id = f"{tenant_id}:{customer_email}"
        raw_key = generate_user_api_key(tenant_id)
        key_hash = hash_api_key(raw_key)
        key_prefix = raw_key[:12] + "..."

        now_iso = datetime.now(timezone.utc).isoformat()

        doc = TeamMemberDocument(
            id=member_id,
            tenant_id=tenant_id,
            email=customer_email,
            display_name="Owner",
            role=TeamMemberRole.SUPERADMIN,
            is_active=True,
            escalation_categories=[],
            max_concurrent_conversations=0,
            user_api_key_hash=key_hash,
            user_api_key_prefix=key_prefix,
            created_at=now_iso,
            updated_at=now_iso,
            invited_by="system",
        )

        await repo.create(tenant_id, doc)
        logger.info(
            "Superadmin auto-provisioned: tenant=%s email=%s prefix=%s",
            tenant_id[:8],
            customer_email,
            key_prefix,
        )
        return raw_key
    except Exception as exc:
        logger.error(
            "Failed to auto-provision superadmin for tenant %s: %s",
            tenant_id,
            exc,
        )
        return None


async def activate_tenant(
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
    tenant = await _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    operations = [
        {"op": "set", "path": "/status", "value": TenantStatus.ACTIVE.value},
        {"op": "set", "path": "/updated_at", "value": now_iso},
        {"op": "set", "path": "/deactivated_at", "value": None},
        {"op": "set", "path": "/grace_period_ends_at", "value": None},
    ]

    updated_doc = await _tenant_repo.patch(tenant.tenant_id, tenant.tenant_id, operations)

    logger.info("Tenant activated: tenant=%s", tenant.tenant_id)
    return _doc_to_record(updated_doc)


async def update_tenant(
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
    tenant = await _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/updated_at", "value": now_iso},
    ]
    if tier is not None:
        operations.append({"op": "set", "path": "/tier", "value": tier})
    if interval is not None:
        operations.append({"op": "set", "path": "/interval", "value": interval})
    if addons is not None:
        operations.append({"op": "set", "path": "/addons", "value": addons})

    old_tier = tenant.tier
    updated_doc = await _tenant_repo.patch(tenant.tenant_id, tenant.tenant_id, operations)

    logger.info(
        "Tenant updated: tenant=%s tier=%s→%s",
        tenant.tenant_id,
        old_tier,
        tier if tier is not None else old_tier,
    )
    return _doc_to_record(updated_doc)


async def deactivate_tenant(
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
    tenant = await _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    grace_end_iso = (now + _GRACE_PERIOD).isoformat()

    operations = [
        {"op": "set", "path": "/status", "value": TenantStatus.GRACE_PERIOD.value},
        {"op": "set", "path": "/updated_at", "value": now_iso},
        {"op": "set", "path": "/deactivated_at", "value": now_iso},
        {"op": "set", "path": "/grace_period_ends_at", "value": grace_end_iso},
    ]

    updated_doc = await _tenant_repo.patch(tenant.tenant_id, tenant.tenant_id, operations)

    logger.info(
        "Tenant deactivated: tenant=%s grace_period_ends=%s",
        tenant.tenant_id,
        grace_end_iso,
    )
    return _doc_to_record(updated_doc)


async def flag_payment_issue(
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
    tenant = await _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)
    if not tenant:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    operations = [
        {"op": "set", "path": "/status", "value": TenantStatus.PAST_DUE.value},
        {"op": "set", "path": "/updated_at", "value": now_iso},
    ]

    updated_doc = await _tenant_repo.patch(tenant.tenant_id, tenant.tenant_id, operations)

    logger.info("Tenant flagged past_due: tenant=%s", tenant.tenant_id)
    return _doc_to_record(updated_doc)


async def provision_trial_tenant(
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

    Raises:
        RuntimeError: If the tenant repository is not configured.
    """
    if _tenant_repo is None:
        raise RuntimeError("Tenant repository not configured")

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    trial_end_iso = (now + timedelta(days=trial_duration_days)).isoformat()
    tenant_id = str(uuid.uuid4())

    from src.multi_tenant.cosmos_schema import TenantDocument

    doc = TenantDocument(
        id=tenant_id,
        tenant_id=tenant_id,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel.TRIAL,
        tier="trial",
        interval=None,
        addons=[],
        customer_email=customer_email,
        trial_expires_at=trial_end_iso,
        trial_conversation_limit=conversation_limit,
        created_at=now_iso,
        updated_at=now_iso,
    )

    await _tenant_repo.upsert(tenant_id, doc)

    logger.info(
        "Trial tenant provisioned: tenant=%s email=%s duration=%dd limit=%d",
        tenant_id,
        customer_email,
        trial_duration_days,
        conversation_limit,
    )

    return TenantRecord(
        tenant_id=tenant_id,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel.TRIAL,
        tier="trial",
        interval=None,
        addons=[],
        customer_email=customer_email,
        created_at=now_iso,
        updated_at=now_iso,
    )


async def get_tenant(
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
    return await _lookup_tenant(tenant_id, stripe_customer_id, shopify_shop_domain)


# ---------------------------------------------------------------------------
# API key lookup (used by /api/tenants/lookup endpoint)
# ---------------------------------------------------------------------------


async def _lookup_by_api_key(api_key: str) -> dict[str, Any] | None:
    """Lookup a tenant in Cosmos DB by API key hash.

    Used by the standalone admin login flow — the raw key is hashed
    with SHA-256 and matched against the stored hash.

    Supports both key types:
    - Tenant API keys (ar_*): matched against tenant.api_key_hash
    - Per-user API keys (ar_user_*): matched against team_member.user_api_key_hash,
      then resolved to the parent tenant document
    """
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    # Per-user API key → resolve via team member → tenant
    if api_key.startswith("ar_user_") and _team_repo is not None:
        try:
            member = await _team_repo.find_by_user_api_key_hash(key_hash)
            if member and _tenant_repo is not None:
                tid = member.get("tenant_id")
                if tid:
                    return await _tenant_repo.read(tid, tid)
        except Exception as exc:
            logger.warning("User API key lookup failed: %s", exc)
        return None

    # Tenant API key → direct lookup
    if _tenant_repo is None:
        return None
    try:
        return await _tenant_repo.find_by_api_key_hash(key_hash)
    except Exception as exc:
        logger.warning("API key lookup failed: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/lookup",
    response_model=TenantLookupResponse,
    status_code=200,
    summary="Lookup tenant by channel identifier",
    description="Looks up a tenant by Stripe customer ID, Shopify shop domain, or API key header. Returns the tenant's status, tier, and billing channel.",
    responses={
        400: {"description": "No lookup parameter or API key provided"},
        401: {"description": "Invalid API key"},
    },
)
async def lookup_tenant_endpoint(
    request: Request,
    stripe_customer_id: str | None = None,
    shop: str | None = None,
) -> TenantLookupResponse:
    """Lookup a tenant by Stripe customer ID, Shopify shop domain, or API key.

    Query parameters:
        stripe_customer_id: Stripe customer ID (cus_...)
        shop: Shopify store domain (*.myshopify.com)

    Headers:
        X-API-Key: API key for standalone admin authentication

    At least one lookup method is required.

    NOTE: This route is declared before /{tenant_id} to prevent
    FastAPI from matching "lookup" as a tenant_id path parameter.
    """
    # --- API key lookup (standalone admin login) ---
    # Only attempt API key auth when no query parameters are provided.
    # When shop or stripe_customer_id is given, those take precedence.
    api_key = request.headers.get("X-API-Key", "").strip()
    if api_key and not stripe_customer_id and not shop:
        doc = await _lookup_by_api_key(api_key)
        if doc:
            return TenantLookupResponse(
                found=True,
                tenant_id=doc.get("tenant_id") or doc.get("id"),
                status=doc.get("status"),
                tier=doc.get("tier"),
                billing_channel=doc.get("billing_channel"),
                has_stripe_billing=bool(doc.get("stripe_customer_id")),
                shopify_shop_domain=doc.get("shopify_shop_domain"),
            )
        raise HTTPException(status_code=401, detail="Invalid API key.")

    if not stripe_customer_id and not shop:
        raise HTTPException(
            status_code=400,
            detail="Provide 'stripe_customer_id' or 'shop' query parameter, or X-API-Key header.",
        )

    # Direct channel lookup — repo is the primary path
    tenant = await get_tenant(
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
        has_stripe_billing=bool(tenant.stripe_customer_id),
        shopify_shop_domain=tenant.shopify_shop_domain,
    )


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=200,
    summary="Get tenant status by ID",
    description="Returns the full tenant status record including lifecycle status, billing channel, tier, interval, and add-ons.",
    responses={
        404: {"description": "Tenant not found"},
    },
)
async def get_tenant_endpoint(tenant_id: str) -> TenantResponse:
    """Get tenant status by tenant ID."""
    tenant = await get_tenant(tenant_id=tenant_id)
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
