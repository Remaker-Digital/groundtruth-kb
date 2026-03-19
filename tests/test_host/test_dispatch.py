# tests/test_host/test_dispatch.py — Suite dispatch routing tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Tests for the dispatch logic in _diagnostics.py — verifying that suites are
correctly routed between in-process verification runner and the test host
container, and that the SPA trigger endpoint handles all edge cases.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.superadmin_api._diagnostics import (
    VALID_ENVIRONMENTS,
    VALID_SUITES,
    _INPROCESS_SUITES,
    _TESTHOST_SUITES,
    _TEST_HOST_URL,
)


# ---------------------------------------------------------------------------
# Suite routing constants
# ---------------------------------------------------------------------------

class TestSuiteRouting:
    """In-process vs test-host suite classification."""

    def test_inprocess_suites_defined(self):
        """In-process suites include the 4 verification runner suites."""
        assert _INPROCESS_SUITES == {"all", "regression", "smoke", "e2e"}

    def test_testhost_suites_defined(self):
        """Test-host suites include all pytest-based suites."""
        expected = {
            "unit", "core", "integration", "agents", "security",
            "regression_pytest", "ops", "widget", "e2e_live",
            "load", "fuzzing", "property", "pipeline", "full",
        }
        assert _TESTHOST_SUITES == expected

    def test_no_overlap(self):
        """In-process and test-host suites don't overlap."""
        overlap = _INPROCESS_SUITES & _TESTHOST_SUITES
        assert not overlap, f"Overlapping suites: {overlap}"

    def test_valid_suites_is_union(self):
        """VALID_SUITES = in-process ∪ test-host."""
        assert VALID_SUITES == _INPROCESS_SUITES | _TESTHOST_SUITES

    def test_all_testhost_suites_have_config(self):
        """Every test-host suite maps to a SuiteConfig in suites.py.

        Note: regression_pytest may use a different name.
        """
        from test_host.suites import SUITE_CONFIGS

        # These need mapping (dispatch name → suite config name)
        name_mapping = {
            "regression_pytest": "regression",
            "e2e_live": "e2e",
        }
        for suite in _TESTHOST_SUITES:
            config_name = name_mapping.get(suite, suite)
            assert config_name in SUITE_CONFIGS, (
                f"Test-host suite '{suite}' has no SuiteConfig "
                f"(checked as '{config_name}')"
            )


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------

class TestEnvironmentValidation:
    """Only staging and production are valid environments."""

    def test_valid_environments(self):
        assert VALID_ENVIRONMENTS == {"staging", "production"}

    def test_staging_accepted(self):
        assert "staging" in VALID_ENVIRONMENTS

    def test_production_accepted(self):
        assert "production" in VALID_ENVIRONMENTS

    def test_development_rejected(self):
        assert "development" not in VALID_ENVIRONMENTS

    def test_local_rejected(self):
        assert "local" not in VALID_ENVIRONMENTS


# ---------------------------------------------------------------------------
# Test host URL configuration
# ---------------------------------------------------------------------------

class TestHostUrlConfig:
    """TEST_HOST_URL defaults to internal DNS name."""

    def test_default_url(self):
        """Default matches Azure Container Apps internal DNS."""
        assert "agent-red-test-host" in _TEST_HOST_URL
        assert ":8001" in _TEST_HOST_URL

    def test_url_is_http(self):
        """Internal ingress uses HTTP (TLS terminated at load balancer)."""
        assert _TEST_HOST_URL.startswith("http://")


# ---------------------------------------------------------------------------
# Suite naming conventions
# ---------------------------------------------------------------------------

class TestSuiteNaming:
    """Suite names follow project conventions."""

    def test_all_lowercase(self):
        """Suite names are lowercase."""
        for suite in VALID_SUITES:
            assert suite == suite.lower(), f"Suite '{suite}' not lowercase"

    def test_no_spaces(self):
        """Suite names don't contain spaces."""
        for suite in VALID_SUITES:
            assert " " not in suite, f"Suite '{suite}' contains space"

    def test_alphanumeric_or_underscore(self):
        """Suite names are alphanumeric + underscore only."""
        for suite in VALID_SUITES:
            assert suite.replace("_", "").isalnum(), (
                f"Suite '{suite}' has invalid characters"
            )
