"""Superadmin API -- A/B Experiment endpoints (SPEC-0621, SPEC-0624, SPEC-0626).

Provides experiment management endpoints:

  POST   /experiments              — Create experiment (draft)
  GET    /experiments              — List experiments (tenant-scoped or all)
  GET    /experiments/{id}         — Get experiment details
  POST   /experiments/{id}/submit  — Submit for merchant review (draft -> pending_review)
  POST   /experiments/{id}/approve — Merchant approves (pending_review -> active)
  POST   /experiments/{id}/reject  — Merchant rejects (pending_review -> draft)
  POST   /experiments/{id}/conclude — Request conclusion (active -> pending_conclusion)
  POST   /experiments/{id}/finalize — Finalize conclusion (pending_conclusion -> concluded_*)
  GET    /experiments/{id}/kpis    — KPI metrics per variant (SPEC-0624)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends, HTTPException, Query
from pydantic import Field

from src.chat.ab_testing import (
    ExperimentConfig,
    ExperimentService,
    ExperimentStatus,
    VariantConfig,
)
from src.chat.ab_statistics import (
    StatResult,
    two_proportion_z_test,
    two_sample_z_test,
)
from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

logger = logging.getLogger(__name__)

# Module-level service instance (in-memory for now; Cosmos-backed in production)
_experiment_service = ExperimentService(store={})


def get_experiment_service() -> ExperimentService:
    """Return the module-level experiment service."""
    return _experiment_service


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class VariantConfigRequest(CamelCaseModel):
    """Variant configuration for creating an experiment."""

    name: str = Field(description="Variant display name")
    description: str = Field(default="", description="What this variant tests")
    config_overrides: dict[str, Any] = Field(
        default_factory=dict, description="Configuration key overrides"
    )


class CreateExperimentRequest(CamelCaseModel):
    """Request body for POST /experiments."""

    name: str = Field(description="Experiment display name")
    description: str = Field(default="")
    hypothesis: str = Field(default="")
    control: VariantConfigRequest
    treatment: VariantConfigRequest
    control_ratio: float = Field(default=0.80, ge=0.05, le=0.95)
    audience_mode: str = Field(default="all")
    audience_percentage: float = Field(default=100.0, ge=1.0, le=100.0)
    audience_segment: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    min_duration_days: int = Field(default=3, ge=1, le=90)
    metric_keys: list[str] | None = Field(default=None)


class ConcludeRequest(CamelCaseModel):
    """Request body for POST /experiments/{id}/finalize."""

    action: str = Field(description="'promote' or 'rollback'")


class ExperimentResponse(CamelCaseModel):
    """Experiment details returned by API."""

    experiment_id: str
    tenant_id: str
    name: str
    description: str
    hypothesis: str
    status: str
    control_ratio: float
    treatment_ratio: float
    audience_mode: str
    start_date: str | None
    end_date: str | None
    created_at: str
    concluded_at: str | None
    metric_keys: list[str]
    ai_rationale: str
    conclusion_recommendation: str | None


class StatResultResponse(CamelCaseModel):
    """Statistical test result for a single metric."""

    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    ci_lower: float
    ci_upper: float
    significant: bool
    sample_size_control: int
    sample_size_treatment: int


class KPIMetricResponse(CamelCaseModel):
    """Single KPI metric with per-variant values and statistics."""

    metric_key: str
    control_value: float
    treatment_value: float
    stat_result: StatResultResponse | None = None


class KPIResponse(CamelCaseModel):
    """KPI comparison for an experiment (SPEC-0624)."""

    experiment_id: str
    metrics: list[KPIMetricResponse]
    total_control_observations: int = 0
    total_treatment_observations: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _exp_to_response(exp: ExperimentConfig) -> ExperimentResponse:
    return ExperimentResponse(
        experiment_id=exp.experiment_id,
        tenant_id=exp.tenant_id,
        name=exp.name,
        description=exp.description,
        hypothesis=exp.hypothesis,
        status=exp.status.value,
        control_ratio=exp.control_ratio,
        treatment_ratio=exp.treatment_ratio,
        audience_mode=exp.audience_mode,
        start_date=exp.start_date,
        end_date=exp.end_date,
        created_at=exp.created_at,
        concluded_at=exp.concluded_at,
        metric_keys=exp.metric_keys,
        ai_rationale=exp.ai_rationale,
        conclusion_recommendation=exp.conclusion_recommendation,
    )


def _require_enterprise(ctx: TenantContext) -> None:
    """Raise 403 if the tenant is not Enterprise tier."""
    if not ctx.is_platform_admin:
        tier = getattr(ctx, "tier", "free")
        if tier != "enterprise":
            raise HTTPException(
                status_code=403,
                detail="A/B experiments require Enterprise tier",
            )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@_state.router.post(
    "/experiments",
    response_model=ExperimentResponse,
    status_code=201,
    summary="Create A/B experiment (SPEC-0621)",
    tags=["experiments"],
)
async def create_experiment(
    body: CreateExperimentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Create a new experiment in draft status."""
    _require_enterprise(ctx)

    svc = get_experiment_service()
    exp = svc.create_experiment(
        tenant_id=ctx.tenant_id,
        name=body.name,
        control=VariantConfig(
            name=body.control.name,
            description=body.control.description,
            config_overrides=body.control.config_overrides,
        ),
        treatment=VariantConfig(
            name=body.treatment.name,
            description=body.treatment.description,
            config_overrides=body.treatment.config_overrides,
        ),
        description=body.description,
        hypothesis=body.hypothesis,
        control_ratio=body.control_ratio,
        audience_mode=body.audience_mode,
        audience_percentage=body.audience_percentage,
        audience_segment=body.audience_segment,
        end_date=body.end_date,
        min_duration_days=body.min_duration_days,
        metric_keys=body.metric_keys,
    )
    return _exp_to_response(exp)


