"""Tests for the Superadmin Tier Override endpoint.

Covers:
    PUT /api/superadmin/tenants/{tenant_id}/tier — 8 tests
    - Valid tier changes (4 tiers)
    - Invalid tier value rejection
    - Nonexistent tenant rejection
    - Service not initialized rejection
    - Previous tier captured in response

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api import (
    TierOverrideResponse,
    configure_superadmin_services,
    override_tenant_tier,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository with read + patch support."""
    repo = MagicMock()
    repo.read = AsyncMock()
    repo.patch = AsyncMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    ctx.team_member_email = "admin@remakerdigital.com"
    return ctx


@pytest.fixture(autouse=True)
def _setup_services(mock_tenant_repo):
    """Wire up the module-level _tenant_repo reference."""
    configure_superadmin_services(
        tenant_repo=mock_tenant_repo,
        audit_repo=MagicMock(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTierOverride:
    """PUT /api/superadmin/tenants/{tenant_id}/tier"""

    @pytest.mark.asyncio
    async def test_valid_tier_change_starter_to_professional(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Override from starter to professional succeeds."""
        mock_tenant_repo.read.return_value = {
            "id": "test-001", "tenant_id": "test-001", "tier": "starter",
        }
        mock_tenant_repo.patch.return_value = {}

        result = await override_tenant_tier(
            tenant_id="test-001", tier="professional", _ctx=superadmin_ctx,
        )

        assert isinstance(result, TierOverrideResponse)
        assert result.tenant_id == "test-001"
        assert result.previous_tier == "starter"
        assert result.new_tier == "professional"
        assert result.updated_at is not None

        mock_tenant_repo.patch.assert_called_once()
        ops = mock_tenant_repo.patch.call_args[0][2]
        tier_op = next(op for op in ops if op["path"] == "/tier")
        assert tier_op["value"] == "professional"

    @pytest.mark.asyncio
    async def test_valid_tier_change_to_trial(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Override to trial tier succeeds."""
        mock_tenant_repo.read.return_value = {
            "id": "test-001", "tenant_id": "test-001", "tier": "professional",
        }
        mock_tenant_repo.patch.return_value = {}

        result = await override_tenant_tier(
            tenant_id="test-001", tier="trial", _ctx=superadmin_ctx,
        )

        assert result.previous_tier == "professional"
        assert result.new_tier == "trial"

    @pytest.mark.asyncio
    async def test_valid_tier_change_to_enterprise(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Override to enterprise tier succeeds."""
        mock_tenant_repo.read.return_value = {
            "id": "test-001", "tenant_id": "test-001", "tier": "starter",
        }
        mock_tenant_repo.patch.return_value = {}

        result = await override_tenant_tier(
            tenant_id="test-001", tier="enterprise", _ctx=superadmin_ctx,
        )

        assert result.new_tier == "enterprise"

    @pytest.mark.asyncio
    async def test_previous_tier_none_when_unset(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """When tenant has no tier set, previous_tier is None."""
        mock_tenant_repo.read.return_value = {
            "id": "test-001", "tenant_id": "test-001", "tier": None,
        }
        mock_tenant_repo.patch.return_value = {}

        result = await override_tenant_tier(
            tenant_id="test-001", tier="starter", _ctx=superadmin_ctx,
        )

        assert result.previous_tier is None
        assert result.new_tier == "starter"

    @pytest.mark.asyncio
    async def test_invalid_tier_value_rejected(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Invalid tier value returns 400."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await override_tenant_tier(
                tenant_id="test-001", tier="platinum", _ctx=superadmin_ctx,
            )

        assert exc_info.value.status_code == 400
        assert "Invalid tier" in str(exc_info.value.detail)
        mock_tenant_repo.read.assert_not_called()

    @pytest.mark.asyncio
    async def test_nonexistent_tenant_rejected(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Nonexistent tenant_id returns 404."""
        from fastapi import HTTPException

        mock_tenant_repo.read.side_effect = Exception("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await override_tenant_tier(
                tenant_id="nonexistent-tenant", tier="starter", _ctx=superadmin_ctx,
            )

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_service_not_initialized_rejected(
        self, superadmin_ctx,
    ):
        """Returns 503 when _tenant_repo is None."""
        import src.multi_tenant.superadmin_api as mod
        from fastapi import HTTPException

        original = mod._tenant_repo
        mod._tenant_repo = None
        try:
            with pytest.raises(HTTPException) as exc_info:
                await override_tenant_tier(
                    tenant_id="test-001", tier="starter", _ctx=superadmin_ctx,
                )
            assert exc_info.value.status_code == 503
        finally:
            mod._tenant_repo = original

    @pytest.mark.asyncio
    async def test_patch_operations_include_updated_at(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Patch operations include both /tier and /updated_at."""
        mock_tenant_repo.read.return_value = {
            "id": "test-001", "tenant_id": "test-001", "tier": "trial",
        }
        mock_tenant_repo.patch.return_value = {}

        await override_tenant_tier(
            tenant_id="test-001", tier="starter", _ctx=superadmin_ctx,
        )

        call_args = mock_tenant_repo.patch.call_args
        assert call_args[0][0] == "test-001"  # tenant_id
        assert call_args[0][1] == "test-001"  # document_id

        ops = call_args[0][2]
        paths = [op["path"] for op in ops]
        assert "/tier" in paths
        assert "/updated_at" in paths
