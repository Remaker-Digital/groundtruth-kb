"""
Tests for TenantSecretService — Azure Key Vault secret management.

Covers:
    - build_secret_name / parse_secret_name helpers
    - TenantSecretService CRUD (store, get, delete, rotate)
    - Raw name access (get_secret_raw, set_secret_raw, delete_secret_raw)
    - Dev-mode in-memory fallback
    - delete_all_tenant_secrets (GDPR)
    - list_tenant_secrets
    - Health check
    - Lifecycle (initialize, close)
    - KeyVaultDataStoreAdapter (GDPR export/deletion)
    - Singleton (get_secret_service)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

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

TENANT_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


# ---------------------------------------------------------------------------
# build_secret_name / parse_secret_name
# ---------------------------------------------------------------------------


class TestBuildSecretName:
    """Tests for build_secret_name."""

    def test_shopify_token(self):
        name = build_secret_name(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert name == f"tenant-{TENANT_ID}-shopify-token"

    def test_api_key_hash(self):
        name = build_secret_name(TENANT_ID, TenantSecretType.API_KEY_HASH)
        assert name == f"tenant-{TENANT_ID}-api-key-hash"

    def test_stripe_webhook(self):
        name = build_secret_name(TENANT_ID, TenantSecretType.STRIPE_WEBHOOK_SECRET)
        assert name == f"tenant-{TENANT_ID}-stripe-webhook-secret"

    def test_totp_seed(self):
        name = build_secret_name(TENANT_ID, TenantSecretType.TOTP_SEED)
        assert name == f"tenant-{TENANT_ID}-totp-seed"


class TestParseSecretName:
    """Tests for parse_secret_name."""

    def test_valid_shopify_token(self):
        result = parse_secret_name(f"tenant-{TENANT_ID}-shopify-token")
        assert result is not None
        assert result[0] == TENANT_ID
        assert result[1] == "shopify-token"

    def test_valid_api_key_hash(self):
        result = parse_secret_name(f"tenant-{TENANT_ID}-api-key-hash")
        assert result is not None
        assert result[1] == "api-key-hash"

    def test_non_tenant_prefix(self):
        result = parse_secret_name("global-secret-key")
        assert result is None

    def test_unknown_suffix(self):
        result = parse_secret_name(f"tenant-{TENANT_ID}-unknown-type")
        assert result is None

    def test_empty_tenant_id(self):
        result = parse_secret_name("tenant--shopify-token")
        assert result is None

    def test_stripe_api_key(self):
        result = parse_secret_name(f"tenant-{TENANT_ID}-stripe-api-key")
        assert result is not None
        assert result[1] == "stripe-api-key"

    def test_all_secret_types_roundtrip(self):
        """Every enum value should roundtrip through build→parse."""
        for secret_type in TenantSecretType:
            name = build_secret_name(TENANT_ID, secret_type)
            parsed = parse_secret_name(name)
            assert parsed is not None, f"Failed to parse {name}"
            assert parsed[0] == TENANT_ID
            assert parsed[1] == secret_type.value


# ---------------------------------------------------------------------------
# TenantSecretService — Dev mode
# ---------------------------------------------------------------------------


class TestTenantSecretServiceDevMode:
    """Tests for TenantSecretService in dev/in-memory mode."""

    @pytest.mark.asyncio
    async def test_initialize_dev_mode_no_vault_url(self):
        svc = TenantSecretService()
        with patch.dict("os.environ", {}, clear=True):
            # Remove AZURE_KEYVAULT_URL to trigger dev mode
            with patch.dict("os.environ", {"AZURE_KEYVAULT_URL": ""}, clear=False):
                await svc.initialize()
        assert svc._dev_mode is True
        assert svc._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.initialize()
        # Should not reinitialize
        assert svc._dev_mode is True

    @pytest.mark.asyncio
    async def test_ensure_initialized_raises(self):
        svc = TenantSecretService()
        with pytest.raises(RuntimeError, match="not initialized"):
            svc._ensure_initialized()

    @pytest.mark.asyncio
    async def test_store_and_get_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True

        name = await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "shpat_xxx")
        assert name == f"tenant-{TENANT_ID}-shopify-token"

        value = await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert value == "shpat_xxx"

    @pytest.mark.asyncio
    async def test_get_nonexistent_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        value = await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_existing_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val")
        result = await svc.delete_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        result = await svc.delete_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert result is False

    @pytest.mark.asyncio
    async def test_store_with_tags(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        name = await svc.store_secret(
            TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val",
            tags={"created_by": "test"},
        )
        assert name.startswith("tenant-")

    @pytest.mark.asyncio
    async def test_rotate_secret_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "old_val")
        name = await svc.rotate_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "new_val")
        assert name == f"tenant-{TENANT_ID}-shopify-token"
        value = await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert value == "new_val"


# ---------------------------------------------------------------------------
# Raw name access
# ---------------------------------------------------------------------------


class TestRawNameAccess:
    """Tests for get_secret_raw, set_secret_raw, delete_secret_raw."""

    @pytest.mark.asyncio
    async def test_set_and_get_raw(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.set_secret_raw("user-123-totp-seed", "JBSWY3DPEHPK3PXP")
        value = await svc.get_secret_raw("user-123-totp-seed")
        assert value == "JBSWY3DPEHPK3PXP"

    @pytest.mark.asyncio
    async def test_get_raw_nonexistent(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        value = await svc.get_secret_raw("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_raw_existing(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.set_secret_raw("test-key", "val")
        result = await svc.delete_secret_raw("test-key")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_raw_nonexistent(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        result = await svc.delete_secret_raw("nonexistent")
        assert result is False


# ---------------------------------------------------------------------------
# delete_all_tenant_secrets
# ---------------------------------------------------------------------------


class TestDeleteAllTenantSecrets:
    """Tests for delete_all_tenant_secrets (GDPR)."""

    @pytest.mark.asyncio
    async def test_dev_mode_deletes_matching(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True

        # Store some secrets for our tenant and another
        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "a")
        await svc.store_secret(TENANT_ID, TenantSecretType.API_KEY_HASH, "b")
        await svc.store_secret("other-tenant", TenantSecretType.SHOPIFY_TOKEN, "c")

        result = await svc.delete_all_tenant_secrets(TENANT_ID)
        assert len(result["deleted"]) == 2
        assert len(result["errors"]) == 0

        # Other tenant's secret should survive
        other_val = await svc.get_secret("other-tenant", TenantSecretType.SHOPIFY_TOKEN)
        assert other_val == "c"

    @pytest.mark.asyncio
    async def test_dev_mode_no_secrets_to_delete(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True

        result = await svc.delete_all_tenant_secrets(TENANT_ID)
        assert result["deleted"] == []
        assert result["not_found"] == []


# ---------------------------------------------------------------------------
# list_tenant_secrets
# ---------------------------------------------------------------------------


class TestListTenantSecrets:
    """Tests for list_tenant_secrets."""

    @pytest.mark.asyncio
    async def test_list_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True

        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "a")
        await svc.store_secret(TENANT_ID, TenantSecretType.STRIPE_API_KEY, "b")
        await svc.store_secret("other-tenant", TenantSecretType.SHOPIFY_TOKEN, "c")

        result = await svc.list_tenant_secrets(TENANT_ID)
        assert len(result) == 2
        types = {s["type"] for s in result}
        assert "shopify-token" in types
        assert "stripe-api-key" in types

    @pytest.mark.asyncio
    async def test_list_empty_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        result = await svc.list_tenant_secrets(TENANT_ID)
        assert result == []


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for health_check."""

    @pytest.mark.asyncio
    async def test_not_initialized(self):
        svc = TenantSecretService()
        result = await svc.health_check()
        assert result["status"] == "not_initialized"

    @pytest.mark.asyncio
    async def test_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        svc._dev_store["key"] = "val"
        result = await svc.health_check()
        assert result["status"] == "dev_mode"
        assert result["secret_count"] == 1

    @pytest.mark.asyncio
    async def test_dev_mode_empty(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        result = await svc.health_check()
        assert result["status"] == "dev_mode"
        assert result["secret_count"] == 0


# ---------------------------------------------------------------------------
# Lifecycle (close)
# ---------------------------------------------------------------------------


class TestLifecycle:
    """Tests for close."""

    @pytest.mark.asyncio
    async def test_close_dev_mode(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        svc._dev_store["key"] = "val"
        await svc.close()
        assert svc._initialized is False
        assert svc._dev_store == {}

    @pytest.mark.asyncio
    async def test_close_with_client(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._client = AsyncMock()
        await svc.close()
        svc._client is None
        assert svc._initialized is False

    @pytest.mark.asyncio
    async def test_close_no_client(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._client = None
        # Should not raise
        await svc.close()
        assert svc._initialized is False


# ---------------------------------------------------------------------------
# Initialize with Key Vault — import failure paths
# ---------------------------------------------------------------------------


class TestInitializeKeyVault:
    """Tests for initialize with Key Vault client creation paths."""

    @pytest.mark.asyncio
    async def test_initialize_import_error_fallback(self):
        svc = TenantSecretService()
        with patch.dict(
            "os.environ",
            {"AZURE_KEYVAULT_URL": "https://kv-test.vault.azure.net/"},
        ):
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No azure module"),
            ):
                await svc.initialize()
        assert svc._dev_mode is True
        assert svc._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_generic_error_fallback(self):
        svc = TenantSecretService()
        with patch.dict(
            "os.environ",
            {"AZURE_KEYVAULT_URL": "https://kv-test.vault.azure.net/"},
        ):
            # Patch the lazy import to raise a generic error
            with patch.dict("sys.modules", {"azure.identity.aio": MagicMock(), "azure.keyvault.secrets.aio": MagicMock()}):
                with patch(
                    "builtins.__import__",
                    side_effect=RuntimeError("Connection failed"),
                ):
                    await svc.initialize()
        assert svc._dev_mode is True
        assert svc._initialized is True


# ---------------------------------------------------------------------------
# Key Vault client mode (mocked client)
# ---------------------------------------------------------------------------


class TestKeyVaultClientMode:
    """Tests with a mocked Key Vault client (non-dev mode)."""

    @pytest.mark.asyncio
    async def test_store_secret_kv(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        svc._client = MagicMock()
        svc._client.set_secret = AsyncMock()

        name = await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val")
        assert name == f"tenant-{TENANT_ID}-shopify-token"
        svc._client.set_secret.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_store_secret_kv_error(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        svc._client = MagicMock()
        svc._client.set_secret = AsyncMock(side_effect=Exception("KV error"))

        with pytest.raises(Exception, match="KV error"):
            await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val")

    @pytest.mark.asyncio
    async def test_get_secret_kv_found(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        mock_secret = MagicMock()
        mock_secret.value = "secret_val"
        svc._client = MagicMock()
        svc._client.get_secret = AsyncMock(return_value=mock_secret)

        value = await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert value == "secret_val"

    @pytest.mark.asyncio
    async def test_get_secret_kv_not_found(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        class ResourceNotFoundError(Exception):
            pass

        svc._client = MagicMock()
        svc._client.get_secret = AsyncMock(side_effect=ResourceNotFoundError("Not found"))

        value = await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert value is None

    @pytest.mark.asyncio
    async def test_get_secret_kv_other_error(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        svc._client = MagicMock()
        svc._client.get_secret = AsyncMock(side_effect=ValueError("Unexpected"))

        with pytest.raises(ValueError, match="Unexpected"):
            await svc.get_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)

    @pytest.mark.asyncio
    async def test_delete_secret_kv_success(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        poller = AsyncMock()
        svc._client = MagicMock()
        svc._client.begin_delete_secret = AsyncMock(return_value=poller)

        result = await svc.delete_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_secret_kv_not_found(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        class ResourceNotFoundError(Exception):
            pass

        svc._client = MagicMock()
        svc._client.begin_delete_secret = AsyncMock(
            side_effect=ResourceNotFoundError("Not found"),
        )

        result = await svc.delete_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_secret_kv_other_error(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        svc._client = MagicMock()
        svc._client.begin_delete_secret = AsyncMock(
            side_effect=ValueError("Unexpected"),
        )

        with pytest.raises(ValueError, match="Unexpected"):
            await svc.delete_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN)

    @pytest.mark.asyncio
    async def test_get_secret_raw_kv(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        mock_secret = MagicMock()
        mock_secret.value = "raw_val"
        svc._client = MagicMock()
        svc._client.get_secret = AsyncMock(return_value=mock_secret)

        value = await svc.get_secret_raw("user-123-totp-seed")
        assert value == "raw_val"

    @pytest.mark.asyncio
    async def test_get_secret_raw_kv_not_found(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        class ResourceNotFoundError(Exception):
            pass

        svc._client = MagicMock()
        svc._client.get_secret = AsyncMock(side_effect=ResourceNotFoundError("Not found"))

        value = await svc.get_secret_raw("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_secret_raw_kv(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        svc._client = MagicMock()
        svc._client.set_secret = AsyncMock()

        await svc.set_secret_raw("user-123-totp-seed", "seed_val")
        svc._client.set_secret.assert_awaited_once_with("user-123-totp-seed", "seed_val")

    @pytest.mark.asyncio
    async def test_delete_raw_kv_success(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False
        poller = AsyncMock()
        svc._client = MagicMock()
        svc._client.begin_delete_secret = AsyncMock(return_value=poller)

        result = await svc.delete_secret_raw("test-key")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_raw_kv_not_found(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        class ResourceNotFoundError(Exception):
            pass

        svc._client = MagicMock()
        svc._client.begin_delete_secret = AsyncMock(
            side_effect=ResourceNotFoundError("Not found"),
        )

        result = await svc.delete_secret_raw("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_kv_healthy(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        # list_properties_of_secrets is an async generator
        async def mock_gen():
            yield MagicMock(name="test-secret")

        svc._client = MagicMock()
        svc._client.list_properties_of_secrets = mock_gen

        result = await svc.health_check()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_kv_unhealthy(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = False

        async def mock_gen():
            raise ConnectionError("Cannot connect")
            yield  # makes this an async generator (unreachable by design)

        svc._client = MagicMock()
        svc._client.list_properties_of_secrets = mock_gen

        result = await svc.health_check()
        assert result["status"] == "unhealthy"


# ---------------------------------------------------------------------------
# KeyVaultDataStoreAdapter
# ---------------------------------------------------------------------------


class TestKeyVaultDataStoreAdapter:
    """Tests for the GDPR DataStoreAdapter implementation."""

    def test_store_name(self):
        svc = TenantSecretService()
        adapter = KeyVaultDataStoreAdapter(svc)
        assert adapter.store_name == "key_vault"

    @pytest.mark.asyncio
    async def test_export_tenant_data(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val")

        adapter = KeyVaultDataStoreAdapter(svc)
        result = await adapter.export_tenant_data(TENANT_ID)
        assert result["store"] == "key_vault"
        assert result["secret_count"] == 1

    @pytest.mark.asyncio
    async def test_export_customer_data_empty(self):
        svc = TenantSecretService()
        adapter = KeyVaultDataStoreAdapter(svc)
        result = await adapter.export_customer_data(TENANT_ID, "cust-123")
        assert result["store"] == "key_vault"
        assert result["data"] == {}

    @pytest.mark.asyncio
    async def test_delete_tenant_data(self):
        svc = TenantSecretService()
        svc._initialized = True
        svc._dev_mode = True
        await svc.store_secret(TENANT_ID, TenantSecretType.SHOPIFY_TOKEN, "val")

        adapter = KeyVaultDataStoreAdapter(svc)
        result = await adapter.delete_tenant_data(TENANT_ID)
        assert result["store"] == "key_vault"
        assert result["deleted_count"] == 1

    @pytest.mark.asyncio
    async def test_delete_customer_data_noop(self):
        svc = TenantSecretService()
        adapter = KeyVaultDataStoreAdapter(svc)
        result = await adapter.delete_customer_data(TENANT_ID, "cust-123")
        assert result["store"] == "key_vault"
        assert result["deleted_count"] == 0


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestGetSecretService:
    """Tests for get_secret_service singleton."""

    def test_returns_instance(self):
        import src.multi_tenant.tenant_secret_service as mod
        old = mod._service
        try:
            mod._service = None
            svc = get_secret_service()
            assert isinstance(svc, TenantSecretService)
        finally:
            mod._service = old

    def test_returns_same_instance(self):
        import src.multi_tenant.tenant_secret_service as mod
        old = mod._service
        try:
            mod._service = None
            a = get_secret_service()
            b = get_secret_service()
            assert a is b
        finally:
            mod._service = old
