"""Tests for ResponseGeneratorAgent.

Verifies:
    - Non-streaming process() assembles full response
    - Streaming generate_stream() yields chunks
    - Knowledge context injection (VERIFIED KNOWLEDGE BASE block)
    - Greeting intent routing (warm response prompt)
    - Temperature selection (0.3 knowledge vs 0.7 general)
    - Conversation history inclusion
    - Fallback when no OpenAI client

Run:
    pytest tests/agents/test_response_generator.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.response_generator import ResponseGeneratorAgent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class MockStreamChunk:
    """A single streaming chunk from OpenAI."""

    def __init__(self, content: str | None):
        delta = MagicMock()
        delta.content = content
        choice = MagicMock()
        choice.delta = delta
        self.choices = [choice]


class MockAsyncStream:
    """Async iterator that yields streaming chunks."""

    def __init__(self, chunks: list[str]):
        self._chunks = [MockStreamChunk(c) for c in chunks]
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._chunks):
            raise StopAsyncIteration
        chunk = self._chunks[self._index]
        self._index += 1
        return chunk


def _make_streaming_client(chunks: list[str]) -> MagicMock:
    """Build a mock OpenAI client that returns streaming chunks."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=MockAsyncStream(chunks)
    )
    return client


# ---------------------------------------------------------------------------
# RG-01 to RG-04: Non-streaming process()
# ---------------------------------------------------------------------------


