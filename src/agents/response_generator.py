# Agent Red Customer Experience — Response Generator Agent
#
# Generates AI customer service responses using Azure OpenAI with SSE
# streaming. Receives classified intent, knowledge context, and
# conversation history; produces a natural language response.
#
# Extracted from pipeline.py _call_response_generator_stream_direct().
#
# Input payload:
#   {"message": str, "intent": str, "knowledge_context": str,
#    "system_prompt": str, "model": str, "conversation_history": list,
#    "timeout_seconds": float}
#
# Output payload (non-streaming):
#   {"response": str, "model": str, "tokens_input": int, "tokens_output": int}
#
# Streaming: When invoked via the container's /generate/stream endpoint,
# the FastAPI app yields SSE chunks. The A2A handle_message() path returns
# the full assembled response (non-streaming) for protocol compatibility.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

AZURE_RG_MODEL = os.environ.get("AZURE_RG_MODEL", "gpt-4o")


class ResponseGeneratorAgent(AgentRedBaseAgent):
    """Generate AI customer service responses.

    Uses Azure OpenAI (GPT-4o by default, or fine-tuned model for
    Enterprise tenants) with multi-turn conversation history and
    injected knowledge context.
    """

    agent_type = "response-generator"

    def __init__(self, openai_client: Any = None) -> None:
        super().__init__()
        self._openai_client = openai_client

    def configure(self, openai_client: Any) -> None:
        """Inject the Azure OpenAI client after construction."""
        self._openai_client = openai_client
        self._configured = True

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Generate a response (non-streaming, for A2A protocol).

        For SSE streaming, use generate_stream() directly from the
        container's FastAPI endpoint.

        Args:
            payload: {"message": str, "intent": str, "knowledge_context": str,
                      "system_prompt": str, "model": str,
                      "conversation_history": list, "timeout_seconds": float}
            headers: A2A headers.

        Returns:
            {"response": str, "model": str, "tokens_input": int, "tokens_output": int}
        """
        message = payload.get("message", "")
        intent = payload.get("intent", "general_inquiry")
        knowledge_context = payload.get("knowledge_context", "")
        system_prompt = payload.get("system_prompt", "")
        model = payload.get("model", AZURE_RG_MODEL)
        conversation_history = payload.get("conversation_history") or []
        timeout_seconds = payload.get("timeout_seconds", 8.0)

        # Assemble full response from streaming chunks
        full_response = ""
        async for chunk in self.generate_stream(
            customer_message=message,
            intent=intent,
            knowledge_context=knowledge_context,
            system_prompt=system_prompt,
            model=model,
            conversation_history=conversation_history,
            timeout_seconds=timeout_seconds,
        ):
            full_response += chunk

        return {
            "response": full_response,
            "model": model,
            "tokens_input": 0,  # Token counts available only from streaming response
            "tokens_output": 0,
        }

    async def generate_stream(
        self,
        *,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        model: str = "gpt-4o",
        conversation_history: list[dict[str, str]] | None = None,
        timeout_seconds: float = 8.0,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from Azure OpenAI.

        This is the primary generation method, used by both the A2A
        handle_message() path (assembled into full response) and the
        container's SSE /generate/stream endpoint (yielded as chunks).

        Args:
            customer_message: The customer's message text.
            intent: Classified intent (from IntentClassifierAgent).
            knowledge_context: Retrieved KB context (from KnowledgeRetrievalAgent).
            system_prompt: Assembled system prompt (from SystemPromptBuilder).
            model: Azure OpenAI model deployment name.
            conversation_history: Prior turns as [{role, content}] dicts.
            timeout_seconds: Maximum time for the streaming call.

        Yields:
            Response text chunks.
        """
        if not self._openai_client:
            logger.warning(
                "ResponseGenerator: no OpenAI client — yielding fallback"
            )
            yield (
                "I'm sorry, but I'm unable to generate a response right now. "
                "Please try again shortly."
            )
            return

        # Build effective system prompt with knowledge context
        effective_system = system_prompt
        if knowledge_context and intent != "greeting":
            effective_system = (
                f"{system_prompt}\n\n"
                "═══════════════════════════════════════════\n"
                "VERIFIED KNOWLEDGE BASE — USE THIS DATA\n"
                "═══════════════════════════════════════════\n"
                "The articles below contain VERIFIED, ACCURATE information.\n"
                "You MUST incorporate specific details from them into your "
                "response: exact dollar amounts, tier names, feature lists, "
                "quantities, percentages, and policy terms.\n"
                "Include ALL relevant items — if there are multiple tiers, "
                "list ALL of them.  If there are multiple features, list ALL.\n"
                "NEVER say \"check our website\" or \"contact sales\" when the "
                "answer is right here.\n"
                "When a knowledge article includes a 'Source:' URL, include a "
                "clickable link in your response using markdown format: "
                "[descriptive text](url). Place links naturally in context, "
                "e.g. 'You can find our [return policy](https://...) here.' "
                "Do NOT list raw URLs.\n\n"
                f"{knowledge_context}\n\n"
                "═══════════════════════════════════════════\n"
                "END OF KNOWLEDGE BASE\n"
                "═══════════════════════════════════════════"
            )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": effective_system},
        ]

        # Include multi-turn conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Build current user message
        if intent == "greeting":
            user_content = (
                f"{customer_message}\n\n"
                "[Respond warmly and naturally to this greeting. "
                "Be friendly and conversational. Ask how you can help.]"
            )
        else:
            user_content = customer_message

        messages.append({"role": "user", "content": user_content})

        # Use lower temperature for knowledge-grounded queries
        temperature = 0.3 if knowledge_context else 0.7

        stream = await self._openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1024,
            stream=True,
            timeout=timeout_seconds,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
