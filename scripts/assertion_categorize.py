#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Assertion Signal/Noise Categorization (Slice 3 IP-1).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md``
(Codex GO at -008) and ``SPEC-1662 (GOV-18: Assertion Quality Standard)``.

Categorizes currently-failing assertions into one of four classes:

- ``genuine_drift``: latest run FAIL, prior runs PASS within recent history.
  Drift detection per SPEC-1662 (GOV-18). Surfaces newly-broken behavior.
- ``chronic_noise``: all available runs FAIL (consecutive). Candidate for
  retirement-or-accept owner decision per GOV-15.
- ``flaky``: history includes both PASS and FAIL with at least one transition.
  Flag for repair, not retirement.
- ``healthy``: stable PASS, or stable FAIL for a ``specified``-status spec
  where FAIL is expected.

Read-only inference over ``assertion_runs``. Never modifies the source data.
Outputs per-assertion JSON to ``.gtkb-state/assertion-triage/categories/``
and a summary markdown to ``.gtkb-state/assertion-triage/<run_id>/summary.md``.

**Threshold note (implementation finding):** The existing assertion-check.py
hook prunes ``assertion_runs`` to keep at most 5 runs per spec_id (lines 489-
499 of ``.claude/hooks/assertion-check.py``). The SPEC's "50 consecutive FAIL"
chronic-noise threshold is unreachable under this data retention policy. The
SPEC permits configurable thresholds ("default 50, configurable"); this
implementation defaults to 5 to match available history. Owner can override
via ``--chronic-threshold``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Default thresholds (configurable via CLI).
# Calibrated to the 5-run history cap enforced by .claude/hooks/assertion-check.py.
DEFAULT_CHRONIC_THRESHOLD = 5  # consecutive FAIL runs to classify as chronic_noise
DEFAULT_FLAKY_WINDOW = 5  # window of recent runs to check for transitions
DEFAULT_DRIFT_PRIOR_PASS = 2  # minimum prior consecutive PASS runs needed to call newly-FAIL a drift
DEFAULT_DRIFT_WINDOW_DAYS = 7  # transition must be within this many days

# Category constants
CATEGORY_GENUINE_DRIFT = "genuine_drift"
CATEGORY_CHRONIC_NOISE = "chronic_noise"
CATEGORY_FLAKY = "flaky"
CATEGORY_HEALTHY = "healthy"
CATEGORY_UNCATEGORIZED = "uncategorized"


def _resolve_project_root(explicit: str | None) -> Path:
    """Resolve the GT-KB project root.

    Order:
      1. Explicit ``--project-root`` argument.
      2. ``GTKB_PROJECT_ROOT`` env var.
      3. Walk up from this script's location looking for ``groundtruth.toml``.
    """
    if explicit:
        return Path(explicit).resolve()
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise SystemExit("Could not resolve GT-KB project root. Pass --project-root or set GTKB_PROJECT_ROOT.")


def _assertion_id(spec_id: str, assertion_index: int, description: str) -> str:
    """Stable identifier for an assertion within a spec.

    Uses spec_id + assertion_index for the primary key, with description as
    a tiebreaker hash in case assertions are reordered between runs.
    """
    desc_hash = hashlib.sha256(description.encode("utf-8")).hexdigest()[:8]
    return f"{spec_id}__idx{assertion_index}__{desc_hash}"


def _load_runs_for_spec(conn: sqlite3.Connection, spec_id: str) -> list[dict[str, Any]]:
    """Load all assertion_runs rows for a spec, ordered oldest -> newest."""
    cursor = conn.execute(
        "SELECT run_at, overall_passed, results FROM assertion_runs WHERE spec_id = ? ORDER BY run_at ASC",
        (spec_id,),
    )
    out = []
    for row in cursor.fetchall():
        run_at = row[0]
        overall_passed = bool(row[1])
        try:
            results = json.loads(row[2]) if row[2] else []
        except (json.JSONDecodeError, TypeError):
            results = []
        if not isinstance(results, list):
            results = []
        out.append({"run_at": run_at, "overall_passed": overall_passed, "results": results})
    return out


