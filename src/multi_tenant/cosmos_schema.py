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
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATABASE_NAME = "agentred"

# Sentinel tenant_id for platform admin authentication (SPEC-1667).
# SPA console auth produces a TenantContext with this value instead of a real
# tenant UUID. It is deliberately invalid as a UUID and will be rejected by
# TenantScopedRepository._validate_tenant_id() if any code path accidentally
# tries to use it for tenant-scoped operations.
PLATFORM_ADMIN_TENANT_ID = "__platform__"

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
COLLECTION_SLA_SNAPSHOTS = "sla_snapshots"
COLLECTION_VERIFICATION_TOKENS = "verification_tokens"
COLLECTION_INCIDENTS = "incidents"
COLLECTION_ALERT_RULES = "alert_rules"
COLLECTION_ALERT_HISTORY = "alert_history"
COLLECTION_INGESTION_JOBS = "ingestion_jobs"
COLLECTION_PII_TOKEN_MAPPINGS = "pii_token_mappings"
COLLECTION_ADMIN_DOCUMENTATION = "admin_documentation_vectors"
COLLECTION_CONTACT_MESSAGES = "contact_messages"
COLLECTION_PLATFORM_ADMINS = "platform_admins"

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
    COLLECTION_SLA_SNAPSHOTS,
    COLLECTION_VERIFICATION_TOKENS,
    COLLECTION_INCIDENTS,
    COLLECTION_ALERT_RULES,
    COLLECTION_ALERT_HISTORY,
    COLLECTION_INGESTION_JOBS,
    COLLECTION_PII_TOKEN_MAPPINGS,
    COLLECTION_ADMIN_DOCUMENTATION,
    COLLECTION_CONTACT_MESSAGES,
    COLLECTION_PLATFORM_ADMINS,
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
TTL_SLA_SNAPSHOTS = 90 * 24 * 60 * 60     # 90 days (SLA trend retention)
TTL_VERIFICATION_TOKEN = 10 * 60           # 10 minutes (email verification link)
TTL_INCIDENTS = 365 * 24 * 60 * 60        # 1 year (incident history retention)
TTL_ALERT_HISTORY = 90 * 24 * 60 * 60     # 90 days (alert history retention)
TTL_INGESTION_JOBS = 30 * 24 * 60 * 60   # 30 days (ingestion job retention)
TTL_PII_TOKEN_MAPPINGS = 7 * 24 * 60 * 60  # 7 days (PII token mapping retention)


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
    MANUAL = "manual"  # SPA Console provisioned (no webhook trigger)


class ConsentStatus(str, Enum):
    """GDPR consent status for Persistent Customer Memory (Decision #10)."""

    GRANTED = "granted"
    DENIED = "denied"
    NOT_ASKED = "not_asked"


class ConversationStatus(str, Enum):
    """Conversation lifecycle status."""

    ACTIVE = "active"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    TIMED_OUT = "timed_out"
    ERROR = "error"


class AuditEventType(str, Enum):
    """Audit log event types (Decision #13 — 13 event types)."""

    TENANT_CREATED = "tenant.created"
    TENANT_ACTIVATED = "tenant.activated"
    TENANT_UPDATED = "tenant.updated"
    TENANT_DEACTIVATED = "tenant.deactivated"
    TENANT_DELETED = "tenant.deleted"
    TENANT_PROVISIONED = "tenant.provisioned"
    SUBSCRIPTION_CHANGED = "subscription.changed"
    CONFIG_UPDATED = "config.updated"
    CONFIG_CHANGE = "config.change"
    DATA_EXPORTED = "data.exported"
    DATA_DELETED = "data.deleted"
    CONSENT_CHANGED = "consent.changed"
    ESCALATION_TRIGGERED = "escalation.triggered"
    SECURITY_EVENT = "security.event"
    MODEL_DEPLOYED = "model.deployed"
    MODEL_ROLLED_BACK = "model.rolled_back"
    TEAM_MEMBER_ADDED = "team.member_added"
    TEAM_MEMBER_REMOVED = "team.member_removed"
    TEAM_MEMBER_UPDATED = "team.member_updated"


class PiiClassification(str, Enum):
    """PII classification for fields (Decision #7 — PII scrubbing)."""

    NONE = "none"             # No PII (safe to log)
    DIRECT = "direct"         # Directly identifies a person (email, name)
    INDIRECT = "indirect"     # Could identify with other data (IP, device)
    SENSITIVE = "sensitive"   # Special category (health, financial)


