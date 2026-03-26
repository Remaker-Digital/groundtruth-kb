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
from dataclasses import dataclass, field
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
_domain_index_repo = None


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

    # Widget key (populated during provisioning, shown once)
    widget_key: str | None = Field(default=None, description="Raw widget key (pk_live_...) — present only in provisioning response")


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
    brand_name: str | None = None


class ValidateKeyRequest(BaseModel):
    """Request body for POST /api/auth/validate-key (SPEC-1644)."""

    tenant: str


class ValidateKeyResponse(BaseModel):
    """Response for successful API key validation (SPEC-1644).

    Only returned when the key is valid for the specified tenant.
    On failure, a 401 is returned with no tenant information.
    """

    valid: bool = True
    tenant_id: str
    status: TenantStatus | None = None
    tier: str | None = None
    billing_channel: BillingChannel | None = None
    has_stripe_billing: bool = False
    shopify_shop_domain: str | None = None
    brand_name: str | None = None
    role: str | None = None
    email: str | None = None
    team_member_id: str | None = None


# ---------------------------------------------------------------------------
# Repository configuration (called at startup from lifecycle.py)
# ---------------------------------------------------------------------------


def configure_provisioning_repo(
    tenant_repo: Any,
    team_repo: Any = None,
    domain_index_repo: Any = None,
) -> None:
    """Wire Cosmos DB repositories as the primary persistence layer.

    Called from lifecycle.py startup to enable all provisioning operations
    and tenant lookup endpoints.

    Args:
        tenant_repo: TenantRepository for tenant CRUD and lookups.
        team_repo: TeamMemberRepository for per-user API key lookups.
        domain_index_repo: DomainIndexRepository for SPEC-1644 index.
    """
    global _tenant_repo, _team_repo, _domain_index_repo  # noqa: PLW0603
    _tenant_repo = tenant_repo
    _team_repo = team_repo
    _domain_index_repo = domain_index_repo
    logger.info("Provisioning repos configured (team_repo=%s, domain_index=%s)",
                "yes" if team_repo else "no", "yes" if domain_index_repo else "no")


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

    # SPEC-1644: Use domain index for O(1) lookups — no cross-partition queries.
    if doc is None and stripe_customer_id and _domain_index_repo:
        try:
            resolved_id = await _domain_index_repo.lookup(stripe_customer_id)
            if resolved_id:
                doc = await _tenant_repo.read(resolved_id, resolved_id)
        except Exception:
            doc = None

    if doc is None and shopify_shop_domain and _domain_index_repo:
        try:
            resolved_id = await _domain_index_repo.lookup(shopify_shop_domain)
            if resolved_id:
                doc = await _tenant_repo.read(resolved_id, resolved_id)
        except Exception:
            doc = None

    if doc is None:
        return None

    return _doc_to_record(doc)


# ---------------------------------------------------------------------------
# DEK provisioning (SPEC-1843 / WI-1628)
# ---------------------------------------------------------------------------


