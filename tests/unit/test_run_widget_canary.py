"""Slice 1b: S252 widget canary job behavioral tests.

Tests for src/jobs/run_widget_canary.py — exercises check_health, check_widget_js,
check_conversation, check_sse_stream, send_alert, and main orchestration.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 1

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch, ANY

import pytest

from src.jobs.run_widget_canary import (
    check_health,
    check_widget_js,
    check_conversation,
    check_sse_stream,
    send_alert,
    main,
)


# ── check_health ──────────────────────────────────────────────────

class TestCheckHealth:
    """Behavioral tests for /health endpoint check."""

    def test_healthy_response_returns_pass(self):
        """200 with product_version -> (True, version)."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"product_version": "1.98.76"}
        client.get.return_value = mock_response

        ok, detail = check_health(client)

        assert ok is True
        assert "1.98.76" in detail
        client.get.assert_called_once_with("/health", timeout=15)

    def test_non_200_returns_fail(self):
        """Non-200 status -> (False, 'HTTP {status}')."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        client.get.return_value = mock_response

        ok, detail = check_health(client)

        assert ok is False
        assert "503" in detail

    def test_exception_returns_fail(self):
        """Network error -> (False, error message)."""
        client = MagicMock()
        client.get.side_effect = ConnectionError("refused")

        ok, detail = check_health(client)

        assert ok is False
        assert "refused" in detail


# ── check_widget_js ───────────────────────────────────────────────

class TestCheckWidgetJs:
    """Behavioral tests for /widget.js bundle check."""

    def test_valid_bundle_returns_pass(self):
        """200 with JS content-type and >1000 bytes -> pass."""
        client = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "application/javascript"}
        resp.content = b"x" * 5000
        client.get.return_value = resp

        ok, detail = check_widget_js(client)

        assert ok is True
        assert "5000" in detail

    def test_wrong_content_type_returns_fail(self):
        """200 but wrong content-type -> fail."""
        client = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "text/html"}
        resp.content = b"x" * 5000
        client.get.return_value = resp

        ok, detail = check_widget_js(client)

        assert ok is False
        assert "content-type" in detail.lower()

    def test_small_bundle_returns_fail(self):
        """200 with tiny bundle (<1000 bytes) -> suspiciously small."""
        client = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "application/javascript"}
        resp.content = b"x" * 50
        client.get.return_value = resp

        ok, detail = check_widget_js(client)

        assert ok is False
        assert "small" in detail.lower()


# ── check_conversation ────────────────────────────────────────────

class TestCheckConversation:
    """Behavioral tests for POST /api/chat/conversations check."""

    def test_successful_conversation_returns_id(self):
        """201 with conversationId -> pass with conversation ID."""
        client = MagicMock()
        resp = MagicMock()
        resp.status_code = 201
        resp.json.return_value = {"conversationId": "conv-abc-123"}
        client.post.return_value = resp

        ok, detail = check_conversation(client, "wk_test_key")

        assert ok is True
        assert detail == "conv-abc-123"
        # Verify widget key sent in header
        call_kwargs = client.post.call_args
        assert call_kwargs[1]["headers"]["X-Widget-Key"] == "wk_test_key"

    def test_missing_conversation_id_returns_fail(self):
        """200 but no conversation_id in response -> fail."""
        client = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"status": "ok"}
        client.post.return_value = resp

        ok, detail = check_conversation(client, "wk_test_key")

        assert ok is False
        assert "conversation_id" in detail.lower()


# ── check_sse_stream ─────────────────────────────────────────────

class TestCheckSseStream:
    """Behavioral tests for SSE stream check."""

    def test_complete_stream_returns_pass(self):
        """Stream with token + done events -> pass."""
        client = MagicMock()
        # Message send response
        msg_resp = MagicMock()
        msg_resp.status_code = 200
        client.post.return_value = msg_resp

        # SSE stream context manager
        stream_cm = MagicMock()
        stream_resp = MagicMock()
        stream_resp.status_code = 200
        stream_resp.headers = {"content-type": "text/event-stream"}
        stream_resp.iter_lines.return_value = [
            "event: token",
            "data: Hello",
            "event: token",
            "data: World",
            "event: done",
            "data: {}",
        ]
        stream_cm.__enter__ = MagicMock(return_value=stream_resp)
        stream_cm.__exit__ = MagicMock(return_value=False)
        client.stream.return_value = stream_cm

        ok, detail = check_sse_stream(client, "wk_test", "conv-123")

        assert ok is True
        assert "events" in detail

    def test_no_done_event_returns_fail(self):
        """Stream without done event -> fail (incomplete)."""
        client = MagicMock()
        msg_resp = MagicMock()
        msg_resp.status_code = 200
        client.post.return_value = msg_resp

        stream_cm = MagicMock()
        stream_resp = MagicMock()
        stream_resp.status_code = 200
        stream_resp.headers = {"content-type": "text/event-stream"}
        stream_resp.iter_lines.return_value = [
            "event: token",
            "data: partial",
        ]
        stream_cm.__enter__ = MagicMock(return_value=stream_resp)
        stream_cm.__exit__ = MagicMock(return_value=False)
        client.stream.return_value = stream_cm

        ok, detail = check_sse_stream(client, "wk_test", "conv-123")

        assert ok is False

    def test_message_send_failure_returns_fail(self):
        """Message send returning non-200 -> fail."""
        client = MagicMock()
        msg_resp = MagicMock()
        msg_resp.status_code = 500
        client.post.return_value = msg_resp

        ok, detail = check_sse_stream(client, "wk_test", "conv-123")

        assert ok is False
        assert "message send failed" in detail.lower()


# ── send_alert ────────────────────────────────────────────────────

class TestSendAlert:
    """Behavioral tests for SMTP alert delivery."""

    @patch.dict(os.environ, {
        "SMTP_HOST": "mail.example.com",
        "SMTP_PORT": "465",
        "SMTP_USER": "user@example.com",
        "SMTP_PASSWORD": "secret",
        "CANARY_ALERT_EMAIL": "ops@example.com",
    })
    @patch("src.jobs.run_widget_canary.smtplib", create=True)
    def test_sends_email_when_configured(self, mock_smtplib_mod):
        """Alert sends email when SMTP env vars are set."""
        import smtplib as real_smtplib
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_conn = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            send_alert("Test Subject", "Test body")

            mock_smtp.assert_called_once_with("mail.example.com", 465)
            mock_conn.login.assert_called_once_with("user@example.com", "secret")
            mock_conn.send_message.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_skips_when_smtp_not_configured(self):
        """Alert skips gracefully when SMTP env vars missing."""
        # Should not raise — just log a warning
        send_alert("Subject", "Body")


# ── main orchestration ────────────────────────────────────────────

class TestCanaryMain:
    """Behavioral tests for main() orchestration."""

    @patch.dict(os.environ, {"CANARY_TARGET_URL": "", "CANARY_WIDGET_KEY": ""})
    def test_missing_env_returns_1(self):
        """Missing CANARY_TARGET_URL returns exit code 1."""
        assert main() == 1

    @patch.dict(os.environ, {
        "CANARY_TARGET_URL": "https://example.com",
        "CANARY_WIDGET_KEY": "wk_test",
    })
    @patch("src.jobs.run_widget_canary.check_sse_stream", return_value=(True, "5 events"))
    @patch("src.jobs.run_widget_canary.check_conversation", return_value=(True, "conv-id"))
    @patch("src.jobs.run_widget_canary.check_widget_js", return_value=(True, "5000 bytes"))
    @patch("src.jobs.run_widget_canary.check_health", return_value=(True, "v1.98.76"))
    def test_all_pass_returns_0(self, mock_health, mock_js, mock_conv, mock_sse):
        """All checks passing returns exit code 0."""
        assert main() == 0

    @patch.dict(os.environ, {
        "CANARY_TARGET_URL": "https://example.com",
        "CANARY_WIDGET_KEY": "wk_test",
    })
    @patch("src.jobs.run_widget_canary.send_alert")
    @patch("src.jobs.run_widget_canary.check_conversation", return_value=(False, "HTTP 500"))
    @patch("src.jobs.run_widget_canary.check_widget_js", return_value=(True, "5000 bytes"))
    @patch("src.jobs.run_widget_canary.check_health", return_value=(True, "v1.98.76"))
    def test_failure_triggers_alert(self, mock_health, mock_js, mock_conv, mock_alert):
        """Failed check triggers alert and returns 1."""
        result = main()

        assert result == 1
        mock_alert.assert_called_once()
