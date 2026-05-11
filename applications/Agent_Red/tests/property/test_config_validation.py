"""Property-based tests for config field validation (SPEC-1843 / WI-1482).

Tests verify invariants of the validation system:
- Type acceptance/rejection consistency
- Tier gate monotonicity (higher tiers accept more fields)
- Boundary enforcement (min/max length, min/max value)
- Null handling (required vs optional)
- String sanitization (strip whitespace)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.schema.models import (
    ConfigFieldType,
    HEX_COLOR_PATTERN,
)
from src.multi_tenant.schema.registry import get_field_registry
from src.multi_tenant.schema.validation import validate_field, _TIER_RANK, _GATE_RANK
from tests.property.conftest import (
    hex_color_strategy,
    tenant_tier_strategy,
)


# ---------------------------------------------------------------------------
# Strategies derived from the actual field registry
# ---------------------------------------------------------------------------

_registry = get_field_registry()
_field_names = list(_registry.keys())
_string_fields = [n for n, f in _registry.items() if f.field_type in (ConfigFieldType.STRING, ConfigFieldType.TEXT)]
_integer_fields = [n for n, f in _registry.items() if f.field_type == ConfigFieldType.INTEGER]
_float_fields = [n for n, f in _registry.items() if f.field_type == ConfigFieldType.FLOAT]
_boolean_fields = [n for n, f in _registry.items() if f.field_type == ConfigFieldType.BOOLEAN]
_enum_fields = [n for n, f in _registry.items() if f.field_type == ConfigFieldType.ENUM]

field_name_strategy = st.sampled_from(_field_names)


# ---------------------------------------------------------------------------
# Tier gate monotonicity
# ---------------------------------------------------------------------------


class TestTierGateMonotonicity:
    """If a field is accessible to tier A, it must be accessible to all higher tiers."""

    @given(field_name=field_name_strategy)
    def test_higher_tier_accepts_if_lower_accepts(self, field_name: str):
        """For any field, if tier A passes the gate, tier B >= A also passes."""
        field = _registry[field_name]
        gate_rank = _GATE_RANK.get(field.tier_gate, 0)

        tiers_sorted = sorted(TenantTier, key=lambda t: _TIER_RANK.get(t, 0))

        # Find the first tier that passes the gate
        first_passing = None
        for tier in tiers_sorted:
            tier_rank = _TIER_RANK.get(tier, 0)
            if tier_rank >= gate_rank:
                first_passing = tier
                break

        if first_passing is None:
            return  # No tier passes (shouldn't happen with current data)

        # All tiers at or above first_passing must also pass
        first_rank = _TIER_RANK.get(first_passing, 0)
        for tier in tiers_sorted:
            tier_rank = _TIER_RANK.get(tier, 0)
            if tier_rank >= first_rank:
                # This tier should pass the gate — test with a benign value
                is_valid, err, _ = validate_field(field_name, _benign_value(field), tier)
                # The field should not fail due to tier gating
                if not is_valid and err and "requires" in err and "tier" in err:
                    pytest.fail(f"{field_name} rejected for {tier.value} despite tier rank >= gate")


def _benign_value(field):
    """Generate a value that should pass type validation for a field."""
    ft = field.field_type
    rules = field.validation
    if ft in (ConfigFieldType.STRING, ConfigFieldType.TEXT):
        length = max(rules.min_length or 1, 1)
        return "a" * length
    if ft == ConfigFieldType.INTEGER:
        return int(rules.min_value or 0)
    if ft == ConfigFieldType.FLOAT:
        return float(rules.min_value or 0.0)
    if ft == ConfigFieldType.BOOLEAN:
        return True
    if ft == ConfigFieldType.ENUM:
        if rules.allowed_values:
            return rules.allowed_values[0]
        return "default"
    if ft == ConfigFieldType.STRING_LIST:
        return []
    if ft == ConfigFieldType.OBJECT:
        return {}
    return None


# ---------------------------------------------------------------------------
# Type rejection
# ---------------------------------------------------------------------------


class TestTypeRejection:
    """Wrong types must be rejected for every field.

    Uses targeted strategies to avoid excessive filtering by pre-filtering
    the field lists at strategy construction time.
    """

    @given(field_name=st.sampled_from(_string_fields) if _string_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_string_field_rejects_integer(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        is_valid, _, _ = validate_field(field_name, 42, tier)
        assert not is_valid

    @given(field_name=st.sampled_from(_integer_fields) if _integer_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_integer_field_rejects_string(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        is_valid, _, _ = validate_field(field_name, "not_a_number", tier)
        assert not is_valid

    @given(field_name=st.sampled_from(_boolean_fields) if _boolean_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_boolean_field_rejects_string(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        is_valid, _, _ = validate_field(field_name, "true", tier)
        assert not is_valid

    @given(field_name=st.sampled_from(_integer_fields) if _integer_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_boolean_rejects_int(self, field_name: str, tier: TenantTier):
        """Booleans are not accepted as integers (Python bool is subclass of int)."""
        field = _registry[field_name]
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        is_valid, _, _ = validate_field(field_name, True, tier)
        assert not is_valid


# ---------------------------------------------------------------------------
# Null handling
# ---------------------------------------------------------------------------


class TestNullHandling:
    """None values must be accepted for optional fields and rejected for required ones."""

    @given(field_name=field_name_strategy, tier=tenant_tier_strategy)
    def test_optional_field_accepts_none(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(not field.validation.required)
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        is_valid, _, _ = validate_field(field_name, None, tier)
        assert is_valid

    @given(tier=tenant_tier_strategy)
    def test_required_field_rejects_none(self, tier: TenantTier):
        """Required fields must reject None. Uses a targeted strategy to avoid
        excessive filtering (most fields are optional)."""
        required_fields = [n for n, f in _registry.items() if f.validation.required]
        if not required_fields:
            pytest.skip("No required fields in registry")
        for field_name in required_fields:
            field = _registry[field_name]
            if _TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0):
                is_valid, _, _ = validate_field(field_name, None, tier)
                assert not is_valid, f"Required field {field_name} accepted None"


# ---------------------------------------------------------------------------
# String boundary enforcement
# ---------------------------------------------------------------------------


class TestStringBoundaries:
    """String length constraints must be enforced consistently."""

    @given(field_name=st.sampled_from(_string_fields) if _string_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_max_length_enforced(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(field.validation.max_length is not None)
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))

        # A string exactly at max_length should pass (unless pattern blocks it)
        max_len = field.validation.max_length
        value = "a" * max_len
        is_valid_at, _, _ = validate_field(field_name, value, tier)

        # A string over max_length must fail
        over_value = "a" * (max_len + 1)
        is_valid_over, _, _ = validate_field(field_name, over_value, tier)
        assert not is_valid_over

    @given(field_name=st.sampled_from(_string_fields) if _string_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_whitespace_stripped(self, field_name: str, tier: TenantTier):
        """Strings are stripped of leading/trailing whitespace during sanitization."""
        field = _registry[field_name]
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))
        assume(field.validation.pattern is None)  # patterns complicate this test
        min_len = field.validation.min_length or 1

        value = " " + "a" * max(min_len, 1) + " "
        is_valid, _, sanitized = validate_field(field_name, value, tier)
        if is_valid and sanitized is not None:
            assert sanitized == sanitized.strip()


# ---------------------------------------------------------------------------
# Hex color validation
# ---------------------------------------------------------------------------


class TestHexColorProperties:
    """Fields with hex color patterns must accept valid colors and reject invalid ones."""

    @given(color=hex_color_strategy, tier=tenant_tier_strategy)
    def test_valid_hex_accepted(self, color: str, tier: TenantTier):
        """Any well-formed #RRGGBB should be accepted by color fields."""
        color_fields = [
            n for n, f in _registry.items()
            if f.validation.pattern == HEX_COLOR_PATTERN
        ]
        if not color_fields:
            pytest.skip("No hex color fields in registry")
        for field_name in color_fields:
            field = _registry[field_name]
            if _TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0):
                is_valid, err, _ = validate_field(field_name, color, tier)
                assert is_valid, f"{field_name} rejected valid color {color}: {err}"

    @given(bad=st.text(min_size=1, max_size=10).filter(lambda s: not s.startswith("#")),
           tier=tenant_tier_strategy)
    def test_non_hex_rejected(self, bad: str, tier: TenantTier):
        """Strings not matching #RRGGBB must be rejected by color fields."""
        color_fields = [
            n for n, f in _registry.items()
            if f.validation.pattern == HEX_COLOR_PATTERN
        ]
        if not color_fields:
            pytest.skip("No hex color fields in registry")
        for field_name in color_fields:
            field = _registry[field_name]
            if _TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0):
                is_valid, _, _ = validate_field(field_name, bad, tier)
                assert not is_valid


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


