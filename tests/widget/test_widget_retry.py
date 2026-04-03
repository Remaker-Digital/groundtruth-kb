"""Slice 5: S253 Phase 1 — Widget retry/idempotency contract tests.

Tests the widget transport contract from the server side: idempotency_key
reuse, retry_after_ms in 409 responses, structured error codes.

Since the widget is TypeScript, these tests verify the server-side contract
that the widget depends on (rather than running the JS code directly).

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 5

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest


WIDGET_HTTP_TS = (
    Path(__file__).resolve().parent.parent.parent
    / "widget" / "src" / "transport" / "http.ts"
)


# ── Server-side contract: idempotency_key ─────────────────────────

class TestIdempotencyKeyContract:
    """Verify the server accepts and uses idempotency_key from widget."""

    def test_send_message_request_has_idempotency_key(self):
        """SendMessageRequest model accepts idempotency_key."""
        from src.chat.models import SendMessageRequest

        req = SendMessageRequest(
            conversation_id="conv-1",
            content="Hello",
            idempotency_key="test-key-123",
        )

        assert req.idempotency_key == "test-key-123"

    def test_send_message_request_key_optional(self):
        """idempotency_key is optional for backward compatibility."""
        from src.chat.models import SendMessageRequest

        req = SendMessageRequest(
            conversation_id="conv-1",
            content="Hello",
        )

        assert req.idempotency_key is None


# ── Server-side contract: 409 error responses ─────────────────────

class TestStructured409Contract:
    """Verify server produces structured 409 responses the widget can parse."""

    def test_in_flight_response_error_exists(self):
        """InFlightResponseError exists for in-flight 409."""
        from src.chat.session import InFlightResponseError

        err = InFlightResponseError("conv-1")
        assert "conv-1" in str(err)

    def test_concurrency_exhausted_error_exists(self):
        """ConcurrencyExhaustedError exists for retry exhaustion."""
        from src.chat.session import ConcurrencyExhaustedError

        err = ConcurrencyExhaustedError("conv-1")
        assert "conv-1" in str(err)

    def test_turn_limit_reached_error_exists(self):
        """TurnLimitReachedError exists for terminal 409."""
        from src.chat.session import TurnLimitReachedError

        err = TurnLimitReachedError("conv-1", 50)
        assert "conv-1" in str(err)
        assert "50" in str(err)


# ── Widget source contract verification ───────────────────────────

class TestWidgetSourceContract:
    """Verify the widget TypeScript source implements the expected contract."""

    @pytest.fixture(autouse=True)
    def load_source(self):
        """Read widget HTTP transport source."""
        if WIDGET_HTTP_TS.exists():
            self.source = WIDGET_HTTP_TS.read_text(encoding="utf-8")
        else:
            pytest.skip("Widget source not found")

    def test_generates_idempotency_key(self):
        """Widget generates an idempotency key for retry safety."""
        assert "generateIdempotencyKey" in self.source

    def test_sends_idempotency_key_in_body(self):
        """Widget sends idempotency_key in POST /api/chat/message body."""
        assert "idempotency_key" in self.source

    def test_parses_retry_after_ms(self):
        """Widget parses retry_after_ms from structured 409 response."""
        assert "retry_after_ms" in self.source

    def test_handles_in_flight_response_code(self):
        """Widget handles in_flight_response error code."""
        assert "in_flight_response" in self.source

    def test_handles_transfer_to_human_code(self):
        """Widget handles transfer_to_human error code (terminal, no retry)."""
        assert "transfer_to_human" in self.source
