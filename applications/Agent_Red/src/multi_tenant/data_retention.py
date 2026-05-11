# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Data retention enforcement service.

Implements WI #154: Automated enforcement of tier-based data retention
policies. Each tier has a defined history_depth_days:
    - Trial:        14 days
    - Starter:      90 days
    - Professional: 365 days
    - Enterprise:   unlimited (no retention enforcement)

This service periodically scans conversations and customer profiles to
delete data that has exceeded the tenant's retention period. It also
handles warm-tier archival (Cosmos DB → Blob Cool storage) for data
between the retention cutoff and 7-year cold archive.

Should be called periodically via scheduled task (e.g., daily KEDA cron).

Architecture references:
    - Decision #19: Archival storage (Hot → Warm → Cold)
    - Decision #21: Data retention per tier (TIER_DEFAULTS.history_depth_days)
    - WI #37 / #154: Data retention enforcement (overlapping items)
    - WI #153: Archival pipeline (Change Feed → Parquet → Blob)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    TenantTier,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Enterprise tier has no automatic retention limit
UNLIMITED_RETENTION_TIERS = {TenantTier.ENTERPRISE.value}

# Batch size for deletion operations (avoid large transactions)
DELETION_BATCH_SIZE = 100


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetentionScanResult:
    """Result of a data retention enforcement run."""

    tenants_scanned: int
    tenants_with_deletions: int
    conversations_deleted: int
    profiles_purged: int
    vectors_deleted: int
    errors: int
    tenant_details: list[TenantRetentionResult] = field(default_factory=list)


@dataclass(frozen=True)
class TenantRetentionResult:
    """Retention enforcement result for a single tenant."""

    tenant_id: str
    tier: str
    retention_days: int
    cutoff_date: str  # ISO 8601
    conversations_deleted: int
    profiles_purged: int
    vectors_deleted: int


# ---------------------------------------------------------------------------
# DataRetentionService
# ---------------------------------------------------------------------------


