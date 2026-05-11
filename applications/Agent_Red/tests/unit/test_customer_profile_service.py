"""
Tests for CustomerProfileService — Layer 1 customer context management.

Covers:
    - Profile CRUD (get_profile, get_or_create, delete_profile)
    - Data source updates (purchases, questions, regions, segments,
      jurisdiction, cart contents)
    - Identity extraction from text (extract_identity_from_text)
    - extract_and_store_identity pipeline
    - Shopify sync adapter (sync_from_shopify)
    - Profile freshness (is_stale, is_empty)
    - Consent management (update_consent, is_consent_granted)
    - Tier-aware utilities (get_available_layers, get_history_depth_days)
    - record_interaction
    - Singleton (get_profile_service)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    CustomerProfileDocument,
    TenantTier,
)
from src.multi_tenant.customer_profile_service import (
    CustomerProfileService,
    MAX_CART_ITEMS,
    MAX_MARKETING_SEGMENTS,
    MAX_PURCHASE_HISTORY,
    STALE_PROFILE_DAYS,
    extract_identity_from_text,
    get_profile_service,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "tenant-test-001"
CUSTOMER_ID = "cust-abc-123"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_profile(**overrides) -> CustomerProfileDocument:
    """Create a test CustomerProfileDocument."""
    defaults = dict(
        id=f"{TENANT_ID}:{CUSTOMER_ID}",
        tenant_id=TENANT_ID,
        customer_id=CUSTOMER_ID,
        consent_status=ConsentStatus.NOT_ASKED,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    defaults.update(overrides)
    return CustomerProfileDocument(**defaults)


def _make_repo(profile_doc: dict | None = None):
    """Create a mock profile repository."""
    repo = MagicMock()
    repo.get_by_customer_id = AsyncMock(return_value=profile_doc)
    repo.upsert_profile = AsyncMock()
    repo.delete = AsyncMock()
    repo.update_last_interaction = AsyncMock()
    return repo


def _make_service(profile_doc: dict | None = None):
    """Create a configured CustomerProfileService."""
    svc = CustomerProfileService()
    repo = _make_repo(profile_doc)
    svc.configure(profile_repo=repo)
    return svc, repo


# ---------------------------------------------------------------------------
# extract_identity_from_text
# ---------------------------------------------------------------------------


class TestExtractIdentityFromText:
    """Tests for the standalone identity extraction function."""

    def test_extract_name_my_name_is(self):
        result = extract_identity_from_text("Hi, my name is John Smith")
        assert result.get("name") == "John Smith"

    def test_extract_name_im(self):
        result = extract_identity_from_text("I'm Sarah")
        assert result.get("name") == "Sarah"

    def test_extract_name_this_is(self):
        result = extract_identity_from_text("This is Mike Johnson")
        assert result.get("name") == "Mike Johnson"

    def test_extract_name_call_me(self):
        result = extract_identity_from_text("Please call me Alex")
        assert result.get("name") == "Alex"

    def test_extract_name_name_colon(self):
        result = extract_identity_from_text("Name: Lisa")
        assert result.get("name") == "Lisa"

    def test_reject_single_common_word(self):
        # "I'm Sorry." — "Sorry" is captured alone (period ends the word match)
        result = extract_identity_from_text("I'm Sorry.")
        assert "name" not in result

    def test_reject_too_short_name(self):
        result = extract_identity_from_text("My name is A")
        assert "name" not in result

    def test_extract_email(self):
        result = extract_identity_from_text("My email is john@example.com")
        assert result.get("email") == "john@example.com"

    def test_extract_both(self):
        result = extract_identity_from_text(
            "My name is Sarah Jones and my email is sarah@test.com"
        )
        assert result.get("name") == "Sarah Jones"
        assert result.get("email") == "sarah@test.com"

    def test_no_identity(self):
        result = extract_identity_from_text("What time does the store close?")
        assert result == {}

    def test_reject_single_word_back(self):
        # "I'm Back!" — "Back" captured alone (punctuation stops match), in reject list
        result = extract_identity_from_text("I'm Back!")
        assert "name" not in result

    # -- D3 strict E.164 phone extraction (SPEC-1879 Phase 2A remediation) ----

    def test_phone_valid_e164(self):
        result = extract_identity_from_text("my phone is +15551234567")
        assert result.get("phone") == "+15551234567"

    def test_phone_overlong_rejected(self):
        """Overlong digit string must not be truncated."""
        result = extract_identity_from_text("my phone is +155512345678901234")
        assert "phone" not in result

    def test_phone_trailing_alpha_rejected(self):
        """Trailing alpha must not be silently stripped."""
        result = extract_identity_from_text("my phone is +15551234567abc")
        assert "phone" not in result

    def test_phone_embedded_word_rejected(self):
        """Phone embedded in a word must be rejected."""
        result = extract_identity_from_text("call+15551234567now")
        assert "phone" not in result


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------


class TestProfileCRUD:
    """Tests for get_profile, get_or_create, delete_profile."""

    @pytest.mark.asyncio
    async def test_get_profile_found(self):
        profile_dict = _make_profile().model_dump()
        svc, _ = _make_service(profile_doc=profile_dict)
        result = await svc.get_profile(TENANT_ID, CUSTOMER_ID)
        assert result is not None
        assert result.customer_id == CUSTOMER_ID

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self):
        svc, _ = _make_service(profile_doc=None)
        result = await svc.get_profile(TENANT_ID, CUSTOMER_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_profile_unconfigured(self):
        svc = CustomerProfileService()
        result = await svc.get_profile(TENANT_ID, CUSTOMER_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_or_create_existing(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.get_or_create(TENANT_ID, CUSTOMER_ID)
        assert result.customer_id == CUSTOMER_ID
        # Should NOT create
        repo.upsert_profile.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_or_create_new(self):
        svc, repo = _make_service(profile_doc=None)
        result = await svc.get_or_create(TENANT_ID, CUSTOMER_ID)
        assert result.customer_id == CUSTOMER_ID
        assert result.consent_status == ConsentStatus.NOT_ASKED
        repo.upsert_profile.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_or_create_unconfigured_returns_profile(self):
        """Even unconfigured, get_or_create returns an in-memory profile."""
        svc = CustomerProfileService()
        # get_profile returns None (unconfigured), so it creates one in-memory
        result = await svc.get_or_create(TENANT_ID, CUSTOMER_ID)
        assert result.customer_id == CUSTOMER_ID

    @pytest.mark.asyncio
    async def test_delete_profile_success(self):
        svc, repo = _make_service()
        result = await svc.delete_profile(TENANT_ID, CUSTOMER_ID)
        assert result is True
        repo.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self):
        svc, repo = _make_service()
        repo.delete = AsyncMock(side_effect=Exception("Not found"))
        result = await svc.delete_profile(TENANT_ID, CUSTOMER_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_profile_unconfigured(self):
        svc = CustomerProfileService()
        result = await svc.delete_profile(TENANT_ID, CUSTOMER_ID)
        assert result is False


# ---------------------------------------------------------------------------
# Data source updates
# ---------------------------------------------------------------------------


class TestDataSourceUpdates:
    """Tests for update_purchase_history, update_product_questions, etc."""

    @pytest.mark.asyncio
    async def test_update_purchase_history(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        purchases = [{"product_id": "prod-1", "date": "2026-01-15"}]
        result = await svc.update_purchase_history(TENANT_ID, CUSTOMER_ID, purchases)
        assert len(result.purchase_history) == 1
        repo.upsert_profile.assert_awaited()

    @pytest.mark.asyncio
    async def test_purchase_history_capped(self):
        profile_dict = _make_profile(
            purchase_history=[{"product_id": f"p{i}", "date": f"2025-{i:02d}-01"} for i in range(1, 50)],
        ).model_dump()
        svc, _ = _make_service(profile_doc=profile_dict)
        new_purchases = [{"product_id": f"new-{i}", "date": "2026-02-01"} for i in range(10)]
        result = await svc.update_purchase_history(TENANT_ID, CUSTOMER_ID, new_purchases)
        assert len(result.purchase_history) <= MAX_PURCHASE_HISTORY

    @pytest.mark.asyncio
    async def test_update_product_questions(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        questions = [{"question": "Does it come in blue?", "product_id": "p1", "date": "2026-01-15"}]
        result = await svc.update_product_questions(TENANT_ID, CUSTOMER_ID, questions)
        assert len(result.product_questions) == 1
        repo.upsert_profile.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_region_codes(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_region_codes(
            TENANT_ID, CUSTOMER_ID,
            {"shipping_region": "US", "locale": "en-US"},
        )
        assert result.region_codes["shipping_region"] == "US"
        assert result.region_codes["locale"] == "en-US"

    @pytest.mark.asyncio
    async def test_update_marketing_segments(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_marketing_segments(
            TENANT_ID, CUSTOMER_ID, ["vip", "repeat-buyer"],
        )
        assert result.marketing_segments == ["vip", "repeat-buyer"]

    @pytest.mark.asyncio
    async def test_marketing_segments_capped(self):
        profile_dict = _make_profile().model_dump()
        svc, _ = _make_service(profile_doc=profile_dict)
        segments = [f"seg-{i}" for i in range(30)]
        result = await svc.update_marketing_segments(TENANT_ID, CUSTOMER_ID, segments)
        assert len(result.marketing_segments) <= MAX_MARKETING_SEGMENTS

    @pytest.mark.asyncio
    async def test_update_jurisdiction_codes(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_jurisdiction_codes(
            TENANT_ID, CUSTOMER_ID,
            {"country": "US", "state": "CA"},
        )
        assert result.jurisdiction_codes["country"] == "US"
        assert result.jurisdiction_codes["state"] == "CA"

    @pytest.mark.asyncio
    async def test_update_cart_contents_active(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_cart_contents(
            TENANT_ID, CUSTOMER_ID,
            active_cart=[{"product_id": "p1", "qty": 2}],
        )
        assert len(result.cart_contents["active"]) == 1

    @pytest.mark.asyncio
    async def test_update_cart_contents_abandoned(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_cart_contents(
            TENANT_ID, CUSTOMER_ID,
            abandoned_cart=[{"product_id": "p2", "qty": 1, "abandoned_at": "2026-01-01"}],
        )
        assert len(result.cart_contents["abandoned"]) == 1

    @pytest.mark.asyncio
    async def test_update_cart_contents_capped(self):
        profile_dict = _make_profile().model_dump()
        svc, _ = _make_service(profile_doc=profile_dict)
        big_cart = [{"product_id": f"p{i}", "qty": 1} for i in range(30)]
        result = await svc.update_cart_contents(TENANT_ID, CUSTOMER_ID, active_cart=big_cart)
        assert len(result.cart_contents["active"]) <= MAX_CART_ITEMS


# ---------------------------------------------------------------------------
# record_interaction
# ---------------------------------------------------------------------------


class TestRecordInteraction:
    """Tests for record_interaction."""

    @pytest.mark.asyncio
    async def test_record_interaction_success(self):
        svc, repo = _make_service()
        await svc.record_interaction(TENANT_ID, CUSTOMER_ID)
        repo.update_last_interaction.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_record_interaction_failure_non_fatal(self):
        svc, repo = _make_service()
        repo.update_last_interaction = AsyncMock(side_effect=Exception("DB error"))
        # Should not raise
        await svc.record_interaction(TENANT_ID, CUSTOMER_ID)

    @pytest.mark.asyncio
    async def test_record_interaction_unconfigured(self):
        svc = CustomerProfileService()
        # Should not raise
        await svc.record_interaction(TENANT_ID, CUSTOMER_ID)


# ---------------------------------------------------------------------------
# extract_and_store_identity
# ---------------------------------------------------------------------------


class TestExtractAndStoreIdentity:
    """Tests for extract_and_store_identity pipeline."""

    @pytest.mark.asyncio
    async def test_extract_and_store_name(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "My name is John Smith",
        )
        assert result is not None
        assert result["name"] == "John Smith"
        repo.upsert_profile.assert_awaited()

    @pytest.mark.asyncio
    async def test_extract_no_identity(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "What are your store hours?",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_does_not_overwrite_shorter_name(self):
        """If existing name is longer, don't overwrite with a shorter one."""
        profile_dict = _make_profile(
            asserted_identity={"name": "Jonathan Smith"},
        ).model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "Call me John",
        )
        # "John" (4 chars) < "Jonathan Smith" (14 chars), should not update
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_overwrites_with_longer_name(self):
        profile_dict = _make_profile(
            asserted_identity={"name": "John"},
        ).model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "My name is John Smith",
        )
        assert result is not None
        assert result["name"] == "John Smith"

    @pytest.mark.asyncio
    async def test_extract_does_not_overwrite_email(self):
        profile_dict = _make_profile(
            asserted_identity={"email": "old@test.com"},
        ).model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "Email me at new@test.com",
        )
        # Existing email should not be overwritten
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_error_returns_none(self):
        svc, repo = _make_service(profile_doc=None)
        repo.upsert_profile = AsyncMock(side_effect=Exception("DB error"))
        result = await svc.extract_and_store_identity(
            TENANT_ID, CUSTOMER_ID, "My name is Error Case",
        )
        # Error is caught and returns None
        assert result is None