class ConfigState(str, Enum):
    """Activation state of a preferences document.

    The Save → Activate model stores configuration in three states:
    - DRAFT:    saved changes not yet live (admin UI writes here)
    - ACTIVE:   the configuration the chat pipeline reads
    - PREVIOUS: the activation snapshot before the current one (for Restore)

    Documents without a config_state field are treated as ACTIVE for
    backward compatibility with pre-migration data.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    PREVIOUS = "previous"


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
    trial_warnings_sent: list[str] = Field(
        default_factory=list,
        description="Expiry warning milestones already sent (e.g. ['7d', '3d', '1d']). "
        "Prevents duplicate warning emails from the expiry warning scanner.",
    )

    # General access expiry (any billing channel — WI-EXPIRY-1)
    expires_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when tenant access expires. "
        "Works for any billing channel. Auth middleware rejects requests "
        "after this time. Scanner transitions status to TRIAL_EXPIRED.",
    )
    expiry_warnings_sent: list[str] = Field(
        default_factory=list,
        description="Expiry warning milestones already sent (e.g. ['7d', '3d', '1d']). "
        "Prevents duplicate warning emails for general expiry.",
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

    # Conversation type (SPEC-1561 — Co-pilot admin conversations)
    conversation_type: str = Field(
        default="customer",
        description=(
            "Conversation origin: 'customer' (default — storefront visitor) or "
            "'admin_assistance' (team member querying Co-pilot from admin panel). "
            "Admin conversations are non-billable and routed to the Co-pilot agent."
        ),
    )

    # Billing (Decision #24 — billable conversation definition)
    is_billable: bool = Field(default=False, description="Whether this conversation counts for billing")
    message_count: int = Field(default=0, description="Total messages in conversation")
    turn_count: int = Field(default=0, description="Customer-AI turn pairs")

    # Pipeline trace (Decision #28+ — explainability)
    agents_invoked: list[str] = Field(default_factory=list, description="Agents used in pipeline")
    model_used: str | None = Field(default=None, description="Primary model (e.g. gpt-4o)")
    critic_passed: bool | None = Field(default=None, description="Whether Critic approved response")

    # Human agent assignment (WI #171 — admin inbox)
    assigned_to: str | None = Field(default=None, description="Human agent ID (post-escalation)")
    escalation_category: str | None = Field(
        default=None,
        description="Escalation category (from ESCALATION_CATEGORIES) — set during escalation",
    )
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

    # WI #132: First-chunk delivery timestamp — set when the first AI token
    # is streamed to the client via SSE. Used for billing-at-first-chunk and
    # time-to-first-byte (TTFB) latency tracking.
    first_chunk_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when first AI token was delivered to client",
    )

    # Archival (WI #7 — conversation lifecycle)
    archived_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when conversation was archived (null = not archived)",
    )

    # Customer verification level (AUTH-5 — profile linkage)
    customer_verified: bool = Field(
        default=False,
        description="Whether customer identity was verified (OTP token or Shopify HMAC)",
    )

    # In-conversation identity collection (P0-AUTH-FIX)
    identity_email: str | None = Field(
        default=None,
        description="Email address collected in-conversation (before OTP verification)",
    )
    identity_otp_sent_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when OTP was last sent for this conversation",
    )
    identity_otp_attempts: int = Field(
        default=0,
        description="Number of OTP verification attempts in this conversation (rate limit: 3)",
    )

    # Test Mode (C2 — controlled rollout)
    is_test_mode: bool = Field(
        default=False,
        description="Whether this conversation was routed to the test AI configuration",
    )

    # Layer 2 memory vectorization (WI #87)
    vectorized_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when conversation was vectorized for Layer 2 memory. "
        "Null means not yet vectorized. Set by the vectorization background scanner.",
    )

    # Pipeline trace (SPEC-1530 — end-to-end conversation tracing)
    pipeline_trace: dict[str, Any] | None = Field(
        default=None,
        description="Pipeline execution trace: {trace_id, stages[], total_latency_ms, intent, "
        "confidence, critic_passed, model_used}. Set after each AI response turn.",
    )

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

    # Data source 7: Asserted identity (Issue #5b — PCM Layer 1)
    asserted_identity: dict[str, Any] = Field(
        default_factory=dict,
        description="{name, email, extracted_at, source}",
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

    RAG vectorization (WI #209): entries are embedded via text-embedding-3-large
    (3072 dimensions) and stored with a DiskANN vector index for semantic search.
    The embedding field is populated asynchronously after create/update.
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

    # Vector embedding (WI #209 — RAG vectorization)
    embedding: list[float] | None = Field(
        default=None,
        description="3072-dimensional embedding vector (text-embedding-3-large). "
        "Populated asynchronously after create/update.",
    )
    embedding_model: str | None = Field(
        default=None,
        description="Model used to generate the embedding (e.g. text-embedding-3-large)",
    )
    embedded_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when the embedding was last generated",
    )
    content_hash: str | None = Field(
        default=None,
        description="SHA-256 hash of title+content at embedding time. "
        "Used to detect content changes requiring re-embedding.",
    )

    # Staleness tracking (WI #219)
    last_verified_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when a human last confirmed this content is current",
    )
    staleness_score: float | None = Field(
        default=None,
        description="Computed staleness score 0.0 (fresh) to 1.0 (stale). "
        "Based on age, feedback signals, and entry type.",
    )

    # Document upload metadata (WI #214-216)
    source_type: str | None = Field(
        default=None,
        description="How this entry was created: manual | pdf | docx | csv | url",
    )
    source_filename: str | None = Field(
        default=None,
        description="Original filename for uploaded documents",
    )
    source_url: str | None = Field(
        default=None,
        description="Source URL for URL-imported entries",
    )
    chunk_index: int | None = Field(
        default=None,
        description="Chunk position within a multi-chunk document (0-based)",
    )
    parent_entry_id: str | None = Field(
        default=None,
        description="ID of the parent entry when this is a chunk of a larger document",
    )

    # Classification
    category: str | None = Field(
        default=None,
        description="Article category (e.g. Shipping, Returns, Product Info)",
    )
    status: str = Field(
        default="draft",
        description="Article status: published | draft | archived",
    )

    # Lifecycle
    is_active: bool = Field(default=True, description="Whether entry is searchable")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


class WebsiteSourceStatus(str, Enum):
    """Status of a website crawl source."""

    PENDING = "pending"
    CRAWLING = "crawling"
    ACTIVE = "active"
    FAILED = "failed"
    PAUSED = "paused"


class WebsiteSourceDocument(BaseModel):
    """Saved website crawl source for automated knowledge ingestion.

    Stored in the ``knowledge_bases`` container alongside KB entries, using
    ``doc_type = "website_source"`` as discriminator.  The background refresh
    loop checks ``next_crawl_at`` and triggers re-crawls with content change
    detection to keep KB entries fresh.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (UUID)")
    tenant_id: str = Field(description="Partition key — tenant owning this source")
    doc_type: str = Field(
        default="website_source",
        description="Discriminator to distinguish from KnowledgeBaseDocument",
    )

    # Source configuration
    domain: str = Field(description="Normalized domain (e.g. example.myshopify.com)")
    start_url: str = Field(description="Seed URL for crawling")
    max_pages: int = Field(default=25, ge=1, le=100, description="Maximum pages to crawl (1-100)")
    crawl_depth: int = Field(default=3, ge=1, le=10, description="Maximum link-following depth")
    entry_type: str = Field(default="article", description="Default KB entry type for crawled pages")

    # Schedule
    auto_refresh: bool = Field(default=True, description="Enable periodic re-crawling")
    refresh_interval_hours: int = Field(
        default=24, ge=6, le=168,
        description="Hours between automatic re-crawls (6-168)",
    )

    # Status tracking
    status: str = Field(
        default=WebsiteSourceStatus.PENDING.value,
        description="pending | crawling | active | failed | paused",
    )
    last_crawled_at: str | None = Field(default=None, description="ISO 8601 last crawl completion")
    next_crawl_at: str | None = Field(default=None, description="ISO 8601 next scheduled crawl")

    # Progress metrics (from most recent crawl)
    pages_discovered: int = Field(default=0, description="Total URLs found during last crawl")
    pages_crawled: int = Field(default=0, description="Pages successfully parsed")
    articles_created: int = Field(default=0, description="KB entries currently linked to this source")
    total_chars: int = Field(default=0, description="Total content characters across all pages")
    error_message: str | None = Field(default=None, description="Error from last failed crawl")

    # Lifecycle
    is_active: bool = Field(default=True, description="Soft delete flag")
    created_at: str = Field(description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(description="Last update timestamp (ISO 8601)")


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
# Quick Action models (WI #226-229 — Contextual Quick Action Prompt Buttons)
# ---------------------------------------------------------------------------


class QuickActionPrompt(BaseModel):
    """A single quick action prompt button configuration.

    Stored as a list inside PreferencesDocument.quick_actions. Merchants
    create these in the admin dashboard and assign them to page types.

    The prompt_template supports {{variable}} placeholders that the widget
    resolves at click time using page context (e.g. {{product_title}}).
    """

    id: str = Field(description="Unique ID (uuid4)")
    label: str = Field(
        description="Button text shown to customer (e.g. 'What's on sale?')",
    )
    prompt_template: str = Field(
        description="Hidden prompt sent to AI, with {{variable}} placeholders. "
        "Supported variables: {{page_type}}, {{page_title}}, {{page_url}}, "
        "{{page_handle}}, {{product_title}}, {{collection_title}}",
    )
    icon: str | None = Field(
        default=None,
        description="Optional emoji or icon identifier for the button",
    )
    is_active: bool = Field(default=True, description="Whether this action is available")
    sort_order: int = Field(default=0, description="Display priority (lower = first)")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp (ISO 8601)",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp (ISO 8601)",
    )


