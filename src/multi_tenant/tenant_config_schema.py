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
    """10-step merchant onboarding workflow (Decision #22 + Tidio parity).

    Steps 1-8: AI behavior and business configuration (original).
    Step 9: Widget appearance and behavior (new — Tidio parity).
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
        display_name="Brand name",
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
        display_name="Brand voice",
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
        display_name="Greeting message",
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
        display_name="Farewell message",
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
        display_name="Primary language",
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
        display_name="Additional languages",
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
        display_name="Auto-detect language",
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
        display_name="Response length",
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
        display_name="Formality level",
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
        display_name="Emoji usage",
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
        display_name="Fallback message",
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
        display_name="Knowledge scope",
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
        display_name="Product recommendations",
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
        display_name="Out of stock behavior",
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

    # --- Retrieval tuning (RAG Phase 1) ---

    fields.append(ConfigFieldDefinition(
        field_name="retrieval_top_k",
        display_name="Results to retrieve",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(min_value=1, max_value=20),
        platform_default=5,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=3,
        tooltip="How many knowledge base results the AI considers per query.",
        description=(
            "Higher values give the AI more context to draw from but may "
            "include less relevant results. Lower values focus on the most "
            "relevant matches. Default: 5."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#retrieval-tuning",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=False,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="retrieval_vector_weight",
        display_name="Semantic search weight",
        field_type=ConfigFieldType.FLOAT,
        validation=ValidationRule(min_value=0.0, max_value=1.0),
        platform_default=0.7,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=4,
        tooltip="How much to weight meaning-based search vs keyword matching.",
        description=(
            "Controls the balance between semantic similarity (understands "
            "meaning) and keyword matching (exact words). Higher values "
            "favor semantic understanding. Default: 0.7 (70% semantic)."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#retrieval-tuning",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=False,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="retrieval_bm25_weight",
        display_name="Keyword match weight",
        field_type=ConfigFieldType.FLOAT,
        validation=ValidationRule(min_value=0.0, max_value=1.0),
        platform_default=0.3,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=5,
        tooltip="How much to weight keyword matching in search results.",
        description=(
            "Complements semantic search weight. Higher values favor exact "
            "keyword matches. Useful when your knowledge base uses specific "
            "terminology customers search for. Default: 0.3 (30% keywords)."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#retrieval-tuning",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=False,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="retrieval_min_score",
        display_name="Minimum relevance score",
        field_type=ConfigFieldType.FLOAT,
        validation=ValidationRule(min_value=0.0, max_value=1.0),
        platform_default=0.1,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=6,
        tooltip="Minimum relevance score for a result to be included.",
        description=(
            "Results below this threshold are discarded. Higher values "
            "mean stricter filtering — the AI only uses highly relevant "
            "content. Lower values include more results but may reduce "
            "answer precision. Default: 0.1."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#retrieval-tuning",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=False,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="cite_sources_in_response",
        display_name="Cite sources in responses",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=7,
        tooltip="Append source article titles to AI responses.",
        description=(
            "When enabled, the AI appends a 'Sources:' line to its "
            "responses listing the knowledge base articles it referenced. "
            "Helps customers verify information and builds trust."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#source-citation",
        affects_agents=["response-generator"],
        injected_in_prompt=False,
    ))

    fields.append(ConfigFieldDefinition(
        field_name="intent_source_mapping",
        display_name="Intent-to-source routing",
        field_type=ConfigFieldType.OBJECT,
        validation=ValidationRule(),
        platform_default=None,
        onboarding_step=OnboardingStep.KNOWLEDGE_BASE,
        step_order=8,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        tooltip="Route specific question types to specific knowledge sources.",
        description=(
            "Maps customer intent categories to knowledge base entry types. "
            "For example: {\"refund\": \"policy\", \"product_info\": \"product\"}. "
            "When set, the AI only searches the specified source type for "
            "that intent, improving relevance. Leave empty for automatic routing."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/knowledge-base#intent-routing",
        affects_agents=["knowledge-retrieval"],
        injected_in_prompt=False,
    ))

    # ===================================================================
    # Step 5: Business Policies
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="return_policy",
        display_name="Return policy",
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
        display_name="Shipping information",
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
        display_name="Warranty information",
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
        display_name="Support hours",
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
        display_name="Additional policies",
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
        display_name="Escalation threshold",
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
        display_name="Escalation keywords",
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
        display_name="Escalation notification email",
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
        display_name="Max AI turns before escalation",
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
        display_name="Shopify product sync",
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
        display_name="Zendesk ticket creation",
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
        display_name="Mailchimp segment sync",
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
        display_name="Google Analytics export",
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
        display_name="Conversation memory",
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
        display_name="Pattern learning (Layer 3)",
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
        display_name="Dedicated model training (Layer 4)",
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
        display_name="Conversation data retention",
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
        display_name="Collect customer consent",
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
    # Step 9: Widget Appearance (Tidio parity — 22 controls)
    #
    # These fields control the chat widget's visual appearance and
    # interactive behavior on the merchant's storefront. None are
    # injected into AI prompts — they are consumed by the widget
    # frontend (Preact) and the widget configurator admin UI.
    #
    # Reference: Tidio competitive audit (2026-02-01).
    # Architecture: Decision UI-2 (Theme App Extension), UI-3 (Shadow DOM).
    # ===================================================================

    # --- 9A: Visual controls ---

    fields.append(ConfigFieldDefinition(
        field_name="widget_primary_color",
        display_name="Widget color",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            pattern=HEX_COLOR_PATTERN,
        ),
        platform_default="#ff3621",  # Agent Red brand primary
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=0,
        tooltip="The primary color of your chat widget (header, send button, customer message bubbles).",
        description=(
            "Controls the widget header background, send button, and outgoing "
            "customer message bubble color. Use your brand color for consistency. "
            "Ensure sufficient contrast against white text (WCAG AA)."
        ),
        placeholder="#ff3621",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#color",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_background_color",
        display_name="Widget background",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            pattern=HEX_COLOR_PATTERN,
        ),
        platform_default="#FFFFFF",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=1,
        tooltip="Background color of the conversation panel.",
        description=(
            "The background color of the chat conversation area. White is "
            "recommended for readability. Dark mode uses a separate toggle."
        ),
        placeholder="#FFFFFF",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#background",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_position",
        display_name="Widget position",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["bottom-right", "bottom-left"],
        ),
        platform_default="bottom-right",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=2,
        tooltip="Which corner of the screen the chat launcher appears in.",
        description=(
            "Bottom-right is standard and expected by most visitors. Use "
            "bottom-left only if your site has a conflicting element in the "
            "bottom-right corner."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#position",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_offset_x",
        display_name="Horizontal offset",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=0,
            max_value=100,
        ),
        platform_default=20,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=3,
        tooltip="Distance from the screen edge in pixels.",
        description=(
            "Horizontal distance from the left or right edge (depending on "
            "widget position). Default 20px. Increase if the launcher overlaps "
            "other elements on your site."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#offset",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_offset_y",
        display_name="Vertical offset",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=0,
            max_value=100,
        ),
        platform_default=20,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=4,
        tooltip="Distance from the bottom of the screen in pixels.",
        description=(
            "Vertical distance from the bottom edge. Default 20px. Increase "
            "if the launcher overlaps a sticky footer or cookie banner."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#offset",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_agent_avatar_url",
        display_name="Agent avatar",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=500,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=5,
        tooltip="URL of the avatar image shown in the widget header and message bubbles.",
        description=(
            "Upload a square image (recommended 200×200px) through the Widget "
            "Configurator. The URL is stored here after upload. If blank, a "
            "default Agent Red avatar is shown. Supported formats: PNG, JPG, WebP."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#avatar",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_agent_display_name",
        display_name="Agent display name",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=MAX_AGENT_DISPLAY_NAME_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=6,
        tooltip="Name shown in the widget header and message bubbles.",
        description=(
            "The name displayed as the AI agent's identity in conversations. "
            "If blank, falls back to your brand name. Keep it short and "
            "friendly (e.g. 'Support', 'Amy', 'Help Desk')."
        ),
        placeholder="e.g. Support, Amy, Help Desk",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#agent-name",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_agent_title",
        display_name="Agent title",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=MAX_AGENT_TITLE_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=7,
        tooltip="Optional subtitle shown below the agent name (e.g. 'Customer Support').",
        description=(
            "A secondary label shown beneath the agent display name in the "
            "widget header. Optional. Examples: 'Customer Support', "
            "'AI Assistant', 'Here to help'."
        ),
        placeholder="e.g. Customer Support",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#agent-title",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_logo_url",
        display_name="Widget logo",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=500,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=8,
        tooltip="URL of your company logo displayed in the widget header.",
        description=(
            "Upload your company logo through the Widget Configurator. "
            "Recommended dimensions: 120×40px (landscape). Displayed in the "
            "widget header area alongside the agent name. If blank, only the "
            "agent name and avatar are shown."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#logo",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_show_branding",
        display_name="Show 'Powered by Agent Red'",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=9,
        tooltip="Display 'Powered by Agent Red' badge in the widget footer.",
        description=(
            "Professional and Enterprise tiers can remove the Agent Red branding "
            "badge from the widget footer. Starter tier always shows branding."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#branding",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_mobile_enabled",
        display_name="Show on mobile",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=10,
        tooltip="Whether to show the chat widget on mobile devices.",
        description=(
            "When disabled, the widget launcher and conversation panel are "
            "hidden on screens narrower than 768px. Useful if you have a "
            "dedicated mobile app or mobile-specific support channel."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#mobile",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_dark_mode",
        display_name="Dark mode",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=11,
        tooltip="Use a dark color scheme for the widget.",
        description=(
            "When enabled, the widget uses a dark background with light text. "
            "Your primary color is still used for accents and buttons. "
            "Dark mode is not available in most competing products."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#dark-mode",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_color_mode",
        display_name="Color mode",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["light", "dark", "auto"],
        ),
        platform_default="auto",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=24,
        tooltip="Widget color scheme: light, dark, or auto (follows visitor's OS preference).",
        description=(
            "Controls the overall color scheme. 'auto' detects the visitor's OS "
            "dark mode preference. Supersedes the Dark Mode toggle when set to "
            "'light' or 'dark'."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#color-mode",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_header_gradient_end",
        display_name="Header gradient end color",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            pattern=r"^#[0-9A-Fa-f]{6}$",
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=25,
        tooltip="End color for the header gradient. Start color is your primary color.",
        description=(
            "Creates a linear gradient from your primary color to this color "
            "in the widget header. Leave blank for a solid primary color header."
        ),
        placeholder="#8B1520",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#header-gradient",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_font_family",
        display_name="Font family",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=200,
        ),
        platform_default="Inter, system-ui, sans-serif",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=26,
        tooltip="CSS font-family for widget text.",
        description=(
            "The font stack used in the widget. Defaults to Inter. "
            "Use any web-safe font or Google Font that is loaded on your storefront."
        ),
        placeholder="Inter, system-ui, sans-serif",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#font",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_border_radius",
        display_name="Border radius",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=0,
            max_value=32,
        ),
        platform_default=8,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=27,
        tooltip="Corner rounding for the widget panel and inputs (px).",
        description=(
            "Controls how rounded corners are on the widget panel, input fields, "
            "and message bubbles. 0 = square corners, 16 = very rounded."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#border-radius",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_launcher_size",
        display_name="Launcher button size",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=40,
            max_value=80,
        ),
        platform_default=60,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=28,
        tooltip="Diameter of the floating launcher button (px).",
        description=(
            "The size of the circular chat button in the corner of the page. "
            "40px = compact, 60px = standard, 80px = large."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#launcher-size",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_launcher_icon",
        display_name="Launcher icon",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["chat", "headset", "help", "custom"],
        ),
        platform_default="chat",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=29,
        tooltip="Icon displayed on the launcher button.",
        description=(
            "The icon inside the floating launcher button. "
            "'chat' = speech bubble, 'headset' = support headset, "
            "'help' = question mark, 'custom' = use your logo."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#launcher-icon",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_header_title",
        display_name="Header title",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=100,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=30,
        tooltip="Title text displayed in the widget header.",
        description=(
            "The main title shown at the top of the chat panel. "
            "If blank, defaults to 'Support' or your agent display name."
        ),
        placeholder="e.g. Support, Chat with us",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#header-title",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_header_subtitle",
        display_name="Header subtitle",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=200,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=31,
        tooltip="Subtitle text below the header title.",
        description=(
            "A short description shown below the header title. "
            "Use it to set response time expectations."
        ),
        placeholder="e.g. We typically reply within minutes",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#header-subtitle",
        affects_agents=[],
    ))

    # --- 9B: Behavior controls ---

    fields.append(ConfigFieldDefinition(
        field_name="widget_greeting_enabled",
        display_name="Greeting message",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=32,
        tooltip="Show a greeting message when the widget opens.",
        description=(
            "When enabled, a welcome message appears at the top of the "
            "conversation when the visitor opens the chat widget."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#greeting",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_greeting_message",
        display_name="Greeting text",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=500,
        ),
        platform_default="Hi there! How can I help you today?",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=33,
        tooltip="The greeting text displayed when chat opens.",
        description=(
            "Customize the welcome message visitors see. "
            "Supports template variables: {{brand_name}}, {{agent_name}}."
        ),
        placeholder="e.g. Hi there! How can I help you today?",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#greeting-text",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_pre_chat_form_enabled",
        display_name="Pre-chat form",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=34,
        tooltip="Collect visitor info before starting a conversation.",
        description=(
            "When enabled, visitors must fill in selected fields (name, email, "
            "phone, etc.) before they can start chatting."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#pre-chat-form",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_pre_chat_fields",
        display_name="Pre-chat form fields",
        field_type=ConfigFieldType.STRING_LIST,
        validation=ValidationRule(
            max_items=6,
            allowed_values=["name", "email", "phone", "company", "order_number", "subject"],
        ),
        platform_default=[],
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=35,
        tooltip="Which fields to show in the pre-chat form.",
        description=(
            "Select the fields visitors must complete before chatting. "
            "'name' and 'email' are most common."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#pre-chat-fields",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_offline_form_enabled",
        display_name="Offline contact form",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=36,
        tooltip="Show a leave-a-message form when all agents are offline.",
        description=(
            "When enabled and all human agents are offline, visitors can "
            "leave a message with their email for follow-up."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#offline-form",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_offline_message",
        display_name="Offline message",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_OFFLINE_MESSAGE_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=12,
        tooltip="Message displayed when your support team is offline.",
        description=(
            "Shown when all human agents are offline (outside operating hours). "
            "The AI agent remains available 24/7. This message appears alongside "
            "the AI chat to set expectations about human response times. "
            "Leave blank to use the default: 'Our team is currently offline. "
            "Our AI assistant is available to help you now.'"
        ),
        placeholder="e.g. Our team is offline, but our AI assistant is here to help!",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#offline",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_auto_open",
        display_name="Auto-open widget",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=13,
        tooltip="Automatically open the widget after a delay.",
        description=(
            "When enabled, the widget opens automatically after the visitor "
            "has been on the page for the configured delay period. Use "
            "sparingly — auto-opening can feel intrusive if overused."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#auto-open",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_auto_open_delay",
        display_name="Auto-open delay (seconds)",
        field_type=ConfigFieldType.INTEGER,
        validation=ValidationRule(
            min_value=1,
            max_value=AUTO_OPEN_MAX_DELAY,
        ),
        platform_default=5,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=14,
        tooltip="Seconds to wait before auto-opening the widget.",
        description=(
            "Only applies when Auto-Open Widget is enabled. The widget "
            "opens after this many seconds on the page. Recommended: "
            "3-10 seconds. Longer delays feel less intrusive."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#auto-open",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_operating_hours",
        display_name="Operating hours",
        field_type=ConfigFieldType.OBJECT,
        validation=ValidationRule(),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=15,
        tooltip="Your team's business hours schedule.",
        description=(
            "Structured schedule with per-day time ranges and timezone. "
            "Format: {timezone: 'America/New_York', schedule: {monday: "
            "[{start: '09:00', end: '17:00'}], ...}}. When set, the widget "
            "shows an online/offline indicator. Leave blank for 'always available'."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#hours",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_offline_behavior",
        display_name="Offline behavior",
        field_type=ConfigFieldType.ENUM,
        validation=ValidationRule(
            allowed_values=["ai_only", "show_form", "hide_widget"],
        ),
        platform_default="ai_only",
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=16,
        tooltip="What happens when your team is offline.",
        description=(
            "AI only: the AI agent handles all conversations (recommended). "
            "Show form: display a 'leave a message' form instead of chat. "
            "Hide widget: hide the widget entirely during offline hours."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#offline-behavior",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_prechat_form",
        display_name="Pre-chat form",
        field_type=ConfigFieldType.OBJECT,
        validation=ValidationRule(),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=17,
        tooltip="Collect visitor information before starting a conversation.",
        description=(
            "When configured, visitors fill in a form before chatting. "
            "Format: {enabled: true, fields: [{name: 'name', label: 'Your Name', "
            "type: 'text', required: true}, {name: 'email', label: 'Email', "
            "type: 'email', required: true}]}. Supports text, email, phone, "
            "and dropdown field types. Maximum 10 fields."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#prechat",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_chat_rating_enabled",
        display_name="Post-chat rating",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=18,
        tooltip="Show a thumbs up/down rating prompt after conversations.",
        description=(
            "When enabled, visitors see a satisfaction prompt after the "
            "conversation ends. Ratings are tracked in the Analytics dashboard. "
            "Negative ratings optionally include a comment field."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#rating",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_sound_enabled",
        display_name="Notification sound",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=19,
        tooltip="Play a sound when a new message arrives.",
        description=(
            "A subtle notification sound plays in the visitor's browser when "
            "a new agent message arrives and the widget is minimized. "
            "Visitors can also mute this from within the widget."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#sound",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_file_upload_enabled",
        display_name="File uploads",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=20,
        tooltip="Allow visitors to attach images and files.",
        description=(
            "When enabled, visitors can attach files (images, PDFs, documents) "
            "to their messages. Maximum file size: 10MB. Supported formats: "
            "PNG, JPG, GIF, PDF, DOC, DOCX, TXT. Disable if file attachments "
            "are not relevant to your support workflow."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#files",
        affects_agents=[],
    ))

    # --- 9C: Content and targeting controls ---

    fields.append(ConfigFieldDefinition(
        field_name="widget_header_text",
        display_name="Widget header text",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=MAX_WIDGET_TITLE_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=21,
        tooltip="Custom title shown at the top of the widget.",
        description=(
            "Replaces the default header text. If blank, defaults to "
            "'Chat with us' or the agent display name. Keep it short "
            "and action-oriented."
        ),
        placeholder="e.g. Chat with us, Need help?, Ask a question",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#header",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_input_placeholder",
        display_name="Input placeholder",
        field_type=ConfigFieldType.STRING,
        validation=ValidationRule(
            max_length=MAX_PLACEHOLDER_TEXT_LENGTH,
        ),
        platform_default=None,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=22,
        tooltip="Placeholder text in the message input field.",
        description=(
            "The grey hint text shown in the empty message input box. "
            "If blank, defaults to 'Type a message...'. Use it to guide "
            "visitors toward productive queries."
        ),
        placeholder="e.g. Type a message..., Ask me anything...",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#placeholder",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_page_rules",
        display_name="Page visibility rules",
        field_type=ConfigFieldType.STRING_LIST,
        validation=ValidationRule(
            max_items=MAX_PAGE_RULES_COUNT,
            max_length=MAX_PAGE_RULE_LENGTH,
        ),
        platform_default=[],
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=23,
        tooltip="Control which pages the widget appears on.",
        description=(
            "List of URL patterns to control widget visibility. "
            "Prefix with '+' to include or '-' to exclude. "
            "Examples: '+/products/*' (show on product pages), "
            "'-/checkout' (hide on checkout), '-/admin/*' (hide on admin). "
            "If empty, the widget appears on all pages."
        ),
        placeholder="e.g. +/products/*, -/checkout, -/admin/*",
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#page-rules",
        affects_agents=[],
    ))

    fields.append(ConfigFieldDefinition(
        field_name="widget_quick_actions_enabled",
        display_name="Quick action buttons",
        field_type=ConfigFieldType.BOOLEAN,
        platform_default=True,
        onboarding_step=OnboardingStep.WIDGET_APPEARANCE,
        step_order=24,
        tooltip="Show contextual quick action prompt buttons in the chat greeting area.",
        description=(
            "When enabled, up to 2 quick action prompt buttons appear below "
            "the greeting message. Buttons are configured in the Quick Actions "
            "section and can be assigned to specific page types (product, "
            "collection, home, etc.) for contextual relevance."
        ),
        doc_link=f"{DOCS_BASE_URL}/configuration/widget-appearance#quick-actions",
        affects_agents=[],
    ))

    # ===================================================================
    # Step 10: Review & Launch (renumbered from 9)
    # This step shows a review of all configured settings.
    # No fields are defined here.
    # ===================================================================

    # ===================================================================
    # Advanced settings (not part of onboarding, accessible post-setup)
    # Mapped to Step 10 (Review & Launch) for schema completeness.
    # ===================================================================

    fields.append(ConfigFieldDefinition(
        field_name="custom_instructions",
        display_name="Custom AI instructions",
        field_type=ConfigFieldType.TEXT,
        validation=ValidationRule(
            max_length=MAX_CUSTOM_INSTRUCTIONS_LENGTH,
        ),
        platform_default=None,
        tier_gate=TierGate.PROFESSIONAL_PLUS,
        onboarding_step=OnboardingStep.REVIEW_AND_LAUNCH,  # Step 10
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
        display_name="Test mode",
        field_type=ConfigFieldType.BOOLEAN,
        validation=ValidationRule(),
        platform_default=False,
        onboarding_step=OnboardingStep.REVIEW_AND_LAUNCH,  # Step 10
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
