"""
Tenant repository — tenants collection CRUD + lookup by channel ID.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_TENANTS,
    TenantStatus,
)
from src.multi_tenant.repositories.base import TenantScopedRepository


class TenantRepository(TenantScopedRepository):
    """Repository for the tenants collection.

    Provides tenant CRUD operations and lookup by channel identifiers
    (Stripe customer ID, Shopify shop domain).
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_TENANTS)

    async def get_by_stripe_customer_id(
        self, tenant_id: str, stripe_customer_id: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Stripe customer ID within a partition.

        Note: This queries within a known tenant partition. For
        cross-partition lookup by Stripe ID (e.g., webhook processing),
        use find_by_stripe_customer_id() which performs a cross-partition query.
        """
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c WHERE c.stripe_customer_id = @stripe_id"
            ),
            parameters=[{"name": "@stripe_id", "value": stripe_customer_id}],
            max_items=1,
        )
        return results[0] if results else None

    async def find_by_stripe_customer_id(
        self, stripe_customer_id: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Stripe customer ID (cross-partition).

        Used during webhook processing where tenant_id is unknown.
        This performs a cross-partition query — use sparingly.

        Args:
            stripe_customer_id: Stripe cus_... identifier.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.stripe_customer_id = @stripe_id",
            parameters=[{"name": "@stripe_id", "value": stripe_customer_id}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_shopify_domain(
        self, shopify_shop_domain: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Shopify shop domain (cross-partition).

        Used during Shopify webhook/auth processing where tenant_id
        is unknown.

        Args:
            shopify_shop_domain: *.myshopify.com domain.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.shopify_shop_domain = @domain",
            parameters=[{"name": "@domain", "value": shopify_shop_domain}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_api_key_hash(
        self, api_key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by API key hash (cross-partition).

        Used during API key authentication where tenant_id is unknown.
        This performs a cross-partition query — use sparingly.

        Args:
            api_key_hash: SHA-256 hex digest of the API key.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.api_key_hash = @hash",
            parameters=[{"name": "@hash", "value": api_key_hash}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_customer_email(
        self, email: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by customer email (cross-partition).

        Used during API key reset workflow where the merchant provides
        their email but has no valid API key for authentication.
        This performs a cross-partition query -- use sparingly.

        Args:
            email: The merchant's registered email address.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.customer_email = @email",
            parameters=[{"name": "@email", "value": email}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_widget_key_hash(
        self, widget_key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by widget key hash (cross-partition).

        Used during publishable widget key authentication (Decision UI-6)
        where tenant_id is unknown. Scoped to /api/chat/* endpoints only.

        Args:
            widget_key_hash: SHA-256 hex digest of the widget key.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.widget_key_hash = @hash",
            parameters=[{"name": "@hash", "value": widget_key_hash}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def list_by_status(
        self, tenant_id: str, status: TenantStatus,
    ) -> list[dict[str, Any]]:
        """List tenants with a specific status (within partition)."""
        return await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.status = @status",
            parameters=[{"name": "@status", "value": status.value}],
        )

    async def list_active_tenant_ids(self) -> list[str]:
        """List all active tenant IDs (cross-partition).

        Used by the idle conversation scanner to enumerate tenants.
        Performs a cross-partition query — call infrequently.
        """
        ids: list[str] = []
        async for item in self._container.query_items(
            query="SELECT c.tenant_id FROM c WHERE c.status = 'active'",
            max_item_count=100,
        ):
            tid = item.get("tenant_id")
            if tid and tid not in ids:
                ids.append(tid)
        return ids

    async def list_expired_trials(self) -> list[dict[str, Any]]:
        """List active trial tenants whose trial period has expired (cross-partition).

        Returns tenant documents where:
            - status = 'active'
            - billing_channel = 'trial'
            - trial_expires_at < current UTC time (ISO 8601 comparison)

        Used by the trial expiry scanner background task.
        Performs a cross-partition query — call infrequently (hourly).
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        results: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c WHERE c.status = 'active' "
                "AND c.billing_channel = 'trial' "
                "AND c.trial_expires_at < @now"
            ),
            parameters=[{"name": "@now", "value": now_iso}],
            max_item_count=100,
        ):
            results.append(item)
        return results

    async def list_expiring_trials(self, within_iso: str) -> list[dict[str, Any]]:
        """List active trial tenants expiring before the given timestamp (cross-partition).

        Returns tenant documents where:
            - status = 'active'
            - billing_channel = 'trial'
            - trial_expires_at is between now and within_iso

        Used by the trial expiry warning background task.
        Performs a cross-partition query — call infrequently (every 12 hours).

        Args:
            within_iso: ISO 8601 upper-bound timestamp. Tenants expiring
                before this time (but still in the future) are returned.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        results: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c WHERE c.status = 'active' "
                "AND c.billing_channel = 'trial' "
                "AND c.trial_expires_at > @now "
                "AND c.trial_expires_at <= @within"
            ),
            parameters=[
                {"name": "@now", "value": now_iso},
                {"name": "@within", "value": within_iso},
            ],
            max_item_count=100,
        ):
            results.append(item)
        return results

    # ------------------------------------------------------------------
    # General access expiry queries (WI-EXPIRY-1)
    # ------------------------------------------------------------------

    async def list_expired_tenants(self) -> list[dict[str, Any]]:
        """List active tenants whose general access has expired (cross-partition).

        Returns tenant documents where:
            - status = 'active'
            - expires_at is set (not null)
            - expires_at < current UTC time (ISO 8601 comparison)

        No billing_channel filter — works for ANY channel.
        Used by the access expiry scanner background task.
        Performs a cross-partition query — call infrequently (hourly).
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        results: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c WHERE c.status = 'active' "
                "AND IS_DEFINED(c.expires_at) "
                "AND c.expires_at != null "
                "AND c.expires_at < @now"
            ),
            parameters=[{"name": "@now", "value": now_iso}],
            max_item_count=100,
        ):
            results.append(item)
        return results

    async def list_expiring_tenants(self, within_iso: str) -> list[dict[str, Any]]:
        """List active tenants expiring before the given timestamp (cross-partition).

        Returns tenant documents where:
            - status = 'active'
            - expires_at is set (not null)
            - expires_at is between now and within_iso

        No billing_channel filter — works for ANY channel.
        Used by the access expiry warning background task.
        Performs a cross-partition query — call infrequently (every 12 hours).

        Args:
            within_iso: ISO 8601 upper-bound timestamp. Tenants expiring
                before this time (but still in the future) are returned.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        results: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c WHERE c.status = 'active' "
                "AND IS_DEFINED(c.expires_at) "
                "AND c.expires_at != null "
                "AND c.expires_at > @now "
                "AND c.expires_at <= @within"
            ),
            parameters=[
                {"name": "@now", "value": now_iso},
                {"name": "@within", "value": within_iso},
            ],
            max_item_count=100,
        ):
            results.append(item)
        return results

    async def update_status(
        self, tenant_id: str, status: TenantStatus,
    ) -> dict[str, Any]:
        """Update a tenant's lifecycle status."""
        now = datetime.now(timezone.utc).isoformat()
        operations = [
            {"op": "set", "path": "/status", "value": status.value},
            {"op": "set", "path": "/updated_at", "value": now},
        ]

        if status == TenantStatus.GRACE_PERIOD:
            operations.append({"op": "set", "path": "/deactivated_at", "value": now})

        return await self.patch(tenant_id, tenant_id, operations)
