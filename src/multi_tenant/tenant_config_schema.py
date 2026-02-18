"""Tenant configuration JSON schema -- field definitions, validation, and metadata.

Work Item #63 (Decision #22): Layer 1 of the 5-layer tenant configuration system.

R3 refactoring -- this file is now a thin re-export barrel.
All definitions have been moved to ``src.multi_tenant.schema``:
  - models.py: Enums, Pydantic models, constants
  - validation.py: Field-level and config-level validators
  - registry.py: YAML-driven field registry, accessors, export
  - fields.yaml: 78 field definitions (declarative)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

# Re-export everything from the schema package so that existing
# ``from src.multi_tenant.tenant_config_schema import X`` paths continue to work.
from src.multi_tenant.schema import (  # noqa: F401
    AUTO_OPEN_MAX_DELAY,
    ConfigFieldDefinition,
    ConfigFieldType,
    ConfigValidationError,
    ConfigValidationResult,
    DOCS_BASE_URL,
    HEX_COLOR_PATTERN,
    MAX_ADDITIONAL_LANGUAGES,
    MAX_AGENT_DISPLAY_NAME_LENGTH,
    MAX_AGENT_TITLE_LENGTH,
    MAX_BRAND_NAME_LENGTH,
    MAX_BRAND_VOICE_LENGTH,
    MAX_BUSINESS_HOURS_SLOTS,
    MAX_CUSTOM_INSTRUCTIONS_LENGTH,
    MAX_ESCALATION_KEYWORD_LENGTH,
    MAX_ESCALATION_KEYWORDS_COUNT,
    MAX_FAREWELL_LENGTH,
    MAX_FALLBACK_LENGTH,
    MAX_GREETING_LENGTH,
    MAX_OFFLINE_MESSAGE_LENGTH,
    MAX_PAGE_RULE_LENGTH,
    MAX_PAGE_RULES_COUNT,
    MAX_PLACEHOLDER_TEXT_LENGTH,
    MAX_POLICY_TEXT_LENGTH,
    MAX_PRECHAT_FIELDS_COUNT,
    MAX_WIDGET_TITLE_LENGTH,
    OnboardingStep,
    SUPPORTED_LANGUAGES,
    TierGate,
    ValidationRule,
    export_schema_for_api,
    get_field_registry,
    get_fields_by_step,
    get_fields_for_tier,
    get_prompt_injected_fields,
    reset_field_registry,
    resolve_defaults,
    validate_config,
    validate_field,
)

# Backward compatibility: the original module exposed _SUPPORTED_LANGUAGES
# as a private name. Some consumers may reference it.
_SUPPORTED_LANGUAGES = SUPPORTED_LANGUAGES

# Original _build_field_registry is now internal to the schema package.
# Re-export the public registry function for any direct callers.
from src.multi_tenant.schema.registry import (  # noqa: F401, E402
    _build_field_registry,
)
