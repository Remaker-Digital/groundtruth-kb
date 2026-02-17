"""Tests for MCP mutation policy — models and evaluate_request logic.

Test IDs: MPOL-01 → MPOL-15

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.mutation_policy import (
    MutationPolicy,
    MutationRequest,
    MutationResult,
    evaluate_request,
    generate_idempotency_key,
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


# ---------------------------------------------------------------------------
# MPOL-01→MPOL-03: MutationPolicy model
# ---------------------------------------------------------------------------

class TestMutationPolicyModel:
    """Test MutationPolicy defaults and serialization."""

    def test_mpol_01_default_mutations_disabled(self):
        """MPOL-01: Default MutationPolicy has mutations disabled."""
        policy = MutationPolicy()
        assert policy.allow_mutations is False
        assert policy.require_critic_approval is True
        assert policy.require_customer_confirmation is True
        assert policy.allowed_operations == []
        assert policy.max_mutations_per_conversation == 3

    def test_mpol_02_to_dict_roundtrip(self):
        """MPOL-02: to_dict → from_dict roundtrip preserves values."""
        policy = MutationPolicy(
            allow_mutations=True,
            require_critic_approval=False,
            allowed_operations=["refund_charge", "cancel_subscription"],
            max_mutations_per_conversation=5,
        )
        data = policy.to_dict()
        restored = MutationPolicy.from_dict(data)

        assert restored.allow_mutations is True
        assert restored.require_critic_approval is False
        assert restored.allowed_operations == ["refund_charge", "cancel_subscription"]
        assert restored.max_mutations_per_conversation == 5

    def test_mpol_03_from_dict_defaults(self):
        """MPOL-03: from_dict with empty dict uses safe defaults."""
        policy = MutationPolicy.from_dict({})
        assert policy.allow_mutations is False
        assert policy.require_critic_approval is True


# ---------------------------------------------------------------------------
# MPOL-04→MPOL-05: MutationRequest + MutationResult
# ---------------------------------------------------------------------------

class TestMutationRequestResult:
    """Test MutationRequest and MutationResult models."""

    def test_mpol_04_request_fields(self):
        """MPOL-04: MutationRequest stores all fields."""
        req = _make_request(
            tool_name="refund_charge",
            arguments={"charge_id": "ch_abc"},
        )
        assert req.tool_name == "refund_charge"
        assert req.arguments == {"charge_id": "ch_abc"}
        assert req.tenant_id == "tenant-1"
        assert req.conversation_id == "conv-abc"
        assert req.server_name == "stripe"

    def test_mpol_05_result_to_dict(self):
        """MPOL-05: MutationResult.to_dict() includes key fields."""
        result = MutationResult(
            approved=True,
            executed=True,
            idempotency_key="mut-t1-c1-tool-abc12345",
            critic_verdict="approved",
            customer_confirmed=True,
            tool_result={"content": "ok"},
        )
        d = result.to_dict()
        assert d["approved"] is True
        assert d["executed"] is True
        assert d["idempotency_key"] == "mut-t1-c1-tool-abc12345"
        assert d["critic_verdict"] == "approved"
        assert d["has_tool_result"] is True


# ---------------------------------------------------------------------------
# MPOL-06: Idempotency key generation
# ---------------------------------------------------------------------------

class TestIdempotencyKey:
    """Test idempotency key generation."""

    def test_mpol_06_key_format(self):
        """MPOL-06: Idempotency key follows expected format."""
        req = _make_request()
        key = generate_idempotency_key(req)

        assert key.startswith("mut-")
        assert "tenant-1" in key
        assert "conv-abc" in key
        assert "cancel_subscription" in key
        # Should have a hash suffix
        parts = key.split("-")
        assert len(parts) >= 5

    def test_mpol_06b_same_args_same_key(self):
        """MPOL-06b: Same request produces same idempotency key."""
        req1 = _make_request(arguments={"id": "123"})
        req2 = _make_request(arguments={"id": "123"})
        assert generate_idempotency_key(req1) == generate_idempotency_key(req2)

    def test_mpol_06c_different_args_different_key(self):
        """MPOL-06c: Different arguments produce different keys."""
        req1 = _make_request(arguments={"id": "123"})
        req2 = _make_request(arguments={"id": "456"})
        assert generate_idempotency_key(req1) != generate_idempotency_key(req2)


# ---------------------------------------------------------------------------
# MPOL-07→MPOL-15: evaluate_request()
# ---------------------------------------------------------------------------

class TestEvaluateRequest:
    """Test the policy evaluation gate."""

    def test_mpol_07_mutations_disabled_blocks(self):
        """MPOL-07: Mutations disabled → blocks with 'mutations_disabled'."""
        policy = MutationPolicy(allow_mutations=False)
        req = _make_request()

        result = evaluate_request(req, policy)

        assert result.approved is False
        assert result.error_reason == "mutations_disabled"
        assert result.idempotency_key is None

    def test_mpol_08_mutations_enabled_approves(self):
        """MPOL-08: Mutations enabled with no other restrictions → approved."""
        policy = MutationPolicy(
            allow_mutations=True,
            allowed_operations=[],
            max_mutations_per_conversation=0,  # unlimited
        )
        req = _make_request()

        result = evaluate_request(req, policy)

        assert result.approved is True
        assert result.idempotency_key is not None
        assert result.error_reason is None

    def test_mpol_09_allowed_operations_pass(self):
        """MPOL-09: Tool in allowed_operations passes."""
        policy = MutationPolicy(
            allow_mutations=True,
            allowed_operations=["cancel_subscription", "refund_charge"],
        )
        req = _make_request(tool_name="cancel_subscription")

        result = evaluate_request(req, policy)
        assert result.approved is True

    def test_mpol_10_allowed_operations_block(self):
        """MPOL-10: Tool NOT in allowed_operations → blocked."""
        policy = MutationPolicy(
            allow_mutations=True,
            allowed_operations=["refund_charge"],
        )
        req = _make_request(tool_name="cancel_subscription")

        result = evaluate_request(req, policy)
        assert result.approved is False
        assert result.error_reason == "not_in_allowed_operations"

    def test_mpol_11_conversation_limit_blocks(self):
        """MPOL-11: Exceeding conversation limit → blocked."""
        policy = MutationPolicy(
            allow_mutations=True,
            max_mutations_per_conversation=2,
        )
        req = _make_request()

        result = evaluate_request(req, policy, mutations_in_conversation=2)

        assert result.approved is False
        assert result.error_reason == "conversation_limit_exceeded"

    def test_mpol_12_conversation_limit_under_allows(self):
        """MPOL-12: Under conversation limit → approved."""
        policy = MutationPolicy(
            allow_mutations=True,
            max_mutations_per_conversation=3,
        )
        req = _make_request()

        result = evaluate_request(req, policy, mutations_in_conversation=1)
        assert result.approved is True

    def test_mpol_13_zero_limit_means_unlimited(self):
        """MPOL-13: max_mutations_per_conversation=0 means unlimited."""
        policy = MutationPolicy(
            allow_mutations=True,
            max_mutations_per_conversation=0,
        )
        req = _make_request()

        result = evaluate_request(req, policy, mutations_in_conversation=100)
        assert result.approved is True

    def test_mpol_14_approved_result_has_idempotency_key(self):
        """MPOL-14: Approved result includes idempotency key."""
        policy = MutationPolicy(allow_mutations=True)
        req = _make_request()

        result = evaluate_request(req, policy)

        assert result.approved is True
        assert result.idempotency_key is not None
        assert result.idempotency_key.startswith("mut-")

    def test_mpol_15_default_policy_always_blocks(self):
        """MPOL-15: Default MutationPolicy (Cycle 5) blocks everything."""
        policy = MutationPolicy()
        req = _make_request(tool_name="refund_charge")

        result = evaluate_request(req, policy)
        assert result.approved is False
        assert result.error_reason == "mutations_disabled"
