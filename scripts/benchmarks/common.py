"""Shared utilities for GT-KB benchmark scripts.

Each benchmark module is read-only and produces a ``BenchmarkResult`` with
optional per-dimension breakdown. ``write_run_outputs()`` emits one JSON file
and one markdown summary per run under ``.gtkb-state/benchmarks/<run_id>/``.

The idempotency key is the SHA-256 hash of the input window + the benchmark IDs
present in the run. Two runs with identical inputs over identical commits
produce identical keys; this lets ``compare`` subcommands detect drift cheaply.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class BenchmarkResult:
    """One benchmark observation.

    ``value`` is the headline scalar (rate, count, ratio). ``dimensions``
    breaks the value down by category (e.g., per-artifact-type rates for the
    linkage heat map). ``source_query`` documents the exact query that produced
    the value so a reviewer can reproduce it.
    """

    run_id: str
    benchmark_id: str
    window_start: str
    window_end: str
    value: float
    dimensions: dict[str, Any] = field(default_factory=dict)
    source_commit: str | None = None
    source_query: str | None = None
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_run_id() -> str:
    """UTC timestamp run id, format ``YYYYMMDD-HHMMSS``."""
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def _resolve_project_root(project_root: Path | str | None) -> Path:
    if project_root is None:
        return Path(__file__).resolve().parents[2]
    return Path(project_root).resolve()


def benchmark_output_dir(run_id: str, project_root: Path | str | None = None) -> Path:
    """Return (and create) the output directory for a benchmark run."""
    root = _resolve_project_root(project_root)
    out = root / ".gtkb-state" / "benchmarks" / run_id
    out.mkdir(parents=True, exist_ok=True)
    return out


_COMMIT_CACHE: dict[Path, str | None] = {}


def current_source_commit(project_root: Path | str | None = None) -> str | None:
    """Resolve ``HEAD`` SHA for the run's source_commit field.

    Returns None if git is unavailable or the call fails. Read-only.
    """
    root = _resolve_project_root(project_root).resolve()
    if root in _COMMIT_CACHE:
        return _COMMIT_CACHE[root]

    val = None
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            val = out.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    _COMMIT_CACHE[root] = val
    return val


def compute_idempotency_key(
    *,
    window_start: str,
    window_end: str,
    benchmark_ids: list[str],
    source_commit: str | None = None,
) -> str:
    """Stable hash over the run's defining inputs.

    Two runs over the same window with the same benchmark set on the same
    commit produce the same key. ``source_commit=None`` is folded in as the
    literal string ``"none"`` so the function never raises.
    """
    payload = {
        "window_start": window_start,
        "window_end": window_end,
        "benchmark_ids": sorted(benchmark_ids),
        "source_commit": source_commit or "none",
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _format_markdown(results: list[BenchmarkResult], idempotency_key: str) -> str:
    if not results:
        return chr(10).join(["# GT-KB benchmark run (empty)", "", "No benchmarks produced results.", ""])
    first = results[0]
    lines = [
        f"# GT-KB benchmark run {first.run_id}",
        "",
        f"- window_start: `{first.window_start}`",
        f"- window_end: `{first.window_end}`",
        f"- source_commit: `{first.source_commit or 'unknown'}`",
        f"- idempotency_key: `{idempotency_key}`",
        f"- generated_at: `{first.generated_at}`",
        "",
        "## Results",
        "",
        "| Benchmark | Value | Dimensions |",
        "| --- | --- | --- |",
    ]
    for r in results:
        dim_summary = ", ".join(f"{k}={v}" for k, v in (r.dimensions or {}).items()) or "-"
        lines.append(f"| `{r.benchmark_id}` | {r.value} | {dim_summary} |")
    lines.append("")
    return chr(10).join(lines)


def write_run_outputs(
    run_id: str,
    results: list[BenchmarkResult],
    *,
    project_root: Path | str | None = None,
) -> dict[str, Path]:
    """Emit ``run.json`` and ``summary.md`` under the run directory.

    Returns a dict with ``json_path`` and ``markdown_path`` keys.
    """
    out_dir = benchmark_output_dir(run_id, project_root=project_root)
    ids = [r.benchmark_id for r in results]
    if results:
        window_start = results[0].window_start
        window_end = results[0].window_end
        source_commit = results[0].source_commit
    else:
        window_start = window_end = ""
        source_commit = None
    key = compute_idempotency_key(
        window_start=window_start,
        window_end=window_end,
        benchmark_ids=ids,
        source_commit=source_commit,
    )
    payload = {
        "run_id": run_id,
        "idempotency_key": key,
        "results": [r.to_dict() for r in results],
    }
    json_path = out_dir / "run.json"
    md_path = out_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_format_markdown(results, key), encoding="utf-8")
    return {"json_path": json_path, "markdown_path": md_path}
