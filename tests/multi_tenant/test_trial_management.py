"""Comprehensive tests for TrialManagementService — WI #120-128.

Covers the complete trial lifecycle: provisioning, expiry scanning,
conversation cap enforcement, model routing, trial-to-paid conversion,
demo data seeding, trial dashboard status, expired trial cleanup, and
metrics isolation.

Test IDs: TM-01 through TM-37 covering all 9 work items.

Run:
    pytest tests/multi_tenant/test_trial_management.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, call

import pytest

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    BillingChannel,
    TenantStatus,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.trial_management import (
    DEFAULT_TRIAL_CONVERSATION_LIMIT,
    DEFAULT_TRIAL_DURATION_DAYS,
    DEMO_CONVERSATION_COUNT,
    TRIAL_EXPIRED_GRACE_DAYS,
    TRIAL_MODEL,
    DemoDataResult,
    TrialCleanupResult,
    TrialConversionResult,
    TrialManagementService,
    TrialScanResult,
    TrialStatus,
    TrialStatusCode,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_ID = "t-trial-001"
_TENANT_ID_2 = "t-trial-002"
_TENANT_ID_3 = "t-trial-003"


def _make_repos(
    tenant_doc: dict | None = None,
    conversation_count: int = 0,
    usage_counters: list[dict] | None = None,
    query_results: list[dict] | None = None,
) -> tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
    """Build mock repositories for TrialManagementService.

    Returns:
        (tenant_repo, usage_repo, conversation_repo, profile_repo,
         knowledge_repo, audit_repo)
    """
    # -- Tenant repo --
    tenant_repo = AsyncMock()

    # create() stores the tenant doc and returns it
    async def _tenant_create(doc):
        return doc

    tenant_repo.create.side_effect = _tenant_create

    # read() returns the provided tenant doc or None
    if tenant_doc is not None:
        tenant_repo.read.return_value = tenant_doc
    else:
        tenant_repo.read.return_value = None

    # query() returns the provided query_results
    tenant_repo.query.return_value = query_results if query_results is not None else []

    # patch() returns None (success)
    tenant_repo.patch.return_value = None

    # -- Usage repo --
    usage_repo = AsyncMock()
    if usage_counters is not None:
        usage_repo.query.return_value = usage_counters
    else:
        usage_repo.query.return_value = []

    # -- Conversation repo --
    conversation_repo = AsyncMock()
    conversation_repo.create.return_value = {}

    # query for conversation count returns a list with one integer
    conversation_repo.query.return_value = [conversation_count]

    # -- Profile repo --
    profile_repo = AsyncMock()
    profile_repo.create.return_value = {}

    # -- Knowledge repo --
    knowledge_repo = AsyncMock()
    knowledge_repo.create.return_value = {}

    # -- Audit repo --
    audit_repo = AsyncMock()
    audit_repo.log_event.return_value = None

    return (
        tenant_repo,
        usage_repo,
        conversation_repo,
        profile_repo,
        knowledge_repo,
        audit_repo,
    )


def _make_trial_tenant(
    tenant_id: str = _TENANT_ID,
    status: str = TenantStatus.ACTIVE.value,
    days_from_now: int = 10,
    conversation_limit: int = DEFAULT_TRIAL_CONVERSATION_LIMIT,
    created_days_ago: int = 4,
    shop_domain: str | None = None,
) -> dict:
    """Build a trial tenant document dict."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=days_from_now)
    created_at = now - timedelta(days=created_days_ago)
    return {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": status,
        "billing_channel": BillingChannel.TRIAL.value,
        "tier": TenantTier.TRIAL.value,
        "interval": None,
        "addons": [],
        "customer_email": f"{tenant_id}@test.example.com",
        "shopify_shop_domain": shop_domain,
        "consent_status": "not_asked",
        "trial_expires_at": expires_at.isoformat(),
        "trial_conversation_limit": conversation_limit,
        "rate_limit_rpm": TIER_DEFAULTS[TenantTier.TRIAL.value]["rate_limit_rpm"],
        "max_concurrent": TIER_DEFAULTS[TenantTier.TRIAL.value]["max_concurrent"],
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    }


