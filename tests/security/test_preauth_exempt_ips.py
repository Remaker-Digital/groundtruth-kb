"""Tests for PreAuthRateLimiter IP exemption (SPEC-1704).

Verifies that exempt IPs bypass pre-auth rate limiting while
non-exempt IPs remain fully protected.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.multi_tenant.security_hardening import PreAuthRateLimiter


class TestExemptIpNeverBlocked:
    """Exempt IPs must never be blocked, even after exceeding the failure threshold."""

    def test_exempt_ip_not_blocked_after_exceeding_threshold(self) -> None:
        """An exempt IP remains unblocked after max_attempts failures."""
        limiter = PreAuthRateLimiter(
            max_attempts=3,
            window_seconds=60,
            block_seconds=300,
            exempt_ips=frozenset({"10.0.0.1"}),
        )
        for _ in range(10):
            result = limiter.record_failure("10.0.0.1")
            assert result is False, "record_failure should return False for exempt IP"

        assert limiter.is_blocked("10.0.0.1") is False

    def test_exempt_ip_no_tracker_entry_created(self) -> None:
        """Failures for exempt IPs should not create tracker entries."""
        limiter = PreAuthRateLimiter(
            max_attempts=3,
            window_seconds=60,
            block_seconds=300,
            exempt_ips=frozenset({"10.0.0.1"}),
        )
        limiter.record_failure("10.0.0.1")
        limiter.record_failure("10.0.0.1")
        limiter.record_failure("10.0.0.1")

        # Exempt IP should have no tracker entry
        assert "10.0.0.1" not in limiter._trackers


class TestNonExemptIpStillBlocked:
    """Non-exempt IPs must still be blocked normally (regression check)."""

    def test_non_exempt_ip_blocked_after_threshold(self) -> None:
        """A non-exempt IP is blocked after max_attempts failures."""
        limiter = PreAuthRateLimiter(
            max_attempts=3,
            window_seconds=60,
            block_seconds=300,
            exempt_ips=frozenset({"10.0.0.1"}),
        )
        for _ in range(3):
            limiter.record_failure("192.168.1.100")

        assert limiter.is_blocked("192.168.1.100") is True

    def test_mixed_exempt_and_non_exempt(self) -> None:
        """Exempt and non-exempt IPs coexist correctly."""
        limiter = PreAuthRateLimiter(
            max_attempts=3,
            window_seconds=60,
            block_seconds=300,
            exempt_ips=frozenset({"10.0.0.1"}),
        )

        # Both IPs fail 5 times
        for _ in range(5):
            limiter.record_failure("10.0.0.1")
            limiter.record_failure("192.168.1.100")

        # Exempt IP unblocked, non-exempt IP blocked
        assert limiter.is_blocked("10.0.0.1") is False
        assert limiter.is_blocked("192.168.1.100") is True


class TestEnvVarParsing:
    """PRE_AUTH_RATE_LIMIT_EXEMPT_IPS env var parsing."""

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": "10.0.0.1"})
    def test_single_ip_from_env(self) -> None:
        """Single IP parsed from env var."""
        limiter = PreAuthRateLimiter(max_attempts=3)
        assert limiter._exempt_ips == frozenset({"10.0.0.1"})

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": "10.0.0.1,10.0.0.2,172.16.0.1"})
    def test_multiple_ips_from_env(self) -> None:
        """Multiple comma-separated IPs parsed from env var."""
        limiter = PreAuthRateLimiter(max_attempts=3)
        assert limiter._exempt_ips == frozenset({"10.0.0.1", "10.0.0.2", "172.16.0.1"})

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": " 10.0.0.1 , 10.0.0.2 "})
    def test_whitespace_trimmed(self) -> None:
        """Whitespace around IPs is trimmed."""
        limiter = PreAuthRateLimiter(max_attempts=3)
        assert limiter._exempt_ips == frozenset({"10.0.0.1", "10.0.0.2"})

    @patch.dict(os.environ, {}, clear=False)
    def test_unset_env_var_means_no_exemptions(self) -> None:
        """Unset env var results in empty exempt set."""
        env = os.environ.copy()
        env.pop("PRE_AUTH_RATE_LIMIT_EXEMPT_IPS", None)
        with patch.dict(os.environ, env, clear=True):
            limiter = PreAuthRateLimiter(max_attempts=3)
            assert limiter._exempt_ips == frozenset()

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": ""})
    def test_empty_env_var_means_no_exemptions(self) -> None:
        """Empty env var results in empty exempt set."""
        limiter = PreAuthRateLimiter(max_attempts=3)
        assert limiter._exempt_ips == frozenset()

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": ",,,"})
    def test_only_commas_means_no_exemptions(self) -> None:
        """Env var with only commas results in empty exempt set."""
        limiter = PreAuthRateLimiter(max_attempts=3)
        assert limiter._exempt_ips == frozenset()


class TestConstructorParameterOverridesEnv:
    """Constructor exempt_ips parameter takes precedence over env var."""

    @patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": "10.0.0.99"})
    def test_constructor_overrides_env(self) -> None:
        """Explicit exempt_ips parameter overrides env var."""
        limiter = PreAuthRateLimiter(
            max_attempts=3,
            exempt_ips=frozenset({"172.16.0.1"}),
        )
        assert limiter._exempt_ips == frozenset({"172.16.0.1"})
        assert "10.0.0.99" not in limiter._exempt_ips

    def test_constructor_empty_frozenset_overrides_env(self) -> None:
        """Explicit empty frozenset disables exemption even if env var set."""
        with patch.dict(os.environ, {"PRE_AUTH_RATE_LIMIT_EXEMPT_IPS": "10.0.0.99"}):
            limiter = PreAuthRateLimiter(
                max_attempts=3,
                exempt_ips=frozenset(),
            )
            assert limiter._exempt_ips == frozenset()


class TestDefaultBehaviorUnchanged:
    """Without exemptions, PreAuthRateLimiter behaves exactly as before."""

    def test_no_exempt_ips_default(self) -> None:
        """Default construction (no env var) has no exemptions."""
        with patch.dict(os.environ, {}, clear=False):
            env = os.environ.copy()
            env.pop("PRE_AUTH_RATE_LIMIT_EXEMPT_IPS", None)
            with patch.dict(os.environ, env, clear=True):
                limiter = PreAuthRateLimiter(max_attempts=3)
                assert limiter._exempt_ips == frozenset()

                # Normal blocking still works
                for _ in range(3):
                    limiter.record_failure("192.168.1.1")
                assert limiter.is_blocked("192.168.1.1") is True