# ---------------------------------------------------------------------------
# Shopify sync
# ---------------------------------------------------------------------------


class TestSyncFromShopify:
    """Tests for sync_from_shopify."""

    @pytest.mark.asyncio
    async def test_sync_orders(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        shopify_data = {
            "orders": [{"product_id": "p1", "date": "2026-01-15"}],
        }
        result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)
        assert len(result.purchase_history) == 1
        repo.upsert_profile.assert_awaited()

    @pytest.mark.asyncio
    async def test_sync_cart(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        shopify_data = {
            "cart": {
                "active": [{"product_id": "p1", "qty": 2}],
                "abandoned": [{"product_id": "p2", "qty": 1}],
            },
        }
        result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)
        assert len(result.cart_contents["active"]) == 1
        assert len(result.cart_contents["abandoned"]) == 1

    @pytest.mark.asyncio
    async def test_sync_customer_metadata(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        shopify_data = {
            "customer": {
                "country_code": "US",
                "province_code": "CA",
                "locale": "en-US",
                "tags": ["vip", "repeat"],
            },
        }
        result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)
        assert result.region_codes["shipping_region"] == "US"
        assert result.region_codes["availability_zone"] == "CA"
        assert result.region_codes["locale"] == "en-US"
        assert result.marketing_segments == ["vip", "repeat"]

    @pytest.mark.asyncio
    async def test_sync_no_changes(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        # Empty shopify_data — no sections to sync
        await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, {})
        # upsert should NOT be called when nothing changed
        repo.upsert_profile.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sync_empty_orders(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        shopify_data = {"orders": []}
        await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)
        # Empty orders list should not trigger upsert
        repo.upsert_profile.assert_not_awaited()