def _make_paid_tenant(
    tenant_id: str = "t-paid-001",
    tier: str = TenantTier.STARTER.value,
    status: str = TenantStatus.ACTIVE.value,
) -> dict:
    """Build a paid (non-trial) tenant document dict."""
    now = datetime.now(timezone.utc)
    return {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": status,
        "billing_channel": BillingChannel.STRIPE.value,
        "tier": tier,
        "interval": "month",
        "addons": [],
        "customer_email": f"{tenant_id}@test.example.com",
        "shopify_shop_domain": None,
        "consent_status": "not_asked",
        "trial_expires_at": None,
        "trial_conversation_limit": None,
        "rate_limit_rpm": TIER_DEFAULTS.get(tier, {}).get("rate_limit_rpm"),
        "max_concurrent": TIER_DEFAULTS.get(tier, {}).get("max_concurrent"),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }


def _make_service(
    tenant_doc: dict | None = None,
    conversation_count: int = 0,
    usage_counters: list[dict] | None = None,
    query_results: list[dict] | None = None,
) -> tuple[TrialManagementService, tuple[AsyncMock, ...]]:
    """Create a TrialManagementService with mocked repos.

    Returns:
        (service, (tenant_repo, usage_repo, conversation_repo,
         profile_repo, knowledge_repo, audit_repo))
    """
    repos = _make_repos(
        tenant_doc=tenant_doc,
        conversation_count=conversation_count,
        usage_counters=usage_counters,
        query_results=query_results,
    )
    tenant_repo, usage_repo, conversation_repo, profile_repo, knowledge_repo, audit_repo = repos

    service = TrialManagementService(
        tenant_repo=tenant_repo,
        usage_repo=usage_repo,
        conversation_repo=conversation_repo,
        profile_repo=profile_repo,
        knowledge_repo=knowledge_repo,
        audit_repo=audit_repo,
    )
    return service, repos


# ===========================================================================
# WI #120 — Trial provisioning (~5 tests)
# ===========================================================================


class TestTrialProvisioning:
    """TM-01 through TM-05: Trial provisioning flow."""

    async def test_tm_01_provision_basic_trial(self):
        """TM-01: Provision a basic trial tenant with default parameters.

        Verifies: tier=trial, status=active, trial_expires_at set ~14 days
        in the future, trial_conversation_limit=50, billing_channel=trial.
        """
        service, repos = _make_service()
        tenant_repo, _, _, _, _, audit_repo = repos

        result = await service.provision_trial(
            customer_email="test@example.com",
        )

        assert result["tier"] == TenantTier.TRIAL.value
        assert result["status"] == TenantStatus.ACTIVE.value
        assert result["billing_channel"] == BillingChannel.TRIAL.value
        assert result["trial_conversation_limit"] == DEFAULT_TRIAL_CONVERSATION_LIMIT
        assert result["customer_email"] == "test@example.com"

        # trial_expires_at should be approximately 14 days from now
        expires_at = datetime.fromisoformat(result["trial_expires_at"])
        now = datetime.now(timezone.utc)
        delta = expires_at - now
        assert 13 <= delta.days <= 14  # Allow for test execution time

        # Verify tenant was persisted
        tenant_repo.create.assert_awaited_once()
        created_doc = tenant_repo.create.call_args[0][0]
        assert created_doc["tier"] == TenantTier.TRIAL.value

    async def test_tm_02_provision_custom_duration_and_limit(self):
        """TM-02: Provision trial with custom duration and conversation limit."""
        service, repos = _make_service()
        tenant_repo = repos[0]

        result = await service.provision_trial(
            customer_email="custom@example.com",
            trial_duration_days=7,
            conversation_limit=25,
        )

        assert result["trial_conversation_limit"] == 25

        # Expiry should be ~7 days from now (not 14)
        expires_at = datetime.fromisoformat(result["trial_expires_at"])
        now = datetime.now(timezone.utc)
        delta = expires_at - now
        assert 6 <= delta.days <= 7

        tenant_repo.create.assert_awaited_once()

    async def test_tm_03_provision_with_shopify_domain(self):
        """TM-03: Provision trial with Shopify shop domain attached."""
        service, repos = _make_service()

        result = await service.provision_trial(
            customer_email="shop@example.com",
            shopify_shop_domain="my-shop.myshopify.com",
        )

        assert result["shopify_shop_domain"] == "my-shop.myshopify.com"
        assert result["tier"] == TenantTier.TRIAL.value

    async def test_tm_04_provision_calls_demo_data_seeding(self):
        """TM-04: Provisioning with seed_demo_data=True calls seed_demo_data."""
        service, repos = _make_service()
        conversation_repo = repos[2]

        result = await service.provision_trial(
            customer_email="demo@example.com",
            seed_demo_data=True,
        )

        # Demo conversations should have been created
        # _build_demo_conversations creates 5 conversations
        assert conversation_repo.create.await_count >= DEMO_CONVERSATION_COUNT

    async def test_tm_05_provision_creates_audit_log(self):
        """TM-05: Provisioning creates an audit log entry."""
        service, repos = _make_service()
        audit_repo = repos[5]

        result = await service.provision_trial(
            customer_email="audit@example.com",
        )

        audit_repo.log_event.assert_awaited_once()
        log_call = audit_repo.log_event.call_args
        assert log_call.kwargs["event_type"] == AuditEventType.TENANT_PROVISIONED
        assert log_call.kwargs["actor"] == "system"
        assert log_call.kwargs["details"]["tier"] == "trial"
        assert log_call.kwargs["details"]["email"] == "audit@example.com"


