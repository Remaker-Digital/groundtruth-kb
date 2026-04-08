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
    _critic, _openai_client, _session, _agent_urls,
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

        ADR-001/ADR-002/DCL-002: No in-process fallback in canonical path.
        Routes via CriticPolicy (transport/HTTP to container) or fail-closed.

        Priority order:
        1. CriticPolicy (transport/HTTP to AGNTCY container) — if configured
        2. Fail-closed fallback — no unvalidated responses delivered

        Phase 2A: Removed in-process _validate_with_critic_direct() path.
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult

        # Option 1: Use CriticPolicy if configured (transport/HTTP to AGNTCY containers)
        if self._critic:
            return await self._critic.require_critic_approval(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                response_text=response_text,
                customer_message=customer_message,
            )

        # Option 2: Fail-closed — Critic container unavailable
        logger.warning(
            "Critic unavailable for conv=%s — fail-closed safe response. "
            "ADR-001/DCL-002: no in-process fallback.",
            conversation_id,
        )
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

    # -------------------------------------------------------------------
    # Escalation handling
    # -------------------------------------------------------------------

    async def _run_escalation_side_effects(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> dict[str, Any]:
        """Execute escalation side-effects without yielding SSE events.

        WI-3030 Phase 2: Extracted from _handle_escalation so the orchestrator
        can run the normal KR→RG→Critic pipeline first, then fire escalation
        side-effects and yield the notice after the AI answer.

        Returns a dict with:
            email_required (bool): True if customer email is missing
            email_prompt (str): Message asking for email (when email_required)
            escalation_msg (str): Primary escalation notice
            continuation_msg (str): Continuation offer
            email_bridge_sent (bool): Whether email dispatch succeeded
            reason (str): Escalation reason from agent
            category (str): Escalation category
            urgency (str): Escalation urgency
        """
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        reason = "Customer requested human agent"
        urgency = "medium"
        context_summary = ""
        category = "general_inquiry"

        try:
            esc_result = await budget.execute_with_budget(
                "escalation-handler",
                self._call_escalation_handler(customer_message, system_prompt),
            )
            reason = esc_result.get("reason", reason)
            urgency = esc_result.get("urgency", urgency)
            context_summary = esc_result.get("context_summary", "")
            category = esc_result.get("category", category)

            trace.set_escalation(escalated=True, reason=reason)
            trace.add_stage(
                "escalation-handler",
                model=esc_result.get("model", "gpt-4o-mini"),
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
            )
        except (PipelineTimeoutError, Exception) as exc:
            logger.warning(
                "Escalation agent failed: conv=%s error=%s — proceeding with default",
                conversation_id, exc,
            )
            trace.set_escalation(escalated=True, reason=reason)

        # Check for customer email BEFORE escalating.
        customer_email: str | None = None
        conv_doc: dict[str, Any] | None = None
        try:
            conv_doc = await self._session._get_conversation(tenant_id, conversation_id)
            customer_email = conv_doc.get("identity_email")
        except Exception:
            logger.debug("Could not read conversation for identity_email")

        if not customer_email:
            return {
                "email_required": True,
                "email_prompt": (
                    "I'd like to connect you with a human representative who can "
                    "help with this. Could you share your email address so they "
                    "can follow up with you directly?"
                ),
                "escalation_msg": "",
                "continuation_msg": "",
                "email_bridge_sent": False,
                "reason": reason,
                "category": category,
                "urgency": urgency,
            }

        # Auto-assign to best-fit team member
        assigned_agent_id: str | None = None
        try:
            assigned_agent_id = await self._session.find_best_agent_for_category(
                tenant_id, category,
            )
        except Exception as exc:
            logger.warning("Auto-assign failed: %s — proceeding without assignment", exc)

        # Resolve escalation notification recipients
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
                logger.debug("Superadmin lookup failed")

        # Escalate the conversation
        await self._session.escalate_conversation(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            escalation_reason=reason,
            escalation_category=category,
            assigned_to=assigned_agent_id,
        )

        # Async email-bridge dispatch
        email_bridge_sent = False
        try:
            from src.chat.escalation_email import send_escalation_emails
            from src.multi_tenant.repository import TenantRepository

            store_name = "Support"
            try:
                tenant_repo = TenantRepository()
                tenant_doc = await tenant_repo.read(tenant_id)
                store_name = tenant_doc.get("store_name") or tenant_doc.get("name") or "Support"
            except Exception:
                pass

            messages = conv_doc.get("messages", []) if conv_doc else []
            agent_email = recipient_emails[0] if recipient_emails else ""

            if agent_email and customer_email:
                logger.info(
                    "Sending email-bridge escalation: tenant=%s conv=%s customer=%s agent=%s",
                    tenant_id, conversation_id[:8], customer_email, agent_email,
                )
                results = await send_escalation_emails(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    customer_email=customer_email,
                    agent_email=agent_email,
                    messages=messages,
                    store_name=store_name,
                    reason=reason,
                    category=category,
                    urgency=urgency,
                )
                if results.get("agent") not in ("failed", "skipped"):
                    email_bridge_sent = True
            else:
                logger.warning(
                    "Email-bridge incomplete: customer=%s agent=%s — alert only",
                    customer_email or "missing", agent_email or "missing",
                )
        except Exception:
            logger.warning("Email-bridge dispatch failed", exc_info=True)

        # Legacy alert (fire-and-forget)
        try:
            from src.multi_tenant.alert_delivery import send_escalation_alert
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
            logger.debug("Legacy escalation alert skipped")

        # Set delivery-state flag
        try:
            from datetime import datetime, timezone as tz
            await self._session._repo.patch_conversation(
                tenant_id, conversation_id,
                {
                    "escalation_sent": email_bridge_sent,
                    "escalated_via_email_at": (
                        datetime.now(tz.utc).isoformat() if email_bridge_sent else None
                    ),
                },
            )
        except Exception:
            logger.debug("Failed to set escalation_sent flag", exc_info=True)

        return {
            "email_required": False,
            "email_prompt": "",
            "escalation_msg": (
                "I've also escalated your request to a human representative "
                "who will follow up via email. Please check your spam folder "
                "if you don't hear from us soon."
            ),
            "continuation_msg": (
                "Is there anything else I can help you with in the meantime?"
            ),
            "email_bridge_sent": email_bridge_sent,
            "reason": reason,
            "category": category,
            "urgency": urgency,
        }

    async def _handle_escalation(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Handle escalation: call Escalation agent, update session.

        Delegates to _run_escalation_side_effects() and yields SSE events.
        Retained for backwards compatibility with direct-escalation callers.
        """
        yield stage_event("escalation-handler", "started")

        result = await self._run_escalation_side_effects(
            tenant_id, conversation_id, customer_message,
            system_prompt, budget, trace,
        )

        # Emit stage completion (budget was updated by side-effects)
        esc_stages = [s for s in budget.stages if s.stage == "escalation-handler"]
        yield stage_event(
            "escalation-handler", "completed",
            latency_ms=int(esc_stages[-1].elapsed_ms) if esc_stages else None,
        )

        if result["email_required"]:
            yield token_event(result["email_prompt"], 1)
            yield validated_event(conversation_id, "escalation_email_required")
            yield done_event(conversation_id, 0)
            return

        yield token_event(result["escalation_msg"], 1)
        yield token_event(result["continuation_msg"], 2)
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
        """Route escalation via transport → HTTP → default context (ADR-001/DCL-002).

        No in-process fallback (Phase 2A). When transport+HTTP both fail,
        returns a default escalation context instead of 503 — the pipeline
        still hands off to a human agent with basic context.
        """
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
                logger.warning("HTTP ESC call failed: %s", exc)
        # ADR-001/DCL-002: No in-process fallback. Return default escalation context.
        logger.warning(
            "Escalation handler unavailable — all tiers exhausted. "
            "Returning default escalation context. ADR-001/DCL-002: no in-process fallback."
        )
        return {
            "reason": "Customer requested human agent",
            "urgency": "medium",
            "context_summary": "Escalation handler unavailable — transport exhausted",
            "category": "general_inquiry",
            "model": "default",
        }

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
