"""Benchmark 1: Cross-Artifact Linkage Heat Map.

For each (source_type, target_type) pair in {SPEC, WI, ADR_DCL_GOV, DELIB, BRIDGE},
compute the fraction of source artifacts that reference at least one target
artifact of the given type.

Value = mean of all off-diagonal cells (overall linkage density).
Dimensions = the full 5x5 matrix as nested dict.

Read-only.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "linkage_heatmap"
ARTIFACT_TYPES = ("SPEC", "WI", "ADR_DCL_GOV", "DELIB", "BRIDGE")

_ID_PATTERNS = {
    "SPEC": re.compile(r"SPEC-\d+"),
    "WI": re.compile(r"WI-\d+"),
    "ADR_DCL_GOV": re.compile(r"(?:ADR|DCL|GOV|PB|REQ)-[A-Z0-9-]+"),
    "DELIB": re.compile(r"DELIB-[A-Z0-9-]+"),
    "BRIDGE": re.compile(r"bridge/[a-z0-9-]+-\d{3}\.md"),
}


def _classify_source(row_id, type_field):
    if row_id.startswith("SPEC-"):
        return "SPEC"
    if row_id.startswith("WI-"):
        return "WI"
    if row_id.startswith("DELIB-"):
        return "DELIB"
    if type_field in {"architecture_decision", "design_constraint", "governance", "protected_behavior", "requirement"}:
        return "ADR_DCL_GOV"
    return None


def _scan(text, type_):
    if not text:
        return False
    return bool(_ID_PATTERNS[type_].search(text))


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    db_path = root / "groundtruth.db"
    matrix = {s: {t: {"with_link": 0, "total": 0} for t in ARTIFACT_TYPES} for s in ARTIFACT_TYPES}
    if db_path.exists():
        with sqlite3.connect(str(db_path)) as con:
            con.row_factory = sqlite3.Row
            spec_rows = con.execute(
                "SELECT id, type, COALESCE(description, '') || ' ' || COALESCE(change_reason, '') AS text "
                "FROM specifications WHERE changed_at >= ? AND changed_at <= ?",
                (window_start, window_end),
            ).fetchall()
            for r in spec_rows:
                src = _classify_source(r["id"], r["type"])
                if not src:
                    continue
                for t in ARTIFACT_TYPES:
                    matrix[src][t]["total"] += 1
                    if _scan(r["text"], t):
                        matrix[src][t]["with_link"] += 1
            wi_rows = con.execute(
                "SELECT id, COALESCE(description, '') || ' ' || COALESCE(change_reason, '') AS text "
                "FROM work_items WHERE changed_at >= ? AND changed_at <= ?",
                (window_start, window_end),
            ).fetchall()
            for r in wi_rows:
                for t in ARTIFACT_TYPES:
                    matrix["WI"][t]["total"] += 1
                    if _scan(r["text"], t):
                        matrix["WI"][t]["with_link"] += 1
            delib_rows = con.execute(
                "SELECT id, COALESCE(content, '') || ' ' || COALESCE(summary, '') AS text "
                "FROM deliberations WHERE changed_at >= ? AND changed_at <= ?",
                (window_start, window_end),
            ).fetchall()
            for r in delib_rows:
                for t in ARTIFACT_TYPES:
                    matrix["DELIB"][t]["total"] += 1
                    if _scan(r["text"], t):
                        matrix["DELIB"][t]["with_link"] += 1
    rates = {}
    off_diag_rates = []
    for s in ARTIFACT_TYPES:
        rates[s] = {}
        for t in ARTIFACT_TYPES:
            cell = matrix[s][t]
            rate = (cell["with_link"] / cell["total"]) if cell["total"] else 0.0
            rates[s][t] = round(rate, 4)
            if s != t and cell["total"] > 0:
                off_diag_rates.append(rate)
    value = (sum(off_diag_rates) / len(off_diag_rates)) if off_diag_rates else 0.0
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 4),
        dimensions={"matrix": rates},
        source_commit=current_source_commit(root),
        source_query="specifications + work_items + deliberations text-grep for ID patterns",
    )
