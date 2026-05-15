"""Benchmark 6: Assertion Signal/Noise Ratio.

Consumes categorized assertion output from the assertion-triage scaffolding
under ``.gtkb-state/assertion-triage/categories/<assertion_id>.json``. Each
file carries a ``category`` field in {genuine_drift, chronic_noise, flaky,
healthy}.

Value = fraction of categorized assertions that fall outside the
``chronic_noise`` bucket. Higher = more signal per assertion under triage.

Read-only. Returns 0.0 with sample_size=0 when the categories directory has
not been populated.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scripts.benchmarks.common import BenchmarkResult, current_source_commit, new_run_id

BENCHMARK_ID = "assertion_signal_noise"
CATEGORIES = ("genuine_drift", "chronic_noise", "flaky", "healthy")


def run(window_start, window_end, project_root=None):
    root = Path(project_root or Path(__file__).resolve().parents[2])
    cat_dir = root / ".gtkb-state" / "assertion-triage" / "categories"
    counts = Counter()
    if cat_dir.exists():
        for f in cat_dir.glob("*.json"):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            cat = doc.get("category")
            if cat in CATEGORIES:
                counts[cat] += 1
    total = sum(counts.values())
    signal = total - counts.get("chronic_noise", 0)
    value = (signal / total) if total else 0.0
    return BenchmarkResult(
        run_id=new_run_id(),
        benchmark_id=BENCHMARK_ID,
        window_start=window_start,
        window_end=window_end,
        value=round(value, 4),
        dimensions={c: counts.get(c, 0) for c in CATEGORIES} | {"sample_size": total},
        source_commit=current_source_commit(root),
        source_query=".gtkb-state/assertion-triage/categories/*.json category counts",
    )