# ---------------------------------------------------------------------------
# Freshness & emptiness
# ---------------------------------------------------------------------------


class TestProfileFreshness:
    """Tests for is_stale and is_empty."""

    def test_stale_no_interaction(self):
        svc = CustomerProfileService()
        profile = _make_profile(last_interaction_at=None)
        assert svc.is_stale(profile) is True

    def test_stale_old_interaction(self):
        svc = CustomerProfileService()
        old_date = (datetime.now(timezone.utc) - timedelta(days=STALE_PROFILE_DAYS + 1)).isoformat()
        profile = _make_profile(last_interaction_at=old_date)
        assert svc.is_stale(profile) is True

    def test_fresh_recent_interaction(self):
        svc = CustomerProfileService()
        recent = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        profile = _make_profile(last_interaction_at=recent)
        assert svc.is_stale(profile) is False

    def test_stale_invalid_date(self):
        svc = CustomerProfileService()
        profile = _make_profile(last_interaction_at="not-a-date")
        assert svc.is_stale(profile) is True

    def test_stale_custom_threshold(self):
        svc = CustomerProfileService()
        recent = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        profile = _make_profile(last_interaction_at=recent)
        assert svc.is_stale(profile, threshold_days=3) is True
        assert svc.is_stale(profile, threshold_days=10) is False

    def test_empty_profile(self):
        svc = CustomerProfileService()
        profile = _make_profile()
        assert svc.is_empty(profile) is True

    def test_non_empty_with_purchases(self):
        svc = CustomerProfileService()
        profile = _make_profile(purchase_history=[{"product_id": "p1"}])
        assert svc.is_empty(profile) is False

    def test_non_empty_with_questions(self):
        svc = CustomerProfileService()
        profile = _make_profile(product_questions=[{"question": "test?"}])
        assert svc.is_empty(profile) is False

    def test_non_empty_with_region(self):
        svc = CustomerProfileService()
        profile = _make_profile(region_codes={"shipping_region": "US"})
        assert svc.is_empty(profile) is False

    def test_non_empty_with_segments(self):
        svc = CustomerProfileService()
        profile = _make_profile(marketing_segments=["vip"])
        assert svc.is_empty(profile) is False

    def test_non_empty_with_jurisdiction(self):
        svc = CustomerProfileService()
        profile = _make_profile(jurisdiction_codes={"country": "US"})
        assert svc.is_empty(profile) is False

    def test_non_empty_with_active_cart(self):
        svc = CustomerProfileService()
        profile = _make_profile(cart_contents={"active": [{"product_id": "p1"}]})
        assert svc.is_empty(profile) is False

    def test_non_empty_with_abandoned_cart(self):
        svc = CustomerProfileService()
        profile = _make_profile(cart_contents={"abandoned": [{"product_id": "p2"}]})
        assert svc.is_empty(profile) is False