def _extract_assertion_history(
    runs: list[dict[str, Any]],
    assertion_key: tuple[int, str],
) -> list[dict[str, Any]]:
    """Build per-run history for one specific assertion within a spec.

    Returns list of {run_at, passed, detail} entries in chronological order.
    The assertion is identified by (index, description). If the index slot
    in a run doesn't match the expected description, that run is skipped
    (assertions may have been reordered).
    """
    target_index, target_desc = assertion_key
    history = []
    for run in runs:
        results = run["results"]
        if target_index < len(results):
            entry = results[target_index]
            if isinstance(entry, dict) and entry.get("description") == target_desc:
                history.append(
                    {
                        "run_at": run["run_at"],
                        "passed": bool(entry.get("passed", False)),
                        "detail": entry.get("detail", ""),
                    }
                )
                continue
        # Fallback: scan run for matching description regardless of index
        if isinstance(results, list):
            for entry in results:
                if isinstance(entry, dict) and entry.get("description") == target_desc:
                    history.append(
                        {
                            "run_at": run["run_at"],
                            "passed": bool(entry.get("passed", False)),
                            "detail": entry.get("detail", ""),
                        }
                    )
                    break
    return history


def _categorize(
    history: list[dict[str, Any]],
    spec_status: str | None,
    chronic_threshold: int,
    flaky_window: int,
    drift_prior_pass: int,
    drift_window_days: int,
) -> dict[str, Any]:
    """Apply the four-category decision logic to one assertion's history.

    Returns a dict with category, rationale, and confidence fields.
    Deterministic: same input always produces same output.
    """
    if not history:
        return {
            "category": CATEGORY_UNCATEGORIZED,
            "rationale": "no history available",
            "confidence": 0.0,
        }

    latest = history[-1]

    # Healthy: latest PASS
    if latest["passed"]:
        if all(h["passed"] for h in history):
            return {
                "category": CATEGORY_HEALTHY,
                "rationale": f"stable PASS across {len(history)} runs",
                "confidence": 1.0,
            }
        # Latest PASS but earlier FAIL — recovering
        return {
            "category": CATEGORY_HEALTHY,
            "rationale": f"latest PASS after earlier FAIL; recovering ({len(history)} runs)",
            "confidence": 0.8,
        }

    # Latest is FAIL
    all_fail = all(not h["passed"] for h in history)

    # Healthy (expected fail): all FAIL for a `specified`-status spec
    if all_fail and spec_status == "specified":
        return {
            "category": CATEGORY_HEALTHY,
            "rationale": f"expected FAIL for specified-status spec across {len(history)} runs",
            "confidence": 1.0,
        }

    # Chronic noise: all available runs FAIL and count meets threshold
    if all_fail and len(history) >= chronic_threshold:
        return {
            "category": CATEGORY_CHRONIC_NOISE,
            "rationale": (
                f"{len(history)} consecutive FAIL runs (threshold {chronic_threshold}); "
                f"spec status: {spec_status or 'unknown'}"
            ),
            "confidence": 0.9,
        }

    # Genuine drift: prior runs were PASS, latest is FAIL, within window
    window = history[-flaky_window:] if len(history) >= flaky_window else history
    transitions = 0
    prior_pass_streak = 0
    for h in reversed(history[:-1]):
        if h["passed"]:
            prior_pass_streak += 1
        else:
            break

    if prior_pass_streak >= drift_prior_pass:
        # Check that the transition happened recently
        try:
            latest_ts = dt.datetime.fromisoformat(latest["run_at"].replace("Z", "+00:00"))
            cutoff = dt.datetime.now(dt.UTC) - dt.timedelta(days=drift_window_days)
            if latest_ts >= cutoff:
                return {
                    "category": CATEGORY_GENUINE_DRIFT,
                    "rationale": (
                        f"latest FAIL after {prior_pass_streak} prior PASS run(s); "
                        f"transition within {drift_window_days} days"
                    ),
                    "confidence": 0.9,
                }
        except (ValueError, AttributeError):
            pass

    # Flaky: window has both PASS and FAIL with at least one transition
    pass_count = sum(1 for h in window if h["passed"])
    fail_count = len(window) - pass_count
    for i in range(1, len(window)):
        if window[i]["passed"] != window[i - 1]["passed"]:
            transitions += 1
    if pass_count > 0 and fail_count > 0 and transitions >= 1:
        return {
            "category": CATEGORY_FLAKY,
            "rationale": (
                f"window of {len(window)} runs has {pass_count} PASS, {fail_count} FAIL, {transitions} transition(s)"
            ),
            "confidence": 0.8,
        }

    # Default: uncategorized (latest FAIL but doesn't fit drift/chronic/flaky patterns)
    # Common cause: short history that doesn't meet chronic threshold.
    return {
        "category": CATEGORY_UNCATEGORIZED,
        "rationale": (
            f"latest FAIL with {len(history)} runs of history; insufficient data for drift/chronic/flaky classification"
        ),
        "confidence": 0.5,
    }


