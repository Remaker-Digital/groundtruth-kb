"""Tests for EscalationHandlerAgent.

Verifies:
    - Escalation context extraction with mocked OpenAI
    - Default fallback when no OpenAI client
    - Graceful handling of OpenAI exceptions
    - JSON parse failure handling
    - Urgency level extraction

Run:
    pytest tests/agents/test_escalation_handler.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.escalation_handler import EscalationHandlerAgent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_openai_response(content: str) -> MagicMock:
    """Build a mock OpenAI chat completion response."""
    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response


def _make_openai_client(response: MagicMock) -> MagicMock:
    """Build a mock OpenAI client."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


# ---------------------------------------------------------------------------
# EH-01 to EH-04: Normal escalation analysis
# ---------------------------------------------------------------------------


class TestEscalationAnalysis:
    """EscalationHandlerAgent normal operation."""

    @pytest.mark.asyncio
    async def test_eh_01_extracts_reason_and_urgency(self):
        """Extracts escalation reason and urgency from model response."""
        resp = _mock_openai_response(
            json.dumps({
                "reason": "Customer wants to speak with a manager about a billing issue",
                "urgency": "high",
                "context_summary": "Billing dispute over $50 charge",
            })
        )
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process(
            {
                "message": "I want to talk to a manager about this charge!",
                "system_prompt": "Analyze escalation.",
            },
            {},
        )

        assert "billing" in result["reason"].lower()
        assert result["urgency"] == "high"
        assert "Billing" in result["context_summary"]
        assert result["model"] == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_eh_02_low_urgency_escalation(self):
        """Low urgency for non-critical escalation."""
        resp = _mock_openai_response(
            json.dumps({
                "reason": "Customer prefers human assistance",
                "urgency": "low",
                "context_summary": "General preference for human agent",
            })
        )
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process(
            {"message": "Can I talk to someone?", "system_prompt": ""},
            {},
        )

        assert result["urgency"] == "low"

    @pytest.mark.asyncio
    async def test_eh_03_includes_system_prompt(self):
        """System prompt is passed to the OpenAI call."""
        resp = _mock_openai_response(
            json.dumps({"reason": "test", "urgency": "medium", "context_summary": ""})
        )
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        await agent.process(
            {"message": "test", "system_prompt": "Custom escalation prompt"},
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        assert messages[0]["content"] == "Custom escalation prompt"

    @pytest.mark.asyncio
    async def test_eh_04_uses_json_mode(self):
        """OpenAI call uses json_object response format."""
        resp = _mock_openai_response(
            json.dumps({"reason": "test", "urgency": "medium", "context_summary": ""})
        )
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        await agent.process({"message": "test", "system_prompt": ""}, {})

        call_kwargs = client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}
        assert call_kwargs["temperature"] == 0.0


# ---------------------------------------------------------------------------
# EH-05 to EH-09: Error handling and fallback
# ---------------------------------------------------------------------------


class TestEscalationFallback:
    """Fallback behavior when OpenAI is unavailable or fails."""

    @pytest.mark.asyncio
    async def test_eh_05_no_client_returns_default(self):
        """Returns default escalation when no OpenAI client."""
        agent = EscalationHandlerAgent()  # No client

        result = await agent.process(
            {"message": "I need help!", "system_prompt": ""},
            {},
        )

        assert result["reason"] == "Customer requested human agent"
        assert result["urgency"] == "medium"
        assert result["context_summary"] == ""

    @pytest.mark.asyncio
    async def test_eh_06_openai_exception_returns_default(self):
        """OpenAI API exception returns default gracefully."""
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process(
            {"message": "Help!", "system_prompt": ""},
            {},
        )

        assert result["reason"] == "Customer requested human agent"
        assert result["urgency"] == "medium"

    @pytest.mark.asyncio
    async def test_eh_07_json_parse_failure(self):
        """Invalid JSON from model uses defaults for missing fields."""
        resp = _mock_openai_response("not json")
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process({"message": "test", "system_prompt": ""}, {})

        assert result["reason"] == "Customer requested human agent"
        assert result["urgency"] == "medium"

    @pytest.mark.asyncio
    async def test_eh_08_partial_json_uses_defaults(self):
        """Partial JSON from model uses defaults for missing fields."""
        resp = _mock_openai_response(json.dumps({"reason": "Custom reason"}))
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process({"message": "test", "system_prompt": ""}, {})

        assert result["reason"] == "Custom reason"
        assert result["urgency"] == "medium"  # Default
        assert result["context_summary"] == ""  # Default

    @pytest.mark.asyncio
    async def test_eh_09_empty_response_content(self):
        """Empty model response uses defaults."""
        resp = _mock_openai_response("{}")
        client = _make_openai_client(resp)
        agent = EscalationHandlerAgent(openai_client=client)

        result = await agent.process({"message": "test", "system_prompt": ""}, {})

        assert result["reason"] == "Customer requested human agent"


# ---------------------------------------------------------------------------
# EH-10 to EH-11: Agent identity
# ---------------------------------------------------------------------------


class TestEscalationIdentity:
    """Agent identity and configuration."""

    def test_eh_10_agent_type(self):
        """Agent type is 'escalation-handler'."""
        agent = EscalationHandlerAgent()
        assert agent.agent_type == "escalation-handler"

    def test_eh_11_configure(self):
        """configure() injects client."""
        agent = EscalationHandlerAgent()
        mock_client = MagicMock()
        agent.configure(mock_client)
        assert agent._openai_client is mock_client
        assert agent._configured is True
