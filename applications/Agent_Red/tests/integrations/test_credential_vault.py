"""Tests for Two-Layer Credential Vault (SPEC-1765).

Tests cover: initialization, store/get/delete credentials, rotation,
DEK caching, per-tenant isolation, GDPR bulk delete, list credentials.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.integrations.credential_vault import (
    CredentialVault,
    FernetCipher,
    IntegrationSecretType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_KEK = b"test-master-key-for-credential-v"  # 32 bytes


@pytest.fixture
async def vault() -> CredentialVault:
    v = CredentialVault()
    await v.initialize(kek_override=TEST_KEK)
    return v


# ===================================================================
# FernetCipher
# ===================================================================


class TestFernetCipher:
    """SPEC-1765: Fernet encryption layer."""

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Encrypted data can be decrypted back to original."""
        cipher = FernetCipher(TEST_KEK)
        plaintext = "my-secret-token-12345"
        ciphertext = cipher.encrypt(plaintext)
        assert ciphertext != plaintext
        assert cipher.decrypt(ciphertext) == plaintext

    def test_different_keys_cannot_decrypt(self) -> None:
        """Data encrypted with one key cannot be decrypted with another."""
        cipher1 = FernetCipher(b"key-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        cipher2 = FernetCipher(b"key-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        ciphertext = cipher1.encrypt("secret")
        with pytest.raises(Exception):
            cipher2.decrypt(ciphertext)

    def test_empty_string(self) -> None:
        """Empty string encrypts and decrypts correctly."""
        cipher = FernetCipher(TEST_KEK)
        assert cipher.decrypt(cipher.encrypt("")) == ""

    def test_unicode_content(self) -> None:
        """Unicode content encrypts and decrypts correctly."""
        cipher = FernetCipher(TEST_KEK)
        text = "token with unicode: 日本語 émojis 🔑"
        assert cipher.decrypt(cipher.encrypt(text)) == text


# ===================================================================
# CredentialVault Initialization
# ===================================================================


class TestVaultInitialization:
    """SPEC-1765: Vault initialization."""

    @pytest.mark.asyncio
    async def test_initialize_dev_mode(self) -> None:
        """Vault initializes in dev mode without Key Vault URL."""
        vault = CredentialVault()
        await vault.initialize(kek_override=TEST_KEK)
        assert vault._initialized is True
        assert vault._dev_mode is True

    @pytest.mark.asyncio
    async def test_double_initialize_is_noop(self) -> None:
        """Second initialize call is a no-op."""
        vault = CredentialVault()
        await vault.initialize(kek_override=TEST_KEK)
        kek1 = vault._kek
        await vault.initialize(kek_override=b"different-key-000000000000000000")
        assert vault._kek is kek1  # Unchanged

    @pytest.mark.asyncio
    async def test_not_initialized_raises(self) -> None:
        """Operations before initialize raise RuntimeError."""
        vault = CredentialVault()
        with pytest.raises(RuntimeError, match="not initialized"):
            await vault.store_credential(
                "t-1", "z", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "val"
            )


# ===================================================================
# Store / Get / Delete
# ===================================================================


class TestCredentialCRUD:
    """SPEC-1765: Credential CRUD operations."""

    @pytest.mark.asyncio
    async def test_store_and_get(self, vault: CredentialVault) -> None:
        """Store a credential and retrieve it."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "my-token"
        )
        result = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert result == "my-token"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, vault: CredentialVault) -> None:
        """Getting a nonexistent credential returns None."""
        result = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_store_overwrites(self, vault: CredentialVault) -> None:
        """Storing the same credential again overwrites the old value."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "old"
        )
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "new"
        )
        result = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert result == "new"

    @pytest.mark.asyncio
    async def test_delete_credential(self, vault: CredentialVault) -> None:
        """Delete removes the credential."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "token"
        )
        deleted = await vault.delete_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert deleted is True
        result = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, vault: CredentialVault) -> None:
        """Deleting a nonexistent credential returns False."""
        result = await vault.delete_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_multiple_secret_types(self, vault: CredentialVault) -> None:
        """Different secret types are stored independently."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "access"
        )
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_REFRESH_TOKEN, "refresh"
        )
        access = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        )
        refresh = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_REFRESH_TOKEN
        )
        assert access == "access"
        assert refresh == "refresh"


# ===================================================================
# Tenant Isolation
# ===================================================================


