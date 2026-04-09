"""
Usage repository — usage counters, pack balances, and idempotency keys.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_USAGE,
    IdempotencyKeyDocument,
    PackBalanceDocument,
    TenantTier,
    UsageCounterDocument,
)
from src.multi_tenant.repositories.base import DocumentNotFoundError, TenantScopedRepository


class UsageRepository(TenantScopedRepository):
    """Repository for the usage collection.

    Manages usage counters, pack balances, and idempotency keys.
    Uses atomic patch operations for counter increments (no
    read-modify-write race conditions).
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_USAGE)

    # --- Usage counters ---

    async def get_or_create_counter(
        self,
        tenant_id: str,
        billing_period: str,
        tier: TenantTier | None = None,
    ) -> dict[str, Any]:
        """Get or create a usage counter for a billing period.

        Args:
            tenant_id: Tenant partition key.
            billing_period: Period identifier (e.g. "2026-02").
            tier: Tenant's current tier (used to set included_allowance
                  on new counters).

        Returns:
            The usage counter document.
        """
        doc_id = f"{tenant_id}:{billing_period}"

        try:
            return await self.read(tenant_id, doc_id)
        except DocumentNotFoundError:
            included = 0
            if tier:
                from src.multi_tenant.entitlement_service import get_entitlement_service
                defaults = await get_entitlement_service().get_tier_config(tier.value)
                included = defaults.get("included_conversations", 0)

            counter = UsageCounterDocument(
                id=doc_id,
                tenant_id=tenant_id,
                billing_period=billing_period,
                tier=tier,
                included_allowance=included,
            )
            return await self.create(tenant_id, counter)

    async def increment_conversations(
        self,
        tenant_id: str,
        billing_period: str,
        count: int = 1,
    ) -> dict[str, Any]:
        """Atomically increment the conversation counter.

        Uses Cosmos DB patch "incr" operation — no read-modify-write
        race condition.
        """
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/total_conversations", "value": count},
            ],
        )

    async def increment_overage_reported(
        self,
        tenant_id: str,
        billing_period: str,
        count: int,
    ) -> dict[str, Any]:
        """Atomically increment the overage reported counter."""
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/overage_reported", "value": count},
            ],
        )

    async def increment_pack_consumed(
        self,
        tenant_id: str,
        billing_period: str,
        count: int,
    ) -> dict[str, Any]:
        """Atomically increment the pack consumed counter."""
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/pack_consumed", "value": count},
            ],
        )

    # --- Pack balances ---

    async def create_pack(
        self, tenant_id: str, pack: PackBalanceDocument,
    ) -> dict[str, Any]:
        """Create a new pack balance entry."""
        return await self.create(tenant_id, pack)

    async def get_active_packs(
        self, tenant_id: str, now_iso: str,
    ) -> list[dict[str, Any]]:
        """Get all active (non-expired, non-depleted) packs, oldest first.

        FIFO consumption order: oldest purchased_at first.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.pack_id != null "
                "AND c.remaining > 0 "
                "AND c.expires_at > @now "
                "ORDER BY c.purchased_at ASC"
            ),
            parameters=[{"name": "@now", "value": now_iso}],
        )

    async def consume_from_pack(
        self,
        tenant_id: str,
        pack_doc_id: str,
        amount: int,
    ) -> dict[str, Any]:
        """Atomically decrement a pack's remaining balance."""
        return await self.patch(
            tenant_id=tenant_id,
            document_id=pack_doc_id,
            operations=[
                {"op": "incr", "path": "/remaining", "value": -amount},
            ],
        )

    # --- Idempotency keys ---

    async def check_idempotency(
        self, tenant_id: str, event_id: str,
    ) -> bool:
        """Check if an event has already been processed.

        Returns True if the event_id exists (duplicate), False if new.
        """
        doc_id = event_id
        try:
            await self.read(tenant_id, doc_id)
            return True  # Already processed
        except DocumentNotFoundError:
            return False  # New event

    async def record_idempotency(
        self, tenant_id: str, event_id: str, event_type: str,
    ) -> dict[str, Any]:
        """Record that an event has been processed.

        Uses create (not upsert) so duplicate attempts raise
        DocumentConflictError — providing an additional safety net
        against race conditions.
        """
        now = datetime.now(UTC).isoformat()
        doc = IdempotencyKeyDocument(
            id=event_id,
            tenant_id=tenant_id,
            event_id=event_id,
            event_type=event_type,
            processed_at=now,
        )
        return await self.create(tenant_id, doc)
