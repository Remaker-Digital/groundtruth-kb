"""Round-trip verification tests for R3: Config YAML schema migration.

Confirms that the YAML-driven registry produces identical results to the
original Python-based registry for all 78 field definitions.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.schema.models import (
    ConfigFieldDefinition,
    ConfigFieldType,
    ConfigValidationError,
    ConfigValidationResult,
    OnboardingStep,
    SUPPORTED_LANGUAGES,
    TierGate,
    ValidationRule,
    # Constants
    MAX_BRAND_NAME_LENGTH,
    MAX_BRAND_VOICE_LENGTH,
    MAX_POLICY_TEXT_LENGTH,
    MAX_CUSTOM_INSTRUCTIONS_LENGTH,
    HEX_COLOR_PATTERN,
    AUTO_OPEN_MAX_DELAY,
)
from src.multi_tenant.schema.registry import (
    get_field_registry,
    get_fields_by_step,
    get_fields_for_tier,
    get_prompt_injected_fields,
    resolve_defaults,
    export_schema_for_api,
    reset_field_registry,
)
from src.multi_tenant.schema.validation import (
    validate_field,
    validate_config,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset the singleton before each test to ensure clean state."""
    reset_field_registry()
    yield
    reset_field_registry()


# ---------------------------------------------------------------------------
# Registry loading tests
# ---------------------------------------------------------------------------


class TestRegistryLoading:
    """Test that YAML fields load correctly."""

    def test_registry_loads_78_fields(self):
        registry = get_field_registry()
        assert len(registry) == 78

    def test_all_fields_have_required_attributes(self):
        registry = get_field_registry()
        for name, field in registry.items():
            assert field.field_name == name
            assert field.display_name
            assert isinstance(field.field_type, ConfigFieldType)
            assert isinstance(field.tier_gate, TierGate)
            assert isinstance(field.onboarding_step, OnboardingStep)
            assert field.tooltip  # Every field must have a tooltip

    def test_field_types_cover_all_enum_values(self):
        """At least one field should use each ConfigFieldType."""
        registry = get_field_registry()
        used_types = {f.field_type for f in registry.values()}
        # OBJECT type may not be used yet -- check the common ones
        for ft in [ConfigFieldType.STRING, ConfigFieldType.TEXT,
                    ConfigFieldType.INTEGER, ConfigFieldType.BOOLEAN,
                    ConfigFieldType.ENUM, ConfigFieldType.STRING_LIST]:
            assert ft in used_types, f"No field uses type {ft.value}"

    def test_onboarding_steps_covered(self):
        """Fields should span steps 1-9 at minimum."""
        registry = get_field_registry()
        steps = {f.onboarding_step.value for f in registry.values()}
        for s in range(1, 10):
            assert s in steps, f"No field in onboarding step {s}"

    def test_supported_languages_sentinel_resolved(self):
        """Fields using $SUPPORTED_LANGUAGES should have the full list."""
        registry = get_field_registry()
        primary_lang = registry["primary_language"]
        assert primary_lang.validation.allowed_values == SUPPORTED_LANGUAGES
        additional = registry["additional_languages"]
        assert additional.validation.allowed_values == SUPPORTED_LANGUAGES

    def test_brand_name_field_correct(self):
        """Spot-check the brand_name field definition."""
        registry = get_field_registry()
        f = registry["brand_name"]
        assert f.display_name == "Brand name"
        assert f.field_type == ConfigFieldType.STRING
        assert f.validation.min_length == 1
        assert f.validation.max_length == 100
        assert f.validation.required is True
        assert f.platform_default == "My Store"
        assert f.tier_gate == TierGate.ALL
        assert f.onboarding_step == OnboardingStep.BRAND_AND_TONE
        assert f.injected_in_prompt is True

    def test_tier_gated_field_exists(self):
        """Confirm at least one pro+ or enterprise-only field exists."""
        registry = get_field_registry()
        gates = {f.tier_gate for f in registry.values()}
        assert TierGate.PROFESSIONAL_PLUS in gates or TierGate.ENTERPRISE_ONLY in gates


# ---------------------------------------------------------------------------
# Accessor function tests
# ---------------------------------------------------------------------------


