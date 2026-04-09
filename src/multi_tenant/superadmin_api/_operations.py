# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Superadmin API -- Incidents, alerts, MFA, cost analytics, abuse detection.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import UTC
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HV-5: Incident Management — response models
# ---------------------------------------------------------------------------


class IncidentUpdateModel(CamelCaseModel):
    """Single update entry on an incident."""

    timestamp: str
    status: str
    message: str
    author: str = "system"


class IncidentModel(CamelCaseModel):
    """Full incident document for API response."""

    incident_id: str
    title: str
    description: str = ""
    status: str
    severity: str
    affected_services: list[str] = Field(default_factory=list)
    updates: list[IncidentUpdateModel] = Field(default_factory=list)
    created_at: str
    updated_at: str
    resolved_at: str | None = None
    created_by: str = "system"


class IncidentListResponse(CamelCaseModel):
    """List of incidents."""

    incidents: list[IncidentModel] = Field(default_factory=list)
    total: int = 0


class CreateIncidentRequest(CamelCaseModel):
    """Request body for creating an incident."""

    title: str
    description: str = ""
    severity: str = "minor"
    affected_services: list[str] = Field(default_factory=list)


class AddIncidentUpdateRequest(CamelCaseModel):
    """Request body for adding an update to an incident."""

    status: str
    message: str


# ---------------------------------------------------------------------------
# HV-5: Incident Management — endpoints
# ---------------------------------------------------------------------------


def _incident_to_model(doc: dict[str, Any]) -> IncidentModel:
    """Convert a Cosmos incident document to an API model."""
    updates = [
        IncidentUpdateModel(
            timestamp=u.get("timestamp", ""),
            status=u.get("status", ""),
            message=u.get("message", ""),
            author=u.get("author", "system"),
        )
        for u in doc.get("updates", [])
    ]
    return IncidentModel(
        incident_id=doc.get("incident_id", ""),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        status=doc.get("status", "investigating"),
        severity=doc.get("severity", "minor"),
        affected_services=doc.get("affected_services", []),
        updates=updates,
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        resolved_at=doc.get("resolved_at"),
        created_by=doc.get("created_by", "system"),
    )


@router.get(
    "/incidents",
    response_model=IncidentListResponse,
    summary="List incidents",
    description="List all incidents (active first, then resolved).",
    status_code=200,
)
async def list_incidents(

    limit: int = Query(50, ge=1, le=200, description="Max incidents to return"),
) -> IncidentListResponse:
    """List all incidents."""
    if _state._incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    docs = await _state._incident_repo.list_all(limit=limit)
    incidents = [_incident_to_model(d) for d in docs]
    return IncidentListResponse(incidents=incidents, total=len(incidents))


