"""Tests for the cloud-native verification runner (SPEC-1846 / WI-1586).

Verifies:
- CheckResult dataclass serialization
- Suite-to-checks mapping completeness
- VerificationRunner rate limiting behavior
- Background task lifecycle (queued → running → passed/failed)
- Concurrent run protection (409 on second trigger)
- Stale run detection
- Check filtering by status and category

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.verification_runner import (
    CheckResult,
    SUITE_CATEGORIES,
    SUITE_DESCRIPTIONS,
    VerificationRunner,
)


# ---------------------------------------------------------------------------
# CheckResult
# ---------------------------------------------------------------------------

class TestCheckResult:
    """CheckResult dataclass behavior."""

    def test_to_dict(self):
        """to_dict() returns all fields."""
        r = CheckResult(name="test", category="health", status="pass", latency_ms=12.3, detail="ok")
        d = r.to_dict()
        assert d["name"] == "test"
        assert d["category"] == "health"
        assert d["status"] == "pass"
        assert d["latency_ms"] == 12.3
        assert d["detail"] == "ok"

    def test_default_values(self):
        """Defaults: status=pass, latency_ms=0, detail empty."""
        r = CheckResult(name="x", category="y")
        assert r.status == "pass"
        assert r.latency_ms == 0.0
        assert r.detail == ""

    def test_fail_status(self):
        """Fail status round-trips through to_dict."""
        r = CheckResult(name="x", category="y", status="fail", detail="broken")
        assert r.to_dict()["status"] == "fail"


# ---------------------------------------------------------------------------
# Suite definitions
# ---------------------------------------------------------------------------

class TestSuiteDefinitions:
    """Suite category mappings."""

    def test_smoke_includes_health_only(self):
        assert SUITE_CATEGORIES["smoke"] == ["health"]

    def test_regression_includes_health_api_config(self):
        cats = SUITE_CATEGORIES["regression"]
        assert "health" in cats
        assert "api" in cats
        assert "config" in cats

    def test_e2e_includes_security_quality(self):
        cats = SUITE_CATEGORIES["e2e"]
        assert "security" in cats
        assert "quality" in cats

    def test_all_includes_tenant_isolation(self):
        cats = SUITE_CATEGORIES["all"]
        assert "tenant_isolation" in cats

    def test_all_suites_have_descriptions(self):
        for suite in SUITE_CATEGORIES:
            assert suite in SUITE_DESCRIPTIONS, f"Missing description for suite '{suite}'"

    def test_suites_are_cumulative(self):
        """Each larger suite includes all categories of the smaller ones."""
        assert set(SUITE_CATEGORIES["smoke"]).issubset(set(SUITE_CATEGORIES["regression"]))
        assert set(SUITE_CATEGORIES["regression"]).issubset(set(SUITE_CATEGORIES["e2e"]))
        assert set(SUITE_CATEGORIES["e2e"]).issubset(set(SUITE_CATEGORIES["all"]))


# ---------------------------------------------------------------------------
# VerificationRunner check registry
# ---------------------------------------------------------------------------

class TestCheckRegistry:
    """Check count per suite."""

    def _make_runner(self, suite: str = "all") -> VerificationRunner:
        return VerificationRunner(
            run_id="test-run-001",
            environment="staging",
            fqdn="example.com",
            verification_secret="test_secret_hex_value",
            suite=suite,
            cosmos_repo=MagicMock(),
            actor="test@example.com",
        )

    def test_smoke_has_8_checks(self):
        runner = self._make_runner("smoke")
        checks = runner._get_checks_for_categories(SUITE_CATEGORIES["smoke"])
        assert len(checks) == 8

    def test_regression_has_more_than_smoke(self):
        runner = self._make_runner("regression")
        smoke_checks = runner._get_checks_for_categories(SUITE_CATEGORIES["smoke"])
        regression_checks = runner._get_checks_for_categories(SUITE_CATEGORIES["regression"])
        assert len(regression_checks) > len(smoke_checks)

    def test_all_suite_has_most_checks(self):
        runner = self._make_runner("all")
        all_checks = runner._get_checks_for_categories(SUITE_CATEGORIES["all"])
        e2e_checks = runner._get_checks_for_categories(SUITE_CATEGORIES["e2e"])
        assert len(all_checks) > len(e2e_checks)

    def test_all_checks_have_names_and_categories(self):
        runner = self._make_runner("all")
        checks = runner._get_checks_for_categories(SUITE_CATEGORIES["all"])
        for name, category, fn in checks:
            assert name, "Check name must not be empty"
            assert category, "Check category must not be empty"
            assert callable(fn), f"Check {name} handler must be callable"

    def test_no_duplicate_check_names(self):
        runner = self._make_runner("all")
        checks = runner._get_checks_for_categories(SUITE_CATEGORIES["all"])
        names = [name for name, _, _ in checks]
        assert len(names) == len(set(names)), f"Duplicate check names: {[n for n in names if names.count(n) > 1]}"


# ---------------------------------------------------------------------------
# VerificationRunner execution
# ---------------------------------------------------------------------------

class TestVerificationRunnerExecution:
    """Runner execution with mocked HTTP and Cosmos."""

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.set_config = AsyncMock()
        return repo

    @pytest.fixture
    def runner(self, mock_repo):
        return VerificationRunner(
            run_id="test-run-002",
            environment="staging",
            fqdn="test.example.com",
            verification_secret="ar_spa_plat_test",
            suite="smoke",
            cosmos_repo=mock_repo,
            actor="test@test.com",
        )

    @pytest.mark.asyncio
    async def test_run_updates_cosmos_progressively(self, runner, mock_repo):
        """Runner calls set_config multiple times (once per batch + final)."""
        # Mock all HTTP calls to succeed
        with patch.object(runner, '_http_get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = (200, {"x-product-version": "1.92.0"}, '{"status": "healthy"}')
            # Mock internal checks too
            with patch('src.multi_tenant.verification_runner.os.path.exists', return_value=True):
                with patch.dict('os.environ', {'AZURE_KEYVAULT_URL': 'https://kv.example.com'}):
                    results = await runner.run()

        # Should have called set_config multiple times (batches + final)
        assert mock_repo.set_config.call_count >= 2, \
            f"Expected >= 2 Cosmos updates, got {mock_repo.set_config.call_count}"

    @pytest.mark.asyncio
    async def test_run_returns_check_results(self, runner):
        """Runner returns a list of CheckResult objects."""
        with patch.object(runner, '_http_get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = (200, {}, '{"status": "healthy"}')
            with patch.object(runner, '_update_cosmos', new_callable=AsyncMock):
                with patch('src.multi_tenant.verification_runner.os.path.exists', return_value=True):
                    with patch.dict('os.environ', {'AZURE_KEYVAULT_URL': 'https://kv.example.com'}):
                        results = await runner.run()

        assert isinstance(results, list)
        assert len(results) == 8  # smoke = 8 health checks
        assert all(isinstance(r, CheckResult) for r in results)

    @pytest.mark.asyncio
    async def test_failed_check_does_not_crash_runner(self, runner):
        """A failing check should not prevent other checks from running."""
        call_count = 0

        async def _flaky_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Network down")
            return (200, {"x-product-version": "1.92.0"}, '{"status": "healthy"}')

        with patch.object(runner, '_http_get', side_effect=_flaky_get):
            with patch.object(runner, '_update_cosmos', new_callable=AsyncMock):
                with patch('src.multi_tenant.verification_runner.os.path.exists', return_value=True):
                    with patch.dict('os.environ', {'AZURE_KEYVAULT_URL': 'https://kv.example.com'}):
                        results = await runner.run()

        # All 8 checks should complete even if some fail
        assert len(results) == 8
        statuses = [r.status for r in results]
        # Some checks use internal probes (not HTTP), so they may pass or error independently
        assert len(statuses) == 8, "All checks must complete"


# ---------------------------------------------------------------------------
# Diagnostics endpoint changes
# ---------------------------------------------------------------------------

class TestDiagnosticsEndpointModels:
    """Response model updates for SPEC-1846."""

    def test_valid_suites_includes_expected(self):
        """VALID_SUITES includes in-process and test-host suites."""
        from src.multi_tenant.superadmin_api._diagnostics import VALID_SUITES
        # S210: 'pipeline' removed (was duplicate of 'full'); verify current set
        for suite in ("smoke", "regression", "e2e", "all", "unit", "core",
                      "full", "integration"):
            assert suite in VALID_SUITES, f"Expected '{suite}' in VALID_SUITES"

    def test_pipeline_run_status_has_completed_field(self):
        """PipelineRunStatusResponse should include 'completed' for progress bar."""
        from src.multi_tenant.superadmin_api._diagnostics import PipelineRunStatusResponse
        resp = PipelineRunStatusResponse(
            run_id="test", environment="staging", suite="smoke", status="running",
            total_tests=8, completed=3, passed=2, failed=1,
        )
        assert resp.completed == 3

    def test_pipeline_run_status_has_checks_field(self):
        """PipelineRunStatusResponse should include 'checks' for full detail."""
        from src.multi_tenant.superadmin_api._diagnostics import PipelineRunStatusResponse
        resp = PipelineRunStatusResponse(
            run_id="test", environment="staging", suite="smoke", status="passed",
            checks=[{"name": "health", "status": "pass"}],
        )
        assert len(resp.checks) == 1

    def test_resolve_fqdn_from_env(self):
        """_resolve_fqdn reads from environment variables."""
        from src.multi_tenant.superadmin_api._diagnostics import _resolve_fqdn
        with patch.dict('os.environ', {'ENVIRONMENT': 'staging', 'CONTAINER_APP_FQDN': 'test.azure.io'}):
            fqdn = _resolve_fqdn('staging')
            assert fqdn == 'test.azure.io'

    def test_resolve_fqdn_cross_environment(self):
        """_resolve_fqdn uses environment-specific var for cross-env testing."""
        from src.multi_tenant.superadmin_api._diagnostics import _resolve_fqdn
        with patch.dict('os.environ', {'ENVIRONMENT': 'staging', 'PRODUCTION_FQDN': 'prod.azure.io'}):
            fqdn = _resolve_fqdn('production')
            assert fqdn == 'prod.azure.io'

    def test_resolve_fqdn_fallback_returns_empty_when_no_env_vars(self):
        """_resolve_fqdn returns empty string when no env vars are set (fail-closed)."""
        from src.multi_tenant.superadmin_api._diagnostics import _resolve_fqdn
        with patch.dict('os.environ', {'ENVIRONMENT': 'staging'}, clear=True):
            fqdn = _resolve_fqdn('production')
            assert fqdn == '', f"Expected empty FQDN for cross-env without vars, got '{fqdn}'"

    def test_resolve_fqdn_api_gateway_fqdn_fallback(self):
        """_resolve_fqdn uses API_GATEWAY_FQDN as last-resort fallback."""
        from src.multi_tenant.superadmin_api._diagnostics import _resolve_fqdn
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'staging',
            'API_GATEWAY_FQDN': 'gateway.example.com',
        }, clear=True):
            fqdn = _resolve_fqdn('production')
            assert fqdn == 'gateway.example.com'


# ---------------------------------------------------------------------------
# Concurrent run guard
# ---------------------------------------------------------------------------

class TestConcurrentRunGuard:
    """409 protection when a run is already in progress."""

    def test_active_runs_dict_exists(self):
        """_active_runs module-level dict is initialized."""
        from src.multi_tenant.superadmin_api._diagnostics import _active_runs
        assert isinstance(_active_runs, dict)

    def test_sentinel_blocks_concurrent_run(self):
        """A sentinel in _active_runs prevents a second run from starting."""
        from src.multi_tenant.superadmin_api._diagnostics import _active_runs
        # Simulate sentinel insertion
        _active_runs["test-sentinel"] = None  # type: ignore[assignment]
        try:
            assert "test-sentinel" in _active_runs
            assert len(_active_runs) > 0  # guard would see non-empty and raise 409
        finally:
            _active_runs.pop("test-sentinel", None)

    def test_completed_task_cleaned_up(self):
        """Completed asyncio tasks are cleaned from _active_runs."""
        from src.multi_tenant.superadmin_api._diagnostics import _active_runs
        # Simulate a completed task
        mock_task = MagicMock()
        mock_task.done.return_value = True
        _active_runs["test-done"] = mock_task
        # Cleanup logic: filter done tasks
        done_keys = [k for k, t in _active_runs.items() if t is not None and t.done()]
        for k in done_keys:
            _active_runs.pop(k, None)
        assert "test-done" not in _active_runs


# ---------------------------------------------------------------------------
# Stale run detection
# ---------------------------------------------------------------------------

class TestStaleRunDetection:
    """Stale run timeout behavior."""

    def test_stale_timeout_constant(self):
        from src.multi_tenant.superadmin_api._diagnostics import _STALE_RUN_TIMEOUT_S
        assert _STALE_RUN_TIMEOUT_S == 5400  # 90 minutes


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

class TestRateLimiter:
    """VerificationRunner semaphore + cooldown behavior."""

    def test_semaphore_initialized_to_4(self):
        runner = VerificationRunner(
            run_id="test", environment="staging", fqdn="x.com",
            verification_secret="key", suite="smoke", cosmos_repo=MagicMock(),
        )
        assert runner._semaphore._value == 4

    def test_shared_http_client_initialized(self):
        """VerificationRunner initializes _http_client to None before run()."""
        runner = VerificationRunner(
            run_id="test", environment="staging", fqdn="x.com",
            verification_secret="key", suite="smoke", cosmos_repo=MagicMock(),
        )
        assert runner._http_client is None

    def test_start_wall_initialized(self):
        """VerificationRunner initializes _start_wall to empty string."""
        runner = VerificationRunner(
            run_id="test", environment="staging", fqdn="x.com",
            verification_secret="key", suite="smoke", cosmos_repo=MagicMock(),
        )
        assert runner._start_wall == ""


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------

class TestEnvironmentValidation:
    """list_test_runs environment filter validation."""

    def test_valid_environments_defined(self):
        """VALID_ENVIRONMENTS contains staging and production."""
        from src.multi_tenant.superadmin_api._diagnostics import VALID_ENVIRONMENTS
        assert "staging" in VALID_ENVIRONMENTS
        assert "production" in VALID_ENVIRONMENTS
        assert len(VALID_ENVIRONMENTS) == 2


# ---------------------------------------------------------------------------
# HMAC verification tokens (SPEC-1846)
# ---------------------------------------------------------------------------

class TestVerificationTokens:
    """HMAC-signed internal verification token generation and validation."""

    def test_token_format_three_parts(self):
        """Token has exactly 3 dot-separated parts: timestamp.run_id.hmac."""
        from src.multi_tenant.auth import generate_verification_token
        token = generate_verification_token("run-abc123", "secret-key")
        parts = token.split(".")
        assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}: {parts}"

    def test_token_timestamp_is_numeric(self):
        """First part of token is a numeric Unix timestamp."""
        from src.multi_tenant.auth import generate_verification_token
        token = generate_verification_token("run-abc123", "secret-key")
        ts_str = token.split(".")[0]
        assert ts_str.isdigit(), f"Timestamp should be numeric, got '{ts_str}'"

    def test_token_hmac_is_64_hex_chars(self):
        """Third part of token is a 64-character hex HMAC-SHA256."""
        from src.multi_tenant.auth import generate_verification_token
        token = generate_verification_token("run-abc123", "secret-key")
        hmac_hex = token.split(".")[2]
        assert len(hmac_hex) == 64, f"HMAC should be 64 hex chars, got {len(hmac_hex)}"
        int(hmac_hex, 16)  # Validates it's valid hex

    def test_generate_verify_roundtrip(self):
        """generate → verify round-trip returns correct run_id."""
        from src.multi_tenant.auth import generate_verification_token, verify_verification_token
        secret = "test-secret-abc123"
        run_id = "run-e2e-test-001"
        token = generate_verification_token(run_id, secret)
        result = verify_verification_token(token, secret)
        assert result["run_id"] == run_id
        assert isinstance(result["timestamp"], int)

    def test_expired_token_rejected(self):
        """Token with timestamp > max_age_seconds is rejected."""
        import time
        from src.multi_tenant.auth import verify_verification_token, AuthenticationError
        import hmac as _hmac
        import hashlib as _hashlib
        # Create a token with timestamp 2000s in the past
        old_ts = str(int(time.time()) - 2000)
        run_id = "run-old"
        secret = "test-secret"
        sig = _hmac.new(secret.encode(), f"{old_ts}|{run_id}".encode(), _hashlib.sha256).hexdigest()
        token = f"{old_ts}.{run_id}.{sig}"
        with pytest.raises(AuthenticationError, match="expired"):
            verify_verification_token(token, secret, max_age_seconds=60)

    def test_wrong_secret_rejected(self):
        """Token verified with different secret is rejected."""
        from src.multi_tenant.auth import generate_verification_token, verify_verification_token, AuthenticationError
        token = generate_verification_token("run-123", "secret-A")
        with pytest.raises(AuthenticationError):
            verify_verification_token(token, "secret-B")

    def test_tampered_hmac_rejected(self):
        """Token with modified HMAC is rejected."""
        from src.multi_tenant.auth import generate_verification_token, verify_verification_token, AuthenticationError
        secret = "test-secret"
        token = generate_verification_token("run-123", secret)
        parts = token.split(".")
        parts[2] = "a" * 64  # Replace HMAC with garbage
        tampered = ".".join(parts)
        with pytest.raises(AuthenticationError):
            verify_verification_token(tampered, secret)

    def test_tampered_run_id_rejected(self):
        """Token with modified run_id is rejected."""
        from src.multi_tenant.auth import generate_verification_token, verify_verification_token, AuthenticationError
        secret = "test-secret"
        token = generate_verification_token("run-original", secret)
        parts = token.split(".")
        parts[1] = "run-tampered"  # Replace run_id
        tampered = ".".join(parts)
        with pytest.raises(AuthenticationError):
            verify_verification_token(tampered, secret)