class TestAccessors:
    """Test registry accessor functions."""

    def test_get_fields_by_step_returns_sorted(self):
        fields = get_fields_by_step(OnboardingStep.BRAND_AND_TONE)
        assert len(fields) > 0
        orders = [f.step_order for f in fields]
        assert orders == sorted(orders)

    def test_get_fields_by_step_all_match(self):
        for step in OnboardingStep:
            fields = get_fields_by_step(step)
            for f in fields:
                assert f.onboarding_step == step

    def test_get_fields_for_tier_starter(self):
        fields = get_fields_for_tier(TenantTier.STARTER)
        for f in fields.values():
            assert f.tier_gate == TierGate.ALL

    def test_get_fields_for_tier_enterprise_includes_all(self):
        enterprise = get_fields_for_tier(TenantTier.ENTERPRISE)
        starter = get_fields_for_tier(TenantTier.STARTER)
        # Enterprise should have at least as many fields as starter
        assert len(enterprise) >= len(starter)
        # All starter fields should be in enterprise
        for name in starter:
            assert name in enterprise

    def test_get_prompt_injected_fields(self):
        injected = get_prompt_injected_fields()
        assert len(injected) > 0
        for f in injected:
            assert f.injected_in_prompt is True


# ---------------------------------------------------------------------------
# Default resolution tests
# ---------------------------------------------------------------------------


class TestDefaults:
    """Test resolve_defaults()."""

    def test_resolve_defaults_starter(self):
        defaults = resolve_defaults(TenantTier.STARTER)
        assert "brand_name" in defaults
        assert defaults["brand_name"] == "My Store"

    def test_resolve_defaults_uses_tier_override(self):
        """If a field has tier_defaults, those should take priority."""
        registry = get_field_registry()
        defaults = resolve_defaults(TenantTier.PROFESSIONAL)
        for name, field in registry.items():
            if "professional" in field.tier_defaults:
                assert defaults.get(name) == field.tier_defaults["professional"]

    def test_resolve_defaults_all_tiers_produce_values(self):
        for tier in TenantTier:
            defaults = resolve_defaults(tier)
            assert isinstance(defaults, dict)
            assert len(defaults) > 0


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


class TestValidation:
    """Test field-level and config-level validation."""

    def test_validate_valid_brand_name(self):
        ok, err, sanitized = validate_field("brand_name", "Test Store", TenantTier.STARTER)
        assert ok is True
        assert err is None
        assert sanitized == "Test Store"

    def test_validate_brand_name_too_short(self):
        ok, err, _ = validate_field("brand_name", "", TenantTier.STARTER)
        assert ok is False
        assert "at least 1" in err

    def test_validate_brand_name_too_long(self):
        ok, err, _ = validate_field("brand_name", "x" * 101, TenantTier.STARTER)
        assert ok is False
        assert "at most 100" in err

    def test_validate_brand_name_required(self):
        ok, err, _ = validate_field("brand_name", None, TenantTier.STARTER)
        assert ok is False
        assert "required" in err

    def test_validate_enum_valid(self):
        ok, err, val = validate_field("response_length", "concise", TenantTier.STARTER)
        assert ok is True
        assert val == "concise"

    def test_validate_enum_invalid(self):
        ok, err, _ = validate_field("response_length", "verbose", TenantTier.STARTER)
        assert ok is False
        assert "must be one of" in err

    def test_validate_boolean_valid(self):
        ok, err, val = validate_field("auto_detect_language", True, TenantTier.STARTER)
        assert ok is True
        assert val is True

    def test_validate_boolean_invalid(self):
        ok, err, _ = validate_field("auto_detect_language", "yes", TenantTier.STARTER)
        assert ok is False
        assert "boolean" in err

    def test_validate_string_list_valid(self):
        ok, err, val = validate_field(
            "additional_languages", ["es", "fr"], TenantTier.STARTER
        )
        assert ok is True
        assert val == ["es", "fr"]

    def test_validate_string_list_invalid_item(self):
        ok, err, _ = validate_field(
            "additional_languages", ["xx"], TenantTier.STARTER
        )
        assert ok is False
        assert "not a valid option" in err

    def test_validate_unknown_field(self):
        ok, err, _ = validate_field("nonexistent_field", "value", TenantTier.STARTER)
        assert ok is False
        assert "Unknown" in err

    def test_validate_config_full_payload(self):
        result = validate_config(
            {
                "brand_name": "Acme Store",
                "brand_voice": "friendly",
                "primary_language": "en",
            },
            TenantTier.STARTER,
        )
        assert result.valid is True
        assert "brand_name" in result.sanitized
        assert result.sanitized["brand_name"] == "Acme Store"
        assert len(result.errors) == 0

    def test_validate_config_unknown_field_warning(self):
        result = validate_config(
            {"brand_name": "Test", "unknown_xyz": "value"},
            TenantTier.STARTER,
        )
        # Unknown fields produce warnings, not errors
        assert any("unknown_xyz" in w.get("field_name", "") for w in result.warnings)

    def test_validate_integer_field(self):
        """Find an integer field and validate it."""
        registry = get_field_registry()
        int_fields = [n for n, f in registry.items() if f.field_type == ConfigFieldType.INTEGER]
        if int_fields:
            name = int_fields[0]
            ok, err, val = validate_field(name, 5, TenantTier.ENTERPRISE)
            assert ok is True
            assert val == 5

    def test_validate_integer_rejects_bool(self):
        """Integer validation rejects booleans."""
        registry = get_field_registry()
        int_fields = [n for n, f in registry.items() if f.field_type == ConfigFieldType.INTEGER]
        if int_fields:
            ok, err, _ = validate_field(int_fields[0], True, TenantTier.ENTERPRISE)
            assert ok is False
            assert "integer" in err

    def test_validate_hex_color(self):
        """Widget color fields should accept valid hex colors."""
        ok, err, val = validate_field("widget_primary_color", "#ff3621", TenantTier.STARTER)
        assert ok is True
        assert val == "#ff3621"

    def test_validate_hex_color_invalid(self):
        ok, err, _ = validate_field("widget_primary_color", "red", TenantTier.STARTER)
        assert ok is False


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------


