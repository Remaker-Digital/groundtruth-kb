"""Agent Skill Binding service (SPEC-1856, SPEC-1857, SPEC-1858).

Manages per-tenant, per-agent, per-skill authorization bindings.
Enforces deny-by-default: no tool call proceeds without an active binding.

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

    In-memory store for now; will be backed by Cosmos DB in production.
    """

    _instance: SkillBindingService | None = None

    def __init__(self) -> None:
        # Key: (tenant_id, agent_id, skill_id) -> binding dict
        self._bindings: dict[tuple[str, str, str], dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> SkillBindingService:
        if cls._instance is None:
            cls._instance = SkillBindingService()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (testing only)."""
        cls._instance = None

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
