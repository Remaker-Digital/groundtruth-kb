"""
Admin Integration Management API — C10 capability dependency.

Provides endpoints for listing, configuring, activating, deactivating,
and managing third-party integrations (Shopify, Zendesk, Mailchimp,
Google Analytics, Stripe MCP).

Integration enable/disable fields are stored in PreferencesDocument.
Connection status metadata is also stored there.  Actual credential
management (API keys, tokens) is handled separately by
TenantSecretService in Key Vault.

Routes:
    GET  /api/admin/integrations          — List all integrations + status
    GET  /api/admin/integrations/{type}   — Get single integration detail
    PUT  /api/admin/integrations/{type}   — Update integration config
    POST /api/admin/integrations/{type}/activate   — Activate
    POST /api/admin/integrations/{type}/deactivate — Deactivate
    DELETE /api/admin/integrations/{type}           — Disconnect + remove creds

    # Stripe MCP specific (AGNTCY Phase 3B)
    POST /api/admin/integrations/stripe/credentials — Store Stripe API key
    POST /api/admin/integrations/stripe/test        — Test Stripe MCP connection
    GET  /api/admin/integrations/stripe/tools       — List available Stripe MCP tools
    DELETE /api/admin/integrations/stripe/credentials — Remove Stripe API key

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.middleware import get_tenant_context, TenantContext

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Integration registry — static metadata for the 4 supported integrations
# ---------------------------------------------------------------------------

INTEGRATION_TYPES = ("shopify", "zendesk", "mailchimp", "google_analytics", "stripe")

_INTEGRATION_META: dict[str, dict[str, Any]] = {
    "shopify": {
        "name": "Shopify",
        "description": "Sync product catalog and customer data from your Shopify store.",
        "icon": "shopify",
        "enable_field": "shopify_sync_enabled",
        "status_field": "shopify_integration_status",
        "tier_gate": None,  # available on all tiers
        "coming_soon": False,
        "config_fields": [
            {"key": "shopify_sync_enabled", "label": "Product Sync", "type": "boolean"},
        ],
    },
    "zendesk": {
        "name": "Zendesk",
        "description": "Create Zendesk tickets automatically on conversation escalation.",
        "icon": "zendesk",
        "enable_field": "zendesk_escalation_enabled",
        "status_field": "zendesk_integration_status",
        "tier_gate": "professional",
        "coming_soon": True,
        "config_fields": [
            {"key": "zendesk_escalation_enabled", "label": "Auto-create Tickets", "type": "boolean"},
        ],
    },
    "mailchimp": {
        "name": "Mailchimp",
        "description": "Import customer segments from Mailchimp for AI personalization.",
        "icon": "mailchimp",
        "enable_field": "mailchimp_segment_sync",
        "status_field": "mailchimp_integration_status",
        "tier_gate": "professional",
        "coming_soon": True,
        "config_fields": [
            {"key": "mailchimp_segment_sync", "label": "Segment Sync", "type": "boolean"},
        ],
    },
    "google_analytics": {
        "name": "Google Analytics",
        "description": "Export conversation events to your GA4 property for unified analytics.",
        "icon": "google_analytics",
        "enable_field": "google_analytics_enabled",
        "status_field": "google_analytics_integration_status",
        "tier_gate": "professional",
        "coming_soon": True,
        "config_fields": [
            {"key": "google_analytics_enabled", "label": "Event Export", "type": "boolean"},
        ],
    },
    "stripe": {
        "name": "Stripe (MCP)",
        "description": "AI-powered payment lookup and subscription queries via Stripe MCP.",
        "icon": "stripe",
        "enable_field": "stripe_mcp_enabled",
        "status_field": "stripe_mcp_status",
        "tier_gate": "professional",
        "coming_soon": False,
        "config_fields": [
            {"key": "stripe_mcp_enabled", "label": "Enable Stripe MCP", "type": "boolean"},
        ],
    },
}

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class IntegrationSummary(BaseModel):
    """Summary of one integration returned in the list endpoint."""

    model_config = {"populate_by_name": True}

    type: str = Field(description="Integration key (shopify, zendesk, etc.)")
    name: str = Field(description="Human-readable name")
    description: str
    icon: str
    enabled: bool = Field(description="Whether the integration feature is turned on")
    status: str | None = Field(
        default=None,
        description="Connection status: connected | disconnected | error | None",
    )
    tier_gate: str | None = Field(
        default=None,
        alias="tierGate",
        serialization_alias="tierGate",
        description="Minimum tier required (null = all tiers)",
    )
    tier_met: bool = Field(
        default=True,
        alias="tierMet",
        serialization_alias="tierMet",
        description="Whether the current tenant tier meets the gate",
    )
    coming_soon: bool = Field(
        default=False,
        alias="comingSoon",
        serialization_alias="comingSoon",
        description="Whether this integration is not yet implemented (backend stub only)",
    )


class IntegrationDetail(IntegrationSummary):
    """Detailed view including config fields."""
    config_fields: list[dict[str, Any]] = Field(default_factory=list)


class IntegrationUpdateRequest(BaseModel):
    """Body for PUT — update integration-specific config fields."""
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs to update (e.g., {shopify_sync_enabled: true})",
    )


class StripeCredentialRequest(BaseModel):
    """Body for POST /stripe/credentials — store Stripe API key."""
    api_key: str = Field(
        description="Stripe restricted API key (rk_live_... or rk_test_...)",
        min_length=10,
    )


class StripeConnectionTestResult(BaseModel):
    """Response for POST /stripe/test."""
    success: bool
    tool_count: int = Field(default=0, description="Number of available MCP tools")
    tools: list[str] = Field(default_factory=list, description="Available tool names")
    error: str | None = None
    elapsed_ms: float = 0


class IntegrationResponse(BaseModel):
    """Generic mutation response."""
    success: bool
    message: str
    integration: IntegrationSummary | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Tier ordering for gate checks
_TIER_ORDER = {"trial": 0, "starter": 1, "professional": 2, "enterprise": 3}

# Config processor singleton (lazy import to avoid circular deps)
_config_processor = None


def _get_config_processor():
    global _config_processor
    if _config_processor is None:
        from src.multi_tenant.tenant_config_processor import get_config_processor
        _config_processor = get_config_processor()
    return _config_processor


def _tier_meets_gate(tenant_tier: str, gate: str | None) -> bool:
    """Check if the tenant tier meets or exceeds the gate tier."""
    if gate is None:
        return True
    return _TIER_ORDER.get(tenant_tier, 0) >= _TIER_ORDER.get(gate, 0)


def _build_summary(
    int_type: str,
    meta: dict[str, Any],
    config: dict[str, Any],
    tenant_tier: str,
) -> IntegrationSummary:
    """Build an IntegrationSummary from metadata + resolved config."""
    enable_field = meta["enable_field"]
    status_field = meta["status_field"]

    return IntegrationSummary(
        type=int_type,
        name=meta["name"],
        description=meta["description"],
        icon=meta["icon"],
        enabled=bool(config.get(enable_field, False)),
        status=config.get(status_field),
        tier_gate=meta["tier_gate"],
        tier_met=_tier_meets_gate(tenant_tier, meta["tier_gate"]),
        coming_soon=bool(meta.get("coming_soon", False)),
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/admin/integrations",
    tags=["admin-integrations"],
)


@router.get("", response_model=list[IntegrationSummary])
async def list_integrations(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """List all available integrations with their current status."""
    processor = _get_config_processor()
    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}

    return [
        _build_summary(int_type, meta, config, ctx.tier)
        for int_type, meta in _INTEGRATION_META.items()
    ]


@router.get("/{integration_type}", response_model=IntegrationDetail)
async def get_integration(
    integration_type: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Get detailed info for a specific integration."""
    if integration_type not in _INTEGRATION_META:
        raise HTTPException(status_code=404, detail=f"Unknown integration: {integration_type}")

    meta = _INTEGRATION_META[integration_type]
    processor = _get_config_processor()
    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}

    summary = _build_summary(integration_type, meta, config, ctx.tier)
    return IntegrationDetail(
        **summary.model_dump(),
        config_fields=meta["config_fields"],
    )


