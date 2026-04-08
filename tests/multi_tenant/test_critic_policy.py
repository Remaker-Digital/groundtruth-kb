"""P0 CriticPolicy unit tests — fail-closed Critic safety enforcement.

Tests the fail-closed safety gate, circuit breaker state machine,
SAFE_FALLBACK_MESSAGE, audit logging, escalation, and health monitoring.

Test IDs: CP-01 through CP-20 per §4.4 of
docs/COMPREHENSIVE-TEST-PLAN.md.

Work Item: P0 launch-blocker tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.multi_tenant.critic_policy import (
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_RECOVERY_SECONDS,
    CIRCUIT_BREAKER_WINDOW_SECONDS,
    CRITIC_HTTP_TIMEOUT_SECONDS,
    CRITIC_TIMEOUT_MS,
    SAFE_FALLBACK_MESSAGE,
    CircuitBreaker,
    CriticBlockReason,
    CriticPolicy,
    CriticResult,
    CriticVerdict,
)
from src.multi_tenant.cosmos_schema import AuditEventType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_ID = "t-critic-001"
_CONVERSATION_ID = "conv-critic-001"
_RESPONSE_TEXT = "Here is our return policy: you can return items within 30 days."
_CUSTOMER_MESSAGE = "What is your return policy?"
_CRITIC_URLS = ["http://10.0.1.7:8080", "http://10.0.1.7b:8080"]


def _make_policy(
    critic_urls: list[str] | None = None,
    audit_repo: AsyncMock | None = None,
    conversation_repo: AsyncMock | None = None,
) -> CriticPolicy:
    """Create a CriticPolicy with mock repos."""
    if audit_repo is None:
        audit_repo = AsyncMock()
        audit_repo.log_event.return_value = None
    if conversation_repo is None:
        conversation_repo = AsyncMock()
        conversation_repo.patch.return_value = None

    return CriticPolicy(
        critic_urls=critic_urls or list(_CRITIC_URLS),
        conversation_repo=conversation_repo,
        audit_repo=audit_repo,
    )


def _mock_httpx_response(
    status_code: int = 200,
    json_body: dict | None = None,
) -> httpx.Response:
    """Create a mock httpx Response."""
    if json_body is None:
        json_body = {"verdict": "approved", "flags": []}
    resp = httpx.Response(
        status_code=status_code,
        json=json_body,
        request=httpx.Request("POST", "http://10.0.1.7:8080/validate"),
    )
    return resp


# ===========================================================================
# Critic validation — CP-01 through CP-05
# ===========================================================================


class TestCriticValidation:
    """Tests for the core fail-closed validation gate."""

    @pytest.mark.unit
    async def test_critic_approves_response_passes(self):
        """CP-01: Critic approves → response passes through."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(200, {"verdict": "approved", "flags": []})

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is True
        assert result.verdict == CriticVerdict.APPROVED
        assert result.block_reason is None

    @pytest.mark.unit
    async def test_critic_rejects_response_blocked(self):
        """CP-02: Critic rejects → response blocked, SAFE_FALLBACK_MESSAGE returned."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(200, {
            "verdict": "rejected",
            "flags": ["brand_safety_risk"],
        })

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is False
        assert result.verdict == CriticVerdict.REJECTED
        assert result.block_reason == CriticBlockReason.REJECTED
        assert "brand_safety_risk" in result.flags

    @pytest.mark.unit
    async def test_critic_timeout_blocks_response(self):
        """CP-03: Critic timeout (>800ms) → response blocked."""
        policy = _make_policy()

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.side_effect = httpx.ReadTimeout("timed out")
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is False
        assert result.block_reason == CriticBlockReason.UNAVAILABLE

    @pytest.mark.unit
    async def test_critic_error_blocks_response(self):
        """CP-04: Critic error (non-200) → response blocked."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(500, {"error": "internal server error"})

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is False
        assert result.block_reason == CriticBlockReason.ERROR
        assert "critic_http_500" in result.flags

    @pytest.mark.unit
    async def test_critic_unavailable_blocks_response(self):
        """CP-05: All Critic replicas down → response blocked."""
        policy = _make_policy()

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.side_effect = httpx.ConnectError("connection refused")
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is False
        assert result.block_reason == CriticBlockReason.UNAVAILABLE
        assert "all_critic_replicas_unavailable" in result.flags