# ===========================================================================
# WI #121 — Trial expiry scanning (~5 tests)
# ===========================================================================


class TestTrialExpiryScan:
    """TM-06 through TM-10: Trial expiry scanning."""

    async def test_tm_06_scan_no_expired_trials(self):
        """TM-06: Scan when all trials are still active (none expired)."""
        # Active trial with 10 days remaining
        active_trial = _make_trial_tenant(days_from_now=10)
        service, repos = _make_service(query_results=[active_trial])

        result = await service.scan_expired_trials()

        assert isinstance(result, TrialScanResult)
        assert result.scanned_count == 1
        assert result.expired_count == 0
        assert result.expiring_soon_count == 0
        assert result.expired_tenant_ids == []

    async def test_tm_07_scan_transitions_expired_trial(self):
        """TM-07: Scan detects and transitions an expired trial to TRIAL_EXPIRED."""
        # Trial that expired 2 hours ago
        expired_trial = _make_trial_tenant(
            tenant_id=_TENANT_ID,
            days_from_now=-1,  # Expired yesterday
        )
        service, repos = _make_service(query_results=[expired_trial])
        tenant_repo = repos[0]

        result = await service.scan_expired_trials()

        assert result.expired_count == 1
        assert _TENANT_ID in result.expired_tenant_ids

        # Verify patch was called to set TRIAL_EXPIRED status
        tenant_repo.patch.assert_awaited_once()
        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[1].get("operations") or patch_call[0][2]
        status_op = next(op for op in operations if op["path"] == "/status")
        assert status_op["value"] == TenantStatus.TRIAL_EXPIRED.value

    async def test_tm_08_scan_identifies_expiring_soon(self):
        """TM-08: Scan counts trials expiring within 3 days as expiring_soon."""
        # Trial expiring in 2 days (< 3 day threshold)
        expiring_trial = _make_trial_tenant(days_from_now=2)
        service, repos = _make_service(query_results=[expiring_trial])

        result = await service.scan_expired_trials()

        assert result.scanned_count == 1
        assert result.expired_count == 0
        assert result.expiring_soon_count == 1

    async def test_tm_09_scan_invalid_expires_at_handled(self):
        """TM-09: Invalid trial_expires_at value is handled gracefully."""
        invalid_trial = _make_trial_tenant()
        invalid_trial["trial_expires_at"] = "not-a-valid-date"
        service, repos = _make_service(query_results=[invalid_trial])

        result = await service.scan_expired_trials()

        # Should be scanned but not counted as expired or expiring
        assert result.scanned_count == 1
        assert result.expired_count == 0
        assert result.expiring_soon_count == 0

    async def test_tm_10_scan_creates_audit_on_expiry(self):
        """TM-10: Audit log entry is created when a trial expires."""
        expired_trial = _make_trial_tenant(
            tenant_id=_TENANT_ID,
            days_from_now=-1,
        )
        service, repos = _make_service(query_results=[expired_trial])
        audit_repo = repos[5]

        await service.scan_expired_trials()

        audit_repo.log_event.assert_awaited_once()
        log_call = audit_repo.log_event.call_args
        assert log_call.kwargs["event_type"] == AuditEventType.TENANT_DEACTIVATED
        assert log_call.kwargs["details"]["reason"] == "trial_expired"


