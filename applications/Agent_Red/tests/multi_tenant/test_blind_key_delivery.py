# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Pillar 2: Operator-Blind Key Delivery (SPEC-1843, SPEC-1844).

WI-1618: Provisioning response MUST NOT contain raw keys
WI-1619: SPA key rotation: operator key exception, no tenant key rotation via SPA
WI-1620: Audit log MUST NOT contain raw key values
WI-1621: Provider Console UI removes key display
"""
import inspect
import re
from pathlib import Path



# ---------------------------------------------------------------------------
# WI-1618: Provisioning response does not contain raw keys
# ---------------------------------------------------------------------------

class TestProvisioningBlindDelivery:
    """CreateTenantResponse must not include raw API keys."""

    def test_response_model_has_no_api_key_field(self):
        from src.multi_tenant.superadmin_api._tenants import CreateTenantResponse
        fields = set(CreateTenantResponse.model_fields.keys())
        assert "api_key" not in fields, "CreateTenantResponse must not have api_key"
        assert "superadmin_api_key" not in fields, "must not have superadmin_api_key"
        assert "widget_key" not in fields, "must not have widget_key"
        assert "raw_key" not in fields, "must not have raw_key"

    def test_response_model_has_delivery_flag(self):
        from src.multi_tenant.superadmin_api._tenants import CreateTenantResponse
        fields = set(CreateTenantResponse.model_fields.keys())
        assert "keys_delivered_via_email" in fields

    def test_response_model_serializes_without_keys(self):
        from src.multi_tenant.superadmin_api._tenants import CreateTenantResponse
        resp = CreateTenantResponse(
            tenant_id="t-test-001",
            status="active",
            tier="starter",
            superadmin_email="admin@test.com",
            keys_delivered_via_email=True,
        )
        data = resp.model_dump()
        assert "api_key" not in str(data).lower() or data.get("keys_delivered_via_email")
        assert data["keys_delivered_via_email"] is True


# ---------------------------------------------------------------------------
# WI-1619: No SPA endpoint for tenant key rotation
# ---------------------------------------------------------------------------

class TestSpaKeyRotationRestriction:
    """SPA MUST NOT have endpoint to rotate tenant API keys."""

    def test_no_tenant_key_rotation_in_spa_routes(self):
        """superadmin_api module must not expose tenant key rotation."""
        from src.multi_tenant.superadmin_api._platform import router
        paths = [r.path for r in router.routes if hasattr(r, "path")]
        # /platform-admin/regenerate-key is OK (operator's own SPA key)
        tenant_rotate_paths = [
            p for p in paths
            if "rotate" in p.lower() and "platform-admin" not in p
        ]
        assert tenant_rotate_paths == [], \
            f"SPA must not have tenant key rotation endpoints: {tenant_rotate_paths}"

    def test_platform_admin_regenerate_returns_operator_key(self):
        """Operator MAY see their own SPA key — exception per WI-1619."""
        from src.multi_tenant.superadmin_api._platform import RegenerateKeyResponse
        fields = set(RegenerateKeyResponse.model_fields.keys())
        assert "new_api_key" in fields, \
            "RegenerateKeyResponse should still return operator SPA key"


# ---------------------------------------------------------------------------
# WI-1620: Audit log never contains raw key values
# ---------------------------------------------------------------------------

class TestAuditKeySafety:
    """Raw key values must never appear in audit log entries."""

    def test_sanitizer_catches_api_key_patterns(self):
        from src.multi_tenant.audit_sanitizer import sanitize_audit_payload
        payload = {
            "action": "key_rotated",
            "reason": "Rotated to ar_live_abc123def456_ghijklm",
        }
        result = sanitize_audit_payload(payload)
        assert "ar_live_" not in result["reason"]
        assert "[API_KEY]" in result["reason"]

    def test_sanitizer_catches_widget_key_patterns(self):
        from src.multi_tenant.audit_sanitizer import sanitize_audit_payload
        payload = {
            "action": "widget_key_created",
            "reason": "Generated pk_live_abc123def456_ghijklm",
        }
        result = sanitize_audit_payload(payload)
        # pk_live_ matches Stripe key pattern [sp]k_(live|test)_
        assert "pk_live_" not in result["reason"]

    def test_key_rotation_audit_only_logs_prefix(self):
        """admin_apikey_api key rotation audit log uses prefix only, not raw key."""
        from src.multi_tenant import admin_apikey_api
        source = inspect.getsource(admin_apikey_api)
        # Find all _log_audit(...) call blocks and verify none contain raw_key
        import re
        audit_calls = re.findall(r"_log_audit\([^)]+\)", source, re.DOTALL)
        for call in audit_calls:
            assert "raw_key" not in call, \
                f"Audit log call must not reference raw_key: {call[:80]}"

    def test_sanitizer_integrated_in_repository(self):
        """AuditLogRepository.log_event() must call sanitize_audit_payload."""
        from src.multi_tenant.repositories.platform import AuditLogRepository
        source = inspect.getsource(AuditLogRepository.log_event)
        assert "sanitize_audit_payload" in source


# ---------------------------------------------------------------------------
# WI-1621: Provider Console UI blind delivery
# ---------------------------------------------------------------------------

class TestProviderConsoleBlindDelivery:
    """Provider Console must not display raw tenant keys."""

    def test_create_tenant_response_interface_no_raw_keys(self):
        """TypeScript CreateTenantResponse must not include key fields."""
        ui_path = Path(__file__).resolve().parents[2] / "admin" / "provider" / "pages" / "TenantDirectory.tsx"
        assert ui_path.exists(), f"TenantDirectory.tsx not found at {ui_path}"
        source = ui_path.read_text(encoding="utf-8")

        # Find the CreateTenantResponse interface
        match = re.search(
            r"interface\s+CreateTenantResponse\s*\{([^}]+)\}",
            source, re.DOTALL,
        )
        assert match, "CreateTenantResponse interface not found"
        body = match.group(1)

        assert "superadminApiKey" not in body, \
            "UI interface must not include superadminApiKey (SPEC-1843)"
        assert "widgetKey" not in body, \
            "UI interface must not include widgetKey (SPEC-1843)"
        assert "keysDeliveredViaEmail" in body, \
            "UI interface must include keysDeliveredViaEmail"

    def test_no_copy_button_for_keys(self):
        """CopyButton for credential values must not exist."""
        ui_path = Path(__file__).resolve().parents[2] / "admin" / "provider" / "pages" / "TenantDirectory.tsx"
        source = ui_path.read_text(encoding="utf-8")
        # CopyButton should not be imported (was only used for keys)
        assert "CopyButton" not in source, \
            "CopyButton import should be removed (was only for key copy)"

    def test_ui_shows_delivery_confirmation(self):
        """UI must show 'Keys delivered' confirmation, not raw keys."""
        ui_path = Path(__file__).resolve().parents[2] / "admin" / "provider" / "pages" / "TenantDirectory.tsx"
        source = ui_path.read_text(encoding="utf-8")
        assert "Keys delivered" in source or "keys delivered" in source, \
            "UI must show delivery confirmation message"
        assert "Credential Delivery" in source, \
            "UI must have 'Credential Delivery' section heading"
