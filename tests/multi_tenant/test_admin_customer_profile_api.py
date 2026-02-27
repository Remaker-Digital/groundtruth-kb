"""Tests for Admin Customer Profile API.

Covers:
    - Service/repo dependency injection (503 when not initialized)
    - List profiles with pagination and consent filter
    - Get single profile (found and not found)
    - Update consent (valid, invalid, profile not found)
    - Shopify data sync
    - Delete profile (found and not found)

Run:
    pytest tests/multi_tenant/test_admin_customer_profile_api.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_customer_profile_api import (
    ConsentUpdateRequest,
    ShopifySyncRequest,
    VALID_CONSENT_STATUSES,
    configure_admin_profile_services,
    router,
)
from src.multi_tenant.cosmos_schema import ConsentStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
CUSTOMER_ID = "cust-abc-123"


def _ctx() -> MagicMock:
    """Build a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = TENANT_ID
    ctx.tier = "professional"
    return ctx


def _mock_profile(
    customer_id: str = CUSTOMER_ID,
    consent_status: str = "granted",
) -> MagicMock:
    """Build a mock CustomerProfileDocument."""
    profile = MagicMock()
    profile.customer_id = customer_id
    profile.consent_status = ConsentStatus(consent_status)
    profile.purchase_history = [{"product_id": "prod-1"}]
    profile.product_questions = []
    profile.region_codes = {"country": "US"}
    profile.marketing_segments = ["vip"]
    profile.jurisdiction_codes = {}
    profile.cart_contents = {}
    profile.created_at = "2026-01-01T00:00:00Z"
    profile.updated_at = "2026-02-01T00:00:00Z"
    profile.last_interaction_at = "2026-02-15T10:00:00Z"
    return profile


# ---------------------------------------------------------------------------
# CP-01 to CP-02: Service initialization
# ---------------------------------------------------------------------------


class TestServiceInit:
    """Dependency injection and initialization checks."""

    @pytest.mark.asyncio
    async def test_cp_01_service_not_initialized_503(self):
        """Raises 503 when profile service not configured."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import _get_service

        with patch("src.multi_tenant.admin_customer_profile_api._profile_service", None):
            with pytest.raises(HTTPException) as exc_info:
                _get_service()
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_cp_02_repo_not_initialized_503(self):
        """Raises 503 when profile repo not configured."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import _get_repo

        with patch("src.multi_tenant.admin_customer_profile_api._profile_repo", None):
            with pytest.raises(HTTPException) as exc_info:
                _get_repo()
            assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# CP-03 to CP-05: List and Get endpoints
# ---------------------------------------------------------------------------


class TestListAndGet:
    """Profile listing and retrieval."""

    @pytest.mark.asyncio
    async def test_cp_03_list_profiles_paginated(self):
        """List returns paginated profiles with total count."""
        from src.multi_tenant.admin_customer_profile_api import list_profiles

        mock_repo = MagicMock()
        mock_repo.query_count = AsyncMock(return_value=25)
        mock_repo.query = AsyncMock(return_value=[
            {
                "customer_id": CUSTOMER_ID,
                "consent_status": "granted",
                "purchase_history": [],
                "updated_at": "2026-02-01T00:00:00Z",
            },
        ])

        with patch("src.multi_tenant.admin_customer_profile_api._get_repo", return_value=mock_repo):
            result = await list_profiles(
                consent_status=None, offset=0, limit=10, ctx=_ctx(),
            )

        assert result.total == 25
        assert result.offset == 0
        assert result.limit == 10
        assert len(result.profiles) == 1
        assert result.profiles[0].customer_id == CUSTOMER_ID

    @pytest.mark.asyncio
    async def test_cp_04_list_invalid_consent_filter_400(self):
        """List with invalid consent_status filter raises 400."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import list_profiles

        mock_repo = MagicMock()
        with patch("src.multi_tenant.admin_customer_profile_api._get_repo", return_value=mock_repo):
            with pytest.raises(HTTPException) as exc_info:
                await list_profiles(
                    consent_status="invalid_value", offset=0, limit=10, ctx=_ctx(),
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_cp_05_get_profile_not_found_404(self):
        """Get single profile raises 404 when not found."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import get_profile

        mock_service = MagicMock()
        mock_service.get_profile = AsyncMock(return_value=None)

        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_profile(CUSTOMER_ID, ctx=_ctx())
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cp_06_get_profile_returns_full_data(self):
        """Get single profile returns all Layer 1 fields."""
        from src.multi_tenant.admin_customer_profile_api import get_profile

        mock_service = MagicMock()
        mock_service.get_profile = AsyncMock(return_value=_mock_profile())

        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            result = await get_profile(CUSTOMER_ID, ctx=_ctx())

        assert result.customer_id == CUSTOMER_ID
        assert result.consent_status == "granted"
        assert len(result.purchase_history) == 1
        assert result.region_codes["country"] == "US"


