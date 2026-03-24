# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for audit log sanitizer (SPEC-1843 / WI-1615, WI-1616, WI-1617).

Validates that the sanitizer:
1. Strips non-allowlisted fields from audit payloads
2. Scrubs PII patterns from string values
3. Passes allowlisted fields unchanged
4. Handles edge cases (empty, nested, None)
5. Is integrated into AuditLogRepository.log_event()
"""
import inspect
import pytest


# ---------------------------------------------------------------------------
# WI-1615: audit_sanitizer.py — allowlist + PII regex gate
# ---------------------------------------------------------------------------

class TestSanitizeAuditPayload:
    """sanitize_audit_payload() strips non-allowlisted fields and PII."""

    def _sanitize(self, payload: dict) -> dict:
        from src.multi_tenant.audit_sanitizer import sanitize_audit_payload
        return sanitize_audit_payload(payload)

    # -- Allowlisted fields pass through --

    def test_allowlisted_fields_retained(self):
        payload = {
            "action": "update",
            "resource_type": "config",
            "resource_id": "cfg-001",
            "result": "success",
            "reason": "User requested change",
            "count": 5,
            "duration_ms": 120,
            "status_code": 200,
        }
        result = self._sanitize(payload)
        assert result == payload

    def test_old_new_value_hash_retained(self):
        payload = {
            "old_value_hash": "sha256:abc123",
            "new_value_hash": "sha256:def456",
        }
        result = self._sanitize(payload)
        assert result == payload

    # -- Non-allowlisted fields stripped --

    def test_non_allowlisted_fields_stripped(self):
        payload = {
            "action": "create",
            "customer_email": "alice@example.com",
            "brand_name": "Alice's Shop",
            "conversation_text": "Hello, I need help with...",
            "totp_seed": "JBSWY3DPEHPK3PXP",
        }
        result = self._sanitize(payload)
        assert result == {"action": "create"}

    def test_empty_payload_returns_empty(self):
        assert self._sanitize({}) == {}

    def test_none_values_in_allowlisted_fields_retained(self):
        payload = {"action": "delete", "reason": None}
        result = self._sanitize(payload)
        assert result == {"action": "delete", "reason": None}

    # -- PII regex scrubbing on string values --

    def test_email_pattern_scrubbed(self):
        payload = {"reason": "Changed by alice@example.com"}
        result = self._sanitize(payload)
        assert "alice@example.com" not in result["reason"]
        assert "[EMAIL]" in result["reason"]

    def test_api_key_pattern_scrubbed(self):
        payload = {"reason": "Key rotated: ar_live_abc123def456"}
        result = self._sanitize(payload)
        assert "ar_live_abc123def456" not in result["reason"]
        assert "[API_KEY]" in result["reason"]

    def test_spa_key_pattern_scrubbed(self):
        payload = {"reason": "SPA key ar_spa_test1234567890 used"}
        result = self._sanitize(payload)
        assert "ar_spa_test" not in result["reason"]
        assert "[API_KEY]" in result["reason"]

    def test_stripe_key_pattern_scrubbed(self):
        payload = {"reason": "Stripe key sk_live_51abc123XYZ used"}
        result = self._sanitize(payload)
        assert "sk_live_" not in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_publishable_stripe_key_scrubbed(self):
        payload = {"reason": "Used pk_live_51abc123XYZ"}
        result = self._sanitize(payload)
        assert "pk_live_" not in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_shopify_token_pattern_scrubbed(self):
        payload = {"reason": "Shopify token shpat_abc123def456 expired"}
        result = self._sanitize(payload)
        assert "shpat_" not in result["reason"]
        assert "[SHOPIFY_TOKEN]" in result["reason"]

    def test_multiple_pii_patterns_scrubbed(self):
        payload = {
            "reason": "alice@example.com rotated ar_live_key123 via sk_live_stripe456"
        }
        result = self._sanitize(payload)
        assert "[EMAIL]" in result["reason"]
        assert "[API_KEY]" in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_numeric_values_not_scrubbed(self):
        """Non-string values pass through without regex scrubbing."""
        payload = {"count": 42, "duration_ms": 1500, "status_code": 200}
        result = self._sanitize(payload)
        assert result == payload

    def test_nested_dicts_stripped(self):
        """Nested dicts in non-allowlisted fields are stripped entirely."""
        payload = {
            "action": "update",
            "details": {"customer_name": "Alice", "phone": "+1234567890"},
        }
        result = self._sanitize(payload)
        assert result == {"action": "update"}


# ---------------------------------------------------------------------------
# WI-1616: Integration — sanitizer wired into AuditLogRepository.log_event()
# ---------------------------------------------------------------------------

class TestAuditRepositoryIntegration:
    """Verify sanitizer is called in the audit write path."""

    def test_log_event_calls_sanitize_audit_payload(self):
        """AuditLogRepository.log_event() must import and call sanitize_audit_payload."""
        from src.multi_tenant.repositories.platform import AuditLogRepository
        source = inspect.getsource(AuditLogRepository.log_event)
        assert "sanitize_audit_payload" in source, \
            "log_event() must call sanitize_audit_payload (WI-1616)"

    def test_log_event_uses_sanitized_payload(self):
        """log_event() must use sanitized_payload, not raw payload."""
        from src.multi_tenant.repositories.platform import AuditLogRepository
        source = inspect.getsource(AuditLogRepository.log_event)
        assert "sanitized_payload" in source, \
            "log_event() must assign sanitize result to sanitized_payload"


# ---------------------------------------------------------------------------
# WI-1617: SPA audit query restriction
# ---------------------------------------------------------------------------

class TestSanitizeForSpaQuery:
    """sanitize_for_spa_query() returns only SPA-safe fields (WI-1617)."""

    def _sanitize(self, event: dict) -> dict:
        from src.multi_tenant.audit_sanitizer import sanitize_for_spa_query
        return sanitize_for_spa_query(event)

    def test_spa_query_returns_only_safe_fields(self):
        event = {
            "id": "evt-001",
            "event_type": "config.updated",
            "timestamp": "2026-03-24T12:00:00Z",
            "tenant_id": "t-starter-001",
            "actor": "system",
            "actor_type": "admin",
            "payload": {"action": "update", "customer_email": "secret@example.com"},
            "conversation_id": "conv-123",
            "request_id": "req-456",
        }
        result = self._sanitize(event)
        assert set(result.keys()) == {"event_type", "timestamp", "tenant_id", "action"}

    def test_spa_query_extracts_action_from_payload(self):
        event = {
            "event_type": "tenant.created",
            "timestamp": "2026-03-24T12:00:00Z",
            "tenant_id": "t-pro-001",
            "payload": {"action": "create"},
        }
        result = self._sanitize(event)
        assert result["action"] == "create"

    def test_spa_query_action_none_when_no_payload(self):
        event = {
            "event_type": "security.event",
            "timestamp": "2026-03-24T12:00:00Z",
            "tenant_id": "t-ent-001",
        }
        result = self._sanitize(event)
        assert result["action"] is None

    def test_spa_query_never_returns_payload(self):
        event = {
            "event_type": "data.exported",
            "timestamp": "2026-03-24T12:00:00Z",
            "tenant_id": "t-001",
            "payload": {
                "action": "export",
                "file_url": "https://storage.example.com/export.zip",
                "customer_data": "sensitive",
            },
        }
        result = self._sanitize(event)
        assert "payload" not in result
        assert "file_url" not in result
        assert "customer_data" not in result
