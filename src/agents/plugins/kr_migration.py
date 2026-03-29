"""KR MCP migration to binding system (SPEC-1860).

Migrates the current Knowledge Retrieval MCP tool path from
tenant-global mcp_servers config to the agent skill binding system.

Migration is idempotent (SPEC-1860 req 3) and preserves behavior
for existing tenants (SPEC-1860 req 4).

Migration state contract (Codex P1 finding):
  legacy_only      — tenant uses global KR path only
  dual_read        — binding exists, legacy fallback permitted
  binding_enforced — binding required, legacy path blocked

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# KR agent identity in the registry
KR_AGENT_ID = "knowledge-retrieval"
KR_SKILL_ID = "knowledge-retrieval:retrieve-knowledge"


class MigrationState(str, Enum):
    """Explicit migration state for a tenant's KR path (SPEC-1860).

    legacy_only      — no binding, uses global mcp_servers config
    dual_read        — binding exists, legacy fallback still allowed
    binding_enforced — binding is required, legacy path is blocked
    """

    LEGACY_ONLY = "legacy_only"
    DUAL_READ = "dual_read"
    BINDING_ENFORCED = "binding_enforced"


# In-memory migration state store (Cosmos repo deferred to Phase 2)
_migration_states: dict[str, MigrationState] = {}


def get_migration_state(tenant_id: str) -> MigrationState:
    """Get the current migration state for a tenant.

    Defaults to LEGACY_ONLY if no state has been set.
    """
    return _migration_states.get(tenant_id, MigrationState.LEGACY_ONLY)


def set_migration_state(tenant_id: str, state: MigrationState) -> None:
    """Set the migration state for a tenant.

    Typically called by:
      - migrate_tenant_kr_bindings() -> sets DUAL_READ
      - Admin API -> can promote to BINDING_ENFORCED
    """
    _migration_states[tenant_id] = state
    logger.info(
        "Migration state for tenant %s set to %s", tenant_id, state.value
    )


def reset_migration_states() -> None:
    """Clear all migration states (testing only)."""
    _migration_states.clear()


def migrate_tenant_kr_bindings(
    tenant_id: str,
    mcp_servers: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Create bindings for a tenant's existing KR MCP configuration (SPEC-1860 req 2).

    Idempotent: re-running does not create duplicates.
    Sets migration state to DUAL_READ (not BINDING_ENFORCED — that
    requires explicit admin action).
    Returns list of bindings created or already existing.
    """
    from src.agents.plugins.bindings import SkillBindingService

    svc = SkillBindingService.get_instance()
    results: list[dict[str, Any]] = []

    # Always create the base KR skill binding
    existing = svc.get_binding(tenant_id, KR_AGENT_ID, KR_SKILL_ID)
    if existing is None:
        binding = svc.create_binding(
            tenant_id=tenant_id,
            agent_id=KR_AGENT_ID,
            skill_id=KR_SKILL_ID,
            mode="read",
            approval_policy="auto",
            enabled=True,
        )
        results.append(binding)
        logger.info("Created KR binding for tenant %s", tenant_id)
    else:
        results.append(existing)

    # If tenant has MCP server configs, create bindings for each
    # MCP tool mapped to the KR agent's skill set
    if mcp_servers:
        for server_cfg in mcp_servers:
            tools = server_cfg.get("tools", [])
            credential_ref = server_cfg.get("credential_ref")

            for tool_name in tools:
                # Map MCP tool to skill_id format
                skill_id = f"{KR_AGENT_ID}:{_tool_to_skill_name(tool_name)}"
                existing = svc.get_binding(tenant_id, KR_AGENT_ID, skill_id)
                if existing is None:
                    binding = svc.create_binding(
                        tenant_id=tenant_id,
                        agent_id=KR_AGENT_ID,
                        skill_id=skill_id,
                        credential_ref=credential_ref,
                        mode="read",
                        approval_policy="auto",
                        enabled=True,
                    )
                    results.append(binding)
                else:
                    results.append(existing)

    # Promote to dual_read (idempotent — won't downgrade binding_enforced)
    current = get_migration_state(tenant_id)
    if current == MigrationState.LEGACY_ONLY:
        set_migration_state(tenant_id, MigrationState.DUAL_READ)

    return results


