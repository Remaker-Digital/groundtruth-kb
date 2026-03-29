"""
Agent Skill Binding repository — agent_bindings collection (SPEC-1856, WI-4012).

Per-tenant, per-skill authorization bindings persisted in Cosmos DB.
Partition key: /tenant_id. Document ID: skill_id (unique per tenant partition,
per Codex Finding 3 — skill_id already embeds agent identity).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_AGENT_BINDINGS,
    AgentSkillBindingDocument,
)
from src.multi_tenant.repositories.base import (
    DocumentNotFoundError,
    TenantScopedRepository,
)

logger = logging.getLogger(__name__)


class AgentSkillBindingRepository(TenantScopedRepository):
    """Repository for the agent_bindings collection.

    Tenant-scoped. Partition key is ``tenant_id``.
    Document ID is ``skill_id`` — one binding per skill per tenant.
    ``agent_id`` is stored as a separate field for query/filter convenience.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_AGENT_BINDINGS)

    async def get_binding(
        self, tenant_id: str, skill_id: str
    ) -> dict[str, Any] | None:
        """Read a single binding by skill_id. Returns None if not found."""
        try:
            return await self.read(tenant_id, skill_id)
        except DocumentNotFoundError:
            return None

    async def upsert_binding(
        self,
        tenant_id: str,
        agent_id: str,
        skill_id: str,
        *,
        credential_ref: str | None = None,
        mode: str = "read",
        approval_policy: str = "auto",
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Create or replace a skill binding."""
        now = datetime.now(timezone.utc).isoformat()
        doc = AgentSkillBindingDocument(
            id=skill_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            skill_id=skill_id,
            credential_ref=credential_ref,
            mode=mode,
            approval_policy=approval_policy,
            enabled=enabled,
            created_at=now,
            updated_at=now,
        )
        return await self.upsert(tenant_id, doc)

    async def delete_binding(
        self, tenant_id: str, skill_id: str
    ) -> bool:
        """Delete a binding. Returns True if it existed."""
        try:
            await self.delete(tenant_id, skill_id)
            return True
        except DocumentNotFoundError:
            return False

    async def list_bindings(
        self,
        tenant_id: str,
        *,
        agent_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List bindings for a tenant, optionally filtered by agent."""
        if agent_id:
            return await self.query(
                tenant_id,
                "SELECT * FROM c WHERE c.agent_id = @agent_id ORDER BY c.skill_id ASC",
                [{"name": "@agent_id", "value": agent_id}],
            )
        return await self.query(
            tenant_id,
            "SELECT * FROM c ORDER BY c.skill_id ASC",
            [],
        )

    async def list_enabled_skill_ids(
        self,
        tenant_id: str,
        *,
        agent_id: str | None = None,
    ) -> list[str]:
        """Return skill_ids with active bindings (enabled=true)."""
        if agent_id:
            results = await self.query(
                tenant_id,
                "SELECT c.skill_id FROM c WHERE c.enabled = true AND c.agent_id = @agent_id",
                [{"name": "@agent_id", "value": agent_id}],
            )
        else:
            results = await self.query(
                tenant_id,
                "SELECT c.skill_id FROM c WHERE c.enabled = true",
                [],
            )
        return sorted(r["skill_id"] for r in results)

    async def list_by_credential(
        self, credential_ref: str
    ) -> list[dict[str, Any]]:
        """List all bindings referencing a credential (cross-partition audit path).

        This is the only cross-partition query in this repository — used for
        credential audit/rotation (SPEC-1858 req 6).
        """
        return await self.cross_partition_query(
            "SELECT * FROM c WHERE c.credential_ref = @cred",
            [{"name": "@cred", "value": credential_ref}],
        )
