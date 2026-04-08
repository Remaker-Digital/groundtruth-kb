"""SPEC-1881: Tenant display name — human-readable tenant identifier.
SPEC-1882: Superadmin contact requirement — hard provisioning gate.

Tests:
  - TenantDocument schema includes display_name and customer_phone fields
  - provision_tenant() rejects creation without contact address
  - provision_tenant() generates display_name from contact email
  - provision_tenant() generates display_name from contact phone
  - TenantSummaryItem includes display_name in API response
  - _generate_display_name() produces unique ordinals

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


# ---------------------------------------------------------------------------
# SPEC-1881: TenantDocument schema
# ---------------------------------------------------------------------------


class TestTenantDocumentSchema:
    """SPEC-1881: TenantDocument must include display_name field."""

    def test_display_name_field_exists(self):
        """display_name is a defined field on TenantDocument."""
        from src.multi_tenant.cosmos_schema import TenantDocument

        fields = TenantDocument.model_fields
        assert "display_name" in fields, "TenantDocument must have display_name field"

    def test_display_name_is_optional_for_migration(self):
        """display_name defaults to None (backward compat for existing docs)."""
        from src.multi_tenant.cosmos_schema import TenantDocument

        field = TenantDocument.model_fields["display_name"]
        assert field.default is None

    def test_customer_phone_field_exists(self):
        """customer_phone is a defined field on TenantDocument."""
        from src.multi_tenant.cosmos_schema import TenantDocument

        fields = TenantDocument.model_fields
        assert "customer_phone" in fields, "TenantDocument must have customer_phone field"

    def test_tenant_document_accepts_display_name(self):
        """TenantDocument can be constructed with display_name."""
        from src.multi_tenant.cosmos_schema import TenantDocument

        doc = TenantDocument(
            id="test-001",
            tenant_id="test-001",
            status="active",
            billing_channel="manual",
            display_name="Test Tenant-001",
            customer_email="test@example.com",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        assert doc.display_name == "Test Tenant-001"
        assert doc.customer_email == "test@example.com"


# ---------------------------------------------------------------------------
# SPEC-1882: Contact requirement gate
# ---------------------------------------------------------------------------


class TestContactRequirementGate:
    """SPEC-1882: provision_tenant() must reject creation without contact."""

    @pytest.mark.asyncio
    async def test_rejects_no_email_no_phone(self):
        """ValueError raised when both customer_email and customer_phone are None."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )

        repo = AsyncMock()
        configure_provisioning_repo(repo, team_repo=None)

        with pytest.raises(ValueError, match="superadministrator email or phone"):
            await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_email=None,
                customer_phone=None,
            )

        configure_provisioning_repo(None, team_repo=None)

    @pytest.mark.asyncio
    async def test_rejects_empty_email_no_phone(self):
        """ValueError raised when customer_email is empty string and no phone."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )

        repo = AsyncMock()
        configure_provisioning_repo(repo, team_repo=None)

        with pytest.raises(ValueError, match="superadministrator email or phone"):
            await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_email="",
                customer_phone="",
            )

        configure_provisioning_repo(None, team_repo=None)

    @pytest.mark.asyncio
    async def test_accepts_email_only(self):
        """Provisioning succeeds with email and no phone."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )
        from tests.helpers.fake_tenant_repo import FakeDomainIndexRepo, FakeTenantRepo

        repo = FakeTenantRepo()
        domain_repo = FakeDomainIndexRepo()
        configure_provisioning_repo(repo, team_repo=None, domain_index_repo=domain_repo)

        try:
            result = await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_email="test@example.com",
                customer_phone=None,
            )
            assert result.status is not None
        finally:
            configure_provisioning_repo(None, team_repo=None, domain_index_repo=None)

    @pytest.mark.asyncio
    async def test_accepts_phone_only(self):
        """Provisioning succeeds with phone and no email."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )
        from tests.helpers.fake_tenant_repo import FakeDomainIndexRepo, FakeTenantRepo

        repo = FakeTenantRepo()
        domain_repo = FakeDomainIndexRepo()
        configure_provisioning_repo(repo, team_repo=None, domain_index_repo=domain_repo)

        try:
            result = await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_email=None,
                customer_phone="+15551234567",
            )
            assert result.status is not None
        finally:
            configure_provisioning_repo(None, team_repo=None, domain_index_repo=None)


# ---------------------------------------------------------------------------
# SPEC-1881: Display name generation
# ---------------------------------------------------------------------------


class TestDisplayNameGeneration:
    """SPEC-1881: display_name generated from contact at provisioning."""

    @pytest.mark.asyncio
    async def test_display_name_from_email(self):
        """display_name defaults to {email}-001."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )
        from tests.helpers.fake_tenant_repo import FakeDomainIndexRepo, FakeTenantRepo

        repo = FakeTenantRepo()
        domain_repo = FakeDomainIndexRepo()
        configure_provisioning_repo(repo, team_repo=None, domain_index_repo=domain_repo)

        try:
            result = await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_email="merchant@example.com",
            )

            # Read the tenant doc from the fake repo
            doc = repo.store.get(result.tenant_id)
            assert doc is not None
            assert doc.get("display_name") == "merchant@example.com-001"
        finally:
            configure_provisioning_repo(None, team_repo=None, domain_index_repo=None)

    @pytest.mark.asyncio
    async def test_display_name_from_phone(self):
        """display_name defaults to {phone}-001 when no email."""
        from src.integrations.provisioning import (
            BillingChannel,
            configure_provisioning_repo,
            provision_tenant,
        )
        from tests.helpers.fake_tenant_repo import FakeDomainIndexRepo, FakeTenantRepo

        repo = FakeTenantRepo()
        domain_repo = FakeDomainIndexRepo()
        configure_provisioning_repo(repo, team_repo=None, domain_index_repo=domain_repo)

        try:
            result = await provision_tenant(
                billing_channel=BillingChannel.MANUAL,
                tier="starter",
                customer_phone="+15551234567",
            )

            doc = repo.store.get(result.tenant_id)
            assert doc is not None
            assert doc.get("display_name") == "+15551234567-001"
        finally:
            configure_provisioning_repo(None, team_repo=None, domain_index_repo=None)


# ---------------------------------------------------------------------------
# SPEC-1881: SPA API response
# ---------------------------------------------------------------------------


class TestTenantSummaryDisplayName:
    """SPEC-1881: TenantSummaryItem includes display_name."""

    def test_summary_item_has_display_name_field(self):
        """TenantSummaryItem response model includes display_name."""
        from src.multi_tenant.superadmin_api._tenants import TenantSummaryItem

        fields = TenantSummaryItem.model_fields
        assert "display_name" in fields, "TenantSummaryItem must include display_name"

    def test_summary_item_accepts_display_name(self):
        """TenantSummaryItem can be constructed with display_name."""
        from src.multi_tenant.superadmin_api._tenants import TenantSummaryItem

        item = TenantSummaryItem(
            tenant_id="test-001",
            display_name="Test Merchant-001",
            status="active",
            tier="starter",
        )
        assert item.display_name == "Test Merchant-001"

    def test_summary_item_display_name_optional(self):
        """display_name is optional (None for legacy tenants pre-backfill)."""
        from src.multi_tenant.superadmin_api._tenants import TenantSummaryItem

        item = TenantSummaryItem(
            tenant_id="test-001",
            status="active",
        )
        assert item.display_name is None
