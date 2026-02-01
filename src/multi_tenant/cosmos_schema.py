"""
Cosmos DB schema definitions for multi-tenant Agent Red platform.

Defines document models (Pydantic), collection configurations, indexing
policies, and database initialization utilities for all 10 Cosmos DB
collections.

Collections (10 total):
    Tenant-scoped (partition key: /tenant_id):
        1. tenants          — Tenant config, status, billing metadata
        2. conversations    — Conversation transcripts, billing records
        3. usage            — Metered usage counters, pack balances
        4. customer_profiles — Layer 1 structured customer profiles
        5. knowledge_bases  — Per-merchant product/FAQ data
        6. memory_vectors   — Layer 2 vectorized transcript chunks
        7. preferences      — Merchant settings, config versions
        8. team_members     — Merchant team members (admin dashboard access)

    Platform-wide:
        9. platform_config  — Tier defaults, feature flags (partition: /config_type)
       10. audit_log        — Append-only audit events (partition: /time_partition)

Architecture references:
    - Decision #2: Cosmos DB partition key = tenant_id
    - Decision #18: Continuous 7-day backup
    - Decision #13: Append-only audit log (12 event types, 1-year retention)
    - Decision #29: Layer 2 vectorization (DiskANN, 3072 dimensions, cosine)
    - Master Plan Review Section 4: Architecture Decisions Detail

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATABASE_NAME = "agent-red-prod"

# Collection names — used as container IDs in Cosmos DB
COLLECTION_TENANTS = "tenants"
COLLECTION_CONVERSATIONS = "conversations"
COLLECTION_USAGE = "usage"
COLLECTION_CUSTOMER_PROFILES = "customer_profiles"
COLLECTION_KNOWLEDGE_BASES = "knowledge_bases"
COLLECTION_MEMORY_VECTORS = "memory_vectors"
COLLECTION_PREFERENCES = "preferences"
COLLECTION_PLATFORM_CONFIG = "platform_config"
COLLECTION_AUDIT_LOG = "audit_log"
COLLECTION_TEAM_MEMBERS = "team_members"

ALL_COLLECTIONS = [
    COLLECTION_TENANTS,
    COLLECTION_CONVERSATIONS,
    COLLECTION_USAGE,
    COLLECTION_CUSTOMER_PROFILES,
    COLLECTION_KNOWLEDGE_BASES,
    COLLECTION_MEMORY_VECTORS,
    COLLECTION_PREFERENCES,
    COLLECTION_PLATFORM_CONFIG,
    COLLECTION_AUDIT_LOG,
    COLLECTION_TEAM_MEMBERS,
]

# Cosmos DB Serverless — no provisioned throughput (pay per RU consumed)
# Throughput offer_type is not set; Cosmos DB Serverless auto-scales.

# DiskANN vector index configuration (for memory_vectors collection)
VECTOR_DIMENSIONS = 3072  # text-embedding-3-large
VECTOR_SIMILARITY = "cosine"

# TTL values (seconds)
TTL_USAGE_PERIOD = 35 * 24 * 60 * 60       # 35 days (billing period + buffer)
TTL_IDEMPOTENCY = 7 * 24 * 60 * 60         # 7 days for idempotency keys
TTL_AUDIT_LOG = 365 * 24 * 60 * 60         # 1 year (audit log retention)
TTL_PACK_BALANCE = 90 * 24 * 60 * 60       # 90 days (pack validity)


# ---------------------------------------------------------------------------
# Shared enums (re-exported for consistency across multi-tenant code)
# ---------------------------------------------------------------------------


class TenantTier(str, Enum):
    """Subscription tier."""

    TRIAL = "trial"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    """Lifecycle status of a tenant.

    Mirrors src.integrations.provisioning.TenantStatus to maintain
    backward compatibility while the in-memory store is migrated.
    """

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    GRACE_PERIOD = "grace_period"
    DEACTIVATED = "deactivated"
    TRIAL_EXPIRED = "trial_expired"


class BillingChannel(str, Enum):
    """Billing channel through which the customer subscribes."""

    STRIPE = "stripe"
    SHOPIFY = "shopify"
    TRIAL = "trial"


class ConsentStatus(str, Enum):
    """GDPR consent status for Persistent Customer Memory (Decision #10)."""

    GRANTED = "granted"
    DENIED = "denied"
    NOT_ASKED = "not_asked"


class ConversationStatus(str, Enum):
    """Conversation lifecycle status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    TIMED_OUT = "timed_out"
    ERROR = "error"


class AuditEventType(str, Enum):
    """Audit log event types (Decision #13 — 12 event types)."""

    TENANT_CREATED = "tenant.created"
    TENANT_ACTIVATED = "tenant.activated"
    TENANT_UPDATED = "tenant.updated"
    TENANT_DEACTIVATED = "tenant.deactivated"
    TENANT_DELETED = "tenant.deleted"
    SUBSCRIPTION_CHANGED = "subscription.changed"
    CONFIG_UPDATED = "config.updated"
    DATA_EXPORTED = "data.exported"
    DATA_DELETED = "data.deleted"
    CONSENT_CHANGED = "consent.changed"
    ESCALATION_TRIGGERED = "escalation.triggered"
    SECURITY_EVENT = "security.event"


class PiiClassification(str, Enum):
    """PII classification for fields (Decision #7 — PII scrubbing)."""

    NONE = "none"             # No PII (safe to log)
    DIRECT = "direct"         # Directly identifies a person (email, name)
    INDIRECT = "indirect"     # Could identify with other data (IP, device)
    SENSITIVE = "sensitive"   # Special category (health, financial)


# ---------------------------------------------------------------------------
# Document models — Collection 1: tenants
# ---------------------------------------------------------------------------


class TenantDocument(BaseModel):
    """Tenant record stored in the 'tenants' collection.

    This is the single source of truth for tenant status, billing,
    and configuration metadata. Replaces the in-memory _tenants dict
    in src/integrations/provisioning.py.

    Partition key: /tenant_id
    """

    # Cosmos DB system fields
    id: str = Field(description="Document ID (= tenant_id)")
    tenant_id: str = Field(description="Partition key — unique tenant identifier (UUID)")

    # Lifecycle
    status: TenantStatus = Field(description="Current lifecycle status")
    billing_channel: BillingChannel = Field(description="stripe or shopify")

    # Tier & plan
    tier: TenantTier | None = Field(default=None, description="Subscription tier")
    interval: str | None = Field(default=None, description="Billing interval: month or year")
    addons: list[str] = Field(default_factory=list, description="Active add-on IDs")

    # Channel-specific identifiers (PII: indirect)
    stripe_customer_id: str | None = Field(default=None, description="Stripe cus_...")
    stripe_subscription_id: str | None = Field(default=None, description="Stripe sub_...")
    shopify_shop_domain: str | None = Field(default=None, description="*.myshopify.com")
    shopify_subscription_id: str | None = Field(default=None, description="Shopify gid://...")

    # Contact (PII: direct)
    customer_email: str | None = Field(default=None, description="Primary contact email")

    # GDPR consent (Decision #10)
    consent_status: ConsentStatus = Field(
        default=ConsentStatus.NOT_ASKED,
        description="Consent for Persistent Customer Memory Layers 2-4",
    )

    # API key authentication (Decision #4)
    api_key_hash: str | None = Field(
        default=None,
        description="SHA-256 hash of the tenant's API key (for direct-channel auth)",
    )

    # Publishable widget key authentication (Decision UI-6)
    widget_key_hash: str | None = Field(
        default=None,
        description="SHA-256 hash of the tenant's publishable widget key (pk_live_...)",
    )

    # Trial tier (WI #119)
    trial_expires_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when the trial period ends. "
        "Only set for trial-tier tenants. Auth middleware rejects requests "
        "after this time.",
    )
    trial_conversation_limit: int | None = Field(
        default=None,
        description="Hard cap on conversations during the trial period. "
        "Overrides included_conversations from TIER_DEFAULTS when set.",
    )

    # Rate limiting (Decision #5)
    rate_limit_rpm: int | None = Field(
        default=None,
        description="Per-tenant rate limit (requests/min). None = use tier default.",
    )
    max_concurrent: int | None = Field(
        default=None,
        description="Per-tenant concurrency limit. None = use tier default.",
    )

    # Timestamps (ISO 8601)
    created_at: str = Field(description="When tenant was provisioned")
    updated_at: str = Field(description="Last status change")
    deactivated_at: str | None = Field(default=None, description="When cancellation began")
    grace_period_ends_at: str | None = Field(default=None, description="When data will be deleted")


# ---------------------------------------------------------------------------
# Document models — Collection 2: conversations
# ---------------------------------------------------------------------------


class ConversationDocument(BaseModel):
    """Conversation record stored in the 'conversations' collection.

    One document per conversation. Contains the transcript and billing
    metadata needed by the ConversationMeter (Work Items #71-72).

    Partition key: /tenant_id
    Unique key: /conversation_id within a partition
    """

    id: str = Field(description="Document ID (= conversation_id)")
    tenant_id: str = Field(description="Partition key")
    conversation_id: str = Field(description="Unique conversation identifier")

    # Conversation lifecycle
    status: ConversationStatus = Field(description="Current conversation status")
    customer_id: str | None = Field(default=None, description="End-customer identifier (tokenized)")

    # Billing (Decision #24 — billable conversation definition)
    is_billable: bool = Field(default=True, description="Whether this conversation counts for billing")
    message_count: int = Field(default=0, description="Total messages in conversation")
    turn_count: int = Field(default=0, description="Customer-AI turn pairs")

    # Pipeline trace (Decision #28+ — explainability)
    agents_invoked: list[str] = Field(default_factory=list, description="Agents used in pipeline")
    model_used: str | None = Field(default=None, description="Primary model (e.g. gpt-4o)")
    critic_passed: bool | None = Field(default=None, description="Whether Critic approved response")

    # Human agent assignment (WI #171 — admin inbox)
    assigned_to: str | None = Field(default=None, description="Human agent ID (post-escalation)")
    internal_notes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Internal merchant notes [{author, content, created_at}]",
    )

    # Transcript (stored as structured messages, not raw text)
    messages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Conversation messages [{role, content, timestamp}]",
    )

    # Timestamps
    started_at: str = Field(description="First customer message timestamp")
    ended_at: str | None = Field(default=None, description="Conversation end timestamp")
    last_activity_at: str = Field(description="Last message timestamp (for idle timeout)")

    # TTL — no default TTL; conversations persist in hot storage until
    # archival pipeline moves them to warm/cold tiers (Decision #18+).
    ttl: int | None = Field(default=None, alias="_ts_ttl", description="Cosmos DB TTL (seconds)")


