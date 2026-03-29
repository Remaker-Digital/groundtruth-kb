"""Superadmin API -- Tenant Agent Overlay CRUD (SPEC-1854, WI-1666).

Admin endpoints for managing per-tenant, per-agent configuration overlays.

  GET  /tenants/{tenant_id}/agents                             — List overlays for a tenant
  GET  /tenants/{tenant_id}/agents/{agent_id}/overlay          — Get overlay
  PUT  /tenants/{tenant_id}/agents/{agent_id}/overlay          — Create/update overlay
  DELETE /tenants/{tenant_id}/agents/{agent_id}/overlay        — Delete overlay
  GET  /tenants/{tenant_id}/agents/{agent_id}/effective-config — Get resolved config

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)

# In-memory overlay store (will be replaced with Cosmos repo in Phase 1)
_overlay_store: dict[str, dict[str, dict[str, Any]]] = {}


def _get_registry():
    from src.agents.plugins.registry import PluginAgentRegistry
    return PluginAgentRegistry.get_instance()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class SkillOverrideModel(CamelCaseModel):
    """Per-skill override in a tenant overlay."""

    enabled: bool = True
    mode_override: str | None = None
    credential_ref: str | None = None


class AgentOverlayModel(CamelCaseModel):
    """Tenant agent overlay configuration."""

    tenant_id: str = ""
    agent_id: str = ""
    enabled: bool = True
    prompt_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Reserved for Phase 2. Accepted but not yet consumed by SystemPromptBuilder.",
    )
    skill_overrides: dict[str, SkillOverrideModel] = Field(default_factory=dict)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: str = ""


class AgentOverlayInput(CamelCaseModel):
    """Input for creating/updating an overlay."""

    enabled: bool = True
    prompt_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Reserved for Phase 2. Accepted but not yet consumed by SystemPromptBuilder.",
    )
    skill_overrides: dict[str, SkillOverrideModel] = Field(default_factory=dict)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)


class EffectiveSkillModel(CamelCaseModel):
    """Resolved skill in effective config response."""

    skill_id: str
    display_name: str
    mode: str
    enabled: bool
    credential_ref: str | None = None


class EffectiveAgentConfigModel(CamelCaseModel):
    """Resolved agent configuration response."""

    agent_id: str
    display_name: str
    agent_kind: str
    enabled: bool
    prompt_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Reserved for Phase 2. Accepted but not yet consumed by SystemPromptBuilder.",
    )
    skills: list[EffectiveSkillModel] = Field(default_factory=list)


class AgentSummaryModel(CamelCaseModel):
    """Summary of an agent with overlay status."""

    agent_id: str
    display_name: str
    agent_kind: str
    has_overlay: bool
    enabled: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_agent_id(agent_id: str) -> None:
    """Raise 404 if agent_id not in base registry."""
    reg = _get_registry()
    if reg.get(agent_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent: {agent_id}",
        )


def _get_tenant_overlays(tenant_id: str) -> dict[str, dict[str, Any]]:
    """Get all overlays for a tenant."""
    return _overlay_store.get(tenant_id, {})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/tenants/{tenant_id}/agents",
    response_model=list[AgentSummaryModel],
    summary="List agents with overlay status for a tenant",
    status_code=200,
)
async def list_tenant_agents(
    tenant_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[AgentSummaryModel]:
    """List all registered agents with whether a tenant overlay exists (SPEC-1854)."""
    reg = _get_registry()
    overlays = _get_tenant_overlays(tenant_id)
    results = []
    for agent in reg.list_agents():
        overlay = overlays.get(agent.agent_id)
        results.append(AgentSummaryModel(
            agent_id=agent.agent_id,
            display_name=agent.display_name,
            agent_kind=agent.agent_kind,
            has_overlay=overlay is not None,
            enabled=overlay.get("enabled", True) if overlay else True,
        ))
    return results


@router.get(
    "/tenants/{tenant_id}/agents/{agent_id}/overlay",
    response_model=AgentOverlayModel,
    summary="Get tenant agent overlay",
    status_code=200,
)
async def get_agent_overlay(
    tenant_id: str,
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentOverlayModel:
    """Get the overlay for a specific tenant + agent (SPEC-1854)."""
    _validate_agent_id(agent_id)
    overlays = _get_tenant_overlays(tenant_id)
    overlay = overlays.get(agent_id)
    if overlay is None:
        raise HTTPException(status_code=404, detail="No overlay for this agent")

    return AgentOverlayModel(
        tenant_id=tenant_id,
        agent_id=agent_id,
        **overlay,
    )


@router.put(
    "/tenants/{tenant_id}/agents/{agent_id}/overlay",
    response_model=AgentOverlayModel,
    summary="Create or update tenant agent overlay",
    status_code=200,
)
async def put_agent_overlay(
    tenant_id: str,
    agent_id: str,
    body: AgentOverlayInput,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentOverlayModel:
    """Create or update overlay for a tenant + agent (SPEC-1854)."""
    _validate_agent_id(agent_id)

    now = datetime.now(timezone.utc).isoformat()
    overlay_data = body.model_dump()
    overlay_data["updated_at"] = now

    # Serialize skill overrides to dict
    skill_ovr = {}
    for sid, so in (body.skill_overrides or {}).items():
        skill_ovr[sid] = so.model_dump() if hasattr(so, "model_dump") else so
    overlay_data["skill_overrides"] = skill_ovr

    if tenant_id not in _overlay_store:
        _overlay_store[tenant_id] = {}
    _overlay_store[tenant_id][agent_id] = overlay_data

    return AgentOverlayModel(
        tenant_id=tenant_id,
        agent_id=agent_id,
        **overlay_data,
    )


@router.delete(
    "/tenants/{tenant_id}/agents/{agent_id}/overlay",
    summary="Delete tenant agent overlay",
    status_code=204,
)
async def delete_agent_overlay(
    tenant_id: str,
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete overlay, reverting to base registry defaults (SPEC-1854)."""
    _validate_agent_id(agent_id)
    overlays = _get_tenant_overlays(tenant_id)
    if agent_id not in overlays:
        raise HTTPException(status_code=404, detail="No overlay for this agent")
    del _overlay_store[tenant_id][agent_id]


