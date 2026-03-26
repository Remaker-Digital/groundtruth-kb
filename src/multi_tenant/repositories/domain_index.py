"""Domain Index Repository — single-partition lookups for SPEC-1644.

Provides O(1) point reads to resolve external identifiers (Shopify shop
domains, Stripe customer IDs) to tenant IDs without cross-partition queries.

Documents are keyed by the domain/identifier string. The partition key
is ``/domain`` so every lookup is a single-partition point read.

Schema:
    {
        "id": "<domain-string>",          # e.g. "blanco-9939.myshopify.com"
        "domain": "<domain-string>",      # partition key (same as id)
        "tenant_id": "<tenant-id>",       # e.g. "test-customer-001"
        "domain_type": "shopify" | "stripe",
    }

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import COLLECTION_DOMAIN_INDEX

logger = logging.getLogger(__name__)


class DomainIndexRepository:
    """Repository for the domain_index collection.

    Platform-scoped (not tenant-scoped). Partition key is ``domain``.
    Every lookup is a single-partition point read — no cross-partition
    queries are ever performed.
    """

    _collection_name = COLLECTION_DOMAIN_INDEX

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def lookup(self, domain: str) -> str | None:
        """Resolve a domain/identifier to a tenant ID.

        Args:
            domain: The external identifier (e.g. "blanco-9939.myshopify.com"
                or Stripe customer ID "cus_...").

        Returns:
            The tenant_id, or None if not indexed.
        """
        try:
            item = await self._container.read_item(
                item=domain,
                partition_key=domain,
            )
            return item.get("tenant_id")
        except Exception:
            # CosmosResourceNotFoundError or other — domain not indexed
            return None

    async def upsert(
        self,
        domain: str,
        tenant_id: str,
        domain_type: str = "shopify",
    ) -> None:
        """Create or update a domain → tenant_id mapping.

        Args:
            domain: The external identifier.
            tenant_id: The tenant ID to map to.
            domain_type: Classification ("shopify" or "stripe").
        """
        doc = {
            "id": domain,
            "domain": domain,
            "tenant_id": tenant_id,
            "domain_type": domain_type,
        }
        try:
            await self._container.upsert_item(doc)
            logger.info(
                "Domain index upserted: domain=%s tenant=%s type=%s",
                domain, tenant_id, domain_type,
            )
        except Exception:
            logger.exception(
                "Failed to upsert domain index: domain=%s tenant=%s",
                domain, tenant_id,
            )

    async def delete(self, domain: str) -> None:
        """Remove a domain mapping (e.g. when tenant is deprovisioned)."""
        try:
            await self._container.delete_item(
                item=domain,
                partition_key=domain,
            )
        except Exception:
            pass  # Already gone or never existed
