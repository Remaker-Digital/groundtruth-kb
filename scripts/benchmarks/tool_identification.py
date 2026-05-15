"""Benchmark 3: Tool Identification.

Measures the rate at which recent MemBase insertions carry a skill-attribution
marker in ``changed_by``. Attribution markers follow the pattern
``<role>/<harness>/<id>`` (e.g., ``prime-builder/claude/B``).

Value = fraction of recent insertions with an attribution-shaped changed_by.

Read-only.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "tool_identification"

_ATTRIBUTION = re.compile(r"^(prime-builder|loyal-opposition|owner)/[a-z]+/[A-Z0-9]+$")


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    per_table = {"specifications": [0, 0], "work_items": [0, 0], "deliberations": [0, 0]}
    if db_path.exists():
        with sqlite3.connect(str(db_path)) as con:
            for table in per_table:
                rows = con.execute(
                    "SELECT COALESCE(changed_by, '') FROM " + table + " "
                    "WHERE changed_at >= ? AND changed_at <= ?",
                    (window_start, window_end),
                ).fetchall()
                for (by,) in rows:
                    per_table[table][1] += 1
                    if _ATTRIBUTION.match(by.strip()):
                        per_table[table][0] += 1
    with_attr = sum(v[0] for v in per_table.values())
    total = sum(v[1] for v in per_table.values())
    value = (with_attr / total) if total else 0.0
    dims = {t: {"with_attribution": v[0], "total": v[1]} for t, v in per_table.items()}
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 4),
        dimensions=dims,
        source_commit=current_source_commit(root),
        source_query="changed_at-windowed scan of changed_by attribution shape",
    )
