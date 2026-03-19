# tests/test_host/test_cosmos_writer.py — CosmosWriter unit tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Tests for test_host.cosmos_writer — state management, result batching,
throttled upserts, and document schema generation.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from test_host.cosmos_writer import CosmosWriter, RunState, TestResult


# ---------------------------------------------------------------------------
# TestResult dataclass
# ---------------------------------------------------------------------------

class TestTestResultModel:
    """TestResult is a simple data container for individual results."""

    def test_create_minimal(self):
        r = TestResult(name="test_foo", category="unit", status="pass")
        assert r.name == "test_foo"
        assert r.category == "unit"
        assert r.status == "pass"
        assert r.latency_ms == 0.0
        assert r.detail == ""

    def test_create_with_detail(self):
        r = TestResult(
            name="test_bar", category="security",
            status="fail", latency_ms=12.5,
            detail="AssertionError: expected True",
        )
        assert r.latency_ms == 12.5
        assert "AssertionError" in r.detail

    def test_valid_statuses(self):
        """Status values that the system uses."""
        for status in ("pass", "fail", "skip", "error"):
            r = TestResult(name="t", category="c", status=status)
            assert r.status == status


# ---------------------------------------------------------------------------
# RunState dataclass
# ---------------------------------------------------------------------------

class TestRunStateModel:
    """RunState tracks the mutable state of a test run."""

    def test_default_values(self):
        s = RunState(run_id="run-1", environment="staging", suite="unit")
        assert s.status == "queued"
        assert s.triggered_by == "spa-console"
        assert s.total_tests == 0
        assert s.completed == 0
        assert s.passed == 0
        assert s.failed == 0
        assert s.skipped == 0
        assert s.errored == 0
        assert s.duration_s is None
        assert s.phases_completed == []
        assert s.checks == []
        assert s.failures == []

    def test_mutable_counters(self):
        s = RunState(run_id="run-2", environment="staging", suite="core")
        s.passed = 10
        s.failed = 2
        s.completed = 12
        assert s.passed + s.failed == s.completed


# ---------------------------------------------------------------------------
# CosmosWriter — mocked Cosmos client
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_cosmos():
    """Create a CosmosWriter with mocked Cosmos client."""
    with patch("test_host.cosmos_writer.CosmosClient") as mock_client:
        container = MagicMock()
        mock_client.return_value.get_database_client.return_value \
            .get_container_client.return_value = container

        writer = CosmosWriter(
            cosmos_endpoint="https://mock.documents.azure.com:443/",
            cosmos_key="mock-key",
            cosmos_db="test-db",
            run_id="run-abc123",
            environment="staging",
            suite="unit",
        )
        writer._container = container
        yield writer, container


class TestCosmosWriterState:
    """State management before any Cosmos interaction."""

    def test_initial_state(self, mock_cosmos):
        writer, _ = mock_cosmos
        s = writer.state
        assert s.run_id == "run-abc123"
        assert s.environment == "staging"
        assert s.suite == "unit"
        assert s.status == "queued"

    def test_mark_running(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=100, phases_total=3)
        assert writer.state.status == "running"
        assert writer.state.total_tests == 100
        assert writer.state.phases_total == 3
        container.upsert_item.assert_called()

    def test_set_phase(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=50)
        writer.set_phase("core")
        assert writer.state.current_phase == "core"

    def test_complete_phase(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=50)
        writer.set_phase("unit")
        writer.complete_phase("unit")
        assert "unit" in writer.state.phases_completed
        assert writer.state.current_phase == ""

    def test_complete_phase_idempotent(self, mock_cosmos):
        """Completing the same phase twice doesn't duplicate."""
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=50)
        writer.complete_phase("unit")
        writer.complete_phase("unit")
        assert writer.state.phases_completed.count("unit") == 1


class TestCosmosWriterResults:
    """Result accumulation and counter tracking."""

    def test_add_pass_increments_counters(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=10)
        writer.add_results([
            TestResult(name="t1", category="unit", status="pass"),
        ])
        assert writer.state.completed == 1
        assert writer.state.passed == 1

    def test_add_fail_increments_counters_and_failures(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=10)
        writer.add_results([
            TestResult(name="t1", category="unit", status="fail", detail="boom"),
        ])
        assert writer.state.failed == 1
        assert len(writer.state.failures) == 1
        assert writer.state.failures[0]["name"] == "t1"

    def test_add_skip_increments_skipped(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=10)
        writer.add_results([
            TestResult(name="t1", category="unit", status="skip"),
        ])
        assert writer.state.skipped == 1

    def test_add_error_increments_errored_and_failures(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=10)
        writer.add_results([
            TestResult(name="t1", category="unit", status="error"),
        ])
        assert writer.state.errored == 1
        assert len(writer.state.failures) == 1

    def test_batch_accumulation(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=100)
        batch = [
            TestResult(name=f"t{i}", category="unit", status="pass")
            for i in range(25)
        ]
        writer.add_results(batch)
        assert writer.state.completed == 25
        assert writer.state.passed == 25
        assert len(writer.state.checks) == 25

    def test_detail_truncated_to_500(self, mock_cosmos):
        """Long detail strings are truncated at 500 chars."""
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=10)
        writer.add_results([
            TestResult(name="t1", category="unit", status="fail", detail="x" * 1000),
        ])
        stored = writer.state.checks[0]
        assert len(stored["detail"]) == 500


