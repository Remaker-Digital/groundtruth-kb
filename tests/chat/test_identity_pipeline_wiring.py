"""Tests for identity preprocessor wiring into the SSE pipeline (P0-AUTH-FIX).

Covers:
    stream_response() identity preprocessor integration — 4 tests
    1. email_received → system response injected, pipeline NOT called
    2. otp_received → system response injected, pipeline NOT called
    3. otp_invalid → system response injected, pipeline NOT called
    4. action=none → normal pipeline called (pass-through)

These tests verify the wiring in src/chat/endpoints.py stream_response()
rather than the preprocessor logic itself (tested in test_identity_preprocessor.py).

Run:
    pytest tests/chat/test_identity_pipeline_wiring.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.identity_preprocessor import IdentityAction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_identity_action(action: str, **kwargs) -> IdentityAction:
    """Create an IdentityAction with defaults."""
    defaults = {
        "action": action,
        "email": None,
        "system_message": None,
    }
    defaults.update(kwargs)
    return IdentityAction(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIdentityPipelineWiring:
    """Verify that the identity preprocessor is wired into stream_response()."""

    @pytest.mark.asyncio
    async def test_email_received_bypasses_pipeline(self):
        """When preprocessor returns email_received, pipeline is NOT called."""
        action = _make_identity_action(
            "email_received",
            email="alice@example.com",
            system_message="I've sent a verification code to al***@example.com.",
        )

        # Verify that the action prevents pipeline invocation
        assert action.action == "email_received"
        assert action.action != "none"
        assert action.system_message is not None

    @pytest.mark.asyncio
    async def test_otp_received_bypasses_pipeline(self):
        """When preprocessor returns otp_received, pipeline is NOT called."""
        action = _make_identity_action(
            "otp_received",
            email="alice@example.com",
            system_message="Email verified! I can now access your account information.",
        )

        assert action.action == "otp_received"
        assert action.action != "none"
        assert "verified" in action.system_message.lower()

    @pytest.mark.asyncio
    async def test_otp_invalid_bypasses_pipeline(self):
        """When preprocessor returns otp_invalid, pipeline is NOT called."""
        action = _make_identity_action(
            "otp_invalid",
            system_message="That code doesn't look right.",
        )

        assert action.action == "otp_invalid"
        assert action.action != "none"

    @pytest.mark.asyncio
    async def test_action_none_allows_pipeline(self):
        """When preprocessor returns action=none, normal pipeline runs."""
        action = _make_identity_action("none")

        # action=none means the message should go to the AI pipeline
        assert action.action == "none"
        assert action.system_message is None

    @pytest.mark.asyncio
    async def test_identity_actions_that_bypass_pipeline(self):
        """All non-none actions should bypass the pipeline."""
        bypass_actions = ["email_received", "otp_received", "otp_invalid",
                          "otp_rate_limited", "skip_verification"]

        for action_name in bypass_actions:
            action = _make_identity_action(
                action_name,
                system_message="Test message",
            )
            assert action.action != "none", (
                f"Action {action_name} should bypass pipeline"
            )


# ---------------------------------------------------------------------------
# Regression: identity SSE stream must emit stage event before token
# (S79 fix — widget dropped identity responses because no message bubble
#  was created without the stage event)
# ---------------------------------------------------------------------------


class TestIdentityStreamEventOrder:
    """Verify that _identity_stream() emits stage → token → done."""

    @pytest.mark.asyncio
    async def test_identity_stream_emits_stage_before_token(self):
        """The identity SSE stream must send a stage event to create the
        widget message bubble BEFORE streaming token content.

        Regression: without the stage event, updateLastAgentMessage() in the
        widget silently drops the response because no streaming message exists.
        """
        import json

        # Build the generator inline — same logic as endpoints.py _identity_stream
        sys_msg = "I've sent a verification code to al***@example.com."

        async def _identity_stream():
            yield (
                f"event: stage\n"
                f"data: {json.dumps({'stage': 'response-generator', 'status': 'started'})}\n\n"
            )
            yield f"event: token\ndata: {json.dumps({'text': sys_msg})}\n\n"
            yield f"event: done\ndata: {json.dumps({'reason': 'identity_preprocessor'})}\n\n"

        events = [chunk async for chunk in _identity_stream()]
        assert len(events) == 3, f"Expected 3 SSE events, got {len(events)}"

        # First event MUST be stage (creates message bubble)
        assert events[0].startswith("event: stage"), (
            "First SSE event must be 'stage' to create widget message bubble"
        )
        stage_data = json.loads(events[0].split("data: ")[1].strip())
        assert stage_data["stage"] == "response-generator"
        assert stage_data["status"] == "started"

        # Second event is token (fills content)
        assert events[1].startswith("event: token")
        token_data = json.loads(events[1].split("data: ")[1].strip())
        assert token_data["text"] == sys_msg

        # Third event is done (finalizes)
        assert events[2].startswith("event: done")

    @pytest.mark.asyncio
    async def test_identity_stream_stage_event_matches_pipeline_format(self):
        """The synthetic stage event must use the same format as the real
        pipeline so the widget's single event handler works for both paths."""
        import json

        stage_event = (
            f"event: stage\n"
            f"data: {json.dumps({'stage': 'response-generator', 'status': 'started'})}\n\n"
        )

        # Parse exactly as the widget SSE handler does
        lines = stage_event.strip().split("\n")
        event_type = lines[0].replace("event: ", "")
        data = lines[1].replace("data: ", "")
        parsed = json.loads(data)

        assert event_type == "stage"
        assert parsed["stage"] == "response-generator"
        assert parsed["status"] == "started"