@router.get(
    "/tenants/{tenant_id}/agents/{agent_id}/effective-config",
    response_model=EffectiveAgentConfigModel,
    summary="Get resolved effective agent configuration",
    status_code=200,
)
async def get_effective_config(
    tenant_id: str,
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EffectiveAgentConfigModel:
    """Resolve and return the effective config for tenant + agent (SPEC-1854 req 3)."""
    _validate_agent_id(agent_id)

    from src.agents.plugins.overlay import resolve_for_tenant
    overlays = _get_tenant_overlays(tenant_id)
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
# Agent Skill Binding CRUD (SPEC-1856, WI-1674)
# ---------------------------------------------------------------------------


class BindingModel(CamelCaseModel):
    """Agent skill binding."""

    tenant_id: str = ""
    agent_id: str = ""
    skill_id: str = ""
    credential_ref: str | None = None
    mode: str = "read"
    approval_policy: str = "auto"
    enabled: bool = True


class BindingInput(CamelCaseModel):
    """Input for creating/updating a binding."""

    credential_ref: str | None = None
    mode: str = "read"
    approval_policy: str = "auto"
    enabled: bool = True


def _validate_skill_id(agent_id: str, skill_id: str) -> None:
    """Raise 404 if skill_id not in registry for this agent."""
    reg = _get_registry()
    skill = reg.get_skill(skill_id)
    if skill is None or skill.agent_id != agent_id:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown skill: {skill_id} for agent {agent_id}",
        )


def _get_binding_svc():
    from src.agents.plugins.bindings import SkillBindingService
    return SkillBindingService.get_instance()