@router.post(
    "/incidents",
    response_model=IncidentModel,
    summary="Create a new incident",
    status_code=201,
)
async def create_incident(
    body: CreateIncidentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> IncidentModel:
    """Create a new incident."""
    if _state._incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    created_by = ctx.team_member_email or "superadmin"
    doc = await _state._incident_repo.create_incident(
        title=body.title,
        description=body.description,
        severity=body.severity,
        affected_services=body.affected_services,
        created_by=created_by,
    )
    return _incident_to_model(doc)


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentModel,
    summary="Get a single incident",
    status_code=200,
)
async def get_incident(
    incident_id: str,

) -> IncidentModel:
    """Get a single incident by ID."""
    if _state._incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    doc = await _state._incident_repo.find_incident(incident_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_to_model(doc)


@router.post(
    "/incidents/{incident_id}/update",
    response_model=IncidentModel,
    summary="Add status update to an incident",
    status_code=200,
)
async def add_incident_update(
    incident_id: str,
    body: AddIncidentUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> IncidentModel:
    """Add a status update to an incident."""
    if _state._incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    # Find existing incident
    existing = await _state._incident_repo.find_incident(incident_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    author = ctx.team_member_email or "superadmin"
    doc = await _state._incident_repo.add_update(
        incident_id=incident_id,
        current_status=existing["status"],
        new_status=body.status,
        message=body.message,
        author=author,
    )
    if doc is None:
        raise HTTPException(status_code=500, detail="Failed to update incident")
    return _incident_to_model(doc)


@router.post(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentModel,
    summary="Resolve an incident",
    status_code=200,
)
async def resolve_incident(
    incident_id: str,
    message: str = Body("Incident resolved", embed=True),
    ctx: TenantContext = Depends(get_tenant_context),
) -> IncidentModel:
    """Mark an incident as resolved."""
    if _state._incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    existing = await _state._incident_repo.find_incident(incident_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if existing["status"] == "resolved":
        raise HTTPException(status_code=400, detail="Incident is already resolved")

    author = ctx.team_member_email or "superadmin"
    doc = await _state._incident_repo.resolve_incident(
        incident_id=incident_id,
        current_status=existing["status"],
        message=message,
        author=author,
    )
    if doc is None:
        raise HTTPException(status_code=500, detail="Failed to resolve incident")
    return _incident_to_model(doc)


# ---------------------------------------------------------------------------
# RB-4: Alert Rules — response models
# ---------------------------------------------------------------------------


class AlertConditionModel(CamelCaseModel):
    """Condition for an alert rule."""

    metric: str = ""
    operator: str = "gt"
    threshold: float = 0


class AlertRuleModel(CamelCaseModel):
    """Alert rule for API response."""

    rule_id: str
    rule_type: str
    name: str
    description: str = ""
    enabled: bool = True
    condition: AlertConditionModel = Field(default_factory=AlertConditionModel)
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    runbook_url: str = ""
    created_at: str = ""
    updated_at: str = ""


class AlertRuleListResponse(CamelCaseModel):
    """List of alert rules."""

    rules: list[AlertRuleModel] = Field(default_factory=list)
    total: int = 0


class CreateAlertRuleRequest(CamelCaseModel):
    """Request body for creating an alert rule."""

    name: str
    rule_type: str
    description: str = ""
    condition: AlertConditionModel = Field(default_factory=AlertConditionModel)
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    runbook_url: str = ""


class UpdateAlertRuleRequest(CamelCaseModel):
    """Request body for updating an alert rule."""

    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    condition: AlertConditionModel | None = None
    notification_channels: list[str] | None = None
    cooldown_minutes: int | None = None
    runbook_url: str | None = None


class AlertHistoryItemModel(CamelCaseModel):
    """Single alert history entry."""

    alert_id: str = ""
    alert_date: str = ""
    rule_id: str = ""
    rule_name: str = ""
    rule_type: str = ""
    tenant_id: str = ""
    triggered_at: str = ""
    resolved_at: str | None = None
    severity: str = "warning"
    message: str = ""
    metric_value: float = 0
    threshold_value: float = 0
    acknowledged: bool = False
    acknowledged_by: str | None = None


class AlertHistoryResponse(CamelCaseModel):
    """Alert history response."""

    alerts: list[AlertHistoryItemModel] = Field(default_factory=list)
    total: int = 0


class DeleteAlertRuleResponse(CamelCaseModel):
    """Response for DELETE /alerts/rules/{rule_id}."""

    deleted: bool
    rule_id: str


class EvaluateAlertsResponse(CamelCaseModel):
    """Response for POST /alerts/evaluate."""

    evaluated: bool
    message: str = ""
    triggered: int = 0
    total_rules: int = 0


class MfaActionResponse(CamelCaseModel):
    """Generic MFA action response (confirm/disable)."""

    confirmed: bool | None = None
    disabled: bool | None = None
    message: str


class AbuseFlagResponse(CamelCaseModel):
    """Response for POST /abuse/tenant/{tenant_id}/flag."""

    tenant_id: str
    flagged: bool
    updated_at: str


class MessageResponse(CamelCaseModel):
    """Simple message-only response."""

    message: str


# ---------------------------------------------------------------------------
# RB-5: MFA/TOTP — models
# ---------------------------------------------------------------------------


class MfaStatusResponse(CamelCaseModel):
    """MFA enrollment status for the current user."""

    mfa_enabled: bool = False
    enrolled_at: str | None = None
    backup_codes_remaining: int = 0


class MfaEnrollResponse(CamelCaseModel):
    """MFA enrollment response with QR code and backup codes."""

    qr_code_data_url: str
    provisioning_uri: str
    backup_codes: list[str] = Field(default_factory=list)
    backup_code_hashes: list[str] = Field(default_factory=list)


class MfaConfirmRequest(CamelCaseModel):
    """Confirm MFA enrollment with the first TOTP code."""

    code: str
    backup_code_hashes: list[str] = Field(default_factory=list)


class MfaVerifyRequest(CamelCaseModel):
    """Verify TOTP code at login time."""

    code: str


class MfaVerifyResponse(CamelCaseModel):
    """MFA verification response with session token."""

    mfa_token: str
    backup_codes_remaining: int | None = None


class MfaDisableRequest(CamelCaseModel):
    """Disable MFA (requires valid TOTP code)."""

    code: str


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------


def _rule_to_model(doc: dict[str, Any]) -> AlertRuleModel:
    """Convert a Cosmos alert rule document to an API model."""
    cond = doc.get("condition", {})
    return AlertRuleModel(
        rule_id=doc.get("rule_id", ""),
        rule_type=doc.get("rule_type", ""),
        name=doc.get("name", ""),
        description=doc.get("description", ""),
        enabled=doc.get("enabled", True),
        condition=AlertConditionModel(
            metric=cond.get("metric", ""),
            operator=cond.get("operator", "gt"),
            threshold=cond.get("threshold", 0),
        ),
        notification_channels=doc.get("notification_channels", []),
        cooldown_minutes=doc.get("cooldown_minutes", 60),
        runbook_url=doc.get("runbook_url", ""),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
    )


def _history_to_model(doc: dict[str, Any]) -> AlertHistoryItemModel:
    """Convert a Cosmos alert history document to an API model."""
    return AlertHistoryItemModel(
        alert_id=doc.get("id", ""),
        alert_date=doc.get("alert_date", ""),
        rule_id=doc.get("rule_id", ""),
        rule_name=doc.get("rule_name", ""),
        rule_type=doc.get("rule_type", ""),
        tenant_id=doc.get("tenant_id", ""),
        triggered_at=doc.get("triggered_at", ""),
        resolved_at=doc.get("resolved_at"),
        severity=doc.get("severity", "warning"),
        message=doc.get("message", ""),
        metric_value=doc.get("metric_value", 0),
        threshold_value=doc.get("threshold_value", 0),
        acknowledged=doc.get("acknowledged", False),
        acknowledged_by=doc.get("acknowledged_by"),
    )



@router.get(
    "/alerts/rules",
    response_model=AlertRuleListResponse,
    summary="List alert rules",
    status_code=200,
)
async def list_alert_rules(

) -> AlertRuleListResponse:
    """List all alert rules."""
    if _state._alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    docs = await _state._alert_rule_repo.list_all()
    rules = [_rule_to_model(d) for d in docs]
    return AlertRuleListResponse(rules=rules, total=len(rules))


@router.post(
    "/alerts/rules",
    response_model=AlertRuleModel,
    summary="Create alert rule",
    status_code=201,
)
async def create_alert_rule(
    body: CreateAlertRuleRequest,

) -> AlertRuleModel:
    """Create a new alert rule."""
    if _state._alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    doc = await _state._alert_rule_repo.create_rule(
        name=body.name,
        rule_type=body.rule_type,
        description=body.description,
        condition=body.condition.model_dump() if body.condition else None,
        notification_channels=body.notification_channels,
        cooldown_minutes=body.cooldown_minutes,
        runbook_url=body.runbook_url,
    )
    return _rule_to_model(doc)


@router.put(
    "/alerts/rules/{rule_id}",
    response_model=AlertRuleModel,
    summary="Update alert rule",
    status_code=200,
)
async def update_alert_rule(
    rule_id: str,
    body: UpdateAlertRuleRequest,

) -> AlertRuleModel:
    """Update an existing alert rule."""
    if _state._alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    # Find the rule first to get the rule_type (partition key)
    existing = await _state._alert_rule_repo.find_rule(rule_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")

    updates: dict[str, Any] = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.enabled is not None:
        updates["enabled"] = body.enabled
    if body.condition is not None:
        updates["condition"] = body.condition.model_dump()
    if body.notification_channels is not None:
        updates["notification_channels"] = body.notification_channels
    if body.cooldown_minutes is not None:
        updates["cooldown_minutes"] = body.cooldown_minutes
    if body.runbook_url is not None:
        updates["runbook_url"] = body.runbook_url

    if not updates:
        return _rule_to_model(existing)

    doc = await _state._alert_rule_repo.update_rule(
        rule_id=rule_id,
        rule_type=existing["rule_type"],
        updates=updates,
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return _rule_to_model(doc)


@router.delete(
    "/alerts/rules/{rule_id}",
    response_model=DeleteAlertRuleResponse,
    summary="Delete alert rule",
    status_code=200,
)
async def delete_alert_rule(
    rule_id: str,

) -> DeleteAlertRuleResponse:
    """Delete an alert rule."""
    if _state._alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    existing = await _state._alert_rule_repo.find_rule(rule_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")

    deleted = await _state._alert_rule_repo.delete_rule(
        rule_id=rule_id,
        rule_type=existing["rule_type"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return DeleteAlertRuleResponse(deleted=True, rule_id=rule_id)


# ---------------------------------------------------------------------------
# RB-4: Alert History — endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/alerts/history",
    response_model=AlertHistoryResponse,
    summary="Alert firing history",
    status_code=200,
)
async def alert_history(

    days: int = Query(7, ge=1, le=90, description="Days of history"),
    limit: int = Query(100, ge=1, le=500, description="Max alerts to return"),
) -> AlertHistoryResponse:
    """List recent alert history."""
    if _state._alert_history_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    docs = await _state._alert_history_repo.list_recent(days=days, limit=limit)
    alerts = [_history_to_model(d) for d in docs]
    return AlertHistoryResponse(alerts=alerts, total=len(alerts))


@router.post(
    "/alerts/history/{alert_id}/acknowledge",
    response_model=AlertHistoryItemModel,
    summary="Acknowledge an alert",
    status_code=200,
)
async def acknowledge_alert(
    alert_id: str,
    alert_date: str = Query(..., description="Alert date (YYYY-MM-DD partition key)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AlertHistoryItemModel:
    """Acknowledge an alert firing event."""
    if _state._alert_history_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    ack_by = ctx.team_member_email or "superadmin"
    doc = await _state._alert_history_repo.acknowledge(
        alert_id=alert_id,
        alert_date=alert_date,
        acknowledged_by=ack_by,
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _history_to_model(doc)


@router.post(
    "/alerts/evaluate",
    response_model=EvaluateAlertsResponse,
    summary="Force evaluate all alert rules",
    status_code=200,
)
async def evaluate_alerts(

) -> EvaluateAlertsResponse:
    """Manually trigger evaluation of all enabled alert rules."""
    try:
        from src.multi_tenant.alert_engine import get_alert_engine

        engine = get_alert_engine()
        result = await engine.evaluate_all()
        return EvaluateAlertsResponse(
            evaluated=True,
            triggered=result.get("triggered", 0),
            total_rules=result.get("total_rules", 0),
        )
    except ImportError:
        return EvaluateAlertsResponse(evaluated=False, message="Alert engine not yet implemented")
    except Exception as exc:
        logger.warning("Alert evaluation failed: %s", exc)
        return EvaluateAlertsResponse(evaluated=False, message=str(exc))



# ---------------------------------------------------------------------------
# RB-5: MFA/TOTP — endpoints
# ---------------------------------------------------------------------------


def _get_mfa_svc():
    """Lazy import to avoid circular dependencies at module load time."""
    from src.multi_tenant.mfa_totp import get_mfa_service

    return get_mfa_service()


async def _get_team_member(ctx: TenantContext) -> dict[str, Any]:
    """Fetch the full team member document for the authenticated user.

    MFA endpoints need the full document (mfa_enabled, backup code hashes, etc.)
    but TenantContext only carries scalar identity fields.
    """
    if ctx.is_platform_admin:
        raise HTTPException(
            status_code=501,
            detail="MFA not yet supported for platform admins",
        )
    if not ctx.team_member_id:
        raise HTTPException(status_code=401, detail="No authenticated team member")
    from src.multi_tenant.repositories.team import TeamMemberRepository

    repo = TeamMemberRepository()
    try:
        return await repo.read(ctx.tenant_id, ctx.team_member_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Team member not found")


@router.get(
    "/mfa/status",
    response_model=MfaStatusResponse,
    summary="MFA enrollment status",
    status_code=200,
)
async def mfa_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaStatusResponse:
    """Get MFA enrollment status for the current authenticated user."""
    # Platform admins don't have MFA yet — return unenrolled status
    if ctx.is_platform_admin:
        return MfaStatusResponse(
            mfa_enabled=False,
            enrolled_at=None,
            backup_codes_remaining=0,
        )
    member = await _get_team_member(ctx)

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    status = await svc.get_enrollment_status(member)
    return MfaStatusResponse(
        mfa_enabled=status["mfa_enabled"],
        enrolled_at=status.get("enrolled_at"),
        backup_codes_remaining=status.get("backup_codes_remaining", 0),
    )


@router.post(
    "/mfa/enroll",
    response_model=MfaEnrollResponse,
    summary="Start MFA enrollment",
    status_code=200,
)
async def mfa_enroll(
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaEnrollResponse:
    """Start MFA enrollment — generates TOTP secret, QR code, and backup codes.

    The secret is stored in Key Vault immediately. Enrollment is not
    confirmed until the user provides their first valid TOTP code via
    the ``/mfa/confirm`` endpoint.
    """
    member = await _get_team_member(ctx)

    if member.get("mfa_enabled", False):
        raise HTTPException(status_code=409, detail="MFA is already enabled")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.start_enrollment(member)
    return MfaEnrollResponse(
        qr_code_data_url=result["qr_code_data_url"],
        provisioning_uri=result["provisioning_uri"],
        backup_codes=result["backup_codes"],
        backup_code_hashes=result["backup_code_hashes"],
    )


@router.post(
    "/mfa/confirm",
    response_model=MfaActionResponse,
    summary="Confirm MFA enrollment",
    status_code=200,
)
async def mfa_confirm(
    body: MfaConfirmRequest = Body(...),
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaActionResponse:
    """Confirm MFA enrollment with the first valid TOTP code.

    After this succeeds, MFA is required for all subsequent logins.
    """
    member = await _get_team_member(ctx)

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    confirmed = await svc.confirm_enrollment(
        member=member,
        code=body.code,
        backup_code_hashes=body.backup_code_hashes,
    )
    if not confirmed:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    return MfaActionResponse(confirmed=True, message="MFA enrollment confirmed")


@router.post(
    "/mfa/verify",
    response_model=MfaVerifyResponse,
    summary="Verify TOTP code at login",
    status_code=200,
)
async def mfa_verify(
    body: MfaVerifyRequest = Body(...),
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaVerifyResponse:
    """Verify a TOTP code at login time and return an MFA session token.

    The returned token should be included in subsequent requests as
    the ``X-MFA-Token`` header.
    """
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled for this user")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.verify_code(member, body.code)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    return MfaVerifyResponse(mfa_token=result["mfa_token"])


@router.post(
    "/mfa/disable",
    response_model=MfaActionResponse,
    summary="Disable MFA",
    status_code=200,
)
async def mfa_disable(
    body: MfaDisableRequest = Body(...),
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaActionResponse:
    """Disable MFA for the current user. Requires a valid TOTP code."""
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    disabled = await svc.disable_mfa(member, body.code)
    if not disabled:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    return MfaActionResponse(disabled=True, message="MFA has been disabled")


@router.post(
    "/mfa/backup-verify",
    response_model=MfaVerifyResponse,
    summary="Verify backup code at login",
    status_code=200,
)
async def mfa_backup_verify(
    body: MfaVerifyRequest = Body(...),
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaVerifyResponse:
    """Verify a backup code at login time. The backup code is consumed.

    Returns an MFA session token and the number of remaining backup codes.
    """
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled for this user")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.verify_backup(member, body.code)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid backup code")

    return MfaVerifyResponse(
        mfa_token=result["mfa_token"],
        backup_codes_remaining=result.get("backup_codes_remaining"),
    )


# ===========================================================================
# Cost Analytics (WI #88)
# ===========================================================================



class CostBreakdownModel(CamelCaseModel):
    """Per-tenant cost breakdown by category."""

    ai_tokens: float = 0.0
    cosmos_db: float = 0.0
    storage: float = 0.0
    compute: float = 0.0
    total: float = 0.0


class TenantCostProfileModel(CamelCaseModel):
    """Cost attribution for a single tenant over a period."""

    tenant_id: str
    tier: str | None = None
    period_start: str = ""
    period_end: str = ""
    conversation_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    article_count: int = 0
    cost_breakdown: CostBreakdownModel = Field(default_factory=CostBreakdownModel)
    cost_per_conversation: float = 0.0
    cost_share_pct: float = 0.0


class CostOverviewResponse(CamelCaseModel):
    """Platform-wide cost overview with per-tenant breakdown."""

    period_start: str = ""
    period_end: str = ""
    total_platform_cost: float = 0.0
    total_conversations: int = 0
    total_tenants: int = 0
    avg_cost_per_tenant: float = 0.0
    avg_cost_per_conversation: float = 0.0
    tenants: list[TenantCostProfileModel] = Field(default_factory=list)
    cost_by_tier: dict[str, float] = Field(default_factory=dict)


# Token pricing (Azure OpenAI gpt-4o-mini, per 1M tokens)
_INPUT_TOKEN_COST_PER_M = 0.15
_OUTPUT_TOKEN_COST_PER_M = 0.60
# Cosmos DB serverless: ~$0.25 per 1M RU
_COSMOS_RU_COST_PER_CONV = 0.0003  # estimated RU per conversation
# Flat compute share per conversation (container app amortized)
_COMPUTE_COST_PER_CONV = 0.0002
# Storage: negligible for conversations, set per article
_STORAGE_COST_PER_ARTICLE = 0.0001


@router.get(
    "/costs",
    response_model=CostOverviewResponse,
    summary="Cost analytics — per-tenant cost attribution",
    status_code=200,
)
async def get_cost_analytics(
    days: int = Query(default=30, ge=1, le=365),
    ctx: TenantContext = Depends(get_tenant_context),
) -> CostOverviewResponse:
    """Compute estimated per-tenant costs based on conversation volume and token usage."""
    from datetime import datetime, timedelta

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(UTC)
    period_start = (now - timedelta(days=days)).isoformat()
    period_end = now.isoformat()

    # Query all active tenants
    tenant_ids: list[str] = []
    try:
        tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
    except Exception:
        pass

    tenant_profiles: list[TenantCostProfileModel] = []
    total_platform_cost = 0.0
    total_conversations = 0
    cost_by_tier: dict[str, float] = {}

    for tid in tenant_ids:
        try:
            # Get tenant tier
            tenant_doc = await _state._tenant_repo.read(tid, tid)
            tier = tenant_doc.get("tier", "starter") if tenant_doc else "starter"

            # Count conversations in period
            conv_count = 0
            total_input = 0
            total_output = 0
            if _state._conv_repo:
                try:
                    # SPEC-1843 / WI-1609: Never select c.messages —
                    # use only c.message_count for cost estimation.
                    convs = await _state._conv_repo.query(
                        tid,
                        "SELECT c.id, c.message_count, c.started_at FROM c "
                        "WHERE c.started_at >= @start "
                        "ORDER BY c.started_at DESC "
                        "OFFSET 0 LIMIT 500",
                        [{"name": "@start", "value": period_start}],
                    )
                    conv_count = len(convs)
                    # Estimate tokens from message_count (avg ~150 tokens/message)
                    for c in convs:
                        msg_count = c.get("message_count", 0)
                        total_input += int(msg_count * 75)   # customer msgs
                        total_output += int(msg_count * 150)  # AI responses
                except Exception:
                    pass

            # Count KB articles
            article_count = 0
            try:
                from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

                kb_repo = KnowledgeBaseRepository()
                articles = await kb_repo.query(
                    tid,
                    "SELECT VALUE COUNT(1) FROM c",
                    [],
                )
                article_count = articles[0] if articles else 0
            except Exception:
                pass

            # Calculate cost breakdown
            ai_cost = (
                (total_input / 1_000_000) * _INPUT_TOKEN_COST_PER_M
                + (total_output / 1_000_000) * _OUTPUT_TOKEN_COST_PER_M
            )
            cosmos_cost = conv_count * _COSMOS_RU_COST_PER_CONV
            storage_cost = article_count * _STORAGE_COST_PER_ARTICLE
            compute_cost = conv_count * _COMPUTE_COST_PER_CONV
            total_cost = ai_cost + cosmos_cost + storage_cost + compute_cost

            profile = TenantCostProfileModel(
                tenant_id=tid,
                tier=tier,
                period_start=period_start,
                period_end=period_end,
                conversation_count=conv_count,
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                article_count=article_count,
                cost_breakdown=CostBreakdownModel(
                    ai_tokens=round(ai_cost, 6),
                    cosmos_db=round(cosmos_cost, 6),
                    storage=round(storage_cost, 6),
                    compute=round(compute_cost, 6),
                    total=round(total_cost, 6),
                ),
                cost_per_conversation=round(total_cost / max(conv_count, 1), 6),
                cost_share_pct=0.0,  # computed after totals
            )
            tenant_profiles.append(profile)
            total_platform_cost += total_cost
            total_conversations += conv_count
            cost_by_tier[tier] = cost_by_tier.get(tier, 0.0) + total_cost
        except Exception:
            logger.debug("Cost analytics failed for tenant %s", tid)

    # Compute cost share percentages
    for p in tenant_profiles:
        if total_platform_cost > 0:
            p.cost_share_pct = round(
                (p.cost_breakdown.total / total_platform_cost) * 100, 1,
            )

    # Round tier costs
    cost_by_tier = {k: round(v, 4) for k, v in cost_by_tier.items()}

    return CostOverviewResponse(
        period_start=period_start,
        period_end=period_end,
        total_platform_cost=round(total_platform_cost, 4),
        total_conversations=total_conversations,
        total_tenants=len(tenant_profiles),
        avg_cost_per_tenant=round(
            total_platform_cost / max(len(tenant_profiles), 1), 4,
        ),
        avg_cost_per_conversation=round(
            total_platform_cost / max(total_conversations, 1), 4,
        ),
        tenants=tenant_profiles,
        cost_by_tier=cost_by_tier,
    )


# ===========================================================================
# Abuse Detection (WI #89)
# ===========================================================================


class AbuseSignalModel(CamelCaseModel):
    """A single detected abuse signal."""

    tenant_id: str
    signal_type: str
    severity: str
    description: str
    detected_at: str
    metric_value: float = 0.0
    threshold: float = 0.0


class TenantAbuseProfileModel(CamelCaseModel):
    """Abuse profile for a single tenant."""

    tenant_id: str
    is_flagged: bool = False
    flagged_at: str | None = None
    flagged_by: str | None = None
    signals: list[AbuseSignalModel] = Field(default_factory=list)
    risk_score: int = 0


class AbuseOverviewResponse(CamelCaseModel):
    """Platform-wide abuse scan results.

    SPEC-1843 v6 boundary: per-tenant abuse flags are TENANCY MANAGEMENT
    data — the operator needs to identify which tenant to throttle or
    contact.  ``high_risk_tenants`` restored with tenant_id + risk_score
    + signal types only (no conversation content, no customer PII).

    WI-1641: ``high_risk_tenants`` restored after S137 audit found WI-1610
    over-applied the ZK mandate.
    """

    total_tenants_scanned: int = 0
    flagged_count: int = 0
    high_risk_count: int = 0
    high_risk_tenants: list[TenantAbuseProfileModel] = Field(default_factory=list)
    signals_by_type: dict[str, int] = Field(default_factory=dict)


class FlagTenantRequest(BaseModel):
    """Request body for POST /api/superadmin/abuse/tenant/{tenant_id}/flag."""

    flagged: bool


# Abuse detection thresholds
_RATE_ANOMALY_THRESHOLD = 100     # conversations per day
_VOLUME_SPIKE_MULTIPLIER = 3.0    # 3x above normal
_ERROR_RATE_THRESHOLD = 0.25      # 25% error rate
_TOKEN_EXHAUSTION_THRESHOLD = 500_000  # tokens per day


@router.get(
    "/abuse/signals",
    response_model=AbuseOverviewResponse,
    summary="Abuse detection — cross-tenant anomaly scan",
    status_code=200,
)
async def get_abuse_signals(
    ctx: TenantContext = Depends(get_tenant_context),
) -> AbuseOverviewResponse:
    """Scan all active tenants for abuse signals and anomalous usage patterns."""
    from datetime import datetime, timedelta

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(UTC)
    day_ago = (now - timedelta(days=1)).isoformat()

    tenant_ids: list[str] = []
    try:
        tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
    except Exception:
        pass

    high_risk: list[TenantAbuseProfileModel] = []
    signals_by_type: dict[str, int] = {}
    flagged_count = 0

    for tid in tenant_ids:
        try:
            tenant_doc = await _state._tenant_repo.read(tid, tid)
            is_flagged = tenant_doc.get("abuse_flagged", False) if tenant_doc else False
            flagged_at = tenant_doc.get("abuse_flagged_at") if tenant_doc else None
            flagged_by = tenant_doc.get("abuse_flagged_by") if tenant_doc else None

            if is_flagged:
                flagged_count += 1

            signals: list[AbuseSignalModel] = []

            # Check conversation volume (last 24h)
            daily_convs = 0
            error_convs = 0
            if _state._conv_repo:
                try:
                    results = await _state._conv_repo.query(
                        tid,
                        "SELECT c.status FROM c WHERE c.started_at >= @start",
                        [{"name": "@start", "value": day_ago}],
                    )
                    daily_convs = len(results)
                    error_convs = sum(
                        1 for r in results if r.get("status") == "error"
                    )
                except Exception:
                    pass

            # Rate anomaly: too many conversations per day
            if daily_convs > _RATE_ANOMALY_THRESHOLD:
                sig = AbuseSignalModel(
                    tenant_id=tid,
                    signal_type="rate_anomaly",
                    severity="high" if daily_convs > _RATE_ANOMALY_THRESHOLD * 2 else "medium",
                    description=f"{daily_convs} conversations in 24h (threshold: {_RATE_ANOMALY_THRESHOLD})",
                    detected_at=now.isoformat(),
                    metric_value=float(daily_convs),
                    threshold=float(_RATE_ANOMALY_THRESHOLD),
                )
                signals.append(sig)
                signals_by_type["rate_anomaly"] = signals_by_type.get("rate_anomaly", 0) + 1

            # Error rate: high proportion of error conversations
            if daily_convs >= 10 and error_convs / daily_convs > _ERROR_RATE_THRESHOLD:
                error_rate = error_convs / daily_convs
                sig = AbuseSignalModel(
                    tenant_id=tid,
                    signal_type="error_rate",
                    severity="critical" if error_rate > 0.5 else "high",
                    description=f"{error_rate:.0%} error rate ({error_convs}/{daily_convs})",
                    detected_at=now.isoformat(),
                    metric_value=round(error_rate, 3),
                    threshold=_ERROR_RATE_THRESHOLD,
                )
                signals.append(sig)
                signals_by_type["error_rate"] = signals_by_type.get("error_rate", 0) + 1

            # Compute risk score (0-100)
            risk_score = 0
            for s in signals:
                if s.severity == "critical":
                    risk_score += 40
                elif s.severity == "high":
                    risk_score += 25
                elif s.severity == "medium":
                    risk_score += 15
                else:
                    risk_score += 5
            if is_flagged:
                risk_score += 20
            risk_score = min(risk_score, 100)

            # Include in high-risk list if score >= 25 or flagged
            if risk_score >= 25 or is_flagged:
                profile = TenantAbuseProfileModel(
                    tenant_id=tid,
                    is_flagged=is_flagged,
                    flagged_at=flagged_at,
                    flagged_by=flagged_by,
                    signals=signals,
                    risk_score=risk_score,
                )
                high_risk.append(profile)
        except Exception:
            logger.debug("Abuse scan failed for tenant %s", tid)

    # SPEC-1843 v6: per-tenant abuse flags are tenancy management data
    # (operator needs to identify which tenant to throttle/contact).
    # WI-1641: high_risk_tenants restored after S137 over-application audit.
    return AbuseOverviewResponse(
        total_tenants_scanned=len(tenant_ids),
        flagged_count=flagged_count,
        high_risk_count=len(high_risk),
        high_risk_tenants=high_risk,
        signals_by_type=signals_by_type,
    )


@router.post(
    "/abuse/tenant/{tenant_id}/flag",
    response_model=AbuseFlagResponse,
    summary="Flag or unflag a tenant for abuse review",
    status_code=200,
)
async def toggle_abuse_flag(
    tenant_id: str,
    body: FlagTenantRequest = Body(...),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AbuseFlagResponse:
    """Flag or unflag a tenant for manual abuse review."""
    from datetime import datetime

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now_iso = datetime.now(UTC).isoformat()
    actor = ctx.user_id if hasattr(ctx, "user_id") else "superadmin"

    try:
        operations = [
            {"op": "set", "path": "/abuse_flagged", "value": body.flagged},
            {"op": "set", "path": "/abuse_flagged_at", "value": now_iso if body.flagged else None},
            {"op": "set", "path": "/abuse_flagged_by", "value": actor if body.flagged else None},
        ]
        await _state._tenant_repo.patch(
            tenant_id=tenant_id,
            document_id=tenant_id,
            operations=operations,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update flag")

    # Audit log
    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                tenant_id=tenant_id,
                event_type=AuditEventType.SECURITY_EVENT,
                actor_id=actor,
                resource_type="tenant",
                resource_id=tenant_id,
                details={
                    "action": "abuse_flag_toggled",
                    "flagged": body.flagged,
                },
            )
        except Exception:
            pass

    return AbuseFlagResponse(
        tenant_id=tenant_id,
        flagged=body.flagged,
        updated_at=now_iso,
    )

