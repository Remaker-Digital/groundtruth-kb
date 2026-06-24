"""Command-line entry point for the GT-KB benchmark suite.

Subcommands:

  run      Execute one or all benchmarks; write JSON + markdown summary.
  report   Print a previously emitted run summary.
  compare  Diff two runs by idempotency_key and benchmark value.
  observatory  Build an advisory effectiveness report for an existing run.

Usage examples:

  python -m scripts.benchmarks.cli run --benchmark assertion_signal_noise
  python -m scripts.benchmarks.cli run --all --window-start 2026-01-01
  python -m scripts.benchmarks.cli report --run-id 20260514-040000
  python -m scripts.benchmarks.cli compare --baseline RUN_A --candidate RUN_B
  python -m scripts.benchmarks.cli observatory --run-id 20260514-040000
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

# FAB-17: support script-form invocation (`python scripts/benchmarks/cli.py`),
# not only module form (`python -m scripts.benchmarks.cli`). Ensure the repo
# root is importable so the `scripts.benchmarks.*` imports below resolve.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.benchmarks.common import write_run_outputs  # noqa: E402
from scripts.benchmarks.effectiveness_observatory import (  # noqa: E402
    EffectivenessObservatoryError,
    build_effectiveness_payload,
    load_run_payload,
    write_effectiveness_outputs,
)
from scripts.benchmarks.harness_quality_manifest import (  # noqa: E402
    HARNESS_QUALITY_MANIFEST,
    manifest_to_dict,
    validate_manifest,
)

BENCHMARK_MODULES = [
    "assertion_signal_noise",
    "advisory_latency",
    "backlog_triage",
    "deliberation_recall",
    "harness_role_protocol_smoke",
    "linkage_heatmap",
    "recall_coverage",
    "tool_identification",
    "versions_per_landed_change",
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
    print(
        json.dumps(
            {
                "baseline_key": a.get("idempotency_key"),
                "candidate_key": b.get("idempotency_key"),
                "diff": diff,
            },
            indent=2,
        )
    )
    return 0


def _path_for_output(path: Path) -> str:
    try:
        return path.resolve().as_posix()
    except OSError:
        return str(path)


def cmd_observatory(args):
    root = Path(args.project_root).resolve() if args.project_root else _resolve_root()
    try:
        paths = write_effectiveness_outputs(args.run_id, project_root=root)
        payload = build_effectiveness_payload(load_run_payload(args.run_id, project_root=root))
    except EffectivenessObservatoryError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"run_id": args.run_id, **{k: _path_for_output(v) for k, v in paths.items()}}, indent=2))
    else:
        print("Effectiveness observatory report")
        print("run_id:", args.run_id)
        print("advisory_status:", payload["advisory_status"])
        print("available_metrics:", payload["summary"]["available_metric_count"])
        print("missing_metrics:", payload["summary"]["missing_metric_count"])
        print("json_path:", _path_for_output(paths["json_path"]))
        print("markdown_path:", _path_for_output(paths["markdown_path"]))
    return 0


def build_manifest_payload() -> dict[str, object]:
    """Return the read-only harness-quality manifest validation payload."""
    validation_errors = validate_manifest()
    manifest = asdict(HARNESS_QUALITY_MANIFEST) if validation_errors else manifest_to_dict()
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "manifest": manifest,
        "summary": {
            "modes": len(manifest["modes"]),
            "tiers": len(manifest["tiers"]),
            "challenge_families": len(manifest["challenge_families"]),
            "safety_invariants": len(manifest["safety_invariants"]),
            "dispatcher_bridge_cli_requirements": len(manifest["dispatcher_bridge_cli_requirements"]),
        },
    }


def cmd_manifest(args):
    payload = build_manifest_payload()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        summary = payload["summary"]
        print("Harness quality benchmark manifest")
        print("valid:", payload["valid"])
        print("modes:", summary["modes"])
        print("tiers:", summary["tiers"])
        print("challenge_families:", summary["challenge_families"])
        print("safety_invariants:", summary["safety_invariants"])
        print("dispatcher_bridge_cli_requirements:", summary["dispatcher_bridge_cli_requirements"])
        for error in payload["validation_errors"]:
            print("manifest validation error:", error, file=sys.stderr)
    return 0 if payload["valid"] else 1


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
    obs = sp.add_parser("observatory", help="write an effectiveness report for an existing run")
    obs.add_argument("--run-id", required=True)
    obs.add_argument("--json", action="store_true", help="emit machine-readable output paths")
    obs.add_argument(
        "--project-root",
        help="Project root containing .gtkb-state/benchmarks; defaults to the GT-KB checkout.",
    )
    obs.set_defaults(func=cmd_observatory)
    manifest = sp.add_parser("manifest", help="validate and print the harness-quality manifest")
    manifest.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    manifest.set_defaults(func=cmd_manifest)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
