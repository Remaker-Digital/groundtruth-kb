# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shopify customer identity verification — HMAC-SHA256 passthrough (AUTH-4).

Verifies that a Shopify customer identity submitted by the widget is
authentic. The widget injects the Shopify ``customer.id`` and an
HMAC-SHA256 signature computed using the tenant's identity secret.

The server verifies by recomputing HMAC(customer_id, secret) and
comparing. On success, the customer gets full PCM access with zero
friction (no pre-chat form, no OTP).

Flow:
    1. Merchant enters identity secret in Shopify theme settings
    2. Liquid template: ``{{ customer.id | hmac_sha256: block.settings.identity_secret }}``
    3. Widget reads data attributes → sends in conversation start
    4. Backend: verify_shopify_customer_hmac() checks HMAC
    5. If valid → conversation linked to verified Shopify customer

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets

logger = logging.getLogger(__name__)


async def verify_shopify_customer_hmac(
    tenant_id: str,
    customer_id: str,
    provided_hmac: str,
) -> bool:
    """Verify the HMAC-SHA256 signature of a Shopify customer identity.

    Args:
        tenant_id: The tenant whose identity secret should be used.
        customer_id: Shopify customer ID (e.g. "gid://shopify/Customer/12345").
        provided_hmac: The HMAC signature from the widget (hex string).

    Returns:
        True if the HMAC is valid, False otherwise.
    """
    # Load the tenant's customer identity secret from Key Vault
    try:
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        service = get_secret_service()
        secret = await service.get_secret(
            tenant_id,
            TenantSecretType.CUSTOMER_IDENTITY_SECRET,
        )
    except Exception:
        logger.exception(
            "Failed to load customer identity secret: tenant=%s",
            tenant_id,
        )
        return False

    if not secret:
        logger.debug(
            "No customer identity secret configured: tenant=%s",
            tenant_id,
        )
        return False

    # Compute expected HMAC-SHA256(customer_id, secret)
    expected = hmac.new(
        secret.encode("utf-8"),
        customer_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    is_valid = secrets.compare_digest(provided_hmac, expected)

    if not is_valid:
        logger.warning(
            "Shopify customer HMAC mismatch: tenant=%s customer_id=%s",
            tenant_id,
            customer_id,
        )
    else:
        logger.info(
            "Shopify customer verified: tenant=%s customer_id=%s",
            tenant_id,
            customer_id,
        )

    return is_valid


def generate_identity_secret() -> str:
    """Generate a new customer identity secret.

    Returns a 32-byte hex string (256-bit) suitable for HMAC-SHA256
    key material.
    """
    return secrets.token_hex(32)
