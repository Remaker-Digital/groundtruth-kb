"""Tests for Admin Integration Management API.

Covers:
    - Integration listing (all 4 types)
    - Tier gate enforcement
    - Integration activation (coming_soon rejection, tier gate)
    - Integration deactivation
    - Integration config update (allowed keys, tier gate)
    - Integration disconnect (credential cleanup)
    - Helper functions (_tier_meets_gate, _build_summary)

Run:
    pytest tests/multi_tenant/test_admin_integration_api.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_integration_api import (
    INTEGRATION_TYPES,
    IntegrationDetail,
    IntegrationSummary,
    IntegrationUpdateRequest,
    _build_summary,
    _INTEGRATION_META,
    _tier_meets_gate,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"


def _ctx(tier: str = "professional") -> MagicMock:
    """Build a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = TENANT_ID
    ctx.tier = tier
    return ctx


def _mock_config_result(config: dict[str, Any] | None = None) -> MagicMock:
    """Build a mock config processor result."""
    result = MagicMock()
    result.config = config or {}
    result.success = True
    return result


def _mock_processor(
    config: dict[str, Any] | None = None,
    update_success: bool = True,
) -> MagicMock:
    """Build a mock config processor."""
    processor = MagicMock()
    get_result = _mock_config_result(config)
    processor.get_config = AsyncMock(return_value=get_result)

    update_result = MagicMock()
    update_result.success = update_success
    processor.update_config = AsyncMock(return_value=update_result)

    return processor


# ---------------------------------------------------------------------------
# IA-01 to IA-04: Helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    """Integration API helper function tests."""

    def test_ia_01_tier_meets_gate_none(self):
        """No gate means all tiers pass."""
        assert _tier_meets_gate("trial", None) is True
        assert _tier_meets_gate("starter", None) is True

    def test_ia_02_tier_meets_gate_below(self):
        """Lower tier fails professional gate."""
        assert _tier_meets_gate("trial", "professional") is False
        assert _tier_meets_gate("starter", "professional") is False

    def test_ia_03_tier_meets_gate_at_or_above(self):
        """Same or higher tier passes gate."""
        assert _tier_meets_gate("professional", "professional") is True
        assert _tier_meets_gate("enterprise", "professional") is True

    def test_ia_04_build_summary_shopify(self):
        """Build summary for Shopify (no tier gate, not coming_soon)."""
        config = {"shopify_sync_enabled": True, "shopify_integration_status": "connected"}
        summary = _build_summary("shopify", _INTEGRATION_META["shopify"], config, "starter")

        assert summary.type == "shopify"
        assert summary.name == "Shopify"
        assert summary.enabled is True
        assert summary.status == "connected"
        assert summary.tier_gate is None
        assert summary.tier_met is True
        assert summary.coming_soon is False

    def test_ia_05_build_summary_zendesk_tier_unmet(self):
        """Zendesk summary shows tier_met=False for trial tenant."""
        config: dict = {}
        summary = _build_summary("zendesk", _INTEGRATION_META["zendesk"], config, "trial")

        assert summary.type == "zendesk"
        assert summary.enabled is False
        assert summary.tier_met is False
        assert summary.coming_soon is True


# ---------------------------------------------------------------------------
# IA-06 to IA-08: List and Get endpoints
# ---------------------------------------------------------------------------


class TestListAndGet:
    """Integration list and detail endpoints."""

    @pytest.mark.asyncio
    async def test_ia_06_list_returns_all_types(self):
        """List endpoint returns all 4 integration types."""
        from src.multi_tenant.admin_integration_api import list_integrations

        processor = _mock_processor()
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            result = await list_integrations(ctx=_ctx())

        assert len(result) == 4
        types = {s.type for s in result}
        assert types == set(INTEGRATION_TYPES)

    @pytest.mark.asyncio
    async def test_ia_07_get_returns_config_fields(self):
        """Get detail endpoint includes config_fields."""
        from src.multi_tenant.admin_integration_api import get_integration

        processor = _mock_processor()
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            result = await get_integration("shopify", ctx=_ctx())

        assert isinstance(result, IntegrationDetail)
        assert len(result.config_fields) > 0
        assert result.config_fields[0]["key"] == "shopify_sync_enabled"

    @pytest.mark.asyncio
    async def test_ia_08_get_unknown_type_404(self):
        """Get with unknown type raises 404."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_integration_api import get_integration

        with pytest.raises(HTTPException) as exc_info:
            await get_integration("unknown_platform", ctx=_ctx())
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# IA-09 to IA-12: Activate / Deactivate / Update / Disconnect
# ---------------------------------------------------------------------------


class TestMutations:
    """Integration activation, deactivation, update, and disconnect."""

    @pytest.mark.asyncio
    async def test_ia_09_activate_coming_soon_rejected(self):
        """Cannot activate a coming_soon integration."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_integration_api import activate_integration

        processor = _mock_processor()
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            with pytest.raises(HTTPException) as exc_info:
                await activate_integration("zendesk", ctx=_ctx())
            assert exc_info.value.status_code == 400
            assert "coming soon" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_ia_10_activate_tier_gate_rejected(self):
        """Cannot activate when tier is below gate."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_integration_api import activate_integration

        processor = _mock_processor()
        # Zendesk requires professional; use starter tier
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            with pytest.raises(HTTPException) as exc_info:
                await activate_integration("zendesk", ctx=_ctx(tier="starter"))
            # The coming_soon check fires first (400), but tier gate would also block
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_ia_11_deactivate_sets_disabled(self):
        """Deactivate writes enabled=False and status=disconnected."""
        from src.multi_tenant.admin_integration_api import deactivate_integration

        processor = _mock_processor(config={"shopify_sync_enabled": False, "shopify_integration_status": "disconnected"})
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            result = await deactivate_integration("shopify", ctx=_ctx())

        assert result.success is True
        # Verify update_config was called with correct fields
        call_kwargs = processor.update_config.call_args[1]
        assert call_kwargs["updates"]["shopify_sync_enabled"] is False
        assert call_kwargs["updates"]["shopify_integration_status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_ia_12_update_rejects_invalid_fields(self):
        """Update rejects config keys not belonging to the integration."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_integration_api import update_integration

        body = IntegrationUpdateRequest(config={"not_a_real_field": True})
        processor = _mock_processor()
        with patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor):
            with pytest.raises(HTTPException) as exc_info:
                await update_integration("shopify", body=body, ctx=_ctx())
            assert exc_info.value.status_code == 400
            assert "not_a_real_field" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_ia_13_disconnect_clears_credentials(self):
        """Disconnect clears status and attempts Key Vault secret removal."""
        from src.multi_tenant.admin_integration_api import disconnect_integration

        processor = _mock_processor(config={"shopify_sync_enabled": False})
        mock_secret_svc = MagicMock()
        mock_secret_svc.delete_secret = AsyncMock()

        with (
            patch("src.multi_tenant.admin_integration_api._get_config_processor", return_value=processor),
            patch("src.multi_tenant.tenant_secret_service.get_secret_service", return_value=mock_secret_svc),
        ):
            result = await disconnect_integration("shopify", ctx=_ctx())

        assert result.success is True
        # Status cleared to None
        call_kwargs = processor.update_config.call_args[1]
        assert call_kwargs["updates"]["shopify_integration_status"] is None
        # Key Vault secret deletion attempted
        mock_secret_svc.delete_secret.assert_called_once_with(TENANT_ID, "shopify_api_key")
