"""Tenant Agent Overlay resolution (SPEC-1854, SPEC-1859).

Computes effective agent/skill configuration by merging the base
registry definition with per-tenant overlays and skill bindings.

Three-layer resolution order (SPEC-1859 req 1):
  base_registry -> tenant_overlay -> skill_binding

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from src.agents.plugins.registry import (
    PluginAgentDefinition,
    PluginAgentRegistry,
    SkillDefinition,
)

logger = logging.getLogger(__name__)

# Default resolution cache TTL in seconds (SPEC-1859 req 5)
_DEFAULT_CACHE_TTL = 60.0

# prompt_overrides is reserved for Phase 2 (IntentRouter).
# The field is accepted and stored but NOT consumed by SystemPromptBuilder
# until a prompt-resolution contract is specified.
_PROMPT_OVERRIDES_PHASE = 2


@dataclass
class EffectiveSkillConfig:
    """Resolved skill configuration for a specific tenant + agent + skill."""

    skill_id: str
    agent_id: str
    skill_name: str
    display_name: str
    description: str
    mode: str
    mcp_tool_names: tuple[str, ...]
    credential_types: tuple[str, ...]
    enabled: bool
    credential_ref: str | None = None


@dataclass
class EffectiveAgentConfig:
    """Resolved agent configuration for a specific tenant + agent."""

    agent_id: str
    display_name: str
    description: str
    agent_kind: str
    category: str
    endpoint: str
    tier_gate: str
    enabled: bool
    prompt_overrides: dict[str, str]
    skills: list[EffectiveSkillConfig]
    custom_metadata: dict[str, Any]


def resolve_effective_config(
    agent_defn: PluginAgentDefinition,
    overlay: dict[str, Any] | None = None,
) -> EffectiveAgentConfig:
    """Compute effective agent config by merging base with tenant overlay (SPEC-1854 req 3).

    If no overlay exists, base registry defaults apply (SPEC-1854 req 4).
    Unknown agent_ids in overlays are ignored at the caller level (SPEC-1854 req 3).
    """
    skill_overrides = {}
    prompt_overrides: dict[str, str] = {}
    custom_metadata: dict[str, Any] = {}
    enabled = True

    if overlay:
        enabled = overlay.get("enabled", True)
        prompt_overrides = overlay.get("prompt_overrides", {})
        custom_metadata = overlay.get("custom_metadata", {})
        raw_skill_overrides = overlay.get("skill_overrides", {})
        for sid, so in raw_skill_overrides.items():
            if isinstance(so, dict):
                skill_overrides[sid] = so

    # Build effective skills
    effective_skills: list[EffectiveSkillConfig] = []
    for skill in agent_defn.skills:
        so = skill_overrides.get(skill.skill_id, {})
        effective_skills.append(EffectiveSkillConfig(
            skill_id=skill.skill_id,
            agent_id=skill.agent_id,
            skill_name=skill.skill_name,
            display_name=skill.display_name,
            description=skill.description,
            mode=so.get("mode_override") or skill.mode,
            mcp_tool_names=skill.mcp_tool_names,
            credential_types=skill.credential_types,
            enabled=so.get("enabled", skill.enabled),
            credential_ref=so.get("credential_ref"),
        ))

    return EffectiveAgentConfig(
        agent_id=agent_defn.agent_id,
        display_name=agent_defn.display_name,
        description=agent_defn.description,
        agent_kind=agent_defn.agent_kind,
        category=agent_defn.category,
        endpoint=agent_defn.endpoint,
        tier_gate=agent_defn.tier_gate,
        enabled=enabled,
        prompt_overrides=prompt_overrides,
        skills=effective_skills,
        custom_metadata=custom_metadata,
    )


def resolve_for_tenant(
    tenant_id: str,
    agent_id: str,
    overlay_store: dict[str, dict[str, Any]] | None = None,
) -> EffectiveAgentConfig | None:
    """Resolve effective config for a (tenant_id, agent_id) pair.

    overlay_store maps agent_id -> overlay dict.
    Returns None if the agent_id is not in the base registry.
    """
    registry = PluginAgentRegistry.get_instance()
    agent_defn = registry.get(agent_id)
    if agent_defn is None:
        return None

    overlay = (overlay_store or {}).get(agent_id)
    return resolve_effective_config(agent_defn, overlay)


# ---------------------------------------------------------------------------
# Effective Skill Resolution (SPEC-1859)
# ---------------------------------------------------------------------------


@dataclass
class ResolvedSkill:
    """Full three-layer resolved skill (SPEC-1859 req 4)."""

    agent_id: str
    skill_id: str
    mode: str
    credential_ref: str | None
    approval_policy: str
    prompt_overrides: dict[str, str]
    mcp_tool_names: tuple[str, ...]
    enabled: bool
    display_name: str = ""
    description: str = ""


@dataclass
class SkillDenial:
    """Reason a skill resolution was denied."""

    reason: str
    agent_id: str
    skill_id: str


# Resolution cache: (tenant_id, agent_id, skill_id) -> (result, expiry)
_resolution_cache: dict[tuple[str, str, str], tuple[ResolvedSkill | SkillDenial, float]] = {}


def clear_resolution_cache() -> None:
    """Clear the resolution cache (testing / config reload)."""
    _resolution_cache.clear()


def resolve_skill(
    tenant_id: str,
    agent_id: str,
    skill_id: str,
    *,
    overlay_store: dict[str, dict[str, Any]] | None = None,
    cache_ttl: float = _DEFAULT_CACHE_TTL,
) -> ResolvedSkill | SkillDenial:
    """Three-layer effective resolution (SPEC-1859 req 1-6).

    Resolution order: base_registry -> tenant_overlay -> skill_binding.
    Returns ResolvedSkill if invocable, SkillDenial with reason if not.
    Results are cached with configurable TTL (SPEC-1859 req 5).
    """
    cache_key = (tenant_id, agent_id, skill_id)
    now = time.monotonic()

    # Check cache
    if cache_key in _resolution_cache:
        cached, expiry = _resolution_cache[cache_key]
        if now < expiry:
            return cached

    result = _resolve_skill_uncached(
        tenant_id, agent_id, skill_id, overlay_store=overlay_store
    )

    # Cache result
    _resolution_cache[cache_key] = (result, now + cache_ttl)
    return result


def _resolve_skill_uncached(
    tenant_id: str,
    agent_id: str,
    skill_id: str,
    *,
    overlay_store: dict[str, dict[str, Any]] | None = None,
) -> ResolvedSkill | SkillDenial:
    """Uncached three-layer resolution."""
    registry = PluginAgentRegistry.get_instance()

    # Layer 1: Base registry — agent must exist
    agent_defn = registry.get(agent_id)
    if agent_defn is None:
        return SkillDenial(
            reason=f"Agent {agent_id} not in registry",
            agent_id=agent_id,
            skill_id=skill_id,
        )

    # Layer 1: Base registry — skill must exist
    skill_defn = registry.get_skill(skill_id)
    if skill_defn is None:
        return SkillDenial(
            reason=f"Skill {skill_id} not in registry",
            agent_id=agent_id,
            skill_id=skill_id,
        )

    # Layer 2: Tenant overlay — agent enabled check (SPEC-1859 req 2)
    overlay = (overlay_store or {}).get(agent_id)
    if overlay and not overlay.get("enabled", True):
        return SkillDenial(
            reason=f"Agent {agent_id} disabled by tenant overlay",
            agent_id=agent_id,
            skill_id=skill_id,
        )

    # Layer 2: Overlay — skill enabled check (SPEC-1859 req 3c)
    skill_override = {}
    if overlay:
        raw_overrides = overlay.get("skill_overrides", {})
        skill_override = raw_overrides.get(skill_id, {})
        if isinstance(skill_override, dict) and not skill_override.get("enabled", True):
            return SkillDenial(
                reason=f"Skill {skill_id} disabled by tenant overlay",
                agent_id=agent_id,
                skill_id=skill_id,
            )

    # Layer 3: Skill binding — must have active binding (SPEC-1859 req 3d)
    from src.agents.plugins.bindings import SkillBindingService
    svc = SkillBindingService.get_instance()
    binding = svc.get_binding(tenant_id, agent_id, skill_id)
    if binding is None:
        return SkillDenial(
            reason=f"No binding for {tenant_id}/{agent_id}/{skill_id}",
            agent_id=agent_id,
            skill_id=skill_id,
        )
    if not binding.get("enabled", True):
        return SkillDenial(
            reason=f"Binding disabled for {skill_id}",
            agent_id=agent_id,
            skill_id=skill_id,
        )

    # Merge: overlay mode override > binding mode > base skill mode
    effective_mode = (
        skill_override.get("mode_override")
        or binding.get("mode")
        or skill_defn.mode
    )

    # Merge: binding credential > overlay credential
    credential_ref = (
        binding.get("credential_ref")
        or skill_override.get("credential_ref")
    )

    # Prompt overrides from overlay
    prompt_overrides = overlay.get("prompt_overrides", {}) if overlay else {}

    return ResolvedSkill(
        agent_id=agent_id,
        skill_id=skill_id,
        mode=effective_mode,
        credential_ref=credential_ref,
        approval_policy=binding.get("approval_policy", "auto"),
        prompt_overrides=prompt_overrides,
        mcp_tool_names=skill_defn.mcp_tool_names,
        enabled=True,
        display_name=skill_defn.display_name,
        description=skill_defn.description,
    )


def list_available_skills(
    tenant_id: str,
    *,
    overlay_store: dict[str, dict[str, Any]] | None = None,
    agent_id: str | None = None,
    tier: str | None = None,
) -> list[ResolvedSkill]:
    """List all invocable skills for a tenant (SPEC-1859 req 7).

    Returns only skills that pass all three resolution layers.
    If *tier* is supplied, agents above the tenant's tier are excluded.
    Used for LLM tool catalog generation.
    """
    registry = PluginAgentRegistry.get_instance()
    if agent_id:
        agents = [registry.get(agent_id)]
    else:
        agents = registry.list_available(tier=tier) if tier else registry.list_agents()

    # Tier filtering applies even for single-agent lookups
    tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
    tenant_level = tier_order.get(tier, 99) if tier else 99  # 99 = no gate

    results: list[ResolvedSkill] = []
    for agent_defn in agents:
        if agent_defn is None:
            continue
        # Skip agents above the tenant's tier
        if tier and getattr(agent_defn, "tier_gate", None):
            required_level = tier_order.get(agent_defn.tier_gate, 0)
            if tenant_level < required_level:
                continue
        for skill in agent_defn.skills:
            resolved = resolve_skill(
                tenant_id, agent_defn.agent_id, skill.skill_id,
                overlay_store=overlay_store,
            )
            if isinstance(resolved, ResolvedSkill):
                results.append(resolved)

    return sorted(results, key=lambda s: s.skill_id)
