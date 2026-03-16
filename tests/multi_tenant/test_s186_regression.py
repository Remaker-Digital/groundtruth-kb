"""
Regression tests for S186 bug fixes.

Covers:
    1. Widget auto-save: useAutoSaveDraft exposes triggerSave + uses saveRef
    2. Widget.tsx: non-text controls use updateAndSave (not plain update)
    3. Avatar upload: 413 error produces user-friendly file-size message
    4. widget_greeting_mode: field present in Cosmos schema + field_mapping
    5. Security middleware: 413 response includes both "error" and "max_bytes"

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ADMIN_SRC = ROOT / "admin"
WIDGET_PAGE = ADMIN_SRC / "standalone" / "pages" / "Widget.tsx"
AUTO_SAVE_HOOK = ADMIN_SRC / "shared" / "hooks" / "useAutoSaveDraft.ts"
AVATAR_HOOK = ADMIN_SRC / "shared" / "hooks" / "useAvatar.ts"


# ---------------------------------------------------------------------------
# 1. useAutoSaveDraft — ref-based save, triggerSave exposed
# ---------------------------------------------------------------------------


class TestAutoSaveDraftHook:
    """Verify useAutoSaveDraft uses a ref for the save function and exposes triggerSave."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        self.src = AUTO_SAVE_HOOK.read_text(encoding="utf-8")

    def test_save_ref_declared(self):
        """Hook must store save function in a ref to avoid stale closures."""
        assert "saveRef" in self.src, "useAutoSaveDraft must use a saveRef to avoid stale closure bugs"

    def test_save_ref_current_assigned(self):
        """saveRef.current must be updated on every render."""
        assert "saveRef.current = save" in self.src, (
            "saveRef.current must be assigned to the latest save function on each render"
        )

    def test_timer_calls_save_ref(self):
        """The debounce timer must call saveRef.current(), not the stale save closure."""
        assert "saveRef.current()" in self.src, (
            "Timer must call saveRef.current() to get the latest save function"
        )

    def test_trigger_save_exported(self):
        """Hook must expose triggerSave in its return value."""
        assert "triggerSave" in self.src, "useAutoSaveDraft must export triggerSave"
        # Verify it's in the return statement
        assert re.search(r"return\s*\{.*triggerSave", self.src, re.DOTALL), (
            "triggerSave must be in the return object of useAutoSaveDraft"
        )

    def test_on_blur_is_trigger_save(self):
        """onBlur should be the same function as triggerSave for backward compatibility."""
        assert "onBlur: triggerSave" in self.src, (
            "onBlur must alias triggerSave for backward compatibility"
        )


# ---------------------------------------------------------------------------
# 2. Widget.tsx — non-text controls use updateAndSave
# ---------------------------------------------------------------------------