# ---------------------------------------------------------------------------
# CP-07 to CP-09: Consent update
# ---------------------------------------------------------------------------


class TestConsentUpdate:
    """Consent status update endpoint."""

    @pytest.mark.asyncio
    async def test_cp_07_update_consent_valid(self):
        """Valid consent update returns previous and new status."""
        from src.multi_tenant.admin_customer_profile_api import update_consent

        mock_service = MagicMock()
        mock_service.get_profile = AsyncMock(return_value=_mock_profile(consent_status="not_asked"))
        mock_service.update_consent = AsyncMock()

        body = ConsentUpdateRequest(consent_status="granted")
        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            result = await update_consent(CUSTOMER_ID, body, ctx=_ctx())

        assert result.previous_status == "not_asked"
        assert result.new_status == "granted"
        mock_service.update_consent.assert_called_once()

    @pytest.mark.asyncio
    async def test_cp_08_update_consent_invalid_status_400(self):
        """Invalid consent_status raises 400."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import update_consent

        body = ConsentUpdateRequest(consent_status="maybe")
        with pytest.raises(HTTPException) as exc_info:
            await update_consent(CUSTOMER_ID, body, ctx=_ctx())
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_cp_09_update_consent_profile_not_found_404(self):
        """Consent update on nonexistent profile raises 404."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import update_consent

        mock_service = MagicMock()
        mock_service.get_profile = AsyncMock(return_value=None)

        body = ConsentUpdateRequest(consent_status="granted")
        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await update_consent(CUSTOMER_ID, body, ctx=_ctx())
            assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# CP-10 to CP-12: Sync and Delete
# ---------------------------------------------------------------------------


class TestSyncAndDelete:
    """Shopify sync and profile deletion."""

    @pytest.mark.asyncio
    async def test_cp_10_sync_shopify_data(self):
        """Shopify sync delegates to service and returns synced_at."""
        from src.multi_tenant.admin_customer_profile_api import sync_shopify_data

        mock_service = MagicMock()
        synced_profile = _mock_profile()
        mock_service.sync_from_shopify = AsyncMock(return_value=synced_profile)

        body = ShopifySyncRequest(shopify_data={"orders": [{"product_id": "p1"}]})
        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            result = await sync_shopify_data(CUSTOMER_ID, body, ctx=_ctx())

        assert result.customer_id == CUSTOMER_ID
        assert result.synced_at == synced_profile.updated_at
        mock_service.sync_from_shopify.assert_called_once_with(
            tenant_id=TENANT_ID,
            customer_id=CUSTOMER_ID,
            shopify_data={"orders": [{"product_id": "p1"}]},
        )

    @pytest.mark.asyncio
    async def test_cp_11_delete_profile_success(self):
        """Delete profile returns deleted=True."""
        from src.multi_tenant.admin_customer_profile_api import delete_profile

        mock_service = MagicMock()
        mock_service.delete_profile = AsyncMock(return_value=True)

        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            result = await delete_profile(CUSTOMER_ID, ctx=_ctx())

        assert result.deleted is True
        assert result.customer_id == CUSTOMER_ID

    @pytest.mark.asyncio
    async def test_cp_12_delete_profile_not_found_404(self):
        """Delete nonexistent profile raises 404."""
        from fastapi import HTTPException

        from src.multi_tenant.admin_customer_profile_api import delete_profile

        mock_service = MagicMock()
        mock_service.delete_profile = AsyncMock(return_value=False)

        with patch("src.multi_tenant.admin_customer_profile_api._get_service", return_value=mock_service):
            with pytest.raises(HTTPException) as exc_info:
                await delete_profile(CUSTOMER_ID, ctx=_ctx())
            assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# CP-13 to CP-14: Router prefix and empty list
# ---------------------------------------------------------------------------


class TestRouterAndEmptyList:
    """Router prefix verification and list_profiles with zero results."""

    def test_cp_13_router_prefix_is_api_admin_profiles(self):
        """Router prefix must be /api/admin/profiles."""
        assert router.prefix == "/api/admin/profiles"

    @pytest.mark.asyncio
    async def test_cp_14_list_profiles_empty(self):
        """list_profiles returns total=0 and empty profiles when repo returns nothing."""
        from src.multi_tenant.admin_customer_profile_api import list_profiles

        mock_repo = MagicMock()
        mock_repo.query_count = AsyncMock(return_value=0)
        mock_repo.query = AsyncMock(return_value=[])

        with patch("src.multi_tenant.admin_customer_profile_api._get_repo", return_value=mock_repo):
            result = await list_profiles(
                consent_status=None, offset=0, limit=50, ctx=_ctx(),
            )

        assert result.total == 0
        assert result.profiles == []
        assert result.tenant_id == TENANT_ID
