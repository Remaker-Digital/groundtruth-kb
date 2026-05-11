# tests/test_host/test_runner.py — TestRunner unit tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Tests for test_host.runner — subprocess orchestration, JSON report parsing,
environment building, and composite suite execution.
"""

from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from test_host.cosmos_writer import CosmosWriter, RunState
from test_host.runner import TestRunner
from test_host.suites import SUITE_CONFIGS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_writer():
    """Create a mocked CosmosWriter that tracks state without Cosmos."""
    writer = MagicMock(spec=CosmosWriter)
    writer.state = RunState(
        run_id="run-test123",
        environment="staging",
        suite="unit",
    )
    writer.mark_running = MagicMock()
    writer.set_phase = MagicMock()
    writer.complete_phase = MagicMock()
    writer.add_results = MagicMock()
    writer.update_stdout = MagicMock()
    writer.finalize = MagicMock()
    return writer


@pytest.fixture
def runner(mock_writer):
    """Create a TestRunner with mocked writer."""
    return TestRunner(
        run_id="run-test123",
        suite="unit",
        environment="staging",
        target_url="https://staging.example.com",
        cosmos_writer=mock_writer,
    )


# ---------------------------------------------------------------------------
# Construction and properties
# ---------------------------------------------------------------------------

class TestRunnerConstruction:
    """TestRunner initializes with correct state."""

    def test_run_id(self, runner):
        assert runner.run_id == "run-test123"

    def test_suite(self, runner):
        assert runner.suite == "unit"

    def test_environment(self, runner):
        assert runner.environment == "staging"

    def test_target_url(self, runner):
        assert runner.target_url == "https://staging.example.com"

    def test_not_cancelled_initially(self, runner):
        assert runner._cancelled is False

    def test_no_active_process(self, runner):
        assert runner._process is None


# ---------------------------------------------------------------------------
# Environment variable building
# ---------------------------------------------------------------------------

class TestBuildEnv:
    """_build_env() creates subprocess environment correctly."""

    def test_inherits_current_env(self, runner):
        env = runner._build_env()
        # Should contain at least PATH from the parent process
        assert "PATH" in env

    def test_sets_prod_url_from_target(self, runner):
        env = runner._build_env()
        assert env["PROD_URL"] == "https://staging.example.com"

    def test_sets_staging_url_from_target(self, runner):
        env = runner._build_env()
        assert env["STAGING_URL"] == "https://staging.example.com"

    def test_propagates_staging_keys(self, runner):
        """When staging keys are in the environment, they propagate."""
        with patch.dict(os.environ, {"STAGING_SPA_KEY": "test-spa-key"}):
            env = runner._build_env()
            assert env["STAGING_SPA_KEY"] == "test-spa-key"

    def test_env_overrides_applied(self, mock_writer):
        """Custom env_overrides are merged into the subprocess env."""
        runner = TestRunner(
            run_id="run-1", suite="unit", environment="staging",
            target_url="https://example.com", cosmos_writer=mock_writer,
            env_overrides={"CUSTOM_VAR": "custom_value"},
        )
        env = runner._build_env()
        assert env["CUSTOM_VAR"] == "custom_value"

    def test_env_overrides_take_precedence(self, mock_writer):
        """Overrides take precedence over inherited env."""
        with patch.dict(os.environ, {"STAGING_URL": "old"}):
            runner = TestRunner(
                run_id="run-1", suite="unit", environment="staging",
                target_url="https://example.com", cosmos_writer=mock_writer,
                env_overrides={"STAGING_URL": "overridden"},
            )
            env = runner._build_env()
            assert env["STAGING_URL"] == "overridden"

    def test_e2e_suite_clears_live_spa_base_url(self, runner):
        """E2E suites clear LIVE_SPA_BASE_URL so conftest starts local Vite."""
        e2e_config = SUITE_CONFIGS["e2e"]
        with patch.dict(os.environ, {"LIVE_SPA_BASE_URL": "https://should-be-cleared"}):
            env = runner._build_env(e2e_config)
            assert "LIVE_SPA_BASE_URL" not in env

    def test_e2e_suite_sets_api_proxy_target(self, runner):
        """E2E suites set API_PROXY_TARGET so Vite proxies /api/* to staging."""
        e2e_config = SUITE_CONFIGS["e2e"]
        env = runner._build_env(e2e_config)
        assert env["API_PROXY_TARGET"] == "https://staging.example.com"

    def test_non_e2e_suite_sets_live_spa_base_url(self, runner):
        """Non-E2E suites set LIVE_SPA_BASE_URL to deployed SPA."""
        unit_config = SUITE_CONFIGS["unit"]
        env = runner._build_env(unit_config)
        assert env["LIVE_SPA_BASE_URL"] == "https://staging.example.com/admin/standalone"

    def test_no_config_sets_live_spa_base_url(self, runner):
        """When no config is passed, LIVE_SPA_BASE_URL defaults to deployed SPA."""
        env = runner._build_env()
        assert env["LIVE_SPA_BASE_URL"] == "https://staging.example.com/admin/standalone"

    def test_e2e_suite_keeps_prod_url(self, runner):
        """E2E suites still set PROD_URL for conftest reachability checks."""
        e2e_config = SUITE_CONFIGS["e2e"]
        env = runner._build_env(e2e_config)
        assert env["PROD_URL"] == "https://staging.example.com"


# ---------------------------------------------------------------------------
# JSON report parsing
# ---------------------------------------------------------------------------

class TestJsonReportParsing:
    """_parse_json_report() converts pytest-json-report to TestResults."""

    def _write_report(self, tmp_path, tests):
        """Helper: write a pytest-json-report format file."""
        report = {"tests": tests}
        p = tmp_path / "report.json"
        p.write_text(json.dumps(report), encoding="utf-8")
        return p

    def test_parse_passed_test(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_bar",
            "outcome": "passed",
            "duration": 0.123,
        }])
        runner._parse_json_report(report, "unit")
        runner.cosmos.add_results.assert_called_once()
        batch = runner.cosmos.add_results.call_args[0][0]
        assert len(batch) == 1
        assert batch[0].name == "test_foo::test_bar"
        assert batch[0].status == "pass"
        assert batch[0].latency_ms == 123.0

    def test_parse_failed_test_with_detail(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_fail",
            "outcome": "failed",
            "duration": 0.05,
            "call": {"longrepr": "AssertionError: expected True"},
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert batch[0].status == "fail"
        assert "AssertionError" in batch[0].detail

    def test_parse_skipped_test(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_skip",
            "outcome": "skipped",
            "duration": 0.001,
            "setup": {"longrepr": "Skipped: not applicable"},
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert batch[0].status == "skip"

    def test_parse_xfailed_maps_to_skip(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_xfail",
            "outcome": "xfailed",
            "duration": 0.01,
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert batch[0].status == "skip"

    def test_parse_xpassed_maps_to_pass(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_xpass",
            "outcome": "xpassed",
            "duration": 0.01,
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert batch[0].status == "pass"

    def test_detail_truncated_to_500(self, runner, tmp_path):
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_long",
            "outcome": "failed",
            "duration": 0.01,
            "call": {"longrepr": "x" * 1000},
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert len(batch[0].detail) <= 500

    def test_batching_at_50(self, runner, tmp_path):
        """Results are batched in groups of 50."""
        tests = [
            {"nodeid": f"tests/unit/test.py::test_{i}", "outcome": "passed", "duration": 0.01}
            for i in range(75)
        ]
        report = self._write_report(tmp_path, tests)
        runner._parse_json_report(report, "unit")
        # 75 results = 1 batch of 50 + 1 batch of 25
        assert runner.cosmos.add_results.call_count == 2

    def test_node_id_shortening(self, runner, tmp_path):
        """Long paths are shortened to file::test format."""
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/multi_tenant/auth/test_deep.py::TestClass::test_method",
            "outcome": "passed",
            "duration": 0.01,
        }])
        runner._parse_json_report(report, "core")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert batch[0].name == "test_deep::test_method"

    def test_corrupt_report_handled(self, runner, tmp_path):
        """Corrupt JSON report is handled gracefully."""
        p = tmp_path / "bad_report.json"
        p.write_text("not valid json", encoding="utf-8")
        # Should not raise
        runner._parse_json_report(p, "unit")

    def test_dict_longrepr_handled(self, runner, tmp_path):
        """Dict-style longrepr (reprcrash format) is parsed."""
        report = self._write_report(tmp_path, [{
            "nodeid": "tests/unit/test_foo.py::test_dict_repr",
            "outcome": "failed",
            "duration": 0.01,
            "call": {
                "longrepr": {
                    "reprcrash": {"message": "TypeError: cannot compare"},
                    "reprtraceback": {},
                },
            },
        }])
        runner._parse_json_report(report, "unit")
        batch = runner.cosmos.add_results.call_args[0][0]
        assert "TypeError" in batch[0].detail


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

class TestRunnerSummary:
    """_summary() returns correct run metadata."""

    def test_summary_fields(self, runner):
        runner.cosmos.state.status = "passed"
        runner.cosmos.state.passed = 10
        runner.cosmos.state.failed = 0
        runner.cosmos.state.completed = 10
        runner.cosmos.state.phases_completed = ["unit"]
        summary = runner._summary()
        assert summary["run_id"] == "run-test123"
        assert summary["suite"] == "unit"
        assert summary["status"] == "passed"
        assert summary["total_tests"] == 10
        assert summary["passed"] == 10


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------

class TestRunnerCancel:
    """cancel() sets the cancelled flag and finalizes."""

    @pytest.mark.asyncio
    async def test_cancel_sets_flag(self, runner):
        await runner.cancel()
        assert runner._cancelled is True

    @pytest.mark.asyncio
    async def test_cancel_finalizes_as_error(self, runner):
        await runner.cancel()
        runner.cosmos.finalize.assert_called_once_with(status="error")

    @pytest.mark.asyncio
    async def test_cancel_with_no_process(self, runner):
        """Cancel when no subprocess is running doesn't raise."""
        await runner.cancel()  # Should not raise


# ---------------------------------------------------------------------------
# Suite routing
# ---------------------------------------------------------------------------

class TestSuiteRouting:
    """run() routes to single or composite execution based on config."""

    @pytest.mark.asyncio
    async def test_unknown_suite_returns_error(self, mock_writer):
        runner = TestRunner(
            run_id="r", suite="nonexistent", environment="staging",
            target_url="https://x.com", cosmos_writer=mock_writer,
        )
        result = await runner.run()
        assert "error" in result
        mock_writer.finalize.assert_called_once_with(status="error")

    @pytest.mark.asyncio
    async def test_composite_calls_multiple_phases(self, mock_writer):
        """Composite suite iterates over composite_suites."""
        runner = TestRunner(
            run_id="r", suite="pipeline", environment="staging",
            target_url="https://x.com", cosmos_writer=mock_writer,
        )
        # Mock _run_pytest and _run_locust to avoid subprocess calls
        runner._run_pytest = AsyncMock()
        runner._run_locust = AsyncMock()

        await runner.run()

        # Should set phases for each sub-suite
        assert mock_writer.set_phase.call_count >= len(
            SUITE_CONFIGS["pipeline"].composite_suites
        )
        assert mock_writer.finalize.called
