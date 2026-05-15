"""Command-line entry point for the GT-KB benchmark suite.

Subcommands:

  run      Execute one or all benchmarks; write JSON + markdown summary.
  report   Print a previously emitted run summary.
  compare  Diff two runs by idempotency_key and benchmark value.

Usage examples:

  python -m scripts.benchmarks.cli run --benchmark assertion_signal_noise
  python -m scripts.benchmarks.cli run --all --window-start 2026-01-01
  python -m scripts.benchmarks.cli report --run-id 20260514-040000
  python -m scripts.benchmarks.cli compare --baseline RUN_A --candidate RUN_B
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from scripts.benchmarks.common import write_run_outputs

BENCHMARK_MODULES = [
    "assertion_signal_noise",
    "advisory_latency",
    "deliberation_recall",
    "linkage_heatmap",
    "recall_coverage",
    "tool_identification",
]


def _resolve_root():
    return Path(__file__).resolve().parents[2]


def _import_benchmark(name):
    mod = importlib.import_module("scripts.benchmarks." + name)
    return mod


def _default_window():
    end = datetime.now(UTC)
    start = end.replace(year=end.year - 1)
    return start.isoformat(), end.isoformat()


def cmd_run(args):
    root = _resolve_root()
    window_start = args.window_start or _default_window()[0]
    window_end = args.window_end or _default_window()[1]
    targets = BENCHMARK_MODULES if args.all else ([args.benchmark] if args.benchmark else BENCHMARK_MODULES)
    results = []
    for name in targets:
        try:
            mod = _import_benchmark(name)
            results.append(mod.run(window_start, window_end, root))
        except Exception as e:
            print("benchmark", name, "failed:", e, file=sys.stderr)
    if not results:
        print("no results", file=sys.stderr)
        return 1
    run_id = results[0].run_id
    paths = write_run_outputs(run_id, results, project_root=root)
    print(json.dumps({"run_id": run_id, **{k: str(v) for k, v in paths.items()}}, indent=2))
    return 0


def cmd_report(args):
    root = _resolve_root()
    run_dir = root / ".gtkb-state" / "benchmarks" / args.run_id
    md = run_dir / "summary.md"
    if not md.exists():
        print("no such run:", args.run_id, file=sys.stderr)
        return 2
    print(md.read_text(encoding="utf-8"))
    return 0


def cmd_compare(args):
    root = _resolve_root()
    base = root / ".gtkb-state" / "benchmarks" / args.baseline / "run.json"
    cand = root / ".gtkb-state" / "benchmarks" / args.candidate / "run.json"
    if not base.exists() or not cand.exists():
        print("missing run.json for one of the runs", file=sys.stderr)
        return 2
    a = json.loads(base.read_text(encoding="utf-8"))
    b = json.loads(cand.read_text(encoding="utf-8"))
    a_vals = {r["benchmark_id"]: r["value"] for r in a["results"]}
    b_vals = {r["benchmark_id"]: r["value"] for r in b["results"]}
    diff = {}
    for k in sorted(set(a_vals) | set(b_vals)):
        diff[k] = {"baseline": a_vals.get(k), "candidate": b_vals.get(k)}
    print(json.dumps({
        "baseline_key": a.get("idempotency_key"),
        "candidate_key": b.get("idempotency_key"),
        "diff": diff,
    }, indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="gtkb-benchmarks")
    sp = p.add_subparsers(dest="cmd", required=True)
    run = sp.add_parser("run", help="execute benchmarks")
    run.add_argument("--benchmark", choices=BENCHMARK_MODULES)
    run.add_argument("--all", action="store_true")
    run.add_argument("--window-start")
    run.add_argument("--window-end")
    run.set_defaults(func=cmd_run)
    rep = sp.add_parser("report", help="print a previously emitted run summary")
    rep.add_argument("--run-id", required=True)
    rep.set_defaults(func=cmd_report)
    cmp = sp.add_parser("compare", help="diff two runs")
    cmp.add_argument("--baseline", required=True)
    cmp.add_argument("--candidate", required=True)
    cmp.set_defaults(func=cmd_compare)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
