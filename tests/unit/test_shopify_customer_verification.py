"""Unit tests for Shopify customer HMAC verification (AUTH-4).

Tests the HMAC-SHA256 identity verification in
src/multi_tenant/shopify_customer_verification.py.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.multi_tenant.shopify_customer_verification import (
    generate_identity_secret,
    verify_shopify_customer_hmac,
)


# ---------------------------------------------------------------------------
# Identity secret generation
# ---------------------------------------------------------------------------


class TestGenerateIdentitySecret:
    """Test identity secret generation."""

    def test_generates_64_char_hex(self):
        """Secret should be a 64-character hex string (32 bytes)."""
        secret = generate_identity_secret()
        assert len(secret) == 64
        assert all(c in "0123456789abcdef" for c in secret)

    def test_generates_unique_secrets(self):
        """Each call should produce a unique secret."""
        secrets_set = {generate_identity_secret() for _ in range(20)}
        assert len(secrets_set) == 20

    def test_secret_is_valid_hmac_key(self):
        """Generated secret should work as an HMAC-SHA256 key."""
        secret = generate_identity_secret()
        result = hmac.new(
            secret.encode("utf-8"),
            b"test-customer-id",
            hashlib.sha256,
        ).hexdigest()
        assert len(result) == 64


# ---------------------------------------------------------------------------
# HMAC verification
# ---------------------------------------------------------------------------


class TestVerifyShopifyCustomerHmac:
    """Test HMAC-SHA256 verification of Shopify customer identity."""

    @pytest.mark.asyncio
    async def test_valid_hmac_returns_true(self):
        """A correctly signed customer_id should verify."""
        test_secret = "abcdef1234567890abcdef1234567890"
        customer_id = "7654321012345"

        # Compute the expected HMAC
        expected_hmac = hmac.new(
            test_secret.encode("utf-8"),
            customer_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=test_secret)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id=customer_id,
                provided_hmac=expected_hmac,
            )

        assert result is True

    @pytest.mark.asyncio
    async def test_invalid_hmac_returns_false(self):
        """A wrong HMAC should fail verification."""
        test_secret = "abcdef1234567890abcdef1234567890"
        customer_id = "7654321012345"

        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=test_secret)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id=customer_id,
                provided_hmac="0000000000000000000000000000000000000000000000000000000000000000",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_tampered_customer_id_fails(self):
        """HMAC computed for one customer_id must not verify for another."""
        test_secret = "abcdef1234567890abcdef1234567890"
        real_customer_id = "7654321012345"
        fake_customer_id = "9999999999999"

        # Sign with the real customer_id
        signed_hmac = hmac.new(
            test_secret.encode("utf-8"),
            real_customer_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=test_secret)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            # Try to verify the fake customer_id with the real HMAC
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id=fake_customer_id,
                provided_hmac=signed_hmac,
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_no_secret_configured_returns_false(self):
        """If the tenant has no identity secret, verification fails."""
        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=None)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id="12345",
                provided_hmac="anything",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_key_vault_error_returns_false(self):
        """If Key Vault fails, verification fails gracefully."""
        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(side_effect=Exception("Key Vault unavailable"))

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id="12345",
                provided_hmac="anything",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_gid_format_customer_id(self):
        """Shopify GID-format customer IDs should verify correctly."""
        test_secret = "testsecret123"
        customer_id = "gid://shopify/Customer/7654321012345"

        expected_hmac = hmac.new(
            test_secret.encode("utf-8"),
            customer_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=test_secret)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            result = await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id=customer_id,
                provided_hmac=expected_hmac,
            )

        assert result is True

    @pytest.mark.asyncio
    async def test_uses_correct_secret_type(self):
        """Verify we request CUSTOMER_IDENTITY_SECRET from the service."""
        mock_service = MagicMock()
        mock_service.get_secret = AsyncMock(return_value=None)

        with patch(
            "src.multi_tenant.tenant_secret_service.get_secret_service",
            return_value=mock_service,
        ):
            await verify_shopify_customer_hmac(
                tenant_id="test-tenant",
                customer_id="12345",
                provided_hmac="anything",
            )

        from src.multi_tenant.tenant_secret_service import TenantSecretType

        mock_service.get_secret.assert_called_once_with(
            "test-tenant",
            TenantSecretType.CUSTOMER_IDENTITY_SECRET,
        )
