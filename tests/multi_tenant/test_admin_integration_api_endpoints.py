"""Endpoint-level tests for Admin Integration Management API.

Covers 5 specs:
    1. Router prefix /api/admin/integrations
    2. list_integrations — mock config processor
    3. get_integration — mock config processor for type="shopify"
    4. activate_integration — mock processor.update_config + get_config
    5. deactivate_integration — mock processor.update_config + get_config

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_integration_api import (
    INTEGRATION_TYPES,
    IntegrationDetail,
    router,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_ID = "test-tenant-001"


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", TENANT_ID)
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


def _mock_processor(
    config: dict[str, Any] | None = None,
    update_success: bool = True,
) -> MagicMock:
    """Build a mock config processor with get_config and update_config."""
    processor = MagicMock()

    get_result = MagicMock()
    get_result.config = config or {}
    processor.get_config = AsyncMock(return_value=get_result)

    update_result = MagicMock()
    update_result.success = update_success
    processor.update_config = AsyncMock(return_value=update_result)

    return processor


# ---------------------------------------------------------------------------
# 1. Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Spec: Router has prefix /api/admin/integrations."""

    def test_router_prefix_is_correct(self):
        assert router.prefix == "/api/admin/integrations"

    def test_router_tags(self):
        assert "admin-integrations" in router.tags


# ---------------------------------------------------------------------------
# 2. list_integrations — mock config processor
# ---------------------------------------------------------------------------


class TestListIntegrationsEndpoint:
    """Spec: GET /api/admin/integrations returns all integration types."""

    @pytest.mark.asyncio
    async def test_returns_all_integration_types(self):
        from src.multi_tenant.admin_integration_api import list_integrations

        processor = _mock_processor()
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            result = await list_integrations(ctx=ctx)

        assert len(result) == len(INTEGRATION_TYPES)
        types_returned = {s.type for s in result}
        assert types_returned == set(INTEGRATION_TYPES)

    @pytest.mark.asyncio
    async def test_processor_get_config_called(self):
        from src.multi_tenant.admin_integration_api import list_integrations

        processor = _mock_processor()
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            await list_integrations(ctx=ctx)

        processor.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_shopify_enabled_reflects_config(self):
        from src.multi_tenant.admin_integration_api import list_integrations

        processor = _mock_processor(config={
            "shopify_sync_enabled": True,
            "shopify_integration_status": "connected",
        })
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            result = await list_integrations(ctx=ctx)

        shopify = next(s for s in result if s.type == "shopify")
        assert shopify.enabled is True
        assert shopify.status == "connected"


# ---------------------------------------------------------------------------
# 3. get_integration — for type="shopify"
# ---------------------------------------------------------------------------


class TestGetIntegrationEndpoint:
    """Spec: GET /api/admin/integrations/{type} returns detail with config fields."""

    @pytest.mark.asyncio
    async def test_returns_shopify_detail(self):
        from src.multi_tenant.admin_integration_api import get_integration

        processor = _mock_processor(config={
            "shopify_sync_enabled": False,
        })
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            result = await get_integration("shopify", ctx=ctx)

        assert isinstance(result, IntegrationDetail)
        assert result.type == "shopify"
        assert result.name == "Shopify"
        assert len(result.config_fields) > 0
        assert result.config_fields[0]["key"] == "shopify_sync_enabled"

    @pytest.mark.asyncio
    async def test_raises_404_for_unknown_type(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_integration_api import get_integration

        ctx = _ctx()

        with pytest.raises(HTTPException) as exc_info:
            await get_integration("unknown_platform", ctx=ctx)
        assert exc_info.value.status_code == 404
        assert "Unknown integration" in exc_info.value.detail


# ---------------------------------------------------------------------------
# 4. activate_integration — processor.update_config + get_config
# ---------------------------------------------------------------------------


class TestActivateIntegrationEndpoint:
    """Spec: POST /api/admin/integrations/{type}/activate enables integration."""

    @pytest.mark.asyncio
    async def test_activates_shopify(self):
        from src.multi_tenant.admin_integration_api import activate_integration

        processor = _mock_processor(config={
            "shopify_sync_enabled": True,
            "shopify_integration_status": "connected",
        })
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            result = await activate_integration("shopify", ctx=ctx)

        assert result.success is True
        assert result.integration is not None
        assert result.integration.type == "shopify"

        # Verify update_config was called with enable=True and status=connected
        call_kwargs = processor.update_config.call_args.kwargs
        assert call_kwargs["updates"]["shopify_sync_enabled"] is True
        assert call_kwargs["updates"]["shopify_integration_status"] == "connected"

    @pytest.mark.asyncio
    async def test_rejects_coming_soon_integration(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_integration_api import activate_integration

        processor = _mock_processor()
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await activate_integration("zendesk", ctx=ctx)
            assert exc_info.value.status_code == 400
            assert "coming soon" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_rejects_tier_gate_not_met(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_integration_api import activate_integration

        processor = _mock_processor()
        # Stripe requires professional; use starter tier
        ctx = _ctx(tier="starter")

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await activate_integration("stripe", ctx=ctx)
            assert exc_info.value.status_code == 403
            assert "requires" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 5. deactivate_integration — processor.update_config + get_config
# ---------------------------------------------------------------------------


class TestDeactivateIntegrationEndpoint:
    """Spec: POST /api/admin/integrations/{type}/deactivate disables integration."""

    @pytest.mark.asyncio
    async def test_deactivates_shopify(self):
        from src.multi_tenant.admin_integration_api import deactivate_integration

        processor = _mock_processor(config={
            "shopify_sync_enabled": False,
            "shopify_integration_status": "disconnected",
        })
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            result = await deactivate_integration("shopify", ctx=ctx)

        assert result.success is True
        assert result.integration is not None

        # Verify update_config was called with enable=False and status=disconnected
        call_kwargs = processor.update_config.call_args.kwargs
        assert call_kwargs["updates"]["shopify_sync_enabled"] is False
        assert call_kwargs["updates"]["shopify_integration_status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_raises_404_for_unknown_type(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_integration_api import deactivate_integration

        ctx = _ctx()

        with pytest.raises(HTTPException) as exc_info:
            await deactivate_integration("fake_integration", ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_handles_update_failure(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_integration_api import deactivate_integration

        processor = _mock_processor(update_success=False)
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_integration_api._get_config_processor",
            return_value=processor,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await deactivate_integration("shopify", ctx=ctx)
            assert exc_info.value.status_code == 500
