"""Benchmark 4: Deliberation Recall Quality.

Samples up to 50 recent owner-decision deliberations and measures how well a
bounded read-only recall query finds each one. The default benchmark path uses
SQLite MemBase rows only, avoiding live ChromaDB/ONNX semantic embedding work in
platform tests. A live semantic search path remains available only through an
explicit keyword argument.

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
SEARCH_FIELDS = ("id", "title", "summary", "content", "source_ref", "spec_id", "work_item_id", "outcome")


def _load_db(project_root):
    src = project_root / "groundtruth-kb" / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from groundtruth_kb.db import KnowledgeDB

        return KnowledgeDB(project_root / "groundtruth.db")
    except Exception:
        return None


def _deliberation_relation(con: sqlite3.Connection) -> str:
    row = con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'view' AND name = 'current_deliberations'"
    ).fetchone()
    return "current_deliberations" if row else "deliberations"


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _sample_deliberations(db_path: Path, window_start: str, window_end: str) -> list[tuple[str, str]]:
    sample = []
    if not db_path.exists():
        return sample
    with sqlite3.connect(str(db_path)) as con:
        relation = _deliberation_relation(con)
        cur = con.execute(
            f"SELECT id, COALESCE(NULLIF(title, ''), NULLIF(summary, '')) FROM {relation} "
            "WHERE source_type = ? AND changed_at >= ? AND changed_at <= ? "
            "ORDER BY changed_at DESC, id DESC LIMIT ?",
            ("owner_conversation", window_start, window_end, SAMPLE_SIZE),
        )
        sample = [(row[0], row[1] or "") for row in cur.fetchall() if row[1]]
    return sample


def _search_sqlite_deliberations(db_path: Path, query: str, *, limit: int = TOP_K) -> list[str]:
    if not db_path.exists() or not query.strip():
        return []
    pattern = _like_pattern(query.strip())
    where_clause = " OR ".join(f"COALESCE({field}, '') LIKE ? ESCAPE '\\'" for field in SEARCH_FIELDS)
    params = [pattern for _ in SEARCH_FIELDS]
    with sqlite3.connect(str(db_path)) as con:
        relation = _deliberation_relation(con)
        cur = con.execute(
            f"SELECT id FROM {relation} WHERE {where_clause} ORDER BY changed_at DESC, id DESC LIMIT ?",
            [*params, limit],
        )
        return [row[0] for row in cur.fetchall()]


def _search_semantic(root: Path, sample: list[tuple[str, str]]) -> tuple[int, int]:
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
    return hits, failures


def _search_sqlite(db_path: Path, sample: list[tuple[str, str]]) -> tuple[int, int]:
    hits = 0
    failures = 0
    for delib_id, query in sample:
        try:
            top_ids = _search_sqlite_deliberations(db_path, query, limit=TOP_K)
        except sqlite3.Error:
            failures += 1
            continue
        if delib_id in top_ids:
            hits += 1
    return hits, failures


def run(window_start, window_end, project_root=None, *, semantic: bool = False):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    sample = _sample_deliberations(db_path, window_start, window_end)
    hits, failures = _search_semantic(root, sample) if semantic else _search_sqlite(db_path, sample)
    sample_size = len(sample)
    value = (hits / sample_size) if sample_size else 0.0
    search_mode = "semantic search top-3 recall" if semantic else "SQLite LIKE top-3 recall"
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
        source_query=f"recent owner_conversation deliberations; {search_mode}",
    )
