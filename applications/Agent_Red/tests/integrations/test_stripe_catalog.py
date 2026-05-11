"""P0 Stripe Catalog Model tests — §4.7 of COMPREHENSIVE-TEST-PLAN.md.

Test IDs: SC-01 through SC-05.

Validates:
    - StripeCatalog loads and parses config/stripe_product_ids.json
    - All 3 tier product IDs, monthly price IDs, annual price IDs present
    - Pack price IDs present (1K, 5K, 20K)
    - Tier lookup helpers and add-on validation
    - TierCatalog.price_id_for_interval() routing

Uses the actual catalog file (config/stripe_product_ids.json) — no mocking needed.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.integrations.stripe_catalog import (
    AddonCatalog,
    StripeCatalog,
    TierCatalog,
    load_catalog,
)


# ---------------------------------------------------------------------------
# Fixture: fresh catalog instance (bypass lru_cache)
# ---------------------------------------------------------------------------

@pytest.fixture
def catalog() -> StripeCatalog:
    """Load the Stripe catalog from the real config file."""
    # Clear lru_cache to ensure a fresh load each test run
    load_catalog.cache_clear()
    return load_catalog()


# ===================================================================
# SC-01: StripeCatalog loads from stripe_product_ids.json
# ===================================================================


class TestCatalogLoading:
    """SC-01: Catalog loads and parses correctly."""

    @pytest.mark.unit
    def test_catalog_loads_successfully(self, catalog):
        """SC-01: StripeCatalog loads from config/stripe_product_ids.json."""
        assert isinstance(catalog, StripeCatalog)
        assert catalog.mode == "test"
        assert catalog.meter_id.startswith("mtr_")
        assert catalog.coupon_id == "annual_17pct_off"

    @pytest.mark.unit
    def test_catalog_has_three_tiers(self, catalog):
        """SC-01 supplement: Catalog contains exactly 3 tiers."""
        assert len(catalog.tiers) == 3
        assert set(catalog.tiers.keys()) == {"starter", "professional", "enterprise"}

    @pytest.mark.unit
    def test_catalog_has_three_packs(self, catalog):
        """SC-01 supplement: Catalog contains exactly 3 packs."""
        assert len(catalog.packs) == 3
        assert set(catalog.packs.keys()) == {"pack_1k", "pack_5k", "pack_20k"}

    @pytest.mark.unit
    def test_catalog_has_seven_addons(self, catalog):
        """SC-01 supplement: Catalog contains 7 add-ons."""
        assert len(catalog.addons) == 7


# ===================================================================
# SC-02: All 3 tier product IDs present
# ===================================================================


class TestTierProductIDs:
    """SC-02: All tier product IDs are valid Stripe product IDs."""

    @pytest.mark.unit
    def test_all_tier_product_ids_present(self, catalog):
        """SC-02: All 3 tiers have product_id starting with prod_."""
        for tier_name in ("starter", "professional", "enterprise"):
            tier = catalog.tiers[tier_name]
            assert tier.product_id.startswith("prod_"), (
                f"{tier_name} product_id missing or malformed: {tier.product_id}"
            )

    @pytest.mark.unit
    def test_included_conversations_match_pricing(self, catalog):
        """SC-02 supplement: Included conversations match pricing tiers."""
        assert catalog.tiers["starter"].included_conversations == 1_000
        assert catalog.tiers["professional"].included_conversations == 5_000
        assert catalog.tiers["enterprise"].included_conversations == 20_000


# ===================================================================
# SC-03: All 3 tier monthly price IDs present
# ===================================================================


class TestTierMonthlyPriceIDs:
    """SC-03: Monthly price IDs present for all tiers."""

    @pytest.mark.unit
    def test_all_tier_monthly_prices_present(self, catalog):
        """SC-03: All 3 tiers have monthly_price_id starting with price_."""
        for tier_name in ("starter", "professional", "enterprise"):
            tier = catalog.tiers[tier_name]
            assert tier.monthly_price_id.startswith("price_"), (
                f"{tier_name} monthly_price_id missing or malformed"
            )

    @pytest.mark.unit
    def test_price_id_for_interval_month(self, catalog):
        """SC-03 supplement: price_id_for_interval('month') returns monthly."""
        tier = catalog.tiers["starter"]
        assert tier.price_id_for_interval("month") == tier.monthly_price_id


# ===================================================================
# SC-04: All 3 tier annual price IDs present
# ===================================================================


class TestTierAnnualPriceIDs:
    """SC-04: Annual price IDs present for all tiers."""

    @pytest.mark.unit
    def test_all_tier_annual_prices_present(self, catalog):
        """SC-04: All 3 tiers have annual_price_id starting with price_."""
        for tier_name in ("starter", "professional", "enterprise"):
            tier = catalog.tiers[tier_name]
            assert tier.annual_price_id.startswith("price_"), (
                f"{tier_name} annual_price_id missing or malformed"
            )

    @pytest.mark.unit
    def test_price_id_for_interval_year(self, catalog):
        """SC-04 supplement: price_id_for_interval('year') returns annual."""
        tier = catalog.tiers["starter"]
        assert tier.price_id_for_interval("year") == tier.annual_price_id


# ===================================================================
# SC-05: Pack price IDs present
# ===================================================================


class TestPackPriceIDs:
    """SC-05: Pack price IDs present for all 3 packs."""

    @pytest.mark.unit
    def test_all_pack_price_ids_present(self, catalog):
        """SC-05: All 3 packs have price_id starting with price_."""
        for pack_name in ("pack_1k", "pack_5k", "pack_20k"):
            pack = catalog.packs[pack_name]
            assert pack.price_id.startswith("price_"), (
                f"{pack_name} price_id missing or malformed"
            )

    @pytest.mark.unit
    def test_pack_conversation_counts(self, catalog):
        """SC-05 supplement: Pack conversation counts match catalog."""
        assert catalog.packs["pack_1k"].conversations == 1_000
        assert catalog.packs["pack_5k"].conversations == 5_000
        assert catalog.packs["pack_20k"].conversations == 20_000

    @pytest.mark.unit
    def test_all_pack_product_ids_present(self, catalog):
        """SC-05 supplement: All packs have product_id."""
        for pack_name in ("pack_1k", "pack_5k", "pack_20k"):
            pack = catalog.packs[pack_name]
            assert pack.product_id.startswith("prod_"), (
                f"{pack_name} product_id missing or malformed"
            )


# ===================================================================
# Supplementary: Catalog helper methods
# ===================================================================


class TestCatalogHelpers:
    """Catalog convenience methods — get_tier, get_addon, validate_addon_for_tier."""

    @pytest.mark.unit
    def test_get_tier_valid(self, catalog):
        """get_tier() returns TierCatalog for known tier."""
        tier = catalog.get_tier("starter")
        assert isinstance(tier, TierCatalog)
        assert tier.included_conversations == 1_000

    @pytest.mark.unit
    def test_get_tier_invalid(self, catalog):
        """get_tier() raises ValueError for unknown tier."""
        with pytest.raises(ValueError, match="Unknown tier"):
            catalog.get_tier("platinum")

    @pytest.mark.unit
    def test_get_addon_valid(self, catalog):
        """get_addon() returns AddonCatalog for known add-on."""
        addon = catalog.get_addon("addon_multi_language")
        assert isinstance(addon, AddonCatalog)
        assert "starter" in addon.available_on

    @pytest.mark.unit
    def test_get_addon_invalid(self, catalog):
        """get_addon() raises ValueError for unknown add-on."""
        with pytest.raises(ValueError, match="Unknown add-on"):
            catalog.get_addon("addon_nonexistent")

    @pytest.mark.unit
    def test_validate_addon_for_tier_allowed(self, catalog):
        """validate_addon_for_tier() passes for valid tier/addon combo."""
        catalog.validate_addon_for_tier("addon_multi_language", "starter")

    @pytest.mark.unit
    def test_validate_addon_for_tier_rejected(self, catalog):
        """validate_addon_for_tier() raises for tier not in available_on."""
        with pytest.raises(ValueError, match="not available on tier"):
            catalog.validate_addon_for_tier("addon_white_label", "starter")

    @pytest.mark.unit
    def test_addon_availability_enterprise_only(self, catalog):
        """White-label and custom integration are enterprise-only."""
        wl = catalog.get_addon("addon_white_label")
        assert wl.available_on == ["enterprise"]
        ci = catalog.get_addon("addon_custom_integration")
        assert ci.available_on == ["enterprise"]

    @pytest.mark.unit
    def test_valid_tiers_constant(self):
        """VALID_TIERS class var matches expected set."""
        assert StripeCatalog.VALID_TIERS == frozenset({"starter", "professional", "enterprise"})

    @pytest.mark.unit
    def test_valid_intervals_constant(self):
        """VALID_INTERVALS class var matches expected set."""
        assert StripeCatalog.VALID_INTERVALS == frozenset({"month", "year"})

    @pytest.mark.unit
    def test_overage_price_ids_present(self, catalog):
        """All tiers have overage_price_id for Stripe Billing Meter."""
        for tier_name in ("starter", "professional", "enterprise"):
            tier = catalog.tiers[tier_name]
            assert tier.overage_price_id.startswith("price_"), (
                f"{tier_name} overage_price_id missing or malformed"
            )
