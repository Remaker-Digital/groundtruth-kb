"""Tests for Secret Health aggregate endpoint (SPEC-1843, WI-1606).

Validates that the secret_health endpoint returns only aggregate key
coverage counts.  The former secret_posture endpoint was removed because
it exposed per-tenant secret inventories, customer emails, and TOTP seeds.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api import (
    SecretHealthResponse,
    configure_superadmin_services,
    secret_health,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_TENANT_DOC = {
    "id": "test-tenant-001",
    "tenant_id": "test-tenant-001",
    "status": "active",
    "tier": "professional",
    "api_key_hash": "sha256_hash_of_api_key",
    "widget_key_hash": "sha256_hash_of_widget_key",
}


@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo._container = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["test-tenant-001"])
    repo.read = AsyncMock(return_value=SAMPLE_TENANT_DOC)
    return repo


# ---------------------------------------------------------------------------
# TestSecretHealth — SPEC-1843
# ---------------------------------------------------------------------------

class TestSecretHealth:
    """Tests for aggregate secret health endpoint."""

    @pytest.mark.asyncio
    async def test_tenant_with_both_keys_counted(self, mock_tenant_repo):
        """Tenant with api_key_hash + widget_key_hash → counted in both (TEST-10904)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        result = await secret_health()

        assert isinstance(result, SecretHealthResponse)
        assert result.tenants_with_api_key == 1
        assert result.tenants_with_widget_key == 1
        assert result.tenants_missing_keys == 0

    @pytest.mark.asyncio
    async def test_tenant_missing_keys_counted(self, mock_tenant_repo):
        """Tenant with no key hashes → counted as missing (TEST-10904)."""
        doc_no_keys = {**SAMPLE_TENANT_DOC, "api_key_hash": None, "widget_key_hash": None}
        mock_tenant_repo.read = AsyncMock(return_value=doc_no_keys)

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        result = await secret_health()

        assert result.tenants_with_api_key == 0
        assert result.tenants_with_widget_key == 0
        assert result.tenants_missing_keys == 1

    @pytest.mark.asyncio
    async def test_no_per_tenant_detail_in_response(self, mock_tenant_repo):
        """Response must not contain per-tenant detail or PII (SPEC-1843)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        result = await secret_health()

        # Verify response model only has aggregate fields
        response_dict = result.model_dump()
        assert "tenants" not in response_dict
        assert "customer_email" not in str(response_dict)
        assert "shopify_shop_domain" not in str(response_dict)
        assert "totp_count" not in str(response_dict)

    @pytest.mark.asyncio
    async def test_read_failure_counted_as_missing(self, mock_tenant_repo):
        """If tenant doc read fails, tenant counted as missing keys."""
        mock_tenant_repo.read = AsyncMock(side_effect=Exception("Cosmos failure"))

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
        )

        result = await secret_health()

        assert result.tenants_missing_keys == 1