# Valid page types for quick action assignments
VALID_PAGE_TYPES = {
    "home", "product", "collection", "cart", "search",
    "blog", "page", "all", "other",
}


class QuickActionPageAssignment(BaseModel):
    """Maps quick actions to specific page types with 2 slot positions.

    Each page type (or specific page handle) gets up to 2 quick action
    buttons. The widget requests its page context at boot, and the server
    returns the matching assignment's actions.

    Priority: specific handle match > page type match > "all" fallback.
    """

    page_type: str = Field(
        description="Page type: home, product, collection, cart, search, blog, page, all, other",
    )
    page_handle: str | None = Field(
        default=None,
        description="Specific page handle (e.g. product slug). "
        "null = applies to all pages of this type.",
    )
    slot_1_action_id: str | None = Field(
        default=None,
        description="Quick action ID for slot 1 (left/top button)",
    )
    slot_2_action_id: str | None = Field(
        default=None,
        description="Quick action ID for slot 2 (right/bottom button)",
    )
    auto_open: bool = Field(
        default=False,
        description="Whether the quick action auto-opens on this page type",
    )
    auto_open_delay_ms: int = Field(
        default=3000,
        description="Delay in milliseconds before auto-opening (0 = immediate)",
    )


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

    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Document ID (= tenant_id:version)")
    tenant_id: str = Field(description="Partition key")
    version: int = Field(description="Config version number (monotonically increasing)")
    is_current: bool = Field(default=True, description="Whether this is the active config version")
    config_state: str = Field(
        default="active",
        description="Activation lifecycle state: draft | active | previous. "
                    "Documents without this field are treated as 'active' for "
                    "backward compatibility.",
    )
    activated_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of when this config was activated (set "
                    "on state transition to 'active')",
    )
    activated_by: str | None = Field(
        default=None,
        description="Actor who activated this config version",
    )
    config_name: str | None = Field(
        default=None,
        description="Named configuration label (e.g. 'Default', 'Holiday Mode'). "
                    "'Default' is the undeletable initial production config.",
    )
    appearance_name: str | None = Field(
        default=None,
        description="Named widget appearance label (e.g. 'Default', 'Dark Theme'). "
                    "'Default' is the undeletable initial widget appearance.",
    )

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
    customer_identification_mode: str = Field(
        default="standard",
        description=(
            "How aggressively the AI encourages customers to identify themselves. "
            "Values: off, gentle, standard, aggressive. Controls prompt injection "
            "in Response Generator for authentication suggestions and PCM-building "
            "probing questions."
        ),
    )

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
    widget_mobile_fullscreen: bool | None = Field(default=None, description="Chat panel fills full viewport on mobile")
    widget_mobile_position: str | None = Field(default=None, description="Mobile position override (bottom-right|bottom-left)")
    widget_mobile_offset_x: int | None = Field(default=None, description="Mobile horizontal offset in pixels")
    widget_mobile_offset_y: int | None = Field(default=None, description="Mobile vertical offset in pixels")
    widget_dark_mode: bool | None = Field(default=None, description="Use dark color scheme")
    widget_color_mode: str | None = Field(default=None, description="light | dark | auto")
    widget_header_gradient_end: str | None = Field(default=None, description="Hex color for header gradient end (#RRGGBB)")
    widget_header_gradient_enabled: bool | None = Field(default=None, description="Enable header gradient (left→right color blend)")
    widget_font_family: str | None = Field(default=None, description="CSS font-family value")
    widget_border_radius: int | None = Field(default=None, description="Border radius for widget panels (px)")
    widget_launcher_size: int | None = Field(default=None, description="Launcher button diameter (px)")
    widget_launcher_icon: str | None = Field(default=None, description="chat | headset | help | custom")
    widget_header_title: str | None = Field(default=None, description="Widget header title text")
    widget_header_subtitle: str | None = Field(default=None, description="Widget header subtitle text")
    widget_agent_bubble_color: str | None = Field(default=None, description="Hex color for agent message bubble background (#RRGGBB)")
    widget_agent_bubble_text_color: str | None = Field(default=None, description="Hex color for agent message bubble text (#RRGGBB)")
    widget_customer_bubble_color: str | None = Field(default=None, description="Hex color for customer message bubble background (#RRGGBB)")
    widget_customer_bubble_text_color: str | None = Field(default=None, description="Hex color for customer message bubble text (#RRGGBB)")
    widget_launcher_shape: str | None = Field(default=None, description="circle | rounded-square | pill")
    widget_launcher_color: str | None = Field(default=None, description="Hex color for launcher button background (#RRGGBB). Falls back to widget_primary_color.")
    widget_shadow_intensity: str | None = Field(default=None, description="none | subtle | standard | heavy")
    widget_panel_width: str | None = Field(default=None, description="compact | standard | wide")
    widget_panel_height: str | None = Field(default=None, description="short | standard | tall")
    widget_locale: str | None = Field(default=None, description="auto | en | es | fr | de | pt | ja | zh | ko")

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
    widget_greeting_enabled: bool | None = Field(default=None, description="Show greeting message on open")
    widget_greeting_mode: str | None = Field(default=None, description="Greeting mode: 'static' or 'ai_generated'")
    widget_greeting_message: str | None = Field(default=None, description="Greeting message text")
    widget_pre_chat_form_enabled: bool | None = Field(default=None, description="Show pre-chat form before conversation")
    widget_pre_chat_fields: list[str] | None = Field(default=None, description="Pre-chat form field names (name, email, phone, etc.)")
    widget_offline_form_enabled: bool | None = Field(default=None, description="Show offline contact form")

    # Content and targeting
    widget_key: str | None = Field(default=None, description="Publishable widget key (pk_live_...) for widget authentication")
    widget_header_text: str | None = Field(default=None, description="Custom widget header/title text")
    widget_input_placeholder: str | None = Field(default=None, description="Message input placeholder text")
    widget_page_rules: list[str] | None = Field(default=None, description="URL patterns for page visibility rules")
    widget_exit_intent_enabled: bool = Field(default=False, description="Auto-open widget on exit intent (desktop mouseleave)")
    widget_scroll_depth_trigger: int | None = Field(default=None, description="Auto-open widget at scroll depth percentage (1-100)")

    # Notifications (WI-G: email alerts)
    notification_email: str | None = Field(
        default=None,
        description="Email address for alert notifications (usage, trial, outage)",
    )

    # Fine-tuning configuration (Enterprise add-on, Layer 4 — Decision #31, WI #93-96)
    fine_tuning_enabled: bool = Field(
        default=False,
        description="Whether per-tenant fine-tuning is active (Enterprise add-on, $299/mo)",
    )
    fine_tuning_schedule: str | None = Field(
        default=None,
        description="Retraining schedule: monthly | weekly | trigger",
    )
    fine_tuning_min_conversations: int = Field(
        default=1000,
        description="Minimum conversation count before fine-tuning is eligible",
    )
    fine_tuning_active_model_id: str | None = Field(
        default=None,
        description="Currently deployed fine-tuned model ID (ft:gpt-4o-mini:...)",
    )
    fine_tuning_active_model_version: int | None = Field(
        default=None,
        description="Version number of the active fine-tuned model",
    )
    fine_tuning_ab_experiment_id: str | None = Field(
        default=None,
        description="Currently active A/B experiment ID (if any)",
    )

    # Integrations (onboarding step 7 — C10)
    shopify_sync_enabled: bool = Field(
        default=True,
        description="Auto-sync product data from Shopify store",
    )
    zendesk_escalation_enabled: bool = Field(
        default=False,
        description="Create Zendesk tickets on escalation (Professional+)",
    )
    mailchimp_segment_sync: bool = Field(
        default=False,
        description="Sync Mailchimp segments for personalization (Professional+)",
    )
    google_analytics_enabled: bool = Field(
        default=False,
        description="Export conversation events to GA4 (Professional+)",
    )
    # Integration connection metadata (not directly configurable — set by integration flow)
    shopify_integration_status: str | None = Field(
        default=None,
        description="connected | disconnected | error",
    )
    zendesk_integration_status: str | None = Field(
        default=None,
        description="connected | disconnected | error",
    )
    mailchimp_integration_status: str | None = Field(
        default=None,
        description="connected | disconnected | error",
    )
    google_analytics_integration_status: str | None = Field(
        default=None,
        description="connected | disconnected | error",
    )

    # Retrieval tuning (RAG Phase 1)
    retrieval_top_k: int | None = Field(
        default=None,
        description="Number of KB results to retrieve (1-20, default 5)",
    )
    retrieval_vector_weight: float | None = Field(
        default=None,
        description="Weight for vector similarity in hybrid search (0.0-1.0, default 0.7)",
    )
    retrieval_bm25_weight: float | None = Field(
        default=None,
        description="Weight for BM25 keyword matching in hybrid search (0.0-1.0, default 0.3)",
    )
    retrieval_min_score: float | None = Field(
        default=None,
        description="Minimum relevance score to include a result (0.0-1.0, default 0.1)",
    )

    # Intent-to-source routing (RAG Phase 1)
    intent_source_mapping: dict[str, str] | None = Field(
        default=None,
        description="Maps intent names to KB entry_type filters, e.g. {'refund': 'policy', 'product_info': 'product'}",
    )

    # Source citation (RAG Phase 1)
    cite_sources_in_response: bool = Field(
        default=False,
        description="When enabled, append source titles to AI responses",
    )

    # Quick Action Prompt Buttons (WI #226-229)
    quick_actions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Quick action prompt button definitions (QuickActionPrompt dicts)",
    )
    quick_action_assignments: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Page-to-quick-action slot assignments (QuickActionPageAssignment dicts)",
    )
    widget_quick_actions_enabled: bool = Field(
        default=True,
        description="Whether quick action buttons are shown in the widget",
    )

    # MCP Server Configuration (AGNTCY Phase 3)
    mcp_servers: list[dict[str, Any]] = Field(
        default_factory=list,
        description="MCP server configurations [{server_name, server_url, "
        "server_type, enabled, read_only, shop_domain, tool_allowlist, timeout_ms}]",
    )
    mcp_enabled: bool = Field(
        default=False,
        description="Master switch for MCP tool augmentation",
    )

    # Stripe MCP (AGNTCY Phase 3B — Cycle 5)
    stripe_mcp_enabled: bool = Field(
        default=False,
        description="Enable Stripe MCP for AI-powered payment/subscription queries",
    )
    stripe_mcp_status: str | None = Field(
        default=None,
        description="Stripe MCP connection status: connected | disconnected | None",
    )

    # Mutation policy (AGNTCY Phase 3B — Cycle 5, disabled by default)
    mutation_policy: dict[str, Any] | None = Field(
        default=None,
        description="MCP mutation policy config (allow_mutations, require_critic_approval, etc.)",
    )

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
    """Team member roles within a tenant.

    Role hierarchy (highest to lowest):
        superadmin — Hidden from other users, cannot be deleted/disabled.
                     Auto-created during provisioning. Safety net against lockout.
        admin      — Full dashboard access, can manage team (except superadmin).
        escalation_agent — Read-only Inbox access only. Receives escalation
                     email notifications for assigned categories. No config access.
        viewer     — Read-only access to all dashboard pages.
    """

    SUPERADMIN = "superadmin"              # Hidden, undeletable, auto-provisioned
    ADMIN = "admin"                        # Full access, can manage team
    ESCALATION_AGENT = "escalation_agent"  # Read-only Inbox, escalation email target
    VIEWER = "viewer"                      # Read-only dashboard access


