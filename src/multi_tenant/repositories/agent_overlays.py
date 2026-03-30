"""
Tenant Agent Overlay repository — agent_overlays collection (SPEC-1854, WI-4011).

Per-tenant, per-agent configuration overlays persisted in Cosmos DB.
Partition key: /tenant_id. Document ID: agent_id (unique per tenant).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_AGENT_OVERLAYS,
    TenantAgentOverlayDocument,
)
from src.multi_tenant.repositories.base import (
    DocumentNotFoundError,
    TenantScopedRepository,
)

logger = logging.getLogger(__name__)

# Allowed top-level keys in custom_metadata (Codex Finding 4: schema guardrails).
# Secret values MUST NOT be stored here — they live in Key Vault only.
_ALLOWED_CUSTOM_METADATA_KEYS = frozenset({
    "intent_routes",
})

# Valid keys inside an intent_routes route config entry.
# Maps intent name -> {agent_id|suggested_peer, skill_id|skill}
_INTENT_ROUTE_ALLOWED_KEYS = frozenset({
    "agent_id", "suggested_peer", "skill_id", "skill",
})


def _validate_intent_routes(
    value: Any, tenant_id: str, agent_id: str
) -> dict[str, dict[str, str]] | None:
    """Validate intent_routes shape: dict[str, dict[str, str]].

    Each entry maps an intent name to a route config with known keys.
    Unknown nested keys are stripped. Non-dict entries are rejected.
    Returns validated dict, or None if the entire value is malformed.
    """
    if not isinstance(value, dict):
        logger.warning(
            "Rejected intent_routes (not a dict) for tenant=%s agent=%s",
            tenant_id, agent_id,
        )
        return None

    validated: dict[str, dict[str, str]] = {}
    for intent_name, route_cfg in value.items():
        if not isinstance(intent_name, str):
            continue
        if not isinstance(route_cfg, dict):
            logger.warning(
                "Rejected intent_routes[%r] (not a dict) for tenant=%s agent=%s",
                intent_name, tenant_id, agent_id,
            )
            continue
        clean_cfg: dict[str, str] = {}
        for k, v in route_cfg.items():
            if k in _INTENT_ROUTE_ALLOWED_KEYS and isinstance(v, str):
                clean_cfg[k] = v
        if clean_cfg:
            validated[intent_name] = clean_cfg

    return validated


class TenantAgentOverlayRepository(TenantScopedRepository):
    """Repository for the agent_overlays collection.

    Tenant-scoped. Partition key is ``tenant_id``.
    Document ID is ``agent_id`` — one overlay per agent per tenant.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_AGENT_OVERLAYS)

    async def get_overlay(
        self, tenant_id: str, agent_id: str
    ) -> dict[str, Any] | None:
        """Read a single overlay by agent_id. Returns None if not found."""
        try:
            return await self.read(tenant_id, agent_id)
        except DocumentNotFoundError:
            return None

    async def upsert_overlay(
        self,
        tenant_id: str,
        agent_id: str,
        *,
        enabled: bool = True,
        prompt_overrides: dict[str, str] | None = None,
        skill_overrides: dict[str, Any] | None = None,
        custom_metadata: dict[str, Any] | None = None,
        visibility_scope: str = "public",
        staff_domain_tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create or replace an overlay for tenant + agent."""
        now = datetime.now(timezone.utc).isoformat()

        # Validate custom_metadata keys AND shapes (Codex Findings 4 + review P2)
        clean_metadata = {}
        if custom_metadata:
            for key, val in custom_metadata.items():
                if key not in _ALLOWED_CUSTOM_METADATA_KEYS:
                    logger.warning(
                        "Rejected custom_metadata key %r for tenant=%s agent=%s",
                        key, tenant_id, agent_id,
                    )
                    continue
                if key == "intent_routes":
                    validated = _validate_intent_routes(val, tenant_id, agent_id)
                    if validated is not None:
                        clean_metadata[key] = validated
                else:
                    clean_metadata[key] = val

        doc = TenantAgentOverlayDocument(
            id=agent_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            enabled=enabled,
            prompt_overrides=prompt_overrides or {},
            skill_overrides=skill_overrides or {},
            custom_metadata=clean_metadata,
            visibility_scope=visibility_scope,
            staff_domain_tags=staff_domain_tags or [],
            created_at=now,
            updated_at=now,
        )
        return await self.upsert(tenant_id, doc)

    async def delete_overlay(
        self, tenant_id: str, agent_id: str
    ) -> bool:
        """Delete an overlay. Returns True if it existed."""
        try:
            await self.delete(tenant_id, agent_id)
            return True
        except DocumentNotFoundError:
            return False

    async def list_overlays(
        self, tenant_id: str
    ) -> list[dict[str, Any]]:
        """List all overlays for a tenant (single-partition query)."""
        return await self.query(
            tenant_id,
            "SELECT * FROM c ORDER BY c.agent_id ASC",
            [],
        )

    async def list_enabled_agent_ids(
        self, tenant_id: str
    ) -> list[str]:
        """Return agent_ids with enabled overlays for a tenant."""
        results = await self.query(
            tenant_id,
            "SELECT c.agent_id FROM c WHERE c.enabled = true",
            [],
        )
        return [r["agent_id"] for r in results]
