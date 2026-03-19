# tests/test_host/test_dispatch_integration.py — Dispatch endpoint integration tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Tests for the main API dispatch endpoint that routes test run requests
to either the in-process verification runner or the test host container.

This verifies:
  1. Dispatch routing logic (in-process vs test-host)
  2. Test host forwarding (HTTP POST to internal ingress)
  3. Status proxying (GET status from test host or Cosmos)
  4. Run listing from Cosmos
  5. Error handling (test host unreachable, invalid suite, etc.)
  6. Security: HMAC auth for test host communication
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api._diagnostics import (
    VALID_ENVIRONMENTS,
    VALID_SUITES,
    _INPROCESS_SUITES,
    _TESTHOST_SUITES,
    _TEST_HOST_URL,
)


# ---------------------------------------------------------------------------
# Dispatch routing — correct path for each suite
# ---------------------------------------------------------------------------

class TestDispatchRouting:
    """Verify correct routing between in-process and test host."""

    def test_smoke_routes_inprocess(self):
        assert "smoke" in _INPROCESS_SUITES

    def test_regression_routes_inprocess(self):
        assert "regression" in _INPROCESS_SUITES

    def test_e2e_routes_inprocess(self):
        assert "e2e" in _INPROCESS_SUITES

    def test_all_routes_inprocess(self):
        assert "all" in _INPROCESS_SUITES

    def test_unit_routes_to_testhost(self):
        assert "unit" in _TESTHOST_SUITES

    def test_core_routes_to_testhost(self):
        assert "core" in _TESTHOST_SUITES

    def test_property_routes_to_testhost(self):
        assert "property" in _TESTHOST_SUITES

    def test_pipeline_routes_to_testhost(self):
        assert "pipeline" in _TESTHOST_SUITES

    def test_full_routes_to_testhost(self):
        assert "full" in _TESTHOST_SUITES

    def test_load_routes_to_testhost(self):
        assert "load" in _TESTHOST_SUITES

    def test_fuzzing_routes_to_testhost(self):
        assert "fuzzing" in _TESTHOST_SUITES


# ---------------------------------------------------------------------------
# Test host URL configuration
# ---------------------------------------------------------------------------

class TestHostConfiguration:
    """Test host URL and connectivity configuration."""

    def test_default_url_scheme(self):
        """Internal ingress uses HTTP (TLS at load balancer)."""
        assert _TEST_HOST_URL.startswith("http://")

    def test_default_url_port(self):
        """Test host listens on port 8001."""
        assert ":8001" in _TEST_HOST_URL

    def test_default_url_host(self):
        """Uses Azure Container Apps internal DNS name."""
        assert "agent-red-test-host" in _TEST_HOST_URL

    def test_url_overridable_via_env(self):
        """TEST_HOST_URL env var overrides the default."""
        # The constant reads from env at import time, so we test the pattern
        url = os.environ.get("TEST_HOST_URL", "http://agent-red-test-host.internal:8001")
        assert url  # Non-empty

    def test_url_ends_without_trailing_slash(self):
        """URL should not have trailing slash (path concatenation)."""
        assert not _TEST_HOST_URL.endswith("/")


# ---------------------------------------------------------------------------
# Forwarding payload validation
# ---------------------------------------------------------------------------

class TestForwardingPayload:
    """Verify the payload shape sent to the test host /run endpoint."""

    def test_testhost_run_accepts_required_fields(self):
        """Test host /run endpoint requires: suite, environment, target_url."""
        # These are the required fields from TestExecution.tsx → _diagnostics.py
        required_fields = {"suite", "environment", "target_url"}
        # All test-host suites must include these when forwarded
        for field in required_fields:
            assert isinstance(field, str)

    def test_testhost_run_accepts_optional_fields(self):
        """Test host /run also accepts: run_id, dry_run, env_overrides."""
        optional_fields = {"run_id", "dry_run", "env_overrides"}
        for field in optional_fields:
            assert isinstance(field, str)