# ===========================================================================
# Pipeline wrapper — CP-06, CP-07, CP-08
# ===========================================================================


class TestRequireCriticApproval:
    """Tests for the require_critic_approval() pipeline wrapper."""

    @pytest.mark.unit
    async def test_approval_returns_true_and_text(self):
        """CP-06: require_critic_approval() returns (True, text, result) on approval."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(200, {"verdict": "approved", "flags": []})

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            approved, text, result = await policy.require_critic_approval(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert approved is True
        assert text == _RESPONSE_TEXT
        assert result.approved is True

    @pytest.mark.unit
    async def test_rejection_returns_false_and_fallback(self):
        """CP-07: require_critic_approval() returns (False, fallback, result) on rejection."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(200, {"verdict": "rejected", "flags": []})

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            approved, text, result = await policy.require_critic_approval(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert approved is False
        assert text == SAFE_FALLBACK_MESSAGE
        assert result.approved is False

    @pytest.mark.unit
    async def test_fallback_message_is_only_unvalidated_text(self):
        """CP-08: SAFE_FALLBACK_MESSAGE is the only text delivered when Critic fails."""
        policy = _make_policy()

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.side_effect = httpx.ConnectError("down")
            mock_client.return_value = client

            _, text, _ = await policy.require_critic_approval(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert text == SAFE_FALLBACK_MESSAGE
        assert "sorry" in text.lower()
        assert "try again" in text.lower()


# ===========================================================================
# Audit logging — CP-09, CP-10
# ===========================================================================


class TestAuditLogging:
    """Tests for SECURITY_EVENT and ESCALATION_TRIGGERED audit logging."""

    @pytest.mark.unit
    async def test_security_event_logged_on_block(self):
        """CP-09: SECURITY_EVENT audit logged on blocked response."""
        audit_repo = AsyncMock()
        audit_repo.log_event.return_value = None
        policy = _make_policy(audit_repo=audit_repo)

        mock_resp = _mock_httpx_response(200, {"verdict": "rejected", "flags": ["pii_detected"]})

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        # SECURITY_EVENT should be logged
        audit_repo.log_event.assert_awaited()
        call_kwargs = audit_repo.log_event.call_args_list[0].kwargs
        assert call_kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert call_kwargs["payload"]["action"] == "response_blocked"
        assert call_kwargs["payload"]["block_reason"] == "rejected"

    @pytest.mark.unit
    async def test_escalation_triggered_when_unavailable(self):
        """CP-10: ESCALATION_TRIGGERED when Critic replicas unavailable."""
        audit_repo = AsyncMock()
        audit_repo.log_event.return_value = None
        policy = _make_policy(audit_repo=audit_repo)

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.side_effect = httpx.ConnectError("down")
            mock_client.return_value = client

            await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        # Should have SECURITY_EVENT + ESCALATION_TRIGGERED
        event_types = [
            call.kwargs["event_type"]
            for call in audit_repo.log_event.call_args_list
        ]
        assert AuditEventType.SECURITY_EVENT in event_types
        assert AuditEventType.ESCALATION_TRIGGERED in event_types


# ===========================================================================
# Circuit breaker — CP-11 through CP-14
# ===========================================================================


class TestCircuitBreaker:
    """Tests for the circuit breaker state machine."""

    @pytest.mark.unit
    def test_closed_to_open_after_threshold_failures(self):
        """CP-11: Circuit breaker CLOSED → OPEN after 5 failures in 30s."""
        cb = CircuitBreaker(
            failure_threshold=5,
            window_seconds=30,
            recovery_seconds=15,
        )

        assert cb.state == CircuitBreaker.State.CLOSED

        for _ in range(5):
            cb.record_failure()

        assert cb.state == CircuitBreaker.State.OPEN
        assert cb.is_open is True

    @pytest.mark.unit
    def test_open_to_half_open_after_recovery(self):
        """CP-12: Circuit breaker OPEN → HALF_OPEN after 15s recovery."""
        cb = CircuitBreaker(
            failure_threshold=5,
            window_seconds=30,
            recovery_seconds=15,
        )

        # Force to OPEN
        for _ in range(5):
            cb.record_failure()
        assert cb.state == CircuitBreaker.State.OPEN

        # Simulate time passing beyond recovery period
        cb._opened_at = time.monotonic() - 20  # 20s ago, recovery is 15s

        assert cb.state == CircuitBreaker.State.HALF_OPEN

    @pytest.mark.unit
    def test_half_open_to_closed_on_success(self):
        """CP-13: Circuit breaker HALF_OPEN → CLOSED on success."""
        cb = CircuitBreaker(
            failure_threshold=5,
            window_seconds=30,
            recovery_seconds=15,
        )

        # Force to OPEN then HALF_OPEN
        for _ in range(5):
            cb.record_failure()
        cb._opened_at = time.monotonic() - 20
        assert cb.state == CircuitBreaker.State.HALF_OPEN

        # Record success
        cb.record_success()
        assert cb.state == CircuitBreaker.State.CLOSED
        assert cb.is_open is False

    @pytest.mark.unit
    def test_half_open_to_open_on_failure(self):
        """CP-14: Circuit breaker HALF_OPEN → OPEN on failure."""
        cb = CircuitBreaker(
            failure_threshold=1,  # Low threshold for easy test
            window_seconds=30,
            recovery_seconds=15,
        )

        # Force to OPEN then HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitBreaker.State.OPEN
        cb._opened_at = time.monotonic() - 20
        assert cb.state == CircuitBreaker.State.HALF_OPEN

        # Record another failure — should go back to OPEN
        cb.record_failure()
        assert cb.state == CircuitBreaker.State.OPEN


# ===========================================================================
# Data integrity — CP-15, CP-16
# ===========================================================================


class TestCriticResultDataClass:
    """Tests for the CriticResult frozen dataclass."""

    @pytest.mark.unit
    def test_critic_result_is_frozen(self):
        """CP-15: CriticResult dataclass is frozen (immutable)."""
        result = CriticResult(
            approved=True,
            verdict=CriticVerdict.APPROVED,
            block_reason=None,
            flags=[],
            modified_response=None,
            latency_ms=50.0,
            critic_instance="http://10.0.1.7:8080",
            request_id="req-001",
        )

        with pytest.raises(AttributeError):
            result.approved = False  # type: ignore[misc]

    @pytest.mark.unit
    def test_critic_result_captures_latency(self):
        """CP-16: CriticResult captures latency."""
        result = CriticResult(
            approved=True,
            verdict=CriticVerdict.APPROVED,
            block_reason=None,
            flags=[],
            modified_response=None,
            latency_ms=123.45,
            critic_instance="http://10.0.1.7:8080",
            request_id="req-002",
        )

        assert result.latency_ms == 123.45
        assert isinstance(result.latency_ms, float)


# ===========================================================================
# Health check — CP-17
# ===========================================================================


class TestHealthCheck:
    """Tests for Critic health monitoring."""

    @pytest.mark.unit
    async def test_health_check_returns_circuit_breaker_state(self):
        """CP-17: Health check returns circuit breaker state."""
        policy = _make_policy()

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            # Both replicas healthy
            client.get.return_value = httpx.Response(
                200,
                request=httpx.Request("GET", "http://10.0.1.7:8080/health"),
            )
            mock_client.return_value = client

            health = await policy.check_critic_health()

        assert health.healthy is True
        assert health.replicas_available == 2
        assert health.replicas_total == 2
        assert health.open_breaker_count == 0
        assert health.total_breakers >= 0
        assert len(health.details) == 2


# ===========================================================================
# Connection pooling — CP-18
# ===========================================================================


class TestConnectionPooling:
    """Tests for httpx connection pooling reuse."""

    @pytest.mark.unit
    async def test_http_client_reused_across_calls(self):
        """CP-18: Connection pooling reused across calls (httpx)."""
        policy = _make_policy()

        # First call creates the client
        client1 = await policy._get_http_client()
        assert client1 is not None

        # Second call reuses the same client
        client2 = await policy._get_http_client()
        assert client1 is client2


# ===========================================================================
# Timeout budget — CP-19
# ===========================================================================


class TestTimeoutBudget:
    """Tests for 800ms timeout budget enforcement."""

    @pytest.mark.unit
    def test_timeout_constants(self):
        """CP-19: 800ms timeout budget enforced via constants."""
        assert CRITIC_TIMEOUT_MS == 800
        assert CRITIC_HTTP_TIMEOUT_SECONDS == 1.0  # Slightly above 800ms for network buffer
        assert CIRCUIT_BREAKER_FAILURE_THRESHOLD == 5
        assert CIRCUIT_BREAKER_WINDOW_SECONDS == 30
        assert CIRCUIT_BREAKER_RECOVERY_SECONDS == 15


# ===========================================================================
# Modified response — CP-20
# ===========================================================================


class TestModifiedResponse:
    """Tests for Critic response modification handling."""

    @pytest.mark.unit
    async def test_critic_modifies_response_text(self):
        """CP-20: Critic modifies response text → modified text returned."""
        policy = _make_policy()

        modified_text = "Here is our return policy: items can be returned within 30 days with receipt."
        mock_resp = _mock_httpx_response(200, {
            "verdict": "modified",
            "flags": ["response_refined"],
            "modified_response": modified_text,
        })

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            approved, text, result = await policy.require_critic_approval(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert approved is True
        assert text == modified_text
        assert result.verdict == CriticVerdict.MODIFIED
        assert result.modified_response == modified_text

    @pytest.mark.unit
    async def test_modified_verdict_without_text_rejected(self):
        """CP-20b: Modified verdict without modified_response is treated as rejection."""
        policy = _make_policy()

        mock_resp = _mock_httpx_response(200, {
            "verdict": "modified",
            "flags": [],
            # No modified_response provided
        })

        with patch.object(policy, "_get_http_client") as mock_client:
            client = AsyncMock()
            client.post.return_value = mock_resp
            mock_client.return_value = client

            result = await policy.validate_response(
                _TENANT_ID, _CONVERSATION_ID, _RESPONSE_TEXT, _CUSTOMER_MESSAGE,
            )

        assert result.approved is False
        assert "modified_verdict_without_text" in result.flags


# ===========================================================================
# Constructor validation
# ===========================================================================


class TestConstructorValidation:
    """Tests for CriticPolicy constructor."""

    @pytest.mark.unit
    def test_no_urls_raises_value_error(self):
        """CriticPolicy requires at least one URL."""
        with pytest.raises(ValueError, match="At least one Critic"):
            CriticPolicy(critic_urls=[])

    @pytest.mark.unit
    def test_circuit_breaker_reset(self):
        """Circuit breaker can be force-reset to CLOSED."""
        cb = CircuitBreaker(failure_threshold=2, window_seconds=30, recovery_seconds=15)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreaker.State.OPEN

        # Reset
        cb.reset()
        assert cb.state == CircuitBreaker.State.CLOSED
        assert cb.is_open is False

    @pytest.mark.unit
    def test_policy_exposes_circuit_breaker_state(self):
        """get_circuit_breaker_state() returns state for a tenant."""
        policy = _make_policy()
        # No breaker created yet for this tenant
        assert policy.get_circuit_breaker_state("t-test") == "no_breaker"
        # Create breaker by getting it
        policy._get_breaker("t-test")
        assert policy.get_circuit_breaker_state("t-test") == "closed"

    @pytest.mark.unit
    def test_policy_reset_circuit_breaker(self):
        """reset_circuit_breaker() forces CLOSED for a specific tenant."""
        policy = _make_policy()
        tenant_id = "t-reset-test"
        # Force open via tenant breaker
        breaker = policy._get_breaker(tenant_id)
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()
        assert policy.get_circuit_breaker_state(tenant_id) == "open"

        policy.reset_circuit_breaker(tenant_id)
        assert policy.get_circuit_breaker_state(tenant_id) == "closed"