# ---------------------------------------------------------------------------
# Document models — Collection 3: usage
# ---------------------------------------------------------------------------


class UsageCounterDocument(BaseModel):
    """Usage counter for a tenant's billing period.

    Replaces the in-memory _usage_counters dict in stripe_usage.py.
    One document per tenant per billing period.

    Partition key: /tenant_id
    Unique key: /billing_period within a partition
    """

    id: str = Field(description="Document ID (= tenant_id:billing_period)")
    tenant_id: str = Field(description="Partition key")
    billing_period: str = Field(description="Billing period identifier (e.g. 2026-02)")

    # Counters (atomic increments via Cosmos DB patch operations)
    total_conversations: int = Field(default=0, description="All conversations this period")
    overage_reported: int = Field(default=0, description="Conversations reported to Stripe Meter")
    pack_consumed: int = Field(default=0, description="Conversations absorbed by pack balance")

    # Tier snapshot (for included allowance calculation)
    tier: TenantTier | None = Field(default=None, description="Tier at period start")
    included_allowance: int = Field(default=0, description="Included conversations for this tier")

    # Reconciliation
    last_reconciled_at: str | None = Field(default=None, description="Last Stripe reconciliation")
    stripe_meter_total: int | None = Field(default=None, description="Stripe's meter count (for reconciliation)")

    # TTL — auto-expire after billing period + buffer
    ttl: int = Field(default=TTL_USAGE_PERIOD, alias="_ts_ttl")


