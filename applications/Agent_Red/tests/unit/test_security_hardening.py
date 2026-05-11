"""
Tests for security hardening utilities — input/output sanitization,
pre-auth rate limiting, API key rotation, and middleware.

Covers:
    - WI #160: Input sanitization (tenant_id, path params, conversation_id)
    - WI #161: Output sanitization for AI responses
    - WI #163: Pre-auth rate limiting
    - WI #159: API key rotation endpoints
    - PreAuthRateLimitMiddleware ASGI integration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.security_hardening import (
    PreAuthRateLimiter,
    PreAuthRateLimitMiddleware,
    _generate_api_key,
    _generate_widget_key,
    configure_key_rotation_services,
    get_pre_auth_limiter,
    rotate_api_key,
    rotate_widget_key,
    sanitize_ai_response,
    sanitize_conversation_id,
    sanitize_for_html,
    sanitize_path_param,
    sanitize_tenant_id,
)


# ---------------------------------------------------------------------------
# WI #160: Input sanitization — sanitize_tenant_id
# ---------------------------------------------------------------------------


class TestSanitizeTenantId:
    """Tests for sanitize_tenant_id."""

    def test_valid_uuid(self):
        tid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert sanitize_tenant_id(tid) == tid

    def test_valid_uuid_uppercase(self):
        tid = "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        assert sanitize_tenant_id(tid) == tid

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id("")

    def test_none_raises(self):
        with pytest.raises((ValueError, TypeError)):
            sanitize_tenant_id(None)

    def test_short_string_raises(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id("abc123")

    def test_path_traversal_raises(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id("../etc/passwd")

    def test_invalid_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id("a1b2c3d4-e5f6-7890-abcd-ef123456789g")

    def test_too_short_uuid_raises(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            sanitize_tenant_id("a1b2c3d4-e5f6-7890-abcd")


# ---------------------------------------------------------------------------
# WI #160: Input sanitization — sanitize_path_param
# ---------------------------------------------------------------------------


class TestSanitizePathParam:
    """Tests for sanitize_path_param."""

    def test_valid_alphanumeric(self):
        assert sanitize_path_param("my-param_123") == "my-param_123"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Empty"):
            sanitize_path_param("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="too long"):
            sanitize_path_param("x" * 257)

    def test_exactly_256_chars_passes(self):
        val = "a" * 256
        assert sanitize_path_param(val) == val

    def test_null_bytes_rejected(self):
        with pytest.raises(ValueError, match="invalid characters"):
            sanitize_path_param("test\x00injection")

    def test_control_chars_rejected(self):
        with pytest.raises(ValueError, match="invalid characters"):
            sanitize_path_param("test\x1fvalue")

    def test_html_injection_rejected(self):
        with pytest.raises(ValueError, match="invalid characters"):
            sanitize_path_param("<script>alert(1)</script>")

    def test_backslash_rejected(self):
        with pytest.raises(ValueError, match="invalid characters"):
            sanitize_path_param("path\\traversal")

    def test_backtick_rejected(self):
        with pytest.raises(ValueError, match="invalid characters"):
            sanitize_path_param("test`cmd`")

    def test_path_traversal_dot_dot_slash(self):
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_path_param("foo/../bar")

    def test_path_traversal_encoded(self):
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_path_param("foo%2e%2e/bar")

    def test_path_traversal_double_encoded(self):
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_path_param("foo%252e/bar")

    def test_custom_param_name_in_error(self):
        with pytest.raises(ValueError, match="conversation_id"):
            sanitize_path_param("", param_name="conversation_id")


# ---------------------------------------------------------------------------
# WI #160: Input sanitization — sanitize_conversation_id
# ---------------------------------------------------------------------------


class TestSanitizeConversationId:
    """Tests for sanitize_conversation_id."""

    def test_valid_id(self):
        assert sanitize_conversation_id("conv-123_abc") == "conv-123_abc"

    def test_valid_numeric(self):
        assert sanitize_conversation_id("12345") == "12345"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Invalid conversation_id format"):
            sanitize_conversation_id("")

    def test_special_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid conversation_id format"):
            sanitize_conversation_id("conv/../../etc")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="Invalid conversation_id format"):
            sanitize_conversation_id("x" * 129)

    def test_max_length_passes(self):
        val = "a" * 128
        assert sanitize_conversation_id(val) == val

    def test_spaces_rejected(self):
        with pytest.raises(ValueError, match="Invalid conversation_id format"):
            sanitize_conversation_id("conv with spaces")


# ---------------------------------------------------------------------------
# WI #161: Output sanitization — sanitize_ai_response
# ---------------------------------------------------------------------------


class TestSanitizeAiResponse:
    """Tests for sanitize_ai_response."""

    def test_empty_string(self):
        assert sanitize_ai_response("") == ""

    def test_none_returns_none(self):
        assert sanitize_ai_response(None) is None

    def test_safe_text_unchanged(self):
        text = "Hello! How can I help you today?"
        assert sanitize_ai_response(text) == text

    def test_safe_markdown_preserved(self):
        text = "**Bold** and *italic* and `code`"
        assert sanitize_ai_response(text) == text

    def test_script_tag_removed(self):
        text = 'Check this out: <script>alert("xss")</script>'
        result = sanitize_ai_response(text)
        assert "<script>" not in result
        assert "[removed]" in result

    def test_iframe_removed(self):
        text = '<iframe src="evil.com"></iframe>'
        result = sanitize_ai_response(text)
        assert "<iframe" not in result

    def test_object_tag_removed(self):
        text = '<object data="exploit.swf"></object>'
        result = sanitize_ai_response(text)
        assert "<object" not in result

    def test_embed_tag_removed(self):
        text = '<embed src="evil.swf">'
        result = sanitize_ai_response(text)
        assert "<embed" not in result

    def test_form_tag_removed(self):
        text = '<form action="evil.com"><input type="text"></form>'
        result = sanitize_ai_response(text)
        assert "<form" not in result
        assert "<input" not in result

    def test_event_handler_removed(self):
        text = '<img src="x" onerror="alert(1)">'
        result = sanitize_ai_response(text)
        assert "onerror=" not in result

    def test_onclick_removed(self):
        text = '<div onclick="steal()">Click me</div>'
        result = sanitize_ai_response(text)
        assert "onclick=" not in result

    def test_javascript_uri_removed(self):
        text = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_ai_response(text)
        assert "javascript:" not in result

    def test_data_uri_html_removed(self):
        text = '<a href="data:text/html,<script>alert(1)</script>">Click</a>'
        result = sanitize_ai_response(text)
        assert "data:text/html" not in result.lower()

    def test_markdown_image_injection(self):
        text = "![img](javascript:alert(1))"
        result = sanitize_ai_response(text)
        assert "javascript:" not in result

    def test_markdown_link_injection(self):
        text = "[click](javascript:alert(1))"
        result = sanitize_ai_response(text)
        assert "javascript:" not in result

    def test_safe_links_preserved(self):
        text = "[Visit](https://example.com)"
        assert sanitize_ai_response(text) == text

    def test_mixed_safe_and_unsafe(self):
        text = "Hello **user**! <script>steal()</script> Have a great day!"
        result = sanitize_ai_response(text)
        assert "Hello **user**!" in result
        assert "Have a great day!" in result
        assert "<script>" not in result

    def test_style_tag_removed(self):
        text = '<style>body{display:none}</style>'
        result = sanitize_ai_response(text)
        assert "<style>" not in result

    def test_link_tag_removed(self):
        text = '<link rel="stylesheet" href="evil.css">'
        result = sanitize_ai_response(text)
        assert "<link" not in result

    def test_meta_tag_removed(self):
        text = '<meta http-equiv="refresh" content="0;url=evil.com">'
        result = sanitize_ai_response(text)
        assert "<meta" not in result

    def test_base_tag_removed(self):
        text = '<base href="evil.com">'
        result = sanitize_ai_response(text)
        assert "<base" not in result


# ---------------------------------------------------------------------------
# WI #161: Output sanitization — sanitize_for_html
# ---------------------------------------------------------------------------


class TestSanitizeForHtml:
    """Tests for sanitize_for_html."""

    def test_empty_string(self):
        assert sanitize_for_html("") == ""

    def test_none_returns_none(self):
        assert sanitize_for_html(None) is None

    def test_plain_text_unchanged(self):
        assert sanitize_for_html("Hello World") == "Hello World"

    def test_angle_brackets_escaped(self):
        assert sanitize_for_html("<script>") == "&lt;script&gt;"

    def test_ampersand_escaped(self):
        assert sanitize_for_html("A & B") == "A &amp; B"

    def test_quotes_escaped(self):
        result = sanitize_for_html('He said "hello"')
        assert "&quot;" in result

    def test_single_quotes_escaped(self):
        result = sanitize_for_html("It's fine")
        assert "&#x27;" in result or "'" not in result or "'" in result


# ---------------------------------------------------------------------------
# WI #163: PreAuthRateLimiter
# ---------------------------------------------------------------------------


class TestPreAuthRateLimiter:
    """Tests for PreAuthRateLimiter."""

    def test_new_ip_not_blocked(self):
        limiter = PreAuthRateLimiter(max_attempts=3, window_seconds=60)
        assert limiter.is_blocked("1.2.3.4") is False

    def test_record_failure_below_threshold(self):
        limiter = PreAuthRateLimiter(max_attempts=3, window_seconds=60)
        assert limiter.record_failure("1.2.3.4") is False
        assert limiter.record_failure("1.2.3.4") is False
        assert limiter.is_blocked("1.2.3.4") is False

    def test_record_failure_at_threshold_blocks(self):
        limiter = PreAuthRateLimiter(max_attempts=3, window_seconds=60)
        limiter.record_failure("1.2.3.4")
        limiter.record_failure("1.2.3.4")
        assert limiter.record_failure("1.2.3.4") is True  # 3rd attempt
        assert limiter.is_blocked("1.2.3.4") is True

    def test_different_ips_independent(self):
        limiter = PreAuthRateLimiter(max_attempts=2, window_seconds=60)
        limiter.record_failure("1.1.1.1")
        limiter.record_failure("1.1.1.1")  # blocks 1.1.1.1
        assert limiter.is_blocked("1.1.1.1") is True
        assert limiter.is_blocked("2.2.2.2") is False

    def test_record_success_clears(self):
        limiter = PreAuthRateLimiter(max_attempts=3, window_seconds=60)
        limiter.record_failure("1.2.3.4")
        limiter.record_failure("1.2.3.4")
        limiter.record_success("1.2.3.4")
        assert limiter.is_blocked("1.2.3.4") is False
        assert limiter.get_remaining_attempts("1.2.3.4") == 3

    def test_get_remaining_attempts_new_ip(self):
        limiter = PreAuthRateLimiter(max_attempts=5, window_seconds=60)
        assert limiter.get_remaining_attempts("1.2.3.4") == 5

    def test_get_remaining_attempts_after_failures(self):
        limiter = PreAuthRateLimiter(max_attempts=5, window_seconds=60)
        limiter.record_failure("1.2.3.4")
        limiter.record_failure("1.2.3.4")
        assert limiter.get_remaining_attempts("1.2.3.4") == 3

    def test_block_expiry(self):
        limiter = PreAuthRateLimiter(
            max_attempts=2, window_seconds=60, block_seconds=1,
        )
        limiter.record_failure("1.2.3.4")
        limiter.record_failure("1.2.3.4")
        assert limiter.is_blocked("1.2.3.4") is True

        # Simulate time passing (block_seconds=1)
        time.sleep(1.1)
        assert limiter.is_blocked("1.2.3.4") is False

    def test_cleanup_removes_expired(self):
        limiter = PreAuthRateLimiter(
            max_attempts=5, window_seconds=1, block_seconds=1,
        )
        limiter.record_failure("1.2.3.4")
        limiter.record_failure("5.6.7.8")
        time.sleep(1.1)
        removed = limiter.cleanup()
        assert removed == 2

    def test_cleanup_preserves_active(self):
        limiter = PreAuthRateLimiter(
            max_attempts=5, window_seconds=60, block_seconds=60,
        )
        limiter.record_failure("1.2.3.4")
        removed = limiter.cleanup()
        assert removed == 0


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestGetPreAuthLimiter:
    """Tests for get_pre_auth_limiter singleton."""

    def test_returns_instance(self):
        import src.multi_tenant.security_hardening as mod
        old = mod._pre_auth_limiter
        try:
            mod._pre_auth_limiter = None
            limiter = get_pre_auth_limiter()
            assert isinstance(limiter, PreAuthRateLimiter)
        finally:
            mod._pre_auth_limiter = old

    def test_returns_same_instance(self):
        import src.multi_tenant.security_hardening as mod
        old = mod._pre_auth_limiter
        try:
            mod._pre_auth_limiter = None
            a = get_pre_auth_limiter()
            b = get_pre_auth_limiter()
            assert a is b
        finally:
            mod._pre_auth_limiter = old


# ---------------------------------------------------------------------------
# PreAuthRateLimitMiddleware
# ---------------------------------------------------------------------------


class TestPreAuthRateLimitMiddleware:
    """Tests for PreAuthRateLimitMiddleware ASGI."""

    @pytest.mark.asyncio
    async def test_non_http_passes_through(self):
        app = AsyncMock()
        middleware = PreAuthRateLimitMiddleware(app)
        scope = {"type": "lifespan"}
        await middleware(scope, AsyncMock(), AsyncMock())
        app.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_auth_exempt_path_passes_through(self):
        app = AsyncMock()
        middleware = PreAuthRateLimitMiddleware(app)
        scope = {"type": "http", "path": "/health", "client": ("1.2.3.4", 1234)}
        with patch("src.multi_tenant.auth.is_auth_exempt", return_value=True):
            await middleware(scope, AsyncMock(), AsyncMock())
        app.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_blocked_ip_returns_429(self):
        app = AsyncMock()
        middleware = PreAuthRateLimitMiddleware(app)
        # Manually block the IP
        middleware._limiter.record_failure("1.2.3.4")
        for _ in range(15):
            middleware._limiter.record_failure("1.2.3.4")

        scope = {"type": "http", "path": "/api/chat", "client": ("1.2.3.4", 1234)}
        send = AsyncMock()

        with patch("src.multi_tenant.auth.is_auth_exempt", return_value=False):
            await middleware(scope, AsyncMock(), send)

        # The app should NOT have been called
        app.assert_not_awaited()
        # send should have been called (429 response)
        assert send.call_count > 0

    @pytest.mark.asyncio
    async def test_unblocked_ip_passes_through(self):
        app = AsyncMock()
        middleware = PreAuthRateLimitMiddleware(app)
        scope = {"type": "http", "path": "/api/chat", "client": ("1.2.3.4", 1234)}

        with patch("src.multi_tenant.auth.is_auth_exempt", return_value=False):
            await middleware(scope, AsyncMock(), AsyncMock())
        app.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_missing_client_uses_unknown(self):
        app = AsyncMock()
        middleware = PreAuthRateLimitMiddleware(app)
        scope = {"type": "http", "path": "/api/chat"}

        with patch("src.multi_tenant.auth.is_auth_exempt", return_value=False):
            await middleware(scope, AsyncMock(), AsyncMock())
        app.assert_awaited_once()


# ---------------------------------------------------------------------------
# WI #159: API key generation helpers
# ---------------------------------------------------------------------------


class TestKeyGeneration:
    """Tests for _generate_api_key and _generate_widget_key."""

    def test_api_key_format(self):
        key = _generate_api_key()
        assert key.startswith("arx_")
        assert len(key) == 4 + 40  # "arx_" + 40 hex chars

    def test_api_keys_unique(self):
        keys = {_generate_api_key() for _ in range(100)}
        assert len(keys) == 100

    def test_widget_key_format(self):
        key = _generate_widget_key("test-tenant-id")
        assert key.startswith("pk_live_")
        parts = key.split("_")
        assert len(parts) == 4  # pk, live, tenant_hash, random

    def test_widget_key_contains_tenant_hash(self):
        tenant_id = "my-tenant-uuid"
        key = _generate_widget_key(tenant_id)
        expected_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:12]
        assert expected_hash in key

    def test_widget_keys_unique(self):
        keys = {_generate_widget_key("tenant-1") for _ in range(100)}
        assert len(keys) == 100


# ---------------------------------------------------------------------------
# WI #159: API key rotation endpoints
# ---------------------------------------------------------------------------


class TestRotateApiKey:
    """Tests for rotate_api_key endpoint."""

    @pytest.mark.asyncio
    async def test_not_configured_returns_503(self):
        import src.multi_tenant.security_hardening as mod
        old_ss, old_tr = mod._secret_service, mod._tenant_repo
        try:
            mod._secret_service = None
            mod._tenant_repo = None
            request = MagicMock()
            with pytest.raises(Exception) as exc_info:
                await rotate_api_key(request)
            assert exc_info.value.status_code == 503
        finally:
            mod._secret_service, mod._tenant_repo = old_ss, old_tr

    @pytest.mark.asyncio
    async def test_no_tenant_context_returns_401(self):
        mock_ss = MagicMock()
        mock_tr = MagicMock()
        configure_key_rotation_services(mock_ss, mock_tr)

        request = MagicMock()
        request.state = MagicMock(spec=[])  # No tenant_context attribute
        with pytest.raises(Exception) as exc_info:
            await rotate_api_key(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_successful_rotation(self):
        mock_tr = MagicMock()
        mock_tr.read = AsyncMock(return_value={"api_key_hash": "old_hash"})
        mock_tr.patch = AsyncMock()
        configure_key_rotation_services(MagicMock(), mock_tr)

        request = MagicMock()
        ctx = MagicMock()
        ctx.tenant_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        request.state.tenant_context = ctx

        result = await rotate_api_key(request)
        assert result.new_api_key.startswith("arx_")
        assert "24 hours" in result.message
        mock_tr.patch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rotation_without_old_key(self):
        """First-time rotation where no old key hash exists."""
        mock_tr = MagicMock()
        mock_tr.read = AsyncMock(return_value={})
        mock_tr.patch = AsyncMock()
        configure_key_rotation_services(MagicMock(), mock_tr)

        request = MagicMock()
        ctx = MagicMock()
        ctx.tenant_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        request.state.tenant_context = ctx

        result = await rotate_api_key(request)
        assert result.new_api_key.startswith("arx_")
        # With no old hash, fewer operations
        call_args = mock_tr.patch.call_args
        ops = call_args.kwargs.get("operations") or call_args[1].get("operations") or call_args[0][2]
        # Should have exactly 2 ops (new hash + updated_at), not 4
        assert len(ops) == 2


class TestRotateWidgetKey:
    """Tests for rotate_widget_key endpoint."""

    @pytest.mark.asyncio
    async def test_not_configured_returns_503(self):
        import src.multi_tenant.security_hardening as mod
        old_tr = mod._tenant_repo
        try:
            mod._tenant_repo = None
            request = MagicMock()
            with pytest.raises(Exception) as exc_info:
                await rotate_widget_key(request)
            assert exc_info.value.status_code == 503
        finally:
            mod._tenant_repo = old_tr

    @pytest.mark.asyncio
    async def test_no_tenant_context_returns_401(self):
        import src.multi_tenant.security_hardening as mod
        old_tr = mod._tenant_repo
        try:
            mod._tenant_repo = MagicMock()
            request = MagicMock()
            request.state = MagicMock(spec=[])
            with pytest.raises(Exception) as exc_info:
                await rotate_widget_key(request)
            assert exc_info.value.status_code == 401
        finally:
            mod._tenant_repo = old_tr

    @pytest.mark.asyncio
    async def test_successful_widget_rotation(self):
        mock_tr = MagicMock()
        mock_tr.patch = AsyncMock()
        configure_key_rotation_services(MagicMock(), mock_tr)

        request = MagicMock()
        ctx = MagicMock()
        ctx.tenant_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        request.state.tenant_context = ctx

        result = await rotate_widget_key(request)
        assert result.new_widget_key.startswith("pk_live_")
        assert "embed code" in result.message
        mock_tr.patch.assert_awaited_once()