# ===========================================================================
# WI #122 — Conversation cap enforcement (~5 tests)
# ===========================================================================


class TestTrialCapEnforcement:
    """TM-11 through TM-15: Trial conversation cap enforcement."""

    async def test_tm_11_allow_when_under_cap(self):
        """TM-11: Allow conversation when usage is under the cap."""
        trial_tenant = _make_trial_tenant(conversation_limit=50)
        service, repos = _make_service(
            tenant_doc=trial_tenant,
            conversation_count=10,  # Well under 50
        )

        allowed, status = await service.enforce_trial_cap(_TENANT_ID)

        assert allowed is True
        assert status is not None
        assert status.conversations_remaining == 40
        assert status.can_send_message is True

    async def test_tm_12_block_when_cap_reached(self):
        """TM-12: Block conversation when cap has been reached."""
        trial_tenant = _make_trial_tenant(conversation_limit=50)
        service, repos = _make_service(
            tenant_doc=trial_tenant,
            conversation_count=50,  # At the cap
        )

        allowed, status = await service.enforce_trial_cap(_TENANT_ID)

        assert allowed is False
        assert status is not None
        assert status.conversations_remaining == 0
        assert status.status == TrialStatusCode.CAP_REACHED

    async def test_tm_13_block_when_trial_expired(self):
        """TM-13: Block conversation when trial has expired."""
        expired_tenant = _make_trial_tenant(
            days_from_now=-1,
            status=TenantStatus.TRIAL_EXPIRED.value,
        )
        service, repos = _make_service(
            tenant_doc=expired_tenant,
            conversation_count=5,
        )

        allowed, status = await service.enforce_trial_cap(_TENANT_ID)

        assert allowed is False
        assert status is not None
        assert status.status == TrialStatusCode.EXPIRED

    async def test_tm_14_non_trial_passes_through(self):
        """TM-14: Non-trial tenant bypasses cap enforcement entirely."""
        paid_tenant = _make_paid_tenant(tier=TenantTier.STARTER.value)
        service, repos = _make_service(tenant_doc=paid_tenant)

        allowed, status = await service.enforce_trial_cap("t-paid-001")

        assert allowed is True
        assert status is None  # No TrialStatus for paid tenants

    async def test_tm_15_tenant_not_found_returns_false(self):
        """TM-15: Returns (False, None) when tenant does not exist."""
        service, repos = _make_service(tenant_doc=None)

        allowed, status = await service.enforce_trial_cap("nonexistent-tenant")

        assert allowed is False
        assert status is None


# ===========================================================================
# WI #123 — Trial model routing (~3 tests)
# ===========================================================================


class TestTrialModelRouting:
    """TM-16 through TM-18: Trial model routing for cost containment."""

    def test_tm_16_trial_returns_gpt4o_mini(self):
        """TM-16: Trial tier returns 'gpt-4o-mini' model identifier."""
        result = TrialManagementService.get_trial_model(TenantTier.TRIAL)

        assert result == TRIAL_MODEL
        assert result == "gpt-4o-mini"

    def test_tm_17_paid_tiers_return_none(self):
        """TM-17: Starter, Professional, Enterprise return None (use default)."""
        assert TrialManagementService.get_trial_model(TenantTier.STARTER) is None
        assert TrialManagementService.get_trial_model(TenantTier.PROFESSIONAL) is None
        assert TrialManagementService.get_trial_model(TenantTier.ENTERPRISE) is None

    def test_tm_18_works_with_string_tier(self):
        """TM-18: Accepts both TenantTier enum and raw string values."""
        assert TrialManagementService.get_trial_model("trial") == TRIAL_MODEL
        assert TrialManagementService.get_trial_model("starter") is None
        assert TrialManagementService.get_trial_model("professional") is None
        assert TrialManagementService.get_trial_model("enterprise") is None