class PackBalanceDocument(BaseModel):
    """Individual conversation pack balance.

    Replaces the in-memory _pack_balances list in stripe_packs.py.
    One document per pack purchase. Consumed FIFO (oldest first).

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (= pack purchase ID)")
    tenant_id: str = Field(description="Partition key")
    stripe_customer_id: str = Field(description="Stripe customer who purchased")

    pack_id: str = Field(description="Pack identifier: pack_1k, pack_5k, pack_20k")
    conversations_purchased: int = Field(description="Original pack size")
    remaining: int = Field(description="Conversations remaining")

    purchased_at: str = Field(description="Purchase timestamp (ISO 8601)")
    expires_at: str = Field(description="Expiry timestamp (ISO 8601)")

    # TTL — auto-expire at pack validity end
    ttl: int = Field(default=TTL_PACK_BALANCE, alias="_ts_ttl")


class IdempotencyKeyDocument(BaseModel):
    """Idempotency key for webhook deduplication.

    Replaces the in-memory _processed_events set in stripe_webhooks.py.

    Partition key: /tenant_id (or "platform" for platform-wide events)
    """

    id: str = Field(description="Document ID (= event ID)")
    tenant_id: str = Field(description="Partition key (tenant_id or 'platform')")
    event_id: str = Field(description="Stripe/Shopify event ID")
    event_type: str = Field(description="Event type (e.g. checkout.session.completed)")
    processed_at: str = Field(description="When the event was processed")

    # TTL — auto-expire after 7 days
    ttl: int = Field(default=TTL_IDEMPOTENCY, alias="_ts_ttl")


# ---------------------------------------------------------------------------
# Document models — Collection 4: customer_profiles
# ---------------------------------------------------------------------------


class CustomerProfileDocument(BaseModel):
    """Layer 1 customer profile (Decision #28).

    Structured profile with 6 data sources, injected into every
    conversation as ~250 tokens of context.

    Partition key: /tenant_id
    Unique key: /customer_id within a partition
    """

    id: str = Field(description="Document ID (= tenant_id:customer_id)")
    tenant_id: str = Field(description="Partition key")
    customer_id: str = Field(description="Tokenized customer identifier")

    # Data source 1: Purchase history
    purchase_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="[{product_id, date, rating, review_snippet}]",
    )

    # Data source 2: Historical product questions
    product_questions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="[{question, product_id, date, resolved}]",
    )

    # Data source 3: Geographic region codes
    region_codes: dict[str, str] = Field(
        default_factory=dict,
        description="{shipping_region, availability_zone, timezone, locale}",
    )

    # Data source 4: Marketing segmentation codes
    marketing_segments: list[str] = Field(
        default_factory=list,
        description="Active marketing segment identifiers",
    )

    # Data source 5: Jurisdiction codes
    jurisdiction_codes: dict[str, str] = Field(
        default_factory=dict,
        description="{country, state, tax_region, regulatory_framework}",
    )

    # Data source 6: Shopping cart contents
    cart_contents: dict[str, Any] = Field(
        default_factory=dict,
        description="{active: [{product_id, qty}], abandoned: [{product_id, qty, abandoned_at}]}",
    )

    # GDPR consent (inherited from tenant, can be overridden per-customer)
    consent_status: ConsentStatus = Field(
        default=ConsentStatus.NOT_ASKED,
        description="Customer-level consent for memory layers",
    )

    # Metadata
    created_at: str = Field(description="Profile creation timestamp")
    updated_at: str = Field(description="Last profile update")
    last_interaction_at: str | None = Field(default=None, description="Last conversation timestamp")


# ---------------------------------------------------------------------------
# Document models — Collection 5: knowledge_bases
# ---------------------------------------------------------------------------


class KnowledgeBaseDocument(BaseModel):
    """Per-merchant knowledge base entry.

    Stores product data, FAQ content, and policy documents that the
    Knowledge Retrieval agent searches during conversations.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID")
    tenant_id: str = Field(description="Partition key")
    entry_type: str = Field(description="product | faq | policy | custom")

    # Content
    title: str = Field(description="Entry title / product name")
    content: str = Field(description="Full text content for retrieval")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific metadata (e.g. product_id, category, price)",
    )

    # Search optimization
    tags: list[str] = Field(default_factory=list, description="Search tags")
    language: str = Field(default="en", description="Content language (ISO 639-1)")

    # Lifecycle
    is_active: bool = Field(default=True, description="Whether entry is searchable")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