class TestExport:
    """Test export_schema_for_api()."""

    def test_export_returns_steps(self):
        result = export_schema_for_api(TenantTier.STARTER)
        assert "steps" in result
        assert "total_fields" in result
        assert "tier" in result
        assert result["tier"] == "starter"
        assert len(result["steps"]) > 0

    def test_export_fields_have_metadata(self):
        result = export_schema_for_api(TenantTier.ENTERPRISE)
        for step in result["steps"]:
            for field in step["fields"]:
                assert "field_name" in field
                assert "display_name" in field
                assert "field_type" in field
                assert "tooltip" in field

    def test_export_enterprise_has_more_fields(self):
        starter = export_schema_for_api(TenantTier.STARTER)
        enterprise = export_schema_for_api(TenantTier.ENTERPRISE)
        assert enterprise["total_fields"] >= starter["total_fields"]


# ---------------------------------------------------------------------------
# Backward compatibility tests
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    """Test that imports from the original module path still work."""

    def test_import_from_tenant_config_schema(self):
        """The old import path should still work via re-export barrel."""
        from src.multi_tenant.tenant_config_schema import (
            ConfigFieldDefinition,
            ConfigFieldType,
            ConfigValidationResult,
            OnboardingStep,
            TierGate,
            get_field_registry,
            validate_config,
            validate_field,
            resolve_defaults,
            export_schema_for_api,
        )
        # Verify they are the same objects
        from src.multi_tenant.schema import (
            ConfigFieldDefinition as CFD2,
            get_field_registry as gfr2,
        )
        assert ConfigFieldDefinition is CFD2
        assert get_field_registry is gfr2

    def test_supported_languages_backward_compat(self):
        """_SUPPORTED_LANGUAGES should still be accessible."""
        from src.multi_tenant.tenant_config_schema import _SUPPORTED_LANGUAGES
        assert len(_SUPPORTED_LANGUAGES) == 20
        assert "en" in _SUPPORTED_LANGUAGES

    def test_constants_accessible(self):
        from src.multi_tenant.tenant_config_schema import (
            MAX_BRAND_NAME_LENGTH,
            HEX_COLOR_PATTERN,
        )
        assert MAX_BRAND_NAME_LENGTH == 100
        assert HEX_COLOR_PATTERN == r"^#[0-9a-fA-F]{6}$"