# Escalation categories that can be assigned to escalation agents
ESCALATION_CATEGORIES = [
    "service",
    "support",
    "sales",
    "account",
    "technical_assistance",
    "general_inquiry",
]


class IncidentStatus(str, Enum):
    """Incident lifecycle status (HV-5 status page)."""

    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    SCHEDULED = "scheduled"


class IncidentSeverity(str, Enum):
    """Incident severity level."""

    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


# Standard services that can be affected by incidents
INCIDENT_SERVICES = [
    "API",
    "Widget",
    "NATS",
    "Key Vault",
    "MCP",
    "Admin Console",
    "Cosmos DB",
]


class AlertRuleType(str, Enum):
    """Alert rule category (RB-4 alerting)."""

    QUEUE_DEPTH = "queue_depth"
    SECRET_EXPIRY = "secret_expiry"
    CIRCUIT_BREAKER = "circuit_breaker"
    SLA_BREACH = "sla_breach"
    INCIDENT = "incident"


class AlertSeverity(str, Enum):
    """Alert severity level."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TeamMemberDocument(BaseModel):
    """Team member within a tenant (WI #179).

    Stores merchant team members who can access the admin dashboard
    and/or handle escalated conversations.

    Per-user API key auth: each team member has a unique API key
    (ar_user_{prefix}_{random}) that resolves to their identity and role.
    The key hash is stored here for lookup.

    Partition key: /tenant_id
    """

    id: str = Field(description="Document ID (= tenant_id:email)")
    tenant_id: str = Field(description="Partition key")
    email: str = Field(description="Team member email (unique within tenant, immutable by self)")
    display_name: str = Field(description="Display name shown in inbox/notes")
    role: TeamMemberRole = Field(description="Permission role")

    # Per-user API key authentication
    user_api_key_hash: str | None = Field(
        default=None,
        description="SHA-256 hash of the team member's personal API key (ar_user_...)",
    )
    user_api_key_prefix: str | None = Field(
        default=None,
        description="First 12 chars of the API key for display (ar_user_rema...)",
    )

    # Status
    is_active: bool = Field(default=True, description="Whether member has access")

    # Escalation agent configuration
    escalation_categories: list[str] = Field(
        default_factory=list,
        description="Escalation categories this agent handles: "
        "service, support, sales, account, technical_assistance, general_inquiry. "
        "Only applicable when role = escalation_agent.",
    )
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
# Incident document (HV-5 — status page)
# ---------------------------------------------------------------------------


class IncidentUpdateEntry(BaseModel):
    """A single status update on an incident timeline."""

    timestamp: str
    status: str
    message: str
    author: str = "system"


class IncidentDocument(BaseModel):
    """Incident record for the status page.

    Partition key: /status (investigating, identified, monitoring, resolved, scheduled)
    TTL: 365 days. Unique key: /incident_id.
    """

    id: str = ""
    incident_id: str = ""
    title: str = ""
    description: str = ""
    status: str = IncidentStatus.INVESTIGATING.value
    severity: str = IncidentSeverity.MINOR.value
    affected_services: list[str] = Field(default_factory=list)
    updates: list[IncidentUpdateEntry] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    resolved_at: str | None = None
    created_by: str = ""
    ttl: int = Field(default=TTL_INCIDENTS, alias="_ts_ttl")


# ---------------------------------------------------------------------------
# Alert rule document (RB-4 — alerting)
# ---------------------------------------------------------------------------


class AlertCondition(BaseModel):
    """Condition that triggers an alert."""

    metric: str = ""
    operator: str = "gt"  # gt, lt, gte, lte, eq, ne
    threshold: float = 0


class AlertRuleDocument(BaseModel):
    """Alert rule definition.

    Partition key: /rule_type (queue_depth, secret_expiry, etc.)
    No TTL — rules persist until deleted.
    """

    id: str = ""
    rule_id: str = ""
    rule_type: str = AlertRuleType.QUEUE_DEPTH.value
    name: str = ""
    description: str = ""
    enabled: bool = True
    condition: AlertCondition = Field(default_factory=AlertCondition)
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    runbook_url: str = ""
    created_at: str = ""
    updated_at: str = ""


class AlertHistoryDocument(BaseModel):
    """Alert firing history.

    Partition key: /alert_date (YYYY-MM-DD for even distribution)
    TTL: 90 days.
    """

    id: str = ""
    alert_date: str = ""
    rule_id: str = ""
    rule_name: str = ""
    rule_type: str = ""
    triggered_at: str = ""
    resolved_at: str | None = None
    severity: str = AlertSeverity.WARNING.value
    message: str = ""
    metric_value: float = 0
    threshold_value: float = 0
    acknowledged: bool = False
    acknowledged_by: str | None = None
    ttl: int = Field(default=TTL_ALERT_HISTORY, alias="_ts_ttl")


class IngestionJobType(str, Enum):
    """Type of storefront ingestion job."""

    SHOPIFY = "shopify"
    URL = "url"
    CATEGORY_TEMPLATE = "category_template"
    WEBSITE_REFRESH = "website_refresh"


class IngestionJobStatus(str, Enum):
    """Status of a storefront ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionJobDocument(BaseModel):
    """Storefront ingestion job tracking (KA-1: Knowledge Automation).

    Tracks background knowledge ingestion jobs — Shopify product imports,
    URL crawls, and category template applications. Each job creates
    KB articles and vectorizes them asynchronously.

    Partition key: /tenant_id
    TTL: 30 days.
    """

    id: str = Field(description="Document ID (UUID)")
    tenant_id: str = Field(description="Partition key — tenant owning this job")

    # Job configuration
    job_type: str = Field(description="shopify | url | category_template")
    status: str = Field(
        default=IngestionJobStatus.PENDING.value,
        description="pending | running | completed | failed | cancelled",
    )
    source_config: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Job-specific configuration. "
            "Shopify: {shop_domain, access_token_ref}. "
            "URL: {start_url, max_pages, entry_type}. "
            "Template: {category_id, merge_mode}."
        ),
    )

    # Progress tracking
    progress_percent: int = Field(default=0, description="0-100 completion percentage")
    articles_created: int = Field(default=0, description="KB articles successfully created")
    articles_failed: int = Field(default=0, description="KB articles that failed to create")
    total_chars: int = Field(default=0, description="Total characters of content ingested")
    pages_crawled: int = Field(default=0, description="Number of pages/products processed")

    # Results
    entry_ids: list[str] = Field(
        default_factory=list,
        description="IDs of created KB articles (for rollback/tracking)",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if job failed",
    )

    # Timestamps
    created_at: str = Field(description="When job was created (ISO 8601)")
    started_at: str | None = Field(default=None, description="When processing began")
    completed_at: str | None = Field(default=None, description="When processing finished")

    # TTL
    ttl: int = Field(default=TTL_INGESTION_JOBS, alias="_ts_ttl")