class TestCosmosWriterStdout:
    """Stdout tail management."""

    def test_update_stdout(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.update_stdout("some output")
        assert writer.state.stdout_tail == "some output"

    def test_stdout_truncated_to_2000(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.update_stdout("x" * 5000)
        assert len(writer.state.stdout_tail) == 2000


class TestCosmosWriterFinalize:
    """Finalize sets terminal status and calculates duration."""

    def test_finalize_passed(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=3)
        writer.add_results([
            TestResult(name="t1", category="unit", status="pass"),
            TestResult(name="t2", category="unit", status="pass"),
            TestResult(name="t3", category="unit", status="skip"),
        ])
        writer.finalize()
        assert writer.state.status == "passed"
        assert writer.state.completed_at is not None
        assert writer.state.duration_s is not None
        container.upsert_item.assert_called()

    def test_finalize_failed_on_failures(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=2)
        writer.add_results([
            TestResult(name="t1", category="unit", status="pass"),
            TestResult(name="t2", category="unit", status="fail"),
        ])
        writer.finalize()
        assert writer.state.status == "failed"

    def test_finalize_failed_on_errors(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=1)
        writer.add_results([
            TestResult(name="t1", category="unit", status="error"),
        ])
        writer.finalize()
        assert writer.state.status == "failed"

    def test_finalize_explicit_status_overrides(self, mock_cosmos):
        writer, _ = mock_cosmos
        writer.mark_running(total_tests=1)
        writer.finalize(status="error")
        assert writer.state.status == "error"


class TestCosmosWriterThrottling:
    """Upsert throttling (max once per 2 seconds)."""

    def test_throttled_upsert_skips_frequent_calls(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=100)
        initial_count = container.upsert_item.call_count

        # These should be throttled (within 2s window)
        writer.add_results([TestResult(name="t1", category="c", status="pass")])
        writer.add_results([TestResult(name="t2", category="c", status="pass")])
        writer.add_results([TestResult(name="t3", category="c", status="pass")])

        # At most 1 additional upsert should have happened (throttled)
        assert container.upsert_item.call_count <= initial_count + 1

    def test_finalize_forces_upsert(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=1)
        count_before = container.upsert_item.call_count
        writer.finalize()
        assert container.upsert_item.call_count > count_before


class TestCosmosDocumentSchema:
    """Verify the upserted document matches expected schema."""

    def test_document_has_required_fields(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=1)
        writer.add_results([TestResult(name="t1", category="unit", status="pass")])
        writer.finalize()

        doc = container.upsert_item.call_args[0][0]
        assert doc["id"] == "test_runs:run-abc123"
        assert doc["config_type"] == "test_runs"
        assert doc["config_key"] == "run-abc123"
        assert "value" in doc
        assert doc["version"] == 1
        assert doc["updated_by"] == "test-host"

    def test_value_contains_all_state_fields(self, mock_cosmos):
        writer, container = mock_cosmos
        writer.mark_running(total_tests=1)
        writer.finalize()

        doc = container.upsert_item.call_args[0][0]
        value = doc["value"]
        required = {
            "run_id", "environment", "suite", "status",
            "triggered_by", "started_at", "completed_at",
            "total_tests", "completed", "passed", "failed",
            "skipped", "errored", "duration_s", "current_phase",
            "phases_completed", "phases_total", "phases_run",
            "failures", "checks", "stdout_tail",
        }
        missing = required - set(value.keys())
        assert not missing, f"Missing fields in document value: {missing}"

    def test_failures_capped_at_100(self, mock_cosmos):
        """Document caps failures list at 100 entries."""
        writer, container = mock_cosmos
        writer.mark_running(total_tests=200)
        for i in range(150):
            writer.add_results([
                TestResult(name=f"t{i}", category="unit", status="fail", detail="boom")
            ])
        writer.finalize()

        doc = container.upsert_item.call_args[0][0]
        assert len(doc["value"]["failures"]) <= 100