class TestWidgetAutoSaveIntegration:
    """Verify Widget.tsx calls updateAndSave for non-text controls."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        self.src = WIDGET_PAGE.read_text(encoding="utf-8")

    def test_update_and_save_function_defined(self):
        """Widget.tsx must define updateAndSave helper."""
        assert "function updateAndSave" in self.src

    def test_trigger_save_destructured(self):
        """Widget.tsx must destructure triggerSave from useAutoSaveDraft."""
        assert "triggerSave" in self.src

    # --- SegmentedControl fields must use updateAndSave ---

    def test_panel_width_uses_update_and_save(self):
        """Panel width SegmentedControl must call updateAndSave (WI-1325)."""
        assert "updateAndSave('panelWidth'" in self.src

    def test_panel_height_uses_update_and_save(self):
        """Panel height SegmentedControl must call updateAndSave (WI-1325)."""
        assert "updateAndSave('panelHeight'" in self.src

    def test_shadow_intensity_uses_update_and_save(self):
        """Panel shadow SegmentedControl must call updateAndSave (WI-1325)."""
        assert "updateAndSave('shadowIntensity'" in self.src

    def test_color_mode_uses_update_and_save(self):
        """Color mode SegmentedControl must call updateAndSave."""
        assert "updateAndSave('colorMode'" in self.src

    def test_position_uses_update_and_save(self):
        """Position SegmentedControl must call updateAndSave."""
        assert "updateAndSave('position'" in self.src

    def test_greeting_mode_uses_update_and_save(self):
        """Greeting mode SegmentedControl must call updateAndSave."""
        assert "updateAndSave('greetingMode'" in self.src

    # --- Switch fields must use updateAndSave ---

    def test_greeting_enabled_uses_update_and_save(self):
        """Greeting enabled Switch must call updateAndSave."""
        assert "updateAndSave('greetingEnabled'" in self.src

    def test_sound_enabled_uses_update_and_save(self):
        """Sound enabled Switch must call updateAndSave."""
        assert "updateAndSave('soundEnabled'" in self.src

    def test_pre_chat_form_uses_update_and_save(self):
        """Pre-chat form Switch must call updateAndSave."""
        assert "updateAndSave('preChatFormEnabled'" in self.src

    def test_header_gradient_uses_update_and_save(self):
        """Header gradient Switch must call updateAndSave."""
        assert "updateAndSave('headerGradientEnabled'" in self.src

    def test_exit_intent_uses_update_and_save(self):
        """Exit intent Switch must call updateAndSave."""
        assert "updateAndSave('exitIntentEnabled'" in self.src

    def test_mobile_fullscreen_uses_update_and_save(self):
        """Mobile fullscreen Switch must call updateAndSave."""
        assert "updateAndSave('mobileFullscreen'" in self.src

    # --- Other non-text controls ---

    def test_launcher_color_uses_update_and_save(self):
        """Launcher color picker must call updateAndSave."""
        assert "updateAndSave('launcherColor'" in self.src

    def test_primary_color_uses_update_and_save(self):
        """Primary color picker must call updateAndSave."""
        assert "updateAndSave('primaryColor'" in self.src

    def test_font_family_uses_update_and_save(self):
        """Font family Select must call updateAndSave."""
        assert "updateAndSave('fontFamily'" in self.src

    def test_locale_uses_update_and_save(self):
        """Locale Select must call updateAndSave."""
        assert "updateAndSave('locale'" in self.src

    def test_pre_chat_fields_uses_update_and_save(self):
        """Pre-chat fields Chip.Group must call updateAndSave."""
        assert "updateAndSave('preChatFields'" in self.src

    # --- Text inputs must use plain update (saved via onBlur) ---

    def test_greeting_message_uses_plain_update(self):
        """Greeting message Textarea uses plain update (blur triggers save)."""
        assert "update('greetingMessage'" in self.src

    def test_header_title_uses_plain_update(self):
        """Header title TextInput uses plain update (blur triggers save)."""
        assert "update('headerTitle'" in self.src


# ---------------------------------------------------------------------------
# 3. Avatar upload — 413 error message
# ---------------------------------------------------------------------------


class TestAvatarUpload413ErrorMessage:
    """Verify useAvatar.ts handles 413 responses with user-friendly messages."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        self.src = AVATAR_HOOK.read_text(encoding="utf-8")

    def test_checks_for_413_status(self):
        """Frontend must check for resp.status === 413 specifically."""
        assert "resp.status === 413" in self.src, (
            "useAvatarUpload must handle 413 status code with a specific message"
        )

    def test_provides_file_size_hint(self):
        """413 error message must mention maximum file size."""
        assert "File too large" in self.src, (
            "413 error must tell user the file is too large"
        )
        assert "max_bytes" in self.src, (
            "413 handler should read max_bytes from response to show the limit"
        )

    def test_checks_body_error_field(self):
        """Frontend must check body.error (from middleware) in addition to body.detail."""
        assert "body.error" in self.src, (
            "useAvatarUpload must check body.error field from RequestBodyLimitMiddleware"
        )


# ---------------------------------------------------------------------------
# 4. widget_greeting_mode — schema + field_mapping coverage
# ---------------------------------------------------------------------------


class TestWidgetGreetingModeSchema:
    """Verify widget_greeting_mode is in Cosmos schema and field_mapping."""

    def test_greeting_mode_in_preferences_document(self):
        """widget_greeting_mode must be a field on PreferencesDocument."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        assert "widget_greeting_mode" in PreferencesDocument.model_fields, (
            "widget_greeting_mode must be defined in PreferencesDocument for persistence"
        )

    def test_greeting_mode_in_field_mapping(self):
        """widget_greeting_mode must be in _PREFS_DIRECT_FIELDS for the config pipeline."""
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS

        assert "widget_greeting_mode" in _PREFS_DIRECT_FIELDS, (
            "widget_greeting_mode must be in field_mapping._PREFS_DIRECT_FIELDS"
        )

    def test_greeting_mode_accepts_static(self):
        """widget_greeting_mode must accept 'static' value."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        doc = PreferencesDocument(
            id="test",
            tenant_id="t-test",
            version=1,
            created_at="2026-01-01T00:00:00Z",
            widget_greeting_mode="static",
        )
        assert doc.widget_greeting_mode == "static"

    def test_greeting_mode_accepts_ai_generated(self):
        """widget_greeting_mode must accept 'ai_generated' value."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        doc = PreferencesDocument(
            id="test",
            tenant_id="t-test",
            version=1,
            created_at="2026-01-01T00:00:00Z",
            widget_greeting_mode="ai_generated",
        )
        assert doc.widget_greeting_mode == "ai_generated"

    def test_greeting_mode_defaults_to_none(self):
        """widget_greeting_mode defaults to None for existing tenants."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        doc = PreferencesDocument(
            id="test",
            tenant_id="t-test",
            version=1,
            created_at="2026-01-01T00:00:00Z",
        )
        assert doc.widget_greeting_mode is None


# ---------------------------------------------------------------------------
# 5. Security middleware — 413 response shape
# ---------------------------------------------------------------------------


class TestMiddleware413ResponseShape:
    """Verify RequestBodyLimitMiddleware returns error + max_bytes in 413 response."""

    def test_413_response_has_error_field(self):
        """413 response body must include 'error' key."""
        from starlette.testclient import TestClient
        from src.multi_tenant.security_middleware import RequestBodyLimitMiddleware
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route

        async def handler(request):
            return PlainTextResponse("ok")

        app = Starlette(routes=[Route("/test", handler, methods=["POST"])])
        app = RequestBodyLimitMiddleware(app, max_body_size=10)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.post("/test", content=b"x" * 50, headers={"content-length": "50"})
        assert resp.status_code == 413
        body = resp.json()
        assert "error" in body, "413 response must include 'error' field"
        assert "max_bytes" in body, "413 response must include 'max_bytes' field"

    def test_413_error_message_contains_too_large(self):
        """413 error message must say 'too large'."""
        from starlette.testclient import TestClient
        from src.multi_tenant.security_middleware import RequestBodyLimitMiddleware
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route

        async def handler(request):
            return PlainTextResponse("ok")

        app = Starlette(routes=[Route("/test", handler, methods=["POST"])])
        app = RequestBodyLimitMiddleware(app, max_body_size=10)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.post("/test", content=b"x" * 50, headers={"content-length": "50"})
        body = resp.json()
        assert "too large" in body["error"].lower()


# ---------------------------------------------------------------------------
# 6. AI-generated greeting — template-based generation
# ---------------------------------------------------------------------------


class TestAIGeneratedGreeting:
    """Verify _generate_ai_greeting produces brand-aware, time-aware greetings."""

    def test_greeting_includes_brand_name(self):
        """Generated greeting must include the tenant's brand name."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        config = {"brand_name": "Acme Store"}
        greeting = _generate_ai_greeting(config)
        assert "Acme Store" in greeting, (
            f"Greeting must include brand name 'Acme Store', got: {greeting}"
        )

    def test_greeting_falls_back_to_agent_display_name(self):
        """When brand_name is absent, uses widget_agent_display_name."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        config = {"widget_agent_display_name": "Red Bot"}
        greeting = _generate_ai_greeting(config)
        assert "Red Bot" in greeting, (
            f"Greeting must include agent display name fallback, got: {greeting}"
        )

    def test_greeting_falls_back_to_us(self):
        """When no brand info available, uses 'us' as fallback."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        greeting = _generate_ai_greeting({})
        assert "us" in greeting.lower(), (
            f"Greeting must include 'us' fallback, got: {greeting}"
        )

    def test_greeting_is_nonempty_string(self):
        """Generated greeting must be a non-empty string."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        greeting = _generate_ai_greeting({"brand_name": "Test"})
        assert isinstance(greeting, str)
        assert len(greeting) > 10, "Greeting should be a meaningful message"

    def test_product_page_greeting_is_product_specific(self):
        """Product page greeting should reference the product context."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        greeting = _generate_ai_greeting({"brand_name": "Shop"}, page_type="product")
        # Product greetings mention product-related terms
        lower = greeting.lower()
        assert any(word in lower for word in ["product", "sizing", "questions", "help"]), (
            f"Product page greeting should be product-relevant, got: {greeting}"
        )

    def test_cart_page_greeting_is_checkout_specific(self):
        """Cart page greeting should reference checkout/order context."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        greeting = _generate_ai_greeting({"brand_name": "Shop"}, page_type="cart")
        lower = greeting.lower()
        assert any(word in lower for word in ["checkout", "order", "questions"]), (
            f"Cart page greeting should reference checkout, got: {greeting}"
        )

    def test_generic_page_uses_default_templates(self):
        """Unknown page type uses default greeting templates."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        greeting = _generate_ai_greeting({"brand_name": "Acme"}, page_type="blog")
        # Should still include brand name — uses default template
        assert "Acme" in greeting

    def test_greeting_varies_across_calls(self):
        """Greetings should have some variation (random template selection)."""
        from src.multi_tenant.tenant_config_api import _generate_ai_greeting

        config = {"brand_name": "TestBrand"}
        greetings = {_generate_ai_greeting(config) for _ in range(20)}
        # With 5 templates, 20 calls should produce at least 2 unique greetings
        assert len(greetings) >= 2, (
            f"Expected greeting variation across calls, got only: {greetings}"
        )


# ---------------------------------------------------------------------------
# 7. Inbox conversation info pane — width + text overflow
# ---------------------------------------------------------------------------

INBOX_PAGE = ADMIN_SRC / "standalone" / "pages" / "Inbox.tsx"


class TestInboxInfoPaneWidth:
    """Verify the conversation info pane is wide enough and handles overflow."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        self.src = INBOX_PAGE.read_text(encoding="utf-8")

    def test_right_panel_width_at_least_320(self):
        """Right panel must be at least 320px to prevent text clipping (S186)."""
        match = re.search(r"width:\s*(\d+)", self.src[self.src.index("RIGHT PANEL"):])
        assert match, "Could not find width declaration for right panel"
        width = int(match.group(1))
        assert width >= 320, (
            f"Right panel width must be >= 320px to prevent text clipping, got {width}"
        )

    def test_email_text_has_overflow_ellipsis(self):
        """Email value text must use textOverflow: 'ellipsis' for long addresses."""
        # Find the Email row region
        email_idx = self.src.index("identityEmail && (")
        email_section = self.src[email_idx:email_idx + 400]
        assert "textOverflow" in email_section, (
            "Email text must have textOverflow style to handle long addresses"
        )

    def test_customer_id_text_has_overflow_ellipsis(self):
        """Customer ID value text in profile section must use textOverflow for long IDs."""
        # Find the Customer profile section's Customer ID row (has "Customer ID" label)
        profile_idx = self.src.index("Customer profile")
        profile_section = self.src[profile_idx:profile_idx + 600]
        assert "textOverflow" in profile_section, (
            "Customer ID text in profile section must have textOverflow style to handle long IDs"
        )

    def test_value_texts_have_min_width_zero(self):
        """Value texts must have minWidth: 0 to allow flex truncation."""
        assert "minWidth: 0" in self.src, (
            "Value texts need minWidth: 0 for flex-based text truncation"
        )


# ---------------------------------------------------------------------------
# 8. Email unsubscribe message — present in every email via wrapper
# ---------------------------------------------------------------------------

# Modules that must use format_branded_email (not raw _EMAIL_WRAPPER.format)
_EMAIL_MODULES = [
    "src.multi_tenant.welcome_email",
    "src.multi_tenant.service_message_delivery",
    "src.multi_tenant.admin_apikey_api",
    "src.multi_tenant.access_expiry_email",
    "src.multi_tenant.trial_expiry_email",
    "src.multi_tenant.email_change",
    "src.multi_tenant.email_verification",
    "src.multi_tenant.magic_link_auth",
    "src.multi_tenant.login_notification",
    "src.multi_tenant.tenant_recovery",
    "src.multi_tenant.spa_recovery",
    "src.multi_tenant.widget_otp_verification",
]


class TestEmailUnsubscribeMessage:
    """Verify every branded email includes an unsubscribe message (S186)."""

    def test_wrapper_contains_unsubscribe_text(self):
        """_EMAIL_WRAPPER must include the unsubscribe message text."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert "To unsubscribe" in _EMAIL_WRAPPER, (
            "Email wrapper must include unsubscribe text"
        )

    def test_wrapper_contains_access_your_account_link(self):
        """Unsubscribe message must have an 'access your account' hyperlink."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert "access your account" in _EMAIL_WRAPPER
        assert "{unsubscribe_url}" in _EMAIL_WRAPPER, (
            "Wrapper must have {unsubscribe_url} placeholder for the admin link"
        )

    def test_wrapper_contains_system_configuration_text(self):
        """Unsubscribe message must mention system configuration."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert "change your system configuration" in _EMAIL_WRAPPER

    def test_format_branded_email_resolves_url(self):
        """format_branded_email must resolve {unsubscribe_url} in the output."""
        from src.multi_tenant.alert_delivery import format_branded_email

        html = format_branded_email("<p>Test</p>")
        assert "{unsubscribe_url}" not in html, (
            "format_branded_email must resolve the unsubscribe_url placeholder"
        )
        assert "access your account" in html
        assert "To unsubscribe" in html

    def test_format_branded_email_uses_explicit_url(self):
        """When admin_url is passed, it appears in the unsubscribe link."""
        from src.multi_tenant.alert_delivery import format_branded_email

        custom_url = "https://example.com/admin/"
        html = format_branded_email("<p>Test</p>", admin_url=custom_url)
        assert custom_url in html, (
            "Explicit admin_url must be used in the unsubscribe link"
        )

    def test_format_branded_email_preserves_body(self):
        """format_branded_email must include the body content."""
        from src.multi_tenant.alert_delivery import format_branded_email

        body = "<h2>Important Message</h2><p>Hello world</p>"
        html = format_branded_email(body)
        assert "Important Message" in html
        assert "Hello world" in html

    @pytest.mark.parametrize("module_path", _EMAIL_MODULES)
    def test_email_module_uses_format_branded_email(self, module_path):
        """Every email module must use format_branded_email (not raw _EMAIL_WRAPPER.format)."""
        import importlib
        import inspect

        mod = importlib.import_module(module_path)
        source = inspect.getsource(mod)
        assert "format_branded_email" in source, (
            f"{module_path} must import and use format_branded_email "
            f"to ensure unsubscribe message is included in all emails"
        )