class PiiTokenMappingDocument(BaseModel):
    """PII token mapping for reversible tokenization (SPEC-1545).

    Stores the mapping between PII tokens (``pii-{type}-{uuid}``) and their
    original values. Used by PiiTokenizer to detokenize responses before
    delivery to the customer.

    Each document represents one conversation's complete token mapping set.
    Per-conversation granularity enables efficient lookup during detokenization
    and GDPR-compliant deletion (one conversation at a time or all for a tenant).

    Partition key: /tenant_id
    TTL: 7 days (matching conversation retention window).
    """

    id: str = Field(description="Document ID: {tenant_id}:{conversation_id}")
    tenant_id: str = Field(description="Partition key — tenant owning this conversation")
    conversation_id: str = Field(description="Conversation these tokens belong to")

    # Token mappings: list of {token, original, pii_type, created_at}
    mappings: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "List of token mappings. Each entry: "
            "{token: 'pii-email-uuid', original: 'user@example.com', "
            "pii_type: 'email', created_at: 'ISO 8601'}"
        ),
    )

    # Metadata
    mapping_count: int = Field(default=0, description="Number of active token mappings")
    created_at: str = Field(description="When first mapping was created (ISO 8601)")
    updated_at: str = Field(description="When last mapping was added (ISO 8601)")

    # TTL
    ttl: int = Field(default=TTL_PII_TOKEN_MAPPINGS, alias="_ts_ttl")