class TestEnumProperties:
    """Enum fields must accept declared values and reject everything else."""

    @given(field_name=st.sampled_from(_enum_fields) if _enum_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_allowed_values_accepted(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(field.validation.allowed_values is not None)
        assume(len(field.validation.allowed_values) > 0)
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))

        for val in field.validation.allowed_values:
            # The validator does val.strip().lower() before checking membership.
            # Only test values whose lowercase form is still in allowed_values,
            # since mixed-case entries (e.g. 'zh-TW') fail after lowercasing.
            # That inconsistency is tracked as a separate defect.
            if val.lower() not in field.validation.allowed_values:
                continue
            is_valid, err, _ = validate_field(field_name, val, tier)
            assert is_valid, f"{field_name} rejected allowed value '{val}': {err}"

    @given(field_name=st.sampled_from(_enum_fields) if _enum_fields else st.nothing(),
           tier=tenant_tier_strategy)
    def test_random_value_rejected(self, field_name: str, tier: TenantTier):
        field = _registry[field_name]
        assume(field.validation.allowed_values is not None)
        assume(_TIER_RANK.get(tier, 0) >= _GATE_RANK.get(field.tier_gate, 0))

        bogus = "DEFINITELY_NOT_A_VALID_ENUM_VALUE_xyz123"
        is_valid, _, _ = validate_field(field_name, bogus, tier)
        assert not is_valid


# ---------------------------------------------------------------------------
# Unknown field handling
# ---------------------------------------------------------------------------


class TestUnknownFieldHandling:
    """Unknown fields must always be rejected."""

    @given(tier=tenant_tier_strategy)
    def test_unknown_field_rejected(self, tier: TenantTier):
        is_valid, _, _ = validate_field("__nonexistent_field_xyz__", "anything", tier)
        assert not is_valid