# ---------------------------------------------------------------------------
# Document models — Collection 6: memory_vectors
# ---------------------------------------------------------------------------


class MemoryVectorDocument(BaseModel):
    """Layer 2 vectorized transcript chunk (Decision #29).

    Post-conversation pipeline: transcript -> chunking (200-300 tokens)
    -> PII tokenization -> embedding (text-embedding-3-large, 3072d)
    -> stored here with DiskANN vector index.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (= chunk ID)")
    tenant_id: str = Field(description="Partition key")
    customer_id: str = Field(description="Tokenized customer identifier")
    conversation_id: str = Field(description="Source conversation ID")

    # Chunk content
    chunk_text: str = Field(description="PII-tokenized chunk text (200-300 tokens)")
    chunk_index: int = Field(description="Position within conversation transcript")

    # Vector embedding (3072 dimensions, text-embedding-3-large)
    embedding: list[float] = Field(description="3072-dimensional embedding vector")

    # Metadata for search filtering
    language: str = Field(default="en", description="Chunk language")
    topics: list[str] = Field(default_factory=list, description="Extracted topics for filtering")

    # Timestamps
    created_at: str = Field(description="When chunk was vectorized")
    conversation_date: str = Field(description="When the source conversation occurred")


# ---------------------------------------------------------------------------
# Document models — Collection 7: preferences
# ---------------------------------------------------------------------------


class PreferencesDocument(BaseModel):
    """Merchant configuration and preferences (Decision #22).

    Stores per-tenant configuration with version history. The
    TenantConfigProcessor validates and cleanses config changes
    before persisting here.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (= tenant_id:version)")
    tenant_id: str = Field(description="Partition key")
    version: int = Field(description="Config version number (monotonically increasing)")
    is_current: bool = Field(default=True, description="Whether this is the active config version")

    # Brand & tone (onboarding step 1)
    brand_name: str | None = Field(default=None, description="Merchant's brand display name")
    brand_voice: str | None = Field(default=None, description="Tone descriptor (e.g. friendly, formal)")

    # Languages (onboarding step 2)
    primary_language: str = Field(default="en", description="Primary support language")
    additional_languages: list[str] = Field(default_factory=list, description="Additional languages")

    # Response style (onboarding step 3)
    response_length: str | None = Field(default=None, description="concise | standard | detailed")
    formality_level: str | None = Field(default=None, description="casual | balanced | formal")

    # Business policies (onboarding step 5)
    return_policy: str | None = Field(default=None, description="Return policy summary for AI context")
    shipping_info: str | None = Field(default=None, description="Shipping policy summary")

    # Escalation rules (onboarding step 6)
    escalation_threshold: float = Field(
        default=0.7,
        description="Confidence threshold for auto-escalation (0.0-1.0)",
    )
    escalation_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that trigger immediate escalation",
    )

    # Memory & privacy (onboarding step 8)
    memory_enabled: bool = Field(default=True, description="Whether Layer 2+ memory is active")

    # Custom system prompt additions
    custom_instructions: str | None = Field(
        default=None,
        description="Merchant-provided instructions appended to system prompt",
    )

    # Widget appearance (onboarding step 9 — Tidio parity, 22 controls)
    # Visual
    widget_primary_color: str | None = Field(default=None, description="Hex color for widget header/buttons (#RRGGBB)")
    widget_background_color: str | None = Field(default=None, description="Hex color for conversation panel background")
    widget_position: str | None = Field(default=None, description="bottom-right | bottom-left")
    widget_offset_x: int | None = Field(default=None, description="Horizontal offset from screen edge (px)")
    widget_offset_y: int | None = Field(default=None, description="Vertical offset from bottom edge (px)")
    widget_agent_avatar_url: str | None = Field(default=None, description="URL of agent avatar image")
    widget_agent_display_name: str | None = Field(default=None, description="Name shown in widget header/bubbles")
    widget_agent_title: str | None = Field(default=None, description="Subtitle under agent name (e.g. Customer Support)")
    widget_logo_url: str | None = Field(default=None, description="URL of company logo in widget header")
    widget_show_branding: bool | None = Field(default=None, description="Show 'Powered by Agent Red' badge")
    widget_mobile_enabled: bool | None = Field(default=None, description="Show widget on mobile devices")
    widget_dark_mode: bool | None = Field(default=None, description="Use dark color scheme")

    # Behavior
    widget_offline_message: str | None = Field(default=None, description="Message when team is offline")
    widget_auto_open: bool | None = Field(default=None, description="Auto-open widget after delay")
    widget_auto_open_delay: int | None = Field(default=None, description="Seconds before auto-open")
    widget_operating_hours: dict[str, Any] | None = Field(default=None, description="Structured schedule JSON")
    widget_offline_behavior: str | None = Field(default=None, description="ai_only | show_form | hide_widget")
    widget_prechat_form: dict[str, Any] | None = Field(default=None, description="Pre-chat form config JSON")
    widget_chat_rating_enabled: bool | None = Field(default=None, description="Post-chat thumbs up/down rating")
    widget_sound_enabled: bool | None = Field(default=None, description="Notification sound for new messages")
    widget_file_upload_enabled: bool | None = Field(default=None, description="Allow visitor file attachments")

    # Content and targeting
    widget_header_text: str | None = Field(default=None, description="Custom widget header/title text")
    widget_input_placeholder: str | None = Field(default=None, description="Message input placeholder text")
    widget_page_rules: list[str] = Field(default_factory=list, description="URL patterns for page visibility rules")

    # Metadata
    created_at: str = Field(description="When this version was created")
    created_by: str | None = Field(default=None, description="Who created this version")