# ===========================================================================
# WI #124 — Trial → paid conversion (~5 tests)
# ===========================================================================


class TestTrialConversion:
    """TM-19 through TM-23: Trial to paid tier conversion."""

    async def test_tm_19_convert_trial_to_starter(self):
        """TM-19: Convert trial to Starter tier with Stripe billing."""
        trial_tenant = _make_trial_tenant()
        service, repos = _make_service(
            tenant_doc=trial_tenant,
            usage_counters=[{"total_conversations": 12}],
        )
        tenant_repo = repos[0]

        result = await service.convert_trial_to_paid(
            tenant_id=_TENANT_ID,
            new_tier=TenantTier.STARTER,
            billing_channel=BillingChannel.STRIPE,
        )

        assert isinstance(result, TrialConversionResult)
        assert result.tenant_id == _TENANT_ID
        assert result.previous_tier == TenantTier.TRIAL.value
        assert result.new_tier == TenantTier.STARTER.value
        assert result.billing_channel == BillingChannel.STRIPE.value
        assert result.data_preserved is True
        assert result.conversations_carried_over == 12

        # Verify patch operations include clearing trial fields
        tenant_repo.patch.assert_awaited_once()
        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[0][2]

        # Extract operation paths and values
        ops_dict = {op["path"]: op["value"] for op in operations}
        assert ops_dict["/tier"] == TenantTier.STARTER.value
        assert ops_dict["/status"] == TenantStatus.ACTIVE.value
        assert ops_dict["/billing_channel"] == BillingChannel.STRIPE.value
        assert ops_dict["/trial_expires_at"] is None
        assert ops_dict["/trial_conversation_limit"] is None
        assert ops_dict["/rate_limit_rpm"] == TIER_DEFAULTS[TenantTier.STARTER.value]["rate_limit_rpm"]
        assert ops_dict["/max_concurrent"] == TIER_DEFAULTS[TenantTier.STARTER.value]["max_concurrent"]

    async def test_tm_20_convert_with_stripe_customer_id(self):
        """TM-20: Convert trial with Stripe customer and subscription IDs."""
        trial_tenant = _make_trial_tenant()
        service, repos = _make_service(tenant_doc=trial_tenant)
        tenant_repo = repos[0]

        result = await service.convert_trial_to_paid(
            tenant_id=_TENANT_ID,
            new_tier=TenantTier.PROFESSIONAL,
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_test_abc123",
            stripe_subscription_id="sub_test_xyz789",
        )

        assert result.new_tier == TenantTier.PROFESSIONAL.value

        # Verify Stripe IDs were included in patch operations
        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[0][2]
        ops_dict = {op["path"]: op["value"] for op in operations}
        assert ops_dict["/stripe_customer_id"] == "cus_test_abc123"
        assert ops_dict["/stripe_subscription_id"] == "sub_test_xyz789"

    async def test_tm_21_convert_with_shopify_subscription(self):
        """TM-21: Convert trial with Shopify subscription ID."""
        trial_tenant = _make_trial_tenant(shop_domain="convert-shop.myshopify.com")
        service, repos = _make_service(tenant_doc=trial_tenant)
        tenant_repo = repos[0]

        result = await service.convert_trial_to_paid(
            tenant_id=_TENANT_ID,
            new_tier=TenantTier.STARTER,
            billing_channel=BillingChannel.SHOPIFY,
            shopify_subscription_id="gid://shopify/AppSubscription/12345",
        )

        assert result.billing_channel == BillingChannel.SHOPIFY.value

        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[0][2]
        ops_dict = {op["path"]: op["value"] for op in operations}
        assert ops_dict["/shopify_subscription_id"] == "gid://shopify/AppSubscription/12345"
        assert ops_dict["/billing_channel"] == BillingChannel.SHOPIFY.value

    async def test_tm_22_convert_raises_if_not_trial(self):
        """TM-22: ValueError raised if tenant is not on trial tier."""
        paid_tenant = _make_paid_tenant(tier=TenantTier.STARTER.value)
        service, repos = _make_service(tenant_doc=paid_tenant)

        with pytest.raises(ValueError, match="not a trial"):
            await service.convert_trial_to_paid(
                tenant_id="t-paid-001",
                new_tier=TenantTier.PROFESSIONAL,
                billing_channel=BillingChannel.STRIPE,
            )

    async def test_tm_23_convert_raises_if_tenant_not_found(self):
        """TM-23: ValueError raised if tenant does not exist."""
        service, repos = _make_service(tenant_doc=None)

        with pytest.raises(ValueError, match="Tenant not found"):
            await service.convert_trial_to_paid(
                tenant_id="nonexistent",
                new_tier=TenantTier.STARTER,
                billing_channel=BillingChannel.STRIPE,
            )


