"""Tests for AgentRedBaseAgent and message utilities.

Verifies:
    - Message construction (make_request, make_response, make_error_response)
    - Payload parsing (parse_payload)
    - handle_message() error handling and wrapping
    - ABC contract enforcement
    - Health check

Run:
    pytest tests/agents/test_base_agent.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agntcy_app_sdk.semantic.message import Message

from src.agents.base import (
    AgentRedBaseAgent,
    make_error_response,
    make_request,
    make_response,
    parse_payload,
)


# ---------------------------------------------------------------------------
# Concrete test agent
# ---------------------------------------------------------------------------


class _EchoAgent(AgentRedBaseAgent):
    """Simple agent that echoes the payload back."""

    agent_type = "test-echo"

    async def process(
        self, payload: dict[str, Any], headers: dict[str, str],
    ) -> dict[str, Any]:
        return {"echo": payload}


class _FailingAgent(AgentRedBaseAgent):
    """Agent that always raises."""

    agent_type = "test-failing"

    async def process(
        self, payload: dict[str, Any], headers: dict[str, str],
    ) -> dict[str, Any]:
        raise RuntimeError("intentional failure")


# ---------------------------------------------------------------------------
# AGENT-BASE-01 to AGENT-BASE-05: Message utilities
# ---------------------------------------------------------------------------


class TestMessageUtilities:
    """Message construction and parsing."""

    def test_base_01_make_request(self):
        """make_request produces correct A2A Message."""
        msg = make_request(
            "intent-classifier",
            {"message": "hello"},
            tenant_id="t-001",
            conversation_id="c-001",
        )
        assert msg.type == "A2ARequest"
        assert msg.method == "POST"
        assert msg.headers["agent-type"] == "intent-classifier"
        assert msg.headers["x-tenant-id"] == "t-001"
        assert msg.headers["x-conversation-id"] == "c-001"
        payload = json.loads(msg.payload)
        assert payload["message"] == "hello"

    def test_base_02_make_response(self):
        """make_response produces correct A2A response Message."""
        msg = make_response(
            "intent-classifier",
            {"intent": "greeting", "confidence": 0.9},
            reply_to="req-123",
            status_code=200,
        )
        assert msg.type == "A2AResponse"
        assert msg.reply_to == "req-123"
        assert msg.status_code == 200
        payload = json.loads(msg.payload)
        assert payload["intent"] == "greeting"

    def test_base_03_make_error_response(self):
        """make_error_response sets status_code=500."""
        msg = make_error_response(
            "intent-classifier",
            "something broke",
            code="test_error",
            reply_to="req-456",
        )
        assert msg.status_code == 500
        payload = json.loads(msg.payload)
        assert payload["error"] == "something broke"
        assert payload["code"] == "test_error"

    def test_base_04_parse_payload_valid(self):
        """parse_payload extracts JSON from Message."""
        msg = Message(
            type="A2ARequest",
            payload=json.dumps({"key": "value"}).encode("utf-8"),
        )
        result = parse_payload(msg)
        assert result["key"] == "value"

    def test_base_05_parse_payload_invalid(self):
        """parse_payload raises ValueError for non-JSON."""
        msg = Message(type="A2ARequest", payload=b"not json")
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_payload(msg)


# ---------------------------------------------------------------------------
# AGENT-BASE-06 to AGENT-BASE-12: handle_message() behavior
# ---------------------------------------------------------------------------


class TestHandleMessage:
    """Base agent's handle_message() wrapping behavior."""

    @pytest.mark.asyncio
    async def test_base_06_echo_agent_returns_result(self):
        """handle_message wraps process() result in response Message."""
        agent = _EchoAgent()
        req = make_request("test-echo", {"data": "test"})
        resp = await agent.handle_message(req)

        assert resp.type == "A2AResponse"
        assert resp.status_code == 200
        result = parse_payload(resp)
        assert result["echo"]["data"] == "test"

    @pytest.mark.asyncio
    async def test_base_07_injects_metadata(self):
        """handle_message injects _agent and _latency_ms."""
        agent = _EchoAgent()
        req = make_request("test-echo", {"x": 1})
        resp = await agent.handle_message(req)
        result = parse_payload(resp)
        assert result["_agent"] == "test-echo"
        assert "_latency_ms" in result

    @pytest.mark.asyncio
    async def test_base_08_failing_agent_returns_error(self):
        """handle_message catches exceptions and returns error response."""
        agent = _FailingAgent()
        req = make_request("test-failing", {"x": 1})
        resp = await agent.handle_message(req)

        assert resp.status_code == 500
        result = parse_payload(resp)
        assert "error" in result
        assert "RuntimeError" in result["error"]
        assert result["code"] == "processing_error"

    @pytest.mark.asyncio
    async def test_base_09_invalid_json_returns_error(self):
        """handle_message returns error for invalid JSON payload."""
        agent = _EchoAgent()
        msg = Message(type="A2ARequest", payload=b"not json")
        resp = await agent.handle_message(msg)

        assert resp.status_code == 500
        result = parse_payload(resp)
        assert result["code"] == "invalid_payload"

    @pytest.mark.asyncio
    async def test_base_10_preserves_reply_to(self):
        """handle_message preserves reply_to correlation ID."""
        agent = _EchoAgent()
        req = make_request("test-echo", {"x": 1}, reply_to="corr-789")
        resp = await agent.handle_message(req)
        assert resp.reply_to == "corr-789"

    def test_base_11_type_returns_a2a(self):
        """Agent type() returns 'A2A'."""
        agent = _EchoAgent()
        assert agent.type() == "A2A"

    def test_base_12_create_agent_topic(self):
        """create_agent_topic returns the agent_type string."""
        agent = _EchoAgent()
        assert agent.create_agent_topic() == "test-echo"


# ---------------------------------------------------------------------------
# AGENT-BASE-13 to AGENT-BASE-15: Health and lifecycle
# ---------------------------------------------------------------------------


class TestHealthAndLifecycle:
    """Health checks and ABC enforcement."""

    def test_base_13_health_before_configure(self):
        """Health reports not_configured before setup."""
        agent = _EchoAgent()
        health = agent.health()
        assert health["status"] == "not_configured"
        assert health["agent"] == "test-echo"

    @pytest.mark.asyncio
    async def test_base_14_health_after_setup(self):
        """Health reports healthy after setup."""
        agent = _EchoAgent()
        await agent.setup()
        health = agent.health()
        assert health["status"] == "healthy"

    def test_base_15_abc_enforcement(self):
        """Cannot instantiate AgentRedBaseAgent directly."""
        with pytest.raises(TypeError):
            AgentRedBaseAgent()  # type: ignore[abstract]