# ---------------------------------------------------------------------------
# Document models — Collection 8: platform_config
# ---------------------------------------------------------------------------


class PlatformConfigDocument(BaseModel):
    """Platform-wide configuration (tier defaults, feature flags).

    Partition key: /config_type (not tenant-scoped)
    """

    id: str = Field(description="Document ID (= config_type:config_key)")
    config_type: str = Field(description="Partition key: tier_defaults | feature_flags | rate_limits")
    config_key: str = Field(description="Configuration key within type")

    # Config payload (flexible JSON structure)
    value: dict[str, Any] = Field(description="Configuration value")

    # Versioning
    version: int = Field(default=1, description="Config version")
    updated_at: str = Field(description="Last update timestamp")
    updated_by: str | None = Field(default=None, description="Who made the change")


# ---------------------------------------------------------------------------
# Document models — Collection 9: audit_log
# ---------------------------------------------------------------------------


class AuditLogDocument(BaseModel):
    """Append-only audit event (Decision #13).

    12 event types, time-partitioned, 1-year retention.
    Survives tenant deletion (not cascade-deleted).

    Partition key: /time_partition (YYYY-MM format for even distribution)
    """

    id: str = Field(description="Document ID (= event UUID)")
    time_partition: str = Field(description="Partition key (YYYY-MM)")
    event_type: AuditEventType = Field(description="One of 12 defined event types")

    # Context
    tenant_id: str = Field(description="Which tenant this event relates to")
    actor: str = Field(description="Who/what triggered the event (user ID, system, webhook)")
    actor_type: str = Field(default="system", description="user | system | webhook | admin")

    # Event payload (flexible, event-type-specific)
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data (no PII — scrubbed before storage)",
    )

    # Correlation
    conversation_id: str | None = Field(default=None, description="Related conversation ID")
    request_id: str | None = Field(default=None, description="HTTP request trace ID")

    # Timestamp
    timestamp: str = Field(description="Event timestamp (ISO 8601)")

    # TTL — 1 year retention
    ttl: int = Field(default=TTL_AUDIT_LOG, alias="_ts_ttl")


