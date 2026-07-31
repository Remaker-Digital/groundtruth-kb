"""Platform tests for benchmark: harness_observed_scorecard."""

# ruff: noqa: E402  # sys.path.insert(REPO) must precede scripts.benchmarks import

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.benchmarks import cli
from scripts.benchmarks import harness_observed_scorecard as bm
from scripts.benchmarks.common import BenchmarkResult, write_run_outputs

PAST = "2024-01-01T00:00:00+00:00"
FUTURE = "2027-01-01T00:00:00+00:00"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _append_jsonl(path: Path, *payloads: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for payload in payloads:
        lines.append(payload if isinstance(payload, str) else json.dumps(payload))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bridge_file(root: Path, name: str, status: str, harness_id: str, identity: str) -> None:
    bridge = root / "bridge" / name
    bridge.parent.mkdir(parents=True, exist_ok=True)
    bridge.write_text(
        "\n".join(
            [
                status,
                f"author_identity: {identity}",
                f"author_harness_id: {harness_id}",
                "",
                "# Verdict",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_scorecard_reads_dispatch_failures_diagnostics_and_bridge_chains(tmp_path: Path) -> None:
    poller = tmp_path / ".gtkb-state" / "bridge-poller"
    _write_json(
        poller / "dispatch-state.json",
        {
            "recipients": {
                "loyal-opposition:D": {
                    "circuit_breaker_tripped": False,
                    "last_result": "no_pending",
                    "last_launch": {
                        "launched": True,
                        "exit_code": 0,
                        "verdict_latency_seconds": 12.5,
                    },
                }
            }
        },
    )
    _append_jsonl(
        poller / "dispatch-failures.jsonl",
        {
            "recipient": "loyal-opposition:D",
            "reason": "previous_launch_failed",
            "error_type": "fatal_worker_output_marker",
            "matched_markers": [{"label": "max_turn_exhaustion"}],
            "ts": "2026-07-04T06:10:34+00:00",
        },
        "not json",
    )
    _append_jsonl(
        poller / "dispatch-diagnostic-post.jsonl",
        {
            "recipient": "loyal-opposition:D",
            "verdict_latency_seconds": 15.0,
            "ts": "2026-07-04T06:11:00+00:00",
        },
    )
    _bridge_file(tmp_path, "gtkb-demo-001.md", "GO", "D", "loyal-opposition/ollama")
    _bridge_file(tmp_path, "gtkb-demo-002.md", "VERIFIED", "A", "prime-builder/codex")
    _bridge_file(tmp_path, "gtkb-demo-002-draft.md", "NO-GO", "B", "loyal-opposition/claude")

    result = bm.run(PAST, FUTURE, tmp_path)

    assert isinstance(result, BenchmarkResult)
    assert result.benchmark_id == bm.BENCHMARK_ID
    assert result.value == 1.0
    assert result.dimensions["advisory_only"] is True
    assert result.dimensions["mutation_boundaries"] == {
        "membase_mutation": False,
        "bridge_mutation": False,
        "dispatcher_ranking_mutation": False,
        "harness_eligibility_mutation": False,
    }
    harness_d = result.dimensions["harnesses"]["D"]
    assert harness_d["launch_count"] == 1
    assert harness_d["successful_exit_count"] == 1
    assert harness_d["failure_reasons"]["previous_launch_failed"] == 1
    assert harness_d["failure_classes"]["max_turn_exhaustion"] == 1
    assert harness_d["verdict_latency_seconds"]["median"] == 13.75
    assert result.dimensions["harnesses"]["A"]["latest_bridge_status_counts"]["VERIFIED"] == 1
    assert result.dimensions["summary"]["malformed_jsonl_record_count"] == 1
    assert result.dimensions["summary"]["bridge_file_count"] == 2


def test_scorecard_handles_missing_sources_gracefully(tmp_path: Path) -> None:
    result = bm.run(PAST, FUTURE, tmp_path)

    assert isinstance(result, BenchmarkResult)
    assert result.value == 0.0
    assert result.dimensions["summary"]["candidate_harness_count"] == 0
    assert ".gtkb-state/bridge-poller/dispatch-state.json" in result.dimensions["summary"]["missing_sources"]
    assert "bridge/*-NNN.md" in result.dimensions["summary"]["missing_sources"]


def test_scorecard_is_registered_with_benchmark_cli() -> None:
    assert bm.BENCHMARK_ID in cli.BENCHMARK_MODULES


def test_scorecard_output_writing(tmp_path: Path) -> None:
    result = bm.run(PAST, FUTURE, tmp_path)
    paths = write_run_outputs(result.run_id, [result], project_root=tmp_path)

    payload = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    markdown = paths["markdown_path"].read_text(encoding="utf-8")

    assert payload["run_id"] == result.run_id
    assert payload["results"][0]["benchmark_id"] == bm.BENCHMARK_ID
    assert "harness_observed_scorecard" in markdown