class AdminDocumentationDocument(BaseModel):
    """Platform-level product documentation for the Co-pilot agent (SPEC-1559).

    Stores Agent Red admin documentation vectorized for semantic search.
    Shared across all tenants — NOT tenant-scoped. Partition key is
    ``/document_category`` (e.g., "dashboard", "knowledge_base", "widget").

    The Co-pilot agent retrieves from this collection when a team member
    asks about Agent Red administrative features.

    Partition key: /document_category
    No TTL — documentation is permanent.

    (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
    """

    id: str = Field(description="Document ID: {category}:{slug}")
    document_category: str = Field(
        description=(
            "Partition key — admin feature area. One of: dashboard, "
            "knowledge_base, widget_configuration, team_management, "
            "conversations, analytics, custom_instructions, brand_tone, "
            "business_policies, escalation_rules, integrations, "
            "save_activate, getting_started, billing"
        ),
    )

    # Content
    title: str = Field(description="Documentation page title")
    content: str = Field(description="Full documentation text (markdown)")
    section: str | None = Field(
        default=None,
        description="Sub-section within the category (e.g., 'Search Weights')",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Search tags for keyword matching",
    )

    # Vector embedding (text-embedding-3-large, 3072 dims)
    embedding: list[float] | None = Field(
        default=None,
        description="3072-dimensional embedding for semantic search",
    )
    embedding_model: str | None = Field(
        default=None,
        description="Model used for embedding (e.g., 'text-embedding-3-large')",
    )
    content_hash: str | None = Field(
        default=None,
        description="SHA-256 of title+content for change detection",
    )
    embedded_at: str | None = Field(
        default=None,
        description="When embedding was last computed (ISO 8601)",
    )

    # Metadata
    source_file: str | None = Field(
        default=None,
        description="Original docs-site file path (e.g., 'admin-guide/knowledge-base.md')",
    )
    version: str | None = Field(
        default=None,
        description="Documentation version (tracks product version at time of ingestion)",
    )
    is_active: bool = Field(default=True, description="Whether this entry is searchable")
    created_at: str = Field(description="When created (ISO 8601)")
    updated_at: str = Field(description="When last updated (ISO 8601)")


