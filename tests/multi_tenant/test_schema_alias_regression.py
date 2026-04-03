"""Regression tests for schema alias wiring (S256 Batch 1 v3).

Verifies:
  1. TierGate.PROFESSIONAL is handled correctly by get_fields_for_tier
     (professional fields excluded from starter, included in professional).
  2. YAML validation.options is normalized to allowed_values for SELECT fields
     (invalid values rejected, valid values accepted).

Bug: registry.py gate_rank was missing TierGate.PROFESSIONAL, so professional-
gated fields leaked into starter exports. YAML validation.options was not mapped
to ValidationRule.allowed_values, so SELECT fields accepted any value.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md (Batch 1 schema alias)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.schema.models import TierGate
from src.multi_tenant.schema.registry import (
    get_field_registry,
    get_fields_for_tier,
    reset_field_registry,
)
from src.multi_tenant.schema.validation import validate_field


@pytest.fixture(autouse=True)
def fresh_registry():
    """Reset registry singleton before each test for isolation."""
    reset_field_registry()
    yield
    reset_field_registry()


# ── TierGate.PROFESSIONAL handling ────────────────────────────────

class TestTierGateProfessional:
    """Regression: TierGate.PROFESSIONAL must be respected by get_fields_for_tier."""

    def test_professional_field_excluded_from_starter(self):
        """Fields with tier_gate=professional must NOT appear at starter tier."""
        starter_fields = get_fields_for_tier(TenantTier.STARTER)

        assert "structured_blocks_enabled" not in starter_fields, (
            "structured_blocks_enabled (tier_gate=professional) leaked into starter"
        )

    def test_professional_field_included_in_professional(self):
        """Fields with tier_gate=professional must appear at professional tier."""
        pro_fields = get_fields_for_tier(TenantTier.PROFESSIONAL)

        assert "structured_blocks_enabled" in pro_fields

    def test_professional_field_included_in_enterprise(self):
        """Fields with tier_gate=professional must appear at enterprise tier."""
        ent_fields = get_fields_for_tier(TenantTier.ENTERPRISE)

        assert "structured_blocks_enabled" in ent_fields

    def test_gate_rank_covers_all_tier_gates(self):
        """Every TierGate enum value must appear in registry gate_rank."""
        # Exercise get_fields_for_tier for every tier — should not KeyError
        for tier in TenantTier:
            fields = get_fields_for_tier(tier)
            assert isinstance(fields, dict)

    def test_professional_field_validate_rejects_starter(self):
        """validate_field rejects professional field for starter tier."""
        is_valid, error, _ = validate_field(
            "structured_blocks_enabled", True, TenantTier.STARTER,
        )

        assert not is_valid
        assert "professional" in error.lower() or "tier" in error.lower()

    def test_professional_field_validate_accepts_professional(self):
        """validate_field accepts professional field for professional tier."""
        is_valid, error, sanitized = validate_field(
            "structured_blocks_enabled", True, TenantTier.PROFESSIONAL,
        )

        assert is_valid
        assert sanitized is True


# ── SELECT field validation.options → allowed_values ──────────────

class TestSelectFieldOptionsAlias:
    """Regression: YAML validation.options must be normalized to allowed_values."""

    def test_select_field_rejects_invalid_value(self):
        """SELECT field with validation.options rejects values not in options list."""
        is_valid, error, _ = validate_field(
            "widget_transcript_continuity", "bogus", TenantTier.PROFESSIONAL,
        )

        assert not is_valid
        assert "must be one of" in error

    def test_select_field_accepts_valid_value(self):
        """SELECT field with validation.options accepts valid option."""
        is_valid, error, sanitized = validate_field(
            "widget_transcript_continuity", "session", TenantTier.PROFESSIONAL,
        )

        assert is_valid
        assert sanitized == "session"

    def test_select_field_all_options_accepted(self):
        """All three options (none, session, persistent) are valid."""
        for value in ["none", "session", "persistent"]:
            is_valid, _, sanitized = validate_field(
                "widget_transcript_continuity", value, TenantTier.PROFESSIONAL,
            )
            assert is_valid, f"Expected '{value}' to be valid"
            assert sanitized == value

    def test_select_field_case_insensitive(self):
        """SELECT validation is case-insensitive (enum behavior WI-1493)."""
        is_valid, _, sanitized = validate_field(
            "widget_transcript_continuity", "SESSION", TenantTier.PROFESSIONAL,
        )

        assert is_valid
        # Returns canonical (lowercase) form
        assert sanitized == "session"

    def test_registry_loads_allowed_values(self):
        """Registry loads validation.options into ValidationRule.allowed_values."""
        registry = get_field_registry()
        field = registry["widget_transcript_continuity"]

        assert field.validation.allowed_values is not None
        assert set(field.validation.allowed_values) == {"none", "session", "persistent"}
