"""Tests for Communication Capture & Audit Infrastructure (SPEC-1687).

Covers:
    - CommunicationEvent dataclass
    - Token hashing (SHA-256)
    - In-memory capture store (thread-safety, ring-buffer)
    - emit_communication_event() in both capture and audit modes
    - REST API endpoints (GET / POST / DELETE)
    - Auth exemption for capture endpoints
    - Router registration

Run:
    pytest tests/multi_tenant/test_communication_capture.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import threading
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# CommunicationEvent dataclass
# ---------------------------------------------------------------------------


class TestCommunicationEvent:

    def test_event_has_required_fields(self):
        from src.multi_tenant.communication_capture import CommunicationEvent

        event = CommunicationEvent(
            event_type="magic_link",
            recipient="user@example.com",
            channel="email",
        )
        assert event.event_type == "magic_link"
        assert event.recipient == "user@example.com"
        assert event.channel == "email"

    def test_event_defaults(self):
        from src.multi_tenant.communication_capture import CommunicationEvent

        event = CommunicationEvent(
            event_type="otp",
            recipient="user@example.com",
            channel="sms",
        )
        assert event.subject == ""
        assert event.body == ""
        assert event.token_hash == ""
        assert event.ttl_minutes == 0
        assert event.metadata == {}
        assert event.timestamp  # auto-populated

    def test_event_accepts_all_fields(self):
        from src.multi_tenant.communication_capture import CommunicationEvent

        event = CommunicationEvent(
            event_type="login_notification",
            recipient="admin@remaker.digital",
            channel="email",
            subject="Platform Sign-in",
            body="<h1>Hello</h1>",
            token_hash="abc123",
            ttl_minutes=15,
            metadata={"ip": "10.0.0.1"},
        )
        assert event.subject == "Platform Sign-in"
        assert event.body == "<h1>Hello</h1>"
        assert event.ttl_minutes == 15
        assert event.metadata["ip"] == "10.0.0.1"


# ---------------------------------------------------------------------------
# Token hashing
# ---------------------------------------------------------------------------


class TestTokenHashing:

    def test_hash_token_returns_sha256(self):
        from src.multi_tenant.communication_capture import hash_token

        result = hash_token("my-secret-token")
        expected = hashlib.sha256("my-secret-token".encode()).hexdigest()
        assert result == expected
        assert len(result) == 64  # SHA-256 hex digest length

    def test_hash_token_empty_returns_empty(self):
        from src.multi_tenant.communication_capture import hash_token

        assert hash_token("") == ""

    def test_hash_token_deterministic(self):
        from src.multi_tenant.communication_capture import hash_token

        assert hash_token("abc") == hash_token("abc")

    def test_hash_token_different_inputs_different_hashes(self):
        from src.multi_tenant.communication_capture import hash_token

        assert hash_token("token-a") != hash_token("token-b")


# ---------------------------------------------------------------------------
# Capture store (thread-safety, ring-buffer, filtering)
# ---------------------------------------------------------------------------


class TestCaptureStore:

    def setup_method(self):
        """Clear capture store before each test."""
        from src.multi_tenant import communication_capture

        with communication_capture._capture_lock:
            communication_capture._captured_messages.clear()

    def test_store_and_retrieve_message(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
        )

        event = CommunicationEvent(
            event_type="otp",
            recipient="user@example.com",
            channel="email",
            subject="Your code",
            body="Code: 123456",
        )
        _store_message(event)
        msgs = get_captured_messages()
        assert len(msgs) == 1
        assert msgs[0]["event_type"] == "otp"
        assert msgs[0]["recipient"] == "user@example.com"

    def test_filter_by_event_type(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
        )

        _store_message(CommunicationEvent(event_type="otp", recipient="a@b.com", channel="email"))
        _store_message(CommunicationEvent(event_type="magic_link", recipient="a@b.com", channel="email"))
        _store_message(CommunicationEvent(event_type="otp", recipient="c@d.com", channel="sms"))

        otp_msgs = get_captured_messages(event_type="otp")
        assert len(otp_msgs) == 2

    def test_filter_by_recipient(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
        )

        _store_message(CommunicationEvent(event_type="otp", recipient="a@b.com", channel="email"))
        _store_message(CommunicationEvent(event_type="otp", recipient="c@d.com", channel="email"))

        msgs = get_captured_messages(recipient="a@b.com")
        assert len(msgs) == 1
        assert msgs[0]["recipient"] == "a@b.com"

    def test_filter_by_channel(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
        )

        _store_message(CommunicationEvent(event_type="otp", recipient="a@b.com", channel="email"))
        _store_message(CommunicationEvent(event_type="otp", recipient="a@b.com", channel="sms"))

        sms = get_captured_messages(channel="sms")
        assert len(sms) == 1
        assert sms[0]["channel"] == "sms"

    def test_clear_captured_messages(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
            clear_captured_messages,
        )

        _store_message(CommunicationEvent(event_type="otp", recipient="a@b.com", channel="email"))
        _store_message(CommunicationEvent(event_type="otp", recipient="b@c.com", channel="email"))

        cleared = clear_captured_messages()
        assert cleared == 2
        assert len(get_captured_messages()) == 0

    def test_ring_buffer_ceiling(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
            _MAX_CAPTURED,
        )

        for i in range(_MAX_CAPTURED + 10):
            _store_message(CommunicationEvent(
                event_type="test",
                recipient=f"user{i}@example.com",
                channel="email",
            ))

        msgs = get_captured_messages()
        assert len(msgs) == _MAX_CAPTURED
        # Oldest messages should have been evicted
        assert msgs[0]["recipient"] == "user10@example.com"

    def test_thread_safety(self):
        from src.multi_tenant.communication_capture import (
            CommunicationEvent,
            _store_message,
            get_captured_messages,
        )

        errors = []

        def writer(thread_id):
            try:
                for i in range(50):
                    _store_message(CommunicationEvent(
                        event_type="test",
                        recipient=f"thread{thread_id}-{i}@example.com",
                        channel="email",
                    ))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        msgs = get_captured_messages()
        assert len(msgs) == 200  # 4 threads x 50 messages


# ---------------------------------------------------------------------------
# emit_communication_event — capture mode
# ---------------------------------------------------------------------------


class TestEmitCaptureMode:

    def setup_method(self):
        from src.multi_tenant import communication_capture
        with communication_capture._capture_lock:
            communication_capture._captured_messages.clear()

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_emit_stores_event_in_capture_mode(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="magic_link",
            recipient="user@example.com",
            channel="email",
            subject="Your magic link",
            body='<a href=https://example.com/auth?token=abc>Login</a>',
            token="abc",
            ttl_minutes=15,
        )
        msgs = get_captured_messages()
        assert len(msgs) == 1
        assert msgs[0]["event_type"] == "magic_link"
        assert msgs[0]["recipient"] == "user@example.com"
        assert msgs[0]["body"] != ""  # body IS stored in capture mode
        assert msgs[0]["ttl_minutes"] == 15

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_emit_hashes_token(self):
        import hashlib
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="otp",
            recipient="user@example.com",
            channel="sms",
            token="123456",
        )
        msgs = get_captured_messages()
        expected_hash = hashlib.sha256("123456".encode()).hexdigest()
        assert msgs[0]["token_hash"] == expected_hash

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_emit_no_token_produces_empty_hash(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="login_notification",
            recipient="admin@example.com",
            channel="email",
        )
        msgs = get_captured_messages()
        assert msgs[0]["token_hash"] == ""

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_emit_stores_metadata(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="otp",
            recipient="user@example.com",
            channel="sms",
            metadata={"phone_type": "mobile"},
        )
        msgs = get_captured_messages()
        assert msgs[0]["metadata"]["phone_type"] == "mobile"


# ---------------------------------------------------------------------------
# emit_communication_event — audit mode (default)
# ---------------------------------------------------------------------------


class TestEmitAuditMode:

    def setup_method(self):
        from src.multi_tenant import communication_capture
        with communication_capture._capture_lock:
            communication_capture._captured_messages.clear()

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_emit_does_not_store_in_audit_mode(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="magic_link",
            recipient="user@example.com",
            channel="email",
            body="secret body",
        )
        msgs = get_captured_messages()
        assert len(msgs) == 0

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_audit_mode_does_not_raise(self):
        from src.multi_tenant.communication_capture import emit_communication_event

        # Should not raise in audit mode
        emit_communication_event(
            event_type="otp",
            recipient="user@example.com",
            channel="sms",
            token="999999",
        )


# ---------------------------------------------------------------------------
# REST API endpoints
# ---------------------------------------------------------------------------


class TestRestApiCaptureEnabled:

    def setup_method(self):
        from src.multi_tenant import communication_capture
        with communication_capture._capture_lock:
            communication_capture._captured_messages.clear()

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    @pytest.mark.asyncio
    async def test_get_returns_empty_list(self):
        from src.multi_tenant.communication_capture import list_captured_messages_endpoint

        result = await list_captured_messages_endpoint()
        assert result["count"] == 0
        assert result["messages"] == []

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    @pytest.mark.asyncio
    async def test_get_returns_filtered_messages(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            list_captured_messages_endpoint,
        )

        emit_communication_event(
            event_type="otp",
            recipient="user@example.com",
            channel="email",
        )
        emit_communication_event(
            event_type="magic_link",
            recipient="other@example.com",
            channel="email",
        )
        result = await list_captured_messages_endpoint(
            event_type="otp", recipient=None, channel=None
        )
        assert result["count"] == 1

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    @pytest.mark.asyncio
    async def test_post_injects_message(self):
        from src.multi_tenant.communication_capture import (
            StoreRequest,
            store_captured_message,
            get_captured_messages,
        )

        req = StoreRequest(
            event_type="test_inject",
            recipient="test@example.com",
            channel="email",
            subject="Injected message",
            body="Test body",
        )
        result = await store_captured_message(req)
        assert result["count"] >= 1
        all_msgs = get_captured_messages()
        assert any(m["event_type"] == "test_inject" for m in all_msgs)

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    @pytest.mark.asyncio
    async def test_delete_clears_store(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            clear_capture_store,
            get_captured_messages,
        )

        emit_communication_event(
            event_type="otp", recipient="a@b.com", channel="email"
        )
        result = await clear_capture_store()
        assert result["cleared"] == 1
        assert len(get_captured_messages()) == 0


class TestRestApiCaptureDisabled:

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    @pytest.mark.asyncio
    async def test_get_returns_404(self):
        from src.multi_tenant.communication_capture import list_captured_messages_endpoint

        result = await list_captured_messages_endpoint()
        # Returns a JSONResponse with 404
        assert result.status_code == 404

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    @pytest.mark.asyncio
    async def test_post_returns_404(self):
        from src.multi_tenant.communication_capture import (
            StoreRequest,
            store_captured_message,
        )

        req = StoreRequest(
            event_type="test", recipient="a@b.com", channel="email"
        )
        result = await store_captured_message(req)
        assert result.status_code == 404

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    @pytest.mark.asyncio
    async def test_delete_returns_404(self):
        from src.multi_tenant.communication_capture import clear_capture_store

        result = await clear_capture_store()
        assert result.status_code == 404


# ---------------------------------------------------------------------------
# Auth exemption and router registration
# ---------------------------------------------------------------------------


class TestAuthExemption:

    def test_capture_path_is_auth_exempt(self):
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES

        exempt_paths = AUTH_EXEMPT_PREFIXES
        assert any(
            "/api/test/email-capture" in p for p in exempt_paths
        ), "Capture endpoint must be in AUTH_EXEMPT_PREFIXES"

    def test_is_auth_exempt_for_capture(self):
        from src.multi_tenant.auth import is_auth_exempt

        assert is_auth_exempt("/api/test/email-capture")
        assert is_auth_exempt("/api/test/email-capture?recipient=user@test.com")


class TestRouterRegistration:

    def test_capture_router_is_registered(self):
        from src.app.routers import capture_router

        assert capture_router is not None

    def test_capture_router_has_correct_prefix(self):
        from src.multi_tenant.communication_capture import router

        # Check routes have the expected prefix
        route_paths = [r.path for r in router.routes]
        assert any("/api/test/email-capture" in p for p in route_paths)

    def test_capture_router_has_three_endpoints(self):
        from src.multi_tenant.communication_capture import router

        # GET, POST, DELETE
        methods = set()
        for route in router.routes:
            if hasattr(route, "methods"):
                methods.update(route.methods)
        assert "GET" in methods
        assert "POST" in methods
        assert "DELETE" in methods


# ---------------------------------------------------------------------------
# Environment gate
# ---------------------------------------------------------------------------


class TestEnvironmentGate:

    def test_capture_mode_module_attribute_exists(self):
        from src.multi_tenant.communication_capture import CAPTURE_MODE

        # Default is False (env var not set in test context)
        assert isinstance(CAPTURE_MODE, bool)

    def test_capture_mode_default_is_false(self):
        """Without ENABLE_EMAIL_CAPTURE env var, capture mode is off."""
        # This tests the module-level constant. Since it is evaluated
        # at import time, we test by checking the module attribute.
        from src.multi_tenant.communication_capture import CAPTURE_MODE

        # In test context, ENABLE_EMAIL_CAPTURE is not set
        assert CAPTURE_MODE is False