async def _provision_tenant_dek(tenant_id: str) -> None:
    """Create and store a per-tenant DEK for envelope encryption.

    Called during tenant provisioning. Graceful degradation: if encryption
    is not configured or Key Vault is unavailable, logs a warning and
    returns without failing the provisioning flow.
    """
    try:
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        svc = get_envelope_encryption_service()
        if svc is None:
            logger.debug("Encryption service not initialized — skipping DEK provisioning for %s", tenant_id)
            return

        # Generate DEK and wrap it with the Master KEK
        wrapped_dek = await svc.create_tenant_dek(tenant_id)

        # Store wrapped DEK as base64 string in Key Vault
        import base64
        wrapped_b64 = base64.b64encode(wrapped_dek).decode("ascii")

        secret_svc = get_secret_service()
        await secret_svc.store_secret(
            tenant_id,
            TenantSecretType.DEK,
            wrapped_b64,
            tags={"purpose": "envelope-encryption-dek"},
        )

        logger.info("DEK provisioned for tenant %s", tenant_id)

    except Exception:
        logger.warning(
            "Failed to provision DEK for tenant %s — encryption inactive until retry",
            tenant_id,
            exc_info=True,
        )


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
    # SPEC-1644: Use domain index for duplicate detection — no cross-partition queries.
    if billing_channel == BillingChannel.STRIPE and stripe_customer_id and _domain_index_repo:
        try:
            resolved_id = await _domain_index_repo.lookup(stripe_customer_id)
            if resolved_id:
                existing_doc = await _tenant_repo.read(resolved_id, resolved_id)
        except Exception:
            existing_doc = None
    elif billing_channel == BillingChannel.SHOPIFY and shopify_shop_domain and _domain_index_repo:
        try:
            resolved_id = await _domain_index_repo.lookup(shopify_shop_domain)
            if resolved_id:
                existing_doc = await _tenant_repo.read(resolved_id, resolved_id)
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
        # SPEC-1843: customer_email is encrypted — cannot patch directly.
        # Use update_encrypted_fields for it separately.
        encrypted_updates: dict[str, Any] = {}
        if customer_email:
            encrypted_updates["customer_email"] = customer_email

        if encrypted_updates:
            # Patch non-encrypted fields first, then read-modify-write encrypted ones
            if operations:
                await _tenant_repo.patch(existing_id, existing_id, operations)
            updated_doc = await _tenant_repo.update_encrypted_fields(
                existing_id, existing_id, encrypted_updates,
            )
        else:
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

    # SPEC-1644: Write domain index entries for O(1) lookups
    if _domain_index_repo:
        if shopify_shop_domain:
            await _domain_index_repo.upsert(shopify_shop_domain, tenant_id, "shopify")
        if stripe_customer_id:
            await _domain_index_repo.upsert(stripe_customer_id, tenant_id, "stripe")

    # SPEC-1843 / WI-1628: Create per-tenant DEK for envelope encryption
    await _provision_tenant_dek(tenant_id)

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


