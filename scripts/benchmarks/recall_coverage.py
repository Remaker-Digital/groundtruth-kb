"""Benchmark 2: Recall Evidence Coverage.

For each mutation in the window across (specifications, work_items, tests),
measure whether its change_reason cites prior state (DELIB / SPEC / WI
identifiers). The benchmark reports the fraction of mutations with at least
one prior-state citation.

Value = mutations_with_evidence / total_mutations.

Read-only.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "recall_coverage"

_CITATION = re.compile(r"(?:DELIB|SPEC|WI|ADR|DCL|GOV|PB)-[A-Z0-9-]+")


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    per_table = {"specifications": [0, 0], "work_items": [0, 0], "tests": [0, 0]}
    if db_path.exists():
        with sqlite3.connect(str(db_path)) as con:
            for table in per_table:
                rows = con.execute(
                    "SELECT COALESCE(change_reason, '') FROM " + table + " WHERE changed_at >= ? AND changed_at <= ?",
                    (window_start, window_end),
                ).fetchall()
                for (reason,) in rows:
                    per_table[table][1] += 1
                    if _CITATION.search(reason):
                        per_table[table][0] += 1
    total_with = sum(v[0] for v in per_table.values())
    total_all = sum(v[1] for v in per_table.values())
    value = (total_with / total_all) if total_all else 0.0
    dims = {t: {"with_evidence": v[0], "total": v[1]} for t, v in per_table.items()}
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 4),
        dimensions=dims,
        source_commit=current_source_commit(root),
        source_query="changed_at-windowed scan of change_reason across spec, work_item, and test tables",
    )
