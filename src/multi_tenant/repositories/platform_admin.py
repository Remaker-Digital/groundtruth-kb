"""Repository for the platform_admins collection (SPEC-1667).

Stores Service Provider Administrator credentials, completely isolated
from all tenant team_members collections. The SPA has zero permissions
within any tenancy and does not exist as a user for any tenancy.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from src.multi_tenant.cosmos_schema import COLLECTION_PLATFORM_ADMINS
from src.multi_tenant.repositories.platform import PlatformScopedRepository

logger = logging.getLogger(__name__)


class PlatformAdminRepository(PlatformScopedRepository):
    """Repository for the platform_admins collection.

    Stores Service Provider Administrator credentials, completely
    isolated from all tenant team_members collections. This is a
    very small collection (1-5 records) so cross-partition scans
    are trivial.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_PLATFORM_ADMINS)

    async def find_by_api_key_hash(
        self, key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a platform admin by API key hash.

        Used at authentication time to resolve an ar_spa_* key to
        a platform admin document.

        Args:
            key_hash: SHA-256 hex digest of the SPA API key.

        Returns:
            Platform admin document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c "
                "WHERE c.api_key_hash = @key_hash "
                "AND c.is_active = true"
            ),
            parameters=[{"name": "@key_hash", "value": key_hash}],
            enable_cross_partition_query=True,
        ):
            items.append(item)
            if len(items) >= 1:
                break
        return items[0] if items else None

    async def find_by_email(
        self, email: str,
    ) -> dict[str, Any] | None:
        """Find a platform admin by email address."""
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.email = @email",
            parameters=[{"name": "@email", "value": email}],
            enable_cross_partition_query=True,
        ):
            items.append(item)
            if len(items) >= 1:
                break
        return items[0] if items else None

    async def create_admin(
        self, document: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new platform admin document.

        Args:
            document: Platform admin document with admin_id, email,
                api_key_hash, display_name, is_active, etc.

        Returns:
            Created document (with Cosmos _rid, _etag, etc.).
        """
        return await self._container.create_item(body=document)

    async def list_admins(self) -> list[dict[str, Any]]:
        """List all platform admins (cross-partition, small collection)."""
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.is_active = true",
            enable_cross_partition_query=True,
        ):
            items.append(item)
        return items
