# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
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
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
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

    async def update_api_key_hash(
        self, admin_id: str, new_key_hash: str, updated_at: str,
    ) -> dict[str, Any]:
        """Replace the API key hash for a platform admin (SPEC-1669).

        Reads the current document, updates the api_key_hash and
        updated_at fields, then replaces the document in Cosmos DB.
        The previous key is immediately invalidated because the hash
        no longer matches.

        Args:
            admin_id: Platform admin document ID (also partition key).
            new_key_hash: SHA-256 hex digest of the new SPA API key.
            updated_at: ISO 8601 timestamp of the key regeneration.

        Returns:
            Updated document (with new _etag).

        Raises:
            CosmosResourceNotFoundError: If no admin with this ID exists.
        """
        # Read current document
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )

        # Replace the key hash — the old key is immediately invalid
        doc["api_key_hash"] = new_key_hash
        doc["updated_at"] = updated_at
        doc["key_regenerated_at"] = updated_at

        return await self._container.upsert_item(body=doc)

    async def list_admins(self) -> list[dict[str, Any]]:
        """List all platform admins (cross-partition, small collection)."""
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.is_active = true",
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
        ):
            items.append(item)
        return items

    # ----- SPEC-1675: User hierarchy methods -----

    async def find_by_admin_id(
        self, admin_id: str,
    ) -> dict[str, Any] | None:
        """Read a platform admin by document ID (partition key)."""
        try:
            return await self._container.read_item(
                item=admin_id,
                partition_key=admin_id,
            )
        except Exception:
            return None

    async def deactivate_admin(
        self, admin_id: str, updated_at: str,
    ) -> dict[str, Any]:
        """Deactivate a platform admin (set is_active=false)."""
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )
        doc["is_active"] = False
        doc["updated_at"] = updated_at
        doc["deactivated_at"] = updated_at
        return await self._container.upsert_item(body=doc)

    async def update_notification_email(
        self, admin_id: str, email: str | None, updated_at: str,
    ) -> dict[str, Any]:
        """Set or clear the notification email address (SPEC-1676)."""
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )
        doc["notification_email_address"] = email
        doc["updated_at"] = updated_at
        return await self._container.upsert_item(body=doc)

    async def update_backup_code_hashes(
        self, admin_id: str,
        hashes: list[str], count: int, updated_at: str,
    ) -> dict[str, Any]:
        """Replace all backup recovery code hashes (SPEC-1678)."""
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )
        doc["backup_recovery_code_hashes"] = hashes
        doc["backup_codes_remaining"] = count
        doc["updated_at"] = updated_at
        return await self._container.upsert_item(body=doc)

    async def consume_backup_code(
        self, admin_id: str,
        remaining_hashes: list[str], new_count: int, updated_at: str,
    ) -> dict[str, Any]:
        """Remove a used backup code hash and decrement the counter."""
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )
        doc["backup_recovery_code_hashes"] = remaining_hashes
        doc["backup_codes_remaining"] = new_count
        doc["updated_at"] = updated_at
        return await self._container.upsert_item(body=doc)

    async def update_last_login(
        self, admin_id: str, timestamp: str,
    ) -> dict[str, Any]:
        """Record last login time for an admin."""
        doc = await self._container.read_item(
            item=admin_id,
            partition_key=admin_id,
        )
        doc["last_login_at"] = timestamp
        return await self._container.upsert_item(body=doc)
