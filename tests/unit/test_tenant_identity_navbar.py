"""
Unit tests for SPEC-1848: Tenant Identity Display in Navbar.

Verifies:
    1. /api/tenants/lookup returns shopify_shop_domain when present
    2. /api/tenants/lookup returns brand_name when present
    3. TenantLookupResponse always provides at least tenant_id (never all-blank)

Run:
    pytest tests/unit/test_tenant_identity_navbar.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.integrations.provisioning import (
    TenantLookupResponse,
    _read_brand_name,
    lookup_tenant_endpoint,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_tenant_doc(
    tenant_id: str = "t-001",
    shopify_shop_domain: str | None = None,
    billing_channel: str = "manual",
    stripe_customer_id: str | None = None,
    **extra,
) -> dict:
    """Create a minimal tenant document as returned by Cosmos."""
    doc = {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": "active",
        "tier": "starter",
        "billing_channel": billing_channel,
        "shopify_shop_domain": shopify_shop_domain,
        "stripe_customer_id": stripe_customer_id,
        **extra,
    }
    return doc


# ---------------------------------------------------------------------------
# TenantLookupResponse model tests
# ---------------------------------------------------------------------------

class TestTenantLookupResponseModel:
    """SPEC-1848: TenantLookupResponse includes identity fields."""

    def test_shopify_shop_domain_field_exists(self):
        """Response model has shopify_shop_domain field."""
        resp = TenantLookupResponse(found=True, tenant_id="t-001",
                                     shopify_shop_domain="blanco-9939.myshopify.com")
        assert resp.shopify_shop_domain == "blanco-9939.myshopify.com"

    def test_brand_name_field_exists(self):
        """Response model has brand_name field."""
        resp = TenantLookupResponse(found=True, tenant_id="t-001",
                                     brand_name="Toys & Games")
        assert resp.brand_name == "Toys & Games"

    def test_shopify_domain_none_when_absent(self):
        """shopify_shop_domain defaults to None."""
        resp = TenantLookupResponse(found=True, tenant_id="t-001")
        assert resp.shopify_shop_domain is None

    def test_brand_name_none_when_absent(self):
        """brand_name defaults to None."""
        resp = TenantLookupResponse(found=True, tenant_id="t-001")
        assert resp.brand_name is None

    def test_tenant_id_always_present_when_found(self):
        """tenant_id is always present in a found response."""
        resp = TenantLookupResponse(found=True, tenant_id="t-001")
        assert resp.tenant_id == "t-001"
        # At minimum, tenant_id gives the navbar something to display
        identity = resp.shopify_shop_domain or resp.brand_name or resp.tenant_id
        assert identity is not None and len(identity) > 0


# ---------------------------------------------------------------------------
# Lookup endpoint integration tests
# ---------------------------------------------------------------------------

class TestLookupReturnsShopDomain:
    """SPEC-1848: /api/tenants/lookup returns shopify_shop_domain from Cosmos."""

    @pytest.mark.asyncio
    async def test_api_key_lookup_includes_shop_domain(self):
        """When tenant has shopify_shop_domain, lookup returns it."""
        doc = _make_tenant_doc(
            shopify_shop_domain="blanco-9939.myshopify.com",
            billing_channel="shopify",
        )

        mock_request = AsyncMock()
        mock_request.headers = {"X-API-Key": "ar_test_key_123"}

        with patch(
            "src.integrations.provisioning._lookup_by_api_key",
            new_callable=AsyncMock,
            return_value=doc,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value="Test Brand",
        ):
            resp = await lookup_tenant_endpoint(mock_request)

        assert resp.found is True
        assert resp.shopify_shop_domain == "blanco-9939.myshopify.com"
        assert resp.brand_name == "Test Brand"

    @pytest.mark.asyncio
    async def test_api_key_lookup_shop_domain_none_when_absent(self):
        """When tenant has no shopify_shop_domain, lookup returns None."""
        doc = _make_tenant_doc(billing_channel="manual")

        mock_request = AsyncMock()
        mock_request.headers = {"X-API-Key": "ar_test_key_123"}

        with patch(
            "src.integrations.provisioning._lookup_by_api_key",
            new_callable=AsyncMock,
            return_value=doc,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value="My Brand",
        ):
            resp = await lookup_tenant_endpoint(mock_request)

        assert resp.found is True
        assert resp.shopify_shop_domain is None
        assert resp.brand_name == "My Brand"

    @pytest.mark.asyncio
    async def test_identity_never_all_blank(self):
        """Lookup always returns at least tenant_id — navbar is never blank."""
        doc = _make_tenant_doc(billing_channel="manual")

        mock_request = AsyncMock()
        mock_request.headers = {"X-API-Key": "ar_test_key_123"}

        with patch(
            "src.integrations.provisioning._lookup_by_api_key",
            new_callable=AsyncMock,
            return_value=doc,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await lookup_tenant_endpoint(mock_request)

        assert resp.found is True
        # Even when shop domain and brand name are both None,
        # tenant_id is always present as the last-resort fallback
        identity = resp.shopify_shop_domain or resp.brand_name or resp.tenant_id
        assert identity is not None and len(identity) > 0, (
            "All identity fields are blank — navbar would show nothing"
        )
