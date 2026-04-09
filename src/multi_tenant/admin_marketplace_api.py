# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Admin Agent Marketplace API — browse and install peer agents (SPEC-1865).

Provides REST endpoints for the merchant admin dashboard's Agent Marketplace:

    GET    /api/admin/marketplace                   — List installable peer agents
    POST   /api/admin/marketplace/{agent_id}/install — Install (overlay + bindings)
    DELETE /api/admin/marketplace/{agent_id}/install — Uninstall (cleanup)

Only peer agents are shown (core pipeline agents are infrastructure).
Install is best-effort: overlay + read-skill bindings across two Cosmos
collections. On partial failure, compensating cleanup removes artifacts.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/marketplace", tags=["admin-marketplace"])


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
    """Invalidate resolution + binding caches after install/uninstall writes."""
    from src.agents.plugins.bindings import SkillBindingService
    from src.agents.plugins.overlay import clear_resolution_cache
    clear_resolution_cache()
    svc = SkillBindingService.get_instance()
    svc.invalidate(tenant_id)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class MarketplaceAgentSummary(CamelCaseModel):
    """An agent available in the marketplace."""

    agent_id: str
    display_name: str
    description: str
    category: str
    tier_gate: str
    capabilities: list[str] = Field(default_factory=list)
    skill_count: int = 0
    installed: bool = False


class MarketplaceListResponse(CamelCaseModel):
    """Paginated list of marketplace agents."""

    total: int
    agents: list[MarketplaceAgentSummary]


class InstallResponse(CamelCaseModel):
    """Result of an agent install."""

    agent_id: str
    overlay_created: bool
    bindings_created: int
    bindings_failed: int = 0


class UninstallResponse(CamelCaseModel):
    """Result of an agent uninstall."""

    agent_id: str
    overlay_removed: bool
    bindings_removed: int


