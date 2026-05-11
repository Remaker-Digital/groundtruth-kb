"""Tests for CQ-4 DeepEval scaffold — validates the adapter and runner.

DeepEval may not be installed, so tests validate graceful degradation
and the adapter logic without requiring the full DeepEval package.

Run:
    pytest tests/evaluation/test_deepeval_scaffold.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from evaluation.deepeval_config import (
    DEEPEVAL_AVAILABLE,
    EVAL_MODEL,
    FAITHFULNESS_THRESHOLD,
    HALLUCINATION_THRESHOLD,
    RELEVANCY_THRESHOLD,
    create_deepeval_test_cases,
    create_metrics,
    run_deepeval_evaluation,
)


class TestDeepEvalConfig:
    """DeepEval scaffold configuration."""

    def test_de_01_thresholds_are_sensible(self):
        """DE-01: Metric thresholds are in valid range."""
        assert 0.0 <= FAITHFULNESS_THRESHOLD <= 1.0
        assert 0.0 <= RELEVANCY_THRESHOLD <= 1.0
        assert 0.0 <= HALLUCINATION_THRESHOLD <= 1.0

    def test_de_02_eval_model_configured(self):
        """DE-02: Evaluation model is set."""
        assert EVAL_MODEL is not None
        assert len(EVAL_MODEL) > 0

    def test_de_03_availability_flag_is_boolean(self):
        """DE-03: DEEPEVAL_AVAILABLE is a boolean."""
        assert isinstance(DEEPEVAL_AVAILABLE, bool)


class TestDeepEvalAdapter:
    """DeepEval adapter — golden dataset → test cases."""

    def test_de_04_empty_scenarios_returns_empty(self):
        """DE-04: Empty scenario list returns empty test cases."""
        cases = create_deepeval_test_cases([], {})
        assert cases == []

    def test_de_05_missing_responses_skipped(self):
        """DE-05: Scenarios without responses are skipped."""
        scenarios = [
            {"id": "GD-001", "customer_message": "Hi", "knowledge_context": []},
        ]
        # No response for GD-001
        cases = create_deepeval_test_cases(scenarios, {})
        # Should return empty (or skip) since no actual response
        assert len(cases) == 0

    def test_de_06_empty_response_skipped(self):
        """DE-06: Scenarios with empty response strings are skipped."""
        scenarios = [
            {"id": "GD-001", "customer_message": "Hi", "knowledge_context": []},
        ]
        responses = {"GD-001": {"response": ""}}
        cases = create_deepeval_test_cases(scenarios, responses)
        assert len(cases) == 0


class TestDeepEvalRunner:
    """DeepEval runner — graceful degradation."""

    def test_de_07_unavailable_returns_status(self):
        """DE-07: When DeepEval not installed, returns unavailable status."""
        if DEEPEVAL_AVAILABLE:
            pytest.skip("DeepEval is installed — testing unavailable path not possible")

        result = run_deepeval_evaluation([])
        assert result["status"] in ("unavailable", "empty")

    def test_de_08_empty_test_cases_returns_empty(self):
        """DE-08: Empty test case list returns empty status."""
        if DEEPEVAL_AVAILABLE:
            result = run_deepeval_evaluation([])
            assert result["status"] == "empty"
        else:
            result = run_deepeval_evaluation([])
            assert result["status"] == "unavailable"

    def test_de_09_create_metrics_graceful(self):
        """DE-09: create_metrics returns list (empty if DeepEval unavailable)."""
        metrics = create_metrics()
        assert isinstance(metrics, list)
        if DEEPEVAL_AVAILABLE:
            assert len(metrics) == 3  # faithfulness, relevancy, hallucination
        else:
            assert len(metrics) == 0
