# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for audit log sanitizer (SPEC-1843 / WI-1615, WI-1616, WI-1617).

Validates that the sanitizer:
1. Strips PII-denylisted fields unconditionally
2. Strips non-allowlisted fields from audit payloads
3. Scrubs PII patterns (email, API key, phone, TOTP) from string values
4. Truncates long string content
5. Recursively scrubs nested structures
6. Passes allowlisted operational fields unchanged
7. Is integrated into AuditLogRepository.log_event()
8. SPA query projection returns only safe fields
"""
import inspect
import pytest


# ---------------------------------------------------------------------------
# WI-1615: audit_sanitizer.py — denylist + allowlist + PII regex gate
# ---------------------------------------------------------------------------

class TestSanitizeAuditPayload:
    """sanitize_audit_payload() strips PII and non-allowlisted fields."""

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
            "reason": "User requested",
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

    def test_expanded_operational_fields_retained(self):
        payload = {
            "auth_method": "api_key",
            "key_suffix": "abc12345",
            "path": "/api/chat",
            "method": "POST",
            "client_ip": "10.0.0.1",
            "from_version": 3,
            "to_version": 4,
            "fields_changed": ["greeting", "theme"],
            "change_count": 2,
            "deploy_id": "deploy-001",
            "environment": "staging",
            "tier": "professional",
            "role": "admin",
            "version": "1.98.82",
        }
        result = self._sanitize(payload)
        assert result == payload

    # -- PII denylist: unconditionally stripped --

    def test_pii_denylist_fields_stripped(self):
        payload = {
            "action": "create",
            "email": "alice@example.com",
            "customer_email": "bob@example.com",
            "name": "Alice Smith",
            "display_name": "Alice S.",
            "phone": "+15551234567",
            "api_key": "ar_live_secret",
            "widget_key": "wk_abc123",
            "totp_seed": "JBSWY3DPEHPK3PXP",
            "session_token": "tok_abc",
            "shopify_domain": "my-store.myshopify.com",
            "messages": [{"role": "user", "content": "help me"}],
            "content": "Full conversation text...",
            "body": "Email body...",
            "message": "Something sensitive",
            "diff_summary": "Changed email to...",
            "new_keys": ["key1"],
            "old_keys": ["key0"],
            "changes": {"field": {"old": "a", "new": "b"}},
            "metadata": {"source": "widget"},
        }
        result = self._sanitize(payload)
        assert result == {"action": "create"}

    def test_customer_field_stripped(self):
        payload = {"action": "export", "customer": "Alice Smith"}
        result = self._sanitize(payload)
        assert "customer" not in result

    def test_recovery_email_stripped(self):
        payload = {"action": "recover", "recovery_email": "recover@test.com"}
        result = self._sanitize(payload)
        assert "recovery_email" not in result

    def test_team_member_email_stripped(self):
        payload = {"action": "invite", "team_member_email": "member@co.com"}
        result = self._sanitize(payload)
        assert "team_member_email" not in result

    # -- Non-allowlisted, non-denylisted fields stripped --

    def test_unknown_fields_stripped(self):
        payload = {
            "action": "create",
            "brand_name": "Alice's Shop",
            "conversation_text": "Hello",
            "unknown_field": 42,
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
        payload = {"reason": "Key: ar_live_abc123def456"}
        result = self._sanitize(payload)
        assert "ar_live_abc123def456" not in result["reason"]
        assert "[API_KEY]" in result["reason"]

    def test_spa_key_pattern_scrubbed(self):
        payload = {"reason": "ar_spa_test1234567890"}
        result = self._sanitize(payload)
        assert "ar_spa_test" not in result["reason"]
        assert "[API_KEY]" in result["reason"]

    def test_stripe_key_pattern_scrubbed(self):
        payload = {"reason": "sk_live_51abc123XYZ"}
        result = self._sanitize(payload)
        assert "sk_live_" not in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_publishable_stripe_key_scrubbed(self):
        payload = {"reason": "pk_live_51abc123XYZ"}
        result = self._sanitize(payload)
        assert "pk_live_" not in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_stripe_restricted_key_scrubbed(self):
        payload = {"reason": "rk_live_51abc123XYZ"}
        result = self._sanitize(payload)
        assert "rk_live_" not in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    def test_shopify_token_pattern_scrubbed(self):
        payload = {"reason": "shpat_abc123def456"}
        result = self._sanitize(payload)
        assert "shpat_" not in result["reason"]
        assert "[SHOPIFY_TOKEN]" in result["reason"]

    def test_phone_pattern_scrubbed(self):
        payload = {"reason": "Called +1-555-123-4567"}
        result = self._sanitize(payload)
        assert "555-123-4567" not in result["reason"]
        assert "[PHONE]" in result["reason"]

    def test_phone_pattern_no_plus_scrubbed(self):
        payload = {"reason": "(555) 123-4567"}
        result = self._sanitize(payload)
        assert "555" not in result["reason"]
        assert "[PHONE]" in result["reason"]

    def test_totp_seed_pattern_scrubbed(self):
        payload = {"reason": "Seed JBSWY3DPEHPK3PXP enrolled"}
        result = self._sanitize(payload)
        assert "JBSWY3DPEHPK3PXP" not in result["reason"]
        assert "[TOTP_SEED]" in result["reason"]

    def test_multiple_pii_patterns_scrubbed(self):
        payload = {
            "reason": "alice@example.com ar_live_key123 sk_live_stripe456"
        }
        result = self._sanitize(payload)
        assert "[EMAIL]" in result["reason"]
        assert "[API_KEY]" in result["reason"]
        assert "[STRIPE_KEY]" in result["reason"]

    # -- Content truncation --

    def test_long_string_truncated(self):
        long_value = "x" * 150
        payload = {"reason": long_value}
        result = self._sanitize(payload)
        assert result["reason"] == "[redacted: 150 chars]"

    def test_short_string_not_truncated(self):
        payload = {"reason": "Short value"}
        result = self._sanitize(payload)
        assert result["reason"] == "Short value"

    def test_exactly_100_chars_not_truncated(self):
        value = "a" * 100
        payload = {"reason": value}
        result = self._sanitize(payload)
        assert result["reason"] == value

    # -- Recursive scrubbing --

    def test_list_values_scrubbed(self):
        payload = {"fields_changed": ["greeting", "alice@example.com"]}
        result = self._sanitize(payload)
        assert "alice@example.com" not in str(result["fields_changed"])
        assert "[EMAIL]" in result["fields_changed"][1]

    def test_nested_dict_pii_keys_stripped(self):
        """Nested dicts have PII denylist keys removed recursively."""
        payload = {"steps": {"phase": "deploy", "email": "leak@test.com"}}
        result = self._sanitize(payload)
        assert "email" not in result["steps"]
        assert result["steps"]["phase"] == "deploy"

    def test_numeric_values_not_scrubbed(self):
        payload = {"count": 42, "duration_ms": 1500, "status_code": 200}
        result = self._sanitize(payload)
        assert result == payload

    def test_nested_dicts_in_non_allowlisted_fields_stripped(self):
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
        assert set(result.keys()) == {
            "id", "event_type", "timestamp", "tenant_id",
            "actor", "actor_type", "action",
        }

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

    def test_spa_query_never_returns_conversation_id(self):
        event = {
            "event_type": "config.updated",
            "timestamp": "2026-03-24T12:00:00Z",
            "tenant_id": "t-001",
            "conversation_id": "conv-secret-123",
        }
        result = self._sanitize(event)
        assert "conversation_id" not in result


# ---------------------------------------------------------------------------
# Admin audit API: defense-in-depth sanitization on read path
# ---------------------------------------------------------------------------

class TestAdminAuditApiSanitization:
    """admin_audit_api reads payload (not details) and re-sanitizes."""

    def test_admin_audit_api_imports_sanitizer(self):
        import inspect
        import src.multi_tenant.admin_audit_api as mod
        source = inspect.getsource(mod)
        assert "sanitize_audit_payload" in source, \
            "admin_audit_api must import sanitize_audit_payload for read-path defense"

    def test_admin_audit_api_reads_payload_field(self):
        import inspect
        import src.multi_tenant.admin_audit_api as mod
        source = inspect.getsource(mod)
        assert 'e.get("payload")' in source, \
            "admin_audit_api must read from 'payload' field (not 'details')"


# ---------------------------------------------------------------------------
# Guard test: no direct _audit_repo.create() in superadmin modules (SPEC-1843)
# ---------------------------------------------------------------------------


class TestAuditWriteGuard:
    """Ensure all audit writes go through log_event() for sanitization."""

    def test_no_direct_audit_create_in_superadmin(self):
        """No superadmin module should call _audit_repo.create() directly.

        All audit writes must route through AuditLogRepository.log_event()
        which applies sanitize_audit_payload(). Direct .create() bypasses
        sanitization and violates SPEC-1843 Pillar 4.
        """
        import pathlib
        spa_dir = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "multi_tenant" / "superadmin_api"
        violations = []
        for py_file in spa_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if "_audit_repo.create(" in line and not line.strip().startswith("#"):
                    violations.append(f"{py_file.name}:{i}: {line.strip()}")
        assert not violations, (
            f"Direct _audit_repo.create() calls found — must use log_event() "
            f"for SPEC-1843 sanitization:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# Denylist / allowlist coverage guard
# ---------------------------------------------------------------------------


class TestSanitizerCoverage:
    """Verify denylist and allowlist are properly populated."""

    def test_pii_denylist_contains_required_fields(self):
        from src.multi_tenant.audit_sanitizer import PII_DENYLIST
        required = {
            "email", "customer_email", "name", "display_name", "phone",
            "api_key", "widget_key", "totp_seed", "shopify_domain",
            "messages", "content", "body", "session_token",
        }
        assert required.issubset(PII_DENYLIST)

    def test_pii_denylist_and_allowlist_disjoint(self):
        from src.multi_tenant.audit_sanitizer import (
            ALLOWED_PAYLOAD_FIELDS,
            PII_DENYLIST,
        )
        overlap = PII_DENYLIST & ALLOWED_PAYLOAD_FIELDS
        assert not overlap, f"Fields in both denylist and allowlist: {overlap}"
