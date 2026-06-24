"""Tests for the benchmark effectiveness observatory."""

# ruff: noqa: E402  # sys.path.insert(REPO) must precede scripts.benchmarks import

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.benchmarks import cli as benchmark_cli
from scripts.benchmarks.common import BenchmarkResult, write_run_outputs
from scripts.benchmarks.effectiveness_observatory import (
    build_effectiveness_payload,
    render_markdown,
    write_effectiveness_outputs,
)
from scripts.benchmarks.metric_registry import metric_definitions, registry_payload


def _write_run(tmp_path: Path, results: list[BenchmarkResult]) -> str:
    run_id = results[0].run_id if results else "empty-run"
    write_run_outputs(run_id, results, project_root=tmp_path)
    return run_id


def _result(
    run_id: str, benchmark_id: str, value: float, dimensions: dict[str, object] | None = None
) -> BenchmarkResult:
    return BenchmarkResult(
        run_id=run_id,
        benchmark_id=benchmark_id,
        window_start="2026-01-01T00:00:00+00:00",
        window_end="2026-01-02T00:00:00+00:00",
        value=value,
        dimensions=dimensions or {},
        source_commit="abc123",
        source_query=f"fixture query for {benchmark_id}",
        generated_at="2026-01-02T00:00:00+00:00",
    )


def test_metric_registry_has_guardrails_and_advisory_status() -> None:
    definitions = metric_definitions()
    assert definitions
    assert {definition.source_benchmark_id for definition in definitions} >= {
        "advisory_latency",
        "linkage_heatmap",
        "assertion_signal_noise",
        "versions_per_landed_change",
    }
    for definition in definitions:
        assert definition.status == "experimental_advisory"
        assert definition.decision_informed
        assert definition.guardrails
        assert definition.known_failure_modes
    assert all(entry["status"] == "experimental_advisory" for entry in registry_payload())


def test_effectiveness_payload_is_deterministic_for_same_run(tmp_path: Path) -> None:
    run_id = "fixture-run"
    _write_run(
        tmp_path,
        [
            _result(run_id, "advisory_latency", 12.5, {"sample_size": 4}),
            _result(run_id, "linkage_heatmap", 0.75, {"matrix": {"SPEC": {"WI": 1}}}),
            _result(run_id, "assertion_signal_noise", 0.9, {"sample_size": 10}),
            _result(run_id, "versions_per_landed_change", 2.0, {"unique_documents": 3}),
        ],
    )
    paths_a = write_effectiveness_outputs(run_id, project_root=tmp_path)
    json_a = paths_a["json_path"].read_text(encoding="utf-8")
    paths_b = write_effectiveness_outputs(run_id, project_root=tmp_path)
    assert json_a == paths_b["json_path"].read_text(encoding="utf-8")
    payload = json.loads(json_a)
    assert payload["summary"]["available_metric_count"] == 4
    assert payload["summary"]["missing_metric_count"] == 0
    assert payload["summary"]["gating_authority"] is False


def test_missing_benchmark_degrades_without_inventing_value(tmp_path: Path) -> None:
    run_id = "partial-run"
    _write_run(tmp_path, [_result(run_id, "advisory_latency", 5.0, {"sample_size": 1})])
    paths = write_effectiveness_outputs(run_id, project_root=tmp_path)
    payload = json.loads(paths["json_path"].read_text(encoding="utf-8"))
    missing = [metric for metric in payload["metrics"] if metric["availability"] == "missing"]
    assert missing
    assert all(metric["value"] is None for metric in missing)
    assert "artifact_linkage_density" in payload["summary"]["missing_metrics"]


def test_markdown_carries_source_run_and_guardrails(tmp_path: Path) -> None:
    run_id = "markdown-run"
    _write_run(tmp_path, [_result(run_id, "advisory_latency", 3.0)])
    payload = build_effectiveness_payload(
        json.loads((tmp_path / ".gtkb-state" / "benchmarks" / run_id / "run.json").read_text(encoding="utf-8"))
    )
    markdown = render_markdown(payload)
    assert f"GT-KB effectiveness observatory {run_id}" in markdown
    assert "gating_authority: `false`" in markdown
    assert "## Guardrails" in markdown
    assert "advisory_acknowledgement_latency" in markdown


def test_cli_observatory_writes_output_paths(tmp_path: Path, capsys) -> None:
    run_id = "cli-run"
    _write_run(tmp_path, [_result(run_id, "advisory_latency", 8.0)])
    rc = benchmark_cli.main(["observatory", "--run-id", run_id, "--project-root", str(tmp_path), "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["run_id"] == run_id
    assert Path(out["json_path"]).is_file()
    assert Path(out["markdown_path"]).is_file()
