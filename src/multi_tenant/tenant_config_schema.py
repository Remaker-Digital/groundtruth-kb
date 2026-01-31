"""Tenant configuration JSON schema — field definitions, validation, and metadata.

Work Item #63 (Decision #22): Layer 1 of the 5-layer tenant configuration system.

Defines the complete schema for merchant-configurable fields including:
    - Field types, constraints, and default values (per tier)
    - Validation rules (regex, range, enum, length)
    - UI metadata: tooltips, documentation links, onboarding step mapping
    - Config inheritance model: platform defaults → tier defaults → tenant overrides
    - Field-level tier gating (which fields are available at each tier)
    - Field grouping aligned with the 9-step onboarding workflow

The schema is consumed by:
    - TenantConfigProcessor (#64) for validation and cleansing
    - Configuration API (#65) for field metadata in responses
    - Future Merchant Configuration UI (#67) for rendering forms
    - SystemPromptBuilder (#70) via resolved PreferencesDocument

Config inheritance (Decision #22):
    platform defaults → tier defaults → tenant overrides → (future: A/B variant)
    60-second in-memory cache. Version history with rollback.

Architecture references:
    - Decision #22: 5-layer tenant configuration management system
    - Decision #23: SystemPromptBuilder (consumes resolved config)
    - Work Item #63: Design tenant_config JSON schema
    - Work Item #64: TenantConfigProcessor (downstream consumer)
    - Work Item #65: Configuration API (downstream consumer)

Dependencies:
    - cosmos_schema.py: PreferencesDocument, TenantTier, TIER_DEFAULTS

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.multi_tenant.cosmos_schema import TenantTier, TIER_DEFAULTS

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
MAX_BUSINESS_HOURS_SLOTS = 14  # 7 days × 2 shifts


# ---------------------------------------------------------------------------
# Enums — field types and constraint kinds
# ---------------------------------------------------------------------------


class ConfigFieldType(str, Enum):
    """Data type for a configuration field."""

    STRING = "string"
    TEXT = "text"          # Multi-line string
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"          # Single choice from a set
    STRING_LIST = "string_list"
    OBJECT = "object"      # Nested JSON object


class OnboardingStep(int, Enum):
    """9-step merchant onboarding workflow (Decision #22)."""

    BRAND_AND_TONE = 1
    LANGUAGES = 2
    RESPONSE_STYLE = 3
    KNOWLEDGE_BASE = 4
    BUSINESS_POLICIES = 5
    ESCALATION_RULES = 6
    INTEGRATIONS = 7
    MEMORY_AND_PRIVACY = 8
    REVIEW_AND_LAUNCH = 9


class TierGate(str, Enum):
    """Which tiers can access a field."""

    ALL = "all"                    # Starter, Professional, Enterprise
    PROFESSIONAL_PLUS = "pro+"     # Professional and Enterprise only
    ENTERPRISE_ONLY = "enterprise" # Enterprise only


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
    allowed_values: list[str] | None = Field(
        default=None, description="Enum: valid choices"
    )
    max_items: int | None = Field(default=None, description="Max items for list fields")
    required: bool = Field(default=False, description="Whether the field must be set")


# ---------------------------------------------------------------------------
# Field definition model — the core schema building block
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
    validation: ValidationRule = Field(
        default_factory=ValidationRule, description="Validation constraints"
    )

    # Defaults (per tier, with platform fallback)
    platform_default: Any = Field(
        default=None, description="Platform-wide default (lowest priority)"
    )
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
    onboarding_step: OnboardingStep = Field(
        description="Which onboarding step this field belongs to"
    )
    step_order: int = Field(
        default=0,
        description="Display order within the onboarding step (0-indexed)",
    )

    # UI metadata
    tooltip: str = Field(description="Short help text shown on hover/focus")
    description: str = Field(
        default="", description="Longer explanation for documentation"
    )
    placeholder: str | None = Field(
        default=None, description="Placeholder text for input fields"
    )
    doc_link: str | None = Field(
        default=None, description="Link to relevant documentation page"
    )

    # Agent impact — which agents consume this field in prompt assembly
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
# Field registry — all configurable fields
# ---------------------------------------------------------------------------

def _build_field_registry() -> dict[str, ConfigFieldDefinition]:
    """Build the complete registry of tenant-configurable fields.

    Organized by the 9-step onboarding workflow. Each field maps to a
    PreferencesDocument property (or extends it for fields that will be
    added to PreferencesDocument in the TenantConfigProcessor).

    Returns:
        Dict keyed by field_name.
    """
    fields: list[ConfigFieldDefinition] = []

    # ===================================================================
    # Step 1: Brand & Tone
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="brand_name",
        display_name="Brand Name",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            min_length=1,
            max_length=MAX_BRAND_NAME_LENGTH,
            required=True,
        ),
        platform_default="My Store",
        onboarding_step=OnboardingStep.BRAND_AND_TONE,
        step_order=0,
        tooltip="Your brand name as it appears in customer conversations.",
        description=(
            "The AI agent introduces itself using this name. Appears in greetings, "
            "sign-offs, and when referencing your business. Keep it consistent with "
            "your storefront branding."
        ),
        placeholder="e.g. Acme Outdoor Gear",
        doc_link=f"{DOCS_BASE_URL}/configuration/brand-tone",
        affects_agents=[
            "intent-classifier", "knowledge-retrieval",
            "response-generator", "escalation-handler",
            "analytics-collector",
        ],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="brand_voice",
        display_name="Brand Voice",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=MAX_BRAND_VOICE_LENGTH,
        ),
        platform_default="friendly and helpful",
        onboarding_step=OnboardingStep.BRAND_AND_TONE,
        step_order=1,
        tooltip="Describe your brand's personality in a few words.",
        description=(
            "Guides the AI's overall communication style. Examples: "
            "'friendly and casual', 'professional and concise', "
            "'warm and empathetic', 'technical and precise'. "
            "This shapes word choice, sentence structure, and tone."
        ),
        placeholder="e.g. friendly and helpful",
        doc_link=f"{DOCS_BASE_URL}/configuration/brand-tone#voice",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="greeting_message",
        display_name="Greeting Message",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_GREETING_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BRAND_AND_TONE,
        step_order=2,
        tooltip="Optional custom greeting when a customer starts a conversation.",
        description=(
            "If set, this message is sent as the first response when a customer "
            "initiates a conversation. Leave blank to let the AI generate a "
            "contextual greeting based on your brand voice settings."
        ),
        placeholder="e.g. Hi there! How can I help you today?",
        doc_link=f"{DOCS_BASE_URL}/configuration/brand-tone#greeting",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="farewell_message",
        display_name="Farewell Message",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_FAREWELL_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BRAND_AND_TONE,
        step_order=3,
        tooltip="Optional sign-off message at end of conversations.",
        description=(
            "Sent when a conversation is resolved. Leave blank to let the AI "
            "generate an appropriate closing based on the conversation context."
        ),
        placeholder="e.g. Thanks for reaching out! Have a great day.",
        doc_link=f"{DOCS_BASE_URL}/configuration/brand-tone#farewell",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 2: Languages
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="primary_language",
        display_name="Primary Language",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=_SUPPORTED_LANGUAGES,
            required=True,
        ),
        platform_default="en",
        onboarding_step=OnboardingStep.LANGUAGES,
        step_order=0,
        tooltip="The main language your AI agent communicates in.",
        description=(
            "Sets the default response language. The intent classifier uses this "
            "to optimize classification accuracy. Customers writing in other "
            "supported languages will still be understood if additional languages "
            "are enabled."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/languages",
        affects_agents=[
            "intent-classifier", "response-generator", "escalation-handler",
        ],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="additional_languages",
        display_name="Additional Languages",
        field_type=ConfigFieldType.STRING_LIST,
        validation=ValidationRule(
            max_items=MAX_ADDITIONAL_LANGUAGES,
            allowed_values=_SUPPORTED_LANGUAGES,
        ),
        platform_default=[],
        tier_defaults={
            TenantTier.STARTER.value: [],
            TenantTier.PROFESSIONAL.value: [],
            TenantTier.ENTERPRISE.value: [],
        },
        tier_gate=TierGate.ALL,
        onboarding_step=OnboardingStep.LANGUAGES,
        step_order=1,
        tooltip="Additional languages the AI agent can respond in.",
        description=(
            "The Multi-Language Pack add-on is required for additional languages "
            "beyond the primary. When enabled, the AI detects the customer's "
            "language and responds accordingly. Supported languages vary by model."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/languages#additional",
        affects_agents=[
            "intent-classifier", "response-generator", "escalation-handler",
        ],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="auto_detect_language",
        display_name="Auto-Detect Language",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.LANGUAGES,
        step_order=2,
        tooltip="Automatically detect customer language and respond in kind.",
        description=(
            "When enabled, the AI analyses the customer's first message to detect "
            "their language and responds in that language if supported. When "
            "disabled, the AI always responds in the primary language."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/languages#auto-detect",
        affects_agents=["intent-classifier", "response-generator"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 3: Response Style
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="response_length",
        display_name="Response Length",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["concise", "standard", "detailed"],
        ),
        platform_default="standard",
        onboarding_step=OnboardingStep.RESPONSE_STYLE,
        step_order=0,
        tooltip="How long AI responses should be.",
        description=(
            "Concise: 1-2 sentences, direct answers. Standard: 2-4 sentences "
            "with context. Detailed: comprehensive responses with explanations "
            "and next steps. Affects the Response Generator's output length."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/response-style",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="formality_level",
        display_name="Formality Level",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["casual", "balanced", "formal"],
        ),
        platform_default="balanced",
        onboarding_step=OnboardingStep.RESPONSE_STYLE,
        step_order=1,
        tooltip="The formality of AI responses.",
        description=(
            "Casual: conversational, contractions, informal phrasing. "
            "Balanced: professional but approachable. "
            "Formal: no contractions, structured sentences, professional register. "
            "Works in combination with your brand voice setting."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/response-style#formality",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="emoji_usage",
        display_name="Emoji Usage",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["none", "minimal", "moderate"],
        ),
        platform_default="minimal",
        onboarding_step=OnboardingStep.RESPONSE_STYLE,
        step_order=2,
        tooltip="How often the AI uses emojis in responses.",
        description=(
            "None: no emojis at all. Minimal: occasional emoji for friendliness "
            "(1-2 per conversation). Moderate: emojis in most responses where "
            "appropriate. Does not affect the Critic's content evaluation."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/response-style#emoji",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="fallback_message",
        display_name="Fallback Message",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_FALLBACK_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.RESPONSE_STYLE,
        step_order=3,
        tooltip="Message shown when the AI cannot answer a question.",
        description=(
            "Used when the knowledge base has no relevant information and the AI "
            "cannot confidently respond. Leave blank to use the platform default: "
            "'I don't have enough information to answer that. Let me connect you "
            "with our support team.'"
        ),
        placeholder="e.g. I'm not sure about that. Let me find someone who can help.",
        doc_link=f"{DOCS_BASE_URL}/configuration/response-style#fallback",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 4: Knowledge Base (metadata — actual KB content is separate)
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="knowledge_scope",
        display_name="Knowledge Scope",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["products_only", "products_and_faqs", "full"],
        ),
        platform_default="full",
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=0,
        tooltip="What types of knowledge the AI can search.",
        description=(
            "Products only: the AI references product catalog data. "
            "Products and FAQs: adds FAQ content. "
            "Full: products, FAQs, and custom policy documents. "
            "Restricting scope can reduce irrelevant responses."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="product_recommendation_enabled",
        display_name="Product Recommendations",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=1,
        tooltip="Allow the AI to suggest related or alternative products.",
        description=(
            "When enabled, the AI may recommend complementary or substitute "
            "products during conversations. Uses the knowledge base product "
            "catalog for recommendations. Disable if you prefer the AI to "
            "only answer direct questions."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#recommendations",
        affects_agents=["response-generator", "knowledge-retrieval"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="out_of_stock_behavior",
        display_name="Out of Stock Behavior",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["inform", "suggest_alternatives", "collect_email"],
        ),
        platform_default="suggest_alternatives",
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=2,
        tooltip="What the AI does when a requested product is out of stock.",
        description=(
            "Inform: tells the customer the item is unavailable. "
            "Suggest alternatives: proposes similar in-stock products. "
            "Collect email: offers to notify when restocked."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#out-of-stock",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 5: Business Policies
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="return_policy",
        display_name="Return Policy",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_POLICY_TEXT_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BUSINESS_POLICIES,
        step_order=0,
        tooltip="Your return/refund policy — the AI references this in conversations.",
        description=(
            "Paste or summarise your return/refund policy. The AI uses this "
            "text to answer return-related questions accurately. The Critic "
            "validates responses don't contradict this policy. Keep it factual "
            "and specific (time limits, conditions, process)."
        ),
        placeholder="e.g. 30-day returns on unused items. Refunds processed within 5-7 business days.",
        doc_link=f"{DOCS_BASE_URL}/configuration/policies#returns",
        affects_agents=["response-generator", "critic-supervisor"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="shipping_info",
        display_name="Shipping Information",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_POLICY_TEXT_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BUSINESS_POLICIES,
        step_order=1,
        tooltip="Your shipping policy — the AI references this for delivery questions.",
        description=(
            "Summarise your shipping options, timelines, and costs. The AI "
            "uses this to answer shipping inquiries. Include: standard/express "
            "options, typical delivery times, free shipping thresholds, "
            "international availability."
        ),
        placeholder="e.g. Free shipping on orders over $50. Standard delivery: 3-5 business days.",
        doc_link=f"{DOCS_BASE_URL}/configuration/policies#shipping",
        affects_agents=["response-generator", "critic-supervisor"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="warranty_info",
        display_name="Warranty Information",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_POLICY_TEXT_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BUSINESS_POLICIES,
        step_order=2,
        tooltip="Product warranty details for the AI to reference.",
        description=(
            "Describe your warranty coverage, duration, and claim process. "
            "Leave blank if not applicable."
        ),
        placeholder="e.g. 1-year manufacturer warranty. Contact us for claims.",
        doc_link=f"{DOCS_BASE_URL}/configuration/policies#warranty",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="support_hours",
        display_name="Support Hours",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=500,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BUSINESS_POLICIES,
        step_order=3,
        tooltip="Your human support team's business hours.",
        description=(
            "The AI references this when suggesting escalation or when "
            "customers ask about human agent availability. The AI is always "
            "available 24/7 regardless of this setting."
        ),
        placeholder="e.g. Mon-Fri 9am-5pm EST",
        doc_link=f"{DOCS_BASE_URL}/configuration/policies#hours",
        affects_agents=["response-generator", "escalation-handler"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="custom_policies",
        display_name="Additional Policies",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_POLICY_TEXT_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.BUSINESS_POLICIES,
        step_order=4,
        tooltip="Any other policies the AI should know about.",
        description=(
            "Include additional business rules, loyalty programs, price-match "
            "policies, or any other information the AI should reference. "
            "This is supplementary to the structured policy fields above."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/policies#custom",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 6: Escalation Rules
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="escalation_threshold",
        display_name="Escalation Threshold",
        field_type=ConfigFieldType.FLOAT,
        validation=ValidationRule(
            min_value=0.0,
            max_value=1.0,
        ),
        platform_default=0.7,
        tier_defaults={
            TenantTier.STARTER.value: 0.7,
            TenantTier.PROFESSIONAL.value: 0.6,
            TenantTier.ENTERPRISE.value: 0.5,
        },
        onboarding_step=OnboardingStep.ESCALATION_RULES,
        step_order=0,
        tooltip="Confidence level below which the AI escalates to a human agent.",
        description=(
            "When the AI's confidence in its response falls below this threshold, "
            "it initiates escalation. Lower values mean fewer escalations (the AI "
            "handles more). Higher values mean more escalations (more cautious). "
            "Professional and Enterprise tiers default lower because they typically "
            "have richer knowledge bases."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/escalation#threshold",
        affects_agents=["escalation-handler", "response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="escalation_keywords",
        display_name="Escalation Keywords",
        field_type=ConfigFieldType.STRING_LIST,
        validation=ValidationRule(
            max_items=MAX_ESCALATION_KEYWORDS_COUNT,
            max_length=MAX_ESCALATION_KEYWORD_LENGTH,
        ),
        platform_default=[],
        onboarding_step=OnboardingStep.ESCALATION_RULES,
        step_order=1,
        tooltip="Words/phrases that trigger immediate escalation to a human.",
        description=(
            "When a customer message contains any of these keywords or phrases, "
            "the conversation is immediately escalated regardless of the AI's "
            "confidence score. Use for sensitive topics: 'lawyer', 'sue', "
            "'complaint', 'manager', etc."
        ),
        placeholder="e.g. lawyer, complaint, manager",
        doc_link=f"{DOCS_BASE_URL}/configuration/escalation#keywords",
        affects_agents=["escalation-handler", "response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="escalation_email",
        display_name="Escalation Notification Email",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=254,
            pattern=r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.ESCALATION_RULES,
        step_order=2,
        tooltip="Email address notified when a conversation is escalated.",
        description=(
            "When a conversation escalates to a human agent, a notification "
            "is sent to this email. If blank, escalation follows the default "
            "workflow (Zendesk ticket, Shopify inbox, etc.)."
        ),
        placeholder="e.g. support@yourstore.com",
        doc_link=f"{DOCS_BASE_URL}/configuration/escalation#notifications",
        affects_agents=["escalation-handler"],
        pii_classification="direct",
    ))

    fields.append(ConfigFieldDefinition(
        field_name="max_ai_turns_before_escalation",
        display_name="Max AI Turns Before Escalation",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=1,
            max_value=50,
        ),
        platform_default=10,
        onboarding_step=OnboardingStep.ESCALATION_RULES,
        step_order=3,
        tooltip="Maximum conversation turns before automatic escalation.",
        description=(
            "If a conversation reaches this many turns without resolution, "
            "the AI offers escalation to a human agent. Prevents long loops "
            "where the AI cannot resolve the issue. Set higher for complex "
            "product domains."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/escalation#max-turns",
        affects_agents=["escalation-handler"],
        injected_in_prompt=True,
    ))

    # ===================================================================
    # Step 7: Integrations (metadata — actual integration setup is separate)
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="shopify_sync_enabled",
        display_name="Shopify Product Sync",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.INTEGRATIONS,
        step_order=0,
        tooltip="Automatically sync product data from your Shopify store.",
        description=(
            "When enabled, the knowledge base is automatically updated when "
            "products are added, modified, or removed in your Shopify store. "
            "Uses Shopify webhooks for real-time sync."
        ),
        doc_link=f"{DOCS_BASE_URL}/integrations/shopify",
        affects_agents=["knowledge-retrieval"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="zendesk_escalation_enabled",
        display_name="Zendesk Ticket Creation",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.INTEGRATIONS,
        step_order=1,
        tooltip="Create Zendesk tickets automatically on escalation.",
        description=(
            "When enabled, escalated conversations automatically create a "
            "Zendesk Support ticket with the full conversation transcript and "
            "customer context. Requires Zendesk integration setup."
        ),
        doc_link=f"{DOCS_BASE_URL}/integrations/zendesk",
        affects_agents=["escalation-handler"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="mailchimp_segment_sync",
        display_name="Mailchimp Segment Sync",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.INTEGRATIONS,
        step_order=2,
        tooltip="Sync marketing segments from Mailchimp for personalization.",
        description=(
            "Imports customer segments from Mailchimp to enhance the AI's "
            "customer context (Layer 1). Enables personalized responses based "
            "on campaign membership and engagement data."
        ),
        doc_link=f"{DOCS_BASE_URL}/integrations/mailchimp",
        affects_agents=["response-generator"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="google_analytics_enabled",
        display_name="Google Analytics Export",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.INTEGRATIONS,
        step_order=3,
        tooltip="Export conversation events to Google Analytics 4.",
        description=(
            "Sends conversation events (start, resolution, escalation, CSAT) "
            "to your GA4 property for unified analytics. Requires GA4 "
            "integration setup."
        ),
        doc_link=f"{DOCS_BASE_URL}/integrations/google-analytics",
        affects_agents=[],
    ))

    # ===================================================================
    # Step 8: Memory & Privacy
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="memory_enabled",
        display_name="Conversation Memory",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.MEMORY_AND_PRIVACY,
        step_order=0,
        tooltip="Enable Layer 2+ memory (remembers past conversations).",
        description=(
            "When enabled, the AI remembers past conversations with each customer "
            "and uses that history to provide more personalized responses. "
            "Layer 1 (customer profile) is always active. This controls Layers 2-4 "
            "(conversation history, learned patterns, dedicated model). "
            "Disabling this limits personalization to the current session."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/memory-privacy",
        affects_agents=["response-generator", "escalation-handler"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="pattern_learning_enabled",
        display_name="Pattern Learning (Layer 3)",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.MEMORY_AND_PRIVACY,
        step_order=1,
        tooltip="Enable automatic learning of customer communication patterns.",
        description=(
            "The AI analyses completed conversations to learn customer preferences, "
            "communication style, and common needs. Extracted patterns are stored "
            "with confidence scores and decay over time without reinforcement. "
            "Professional and Enterprise tiers only."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/memory-privacy#layer3",
        affects_agents=["response-generator"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="dedicated_model_enabled",
        display_name="Dedicated Model Training (Layer 4)",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        tier_gate=TierGate.ENTERPRISE_ONLY,
        onboarding_step=OnboardingStep.MEMORY_AND_PRIVACY,
        step_order=2,
        tooltip="Train a dedicated AI model on your customer conversations.",
        description=(
            "After 1,000+ conversations, a dedicated GPT-4o-mini model is "
            "fine-tuned on your data for maximum personalization. Includes "
            "monthly retraining pipeline with quality gates and A/B validation. "
            "Enterprise add-on ($299/mo). The Critic still validates all outputs."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/memory-privacy#layer4",
        affects_agents=["response-generator"],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="data_retention_days",
        display_name="Conversation Data Retention",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=30,
            max_value=730,  # 2 years max
        ),
        platform_default=365,
        tier_defaults={
            TenantTier.STARTER.value: 90,
            TenantTier.PROFESSIONAL.value: 365,
            TenantTier.ENTERPRISE.value: 730,
        },
        onboarding_step=OnboardingStep.MEMORY_AND_PRIVACY,
        step_order=3,
        tooltip="How long conversation data is retained in hot storage.",
        description=(
            "Conversations older than this are archived to warm/cold storage. "
            "Affects Layer 2 (conversation history search depth). Tier defaults "
            "reflect the included history depth. GDPR data deletion requests "
            "override this setting."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/memory-privacy#retention",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="consent_collection_enabled",
        display_name="Collect Customer Consent",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.MEMORY_AND_PRIVACY,
        step_order=4,
        tooltip="Ask customers for consent before using their data for memory.",
        description=(
            "When enabled, customers are asked for consent before their data is "
            "used for Layers 2-4 of Persistent Customer Memory. Required for "
            "GDPR compliance in the EU. Layer 1 (basic profile from Shopify) "
            "operates under legitimate interest basis and does not require "
            "separate consent."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/memory-privacy#consent",
        affects_agents=["response-generator"],
    ))

    # ===================================================================
    # Step 9: Review & Launch (no configurable fields — summary step)
    # This step shows a review of all configured settings.
    # No fields are defined here.
    # ===================================================================

    # ===================================================================
    # Advanced settings (not part of onboarding, accessible post-setup)
    # Mapped to Step 9 (Review & Launch) for schema completeness.
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="custom_instructions",
        display_name="Custom AI Instructions",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_CUSTOM_INSTRUCTIONS_LENGTH,
        ),
        platform_default=None,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.REVIEW_AND_LAUNCH,
        step_order=0,
        tooltip="Advanced: free-form instructions appended to the AI's system prompt.",
        description=(
            "Custom instructions are injected into the Response Generator's "
            "system prompt. They are advisory — platform safety rules and the "
            "Critic always take precedence. Use for domain-specific guidance "
            "the structured fields don't cover. Professional and Enterprise only."
        ),
        placeholder="e.g. Always mention our loyalty program when discussing returns.",
        doc_link=f"{DOCS_BASE_URL}/configuration/advanced#custom-instructions",
        affects_agents=["response-generator"],
        injected_in_prompt=True,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="test_mode_enabled",
        display_name="Test Mode",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.REVIEW_AND_LAUNCH,
        step_order=1,
        tooltip="Enable test mode — conversations are not billed.",
        description=(
            "When test mode is active, conversations are prefixed with 'test_' "
            "and excluded from billing. Use this to verify your configuration "
            "before going live. Test conversations still flow through the full "
            "pipeline including the Critic."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/advanced#test-mode",
        affects_agents=[],
    ))

    # Build registry dict
    registry: dict[str, ConfigFieldDefinition] = {}
    for field in fields:
        if field.field_name in registry:
            raise ValueError(
                f"Duplicate field_name in config schema: {field.field_name}"
            )
        registry[field.field_name] = field

    return registry


# ---------------------------------------------------------------------------
# Supported languages (ISO 639-1 codes)
# ---------------------------------------------------------------------------

_SUPPORTED_LANGUAGES: list[str] = [
    "en",     # English
    "es",     # Spanish
    "fr",     # French
    "pt",     # Portuguese
    "de",     # German
    "it",     # Italian
    "nl",     # Dutch
    "ja",     # Japanese
    "ko",     # Korean
    "zh",     # Chinese (Simplified)
    "zh-TW",  # Chinese (Traditional)
    "ar",     # Arabic
    "hi",     # Hindi
    "ru",     # Russian
    "pl",     # Polish
    "tr",     # Turkish
    "sv",     # Swedish
    "da",     # Danish
    "no",     # Norwegian
    "fi",     # Finnish
]


# ---------------------------------------------------------------------------
# Config schema registry — module-level singleton
# ---------------------------------------------------------------------------

_field_registry: dict[str, ConfigFieldDefinition] | None = None


def get_field_registry() -> dict[str, ConfigFieldDefinition]:
    """Return the field registry singleton (lazy-built on first call)."""
    global _field_registry  # noqa: PLW0603
    if _field_registry is None:
        _field_registry = _build_field_registry()
        logger.info(
            "TenantConfigSchema: %d fields registered across %d onboarding steps",
            len(_field_registry),
            len(set(f.onboarding_step for f in _field_registry.values())),
        )
    return _field_registry


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------


def get_fields_by_step(step: OnboardingStep) -> list[ConfigFieldDefinition]:
    """Return all fields for a given onboarding step, sorted by step_order."""
    registry = get_field_registry()
    return sorted(
        [f for f in registry.values() if f.onboarding_step == step],
        key=lambda f: f.step_order,
    )


def get_fields_for_tier(tier: TenantTier) -> dict[str, ConfigFieldDefinition]:
    """Return all fields available at the given tier."""
    registry = get_field_registry()
    tier_rank = {
        TenantTier.STARTER: 0,
        TenantTier.PROFESSIONAL: 1,
        TenantTier.ENTERPRISE: 2,
    }
    gate_rank = {
        TierGate.ALL: 0,
        TierGate.PROFESSIONAL_PLUS: 1,
        TierGate.ENTERPRISE_ONLY: 2,
    }
    rank = tier_rank.get(tier, 0)
    return {
        name: field
        for name, field in registry.items()
        if gate_rank.get(field.tier_gate, 0) <= rank
    }


def get_prompt_injected_fields() -> list[ConfigFieldDefinition]:
    """Return fields that are injected into AI system prompts."""
    registry = get_field_registry()
    return [f for f in registry.values() if f.injected_in_prompt]


# ---------------------------------------------------------------------------
# Default resolution — platform → tier → tenant override
# ---------------------------------------------------------------------------


def resolve_defaults(tier: TenantTier) -> dict[str, Any]:
    """Compute the fully resolved defaults for a given tier.

    Inheritance: platform_default → tier_defaults[tier] → (tenant override later).
    This returns the base layer before any tenant-specific overrides.

    Args:
        tier: The subscription tier to resolve defaults for.

    Returns:
        Dict of field_name → default value for every field available at this tier.
    """
    tier_fields = get_fields_for_tier(tier)
    result: dict[str, Any] = {}

    for name, field in tier_fields.items():
        # Tier-specific default takes priority over platform default
        if tier.value in field.tier_defaults:
            result[name] = field.tier_defaults[tier.value]
        else:
            result[name] = field.platform_default

    return result


# ---------------------------------------------------------------------------
# Validation — field-level
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


def validate_field(
    field_name: str,
    value: Any,
    tier: TenantTier,
) -> tuple[bool, str | None, Any]:
    """Validate a single config field value.

    Args:
        field_name: The field to validate.
        value: The proposed value.
        tier: The tenant's tier (for tier gating and tier-specific rules).

    Returns:
        Tuple of (is_valid, error_message_or_none, sanitized_value).
    """
    registry = get_field_registry()

    if field_name not in registry:
        return False, f"Unknown configuration field: {field_name}", None

    field = registry[field_name]

    # Tier gate check
    tier_rank = {TenantTier.STARTER: 0, TenantTier.PROFESSIONAL: 1, TenantTier.ENTERPRISE: 2}
    gate_rank = {TierGate.ALL: 0, TierGate.PROFESSIONAL_PLUS: 1, TierGate.ENTERPRISE_ONLY: 2}
    if gate_rank.get(field.tier_gate, 0) > tier_rank.get(tier, 0):
        return (
            False,
            f"Field '{field_name}' requires {field.tier_gate.value} tier or higher",
            None,
        )

    rules = field.validation

    # Null / None handling
    if value is None:
        if rules.required:
            return False, f"Field '{field_name}' is required", None
        return True, None, None

    # Type-specific validation
    if field.field_type == ConfigFieldType.STRING:
        return _validate_string(field_name, value, rules)

    if field.field_type == ConfigFieldType.TEXT:
        return _validate_string(field_name, value, rules)

    if field.field_type == ConfigFieldType.INTEGER:
        return _validate_integer(field_name, value, rules)

    if field.field_type == ConfigFieldType.FLOAT:
        return _validate_float(field_name, value, rules)

    if field.field_type == ConfigFieldType.BOOLEAN:
        return _validate_boolean(field_name, value)

    if field.field_type == ConfigFieldType.ENUM:
        return _validate_enum(field_name, value, rules)

    if field.field_type == ConfigFieldType.STRING_LIST:
        return _validate_string_list(field_name, value, rules)

    if field.field_type == ConfigFieldType.OBJECT:
        # Object fields are passed through with basic type check
        if not isinstance(value, dict):
            return False, f"Field '{field_name}' must be a JSON object", None
        return True, None, value

    return False, f"Unsupported field type: {field.field_type}", None


def validate_config(
    config: dict[str, Any],
    tier: TenantTier,
) -> ConfigValidationResult:
    """Validate an entire tenant config payload.

    Validates each provided field, checks tier gating, enforces required
    fields, and returns a comprehensive result with sanitized values.

    Args:
        config: Dict of field_name → value to validate.
        tier: The tenant's subscription tier.

    Returns:
        ConfigValidationResult with validation outcomes.
    """
    result = ConfigValidationResult(valid=True)
    registry = get_field_registry()
    tier_fields = get_fields_for_tier(tier)

    for field_name, value in config.items():
        if field_name not in registry:
            result.warnings.append({
                "field_name": field_name,
                "message": f"Unknown field '{field_name}' — ignored",
            })
            continue

        is_valid, error, sanitized = validate_field(field_name, value, tier)

        if not is_valid:
            result.valid = False
            result.errors.append({
                "field_name": field_name,
                "message": error or "Validation failed",
            })
        elif field_name not in tier_fields:
            result.warnings.append({
                "field_name": field_name,
                "message": (
                    f"Field '{field_name}' is not available at "
                    f"{tier.value} tier — ignored"
                ),
            })
        else:
            result.sanitized[field_name] = sanitized

    # Check required fields that are missing from the payload
    for field_name, field in tier_fields.items():
        if field.validation.required and field_name not in config:
            # Only error if there's no platform/tier default
            default = (
                field.tier_defaults.get(tier.value)
                if tier.value in field.tier_defaults
                else field.platform_default
            )
            if default is None:
                result.valid = False
                result.errors.append({
                    "field_name": field_name,
                    "message": f"Required field '{field_name}' is missing",
                })

    return result


# ---------------------------------------------------------------------------
# Type-specific validators
# ---------------------------------------------------------------------------


def _validate_string(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a string field."""
    if not isinstance(value, str):
        return False, f"Field '{field_name}' must be a string", None

    # Strip whitespace
    sanitized = value.strip()

    if rules.min_length is not None and len(sanitized) < rules.min_length:
        return (
            False,
            f"Field '{field_name}' must be at least {rules.min_length} characters",
            None,
        )

    if rules.max_length is not None and len(sanitized) > rules.max_length:
        return (
            False,
            f"Field '{field_name}' must be at most {rules.max_length} characters",
            None,
        )

    if rules.pattern is not None:
        if not re.match(rules.pattern, sanitized):
            return (
                False,
                f"Field '{field_name}' does not match required format",
                None,
            )

    return True, None, sanitized


def _validate_integer(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate an integer field."""
    if isinstance(value, bool):
        return False, f"Field '{field_name}' must be an integer", None
    if not isinstance(value, int):
        return False, f"Field '{field_name}' must be an integer", None

    if rules.min_value is not None and value < rules.min_value:
        return (
            False,
            f"Field '{field_name}' must be >= {rules.min_value}",
            None,
        )

    if rules.max_value is not None and value > rules.max_value:
        return (
            False,
            f"Field '{field_name}' must be <= {rules.max_value}",
            None,
        )

    return True, None, value


def _validate_float(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a float field."""
    if isinstance(value, bool):
        return False, f"Field '{field_name}' must be a number", None
    if not isinstance(value, (int, float)):
        return False, f"Field '{field_name}' must be a number", None

    num = float(value)

    if rules.min_value is not None and num < rules.min_value:
        return (
            False,
            f"Field '{field_name}' must be >= {rules.min_value}",
            None,
        )

    if rules.max_value is not None and num > rules.max_value:
        return (
            False,
            f"Field '{field_name}' must be <= {rules.max_value}",
            None,
        )

    return True, None, num


def _validate_boolean(
    field_name: str,
    value: Any,
) -> tuple[bool, str | None, Any]:
    """Validate a boolean field."""
    if not isinstance(value, bool):
        return False, f"Field '{field_name}' must be a boolean", None
    return True, None, value


def _validate_enum(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate an enum field."""
    if not isinstance(value, str):
        return False, f"Field '{field_name}' must be a string", None

    sanitized = value.strip().lower()

    if rules.allowed_values and sanitized not in rules.allowed_values:
        allowed = ", ".join(rules.allowed_values)
        return (
            False,
            f"Field '{field_name}' must be one of: {allowed}",
            None,
        )

    return True, None, sanitized


def _validate_string_list(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a string list field."""
    if not isinstance(value, list):
        return False, f"Field '{field_name}' must be a list", None

    if rules.max_items is not None and len(value) > rules.max_items:
        return (
            False,
            f"Field '{field_name}' can have at most {rules.max_items} items",
            None,
        )

    sanitized: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            return (
                False,
                f"Field '{field_name}[{i}]' must be a string",
                None,
            )
        stripped = item.strip()
        if not stripped:
            continue  # Skip empty strings

        if rules.max_length is not None and len(stripped) > rules.max_length:
            return (
                False,
                f"Field '{field_name}[{i}]' exceeds max length of {rules.max_length}",
                None,
            )

        # If allowed_values is set, validate each item
        if rules.allowed_values and stripped.lower() not in rules.allowed_values:
            allowed = ", ".join(rules.allowed_values[:10])
            return (
                False,
                f"Field '{field_name}[{i}]' ({stripped}) is not a valid option. "
                f"Valid: {allowed}",
                None,
            )

        sanitized.append(stripped)

    return True, None, sanitized


# ---------------------------------------------------------------------------
# Schema export — for API metadata responses
# ---------------------------------------------------------------------------


def export_schema_for_api(tier: TenantTier) -> dict[str, Any]:
    """Export the config schema as a JSON-serializable structure for API responses.

    Used by the Configuration API (#65) to return field metadata so that
    clients (including the future Merchant UI) can render forms dynamically.

    Args:
        tier: The tenant's tier (filters fields by tier gate).

    Returns:
        Dict with steps, fields (tier-filtered), and defaults.
    """
    tier_fields = get_fields_for_tier(tier)
    defaults = resolve_defaults(tier)

    steps: list[dict[str, Any]] = []
    for step in OnboardingStep:
        step_fields = get_fields_by_step(step)
        # Filter to fields available at this tier
        available = [f for f in step_fields if f.field_name in tier_fields]
        if not available:
            continue

        steps.append({
            "step_number": step.value,
            "step_name": step.name.lower().replace("_", " ").title(),
            "fields": [
                {
                    "field_name": f.field_name,
                    "display_name": f.display_name,
                    "field_type": f.field_type.value,
                    "default": defaults.get(f.field_name),
                    "validation": {
                        k: v
                        for k, v in f.validation.model_dump().items()
                        if v is not None
                    },
                    "tooltip": f.tooltip,
                    "description": f.description,
                    "placeholder": f.placeholder,
                    "doc_link": f.doc_link,
                    "affects_agents": f.affects_agents,
                    "injected_in_prompt": f.injected_in_prompt,
                    "tier_gate": f.tier_gate.value,
                }
                for f in available
            ],
        })

    return {
        "tier": tier.value,
        "total_fields": len(tier_fields),
        "steps": steps,
    }
