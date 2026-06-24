"""Read-only effectiveness observatory report over benchmark run output.

This module consumes an existing ``.gtkb-state/benchmarks/<run_id>/run.json``
payload and writes deterministic advisory outputs next to it:
``effectiveness.json`` and ``effectiveness.md``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.benchmarks.common import benchmark_output_dir
from scripts.benchmarks.metric_registry import MetricDefinition, metric_definitions

JSON_OUTPUT_NAME = "effectiveness.json"
MARKDOWN_OUTPUT_NAME = "effectiveness.md"
SCHEMA_VERSION = 1


class EffectivenessObservatoryError(RuntimeError):
    """Raised when the observatory cannot load or write a benchmark report."""


def run_json_path(run_id: str, project_root: Path | str | None = None) -> Path:
    """Return the expected ``run.json`` path for a benchmark run id."""
    return benchmark_output_dir(run_id, project_root=project_root) / "run.json"


def load_run_payload(run_id: str, project_root: Path | str | None = None) -> dict[str, Any]:
    """Load a benchmark run payload by id."""
    path = run_json_path(run_id, project_root=project_root)
    if not path.is_file():
        raise EffectivenessObservatoryError(f"benchmark run.json not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EffectivenessObservatoryError(f"benchmark run.json is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise EffectivenessObservatoryError(f"benchmark run.json must contain an object: {path}")
    return payload


def _result_by_benchmark(run_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = run_payload.get("results")
    if not isinstance(results, list):
        return {}
    by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict):
            continue
        benchmark_id = result.get("benchmark_id")
        if isinstance(benchmark_id, str) and benchmark_id:
            by_id[benchmark_id] = result
    return by_id


def _observed_metric(definition: MetricDefinition, result: dict[str, Any] | None) -> dict[str, Any]:
    base = definition.to_dict()
    if result is None:
        return {
            **base,
            "availability": "missing",
            "value": None,
            "dimensions": {},
            "source_query": None,
            "source_commit": None,
        }
    dimensions = result.get("dimensions")
    return {
        **base,
        "availability": "available",
        "value": result.get("value"),
        "dimensions": dimensions if isinstance(dimensions, dict) else {},
        "source_query": result.get("source_query"),
        "source_commit": result.get("source_commit"),
    }


def build_effectiveness_payload(run_payload: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic advisory effectiveness payload from ``run.json``."""
    results = _result_by_benchmark(run_payload)
    metrics = [
        _observed_metric(definition, results.get(definition.source_benchmark_id)) for definition in metric_definitions()
    ]
    available = [metric["metric_id"] for metric in metrics if metric["availability"] == "available"]
    missing = [metric["metric_id"] for metric in metrics if metric["availability"] == "missing"]
    benchmark_ids = sorted(results)
    source_commits = sorted(
        {
            str(result.get("source_commit"))
            for result in results.values()
            if isinstance(result.get("source_commit"), str) and result.get("source_commit")
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "advisory_status": "experimental_advisory",
        "source_run": {
            "run_id": run_payload.get("run_id"),
            "idempotency_key": run_payload.get("idempotency_key"),
            "benchmark_ids": benchmark_ids,
            "source_commits": source_commits,
        },
        "summary": {
            "metric_count": len(metrics),
            "available_metric_count": len(available),
            "missing_metric_count": len(missing),
            "available_metrics": available,
            "missing_metrics": missing,
            "gating_authority": False,
        },
        "metrics": metrics,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render a stable markdown effectiveness report."""
    source_run = payload.get("source_run") if isinstance(payload.get("source_run"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), list) else []
    lines = [
        f"# GT-KB effectiveness observatory {source_run.get('run_id', 'unknown')}",
        "",
        f"- idempotency_key: `{source_run.get('idempotency_key', 'unknown')}`",
        f"- advisory_status: `{payload.get('advisory_status', 'experimental_advisory')}`",
        f"- gating_authority: `{str(summary.get('gating_authority', False)).lower()}`",
        f"- available_metrics: `{summary.get('available_metric_count', 0)}`",
        f"- missing_metrics: `{summary.get('missing_metric_count', 0)}`",
        "",
        "## Metrics",
        "",
        "| Metric | Source Benchmark | Availability | Value | Decision Informed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        value = metric.get("value")
        display_value = "" if value is None else str(value)
        lines.append(
            "| `{metric_id}` | `{source}` | {availability} | {value} | {decision} |".format(
                metric_id=metric.get("metric_id", ""),
                source=metric.get("source_benchmark_id", ""),
                availability=metric.get("availability", ""),
                value=display_value,
                decision=str(metric.get("decision_informed", "")).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Guardrails", ""])
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        lines.append(f"### {metric.get('metric_id', '')}")
        guardrails = metric.get("guardrails")
        if isinstance(guardrails, list) and guardrails:
            for guardrail in guardrails:
                lines.append(f"- {guardrail}")
        else:
            lines.append("- No guardrails registered.")
        lines.append("")
    return "\n".join(lines)


def write_effectiveness_outputs(run_id: str, project_root: Path | str | None = None) -> dict[str, Path]:
    """Load a benchmark run and write deterministic effectiveness outputs."""
    payload = build_effectiveness_payload(load_run_payload(run_id, project_root=project_root))
    out_dir = benchmark_output_dir(run_id, project_root=project_root)
    json_path = out_dir / JSON_OUTPUT_NAME
    markdown_path = out_dir / MARKDOWN_OUTPUT_NAME
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return {"json_path": json_path, "markdown_path": markdown_path}
