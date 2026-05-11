"""
Trial lifecycle end-to-end tests (MT-1009→MT-1013).

Tests the complete trial tenant lifecycle: provisioning, conversation
consumption, paid conversion, expiry scanning, and demo data seeding.

Master Test Plan: §4 Gap Register — Trial Lifecycle E2E (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    BillingChannel,
    TenantStatus,
    TenantTier,
)
from src.multi_tenant.trial_management import (
    DEFAULT_TRIAL_CONVERSATION_LIMIT,
    DEFAULT_TRIAL_DURATION_DAYS,
    DEMO_CONVERSATION_COUNT,
    TRIAL_EXPIRED_GRACE_DAYS,
    TRIAL_MODEL,
    TrialConversionResult,
    TrialManagementService,
    TrialScanResult,
)


# ---------------------------------------------------------------------------
# Mock repositories
# ---------------------------------------------------------------------------


def _mock_repos():
    """Create a set of mock repositories for TrialManagementService."""
    tenant_repo = AsyncMock()
    usage_repo = AsyncMock()
    conversation_repo = AsyncMock()
    profile_repo = AsyncMock()
    knowledge_repo = AsyncMock()
    audit_repo = AsyncMock()

    # Default: tenant_repo.create succeeds
    tenant_repo.create = AsyncMock(return_value=None)
    # Default: audit_repo.log_event succeeds
    audit_repo.log_event = AsyncMock(return_value=None)
    # Default: conversation_repo.create succeeds
    conversation_repo.create = AsyncMock(return_value=None)

    return {
        "tenant_repo": tenant_repo,
        "usage_repo": usage_repo,
        "conversation_repo": conversation_repo,
        "profile_repo": profile_repo,
        "knowledge_repo": knowledge_repo,
        "audit_repo": audit_repo,
    }


def _make_service(repos: dict) -> TrialManagementService:
    return TrialManagementService(
        tenant_repo=repos["tenant_repo"],
        usage_repo=repos["usage_repo"],
        conversation_repo=repos["conversation_repo"],
        profile_repo=repos["profile_repo"],
        knowledge_repo=repos["knowledge_repo"],
        audit_repo=repos["audit_repo"],
    )


# ---------------------------------------------------------------------------
# MT-1009: Trial tenant provisioning
# ---------------------------------------------------------------------------


class TestTrialProvisioning:
    """MT-1009: Provision a new trial tenant with correct defaults."""

    @pytest.mark.asyncio
    async def test_provision_creates_trial_tenant(self):
        """provision_trial creates a tenant with TRIAL tier and ACTIVE status."""
        repos = _mock_repos()
        service = _make_service(repos)

        result = await service.provision_trial(
            customer_email="test@example.com",
            seed_demo_data=False,
        )

        assert result["tier"] == TenantTier.TRIAL.value
        assert result["status"] == TenantStatus.ACTIVE.value
        assert result["billing_channel"] == BillingChannel.TRIAL.value
        assert result["customer_email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_provision_sets_trial_limits(self):
        """Provisioned trial has 14-day expiry and 50 conversation limit."""
        repos = _mock_repos()
        service = _make_service(repos)

        result = await service.provision_trial(seed_demo_data=False)

        assert result["trial_conversation_limit"] == DEFAULT_TRIAL_CONVERSATION_LIMIT
        # Verify expiry is ~14 days from now
        expires_at = datetime.fromisoformat(result["trial_expires_at"])
        now = datetime.now(timezone.utc)
        days_until_expiry = (expires_at - now).total_seconds() / 86400
        assert 13.5 < days_until_expiry < 14.5

    @pytest.mark.asyncio
    async def test_provision_logs_audit_event(self):
        """Trial provisioning creates an audit trail entry."""
        repos = _mock_repos()
        service = _make_service(repos)

        await service.provision_trial(seed_demo_data=False)

        repos["audit_repo"].log_event.assert_called_once()
        call_kwargs = repos["audit_repo"].log_event.call_args
        assert call_kwargs.kwargs["event_type"] == AuditEventType.TENANT_PROVISIONED

    @pytest.mark.asyncio
    async def test_provision_sets_tier_rate_limits(self):
        """SPEC-1803: Trial tenant gets 300 RPM default from TIER_DEFAULTS."""
        repos = _mock_repos()
        service = _make_service(repos)

        result = await service.provision_trial(seed_demo_data=False)

        # SPEC-1803: rate_limit_rpm restored at 300 RPM
        assert result.get("rate_limit_rpm") == 300
        assert result.get("max_concurrent") is None


# ---------------------------------------------------------------------------
# MT-1010: Trial conversation consumption
# ---------------------------------------------------------------------------


class TestTrialConversationCap:
    """MT-1010: Trial conversation cap enforcement prevents overuse."""

    @pytest.mark.asyncio
    async def test_enforce_cap_allows_when_under_limit(self):
        """enforce_trial_cap returns True when conversations remain."""
        repos = _mock_repos()
        service = _make_service(repos)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=7)

        # Mock tenant is trial with 50 limit, 10 used
        repos["tenant_repo"].read = AsyncMock(return_value={
            "id": "t-trial-001",
            "tenant_id": "t-trial-001",
            "tier": TenantTier.TRIAL.value,
            "status": TenantStatus.ACTIVE.value,
            "trial_expires_at": expires.isoformat(),
            "trial_conversation_limit": 50,
        })

        # Mock conversation query returns count of 10 (SELECT VALUE COUNT(1))
        repos["conversation_repo"].query = AsyncMock(return_value=[10])

        allowed, status = await service.enforce_trial_cap("t-trial-001")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_enforce_cap_blocks_when_limit_reached(self):
        """enforce_trial_cap returns False when conversation limit hit."""
        repos = _mock_repos()
        service = _make_service(repos)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=7)

        repos["tenant_repo"].read = AsyncMock(return_value={
            "id": "t-trial-001",
            "tenant_id": "t-trial-001",
            "tier": TenantTier.TRIAL.value,
            "status": TenantStatus.ACTIVE.value,
            "trial_expires_at": expires.isoformat(),
            "trial_conversation_limit": 50,
        })

        # 50 conversations used = limit reached (SELECT VALUE COUNT(1))
        repos["conversation_repo"].query = AsyncMock(return_value=[50])

        allowed, status = await service.enforce_trial_cap("t-trial-001")
        assert allowed is False

    @pytest.mark.asyncio
    async def test_non_trial_tenant_bypasses_cap(self):
        """enforce_trial_cap returns True for non-trial (paid) tenants."""
        repos = _mock_repos()
        service = _make_service(repos)

        repos["tenant_repo"].read = AsyncMock(return_value={
            "id": "t-pro-001",
            "tenant_id": "t-pro-001",
            "tier": TenantTier.PROFESSIONAL.value,
            "status": TenantStatus.ACTIVE.value,
        })

        allowed, status = await service.enforce_trial_cap("t-pro-001")
        assert allowed is True


# ---------------------------------------------------------------------------
# MT-1011: Trial → paid conversion
# ---------------------------------------------------------------------------


class TestTrialConversion:
    """MT-1011: Trial tenant converts to paid tier preserving data."""

    @pytest.mark.asyncio
    async def test_convert_trial_to_professional(self):
        """convert_trial_to_paid upgrades tier and preserves data."""
        repos = _mock_repos()
        service = _make_service(repos)

        repos["tenant_repo"].read = AsyncMock(return_value={
            "id": "t-trial-convert",
            "tenant_id": "t-trial-convert",
            "tier": TenantTier.TRIAL.value,
            "status": TenantStatus.ACTIVE.value,
            "trial_expires_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "trial_conversation_limit": 50,
        })
        repos["tenant_repo"].patch = AsyncMock(return_value=None)
        repos["usage_repo"].query = AsyncMock(return_value=[{
            "tenant_id": "t-trial-convert",
            "total_conversations": 15,
        }])

        result = await service.convert_trial_to_paid(
            tenant_id="t-trial-convert",
            new_tier=TenantTier.PROFESSIONAL,
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_test123",
        )

        assert isinstance(result, TrialConversionResult)
        assert result.previous_tier == TenantTier.TRIAL.value
        assert result.new_tier == TenantTier.PROFESSIONAL.value
        assert result.data_preserved is True
        assert result.conversations_carried_over == 15

    @pytest.mark.asyncio
    async def test_convert_non_trial_raises_error(self):
        """convert_trial_to_paid raises ValueError for non-trial tenants."""
        repos = _mock_repos()
        service = _make_service(repos)

        repos["tenant_repo"].read = AsyncMock(return_value={
            "id": "t-pro-existing",
            "tenant_id": "t-pro-existing",
            "tier": TenantTier.PROFESSIONAL.value,
            "status": TenantStatus.ACTIVE.value,
        })

        with pytest.raises(ValueError, match="not a trial"):
            await service.convert_trial_to_paid(
                tenant_id="t-pro-existing",
                new_tier=TenantTier.ENTERPRISE,
                billing_channel=BillingChannel.STRIPE,
            )

    @pytest.mark.asyncio
    async def test_convert_not_found_raises_error(self):
        """convert_trial_to_paid raises ValueError for non-existent tenant."""
        repos = _mock_repos()
        service = _make_service(repos)

        repos["tenant_repo"].read = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.convert_trial_to_paid(
                tenant_id="t-nonexistent",
                new_tier=TenantTier.STARTER,
                billing_channel=BillingChannel.STRIPE,
            )


# ---------------------------------------------------------------------------
# MT-1012: Trial expiry scanning
# ---------------------------------------------------------------------------


class TestTrialExpiry:
    """MT-1012: Expired trials are detected and transitioned."""

    @pytest.mark.asyncio
    async def test_scan_detects_expired_trials(self):
        """scan_expired_trials transitions expired tenants to TRIAL_EXPIRED."""
        repos = _mock_repos()
        service = _make_service(repos)

        expired_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        active_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        repos["tenant_repo"].query = AsyncMock(return_value=[
            {
                "tenant_id": "t-expired-001",
                "tier": TenantTier.TRIAL.value,
                "status": TenantStatus.ACTIVE.value,
                "trial_expires_at": expired_time,
            },
            {
                "tenant_id": "t-active-002",
                "tier": TenantTier.TRIAL.value,
                "status": TenantStatus.ACTIVE.value,
                "trial_expires_at": active_time,
            },
        ])
        repos["tenant_repo"].patch = AsyncMock(return_value=None)

        result = await service.scan_expired_trials()

        assert isinstance(result, TrialScanResult)
        assert result.scanned_count == 2
        assert result.expired_count == 1
        assert "t-expired-001" in result.expired_tenant_ids

    @pytest.mark.asyncio
    async def test_scan_detects_expiring_soon(self):
        """scan_expired_trials counts tenants expiring within 3 days."""
        repos = _mock_repos()
        service = _make_service(repos)

        soon_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

        repos["tenant_repo"].query = AsyncMock(return_value=[
            {
                "tenant_id": "t-soon-001",
                "tier": TenantTier.TRIAL.value,
                "status": TenantStatus.ACTIVE.value,
                "trial_expires_at": soon_time,
            },
        ])

        result = await service.scan_expired_trials()

        assert result.expired_count == 0
        assert result.expiring_soon_count == 1


# ---------------------------------------------------------------------------
# MT-1013: Demo data seeding
# ---------------------------------------------------------------------------


class TestDemoDataSeeding:
    """MT-1013: Trial provisioning seeds demo conversations."""

    @pytest.mark.asyncio
    async def test_provision_with_demo_data(self):
        """provision_trial with seed_demo_data=True populates demo conversations."""
        repos = _mock_repos()
        service = _make_service(repos)

        # seed_demo_data calls conversation_repo.create for each demo conversation
        await service.provision_trial(
            customer_email="demo@example.com",
            seed_demo_data=True,
        )

        # Tenant should be created
        repos["tenant_repo"].create.assert_called_once()
        # Demo data should be seeded (conversation_repo.create called multiple times)
        assert repos["conversation_repo"].create.call_count >= 1

    def test_trial_model_is_cost_effective(self):
        """Trial tier uses GPT-4o-mini for cost containment."""
        assert TRIAL_MODEL == "gpt-4o-mini"

    def test_trial_model_routing(self):
        """get_trial_model returns model for TRIAL tier, None for paid."""
        model = TrialManagementService.get_trial_model(TenantTier.TRIAL)
        assert model == "gpt-4o-mini"

        model = TrialManagementService.get_trial_model(TenantTier.PROFESSIONAL)
        assert model is None

    def test_trial_constants(self):
        """Trial constants are set correctly."""
        assert DEFAULT_TRIAL_DURATION_DAYS == 14
        assert DEFAULT_TRIAL_CONVERSATION_LIMIT == 50
        assert TRIAL_EXPIRED_GRACE_DAYS == 30
        assert DEMO_CONVERSATION_COUNT == 5
