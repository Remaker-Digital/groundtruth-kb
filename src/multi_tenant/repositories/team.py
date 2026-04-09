"""
Team member repository — team_members collection (admin dashboard access).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.multi_tenant.cosmos_schema import COLLECTION_TEAM_MEMBERS
from src.multi_tenant.repositories.base import TenantScopedRepository


class TeamMemberRepository(TenantScopedRepository):
    """Repository for the team_members collection.

    Manages merchant team members who access the admin dashboard
    and/or handle escalated conversations.
    """

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    # Per architecture plan section 4.1.3: team member PII
    _encryption_fields = frozenset({
        "email", "display_name",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_TEAM_MEMBERS)

    async def list_members(
        self,
        tenant_id: str,
        *,
        role: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List team members with optional filtering.

        Args:
            tenant_id: Tenant partition key.
            role: Filter by role (owner, admin, agent, viewer).
            is_active: Filter by active status (None = all).
            offset: Pagination offset.
            limit: Page size.
        """
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if role is not None:
            conditions.append("c.role = @role")
            params.append({"name": "@role", "value": role})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.updated_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_members(
        self,
        tenant_id: str,
        *,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count team members matching filters (for pagination)."""
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if role is not None:
            conditions.append("c.role = @role")
            params.append({"name": "@role", "value": role})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def find_by_email(
        self, tenant_id: str, email: str,
    ) -> dict[str, Any] | None:
        """Find a team member by email address (unique within tenant)."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.email = @email",
            parameters=[{"name": "@email", "value": email}],
            max_items=1,
        )
        return results[0] if results else None

    async def deactivate(
        self, tenant_id: str, document_id: str,
    ) -> dict[str, Any]:
        """Deactivate a team member (set is_active = false)."""
        now = datetime.now(UTC).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=document_id,
            operations=[
                {"op": "set", "path": "/is_active", "value": False},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    async def list_active_agents(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List active team members with the escalation_agent role.

        Used for escalation routing — returns agents who can handle
        escalated conversations.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.role IN ('agent', 'escalation_agent') AND c.is_active = true "
                "ORDER BY c.max_concurrent_conversations DESC"
            ),
        )

    async def find_all_by_email(
        self, email: str,
    ) -> list[dict[str, Any]]:
        """Find all active team members matching an email across all tenants.

        Cross-partition query used at magic link request time when the
        tenant is not yet known. Returns all matching active members
        (one email can appear in multiple tenants).

        Args:
            email: Email address to search (should be pre-normalized to
                lowercase).

        Returns:
            List of team member documents (may be empty).
        """
        return await self.cross_partition_query(
            query_text=(
                "SELECT * FROM c "
                "WHERE c.email = @email "
                "AND c.is_active = true"
            ),
            parameters=[{"name": "@email", "value": email}],
        )

    async def verify_user_key_hash(
        self, tenant_id: str, key_hash: str,
    ) -> dict[str, Any] | None:
        """Verify a per-user API key hash within a known tenant (partition-scoped).

        SPEC-1644: API keys authenticate users, they do NOT identify tenants.
        The tenant_id must be known in advance (from the URL).  This queries
        only within the specified tenant's partition — no cross-partition
        lookup is ever performed.

        Args:
            tenant_id: The tenant to validate against (from URL).
            key_hash: SHA-256 hex digest of the per-user API key.

        Returns:
            The team member document if the hash matches, None otherwise.
        """
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.user_api_key_hash = @key_hash "
                "AND c.is_active = true"
            ),
            parameters=[{"name": "@key_hash", "value": key_hash}],
            max_items=1,
        )
        return results[0] if results else None

    async def update_member_fields(
        self,
        tenant_id: str,
        member_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update arbitrary fields on a team member document.

        Builds Cosmos DB patch operations from the updates dict and
        always sets ``updated_at`` to the current UTC timestamp.

        Args:
            tenant_id: Tenant partition key.
            member_id: Team member document ID.
            updates: Dict of field names → new values. Values of ``None``
                are stored as JSON null (for clearing fields).
        """
        now = datetime.now(UTC).isoformat()
        operations: list[dict[str, Any]] = [
            {"op": "set", "path": f"/{key}", "value": value}
            for key, value in updates.items()
        ]
        operations.append({"op": "set", "path": "/updated_at", "value": now})
        return await self.patch(
            tenant_id=tenant_id,
            document_id=member_id,
            operations=operations,
        )

    async def list_agents_for_category(
        self, tenant_id: str, category: str,
    ) -> list[dict[str, Any]]:
        """List active escalation agents assigned to a specific category.

        Used for escalation email routing — returns agents whose
        escalation_categories list contains the given category.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.role IN ('agent', 'escalation_agent') "
                "AND c.is_active = true "
                "AND ARRAY_CONTAINS(c.escalation_categories, @category)"
            ),
            parameters=[{"name": "@category", "value": category}],
        )