class CopilotConfigDocument(BaseModel):
    """Platform-level Co-Pilot configuration (SPEC-1575, SPEC-1576).

    Stores scan schedule and retrieval tuning parameters. Single document
    per platform with id='copilot_config', partition key 'platform'.
    Stored in admin_documentation_vectors collection alongside docs.
    """

    id: str = Field(default="copilot_config")
    document_category: str = Field(
        default="platform",
        description="Partition key — 'platform' for config documents",
    )

    # Scan schedule (SPEC-1575)
    scan_frequency: str = Field(
        default="manual",
        description="Scan frequency: 'manual', 'daily', or 'weekly'",
    )
    scan_scope: str = Field(
        default="docs-site",
        description="Scope: 'docs-site', 'urls', or 'both'",
    )
    last_scan_at: str | None = Field(
        default=None,
        description="Last scan timestamp (ISO 8601)",
    )
    next_scan_at: str | None = Field(
        default=None,
        description="Next scheduled scan timestamp (ISO 8601)",
    )
    scan_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Last 10 scan results (timestamp, created, updated, skipped, errors)",
    )

    # Retrieval parameters (SPEC-1576)
    vector_weight: float = Field(
        default=0.7,
        description="Weight for vector search in RRF merge (0.0-1.0)",
    )
    bm25_weight: float = Field(
        default=0.3,
        description="Weight for BM25 search in RRF merge (0.0-1.0)",
    )
    rrf_k: int = Field(
        default=60,
        description="RRF k parameter for rank fusion (1-100)",
    )
    top_k: int = Field(
        default=5,
        description="Number of results to return (1-20)",
    )
    min_score: float = Field(
        default=0.1,
        description="Minimum relevance score threshold (0.0-1.0)",
    )

    updated_at: str = Field(description="When last updated (ISO 8601)")
    updated_by: str | None = Field(
        default=None,
        description="Who last updated the config",
    )


