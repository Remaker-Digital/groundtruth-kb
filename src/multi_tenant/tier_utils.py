"""Shared tenant tier utilities (SPEC-1879).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def check_tier_gate(tenant_id: str) -> bool:
    """Return True if tenant is professional+ tier (SMS features enabled).

    Defaults to blocked (False) on any lookup failure — fail-closed.
    """
    try:
        from src.multi_tenant.repository import TenantRepository

        tenant_repo = TenantRepository()
        # TenantScopedRepository.read(tenant_id, document_id) — for tenants
        # the document_id is the tenant_id itself.
        tenant = await tenant_repo.read(tenant_id, tenant_id)
        if tenant:
            tier = tenant.get("tier", "starter")
            return tier in ("professional", "enterprise")
    except Exception:
        logger.debug("Failed to check tier for %s — defaulting to blocked", tenant_id)
    return False