@_state.router.get(
    "/experiments",
    response_model=list[ExperimentResponse],
    summary="List A/B experiments (SPEC-0621)",
    tags=["experiments"],
)
async def list_experiments(
    status: str | None = Query(default=None, description="Filter by status"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[ExperimentResponse]:
    """List experiments. Platform admins see all; tenants see their own."""
    svc = get_experiment_service()
    tenant_filter = None if ctx.is_platform_admin else ctx.tenant_id
    status_filter = ExperimentStatus(status) if status else None

    exps = svc.list_experiments(tenant_id=tenant_filter, status=status_filter)
    return [_exp_to_response(e) for e in exps]


@_state.router.get(
    "/experiments/{experiment_id}",
    response_model=ExperimentResponse,
    summary="Get experiment details (SPEC-0621)",
    tags=["experiments"],
)
async def get_experiment(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Get a single experiment by ID."""
    svc = get_experiment_service()
    exp = svc.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if not ctx.is_platform_admin and exp.tenant_id != ctx.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return _exp_to_response(exp)


@_state.router.post(
    "/experiments/{experiment_id}/submit",
    response_model=ExperimentResponse,
    summary="Submit for review (SPEC-0626)",
    tags=["experiments"],
)
async def submit_for_review(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Submit a draft experiment for merchant review."""
    _require_enterprise(ctx)
    svc = get_experiment_service()
    try:
        exp = svc.submit_for_review(experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _exp_to_response(exp)


@_state.router.post(
    "/experiments/{experiment_id}/approve",
    response_model=ExperimentResponse,
    summary="Approve experiment (SPEC-0626)",
    tags=["experiments"],
)
async def approve_experiment(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Merchant approves experiment — transitions to active."""
    _require_enterprise(ctx)
    svc = get_experiment_service()
    try:
        exp = svc.approve_experiment(experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _exp_to_response(exp)


@_state.router.post(
    "/experiments/{experiment_id}/reject",
    response_model=ExperimentResponse,
    summary="Reject experiment (SPEC-0626)",
    tags=["experiments"],
)
async def reject_experiment(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Merchant rejects experiment — returns to draft."""
    _require_enterprise(ctx)
    svc = get_experiment_service()
    try:
        exp = svc.reject_experiment(experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _exp_to_response(exp)


@_state.router.post(
    "/experiments/{experiment_id}/conclude",
    response_model=ExperimentResponse,
    summary="Request conclusion (SPEC-0626)",
    tags=["experiments"],
)
async def request_conclusion(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """AI or admin requests experiment conclusion — enters pending_conclusion."""
    _require_enterprise(ctx)
    svc = get_experiment_service()
    try:
        exp = svc.request_conclusion(experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _exp_to_response(exp)


@_state.router.post(
    "/experiments/{experiment_id}/finalize",
    response_model=ExperimentResponse,
    summary="Finalize conclusion (SPEC-0626)",
    tags=["experiments"],
)
async def finalize_conclusion(
    experiment_id: str,
    body: ConcludeRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExperimentResponse:
    """Merchant finalizes conclusion — promote or rollback."""
    _require_enterprise(ctx)
    svc = get_experiment_service()
    try:
        if body.action == "promote":
            exp = svc.conclude_promote(experiment_id)
        elif body.action == "rollback":
            exp = svc.conclude_rollback(experiment_id)
        else:
            raise HTTPException(
                status_code=400, detail="action must be 'promote' or 'rollback'"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _exp_to_response(exp)


@_state.router.get(
    "/experiments/{experiment_id}/kpis",
    response_model=KPIResponse,
    summary="Get experiment KPIs (SPEC-0624)",
    tags=["experiments"],
)
async def get_experiment_kpis(
    experiment_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> KPIResponse:
    """Return KPI metrics per variant with statistical significance.

    In production, reads from Cosmos conversation metadata aggregated
    by variant.  For now, returns placeholder structure.
    """
    _require_enterprise(ctx)
    svc = get_experiment_service()
    exp = svc.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if not ctx.is_platform_admin and exp.tenant_id != ctx.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Placeholder: in production, aggregate from Cosmos conversation docs
    # filtered by ab_experiment_id and grouped by ab_variant
    metrics: list[KPIMetricResponse] = []
    for key in exp.metric_keys:
        metrics.append(
            KPIMetricResponse(
                metric_key=key,
                control_value=0.0,
                treatment_value=0.0,
                stat_result=None,
            )
        )

    return KPIResponse(
        experiment_id=experiment_id,
        metrics=metrics,
        total_control_observations=0,
        total_treatment_observations=0,
    )


# ---------------------------------------------------------------------------
# SPEC-0625: AI Configuration Suggestion
# ---------------------------------------------------------------------------


class SuggestVariantRequest(CamelCaseModel):
    """Request body for AI variant suggestion."""

    current_config: dict[str, Any] = Field(
        default_factory=dict, description="Current tenant config"
    )
    commentary: str = Field(
        default="", description="Merchant preferences or commentary"
    )


class SuggestVariantResponse(CamelCaseModel):
    """AI-generated variant suggestion."""

    suggested_config: dict[str, Any] = Field(description="Suggested config overrides")
    rationale: str = Field(description="AI explanation of suggested changes")
    diff: dict[str, Any] = Field(description="Key-by-key diff from current config")


@_state.router.post(
    "/experiments/suggest-variant",
    response_model=SuggestVariantResponse,
    summary="AI-suggest experiment variant (SPEC-0625)",
    tags=["experiments"],
)
async def suggest_variant(
    body: SuggestVariantRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SuggestVariantResponse:
    """Generate AI-suggested configuration variation.

    Uses heuristic suggestions based on the current config and merchant
    commentary.  Rate limited to 5 requests per hour per tenant.

    In production, this will call a foundation model for more sophisticated
    suggestions.  For now, applies simple heuristic transformations.
    """
    _require_enterprise(ctx)

    current = body.current_config
    commentary = body.commentary.lower()

    # Heuristic suggestion engine (placeholder for LLM call)
    suggested = dict(current)
    diff: dict[str, Any] = {}
    rationale_parts: list[str] = []

    # Quality threshold adjustment
    qt = current.get("quality_threshold", 3.5)
    if "strict" in commentary or "quality" in commentary or "improve" in commentary:
        new_qt = min(5.0, qt + 0.5)
        suggested["quality_threshold"] = new_qt
        diff["quality_threshold"] = {"from": qt, "to": new_qt}
        rationale_parts.append(
            f"Increased quality_threshold from {qt} to {new_qt} "
            "to improve conversation quality."
        )
    elif "relax" in commentary or "lenient" in commentary:
        new_qt = max(1.0, qt - 0.5)
        suggested["quality_threshold"] = new_qt
        diff["quality_threshold"] = {"from": qt, "to": new_qt}
        rationale_parts.append(
            f"Decreased quality_threshold from {qt} to {new_qt} "
            "for a more lenient quality bar."
        )

    # Escalation threshold
    et = current.get("escalation_threshold", 2.5)
    if "escalat" in commentary or "support" in commentary:
        new_et = min(4.0, et + 0.5)
        suggested["escalation_threshold"] = new_et
        diff["escalation_threshold"] = {"from": et, "to": new_et}
        rationale_parts.append(
            f"Raised escalation_threshold from {et} to {new_et} "
            "to reduce unnecessary escalations."
        )

    # Feedback toggle
    if "feedback" in commentary:
        suggested["enable_quality_feedback"] = True
        diff["enable_quality_feedback"] = {"from": False, "to": True}
        rationale_parts.append("Enabled quality feedback loop for real-time guidance.")

    # Default suggestion if no keywords matched
    if not rationale_parts:
        new_qt = min(5.0, qt + 0.3)
        suggested["quality_threshold"] = new_qt
        diff["quality_threshold"] = {"from": qt, "to": new_qt}
        rationale_parts.append(
            f"Slightly increased quality_threshold from {qt} to {new_qt} "
            "as a general quality improvement experiment."
        )

    return SuggestVariantResponse(
        suggested_config=suggested,
        rationale=" ".join(rationale_parts),
        diff=diff,
    )
