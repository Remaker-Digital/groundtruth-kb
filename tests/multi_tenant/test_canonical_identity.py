"""Tests for ADR-004 Canonical Customer Identity — Phase 1 (schema + repository).

Covers:
    CID-01  generate_canonical_id format and uniqueness
    CID-02  ContactAttribute construction and serialization
    CID-03  CustomerProfileDocument with canonical_id + contact_attributes
    CID-04  CustomerProfileDocument backward compat (no canonical fields)
    CID-05  ConversationDocument with canonical_customer_id
    CID-06  ConversationDocument backward compat (no canonical field)
    CID-07  Repository: get_by_canonical_id
    CID-08  Repository: resolve_by_attribute
    CID-09  Repository: create_profile_with_canonical_id
    CID-10  Repository: link_attribute (success)
    CID-11  Repository: link_attribute (uniqueness violation)
    CID-12  Repository: unlink_attribute (success)
    CID-13  Repository: unlink_attribute (not found)
    CID-14  Repository: get_by_customer_id routes cid_ to canonical lookup
    CID-15  ContactAttributeType enum values

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    ContactAttribute,
    ContactAttributeType,
    ConversationDocument,
    CustomerProfileDocument,
)
from src.multi_tenant.repositories.customer import (
    CustomerProfileRepository,
    generate_canonical_id,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT = "tenant-cid-test"
CID_PATTERN = re.compile(r"^cid_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_attr(
    attr_type: ContactAttributeType = ContactAttributeType.EMAIL,
    value: str = "test@example.com",
    verified: bool = False,
    source: str = "self_asserted",
) -> ContactAttribute:
    return ContactAttribute(
        attribute_type=attr_type,
        value=value,
        verified=verified,
        source=source,
        added_at=_now(),
    )


# ---------------------------------------------------------------------------
# CID-01: generate_canonical_id
# ---------------------------------------------------------------------------


class TestGenerateCanonicalId:
    def test_cid_01_format(self) -> None:
        cid = generate_canonical_id()
        assert CID_PATTERN.match(cid), f"Expected cid_<uuid4>, got {cid}"

    def test_cid_01_uniqueness(self) -> None:
        ids = {generate_canonical_id() for _ in range(100)}
        assert len(ids) == 100, "Generated IDs should be unique"

    def test_cid_01_prefix(self) -> None:
        cid = generate_canonical_id()
        assert cid.startswith("cid_")
        assert len(cid) == 40  # "cid_" (4) + uuid (36)


# ---------------------------------------------------------------------------
# CID-02: ContactAttribute
# ---------------------------------------------------------------------------


class TestContactAttribute:
    def test_cid_02_construction(self) -> None:
        attr = _make_attr(
            attr_type=ContactAttributeType.EMAIL,
            value="user@shop.com",
            verified=True,
            source="otp",
        )
        assert attr.attribute_type == ContactAttributeType.EMAIL
        assert attr.value == "user@shop.com"
        assert attr.verified is True
        assert attr.source == "otp"
        assert attr.added_at  # non-empty

    def test_cid_02_serialization(self) -> None:
        attr = _make_attr()
        data = attr.model_dump()
        assert data["attribute_type"] == ContactAttributeType.EMAIL
        assert isinstance(data["value"], str)
        assert isinstance(data["verified"], bool)


# ---------------------------------------------------------------------------
# CID-03 / CID-04: CustomerProfileDocument
# ---------------------------------------------------------------------------


class TestCustomerProfileDocument:
    def test_cid_03_with_canonical_fields(self) -> None:
        cid = generate_canonical_id()
        attr = _make_attr(verified=True, source="otp")
        profile = CustomerProfileDocument(
            id=f"{TENANT}:{cid}",
            tenant_id=TENANT,
            customer_id=cid,
            canonical_id=cid,
            contact_attributes=[attr],
            created_at=_now(),
            updated_at=_now(),
        )
        assert profile.canonical_id == cid
        assert len(profile.contact_attributes) == 1
        assert profile.contact_attributes[0].verified is True

    def test_cid_04_backward_compat(self) -> None:
        """Old profiles without canonical_id default to empty string."""
        profile = CustomerProfileDocument(
            id=f"{TENANT}:old@email.com",
            tenant_id=TENANT,
            customer_id="old@email.com",
            created_at=_now(),
            updated_at=_now(),
        )
        assert profile.canonical_id == ""
        assert profile.contact_attributes == []


# ---------------------------------------------------------------------------
# CID-05 / CID-06: ConversationDocument
# ---------------------------------------------------------------------------


class TestConversationDocument:
    def _make_conv(self, **overrides: Any) -> ConversationDocument:
        defaults: dict[str, Any] = {
            "id": "conv-001",
            "tenant_id": TENANT,
            "conversation_id": "conv-001",
            "status": "active",
            "customer_id": None,
            "created_at": _now(),
            "updated_at": _now(),
            "started_at": _now(),
            "last_activity_at": _now(),
            "messages": [],
        }
        defaults.update(overrides)
        return ConversationDocument(**defaults)

    def test_cid_05_with_canonical(self) -> None:
        cid = generate_canonical_id()
        conv = self._make_conv(customer_id=cid, canonical_customer_id=cid)
        assert conv.canonical_customer_id == cid

    def test_cid_06_backward_compat(self) -> None:
        conv = self._make_conv(customer_id="old@email.com")
        assert conv.canonical_customer_id is None


# ---------------------------------------------------------------------------
# CID-07..CID-14: Repository methods (mocked Cosmos)
# ---------------------------------------------------------------------------


class TestCanonicalRepository:
    """Repository tests using mocked base class methods."""

    @pytest.fixture
    def repo(self) -> CustomerProfileRepository:
        r = CustomerProfileRepository()
        r.read = AsyncMock()
        r.create = AsyncMock(side_effect=lambda tid, doc: doc.model_dump() if hasattr(doc, "model_dump") else doc)
        r.upsert = AsyncMock(side_effect=lambda tid, doc: doc.model_dump() if hasattr(doc, "model_dump") else doc)
        r.query = AsyncMock(return_value=[])
        r.patch = AsyncMock(return_value={})
        return r

    @pytest.mark.asyncio
    async def test_cid_07_get_by_canonical_id(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        expected = {"canonical_id": cid, "tenant_id": TENANT}
        repo.read = AsyncMock(return_value=expected)

        result = await repo.get_by_canonical_id(TENANT, cid)
        assert result == expected
        repo.read.assert_awaited_once_with(TENANT, f"{TENANT}:{cid}")

    @pytest.mark.asyncio
    async def test_cid_07_not_found(self, repo: CustomerProfileRepository) -> None:
        from src.multi_tenant.repositories.base import DocumentNotFoundError
        repo.read = AsyncMock(side_effect=DocumentNotFoundError("customer_profiles", "cid_nonexistent", TENANT))

        result = await repo.get_by_canonical_id(TENANT, "cid_nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_cid_08_resolve_by_attribute(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        repo.query = AsyncMock(return_value=[{"canonical_id": cid}])

        result = await repo.resolve_by_attribute(TENANT, ContactAttributeType.EMAIL, "user@shop.com")
        assert result == cid
        repo.query.assert_awaited_once()
        call_args = repo.query.call_args
        assert "ARRAY_CONTAINS" in call_args.kwargs["query_text"]

    @pytest.mark.asyncio
    async def test_cid_08_resolve_not_found(self, repo: CustomerProfileRepository) -> None:
        repo.query = AsyncMock(return_value=[])
        result = await repo.resolve_by_attribute(TENANT, "email", "nobody@nowhere.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_cid_09_create_profile(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        attr = _make_attr(verified=True, source="shopify_hmac")

        result = await repo.create_profile_with_canonical_id(
            TENANT, cid, contact_attributes=[attr],
        )
        assert result["canonical_id"] == cid
        assert result["customer_id"] == cid
        assert len(result["contact_attributes"]) == 1

    @pytest.mark.asyncio
    async def test_cid_10_link_attribute_success(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        # read returns the profile (for get_by_canonical_id)
        mock_profile = {"id": f"{TENANT}:{cid}", "canonical_id": cid, "contact_attributes": []}
        repo.read = AsyncMock(return_value=mock_profile)
        # No existing profile claims this attribute
        repo.query = AsyncMock(return_value=[])
        attr = _make_attr(
            attr_type=ContactAttributeType.PHONE,
            value="+15551234567",
            verified=True,
            source="admin",
        )

        await repo.link_attribute(TENANT, cid, attr)
        repo.patch.assert_awaited_once()
        ops = repo.patch.call_args.kwargs["operations"]
        assert any(op["op"] == "add" and "/contact_attributes/" in op["path"] for op in ops)

    @pytest.mark.asyncio
    async def test_cid_11_link_uniqueness_violation(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        other_cid = generate_canonical_id()
        # Another profile already claims this email
        repo.query = AsyncMock(return_value=[{"canonical_id": other_cid}])

        attr = _make_attr(value="taken@example.com")
        with pytest.raises(ValueError, match="already linked"):
            await repo.link_attribute(TENANT, cid, attr)

    @pytest.mark.asyncio
    async def test_cid_11_link_same_profile_ok(self, repo: CustomerProfileRepository) -> None:
        """Re-linking an attribute to the same profile should succeed."""
        cid = generate_canonical_id()
        mock_profile = {"id": f"{TENANT}:{cid}", "canonical_id": cid, "contact_attributes": []}
        repo.read = AsyncMock(return_value=mock_profile)
        repo.query = AsyncMock(return_value=[{"canonical_id": cid}])
        attr = _make_attr(value="existing@example.com")

        await repo.link_attribute(TENANT, cid, attr)
        repo.patch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cid_12_unlink_attribute(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        repo.read = AsyncMock(return_value={
            "id": f"{TENANT}:{cid}",
            "canonical_id": cid,
            "contact_attributes": [
                {"attribute_type": "email", "value": "a@b.com"},
                {"attribute_type": "phone", "value": "+1555"},
            ],
        })

        await repo.unlink_attribute(TENANT, cid, "email", "a@b.com")
        repo.patch.assert_awaited_once()
        ops = repo.patch.call_args.kwargs["operations"]
        set_op = next(op for op in ops if op["path"] == "/contact_attributes")
        assert len(set_op["value"]) == 1  # only phone remains

    @pytest.mark.asyncio
    async def test_cid_13_unlink_not_found(self, repo: CustomerProfileRepository) -> None:
        cid = generate_canonical_id()
        repo.read = AsyncMock(return_value={
            "canonical_id": cid,
            "contact_attributes": [],
        })

        with pytest.raises(ValueError, match="not found"):
            await repo.unlink_attribute(TENANT, cid, "email", "nobody@example.com")

    @pytest.mark.asyncio
    async def test_cid_14_get_by_customer_id_routes_cid(self, repo: CustomerProfileRepository) -> None:
        """get_by_customer_id with cid_ prefix should use canonical lookup."""
        cid = generate_canonical_id()
        expected = {"canonical_id": cid}
        repo.read = AsyncMock(return_value=expected)

        result = await repo.get_by_customer_id(TENANT, cid)
        assert result == expected
        # Should have called read with canonical doc ID format
        repo.read.assert_awaited_once_with(TENANT, f"{TENANT}:{cid}")


# ---------------------------------------------------------------------------
# CID-15: ContactAttributeType enum
# ---------------------------------------------------------------------------


class TestContactAttributeType:
    def test_cid_15_all_types(self) -> None:
        expected = {"email", "phone", "shopify_customer_gid", "stripe_customer_id", "external_id"}
        actual = {t.value for t in ContactAttributeType}
        assert actual == expected
