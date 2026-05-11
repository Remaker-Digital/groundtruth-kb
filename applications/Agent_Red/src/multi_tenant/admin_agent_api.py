# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tenant Admin — Agent Lifecycle API (Phase 4a, WI-4016).

Tenant-scoped agent overlay and skill binding management for the
standalone admin console. Uses get_tenant_context for auth (tenant admin
keys accepted), unlike the superadmin router which requires platform admin.

  GET    /api/admin/agents                                — List agents with overlay status
  GET    /api/admin/agents/{agent_id}/overlay             — Get overlay
  PUT    /api/admin/agents/{agent_id}/overlay             — Create/update overlay
  DELETE /api/admin/agents/{agent_id}/overlay             — Delete overlay
  GET    /api/admin/agents/{agent_id}/effective-config    — Get resolved config
  GET    /api/admin/agents/{agent_id}/bindings            — List bindings
  PUT    /api/admin/agents/{agent_id}/skills/{skill_id}/binding  — Create/update binding
  DELETE /api/admin/agents/{agent_id}/skills/{skill_id}/binding  — Delete binding
  GET    /api/admin/agents/available-skills               — List invocable skills

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/agents", tags=["admin-agents"])


# ---------------------------------------------------------------------------
# Helpers (lazy imports to avoid circular deps at module load)
# ---------------------------------------------------------------------------


def _get_registry():
    from src.agents.plugins.registry import PluginAgentRegistry
    return PluginAgentRegistry.get_instance()


def _get_overlay_repo():
    from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository
    return TenantAgentOverlayRepository()


def _get_binding_repo():
    from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository
    return AgentSkillBindingRepository()


def _invalidate_caches(tenant_id: str) -> None:
    """Invalidate resolution + binding caches on write."""
    from src.agents.plugins.bindings import SkillBindingService
    from src.agents.plugins.overlay import clear_resolution_cache
    clear_resolution_cache()
    svc = SkillBindingService.get_instance()
    svc.invalidate(tenant_id)


def _validate_agent_id(agent_id: str) -> None:
    reg = _get_registry()
    if reg.get(agent_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")


def _validate_tier_gate(ctx: TenantContext, agent_id: str) -> None:
    """Enforce tier-based entitlement for the given agent.

    Compares the tenant's tier against the agent's tier_gate field from
    the registry YAML. If the tenant tier is below the required gate,
    returns 403 (fail-closed). Platform admins bypass the gate.

    SPEC-1852 / Phase 4b WP1: shared entitlement gate applied to all
    admin agent API endpoints and runtime dispatch paths.
    """
    if ctx.is_platform_admin:
        return  # Platform admins bypass tier gating

    reg = _get_registry()
    agent_defn = reg.get(agent_id)
    if agent_defn is None:
        return  # Let _validate_agent_id handle 404

    tier_gate = getattr(agent_defn, "tier_gate", None)
    if not tier_gate or tier_gate == "free":
        return  # No gate or free-tier agent — always accessible

    tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
    tenant_tier = ctx.tier.value if ctx.tier and hasattr(ctx.tier, "value") else (ctx.tier or "free")
    tenant_level = tier_order.get(str(tenant_tier), 0)
    required_level = tier_order.get(tier_gate, 0)

    if tenant_level < required_level:
        raise HTTPException(
            status_code=403,
            detail=f"Agent '{agent_id}' requires tier '{tier_gate}'. Current tier: '{tenant_tier}'.",
        )


def _validate_skill_id(agent_id: str, skill_id: str) -> None:
    reg = _get_registry()
    skill = reg.get_skill(skill_id)
    if skill is None or skill.agent_id != agent_id:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown skill: {skill_id} for agent {agent_id}",
        )


# ---------------------------------------------------------------------------
# Response / Input models (re-use shapes from superadmin, tenant-admin naming)
# ---------------------------------------------------------------------------


class SkillOverrideModel(CamelCaseModel):
    enabled: bool = True
    mode_override: str | None = None
    credential_ref: str | None = None


class AgentOverlayModel(CamelCaseModel):
    agent_id: str = ""
    enabled: bool = True
    prompt_overrides: dict[str, str] = Field(default_factory=dict)
    skill_overrides: dict[str, SkillOverrideModel] = Field(default_factory=dict)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)
    visibility_scope: str = "public"
    staff_domain_tags: list[str] = Field(default_factory=list)
    updated_at: str = ""


class AgentOverlayInput(CamelCaseModel):
    enabled: bool = True
    prompt_overrides: dict[str, str] = Field(default_factory=dict)
    skill_overrides: dict[str, SkillOverrideModel] = Field(default_factory=dict)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)
    visibility_scope: str = Field(
        default="public",
        description="Controls agent visibility: 'public' (all staff) or 'private' (matching domain tags only)",
    )
    staff_domain_tags: list[str] = Field(
        default_factory=list,
        description="Domain tags required for private-scope agents",
    )


class EffectiveSkillModel(CamelCaseModel):
    skill_id: str
    display_name: str
    description: str = ""
    mode: str
    enabled: bool
    credential_ref: str | None = None


class EffectiveAgentConfigModel(CamelCaseModel):
    agent_id: str
    display_name: str
    agent_kind: str
    enabled: bool
    prompt_overrides: dict[str, str] = Field(default_factory=dict)
    skills: list[EffectiveSkillModel] = Field(default_factory=list)


class AgentSummaryModel(CamelCaseModel):
    agent_id: str
    display_name: str
    description: str = ""
    agent_kind: str
    category: str = ""
    has_overlay: bool
    enabled: bool


class BindingModel(CamelCaseModel):
    agent_id: str = ""
    skill_id: str = ""
    credential_ref: str | None = None
    mode: str = "read"
    approval_policy: str = "auto"
    enabled: bool = True


class BindingInput(CamelCaseModel):
    credential_ref: str | None = None
    mode: str = "read"
    approval_policy: str = "auto"
    enabled: bool = True


