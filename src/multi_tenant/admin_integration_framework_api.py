"""Admin Integration Framework API — SPEC-1771 endpoint extensions.

New endpoints for the Integration Framework (SPEC-1761+) that use
IntegrationRegistry instead of the legacy _INTEGRATION_META.

Routes:
    GET  /api/admin/integration-framework/{id}/setup   — Setup instructions + auth URL
    POST /api/admin/integration-framework/{id}/test    — Connection test
    GET  /api/admin/integration-framework/{id}/sync    — Sync status
    POST /api/admin/integration-framework/{id}/sync    — Trigger manual sync
    GET  /api/admin/integration-framework/{id}/logs    — Recent events (paginated)
    GET  /api/admin/integration-framework/{id}/actions — Available actions + HITL config
    PUT  /api/admin/integration-framework/{id}/actions — Update HITL config
    GET  /api/integrations/oauth/callback              — Universal OAuth redirect

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.multi_tenant.middleware import get_tenant_context, TenantContext

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SetupInstructions(BaseModel):
    """Setup instructions for an integration."""

    integration_id: str
    display_name: str
    auth_type: str
    setup_steps: list[str] = Field(default_factory=list)
    auth_url: str | None = None
    required_scopes: list[str] = Field(default_factory=list)
    api_key_header: str = ""
    status: str = "not_connected"


class ConnectionTestResult(BaseModel):
    """Result of testing an integration connection."""

    integration_id: str
    success: bool
    message: str = ""
    elapsed_ms: float = 0.0


class SyncStatus(BaseModel):
    """Current sync status for an integration."""

    integration_id: str
    sync_strategy: str
    last_sync_at: datetime | None = None
    last_sync_status: str = "never"  # never, success, error, in_progress
    items_synced: int = 0
    next_sync_at: datetime | None = None
    error: str = ""


class SyncTriggerResult(BaseModel):
    """Result of manually triggering a sync."""

    integration_id: str
    triggered: bool
    message: str = ""


class EventLogEntry(BaseModel):
    """A single integration event log entry."""

    event_id: str
    integration_id: str
    event_type: str
    timestamp: datetime
    actor: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class EventLogResponse(BaseModel):
    """Paginated event log response."""

    integration_id: str
    events: list[EventLogEntry] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50


class ActionConfig(BaseModel):
    """Available actions and HITL configuration."""

    integration_id: str
    actions: list[dict[str, Any]] = Field(default_factory=list)
    hitl_overrides: dict[str, str] = Field(default_factory=dict)


class HITLUpdateRequest(BaseModel):
    """Request to update HITL configuration."""

    overrides: dict[str, str] = Field(
        default_factory=dict,
        description="action_type -> hitl_policy (always, default, optional, never)",
    )


class OAuthCallbackResponse(BaseModel):
    """Response for OAuth callback."""

    success: bool
    integration_id: str = ""
    message: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_registry():
    """Lazy-import the IntegrationRegistry singleton."""
    from src.integrations.registry import IntegrationRegistry
    return IntegrationRegistry.get_instance()


def _get_action_executor():
    """Lazy-import or create an ActionExecutor."""
    from src.integrations.action_executor import ActionExecutor
    return ActionExecutor()


# Sync state: in-memory for now, production would use Cosmos
_sync_state: dict[tuple[str, str], dict[str, Any]] = {}

# Event log: in-memory for now
_event_log: list[dict[str, Any]] = []


def _record_event(
    integration_id: str,
    tenant_id: str,
    event_type: str,
    *,
    actor: str = "",
    details: dict[str, Any] | None = None,
) -> None:
    """Record an integration event to the log."""
    import uuid
    _event_log.append({
        "event_id": str(uuid.uuid4()),
        "integration_id": integration_id,
        "tenant_id": tenant_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "details": details or {},
    })


# ---------------------------------------------------------------------------
# Router — Integration Framework endpoints
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/admin/integration-framework",
    tags=["admin-integration-framework"],
)


@router.get("/{integration_id}/setup", response_model=SetupInstructions)
async def get_setup_instructions(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Get setup instructions and auth URL for an integration."""
    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    # Build setup steps based on auth type
    auth_type = manifest.auth_type.value
    steps: list[str] = []
    auth_url: str | None = None

    if auth_type in ("oauth2", "oauth2_pkce"):
        steps = [
            f"Click 'Connect' to authorize {manifest.display_name}.",
            "You will be redirected to the provider's authorization page.",
            "Grant the requested permissions.",
            "You will be redirected back automatically.",
        ]
        if manifest.auth_config.authorize_url:
            # Build OAuth URL with state parameter
            from src.integrations.oauth import OAuthManager
            try:
                mgr = OAuthManager()
                auth_url = mgr.get_authorization_url(
                    integration_id=integration_id,
                    tenant_id=ctx.tenant_id,
                    redirect_uri=f"/api/integrations/oauth/callback",
                    scopes=manifest.auth_config.scopes,
                )
            except Exception:
                auth_url = manifest.auth_config.authorize_url
    elif auth_type == "api_key":
        header = manifest.auth_config.api_key_header or "Authorization"
        steps = [
            f"Generate an API key from your {manifest.display_name} account.",
            f"Enter the API key below (sent via {header} header).",
            "Click 'Test Connection' to verify.",
        ]
    elif auth_type == "basic":
        steps = [
            f"Enter your {manifest.display_name} username and password.",
            "Click 'Test Connection' to verify.",
        ]
    elif auth_type == "webhook_only":
        steps = [
            f"Configure a webhook in {manifest.display_name} pointing to your Agent Red endpoint.",
            "Copy the webhook secret and enter it below.",
        ]
    else:
        steps = [f"No authentication required for {manifest.display_name}."]

    return SetupInstructions(
        integration_id=integration_id,
        display_name=manifest.display_name,
        auth_type=auth_type,
        setup_steps=steps,
        auth_url=auth_url,
        required_scopes=list(manifest.auth_config.scopes),
        api_key_header=manifest.auth_config.api_key_header,
    )