class ContactMessageDocument(BaseModel):
    """Persisted Contact Us form submission (SPEC-1588).

    Each submission from the merchant admin Contact Us modal is stored
    here in addition to being dispatched via email. Partitioned by
    tenant_id for efficient per-tenant queries; cross-partition queries
    used for superadmin dashboards. Status lifecycle: new → read →
    resolved → archived (SPEC-1592).
    """

    id: str = Field(description="UUID for this message")
    tenant_id: str = Field(description="Partition key — originating tenant")
    topic: str = Field(
        description="Message category: support, feature_request, billing, bug_report, general",
    )
    subject: str = Field(description="Subject line (max 200 chars)")
    message: str = Field(description="Full message body (max 5000 chars)")
    member_email: str | None = Field(
        default=None, description="Team member email who sent the message",
    )
    member_role: str | None = Field(
        default=None, description="Team member role (admin, viewer, etc.)",
    )
    member_id: str | None = Field(
        default=None, description="Team member ID",
    )
    tier: str | None = Field(
        default=None, description="Tenant tier at time of submission",
    )
    status: str = Field(
        default="new",
        description="Lifecycle status: new, read, resolved, archived",
    )
    notes: str = Field(
        default="",
        description="Operator annotations / internal notes",
    )
    created_at: str = Field(description="When submitted (ISO 8601 UTC)")
    updated_at: str = Field(description="When last modified (ISO 8601 UTC)")

    VALID_STATUSES: ClassVar[list[str]] = ["new", "read", "resolved", "archived"]


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
    """Return collection configurations for all 19 containers.

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
        # 5. knowledge_bases (with DiskANN vector index — WI #209)
        CollectionConfig(
            name=COLLECTION_KNOWLEDGE_BASES,
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
                    {"path": "/content/?"},  # Full text excluded from range index
                    {"path": "/embedding/*"},  # Vector handled by vector index
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
                    [
                        {"path": "/is_active", "order": "ascending"},
                        {"path": "/embedded_at", "order": "descending"},
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
                    [
                        {"path": "/config_state", "order": "ascending"},
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
        # 11. sla_snapshots (C-2: SLA persistence — hourly + daily rollups)
        CollectionConfig(
            name=COLLECTION_SLA_SNAPSHOTS,
            partition_key="/snapshot_type",
            default_ttl=TTL_SLA_SNAPSHOTS,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/per_tenant/*"},  # Embedded tenant data excluded from range index
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/snapshot_type", "order": "ascending"},
                        {"path": "/timestamp", "order": "descending"},
                    ],
                ],
            },
        ),
        # 12. verification_tokens (email verification, magic links — short TTL)
        CollectionConfig(
            name=COLLECTION_VERIFICATION_TOKENS,
            partition_key="/token_type",
            default_ttl=TTL_VERIFICATION_TOKEN,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
            },
        ),
        # 13. incidents (HV-5: status page — incident management)
        CollectionConfig(
            name=COLLECTION_INCIDENTS,
            partition_key="/status",
            default_ttl=TTL_INCIDENTS,
            unique_keys=[["/incident_id"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/updates/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/status", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"},
                    ],
                    [
                        {"path": "/severity", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 14. alert_rules (RB-4: alerting — rule definitions)
        CollectionConfig(
            name=COLLECTION_ALERT_RULES,
            partition_key="/rule_type",
            unique_keys=[["/rule_id"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
            },
        ),
        # 15. alert_history (RB-4: alerting — firing history, 90-day TTL)
        CollectionConfig(
            name=COLLECTION_ALERT_HISTORY,
            partition_key="/alert_date",
            default_ttl=TTL_ALERT_HISTORY,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
                "compositeIndexes": [
                    [
                        {"path": "/alert_date", "order": "ascending"},
                        {"path": "/triggered_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 16. ingestion_jobs (KA-1: storefront ingestion — job tracking, 30-day TTL)
        CollectionConfig(
            name=COLLECTION_INGESTION_JOBS,
            partition_key="/tenant_id",
            default_ttl=TTL_INGESTION_JOBS,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/entry_ids/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/tenant_id", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"},
                    ],
                    [
                        {"path": "/status", "order": "ascending"},
                        {"path": "/created_at", "order": "ascending"},
                    ],
                ],
            },
        ),
        # 17. pii_token_mappings (Phase 6: reversible PII tokenization, 7-day TTL)
        CollectionConfig(
            name=COLLECTION_PII_TOKEN_MAPPINGS,
            partition_key="/tenant_id",
            default_ttl=TTL_PII_TOKEN_MAPPINGS,
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/mappings/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/tenant_id", "order": "ascending"},
                        {"path": "/conversation_id", "order": "ascending"},
                    ],
                    [
                        {"path": "/tenant_id", "order": "ascending"},
                        {"path": "/updated_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 18. admin_documentation_vectors (SPEC-1559: Co-pilot shared docs, DiskANN)
        CollectionConfig(
            name=COLLECTION_ADMIN_DOCUMENTATION,
            partition_key="/document_category",
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
                    {"path": "/content/?"},
                    {"path": "/embedding/*"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/document_category", "order": "ascending"},
                        {"path": "/is_active", "order": "ascending"},
                    ],
                    [
                        {"path": "/is_active", "order": "ascending"},
                        {"path": "/embedded_at", "order": "descending"},
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
        # 19. contact_messages (SPEC-1588: persisted Contact Us submissions)
        CollectionConfig(
            name=COLLECTION_CONTACT_MESSAGES,
            partition_key="/tenant_id",
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [
                    {"path": "/message/?"},
                    {"path": "/notes/?"},
                    {"path": '/"_etag"/?'},
                ],
                "compositeIndexes": [
                    [
                        {"path": "/status", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"},
                    ],
                    [
                        {"path": "/topic", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"},
                    ],
                ],
            },
        ),
        # 20. platform_admins (SPEC-1667: SPA authentication isolation)
        # Stores Service Provider Administrator credentials, completely
        # isolated from all tenant team_members collections.
        CollectionConfig(
            name=COLLECTION_PLATFORM_ADMINS,
            partition_key="/admin_id",
            unique_keys=[["/email"]],
            indexing_policy={
                "automatic": True,
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tier defaults (Decision #5 — rate limits, Decision #14 — concurrency)
# ---------------------------------------------------------------------------

# SPEC-1803: Data-driven RPM default from ramp-to-overload testing (2026-03-14).
# 1,380 RPM safe capacity per replica. 300 RPM/tenant allows 9 concurrent
# max-rate tenants before single-replica saturation. Production min=2 replicas
# doubles this to 18. SPEC-1805: minimum floor is 10 RPM.
RATE_LIMIT_RPM_DEFAULT = 300
RATE_LIMIT_RPM_FLOOR = 10

TIER_DEFAULTS: dict[str, dict[str, Any]] = {
    # Trial: Full professional-grade entitlements for 14 days.
    # After expiry the merchant chooses Basic, Professional, Professional+, or Enterprise.
    TenantTier.TRIAL.value: {
        "included_conversations": 5_000,
        "memory_layers": [1, 2, 3],
        "overage_rate": 0.0,            # No overage during trial — hard cap
        "trial_duration_days": 14,      # 14-day trial period
        "rate_limit_rpm": RATE_LIMIT_RPM_DEFAULT,
    },
    TenantTier.STARTER.value: {
        "included_conversations": 1_000,
        "memory_layers": [1, 2],
        "overage_rate": 0.04,
        "rate_limit_rpm": RATE_LIMIT_RPM_DEFAULT,
    },
    TenantTier.PROFESSIONAL.value: {
        "included_conversations": 5_000,
        "memory_layers": [1, 2, 3],
        "overage_rate": 0.025,
        "rate_limit_rpm": RATE_LIMIT_RPM_DEFAULT,
    },
    TenantTier.ENTERPRISE.value: {
        "included_conversations": 20_000,
        "memory_layers": [1, 2, 3, 4],
        "overage_rate": 0.015,
        "rate_limit_rpm": RATE_LIMIT_RPM_DEFAULT,
    },
}


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------


async def initialize_database(
    client: Any,
    database_name: str = DATABASE_NAME,
) -> dict[str, Any]:
    """Create the database and all 11 containers if they don't exist.

    This function is idempotent — safe to call on every application
    startup. It uses create_if_not_exists semantics for both the
    database and each container.

    Args:
        client: An azure.cosmos.aio.CosmosClient instance.
        database_name: Database name (default: agentred).

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