def _get_spec_status(conn: sqlite3.Connection, spec_id: str) -> str | None:
    """Fetch the latest status for a spec_id."""
    try:
        cursor = conn.execute(
            "SELECT status FROM current_specifications WHERE id = ?",
            (spec_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        # Fallback if current_specifications view doesn't exist
        cursor = conn.execute(
            "SELECT status FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1",
            (spec_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def categorize_all(
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False,
    chronic_threshold: int = DEFAULT_CHRONIC_THRESHOLD,
    flaky_window: int = DEFAULT_FLAKY_WINDOW,
    drift_prior_pass: int = DEFAULT_DRIFT_PRIOR_PASS,
    drift_window_days: int = DEFAULT_DRIFT_WINDOW_DAYS,
) -> dict[str, Any]:
    """Categorize all currently-failing assertions across all specs.

    Returns a summary dict with counts per category, plus per-assertion records.
    """
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        raise SystemExit(f"groundtruth.db not found at {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        # Get all spec_ids with at least one run
        cursor = conn.execute("SELECT DISTINCT spec_id FROM assertion_runs ORDER BY spec_id")
        spec_ids = [row[0] for row in cursor.fetchall()]

        results: dict[str, dict[str, Any]] = {}
        counts = {
            CATEGORY_GENUINE_DRIFT: 0,
            CATEGORY_CHRONIC_NOISE: 0,
            CATEGORY_FLAKY: 0,
            CATEGORY_HEALTHY: 0,
            CATEGORY_UNCATEGORIZED: 0,
        }
        examined = 0
        currently_failing = 0

        for spec_id in spec_ids:
            runs = _load_runs_for_spec(conn, spec_id)
            if not runs:
                continue
            spec_status = _get_spec_status(conn, spec_id)
            latest_run = runs[-1]
            latest_results = latest_run["results"]

            # Iterate over every assertion in the latest run
            for idx, entry in enumerate(latest_results):
                if not isinstance(entry, dict):
                    continue
                description = entry.get("description", f"(no description) idx={idx}")
                examined += 1
                latest_passed = bool(entry.get("passed", False))
                if not latest_passed:
                    currently_failing += 1

                # Categorize regardless of latest outcome — healthy assertions
                # are useful for the dashboard rollup too
                history = _extract_assertion_history(runs, (idx, description))
                verdict = _categorize(
                    history,
                    spec_status,
                    chronic_threshold,
                    flaky_window,
                    drift_prior_pass,
                    drift_window_days,
                )
                aid = _assertion_id(spec_id, idx, description)
                results[aid] = {
                    "assertion_id": aid,
                    "spec_id": spec_id,
                    "spec_status": spec_status,
                    "assertion_index": idx,
                    "description": description,
                    "category": verdict["category"],
                    "rationale": verdict["rationale"],
                    "confidence": verdict["confidence"],
                    "latest_passed": latest_passed,
                    "latest_detail": entry.get("detail", ""),
                    "history_length": len(history),
                    "categorized_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                }
                counts[verdict["category"]] += 1

        run_id = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        summary = {
            "run_id": run_id,
            "generated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "project_root": str(project_root),
            "thresholds": {
                "chronic_threshold": chronic_threshold,
                "flaky_window": flaky_window,
                "drift_prior_pass": drift_prior_pass,
                "drift_window_days": drift_window_days,
            },
            "total_assertions_examined": examined,
            "currently_failing": currently_failing,
            "counts_by_category": counts,
            "dry_run": dry_run,
        }

        if not dry_run:
            _write_outputs(output_dir, run_id, summary, results)

        return {"summary": summary, "results": results}
    finally:
        conn.close()


def _write_outputs(
    output_dir: Path,
    run_id: str,
    summary: dict[str, Any],
    results: dict[str, dict[str, Any]],
) -> None:
    """Write per-assertion JSON files and a summary markdown."""
    categories_dir = output_dir / "categories"
    run_dir = output_dir / run_id
    categories_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write per-assertion JSON
    for aid, record in results.items():
        target = categories_dir / f"{aid}.json"
        target.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    # Write summary JSON
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Write summary markdown
    counts = summary["counts_by_category"]
    md = [
        f"# Assertion Signal/Noise Categorization Run {run_id}",
        "",
        f"Generated: {summary['generated_at']}",
        f"Total assertions examined: {summary['total_assertions_examined']}",
        f"Currently failing: {summary['currently_failing']}",
        "",
        "## Counts by category",
        "",
        f"- genuine_drift: {counts[CATEGORY_GENUINE_DRIFT]}",
        f"- chronic_noise: {counts[CATEGORY_CHRONIC_NOISE]}",
        f"- flaky:         {counts[CATEGORY_FLAKY]}",
        f"- healthy:       {counts[CATEGORY_HEALTHY]}",
        f"- uncategorized: {counts[CATEGORY_UNCATEGORIZED]}",
        "",
        "## Thresholds applied",
        "",
        f"- chronic_threshold: {summary['thresholds']['chronic_threshold']}",
        f"- flaky_window: {summary['thresholds']['flaky_window']}",
        f"- drift_prior_pass: {summary['thresholds']['drift_prior_pass']}",
        f"- drift_window_days: {summary['thresholds']['drift_window_days']}",
        "",
        "## Highest-priority entries (genuine_drift first)",
        "",
    ]

    drift_entries = [r for r in results.values() if r["category"] == CATEGORY_GENUINE_DRIFT]
    for record in drift_entries[:20]:
        md.append(f"- **GENUINE_DRIFT** {record['assertion_id']}")
        md.append(f"  - spec: {record['spec_id']} ({record['spec_status']})")
        md.append(f"  - description: {record['description']}")
        md.append(f"  - rationale: {record['rationale']}")
        md.append("")

    (run_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Categorize assertion failures into genuine_drift / chronic_noise / flaky / healthy."
    )
    parser.add_argument("--project-root", help="GT-KB project root (default: walk up from script)")
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: <project-root>/.gtkb-state/assertion-triage/)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute results but write no files")
    parser.add_argument(
        "--chronic-threshold",
        type=int,
        default=DEFAULT_CHRONIC_THRESHOLD,
        help=f"Consecutive FAIL runs to classify chronic_noise (default {DEFAULT_CHRONIC_THRESHOLD})",
    )
    parser.add_argument(
        "--flaky-window",
        type=int,
        default=DEFAULT_FLAKY_WINDOW,
        help=f"Window for flaky detection (default {DEFAULT_FLAKY_WINDOW})",
    )
    parser.add_argument(
        "--drift-prior-pass",
        type=int,
        default=DEFAULT_DRIFT_PRIOR_PASS,
        help=f"Prior PASS streak to classify drift (default {DEFAULT_DRIFT_PRIOR_PASS})",
    )
    parser.add_argument(
        "--drift-window-days",
        type=int,
        default=DEFAULT_DRIFT_WINDOW_DAYS,
        help=f"Drift transition must be within this many days (default {DEFAULT_DRIFT_WINDOW_DAYS})",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Stdout format")
    args = parser.parse_args()

    project_root = _resolve_project_root(args.project_root)
    output_dir = Path(args.output_dir) if args.output_dir else project_root / ".gtkb-state" / "assertion-triage"

    result = categorize_all(
        project_root=project_root,
        output_dir=output_dir,
        dry_run=args.dry_run,
        chronic_threshold=args.chronic_threshold,
        flaky_window=args.flaky_window,
        drift_prior_pass=args.drift_prior_pass,
        drift_window_days=args.drift_window_days,
    )

    if args.format == "json":
        print(json.dumps(result["summary"], indent=2, sort_keys=True))
    else:
        s = result["summary"]
        counts = s["counts_by_category"]
        print(f"Assertion categorization run {s['run_id']}")
        print(f"  examined: {s['total_assertions_examined']}")
        print(f"  currently failing: {s['currently_failing']}")
        print(f"  genuine_drift:  {counts[CATEGORY_GENUINE_DRIFT]}")
        print(f"  chronic_noise:  {counts[CATEGORY_CHRONIC_NOISE]}")
        print(f"  flaky:          {counts[CATEGORY_FLAKY]}")
        print(f"  healthy:        {counts[CATEGORY_HEALTHY]}")
        print(f"  uncategorized:  {counts[CATEGORY_UNCATEGORIZED]}")
        if not s["dry_run"]:
            print(f"  outputs: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
