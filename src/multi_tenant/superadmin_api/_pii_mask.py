# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""PII masking helpers for superadmin API responses.

SPEC-1843 (ZK Pillar 3): platform operator MUST NOT read tenant data.
Masking applied at the response boundary so Cosmos queries still function
but raw PII never reaches the API consumer.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations


def mask_email(email: str | None) -> str | None:
    """``john@example.com`` -> ``j***@example.com``."""
    if not email:
        return email
    at = email.find("@")
    if at < 1:
        return "***"
    return email[0] + "***" + email[at:]


def mask_domain(domain: str | None) -> str | None:
    """``my-store.myshopify.com`` -> ``***.myshopify.com``."""
    if not domain:
        return domain
    dot = domain.find(".")
    if dot < 0:
        return "***"
    return "***" + domain[dot:]


def mask_brand(brand: str | None) -> str | None:
    """``Acme Widgets`` -> ``Acm***``."""
    if not brand:
        return brand
    return brand[:3] + "***" if len(brand) > 3 else brand + "***"
