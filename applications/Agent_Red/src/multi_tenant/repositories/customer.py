# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Customer profile repository — customer_profiles collection (Layer 1).

ADR-004: Canonical customer identity.  The primary key is ``canonical_id``
(format: cid_<uuid4>).  Contact methods are stored as ``contact_attributes``
and can be linked/unlinked without changing the canonical identity.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_CUSTOMER_PROFILES,
    ContactAttribute,
    ContactAttributeType,
    CustomerProfileDocument,
)
from src.multi_tenant.repositories.base import DocumentNotFoundError, TenantScopedRepository


def generate_canonical_id() -> str:
    """Generate a new canonical customer ID (ADR-004).

    Format: cid_<uuid4>  (e.g., cid_a1b2c3d4-e5f6-7890-abcd-ef1234567890)
    """
    return f"cid_{uuid.uuid4()}"


class CustomerProfileRepository(TenantScopedRepository):
    """Repository for the customer_profiles collection (Layer 1)."""

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    # Per architecture plan section 4.1.3: customer PII + preferences
    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK.
    # contact_attributes is EXCLUDED — it contains identity claims used
    # as lookup keys (ARRAY_CONTAINS queries). Encrypting it would break
    # resolve_by_attribute() and all cross-channel identity resolution.
    _encryption_fields = frozenset({
        "name", "email", "phone", "address", "notes", "preferences",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_CUSTOMER_PROFILES)

    # ------------------------------------------------------------------
    # Legacy lookups (backward compat — existing callers)
    # ------------------------------------------------------------------

    async def get_by_customer_id(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any] | None:
        """Get a customer profile by customer_id within a tenant.

        Legacy method — prefers canonical_id lookup when the value starts
        with 'cid_', otherwise falls back to the old document ID format.
        """
        if customer_id.startswith("cid_"):
            return await self.get_by_canonical_id(tenant_id, customer_id)
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
        now = datetime.now(UTC).isoformat()
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

    # ------------------------------------------------------------------
    # ADR-004: Canonical identity methods
    # ------------------------------------------------------------------

    async def get_by_canonical_id(
        self, tenant_id: str, canonical_id: str,
    ) -> dict[str, Any] | None:
        """Get a customer profile by canonical_id.

        Attempts O(1) point read first ({tenant_id}:{canonical_id}),
        then falls back to query for migrated profiles whose document ID
        still uses the legacy format ({tenant_id}:{old_customer_id}).
        """
        # Attempt 1: point read at canonical doc ID
        doc_id = f"{tenant_id}:{canonical_id}"
        try:
            return await self.read(tenant_id, doc_id)
        except DocumentNotFoundError:
            pass

        # Attempt 2: query fallback for migrated docs with legacy ID format
        results = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.canonical_id = @cid",
            parameters=[{"name": "@cid", "value": canonical_id}],
        )
        return results[0] if results else None

    async def resolve_by_attribute(
        self, tenant_id: str, attr_type: str | ContactAttributeType, value: str,
    ) -> str | None:
        """Resolve a contact attribute to a canonical_id.

        Queries the contact_attributes array using Cosmos ARRAY_CONTAINS.
        Returns the canonical_id if found, None otherwise.
        """
        attr_type_str = attr_type.value if isinstance(attr_type, ContactAttributeType) else attr_type
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT c.canonical_id FROM c "
                "WHERE ARRAY_CONTAINS(c.contact_attributes, "
                "{\"attribute_type\": @attr_type, \"value\": @value}, true)"
            ),
            parameters=[
                {"name": "@attr_type", "value": attr_type_str},
                {"name": "@value", "value": value},
            ],
        )
        if results:
            return results[0].get("canonical_id") or None
        return None

    async def create_profile_with_canonical_id(
        self, tenant_id: str, canonical_id: str,
        contact_attributes: list[ContactAttribute] | None = None,
    ) -> dict[str, Any]:
        """Create a new customer profile with a canonical_id (ADR-004).

        The canonical_id becomes both the customer_id (for backward compat)
        and the canonical_id field.  Document ID: {tenant_id}:{canonical_id}.

        Uses create (not upsert) so a 409 Conflict is raised if a
        concurrent writer already created a profile with this ID.
        """
        now = datetime.now(UTC).isoformat()
        profile = CustomerProfileDocument(
            id=f"{tenant_id}:{canonical_id}",
            tenant_id=tenant_id,
            customer_id=canonical_id,
            canonical_id=canonical_id,
            contact_attributes=contact_attributes or [],
            created_at=now,
            updated_at=now,
        )
        return await self.create(tenant_id, profile)

    async def link_attribute(
        self, tenant_id: str, canonical_id: str,
        attribute: ContactAttribute,
    ) -> dict[str, Any]:
        """Link a new contact attribute to an existing canonical profile.

        Checks for uniqueness within the tenant first — if another profile
        already claims this (type, value) pair, raises ValueError.
        """
        # Uniqueness check: no other profile should own this attribute
        existing = await self.resolve_by_attribute(
            tenant_id, attribute.attribute_type, attribute.value,
        )
        if existing and existing != canonical_id:
            raise ValueError(
                f"Contact attribute {attribute.attribute_type}={attribute.value} "
                f"is already linked to {existing}"
            )

        # Look up actual doc ID (may be legacy format for migrated profiles)
        profile = await self.get_by_canonical_id(tenant_id, canonical_id)
        if not profile:
            raise DocumentNotFoundError(
                COLLECTION_CUSTOMER_PROFILES,
                f"{tenant_id}:{canonical_id}",
                tenant_id,
            )
        doc_id = profile.get("id", f"{tenant_id}:{canonical_id}")
        now = datetime.now(UTC).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {
                    "op": "add",
                    "path": "/contact_attributes/-",
                    "value": attribute.model_dump(),
                },
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    async def unlink_attribute(
        self, tenant_id: str, canonical_id: str,
        attr_type: str | ContactAttributeType, value: str,
    ) -> dict[str, Any]:
        """Remove a contact attribute from a canonical profile.

        Reads the profile, removes the matching attribute, and writes back.
        Uses upsert rather than patch because Cosmos patch doesn't support
        conditional array element removal.
        """
        profile = await self.get_by_canonical_id(tenant_id, canonical_id)
        if not profile:
            raise DocumentNotFoundError(
                COLLECTION_CUSTOMER_PROFILES,
                f"{tenant_id}:{canonical_id}",
                tenant_id,
            )

        attr_type_str = attr_type.value if isinstance(attr_type, ContactAttributeType) else attr_type
        attrs = profile.get("contact_attributes", [])
        filtered = [
            a for a in attrs
            if not (a.get("attribute_type") == attr_type_str and a.get("value") == value)
        ]
        if len(filtered) == len(attrs):
            raise ValueError(f"Attribute {attr_type_str}={value} not found on {canonical_id}")

        # Use actual document ID from profile (may be legacy format for migrated docs)
        doc_id = profile.get("id", f"{tenant_id}:{canonical_id}")
        now = datetime.now(UTC).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/contact_attributes", "value": filtered},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )
