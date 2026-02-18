"""Schema package -- tenant configuration field definitions and validation.

Barrel re-export preserving the original ``from src.multi_tenant.tenant_config_schema import ...``
import paths. All public symbols that were previously in the monolithic
``tenant_config_schema.py`` module are re-exported here.

R3 refactoring -- session 39.
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.multi_tenant.schema.models import (
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
)
from src.multi_tenant.schema.registry import (
    export_schema_for_api,
    get_field_registry,
    get_fields_by_step,
    get_fields_for_tier,
    get_prompt_injected_fields,
    reset_field_registry,
    resolve_defaults,
)
from src.multi_tenant.schema.validation import (
    validate_config,
    validate_field,
)

__all__ = [
    # Models and enums
    "ConfigFieldDefinition",
    "ConfigFieldType",
    "ConfigValidationError",
    "ConfigValidationResult",
    "OnboardingStep",
    "TierGate",
    "ValidationRule",
    # Constants
    "AUTO_OPEN_MAX_DELAY",
    "DOCS_BASE_URL",
    "HEX_COLOR_PATTERN",
    "MAX_ADDITIONAL_LANGUAGES",
    "MAX_AGENT_DISPLAY_NAME_LENGTH",
    "MAX_AGENT_TITLE_LENGTH",
    "MAX_BRAND_NAME_LENGTH",
    "MAX_BRAND_VOICE_LENGTH",
    "MAX_BUSINESS_HOURS_SLOTS",
    "MAX_CUSTOM_INSTRUCTIONS_LENGTH",
    "MAX_ESCALATION_KEYWORD_LENGTH",
    "MAX_ESCALATION_KEYWORDS_COUNT",
    "MAX_FAREWELL_LENGTH",
    "MAX_FALLBACK_LENGTH",
    "MAX_GREETING_LENGTH",
    "MAX_OFFLINE_MESSAGE_LENGTH",
    "MAX_PAGE_RULE_LENGTH",
    "MAX_PAGE_RULES_COUNT",
    "MAX_PLACEHOLDER_TEXT_LENGTH",
    "MAX_POLICY_TEXT_LENGTH",
    "MAX_PRECHAT_FIELDS_COUNT",
    "MAX_WIDGET_TITLE_LENGTH",
    "SUPPORTED_LANGUAGES",
    # Registry functions
    "export_schema_for_api",
    "get_field_registry",
    "get_fields_by_step",
    "get_fields_for_tier",
    "get_prompt_injected_fields",
    "reset_field_registry",
    "resolve_defaults",
    # Validation functions
    "validate_config",
    "validate_field",
]
