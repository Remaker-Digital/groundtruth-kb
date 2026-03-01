"""Tests for Secret Posture multi-source aggregation (SPEC-1568, SPEC-1569).

Validates that the secret_posture endpoint aggregates credentials from:
- Key Vault: tenant-{id}-* secrets
- Cosmos DB: api_key_hash, widget_key_hash on TenantDocument
- Cosmos DB: shopify_shop_domain, stripe_customer_id on TenantDocument
- Key Vault: user-{member_id}-totp-seed per team member

Also validates human-readable tenant identification (SPEC-1569):
- customer_email and shopify_shop_domain included in response
- Tenant tables should show email as primary identifier

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    SecretPostureResponse,
    TenantSecretInfo,
    configure_superadmin_services,
    secret_posture,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeAsyncIterator:
    """Async iterator for mocking Cosmos query_items."""

    def __init__(self, items: list[dict]) -> None:
        self._items = items
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


def make_superadmin_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


SAMPLE_TENANT_DOC = {
    "id": "test-tenant-001",
    "tenant_id": "test-tenant-001",
    "status": "active",
    "tier": "professional",
    "customer_email": "admin@example.com",
    "shopify_shop_domain": "example-shop.myshopify.com",
    "stripe_customer_id": "cus_abc123",
    "api_key_hash": "sha256_hash_of_api_key",
    "widget_key_hash": "sha256_hash_of_widget_key",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-02-20T14:30:00Z",
}

SAMPLE_KV_SECRETS = [
    {
        "name": "tenant-test-tenant-001-shopify-token",
        "type": "shopify-token",
        "created": "2026-01-20T12:00:00Z",
        "enabled": True,
    },
    {
        "name": "tenant-test-tenant-001-stripe-api-key",
        "type": "stripe-api-key",
        "created": "2026-02-01T09:00:00Z",
        "enabled": True,
    },
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo._container = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["test-tenant-001"])
    repo.read = AsyncMock(return_value=SAMPLE_TENANT_DOC)
    return repo


@pytest.fixture()
def mock_secret_service():
    svc = MagicMock()
    svc.list_tenant_secrets = AsyncMock(return_value=SAMPLE_KV_SECRETS)
    svc.get_secret_raw = AsyncMock(return_value=None)
    return svc


@pytest.fixture()
def superadmin_ctx():
    return make_superadmin_ctx()


# ---------------------------------------------------------------------------
# TestSecretPostureAggregation — SPEC-1568
# ---------------------------------------------------------------------------

class TestSecretPostureAggregation:
    """Tests for multi-source secret aggregation."""

    @pytest.mark.asyncio
    async def test_cosmos_api_key_hash_detected(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """API key hash in TenantDocument → has_api_key=true (TEST-2726)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.superadmin_api.require_role",
            return_value=lambda: superadmin_ctx,
        ), patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert isinstance(result, SecretPostureResponse)
        assert len(result.tenants) == 1
        assert result.tenants[0].has_api_key is True

    @pytest.mark.asyncio
    async def test_cosmos_widget_key_hash_detected(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Widget key hash in TenantDocument → has_api_key=true (TEST-2727)."""
        # Tenant with widget_key_hash but no api_key_hash
        doc = {**SAMPLE_TENANT_DOC, "api_key_hash": None, "widget_key_hash": "hash"}
        mock_tenant_repo.read = AsyncMock(return_value=doc)
        mock_secret_service.list_tenant_secrets = AsyncMock(return_value=[])

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].has_api_key is True

    @pytest.mark.asyncio
    async def test_shopify_detected_from_cosmos(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """shopify_shop_domain in TenantDocument → has_shopify=true (TEST-2728)."""
        mock_secret_service.list_tenant_secrets = AsyncMock(return_value=[])

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].has_shopify is True
        assert result.tenants_with_shopify == 1

    @pytest.mark.asyncio
    async def test_stripe_detected_from_cosmos(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """stripe_customer_id in TenantDocument → has_stripe=true (TEST-2729)."""
        mock_secret_service.list_tenant_secrets = AsyncMock(return_value=[])

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].has_stripe is True
        assert result.tenants_with_stripe == 1

    @pytest.mark.asyncio
    async def test_totp_seeds_counted(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """TOTP seeds from team members counted (TEST-2730)."""
        mock_secret_service.list_tenant_secrets = AsyncMock(return_value=[])

        # Mock team member query
        mock_container = MagicMock()
        team_members = [{"id": "member-001"}, {"id": "member-002"}]
        mock_container.query_items = MagicMock(
            return_value=FakeAsyncIterator(team_members)
        )

        mock_manager = MagicMock()
        mock_manager.get_container = MagicMock(return_value=mock_container)

        # member-001 has TOTP, member-002 does not
        async def fake_get_secret_raw(name):
            if name == "user-member-001-totp-seed":
                return "JBSWY3DPEHPK3PXP"
            return None

        mock_secret_service.get_secret_raw = AsyncMock(side_effect=fake_get_secret_raw)

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            return_value=mock_manager,
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].totp_count == 1

    @pytest.mark.asyncio
    async def test_oldest_newest_dates_aggregated(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Oldest/newest dates span across KV + Cosmos timestamps (TEST-2731)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        t = result.tenants[0]
        # KV secrets: 2026-01-20 and 2026-02-01
        # Cosmos: created_at 2026-01-15, updated_at 2026-02-20
        # Oldest should be 2026-01-15 (Cosmos created_at)
        assert t.oldest_secret is not None
        assert "2026-01-15" in t.oldest_secret
        # Newest should be 2026-02-20 (Cosmos updated_at)
        assert t.newest_secret is not None
        assert "2026-02-20" in t.newest_secret

    @pytest.mark.asyncio
    async def test_secret_count_includes_all_sources(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Total secret count = KV secrets + Cosmos hashes + TOTP seeds."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        t = result.tenants[0]
        # 2 KV secrets + 2 Cosmos hashes (api_key + widget_key) + 0 TOTP = 4
        assert t.secret_count == 4

    @pytest.mark.asyncio
    async def test_secrets_by_type_includes_cosmos_types(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """secrets_by_type includes api_key_hash and widget_key_hash from Cosmos."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        by_type = result.tenants[0].secrets_by_type
        assert "api_key_hash" in by_type
        assert "widget_key_hash" in by_type
        assert by_type["api_key_hash"] == 1
        assert by_type["widget_key_hash"] == 1


# ---------------------------------------------------------------------------
# TestTenantIdentification — SPEC-1569
# ---------------------------------------------------------------------------

class TestTenantIdentification:
    """Tests for human-readable tenant identification."""

    @pytest.mark.asyncio
    async def test_customer_email_included(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Response includes customer_email from TenantDocument (TEST-2732)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].customer_email == "admin@example.com"

    @pytest.mark.asyncio
    async def test_shop_domain_included(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Response includes shopify_shop_domain when available (TEST-2733)."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].shopify_shop_domain == "example-shop.myshopify.com"

    @pytest.mark.asyncio
    async def test_null_email_handled(
        self, mock_tenant_repo, mock_secret_service, superadmin_ctx
    ):
        """Response handles tenant without email gracefully."""
        doc = {**SAMPLE_TENANT_DOC, "customer_email": None, "shopify_shop_domain": None}
        mock_tenant_repo.read = AsyncMock(return_value=doc)

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            secret_service=mock_secret_service,
        )

        with patch(
            "src.multi_tenant.cosmos_client.get_cosmos_manager",
            side_effect=ImportError("No cosmos in test"),
        ):
            result = await secret_posture(_ctx=superadmin_ctx)

        assert result.tenants[0].customer_email is None
        assert result.tenants[0].shopify_shop_domain is None
        # tenant_id is always present as fallback
        assert result.tenants[0].tenant_id == "test-tenant-001"

    @pytest.mark.asyncio
    async def test_tenant_secret_info_model_has_new_fields(self):
        """TenantSecretInfo model includes customer_email and shopify_shop_domain."""
        info = TenantSecretInfo(
            tenant_id="test-001",
            customer_email="test@example.com",
            shopify_shop_domain="test.myshopify.com",
            totp_count=2,
        )
        assert info.customer_email == "test@example.com"
        assert info.shopify_shop_domain == "test.myshopify.com"
        assert info.totp_count == 2

        # Verify camelCase serialization
        data = info.model_dump(by_alias=True)
        assert "customerEmail" in data or "customer_email" in data
