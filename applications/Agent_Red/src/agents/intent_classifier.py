# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Agent Red Customer Experience — Intent Classification Agent
#
# Classifies customer messages into one of 17 intent categories using
# Azure OpenAI GPT-4o-mini with JSON mode structured output.
#
# Extracted from pipeline.py _call_intent_classifier_direct().
#
# Input payload:
#   {"message": str, "system_prompt": str}
#
# Output payload:
#   {"intent": str, "confidence": float, "model": str,
#    "tokens_input": int, "tokens_output": int}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import json
import logging
import os
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

# Azure OpenAI model deployment name for intent classification
AZURE_IC_MODEL = os.environ.get("AZURE_IC_MODEL", "gpt-4o-mini")

# Intent classification taxonomy — 18-intent taxonomy (SPEC-1558).
# admin_assistance is ONLY available for admin-key-authenticated requests;
# the pipeline gates this intent from widget-key conversations.
INTENT_TAXONOMY = [
    "general_inquiry",
    "product_question",
    "order_status",
    "return_request",
    "exchange_request",
    "refund_request",
    "shipping_inquiry",
    "pricing_question",
    "availability_check",
    "complaint",
    "feedback",
    "account_issue",
    "payment_issue",
    "subscription_question",
    "technical_support",
    "greeting",
    "escalation",
    "admin_assistance",
]


class IntentClassifierAgent(AgentRedBaseAgent):
    """Classify customer intent from a raw message.

    Uses Azure OpenAI GPT-4o-mini with JSON mode to produce a structured
    classification with intent label and confidence score.
    """

    agent_type = "intent-classifier"

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
        """Classify the customer message intent.

        Args:
            payload: {"message": str, "system_prompt": str}
            headers: A2A headers (x-tenant-id, etc.)

        Returns:
            {"intent": str, "confidence": float, "model": str,
             "tokens_input": int, "tokens_output": int}
        """
        message = payload.get("message", "")
        system_prompt = payload.get("system_prompt", "")

        if not self._openai_client:
            logger.warning(
                "IntentClassifier: no OpenAI client — returning general_inquiry default"
            )
            return {
                "intent": "general_inquiry",
                "confidence": 0.5,
                "model": AZURE_IC_MODEL,
                "tokens_input": 0,
                "tokens_output": 0,
            }

        intent_list = ", ".join(INTENT_TAXONOMY)
        ic_user_prompt = (
            f"Classify the following customer message into exactly one intent.\n"
            f"Valid intents: {intent_list}\n\n"
            f"Respond with a JSON object containing:\n"
            f'- "intent": one of the valid intents listed above\n'
            f'- "confidence": a number between 0.0 and 1.0\n'
            f'- "reasoning": a brief explanation (1 sentence)\n\n'
            f"Customer message: {message}"
        )

        response = await self._openai_client.chat.completions.create(
            model=AZURE_IC_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ic_user_prompt},
            ],
            temperature=0.0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {}

        intent = parsed.get("intent", "general_inquiry")
        if intent not in INTENT_TAXONOMY:
            intent = "general_inquiry"

        return {
            "intent": intent,
            "confidence": float(parsed.get("confidence", 0.5)),
            "model": AZURE_IC_MODEL,
            "tokens_input": response.usage.prompt_tokens if response.usage else 0,
            "tokens_output": response.usage.completion_tokens if response.usage else 0,
        }
