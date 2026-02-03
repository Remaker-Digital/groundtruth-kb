"""Test data fixtures for Persistent Customer Memory (WI #100, Decision #32).

Synthetic profiles, transcripts, purchases, carts, vector data, and
fine-tuning configuration for deterministic testing across all 4 memory layers.

Usage:
    from tests.persistent_memory.fixtures import (
        TENANT_STARTER, TENANT_PROFESSIONAL, TENANT_ENTERPRISE,
        CUSTOMER_RETURNING, CUSTOMER_NEW, CUSTOMER_STALE,
        make_profile, make_conversation_messages, make_vector_results,
        make_fine_tuning_config, make_training_job, make_fine_tuned_model,
    )

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    ConversationDocument,
    ConversationStatus,
    CustomerProfileDocument,
    MemoryVectorDocument,
    PreferencesDocument,
    TenantDocument,
    TenantStatus,
    TenantTier,
)

# ---------------------------------------------------------------------------
# Constants — Tenant identifiers
# ---------------------------------------------------------------------------

TENANT_STARTER = "tenant-starter-001"
TENANT_PROFESSIONAL = "tenant-pro-001"
TENANT_ENTERPRISE = "tenant-ent-001"
TENANT_OTHER = "tenant-other-999"  # For cross-tenant isolation tests

# ---------------------------------------------------------------------------
# Constants — Customer identifiers
# ---------------------------------------------------------------------------

CUSTOMER_RETURNING = "cust-returning-alice"
CUSTOMER_NEW = "cust-new-bob"
CUSTOMER_STALE = "cust-stale-carol"
CUSTOMER_DENIED_CONSENT = "cust-denied-dave"
CUSTOMER_CASUAL = "cust-casual-emma"
CUSTOMER_ENTERPRISE = "cust-enterprise-frank"
CUSTOMER_HIGH_VOLUME = "cust-highvol-grace"


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------------
# Tenant fixtures
# ---------------------------------------------------------------------------


def make_tenant(
    tenant_id: str = TENANT_STARTER,
    tier: TenantTier = TenantTier.STARTER,
    status: TenantStatus = TenantStatus.ACTIVE,
) -> TenantDocument:
    """Create a tenant document for testing."""
    return TenantDocument(
        id=tenant_id,
        tenant_id=tenant_id,
        shop_domain=f"{tenant_id}.myshopify.com",
        tier=tier,
        status=status,
        billing_channel="shopify",
        subscription_id=f"sub_{tenant_id}",
        stripe_customer_id=f"cus_{tenant_id}",
        created_at=_days_ago(90),
        updated_at=_now(),
    )


# ---------------------------------------------------------------------------
# Customer profile fixtures
# ---------------------------------------------------------------------------


def make_profile(
    tenant_id: str = TENANT_STARTER,
    customer_id: str = CUSTOMER_RETURNING,
    *,
    consent: ConsentStatus = ConsentStatus.GRANTED,
    with_purchases: bool = True,
    with_cart: bool = True,
    with_questions: bool = True,
    with_region: bool = True,
    with_segments: bool = True,
    with_jurisdiction: bool = True,
    stale: bool = False,
    empty: bool = False,
) -> CustomerProfileDocument:
    """Create a customer profile with configurable data sources.

    Args:
        empty: If True, returns a profile with no data sources (L1-05).
        stale: If True, last_interaction_at is 120 days ago (L1-06).
    """
    now = _now()

    profile = CustomerProfileDocument(
        id=f"{tenant_id}:{customer_id}",
        tenant_id=tenant_id,
        customer_id=customer_id,
        consent_status=consent,
        created_at=_days_ago(180),
        updated_at=now,
        last_interaction_at=_days_ago(120) if stale else _days_ago(2),
    )

    if empty:
        return profile

    if with_purchases:
        profile.purchase_history = SAMPLE_PURCHASES.copy()
    if with_questions:
        profile.product_questions = SAMPLE_QUESTIONS.copy()
    if with_region:
        profile.region_codes = SAMPLE_REGION_CODES.copy()
    if with_segments:
        profile.marketing_segments = SAMPLE_MARKETING_SEGMENTS.copy()
    if with_jurisdiction:
        profile.jurisdiction_codes = SAMPLE_JURISDICTION_CODES.copy()
    if with_cart:
        profile.cart_contents = SAMPLE_CART_CONTENTS.copy()

    return profile


# ---------------------------------------------------------------------------
# Sample data — purchases
# ---------------------------------------------------------------------------

SAMPLE_PURCHASES: list[dict[str, Any]] = [
    {
        "product_id": "prod-organic-face-cream",
        "date": _days_ago(5),
        "rating": 5,
        "review_snippet": "Love this cream, very moisturizing",
    },
    {
        "product_id": "prod-vitamin-c-serum",
        "date": _days_ago(30),
        "rating": 4,
        "review_snippet": None,
    },
    {
        "product_id": "prod-sunscreen-spf50",
        "date": _days_ago(60),
        "rating": 3,
        "review_snippet": "A bit greasy but good protection",
    },
    {
        "product_id": "prod-retinol-night-cream",
        "date": _days_ago(90),
        "rating": 5,
        "review_snippet": "Game changer for my skin",
    },
    {
        "product_id": "prod-hyaluronic-acid",
        "date": _days_ago(120),
        "rating": 4,
        "review_snippet": None,
    },
]

# ---------------------------------------------------------------------------
# Sample data — product questions
# ---------------------------------------------------------------------------

SAMPLE_QUESTIONS: list[dict[str, Any]] = [
    {
        "question": "Is the organic face cream suitable for sensitive skin?",
        "product_id": "prod-organic-face-cream",
        "date": _days_ago(10),
        "resolved": True,
    },
    {
        "question": "Can I use vitamin C serum with retinol?",
        "product_id": "prod-vitamin-c-serum",
        "date": _days_ago(45),
        "resolved": True,
    },
    {
        "question": "What SPF level do you recommend for daily use?",
        "product_id": "prod-sunscreen-spf50",
        "date": _days_ago(65),
        "resolved": True,
    },
]

# ---------------------------------------------------------------------------
# Sample data — region codes
# ---------------------------------------------------------------------------

SAMPLE_REGION_CODES: dict[str, str] = {
    "shipping_region": "US",
    "availability_zone": "NA-EAST",
    "timezone": "America/New_York",
    "locale": "en-US",
}

# ---------------------------------------------------------------------------
# Sample data — marketing segments
# ---------------------------------------------------------------------------

SAMPLE_MARKETING_SEGMENTS: list[str] = [
    "skincare-enthusiast",
    "repeat-buyer",
    "premium-tier",
    "email-engaged",
]

# ---------------------------------------------------------------------------
# Sample data — jurisdiction codes
# ---------------------------------------------------------------------------

SAMPLE_JURISDICTION_CODES: dict[str, str] = {
    "country": "US",
    "state": "NY",
    "tax_region": "US-NY",
    "regulatory_framework": "US-FEDERAL",
}

# ---------------------------------------------------------------------------
# Sample data — cart contents
# ---------------------------------------------------------------------------

SAMPLE_CART_CONTENTS: dict[str, Any] = {
    "active": [
        {"product_id": "prod-eye-cream", "qty": 1},
        {"product_id": "prod-cleanser", "qty": 2},
    ],
    "abandoned": [
        {
            "product_id": "prod-toner",
            "qty": 1,
            "abandoned_at": _days_ago(14),
        },
    ],
}


# ---------------------------------------------------------------------------
# Conversation message fixtures
# ---------------------------------------------------------------------------


def make_conversation_messages(
    scenario: str = "return_inquiry",
    customer_name: str = "Alice",
) -> list[dict[str, Any]]:
    """Generate synthetic conversation transcripts.

    Scenarios:
        return_inquiry: Customer asking about a product return (L2-01)
        webhook_issue: Customer reporting a webhook problem (L2-02)
        shipping_policy: Customer asking about shipping (L2-03)
        general_greeting: Simple greeting (L1-01)
        feature_question: Question about plan features (L1-02)
        integration_sync: Integration sync issue (L1-03)
    """
    scenarios: dict[str, list[dict[str, Any]]] = {
        "return_inquiry": [
            {"role": "customer", "content": f"Hi, I'm {customer_name}. I need to return the organic face cream I bought last week.", "timestamp": _days_ago(3)},
            {"role": "assistant", "content": "I'd be happy to help with your return. I can see your recent purchase of the Organic Face Cream. Could you let me know the reason for the return?", "timestamp": _days_ago(3)},
            {"role": "customer", "content": "It caused a slight rash on my skin. I think I might be allergic to one of the ingredients.", "timestamp": _days_ago(3)},
            {"role": "assistant", "content": "I'm sorry to hear that. Your health is our priority. I've initiated a return for the Organic Face Cream (order from 5 days ago). You'll receive a full refund within 3-5 business days. I'd also recommend our Sensitive Skin line which is hypoallergenic.", "timestamp": _days_ago(3)},
            {"role": "customer", "content": "Thank you, that's very helpful!", "timestamp": _days_ago(3)},
        ],
        "webhook_issue": [
            {"role": "customer", "content": "My Shopify webhooks aren't firing for new orders. This started two weeks ago.", "timestamp": _days_ago(14)},
            {"role": "assistant", "content": "I can see your Shopify integration is active. Let me check the webhook configuration. Have you made any changes to your Shopify admin recently?", "timestamp": _days_ago(14)},
            {"role": "customer", "content": "I updated my Shopify theme last week, but the webhook issue started before that.", "timestamp": _days_ago(14)},
            {"role": "assistant", "content": "I've identified the issue — your webhook endpoint URL was changed during an API update. I've reconfigured it to point to the correct endpoint. New orders should start syncing within the next few minutes.", "timestamp": _days_ago(14)},
        ],
        "shipping_policy": [
            {"role": "customer", "content": "What's your shipping policy for international orders?", "timestamp": _days_ago(7)},
            {"role": "assistant", "content": "We ship internationally to over 50 countries. Standard international shipping takes 7-14 business days and costs $12.99. Express shipping (3-5 days) is available for $24.99. Free shipping on orders over $75 to the US and Canada.", "timestamp": _days_ago(7)},
            {"role": "customer", "content": "Do you ship to Australia?", "timestamp": _days_ago(7)},
            {"role": "assistant", "content": "Yes, we ship to Australia! Standard delivery to Australia typically takes 10-14 business days. You can track your package once it's shipped.", "timestamp": _days_ago(7)},
        ],
        "general_greeting": [
            {"role": "customer", "content": "Hi, I need help", "timestamp": _now()},
        ],
        "feature_question": [
            {"role": "customer", "content": "Can I use the advanced analytics dashboard?", "timestamp": _now()},
        ],
        "integration_sync": [
            {"role": "customer", "content": "My orders aren't syncing between Shopify and my account", "timestamp": _now()},
        ],
    }

    return scenarios.get(scenario, scenarios["general_greeting"])


# ---------------------------------------------------------------------------
# Conversation document fixtures
# ---------------------------------------------------------------------------


def make_conversation_doc(
    tenant_id: str = TENANT_STARTER,
    customer_id: str = CUSTOMER_RETURNING,
    conversation_id: str = "conv-001",
    status: ConversationStatus = ConversationStatus.COMPLETED,
    days_ago: int = 3,
) -> ConversationDocument:
    """Create a conversation document for testing."""
    return ConversationDocument(
        id=conversation_id,
        tenant_id=tenant_id,
        customer_id=customer_id,
        status=status,
        is_billable=True,
        message_count=5,
        turn_count=3,
        started_at=_days_ago(days_ago),
        ended_at=_days_ago(days_ago),
        created_at=_days_ago(days_ago),
    )


# ---------------------------------------------------------------------------
# Vector search result fixtures
# ---------------------------------------------------------------------------


def make_vector_results(
    tenant_id: str = TENANT_STARTER,
    customer_id: str = CUSTOMER_RETURNING,
    count: int = 3,
    *,
    high_similarity: bool = True,
    scenario: str = "return_inquiry",
) -> list[dict[str, Any]]:
    """Create synthetic vector search results.

    Used for testing compress_for_prompt() and search_history() outputs.
    """
    base_similarity = 0.92 if high_similarity else 0.45

    results = []
    for i in range(count):
        results.append({
            "chunk_text": f"customer: I need to return the organic face cream. assistant: I've initiated a return for your order. (chunk {i})" if scenario == "return_inquiry" else f"Conversation chunk {i} about {scenario}",
            "conversation_date": _days_ago(3 + i * 7),
            "similarity": round(base_similarity - (i * 0.05), 2),
            "conversation_id": f"conv-{100 + i}",
            "tenant_id": tenant_id,
            "customer_id": customer_id,
        })

    return results


# ---------------------------------------------------------------------------
# Preferences document fixtures
# ---------------------------------------------------------------------------


def make_preferences(
    tenant_id: str = TENANT_STARTER,
    *,
    brand_name: str = "GlowSkin Co",
    voice: str = "friendly",
    formality: str = "casual",
    response_length: str = "concise",
    custom_instructions: str = "",
) -> PreferencesDocument:
    """Create a preferences document for testing."""
    return PreferencesDocument(
        id=f"{tenant_id}:live",
        tenant_id=tenant_id,
        version=1,
        brand_name=brand_name,
        brand_voice=voice,
        formality_level=formality,
        response_length=response_length,
        custom_instructions=custom_instructions or None,
        escalation_keywords=[
            "legal action",
            "manager",
            "lawyer",
        ],
        return_policy="30-day return policy on all products",
        shipping_info="Free shipping on orders over $75",
        primary_language="en",
        created_at=_days_ago(60),
    )


# ---------------------------------------------------------------------------
# Shopify sync data fixtures
# ---------------------------------------------------------------------------

SAMPLE_SHOPIFY_SYNC_DATA: dict[str, Any] = {
    "orders": [
        {"product_id": "prod-new-moisturizer", "date": _days_ago(1)},
        {"product_id": "prod-lip-balm", "date": _days_ago(3)},
    ],
    "cart": {
        "active": [{"product_id": "prod-face-mask", "qty": 3}],
        "abandoned": [],
    },
    "customer": {
        "country_code": "CA",
        "province_code": "ON",
        "locale": "en-CA",
        "tags": ["vip-customer", "skincare-subscriber"],
    },
}


# ---------------------------------------------------------------------------
# Bulk conversation fixtures (for high-volume tests)
# ---------------------------------------------------------------------------


def make_bulk_conversations(
    tenant_id: str = TENANT_STARTER,
    customer_id: str = CUSTOMER_HIGH_VOLUME,
    count: int = 500,
) -> list[dict[str, Any]]:
    """Generate a large set of conversation message lists.

    Used for L2-06 (high-volume history search) testing.
    Each conversation is a minimal 2-message exchange.
    """
    conversations = []
    topics = [
        "shipping", "returns", "product quality", "billing",
        "integration setup", "webhook config", "order tracking",
        "account settings", "pricing", "feature request",
    ]

    for i in range(count):
        topic = topics[i % len(topics)]
        conversations.append([
            {
                "role": "customer",
                "content": f"I have a question about {topic} (conversation {i})",
                "timestamp": _days_ago(count - i),
            },
            {
                "role": "assistant",
                "content": f"I can help with {topic}. Here's what you need to know about {topic} for your account.",
                "timestamp": _days_ago(count - i),
            },
        ])

    return conversations


# ---------------------------------------------------------------------------
# Fine-tuning pipeline fixtures (WI #93-96, Layer 4)
# ---------------------------------------------------------------------------


def make_fine_tuning_config(
    tenant_id: str = TENANT_ENTERPRISE,
    *,
    enabled: bool = True,
    schedule: str = "monthly",
    min_conversations: int = 1000,
    active_model_id: str | None = None,
    active_model_version: int | None = None,
    ab_experiment_id: str | None = None,
) -> PreferencesDocument:
    """Create a PreferencesDocument configured for fine-tuning.

    Returns an Enterprise-tier preferences document with fine-tuning
    fields set.  Extends :func:`make_preferences` with Layer 4 fields.
    """
    prefs = make_preferences(
        tenant_id=tenant_id,
        brand_name="Enterprise Corp",
        voice="professional",
        formality="formal",
        response_length="detailed",
    )
    prefs.fine_tuning_enabled = enabled
    prefs.fine_tuning_schedule = schedule
    prefs.fine_tuning_min_conversations = min_conversations
    prefs.fine_tuning_active_model_id = active_model_id
    prefs.fine_tuning_active_model_version = active_model_version
    prefs.fine_tuning_ab_experiment_id = ab_experiment_id
    return prefs


def make_training_job(
    tenant_id: str = TENANT_ENTERPRISE,
    *,
    job_id: str = "ftjob-test-001",
    openai_job_id: str = "ftjob-abc123",
    status: str = "completed",
    base_model: str = "gpt-4o-mini",
    training_conversations: int = 1500,
    training_examples: int = 4500,
    validation_examples: int = 500,
    resulting_model_id: str | None = "ft:gpt-4o-mini:agentred:tenant-ent-001:v1",
    error_message: str | None = None,
) -> dict[str, Any]:
    """Create a TrainingJobRecord-compatible dict for testing.

    Returns a dict matching the TrainingJobRecord dataclass fields.
    """
    return {
        "id": job_id,
        "tenant_id": tenant_id,
        "job_id": job_id,
        "openai_job_id": openai_job_id,
        "status": status,
        "base_model": base_model,
        "training_conversations": training_conversations,
        "training_examples": training_examples,
        "validation_examples": validation_examples,
        "training_file_id": "file-train-abc123",
        "validation_file_id": "file-val-abc123",
        "resulting_model_id": resulting_model_id,
        "quality_report": None,
        "cost_estimate": 12.50,
        "error_message": error_message,
        "created_at": _days_ago(7),
        "started_at": _days_ago(7),
        "completed_at": _days_ago(6),
    }


def make_fine_tuned_model(
    tenant_id: str = TENANT_ENTERPRISE,
    *,
    model_id: str = "ft:gpt-4o-mini:agentred:tenant-ent-001:v1",
    model_version: int = 1,
    status: str = "deployed",
    base_model: str = "gpt-4o-mini",
    training_job_id: str = "ftjob-test-001",
    training_data_count: int = 1500,
    deployed_at: str | None = None,
    rolled_back_at: str | None = None,
    rollback_reason: str | None = None,
) -> dict[str, Any]:
    """Create a FineTunedModelRecord-compatible dict for testing.

    Returns a dict matching the FineTunedModelRecord dataclass fields.
    """
    return {
        "id": f"{tenant_id}:model:{model_version}",
        "tenant_id": tenant_id,
        "model_id": model_id,
        "model_version": model_version,
        "status": status,
        "base_model": base_model,
        "training_job_id": training_job_id,
        "training_data_count": training_data_count,
        "quality_report": None,
        "ab_experiment": None,
        "deployed_at": deployed_at or _days_ago(5),
        "rolled_back_at": rolled_back_at,
        "rollback_reason": rollback_reason,
        "created_at": _days_ago(6),
        "updated_at": _now(),
    }
