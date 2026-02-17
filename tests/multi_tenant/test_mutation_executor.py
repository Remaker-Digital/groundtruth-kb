"""Tests for MCP mutation executor — Critic-gated, idempotent execution.

Test IDs: MEXE-01 → MEXE-20

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.mutation_executor import (
    MUTATION_LOG_COLLECTION,
    MUTATION_LOG_TTL_SECONDS,
    MutationExecutor,
    MutationLogDocument,
)
from src.multi_tenant.mutation_policy import (
    MutationPolicy,
    MutationRequest,
    MutationResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(
    tool_name: str = "cancel_subscription",
    tenant_id: str = "tenant-1",
    conversation_id: str = "conv-abc",
    arguments: dict | None = None,
) -> MutationRequest:
    """Create a test MutationRequest."""
    return MutationRequest(
        tool_name=tool_name,
        arguments=arguments or {"subscription_id": "sub_123"},
        proposed_summary=f"Execute {tool_name}",
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        server_name="stripe",
    )


def _make_critic(verdict: str = "approved") -> AsyncMock:
    """Create a mock CriticSupervisorAgent."""
    critic = AsyncMock()
    critic.process = AsyncMock(return_value={
        "approved": verdict == "approved",
        "verdict": verdict,
        "flags": [],
        "modified_response": None,
        "block_reason": None if verdict == "approved" else "unsafe_action",
    })
    return critic


def _make_log_store(existing_doc: dict | None = None) -> AsyncMock:
    """Create a mock Cosmos DB mutation log container."""
    store = AsyncMock()
    if existing_doc:
        store.read_item = AsyncMock(return_value=existing_doc)
    else:
        store.read_item = AsyncMock(side_effect=Exception("NotFound"))
    store.upsert_item = AsyncMock()
    return store


# ---------------------------------------------------------------------------
# MEXE-01→MEXE-04: Policy gate (mutations disabled)
# ---------------------------------------------------------------------------

class TestMutationExecutorPolicyGate:
    """Test executor when mutations are disabled (Cycle 5 default)."""

    @pytest.mark.asyncio
    async def test_mexe_01_disabled_policy_blocks(self):
        """MEXE-01: Default policy (mutations_disabled) blocks immediately."""
        executor = MutationExecutor()
        policy = MutationPolicy()  # allow_mutations=False
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.executed is False
        assert result.error_reason == "mutations_disabled"

    @pytest.mark.asyncio
    async def test_mexe_02_disabled_never_calls_critic(self):
        """MEXE-02: Disabled mutations never invokes the Critic."""
        critic = _make_critic()
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy()
        request = _make_request()

        await executor.execute(request, policy)

        critic.process.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_mexe_03_disabled_increments_blocked(self):
        """MEXE-03: Blocked mutations increment the blocked counter."""
        executor = MutationExecutor()
        policy = MutationPolicy()

        await executor.execute(_make_request(), policy)
        await executor.execute(_make_request(), policy)

        assert executor.stats()["total_blocked"] == 2
        assert executor.stats()["total_requests"] == 2
        assert executor.stats()["total_executed"] == 0

    @pytest.mark.asyncio
    async def test_mexe_04_disabled_logs_mutation(self):
        """MEXE-04: Blocked mutations are still logged."""
        store = _make_log_store()
        executor = MutationExecutor(mutation_log_store=store)
        policy = MutationPolicy()

        await executor.execute(_make_request(), policy)

        store.upsert_item.assert_awaited_once()
        logged_doc = store.upsert_item.call_args[0][0]
        assert logged_doc["executed"] is False
        assert logged_doc["error_reason"] == "mutations_disabled"


# ---------------------------------------------------------------------------
# MEXE-05→MEXE-08: Critic validation
# ---------------------------------------------------------------------------

class TestMutationExecutorCritic:
    """Test Critic-gated validation pipeline."""

    @pytest.mark.asyncio
    async def test_mexe_05_critic_approves(self):
        """MEXE-05: Critic approval passes the validation stage."""
        critic = _make_critic("approved")
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
            require_customer_confirmation=False,
        )
        request = _make_request()

        # Tool execution will raise NotImplementedError since factory is None
        result = await executor.execute(request, policy, customer_confirmed=True)

        # Should get to execution stage and fail there
        assert result.approved is True
        # Either executed=False with execution_failed or the NotImplementedError
        # In Cycle 5, the execute path raises NotImplementedError
        assert result.executed is False
        assert "execution_failed" in (result.error_reason or "")

    @pytest.mark.asyncio
    async def test_mexe_06_critic_rejects(self):
        """MEXE-06: Critic rejection blocks the mutation."""
        critic = _make_critic("rejected")
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.critic_verdict == "rejected"
        assert result.error_reason == "critic_rejected"

    @pytest.mark.asyncio
    async def test_mexe_07_no_critic_agent_blocks(self):
        """MEXE-07: No Critic agent configured → fail-closed block."""
        executor = MutationExecutor(critic_agent=None)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.error_reason == "critic_error"

    @pytest.mark.asyncio
    async def test_mexe_08_critic_exception_blocks(self):
        """MEXE-08: Critic exception → fail-closed block."""
        critic = AsyncMock()
        critic.process = AsyncMock(side_effect=RuntimeError("OpenAI down"))
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.error_reason == "critic_error"


# ---------------------------------------------------------------------------
# MEXE-09→MEXE-11: Customer confirmation
# ---------------------------------------------------------------------------

class TestMutationExecutorConfirmation:
    """Test customer confirmation gate."""

    @pytest.mark.asyncio
    async def test_mexe_09_requires_confirmation(self):
        """MEXE-09: When customer_confirmed=False, returns awaiting confirmation."""
        critic = _make_critic("approved")
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
            require_customer_confirmation=True,
        )
        request = _make_request()

        result = await executor.execute(request, policy, customer_confirmed=False)

        assert result.approved is True
        assert result.executed is False
        assert result.error_reason == "awaiting_customer_confirmation"

    @pytest.mark.asyncio
    async def test_mexe_10_confirmation_not_required(self):
        """MEXE-10: When require_customer_confirmation=False, skips confirmation."""
        critic = _make_critic("approved")
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=True,
            require_customer_confirmation=False,
        )
        request = _make_request()

        # Will proceed to execution (and fail at NotImplementedError)
        result = await executor.execute(request, policy, customer_confirmed=False)

        assert result.approved is True
        # Gets past confirmation to execution
        assert "awaiting_customer_confirmation" != (result.error_reason or "")

    @pytest.mark.asyncio
    async def test_mexe_11_skip_critic_and_confirmation(self):
        """MEXE-11: Skip both Critic and confirmation → straight to execution."""
        executor = MutationExecutor()
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=False,
            require_customer_confirmation=False,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is True
        # Reaches execution but no factory → error
        assert result.executed is False
        assert "execution_failed" in (result.error_reason or "")


# ---------------------------------------------------------------------------
# MEXE-12→MEXE-14: Idempotency
# ---------------------------------------------------------------------------

class TestMutationExecutorIdempotency:
    """Test idempotency key and replay prevention."""

    @pytest.mark.asyncio
    async def test_mexe_12_already_executed_blocks(self):
        """MEXE-12: Existing executed mutation blocks re-execution."""
        existing_doc = {
            "id": "mut-tenant-1-conv-abc-cancel_subscription-1234abcd",
            "executed": True,
            "tenant_id": "tenant-1",
        }
        store = _make_log_store(existing_doc)
        executor = MutationExecutor(mutation_log_store=store)
        policy = MutationPolicy(allow_mutations=True)
        request = _make_request()

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.error_reason == "already_executed"

    @pytest.mark.asyncio
    async def test_mexe_13_non_executed_allows(self):
        """MEXE-13: Existing non-executed doc allows re-attempt."""
        existing_doc = {
            "id": "mut-tenant-1-conv-abc-cancel_subscription-1234abcd",
            "executed": False,  # Was blocked before
            "tenant_id": "tenant-1",
        }
        store = _make_log_store(existing_doc)
        executor = MutationExecutor(mutation_log_store=store)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=False,
            require_customer_confirmation=False,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        # Should proceed past idempotency check
        assert result.error_reason != "already_executed"

    @pytest.mark.asyncio
    async def test_mexe_14_no_store_skips_check(self):
        """MEXE-14: No mutation_log_store → skip idempotency check."""
        executor = MutationExecutor(mutation_log_store=None)
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=False,
            require_customer_confirmation=False,
        )
        request = _make_request()

        result = await executor.execute(request, policy)

        # Should proceed past idempotency (no store to check)
        assert result.error_reason != "already_executed"


# ---------------------------------------------------------------------------
# MEXE-15→MEXE-17: Mutation log persistence
# ---------------------------------------------------------------------------

class TestMutationExecutorLogging:
    """Test mutation audit log persistence."""

    @pytest.mark.asyncio
    async def test_mexe_15_logs_blocked_mutations(self):
        """MEXE-15: Blocked mutations are logged to Cosmos."""
        store = _make_log_store()
        executor = MutationExecutor(mutation_log_store=store)
        policy = MutationPolicy()  # mutations disabled

        await executor.execute(_make_request(), policy)

        store.upsert_item.assert_awaited_once()
        doc = store.upsert_item.call_args[0][0]
        assert doc["executed"] is False
        assert doc["error_reason"] == "mutations_disabled"
        assert doc["tenant_id"] == "tenant-1"
        assert doc["tool_name"] == "cancel_subscription"
        assert doc["ttl"] == MUTATION_LOG_TTL_SECONDS

    @pytest.mark.asyncio
    async def test_mexe_16_log_failure_non_fatal(self):
        """MEXE-16: Mutation log persistence failure is non-fatal."""
        store = AsyncMock()
        store.read_item = AsyncMock(side_effect=Exception("NotFound"))
        store.upsert_item = AsyncMock(side_effect=RuntimeError("Cosmos down"))
        executor = MutationExecutor(mutation_log_store=store)
        policy = MutationPolicy()

        # Should not raise
        result = await executor.execute(_make_request(), policy)
        assert result.error_reason == "mutations_disabled"

    @pytest.mark.asyncio
    async def test_mexe_17_no_store_logs_to_debug(self):
        """MEXE-17: No log store → debug logging only (no exception)."""
        executor = MutationExecutor(mutation_log_store=None)
        policy = MutationPolicy()

        # Should not raise
        result = await executor.execute(_make_request(), policy)
        assert result.approved is False


# ---------------------------------------------------------------------------
# MEXE-18: MutationLogDocument
# ---------------------------------------------------------------------------

class TestMutationLogDocument:
    """Test MutationLogDocument model."""

    def test_mexe_18_log_document_fields(self):
        """MEXE-18: MutationLogDocument captures all fields."""
        request = _make_request()
        result = MutationResult(
            approved=False,
            executed=False,
            error_reason="mutations_disabled",
        )

        doc = MutationLogDocument("mut-key-123", request, result)
        data = doc.to_dict()

        assert data["id"] == "mut-key-123"
        assert data["tenant_id"] == "tenant-1"
        assert data["conversation_id"] == "conv-abc"
        assert data["tool_name"] == "cancel_subscription"
        assert data["server_name"] == "stripe"
        assert data["executed"] is False
        assert data["error_reason"] == "mutations_disabled"
        assert data["ttl"] == MUTATION_LOG_TTL_SECONDS
        assert data["created_at"] is not None
        assert data["arguments_hash"] != ""


# ---------------------------------------------------------------------------
# MEXE-19→MEXE-20: Stats and allowed operations
# ---------------------------------------------------------------------------

class TestMutationExecutorStats:
    """Test executor statistics."""

    @pytest.mark.asyncio
    async def test_mexe_19_stats_tracking(self):
        """MEXE-19: Executor tracks request/blocked/executed/critic stats."""
        executor = MutationExecutor()

        stats = executor.stats()
        assert stats["total_requests"] == 0
        assert stats["total_blocked"] == 0
        assert stats["total_executed"] == 0
        assert stats["total_critic_rejections"] == 0

    @pytest.mark.asyncio
    async def test_mexe_20_allowed_operations_gate(self):
        """MEXE-20: Allowed operations gate blocks unlisted tools."""
        critic = _make_critic("approved")
        executor = MutationExecutor(critic_agent=critic)
        policy = MutationPolicy(
            allow_mutations=True,
            allowed_operations=["refund_charge"],
        )
        request = _make_request(tool_name="delete_customer")

        result = await executor.execute(request, policy)

        assert result.approved is False
        assert result.error_reason == "not_in_allowed_operations"
