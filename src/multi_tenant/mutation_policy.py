"""MCP mutation safety — policy models and evaluation logic.

Defines the mutation safety framework for gating MCP tool invocations
that modify external state (e.g., cancel subscription, refund payment).

Architecture:
    1. ``MutationPolicy`` — per-tenant configuration (allow_mutations,
       require_critic_approval, require_customer_confirmation, allowed_operations)
    2. ``MutationRequest`` — represents a proposed mutating tool call
    3. ``MutationResult`` — outcome of policy evaluation or execution
    4. ``evaluate_request()`` — synchronous policy gate

**Cycle 5: Mutations are DISABLED.** ``allow_mutations=False`` for all tenants.
The models and evaluation logic exist and are tested, but the pipeline never
activates mutation execution. This will be enabled in a future cycle when
the Critic-gated confirmation UX is implemented.

AGNTCY Phase 3B assertion targets: 3.7 (mutation safety), 3.8 (idempotency).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Idempotency key format: mut-{tenant_id}-{conversation_id}-{tool}-{hash(args)[:8]}
IDEMPOTENCY_KEY_PREFIX = "mut"


# ---------------------------------------------------------------------------
# Policy model
# ---------------------------------------------------------------------------


@dataclass
class MutationPolicy:
    """Per-tenant mutation policy configuration.

    Controls whether mutating MCP tools can be executed, and what
    safety gates must be passed before execution.

    Attributes:
        allow_mutations: Global kill-switch. ``False`` = block ALL mutations.
            Cycle 5 default: ``False`` (mutations disabled).
        require_critic_approval: Whether the Critic Supervisor must approve
            the mutation before execution. Default: ``True``.
        require_customer_confirmation: Whether the customer must explicitly
            confirm the action in the chat widget. Default: ``True``.
        allowed_operations: Explicit allowlist of permitted tool names.
            Empty list = allow all (subject to other gates).
        max_mutations_per_conversation: Maximum mutations allowed in a single
            conversation. ``0`` = unlimited. Default: ``3``.
    """

    allow_mutations: bool = False
    require_critic_approval: bool = True
    require_customer_confirmation: bool = True
    allowed_operations: list[str] = field(default_factory=list)
    max_mutations_per_conversation: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for Cosmos DB storage."""
        return {
            "allow_mutations": self.allow_mutations,
            "require_critic_approval": self.require_critic_approval,
            "require_customer_confirmation": self.require_customer_confirmation,
            "allowed_operations": list(self.allowed_operations),
            "max_mutations_per_conversation": self.max_mutations_per_conversation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MutationPolicy:
        """Deserialize from Cosmos DB dict."""
        return cls(
            allow_mutations=bool(data.get("allow_mutations", False)),
            require_critic_approval=bool(
                data.get("require_critic_approval", True)
            ),
            require_customer_confirmation=bool(
                data.get("require_customer_confirmation", True)
            ),
            allowed_operations=list(data.get("allowed_operations", [])),
            max_mutations_per_conversation=int(
                data.get("max_mutations_per_conversation", 3)
            ),
        )


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------


@dataclass
class MutationRequest:
    """A proposed mutating tool invocation.

    Created by the KR agent or Response Generator when a tool call
    is classified as ``"mutate"`` and the tenant's policy allows mutations.

    Attributes:
        tool_name: The MCP tool name (e.g. ``"cancel_subscription"``).
        arguments: Tool arguments dict (PII-scrubbed).
        proposed_summary: Human-readable description of the action
            (e.g. ``"Cancel subscription for customer"``).
        conversation_id: The conversation this request belongs to.
        tenant_id: The tenant identifier.
        server_name: The MCP server that owns the tool.
    """

    tool_name: str
    arguments: dict[str, Any]
    proposed_summary: str
    conversation_id: str
    tenant_id: str
    server_name: str = ""


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


@dataclass
class MutationResult:
    """Outcome of a mutation policy evaluation or execution attempt.

    Attributes:
        approved: Whether the policy evaluation approved the mutation.
        executed: Whether the tool was actually invoked.
        idempotency_key: Unique key for replay prevention (set if approved).
        critic_verdict: Critic evaluation result (``"approved"``/
            ``"modified"``/``"rejected"``/``None``).
        customer_confirmed: Whether the customer confirmed the action.
        error_reason: Reason for denial (if ``approved=False``).
        tool_result: Raw MCP tool result (if ``executed=True``).
    """

    approved: bool
    executed: bool = False
    idempotency_key: str | None = None
    critic_verdict: str | None = None
    customer_confirmed: bool = False
    error_reason: str | None = None
    tool_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for logging/storage."""
        return {
            "approved": self.approved,
            "executed": self.executed,
            "idempotency_key": self.idempotency_key,
            "critic_verdict": self.critic_verdict,
            "customer_confirmed": self.customer_confirmed,
            "error_reason": self.error_reason,
            "has_tool_result": self.tool_result is not None,
        }


# ---------------------------------------------------------------------------
# Idempotency key generation
# ---------------------------------------------------------------------------


def generate_idempotency_key(request: MutationRequest) -> str:
    """Generate a deterministic idempotency key for a mutation request.

    Format: ``mut-{tenant_id}-{conversation_id}-{tool_name}-{hash(args)[:8]}``

    The hash component ensures that different arguments to the same tool
    in the same conversation produce different keys.

    Args:
        request: The mutation request.

    Returns:
        Idempotency key string.
    """
    # Hash arguments deterministically
    args_str = str(sorted(request.arguments.items())) if request.arguments else ""
    args_hash = hashlib.sha256(args_str.encode("utf-8")).hexdigest()[:8]

    return (
        f"{IDEMPOTENCY_KEY_PREFIX}-{request.tenant_id}"
        f"-{request.conversation_id}-{request.tool_name}-{args_hash}"
    )


# ---------------------------------------------------------------------------
# Policy evaluation
# ---------------------------------------------------------------------------


def evaluate_request(
    request: MutationRequest,
    policy: MutationPolicy,
    mutations_in_conversation: int = 0,
) -> MutationResult:
    """Evaluate a mutation request against the tenant's policy.

    This is the synchronous policy gate — it checks whether the mutation
    is allowed in principle. If approved, the caller must still run the
    async execution pipeline (Critic → customer confirmation → execute).

    Args:
        request: The proposed mutation.
        policy: The tenant's mutation policy.
        mutations_in_conversation: Number of mutations already executed
            in this conversation (for rate limiting).

    Returns:
        ``MutationResult`` with ``approved=True`` if the mutation passes
        all policy gates, or ``approved=False`` with ``error_reason``.
    """
    # Gate 1: Global kill-switch
    if not policy.allow_mutations:
        logger.debug(
            "Mutation blocked: mutations_disabled tenant=%s tool=%s",
            request.tenant_id, request.tool_name,
        )
        return MutationResult(
            approved=False,
            error_reason="mutations_disabled",
        )

    # Gate 2: Allowed operations allowlist
    if policy.allowed_operations and request.tool_name not in policy.allowed_operations:
        logger.debug(
            "Mutation blocked: not_in_allowed_operations tenant=%s tool=%s",
            request.tenant_id, request.tool_name,
        )
        return MutationResult(
            approved=False,
            error_reason="not_in_allowed_operations",
        )

    # Gate 3: Per-conversation rate limit
    if (
        policy.max_mutations_per_conversation > 0
        and mutations_in_conversation >= policy.max_mutations_per_conversation
    ):
        logger.debug(
            "Mutation blocked: conversation_limit_exceeded tenant=%s "
            "tool=%s count=%d max=%d",
            request.tenant_id, request.tool_name,
            mutations_in_conversation, policy.max_mutations_per_conversation,
        )
        return MutationResult(
            approved=False,
            error_reason="conversation_limit_exceeded",
        )

    # All policy gates passed — approved (pending Critic + customer confirmation)
    idempotency_key = generate_idempotency_key(request)

    logger.info(
        "Mutation approved by policy: tenant=%s tool=%s key=%s "
        "requires_critic=%s requires_confirm=%s",
        request.tenant_id, request.tool_name, idempotency_key,
        policy.require_critic_approval, policy.require_customer_confirmation,
    )

    return MutationResult(
        approved=True,
        idempotency_key=idempotency_key,
    )