# ===========================================================================
# WI #125 — Demo data seeding (~3 tests)
# ===========================================================================


class TestDemoDataSeeding:
    """TM-24 through TM-26: Demo data seeding for trial tenants."""

    async def test_tm_24_seeds_conversations_profiles_knowledge(self):
        """TM-24: seed_demo_data populates conversations, profiles, and KB articles."""
        service, repos = _make_service()
        conversation_repo, profile_repo, knowledge_repo = repos[2], repos[3], repos[4]

        result = await service.seed_demo_data(_TENANT_ID)

        assert isinstance(result, DemoDataResult)
        assert result.tenant_id == _TENANT_ID
        assert result.conversations_seeded == DEMO_CONVERSATION_COUNT  # 5 demo conversations
        assert result.profiles_seeded == 2   # 2 demo profiles from _build_demo_profiles
        assert result.knowledge_articles_seeded == 3  # 3 demo KB articles

        assert conversation_repo.create.await_count == DEMO_CONVERSATION_COUNT
        assert profile_repo.create.await_count == 2
        assert knowledge_repo.create.await_count == 3

    async def test_tm_25_demo_conversations_use_non_billable_prefix(self):
        """TM-25: Demo conversations use 'system_demo_' prefix (non-billable)."""
        service, repos = _make_service()
        conversation_repo = repos[2]

        await service.seed_demo_data(_TENANT_ID)

        # Check all created conversation docs have system_demo_ prefix
        for call_item in conversation_repo.create.call_args_list:
            conv_doc = call_item[0][0]
            assert conv_doc["conversation_id"].startswith("system_demo_"), (
                f"Demo conversation ID should start with 'system_demo_', "
                f"got: {conv_doc['conversation_id']}"
            )
            assert conv_doc["is_billable"] is False

    async def test_tm_26_handles_missing_repos_gracefully(self):
        """TM-26: seed_demo_data works when optional repos are None."""
        tenant_repo = AsyncMock()
        usage_repo = AsyncMock()

        service = TrialManagementService(
            tenant_repo=tenant_repo,
            usage_repo=usage_repo,
            conversation_repo=None,
            profile_repo=None,
            knowledge_repo=None,
            audit_repo=None,
        )

        result = await service.seed_demo_data(_TENANT_ID)

        assert result.conversations_seeded == 0
        assert result.profiles_seeded == 0
        assert result.knowledge_articles_seeded == 0


# ===========================================================================
# WI #126 — Trial status/dashboard (~5 tests)
# ===========================================================================