# ---------------------------------------------------------------------------
# GET /api/admin/marketplace — List installable peer agents
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=MarketplaceListResponse,
    summary="List marketplace agents",
    description="Returns all peer agents available for installation, with install status for the current tenant.",
)
async def list_marketplace_agents(
    category: str | None = Query(default=None, description="Filter by agent category"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> MarketplaceListResponse:
    """List peer agents available for install/uninstall."""
    reg = _get_registry()
    overlay_repo = _get_overlay_repo()

    # Only peer agents appear in the marketplace
    peers = reg.get_peer_agents()

    if category:
        peers = [p for p in peers if p.category == category]

    # Check which agents already have overlays (= installed)
    installed_ids: set[str] = set()
    for agent in peers:
        overlay = await overlay_repo.get_overlay(ctx.tenant_id, agent.agent_id)
        if overlay is not None:
            installed_ids.add(agent.agent_id)

    # Tier-gate filter: hide agents the tenant can't use
    tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
    tenant_tier_val = tier_order.get(
        str(ctx.tier.value if hasattr(ctx.tier, "value") else ctx.tier) if ctx.tier else "free",
        0,
    )

    summaries = []
    for agent in peers:
        gate_val = tier_order.get(agent.tier_gate, 0)
        if gate_val > tenant_tier_val:
            continue  # skip agents above tenant tier

        summaries.append(MarketplaceAgentSummary(
            agent_id=agent.agent_id,
            display_name=agent.display_name,
            description=agent.description,
            category=agent.category,
            tier_gate=agent.tier_gate,
            capabilities=list(agent.capabilities),
            skill_count=len(agent.skills),
            installed=agent.agent_id in installed_ids,
        ))

    return MarketplaceListResponse(total=len(summaries), agents=summaries)


# ---------------------------------------------------------------------------
# POST /api/admin/marketplace/{agent_id}/install — Install agent
# ---------------------------------------------------------------------------


@router.post(
    "/{agent_id}/install",
    response_model=InstallResponse,
    summary="Install a peer agent",
    description=(
        "Creates an overlay (enabled) and read-skill bindings for all agent "
        "skills. Best-effort: on partial failure, compensating cleanup removes "
        "successfully created artifacts."
    ),
    responses={
        404: {"description": "Agent not found in registry"},
        409: {"description": "Agent already installed"},
        422: {"description": "Agent tier-gated above tenant tier"},
    },
)
async def install_agent(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> InstallResponse:
    """Install a peer agent for this tenant."""
    reg = _get_registry()
    agent_defn = reg.get(agent_id)

    if agent_defn is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if agent_defn.agent_kind != "peer":
        raise HTTPException(status_code=422, detail="Only peer agents can be installed")

    # Tier-gate
    tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
    tenant_tier_val = tier_order.get(
        str(ctx.tier.value if hasattr(ctx.tier, "value") else ctx.tier) if ctx.tier else "free",
        0,
    )
    if tier_order.get(agent_defn.tier_gate, 0) > tenant_tier_val:
        raise HTTPException(
            status_code=422,
            detail=f"Tenant tier '{ctx.tier}' does not meet agent tier gate '{agent_defn.tier_gate}'",
        )

    overlay_repo = _get_overlay_repo()
    binding_repo = _get_binding_repo()

    # Check not already installed
    existing = await overlay_repo.get_overlay(ctx.tenant_id, agent_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Agent '{agent_id}' already installed")

    # Step 1: Create overlay (enabled, no customizations)
    await overlay_repo.upsert_overlay(
        ctx.tenant_id, agent_id, enabled=True,
    )

    # Step 2: Create bindings for each skill
    created_bindings: list[str] = []
    failed_bindings: list[str] = []
    for skill in agent_defn.skills:
        try:
            await binding_repo.upsert_binding(
                ctx.tenant_id,
                agent_id,
                skill.skill_id,
                mode=skill.mode,
                enabled=True,
            )
            created_bindings.append(skill.skill_id)
        except Exception:
            logger.warning(
                "Marketplace: binding creation failed for %s/%s/%s",
                ctx.tenant_id[:8], agent_id, skill.skill_id,
                exc_info=True,
            )
            failed_bindings.append(skill.skill_id)

    # Compensating cleanup on full failure
    if failed_bindings and not created_bindings:
        logger.error(
            "Marketplace: all bindings failed for %s/%s, removing overlay",
            ctx.tenant_id[:8], agent_id,
        )
        await overlay_repo.delete_overlay(ctx.tenant_id, agent_id)
        raise HTTPException(
            status_code=500,
            detail=f"Installation failed: could not create any skill bindings for '{agent_id}'",
        )

    _invalidate_caches(ctx.tenant_id)

    logger.info(
        "Marketplace: installed agent=%s tenant=%s bindings=%d/%d",
        agent_id, ctx.tenant_id[:8],
        len(created_bindings), len(created_bindings) + len(failed_bindings),
    )

    return InstallResponse(
        agent_id=agent_id,
        overlay_created=True,
        bindings_created=len(created_bindings),
        bindings_failed=len(failed_bindings),
    )


# ---------------------------------------------------------------------------
# DELETE /api/admin/marketplace/{agent_id}/install — Uninstall agent
# ---------------------------------------------------------------------------


@router.delete(
    "/{agent_id}/install",
    response_model=UninstallResponse,
    summary="Uninstall a peer agent",
    description="Removes the overlay and all skill bindings for this agent.",
    responses={
        404: {"description": "Agent not installed"},
    },
)
async def uninstall_agent(
    agent_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> UninstallResponse:
    """Uninstall a peer agent — remove overlay and all bindings."""
    overlay_repo = _get_overlay_repo()
    binding_repo = _get_binding_repo()

    # Check overlay exists (= installed)
    existing = await overlay_repo.get_overlay(ctx.tenant_id, agent_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not installed")

    # Remove all bindings for this agent — fail-closed:
    # if any binding deletion fails, abort before removing the overlay
    # to prevent residual routability (Codex P1).
    bindings = await binding_repo.list_bindings(ctx.tenant_id, agent_id=agent_id)
    removed = 0
    failed_skills: list[str] = []
    for binding in bindings:
        skill_id = binding.get("skill_id") or binding.get("id")
        if skill_id:
            try:
                await binding_repo.delete_binding(ctx.tenant_id, skill_id)
                removed += 1
            except Exception:
                logger.warning(
                    "Marketplace: binding removal failed for %s/%s/%s",
                    ctx.tenant_id[:8], agent_id, skill_id,
                    exc_info=True,
                )
                failed_skills.append(skill_id)

    if failed_skills:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Uninstall aborted: could not remove bindings {failed_skills}. "
                f"Overlay preserved to prevent residual routability."
            ),
        )

    # All bindings removed — safe to remove overlay
    overlay_removed = await overlay_repo.delete_overlay(ctx.tenant_id, agent_id)

    _invalidate_caches(ctx.tenant_id)

    logger.info(
        "Marketplace: uninstalled agent=%s tenant=%s bindings_removed=%d",
        agent_id, ctx.tenant_id[:8], removed,
    )

    return UninstallResponse(
        agent_id=agent_id,
        overlay_removed=overlay_removed,
        bindings_removed=removed,
    )
