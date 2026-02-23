"""Tests for system prompt Layer 6 identity collection rules (P0-AUTH-FIX).

Covers:
    SystemPromptBuilder.build() Layer 6 injection — 4 tests
    1. Unverified conversation → Layer 6 = _IDENTITY_COLLECTION_RULES
    2. Verified conversation → no Layer 6 injected
    3. Shopify HMAC verified (customer_id present) → no Layer 6
    4. Anonymous after explicit skip → Layer 6 present with identity rules

The tests verify that the system prompt builder injects the correct
identity collection rules based on the is_anonymous parameter.

Run:
    pytest tests/chat/test_system_prompt_identity.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    SystemPromptBuilder,
    _ANONYMOUS_SESSION_RULES,
    _IDENTITY_COLLECTION_RULES,
)
from src.multi_tenant.cosmos_schema import TenantDocument, PreferencesDocument


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def builder():
    """Create a SystemPromptBuilder instance."""
    return SystemPromptBuilder()


@pytest.fixture()
def tenant():
    """Create a minimal TenantDocument."""
    return TenantDocument(
        id="test-tenant:1",
        tenant_id="test-tenant",
        tier="starter",
        status="active",
        billing_channel="manual",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


@pytest.fixture()
def preferences():
    """Create a minimal PreferencesDocument."""
    return PreferencesDocument(
        id="test-tenant:prefs:1",
        tenant_id="test-tenant",
        version=1,
        is_current=True,
        brand_name="Test Store",
        brand_voice="friendly and helpful",
        created_at="2026-01-01T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSystemPromptIdentityRules:
    """System prompt Layer 6 identity collection rules."""

    def test_unverified_conversation_injects_identity_rules(
        self, builder, tenant, preferences,
    ):
        """Unverified customer → Layer 6 = _IDENTITY_COLLECTION_RULES."""
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=True,
        )

        # Should contain the proactive identity collection rules
        assert "IDENTITY STATUS" in prompt
        assert "has NOT been identified" in prompt
        assert "In your FIRST response" in prompt
        assert "ask for their email address" in prompt

    def test_verified_conversation_no_layer_6(
        self, builder, tenant, preferences,
    ):
        """Verified customer (is_anonymous=False) → no Layer 6."""
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=False,
        )

        assert "IDENTITY STATUS" not in prompt
        assert "ANONYMOUS SESSION" not in prompt
        assert "_IDENTITY_COLLECTION_RULES" not in prompt

    def test_shopify_customer_no_layer_6(
        self, builder, tenant, preferences,
    ):
        """Shopify HMAC-verified customer (customer_id present) → no Layer 6.

        When customer_id is set (Shopify login), is_anonymous=False,
        so no identity rules are injected.
        """
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=False,  # Shopify customer has customer_id
        )

        assert "IDENTITY STATUS" not in prompt

    def test_anonymous_gets_identity_collection_not_anonymous_rules(
        self, builder, tenant, preferences,
    ):
        """Unverified user gets _IDENTITY_COLLECTION_RULES, not old rules.

        P0-AUTH-FIX changed Layer 6 from _ANONYMOUS_SESSION_RULES to
        _IDENTITY_COLLECTION_RULES. The AI proactively asks for email
        in its first response per the P0 mandate.
        """
        prompt = builder.build(
            agent=AgentRole.RESPONSE_GENERATOR,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=True,
        )

        # New rules: proactively ask for email in first response
        assert "In your FIRST response" in prompt
        assert "ask for their email address" in prompt
        # Old rules: warned at the start — should NOT be present
        assert "ANONYMOUS SESSION" not in prompt
        assert "Since you're chatting as a guest" not in prompt

    def test_identity_rules_on_escalation_handler_too(
        self, builder, tenant, preferences,
    ):
        """Identity rules are also injected for Escalation Handler."""
        prompt = builder.build(
            agent=AgentRole.ESCALATION_HANDLER,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=True,
        )

        assert "IDENTITY STATUS" in prompt

    def test_identity_rules_not_on_critic(
        self, builder, tenant, preferences,
    ):
        """Critic prompt is NEVER modified (immutable safety invariant)."""
        prompt = builder.build(
            agent=AgentRole.CRITIC_SUPERVISOR,
            tenant=tenant,
            preferences=preferences,
            is_anonymous=True,
        )

        assert "IDENTITY STATUS" not in prompt
        assert "ANONYMOUS SESSION" not in prompt