def is_tenant_migrated(tenant_id: str) -> bool:
    """Check if a tenant has been migrated to the binding system (SPEC-1860 req 5).

    Returns True if migration state is DUAL_READ or BINDING_ENFORCED.
    """
    state = get_migration_state(tenant_id)
    return state in (MigrationState.DUAL_READ, MigrationState.BINDING_ENFORCED)


def _mcp_configs_from_binding(binding: dict[str, Any]) -> list[dict[str, Any]]:
    """Build MCP configs from a binding's credential_ref (SPEC-1860).

    When a tenant is binding-sourced, MCP configs derive from the
    binding rather than from legacy preferences.mcp_servers.
    """
    credential_ref = binding.get("credential_ref")
    if not credential_ref:
        return []
    return [{
        "server_type": "binding",
        "credential_ref": credential_ref,
        "skill_id": binding.get("skill_id", KR_SKILL_ID),
        "agent_id": binding.get("agent_id", KR_AGENT_ID),
    }]


def resolve_kr_with_fallback(
    tenant_id: str,
    mcp_configs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Resolve KR config through bindings with fallback (SPEC-1860 req 5).

    Returns a dict with:
      - "source": "binding", "legacy", or "error"
      - "mcp_configs": resolved configs to pass to KR agent

    When source is "binding", mcp_configs are derived from the binding's
    credential_ref — NOT passed through from legacy resolve_mcp_configs().
    When source is "legacy", mcp_configs are the caller-provided legacy configs.
    """
    state = get_migration_state(tenant_id)

    if state == MigrationState.BINDING_ENFORCED:
        # Must use binding — no legacy fallback, no legacy config passthrough
        from src.agents.plugins.bindings import SkillBindingService
        svc = SkillBindingService.get_instance()
        binding = svc.get_binding(tenant_id, KR_AGENT_ID, KR_SKILL_ID)
        if binding is None:
            logger.error(
                "Tenant %s is binding_enforced but has no KR binding", tenant_id
            )
            return {
                "source": "error",
                "error": "binding_enforced but no KR binding exists",
                "mcp_configs": [],
            }
        return {
            "source": "binding",
            "binding": binding,
            "mcp_configs": _mcp_configs_from_binding(binding),
        }

    if state == MigrationState.DUAL_READ:
        # Try binding first, fall back to legacy
        from src.agents.plugins.bindings import SkillBindingService
        svc = SkillBindingService.get_instance()
        binding = svc.get_binding(tenant_id, KR_AGENT_ID, KR_SKILL_ID)
        if binding is not None:
            return {
                "source": "binding",
                "binding": binding,
                "mcp_configs": _mcp_configs_from_binding(binding),
            }
        # Fall through to legacy with audit event
        _emit_legacy_audit(tenant_id, "dual_read_fallback")
        return {
            "source": "legacy",
            "mcp_configs": mcp_configs,
        }

    # LEGACY_ONLY — straight to legacy with audit event
    _emit_legacy_audit(tenant_id, "legacy_only")
    return {
        "source": "legacy",
        "mcp_configs": mcp_configs,
    }


def _emit_legacy_audit(tenant_id: str, reason: str) -> None:
    """Emit an audit event whenever the legacy KR path is used."""
    try:
        from src.agents.plugins.events import emit_invocation
        emit_invocation(
            trace_id="",
            target_agent_id=KR_AGENT_ID,
            skill_id=KR_SKILL_ID,
            tenant_id=tenant_id,
            conversation_id="",
            result_class="legacy_fallback",
            policy_verdict=reason,
        )
    except Exception:
        logger.debug("Failed to emit legacy audit event", exc_info=True)


def _tool_to_skill_name(tool_name: str) -> str:
    """Convert an MCP tool name to a skill_name component.

    e.g. "search_knowledge" -> "search-knowledge"
    """
    return tool_name.replace("_", "-").replace(".", "-").lower()