# ---------------------------------------------------------------------------
# Document models — Collection 10: team_members
# ---------------------------------------------------------------------------


class TeamMemberRole(str, Enum):
    """Team member roles within a tenant."""

    OWNER = "owner"        # Full access, cannot be removed
    ADMIN = "admin"        # Full access, can manage team
    AGENT = "agent"        # Can handle escalated conversations
    VIEWER = "viewer"      # Read-only dashboard access


class TeamMemberDocument(BaseModel):
    """Team member within a tenant (WI #179).

    Stores merchant team members who can access the admin dashboard
    and/or handle escalated conversations.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (= tenant_id:email)")
    tenant_id: str = Field(description="Partition key")
    email: str = Field(description="Team member email (unique within tenant)")
    display_name: str = Field(description="Display name shown in inbox/notes")
    role: TeamMemberRole = Field(description="Permission role")

    # Status
    is_active: bool = Field(default=True, description="Whether member has access")

    # Agent-specific (for human-agent escalation)
    max_concurrent_conversations: int = Field(
        default=5,
        description="Max simultaneous escalated conversations this agent can handle",
    )

    # Metadata
    created_at: str = Field(description="When member was added")
    updated_at: str = Field(description="Last update timestamp")
    last_login_at: str | None = Field(default=None, description="Last dashboard login")
    invited_by: str | None = Field(default=None, description="Who added this member")


# ---------------------------------------------------------------------------
# Collection configuration
# ---------------------------------------------------------------------------


class CollectionConfig(BaseModel):
    """Configuration for a single Cosmos DB collection/container."""

    name: str
    partition_key: str
    unique_keys: list[list[str]] = Field(default_factory=list)
    default_ttl: int | None = None
    vector_embedding_policy: dict[str, Any] | None = None
    indexing_policy: dict[str, Any] | None = None


def get_collection_configs() -> list[CollectionConfig]:
    """Return collection configurations for all 10 containers.

    These configs are used by the database initialization utility
    to create containers idempotently.
    """
    return [
        # 1. tenants
        CollectionConfig(
            name=COLLECTION_TENANTS,
            partition_key="/tenant_id",
            unique_keys=[["/stripe_customer_id"], ["/shopify_shop_domain"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
                "compositeIndexes": [
                    [
                        {"path": "/status", "order": "ascending"},
                        {"path": "/tier", "order": "ascending"},
                    ],
                    [
                        {"path": "/billing_channel", "order": "ascending"},
                        {"path": "/status", "order": "ascending"},
                    ],
                ],
            },
        ),
        # 2. conversations
        CollectionConfig(
            name=COLLECTION_CONVERSATIONS,
            partition_key="/tenant_id",
            unique_keys=[["/conversation_id"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/messages/*"},  # Exclude transcript from indexing (large)
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/status", "order": "ascending"},
                        {"path": "/started_at", "order": "descending"},
                    ],
                    [
                        {"path": "/is_billable", "order": "ascending"},
                        {"path": "/started_at", "order": "descending"},
                    ],
                    [
                        {"path": "/customer_id", "order": "ascending"},
                        {"path": "/started_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 3. usage
        CollectionConfig(
            name=COLLECTION_USAGE,
            partition_key="/tenant_id",
            default_ttl=TTL_USAGE_PERIOD,
            unique_keys=[["/billing_period"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
            },
        ),
        # 4. customer_profiles
        CollectionConfig(
            name=COLLECTION_CUSTOMER_PROFILES,
            partition_key="/tenant_id",
            unique_keys=[["/customer_id"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/purchase_history/*"},
                    {"path": "/product_questions/*"},
                    {"path": "/cart_contents/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/consent_status", "order": "ascending"},
                        {"path": "/updated_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 5. knowledge_bases
        CollectionConfig(
            name=COLLECTION_KNOWLEDGE_BASES,
            partition_key="/tenant_id",
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/content/?"},  # Full text excluded from range index
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/entry_type", "order": "ascending"},
                        {"path": "/is_active", "order": "ascending"},
                    ],
                    [
                        {"path": "/language", "order": "ascending"},
                        {"path": "/entry_type", "order": "ascending"},
                    ],
                ],
            },
        ),
        # 6. memory_vectors (with DiskANN vector index)
        CollectionConfig(
            name=COLLECTION_MEMORY_VECTORS,
            partition_key="/tenant_id",
            vector_embedding_policy={
                "vectorEmbeddings": [
                    {
                        "path": "/embedding",
                        "dataType": "float32",
                        "dimensions": VECTOR_DIMENSIONS,
                        "distanceFunction": VECTOR_SIMILARITY,
                    },
                ],
            },
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/embedding/*"},  # Vector handled by vector index
                    {"path": "/chunk_text/?"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/customer_id", "order": "ascending"},
                        {"path": "/conversation_date", "order": "descending"},
                    ],
                ],
                "vectorIndexes": [
                    {
                        "path": "/embedding",
                        "type": "diskANN",
                    },
                ],
            },
        ),
        # 7. preferences
        CollectionConfig(
            name=COLLECTION_PREFERENCES,
            partition_key="/tenant_id",
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
                "compositeIndexes": [
                    [
                        {"path": "/is_current", "order": "ascending"},
                        {"path": "/version", "order": "descending"},
                    ],
                ],
            },
        ),
        # 8. platform_config
        CollectionConfig(
            name=COLLECTION_PLATFORM_CONFIG,
            partition_key="/config_type",
            unique_keys=[["/config_key"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
            },
        ),
        # 9. audit_log
        CollectionConfig(
            name=COLLECTION_AUDIT_LOG,
            partition_key="/time_partition",
            default_ttl=TTL_AUDIT_LOG,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/payload/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/tenant_id", "order": "ascending"},
                        {"path": "/timestamp", "order": "descending"},
                    ],
                    [
                        {"path": "/event_type", "order": "ascending"},
                        {"path": "/timestamp", "order": "descending"},
                    ],
                    [
                        {"path": "/tenant_id", "order": "ascending"},
                        {"path": "/event_type", "order": "ascending"},
                        {"path": "/timestamp", "order": "descending"},
                    ],
                ],
            },
        ),
        # 10. team_members
        CollectionConfig(
            name=COLLECTION_TEAM_MEMBERS,
            partition_key="/tenant_id",
            unique_keys=[["/email"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
                "compositeIndexes": [
                    [
                        {"path": "/role", "order": "ascending"},
                        {"path": "/is_active", "order": "ascending"},
                    ],
                    [
                        {"path": "/is_active", "order": "ascending"},
                        {"path": "/updated_at", "order": "descending"},
                    ],
                ],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tier defaults (Decision #5 — rate limits, Decision #14 — concurrency)
# ---------------------------------------------------------------------------

TIER_DEFAULTS: dict[str, dict[str, Any]] = {
    TenantTier.TRIAL.value: {
        "included_conversations": 50,
        "rate_limit_rpm": 5,
        "max_concurrent": 2,
        "queue_depth": 3,
        "history_depth_days": 14,       # Trial: 14-day retention only
        "memory_layers": [1],           # Layer 1 only (basic profile)
        "overage_rate": 0.0,            # No overage — hard cap at 50
        "trial_duration_days": 14,      # 14-day trial period
    },
    TenantTier.STARTER.value: {
        "included_conversations": 1_000,
        "rate_limit_rpm": 10,
        "max_concurrent": 3,
        "queue_depth": 5,
        "history_depth_days": 90,       # Layer 2 retention
        "memory_layers": [1, 2],        # Layers available
        "overage_rate": 0.04,
    },
    TenantTier.PROFESSIONAL.value: {
        "included_conversations": 5_000,
        "rate_limit_rpm": 50,
        "max_concurrent": 10,
        "queue_depth": 20,
        "history_depth_days": 365,
        "memory_layers": [1, 2, 3],
        "overage_rate": 0.025,
    },
    TenantTier.ENTERPRISE.value: {
        "included_conversations": 20_000,
        "rate_limit_rpm": 200,
        "max_concurrent": 30,
        "queue_depth": 50,
        "history_depth_days": None,     # Unlimited
        "memory_layers": [1, 2, 3, 4],
        "overage_rate": 0.015,
    },
}


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------


async def initialize_database(
    client: Any,
    database_name: str = DATABASE_NAME,
) -> dict[str, Any]:
    """Create the database and all 9 containers if they don't exist.

    This function is idempotent — safe to call on every application
    startup. It uses create_if_not_exists semantics for both the
    database and each container.

    Args:
        client: An azure.cosmos.aio.CosmosClient instance.
        database_name: Database name (default: agent-red-prod).

    Returns:
        Dict with creation results: {database, containers: {name: status}}.
    """
    results: dict[str, Any] = {"database": database_name, "containers": {}}

    # Create database (idempotent)
    try:
        database = await client.create_database_if_not_exists(id=database_name)
        logger.info("Database ready: %s", database_name)
    except Exception:
        logger.exception("Failed to create database: %s", database_name)
        raise

    # Create containers (idempotent)
    configs = get_collection_configs()
    for config in configs:
        try:
            kwargs: dict[str, Any] = {
                "id": config.name,
                "partition_key": {"paths": [config.partition_key], "kind": "Hash"},
            }

            # Unique key policy
            if config.unique_keys:
                kwargs["unique_key_policy"] = {
                    "uniqueKeys": [{"paths": paths} for paths in config.unique_keys],
                }

            # Default TTL
            if config.default_ttl is not None:
                kwargs["default_ttl"] = config.default_ttl

            # Indexing policy
            if config.indexing_policy is not None:
                kwargs["indexing_policy"] = config.indexing_policy

            # Vector embedding policy (memory_vectors collection)
            if config.vector_embedding_policy is not None:
                kwargs["vector_embedding_policy"] = config.vector_embedding_policy

            await database.create_container_if_not_exists(**kwargs)
            results["containers"][config.name] = "ready"
            logger.info("Container ready: %s (partition: %s)", config.name, config.partition_key)

        except Exception:
            results["containers"][config.name] = "error"
            logger.exception("Failed to create container: %s", config.name)
            raise

    logger.info(
        "Database initialization complete: %d containers ready",
        len([s for s in results["containers"].values() if s == "ready"]),
    )
    return results
