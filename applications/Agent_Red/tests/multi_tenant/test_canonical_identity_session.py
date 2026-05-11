"""Tests for ADR-004 Phase 2 — session identity resolution + pipeline integration.

Covers:
    SID-01  _resolve_canonical_customer_id with Shopify GID (existing profile)
    SID-02  _resolve_canonical_customer_id with Shopify GID (new, auto-create)
    SID-03  _resolve_canonical_customer_id with email (existing profile)
    SID-04  _resolve_canonical_customer_id with email (new, auto-create)
    SID-05  _resolve_canonical_customer_id with cid_ prefix (passthrough)
    SID-06  _resolve_canonical_customer_id anonymous (None visitor)
    SID-07  _resolve_canonical_customer_id anonymous (empty visitor)
    SID-08  start_conversation populates canonical_customer_id (with repo)
    SID-09  start_conversation legacy mode (no customer_repo)
    SID-10  Shopify GID + email creates both contact attributes

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.chat.models import (
    ConversationStartRequest,
    VisitorIdentity,
)
from src.chat.session import (
    ConversationSession,
    _resolve_canonical_customer_id,
)
from src.multi_tenant.cosmos_schema import ContactAttributeType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT = "tenant-sid-test"


def _mock_customer_repo(
    resolve_result: str | None = None,
    create_result: dict | None = None,
) -> AsyncMock:
    """Create a mock CustomerProfileRepository."""
    repo = AsyncMock()
    repo.resolve_by_attribute = AsyncMock(return_value=resolve_result)
    if create_result is None:
        create_result = {"canonical_id": "cid_new-profile", "customer_id": "cid_new-profile"}
    repo.create_profile_with_canonical_id = AsyncMock(return_value=create_result)
    return repo


def _visitor(
    customer_id: str | None = None,
    email: str | None = None,
    name: str | None = None,
    hmac: str | None = None,
) -> VisitorIdentity:
    return VisitorIdentity(
        customer_id=customer_id,
        email=email,
        name=name,
        hmac=hmac,
    )


# ---------------------------------------------------------------------------
# SID-01..SID-07: _resolve_canonical_customer_id
# ---------------------------------------------------------------------------


class TestResolveCanonicalCustomerId:
    @pytest.mark.asyncio
    async def test_sid_01_shopify_gid_existing(self) -> None:
        """Shopify GID resolves to existing canonical_id."""
        repo = _mock_customer_repo(resolve_result="cid_existing-123")
        visitor = _visitor(customer_id="gid://shopify/Customer/12345")

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical == "cid_existing-123"
        assert legacy == "gid://shopify/Customer/12345"
        repo.resolve_by_attribute.assert_awaited_once_with(
            TENANT, ContactAttributeType.SHOPIFY_CUSTOMER_GID, "gid://shopify/Customer/12345",
        )
        repo.create_profile_with_canonical_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sid_02_shopify_gid_new(self) -> None:
        """New Shopify GID creates a canonical profile."""
        repo = _mock_customer_repo(resolve_result=None)
        visitor = _visitor(customer_id="gid://shopify/Customer/99999")

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical is not None
        assert canonical.startswith("cid_")
        assert legacy == "gid://shopify/Customer/99999"
        repo.create_profile_with_canonical_id.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sid_03_email_existing(self) -> None:
        """Email resolves to existing canonical_id."""
        repo = _mock_customer_repo(resolve_result="cid_email-456")
        visitor = _visitor(email="returning@customer.com")

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical == "cid_email-456"
        assert legacy == "returning@customer.com"

    @pytest.mark.asyncio
    async def test_sid_04_email_new(self) -> None:
        """New email creates a canonical profile."""
        repo = _mock_customer_repo(resolve_result=None)
        visitor = _visitor(email="new@customer.com")

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical is not None
        assert canonical.startswith("cid_")
        assert legacy == "new@customer.com"
        repo.create_profile_with_canonical_id.assert_awaited_once()
        # Verify the email attribute was created
        call_kwargs = repo.create_profile_with_canonical_id.call_args
        attrs = call_kwargs.kwargs.get("contact_attributes") or call_kwargs.args[2] if len(call_kwargs.args) > 2 else []
        if not attrs and call_kwargs.kwargs:
            attrs = call_kwargs.kwargs.get("contact_attributes", [])
        assert any(a.attribute_type == ContactAttributeType.EMAIL for a in attrs)

    @pytest.mark.asyncio
    async def test_sid_05_cid_prefix_passthrough(self) -> None:
        """cid_ prefixed customer_id is passed through directly."""
        repo = _mock_customer_repo()
        visitor = _visitor(customer_id="cid_already-resolved")

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical == "cid_already-resolved"
        assert legacy == "cid_already-resolved"
        repo.resolve_by_attribute.assert_not_awaited()
        repo.create_profile_with_canonical_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sid_06_anonymous_none(self) -> None:
        """None visitor → (None, None)."""
        repo = _mock_customer_repo()

        canonical, legacy = await _resolve_canonical_customer_id(None, TENANT, repo)

        assert canonical is None
        assert legacy is None

    @pytest.mark.asyncio
    async def test_sid_07_anonymous_empty(self) -> None:
        """Visitor with no identifiers → (None, None)."""
        repo = _mock_customer_repo()
        visitor = _visitor()  # no customer_id, no email

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical is None
        assert legacy is None

    @pytest.mark.asyncio
    async def test_sid_10_shopify_gid_with_email(self) -> None:
        """Shopify GID + email → both linked as contact attributes on new profile."""
        repo = _mock_customer_repo(resolve_result=None)
        visitor = _visitor(
            customer_id="gid://shopify/Customer/77777",
            email="shopify@customer.com",
        )

        canonical, legacy = await _resolve_canonical_customer_id(visitor, TENANT, repo)

        assert canonical is not None
        call_kwargs = repo.create_profile_with_canonical_id.call_args
        attrs = call_kwargs.kwargs.get("contact_attributes", [])
        attr_types = {a.attribute_type for a in attrs}
        assert ContactAttributeType.SHOPIFY_CUSTOMER_GID in attr_types
        assert ContactAttributeType.EMAIL in attr_types


# ---------------------------------------------------------------------------
# SID-08, SID-09: start_conversation integration
# ---------------------------------------------------------------------------


class TestStartConversationCanonicalId:
    @pytest.fixture
    def conv_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.create = AsyncMock()
        return repo

    @pytest.mark.asyncio
    async def test_sid_08_with_customer_repo(self, conv_repo: AsyncMock) -> None:
        """start_conversation populates canonical_customer_id when repo is available."""
        customer_repo = _mock_customer_repo(resolve_result="cid_test-123")

        session = ConversationSession(
            conversation_repo=conv_repo,
            customer_profile_repo=customer_repo,
        )

        request = ConversationStartRequest(
            visitor=_visitor(email="test@example.com"),
        )

        await session.start_conversation(TENANT, request)

        # Verify the created document has canonical_customer_id
        conv_repo.create.assert_awaited_once()
        created_doc = conv_repo.create.call_args.args[1]
        assert created_doc.canonical_customer_id == "cid_test-123"
        assert created_doc.customer_id == "test@example.com"

    @pytest.mark.asyncio
    async def test_sid_09_legacy_no_customer_repo(self, conv_repo: AsyncMock) -> None:
        """start_conversation without customer_repo uses legacy resolution."""
        session = ConversationSession(
            conversation_repo=conv_repo,
        )

        request = ConversationStartRequest(
            visitor=_visitor(email="legacy@example.com"),
        )

        await session.start_conversation(TENANT, request)

        conv_repo.create.assert_awaited_once()
        created_doc = conv_repo.create.call_args.args[1]
        assert created_doc.canonical_customer_id is None  # Legacy mode
        assert created_doc.customer_id == "legacy@example.com"
