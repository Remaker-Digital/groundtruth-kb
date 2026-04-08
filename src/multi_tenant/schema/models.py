"""Schema models -- enums, Pydantic models, and constants for tenant config.

R3 refactoring -- extracted from tenant_config_schema.py (session 39).
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Documentation base URL for tooltips linking to docs-site pages
DOCS_BASE_URL = "https://docs.agentred.ai"

# Maximum lengths for free-text fields
MAX_BRAND_NAME_LENGTH = 100
MAX_BRAND_VOICE_LENGTH = 200
MAX_POLICY_TEXT_LENGTH = 2000
MAX_CUSTOM_INSTRUCTIONS_LENGTH = 4000
MAX_ESCALATION_KEYWORD_LENGTH = 50
MAX_ESCALATION_KEYWORDS_COUNT = 30
MAX_ADDITIONAL_LANGUAGES = 10
MAX_GREETING_LENGTH = 500
MAX_FAREWELL_LENGTH = 500
MAX_FALLBACK_LENGTH = 500
MAX_BUSINESS_HOURS_SLOTS = 14  # 7 days x 2 shifts

# Widget appearance constants
MAX_WIDGET_TITLE_LENGTH = 100
MAX_AGENT_DISPLAY_NAME_LENGTH = 100
MAX_AGENT_TITLE_LENGTH = 100
MAX_PLACEHOLDER_TEXT_LENGTH = 200
MAX_OFFLINE_MESSAGE_LENGTH = 500
MAX_PAGE_RULES_COUNT = 20
MAX_PAGE_RULE_LENGTH = 500
MAX_PRECHAT_FIELDS_COUNT = 10
HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"
AUTO_OPEN_MAX_DELAY = 120  # seconds


# ---------------------------------------------------------------------------
# Supported languages (ISO 639-1 codes)
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: list[str] = [
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "pt",  # Portuguese
    "de",  # German
    "it",  # Italian
    "nl",  # Dutch
    "ja",  # Japanese
    "ko",  # Korean
    "zh",  # Chinese (Simplified)
    "zh-TW",  # Chinese (Traditional)
    "ar",  # Arabic
    "hi",  # Hindi
    "ru",  # Russian
    "pl",  # Polish
    "tr",  # Turkish
    "sv",  # Swedish
    "da",  # Danish
    "no",  # Norwegian
    "fi",  # Finnish
]


# ---------------------------------------------------------------------------
# Enums -- field types and constraint kinds
# ---------------------------------------------------------------------------


class ConfigFieldType(str, Enum):
    """Data type for a configuration field."""

    STRING = "string"
    TEXT = "text"  # Multi-line string
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"  # Single choice from a set
    SELECT = "select"  # Dropdown selection (alias for enum in YAML configs)
    STRING_LIST = "string_list"
    OBJECT = "object"  # Nested JSON object


class OnboardingStep(int, Enum):
    """10-step merchant onboarding workflow (Decision #22 + Tidio parity).

    Steps 1-8: AI behavior and business configuration (original).
    Step 9: Widget appearance and behavior (new -- Tidio parity).
    Step 10: Review and launch (renumbered from 9).
    """

    BRAND_AND_TONE = 1
    LANGUAGES = 2
    RESPONSE_STYLE = 3
    KNOWLEDGE_BASE = 4
    BUSINESS_POLICIES = 5
    ESCALATION_RULES = 6
    INTEGRATIONS = 7
    MEMORY_AND_PRIVACY = 8
    WIDGET_APPEARANCE = 9
    REVIEW_AND_LAUNCH = 10


class TierGate(str, Enum):
    """Which tiers can access a field."""

    ALL = "all"  # Starter, Professional, Enterprise
    PROFESSIONAL_PLUS = "pro+"  # Professional and Enterprise only
    PROFESSIONAL = "professional"  # Professional and above (YAML alias)
    ENTERPRISE_ONLY = "enterprise"  # Enterprise only


# ---------------------------------------------------------------------------
# Validation rule model
# ---------------------------------------------------------------------------


class ValidationRule(BaseModel):
    """Validation constraint for a config field."""

    min_length: int | None = Field(default=None, description="Minimum string length")
    max_length: int | None = Field(default=None, description="Maximum string length")
    min_value: float | None = Field(default=None, description="Minimum numeric value")
    max_value: float | None = Field(default=None, description="Maximum numeric value")
    pattern: str | None = Field(default=None, description="Regex pattern for validation")
    allowed_values: list[str] | None = Field(default=None, description="Enum: valid choices")
    max_items: int | None = Field(default=None, description="Max items for list fields")
    required: bool = Field(default=False, description="Whether the field must be set")


# ---------------------------------------------------------------------------
# Field definition model -- the core schema building block
# ---------------------------------------------------------------------------


class ConfigFieldDefinition(BaseModel):
    """Complete definition of a single tenant configuration field.

    Contains everything needed to render, validate, and document the field:
    type info, constraints, defaults, tier gating, UI metadata, and
    documentation links.
    """

    # Identity
    field_name: str = Field(description="Programmatic field name (snake_case)")
    display_name: str = Field(description="Human-readable label for UI")

    # Type and validation
    field_type: ConfigFieldType = Field(description="Data type")
    validation: ValidationRule = Field(default_factory=ValidationRule, description="Validation constraints")

    # Defaults (per tier, with platform fallback)
    platform_default: Any = Field(default=None, description="Platform-wide default (lowest priority)")
    tier_defaults: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-tier default overrides: {starter: ..., professional: ..., enterprise: ...}",
    )

    # Tier gating
    tier_gate: TierGate = Field(
        default=TierGate.ALL,
        description="Minimum tier required to configure this field",
    )

    # Onboarding workflow
    onboarding_step: OnboardingStep = Field(description="Which onboarding step this field belongs to")
    step_order: float = Field(
        default=0,
        description=(
            "Display order within the onboarding step (supports fractional values for insertion between existing "
            "fields)"
        ),
    )

    # UI metadata
    tooltip: str = Field(description="Short help text shown on hover/focus")
    description: str = Field(default="", description="Longer explanation for documentation")
    placeholder: str | None = Field(default=None, description="Placeholder text for input fields")
    doc_link: str | None = Field(default=None, description="Link to relevant documentation page")

    # Agent impact -- which agents consume this field in prompt assembly
    affects_agents: list[str] = Field(
        default_factory=list,
        description="Agent roles affected by this field (for change impact display)",
    )

    # Sensitivity
    pii_classification: str = Field(
        default="none",
        description="PII classification: none, indirect, direct, sensitive",
    )

    # Prompt injection
    injected_in_prompt: bool = Field(
        default=False,
        description="Whether this field value is injected into AI system prompts",
    )


# ---------------------------------------------------------------------------
# Validation result models
# ---------------------------------------------------------------------------


class ConfigValidationError(Exception):
    """Raised when a config value fails validation."""

    def __init__(self, field_name: str, message: str) -> None:
        self.field_name = field_name
        self.message = message
        super().__init__(f"{field_name}: {message}")


class ConfigValidationResult(BaseModel):
    """Result of validating a tenant config payload."""

    valid: bool = Field(description="Whether all fields passed validation")
    errors: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of {field_name, message} for each invalid field",
    )
    warnings: list[dict[str, str]] = Field(
        default_factory=list,
        description="Non-blocking warnings (e.g. field unavailable at tier)",
    )
    sanitized: dict[str, Any] = Field(
        default_factory=dict,
        description="The validated and sanitized config values",
    )
