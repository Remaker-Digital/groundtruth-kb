# Agent Red Customer Experience — Escalation Handler Agent
#
# Evaluates escalation context when the Intent Classifier detects an
# escalation intent. Determines reason, urgency, and context summary
# for the human agent handoff.
#
# Extracted from pipeline.py _call_escalation_handler_direct().
#
# Input payload:
#   {"message": str, "system_prompt": str}
#
# Output payload:
#   {"reason": str, "urgency": str, "context_summary": str, "model": str}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import json
import logging
import os
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

AZURE_IC_MODEL = os.environ.get("AZURE_IC_MODEL", "gpt-4o-mini")


class EscalationHandlerAgent(AgentRedBaseAgent):
    """Evaluate escalation context for human agent handoff.

    Uses Azure OpenAI GPT-4o-mini to determine escalation reason,
    urgency level, and a context summary for the human agent.
    """

    agent_type = "escalation-handler"

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
        """Evaluate escalation context.

        Args:
            payload: {"message": str, "system_prompt": str}
            headers: A2A headers.

        Returns:
            {"reason": str, "urgency": str, "context_summary": str, "model": str}
        """
        message = payload.get("message", "")
        system_prompt = payload.get("system_prompt", "")

        if not self._openai_client:
            return {
                "reason": "Customer requested human agent",
                "urgency": "medium",
                "context_summary": "",
                "model": AZURE_IC_MODEL,
            }

        esc_user_prompt = (
            "Analyze the following customer message and determine the "
            "escalation reason. Respond with a JSON object containing:\n"
            '- "reason": a clear, concise summary of why the customer needs '
            "human assistance (1-2 sentences)\n"
            '- "urgency": "low", "medium", or "high"\n'
            '- "context_summary": brief summary for the human agent\n\n'
            f"Customer message: {message}"
        )

        try:
            response = await self._openai_client.chat.completions.create(
                model=AZURE_IC_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": esc_user_prompt},
                ],
                temperature=0.0,
                max_tokens=200,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {}

            return {
                "reason": parsed.get("reason", "Customer requested human agent"),
                "urgency": parsed.get("urgency", "medium"),
                "context_summary": parsed.get("context_summary", ""),
                "model": AZURE_IC_MODEL,
            }
        except Exception:
            return {
                "reason": "Customer requested human agent",
                "urgency": "medium",
                "context_summary": "",
                "model": AZURE_IC_MODEL,
            }