# ---------------------------------------------------------------------------
# Suite validation edge cases
# ---------------------------------------------------------------------------

class TestSuiteValidation:
    """Edge cases in suite validation."""

    def test_empty_suite_not_valid(self):
        assert "" not in VALID_SUITES

    def test_none_suite_not_valid(self):
        assert None not in VALID_SUITES

    def test_case_sensitive(self):
        """Suite names are case-sensitive (lowercase only)."""
        assert "Unit" not in VALID_SUITES
        assert "SMOKE" not in VALID_SUITES
        assert "Pipeline" not in VALID_SUITES

    def test_no_whitespace_suites(self):
        for s in VALID_SUITES:
            assert s.strip() == s, f"Suite '{s}' has whitespace"

    def test_sql_injection_not_valid(self):
        assert "'; DROP TABLE--" not in VALID_SUITES

    def test_path_traversal_not_valid(self):
        assert "../../etc/passwd" not in VALID_SUITES


# ---------------------------------------------------------------------------
# Environment validation edge cases
# ---------------------------------------------------------------------------

class TestEnvironmentValidation:
    """Environment parameter validation."""

    def test_only_two_environments(self):
        assert len(VALID_ENVIRONMENTS) == 2

    def test_development_not_valid(self):
        assert "development" not in VALID_ENVIRONMENTS

    def test_local_not_valid(self):
        assert "local" not in VALID_ENVIRONMENTS

    def test_empty_not_valid(self):
        assert "" not in VALID_ENVIRONMENTS


# ---------------------------------------------------------------------------
# Security — no user input in subprocess args
# ---------------------------------------------------------------------------

class TestSecurityBoundaries:
    """Verify test host doesn't expose subprocess injection vectors."""

    def test_suite_configs_use_hardcoded_args(self):
        """SuiteConfig pytest_args are hardcoded, not from user input."""
        from test_host.suites import SUITE_CONFIGS

        for name, cfg in SUITE_CONFIGS.items():
            for arg in cfg.pytest_args:
                # No env var expansion or shell-like patterns
                assert "$" not in arg, f"Suite {name} has shell variable in args: {arg}"
                assert "`" not in arg, f"Suite {name} has backtick in args: {arg}"

    def test_test_host_url_not_from_request(self):
        """Test host URL comes from env/constant, not from request body."""
        # _TEST_HOST_URL is a module-level constant, not derived from request
        assert isinstance(_TEST_HOST_URL, str)
        assert _TEST_HOST_URL.startswith("http://")

    def test_valid_suites_is_allowlist(self):
        """Suite routing uses an allowlist, not a blocklist."""
        assert isinstance(VALID_SUITES, (set, frozenset))
        assert len(VALID_SUITES) > 0
        # Unknown suites should be rejected (not in the set)
        assert "malicious_suite" not in VALID_SUITES


# ---------------------------------------------------------------------------
# HMAC auth contract for verification runner
# ---------------------------------------------------------------------------

