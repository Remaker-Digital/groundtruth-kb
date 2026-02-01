"""Tenant Secret Service tests — Key Vault per-tenant secret management (SS-01 to SS-15).

Tests SS-01 through SS-15 from COMPREHENSIVE-TEST-PLAN.md §5 (P1 pre-launch).

Validates:
    - TenantSecretType enum values
    - Secret name construction and parsing
    - TenantSecretService dev-mode operations (store, get, delete, list, rotate)
    - delete_all_tenant_secrets
    - KeyVaultDataStoreAdapter GDPR integration
    - Health check
    - Singleton lifecycle

Work Item #29 (Decision #6).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.tenant_secret_service import (
    KeyVaultDataStoreAdapter,
    TenantSecretService,
    TenantSecretType,
    build_secret_name,
    get_secret_service,
    parse_secret_name,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "abc123-def456-ghi789"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
async def dev_service():
    """TenantSecretService initialized in dev mode (no AZURE_KEYVAULT_URL)."""
    service = TenantSecretService()
    await service.initialize()
    assert service._dev_mode is True
    yield service
    await service.close()


# ---------------------------------------------------------------------------
# Secret name tests
# ---------------------------------------------------------------------------

class TestSecretNameConstruction:
    """Secret name building and parsing."""

    def test_ss01_build_secret_name_format(self):
        """SS-01: build_secret_name produces tenant-{id}-{type} format."""
        name = build_secret_name("t-123", TenantSecretType.SHOPIFY_TOKEN)
        assert name == "tenant-t-123-shopify-token"

    def test_ss02_build_name_all_types(self):
        """SS-02: build_secret_name works for all enum types."""
        for secret_type in TenantSecretType:
            name = build_secret_name("tid", secret_type)
            assert name.startswith("tenant-tid-")
            assert name.endswith(f"-{secret_type.value}")

    def test_ss03_parse_secret_name_roundtrip(self):
        """SS-03: parse_secret_name reverses build_secret_name."""
        for secret_type in TenantSecretType:
            name = build_secret_name(TENANT_ID, secret_type)
            result = parse_secret_name(name)
            assert result is not None
            assert result[0] == TENANT_ID
            assert result[1] == secret_type.value

    def test_ss04_parse_non_tenant_name_returns_none(self):
        """SS-04: parse_secret_name returns None for non-tenant secrets."""
        assert parse_secret_name("global-api-key") is None
        assert parse_secret_name("") is None
        assert parse_secret_name("tenant-") is None


# ---------------------------------------------------------------------------
# TenantSecretType enum
# ---------------------------------------------------------------------------

class TestTenantSecretType:
    """Enum value validation."""

    def test_ss05_enum_has_expected_types(self):
        """SS-05: TenantSecretType contains all required secret types."""
        expected = {
            "shopify-token", "shopify-webhook-secret",
            "stripe-api-key", "stripe-webhook-secret",
            "api-key-hash", "openai-api-key",
            "zendesk-api-token", "mailchimp-api-key",
            "cmk-key-id", "webhook-signing-secret",
        }
        actual = {t.value for t in TenantSecretType}
        assert expected == actual

    def test_ss06_enum_is_str_enum(self):
        """SS-06: TenantSecretType is a str enum (usable as string)."""
        assert isinstance(TenantSecretType.SHOPIFY_TOKEN, str)
        assert TenantSecretType.SHOPIFY_TOKEN == "shopify-token"


# ---------------------------------------------------------------------------
# Dev mode operations
# ---------------------------------------------------------------------------

class TestDevModeOperations:
    """Service operations in development (in-memory) mode."""

    async def test_ss07_store_and_get(self, dev_service):
        """SS-07: Store and retrieve a secret in dev mode."""
        name = await dev_service.store_secret(
            TENANT_ID,
            TenantSecretType.SHOPIFY_TOKEN,
            "shpat_test123",
        )
        assert "shopify-token" in name

        value = await dev_service.get_secret(
            TENANT_ID,
            TenantSecretType.SHOPIFY_TOKEN,
        )
        assert value == "shpat_test123"

    async def test_ss08_get_nonexistent_returns_none(self, dev_service):
        """SS-08: get_secret returns None for missing secret."""
        value = await dev_service.get_secret(
            TENANT_ID,
            TenantSecretType.ZENDESK_API_TOKEN,
        )
        assert value is None

    async def test_ss09_delete_existing(self, dev_service):
        """SS-09: delete_secret returns True when secret exists."""
        await dev_service.store_secret(
            TENANT_ID,
            TenantSecretType.STRIPE_API_KEY,
            "sk_test_xxx",
        )
        deleted = await dev_service.delete_secret(
            TENANT_ID,
            TenantSecretType.STRIPE_API_KEY,
        )
        assert deleted is True

        # Confirm gone
        value = await dev_service.get_secret(
            TENANT_ID,
            TenantSecretType.STRIPE_API_KEY,
        )
        assert value is None

    async def test_ss10_delete_nonexistent_returns_false(self, dev_service):
        """SS-10: delete_secret returns False when secret doesn't exist."""
        deleted = await dev_service.delete_secret(
            TENANT_ID,
            TenantSecretType.CMK_KEY_ID,
        )
        assert deleted is False

    async def test_ss11_list_tenant_secrets(self, dev_service):
        """SS-11: list_tenant_secrets returns metadata for all tenant secrets."""
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val1",
        )
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.STRIPE_API_KEY, "val2",
        )
        # Different tenant — should not appear
        await dev_service.store_secret(
            "other-tenant", TenantSecretType.SHOPIFY_TOKEN, "other",
        )

        secrets = await dev_service.list_tenant_secrets(TENANT_ID)
        assert len(secrets) == 2
        types = {s["type"] for s in secrets}
        assert "shopify-token" in types
        assert "stripe-api-key" in types

    async def test_ss12_delete_all_tenant_secrets(self, dev_service):
        """SS-12: delete_all_tenant_secrets removes only target tenant."""
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val1",
        )
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.STRIPE_API_KEY, "val2",
        )
        await dev_service.store_secret(
            "keep-tenant", TenantSecretType.SHOPIFY_TOKEN, "keep",
        )

        result = await dev_service.delete_all_tenant_secrets(TENANT_ID)
        assert len(result["deleted"]) == 2
        assert len(result["errors"]) == 0

        # Target tenant secrets gone
        remaining = await dev_service.list_tenant_secrets(TENANT_ID)
        assert len(remaining) == 0

        # Other tenant untouched
        other = await dev_service.list_tenant_secrets("keep-tenant")
        assert len(other) == 1

    async def test_ss13_rotate_secret(self, dev_service):
        """SS-13: rotate_secret stores a new value (version)."""
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.OPENAI_API_KEY, "old-key",
        )
        await dev_service.rotate_secret(
            TENANT_ID, TenantSecretType.OPENAI_API_KEY, "new-key",
        )
        value = await dev_service.get_secret(
            TENANT_ID, TenantSecretType.OPENAI_API_KEY,
        )
        assert value == "new-key"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """Health check endpoint integration."""

    async def test_ss14_health_check_dev_mode(self, dev_service):
        """SS-14: health_check returns dev_mode status."""
        health = await dev_service.health_check()
        assert health["status"] == "dev_mode"
        assert "secret_count" in health

    async def test_ss14b_health_check_not_initialized(self):
        """SS-14b: health_check returns not_initialized before init."""
        service = TenantSecretService()
        health = await service.health_check()
        assert health["status"] == "not_initialized"


