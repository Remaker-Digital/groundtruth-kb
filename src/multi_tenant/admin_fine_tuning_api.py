"""Admin Fine-Tuning API — Layer 4 management endpoints (SPEC-1522).

Provides REST endpoints for managing per-tenant model fine-tuning:

    POST /api/admin/fine-tuning/trigger    — Trigger training pipeline
    GET  /api/admin/fine-tuning/status     — Job status + model history
    GET  /api/admin/fine-tuning/experiments — A/B experiment status
    POST /api/admin/fine-tuning/rollback   — Rollback to base model

All endpoints require Enterprise tier. Non-Enterprise requests receive 403.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/fine-tuning", tags=["admin-fine-tuning"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class TriggerResponse(CamelCaseModel):
    """Response from POST /trigger."""

    job_id: str = Field(description="Training job ID")
    status: str = Field(description="Initial job status")
    message: str = Field(default="Fine-tuning pipeline triggered")


class StatusResponse(CamelCaseModel):
    """Response from GET /status."""

    fine_tuning_enabled: bool = Field(description="Whether fine-tuning is enabled")
    active_model_id: str | None = Field(default=None, description="Currently active model")
    active_model_version: int | None = Field(default=None, description="Active model version")
    jobs: list[dict[str, Any]] = Field(default_factory=list, description="Job history")
    models: list[dict[str, Any]] = Field(default_factory=list, description="Model history")


class ExperimentsResponse(CamelCaseModel):
    """Response from GET /experiments."""

    active_experiment_id: str | None = Field(default=None)
    experiments: list[dict[str, Any]] = Field(default_factory=list)


class RollbackResponse(CamelCaseModel):
    """Response from POST /rollback."""

    message: str = Field(description="Rollback confirmation")
    previous_model_id: str | None = Field(default=None)


# ---------------------------------------------------------------------------
# Tier enforcement helper
# ---------------------------------------------------------------------------


def _require_enterprise(ctx: TenantContext) -> None:
    """Raise 403 if tenant is not Enterprise tier."""
    if ctx.tier != TenantTier.ENTERPRISE:
        raise HTTPException(
            status_code=403,
            detail="Fine-tuning is an Enterprise-only feature. Upgrade to access.",
        )


def _get_service() -> Any:
    """Get the singleton FineTuningPipelineService."""
    from src.multi_tenant.fine_tuning_pipeline import get_fine_tuning_service

    return get_fine_tuning_service()


# ---------------------------------------------------------------------------
# POST /api/admin/fine-tuning/trigger — Start training pipeline
# ---------------------------------------------------------------------------


@router.post(
    "/trigger",
    response_model=TriggerResponse,
    summary="Trigger fine-tuning pipeline",
    responses={403: {"description": "Enterprise tier required"}},
)
async def trigger_fine_tuning(
    ctx: TenantContext = Depends(get_tenant_context),
) -> TriggerResponse:
    """Trigger the full fine-tuning pipeline for this tenant.

    Runs asynchronously: collect → cleanse → format → train → evaluate → deploy.
    """
    _require_enterprise(ctx)

    service = _get_service()
    try:
        result = await service.run_full_pipeline(ctx.tenant_id)
        if result is None:
            return TriggerResponse(
                job_id="",
                status="failed",
                message="Pipeline did not produce a model. Check logs for details.",
            )
        return TriggerResponse(
            job_id=result.id if hasattr(result, "id") else "",
            status=result.status.value if hasattr(result, "status") else "completed",
            message="Fine-tuning pipeline completed successfully",
        )
    except Exception as exc:
        logger.error("Fine-tuning trigger failed: tenant=%s error=%s", ctx.tenant_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# GET /api/admin/fine-tuning/status — Job status + model history
# ---------------------------------------------------------------------------


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Get fine-tuning status and model history",
    responses={403: {"description": "Enterprise tier required"}},
)
async def get_fine_tuning_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> StatusResponse:
    """Return fine-tuning status, active model, and model history."""
    _require_enterprise(ctx)

    service = _get_service()
    models = await service.get_model_history(ctx.tenant_id)

    return StatusResponse(
        fine_tuning_enabled=ctx.preferences.fine_tuning_enabled if ctx.preferences else False,
        active_model_id=ctx.preferences.fine_tuning_active_model_id if ctx.preferences else None,
        active_model_version=ctx.preferences.fine_tuning_active_model_version if ctx.preferences else None,
        models=[m.model_dump() for m in models],
    )


# ---------------------------------------------------------------------------
# GET /api/admin/fine-tuning/experiments — A/B experiment status
# ---------------------------------------------------------------------------


@router.get(
    "/experiments",
    response_model=ExperimentsResponse,
    summary="Get A/B experiment status",
    responses={403: {"description": "Enterprise tier required"}},
)
async def get_experiments(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentsResponse:
    """Return active and historical A/B experiments."""
    _require_enterprise(ctx)

    active_exp_id = (
        ctx.preferences.fine_tuning_ab_experiment_id if ctx.preferences else None
    )

    service = _get_service()
    experiments: list[dict[str, Any]] = []
    if active_exp_id:
        exp = await service.get_experiment(active_exp_id)
        if exp:
            experiments.append(exp.model_dump())

    return ExperimentsResponse(
        active_experiment_id=active_exp_id,
        experiments=experiments,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/fine-tuning/rollback — Rollback to base model
# ---------------------------------------------------------------------------


@router.post(
    "/rollback",
    response_model=RollbackResponse,
    summary="Rollback to base model",
    responses={403: {"description": "Enterprise tier required"}},
)
async def rollback_model(
    ctx: TenantContext = Depends(get_tenant_context),
) -> RollbackResponse:
    """Rollback to the base model, deactivating any fine-tuned model."""
    _require_enterprise(ctx)

    previous_model = (
        ctx.preferences.fine_tuning_active_model_id if ctx.preferences else None
    )

    service = _get_service()
    await service._update_preferences(
        ctx.tenant_id,
        fine_tuning_active_model_id=None,
        fine_tuning_active_model_version=None,
        fine_tuning_ab_experiment_id=None,
    )

    logger.info(
        "Model rolled back: tenant=%s previous_model=%s",
        ctx.tenant_id, previous_model,
    )

    return RollbackResponse(
        message="Rolled back to base model successfully",
        previous_model_id=previous_model,
    )
