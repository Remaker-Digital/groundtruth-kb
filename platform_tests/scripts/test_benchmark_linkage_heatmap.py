"""Platform tests for benchmark: linkage_heatmap.

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

from scripts.benchmarks import linkage_heatmap as bm
from scripts.benchmarks.common import BenchmarkResult, write_run_outputs

PAST = "2024-01-01T00:00:00+00:00"
FUTURE = "2027-01-01T00:00:00+00:00"
EMPTY_START = "1990-01-01T00:00:00+00:00"
EMPTY_END = "1990-01-02T00:00:00+00:00"


def test_linkage_heatmap_basic_run():
    result = bm.run(PAST, FUTURE, REPO)
    assert isinstance(result, BenchmarkResult)
    assert result.benchmark_id == bm.BENCHMARK_ID
    assert result.window_start == PAST
    assert result.window_end == FUTURE
    assert isinstance(result.value, (int, float))
    assert isinstance(result.dimensions, dict)


def test_linkage_heatmap_idempotency_dimensions():
    a = bm.run(PAST, FUTURE, REPO)
    b = bm.run(PAST, FUTURE, REPO)
    assert a.dimensions == b.dimensions
    assert a.value == b.value


def test_linkage_heatmap_expected_dimension_keys():
    result = bm.run(PAST, FUTURE, REPO)
    assert "matrix" in result.dimensions
    for src in ("SPEC", "WI", "ADR_DCL_GOV", "DELIB", "BRIDGE"):
        assert src in result.dimensions["matrix"]


def test_linkage_heatmap_empty_window_graceful():
    result = bm.run(EMPTY_START, EMPTY_END, REPO)
    assert isinstance(result, BenchmarkResult)
    assert isinstance(result.value, (int, float))


def test_linkage_heatmap_output_writing(tmp_path):
    result = bm.run(PAST, FUTURE, tmp_path)
    paths = write_run_outputs(result.run_id, [result], project_root=tmp_path)
    assert paths["json_path"].exists()
    assert paths["markdown_path"].exists()
    payload = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    assert payload["run_id"] == result.run_id
    assert "idempotency_key" in payload
    assert len(payload["results"]) == 1
