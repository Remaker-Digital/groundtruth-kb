"""Benchmark 4: Deliberation Recall Quality.

Samples up to 50 recent owner-decision deliberations and measures how well the
semantic search index recalls each one. For each sampled DELIB, the title or
summary is used as the query and the top-3 search results are inspected. A
recall hit means the original DELIB ID appears in the top-3.

Value = recall@3 over the sample. Reports failure_rate as a dimension.

Read-only.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "deliberation_recall"
SAMPLE_SIZE = 50
TOP_K = 3


def _load_db(project_root):
    src = project_root / "groundtruth-kb" / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from groundtruth_kb.db import KnowledgeDB
        return KnowledgeDB(project_root / "groundtruth.db")
    except Exception:
        return None


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    sample = []
    if db_path.exists():
        with sqlite3.connect(str(db_path)) as con:
            cur = con.execute(
                "SELECT id, COALESCE(title, summary) FROM deliberations "
                "WHERE source_type = ? AND changed_at >= ? AND changed_at <= ? "
                "ORDER BY changed_at DESC LIMIT ?",
                ("owner_conversation", window_start, window_end, SAMPLE_SIZE),
            )
            sample = [(row[0], row[1] or "") for row in cur.fetchall() if row[1]]
    kdb = _load_db(root)
    hits = 0
    failures = 0
    if kdb is not None:
        for delib_id, query in sample:
            try:
                results = kdb.search_deliberations(query, limit=TOP_K)
            except Exception:
                failures += 1
                continue
            top_ids = [r.get("id") for r in (results or [])][:TOP_K]
            if delib_id in top_ids:
                hits += 1
    sample_size = len(sample)
    value = (hits / sample_size) if sample_size else 0.0
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 4),
        dimensions={
            "sample_size": sample_size,
            "hits_at_3": hits,
            "search_failure_rate": round(failures / sample_size, 4) if sample_size else 0.0,
        },
        source_commit=current_source_commit(root),
        source_query="recent owner_conversation deliberations; semantic search top-3 recall",
    )