# ---------------------------------------------------------------------------
# Overlay Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=list[AgentSummaryModel],
    summary="List agents with overlay status",
    status_code=200,
)
async def list_agents(
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[AgentSummaryModel]:
    """List registered agents filtered by tenant tier entitlement."""
    tenant_id = ctx.tenant_id
    tenant_tier = ctx.tier.value if ctx.tier and hasattr(ctx.tier, "value") else (ctx.tier or "free")
    reg = _get_registry()
    repo = _get_overlay_repo()
    docs = await repo.list_overlays(tenant_id)
    overlays = {doc["agent_id"]: doc for doc in docs}

    results = []
    for agent in reg.list_available(tier=str(tenant_tier)):
        overlay = overlays.get(agent.agent_id)
        results.append(AgentSummaryModel(
            agent_id=agent.agent_id,
            display_name=agent.display_name,
            description=agent.description,
            agent_kind=agent.agent_kind,
            category=agent.category,
            has_overlay=overlay is not None,
            enabled=overlay.get("enabled", True) if overlay else True,
        ))
    return results


@router.get(
    "/{agent_id}/overlay",
    response_model=AgentOverlayModel,
    summary="Get agent overlay",
    status_code=200,
)
async def get_overlay(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentOverlayModel:
    """Get the overlay for this tenant + agent."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    repo = _get_overlay_repo()
    overlay = await repo.get_overlay(ctx.tenant_id, agent_id)
    if overlay is None:
        raise HTTPException(status_code=404, detail="No overlay for this agent")

    return AgentOverlayModel(
        agent_id=overlay.get("agent_id", agent_id),
        enabled=overlay.get("enabled", True),
        prompt_overrides=overlay.get("prompt_overrides", {}),
        skill_overrides={
            k: SkillOverrideModel(**v) if isinstance(v, dict) else v
            for k, v in overlay.get("skill_overrides", {}).items()
        },
        custom_metadata=overlay.get("custom_metadata", {}),
        visibility_scope=overlay.get("visibility_scope", "public"),
        staff_domain_tags=overlay.get("staff_domain_tags", []),
        updated_at=overlay.get("updated_at", ""),
    )


@router.put(
    "/{agent_id}/overlay",
    response_model=AgentOverlayModel,
    summary="Create or update agent overlay",
    status_code=200,
)
async def put_overlay(
    agent_id: str,
    body: AgentOverlayInput,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentOverlayModel:
    """Create or update overlay for this tenant + agent."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    tenant_id = ctx.tenant_id

    skill_ovr = {}
    for sid, so in (body.skill_overrides or {}).items():
        skill_ovr[sid] = so.model_dump() if hasattr(so, "model_dump") else so

    repo = _get_overlay_repo()
    result = await repo.upsert_overlay(
        tenant_id,
        agent_id,
        enabled=body.enabled,
        prompt_overrides=body.prompt_overrides,
        skill_overrides=skill_ovr,
        custom_metadata=body.custom_metadata,
        visibility_scope=body.visibility_scope,
        staff_domain_tags=body.staff_domain_tags,
    )

    _invalidate_caches(tenant_id)

    return AgentOverlayModel(
        agent_id=result.get("agent_id", agent_id),
        enabled=result.get("enabled", True),
        prompt_overrides=result.get("prompt_overrides", {}),
        skill_overrides={
            k: SkillOverrideModel(**v) if isinstance(v, dict) else v
            for k, v in result.get("skill_overrides", {}).items()
        },
        custom_metadata=result.get("custom_metadata", {}),
        visibility_scope=result.get("visibility_scope", "public"),
        staff_domain_tags=result.get("staff_domain_tags", []),
        updated_at=result.get("updated_at", ""),
    )


@router.delete(
    "/{agent_id}/overlay",
    summary="Delete agent overlay",
    status_code=204,
)
async def delete_overlay(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete overlay, reverting to base registry defaults."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    repo = _get_overlay_repo()
    deleted = await repo.delete_overlay(ctx.tenant_id, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No overlay for this agent")
    _invalidate_caches(ctx.tenant_id)


# ---------------------------------------------------------------------------
# Effective Config
# ---------------------------------------------------------------------------


@router.get(
    "/{agent_id}/effective-config",
    response_model=EffectiveAgentConfigModel,
    summary="Get resolved effective agent configuration",
    status_code=200,
)
async def get_effective_config(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EffectiveAgentConfigModel:
    """Resolve and return the effective config for this tenant + agent."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    tenant_id = ctx.tenant_id

    from src.agents.plugins.bindings import SkillBindingService
    from src.agents.plugins.overlay import resolve_for_tenant

    # Hydrate binding cache before sync resolution
    svc = SkillBindingService.get_instance()
    if tenant_id not in svc._loaded_tenants:
        await svc.load_tenant_bindings(tenant_id)

    repo = _get_overlay_repo()
    docs = await repo.list_overlays(tenant_id)
    overlays = {doc["agent_id"]: doc for doc in docs}

    config = resolve_for_tenant(tenant_id, agent_id, overlays)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")

    return EffectiveAgentConfigModel(
        agent_id=config.agent_id,
        display_name=config.display_name,
        agent_kind=config.agent_kind,
        enabled=config.enabled,
        prompt_overrides=config.prompt_overrides,
        skills=[
            EffectiveSkillModel(
                skill_id=s.skill_id,
                display_name=s.display_name,
                mode=s.mode,
                enabled=s.enabled,
                credential_ref=s.credential_ref,
            )
            for s in config.skills
        ],
    )


# ---------------------------------------------------------------------------
# Binding Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/{agent_id}/bindings",
    response_model=list[BindingModel],
    summary="List skill bindings for agent",
    status_code=200,
)
async def list_bindings(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[BindingModel]:
    """List all bindings for this tenant + agent."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    repo = _get_binding_repo()
    bindings = await repo.list_bindings(ctx.tenant_id, agent_id=agent_id)
    return [
        BindingModel(
            agent_id=b.get("agent_id", agent_id),
            skill_id=b.get("skill_id", ""),
            credential_ref=b.get("credential_ref"),
            mode=b.get("mode", "read"),
            approval_policy=b.get("approval_policy", "auto"),
            enabled=b.get("enabled", True),
        )
        for b in bindings
    ]


@router.get(
    "/{agent_id}/skills/{skill_id}/binding",
    response_model=BindingModel,
    summary="Get a skill binding",
    status_code=200,
)
async def get_binding(
    agent_id: str,
    skill_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> BindingModel:
    """Get a specific skill binding."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    _validate_skill_id(agent_id, skill_id)
    repo = _get_binding_repo()
    binding = await repo.get_binding(ctx.tenant_id, skill_id)
    if binding is None:
        raise HTTPException(status_code=404, detail="No binding found")
    return BindingModel(
        agent_id=binding.get("agent_id", agent_id),
        skill_id=binding.get("skill_id", skill_id),
        credential_ref=binding.get("credential_ref"),
        mode=binding.get("mode", "read"),
        approval_policy=binding.get("approval_policy", "auto"),
        enabled=binding.get("enabled", True),
    )


@router.put(
    "/{agent_id}/skills/{skill_id}/binding",
    response_model=BindingModel,
    summary="Create or update a skill binding",
    status_code=200,
)
async def put_binding(
    agent_id: str,
    skill_id: str,
    body: BindingInput,
    ctx: TenantContext = Depends(get_tenant_context),
) -> BindingModel:
    """Create or update a binding."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    _validate_skill_id(agent_id, skill_id)
    tenant_id = ctx.tenant_id
    repo = _get_binding_repo()
    result = await repo.upsert_binding(
        tenant_id,
        agent_id,
        skill_id,
        credential_ref=body.credential_ref,
        mode=body.mode,
        approval_policy=body.approval_policy,
        enabled=body.enabled,
    )
    _invalidate_caches(tenant_id)
    return BindingModel(
        agent_id=result.get("agent_id", agent_id),
        skill_id=result.get("skill_id", skill_id),
        credential_ref=result.get("credential_ref"),
        mode=result.get("mode", "read"),
        approval_policy=result.get("approval_policy", "auto"),
        enabled=result.get("enabled", True),
    )


@router.delete(
    "/{agent_id}/skills/{skill_id}/binding",
    summary="Delete a skill binding",
    status_code=204,
)
async def delete_binding(
    agent_id: str,
    skill_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete a binding, revoking tenant access to this skill."""
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    _validate_skill_id(agent_id, skill_id)
    repo = _get_binding_repo()
    deleted = await repo.delete_binding(ctx.tenant_id, skill_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No binding found")
    _invalidate_caches(ctx.tenant_id)


# ---------------------------------------------------------------------------
# Available Skills
# ---------------------------------------------------------------------------


@router.get(
    "/{agent_id}/bindable-skills",
    response_model=list[EffectiveSkillModel],
    summary="List all skills that can be bound for an agent",
    status_code=200,
)
async def list_bindable_skills(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[EffectiveSkillModel]:
    """List skills from the registry for an agent, regardless of binding state.

    This endpoint returns the full skill catalog for Add Binding bootstrapping.
    Unlike /available-skills, it does NOT require existing bindings to return results.
    """
    _validate_agent_id(agent_id)
    _validate_tier_gate(ctx, agent_id)
    reg = _get_registry()
    agent_defn = reg.get(agent_id)
    if agent_defn is None:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")

    return [
        EffectiveSkillModel(
            skill_id=skill.skill_id,
            display_name=skill.display_name,
            description=skill.description,
            mode=skill.mode,
            enabled=skill.enabled,
            credential_ref=None,
        )
        for skill in agent_defn.skills
    ]


@router.get(
    "/available-skills",
    response_model=list[EffectiveSkillModel],
    summary="List all invocable skills for this tenant",
    status_code=200,
)
async def list_available_skills(
    agent_id: str | None = Query(None, description="Filter by agent ID"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[EffectiveSkillModel]:
    """List skills that pass all three resolution layers."""
    from src.agents.plugins.bindings import SkillBindingService
    from src.agents.plugins.overlay import list_available_skills as _list_available

    tenant_id = ctx.tenant_id

    # Hydrate binding cache
    svc = SkillBindingService.get_instance()
    if tenant_id not in svc._loaded_tenants:
        await svc.load_tenant_bindings(tenant_id)

    repo = _get_overlay_repo()
    docs = await repo.list_overlays(tenant_id)
    overlays = {doc["agent_id"]: doc for doc in docs}

    tenant_tier = ctx.tier.value if ctx.tier and hasattr(ctx.tier, "value") else (ctx.tier or "free")
    resolved = _list_available(tenant_id, overlay_store=overlays, agent_id=agent_id, tier=str(tenant_tier))
    return [
        EffectiveSkillModel(
            skill_id=s.skill_id,
            display_name=s.display_name,
            mode=s.mode,
            enabled=s.enabled,
            credential_ref=s.credential_ref,
        )
        for s in resolved
    ]