class TestTrialStatusDashboard:
    """TM-27 through TM-31: Trial status for dashboard display."""

    async def test_tm_27_active_trial_with_days_remaining(self):
        """TM-27: Active trial returns correct days/hours remaining."""
        trial_tenant = _make_trial_tenant(days_from_now=10, conversation_limit=50)
        service, repos = _make_service(
            tenant_doc=trial_tenant,
            conversation_count=5,
        )

        status = await service.get_trial_status(_TENANT_ID)

        assert status is not None
        assert isinstance(status, TrialStatus)
        assert status.status == TrialStatusCode.ACTIVE
        assert status.days_remaining >= 9  # Allow for execution time
        assert status.days_remaining <= 10
        assert status.hours_remaining >= 216  # ~9 days in hours
        assert status.conversation_limit == 50
        assert status.conversations_used == 5
        assert status.conversations_remaining == 45
        assert status.can_send_message is True
        assert status.model == TRIAL_MODEL
        assert status.tier_after_expiry == "starter"  # < 30 conversations used

    async def test_tm_28_expiring_soon_within_3_days(self):
        """TM-28: Trial with < 3 days remaining has EXPIRING_SOON status."""
        expiring_tenant = _make_trial_tenant(days_from_now=2, conversation_limit=50)
        service, repos = _make_service(
            tenant_doc=expiring_tenant,
            conversation_count=10,
        )

        status = await service.get_trial_status(_TENANT_ID)

        assert status is not None
        assert status.status == TrialStatusCode.EXPIRING_SOON
        assert status.days_remaining <= 2
        assert status.can_send_message is True  # Still allowed to send

    async def test_tm_29_expired_trial(self):
        """TM-29: Expired trial returns EXPIRED status with can_send=False."""
        expired_tenant = _make_trial_tenant(
            days_from_now=-1,
            status=TenantStatus.TRIAL_EXPIRED.value,
        )
        service, repos = _make_service(
            tenant_doc=expired_tenant,
            conversation_count=20,
        )

        status = await service.get_trial_status(_TENANT_ID)

        assert status is not None
        assert status.status == TrialStatusCode.EXPIRED
        assert status.days_remaining == 0
        assert status.can_send_message is False

    async def test_tm_30_cap_reached_conversations_remaining_zero(self):
        """TM-30: Trial with all conversations used returns CAP_REACHED."""
        trial_tenant = _make_trial_tenant(days_from_now=10, conversation_limit=50)
        service, repos = _make_service(
            tenant_doc=trial_tenant,
            conversation_count=50,  # All conversations used
        )

        status = await service.get_trial_status(_TENANT_ID)

        assert status is not None
        assert status.status == TrialStatusCode.CAP_REACHED
        assert status.conversations_remaining == 0
        assert status.usage_percent == 100.0
        assert status.can_send_message is False
        assert status.tier_after_expiry == "professional"  # > 30 conversations

    async def test_tm_31_non_trial_returns_none(self):
        """TM-31: Non-trial tenant returns None (no trial status)."""
        paid_tenant = _make_paid_tenant(tier=TenantTier.PROFESSIONAL.value)
        service, repos = _make_service(tenant_doc=paid_tenant)

        status = await service.get_trial_status("t-paid-001")

        assert status is None


# ===========================================================================
# WI #127 — Expired trial cleanup (~3 tests)
# ===========================================================================


