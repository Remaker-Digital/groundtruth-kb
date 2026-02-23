# Agent Red Customer Experience — Critic/Supervisor Agent
#
# Validates AI-generated responses for safety (fail-closed gate).
# The Critic's system prompt is IMMUTABLE — merchant config has zero
# influence (Decision #23, Decision #50).
#
# Extracted from pipeline.py _validate_with_critic_direct().
#
# Input payload:
#   {"response_text": str, "customer_message": str,
#    "knowledge_titles": [str], "conversation_id": str}
#
# Output payload:
#   {"approved": bool, "verdict": str, "flags": [str],
#    "modified_response": str|null, "block_reason": str|null,
#    "model": str, "latency_ms": float}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from src.agents.base import AgentRedBaseAgent
from src.multi_tenant.critic_policy import (
    SAFE_FALLBACK_MESSAGE,
    CriticBlockReason,
    CriticResult,
    CriticVerdict,
)

logger = logging.getLogger(__name__)

AZURE_CR_MODEL = os.environ.get("AZURE_CR_MODEL", "gpt-4o-mini")


class CriticSupervisorAgent(AgentRedBaseAgent):
    """Validate AI responses for safety violations (fail-closed).

    The Critic uses an IMMUTABLE system prompt from the platform base
    prompts. Merchant configuration cannot modify Critic behavior.

    Fail-closed semantics:
    - Model approves → deliver response
    - Model rejects → block + use fallback
    - Call fails → block + use fallback
    """

    agent_type = "critic-supervisor"

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
        """Validate an AI-generated response.

        Args:
            payload: {"response_text": str, "customer_message": str,
                      "knowledge_titles": [str], "conversation_id": str}
            headers: A2A headers.

        Returns:
            {"approved": bool, "verdict": str, "flags": [str],
             "modified_response": str|null, "safe_text": str,
             "block_reason": str|null, "model": str, "latency_ms": float}
        """
        response_text = payload.get("response_text", "")
        customer_message = payload.get("customer_message", "")
        knowledge_titles = payload.get("knowledge_titles") or []
        conversation_id = payload.get("conversation_id", "unknown")

        # Fail-closed: if no OpenAI client, block the response
        if not self._openai_client:
            logger.warning("Critic: no OpenAI client — BLOCKING (fail-closed)")
            return self._fail_closed_result(conversation_id, "no_openai_client")

        start_time = time.monotonic()
        request_id = f"critic-{conversation_id}-{int(time.time() * 1000)}"

        try:
            # Build KB context line to prevent false-positive blocking
            kb_context_line = ""
            if knowledge_titles:
                titles_str = ", ".join(f'"{t}"' for t in knowledge_titles[:10])
                kb_context_line = (
                    f"\nKNOWLEDGE BASE ARTICLES USED:\n{titles_str}\n"
                    "The response above was generated from these knowledge base "
                    "articles, which are curated by the merchant. Content derived "
                    "from knowledge base articles is legitimate product information "
                    "and should NOT be flagged as hallucination or internal details.\n"
                )

            critic_user_prompt = (
                "Review the following AI-generated customer service response.\n\n"
                f"CUSTOMER MESSAGE:\n{customer_message}\n\n"
                f"AI RESPONSE:\n{response_text}\n"
                f"{kb_context_line}\n"
                "Return a JSON object with:\n"
                '- "verdict": "approved", "rejected", or "modified"\n'
                '- "flags": array of concerns (empty array if none)\n'
                '- "modified_response": corrected text if verdict is "modified"\n'
                '- "reasoning": brief explanation\n\n'
                "DEFAULT TO APPROVED.  Only reject if the response contains "
                "one of the specific violations listed in your system prompt "
                "(cross-customer PII leakage, literal secrets, medical/legal/"
                "financial advice, hate speech, or policy contradictions).  "
                "Using the customer's own name or preferences back to them "
                "is NORMAL and must be approved.  ASKING the customer for "
                "their email address or name for identification purposes is "
                "STANDARD customer service and must be approved.  Describing "
                "product features, technology, architecture, or capabilities "
                "is never a violation."
            )

            # Immutable Critic system prompt
            from src.multi_tenant.system_prompt_builder import AgentRole, _PLATFORM_BASE
            critic_system_prompt = _PLATFORM_BASE.get(
                AgentRole.CRITIC_SUPERVISOR, ""
            )

            response = await self._openai_client.chat.completions.create(
                model=AZURE_CR_MODEL,
                messages=[
                    {"role": "system", "content": critic_system_prompt},
                    {"role": "user", "content": critic_user_prompt},
                ],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"},
            )

            elapsed_ms = (time.monotonic() - start_time) * 1000
            content = response.choices[0].message.content or "{}"

            logger.info(
                "Critic raw response: conv=%s content=%s",
                conversation_id[:8], content[:500],
            )

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(
                    "Critic JSON parse failed: conv=%s content=%s",
                    conversation_id[:8], content[:200],
                )
                parsed = {}

            verdict_str = parsed.get("verdict", "rejected")
            reasoning = parsed.get("reasoning", "")
            try:
                verdict = CriticVerdict(verdict_str)
            except ValueError:
                logger.warning(
                    "Critic unknown verdict: conv=%s verdict=%s",
                    conversation_id[:8], verdict_str,
                )
                verdict = CriticVerdict.REJECTED

            approved = verdict in (CriticVerdict.APPROVED, CriticVerdict.MODIFIED)
            flags = parsed.get("flags", [])
            modified_response = parsed.get("modified_response")

            if verdict == CriticVerdict.MODIFIED and not modified_response:
                approved = False
                flags.append("modified_verdict_without_text")

            block_reason = None if approved else CriticBlockReason.REJECTED.value
            safe_text = (
                (modified_response or response_text)
                if approved
                else SAFE_FALLBACK_MESSAGE
            )

            logger.info(
                "Critic decision: conv=%s approved=%s verdict=%s flags=%s",
                conversation_id[:8], approved, verdict_str, flags,
            )

            return {
                "approved": approved,
                "verdict": verdict_str,
                "flags": flags,
                "modified_response": modified_response if approved else None,
                "safe_text": safe_text,
                "block_reason": block_reason,
                "model": AZURE_CR_MODEL,
                "latency_ms": round(elapsed_ms, 1),
                "request_id": request_id,
            }

        except Exception as exc:
            # Fail-closed: any error means block the response
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.warning(
                "Critic call failed — BLOCKING (fail-closed): conv=%s error=%s",
                conversation_id, exc,
            )
            return self._fail_closed_result(
                conversation_id, "critic_error", elapsed_ms,
            )

    def _fail_closed_result(
        self,
        conversation_id: str,
        reason: str,
        elapsed_ms: float = 0.0,
    ) -> dict[str, Any]:
        """Build a fail-closed rejection result."""
        return {
            "approved": False,
            "verdict": "unavailable",
            "flags": [reason],
            "modified_response": None,
            "safe_text": SAFE_FALLBACK_MESSAGE,
            "block_reason": CriticBlockReason.UNAVAILABLE.value
            if reason == "no_openai_client"
            else CriticBlockReason.ERROR.value,
            "model": AZURE_CR_MODEL,
            "latency_ms": round(elapsed_ms, 1),
            "request_id": f"critic-{conversation_id}-failclosed",
        }