async def auto_provision_widget_key(tenant_id: str) -> str | None:
    """Generate and persist a widget key for a newly provisioned tenant.

    Writes to both storage locations:
    - TenantDocument.widget_key_hash  (for auth lookup)
    - PreferencesDocument.widget_key  (for admin UI display + activation gate)

    Called after tenant provisioning (both paid and trial). The raw key
    is returned once — callers should include it in the provisioning
    response so the merchant can embed it in their widget script tag.

    Args:
        tenant_id: The new tenant's ID.

    Returns:
        The raw widget key (pk_live_...) or None if provisioning failed.
    """
    if _tenant_repo is None:
        logger.warning("No tenant repo — skipping widget key provisioning for %s", tenant_id)
        return None

    try:
        from src.multi_tenant.auth import generate_widget_key, hash_widget_key
        from src.multi_tenant.repository import PreferencesRepository

        raw_key = generate_widget_key(tenant_id)
        key_hash = hash_widget_key(raw_key)
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Patch TenantDocument with key hash (for auth lookup)
        await _tenant_repo.patch(
            tenant_id,
            tenant_id,
            operations=[
                {"op": "set", "path": "/widget_key_hash", "value": key_hash},
                {"op": "set", "path": "/updated_at", "value": now_iso},
            ],
        )

        # 2. Write raw key to PreferencesDocument (for admin UI + activation gate)
        #
        # The activation service reads widget_key from the active prefs doc
        # when creating drafts (save_draft, start_from_defaults).  If no
        # active prefs doc exists yet (fresh tenant), we create a seed
        # document (version 0) so widget_key is available for the wizard's
        # first draft.  Bug fix: patch() on a non-existent doc was silently
        # failing, leaving widget_key absent and blocking activation (CP.6).
        prefs_repo = PreferencesRepository()
        try:
            existing = await prefs_repo.get_active(tenant_id)
            if existing:
                # Active prefs doc already exists — patch widget_key into it
                await prefs_repo.patch(
                    tenant_id,
                    existing["id"],
                    operations=[
                        {"op": "set", "path": "/widget_key", "value": raw_key},
                        {"op": "set", "path": "/updated_at", "value": now_iso},
                    ],
                )
            else:
                # No active prefs doc yet (fresh tenant) — create seed
                from src.multi_tenant.cosmos_schema import PreferencesDocument

                seed_doc = PreferencesDocument(
                    id=f"{tenant_id}:0",
                    tenant_id=tenant_id,
                    version=0,
                    is_current=True,
                    config_state="active",
                    widget_key=raw_key,
                    created_at=now_iso,
                    activated_at=now_iso,
                )
                await prefs_repo.upsert(tenant_id, seed_doc)
        except Exception:
            logger.warning(
                "Failed to write widget key to preferences doc: tenant=%s",
                tenant_id[:8],
            )

        logger.info(
            "Widget key auto-provisioned: tenant=%s prefix=%s",
            tenant_id[:8],
            raw_key[:16] + "...",
        )
        return raw_key
    except Exception as exc:
        logger.error(
            "Failed to auto-provision widget key for tenant %s: %s",
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


# ---------------------------------------------------------------------------
# SPA Console provisioning (P0-PROV-1)
# ---------------------------------------------------------------------------


@dataclass
class SpaProvisionResult:
    """Result of SPA Console tenant provisioning.

    Partial failures are captured in ``errors`` — the tenant is still
    created even if superadmin key or widget key generation fails.
    The SPA operator can see what failed and retry manually.
    """

    tenant_id: str
    status: str
    tier: str
    superadmin_email: str
    superadmin_api_key: str | None = None
    widget_key: str | None = None
    errors: list[str] = field(default_factory=list)


async def spa_provision_tenant(
    merchant_name: str,
    merchant_url: str | None,
    superadmin_email: str,
    tier: str,
) -> SpaProvisionResult:
    """Provision a new tenant from the SPA Console.

    Orchestrates the full provisioning pipeline:
    1. provision_tenant() — creates TenantDocument (PROVISIONING status)
    2. activate_tenant() — transitions to ACTIVE (no webhook delay)
    3. auto_provision_superadmin() — creates SUPERADMIN team member + API key
    4. auto_provision_widget_key() — generates + dual-writes widget key

    Each step after (1) is individually wrapped so partial failures
    are captured without rolling back the tenant. The SPA operator
    can see which steps failed via the ``errors`` list.

    Optionally sends a welcome email (never raises).

    Args:
        merchant_name: Display name (becomes brand_name in preferences).
        merchant_url: Merchant website or Shopify domain (optional).
        superadmin_email: Tenant owner email (becomes SUPERADMIN member).
        tier: Subscription tier (validated by caller against TenantTier).

    Returns:
        SpaProvisionResult with tenant_id, credentials, and any errors.

    Raises:
        RuntimeError: If tenant repository is not configured or
            provision_tenant() fails (total failure — nothing was created).
    """
    # Step 1: Create tenant (PROVISIONING status)
    record = await provision_tenant(
        billing_channel=BillingChannel.MANUAL,
        tier=tier,
        customer_email=superadmin_email,
    )

    result = SpaProvisionResult(
        tenant_id=record.tenant_id,
        status=record.status.value if hasattr(record.status, "value") else str(record.status),
        tier=tier,
        superadmin_email=superadmin_email,
    )

    # Step 2: Activate immediately (no webhook round-trip for manual channel)
    try:
        activated = await activate_tenant(tenant_id=record.tenant_id)
        if activated:
            result.status = activated.status.value if hasattr(activated.status, "value") else str(activated.status)
        else:
            result.errors.append("Activation returned None — tenant may still be in PROVISIONING state")
    except Exception as exc:
        logger.error("SPA provision — activation failed for %s: %s", record.tenant_id, exc)
        result.errors.append(f"Activation failed: {exc}")

    # Step 3: Create SUPERADMIN team member + API key
    try:
        superadmin_key = await auto_provision_superadmin(record.tenant_id, superadmin_email)
        result.superadmin_api_key = superadmin_key
        if not superadmin_key:
            result.errors.append("Superadmin provisioning returned None — check logs")
    except Exception as exc:
        logger.error("SPA provision — superadmin failed for %s: %s", record.tenant_id, exc)
        result.errors.append(f"Superadmin provisioning failed: {exc}")

    # Step 4: Generate widget key
    try:
        widget_key = await auto_provision_widget_key(record.tenant_id)
        result.widget_key = widget_key
        if not widget_key:
            result.errors.append("Widget key provisioning returned None — check logs")
    except Exception as exc:
        logger.error("SPA provision — widget key failed for %s: %s", record.tenant_id, exc)
        result.errors.append(f"Widget key provisioning failed: {exc}")

    # Step 5: Send welcome email (never raises — defensive by design)
    try:
        from src.multi_tenant.welcome_email import send_welcome_email

        await send_welcome_email(
            to_email=superadmin_email,
            tenant_id=record.tenant_id,
            superadmin_key=result.superadmin_api_key,
            widget_key=result.widget_key,
            tier=tier,
        )
    except Exception as exc:
        # Welcome email is best-effort — log but surface to operator (never fail silently)
        logger.warning("SPA provision — welcome email failed for %s: %s", record.tenant_id, exc)
        result.errors.append(f"Welcome email failed: {exc}")

    logger.info(
        "SPA tenant provisioned: tenant=%s tier=%s email=%s errors=%d",
        record.tenant_id[:8],
        tier,
        superadmin_email,
        len(result.errors),
    )

    return result


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

    # Auto-provision widget key (failures logged, don't block trial creation)
    widget_key = await auto_provision_widget_key(tenant_id)

    # Send welcome email (failures logged, don't block trial creation)
    if customer_email:
        from src.multi_tenant.welcome_email import send_welcome_email

        await send_welcome_email(
            to_email=customer_email,
            tenant_id=tenant_id,
            widget_key=widget_key,
            tier="trial",
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
        widget_key=widget_key,
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
# Partition-scoped API key validation (SPEC-1644)
# ---------------------------------------------------------------------------


async def _validate_api_key_for_tenant(
    tenant_id: str, api_key: str,
) -> dict[str, Any] | None:
    """Validate an API key against a known tenant (partition-scoped).

    SPEC-1644: API keys MUST NOT identify tenants.  The caller must already
    know the tenant_id (from the URL).  This method reads the tenant or
    team-member document within that single partition and compares the hash.
    No cross-partition query is ever performed.

    Returns a dict with tenant info + optional team member info, or None.
    """
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    # Per-user API key → partition-scoped team member lookup
    if api_key.startswith("ar_user_") and _team_repo is not None:
        try:
            member = await _team_repo.verify_user_key_hash(tenant_id, key_hash)
            if member and _tenant_repo is not None:
                tenant_doc = await _tenant_repo.read(tenant_id, tenant_id)
                if tenant_doc:
                    return {**tenant_doc, "_team_member": member}
        except Exception as exc:
            logger.warning("User API key validation failed for tenant=%s: %s", tenant_id, exc)
        return None

    # Tenant API key → partition-scoped verification
    if _tenant_repo is None:
        return None
    try:
        return await _tenant_repo.verify_key_hash(tenant_id, key_hash)
    except Exception as exc:
        logger.warning("API key validation failed for tenant=%s: %s", tenant_id, exc)
    return None


async def _read_brand_name(tenant_id: str) -> str | None:
    """Read brand_name from the tenant's active config (lightweight single-field read).

    Used to enrich the tenant lookup response so the admin navbar can display
    the brand name without a separate config fetch.
    """
    try:
        from src.multi_tenant.config.config_processor import get_config_processor
        processor = get_config_processor()
        result = await processor.get_config(tenant_id)
        return result.config.get("brand_name") if result and result.config else None
    except Exception as exc:
        logger.debug("brand_name read failed for %s: %s", tenant_id, exc)
        return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/lookup",
    response_model=TenantLookupResponse,
    status_code=200,
    summary="Lookup tenant by channel identifier",
    description="Looks up a tenant by Stripe customer ID or Shopify shop domain. Returns the tenant's status, tier, and billing channel.",
    responses={
        400: {"description": "No lookup parameter provided"},
    },
)
async def lookup_tenant_endpoint(
    request: Request,
    stripe_customer_id: str | None = None,
    shop: str | None = None,
) -> TenantLookupResponse:
    """Lookup a tenant by Stripe customer ID or Shopify shop domain.

    Query parameters:
        stripe_customer_id: Stripe customer ID (cus_...)
        shop: Shopify store domain (*.myshopify.com)

    At least one lookup parameter is required.

    SPEC-1644: API keys MUST NOT be used to identify tenants.
    Use POST /api/auth/validate-key for API key authentication.

    NOTE: This route is declared before /{tenant_id} to prevent
    FastAPI from matching "lookup" as a tenant_id path parameter.
    """
    if not stripe_customer_id and not shop:
        raise HTTPException(
            status_code=400,
            detail="Provide 'stripe_customer_id' or 'shop' query parameter. API key tenant discovery is not supported (SPEC-1644). Use POST /api/auth/validate-key instead.",
        )

    # Direct channel lookup — repo is the primary path
    tenant = await get_tenant(
        stripe_customer_id=stripe_customer_id,
        shopify_shop_domain=shop,
    )

    if not tenant:
        return TenantLookupResponse(found=False)

    # Enrich with brand_name from active config
    brand_name = await _read_brand_name(tenant.tenant_id)

    return TenantLookupResponse(
        found=True,
        tenant_id=tenant.tenant_id,
        status=tenant.status,
        tier=tenant.tier,
        billing_channel=tenant.billing_channel,
        has_stripe_billing=bool(tenant.stripe_customer_id),
        shopify_shop_domain=tenant.shopify_shop_domain,
        brand_name=brand_name,
    )


@router.post(
    "/auth/validate-key",
    response_model=ValidateKeyResponse,
    status_code=200,
    summary="Validate API key against a known tenant (SPEC-1644)",
    description=(
        "Validates an API key against a specific tenant identified in the "
        "request body.  The tenant MUST be known in advance (from the URL).  "
        "API keys MUST NOT be used to discover which tenant they belong to.  "
        "Returns user info on success, 401 on failure with no tenant info."
    ),
    responses={
        400: {"description": "Missing tenant or API key"},
        401: {"description": "Invalid API key for this tenant"},
    },
)
async def validate_key_endpoint(
    request: Request,
    body: ValidateKeyRequest,
) -> ValidateKeyResponse:
    """Validate an API key against a specified tenant (SPEC-1644).

    The caller must already know the tenant (from the URL ?tenant= param).
    This endpoint performs a partition-scoped lookup — no cross-partition
    query is ever executed.  On failure, the response reveals nothing
    about which tenant the key actually belongs to.
    """
    api_key = request.headers.get("X-API-Key", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="X-API-Key header is required.")

    doc = await _validate_api_key_for_tenant(body.tenant, api_key)
    if not doc:
        # SPEC-1644: reveal nothing about the key's actual tenant
        raise HTTPException(status_code=401, detail="Invalid API key.")

    tenant_id = doc.get("tenant_id") or doc.get("id")
    brand_name = await _read_brand_name(tenant_id) if tenant_id else None

    # Extract team member info if present (per-user key)
    member = doc.get("_team_member")
    role = None
    email = None
    team_member_id = None
    if member:
        role = member.get("role")
        email = member.get("email")
        team_member_id = member.get("id")
    else:
        # Legacy tenant API key — implicit admin role
        role = "admin"

    return ValidateKeyResponse(
        tenant_id=tenant_id,
        status=doc.get("status"),
        tier=doc.get("tier"),
        billing_channel=doc.get("billing_channel"),
        has_stripe_billing=bool(doc.get("stripe_customer_id")),
        shopify_shop_domain=doc.get("shopify_shop_domain"),
        brand_name=brand_name,
        role=role,
        email=email,
        team_member_id=team_member_id,
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