class TestExpiredTrialCleanup:
    """TM-32 through TM-34: Expired trial data cleanup after grace period."""

    async def test_tm_32_skip_within_grace_period(self):
        """TM-32: Expired trials within grace period are not cleaned."""
        # Expired trial updated 5 days ago (< 30 day grace)
        recent_expired = _make_trial_tenant(
            tenant_id=_TENANT_ID,
            status=TenantStatus.TRIAL_EXPIRED.value,
            days_from_now=-5,
        )
        # Set updated_at to 5 days ago (within grace period)
        recent_expired["updated_at"] = (
            datetime.now(timezone.utc) - timedelta(days=5)
        ).isoformat()

        service, repos = _make_service(query_results=[recent_expired])
        tenant_repo = repos[0]

        result = await service.cleanup_expired_trials()

        assert isinstance(result, TrialCleanupResult)
        assert result.tenants_cleaned == 0
        assert result.tenant_ids == []
        # No patch call for deactivation
        tenant_repo.patch.assert_not_awaited()

    async def test_tm_33_delete_past_grace_period(self):
        """TM-33: Expired trials past grace period have data deleted and status set to DEACTIVATED."""
        # Expired trial updated 35 days ago (past 30-day grace)
        old_expired = _make_trial_tenant(
            tenant_id=_TENANT_ID,
            status=TenantStatus.TRIAL_EXPIRED.value,
            days_from_now=-40,
        )
        old_expired["updated_at"] = (
            datetime.now(timezone.utc) - timedelta(days=35)
        ).isoformat()

        service, repos = _make_service(query_results=[old_expired])
        tenant_repo = repos[0]
        conversation_repo = repos[2]
        audit_repo = repos[5]

        # Mock the query for data deletion to return some items
        conversation_repo.query.return_value = [{"id": "conv1"}, {"id": "conv2"}]

        result = await service.cleanup_expired_trials()

        assert result.tenants_cleaned == 1
        assert _TENANT_ID in result.tenant_ids

        # Verify status patched to DEACTIVATED
        tenant_repo.patch.assert_awaited()
        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[0][2]
        ops_dict = {op["path"]: op["value"] for op in operations}
        assert ops_dict["/status"] == TenantStatus.DEACTIVATED.value
        assert "/deactivated_at" in ops_dict

        # Verify audit log
        audit_repo.log_event.assert_awaited_once()
        log_call = audit_repo.log_event.call_args
        assert log_call.kwargs["event_type"] == AuditEventType.DATA_DELETED
        assert log_call.kwargs["details"]["reason"] == "trial_expired_grace_period_elapsed"

    async def test_tm_34_transition_to_deactivated(self):
        """TM-34: Cleaned trial transitions to DEACTIVATED with deactivated_at timestamp."""
        old_expired = _make_trial_tenant(
            tenant_id=_TENANT_ID_2,
            status=TenantStatus.TRIAL_EXPIRED.value,
        )
        old_expired["updated_at"] = (
            datetime.now(timezone.utc) - timedelta(days=TRIAL_EXPIRED_GRACE_DAYS + 5)
        ).isoformat()

        service, repos = _make_service(query_results=[old_expired])
        tenant_repo = repos[0]

        result = await service.cleanup_expired_trials()

        assert result.tenants_cleaned == 1

        # Verify deactivated_at is set to approximately now
        patch_call = tenant_repo.patch.call_args
        operations = patch_call.kwargs.get("operations") or patch_call[0][2]
        deactivated_op = next(op for op in operations if op["path"] == "/deactivated_at")
        deactivated_at = datetime.fromisoformat(deactivated_op["value"])
        now = datetime.now(timezone.utc)
        assert abs((now - deactivated_at).total_seconds()) < 5  # Within 5 seconds


# ===========================================================================
# WI #128 — Metrics isolation (~3 tests)
# ===========================================================================


class TestMetricsIsolation:
    """TM-35 through TM-37: Trial metrics exclusion from platform benchmarks."""

    def test_tm_35_is_trial_tenant_true_for_trial(self):
        """TM-35: is_trial_tenant returns True for trial-tier tenant."""
        trial_doc = {"tier": TenantTier.TRIAL.value, "status": TenantStatus.ACTIVE.value}
        assert TrialManagementService.is_trial_tenant(trial_doc) is True

    def test_tm_36_should_exclude_trial_and_expired(self):
        """TM-36: should_exclude_from_benchmarks returns True for trial and trial_expired."""
        trial_active = {"tier": TenantTier.TRIAL.value, "status": TenantStatus.ACTIVE.value}
        assert TrialManagementService.should_exclude_from_benchmarks(trial_active) is True

        trial_expired = {"tier": TenantTier.TRIAL.value, "status": TenantStatus.TRIAL_EXPIRED.value}
        assert TrialManagementService.should_exclude_from_benchmarks(trial_expired) is True

        # Non-trial but TRIAL_EXPIRED status should also be excluded
        weird_case = {"tier": TenantTier.STARTER.value, "status": TenantStatus.TRIAL_EXPIRED.value}
        assert TrialManagementService.should_exclude_from_benchmarks(weird_case) is True

    def test_tm_37_should_not_exclude_paid_tiers(self):
        """TM-37: should_exclude_from_benchmarks returns False for paid active tiers."""
        starter = {"tier": TenantTier.STARTER.value, "status": TenantStatus.ACTIVE.value}
        assert TrialManagementService.should_exclude_from_benchmarks(starter) is False

        professional = {"tier": TenantTier.PROFESSIONAL.value, "status": TenantStatus.ACTIVE.value}
        assert TrialManagementService.should_exclude_from_benchmarks(professional) is False

        enterprise = {"tier": TenantTier.ENTERPRISE.value, "status": TenantStatus.ACTIVE.value}
        assert TrialManagementService.should_exclude_from_benchmarks(enterprise) is False
