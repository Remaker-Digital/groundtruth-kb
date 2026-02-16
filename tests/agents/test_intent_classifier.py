"""Tests for IntentClassifierAgent.

Verifies:
    - Classification with mocked OpenAI client
    - Graceful fallback when no OpenAI client
    - Invalid intent normalization (unknown → general_inquiry)
    - JSON parse failure handling
    - Confidence float coercion
    - Token usage extraction

Run:
    pytest tests/agents/test_intent_classifier.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.intent_classifier import (
    INTENT_TAXONOMY,
    IntentClassifierAgent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_openai_response(
    content: str,
    prompt_tokens: int = 50,
    completion_tokens: int = 30,
) -> MagicMock:
    """Build a mock OpenAI chat completion response."""
    usage = MagicMock()
    usage.prompt_tokens = prompt_tokens
    usage.completion_tokens = completion_tokens

    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


def _make_openai_client(response: MagicMock) -> MagicMock:
    """Build a mock OpenAI client that returns a canned response."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


# ---------------------------------------------------------------------------
# IC-01 to IC-03: Basic classification
# ---------------------------------------------------------------------------


class TestClassification:
    """IntentClassifierAgent classification behavior."""

    @pytest.mark.asyncio
    async def test_ic_01_classifies_greeting(self):
        """Correctly classifies a greeting message."""
        resp = _mock_openai_response(
            json.dumps({"intent": "greeting", "confidence": 0.95, "reasoning": "Hi"}),
        )
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process(
            {"message": "Hello!", "system_prompt": "You are a classifier."},
            {"x-tenant-id": "t-001"},
        )

        assert result["intent"] == "greeting"
        assert result["confidence"] == 0.95
        assert result["model"] == "gpt-4o-mini"
        assert result["tokens_input"] == 50
        assert result["tokens_output"] == 30

    @pytest.mark.asyncio
    async def test_ic_02_classifies_product_question(self):
        """Correctly classifies a product question."""
        resp = _mock_openai_response(
            json.dumps({"intent": "product_question", "confidence": 0.88}),
        )
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process(
            {"message": "What colors does the jacket come in?", "system_prompt": ""},
            {},
        )
        assert result["intent"] == "product_question"
        assert result["confidence"] == 0.88

    @pytest.mark.asyncio
    async def test_ic_03_all_taxonomy_intents_recognized(self):
        """Every intent in the taxonomy is accepted without normalization."""
        for intent_name in INTENT_TAXONOMY:
            resp = _mock_openai_response(
                json.dumps({"intent": intent_name, "confidence": 0.9}),
            )
            client = _make_openai_client(resp)
            agent = IntentClassifierAgent(openai_client=client)

            result = await agent.process({"message": "test"}, {})
            assert result["intent"] == intent_name, f"Failed for {intent_name}"


# ---------------------------------------------------------------------------
# IC-04 to IC-07: Error handling and edge cases
# ---------------------------------------------------------------------------


class TestClassificationEdgeCases:
    """Edge case handling for IntentClassifierAgent."""

    @pytest.mark.asyncio
    async def test_ic_04_no_openai_client_returns_default(self):
        """Returns general_inquiry default when no OpenAI client."""
        agent = IntentClassifierAgent()  # No client

        result = await agent.process(
            {"message": "Hi", "system_prompt": ""},
            {},
        )

        assert result["intent"] == "general_inquiry"
        assert result["confidence"] == 0.5
        assert result["tokens_input"] == 0
        assert result["tokens_output"] == 0

    @pytest.mark.asyncio
    async def test_ic_05_unknown_intent_normalized_to_general_inquiry(self):
        """Unknown intent from model is normalized to general_inquiry."""
        resp = _mock_openai_response(
            json.dumps({"intent": "unknown_made_up_intent", "confidence": 0.7}),
        )
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process({"message": "test"}, {})
        assert result["intent"] == "general_inquiry"

    @pytest.mark.asyncio
    async def test_ic_06_json_parse_failure_returns_default(self):
        """Invalid JSON from model returns general_inquiry default."""
        resp = _mock_openai_response("not valid json at all")
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process({"message": "test"}, {})
        assert result["intent"] == "general_inquiry"
        assert result["confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_ic_07_empty_response_content(self):
        """Empty/null model response content returns default."""
        resp = _mock_openai_response("{}")
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process({"message": "test"}, {})
        assert result["intent"] == "general_inquiry"

    @pytest.mark.asyncio
    async def test_ic_08_confidence_coerced_to_float(self):
        """String confidence from model is coerced to float."""
        resp = _mock_openai_response(
            json.dumps({"intent": "greeting", "confidence": "0.82"}),
        )
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process({"message": "hi"}, {})
        assert isinstance(result["confidence"], float)
        assert result["confidence"] == 0.82

    @pytest.mark.asyncio
    async def test_ic_09_no_usage_returns_zero_tokens(self):
        """Handles None usage gracefully."""
        resp = _mock_openai_response(
            json.dumps({"intent": "greeting", "confidence": 0.9}),
        )
        resp.usage = None
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        result = await agent.process({"message": "hi"}, {})
        assert result["tokens_input"] == 0
        assert result["tokens_output"] == 0


# ---------------------------------------------------------------------------
# IC-10 to IC-12: Agent identity and lifecycle
# ---------------------------------------------------------------------------


class TestIntentClassifierIdentity:
    """Agent identity and configuration."""

    def test_ic_10_agent_type(self):
        """Agent type is 'intent-classifier'."""
        agent = IntentClassifierAgent()
        assert agent.agent_type == "intent-classifier"
        assert agent.create_agent_topic() == "intent-classifier"

    def test_ic_11_configure_sets_client(self):
        """configure() injects the OpenAI client."""
        agent = IntentClassifierAgent()
        mock_client = MagicMock()
        agent.configure(mock_client)
        assert agent._openai_client is mock_client
        assert agent._configured is True

    @pytest.mark.asyncio
    async def test_ic_12_handle_message_integration(self):
        """Full handle_message() round-trip via A2A protocol."""
        from src.agents.base import make_request, parse_payload

        resp = _mock_openai_response(
            json.dumps({"intent": "complaint", "confidence": 0.91}),
        )
        client = _make_openai_client(resp)
        agent = IntentClassifierAgent(openai_client=client)

        req = make_request(
            "intent-classifier",
            {"message": "This product is broken!", "system_prompt": "Classify."},
            tenant_id="t-001",
        )
        msg = await agent.handle_message(req)
        result = parse_payload(msg)

        assert result["intent"] == "complaint"
        assert result["_agent"] == "intent-classifier"
        assert "_latency_ms" in result
