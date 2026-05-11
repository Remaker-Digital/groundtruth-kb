# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Action Executor with HITL Gating — routes AI requests to adapters (SPEC-1769).

The ActionExecutor is the single dispatch point for AI-initiated actions against
external integrations.  Every action flows through HITL (Human-In-The-Loop) gating
before execution: high-risk actions (refunds, status changes) require human approval,
while low-risk reads can execute immediately.

Audit logging captures every action attempt, approval, and result.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.integrations.models import IntegrationError, RateLimitError
from src.integrations.registry import IntegrationRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Action types & HITL policy
# ---------------------------------------------------------------------------


class ActionType(str, Enum):
    """Standardized action types routable through the executor."""

    # Read actions (typically auto-approved)
    TICKET_LOOKUP = "ticket_lookup"
    ORDER_LOOKUP = "order_lookup"
    CUSTOMER_LOOKUP = "customer_lookup"
    ARTICLE_SEARCH = "article_search"
    PRODUCT_SEARCH = "product_search"

    # Write actions (HITL-gated by default)
    REPLY_SEND = "reply_send"
    REPLY_DRAFT = "reply_draft"
    NOTE_ADD = "note_add"
    STATUS_UPDATE = "status_update"
    TAG_ADD = "tag_add"
    TICKET_ASSIGN = "ticket_assign"
    TICKET_CREATE = "ticket_create"
    MESSAGE_SEND = "message_send"

    # High-risk actions (always HITL)
    REFUND_PROCESS = "refund_process"


class HITLPolicy(str, Enum):
    """Human-in-the-loop requirement level."""

    ALWAYS = "always"        # Always requires human approval
    DEFAULT = "default"      # HITL by default, can be overridden per-tenant
    OPTIONAL = "optional"    # HITL off by default, can be enabled per-tenant
    NEVER = "never"          # Auto-approved (read-only actions)


class ActionStatus(str, Enum):
    """Lifecycle status of an action."""

    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


# Default HITL policy per action type
_DEFAULT_HITL_POLICY: dict[ActionType, HITLPolicy] = {
    # Reads — auto-approved
    ActionType.TICKET_LOOKUP: HITLPolicy.NEVER,
    ActionType.ORDER_LOOKUP: HITLPolicy.NEVER,
    ActionType.CUSTOMER_LOOKUP: HITLPolicy.NEVER,
    ActionType.ARTICLE_SEARCH: HITLPolicy.NEVER,
    ActionType.PRODUCT_SEARCH: HITLPolicy.NEVER,
    # Writes — HITL by default
    ActionType.REPLY_SEND: HITLPolicy.DEFAULT,
    ActionType.REPLY_DRAFT: HITLPolicy.DEFAULT,
    ActionType.NOTE_ADD: HITLPolicy.OPTIONAL,
    ActionType.STATUS_UPDATE: HITLPolicy.DEFAULT,
    ActionType.TAG_ADD: HITLPolicy.OPTIONAL,
    ActionType.TICKET_ASSIGN: HITLPolicy.OPTIONAL,
    ActionType.TICKET_CREATE: HITLPolicy.DEFAULT,
    ActionType.MESSAGE_SEND: HITLPolicy.DEFAULT,
    # High-risk — always HITL
    ActionType.REFUND_PROCESS: HITLPolicy.ALWAYS,
}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class AIAction(BaseModel):
    """An action requested by the AI agent against an integration."""

    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    integration_id: str
    action_type: ActionType
    params: dict[str, Any] = Field(default_factory=dict)
    conversation_id: str = ""
    requested_by: str = "ai_agent"
    hitl_required: bool | None = None  # None = use policy default
    priority: str = "normal"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActionResult(BaseModel):
    """Result of executing an action."""

    action_id: str
    status: ActionStatus
    result: dict[str, Any] = Field(default_factory=dict)
    error_message: str = ""
    approved_by: str = ""
    executed_at: datetime | None = None
    duration_ms: float = 0.0


