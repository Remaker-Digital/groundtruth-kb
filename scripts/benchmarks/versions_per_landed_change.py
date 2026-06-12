"""Benchmark: Versions per Landed Change.

Calculates the average number of bridge proposal/report versions filed per unique
bridge document thread within the specified time window.

Read-only.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "versions_per_landed_change"

_BRIDGE_FILE_PATTERN = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")


def run(window_start: str, window_end: str, project_root: Path | str | None = None) -> BenchmarkResult:
    root = Path(project_root or Path(__file__).resolve().parents[2])
    bridge_dir = root / "bridge"

    # Parse ISO times to datetime objects in UTC
    t_start = datetime.fromisoformat(window_start)
    if t_start.tzinfo is None:
        t_start = t_start.replace(tzinfo=timezone.utc)
    t_end = datetime.fromisoformat(window_end)
    if t_end.tzinfo is None:
        t_end = t_end.replace(tzinfo=timezone.utc)

    total_versions = 0
    unique_slugs = set()

    if bridge_dir.exists():
        for f in bridge_dir.glob("*.md"):
            match = _BRIDGE_FILE_PATTERN.match(f.name)
            if not match:
                continue

            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue

            if t_start <= mtime <= t_end:
                total_versions += 1
                unique_slugs.add(match.group("slug"))

    value = (total_versions / len(unique_slugs)) if unique_slugs else 0.0

    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 2),
        dimensions={
            "total_versions": total_versions,
            "unique_documents": len(unique_slugs),
        },
        source_commit=current_source_commit(root),
        source_query="Average count of version files per unique document slug in E:\\GT-KB\\bridge\\",
    )