# ---------------------------------------------------------------------------
# Consent management
# ---------------------------------------------------------------------------


class TestConsentManagement:
    """Tests for update_consent and is_consent_granted."""

    @pytest.mark.asyncio
    async def test_update_consent_granted(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_consent(TENANT_ID, CUSTOMER_ID, ConsentStatus.GRANTED)
        assert result.consent_status == ConsentStatus.GRANTED
        repo.upsert_profile.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_consent_denied(self):
        profile_dict = _make_profile().model_dump()
        svc, repo = _make_service(profile_doc=profile_dict)
        result = await svc.update_consent(TENANT_ID, CUSTOMER_ID, ConsentStatus.DENIED)
        assert result.consent_status == ConsentStatus.DENIED

    def test_is_consent_granted_true(self):
        svc = CustomerProfileService()
        profile = _make_profile(consent_status=ConsentStatus.GRANTED)
        assert svc.is_consent_granted(profile) is True

    def test_is_consent_granted_false(self):
        svc = CustomerProfileService()
        profile = _make_profile(consent_status=ConsentStatus.NOT_ASKED)
        assert svc.is_consent_granted(profile) is False

    def test_is_consent_granted_denied(self):
        svc = CustomerProfileService()
        profile = _make_profile(consent_status=ConsentStatus.DENIED)
        assert svc.is_consent_granted(profile) is False


# ---------------------------------------------------------------------------
# Tier utilities
# ---------------------------------------------------------------------------


class TestTierUtilities:
    """Tests for get_available_layers and get_history_depth_days."""

    def test_trial_layers(self):
        # Trial now has professional-level entitlements: layers [1, 2, 3]
        layers = CustomerProfileService.get_available_layers(TenantTier.TRIAL)
        assert 1 in layers
        assert 2 in layers
        assert 3 in layers
        assert len(layers) == 3

    def test_starter_layers(self):
        layers = CustomerProfileService.get_available_layers(TenantTier.STARTER)
        assert 1 in layers
        assert 2 in layers

    def test_professional_layers(self):
        layers = CustomerProfileService.get_available_layers(TenantTier.PROFESSIONAL)
        assert 3 in layers

    def test_enterprise_layers(self):
        layers = CustomerProfileService.get_available_layers(TenantTier.ENTERPRISE)
        assert 4 in layers

    def test_trial_history_depth(self):
        # history_depth_days removed from TIER_DEFAULTS; falls back to 90
        days = CustomerProfileService.get_history_depth_days(TenantTier.TRIAL)
        assert days == 90

    def test_starter_history_depth(self):
        days = CustomerProfileService.get_history_depth_days(TenantTier.STARTER)
        assert days == 90

    def test_enterprise_history_depth(self):
        # history_depth_days removed from TIER_DEFAULTS; falls back to 90
        days = CustomerProfileService.get_history_depth_days(TenantTier.ENTERPRISE)
        assert days == 90


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestGetProfileService:
    """Tests for get_profile_service singleton."""

    def test_returns_instance(self):
        import src.multi_tenant.customer_profile_service as mod
        old = mod._service
        try:
            mod._service = None
            svc = get_profile_service()
            assert isinstance(svc, CustomerProfileService)
        finally:
            mod._service = old

    def test_returns_same_instance(self):
        import src.multi_tenant.customer_profile_service as mod
        old = mod._service
        try:
            mod._service = None
            a = get_profile_service()
            b = get_profile_service()
            assert a is b
        finally:
            mod._service = old
