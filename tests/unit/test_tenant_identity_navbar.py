"""
Unit tests for SPEC-1848: Tenant Identity Display in Navbar.

Verifies:
    1. /api/tenants/lookup returns shopify_shop_domain when present
    2. /api/tenants/lookup returns brand_name when present
    3. TenantLookupResponse always provides at least tenant_id (never all-blank)

SPEC-1644 compliance: Tests use shop= or stripe_customer_id= parameters
for tenant lookup (API-key-based tenant discovery is prohibited).

WI-1636 / S137: Rewritten to use SPEC-1644-compliant lookup mechanism.
Previously mocked the removed _lookup_by_api_key function.

Run:
    pytest tests/unit/test_tenant_identity_navbar.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.provisioning import (
    TenantLookupResponse,
    TenantRecord,
    lookup_tenant_endpoint,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_tenant_record(
    tenant_id: str = "t-001",
    shopify_shop_domain: str | None = None,
    billing_channel: str = "manual",
    stripe_customer_id: str | None = None,
) -> TenantRecord:
    """Create a TenantRecord as returned by get_tenant()."""
    return TenantRecord(
        tenant_id=tenant_id,
        status="active",
        tier="starter",
        billing_channel=billing_channel,
        shopify_shop_domain=shopify_shop_domain,
        stripe_customer_id=stripe_customer_id,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


def _mock_request() -> MagicMock:
    """Create a minimal mock Request (required by the endpoint signature)."""
    req = MagicMock()
    req.headers = {}
    return req


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
# Lookup endpoint integration tests (SPEC-1644 compliant)
# ---------------------------------------------------------------------------

class TestLookupReturnsShopDomain:
    """SPEC-1848: /api/tenants/lookup returns shopify_shop_domain from Cosmos.

    SPEC-1644: Lookup uses shop= query parameter, NOT API key headers.
    """

    @pytest.mark.asyncio
    async def test_shop_lookup_includes_shop_domain(self):
        """When tenant has shopify_shop_domain, lookup returns it."""
        record = _make_tenant_record(
            shopify_shop_domain="blanco-9939.myshopify.com",
            billing_channel="shopify",
        )

        with patch(
            "src.integrations.provisioning.get_tenant",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value="Test Brand",
        ):
            resp = await lookup_tenant_endpoint(
                _mock_request(),
                shop="blanco-9939.myshopify.com",
            )

        assert resp.found is True
        assert resp.shopify_shop_domain == "blanco-9939.myshopify.com"
        assert resp.brand_name == "Test Brand"

    @pytest.mark.asyncio
    async def test_stripe_lookup_shop_domain_none_when_absent(self):
        """When tenant has no shopify_shop_domain, lookup returns None."""
        record = _make_tenant_record(
            billing_channel="stripe",
            stripe_customer_id="cus_test_123",
        )

        with patch(
            "src.integrations.provisioning.get_tenant",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value="My Brand",
        ):
            resp = await lookup_tenant_endpoint(
                _mock_request(),
                stripe_customer_id="cus_test_123",
            )

        assert resp.found is True
        assert resp.shopify_shop_domain is None
        assert resp.brand_name == "My Brand"

    @pytest.mark.asyncio
    async def test_identity_never_all_blank(self):
        """Lookup always returns at least tenant_id — navbar is never blank."""
        record = _make_tenant_record(billing_channel="stripe",
                                      stripe_customer_id="cus_test_456")

        with patch(
            "src.integrations.provisioning.get_tenant",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "src.integrations.provisioning._read_brand_name",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await lookup_tenant_endpoint(
                _mock_request(),
                stripe_customer_id="cus_test_456",
            )

        assert resp.found is True
        # Even when shop domain and brand name are both None,
        # tenant_id is always present as the last-resort fallback
        identity = resp.shopify_shop_domain or resp.brand_name or resp.tenant_id
        assert identity is not None and len(identity) > 0, (
            "All identity fields are blank — navbar would show nothing"
        )

    @pytest.mark.asyncio
    async def test_lookup_without_params_returns_400(self):
        """SPEC-1644: Lookup without shop= or stripe_customer_id= returns 400."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await lookup_tenant_endpoint(_mock_request())

        assert exc_info.value.status_code == 400
        assert "SPEC-1644" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_lookup_not_found_returns_empty(self):
        """Lookup for nonexistent tenant returns found=False."""
        with patch(
            "src.integrations.provisioning.get_tenant",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await lookup_tenant_endpoint(
                _mock_request(),
                shop="nonexistent.myshopify.com",
            )

        assert resp.found is False