@router.post("/{integration_id}/test", response_model=ConnectionTestResult)
async def test_connection(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Test connection to an integration via adapter.health_check()."""
    import time

    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    start = time.monotonic()

    try:
        healthy = await registry.health_check(ctx.tenant_id, integration_id)
        elapsed = (time.monotonic() - start) * 1000

        _record_event(
            integration_id, ctx.tenant_id, "connection_test",
            actor=f"admin:{ctx.tenant_id}",
            details={"success": healthy, "elapsed_ms": round(elapsed, 1)},
        )

        return ConnectionTestResult(
            integration_id=integration_id,
            success=healthy,
            message="Connection successful" if healthy else "Health check failed",
            elapsed_ms=round(elapsed, 1),
        )
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return ConnectionTestResult(
            integration_id=integration_id,
            success=False,
            message=str(exc)[:200],
            elapsed_ms=round(elapsed, 1),
        )


@router.get("/{integration_id}/sync", response_model=SyncStatus)
async def get_sync_status(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Get current sync status for an integration."""
    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    key = (ctx.tenant_id, integration_id)
    state = _sync_state.get(key, {})

    return SyncStatus(
        integration_id=integration_id,
        sync_strategy=manifest.sync_strategy.value,
        last_sync_at=state.get("last_sync_at"),
        last_sync_status=state.get("last_sync_status", "never"),
        items_synced=state.get("items_synced", 0),
        next_sync_at=state.get("next_sync_at"),
        error=state.get("error", ""),
    )


@router.post("/{integration_id}/sync", response_model=SyncTriggerResult)
async def trigger_sync(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Manually trigger a sync for an integration."""
    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    key = (ctx.tenant_id, integration_id)
    state = _sync_state.get(key, {})

    if state.get("last_sync_status") == "in_progress":
        return SyncTriggerResult(
            integration_id=integration_id,
            triggered=False,
            message="Sync already in progress",
        )

    # Mark as in-progress
    _sync_state[key] = {
        **state,
        "last_sync_status": "in_progress",
        "last_sync_at": datetime.now(timezone.utc),
    }

    _record_event(
        integration_id, ctx.tenant_id, "sync_triggered",
        actor=f"admin:{ctx.tenant_id}",
    )

    logger.info(
        "Manual sync triggered: integration=%s tenant=%s",
        integration_id, ctx.tenant_id,
    )

    return SyncTriggerResult(
        integration_id=integration_id,
        triggered=True,
        message="Sync started",
    )


@router.get("/{integration_id}/logs", response_model=EventLogResponse)
async def get_event_logs(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    """Get recent integration events (paginated, max 100 per page)."""
    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    # Filter events for this tenant + integration
    filtered = [
        e for e in _event_log
        if e["integration_id"] == integration_id and e["tenant_id"] == ctx.tenant_id
    ]

    total = len(filtered)
    # Most recent first
    filtered.sort(key=lambda e: e["timestamp"], reverse=True)
    start_idx = (page - 1) * page_size
    page_events = filtered[start_idx:start_idx + page_size]

    return EventLogResponse(
        integration_id=integration_id,
        events=[
            EventLogEntry(
                event_id=e["event_id"],
                integration_id=e["integration_id"],
                event_type=e["event_type"],
                timestamp=e["timestamp"],
                actor=e.get("actor", ""),
                details=e.get("details", {}),
            )
            for e in page_events
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{integration_id}/actions", response_model=ActionConfig)
async def get_action_config(
    integration_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Get available actions and HITL configuration for an integration."""
    from src.integrations.action_executor import (
        ActionType,
        HITLPolicy,
        _DEFAULT_HITL_POLICY,
    )

    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    executor = _get_action_executor()

    # Build action list with current HITL policy
    actions = []
    for at in ActionType:
        policy = executor.get_hitl_policy(ctx.tenant_id, at)
        default = _DEFAULT_HITL_POLICY.get(at, HITLPolicy.DEFAULT)
        actions.append({
            "action_type": at.value,
            "hitl_policy": policy.value,
            "default_policy": default.value,
            "can_override": default != HITLPolicy.ALWAYS,
        })

    # Current tenant overrides
    overrides = executor._tenant_overrides.get(ctx.tenant_id, {})

    return ActionConfig(
        integration_id=integration_id,
        actions=actions,
        hitl_overrides=overrides,
    )


@router.put("/{integration_id}/actions", response_model=ActionConfig)
async def update_action_config(
    integration_id: str,
    body: HITLUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Update HITL configuration for action types."""
    from src.integrations.action_executor import (
        ActionType,
        HITLPolicy,
        _DEFAULT_HITL_POLICY,
    )

    registry = _get_registry()
    manifest = registry.get_manifest(integration_id)

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Integration {integration_id} not found")

    # Validate overrides
    for action_key, policy_val in body.overrides.items():
        # Validate action type
        try:
            at = ActionType(action_key)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action type: {action_key}",
            )

        # Validate policy value
        try:
            policy = HITLPolicy(policy_val)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown HITL policy: {policy_val}",
            )

        # Cannot override ALWAYS
        default = _DEFAULT_HITL_POLICY.get(at, HITLPolicy.DEFAULT)
        if default == HITLPolicy.ALWAYS and policy != HITLPolicy.ALWAYS:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot override ALWAYS policy for {action_key}",
            )

    executor = _get_action_executor()
    if ctx.tenant_id not in executor._tenant_overrides:
        executor._tenant_overrides[ctx.tenant_id] = {}
    executor._tenant_overrides[ctx.tenant_id].update(body.overrides)

    _record_event(
        integration_id, ctx.tenant_id, "hitl_config_updated",
        actor=f"admin:{ctx.tenant_id}",
        details={"overrides": body.overrides},
    )

    logger.info(
        "HITL config updated: integration=%s tenant=%s overrides=%s",
        integration_id, ctx.tenant_id, body.overrides,
    )

    return await get_action_config(integration_id, ctx)


# ---------------------------------------------------------------------------
# OAuth callback — auth-exempt universal redirect
# ---------------------------------------------------------------------------

oauth_router = APIRouter(
    prefix="/api/integrations",
    tags=["integration-oauth"],
)


@oauth_router.get("/oauth/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(
    request: Request,
    code: str = Query(default=""),
    state: str = Query(default=""),
    error: str = Query(default=""),
):
    """Universal OAuth redirect handler (auth-exempt).

    Receives the authorization code from the provider, exchanges it for
    tokens via OAuthManager, and stores the result.
    """
    if error:
        logger.warning("OAuth callback error: %s", error)
        return OAuthCallbackResponse(
            success=False,
            message=f"Authorization denied: {error}",
        )

    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing code or state parameter",
        )

    try:
        from src.integrations.oauth import OAuthManager
        mgr = OAuthManager()
        result = await mgr.handle_callback(
            code=code,
            state=state,
            redirect_uri=str(request.url_for("oauth_callback")),
        )

        integration_id = result.get("integration_id", "")
        tenant_id = result.get("tenant_id", "")

        if tenant_id:
            _record_event(
                integration_id, tenant_id, "oauth_connected",
                details={"scopes": result.get("scopes", [])},
            )

        return OAuthCallbackResponse(
            success=True,
            integration_id=integration_id,
            message="Authorization successful",
        )
    except Exception as exc:
        logger.error("OAuth callback failed: %s", exc)
        return OAuthCallbackResponse(
            success=False,
            message=str(exc)[:200],
        )