# ---------------------------------------------------------------------------
# KeyVaultDataStoreAdapter (GDPR)
# ---------------------------------------------------------------------------

class TestKeyVaultDataStoreAdapter:
    """GDPR data store adapter for Key Vault."""

    async def test_ss15_adapter_export_tenant_data(self, dev_service):
        """SS-15: Adapter exports secret metadata (not values)."""
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "secret-val",
        )

        adapter = KeyVaultDataStoreAdapter(dev_service)
        assert adapter.store_name == "key_vault"

        export = await adapter.export_tenant_data(TENANT_ID)
        assert export["store"] == "key_vault"
        assert export["secret_count"] == 1
        # Values must not be exported
        for s in export["secrets"]:
            assert "value" not in s

    async def test_ss15b_adapter_delete_tenant_data(self, dev_service):
        """SS-15b: Adapter deletes all tenant secrets via GDPR flow."""
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val1",
        )
        await dev_service.store_secret(
            TENANT_ID, TenantSecretType.STRIPE_API_KEY, "val2",
        )

        adapter = KeyVaultDataStoreAdapter(dev_service)
        result = await adapter.delete_tenant_data(TENANT_ID)
        assert result["store"] == "key_vault"
        assert result["deleted_count"] == 2

    async def test_ss15c_adapter_customer_operations_noop(self, dev_service):
        """SS-15c: Customer-level operations are no-ops for Key Vault."""
        adapter = KeyVaultDataStoreAdapter(dev_service)

        export = await adapter.export_customer_data(TENANT_ID, "cust-1")
        assert export["data"] == {}

        delete = await adapter.delete_customer_data(TENANT_ID, "cust-1")
        assert delete["deleted_count"] == 0


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

class TestSingleton:
    """Module-level singleton lifecycle."""

    def test_ss_singleton_returns_same_instance(self):
        """get_secret_service returns the same instance."""
        s1 = get_secret_service()
        s2 = get_secret_service()
        assert s1 is s2

    async def test_ss_uninitialized_raises(self):
        """Operations before initialize() raise RuntimeError."""
        service = TenantSecretService()
        with pytest.raises(RuntimeError, match="not initialized"):
            await service.store_secret(
                "t", TenantSecretType.SHOPIFY_TOKEN, "v",
            )
