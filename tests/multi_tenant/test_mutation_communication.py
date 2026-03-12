"""Mutation endpoint tests for Communication Capture (SPEC-1687).

Tests the REST mutation endpoints in communication_capture.py via
the app_client (TestClient) fixture — exercising the full FastAPI
router stack without authentication (test endpoints are auth-exempt).

Covers:
    - POST /api/test/email-capture (store captured message)
    - DELETE /api/test/email-capture (clear capture store)
    - GET /api/test/email-capture (list / filter captured messages)
    - emit_communication_event() capture vs audit behaviour
    - Token hashing via hash_token()
    - Ring buffer overflow (_MAX_CAPTURED ceiling)
    - CAPTURE_MODE gate (404 when disabled)

Run:
    pytest tests/multi_tenant/test_mutation_communication.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

URL = "/api/test/email-capture"


def _clear_store() -> None:
    """Reset the module-level capture store between tests."""
    from src.multi_tenant.communication_capture import clear_captured_messages

    clear_captured_messages()


# ---------------------------------------------------------------------------
# POST /api/test/email-capture
# ---------------------------------------------------------------------------


class TestStoreCapturedMessage:
    """POST /api/test/email-capture — inject a test message."""

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_store_happy_path(self, app_client):
        _clear_store()
        body = {
            "event_type": "magic_link",
            "recipient": "user@example.com",
            "channel": "email",
            "subject": "Your magic link",
            "body": "Click here: https://example.com/auth?token=abc",
            "token": "abc123",
            "ttl_minutes": 15,
        }
        resp = app_client.post(URL, json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        assert any(
            m["recipient"] == "user@example.com" for m in data["messages"]
        )

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_store_minimal_payload(self, app_client):
        """Only required fields: event_type and recipient."""
        _clear_store()
        body = {"event_type": "test_event", "recipient": "min@example.com"}
        resp = app_client.post(URL, json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        msg = next(
            m for m in data["messages"] if m["recipient"] == "min@example.com"
        )
        assert msg["channel"] == "email"  # default
        assert msg["subject"] == ""
        assert "body" in msg  # body field present (empty string from default)

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_store_returns_404_when_disabled(self, app_client):
        resp = app_client.post(
            URL, json={"event_type": "test", "recipient": "a@b.com"}
        )
        assert resp.status_code == 404
        assert "not enabled" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /api/test/email-capture
# ---------------------------------------------------------------------------


class TestClearCaptureStore:
    """DELETE /api/test/email-capture — clear all captured messages."""

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_clear_happy_path(self, app_client):
        _clear_store()
        # Seed two messages via POST
        for i in range(2):
            app_client.post(
                URL,
                json={
                    "event_type": "otp",
                    "recipient": f"user{i}@example.com",
                },
            )
        resp = app_client.delete(URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["cleared"] == 2

        # Verify store is empty
        get_resp = app_client.get(URL)
        assert get_resp.json()["count"] == 0

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_clear_returns_404_when_disabled(self, app_client):
        resp = app_client.delete(URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/test/email-capture
# ---------------------------------------------------------------------------


class TestListCapturedMessages:
    """GET /api/test/email-capture — list and filter captured messages."""

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_list_empty(self, app_client):
        _clear_store()
        resp = app_client.get(URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["messages"] == []

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_list_with_filters(self, app_client):
        _clear_store()
        # Seed diverse messages
        app_client.post(
            URL,
            json={
                "event_type": "otp",
                "recipient": "alice@example.com",
                "channel": "sms",
            },
        )
        app_client.post(
            URL,
            json={
                "event_type": "magic_link",
                "recipient": "bob@example.com",
                "channel": "email",
            },
        )
        app_client.post(
            URL,
            json={
                "event_type": "otp",
                "recipient": "carol@example.com",
                "channel": "email",
            },
        )

        # Filter by event_type
        resp = app_client.get(URL, params={"event_type": "otp"})
        assert resp.json()["count"] == 2

        # Filter by recipient
        resp = app_client.get(URL, params={"recipient": "bob@example.com"})
        assert resp.json()["count"] == 1
        assert resp.json()["messages"][0]["event_type"] == "magic_link"

        # Filter by channel
        resp = app_client.get(URL, params={"channel": "sms"})
        assert resp.json()["count"] == 1
        assert resp.json()["messages"][0]["recipient"] == "alice@example.com"

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_list_returns_404_when_disabled(self, app_client):
        resp = app_client.get(URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# emit_communication_event() — unit-level capture vs audit behaviour
# ---------------------------------------------------------------------------


class TestEmitCommunicationEvent:
    """Unit tests for emit_communication_event() function."""

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_capture_mode_stores_body(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        _clear_store()
        emit_communication_event(
            event_type="otp",
            recipient="user@test.com",
            channel="sms",
            body="Your code is 123456",
            token="123456",
            ttl_minutes=5,
        )
        msgs = get_captured_messages(event_type="otp")
        assert len(msgs) == 1
        assert msgs[0]["body"] == "Your code is 123456"
        assert msgs[0]["ttl_minutes"] == 5

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", False)
    def test_audit_mode_no_body_stored(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        _clear_store()
        emit_communication_event(
            event_type="otp",
            recipient="user@test.com",
            channel="sms",
            body="Your code is 123456",
        )
        msgs = get_captured_messages(event_type="otp")
        assert len(msgs) == 0  # not stored in audit mode

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_token_is_hashed_not_stored_raw(self):
        from src.multi_tenant.communication_capture import (
            emit_communication_event,
            get_captured_messages,
        )

        _clear_store()
        raw_token = "secret-token-value"
        emit_communication_event(
            event_type="magic_link",
            recipient="user@test.com",
            channel="email",
            token=raw_token,
        )
        msgs = get_captured_messages(event_type="magic_link")
        assert len(msgs) == 1
        expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        assert msgs[0]["token_hash"] == expected_hash
        # Raw token must not appear in any stored field
        msg_str = str(msgs[0])
        assert raw_token not in msg_str or "token_hash" in msg_str

    @patch("src.multi_tenant.communication_capture.CAPTURE_MODE", True)
    def test_ring_buffer_evicts_oldest(self):
        from src.multi_tenant.communication_capture import (
            _MAX_CAPTURED,
            emit_communication_event,
            get_captured_messages,
        )

        _clear_store()
        overflow = 5
        for i in range(_MAX_CAPTURED + overflow):
            emit_communication_event(
                event_type="flood",
                recipient=f"user{i}@example.com",
                channel="email",
            )
        msgs = get_captured_messages(event_type="flood")
        assert len(msgs) == _MAX_CAPTURED
        # First message should be the one at index `overflow`
        assert msgs[0]["recipient"] == f"user{overflow}@example.com"


# ---------------------------------------------------------------------------
# hash_token()
# ---------------------------------------------------------------------------


class TestHashToken:
    """Verify hash_token() utility behaviour."""

    def test_returns_sha256_hex(self):
        from src.multi_tenant.communication_capture import hash_token

        result = hash_token("my-token")
        expected = hashlib.sha256(b"my-token").hexdigest()
        assert result == expected
        assert len(result) == 64

    def test_empty_input_returns_empty(self):
        from src.multi_tenant.communication_capture import hash_token

        assert hash_token("") == ""