@router.put("/{integration_type}", response_model=IntegrationResponse)
async def update_integration(
    integration_type: str,
    body: IntegrationUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Update integration-specific configuration fields."""
    if integration_type not in _INTEGRATION_META:
        raise HTTPException(status_code=404, detail=f"Unknown integration: {integration_type}")

    meta = _INTEGRATION_META[integration_type]

    # Tier gate check
    if not _tier_meets_gate(ctx.tier, meta["tier_gate"]):
        raise HTTPException(
            status_code=403,
            detail=f"{meta['name']} requires {meta['tier_gate']} tier or above.",
        )

    # Only allow updating fields that belong to this integration
    allowed_keys = {f["key"] for f in meta["config_fields"]}
    allowed_keys.add(meta["enable_field"])
    invalid = set(body.config.keys()) - allowed_keys
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Fields not allowed for {meta['name']}: {', '.join(invalid)}",
        )

    processor = _get_config_processor()
    result = await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates=body.config,
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to update integration config.")

    # Re-read to get updated summary
    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary(integration_type, meta, config, ctx.tier)

    logger.info(
        "Integration %s updated for tenant %s: %s",
        integration_type, ctx.tenant_id, body.config,
    )

    return IntegrationResponse(
        success=True,
        message=f"{meta['name']} configuration updated.",
        integration=summary,
    )


@router.post("/{integration_type}/activate", response_model=IntegrationResponse)
async def activate_integration(
    integration_type: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Activate (enable) an integration."""
    if integration_type not in _INTEGRATION_META:
        raise HTTPException(status_code=404, detail=f"Unknown integration: {integration_type}")

    meta = _INTEGRATION_META[integration_type]

    if meta.get("coming_soon"):
        raise HTTPException(
            status_code=400,
            detail=f"{meta['name']} is coming soon and cannot be activated yet.",
        )

    if not _tier_meets_gate(ctx.tier, meta["tier_gate"]):
        raise HTTPException(
            status_code=403,
            detail=f"{meta['name']} requires {meta['tier_gate']} tier or above.",
        )

    processor = _get_config_processor()
    updates = {
        meta["enable_field"]: True,
        meta["status_field"]: "connected",
    }
    result = await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates=updates,
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to activate integration.")

    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary(integration_type, meta, config, ctx.tier)

    logger.info("Integration %s activated for tenant %s", integration_type, ctx.tenant_id)

    return IntegrationResponse(
        success=True,
        message=f"{meta['name']} activated.",
        integration=summary,
    )


@router.post("/{integration_type}/deactivate", response_model=IntegrationResponse)
async def deactivate_integration(
    integration_type: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Deactivate (disable) an integration."""
    if integration_type not in _INTEGRATION_META:
        raise HTTPException(status_code=404, detail=f"Unknown integration: {integration_type}")

    meta = _INTEGRATION_META[integration_type]

    processor = _get_config_processor()
    updates = {
        meta["enable_field"]: False,
        meta["status_field"]: "disconnected",
    }
    result = await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates=updates,
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to deactivate integration.")

    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary(integration_type, meta, config, ctx.tier)

    logger.info("Integration %s deactivated for tenant %s", integration_type, ctx.tenant_id)

    return IntegrationResponse(
        success=True,
        message=f"{meta['name']} deactivated.",
        integration=summary,
    )


@router.delete("/{integration_type}", response_model=IntegrationResponse)
async def disconnect_integration(
    integration_type: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Disconnect an integration — disables it and clears connection status."""
    if integration_type not in _INTEGRATION_META:
        raise HTTPException(status_code=404, detail=f"Unknown integration: {integration_type}")

    meta = _INTEGRATION_META[integration_type]

    processor = _get_config_processor()
    updates = {
        meta["enable_field"]: False,
        meta["status_field"]: None,  # clear connection status
    }
    result = await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates=updates,
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to disconnect integration.")

    # Optionally remove stored credentials from Key Vault
    try:
        from src.multi_tenant.tenant_secret_service import get_secret_service
        secret_svc = get_secret_service()
        if secret_svc:
            secret_type = f"{integration_type}_api_key"
            await secret_svc.delete_secret(ctx.tenant_id, secret_type)
    except Exception:
        logger.warning(
            "Could not remove credentials for %s on tenant %s — may not exist.",
            integration_type, ctx.tenant_id,
        )

    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary(integration_type, meta, config, ctx.tier)

    logger.info("Integration %s disconnected for tenant %s", integration_type, ctx.tenant_id)

    return IntegrationResponse(
        success=True,
        message=f"{meta['name']} disconnected.",
        integration=summary,
    )


# ---------------------------------------------------------------------------
# Stripe MCP — credential management + connection test (AGNTCY Phase 3B)
# ---------------------------------------------------------------------------


@router.post("/stripe/credentials", response_model=IntegrationResponse)
async def store_stripe_credentials(
    body: StripeCredentialRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Store a Stripe restricted API key in Key Vault.

    The key is validated by prefix (must start with ``rk_`` or ``sk_``)
    and stored securely. The Stripe MCP status is updated to "connected".
    """
    meta = _INTEGRATION_META["stripe"]

    # Tier gate check
    if not _tier_meets_gate(ctx.tier, meta["tier_gate"]):
        raise HTTPException(
            status_code=403,
            detail=f"{meta['name']} requires {meta['tier_gate']} tier or above.",
        )

    # Basic key prefix validation
    if not (
        body.api_key.startswith("rk_live_")
        or body.api_key.startswith("rk_test_")
        or body.api_key.startswith("sk_live_")
        or body.api_key.startswith("sk_test_")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe API key format. Expected rk_live_*, rk_test_*, sk_live_*, or sk_test_* prefix.",
        )

    # Store in Key Vault
    try:
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        svc = get_secret_service()
        await svc.initialize()
        await svc.store_secret(
            ctx.tenant_id,
            TenantSecretType.STRIPE_API_KEY,
            body.api_key,
        )
    except Exception as exc:
        logger.error(
            "Failed to store Stripe credentials: tenant=%s error=%s",
            ctx.tenant_id, exc,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to store Stripe API key.",
        )

    # Update connection status
    processor = _get_config_processor()
    await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates={
            "stripe_mcp_enabled": True,
            "stripe_mcp_status": "connected",
        },
        actor=f"admin:{ctx.tenant_id}",
    )

    # Invalidate credential cache
    try:
        from src.multi_tenant.mcp_credential_cache import get_credential_cache

        get_credential_cache().invalidate(ctx.tenant_id, "stripe-api-key")
    except Exception:
        pass

    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary("stripe", meta, config, ctx.tier)

    logger.info("Stripe credentials stored for tenant %s", ctx.tenant_id)

    return IntegrationResponse(
        success=True,
        message="Stripe API key saved. Use 'Test Connection' to verify.",
        integration=summary,
    )


@router.post("/stripe/test", response_model=StripeConnectionTestResult)
async def test_stripe_connection(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Test the Stripe MCP connection by connecting and listing tools.

    Requires a stored Stripe API key. Connects to ``mcp.stripe.com``,
    initializes the session, and returns the list of available tools.
    """
    import time

    meta = _INTEGRATION_META["stripe"]

    if not _tier_meets_gate(ctx.tier, meta["tier_gate"]):
        raise HTTPException(
            status_code=403,
            detail=f"{meta['name']} requires {meta['tier_gate']} tier or above.",
        )

    start = time.monotonic()

    # Retrieve API key from Key Vault
    try:
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        svc = get_secret_service()
        await svc.initialize()
        api_key = await svc.get_secret(ctx.tenant_id, TenantSecretType.STRIPE_API_KEY)
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return StripeConnectionTestResult(
            success=False,
            error=f"Failed to retrieve API key: {str(exc)[:100]}",
            elapsed_ms=round(elapsed, 1),
        )

    if not api_key:
        elapsed = (time.monotonic() - start) * 1000
        return StripeConnectionTestResult(
            success=False,
            error="No Stripe API key stored. Save a key first.",
            elapsed_ms=round(elapsed, 1),
        )

    # Connect to Stripe MCP and list tools
    try:
        from src.multi_tenant.mcp_client import (
            AgentRedMcpClient,
            McpServerConfig,
        )

        config = McpServerConfig(
            server_name="stripe",
            server_url="https://mcp.stripe.com",
            server_type="stripe",
            timeout_ms=10_000,  # generous for connection test
            read_only=True,
        )
        client = AgentRedMcpClient(config=config)
        await client.connect(auth_headers={"Authorization": f"Bearer {api_key}"})
        tools = client.available_tools
        tool_names = [t.get("name", "") for t in tools]
        await client.close()

        elapsed = (time.monotonic() - start) * 1000

        # Update status to connected on success
        processor = _get_config_processor()
        await processor.update_config(
            tenant_id=ctx.tenant_id,
            tier=ctx.tier,
            updates={"stripe_mcp_status": "connected"},
            actor=f"admin:{ctx.tenant_id}",
        )

        logger.info(
            "Stripe MCP connection test PASS: tenant=%s tools=%d elapsed=%.0fms",
            ctx.tenant_id, len(tools), elapsed,
        )

        return StripeConnectionTestResult(
            success=True,
            tool_count=len(tools),
            tools=tool_names[:20],  # limit to first 20 tool names
            elapsed_ms=round(elapsed, 1),
        )

    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000

        # Update status to error
        processor = _get_config_processor()
        await processor.update_config(
            tenant_id=ctx.tenant_id,
            tier=ctx.tier,
            updates={"stripe_mcp_status": "error"},
            actor=f"admin:{ctx.tenant_id}",
        )

        logger.warning(
            "Stripe MCP connection test FAIL: tenant=%s error=%s elapsed=%.0fms",
            ctx.tenant_id, exc, elapsed,
        )

        return StripeConnectionTestResult(
            success=False,
            error=str(exc)[:200],
            elapsed_ms=round(elapsed, 1),
        )


@router.get("/stripe/tools", response_model=StripeConnectionTestResult)
async def get_stripe_tools(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Return cached Stripe MCP tools (delegates to test endpoint)."""
    return await test_stripe_connection(ctx=ctx)


@router.delete("/stripe/credentials", response_model=IntegrationResponse)
async def remove_stripe_credentials(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Remove Stripe API key from Key Vault and disconnect."""
    meta = _INTEGRATION_META["stripe"]

    # Delete from Key Vault
    try:
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        svc = get_secret_service()
        await svc.initialize()
        await svc.delete_secret(ctx.tenant_id, TenantSecretType.STRIPE_API_KEY)
    except Exception as exc:
        logger.warning(
            "Could not remove Stripe credentials: tenant=%s error=%s",
            ctx.tenant_id, exc,
        )

    # Update status
    processor = _get_config_processor()
    await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        updates={
            "stripe_mcp_enabled": False,
            "stripe_mcp_status": "disconnected",
        },
        actor=f"admin:{ctx.tenant_id}",
    )

    # Invalidate credential cache
    try:
        from src.multi_tenant.mcp_credential_cache import get_credential_cache

        get_credential_cache().clear_tenant(ctx.tenant_id)
    except Exception:
        pass

    cfg_result = await processor.get_config(ctx.tenant_id, TenantTier(ctx.tier))
    config = cfg_result.config if cfg_result else {}
    summary = _build_summary("stripe", meta, config, ctx.tier)

    logger.info("Stripe credentials removed for tenant %s", ctx.tenant_id)

    return IntegrationResponse(
        success=True,
        message="Stripe API key removed and integration disconnected.",
        integration=summary,
    )
