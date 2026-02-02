"""Deep tests for CustomerProfileService (customer_profile_service.py).

Tests CPD-01 through CPD-15 covering:
    - Shopify sync adapter (orders, cart, customer metadata)
    - Tier-aware layer availability and history depth
    - Consent management and status checks
    - Profile staleness and emptiness detection
    - Module singleton pattern

Uses mocked CustomerProfileRepository to avoid Cosmos DB dependency.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    CustomerProfileDocument,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.customer_profile_service import (
    CustomerProfileService,
    STALE_PROFILE_DAYS,
    get_profile_service,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_ID = "tenant-cpd-test"
CUSTOMER_ID = "cust-cpd-001"


def _make_profile(**overrides: Any) -> CustomerProfileDocument:
    """Create a CustomerProfileDocument with sensible defaults."""
    now = datetime.now(timezone.utc).isoformat()
    defaults: dict[str, Any] = {
        "id": f"{TENANT_ID}:{CUSTOMER_ID}",
        "tenant_id": TENANT_ID,
        "customer_id": CUSTOMER_ID,
        "consent_status": ConsentStatus.NOT_ASKED,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return CustomerProfileDocument(**defaults)


def _make_service(existing_profile: CustomerProfileDocument | None = None) -> tuple[
    CustomerProfileService, AsyncMock
]:
    """Create a configured service with a mocked repository.

    If *existing_profile* is provided, ``get_by_customer_id`` returns
    its ``model_dump()``; otherwise it returns ``None`` (triggering
    profile creation on ``get_or_create``).
    """
    repo = AsyncMock()
    if existing_profile is not None:
        repo.get_by_customer_id = AsyncMock(return_value=existing_profile.model_dump())
    else:
        repo.get_by_customer_id = AsyncMock(return_value=None)
    repo.upsert_profile = AsyncMock()

    svc = CustomerProfileService()
    svc.configure(profile_repo=repo)
    return svc, repo


# ---------------------------------------------------------------------------
# CPD-01: sync_from_shopify — orders mapped to purchase_history sorted DESC
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cpd_01_sync_shopify_orders_sorted_desc():
    """Orders from Shopify sync should be merged into purchase_history
    and sorted by date descending (most recent first)."""
    existing = _make_profile(purchase_history=[
        {"product_id": "OLD-1", "date": "2025-01-01"},
    ])
    svc, repo = _make_service(existing)

    shopify_data = {
        "orders": [
            {"product_id": "NEW-A", "date": "2026-01-15"},
            {"product_id": "NEW-B", "date": "2025-06-10"},
        ],
    }

    result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)

    dates = [p["date"] for p in result.purchase_history]
    assert dates == ["2026-01-15", "2025-06-10", "2025-01-01"]
    repo.upsert_profile.assert_awaited_once()


# ---------------------------------------------------------------------------
# CPD-02: sync_from_shopify — cart active/abandoned mapped
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cpd_02_sync_shopify_cart_active_abandoned():
    """Active and abandoned cart items should be written to cart_contents."""
    existing = _make_profile(cart_contents={"active": [], "abandoned": []})
    svc, repo = _make_service(existing)

    shopify_data = {
        "cart": {
            "active": [
                {"product_id": "PROD-1", "qty": 2},
                {"product_id": "PROD-2", "qty": 1},
            ],
            "abandoned": [
                {"product_id": "PROD-3", "qty": 1, "abandoned_at": "2026-01-10"},
            ],
        },
    }

    result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)

    assert len(result.cart_contents["active"]) == 2
    assert result.cart_contents["active"][0]["product_id"] == "PROD-1"
    assert len(result.cart_contents["abandoned"]) == 1
    assert result.cart_contents["abandoned"][0]["product_id"] == "PROD-3"


# ---------------------------------------------------------------------------
# CPD-03: sync_from_shopify — customer tags → marketing_segments,
#          country_code → region_codes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cpd_03_sync_shopify_customer_tags_and_region():
    """Customer tags should map to marketing_segments and country_code
    should map to region_codes.shipping_region."""
    existing = _make_profile()
    svc, repo = _make_service(existing)

    shopify_data = {
        "customer": {
            "country_code": "CA",
            "province_code": "ON",
            "locale": "fr-CA",
            "tags": ["vip", "wholesale", "returning"],
        },
    }

    result = await svc.sync_from_shopify(TENANT_ID, CUSTOMER_ID, shopify_data)

    assert result.marketing_segments == ["vip", "wholesale", "returning"]
    assert result.region_codes["shipping_region"] == "CA"
    assert result.region_codes["availability_zone"] == "ON"
    assert result.region_codes["locale"] == "fr-CA"


# ---------------------------------------------------------------------------
# CPD-04: get_available_layers — Starter returns [1, 2]
# ---------------------------------------------------------------------------


def test_cpd_04_available_layers_starter():
    """Starter tier should have memory layers [1, 2] per TIER_DEFAULTS."""
    layers = CustomerProfileService.get_available_layers(TenantTier.STARTER)
    assert layers == TIER_DEFAULTS[TenantTier.STARTER.value]["memory_layers"]
    assert layers == [1, 2]


# ---------------------------------------------------------------------------
# CPD-05: get_available_layers — Professional returns [1, 2, 3]
# ---------------------------------------------------------------------------


def test_cpd_05_available_layers_professional():
    """Professional tier should have memory layers [1, 2, 3]."""
    layers = CustomerProfileService.get_available_layers(TenantTier.PROFESSIONAL)
    assert layers == [1, 2, 3]


# ---------------------------------------------------------------------------
# CPD-06: get_available_layers — Enterprise returns [1, 2, 3, 4]
# ---------------------------------------------------------------------------


def test_cpd_06_available_layers_enterprise():
    """Enterprise tier should have all four memory layers."""
    layers = CustomerProfileService.get_available_layers(TenantTier.ENTERPRISE)
    assert layers == [1, 2, 3, 4]


# ---------------------------------------------------------------------------
# CPD-07: get_history_depth_days — Starter returns 90
# ---------------------------------------------------------------------------


def test_cpd_07_history_depth_starter():
    """Starter tier Layer 2 history should be 90 days."""
    depth = CustomerProfileService.get_history_depth_days(TenantTier.STARTER)
    assert depth == 90


# ---------------------------------------------------------------------------
# CPD-08: get_history_depth_days — Professional returns 365
# ---------------------------------------------------------------------------


def test_cpd_08_history_depth_professional():
    """Professional tier Layer 2 history should be 365 days."""
    depth = CustomerProfileService.get_history_depth_days(TenantTier.PROFESSIONAL)
    assert depth == 365


# ---------------------------------------------------------------------------
# CPD-09: get_history_depth_days — Enterprise returns None (unlimited)
# ---------------------------------------------------------------------------


def test_cpd_09_history_depth_enterprise():
    """Enterprise tier Layer 2 history should be unlimited (None)."""
    depth = CustomerProfileService.get_history_depth_days(TenantTier.ENTERPRISE)
    assert depth is None


# ---------------------------------------------------------------------------
# CPD-10: update_consent — GRANTED state persisted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cpd_10_update_consent_granted():
    """Updating consent to GRANTED should set consent_status on the profile."""
    existing = _make_profile(consent_status=ConsentStatus.NOT_ASKED)
    svc, repo = _make_service(existing)

    result = await svc.update_consent(TENANT_ID, CUSTOMER_ID, ConsentStatus.GRANTED)

    assert result.consent_status == ConsentStatus.GRANTED
    repo.upsert_profile.assert_awaited_once()


# ---------------------------------------------------------------------------
# CPD-11: is_consent_granted — True for GRANTED, False for DENIED
# ---------------------------------------------------------------------------


def test_cpd_11_consent_granted_vs_denied():
    """is_consent_granted should return True only for GRANTED status."""
    svc = CustomerProfileService()

    granted = _make_profile(consent_status=ConsentStatus.GRANTED)
    assert svc.is_consent_granted(granted) is True

    denied = _make_profile(consent_status=ConsentStatus.DENIED)
    assert svc.is_consent_granted(denied) is False


# ---------------------------------------------------------------------------
# CPD-12: is_consent_granted — False for NOT_ASKED
# ---------------------------------------------------------------------------


def test_cpd_12_consent_not_asked():
    """is_consent_granted should return False for NOT_ASKED status."""
    svc = CustomerProfileService()

    not_asked = _make_profile(consent_status=ConsentStatus.NOT_ASKED)
    assert svc.is_consent_granted(not_asked) is False


# ---------------------------------------------------------------------------
# CPD-13: is_stale — None last_interaction_at returns True
# ---------------------------------------------------------------------------


def test_cpd_13_stale_none_last_interaction():
    """A profile with no last_interaction_at should be considered stale."""
    svc = CustomerProfileService()

    profile = _make_profile(last_interaction_at=None)
    assert svc.is_stale(profile) is True

    # Also verify that a recent interaction is NOT stale
    recent = datetime.now(timezone.utc) - timedelta(days=10)
    fresh_profile = _make_profile(last_interaction_at=recent.isoformat())
    assert svc.is_stale(fresh_profile) is False

    # And an old interaction IS stale
    old = datetime.now(timezone.utc) - timedelta(days=STALE_PROFILE_DAYS + 1)
    stale_profile = _make_profile(last_interaction_at=old.isoformat())
    assert svc.is_stale(stale_profile) is True


# ---------------------------------------------------------------------------
# CPD-14: is_empty — all empty sources → True, one filled → False
# ---------------------------------------------------------------------------


def test_cpd_14_empty_profile_detection():
    """A profile with all empty data sources should be detected as empty;
    adding data to any single source should make it non-empty."""
    svc = CustomerProfileService()

    # Completely empty profile
    empty = _make_profile(
        purchase_history=[],
        product_questions=[],
        region_codes={},
        marketing_segments=[],
        jurisdiction_codes={},
        cart_contents={"active": [], "abandoned": []},
    )
    assert svc.is_empty(empty) is True

    # Profile with one purchase — not empty
    with_purchase = _make_profile(
        purchase_history=[{"product_id": "X", "date": "2026-01-01"}],
    )
    assert svc.is_empty(with_purchase) is False

    # Profile with only a region code — not empty
    with_region = _make_profile(
        region_codes={"shipping_region": "US"},
    )
    assert svc.is_empty(with_region) is False

    # Profile with only an active cart item — not empty
    with_cart = _make_profile(
        cart_contents={"active": [{"product_id": "Y", "qty": 1}], "abandoned": []},
    )
    assert svc.is_empty(with_cart) is False


# ---------------------------------------------------------------------------
# CPD-15: get_profile_service — singleton pattern
# ---------------------------------------------------------------------------


def test_cpd_15_singleton_pattern():
    """get_profile_service should return the same instance on repeated calls."""
    # Reset the module-level singleton to ensure clean state
    import src.multi_tenant.customer_profile_service as mod

    mod._service = None

    first = get_profile_service()
    second = get_profile_service()

    assert first is second
    assert isinstance(first, CustomerProfileService)

    # Clean up — reset singleton so other tests are not affected
    mod._service = None
