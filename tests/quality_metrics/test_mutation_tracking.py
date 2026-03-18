"""Tests for mutation score tracking (SPEC-1842/WI-1498).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import pytest

from src.quality_metrics.mutation_tracking import (
    parse_mutmut_results,
    compute_mutation_score,
    identify_oracle_gap_modules,
    format_mutation_summary,
)


# ---------------------------------------------------------------------------
# parse_mutmut_results
# ---------------------------------------------------------------------------


class TestParseMutmutResults:
    def test_standard_summary_line(self) -> None:
        output = "282 mutants were generated. Of those, 200 were killed, 70 survived, and 12 timed out."
        result = parse_mutmut_results(output)
        assert result["killed"] == 200
        assert result["survived"] == 70
        assert result["timeout"] == 12
        assert result["total"] == 282

    def test_partial_output(self) -> None:
        output = "50 killed, 10 survived"
        result = parse_mutmut_results(output)
        assert result["killed"] == 50
        assert result["survived"] == 10
        assert result["timeout"] == 0
        assert result["total"] == 60

    def test_empty_output(self) -> None:
        result = parse_mutmut_results("")
        assert result == {"killed": 0, "survived": 0, "timeout": 0, "total": 0}


# ---------------------------------------------------------------------------
# compute_mutation_score
# ---------------------------------------------------------------------------


class TestComputeMutationScore:
    def test_perfect_score(self) -> None:
        assert compute_mutation_score(100, 0) == 1.0

    def test_zero_score(self) -> None:
        assert compute_mutation_score(0, 100) == 0.0

    def test_typical_score(self) -> None:
        assert compute_mutation_score(7, 3) == 0.7

    def test_no_mutants(self) -> None:
        assert compute_mutation_score(0, 0) == 0.0

    def test_timeout_excluded_from_denominator(self) -> None:
        # 7 killed, 3 survived, 10 timeout → score based on killed+survived only
        assert compute_mutation_score(7, 3, timeout=10) == 0.7


# ---------------------------------------------------------------------------
# identify_oracle_gap_modules
# ---------------------------------------------------------------------------


class TestIdentifyOracleGapModules:
    def test_detects_high_coverage_low_mutation(self) -> None:
        coverage = {"module_a": 0.95, "module_b": 0.60}
        mutation = {"module_a": 0.30, "module_b": 0.80}
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 1
        assert gaps[0]["module"] == "module_a"
        assert gaps[0]["oracle_gap"] == 0.65

    def test_no_gaps_when_mutation_is_good(self) -> None:
        coverage = {"module_a": 0.90}
        mutation = {"module_a": 0.85}
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 0

    def test_no_gaps_when_coverage_is_low(self) -> None:
        coverage = {"module_a": 0.50}
        mutation = {"module_a": 0.10}
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 0

    def test_sorted_by_oracle_gap_descending(self) -> None:
        coverage = {"a": 0.90, "b": 0.95, "c": 0.85}
        mutation = {"a": 0.40, "b": 0.20, "c": 0.45}
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 3
        assert gaps[0]["module"] == "b"  # 0.75 gap
        assert gaps[1]["module"] == "a"  # 0.50 gap
        assert gaps[2]["module"] == "c"  # 0.40 gap

    def test_missing_mutation_data_treated_as_zero(self) -> None:
        coverage = {"module_a": 0.90}
        mutation = {}  # No mutation data
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 1
        assert gaps[0]["mutation_score"] == 0.0

    def test_custom_thresholds(self) -> None:
        coverage = {"module_a": 0.70}
        mutation = {"module_a": 0.30}
        # Default thresholds: coverage >= 0.80, mutation < 0.50 → no gap
        gaps = identify_oracle_gap_modules(coverage, mutation)
        assert len(gaps) == 0
        # Custom thresholds: coverage >= 0.60, mutation < 0.40
        gaps = identify_oracle_gap_modules(
            coverage, mutation, coverage_threshold=0.60, mutation_threshold=0.40
        )
        assert len(gaps) == 1


# ---------------------------------------------------------------------------
# format_mutation_summary
# ---------------------------------------------------------------------------


class TestFormatMutationSummary:
    def test_format_output(self) -> None:
        results = {"killed": 200, "survived": 70, "timeout": 12, "total": 282}
        summary = format_mutation_summary(results, 0.7407)
        assert "74.1%" in summary
        assert "200 killed" in summary
        assert "70 survived" in summary
        assert "12 timed out" in summary
