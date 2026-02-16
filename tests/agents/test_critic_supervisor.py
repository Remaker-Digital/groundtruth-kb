"""Tests for CriticSupervisorAgent.

Verifies:
    - Approval path (model approves response)
    - Rejection path (model rejects response)
    - Modification path (model modifies response)
    - Fail-closed semantics (no client → block)
    - Fail-closed on exception
    - Immutable system prompt usage
    - KB context awareness (anti false-positive)
    - Modified verdict without text → rejection

Run:
    pytest tests/agents/test_critic_supervisor.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.critic_supervisor import CriticSupervisorAgent
from src.multi_tenant.critic_policy import (
    SAFE_FALLBACK_MESSAGE,
    CriticBlockReason,
)


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
# CS-01 to CS-04: Approval / Rejection / Modification
# ---------------------------------------------------------------------------


class TestCriticVerdicts:
    """CriticSupervisorAgent verdict processing."""

    @pytest.mark.asyncio
    async def test_cs_01_approved_response(self):
        """Model approves response — approved=True, safe_text=original."""
        resp = _mock_openai_response(
            json.dumps({
                "verdict": "approved",
                "flags": [],
                "modified_response": None,
                "reasoning": "Response is appropriate.",
            })
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Our return policy allows 30-day returns.",
                "customer_message": "What is your return policy?",
                "knowledge_titles": ["Return Policy"],
                "conversation_id": "c-001",
            },
            {},
        )

        assert result["approved"] is True
        assert result["verdict"] == "approved"
        assert result["flags"] == []
        assert result["safe_text"] == "Our return policy allows 30-day returns."
        assert result["block_reason"] is None

    @pytest.mark.asyncio
    async def test_cs_02_rejected_response(self):
        """Model rejects response — approved=False, safe_text=fallback."""
        resp = _mock_openai_response(
            json.dumps({
                "verdict": "rejected",
                "flags": ["potential_hallucination"],
                "modified_response": None,
                "reasoning": "Response contains unverified claims.",
            })
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "We guarantee 100% satisfaction!",
                "customer_message": "Do you guarantee satisfaction?",
                "conversation_id": "c-002",
            },
            {},
        )

        assert result["approved"] is False
        assert result["verdict"] == "rejected"
        assert "potential_hallucination" in result["flags"]
        assert result["safe_text"] == SAFE_FALLBACK_MESSAGE
        assert result["block_reason"] == CriticBlockReason.REJECTED.value

    @pytest.mark.asyncio
    async def test_cs_03_modified_response(self):
        """Model modifies response — approved=True, safe_text=modified."""
        resp = _mock_openai_response(
            json.dumps({
                "verdict": "modified",
                "flags": ["tone_adjustment"],
                "modified_response": "Here is the corrected response.",
                "reasoning": "Adjusted tone for professionalism.",
            })
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Original response.",
                "customer_message": "Test",
                "conversation_id": "c-003",
            },
            {},
        )

        assert result["approved"] is True
        assert result["verdict"] == "modified"
        assert result["safe_text"] == "Here is the corrected response."
        assert result["modified_response"] == "Here is the corrected response."

    @pytest.mark.asyncio
    async def test_cs_04_modified_without_text_is_rejection(self):
        """Modified verdict without modified_response → treated as rejection."""
        resp = _mock_openai_response(
            json.dumps({
                "verdict": "modified",
                "flags": [],
                "modified_response": None,
                "reasoning": "Should modify but didn't provide text.",
            })
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Original.",
                "customer_message": "Test",
                "conversation_id": "c-004",
            },
            {},
        )

        assert result["approved"] is False
        assert "modified_verdict_without_text" in result["flags"]
        assert result["safe_text"] == SAFE_FALLBACK_MESSAGE


# ---------------------------------------------------------------------------
# CS-05 to CS-08: Fail-closed semantics
# ---------------------------------------------------------------------------


class TestFailClosed:
    """Fail-closed behavior: any failure → block."""

    @pytest.mark.asyncio
    async def test_cs_05_no_client_blocks(self):
        """No OpenAI client → BLOCKED (fail-closed)."""
        agent = CriticSupervisorAgent()  # No client

        result = await agent.process(
            {
                "response_text": "Any response",
                "customer_message": "Any message",
                "conversation_id": "c-005",
            },
            {},
        )

        assert result["approved"] is False
        assert result["verdict"] == "unavailable"
        assert result["safe_text"] == SAFE_FALLBACK_MESSAGE
        assert result["block_reason"] == CriticBlockReason.UNAVAILABLE.value

    @pytest.mark.asyncio
    async def test_cs_06_openai_exception_blocks(self):
        """OpenAI API exception → BLOCKED (fail-closed)."""
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Response",
                "customer_message": "Message",
                "conversation_id": "c-006",
            },
            {},
        )

        assert result["approved"] is False
        assert result["safe_text"] == SAFE_FALLBACK_MESSAGE
        assert result["block_reason"] == CriticBlockReason.ERROR.value

    @pytest.mark.asyncio
    async def test_cs_07_json_parse_failure_rejects(self):
        """Invalid JSON from Critic model → defaults to rejected."""
        resp = _mock_openai_response("not valid json")
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Response",
                "customer_message": "Message",
                "conversation_id": "c-007",
            },
            {},
        )

        # JSON parse fails → parsed = {} → verdict defaults to "rejected"
        assert result["approved"] is False
        assert result["verdict"] == "rejected"

    @pytest.mark.asyncio
    async def test_cs_08_unknown_verdict_rejects(self):
        """Unknown verdict string → treated as rejected."""
        resp = _mock_openai_response(
            json.dumps({
                "verdict": "maybe_ok",
                "flags": [],
            })
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "Response",
                "customer_message": "Message",
                "conversation_id": "c-008",
            },
            {},
        )

        assert result["approved"] is False


# ---------------------------------------------------------------------------
# CS-09 to CS-12: KB context and prompt construction
# ---------------------------------------------------------------------------


class TestCriticPromptConstruction:
    """Prompt construction and KB context handling."""

    @pytest.mark.asyncio
    async def test_cs_09_kb_titles_included_in_prompt(self):
        """Knowledge base titles included in Critic prompt to prevent false positives."""
        resp = _mock_openai_response(
            json.dumps({"verdict": "approved", "flags": [], "reasoning": "OK"})
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        await agent.process(
            {
                "response_text": "We offer 30-day returns.",
                "customer_message": "Return policy?",
                "knowledge_titles": ["Return Policy", "Shipping Guide"],
                "conversation_id": "c-009",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        user_prompt = messages[1]["content"]

        assert "Return Policy" in user_prompt
        assert "Shipping Guide" in user_prompt
        assert "knowledge base articles" in user_prompt.lower()

    @pytest.mark.asyncio
    async def test_cs_10_no_kb_titles_omits_context(self):
        """No KB titles → no KB context line in prompt."""
        resp = _mock_openai_response(
            json.dumps({"verdict": "approved", "flags": []})
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        await agent.process(
            {
                "response_text": "Hello!",
                "customer_message": "Hi",
                "knowledge_titles": [],
                "conversation_id": "c-010",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        user_prompt = call_kwargs["messages"][1]["content"]
        assert "KNOWLEDGE BASE ARTICLES" not in user_prompt

    @pytest.mark.asyncio
    async def test_cs_11_uses_json_mode(self):
        """Critic uses JSON response format."""
        resp = _mock_openai_response(
            json.dumps({"verdict": "approved", "flags": []})
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        await agent.process(
            {
                "response_text": "test",
                "customer_message": "test",
                "conversation_id": "c-011",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}
        assert call_kwargs["temperature"] == 0.0

    @pytest.mark.asyncio
    async def test_cs_12_result_includes_metadata(self):
        """Result includes model, latency_ms, and request_id."""
        resp = _mock_openai_response(
            json.dumps({"verdict": "approved", "flags": []})
        )
        client = _make_openai_client(resp)
        agent = CriticSupervisorAgent(openai_client=client)

        result = await agent.process(
            {
                "response_text": "test",
                "customer_message": "test",
                "conversation_id": "c-012",
            },
            {},
        )

        assert result["model"] == "gpt-4o-mini"
        assert isinstance(result["latency_ms"], float)
        assert result["request_id"].startswith("critic-c-012-")


# ---------------------------------------------------------------------------
# CS-13 to CS-15: Agent identity and lifecycle
# ---------------------------------------------------------------------------


class TestCriticIdentity:
    """Agent identity and configuration."""

    def test_cs_13_agent_type(self):
        """Agent type is 'critic-supervisor'."""
        agent = CriticSupervisorAgent()
        assert agent.agent_type == "critic-supervisor"
        assert agent.create_agent_topic() == "critic-supervisor"

    def test_cs_14_configure(self):
        """configure() injects client."""
        agent = CriticSupervisorAgent()
        mock_client = MagicMock()
        agent.configure(mock_client)
        assert agent._openai_client is mock_client
        assert agent._configured is True

    @pytest.mark.asyncio
    async def test_cs_15_fail_closed_result_structure(self):
        """_fail_closed_result returns correct structure."""
        agent = CriticSupervisorAgent()
        result = agent._fail_closed_result("c-test", "test_reason", 42.5)

        assert result["approved"] is False
        assert result["verdict"] == "unavailable"
        assert "test_reason" in result["flags"]
        assert result["safe_text"] == SAFE_FALLBACK_MESSAGE
        assert result["latency_ms"] == 42.5
        assert "failclosed" in result["request_id"]
