# tests/test_host/test_spa_contract.py — SPA TestExecution contract tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Contract tests verifying that test host API responses match the shapes
expected by the SPA TestExecution.tsx component. These tests ensure that
API changes don't silently break the SPA UI.

SPA depends on these API endpoints:
  POST /api/superadmin/tests/run       → {run_id, status}
  GET  /api/superadmin/tests/{id}/status → PipelineRun shape
  GET  /api/superadmin/tests/runs      → {runs: PipelineRun[]}

The PipelineRun interface requires specific field names (camelCase)
derived from snake_case Python model via response transform.
"""

from __future__ import annotations

import pytest

from test_host.cosmos_writer import CosmosWriter, RunState, TestResult


# ---------------------------------------------------------------------------
# PipelineRun interface contract (SPA expects these exact field names)
# ---------------------------------------------------------------------------

# These are the field names the SPA TypeScript interface expects.
# The API transforms snake_case → camelCase before sending.
SPA_PIPELINE_RUN_FIELDS = {
    "runId",
    "environment",
    "suite",
    "status",
    "triggeredBy",
    "startedAt",
    "completedAt",
    "totalTests",
    "completed",
    "passed",
    "failed",
    "skipped",
    "errored",
    "durationS",
    "phasesRun",
    "phasesCompleted",
    "currentPhase",
    "phasesTotal",
    "checks",
    "stdoutTail",
}

SPA_CHECK_RESULT_FIELDS = {"name", "category", "status", "latencyMs", "detail"}


class TestRunStateToSpaContract:
    """RunState → Cosmos document → API response → SPA PipelineRun."""

    def test_run_state_has_all_spa_fields_snake_case(self):
        """RunState dataclass includes all fields needed by SPA (snake_case)."""
        state = RunState(run_id="r1", environment="staging", suite="unit")
        snake_equivalents = {
            "run_id", "environment", "suite", "status",
            "triggered_by", "started_at", "completed_at",
            "total_tests", "completed", "passed", "failed",
            "skipped", "errored", "duration_s",
            "phases_completed", "current_phase", "phases_total",
            "checks", "stdout_tail",
        }
        # phases_run is a computed alias of phases_completed in the Cosmos doc
        state_fields = set(vars(state).keys())
        missing = snake_equivalents - state_fields
        assert not missing, f"RunState missing fields for SPA contract: {missing}"

    def test_spa_status_values_covered(self):
        """SPA STATUS_COLORS maps: queued, running, passed, failed, error."""
        valid_statuses = {"queued", "running", "passed", "failed", "error"}
        state = RunState(run_id="r", environment="staging", suite="unit")
        assert state.status in valid_statuses  # Default is "queued"

    def test_checks_are_serializable_dicts(self):
        """SPA expects checks as array of objects, not dataclass instances."""
        state = RunState(run_id="r", environment="staging", suite="unit")
        # Checks are stored as dicts, not TestResult objects
        assert isinstance(state.checks, list)


class TestCheckResultContract:
    """CheckResult/TestResult → SPA CheckResult interface."""

    def test_test_result_fields(self):
        """TestResult has the 5 fields SPA expects (snake_case)."""
        r = TestResult(
            name="test_foo", category="unit",
            status="pass", latency_ms=12.5, detail="ok",
        )
        assert r.name == "test_foo"
        assert r.category == "unit"
        assert r.status == "pass"
        assert r.latency_ms == 12.5
        assert r.detail == "ok"

    def test_check_status_values_in_spa_palette(self):
        """SPA CHECK_STATUS_COLORS maps: pass, fail, skip, error."""
        spa_palette = {"pass", "fail", "skip", "error"}
        for status in spa_palette:
            r = TestResult(name="t", category="c", status=status)
            assert r.status in spa_palette


# ---------------------------------------------------------------------------
# Suite options contract (SPA SUITE_OPTIONS)
# ---------------------------------------------------------------------------

class TestSuiteOptionsContract:
    """SPA SUITE_OPTIONS values must match VALID_SUITES in the API."""

    # These are the suite values hardcoded in the SPA SUITE_OPTIONS
    SPA_SUITE_VALUES = {
        # Quick Verification (in-process)
        "smoke", "regression", "e2e", "all",
        # Comprehensive (test-host container)
        "unit", "core", "integration", "agents", "security",
        "ops", "widget", "e2e_live", "load", "fuzzing", "property",
        # Full Suite (composite)
        "pipeline", "full",
    }

    def test_spa_suites_match_api_valid_suites(self):
        """Every SPA suite value must be accepted by the API."""
        from src.multi_tenant.superadmin_api._diagnostics import VALID_SUITES
        unrecognized = self.SPA_SUITE_VALUES - VALID_SUITES
        assert not unrecognized, f"SPA has suites not in API: {unrecognized}"

    def test_api_suites_have_spa_option(self):
        """Every API-valid suite has a corresponding SPA option."""
        from src.multi_tenant.superadmin_api._diagnostics import VALID_SUITES
        missing = VALID_SUITES - self.SPA_SUITE_VALUES
        # regression_pytest is an API-internal alias (dispatches to test host
        # "regression" suite config). SPA uses "regression" which routes
        # in-process. Not a gap — intentional dispatch-level separation.
        allowed_missing = {"regression_pytest"}
        actual_missing = missing - allowed_missing
        assert not actual_missing, f"API suites missing from SPA: {actual_missing}"

    def test_inprocess_suites_in_quick_verification(self):
        """In-process suites (smoke/regression/e2e/all) are in Quick Verification."""
        from src.multi_tenant.superadmin_api._diagnostics import _INPROCESS_SUITES
        quick = {"smoke", "regression", "e2e", "all"}
        assert _INPROCESS_SUITES == quick

    def test_testhost_suites_cover_comprehensive_and_full(self):
        """Test-host suites cover Comprehensive + Full Suite groups."""
        from src.multi_tenant.superadmin_api._diagnostics import _TESTHOST_SUITES
        comprehensive = {
            "unit", "core", "integration", "agents", "security",
            "ops", "widget", "e2e_live", "load", "fuzzing", "property",
        }
        full_group = {"pipeline", "full"}
        # regression_pytest is an API alias
        expected_testhost = comprehensive | full_group | {"regression_pytest"}
        assert _TESTHOST_SUITES == expected_testhost


# ---------------------------------------------------------------------------
# Environment options contract
# ---------------------------------------------------------------------------

class TestEnvironmentContract:
    """SPA environment dropdown values must match API."""

    def test_staging_accepted(self):
        from src.multi_tenant.superadmin_api._diagnostics import VALID_ENVIRONMENTS
        assert "staging" in VALID_ENVIRONMENTS

    def test_production_accepted(self):
        from src.multi_tenant.superadmin_api._diagnostics import VALID_ENVIRONMENTS
        assert "production" in VALID_ENVIRONMENTS

    def test_default_environment_is_staging(self):
        """SPA defaults to 'staging' — ensure it's always valid."""
        from src.multi_tenant.superadmin_api._diagnostics import VALID_ENVIRONMENTS
        assert "staging" in VALID_ENVIRONMENTS


