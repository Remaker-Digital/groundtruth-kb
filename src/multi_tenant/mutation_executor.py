"""MCP mutation executor — Critic-gated, idempotent mutation execution.

Orchestrates the full mutation execution pipeline:
1. Policy evaluation (synchronous gate)
2. Critic Supervisor validation (async, fail-closed)
3. Customer confirmation check (future: widget interaction)
4. Idempotency check (Cosmos DB replay prevention)
5. MCP tool execution
6. Mutation log persistence

**Cycle 5: This executor exists, is tested, but is NEVER activated.**
The ``MutationPolicy.allow_mutations`` is ``False`` for all tenants,
so ``evaluate_request()`` blocks at step 1 before any external calls.

Architecture:
    - Critic approval is fail-closed: if the Critic rejects or errors,
      the mutation is blocked.
    - Idempotency keys prevent replay attacks and accidental re-execution.
    - Mutation log in Cosmos DB provides audit trail (90-day TTL).
    - Escalation path: rejected mutations generate an escalation suggestion.

AGNTCY Phase 3B (Cycle 5) — mutation safety framework.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.mutation_policy import (
    MutationPolicy,
    MutationRequest,
    MutationResult,
    evaluate_request,
    generate_idempotency_key,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Cosmos collection name for mutation audit log
MUTATION_LOG_COLLECTION = "mutation_log"

# TTL for mutation log documents (90 days in seconds)
MUTATION_LOG_TTL_SECONDS = 90 * 24 * 60 * 60  # 7,776,000 seconds


# ---------------------------------------------------------------------------
# Mutation log document model
# ---------------------------------------------------------------------------


class MutationLogDocument:
    """Audit log entry for a mutation execution attempt.

    Stored in Cosmos DB ``mutation_log`` collection with partition key
    ``/tenant_id`` and 90-day TTL.

    Attributes:
        id: Idempotency key (also serves as Cosmos document ID).
        tenant_id: Partition key.
        conversation_id: The conversation where this mutation occurred.
        tool_name: MCP tool that was invoked.
        server_name: MCP server that owns the tool.
        arguments_hash: SHA-256 of PII-scrubbed arguments (not raw values).
        proposed_summary: Human-readable description of the action.
        critic_verdict: Critic evaluation result.
        customer_confirmed: Whether the customer confirmed.
        executed: Whether the tool was actually called.
        result_summary: Brief summary of the execution result.
        error_reason: Reason for denial if not executed.
        created_at: ISO 8601 timestamp.
        ttl: Cosmos DB TTL in seconds.
    """

    def __init__(
        self,
        idempotency_key: str,
        request: MutationRequest,
        result: MutationResult,
    ) -> None:
        self.id = idempotency_key
        self.tenant_id = request.tenant_id
        self.conversation_id = request.conversation_id
        self.tool_name = request.tool_name
        self.server_name = request.server_name
        self.arguments_hash = hashlib.sha256(
            str(sorted(request.arguments.items())).encode("utf-8")
        ).hexdigest() if request.arguments else ""
        self.proposed_summary = request.proposed_summary
        self.critic_verdict = result.critic_verdict
        self.customer_confirmed = result.customer_confirmed
        self.executed = result.executed
        self.result_summary = (
            str(result.tool_result)[:200] if result.tool_result else None
        )
        self.error_reason = result.error_reason
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.ttl = MUTATION_LOG_TTL_SECONDS

    def to_dict(self) -> dict[str, Any]:
        """Serialize for Cosmos DB upsert."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "conversation_id": self.conversation_id,
            "tool_name": self.tool_name,
            "server_name": self.server_name,
            "arguments_hash": self.arguments_hash,
            "proposed_summary": self.proposed_summary,
            "critic_verdict": self.critic_verdict,
            "customer_confirmed": self.customer_confirmed,
            "executed": self.executed,
            "result_summary": self.result_summary,
            "error_reason": self.error_reason,
            "created_at": self.created_at,
            "ttl": self.ttl,
        }


# ---------------------------------------------------------------------------
# MutationExecutor
# ---------------------------------------------------------------------------


