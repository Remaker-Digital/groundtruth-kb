"""Benchmark 5: Advisory-to-Action Latency.

Discovers status-bearing numbered bridge ``ADVISORY`` entries and measures the
median wall-clock time from advisory filing to the first later numbered bridge
entry that cites that advisory. Retired dropbox reports are not discovery
inputs.

Value = median latency in hours over the window. ``None`` is returned as 0.0
with dimensions["sample_size"] = 0 when no qualifying advisory exists.

Read-only.
"""

from __future__ import annotations

import statistics
from datetime import datetime
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "advisory_latency"

_NUMBERED_SUFFIX = "-[0-9][0-9][0-9].md"


def _bridge_files(root):
    bridge_dir = root / "bridge"
    if not bridge_dir.exists():
        return []
    return sorted(bridge_dir.glob(f"*{_NUMBERED_SUFFIX}"))


def _first_status(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _window_timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    bridge_paths = _bridge_files(root)
    start_ts = _window_timestamp(window_start)
    end_ts = _window_timestamp(window_end)
    entries: list[tuple[Path, str, float]] = []
    for bf in bridge_paths:
        try:
            text = bf.read_text(encoding="utf-8", errors="ignore")
            bf_time = bf.stat().st_mtime
        except OSError:
            continue
        entries.append((bf, text, bf_time))

    advisories = [
        (path, timestamp)
        for path, text, timestamp in entries
        if _first_status(text) == "ADVISORY" and start_ts <= timestamp <= end_ts
    ]
    latencies_hours = []
    for advisory_path, advisory_time in advisories:
        advisory_ref = advisory_path.relative_to(root).as_posix()
        first_ack: float | None = None
        for candidate_path, text, candidate_time in entries:
            if candidate_path == advisory_path or candidate_time < advisory_time:
                continue
            if advisory_ref not in text and advisory_path.name not in text:
                continue
            if first_ack is None or candidate_time < first_ack:
                first_ack = candidate_time
        if first_ack is not None:
            latencies_hours.append((first_ack - advisory_time) / 3600.0)
    if latencies_hours:
        value = statistics.median(latencies_hours)
    else:
        value = 0.0
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 2),
        dimensions={
            "advisory_count": len(advisories),
            "matched_advisories": len(latencies_hours),
            "sample_size": len(latencies_hours),
        },
        source_commit=current_source_commit(root),
        source_query="numbered bridge ADVISORY mtimes vs later numbered bridge citations",
    )