@router.get(
    "/tenants/{tenant_id}/agents/{agent_id}/bindings",
    response_model=list[BindingModel],
    summary="List skill bindings for tenant + agent",
    status_code=200,
)
async def list_skill_bindings(
    tenant_id: str,
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[BindingModel]:
    """List all bindings for a tenant + agent (SPEC-1856 req 7)."""
    _validate_agent_id(agent_id)
    svc = _get_binding_svc()
    bindings = svc.list_bindings(tenant_id, agent_id=agent_id)
    return [BindingModel(**b) for b in bindings]


@router.get(
    "/tenants/{tenant_id}/agents/{agent_id}/skills/{skill_id}/binding",
    response_model=BindingModel,
    summary="Get a skill binding",
    status_code=200,
)
async def get_skill_binding(
    tenant_id: str,
    agent_id: str,
    skill_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> BindingModel:
    """Get a specific skill binding (SPEC-1856 req 7)."""
    _validate_agent_id(agent_id)
    _validate_skill_id(agent_id, skill_id)
    svc = _get_binding_svc()
    binding = svc.get_binding(tenant_id, agent_id, skill_id)
    if binding is None:
        raise HTTPException(status_code=404, detail="No binding found")
    return BindingModel(**binding)


@router.put(
    "/tenants/{tenant_id}/agents/{agent_id}/skills/{skill_id}/binding",
    response_model=BindingModel,
    summary="Create or update a skill binding",
    status_code=200,
)
async def put_skill_binding(
    tenant_id: str,
    agent_id: str,
    skill_id: str,
    body: BindingInput,
    ctx: TenantContext = Depends(get_tenant_context),
) -> BindingModel:
    """Create or update a binding (SPEC-1856 req 7)."""
    _validate_agent_id(agent_id)
    _validate_skill_id(agent_id, skill_id)
    svc = _get_binding_svc()
    binding = svc.create_binding(
        tenant_id=tenant_id,
        agent_id=agent_id,
        skill_id=skill_id,
        credential_ref=body.credential_ref,
        mode=body.mode,
        approval_policy=body.approval_policy,
        enabled=body.enabled,
    )
    return BindingModel(**binding)


@router.delete(
    "/tenants/{tenant_id}/agents/{agent_id}/skills/{skill_id}/binding",
    summary="Delete a skill binding",
    status_code=204,
)
async def delete_skill_binding(
    tenant_id: str,
    agent_id: str,
    skill_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete a binding, revoking tenant access to this skill (SPEC-1856)."""
    _validate_agent_id(agent_id)
    svc = _get_binding_svc()
    if not svc.delete_binding(tenant_id, agent_id, skill_id):
        raise HTTPException(status_code=404, detail="No binding found")


@router.get(
    "/tenants/{tenant_id}/available-skills",
    response_model=list[EffectiveSkillModel],
    summary="List all invocable skills for a tenant",
    status_code=200,
)
async def list_tenant_available_skills(
    tenant_id: str,
    agent_id: str | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[EffectiveSkillModel]:
    """List skills that pass all three resolution layers (SPEC-1859 req 7)."""
    from src.agents.plugins.overlay import list_available_skills
    overlays = _get_tenant_overlays(tenant_id)
    resolved = list_available_skills(
        tenant_id, overlay_store=overlays, agent_id=agent_id
    )
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


# ---------------------------------------------------------------------------
# Team Member Agent Access CRUD (SPEC-1862, WI-3007)
# ---------------------------------------------------------------------------


class AgentAccessModel(CamelCaseModel):
    """Team member agent access list."""

    agent_access: list[str] = Field(default_factory=list)


def _get_team_repo():
    """Get TeamMemberRepository for durable agent_access storage."""
    from src.multi_tenant.repositories.team import TeamMemberRepository
    return TeamMemberRepository()


@router.get(
    "/tenants/{tenant_id}/team-members/{member_id}/agent-access",
    response_model=AgentAccessModel,
    summary="Get team member agent access list",
    status_code=200,
)
async def get_agent_access(
    tenant_id: str,
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentAccessModel:
    """Get which agents a team member can chat with directly (SPEC-1862)."""
    repo = _get_team_repo()
    try:
        doc = await repo.read(tenant_id, member_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Team member not found: {member_id}")
    access = doc.get("agent_access", []) if doc else []
    return AgentAccessModel(agent_access=access)


@router.put(
    "/tenants/{tenant_id}/team-members/{member_id}/agent-access",
    response_model=AgentAccessModel,
    summary="Update team member agent access list",
    status_code=200,
)
async def put_agent_access(
    tenant_id: str,
    member_id: str,
    body: AgentAccessModel,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AgentAccessModel:
    """Set which agents a team member can chat with directly (SPEC-1862)."""
    repo = _get_team_repo()
    await repo.update_member_fields(
        tenant_id=tenant_id,
        member_id=member_id,
        updates={"agent_access": body.agent_access},
    )
    return AgentAccessModel(agent_access=body.agent_access)