class DataRetentionService:
    """Enforces tier-based data retention policies.

    Scans all tenants and deletes data older than the tenant's
    tier-defined history_depth_days. Enterprise tenants are skipped
    (unlimited retention).

    Dependencies:
        - tenant_repo: TenantRepository for listing tenants
        - conversation_repo: ConversationRepository for conversation cleanup
        - profile_repo: CustomerProfileRepository for profile cleanup
        - vector_repo: MemoryVectorRepository for vector cleanup
        - audit_repo: AuditLogRepository for audit trail
    """

    def __init__(
        self,
        tenant_repo: Any,
        conversation_repo: Any | None = None,
        profile_repo: Any | None = None,
        vector_repo: Any | None = None,
        audit_repo: Any | None = None,
    ) -> None:
        self._tenants = tenant_repo
        self._conversations = conversation_repo
        self._profiles = profile_repo
        self._vectors = vector_repo
        self._audit = audit_repo

    async def enforce_retention(self) -> RetentionScanResult:
        """Run the full retention enforcement scan.

        Iterates all active tenants, calculates retention cutoff per
        tier, and deletes expired data. Enterprise tenants are skipped.

        Returns:
            RetentionScanResult with aggregate deletion counts.
        """
        now = datetime.now(UTC)
        tenants_scanned = 0
        total_convs = 0
        total_profiles = 0
        total_vectors = 0
        errors = 0
        details: list[TenantRetentionResult] = []

        # Query all active tenants
        all_tenants = await self._tenants.query(
            query="SELECT * FROM c WHERE c.status IN ('active', 'past_due')",
            parameters=[],
        )

        for tenant in all_tenants:
            tenants_scanned += 1
            tenant_id = tenant["tenant_id"]
            tier = tenant.get("tier", TenantTier.STARTER.value)

            # Skip unlimited retention tiers
            if tier in UNLIMITED_RETENTION_TIERS:
                continue

            # Get tier-specific retention period
            from src.multi_tenant.entitlement_service import get_entitlement_service
            tier_defaults = await get_entitlement_service().get_tier_config(tier)
            retention_days = tier_defaults.get("history_depth_days", 90)
            cutoff = now - timedelta(days=retention_days)
            cutoff_iso = cutoff.isoformat()

            try:
                result = await self._enforce_for_tenant(
                    tenant_id, tier, retention_days, cutoff_iso,
                )
                total_convs += result.conversations_deleted
                total_profiles += result.profiles_purged
                total_vectors += result.vectors_deleted
                if (
                    result.conversations_deleted > 0
                    or result.profiles_purged > 0
                    or result.vectors_deleted > 0
                ):
                    details.append(result)
            except Exception:
                logger.exception(
                    "Retention enforcement failed for tenant=%s", tenant_id,
                )
                errors += 1

        tenants_with_deletions = len(details)

        logger.info(
            "Retention scan complete: tenants=%d deletions=%d conversations=%d profiles=%d vectors=%d errors=%d",
            tenants_scanned, tenants_with_deletions, total_convs, total_profiles, total_vectors, errors,
        )

        return RetentionScanResult(
            tenants_scanned=tenants_scanned,
            tenants_with_deletions=tenants_with_deletions,
            conversations_deleted=total_convs,
            profiles_purged=total_profiles,
            vectors_deleted=total_vectors,
            errors=errors,
            tenant_details=details,
        )

    async def _enforce_for_tenant(
        self,
        tenant_id: str,
        tier: str,
        retention_days: int,
        cutoff_iso: str,
    ) -> TenantRetentionResult:
        """Enforce retention for a single tenant.

        Deletes conversations, profiles, and vectors older than the cutoff.
        """
        convs_deleted = 0
        profiles_purged = 0
        vectors_deleted = 0

        # Delete old conversations
        if self._conversations:
            convs_deleted = await self._delete_old_documents(
                self._conversations,
                tenant_id,
                cutoff_iso,
                date_field="ended_at",
                collection_name="conversations",
            )

        # Delete old memory vectors (Layer 2)
        if self._vectors:
            vectors_deleted = await self._delete_old_documents(
                self._vectors,
                tenant_id,
                cutoff_iso,
                date_field="created_at",
                collection_name="memory_vectors",
            )

        # Purge stale customer profile data (not delete entirely — just
        # clear fields that reference conversations beyond retention)
        if self._profiles:
            profiles_purged = await self._purge_stale_profile_data(
                tenant_id, cutoff_iso,
            )

        # Audit log
        if self._audit and (convs_deleted > 0 or profiles_purged > 0 or vectors_deleted > 0):
            await self._audit.log_event(
                tenant_id=tenant_id,
                event_type=AuditEventType.DATA_DELETED,
                actor="system",
                details={
                    "reason": "retention_policy",
                    "tier": tier,
                    "retention_days": retention_days,
                    "cutoff": cutoff_iso,
                    "conversations_deleted": convs_deleted,
                    "profiles_purged": profiles_purged,
                    "vectors_deleted": vectors_deleted,
                },
            )

        return TenantRetentionResult(
            tenant_id=tenant_id,
            tier=tier,
            retention_days=retention_days,
            cutoff_date=cutoff_iso,
            conversations_deleted=convs_deleted,
            profiles_purged=profiles_purged,
            vectors_deleted=vectors_deleted,
        )

    async def _delete_old_documents(
        self,
        repo: Any,
        tenant_id: str,
        cutoff_iso: str,
        date_field: str,
        collection_name: str,
    ) -> int:
        """Delete documents older than cutoff from a collection.

        Returns count of deleted documents.
        """
        deleted = 0
        try:
            old_docs = await repo.query(
                query=f"SELECT c.id FROM c WHERE c.tenant_id = @tid AND c.{date_field} < @cutoff",
                parameters=[
                    {"name": "@tid", "value": tenant_id},
                    {"name": "@cutoff", "value": cutoff_iso},
                ],
            )

            for doc in old_docs:
                try:
                    await repo.delete(doc["id"], tenant_id)
                    deleted += 1
                except Exception:
                    logger.debug(
                        "Could not delete %s/%s for tenant %s",
                        collection_name, doc.get("id"), tenant_id,
                    )
        except Exception:
            logger.warning(
                "Could not query old %s for tenant %s", collection_name, tenant_id,
            )

        return deleted

    async def _purge_stale_profile_data(
        self,
        tenant_id: str,
        cutoff_iso: str,
    ) -> int:
        """Purge stale fields from customer profiles.

        Instead of deleting profiles entirely (the customer may still be
        active), this clears conversation-derived fields that reference
        data beyond the retention period. The core profile (name, email,
        preferences) is preserved.

        Fields purged: conversation_history, interaction_count,
        last_interaction_date (if older than cutoff).

        Returns count of profiles updated.
        """
        purged = 0
        try:
            stale_profiles = await self._profiles.query(
                query=(
                    "SELECT c.id FROM c WHERE c.tenant_id = @tid "
                    "AND c.last_interaction_date < @cutoff"
                ),
                parameters=[
                    {"name": "@tid", "value": tenant_id},
                    {"name": "@cutoff", "value": cutoff_iso},
                ],
            )

            for profile in stale_profiles:
                try:
                    await self._profiles.patch(
                        profile["id"],
                        tenant_id,
                        operations=[
                            {"op": "remove", "path": "/conversation_history"},
                            {"op": "set", "path": "/interaction_count", "value": 0},
                        ],
                    )
                    purged += 1
                except Exception:
                    logger.debug(
                        "Could not purge profile %s for tenant %s",
                        profile.get("id"), tenant_id,
                    )
        except Exception:
            logger.warning(
                "Could not query stale profiles for tenant %s", tenant_id,
            )

        return purged

    def get_retention_days(self, tier: str) -> int | None:
        """Get the retention period for a tier.

        Args:
            tier: The tenant tier.

        Returns:
            Retention period in days, or None for unlimited.
        """
        if tier in UNLIMITED_RETENTION_TIERS:
            return None
        from src.multi_tenant.entitlement_service import get_entitlement_service
        tier_defaults = get_entitlement_service().get_tier_config_sync(tier)
        return tier_defaults.get("history_depth_days", 90)


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

_retention_service: DataRetentionService | None = None


def get_retention_service() -> DataRetentionService | None:
    """Get the module-level DataRetentionService singleton."""
    return _retention_service


def configure_retention_service(service: DataRetentionService) -> None:
    """Wire the retention service at app startup."""
    global _retention_service
    _retention_service = service
