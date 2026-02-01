"""
Trial tenant management service.

Implements WI #120-128 from the work items backlog — comprehensive trial
environment including provisioning, expiry, conversation cap enforcement,
trial→paid conversion, demo data seeding, trial dashboard, expired cleanup,
and metrics isolation.

Trial lifecycle:
    1. provision_trial()       — Creates trial tenant (14 days, 50 conversations)
    2. check_trial_status()    — Returns days remaining, conversations used
    3. enforce_trial_cap()     — Returns whether conversation is allowed
    4. scan_expired_trials()   — Transitions expired trials to TRIAL_EXPIRED
    5. convert_trial_to_paid() — Upgrades trial to paid tier, preserves data
    6. cleanup_expired_trials() — Deletes data for expired trials after grace period

Architecture references:
    - WI #119: TenantTier.TRIAL enum and TIER_DEFAULTS (already implemented)
    - WI #120: Trial provisioning flow
    - WI #121: Trial expiry mechanism
    - WI #122: Trial conversation cap
    - WI #123: Trial model routing
    - WI #124: Trial → paid conversion
    - WI #125: Demo data seeder
    - WI #126: Trial-specific dashboard view
    - WI #127: Expired trial data cleanup
    - WI #128: Trial metrics isolation

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    AuditEventType,
    BillingChannel,
    ConsentStatus,
    TenantStatus,
    TenantTier,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default trial parameters
DEFAULT_TRIAL_DURATION_DAYS = 14
DEFAULT_TRIAL_CONVERSATION_LIMIT = 50

# Trial model routing (WI #123): cost containment
TRIAL_MODEL = "gpt-4o-mini"

# Grace period after trial expires before data deletion (WI #127)
TRIAL_EXPIRED_GRACE_DAYS = 30

# Demo data conversation count (WI #125)
DEMO_CONVERSATION_COUNT = 5


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


class TrialStatusCode(str, Enum):
    """Status of a trial tenant."""

    ACTIVE = "active"               # Trial in progress
    EXPIRING_SOON = "expiring_soon" # < 3 days remaining
    EXPIRED = "expired"             # Trial period ended
    CONVERTED = "converted"         # Upgraded to paid tier
    CAP_REACHED = "cap_reached"     # Conversation limit hit


@dataclass(frozen=True)
class TrialStatus:
    """Detailed trial status for dashboard display (WI #126)."""

    tenant_id: str
    status: TrialStatusCode
    trial_started_at: str          # ISO 8601
    trial_expires_at: str          # ISO 8601
    days_remaining: int
    hours_remaining: int
    conversation_limit: int
    conversations_used: int
    conversations_remaining: int
    usage_percent: float
    model: str                     # AI model used for trial
    tier_after_expiry: str | None  # Recommended upgrade tier
    can_send_message: bool         # Whether new conversations are allowed


@dataclass(frozen=True)
class TrialConversionResult:
    """Result of trial → paid conversion (WI #124)."""

    tenant_id: str
    previous_tier: str
    new_tier: str
    billing_channel: str
    data_preserved: bool
    conversations_carried_over: int
    converted_at: str              # ISO 8601


@dataclass
class DemoDataResult:
    """Result of demo data seeding (WI #125)."""

    tenant_id: str
    conversations_seeded: int
    profiles_seeded: int
    knowledge_articles_seeded: int


@dataclass(frozen=True)
class TrialScanResult:
    """Result of trial expiry scan (WI #121)."""

    scanned_count: int
    expired_count: int
    expiring_soon_count: int
    expired_tenant_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TrialCleanupResult:
    """Result of expired trial data cleanup (WI #127)."""

    tenants_cleaned: int
    tenant_ids: list[str] = field(default_factory=list)
    data_deleted: bool = True


# ---------------------------------------------------------------------------
# TrialManagementService
# ---------------------------------------------------------------------------


class TrialManagementService:
    """Comprehensive trial tenant management.

    This service manages the complete trial lifecycle: provisioning,
    status tracking, conversation cap enforcement, expiry scanning,
    paid conversion, and data cleanup.

    Dependencies:
        - tenant_repo: TenantRepository for tenant CRUD
        - usage_repo: UsageRepository for conversation counts
        - conversation_repo: ConversationRepository for conversation data
        - profile_repo: CustomerProfileRepository for customer profiles
        - knowledge_repo: KnowledgeBaseRepository for KB articles
        - audit_repo: AuditLogRepository for audit trail
    """

    def __init__(
        self,
        tenant_repo: Any,
        usage_repo: Any,
        conversation_repo: Any | None = None,
        profile_repo: Any | None = None,
        knowledge_repo: Any | None = None,
        audit_repo: Any | None = None,
    ) -> None:
        self._tenants = tenant_repo
        self._usage = usage_repo
        self._conversations = conversation_repo
        self._profiles = profile_repo
        self._knowledge = knowledge_repo
        self._audit = audit_repo

    # -------------------------------------------------------------------
    # WI #120: Trial provisioning flow
    # -------------------------------------------------------------------

    async def provision_trial(
        self,
        customer_email: str | None = None,
        shopify_shop_domain: str | None = None,
        trial_duration_days: int = DEFAULT_TRIAL_DURATION_DAYS,
        conversation_limit: int = DEFAULT_TRIAL_CONVERSATION_LIMIT,
        seed_demo_data: bool = True,
    ) -> dict[str, Any]:
        """Provision a new trial tenant.

        Creates a tenant with TRIAL tier, ACTIVE status, and hard-coded
        expiry and conversation limits. No billing channel required.

        Args:
            customer_email: Contact email for the trial user.
            shopify_shop_domain: Shopify store domain (if from app install).
            trial_duration_days: Trial period length in days.
            conversation_limit: Hard cap on conversations during trial.
            seed_demo_data: Whether to populate demo conversations/profiles.

        Returns:
            The created tenant document dict.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=trial_duration_days)
        tenant_id = str(uuid.uuid4())

        # Build tenant document
        tenant_doc = {
            "id": tenant_id,
            "tenant_id": tenant_id,
            "status": TenantStatus.ACTIVE.value,
            "billing_channel": BillingChannel.TRIAL.value,
            "tier": TenantTier.TRIAL.value,
            "interval": None,
            "addons": [],
            "customer_email": customer_email,
            "shopify_shop_domain": shopify_shop_domain,
            "consent_status": ConsentStatus.NOT_ASKED.value,
            "trial_expires_at": expires_at.isoformat(),
            "trial_conversation_limit": conversation_limit,
            "rate_limit_rpm": TIER_DEFAULTS[TenantTier.TRIAL.value]["rate_limit_rpm"],
            "max_concurrent": TIER_DEFAULTS[TenantTier.TRIAL.value]["max_concurrent"],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # Persist tenant
        await self._tenants.create(tenant_doc)

        # Audit trail
        if self._audit:
            await self._audit.log_event(
                tenant_id=tenant_id,
                event_type=AuditEventType.TENANT_PROVISIONED,
                actor="system",
                details={
                    "tier": "trial",
                    "trial_duration_days": trial_duration_days,
                    "conversation_limit": conversation_limit,
                    "email": customer_email,
                },
            )

        # Seed demo data for better first impression
        if seed_demo_data and self._conversations:
            await self.seed_demo_data(tenant_id)

        logger.info(
            "Trial provisioned: tenant=%s email=%s expires=%s limit=%d",
            tenant_id,
            customer_email,
            expires_at.isoformat(),
            conversation_limit,
        )

        return tenant_doc

    # -------------------------------------------------------------------
    # WI #121: Trial expiry mechanism
    # -------------------------------------------------------------------

    async def scan_expired_trials(self) -> TrialScanResult:
        """Scan for expired trial tenants and transition their status.

        This method should be called periodically (e.g., every hour via
        scheduled task or KEDA cron scaler). It:
        1. Queries all ACTIVE trial-tier tenants
        2. Checks trial_expires_at against current time
        3. Transitions expired trials to TRIAL_EXPIRED status

        Returns:
            TrialScanResult with counts of scanned/expired/expiring-soon.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        soon = now + timedelta(days=3)

        # Query active trial tenants
        trial_tenants = await self._tenants.query(
            query="SELECT * FROM c WHERE c.tier = @tier AND c.status = @status",
            parameters=[
                {"name": "@tier", "value": TenantTier.TRIAL.value},
                {"name": "@status", "value": TenantStatus.ACTIVE.value},
            ],
        )

        scanned = 0
        expired_ids: list[str] = []
        expiring_soon = 0

        for tenant in trial_tenants:
            scanned += 1
            expires_at_str = tenant.get("trial_expires_at")
            if not expires_at_str:
                continue

            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid trial_expires_at for tenant=%s: %s",
                    tenant.get("tenant_id"), expires_at_str,
                )
                continue

            tenant_id = tenant["tenant_id"]

            if expires_at <= now:
                # Trial has expired — transition to TRIAL_EXPIRED
                await self._tenants.patch(
                    tenant_id,
                    tenant_id,
                    operations=[
                        {"op": "set", "path": "/status", "value": TenantStatus.TRIAL_EXPIRED.value},
                        {"op": "set", "path": "/updated_at", "value": now_iso},
                    ],
                )

                if self._audit:
                    await self._audit.log_event(
                        tenant_id=tenant_id,
                        event_type=AuditEventType.TENANT_DEACTIVATED,
                        actor="system",
                        details={"reason": "trial_expired", "expired_at": expires_at_str},
                    )

                expired_ids.append(tenant_id)
                logger.info("Trial expired: tenant=%s expired_at=%s", tenant_id, expires_at_str)

            elif expires_at <= soon:
                expiring_soon += 1

        return TrialScanResult(
            scanned_count=scanned,
            expired_count=len(expired_ids),
            expiring_soon_count=expiring_soon,
            expired_tenant_ids=expired_ids,
        )

    # -------------------------------------------------------------------
    # WI #122: Trial conversation cap enforcement
    # -------------------------------------------------------------------

    async def enforce_trial_cap(
        self,
        tenant_id: str,
    ) -> tuple[bool, TrialStatus | None]:
        """Check if a trial tenant can start a new conversation.

        Called before conversation creation to enforce the hard cap.
        Trial tenants cannot exceed their conversation_limit — there is
        no overage billing.

        Args:
            tenant_id: The trial tenant to check.

        Returns:
            Tuple of (allowed: bool, status: TrialStatus or None).
            If not allowed, status explains why.
        """
        tenant = await self._tenants.read(tenant_id, tenant_id)
        if not tenant:
            return False, None

        tier = tenant.get("tier")
        if tier != TenantTier.TRIAL.value:
            # Not a trial tenant — no cap enforcement needed
            return True, None

        status = await self.get_trial_status(tenant_id)
        if not status:
            return False, None

        # Check expiry
        if status.status == TrialStatusCode.EXPIRED:
            return False, status

        # Check conversation cap
        if status.conversations_remaining <= 0:
            return False, status

        return status.can_send_message, status

    # -------------------------------------------------------------------
    # WI #123: Trial model routing
    # -------------------------------------------------------------------

    @staticmethod
    def get_trial_model(tier: str | TenantTier) -> str | None:
        """Get the model to use for trial tenants.

        Trial tenants use GPT-4o-mini for all agents as a cost
        containment measure. Returns None for non-trial tenants
        (use default model selection).

        Args:
            tier: The tenant's tier.

        Returns:
            Model identifier string for trial, None for paid tiers.
        """
        tier_value = tier.value if isinstance(tier, TenantTier) else tier
        if tier_value == TenantTier.TRIAL.value:
            return TRIAL_MODEL
        return None

    # -------------------------------------------------------------------
    # WI #124: Trial → paid conversion
    # -------------------------------------------------------------------

    async def convert_trial_to_paid(
        self,
        tenant_id: str,
        new_tier: str | TenantTier,
        billing_channel: str | BillingChannel,
        interval: str = "month",
        stripe_customer_id: str | None = None,
        stripe_subscription_id: str | None = None,
        shopify_subscription_id: str | None = None,
    ) -> TrialConversionResult:
        """Convert a trial tenant to a paid subscription.

        Preserves all trial data (conversations, profiles, config) and
        upgrades the tenant to the specified paid tier. The trial's
        conversation count carries over into the new billing period.

        Args:
            tenant_id: Trial tenant to convert.
            new_tier: Target paid tier.
            billing_channel: Billing channel for the paid subscription.
            interval: Billing interval (month or year).
            stripe_customer_id: Stripe customer ID (if Stripe channel).
            stripe_subscription_id: Stripe subscription ID.
            shopify_subscription_id: Shopify subscription GID.

        Returns:
            TrialConversionResult with conversion details.

        Raises:
            ValueError: If tenant is not a trial or is not found.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        tenant = await self._tenants.read(tenant_id, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        previous_tier = tenant.get("tier", "unknown")
        if previous_tier != TenantTier.TRIAL.value:
            raise ValueError(
                f"Tenant {tenant_id} is not a trial (tier={previous_tier})"
            )

        new_tier_value = new_tier.value if isinstance(new_tier, TenantTier) else new_tier
        channel_value = billing_channel.value if isinstance(billing_channel, BillingChannel) else billing_channel

        # Get new tier defaults
        tier_defaults = TIER_DEFAULTS.get(new_tier_value, {})

        # Count trial conversations for carryover
        conversations_used = 0
        if self._usage:
            # Get current billing period's counter
            try:
                counters = await self._usage.query(
                    query="SELECT * FROM c WHERE c.tenant_id = @tid ORDER BY c.billing_period DESC",
                    parameters=[{"name": "@tid", "value": tenant_id}],
                )
                if counters:
                    conversations_used = counters[0].get("total_conversations", 0)
            except Exception:
                logger.warning("Could not fetch trial conversation count for %s", tenant_id)

        # Build patch operations for conversion
        operations: list[dict[str, Any]] = [
            {"op": "set", "path": "/tier", "value": new_tier_value},
            {"op": "set", "path": "/status", "value": TenantStatus.ACTIVE.value},
            {"op": "set", "path": "/billing_channel", "value": channel_value},
            {"op": "set", "path": "/interval", "value": interval},
            {"op": "set", "path": "/updated_at", "value": now_iso},
            # Clear trial-specific fields
            {"op": "set", "path": "/trial_expires_at", "value": None},
            {"op": "set", "path": "/trial_conversation_limit", "value": None},
            # Apply new tier rate limits
            {"op": "set", "path": "/rate_limit_rpm", "value": tier_defaults.get("rate_limit_rpm")},
            {"op": "set", "path": "/max_concurrent", "value": tier_defaults.get("max_concurrent")},
        ]

        # Set channel-specific identifiers
        if stripe_customer_id:
            operations.append({"op": "set", "path": "/stripe_customer_id", "value": stripe_customer_id})
        if stripe_subscription_id:
            operations.append({"op": "set", "path": "/stripe_subscription_id", "value": stripe_subscription_id})
        if shopify_subscription_id:
            operations.append({"op": "set", "path": "/shopify_subscription_id", "value": shopify_subscription_id})

        await self._tenants.patch(tenant_id, tenant_id, operations=operations)

        # Audit trail
        if self._audit:
            await self._audit.log_event(
                tenant_id=tenant_id,
                event_type=AuditEventType.TENANT_PROVISIONED,
                actor="system",
                details={
                    "action": "trial_conversion",
                    "previous_tier": previous_tier,
                    "new_tier": new_tier_value,
                    "billing_channel": channel_value,
                    "conversations_carried_over": conversations_used,
                },
            )

        logger.info(
            "Trial converted: tenant=%s %s→%s channel=%s conversations=%d",
            tenant_id, previous_tier, new_tier_value, channel_value, conversations_used,
        )

        return TrialConversionResult(
            tenant_id=tenant_id,
            previous_tier=previous_tier,
            new_tier=new_tier_value,
            billing_channel=channel_value,
            data_preserved=True,
            conversations_carried_over=conversations_used,
            converted_at=now_iso,
        )

    # -------------------------------------------------------------------
    # WI #125: Demo data seeder
    # -------------------------------------------------------------------

    async def seed_demo_data(self, tenant_id: str) -> DemoDataResult:
        """Seed demo data for a trial tenant.

        Populates the tenant with sample conversations, customer profiles,
        and knowledge base articles so the dashboard isn't empty on first
        login. Demo data uses non-billable prefixes to avoid counting
        toward the trial conversation cap.

        Args:
            tenant_id: The trial tenant to seed.

        Returns:
            DemoDataResult with counts of seeded items.
        """
        now = datetime.now(timezone.utc)
        conversations_seeded = 0
        profiles_seeded = 0
        articles_seeded = 0

        # Seed sample conversations (non-billable prefix "system_demo_")
        if self._conversations:
            demo_conversations = _build_demo_conversations(tenant_id, now)
            for conv in demo_conversations:
                try:
                    await self._conversations.create(conv)
                    conversations_seeded += 1
                except Exception:
                    logger.debug("Demo conversation already exists: %s", conv.get("id"))

        # Seed sample customer profile
        if self._profiles:
            demo_profiles = _build_demo_profiles(tenant_id, now)
            for profile in demo_profiles:
                try:
                    await self._profiles.create(profile)
                    profiles_seeded += 1
                except Exception:
                    logger.debug("Demo profile already exists: %s", profile.get("id"))

        # Seed sample knowledge base articles
        if self._knowledge:
            demo_articles = _build_demo_knowledge_articles(tenant_id, now)
            for article in demo_articles:
                try:
                    await self._knowledge.create(article)
                    articles_seeded += 1
                except Exception:
                    logger.debug("Demo article already exists: %s", article.get("id"))

        logger.info(
            "Demo data seeded: tenant=%s conversations=%d profiles=%d articles=%d",
            tenant_id, conversations_seeded, profiles_seeded, articles_seeded,
        )

        return DemoDataResult(
            tenant_id=tenant_id,
            conversations_seeded=conversations_seeded,
            profiles_seeded=profiles_seeded,
            knowledge_articles_seeded=articles_seeded,
        )

    # -------------------------------------------------------------------
    # WI #126: Trial-specific dashboard
    # -------------------------------------------------------------------

    async def get_trial_status(self, tenant_id: str) -> TrialStatus | None:
        """Get comprehensive trial status for dashboard display.

        Returns trial-specific metrics: days remaining, conversation
        cap usage, recommended upgrade tier, and whether messaging
        is still allowed.

        Args:
            tenant_id: The trial tenant.

        Returns:
            TrialStatus or None if tenant not found or not a trial.
        """
        tenant = await self._tenants.read(tenant_id, tenant_id)
        if not tenant:
            return None

        tier = tenant.get("tier")
        if tier != TenantTier.TRIAL.value:
            return None

        now = datetime.now(timezone.utc)

        # Parse trial expiry
        expires_at_str = tenant.get("trial_expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except (ValueError, TypeError):
                expires_at = now  # Treat as expired if unparseable
        else:
            # No expiry set — use default from creation date
            created_str = tenant.get("created_at", now.isoformat())
            try:
                created_at = datetime.fromisoformat(created_str)
            except (ValueError, TypeError):
                created_at = now
            expires_at = created_at + timedelta(days=DEFAULT_TRIAL_DURATION_DAYS)

        # Calculate remaining time
        remaining = expires_at - now
        days_remaining = max(0, remaining.days)
        hours_remaining = max(0, int(remaining.total_seconds() // 3600))

        # Get conversation usage
        conversation_limit = tenant.get(
            "trial_conversation_limit", DEFAULT_TRIAL_CONVERSATION_LIMIT
        )
        conversations_used = await self._get_trial_conversation_count(tenant_id)
        conversations_remaining = max(0, conversation_limit - conversations_used)
        usage_pct = (conversations_used / conversation_limit * 100) if conversation_limit > 0 else 0.0

        # Determine trial status
        tenant_status = tenant.get("status")
        if tenant_status == TenantStatus.TRIAL_EXPIRED.value:
            status_code = TrialStatusCode.EXPIRED
        elif expires_at <= now:
            status_code = TrialStatusCode.EXPIRED
        elif conversations_remaining <= 0:
            status_code = TrialStatusCode.CAP_REACHED
        elif days_remaining <= 3:
            status_code = TrialStatusCode.EXPIRING_SOON
        else:
            status_code = TrialStatusCode.ACTIVE

        can_send = (
            status_code in (TrialStatusCode.ACTIVE, TrialStatusCode.EXPIRING_SOON)
            and conversations_remaining > 0
        )

        # Recommend upgrade tier based on usage pattern
        if conversations_used > 30:
            recommended_tier = "professional"
        else:
            recommended_tier = "starter"

        return TrialStatus(
            tenant_id=tenant_id,
            status=status_code,
            trial_started_at=tenant.get("created_at", ""),
            trial_expires_at=expires_at.isoformat(),
            days_remaining=days_remaining,
            hours_remaining=hours_remaining,
            conversation_limit=conversation_limit,
            conversations_used=conversations_used,
            conversations_remaining=conversations_remaining,
            usage_percent=round(usage_pct, 1),
            model=TRIAL_MODEL,
            tier_after_expiry=recommended_tier,
            can_send_message=can_send,
        )

    # -------------------------------------------------------------------
    # WI #127: Expired trial data cleanup
    # -------------------------------------------------------------------

    async def cleanup_expired_trials(self) -> TrialCleanupResult:
        """Delete data for expired trial tenants past the grace period.

        Trial tenants that have been in TRIAL_EXPIRED status for longer
        than TRIAL_EXPIRED_GRACE_DAYS (30 days) have all their data
        deleted. This satisfies GDPR data minimization (Article 5).

        Should be called periodically (e.g., daily via scheduled task).

        Returns:
            TrialCleanupResult with counts of cleaned tenants.
        """
        now = datetime.now(timezone.utc)
        grace_cutoff = now - timedelta(days=TRIAL_EXPIRED_GRACE_DAYS)

        # Query expired trial tenants
        expired_tenants = await self._tenants.query(
            query="SELECT * FROM c WHERE c.tier = @tier AND c.status = @status",
            parameters=[
                {"name": "@tier", "value": TenantTier.TRIAL.value},
                {"name": "@status", "value": TenantStatus.TRIAL_EXPIRED.value},
            ],
        )

        cleaned_ids: list[str] = []

        for tenant in expired_tenants:
            tenant_id = tenant["tenant_id"]
            updated_str = tenant.get("updated_at", "")

            try:
                updated_at = datetime.fromisoformat(updated_str)
            except (ValueError, TypeError):
                continue

            if updated_at > grace_cutoff:
                # Still within grace period
                continue

            # Grace period elapsed — delete tenant data
            await self._delete_tenant_data(tenant_id)

            # Update tenant status to DEACTIVATED
            await self._tenants.patch(
                tenant_id,
                tenant_id,
                operations=[
                    {"op": "set", "path": "/status", "value": TenantStatus.DEACTIVATED.value},
                    {"op": "set", "path": "/updated_at", "value": now.isoformat()},
                    {"op": "set", "path": "/deactivated_at", "value": now.isoformat()},
                ],
            )

            if self._audit:
                await self._audit.log_event(
                    tenant_id=tenant_id,
                    event_type=AuditEventType.DATA_DELETED,
                    actor="system",
                    details={"reason": "trial_expired_grace_period_elapsed"},
                )

            cleaned_ids.append(tenant_id)
            logger.info("Expired trial cleaned: tenant=%s", tenant_id)

        return TrialCleanupResult(
            tenants_cleaned=len(cleaned_ids),
            tenant_ids=cleaned_ids,
        )

    # -------------------------------------------------------------------
    # WI #128: Trial metrics isolation
    # -------------------------------------------------------------------

    @staticmethod
    def is_trial_tenant(tenant: dict[str, Any]) -> bool:
        """Check if a tenant is a trial tenant.

        Used by analytics and reporting services to exclude trial
        conversations from platform-wide benchmarks.

        Args:
            tenant: Tenant document dict.

        Returns:
            True if the tenant is on the trial tier.
        """
        return tenant.get("tier") == TenantTier.TRIAL.value

    @staticmethod
    def should_exclude_from_benchmarks(tenant: dict[str, Any]) -> bool:
        """Whether this tenant's data should be excluded from benchmarks.

        Trial and expired trial tenants are excluded from:
        - Platform-wide performance benchmarks
        - Average response time calculations
        - Conversation quality metrics
        - Cost-per-conversation reporting

        Args:
            tenant: Tenant document dict.

        Returns:
            True if this tenant should be excluded from platform benchmarks.
        """
        tier = tenant.get("tier")
        status = tenant.get("status")
        return (
            tier == TenantTier.TRIAL.value
            or status == TenantStatus.TRIAL_EXPIRED.value
        )

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    async def _get_trial_conversation_count(self, tenant_id: str) -> int:
        """Get the total conversation count for a trial tenant.

        Counts all billable conversations (excludes system_ and test_ prefixes).
        """
        if not self._conversations:
            return 0

        try:
            results = await self._conversations.query(
                query=(
                    "SELECT VALUE COUNT(1) FROM c "
                    "WHERE c.tenant_id = @tid AND c.is_billable = true"
                ),
                parameters=[{"name": "@tid", "value": tenant_id}],
            )
            return results[0] if results else 0
        except Exception:
            logger.warning("Could not count trial conversations for %s", tenant_id)
            return 0

    async def _delete_tenant_data(self, tenant_id: str) -> None:
        """Delete all data for a tenant across all collections.

        Deletion order follows referential consistency:
        memory_vectors → customer_profiles → conversations → usage →
        knowledge_bases → preferences
        """
        collections_and_repos = [
            ("conversations", self._conversations),
            ("profiles", self._profiles),
            ("knowledge", self._knowledge),
            ("usage", self._usage),
        ]

        for name, repo in collections_and_repos:
            if repo is None:
                continue
            try:
                items = await repo.query(
                    query="SELECT c.id FROM c WHERE c.tenant_id = @tid",
                    parameters=[{"name": "@tid", "value": tenant_id}],
                )
                for item in items:
                    try:
                        await repo.delete(item["id"], tenant_id)
                    except Exception:
                        logger.debug(
                            "Could not delete %s item %s for tenant %s",
                            name, item.get("id"), tenant_id,
                        )
            except Exception:
                logger.warning(
                    "Could not query %s for tenant %s cleanup", name, tenant_id,
                )


# ---------------------------------------------------------------------------
# Demo data builders (WI #125)
# ---------------------------------------------------------------------------


def _build_demo_conversations(
    tenant_id: str, now: datetime
) -> list[dict[str, Any]]:
    """Build sample conversations for demo seeding."""
    conversations = []
    demo_data = [
        {
            "customer_name": "Sarah Johnson",
            "topic": "Product sizing help",
            "messages": 4,
            "status": "completed",
            "delta_hours": -2,
        },
        {
            "customer_name": "Mike Chen",
            "topic": "Shipping status inquiry",
            "messages": 3,
            "status": "completed",
            "delta_hours": -5,
        },
        {
            "customer_name": "Emily Davis",
            "topic": "Return policy question",
            "messages": 6,
            "status": "completed",
            "delta_hours": -12,
        },
        {
            "customer_name": "James Wilson",
            "topic": "Product recommendation",
            "messages": 8,
            "status": "completed",
            "delta_hours": -24,
        },
        {
            "customer_name": "Lisa Park",
            "topic": "Order modification request",
            "messages": 5,
            "status": "escalated",
            "delta_hours": -1,
        },
    ]

    for i, data in enumerate(demo_data):
        conv_id = f"system_demo_{tenant_id[:8]}_{i}"
        started = now + timedelta(hours=data["delta_hours"])
        conversations.append({
            "id": conv_id,
            "tenant_id": tenant_id,
            "conversation_id": conv_id,
            "customer_id": f"demo_customer_{i}",
            "customer_name": data["customer_name"],
            "status": data["status"],
            "is_billable": False,  # Demo conversations are not billable
            "message_count": data["messages"],
            "turn_count": data["messages"] // 2,
            "topic": data["topic"],
            "started_at": started.isoformat(),
            "ended_at": (started + timedelta(minutes=data["messages"] * 2)).isoformat(),
            "created_at": started.isoformat(),
            "updated_at": started.isoformat(),
        })

    return conversations


def _build_demo_profiles(
    tenant_id: str, now: datetime
) -> list[dict[str, Any]]:
    """Build sample customer profiles for demo seeding."""
    profiles = [
        {
            "id": f"demo_profile_{tenant_id[:8]}_0",
            "tenant_id": tenant_id,
            "customer_id": "demo_customer_0",
            "display_name": "Sarah Johnson",
            "email": "sarah.j@example.com",
            "total_orders": 3,
            "total_spend": 245.50,
            "last_order_date": (now - timedelta(days=7)).isoformat(),
            "preferred_language": "en",
            "tags": ["repeat_buyer", "size_sensitive"],
            "created_at": (now - timedelta(days=30)).isoformat(),
            "updated_at": now.isoformat(),
        },
        {
            "id": f"demo_profile_{tenant_id[:8]}_1",
            "tenant_id": tenant_id,
            "customer_id": "demo_customer_1",
            "display_name": "Mike Chen",
            "email": "mike.c@example.com",
            "total_orders": 1,
            "total_spend": 89.99,
            "last_order_date": (now - timedelta(days=2)).isoformat(),
            "preferred_language": "en",
            "tags": ["new_customer"],
            "created_at": (now - timedelta(days=5)).isoformat(),
            "updated_at": now.isoformat(),
        },
    ]
    return profiles


def _build_demo_knowledge_articles(
    tenant_id: str, now: datetime
) -> list[dict[str, Any]]:
    """Build sample knowledge base articles for demo seeding."""
    articles = [
        {
            "id": f"demo_kb_{tenant_id[:8]}_0",
            "tenant_id": tenant_id,
            "title": "Shipping & Delivery",
            "content": (
                "We offer free standard shipping on orders over $50. "
                "Standard delivery takes 5-7 business days. "
                "Express shipping (2-3 business days) is available for $12.99."
            ),
            "category": "policies",
            "status": "published",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        },
        {
            "id": f"demo_kb_{tenant_id[:8]}_1",
            "tenant_id": tenant_id,
            "title": "Returns & Exchanges",
            "content": (
                "Items can be returned within 30 days of delivery for a full refund. "
                "Items must be unworn and in original packaging. "
                "Exchanges are processed within 3-5 business days."
            ),
            "category": "policies",
            "status": "published",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        },
        {
            "id": f"demo_kb_{tenant_id[:8]}_2",
            "tenant_id": tenant_id,
            "title": "Size Guide",
            "content": (
                "Use our size chart to find your perfect fit. "
                "Measure your chest, waist, and hips in inches. "
                "If between sizes, we recommend sizing up for comfort."
            ),
            "category": "product_info",
            "status": "published",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        },
    ]
    return articles


# ---------------------------------------------------------------------------
# REST API endpoints (WI #126 — trial dashboard)
# ---------------------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel as PydanticBaseModel

trial_router = APIRouter(prefix="/api/trial", tags=["trial"])

# Module-level service reference (set during app startup)
_trial_service: TrialManagementService | None = None


def configure_trial_service(service: TrialManagementService) -> None:
    """Wire the trial service at app startup."""
    global _trial_service
    _trial_service = service


def _get_trial_service() -> TrialManagementService:
    """FastAPI dependency for trial service access."""
    if _trial_service is None:
        raise HTTPException(status_code=503, detail="Trial service not configured")
    return _trial_service


# Response models

class TrialStatusResponse(PydanticBaseModel):
    """Trial status response for dashboard display."""

    status: str
    trial_started_at: str
    trial_expires_at: str
    days_remaining: int
    hours_remaining: int
    conversation_limit: int
    conversations_used: int
    conversations_remaining: int
    usage_percent: float
    model: str
    tier_after_expiry: str | None
    can_send_message: bool


class TrialProvisionRequest(PydanticBaseModel):
    """Request to provision a new trial tenant."""

    customer_email: str | None = None
    shopify_shop_domain: str | None = None
    trial_duration_days: int = DEFAULT_TRIAL_DURATION_DAYS
    conversation_limit: int = DEFAULT_TRIAL_CONVERSATION_LIMIT
    seed_demo_data: bool = True


class TrialProvisionResponse(PydanticBaseModel):
    """Response from trial provisioning."""

    tenant_id: str
    status: str
    tier: str
    trial_expires_at: str
    conversation_limit: int


class TrialConvertRequest(PydanticBaseModel):
    """Request to convert trial to paid subscription."""

    new_tier: str
    billing_channel: str
    interval: str = "month"
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    shopify_subscription_id: str | None = None


class TrialConvertResponse(PydanticBaseModel):
    """Response from trial conversion."""

    tenant_id: str
    previous_tier: str
    new_tier: str
    billing_channel: str
    data_preserved: bool
    conversations_carried_over: int
    converted_at: str


# Endpoints

@trial_router.post("/provision", response_model=TrialProvisionResponse)
async def provision_trial_endpoint(
    request: TrialProvisionRequest,
    service: TrialManagementService = Depends(_get_trial_service),
) -> TrialProvisionResponse:
    """Provision a new trial tenant."""
    tenant_doc = await service.provision_trial(
        customer_email=request.customer_email,
        shopify_shop_domain=request.shopify_shop_domain,
        trial_duration_days=request.trial_duration_days,
        conversation_limit=request.conversation_limit,
        seed_demo_data=request.seed_demo_data,
    )
    return TrialProvisionResponse(
        tenant_id=tenant_doc["tenant_id"],
        status=tenant_doc["status"],
        tier=tenant_doc["tier"],
        trial_expires_at=tenant_doc["trial_expires_at"],
        conversation_limit=tenant_doc.get("trial_conversation_limit", DEFAULT_TRIAL_CONVERSATION_LIMIT),
    )


@trial_router.get("/status/{tenant_id}", response_model=TrialStatusResponse)
async def get_trial_status_endpoint(
    tenant_id: str,
    service: TrialManagementService = Depends(_get_trial_service),
) -> TrialStatusResponse:
    """Get trial status for dashboard display."""
    status = await service.get_trial_status(tenant_id)
    if not status:
        raise HTTPException(status_code=404, detail="Trial tenant not found")

    return TrialStatusResponse(
        status=status.status.value,
        trial_started_at=status.trial_started_at,
        trial_expires_at=status.trial_expires_at,
        days_remaining=status.days_remaining,
        hours_remaining=status.hours_remaining,
        conversation_limit=status.conversation_limit,
        conversations_used=status.conversations_used,
        conversations_remaining=status.conversations_remaining,
        usage_percent=status.usage_percent,
        model=status.model,
        tier_after_expiry=status.tier_after_expiry,
        can_send_message=status.can_send_message,
    )


@trial_router.post("/convert/{tenant_id}", response_model=TrialConvertResponse)
async def convert_trial_endpoint(
    tenant_id: str,
    request: TrialConvertRequest,
    service: TrialManagementService = Depends(_get_trial_service),
) -> TrialConvertResponse:
    """Convert a trial tenant to a paid subscription."""
    try:
        result = await service.convert_trial_to_paid(
            tenant_id=tenant_id,
            new_tier=request.new_tier,
            billing_channel=request.billing_channel,
            interval=request.interval,
            stripe_customer_id=request.stripe_customer_id,
            stripe_subscription_id=request.stripe_subscription_id,
            shopify_subscription_id=request.shopify_subscription_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TrialConvertResponse(
        tenant_id=result.tenant_id,
        previous_tier=result.previous_tier,
        new_tier=result.new_tier,
        billing_channel=result.billing_channel,
        data_preserved=result.data_preserved,
        conversations_carried_over=result.conversations_carried_over,
        converted_at=result.converted_at,
    )