class ActionAuditEntry(BaseModel):
    """Audit log entry for action lifecycle events."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str
    tenant_id: str
    integration_id: str
    action_type: str
    event: str  # requested, approved, rejected, executed, failed
    actor: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Action Executor
# ---------------------------------------------------------------------------


class ActionExecutor:
    """Routes AI-requested actions to integration adapters with HITL gating.

    The executor:
    1. Receives an AIAction from the orchestrator
    2. Evaluates HITL policy to determine if approval is needed
    3. If approval required: parks action as PENDING_APPROVAL
    4. If auto-approved: executes immediately via the adapter
    5. Logs every lifecycle event to the audit log
    """

    def __init__(
        self,
        registry: IntegrationRegistry | None = None,
        *,
        tenant_hitl_overrides: dict[str, dict[str, HITLPolicy]] | None = None,
        rate_limits: dict[str, int] | None = None,
    ) -> None:
        self._registry = registry or IntegrationRegistry.get_instance()
        # tenant_id -> {action_type_value -> HITLPolicy}
        self._tenant_overrides: dict[str, dict[str, HITLPolicy]] = (
            tenant_hitl_overrides or {}
        )
        # integration_id -> max RPM
        self._rate_limits: dict[str, int] = rate_limits or {}
        # Pending actions awaiting approval: action_id -> AIAction
        self._pending: dict[str, AIAction] = {}
        # Audit log (in-memory; production would write to Cosmos integration_events)
        self._audit_log: list[ActionAuditEntry] = []

    # -- HITL evaluation ----------------------------------------------------

    def get_hitl_policy(
        self, tenant_id: str, action_type: ActionType
    ) -> HITLPolicy:
        """Determine effective HITL policy for a tenant + action type."""
        # Check tenant-level override first
        overrides = self._tenant_overrides.get(tenant_id, {})
        if action_type.value in overrides:
            override = overrides[action_type.value]
            # ALWAYS cannot be overridden to a lower level
            default = _DEFAULT_HITL_POLICY.get(action_type, HITLPolicy.DEFAULT)
            if default == HITLPolicy.ALWAYS:
                return HITLPolicy.ALWAYS
            return override

        return _DEFAULT_HITL_POLICY.get(action_type, HITLPolicy.DEFAULT)

    def requires_approval(self, action: AIAction) -> bool:
        """Check if an action requires human approval before execution."""
        # Explicit override on the action itself
        if action.hitl_required is True:
            return True
        if action.hitl_required is False:
            # Cannot bypass ALWAYS policy
            policy = self.get_hitl_policy(action.tenant_id, action.action_type)
            if policy == HITLPolicy.ALWAYS:
                return True
            return False

        policy = self.get_hitl_policy(action.tenant_id, action.action_type)
        return policy in (HITLPolicy.ALWAYS, HITLPolicy.DEFAULT)

    # -- Execution ----------------------------------------------------------

    async def submit(self, action: AIAction) -> ActionResult:
        """Submit an action for execution.

        If HITL approval is required, parks the action and returns
        PENDING_APPROVAL status.  Otherwise, executes immediately.
        """
        self._log_audit(action, "requested")

        if self.requires_approval(action):
            self._pending[action.action_id] = action
            self._log_audit(action, "pending_approval")
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.PENDING_APPROVAL,
            )

        return await self._execute(action)

    async def approve(
        self, action_id: str, approved_by: str = "human_agent"
    ) -> ActionResult:
        """Approve a pending action and execute it."""
        action = self._pending.pop(action_id, None)
        if action is None:
            return ActionResult(
                action_id=action_id,
                status=ActionStatus.FAILED,
                error_message=f"Action {action_id} not found in pending queue",
            )

        self._log_audit(action, "approved", actor=approved_by)
        result = await self._execute(action)
        result.approved_by = approved_by
        return result

    async def reject(
        self, action_id: str, rejected_by: str = "human_agent", reason: str = ""
    ) -> ActionResult:
        """Reject a pending action."""
        action = self._pending.pop(action_id, None)
        if action is None:
            return ActionResult(
                action_id=action_id,
                status=ActionStatus.FAILED,
                error_message=f"Action {action_id} not found in pending queue",
            )

        self._log_audit(
            action, "rejected", actor=rejected_by, details={"reason": reason}
        )
        return ActionResult(
            action_id=action.action_id,
            status=ActionStatus.REJECTED,
            error_message=reason or "Rejected by human agent",
        )

    def get_pending(self, tenant_id: str | None = None) -> list[AIAction]:
        """List pending actions, optionally filtered by tenant."""
        actions = list(self._pending.values())
        if tenant_id:
            actions = [a for a in actions if a.tenant_id == tenant_id]
        return sorted(actions, key=lambda a: a.created_at)

    # -- Internal execution -------------------------------------------------

    async def _execute(self, action: AIAction) -> ActionResult:
        """Execute an action against its integration adapter."""
        start = datetime.now(UTC)

        try:
            adapter = self._registry.get_adapter(
                action.tenant_id, action.integration_id
            )
        except IntegrationError as exc:
            self._log_audit(action, "failed", details={"error": str(exc)})
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                error_message=str(exc),
            )

        try:
            result_data = await self._dispatch(adapter, action)
            elapsed = (datetime.now(UTC) - start).total_seconds() * 1000

            self._log_audit(action, "executed", details={"duration_ms": elapsed})

            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.COMPLETED,
                result=result_data,
                executed_at=datetime.now(UTC),
                duration_ms=elapsed,
            )

        except RateLimitError as exc:
            self._log_audit(
                action, "failed",
                details={"error": str(exc), "retry_after": exc.retry_after_seconds},
            )
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                error_message=f"Rate limited: {exc}",
            )
        except IntegrationError as exc:
            self._log_audit(action, "failed", details={"error": str(exc)})
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                error_message=str(exc),
            )
        except Exception as exc:
            self._log_audit(action, "failed", details={"error": str(exc)})
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                error_message=f"Unexpected error: {exc}",
            )

    async def _dispatch(
        self, adapter: Any, action: AIAction
    ) -> dict[str, Any]:
        """Route an action to the appropriate adapter method.

        Returns the result as a dict for serialization.
        """
        at = action.action_type
        p = action.params
        tid = action.tenant_id

        # -- Read actions --
        if at == ActionType.TICKET_LOOKUP:
            ticket = await adapter.get_ticket(tid, p["ticket_id"])
            return ticket.model_dump() if ticket else {"found": False}

        if at == ActionType.ORDER_LOOKUP:
            order = await adapter.lookup_order(tid, p["order_id"])
            return order.model_dump() if order else {"found": False}

        if at == ActionType.CUSTOMER_LOOKUP:
            contact = await adapter.lookup_customer(
                tid, email=p.get("email"), customer_id=p.get("customer_id")
            )
            return contact.model_dump() if contact else {"found": False}

        if at == ActionType.ARTICLE_SEARCH:
            articles = await adapter.search_articles(
                tid, p["query"], limit=p.get("limit", 25)
            )
            return {"articles": [a.model_dump() for a in articles]}

        if at == ActionType.PRODUCT_SEARCH:
            products = await adapter.search_products(
                tid, p["query"], limit=p.get("limit", 25)
            )
            return {"products": products}

        # -- Write actions --
        if at == ActionType.REPLY_SEND:
            msg = await adapter.add_reply(
                tid, p["ticket_id"], p["body"],
                html_body=p.get("html_body"),
                internal=False,
            )
            return msg.model_dump()

        if at == ActionType.REPLY_DRAFT:
            # Drafts are stored as internal notes
            msg = await adapter.add_reply(
                tid, p["ticket_id"], p["body"],
                html_body=p.get("html_body"),
                internal=True,
            )
            return msg.model_dump()

        if at == ActionType.NOTE_ADD:
            msg = await adapter.add_reply(
                tid, p["ticket_id"], p["body"], internal=True
            )
            return msg.model_dump()

        if at == ActionType.STATUS_UPDATE:
            ticket = await adapter.update_status(tid, p["ticket_id"], p["status"])
            return ticket.model_dump()

        if at == ActionType.TAG_ADD:
            ticket = await adapter.add_tags(tid, p["ticket_id"], p["tags"])
            return ticket.model_dump()

        if at == ActionType.TICKET_ASSIGN:
            ticket = await adapter.assign_ticket(
                tid, p["ticket_id"], p["assignee_id"]
            )
            return ticket.model_dump()

        if at == ActionType.TICKET_CREATE:
            ticket = await adapter.create_ticket(
                tid, p["subject"], p["body"],
                requester_email=p.get("requester_email"),
                priority=p.get("priority", "normal"),
                tags=p.get("tags"),
            )
            return ticket.model_dump()

        if at == ActionType.MESSAGE_SEND:
            msg = await adapter.send_message(
                tid, p["channel_id"], p["body"],
                thread_id=p.get("thread_id"),
            )
            return msg.model_dump()

        # -- High-risk actions --
        if at == ActionType.REFUND_PROCESS:
            result = await adapter.process_refund(
                tid, p["order_id"],
                amount=p.get("amount"),
                reason=p.get("reason", ""),
            )
            return result

        raise IntegrationError(
            f"Unsupported action type: {at.value}",
            integration_id=action.integration_id,
        )

    # -- Audit logging ------------------------------------------------------

    def _log_audit(
        self,
        action: AIAction,
        event: str,
        *,
        actor: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record an audit entry for an action lifecycle event."""
        entry = ActionAuditEntry(
            action_id=action.action_id,
            tenant_id=action.tenant_id,
            integration_id=action.integration_id,
            action_type=action.action_type.value,
            event=event,
            actor=actor or action.requested_by,
            details=details or {},
        )
        self._audit_log.append(entry)
        logger.info(
            "Action audit: action=%s event=%s integration=%s tenant=%s",
            action.action_id[:8],
            event,
            action.integration_id,
            action.tenant_id,
        )

    def get_audit_log(
        self,
        *,
        tenant_id: str | None = None,
        action_id: str | None = None,
        limit: int = 100,
    ) -> list[ActionAuditEntry]:
        """Retrieve audit entries, optionally filtered."""
        entries = self._audit_log
        if tenant_id:
            entries = [e for e in entries if e.tenant_id == tenant_id]
        if action_id:
            entries = [e for e in entries if e.action_id == action_id]
        return entries[-limit:]
