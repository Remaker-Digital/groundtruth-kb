"""
Customer profile repository — customer_profiles collection (Layer 1).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_CUSTOMER_PROFILES,
    CustomerProfileDocument,
)
from src.multi_tenant.repositories.base import DocumentNotFoundError, TenantScopedRepository


class CustomerProfileRepository(TenantScopedRepository):
    """Repository for the customer_profiles collection (Layer 1)."""

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    _encryption_fields = frozenset({
        "name", "email", "phone", "address", "notes",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_CUSTOMER_PROFILES)

    async def get_by_customer_id(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any] | None:
        """Get a customer profile by customer_id within a tenant."""
        doc_id = f"{tenant_id}:{customer_id}"
        try:
            return await self.read(tenant_id, doc_id)
        except DocumentNotFoundError:
            return None

    async def upsert_profile(
        self, tenant_id: str, profile: CustomerProfileDocument,
    ) -> dict[str, Any]:
        """Create or update a customer profile."""
        return await self.upsert(tenant_id, profile)

    async def update_last_interaction(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Update the last_interaction_at timestamp."""
        doc_id = f"{tenant_id}:{customer_id}"
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/last_interaction_at", "value": now},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    async def list_with_consent(
        self, tenant_id: str, consent_status: str,
    ) -> list[dict[str, Any]]:
        """List profiles with a specific consent status."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c WHERE c.consent_status = @consent"
            ),
            parameters=[{"name": "@consent", "value": consent_status}],
        )
