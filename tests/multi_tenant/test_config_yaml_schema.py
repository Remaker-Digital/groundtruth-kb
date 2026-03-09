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

    def test_registry_loads_91_fields(self):
        """91 fields after test_mode_enabled removal (S157)."""
        registry = get_field_registry()
        assert len(registry) == 91

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
# Field pipeline completeness tests (regression — S103 gradient toggle bug)
# ---------------------------------------------------------------------------


class TestFieldPipelineCompleteness:
    """Verify that every widget_* field in fields.yaml is mapped through
    the full pipeline: fields.yaml → cosmos_schema → field_mapping.

    The gradient toggle bug (S103) occurred because widget_header_gradient_enabled
    was defined in the admin UI but missing from field_mapping.py, cosmos_schema.py,
    and fields.yaml. These tests ensure no widget field is ever orphaned again.
    """

    # Known discrepancies — fields added to one layer but not yet wired to all.
    # These are tracked as tech debt. When fixed, remove from these sets and the
    # tests will automatically verify full-pipeline coverage.
    _YAML_ONLY_NOT_IN_MAPPING = {
        "widget_greeting_mode",          # S99: added to YAML, not wired to mapping
        "widget_quick_actions_enabled",  # In YAML + Cosmos, not in field_mapping
    }
    _MAPPING_ONLY_NOT_IN_YAML = {
        "widget_agent_bubble_color",          # In mapping, YAML definition pending
        "widget_agent_bubble_text_color",     # In mapping, YAML definition pending
        "widget_customer_bubble_color",       # In mapping, YAML definition pending
        "widget_customer_bubble_text_color",  # In mapping, YAML definition pending
        "widget_key",                         # Internal field, not user-configurable
"widget_launcher_shape",              # In mapping, YAML definition pending
        "widget_launcher_color",              # In mapping, YAML definition pending
    }
    _YAML_ONLY_NOT_IN_COSMOS = {
        "widget_greeting_mode",     # S99: added to YAML, not in Cosmos schema
    }

    def test_all_widget_yaml_fields_in_field_mapping(self):
        """Every widget_* field in fields.yaml must appear in _PREFS_DIRECT_FIELDS."""
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS
        registry = get_field_registry()
        widget_yaml_fields = {name for name in registry if name.startswith("widget_")}
        widget_mapping_fields = {name for name in _PREFS_DIRECT_FIELDS if name.startswith("widget_")}
        missing = widget_yaml_fields - widget_mapping_fields - self._YAML_ONLY_NOT_IN_MAPPING
        assert not missing, (
            f"Widget fields in fields.yaml but NOT in field_mapping.py _PREFS_DIRECT_FIELDS: "
            f"{sorted(missing)}. Add them to field_mapping.py to ensure they flow to the widget."
        )

    def test_all_widget_mapping_fields_in_yaml(self):
        """Every widget_* field in _PREFS_DIRECT_FIELDS must exist in fields.yaml."""
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS
        registry = get_field_registry()
        widget_yaml_fields = {name for name in registry if name.startswith("widget_")}
        widget_mapping_fields = {name for name in _PREFS_DIRECT_FIELDS if name.startswith("widget_")}
        extra = widget_mapping_fields - widget_yaml_fields - self._MAPPING_ONLY_NOT_IN_YAML
        assert not extra, (
            f"Widget fields in field_mapping.py but NOT in fields.yaml: {sorted(extra)}. "
            f"Add them to fields.yaml for validation and documentation."
        )

    def test_all_widget_yaml_fields_in_cosmos_schema(self):
        """Every widget_* field in fields.yaml must exist on PreferencesDocument."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        registry = get_field_registry()
        widget_yaml_fields = {name for name in registry if name.startswith("widget_")}
        schema_fields = set(PreferencesDocument.model_fields.keys())
        missing = widget_yaml_fields - schema_fields - self._YAML_ONLY_NOT_IN_COSMOS
        assert not missing, (
            f"Widget fields in fields.yaml but NOT in PreferencesDocument: {sorted(missing)}. "
            f"Add them to cosmos_schema.py to ensure persistence."
        )

    def test_known_discrepancy_count_shrinks(self):
        """Alert when known discrepancies are fixed — remove them from the allowlists."""
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        registry = get_field_registry()
        yaml_fields = {name for name in registry if name.startswith("widget_")}
        mapping_fields = {name for name in _PREFS_DIRECT_FIELDS if name.startswith("widget_")}
        cosmos_fields = set(PreferencesDocument.model_fields.keys())

        # If a "known discrepancy" field was added to the target layer, remove it
        # from the allowlist so the test becomes stricter over time.
        yaml_not_mapping_fixed = self._YAML_ONLY_NOT_IN_MAPPING & mapping_fields
        mapping_not_yaml_fixed = self._MAPPING_ONLY_NOT_IN_YAML & yaml_fields
        yaml_not_cosmos_fixed = self._YAML_ONLY_NOT_IN_COSMOS & cosmos_fields
        all_fixed = yaml_not_mapping_fixed | mapping_not_yaml_fixed | yaml_not_cosmos_fixed
        assert not all_fixed, (
            f"These 'known discrepancy' fields have been fixed! Remove from allowlists: "
            f"{sorted(all_fixed)}"
        )

    def test_widget_appearance_fields_set_equals_widget_prefix_filter(self):
        """_WIDGET_APPEARANCE_FIELDS should be exactly the widget_* subset of _PREFS_DIRECT_FIELDS."""
        from src.multi_tenant.config.field_mapping import (
            _PREFS_DIRECT_FIELDS,
            _WIDGET_APPEARANCE_FIELDS,
        )
        expected = frozenset(f for f in _PREFS_DIRECT_FIELDS if f.startswith("widget_"))
        assert _WIDGET_APPEARANCE_FIELDS == expected, (
            f"_WIDGET_APPEARANCE_FIELDS is out of sync. "
            f"Missing: {expected - _WIDGET_APPEARANCE_FIELDS}, "
            f"Extra: {_WIDGET_APPEARANCE_FIELDS - expected}"
        )

    def test_widget_gradient_enabled_in_full_pipeline(self):
        """Explicit regression test for the S103 gradient toggle bug.

        widget_header_gradient_enabled must exist in all 3 layers:
        fields.yaml, cosmos_schema.py, and field_mapping.py.
        """
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        field_name = "widget_header_gradient_enabled"

        # Layer 1: fields.yaml
        registry = get_field_registry()
        assert field_name in registry, f"{field_name} missing from fields.yaml"

        # Layer 2: cosmos_schema.py
        assert field_name in PreferencesDocument.model_fields, (
            f"{field_name} missing from PreferencesDocument"
        )

        # Layer 3: field_mapping.py
        assert field_name in _PREFS_DIRECT_FIELDS, (
            f"{field_name} missing from _PREFS_DIRECT_FIELDS"
        )


class TestSetupChecklistFieldNames:
    """Verify that the Dashboard setup checklist references valid field names.

    The setup checklist bug (S103) used 'display_name' instead of 'brand_name'.
    These tests verify that all field names used in checklist logic exist in the
    config schema, preventing similar silent failures.
    """

    def test_brand_name_field_exists(self):
        """The checklist checks config.brand_name — verify it exists."""
        registry = get_field_registry()
        assert "brand_name" in registry, "brand_name not in registry"
        assert registry["brand_name"].platform_default == "My Store"

    def test_brand_voice_field_exists(self):
        """The checklist checks config.brand_voice — verify it exists."""
        registry = get_field_registry()
        assert "brand_voice" in registry, "brand_voice not in registry"

    def test_custom_instructions_field_exists(self):
        """The checklist checks config.custom_instructions — verify it exists."""
        registry = get_field_registry()
        assert "custom_instructions" in registry

    def test_business_category_does_not_exist(self):
        """business_category is referenced in the setup checklist but is not a real field.

        The checklist condition is: custom_instructions || business_category || brand_voice
        Since business_category doesn't exist, it's always falsy — but brand_voice
        and custom_instructions cover the check. If business_category is ever added
        as a real field, remove this test and update the checklist logic.
        """
        registry = get_field_registry()
        assert "business_category" not in registry

    def test_widget_primary_color_field_exists(self):
        """The checklist checks config.widget_primary_color — verify it exists."""
        registry = get_field_registry()
        assert "widget_primary_color" in registry
        assert registry["widget_primary_color"].platform_default == "#ff3621"

    def test_display_name_does_not_exist(self):
        """Negative test: 'display_name' should NOT be in the registry.

        The S103 bug used config.display_name instead of config.brand_name.
        If display_name is ever added, this test alerts us to update the
        checklist (or rename the field deliberately).
        """
        registry = get_field_registry()
        assert "display_name" not in registry, (
            "display_name was added to registry — update Dashboard.tsx "
            "setup checklist if this field should replace brand_name"
        )


class TestTenantLookupResponseSchema:
    """Verify TenantLookupResponse includes brand_name field.

    The brand name display bug (S103) required adding brand_name to the
    lookup response so standalone tenants show their name in the navbar.
    """

    def test_tenant_lookup_response_has_brand_name(self):
        from src.integrations.provisioning import TenantLookupResponse
        fields = TenantLookupResponse.model_fields
        assert "brand_name" in fields, (
            "TenantLookupResponse missing brand_name field — "
            "standalone tenants won't show their name in the admin navbar"
        )

    def test_tenant_lookup_response_brand_name_optional(self):
        """brand_name should be optional (None for unconfigured tenants)."""
        from src.integrations.provisioning import TenantLookupResponse
        field_info = TenantLookupResponse.model_fields["brand_name"]
        assert field_info.default is None, "brand_name should default to None"


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
