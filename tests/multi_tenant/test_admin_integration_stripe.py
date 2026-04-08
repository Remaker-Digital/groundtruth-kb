"""Tests for Stripe MCP integration in admin_integration_api.py.

Test IDs: AINT-01 → AINT-15

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


import pytest

from src.multi_tenant.admin_integration_api import (
    INTEGRATION_TYPES,
    StripeConnectionTestResult,
    StripeCredentialRequest,
    _INTEGRATION_META,
    _build_summary,
    _tier_meets_gate,
)


# ---------------------------------------------------------------------------
# AINT-01→AINT-03: Registry + metadata
# ---------------------------------------------------------------------------

class TestStripeRegistration:
    """Test Stripe entry in integration registry."""

    def test_aint_01_stripe_in_integration_types(self):
        """AINT-01: 'stripe' is in INTEGRATION_TYPES."""
        assert "stripe" in INTEGRATION_TYPES

    def test_aint_02_stripe_meta_fields(self):
        """AINT-02: Stripe metadata has all required fields."""
        meta = _INTEGRATION_META["stripe"]
        assert meta["name"] == "Stripe (MCP)"
        assert meta["icon"] == "stripe"
        assert meta["enable_field"] == "stripe_mcp_enabled"
        assert meta["status_field"] == "stripe_mcp_status"
        assert meta["tier_gate"] == "professional"
        assert meta["coming_soon"] is False
        assert len(meta["config_fields"]) >= 1

    def test_aint_03_stripe_config_field_keys(self):
        """AINT-03: Stripe config fields have correct keys."""
        meta = _INTEGRATION_META["stripe"]
        keys = {f["key"] for f in meta["config_fields"]}
        assert "stripe_mcp_enabled" in keys


# ---------------------------------------------------------------------------
# AINT-04→AINT-06: Tier gating
# ---------------------------------------------------------------------------

class TestStripeTierGating:
    """Test Stripe tier gate behavior."""

    def test_aint_04_professional_meets_gate(self):
        """AINT-04: Professional tier meets Stripe's gate."""
        assert _tier_meets_gate("professional", "professional") is True

    def test_aint_05_enterprise_meets_gate(self):
        """AINT-05: Enterprise tier meets Stripe's gate."""
        assert _tier_meets_gate("enterprise", "professional") is True

    def test_aint_06_starter_does_not_meet_gate(self):
        """AINT-06: Starter tier does NOT meet Stripe's gate."""
        assert _tier_meets_gate("starter", "professional") is False


# ---------------------------------------------------------------------------
# AINT-07→AINT-09: Integration summary building
# ---------------------------------------------------------------------------

class TestStripeSummary:
    """Test _build_summary for Stripe."""

    def test_aint_07_summary_enabled(self):
        """AINT-07: Build summary with Stripe enabled + connected."""
        config = {
            "stripe_mcp_enabled": True,
            "stripe_mcp_status": "connected",
        }
        summary = _build_summary(
            "stripe", _INTEGRATION_META["stripe"], config, "professional",
        )
        assert summary.type == "stripe"
        assert summary.name == "Stripe (MCP)"
        assert summary.enabled is True
        assert summary.status == "connected"
        assert summary.tier_met is True

    def test_aint_08_summary_disabled(self):
        """AINT-08: Build summary with Stripe disabled."""
        config = {
            "stripe_mcp_enabled": False,
            "stripe_mcp_status": None,
        }
        summary = _build_summary(
            "stripe", _INTEGRATION_META["stripe"], config, "professional",
        )
        assert summary.enabled is False
        assert summary.status is None

    def test_aint_09_summary_tier_not_met(self):
        """AINT-09: Build summary when tier doesn't meet gate."""
        config = {"stripe_mcp_enabled": False}
        summary = _build_summary(
            "stripe", _INTEGRATION_META["stripe"], config, "starter",
        )
        assert summary.tier_met is False
        assert summary.tier_gate == "professional"


# ---------------------------------------------------------------------------
# AINT-10→AINT-11: Request models
# ---------------------------------------------------------------------------

class TestStripeRequestModels:
    """Test Stripe-specific request models."""

    def test_aint_10_credential_request_valid(self):
        """AINT-10: StripeCredentialRequest accepts valid key."""
        req = StripeCredentialRequest(api_key="rk_live_abcdefghij")
        assert req.api_key == "rk_live_abcdefghij"

    def test_aint_11_credential_request_too_short(self):
        """AINT-11: StripeCredentialRequest rejects short key."""
        with pytest.raises(Exception):
            StripeCredentialRequest(api_key="short")


# ---------------------------------------------------------------------------
# AINT-12→AINT-13: Connection test result model
# ---------------------------------------------------------------------------

class TestStripeConnectionTestResult:
    """Test StripeConnectionTestResult model."""

    def test_aint_12_success_result(self):
        """AINT-12: Connection test success result."""
        result = StripeConnectionTestResult(
            success=True,
            tool_count=15,
            tools=["list_invoices", "get_customer"],
            elapsed_ms=234.5,
        )
        assert result.success is True
        assert result.tool_count == 15
        assert len(result.tools) == 2
        assert result.error is None

    def test_aint_13_failure_result(self):
        """AINT-13: Connection test failure result."""
        result = StripeConnectionTestResult(
            success=False,
            error="Authentication failed",
            elapsed_ms=50.0,
        )
        assert result.success is False
        assert result.error == "Authentication failed"
        assert result.tool_count == 0


# ---------------------------------------------------------------------------
# AINT-14→AINT-15: Integration count
# ---------------------------------------------------------------------------

class TestIntegrationCount:
    """Test total integration count."""

    def test_aint_14_five_integrations(self):
        """AINT-14: Integration registry has 5 entries (including Stripe)."""
        assert len(_INTEGRATION_META) == 5
        assert len(INTEGRATION_TYPES) == 5

    def test_aint_15_stripe_not_coming_soon(self):
        """AINT-15: Stripe is NOT marked as coming_soon."""
        meta = _INTEGRATION_META["stripe"]
        assert meta["coming_soon"] is False
