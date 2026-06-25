"""SPEC-1882 coverage for the superadmin contact provisioning gate."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.integrations.provisioning import (
    BillingChannel,
    _SUPERADMIN_CONTACT_REQUIRED_MESSAGE,
    _require_superadmin_contact,
    configure_provisioning_repo,
    provision_tenant,
    provision_trial_tenant,
)
from src.multi_tenant.cosmos_schema import BillingChannel as SchemaBillingChannel
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.trial_management import TrialManagementService
from tests.helpers.fake_tenant_repo import FakeDomainIndexRepo, FakeTenantRepo


@pytest.fixture
def fake_tenant_repo():
    repo = FakeTenantRepo()
    domain_repo = FakeDomainIndexRepo()
    configure_provisioning_repo(repo, team_repo=None, domain_index_repo=domain_repo)
    yield repo
    configure_provisioning_repo(None, team_repo=None, domain_index_repo=None)


def _make_trial_service() -> tuple[TrialManagementService, AsyncMock]:
    tenant_repo = AsyncMock()

    async def _create(doc):
        return doc

    tenant_repo.create.side_effect = _create
    usage_repo = AsyncMock()
    conversation_repo = AsyncMock()
    profile_repo = AsyncMock()
    knowledge_repo = AsyncMock()
    audit_repo = AsyncMock()
    return (
        TrialManagementService(
            tenant_repo=tenant_repo,
            usage_repo=usage_repo,
            conversation_repo=conversation_repo,
            profile_repo=profile_repo,
            knowledge_repo=knowledge_repo,
            audit_repo=audit_repo,
        ),
        tenant_repo,
    )


def test_contact_helper_rejects_missing_and_blank_contacts() -> None:
    with pytest.raises(ValueError, match=_SUPERADMIN_CONTACT_REQUIRED_MESSAGE):
        _require_superadmin_contact(None, None)

    with pytest.raises(ValueError, match=_SUPERADMIN_CONTACT_REQUIRED_MESSAGE):
        _require_superadmin_contact("  ", "\t")


def test_contact_helper_strips_email_and_phone() -> None:
    assert _require_superadmin_contact(" info@remakerdigital.com ", " +15555550123 ") == (
        "info@remakerdigital.com",
        "+15555550123",
    )


@pytest.mark.asyncio
async def test_paid_provisioning_rejects_contactless_tenant_before_write(fake_tenant_repo):
    with pytest.raises(ValueError, match=_SUPERADMIN_CONTACT_REQUIRED_MESSAGE):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_contactless",
            customer_email=" ",
            customer_phone=None,
        )

    assert fake_tenant_repo.store == {}


@pytest.mark.asyncio
async def test_paid_provisioning_normalizes_email_before_persisting(fake_tenant_repo):
    record = await provision_tenant(
        billing_channel=BillingChannel.STRIPE,
        tier="starter",
        stripe_customer_id="cus_email",
        customer_email=" info@remakerdigital.com ",
    )

    stored = fake_tenant_repo.store[record.tenant_id]
    assert record.customer_email == "info@remakerdigital.com"
    assert stored["customer_email"] == "info@remakerdigital.com"
    assert stored["display_name"] == "info@remakerdigital.com-001"


@pytest.mark.asyncio
async def test_paid_provisioning_accepts_phone_only_contact(fake_tenant_repo):
    record = await provision_tenant(
        billing_channel=BillingChannel.SHOPIFY,
        tier="professional",
        shopify_shop_domain="phone-only.myshopify.com",
        customer_phone=" +15555550123 ",
    )

    stored = fake_tenant_repo.store[record.tenant_id]
    assert record.customer_email is None
    assert record.customer_phone == "+15555550123"
    assert stored["customer_phone"] == "+15555550123"
    assert stored["display_name"] == "+15555550123-001"


@pytest.mark.asyncio
async def test_trial_provisioning_requires_contact(fake_tenant_repo):
    with pytest.raises(ValueError, match=_SUPERADMIN_CONTACT_REQUIRED_MESSAGE):
        await provision_trial_tenant(customer_email=None, customer_phone=" ")

    assert fake_tenant_repo.store == {}


@pytest.mark.asyncio
async def test_trial_provisioning_accepts_phone_only_contact(fake_tenant_repo):
    record = await provision_trial_tenant(customer_phone=" +15555550199 ")

    stored = fake_tenant_repo.store[record.tenant_id]
    assert record.status == TenantStatus.ACTIVE
    assert record.billing_channel == SchemaBillingChannel.TRIAL
    assert record.customer_email is None
    assert record.customer_phone == "+15555550199"
    assert stored["customer_phone"] == "+15555550199"


@pytest.mark.asyncio
async def test_trial_management_service_requires_and_persists_contact():
    service, tenant_repo = _make_trial_service()

    with pytest.raises(ValueError, match=_SUPERADMIN_CONTACT_REQUIRED_MESSAGE):
        await service.provision_trial(customer_email=" ", customer_phone=None)

    tenant_repo.create.assert_not_awaited()

    result = await service.provision_trial(
        customer_email=None,
        customer_phone=" +15555550188 ",
        seed_demo_data=False,
    )

    assert result["tier"] == TenantTier.TRIAL.value
    assert result["customer_email"] is None
    assert result["customer_phone"] == "+15555550188"
    tenant_repo.create.assert_awaited_once()