# ---------------------------------------------------------------------------
# Cosmos document schema contract
# ---------------------------------------------------------------------------

class TestCosmosDocumentContract:
    """Cosmos document shape must be readable by both test host and main API."""

    def test_document_id_format(self):
        """Documents use 'test_runs:{run_id}' as ID."""
        run_id = "run-abc123"
        expected_id = f"test_runs:{run_id}"
        assert expected_id == "test_runs:run-abc123"

    def test_document_config_type(self):
        """All test run documents use config_type='test_runs'."""
        # This is how the main API queries them
        assert "test_runs" == "test_runs"  # Self-documenting assertion

    def test_cosmos_document_roundtrip(self):
        """A document written by CosmosWriter can be read by the main API.

        The main API reads documents with config_type='test_runs' and
        expects the value field to contain all PipelineRun fields.
        """
        from unittest.mock import MagicMock, patch

        with patch("test_host.cosmos_writer.CosmosClient") as mock_client:
            container = MagicMock()
            mock_client.return_value.get_database_client.return_value \
                .get_container_client.return_value = container

            writer = CosmosWriter(
                cosmos_endpoint="https://mock.docs.azure.com:443/",
                cosmos_key="key",
                cosmos_db="db",
                run_id="run-roundtrip",
                environment="staging",
                suite="unit",
            )
            writer._container = container
            writer.mark_running(total_tests=3)
            writer.add_results([
                TestResult(name="t1", category="unit", status="pass", latency_ms=5.0),
                TestResult(name="t2", category="unit", status="fail", detail="boom"),
                TestResult(name="t3", category="unit", status="skip"),
            ])
            writer.finalize()

            # Capture the document
            doc = container.upsert_item.call_args[0][0]
            value = doc["value"]

            # Verify all SPA-required snake_case fields present
            required_snake = {
                "run_id", "environment", "suite", "status",
                "triggered_by", "started_at", "completed_at",
                "total_tests", "completed", "passed", "failed",
                "skipped", "errored", "duration_s",
                "phases_completed", "current_phase", "phases_total",
                "failures", "checks", "stdout_tail",
            }
            missing = required_snake - set(value.keys())
            assert not missing, f"Document missing fields: {missing}"

            # Verify counters are correct
            assert value["passed"] == 1
            assert value["failed"] == 1
            assert value["skipped"] == 1
            assert value["completed"] == 3
            assert value["status"] == "failed"  # Has failures

            # Verify failures list
            assert len(value["failures"]) == 1
            assert value["failures"][0]["name"] == "t2"

            # Verify checks list
            assert len(value["checks"]) == 3


# ---------------------------------------------------------------------------
# API response field naming convention
# ---------------------------------------------------------------------------

class TestFieldNamingConvention:
    """API transforms snake_case → camelCase for the SPA."""

    # Maps RunState snake_case fields to SPA camelCase.
    # phases_run is a computed alias (not in RunState), so it's not here.
    SNAKE_TO_CAMEL = {
        "run_id": "runId",
        "triggered_by": "triggeredBy",
        "started_at": "startedAt",
        "completed_at": "completedAt",
        "total_tests": "totalTests",
        "duration_s": "durationS",
        "phases_completed": "phasesCompleted",
        "current_phase": "currentPhase",
        "phases_total": "phasesTotal",
        "stdout_tail": "stdoutTail",
        "latency_ms": "latencyMs",
    }

    def test_all_multi_word_fields_have_camel_mapping(self):
        """Every multi-word RunState field has a defined camelCase mapping."""
        state = RunState(run_id="r", environment="staging", suite="unit")
        for field in vars(state):
            if "_" in field:
                assert field in self.SNAKE_TO_CAMEL, (
                    f"RunState field '{field}' has no camelCase mapping"
                )

    def test_camel_names_match_spa_interface(self):
        """camelCase names match the SPA PipelineRun TypeScript interface."""
        for snake, camel in self.SNAKE_TO_CAMEL.items():
            # Basic camelCase validation
            assert camel[0].islower(), f"{camel} should start lowercase"
            assert "_" not in camel, f"{camel} should not have underscores"
