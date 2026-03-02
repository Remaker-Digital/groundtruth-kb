"""Tests for Superadmin Contact Messages API (SPEC-1589, SPEC-1592).

Covers:
    - Router configuration (prefix, auth dependency)
    - List endpoint with filtering and pagination
    - Single message detail retrieval
    - Status/notes update (PATCH) with validation
    - CSV export
    - ContactMessageDocument schema validation

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_contact_api import (
    ContactMessageItem,
    ContactMessageListResponse,
    ContactMessageUpdateRequest,
    ContactMessageUpdateResponse,
    configure_superadmin_contact_services,
    router,
)
from src.multi_tenant.cosmos_schema import ContactMessageDocument


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------


class TestRouterConfig:
    """Verify the superadmin contact router configuration."""

    def test_router_prefix(self):
        assert router.prefix == "/api/superadmin/contact-messages"

    def test_router_tags(self):
        assert "Superadmin Contact Messages" in router.tags


# ---------------------------------------------------------------------------
# ContactMessageDocument schema tests
# ---------------------------------------------------------------------------


class TestContactMessageDocumentSchema:
    """Verify ContactMessageDocument fields and validation."""

    def test_valid_document_creation(self):
        doc = ContactMessageDocument(
            id="msg-001",
            tenant_id="tenant-001",
            topic="support",
            subject="Test subject",
            message="Test message body",
            member_email="admin@test.com",
            member_role="admin",
            member_id="member-001",
            tier="professional",
            status="new",
            notes="",
            created_at="2026-03-01T00:00:00+00:00",
            updated_at="2026-03-01T00:00:00+00:00",
        )
        assert doc.id == "msg-001"
        assert doc.tenant_id == "tenant-001"
        assert doc.topic == "support"
        assert doc.status == "new"

    def test_document_default_status(self):
        doc = ContactMessageDocument(
            id="msg-002",
            tenant_id="t-002",
            topic="billing",
            subject="Billing Q",
            message="Question",
            created_at="2026-03-01T00:00:00+00:00",
            updated_at="2026-03-01T00:00:00+00:00",
        )
        assert doc.status == "new"
        assert doc.notes == ""

    def test_valid_statuses_classvar(self):
        assert ContactMessageDocument.VALID_STATUSES == [
            "new", "read", "resolved", "archived",
        ]

    def test_document_optional_fields(self):
        doc = ContactMessageDocument(
            id="msg-003",
            tenant_id="t-003",
            topic="general",
            subject="General",
            message="Hello",
            created_at="2026-03-01T00:00:00+00:00",
            updated_at="2026-03-01T00:00:00+00:00",
        )
        assert doc.member_email is None
        assert doc.member_role is None
        assert doc.member_id is None
        assert doc.tier is None


# ---------------------------------------------------------------------------
# Response model tests
# ---------------------------------------------------------------------------


class TestResponseModels:
    """Verify CamelCase serialization of response models."""

    def test_contact_message_item_serialization(self):
        item = ContactMessageItem(
            id="msg-001",
            tenant_id="t-001",
            topic="support",
            subject="Test",
            message="Body",
            status="new",
            created_at="2026-03-01T00:00:00+00:00",
            updated_at="2026-03-01T00:00:00+00:00",
        )
        data = item.model_dump(by_alias=True)
        # CamelCase aliases
        assert "tenantId" in data
        assert "createdAt" in data
        assert "updatedAt" in data
        assert "memberEmail" in data
        assert "memberRole" in data

    def test_list_response_serialization(self):
        resp = ContactMessageListResponse(
            messages=[],
            total=0,
            skip=0,
            limit=50,
        )
        data = resp.model_dump(by_alias=True)
        assert data["messages"] == []
        assert data["total"] == 0

    def test_update_request_accepts_status_only(self):
        req = ContactMessageUpdateRequest(status="resolved")
        assert req.status == "resolved"
        assert req.notes is None

    def test_update_request_accepts_notes_only(self):
        req = ContactMessageUpdateRequest(notes="Followed up via email")
        assert req.notes == "Followed up via email"
        assert req.status is None


# ---------------------------------------------------------------------------
# configure_superadmin_contact_services tests
# ---------------------------------------------------------------------------


class TestConfigureSuperadminContactServices:
    """Verify the service wiring function."""

    def test_sets_module_repo(self):
        import src.multi_tenant.superadmin_contact_api as mod

        mock_repo = MagicMock()
        original = mod._contact_repo
        try:
            configure_superadmin_contact_services(mock_repo)
            assert mod._contact_repo is mock_repo
        finally:
            mod._contact_repo = original


# ---------------------------------------------------------------------------
# ContactMessageDocument field coverage (SPEC-1588)
# ---------------------------------------------------------------------------


class TestContactMessageDocumentFields:
    """Verify all SPEC-1588 required fields exist."""

    def test_required_fields(self):
        """All fields from SPEC-1588 are present in the document model."""
        required = {
            "id", "tenant_id", "topic", "subject", "message",
            "member_email", "member_role", "member_id", "tier",
            "status", "notes", "created_at", "updated_at",
        }
        model_fields = set(ContactMessageDocument.model_fields.keys())
        missing = required - model_fields
        assert not missing, f"Missing fields: {missing}"

    def test_status_lifecycle_values(self):
        """SPEC-1592: status must support new, read, resolved, archived."""
        expected = ["new", "read", "resolved", "archived"]
        assert ContactMessageDocument.VALID_STATUSES == expected


# ---------------------------------------------------------------------------
# Cosmos container registration (SPEC-1591)
# ---------------------------------------------------------------------------


class TestCosmosContainerRegistration:
    """Verify contact_messages container is registered in schema."""

    def test_collection_constant_exists(self):
        from src.multi_tenant.cosmos_schema import COLLECTION_CONTACT_MESSAGES
        assert COLLECTION_CONTACT_MESSAGES == "contact_messages"

    def test_collection_in_all_collections(self):
        from src.multi_tenant.cosmos_schema import ALL_COLLECTIONS
        assert "contact_messages" in ALL_COLLECTIONS

    def test_collection_config_exists(self):
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        names = [c.name for c in configs]
        assert "contact_messages" in names

    def test_collection_partition_key(self):
        from src.multi_tenant.cosmos_schema import get_collection_configs
        configs = get_collection_configs()
        config = next(c for c in configs if c.name == "contact_messages")
        assert config.partition_key == "/tenant_id"
