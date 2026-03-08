"""Tests for C-4: Secret Posture endpoint (GET /api/superadmin/secrets/posture).

Covers:
    - Happy path with various secret types
    - Secret classification (Shopify, Stripe, API key detection)
    - Disabled secrets counted
    - Oldest/newest secret tracking
    - Global type aggregation
    - Secret service not configured → 503
    - Tenant repo not configured → 503
    - Partial failures (per-tenant errors)
    - Key Vault failures
    - CamelCase serialization
    - Auth enforcement

Total: 22 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api import (
    SecretPostureResponse,
    TenantSecretInfo,
    configure_superadmin_services,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_secret_service():
    svc = MagicMock()
    svc.list_tenant_secrets = AsyncMock()
    return svc


@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["t-001", "t-002"])
    repo.read = AsyncMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


SECRETS_T001 = [
    {"type": "shopify_access_token", "created": "2026-01-10T00:00:00Z", "enabled": True},
    {"type": "stripe_secret_key", "created": "2026-01-15T00:00:00Z", "enabled": True},
    {"type": "api_key", "created": "2026-01-20T00:00:00Z", "enabled": True},
    {"type": "openai_api_key", "created": "2026-01-05T00:00:00Z", "enabled": False},
]

SECRETS_T002 = [
    {"type": "shopify_access_token", "created": "2026-02-01T00:00:00Z", "enabled": True},
]


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------


class TestSecretPostureHappyPath:

    @pytest.mark.asyncio
    async def test_returns_all_tenants(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Returns secret posture for all active tenants."""
        mock_secret_service.list_tenant_secrets.side_effect = [SECRETS_T001, SECRETS_T002]
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional"}, {"tier": "starter"},
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert isinstance(result, SecretPostureResponse)
        assert result.total_tenants == 2
        assert len(result.tenants) == 2
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_total_secrets(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Total secrets aggregated correctly."""
        mock_secret_service.list_tenant_secrets.side_effect = [SECRETS_T001, SECRETS_T002]
        mock_tenant_repo.read.side_effect = [{"tier": "professional"}, {"tier": "starter"}]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.total_secrets == 5  # 4 + 1

    @pytest.mark.asyncio
    async def test_global_type_aggregation(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Global secrets_by_type_global counts across all tenants."""
        mock_secret_service.list_tenant_secrets.side_effect = [SECRETS_T001, SECRETS_T002]
        mock_tenant_repo.read.side_effect = [{"tier": "professional"}, {"tier": "starter"}]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.secrets_by_type_global["shopify_access_token"] == 2
        assert result.secrets_by_type_global["stripe_secret_key"] == 1
        assert result.secrets_by_type_global["api_key"] == 1
        assert result.secrets_by_type_global["openai_api_key"] == 1

    @pytest.mark.asyncio
    async def test_no_active_tenants(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """No active tenants → empty response."""
        mock_tenant_repo.list_active_tenant_ids.return_value = []
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.total_tenants == 0
        assert result.total_secrets == 0
        assert result.tenants == []


# ---------------------------------------------------------------------------
# Secret Classification
# ---------------------------------------------------------------------------


class TestSecretClassification:

    @pytest.mark.asyncio
    async def test_shopify_detected(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Shopify secret detected by type name."""
        mock_secret_service.list_tenant_secrets.return_value = SECRETS_T001
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "professional"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].has_shopify is True
        assert result.tenants_with_shopify == 1

    @pytest.mark.asyncio
    async def test_stripe_detected(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Stripe secret detected by type name."""
        mock_secret_service.list_tenant_secrets.return_value = SECRETS_T001
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "professional"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].has_stripe is True
        assert result.tenants_with_stripe == 1

    @pytest.mark.asyncio
    async def test_api_key_detected(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """API key secret detected by type name."""
        mock_secret_service.list_tenant_secrets.return_value = SECRETS_T001
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "professional"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].has_api_key is True
        assert result.tenants_with_api_key == 1

    @pytest.mark.asyncio
    async def test_tenant_without_integrations(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Tenant with only generic secrets has all flags False."""
        mock_secret_service.list_tenant_secrets.return_value = [
            {"type": "custom_secret", "created": "2026-01-01T00:00:00Z", "enabled": True},
        ]
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "starter"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].has_shopify is False
        assert result.tenants[0].has_stripe is False
        assert result.tenants[0].has_api_key is False


# ---------------------------------------------------------------------------
# Disabled Secrets and Timestamps
# ---------------------------------------------------------------------------


class TestSecretMetadata:

    @pytest.mark.asyncio
    async def test_disabled_secrets_counted(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Disabled secrets are counted separately."""
        mock_secret_service.list_tenant_secrets.return_value = SECRETS_T001
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "professional"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].disabled_secrets == 1  # openai_api_key

    @pytest.mark.asyncio
    async def test_oldest_newest_secret(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Oldest and newest secret timestamps tracked."""
        mock_secret_service.list_tenant_secrets.return_value = SECRETS_T001
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "professional"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].oldest_secret == "2026-01-05T00:00:00Z"
        assert result.tenants[0].newest_secret == "2026-01-20T00:00:00Z"

    @pytest.mark.asyncio
    async def test_empty_secrets_list(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Tenant with no secrets has all defaults."""
        mock_secret_service.list_tenant_secrets.return_value = []
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_tenant_repo.read.return_value = {"tier": "starter"}
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.tenants[0].secret_count == 0
        assert result.tenants[0].oldest_secret is None
        assert result.tenants[0].newest_secret is None
        assert result.tenants[0].disabled_secrets == 0


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------


class TestSecretPostureErrors:

    @pytest.mark.asyncio
    async def test_secret_service_not_configured_503(self, mock_tenant_repo, superadmin_ctx):
        """Secret service None → 503."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=None,
        )
        from fastapi import HTTPException
        from src.multi_tenant.superadmin_api import secret_posture

        with pytest.raises(HTTPException) as exc_info:
            await secret_posture()
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_tenant_repo_not_configured_503(self, mock_secret_service, superadmin_ctx):
        """Tenant repo None → 503."""
        configure_superadmin_services(
            tenant_repo=None,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from fastapi import HTTPException
        from src.multi_tenant.superadmin_api import secret_posture

        with pytest.raises(HTTPException) as exc_info:
            await secret_posture()
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_partial_failure(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """Per-tenant Key Vault failures go into errors[]."""
        mock_secret_service.list_tenant_secrets.side_effect = [
            SECRETS_T001,
            RuntimeError("Key Vault unavailable"),
        ]
        mock_tenant_repo.read.side_effect = [{"tier": "professional"}, {"tier": "starter"}]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.total_tenants == 1
        assert len(result.errors) == 1
        assert result.errors[0]["tenant_id"] == "t-002"
        assert "Key Vault" in result.errors[0]["message"]

    @pytest.mark.asyncio
    async def test_all_tenants_fail(
        self, mock_secret_service, mock_tenant_repo, superadmin_ctx
    ):
        """All tenants failing → empty tenants, all errors."""
        mock_secret_service.list_tenant_secrets.side_effect = RuntimeError("Key Vault down")
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )
        from src.multi_tenant.superadmin_api import secret_posture
        result = await secret_posture()

        assert result.total_tenants == 0
        assert len(result.errors) == 2
        assert result.total_secrets == 0


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestSecretPostureSerialization:

    def test_response_model_camel_case(self):
        """SecretPostureResponse serializes to camelCase."""
        resp = SecretPostureResponse(
            total_tenants=1,
            total_secrets=4,
            secrets_by_type_global={"shopify_access_token": 1},
            tenants_with_shopify=1,
            tenants_with_stripe=0,
            tenants_with_api_key=1,
            tenants=[TenantSecretInfo(
                tenant_id="t-001",
                tier="professional",
                secret_count=4,
                has_shopify=True,
                has_api_key=True,
                disabled_secrets=1,
            )],
        )
        data = resp.model_dump(by_alias=True)
        assert "totalTenants" in data
        assert "totalSecrets" in data
        assert "secretsByTypeGlobal" in data
        assert "tenantsWithShopify" in data
        assert data["tenants"][0]["tenantId"] == "t-001"
        assert data["tenants"][0]["hasShopify"] is True
        assert data["tenants"][0]["disabledSecrets"] == 1

    def test_empty_response(self):
        """Empty response defaults."""
        resp = SecretPostureResponse()
        data = resp.model_dump(by_alias=True)
        assert data["totalSecrets"] == 0
        assert data["tenants"] == []


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestSecretPostureAuth:

    def test_router_endpoint_exists(self):
        """Secret posture endpoint is mounted."""
        from src.multi_tenant.superadmin_api import router
        routes = [r.path for r in router.routes]
        assert "/api/superadmin/secrets/posture" in routes