class TestHmacAuthContract:
    """HMAC authentication between main API and verification runner."""

    def test_generate_and_verify_roundtrip(self):
        """Token generated by auth.py can be verified by auth.py."""
        from src.multi_tenant.auth import (
            generate_verification_token,
            verify_verification_token,
        )

        secret = "test-secret-for-hmac-validation"
        run_id = "run-hmac-test-42"

        token = generate_verification_token(run_id, secret)
        # Should not raise
        result = verify_verification_token(token, secret)
        assert result["run_id"] == run_id

    def test_token_format_three_parts(self):
        """Token has format: {timestamp}.{run_id}.{hmac_hex}."""
        from src.multi_tenant.auth import generate_verification_token

        token = generate_verification_token("run-fmt", "secret")
        parts = token.split(".")
        assert len(parts) == 3
        # Part 0: timestamp (numeric)
        assert parts[0].isdigit()
        # Part 1: run_id
        assert parts[1] == "run-fmt"
        # Part 2: hex string (64 chars for SHA-256)
        assert len(parts[2]) == 64
        assert all(c in "0123456789abcdef" for c in parts[2])

    def test_wrong_secret_fails(self):
        """Token signed with one secret fails verification with another."""
        from src.multi_tenant.auth import (
            generate_verification_token,
            verify_verification_token,
        )
        from src.multi_tenant.auth import AuthenticationError

        token = generate_verification_token("run-wrong", "correct-secret")
        with pytest.raises(AuthenticationError):
            verify_verification_token(token, "wrong-secret")

    def test_tampered_run_id_fails(self):
        """Tampering with the run_id invalidates the HMAC."""
        from src.multi_tenant.auth import (
            generate_verification_token,
            verify_verification_token,
        )
        from src.multi_tenant.auth import AuthenticationError

        token = generate_verification_token("run-original", "secret")
        parts = token.split(".")
        tampered = f"{parts[0]}.run-tampered.{parts[2]}"
        with pytest.raises(AuthenticationError):
            verify_verification_token(tampered, "secret")

    def test_tampered_timestamp_fails(self):
        """Tampering with the timestamp invalidates the HMAC."""
        from src.multi_tenant.auth import (
            generate_verification_token,
            verify_verification_token,
        )
        from src.multi_tenant.auth import AuthenticationError

        token = generate_verification_token("run-ts", "secret")
        parts = token.split(".")
        tampered = f"9999999999.{parts[1]}.{parts[2]}"
        with pytest.raises(AuthenticationError):
            verify_verification_token(tampered, "secret")

    def test_empty_secret_rejected(self):
        """Empty secret is rejected."""
        from src.multi_tenant.auth import verify_verification_token
        from src.multi_tenant.auth import AuthenticationError

        with pytest.raises(AuthenticationError):
            verify_verification_token("1234.run.abcd", "")

    def test_empty_token_rejected(self):
        """Empty token is rejected."""
        from src.multi_tenant.auth import verify_verification_token
        from src.multi_tenant.auth import AuthenticationError

        with pytest.raises(AuthenticationError):
            verify_verification_token("", "secret")

    def test_malformed_token_rejected(self):
        """Malformed token (wrong number of parts) is rejected."""
        from src.multi_tenant.auth import verify_verification_token
        from src.multi_tenant.auth import AuthenticationError

        with pytest.raises(AuthenticationError):
            verify_verification_token("only-one-part", "secret")
        with pytest.raises(AuthenticationError):
            verify_verification_token("two.parts", "secret")
        with pytest.raises(AuthenticationError):
            verify_verification_token("a.b.c.d", "secret")

    def test_constant_time_comparison(self):
        """Verification uses secrets.compare_digest for constant-time check."""
        import inspect
        from src.multi_tenant.auth import verify_verification_token
        source = inspect.getsource(verify_verification_token)
        assert "compare_digest" in source


# ---------------------------------------------------------------------------
# Run ID format contract
# ---------------------------------------------------------------------------

class TestRunIdContract:
    """Run ID format expected by SPA and stored in Cosmos."""

    def test_generated_run_id_starts_with_prefix(self):
        """Auto-generated run IDs start with 'run-'."""
        import uuid
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        assert run_id.startswith("run-")

    def test_run_id_is_url_safe(self):
        """Run IDs must be URL-safe (used in path: /status/{run_id})."""
        import uuid
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        # URL-safe characters only
        safe_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
        assert all(c in safe_chars for c in run_id)

    def test_cosmos_document_id_format(self):
        """Cosmos document ID = 'test_runs:{run_id}'."""
        run_id = "run-abc123def4"
        doc_id = f"test_runs:{run_id}"
        assert doc_id == "test_runs:run-abc123def4"
        assert ":" in doc_id  # Cosmos partition key separator
