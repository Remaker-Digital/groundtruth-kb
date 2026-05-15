"""Benchmark 5: Advisory-to-Action Latency.

Scans LO advisory artifacts (INSIGHTS-*.md ctimes; bridge ADVISORY entries)
and measures the median wall-clock time from advisory filing to the first
Prime acknowledgement (a subsequent bridge thread that cites the advisory).

Value = median latency in hours over the window. ``None`` is returned as 0.0
with dimensions["sample_size"] = 0 when no qualifying advisory exists.

Read-only.
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "advisory_latency"

_ADVISORY_REF = re.compile(r"INSIGHTS-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-[A-Z0-9-]+\.md")


def _bridge_files(root):
    bridge_dir = root / "bridge"
    if not bridge_dir.exists():
        return []
    return sorted(bridge_dir.glob("*-[0-9][0-9][0-9].md"))


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    dropbox = root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    advisories = []
    if dropbox.exists():
        for f in dropbox.glob("INSIGHTS-*.md"):
            try:
                ctime = f.stat().st_mtime
            except OSError:
                continue
            advisories.append((f.name, ctime))
    bridge_paths = _bridge_files(root)
    bridge_refs = []
    for bf in bridge_paths:
        try:
            text = bf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        matches = _ADVISORY_REF.findall(text)
        if not matches:
            continue
        try:
            bf_time = bf.stat().st_mtime
        except OSError:
            continue
        for m in matches:
            bridge_refs.append((m, bf_time))
    latencies_hours = []
    matched = 0
    for adv_name, adv_time in advisories:
        first_ack = None
        for ref_name, ref_time in bridge_refs:
            if ref_name == adv_name and ref_time >= adv_time:
                if first_ack is None or ref_time < first_ack:
                    first_ack = ref_time
        if first_ack is not None:
            latencies_hours.append((first_ack - adv_time) / 3600.0)
            matched += 1
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
            "matched_advisories": matched,
            "sample_size": len(latencies_hours),
        },
        source_commit=current_source_commit(root),
        source_query="INSIGHTS mtimes vs bridge file mtimes (first reference)",
    )
