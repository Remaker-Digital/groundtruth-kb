"""Platform tests for benchmark: advisory_latency.

Each test exercises one independent contract: basic run, idempotency,
dimension keys, empty-window behavior, and output-writing.
"""

# ruff: noqa: E402  # sys.path.insert(REPO) must precede scripts.benchmarks import

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.benchmarks import advisory_latency as bm
from scripts.benchmarks.common import BenchmarkResult, write_run_outputs

PAST = "2024-01-01T00:00:00+00:00"
FUTURE = "2027-01-01T00:00:00+00:00"
EMPTY_START = "1990-01-01T00:00:00+00:00"
EMPTY_END = "1990-01-02T00:00:00+00:00"


def test_advisory_latency_basic_run(tmp_path):
    result = bm.run(PAST, FUTURE, tmp_path)
    assert isinstance(result, BenchmarkResult)
    assert result.benchmark_id == bm.BENCHMARK_ID
    assert result.window_start == PAST
    assert result.window_end == FUTURE
    assert isinstance(result.value, (int, float))
    assert isinstance(result.dimensions, dict)


def test_advisory_latency_idempotency_dimensions(tmp_path):
    a = bm.run(PAST, FUTURE, tmp_path)
    b = bm.run(PAST, FUTURE, tmp_path)
    assert a.dimensions == b.dimensions
    assert a.value == b.value


def test_advisory_latency_expected_dimension_keys(tmp_path):
    result = bm.run(PAST, FUTURE, tmp_path)
    for k in ("advisory_count", "matched_advisories", "sample_size"):
        assert k in result.dimensions


def test_advisory_latency_empty_window_graceful(tmp_path):
    result = bm.run(EMPTY_START, EMPTY_END, tmp_path)
    assert isinstance(result, BenchmarkResult)
    assert isinstance(result.value, (int, float))


def test_advisory_latency_output_writing(tmp_path):
    result = bm.run(PAST, FUTURE, tmp_path)
    paths = write_run_outputs(result.run_id, [result], project_root=tmp_path)
    assert paths["json_path"].exists()
    assert paths["markdown_path"].exists()
    payload = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    assert payload["run_id"] == result.run_id
    assert "idempotency_key" in payload
    assert len(payload["results"]) == 1
