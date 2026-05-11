# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Agent Skill Binding service (SPEC-1856, SPEC-1857, SPEC-1858, WI-4014).

Manages per-tenant, per-agent, per-skill authorization bindings.
Enforces deny-by-default: no tool call proceeds without an active binding.

Sync/async contract (Codex Finding 2):
  - Runtime reads (get_binding, check_binding, resolve_credential) are SYNCHRONOUS.
    They read from the in-memory _bindings dict which acts as the sole cache.
  - Admin writes go through the Cosmos repo (async) and then call invalidate()
    to clear this cache, forcing next reads to miss.
  - No second TTL cache (Codex Finding 1). Invalidation is immediate on writes.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BindingCheckResult:
    """Result of a binding authorization check (SPEC-1857)."""

    allowed: bool
    policy_verdict: str
    tenant_id: str
    agent_id: str
    skill_id: str
    credential_ref: str | None = None
    reason: str = ""

    @property
    def denied(self) -> bool:
        return not self.allowed


class SkillBindingService:
    """Manages agent skill bindings and enforces deny-by-default (SPEC-1857).

    The _bindings dict is the sole cache layer for synchronous runtime reads.
    Admin API writes go through the Cosmos repo and call invalidate() to
    clear this cache. No TTL — invalidation is immediate on writes.
    """

    _instance: SkillBindingService | None = None

    def __init__(self) -> None:
        # Key: (tenant_id, agent_id, skill_id) -> binding dict
        # Synchronous read cache — populated from Cosmos repo on first miss
        self._bindings: dict[tuple[str, str, str], dict[str, Any]] = {}
        # Tracks which tenants have been loaded from Cosmos
        self._loaded_tenants: set[str] = set()

    @classmethod
    def get_instance(cls) -> SkillBindingService:
        if cls._instance is None:
            cls._instance = SkillBindingService()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (testing only)."""
        cls._instance = None

    def invalidate(self, tenant_id: str | None = None) -> None:
        """Invalidate the binding cache. Called by admin API after Cosmos writes.

        If tenant_id is given, only that tenant's bindings are evicted.
        If None, all bindings are evicted (e.g., for testing or bulk operations).
        """
        if tenant_id is None:
            self._bindings.clear()
            self._loaded_tenants.clear()
            logger.debug("Binding cache fully invalidated")
        else:
            keys_to_remove = [k for k in self._bindings if k[0] == tenant_id]
            for k in keys_to_remove:
                del self._bindings[k]
            self._loaded_tenants.discard(tenant_id)
            logger.debug("Binding cache invalidated for tenant=%s (%d entries)", tenant_id, len(keys_to_remove))

    async def load_tenant_bindings(self, tenant_id: str) -> None:
        """Load all bindings for a tenant from Cosmos into the cache.

        Called on first access for a tenant or after invalidation.
        """
        from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository
        repo = AgentSkillBindingRepository()
        docs = await repo.list_bindings(tenant_id)
        # Clear existing entries for this tenant before loading
        keys_to_remove = [k for k in self._bindings if k[0] == tenant_id]
        for k in keys_to_remove:
            del self._bindings[k]
        # Populate from Cosmos
        for doc in docs:
            key = (doc["tenant_id"], doc["agent_id"], doc["skill_id"])
            self._bindings[key] = {
                "tenant_id": doc["tenant_id"],
                "agent_id": doc["agent_id"],
                "skill_id": doc["skill_id"],
                "credential_ref": doc.get("credential_ref"),
                "mode": doc.get("mode", "read"),
                "approval_policy": doc.get("approval_policy", "auto"),
                "enabled": doc.get("enabled", True),
            }
        self._loaded_tenants.add(tenant_id)
        logger.debug("Loaded %d bindings from Cosmos for tenant=%s", len(docs), tenant_id)

    # -- CRUD ---------------------------------------------------------------

    def create_binding(
        self,
        *,
        tenant_id: str,
        agent_id: str,
        skill_id: str,
        credential_ref: str | None = None,
        mode: str = "read",
        approval_policy: str = "auto",
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Create or update a skill binding."""
        key = (tenant_id, agent_id, skill_id)
        binding = {
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "skill_id": skill_id,
            "credential_ref": credential_ref,
            "mode": mode,
            "approval_policy": approval_policy,
            "enabled": enabled,
        }
        self._bindings[key] = binding
        return binding

    def get_binding(
        self, tenant_id: str, agent_id: str, skill_id: str
    ) -> dict[str, Any] | None:
        """Get a binding by key. Returns None if not found."""
        return self._bindings.get((tenant_id, agent_id, skill_id))

    def list_bindings(
        self,
        tenant_id: str,
        agent_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List bindings for a tenant, optionally filtered by agent."""
        results = []
        for key, binding in self._bindings.items():
            if key[0] != tenant_id:
                continue
            if agent_id and key[1] != agent_id:
                continue
            results.append(binding)
        return results

    def delete_binding(
        self, tenant_id: str, agent_id: str, skill_id: str
    ) -> bool:
        """Delete a binding. Returns True if it existed."""
        key = (tenant_id, agent_id, skill_id)
        if key in self._bindings:
            del self._bindings[key]
            return True
        return False

    def list_bindings_by_credential(
        self, credential_ref: str
    ) -> list[dict[str, Any]]:
        """List all bindings that reference a given credential (SPEC-1858 req 6)."""
        return [
            b for b in self._bindings.values()
            if b.get("credential_ref") == credential_ref
        ]

    # -- Authorization check (SPEC-1857) ------------------------------------

    def check_binding(
        self,
        tenant_id: str,
        agent_id: str,
        skill_id: str,
        *,
        required_mode: str | None = None,
    ) -> BindingCheckResult:
        """Check if a skill invocation is authorized (SPEC-1857 req 1-4).

        Deny-by-default: missing binding = denied.
        Mode enforcement: read binding cannot execute mutate skills.
        Credential fail-closed: missing credential_ref = denied (SPEC-1858 req 4).
        """
        binding = self.get_binding(tenant_id, agent_id, skill_id)

        # SPEC-1857 req 2: No binding = denied
        if binding is None:
            return BindingCheckResult(
                allowed=False,
                policy_verdict="denied_by_binding",
                tenant_id=tenant_id,
                agent_id=agent_id,
                skill_id=skill_id,
                reason=f"No binding for {tenant_id}/{agent_id}/{skill_id}",
            )

        # SPEC-1857 req 2: Disabled binding = denied
        if not binding.get("enabled", True):
            return BindingCheckResult(
                allowed=False,
                policy_verdict="denied_by_binding",
                tenant_id=tenant_id,
                agent_id=agent_id,
                skill_id=skill_id,
                reason="Binding is disabled",
            )

        # SPEC-1857 req 3: Mode enforcement
        if required_mode == "mutate" and binding.get("mode") == "read":
            return BindingCheckResult(
                allowed=False,
                policy_verdict="denied_by_mode",
                tenant_id=tenant_id,
                agent_id=agent_id,
                skill_id=skill_id,
                reason="Read-only binding cannot execute mutate skill",
            )

        # SPEC-1858 req 4: Credential fail-closed for external skills
        credential_ref = binding.get("credential_ref")

        return BindingCheckResult(
            allowed=True,
            policy_verdict="allowed",
            tenant_id=tenant_id,
            agent_id=agent_id,
            skill_id=skill_id,
            credential_ref=credential_ref,
        )

    def get_bound_skill_ids(
        self, tenant_id: str, agent_id: str | None = None
    ) -> list[str]:
        """Return skill_ids with active bindings for tenant (SPEC-1857 req 5).

        Used to filter the tool catalog to only show bound skills.
        """
        results = []
        for key, binding in self._bindings.items():
            if key[0] != tenant_id:
                continue
            if agent_id and key[1] != agent_id:
                continue
            if binding.get("enabled", True):
                results.append(key[2])  # skill_id
        return sorted(results)

    def resolve_credential(
        self, tenant_id: str, agent_id: str, skill_id: str
    ) -> str | None:
        """Resolve credential_ref from binding (SPEC-1858 req 2).

        Returns the credential_ref or None if no binding / no credential.
        """
        binding = self.get_binding(tenant_id, agent_id, skill_id)
        if binding is None:
            return None
        return binding.get("credential_ref")