class MutationExecutor:
    """Critic-gated, idempotent mutation executor.

    Orchestrates the full safety pipeline for mutating MCP tool calls.
    In Cycle 5, this executor is built and tested but never activated
    (``MutationPolicy.allow_mutations=False``).

    Args:
        mcp_client_factory: Async callable that creates an MCP client
            for a given ``McpServerConfig``.
        critic_agent: ``CriticSupervisorAgent`` instance for validation.
        credential_cache: ``McpCredentialCache`` for credential lookup.
        mutation_log_store: Optional Cosmos DB container client for
            persisting mutation audit logs. If ``None``, logging only.

    Usage::

        executor = MutationExecutor(
            mcp_client_factory=create_tenant_mcp_client,
            critic_agent=critic,
            credential_cache=cache,
        )

        result = await executor.execute(request, policy)
        # result.approved → was the mutation permitted?
        # result.executed → was the tool actually called?
    """

    def __init__(
        self,
        mcp_client_factory: Any = None,
        critic_agent: Any = None,
        credential_cache: Any = None,
        mutation_log_store: Any = None,
    ) -> None:
        self._mcp_client_factory = mcp_client_factory
        self._critic_agent = critic_agent
        self._credential_cache = credential_cache
        self._mutation_log_store = mutation_log_store
        # Metrics
        self._total_requests = 0
        self._total_blocked = 0
        self._total_executed = 0
        self._total_critic_rejections = 0

    async def execute(
        self,
        request: MutationRequest,
        policy: MutationPolicy,
        mutations_in_conversation: int = 0,
        customer_confirmed: bool = False,
    ) -> MutationResult:
        """Execute the full mutation safety pipeline.

        Pipeline stages:
        1. Policy evaluation (synchronous)
        2. Idempotency check (Cosmos lookup)
        3. Critic validation (async, fail-closed)
        4. Customer confirmation check
        5. MCP tool execution
        6. Mutation log persistence

        Args:
            request: The proposed mutation.
            policy: The tenant's mutation policy.
            mutations_in_conversation: Count of prior mutations in this
                conversation (for rate limiting).
            customer_confirmed: Whether the customer has confirmed this
                specific action.

        Returns:
            ``MutationResult`` with execution outcome.
        """
        self._total_requests += 1

        # Stage 1: Policy gate
        policy_result = evaluate_request(
            request, policy, mutations_in_conversation,
        )
        if not policy_result.approved:
            self._total_blocked += 1
            await self._log_mutation(request, policy_result)
            return policy_result

        idempotency_key = policy_result.idempotency_key or generate_idempotency_key(
            request,
        )

        # Stage 2: Idempotency check (prevent replay)
        existing = await self._check_idempotency(idempotency_key, request.tenant_id)
        if existing is not None:
            logger.info(
                "Mutation replay prevented: key=%s tenant=%s",
                idempotency_key, request.tenant_id,
            )
            return MutationResult(
                approved=False,
                error_reason="already_executed",
                idempotency_key=idempotency_key,
            )

        # Stage 3: Critic validation (fail-closed)
        if policy.require_critic_approval:
            critic_result = await self._validate_with_critic(request)
            if critic_result != "approved":
                self._total_critic_rejections += 1
                result = MutationResult(
                    approved=False,
                    critic_verdict=critic_result,
                    idempotency_key=idempotency_key,
                    error_reason=f"critic_{critic_result}",
                )
                await self._log_mutation(request, result)
                return result

        # Stage 4: Customer confirmation check
        if policy.require_customer_confirmation and not customer_confirmed:
            result = MutationResult(
                approved=True,  # Policy approved, but waiting for confirmation
                executed=False,
                idempotency_key=idempotency_key,
                critic_verdict="approved" if policy.require_critic_approval else None,
                error_reason="awaiting_customer_confirmation",
            )
            await self._log_mutation(request, result)
            return result

        # Stage 5: Execute MCP tool call
        try:
            tool_result = await self._execute_tool(request)
            self._total_executed += 1
            result = MutationResult(
                approved=True,
                executed=True,
                idempotency_key=idempotency_key,
                critic_verdict="approved" if policy.require_critic_approval else None,
                customer_confirmed=customer_confirmed,
                tool_result=tool_result,
            )
        except Exception as exc:
            logger.error(
                "Mutation execution failed: key=%s tool=%s error=%s",
                idempotency_key, request.tool_name, exc,
            )
            result = MutationResult(
                approved=True,
                executed=False,
                idempotency_key=idempotency_key,
                critic_verdict="approved" if policy.require_critic_approval else None,
                customer_confirmed=customer_confirmed,
                error_reason=f"execution_failed: {str(exc)[:100]}",
            )

        # Stage 6: Persist mutation log
        await self._log_mutation(request, result)
        return result

    # ------------------------------------------------------------------
    # Internal stages
    # ------------------------------------------------------------------

    async def _validate_with_critic(self, request: MutationRequest) -> str:
        """Validate a mutation request with the Critic Supervisor.

        Fail-closed: any error returns ``"error"`` (blocks the mutation).

        Args:
            request: The proposed mutation.

        Returns:
            ``"approved"``, ``"rejected"``, ``"modified"``, or ``"error"``.
        """
        if self._critic_agent is None:
            logger.warning("No Critic agent configured — blocking mutation (fail-closed)")
            return "error"

        try:
            # Build a validation payload for the Critic
            payload = {
                "response_text": (
                    f"I will now perform the following action: "
                    f"{request.proposed_summary}\n"
                    f"Tool: {request.tool_name}\n"
                    f"Server: {request.server_name}"
                ),
                "customer_message": request.proposed_summary,
                "knowledge_titles": [],
                "conversation_id": request.conversation_id,
            }

            result = await self._critic_agent.process(payload, {})
            verdict = result.get("verdict", "rejected")

            logger.info(
                "Critic mutation verdict: %s for tool=%s tenant=%s",
                verdict, request.tool_name, request.tenant_id,
            )

            return verdict

        except Exception as exc:
            logger.error(
                "Critic validation failed (fail-closed): tool=%s error=%s",
                request.tool_name, exc,
            )
            return "error"

    async def _check_idempotency(
        self,
        idempotency_key: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Check if a mutation with this idempotency key has already been executed.

        Args:
            idempotency_key: The mutation's unique key.
            tenant_id: Partition key for Cosmos lookup.

        Returns:
            Existing document dict if found, ``None`` if not.
        """
        if self._mutation_log_store is None:
            return None

        try:
            doc = await self._mutation_log_store.read_item(
                item=idempotency_key,
                partition_key=tenant_id,
            )
            # Only block if the previous execution actually ran the tool
            if doc and doc.get("executed"):
                return doc
            return None
        except Exception:
            # NotFound or connection error — assume no duplicate
            return None

    async def _execute_tool(self, request: MutationRequest) -> dict[str, Any]:
        """Execute the MCP tool call.

        Placeholder for the actual MCP tool invocation. In Cycle 5,
        this is never reached because ``allow_mutations=False``.

        Args:
            request: The mutation request.

        Returns:
            Raw tool result dict.

        Raises:
            RuntimeError: If no MCP client factory is configured.
        """
        if self._mcp_client_factory is None:
            raise RuntimeError("No MCP client factory configured")

        # NOTE: In production, this would:
        # 1. Resolve McpServerConfig for request.server_name
        # 2. Create MCP client via factory
        # 3. Connect with credentials
        # 4. Call the tool
        # 5. Close the client
        #
        # For Cycle 5, this code path is unreachable (mutations disabled).
        raise NotImplementedError(
            "MCP mutation execution is disabled in Cycle 5. "
            "This code path should not be reached."
        )

    async def _log_mutation(
        self,
        request: MutationRequest,
        result: MutationResult,
    ) -> None:
        """Persist a mutation attempt to the audit log.

        Args:
            request: The original mutation request.
            result: The execution result.
        """
        idempotency_key = result.idempotency_key or generate_idempotency_key(request)
        doc = MutationLogDocument(idempotency_key, request, result)

        if self._mutation_log_store is not None:
            try:
                await self._mutation_log_store.upsert_item(doc.to_dict())
                logger.debug(
                    "Mutation log persisted: key=%s", idempotency_key,
                )
            except Exception as exc:
                # Log persistence failure is non-fatal
                logger.warning(
                    "Failed to persist mutation log: key=%s error=%s",
                    idempotency_key, exc,
                )
        else:
            logger.debug(
                "Mutation logged (no store): key=%s approved=%s executed=%s "
                "reason=%s",
                idempotency_key, result.approved, result.executed,
                result.error_reason,
            )

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, int]:
        """Return mutation executor statistics.

        Returns:
            Dict with total_requests, total_blocked, total_executed,
            total_critic_rejections.
        """
        return {
            "total_requests": self._total_requests,
            "total_blocked": self._total_blocked,
            "total_executed": self._total_executed,
            "total_critic_rejections": self._total_critic_rejections,
        }