class TestNonStreamingProcess:
    """ResponseGeneratorAgent.process() (non-streaming A2A path)."""

    @pytest.mark.asyncio
    async def test_rg_01_assembles_full_response(self):
        """process() assembles all streaming chunks into full response."""
        client = _make_streaming_client(["Hello", " there", "!"])
        agent = ResponseGeneratorAgent(openai_client=client)

        result = await agent.process(
            {
                "message": "Hi",
                "intent": "greeting",
                "system_prompt": "Be helpful.",
                "knowledge_context": "",
            },
            {},
        )

        assert result["response"] == "Hello there!"
        assert result["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_rg_02_uses_custom_model(self):
        """process() uses model from payload."""
        client = _make_streaming_client(["OK"])
        agent = ResponseGeneratorAgent(openai_client=client)

        result = await agent.process(
            {"message": "test", "model": "ft-custom-model"},
            {},
        )

        assert result["model"] == "ft-custom-model"

    @pytest.mark.asyncio
    async def test_rg_03_no_client_returns_fallback(self):
        """process() returns fallback when no OpenAI client."""
        agent = ResponseGeneratorAgent()  # No client

        result = await agent.process(
            {"message": "Hi", "system_prompt": ""},
            {},
        )

        assert "unable to generate" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_rg_04_tokens_zero_for_streaming(self):
        """Token counts are 0 (unavailable from streaming)."""
        client = _make_streaming_client(["response"])
        agent = ResponseGeneratorAgent(openai_client=client)

        result = await agent.process({"message": "test"}, {})
        assert result["tokens_input"] == 0
        assert result["tokens_output"] == 0


# ---------------------------------------------------------------------------
# RG-05 to RG-08: Streaming generate_stream()
# ---------------------------------------------------------------------------


class TestStreamingGeneration:
    """ResponseGeneratorAgent.generate_stream() behavior."""

    @pytest.mark.asyncio
    async def test_rg_05_yields_chunks(self):
        """generate_stream() yields individual chunks."""
        client = _make_streaming_client(["chunk1", "chunk2", "chunk3"])
        agent = ResponseGeneratorAgent(openai_client=client)

        chunks = []
        async for chunk in agent.generate_stream(
            customer_message="test",
            intent="general_inquiry",
            knowledge_context="",
            system_prompt="Be helpful.",
        ):
            chunks.append(chunk)

        assert chunks == ["chunk1", "chunk2", "chunk3"]

    @pytest.mark.asyncio
    async def test_rg_06_no_client_yields_fallback(self):
        """generate_stream() yields fallback when no client."""
        agent = ResponseGeneratorAgent()

        chunks = []
        async for chunk in agent.generate_stream(
            customer_message="Hi",
            intent="greeting",
            knowledge_context="",
            system_prompt="",
        ):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "unable to generate" in chunks[0].lower()


# ---------------------------------------------------------------------------
# RG-09 to RG-12: Knowledge context and prompt construction
# ---------------------------------------------------------------------------


class TestPromptConstruction:
    """System prompt and knowledge context injection."""

    @pytest.mark.asyncio
    async def test_rg_09_knowledge_context_injected(self):
        """Knowledge context added to system prompt with delimiter block."""
        client = _make_streaming_client(["OK"])
        agent = ResponseGeneratorAgent(openai_client=client)

        await agent.process(
            {
                "message": "What is your return policy?",
                "intent": "return_request",
                "knowledge_context": "Return within 30 days.",
                "system_prompt": "You are a helpful assistant.",
            },
            {},
        )

        # Verify the system prompt was augmented
        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        system_content = messages[0]["content"]

        assert "VERIFIED KNOWLEDGE BASE" in system_content
        assert "Return within 30 days." in system_content
        assert "END OF KNOWLEDGE BASE" in system_content

    @pytest.mark.asyncio
    async def test_rg_10_greeting_skips_knowledge_injection(self):
        """Greeting intent does NOT inject knowledge context."""
        client = _make_streaming_client(["Hi!"])
        agent = ResponseGeneratorAgent(openai_client=client)

        await agent.process(
            {
                "message": "Hello",
                "intent": "greeting",
                "knowledge_context": "Some KB context",
                "system_prompt": "Be helpful.",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        system_content = messages[0]["content"]

        assert "VERIFIED KNOWLEDGE BASE" not in system_content

    @pytest.mark.asyncio
    async def test_rg_11_greeting_has_warm_prompt(self):
        """Greeting intent adds warm response instruction."""
        client = _make_streaming_client(["Hi!"])
        agent = ResponseGeneratorAgent(openai_client=client)

        await agent.process(
            {"message": "Hello", "intent": "greeting", "system_prompt": ""},
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        user_content = messages[-1]["content"]

        assert "warmly" in user_content.lower() or "friendly" in user_content.lower()

    @pytest.mark.asyncio
    async def test_rg_12_temperature_knowledge_grounded(self):
        """Temperature 0.3 when knowledge context provided."""
        client = _make_streaming_client(["OK"])
        agent = ResponseGeneratorAgent(openai_client=client)

        await agent.process(
            {
                "message": "test",
                "intent": "product_question",
                "knowledge_context": "Some context",
                "system_prompt": "",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_rg_13_temperature_general(self):
        """Temperature 0.7 when no knowledge context."""
        client = _make_streaming_client(["OK"])
        agent = ResponseGeneratorAgent(openai_client=client)

        await agent.process(
            {
                "message": "test",
                "intent": "general_inquiry",
                "knowledge_context": "",
                "system_prompt": "",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.7


# ---------------------------------------------------------------------------
# RG-14 to RG-16: Conversation history and identity
# ---------------------------------------------------------------------------


class TestConversationHistory:
    """Multi-turn conversation history handling."""

    @pytest.mark.asyncio
    async def test_rg_14_history_included_in_messages(self):
        """Conversation history is included in the message list."""
        client = _make_streaming_client(["OK"])
        agent = ResponseGeneratorAgent(openai_client=client)

        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First reply"},
        ]

        await agent.process(
            {
                "message": "Follow-up",
                "conversation_history": history,
                "system_prompt": "Be helpful.",
            },
            {},
        )

        call_kwargs = client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]

        # System + 2 history + current user = 4
        assert len(messages) == 4
        assert messages[1]["content"] == "First message"
        assert messages[2]["content"] == "First reply"
        assert messages[3]["content"] == "Follow-up"

    def test_rg_15_agent_type(self):
        """Agent type is 'response-generator'."""
        agent = ResponseGeneratorAgent()
        assert agent.agent_type == "response-generator"

    def test_rg_16_configure(self):
        """configure() injects client."""
        agent = ResponseGeneratorAgent()
        mock_client = MagicMock()
        agent.configure(mock_client)
        assert agent._openai_client is mock_client
        assert agent._configured is True
