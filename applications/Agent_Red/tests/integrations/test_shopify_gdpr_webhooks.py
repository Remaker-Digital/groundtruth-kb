"""
Shopify GDPR mandatory webhook tests (MT-1017→MT-1020).

Tests HMAC-SHA256 webhook signature verification and correct HTTP responses
for all three Shopify GDPR endpoints:
    - POST /api/shopify/gdpr/customers-data-request
    - POST /api/shopify/gdpr/customers-redact
    - POST /api/shopify/gdpr/shop-redact

Master Test Plan: §4 Gap Register — Shopify GDPR Webhooks (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import base64
import json
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# HMAC helper — reproduces Shopify's webhook signing
# ---------------------------------------------------------------------------

SHOPIFY_SECRET = "test_shopify_api_secret_for_gdpr"


def _shopify_hmac(body: bytes, secret: str = SHOPIFY_SECRET) -> str:
    """Compute Shopify-style HMAC-SHA256 signature (base64-encoded)."""
    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


# ---------------------------------------------------------------------------
# Sample GDPR payloads matching Shopify's documented format
# ---------------------------------------------------------------------------

CUSTOMERS_DATA_REQUEST_PAYLOAD = {
    "shop_id": 654321,
    "shop_domain": "test-store.myshopify.com",
    "orders_requested": [1, 2, 3],
    "customer": {
        "id": 123456789,
        "email": "customer@example.com",
        "phone": "+1555000111",
    },
    "data_request": {
        "id": 98765,
    },
}

CUSTOMERS_REDACT_PAYLOAD = {
    "shop_id": 654321,
    "shop_domain": "test-store.myshopify.com",
    "customer": {
        "id": 123456789,
        "email": "customer@example.com",
        "phone": "+1555000111",
    },
    "orders_to_redact": [1, 2],
}

SHOP_REDACT_PAYLOAD = {
    "shop_id": 654321,
    "shop_domain": "test-store.myshopify.com",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def gdpr_client():
    """TestClient with SHOPIFY_API_SECRET set for HMAC verification."""
    from src.main import app

    with patch.dict(os.environ, {"SHOPIFY_API_SECRET": SHOPIFY_SECRET}), \
         patch("src.integrations.shopify_gdpr_webhooks._SHOPIFY_API_SECRET", SHOPIFY_SECRET):
        with TestClient(app) as client:
            yield client


# ---------------------------------------------------------------------------
# MT-1017: Valid HMAC → 200 for customers-data-request
# MT-1018: Valid HMAC → 200 for customers-redact
# MT-1019: Valid HMAC → 200 for shop-redact
# ---------------------------------------------------------------------------


class TestGDPRValidHMAC:
    """MT-1017/1018/1019: All three GDPR endpoints accept valid HMAC."""

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/shopify/gdpr/customers-data-request", CUSTOMERS_DATA_REQUEST_PAYLOAD),
            ("/api/shopify/gdpr/customers-redact", CUSTOMERS_REDACT_PAYLOAD),
            ("/api/shopify/gdpr/shop-redact", SHOP_REDACT_PAYLOAD),
        ],
        ids=["MT-1017-data-request", "MT-1018-customers-redact", "MT-1019-shop-redact"],
    )
    def test_valid_hmac_returns_200(self, gdpr_client, endpoint, payload):
        """Valid HMAC signature → 200 with acknowledgment response."""
        body = json.dumps(payload).encode("utf-8")
        hmac_header = _shopify_hmac(body)

        response = gdpr_client.post(
            endpoint,
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-SHA256": hmac_header,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "acknowledged"


# ---------------------------------------------------------------------------
# MT-1020: Invalid HMAC → 401 for all endpoints
# ---------------------------------------------------------------------------


class TestGDPRInvalidHMAC:
    """MT-1020: Invalid HMAC signatures are rejected with 401."""

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/shopify/gdpr/customers-data-request", CUSTOMERS_DATA_REQUEST_PAYLOAD),
            ("/api/shopify/gdpr/customers-redact", CUSTOMERS_REDACT_PAYLOAD),
            ("/api/shopify/gdpr/shop-redact", SHOP_REDACT_PAYLOAD),
        ],
        ids=["data-request-invalid", "customers-redact-invalid", "shop-redact-invalid"],
    )
    def test_invalid_hmac_returns_401(self, gdpr_client, endpoint, payload):
        """Tampered or wrong HMAC → 401 Unauthorized."""
        body = json.dumps(payload).encode("utf-8")
        # Use wrong secret to produce invalid HMAC
        bad_hmac = _shopify_hmac(body, secret="wrong_secret_value")

        response = gdpr_client.post(
            endpoint,
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Hmac-SHA256": bad_hmac,
            },
        )

        assert response.status_code == 401

    def test_missing_hmac_returns_401(self, gdpr_client):
        """No HMAC header at all → 401."""
        body = json.dumps(SHOP_REDACT_PAYLOAD).encode("utf-8")

        response = gdpr_client.post(
            "/api/shopify/gdpr/shop-redact",
            content=body,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 401