class TestTenantIsolation:
    """SPEC-1765: Per-tenant credential isolation."""

    @pytest.mark.asyncio
    async def test_tenant_isolation(self, vault: CredentialVault) -> None:
        """Different tenants have independent credentials."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "token-1"
        )
        await vault.store_credential(
            "t-2", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "token-2"
        )
        assert await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        ) == "token-1"
        assert await vault.get_credential(
            "t-2", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN
        ) == "token-2"

    @pytest.mark.asyncio
    async def test_per_tenant_dek(self, vault: CredentialVault) -> None:
        """Each tenant gets a separate DEK."""
        vault._get_or_create_dek("t-1")
        vault._get_or_create_dek("t-2")
        assert "t-1" in vault._dek_cache
        assert "t-2" in vault._dek_cache
        # Different ciphers
        assert vault._dek_cache["t-1"] is not vault._dek_cache["t-2"]


# ===================================================================
# Rotation
# ===================================================================


class TestRotation:
    """SPEC-1765: Credential rotation."""

    @pytest.mark.asyncio
    async def test_rotate_credential(self, vault: CredentialVault) -> None:
        """Rotation replaces the credential value."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.INTEGRATION_API_KEY, "old-key"
        )
        await vault.rotate_credential(
            "t-1", "zendesk", IntegrationSecretType.INTEGRATION_API_KEY, "new-key"
        )
        result = await vault.get_credential(
            "t-1", "zendesk", IntegrationSecretType.INTEGRATION_API_KEY
        )
        assert result == "new-key"


# ===================================================================
# List / Bulk Delete
# ===================================================================


class TestListAndBulkDelete:
    """SPEC-1765: List and GDPR bulk delete."""

    @pytest.mark.asyncio
    async def test_list_credentials(self, vault: CredentialVault) -> None:
        """List returns metadata without values."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "a"
        )
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_REFRESH_TOKEN, "b"
        )
        await vault.store_credential(
            "t-1", "slack", IntegrationSecretType.INTEGRATION_API_KEY, "c"
        )
        results = await vault.list_credentials("t-1")
        assert len(results) == 3
        # No values exposed
        for r in results:
            assert "encrypted_value" not in r
            assert "secret_type" in r

    @pytest.mark.asyncio
    async def test_list_filtered_by_integration(self, vault: CredentialVault) -> None:
        """List can filter by integration_id."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "a"
        )
        await vault.store_credential(
            "t-1", "slack", IntegrationSecretType.INTEGRATION_API_KEY, "b"
        )
        results = await vault.list_credentials("t-1", integration_id="zendesk")
        assert len(results) == 1
        assert results[0]["integration_id"] == "zendesk"

    @pytest.mark.asyncio
    async def test_delete_all_tenant_credentials(self, vault: CredentialVault) -> None:
        """Bulk delete removes all tenant credentials and DEK."""
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "a"
        )
        await vault.store_credential(
            "t-1", "slack", IntegrationSecretType.INTEGRATION_API_KEY, "b"
        )
        await vault.store_credential(
            "t-2", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "c"
        )

        deleted = await vault.delete_all_tenant_credentials("t-1")
        assert deleted == 2
        assert vault.credential_count("t-1") == 0
        # t-2 untouched
        assert vault.credential_count("t-2") == 1
        # DEK cache cleared for t-1
        assert "t-1" not in vault._dek_cache

    @pytest.mark.asyncio
    async def test_credential_count(self, vault: CredentialVault) -> None:
        """credential_count returns correct counts."""
        assert vault.credential_count() == 0
        await vault.store_credential(
            "t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "a"
        )
        assert vault.credential_count() == 1
        assert vault.credential_count("t-1") == 1
        assert vault.credential_count("t-2") == 0


# ===================================================================
# IntegrationSecretType
# ===================================================================


class TestIntegrationSecretType:
    """SPEC-1765: TenantSecretType extensions."""

    def test_enum_values(self) -> None:
        """All required secret types exist."""
        assert IntegrationSecretType.OAUTH_ACCESS_TOKEN.value == "oauth-access-token"
        assert IntegrationSecretType.OAUTH_REFRESH_TOKEN.value == "oauth-refresh-token"
        assert IntegrationSecretType.INTEGRATION_API_KEY.value == "integration-api-key"
        assert IntegrationSecretType.INTEGRATION_WEBHOOK_SECRET.value == "integration-webhook-secret"

    def test_enum_count(self) -> None:
        """Four integration secret types defined."""
        assert len(IntegrationSecretType) == 4
