"""Critic validation and escalation handling mixin.

Provides critic safety validation (fail-closed) and escalation handler
dispatch methods for ChatPipeline.

R10 refactoring — extracted from pipeline.py (session 39).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from src.chat.models import (
    StreamEvent,
    done_event,
    stage_event,
    token_event,
    validated_event,
)
from src.chat.pipeline.constants import (
    AGENT_ESCALATE_PATH,
    USE_AGENT_CONTAINERS,
)
from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE

if TYPE_CHECKING:
    from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget
    from src.multi_tenant.response_explainability import DecisionTraceBuilder

logger = logging.getLogger(__name__)


class CriticEscalationMixin:
    """Mixin providing critic validation and escalation handling for ChatPipeline.

    Methods on this mixin access instance attributes set by ChatPipeline.__init__:
    _critic, _openai_client, _cr_agent, _esc_agent, _session, _agent_urls,
    _get_http_client().
    """

    # -------------------------------------------------------------------
    # Critic validation (fail-closed)
    # -------------------------------------------------------------------

    async def _validate_with_critic(
        self,
        tenant_id: str,
        conversation_id: str,
        response_text: str,
        customer_message: str,
        budget: PipelineTimeoutBudget,
        knowledge_titles: list[str] | None = None,
    ) -> tuple[bool, str, Any]:
        """Validate the generated response via the Critic (fail-closed).

        Priority order:
        1. CriticPolicy (HTTP to AGNTCY container) — if configured
        2. Direct Azure OpenAI GPT-4o-mini validation — if OpenAI client available
        3. Fail-closed fallback — no unvalidated responses delivered

        The direct Azure OpenAI path (option 2) implements the same
        fail-closed semantics: if the model says "reject" or if the
        call fails, the response is blocked.
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

        # Option 1: Use CriticPolicy if configured (HTTP to AGNTCY containers)
        if self._critic:
            return await self._critic.require_critic_approval(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                response_text=response_text,
                customer_message=customer_message,
            )

        # Option 2: Direct Azure OpenAI validation (WI #207)
        # Always fall through to direct validation when CriticPolicy (Option 1)
        # is unavailable, regardless of USE_AGENT_CONTAINERS setting.
        if self._openai_client:
            return await self._validate_with_critic_direct(
                tenant_id, conversation_id, response_text,
                customer_message, budget,
                knowledge_titles=knowledge_titles,
            )

        # Option 3: Fail-closed — no Critic available
        fallback_result = CriticResult(
            approved=False,
            verdict=None,
            block_reason=CriticBlockReason.UNAVAILABLE,
            flags=[],
            modified_response=None,
            latency_ms=0.0,
            critic_instance="none",
            request_id=f"critic-{conversation_id}-{int(time.time() * 1000)}",
        )
        return False, SAFE_FALLBACK_MESSAGE, fallback_result

    async def _validate_with_critic_direct(
        self,
        tenant_id: str,
        conversation_id: str,
        response_text: str,
        customer_message: str,
        budget: PipelineTimeoutBudget,
        knowledge_titles: list[str] | None = None,
    ) -> tuple[bool, str, Any]:
        """Validate response via in-process CriticSupervisorAgent (A2A).

        Delegates to the extracted agent module which encapsulates the
        fail-closed Critic validation using Azure OpenAI GPT-4o-mini.

        The agent returns a dict; this method adapts it to the
        (approved, safe_text, CriticResult) tuple expected by the caller.
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

        cr_result = await self._cr_agent.process(
            {
                "response_text": response_text,
                "customer_message": customer_message,
                "knowledge_titles": knowledge_titles or [],
                "conversation_id": conversation_id,
            },
            {},
        )

        approved = cr_result.get("approved", False)
        safe_text = cr_result.get("safe_text", SAFE_FALLBACK_MESSAGE)

        # Map agent dict to CriticResult dataclass for pipeline compatibility
        verdict_str = cr_result.get("verdict", "unavailable")
        try:
            verdict = CriticVerdict(verdict_str)
        except ValueError:
            verdict = None

        block_reason_str = cr_result.get("block_reason")
        block_reason = None
        if block_reason_str:
            try:
                block_reason = CriticBlockReason(block_reason_str)
            except ValueError:
                block_reason = CriticBlockReason.ERROR

        result = CriticResult(
            approved=approved,
            verdict=verdict,
            block_reason=block_reason,
            flags=cr_result.get("flags", []),
            modified_response=cr_result.get("modified_response"),
            latency_ms=cr_result.get("latency_ms", 0.0),
            critic_instance="in-process-agent",
            request_id=cr_result.get("request_id", f"critic-{conversation_id}"),
        )

        return approved, safe_text, result

    # -------------------------------------------------------------------
    # Escalation handling
    # -------------------------------------------------------------------

    async def _handle_escalation(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Handle escalation: call Escalation agent, update session."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        yield stage_event("escalation-handler", "started")

        urgency = "medium"
        context_summary = ""

        try:
            esc_result = await budget.execute_with_budget(
                "escalation-handler",
                self._call_escalation_handler(customer_message, system_prompt),
            )

            reason = esc_result.get("reason", "Customer requested human agent")
            urgency = esc_result.get("urgency", "medium")
            context_summary = esc_result.get("context_summary", "")
            category = esc_result.get("category", "general_inquiry")
            trace.add_stage(
                "escalation-handler",
                model=esc_result.get("model", "gpt-4o-mini"),
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
            )

            yield stage_event("escalation-handler", "completed")

        except (PipelineTimeoutError, Exception) as exc:
            logger.warning(
                "Escalation agent failed: conv=%s error=%s — proceeding with default",
                conversation_id, exc,
            )
            reason = "Customer requested human agent"
            category = "general_inquiry"

        # Auto-assign to best-fit team member
        assigned_agent_id: str | None = None
        try:
            assigned_agent_id = await self._session.find_best_agent_for_category(
                tenant_id, category,
            )
        except Exception as exc:
            logger.warning("Auto-assign failed: %s — proceeding without assignment", exc)

        # Escalate the conversation in the session
        await self._session.escalate_conversation(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            escalation_reason=reason,
            escalation_category=category,
            assigned_to=assigned_agent_id,
        )

        # Resolve escalation notification recipients:
        #   1. Assigned agent's email (extracted from doc ID {tenant}:{email})
        #   2. Fallback: superadmin's email
        recipient_emails: list[str] = []
        if assigned_agent_id and ":" in assigned_agent_id:
            agent_email = assigned_agent_id.split(":", 1)[1]
            if agent_email:
                recipient_emails = [agent_email]

        if not recipient_emails:
            try:
                superadmin_email = await self._session.find_superadmin_email(tenant_id)
                if superadmin_email:
                    recipient_emails = [superadmin_email]
            except Exception:
                logger.debug("Superadmin lookup failed — escalation alert will use tenant notification email")

        # Fire-and-forget: notify escalation recipient
        try:
            from src.multi_tenant.alert_delivery import send_escalation_alert

            logger.info(
                "Firing escalation alert: tenant=%s conversation=%s reason=%s urgency=%s category=%s assigned=%s recipients=%s",
                tenant_id, conversation_id, reason[:80], urgency,
                category, assigned_agent_id or "unassigned",
                recipient_emails or ["tenant-default"],
            )
            asyncio.ensure_future(
                send_escalation_alert(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    reason=reason,
                    urgency=urgency,
                    context_summary=context_summary,
                    escalation_category=category,
                    assigned_to=assigned_agent_id,
                    recipient_emails=recipient_emails or None,
                )
            )
        except Exception:
            logger.debug("Escalation alert skipped (alert service not configured)")

        # Yield escalation system message as a token event
        escalation_msg = (
            "I'm connecting you with a member of our support team. "
            "A human agent will be with you shortly."
        )
        yield token_event(escalation_msg, 1)
        yield validated_event(conversation_id, "escalation")
        yield done_event(conversation_id, 0)

    def _transport_available(self) -> bool:
        """Check if AGNTCY transport is available (delegate to dispatch mixin)."""
        try:
            from src.multi_tenant.agntcy_sdk_integration import _transport
            return _transport is not None
        except Exception:
            return False

    async def _call_via_transport(
        self,
        agent_topic: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Route via SLIM/NATS transport (SPEC-1536)."""
        from src.multi_tenant.agntcy_sdk_integration import create_a2a_client

        client = create_a2a_client(agent_topic)
        response = await client.send(payload, headers={
            "X-Tenant-Id": getattr(self, "_current_tenant_id", ""),
            "X-Conversation-Id": getattr(self, "_current_conversation_id", ""),
            "X-Trace-Id": getattr(self, "_current_trace_id", ""),
        })
        return response if isinstance(response, dict) else {"result": response}

    async def _call_escalation_handler(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Route escalation via transport → HTTP → in-process (SPEC-1536)."""
        if self._transport_available():
            try:
                return await self._call_via_transport(
                    "escalation-handler",
                    {"message": message, "system_prompt": system_prompt},
                )
            except Exception as exc:
                logger.warning("Transport ESC call failed, falling back: %s", exc)
        if USE_AGENT_CONTAINERS:
            try:
                return await self._call_escalation_handler_http(message, system_prompt)
            except Exception as exc:
                logger.warning("HTTP ESC call failed, falling back to in-process: %s", exc)
        return await self._call_escalation_handler_direct(message, system_prompt)

    async def _call_escalation_handler_direct(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Evaluate escalation via in-process EscalationHandlerAgent (A2A).

        Delegates to the extracted agent module which encapsulates the
        Azure OpenAI GPT-4o-mini call for escalation analysis.
        """
        return await self._esc_agent.process(
            {"message": message, "system_prompt": system_prompt},
            {},
        )

    async def _call_escalation_handler_http(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Escalation Handler agent via HTTP (AGNTCY container)."""
        url = self._agent_urls.get("escalation-handler", "")
        client = await self._get_http_client()

        response = await client.post(
            f"{url.rstrip('/')}{AGENT_ESCALATE_PATH}",
            json={
                "message": message,
                "system_prompt": system_prompt,
            },
        )
        response.raise_for_status()
        return response.json()
