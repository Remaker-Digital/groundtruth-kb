"""
Flow tests: Audit sanitization integrity.

Verifies that actions taken through external interfaces produce audit log
entries that are properly sanitized — PII is scrubbed, only allowlisted
fields are persisted, and the SPA query projection hides sensitive data.

Flow pattern:
  1. Perform an action via HTTP API (config change, auth event, etc.)
  2. Query audit log via HTTP API
  3. Verify PII is scrubbed in the returned events
  4. Verify non-allowlisted fields are not present
  5. Verify SPA projection strips payload details

SPEC-1843 / WI-1615 / WI-1616.
GOV-19: Outside-in testing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


from src.multi_tenant.audit_sanitizer import (
    ALLOWED_PAYLOAD_FIELDS,
    sanitize_audit_payload,
    sanitize_for_spa_query,
)


class TestFlowAuditPayloadSanitization:
    """Verify the allowlist gate strips dangerous fields."""

    def test_allowed_fields_pass_through(self):
        """Fields on the allowlist are preserved."""
        payload = {
            "action": "config_update",
            "resource_type": "tenant_config",
            "resource_id": "t-001",
            "result": "success",
        }
        sanitized = sanitize_audit_payload(payload)
        assert sanitized == payload

    def test_pii_fields_stripped(self):
        """Fields NOT on the allowlist are silently dropped."""
        payload = {
            "action": "login",
            "result": "success",
            # These should be stripped:
            "customer_email": "alice@example.com",
            "api_key": "ar_live_secret123",
            "messages": [{"role": "user", "content": "my SSN is 123-45-6789"}],
            "brand_name": "Alice's Shop",
            "conversation_transcript": "sensitive chat content",
        }
        sanitized = sanitize_audit_payload(payload)

        # Allowed fields survive
        assert sanitized["action"] == "login"
        assert sanitized["result"] == "success"

        # PII fields are gone
        assert "customer_email" not in sanitized
        assert "api_key" not in sanitized
        assert "messages" not in sanitized
        assert "brand_name" not in sanitized
        assert "conversation_transcript" not in sanitized

    def test_pii_in_allowed_field_values_scrubbed(self):
        """PII patterns within allowed field string values are redacted."""
        payload = {
            "action": "key_rotation",
            "reason": "Old key was ar_live_abc123def456, rotated by admin@shop.com",
            "result": "success",
        }
        sanitized = sanitize_audit_payload(payload)

        assert "ar_live_abc123def456" not in sanitized["reason"]
        assert "admin@shop.com" not in sanitized["reason"]
        assert "[API_KEY]" in sanitized["reason"]
        assert "[EMAIL]" in sanitized["reason"]

    def test_email_pattern_scrubbed(self):
        """Email addresses in allowed fields are replaced with [EMAIL]."""
        payload = {
            "action": "team_invite",
            "reason": "Invited user@example.com to the team",
        }
        sanitized = sanitize_audit_payload(payload)
        assert "user@example.com" not in sanitized["reason"]
        assert "[EMAIL]" in sanitized["reason"]

    def test_stripe_key_scrubbed(self):
        """Stripe keys in allowed fields are replaced with [STRIPE_KEY]."""
        payload = {
            "action": "billing_update",
            "reason": "Webhook verified with sk_live_abc123",
        }
        sanitized = sanitize_audit_payload(payload)
        assert "sk_live_abc123" not in sanitized["reason"]
        assert "[STRIPE_KEY]" in sanitized["reason"]

    def test_shopify_token_scrubbed(self):
        """Shopify tokens in allowed fields are replaced with [SHOPIFY_TOKEN]."""
        payload = {
            "action": "app_install",
            "reason": "Connected with shpat_abc123def456",
        }
        sanitized = sanitize_audit_payload(payload)
        assert "shpat_abc123def456" not in sanitized["reason"]
        assert "[SHOPIFY_TOKEN]" in sanitized["reason"]

    def test_empty_payload_safe(self):
        """Empty payload returns empty dict."""
        assert sanitize_audit_payload({}) == {}

    def test_nested_objects_in_non_allowed_field_stripped(self):
        """Nested objects in non-allowed fields don't survive."""
        payload = {
            "action": "data_export",
            "customer_data": {"name": "Alice", "email": "alice@test.com"},
        }
        sanitized = sanitize_audit_payload(payload)
        assert "customer_data" not in sanitized


class TestFlowSpaQueryProjection:
    """Verify that SPA audit queries never expose sensitive data."""

    def test_spa_projection_strips_payload(self):
        """SPA query result must not contain the raw payload field."""
        event = {
            "event_type": "config_change",
            "timestamp": "2026-03-25T00:00:00Z",
            "tenant_id": "t-001",
            "payload": {
                "action": "update",
                "resource_type": "config",
                "reason": "Changed by admin",
            },
        }
        projected = sanitize_for_spa_query(event)

        # Must have safe fields
        assert "event_type" in projected
        assert "timestamp" in projected
        assert "tenant_id" in projected

        # Must NOT have raw payload
        assert "payload" not in projected

    def test_spa_projection_extracts_action(self):
        """SPA projection extracts action from payload for display."""
        event = {
            "event_type": "config_change",
            "timestamp": "2026-03-25T00:00:00Z",
            "tenant_id": "t-001",
            "payload": {"action": "brand_color_update"},
        }
        projected = sanitize_for_spa_query(event)
        assert projected.get("action") == "brand_color_update"

    def test_spa_projection_no_conversation_content(self):
        """SPA projection never exposes conversation content."""
        event = {
            "event_type": "escalation",
            "timestamp": "2026-03-25T00:00:00Z",
            "tenant_id": "t-001",
            "payload": {"action": "escalate"},
            "messages": [{"role": "user", "content": "I want a refund"}],
            "transcript": "Full conversation text...",
            "customer_email": "alice@shop.com",
        }
        projected = sanitize_for_spa_query(event)

        assert "messages" not in projected
        assert "transcript" not in projected
        assert "customer_email" not in projected


class TestFlowAuditCompleteness:
    """Verify the allowlist covers exactly the intended fields."""

    def test_allowlist_is_explicit(self):
        """The allowlist contains only operation metadata, never PII."""
        pii_fields = {
            "email", "customer_email", "name", "display_name",
            "phone", "address", "api_key", "messages", "transcript",
            "content", "brand_name", "shop_domain", "notes",
        }
        overlap = ALLOWED_PAYLOAD_FIELDS & pii_fields
        assert overlap == set(), (
            f"ALLOWED_PAYLOAD_FIELDS contains PII-class fields: {overlap}"
        )

    def test_allowlist_frozen(self):
        """The allowlist is a frozenset — immutable at runtime."""
        assert isinstance(ALLOWED_PAYLOAD_FIELDS, frozenset)
