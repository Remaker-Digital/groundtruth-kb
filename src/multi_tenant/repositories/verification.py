"""
Verification token repository — short-lived tokens for email verification
and magic links.

Tokens are stored with Cosmos DB TTL so they auto-expire. The collection
uses ``token_type`` as partition key (e.g. "email_verification",
"magic_link") to separate token families.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from azure.cosmos.exceptions import (
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import (
    COLLECTION_VERIFICATION_TOKENS,
    TTL_VERIFICATION_TOKEN,
)

logger = logging.getLogger(__name__)


class VerificationTokenRepository:
    """Repository for the verification_tokens collection.

    Platform-scoped (not tenant-scoped). Partition key is ``token_type``.
    Documents auto-expire via Cosmos DB TTL.
    """

    def __init__(self) -> None:
        self._collection_name = COLLECTION_VERIFICATION_TOKENS

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def create_token(
        self,
        token_id: str,
        token_type: str,
        tenant_id: str,
        email: str,
        ttl: int = TTL_VERIFICATION_TOKEN,
        *,
        member_id: str | None = None,
        sign_in_code: str | None = None,
    ) -> dict[str, Any]:
        """Persist a verification token document.

        Args:
            token_id: Unique token identifier (URL-safe random string).
            token_type: Partition key value (e.g. "email_verification").
            tenant_id: Tenant this token belongs to.
            email: Email address being verified.
            ttl: Time-to-live in seconds (default: 10 minutes).
            member_id: Optional team member document ID. When present,
                the verification flow can carry member identity through
                to JWT issuance without an additional DB lookup.

        Returns:
            Created document dict.

        Raises:
            DocumentConflictError: If token_id already exists.
        """
        from datetime import datetime, timezone

        doc = {
            "id": token_id,
            "token_type": token_type,
            "tenant_id": tenant_id,
            "email": email,
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ttl": ttl,
        }
        if member_id is not None:
            doc["member_id"] = member_id
        if sign_in_code is not None:
            doc["sign_in_code"] = sign_in_code
        try:
            result = await self._container.create_item(body=doc)
            logger.info(
                "Verification token created: type=%s tenant=%s",
                token_type, tenant_id,
            )
            return result
        except CosmosResourceExistsError:
            logger.warning("Token conflict: id=%s", token_id)
            raise

    async def consume_token(
        self,
        token_id: str,
        token_type: str,
    ) -> dict[str, Any] | None:
        """Read and mark a token as used (single-use).

        Returns the token document if valid and unused, or None if
        the token does not exist, is already used, or has expired.
        Uses Cosmos DB patch to atomically set ``used=True``.
        """
        try:
            doc = await self._container.read_item(
                item=token_id,
                partition_key=token_type,
            )
        except CosmosResourceNotFoundError:
            return None

        if doc.get("used"):
            return None

        # Atomically mark as used
        try:
            await self._container.patch_item(
                item=token_id,
                partition_key=token_type,
                patch_operations=[
                    {"op": "set", "path": "/used", "value": True},
                ],
            )
        except Exception:
            logger.warning("Failed to mark token as used: id=%s", token_id)
            return None

        return doc

    async def consume_token_by_code(
        self,
        tenant_id: str,
        sign_in_code: str,
        token_type: str,
    ) -> dict[str, Any] | None:
        """Look up and consume a token by its 6-digit sign-in code.

        SPEC-0429: Alternative to link-based verification. Queries within
        the token_type partition for a matching tenant + code + unused token.
        Returns the token document if found and valid, or None.
        """
        try:
            query = (
                "SELECT * FROM c WHERE c.tenant_id = @tid "
                "AND c.sign_in_code = @code AND c.used = false"
            )
            params = [
                {"name": "@tid", "value": tenant_id},
                {"name": "@code", "value": sign_in_code},
            ]
            items = [
                item async for item in self._container.query_items(
                    query=query,
                    parameters=params,
                    partition_key=token_type,
                    max_item_count=1,
                )
            ]
        except Exception:
            logger.exception("Error querying token by code: tenant=%s", tenant_id)
            return None

        if not items:
            return None

        doc = items[0]
        if doc.get("used"):
            return None

        # Atomically mark as used
        try:
            await self._container.patch_item(
                item=doc["id"],
                partition_key=token_type,
                patch_operations=[
                    {"op": "set", "path": "/used", "value": True},
                ],
            )
        except Exception:
            logger.warning("Failed to mark token as used: id=%s", doc["id"])
            return None

        return doc

    async def delete_token(
        self,
        token_id: str,
        token_type: str,
    ) -> bool:
        """Delete a token document. Returns True if deleted."""
        try:
            await self._container.delete_item(
                item=token_id,
                partition_key=token_type,
            )
            return True
        except CosmosResourceNotFoundError:
            return False
