"""Shopify GDPR mandatory webhook handlers (WI #35).

Shopify requires all apps to implement three GDPR webhook endpoints before
app submission. These endpoints are called by Shopify (not merchants) when
a data subject exercises their GDPR rights through Shopify's admin.

Endpoints:
    POST /api/shopify/gdpr/customers-data-request
        → Customer requests export of their data (GDPR Article 15/20)
    POST /api/shopify/gdpr/customers-redact
        → Customer requests deletion of their data (GDPR Article 17)
    POST /api/shopify/gdpr/shop-redact
        → Shop uninstalled; delete all shop data after 48-hour grace period

Authentication:
    Shopify signs each webhook payload with HMAC-SHA256 using the app's
    client secret. The signature is sent in the X-Shopify-Hmac-Sha256
    header. All three endpoints verify this signature before processing.
    These endpoints bypass the tenant auth middleware (added to
    AUTH_EXEMPT_PREFIXES in auth.py).

Shopify GDPR webhook reference:
    https://shopify.dev/docs/apps/build/privacy-law-compliance

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import base64
import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Shopify uses the app's client secret to sign GDPR webhook payloads.
# This is the same SHOPIFY_API_SECRET used for session token verification.
_SHOPIFY_API_SECRET = os.environ.get("SHOPIFY_API_SECRET", "")

# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_export_service: Any | None = None
_deletion_service: Any | None = None
_tenant_repo: Any | None = None
_domain_index_repo: Any | None = None


def configure_shopify_gdpr_services(
    export_service: Any | None = None,
    deletion_service: Any | None = None,
    tenant_repo: Any | None = None,
    domain_index_repo: Any | None = None,
) -> None:
    """Wire the Shopify GDPR webhooks to their backing services.

    Called during app startup after GDPR services are initialised.
    Services are optional — if not wired, endpoints still accept
    webhooks (returning 200) but log a warning about missing services.
    """
    global _export_service, _deletion_service, _tenant_repo, _domain_index_repo
    _export_service = export_service
    _deletion_service = deletion_service
    _tenant_repo = tenant_repo
    _domain_index_repo = domain_index_repo
    logger.info("Shopify GDPR webhook services configured")


# ---------------------------------------------------------------------------
# HMAC-SHA256 verification
# ---------------------------------------------------------------------------


def _verify_shopify_hmac(body: bytes, hmac_header: str) -> bool:
    """Verify the Shopify webhook HMAC-SHA256 signature.

    Shopify computes HMAC-SHA256 of the raw request body using the app's
    client secret, then base64-encodes the result. This is sent in the
    X-Shopify-Hmac-Sha256 header.

    Args:
        body: Raw request body bytes.
        hmac_header: Value of the X-Shopify-Hmac-Sha256 header.

    Returns:
        True if the signature is valid.
    """
    secret = _SHOPIFY_API_SECRET or os.environ.get("SHOPIFY_API_SECRET", "")
    if not secret:
        logger.error("SHOPIFY_API_SECRET not configured — cannot verify webhook HMAC")
        return False

    computed = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    computed_b64 = base64.b64encode(computed).decode("utf-8")

    return hmac.compare_digest(computed_b64, hmac_header)


async def _verify_webhook_request(request: Request) -> dict[str, Any]:
    """Read body, verify HMAC, and parse JSON payload.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The parsed JSON payload as a dict.

    Raises:
        HTTPException: If HMAC verification fails or payload is invalid.
    """
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")

    if not hmac_header:
        logger.warning("Shopify GDPR webhook missing HMAC header")
        raise HTTPException(status_code=401, detail="Missing HMAC signature")

    if not _verify_shopify_hmac(body, hmac_header):
        logger.warning("Shopify GDPR webhook HMAC verification failed")
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    try:
        import json
        payload = json.loads(body)
    except (ValueError, TypeError):
        logger.warning("Shopify GDPR webhook payload is not valid JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    return payload


# ---------------------------------------------------------------------------
# Tenant resolution helper
# ---------------------------------------------------------------------------


async def _resolve_tenant_id(shop_domain: str) -> str | None:
    """Resolve a Shopify shop domain to a tenant_id.

    Uses the DomainIndexRepository for O(1) point-read lookup (no
    cross-partition query).  Falls back to TenantRepository if
    domain index is not configured.

    Returns:
        The tenant_id, or None if the shop is not recognised.
    """
    # Prefer domain index — single-partition point read
    if _domain_index_repo is not None:
        try:
            tenant_id = await _domain_index_repo.lookup(shop_domain)
            if tenant_id is not None:
                return tenant_id
        except Exception:
            logger.exception(
                "Domain index lookup failed for shop=%s, trying fallback",
                shop_domain,
            )

    # Fallback to cross-partition query (legacy path)
    if _tenant_repo is not None:
        try:
            tenant_doc = await _tenant_repo.find_by_shopify_domain(shop_domain)
            if tenant_doc is not None:
                return tenant_doc.get("id") or tenant_doc.get("tenant_id")
        except Exception:
            logger.exception(
                "Error resolving shop domain to tenant: shop=%s", shop_domain,
            )

    logger.warning(
        "Cannot resolve shop %s to tenant — no repo configured", shop_domain,
    )
    return None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/shopify/gdpr", tags=["shopify-gdpr"])


# ---------------------------------------------------------------------------
# POST /api/shopify/gdpr/customers-data-request
# ---------------------------------------------------------------------------


@router.post(
    "/customers-data-request",
    status_code=200,
    summary="Handle customer data request webhook",
    description="Handles the Shopify customers/data_request GDPR webhook. Verifies HMAC signature and exports customer data when services are available.",
    responses={
        400: {"description": "Invalid JSON payload"},
        401: {"description": "Missing or invalid HMAC signature"},
    },
)
async def customers_data_request(request: Request) -> JSONResponse:
    """Handle Shopify customers/data_request webhook.

    Shopify sends this when a customer requests their data through the
    store's privacy page. The app should respond with a data export or
    acknowledge the request and fulfill it asynchronously.

    Payload shape (from Shopify):
        {
            "shop_id": 954889,
            "shop_domain": "example.myshopify.com",
            "orders_requested": [299938, 280263, ...],
            "customer": {
                "id": 191167,
                "email": "customer@example.com",
                "phone": "+1-555-555-5555"
            },
            "data_request": {
                "id": 9999
            }
        }
    """
    payload = await _verify_webhook_request(request)

    shop_domain = payload.get("shop_domain", "")
    customer = payload.get("customer", {})
    customer_id = str(customer.get("id", ""))
    customer_email = customer.get("email", "")
    data_request_id = payload.get("data_request", {}).get("id")

    logger.info(
        "Shopify GDPR customers/data_request: shop=%s customer_id=%s "
        "data_request_id=%s",
        shop_domain,
        customer_id,
        data_request_id,
    )

    # Resolve tenant and export data if services are available
    tenant_id = await _resolve_tenant_id(shop_domain)

    if tenant_id and _export_service is not None:
        try:
            # Export customer data using the same service as the admin API
            result = await _export_service.export_customer(tenant_id, customer_id)
            logger.info(
                "Shopify GDPR data export completed: shop=%s customer=%s "
                "export_id=%s stores=%d",
                shop_domain,
                customer_id,
                result.export_id,
                len(result.stores_exported),
            )
        except Exception:
            logger.exception(
                "Shopify GDPR data export failed: shop=%s customer=%s",
                shop_domain,
                customer_id,
            )
    elif tenant_id is None:
        logger.info(
            "Shopify GDPR customers/data_request: shop=%s not found in tenants "
            "(may have already been deleted)",
            shop_domain,
        )
    else:
        logger.warning(
            "Shopify GDPR customers/data_request: export service not available "
            "— request acknowledged but not fulfilled",
        )

    # Always return 200 to Shopify to acknowledge receipt.
    # The actual data export is delivered to the merchant via the
    # Shopify admin, not through this webhook response.
    return JSONResponse(
        status_code=200,
        content={"status": "acknowledged", "data_request_id": data_request_id},
    )


# ---------------------------------------------------------------------------
# POST /api/shopify/gdpr/customers-redact
# ---------------------------------------------------------------------------


@router.post(
    "/customers-redact",
    status_code=200,
    summary="Handle customer data redaction webhook",
    description="Handles the Shopify customers/redact GDPR webhook. Verifies HMAC signature and deletes all personal data for the specified customer.",
    responses={
        400: {"description": "Invalid JSON payload"},
        401: {"description": "Missing or invalid HMAC signature"},
    },
)
async def customers_redact(request: Request) -> JSONResponse:
    """Handle Shopify customers/redact webhook.

    Shopify sends this when a customer requests deletion of their data.
    The app must delete all personal data for this customer within 30 days.

    This endpoint delegates to DataDeletionService.delete_customer() which
    performs cascading deletion across all registered data stores.

    Payload shape (from Shopify):
        {
            "shop_id": 954889,
            "shop_domain": "example.myshopify.com",
            "orders_to_redact": [299938, 280263, ...],
            "customer": {
                "id": 191167,
                "email": "customer@example.com",
                "phone": "+1-555-555-5555"
            }
        }
    """
    payload = await _verify_webhook_request(request)

    shop_domain = payload.get("shop_domain", "")
    customer = payload.get("customer", {})
    customer_id = str(customer.get("id", ""))
    customer_email = customer.get("email", "")

    logger.info(
        "Shopify GDPR customers/redact: shop=%s customer_id=%s",
        shop_domain,
        customer_id,
    )

    # Resolve tenant and delete customer data if services are available
    tenant_id = await _resolve_tenant_id(shop_domain)

    if tenant_id and _deletion_service is not None:
        try:
            result = await _deletion_service.delete_customer(tenant_id, customer_id)
            logger.info(
                "Shopify GDPR customer redaction completed: shop=%s customer=%s "
                "deletion_id=%s stores=%d",
                shop_domain,
                customer_id,
                result.deletion_id,
                len(result.stores_deleted),
            )
        except Exception:
            logger.exception(
                "Shopify GDPR customer redaction failed: shop=%s customer=%s",
                shop_domain,
                customer_id,
            )
    elif tenant_id is None:
        logger.info(
            "Shopify GDPR customers/redact: shop=%s not found in tenants "
            "(may have already been deleted — data considered redacted)",
            shop_domain,
        )
    else:
        logger.warning(
            "Shopify GDPR customers/redact: deletion service not available "
            "— request acknowledged but not fulfilled. MANUAL ACTION REQUIRED.",
        )

    return JSONResponse(
        status_code=200,
        content={"status": "acknowledged"},
    )


# ---------------------------------------------------------------------------
# POST /api/shopify/gdpr/shop-redact
# ---------------------------------------------------------------------------


@router.post(
    "/shop-redact",
    status_code=200,
    summary="Handle shop data redaction webhook",
    description="Handles the Shopify shop/redact GDPR webhook. Verifies HMAC signature and deletes all data associated with the shop after the 48-hour grace period.",
    responses={
        400: {"description": "Invalid JSON payload"},
        401: {"description": "Missing or invalid HMAC signature"},
    },
)
async def shop_redact(request: Request) -> JSONResponse:
    """Handle Shopify shop/redact webhook.

    Shopify sends this 48 hours after a merchant uninstalls the app.
    The app must delete ALL data associated with the shop. This is the
    terminal cleanup — after this, no shop data should remain.

    The 48-hour delay is Shopify's built-in grace period, which aligns
    with our GracePeriodManager's SHOPIFY_GRACE_PERIOD_HOURS = 48.

    This endpoint delegates to DataDeletionService.delete_tenant() with
    force=True because Shopify's own 48-hour grace period has already
    elapsed by the time this webhook fires.

    Payload shape (from Shopify):
        {
            "shop_id": 954889,
            "shop_domain": "example.myshopify.com"
        }
    """
    payload = await _verify_webhook_request(request)

    shop_domain = payload.get("shop_domain", "")
    shop_id = payload.get("shop_id")

    logger.info(
        "Shopify GDPR shop/redact: shop=%s shop_id=%s",
        shop_domain,
        shop_id,
    )

    # Resolve tenant and delete ALL shop data
    tenant_id = await _resolve_tenant_id(shop_domain)

    if tenant_id and _deletion_service is not None:
        try:
            # Force=True because Shopify's own 48-hour grace period
            # has already elapsed before this webhook fires.
            result = await _deletion_service.delete_tenant(tenant_id, force=True)
            logger.info(
                "Shopify GDPR shop redaction completed: shop=%s tenant=%s "
                "deletion_id=%s stores=%d",
                shop_domain,
                tenant_id,
                result.deletion_id,
                len(result.stores_deleted),
            )
        except Exception:
            logger.exception(
                "Shopify GDPR shop redaction failed: shop=%s tenant=%s",
                shop_domain,
                tenant_id,
            )
    elif tenant_id is None:
        logger.info(
            "Shopify GDPR shop/redact: shop=%s not found in tenants "
            "(may have already been deleted — data considered redacted)",
            shop_domain,
        )
    else:
        logger.warning(
            "Shopify GDPR shop/redact: deletion service not available "
            "— request acknowledged but not fulfilled. MANUAL ACTION REQUIRED.",
        )

    return JSONResponse(
        status_code=200,
        content={"status": "acknowledged"},
    )
